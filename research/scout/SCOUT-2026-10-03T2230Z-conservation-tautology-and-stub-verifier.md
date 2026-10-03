# SCOUT 2026-10-03T2230Z — A conservation law that cannot be violated, a "certifiable" compiler whose verifier is a stub, and a CI that runs `|| true`

Scout of the SuperInstance fleet for substance nobody has examined. Every claim below was
executed, not inferred. Six items, ranked by surprise. Three are POSITIVE findings — real,
mutation-verified gates — because a scout that only finds defects teaches the wrong lesson.

## Census (re-derived, never hardcoded)

| fact | value |
|---|---|
| pages, `sort=full_name&direction=asc` | **52** (51×100 + terminal 63; page 53 = 0 rows) |
| rows returned / unique `full_name` | 5,163 / 5,163 — **ASSERT PASS** |
| forks (filtered before ranking) | 819 |
| own work | 4,344 |
| own repos never named in any of the 36 prior `research/scout/*.md` | **4,017** |

Grew from 5,161 (1917Z scout) to 5,163 two hours later. All 15 named prior targets survive
the fork filter (`fork: False`), so the prior findings stand.

Ranking used `git/trees/HEAD?recursive=1` blob bytes with
`node_modules/ vendor/ target/ dist/ build/ __pycache__/ .zig-cache/ zig-out/ …` stripped —
**not** API `size`. That distinction was load-bearing: `native-conservation-core` reports
`api=1MB` but **1.02 MB of its "code" is 3 committed ELF binaries**; strip binaries and it is
a ~60 KB C library. Ranking by API size alone would have put a build-artifact dump near the top.

---

## 1. `native-conservation-core` — the conservation law is an identity, so the audit that "verifies" it cannot fail

> **Scope honesty:** "unfalsifiable gate" is a class already covered (`SCOUT-2026-10-03T1320Z`,
> `SCOUT-2026-10-03T1917Z`). This is a **new instance, and a nastier one** — the tautology is
> in the *physics*, not in a test helper.

The repo bills itself as a "bulletproof C/CUDA implementation of the conservation law γ + η = C",
shipped as a lock-free SPSC ring buffer with a CUDA ternary-MAC kernel. It is the C-level anchor
for the fleet-wide `γ + η = C` claim, so its audit function carries real weight.

**What is actually there (clean clone, x86-64 Linux):**

- `src/conservation_core.c`, `src/ternary_alu.c`, `src/ternary_mac_kernel.cu`, plus a ctypes
  Python binding and a **real 28-test pytest suite** (`python/test_conservation.py`,
  classes `TestCompute`, `TestClosedForm`, `TestCancellation50`, `TestMonteCarlo`,
  `TestRingBuffer`, `TestAudit`, `TestNumpyInterface`, `TestBenchmark`).
- 16 tracked blobs. Genuinely careful work: `memory_order_acquire/release`, 64-byte cache-line
  padding to kill false sharing, hand-written `ctypes` struct-layout tests asserting
  `sizeof(conservation_state)==24` and exact field offsets.

**The defect — `src/conservation_core.c:50-52`:**

```c
state.gamma = gamma_sum / (double)n;
state.eta   = eta_sum   / (double)n;
state.C     = state.gamma + state.eta;   // C is DEFINED as the sum
```

and the audit at line 144:

```c
double residual = fabs(state->gamma + state->eta - state->C);   // ≡ 0 always
```

`C` is defined as `γ + η`, so `|γ + η − C|` is **identically zero for every possible input**.
The audit cannot fail by construction. The author appears to know this — `test_conservation.py:271`
carries the comment `# identity always holds exactly` — and asserts `passed` anyway.

**Verified by mutation (the only test that matters):**

| mutation | expected | result |
|---|---|---|
| A: corrupt `eta_sum += … * 1.15` (real signal corruption) | RED | **RED — 25/28, 3 failures, exit 1** |
| B: `state.C = 1.0;` — hardcode C to a constant, falsifying it | RED | **GREEN — 28/28, exit 0** |

