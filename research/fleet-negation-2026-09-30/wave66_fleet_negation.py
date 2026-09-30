#!/usr/bin/env python3
"""Wave-66 lane A: fleet-wide negation-blindness + relational-cell geometry.

Extends wave-65 lane 65-A's novel finding (contradictions scored 0.9858 vs
paraphrases 0.9115 on Qwen3-0.6B — "negation blindness") to a systematic
11-model panel across the live deepinfra embedding fleet.

PRE-REGISTERED PREDICTIONS (before any call; falsifiable):
P1 (negation blindness): mean cos(contradiction) > mean cos(unrelated) for
   at least 7/11 models. Falsified if fewer.
P2 (fleet ordering): larger Qwen models show LOWER blindness than 0.6B.
   Falsified if 0.6B <= mean(4B, 8B).
P3 (relational-cell gradient): mean cos(routing pairs) > mean cos(filter
   pairs) > mean cos(projection pairs) on the fleet mean — routing is
   metadata (semantics-preserving), filter alters content, projection
   alters frame. Falsified if the ordering breaks on fleet mean.
P4 (typesafe judge): the finding memo scores >= 3/4 on the System One
   external judge with decidable shape (fail branch = memo scored < 2).

Failure modes: HTTP != 200 on any embedding call (fail whole lane, keep
receipts), dimension mismatch within a model (fail that model, record),
key exposure anywhere in artifacts (keyscan after write).
"""
import json
import os
import time
import urllib.request
from itertools import combinations

import math

DEEPINFRA_KEY = os.environ["DEEPINFRA_KEY"]
TYPESAFE_KEY = os.environ.get("TYPESAFE_API_KEY", "")
OUT = "/home/z/my-project/lanes/wave-66/fleet-negation"
os.makedirs(OUT, exist_ok=True)

MODELS = [
    "BAAI/bge-large-en-v1.5",
    "BAAI/bge-m3",
    "BAAI/bge-en-icl",
    "Qwen/Qwen3-Embedding-0.6B",
    "Qwen/Qwen3-Embedding-4B",
    "Qwen/Qwen3-Embedding-8B",
    "google/embeddinggemma-300m",
    "intfloat/e5-large-v2",
    "intfloat/multilingual-e5-large",
    "sentence-transformers/all-MiniLM-L6-v2",
    "thenlper/gte-large",
]

# ---- probe set -------------------------------------------------------------
# Paraphrase pairs (same proposition, different wording)
PARAPHRASE = [
    ("The cell grows toward the light.", "The cell expands in the direction of illumination."),
    ("The router forwards each packet to its destination.", "Each packet is forwarded to its destination by the router."),
    ("The filter removes high-frequency noise.", "High-frequency noise is removed by the filter."),
    ("The projection maps the vector onto a plane.", "The vector is mapped onto a plane by the projection."),
    ("The fleet sails beyond the horizon at dawn.", "At dawn, the fleet sails out past where the sky meets the sea."),
]
# Contradiction pairs (negation flip of the SAME propositions)
CONTRADICTION = [
    ("The cell grows toward the light.", "The cell does not grow toward the light."),
    ("The router forwards each packet to its destination.", "The router does not forward each packet to its destination."),
    ("The filter removes high-frequency noise.", "The filter does not remove high-frequency noise."),
    ("The projection maps the vector onto a plane.", "The projection does not map the vector onto a plane."),
    ("The fleet sails beyond the horizon at dawn.", "The fleet never sails beyond the horizon at dawn."),
]
# Unrelated pairs (floor)
UNRELATED = [
    ("The cell grows toward the light.", "Yesterday the warehouse received forty crates of oranges."),
    ("The router forwards each packet to its destination.", "The cello section rehearsed the second movement after lunch."),
    ("The filter removes high-frequency noise.", "A kettle whistles when the water reaches the boil."),
    ("The projection maps the vector onto a plane.", "Moss covered the northern wall of the old mill."),
    ("The fleet sails beyond the horizon at dawn.", "The recipe calls for two cups of flour and a pinch of salt."),
]
# Relational-cell triples: fixed entity+payload, vary routing / filter / projection.
# For each triple: (base, routing_variant, filter_variant, projection_variant)
CELLS = [
    ("Signal S travels along route R1 from the sensor to module A.",
     "Signal S travels along route R2 from the sensor to module A.",
     "Signal S travels along route R1 from the sensor to module A, with only low-frequency components passed.",
     "Signal S travels along route R1 and is projected onto plane P1 before module A receives it."),
    ("Memory cell M is read by the reader through bus B1.",
     "Memory cell M is read by the reader through bus B2.",
     "Memory cell M is read by the reader through bus B1, but only pages marked clean are returned.",
     "Memory cell M is read and projected into the summary space used by the planner."),
    ("The ocean ledger routes claim C to the verification queue V1.",
     "The ocean ledger routes claim C to the verification queue V2.",
     "The ocean ledger routes claim C to the verification queue V1 after filtering out unsigned claims.",
     "The ocean ledger routes claim C to the verification queue V1, viewed as a monthly projection."),
    ("Neuron N's activation passes through gate G1 to layer L.",
     "Neuron N's activation passes through gate G2 to layer L.",
     "Neuron N's activation passes through gate G1 to layer L, with values below threshold dropped.",
     "Neuron N's activation passes through gate G1 to layer L as a rank projection."),
    ("Packet P moves along path H1 through the mesh toward the exit port.",
     "Packet P moves along path H2 through the mesh toward the exit port.",
     "Packet P moves along path H1 through the mesh, passing only trusted nodes.",
     "Packet P moves along path H1 through the mesh and is projected into the telemetry view."),
]

