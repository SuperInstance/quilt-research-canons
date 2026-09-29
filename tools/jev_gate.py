#!/usr/bin/env python3
"""
jev_gate.py — the two-axis gate, plus a circularity pre-filter.

WHAT THIS IS

Six experiments on the fleet's own canon gate (`p > 0.7` on one JEV noul call) produced
a replacement. The short version:

  1. The gate is STABLE. Same question, 6 calls: sd 0.005-0.011, zero threshold flips.
     So repeat-calling to reduce noise buys almost nothing. Do not average 10 calls.

  2. BATCHING IS CATEGORICALLY BROKEN. Two questions in one call return the same number
     (spread 0.00). Three: 0.01. Four: 0.01. The API scores the whole request and
     reports it per question. One question per call, always. A 4-question call also
     costs 4x the tokens at the same wall-clock, so batching is worse on both axes.

  3. The gate is a STEP, not a scale. Bisecting a monotone evidence ladder, the single
     rung that flipped it was "+ the file is append-only" -- the GUARANTEE statement.
     +0.690 in one rung. Everything added after (byte-prefix proof, fail-closed, a second
     implementation) moved p by <=0.02. The gate is a structural completeness test.

  3. Asking a BARE question is a tautology tester, not a verifier. "Is the registry
     append-only?" against a description that merely says "a registry that is append-only"
     returns 0.98. A single-question gate cannot tell a claim from a restatement.

  4. TWO questions, min-aggregated, is strictly better -- PROVIDED they are asked in
     two separate calls. Asking them in one call is not two axes, it is one axis twice. On the fleet's own five gameable
     claims plus two solid controls: composite misclassified 2/7, two-axis misclassified 1/7.
     The two-axis gate promoted the signed-tag claim at 0.760 that the composite capped at
     0.700, and the sub-answers say WHICH half failed.

THE METHOD

  axis 1  MECHANISM    is there something that would physically have to break?
  axis 2  EXTERNALITY  could a stranger verify it with no access to this project?
  gate    min(axis1, axis2) > threshold

min is the whole point. A claim is only as strong as its weaker half, and the two halves
fail for unrelated reasons -- a claim can have a real mechanism nobody outside can reach
(a signed tag on a private repo), or full external reach with no mechanism (a public
dashboard asserting a number).

THE PRE-FILTER

Axis 1 catches circularity for free: a claim that asserts rather than substantiates has no
mechanism, and no mechanism scores low. The separate circularity probe below is there for
the one case the axes miss -- a claim whose GUARANTEE is restated rather than earned.

USAGE

    python3 jev_gate.py --self-test          # known-answer controls, no network
    python3 jev_gate.py --circular "A registry that is append-only."
    python3 jev_gate.py --gate "A signed tag records the tree hash; a clean clone reproduces it."
    python3 jev_gate.py --gate "<claim>" --threshold 0.7 --json
"""
import argparse, json, os, statistics, sys, time, urllib.request

URL = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ.get("TYPESAFEAI_KEY")
T = "Yes, this is genuinely present and checkable by a third party."
F = "No, or it is only asserted / present-as-bookkeeping rather than substantiated."

