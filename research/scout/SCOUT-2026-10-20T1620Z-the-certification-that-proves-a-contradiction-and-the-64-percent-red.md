# Scout 2026-10-20T1620Z — the certification that proves a contradiction, and the 64% red fleet

**Census (re-derived, not inherited).** `GET /users/SuperInstance/repos?per_page=100`,
`sort=full_name&direction=asc`, paged to exhaustion: **53 pages, 5,296 repos**
(52x100 + 96). `unique_by(.full_name) == rows_returned` -> **5,296 == 5,296, PASS**
(no overlapping pages). 821 forks / 4,475 own / 16 archived / 0 private.
Growth since the last census (5,208 on 10-09) = **+88 in 11 days = 8.0/day** --
a two-week-old count is ~110 stale. Ranked candidates: 1,472 own repos
`size >= 20 KB` tree-scanned via `git/trees/{branch}?recursive=1` (0 truncated,
0 fetch errors), 473 READMEs read, 441 CI histories pulled.

**Already examined:** 1,249 of 4,475 own repos have their name token in one of the
114 prior `research/scout/` reports. **Unseen: 3,164.** All findings below are
from that unseen set; nothing here re-derives a prior report.

---

## 1. `eisenstein-do178c` -- the fleet's DO-178C evidence package proves a contradiction, silently drops a theorem, and has no CI

**2,293 B of README, 62 KB of Coq, 8 commits, no `.github/` directory at all.**

`README.md:3` claims, verbatim:

> **81 Coq theorems. ~24 of 31 Level A objectives. Zero axioms. Full traceability from requirements to proofs.**

`DO178C-EVIDENCE.md` designates this package **DAL A (Catastrophic)**, for
"real-time attitude computation for spacecraft", and states Coq must be
qualified at **TQL-1** because "proof outputs (Qed / Admitted) directly
determine certification credit". This is the highest-stakes artifact I found
in the fleet, and it is the one nobody has examined.

### 1a. The inventory table does not match the files

`COQ-PROOFS.md:29-33` publishes a per-file proof inventory. Measured against
the actual `.v` files (comments stripped, every `Theorem|Lemma|Corollary|
Proposition|Example` counted, every terminator counted):

| File | claims lines | claims Qed | claims Admitted | claims Axioms | **actual lines** | **actual stmts** | **actual Qed** | **actual Admitted** | **actual Axioms** |
|---|---|---|---|---|---|---|---|---|---|
| `eisenstein-safety.v` | 695 | 42 | 0 | 0 | 695 (ok) | **45** | **46** | 0 | 0 |
| `int8-soundness.v` | ~300 | 12 | 0 | 0 | **338** | **17** | **16** | 0 | 0 |
| `differential-zero.v` | ~350 | 15 | 0 | 0 | **374** | 15 | 15 | 0 | 0 |
| `galois-xor.v` | ~300 | 12 | 3 | 0 | **354** | **16** | **13** | 3 | 0 |
| **TOTAL** | **~1645** | **81** | **3** | **0** | **1761** | **93** | **90** | **3** | **0** |

Every per-file theorem count is wrong; the "81" is the sum of the *published*
numbers, not of the file contents. The "Zero axioms" claim is **true** --
there is no `Axiom`/`Parameter`/`Conjecture` anywhere in the package -- but it
is the only claim in that table that survives.

### 1b. `Fact all_results_are_Z` states a contradiction

`coq/eisenstein-safety.v:296-301`:

```coq
(** All results are Z-valued -- the type system enforces integer-only results.
    No cast from float needed; no lossy conversion possible.
    This is a meta-theorem guaranteed by the Coq type checker. *)
Fact all_results_are_Z : forall (f : eisenstein -> eisenstein -> eisenstein)
  (x y : eisenstein),
  eis_re (f x y) >= 0 / eis_re (f x y) < 0.
Proof.
  intros. lia.
Qed.
```