Mutation A proves the suite genuinely exercises the computation. Mutation B proves the
**audit is unfalsifiable**: `C` can be replaced with an arbitrary lie and every test still passes.
Restoring returns 28/28 green; `git status` clean.

**Why another agent should care:** this is the C anchor of a conservation law that recurs
across the fleet (Python, JS, this C core). The γ/η *arithmetic* is well tested. The
**identity check that gives the law its name is a tautology** — it is a restatement of the
assignment, not evidence. Any downstream claim of the form "the audit passed, therefore the
conservation law holds" is circular. The honest version of this test would perturb `C`
independently of `γ+η` and assert they *disagree* when the model is wrong.

**Also structurally wrong (3 independent issues):**

1. **Committed build artifacts.** `benchmarks/ternary_mac` (864 KB), `ternary_alu_test` (29 KB),
   `conservation_bench` (21 KB) are tracked **x86-64 ELF executables**. `.gitignore` lists
   `benchmarks/` and `git check-ignore` confirms the rule is live — the binaries predate the rule
   and were never `git rm --cached`'d. The classic cosmetic-ignore case, same shape as
   `superinstance-api`'s `.wrangler/`.
2. **`make test` fails in a clean clone on any non-CUDA machine.** The `test` target depends on
   `cuda`, which needs `nvcc`; absent it: `make: nvcc: No such file or directory … Error 127`.
   The committed binaries exist precisely to hide this — someone can clone, run the prebuilt
   ELF, and believe the suite is portable.
3. **The committed CUDA benchmark is a forged receipt.** Running `./benchmarks/ternary_mac` on a
   machine with **no GPU** prints `GPU: RTX 4050 Laptop (20 SMs, 2560 cores)` and a full results
   table of `0.000 ms` timings, `-nan` speedups and `inf` GFLOPS. The GPU name is a **hardcoded
   string literal at `src/ternary_mac_kernel.cu:225`**:
   `printf("GPU: %s\n\n", "RTX 4050 Laptop (20 SMs, 2560 cores)");`
   The table divides by a zero CUDA timer, so it is `-nan`/`inf` on any host without the exact
   GPU it was built on. Same class as the fabricated-benchmark findings in
   `SCOUT-2026-10-03T0440Z`, but disguised as a hardware receipt.

**Bonus contradiction:** the README claims *"At n=50: δ = 0.137 → 86.3% cancellation (verified by
Monte Carlo to 0.3%)"*. The repo's own committed benchmark prints at n=50
`delta_emp 0.090406, Cancel% 90.9594, Error% 5.4209` — an absolute error of **4.68 percentage
points, 16× the claimed 0.3% tolerance**. The headline physics number is contradicted by the
artifact shipped beside it, and no test covers the Monte-Carlo-vs-theory gap at n=50.

---

## 2. `flux-compiler` — "the first certifiable constraint compiler" has a verifier that is `// Stub: always passes`

The repo advertises *"Correctness Verified. Safety Certified. Zero Surprises."* and describes a
GUARD-DSL → verified-machine-code compiler. Unlike most of the fleet, **its CI is genuinely
strict** — `cargo fmt --all -- --check` + `cargo test --workspace --all-features`, no `|| true`,
no `continue-on-error`. (No `cargo`/`rustc` in this sandbox, so this is inspection, not execution.)

**`crates/fluxc-verify/src/lib.rs:25-33` — the entire verifier:**

```rust
pub fn validate(ir: &IrModule, output: &CodegenOutput) -> Result<ValidationResult, VerifyError> {
    // Stub: always passes for now
    Ok(ValidationResult {
        valid: true,
        message: format!("translation validation passed for '{}' targeting {:?}",
                         ir.name, output.target),
    })
}
```

