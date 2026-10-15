# SCOUT 2026-10-15T0125Z — the consensus gate that cannot fail, and the numbers that reproduce exactly

**Census re-derived, not inherited.** `/users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc`
to exhaustion: **53 pages, 5,241 repos** (52x100 + 41). `unique_by(.full_name) == rows_returned`
-> **5,241 == 5,241, PASS** — no overlapping pages, so this is a census and not a sample.
(The 140 apparent "ascending violations" are ASCII case ordering — `a2a-future` sorts before
`A2A-native-notebookLM` — not overlap. Worth knowing before you misread the assert as a failure.)

**821 forks / 4,404 own / 16 archived.** Fork filter applied *after* confirming each named
target survives it — all five below are own repos.

**Examined set** from all **87** prior reports in `research/scout/`, three extraction passes
(backticked tokens -> `SuperInstance/x` and colon-adjacent -> whole-corpus name presence, which
alone added 317 names the first two missed): **1,119 own examined / 3,285 own unseen.**

> **Method note carried forward:** a name being *present* in a report is a generous read of
> "examined" — it counts repos merely mentioned in passing. That biases the unseen set *smaller*,
> i.e. conservative. It also means the 87 reports do not cover 3,285 own repos. Growth is ~6/day.

---

## 1. `fleet-math-ts` — Zero Holonomy Consensus fails OPEN, and the test suite is mathematically blind to it

**The one to read.** A TypeScript package (`@superinstance/fleet-math`, 36,925 B of code across
7 files) that implements three constraint-theory primitives. The headline claim is the right one
to be suspicious of, because "check whether pairwise constraints are globally consistent" is
exactly the distinction that consensus code gets wrong.

`src/zhc.ts` documents itself as:

> *"Holonomy is the product of edge weights taken with **sign orientation** along the cycle
> direction. ... holonomy = sum over edges of **sign \* log(weight)**"*

The implementation is:

```ts
h += Math.log(w);            // src/zhc.ts:197 — no sign
```

Every term is added. Nothing is ever negated. The code computes `log(product of weights around
the cycle)`, not the signed telescoping sum. Under the constraint semantics the docstring itself
states (`p_v - p_u = log(w)`), traversing an edge **backwards** must contribute `-log(w)`; this
adds it.

### The fail-open, demonstrated

A triangle `a-b = 0.5`, `b-c = 0.5`, `a-c = 4.0` — an utterly incoherent constraint system:

```
PROBE triangle   : {"consensus":true,"violations":[]}
  cycles found   : 1
  holonomy       : 0                       <-- the cycle WAS found, and scored exactly zero
  TRUE signed holonomy : -2.772589         <-- what the docstring promises
  CODE  unsigned sum   :  0.000000
```

`log(0.5) + log(0.5) + log(4) = 0` exactly, so the library certifies **perfect zero-holonomy
consensus**. The true signed holonomy is **-2.77** — five orders of magnitude outside the `1e-6`
tolerance. The cycle is found, traversed, and scored; the score is just the wrong quantity.

**Why anyone should care:** this is published as `@superinstance/fleet-math`, and the ZHC check is
a *gate* — `checkConsensus()` returning `consensus: true` is the thing you would wire into a
fleet as "are these agents compatible?" The gate returns green on incoherent input. It does not
fail loudly or produce a false negative; it manufactures a zero.

### MUTATION-VERIFIED: the correct implementation is invisible to the entire suite

I applied the one-line mathematical fix (`h += (u < v ? 1 : -1) * Math.log(w)`) and re-ran the
repo's **real, unmodified** 31-test suite:

| | suite result | independent probe |
|---|---|---|
| as published | **104 assertions, 0 failed** | `consensus:true`, holonomy `0.0` |
| with correct sign | **104 assertions, 0 failed** | `consensus:false`, holonomy `2.7725887` |
| restored | **104 assertions, 0 failed** | back to `0.0` |

The suite **cannot distinguish the bug from the fix**. The fix produces precisely
`|-2.772589|` — the true magnitude — and not one of 104 assertions notices.

**Root cause of the blindness:** in every cycle the suite constructs, the edge that gets
traversed backwards has weight exactly `1.0`, and `log(1) = 0`, so the sign is multiplied by
zero. The suite tests the *unsigned product rule* and mistakes it for holonomy — and says so in
a test name:

```ts
it('should achieve consensus when weights multiply to 1 (non-trivial)', () => {
  g.addEdge('a','b',2.0); g.addEdge('b','c',0.5); g.addEdge('a','c',1.0);
```

That test is labelled "non-trivial" and is in fact the only non-unit case in the suite. It lands
on `a-c = 1.0`, so it cannot fail. **A test suite that passes identically before and after a
semantic fix is not evidence of correctness — it is evidence that the semantics are unconstrained.**

### Credit where due — this is careful code otherwise

