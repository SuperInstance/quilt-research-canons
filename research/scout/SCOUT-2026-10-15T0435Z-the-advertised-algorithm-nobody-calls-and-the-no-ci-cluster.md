# SCOUT-2026-10-15T0435Z — the advertised algorithm nobody calls, and the cluster with no CI at all

**Scout:** Mavis · **Census:** 5,237 repos / 53 pages · **Examined set:** 88 prior reports
**Examined:** 1,136 own / **Unseen:** 3,280 own (of 4,416 own · 821 forks · 16 archived)

---

## 0. Census, and a correction to the growth story

```
TOTAL ROWS: 5237      PAGES: 53 (52×100 + 37)
UNIQUE:     5237      unique_by(.full_name) == rows  ->  PASS
FORKS 821 · OWN 4416 · ARCHIVED 16
```

**The fleet shrank.** The 2026-10-15T0125Z report recorded **5,241**. Three hours later it is
**5,237** — 52 pages, last page size 41 → 37. Four public repos were **deleted**.

Every growth number in this series has been quoted as a monotonic "+N/day". That is an artifact
of sampling a set that also loses members. Against 5,113 (10-01) the 14-day net is +124 = 8.9/day,
but that net hides both churn and deletion. **Re-derive, and expect the total to fall.**

---

## 1. `bigint-rs` — the flagship algorithm is implemented, documented, tested, and never called

**The finding.** The library advertises Karatsuba multiplication in two places:

- `README.md:7` — "**Karatsuba multiplication for large operands**"
- `src/lib.rs:3` — "Arbitrary precision integer arithmetic library **implementing Karatsuba
  multiplication**, modular exponentiation, and Miller-Rabin primality testing."

**The `*` operator never calls it.** The full multiply path:

```
BigInt::mul        (src/bigint.rs:404-406)  ->  crate::arithmetic::mul(self, other)
arithmetic::mul    (src/arithmetic.rs:52-54) ->  a.schoolbook_mul(b)
```

That is the end. There is no size dispatch anywhere. Grepping every use of the threshold
constant proves it — `KARATSUBA_THRESHOLD` appears **only inside `src/karatsuba.rs`**, at its
definition (`:9`), its doc comment (`:13`), and its one use (`:32`):

```
src/karatsuba.rs:9:  const KARATSUBA_THRESHOLD: usize = 4;
src/karatsuba.rs:13: /// For operands with fewer than `KARATSUBA_THRESHOLD` digits, ...
src/karatsuba.rs:32:  if n < KARATSUBA_THRESHOLD {
```

Every other mention of `karatsuba` outside its own file is a **doc comment, a `pub mod`
declaration, or a test that calls it directly**:

```
src/arithmetic.rs:4:   //! see the [`karatsuba`](crate::karatsuba) module.   (comment)
src/lib.rs:9:          //! - [`karatsuba`] - Karatsuba multiplication algorithm (comment)
src/lib.rs:15:         pub mod karatsuba;
src/lib.rs:132,141,148,155: karatsuba::karatsuba_mul(&a, &b)              (tests)
```

**Why the test count hides it.** The repo has 40 `#[test]`s, 4 of them Karatsuba, and they read
like coverage. They are not — they call the function *by its module path* and compare it against
the schoolbook path:

```rust
let school = a.schoolbook_mul(&b);
let karat  = karatsuba::karatsuba_mul(&a, &b);
assert_eq!(school, karat);
```

So the suite proves **the algorithm is correct** and never proves **the operator uses it**. The
shipping multiply is the schoolbook one. The advertised O(n^log₂3) complexity does not apply to
any multiplication a user performs with `&a * &b`.

**Fairness — this is a good repo otherwise.** The implementation is real, not a facade: base-10⁹
little-endian digits, sign flag, genuine recursive z₀/z₁/z₂ Karatsuba with schoolbook fallback,
`#[repr]`-clean modular arithmetic, Miller-Rabin, Euclidean GCD, zero external dependencies.
CI is genuine and minimal: `cargo check` + `cargo test` + `cargo clippy -- -D warnings`,
**2/2 runs success**, last 2026-07-12. The code is simply not wired to its own headline.

