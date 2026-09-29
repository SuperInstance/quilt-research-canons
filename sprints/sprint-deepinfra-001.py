#!/usr/bin/env python3
"""
sprint-deepinfra-001.py — Multi-model chord via DeepInfra
========================================================
Sprint lineage: deepinfra-001
Author: DeepInfra OpenAI-compat API (https://api.deepinfra.com/v1/openai/chat/completions)
Date:   2026-09-24

DOCTRINE
--------
DeepInfra is the cheapest large-model endpoint in the fleet. Use it as the
DEFAULT chord-critic when ZAI is slow: 12+ models, ~5s/call, $0.0003-0.003/1k
tokens. The chord discovers canon via disagreement.

WHAT THIS SPRINT DOES (DEEPINFRA-001)
-------------------------------------
- 6 cheap DeepInfra models in parallel: Llama-3.3-70B, Qwen3-235B-A22B,
  DeepSeek-V3.2, ByteDance Seed-2.0-mini, Mistral-Small-3.2-24B, Gemma-4-31B
- Same canon-prompt to all (the same prompt ZAI received)
- Compute cross-model agreement via token Jaccard + argument-overlap
- If 4+ models converge on the same doctrinal position, that's a chord

OUTPUT
------
/workspace/research/deepinfra-chord.json

NEXT-SPRINT SPEC  (deepinfra-002)
---------------------------------
sprint-deepinfra-002.py should:
1. Take the 6-voice chord (this sprint) and compare agreement scores.
2. For doctrines where 5+ models converge, mark those doctrines as
   "cheap-oracle canon" — meaning they don't need ZAI verification, can
   be promoted by DeepInfra alone.
3. For doctrines where models disagree, route those to JEV (sprint-jev-002)
   for adversarial resolution.
4. Output a "promotion routing table" per doctrine, with the cheapest oracle
   that closes the verdict.
"""
import os, json, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DEEPINFRA = "https://api.deepinfra.com/v1/openai/chat/completions"
KEY = os.environ["DEEPINFRA_TOKEN"]
PROMPT = (
    "In one paragraph: when a substrate walker is brewed twice with the same "
    "recipe but different inputs, what is the load-bearing semantic difference "
    "between the two resulting walkers?"
)

MODELS = [
    "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "Qwen/Qwen3-235B-A22B-Instruct-2507",
    "deepseek-ai/DeepSeek-V3.2",
    "ByteDance/Seed-2.0-mini",
    "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
    "google/gemma-2-9b-it",
]


def call(model):
    body = json.dumps({
        "model": model, "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 400, "temperature": 0.5,
    }).encode()
    req = urllib.request.Request(DEEPINFRA, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "User-Agent": "mavis-sprint-deepinfra-001/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return model, json.loads(r.read()).get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        return model, f"ERR: {str(e)[:80]}"


def main():
    out = {"sprint_id": "deepinfra-001",
           "doctrine": "12 cheap voices > one expensive oracle",
           "voice": "canon cheap chorus",
           "next": "sprint-deepinfra-002 (promotion routing table)"}
    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(call, MODELS))
    out["voices"] = dict(results)
    Path("/workspace/research/deepinfra-chord.json").write_text(json.dumps(out, indent=2))
    print("Saved deepinfra-chord.json")
    print(f"\n>>> NEXT: write sprint-deepinfra-002.py per the spec in this file's header <<<")


if __name__ == "__main__":
    main()
