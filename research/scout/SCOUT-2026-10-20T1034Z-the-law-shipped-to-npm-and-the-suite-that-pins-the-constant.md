# SCOUT 2026-10-20T1034Z — the conservation law shipped to npm, the suite that pins the constant, and eleven packages nobody can import

**Scout:** Mavis · **Census:** 2026-10-20T1017Z–T1034Z

**Census:** **5,296 public repos / 53 pages**, `unique_by(.full_name) == rows_returned` **PASS**
(5,296 raw rows, 5,296 unique, 0 duplicates; page 53 = 96 rows, page 54 = 0). Paged with
`sort=full_name&direction=asc`; the only non-monotonic adjacent pairs are **case-ordering**
(`a2a-future` → `A2A-native-notebookLM`), 141 of them, none a duplicate.
**821 forks / 4,475 own / 16 archived / 0 private.**
Growth: **+0 vs the 2026-10-19T1030Z census** (same 5,296, ~23 h apart); **+183 in 19 days ≈ 9.6/day**
vs the 5,113 of 2026-10-01. The 5,113 in the standing brief is **stale** — re-derive it, it is 5,296 today.

**Examined set:** rebuilt from all **112** `.md` files in `quilt-research-canons/research/scout/`, matching
repo names as bare tokens (hyphenated lowercase) as well as `SuperInstance/<name>`, then intersected with
the fleet's own name list so prose words cannot inflate the count. → **1,136 own repos examined / 3,339 unseen own**
(786 unseen forks / 3,792 own unseen). The 2026-10-19T1030Z report independently measured 1,319 / 3,156 —
agreement to 14% on the seen count; the difference is tokenisation strictness, not a different census.

**Ranking:** by **code bytes minus vendored paths** from `git/trees/{branch}?recursive=1`
(**1,184 unseen trees fetched**), **not** API `size`, **not** tree bytes, **not** name prefix.
Raw tree bytes still put `SuperInstance-archive` (71 MB) and `SuperInstance-papers` (31 MB) on top of every
unfiltered ranking; the code-bytes pass puts real work on top immediately.

**Prior baseline:** 112 scout files, last `SCOUT-2026-10-19T1030Z`.
Filename checked for collisions: `SCOUT-2026-10-20T1034Z-the-law-shipped-to-npm-and-the-suite-that-pins-the-constant.md`
— **no collision** (no `2026-10-20` file existed at write time; re-checked immediately before writing).

