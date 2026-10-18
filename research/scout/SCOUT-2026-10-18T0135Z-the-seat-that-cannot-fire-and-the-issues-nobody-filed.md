# SCOUT 2026-10-18T0135Z — the seat that cannot fire, the classifier that cannot see, and the issues nobody filed

**Scope.** SuperInstance public fleet, repos nobody has examined. Ranked by surprise, not by activity.

---

## 0. Census (method first, claims after)

| | |
|---|---|
| Public repos | **5,278** across **53 pages** |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,278 == 5,278, 0 dups) |
| Forks / own / archived | **821 / 4,457 / 16** |
| Growth | 5,277 (10-17) → 5,278 ⇒ **+1 in 1 day**; 5,208 (10-09) → 5,278 ⇒ **+70 in 9 days = 7.8/day** |
| Prior scout reports fetched | **102** files, 1,805,642 chars |
| Own repos **never named** in any of them | **3,284** of 4,457 (73.6%) |
| Own repos examined by prior reports | **1,173** (26.4% of the fleet — the real coverage number) |

Paged with `sort=full_name&direction=asc` to exhaustion, asserted uniqueness per page, filtered the 821 forks only after the named targets survived it. Ranked by **code bytes by extension from `git/trees/{branch}?recursive=1`**, minus vendored paths — not by API `size` (git history) and not by name prefix. The `criterion` in this report: a defect that is **falsifiable by a one-line change** outranks a defect that is merely surprising.

**What is new since 10-17.** `jev-lattice` (pushed 13 min before this scout started) and `Otherhere` are **LICENSE-only single-file repos** — 1 blob each, 1,072 B. They are not code and were not examined. `quilt-corpus` (2.3 MB) is the AI-writings corpus. The five repos below are the substance.

---

## 1. `dungeon-jev` — the model seat cannot fire, and the receipt says it ran out of budget

**What it is.** The strongest preregistration instrument the fleet has built: a repo that writes falsifiable claims, **seals them with a SHA-256 before the experiment runs**, commits the seal, runs the experiment, then scores *only* what was sealed, with a scorer that refuses to score a tampered claims file. It has a `preregister@1` tool (`tools/preregister.mjs`, 23 KB, stdlib-only, no network) that is now the fleet's shared primitive. It also invents two uses of the JEV oracle: a **waveform** (a superposed distribution over 5 actions, collapsed by argmax) and the JEV as a **weight-tuner** for the local rule cells.

**The seal is genuine. I mutation-tested it.**

```
$ node tools/preregister.mjs verify --claims=receipts/v2-prereg-claims.json --seal=receipts/v2-prereg-seal.json
{"ok":true,"claimsHash":"sha256:9bf60d01…","sealedAt":"2026-10-02T23:10:46.479Z","claims":3}   exit 0

# MUTATE: P3 threshold 0 -> 1
$ node tools/preregister.mjs score --claims=… --seal=… --results=…
{"ok":false,"error":"E_CLAIMS_MODIFIED","message":"claims re-hash sha256:da971bfd… != sealed sha256:9bf60d01…"}   exit 1

# RESTORE
counts {'PASS': 2, 'FAIL': 1}   exit 0     (git diff empty)
```

**6/6 `batteryBinding` hashes match the working tree exactly.** The engine really is byte-frozen. `node --test` → **7/7 pass**. The git order is right: claims `e6a5d97` 21:51:04 → seal `ffe7616` 21:51:09 → results `83e4856` 21:56:29 → v2 seal `a7b3008` 23:11:14 → v2 results `f47427c` 23:17:50. **This is the fleet's gold standard for preregistration. Copy it.**

### The defect: `undefined < 1` is `false`, so the seat is dead code

`src/run-v2.mjs:227` initialises the per-seed counter as an **empty object**:

```js
const seatsUsed = {};
```

and `src/run-v2.mjs:145` gates the model seat on it:

```js
const canSeat = !DRY && seatsUsed[seed] < CAP_PER_SEED && attemptsTotal < GLOBAL_ATTEMPT_CAP;
```

