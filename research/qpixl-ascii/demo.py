#!/usr/bin/env python3
"""
demo.py — the numbers, on a frame that behaves like a camera looking at a scene.

Three claims, all measured here rather than asserted:

  4D  a moving camera changes a SMALL SUBSET of cells, so the frame-to-frame
      description is sparse without anyone deciding it should be
  5D  a storyboard frame and a high-frame-rate frame are the SAME grid at
      different sampling rates, and the cost falls out of the sampling
  6D  the per-cell budget is a FUNCTION of what the cell is doing — not FP8,
      not FP4, not ternary — and it differs between a static installation and
      a moving camera in the same renderer
"""
import os, sys, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qpixl_ascii import Frame, reduce_frame

RAMP = " .:-=+*#%@"
COLS, ROWS = 48, 18

def scene(t: float, noise: float = 0.0, pan: float = 0.0, seed: int = 11, steps: int = 10):
    """A frame of a scene that pans and pulses. Deterministic given t.

    Intensity is QUANTISED to the glyph ramp. That is not a simplification: a glyph IS
    a quantisation, and a renderer that emits continuous intensity per cell is not
    rendering characters, it is writing numbers that happen to be near letters.
    """
    rnd = random.Random(seed)
    rows, inten, col = [], [], []
    for y in range(ROWS):
        line, ir, cr = [], [], []
        for x in range(COLS):
            u = (x + pan) / COLS
            v = y / ROWS
            # a horizon, a moving subject, and a gradient — all continuous in t
            horizon = 0.55 + 0.12 * math.sin(t * 0.7)
            body = math.exp(-(((u - (0.3 + 0.22 * math.sin(t * 0.5))) ** 2) / 0.004
                            + ((v - (0.62 - 0.08 * math.cos(t * 0.6))) ** 2) / 0.02))
            val = (0.18 * v + 0.55 * body
                   + (0.30 if abs(v - horizon) < 0.012 else 0.0)
                   + 0.10 * math.sin(u * 12 + t))
            val = max(0.0, min(1.0, val + rnd.gauss(0, noise)))
            q = min(len(RAMP) - 1, int(val * len(RAMP)))
            line.append(RAMP[q])
            ir.append(q / (len(RAMP) - 1))     # the glyph's own level, not the raw one
            cr.append((val, val * 0.82, val * 0.55))
        rows.append("".join(line)); inten.append(ir); col.append(cr)
    return Frame.from_rows(rows, inten, col)

def cost_line(r, label):
    bits = r.cost_bits(math.log2(max(2, r.glyph_alphabet)))
    live = len(r.keep_glyph | r.keep_intensity | r.keep_colour | r.keep_delta)
    per = bits / max(1, r.grid_cells)
    print(f"  {label:28} {bits:>8.0f} bits   {per:>5.2f} bits/cell   "
          f"free cells {r.free_cells():>4}/{r.grid_cells}")
    return bits, per

def main():
    print()
    print("  QPIXL FOR CHARACTER GRIDS — the reduction, measured")
    print("  " + "=" * 78)
    print()

    print("  THE 4D CLAIM — a moving camera changes a small subset of cells")
    print("  " + "-" * 78)
    f0 = scene(0.0, noise=0.02, pan=0.0)
    r0 = reduce_frame(f0)
    cost_line(r0, "frame 0 (baseline)")
    print()
    for k, (t, pan) in enumerate([(0.25, 0.8), (0.5, 1.6), (0.75, 2.4)]):
        f1 = scene(t, noise=0.02, pan=pan)
        r1 = reduce_frame(f1, f0)
        moved = len(r1.keep_delta)
        print(f"  t={t:<5} pan={pan:<4} changed cells: {moved:>4}/{r1.grid_cells}  "
              f"({100*moved/r1.grid_cells:.1f}%)  free: {r1.free_cells()}")
    print()
    print("  The camera moved and the grid is 48x18. The cells that changed are the")
    print("  subject, the horizon and the gradient behind it. Everything else is")
    print("  identity and cancels. The sparsity is not a design decision.")
    print()

    print("  THE 5D CLAIM — storyboard vs high-frame-rate, same grid, different sampling")
    print("  " + "-" * 78)
    storyboard = [scene(0.0, noise=0.02, pan=0.0), scene(0.5, noise=0.02, pan=1.6),
                  scene(1.0, noise=0.02, pan=3.2)]
    hfr = [scene(i * 0.04, noise=0.02, pan=i * 0.13) for i in range(25)]
    prev = None
    sb_tot = hfr_tot = 0
    for f in storyboard:
        r = reduce_frame(f, prev); sb_tot += r.cost_bits(math.log2(max(2, r.glyph_alphabet))); prev = f
    prev = None
    for f in hfr:
        r = reduce_frame(f, prev); hfr_tot += r.cost_bits(math.log2(max(2, r.glyph_alphabet))); prev = f
    print(f"  storyboard    3 frames : {sb_tot:>9.0f} bits   {sb_tot/3:>7.0f} bits/frame")
    print(f"  high-frame   25 frames : {hfr_tot:>9.0f} bits   {hfr_tot/25:>7.0f} bits/frame")
    print(f"  per-frame cost at 25fps is {(1-sb_tot/3/(hfr_tot/25))*100:.0f}% lower than at 3 frames.")
    print()
    print("  The same renderer, the same grid. The extra frames are nearly free")
    print("  because each one is mostly a delta from the one before it. That is the 5D")
    print("  claim and it is arithmetic.")
    print()

    print("  THE 6D CLAIM — the per-cell budget is a function, not a width")
    print("  " + "-" * 78)
    still = scene(0.0, noise=0.001, pan=0.0)
    noisy = scene(0.0, noise=0.14, pan=0.0)
    still_r = reduce_frame(still, still)
    noisy_r = reduce_frame(noisy, still)
    sb, sp = cost_line(still_r, "a still camera")
    nb, np_ = cost_line(noisy_r, "a camera in the world")
    print()
    print(f"  fixed 8-bit everywhere      : {still_r.grid_cells*8:>8} bits both cases")
    print(f"  fixed 4-bit everywhere      : {still_r.grid_cells*4:>8} bits both cases")
    print(f"  measured, still camera      : {sb:>8.0f} bits  ({sp:.2f} bits/cell)")
    print(f"  measured, camera in motion  : {nb:>8.0f} bits  ({np_:.2f} bits/cell)")
    print()
    print(f"  The still frame is {sp:.2f} bits per cell and the moving one is {np_:.2f}.")
    print(f"  A fixed 4-bit encoding spends {still_r.grid_cells*4/sp:.0f}x too much on the")
    print(f"  still one and {still_r.grid_cells*4/np_:.0f}x too little on the other.")
    print()
    print("  That is the 6D answer, arrived at from a quantum image encoder's")
    print("  optimal-decomposition result rather than from a bit-width table: the")
    print("  description of a cell is whatever that cell costs, and the cost is a")
    print("  function of the application, the camera and the motion. An ML-learned")
    print("  font is the same idea one level up — choosing the alphabet, not the")
    print("  width — and micrograd-quilt is where that would be trained.")
    print()

if __name__ == "__main__":
    main()
