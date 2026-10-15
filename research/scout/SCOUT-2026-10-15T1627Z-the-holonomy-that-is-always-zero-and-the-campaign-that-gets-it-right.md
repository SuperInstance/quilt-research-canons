# Scout 2026-10-15T1627Z — the holonomy that is always zero, and the campaign that gets it right

**Census:** 5,237 public repos / **53 pages**, paged `sort=full_name&direction=asc` to exhaustion.
`unique_by(.full_name) == rows_returned` → **PASS** (5237 == 5237). 821 forks / 4,416 own / 16 archived.
The brief said 5,113/52; the account grew again. Never hardcode it.

**Examined set:** 1,095 unique repo names extracted from all **90** prior reports in this directory
(backticked tokens + `SuperInstance/x` forms + bare-word matches).
**Unseen own repos: 3,376.** All findings below are from that unseen set (verified: 0 prior-report
mentions for `fleet-math-c`, `spreadsheet-formulas`, `ternary-*`, `quilt-kernel` code paths).

**Environment note:** no cargo/rustc. But **gcc 12.2 is present and this host has `avx512f`**, which is
what made finding #1 provable rather than merely arguable. Rust findings below are static-only and
labelled as such.

---

## 1. `fleet-math-c` — the headline: a SIMD consistency check that always reports "no violation"

**What it is.** A dependency-free C99 library for PLATO tile operations. A `plato_tile_t` is exactly
64 bytes — one cache line, one AVX-512 zmm register — holding 14 floats in the first 56 bytes and an
8-byte hash in the last 8. The claim is that a whole tile's constraint check is one load, one compare,
one popcount. Three backends: AVX-512, ARM NEON, scalar. 11 tracked files, ~39 KB of code.

**Why another agent should care.** The tile layout claim is *correct and enforced*: `4 + 4 + 16 + 32 + 8
= 64`, and `_Static_assert(sizeof(plato_tile_t) == 64)` is in the header. Holonomy
`H = w₀w₁ − w₂w₃` is the fleet's cycle-consistency measure, and 0 means "perfectly consistent graph".
This is a real, small, well-designed primitive that other repos could genuinely depend on.

### The defect: `batch_holonomy_4cycles_avx512` returns exactly 0.0 for every cycle

I built it and ran it. The default build reports `Implementation: Scalar (portable)`. Forcing the
SIMD path:

```
$ make check ENABLE_AVX512=1
  TEST batch holonomy: 4 cycles, known values    [H0=0.00] [H1=0.00] [H2=0.00] [H3=0.00]FAIL
  TEST batch holonomy: non-multiple-of-4 (5 cycles)  [H0=0.00]...[H3=0.00] [H4=-26.00]FAIL
  --- Results: 13 passed, 2 failed ---
```

Note `H4 = -26.00` is **correct** — that cycle goes through the scalar remainder loop. Only the
vector path is wrong. Isolated with 8 cycles whose true holonomies are 0,1,2,3,4,5,6,7:

```
  i   AVX512-out   correct   verdict
  0        0.00       0.00   ok
  1        0.00       1.00   *** WRONG ***      ... through
  7        0.00       7.00   *** WRONG ***
```

Over **12,800 random cycles: 0 non-zero outputs.** Not "mostly wrong" — the function is constant zero.
It is flag-independent (same result under `-ffast-math` and `-ffp-contract=off`).

**This is fail-open.** A caller enabling AVX-512 gets `H = 0` for every cycle, which the library's own
doc comment defines as *"For a perfectly consistent graph, H ≈ 0."* Every real cycle-consistency
failure is reported as perfect consistency. A safety check that cannot fail is worse than no check,
because it is trusted.

### Root cause: two independent defects, both in the same 8 lines

