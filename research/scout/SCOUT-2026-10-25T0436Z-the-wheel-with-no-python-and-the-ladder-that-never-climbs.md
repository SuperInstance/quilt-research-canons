# SCOUT 2026-10-25T0436Z — the wheel with no Python in it, the ladder that never climbs, and the two detectors that cannot fail

**Scope:** the never-examined pool of the SuperInstance fleet. Every finding below was **executed**, not inferred: Rust crates were compiled with a real `cargo` toolchain, Python suites were run in clean clones, and every "gate" was **mutated** to prove it can go red. Where a repo had been examined by a prior scout, that is stated plainly and only the *new* part is claimed.

**Census re-derived (never hardcoded):** `GET /users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc`, paged to exhaustion. **54 pages, 5,308 public repos, 0 duplicate `full_name`** (asserted `unique_by(.full_name) == rows_returned`; the short final page held 8 rows). Split: **4,486 own + 822 forks.** Identical to the 2026-10-25T0130Z round — the fleet did not grow in the two hours between rounds.

**Pool:** 149 prior scout files (3.9 MB of prose) were tokenised once into 44,887 repo-like tokens and matched against every own repo name. **2,541 own repos have never been named in any prior scout report.**

**Ranking method:** API `size` is git *history*, not substance, so it was only a prefilter. Real trees were pulled via `git/trees/{branch}?recursive=1` for **all 2,786** never-examined own repos (39 errored) and ranked on **code bytes by extension, excluding vendored paths** (`node_modules`, `vendor`, `target`, `dist`, `build`, `__pycache__`, `.venv`, `venv`, `.next`, `coverage`, `.git`).

The trap is the same every month and it is large: the raw-byte top of the fleet is `SuperInstance-archive` (71 MB of Python in a portfolio snapshot), `Lucineer` (12 MB), `ACE-Step-1.5` (5 MB) — and `Equipment-Memory-Hierarchy`, whose 18 MB of API "size" is **994 committed `node_modules` files**, not 134 KB of code. Ranking on API size would have put all of them on top.

---

## 1. `cache-layer-optimizer` — the wheel contains no Python, the crate cannot resolve, and the CI cannot fail

**Never examined** (appears once in a prior file only as a name inside a bulk "not examined" list). This is a **dual-language repo with two independent build breakages and a CI that is structurally incapable of detecting either.**

### 1a. The Python package is never packaged — `src/` is a Rust directory

The README leads with:

```bash
pip install cache-layer-optimizer
```

`pyproject.toml` declares `[build-system] requires = ["setuptools>=68.0"]` and **contains no `[tool.setuptools]` section at all**, so setuptools auto-discovery decides the layout. The repo has a `src/` directory — **eight `.rs` files, zero Python** — and setuptools reads that as the **src-layout** and looks for packages *under* `src/`:

```
$ python3 -c "from setuptools import find_packages; print(find_packages(where='src'))"
[]
$ python3 -c "from setuptools import find_packages; print(find_packages(where='.'))"
['cache_layer_optimizer', 'tests']
```

The actual build metadata confirms it. `prepare_metadata_for_build_wheel` produces:

```
$ cat /tmp/clo_meta/cache_layer_optimizer.egg-info/top_level.txt
$ cat /tmp/clo_meta/cache_layer_optimizer.egg-info/SOURCES.txt
LICENSE
README.md
pyproject.toml
```

**`top_level.txt` is empty and `SOURCES.txt` contains no `.py` file at all.** The wheel ships a licence, a README and a `pyproject.toml`, and **zero importable modules**. The 615-line `cache_layer_optimizer/` package sitting at the repository root — which is the *entire* Python API the README documents — is never included in any distribution.

The package is also not on PyPI (`GET https://pypi.org/pypi/cache-layer-optimizer/json` → **404**), so the README's one-line install instruction cannot work by either route.

### 1b. The Rust crate cannot resolve its own dependency

`Cargo.toml`:

```toml
[dependencies]
cache-layer = { path = "../cache-layer", default-features = false }
```

A path dependency. In a clean clone the sibling does not exist, and crates.io has never heard of either crate (`GET https://crates.io/api/v1/crates/cache-layer-optimizer` → `crate 'cache-layer-optimizer' does not exist`). Executed in an isolated clone:

```
$ cargo check --all-features
    Updating crates.io index
error: no matching package named `cache-layer` found
location searched: /tmp/scout/cl/cache-layer
required by package `cache-layer-optimizer v0.1.0`
EXIT=101
```

