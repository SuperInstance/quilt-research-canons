"""ROUND 11 — the simpler explanation.

Round 10 produced a result that contradicts round 6. With the SAME instruction for all
four questions, the batch survived (spread 0.86). Round 6 said identical instructions
collapse. Something else is going on.

The one structural difference: in round 10 every question NAMES ITS SUBJECT — "Is Subject
A backed by...", "Could an outsider run Subject B's validator...". In round 6 the questions
were identical and unnamed, so every question applied to the whole state at once.

So the mechanism may not be instruction-dedup at all. It may be SUBJECT IDENTIFICATION:
a question that says which part of the state it is about can be evaluated; a question that
applies to the whole state gets the whole state's answer, and N of those are the same.

That predicts something specific and testable: the collapse should track whether the
question identifies its subject, NOT whether the instructions are textually distinct.

PRE-REGISTERED.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(11, "is the collapse about subject identification, not instruction dedup", [
  {"id": "identification-is-the-mechanism", "kind": "bool", "predict": True,
   "claim": "A batch where all four questions are TEXTUALLY IDENTICAL and UNNAMED will "
            "collapse, while a batch where all four are TEXTUALLY IDENTICAL but each NAMES "
            "its subject will survive. If true, the mechanism is subject identification and "
            "instruction wording is irrelevant.",
   "result": None},
  {"id": "unnamed-always-collapses", "kind": "bool", "predict": True,
   "claim": "An unnamed question collapses regardless of what other questions are in the "
            "batch. Naming at least one other question in the batch will not rescue it.",
   "result": None},
  {"id": "single-identifier-suffices", "kind": "bool", "predict": True,
   "claim": "Naming the subject in a fixed PREFIX (e.g. 'Regarding Subject C: ...') is as "
            "effective as a fully distinct question. The mechanism needs a pointer, not a "
            "different question.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."
GENERIC = "Is this claim genuinely present and checkable by a third party?"

SUBJ = {
 "A": "A signed git tag records the source-tree sha256; a clean clone of the public repo reproduces that hash; anyone can run git and sha256sum to confirm it.",
 "B": "A validator refuses to pass unless the prior registry file is a byte-prefix of the new one. Both files, the validator and its tests are public and anyone can run it against any prior commit.",
 "C": "Every lane header carries a pre-registered budget cap and each verdict states the spend against it, recorded in a private tracker.",
 "D": "Every registration names its nearest prior and states the delta between them, in a private planning document.",
}
def state_of(keys): return "; ".join(f"Subject {k}: {SUBJ[k]}" for k in keys)

def batch_q(instrs, keys):
    q = {k: {"type":"noul","instructions":instrs[k],"criteria":{"true":T,"false":F}} for k in keys}
    try:
        a = _post(state_of(keys), q)["answers"]
        return {k: a[k].get("noul") for k in keys}
    except Exception:
        return {k: None for k in keys}
def sp(d):
    v=[x for x in d.values() if isinstance(x,(int,float))]
    return round(max(v)-min(v),3) if len(v)>1 else None

# 1. identical + UNNAMED (the round-6 shape)
unnamed = batch_q({k: GENERIC for k in "ABCD"}, list("ABCD"))
# 2. identical TEXT but each names its subject
named = batch_q({k: f"Regarding Subject {k}: {GENERIC}" for k in "ABCD"}, list("ABCD"))
# 3. one question, alone, unnamed (baseline)
solo = batch_q({"A": GENERIC}, ["A"])

print("=== identical wording, UNNAMED (round-6 shape) ===")
print(f"  {unnamed}  spread={sp(unnamed)}")
print("=== identical wording, SUBJECT-NAMED via fixed prefix ===")
print(f"  {named}  spread={sp(named)}")
print("=== single question alone ===")
print(f"  {solo}")

unnamed_collapses = sp(unnamed) is not None and sp(unnamed) < 0.10
named_survives    = sp(named) is not None and sp(named) >= 0.15
identification = unnamed_collapses and named_survives

# 4. one unnamed question + one named, is the unnamed one rescued?
mixed = batch_q({"A": f"Regarding Subject A: {GENERIC}", "B": GENERIC, "C": GENERIC, "D": GENERIC}, list("ABCD"))
mixed_b = mixed.get("B")
unnamed_stays_collapsed = isinstance(mixed_b,(int,float)) and (sp(unnamed) is not None) and abs(mixed_b - [v for v in unnamed.values() if isinstance(v,(int,float))][0]) < 0.10

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = bool(identification)
rnd['predictions'][1]['result'] = bool(unnamed_stays_collapsed)
rnd['predictions'][2]['result'] = bool(named_survives)
rnd['data'] = {"unnamed": unnamed, "unnamed_spread": sp(unnamed),
               "named": named, "named_spread": sp(named), "solo": solo,
               "mixed": mixed, "identification_is_mechanism": identification,
               "unnamed_stays_collapsed": unnamed_stays_collapsed}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(11)
show(11)
