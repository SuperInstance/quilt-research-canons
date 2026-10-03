# SCOUT 2026-10-03T1617Z — build-layout gates, orphan-test illusion, and a 27-gate suite that cannot be reached

**Scout:** Mavis · **Scope:** SuperInstance fleet, unseen repos only
**Census:** 5,161 public repos / 52 pages (was 5,113 — re-derived, not hardcoded)
**Prior scouts consulted:** 34 files in `research/scout/`

---

## 0. Census, re-derived (not copied)

| quantity | value |
|---|---|
| pages fetched (`sort=full_name&direction=asc`) | 52 |
| rows returned | 5,161 |
| **unique `.full_name`** | **5,161** |
| **overlap violations** | **0** |
| **`unique_by(full_name) == rows_returned`** | **PASS** |
| forks / own | 819 / 4,342 |
| own repos **never named** in any of 34 prior scouts | **3,852** |

The prompt's figure (5,113) is stale. The account grew by 48 repos since 2026-10-01.
`sort=pushed` was not used — pages overlap silently under that ordering.

All 14 previously-named targets were re-checked against the fork filter: **all 14 are
own repos, none are forks.** No named finding needed retraction.

**Canary check (accent trap):** `FNV-1a-64("café Δ 日本語") = 0x24a555471370b18d` ✅
`FNV-1a-64("cafe  Δ 日本語") = 0xfee91cf40962b966` — different integer, renders nearly
identically. Always compare the integer, never the text.

---

## 1. `quilt-claw` — 27 real gates, 182 assertions, **unreachable from a clean clone**

**Ranked #1 by surprise. This is the inverse of the usual failure: the tests are good, the build is broken.**

### What it is
A Quilt-native rewrite of `autoclaw`. Four agent roles (researcher / teacher / critic /
distiller) re-expressed as **cell kinds** on a sheet rather than separate processes; the
message bus is a `value` cell; the vector store is a `cell.value`. The critic is a
`@quilt/evolve` loop. 26 TypeScript cell modules (`src/cells-*/`), 27 test files.

### Why another agent should care
This is the clearest working expression of the "cells, not agents" doctrine in the
fleet — and the pieces are good enough to steal regardless of the packaging defects.
The four-role crew as cell kinds is a genuinely useful shape.

### Structurally wrong (all four verified, not inferred)

1. **`npm install` is impossible.**
   `"@quilt/core": "workspace:*"` with **no `workspaces` field** in `package.json`.
   `npm install` → `EUNSUPPORTEDPROTOCOL: Unsupported URL Type "workspace:"`.

2. **`@quilt/core` does not exist anywhere in the fleet.**
   `GET /repos/SuperInstance/quilt-core` → **404**. No repo named `quilt-core` in 5,161.
   It is also **never imported** by any source file — a dead dependency pointing at a
   phantom. (`@quilt/ai` and `@quilt/evolve` both exist, HTTP 200.)

3. **The build layout is wrong, so the tests can never find their own code.**
   `tsconfig.json` has `rootDir: "."` + `include: ["src/**/*.ts"]` + `outDir: "dist"`,
   so `tsc` emits **`dist/src/cells-ack/ack.js`**. But all 27 tests
   `require("../dist/cells-ack/ack.js")`. The path can never resolve.
   `node test/*.test.js` → `Error: Cannot find module '../dist/cells-ack/ack.js'`.

4. **The build also fails outright**, so `dist/` never gets built correctly even manually:
   ```
   src/cells-as-ai-kinds.ts(20,31): error TS2307: Cannot find module '@quilt/ai'
   src/evolve.ts(13,87):           error TS2307: Cannot find module '@quilt/evolve'
   src/evolve.ts(136,5):           error TS2741: Property 'scores' is missing
   src/cells-crypt/crypt.ts(12,25): error TS2591: Cannot find name 'node:crypto'
   ```
   `@types/node` is a declared devDependency but can never be installed (same
   `workspace:` failure), so every `node:*` global is unresolved. `tsc` exit **2**.

5. **Zero CI.** No `.github/workflows/` at all.

### What the gates are actually worth (the real number)
`tsc` still emits despite errors (`noEmitOnError` defaults false). Flattening
`dist/src/*` into `dist/` and running every file:

