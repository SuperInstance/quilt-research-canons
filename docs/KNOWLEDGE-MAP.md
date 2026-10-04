# quilt-research-canons — Knowledge Map
> The index of indexes. Everything below was verified against the working tree during
> wave-69 (task 69-doc-f). Staleness is dated, not hidden.

## In this repo

### Top level
- `README.md` — discoverability layer; founding snapshot (2026-09-24) + doctrine
  ("the roadmap is in the directory, not in memory") + what the repo does NOT do.
- `.github/workflows/bitlaw-conformance.yml` — CI L0 gate: regenerates bitlaw codecs
  on push, asserts two runs produce identical bytes (Python 3.12 + Node 22).
- `docs/REFERRAL-fleet-triage-resolver.md` — pre-existing wave doc: the fleet-triage
  resolver scoped run over 244 repos, 192 RESOLVES landing on this repo (0.0% FP on
  audited hard outcomes).
- `quilt-research-canons/research/` — nested duplicate directory (lineage noise);
  contains one stray essay, `contribution-thesis-week-of-2026-09-29.md`.

### `research/` — one receipt per lane (~60 artifact directories)
**Orientation and protocol**
- `HANDOFF.md` — the living handoff: position paragraph, merged/live table, open items,
  measured facts (§4), discipline (§5), open queue (§6), what NOT to do (§7), where
  things go (§8), corrections (§9). The single highest-value file for a newcomer.
- `SPRINT-LINEAGE.md` — the sprint contract (7 header sections, NEXT-SPRINT SPEC,
  trailer line, no sub-agents) and the active-lineage table.
- `2026-09-24-novel-problems-report.md` — founding experiments: H1 (Fork)
  FALSIFIED+REFINED, H2 (Reveal) CONFIRMED at 85%, H3 (Chorale) CONFIRMED.
- `jev-velocity.json` / `moth-fidelity-matrix.{json,md}` — founding sprint outputs
  (5q×20 trials, most stable at trial 1; QSM best for continuous, QPAM all-rounder).
- `quantum-chaos-001.json` — QRNG-sealed quantum verdict artifact (bell_S recorded,
  grade: simulator-baseline).

**The pre-registered loop and its outward turns**
- `loop/` — `loop.py` (pre-register → run → debrief harness), `loop_state.json`
  (all 11 rounds), `round1.py`–`round11.py` (re-runnable experiments), `INDEX.md`
  (scorecard: 35 predictions / 24 confirmed / 11 refuted + the operating rule).
- `scout-theirs/` — the same discipline pointed outward at keeper/Claude work:
  `round1.py`, `round2.py`, `loop2.py`, `loop2_state.json`.
- `scout-the-other-agents.md` — the scout-theirs receipt: 9 predictions, 6 confirmed,
  3 refuted; corrected the attribution census (≥3 distinct credentials, 9 author names,
  85/110 commits unauthenticated AND 0 signed).
- `jevlab/` — `jev_gate.py` (the original known-answer test that found the score-type
  collapse) + `exp1`–`exp6` stability/ceiling/transition/method/payoff/order experiments.

**JEV gate instruments and findings**
- `jev-gate-experiments-2026-09-29.md` — the gate is a step, not a scale (+0.690 on the
  guarantee rung; later rungs inert ≤0.02).
- `jev-loop-six-rounds-2026-09-29.md`, `jev-loop-rounds-7-8-2026-09-29.md`,
  `jev-loop-rounds-9-11-2026-09-29.md` — the batching saga, round by round.
- `jev-velocity.json`, `jev-kat-result-2026-09-29.md` — velocity profile + KAT receipt.
- `jevlab/` (above) is the KAT's home.

**Audits (inward and outward)**
- `externalisability-audit-2026-09-29.md` — 10/10 sealed predictions, 0/10 externally
  decidable: "the fleet has falsifiers but not substance tests". Stale on purpose:
  HANDOFF §9 records it moving to 3/11.
- `attribution-audit-2026-09-29.md` — 791 commits, 0 signed; per-agent GitHub Apps is
  the fix.
- `claw-audit.md` (+ `claw-paths.json`) — the biggest repo in the fleet (7,445 files,
  402 MB), its README claims three mechanisms that are not in the repository.