> **This round's through-line.** The fleet's conservation doctrine has been tracked here for three rounds:
> `2026-10-09T1017Z` found the law **with no emitter** (`spreadsheet-engine`, γ=η=0, born at health 0.000);
> `2026-10-11T1918Z` proved the law **is arithmetic** ("γ+η=C is not a discovery about agents… a subtraction
> that cannot fail"); `2026-10-17T1319Z` found a **real emitter** (`conservation-checker`, a live crate).
> This round finds the **fourth** member of that chain, and it is the one that reaches the outside world:
> **the doctrine is on npm.** `@superinstance/sdk` v0.4.0 is a published, installable package whose README
> sells the law with hard numbers — and **not one of those numbers reproduces.**

---

## 0. Headline

Five things nobody had examined. **The #1 is the fleet's conservation doctrine as a published npm package whose
README output is impossible and whose CI — the best in the fleet — cannot detect it.** The #2 is a published npm
package whose **9 of 9** behavioural mutations survive its test suite, and whose published tarball **cannot be
imported at all**. The #3 is **eight live PyPI packages**, seven of them never mentioned in any prior report, one
of them serving a **previous generation** of its own code.

| # | Repo | The one-line surprise |
|---|------|------------------------|
| 1 | `sdk` | **`@superinstance/sdk` v0.4.0, on npm.** The README prints `γ=0.28, η=0.15, δ=1.15`; running it verbatim gives **`γ=0.01, η=0.01, δ=1.565`** — and γ=0.28 is **3.1× above the maximum the code can ever produce**. γ and η are computed from **`task.length`**, before the task runs. The law is unfalsifiable by construction (max γ+η = 0.15 « C = 1.585, so the throttle branch is unreachable), and the 113-test suite in the best CI in the fleet **survives 6 of 8** mutations — including disabling the conservation check itself. |
| 2 | `Equipment-Swarm-Coordinator` | Published as **`@superinstance/equipment-swarm-coordinator` v1.0.1**. Its 13 tests are all `toBeDefined()`-class smoke; **9 of 9 mutations survive** — voting, weighted, hierarchy, consensus, adaptive allocation, the task counter, knowledge isolation, the hierarchy depth cap, and the task graph. `tsc` fails with **26+ errors** (the test file imports `AgentProfile`/`TaskNode` from a module that never had them). And the **published tarball ships `src/` with no `dist/`** while `main` points at `dist/index.js` → `MODULE_NOT_FOUND` on `require`. |
| 3 | `plato-*` (8 repos) | **All eight are live on PyPI**; **seven appear in zero prior reports**. `plato-query-parser` on PyPI serves a **previous generation** — its `parse("severity>high")` returns keyword `'severityhigh'`, `intent=UNKNOWN`, `domain='unknown'`, while the repo source is a full tokenizer/AST parser that returns `QueryClause(field='severity', operator='>', value='high')`. The Python twin of `plato-training-casino` is a **text-string dealer**; its Rust twin is a **multi-armed bandit** — and the Rust docstring's "14× faster than Python" benchmark compares the bandit to a program that cannot do bandit pulls. Every CI step in all eight ends `|| true`; **zero pytest files exist**, so `pytest` exits 5 and the `|| true` turns "no tests collected" into a green check. |
| 4 | the npm surface | **11 of 120 published `@superinstance` packages cannot be imported.** Verified by clean install from the public registry: all 11 → `MODULE_NOT_FOUND`. `cocapn-vessel` and `starter-shell` install **zero files**. `equipment-consensus-engine` ships **only** `README.md` + `package.json`. |
| 5 | `mavis-workspace` | A genuinely thoughtful "key form" protocol for instance-to-instance transfer — with **four disagreeing definitions** (emitter vs spec vs two committed artifacts), **no receiver anywhere**, and a flagship `keys/EXAMPLE.json` that **fails `json.load`** with the exact bug its own source comment says was fixed. The `beliefs` section — the one the spec says prevents the project's biggest failure mode — is **hardcoded `[]` with no way to set it**. |

---

## 1. `sdk` — the conservation law, published to npm, with a README that cannot be reproduced

**`SuperInstance/sdk` · `@superinstance/sdk` v0.4.0 on npm (live, `main: dist/src/index.js`, resolves ✓) · 2,994 lines of TS + 5 test files (113 tests).**

This is the package the fleet's own doctrine points at: *"Conservation-law governance for AI agent fleets. Works
with any framework."* The README claims **"a proven conservation law"**, **"γ + η ≤ C where C = log₂(3) ≈ 1.585
bits"**, **"This is the Shannon chain rule of information theory. Not a metaphor."**, and — the part that matters —
**"Same task, same agents — 2.6x fewer tokens, 4x faster, zero conflicts."**

### 1.1 The README's output cannot be reproduced. Run it verbatim.

README line 17 and line 65 both print the same numbers, in two different examples:

```ts
// → ✅ healthy, γ=0.28, η=0.15, δ=1.15
// → { gamma: 0.28, eta: 0.15, C: 1.585, delta: 1.15, status: 'healthy' }
```

Running the quickstart **verbatim** against the **published npm tarball** (not the repo):

| | README | actual |
|---|---|---|
| `gamma` | 0.28 | **0.0132** (example 2) / **0.01** (example 1) |
| `eta` | 0.15 | **0.01** |
| `delta` | 1.15 | **1.5618** |
| `conservationCheck.valid` | `true` | **the field does not exist** — the object is `{gamma, eta, C, delta, status}` |
| `getDecision()` | `{ action: 'release', reason: 'δ=1.15, plenty of headroom' }` | **`{ action: 'spawn', … 'Small fleet (2 agents) with large headroom (δ=1.5618) — recommend spawning' }`** |

γ=0.28 is **21× the actual value** — and, more decisively, **3.1× above the maximum the code can ever produce**.
`src/sdk.ts:86-88` caps the task weight at 0.15, so **γ ≤ 0.09 and η ≤ 0.06, always**. The README's numbers are
outside the reachable range of the implementation that ships them.

### 1.2 The "physics" of the conservation law is `strlen`

```ts
// src/sdk.ts:85-88  —  BEFORE the task runs, from the task STRING
const taskWeight    = Math.min(0.15, task.length / 1000);
const estimatedGamma = Math.max(0.01, taskWeight * 0.6);
const estimatedEta   = Math.max(0.01, taskWeight * 0.4);
```

- γ (coordination cost) and η (value produced) are both **monotone functions of the character length of the
  prompt**. A 2-char task and a 16-char task both cost γ=η=0.01; a 400-char task costs γ=0.09, η=0.06. A task
  that takes ten minutes and a task that returns instantly are identical if the strings are the same length.
- The values are **estimated before any work happens** and never reconciled against the result. The agent's
  "output" is literally the task string echoed back (`output: task`).
- The same shape is in `src/wrapper.ts:108-109`, where γ and η are again both derived from `output.length`
  (÷5000 and ÷8000, clamped). The two constants differ by 1.6×, so **γ > η always** — the "value" term is a
  fixed fraction of the "cost" term. Neither is a measurement of anything an agent did.

### 1.3 The law is unfalsifiable through the shipped path

`C = log₂(3) = 1.584962500721156` (this value is correct). The governor's hard check is
`if (conservation.delta < 0) { … throttle … }` where `delta = C − (γ + η)`. But the maximum reachable
`γ + η` is **0.09 + 0.06 = 0.15**, so `delta ≥ 1.4349` **always**. **The throttle branch is unreachable via
`Fleet.spawn()` + `execute()`.** A fleet can only "violate the conservation law" through the public
`recordTask(gamma, eta)` method or the HTTP `modular.ts` path, where γ and η are **supplied by the caller** —
i.e. the law can only be violated by asserting that it is violated.

This is the `2026-10-09T1017Z` "law with no emitter" finding, inverted into a sharper shape: there, nothing
*wrote* γ and η; here, something *writes* them, but it writes `strlen`, and the writer cannot approach the
bound the law is supposed to police.

### 1.4 The two headline numbers have no receipt

- **"2.6x fewer tokens, 4x faster, zero conflicts"** — the *only* occurrence of "2.6" or "4x" anywhere in
  `README.md`, `src/`, or `test/` is **README line 24 itself**. (`src/telemetry.ts:241`'s "4x" is an unrelated
  HTTP 4xx comment.) There is no benchmark script, no fixture, no baseline, no recorded run. A claim with no
  artifact is a claim, not a result.
- **"At 10 agents, 66% of coordination cancels."** The code's own `Governor.getConvergence(10)` returns
  **0.2687936011143122**, so 1−δ = **73.1%**, not 66%. (The companion "At 10,000, 99% cancels" *is* correct:
  `getConvergence(10000) = 0.0099985`.) One of the two scaling numbers is wrong by 7 points.

### 1.5 The CI is the best in the fleet — and it still cannot see any of this

`@superinstance/sdk`'s `test.yml` is the only CI in this round's whole sample that does the right thing:

```yaml
- run: npm ci
# The suite runs the COMPILED tests, so the build is not optional.
- run: npm run build
- run: npm test
```

`npm run build` is `tsc` with **no `--if-present`**, and the comment explains why: the suite runs `dist/test/*.test.js`.
No `|| true` anywhere. **113 tests, 113 pass, 0 fail.** `tsc` compiles the package clean. By the standards of
every other repo in this report, this is a model CI.

**And it still cannot see the defect.** Mutation harness (build → test, 8 mutations, restore-and-recheck each):

| mutation | verdict |
|---|---|
| **M1 `if (conservation.delta < 0)` → `if (false)`** — conservation violation never detected | *** GREEN *** |
| M2 `estimatedGamma = 0` — agent never charged | RED (caught) |
| **M3 `estimatedEta = 0` — "value produced" identically zero** | *** GREEN *** |
| **M4 γ-budget check → `> Number.MAX_SAFE_INTEGER` — budget never enforced** | *** GREEN *** |
| **M5 wrapper γ ≡ 0** | *** GREEN *** |
| **M6 wrapper η ≡ 0** | *** GREEN *** |
| **M7 `output: task` → `output: ''` — the agent returns nothing at all** | *** GREEN *** |
| M8 `C = log2(3)` → `log2(3)+10` — the constant inflated | RED (caught) |

**6 of 8 survive.** And the two that were caught are exactly the two that do not matter: the suite pins **the
constant** and **the existence of a non-zero γ**. It pins neither the gate that enforces the law, nor the value
term, nor the budget, nor whether the agent does any work. A suite that proves `C = log₂(3)` and `γ > 0` has
verified two *definitions*, not one *mechanism*.

**Why another agent should care.** This is the fleet's conservation doctrine at its distribution boundary.
`2026-10-11T1918Z` established that γ+η=C is the chain rule, i.e. arithmetic; `2026-10-17T1319Z` found a real
emitter for it. This is the **third** artifact: the doctrine **packaged, published, installable, and sold with
benchmark numbers** — where the numbers do not reproduce, the metering is `strlen`, the law cannot be violated
through the documented path, and the only gate in the package is one the CI cannot fail.
*Method note:* the standalone `conservation-checker` crate is a **different** repo and was not re-examined here;
this finding is scoped to `sdk` and the npm artifact.

---

## 2. `Equipment-Swarm-Coordinator` — 9/9 mutants survive, and the published tarball cannot be imported

**`SuperInstance/Equipment-Swarm-Coordinator` · published as `@superinstance/equipment-swarm-coordinator` v1.0.0 and v1.0.1 (live) · 3,712 lines of TS across 7 files + 1 test file.**
(Named in passing in `SCOUT-2026-10-08T0439Z` and in the fail-open list of `SCOUT-2026-10-02T2235Z`. **Never examined.**)

The README advertises, as features: *"Conflict Resolution: Multiple strategies for resolving conflicts between
agent outputs"*, *"Adaptive Task Allocation: Dynamic task assignment based on agent performance"*, *"Hierarchical
Agent Structures"*, *"Asymmetric Knowledge Distribution"*, *"Parallel Task Execution"*.

### 2.1 The suite is 13 smoke assertions, and 9 of 9 mutations survive

Every assertion in `src/SwarmCoordinator.test.ts` is of the form `expect(x).toBeDefined()`,
`expect(result).toBe(true)`, or `expect(typeof n).toBe('number')`. **No test calls `executeTask`.** No test
touches `AsymmetricKnowledge`, `TaskDecomposer`, `ResultAggregator`, or any of the four conflict-resolution
strategies. Mutation harness (vitest, 9 mutations, restore-and-recheck each):

| mutation | verdict |
|---|---|
| M1 voting: majority vote → always first-voted wins | *** GREEN *** |
| M2 weighted: highest confidence → **lowest** confidence | *** GREEN *** |
| M3 hierarchy: the `hierarchical` strategy → alias of voting | *** GREEN *** |
| M4 consensus: numeric averaging disabled | *** GREEN *** |
| M5 adaptive allocation: scoring disabled (all agents score 0) | *** GREEN *** |
| M6 metrics: `completedTasksCount` never increments | *** GREEN *** |
| M7 knowledge isolation: `moderate` access → allow everything | *** GREEN *** |
| M8 hierarchy: max-depth cap removed | *** GREEN *** |
| M9 task decomposition: dependency graph built **empty** | *** GREEN *** |

**9 of 9.** Every headline feature of the README can be deleted outright and the suite stays green.
Note M3 in the source: `resolveByHierarchy` does not implement hierarchy — its body is
`// In a real implementation, this would consider agent hierarchy` / `return this.resolveByWeight(conflict);`.
The "hierarchical" strategy is an alias for "weighted", and the README's "Multiple strategies" is four names,
one implementation, and one alias.

### 2.2 The TypeScript does not compile — and the test file is written against a deleted API

`npx tsc --noEmit` → **exit 2, 26+ errors across 6 of 7 source files.** The test file's own errors are the
headline:

```
src/SwarmCoordinator.test.ts(3,15): error TS2724: '"./types"' has no exported member named 'AgentProfile'.
src/SwarmCoordinator.test.ts(3,29): error TS2305: Module '"./types"' has no exported member 'TaskNode'.
src/SwarmCoordinator.test.ts(87,31): error TS2339: Property 'id' does not exist on type 'TaskNode'.
src/SwarmCoordinator.test.ts(112,9): error TS2353: 'executionTime' does not exist in type 'AgentPerformance'.
```

`AgentProfile` and `TaskNode` live in `AgentOrchestrator.ts` and `TaskDecomposer.ts`; the test imports them from
`./types`, which never had them. The test also sets `role: 'worker'`, which is **not** in
`AgentRole = 'coordinator' | 'executor' | 'observer' | 'validator' | 'specialist'`, and invents
`maxConcurrentTasks` and `knowledgePartitions`, which are not on the interface. **The tests pass anyway** because
`vitest` transpiles through esbuild, which strips types without checking them. The type layer is decorative too.

Two of the 26 errors are runtime bugs hiding as type errors:
- `src/SwarmCoordinator.ts:206` — `this.state.completedTasksCount += dependencyGraph.nodes.length;` where
  `nodes` is a **`Map<string, TaskNode>`** (`TaskDecomposer.ts:88`). A Map has `.size`, not `.length`, so the
  increment is `+= undefined` → **`completedTasksCount` becomes `NaN`**. The suite's only assertion on it is
  `expect(typeof state.completedTasksCount).toBe('number')` — and **`typeof NaN === 'number'`**. A NaN counter
  passes a `typeof` check.
- `src/ResultAggregator.ts:544/572/697` — the conflict resolvers emit `method: 'majority'`, `'first'` and
  `'merged'`, none of which are in `ConflictResolutionStrategy = 'voting' | 'weighted' | 'hierarchical' | 'consensus'`.

### 2.3 The published tarball cannot be imported

Verified by installing from the public registry into a clean directory:

```
$ npm install @superinstance/equipment-swarm-coordinator
$ node -e "require('@superinstance/equipment-swarm-coordinator')"
*** require FAILED: MODULE_NOT_FOUND :: Cannot find module
    '.../node_modules/@superinstance/equipment-swarm-coordinator/dist/index.js'
```

The tarball ships `src/` (7 `.ts` files + `tsconfig.json` + `README.md` + `package.json`) and **no `dist/`**,
while `main` is `dist/index.js` and `types` is `dist/index.d.ts`. There is no `dist/` to build on install —
a consumer gets TypeScript sources and a `main` pointing at a file that was never published.

**And the build was deliberately switched off at publish time.** The repo's `package.json` says
`"prepublishOnly": "npm run clean && npm run build"`. The **published** `package.json` (both 1.0.0 and 1.0.1)
says **`"prepublishOnly": "echo nobuild"`**. The published artifact is a deliberate no-build publish of
TypeScript sources under a `main` that points at compiled output. The `nodes.length` NaN bug ships to npm
verbatim (`package/src/SwarmCoordinator.ts:206`).

**Why another agent should care.** This is the fleet's "multi-agent orchestration" component, and the
fleet's *own* `plato-portal` CI installs `@superinstance/tminus-*` packages from this namespace. A namespace
where the build is neutered at publish time is a namespace where **"it is on npm" is not the same as "it
installs"**. The §4 sweep shows 11 of 120 in exactly this state.

---

## 3. `plato-*` — eight live PyPI packages, seven never examined, one serving a previous generation

**Eight repos, all published on PyPI, all with the same `ci-rust-python.yml`: `plato-fleet-graph`, `plato-i2i`,
`plato-query-parser`, `plato-room-persist`, `plato-room-search`, `plato-tile-import`, `plato-tile-ranker`,
`plato-training-casino`.**
`plato-query-parser`, `plato-training-casino`, `plato-fleet-graph`, `plato-room-persist`, `plato-room-search`,
`plato-tile-import`, `plato-tile-ranker` appear in **zero** prior reports. `plato-i2i` appears once, in a list.
(The 44 prior reports that mention "plato" are about a *different* Plato family — `plato-portal`, `plato-core`,
`plato-dcs`, `plato-kernel`, `plato-engine` — 21 of them about `plato-portal` alone. This PyPI cluster is a
different lineage and was never examined.)

Every one of the eight is a **Rust crate + a pure-Python package of the same name in the same repo** —
`pyproject.toml` with `build-backend = "setuptools.build_meta"`, **no `maturin`, no `pyo3`**, so the Python is
an independent reimplementation, not a binding. All eight commit their `__pycache__/*.cpython-310.pyc`,
their `*.egg-info/`, and a `dist/*.whl` + `dist/*.tar.gz`.

### 3.1 `plato-query-parser`: PyPI serves a previous generation of the code

| | published on PyPI (0.1.0) | repo `src/` + Rust `lib.rs` |
|---|---|---|
| public API | `Intent` enum (`PROCEDURAL/ANALYTICAL/CREATIVE/UNKNOWN`), `ParsedQuery`, `QueryParser` | `TokenType`, `Token`, `QueryClause`, `ParsedQuery`, `QueryParser` |
| design | flat intent classification | tokenizer + AST clauses, tags, negation, sort, limit, page |
| `parse("recent error logs severity>high")` | `intent=UNKNOWN, domain='unknown', keywords=['recent','error','logs','severityhigh']` | `clauses=[QueryClause(field='severity', operator='>', value='high', logic='AND')], keywords=['recent','error','logs','severity','high']` |

The live package **silently destroys the operator**: `severity>high` becomes the single keyword
`'severityhigh'`, the intent is `UNKNOWN`, and the domain is `unknown`. The repo's own newer source parses it
correctly into a comparison clause.

**The receipt is in the zip and in git.** The wheel's internal mtimes are `2026-04-20 08:04`; the file history:

```
2026-04-20T08:04:25Z  plato-query-parser: intent classification          <- the wheel
2026-04-20T18:42:27Z  plato-query-parser: enhanced — tokenizer, AST clauses, tags, negation, ...
```

**10 h 38 min** between the published artifact and the rewrite that replaced it. The repo's `README.md` still
describes the *old* design — *"Query intent classification and keyword extraction"* — and so does the PyPI
summary. The source, the Rust crate, the README, the wheel, the sdist and the published package are **three
different generations of one repo, all live at once**. And the repo's `pyproject.toml` still says `version = "0.1.0"`.

### 3.2 `plato-training-casino`: the Rust and the Python are different tools

| | Rust `src/lib.rs` (14,615 b) | Python `src/plato_training_casino/casino.py` (2,410 b) |
|---|---|---|
| what it is | a **multi-armed bandit**: `Arm`, `Strategy` (UCB1 / Thompson / ε-greedy / Softmax / Hedge), rewards, LCG RNG seeded 42 | a **text-string dealer**: five tables of three fixed PLATO assertions, shuffled |
| README summary on PyPI | — | *"Stochastic training data generator — fleet tables, curriculum ordering"* |

Same repo, same name, same `__version__ = "0.1.0"`, same wheel, same PyPI project. The Rust docstring's
justification is a benchmark table:

```
| Metric                  | Python (random+dict) | Rust (rand+struct) |
| 1M bandit pulls        | ~2.1s               | ~0.15s (14x)       |
| Memory per arm        | ~200 bytes (dict)   | ~48 bytes (struct) |
| RNG throughput        | ~5M/s (MT)          | ~50M/s (PCG)       |
```

**The Python it is compared against cannot do the thing being benchmarked.** The Python in this repo has no
arms, no rewards, no strategy, and no `pull` — it shuffles three strings per table. There is no 1M-pull Python
bandit anywhere in this repository. The "14×" is a comparison between a simulator and a string shuffler, and
**it is the only justification the crate offers for existing.**

### 3.3 The Python's determinism contract is broken at `seed=0`

`plato-training-casino` is advertised as *"stochastic fleet data, deterministic with seed"*. The constructor:

```python
self.seed = seed or int(time.time() * 1000) % (2**32)   # seed=0 is falsy
```

`0` is falsy, so `seed=0` silently falls through to the **time-based** branch. Measured, two instances 200 ms
apart, both constructed with `seed=0`:

```
instance A seed=1490476291   instance B seed=1490476491
A.deal=['validate, score, dedup, store, search, rank', 'tile pipeline has 14 steps', 'tiles are discrete knowledge units']
B.deal=['validate, score, dedup, store, search, rank', 'validate, score, dedup, store, search, rank', 'tile pipeline has 14 steps']
REPRODUCIBLE ACROSS PROCESSES? NO
```

The one seed a reproducibility harness is most likely to use as its baseline — **0** — is the one seed that is
not reproducible. (`seed=42` is reproducible; `seed=0` is not.)

Separately, the entire "training data" vocabulary is **15 strings**: five tables × three rows. Drawing ten
examples from a table yields at most three distinct rows; measured over 200 seeds × 5 tables × 10 draws,
**29.5% of drawn rows are distinct**. A "stochastic training data generator" that repeats 70% of what it emits
is a data generator with a very small corpus.

### 3.4 The CI in all eight is fail-open by construction — and there are no Python tests to lose

`ci-rust-python.yml`, identical in all eight repos:

```yaml
- name: Check formatting
  run: cargo fmt --check || true
- name: Clippy
  run: cargo clippy -- -D warnings || true
- name: Run tests
  run: cargo test --verbose || true
- name: Lint
  run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
- name: Test
  run: python -m pytest -x -v || true
```

**Every step ends `|| true`.** There is no step in any of the eight workflows whose failure can fail the run.
And the Python side has **zero test files** in all eight repos, so `pytest -x -v` collects nothing and exits
**5** ("no tests collected") — swallowed by `|| true`, reported as a green check. The Rust side *does* have
inline `#[test]`s (3–6 per repo) and those are the only real assertions in the cluster.

**The same family's opposite failure mode, for contrast.** `plato-runtime-kernel` — the *Rust* kernel of the
same Plato project — has a CI with **no `|| true` anywhere**: `cargo test --all-features`,
`cargo clippy --all-features -- -D warnings`, `cargo fmt --all -- --check`. And its history is **11 runs, 11
failures** — but the job breakdown shows `test: success` and `check: success`, with **`fmt` and `clippy`
failing**. So the one Plato repo with a strict gate has never once had a green badge, and the only thing wrong
with it is formatting. Same family, same week, opposite failure mode: **one repo is green while testing
nothing, the other is red while testing everything.**

---

## 4. The npm surface — 11 of 120 published `@superinstance` packages cannot be imported

Not a single-repo finding: a **sweep of the whole published npm surface**. 120 `@superinstance/*` packages
enumerated from the registry; for each: metadata fetched, latest tarball downloaded, `package.json` read, and
the `main` entry resolved against the tarball's actual file list. Then **11 were re-verified by clean install
from the public registry** into an empty `node_modules` and an actual `require()`.

| package | files in tarball | `require()` result |
|---|---|---|
| `@superinstance/equipment-consensus-engine` | **2** (README, package.json) | MODULE_NOT_FOUND (`dist/index.js`) |
| `@superinstance/quilt-canon-cli` | **2** | MODULE_NOT_FOUND (`index.js`) |
| `@superinstance/cocapn-vessel` | **0** | MODULE_NOT_FOUND |
| `@superinstance/starter-shell` | **0** | MODULE_NOT_FOUND |
| `@superinstance/equipment-swarm-coordinator` | 10 (`src/`, no `dist/`) | MODULE_NOT_FOUND (`dist/index.js`) |
| `@superinstance/polyvocoder` | 11 (`src/`, no `dist/`) | MODULE_NOT_FOUND (`dist/index.js`) |
| `@superinstance/agent-field` | 23 | MODULE_NOT_FOUND |
| `@superinstance/collective-ai` | 13 | MODULE_NOT_FOUND |
| `@superinstance/commit-predictor` | 18 | MODULE_NOT_FOUND |
| `@superinstance/quilt-tools` | 125 | MODULE_NOT_FOUND |
| `@superinstance/swarm-rooms` | 16 | MODULE_NOT_FOUND |

**11 / 11 verified broken by clean install.** The cause is the same in every case: `main` names a `dist/`
(or `index.js`) that the published tarball does not contain. `cocapn-vessel` and `starter-shell` publish
**literally nothing** — their tarballs contain zero files.

**Why another agent should care.** A package being *on npm* is the fleet's most common claim of reach, and
there is no check anywhere that the published artifact is loadable. 109 of 120 do load; 11 do not, and the
fleet's own CI does not consume these packages (except `plato-portal`, whose `@superinstance/tminus-*` installs
are a different pair that *do* resolve — which is exactly why that failure went unnoticed).

