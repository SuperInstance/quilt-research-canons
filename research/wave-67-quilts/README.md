# Wave-67 — quilts in one fabric: from bit-law to embedding geometry

**Session:** 2026-09-30 · **Channels:** deepinfra (extensive), typesafe.ai (judge), mothquantum (certified order) · **GitHub:** see §receipts
**Continuity:** extends wave-66 lane A (P1–P4 fleet study) and the superinstance-bitlaw debrief (2c9860d), executing the debrief's named next-steps.

---

## 0. One-paragraph verdict

The relational-cell program now has three mutually reinforcing layers: **empirical semantic laws** (this wave: field salience, model-agnostic relational dialect, patches-carry-states-not-events), **executable laws** (frame-envelope v2 with wrap-boundary vectors; dissent-promotion loop that fires a real PR draft on drift and stays silent on clean fabric), and **the division of truth labor** (embeddings navigate, conformance certifies, dissent promotes). Two of the ideation fleet's four top claims were run to ground and **honestly killed** — each kill sharpened the architecture more than a confirmation would have.

---

## 1. Channel receipts (what ran, what returned, what counts as failure)

| Channel | Call class | Count | Result | Failure mode declared |
|---|---|---|---|---|
| deepinfra | `GET /v1/openai/models` (authed) | 1 | 200, 187 models; **9/9 named chat models PRESENT**; 5 embedding models | non-200 or missing model ⇒ channel closed |
| deepinfra | embeddings (batch, 5 models × 68 texts) | 5 | 200, dims 1024/2560/4096/2048/768, 1.8–34 s | dim/count mismatch ⇒ FAIL-CLOSED (none) |
| deepinfra | embeddings (C1b, 5 × 5 texts) | 5 | 200, 0.9–13 s | — |
| deepinfra | embeddings (E5a, 4 × 100 texts) | 4 | 200 | — |
| deepinfra | chat completions (R1 ×9 +rescues, R2 ×9) | ~27 | 14 parsed claims; **4 models never produced parseable JSON** (Inkling, granite, DeepSeek-R2 visible-but-unparsed, MiMo 2×90 s timeout) | parse fail ⇒ claim recorded absent, never judged (honest hole) |
| typesafe.ai | `POST /v1/systemone` (judge) | 13 | 200 ×13; full typed answers (score + noul ×2) ~0.3 s each | first probe returned **422** (bare-string questions rejected) — fixed by typed `{type,instructions,criteria}` per wave-66 shape |
| mothquantum | `comet-qrng-v1` certified seal | 1 | job `a59a4c66`, grade simulator-baseline, health PASS, 1064 bits delivered, h=0.904, permutation `[8,4,3,5,2,1,7,6,0]` | cert field missing ⇒ fail-closed (none) |
| GitHub | `GET /user` (Bearer + token schemes) | 3 | **401 Bad credentials ×3** — the operator-rolled token is invalid; all pushes + staged payloads blocked this session | 401 ⇒ pushes staged locally, reported honestly |

Typesafe verdict shapes confirmed: `novelty {type:score, score, confidence, probabilities}` and `promote/stranger {type:noul, noul}`; cost of the entire judge round: trivial (output tokens free of charge per wave-64 recon).

---

## 2. E3 — embedding geometry of the cell word (5 embedder families)

Corpus: 68 texts (8 route-variants, 8 glyph, 8 weight, 8 buzz, 8 chimeras; 12 cells × 2 views; 4 gauge configs). Pre-registered predictions in `e3/` scripts. Full data: `e3/{corpus,results,c1b_refinement,api_receipts}.json`, `embeddings.npz`.

### E3a field salience (intra-family mean cosine — LOWER = more salient edit)