- `census-4856-vs-1300.md` — the account-size census discrepancy.
- `active-repos-report.md`, `fleet-state-report-2026-09-28.md`,
  `fleet-motion-digest-2026-09-29.md` — fleet-state photography by date.

**Experiments and instruments-in-research**
- `fleet-negation-2026-09-30/` — the largest single receipt: `report.md`
  (fleet-wide negation blindness, 11/11 models, pre-registered P1–P4, judge 3.73/4),
  `results.json`, `raw_responses.jsonl`, `judge_receipt.json`, `quilt-negation.html`
  (visual), `deploy_wave66_quilt.py`.
- `active-ledger/` + `active-ledger.md` — the routing book as a tensor, filter as a
  cell; selftest 12/12 with four negative controls.
- `growing-pincher/` + `growing-pincher.md` — the pincher bypass ledger idea (open
  item §6.6 of HANDOFF).
- `route-diversity/route_diversity.py` — the (currently single) second-route experiment.
- `locality/` — `locality_spectrum.py` + `frontier_run.txt` receipt.
- `molt/` — soft shells: `molt.py`, `shells.py`, `self_test.py` (15/15 legs, negative
  controls included), `README.md` (the seven shells table with outgrows clauses).
- `moth/` — `moth_frame_test.py`, `frame_test.log`, `moth-qpixl-roundtrip.md`.
- `jevlab/` — see audits/JEV above.
- `sow/` — statement-of-work pattern: `sow.py`, `review.py`, `round.py`, `seeds.jsonl`,
  `self_test.py`.
- `two-views/` — `view.py`, `self_test.py`, `REVIEW.md`, `index.html`.
- `family/` — `family_expansion.py` + `family_run.txt`.
- `codec-gaps/` + `codec-gaps-vs-glyphcast.md` — codec comparison lane.
- `reef-spec/` — `reef.py` + `selftest_reef.py`.
- `qpixl-ascii/` — `qpixl_ascii.py`, `demo.py`, `self_test.py`, README.
- `atlas/` — `grounding_lint.py` + output + `process-atlas.md`.
- `synthesis/gate-taxonomy-2026-09-30.md` — gate taxonomy digest.
- `team/` — team-lane artifacts: exact-calibration, gpu-lab AUC verdict,
  lane-u-collision, witness-barcode.
- `anti-gan-route-diversity.md`, `pincher-round2-visions.md`,
  `pincher-super-site-round1.md`, `zai-far-future.md`, `greater-superinstance-2026-09-29.md`,
  `cy-quilt-mappings.md`, `tradeoff-paradigms.md`, `zeroshot-frontend-audit-2026-09-30.md`,
  `api-payloads-2026-09-30.md`, `pr-sweep-2026-09-29.md` (+ `-final`) — dated essays/
  reports, one receipt each.

**Wave integration receipts (2026-09-30 line)**
- `wave-63-handoff-integration-2026-09-30.md`, `wave-64-keyroll-integration-2026-09-30.md`,
  `wave-65-hot-lanes-integration-2026-09-30.md`, `wave-66-pr-sweep-integration-2026-09-30.md`.
- `wave-67-gift-audit/` — gift audit: `gift_lint.py`, `audit_results.json`,
  `crossruntime_driver.mjs`, frames.
- `wave-68-contract-blindness/` — `README.md` + r1 receipt, r2 critiques/judgements/
  proposals, r3 trace receipt.
- `wave-69-opseq/` — opseq lane: corpus, docs, disambiguation receipt, fleet round.

**Security / key discipline**
- `KEY-ROTATION-2026-10-04.md` — the rotation event receipt: which keys returned,
  which stayed burned, Cloudflare-only capacity period, Groq unblocked via a Worker
  relay. Names keys by service only; no values.

**Receipts of record (numbered)**
- `receipt-001-dependency-closed-artifact.md`, `receipt-002-externally-verifiable-release.md`,
  `receipt-003-pong49-resolution.md`, `receipt-004-a2a-cell-api.md`,
  `receipt-005-distribution.md` — see "Receipts of record" below.
- `superinstance-bitlaw/` — the bit-law/frame-law codec single source (CI-guarded).
- `subagent-harness/wave-64-api-harness-v1.md` — harness spec from the wave-64 lane.

