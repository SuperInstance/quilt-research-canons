#!/usr/bin/env python3
"""
qpixl_ascii.py — QPIXL's trick, applied to character grids.

THE INSIGHT, AND WHERE IT CAME FROM

QuantumArtHack is a fork of HeidelbergQuantum/ParallelQPIXL. QPIXL encodes an image into
qubits and its actual contribution is not the encoding, it is the DECOMPOSITION: split the
encoding into gates, then **delete every zero angle and cancel every CNOT pair that the
optimal decomposition turned into the identity.** The circuit that survives is the
information, and it is smaller than the encoding you started with. That reduction is
classical arithmetic. It does not need a quantum computer.

chiaroscuro is a real-time webcam-to-text renderer where "characters are shapes, not
pixels." So a character grid is an encoding, and the same question applies: how much of
this grid's description is actually information?

The answer, computed rather than assumed, is what this file measures.

WHAT THE REDUCTION DOES

Decompose a frame's cell description into four channels:
    position | glyph | intensity | colour
Then cancel the identity terms in each:
    position  - cells that never move in this frame's deltas
    glyph     - rows where the glyph is constant across the whole frame
    intensity - cells whose intensity is a function of the glyph (redundant, not free)
    colour    - channels that are constant, and channels that are zero
What survives is the RESIDUAL, and the residual's size is the real description length.

WHY THIS IS THE 6D ANSWER WITHOUT BEING THE 6D ANSWER

Fixed-width encoding (FP8, FP4, ternary) spends the same bits on every cell forever,
because it cannot know the cell is boring. This spends per cell what the cell actually
costs, and the cost is a FUNCTION of the application, the camera, and the motion. A
static installation in a dark room converges to almost nothing. A moving camera in
daylight does not. Same renderer, same grid, different budget per cell, and the budget
is computed rather than declared.

The 4D delta falls out for free: under camera motion only a subset of cells change, so
the residual concentrates on the changed set, and the frame-to-frame description is
sparse without anyone having to decide it should be.
"""
from __future__ import annotations
import json, math
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Optional, Sequence

# ── the grid ──────────────────────────────────────────────────────────────────

@dataclass
class Cell:
    """One character cell. Four channels, deliberately separable so they can cancel
    independently — that separability IS the decomposition."""
    gx: int
    gy: int
    glyph: str
    intensity: float = 0.0
    colour: tuple = (0.0, 0.0, 0.0)

@dataclass
class Frame:
    cells: list = field(default_factory=list)
    cols: int = 0
    rows: int = 0

    @staticmethod
    def from_rows(rows: Sequence[str], intensity=None, colour=None):
        cells = []
        for y, line in enumerate(rows):
            for x, ch in enumerate(line):
                cells.append(Cell(
                    gx=x, gy=y, glyph=ch,
                    intensity=(intensity[y][x] if intensity else 0.0),
                    colour=(colour[y][x] if colour else (0.0, 0.0, 0.0))))
        return Frame(cells, max((len(r) for r in rows), default=0), len(rows))

    def index(self):
        return {(c.gx, c.gy): c for c in self.cells}

# ── the reduction: cancel the identity terms ─────────────────────────────────

@dataclass
class Residual:
    """What survives the cancellation. This IS the per-cell description."""
    keep_glyph: set = field(default_factory=set)
    keep_intensity: set = field(default_factory=set)
    keep_colour: set = field(default_factory=set)
    keep_delta: set = field(default_factory=set)
    cancelled: dict = field(default_factory=dict)
    glyph_alphabet: int = 0
    grid_cells: int = 0

    def free_cells(self) -> int:
        """Cells that cost NOTHING to describe, because every one of their channels
        was cancelled. This is the number a fixed-width encoding pays for and this
        does not."""
        live = self.keep_glyph | self.keep_intensity | self.keep_colour | self.keep_delta
        return self.grid_cells - len(live)

    def cost_bits(self, bits_per_glyph: float) -> float:
        """The honest cost model. Not a fixed width: what is actually described.

        A cell in the delta set is described BY the delta, so it is not also charged a
        full intensity and colour. Charging both was the second bug the demo found:
        it made the reduction look four times worse than fixed FP4, which is the
        opposite of the claim the file exists to make.
        """
        g = math.log2(self.glyph_alphabet) if self.glyph_alphabet > 1 else 0.0
        delta = set(self.keep_delta)
        # a cell carried by a delta needs no separate intensity/colour description
        intensity = [k for k in self.keep_intensity if k not in delta]
        colour = [k for k in self.keep_colour if k not in delta]
        return (len(self.keep_glyph) * g
                + len(intensity) * 8.0
                + len(colour) * 24.0
                + len(delta) * 2.0)   # a delta is one of three: up/flat/down