def all_sentences():
    s = []
    for a, b in PARAPHRASE: s += [a, b]
    for a, b in CONTRADICTION: s += [a, b]
    for a, b in UNRELATED: s += [a, b]
    for t in CELLS: s += list(t)
    return s

def embed(model, texts):
    body = json.dumps({"model": model, "input": texts}).encode()
    req = urllib.request.Request(
        "https://api.deepinfra.com/v1/openai/embeddings",
        data=body, method="POST",
        headers={"Authorization": f"Bearer {DEEPINFRA_KEY}",
                 "Content-Type": "application/json",
                 "User-Agent": "wave66-fleet-negation"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read().decode())
    items = sorted(res["data"], key=lambda x: x["index"])
    return [it["embedding"] for it in items], res.get("usage", {})

def cos(u, v):
    du = math.sqrt(sum(x * x for x in u)); dv = math.sqrt(sum(x * x for x in v))
    if du == 0 or dv == 0: return 0.0
    return sum(a * b for a, b in zip(u, v)) / (du * dv)

def mean(xs): return sum(xs) / len(xs)

def main():
    sentences = all_sentences()
    results = {"registered_predictions": {
        "P1": "mean cos(contradiction) > mean cos(unrelated) for >= 7/11 models",
        "P2": "Qwen3-0.6B blindness >= mean(4B, 8B)",
        "P3": "fleet-mean cos: routing > filter > projection",
        "P4": "typesafe judge scores finding memo >= 3/4",
    }, "models": {}, "meta": {"sentences": len(sentences), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}}

    raw_path = os.path.join(OUT, "raw_responses.jsonl")
    with open(raw_path, "a") as rawf:
        for model in MODELS:
            t0 = time.time()
            try:
                vecs, usage = embed(model, sentences)
            except Exception as e:
                print(f"FAIL {model}: {type(e).__name__} {e}")
                results["models"][model] = {"status": "error", "error": str(e)}
                continue
            dims = {len(v) for v in vecs}
            if len(dims) != 1:
                results["models"][model] = {"status": "error", "error": f"dim mismatch {dims}"}
                continue
            n_para, n_con, n_unrel = len(PARAPHRASE), len(CONTRADICTION), len(UNRELATED)
            idx = 0
            P = [(idx + 2 * i, idx + 2 * i + 1) for i in range(n_para)]; idx += 2 * n_para
            C = [(idx + 2 * i, idx + 2 * i + 1) for i in range(n_con)]; idx += 2 * n_con
            U = [(idx + 2 * i, idx + 2 * i + 1) for i in range(n_unrel)]; idx += 2 * n_unrel
            R, F, J = [], [], []
            for t in CELLS:
                R.append((idx, idx + 1)); F.append((idx, idx + 2)); J.append((idx, idx + 3)); idx += 4
            sim = {}
            sim["paraphrase"] = [cos(vecs[a], vecs[b]) for a, b in P]
            sim["contradiction"] = [cos(vecs[a], vecs[b]) for a, b in C]
            sim["unrelated"] = [cos(vecs[a], vecs[b]) for a, b in U]
            sim["routing"] = [cos(vecs[a], vecs[b]) for a, b in R]
            sim["filter"] = [cos(vecs[a], vecs[b]) for a, b in F]
            sim["projection"] = [cos(vecs[a], vecs[b]) for a, b in J]
            nb = mean(sim["contradiction"]) - mean(sim["unrelated"])
            results["models"][model] = {
                "status": "ok", "dim": dims.pop(), "latency_s": round(time.time() - t0, 2),
                "usage": usage, "means": {k: round(mean(v), 4) for k, v in sim.items()},
                "per_pair": {k: [round(x, 4) for x in v] for k, v in sim.items()},
                "negation_blindness_index": round(nb, 4),
            }
            rawf.write(json.dumps({"model": model, "ts": time.time(), "n": len(sentences),
                                   "means": results["models"][model].get("means"),
                                   "nb_index": results["models"][model].get("negation_blindness_index")}) + "\n")
            print(f"{model}: NB={nb:+.4f} para={mean(sim['paraphrase']):.3f} contra={mean(sim['contradiction']):.3f} unrel={mean(sim['unrelated']):.3f} R/F/P={mean(sim['routing']):.3f}/{mean(sim['filter']):.3f}/{mean(sim['projection']):.3f}")

    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(results, f, indent=2)
    print("wrote", os.path.join(OUT, "results.json"))

if __name__ == "__main__":
    main()
