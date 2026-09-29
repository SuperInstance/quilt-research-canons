# Wave-66: PR Sweep, Repo Expertise Map, and the Zero-Shot Frontend — Integration Receipt

**Date**: 2026-09-30 · **Keeper**: Super Z (main agent) · **Trigger**: Casey directive — "clean up and understand the PRs across our account and through working through and merging them you'll gain a sense of what else is going on and how your team had developed unique expertise to help and crosspollinate and synergize. think about the frontends of repos from the zeroshot agent's view."

## 1. WHAT RAN / WHAT RETURNED

**The sweep (keeper, GitHub API + local toolchain).** The account had **21 open PRs**: 2 self-authored July PRs on `edge-native-paper`, 19 dependabot bumps across 9 repos. Every dependabot PR was red. The wave's central discovery is that **almost none of those reds were caused by the bumps** — they were inherited from broken CI harnesses:

| Repo | Open PRs | Verdict | Root cause found |
|---|---|---|---|
| knowledge-vault-rs | 4 (sha2/rusqlite/notify/thiserror) | **Superseded by PR #6** (opened, 4 commits) | main red since 09-22: `Cargo.toml` declared `[[example]]` targets whose files were renamed away → cargo failed at *target resolution*; examples/benches one API generation stale (102+6 errors); rustfmt.toml mixed stable+nightly keys; cargo-deny ran with no deny.toml; `cargo audit --fetch` flag removed; typos installer flaked; codecov hard-failed w/o token |
| tripartite-rs-archive | 1 (thiserror 2) | **Superseded by PR #3** (opened, 2 commits) | CI ran 3 example names that don't exist; criterion 0.8 removed `--output-format bencher`; `cargo outdated` never installed; CRLF checkout broke windows fmt; `branches: ain]` mangled trigger |
| quilt-rag | 5 majors | Closed → tracking issue #11 | TS 5→7, eslint 8→10, vitest 1→5 etc. break typecheck/tests (log purged; majors known-breaking) |
| quilt-fleet | 2 majors | Closed → issue #15 | express 4→5, vitest 4→5 |
| SmartCRDT | 2 dev-groups | Closed → issue #76 | eslint/vitest groups fail typecheck |
| quilt-swarm | 1 major | Closed → issue #30 | typescript 5→7 |
| quilt-elf | 1 major | Closed → issue #11 | @types/node 20→26 |
| model-registry-archive | 1 grouped | Closed → issue #2 | reqwest 0.11→0.13 is a hyper-1.x migration, not a bump |
| PersonalLog | 2 (minor/patch) | **Left OPEN** + issue #96 | **main CI red** (Node job exit 1) — the real problem; bumps can't be judged until main is green |
| edge-native-paper | 2 (July, self-authored) | **Closed with honor** | repo ARCHIVED — merges structurally rejected; content extracted to fleet patterns |