**`SuperInstance/cache-layer` does exist** and is feature-compatible (`memory`, `redis`, `disk` all present) — so the crate builds if and only if you clone two repos as siblings. This is the `substrate-*` `file:../` pattern again, in Rust: **publishable to nobody, installable by nobody, buildable only by an agent who knows the undocumented sibling convention.**

### 1c. The CI cannot fail — and 1,599 lines of Rust tests have never run

`.github/workflows/ci.yml` in full:

```yaml
      - run: cargo check --all-features || true
      - run: cargo test --all-features || true
```

Both steps are `|| true`. **8 CI runs; the 5 most recent are green.** The `tests/` directory holds **4 Rust test files totalling 1,599 lines** (`coherence_tests.rs` 403, `predictive_tests.rs` 386, `tiering_tests.rs` 405, `warming_tests.rs` 405) plus 388 lines of Python tests — and **not one of them has ever executed in CI**, because the crate cannot compile in CI and the `|| true` converts the failure into a green checkmark.

There is **no Python test step either.** The `Makefile` has `test:` → `cargo test --all-targets` and `perf-validate:` → `cargo test --release --test performance_tests` — and **`tests/performance_tests.rs` does not exist.**

### 1d. The provenance points at an organisation that does not exist

`Cargo.toml` says `authors = ["Equilibrium Tokens"]` and `repository = "https://github.com/equilibrium-tokens/cache-layer-optimizer"`. `GET /repos/equilibrium-tokens/cache-layer-optimizer` → **404**; `GET /orgs/equilibrium-tokens` → **404**. The sibling `cache-layer` carries the same phantom author and the same dead repository URL. Nothing in the repo connects these crates to `SuperInstance`.

### 1e. The README's own Quick Start does not run — four separate breaks

The README's first code block is the thing every reader types first. Executed verbatim:

| README says | the code says |
|---|---|
| `CacheLayer(name='L1', max_size=100, ...)` | `TypeError: CacheLayer.__init__() got an unexpected keyword argument 'max_size'` — the field is `max_size_bytes` |
| `MultiTierCache(layers=[...])` | the parameter is `tiers` (`TypeError` on `layers`) |
| `EvictionPolicy.TTL` | `AttributeError: TTL` — the enum is `LRU, LFU, FIFO` only |
| `EvictionPolicy.ADAPTIVE` | `AttributeError: ADAPTIVE` — does not exist |
| `result.tier_adjustments` | `AttributeError: 'OptimizationResult' object has no attribute 'tier_adjustments'. Did you mean: 'adjustments'?` |
| `PlacementPolicy.decide(key, access_pattern)` | the signature is `decide(self, key, size_bytes)` |
| API reference: "EvictionPolicy — LRU, LFU, FIFO, TTL, ADAPTIVE" | two of the five documented policies do not exist |

The README's own API-reference section documents **five** eviction policies; the implementation has **three**.

### 1f. The library is real — that is the tragedy

The Python implementation is not a stub. With the *correct* API, the entire suite passes:

```
$ PYTHONPATH=/tmp/shim:. python3 /tmp/shim/pytest.py tests
PASSED=44 FAILED=0
```

**44/44.** The code works, the tests work, the docs are wrong, the packaging drops the package on the floor, and the CI cannot see any of it.

**Why another agent should care:** this repo is the canonical fleet shape — a real implementation, a real test suite, a CI badge, and four independent defects stacked so that each one hides the next. Any agent that trusts a green checkmark here will ship a package with no code in it.

---

## 2. `Equipment-Memory-Hierarchy` — a skill ladder that can never be climbed, behind a 34/34 green suite

**Partially known:** the vendored `node_modules` mass (994/1,012 tracked files) and the missing `test` script were reported on 2026-10-07. **The following is new.**

4,758 lines of TypeScript implement a four-tier cognitive memory (Working / Episodic / Semantic / Procedural) with a skill-promotion ladder: `LEARNING → PRACTICING → COMPETENT → EXPERT → AUTOMATIC`.

`src/ProceduralMemory.ts` reads a config field that does not exist. The declared field is `expertiseThreshold` (`src/types.ts:307`, default `50` in `src/ProceduralMemory.ts:28`); the ladder reads `expertThreshold`:

