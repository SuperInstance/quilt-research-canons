# Wave-66 lane A — fleet-wide negation blindness and the geometric reality of routings/filters/projections

Date: 2026-09-30. Lane: main agent (keeper). Extends wave-65 lane 65-A's novel finding to a systematic fleet study.
Artifacts: `results.json` (full per-pair cosines), `raw_responses.jsonl` (per-model call log), `judge_receipt.json` (System One verdict), `quilt-negation.html` (visual artifact), `scripts: scripts/wave66_fleet_negation.py`, `scripts/wave66_judge_memo.py`.

## Pre-registered predictions (written before any API call)

- **P1**: negation blindness (mean cos(contradiction) > mean cos(unrelated)) holds for ≥7/11 models.
- **P2**: Qwen3 blindness decreases with scale: NB(0.6B) ≥ mean(NB(4B), NB(8B)).
- **P3**: fleet-mean cos(routing pairs) > cos(filter pairs) > cos(projection pairs).
- **P4**: external System One judge scores the finding memo ≥3/4 novelty.

A prediction that cannot fail is not a prediction; P1/P2/P3 each had a stated falsifier and P4's fail branch was memo < 2.

## Probe set (35 sentences, one batch call per model)

- 5 paraphrase pairs (same proposition, reworded) — ceiling.
- 5 negation-flip contradiction pairs ("grows toward the light." vs "does not grow toward the light.") — the blindness probe.
- 5 unrelated pairs — floor.
- 5 relational-cell triples: fixed base sentence with (a) routing variant (same payload, different route), (b) filter variant (same route, different filter), (c) projection variant (same content, different projection/frame).

Models (live fleet, one per family + full Qwen3 ladder): bge-large-en-v1.5, bge-m3, bge-en-icl, Qwen3-Embedding-0.6B/4B/8B, embeddinggemma-300m, e5-large-v2, multilingual-e5-large, all-MiniLM-L6-v2, gte-large.

## Results

### P1 — CONFIRMED 11/11 (predicted ≥7/11). Negation blindness is universal.

| model | NB index = cos(contra) − cos(unrelated) | paraphrase | contradiction | unrelated |
|---|---|---|---|---|
| all-MiniLM-L6-v2 | **+0.735** | 0.899 | 0.808 | 0.073 |
| embeddinggemma-300m | +0.646 | 0.908 | 0.857 | 0.211 |
| Qwen3-Embedding-0.6B | +0.559 | 0.917 | 0.852 | 0.293 |
| Qwen3-Embedding-4B | +0.516 | 0.935 | 0.849 | 0.334 |
| Qwen3-Embedding-8B | +0.463 | 0.935 | 0.806 | 0.343 |
| bge-m3 | +0.378 | 0.956 | 0.834 | 0.456 |
| bge-large-en-v1.5 | +0.377 | 0.963 | 0.802 | 0.425 |
| bge-en-icl | +0.296 | 0.935 | 0.772 | 0.476 |
| gte-large | +0.178 | 0.979 | 0.925 | 0.747 |
| e5-large-v2 | +0.177 | 0.966 | 0.900 | 0.723 |
| multilingual-e5-large | +0.173 | 0.978 | 0.914 | 0.741 |

Even the least blind models put contradictions 0.15–0.18 above the unrelated floor. Caveat: e5/gte compress the whole similarity range upward (anisotropic floor), so their NB is smaller partly by dynamic range, not necessarily better truth-tracking. Within-family comparisons are safe; cross-family raw cosines are not.

### P2 — CONFIRMED. Scaling shrinks blindness; it does not remove it.

Qwen3 ladder: 0.6B +0.559 → 4B +0.516 → 8B +0.463. Monotone decrease, 16% relative from 0.6B to 8B. Extrapolation is not proof, but the trend is consistent with blindness being a structural property of contrastively-trained embedding spaces, fading slowly with capacity.

### P3 — CONFIRMED 11/11 with strict ordering on every model.

Fleet mean (and per-model, no exceptions): cos(routing) > cos(filter) > cos(projection).

| model | routing | filter | projection |
|---|---|---|---|
| gte-large | 0.993 | 0.966 | 0.944 |
| Qwen3-0.6B | 0.985 | 0.898 | 0.850 |
| e5-large-v2 | 0.982 | 0.942 | 0.941 |
| all-MiniLM-L6-v2 | 0.971 | 0.885 | 0.829 |
| bge-en-icl | 0.968 | 0.904 | 0.893 |
| … (full table in results.json) | | | |

**This is the round's headline.** The fleet agrees, model family by model family, on the *relative semantic weight* of our three relational-cell axes: changing which route carries a payload is nearly meaning-preserving; changing what the filter lets through alters content more; changing the projection changes the frame most. The relational-cell vocabulary is not just a convenient taxonomy — it has a measurable, cross-family geometric basis in embedding space.

### P4 — CONFIRMED. System One judge: novelty 3.73/4 (P(4)=0.81), promote noul 0.64, stranger-verifiable noul 0.53.

request_id `req_01a0ef9c6cb17d2296c7731e9a299708` banked in judge_receipt.json. The 0.53 stranger-verifiability is honest and instructive: the judge could not *see* the receipts from inside the memo; the receipts now ship with this report in the same directory, which is exactly the point — stranger-verifiability is a property of where artifacts live, not of how the memo is phrased.

## Implications for quilts and the ocean memory

1. **Embeddings for recall, receipts for truth** — now a measured fleet law, not a one-model anecdote. Any vector-only memory in the fleet will rank refuted claims above unrelated noise.
2. **Construction rule for relational cells**: decompose along the axis where fleet geometry says meaning actually changes — routes are cheap to swap (near-free in similarity), filters are content decisions, projections are frame decisions. Cell identity should live at the projection level; routing should be an address, not a property.
3. **Model selection heuristic**: high-NB models are fine for recall engines but need symbolic guards; low-NB models (e5/gte family) trade blindness for range compression — similarity thresholds must be re-calibrated per family.

## Failure modes / honesty

- 5 probes per category: small n; effects are large and uniform (11/11), but per-model ranks should be treated as provisional until the probe set widens.
- English-only, synthetic short sentences, one seed. The 65-A negation finding used natural fleet vocabulary; this round's probes are stylized variants of the same axes.
- Costs: 11 embedding batch calls + 1 System One call. Embeddings ≈ $0.00–0.01 total; judge ~1.2k input tokens (output free).
- No keys in any artifact (keyscan clean at close).
