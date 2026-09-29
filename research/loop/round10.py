"""ROUND 10 — how far does the distinct-instruction fix go?

Round 9 found the collapse is an INSTRUCTION-DEDUP artifact: a batch where every
question carries the same instruction returns one number, and a batch where each question
carries a DISTINCT instruction separates (spread 0.24 vs 0.00).

If that is the mechanism, the fix is free — just make the instructions distinct. But
"0.24 is not 0.00" is not the same as "0.24 is correct". Three things to settle:

  A. Does it survive at 3 and 4, or does it degrade with size?
  B. Is the recovered value ACCURATE, or just different? Compare a distinct-instruction
     batch against separate calls on the same subjects.
  C. Does a synthetically-distinct instruction (same meaning, different words) work, or
     does the instruction have to be genuinely different? That decides whether the fix is
     real or a trick.

PRE-REGISTERED.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(10, "how far does the distinct-instruction fix go, and is it accurate", [
  {"id": "survives-at-3-and-4", "kind": "bool", "predict": True,
   "claim": "Distinct instructions will keep the per-item spread >= 0.15 at batch sizes 3 "
            "AND 4, not just 2. If it decays with size the fix is only good for pairs.",
   "result": None},
  {"id": "recovered-is-accurate", "kind": "bool", "predict": True,
   "claim": "A distinct-instruction batch will land within 0.15 of the SEPARATE-CALL value "
            "for each subject, i.e. it recovers the right number and not merely a "
            "different one.",
   "result": None},
  {"id": "semantic-distinctness-required", "kind": "bool", "predict": True,
   "claim": "Synonym-swapped instructions (same meaning, different words) will ALSO survive. "
            "If they do not, the fix depends on the instructions being genuinely different, "
            "not merely textually distinct.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."

SUBJ = {
 "A": "A signed git tag records the source-tree sha256; a clean clone of the public repo reproduces that hash; anyone can run git and sha256sum to confirm it.",
 "B": "A validator refuses to pass unless the prior registry file is a byte-prefix of the new one. Both files, the validator and its tests are public and anyone can run it against any prior commit.",
 "C": "Every lane header carries a pre-registered budget cap and each verdict states the spend against it, recorded in a private tracker.",
 "D": "Every registration names its nearest prior and states the delta between them, in a private planning document.",
}
# four genuinely DISTINCT questions, one per subject
DISTINCT = {
 "A": "Is Subject A backed by a signed artifact that a stranger could re-derive independently?",
 "B": "Could an outsider run Subject B's validator against the public history and reach a verdict?",
 "C": "Is Subject C's budget claim something a person outside the project could audit at all?",
 "D": "Does Subject D leave any trace an outside reviewer could examine?",
}
# same meaning, different words — a cosmetic rewrite of the SAME question
COSMETIC = {
 "A": "Is Subject A backed by a signed artifact that a stranger could re-derive independently?",
 "B": "Is Subject B backed by a signed artifact that a stranger could re-derive independently?",
 "C": "Is Subject C backed by a signed artifact that a stranger could re-derive independently?",
 "D": "Is Subject D backed by a signed artifact that a stranger could re-derive independently?",
}
# cosmetic = same MEANING per subject, varied wording per subject
COSMETIC_VARIED = {
 "A": "Does Subject A rest on a signed artifact an outsider could re-derive unaided?",
 "B": "Would an independent party be able to execute Subject B's validator over the public history and form a verdict?",
 "C": "Could anyone beyond the project scrutinise Subject C's stated budget at all?",
 "D": "Is anything an external reviewer could look at left behind by Subject D?",
}

def batch(instr_map, keys):
    q = {k: {"type":"noul","instructions":instr_map[k],"criteria":{"true":T,"false":F}} for k in keys}
    st = "; ".join(f"Subject {k}: {SUBJ[k]}" for k in keys)
    try:
        a = _post(st, q)["answers"]
        return {k: a[k].get("noul") for k in keys}
    except Exception:
        return {k: None for k in keys}

def one(k, instr):
    try:
        a = _post(f"Subject {k}: {SUBJ[k]}", {k:{"type":"noul","instructions":instr,"criteria":{"true":T,"false":F}}})["answers"]
        return a[k].get("noul")
    except Exception:
        return None

def spread(d):
    v=[x for x in d.values() if isinstance(x,(int,float))]
    return (max(v)-min(v)) if len(v)>1 else None

print("=== A: distinct instructions at batch size 2, 3, 4 ===")
b2 = batch(DISTINCT, ["A","B"]); b3 = batch(DISTINCT, ["A","B","C"]); b4 = batch(DISTINCT, list("ABCD"))
print(f"  n=2 spread={spread(b2)}  vals={list(b2.values())}")
print(f"  n=3 spread={spread(b3)}  vals={list(b3.values())}")
print(f"  n=4 spread={spread(b4)}  vals={list(b4.values())}")
survives = (spread(b2) or 0) >= 0.15 and (spread(b3) or 0) >= 0.15 and (spread(b4) or 0) >= 0.15

print()
print("=== B: is the recovered value ACCURATE? batch vs separate ===")
sep = {k: one(k, DISTINCT[k]) for k in "ABCD"}
errs = []
for k in "ABCD":
    bv, sv = b4.get(k), sep.get(k)
    if isinstance(bv,(int,float)) and isinstance(sv,(int,float)):
        errs.append(abs(bv-sv))
max_err = max(errs) if errs else None
print(f"  batched : {[f'{b4[k]:.2f}' if isinstance(b4.get(k),(int,float)) else '--' for k in 'ABCD']}")
print(f"  separate: {[f'{sep[k]:.2f}' if isinstance(sep.get(k),(int,float)) else '--' for k in 'ABCD']}")
print(f"  max error vs separate: {max_err}")
accurate = max_err is not None and max_err <= 0.15

print()
print("=== C: cosmetic variety — same MEANING per subject, varied WORDING ===")
cos = batch(COSMETIC, list("ABCD")); cos_spread = spread(cos)
var = batch(COSMETIC_VARIED, list("ABCD")); var_spread = spread(var)
uni = batch(COSMETIC, ["A"])  # sanity
print(f"  identical wording for all 4 : spread={cos_spread}  vals={list(cos.values())}")
print(f"  varied wording, same meaning: spread={var_spread}  vals={list(var.values())}")
# 'semantic distinctness required' predicted True; refuted if identical-wording also survives
same_means_survive = cos_spread is not None and cos_spread >= 0.15

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = bool(survives)
rnd['predictions'][1]['result'] = bool(accurate)
rnd['predictions'][2]['result'] = bool(same_means_survive)
rnd['data'] = {"b2": b2, "b3": b3, "b4": b4, "spreads": {"2":spread(b2),"3":spread(b3),"4":spread(b4)},
               "separate": sep, "max_err": max_err, "accurate": accurate,
               "identical_wording": cos, "identical_spread": cos_spread,
               "varied_wording": var, "varied_spread": var_spread,
               "same_means_survive": same_means_survive}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(10)
show(10)
