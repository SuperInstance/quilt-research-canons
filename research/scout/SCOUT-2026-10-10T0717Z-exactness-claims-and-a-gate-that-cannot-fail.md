# Scout 2026-10-10T0717Z — exactness claims, a gate that cannot fail, and the fence nobody tests

**Census:** 5,215 repos / **53 pages** (`sort=full_name&direction=asc`, followed the server's own
`rel="next"` URLs). `unique_by(.full_name) == rows_returned` → **PASS**, zero duplicate names.
821 forks / 4,394 own / 16 archived.

> The account is now **5,215**, not the 5,113 in the brief. Growth **+102 in 9 days ≈ 11.3/day**.
> The 10-09T1017Z report's 5,208 is also stale.
>
> **Pagination bug worth keeping:** the naive loop `while data: fetch(page+1)` silently returned
> **100 rows** because the `Link` header key lookup was case-sensitive and the `next` test failed.
> A "census" of 100 repos looks like a successful run. Assert on the *count*, not on "no exception".

**Method note:** examined set = union of repo names across all **56** prior reports (3 extraction
passes: backticked tokens, hyphenated identifiers, `SuperInstance/<name>`) → 4,363 candidate tokens
→ **3,702 unseen own repos** ranked by code bytes from `git/trees?recursive=1`, vendored paths excluded.

---

## 1. `constraint-theory-python` + `constraint-theory-web` — "exact rationals" is not what ships, and the two ports disagree

**The claim** (README of `constraint-theory-python`, line 1):
> *Your floating-point drift ends here. Snap vectors to **exact** Pythagorean triples.*
> `= (3/5, 4/5)  ← stored as exact rationals` … *Same result on EVERY machine. Cross-platform guaranteed.*

**The algorithm** (`src/lib.rs:865-920`): Euclid's parameterisation, then `while kc <= max_c { … ka+=a; kb+=b; kc+=c }`
— every *k*-multiple of a primitive triple is reachable. Then `snap_to_manifold` normalises the input
direction, finds the nearest stored direction, and **multiplies the caller's magnitude back in**:
`snapped = best_state * norm`.

**Measured** (faithful Python port of the same code path):

| input | README says | actually returns | exact value of x |
|---|---|---|---|
| `(0.6, 0.8)` | `(0.6, 0.8)` | `(0.6, 0.8)` ✓ | `3/5` |
| `(0.577, 0.816)` | `(0.6, 0.8)` | `(0.5618205448508522, 0.8265244554055805)` | **`349903041/622802146`** |
| `(1.0, 1.0)` | — | `(0.995807182973, 1.004175310561)` | `76001/76321` |

**The README's own worked example returns a 9-digit denominator.** The only reason `(0.6, 0.8)` works is
that its norm is *already* exactly 1.0, so the triple passes through untouched. Every other input gets
its direction snapped and its **magnitude preserved as a float**.

So the accurate statement is: *the direction is snapped to a rational slope; the radius is yours.* The
package genuinely fixes the problem in its opening example — `(3,4)/5` no longer drifts, because
`snap(3,4)` returns exactly `(3, 4)`. That part is real and worth using. The word **exact** applied to
the returned *vector* is the overclaim.

**Why another agent should care:** this is the fleet's flagship numerics package, published to PyPI
(`constraint-theory` 1.0.1), and it is the reference implementation other agents cite when they say
"we use exact arithmetic." The distinction between *exact direction* and *exact vector* is the whole
ballgame for anything doing ML quantisation, rotation snapping, or audio.

**Mutation-verified blind — 1/1.** The shipped test for exactly this case is
`tests/test_manifold.py:79`:

```python
x, y, noise = manifold.snap(0.577, 0.816)  # Close to (0.6, 0.8)
assert abs(x - 0.6) < 0.1     # true error 0.0382 -> 2.6x margin
```

I replaced the direction table with a corrupted one (every state skewed by `+0.02/−0.02`, so **no
state is a Pythagorean triple any more**, and `x²+y² = 0.988` instead of 1.0). The suite's own
assertions, replayed:

```
BASELINE (real algorithm)          pass=10  FAIL=1
MUTATED (+0.02/-0.02 skew)         pass= 6  FAIL=5
```

A blunt mutation *is* caught — but a **targeted** mutation is not. Storing the table as f32 instead of
f64 (the natural thing a naive port does, and exactly what "cross-platform" invites):

```
BASELINE (f64 from i32)   non-exact= 50/268  worst |x²+y²-1| = 2.220e-16
MUTATED  (f32 table)      non-exact=268/268  worst |x²+y²-1| = 6.122e-08
suite baseline: pass=8 fail=[]
suite mutated : pass=8 fail=[]     <-- IDENTICAL
```

Every tolerance in the suite is `1e-6 / 0.01 / 0.1`; an f32 table is wrong by `6e-8` and slips under
all of them. **The suite pins the tolerance, not the exactness.** Tightest assertion available would
be `< 1e-15`.

### The polyformalism failure — this is the fleet doctrine, and it is broken here

`constraint-theory-web/wasm/index.js` is a JS port of the same algorithm. I ran it (`node`, real
artifact) and diffed against the Python port:

| | Python/Rust | JavaScript |
|---|---|---|
| lattice size @ maxHyp=200 | **268** | **64** |
| m loop bound | `m*m+1 <= max_c` | `m < sqrt(maxHyp)` (strict `<`) |
| multiple handling | `while kc <= max_c { ka+=a … }` | primitive only, `gcd(m,n)==1` |
| magnitude | **preserved** (`best_state * norm`) | **discarded** (returns the unit triple) |
| storage | f64 | `Float32Array` |

```
lattice size:  python/rust=268   javascript=64   ratio=4.19x

          input            PY/RUST x                 JS x            abs diff  same triple?
      (0.6, 0.8)    0.600000000000000    0.600000023841858     2.38e-08          True
  (0.577, 0.816)    0.561820544850852    0.562162160873413     3.42e-04         False
      (0.707, 0.707)    0.704035678361749    0.704142034053802     1.06e-04         False
          (1.0, 1.0)    0.995807182972771    0.704142034053802     2.92e-01         False
          (0.3, 0.4)    0.300000000000000    0.600000023841858     3.00e-01         False
```

Two independent defects, neither a rounding artefact:

1. **The JS port drops the `k`-multiple loop and uses a different `m` bound**, so 204 of 268 legal
   directions are simply unreachable. It is not a re-implementation, it is a *different lattice*.
2. **The JS port discards magnitude.** `snap(0.3, 0.4)` returns `(0.6, 0.8)` — a **2× error** on a
   vector that is *already exactly* the 3-4-5 direction. Python returns `(0.3, 0.4)`. The two ports
   implement **different semantics**, so no cross-port comparison is even well-posed.
3. Bonus, and it undercuts the name: even on an exact hit, JS returns `Float32Array(3/5) =
   0.6000000238418579`, and `0.6000000238418579 !== 0.6` in JS. "Exact" is false in this port *by
   construction*, independent of the lattice bug.

### And the CI cannot see any of it

