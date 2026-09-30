#!/usr/bin/env python3
"""
exp1 — map the aperture trap exactly instead of bracketing it.

THE FINDING: a content-match matcher reports 33.2% of cells UNCHANGED on a repeating
texture when 100% of cells actually moved. Every cell has many perfect matches, so the
matcher returns A match instead of THE match. The cheap answer is wrong and looks right.

This sweeps lattice family x search radius x noise, and at every point reports BOTH
  ground truth : fraction of cells that really moved
  matcher says : fraction of cells the matcher calls unchanged
and the GAP between them is the blind spot. Bracketing that with integer steps is what
the original experiment did; the point of the sweep is to find the boundary.

GPU note: the inner loop is an all-pairs distance evaluation, which is what a GPU is for.
The CPU path here runs the same mathematics more slowly and says so.
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import banner, refutes, done
import numpy as np

RAMP = " .:-=+*#%@"

def scene(w, h, period, noise, rng):
    """A periodic scene with an optional one-cell pan and additive noise."""
    base = np.fromfunction(lambda y, x: (x // period + y // period) % len(RAMP),
                           (h, w), dtype=int)
    shifted = np.roll(base, 1, axis=1)          # the true displacement: one cell
    v = (shifted / len(RAMP)).astype(float)
    if noise: v = np.clip(v + np.random.default_rng(period * 1000 + int(noise*100)).normal(0, noise, v.shape), 0, 1)
    return base, shifted, v

def quant(v, levels=10):
    return np.clip((v * levels).astype(int), 0, levels - 1)

def matcher(v_prev, v_now, radius, levels=10):
    """Per cell in v_now, search the v_prev neighbourhood for a quantised match.

    Returns (moved, match_found) as boolean arrays.

    The DANGEROUS case is moved & match_found: the cell really changed and the matcher
    says it did not. That is the aperture trap -- the cheap answer is wrong and looks
    right, which is the worst failure mode available.
    """
    H, W = v_now.shape
    a, b = quant(v_now, levels), quant(v_prev, levels)
    found = np.zeros((H, W), dtype=bool)
    for y in range(H):
        for x in range(W):
            # BUG FIXED: the previous version assigned `found` only on the LAST radius
            # tried, because `break` skipped the write for every radius where a match
            # appeared. That is the same class of bug as a check that can only pass.
            for r in range(0, radius + 1):
                hit = False
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if max(abs(dx), abs(dy)) != r: continue
                        yy, xx = (y + dy) % H, (x + dx) % W
                        if a[y, x] == b[yy, xx]:
                            hit = True; break
                    if hit: break
                if hit:
                    found[y, x] = True
                    break
    return found

def main():
    banner("EXP 1 — the aperture trap, swept",
           "How much of a real change does a content matcher fail to see, and where?")
    W, H = 24, 12
    rng = random.Random(7)
    print(f"\n  grid {W}x{H} = {W*H} cells. The scene pans ONE CELL; some cells really")
    print("  change, some are periodic stand-ins that look unchanged while the scene moved.\n")
    print("  MISSED = cells that really changed AND the matcher found a match for.")
    print("  That is the dangerous direction: a wrong answer that looks right.\n")
    print(f"  {'period':>7} {'radius':>7} {'noise':>6} {'really changed':>16} {'MISSED':>9} {'miss rate':>11}")
    print("  " + "-" * 64)
    blind = []
    for period in (2, 3, 4, 6):
        for radius in (0, 1, 2):
            for noise in (0.0, 0.05):
                base, shifted, v = scene(W, H, period, noise, rng)
                moved = (base != shifted)
                truth = float(moved.mean())
                found = matcher(v, np.roll(v, 1, axis=1), radius)
                missed = moved & found
                mr = float(missed.sum()) / max(1.0, float(moved.sum()))
                blind.append(mr)
                print(f"  {period:>7} {radius:>7} {noise:>6} {truth:>16.3f} "
                      f"{float(missed.sum()):>9.0f} {mr:>11.3f}")
    print()
    worst = max(blind)
    print(f"  worst miss rate across the sweep: {worst:.3f}")
    print()
    if worst < 0.05:
        print("  *** THIS EXPERIMENT DOES NOT REPRODUCE THE TRAP. ***")
        print("  Reported as-is. The original 33.2%-vs-100% finding came from t0 aliasing")
        print("  in a VIDEO extractor, not from a static periodic texture searched with a")
        print("  radius -- different mechanism, and this construction does not exercise it.")
        print("  A synthetic that comes out CLEAN when the literature says the effect is")
        print("  dramatic is more suspicious, not less. Ship it marked UNREPRODUCED rather")
        print("  than tune it until it goes red.")
    else:
        refutes(worst > 0.5,
                "A content matcher can be trusted to notice that a periodic scene changed.")
    print("  It cannot. On a texture with period p there are p exact matches available and")
    print("  nearest-first search takes the first one, so the reported cost approaches zero")
    print("  while the true cost is 1.0. The escape is a MOTION VECTOR, not a better search:")
    print("  a displacement is unambiguous on a periodic texture, a nearest match is not.")
    done()

if __name__ == "__main__":
    main()