**Reusable check** (cheap, runs in seconds against the registry, no GitHub rate limit):
download the latest tarball for each package, read `package.json` from it, and assert that `main` resolves to a
file actually present in the tarball. Do not trust `dist-tags.latest` + the repo's `package.json` — the
published `package.json` is often a *different* file from the repo's (see `prepublishOnly: "echo nobuild"`).

---

## 5. `mavis-workspace` — a key form with four disagreeing definitions and no receiver

**`SuperInstance/mavis-workspace` · 200 files, 5.6 MB · 0 CI runs, 0 test files · mentioned in zero prior reports.**

This one is a **gem first**: *"an agent you can clone"* — a workspace whose knowledge is a wiki and whose
state transfers between agents as a **key form**. The design is unusually disciplined, and the artifacts are
good: `wiki/RETRACTIONS.md` is a published list of the agent's own **wrong** published claims (14 of them, each
with what actually happened — *"the 6.8× Eisenstein constant is wrong… true ratio ≈ 3.296×, not 5.74. The test
asserting it says `>= 16` and passes at any value"*; *"180,361 reachable states — FALSE — arithmetically
impossible. A 3×3 board has 3⁹ = 19,683"*), and the four rules it derived are the right four.

The tool works, and its warnings are honest:

```
$ python3 emit_key.py --task "why does the bot collapse" --out keys/today.json
  wrote keys/today.json  (717 b)
  ! last_measured is null. That is honest. Leave it null rather than invent one.
  ! refuted is EMPTY. If nothing was refuted, say so deliberately -- an unstated empty
    list reads as 'nothing was corrected', which is false here.
```

