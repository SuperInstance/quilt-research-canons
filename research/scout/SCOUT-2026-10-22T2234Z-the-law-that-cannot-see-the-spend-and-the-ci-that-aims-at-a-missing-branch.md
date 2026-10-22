# SCOUT — 2026-10-22T2234Z — the law that cannot see the spend, the test module that does not compile, and the CI that aims at a branch that does not exist

**Round 130** · SuperInstance fleet scout · 6 findings, every one reproduced by execution where execution was possible.

---

## 0. Census and method

| | |
|---|---|
| Census | **5,306 repos / 54 pages**, `unique_by(.full_name) == rows_returned` → **PASS** (paged `sort=full_name&direction=asc`) |
| Split | own **4,485** · forks **821** · archived own **16** |
| Prior scout files | **132** in `research/scout/` (2.8 MB, all read) |
| Examined set | **1,347** own repos (context-matched: `owner/name` path form, backtick spans, name-followed-by-path, markdown link targets — with every "next round"/"carry forward" section carved out) |
| Unseen own | **3,138** |
| Tree-scanned for substance | **1,505** unseen own (`git/trees/{branch}?recursive=1`), ranked on **code bytes by extension minus vendored paths** — never API `size`, never tree bytes, never name prefix |
| Ranking headroom | 12 unseen own carry ≥ 30 KB of history; the 1,347 examined set already contains **every** own repo ≥ 30 KB except those 12 |

The account did **not** grow this round: 5,306 repos, identical to round 129. The 10-01 brief's "5,113 across 52 pages" is now **193 repos stale** — re-derived, not carried.

**The candidate pool is thin, and that is itself the finding.** 4,220 of 4,485 own repos have < 10 KB of git history — the "phantom repo" class from round 126. After 130 rounds the *substantive* unseen set is 12 repos. The gems below are drawn from a pool that had to be re-derived by tree-scanning 1,505 repos, not by reading a list.

---

## 1. `fleet-agent-core` — the fleet's best-verified crate, with one real behavioural bug its own suite cannot see

**What it is.** A single-binary fleet agent in Rust: one process, one event loop (`SENSE → CONSTRAINT CHECK → ORIENT → DECIDE → ACT → RECORD`), four phases (Commissioning / Operational / Stressed / Recovering), five actions (Hold / ChangeHeading / Refit / Prune / Broadcast). **Zero external dependencies** — `std` only.

**Verified green, and the suite is real.** `cargo test` in a clean clone:

```
test result: ok. 36 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s
```

CI: **5 runs, 5 successes** (`CI` workflow, `master` + `production-round4-*`).

**Mutation-verified 3/3** — the suite is not theatre:

| Mutation | Result |
|---|---|
| `check_constraints()` → always `true` | **4 tests FAILED** (`test_constraint_fails`, `test_constraint_uses_max_value`, `test_build_record_tracks_refits`, `test_build_record_refits_increment_version`) |
| `has_stress` → always `false` | **1 test FAILED** (`test_build_record_tracks_prunes`) |
| `sense()` filter disabled | **3 tests FAILED** (`test_sense_empty_when_no_overlap`, `test_sense_relevant_observations`, `test_tick_filters_irrelevant_observations_from_phase`) |
| restore (md5 `495d24274382d8a471a25c09906dcf66`) | **36 passed, 0 failed** |

**Why another agent should care.** This is the crate to copy. Zero deps means it compiles anywhere; a mutation-sensitive suite means the badge means something; and the commit log shows the author auditing their own work: *"Production hardening: fix collision-sensing bug, dead BuildRecord fields, add real CI (#1)"*. The last test in the file, `probe_collision_course_no_overlap_is_relevant`, carries a comment that **explicitly names a sibling test that "passes unconditionally"** and fixes it. That is the rarest thing in this fleet.

### 🔴 DEFECT A — one collision-course observation latches the agent into Stressed forever

`tick()` accumulates every sensed observation into `self.observations` and **never clears it**; `orient()`/`phase()` then evaluate `has_stress` over that entire history:

```rust
self.observations.extend(sensed_refs.clone());          // never cleared
...
let has_stress = self.observations.iter().any(|o| o.bearing_rate < 0.01);
```

