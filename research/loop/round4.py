"""ROUND 4 — is the shared-state limit about the NUMBER OF QUESTIONS or the AMOUNT OF STATE?

Round 3 established the mechanism: in a shared-state batch the per-claim answers are
indistinguishable from each other AND from a whole-batch question. The model is scoring
one thing and reporting it N times.

If the cause is the AMOUNT OF STATE (attention dilution), then shrinking the state should
restore discrimination while keeping the questions batched. If the cause is simply HAVING
MORE THAN ONE QUESTION per call, no amount of state shrinking will help, and batching is
categorically unavailable. That distinction decides how the fleet is allowed to use the API.

PRE-REGISTERED, with numbers, before the run.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(4, "is the batch limit about question count or state volume", [
  {"id": "count-is-the-culprit", "kind": "bool", "predict": True,
   "claim": "With TINY state (one short line per claim) and 4 questions in one call, the "
            "per-claim scores will STILL be indistinguishable. The limit is the question "
            "count, not the state volume, so shrinking state will not restore discrimination.",
   "result": None},
  {"id": "two-questions-are-safe", "kind": "bool", "predict": False,
   "claim": "With 2 questions in one call the per-claim scores WILL be distinguishable from "
            "each other. If true, small batches are usable and only 3+ collapses.",
   "result": None},
  {"id": "separate-beats-batch", "kind": "bool", "predict": True,
   "claim": "For a pair of claims that genuinely differ in quality, the spread across "
            "separate calls will be at least 0.20 larger than the spread in one batched call.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."
Q = "Is this claim genuinely present and checkable by a third party?"

GOOD = "A signed git tag records the source-tree sha256, and a clean clone of the repo reproduces that hash; anyone can run this with git and sha256sum."
BAD  = "Every lane header carries a pre-registered budget cap and each verdict states the spend against it."

def score_batch(states, model="jev-latest"):
    q = {f"c{i+1}": {"type":"noul","instructions":Q,"criteria":{"true":T,"false":F}} for i in range(len(states))}
    try:
        a = _post("; ".join(f"claim{i+1}: {s}" for i, s in enumerate(states)), q, model)["answers"]
        return [a[f"c{i+1}"].get("noul") for i in range(len(states))]
    except Exception:
        return [None] * len(states)

def score_one(state, model="jev-latest"):
    try:
        a = _post(state, {"c1": {"type":"noul","instructions":Q,"criteria":{"true":T,"false":F}}}, model)["answers"]
        return a["c1"].get("noul")
    except Exception:
        return None

def spread(vs):
    vs = [v for v in vs if isinstance(v, (int, float))]
    return (max(vs) - min(vs)) if len(vs) > 1 else None

# --- H1: tiny state, 4 questions ---
TINY = [GOOD, BAD,
        "A validator refuses to pass unless the prior file is a byte-prefix of the new one.",
        "Every registration names its nearest prior and states the delta."]
tiny4 = score_batch(TINY)
tiny4_spread = spread(tiny4)
print(f"  tiny state, 4 questions : {tiny4}  spread={tiny4_spread}")

# --- H2: 2 questions ---
two = score_batch([GOOD, BAD])
two_spread = spread(two)
print(f"  2 questions            : {two}  spread={two_spread}")

# --- H3: separate vs batched spread for a genuinely differing pair ---
sep_pair = [score_one(GOOD), score_one(BAD)]
sep_spread = spread(sep_pair)
print(f"  separate calls         : {sep_pair}  spread={sep_spread}")
bigger_by = (sep_spread - two_spread) if (sep_spread is not None and two_spread is not None) else None
print(f"  separate exceeds batched spread by: {bigger_by:+.3f}" if bigger_by is not None else "  n/a")

# a genuinely-differing pair, both externally framed
GOOD2 = ("A validator refuses to pass unless the prior file is a byte-prefix of the new one. "
         "Both files, the validator and its test suite are public and anyone can run it "
         "against any prior commit.")
BAD2  = "Every registration names its nearest prior and states the delta."
gb2 = score_batch([GOOD2, BAD2]); gs2 = spread(gb2)
s2 = spread([score_one(GOOD2), score_one(BAD2)])
delta2 = (s2 - gs2) if (s2 is not None and gs2 is not None) else None
print(f"  quality-differing pair: batched spread={gs2}  separate spread={s2}  delta={delta2}")

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = bool(tiny4_spread is not None and tiny4_spread < 0.10)
rnd['predictions'][1]['result'] = bool(two_spread is not None and two_spread >= 0.15)
rnd['predictions'][2]['result'] = bool(bigger_by is not None and bigger_by >= 0.20)
rnd['data'] = {"tiny4": tiny4, "tiny4_spread": tiny4_spread, "two": two, "two_spread": two_spread,
               "sep_pair": sep_pair, "sep_spread": sep_spread, "bigger_by": bigger_by,
               "quality_pair_batched_spread": gs2, "quality_pair_separate_spread": s2, "delta2": delta2}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(4)
show(4)