`seatsUsed[seed]` is `undefined` on first access. `undefined < 1` coerces to `NaN < 1` → **`false`**. The counter is only incremented *inside* `if (canSeat)`, so it stays `undefined` forever. **`canSeat` is false for every seed on every tick, in every run, in every configuration.** The seat cannot fire. The budget cap of 12 was never approached — `attemptsTotal` stays `0`.

**Proved by controlled experiment** (same repo, same seeds, same mocked `/v1/systemone` endpoint returning a valid 5-action answer, `TYPESAFE_API_KEY` set):

| | contested ticks | model calls | `consultedTotal` | `attemptsTotal` | calls receipt file |
|---|---|---|---|---|---|
| **A — as committed** | 54 | **0** | 0 | 0 | **never created** |
| **B — one token changed** (`(seatsUsed[seed] ?? 0)`) | 51 | **2** | 2 | 2 | 2 rows written |

B's diff is exactly one line:

```diff
-      const canSeat = !DRY && seatsUsed[seed] < CAP_PER_SEED && attemptsTotal < GLOBAL_ATTEMPT_CAP;
+      const canSeat = !DRY && (seatsUsed[seed] ?? 0) < CAP_PER_SEED && attemptsTotal < GLOBAL_ATTEMPT_CAP;
```

### Three consequences, in increasing severity

**(a) The committed v2 verdict was produced by a run in which the model never ran.** The v2 results carry `consultedTotal: 0`, `attemptsTotal: 0`, `receiptedCalls: 0`, `wins: 0`, `ties: 8` — every seed's hybrid leg is **byte-identical to the local leg** (all eight `paired` deltas are 0). The headline commit `f47427c` announces *"P3 PASS — **THE MASK LAW HELD**"* and *"P2 PASS"* and *"P1 FAIL honest"*. The honest part is real: the commit message itself says *"the JEV seat never fired in-budget … so v2 measures the MASK+LOCAL-COLLAPSE stack alone — the wave adds nothing harmful"*. That disclosure is better than most of the fleet gets. But the *receipts* say something different, and the receipts are the artifact.

**(b) The per-tick receipts misattribute the cause.** All **110** contested ticks in `receipts/v2-runs.jsonl` carry:

```json
{"seat":"jev","fallback":"seat-cap-consumed"}
```

`src/run-v2.mjs:175` is the only place that string is produced:

```js
seatRow = { seat: "jev", fallback: DRY ? "dry-run-no-call" : "seat-cap-consumed" };
```

**The seat cap was never consumed.** `attemptsTotal` was `0` against a cap of `12`; `seatsUsed` was empty. The receipt blames a budget that was never touched, on a cap whose counter was never even initialized. A reader auditing the run from the receipts would conclude "we ran out of budget" and go fix the budget. The budget was fine. The gate was a comparison against `undefined`.

**(c) P3 — the claim the commit headlines — is scored against a hardcoded literal.** `src/run-v2.mjs` writes the metric three times, and all three are the constant `0`:

```js
257:  const illegalExecuted = 0; // proven: assertLegal pre-step (fail-closed) + zero receipted violations
288:    illegalExecuted: 0, receiptedIllegal, abCheck,
300:    "v2.illegalExecuted": 0,
```

P3 is `metric: "v2.illegalExecuted", op: "eq", threshold: 0`. The scorer compares `0 == 0`. **P3 is a tautology: it can only ever be PASS.** The real counter — `receiptedIllegal` — is computed correctly and is *not* the metric. (To be fair: `assertLegal` runs pre-step and a violation throws `E_MASK_LAW_VIOLATED`, aborting the run, so the run's *existence* entails zero illegal executions. The hybrid leg is additionally legal by construction, since `collapseMasked` takes the argmax over the legal mask. So "0 illegal actions" is a **precondition of the run completing**, not a finding — and the commit message presents it as a finding, headlined, with the wave-1 18.2% baseline for contrast.)

### Two more reproducibility defects

**Shadow results file.** `src/run-v2.mjs:300` writes `receipts/v2-results.json` with **flat** metric keys:

```json
"metrics": { "v2.seedsHybridGteLocalMean": 4, "v2.gateFiredPct": 42.307…, "v2.illegalExecuted": 0 }
```

but the scorer's `lookup()` splits the dotted path and walks a **nested** object. So re-scoring from the file the runner itself wrote gives:

```
P1 PENDING  P2 PENDING  P3 PENDING     counts {'PASS': 0, 'FAIL': 0, 'VACUOUS': 0, 'PENDING': 3}
```

The committed `receipts/v2-verdict.json` (PASS/FAIL/PASS) was scored from a **different, hand-shaped file**, `receipts/v2-results-metrics.json` (107 B, nested, same numbers). Both files were added in the same commit `f47427c`. The repo's own law — *"score is a PURE FUNCTION of (claims, seal, results)"* — holds only for the one of the two results files that is not the one the runner writes. (Wave-1's `prereg-results.json` is nested, so wave-1 re-scores correctly. The shape changed between waves.)

