# Wave-68 — Contract-Blindness: the relation is not in the vectors

Program: the operator's standing mandate — "discovering novel properties in the
decomposing into relational-cells in routings and filters and projections
between one another", probed with deepinfra embedding panels, a 9-model fleet
round-robin, and typesafe.ai judging, in quilts cadence.

## Design discipline

Every claim below was pre-registered in the experiment script's module
docstring **before** the first embedding call, with panel bars and controls
named. Two claims died; both deaths are receipts, not footnotes.

## Corpus (quilt-c @ pypi-oidc-publish, 6c616c5)

Seven kernel cells + one shared contract. The compile-level fact that frames
everything: **the kernels never call each other.** Zero cross-cell call edges
(measured). They meet only in `include/quilt/cell.h` — the 5+1 opcode
contract (BIND/LINK/EFFECT/VIEW/TICK/FORGET). `route` (routing), `quf`
(filter), `time`/`world` (projection), `crdt` (replicated state), `proof`
(verification), `engine` (the journal iterator). The operator's phrase
"routings, filters, projections between one another" is literally the file
layout: the between-organs are `route`, `quf`, `time`.

## R1 — interface embeddings (5 embedders, 3 families, 19 docs)

- **C2 contract gravity** (every kernel nearer the contract than to other
  kernels): PASS 5/5 — but the sentence-shuffle control also passes it.
  Mechanism: shared vocabulary. The opcodes ARE the shared protocol; gravity
  is lexical.
- **C1 dialect recovery** (between-organs {route,quf,time} cluster tighter
  than in-cell {crdt,proof,world}): **KILLED**. 3/5 embedders (bar 4/5);
  mpnet's shuffle control (+0.117) exceeds its real signal (+0.106).
- Foreign-domain control: PASS 5/5 (trivial, reported for completeness).

## R2 — fleet round-robin (9 named models, certified order, typesafe-judged)

Each model saw the R1 receipt and proposed one next probe; cross-critique
pass; blind typesafe System One judging (novelty/promote noul).

- Judge calibration datum: EMPTY proposals score 0.42-0.53 — the noul floor
  is ~0.45, so top scores are genuinely above-floor.
- Reasoning models (granite, DeepSeek, MiMo) returned empty content at
  max_tokens=500 and were rescued at 3000-8000 (receipts label the rescue;
  re-judged post-rescue).
- Leaderboard (novelty+promote): Qwen3.8-Flash 1.53, DeepSeek-V4 1.49,
  Muse-Glimmer 1.51, MiMo 1.47, granite 1.46, Inkling 1.45, Seed 1.42,
  Nemotron 1.22, Ling 0.75.
- **Convergence: 4/9 models independently proposed the same next probe** —
  move from static interface text to runtime journal/trace embeddings
  (TraceGram / JSDE / PatchStream Corpus v1, near-identical instruments).
  Fleet convergence 3x in wave-67 was on dissent tooling; this is the first
  4-way convergence, on the trace layer.

## R3 — trace-gram v0 (the fleet's convergent instrument, built)

`trace_gram.c` drives each kernel through seeded exercise schedules (the
payloads are honest telemetry: state values, error codes, counts). 7 cells x
10 seeds, rendered as 4 text variants: full / opsonly / statesonly / shuffled.
Same 5-embedder panel.

- **T1 cell identity**: PASS 5/5 (+0.09..+0.52) — **but the shuffle control
  matches it** (within ±0.006). Trace identity is bag-of-payloads; step
  order carries nothing.
- **C1-trace**: ~zero on 5/5. Dialect separation is absent at trace level.
- Declared flaw: opsonly was degenerate (deterministic schedules produce
  identical docs; C1-opsonly = 0.0000 exactly, all panels). A
  schedule-varying rerun is pre-registered for wave-69 — deliberately NOT
  silently patched here.

## R3b — the histogram instrument (H1/H2)

If identity is bag-of-payloads, a TF-IDF histogram with no model calls
should match the neural panel.

- **H1 rejected in the interesting direction**: TF-T1 = **+0.8797** vs the
  neural panel's best +0.5216. The histogram does not merely match — it
  dominates. Neural embeddings add noise to a purely lexical signal.
- **H2 confirmed**: TF-C1 = +0.0125 ≈ 0. No dialect split in pure lexical
  space either.

## The wave-68 law (triple-replicated)

**Embedding geometry is relation-blind in contract-decomposed systems: it
recovers identity (which cell) and vocabulary (what vocabulary the cell
speaks), never topology, dialect role, or ordering (how cells relate).**

Evidence: 5 embedders x 3 artifact types (interfaces, full traces, lexical
traces) x 3 controls (shuffle, foreign, degenerate-opsonly). Kills:

- any "embed-and-wire" tool family (interface similarity as a wiring
  suggestion basis) — dead on arrival;
- any "trace-similarity as dialect drift detector" — dead;
- re-anchors relational tooling on the ONLY carriers left standing: the
  contract (opcode semantics) and the runtime addressing/journal.

This is the fourth independent convergence on "the contract is the relation"
after wave-67's route non-locality at the addressing layer, states-not-events,
and the two-heads-drift contract evidence.

## Tooling unlocked this wave

1. **trace_gram.c** — reusable per-cell exercise harness (seeded, JSONL
   telemetry, fail-records-errors). Zero-model cell-identity and drift
   linters can build on it (TF instrument included in receipts).
2. **The noul floor datum** (~0.45 on empty input) — judge calibration is
   now measurable per-wave; blind-judging must include an empty-input probe.
3. **Budget rule of thumb, empirically priced**: at artifact granularity
   where a shuffle control explains the signal, use histograms and save the
   neural budget for semantics histograms cannot see.

## Pre-registered for wave-69

- Schedule-varying trace-gram rerun (repairs the opsonly degeneracy).
- Contract-side probe (the surviving hypothesis): does opcode-SEQUENCE
  structure under the engine's journal — not text at all — recover the
  between/in-cell split? The instrument is the engine itself, the encoding
  is the addressing layer.