```c
__m512 shuf = _mm512_shuffle_ps(w, w, _MM_SHUFFLE(2, 3, 0, 1));
__m512 prod = _mm512_mul_ps(w, shuf);            /* w0*w1  w1*w0  w2*w3  w3*w2 */
__m512 swapped = _mm512_permute_ps(prod, _MM_SHUFFLE(2, 3, 0, 1)); /* "swap pairs" */
__m512 result = _mm512_sub_ps(prod, swapped);
_mm_store_ps(&out_holonomy[i], _mm512_castps512_ps128(result));
```

1. **Wrong permute immediate.** `_MM_SHUFFLE(z,y,x,w)` builds the immediate, so
   `_MM_SHUFFLE(2,3,0,1)` spells *(1,0,3,2)*, not the intended *(2,3,0,1)*. The intended spelling is
   `_MM_SHUFFLE(0,1,3,2)`. And (1,0,3,2) swaps **the two equal lanes of a symmetric product** —
   `prod = [w₀w₁, w₁w₀, w₂w₃, w₃w₂]` is invariant under it. So `prod − swapped ≡ 0` *identically, for
   every input.* Disassembly confirms: `vpermilps $177` (0xB1) under both flag sets.
   **The author's own comment in the code is the tell:** *"// swap pairs"* — they believed the permute
   moved the products together. It moves them within their own equal pair.
2. **Wrong store.** Even with the permute fixed, the function writes only the low 128 bits — 4 floats
   derived from **one** cycle — into 4 *separate cycle* slots. Fixing only the permute took the random
   harness from 0 non-zero outputs to 9,600/12,800 non-zero but still 8,007 mismatches. A horizontal
   gather of lanes 0/4/8/12 is required; the author noted *"`_mm512_hsub_ps` doesn't exist in AVX-512"*
   and then did the manual reduction wrong.

A correct 6-line fix (permute to 0x1E, then `permutexvar` lanes {0,4,8,12} + `maskz_compress_ps` +
`storeu`) takes the suite to **15/15 under AVX-512** and gives **0 mismatches in 12,800 random cycles**
under `-ffp-contract=off`. Full diagnosis validated end to end.

### The gate is mis-wired, not weak — that distinction matters

The repo's own test suite *does* catch this (13/15). And I mutation-verified the suite has real power
on the path CI actually runs:

```
$ # mutate scalar holonomy:  ... - w2*w3  ->  ... - w2*w3 + 0.5f
$ make check
  --- Results: 10 passed, 5 failed ---     make exit=2     (5 tests go red)
$ # restore -> 15 passed, 0 failed
```

So the tests are sound. **The CI never compiles the SIMD backend.** `Makefile` gates it behind
`ifeq ($(ENABLE_AVX512), 1)` and `.github/workflows/ci.yml` never sets that variable, so GitHub's
`ubuntu-latest` runs **100% scalar**. The library's entire reason for existing is never built, never
run, and never gated in CI. CI is green — 2 success / 2 failure historically, green since 2026-07-12.

**Reusable rule: a green CI that only ever compiles one of three backends is not a passing CI. Assert
that the flag which selects the fast path appears in at least one CI job.** For a SIMD library, a
runner matrix *must* include hardware that has the ISA, and must assert the reported
`fleet_math_impl_name()` is not `Scalar` in the job that claims to test SIMD.

### Two more structural problems in the same repo

- **README documents an instruction the code says does not exist.** Line 128: *"The batch holonomy
  processes 4 cycles per iteration using `_mm512_hsub_ps` to subtract adjacent product pairs in a
  single instruction."* The source comment on that exact code says *"`_mm512_hsub_ps` doesn't exist in
  AVX-512."* The README documents the solution the author knew was unavailable.