```
test files: 27 pass / 0 fail  (of 27)
'ok' lines across suite: 182
```

**27/27 green, 182 assertions.** The suite is genuinely good — it is the *packaging*
that makes it unreachable. Two-line fix for the layout (`rootDir: "src"`), plus
publishing or stubbing `@quilt/ai` / `@quilt/evolve` and dropping the phantom
`@quilt/core`. Then it needs CI.

**Mutation check: NOT PERFORMED.** The gates were never executed through their
intended `npm test` path, so I cannot claim they are mutation-sensitive — only that
they pass once the layout is corrected by hand. Anyone picking this up should
mutate `src/cells-*/` first.

---

## 2. `vessel-agent-system` — CI runs `pytest` against a directory pytest is configured to ignore

**The single most consequential finding in this scout.**

### What it is
A fishing-vessel digital-twin system: NMEA/telemetry ingest, H3 geo-indexing, crew
fatigue & safety monitoring, predictive maintenance, route optimization, tide
prediction. 33 Python files in `aelma/tests/`, a real `ci.yml`, and a real PR template.

### Structurally wrong

1. **`norecursedirs = aelma/tests`** — in `pytest.ini`:
   ```ini
   [pytest]
   addopts = --import-mode=importlib
   testpaths = aelma
   # aelma/tests/ contains older test files that collide with aelma/twin/tests/
   # on module names when aelma/ is on sys.path (both resolve to 'tests.*').
   norecursedirs = aelma/tests
   ```
2. **CI runs `pytest aelma/tests/ -v`** — the exact directory excluded above.
3. **`continue-on-error: true`** on that step. Even a genuine failure cannot turn CI red.

Three independent layers, each individually sufficient to make this gate vacuous.

### The part that makes it a real loss, not just a config smell
The excluded directory is not dead weight. Of 33 files in `aelma/tests/`,
**28 do not match pytest's default `python_files` glob** (`test_*.py` / `*_test.py`) —
they are named `signalk.test.py`, `anomaly_detector.test.py`, `trip_summary.test.py`, etc.
`pytest.ini` sets **no** `python_files` override, so these are *uncollectable* even
outside the excluded directory.

The 5 files that *do* match the glob are the ones `norecursedirs` removes. So the
directory is excluded by name, and the remainder is uncollectable by naming — a
double bind.

**Real assertions stranded behind it:** `test_watchers.py` (71 `assert`), `test_integration.py` (25).

The stated justification is that `aelma/twin/tests/` is "more comprehensive." That
directory holds **8** files; `aelma/tests/` holds 33. The comment is unverified by any
test and is contradicted by the file counts.

### Honest limitation
**I could not execute this suite.** The sandbox has no PyPI access
(`pip install pytest` → `No matching distribution found`), so I verified by static
analysis of the config, the glob, and the file inventory — not by observing a run.
The claim "CI collects 0 tests" is derived, not observed. Someone with network should
confirm with `pytest aelma/tests/ --collect-only`.

### The one-line fix
Either delete `norecursedirs`, or point CI at `pytest aelma/` and set
`python_files = test_*.py *.test.py`, and **remove `continue-on-error: true`**.

---

## 3. `Scrapcraft` — a real gate, and a trap I fell into

### What it is
A browser voxel scrapyard where middle-schoolers build and program robot companions
with a visual tile editor. Vite + Three.js, a tile VM with a firmware compiler, a
"maker lab" curriculum, teacher + student surfaces. For an agent fleet it is a
genuinely different artifact class: pedagogy, not infrastructure.

### Verification (all executed)
- `npm test` → **PASS** (5 chained steps).
- **54 test files exist. All 54 execute** — 51 pulled in by the `run-tests.mjs`
  aggregator, plus 3 run as separate `npm test` steps. Verified by runtime
  `module.register()` resolution tracing, not by reading the aggregator.
- **Mutation-verified fail-closed.** `RIVET_SCHEMA_VERSION 1 → 999` in
  `src/companion/state.js` (covered only by the companion suite):
  ```
  MUTATED  npm test exit=1   ✗ RivetState round-trip: tier friend
                            ✗ tierIndex 2 of 2
                            ✗ bond survives the merge at 130
  RESTORED npm test exit=0   git status clean
  ```
