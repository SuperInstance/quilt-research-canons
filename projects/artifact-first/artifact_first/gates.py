"""
The two gates, and the reason there are two.

    GATE 1  grounding    did the artifact exist before the claim was written?
    GATE 2  consistency  does the report contradict itself?

They catch different failures and neither substitutes for the other. A receipt that
predates a claim does not mean the claim agrees with the receipt -- the fleet's own
lane-u-collision report is timestamp-grounded and wrong, because the artifact it cites
refutes it.

A claim passes the combined gate when it is GROUNDED **and** its report shows no
consistency finding. Anything less is a finding, not a pass with a note.
"""
from __future__ import annotations

from dataclasses import dataclass
from .claim import Claim, GROUNDED, NARRATIVE_FIRST, UNSOURCED, INCONSISTENT
from . import consistency


@dataclass
class Verdict:
    claim_id: str
    passed: bool
    grounding: str
    consistency_findings: list

    def summary(self) -> str:
        if self.passed:
            return f"  [ ok ] {self.claim_id:28} GROUNDED, no self-contradiction"
        bits = [self.grounding]
        if self.consistency_findings:
            bits.append(f"{len(self.consistency_findings)} consistency finding(s)")
        return f"  [FAIL] {self.claim_id:28} " + ", ".join(bits)


def check_claim(c: Claim, report_text: str | None = None) -> Verdict:
    g = c.grounding()
    findings = consistency.lint(report_text) if report_text else []
    passed = (g == GROUNDED) and not findings
    return Verdict(c.id, passed, g, findings)


def check_all(claims, report_text: str | None = None) -> list[Verdict]:
    return [check_claim(c, report_text) for c in claims]


def report(verdicts) -> str:
    lines = ["", "  ARTIFACT-FIRST — combined gate", "  " + "=" * 66, ""]
    for v in verdicts:
        lines.append(v.summary())
    npass = sum(1 for v in verdicts if v.passed)
    lines += ["  " + "-" * 66,
              f"  {npass}/{len(verdicts)} claims clear both gates", ""]
    return "\n".join(lines)
