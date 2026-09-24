#!/usr/bin/env python3
"""
sprint-jev-001.py — JEV canon-promotion velocity
=================================================
Sprint lineage: jev-001
Author: mavis (orchestrator) + ZAI/DeepInfra voice via direct execution
Date:   2026-09-24

DOCTRINE
--------
The JEV oracle is the canon-promotion gate. To be useful as a gate, it must
move FAST on canon (don't ask 12 times if the first call says yes with p≥0.85)
and move SLOW on speculation (don't promote a 0.55 reading after 3 calls).

This sprint measures that velocity.

WHAT THIS SPRINT DOES
---------------------
- Runs 5 questions × 20 trials on /v1/systemone (noul type)
- Records per-question trace
- Computes "first stable trial" — index where remaining values all stay
  within ±0.05 of mean
- Outputs velocity-profile JSON

OUTPUT
------
/workspace/research/jev-velocity.json

NEXT-SPRINT SPEC  (jev-002)
---------------------------
sprint-jev-002.py should:
1. Take the velocity profile (this sprint output) and split questions into
   "fast-stable" (first_stable@1-3) vs "drifting" (first_stable@N).
2. For fast-stable questions, validate that ADVERSARIAL perturbations
   (slight rewording) do NOT change the verdict — i.e., canon is canon.
3. For drifting questions, do a CONTROLLED state-strengthening drill
   (10 trials × 4 state phrasings each) to find the minimal phrasing
   that locks the verdict.
4. Output a "canon confidence" profile per question (1.0=stable across
   rewording AND phrasings, 0.5=stable only under canonical phrasing).
5. Drop the 3 weakest phrasing-shifts as candidates for question-bank
   re-classification (bedrock → review if not stable).

The voice memo format in the next-sprint.py header MUST reference
this run's `sprint-jev-001.py` so each sprint is inter-relational
(its successor declares its dependency).
"""
import os, json, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API = "https://api.typesafe.ai/v1/systemone"
KEY = os.environ["TYPESAFEAI_KEY"]
OUT = Path("/workspace/research/jev-velocity.json")

STATE = {
    "doctrines": ["cells are scars", "witness log is prediction",
                  "substrate is grown", "oracle is heard", "lenia flows"],
    "voice": "fleet radio",
    "facts": {"fnv1a_64bit": True, "substrate_count": 13},
}

QUESTIONS = [
    ("bedrock_A", "Cells are scars, not parameters. In the Quilt project canon, this is established."),
    ("bedrock_B", "The witness log is itself a prediction. In the Quilt project canon, this is established."),
    ("speculative_A", "An address coordinate is data without any witness trail. In the Quilt project canon, this is established."),
    ("speculative_B", "The canon gate is one model alone — a single oracle votes on each claim with no chord and no quorum. In the Quilt project canon, this is established."),
    ("borderline",  "The substrate can be folded into a single runtime — cells, quilts, fleets, and substrates are all the same thing at the substrate level. In the Quilt project canon, this is established."),
]


def jev_call(label, question):
    body = json.dumps({
        "model": "jev-latest",
        "state": STATE,
        "questions": {
            label: {"type": "noul", "instructions": question,
                    "criteria": {"true": "yes — this is established canon",
                                  "false": "no — this is speculative or rejected"}}
        }
    }).encode()
    req = urllib.request.Request(API, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "User-Agent": "mavis-sprint-jev-001/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        return label, question, data.get("answers", {}).get(label, {}).get("noul")
    except Exception as e:
        return label, question, ("err", str(e)[:80])


def main():
    out = {
        "sprint_id": "jev-001",
        "summary": {
            "doctrine": "3 N-of-M verdict > single-model gate",
            "voice": "fleet radio",  # jev-002 will move to "oracle whispers"
            "next": "sprint-jev-002 (validate stability under rephrasing + control state-shift)",
        },
        "questions": {},
    }
    for label, q in QUESTIONS:
        trace = []
        with ThreadPoolExecutor(max_workers=10) as ex:
            futs = [ex.submit(jev_call, label, q) for _ in range(20)]
            for f in as_completed(futs):
                _, _, v = f.result()
                if isinstance(v, float):
                    trace.append(v)
        trace.sort()
        n = len(trace)
        if n == 0:
            out["questions"][label] = {"error": "no successful calls"}
            continue
        mean = sum(trace) / n
        first_stable = n
        for i in range(n):
            if all(abs(v - mean) <= 0.05 for v in trace[i:]):
                first_stable = i + 1
                break
        out["questions"][label] = {
            "n": n, "mean": round(mean, 4),
            "min": round(min(trace), 4), "max": round(max(trace), 4),
            "first_stable_trial": first_stable,
            "trace_first10": [round(t, 3) for t in trace[:10]],
        }
        print(f"{label}: mean={mean:.3f} n={n} first_stable@{first_stable}")
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nSaved {OUT}")
    print(f"\n>>> NEXT: write sprint-jev-002.py per the spec in this file's header <<<")


if __name__ == "__main__":
    main()