So the condition is **latched**, not evaluated per-tick. The README's phase table reads like a predicate ("Stressed | bearing_rate < 0.01 (collision course) | Evasive heading + Broadcast"), but it is a one-way door.

Measured, with a probe built against the crate's own public API:

```
phase counts: {Stressed: 13, Operational: 6, Commissioning: 49, Recovering: 32}
ticks>55 in Operational: 0        <-- never returns
ticks>55 in Stressed:   12
ticks>55 in Recovering: 32
```

A single hostile observation at tick 55 ⇒ **0 Operational ticks in the remaining 45**. In a real fleet this means one agent broadcasts a distress signal on every tick indefinitely.

### 🔴 DEFECT B — state energy only ever decays, so every agent ends as a permanent no-op

`tick_state()` multiplies each state value by `0.99` and floors it at 0. Nothing ever recharges. `State::energy()` is `sum(abs(values))`, and `Recovering` is entered when `energy < 0.5`. So:

```
energy after 200 idle ticks (fresh agent): phase=Recovering
```

`0.99^69 = 0.4998` — a fresh agent crosses the threshold at tick 69 and **never returns**. The crate's own 100-tick demonstration, run from `main.rs`, ends:

```
  Phase distribution:
    Commissioning   : 50
    Operational     : 5
    Stressed        : 14
    Recovering      : 31
```

**45 of 100 ticks are non-Operational, and the last 31 are a permanent Hold.** A "100-tick demonstration" of a self-optimising agent that spends a third of its life doing nothing is not demonstrating the agent. The demo also reports `Build refits: 0` / `Build prunes: 0` — the Refit and Prune paths are never exercised either.

### 🟠 DEFECT C — the event log drops every action after the first

`tick()` records `actions.first()` into the `LogEntry`. The `Stressed` branch emits two actions (`ChangeHeading` **then** `Broadcast`), so the fleet-wide `Broadcast` is **never written to the log**. The `BuildRecord` sees both (it iterates all actions), but the tick log — the thing you'd read to reconstruct what the agent did — silently loses half of them.

### 🟡 Minor

- README says *"cargo test # 35 tests"*; there are **36**. The extra one is the `probe_` regression guard, added after the README was written. Stale by exactly one.
- `orient()` and `phase()` are **byte-identical duplicated bodies** (`orient` takes `&mut self`, `phase` takes `&self`). The `tick()` path uses `orient()`; `phase()` is the public accessor. They agree today by construction, not by construction of a single source of truth. The `tick()` comment claims *"SENSE — reuse the public filter so tick and sense cannot diverge"* — the author was careful about one duplication and missed another.

---

## 2. `superinstance-harness` — the γ + η = C crate whose test module cannot compile, whose law cannot see the spend, and whose "core engine" has no callers

**What it is.** A self-optimising allocator that splits a capacity budget `C` between exploitation (γ) and exploration (η), using ternary signals, EWMA quality tracking and regret accumulation. Claims to be *"the core optimization engine of SuperInstance"*, with *"the Cocapn delegat[ing] fleet-wide allocation decisions to this harness"*.

### 🔴 DEFECT A — the test module has a hard syntax error; the 13 tests can never run

At **`src/lib.rs:516`** (HEAD `0778768`, default branch) an orphaned test body sits with no `#[test] fn …` header:

```
 513|         assert_eq!(signal, TernarySignal::Decrease, "Low quality + high gamma should decrease exploitation");
 514|         assert!(h.verify_conservation());
 515|     }
 516|         let mut h = HarnessState::new();      <-- no #[test] fn header
 517|
 518|         // Simulate cycles with low exploration yield → should converge to more exploitation
```

`cargo build` succeeds (the module is `#[cfg(test)]`). `cargo test` **fails to compile** — `error: unexpected closing delimiter`. The 13 `#[test]`s in the crate have never run and *cannot* run. There is also **no `.github/workflows/` directory** and **0 Actions runs**, so nothing ever surfaced the breakage. This is strictly stronger than round 129's "no CI" class: the suite is not unreachable, it is unparseable.

### 🔴 DEFECT B — the conservation law constrains the *plan* and never looks at the *spend*