### `projects/` — standalone instrument toolkits (each with its own receipt)
- `artifact-first/` — "reach for the artifact before you form the view". Two gates
  (grounding, consistency) + combined gate; `tests/test_gates.py` (16/16 fresh;
  stored `test_output.txt` says 17/17), `PROOF.md` (what the gates establish and
  refuse to), `CASEBOOK.md` (six real caught failures from one session), `METHOD.md`,
  `examples/tonight.jsonl`, package `artifact_first/`.
- `fleet-legend/` — "a repo's frontend is its first error message". Census of 100 repos
  (98% README, 68% runnable first command, 20% no description); L1–L5 obligations.
  `lint_legibility.py`, `verdicts.json` (per-repo verdicts: INVISIBLE /
  ENTERABLE-WEAK / ...), `GOOD.md`/`WEAK.md`/`BAD.md` legibility corpora, `ERRORS.md`
  (the L5 evidence), `fleet_legibility_report.md`, `success-without-evidence.md`,
  `legibility/`, `run_complete2.py`, `complete_run2.txt`, `completion_summary.json`.
- `gpu-lab/` — six experiments derived from real findings, all with honest CPU
  fallback (`exp1_aperture_gpu.py`, `common.py`, `exp1_run.txt`); knowledge index on
  Cloudflare: `wrangler.toml` (KV binding, Vectorize deliberately NOT bound — code 1005)
  + `vectorize_worker.js` (KV + in-Worker cosine, `/health`, `/search`, `/gaps`) +
  `upload_index.py`.
- `instrument-registry/` — instruments count only after a known-answer case:
  `instruments.json`, `render.py`, `validate.py`, generated README.
- `jev-lite/` — 15-feature logistic regression on real oracle measurements:
  `collect.py`, `features.py`, `train.py` (stratified 25% holdout, seed 20260930,
  asserts held-out AUC ≥ 0.85; rewrites `weights.json`), `weights.json`, `corpus.json`,
  `index.html`. No README (the only projects/ entry without one).
- `process-signature/` — read repo shape → report process archetype:
  `process_signature.py`, `sweep.py`, `fleet_sweep.json`, `fleet_sweep_out.txt`.
- `the-wheel/` — spine/angles/gaps harness where the negative space is the work queue:
  `wheel.py`, `calibrate.py`, `calibration_out.txt`, `wheel_index_out.txt`,
  `control_agreeable.txt`, `out/`, and `FINDING.md` (the stopword bug: corpus-specific
  vocabulary filtered as generic).
- `chain-lint/` — "is the witness chain in the data, or only in the schema?":
  `chain_lint.py`. Motivated by 550 live cells with uniform zero `prev_hash`.
- `readme-verifier/` — verifies the claw README's three claimed mechanisms:
  `verify.py`, `census.py`, `FINDING-claw.md` (checked 2026-09-30, scope stated).
- `sunset-run/` — runs the sunset-ecosystem's OWN baton protocol against the session:
  `sunset_run.py`, `sunset_2026-09-29.json`.
- `toolchain-kar/` — live instrument characterisation; the 4/11 "lie of composition":
  IDENTITY vs SHAPE vs HEALTH failure classes; `probe.py`.
- `quilt-widening/` — self-decomposition loop graded on structure-vs-restatement:
  `widening.py`, `widening_trace.json`, `widening_run.txt`.
- `findings/` — cross-checks of external claims: `crdt-results-do-not-reproduce.md`
  (one headline is an identity; one number does not come back; 196-run package).

### `sprints/` — the lineage chain
- `sprint-jev-001.py` — JEV canon-promotion velocity; declares sprint-jev-002.
- `sprint-moth-001.py` — MOTH quantum-audio fidelity; declares sprint-moth-002.
- `sprint-zai-001.py` — 3-voice ZAI chord; declares sprint-zai-002.
- `sprint-deepinfra-001.py` — 6-model DeepInfra chord; declares sprint-deepinfra-002.
- `sprint-quantum-001.py` — quantum-chaos sprint (in tree; absent from README snapshot
  and SPRINT-LINEAGE tables — registry drift, receipted in the journal).