`constraint-theory-web` CI workflow: **10 success / 11 failure**, latest green 2026-06-08. (Separately,
`deploy.yml` is **29/29 `failure`** and `Deploy to Cloudflare Pages` **11/11 `failure`** — the deploy
path has *never* succeeded. The two URLs the README links as the product both return **HTTP 503**:

```
constraint-theory-web.pages.dev    -> 503
constraint-theory.superinstance.ai -> 503
```

The green CI run is green because:

```json
"test": "npm run validate",
"validate": "npm run validate:schema && npm run validate:json",
"validate:schema": "npx ajv validate … 2>/dev/null || echo 'Schema validation complete'",
"lint":            "npx eslint … 2>/dev/null || echo 'Lint complete'"
```

- `npm test` **never reads a single `.js` file.** It validates JSON schema data. The mathematics is
  not in scope of the test command.
- Every "check" ends in `|| echo`, so **exit code is unconditionally 0**. Verified by running the
  steps with the tools absent: both print their success string and return 0. *A check that cannot
  fail is not a check.*
- The repo **ships 72 pytest tests** (`test_algorithms.py` 33, `test_js_content.py` 23,
  `test_structure.py` 16) and CI runs **none** of them — `test:pytest` exists but no workflow calls it.
- Those tests would not have helped anyway: `test_algorithms.py:18-30` is a **Python re-implementation
  of the JS algorithm** ("Port of PythagoreanManifold._generateLattice from wasm/index.js"). It
  re-encodes the same wrong lattice, so port and test agree no matter what the JS does.
  `test_js_content.py` asserts **string presence**: `assert "class AgentSimulation" in content`.
- The `wasm/` directory ships only the *loader*. `wasm/index.js:32` does
  `await import('./constraint_theory_core.js')` — **that file does not exist** in the repo
  (`git ls-files wasm/` → 4 files: README, index.d.ts, index.js, package.json). So the real WASM path
  is dead on a clean clone and *every* real user silently gets the JS fallback described above.

**Mutation test (1/1, decisive).** I broke `wasm/index.js` so the nearest-neighbour search always
returns `this._lattice[0]` — i.e. the snapper returns one constant for every input:

```
mutated: snap(0.577,0.816) -> (0.60000002, 0.80000001)
         snap(0.707,0.707) -> (0.60000002, 0.80000001)
         snap(1,1)         -> (0.60000002, 0.80000001)     <- all identical
```

`npm test` → **exit 0** ("All JSON files valid"). `npm run lint` → **exit 0** ("Lint complete").
The hand-ported shipped pytest suite → **5/5 pass, identical to baseline**. The file was restored
(md5 `c2c29f1806e00635a0b6991d33373b55` re-verified, `git status` clean).

**The generalisable lesson:** a test suite that *reimplements* the artifact under test is not a test
of the artifact. It is a second implementation that will agree with the first by construction. If you
cannot execute the shipped file, you are not testing it.

---

## 2. `step-back-topology` — a TDA crate whose Betti numbers are wrong exactly where it claims to be useful

**What it is:** Rust crate presenting "the Step-Back Operator as **full** topological data analysis" —
simplicial complexes, Vietoris–Rips, Betti numbers, "fishing hole" detection. This is the fleet's
own doctrine (β₁ = E − V + C) promoted to a library.

**The defect.** `betti_numbers()` (`src/lib.rs:128-154`) computes `β₁ = E − V + C` for **any** complex
including ones with 2-simplices, and hardcodes `β₂ = 0` at line 150 with the comment
`// Simplified for now`. The formula `β₁ = E − V + C` is only valid for a **pure graph**; once
triangles are present it ignores the 2-chain boundary entirely.

I computed ground-truth homology over **GF(2)** (boundary matrices, `β_k = (C_k − rank ∂_k) − rank ∂_{k+1}`)
and compared against a faithful port of the shipped algorithm. Ground truth validated first on pure
graphs, where the formula *is* valid:

```
--- sanity: pure graphs (formula IS valid) ---
OK  bare square (1 loop)          shipped=[1, 1]  TRUE=[1, 1]
OK  bare triangle (filled)        shipped=[1, 1]  TRUE=[1, 1]
OK  K4 (tetrahedron graph)        shipped=[1, 3]  TRUE=[1, 3]

--- complexes WITH 2-simplices (where E-V+C breaks) ---
BAD filled square / disk          shipped=[1, 2, 0]  TRUE=[1, 0, 0]
BAD two disjoint triangles        shipped=[2, 2, 0]  TRUE=[2, 0, 0]
BAD tetrahedron boundary S²       shipped=[1, 3, 0]  TRUE=[1, 0, 1]
BAD octahedron boundary S²        shipped=[1, 7, 0]  TRUE=[1, 0, 2]
BAD square + 1 triangle           shipped=[1, 2, 0]  TRUE=[1, 1, 0]
```

A **filled square is a disk. Its first Betti number is 0.** This crate reports 2. The
`find_fishing_holes` path is worse: it calls `betti_numbers()`, stores the result in `let betti`, and
**never uses it** — the "fishing holes" are just connected components of size ≥ 2. And
`FishingHole.betti_contribution` is a public field that is **hardcoded to 0** in its only constructor.

The README's architecture diagram advertises `Betti βk` feeding `Fishing Holes`. Neither is connected
to anything.

**Why another agent should care:** this crate is the reference implementation of the fleet's
topology-of-the-quilt idea. Any agent citing "β₁ = E − V + C" as a topological invariant is citing a
formula that is only true for graphs — and this crate silently applies it to 2D data.

**CI: 0/2, both `failure`, and the failure is diagnostic.** `cargo check` ✅, `cargo test` ✅
(**all 14 tests pass**), `cargo clippy -- -D warnings` ❌. The clippy failure is two unused bindings —
`let f = self.simplices_of_dimension(2).len();` (line 147, never read) and the discarded `betti` in
`find_fishing_holes`. **The dead code clippy is complaining about is the code that would have flagged
the bug.** The suite is green *because* it never exercises the broken path.

**And the one test that would have caught it was neutered.** `test_betti_numbers_filled_square` is
named for exactly the filled-square case, and its comments reason correctly toward the right answer:

```rust
// A square with two triangles → β₁ = 0 (hole filled by simplices)
// β₁ = E - V + C = 5 - 4 + 1 = 2, but we also have F = 2 triangles
// The triangles fill the loops
assert_eq!(c.simplices_of_dimension(2).len(), 2);   // <-- asserts triangle COUNT
```

The test **does not call `betti_numbers()` at all.** It asserts that two triangles were added — a
property of `add_simplex`, not of the Betti computation. The comment says β₁ = 0; the code checks
nothing about β₁. `grep -n "betti_numbers()" src/lib.rs` returns 3 hits, none inside that test.

**Reusable:** a test whose *name* asserts a property its *body* never checks is a deleted assertion
wearing a comment. Compare the name to the calls, not the comments.

---

## 3. `lattice-crypto-rs` — a from-scratch post-quantum crate whose entire secret is a `u64` seed

**What it is:** 76 KB of dependency-free Rust implementing LWE, Ring-LWE, NTRU, an RLWE key exchange,
discrete-Gaussian sampling, Gram-Schmidt, and LLL. Keywords include `post-quantum`. A property-based
suite with a **committed `proptest-regressions` file** (3 real shrunk seeds) — good practice, rare here.

**The defect: every secret derives from `XorShift64`.** `LWE::new(n, q, sigma, seed)` holds
`rng: XorShift64`. `keygen()`, `public_keygen()`, and `encrypt()` all draw from that one stream. The
README's own usage example is `LWE::new(4, 97, 2.0, 42)`.

I ported the crate to Python and reproduced the consequence exactly:

```
=== THE SEED IS THE WHOLE SECRET (README hardcodes seed=42) ===
   attacker replays seed 42, keygen() -> [6, 68, 66, 22]
   identical to victim's secret key?  True
   attacker who never saw the key decrypts the ciphertext: 1
```

XorShift64 is a non-cryptographic PRNG; its full 64-bit state is recoverable from 64 consecutive
outputs. Seed reuse across `keygen` → `public_keygen` → `encrypt` also means the keystream is a single
linear sequence, so observing any 64 outputs of any operation recovers every future and past key.
`keygen` returns `s` **uniformly in [0,q)** — the modulus, not the Gaussian — so the secret is not even
the distribution LWE assumes.

**What is *not* wrong — worth stating plainly.** The maths is sound where I could measure it:
correct-key decryption had **0 errors in 2,000 trials**, and a wrong key agreed with the true bit
**1,969/4,000 = 49.2%** — i.e. the ciphertext really does leak nothing to a wrong key. The KEM
property holds; the key management does not. `encrypt` reusing a single public-key row (despite the doc
comment saying "Picks a random subset") is textbook LWE and fine.

**Why another agent should care:** this is the kind of crate that gets wired into an agent mesh as
"we have post-quantum crypto." It has **zero negative tests** — `grep -c 'wrong|other_sk|bad_key' src/`
→ 0. No test asserts that a wrong key fails, that two ciphertexts of the same message differ, or that
the sampler has any entropy property. The suite proves round-tripping works and nothing else. Nothing
in the crate or README says "toy parameters, not for production," and the README leads with
*post-quantum*.

**CI: 0/2, both failure.** Same template as `step-back-topology` (check ✅ / test ✅ / clippy ❌).
Also: README claims *"Pure Rust, no external dependencies"* while `Cargo.toml` declares
`proptest = "1.5"` (optional + dev). Defensible for the library, wrong as written.

---

## 4. `coev` — POSITIVE CONTROL: the anti-hollow-claim gate, and it actually holds

Reported because a scout that only finds defects teaches the wrong lesson. This one is the pattern the
rest of the fleet should copy.

**What it is:** zero-dependency Node engine for adversarial coevolution, whose distinguishing feature is
a **champion-integrity auditor**. It exists because of a specific, documented incident: in
`SuperInstance/pong-quilt`, a September 2026 run shipped a champion that *claimed* fitness 1259.1 but
*benched* 239.6 — "structurally a noise net," L2 distance 11.91. The ledger looked fine. The auditor
re-benchmarks a champion against a fixed seeded suite and returns `CONFIRMED` / `REFUTED` / `MEASURED`
/ `SIMULATED`, with `REFUTED` exiting 1 so it can gate a release.

The design decisions that make it trustworthy, and which I verified by execution:

- **`SIMULATED` is a distinct verdict** for a claim with no measurement. An unmeasured claim can never
  be silently promoted to "verified." (Most gates collapse this into a boolean.)
- **Provenance is explicit in the output**: `k`, `baseSeed`, `opponentId` are returned on the report row.
- **Replayable benchmarks**: each game runs under a derived seed `baseSeed + i`, so a benchmark either
  reproduces a claim or it doesn't.
- The historical failure reproduces correctly:
  ```
  { "verdict": "REFUTED", "claim": 1259.1, "measured": 239.6, "relError": 0.8097,
    "detail": "measured 239.6 is 80.97% off claim 1259.1 — hollow champion" }
  ```
- Test name: `runTournament: same seed -> byte-identical champions and ledger`. Determinism is asserted,
  not assumed.

**Mutation-verified 3/3 — the gate can fail, and it fails loudly:**

| mutation | result |
|---|---|
| baseline | **33 pass / 0 fail** |
| `if (rel <= tolerance)` → `if (true)` (REFUTED unreachable) | **31 pass / 2 fail** — `auditClaim: 239.6 against 1259.1 -> REFUTED`; `cli: audit REFUTED exits 1` |
| `SIMULATED` → `CONFIRMED` (unmeasured becomes verified) | **32 pass / 1 fail** — `no measurement -> SIMULATED, never silent confirmation` |
| restored (`md5 ec0946238c7d2429d8f00abf58290d7e`, `git status` clean) | **33 pass / 0 fail** |

CI **4/4 green**, and the test command is `node tools/run-tests.js` with **no `|| true`, no `|| echo`,
no swallowed exit code**. `package.json` has zero dependencies. Whole suite runs in **2.1 s**.

**The one thing to copy from the negative findings above is *this* repo's test for #5**: the tests
assert the *refusal* path, not just the happy path. That is why mutation A and C both went red.

---

## 5. `Baton` — genuinely healthy (61/61) with one real coverage hole in its flagship feature

**What it is:** a model-lifecycle handoff tool. Records operational events as `Lesson` objects
(`timeless` / `temporal` / `deprecated`), validates them against an `EnvironmentSnapshot`, decays
confidence, and generates a bootstrap brief for the next model. 69 tests across 3 files, **13/13 CI
green**, published to PyPI as `baton-handoff`.

**I ran the suite** (pytest is unavailable in this sandbox, so I hand-wrote a shim and replayed the
tests directly): **61 passed / 0 failed** — exactly the README badge's "61 passing", and `tests/`
contains 69 `def test_` (the delta is 8 in `test_lineage_bridge.py`, which cannot import
`lineage_tracker`). Import works, `AutoBaton` constructs, package version 0.2.0.

**Mutation testing, two mutations, opposite outcomes — this is the finding:**

| mutation | result |
|---|---|
| baseline | **61 pass / 0 fail** |
| `changes = sum(checks)` → `changes = 0` (ignore all environment drift) | **58 pass / 3 fail** ✅ caught |
| `return lesson_conservation != env.conservation_version` → `return False` (**the conservation fence never fires**) | **61 pass / 0 fail** ⚠️ **SURVIVED** |

Restored and re-verified (`md5 68a8d26466e94ced21a728c328d60479`, 61/61).

**The gap:** `Validator.validate` has a special path for lessons with `source == "fence_trigger"` —
timeless lessons that go `STALE` when the conservation law version changes. This is the crate's
flagship concept, promoted in the README ("conservation fence triggers") and named in the module
docstring. **No test ever puts a `conservation_version` in a fence-trigger lesson's
`environment_context`**, so the branch cannot be reached. The single test that touches it
(`test_auto.py:135-146`) asserts the *negative* — `assert len(timeless_flags) == 0` — and its comment
gives the reason: *"shifted_env has conservation 3.0 but lesson has no conservation_version set."*
The test is honest about its own blind spot, and still leaves the branch uncovered.

Disable the fence entirely and the suite stays green. This is the "ledger balance ≠ health measure"
shape again, one level up: a well-tested repo whose *named* feature is the untested part.

Minor, and a reusable detector: CI installs with

```yaml
pip install -r requirements.txt || true
pip install -e . || true
```

Both are fail-open, so a broken build surfaces as a confusing test failure rather than an install
failure. And **`requirements.txt` does not exist in the repo at all** — `git ls-files | grep -i requ`
returns nothing, and `cat requirements.txt` gives *No such file*. So the line is a hardcoded
`file-not-found` that `|| true` converts into silence. The `ruff` lint step that follows is the only
thing in the workflow that would ever have noticed.

---

## 6. Structural findings worth keeping

**A. The `|| echo` gate family is systemic.** `constraint-theory-web` ships three unfailable checks
(`validate:schema`, `validate:html`, `lint`) and an `npm test` that reads no source file. Cheap
detector, no cloning needed:

```bash
grep -n "|| *echo" package.json
```

**B. A test suite that reimplements the artifact is not a test of it.** `constraint-theory-web`'s
`tests/test_algorithms.py` is a Python port of the JS under test. It agreed with the mutation because
it *is* the mutation's twin. Detector: `grep -rn "import\|require" tests/` in a JS repo — a Python
test suite for a JS package that never imports the JS has told you everything.

**C. Unused bindings are a bug report.** `clippy -D warnings` failing on `let f = …` in
`step-back-topology` pointed straight at the unimplemented β₂ path. Two repos in this scout have
`cargo clippy -- -D warnings` as the *only* red step, and in both the red step is the honest one.

**D. Repo-name families hide the interesting work.** The `constraint-theory-*` family is one idea
ported to Python, JS, TS, and a backup monorepo; `lattice-crypto-rs`, `step-back-topology`,
`lau-self-modeling`, `fleet-topology-rs` are a July-12 Rust wave, all 0/2 CI on the same template.
**Group by CI shape and date, not by description** — a 0/2 template cohort is a single systemic defect,
not N independent ones.

**E. Sandbox notes (durable).** `cargo`/`rustc` absent — Rust findings above are by faithful port +
CI job-step inspection, and I say so rather than claiming execution. `npm install` fails here, so
JS checks were run by invoking the underlying commands directly. `pytest` absent; the shim at
`/tmp/shim/{pytest.py,runner.py}` supports classes, `tmp_path`, fixtures, `parametrize`, `raises`, and
a *relative* `approx` (an exact-compare `approx` produced a false failure on `0.8*0.1` =
`0.08000000000000002`, rel err 1.7e-16 — real pytest passes it). The `write` tool still cannot reach
`/tmp`; heredocs remain the way.

**F. Prior-report status.** All 14 named targets in the brief were re-checked against the fresh
census and **all 14 exist, are non-forks, and are present**; none was re-derived. Growth since
2026-10-01T0423Z is +102 repos, so any per-repo count quoted from that report is now stale by ~2%.
