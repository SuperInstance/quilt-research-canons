"""ROUND 5 — the fix, tested. And the question the fix raises.

Round 4 settled the operational question decisively: batching is categorically
unavailable. Two questions in one call return the SAME number for both (spread 0.00).
Four questions with tiny state return 0.28/0.28/0.28/0.27. Separate calls return
0.62 vs 0.31 for the same pair.

So the fleet's rule is: ONE QUESTION PER CALL, always. That costs 4x the calls.

The obvious next question is whether the cost is avoidable. The `state` field is shared
across questions in a call — but what if the state itself is the thing being scored, and
each question is a different LENS rather than a different subject? In that case batching
is fine, because the subjects are not being compared, only the same subject under
different lenses. That is exactly what the two-axis gate does — and if it is wrong, the
gate I shipped this session is measuring one axis twice.

PRE-REGISTERED.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(5, "is the two-axis gate valid, and can lens-batching be made safe", [
  {"id": "lens-batching-is-valid", "kind": "bool", "predict": True,
   "claim": "When questions are DIFFERENT LENSES on ONE state (not different subjects), the "
            "answers will differ from each other. Batching collapses only when the questions "
            "are about DIFFERENT subjects, because then the model is averaging over them.",
   "result": None},
  {"id": "two-axis-gate-is-honest", "kind": "bool", "predict": True,
   "claim": "The two-axis gate (mechanism + externality, min-aggregated) will give different "
            "numbers for the two axes on a claim where only one holds. If batching collapsed "
            "the axes together, the gate has been reporting one value twice.",
   "result": None},
  {"id": "agreement-under-repetition", "kind": "bool", "predict": True,
   "claim": "Asking the SAME axis in two separate calls on the same state will agree within "
            "0.10, so a min-of-two-axes computed across separate calls equals the min-of-two "
            "computed in one call.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."

MECH = "A signed git tag records the source-tree sha256; a clean clone reproduces it; anyone can run this with git and sha256sum. A registry where lines are sha256-sealed and append-only by construction."
EXT  = "Is this something a third party with NO access to this project could verify, using only public information?"
MECH_Q = "Is there a mechanism here — something that would physically have to break for this to be false?"

def multi(state, questions):
    try:
        a = _post(state, questions)["answers"]
        return {k: a[k].get("noul") for k in questions}
    except Exception:
        return {k: None for k in questions}

# H1: lens-batching (same state, different LENSES) vs subject-batching
lens = multi(MECH, {
  "a": {"type":"noul","instructions":MECH_Q,"criteria":{"true":T,"false":F}},
  "b": {"type":"noul","instructions":EXT,"criteria":{"true":T,"false":F}},
})
subj = multi(f"Subject A: {MECH} Subject B: Every registration names its nearest prior and states the delta.", {
  "a": {"type":"noul","instructions":MECH_Q,"criteria":{"true":T,"false":F}},
  "b": {"type":"noul","instructions":EXT,"criteria":{"true":T,"false":F}},
})
lens_spread = abs(lens["a"]-lens["b"]) if all(isinstance(v,(int,float)) for v in lens.values()) else None
subj_spread = abs(subj["a"]-subj["b"]) if all(isinstance(v,(int,float)) for v in subj.values()) else None
print(f"  LENS batching (same state, 2 questions) : {lens}  spread={lens_spread}")
print(f"  SUBJECT batching (2 subjects, 1 state)  : {subj}  spread={subj_spread}")

# H2: does the two-axis gate give different numbers where only one axis holds?
ONE_AXIS_ONLY = "Every lane header carries a pre-registered budget cap. The mechanism is a bash script that reads a YAML file and refuses to emit a verdict if the cap field is missing."
g = multi(ONE_AXIS_ONLY, {
  "a": {"type":"noul","instructions":MECH_Q,"criteria":{"true":T,"false":F}},
  "b": {"type":"noul","instructions":EXT,"criteria":{"true":T,"false":F}},
})
g_spread = abs(g["a"]-g["b"]) if all(isinstance(v,(int,float)) for v in g.values()) else None
print(f"  one-axis-holds case: mech={g['a']}  ext={g['b']}  spread={g_spread}")

# H3: does separate == batched for the same axis?
sep_m = multi(MECH, {"m":{"type":"noul","instructions":MECH_Q,"criteria":{"true":T,"false":F}}})["m"]
sep_e = multi(MECH, {"e":{"type":"noul","instructions":EXT,"criteria":{"true":T,"false":F}}})["e"]
batched_m = lens["a"]; batched_e = lens["b"]
agree = (isinstance(sep_m,(int,float)) and isinstance(batched_m,(int,float)) and abs(sep_m-batched_m)<=0.10
         and isinstance(sep_e,(int,float)) and isinstance(batched_e,(int,float)) and abs(sep_e-batched_e)<=0.10)
mins_match = (abs(min(sep_m,sep_e)-min(batched_m,batched_e)) <= 0.10) if all(isinstance(v,(int,float)) for v in (sep_m,sep_e,batched_m,batched_e)) else None
print(f"  mech: separate={sep_m}  batched={batched_m}")
print(f"  ext : separate={sep_e}  batched={batched_e}")
print(f"  min agrees: {mins_match}")

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = bool(lens_spread is not None and subj_spread is not None and lens_spread > subj_spread + 0.15)
rnd['predictions'][1]['result'] = bool(g_spread is not None and g_spread > 0.20)
rnd['predictions'][2]['result'] = bool(agree)
rnd['data'] = {"lens": lens, "lens_spread": lens_spread, "subj": subj, "subj_spread": subj_spread,
               "one_axis": g, "one_axis_spread": g_spread, "sep_m": sep_m, "sep_e": sep_e,
               "batched_m": batched_m, "batched_e": batched_e, "mins_match": mins_match}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(5)
show(5)
