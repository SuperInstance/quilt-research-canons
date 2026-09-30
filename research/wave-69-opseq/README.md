# Wave-69 — Opcode-Sequence Layer: schedule variation + the contract-side probe

Lineage: wave-68 established (triple-replicated) that **embedding geometry is
relation-blind in contract-decomposed systems** — identity + vocabulary only,
never topology/dialect/order. Two probes were pre-registered for wave-69.
This lane executes both. The instrument is the engine itself; the encoding is
the addressing layer.

Instrument upgrade (P1 repair): `trace_gram2.c` — per-cell exercise harness
where the **schedule itself now varies** (4 classes: 0=original, 1=reverse
middle, 2=seeded Fisher-Yates, 3=alternating front/back; init always first,
free always last — reordering is UB-safe by construction). Wave-68's
`opsonly` degeneracy came from the fixed call skeleton; this removes the
degeneracy at the engine level, not by text shuffling.

Corpus: 7 cells x 10 seeds x 4 schedules = 280 traces, rendered as `full`
(op+call+args+state) and `opsonly` (op + cell) = 560 docs.

## Declared instrument structure (measured, not assumed)

Middle-phase counts (permutable phases per cell): route 2, crdt 2, time 3,
quf 3, world 3, proof 1, engine 6. Therefore:

- **proof is schedule-invariant BY INSTRUMENT** — a built-in noise-floor
  control: any schedule-class recovery on proof is pure noise measurement.
- route/crdt have only 2 distinct schedule orders (classes 0/2/3 collapse).
- engine has the deepest variation (4 distinct orders across the 4 classes).
- Step count and the opcode multiset (1-gram bag) are schedule-invariant BY
  CONSTRUCTION: only order-sensitive features (2+ grams, edit distance) can
  see the schedule. This is the structural negative control for the
  "embeddings are lexical bags" mechanism.

## Pre-registered claims (BEFORE any embedding call)

- **S1 (repair)**: ≥5/7 cells have ≥2 distinct opsonly sequences across
  schedules; ≥2 cells have ≥3. KILL: fewer, or no cell ≥3.
- **S1b (declared invariance)**: per (cell,seed), step counts identical
  across schedules; op 1-gram multisets identical across schedules.
  KILL: any violation (instrument bug, stop everything).
- **S2 (identity invariance)**: T1 = within-cell across-(seed,sched) mean cos
  minus between-cell mean cos on `full` > 0 for ≥4/5 embedders.