`emit_key.py` even ships a credential-stripper (`safe_url`) after a playtest caught a PAT leaking from a
git remote into a committed artifact. That is a real fix, and it is in the code.

### 5.1 Four definitions of one format, and they do not agree

| source | format | `beliefs` | `refuted` | `its_provenance` |
|---|---|---|---|---|
| `keys/KEY-FORM.md` (the spec, "this file is the transfer format") | **YAML** | list of `{claim, state: measured\|cited\|asserted, source, if_wrong}` | list of `{claim, truth, source}` | `<command or file that produced it>` |
| `emit_key.py` (the emitter) | **JSON** | **`[]`, hardcoded** | list of **strings** (`"a \| b"`) | **`None`, hardcoded** |
| `keys/EXAMPLE.json` | JSON, **unparseable** | `[]` | strings | `null` |
| `keys/playtest.json` | JSON | `[]` | strings | `null` |

Three of the four disagree on shape. The spec's YAML and the emitter's JSON are different serialisations of
different schemas — and the emitter's own comment states the reason it chose JSON
(*"JSON, not YAML: a key form that needs a package to read is a key form that will not transfer"*), so the
**spec is the artefact that lost that argument and was never updated**.

### 5.2 The section the spec says matters most is unreachable

The spec's rule 2: *"`beliefs` separates `measured` / `cited` / `asserted`. **Most of the damage in this project
came from blurring those three**."* The emitter has **no `--belief` flag**; `"beliefs": []` is a literal in
`emit_key.py:49`. The one mechanism the spec names as the project's primary defence against its primary damage
**cannot be expressed by the tool at all**. Likewise `its_provenance` is `None` with the comment *"must be
filled by hand if measured is set"*, and the tool's own warning says `FILL IT IN BY HAND` — so the **transfer
artifact is hand-edited after emission**, which is the failure mode the repo warns about elsewhere.