`CycleRecord` carries `gamma_spent` and `eta_spent`; `total_spent()` sums them. `enforce_conservation()` re-normalises `gamma`/`eta` to sum to `C`; `verify_conservation()` asserts `|γ + η − C| < 1e-9`.

**`total_spent()` is never compared to `capacity` anywhere in the crate.** Grep of every use:

```
83:        let spent = self.total_spent();              // productivity divisor
232:        let hindsight_value = if record.total_spent() > 0.0 {
234:            h_productivity / record.total_spent()
```

Runtime probe against the crate's own arithmetic (compiled with `rustc 1.99.1`; only the serde derives were stripped, because crates.io is unreachable from this sandbox — the numeric core is untouched):

```
=== PROBE 2: the law constrains the PLAN, never the SPEND ===
  C = 1, gamma+eta = 1
  a cycle spent 18.0 against a capacity of 1.0
  verify_conservation() = true  <-- the law still holds
  history[1].total_spent() = 18  (never compared to capacity)
```

**A harness whose cycle consumed 18× its capacity still reports the conservation law holds.** The law is a re-normalisation identity on the plan; it is unfalsifiable by the thing it purports to conserve. (Round 129 found the inverse of this — `spreadsheet-engine`'s γ+η=C with *no emitter*. Here there *is* an emitter, and the law still cannot see the world.)

### 🔴 DEFECT C — `verify_conservation()` is vacuously true for a harness with no capacity

```
=== PROBE 1: zero capacity still 'satisfies' the conservation law ===
  capacity = 0  gamma = 0  eta = 0
  verify_conservation() = true
  gamma_fraction() = 0  eta_fraction() = 0
```

`with_capacity(0.0)` builds a harness with `C = 0, γ = 0, η = 0`, and `|0 + 0 − 0| < 1e-9` is true. The crate's own test `test_zero_capacity_recovery` asserts `capacity == DEFAULT_CAPACITY` — but that only holds *after* `enforce_conservation()` runs, and that test cannot run (Defect A).

### 🔴 DEFECT D — the documented η cap is violated by the code, because the clamp runs before the normalisation

The README states the bound as *"η_cap = 0.6 (never spend more than 60% on exploration)"*. `apply_signal` does:

```rust
self.eta = self.eta.clamp(ETA_FLOOR * self.capacity, ETA_CAP * self.capacity);
self.enforce_conservation();     // scale = C/(γ+η) > 1  → scales η back UP past the cap
```

The clamp is applied **before** the re-normalisation, and the normalisation multiplies both terms by `C/(γ+η)`, which is `> 1` whenever the step reduced the total. So the clamp is undone.

```
=== PROBE 3: eta cap violated because the clamp runs BEFORE the normalisation ===
  after 14 Decrease signals: eta_fraction = 0.615164  (documented cap ETA_CAP = 0.6)
  gamma_fraction = 0.384836   gamma+eta = 1.000000  (C = 1)
```

This is reachable, not exotic: `compute_signal` returns `Decrease` whenever `roi > 0.6 && quality > 0.6` — i.e. **exploration keeps paying off**. A workload that keeps finding value in exploration walks η straight through the documented ceiling.

### 🔴 DEFECT E — "regret" is a rescaled copy of productivity, and it is inverted

```rust
let actual_value    = record.productivity();                       // q·qty/spent
let h_productivity  = record.output_quality * record.output_quantity * 1.1;
let hindsight_value = h_productivity / record.total_spent();       // == 1.1 × actual_value, ALWAYS
self.performance.regret += (hindsight_value - actual_value).max(0.0);
```

`hindsight_value` is **identically `1.1 × actual_value`**, so `regret += 0.1 × productivity` every cycle, regardless of allocation quality. The only quantity that depended on allocation quality —

```rust
let _hindsight_gamma = if record.exploration_yield > 0.5 { … } else { … };
```

— is assigned to `_` and **thrown away**. Measured:

```
=== PROBE 4: 'regret' is a rescaled copy of productivity ===
  productivity of last cycle = 9.0000
  accumulated regret        = 4.5000        (= 0.1 × sum of all productivities, exactly)
  regret with GOOD output (q=0.9): 4.5000
  regret with POOR output (q=0.1): 0.5000   <-- 'growing regret = suboptimal strategy' is INVERTED
```

The README says *"A growing regret indicates the allocation strategy is suboptimal."* It is backwards: **regret grows when quality goes up.** It is a quality-*praise* meter wearing a regret label.

### 🟠 The "core optimization engine" has no callers

README: *"This crate IS the γ + η = C conservation law in action. It's the core optimization engine of SuperInstance. The Cocapn delegates fleet-wide allocation decisions to this harness."*

Checked `Cargo.toml` of `cocapn-core`, `cocapn-wasm`, `fleet-agent-core`, plus `SuperInstance/ARCHITECTURE.md` (the link target) and `README.md`: **zero hits for `superinstance-harness` / `superinstance_harness`** in any of them. Nothing in the fleet depends on it.

### ✅ What is genuinely good here

The EWMA streak logic is right, and right for a subtle reason: `ewma_quality` is updated *before* the comparison, so `output_quality < ewma_quality` reduces to `q < ewma_old` — comparing against the *previous* EWMA, as intended. The ternary-signal design (Decrease/Increase/Maintain with a quality-weighted inversion below 0.5) is a real bandit-flavoured controller with proper references (Auer et al. 2002, Sutton & Barto). The **idea is worth stealing; the implementation's guarantees are not.**

---

## 3. `flux-a2a-prototype` — the fleet's largest unseen implementation, with a 879-test suite that has never once been green

**What it is.** A 26-module, 1,475 KB Python implementation of an agent-to-agent protocol for the FLUX multilingual ecosystem: typed messages (TELL/ASK/REPLY/BCAST/FORK/JOIN/SYNC/VOTE/PROPOSE/MERGE), a capability router, a **type-safe cross-language bridge** with a cost matrix over 5 languages, a paradigm lattice, a partial evaluator, a consensus/discussion module, and a `message-in-a-bottle/` fleet mailbox protocol. 16 test files, **879 collected tests** (657 test functions, expanded by `parametrize`), plus round-based research docs (R1-3, R4-6, R10-12, R16-18) and a `docs/isa-mapping-analysis.md`.

**The CI has never passed:** `total_runs = 7`, **7 failures**, 0 successes.

**The README describes a different artifact.** It documents `from a2a import A2AClient, …` and closes with *"13 tests passing."* That is the **267-line top-level `a2a.py`**, not the 26-module `src/flux_a2a/` package with 879 collected tests. The README is describing a prototype, not the thing in the box.

### The suite, actually executed

PyPI is blocked in this sandbox, so pytest was **built from GitHub source** (pytest 8.4.2 + pluggy 1.5.0 + iniconfig 2.0.0 + packaging 24.0 + pygments 2.18.0 + typing_extensions 4.12.2, hand-written `_pytest/_version.py`). Run against the repo's own `src/`:

```
8 failed, 832 passed, 39 skipped in 2.45s      (879 tests collected)
```

**All 8 failures are real.** Each was additionally re-derived directly against `src/flux_a2a/` — outside pytest entirely — so none of them depends on the harness:

| Failing test | Reality |
|---|---|
| `test_wen_lat_bridge.py::TestPoetryMoodExpression::test_seven_char_poetry_with_modifier` | The docstring is about **七言 (seven-character) poetry**. The line `大道之行也天下为公` is **9 characters**; the assertion is `len(line) == 10`. The test fails on a literal it can never satisfy, and it is wrong on its own subject twice. |
| `test_zho_deu_bridge.py::TestBridgeSemantics::test_paradigm_distance_is_computable` | `ParadigmLattice` stores `self._points` and exposes `all_points`/`classical_points`/`nl_points`/`get` — there is **no public `points`**. The test's `try/except ImportError` does not catch `AttributeError`, so the error escapes. |
| `test_optimizer.py::TestBridgeOptimizer::test_optimize_bridge_sequence_same_source_target` | `optimize_bridge_sequence(["zho","zho"])` returns **`['zho','zho']`** — it does not collapse a same-source/same-target path. Test asserts `== ["zho"]`. |
| `test_optimizer.py::TestBridgeOptimizer::test_find_cheaper_intermediate` | Over all 20 language pairs, `find_cheaper_intermediate` returns a result for **0 of them**. The test asserts `len(results) > 0`. The feature is effectively dead. |
| `test_optimizer.py::TestParadigmProfiler::test_lat_strong_in_temporal_reasoning` | `profile("lat").suitability("temporal_reasoning")` = **0.85**; the test asserts `≥ 0.9`. |
| `…::test_san_strong_in_formal_reasoning` | `profile("san").suitability("formal_reasoning")` = **0.85**; asserted `≥ 0.9`. |
| `…::test_wen_strong_in_contextual_inference` | `profile("wen").suitability("contextual_inference")` = **0.85**; asserted `≥ 0.9`. |
| `test_optimizer.py::TestIntegration::test_bridge_optimizer_with_cross_optimizer` | Cross-optimizer path does not preserve the asserted first hop. |

Real pytest's own failure output for the poetry case, verbatim:

```
E        +  where 9 = len('大道之行也天下为公')
tests/test_wen_lat_bridge.py:166: AssertionError
```

**And 39 tests skip**, almost all because the external runtimes are absent:

```
   9  flux_zho not available (8) + 1 "not available in test environment"
   9  No shared equivalence classes for <src><-><tgt>      (all_pairs_bridge)
   7  flux_kor not available
   5  flux_wen not available
   4  flux_deu not available
   3  flux_san not available
   2  flux runtime not available
```

The three bridge test files (`kor_san` 11 skips, `zho_deu` 14, `wen_lat` 5) are **mostly skipped** — so the flagship cross-language feature is the *least* verified part of the package. The 9 "no shared equivalence classes" skips in `all_pairs_bridge` are a different failure: the lattice has no bridge for those language pairs, so the cost matrix silently does not cover them.

**Why another agent should care.** The type-safe cross-language bridge with a **cost matrix**, an 8-dimensional paradigm lattice, and an AST unifier is genuinely reusable fleet infrastructure that nobody outside this repo has looked at. It is also the cleanest specimen so far of a *falsifiable* red CI: **832 of 879 tests pass**, and the 8 that fail fail for reasons a human can read in one line each. The fix list is an afternoon.

---

## 4. `quilt-cellular-arch` — the architectural synthesis repo, with one honest benchmark and one benchmark that is not

**What it is.** 130 files / 70 Python files / 833 KB of code — the "architectural synthesis" of the Quilt ecosystem: the cell-as-foundation thesis, the 5-opcode polyformalism in vector-native form, the DSH lifecycle (Decompose-Synthesize-Harden), the cross-device ESP32 herd, a canon DB, a curator (relevance field, hand evolution), and four benchmarks. **No test files anywhere. No `.github/workflows/` at all.**

**Benchmark 01 (SIMD) is honest.** `RESULTS.md` claims *"All measurements are from the parent session (not LLM-fabricated)"* and the claim survives. Re-run here:

| Opcode | RESULTS.md | measured here |
|---|---|---|
| BIND | 57x | 95.3x |
| VIEW | 181x | 128.2x |
| EFFECT | 57x | 180.0x |
| TICK | 28x (per cell) | 17.7x (per cell) |
| LINK | 5.5x | 2.7x |

Different hardware, same structure, same order of magnitude, and the TICK row's arithmetic checks out (0.357 ms ÷ 10 × 1000 ÷ 1.03 ms → 28.8x, matching the 28x claim). **This is a benchmark file that is telling the truth**, which is why the next one is worth reading closely.

### 🔴 DEFECT — "Cost reduction: 99.8% of model calls avoided per TICK" is a unit error; the true value is 0.0%

`benchmarks/02-dsh-lifecycle.py:124`:

```python
print(f"    Cost reduction: {(1 - total_calls_after / (total_calls_before * 1000)) * 100:.1f}%")
```

Two compounding errors:

1. **The denominator multiplies a *total* by the tick count instead of using the *rate*.** `total_calls_before` is 1000 calls made over 1000 ticks = **1 call/tick**; `total_calls_before * 1000` asserts **1000 calls/tick**. The denominator is inflated 1000×.
2. **The numerator is a one-time setup cost charged against a recurring budget.** `total_calls_after` = 2000 is the number of model calls spent *observing* the two newly synthesised cells — it is the cost of the decomposition, not a per-tick running cost.

Measured with the script's **own `Cell` class**, over 1000 further ticks of the hardened system:

```
  BEFORE: 1000 model calls over 1000 ticks = 1.000 model calls/tick
  AFTER:  1000 model calls over 1000 ticks = 1.000 model calls/tick
         (algo-cell: 0 calls, joint-cell: 1000 calls)

  TRUE cost reduction = (1 - 1.000/1.000)*100 = 0.0%
  SCRIPT prints 'Cost reduction: 99.8%'
```

**The hardened system costs exactly what the immature one cost.** The algo-cell sheds its model (0 calls/tick) and the joint keeps its model (1 call/tick) — the model moved from the body to the seam, it did not disappear. DSH relocates the cost; it does not reduce it. `RESULTS.md` headlines the number as *"Cost reduction: 99.8% of model calls avoided per TICK"*, and the script's own output on screen says **"Total model calls after DSH: 2000"** against **"Original cell: 1 model-bearing cell, 1000 model calls"** — the contradiction is printed in the same block, four lines above the headline.

**Why it matters beyond this repo.** The 5-opcode "the substrate is vector-native" argument in `RESULTS.md` rests on this number, and `quilt-cellular-arch` is the synthesis document the rest of the fleet cites. A headline that survives contact with the script's own output is the cheapest kind of credibility to spend.

---

## 5. The dead push trigger — 17 workflows across 13 repos aim CI at a branch that does not exist

**The class.** A workflow file whose `on: push: branches: [...]` filter excludes the repo's **default branch**. In this fleet the default branch is `master` and the workflow filter says `main` — and in 12 of the 13 repos **no `main` branch exists at all** (verified via `/repos/{o}/{r}/branches`).

Fleet-wide sweep: 1,084 unseen own repos carry at least one workflow file; 1,168 workflow files inspected; **17 push triggers are dead**.

**The three pure cases — every workflow in the repo is dead, so CI has never run at all:**

| Repo | default | workflows | Action runs | on.push.branches |
|---|---|---|---|---|
| `SuperInstance/local-model-manager` | master | 3 | **0** | `main, develop` ×2 + `release` |
| `SuperInstance/etcd-client` | ci/add-github-actions | 1 | **0** | `main, master` |
| `SuperInstance/plato-mythos-bridge` | master | 1 | **0** | `main` |

`local-model-manager` is the worst of these and the most ironic: it is a **properly packaged repo** — `setup.py` + `pyproject.toml` + `MANIFEST.in` + `requirements.txt` + `pytest.ini` + `conftest.py` + 10 test files (**216 test functions**) — with three substantial workflows (Test Suite = pytest + black + isort + mypy; Validate Package = package structure + MANIFEST.in + quality; Publish to PyPI). **216 tests, a linter, a type checker and a package validator that have never executed once.** `etcd-client`'s single workflow names `main, master` and its default branch is `ci/add-github-actions` — neither is named.

**The graded cases — the run count comes from a different workflow, so the badge lies by proxy:**

| Repo | runs | by workflow name | dead workflow |
|---|---|---|---|
| `cocapn-ai-web` | 58 (47 ok) | `pages build and deployment` | `ci.yml` — the **only** workflow in the repo |
| `quicunnel-archive` | 10 (10 ok) | `cargo in /. - Update …`, `github_actions in /. - Update …` (Dependabot) | `ci.yml` — the only project CI |
| `hwscan` | 5 (5 ok) | `cargo in /. - Update …` (Dependabot) | `ci.yml` — the only project CI |
| `ecosystem-dashboard` | 8 (6 ok) | `pages build and deployment` | `ci.yml` — the only workflow |
| `distributed-tracing` | 1 | `Graph Update: go_modules …` (Dependabot) | `test.yml` — the only workflow |
| `ai-token-counter` / `conversation-toolkit` / `embedding-utils` | 1 (1 ok) | `CI` | `test.yml` + `validate.yml` dead; a thin `ci.yml` on `master` carries the badge |
| `ternary-rhythm` | 8 (**0 ok, 8 fail**) | `CI` | `rust.yml` — the only workflow |
| `quilt-live-canon` | 6 (5 ok, 1 fail) | `canon-hash` ×3, `canon-verify` ×3 | `canon-verify.yml` targets `master` while default is `main` |

`cocapn-ai-web` is the sharpest: **58 green runs, every one of them a Pages deploy.** The repository's own `ci.yml` has never run on a push. Reading the Actions count as "CI is green here" is exactly the mistake this class invites — the same mistake as round 129's "plato-portal is green (26/30) and 100% broken (CI 0/5) simultaneously", but with a different mechanism.

**Detector (one request per repo, no file fetch):** for each repo, read `default_branch` from `/repos/{o}/{r}` and list `/repos/{o}/{r}/branches`; if any workflow's `on.push.branches` excludes every existing branch, the push CI is dead. Corroborate with `actions/runs` **grouped by `name`**, not by `conclusion` — Dependabot and Pages workflows will happily manufacture a green-looking count.

---

## 6. `voice-games` — pushed today; 98.8% of a 630 MB tree is committed tournament output

Pushed **2026-10-22T22:08Z**, nine minutes before this session opened — so certainly unexamined.

**What it is.** Three self-contained voice-commanded games: *Sitka Skies* (a flight sim over Sitka, Alaska, flown by voice — "fly to Sitka", "turn left", "speed up") in an HP and a ProArt build, and *COLOR SQUAD*, a 4-unit voice-commanded RTS capture-the-flag with a squad that "learns your voice", tutor-unlocked verbs and Jev negation guards. Plus a tournament demo where scripted strategies fight on a call budget. No build step; Web Speech API with a Cloudflare STT fallback for Safari/iPad and a text box as last resort. Live on GitHub Pages. **This is a lovely piece of work and it is exactly the kind of thing nobody has looked at.**

**But the repository is 98.8% machine-generated output.** 19,653 blobs / 630 MB tree:

| extension | count | size |
|---|---|---|
| **`.json`** | **19,586** | **621 MB** |
| `.jsonl` | 1 | 3.6 MB |
| `.mp3` | 44 | 4 MB |
| `.html` | 10 | ~0 |
| `.js` | 3 | ~0 |
| `.md` | 8 | ~0 |

All 19,582 of the JSON files live in **`tournament/replays/`** — one file per scripted tournament run, ~32 KB each, timestamp-named (`2026-10-10T16-02-23-401Z.json`). The actual game is **10 HTML files and 3 JS files**. In other words: the entire product is ~13 code files, and 621 MB of recorded replays are committed alongside it.

**Why it matters.** The API reports 105 MB of git history for a 630 MB tree — a 6× history excess — and every clone pays to pull a megabyte-scale archive of tournament logs that no code reads. The `tournament/results.jsonl` (3.6 MB) is the one artefact that looks like it might be the roll-up; the 19,582 per-run files are what is not. No `.gitignore` (the repo has none) and no CI.

---

## 7. Method corrections carried forward

1. **Never filter the candidate pool on API `size`; tree-scan it.** API `size` is in **KB** and is an upper bound on tree bytes, but it is a *terrible* proxy in the other direction: the tree of `superinstance-ai` is 627 KB while its API size is 605 KB, and `flux-genome-rs` has 48,562 KB of history for a 225 KB tree. Filtering on `size` at all cost me a 1000× unit error this round (I filtered `>= 10_000` believing the field was bytes, and got 12 candidates instead of 1,408). **The right filter is "API size ≥ 20 KB" → 1,408 repos → tree-scan all of them → rank on code bytes.**
2. **A suite that reports `PASSED=0 FAILED=0 SKIPPED=0` is a broken collector, not an empty suite.** My first shim run returned exactly that, and I nearly filed "the suite is empty" — the modules had imported fine and all the tests were inside `class Test*:` bodies. The number to trust is the **module count**, not the test count. Same lesson as round 129's `/.git` matching `/.github`.
3. **Build pytest from GitHub source — do not hand-write a shim.** PyPI is blocked, but `pytest-dev/pytest` (8.4.2), `pluggy`, `iniconfig`, `packaging`, `pygments` and `typing_extensions` all clone and copy into site-packages, with a hand-written `_pytest/_version.py`. My hand-written shim got the **8 failures exactly right** but under-expanded `parametrize` and reported **619 passed** where real pytest reports **832** (657 collected vs 879) — a shim that agrees with pytest on *failures* can still be wrong on *totals*, and a wrong denominator is how a suite gets over-claimed. Corollary: **every reported failure must be re-derived directly against `src/`**, outside any harness — all 8 in §3 were, and all 8 held.
4. **A test module that does not compile is a different class from a test module that never runs.** `cargo test` failing to *parse* is invisible to `cargo build` and invisible to a badge.
5. **Group `actions/runs` by `name`, never by `conclusion`.** §5 is built on this: `cocapn-ai-web` has 58 green runs, all Pages deploys, and a `ci.yml` that has never fired.
6. **A benchmark that states its own provenance ("not LLM-fabricated") deserves a rerun — but check the formula, not just the code.** §4's number is computed, not hardcoded; it is a *unit error*. Reading `RESULTS.md` alone would have passed it.

---

## 8. Status of the 10-01 "already found" list (spot-checked, not re-derived)

| Repo | Status at 2026-10-22T22:34Z |
|---|---|
| `xruntime-conformance` | still **0 Actions runs** — no CI |
| `substrate-foundation` | still **0 Actions runs** |
| `quilt-ewitness` | still **0 Actions runs** |
| `pie-minimax` | still **0 Actions runs** |
| `quilt-i2i` | still **0 Actions runs** |
| `superinstance-api` | still **0 Actions runs**; `.wrangler/cache/wrangler-account.json` **still git-tracked** (the cosmetic-ignore defect persists) |
| `substrate-attest-rs` | still **0 Actions runs** |
| `quilt-canary` | **worse**: 66 blobs of which **64 are `target/` entries** (was 52); `.gitignore` still **404 — the file does not exist**; still **0 test files**; still 0 Actions runs |
| `quilt-gpu-lab` | 453 runs · `fleet-seeds` 85 · `quilt-verilog` 148 · `constraint-theory-core` 92 · `moth-honest` 12 · `quality-gate-stream` 22 — CI present, unchanged |

---

## 9. Environment (durable)

- **`/workspace` is still at 100% EDQUOT.** All work was done in `/tmp` (overlay, 28 GB free). The `write` tool cannot reach `/tmp`; every file was written with a shell heredoc.
- **PyPI is blocked** (`pip download pytest` → *No matching distribution found*), but **pytest can be built from GitHub source** — `pytest-dev/pytest` @ 8.4.2 + `pluggy` 1.5.0 + `iniconfig` v2.0.0 + `packaging` 24.0 + `pygments` 2.18.0 + `typing_extensions` 4.12.2, copied into `/usr/local/lib/python3.11/dist-packages`, with a hand-written `_pytest/_version.py` (`version = "8.4.2"`). That is how the `flux-a2a-prototype` suite was really executed.
- **crates.io is 403**, so any crate with external deps cannot be built by cargo. **But `static.rust-lang.org` and `sh.rustup.rs` are reachable (HTTP 200)** — `rustc`/`cargo` **1.99.1** install and work. `fleet-agent-core` (zero deps) therefore got a genuine `cargo test` receipt, and `superinstance-harness` was compiled with `rustc` directly after stripping only the serde derives (crates.io unreachable) — the numeric core is byte-identical. **This upgrades the toolchain story materially: Rust findings in this fleet no longer have to be inspection-only.**
- `rustup` must be run with `HOME=/root` (the default `HOME=/workspace/.home` is on the full NAS → *Disk quota exceeded*).
- `gh` is absent; `curl -sk` + `$GITHUB_TOKEN` throughout. `GIT_SSL_NO_VERIFY=1` for clones. `raw.githubusercontent.com` has a separate rate limit from the API and was used for the 1,168-workflow sweep at no API cost.
- API budget used this round: ~2,000 of 5,000 (54 census pages + ~1,505 tree scans + ~200 workflow/Actions calls).