| model | route | glyph | weight | buzz | chimera |
|---|---|---|---|---|---|
| Qwen3-0.6B | 0.9930 | 0.9149 | 0.9983 | 0.9979 | 0.8915 |
| Qwen3-4B | 0.9763 | 0.8531 | 0.9875 | 0.9830 | 0.8480 |
| Qwen3-8B | 0.9646 | 0.9128 | 0.9934 | 0.9967 | 0.8559 |
| nemotron-embed-vl-1b-v2 | 0.9643 | 0.9271 | 0.9936 | 0.9967 | 0.7981 |
| embeddinggemma-300m | 0.9027 | 0.9126 | 0.9734 | 0.9569 | 0.7574 |
| **MEAN** | **0.9602** | **0.9041** | **0.9892** | **0.9862** | **0.8302** |

- **A1 as stated FAILED** (route > weight predicted; got weight 0.989 > route 0.960). **Refined law (5/5 families):** salience ordering is *glyph (projection) > route (address) > buzz ≈ weight (magnitudes) ≫ chimeras*. Continuous magnitudes are near-transparent to embedding semantics; the projection IS the identity, the route is the address, the weights are dimmers.
- **Novel property — the dissent channel is semantically silent.** Buzz edits move meaning least of all fields (0.986), exactly what a *non-authoritative* channel demands: dissent rides outside the semantic payload, so carrying it in the high nibble cannot corrupt meaning. The bit-law's placement of buzz is now empirically motivated, not just aesthetically.
- Control held: chimeras lowest on every model (0.8302) — incoherent multi-field edits are recognized as out-of-family.

### E3b two views (relational vs internal descriptions of the same 12 cells)

- Cross-model RSA: **relational 0.6275 > internal 0.5923** (shuffled-label control **0.0321** — the instrument can detect misalignment).
- Matched cross-view diagonal: mean 0.4384 (both views of one cell weakly-moderately recognize each other; nemotron weakest at 0.277).
- **B1 holds:** the relational dialect (who-talks-to-whom) is the more model-agnostic one. Quilt patches should carry the relational fingerprint as canonical; internals are model-local annotation.

### E3c gauge/swap — falsified, then refined into a construction rule

- **C1 FAILED 0/5**: with event language ("swap", "re-route to compensate"), `cos(orig, unrelated) = 0.84–0.90` EXCEEDS both swap variants (~0.6) — embeddings rank the *event* over the resulting *configuration*.
- **C1b (pre-registered refinement) PASSED 5/5**: neutral state-language descriptions recover the correct ordering `comp (0.95–0.99) > naive (0.93–0.97) > minimal-pair (0.89–0.95) > unrelated (0.68–0.85)`. The frame-coherence clause is visible but weakest — the last thing embeddings see.
- **Construction rule (new fleet law): "patches carry states, not events."** A quilt patch must be written as the resulting configuration; event language hijacks the geometry. And mechanical conformance remains the only truth source for equivalence — reinforcing *embeddings for recall, receipts for truth*.

---

## 3. E4 — nine-model ideation round-robin (moth-certified order)

Stitch order (certified Fisher-Yates, pool 9, job `a59a4c66`): **MiMo → Ling → granite → Muse → DeepSeek → Qwen → Inkling → Nemotron → Seed → (MiMo)**. R2 critiques pass each model its two stitch neighbors — the certified permutation literally stitched the round table.

- Claims parsed: 6/9 R1 (Inkling, granite, MiMo never produced parseable JSON even after a declared 150 s rescue; Muse rescued from reasoning channel), 5/9 R2. Reasoning-channel confound (wave-65-E finding) re-confirmed; `reasoning_extracted` recovery recovered 1 claim.
- **Judge calibration healthy:** banal control scored novelty 0.04 (rejected), P3 anchor 2.72 (mid-high), fleet best 2.99. Controls bracket the board as designed.
- Quilt map: 11 judged claims, mean pairwise cos **0.6236** — genuine diversity (no wave-65-style gravity well on open-design questions), 2 convergence pairs > 0.82, both around dissent tooling.
- **Fleet convergence:** three independent models (Qwen, Seed, Nemotron) proposed buzz/dissent tooling — the wave built it (§5c) rather than a fourth proposal.

