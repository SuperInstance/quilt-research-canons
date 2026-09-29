"""ROUND 2 — designed by Round 1's REFUTATION, plus the anomaly the round stumbled into.

Round 1 refuted axis-complementarity: the reproduction axis scored 0.18 where externality
scored 0.64 on the same evidence, so reproduction was NOT carrying independent signal — it
was tracking something much weaker. A refutation is a pointer, so this round asks what the
reproduction axis is actually measuring.

Round 1 also produced an anomaly nobody designed: the SAME claim scored 0.83 when asked
alone and 0.19 when asked inside a 4-claim batch. Exp 6 measured POSITION and found
nothing, so the cause is not position. It is the state. That is the second question.

PRE-REGISTERED, with numbers, before the run.
"""
import sys, json, statistics
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(2, "what the reproduction axis measures, and why batched state collapses", [
  {"id": "repro-is-vestigial", "predict": 0.40, "tolerance": 0.25,
   "claim": "The reproduction axis will score the repro_heavy evidence NO HIGHER than the "
            "mech+guar evidence (delta < 0.10), i.e. it does not respond to actual independent "
            "reproduction and is vestigial rather than a real signal.",
   "result": None},
  {"id": "batching-is-a-dilution", "predict": 0.40, "tolerance": 0.30,
   "claim": "As the number of claims in the state grows 1 -> 2 -> 4, the per-claim score will "
            "DECREASE monotonically. Batching dilutes.",
   "result": None},
  {"id": "separation-is-the-remedy", "predict": 0.25, "tolerance": 0.25,
   "claim": "Presenting each claim in its OWN state (4 separate calls) will recover the "
            "single-claim score, i.e. the dilution is caused by sharing state, not by asking "
            "multiple questions.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."
Q = "Is this claim genuinely present and checkable by a third party?"

CLAIM = "A signed git tag records the source-tree sha256; a clean clone reproduces it; anyone can run this with git and sha256sum."

def one(state, model="jev-latest", name="q"):
    try:
        a = _post(state, {name: {"type":"noul","instructions":Q,"criteria":{"true":T,"false":F}}}, model)["answers"]
        return a[name].get("noul")
    except Exception:
        return None

def batch(states, model="jev-latest"):
    q = {f"c{i+1}": {"type":"noul","instructions":Q,"criteria":{"true":T,"false":F}} for i in range(len(states))}
    try:
        a = _post("; ".join(f"claim{i+1}: {s}" for i, s in enumerate(states)), q, model)["answers"]
        return [a[f"c{i+1}"].get("noul") for i in range(len(states))]
    except Exception:
        return [None]*len(states)

FILLER = [
  "Every lane header carries a pre-registered budget cap and each verdict states spend against it.",
  "A validator proves the old registry is a byte-prefix of the new across commits, and fails closed.",
  "Every registration cites its nearest prior and states the delta.",
  "A second independent implementation in a different language reproduces every digest, and both are public.",
]

# --- Q1: is the reproduction axis vestigial? ---
REPRO_AXIS = "Is this claim independently REPRODUCED — verified by a second implementation, or by a second party re-deriving the result, rather than asserted once?"
EXT_AXIS   = "Is this claim something a third party could verify with no access to this project?"
MEG = "A registry where each line is sha256-sealed, the file is append-only, and a validator proves the old file is a byte-prefix of the new across commits."
REPRO_HEAVY = MEG + " Two independent implementations in different languages both reproduce every digest, and both are public with a passing conformance suite."

def axes(state):
    q = {k: {"type":"noul","instructions":v,"criteria":{"true":T,"false":F}} for k, v in
         {"repro":REPRO_AXIS, "ext":EXT_AXIS}.items()}
    try:
        a = _post(state, q)["answers"]
        return a["repro"].get("noul"), a["ext"].get("noul")
    except Exception:
        return None, None

r_meg, e_meg     = axes(MEG)
r_heavy, e_heavy = axes(REPRO_HEAVY)
repro_delta = (r_heavy - r_meg) if isinstance(r_meg,(int,float)) and isinstance(r_heavy,(int,float)) else None
ext_delta  = (e_heavy - e_meg) if isinstance(e_meg,(int,float)) and isinstance(e_heavy,(int,float)) else None
print(f"  mech+guar      repro={r_meg}  ext={e_meg}")
print(f"  repro_heavy    repro={r_heavy}  ext={e_heavy}")
print(f"  delta from adding REAL independent reproduction: repro {repro_delta:+.3f}  ext {ext_delta:+.3f}"
      if repro_delta is not None else "  delta: n/a")

# --- Q2 + Q3: batching dilution and whether separation remedies it ---
alone = one(CLAIM)
b2 = batch([CLAIM, FILLER[0]])
b4 = batch([CLAIM] + FILLER[:3])
sep4 = [one(c) for c in [CLAIM] + FILLER[:3]]
print(f"  alone        {alone}")
print(f"  batch of 2   {b2[0]}")
print(f"  batch of 4   {b4[0]}")
print(f"  4 separate   {[f'{v:.2f}' if isinstance(v,(int,float)) else '--' for v in sep4]}")

monotone = (isinstance(alone,(int,float)) and isinstance(b2[0],(int,float)) and isinstance(b4[0],(int,float))
            and alone >= b2[0] >= b4[0])
recovered = (isinstance(alone,(int,float)) and isinstance(sep4[0],(int,float))
             and abs(sep4[0] - alone) < 0.15)

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = repro_delta
rnd['predictions'][1]['result'] = 1 if monotone else 0
rnd['predictions'][2]['result'] = sep4[0] if isinstance(sep4[0],(int,float)) else None
rnd['data'] = {"meg": {"repro": r_meg, "ext": e_meg}, "repro_heavy": {"repro": r_heavy, "ext": e_heavy},
               "alone": alone, "batch2": b2[0], "batch4": b4[0], "separate4": sep4}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
show(2)