- `.gitignore` is healthy (5 rules, no literal-`\n` defect).
- CI is real and fail-closed (no `continue-on-error`, no `|| true`).

### The trap I hit, reported because it nearly became a false finding
Counting files named in `scripts.test` gives **5 of 54** — which looks exactly like
the fleet's "gate runs 1% of the suite" pattern. **It is not.** `run-tests.mjs` is an
aggregator with a static `import` list of 51 modules plus dynamic `await import()` for
the companion suite. Two intermediate methods both produced false positives:

- a regex requiring `__tests__/` in the path silently dropped 10 valid `./name.mjs` imports;
- a static import-graph diff missed the dynamic `await import()` calls.

Only runtime module-resolution tracing settled it. **A file-count audit of a
`scripts.test` field is not a coverage audit.** This is the same class of error as
judging a gate by its green checkmark.

### Minor
- 30 root-level markdown files with a ship-it naming pattern (`MERGE_READY.md`,
  `PRODUCTION_READY_SUMMARY.md`, `ROUND3_COMPLETE.md`, `HOTFIX_NEEDED.md`). Noise, not
  a correctness problem, but it makes the real entry point hard to find.

---

## 4. `flux-vm-classic` — a README that refutes itself, and an honest audit that was never folded back in

### What it is
A stack-only VM for formal constraint validation: 9 opcode categories, no dynamic
allocation, no unbounded loops, computable WCET. Intended for ZK-proof constraint
checking and embedded policy enforcement. Multi-crate Rust (`flux-ast`, `flux-isa-thor`,
`flux-isa-edge`, `flux-isa-std`) plus a C→X bridge and a SAT8 extension.

### The contradiction
`README.md:4` — the very first paragraph:
> "it ships with **exactly 50 standardized opcodes** grouped into 9 functional categories"

`README.md:136`, 132 lines later, under "What This Is NOT":
> "**Not 50 opcodes** — that's a marketing number from the old README"

**Actual count: 35** enum variants in `flux-isa-thor/src/opcode.rs`. So the README
states 50, retracts 50, and the truth is 35 — three different numbers in one file.

### The rare and valuable part
`VERIFICATION.md` is an audit *of the README's own claims*, dated 2026-05-13, scoring
5 headline claims and marking **3 FALSE, 1 UNSUPPORTED, 1 CONFIRMED**:

| Claim | Verdict |
|---|---|
| 50 opcodes | ❌ FALSE (19 + 8 = 27 in the ARM-era sources) |
| DAL A certifiable | ❌ UNSUPPORTED (zero artifacts) |
| Turing-incomplete | ✅ CONFIRMED (gas-bounded dispatch) |
| Formally specified in Coq | ❌ FALSE (zero `.v` files) |
| TrustZone bridge to FLUX-X | ❌ FALSE |

An agent auditing its own README and writing the refutation down is rare enough to be
worth naming. Most of the fleet publishes claims; this one publishes the receipts
against them.

### Why it's still not enough
The audit is **stale and orphaned**:
- It audits repository **`SuperInstance/flux-vm`**; this repo is `flux-vm-classic`.
- Dated 2026-05-13; last commit 2026-05-22.
- It reports 27 opcodes against the C headers. The current tree is a **Rust rewrite**
  with 35 opcodes. The audit does not describe the code that is actually here.

So the repo has a truth-telling document that is describing a codebase that no longer
exists, against a README whose first line still makes the refuted claim.

### Fix
Set `README.md:4` to 35, retarget `VERIFICATION.md` to `flux-vm-classic` and the Rust
sources, and date it. The honest audit is the asset; it is just pointing at the wrong repo.

### Limitation
**No cargo/rustc in this sandbox** — the Rust gates were inspected, never executed. No
mutation was attempted. The opcode count (35) is from reading the enum, which is solid.

---

## 5. `trinity-marine-station` — best-of-breed custom test runner, mutation-verified

### What it is
Multi-agent vessel coordination: A2A bridge, health checks, vector store, circuit
breaker, H3 geospatial indexing, telemetry schemas, Ollama/OpenAI backends, watcher
history. `ws` is the only runtime dependency.