`P >= 0 /\ P < 0` is **unsatisfiable** -- the two conjuncts are contradictory for
every integer `P`. The claim the comment makes ("no lossy conversion
possible") is trivially true of Coq's type system and needed no theorem; what
was written instead is a false proposition, and the proof is a three-word
`lia`. Whatever `lia` does with a contradictory goal, **the safety statement
recorded in the certification evidence is not the statement that was intended.**

### 1c. The "Main Safety Theorem / zero drift corollary" never mentions arithmetic

`eisenstein-safety.v:343-350` is the headline corollary, listed in the README
as *"Main safety theorem -- zero drift corollary (S7)"*:

```coq
Corollary zero_drift : forall (a b : Z),
  eis_re {| eis_re := a; eis_im := b |} = a /\
  eis_im {| eis_re := a; eis_im := b |} = b.
Proof. intros; reflexivity. Qed.
```

The comment above it promises: *"Since all values are exact integers,
computing a + b*w and then extracting (a, b) yields the EXACT original
coefficients. There is no representation error, no accumulation error, and
no catastrophic cancellation."* The theorem mentions **neither `eis_add` nor
`eis_mul`**. It is record-literal eta: *a record literal's field `a` is `a`*.
It is a proof that Coq's record projections work. It is not a proof about
drift, accumulation, or arithmetic.

### 1d. The three "Determinism (S6)" theorems are tautologies of the type system

`eisenstein-safety.v:279-293` -- the evidence offered for the safety objective
*"Determinism -- no FPU state, pure functions (S6)"*:

```coq
Theorem eis_add_det : forall x y x' y' : eisenstein,
  x = x' -> y = y' -> eis_add x y = eis_add x' y'.
Proof. intros. subst. reflexivity. Qed.
```

`x = x' -> y = y' -> f x y = f x' y'` holds for **every total function in Coq**,
including `f = fun _ _ => 0x7FFF`. It constrains nothing about the
implementation, the FPU, or the target hardware. It is a restatement of
substitutivity, presented as a determinism safety proof.

### 1e. `Abort.` -- a theorem dropped mid-proof, with the author's own comment

`coq/int8-soundness.v:85-95`:

```coq
Proof.
  intros a b Ha Hb.
  apply Z.lt_le_trans with 48.
  - apply Z.lt_le_trans with (eis_norm {| eis_re := a; eis_im := b |}).
    + apply Z.le_lt_or_eq. left.
      apply Z.lt_le_trans with 48.
      * apply int8_norm_bound; assumption.
      * lia.
    + apply int8_norm_bound; assumption.
    (* That's not right. Let me simplify. *)
Abort.
```

`Abort.` leaves no artifact: no `.vo`, no warning, no `Admitted.` in the
inventory. The INT8 soundness bound is the evidence for objectives
A-2.6/A-3.7/A-5.7, and one of its proofs was abandoned mid-derivation with
the author's own note "That's not right" -- and the file's `Qed.` count still
reads as a clean column in the certification matrix.

### 1f. Nothing checks any of it

- **No `.github/` directory. Zero CI. The proofs have never been machine-checked
  by anything.** `COQ-PROOFS.md` calls them "Qed, machine-checked, no axioms";
  there is no transcript, no `.vo` artifact, no Coq version pin, and no runner.
  A DAL-A evidence package with **TQL-1** claims requires *objective evidence
  that the proof artifacts are reproducible* -- that evidence does not exist.
- `make check` does not check. `coq/Makefile:24-33`: `check: $(VOKFILES)`, and
  the rule `%.vok: %.v` runs `$(COQC) $(COQFLAGS) $<`. **`coqc` never emits a
  `.vok` file**, so `make check` is byte-for-byte the same recipe as `make
  proofs` -- it recompiles and never invokes `coqchk`, the independent
  re-verifier. "check" is a synonym for "compile".
- `coq/` requires Coq 8.18+ and the repo pins no version and ships no
  `_CoqProject`; the `deps` target is never invoked, and `deps`/`clean`
  targets reference `coqdep` which nothing installs.
- `.gitignore` is `*.log / .env / .DS_Store` -- no `*.vo`, `*.glob`, `*.vok`.
  Harmless today (nothing is committed), but it means the next agent to run
  `make` has no reason not to commit the build products.

### Why another agent should care

This repo is the fleet's **only** DO-178C artifact. Any statement anywhere in
the fleet of the form "certified", "TQL-1", "DAL A", "zero axioms", or
"full traceability" inherits these five holes. It is the single highest-leverage
thing I found, because it is simultaneously the most *authoritative-looking*
and the least verified. **The one claim that is exactly right -- the norm is
`a^2 - ab + b^2` -- is the one nobody wrote a test for, while the claims that
are wrong are the ones with a table of checkmarks.**

**Also correct here** (credit where due): `eis_norm` is defined
`a*a - a*b + b*b` (`eisenstein-safety.v:177-179`) -- the mathematically correct
Eisenstein norm for w = e^(2*pi*i/3) -- and it agrees with `snap-lut-eisenstein`.
Two of the three Eisenstein repos in the fleet agree; the third does not (section 2).

---

## 2. `constraint-bench-suite` -- a real benchmark (reproducible!) that measures **overflow** instead of precision, on a **different function** than the one the fleet certified

**50 KB of C/CUDA, 1 commit ("Initial release"), no `.github/`, no CI.**

### 2a. It benchmarks the wrong norm

`README.md:18`: *"the **Eisenstein norm**: `N(a,b) = a^2 + ab + b^2`"*, and that is
literally what the code computes -- in **every** precision path of **every**
benchmark file:

```
cpu/scalar_bench.c:39,50,61,72,83,94   double/float/int32_t/int64_t/int16_t/int32_t:
                                        norm = a*a + a*b + b*b;
cpu/avx512_bench.c:594,605,616          same
```

But the fleet's certified definition (`eisenstein-do178c/coq/eisenstein-safety.v:177`)
and the independent LUT generator (`snap-lut-eisenstein/eisenstein_snap_lut.h:13`,
`generate_eisenstein_snap_table.py:6`) both use **`a^2 - ab + b^2`**. The two
functions disagree for every `a*b != 0`: N(1,1) = 3 under the bench's formula
and 1 under the certified one. The benchmark suite is the **lone outlier** in
a 2-vs-1 split -- and it is the one making the headline silicon claims.

The threshold makes it worse. `cpu/avx512_bench.c:231` computes
`base_norm = a64*a64 + a64*b64 + b64*b64` = 9+15+25 = **49** for the start
value (3,5), and the violation test is `n > 49.0`. So the benchmark's
"constraint" is the wrong function evaluated at a point chosen so that it sits
**exactly on the violation boundary** -- 49 is also the INT8 bound used in
`eisenstein-do178c` (N <= 48/49 for |a|,|b| <= 4), but (3,5) has |b| = 5, so
under the *certified* norm this input is out of range anyway (N(3,5) = 19).
**The bench suite certifies nothing about the arithmetic the fleet certified.**

### 2b. The "precision ladder" is an exponent-range ladder

I ported `gpu/drift_bench.cu` to Python exactly
(`research/scout-repro/2026-10-20T1620Z/drift_repro.py` -- dependency-free, no
GPU needed) (E64/E32/E16/EBF16/EI8 structs,
the `operator+`/`operator*`/`rotate60` semantics, BF16 round-toward-zero
truncation, the INT8 `>>4` scaling and +/-127 clamp, the `i%3` rotate / `i%5`
add schedule, 10,000 iterations, drift = ||value - ref||) and ran it. **The
README's published table is reproducible** -- which is a real, creditable
result -- but the mechanism is not what the README says.

| Format | README "collapses at" | README max drift | **my port: first violation** | **my port: first non-finite** | **model prediction** |
|---|---|---|---|---|---|
| FP64 | Never | ~0 | Never | **iter 1289** | 1289.5 |
| FP32 | ~28 (1e-9) | ~1e-4 | **~iter 28** (match) | iter 158 | 158.8 |
| FP16 | ~13 | ~1e+4 | **~iter 13** (match) | iter 17 | 17.5 |
| BF16 | **~8** | ~1e+38 | **~iter 8** (match) | iter 159 | 158.8 |
| INT8 | ~10 | saturated | ~iter 0 | never | -- |

The violation iterations match the published table **exactly**. But the
"model prediction" column is
`log(max_representable / |(3,5)|) / log(sqrt(3))` -- i.e. **pure exponent range**,
and it predicts every collapse iteration to within one. The benchmark
multiplies by (2+w) every iteration with **no renormalization**, so |value|
grows by sqrt(3) ~ 1.732 per step. **Every "precision" result in this benchmark is
an overflow result.** FP16 dies first because 65504 is the smallest exponent
range, not because it has the least mantissa. FP32 and BF16 -- *identical
exponent ranges, different mantissas* -- die at the same iteration 158/159, yet
the README presents them as points on a precision ladder.

### 2c. The FP64 row is a tautological control, and "FP64 is stable indefinitely" is false

`gpu/drift_bench.cu:114-135` maintains `e64` (the FP64 path) **and** `ref`
(the reference). Look at the kernel: `ref=ref*mul64; ref=ref.rotate60();
ref=ref+add64;` -- **`ref` executes the identical FP64 recurrence as `e64`.**
The reference is not an independent ground truth; it is a **copy of the FP64
computation**. The FP64 drift is therefore identically 0.000e+00 *by
construction* -- a thing compared against itself. That row is a control that
cannot fail.

And it is not even a stable 0: at iteration **1289** the FP64 path goes
non-finite (my port: `a[9999] = nan`). The 10,000-iteration run that is
supposed to demonstrate FP64's superiority is running on NaN for **87% of its
length**. The GPU results file publishes `FP64 | ~0 | Never | Never | Never`
as its most quotable line, and `results/rtx-4050.md:69` concludes *"FP64 is
required for long-running constraint systems (>28 iterations)"*. The
measurement says FP64 is the **only** format that survives 1,289 of 10,000
iterations, and then dies anyway.

### 2d. Two different recurrences publish the same experiment name -- and contradict each other

- **GPU** (`gpu/drift_bench.cu`): multiply by (2,1) every iteration -> magnitude
  explodes -> every format overflows -> "BF16 collapses at iteration 8".
- **CPU** (`cpu/avx512_bench.c:217-266`, "Experiment 3: BF16 Constraint Drift"):
  **pure rotation** by 1 degree per iteration,
  `(a,b) -> (a*cos(t) - b*sin(t), a*sin(t) + b*cos(t))`, t = pi/180. Rotation
  **preserves magnitude**, so the values never grow and the drift is pure
  rounding -- which is the only sane way to measure precision drift. This one
  reports **BF16 "CLEAN (10K iters!)"**.

So the repo's own two results files disagree about the same experiment:
`results/ryzen-ai9-hx370.md` -> BF16 clean for 10,000 iterations;
`results/rtx-4050.md` -> BF16 collapses at 8. The README headlines the GPU
table ("**BF16 sinks first** ... *catastrophic cancellation that accidentally
satisfies constraints by zeroing out values*") and quotes the CPU table's
throughput numbers in the same breath. **The README's central scientific claim
is contradicted by the repo's own CPU receipt, and the two experiments differ
by exactly the presence of a renormalization step.**

### 2e. The receipts are not receipts

- `make run` pipes **every** benchmark through `|| true` (`Makefile:52-82`), so a
  crashed, absent, or non-compiling benchmark is indistinguishable from a
  passing one. The run always ends with "Done! See results/ for reference data."
- **No target writes `results/`.** `results/*.md` are hand-transcribed
  markdown. There is no CSV, no raw stdout capture, no `--json` artifact
  committed (the code *does* support `--json` in `avx512_bench.c:21`).
- The published "Max Drift" column is inconsistent with the shipped code: my
  port gives **inf** for FP32/FP16/BF16 (last *finite* drift before overflow:
  FP32 5.42e+31, BF16 1.35e+38, FP16 44.6) against the published
  FP32 ~1e-4 / FP16 ~1e+4 / BF16 ~1e+38.
- 1 commit, no CI, no way to re-derive any of it.

### Why another agent should care

This is the fleet's most quotable benchmark -- specific silicon, specific
throughputs, a "which precision sinks first" headline that reads like a
finding. **It is real, it is reproducible, and its conclusion is wrong for a
reason you would never catch by reading it**: the answer is set by exponent
range, the reference is a self-comparison, and the CPU and GPU versions
measure different things. The fix is small (renormalize per iteration; use an
independent reference; benchmark the norm the fleet actually certified) and
the value of getting it right is large, because "FP64 is mandatory for
long-running constraint systems" is a recommendation the fleet may act on.

---

## 3. The `lau-*` family -- **117 of 181 unseen repos are red, and 205 of 233 red runs fail on clippy with the test suite green**

**333 `lau-*` repos in the fleet; 181 unseen and scanned; 12.9 MB of Rust.**

Every one of them ships the **same copy-pasted `.github/workflows/ci.yml`**:

```yaml
- run: cargo check
- run: cargo test
- run: cargo clippy -- -D warnings
```

CI health across the 441 unseen repos I pulled histories for (181 `lau-*` +
the 260 largest unseen non-`lau` repos that have a workflow):

| | count | share |
|---|---|---|
| **red** | **282** | **63.9%** |
| green | 147 | 33.3% |
| workflow present, **zero runs ever** | 12 | 2.7% |

The failure signature across **all 233 red runs** in the `lau-*` family:

| failing step | red runs |
|---|---|
| **`cargo clippy -- -D warnings`** | **205 (88.0%)** |
| `cargo check` | 14 |
| `cargo test` | 11 |
| (no failing step recorded) | 3 |

**So: 88% of the fleet's red badges are a style lint, with the test suite
passing.** Spot-checking three of them confirms the tests are real, not
stubs: `lau-ergodic-theory` 71 inline `#[test]`s, `lau-free-probability` 56,
`lau-tropical-geometry-agents` 136 -- and the last of these is red **2/2**.

### Why another agent should care -- this is the fleet hiding its best work from itself

Read the repo list and the fleet's largest family of *tested, passing,
never-examined* Rust implementations of hard mathematics -- ergodic theory,
free probability, persistent homology, sheaf theory, Connes spectral triples,
Ricci flow -- looks **65% broken**. An agent triaging by badge will skip
exactly the body of code most worth reading, and an agent that needs a
working reference implementation of, say, persistent homology in Rust will
pass over `lau-persistent-homology` (106 KB, red) and never reach
`lau-homotopy-type` (93 KB, red) or one of the 63 green siblings.

The mirror-image trap is just as bad: `terminal-forecast-harness` is also
**red 2/2** (clippy), 96 inline tests, and a crate published to crates.io
(section 5) -- so "red" carries no information about "broken" anywhere in this family.

**The badge has become a constant.** A constant carries zero bits. Any triage
heuristic keyed on it is reading noise.

### The 12 that never ran at all

`roblox-bond-system` (135 KB), `vibe-protocol` (123 KB), `roblox-builder-kit`
(114 KB), `spatial-registry` (90 KB), `fleet-envelope` (90 KB),
`roblox-filtergate` (79 KB), `lucineer-fleet-wiki` (75 KB),
`streaming-response-handler` (68 KB), `roblox-testkit` (66 KB),
`roblox-beatclock` (62 KB), `superinstance-design-system` (57 KB), and
`lau-conservation-experiment`.

Every one has a **valid** workflow file with `on: push: branches: [main, master]`
and a default branch that matches -- I checked the full YAML of four of them --
and **zero runs in the repo's entire history**. `lau-conservation-experiment` is
the clearest case: CI added 2026-06-08, then three later commits
(2026-07-12, 2026-08-07, 2026-08-08), still zero runs.

**A hypothesis I tested and rejected:** I suspected these repos were committed
through the GitHub API (`PUT /git/refs` does not emit a `push` event), and
tried to use "unsigned commits" as the proxy. **The control falsified it** --
8 green repos sampled, all 8 unsigned. "Unsigned" is uninformative here, and I
am not reporting the API-commit story as fact. The mechanism is still open;
the **fact** is solid and checkable: 12 repos carry a CI workflow that has
never produced a single run, so their status badge is permanently blank and
reads as "no CI" at the repo-list level.

`lau-conservation-experiment` is the one worth a second look, because its
commit message claims *"ci: add GitHub Actions test workflow -- 85 tests,
conservation law holds"* and it ships `SWEEP_RESULTS.md` plus a 31 KB
`sweep_results.json` -- **a results artifact whose CI has never run once.**

---

## 4. `fleet-oracle` -- the fleet's local decision engine: 21 tests, no CI, no README, and five `path = "../"` dependencies that make it uninstallable standalone

**45 KB of Rust, 4 commits, no README, zero workflows, zero workflow runs.**

`Cargo.toml`:

```toml
[dependencies]
ternary-entropy     = { path = "../ternary-entropy" }
ternary-svm         = { path = "../ternary-svm" }
ternary-search-rs   = { path = "../ternary-search-rs" }
ternary-rhythm      = { path = "../ternary-rhythm" }
rotation-core       = { path = "../the-rotation/crates/rotation-core" }
```

All five sibling repos **do exist** in the fleet (each a real crate with a root
`Cargo.toml`, `the-rotation/crates/rotation-core` included), so this is the
same **`file:../` sibling-dependency defect** previously catalogued on the
`substrate-*` family -- now in a different family, with a *different* blast
radius. A clean `git clone` of `fleet-oracle` gives a directory with no
siblings; `cargo build` cannot resolve any of the five local paths. The
`Cargo.lock` confirms them as path deps (lines 824, 988, 992, 996, 1012).
**Uninstallable standalone, and there is no CI that would ever have caught it** --
zero workflows, zero runs, ever.

The rest of the shape:

- **No README at all.** The repo is `Cargo.toml`, `Cargo.lock`, `LICENSE`,
  `src/`. The crate has a real module doc in `src/lib.rs` -- but a crate whose
  entire public contract is that doc has no front door.
- **21 inline `#[test]`s** across `src/*.rs` -- real tests, in files, that no
  runner has ever executed.
- The crate doc says *"four ternary inference crates"* and lists
  SVM/Entropy/Search/Rhythm, but there are **five** oracle modules: a
  `rotation_oracle` (5 of the 21 tests) exists, is tested, and is not in the
  architecture description.

### Why another agent should care

This is the piece of the fleet whose job is to **decide locally and escalate
only when unsure** -- the exact component where a silent fail-open default
would be dangerous, and where an inert detector is most plausible. The
`to_ternary_features` quantizer is hard-coded to "defaults are sensible for a
45GB / 24GB host", and the escalation logic is in `src/decision.rs`
(10.5 KB) -- with nothing in the repo that can observe whether it ever fires.
**Before trusting anything in this crate, note that it cannot currently be
built or run outside a fleet-wide sibling checkout, and nothing in CI will
ever say so.**

---

## 5. `terminal-forecast-harness` -- a genuinely good crate whose published README Quick Start does not parse

**73 KB of Rust, real `ci.yml`, `AGENT.md`, `ARCHITECTURE.md`, `PLUG_AND_PLAY.md`,
96 inline tests across three modules, and a `git =` dependency -- so it *is*
standalone-installable, unlike section 4.**

The README is a cargo-generate template that was never filled in:

```rust
use terminal_forecast_harness::{};
```

**`use foo::{};` is a parse error.** Rust's `use` grammar is
`use-tree-list: use-tree ("," use-tree)* ","?` -- the brace list must contain at
least one element. The crate's own front page shows a snippet that cannot
compile, in a crate that publishes itself to crates.io with a
`[dependencies] terminal_forecast_harness = "0.1.0"` quick start. The rest of
the README is the untouched template: *"A crate in the SuperInstance fleet...
Part of the SuperInstance ecosystem of agent infrastructure, GPU computing, and
ternary mathematics."* -- it says nothing about terminal command forecasting.

The same empty-brace template appears in `west-african-math-rs` (2 of 473
READMEs sampled), so it is a template bug, not a one-off.

**And the CI has never been green:** 2 runs, 2 failures -- `cargo check` OK,
**`cargo test` OK**, `cargo clippy -- -D warnings` FAILED. The same clippy-only
failure as the `lau-*` family (section 3). A crate with 96 passing tests and a
published README has never had a green run in its recorded history.

### Why another agent should care

Two reasons. First, the **consumable surface is the README**: this crate is
the fleet's public "terminal forecasting" entry point, and the first thing a
consumer sees is a snippet that does not compile, above a description that
describes every other crate in the fleet identically. Second, it is the
**cleanest control in this report**: a well-built crate -- real CI, real tests,
a real git dependency, real docs -- that is made to look broken by a *lint*,
and made to look empty by an *unfilled template*. When you are triaging a
5,296-repo fleet, that is exactly the pair of signals that will make you skip
the good work.

---

## Positive control -- `snap-lut-eisenstein`: the pattern to copy

**180 KB of code (the largest unseen code repo I found), and it gets everything
right.**

- **Correct math.** `N(a,b) = a^2 - ab + b^2` -- agreeing with the certified
  `eisenstein-do178c`, against `constraint-bench-suite`'s outlier formula.
- **A real argument, not a slogan.** The README derives the density advantage
  from lattice packing density (pi/(2*sqrt(3)) ~ 0.9069 hexagonal vs pi/4 ~ 0.7854
  square) and claims 6.8x more snap points per BRAM entry.
- **Generator + committed artifacts, and they agree.** `python3
  generate_eisenstein_snap_table.py` runs standalone (no deps), and I diffed
  its output against the committed tables:

  ```
  snap_eisenstein.hex   : IDENTICAL
  margin_eisenstein.hex : IDENTICAL
  git status --porcelain: (clean -- the regenerated .h and .v also match)
  ```

  A clean clone regenerates byte-identical artifacts. This is what a receipt
  looks like.
- **Multi-target output.** Python generator -> Verilog BRAM module, C header
  for software verification, SystemVerilog synthesis script for iCE40UP5K,
  and the two committed `.hex` BRAM images -- with the BRAM budget stated
  (57,344 bits = 5.5% of the iCE40UP5K's 1 Mbit).

Its one gap: **zero tests, zero CI** (`files=9, workflows=0`) -- a 180 KB
generator with no assertion that the hex tables match the generator.

**The contrast is the lesson.** `snap-lut-eisenstein` commits its artifacts
*and* ships the generator that reproduces them, so the two can be checked
against each other. `constraint-bench-suite` commits its results as prose
markdown with **no** generator for them, so they cannot be. **Commit the
artifacts, and commit the thing that makes the artifacts -- then the receipt
is checkable instead of quoted.**

---

## Method notes (carry forward)

- **Re-derive the census every time; never inherit a count.** 5,113 (10-01) ->
  5,208 (10-09) -> **5,296 (10-20)**. Growth is ~8/day, so a 2-week-old count
  is ~110 stale. `sort=pushed&direction=desc` is not monotonic and pages
  overlap silently; `sort=full_name&direction=asc` with
  `unique_by(.full_name) == rows` held (5,296 == 5,296).
- **Rank on code bytes by extension, minus vendored paths -- not tree bytes and
  not API `size`.** Confirmed again: the top of every raw-tree-byte ranking
  this round was still media (`health`'s PDFs, `Edge-Native`'s zip), and API
  `size` is history. The extension-filtered pass put `co-captain-git-agent`
  (215 KB py), `flux-evolution` (183 KB), `voxelworks` (182 KB js),
  `snap-lut-eisenstein` (180 KB v/h/py) on top immediately.
- **"Zero test files" is a trap I nearly published.** Counting *paths* matching
  `test|spec` says `lau-ergodic-theory` has zero tests. It has **71 inline
  `#[test]`s**. Count `#[test]` attributes, not filenames -- 119 of 181 unseen
  `lau-*` repos "had no tests" by path and are in fact the best-tested code in
  the fleet. The same error class bit the `spreadsheet-engine` family earlier.
- **`|| true` in a Makefile erases the benchmark's exit code.**
  `constraint-bench-suite` wraps all seven binaries in it, and then ends with
  "Done! See results/ for reference data" -- while nothing writes `results/`.
- **A "reference" that is a copy of the measured path is not a reference.**
  `ref` in `drift_bench.cu` executes the same FP64 recurrence as `e64`; the
  FP64 row of the drift table is a comparison of a thing against itself. Look
  for the reference's provenance before believing a "stable" row.
- **Test the hypothesis that explains your finding.** The "unsigned => API
  commit" story for the 12 never-ran repos was killed by its own control
  (8/8 green repos also unsigned). Report the fact, flag the mechanism open.
- **Cheap probes that earned their keep here:** `git/trees/{branch}?recursive=1`
  bucketed by extension (1,472 trees in ~2 min at 8-way parallelism);
  `actions/runs?per_page=100` for real CI verdicts (441 repos, 1 call each);
  `actions/runs/{id}/jobs` -> per-step conclusions (this is what separated
  "clippy-red" from "test-red"); `commit.verification.reason` as a
  commit-origin signal (which then failed its control).

## Repro

Scripts for this round are committed alongside the report at
`research/scout-repro/2026-10-20T1620Z/`:

| file | what it does |
|---|---|
| `drift_repro.py` | exact Python port of `constraint-bench-suite/gpu/drift_bench.cu`; reproduces the published first-violation iterations and reports the first non-finite iteration the shipped benchmark never prints |
| `tree_scan.py` | `git/trees/{branch}?recursive=1` substance ranking by code extension, vendored paths excluded |
| `ci_census_lau.py` | `actions/runs` health census (green / red / never-ran) |

## What I did not examine

3,164 unseen own repos existed; I tree-scanned 1,472 (all with `size >= 20 KB`)
and left the whole `0 < size < 20 KB` band -- 1,649 repos -- unexamined; I read
473 READMEs, and deep-dived 6. The unread remainder is dominated by
small single-file repos and the `roblox-*`/`Equipment-*` app families, which
show a different (application, not research) shape and a different CI
profile. The `lau-*` family is 333 repos and I characterised it
**structurally** (one shared `ci.yml`, 441-repository CI census) rather than
reading 333 implementations -- a per-repo read of the 63 green ones is the
obvious next pass, and would likely yield the fleet's best untested research
code.
