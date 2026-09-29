"""ROUND 9 — the three questions R7/R8 opened.

  A. Does the distribution trick work with a `score` rubric? If a rubric whose LEVELS are
     the two axes yields a usable graded signal, that is a third option with no noul in it.
  B. Is the noul collapse a SERVING artifact? One type of three broken while two are fine
     is suspicious. A raw HTTP call bypassing anything that might reshape the request
     separates "the model does this" from "the endpoint does this".
  C. What is the smallest noul batch that survives? R6 tested 2/3/4 but every one used the
     SAME instruction for all questions. If the collapse is an instruction-dedup artifact,
     distinct instructions per question might survive. Cheapest remaining test, biggest
     win if true: it would restore batching at no accuracy cost.

PRE-REGISTERED.
"""
import sys, json, urllib.request, os
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(9, "score-as-rubric, serving-vs-model, and distinct-instruction batches", [
  {"id": "score-rubric-carries-signal", "kind": "bool", "predict": True,
   "claim": "A `score` question whose rubric LEVELS are the two axes will produce "
            "per-level probabilities that separate the both/one/neither cases, giving a "
            "third gate option with no noul in it.",
   "result": None},
  {"id": "collapse-is-servicing-not-model", "kind": "bool", "predict": False,
   "claim": "The noul collapse is a property of the MODEL, not the serving layer. A raw HTTP "
            "request with an identical body will collapse exactly as the client does. "
            "(If the raw call behaves DIFFERENTLY, the client or an intermediary is "
            "reshaping the request, and the client is the fix.)",
   "result": None},
  {"id": "distinct-instructions-survive", "kind": "bool", "predict": True,
   "claim": "A batched noul call where each question carries a DISTINCT instruction will "
            "survive, because the collapse is an instruction-dedup artifact.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."
NQ = "Is this claim genuinely present and checkable by a third party?"
KEY = os.environ["TYPESAFEAI_KEY"]
URL = "https://api.typesafe.ai/v1/systemone"

BOTH = "A signed git tag records the source-tree sha256; a clean clone of the public repo reproduces that hash; anyone can run git and sha256sum to confirm it. The tag is signed, so it cannot be silently replaced."
ONE  = "A signed git tag records the source-tree sha256 and a clean clone reproduces it, but the repository is private, so a third party has no way to obtain the clone."
NEIT = "Every lane header carries a pre-registered budget cap and each verdict states the spend against it. The statements are recorded in a private tracker nobody outside can read."

# ── A: score rubric whose LEVELS are the axes ──────────────────────────────────
RUB = ["0 — pure bookkeeping: no mechanism, no external check.",
       "1 — a real mechanism exists, but no third party can verify it.",
       "2 — a third party can verify it, but nothing could physically break it.",
       "3 — both: a mechanism that could physically break, and a third-party check."]
def score_case(state):
    try:
        r = _post(state, {"s": {"type":"score","instructions":"Where does this sit?","criteria":RUB}})["answers"]["s"]
        return r.get("score"), r.get("probabilities"), r.get("legend")
    except Exception:
        return None, None, None
print("=== A: score question whose RUBRIC LEVELS are the two axes ===")
sc = {}
for k, s in (("both", BOTH), ("one", ONE), ("neither", NEIT)):
    v, p, _ = score_case(s)
    sc[k] = (v, p)
    top = max(p.items(), key=lambda x: x[1])[0] if p else "--"
    print(f"  {k:8} score={v}  top level={top}")
    if p: print(f"           {p}")
# graded + correctly ordered?
def lv(v): return v if isinstance(v,(int,float)) else None
l_both, l_one, l_neit = lv(sc["both"][0]), lv(sc["one"][0]), lv(sc["neither"][0])
graded = all(isinstance(p, dict) and len({round(x,2) for x in p.values()}) > 1 for _, p in sc.values() if p)
ordered = (l_both is not None and l_one is not None and l_neit is not None
           and l_both > l_one > l_neit)
print(f"  graded distributions: {graded}   correctly ordered both>one>neither: {ordered}")

# ── B: raw HTTP, byte-identical body ───────────────────────────────────────────
def raw_call(body_obj):
    body = json.dumps(body_obj).encode()
    req = urllib.request.Request(URL, data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())
body_batched = {"model":"jev-latest",
  "state": f"Subject A: {BOTH} Subject B: {NEIT}",
  "questions": {
    "qa":{"type":"noul","instructions":NQ,"criteria":{"true":T,"false":F}},
    "qb":{"type":"noul","instructions":NQ,"criteria":{"true":T,"false":F}}}}
try:
    raw = raw_call(body_batched)
    r_a, r_b = raw["answers"]["qa"].get("noul"), raw["answers"]["qb"].get("noul")
except Exception as e:
    r_a = r_b = None
raw_spread = abs(r_a-r_b) if isinstance(r_a,(int,float)) and isinstance(r_b,(int,float)) else None
# same via the _post client path
try:
    cl = _post(body_batched["state"], body_batched["questions"])["answers"]
    c_a, c_b = cl["qa"].get("noul"), cl["qb"].get("noul")
except Exception:
    c_a = c_b = None
print()
print("=== B: raw HTTP vs the client, byte-identical body ===")
print(f"  raw    : A={r_a}  B={r_b}  spread={raw_spread}")
print(f"  client : A={c_a}  B={c_b}")
client_also_collapses = isinstance(raw_spread,(int,float)) and raw_spread < 0.10
serving_artifact = isinstance(raw_spread,(int,float)) and raw_spread >= 0.15
print(f"  raw also collapses: {client_also_collapses}  -> the collapse is in the MODEL, not the client")

# ── C: DISTINCT instructions per question in one batch ──────────────────────────
print()
print("=== C: same batch, but DISTINCT instruction per question ===")
def distinct_batch(state):
    q = {
      "qa": {"type":"noul","instructions":"Is Subject A backed by a mechanism that could physically break?","criteria":{"true":T,"false":F}},
      "qb": {"type":"noul","instructions":"Is Subject B checkable by a stranger with no access to the project?","criteria":{"true":T,"false":F}},
    }
    try:
        a = _post(state, q)["answers"]
        return a["qa"].get("noul"), a["qb"].get("noul")
    except Exception:
        return None, None
d_a, d_b = distinct_batch(f"Subject A: {BOTH} Subject B: {NEIT}")
d_spread = abs(d_a-d_b) if isinstance(d_a,(int,float)) and isinstance(d_b,(int,float)) else None
print(f"  distinct instructions: A={d_a}  B={d_b}  spread={d_spread}")
print(f"  (same-instruction batch for comparison: spread={raw_spread})")
distinct_survives = isinstance(d_spread,(int,float)) and d_spread >= 0.15

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = bool(graded and ordered)
rnd['predictions'][1]['result'] = bool(serving_artifact)
rnd['predictions'][2]['result'] = bool(distinct_survives)
rnd['data'] = {"score_rubric": {k: {"score": v[0], "probs": v[1]} for k, v in sc.items()},
               "graded": graded, "ordered": ordered,
               "raw_http": [r_a, r_b], "raw_spread": raw_spread,
               "client": [c_a, c_b], "serving_artifact": serving_artifact,
               "distinct": [d_a, d_b], "distinct_spread": d_spread,
               "distinct_survives": distinct_survives}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(9)
show(9)