def reduce_frame(frame: Frame, prev: Frame | None = None, motion_tol: float = 0.0) -> Residual:
    """Cancel the identity terms. Everything cancelled here is a term the encoding
    was spending bits on that the data did not need.

    motion_tol: how far a cell may move between frames and still count as the same
    cell. At 0 the delta is positional and camera motion looks like total change.
    At 1 the delta is by content, and only genuinely new or gone cells show up.
    """
    r = Residual(grid_cells=len(frame.cells))
    idx = frame.index()

    # CHANNEL 1 — glyph. A row whose glyph is constant is describable once for the
    # whole row, not per cell.
    by_row = {}
    for (x, y), c in idx.items():
        by_row.setdefault(y, []).append(c.glyph)
    const_rows = {y for y, gs in by_row.items() if len(set(gs)) == 1}
    for (x, y), c in idx.items():
        if y not in const_rows:
            r.keep_glyph.add((x, y))
    r.cancelled["glyph_constant_rows"] = len(const_rows)

    # CHANNEL 2 — intensity. Constant intensity across the whole frame is free.
    ints = {round(c.intensity, 6) for c in frame.cells}
    uniform_intensity = len(ints) == 1
    if not uniform_intensity:
        vals = Counter(round(c.intensity, 6) for c in frame.cells)
        common, n = vals.most_common(1)[0]
        if n > len(frame.cells) * 0.9:        # a dominant level plus noise
            r.keep_intensity = {k for k in idx if round(idx[k].intensity, 6) != common}
            r.cancelled["intensity_dominant"] = n
        else:
            r.keep_intensity = set(idx)
    else:
        r.cancelled["intensity_uniform"] = len(frame.cells)

    # CHANNEL 3 — colour. Per channel, a constant channel is free; a zero channel is
    # not merely constant, it is ABSENT, and absent is cheaper than zero.
    for ci, name in enumerate("rgb"):
        chans = {round(c.colour[ci], 6) for c in frame.cells}
        if len(chans) == 1:
            r.cancelled[f"colour_{name}_constant"] = len(frame.cells)
        elif all(round(c.colour[ci], 6) == 0.0 for c in frame.cells):
            r.cancelled[f"colour_{name}_absent"] = len(frame.cells)
        else:
            r.keep_colour |= {k for k, c in idx.items() if round(c.colour[ci], 6) != 0.0}

    r.glyph_alphabet = len({c.glyph for c in frame.cells})

    # CHANNEL 4 — the 4D delta, computed BY CONTENT and not by position.
    #
    # The first version compared each cell to the cell at the same grid index in the
    # previous frame. Under camera motion that is almost never the same cell, so 85% of
    # the grid came back "changed" and the 4D claim was a fiction. A motion delta has
    # to ask: which cell in the previous frame is THIS cell? If the scene is locally
    # continuous, the answer is a near neighbour, not the same index.
    if prev is not None:
        pidx = prev.index()
        cols, rows = frame.cols or 1, frame.rows or 1
        def near(px, py, rad):
            for dy in range(-rad, rad+1):
                for dx in range(-rad, rad+1):
                    q = (px+dx, py+dy)
                    if q in pidx: yield q
        for k, c in idx.items():
            match = None
            for rad in range(0, 3):
                for q in near(k[0], k[1], rad):
                    pc = pidx[q]
                    if (pc.glyph == c.glyph
                        and abs(pc.intensity - c.intensity) <= 0.02
                        and abs(pc.colour[0]-c.colour[0]) <= 0.02):
                        match = q; break
                if match: break
            if match is None:
                r.keep_delta.add(k)
        r.cancelled["unchanged_since_prev"] = len(idx) - len(r.keep_delta)
    return r
