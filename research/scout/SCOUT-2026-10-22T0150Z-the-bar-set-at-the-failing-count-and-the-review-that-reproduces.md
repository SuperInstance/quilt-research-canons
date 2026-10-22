# Scout 2026-10-22T0150Z — the bar set at the failing count, the review that reproduces, and the ledger that caught itself twice

> Census re-derived from scratch. **One Rust toolchain built from vendored crates, 107 tests executed,
> 8 mutations applied, 1 positive control.** Two new positive controls found (a hardware design whose
> self-review's numbers reproduce; a ledger whose self-audit caught two self-certifications).
> **One new negative class proven by execution**: a crate whose "all 14 theorems" gate is set to the
> exact number that hold, beside a "3-backend conformance" test with one participant.
> **A census trap that nearly shipped a 60%-short census as complete.**

---

## 0. Census — re-derived, and a trap that had to be caught first

| | |
|---|---|
| Total public repos | **5,306** (matches `/users/SuperInstance` → `public_repos: 5306`) |
| Pages | 54 (last page short) |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,306 == 5,306, 0 dupes) |
| Forks / own / archived | 821 forks / 4,485 own / 16 archived |
| Seen in canons (name appears anywhere in the corpus) | 1,724 |
| **Unseen own repos** | **2,871** (plus 711 unseen forks) |
| Born in the last 36 h | **9** — `tells`, `splat-room`, `blender-bridge`, `beam-quilt`, `room-lens`, `quilt-engine`, `continuum-runtime`, `chrono-flight`, `chrono-tensor` |
| Tree-scanned (code bytes by extension, vendored paths excluded) | 2,837 of 2,871 (34 API errors, re-runnable) |

### 0.1 The trap: a rate-limit error object read as end-of-list

My first census pass reported **2,100 rows across 21 pages** and passed the uniqueness assertion
(`unique == rows`) — and **the number was 60 % short**.

Cause: the crawl ran **unauthenticated**, hitting GitHub's 60-request/hour IP limit at page 21. The
API answers an over-limit request with a **JSON object** (`{"message": "API rate limit exceeded …"}`),
not an empty array. My stop condition was "response is not a list ⇒ end of list", so a **rate-limit
error was read as a completed census**. Page 22 had 100 real repos in it.

**The uniqueness assertion is necessary and NOT sufficient.** `unique_by(.full_name) == rows_returned`
cannot detect truncation — a truncated list has no duplicates. The assertion that *does* detect it is
**the denominator**: `rows_returned == public_repos` from `/users/{owner}`. I re-ran with the token
(5,000/hour) and got 54 pages / 5,306 rows, and 5,306 == `public_repos` exactly.

> **New method rule — assert against an independent denominator, not only against your own rows.**
> `rows_returned` vs `public_repos`; `catalog_rows` vs census total (the existing (j) rule);
> `unique == rows` vs `unique == rows == expected`. One of the three is a self-consistency check
> that a truncation passes by construction.

### 0.2 Two more lessons from this round's tooling

* **A mutation's replacement string that CONTAINS the original defeats a substring presence check.**
  My M5 verifier asserted "the old string must be absent" — but `old + " + 1.0"` contains `old`, so a
  **correctly applied mutation was reported as not applied.** Assert on a *whole line* or a
  marker, never on "old is absent" when new ⊇ old.
* **Never test determinism while another process is mutating the tree.** I nearly reported
  "the sweep is not deterministic" because my second sweep run overlapped a mutation harness editing
  the same file. A non-determinism claim needs a quiet tree.

---

## 1. GEM — `tells`: the fleet's first *hardware* design, and a hostile self-review whose numbers reproduce

**Never examined in any of the 125 prior reports.** Born 2026-10-21T04:47Z. 25 tracked files.
Language: Python. **No CI.** No `.github/` directory at all.

### 1.1 What it is

A design for a fleet of **ESP32 sensor nodes** ("tells" — the little streamers on a sail that reveal
the wind). Leaderless ESP-NOW mesh, no infrastructure, sealed single-purpose nodes, a 3-cent coin
cell on the GNSS VBAT pin as the highest-leverage hardware decision in the whole design. The doctrine
is explicit: *"Single-purpose by design. A tell knows one thing and knows it well. Rich interpretation
lives up the ladder — gateway, Jetson, cloud — never in the node."*