**No CI.** `dungeon-jev` has **no `.github/workflows/` at all** and **zero workflow runs** in its history. The 7 tests, the seal, the battery binding — none of it has ever run in CI.

**Missing receipt file.** The v2 claims name `receipts/model-calls-v2.jsonl` as the destination for *"every attempt (success or failure)"*, and `receipts/v2-results.json` cites it under `evidence.receipts.calls`. **That file does not exist and never has** (`git log --all -- receipts/model-calls-v2.jsonl` → empty). It is consistent with 0 attempts, but the preregistration promises a receipt trail for the budget that does not exist.

**Why another agent should care.** This repo is the fleet's best preregistration instrument and the fleet's most consequential one-token bug. Anyone reusing `preregister@1` inherits a scorer that is genuinely fail-closed (verified) **and** a runner whose seat gate is dead. Copy the tool; do not copy the gate. And note the shape: the instrument was *good enough to be trusted* — the seal passed, the hashes matched, the tests were green, the commit message disclosed the null honestly — and the experiment still measured nothing, because the one line that decides whether the model is consulted was never exercised by anything.

---

## 2. `holonomy-harmony` — the flagship example is misclassified by the tool's own data, and the topology numbers are wrong

**What it is.** A pure-Python (no runtime deps) music-theory library that applies constraint theory to chord progressions: circle-of-fifths holonomy, Roman-numeral parsing, modulation detection, a tonal graph, stability scoring, Ricci flow, and a topological-analysis module (Euler characteristic, Betti numbers, fundamental group, homology groups). 20 built-in progressions. **Published on PyPI** (`holonomy-harmony` 0.1.0, Forgemaster). This is a genuinely novel fleet artifact — constraint theory applied to harmony, with tests.

### The README's flagship example is wrong, by the tool's own numbers

The README's own quick-start output is **faithfully reproduced** (I ran it verbatim):

```
Holonomy:   -5
Winding:    0.08333333333333333
Type:       ProgressionType.MODULATION
Stability:  0.35
Chords:     8
```

for the **Pachelbel Canon in D major** — `['I','V','vi','iii','IV','I','IV','V']`. Now ask the tool what it thinks about those eight chords:

```
I   root=D  quality=maj  is_diatonic=True  implied=D major
V   root=A  quality=maj  is_diatonic=True  implied=D major
vi  root=B  quality=min  is_diatonic=True  implied=D major
iii root=F# quality=min  is_diatonic=True  implied=D major
IV  root=G  quality=maj  is_diatonic=True  implied=D major
I   root=D  quality=maj  is_diatonic=True  implied=D major
IV  root=G  quality=maj  is_diatonic=True  implied=D major
V   root=A  quality=maj  is_diatonic=True  implied=D major
-> 8/8 chords flagged diatonic, yet the progression is typed ProgressionType.MODULATION
```

**Every chord is diatonic in D major. The tool says it is a modulation with stability 0.35** — while the README's own text says *"A fully diatonic I-IV-V-I scores ~1.0"* (verified: I-IV-V-I → holonomy 0, winding 0, DIATONIC, stability **1.0**). The most diatonic progression in the repertoire is the one the flagship example prints, and it is typed as a modulation.

**The cause is structural, not a threshold.** `holonomy_harmony/cycle_checker.py:160`:

```python
ptype = _classify_from_signature(holonomy_semitones, max_dev, winding, steps)
```

```python
def _classify_from_signature(holonomy, max_dev, winding, steps) -> ProgressionType:
```

**The classifier's signature does not contain diatonicity.** The analyzer computes `is_diatonic` and `implied_key` for every chord, and then the progression-level verdict is a function of displacement statistics that *cannot see* them. The data is in the building; the decision is made in another room.

### The README's explanation of Giant Steps is backwards, and its reason is wrong

README:31 —

> *"A I-IV-V-I progression has holonomy 0 and winding number 0 — it's a closed walk. **Giant Steps has non-zero holonomy** because its major-third cycles don't close on the circle of fifths."*

Measured:

| progression | holonomy | winding | type | stability |
|---|---|---|---|---|
| `giant_steps` | **0** | **1.0** | CHROMATIC_MEDIANT | 0.377 |
| `coltrane_changes` | 0 | -1.0 | CHROMATIC_MEDIANT | 0.160 |
| `pachelbel_canon` | -5 | 0.0833 | MODULATION | 0.350 |
| `autumn_leaves` | -2 | 0.8333 | MODULATION | 0.175 |
| `I-IV-V-I` | 0 | 0.0 | DIATONIC | 1.0 |

Giant Steps has **holonomy 0** — the claim in the README is false. The non-zero quantity is the **winding number** (1.0), which the code's own docstring gets right (`cycle_checker.py:213`: *"Giant Steps has non-zero winding because each major-third jump carries you around the circle"*). And the stated *reason* is mathematically wrong: a major third is ±4 steps on the circle of fifths, so a three-chord major-third cycle sums to ±12 ≡ 0 (mod 12) — it **closes exactly**, one full turn. The README says the opposite.

### The topological invariants are computed with the wrong edge count

`holonomy_harmony/topology.py:171` builds the complex from the **directed** tonal graph:

```python
for j in self._graph.neighbors(i):
    edge_set.add((i, j))
```

`(i,j)` and `(j,i)` are distinct elements, so a reciprocal transition is counted **twice** in `E`. But every invariant formula is an **undirected** one: `χ = V − E + F` (`topology.py:206`) and `β₁ = E − V + β₀` (`topology.py:244`). And `compute_connected_components` is explicitly undirected — *"Find connected components via BFS on the undirected version of the graph"*. So β₀ is computed on the undirected graph while E, χ and β₁ are computed on the directed edge count.

Measured on the Pachelbel progression's own complex:

| | repo | truth (brute-force GF(2) homology) |
|---|---|---|
| E | 7 (directed) | 6 (undirected) |
| χ | **-1** | **0** |
| β₁ | **2** | **1** |
| β₀, β₂ | 1, 0 | 1, 0 |

`β₁` is off by the number of reciprocal transitions, and χ with it. The `SimplicialComplex` docstring even says *"1-simplices: **directed edges** (ordered pairs)"* — the data structure knows, the formulas do not. (I also brute-forced 606 random valid complexes: the `compute_betti` *heuristic* for β₂ agreed with truth on all 606, so the β₂ shortcut is fine — the error is the edge count, not the β₂ approximation.)

### And a type check that can never fail

`.github/workflows/ci.yml:28`:

```yaml
- name: Type check
  run: mypy src/ --ignore-missing-imports || true
```

**`src/` does not exist** — the package is `holonomy_harmony/` at the repo root. And `|| true` discards the exit code, so even mypy's "can't read file 'src/'" error cannot turn the job red. The step has **never type-checked a single line** of this codebase and is structurally incapable of failing. The CI shows 4 green runs.

### And a 150-test green suite that asserts none of it

`pytest` → **150 passed**. But grepping the suite: `grep -rn "progression_type" tests/` returns **one** hit, and it is `assert hasattr(result, "progression_type")`. **No test in the repo asserts a single progression verdict.** `test_pachelbel_canon` asserts `len(analysis.chords) == 8` and nothing else. Meanwhile `test_blues_12_bar` *does* assert `all(c.is_diatonic for c in analysis.chords)` — the chord-level fact is tested; the progression-level conclusion drawn from it is not.