### `tools/` — the JEV instruments
- `jev_gate.py` — two-axis gate (mechanism + externality), two separate `noul` calls,
  min-aggregated; circularity pre-filter; stability receipt in header.
- `jev_batch.py` — safe batching via subject-naming prefix (round-11 mechanism);
  2.5x cheaper than one-per-call with the prefix in place.
- `jev_gate2.py` — one-call `choice` gate; promote iff P(both_axes) > P(neither) and
  P(both_axes) > threshold; avoids the broken `noul` path entirely.

## Pre-existing docs (before wave-69)
- `README.md` — discoverability layer + founding snapshot + doctrine + does-NOT-do list.
- `research/HANDOFF.md` — the rolling handoff (kept current by its lane).
- `research/SPRINT-LINEAGE.md` — the sprint contract.
- `research/loop/INDEX.md` — the loop scorecard and operating rule.
- `research/molt/README.md` — the soft-shell doctrine and seven-shell table.
- `research/2026-10-02-tripartite-canon/report.md` — the external-ideation digest
  (six movements, five open problems P1–P5, fleet synergy map, adoption relations).
- `docs/REFERRAL-fleet-triage-resolver.md` — the fleet-triage referral (PENDING,
  CANDIDATE per weight law).
- Per-project READMEs: `artifact-first`, `fleet-legend`, `gpu-lab`,
  `instrument-registry`, `process-signature`, `the-wheel`, `chain-lint`,
  `readme-verifier` (as FINDING), `toolchain-kar`, `quilt-widening`.
- Project-level proof docs: `artifact-first/PROOF.md`, `artifact-first/CASEBOOK.md`,
  `artifact-first/METHOD.md`, `the-wheel/FINDING.md`, `readme-verifier/FINDING-claw.md`,
  `fleet-legend/ERRORS.md`, `fleet-legend/success-without-evidence.md`,
  `fleet-legend/fleet_legibility_report.md`, `findings/crdt-results-do-not-reproduce.md`,
  `research/scout-the-other-agents.md`, `research/claw-audit.md`,
  `research/externalisability-audit-2026-09-29.md`,
  `research/active-ledger.md`, `research/growing-pincher.md`,
  `research/KEY-ROTATION-2026-10-04.md`, plus the dated reports listed above.
- `docs/` wave-69 additions (this package): ONBOARDING / USER-GUIDE /
  DEVELOPER-GUIDE / ENGINEERING-NOTES / CTO-BRIEF / KNOWLEDGE-MAP.

## In the fleet
- **SuperInstance/quilt** — upstream runtime (cells, pull-based reactive engine,
  `with(cells)` DSL, listeners). This repo's cellular vocabulary derives from it. Sibling.
- **SuperInstance/jev-quilt** — JEV canonical SDK; the `tools/` here are the
  experiment-generation precursors of that SDK. Used-by relationship (the SDK cites the
  loop findings).
- **SuperInstance/quilt-c** — the dependency-closed C99 artifact receipted in
  `receipt-001/002`; published to crates.io + npm per HANDOFF §2. Downstream of the
  receipts here.
- **SuperInstance/fleet-seeds** — hosts the lode ledger and the externalisability gate
  that this repo's audit criticized (0/10 → 3/11); mutual awareness. Sibling.
- **SuperInstance/quilt-gpu-lab** — the account-level GPU lab; `projects/gpu-lab` here
  is the local-variant sibling with the Cloudflare index worker.
- **SuperInstance/fleet-triage** — its resolver resolved 192 citation outcomes against
  this repo (see `docs/REFERRAL-fleet-triage-resolver.md`). Uses this repo.
- **SuperInstance/claw** — the audited outside-work repo (biggest in the account;
  README claims three mechanisms not present). Audited by `research/claw-audit.md` and
  `projects/readme-verifier/`.
- **SuperInstance/sunset-ecosystem** — third-party repo whose baton protocol
  `projects/sunset-run/` dog-foods. External, used-by.
- **SuperInstance/superinstance-lab** — the journal repo (`worklog.md`), the memory of
  record for lanes that touched this repo.
- Other cross-references from the README: `quilt-cell-harness`, `quilt-multi-oracle`,
  `quilt-brewer`, `quilt-bootstrap`, `quilt-fleet-snapshot`, `mavis-fleet`, `quilt-cli`.

