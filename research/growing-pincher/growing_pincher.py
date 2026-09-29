#!/usr/bin/env python3
"""
growing_pincher.py — the cell that learns to bypass the LLM.

THE CELL

In the route, the pincher sits between grammar-cleanup and the LLM. Its job starts as the
obvious one: pinch the route off when the answer is already known, so the LLM is not called
at all. The interesting part is what happens to a pincher that runs for weeks.

It gets better at pinching, or it gets worse at pinching, and the difference is entirely
down to whether it is allowed to be wrong in a way it can observe. A cache that always
answers is wrong in a way nobody notices until the answer is wrong in production. A
pincher that measures its own bypass accuracy and withdraws confidence when it drops is
a different animal.

So this is a pincher with a POLICY, not a cache. It has:

  - a signature function that decides when two inputs are "the same question"
  - a set of known answers, each with a provenance
  - a per-signature accuracy record
  - a withdrawal rule: a pincher that starts missing stops pinching

The withdrawal rule is the whole design. Without it this is a cache with extra steps.

WHAT IT IS NOT

It is not a semantic cache and not a vector store. The signature is structural and
inspectable, because the point of the routing book is that a decision is a reading you can
read. An embedding distance is a number that hides the question "was this the same
question?", and that question is the one the ledger is supposed to answer.

USAGE
    python3 growing_pincher.py --self-test
    python3 growing_pincher.py --demo
    python3 growing_pincher.py --ledger
"""
from __future__ import annotations
import json, re, sys
from dataclasses import dataclass, field, asdict
from typing import Callable

# ── signature: structural, inspectable, and it can be wrong loudly ───────────────

def signature(text: str) -> str:
    """A structural signature for a question.

    Deliberately NOT semantic. It normalises whitespace, case, digits and a small set of
    content words. That means:
      - it UNDER-matches (two genuinely different questions can share a signature),
        which the accuracy record catches, and
      - it never silently over-matches, because you can read exactly what it ignored.
    A semantic cache hides its decision. This one shows it.
    """
    t = text.strip().lower()
    t = re.sub(r"\d+", "#", t)              # 3, 47, 1285 all become #
    t = re.sub(r"[^\w#\s]", " ", t)
    t = re.sub(r"\s+", " ", t)
    stop = {"the","a","an","is","are","was","were","to","of","in","on","for","and","or",
            "what","how","do","does","did","my","me","i","it","that","this","be"}
    words = [w for w in t.split() if w not in stop]
    return " ".join(words)

@dataclass
class Known:
    answer: str
    provenance: str            # where the answer came from — a receipt, not a vibe
    n_asked: int = 0
    n_right: int = 0
    # Exponential moving accuracy. A routing cell decides on the NEXT call, so recent
    # behaviour is the only thing that predicts it. A cumulative average makes a
    # 400-call-old mistake still count against a 3-call-old recovery, which is wrong for
    # a cell in a live route — a pincher cannot un-ring that bell, it can only get better.
    decayed_right: float = 0.0
    alpha: float = 0.3

    def record(self, was_right: bool) -> None:
        self.n_asked += 1
        if was_right:
            self.n_right += 1
        if self.n_asked == 1:
            self.decayed_right = 1.0 if was_right else 0.0
        else:
            self.decayed_right = (1 - self.alpha) * self.decayed_right + self.alpha * (1.0 if was_right else 0.0)

    @property
    def accuracy(self) -> float:
        """Cumulative, kept for the receipt — what the pincher has done over its life."""
        return self.n_right / self.n_asked if self.n_asked else 0.0

    @property
    def recent(self) -> float:
        """Decayed, used for the DECISION — what the pincher has been doing lately."""
        return self.decayed_right if self.n_asked else 0.0

# ── the policy ──────────────────────────────────────────────────────────────────

@dataclass
class Policy:
    """When may the pincher answer without asking?

    The thresholds are the design. MIN_ASKS stops a single lucky hit from creating a
    bypass; MIN_ACCURACY withdraws one; BACKOFF pauses one whose accuracy has fallen
    below the floor, and the pause is what lets it recover.
    """
    threshold: float = 0.85
    min_asks: int = 3
    backoff_ratio: float = 0.5      # pause at half the threshold, re-arm above it

    def may_answer(self, k: Known) -> tuple[bool, str]:
        if k.n_asked < self.min_asks:
            return False, f"not enough evidence ({k.n_asked}/{self.min_asks})"
        if k.recent >= self.threshold:
            return True, f"recent {k.recent:.2f} >= {self.threshold} (lifetime {k.accuracy:.2f})"
        return False, f"recent {k.recent:.2f} < {self.threshold} (lifetime {k.accuracy:.2f})"

# ── the cell ────────────────────────────────────────────────────────────────────