It ignores both arguments and returns `valid: true` unconditionally. Its two tests
(`validate_passes_for_valid_module`, `validate_empty_module`) both assert `result.valid` — they
assert the constant. **The crate named `fluxc-verify` cannot reject anything.**

**The formal-methods substrate is placeholders:**

```
formal/guard-semantics/  README.md only   "Status: In Development"
formal/pass-theorems/    README.md only   "Status: In Development"
formal/vrs/              README.md only   "Status: In Development"
tests/fuzz/              README.md only (75 bytes) "Status: In Development"
```

`find . -name "*.v"` → **0 files**. `git ls-files | grep formal` → 3 README paths, zero `.v`.
The README states *"The project includes Coq proof files in `formal/guard-semantics/`"* and lists
8 specific proven properties (*"Register allocation does not spill across interrupt boundaries"*,
*"No compiler pass introduces undefined behaviour"*, …). **No Coq file exists in the repository.**
The 8-lemma bulleted list is the load-bearing claim of the whole "certifiable" positioning, and it
is backed by three placeholder READMEs.

**4th instance of the literal-`\n` defect.** All four placeholder READMEs are stored with literal
backslash-n instead of newlines — `od -c formal/pass-theorems/README.md` shows
`T h e o r e m s \ n \ n O n e …` on a single line. Same class as `witness-complex` and the other
repos in `SCOUT-2026-10-03T0440Z`. **Now seen in 4 repos: treat any file whose first line holds a
backslash as malformed until proven otherwise.**

**In fairness — and this is why it's still worth reading — the README is unusually honest.**
It explicitly retracts its own headline badges:

> *"**Formal Verification Coverage and Fuzz Uptime badges have been removed pending independent
> audit.** … the specific '100% coverage' and '147 days' claims have not been independently verified."*

and under Formal Verification:

> *"**What remains unproven (as of this writing):** Termination proofs for all compiler passes;
> **Translation validation equivalence across all targets**"*

That second line names the exact gap — translation validation is the stub. **So the README
discloses that the verifier is unproven while the code comment says it is a stub, and neither
says the word "stub" where a reader would look.** The dishonesty is in the *title* and in the
"includes Coq proof files" sentence, not in the body. This is a much more salvageable repo than a
fabricating one: the scaffolding, IR, codegen and strict CI are real; the certification layer is
a to-do list wearing a certificate's name.

**Why another agent should care:** "certifiable" is a load-bearing word in this fleet's safety
story. A grep for `valid` / `verify` / `formal` in a capability audit returns **green**: the
crate exists, the tests pass, the CI is honest, the directory tree looks like a proof hierarchy.
Nothing in the automated surface distinguishes this from a real verifier. **Rank capability by
"does the gate execute the claim", not by "does the gate exist and pass"** — the same rule that
caught the fabricated benchmarks, and the reason this finding is #2 rather than lower.

---

## 3. `sonar-vision` — real physics, real tests, and a CI line that discards every failure