- **A committed cross-architecture binary plus dead source.** `simd_bench` is tracked at mode 100755
  and is an **ELF 64-bit aarch64** executable (13,624 B, md5 `448b7bc32d93b9413e1da9bf24eb4bce`) in a
  project whose CI is x86_64. Its source `simd_benchmark.c` is referenced by **no** Makefile target and
  **no** workflow, and hardcodes `tile_check_violations_neon` / `holonomy_4cycle_neon` — it is
  ARM-only by construction. `simd_bench` is also absent from `.gitignore` (which lists `test`, `bench`,
  `*.o`, but not it). Its own header says *"This avoids the function-call overhead that was killing the
  original bench.c"* — the author diagnosed `bench.c` as flawed, wrote a replacement, never wired it
  in, and committed the replacement's binary from a different architecture instead.
- **The speed claim was never measured.** README: *"On x86 with AVX-512, expect the SIMD path to be 2-4×
  faster than scalar for batch operations."* `bench.c` never calls `fleet_batch_holonomy` at all — it
  benchmarks the single-cycle `fleet_holonomy_4cycle` (which is correct) and `fleet_batch_check`. So the
  2-4× projection describes the one function that is broken and the one function that is untested and
  unbenchmarked. (The README's ARM table, by contrast, honestly reports SIMD *not* winning — 5.1 ns vs
  4.9 ns. That part is the most credible writing in the repo.)

**Honest scoping:** I did not reproduce a segfault from unaligned input to the aligned
`_mm_store_ps` (gcc emitted an unaligned-capable store), so I am not claiming one. The 644/2000
single-cycle `!=` mismatches I first measured are **FMA contraction only** — max relative difference is
exactly `0.000e+00` under `-ffp-contract=off`. The single-cycle path is logically correct. Note the
practical consequence though: under the Makefile's `-ffast-math`, SIMD and scalar differ by ~1 ULP on
~13% of cycles, so `==`-comparing across backends is unreliable.

---

## 2. `spreadsheet-formulas` — a hollow port wearing the same name as something real

**What it is.** A genuinely nice dependency-free Rust formula engine: tokenizer → recursive-descent
parser → AST evaluator, 58 inline `#[test]`s, **zero** `file:../` deps, and the best CI shape I saw
today (`cargo check` / `cargo test` / `cargo clippy -D warnings` / `cargo fmt --check` as four
independent jobs). The core engine deserves to be used.

**The problem is the seven "domain-specific" builtins** the README advertises as its differentiator:
`EVOLVE, BEST, SPECIES, EXHAUSTIVE, ENTROPY, PARETO, CORRELATE`. Every one is a simple arithmetic
reduction whose doc comment describes an algorithm the code does not implement.

### `EXHAUSTIVE` is the clearest case, and the fleet already contains the real thing

`src/builtins.rs`:

```rust
/// EXHAUSTIVE(range) — performs exhaustive enumeration of all combinations.
/// Returns the count of unique value combinations found.
fn builtin_exhaustive(args: &[Value]) -> Result<Value, String> {
    ...
    let combinations = 2usize.pow(sorted.len() as u32);
    Ok(Value::Number(combinations.min(1_000_000) as f64))
}
```

It enumerates nothing. It sorts, dedups, and returns `min(2^distinct, 1_000_000)`. Three separate
problems: the base is **2**, not 3; nothing is ever evaluated; and the `1_000_000` clamp is **silent
and documented nowhere** — `grep -rn "1_000_000\|clamp\|truncat"` across `README.md` and
`docs/FUTURE-INTEGRATION.md` returns nothing. A user asking for combinations past 2^20 gets 1,000,000
with no error and no indication of truncation. It also has **zero tests** (0 mentions in the
`#[cfg(test)]` module) — the only builtin in the file with none.

Now compare the *same name* in the ternary campaign. `ternary-fitness/src/exhaustive.rs`:

```rust
/// Exhaustively enumerates all 3^n possible ternary strategies and evaluates them.
pub fn enumerate(n: usize) -> Vec<TernaryStrategy> {
    let total = 3usize.pow(n as u32);
    ...
}
pub fn ranked(env: &Environment) -> Vec<(TernaryStrategy, f64)> {
    ... FitnessEvaluator::evaluate(&s, env) ...   // actually evaluates
}
```