- **S3 (the law's sharp edge — schedule blindness)**: schedule-class
  recovery from `full` docs via 1-NN LOO on embeddings ≤ 0.40 (chance 0.25)
  for ≥4/5 embedders → CONFIRMS the law at engine-varying schedules.
  FALSIFIED if any embedder > 0.55 with label-shuffle p < 0.05 (then order
  leaks into embeddings and wave-68's law needs a scope amendment).
- **S4 (positive control by construction)**: op 2-gram TF-IDF schedule
  recovery ≥ 0.80. KILL: below 0.6 (instrument doesn't actually vary).
  op 1-gram TF is the structural control: predicted ≈ chance (0.25).
- **S5 (the P2 bar — dialect in sequence space)**: C1-seq (between-organ
  {route,quf,time} same-cell pair similarity minus in-cell {crdt,proof,world},
  averaged over same-cell (seed,sched) pairs) computed in 3 sequence spaces:
  op 2-gram TF-IDF cosine, op 3-gram TF-IDF cosine, normalized Levenshtein
  distance (as −d). PASS if ≥2/3 spaces give C1-seq > 0 with label-shuffle
  permutation p < 0.05 (1000 draws).
  - PASS ⇒ relational signal EXISTS at the opcode-sequence layer: wave-68's
    kill was a kill of TEXT embeddings, not of sequence encoding; unlock
    opcode-sequence drift linters (contract-side tooling).
  - FAIL ⇒ traces carry no relational structure under ANY encoding tried;
    relational tooling re-anchors fully on the runtime addressing layer.
- **Controls**: (a) label-shuffle permutation for every recovery/C1 claim;
  (b) batch-noise: 4 docs re-embedded 2x per model — self-cos must exceed
  the largest reported effect by ≥20x (wave-67 E5b rule); (c) proof
  noise-floor cell for S3/S4.

Panel: same 5 embedders as wave-68 R1/R3 (Qwen3-8B, Qwen3-0.6B, bge-m3,
e5-large-instruct, mpnet). Budget: one batched call chain per model.

## ADDENDUM — pre-registered AFTER first results, BEFORE disambiguation runs

First-pass results (p1p2_receipt.json): S2 PASS (T1 +0.09..+0.51, 5/5);
S3 SHOCK: schedule recovery from full docs 0.64-0.68 on 5/5 (bar was ≤0.40;
proof floor 0.20-0.23 as designed); op-1gram structural control EXACT
(chance 0.225 ≈ proof 0.23, C1 = +0.0000); S4 between bars (0.707-0.711:
directional, < 0.80 pass bar); C1-seq NEGATIVE and max-significant
(2-gram -0.142, 3-gram -0.194, p = 1.000).

Two questions must be settled before verdicts, registered here first:

- **A1 (S3 disambiguation)**: rerun schedule recovery on `opsonly` docs
  (op + cell only, no payloads). PREDICTION (lexical-mechanism refinement of
  the wave-68 law): opsonly recovery ≈ chance — the full-doc recovery rides
  on payload distribution shifts induced by the schedule (state values,
  error codes, phase-dependent telemetry), NOT on opcode order. If opsonly
  recovery > 0.55: the law dies outright (embeddings read opcode order).
  If ≈ chance: law SURVIVES in refined form — "embeddings recover schedules
  only through the payload distributions schedules induce; order itself
  remains invisible".
- **A2 (C1-seq decomposition)**: the raw negative C1-seq is confounded by
  instrument degeneracies in OPPOSITE directions (proof: INCELL, 1 distinct
  sequence -> mechanical within-cell sim ~1.0; route: BETWEEN, collapsed to
  2 orders -> inflated within-cell sim). Decompose: per-cell within-cell
  grammar self-similarity table + C1 variants (full groups / drop-proof /
  schedule-rich-only BETWEEN={time,quf} vs INCELL={world}). PREDICTION:
  open — if the negative sign survives rich-only decomposition, register the
  candidate law "bridge organs speak mutually-distant grammars; interior
  organs share one" (bridge-grammar specialization); if it flips, the
  negative was an instrument artifact and the proof-control did its job.

## RESULTS (2026-09-30, receipts: p1p2_receipt.json, disambiguation_receipt.json, fleet_round.json)

| claim | verdict | evidence |
|---|---|---|
| S1 repair | **PASS** | 6/7 cells ≥2 distinct op-sequences (time/quf/world 5, engine 13); proof = 1 exactly as the structural control demands |
| S1b invariance | **PASS** | 0 violations across 70 (cell,seed) groups |
| S2 identity | **PASS** | T1 full +0.09..+0.51, 5/5 embedders |
| S3 schedule-blind | **FALSIFIED → REFINED** | full 0.64–0.68, opsonly **0.69–0.71** (5/5) — embeddings DO read opcode order when it varies at engine level; op-1gram stays at chance (0.225 ≈ proof floor 0.23) |
| S4 order-visible (TF) | directional, **below bar** | 2-gram 0.707 / 3-gram 0.711 / edit 0.707 — above kill (0.60), below pass (0.80); TIES best embedder at zero cost |
| S5 dialect-in-sequences | **FAIL as pre-registered** | C1-seq 2-gram −0.142, 3-gram −0.194 (p=1.000) |
| A1 prediction | **DIED** (predicted ≈chance) | the law's "never ordering" clause is dead; embeddings ≈ opcode-bigram detectors |
| A2 artifact hypothesis | **CONFIRMED** | no-proof −0.024 → rich-only **+0.138** (2-gram), +0.128 (edit): the raw negative was proof-degeneracy; sign flips positive |

Batch-noise control: duplicate self-cos ≥ 0.9998 (5/5) vs effects ≤ 0.71.

### The wave-69 law amendment (replaces the wave-68 scope)

**Embedding geometry over engine traces recovers identity, vocabulary, AND
local opcode order (bigram grammar) whenever order genuinely varies at the
engine level. What it still cannot recover is dialect role / global
topology** (C1-seq ≈ 0 at best, never clusterable; R1's interface kill
stands). Wave-68's shuffle control could not see this because text-shuffling
a fixed trace preserves bigram structure — the repair instrument removed
that blindspot. Mechanism pinned by the n-gram ladder: 1-gram chance /
2-gram 0.707 / embeddings 0.69–0.71 — the neural panel behaves exactly like
a bigram detector, and histograms match it for free (budget rule replicated
a third time).

### Tooling unlocked

1. `trace_gram2.c` — schedule-varying exercise harness (init-fixed/free-last
   phase reordering; UB-safe; proof cell = built-in noise floor).
2. **Schedule-drift linter** — embed (or 2-gram TF) the op stream of a run,
   kNN against known schedule classes; recalibrate against the proof floor.
   Retroactively revives "trace-similarity as drift detector" for SCHEDULE
   drift (the wave-68 kill only ever covered dialect drift). Zero-model
   variant: op-2gram TF at 0.707.
3. Fleet adversarial round: 3/9 models independently converged on the
   **payload-swap ablation** (hold opcode sequence fixed, permute payloads /
   binding targets, measure what collapses to chance) — pre-registered as
   the wave-70 seed, together with: rich-only C1-seq confirmation round, and
   MiMo's linear-probe adjacency test (predict routing adjacency from
   2-gram features vs rewired-label null).

Fleet round leaderboard (typesafe-judged, novelty+soundness): Muse-Glimmer
2.8/3.54 promote 0.70 · Inkling 2.9/3.37 · MiMo 2.67/3.49 · DeepSeek-V4
2.3/3.41. Qwen3.8-Flash 429'd (9th model absent, receipted).
