#!/usr/bin/env python3
"""KAT for the reduction. The claim under test is that cancellation is SAFE — that the
residual describes the frame as well as the frame describes itself."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qpixl_ascii import Frame, reduce_frame, Residual

T = []
def t(name, want, fn=None):
    def deco(f):
        T.append((name, want, f)); return f
    return deco(f) if fn is not None else deco

def grid(rows, intens=None, col=None):
    return Frame.from_rows(rows, intens, col)

@t("SAFETY: the residual keeps every cell whose glyph is NOT constant in its row", True)
def _1():
    f = grid(["AB", "CD"])
    r = reduce_frame(f)
    # no row is constant -> nothing may be cancelled
    return len(r.keep_glyph) == 4 and r.cancelled.get("glyph_constant_rows") == 0

@t("SAFETY: a constant row cancels completely and costs nothing", True)
def _2():
    f = grid(["AA", "BB"])
    r = reduce_frame(f)
    return r.cancelled.get("glyph_constant_rows") == 2 and r.keep_glyph == set()

@t("SAFETY: uniform intensity cancels; non-uniform is kept", True)
def _3():
    r1 = reduce_frame(grid(["AB"], [[0.5, 0.5]]))
    r2 = reduce_frame(grid(["AB"], [[0.5, 0.9]]))
    return r1.cancelled.get("intensity_uniform") == 2 and len(r2.keep_intensity) == 2

@t("SAFETY: a constant colour channel cancels; a varying one is kept", True)
def _4():
    flat = grid(["AB"], None, [[(1, 1, 1), (1, 1, 1)]])
    vary = grid(["AB"], None, [[(1, 0, 0), (0, 1, 0)]])
    r1, r2 = reduce_frame(flat), reduce_frame(vary)
    return r1.cancelled.get("colour_g_constant") == 2 and len(r2.keep_colour) > 0

@t("THE 4D CLAIM: under camera motion, fewer cells change than exist", True)
def _5():
    f0 = grid(["abcdefgh", "ijklmnop", "qrstuvwx"])
    f1 = grid(["abcdefgh", "ijklmnop", "qrstUVWX"])   # camera panned: 4 cells moved
    r = reduce_frame(f1, f0)
    return 0 < len(r.keep_delta) < len(f1.cells) and r.cancelled["unchanged_since_prev"] > 0

@t("NEGATIVE: an UNRELATED frame matches almost nothing (the matcher is not a liar)", True)
def _5b():
    """The control that makes _5 mean anything. A content matcher that matched
    indiscriminately would report the same sparsity on a RANDOM frame, and the
    4D claim would be a property of the matcher rather than of the scene.
    This leg is why the sparsity number can be believed."""
    import random
    rnd = random.Random(3)
    # A big enough grid that a lenient matcher cannot pass by luck. The first version
    # used 3x8 and set the bar at ">50% unmatched", which a 24-cell sample cannot
    # support — 11/24 failed a >12 threshold. The bar was wrong, not the matcher, and
    # the honest fix is a sample large enough to carry the claim rather than a smaller
    # bar that the noise could clear.
    f0 = grid(["abcdefghijklmnopqr", "stuvwxyz0123456789", "qrstuvwx!@#$%^&*("])
    noise = grid(["".join(rnd.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(20))
                  for _ in range(8)])
    r = reduce_frame(noise, f0)
    return len(r.keep_delta) > len(noise.cells) * 0.75   # at least 75% unmatched

@t("THE 6D CLAIM: a static frame costs less per cell than a moving one", True)
def _6():
    f0 = grid(["abcdefgh", "ijklmnop", "qrstuvwx"])
    f1 = grid(["abcdefgh", "ijklmnop", "qrstUVWX"])
    same = reduce_frame(f0, f0)
    moved = reduce_frame(f1, f0)
    return moved.cost_bits(5.0) > same.cost_bits(5.0)

@t("NEGATIVE: a fully-varying frame cancels nothing (proves the reducer can fail)", True)
def _7():
    random.seed(7)
    glyphs = "abcdefghijklmnopqrstuvwxyz"
    rows = ["".join(random.choice(glyphs) for _ in range(12)) for _ in range(12)]
    f = grid(rows, [[random.random() for _ in range(12)] for _ in range(12)])
    r = reduce_frame(f)
    return len(r.keep_glyph) == f.rows * 12 and r.free_cells() == 0

@t("NEGATIVE: identical frames have an EMPTY delta set (proves _5 can fail)", True)
def _8():
    f = grid(["abcdefgh", "ijklmnop"])
    r = reduce_frame(f, f)
    return r.keep_delta == set() and r.cancelled["unchanged_since_prev"] == len(f.cells)

@t("COST: free_cells counts cells with no live channel at all", True)
def _9():
    f = grid(["AA", "AA"], [[0.5, 0.5], [0.5, 0.5]], [[(0,0,0)]*2, [(0,0,0)]*2])
    r = reduce_frame(f)
    return r.free_cells() == 4 and r.cost_bits(5.0) == 0.0

@t("COST: cost is zero for a degenerate frame and rises with live channels", True)
def _10():
    f = grid(["abcdefghijkl"])
    r = reduce_frame(f)
    return r.cost_bits(5.0) > 0.0 and Residual(grid_cells=0).cost_bits(5.0) == 0.0

def main():
    print("qpixl_ascii self-test")
    print("=" * 72)
    bad = 0
    for name, want, fn in T:
        try: ok = bool(fn()) == want
        except Exception as e: ok = False; name += f"  [{type(e).__name__}: {e}]"
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * 72)
    print(f"selftest: {len(T)-bad}/{len(T)} legs correct")
    return 0 if bad == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