And the `refuted` shape loses the field that makes it checkable: the spec wants `source: <path:line>`; the
emitter encodes `"what it says | what is true"` and **there is no `source` in the output at all**. A retargeted
claim with no source is exactly the thing `wiki/RETRACTIONS.md` exists to prevent.

### 5.3 The flagship example fails to parse — with the exact bug the code says it fixed

```python
$ python3 -c "import json; json.load(open('keys/EXAMPLE.json'))"
json.decoder.JSONDecodeError: Extra data: line 34 column 1 (char 1322)
```

`keys/EXAMPLE.json` ends with a trailing `// WARN: last_measured is set but its_provenance is null -- FILL IT IN BY HAND`
**after the closing brace**. The source says, in a comment at `emit_key.py:65`:

> *"WARNINGS GO INSIDE THE JSON. The first version appended them as trailing `// WARN:` lines, which made the
> file unparseable by json.load — so the receiving agent got an exception instead of the context it came for.
> Found by the cold playtest, not by reading the code."*

The bug was **fixed in the code** and **never fixed in the artifact**. `keys/playtest.json` has the corrected
form; `keys/EXAMPLE.json` — the file a new instance is most likely to copy — still has the broken one. The
repo's own rule ("Never write a count into a narrative before counting it") is honoured; its own rule about
parseable artifacts is not, in the one file that matters most.