```
src/ProceduralMemory.ts:557:    if (status === SkillStatus.PRACTICING && executionCount >= this.config.expertThreshold / 2) {
src/ProceduralMemory.ts:563:    if (status === SkillStatus.COMPETENT && executionCount >= this.config.expertThreshold) {
src/ProceduralMemory.ts:569:    if (status === SkillStatus.EXPERT && executionCount >= this.config.expertThreshold * 2) {
src/ProceduralMemory.ts:578:    const experienceFactor = Math.min(1, item.executionCount / this.config.expertThreshold);
```

At runtime `this.config.expertThreshold` is **`undefined`**, so every comparison is `>= NaN` → `false`. The first gate (`learningThreshold`, which does exist) fires; the other three never can.

**Receipt** — 300 executions, all successful, `successRate` 1.0000:

```
learningThreshold = 3 (exists)
expertiseThreshold= 50 (exists)
expertThreshold  = undefined   <-- read at ProceduralMemory.ts:557,563,569,578

=== AFTER 300 SUCCESSFUL EXECUTIONS (success=true, executor returns ok) ===
status         : practicing
executionCount : 300
successRate    : 1.0000
confidence     : NaN
```

`confidence` is **NaN on every single skill execution** — `calculateConfidence` divides by the same `undefined` (`Math.min(1, 300/undefined)` → `NaN`), and `NaN * 0.3` poisons the whole sum.

**Mutation receipt — the suite cannot see it.** Replacing the four `expertThreshold` reads with `expertiseThreshold`:

| build | status after 300 executions | confidence | suite |
|---|---|---|---|
| pristine | `practicing` | `NaN` | **34/34 PASSED** |
| mutated (fixed) | **`expert`** | **0.9999999999999907** | **34/34 PASSED** |

The suite is green in both worlds. **It is not a weak assertion — the suite simply never drives a skill past `PRACTICING`, so the three dead gates are outside its reach entirely.** 300 successful executions and a 100% success rate still cannot promote a skill, because the thing that promotes it is `undefined`.

**The type checker *does* catch it** — `tsc` reports `TS2551: Property 'expertThreshold' does not exist on type 'ProceduralMemoryConfig'. Did you mean 'expertiseThreshold'?` four times, and `npm run build` is literally `tsc`. But this repo's CI has been **red since 2026-04-14** (3 runs, all `failure`), so the one signal that fires is a signal nobody reads.

### The vendored `node_modules` is also the wrong architecture

Known: 994 of 1,012 tracked files are `node_modules`, and there is **no `.gitignore`** at all. New and load-bearing: the vendored tree contains exactly one native binding, and it is for the wrong CPU.

```
$ ls Equipment-Memory-Hierarchy/node_modules/@rolldown/
binding-linux-arm64-gnu
pluginutils
$ uname -m
x86_64
$ node_modules/.bin/vitest run
Error: Cannot find module '@rolldown/binding-linux-x64-gnu'
  cause: Error: Cannot find module '../rolldown-binding.linux-x64-gnu.node'
```

The 18 MB of committed dependencies were captured on an **ARM** machine, so the offline tree is unusable on x86-64 — which is every GitHub Actions runner. The suite cannot be run from a clean clone without a network install, and `npm ci` in CI **deletes the committed tree and reinstalls anyway**. So the vendored dependencies are simultaneously unusable and useless.

**Why another agent should care:** `Equipment-Memory-Hierarchy` is the most substantial single-repo implementation in the never-examined pool, and it is a working cognitive-memory engine with one silently dead dimension: it can never tell you it has become competent.

---

## 3. `Equipment-Self-Improvement` — its test file is written against an API that does not exist, and two of its detectors cannot fail

**Partially known:** the vendored mass (1,018/1,034) and the missing `lint` script were reported on 2026-10-07. **The following is new.**

5,134 lines of TypeScript implementing self-modification, performance monitoring and knowledge distillation. `src/` compiles **clean** — 0 errors. The **test file has 42 TypeScript errors**, and they are all of one kind: the test calls a different API than the source declares.

```
src/__tests__/self-improvement.test.ts(17,33): error TS2353: Object literal may only specify known properties,
  and 'name' does not exist in type 'Omit<PerformanceMetric, "id" | "timestamp">'.
src/__tests__/self-improvement.test.ts(52,37): error TS2561: Object literal may only specify known properties,
  but 'content' does not exist in type 'Omit<AgentObservation, "id" | "timestamp">'. Did you mean to write 'context'?
```