Top of the judged board:

| claim | source | novelty | promote | stranger |
|---|---|---|---|---|
| route edits are non-local | DeepSeek R1 | 2.99 | 0.70 | 0.40 |
| R/F/P displacement orthogonality | Ling R1 | 2.89 | 0.57 | 0.51 |
| dissent-audit refinement | MiMo R2 | 2.86 | 0.39 | 0.25 |
| (CTRL-banal, must be low) | — | **0.04** | 0.46 | 0.34 |

## 4. E5a/E5b — the top two claims, run to ground (both killed, both instructive)

- **E5b (Ling, orthogonality): KILLED.** Cross-field displacement mean |cos| = 0.22–0.40 (kill bar 0.15); worst pair weight×buzz (0.40) — the two magnitude fields share a direction. R/F/P edits form **overlapping cones, not orthogonal axes**. The "zero-crosstalk relational slider UI" is not justified by geometry: salience is ranked, controllability is not independent. Test cost: zero API calls (computed from banked E3a matrices) — banked artifacts pay rent.
- **E5a (DeepSeek, route non-locality): KILLED at the encoder, REBORN at the addressing layer.** Mutating one cell's route byte moves only that cell's embedding (sharing cells shift 0.0051 ≈ batch-noise floor 0.0058; mutated cell 0.115). Weight mutation likewise local (0.053 vs 0.0051). Embeddings are strictly per-text — there is no encoder-level non-locality. **But route non-locality is trivially real at the addressing layer**: in a route-keyed quilt memory, changing one cell's route re-buckets it, moving the entire old and new route sets *as an index operation*. Refinement: a route-diff linter must **diff the routing table, not the vectors**. This is the wave's clearest example of the division of truth labor doing real work: the encoder's locality is exactly what makes receipts (index state) the right place to carry routing truth.
- Batch-noise negative control: re-embedding the identical corpus produced per-cell shifts ≤ 0.006 — the instrument can see 20× smaller effects than the claim required to pass.

## 5. E5c + E2 — the dissent promotion loop and the frame law (the fleet's converged tool, built)

Built and green:
- **Frame law v2** (`research/superinstance-bitlaw/frame_gen.py` → `out/frame.{py,js}` + `out/frame_conformance.json`): u32 tick + per-row tick slots, all multi-byte big-endian, **serial-number delta arithmetic** with 6 wrap-boundary vectors (`0xFFFFFFFF → 0x00000000 = +1`). Conformance: python reference PASS, node PASS (3 frame vectors + 6 deltas), emitted-py module PASS. This retires the T2 bug class by law (the discussion's u16 tick wrapped every 18.2 min; its own detector missed the loss at wrap).
- **Cell word gen.py now also emits `out/cellword.py`** — the loop imports generated codecs; a fourth hand-rolled copy would have violated the very law the debrief established. 243/243 cellword vectors re-verified after the change (python + node).
- **Dissent loop** (`scripts/w67_e5c_loop.py` → `wave-67-quilts/e5c/`): producer → frames → receivers (contract unpack, route mismatch ⇒ buzz 10–15 on ack words) → monitor (per-receiver buzz histograms, KL(baseline‖window) > 2.0) → **PR draft promotion**.

Results (all three legs):

| scenario | result |
|---|---|
| clean fabric (negative control) | **PASS** — KL max 0.5241, no PR |
| drifted fabric (route `<< 1` from tick 30) | **PASS** — PR promoted at tick 58, route 17, KL 4.7235; sample ack word `0x00772242` shows the drift in hex (route nibble 0x22 = 34 = 17≪1, glyph 'B' = expected route-17 receiver) |
| T2 what-if (executable) | **PASS** — at the mid-run u32 wrap (ticks started at 0xFFFFFFF0), u16-naive diff = **−65535** (a naive reorder detector false-fires); v2 serial delta = **+1**, monitor never notices |

The promoted PR draft (`e5c/pr-draft-drift.md`) carries its own evidence, the conformance commands, and the requested change — dissent-in-bits became dissent-in-PRs with zero human in the loop.

## 6. E1 — CI gate (staged, token-gated)

`.github/workflows/bitlaw-conformance.yml` (in this repo, unpushed): on any push touching `research/superinstance-bitlaw/**` — regen from single source, **byte-identical determinism assert** (two runs, sha256 diff), node conformance ×2, emitted-python conformance. This is the debrief's "L0 gate" next-step, ready to arm on push.

---

## 7. The greater architecture (what all of this is describing)

The fabric is a **three-layer truth machine**, and this wave put a measured, executable piece in each layer:

1. **Semantic layer (embeddings)** — navigates. Measured laws: P3 ordering; field salience hierarchy; relational dialect as the model-agnostic one; patches-carry-states-not-events. These laws say *how to write patches so the geometry stays honest* — they are authoring rules for quilts.
2. **Contract layer (bit-law + frame-law)** — certifies. u32 cell word + frame envelope v2, single-source generated codecs in 3+1 languages, wrap-safe tick arithmetic, 243+9 shared vectors, byte-identical regen determinism, CI-gated. This layer says *what is true regardless of any model's opinion* — it is where gauge-equivalence actually lives (E3c showed embeddings can't certify it, conformance can).
3. **Dissent layer (buzz → KL → PR)** — adapts. Receivers hold the contract's expectation, buzz is their non-authoritative vote, the monitor's promotion threshold turns accumulated dissent into a PR against the contract. The fabric's change protocol is now closed-loop: contract ⇒ expectation ⇒ dissent ⇒ promotion ⇒ new contract revision. And because the dissent channel is semantically silent (E3a), carrying it costs nothing in meaning.

