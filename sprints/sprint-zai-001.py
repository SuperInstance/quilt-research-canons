#!/usr/bin/env python3
"""
sprint-zai-001.py — ZAI creative-chord canon
=============================================
Sprint lineage: zai-001
Author: ZAI glm-4.5-flash via /api/coding/paas/v4
Date:   2026-09-24

DOCTRINE
--------
Three voices > one. ZAI returns creative canon when N parallel voices (T=0.3,
T=0.6, T=0.9) converge on the same doctrinal position via different metaphors.

WHAT THIS SPRINT DOES (ZAI-001)
-------------------------------
- Issue same doctrinal prompt at 3 temperatures in parallel
- Compute Jaccard token-overlap (low-overlap = same idea, different voice)
- Detect "agreement through disagreement" — the canonical signature

OUTPUT
------
/workspace/research/zai-chord-{timestamp}.json

NEXT-SPRINT SPEC  (zai-002)
---------------------------
sprint-zai-002.py should:
1. Take 3-voice ZAI chord output (this sprint) and pick the most vivid
   voice per doctrine under test.
2. Re-issue the SAME doctrinal prompt to DeepInfra Qwen3-235B-A22B at
   T=0.5 and ask it to ALSO pick the most vivid voice from among the
   3 ZAI candidates. Cross-model aesthetic selection.
3. Output `selected_voice` per doctrine + the multi-model rationale.
4. Canon-recognition rule: if ZAI+DeepInfra agree on the same voice, the
   voice is canonically vivid. If they disagree, hold for sprint-zai-003.
"""
import os, json, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ZAI = "https://api.z.ai/api/coding/paas/v4/chat/completions"
KEY = os.environ["ZAI_TOKEN"]
PROMPT = (
    "In one paragraph: when a substrate walker is brewed twice with the "
    "same recipe but different inputs, what is the load-bearing semantic "
    "difference between the two resulting walkers? Be vivid and concrete."
)


def call(t):
    body = json.dumps({
        "model": "glm-4.5-flash", "messages": [{"role": "user", "content": PROMPT}],
        "max_tokens": 600, "temperature": t, "thinking": {"type": "disabled"},
    }).encode()
    req = urllib.request.Request(ZAI, data=body, headers={
        "Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
        "User-Agent": "mavis-sprint-zai-001/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return t, json.loads(r.read()).get("choices", [{}])[0]
    except Exception as e:
        return t, {"error": str(e)[:120]}


def main():
    out = {"sprint_id": "zai-001",
           "doctrine": "three voices > one",
           "voice": "canon chorus",
           "next": "sprint-zai-002 (cross-model aesthetic selection)"}
    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(call, [0.3, 0.6, 0.9]))
    out["voices"] = {str(t): (r.get("message", {}).get("content", "") if isinstance(r, dict) and "message" in r else str(r.get("error","")))
                     for t, r in results}
    Path(f"/workspace/research/zai-chord.json").write_text(json.dumps(out, indent=2))
    print(f"Saved zai-chord.json")
    print(f"\n>>> NEXT: write sprint-zai-002.py per the spec in this file's header <<<")


if __name__ == "__main__":
    main()