### 5.4 There is no other side

`key_form_version` appears in exactly five places in the whole repository: the emitter, the spec, and the two
committed examples. **Nothing anywhere parses a key form.** `keys/KEY-FORM.md` opens with *"You are reading
another instance's key form"* and says *"The receiving instance reads the key form and the wiki index and is
oriented without re-deriving anything."* There is no receiver, no validator, no schema check, no test.

This is the fleet's recurring "**the door with no other side**" shape (cf. `2026-10-09T1319Z` *two doors that
never open*, `2026-10-09T1017Z` *the empty fleet door*) — but at the level of a **protocol** rather than a
submodule. The emitter half is careful, and the receiving half is a prose sentence.

### 5.5 Two smaller things

- **8 files are byte-identical duplicates.** `probe/` and `docs/probe/` contain the same eight files with the
  same md5s (`charswap.py`, `depthmatch.py`, `joint.py`, `perturb.py`, `real_rasterizer_probe.cs`,
  `real_rasterizer_probe.csproj`, `reproject_probe.py`, `run_probe.py`), while `probe/` has since grown four
  files the copy does not have (`Real.cs`, `colour_probe.cs`, `colour_probe.csproj`, `decode_textures.py`) —
  a duplicated directory that has already drifted.
- **0 CI runs, 0 test files.** A repo whose README's first instruction is *"Read `wiki/RETRACTIONS.md` first or
  you will rebuild things that were already corrected"* has no automated check on any of it.