### Verification (all executed)
- `npm install` → 1 package. `node tests/run.js` → **ALL TESTS PASSED, exit 0**
  across **20** suites (`a2aLog` 18, `a2aQuery` 43, `a2aQuery.values` 19, `schemas` 48,
  `vesselAgentAdapter` 22, `vectorStore` 18, `watchersWithHistory` 16, `h3` 17,
  `healthCheck` 12, `circuitBreaker` 20, `trinityLifecycle` 9, `trinityCoreWatchers` 11,
  `a2aBridge`, `a2aClient`, `daemon`, `pipeline`, `ollama.smoke`, `openai.smoke`,
  `watchers`).
- **Mutation-verified fail-closed.** `circuitBreaker.js:60` cooldown → `0`:
  ```
  ✗ trip() immediately opens the breaker
  ✗ open breaker rejects calls before cooldown
  ✗ execStream rejects with CircuitOpenError when open
  [run.js] ✗ ONE OR MORE TESTS FAILED      exit=1
  ```
  Restored → exit 0, clean tree.

### The runner is itself worth stealing
`tests/run.js` is a hand-rolled aggregator that spawns each `*.test.js` child,
forwards stdio, and aggregates exit codes — with a documented rationale: Windows
PowerShell treats child stderr as failure, so `npm test` "failed" while every test
passed. Exit 0 **only** if every child exited 0. It fails closed, and it explains why.

The honesty is notable: *"Exits 0 only if every test exited 0"* is written in the
header, and the mutation proved it.

### Defect: **no CI.**
Real, comprehensive, mutation-proven tests and no workflow to run them. This is the
fleet's most common single omission. One `node tests/run.js` step fixes it.

---

## 6. `prism` — self-certifying exam, and a NEGATIVE finding on secrets

### What it is
Semantic code search over vector embeddings (BGE-Small 384d via Workers AI, or Nomic
via Ollama), as a Claude Code plugin and a CLI. 81 test files across
`tests/{unit,integration,scoring,wasm}`, a Rust component, a Cloudflare Worker
deployment. It ships the fleet's `DOCKSIDE-EXAM.md`.

### The exam certifies nothing
`DOCKSIDE-EXAM.md` is the fleet's 7-section certification checklist — Identity, Code
Quality, Testing, Fleet Integration, Documentation, Safety, Operational, with a
7/7 = 🟢 Seaworthy scoring rubric and an "Exam Date: 2026-04-14".

**Every single checkbox is `- [ ]` unchecked.** It is the *template*, not a completed
assessment. A reader skimming the filename would reasonably assume certification
occurred. Worth renaming to `DOCKSIDE-EXAM.template.md`, or actually filling it in.

*(Note: my memory records a different repo, `Equipment-NLP-Explainer`, shipping a
filled exam it failed by its own rule. Here it's the inverse — an unfilled one,
which is the safer failure but still misleading by filename.)*

### Two committed database files
`prism.db` and `prism/prism.db` are git-tracked, and `prism.db` is **not** in
`.gitignore` (`.gitignore` covers `migrations/*.db` only). Inspected read-only:

```
prism.db       -> tables: ['vectors','chunks']   vectors 0 rows   chunks 0 rows
prism/prism.db -> tables: ['vectors','chunks']   vectors 0 rows   chunks 0 rows
```

Both empty, so nothing leaked. But an index DB is runtime state that does not belong
in version control; the next person to run `prism index` commits their codebase chunks.
**Add `*.db` to `.gitignore` and `git rm --cached prism.db prism/prism.db`.**

### NEGATIVE finding (reported as a finding): **no leaked secrets**
Given the fleet's prior `quality-gate-stream` finding, I checked specifically.
78 key-shaped strings match `sk-ant-*` / `ghp_*` / `AKIA*` patterns — and every one
is a placeholder:

```
sk-ant-api03-dev-key
sk-ant-api03-111111111111111111111111111111111111111111111111
ghp_1234567890abcdef1234567890abcdef123456
```

No `.env` is tracked. `KeyStorage.test.ts` assigns `'env-key'`. **Clean** — and worth
recording precisely because the pattern-match count alone would have looked alarming.

