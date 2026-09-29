#!/usr/bin/env python3
"""
jev_gate2.py — the gate that survives what the loop found.

EIGHT pre-registered rounds established, and this gate is built on all of them:

  R1-R3  the gate is a STEP not a scale: it fires when a description carries a mechanism
         AND an explicit guarantee, and everything piled on after that is inert.
  R4     a BARE guarantee question is a tautology tester, not a verifier. Asking "is it
         append-only?" of a description that says it returns 0.98.
  R5     the composite question is correct; decomposition is equal and more diagnostic.
  R6/R7  BATCHING IS BROKEN FOR noul. Two questions in one call return the same number
         (spread 0.00). Three: 0.01. Four: 0.01. It is not averaging and it is not
         position -- two questions on COMPLETELY UNRELATED TOPICS collapse identically.
  R7     but the collapse is noul-SPECIFIC. `choice` and `score` discriminate inside a
         batch: choice returned probabilities 1.0/0.0 and 0.0/1.0 in one call.
  R8     a `choice` question cannot LABEL which axis is missing (argmax got 2/3) but its
         PROBABILITY DISTRIBUTION carries the signal, and a derived rule gets 3/3.

So: one call, `choice` type, four criteria, and read the DISTRIBUTION rather than the
argmax. The derived score is

    both   = P(both_axes)        the thing that promotes
    neither= P(neither)          the thing that kills it
    promote iff both > neither and both > threshold

That is one call instead of two, and it does not depend on the broken noul path at all.

THE INERT REGION IS STILL THE POINT

R3 proved evidence past the guarantee moves the score by <=0.02. So this gate cannot tell a
byte-prefix proof from a formal proof. It CAN tell a claim with a mechanism and a guarantee
from a claim with neither. Use it for that, and use the receipts for the rest.
"""
import argparse, json, os, sys, time, urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ.get("TYPESAFEAI_KEY")

CRITERIA = {
    "both_axes":      "It has a mechanism that could physically break AND a third party "
                      "could verify it with no access to the project.",
    "mechanism_only": "It has a real mechanism that could physically break, but no third "
                      "party can verify it.",
    "externality_only":"A third party could verify it, but there is no mechanism that could "
                      "physically break.",
    "neither":        "It is bookkeeping — asserted, with no mechanism and no external "
                      "verifiability.",
}

def _post(state, questions, retries=4):
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

def gate(claim, threshold=0.7):
    """ONE call. `choice` type. Read the distribution, not the argmax."""
    try:
        r = _post(claim, {"c": {"type": "choice",
                                 "instructions": "Which of these best describes the claim?",
                                 "criteria": CRITERIA}})["answers"]["c"]
    except Exception as e:
        return {"verdict": "ERROR", "error": str(e), "promotes": False, "threshold": threshold}
    p = r.get("probabilities") or {}
    both = float(p.get("both_axes", 0.0))
    neither = float(p.get("neither", 0.0))
    promotes = both > neither and both > threshold
    if promotes:
        diag = "both axes clear"
    elif both <= neither:
        diag = f"bookkeeping-leaning (neither={neither:.2f} >= both={both:.2f})"
    else:
        diag = f"weak on: the both-axes side ({both:.2f} vs {threshold})"
    return {
        "verdict": "PROMOTES" if promotes else "BLOCKED",
        "promotes": promotes,
        "both_axes_p": both, "neither_p": neither,
        "argmax": r.get("choice"), "probabilities": p,
        "threshold": threshold,
        "note": "argmax is NOT the readout; it mislabels the neither case",
        "diagnosis": diag,
    }

SELFTEST = [
    # offline: the derived rule, applied to distributions the API actually returned
    ({"both_axes": 0.77, "externality_only": 0.22, "mechanism_only": 0.01, "neither": 0.00}, True),
    ({"both_axes": 0.00, "mechanism_only": 0.94, "externality_only": 0.05, "neither": 0.01}, False),
    # the case where argmax said mechanism_only but the distribution said neither
    ({"both_axes": 0.00, "mechanism_only": 0.56, "externality_only": 0.01, "neither": 0.43}, False),
    ({"both_axes": 0.30, "mechanism_only": 0.40, "externality_only": 0.20, "neither": 0.10}, False),
    ({"both_axes": 0.95, "mechanism_only": 0.03, "externality_only": 0.01, "neither": 0.01}, True),
]

def self_test():
    print("jev_gate2 self-test (offline: the derived rule on real distributions)")
    print("=" * 66)
    bad = 0
    for p, want in SELFTEST:
        both, neither = p.get("both_axes", 0.0), p.get("neither", 0.0)
        got = both > neither and both > 0.7
        argmax_would_say = max(p, key=p.get)
        ok = got == want
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] both={both:.2f} neither={neither:.2f} -> "
              f"{'PROMOTES' if got else 'BLOCKS'} (want {'PROMOTES' if want else 'BLOCKS'}, "
              f"argmax would say {argmax_would_say})")
    print("=" * 66)
    print(f"selftest: {len(SELFTEST)-bad}/{len(SELFTEST)} legs correct" if bad == 0
          else f"selftest: {bad} leg(s) wrong")
    return 0 if bad == 0 else 2

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate"); ap.add_argument("--threshold", type=float, default=0.7)
    ap.add_argument("--json", action="store_true"); ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test: return self_test()
    if not KEY: print("TYPESAFEAI_KEY not set", file=sys.stderr); return 2
    if not a.gate: ap.print_help(); return 2
    r = gate(a.gate, a.threshold)
    if a.json: print(json.dumps(r, indent=2))
    else:
        print(f"  both_axes  {r['both_axes_p']}")
        print(f"  neither   {r['neither_p']}")
        print(f"  argmax    {r['argmax']}  (ignored by design)")
        print(f"  {r['verdict']}: {r['diagnosis']}")
    return 0 if r["promotes"] else 1

if __name__ == "__main__":
    sys.exit(main())