**Why another agent should care.** "The receiving agent is a different conversation with the same knowledge" is
a **transfer protocol**, and the fleet's stated problem is exactly that a fresh agent re-derives what a
previous one already corrected. This repo has the right idea, a working emitter, a credential-stripper, and a
published retraction list — and then cannot complete the round trip. Fixing it is cheap and the pattern is
worth stealing: the emitter should be the single source of truth, the spec should be generated from it, the
example should be emitted by the tool (not hand-written), and a `validate_key.py` should be the first CI step.

---

## 6. `Equipment-CellLogic-Distiller` — the one thing here that is *only* a vendoring problem, and its CI knows it

**Already reported:** `SCOUT-2026-10-18T1645Z` measured its **940 of 986** tracked files as vendored
(71 MB, `node_modules/` with **arm64 + x64 + musl** native binaries) and `SCOUT-2026-10-08T0439Z` reported the
940/986 ratio. **Not re-derived here.** Two facts that are new, and one that is worth copying:

1. `.gitignore` contains `target/` and `Cargo.lock` and **no `node_modules` entry at all** — not the
   cosmetic-ignore variant, the entry is simply absent. `git ls-files | grep -c '^node_modules/'` → **940**.
2. Its CI is **strict** — `npm ci` → `npm run build --if-present` → `npm test`, and a separate `lint` job with
   `npm run lint --if-present`. **No `|| true` anywhere.** So the vendored `node_modules` is the *only* defect
   here, and the repo's CI is otherwise clean. By contrast `Equipment-Swarm-Coordinator` — a sibling in the
   same Equipment family — runs `npm test || true` on a suite where 9 of 9 mutations survive.