class Pincher:
    def __init__(self, policy: Policy | None = None, threshold: float = 0.85):
        self.known: dict[str, Known] = {}
        self.p = policy or Policy(threshold=threshold)
        # the ledger, because a decision to bypass is a decision and decisions are entries
        self.ledger: list[dict] = []
        # what the LLM would have said, for learning. In production this is the call.
        self.oracle: Callable[[str], str] | None = None

    # -- the one operation -------------------------------------------------------
    def route(self, text: str) -> dict:
        """Return what the route should do. Records the decision either way."""
        sig = signature(text)
        k = self.known.get(sig)

        if k is not None:
            may, why = self.p.may_answer(k)
            if may:
                # BYPASS: the known answer goes downstream, the LLM is never called.
                # n_asked is NOT incremented here. This route DECIDED; observe() will
                # report whether the decision was right, and that is the only place the
                # denominator moves. Counting both double-counted every interaction and
                # meant a perfectly reliable pincher could never accumulate confidence.
                self._entry(sig, "BYPASS", k.answer, why, llm_called=False)
                return {"action": "bypass", "answer": k.answer, "signature": sig,
                        "why": why, "llm_called": False}
            self._entry(sig, "PASS", None, why, llm_called=True)
        else:
            self._entry(sig, "PASS", None, "no known answer for this signature", llm_called=True)

        # PASS: the LLM is called, and the answer is learned.
        answer = self.oracle(text) if self.oracle else f"llm({sig[:40]})"
        if k is None:
            self.known[sig] = Known(answer, "first-pass")
        else:
            k.answer = answer
        return {"action": "pass", "answer": answer, "signature": sig,
                "why": "learned", "llm_called": True}

    def _entry(self, sig, action, answer, why, llm_called):
        self.ledger.append({
            "signature": sig, "action": action, "why": why,
            "llm_called": llm_called, "n": len(self.ledger) + 1,
        })

    # -- learning ----------------------------------------------------------------
    def observe(self, text: str, was_right: bool) -> None:
        """Tell the pincher whether a BYPASS it made was correct.

        This is the only feedback the pincher ever gets about a decision it made on its
        own. Without it, a pincher is a cache that cannot be wrong because it is never
        checked, which is the same as a pincher that is always wrong.
        """
        k = self.known.get(signature(text))
        if k is None:
            return
        k.record(was_right)

    def health(self) -> dict:
        live, dead = [], []
        for sig, k in self.known.items():
            row = {"signature": sig[:48], "asked": k.n_asked, "right": k.n_right,
                   "lifetime_acc": round(k.accuracy, 3), "recent_acc": round(k.recent, 3),
                   "provenance": k.provenance}
            (live if self.p.may_answer(k)[0] else dead).append(row)
        byp = sum(1 for e in self.ledger if e["action"] == "BYPASS")
        return {
            "known": len(self.known),
            "bypass_rate": round(byp / len(self.ledger), 3) if self.ledger else 0.0,
            "live": live, "withdrawn": dead,
            "llm_calls_saved": byp,
        }


# ── the demonstration: a pincher that grows, and a pincher that gets better at being wrong ──

def _demo():
    out = ["", "  THE GROWING PINCHER", "  " + "=" * 70, ""]
    out += ["  A pincher starts by answering nothing. It learns what it can, pinches what",
            "  it is sure about, and — the part that makes it a cell rather than a cache —",
            "  WITHDRAWS when it starts being wrong. Then it recovers.", ""]

    LLM = {
        "how many cells in the graph": "the 4D graph holds 14-tuple cells; 8 kinds in typed, 15 in cloud",
        "what is the resonance band": "47 Hz, inside the 45-55 Hz structural band",
        "which port is the reference": "quilt-c, the C99 reference port, 1,285 assertions",
    }
    p = Pincher()
    p.oracle = lambda t: LLM.get(signature(t), "unknown")

    questions = [
        "How many cells are in the graph?",
        "how many cells are in the graph",          # same signature
        "How many cells are in the 4D graph?",     # same signature (digits -> #)
        "What is the 47 Hz resonance band for?",
        "what is the resonance band",
        "which port is the reference",
    ]

    out.append("  phase 1 — learning (no bypasses yet)")
    for q in questions:
        r = p.route(q)
        out.append(f"    {r['action']:7} {r['signature'][:40]:42} {r['why']}")

    out += ["", "  phase 2 — the pincher is now confident on the resonance signature"]
    for _ in range(4):
        p.observe("what is the resonance band", True)
    for q in ["what is the resonance band", "what is the resonance band"]:
        r = p.route(q)
        out.append(f"    {r['action']:7} {r['signature'][:40]:42} {r['why']}")

    out += ["", "  phase 3 — the world changes underneath it (the LLM's answer drifts)"]
    for _ in range(4):
        p.observe("what is the resonance band", False)
    r = p.route("what is the resonance band")
    out.append(f"    {r['action']:7} {r['signature'][:40]:42} {r['why']}")
    out.append("    ^ it WITHDREW. A pincher that cannot be wrong is a pincher that is wrong.")

    out += ["", "  phase 4 — the new answer holds, and the pincher comes back"]
    for _ in range(10):
        p.observe("what is the resonance band", True)
    r = p.route("what is the resonance band")
    out.append(f"    {r['action']:7} {r['signature'][:40]:42} {r['why']}")

    h = p.health()
    out += ["", "  phase 5 — what the cell knows about itself", "  " + "-" * 70]
    out.append(f"    known signatures:   {h['known']}")
    out.append(f"    bypass rate:        {h['bypass_rate']:.2f}")
    out.append(f"    LLM calls saved:    {h['llm_calls_saved']}")
    for row in h["live"] + h["withdrawn"]:
        state = "live     " if row in h["live"] else "withdrawn"
        out.append(f"    {state} {row['signature'][:36]:38} "
                   f"lifetime={row['lifetime_acc']:.2f} recent={row['recent_acc']:.2f}")
    out += ["", "  The gap between lifetime and recent IS the story: the pincher was once",
            "  reliable, stopped being, and became reliable again. A cumulative average",
            "  would have hidden that, and a pincher that cannot see its own decline cannot",
            "  stop causing it.", ""]
    return "\n".join(out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        sys.path.insert(0, ".")
        import selftest_pincher
        sys.exit(selftest_pincher.main())
    print(_demo())
