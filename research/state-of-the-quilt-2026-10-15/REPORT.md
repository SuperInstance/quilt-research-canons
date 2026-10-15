# State of the Quilt — October 2026

> A quarterly-style summary of what's merged, what's open, what's next. For the captain, for new contributors, for anyone catching up.

## TL;DR

The Quilt project had a 26-PR burst in the 6 days leading up to this report (Oct 9–15), with all PRs #1–#26 of `git.pp-ng` merged. The fold is real (1,151/1,151 conformance across 3 ports), the audit/gate/ledger/ship-gate stack is shipped, and the open design questions are documented. The §6 doctrine question is the only thing blocking the next merge.

## What's MERGED (since 2026-10-09)

### `patchwork-quilt/git.pp-ng` (the hub)

26 PRs merged in 6 days, all green, all green, all green. The 26 include:

- **The fold's graduation from spike to production.** #7 (checkpoint v2 spike) → #9 (graduation) → #14 (memoised ancestry engine, scale wall fix) → #15 (production checkpoint+tail derivation) → #21 (frontier checkpoints wiring).
- **The conformance corpus's graduation.** #3 (depth-pass: fold correctness + determinism fixes) → #4 (README totals to the verified depth-pass numbers) → #11 (production-scale corpus, 62/250/1,000 records, three-way oracle) → #13 (spec-truth: candidates defined).
- **The runner's production hardening.** #5 (pp.py pre-push refusals: secrets, genesis guard, kind discipline) → #8 (refuse empty-effects task records) → #18 (override-grounding refusal).
- **The docs-accuracy sweep.** #10 (README graft R4 Proposal B structure) → #17 + #19 (gauntlet wave-1 and wave-2 artefact fixes) → #23 (retarget demo video link) → #24 (RESULTS.md: the honest ledger) → #25 (format v2: records born with digests) → #26 (checkpoints and the bitset engine have shipped — correct the stale wording).
- **The license and bookkeeping.** #6 (LICENSE: copyright holder SuperInstance).
- **The frontier checkpoints.** #20 (set-form closure roots) → #21 (read path + runner default).
- **The security and conformance.** #12 (Production security pass: F2 route removal, F1/F3 fixes, P1–P4).
- **The depth-pass.** #3 (fold correctness + determinism fixes, collection speedup, engineering audit).
- **The docs-accuracy polish (open, not yet merged).** #27 — adds `npm test` running the full offline battery, fixes `scene.sh`'s `PP_POC_DIR=../../poc` bug, and sweeps stale wording in README/DESIGN/DEPLOY/RESULTS.

### `patchwork-quilt/git.pp` (the substrate)

- #1 (2026-10-09, merged) — "Add end-to-end architecture; restore the tested substrate." The original architecture, plus the judgment log v2 and the tested tick.sh/project.sh.

### `patchwork-quilt/git.pp-grid` (the Grid UI)

- #1, #2, #3 all merged Oct 14–15. "Generalise the Grid: one engine, many instances." SSR facts snapshot. Face-grade fixes (latest settlement reason + open proposal note on the cell face; counter-proposal affordance).

### `patchwork-quilt/git.pp-desk` (the captain's desk)

- #1 (2026-10-15, merged) — "Desk v2: closure-root pinning, manifest-gated refresh, the real destroy() test."

### `patchwork-quilt/gitpp-beam` (Elixir port)

- #1 (2026-10-15, merged) — "Link sweep: retarget git.pp-ng references to patchwork-quilt (post-transfer)."

### Dependabot (the `quilt-*` runtime repos)

- `quilt-pincher` #21–#25 (merged) — dev-dep bumps: `@typescript-eslint/eslint-plugin 8.71.0`, `vitest 5.0.3`, `@types/node 26.6.4`, `@typescript-eslint/parser 8.71.0`, `eslint 10.12.0`. All green, all squashed.
- `quilt` #38 (merged) — patch-and-minor group: `@types/node 26.6.5`, `@typescript-eslint/* 8.71.1`, `eslint 10.12.0`, `@modelcontextprotocol/sdk 1.32.1`.
- `quilt-cloudflare` #20 (merged) — patch-and-minor group: `@cloudflare/workers-types 5.20261010.1`, `wrangler 4.149.0`, `eslint 10.12.0`, `@typescript-eslint/* 8.71.1`.

## What's OPEN and awaiting a decision

| # | Repo | What | Decision needed |
|---|---|---|---|
| #2 | `patchwork-quilt/git.pp` | Audit stream, region gate, ledger, ship gate | Engineering — calibration table review |
| #16 | `patchwork-quilt/git.pp-ng` | Retraction spike (dispute + settlement mechanics) | **Captain** — §6 doctrine |
| #27 | `patchwork-quilt/git.pp-ng` | Polish + CI pass | Engineering — `grep` check for half-applied scene.sh fix, then merge |
| #1 | `SuperInstance/fold-bout` | Claude's Bout 1 entry | **Referee (Muse)** — score against the stress set |

The §6 doctrine is the only blocker for the next merge in the active stream. The doc is at `quilt-research-canons/research/retraction-doctrine-2026-10-15/DOCTRINE.md` — three options, recommended Option II.

## What was CLOSED (this session's PR sweep, 2026-10-15)

- `quilt#39` — TS 6→7 major bump. ERESOLVE on `@typescript-eslint/eslint-plugin@8.71.0`. Closed with reference to `quilt#34` (the prior rollback).
- `quilt-cloudflare#21` — same TS 6→7 bump, same failure. Closed with reference to `quilt-cloudflare#15` (the prior attempt).
- `Lucineer/purplepincher.org#1` — 6 months stale, no CI, base moved on. Closed.
- `Lucineer/the-seed#2` — 6 months stale, no CI, +310/−372 on a single file, master has been quiet since April. Closed.