The source declares `PerformanceMetric { id, timestamp, metricType, value, unit, context, agentId?, cellId?, tileId? }` and `AgentObservation { id, timestamp, agentId, context, inputs, actions, outcomes, success, duration }` — with `agentId` **required**. The test passes `{ name, value, category }` and `{ content, category }` and omits `agentId` entirely.

**Neither CI nor `tsc` can see this.** `vitest` does not typecheck, and `tsconfig.json` excludes `"**/*.test.ts"` from the build. The 42 errors are invisible to both gates, and the suite is **23/23 green**.

### What the phantom API does at runtime

`recordMetric` spreads the caller's object and stamps an id and a timestamp. It never constructs a `PerformanceMetric`:

```
=== recordMetric({name:'latency',value:150,category:'performance'}) -> stored metric ===
{ "name": "latency", "value": 150, "category": "performance",
  "id": "pm_1792902488544_us6t9d1kz", "timestamp": "2026-10-25T04:28:08.544Z" }

metricType : undefined  <-- undefined
unit       : undefined  <-- undefined
```

Every metric in the system therefore has **no type and no unit**. The anomaly detector iterates `getMetricTypes()` and the opportunity engine classifies by type — so the reports it produces are malformed:

```
detectAnomalies() -> 1 anomaly
  "undefined value 9999 deviates 3444.82 standard deviations from mean 104"
```

### Mutation receipt: both detectors are unfailable

`detectAnomalies` was made to `return []` and `identifyImprovementOpportunities` was made to `return []`:

```
MUTANT 1 applied: detectAnomalies -> []
MUTANT 2 applied: identifyImprovementOpportunities -> []
=== RUN SUITE WITH BOTH DETECTORS MUTATED TO ALWAYS-EMPTY ===
PASSED=23 FAILED=0
```

**23/23 green with the entire anomaly-detection and improvement-opportunity machinery disabled.** The two tests that cover them assert only `expect(Array.isArray(anomalies)).toBe(true)` — which an empty array satisfies perfectly. A whole feature area of a self-improvement system is untested, and the suite reports green.

For contrast, the sibling `Equipment-Self-Improvement` *does* declare `"test": "vitest run"`, so its test step is real; the failure there is not that CI is hollow but that **CI is blind to a 42-error test file**.

**Why another agent should care:** `Equipment-Self-Improvement` is the fleet's self-modification engine, and its central promise — "notice when performance degrades, then suggest improvements" — is exercised by two `Array.isArray()` assertions that survive the feature being deleted.

---

## 4. `Baton` — a CI that cannot fail, wrapped around a test that cannot import

**Known in part:** 2026-10-10 reported "genuinely healthy (61/61) with one real coverage hole in its flagship feature" and named `lineage_tracker`. **This round confirms the hole is now a hard CI failure that CI swallows.**

Every step of `Baton/.github/workflows/ci.yml` is `|| true`:

```yaml
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt || true
          pip install -e . || true
      - name: Lint with ruff
        run: |
          pip install ruff || true
          ruff check . || true
      - name: Run tests
        run: |
          python -m pytest || true
```

- `requirements.txt` **does not exist** in the repo — that install fails immediately and is swallowed.
- `ruff check .` cannot report a lint error and cannot fail the job.
- **`python -m pytest || true`** — the test step cannot fail. **6 CI runs, all green.**

And the test step *would* fail. `tests/test_lineage_bridge.py` line 8:

```python
from lineage_tracker import LineageTracker
```

`lineage_tracker` is **not in the repo**, **not in `pyproject.toml`** (the package declares `dependencies = none`; only `dev = ["pytest>=7.0", "pytest-cov"]`), and **not on PyPI under either spelling** (`/pypi/lineage_tracker/json` → 404, `/pypi/lineage-tracker/json` → 404). Executed:

```
PASSED=61 FAILED=1
  FAIL test_lineage_bridge.py::<import> -> ModuleNotFoundError: No module named 'lineage_tracker'
```

pytest exits non-zero on that collection error. **`|| true` converts it into a green checkmark.**

The library itself is good: **61/61 real tests pass**, and the README badge honestly says "tests-61%20passing". The `AutoBaton`/`Baton` split, the lesson types (`timeless`/`temporal`/`deprecated`), the environment-aware validator and the bootstrap brief are all genuinely implemented.

**Why another agent should care:** `Baton` is a real tool with a real suite whose flagship feature (the lineage bridge) has been un-runnable since the day it was written, and whose green badge has been reporting that fact as success for the entire life of the repository.

---

