#!/usr/bin/env python3
"""Wave-69 optional ideation: 9-model adversarial kill-round against P2, typesafe-judged.

Pre-registered frame (README): ask every fleet member to predict what
opcode-sequence features CANNOT capture — i.e. design the kill-round against
our own P2 claim family — then typesafe System One judges novelty + soundness.
Budget: 9 deepinfra chat calls (1/model, max_tokens=4000 — wave-68 rescue
lesson for reasoning models), 19 typesafe calls (2/response + 1 empty-input
noul-floor calibration probe) <= 25 cap. No moth calls.
"""
import json
import os
import time
import urllib.request

DI = os.environ["DEEPINFRA_TOKEN"]
TS = os.environ["TYPESAFE_API_KEY"]
HERE = os.path.dirname(os.path.abspath(__file__))

MODELS = ["Qwen/Qwen3.8-Flash", "ibm-granite/granite-4.2-30b", "inclusionAI/Ling-3.0-flash",
          "meta-models/Muse-Glimmer-30B", "nvidia/NVIDIA-Nemotron-3.5-Lightning",
          "thinkingmachines/Inkling-Small", "deepseek-ai/DeepSeek-V4-Flash-Vision-Exp",
          "ByteDance/Seed-2.0-mini", "XiaomiMiMo/MiMo-V2.6-Flash"]

RECEIPT = """EXPERIMENT RECEIPTS (waves 68-69, pre-registered, negatives kept):
Corpus: 7 kernel cells (route,crdt,time,quf,world,proof,engine) of a C cell
runtime; 5+1 opcode contract (BIND/LINK/EFFECT/VIEW/TICK/FORGET); cells never
call each other; they meet only in the shared contract. Exercise journal:
seeded per-cell schedules emitting {op, call, args, state} steps; 4 schedules
(A linear, B reverse, C interleave, D split-swap) reorder the same phases on
the same contract (payload multiset provably schedule-invariant).

Wave-68 law (triple-replicated): embedding geometry is relation-blind — it
recovers cell IDENTITY (T1 +0.09..+0.52) and vocabulary, never topology /
dialect role. Dialect recovery (between-organs {route,quf,time} vs in-cell
{crdt,proof,world}) killed on interfaces AND traces; TF histograms dominate
neural embeddings for identity (TF-T1 +0.879 vs +0.52) but TF-C1 = 0.

Wave-69 receipts:
- Identity is schedule-invariant (T1 unchanged under 4 schedules, z>90, 5/5
  embedders); dialect stays dead under every schedule (C1 inside null 5/5).
- BUT schedule-blindness FAILED: embeddings weakly DO see the schedule
  (S1 +0.003..+0.052, p=0.002 on 5/5 embedders, also on reseeded payloads).
  Mechanism receipt: S1 magnitude tracks each encoder's order sensitivity
  (order-twin cos 0.995->S1 0.003 for e5; 0.940->0.052 for Qwen-0.6B).
- P2 KILLED: cheap sequence features (bigram/trigram-TF cos, Levenshtein,
  Needleman-Wunsch, Smith-Waterman) over the op-token journal are ALIVE to
  order (cross-cell schedule recovery p<=0.002 on 5/5 instruments) but the
  TRUE dialect split ranks 9-18 of 20 possible 3/3 partitions (chance) on
  ALL 5 instruments x 2 encodings x 4 schedules. 0/5 pass the dialect bar.
- Dissociation: sequence features see ORDER not DIALECT; embeddings see
  IDENTITY barely ORDER; NEITHER sees dialect/topology role."""

