#!/usr/bin/env python3
"""
view.py — ONE dataset, TWO projections. Human and agent, same truth.

The fleet doctrine says three views of one graph. This is that, and the two views are not
even the same render: the human view is a spatial spreadsheet you can rewind, and the agent
view is a flat append-only tape a machine can stream. They are generated from the same
cells in the same pass, so they cannot disagree — and that is the property that matters,
because a human UI and an agent API that drift apart are two sources of truth and one of
them is always lying.

The rewind is the part that matters for the human view. A substrate you cannot step
backwards through is a log. A substrate you can is a timeline, and a timeline is what you
reason about.
"""
from __future__ import annotations
import json, hashlib
from dataclasses import dataclass, field, asdict
from typing import Any

SCHEMA = "superinstance/view@v1"

@dataclass
class Cell:
    """A unit of the graph. Everything the views render comes from these."""
    addr: str
    kind: str
    value: Any = None
    receipt: str | None = None      # sha256 of the measurement that set this
    op: str | None = None          # the opcode that last touched it
    epoch: int = 0
    note: str = ""

@dataclass
class Frame:
    """One point on the timeline. Rewindable by index."""
    n: int
    cells: dict = field(default_factory=dict)
    label: str = ""
    digest: str = ""

class Substrate:
    def __init__(self):
        self.frames: list[Frame] = []
        self.cells: dict[str, Cell] = {}

    # -- the five opcodes, as mutations on the graph -------------------------
    def _frame(self, label=""):
        f = Frame(n=len(self.frames), cells=dict(self.cells), label=label)
        self.frames.append(f)
        return f

    def bind(self, addr, value, note="", label="bind"):
        c = Cell(addr=addr, kind="leaf", value=value, op="BIND", epoch=len(self.frames),
                 receipt=self._receipt(addr, value), note=note)
        self.cells[addr] = c
        return self._frame(label)

    def link(self, a, b, note="", label="link"):
        c = Cell(addr=f"{a}->{b}", kind="edge", value=[a, b], op="LINK", epoch=len(self.frames),
                 receipt=self._receipt(f"{a}->{b}", [a, b]), note=note)
        self.cells[c.addr] = c
        return self._frame(label)

    def effect(self, addr, value, note="", label="effect"):
        c = Cell(addr=addr, kind="leaf", value=value, op="EFFECT", epoch=len(self.frames),
                 receipt=self._receipt(addr, value), note=note)
        self.cells[addr] = c
        return self._frame(label)

    def view(self, addr):
        return self.cells.get(addr)

    def tick(self, label="tick"):
        f = self._frame(label or "tick")
        return f

    @staticmethod
    def _receipt(addr, value):
        return hashlib.sha256(f"{addr}|{json.dumps(value, sort_keys=True, default=str)}"
                              .encode()).hexdigest()[:16]

    # -- rewind -------------------------------------------------------------
    def rewind(self, n: int) -> Frame:
        """Return the state as of frame n. The substrate does not FORGET to rewind;
        it moves its head. Frames are append-only, which is the whole no-deletion
        doctrine and also what makes rewind free."""
        if n < 0 or n >= len(self.frames):
            raise IndexError(f"no frame {n}; have {len(self.frames)}")
        return self.frames[n]

    # -- THE TWO PROJECTIONS -------------------------------------------------
    def project_human(self, n: int | None = None) -> dict:
        """The synoptic view. A human reads this. It leads with what is live, and
        every cell carries the receipt that set it, because a number a human cannot
        trace is a number they have to take on faith."""
        f = self.frames[n] if n is not None else (self.frames[-1] if self.frames else Frame(0))
        rows = []
        for addr in sorted(f.cells):
            c = f.cells[addr]
            rows.append({
                "cell": addr, "kind": c.kind, "op": c.op or "-",
                "value": c.value, "receipt": (c.receipt or "")[:8],
                "age": (f.n - c.epoch), "note": c.note,
            })
        return {
            "schema": f"{SCHEMA}/human",
            "frame": f.n, "label": f.label, "total_frames": len(self.frames),
            "rewind_to": f"POST /v1/substrate/rewind {{frame:{f.n}}}",
            "cols": ["cell", "kind", "op", "value", "receipt", "age", "note"],
            "rows": rows,
        }

    def project_agent(self, n: int | None = None) -> dict:
        """The machine view. Same cells, no chrome, stable keys, typed, and it
        states its own error contract so an agent can fail against it rather than
        guess."""
        f = self.frames[n] if n is not None else (self.frames[-1] if self.frames else Frame(0))
        return {
            "schema": SCHEMA + "/agent",
            "frame": f.n, "total_frames": len(self.frames),
            "cells": [
                {"addr": c.addr, "kind": c.kind, "op": c.op, "value": c.value,
                 "receipt": c.receipt, "epoch": c.epoch}
                for _, c in sorted(f.cells.items())
            ],
            "errors": {
                "shape": {"error": "str", "detail": "str", "frame": "int|null"},
                "codes": ["UNKNOWN_CELL", "NO_SUCH_FRAME", "RATE_LIMITED"],
                "retry": "idempotent on GET; 429 carries Retry-After",
            },
            "digest": hashlib.sha256(
                json.dumps([c.addr for c in sorted(f.cells.values(), key=lambda x: x.addr)],
                           separators=(",", ":")).encode()).hexdigest()[:16],
        }
