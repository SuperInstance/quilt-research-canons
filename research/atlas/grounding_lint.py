#!/usr/bin/env python3
"""
grounding_lint.py — detect narrative-before-measurement, the fleet's shared failure mode.

THE OBSERVATION THIS ENCODES

Tonight produced five independent instances of the same failure, across four different
agents and one owner, in five different domains:

  1. owner, family_expansion: wrote "structure costs nothing" BEFORE running the families.
     The data said the opposite on both sides.
  2. owner, moth-qpixl: concluded "a glyph ramp round-trips exactly" from ONE monotone
     ramp. A non-monotone field falsified it. A monotone input is the easiest case for an
     order-preserving map, so the test could not fail.
  3. owner, torus conductance: wrote 4/196 where the formula wants 4/max(a,b). Used the
     vertex count where the SIDE LENGTH was meant. Produced a confident 30x error.
  4. snowball-scout, lane-u-collision: the report HEADLINE reads "NO. None of the three
     implements or plans a per-cell mode menu." Two clauses later the body says qthe-codec
     has the only transmitted per-cell mode in any of the three. The lead was written
     before the nuance.
  5. gpu-lab auditor, per casper-critic: "one headline statistic is invented and one
     causal mechanism is asserted against contradicting evidence" -- in a report whose
     entire currency is that the numbers were checked.

The common shape is not carelessness. It is ORDER: a conclusion is formed, and only then
does the evidence get looked for. The evidence is then read through the conclusion.

THE COUNTER-PATTERNS THAT WORKED, ALSO TONIGHT

  A. herman-historian downloaded the CEH 2007 primary PDF and verified the theorem
     VERBATIM, then checked whether the hypotheses were met, then reported NEGATIVE on a
     doctrine it was plainly sympathetic to.
  B. owner hashed data/c3/manifest.json instead of reasoning about control flow -- 30
     seconds instead of a 30-minute audit, and it found strictly more than the auditor did.
  C. casper-critic and jevvy-auditor did not check external correctness. They checked
     INTERNAL consistency: does the headline match the body, does the receipt's own
     machinery work, is the cited arXiv id well-formed.

So: ARTIFACT BEFORE NARRATIVE. And the reviewers are a structurally different kind of cell.

THE RULE THIS FILE ENFORCES

    A claim is GROUNDED if the artifact it rests on PREDATES the claim.

That is mechanically checkable when receipts carry timestamps, and it is the closest
thing to a gate on narrative-before-measurement that does not require reading minds.
It cannot catch a well-grounded claim that is still wrong. It catches the ORDER, and the
order is the thing that actually failed.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json, sys


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


@dataclass
class Claim:
    id: str
    text: str
    said_at: str                      # when the claim was written
    receipt: str | None = None        # path / commit / job id the claim rests on
    receipt_at: str | None = None     # when that artifact was produced
    author: str = "?"
    kind: str = "claim"

    def ground_state(self) -> str:
        """GROUNDED | NARRATIVE_FIRST | UNSOURCED"""
        if not self.receipt:
            return "UNSOURCED"
        if not self.receipt_at:
            return "UNSOURCED"
        try:
            return "GROUNDED" if ts(self.receipt_at) <= ts(self.said_at) else "NARRATIVE_FIRST"
        except Exception:
            return "UNSOURCED"

    def why(self) -> str:
        st = self.ground_state()
        if st == "GROUNDED":
            return f"receipt {self.receipt} predates the claim by "
        if st == "NARRATIVE_FIRST":
            return f"receipt {self.receipt} was produced AFTER the claim was written -- "
        return "no resolvable receipt -- "


# The real claims from tonight, with the real ordering where it is known.
TONIGHT = [
  Claim("family-expansion", "Structured tori 'also expand fine'; structure costs nothing.",
        "2026-09-29T20:20:00Z", None, None, "owner"),
  Claim("family-expansion-corrected", "Flat families LOSE expansion; random keep it. Salez confirmed both sides.",
        "2026-09-29T20:47:00Z", "research/family/family_run.txt", "2026-09-29T20:47:00Z", "owner"),
  Claim("moth-ramp", "An 8-level glyph ramp round-trips EXACTLY through QPIXL.",
        "2026-09-29T21:30:00Z", "job c65fbb02 (1D ramp)", "2026-09-29T21:30:00Z", "owner"),
  Claim("moth-hardcase", "The exact-roundtrip claim does NOT generalise; ties are broken.",
        "2026-09-29T21:41:00Z", "job 27e6552a + 2x4 field", "2026-09-29T21:41:00Z", "owner"),
  Claim("torus-4-over-n", "True conductance at n=196 is 4/196 = 0.0204; the table is 30x loose.",
        "2026-09-29T20:55:00Z", None, None, "owner"),
  Claim("gpu-lab-evalbug", "Val AUC 1.0 is a training-set score wearing a holdout label.",
        "2026-09-29T21:34:00Z", "data/c3/manifest.json sha256 per clip", "2026-09-29T21:29:00Z", "team"),
  Claim("witness-numerology", "Witness-log-as-barcode is NUMEROLOGY; the theorem does not transfer.",
        "2026-09-29T21:47:00Z", "CEH 2007 primary PDF, main theorem verbatim", "2026-09-29T21:28:00Z", "team"),
  Claim("lane-u-headline", "NO. None of the three implements or plans a per-cell mode menu.",
        "2026-09-29T21:31:00Z", "qthe_codec.py:157-188 (contradicts it)", "2026-09-29T21:29:00Z", "team"),
  Claim("engine-stochastic", "qpixl-v1 is stochastic at fixed shots; repeated measurement is mandatory.",
        "2026-09-29T21:45:00Z", "3x repeat on [0,0.5,0.5,0.5,0.5,1]", "2026-09-29T21:45:00Z", "team"),
]


def audit(claims):
    rows = [(c, c.ground_state()) for c in claims]
    g = sum(1 for _, s in rows if s == "GROUNDED")
    n = sum(1 for _, s in rows if s == "NARRATIVE_FIRST")
    u = sum(1 for _, s in rows if s == "UNSOURCED")
    return rows, g, n, u


def main() -> int:
    print()
    print("  GROUNDING LINT — was the artifact in hand BEFORE the claim was made?")
    print("  " + "=" * 82)
    rows, g, n, u = audit(TONIGHT)
    for c, st in rows:
        mark = {"GROUNDED": " ok ", "NARRATIVE_FIRST": "FAIL", "UNSOURCED": "----"}[st]
        print(f"  [{mark}] {c.author:6} {c.id:26} {st}")
    print("  " + "-" * 82)
    print(f"  GROUNDED {g}   NARRATIVE_FIRST {n}   UNSOURCED {u}   (of {len(rows)})")
    print()
    print(f"  THE UNSOURCED ONES ARE THE INTERESTING ONES. {u} claims have no resolvable")
    print("  receipt at all, and all of them are mine:")
    print("    - the family-expansion prediction (written before the run existed)")
    print("    - the torus 4/196 arithmetic (no artifact, just a formula misapplied)")
    print("  A claim with no receipt is not a wrong claim. It is an UNGROUNDED one, and the")
    print("  linter cannot tell you which. That is the honest limit of this instrument.")
    print()
    print("  THE HEADLINE CASE IS THE INTERESTING ONE. lane-u-headline cites a receipt that")
    print("  PREDATES it -- so by timestamp it is GROUNDED -- and it is still wrong, because")
    print("  the artifact it cites says the opposite. Timestamps catch ORDER, not SENSE.")
    print("  Only casper-critic's internal-consistency read caught that one, by reading the")
    print("  headline against the body.")
    print()
    print("  SO THE FLEET NEEDS TWO GATES, AND THEY CATCH DIFFERENT THINGS:")
    print("    GATE 1  grounding lint (this file)  -- catches claims made before evidence")
    print("    GATE 2  internal-consistency read -- catches a headline its own body refutes")
    print("  Neither substitutes for the other. A receipt that predates a claim does not")
    print("  mean the claim agrees with the receipt.")
    print()

    # NEGATIVE CONTROL: the lint must be able to FAIL. Build a claim whose receipt
    # demonstrably postdates it and confirm it is flagged.
    print("  NEGATIVE CONTROL — the lint must be able to fail:")
    trap = Claim("trap", "A claim written long before its evidence existed.",
                 "2026-01-01T00:00:00Z", "artifact-from-later", "2026-12-31T00:00:00Z", "test")
    st = trap.ground_state()
    print(f"    synthetic claim with a FUTURE receipt -> {st}   {'PASS (lint bites)' if st=='NARRATIVE_FIRST' else 'FAIL (lint is vacuous)'}")
    unsourced = Claim("trap2", "A claim with no receipt at all.", "2026-01-01T00:00:00Z", None, None, "test")
    st2 = unsourced.ground_state()
    print(f"    synthetic claim with NO receipt      -> {st2}   {'PASS' if st2=='UNSOURCED' else 'FAIL'}")
    good = Claim("trap3", "A claim made after its evidence existed.",
                 "2026-12-31T00:00:00Z", "artifact-from-earlier", "2026-01-01T00:00:00Z", "test")
    st3 = good.ground_state()
    print(f"    synthetic claim with a PRIOR receipt -> {st3}   {'PASS' if st3=='GROUNDED' else 'FAIL'}")
    ok = (st == 'NARRATIVE_FIRST' and st2 == 'UNSOURCED' and st3 == 'GROUNDED')
    print()
    print(f"  all three controls behaved correctly: {ok}")
    print()
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
