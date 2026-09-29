#!/usr/bin/env python3
"""
sow.py — the seed / okra / big loop.

THE IDEA

Casey's framing, built:

  1. A big model (or me) has a real task. Deep-think it. That is the EXPENSIVE token.
  2. Spend it once, and save the whole chain: the task, the thinking, the answer that
     would be ACCEPTABLE, and what a good decomposition of the task looks like.
  3. That saved chain is a TRAINING EXAMPLE. A small model reads it and produces a
     first-pass decomposition of a SIMILAR task, cheaply, outside the big model's budget.
  4. The big model looks at the small model's output and judges one of three things:
       ACCEPT   - the small answer would pass
       SALVAGE  - close, but not as-is; here is why, and the acceptable variant
       REJECT   - wrong, and here is the specific reason
  5. That verdict is saved. It is supervision generated at the exact point where it is
     most informative, and it compounds: round N's REJECTs are round N+1's training data.

The point is NOT that the small model is better. The point is that a small model's
output can be **decomposed** into what it was actually doing, and the decomposition is
where the learning signal is. A wrong answer with a legible failure mode is worth more
than a right answer with no trace.

Every round emits a training record. The corpus is the product.

USAGE
    python3 sow.py --self-test
    python3 sow.py --probe            # which small models are actually reachable
    python3 sow.py --round            # run a real round over the saved seeds
"""
from __future__ import annotations
import json, os, re, sys, time, urllib.request, urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

DI = os.environ.get("DEEPINFRA_TOKEN")
DI_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
MOTH = os.environ.get("MOTH_API_KEY")
MOTH_URL = "https://api.mothquantum.com/api/v1"
JEV = os.environ.get("TYPESAFEAI_KEY")
JEV_URL = "https://api.typesafe.ai/v1/systemone"

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = os.path.join(HERE, "seeds.jsonl")
TRACES = os.path.join(HERE, "traces.jsonl")

# The ladder. Cheap-to-capable, in the order they get consulted.
SMALL = [
    "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
    "google/gemma-3-27b-it",
    "meta-llama/Llama-3.3-70B-Instruct",
    "deepseek-ai/DeepSeek-V3",
]

# ── the seed: a saved chain, and it is the training example ────────────────────

@dataclass
class Seed:
    """One expensive piece of thinking, saved whole.

    `answer` is the reference. `accept` says what a PASSING answer would look like,
    which is not the same thing — a small model that produces a different shape of
    answer and is still acceptable is a success, and the accept_criteria are what
    let the judge know that.
    """
    id: str
    task: str
    thinking: str          # the chain, condensed but not destroyed
    answer: str            # the reference answer
    accept: str            # what would count as passing
    decompose: str         # an example decomposition, for the small model to pattern on
    tags: list = field(default_factory=list)

# The judge is non-deterministic at temperature 0. Verified: identical input, identical
# settings, three consecutive calls -> ACCEPT, REJECT, (and a third). So a verdict is a
# SAMPLE. Run the judge N times and keep the distribution. This is the same discipline
# as the JEV gate work: a number from one call is not a measurement, and the
# distribution is the thing worth recording.
JUDGE_RUNS = 3
JUDGE_UNANIMITY = True

def di(model: str, prompt: str, max_tokens=900, temperature=0.7):
    req = urllib.request.Request(DI_URL,
        data=json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                         "max_tokens": max_tokens, "temperature": temperature}).encode(),
        headers={"Authorization": f"Bearer {DI}", "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"__ERR__ {e}"

def moth_engine(engine: str, params: dict, poll=6):
    """submit -> poll -> result. The QRNG engine returns a CHSH Bell witness, which
    means the draw is checkable by a third party without trusting us."""
    req = urllib.request.Request(f"{MOTH_URL}/engines/{engine}/process",
        data=json.dumps({"params": params}).encode(),
        headers={"Authorization": f"Bearer {MOTH}", "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            job = json.loads(r.read())["job_id"]
    except Exception as e:
        return {"error": f"submit: {e}"}
    for _ in range(poll):
        time.sleep(2.5)
        try:
            req = urllib.request.Request(f"{MOTH_URL}/jobs/{job}/status",
                headers={"Authorization": f"Bearer {MOTH}", "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=25) as r:
                st = json.loads(r.read()).get("status")
            if st in ("completed", "failed", "cancelled"):
                break
        except Exception:
            pass
    try:
        req = urllib.request.Request(f"{MOTH_URL}/jobs/{job}/result",
            headers={"Authorization": f"Bearer {MOTH}", "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return {"job_id": job, "result": json.loads(r.read()).get("result")}
    except Exception as e:
        return {"job_id": job, "error": f"result: {e}"}

def jev_noul(state: str, instructions: str, true: str, false: str):
    req = urllib.request.Request(JEV_URL,
        data=json.dumps({"model": "jev-latest", "state": state,
                         "questions": {"q": {"type": "noul", "instructions": instructions,
                                             "criteria": {"true": true, "false": false}}}}).encode(),
        headers={"Authorization": f"Bearer {JEV}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["answers"]["q"].get("noul")
    except Exception as e:
        return None