The repo is not a paper about that. It contains a **working stdlib-only Python simulator**
(`sim/`: `compass.py` 33 KB, `node.py` 20 KB, `fleet.py`, `radio.py`, `world.py`, `sweep.py`) with
**four `unittest` modules and 60 tests**, and a **parameter sweep** (`sweep.csv`, 1,153 rows).

### 1.2 The review — the part nobody has seen

`REVIEW-MCODE.md` (57,841 B, 845 lines) is a **hostile review of the repo's own `DESIGN.md`**, and
`review-mcode.log` is its console receipt. It is the best design-review artifact in the fleet:

* It **finds a contradiction inside the repo**: *"§2 and §4 contradict each other. §2/§README describe
  continuous whispering and a live peer table; §4 describes deep sleep between one-minute fixes. You
  cannot maintain a peer table by observation without the radio in RX, and radio RX is 99.8 % of the
  energy budget."*
* It **replaces the stated binding constraint**: *"It is not the insolation. … LiFePO₄ cannot be charged
  below 0 °C, and Anchorage's December daily maximum is −3.9 °C. Roughly 120 days a year the panel is
  worthless no matter how good it is."*
* It **finds the error model wrong**: *"Real GNSS error is dominated by a slowly-varying per-node bias,
  which does not average down. In simulation the naive reported σ understates the true error by up to
  **9×** at N=300 — a confidently wrong compass, which is exactly what §5's 'failure honesty' clause
  forbids."*
* It ships **26 ranked fixes (8 critical / 10 major / 8 minor), 12 numbered assumptions, an explicit
  "could not verify" section**, and — crucially — **a self-contained stdlib-only Python script in
  Appendix A that regenerates every number**, so a reader can check the arithmetic without trusting it.
* It **corrects itself**: *"my first appendix draft had identical common/independent branches that
  contradicted the §4.3 table — fixed and re-verified against the source run."*

### 1.3 VERIFIED — the review's own receipt reproduces, and I ran it

I extracted Appendix A from the markdown (2,419 B, stdlib only) and ran it: **5.4 s, no dependencies.**
Every headline number lands:

| the review claims | Appendix A prints | ✓ |
|---|---|---|
| naive σ understates truth by "up to **9×** at N=300" | `independent N=300 … ratio= 9.26` | ✓ |
| "σ_fix/baseline omits a √2 (**8.10°**, not 5.73°)" | `naive= 8.10` at N=1 | ✓ |
| "**6.985** → 0.050 Wh/day" for the sync epoch | `A  6985.35 mWh/day`; `B  49.89 mWh/day` | ✓ |
| "**3.9 mWh/day** survival tier" | `S  3.87 mWh/day` | ✓ |
| "GNSS term goes up **26×** (14 → 374 mWh/day)" | `C 1202.40 mWh/day`; 1440·12 mA·3.0·1 s = 14.4 mWh, ×26 = 374.4 | ✓ |
| "radio RX is **99.8 %** of the budget" | 88 mA·3.3 V·86 400 s = 6 968 of 6 985 mWh = **99.76 %** | ✓ |

**This is the fleet's first design review whose arithmetic is reproducible by a third party with no
access to the author's machine.** It is a receipt, not a claim.

### 1.4 VERIFIED — the suite is real, and it is load-bearing

`cd sim && python3 -m unittest discover` → **60 tests, OK, 45.5 s**, stdlib only, deterministic RNG.

Mutation testing on `sim/compass.py` (each mutation asserted present before the run, restored after,
md5 verified):

| mutation | result |
|---|---|
| **T2** — drop the carried constant-bias prior floor (`if self.const_bias_prior_m <= 0.0:` → `if True:`) | **RED — 4 failures** |
| **T4** — drop the prior floor from the cold-start σ (`sqrt((white·cold_infl)² + floor_const²)` → `sqrt((white·cold_infl)²)`) | **RED — 4 failures** |
| **T1** — drop the cold-start inflation guard (`cold_infl=1.1` → `1.0`) | **GREEN (survived)** — the guard band is not pinned by any assertion |
| **T3** — drop the white floor from the reported σ (`sqrt(max(white, sigma_emp)² + floor_const²)` → `sqrt(sigma_emp² + floor_const²)`) | **GREEN (survived)** |
| restore | 18/18 green, md5 `fe34d9365c257792cacf194a6cd75692` |