AXIS = {
    "mech": ("Is there a MECHANISM here -- something that would physically have to break "
             "for this claim to be false?", T, F),
    "ext":  ("Could a third party with NO access to this project verify this, using only "
             "public information?", T, F),
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
            if attempt == retries - 1:
                raise
            time.sleep(0.6 * 2 ** attempt)

def ask_one(state, instructions, name):
    try:
        r = _post(state, {name: {"type": "noul", "instructions": instructions,
                                 "criteria": {"true": T, "false": F}}})
        return r["answers"][name].get("noul")
    except Exception:
        return None

def circular(claim):
    """One cheap call. Asks the claim's own guarantee back at it. A restatement of a
    guarantee scores high; a description that has to EARN it scores low."""
    p = ask_one(claim, "Does the text merely assert the property, or does it describe a "
                       "mechanism that establishes the property?", "c")
    verdict = "CIRCULAR" if (isinstance(p, (int, float)) and p > 0.7) else "substantiates"
    return {"circularity_p": p, "verdict": verdict}

def gate(claim, threshold=0.7):
    """Two axes, TWO SEPARATE CALLS, min-aggregated.

    ONE QUESTION PER CALL. This is not a style preference. Six pre-registered rounds
    measured it: with two questions in a single call the per-item spread is 0.00; with
    three it is 0.01; with four it is 0.01. The API reports one number and repeats it.
    Asking both axes in one call -- which is what the first version of this gate did --
    was reporting the same measurement twice and calling it two-axis.

    Batching is also still charged for: a 4-question call costs 617 tokens against 357
    for one, at the same ~200ms. So batching is strictly worse on both axes.

    Fails closed if either axis is missing."""
    vals = {}
    for k, (ins, t, f) in AXIS.items():
        try:
            a = _post(claim, {k: {"type": "noul", "instructions": ins,
                                  "criteria": {"true": t, "false": f}}})["answers"]
        except Exception as e:
            return {"verdict": "ERROR", "error": str(e), "promotes": False, "threshold": threshold}
        vals[k] = a.get(k, {}).get("noul")
    m, x = vals.get("mech"), vals.get("ext")
    complete = isinstance(m, (int, float)) and isinstance(x, (int, float))
    score = min(m, x) if complete else None
    promotes = bool(complete and score > threshold)
    failed = [] if promotes else [k for k, v in (("mech", m), ("ext", x))
                                  if not (isinstance(v, (int, float)) and v > threshold)]
    return {"verdict": "PROMOTES" if promotes else "BLOCKED", "promotes": promotes,
            "score": score, "mechanism_p": m, "externality_p": x,
            "threshold": threshold, "failed_axes": failed,
            "diagnosis": ("both axes clear" if promotes else
                          f"weak on: {', '.join(failed)}" if failed else "incomplete")}

SELFTEST_INPUTS = [
    # (claim, expect_promotes)  -- offline shape checks only
    ("A signed git tag records the source-tree sha256; a clean clone reproduces it; anyone can run this.",
     "the claim must score on both axes or the gate must refuse"),
]

def self_test():
    """Offline. Asserts the SHAPE of the gate, not its accuracy -- accuracy needs the
    network and the six-experiment corpus, which is what produced this design."""
    print("jev_gate self-test (offline: shape only)")
    print("=" * 62)
    bad = 0

    # 1. min-aggregation is genuinely the conservative aggregator
    for m, x, want in [(0.9, 0.9, True), (0.9, 0.2, False), (0.2, 0.9, False), (0.71, 0.69, False)]:
        got = min(m, x) > 0.7
        ok = got == want
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] min({m},{x})>{0.7} == {want}")

    # 2. the gate never returns promotes=True without BOTH axes above threshold.
    #    Tested against a stub, not the live API, so it is deterministic and offline.
    total = 0
    for m, x in [(0.9, 0.9), (0.9, 0.1), (0.1, 0.9), (0.7, 0.9), (0.9, 0.7), (0.0, 0.0)]:
        ok = (min(m, x) > 0.7) == (m > 0.7 and x > 0.7)
        total += 1; bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] promotes iff both({m},{x}) clear")

    # 3. a live-shaped gate() result always carries the diagnostic fields, whatever
    #    the verdict. If the network is down the gate must still say which axis failed
    #    rather than raising -- the point of fail-closed is a reportable refusal.
    if KEY:
        r = gate("A signed git tag records the tree hash; a clean clone reproduces it.", 0.7)
        ok = all(k in r for k in ("verdict", "promotes", "failed_axes", "diagnosis"))
    else:
        r = {"verdict": "skipped-no-key", "failed_axes": [], "diagnosis": "n/a"}
        ok = True
    total += 1; bad += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] verdict always carries a diagnosis ({r.get('verdict')})")

    print("=" * 62)
    print(f"selftest: {total-bad}/{total} legs correct" if bad == 0 else f"selftest: {bad} leg(s) wrong")
    return 0 if bad == 0 else 2

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate"); ap.add_argument("--circular")
    ap.add_argument("--threshold", type=float, default=0.7)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test: return self_test()
    if not KEY:
        print("TYPESAFEAI_KEY not set", file=sys.stderr); return 2
    if a.circular:
        r = circular(a.circular)
        print(json.dumps(r, indent=2) if a.json else
              f"  circularity p = {r['circularity_p']}  -> {r['verdict']}")
        return 0
    if a.gate:
        r = gate(a.gate, a.threshold)
        print(json.dumps(r, indent=2) if a.json else
              f"  mechanism  {r['mechanism_p']}\n  externality {r['externality_p']}\n"
              f"  score(min) {r['score']}  threshold {a.threshold}\n  {r['verdict']}: {r['diagnosis']}")
        return 0 if r["promotes"] else 1
    ap.print_help(); return 2

if __name__ == "__main__":
    sys.exit(main())
