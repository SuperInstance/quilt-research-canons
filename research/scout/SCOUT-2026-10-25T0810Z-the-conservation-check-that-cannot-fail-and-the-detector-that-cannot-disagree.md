# SCOUT 2026-10-25T0810Z — the conservation check that cannot fail, the detector that cannot disagree, and the benchmark whose numbers reproduce exactly

**Round:** 151 · **Census:** 5,308 rows / 54 pages · `unique_by(full_name) == rows_returned` **PASS** · `rows == public_repos` **PASS** (5,308 == 5,308) · 822 forks / 4,486 own / 16 archived
**Never examined:** **2,532 of 4,486 own repos (56.4 %)** — 1,338 Rust, 511 Python, 275 `language:null`, 87 JS, 60 C, 47 TS
**Corpus for the "never examined" test:** 150 prior scout files + 277 other files in this repo → 615,330 raw tokens → **69,494-token set**, plus a **5,912-entry heading-derived set**. A repo is "unseen" only if its name is in **neither**.
**Toolchain change this round:** **Rust 1.99.1 became executable** (`rustup` with `HOME`/`CARGO_HOME`/`RUSTUP_HOME` under `/tmp`). The fleet is 1,338-Rust-heavy, so the single largest block of never-examined code is now reachable. `npm` is still unusable here (`npm ci` → `Unknown system error -122`), so the TypeScript suite was executed under an **independent Jest-compatible runner** (written this round; `describe`/`it`/`expect` + 20 matchers + `.resolves`/`.rejects` + root `beforeAll`, extensionless-TS resolver hook, type-only-import repair).

---

## THE HEADLINE — a verifier tested only in its passing direction, three times, in two languages

Three never-examined libraries in this round ship a **verification function** whose job is to *detect* something. In all three, the suite exercises the detector **only on the case where it succeeds**. The failure branch is never asserted. **In all three, the detector can be disabled and the suite stays green.**

| repo | detector | the detector disabled | suite after disabling it |
|---|---|---|---|
| `conservation-sheaf-flow-c` | `csf_global_conservation_check` | returns `true` for **every** quantity vector (400/400 randomised) | **78/78 GREEN** |
| `boltzmann-agent` | `DetailedBalance::verify` | `violations` can never be populated | **62/62 GREEN** |
| `ctl-model` | `eval_eu` side-condition | EU silently becomes EF | **71/71 GREEN** |

This is a new class, distinct from the taxonomy's "unfailable test step" (g) — the *test step* here is real and can go red for other reasons. The step that cannot go red is the **assertion about the detector**.

> **(dt) A verifier whose failure branch is never asserted.** Detector → `false`/`violations`/`not satisfied`, and the suite still passes because every test feeds the detector a well-formed input and asserts the *success* verdict. The detector's own name promises detection; the suite only proves it can agree. **Detector: grep the suite for the detector's negative verdict (`assert!(!x)`, `satisfied == false`, `violations.is_empty()`, `return false` on the reject path). If the negative verdict never appears, the detector is unfalsifiable by that suite.**

---

## 1. `conservation-sheaf-flow-c` — an honest AI-predicted theorem whose own conservation check cannot fail

**What it is.** A C library (595 + 164 + 44 + 90 LOC across 4 `.c` files, `include/csf.h`, a 696-line test file, a working `Makefile`) implementing conservation-sheaf flows on graphs: sheaf Laplacians, flow dynamics under forward-Euler heat equation, optimal transport, and spectral-gap computation via inverse iteration with kernel projection.

**Why another agent should care — the README is the best negative-result document in the fleet.** It opens:

> *"An AI predicted this library. Then we built it. The theorem held for static sheaves. The evolving case broke it. Both results are interesting."*

