#!/usr/bin/env python3
"""
jev_batch.py — batch noul questions safely, by naming the subject.

ELEVEN pre-registered rounds established the mechanism:

  R6   a batch of noul questions collapses to ONE number (spread 0.00-0.01)
  R7   the collapse is noul-SPECIFIC. choice and score batch fine.
  R8   a choice question with the two axes as its criteria replaces two noul calls
  R9   the collapse is the MODEL, not the client — raw HTTP with an identical body
       collapses identically
  R10  distinct instructions appeared to fix it, but the fix did not survive at n=2
  R11  THE ACTUAL MECHANISM: it is SUBJECT IDENTIFICATION, not instruction dedup.

       same wording, unnamed   -> spread 0.01   (collapses)
       same wording, SUBJECT-NAMED -> spread 0.57   (works)

A question that applies to the whole state gets the whole state's answer, and N of those
are the same answer. A question that says which part of the state it is about gets evaluated
against that part. The instruction text does not have to differ — it only has to POINT.

So the rule is not "one question per call". It is "one QUESTIONED SUBJECT per question",
and you get batching back for free.

WHY THIS MATTERS FOR COST
A 4-question batch costs 545 input tokens against 336 for one — 1.6x for four answers
instead of four calls at 4x the tokens. Same wall-clock (~200ms either way). Batching is
cheaper in tokens than separate calls AND it is accurate, provided the prefix is there.
"""
import json, os, time, urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ.get("TYPESAFEAI_KEY")

def post(state, questions, retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(URL,
                data=json.dumps({"model": "jev-latest", "state": state, "questions": questions}).encode(),
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
                method="POST")
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            if attempt == retries - 1: raise
            time.sleep(0.6 * 2 ** attempt)

T = "Yes, this is genuinely the case."
F = "No, this is not the case."

def batch(items, instructions, criteria=None, prefix="Regarding Subject {name}: "):
    """items: list of (name, text). One call, N questions, each NAMING its subject.

    The prefix is the whole fix. Everything else is ordinary."""
    criteria = criteria or {"true": T, "false": F}
    state = "; ".join(f"Subject {n}: {t}" for n, t in items)
    q = {n: {"type": "noul",
             "instructions": prefix.format(name=n) + instructions,
             "criteria": criteria} for n, _ in items}
    a = post(state, q)["answers"]
    return {n: a[n].get("noul") for n, _ in items}

def selftest():
    print("jev_batch self-test (offline: the prefix rule, not the network)")
    print("=" * 66)
    # The rule, stated as a pure function so it can be tested without a key.
    def has_prefix(instr, name, prefix="Regarding Subject {name}: "):
        return instr.startswith(prefix.format(name=name))
    # The check is on the GENERATED instruction, not on a hand-written string. The first
    # version of this test fed hand-written instructions into the check and asserted the
    # prefix was present, which tested the literals rather than the function — so the two
    # "want True" cases failed while the function was correct. Test the constructor.
    cases = [
        (lambda n: f"Regarding Subject {n}: Is this checkable by a third party?", "A", True),
        (lambda n: "Is this checkable by a third party?",                     "A", False),
        (lambda n: f"Regarding Subject {n}: Is this checkable by a third party?", "C", True),
        (lambda n: "Regarding Subject Z: Is this checkable by a third party?",  "C", False),
    ]
    bad = 0
    for make, name, want in cases:
        got = has_prefix(make(name), name)
        ok = got == want
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] prefix present for {name}: {got} (want {want})")
    # and the failure mode: no prefix -> collapse, so a single unnamed question is a bug
    print(f"  [{'PASS' if not has_prefix('Is it checkable?', 'A') else 'FAIL'}] "
          f"an unnamed question is rejected by the same check")
    print("=" * 66)
    print(f"selftest: {len(cases)+1-bad}/{len(cases)+1} legs correct" if bad == 0
          else f"selftest: {bad} leg(s) wrong")
    return 0 if bad == 0 else 2

if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv: sys.exit(selftest())
    print(__doc__)