Pure-Python sonar ping/echo simulation with tracking and occupancy mapping (200 kHz fish-finder
parameters, 1500 m/s, 30° beam). The most physically careful repo examined this round: the
`SIMULATION_TEST_REPORT.md` justifies every parameter choice (absorption 30 dB/km "approximate
high-frequency seawater value", threshold `signal_strength ≥ 0.05`), and the package imports
cleanly with real signal processing.

**86 real tests** across `tests/test_all.py` (77) and `tests/test_simulation_scenarios.py` (9).
Executed via a minimal pytest shim (PyPI unreachable from this sandbox): **82/86 pass**. The 4
non-passes are *my harness's* limitation — they use instance-level `@pytest.fixture`, which the
shim cannot resolve — **not repo defects**. So: 82/86 verified, 4 unverified-by-harness.

**`.github/workflows/ci.yml` — the entire test step:**

```yaml
      - run: pip install pytest
      - run: pytest || true
```

**`|| true` makes the job exit 0 unconditionally.** Every assertion failure, every import error,
every collection error is discarded and the badge stays green. This is the fail-open class
(`SCOUT-2026-10-02T2235Z`), and here it is load-bearing rather than cosmetic.

**Mutation result — and it is subtler than expected:**

| mutation | result |
|---|---|
| `SOUND_SPEED_WATER: 1500.0 → 999.0` | **82/86 unchanged — GREEN** |
| same corruption, test pins the literal `1500.0` instead of importing the constant | **RED — 81/86, exit 1** |

The first row is the interesting one. `tests/test_all.py:170` reads:

```python
assert s.sound_speed == SOUND_SPEED_WATER      # imported FROM the module under test
```

The test asserts the default equals **the very constant it is testing**, imported from the same
module. Corrupt the physics constant and the assertion moves with it — the test is a **tautological
import**, a distinct and quieter failure mode than a hardcoded literal. Corrupting the speed of
sound in the physics is *exactly* the bug this suite exists to catch, and the suite is structurally
incapable of catching it. Repinning the assertion to an independent literal turned the identical
corruption RED immediately. (`test_all.py:180,185,232` do hardcode `1500` at call sites, so the
round-trip math is partly covered — the *default* is not.)

Restored; `git status` clean.

**Why another agent should care:** this is the only repo examined this round whose tests are
genuinely numerous *and* whose CI cannot report failure. `|| true` means the 86 tests are
documentation, not a gate. It also shows a second, quieter pattern worth adding to the taxonomy:
**asserting a value against the constant imported from the module under test** is a real defect
that passes review, because the assertion *looks* specific.

---

## 4. `exoj` — a gate that pins a number to an artifact, and documents its own fail-first history

The best-engineered verification artifact found this round, and included as a positive model.

**28/28 pass** in a clean clone (`node --test lab/*.test.mjs`). The interesting file is
`lab/readme-pin.test.mjs`, which pins README prose to a machine artifact:

```js
const art = JSON.parse(readFileSync(`${ROOT}../experiments/outputs/e40_scratch.json`)).sense;
t('deformations pinned to artifact', num('deformations') === art.deformations, …);
t('prob_open pinned to artifact (±0.001)', Math.abs(num('prob_open') - art.prob_open) < 1e-3, …);
t('conservation Σ ≤ 1 + 1e-9 in artifact', art['Σ'] <= 1 + 1e-9, …);
```

The README's prose `prob_open=0.9412` is checked against `e40_scratch.json`'s
`0.9411764705882353` — a number in a document held to a number in a file. It also verifies Σ ≤ 1
in the artifact itself, and asserts the README names its artifact of record.

**Mutation-verified fail-first:** setting the artifact's `prob_open` to `0.5` →
`FAIL prob_open pinned to artifact (±0.001)  readme=0.9412 artifact=0.5000`, suite RED, exit 1,
`not ok 3 - lab/readme-pin.test.mjs`. Restoring the artifact returns 28/28 green, tree clean.

**The part that makes it a model:** the file's own header comment records the gate's history —

```js
// FAIL-FIRST: on first run this was RED (README: deformations=16, prob_open=0.917 vs artifact 39/0.9412).
```

The author kept the evidence that the check *used to fail*, which is the receipt that
distinguishes a gate from a decoration. `SCOUT-2026-10-03T0440Z` established that a suite no
test calls can never detect mutation; `exoj` is the counter-example — a suite that is called,
that fails when the artifact moves, and that carries its own red-first receipt.

**Minor:** the suite is a bespoke runner (`pass`/`fail` counters + `process.exit`), not
`node:test` assertions, so `node --test` reports pass/fail at file granularity with 28 subtests.
No CI defect found; `test`, `smoke` and `gate` scripts all present.

---

## 5. `twist-engine` — a 130-test physics suite that survives a broken displacement law... and doesn't

Four substrates (TWIST/FLOCK/CHIRP/QUILT) unified by one law: layers + deliberate offset →
interference → emergence. `tests/sim.test.js` runs the **real `app.js`** under a stubbed DOM with
a seeded RNG (seed 42, 960×600), sweeping all six substrates and asserting physics invariants
without a browser. Plus `tests/jev.test.js`.

**130/130 pass.** `playtest.py` and a `CANON.md` ledger accompany it.

**Mutation-verified:** the SETL displacement law is asserted across **all 256 subset pairs**
(`app.js:1078`, `this.displacement = twistRank - rank;`, tested by
`check("setl: displacement = |K| − 2|A∩K| (all 256 pairs)", laws.disp)`).
Appending `+ 1` → **128 passed, 2 failed, exit 1**. Restoring → 130/130, tree clean.

**Why it matters as a peer of #4:** between them, `exoj` (pins prose to artifact) and
`twist-engine` (sweeps a 256-case invariant family in the real app under a deterministic seed)
are the two strongest gates in the fleet examined today. Both are **positive** results: the fleet
is not uniformly broken, and any capability ranking that reports only defects will misrepresent it.

---

## 6. `quilt-mojo` — a polyformalism port that booked its own cross-runtime hash divergence (and a README that never mentions it)

Part of the polyformalism family (Quilt ported to many languages). Most siblings are README-only
prose (`quilt-cobol`, `quilt-julia`, `quilt-cpp`, `quilt-swift` = 2 blobs each: LICENSE +
README; already covered by `SCOUT-2026-10-03T1917Z`). **`quilt-mojo` is different — it has real
source and a runnable cross-language parity oracle.**

`quilt_vibe.mojo` (145 lines), `reference_vibe.py`, `test_vibe_hash.mojo` (byte-exact hash
`0xe435d91d6d92a1d8`), and `examples/parity_oracle.py` (174 lines) implementing FNV-1a 64 +
`struct.pack` serialization in two order modes.

**Executed — `python3 examples/parity_oracle.py`, 8 cases, all self-checking:**

```
ORACLE self-check canonical 0xe435d91d6d92a1d8 OK
PY canonical     e435d91d6d92a1d8  e435d91d6d92a1d8
PY multi_sorted  5acf6043f877bc77  5acf6043f877bc77
PY multi_unsorted 5acf6043f877bc77  6fec04301caffe5f     <-- DIVERGES
PY tick_effect   d895d2395e983f8d  d895d2395e983f8d
```

**This is a real, reproducible polyformalism divergence and the author caught it themselves.**
`docs/USERMANUAL.md:108-115` records it:

```
case    : multi_unsorted
mojo    : 0x6fec04301caffe5f
py-sorted (canon): 0x5acf6043f877bc77
py-insertion     : 0x6fec04301caffe5f
verdict : DIVERGENCE (BOOKED) — byte format matches insertion-order oracle exactly;
         differs from sorted canon ONLY in serialization order (Mojo Dict insertion vs sorted id).
```

The cause is diagnosed precisely: Mojo's `Dict` iterates in insertion order while the Python
canon sorts by cell id. The byte format is correct; only the *iteration order* differs. **The port
did not hide the divergence — it isolated it, named it, and booked it in a verdicted table.**
That is exactly the behavior the "witness-log-is-prediction" doctrine asks for, and it is the
single most valuable artifact in this scout for anyone extending polyformalism to a language with
insertion-ordered maps.

**The reporting gap:** `README.md` **never mentions it.** A reader of the README sees a clean
port; the divergence lives only in `docs/USERMANUAL.md` and the oracle docstring. A divergence
that is booked but absent from the front door will still be read as a port with no known
divergence. The fix is one line in the README.

**Two smaller issues:**

1. **3 tracked `.orig-20260930` backup files** (`quilt_vibe.mojo.orig-20260930`,
   `reference_vibe.py.orig-20260930`, `test_vibe_hash.mojo.orig-20260930`) — editor backups
   committed alongside the live files they shadow.
2. **The hash test is a no-op without a flag, and says so:**
   `test_vibe_hash.mojo` header — *"Run with: `pixi run mojo test_vibe_hash.mojo -D ASSERT=all`
   (assert is a no-op without `-D ASSERT=all` on this toolchain)."*
   On a default invocation the test prints `test_hash: OK` and verifies nothing. There is no
   `pixi.toml` in the tracked file list, so the exact invocation isn't pinned by the repo either.
   Honest comment, dangerous default. No `mojo`/Max toolchain in this sandbox, so **this is
   inspection, not execution** — I did not run the Mojo test.

**Why another agent should care:** the fleet's polyformalism claim is "the algebra holds
bit-identically across N ports." This repo is the one place where a port found a genuine
divergence and reported it instead of asserting parity. Any new port should copy the
`parity_oracle.py` pattern — two order modes, per-case verdict table, divergence booked — and
should check `docs/USERMANUAL.md`, not the README, for known divergences.

---

## Cross-cutting: the taxonomy got two new entries

Consolidating this round against the classes in `SCOUT-2026-10-03T0440Z`:

| # | class | this round | how to detect |
|---|---|---|---|
| 1 | hardcoded receipt literals | `native-conservation-core` `.cu:225` GPU name; `ternary_mac` `-nan`/`inf` table | run the artifact on hardware it wasn't built for; a result table with all-zero timings is a receipt, not a measurement |
| 2 | **unfalsifiable *physics*** (new) | `state.C = state.gamma + state.eta` then audit `\|γ+η−C\|<ε` | grep for an identity asserted on a value defined as that identity's terms |
| 3 | **tautological import** (new) | `sonar-vision` `assert s.sound_speed == SOUND_SPEED_WATER` (imported from module under test) | grep tests for `== <CONST>` where `<CONST>` is imported from the module under test; re-pin to a literal and re-run |
| 4 | stub verifier under a green surface | `fluxc-verify` `// Stub: always passes for now`; `formal/` = 3 READMEs, 0 `.v` | open the `verify`/`certify` crate and read the function body, not the test count |
| 5 | fail-open CI | `sonar-vision` `pytest \|\| true` | grep workflows for `\|\| true` / `continue-on-error` |
| 6 | cosmetic `.gitignore` | `native-conservation-core` `benchmarks/` ignored, 3 ELFs still tracked | `git check-ignore -q --no-index <path>` **and** `git ls-files <path>` |
| 7 | literal-`\n` files | flux-compiler ×4 (**4th repo class-wide**) | `od -c file \| head` — a `\   n` pair on line 1 |

**The unifying rule, now stated three ways across scouts:** a green surface is evidence of
*nothing* until you have watched it go red against a specific corruption. This round ran five
mutations: 3 went RED as they should (`native-conservation-core` η, `twist-engine` displacement,
`sonar-vision` literal-pinned constant, `exoj` artifact) and 1 stayed GREEN while corrupting the
audit (`native-conservation-core` C). **The mutation that survives is the finding.**

**Ranking health by "does the gate execute the claim" — never by CI conclusion** — separates
`flux-compiler` (strict CI, stub verifier) from `exoj` (no badges, mutation-verified gate) in
the opposite direction from what a green-checkmark ranking would tell you.

## Reproduce

```bash
git clone https://github.com/SuperInstance/native-conservation-core && cd native-conservation-core
make test                                    # FAILS without nvcc (Error 127)
./benchmarks/ternary_mac                     # prints "GPU: RTX 4050" + all-zero table, no GPU present
cc -O3 -fPIC -shared -Iinclude -o python/libconservation.so src/conservation_core.c
sed -i '52s/.*/state.C = 1.0;/' src/conservation_core.c   # falsify C
cd python && pytest test_conservation.py      # 28/28 GREEN — the audit cannot fail
```

```bash
git clone https://github.com/SuperInstance/sonar-vision
sed -n '/run: pytest/p' .github/workflows/ci.yml          # → "pytest || true"
```