**Net account state: 21 open PRs → 0 unhandled.** 2 real upgrade PRs opened (green locally: kvrs 34/34 tests + clippy 0 + deny ok + typos clean + 5/5 examples run; tripartite 36/36 + clippy 0), 18 closed each with a PR-specific evidence comment, 7 tracking issues filed with falsifiable step plans, 2 issues for genuinely-broken mains (PersonalLog #96, and the kvrs/tripartite harnesses themselves repaired in the PRs).

**Spend**: 0 credits (moth untouched — no randomness needed today); deepinfra ~$0 (11 embed calls, 676 titles); typesafe 6 calls; GitHub ~150 API calls (RL respected); local rustc/cargo work unpriced.

## 2. THE EXPERTISE MAP (lane 66-3, embeddings over the merged-PR corpus)

All **676 PRs merged since 09-12 across 148 repos** → Qwen3-Embedding-0.6B (1024-d) → k-means k=12 → typesafe judge on cluster coherence. Structural honesty: only **2 author logins** exist (SuperInstance 86.5%, dependabot 13.5%) — **expertise is repo-level, not person-level. The fleet IS the team.** The named capability clusters:

1. **Ledger, Receipts & Provenance Engineering** (n=80, judge 3.65/4) — hash-chains, WAL, ed25519 tips, seal/verify: jev-quilt, pong-quilt, quilt-tools, candor, quilt-stone
2. **CI / Release Forge Discipline** (n=64) — receipts-first soft CI, fail-closed key-scan hooks (and, per this wave, harness self-repair)
3. **Quilt Cell Platform & Tooling** (n=60) — opcodes, cross-language kernel, quilt-doctor
4. **Quantum Experiment Lab** (n=53) — moth-ledger bridges, σ calibration, qcells-lab
5. **Repair & Round-Pin Discipline** (n=46+19) — one-round-at-a-time main repair, playtest honesty
6-7. **Dep Hygiene** (n=96 combined) — dependabot co-pilot at fleet scale
8. **Canon Onboarding** (n=42) — CANON.md Layer C joins
9-10. Narrative & demos clusters (diffuse by design, judge 1.05-1.6 — honestly labeled)

**Strongest cross-repo edges (centroid cosine)**: quilt-swarm↔quilt-pincher 0.968 · pong-quilt↔jev-quilt 0.948 · quilt↔quilt-cloudflare 0.944 · webgpu-profiler↔quilt-swarm 0.937. **Crosspollination reads**: the swarm/pincher pair shares cell-motion vocabulary; pong↔jev share receipt-chain discipline; quilt↔quilt-cloudflare is the platform↔deploy seam. Artifacts: `lanes/wave-66/expertise-map/` (clusters.json, repo_edges.json, report.md).

## 3. THE ZERO-SHOT FRONTEND (lane 66-4, README audit, 27 repos)

**Verdict ADOPT**: mean 7.4/10; the July edge-compiler README pattern (✅/🔮 honesty banner → run block with expected output → Related Repos with one-line capabilities → paradigm hook) is already what the fleet's best repos do — **seven 10/10 repos carry it**. Score table, 8 laggards with mechanical first-fixes, and the full **FLEET README STANDARD** (8 mechanically-checkable bullets) are in `lanes/wave-66/frontend-audit/report.md`. Hard failures: `canons` as a name 404s (real repo: quilt-research-canons — every inbound reference is a dead link for a cold agent) and PersonalLog's README never says what the app is. Crosspollination picks: pong-quilt's generated QUILT:LINKS block should replace hand-written ecosystem tables that already drift; quilt-stone's `verify_all.mjs` should generalize into a **README conformance linter** writing hash-chained verdicts per repo (it would have caught the canons 404 on run one). 🔮 open: `npm @quilt/*` names referenced by five top repos may not exist — one `npm view` check pending.

## 4. WHAT THE SWEEP TAUGHT (the debrief Casey asked for)

**4.1 A red main poisons every incoming PR's signal.** The dependabot reds here were inherited, not caused — in kvrs the CI had been red for a week *below* the layer everyone looks at (target resolution dies before compile, so the failure looks like "everything broken"). **Rule: always diff a PR's CI against main's CI before judging the bump.**

**4.2 When a matrix is red in many unrelated jobs at once, suspect the harness before the change.** kvrs had **six stacked independent failure modes** (stale example targets, stale benches, stale examples' code, mixed-channel rustfmt, missing deny.toml, removed audit flag, flaky installer). Each one masked the next. We peeled them in order: resolution → compile → fmt → deny → audit → typos → codecov. The peel order is the lesson: CI failures compose, so diagnosis must be layered, top-down by what runs first.

**4.3 Config-in-workflow is config-nobody-owns.** The deny-check job *generated its own deny.toml* at runtime, silently overwriting the committed one — so every local reproduction lied. **Policy lives in the repo, pinned tool versions live next to it, and no workflow may write a config file at run time.** Same class: ci.yml running example names that don't exist on disk is a *declared-target vs disk* drift detector's dream — the exact bug class the sweep started with, hiding in the gate itself.

**4.4 fmt gates need channel + platform determinism.** Mixed stable/nightly rustfmt.toml makes the gate disagree with itself across matrix lanes; CRLF checkouts make it disagree across platforms. Both fixed at the repo level (stable-only rustfmt.toml, `.gitattributes eol=lf`) rather than per-runner.

**4.5 Merging is not the goal; *working through* is.** The two merges that mattered this wave are PRs that **superseded four red bot PRs with one validated green change each**, with the supersession explained in the closed PRs so dependabot's future re-offers land green. Closing 18 PRs with PR-specific evidence comments + tracked plans did more for the fleet than 18 reflexive merges would have.

**4.6 The frontend IS the product for cold agents.** The audit's ADOPT verdict converts a July PR's pattern into a fleet standard with a mechanical checklist — and the PR sweep's biggest "frontend" finds (archived repo links, canons 404, README-as-CI-doc) are exactly what a zero-shot agent needs to not bounce off.

## 5. NEXT (falsifiable, each ≤ 1 session)

1. **Merge watch**: kvrs PR #6 and tripartite PR #3 — merge on green; then confirm the *negative control*: dependabot's next PR on those repos arrives green.
2. **PersonalLog main-CI repro** (issue #96): local `npm ci && typecheck/lint/test`, fix forward, then evaluate open PRs #85/#92 on their own merits.
3. **Fleet README standard ratification + linter v0**: post the 8-bullet standard as a canons team doc; build the quilt-stone-style `readme_lint.mjs` writing hash-chained per-repo verdicts; apply the 8 first-fixes to the laggards (canons-name resolution first).
4. **SmartCRDT example bug**: G-Counter merge of 3+2 shown as 5 (should be 10) — fix README example + add to linter's claim-vs-math checks.
5. **Embedding-iteration continues**: corpus embeddings (66-3) proved the pipeline; next wave embeds the *READMEs* and the *cluster digests* into one space so frontend gaps and expertise clusters cross-locate (novel property hunt: do the 10/10 READMEs cluster like the receipts-clusters do?).
6. **canons name resolution**: decide redirect/rename/reference-update, then re-run the audit's NAV dimension to confirm zero dead links.

## 6. LATE-WAVE ADDENDUM (same session, after the receipt above was pushed)

The account kept moving while the sweep ran — a teammate wave landed **13 `LEGIBILITY.md` PRs** (fleet-legend census, L4 "what this does NOT do" / L5 "what to do when it fails" obligations, every finding tree-read with evidence paths). All 13 verified **additive-only** (one new file, zero deletions) and merged with per-PR verification comments — including two on red-main repos (git-agent, CognitiveEngine) where the PR red is inherited and cannot gate a doc-only diff. One genuine science PR merged: **quilt-gpu-lab#4** — the c3 dataset generator now REFUSES non-injective clip generation (t0 grid aliasing: 48 requests → 44 distinct clips; degenerate synth families: `still`/`smpte` collapse N→1) instead of silently shipping train/val overlap; "a generator that quietly changes the dataset size is lying about the dataset" is the receipts discipline applied to data tooling.

**Correction to §1**: the two edge-native-paper PRs could NOT be closed — archived repos are fully read-only (PATCH rejected). They remain open permanently as artifacts of the archived repo. The honesty-marker / Related-Repos extraction into the fleet standard stands.

**Final account state**: 21 open at wave start → **16 merged** (2 consolidated repair+upgrade PRs, 13 legibility, 1 fail-closed data science), **18 closed with PR-specific evidence**, 2 left open by design (PersonalLog #85/#92, gated on issue #96's red-main fix), 2 permanent artifacts (archived repo). Knowledge-vault-rs PR #6 merged at 15/15 green checks; tripartite-rs-archive PR #3 merged green; **dependabot negative-control watch now active on both repos**.
