"""ROUND 1 — the three questions I said were worth testing, pre-registered.

The predictions are written with NUMBERS before the run. If I only wrote the question,
every outcome would be a finding and the loop would learn nothing.
"""
import sys, statistics, json
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, noul, _post

# Pre-register. Each states what I believe BEFORE running, with a tolerance.
pre_register(1, "three questions about the gate that were worth asking", [
  {"id": "inert-axis-responsiveness", "predict": 0.30, "tolerance": 0.25,
   "claim": "An axis asking SPECIFICALLY about independent reproduction will score the "
            "'mech only' rung (0.95 on the generic mechanism axis) BELOW 0.30, because it "
            "asks about something the composite is provably insensitive to.",
   "result": None},
  {"id": "preview-agreements", "predict": 0.20, "tolerance": 0.20,
   "claim": "jev-preview will disagree with jev-latest on at least 2 of 4 borderline claims "
            "by more than 0.15, so cross-model agreement is a real constraint and not free.",
   "result": None},
  {"id": "axis-complementarity", "predict": 0.60, "tolerance": 0.30,
   "claim": "The reproduction axis and the externality axis will NOT be redundant — their "
            "min over the mech+guar control will be within 0.15 of the externality axis alone, "
            "meaning reproduction carries little independent signal there.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."

# --- Q1: does a reproduction-specific axis respond where the composite is inert? ---
BORDERLINE = {
 "mech_only": "A registry where each line is sha256-sealed with the sha256 of its own text. Editing a sealed line breaks that line's hash.",
 "mech+guar": "A registry where each line is sha256-sealed, the file is append-only, and a validator proves the old file is a byte-prefix of the new across commits.",
 "guar_only": "A registry that is append-only. Nothing else is specified.",
 "repro_heavy": "A registry where each line is sha256-sealed and append-only, AND two independent implementations in different languages both reproduce every digest, AND both are public with a passing conformance suite.",
}

def ask_many(state, questions, model="jev-latest"):
    q = {k: {"type": "noul", "instructions": ins, "criteria": {"true": T, "false": F}}
         for k, ins in questions.items()}
    try:
        a = _post(state, q, model)["answers"]
        return {k: a[k].get("noul") for k in questions}
    except Exception as e:
        return {k: None for k in questions}

# --- Q1 ---
AXES = {
 "generic_mech": "Is there a mechanism here — something that would physically have to break for this to be false?",
 "reproduction":  "Is this claim independently REPRODUCED — verified by a second implementation, or by a second party re-deriving the result, rather than asserted once?",
 "externality":   "Could a third party with NO access to this project verify this, using only public information?",
}
res1 = {}
for name, s in BORDERLINE.items():
    r = ask_many(s, AXES)
    res1[name] = r
    print(f"  {name:12} generic={r.get('generic_mech')}  repro={r.get('reproduction')}  ext={r.get('externality')}")

# --- Q2: cross-model agreement ---
SAME_Q = {f"c{i}": "Is this claim genuinely present and checkable by a third party?" for i in range(1, 5)}
CLAIMS4 = [
 "A signed git tag records the source-tree sha256; a clean clone reproduces it.",
 "Every lane header carries a pre-registered budget cap and each verdict states spend.",
 "A validator proves the old registry is a byte-prefix of the new across commits, and fails closed.",
 "Every registration cites its nearest prior and states the delta.",
]
def batch(model):
    q = {f"c{i+1}": {"type":"noul","instructions":SAME_Q[f"c{i+1}"],"criteria":{"true":T,"false":F}} for i in range(4)}
    st = "; ".join(f"claim{i+1}: {c}" for i, c in enumerate(CLAIMS4))
    try:
        a = _post(st, q, model)["answers"]
        return {f"c{i+1}": a[f"c{i+1}"].get("noul") for i in range(4)}
    except Exception:
        return {f"c{i+1}": None for i in range(4)}
res2 = {"latest": batch("jev-latest"), "preview": batch("jev-preview")}
print(f"  jev-latest : {res2['latest']}")
print(f"  jev-preview: {res2['preview']}")

# --- score the round against the pre-registered predictions ---
disagree = 0
for k in SAME_Q:
    a, b = res2['latest'].get(k), res2['preview'].get(k)
    if isinstance(a,(int,float)) and isinstance(b,(int,float)) and abs(a-b) > 0.15:
        disagree += 1
r1 = res1['mech_only'].get('reproduction')
ext_only = res1['mech+guar'].get('externality')
red_un   = res1['mech+guar'].get('reproduction')
r2 = res2['latest'].get('c1')
compat = None
if all(isinstance(v,(int,float)) for v in (ext_only, red_un)):
    compat = min(ext_only, red_un)

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = r1
rnd['predictions'][1]['result'] = disagree
rnd['predictions'][2]['result'] = compat
rnd['data'] = {"axes_by_evidence": res1, "cross_model": res2}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)

print()
show(1)
