"""Tests for the two gates.

Every positive assertion has a negative control beside it. A test that cannot fail is
not a test, and the fleet's own history tonight is a demonstration of that: four separate
instruments produced confident wrong numbers before anyone checked whether they COULD be
wrong.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from artifact_first.claim import Claim, GROUNDED, NARRATIVE_FIRST, UNSOURCED
from artifact_first.consistency import lint
from artifact_first.gates import check_claim

T, F = [], []


def t(name, cond):
    (T if cond else F).append(name)
    return cond


# ---------------------------------------------------------------- gate 1
grounded = Claim("g", "t", "2026-01-02T00:00:00Z", "r", "2026-01-01T00:00:00Z")
narrative = Claim("n", "t", "2026-01-01T00:00:00Z", "r", "2026-01-02T00:00:00Z")
unsourced = Claim("u", "t", "2026-01-01T00:00:00Z")
broken = Claim("b", "t", "not-a-timestamp", "r", "also-not")

t("grounded claim passes gate 1", grounded.grounding() == GROUNDED)
t("claim made before its artifact fails gate 1", narrative.grounding() == NARRATIVE_FIRST)
t("claim with no receipt is UNSOURCED not false", unsourced.grounding() == UNSOURCED)
t("NEGATIVE: unparseable timestamps are UNSOURCED, not a crash", broken.grounding() == UNSOURCED)
t("lag is negative exactly when the claim came first", narrative.lag_seconds() < 0 < grounded.lag_seconds())

# ---------------------------------------------------------------- gate 2
CLEAN = """
# Title

## Summary

The measurement was 41 of 64 clips and the effect held.

## Body

Measured across the whole set, 41 of 64 val clips were duplicates. The effect
is real and the pre-registration was genuine. Nothing here contradicts the summary.
"""
C1 = """
# Title

## Summary

Verdict: NO. None of the three implements a per-cell mode menu.

## Body

The per-cell escape is genuinely a transmitted per-cell mode, and it is
the only one in any of the three repos.
"""
C2 = """
# Title

## Summary

Summary asserts 91 of 100 cases were positive across every run.

## Body

The run is described in detail here with plenty of prose and no such
statistic appears anywhere in this section at all.
"""
C3 = """
# Title

## Summary

The round trip is not lossless and the glyphs do not survive.

## Body

The result is lossless because the order is preserved at every step and
the reconstruction is exact for every cell in the field.
"""
C4 = """
# Title

## Summary

We found 41 of 64 val clips duplicated.

## Body

Measured across the whole set, 33 of 64 val clips turned out to be duplicates
of a training clip when the manifest was checked directly.
"""

t("CLEAN report produces no findings", lint(CLEAN) == [])
t("NEGATIVE: C1 universal-vs-exception is detected", any(f.check == "C1" for f in lint(C1)))
t("NEGATIVE: C2 summary-only statistic is detected", any(f.check == "C2" for f in lint(C2)))
t("NEGATIVE: C3 polarity flip is detected", any(f.check == "C3" for f in lint(C3)))
t("NEGATIVE: C4 count disagreement is detected", any(f.check == "C4" for f in lint(C4)))
t("DOCUMENTED LIMIT: a headingless report has no body, so C1 cannot fire",
  lint("NO. None of the three has it.\n\nThe only one is in qthe.\n") == [])
t("every check has a corresponding firing input", all(
    any(f.check == c for f in lint(txt)) for c, txt in (("C1", C1), ("C2", C2), ("C3", C3), ("C4", C4))))

# ---------------------------------------------------------------- the real case
REAL = open("/tmp/scout_out/lane-u-collision.md").read() if os.path.exists(
    "/tmp/scout_out/lane-u-collision.md") else ""
if REAL:
    t("the linter rediscovers the REAL defect in the REAL fleet report",
      any(f.check == "C1" for f in lint(REAL)))

# ---------------------------------------------------------------- combined
t("grounded claim with a contradictory report FAILS the combined gate",
  not check_claim(grounded, C1).passed)
t("grounded claim with a clean report PASSES the combined gate",
  check_claim(grounded, CLEAN).passed)
t("unsourced claim FAILS even with a clean report",
  not check_claim(unsourced, CLEAN).passed)
t("NEGATIVE: the combined gate is not just gate 1 -- a grounded claim can still fail it",
  check_claim(grounded, CLEAN).passed and not check_claim(grounded, C1).passed)

if __name__ == "__main__":
    print("\n  artifact-first test suite")
    print("  " + "=" * 60)
    for n in T:
        print(f"  [PASS] {n}")
    for n in F:
        print(f"  [FAIL] {n}")
    print("  " + "=" * 60)
    print(f"  {len(T)}/{len(T)+len(F)} correct")
    sys.exit(1 if F else 0)