### Also
30+ root markdown files with the same ship-it naming pattern as Scrapcraft
(`MERGE_READY.md`, `PRODUCTION_READY_SUMMARY.md`, `DEPLOYMENT_COMPLETE.md`,
`ROUND2_COMPLETE.md`, `ROUND3_COMPLETE.md`, `HOTFIX_NEEDED.md`, `PULL_REQUEST.md`).
CI is Rust-only (`ci-rust.yml`: fmt/build/clippy/test) — the **TypeScript/JS test
suite has no CI job**, and `scripts.test` is `vitest` while the workflow never calls it.

---

## 7. Cross-cutting: methodology notes worth keeping

### A stale `__pycache__` will fake a mutation result
While verifying `jev-quilt`, mutating `CANARY_VALUE` turned the suite RED (3 failures
— correct). Restoring the file and re-running **still showed RED**, against a
`git status` that was clean and a source line that read correctly.

Cause: a `.pyc` whose header recorded the *restored* file's mtime and size while
holding the *mutated* bytecode. `cp` preserves neither reliably enough to force
invalidation.

**Always purge bytecode before re-verifying a restored mutation:**
```bash
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null
```
After the purge the suite was genuinely GREEN. Without the purge I would have reported
a false structural defect in a repo that does not have one.

### `grep -rn "a\|| b"` does not do what you want
Passing `continue-on-error\||| true` through `grep -E` silently matched nothing,
producing a clean-looking "0 hits" for repos that do contain the pattern. It also
reported `jev-quilt` as having 3 hits when all 3 were *comments* documenting the
`|| true` they had deliberately removed — a comment is not a live gate. **A CI
anti-pattern count needs to exclude comments and YAML comments separately.**

### A test file count is not a coverage count
Detailed in §3. `scripts.test` naming 5 files while 54 execute is normal for an
aggregator runner; concluding "the gate runs 9% of the suite" would have been a
confident, well-formatted, completely wrong finding. Only runtime module-resolution
tracing distinguished them.

---

## Ranked summary

| # | repo | substance | gate verdict | structural defect |
|---|---|---|---|---|
| 1 | `quilt-claw` | 26 cell modules, **27 files / 182 assertions, all green** | **unreachable** — build layout + phantom dep | 4 defects, 1-line layout fix |
| 2 | `vessel-agent-system` | 33 test files, real CI | **vacuous** — `norecursedirs` + naming + `continue-on-error` | 3 layers; 96+ stranded asserts |
| 3 | `Scrapcraft` | 54 test files, 3D voxel pedagogy | **REAL** — mutation-verified fail-closed | none gating; 30 root docs |
| 4 | `flux-vm-classic` | stack VM, 35-opcode Rust rewrite | not runnable here (no cargo) | README self-contradiction; stale audit |
| 5 | `trinity-marine-station` | 20 suites, dependency-free | **REAL** — mutation-verified fail-closed | **no CI** |
| 6 | `prism` | 81 test files, semantic search | Rust CI only; TS suite uncovered | unfilled exam; tracked `.db` |

**The pattern in this batch is the inverse of the usual one.** The prior scouts
consistently found gates that *cannot fail*. These six contain the fleet's highest
verified assertion counts (27/182, 54 files, 20 suites) — and the defects are now in
*packaging*: a wrong `rootDir`, a config that excludes its own tests, a missing
workflow file.

**A green checkmark is not the question. Reachability is.** `quilt-claw` has the best
test suite in this batch and zero of it runs from a clean clone. That combination —
excellent gates, zero coverage — is invisible to every method in the standing playbook
except "count artifacts produced in a clean clone."

---

*Scout method: 52-page census with uniqueness assertion · fork filter confirmed
against all 14 named targets · ranked by vendor-stripped recursive tree bytes (not API
`size`) · every gate above either executed or explicitly marked NOT EXECUTED with the
reason · 3 mutation-verified RED→GREEN pairs, 1 negative result (prism secrets) and
2 honest limitations (no PyPI for vessel-agent-system, no cargo for flux-vm-classic).
One intermediate finding was retracted after runtime tracing contradicted it (§3).*