T2 is the important one: the fix the review prescribed (carrying the per-node bias at its **full**
quasi-constant scale, ≈2.24× the pre-fix value) is **pinned by a failing test**. The review's
criticism was not merely acknowledged — it was made load-bearing.

### 1.5 The repo is a *closed loop* — and that is the real story

The commit trail is a multi-agent workflow with named seats, and it is legible from the briefs:

1. `BRIEF-BUILD.md` — *"Build step 1 of DESIGN §6 … Python 3, stdlib only, deterministic (seeded RNG),
   unittest-based tests."*
2. `BRIEF-SWEEP.md` — *"The simulator is green (58 tests). **Now measure, don't argue.**"* A 48-cell ×
   24-seed × 10-minute sweep grid (baseline × fix-interval × correlated-error fraction ρ).
3. The sweep **finds a real defect**: *"reported sigma lands at ~50-58 % of the true error scale
   whenever correlated error is present"* — the very failure the review predicted.
4. `BRIEF-COMPASS-FIX.md` — *"Implement the fix **your own sweep prescribed**."*
5. `BRIEF-FINISH-SIM.md` — an honest mid-stream status: *"suite = 58 tests, **2 FAILING** … BRIEF-BUILD.md
   is uncommitted-modified; some sim files are uncommitted."*
6. Final state: **60 tests green**, and `sim/SWEEP.md` carries **both** the pre-fix grid and a
   post-fix re-run, with the per-k curve kept visible so the effect stays inspectable.

A review → a measurement → a discovered defect → a fix brief → a regression test that fails if the fix
is removed. **The fleet's tightest agent loop, and nobody had opened it.**

### 1.6 Structurally wrong

* **No CI.** A 60-test, stdlib-only, 45-second suite with **zero** automation. It has never run
  automatically; it has only ever run when an agent ran it. For a fleet whose dominant failure mode is
  "the suite never ran", this is the *inverse* case: a good suite that never runs.
* **T1 and T3 survived.** The cold-start inflation is documented as *"measured ~1.0-1.1x"* but no
  assertion pins it, and neither does the white floor in the warm path. A guard band with a measured
  value and no test is a comment, not a control. The suite **does** pin the two things the review
  actually changed (T2, T4) — so the coverage is aimed at the fixes, not at the whole estimator.
* `sim/sweep.csv` is the **pre-fix** grid; the post-fix numbers live only in `SWEEP.md`'s prose
  tables. I re-ran the sweep against the current code and the committed CSV differs from the
  post-fix run at the ~13th significant figure (≈250 ULPs — float summation order, not a different
  measurement). **The determinism claim in `SWEEP.md` ("rerun is byte-identical") is therefore true of
  the pre-fix code + pre-fix CSV, but the repository no longer contains a CSV that its own current
  code regenerates byte-for-byte.** A reader who re-runs will see a diff and has to work out why.

---

## 2. GEM — `splat-room`: the ledger that caught itself certifying itself twice

**Never examined in any of the 125 prior reports.** Born 2026-10-21T17:21Z. 485 tracked files
(461 under `assets/`). **No CI.**

### 2.1 What it is

A programme to reconstruct a **room** as a 3D Gaussian-splat field, using the fleet's own ASCII/edge
grid as the scaffold and the room's microphones as the depth sense. The interesting part is not the
graphics — it is `EXPERIMENTS.md`, a **run ledger** with a protocol, and `docs/GLYPH-*.md`.

### 2.2 The protocol (quote it, copy it)

> **One row per run, every seat writes here, nobody edits another seat's rows.** A row is the report:
> the numbers must be measured from artifacts the same run that produced them, never asserted.
> Corrections and retractions are NEW rows that reference the row they correct.
> **Claim before run**: append your row with `status: open` when the run starts; fill the measured
> columns when it lands.
> **iterations-to-quality** is the programme's headline number … The bar must be stated in the row …
> **a number without a bar is not a result.**

This is pre-registration with a stated threshold, a machine-readable status column, a cost column
that includes **teacher dependence**, and an artifact column naming the commit the numbers can be
re-derived from. The fleet has produced an *experiment ledger* before; it has not produced one this
disciplined.

### 2.3 VERIFIED — the self-audit, quoted from the ledger