CI is also 4-failure / 4-success across 8 runs, with the failures at *"Install dependencies"* (`pip install -e ".[dev]"`) skipping ruff, mypy and pytest in the same job.

**Why another agent should care.** This is the fleet's only "constraint theory applied to music" artifact, it is on PyPI, and it is a clean worked example of a defect class the fleet keeps re-finding: **the verdict is computed from a feature vector that omits the fact the system already computed.** The fix is small (pass the diatonicity count into the classifier) and the flagship example is the test that should have existed.

---

## 3. `cathedral-probe` — a first-rate adversarial review whose "issues logged" appendix logged zero issues

**What it is.** A Rust crate for spectral analysis of weighted component graphs: Laplacian eigenvalues, Fiedler value, Cheeger bounds, fragility index, component importance, bottleneck edges, effective resistance, Kirchhoff index, spectral embedding and clustering. It ships a **`TEST-DIARY.md`** — a 13 KB first-person review by "Aisha, ML Engineer (Fintech — Fraud Detection)", dated 2026-06-01, with a severity-ranked defect table, a worked fraud-detection example on a transaction network, real measured numbers, and a 2.5/5 verdict. **This is the best adversarial-review artifact I have found in the fleet.** It reads like a human who wanted the crate to be good, found it not to be, and wrote it all down.

**The diary's appendix is a receipt for a receipt.**

```
## Appendix: Issues Logged (for the repo)

| # | Severity | File | Description |
|---|----------|------|-------------|
| 1 | Major | `lib.rs:full_eigen()` | Private method — blocks access to eigenvectors |
| 2 | Major | `lib.rs:component_importance()` | Returns all zeros when graph has multiple connected components |
| 3 | Major | `lib.rs:bottlenecks()` | Same issue — disconnected graph → all zeros |
| 4 | Major | `lib.rs:fiedler_sensitivity()` | Same issue — zero sensitivity for all edges |
| 5 | Medium | `lib.rs:effective_resistance()` | Returns finite value for nodes in different components (should be INF) |
| 6 | Minor | `README.md` | Doesn't document ~50% of the public API |
| 7 | Minor | `lanczos_eigenvalues()` | Hardcoded RNG seed |
| 8 | Enhancement | `Cargo.toml` | Add `criterion` for benchmarks, add `rayon` optional |
```

The heading is **"Issues Logged (for the repo)"**. The repo has **0 issues and 0 pull requests, ever**:

```
GET /repos/SuperInstance/cathedral-probe/issues?state=all  ->  issues: 0  PRs: 0
```

**Not one of the eight was filed.** The table is the ledger of a filing ritual that never happened.

**And the defects it describes are still live, while the README still advertises them.**

```
lib.rs:285   let base_fiedler = self.fiedler_value();     # issue 2 — still there
lib.rs:312   let base = self.fiedler_value();              # issue 3 — still there
lib.rs:521   fn full_eigen(&self) -> (Vec<f64>, Vec<Vec<f64>>) {   # issue 1 — still PRIVATE
```

`fiedler_value()` is 0 for any disconnected graph, so `base − sub.fiedler_value()` is 0 for every edge, so `component_importance()` and `bottlenecks()` return **all zeros** for any graph with more than one component — i.e. most real microservice and dependency graphs. The diary says so explicitly: *"These three methods **effectively broken for production graphs**."* The README (lines 35–37) still advertises them:

> **Component importance** | How much removing each component hurts connectivity.
> **Bottleneck edges** | Edges whose removal most reduces connectivity.

One of the eight was in fact addressed: `fiedler_sensitivity()` (issue 4) no longer references a base Fiedler — it now returns squared eigenvector differences. **The diary was never updated to say so**, so the appendix is wrong in one direction (claims a fix never happened) while being wrong in the other (claims nothing was filed when nothing was). The diary is also **stale on its own transcript**: it records *"running 115 tests / test result: ok. 115 passed; 0 failed"*, and the crate now contains **120** `#[test]` functions.

CI is green (2/2) — the crate is fine. It is the *filing* that never happened, and the *README* that still sells two broken features.