PROMPT = RECEIPT + """

You are a fleet member running the KILL-ROUND against our own claims. Assume
we are tempted to conclude "the relation lives only in contract + runtime
addressing". Attack this. Reply in EXACTLY this format:

KILL_CLAIM: <the single strongest thing opcode-sequence features (or any
cheap journal-derived feature) provably CANNOT capture in this system — name
the concrete relational structure>
INSTRUMENT: <a concrete artifact (name it) that would demonstrate that
blindness, or expose our receipts as artifacts>
FALSIFIER: <the observation that would kill YOUR kill-claim>
ARTIFACT_RISK: <one way our P1/P2 receipts could be instrumentation artifacts
(duplicates, length confounds, schedule-length coupling), and the control
that would expose it>"""

def chat(model, user, max_tokens=4000):
    body = {"model": model, "messages": [{"role": "user", "content": user}],
            "max_tokens": max_tokens, "temperature": 0.8}
    for attempt in range(3):
        try:
            req = urllib.request.Request("https://api.deepinfra.com/v1/openai/chat/completions",
                data=json.dumps(body).encode(),
                headers={"Authorization": f"Bearer {DI}", "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
                c = d["choices"][0]["message"].get("content") or ""
                rc = d.get("usage", {}).get("completion_tokens")
                return c, rc
        except Exception as e:
            if attempt == 2:
                return f"[ERROR {type(e).__name__}: {str(e)[:100]}]", None
            time.sleep(3)

def typesafe(state, questions):
    body = {"model": "jev-latest", "state": state, "questions": questions}
    req = urllib.request.Request("https://api.typesafe.ai/v1/systemone",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {TS}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())

ts_calls = 0
def judge_kill(text):
    global ts_calls
    state = ("A research fleet probes a C cell-runtime (7 kernel cells, shared "
             "5+1 opcode contract, journal-based evaluation). Established "
             "receipts: embedding geometry recovers cell identity but not "
             "dialect role; opcode-sequence features (n-gram TF, edit distance, "
             "alignment) recover schedule/order but rank the true dialect split "
             "at chance. A fleet member designed a kill-round attack:\n\n" + text[:1800])
    q = {"novelty": {"type": "noul", "instructions":
                     "How novel is this kill-round claim/instrument relative to the stated receipts? 0 = restatement, 1 = genuinely new."},
         "soundness": {"type": "score", "instructions":
                       "Rate the soundness of the kill-claim and its falsifier as experimental design. 0 = vacuous, 1 = weak, 2 = plausible, 3 = strong, 4 = airtight.",
                       "criteria": {"vacuous": 0, "weak": 1, "plausible": 2, "strong": 3, "airtight": 4}}}
    ts_calls += 1
    try:
        d = typesafe(state, q)
        a = d.get("answers", {})
        return {"novelty": a.get("novelty", {}).get("noul"),
                "soundness": a.get("soundness", {}).get("score")}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:120]}"}

proposals, judged = {}, {}
for m in MODELS:
    short = m.split("/")[-1]
    t0 = time.time()
    resp, rc = chat(m, PROMPT)
    proposals[m] = {"text": resp, "completion_tokens": rc}
    with open(f"{HERE}/ideation_proposals.json", "w") as f:
        json.dump(proposals, f, indent=1)
    j = judge_kill(resp)
    judged[m] = j
    with open(f"{HERE}/ideation_judgements.json", "w") as f:
        json.dump(judged, f, indent=1)
    print(f"{short} ({time.time()-t0:.0f}s, {rc} tok): {len(resp)} chars | judge {j}", flush=True)

# noul-floor calibration probe (wave-68 datum replication), 1 extra call
ts_calls += 1
try:
    d = typesafe("Empty state.", {"novelty": {"type": "noul", "instructions": "Rate novelty."}})
    floor = d.get("answers", {}).get("novelty", {}).get("noul")
except Exception as e:
    floor = f"ERROR {e}"
print(f"empty-input noul floor: {floor} | total typesafe calls: {ts_calls}")
with open(f"{HERE}/ideation_receipt.json", "w") as f:
    json.dump({"typesafe_calls": ts_calls, "noul_floor_empty": floor,
               "models": MODELS, "judged": judged}, f, indent=1)
print("ideation complete")