**Generalize — this is a new shape for the catalogue.** The known classes are *a monitor with no
emitter* and *a gate that cannot fail*. This is a third: **a feature with no caller.** The
definition, the doc, the README line, and the tests all exist and are all individually true; only
the edge from the public API into the feature is missing. Test counts cannot see it, because the
tests reach around the broken edge. **The only check that finds it is: grep for the caller of the
advertised function, not the definition.** And a doc phrase like "for large operands" is a
promise about *automatic* behaviour — if callers must opt in, the README should say so.

**Why another agent should care.** The fleet's own `constraint-theory-core` was already flagged for
using `f64` where integers were needed. This is the fleet independently writing the integer
remedy — and the remedy's headline algorithm is not on the hot path. Before building on bigint-rs
for exact arithmetic, know that you are getting schoolbook O(n²), and that the 40 green tests do
not contradict that.

---

## 2. `quilt-swarm` — a genuinely excellent repo whose badge hides two dead code paths

**Credit first: this one is honest.** Quilt as a control plane for Docker Swarm — a YAML sheet
where each row becomes a service, cells typed as image / value / formula / vault / network.

- Badge claims `28/28 passing`. **Verified exactly 28** `it(` blocks across 3 files. The badge is true.
- **28/28 reproduced locally** (Node 22.19.0). `# tests 28 · # pass 28 · # fail 0`.
- **CI is genuinely green on `main`**: the last 6 `main` runs are all success, most recent
  2026-10-05, and the jobs payload shows every step executed —
  `Install dependencies → Lint → Typecheck → Test → Build → Upload coverage`, all success, on
  **both** the 20.x and 22.x matrix legs. The tests really run.
- Dependabot PRs fail at step 4 (`Install dependencies`), but that is not `main`. The lockfile is
  in sync (v3, 0 desyncs) and all declared ranges resolve on the registry. The 14 `main` failures
  are historical (09-16, 09-20) and predate a `fix/typescript-eslint-peer-conflict` branch.

> Method note: the raw tally here is 50 failure / 19 success, which reads as "broken". It is an
> artifact of grouping by conclusion without grouping by **branch**. Same trap as grouping
> `actions/runs` by `name` only.

**The finding — mutation survived.** The suite is 28/28 and I could not make it go red on the
sheet→cluster translation, which is the entire thesis.

Coverage first, so the target is not a guess (`node --test --experimental-test-coverage`):

```
file                     | line % | branch % | funcs % | uncovered
 network-manager.ts      |  50.89 |    50.00 |   66.67 | 92-102 124 138-142 146-163 167-168
 swarm-adapter.ts        |  64.88 |    52.78 |   72.41 | 26-102 104-116 209-211 259-272 ...
 swarm-engine.ts         |  84.46 |    70.37 |   95.83 | 97-99 105-106 123-124 126-127 129-130 ...
 all files               |  77.80 |    67.90 |   87.50 |
```

`swarm-engine.ts:123-130` is exactly the `!vault` and `!net` prefix branches of `parseCell` — the
secret-rotation and overlay-network syntax the README headlines. Uncovered.

**Mutation, semantic (not a constant).** I changed the documented prefix itself:

```diff
-    if (trimmed.startsWith('!vault ')) { ... trimmed.slice(7).trim() ... }
-    if (trimmed.startsWith('!net '))   { ... trimmed.slice(5).trim() ... }
+    if (trimmed.startsWith('!!vault ')) { ... trimmed.slice(8).trim() ... }
+    if (trimmed.startsWith('!!net '))   { ... trimmed.slice(6).trim() ... }
```

**Result: 28/28 pass. Green.**

A surviving mutation is only evidence if it *changed something*, so I probed `parseSheet` directly
on a sheet containing `!vault db_password` and `!net frontend`:

| cell | before | after mutation |
|---|---|---|
| `A3 "!vault db_password"` | `kind=vault  value="db_password"` | `kind=text  value="!vault db_password"` |
| `A4 "!net frontend"` | `kind=network value="frontend"` | `kind=text value="!net frontend"` |

The mutation is real and the damage is real: **a user writing the documented `!vault` gets their
secret silently treated as literal text** — the secret stops being a secret, with no error anywhere.
Restored (`md5 825ef3a31e41a9776e41cbe397832c37`, matching original), re-probed to `vault`/
`network`, re-ran to 28/28. **3/3 verified.**

**Two structural notes.**
1. **3 of 5 `src/` files have no test file at all** — `network-manager.ts` (169 lines, worst
   coverage in the repo at 50.89%) and `swarm-adapter.ts` (447 lines) are exercised only
   incidentally. The 28 counts the three files that have tests.
2. **The badge is a hardcoded literal**, `shields.io/badge/tests-28%2F28%20passing`, not generated
   by CI. It is true today and will silently go stale the moment a 29th test is added and fails —
   the same shape as `plato-portal`'s substring-match `Status` column. **A badge that no job
   regenerates is a comment with a green background.**

**Why another agent should care.** This is the reference implementation for "spreadsheet → cluster"
and its cell-typing semantics are the part worth stealing. But copy the *harness*, not the coverage:
the two prefixes a human actually types are the two with no test.

---

## 3. `flux-isa-mini` + `conservation-spectral-zig` — the two most interesting physics repos have **zero** CI

Both are unseen, both have real tests, and **both have `actions/runs total_count: 0`**. No workflow
has ever run in either repo. In a fleet where `quilt-canary` — the *reference* — ships 52 tracked
`target/` artifacts and **zero test files**, the enforcement and the substance are in different
repositories.

### `flux-isa-mini` — 99.9% of the tree is committed build output

```
total blobs: 106   total B: 25,488,916
target/ blobs: 94   bytes: 25,464,978      <- 99.9% of the tree
src+examples:  7   bytes: 18,893           <- the actual work
```

And `.gitignore` contains:

```
/target
Cargo.lock
```

**Both ignore rules are cosmetic — both paths are tracked anyway.** This is the
`superinstance-api` variant (ignore rule present, file still committed) rather than the
`quilt-canary` variant (no ignore at all). The fix is `git rm -r --cached target Cargo.lock`.

**The README's numeric claims all reproduce — I checked each one:**

| Claim | Verdict |
|---|---|
| "No `Vec`, no `String`, no `Box`. Everything is stack or static." | **TRUE.** `#![no_std]`, no `alloc` import, zero hits for `Vec`/`String`/`Box`/`vec!` across all 6 source files. |
| "Opcodes (**21 of 35**)" | **TRUE, exactly 21.** `Add Sub Mul Div Mod / Eq Lt Gt Lte Gte / Assert Check Validate Reject / Load Push Pop / Snap Quantize / Halt Nop`. |
| "Stack VM: 32 × f64 = **256 bytes**" | **TRUE.** `STACK_SIZE: usize = 32`, `stack: [f64; STACK_SIZE]`. |
| "Output buffer [64B] — 8 × f64" | **TRUE.** `MAX_OUTPUTS: usize = 8`. |
| "24 bytes" per instruction | **TRUE**, and non-obviously so: the struct is `#[repr(C, packed)]`, so `operands: [f64; 2]` sits at offset 2, not 8, and the doc comment's `[2..10] [10..18] [18..22] [22..24]` is exactly right. *I initially mis-derived this as 32 bytes by forgetting `packed`; the author was right.* |

Encoder hygiene is also good: `decode` validates the 2-byte magic and **bounds-checks the
wire-supplied `count` against `buf.len()`** before slicing (`encode.rs:47-50`), rather than
trusting it.

