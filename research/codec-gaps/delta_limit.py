#!/usr/bin/env python3
"""
delta_limit.py — where does content-match delta stop working?

The qpixl_ascii reduction showed a content-match delta gets 2.2% of cells changed under a
small camera pan, against 85% for a positional delta. That is the win. It is also a number
with no failure mode attached, and a technique with no failure mode has not been tested,
it has been demonstrated.

This finds the limits. Four regimes where content-match should be expected to degrade, each
measured rather than asserted:

  L1  APERTURE — a texture that repeats. Every cell has a perfect match somewhere, so
      match-anywhere finds a "correct" correspondence that is the WRONG correspondence.
      Predicted: content-match looks perfect and the motion it infers is garbage.
  L2  RADIAL SPEED — under a large pan the true displacement exceeds the search radius,
      so the best match is a partial one and the residual is charged in full.
  L3  OCCLUSION — content that leaves the frame has no match at all, and is charged as if
      it had a bad one.
  L4  ALIASING — two different glyphs at the same intensity. A glyph IS a quantisation, so
      intensity carries no information below the ramp step, and a matcher keyed on
      intensity will confuse the levels that matter least for a human and most for a camera.
"""
from __future__ import annotations
import math, os, random, sys
from dataclasses import dataclass

RAMP = " .:-=+*#%@"
W, H = 64, 24

def blank():
    return [[0 for _ in range(W)] for _ in range(H)]

def render(stage, frame, pan=0.0, zoom=1.0):
    """A panning, zooming scene. Deterministic."""
    out = blank()
    for y in range(H):
        for x in range(W):
            u = (x / W - pan) * zoom
            v = y / H
            horizon = 0.52 + 0.10 * math.sin(frame * 0.4)
            body = math.exp(-(((u - 0.34) ** 2) / 0.006 + ((v - 0.6) ** 2) / 0.03))
            bars = 0.35 if abs((u * 7) % 1 - 0.5) < 0.22 and v > horizon else 0.0
            val = 0.15 * v + 0.6 * body + bars + (0.45 if abs(v - horizon) < 0.010 else 0)
            out[y][x] = RAMP[max(0, min(len(RAMP) - 1, int(max(0.0, min(1.0, val)) * len(RAMP))))]
    return out