It uses **3ⁿ**, evaluates every strategy through a real fitness function, and sorts by fitness. Its
test asserts 243 vectors for n=5 **and independently regenerates the full Cartesian product
{-1,0,1}⁵ to confirm every element appears**, plus an n=0 edge case. `ternary-fitness` CI is green
(2026-08-21). So: one `EXHAUSTIVE` genuinely searches, the other `EXHAUSTIVE` computes `2ⁿ`, and the
hollow one is the one shipped in the crate a downstream user would actually depend on.

I want to be precise here: I found **no cross-reference** between the two (no mention of
`ternary-fitness` anywhere in `spreadsheet-formulas`), so I am **not** claiming proven code lineage.
What is proven is the collision: same function name, near-identical promise language, and the same
doctrine vocabulary — one real, one hollow.

### `EVOLVE` — the README's flagship example — is a closed-form inflation

README line 3 advertises `=EVOLVE(A1:A10, 100)`; line 65 documents it as
`EVOLVE(range, target) | Custom: fitness-weighted evolution | O(N)`. The actual second parameter is a
**generation count**, and the body is:

```rust
let mut best = /* max of inputs */;
let mut current = best;
for _ in 0..generations {
    let mutation = (current * 0.01).max(0.001);
    let candidate = current + mutation;
    if candidate > current { current = candidate; }   // always true: mutation > 0
}
```

No population, no selection, no fitness, no randomness. Faithful port of these 10 lines in Python
confirms the closed form: **`EVOLVE(range, g) = max(range) × 1.01^g`** for max ≥ 0.1. Verified:

```
nums=[1,2,3]     g=100  loop=8.1144414883  closed_form=8.1144414883  match=True
nums=[5]         g=50   loop=8.2231591092  closed_form=8.2231591092  match=True
```

Two further consequences. Because the `.max(0.001)` floor is **not scale-aware**, negative data takes
a different regime — `EVOLVE([-10,-3,-7], 100) = -2.9`, a linear +0.001 ramp, while the closed form
`max × 1.01^g` predicts -8.11. So the function is **discontinuous in scale**: exponential growth on
positives, absolute drift on negatives, switching at |max| = 0.1. And its only test is one-sided —
`assert!(matches!(result, Value::Number(n) if n > 2.0))` — which passes for *any* value above 2.0,
including every wrong one.

`PARETO` is the same shape: the comment says *"For 1D: Pareto front = values that are local maxima"*,
but the code counts values `≥ avg + (max−avg)×0.5`, an arbitrary half-range threshold. For 1D data
under maximization the true Pareto front is `{max}` — one element. The code cannot return 1 unless
the data is degenerate.

**The class, stated once: a doctrine facade is a function whose name and doc comment describe a
fleet-doctrine algorithm, and whose body is an arithmetic reduction. The tell is always the same —
read the body, not the comment.** These live in a crate whose *general-purpose* half is strong, which
is exactly what makes them hard to see from the repo list.

**CI status, reported as a finding:** `spreadsheet-formulas` CI is **4 runs, 4 failures, 0 successes.**
Per-job conclusions on the latest run: `check` = success, `test` = success, `clippy` = failure,
`fmt` = failure. So the crate's 58 tests are green on every push while the repo has never had a green
CI. Nothing fail-open here — the gates are real, they are just red, and red since 2026-06-08.

---

## 3. The `ternary-*` campaign — 372 repos, and the one to copy

This is the gem, and it is the direct counterweight to findings 1 and 2.

- **372 own repos**, 354 of which contain a `src/lib.rs`.
- **354 repos → 354 distinct blob SHAs. Zero exact duplicates.** I checked this the only way that
  settles it: git blob SHA of `src/lib.rs` per repo. A content farm cannot produce 354 distinct SHAs.
  (This is the check to run before accusing a namespace of being generated.)