`addEdge` rejects non-positive/non-finite weights and self-loops, with comments that correctly
diagnose *why* (`|NaN| < tol` is false but `Math.abs(NaN) > tol` is also false, so NaN would
silently pass a naive check). `checkConsensus` has an explicit `Number.isNaN` guard for exactly
that. Those are real defensive instincts — the sign bug is the one place the same care wasn't
applied. CI is genuine (typecheck -> build -> test, 31 tests via vitest, node 20). The defect is
narrow and the fix is one line.

**Laman is sound** — `isRigid` runs the real (2,3)-pebble game, not just the edge count, and an
exhaustive all-subsets check exists alongside it. I initially suspected the subset condition was
missing (my `K_3,3` probe returned `true`); `K_3,3` is in fact Laman, so that thread is closed.

**One-line fix:** negate the contribution when the cycle traverses an edge against the reference
orientation, and add the regression case `(0.5, 0.5, 4.0)` — the one the current suite cannot
express.

---

## 2. `grand-pattern-experiments` — every falsifiable number reproduces EXACTLY under independent reimplementation

This is the **positive control**, and it is worth as much as the defect above. A single-file
31,072 B Rust crate testing "Grand Pattern theory" (vibe diffusion, surprise cascades,
conservation under GC, topology, dissolution). No cargo in this sandbox, so I transcribed the
algorithm from `src/main.rs` into an independent Python implementation and re-derived every
number the docs claim.

**Convergence ticks (10 rooms, room 0 at vibe 1.0, rest 0.5, diffusion 0.1, threshold 0.01):**

| topology | claimed | re-derived | delta |
|---|---|---|---|
| ring | ~460 | **460** | 0 |
| star | 35 | **35** | 0 |
| chain | 159 | **159** | 0 |
| mesh | 504 | **504** | 0 |

**Surprise cascade peaks (5-room chain, `[0.1x5, 0.95]` injected at room A):**

| room | claimed | re-derived | delta |
|---|---|---|---|
| A | 0.635 | **0.635000** | 0.00000 |
| B | 0.573 | **0.572557** | -0.00044 |
| C | 0.524 | **0.524185** | +0.00018 |
| D | 0.509 | **0.508940** | -0.00006 |
| E | 0.508 | **0.507480** | -0.00052 |

All nine reproduce; the residuals are the 3-decimal rounding in `CONCLUSIONS.md`. **A different
language, a different implementation, the same numbers to the digit.** This is the standard the
rest of the fleet should be measured against — and note what it took: the crate states its
setup precisely enough to be re-derived by someone who has never seen it.

### Two defects, both small

**(a) `README.md:31` contradicts the program's own output and its own `CONCLUSIONS.md`.**

- README: *"Star topology converges fastest (35 ticks), **chain slowest (159 ticks)**"*
- `main.rs:694` prints: *"Star converges fastest (35), chain moderate (159), **mesh slowest (504)**"*
- `CONCLUSIONS.md:28`: *"**Mesh topology:** Surprisingly slow convergence (tick 504)"*

The README is simply wrong about which topology is slowest, and it is wrong in the one direction
that understates the most interesting result — the counterintuitive one, that full connectivity
converges *slowest*. The deeper doc got the interesting case right; the headline doc dropped it.

**(b) The surprise-leak channel contributes ~0.2% of the signal it's named for.**
`surprise_accumulator` is written only by `inject_input` and scaled by `(1 - gc)` in `tick` —
it is **never incremented by propagation**. In this experiment `gc_aggressiveness = 0`, so the
accumulator never decays and never spreads: the only non-zero accumulator in the whole run is
room A's, so the leak fires only at hop A->B, worth `0.0014` against a `0.635` peak. The measured
"surprise cascade" is 99.8% plain diffusion of the `dims[5]` channel. The result is real; the
mechanism the README names is not the mechanism that produced it.

CI is genuine and strict — `cargo check`, `cargo test`, `cargo clippy -- -D warnings` on
push/PR. **0 canary references** and no `substrate-*` deps, so it installs standalone.

---

## 3. `ternary-benchmark` — the honesty note is scoped to the wrong axis

This crate does something the fleet rarely does — it opens with a warning about itself:

> *"**Honesty note.** The kernel model is **analytic/simulated**, not a measurement of real GPU
> workloads. ... Treat the kernel numbers as a reasoning aid, not a benchmark report."*

That is good practice, and the constants are honestly labelled at the source
(`src/kernel.rs:92-94`, `// Simulated`). The README status table also correctly marks
*"Real GPU measurement — not implemented"*, and the 40 `#[test]`s genuinely cover the modules
that carry none of their own (`tests.rs` exercises `Exhaustive`, `Evolution`, `Ecology`,
`BenchmarkSuite`, `BenchmarkReport`, `Scaling`). Credit all of that.