**Why another agent should care.** This repo proves the fleet can produce a genuinely excellent adversarial review, and in the same breath proves the fleet's filing ritual is a table of prose. The diary's own §6 conclusion — *"**Score: 2.5 / 5 Stars**"* — was never acted on, and the README was never reconciled. A defect report with no issue, no commit, and no doc change is a *report*, not a *fix*; and the artifact that says "logged" is the one artifact you are most likely to trust.

---

## 4. `flux-policy-tester-rs` — published to crates.io on the day its own test suite was skipped

**What it is.** A Rust testing framework for FLUX bytecode agent policies: an assembler, a VM, a fuzzer, YAML-driven suites, and **real conservation-bound checks** (the fleet's `γ + η = C` law) — `test_conservation_bounds` genuinely collects violations and sets `passed = violations.is_empty()`. This is real work and it is published: **`flux-policy-tester` v0.1.0 and v0.1.1 are on crates.io**, both created 2026-07-12, 35 and 19 downloads.

**The badge is a picture of a passing test run.**

```
README.md:5   ![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
```

That is a **static** shields.io badge — a hardcoded image that says "tests passing" forever, with no workflow status behind it. (The crates.io badge on line 3 *is* dynamic; the tests badge is not.) Meanwhile:

**CI has never been green. 7 runs, 7 failures.** The step data for the last two runs:

```
2026-07-12 bf1e932 failure  job=test (stable)  [('Run cargo fmt --all -- --check','failure'),
                                                 ('Run cargo test --verbose','skipped'),
                                                 ('Run cargo clippy -- -D warnings','skipped')]
2026-07-12 bf1e932 failure  job=test (beta)    [same]
```

`cargo fmt` is the first step, so **the entire test suite is skipped** — and the suite is 33 `#[test]` functions in `tests/test_policy_tester.rs` (`src/lib.rs` has 0). Those 33 tests have **never executed in CI**. Earlier runs died at clippy with the same cascade. The workflow is `fmt → test → clippy`; a formatter is upstream of the test runner, so a whitespace nit hides the whole suite.

And the timing: the crates.io publishes and the red CI run are **the same day** — 2026-07-12. The repo's only commit is `bf1e932` *"docs: production-quality README…"*, and **its `Cargo.toml` still says `version = "0.1.0"` while v0.1.1 is on crates.io**. The published artifact and the repo tree disagree about what was published, and the tree that is on GitHub is the one whose CI was red.

**Why another agent should care.** This is the fleet's "enforce conservation bounds" tool, and it is the tool that would be pointed at the `γ + η = C` law. It is shipped, installable, and carrying a badge that asserts its tests pass. The suite is real and the conservation check is real — but nothing has ever run them, and the badge is a picture of a fact rather than the fact.

---

## 5. `flux-signatures` — every "confidence score" is a hardcoded constant, and the test suite certifies the constants

**What it is.** A Python module that statically analyses FLUX bytecode for patterns — loops, counters, accumulators, MAC, swaps, conditionals, stack-heaviness — emitting a `SignatureResult` with "confidence scores, complexity estimates, and cycle predictions". 75 tests, all passing.

**The confidence field carries no information.** `signatures.py` contains exactly six confidence values and **all six are literals**:

```
PatternType.LOOP, 0.95        PatternType.COUNTER, 0.9
PatternType.SWAP, 0.85        PatternType.CONDITIONAL, 0.85
PatternType.COPY, 0.7         PatternType.STACK_HEAVY, 0.7
```

Not one is computed from evidence. Every loop ever detected is 95% confident — whether it matched one backward jump or five. The README's feature table presents this as a statistic (*"Loop Detection | Identifies backward jumps (95% confidence)"*), and the intro says the tool *"produces a `SignatureResult` with confidence scores"*.

**And the test suite pins the constants rather than the meaning:**

```python
tests/test_signatures.py:275   assert loops[0].confidence == 0.95
tests/test_signatures.py:299   assert counters[0].confidence == 0.9
tests/test_signatures.py:350   assert swaps[0].confidence == 0.85
```

75 green tests certify that the hardcoded literals are the hardcoded literals. **A suite that asserts a constant is a tautology test** — it can only fail if someone edits the constant, which is exactly when you *want* the suite to stay green.

Two smaller notes: `signing.py`'s `AgentIdentity` has a `public_key` field that is **never used for verification** — `verify()` checks only the private key and the `previous_keys` history, so the "key pair" is a symmetric HMAC with a decorative hash-derived public key that no one can verify against. And `rotate_key()` never expires the old key, so a retired key verifies forever.

**Why another agent should care.** This is the static-analysis half of the FLUX toolchain, and "the detector's confidence is a per-rule constant" is a design choice that is fine **if labelled as a rule weight**. It is not labelled that way, and the test suite turns the label into a contract. Any fleet work that consumes these confidences as probabilities is consuming a lookup table.

---

## 6. Action list (owner-ready)

* **`dungeon-jev`** — `(seatsUsed[seed] ?? 0) < CAP_PER_SEED` at `src/run-v2.mjs:145`. One token. Then re-run the v2 wave; the committed P1/P2/P3 verdicts for wave 74-a are void because the seat never ran. Add a CI job that runs `node --test` and asserts `receipts/model-calls-v2.jsonl` is non-empty whenever the run is non-dry.
* **`dungeon-jev`** — make `run-v2.mjs` write the **nested** metric shape the scorer expects, and delete `receipts/v2-results-metrics.json`. A re-scorer using the runner's own output file currently gets `PENDING×3`.
* **`dungeon-jev`** — replace `const illegalExecuted = 0` with the computed `receiptedIllegal`, and give P3 a `vacuousIf` clause for "the model was never consulted" (the v1 claims already have that clause on P2/P3 — the v2 claims dropped it on the claim that actually needed it).
* **`dungeon-jev`** — change the fallback label. `"seat-cap-consumed"` when `attemptsTotal === 0` is a false statement in 110 receipt rows.
* **`holonomy-harmony`** — pass the diatonic-chord count into `_classify_from_signature` and add a `vacuousIf`-style guard; a progression whose chords are all `is_diatonic` in the home key cannot be `MODULATION`. Fix README:31 — Giant Steps has holonomy **0** and winding **1.0**, and major-third cycles *do* close (3 × 4 = 12 steps ≡ 0 mod 12).
* **`holonomy-harmony`** — build the complex with **undirected** edges (or de-duplicate `(i,j)`/`(j,i)`) before computing χ and β₁. Add a test that asserts a known complex's β₁.
* **`holonomy-harmony`** — `mypy src/ --ignore-missing-imports || true` → `mypy holonomy_harmony/ --ignore-missing-imports` (drop `|| true`). Point it at a directory that exists.
* **`holonomy-harmony`** — add a test asserting `analyze_progression(PROGRESSIONS["pachelbel_canon"]).holonomy.progression_type`. One assertion would have caught the flagship misclassification.
* **`cathedral-probe`** — file the eight issues. Or, if the diary is a point-in-time artifact, retitle the appendix to *"Issues Identified (not filed)"* and link the two still-live majors from the README's feature table.
* **`cathedral-probe`** — fix `component_importance()` (`lib.rs:285`) and `bottlenecks()` (`lib.rs:312`) for the disconnected case (per-component analysis, as the diary suggests), or mark both features as disconnected-unsafe in the README.
* **`flux-policy-tester-rs`** — delete the static "tests-passing" badge or point it at the real workflow status. Move `cargo fmt` to a **separate job** from `cargo test` so a whitespace nit cannot skip the suite. The crate is on crates.io; the suite has never run.
* **`flux-signatures`** — either compute the confidences or rename the field to `rule_weight` and say so in the README table. Stop asserting the constants in the test suite; assert the *detection*, not the number.

---

## 7. Method corrections (carry forward)

* **A counter initialised as `{}` is `undefined`, and `undefined < 1` is `false`.** Any per-key budget/counter gate written as `map[key] < CAP` is dead unless the map is pre-seeded. Grep for `const .* = {}` next to a `<` comparison against a cap. **Mutation-proof it: run the gate with a working mock endpoint and check the call counter moved.**
* **A receipt that names a cause is a claim about the cause.** `receipts/v2-runs.jsonl` said `fallback: "seat-cap-consumed"` on 110 rows while `attemptsTotal` was `0`. Read the *counter*, not the label.
* **A metric written as a literal is a tautology, even when a real counter sits next to it.** `const illegalExecuted = 0` next to `receiptedIllegal` — the scorer read the literal.
* **Two results files with the same values and different shapes is a reproducibility hole.** The runner writes one shape; the scorer needs another. Always re-score from *the file the producer wrote*.
* **A classifier's signature is its blindness.** `_classify_from_signature(holonomy, max_dev, winding, steps)` cannot see diatonicity, so a 8/8-diatonic progression is a modulation. When a system computes a fact and then classifies without it, find the fact and the verdict in the same trace and compare them.
* **"A `winding number`" that is not an integer is not a winding number** (it is `total/12` over an *open* path). Check the codomain of a quantity before trusting its name.
* **Directed edges in undirected invariant formulas.** `χ = V − E + F` and `β₁ = E − V + β₀` need an undirected E. If the complex stores ordered pairs, reciprocal edges are double-counted. Brute-force GF(2) homology over random valid complexes is a cheap, decisive check.
* **`mypy src/ || true` is a check that cannot fail, twice over** — the path does not exist *and* the error is swallowed. A type-check step must point at a real directory and must not be `|| true`.
* **"Issues Logged" is a claim, not a receipt.** `GET /repos/{owner}/{repo}/issues?state=all` is one call. If a diary's appendix says logged, the issues must be there.
* **A static shields.io badge is a picture.** `img.shields.io/badge/<label>-<message>-<color>` never changes. The dynamic form is `img.shields.io/github/actions/workflow/status/...`. A repo that also has a real badge on the line above makes the fake one easy to miss.
* **A formatter upstream of a test runner hides the whole suite.** `fmt → test → clippy` in one job means a whitespace nit skips every test. Put lint in its own job.
* **A crate on crates.io is a published artifact.** Check the crates.io version list against `Cargo.toml`'s `version` and against the CI conclusion on that sha. Publishing is a delivery event; it deserves the same scrutiny as a push.
* **A test that asserts a constant is a tautology test.** `assert loops[0].confidence == 0.95` certifies the literal, not the detector. Assert the *detection*; leave the constant alone.
* **A first-party review diary is the best artifact in a repo — and its appendix is the least checked.** The prose analysis in `cathedral-probe/TEST-DIARY.md` is excellent; the "logged" table under it was never filed. Verify the ledger part of every ledger-shaped appendix.
* **Positive control to copy, whole-hog: `dungeon-jev`'s `preregister@1`.** Seal the claims, commit the seal, run, score only what was sealed, refuse to score tampered claims. I mutated one byte and it went red with a named error; restoring it went green with the same verdict. The 6-file `batteryBinding` hashes all matched the working tree. A runner can fail; the *instrument* should not. Build more of these.

---

## 8. Environment notes

`/workspace` is a NAS mount at 100% quota (EDQUOT) — all scratch went to `/tmp`. PyPI's **resolver is blocked but the JSON API is not**: `https://pypi.org/pypi/<pkg>/json` → `files.pythonhosted.org` → hand-install wheels into a venv (pytest 9.1.1 + iniconfig + packaging + pluggy + exceptiongroup + pygments). `gh` is **not** installed — the REST API via `curl` + `GITHUB_TOKEN` covers everything, including `actions/runs` and `actions/jobs` (note: the runs endpoint returns `{"total_count":…,"workflow_runs":[…]}` on this host, not a bare array). `GIT_SSL_NO_VERIFY=1` is required for clone **and** push. node 22.19, python 3.11, gcc 12.2, dotnet 9.0.316 present; **no cargo/rustc/cmake/julia**, so the Rust and C++ repos in this report were **read, not run** — every Rust/C++ claim here is sourced to a line, not to an execution. The two repos I could execute (`holonomy-harmony`, `flux-signatures`) were run in full. `dungeon-jev` was executed under a mocked `api.typesafe.ai` endpoint with `globalThis.fetch` preloaded — the mock returns a well-formed 5-action answer, so a zero-call result cannot be blamed on the mock.
