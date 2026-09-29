"""ROUND 6 — the operational rule, and one thing nobody has checked.

Rounds 3-5 settled the mechanism: batched questions collapse toward a single number
WHATEVER they are about, and separate calls recover the discrimination. The remaining
question is how much that costs and whether there is any safe way to batch at all.

Round 5 refuted the hope that "lens batching" is safe (spread 0.20 for lenses vs 0.12
for subjects -- lenses spread MORE, which is the opposite of what I predicted: even
different questions about the SAME state get pulled together).

So one question per call. That is 2x cost for the two-axis gate. The last open question
is whether the API is doing this client-side (a per-request cost model would mean batching
is priced as one call and is a real loss) or whether multi-question requests are simply
mis-served.

PRE-REGISTERED.
"""
import sys, json, time
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(6, "the cost of the one-question rule, and whether any batching is safe", [
  {"id": "n-questions-cost-is-flat", "kind": "bool", "predict": True,
   "claim": "Wall-clock per CALL is flat regardless of how many questions it carries, so a "
            "batched call is cheaper in time even though it is useless for discrimination. "
            "That means the batching collapse is a correctness problem, not a cost problem.",
   "result": None},
  {"id": "usage-reports-per-question", "kind": "bool", "predict": True,
   "claim": "The response's usage block will report the SAME input/output token count for a "
            "1-question and a 4-question call with identical state. If it reports more, the "
            "batched call is being charged for and is worth using for throughput.",
   "result": None},
  {"id": "three-questions-are-safe", "kind": "bool", "predict": False,
   "claim": "Some batch size between 2 and 4 is safe -- there will be a k where the per-item "
            "spread is still >= 0.15. If no such k exists the rule is absolute, not a "
            "guideline.",
   "result": None},
])

import os, urllib.request
URL = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ["TYPESAFEAI_KEY"]
T = "Yes, this is genuinely the case."
F = "No, this is not the case."
Q = "Is this claim genuinely present and checkable by a third party?"
STATES = ["A signed git tag records the source-tree sha256 and a clean clone reproduces it.",
          "A validator refuses to pass unless the prior file is a byte-prefix of the new one.",
          "Every registration names its nearest prior and states the delta.",
          "Every lane header carries a pre-registered budget cap."]

def timed(nq, reps=3):
    ts = []
    usage = None
    for _ in range(reps):
        q = {f"c{i+1}": {"type":"noul","instructions":Q,"criteria":{"true":T,"false":F}} for i in range(nq)}
        st = "; ".join(f"claim{i+1}: {s}" for i, s in enumerate(STATES[:nq]))
        t0 = time.time()
        try:
            req = urllib.request.Request(URL, data=json.dumps({"model":"jev-latest","state":st,"questions":q}).encode(),
                headers={"Authorization": f"Bearer {KEY}", "Content-Type":"application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            ts.append(time.time()-t0)
            usage = d.get("usage")
            vals = [d["answers"][f"c{i+1}"].get("noul") for i in range(nq)]
        except Exception:
            return None, None, [None]*nq
    return (sum(ts)/len(ts)), usage, vals

t1, u1, v1 = timed(1)
t2, u2, v2 = timed(2)
t4, u4, v4 = timed(4)
t3, u3, v3 = timed(3)
print(f"  1 question : {t1*1000:.0f}ms  usage={u1}  vals={v1}")
print(f"  2 questions: {t2*1000:.0f}ms  usage={u2}  vals={v2}")
print(f"  3 questions: {t3*1000:.0f}ms  usage={u3}  vals={v3}")
print(f"  4 questions: {t4*1000:.0f}ms  usage={u4}  vals={v4}")

def spread(vs):
    vs=[v for v in vs if isinstance(v,(int,float))]
    return (max(vs)-min(vs)) if len(vs)>1 else None
spreads = {n: spread(v) for n, v in [(1,v1),(2,v2),(3,v3),(4,v4)] if spread(v) is not None}
print(f"  per-item spread by batch size: {spreads}")
usage_flat = (u1 == u2 == u4) if (u1 and u2 and u4) else None
any_safe = any(s >= 0.15 for s in spreads.values()) if spreads else None

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = bool(t1 and t2 and t4 and abs(t4-t1) < max(0.35, t1))
rnd['predictions'][1]['result'] = bool(usage_flat)
rnd['predictions'][2]['result'] = bool(any_safe is False)
rnd['data'] = {"times_ms": {"1":t1*1000 if t1 else None, "2":t2*1000 if t2 else None,
                            "3":t3*1000 if t3 else None, "4":t4*1000 if t4 else None},
               "usage": {"1":u1,"2":u2,"3":u3,"4":u4},
               "spreads": spreads, "any_safe_k": any_safe, "usage_flat": usage_flat}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(6)
show(6)