**The gap is what the note doesn't cover.** The note disclaims the *timing* model, but two
numbers in the same `KernelResult` struct are un-disclaimed:

**(a) The headline speedup is a product of two invented constants, and it is not 5x — it's 160x.**
`fp32_time = fp32_ops / 10_000` and `ternary_time = ternary_ops / 50_000`, so
`speedup = 5 * (fp32_ops / ternary_ops)`. With `fp32_ops_per_element = 2n` and
`ternary_ops_per_element = n/16`, the ops ratio is a flat **32**, giving a constant **160x** for
any `n >= 16`. The throughput ratio (50/10) and the packing ratio (16) are both hardcoded
modelling choices. A 160x ternary-vs-FP32 matmul claim is a *very* strong headline, and it is a
restatement of two arbitrary literals. "Analytic model, not a measurement" is true and still
understates it: the number is not a weak measurement, it is the model's own input echoed back.

**(b) `accuracy_loss_pct` is a hardcoded linear ramp presented as a property of ternary
quantization**, with no source anywhere in the repo:

```rust
// Accuracy loss: ~1.5-3.5% for well-trained ternary, growing with tensor size.
let accuracy_loss = 1.5 + (self.element_count as f64 / 1_000_000.0).min(2.0);
```

That is `1.5 + min(n/10^6, 2)`. It ships in the same result struct as the modelled times, under a
comment citing a literature range the code does not implement. **This is the axis the honesty
note should have covered** — not the timing, which is already labelled.

**(c) A `.max(1)` floor turns the benchmark into a step function.** Both times floor to 1 us, so
every matrix whose op count is under 10,000 reports **exactly 1x speedup** regardless of the
model. The discontinuity between "1x" and "160x" is an integer-truncation artifact at
`fp32_ops = 10,000`, not a physical result.

---

## 4. `quilt-edge-lab` — receipt discipline worth copying, with no gate to copy it into

47,447 B of JS across 8 files, a live Worker, and the most complete *process* documentation in
this batch. `PREREG.md` before the run, `DEBRIEF.md` after, three **sealed instrument FAILs**
(`E-CF-2`: per-request wall clock reads 0 ms because isolate clocks are frozen — so the fix was
to measure *accumulated* repeats, and the FAIL log ships in `receipts/`), and `pins-failfirst.log`
sitting next to `pins-final.log`. **"FAIL receipts ride forever" is actually implemented here, not
just asserted.** The `E-CF-1 determinism PASS` claim is backed by `GET /compare` doing real tail
+ full-chain equality.

**Structurally weak anyway:** one source file (`src/worker.js`), **no `tests/` directory, no CI
workflow, no canary reference.** So every sealed receipt is a *claim about a run*, verified by a
human reading a log — there is no automated gate that could fail. The culture is the artifact
here, not the verification. Copy the debrief discipline; do not assume the receipts are enforced.

---

## 5. Fleet-wide: 0 of 5 unseen repos reference the canonical canary

`grep` for the canary integer across all five examined repos: **0 hits in 0 files, all five.**
This is the same gap already logged for `quilt-i2i` (fixable by importing `FLEET_CANARY_HASH`),
now measured on five more repos that all present as fleet infrastructure.

**Canary + accent trap re-verified this pass** (compare the INTEGER, never the text):

```
cafe-accented   : 0x24a555471370b18d   MATCH
cafe-unaccented : 0xfee91cf40962b966   renders identically on screen
```

---

## Ranking

1. **`fleet-math-ts` ZHC fails open** — a published consensus gate that returns `true` on a
   holonomy of -2.77, with a 104-assertion suite proven *incapable* of detecting the difference
   by mutation. Only finding here that is both reproducible and actionable.
2. **`grand-pattern-experiments`** — nine numbers, nine exact reproductions, cross-language.
   The fleet's best evidence that its science is real. Fix one README line.
3. **`ternary-benchmark`** — a 160x headline that is two hardcoded literals, and an
   `accuracy_loss` formula with no source in a repo that otherwise models its own limits well.
4. **`quilt-edge-lab`** — real debrief culture, no executable gate.
5. **Canary adoption 0/5** — recurring, cheap to fix, now measured on five more repos.

**Reusable methods this pass:** (i) a self-measuring gate is proven blind by mutating the
*semantics* and confirming the suite stays green — stronger than mutating a constant; (ii) for
any doc claiming falsifiable numbers, re-derive them in a second language before trusting the
README's *summary* line — here the summary was wrong and the deep doc was right; (iii) when a
docstring specifies a formula, diff the docstring against the code operator by operator — the
divergence *was* the bug. (iv) `node --experimental-strip-types` runs TS directly if you rewrite
extensionless relative imports to `.ts` and mark type-only imports `import type`; a small
`describe/it/expect` shim plus a local `vitest` stub runs the real test file unmodified when
`npm install` is unavailable.