## 5. GEMS — three strictly-unexamined repos that are actually good

These have **zero prior mentions** in 149 scout files. All three were cloned clean and executed.

### 5a. `fleet-build` — the loop the fleet does not run (82/82, compiled and run)

**The gem.** A Rust CLI that automates exactly the workflow the fleet keeps doing by hand. Its README says it was built from "analysis of 10 real sessions and 652 tool calls", and the top of the list is `cd` into a repo (116 occurrences), `cargo test` (78), fix errors (45 edits), `git push` (22).

```
$ cargo test --all-targets
   Compiling fleet-build v0.1.0
     Running unittests src/lib.rs
running 63 tests
test result: ok. 63 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
     Running tests/integration.rs
running 19 tests
test result: ok. 19 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
EXIT=0

$ cargo run -- --help
Automated Rust crate build/test/fix/push CLI
Commands:
  build   Clean build: remove target dir, run cargo test, capture output
  fix     Read error output and apply common automated fixes
  push    git add -A, commit, push with secret scanning
  batch   Run build+test+push on multiple repos in parallel
  status  Scan ~/repos for uncommitted changes, failing tests, missing READMEs, etc
  clean   Remove all target/ directories under ~/repos
```

**82/82, `EXIT=0`, and the binary runs.** No path dependencies, no vendored blobs, a lib + bin split with real integration tests. `push` even does secret scanning before pushing.

**Why another agent should care, specifically:** `cache-layer-optimizer` in §1 is a crate whose CI is a green `|| true` over a build that exits 101. `fleet-build build` would have caught that in one command. **The fleet built the tool that finds this class of defect and has not pointed it at its own repositories.**

### 5b. `edge-relay-agent` — 82/82, zero dependencies, and it documents its own limits

Models asymmetric information flow between a cloud and a resource-constrained edge: a `ResearchRelay`, four "tender" carriers (`ResearchTender`, `DataTender`, `PriorityTender`, `ContextTender`), a `DiscoveryService` with heartbeat health monitoring, and a `BandwidthBudget` that allocates bytes/second across message types with overflow queuing and priority preemption. Eight-subcommand CLI persisting to JSON.

```
PASSED=82 FAILED=0 SKIPPED=0
```

Its README states: *"The core engines are complete and covered by **79 passing tests**. The network-facing pieces (a listening `serve` loop, real peer auto-discovery over the wire) are intentionally **not** implemented — this is an in-process engine and CLI, not a deployed network service."*

The suite is now **82** (the README says 79 — it grew, and the README is not updated, a minor but real drift). The important part is the **honesty assessment section**, which enumerates real-vs-stub per component. That is rarer in this fleet than working code.

### 5c. `flux-vm-agent` and `training-data-collector` — 56/56 and 18/18

`flux-vm-agent` is a standalone bytecode VM with an assembler, an interpreter, an LCAR bridge, a CLI and a workshop directory: **56/56 PASSED**. `training-data-collector` converts gameplay data into training data with QLoRA export: **18/18 PASSED**. Both are zero-dependency, both have real CI, and neither has been looked at by anyone.

---

## 6. `Spreader-tool` — status confirmation, and the strongest mutation receipt in the fleet

**Previously examined** (2026-10-02: "337/337"; 2026-10-11: "a 'frozen' snapshot whose payload is writable, and a 'proven' flag with no proof"). **This round re-verifies 337/337 and adds the mutation proof that the prior rounds did not have.**

4,036 lines of pure-Python dataclasses implementing deadband detection with hysteresis, frozen copy-on-write context windows, a seed lock pipeline, redaction and a self-optimiser. CI is real — `python -m pytest tests/ -v`, **no `|| true` anywhere** — and green.

**Mutation 1 — disable the deadband detector.** `is_breached = (value < threshold) if below else (value > threshold)` → `is_breached = False`:

```
PASSED=325 FAILED=12
  FAIL test_deadband.py::TestEntersDeadband::test_completion_rate_drop
  FAIL test_deadband.py::TestEntersDeadband::test_wait_time_sustained
  FAIL test_deadband.py::TestExitsDeadband::test_recovery
  FAIL test_deadband.py::TestHysteresis::test_no_flicker_on_marginal_recovery
  FAIL test_deadband.py::TestMultipleMetrics::test_all_four_breached
  ... (12 RED)
```

**Mutation 2 — delete the seed-lock precondition guard** (`if seed.state != SeedState.LOCK_PENDING: raise ValueError(...)`):

