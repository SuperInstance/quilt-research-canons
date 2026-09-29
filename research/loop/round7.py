"""ROUND 7 — does the collapse apply to choice and score, or only to noul?

Everything in rounds 1-6 was `noul`. The operating rule ("one question per call")
is stated absolutely, but it is only supported for ONE of three question types. If
`choice` discriminates inside a batch, a multi-axis gate is recoverable with a mixed-type
call, and the rule softens from absolute to type-specific.

Also: is the collapse "averaging over the state" or "reads the first instruction only"?
A batched call whose two questions are on COMPLETELY UNRELATED TOPICS separates those.

PRE-REGISTERED.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/loop')
from loop import pre_register, debrief, show, _post

pre_register(7, "does the batch collapse hit choice and score, and is it averaging or first-instruction", [
  {"id": "collapse-hits-choice", "kind": "bool", "predict": True,
   "claim": "`choice` will ALSO collapse in a batch — two different choice questions in one "
            "call will return the same selected option or near-identical probabilities. The "
            "collapse is a property of the CALL, not of the noul type.",
   "result": None},
  {"id": "collapse-hits-score", "kind": "bool", "predict": True,
   "claim": "`score` will collapse similarly. NOTE: score is already known to be a constant "
            "generator, so this is partly confounded — the collapse test needs subjects whose "
            "STANDALONE scores differ, which for score may be impossible to construct.",
   "result": None},
  {"id": "unrelated-topics-still-collapse", "kind": "bool", "predict": True,
   "claim": "Two questions on COMPLETELY UNRELATED TOPICS (a software registry and a fishing "
            "catch log) will still collapse in a batch. That means the collapse is not "
            "averaging over related subjects — it is the call returning one answer.",
   "result": None},
])

T = "Yes, this is genuinely the case."
F = "No, this is not the case."
NQ = "Is this claim genuinely present and checkable by a third party?"

A = "A signed git tag records the source-tree sha256 and a clean clone reproduces it."
B = "Every lane header carries a pre-registered budget cap and each verdict states the spend."

def one(state, q, model="jev-latest", name="q"):
    try:
        a = _post(state, {name: {"type":"noul","instructions":q,"criteria":{"true":T,"false":F}}}, model)["answers"]
        return a[name].get("noul")
    except Exception:
        return None

def two_noul(a_state, b_state, model="jev-latest"):
    try:
        r = _post(f"Subject A: {a_state} Subject B: {b_state}", {
          "qa": {"type":"noul","instructions":NQ,"criteria":{"true":T,"false":F}},
          "qb": {"type":"noul","instructions":NQ,"criteria":{"true":T,"false":F}},
        }, model)["answers"]
        return r["qa"].get("noul"), r["qb"].get("noul")
    except Exception:
        return None, None

# --- H1: choice ---
def choice_q(text, options, model="jev-latest"):
    try:
        r = _post(text, {"ch": {"type":"choice","instructions":"Which best describes this?",
                                "criteria": {k: v for k, v in options.items()}}}, model)["answers"]["ch"]
        return r.get("choice"), r.get("probabilities")
    except Exception:
        return None, None

CH_A = "A signed git tag records the source-tree sha256 and a clean clone reproduces it. Anyone can verify this without asking the author anything."
CH_B = "Every lane header carries a pre-registered budget cap and each verdict states the spend against it. No outsider can check whether the stated spend matches reality."

# choice, SEPARATE calls
chA1, _ = choice_q(CH_A, {"verifiable": "Anyone can verify it independently.", "bookkeeping": "It is internal bookkeeping only."})
chB1, _ = choice_q(CH_B, {"verifiable": "Anyone can verify it independently.", "bookkeeping": "It is internal bookkeeping only."})
# choice, ONE batched call (two DIFFERENT choice questions)
try:
    r = _post(f"Subject A: {CH_A} Subject B: {CH_B}", {
      "a": {"type":"choice","instructions":"Which best describes Subject A?",
            "criteria":{"verifiable":"Anyone can verify it independently.","bookkeeping":"It is internal bookkeeping only."}},
      "b": {"type":"choice","instructions":"Which best describes Subject B?",
            "criteria":{"verifiable":"Anyone can verify it independently.","bookkeeping":"It is internal bookkeeping only."}},
    })["answers"]
    chA2, chB2 = r["a"].get("choice"), r["b"].get("choice")
    probs = (r["a"].get("probabilities"), r["b"].get("probabilities"))
except Exception:
    chA2, chB2, probs = None, None, None
print(f"  choice SEPARATE : A={chA1}  B={chB1}")
print(f"  choice BATCHED  : A={chA2}  B={chB2}   probs={probs}")

# --- H2: score ---
SC_A = "A signed git tag records the source-tree sha256 and a clean clone reproduces it; anyone can run this."
SC_B = "A folder containing a single README that says work in progress."
RUB = ["0 — nothing to check.", "1 — described only.", "2 — runnable by a stranger.", "3 — independently verifiable."]
def score_q(text, model="jev-latest"):
    try:
        r = _post(text, {"s": {"type":"score","instructions":"How checkable is this?","criteria":RUB}}, model)["answers"]["s"]
        return r.get("score")
    except Exception:
        return None
scA1, scB1 = score_q(SC_A), score_q(SC_B)
try:
    r = _post(f"Subject A: {SC_A} Subject B: {SC_B}", {
      "a": {"type":"score","instructions":"How checkable is Subject A?","criteria":RUB},
      "b": {"type":"score","instructions":"How checkable is Subject B?","criteria":RUB},
    })["answers"]
    scA2, scB2 = r["a"].get("score"), r["b"].get("score")
except Exception:
    scA2, scB2 = None, None
print(f"  score SEPARATE  : A={scA1}  B={scB1}")
print(f"  score BATCHED   : A={scA2}  B={scB2}")

# --- H3: unrelated topics ---
U1 = "A software repository seals each prediction line with the sha256 of that line's text, so editing a sealed prediction breaks its own hash."
U2 = "A fishing vessel logs each trip's catch, gear, depth, water temperature and fuel use, and the log cannot be edited after the trip ends without a visible correction entry."
uq = "Is this record keeping genuinely tamper-evident?"
un1, un2 = one(U1, uq, name="a"), one(U2, uq, name="b")
bu1, bu2 = two_noul(U1, U2)
print(f"  unrelated SEPARATE: U1={un1}  U2={un2}")
print(f"  unrelated BATCHED : U1={bu1}  U2={bu2}")

def spread(a, b):
    return abs(a-b) if isinstance(a,(int,float)) and isinstance(b,(int,float)) else None
ch_sep = None
if chA1 and chB1 and chA1 != chB1: ch_sep = 1
elif chA1 == chB1: ch_sep = 0
choice_collapses = bool(chA2 == chB2) if (chA2 and chB2) else None
score_collapses = bool(abs((scA2 or 0)-(scB2 or 0)) < 0.15) if (scA2 is not None and scB2 is not None) else None
un_sep, un_bat = spread(un1, un2), spread(bu1, bu2)
unrelated_collapses = bool(un_bat is not None and un_bat < 0.10)
print()
print(f"  choice: separate differ={ch_sep}  batched identical={choice_collapses}")
print(f"  score : batched spread={abs((scA2 or 0)-(scB2 or 0)):.3f} collapses={score_collapses}")
print(f"  unrelated topics: separate spread={un_sep}  batched spread={un_bat}  collapses={unrelated_collapses}")

st = json.load(open('/workspace/research/lanes/loop/loop_state.json'))
rnd = st['rounds'][-1]
rnd['predictions'][0]['result'] = choice_collapses
rnd['predictions'][1]['result'] = score_collapses
rnd['predictions'][2]['result'] = unrelated_collapses
rnd['data'] = {"choice_sep": [chA1, chB1], "choice_bat": [chA2, chB2],
               "score_sep": [scA1, scB1], "score_bat": [scA2, scB2],
               "unrelated_sep": [un1, un2], "unrelated_bat": [bu1, bu2]}
json.dump(st, open('/workspace/research/lanes/loop/loop_state.json','w'), indent=2)
print()
debrief(7)
show(7)