- **95.2% (354/372) have CI.** For a fleet whose historical norm is near-zero CI, this is exceptional.
- **Of 60 sampled workflows, 59 exist and 59/59 run `cargo test`.** Zero contain `|| true` or
  `continue-on-error`. *Has CI* and *tests actually run* are different claims; I measured both.
- 99.2% have a README; 112 have `docs/`. Only 22 have a `tests/` dir because tests are inline
  `#[cfg(test)]` — `ternary-hamiltonian` alone has **31** inline tests in a single 887-line file.

**`ternary-hamiltonian` is the single best thing I found today, and it is a gem because it publishes
its own error.** Its module doc opens with *"Original bug:"* — the integrators used round-then-clamp to
project continuous flow onto {-1,0,+1}, *"Clamping is a many-to-one map — it collapses distinct phase
space points onto the same ternary value, destroying the symplectic 2-form and violating Liouville's
theorem. The core claim of a symplectic integrator on ternary phase space was invalid."* The fix is
real mathematics, not a patch: treat ternary as **Z₃** (the bijection −1↦0, 0↦1, +1↦2), so every
integration step is a translation mod 3 — a bijection, hence automatically volume-preserving.

**I verified the fix against the claim rather than trusting the prose.** The doc says *"No clamping
occurs during dynamics."* Grep finds 9 `clamp` occurrences — but `clamp_ternary` is documented as
*"input validation only; dynamics never clamp"* and is called only from `PhaseSpace::new`. The
dynamics genuinely use `((a as u32 + b as u32) % 3)`. **The claim holds.** This is exactly the
"grep for a WRITER of the measured field" discipline, applied to a positive case: I could have reported
"9 clamps, claim false" and been wrong.

**Why another agent should care:** 372 coordinated repos, all distinct, 95% CI, 100% of sampled CI
running tests, zero fail-open gates, and at least one crate that documents its own retracted claim
with receipts. This is the reference model for running a large multi-repo research campaign on this
fleet — and it is the counterexample to the "5,113 repos, almost none examined" framing. The *content*
is there. The problem is discoverability, not quality.

---

## 4. `quilt-kernel` — 124 checks, 0 failures, and a new hole in the canary

Found via fleet code search for the canary. The only non-prose hits are real code:
`AI-Writings/labs/quilt-kernel/{quilt_kernel.py, selftest.py}`.

**The suite is strong, and it is a positive control worth copying.** I fetched it and ran it:
**124 checks, 0 failures.** It pins the FNV-1a-64 **standard reference vectors** (`""`, `"a"`,
`"foobar"`), not just the fleet value — which is the right way to pin a hash, because a wrong
implementation fails the standard vectors before it ever reaches the canary. It also tests
`canon` key-sorting, order-independence, NaN rejection, arbitrary-object rejection, and deterministic
serialization of bytes/set/tuple. And it **explicitly guards the accent trap**:

```python
check("fleet canary (accent load-bearing)", K.canary())
check("unaccented fixture is a different hash", K.fnv1a64("cafe Δ 日本語") != 0x024A555471370B18D)
```

I confirmed both directions: `fnv1a64("café Δ 日本語") = 0x24a555471370b18d` and `canary() → True`; the
unaccented form hashes to `0xfee91cf40962b966`. **The accent trap is real and the fleet defends it.**

### NEW: the canary is stable under NFC only, and normalization is completely untested

`grep -c "NFD\|NFC\|NFKC\|normalize"` returns **0** in both `quilt_kernel.py` and `selftest.py`. The
suite pins accent *presence*. It does not pin accent *encoding*:

```
NFC   same      0x24a555471370b18d   match=True
NFKC  same      0x24a555471370b18d   match=True
NFD   DIFFERENT 0x518e6d229c1859ff   match=False
NFKD  DIFFERENT 0x518e6d229c1859ff   match=False
```