```
PASSED=336 FAILED=1
  FAIL test_seed_lock.py::TestLock::test_cant_lock_without_validation
       -> AssertionError: ValueError('Invalid Seed transition: SeedState.CANDIDATE → SeedState.LOCKED') !~ LOCK_PENDING
```

Note the second receipt: the mutation was caught **by the state machine as well as the guard** — `transition_to` independently rejects `CANDIDATE → LOCKED`. There is defence in depth here, and the suite catches both layers.

**`Spreader-tool` is the fleet's control group.** It is the same shape as the repos in §1–§4 — a zero-dependency agent tool with a real test suite — but its suite goes **RED** when you break it. Restore-and-recheck was performed on both mutations (`git checkout --`, md5 `536b44e8dfbc9e07028ac7e730d946b5` and `6db21cf6e6aa694da2dc6de0efe7e1d2` verified against the pre-mutation digests, 337/337 GREEN again).

Minor: `.coverage` and `examples/__pycache__/*.pyc` are tracked.

---

## 7. What the fleet-wide pattern actually is

Four repositories, four independent languages of the same mistake:

| repo | the claim | the truth | could CI see it? |
|---|---|---|---|
| `cache-layer-optimizer` | CI green, 44 Python tests, 82 Rust tests | wheel ships **0** Python modules; crate exits 101 | **no** — `\|\| true` ×2 |
| `Equipment-Memory-Hierarchy` | 34/34 green | skill ladder dead; confidence NaN | **no** — suite green before *and* after the fix |
| `Equipment-Self-Improvement` | 23/23 green | test file has 42 type errors; 2 detectors unfailable | **no** — green with both detectors disabled |
| `Baton` | 6 green CI runs | `pytest` exits non-zero on a missing import | **no** — `python -m pytest \|\| true` |

**And the one repo that does it right — `Spreader-tool`, 337 tests, two mutation-verified REDs — was found by a prior scout and is the only one in this report that would survive an adversarial reader.**

The structural insight is not that the fleet writes bad code. `cache-layer-optimizer`'s Python is 44/44 green on the real API; `Equipment-Memory-Hierarchy` is 4,758 lines of competent TypeScript; `Baton` is a real tool. **The fleet's failure is that its gates are configured to succeed.** `|| true` in a CI file, `Array.isArray()` in place of an assertion, a `vitest` run with no typecheck, a `tsc` build that has been red for six months — each is individually a small thing, and together they convert "the code is broken" into "the badge is green", which is the only signal most of these repos will ever get.

`fleet-build` exists, works, 82/82, and does exactly the job of noticing. It has never been pointed at the fleet.

---

## Method, verification, and honesty notes

- **Census:** paged to exhaustion with `sort=full_name&direction=asc`; asserted `unique_by(.full_name) == rows_returned`; **54 pages, 5,308 repos, 0 duplicates.** Forks filtered **after** the census (822 of 5,308).
- **Ranking:** real trees via `git/trees/{branch}?recursive=1` for all 2,786 never-examined own repos; ranked on code bytes by extension minus vendored paths. API `size` used only as a prefilter.
- **Toolchain:** Rust installed into `/tmp` (`HOME`/`CARGO_HOME`/`RUSTUP_HOME` off the NAS mount) so `cargo check`/`cargo test` could actually be executed. Python suites run in clean clones against a purpose-built pytest-compatible shim (fixtures, class-scoped and module-scoped, generator fixtures, `setup_method`, `unittest.TestCase.setUp`, `parametrize`, `capsys`, `raises`, `approx`).
- **Mutation:** every gate reported on was mutated in a **clone**, then restored with `git checkout --` and the restored file's md5 re-verified against the pre-mutation digest — no file was restored from a self-made backup.
- **Not claimed:** no cargo execution is claimed for any repo where cargo was not run. `cache-layer-optimizer`'s Rust suite was **never executed** (it cannot compile in isolation); the claim there is about what CI *would* do, proven by the exit code of `cargo check`.
- **Prior work is credited, not re-reported.** `Spreader-tool` (2026-10-02) and `Baton` (2026-10-10) were examined before; `Equipment-Memory-Hierarchy` and `Equipment-Self-Improvement` had their vendored mass reported on 2026-10-07. Only the new parts are claimed above.
- **Not a finding:** the committed `node_modules` in the two `Equipment-*` repos is known and is counted here only as the substrate for the arm64-binding defect.