## In the journal
Source: SuperInstance/superinstance-lab → `worklog.md` (grep `quilt-research-canons`).
Task IDs and lanes found touching this repo or its state:
- **Wave-64 sync receipt** (worklog line ~700): fresh clone of
  quilt-research-canons @ 3547d01; remote census 100 repos; compose-don't-clobber
  adopted.
- **Wave-64/65 line** (line ~846): "quilt-research-canons CI-green-but-vacuous +
  reseal-forgery #3" — the repo cited as evidence in the fleet BOARD finding
  (CI green ≠ substantive; receipts must bind to artifacts).
- **Organ-family decomposition lane** (line 1149, Task: "Decompose organ family
  (quilt-mcp-receipts, quilt-jev-toolkit, quilt-organ-workers,
  quilt-research-canons)…"): read README, SPRINT-LINEAGE.md, sprint-jev-001.py header,
  novel-problems report; smoke = offline conformance 5/5 sprint scripts, 3/3 JSONs
  parse, scripts NOT executed (no keys/network); negatives receipted: registry drift
  (sprint-quantum-001.py absent from README tree and SPRINT-LINEAGE tables) and the
  nested duplicate dir. Decomposition JSON written to the atlas.
- **Wave-69 census** (line ~1426): remote census — quilt-research-canons +245 behind
  local record at census time; others pushing.
- (Earlier formation of this repo happened inside the Mavis × Casey session line before
  these task IDs; the founding snapshot's own README is the primary record.)

## Receipts of record
The load-bearing artifacts a stranger should check first, and what each proves:
- `research/fleet-negation-2026-09-30/report.md` + `judge_receipt.json` +
  `raw_responses.jsonl` — 11/11 models measured negation-blind under pre-registered
  P1–P4; judge 3.73/4; raw responses committed.
- `research/loop/loop_state.json` + `INDEX.md` — 35 pre-registered predictions across
  11 rounds, 24 confirmed / 11 refuted, with debriefs; the basis of the JEV operating
  rule.
- `research/externalisability-audit-2026-09-29.md` — 30 verifier calls, unanimous:
  falsifiers exist, substance tests do not.
- `projects/artifact-first/test_output.txt` + `tests/test_gates.py` — the gates pass a
  grounded/clean case and fail unsourced/negative cases (stored 17/17; fresh 16/16 —
  discrepancy flagged in docs).
- `research/molt/self_test.py` output (15/15) — the shells' rewind/composition
  guarantees, including negative legs.
- `research/jev-velocity.json` — JEV canon-promotion velocity profile (founding run).
- `research/moth-fidelity-matrix.json` — MOTH scheme-per-signal verdicts (QSM best for
  continuous; QPAM all-rounder).
- `projects/fleet-legend/verdicts.json` + `complete_run2.txt` — the 100-repo legibility
  census with per-repo verdicts.
- `research/KEY-ROTATION-2026-10-04.md` — the key-rotation event: services returned vs
  still-burned, no key values.
- `receipt-001…005-*.md` — the numbered series: dependency-closed artifact,
  externally-verifiable release, pong49 resolution (Brier 0.0049–0.0225, closed false,
  n=1), A2A cell API, distribution.

## How to search further
```bash
# All loop evidence for the batching mechanism
grep -rn "subject" research/loop/ tools/jev_batch.py | head -30

# Every place a receipt was corrected rather than rewritten
grep -rn "correction\|corrected in place\|stale" research/HANDOFF.md README.md

# The legibility obligations and who fails them
grep -rln "L5" projects/fleet-legend/ && python3 -c "import json;[print(v['name'],v['v']) for v in json.load(open('projects/fleet-legend/verdicts.json'))]"

# Every env-var key NAME (never values) used by runnable scripts
grep -rn "os.environ" tools/ sprints/ projects/ | grep -v Binary

# Negative controls across the repo (the discipline made visible)
grep -rn "NEGATIVE:" projects/artifact-first/tests/test_gates.py research/molt/self_test.py

# Journal history for this repo (from a clone of superinstance-lab)
grep -n "quilt-research-canons" worklog.md
```
