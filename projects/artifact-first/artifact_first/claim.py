"""A claim, and the artifact it rests on.

The unit here is deliberately small: a statement, the artifact that grounds it, and the
order in which the two existed. Order is the whole point, and it is the thing that is
usually lost.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json

GROUNDED = "GROUNDED"
NARRATIVE_FIRST = "NARRATIVE_FIRST"
UNSOURCED = "UNSOURCED"
INCONSISTENT = "INCONSISTENT"

VERDICTS = (GROUNDED, NARRATIVE_FIRST, UNSOURCED, INCONSISTENT)


def parse_ts(s: str) -> datetime:
    """ISO-8601 with or without a trailing Z. Tolerant on purpose: receipts come from
    many tools and a timestamp that fails to parse should mark the claim unsourced,
    not crash the gate."""
    if not s:
        raise ValueError("empty timestamp")
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


@dataclass
class Claim:
    id: str
    text: str
    said_at: str
    receipt: str | None = None
    receipt_at: str | None = None
    author: str = "?"
    #: Free-form location of the claim inside a report, for gate 2. e.g. "SUMMARY" / "L12"
    where: str = ""

    def grounding(self) -> str:
        """Did the artifact exist BEFORE the claim was written?

        A claim with no resolvable receipt is UNSOURCED, not false. Those are different
        states and conflating them is how a linter starts lying."""
        if not self.receipt or not self.receipt_at:
            return UNSOURCED
        try:
            return GROUNDED if parse_ts(self.receipt_at) <= parse_ts(self.said_at) else NARRATIVE_FIRST
        except Exception:
            return UNSOURCED

    def lag_seconds(self) -> float | None:
        """How long after the evidence the claim was made. Negative means the claim
        came first, which is the failure this whole project exists to catch."""
        try:
            return (parse_ts(self.said_at) - parse_ts(self.receipt_at)).total_seconds()
        except Exception:
            return None

    def to_dict(self) -> dict:
        return {
            "id": self.id, "text": self.text, "said_at": self.said_at,
            "receipt": self.receipt, "receipt_at": self.receipt_at,
            "author": self.author, "where": self.where,
        }


def load_claims(path: str) -> list[Claim]:
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            d = json.loads(line)
            out.append(Claim(**d))
    return out


def dump_claims(claims, path: str) -> None:
    with open(path, "w") as f:
        for c in claims:
            f.write(json.dumps(c.to_dict()) + "\n")