## What was BUILT (R&D, this session)

- **`SuperInstance/git.pp-spec`** — The canonical, normative spec for the record format. ~280 lines, 11 sections. Useful for any new port.
- **`SuperInstance/git.pp-doctor`** v0.1.0 — A single-file Python validator, stdlib only. Three commands (`root` / `check` / `fold`), three-way verdict. CI workflow runs against the live `poc-quilt-1` deployment. Receipt: closure root at `poc-quilt-1@task-c` = `60effe23970d8a5cc837636c44685502361288c1f00577e9addfa10cbd4fc91d` (matches hub exactly).
- **`SuperInstance/gitpp-rust`** — Scaffolded, 4th port in progress. Doc-only discipline.
- **`SuperInstance/quilt-status`** — A single-page index of the 4 orgs and 9 active repos.
- **`SuperInstance/what-is-the-quilt`** — A one-page explainer for newcomers.
- **`quilt-research-canons/research/retraction-doctrine-2026-10-15/`** — The §6 doctrine doc, three options, recommended Option II. HANDOFF.md §3 updated.

## The numbers

| What | Number | Source |
|---|---|---|
| Conformance cases | 1,151/1,151 | git.pp-ng/conformance/ + the §6 retraction families |
| Checkpoint probes | 1,029 | CKPT_V2_EXPECTED |
| Witness-freshness checks | 3,231 | same |
| Closure-root digests compared | 16,290 | same |
| Three-way pins (live-golden + oracle) | 2,820 | same |
| Fold ports | 3 in production (TS, Python, Elixir) + 1 in progress (Rust) | git.pp-ng / git.pp-ng/referee / gitpp-beam / gitpp-rust |
| Live records on the demo | 8 (poc-quilt-1) | https://gitpp.superinstance.dev/api/records?project=poc-quilt-1 |
| Fold time at 62 records | 1.8 ms | git.pp-ng/RESULTS.md |
| Live-read time, full | 2.42 s | git.pp-ng/RESULTS.md |
| PRs merged in the last 6 days | 26 (git.pp-ng) + 5 (sister repos) | git.pp-ng/branches/main log |
| Repos in `SuperInstance` | 5,208 (sketchbook) + the 9 active in this report | GitHub API |
| Repos in `patchwork-quilt` | 5 public + 1 private | GitHub API |
| Repos in `purplepincher` | 19 public | GitHub API |
| Repos in `si-ready` | 1 (.github profile only) | GitHub API |

## The open design questions

From `git.pp-ng/docs/OPEN-QUESTIONS.md` and the §6 doctrine doc:

1. **§6 doctrine (PR #16):** May a third party's accusation, once ratified, stain a record its author still stands behind? **Three options in the doctrine doc. Recommended: Option II.** Captain's call.
2. **1a. Read-sets and read-hazards.** Engineering — a sibling function that flags when a record's completion rests on a read the current state has since moved. Recommend `reads` value-form; hazard is advisory, never state-deciding.
3. **1b. Record-count vs key-scoped freshness.** Engineering — `recordsBehind` (current) vs `keysSupersededSince` (proposed). Ship v2 if operators are misled by the current number.
4. **1c. Verification in the fold vs an ingest gate.** **Captain's call.** Self-consistency + spot checks vs. gate-on-accept. The latter re-introduces a trusted service in the write path.
5. **1d. Lock-vs-override.** **Captain's call.** (A) override always wins, or (B) locked defaults outrank override for that key.

## What to do next

- **Captain signs §6 doctrine** (recommended Option II). One paragraph in `docs/RETRACTION-SPIKE.md`. PR #16 graduates.
- **Merge PR #27** after a `grep` check for the `PP_POC_DIR=../../poc` half-apply. Polish + CI pass, all green.
- **Merge PR #2** in `git.pp` after the calibration table review. The audit/gate/ledger/ship-gate stack is the §2 architecture's main contribution.
- **The Rust port ships.** A `Coder` subagent is implementing the leaf + closure root + 1 test in `gitpp-rust`; the push gate is enforced this time. If the subagent lands, the next step is the fold on top.
- **A 5th fold port** (Lua? Ruby? Zig?) catches different shared assumptions than the 3 production ports. The spec and the corpus make the doc-only-discipline workflow tractable.
- **Triage the public-facing bugs in the SuperInstance org.** `plato-portal` empty-door defect (25 mode-160000 gitlinks, no `.gitmodules`), `SuperInstance/health` PII exposure (40MB PHI PDFs, public since January 2026), `flux-lucid` 0/19 green CI with a test dir the workflow can't see, `spreadsheet-engine` conservation monitor with no writer outside tests.

## The honest assessment

The Quilt's fold is real and conformant across three ports. The architecture is sound. The audit/gate/ledger/ship-gate stack is shipped but needs broader validation. The 5,208-repo sketchbook is intentional noise, not a bug, but the public-facing bugs in the active stream are real and worth fixing. The §6 doctrine is a real design question, not a bug. The Rust port is the only unfinished item from the recent R&D burst; the 4th-port scaffold is up and a Coder subagent is implementing.

The next six weeks, if the captain's calls land and the Rust port ships, will be the most concrete version of the project so far: 4 conformant ports, a signed §6 doctrine, a public record-format spec, and a public record-set validator. The bottleneck is the captain's time, not the engineering.