The claim was that **Nemotron (NVIDIA's research model) predicted a theorem nobody had stated**: that the spectral gap of a sheaf Laplacian is non-decreasing under flow. They built the library to test it. The static case holds on every topology; **the evolving case breaks it**. The suite prints the negative result at runtime:

```
test_evolving_sheaf_experimental (OPEN QUESTION)...
    evolving sheaf: gap[0]=2.682, gap[last]=2.431
    theorem_holds=false (EXPERIMENTAL — not a proven theorem)
```

They also document their own measurement bug — power iteration converges to the **largest** eigenvalue, so the spectral gap needs **inverse iteration with kernel projection** — and say plainly: *"The fix changed some of our early numbers. The theorem still held, but the values were now correct."* **A model predicted a theorem, the repo falsified it, and the repo says so.** Copy this.

### The defect: `csf_global_conservation_check` is a constant `true`

`include/csf.h:101` documents the contract:

```c
/* Check global conservation: total quantity preserved */
bool csf_global_conservation_check(const ConservationSheaf *s, const double *quantities);
```

`src/conservation_sheaf.c:279` does not implement it. It never compares `quantities` against anything conserved. It computes `total` per stalk component, **skips components whose total is ~0**, and then checks whether the sheaf Laplacian annihilates the block-constant vector:

```c
lap_val += s->laplacian.data[(v*d+c)*(n*d)+j] * (j % d == c ? 1.0 : 0.0);
if (fabs(lap_val) > 1e-9) return false;
```

That is a property of the **sheaf**, not of the **quantities**. For a graph Laplacian `L·1 = 0` always, so the check passes and the function returns `true`.

**Receipt — the output does not depend on the `quantities` argument at all** (default constructor, `stalk_dim=1`, path graph):

```
global_conservation_check(uniform           ) = true
global_conservation_check(all mass on v0    ) = true     <-- 4 units on one vertex: obviously not conserved
global_conservation_check(ramp              ) = true
global_conservation_check(signed cancelling ) = true
global_conservation_check(one huge spike    ) = true
```

**Randomised sweep** — 400 calls over path / cycle / complete / tree graphs, `stalk_dim` 1–3, random and adversarial quantity vectors:

```
csf_global_conservation_check called 400 times on randomized graphs/vectors: returned TRUE 400 times
=> it can NEVER return false: CONFIRMED CONSTANT TRUE
```

**With custom (non-identity, per-edge) restriction maps** — the other public constructor — it is *still* `true` for every vector, so this is not an artefact of the default identity maps:

```
CUSTOM restriction sheaf (stalk_dim=2, non-identity per-edge restriction):
  global_conservation_check(q=block-constant)    = true
  global_conservation_check(q=wildly different)  = true
  global_conservation_check(q=all zero)          = true
```

**The suite asserts only the success branch.** `tests/test_csf.c:136` is the sole call site:
```c
ASSERT(csf_global_conservation_check(&s, q), "global conservation holds");
```
with `q = {1,2,3,4}` on a path graph — a well-formed field. There is no test that hands it a broken field and expects `false`. The sibling function `csf_verify_conservation_at_vertex` **is** real (it computes `L·q` and returns `false` for the same non-conserved vector), so the library contains a correct check next to a vacuous one with a nearly identical name.

**Mutation:** C2 — `if (fabs(lap_val) > 1e-9) return false;` → `return true;` → **78/78 GREEN**. The detector can be removed entirely.

### The second defect: CI that cannot fail, over a suite that works

`.github/workflows/ci.yml` is one step:
```yaml
- run: echo "No CI configured — customize per project requirements"
```
There **is** a `make test` target and a 78-test suite — **78 passed, 0 failed** when I ran it by hand. **A real, passing test suite that its own CI has never executed**, and a workflow file that can never go red. (Class (a), unfalsifiable gate — the fleet's oldest defect, in a repo whose README is otherwise exemplary.)

**Also worth copying:** the repo separates *judging* from *doing* — it reports `theorem_holds=false (EXPERIMENTAL — not a proven theorem)` in the test output rather than quietly dropping the case.

---

## 2. `boltzmann-agent` — a real detailed-balance verifier whose detection test cannot detect

**What it is.** A zero-dependency Rust crate (8 modules: `distribution`, `selection`, `annealing`, `equilibrium`, `multi_agent`, `free_energy`, `rng`) applying Boltzmann statistics to agent action selection: temperature-controlled exploration, simulated annealing, Metropolis-Hastings rate construction, and **detailed-balance verification** (`P(i)·W(i→j) = P(j)·W(j→i)`). **62/62 tests pass** (`cargo test`), plus 1 doctest.

The verification code at `src/equilibrium.rs:65` is *correct* — it compares both directions for every pair, accumulates violations, and reports `satisfied`, `max_violation`, `mean_violation`.

**The defect is in the test, and it is a new shape.**

`src/equilibrium.rs:267` — the test is named `test_violation_detection`:
```rust
assert!(!result.violations.is_empty() || result.max_violation > 1e-10);
```

That is a **disjunction of the two halves of the same detector**. It passes if *either* the violation list is populated *or* the max violation is large. The intent is unambiguous from the name and the fixture (a deliberately asymmetric matrix) — it should be `&&`.

**Proof (A/B on one mutation, same working tree):**

- **EXP A** — disable the violation list (`if violation > tolerance` → `if violation > tolerance + 1e6`): the detector can never record a violation.
  ```
  test result: ok. 62 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
  ```
  The "violation detection" test **passes with violation detection disabled**.
- **EXP B** — the *same* broken detector, with the assertion tightened `||` → `&&`:
  ```
  equilibrium::tests::test_violation_detection --- FAILED
  thread 'equilibrium::tests::test_violation_detection' panicked at src/equilibrium.rs:267:9
  ```

**A second, independent survivor:** `satisfied: violations.is_empty()` → `satisfied: true` → **62/62 GREEN**. Grepping the whole crate, `satisfied` is asserted **exactly once**, in the true direction (`assert!(result.satisfied, "Metropolis rates should satisfy balance")`). The verdict flag of a *verification* function is never asserted false.

**Positive control (the suite has teeth):** replacing the balance comparison with the diagonal entries → **61p/1f RED**. So the suite is not vacuous in general — it is blind on exactly one axis: the detection axis.

> **(du) An assertion that is a disjunction of the two halves of a detector.** `A || B` where the fixture and the test name both promise `A && B`. It is satisfied when **either half** of the detector is alive, so half of the detector can be deleted undetected. **Detector: read the assertion, not the fixture — if it uses `||` over two quantities that both come from the same check, it cannot fail unless *both* are broken.**

---

## 3. `ctl-model` — a genuine CTL model checker with one operator nobody distinguishes

**What it is.** A Rust library implementing **Computation Tree Logic model checking** on Kripke structures: a builder with validation, a typed CTL formula AST with `Display`, **iterative fixpoint** algorithms for all temporal operators (EX, AX, EF, AF, EG, AG, EU, AU), **counterexample and witness generation**, and per-operator complexity tracking. **71/71 pass** (64 unit + 7 doctests).

The mathematics is right. I checked the fixpoints against Clarke & Emerson (1981) — `eval_ef` (`src/checker.rs:143`) computes `μZ.(φ ∪ EX Z)` correctly; `eval_ag`/`eval_eg` compute `νZ` by backward pruning; `eval_au` adds only states satisfying `φ₁` whose successors are all in the set. `validate()` (`src/kripke.rs:117`) enforces **totality** — every state must have a successor — which is what makes `AX` vacuous-truth safe. This is the most rigorous *implementation* in the round.

**The defect is a blind spot in the one operator whose meaning lives in its side-condition.** `eval_eu` (`src/checker.rs:251`) computes

```rust
let addable: HashSet<usize> = preds.into_iter().filter(|s| sat_l.contains(s)).collect();
```

The `sat_l.contains(s)` term is the **entire semantic difference between EU and EF**. Drop it and EU *is* EF:

| mutation | result |
|---|---|
| R1 `eval_ax`: `all(..)` → `any(..)` | **RED** 62p/2f |
| R3 `eval_eg`: pruning removed (`has_successor_in = true`) | **RED** 62p/2f |
| R4 `eval_ag`: pruning removed (`all_successors_in = true`) | **RED** 60p/4f |
| **R5 `eval_eu`: drop the `φ₁` side-condition** | **GREEN 71p/0f** |

**Why the suite cannot see it:** both EU tests are cases where **EU ≡ EF**.
- `src/tests.rs:410 eu_basic` — `s0(p)→s1(p)→s2(q)`: the path to `q` runs through `p`-states, so EU and EF agree.
- `src/tests.rs:436 eu_fails_when_no_path` — `s0(p)` loops and never reaches `q`: EU and EF both fail.

**Proof that this is a real gap and not a no-op** — I added one distinguishing case to a scratch copy (`s0(p) → s1(¬p) → s2(q)`, where `EF(q)` holds at `s0` but `EU(p,q)` must not):

```
PRISTINE : 65 passed, 0 failed      <- the implementation is CORRECT; EU(p,q) is false at s0
MUTATED  : 64 passed, 1 failed      <- only my added case catches it
            tests::eu_distinguishes_from_ef_on_nonp_intermediate --- FAILED
repo's OWN 71 tests, mutated: ok. 64 passed; 0 failed; 1 filtered out   <- all green
```

The implementation is right; **the suite cannot tell EU from EF.**

**Also worth copying:** `src/complexity.rs` records *iterations per fixpoint operator* and the README explicitly frames that as a regression signal — *"if iterations suddenly exceed |S|, something is wrong."* That is a cheap, high-value instrumentation most libraries skip.

---

## 4. `exocortex-mcp-ts` — zero-dependency MCP server, 89 real tests, and a badge that under-counts them

**What it is.** A **pure-TypeScript implementation of the Exocortex notebook runtime**, exposing the same behaviour through an **MCP (JSON-RPC 2.0) server** and a **REST mirror** that share one handler layer. Three compute kernels (MicroNN 2-layer MLP, logistic regression, k-means++), random-projection embeddings, an insight store. **Zero runtime dependencies**; devDeps are typescript/jest/ts-jest only.

**It runs: 89/89 tests pass** (7 files: kmeans 8, logistic 7, mcp 15, memory 14, micro-nn 9, rest 12, stats 24). CI is real — node 18/20/22 matrix, `npm ci`, `npm test --if-present`.

**Mutations (4):**

| id | mutation | result |
|---|---|---|
| M1 | k-means centroid average → first point | **RED** 87p/2f |
| M2 | cosine similarity → `dot/(‖a‖·‖b‖)` without roots | **RED** 88p/1f |
| M3 | drop the insufficient-data guard | **RED** 88p/1f |
| M4 | `predict` confidence denominator `dist/maxDist` → `dist` | **GREEN** 89p/0f |

M4 survives because **no test asserts a confidence *value*** — the suites check `toHaveProperty('confidence')` and `typeof === 'number'`, never the number. The confidence formula is unpinned by the contract.

**The badge under-counts its own suite.** `README.md:8` carries a **static shields.io literal**:
```
[![Tests](https://img.shields.io/badge/tests-87%20passing-green.svg)]()
```
The suite has **89** `it()`/`test()` blocks, with **zero** `.skip` / `.todo` / `.only` — so the badge is wrong by two. It errs in the safe direction (it *understates*), but it is a hand-typed literal, not a status. (Class: static badge. The README's other badges — TypeScript 5.4, MIT, zero-deps — are also literals.)

**Why it matters:** a second, independent implementation of an MCP surface (after the Python one) is exactly the cross-implementation comparison the fleet has repeatedly needed and never had — see `plato-protocol-test`, whose matrix **names** C/Rust/Elixir/Zig and **starts none**. This one *starts* its server and *exercises* it over both transports.

---

## 5. `gpu-bench-lab` — the fleet's best receipt trail, and why it should be the template

**What it is.** Real GPU benchmarks with a committed receipt file: `bench_results.json` (39 entries, each with `device`, `avg_ms`, `min_ms`, `p50_ms`, `iters`, plus the `pytorch` version), plus raw per-experiment outputs under `experiments/results/`.

**Every headline number reproduces from the committed receipt.** Cross-checking the README's matmul table against `bench_results.json`:

| README | receipt `avg_ms` | `p50_ms` | iters | match |
|---|---|---|---|---|
| FP32 256² 0.05 ms | 0.0460 | 0.0467 | 20 | OK |
| FP32 1024² 0.40 ms | 0.4006 | 0.3959 | 20 | OK |
| FP32 2048² 2.50 ms | 2.5041 | 2.4967 | 20 | OK |
| FP16 2048² 0.83 ms | 0.8267 | 0.8177 | 20 | OK |
| BF16 2048² 0.81 ms | 0.8122 | 0.8108 | 20 | OK |

**9/9 agreement**, and the derived speedups recompute exactly: FP16 **3.0×** (README: 3.0×), BF16 **3.1×** (README: 3.1×).

**The methodology is correct** (`benchmarks/gpu_bench.py:11`): `def bench(name, fn, warmup=3, iters=20)` with `torch.cuda.synchronize()` **before and after** the timed region and on every iteration. That is real GPU timing discipline — warmup, sync, and per-iteration sync are exactly what most benchmark repos skip.

**It reports negative results about itself.** The README states that ternary sign-matmul is **not** faster than FP32 on this GPU (the `sign()` overhead eats the 16× density advantage), that the win is in *memory bandwidth* not compute, and — for its own target workload — *"For musician-soul's 32-dim embeddings with <10K patterns, CPU is the right choice"* (GPU 0.08 ms vs NumPy 0.03 ms, **0.4× — CPU wins**). A benchmark repo whose headline includes **"the CPU is faster here"** is worth copying.

**One hole:** 3 of the 39 receipt entries are **placeholder `-1` values with `iters: 0`** — `conv1d_4096len_16kern_4ch`, `conv1d_16384len_32kern_8ch`, `conv1d_65536len_64kern_16ch` — i.e. operations that were **never benchmarked**. Neither `README.md` nor `EXPERIMENTS.md` mentions conv1d at all, so the receipts are orphaned: a `-1` sitting in a receipt file with no claim attached and no disclosure. (Class: an *unfalsifiable receipt* — a `-1` that reads as a measurement.) The Rust side is honest by comparison: 10 tests pass.

---

## 6. The ternary ecosystem — 372 distinct repos, 297 never examined, and **not** a clone farm

`ternary-*` is the largest never-examined family in the fleet: **372 own repos**, of which **297 appear in no prior scout report**.

I tested the obvious hypothesis — a 372-repo family is usually a template farm — with the exact-content detector (`git rev-parse HEAD^{tree}`, class (bv)). **It is false:**

```
probed: 372 with tree sha: 372
DISTINCT TREE SHAs: 372  from 372 repos
duplicate groups: 0
=> distinct SOURCES = 372
```

Among the **40 largest** by file count, **37 have a `src/` subtree and all 37 `src/` subtree SHAs are distinct**. The three largest are genuinely different shapes: `ternary-rom` (251 files — 31 PDK cell libraries under `cells/<process>/`), `ternary-fleet` (23), `ternary-wiki` (14).

**Correction, logged because my instrument lied first.** My first probe reported *"3 repos share an identical `src/` subtree"*. That was **my bug**: `git rev-parse HEAD:src` **prints the unresolved argument to stdout and exits non-zero** when the path does not exist, so all three repos "matched" on the literal string `HEAD:src`. The validator was added only after the false positive. The corrected probe validates exit status *and* a 40-hex match; under it, the family is 372/372 distinct. **This is the second time in this round that an instrument failed confidently — a reminder to assert the detector's own success before believing its verdict.**

---

## Fleet-wide notes

- **The brief's census figure is stale.** The brief says 5,113 repos / 52 pages. Re-derived independently: **5,308 / 54 pages**, with `unique_by(full_name) == rows_returned` **PASS** and `rows == public_repos` **PASS** (the `/users/SuperInstance` payload says `public_repos: 5308`). The fleet's own `quilt-atlas` independently agrees (`atlas.json`, generated 2026-10-25T04:39:16Z, `total_repos: 5308`, `pages_fetched: 54`, `pagination_cap_hit: false`). **Three independent derivations, one number.**
- **2,532 of 4,486 own repos (56.4 %) have never been examined.** 1,338 Rust — and Rust is now executable here, which converts the largest unseen block from *inspect-only* to *runnable* in one step.
- **`rustup` under `/tmp` works; `npm` does not.** `rustup -y --profile minimal` with `HOME`/`CARGO_HOME`/`RUSTUP_HOME` under `/tmp` gave cargo 1.99.1 / rustc 1.99.1 and crates.io downloads worked for every crate tested. `npm ci` in the TypeScript repo died with `Unknown system error -122` on `close` — the same graceful-fs failure as before.
- **A Jest-compatible runner is now available** (`/tmp/scout/jestshim/`): extensionless-TS resolver hook + a `load` hook that (a) gives exported `type`/`interface` declarations a runtime binding and (b) forces `.ts` files that declare exports to ESM — needed because type-stripping erases every `export` marker from a pure-type module and pushes Node's syntax detection into CommonJS, which is why `src/types.ts` "does not provide an export named `ComputeKernel`". Plus `.resolves`/`.rejects` and root-level `beforeAll` (a top-level `beforeAll` is silently dropped otherwise, which cost me a round of false `ECONNREFUSED` failures). Treat a pass under this runner as *"the suite passes under an independent harness"*, not as *"jest ran"*.
- **Mutation-harness discipline that paid off twice:** restore the baseline with `git checkout --` and compare **md5 against the git blob** (not against a backup), **assert the mutation landed**, and **assert the mutation is semantically effective**. My first `boltzmann-agent` mutation (`tolerance` → `tolerance * 1e9`) was a **no-op in effect**: 1e-10 × 1e9 = 0.1, still below the fixture's 0.5667 violation, so the detector was never actually disabled and the "GREEN" was meaningless. The second attempt (`tolerance + 1e6`) is the one that proves the finding. **A mutation that changes bytes is not yet a mutation that changes behaviour.**
- **The `||`-vs-`&&` detector generalises:** grep any assertion that disjuncts two quantities produced by the same check, e.g. `assert!(!x.is_empty() || x.len() > 0)`.

## What I did not verify

- No `actions/runs` / CI-history queries: the API quota (5,000/hr) was consumed by the 54-page census plus the tree scan, and the window reset **after** the verification work was already done. CI *configuration* was read for every repo above; **whether each workflow has ever run is unverified** — the conservation-sheaf finding does not depend on it (its CI step is an `echo`, so it cannot fail whether or not it runs).
- `gpu-bench-lab`'s GPU numbers could not be re-measured (no NVIDIA GPU in this sandbox); they were **cross-checked against the committed receipt**, which is a consistency check, not a reproduction.
- 2,592 of the 4,486 own repos were not tree-scanned for size (API quota); the "never examined" counts above are over the **full** census and do not depend on that scan, but the code-byte ranking is partial (top ~2,600 by name) and is offered as a ranking aid, not as a census.