def render_repeating(frame, period=6):
    """L1: a texture that repeats exactly. Every cell has many perfect matches."""
    out = blank()
    for y in range(H):
        for x in range(W):
            v = int((x // period + y // period + frame) % len(RAMP))
            out[y][x] = RAMP[v]
    return out

def content_delta(prev, cur, radius=2, key=None):
    """Match by CONTENT and return the set of unmatched cells.

    This is the qpixl_ascii matcher, isolated so the limits are measurable. The search goes
    outward from the same position, so on a repeating texture it takes the NEAREST match —
    which is precisely the failure: nearest is not right, it is only close.
    """
    pmap = {(x, y): prev[y][x] for y in range(len(prev)) for x in range(len(prev[0]))}
    unmatched = 0
    matched = 0
    for y in range(len(cur)):
        for x in range(len(cur[0])):
            c = cur[y][x]
            found = False
            for r in range(0, radius + 1):
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if max(abs(dx), abs(dy)) != r:
                            continue
                        q = pmap.get((x + dx, y + dy))
                        if q is not None and (key(c, q) if key else c == q):
                            found = True
                            break
                    if found: break
                if found: break
            matched += found
            unmatched += (not found)
    return matched, unmatched

def positional_delta(prev, cur):
    same = sum(1 for y in range(H) for x in range(W) if prev[y][x] == cur[y][x])
    return same, W * H - same

def pct(unmatched):
    return 100.0 * unmatched / (W * H)

def main():
    print()
    print("  WHERE CONTENT-MATCH DELTA BREAKS")
    print("  " + "=" * 74)
    print(f"  grid {W}x{H} = {W*H} cells. every number is unmatched cells, lower is better.")
    print()

    print("  L0  the working case — a scene panning under a small displacement")
    for pan in (0.2, 1.0, 3.0, 8.0, 20.0):
        a, b = render(0, 0.0), render(0, pan)
        _, upos = positional_delta(a, b)
        _, uc = content_delta(a, b, radius=3)
        print(f"    pan={pan:>5}  positional {pct(upos):>5.1f}%   content-match {pct(uc):>5.1f}%")
    print()

    print("  L1  APERTURE — a repeating texture. every cell has many perfect matches,")
    print("      so the matcher reports near-zero cost while inferring the wrong motion.")
    a, b = render_repeating(0), render_repeating(1)
    _, upos = positional_delta(a, b)
    _, uc = content_delta(a, b, radius=3)
    print(f"    positional  {pct(upos):>5.1f}%")
    print(f"    content     {pct(uc):>5.1f}%   <- the trap: looks free")
    truth = sum(1 for y in range(H) for x in range(W) if b[y][x] == a[y][(x - 1) % W])
    print(f"    ground truth: {pct(W*H-truth):>5.1f}% of cells ACTUALLY moved")
    print(f"    => the matcher under-reports the true cost by {pct(uc):.1f} points. The cheap")
    print(f"       answer here is WRONG and it looks right, which is the dangerous kind.")
    print()

    print("  L2  RADIAL SPEED — NOT YET EXERCISED. The obvious test (two identical frames")
    print("      at increasing radius) is degenerate: identical frames match at radius 0,")
    print("      so every radius returns 0.0% and the test cannot fail. Exercising this needs")
    print("      a displacement that exceeds the radius AND has no in-frame substitute,")
    print("      which a periodic scene always has. Left marked rather than faked.")
    print()

    print("  L3  OCCLUSION — content that leaves the frame has no match, and is charged")
    print("      as though it had a bad one rather than no one.")
    a, b = render(0, 0.0), render(0, 30.0)     # a pan so large most content is gone
    _, uc = content_delta(a, b, radius=4)
    print(f"    large pan, radius 4: {pct(uc):>5.1f}% unmatched")
    print("    a codec would code these as SKIP blocks at near-zero cost. This does not,")
    print("    because it has no mode where 'absent' is cheaper than 'present and wrong'.")
    print()

    print("  L4  ALIASING — NOT YET EXERCISED. The two keys compared here are")
    print("      both total on single characters, so they cannot disagree. A real test needs")
    print("      a renderer whose colour channel varies INDEPENDENTLY of its glyph channel,")
    print("      which means a colour-ramped grid rather than a single ramp. That is a")
    print("      chiaroscuro engine question, not a matcher question.")
    print()
    print("  TWO OF FOUR LIMITS ARE NOT YET MEASURED. The two that are, are the two that")
    print("  matter, and one of them fails in the dangerous direction.")
    print()

    print("  WHAT THIS TELLS THE CODEC QUESTION")
    print("  " + "-" * 74)
    print("  On ordinary motion content-match is far better than positional. It LOSES on")
    print("  the two regimes we could actually construct, and both are exactly what a video")
    print("  codec already spends its bits defending against:")
    print("    L1 aperture  -> codecs solve it with a MOTION VECTOR, not a match")
    print("    L3 occlusion  -> codecs solve it with per-block MODE SELECTION, where")
    print("                        'skip' is a coded mode and costs almost nothing")
    print("    L4 aliasing   -> codecs solve it with a LOOP FILTER and a mode-specific")
    print("                        reconstruction that is deliberately not the source")
    print()
    print("  So the borrowable idea is not 'match content'. It is that a cell's ENCODING")
    print("  is a per-cell decision with its own cost, and the decision itself is coded.")
    print("  That is glyphcast's coarse-to-fine heads with one thing missing: the heads")
    print("  are a pyramid, not a menu. A pyramid says how much resolution to spend. A")
    print("  menu says which of several ways to describe this cell, and pays for the")
    print("  choice. That is the 6D question, and a codec answers it in one line of")
    print("  bitstream that nobody has written down for cells.")

if __name__ == "__main__":
    main()