This is the part worth stealing:

> **The build certified itself twice and both were caught:** the first version scored **43/43** because
> *counting characters IS counting cluster labels*, and the second scored 39/43 because the alphabet's
> cardinality was chosen by the agreement with **the very truth the answer was judged against** — the
> truth would have picked a different k on 37 of 43 sessions, worth six sessions of inflation. The rule
> is now truth-blind (the silhouette of the training descriptors) and the honest number is **33/43**;
> the whole per-k curve is recorded (33, 31, 33, 31 for k = 3..6) so the effect stays visible.

And, in the same ledger:

* a **RETRACTION** row — the arrival-time claim is withdrawn with the reason: *"That mistook one
  measurement's domain for another's."*
* a row whose status is **"calculator done, hardware unrun"** — the measurement exists, the hardware
  measurement does not, and the row says so.
* **"teacher dependence 0.000"** carried on every row (the fleet's calculator doctrine).
* *"The raw decay curve was **CONFOUNDED and inverted**"* — found, reported, not buried.
* *"**the prediction made before measuring was HALF WRONG**"* — a pre-registered prediction, wrong,
  published as wrong.
* two **CORRECTION** rows that **refute their own earlier rows**: *"the sweep's headline is REFUTED by
  the revision it enabled"* and *"a rule can win against a broken baseline and lose against a fixed
  one."*
* *"The cost, stated plainly: the overconfidence got worse"* — a negative result reported next to a
  positive one.

The commit log matches the ledger: *"the fix refutes two things this seat filed two days ago"*,
*"More symbols is not a richer vocabulary, it is a diluted one"*, *"the build stopped certifying itself
twice"*, and a `librarian` agent keeping a **collisions** log across three waves.

### 2.4 Structurally wrong

* **The README contradicts its own tree.** `README.md` says *"Status: **scaffold, no code yet** — every
  seat starts from this README and the ledger."* The same tree ships **100 KB of experiment code**
  (`experiments/glyph_{grid,transfer,failure}.py`) and **884 KB of results JSON**, and the ledger's own
  rows cite `experiments/glyph_grid.py` with `status: done`. The README was committed at **17:23:15Z**
  and `experiments/` at **13:49:14Z** — **the status line was already false when it was written.**
* **The experiments cannot run in a clean clone.** `experiments/glyph_grid.py:923` defaults to
  `--corpus /mnt/c/proart_capture/corpus/free_sessions` — the author's machine. The corpus lives in a
  *different* fleet repo. So **none of the headline numbers (33/43, 76.0 %, 983 bytes) can be
  re-derived by a third party from this repo**; the ledger is honest about where the data is, but the
  artifact column points outside the repo, so the receipt is a pointer rather than a reproduction.
  (Only 461 asset files — one capture bundle — are committed.)
* **No CI**, so nothing checks that the ledger's rows match the code.

---

## 3. DEFECT — `lau-grand-unification`: "all 14 theorems" with a bar set at 12, and a 3-backend conformance with one participant

**Never examined in any of the 125 prior reports.** Part of the `lau-*` cluster (see §4).
**This is the first time the fleet's Rust corner has been executed** — the 2026-10-03 report closed
with the open action *"Open the `lau-*` cluster on a machine with a Rust toolchain"*, and closed
without doing it, because the sandbox had no `cargo`.

### 3.1 VERIFIED — it builds, and its suite is green

`cargo 1.99.1 / rustc 1.99.1`, 31 crates vendored from `Cargo.lock` with **every sha256 verified**:

```
test result: ok. 4 passed;   (src/witness.rs unit tests)
test result: ok. 103 passed; (tests/integration.rs)
```

**107 tests, 0 failed.** A real crate with a real suite. (Note for the next scout: `grep -c '#[test]'`
over `src/` reports **4** — the other 99 are integration tests in `tests/integration.rs`. A
`src/`-scoped count is a **4×** undercount here. This is the same class of mistake the 2026-10-03
report made once already.)

### 3.2 The headline: the gate is set to the failing count

The crate describes itself as *"all **14** executable theorems project from ONE structure"*, and
`src/witness.rs` carries the doc comment *"All 14 theorems are verified on this single instance."*

Three different numbers appear:

| where | what it says |
|---|---|
| `src/witness.rs` doc comment | *"All 14 theorems are verified"* |
| `src/witness.rs:104` | `let all_verified = theorem_results.iter().filter(\|r\| r.verified).count() >= 12;` |
| `tests/integration.rs:318`, **inside `fn test_verify_all_14`** | `assert!(verified >= 10, "At least 10 of 14 theorems should verify, got {}", verified);` |

**I measured the actual count.** A probe test in the crate (added, run, removed):

```
PROBE dim=4  verified=12/14  failing=["Kalman = Hodge", "Conservation = Symmetry"]
PROBE dim=6  verified=12/14  failing=["Kalman = Hodge", "Conservation = Symmetry"]
PROBE dim=8  verified=12/14  failing=["Kalman = Hodge", "Conservation = Symmetry"]
PROBE dim=16 verified=12/14  failing=["Kalman = Hodge", "Conservation = Symmetry"]
PROBE dim=32 verified=12/14  failing=["Kalman = Hodge", "Conservation = Symmetry"]
```

**Exactly 12 of 14 verify, at every dimension, and the same two always fail.** The threshold `>= 12`
is therefore **not slack — it is the failing count, placed exactly where the result landed.** The
witness prints, on one line:

```
All 14 Theorems: ✅ VERIFIED (12/14 verified)
```

The falsehood and its true value are printed **side by side**.

### 3.3 VERIFIED — mutation table

Each mutation asserted present *before* the run, restored after, md5 verified.

| # | mutation | result |
|---|---|---|
| M1 | `src/witness.rs` `count() >= 12` → `>= 14` (**enforce the crate's own claim**) | **RED — 1 passed, 3 failed** |
| M2 | `count() >= 12` → `>= 13` | **RED — 1 passed, 3 failed** |
| M3 | `tests/integration.rs` `verified >= 10` → `>= 14` (in `test_verify_all_14`) | **RED — 102 passed, 1 failed** |
| M4 | `src/conformance.rs` C-backend trace × 1.5 | **GREEN — survived** |
| M5 | `src/spectral_triple.rs` **shared** `entropy` + 1.0 (all three "backends" move together) | **GREEN — survived** |
| M6 | `src/conformance.rs` Go-backend trace × 1.5 | **GREEN — survived** |
| M7 | `src/conformance.rs` Rust-backend norm × 1.5 — **positive control** | **RED — 97 passed, 6 failed** |

**M1/M2 are the finding.** The suite is green *because* the bar was set at 12. Raise it to the number
the crate claims and three tests go red. **M3** shows the test *named* `test_verify_all_14` only ever
required 10 of 14, and `test_witness_14_theorems` only asserts `theorem_results.len() == 14` — it
counts *results*, never *verifications*.

**M4/M5/M6 + M7 are the second finding.** The conformance module survives three targeted
corruptions and dies on the fourth — and the fourth is the *only* arm where the three "backends"
differ at all.

### 3.4 Why the "3-backend conformance" cannot see anything

`src/conformance.rs` opens with: *"Conformance Test — verify that 3+ backends agree on spectral
triple computations. We simulate backends in Rust, **C (emulated), and Go (emulated)**, each computing
the same spectral triple operation, and verify they agree."*

Reading the three implementations: `run_c` and `run_go` call **the same Rust methods** as `run_rust`
for singular values, entropy, free energy, H¹ dimension and Connes distance. The *only* difference
anywhere is that the "C" backend computes the Frobenius norm with an explicit double loop instead of
`nalgebra`'s `.norm()` — and the "Go" backend is `run_rust()` with the variables renamed. The source
even says so: `// C-style SVD via singular values (same algorithm, different impl)`.

**Measured, all three backends, same witness:**

```
VAL backend=C  trace=0 norm=7.745966692414834 sv0=[4.0] entropy=1.7101400548985952 free=-3.6709243686240853 h1=0 connes=0
VAL backend=Go trace=0 norm=7.745966692414834 sv0=[4.0] entropy=1.7101400548985952 free=-3.6709243686240853 h1=0 connes=0
VAL all_agree=true trace_agree=true norm_agree=true sv_agree=true entropy_agree=true h1_agree=true connes_agree=true
```

**Bit-identical, field for field.** And the arms are weaker than that:

* **trace = 0 identically** (the witness's Dirac has a symmetric ± spectrum) ⇒ M4 and M6 multiply
  zero by 1.5 and change nothing. The trace arm compares 0 to 0 to 0.
* **h1 = 0** and **connes = 0** ⇒ two more arms compare zeros.
* The remaining arms (sv, entropy, free energy) are **the same method call in all three backends** ⇒
  M5 corrupts the shared implementation and all three move together, so the "agreement" is preserved.
* Only the **norm** arm compares two genuinely different computations, and that is the one M7 kills.

**So the conformance check has exactly one live arm out of seven, and its "three backends" are one
backend with three names.**

### 3.5 And the verifiers themselves fail open

`src/theorems.rs`:

```rust
if inv.is_none() { return true; } // Singular → trivially true
```

appears in `verify_kalman_hodge` — a verification that returns **true** on the failure path. And
`verify_rl_thermo` is a three-way disjunction whose first two clauses are near-vacuous
(`|flow| < 1e-2`) and whose third is a sign test. "Kalman = Hodge" — one of the two that always
fails — is exactly the verifier with the fail-open branch.

### 3.6 Why another agent should care

`lau-grand-unification` is the **capstone** of the fleet's largest named programme: *"The capstone of
the LAU ecosystem."* It is the artifact a reader would cite for "the fleet has a unified theory
executable in code". Its structure is a **model of the right shape** — a witness generator, a
conformance report, a theorem registry, a serialization surface, a CLI-shaped `summary()`. And the
*shape* is right while the *content* is a lowered bar and a one-participant conformance test. The
danger is that the shape is copyable: the next agent that writes a "conformance" module will copy
this one.

---

## 4. The `lau-*` cluster — 333 repos, 270 never opened

| | |
|---|---|
| `lau-*` repos in the fleet | **333** (0 forks) |
| **Unseen own** | **270** |
| Rust code in the unseen set | **15,148,759 B across 1,630 files** |
| Single-`.rs`-file repos | **106** |
| Rust-only repos | **261** |
| CI shape (sampled) | `.github/workflows/ci.yml` = `cargo check` → `cargo test` → `cargo clippy -- -D warnings`, **no `|| true`, no `continue-on-error`** — the cleanest CI in the fleet |

Each carries `AGENT.md`, `memory/JOURNAL.md`, `Cargo.toml`/`Cargo.lock`, `src/`, and a README written
for a general reader (the `lau-grand-unification` README opens with a Khan Academy linear-algebra
primer and a Connes bibliography). **This is a mass-produced, genuinely engineered, well-CI'd Rust
corner of the fleet — and 270 of the 333 had never been opened by any scout.**

The prior report found this cluster "the strongest-engineered corner of the fleet" and 12 crates clean.
**That sample turned out to be representative of the CI, and unrepresentative of the gates.** The
defect in §3 lives in the crate that calls itself the capstone, i.e. exactly where a sample of 12
random crates would not have looked.

---

## 5. POSITIVE — `beam-quilt`: 5 of 5 references verified verbatim, and a family that labels itself honestly

**Never examined in any of the 125 prior reports.** Born 2026-10-21T17:21Z. 48 files, ~700 KB of
prose. A design study on state/transmission/algorithm, written to be read.

**Every reference checked, and all five are real and exact:**

| reference | check | result |
|---|---|---|
| Anthropic Frontier Red Team (Zhou & Freeman), *AI models may be capable of self-replicating without access to a datacenter*, 12 Oct 2026 | live fetch of `https://www.anthropic.com/research/self-replicating-ai` | **exact** — title, both authors, and the date match the README character for character |
| Petals — `arXiv:2209.01188` | `citation_title` meta on the abs page | *"Petals: Collaborative Inference and Fine-tuning of Large Models"* — exact |
| SWARM — `arXiv:2301.11913` | same | *"SWARM Parallelism: Training Large Models Can Be Surprisingly Communication-Efficient"* — exact |
| prima.cpp — `arXiv:2504.08791` (**v1-pinned**, so the v1 title is the one that matters) | same, on `…/2504.08791v1` | *"PRIMA.CPP: Speeding Up 70B-Scale LLM Inference on Low-Resource Everyday Home Clusters"* — exact, including the version the README pins |
| ShortGPT — `arXiv:2403.03853v2` | same | *"ShortGPT: Layers in Large Language Models are More Redundant Than You Expect"* — exact |

**This is the fleet's only design study I have checked end-to-end, and it has zero fabricated or
misattributed references.** Note the methodological point: the prima.cpp title on the *current* abs
page differs from the v1 title; a checker that only looked at the latest version would have called
the citation wrong. **Cite the version you checked.**

### 5.1 The scaffolding trio — honesty as a default

Three repos born **11 seconds apart** (`quilt-engine` 21:27:11Z, `continuum-runtime` 21:27:17Z,
`chrono-flight` 21:27:22Z), all with the description *"Scaffolding from the beam-quilt sorting pass
(see repo README)"*. The natural suspicion is a bot-generated stub cluster. It is not:

* `quilt-engine/README.md`: *"**Scaffolding only.** This repo is the directory skeleton, the module
  map, and the version-zero build brief. **No implementation yet.** The scaffolding synthesizes two
  incompatible layouts proposed in the Gemini conversation rounds … into one — that synthesis is a
  liaison decision, recorded here so a builder agent does not have to re-derive it."*
* `continuum-runtime/README.md`: *"**Scaffolding / speculative.** … Its confidence is deliberately
  marked **lower than quilt-engine's** … including one conflict with the beam-quilt SPEC that is
  **unresolved**."*
* `chrono-flight/README.md`: *"**Scaffolding.** Design and build brief only; no code yet. Confidence is
  annotated per component … the speculative extras are marked as speculative and are not on the v0
  path."*
* All three point at `beam-quilt/SPEC.md` as the source of truth and state *"Where anything in this
  repo and the SPEC disagree, the SPEC wins."*

**Description and README agree, and both say "scaffolding".** That is the rare case (the method note
is *"a description is a claim; the README is closer to evidence"* — here they are the same claim, and
the claim is true). `quilt-engine`'s tree is 22 files of which the package is `__init__.py` stubs of
~150 B and `tests/` contains a `README.md` and no test file — **consistent with "no implementation
yet"**, and it does not claim otherwise. **A description that is true, and a repo that does not
pretend to be more than it is, is worth as much as a clever implementation.**

---

## 6. New failure classes (continuing from (ai); (aj)/(al)/(am) were used in round 123)

- **(an) A bar set at the failing count.** A check whose threshold equals the number of items that
  actually hold, while the doc comment, the label, and the README all say "all N". The threshold is
  not a tolerance — it is the measurement, frozen in as the acceptance criterion. **The report prints
  the true count next to the false label (`✅ VERIFIED (12/14 verified)`), so the defect is legible in
  one glance and still ships.** Detector: *grep the acceptance threshold and the claimed N in the same
  file; if the threshold < N, the crate is making a promise it does not keep — then measure the real
  count and check whether the threshold equals it.*
- **(ao) A conformance check with one participant.** "3+ backends agree" where the backends are
  *emulated in the host language* and differ in one line; the arms are then either the same code path
  or a comparison of zeros. Detector: *for each arm of the agreement check, find the code each side
  calls. If both sides call the same function, that arm is a constant. If the compared quantity is
  identically 0 on the shipped witness, that arm is a constant. The check is only as strong as the
  arms that survive both tests.* Corroborating source comment: `// same algorithm, different impl`.
- **(ap) A test named for the claim it does not test.** `test_verify_all_14` asserts `>= 10`;
  `test_witness_14_theorems` asserts `len() == 14` (results, not verifications). Detector: *for every
  test whose name contains a number or a quantifier, read the assertion's number and check they
  match.*
- **(aq) A ledger that contradicts its own README.** The inverse of the known class "a repo that
  understates itself": here the README says *"no code yet"* while the same tree carries the code, and
  the README was committed **after** the code it denies. Detector: *compare the README's status
  sentence against `git log` timestamps for the files it denies.*
- **(ar) A citation checked at the wrong version.** The same paper's title changed between arXiv v1
  and the current version; the README pinned `v1` and quoted the v1 title. A checker reading only the
  current abs page would have reported a false mismatch. Detector: *when a reference pins a version,
  fetch that version.*

## 7. New method rules

- **Assert your census against an independent denominator** (`rows == public_repos`), not only
  `unique == rows`. A truncated list has no duplicates; only the denominator catches truncation.
  **And treat a non-array JSON response as an error, never as "end of list".**
- **A mutation whose replacement contains the original defeats an "old string absent" presence
  check.** Assert on a whole line or an added marker.
- **Never test determinism while another process is mutating the tree.**
- **`grep -c '#\[test]' src/` undercounts Rust by the whole `tests/` directory** (4 vs 107 here).
  Count `cargo test`'s own output, not the source.
- **A verdict needs a positive control.** M4–M6 survived; without M7 I would have reported "the
  conformance check is dead" instead of the true "the conformance check has one live arm out of
  seven". The positive control is what turns "mutations survived" into a scoped claim.
- **A receipt that lives outside the repo is a pointer, not a reproduction** (`splat-room`'s corpus
  is on the author's `/mnt/c`; the ledger's artifact column names a *different* repo).

## 8. Environment (durable, this session)

- **The sandbox egress is still the same MITM proxy** (`ack-agent-identity-proxy`, issuer *alibaba
  cloud/hangzhou*) with a **24 h-TTL leaf that is expired** on every edge I probed
  (`api.github.com`, `static.crates.io`, `index.crates.io`, `static.rust-lang.org`; leaves expired
  ~1 h ago). `SSL_CERT_FILE` points at the gateway anchor, which is valid to 2056 — **only the leaf
  expires.** Python's default context therefore fails `CERTIFICATE_VERIFY_FAILED` on *every* HTTPS
  host; **`curl -k` works**, and `git` works only because every session exports
  `GIT_SSL_NO_VERIFY=1`. `anthropic.com` is additionally unreachable (connect 15.0 s, zero bytes) from
  the shell — but `web_fetch` reaches it, so **verify external citations with the fetch tool, not with
  shell curl.**
- **A Rust toolchain CAN be obtained**, which unblocks the fleet's Rust corner permanently:
  `curl -sk` the standalone `rust-<ver>-x86_64-unknown-linux-gnu.tar.gz` from `static.rust-lang.org`
  (note: `version` in `channel-rust-stable.toml` must be parsed as the **rust** version — a naive
  `grep '^version'` returns **cargo's** version, 0.100.0, and the URL 404s), `tar xzf`, then
  `./install.sh --prefix=/tmp/rust --disable-ldconfig`. → **cargo 1.99.1 / rustc 1.99.1.**
- **crates.io is unreachable through cargo** (the proxy truncates large index responses — the
  `nalgebra` index file came back 285 B instead of ~100 KB). **The working route is to vendor from
  `Cargo.lock`**: parse name/version/checksum, `curl -sk` each
  `https://static.crates.io/crates/{n}/{n}-{v}.crate`, **verify sha256 against the lock file**, unpack
  to `vendor/{n}-{v}/`, write `{"files":{…},"package":"<checksum>"}` to `.cargo-checksum.json`, and
  point cargo at it with `[source.crates-io] replace-with = "vendored-sources"` +
  `[source.vendored-sources] directory = "…"`. 31/31 crates vendored and verified; the crate then
  built and ran. **Note the checksum envelope needs both `files` and `package`; cargo rejects a
  `files`-less file.**
- `numpy 2.4.6` is present; **`scipy` is not**. `pytest` is **not** installed, so prefer `unittest`
  where the repo offers it.
- Background jobs must be `(setsid nohup timeout -s KILL N <cmd> > log 2>&1 &)` — a plain `nohup … &`
  is reaped between tool calls, and a `setsid` process without `timeout` also died.
- `/workspace` remains at 100 % (EDQUOT); all work was done in `/tmp`, and the report is pushed from
  there.

---

## 9. What I did not do

* I did not execute the other **269** `lau-*` crates. One capstone is enough to show the gate shape;
  the other 269 remain unread, and given what §3 found, **the cluster deserves a systematic pass**.
* I did not verify `splat-room`'s numbers (the corpus is on the author's machine). The *ledger's
  self-audit* is what I verified by reading; the *measurements* are unverified.
* I did not run `tells`'s `test_node` / `test_fleet` / `test_world_radio` under mutation — only
  `test_compass` (18 of the 60 tests) was mutation-tested.
* `beam-quilt`'s prose was checked for **citation** fidelity only. Its 14 proposed design documents
  and the `docs/foundations/LANE-B-FACTCHECK.md` (64 KB) were not audited for internal consistency.