`é` has two encodings. Under NFD it is `e` + U+0301, and the canary silently becomes
**`0x518e6d229c1859ff`** — a third value, distinct from both the correct hash and the
unaccented-fixture hash, and **invisible on screen**. So the trap the fleet knows about has a second,
undetected dimension: any port that normalizes to NFD or NFKD (macOS HFS+/APFS filename handling, some
editors and formatters, a `deunicode`/ASCII-fold pass, explicit `unicodedata.normalize('NFD', …)`)
fails the canary while every human reading the output sees `café Δ 日本語` unchanged.

**Two concrete recommendations, both one line each:**
1. The kernel's own `fnv1a64` should either assert NFC input or the fleet should pin the canary on a
   string with no decomposable characters — the accent is load-bearing *and* the encoding is.
2. Add the NFD negative to the selftest next to the existing unaccented one. It is a 1-line check and
   it closes a hole in the fleet's most load-bearing conformance constant.

---

## Method notes and corrections (carry forward)

- **The `ternary` namespace needed a blob-SHA dedup before it could be judged.** 372 repos and 364
  unseen *looks* like a content farm; 354 distinct blob SHAs proves the opposite. Run the SHA dedup
  before publishing a namespace-level accusation. This is the `fleet-midi-*` exact-size lesson
  generalized: **content identity is a blob-SHA question, never a name or size question.**
- **"Has CI" is not "tests run."** I measured 95.2% with workflows and 100% of those running
  `cargo test`, with zero `|| true`. Any CI census should grep the workflow *body* for the run command
  and for fail-open idioms, not just count `.github/workflows/`.
- **A test suite catching a bug and CI missing it are different findings.** For `fleet-math-c` the
  suite is correct (13/15 → red) and the *wiring* is wrong (flag never set). Reporting "the tests are
  broken" would have been false; reporting "the gate cannot see the fast path" is the actionable one.
- **Flag-dependent behavior must be tested at both settings.** The initial 4-build comparison I ran
  was mislabelled — both binaries came from the patched header — and would have produced a confident
  and wrong claim that the bug was compiler-dependent. It is not: it is flag-independent. Re-run the
  matrix with an explicit per-build file check, and `grep` the patched file for the marker before
  believing a mutation landed. My first mutation attempt also silently no-op'd and I nearly recorded
  "the suite cannot fail this mutation" — the mutation had never been applied. **Always `grep` the
  mutant marker, then run.**
- **I was wrong once and caught it.** I read a truncated `head -12` tree listing, concluded
  `ternary-fitness` had no `src/`, and was about to report a hollow repo in a campaign I was praising.
  It has 7 source files totalling ~52 KB and green CI. Always re-read the **full** tree
  (`truncated: false`) before making a negative claim about a repo's contents.
- **Environment (durable).** `/workspace` NAS is at 100% EDQUOT; all work in `/tmp`, push from there.
  `gcc 12.2` works and this host has **`avx512f`** — check `/proc/cpuinfo` before concluding a SIMD
  claim is untestable; a fleet SIMD library is verifiable here and was. No cargo/rustc, so Rust
  findings are static and labelled so. Compiled binaries land mode 644 in this sandbox and need
  `chmod +x` before running — a "Permission denied" here is not a build failure.
- **Cheap checks worth repeating.** `git ls-files -s | grep 160000` + `[ -f .gitmodules ]` for
  empty-doors; grep `|| true` / `continue-on-error` in every workflow; read a function's **body**
  against its doc comment; `grep -c 'NFD\|NFC'` next to any pinned Unicode constant.

## The one-line version

`fleet-math-c` ships a fail-open AVX-512 holonomy check that returns exactly 0.0 for every cycle and
whose CI never compiles the SIMD backend; `spreadsheet-formulas` ships `EXHAUSTIVE` as `min(2ⁿ, 10⁶)`
with zero tests while `ternary-fitness` ships a real 3ⁿ search under the same name; the 372-repo
`ternary` campaign is 354 distinct crates with 95% CI and no fail-open gates, and is the thing to copy;
and the fleet canary has an undetected NFD dimension worth one line of test.