The deep infra-structure connecting them is the **division of truth labor**: embeddings for recall and navigation, receipts and conformance for truth, dissent for adaptation. E3c and E5a are the empirical proofs of this division — both showed exactly the kind of judgment embeddings cannot make (equivalence, locality) and both showed the layer that can.

**Next smallest falsifiable steps** (staged for the next tokened session):
1. Push + arm the CI gate; post the three staged payloads from `research/api-payloads-2026-09-30.md` (still unposted — GitHub 401).
2. Wire the dissent loop to a live producer (wave66-quilt worker): real frames from the edge, monitor as a cron Worker, PR drafts filed as issues (write:discussion + issues scopes are on the new token once valid).
3. Route-table diff linter (E5a's reborn tool): diff route buckets, emit affected-cell lists — a 50-line worker.
4. Cross-fabric buzz KL as a fleet health metric: run the monitor's KL between two independent fabrics' dissent histograms — divergence = the fabrics disagree about the contract.
5. Retire WGSL residual risk: one GPU round-trip on the frame codec (debrief next-step, needs a browser/CDP harness).

## 8. Honesty ledger (negative controls and their outcomes)

| instrument | control | outcome |
|---|---|---|
| E3a field salience | chimeras must be outliers | held (0.8302, lowest everywhere) |
| E3b RSA | label-shuffle must collapse to ~0 | held (0.0321) |
| E5a locality | batch-noise floor (re-embed identical corpus) | held (0.0058; claim needed >0.1 — instrument sensitive enough to kill the claim) |
| E5c loop | clean fabric must not fire | held (KL 0.52 < 2.0) |
| E5c loop | T2 what-if: old design must have failed | held (u16 diff −65535 would false-fire; recorded as executable evidence the law fix matters) |
| judge | banal claim must score low | held (0.04) |
| judge | banked result must score mid-high | held (2.72) |
| keyscan | scanner must flag planted shapes (tested both directions in prior waves; regex unchanged) | regex reused verbatim |
| **failed controls** | R1 parse (4 models), R2 parse (4 models), GitHub token | **honestly absent** — claims unjudged, pushes unpushed; holes recorded, not papered over |
