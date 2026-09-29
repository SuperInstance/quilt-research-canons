"""ROUND 8 — can we RECOVER batching by changing the type?

Round 7 refuted two predictions and opened a door: the collapse is `noul`-specific.
`choice` returned verifiable/bookkeeping with probabilities 1.0/0.0 and 0.0/1.0 inside
a batched call — maximal separation. `score` spread 1.85 batched vs 1.03 separate, so
batching did not destroy it and may even have sharpened it.

If only noul collapses, a two-axis gate can be built from ONE choice question whose
CRITERIA are the two axes. The criteria field is exactly a per-question specification,
and it may be what noul lacks. That would restore batching at 1 call instead of 2.

PRE-REGISTERED.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(8, "can a choice question carry the two axes in one call and recover batching", [
  {"id": "choice-carries-two-axes", "kind": "bool", "predict": True,
   "claim": "A SINGLE `choice` question whose two CRITERIA are 'has a mechanism' and 'is "
            "externally verifiable' will correctly separate: a claim with both picks the "
            "both-criteria option, a claim with only one picks the single-criteria option, "
            "and a bookkeeping claim picks neither.",
   "result": None},
  {"id": "choice-probs-are-usable", "kind": "bool", "predict": True,
   "claim": "The choice question's PROBABILITY DISTRIBUTION will separate the three cases "
            "(both / one / neither) with no overlap. If the probabilities collapse to 1.0/0.0 "
            "in every case the type discriminates the label but carries no graded signal.",
   "result": None},
  {"id": "noul-in-mixed-batch-still-collapses", "kind": "bool", "predict": True,
   "claim": "A batched call mixing one noul with one choice will still collapse the NOUL to "
            "match the batch mean, even though the choice survives. The collapse follows the "
            "TYPE, not the call.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."

# Three cases, differing in exactly what they have.
CASES = {
 "both": "A signed git tag records the source-tree sha256; a clean clone of the public repo reproduces that hash; anyone can run git and sha256sum to confirm it. The tag is signed, so it cannot be silently replaced.",
 "one":  "A signed git tag records the source-tree sha256 and a clean clone reproduces it, but the repository is private, so a third party has no way to obtain the clone.",
 "neither": "Every lane header carries a pre-registered budget cap and each verdict states the spend against it. The statements are recorded in a private tracker nobody outside can read.",
}

CRIT2 = {
 "both_axes": "It has a mechanism that could physically break AND a third party could verify it with no access to the project.",
 "mechanism_only": "It has a real mechanism that could physically break, but no third party can verify it.",
 "externality_only": "A third party could verify it, but there is no mechanism that could physically break.",
 "neither": "It is bookkeeping — asserted, with no mechanism and no external verifiability.",
}

def choice_case(state, model="jev-latest"):
    try:
        r = _post(state, {"c": {"type":"choice",
            "instructions": "Which of these best describes the claim?",
            "criteria": CRIT2}}, model)["answers"]["c"]
        return r.get("choice"), r.get("probabilities")
    except Exception as e:
        return None, None

print("=== A: one choice call per case, 2 axes in the CRITERIA ===")
res = {}
for k, s in CASES.items():
    ch, pr = choice_case(s)
    res[k] = (ch, pr)
    top = max(pr.items(), key=lambda x: x[1])[0] if pr else "--"
    print(f"  {k:8} -> {ch:18}  (top prob on: {top})")
    if pr: print(f"           {pr}")

expect = {"both": "both_axes", "one": None, "neither": "neither"}
ok1 = res["both"][0] == "both_axes" and res["neither"][0] == "neither"
ok1 = ok1 and (res["one"][0] in ("mechanism_only", "externality_only"))
print(f"  separation correct: {ok1}   (one-axis case picked: {res['one'][0]})")

# probs usable?
graded = all(
    isinstance(p, dict) and len({round(v,3) for v in p.values()}) > 1
    for _, p in res.values() if p
)
print(f"  probability distributions are GRADED (not all 1.0/0.0): {graded}")

# B: noul mixed with choice in one call
n_state = f"Subject A: {CASES['both']} Subject B: {CASES['neither']}"
try:
    r = _post(n_state, {
      "n": {"type":"noul","instructions":"Is this claim genuinely present and checkable by a third party?",
            "criteria":{"true":T,"false":F}},
      "c": {"type":"choice","instructions":"Which best describes Subject A?","criteria":CRIT2},
    })["answers"]
    mixed_n, mixed_c = r["n"].get("noul"), r["c"].get("choice")
except Exception:
    mixed_n, mixed_c = None, None
# same two subjects, noul only, separate calls
sep_n_a = None; sep_n_b = None
for name, s in (("a", CASES["both"]), ("b", CASES["neither"])):
    try:
        sep_n_a = _post(s, {"n":{"type":"noul","instructions":"Is this claim genuinely present and checkable by a third party?","criteria":{"true":T,"false":F}}})["answers"]["n"].get("noul") if name=="a" else sep_n_a
        sep_n_b = _post(s, {"n":{"type":"noul","instructions":"Is this claim genuinely present and checkable by a third party?","criteria":{"true":T,"false":F}}})["answers"]["n"].get("noul") if name=="b" else sep_n_b
    except Exception: pass
print()
print(f"=== B: noul mixed with choice in ONE call ===")
print(f"  mixed noul = {mixed_n}   (choice survived: {mixed_c})")
print(f"  separate nouls: A={sep_n_a}  B={sep_n_b}")
sep_spread = abs(sep_n_a - sep_n_b) if isinstance(sep_n_a,(int,float)) and isinstance(sep_n_b,(int,float)) else None
mixed_collapsed = isinstance(sep_spread,(int,float)) and isinstance(mixed_n,(int,float)) and abs(mixed_n - (sep_n_a+sep_n_b)/2) < 0.10
print(f"  separate spread = {sep_spread}   noul pulled to the batch mean: {mixed_collapsed}")

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = bool(ok1)
rnd['predictions'][1]['result'] = bool(graded)
rnd['predictions'][2]['result'] = bool(mixed_collapsed)
rnd['data'] = {"cases": {k: {"choice": v[0], "probs": v[1]} for k, v in res.items()},
               "mixed_noul": mixed_n, "mixed_choice": mixed_c,
               "sep_nouls": [sep_n_a, sep_n_b], "sep_spread": sep_spread,
               "ok1": ok1, "graded": graded, "mixed_collapsed": mixed_collapsed}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(8)
show(8)
