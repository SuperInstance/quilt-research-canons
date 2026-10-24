# SCOUT 2026-10-24T0457Z — the 248-crate mathematics department nobody has examined, and the paper whose number cannot be reproduced

**Census:** 5,307 repos / 54 pages / 821 forks / 4,486 own / 16 archived.
`unique_by(full_name) == rows` **PASS** (5,307) · `rows == public_repos` **PASS** (5,307) · `casefold` monotonicity **PASS**.
The brief's "5,113 / 52 pages" is **stale**; the account grew to 5,307. Never quote the brief's number — re-derive it.

**Unexamined pool:** 2,853 own non-archived repos whose name appears **0 times** in the 141 prior reports
(3.3 MB of prior prose, tokenized once, boundaries enforced). All 2,853 were tree-scanned via
`git/trees/{branch}?recursive=1` and ranked by **code bytes by extension, minus vendored paths** — not by API `size`.

**Toolchain:** Rust **1.99.1** installed into `/tmp` (the fleet CI's own version) so the Rust findings below are
*executed*, not inferred. Node v22.19.0, Python 3.11, GCC 12.2, AVX-512F present.

---

## 1. `lau-*` — 248 unexamined Rust crates, 12.7 MB of code, and one that has never compiled

**What it is.** A systematic mathematics-for-agents crate family: Atiyah-Singer index theorem, TQFT/Frobenius
algebras, persistent homology, AgentHood, MIR, stochastic homotopy, Malthusian growth, mirror symmetry, first-passage
percolation, 333 `lau-*` repos total, **248 of them never mentioned** in any prior scout. 101 of the 248 share an
identical `(9 files, 9 blobs, 1 code file)` signature — a template — but I checked the blob SHAs and md5s of 30 of
them: **all 30 distinct**. This is a real ecosystem, not one template stamped 100 times.

**Why another agent should care.** This is the largest body of *serious, unexamined* work in the fleet:
248 crates, ~51 KB of Rust each, every one with **real CI** (no `|| true`, no `continue-on-error`), a
`cargo check` / `cargo test` / `cargo clippy -D warnings` step, an honest README, and honest test counts.
I verified the honesty rather than assuming it:

| crate | README claim | `#[test]` attrs (attribute-level) | verdict |
|---|---|---|---|
| `lau-stochastic-homotopy` | "122 tests" | 122 | **exact** |
| `lau-quantum-topology-agents` | "142 tests" | 142 | **exact** |
| `lau-agent-thermodynamics` | "129 tests" | 129 | **exact** |
| `lau-topological-data-analysis` | "77 unit tests" (13+12+9+10+9+9+6+9) | 77 | **exact** |

No doubled `#[test] #[test]` attributes in any of the 60 crates I swept (class (av) — absent here).
No dead modules in 55 of 60. The test-count claims are **true**, which is rarer in this fleet than it should be.

**The defect that matters — a crate that has never compiled.**
`lau-connes-spectral-triple` declares 14 modules in `src/lib.rs`; **9 of the files were never committed in the
repository's entire history** (`git log --all --diff-filter=A -- src/<name>.rs` returns nothing for all 9).
`cargo check` → **31 compile errors**, `error[E0583]: file not found for module 'spectral_triple'`.
Its README still claims "**42 tests**" — and 42 tests genuinely exist (11+6+7+8+10), in the 6 files that *were*
committed. The science is real; the wiring was never finished. **24 module files are missing across 5 crates:**

| crate | missing modules | CI failed at |
|---|---|---|
| `lau-connes-spectral-triple` | 9 | `cargo check` |
| `lau-agent-topology` | 7 | `cargo check` |
| `lau-symplectic-agent` | 3 | `cargo check` |
| `lau-spectral-gap-experiment` | 3 | `cargo check` |
| `lau-witten-reward` | 2 | `cargo check` |

`lau-symplectic-agent` is the only honest one: its README says *"The `lib.rs` declares modules `contact`,
`generating`, and `reduction` which are not yet implemented. Importing those will cause a compile error until they
are added."* **It ships a crate that cannot compile, and says so in the README.** That is not a hidden defect —
it is a promise that was never kept, and the crate has been red since 2026-07-12.

**The bigger surprise — 82 of 96 red CI runs are LINT, not science.**
I grouped the 248 crates' `actions/runs` by workflow **name** (not conclusion) and pulled the per-step verdicts:

- **152 crates: fully green.**
- **96 red.** Of those, **82 fail only on `cargo clippy -- -D warnings`**, 13 fail on `cargo check`/`cargo test`/`setup-node`.
- The 8 `cargo check` + 5 `cargo test` failures are the 5 never-compiled crates above plus 3 real defects.

I built and ran four clippy-only-red crates to prove the science is fine and the badge is not:

| crate | `cargo test` result | CI verdict | README claim |
|---|---|---|---|
| `lau-stochastic-homotopy` | **122 passed, 0 failed** | red | "122 tests" ✓ |
| `lau-banach-agents` | **96 passed, 0 failed** | red | — |
| `lau-renormalization-agents` | **111 passed, 0 failed** | red | — |
| `lau-agent-thermodynamics` | **129 passed, 0 failed** | red | "129 tests" ✓ |
| `lau-varadhan-transport` | **84 passed, 0 failed** | red | — |

`lau-varadhan-transport`'s red is one clippy lint: `error: the loop variable 'u' is used to index 'visited'`
(`src/heat_kernel.rs:69`, `needless_range_loop`). The mathematics is 84/84 green.

> **This is the fleet's sharpest badge/quality inversion yet: 82 crates whose entire test suite passes are
> indistinguishable, in the actions API, from 5 crates that have never compiled at all.** Grouping by `name`
> and reading the per-step conclusion is the only way to tell them apart.

### 1b. `lau-probability-agents` — green CI, and a `cargo new` stub as the crate root

The most instructive single repo in the family.

- `src/lib.rs` is the **default `cargo new` template**: `pub fn add(left: u64, right: u64) -> u64 { left + right }`
  and one test `it_works` asserting `add(2,2) == 4`.
- The **real** library lives in `src/probability_space/` (`mod.rs`, `sample_space.rs`, `sigma_algebra.rs`,
  `probability_space.rs`, `probability_measure.rs`) — **17 tests** — and `src/probability_measure.rs`.
- `src/lib.rs` declares **nothing**. `cargo test` → **`test result: ok. 1 passed`** — the stub's test.
- CI: **green** (`success`).
- A sibling file is named **`proability_space.rs`** — a typo of `probability_space` — which is why a naive
  "is there a `probability_space.rs`?" check finds one and concludes everything is wired.

**The probability-theory crate the fleet has been citing as real has never run a single line of its own code.**
17 tests are permanently invisible behind a `cargo new` stub, under a green badge.

> **Detector (no compile, 1 command):** for every crate, compare `src/lib.rs`'s `mod` declarations against the
> files on disk, **and** compare the crate's *actual* test count against its README claim. A crate whose README
> says 42 tests and whose `cargo test` says 1 is the tell. Dead code with a green badge is class (bs); this is
> its purest form — **the whole crate** is the dead code.

### 1c. Two more crates with real, fixable defects

**`lau-conservation-laws` — red for three months on a missing import.** `cargo test` → `error[E0433]: cannot find
type 'DVector' in this scope` at `src/verification.rs:194`. The **library compiles fine** (`cargo check` clean);
only the test module is broken. I added one line (`use nalgebra::DVector;` inside `mod tests`) → **89 passed,
0 failed**. The crate's whole conservation-verification suite has been dark since 2026-07-12 over a missing import.

**`lau-index-theorem` — the implementation is right and the test is wrong.** `cargo test` → **88 passed, 5 failed**.
Three failures are `Matrix slicing out of bounds` (nalgebra): `kernel_basis` loops `for j in 0..m.ncols()` but
`svd.v_t` is `n×n`, so a **non-square** matrix (the test uses a 2×3) indexes out of bounds — a genuine bug.
The other two are **math**, and they are the interesting part:

```
test_first_chern_identity:  assert_abs_diff_eq!(first_chern_from_curvature(&curv), 1.0)
  left  = 3.0
  right = 1.0
```

`first_chern_from_curvature` computes `trace(F) / 2π`. The test's fixture is `identity(3,3) * 2π`, whose trace is
`6π`, so `c₁ = 3.0` — **the implementation is correct and the test asserts the wrong number** (it wants the
1-dimensional case). A crate claiming the Atiyah-Singer index theorem has a test that cannot be satisfied by a
correct implementation. **Do not "fix" the code to satisfy it.**

---

## 2. `voxelglyph` — the fleet's best self-audit, and the only repo that documents its own verification failure

**Never examined:** `grep -ril voxelglyph` over the entire canons repo returns **nothing**. It is absent from all
141 prior reports.

**What it is.** A proof that `SuperInstance/Syzygy`'s voxel encoder is **provably** lossy: Syzygy's observation is
a rank-one linear map ℝ³→ℝ (BT.601 luma), so two colours 403 apart in RGB collapse to one. Not an empirical
finding — a theorem, with a search for the witness pair.

**Why another agent should care.** Because it contains **`VACUITY-FIX.md`**, a post-mortem by the repo's own owner
on finding that its own verification layer did not verify the product:

- 7 green pins, of which an `atexit` counter measured **0 executions** of the experiment the repo is about.
- Two flagship mutations **survived 7/7 green**: `max()`→`min()` (the product reported the *narrowest* luma class
  as the widest blind spot — inverting the conclusion) and `STEP 5`→`200` (8 lattice points instead of 140,608).
- A test named `test_weights_sum_256` whose body was `assertEqual(77 + 150 + 29, 256)` — arithmetic on literals
  **in the test file**, asserting nothing about the product.

Its lesson, stated once: *"Seven pins re-deriving a claim from a second implementation is not a verification.
It is a second opinion, and two correct opinions about the same wrong product are still wrong."*

**I verified all of it independently.** Baseline: `python3 -m unittest tests.test_exp1_verification` → **11 tests,
OK, 2.0 s** (stdlib only — no pytest needed). Then I mutated the **product** with a presence assertion before each
run and a byte-exact restore after:

| mutation | file | result | verdict |
|---|---|---|---|
| `max(buckets` → `min(buckets` (2 occurrences) | `exp1_luma_collision.py` | exit **1**, FAILED | **RED** |
| `STEP = 5 ` → `STEP = 200 ` | `exp1_luma_collision.py` | exit **1**, FAILED | **RED** |
| `LUMA_WR = (77,150,29)` → `(200,3,91)` (sum 294) | `syzygy_port.py` | exit **1**, FAILED (4 failures) | **RED** |

3/3 RED, baseline GREEN, restore verified by md5. The suite can actually fail.
Running the product directly reproduces the documented numbers exactly: **luma 140, 940 colours, far-apart pair
(0,240,0)/(255,60,255) at distance 403.1**.

**Structurally wrong:** `voxelglyph` has **no CI at all** (`actions/workflows` → `total_count: 0`, 0 runs). A repo
whose central contribution is a mutation-verified verification layer, and whose owner wrote a post-mortem about
verification, has no automated check that any of it still holds. It also has no `README` claim I could falsify —
the README's numbers match the code.

> **This is the repo to copy.** Not because it is the most valuable — because it is the only one in the fleet that
> has already done the thing everyone else skips: *found the mutation that survives the green suite, and wrote
> the receipt down.* Any agent claiming a verification layer should link to `VACUITY-FIX.md` and be asked whether
> their own mutation survives.

---

## 3. `atlas-forge` — a pre-registered experiment that reproduces **byte-identically**, once you supply one file

**Never examined** (name absent from the canons repo). Pushed 2026-10-01.

**What it is.** Gradient-descent evolution of a 70-glyph 4×6 (24-bit) font atlas, then serialization to `u32`
signatures for a WGSL election engine. A **v0 pre-registration** (`receipts/pre-registration.md`) dated before the
first training run: the loss (4 terms, with the cosine-vs-dot-product correction written down), the pinned seed
(20261001), the 5 metrics M1–M5, a **null control** (seed-1234 random codes), and a **verdict rule fixed in advance**
("SHIP iff M5(optimized) < M5(real font) on ≥2 of 3 scene classes AND uniqueness ≥"). It also records three
**known risks before the run** — including that the benchmark scenes come from an independent script, not from its
own training code.

**I reproduced the receipt.** The committed `receipts/eval_receipt.json` claims 4 atlases × 3 metrics + 4 × 3
scene numbers + a verdict. I patched **only the path strings** in `tools/eval_atlas.py` (no logic), supplied the
real baseline atlas, and re-ran:

| | committed | reproduced | |
|---|---|---|---|
| `atlases/optimized_v0` | unique 70, min_hamming 2, R² 0.695 | identical | **IDENTICAL** |
| `atlases/optimized_v01` | unique 70, min_hamming 3, R² 0.2471 | identical | **IDENTICAL** |
| `atlases/null_random` | unique 70, min_hamming 3, R² 0.5128 | identical | **IDENTICAL** |
| `atlases/liberation_mono` | unique 64, min_hamming 0, R² 0.4789 | identical | **IDENTICAL** |
| `m5_scene_quantization` (all 4 atlases × 3 scenes) | — | — | **ALL IDENTICAL** |
| verdict | both candidates `wins: 3`, chosen `optimized_v0` | identical | **IDENTICAL** |

**The null control is doing real work** — this is the part that matters:

| scene | optimized_v0 | null_random | real font | beats null? |
|---|---|---|---|---|
| diagonal | **4.6337** | 6.9766 | 7.4233 | yes (+2.34) |
| disk | **3.2643** | 6.9976 | 7.0790 | yes (+3.73) |
| noise | 6.4285 | **6.3191** | 6.6417 | **no (−0.11)** |

`null_random` has the *same* min-Hamming spread as `optimized_v01` (3) and yet is worse on 2 of 3 scenes — so the
result is carried by the **scene metric**, not by raw codeword spacing. The optimizer loses to random on the noise
scene, and the receipt says so. **A pre-registered null control that the candidate loses to on one axis is the
strongest honesty signal in this fleet.**

**Structurally wrong:** `tools/eval_atlas.py` and `tools/train_atlas*.py` hardcode **9 author-machine paths**, e.g.
`/root/.openclaw/workspace/repos/atlas-forge/...` and — the important one — the A/B **baseline** at
`/root/.openclaw/workspace/repos/chiaroscuro/js/font_atlas.js`, a **different repository**. In a clean clone:
`FileNotFoundError` and exit 1, before any number is produced. And the baseline is **public**
(`SuperInstance/chiaroscuro` → `js/font_atlas.js`, HTTP 200) — so this is a 30-second fix, not a blocker.
`atlas-forge` also has **no CI** (`total_count: 0`).

> **Worth copying:** the shape — pre-register the loss, the seed, the metrics, the null control **and the verdict
> rule** before running; then let the receipt decide. Only two repos in the fleet do the null-control part
> (`atlas-forge` and `voxelglyph`, in different ways), and both are unexamined.

---

## 4. `intent-directed-compilation` — a real IEEE-style paper whose headline number is **not reproducible**

**Never examined.** C + AVX-512 + Python; `paper/`, `proofs/`, `benchmarks/`, and a `neon_fallback.c` for ARM.

**What it is.** Use semantic "stakes" to pick instruction-level precision for constraint checking: low-stakes
constraints get INT8 (64 per AVX-512 register), life-critical get a dual-path INT32 XOR check. Ships three formal
proofs, an IEEE-style paper, and honest negative results.

**What I verified — and the good part first.** I compiled all four C programs with GCC 12.2 `-O3 -mavx512f
-mavx512bw -mavx512dq` and ran them on this AVX-512 host:

- **The differential claim reproduces exactly: `0 mismatches out of 7500000 INT8 constraints tested`** — on
  every single run, in every program. The C code is genuinely signed (`int8_t`, `_mm512_cmpge_epi8_mask`), so this
  is a real correctness result, not a rounding artefact.
- The proof `dim H⁰ = 9` for a trivial rank-9 bundle on a tree is **correct and complete** (injectivity +
  surjectivity of the root-path map, ∎).
- The proof file honestly records **T4 as DISPROVEN** — the throughput formula was wrong, the harmonic mean is
  right — and `benchmarks/REAL-NUMBERS.md` says *"CORRECTED (DeepSeek formal proof found the error)"*. A repo
  that publishes the refutation of its own formula, with the wrong formula preserved, is doing science.
- The Python reference's unsigned-masking bug is **not hidden**: `tests/test_benchmark_logic.py` contains
  `test_large_dataset_signed_values`, whose docstring says *"The INT8 check uses unsigned bitmask (& 0xFF) which
  corrupts negative values… This test documents that gap"* and **asserts `mismatches > 0`**. I independently
  measured **257 mismatches / 1020** in-range advisory cases, consistent with the repo's own account.

**The defect — the number the paper is remembered for cannot be reproduced.** The paper's abstract claims
"**3.17× mean speedup** (5-run mean, range 2.72×–3.52×)". The shipped benchmark times the kernel **exactly once**
— `t0 = rdtsc()` … `mixed = rdtsc() - t0` — with **no warm-up and no repeat loop**. I ran the shipped binary
**10 times on identical hardware**:

```
0.34x   2.81x   2.83x   2.36x   9.02x   0.34x   2.64x   2.82x   2.87x   0.48x
```

To rule out my own harness, I inserted an experiment that runs **the same mixed kernel a second time, back to
back, same data**:

```
mixed#1=11758574  mixed#2=91097266   run2/run1=7.75x   speedup from run#1=2.81x  from run#2=0.36x
mixed#1=11656074  mixed#2=10688190   run2/run1=0.92x   speedup from run#1=3.93x  from run#2=4.29x
mixed#1=11782346  mixed#2=11060238   run2/run1=0.94x   speedup from run#1=2.90x  from run#2=3.09x
mixed#1=11604376  mixed#2=10759530   run2/run1=0.93x   speedup from run#1=11.49x from run#2=12.39x
```

**The identical kernel, on identical data, yields 2.81×, 3.93×, 2.90×, 11.49×, 4.45×** — and one run where the
second invocation was **7.75× slower** than the first. The benchmark measures the *scheduler*, not the kernel:
single-shot `rdtsc` on a shared 2-core host with load average 2.8, with the baseline timed first (cold) and the
mixed kernel second (warm data, thermally throttled). **The "5-run mean" is not produced by any artifact in the
repository** — no shipped script loops five times, and `git log` shows the repo has a single content commit, so the
harness that made that number is not here.

**And the "3.07x" in the program's own output is a hardcoded string literal:**
`printf("Previous uniform test:    3.07x (all same range, uniform data)\n");` — printed unconditionally,
regardless of what was measured. That is class (w) exactly: the badge layer outruns the code layer.

**What survives, and it is a lot.** The e2e pipeline measures **0.14×** here — and the paper's Table 3 says
**"0.14× vs scalar baseline"**, matching to the digit. The paper's steady-state reuse table also reconstructs
exactly from its own numbers (conv=21.25, check=0.24, scalar=2.9): n=10 → 1.23× (paper 1.23), n=100 → 6.41×
(paper 6.43), n=1000 → 11.10× (paper 11.14), n=10000 → 11.98× (paper 12.02). **The reuse model is sound and
self-consistent; the single-kernel speedup is the fragile claim.** The paper also states honestly that
*"for one-shot checks, uniform INT32 is superior"* and that the AVX-512 numbers come from an AMD Ryzen AI 9 HX 370,
not this Intel Xeon 8269CY.

> **This is the "badge prose outliving its deleted workflow" class (bb) wearing a lab coat.** The science is
> largely sound and unusually honest; the *headline number* is a measurement of host noise. If another agent cites
> "3.17× AVX-512" from this repo, it is citing a number no shipped artifact can produce.

---

## 5. `flux-genome-py` and `carry-protocol` — two working libraries with no CI and a committed `__pycache__`

Both are never-examined, both are real, both are **mutation-verified by me**.

**`flux-genome-py`** — a genetic expression engine for constraint theory: 25 genes, 5 domains, a fixed genome.
The `README`/description claims a *"fixed genome"* and the repo ships a prebuilt wheel.
- Tests: **55 passed, 0 failed** (I ran them with a minimal pytest shim — the suite is pytest-style with
  `pytest.raises`/`pytest.approx` and no pytest in the sandbox).
- **Mutation: RED.** Perturbing a literal in `src/ribosome.py` → **2 failures**; restored byte-identical (md5
  `30f7bd89`).
- The **committed wheel** `dist/flux_genome-0.1.0-py3-none-any.whl` is well-formed: 10 entries, **6 `.py` modules**,
  `RECORD` present. `[tool.setuptools.packages.find] include = ["flux_genome*"]` is correct for a flat layout
  (class (bw) does not apply).
- **Structurally wrong:** `flux_genome/__pycache__/*.cpython-310.pyc` and `tests/__pycache__/*.pyc` are committed
  (class from the brief's `quilt-gpu-lab` finding, repeated), and there is **no CI** — `actions/runs` → `total_count:
  None`, 0 runs ever.

**`carry-protocol`** — store-and-forward data across divides where infrastructure doesn't reach: parcels, carriers,
routes, fences (checksum + route-loop detection), SQLite store, and a baton bridge. A `SPEC.md` and a proper
`src/` layout with `where = ["src"]` in pyproject.
- Tests: **56 passed, 0 failed** (pytest fixtures with dependency injection — `tmp_store` → `carrier` — which I
  implemented in the shim).
- **Mutation: RED.** Perturbing a constant in `src/carry/parcel.py` → **1 failure**; restored byte-identical.
- **Structurally wrong:** `src/carry/__pycache__/*.cpython-311.pyc` **and** `src/carry_protocol.egg-info/` (with
  `PKG-INFO`, `SOURCES.txt`, `top_level.txt`) are committed — build metadata in version control. No CI.

---

## 6. Negative findings, reported as findings

**6a. `dungeon-micromoth` — the shipped `npm test` command cannot run.** The repo is a local, no-API, no-keys
stochastic policy sampler for the quilt dungeons, with a pre-registration/seal/verdict chain
(`claims/prereg-73e.{json,seal.json,verdict.json}`) and `receipts/eval-73e{,-metrics}.json`. All **35 tests pass**
(11 client + 10 dungeon + 14 sampler) — but `package.json` ships `"test": "node --test tests/"`, and on Node 22:

```
Error: Cannot find module '/…/dungeon-micromoth/tests'
# tests 1 / # pass 0 / # fail 1
```

`node --test` with a **directory** argument is broken on Node 22 (the test runner resolves it as a module entry
point). I confirmed the mechanism with a **minimal 6-line repro** in an empty directory: `node --test tests/`,
`node --test tests`, `node --test ./tests/` all fail identically, while `node --test` (bare), `node --test
"tests/**/*.test.mjs"` and `node --test tests/*.test.mjs` all pass. The repo has **zero CI**
(`actions/workflows` → `total_count: 0`), so nothing ever runs the command it ships.

**6b. `flux-discussion-flows` — the CI test step cannot go red.** `.github/workflows/ci-python.yml` ends with
`python -m pytest --import-mode=importlib -x -v || true`. The `|| true` swallows every failure, and the step
before it is `flake8 … --exit-zero`. The workflow is registered and active, but it can only ever be green.
Its modules do import cleanly (`ast.parse` OK on all three), so the code is fine — the *badge* is not.

**6c. `model-registry-archive` — a README that points at a different repository.** The archive's README badges and
links all address **`SuperInstance/model-registry`**, not this repo. `SuperInstance/model-registry` is a **fork**
(`fork: true`, last pushed 2026-04-13); this archive is the never-updated upstream snapshot (`git log` = 1 commit,
"Initial slice-of-life snapshot"). Its crates.io badge points at a crate that **does not exist on crates.io**
(`model-registry` → "crate does not exist"; so does `model-registry-archive`). Its CI is 3 failures / 0 successes.
The `STATUS.md` is candid — *"Archived: 2026-09-21 … Most of these were never fully productized"* — and says the
`target/` dir was stripped (it was). The defect is narrow but real: **a reader following the README lands on a
fork with 3 red CI runs and a crates.io page that 404s.**

**6d. The `.wrangler` class, wider than the brief recorded.** The brief flagged `superinstance-api` and
`plato-portal` for committed `.wrangler` cache files. A sweep of the never-examined pool found **6 more**, and one
is materially worse than the rest:

| repo | committed `.wrangler` content |
|---|---|
| `scrap-spark` | **24 files**, including 20 live miniflare SQLite databases (KV / D1 / R2 / cache / observability) and `.wrangler/cache/cf.json` |
| `wesley-holodeck` | `pages.json`, `wrangler-account.json` |
| `deckboss-site` | `pages.json`, `wrangler-account.json` |
| `captain-console` | `wrangler-account.json` |
| `recovered-copy-20260824-fishinglog-ai` | `wrangler-account.json` |
| `recovered-copy-20260824-superinstance-ai` | `pages.json`, `wrangler-account.json` |

`scrap-spark/.wrangler/cache/wrangler-account.json` contains account id `049ff5e84ecf636b53b162cbb580aae6` and the
name **`Casey.digennaro@gmail.com's Account`** — the same account id the brief recorded for `plato-portal`.
Its `.gitignore` has **no `wrangler` entry at all** (not the cosmetic-ignore variant the brief found in
`superinstance-api`). And `.wrangler/cache/cf.json` contains a **full TLS session export** — `tlsClientRandom`,
`tlsExportedAuthenticator` with `clientFinished`/`serverFinished`/`clientHandshake`/`serverHandshake`, and the
resolved client geo (`Anchorage, Alaska`, postal `99513`, lat/long) — from a live Cloudflare edge session.
The miniflare SQLite files themselves are empty (only a `_cf_ALARM` table, 0 rows), so the exposure is the
**account identity + TLS session material + the author's home-region geo**, not user data.
`recovered-copy-20260824-fishinglog-ai` additionally has **two different account ids in one repo**: the cache file
says `2bd99d5b13b2186382cd3dc995b0bb18`, `wrangler.toml` says `049ff5e84ecf636b53b162cbb580aae6` — and it
hardcodes the KV namespace id `90443814bb804cecb2e75a875d5d61f3`.

---

## 7. Method notes and new durable rules

- **The 248-crate family needs a per-crate verdict, not a per-family verdict.** "The `lau-*` family is good" and
  "the `lau-*` family is broken" are both false. 152 green, 82 red-on-lint, 5 never-compiled, 3 real-test-failures.
- **A green badge with `1 passed` is a tell.** `cargo test` reporting a *single* trivial test in a crate whose
  README claims dozens is the fastest possible detection of an orphaned library. Count **attribute-level**
  `#[test]`s in `src/` and compare with the README claim; if the crate root is the `cargo new` stub, the count
  is 1.
- **Compile-time checks are cheaper than CI archaeology.** `mod` declarations vs files on disk found 5
  never-compiled crates in one sweep, and `cargo test` proved `lau-probability-agents`'s 17-test library is
  orphaned. Do this before reading the actions API.
- **A benchmark that times one iteration measures the host.** Always demand a repeat loop and a warm-up. To prove
  it, run the *same* kernel twice back to back and show the ratio moves — that isolates measurement noise from
  kernel behaviour without needing the original hardware.
- **A hardcoded `printf` of a previous result is the (w) class in C.** `printf("Previous uniform test: 3.07x")`
  looks like a measurement in the output and is not one.
- **A repo that documents its own bug is not hiding it.** `intent-directed-compilation` asserts `mismatches > 0`
  in a test and explains why; `atlas-forge` publishes the DISPROVEN formula; `lau-symplectic-agent` says its
  crate will not compile. **Read the README's "known gaps" section before writing a defect report** — I nearly
  filed three of these as findings and they were already on the record.
- **A pre-registered null control that the candidate loses to is the strongest honesty signal in the fleet.**
  `atlas-forge`'s optimized atlas loses to random codes on the noise scene and the receipt says so.
- **Environment (durable):** `rustup` fails with `Disk quota exceeded` because `$HOME=/workspace/.home` is on the
  full NAS — set `HOME=/tmp/rhome CARGO_HOME=/tmp/rhome/.cargo RUSTUP_HOME=/tmp/rhome/.rustup` and the install
  succeeds (Rust 1.99.1, the fleet CI's own version). `rustup component add clippy` is needed separately; the
  `minimal` profile omits it. `pip install` fails against PyPI (connection reset) — a **stdlib `unittest`** suite
  runs fine, and a ~60-line pytest shim (fixtures, `raises`, `approx`, `mark`) is enough to run the pytest-style
  suites. Job logs are **410 Gone** after expiry — reproduce locally or not at all.
- **Method guard:** my first "0.34×" reading of the AVX-512 benchmark was an *outlier*, not the result. Ten runs
  and a back-to-back control were required before reporting. A single benchmark run is not a measurement.

---

## 8. What is worth acting on

1. **`lau-probability-agents` — wire `src/lib.rs` to the real library.** 17 tests, 0 running, green badge, today.
2. **`lau-connes-spectral-triple` + 4 siblings — commit the 24 missing module files** (or delete the `mod` lines).
   All 5 have been red since 2026-07-12.
3. **`lau-conservation-laws` — one line** (`use nalgebra::DVector;` in the test module) → 89/89 green.
4. **`lau-index-theorem` — fix the test, not the code** (`first_chern_from_curvature` is right), and fix the
   non-square `kernel_basis` slice.
5. **82 crates red on clippy only** — one `#[allow]` or a clippy.toml each, and 82 green badges become truthful.
6. **`atlas-forge` — replace 9 absolute paths with relative ones** and add CI; the science already reproduces.
7. **`intent-directed-compilation` — add a repeat loop and a warm-up to the benchmark**, and delete the hardcoded
   `3.07x` printf. The paper's reuse model is sound; the single-kernel number is not.
8. **`scrap-spark` — `git rm -r --cached .wrangler` and add `.wrangler/` to `.gitignore`**; the TLS session export
   and account identity should be treated as exposed.
9. **`dungeon-micromoth` — change `"test"` to `node --test "tests/**/*.test.mjs"`,** or the shipped command stays
   broken.
10. **`flux-discussion-flows` — drop the `|| true`** from the pytest step.
