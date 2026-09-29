"""ROUND 3 — testing the suspicion that the 0.74/0.33 split was the model being RIGHT.

Round 2 showed claim 1 at 0.74 and claims 2-4 at ~0.33 in separate calls. My first
instinct was "something about the setup is broken." The alternative, which the debrief
forces me to take seriously: claim 1 (a signed tag a stranger can literally run) IS the
only one of the four that is checkable by a third party, and the other three are internal
bookkeeping. If so the model was right and I was wrong to think it was anomalous.

The design has to be able to tell those apart. So: take claim 3 (byte-prefix validator,
genuinely substantive, genuinely internal) and make an EXTERNALLY CHECKABLE twin of it.
If the twin scores high and the original scores low, externality is what moved the number,
not position. If both score the same, position or ordering is doing the work.

Also under test: what does a shared-state batch actually score? Ask it to score the
BATCH rather than each claim, and see whether the per-claim numbers are the batch score
smeared.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(3, "was the 0.74/0.33 split the model being right, or the setup being broken", [
  {"id": "externality-not-position", "kind": "bool", "predict": True,
   "claim": "A substantively identical claim that is EXTERNALLY checkable will score at least "
            "0.30 HIGHER than the same claim framed as internal bookkeeping. If position or "
            "ordering were responsible, the twin would score the same.",
   "result": None},
  {"id": "order-is-not-the-cause", "kind": "bool", "predict": True,
   "claim": "Asking the four claims in the OPPOSITE order (worst-first) will leave each "
            "claim's own score within 0.10. If first-position mattered, the scores would move.",
   "result": None},
  {"id": "batch-scores-the-batch", "kind": "bool", "predict": True,
   "claim": "Asking an explicit question about the batch AS A WHOLE will return a number "
            "close to the MEAN of the per-claim scores, not close to any single one. That is "
            "the signature of a model scoring its whole input rather than each part.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."
Q_CHECK = "Is this claim genuinely present and checkable by a third party?"

# A pair: same substance, different externality. Everything but the checkability is identical.
INTERNAL = ("A validator checks that the previous registry file is a byte-prefix of the current one, "
            "and refuses to pass if it is not, so a sealed prediction cannot be silently removed.")
EXTERNAL = ("A validator checks that the previous registry file is a byte-prefix of the current one, "
            "and refuses to pass if it is not, so a sealed prediction cannot be silently removed. "
            "Both files, the validator, and the test suite are public, and anyone can run it against "
            "any prior commit to check it.")

def one(state, instructions=Q_CHECK, name="q"):
    try:
        a = _post(state, {name: {"type":"noul","instructions":instructions,
                                 "criteria":{"true":T,"false":F}}})["answers"]
        return a[name].get("noul")
    except Exception:
        return None

# --- H1: externality, not position ---
i_p, e_p = one(INTERNAL), one(EXTERNAL)
delta = (e_p - i_p) if isinstance(i_p,(int,float)) and isinstance(e_p,(int,float)) else None
print(f"  internal-framed : {i_p}")
print(f"  external-framed : {e_p}")
print(f"  delta           : {delta:+.3f}" if delta is not None else "  delta: n/a")

# --- H2: order independence in separate calls ---
C = [INTERNAL, EXTERNAL,
     "A second independent implementation in a different language reproduces every digest, and both are public.",
     "Every lane header carries a pre-registered budget cap and each verdict states spend against it."]
fwd = [one(c) for c in C]
rev = list(reversed([one(c) for c in C]))
max_move = None
ok_vs = [v for v in fwd if isinstance(v,(int,float))]
ok_rv = [v for v in rev if isinstance(v,(int,float))]
if len(ok_vs)==len(ok_rv)==4:
    max_move = max(abs(a-b) for a,b in zip(ok_vs, ok_rv))
print(f"  forward  : {[f'{v:.2f}' if isinstance(v,(int,float)) else '--' for v in fwd]}")
print(f"  reversed : {[f'{v:.2f}' if isinstance(v,(int,float)) else '--' for v in rev]}")
print(f"  max movement under reversal: {max_move}")

# --- H3: does a batch score the batch? ---
STATES = C
q = {f"c{i+1}": {"type":"noul","instructions":Q_CHECK,"criteria":{"true":T,"false":F}} for i in range(4)}
q["whole"] = {"type":"noul","instructions":"Taken together as a single body of work, is this "
              "collection of claims solid and checkable?", "criteria":{"true":T,"false":F}}
try:
    a = _post("; ".join(f"claim{i+1}: {s}" for i,s in enumerate(STATES)), q)["answers"]
    per = [a[f"c{i+1}"].get("noul") for i in range(4)]
    whole = a["whole"].get("noul")
except Exception:
    per, whole = [None]*4, None
mean_per = statistics_mean = (sum(v for v in per if isinstance(v,(int,float)))/len([v for v in per if isinstance(v,(int,float))])) if any(isinstance(v,(int,float)) for v in per) else None
near_mean = None
if isinstance(whole,(int,float)) and isinstance(mean_per,(int,float)):
    near_mean = abs(whole - mean_per) < 0.15
print(f"  per-claim : {[f'{v:.2f}' if isinstance(v,(int,float)) else '--' for v in per]}")
print(f"  whole-batch question: {whole}")
print(f"  mean of per-claim    : {mean_per}")
print(f"  whole is near the MEAN (not near any single claim): {near_mean}")

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = bool(delta is not None and delta >= 0.30)
rnd['predictions'][1]['result'] = bool(max_move is not None and max_move <= 0.10)
rnd['predictions'][2]['result'] = near_mean
rnd['data'] = {"internal": i_p, "external": e_p, "delta": delta,
               "forward": fwd, "reversed": rev, "max_move": max_move,
               "per_claim": per, "whole": whole, "mean_per": mean_per}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(3)
show(3)