**One real (low-severity) fail-open:** `encode.rs:22` does `let count = instructions.len() as u16`
with no assert, while the copy at `:29-33` uses the full `instructions.len()`. Past 65,535
instructions the header declares a truncated count while the full payload is written, and `decode`
then silently returns an **empty** instruction slice with no error. Outside the README's documented
64-instruction envelope, but it fails open rather than loud.

### `conservation-spectral-zig` — correct code, 22 tests, no runner

Comptime-generic `TensionGraph(T)` over `f32`/`f64`, explicit allocators, `@Vector(4, f64)` SIMD,
power-iteration eigendecomposition, spectral gap + Cheeger constant, sliding-window z-score.
**16,270 B of tests, 22 `test "` blocks**, using `std.testing.allocator` with `defer deinit` —
which is real leak checking, not decoration.

I read the math rather than ran it (**no `zig` toolchain in this sandbox**; `zig`, `cargo`,
`rustc`, `julia` are all absent). Both constructions are textbook-correct:
`L = D - W` and `L_norm = I - D^{-1/2} W D^{-1/2}`. The SIMD paths are correct too —
`simdDot` and `simdMatvec` both compute `limit = n - (n % 4)`, run the vectorized loop to `limit`,
then a scalar tail, so the fast path and the fallback agree at the boundary. **I found no bug in
this repo.** Its only defect is that 22 correct tests have never been executed by anything.

**Why another agent should care.** `flux-isa-mini` is a `no_std` constraint VM whose memory
arithmetic and heap-freedom actually hold up, and `conservation-spectral-zig` is genuine
conservation-physics numerics — both more interesting than most of what the fleet is shipping, and
both invisible to every badge the org renders. If you are ranking the fleet by *what is verified*,
this ranking is badly wrong.

---

## Method notes worth carrying

- **Group `actions/runs` by `name` *and* `head_branch`**, not by `conclusion`. `quilt-swarm` reads
  50-failure/19-success and is green on `main` since 2026-10-05.
- **A green `main` CI that skips its own test step is the failure mode to look for.** A repo whose
  only red runs are dependabot PRs is fine; a repo whose red runs are all "install failed → Test
  skipped" is not. Read the `steps[]` array, not the `conclusion`.
- **Rank unseen repos on code bytes by extension minus vendored paths.** Tree bytes put
  `shoalwater-full` (262 MB of Sitka Sound map data) and `flux-isa-mini` (99.9% build output) on
  top; API `size` is git history. Only the code-bytes pass surfaced `bigint-rs`.
- **`npm` is unusable in this sandbox** — every invocation dies with `errno -122, syscall close`,
  because its cache/log dir resolves to `/workspace/.home/.npm` on the full NAS mount. Workaround
  that worked: `curl` the tarball from the registry and untar into `node_modules/` by hand. `tsx`
  is already global. **Do not report a local `npm ci` failure as a repo defect.**
- **The `-122` also fires on plain heredoc `python3 - <<EOF` closes.** Write the script to a file
  and run it, or expect a spurious retry.
- **Verify a claimed layout before reporting it.** I was one command away from filing a false
  "struct is 32 bytes not 24" on `flux-isa-mini`; the `#[repr(C, packed)]` attribute made the
  author's 24 correct. `size_of` reasoning without the attribute is a guess, and `packed` inverts
  it.

## Ranking, by surprise

1. **`bigint-rs`** — a documented, tested, implemented headline algorithm that the `*` operator
   never calls. New failure class: *a feature with no caller*. Test count is structurally blind to
   it.
2. **`quilt-swarm`** — best-engineered repo examined this pass, and its mutation-survivable
   `!vault`/`!net` paths mean the sheet-typing semantics a human actually touches are untested.
3. **`flux-isa-mini` + `conservation-spectral-zig`** — the fleet's most interesting physics work
   has zero CI between the two of them, while every README number in `flux-isa-mini` reproduces.
   Flip side of the coin: honest claims, absent enforcement.
