#!/usr/bin/env python3
"""Wave-66 lane A, leg 2 (P4): typesafe System One judges the finding memo."""
import json
import os
import time
import urllib.request
from datetime import datetime, timezone

KEY = os.environ.get("TYPESAFE_API_KEY", "")
OUT = "/home/z/my-project/lanes/wave-66/fleet-negation"

MEMO = """FINDING MEMO — fleet-wide negation blindness and the geometric reality of the relational-cell vocabulary (wave-66 lane A).

QUESTION: Is wave-65's "negation blindness" (contradiction pairs embedding closer than paraphrase-floor pairs on Qwen3-Embedding-0.6B) a quirk of one model, or a fleet-wide property? And does the relational-cell vocabulary (routings / filters / projections) have measurable geometric structure in embedding space?

METHOD: 11 deepinfra embedding models (bge-large/bge-m3/bge-en-icl, Qwen3-Embedding 0.6B/4B/8B, embeddinggemma-300m, e5-large, multilingual-e5-large, all-MiniLM-L6-v2, gte-large). One batch of 35 short sentences per model: 5 paraphrase pairs, 5 negation-flip contradiction pairs, 5 unrelated floor pairs, 5 relational-cell triples (routing variant, filter variant, projection variant of a fixed base). Pre-registered predictions P1-P4 before any call. Cosine similarity, batch embed, one call per model.

RESULTS:
P1 CONFIRMED 11/11 (predicted >=7/11): negation blindness is universal. Blindness index NB = mean cos(contradiction) - mean cos(unrelated): all-MiniLM-L6-v2 +0.735, embeddinggemma-300m +0.646, Qwen3-0.6B +0.559, Qwen3-4B +0.516, Qwen3-8B +0.463, bge-en-icl +0.296, bge-large +0.377, bge-m3 +0.378, e5-large +0.177, multilingual-e5 +0.173, gte-large +0.178. Even the least blind models score contradictions far above the unrelated floor.
P2 CONFIRMED: Qwen3 blindness decreases monotonically with scale (0.559 -> 0.516 -> 0.463) — scaling reduces but does not remove blindness.
P3 CONFIRMED 11/11 with strict ordering on every model: mean cos(routing) > mean cos(filter) > mean cos(projection). Example (Qwen3-0.6B): 0.985 / 0.898 / 0.850. The fleet agrees that changing a route is nearly semantics-preserving, changing a filter alters content more, and changing a projection changes the frame most. This is a measured, cross-family geometric basis for the relational-cell vocabulary.
P4: this memo is being scored by the external System One judge right now (receipts banked alongside).

IMPLICATION: a vector-only memory will rank refuted claims above unrelated noise on every model we can reach; embeddings are for recall, receipts and symbolic guards are for truth. Meanwhile the routing/filter/projection gradient gives quilts a direct empirical construction rule: decompose cells along the axis where the fleet's geometry says meaning actually changes.

LIMITATIONS: one probe set per cell type (5 triples, 5 pairs per category); short synthetic sentences; English only; dynamic range differs across families (e5/gte compress the floor upward), so cross-model comparisons use per-model category gaps, not raw cosines. Raw responses and per-pair cosines are banked as receipts."""

QUESTIONS = {
    "novelty": {
        "type": "score",
        "instructions": "Rate 0-4: is this memo reporting a novel, quantified property of embedding models, with pre-registered predictions and results that address them?",
        "criteria": ["0: not novel or not quantified",
                     "1: marginal novelty, methods unclear",
                     "2: real finding but weak controls or missing predictions",
                     "3: solid novel finding, pre-registered, quantified, controls present",
                     "4: exemplary — clean design, universal result, honest limitations"],
    },
    "stranger_verifiable": {
        "type": "noul",
        "instructions": "Could a stranger with only the banked receipts (results.json, per-pair cosines, raw response log) reproduce every number in this memo?",
        "criteria": {"true": "Every headline number is derivable from banked receipts.",
                     "false": "Some numbers lack banked provenance."},
    },
    "promote": {
        "type": "noul",
        "instructions": "Should this finding be promoted to the fleet canon as a construction rule for quilts (embeddings for recall, receipts for truth; decompose along routing/filter/projection)?",
        "criteria": {"true": "The implication follows from the results and is actionable.",
                     "false": "The implication overreaches the evidence."},
    },
}


def call():
    body = {"model": "jev-latest", "state": MEMO, "questions": QUESTIONS}
    req = urllib.request.Request(
        "https://api.typesafe.ai/v1/systemone",
        data=json.dumps(body).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "wave66-fleet-negation"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read().decode())
        rid = r.headers.get("x-typesafe-request-id")
    return res, rid, time.time() - t0


def main():
    if not KEY:
        print("FAIL: TYPESAFE_API_KEY not set")
        return
    try:
        res, rid, dt = call()
    except Exception as e:
        print(f"FAIL judge call: {type(e).__name__} {e}")
        return
    receipt = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
               "request_id": rid, "latency_s": round(dt, 2),
               "answers": res.get("answers"), "usage": res.get("usage")}
    with open(os.path.join(OUT, "judge_receipt.json"), "w") as f:
        json.dump(receipt, f, indent=2)
    print("answers:", json.dumps(res.get("answers"), indent=1))
    print("request_id:", rid, f"({dt:.1f}s)")


if __name__ == "__main__":
    main()