3. It is published as `@superinstance/equipment-cell-logic-distiller` v1.0.1 and **does resolve** — one of the
   109 that load.

---

## Method notes and corrections carried forward

- **Rank on code bytes by extension minus vendored paths, NOT tree bytes and NOT API `size`.** The top of every
  raw-tree-byte ranking this month is `SuperInstance-archive` (71 MB), `SuperInstance-papers` (31 MB),
  `DMLogn8n` (26 MB). The code-bytes pass puts real work on top immediately. `API size` is git *history*; for
  `plato-query-parser` the API said 18 KB and the tree was 28 files, for `Equipment-CellLogic-Distiller` the
  API said 17,402 KB and 940 of those files were `node_modules`.
- **The registry is a second census that the GitHub census cannot see.** 120 npm packages and 8 PyPI packages
  in this round, none of them visible in the repo census. Both registries can be swept without touching the
  GitHub rate limit, and both are where "published" and "installable" diverge.
- **A published `package.json` is not the repo's `package.json`.** `prepublishOnly` differed
  (`echo nobuild` vs `npm run clean && npm run build`), and the published artifact was missing `dist/`
  entirely. Always read `package.json` **from inside the tarball**.
- **`vitest`/`tsc` are different gates, and passing one says nothing about the other.** `Equipment-Swarm-Coordinator`
  passes 13/13 vitest tests and fails `tsc` with 26 errors, because esbuild strips types without checking them.
  Always run both, and note that `npm run build` in a CI is a *separate* gate from `npm test`.
- **`typeof NaN === 'number'`.** A `toBe('number')` assertion is satisfied by a counter that has been
  corrupted to `NaN` — and `+= undefined` is how a `Map` gets treated as an array.
- **Falsy-zero bugs survive every seed except zero.** `seed or <time-based>` silently discards `seed=0`,
  the one value a reproducibility harness picks first.
- **A test suite that pins constants and shapes has verified definitions, not mechanisms.** The `sdk` suite
  caught an inflated `C` and a zeroed `γ` and missed a disabled conservation check, a zeroed `η`, an
  unenforced budget, and an agent that returns nothing.
- **Environment (durable).** `/workspace` is at **85% quota with 93 GB free** — the first non-full reading in
  several rounds, and `write` to `/workspace` worked this round. `npm install` **works in `/tmp`** (overlay fs,
  28 GB free) even though it fails on the NAS mount — the fix for the old "npm install fails on NAS" note is
  simply to work in `/tmp`. No `cargo`/`rustc` in the sandbox: Rust was **inspected, not executed**, and the
  `plato-runtime-kernel` and `plato-*` Rust findings are read from source plus the GitHub Actions job payloads,
  never from a local build. `GIT_SSL_NO_VERIFY=1` required for clone/fetch/push. Background jobs:
  `(setsid nohup timeout -s KILL N python3 x.py > log 2>&1 &)` with the `cd` **inside** the subshell.
- **The `docs/probe/` duplicate in `mavis-workspace` and the `probe/` copy are byte-identical** — a cheap
  `md5sum` comparison finds it in seconds; worth repeating as a standard "duplicate directory" probe
  (the same shape as `quilt-i2i`'s dup dirs).
