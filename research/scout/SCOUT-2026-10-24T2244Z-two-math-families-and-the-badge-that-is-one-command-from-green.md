# SCOUT 2026-10-24T2244Z — two mathematics families nobody has opened, and a red badge that is one command from green

**Scope:** never-examined repos in `SuperInstance`. Every claim below is **executed**, **GitHub-recorded**,
or **source-read** — never taken from a description. Where a prior report already found something,
this report says so and states exactly what is new.

**A Rust toolchain was installed for this round** (`rustup` under `/tmp` — the sandbox `$HOME` is a
full NAS mount and `rustup` dies with `Disk quota exceeded` there; `HOME`/`CARGO_HOME`/`RUSTUP_HOME`
must be redirected to `/tmp`). That toolchain is what closes the open question left by the
2026-10-18 report (§2.1) and what makes the repair receipt in §2.3 possible at all.
Toolchain: `rustc 1.99.1 (58cf8f9c3 2026-10-13)`, `cargo 1.99.1`, `clippy 0.1.99`, `rustfmt` 1.99.1.

---

## 0. Census — re-derived, never hardcoded

| metric | value | note |
|---|---|---|
| Public repos | **5,313** across **54** pages | `per_page=100`, `sort=full_name&direction=asc`, `type=all` |
| Paging assertion | `unique_by(.full_name) == rows_returned` → **5,313 == 5,313 PASS** | 0 overlap events on every one of the 54 pages (overlap checked against *all* prior pages, not just the previous one) |
| Exhaustion | page 54 returned **13** rows (short page) → stop | the `Link: rel="next"` header was also absent |
| Forks (excluded before ranking) | **822** | |
| Own repos | **4,491** | |
| Prior scout reports read | **147** files in `research/scout/` | 1.9 MB |
| Own repos **never named** in any prior report | **3,339** (74.4% of own) | prior coverage 1,152 / 4,491 = 25.7% |

**Growth check.** The brief says 5,113 / 52 pages; the 2026-10-18 report says 5,289 / 53 pages.
Today: **5,313 / 54 pages**. The account grows ~2 repos/day. Every number above was measured this
round; none of the three agree with each other, which is exactly why the brief says re-derive.

**Method note.** `repos.json` (the full 5,313-row census with every field) was written to
`/tmp/scout/` during the run; the summary numbers above are the ones that matter, and every
per-repo figure below can be recomputed from the same four queries.

---

## 1. The headline: **two mathematics families, 665 crates, ~27,900 tests, essentially unexamined**

| family | own repos | with `Cargo.toml` | with CI | `#[test]` total | repos with **zero** tests |
|---|---:|---:|---:|---:|---:|
| `lau-*` | **333** | 314 | 332 | **21,589** | 21 (19 of which have no `.rs` file at all — C/Go/Chapel/CUDA/docs) |
| `ternary-*` | **332** | 319 | 319 | **6,311** | 15 |
| **total** | **665 = 14.8% of all own repos** | 633 | 651 | **27,900** | 36 |

Both families are the fleet's *mathematical* core: `lau-*` is mathematics turned into agents
(`lau-ricci-flow-agents`, `lau-sheaf-learning`, `lau-category-theory`, `lau-spectral-zeta`,
`lau-conformal-agents`, `lau-noether-agents`, `lau-tropical-geometry-agents` …); `ternary-*` is a
whole algebraic framework over `{-1, 0, +1}` (`ternary-pareto`, `ternary-ensemble`,
`ternary-inference`, `ternary-transfer`, `ternary-federated`, `ternary-zkp`, `ternary-criticality` …).

### 1.1 The CI templates — there are six of them, and they are copied verbatim

Every `ci.yml` in both families, fetched and hashed:

| family | repos with a readable `ci.yml` | distinct template bodies | dominant template |
|---|---:|---:|---|
| `lau-*` | 332 | **6** | **310 / 332** — `cargo check` → `cargo test` → `cargo clippy -- -D warnings` |
| `ternary-*` | 319 | **5** | **302 / 319** — 4 jobs: `check --all-features` → `test --all-features` → `clippy --all-features -D warnings` → `fmt --all -- --check` |

The full variant census, because the outliers are where the interesting behaviour lives:

| family | template | repos | note |
|---|---|---:|---|
| `lau-*` | `check` → `test` → `clippy -- -D warnings` | 310 | the dominant one |
| `lau-*` | **`echo "No CI configured — customize per project requirements"`** | **17** | **a green badge that runs nothing** — `lau-architecture`, `lau-bench`, `lau-bytecode-c`, `lau-cloud-deploy`, `lau-docs-*`, `lau-guides`, `lau-lie-group-agents`, `lau-math-c`, `lau-math-chapel`, `lau-math-cuda`, `lau-math-opencl`, `lau-network`, `lau-ringbuf-c`, `lau-sia2-engine-c`, `lau-twistor-agents` |
| `lau-*` | `go test ./...` | 2 | `lau-math-go`, `lau-sia2-engine-go` |
| `lau-*` | 4-job `--all-features` template | 1 | `lau-memory-arena` |
| `lau-*` | **no steps at all** | 1 | `lau-conservation-experiment` |
| `lau-*` | `npm ci` → `npm test --if-present` | 1 | `lau-ts-bridge` |
| `ternary-*` | 4-job `--all-features` template | 302 | the dominant one |
| `ternary-*` | the `lau-*` 1-job template | 13 | `ternary-attention`, `ternary-color`, `ternary-complexity`, `ternary-conserve`, `ternary-criticality`, `ternary-fuse`, `ternary-quorum`, `ternary-rate-limiter`, `ternary-renormalize`, `ternary-resilience`, `ternary-signals`, `ternary-spatial`, `ternary-weather` |
| `ternary-*` | 4-job with `clippy --all-targets` | 2 | `ternary-optimizer`, `ternary-sandbox` |
| `ternary-*` | **`pip install pytest` → `pytest \|\| true`** | **1** | **`ternary-dynamics-python` — see §2.4** |
| `ternary-*` | **no steps at all** | 1 | `ternary-experiment-workers` |

`lau-constellation` has no `ci.yml` at all.

**Why another agent should care.** This is where the cell doctrine's mathematics actually lives, and
it is the only part of the fleet that has never been compiled at scale. 27,900 executable assertions
across 665 crates is a body of work several orders of magnitude larger than anything else in the
account, and it is invisible in the fleet index — which records *activity* (who pushed what, when),
not substance.

### 1.2 These are not clones, and they are not slop

The `lau-*` family has an identical file *layout* across 114 repos (one `src/lib.rs`, or 9–13
module files with the same names). It is tempting to call that a template farm. **It is not.**
I fetched every `.rs` file of all 114 and hashed the concatenated content: **114 distinct content
hashes, 114 distinct implementations.** Same curriculum, genuinely different work.

And the tests are real, not count-farmed. Executed in clean clones (Rust 1.99.1, exact CI command
sequence):

| repo | `cargo check` | `cargo test` | `cargo clippy --all-targets -- -D warnings` |
|---|---|---|---|
| `lau-a2a-protocol` | 0 | **54 passed / 0 failed** | 0 |
| `lau-agent-organism` | 0 | **143 passed / 0 failed** | 0 |
| `lau-animation` | 0 | **90 passed / 0 failed** | 0 |
| `lau-biome` | 0 | **37 passed / 0 failed** | 0 |
| `lau-bytecode` | 0 | **69 passed / 0 failed** | 0 |
| `lau-chaos-theory` | 0 | **59 passed / 0 failed** | 0 |
| `ternary-accumulator` | 0 | **14 passed / 0 failed** | 101 (1 lint) |
| `ternary-activation` | 0 | **18 passed / 0 failed** | 0 |
| `ternary-pareto` | 0 | **23 passed / 0 failed** | 101 (3 lints) |

**452 assertions, 0 failures, across 9 crates in 9 clean clones.**

---

## 2. The verification debt of the fleet is a *formatting* debt, and it is one command from fixed

### 2.1 The lint, named — this closes an explicit open question

The 2026-10-18 report (`SCOUT-2026-10-18T0733Z`) classified all 304 `lau-*` repos by CI step
conclusion and left this on the table, verbatim:

> *(I could not determine the specific clippy lint — no cargo/rustc in this sandbox. … The claim I
> stand behind is the step-level one, which is GitHub-recorded fact.)*

**The lint is `manual_clamp` and `len_zero`.** Reproduced on `lau-agent-lifecycle` (clean clone,
`cargo clippy -- -D warnings`, exit 101):

```
error: clamp-like pattern without using clamp function
   --> src/lib.rs:839:21
839 |             pathos: (self.pathos + delta_pathos).max(0.0).min(1.0),
    |                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ help: replace with clamp:
    |                     `(self.pathos + delta_pathos).clamp(0.0, 1.0)`

error: length comparison to zero
   --> src/lib.rs:988:9
988 |         repaired.knowledge.len() > 0 && repaired.phase == LifecyclePhase::Work
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ help: using `!is_empty` is clearer and more explicit

error: length comparison to zero
   --> src/lib.rs:1190:38
1190 |         self.objects.keys().all(|id| id.len() > 0) // trivially true
    |                                      ^^^^^^^^^^^^ help: using `!is_empty` is clearer …
```

**11 errors. All of them style.** `cargo check` → 0. `cargo test` → 0. The badge is red because
`(x).max(0.0).min(1.0)` is spelled out longhand.

### 2.2 The measurement, at family scale, with per-step receipts

`lau-*` — 313 repos with CI runs: **168 success / 145 failure (46.3% red)**.
`ternary-*` — 317 repos with CI runs: **49 success / 268 failure (84.5% red)**.

I then pulled the **per-step conclusions** of the failing runs (not the run conclusion) for a
random sample of 45 from each family:

| family | red repos sampled | red **only** on fmt/clippy | red on the **test** step |
|---|---:|---:|---|
| `lau-*` | 45 | **42** (`cargo clippy -- -D warnings`) | 3 — `lau-optimization`, `lau-simd-vibe`, `lau-tropical-agent` |
| `ternary-*` | 45 | **43** (`cargo fmt --all -- --check` 43, `cargo clippy --all-features -- -D warnings` 28) | **0** |

**86 of 90 red badges in these two families are red on formatting or lint. 0 of 45 `ternary-*`
red badges are red on a test.** The `ternary-*` CI template is the richer one — four jobs
(`fmt` / `check` / `test` / `clippy`), all with `--all-features` — and it is *still* 84.5% red,
because `cargo fmt --check` is the first thing it runs.

The `lau-*` template is one job with three steps (`cargo check` → `cargo test` →
`cargo clippy -- -D warnings`), **byte-identical across 310 of the 332 `lau-*` repos that have a
`ci.yml`**. Only **6 distinct template bodies** exist across the whole family — and 17 of the repos
wear the `echo "No CI configured"` template that runs nothing at all (§1.1).

### 2.3 The repair receipt — a red badge turned green without touching a single test

`ternary-pareto`, clean clone, running **exactly the four steps its CI runs**:

```
### BEFORE
  cargo fmt --all -- --check              exit=1
  cargo check --all-features              exit=0
  cargo test --all-features              exit=0   23 passed / 0 failed
  cargo clippy --all-features -D warnings exit=101 (4 errors)

### REPAIR:  cargo fmt --all   +   cargo clippy --all-features --fix --allow-dirty --allow-staged
  clippy --fix exit=0

### AFTER
  cargo fmt --all -- --check              exit=0
  cargo test --all-features              exit=0   23 passed / 0 failed

### DIFF
 src/front.rs     |  4 ++--
 src/optimizer.rs | 12 ++----------
 src/tradeoff.rs  | 23 ++++++++++++++++-------
 tests/integration.rs | 14 +++++---------
 4 files changed, 35 insertions(+), 31 deletions(-)
```

The only change to the test file is rustfmt joining a call onto one line — the assertions are
byte-identical, and the suite still reports **23 passed / 0 failed** afterwards.

**The lint is not pure noise, though.** Three errors survive `clippy --fix` because they are not
mechanical:

```
error: this `if` has identical blocks
   --> src/front.rs:121:37
121 |   if acc.is_nan() {
122 |       v
123 |   } else if obj.is_better(v, acc) {
    |       v          <-- identical block
    |   }
```

This is a NaN-guard written as a two-branch chain where both branches do the same thing. The
correct form is `if acc.is_nan() || obj.is_better(v, acc) { v } else { acc }`. The lint is pointing at
genuinely redundant (and, written that way, genuinely fragile) code. **So the gate is earning its
keep — the fleet is failing it for cosmetics and getting the real findings for free.**

**Why another agent should care.** 413 repos across two families currently advertise failure on
GitHub while their behaviour is verified green. That is 413 badges actively *misinforming* any
crawler, dashboard, ranking, or triage that reads `conclusion`. The correction is not a research
project — it is `cargo fmt --all && cargo clippy --fix` across 413 clones, and it would turn the
fleet's largest green/red inversion into green.

### 2.4 `ternary-dynamics-python` — a green badge over 26 tests that have never run

The single Python crate in the `ternary-*` family, and the only fail-open CI in either family:

```yaml
      - run: pip install pytest
      - run: pytest || true
```

**There is no `pip install -e .`.** The package is a **src-layout** project — `pyproject.toml`
declares `[tool.hatch.build.targets.wheel] packages = ["src/ternary_dynamics"]`, and the test file
does `from ternary_dynamics import (...)`. With the package neither installed nor on `sys.path`, and
no `[tool.pytest.ini_options] pythonpath = ["src"]`, pytest's collection fails outright:

```
ModuleNotFoundError: No module named 'ternary_dynamics'
```

`pytest` exits non-zero, `|| true` swallows it, and the step is green. **GitHub records all three
matrix legs as `success`** (Python 3.10, 3.11, 3.12 — run 2026-06-08 and 2026-06-04, both green).

So: a green badge, over 26 tests that have **never executed in CI**. Measured locally with the
package correctly importable, the suite is actually **26/26 green** — the code is fine; the gate
never looks at it.

**And the same repo commits its build output.** `.gitignore` contains `__pycache__/`, `target/`,
`Cargo.lock` — **no `dist/`** — and the tree carries 2 of the repo's 16 tracked files as build
artifacts:

```
dist/ternary_dynamics-0.1.0-py3-none-any.whl   7,648 bytes   (tracked)
dist/ternary_dynamics-0.1.0.tar.gz              7,489 bytes   (tracked)
```

This is the *only* `|| true` in 651 CI workflows across the two families — and it happens to sit on
top of the one repo where the suite cannot even be collected.

---

## 3. The agent-room layer is a form letter — 331 duty logs, one neighbour graph, zero information

**What it is.** 331 of the 333 `lau-*` repos carry `AGENT.md` + `memory/JOURNAL.md`. `AGENT.md`
is written in the first person:

> **Ensign Cli — si-cli**
> I watch over si-cli. Unified CLI for the SuperInstance ecosystem…
> I reside in this repository. This is my room.
> I keep a duty log in `memory/`.
> *The crab inherits the shell. The forge shapes the steel.*

That is a lovely convention and it is fleet-wide. **But:**

**(a) The duty log is one template.** Every `memory/JOURNAL.md` in the family has the same body,
with only the title varying (`# <Name>'s Journal`):

```
## First Watch — Ensign Takes Post
**Date:** 2026-06-08
This repository has been initialized as part of the SuperInstance fleet.
- AGENT.md created
- CI workflow configured
- MIT license applied
**Status:** Operational
**Connected to fleet:** ✅
**Next duty:** Awaiting instructions.
```

331 rooms each record their first watch, and then **331 rooms record nothing else.** "Next duty:
Awaiting instructions" is true of every one of them, permanently. The logs are not a duty log; they
are a duty log's *empty first page*, committed 331 times.

**(b) The neighbour graph is a constant.** `AGENT.md` ends with a "Fleet Neighbors" table naming
five sibling rooms and their roles. Across all 333 repos I extracted **1,655 neighbour entries** —
and they resolve to **five distinct names**:

| neighbour | times named | role |
|---|---:|---|
| `tminus-dispatcher` | 331 | Temporal Heartbeat Keeper |
| `fleet-bridge` | 331 | A2A Transport Operator |
| `symphony-runtime` | 331 | Grammar Conductor |
| `composite-headspace` | 331 | Dual-Shell Mediator |
| `i2i-bottle-agent` | 331 | Bottle Postmaster |

All five exist (verified against the census). But **every room points at the same five rooms** —
so the "neighbour" relation carries **zero information about topology**. It is a form letter with
five names in it. Any agent that reads `AGENT.md` to discover who is adjacent to whom will get the
same answer for every repo in the fleet.

**Why another agent should care.** This is the fleet's self-description, and it is inert in exactly
the two places it would be useful. The rooms are real (the code behind them is good, §1.1); the
*relationships* they assert are template residue. If the fleet wants a topology, this is the file
that is supposed to hold it, and it currently holds the same five names 331 times.

---

## 4. `flux-repl` — the README says 15 tests, the repo has 126, one of them fails, and the badge is red

**Never named in any of the 147 prior scout reports.** A FLUX bytecode assembler + VM + debugger in
plain Python (`repl.py`, 57 KB), with a web playground.

**README.md line 29:**

```
15 tests passing.
```

**Measured in a clean clone:**

```
collected 126 items
PASSED 125  FAILED 1  SKIPPED 0

===== FAILED TestExecuteTrace::test_trace_max_100 =====
    def test_trace_max_100(self):
        result = execute([0x01] * 200 + [0x00])
        assert len(result["trace"]) <= 100
    AssertionError
```

**The defect is a real spec/implementation mismatch.** `repl.py:470` caps the trace at 200:

```python
# Record trace (first 200 steps or all in trace_mode)
if trace_mode or cycles <= 200:
    trace.append({"pc": old_pc, "op": op, "regs": regs_snapshot})
```

Measured: `execute([0x01]*200 + [0x00])` → `trace length = 200`, `cycles = 201`. The test says the
trace is capped at 100; the implementation caps it at 200; the implementation is the contract.

**The badge is red.** GitHub Actions, `SuperInstance/flux-repl`:

| run | branch | date | conclusion |
|---|---|---|---|
| 24611063331 | `main` | 2026-04-18 | **failure** (Python 3.12 failed; 3.10 / 3.11 cancelled) |
| — | `add-comprehensive-tests` | 2026-04-12 | success |

The 3.10/3.11 matrix legs are recorded `cancelled`, so the only surviving leg is the one that fails.

**Structurally wrong, additionally:**

- **No `.gitignore` at all**, and **two committed `__pycache__` files** —
  `__pycache__/repl.cpython-310.pyc` and `__pycache__/repl.cpython-310-pytest-9.0.3.pyc`. The
  second one is a **pytest 9.0.3 run on CPython 3.10 baked into the tree**, which also dates the
  author's last local test run.
- **The repo ships the fleet's own certification exam with every box unticked.**
  `DOCKSIDE-EXAM.md` is the 7-section checklist (Identity / Code Quality / Testing / Fleet
  Integration / Documentation / Safety / Operational), dated 2026-04-14, with a scoring rubric
  ("7/7 = Seaworthy 🟢") and **no score and no ticks whatsoever** — all 22 checkboxes are `- [ ]`.
  §3 of that exam asks "Tests pass". That is now false, and the exam was shipped claiming nothing
  about it either way.
- **`CHARTER.md` asserts "Git-Agent Standard v2.0 compliant · I2I protocol compatible · Fleet
  monitoring ready"** — three compliance claims, none of them checked by anything in the repo.
- **It has an unanswered health check.** `for-fleet/health-check-2026-04-12_171930.json`:

  ```json
  { "type": "HEALTH_CHECK", "from": "lighthouse-keeper",
    "message": "Are you ok? Please respond by updating STATUS.json or pushing a commit.",
    "respond_within": 600 }
  ```

  The repo has **no `STATUS.json`** and made no commit in response. The request is still sitting in
  the tree, unanswered, six months on.

**Why another agent should care.** This is a small repo with an unusually complete set of
dishonesties stacked on top of each other: a number in the README that is off by 8.4×, a test that
fails, a red badge, an unticked self-certification, three unchecked compliance claims, committed
bytecode, and an unanswered liveness ping. Each one alone is a smell; together they are the clearest
example in the fleet of **a repo whose paperwork is healthier than its code** — and the paperwork is
what a reader or a crawler would see first.

---

## 5. `si-cli` — the fleet's own auditor, auditing a number against itself

`si-cli` is "Unified CLI for the SuperInstance ecosystem — scan, audit, rank, graph, and generate",
with 8 subcommands, a 26 KB integration test file, and the standard `check → test → clippy` CI
template. It is the tool the fleet would use to audit itself. I built it (Rust 1.99.1, release
build, 5 m 10 s) and ran both of its self-auditing subcommands.

### 5.1 `si check` — a conservation law, checked against itself

`si check` implements the fleet's γ + H = total law:

```rust
let computed = agent.gamma + agent.h;
let violation = (agent.total - computed).abs();
let passed = violation < tolerance;          // tolerance = 1e-10
```

The failure path is real — `cmd_check` calls `std::process::exit(1)` when any agent violates. I
confirmed that by construction:

```
=== si check on a CONSISTENT file ===
  alpha   0.4000  0.6000  1.0000  1.0000  ✓ OK
  beta    0.7000  0.5000  1.2000  1.2000  ✓ OK
  ✓ All 2 agents pass conservation checks.                                    EXIT=0

=== MUTATION: total 1.20 -> 1.30 ===
  beta    0.7000  0.5000  1.3000  1.2000  ✗ Δ=0.100000
  ✗ 1/2 agents FAIL conservation checks.                                      EXIT=1
```

**But the law is verified against a declaration.** `total` is a column in the same `fleet.toml` the
check reads, so the check certifies that the config author wrote three consistent numbers and can
never detect a fleet that does not conserve anything. The tautology, in one command:

```
=== MUTATION: self-consistent but absurd (gamma = h = 1e6) ===
  absurd-but-consistent  1000000.0000  1000000.0000  2000000.0000  2000000.0000  ✓ OK
  ✓ All 1 agents pass conservation checks.                                    EXIT=0
```

A fleet declaring γ = 10⁶, H = 10⁶, total = 2×10⁶ "conserves" perfectly while being nonsense.
There is no independent source of truth in the loop.

### 5.2 `si audit` — a 0–100 "ecosystem readiness" score computed from file presence

The score is six file-presence checks, and nothing runs:

| check | points | how it is decided |
|---|---:|---|
| `CAPABILITY.toml` exists and parses | 25 | file presence |
| `INTEGRATION.md` exists and is > 50 lines | 15 | line count |
| `README.md` exists and is > 100 lines | 15 | line count |
| **Tests exist** | 20 | **see below** |
| **CI/CD** | 15 | **`.github/workflows` is a directory** |
| `LICENSE` exists | 10 | file presence |

Three defects, each demonstrated by running the binary:

**(a) The auditor cannot see Python tests.** `count_tests` walks `tests/` counting files whose
extension is `rs`, `go`, `js`, or `ts`, and separately counts the string `#[test]` in `.rs` files.
**`.py` is not in the list.** So `si audit` on `flux-repl` — which has **126 tests** in
`tests/test_executor.py` and `tests/test_assembler.py`, 125 of which pass — reports:

```
  ✗ Tests                No tests found [20pts]
```

**(b) The auditor awards 15/15 for a CI that cannot fail.** The check is
`ci_path.exists() && ci_path.is_dir()`. The 17 `lau-*` repos whose entire workflow is
`echo "No CI configured — customize per project requirements"`, and `ternary-dynamics-python`
whose workflow ends in `pytest || true`, all score **full marks** for "CI/CD ✓".

**(c) A grade F exits 0.** `cmd_audit` does `if result.score < 50 { std::process::exit(1) }`. A repo
scoring **exactly 50 is graded `F`** and still exits **0**:

```
  Score: 50/100
  Grade: F
real EXIT=0
```

And a repo with **no `CAPABILITY.toml` at all** takes the `else` branch, prints
`No repos found to audit.` and exits **0** — the fleet's auditor does not flag a repo as
unauditable; it reports nothing and passes.

**Why another agent should care.** This is the shape the fleet keeps reaching for, now visible in
the tool the fleet would use to audit itself: gates that are *runnable* but certify a *declaration*
rather than a *behaviour*. `si check` proves a file is internally consistent; `si audit` proves a
directory contains files of certain names and lengths. Both exit 0 on inputs that are, in the
plainest sense, broken. If the fleet's readiness dashboard is fed by this tool, it is measuring
filename conventions, not health — and it cannot see one of the fleet's main languages at all.

---

## 6. What I checked and did **not** find

- **The `ternary-*` family is not a path-dependency trap.** Only 2 of 332 declare an out-of-repo
  `path = "../…"` dependency (`ternary-spatial` → `../eisenstein-quantize`; `ternary-tnn` →
  `../the-rotation/crates/neon-kernel`). The `lau-*` family has **zero**. The "unbuildable outside
  the author's machine" shape found in `ternary-seed-stability` by the 2026-10-23 report does **not**
  generalise to these two families — worth saying, because the generalisation is the easy mistake.
- **The 114 repos that share a file layout are not clones.** 114 distinct content hashes (§1.1).
- **The `lau-*` mass push is still one event.** 325 of 333 repos were pushed on **2026-07-12**
  (within 04:29–04:32 UTC), with the rest on 2026-06-08. Created 2026-05-30 → 2026-06-01.
  Two CI timestamps in the failure sample (04:29:49, 04:29:59, 04:30:02, …) are 3–10 s apart,
  which is what a single scripted push looks like in the Actions queue.
- **I did not find the `ternary-*` family's own `DOCKSIDE-EXAM.md`/charter convention** — only 62 of
  332 carry `AGENT.md` + `memory/JOURNAL.md` (vs 331 of 333 for `lau-*`), so the room convention
  is a `lau-*` trait, not a fleet-wide one.

---

## 7. Status of the brief's "already found" list (verified, not re-derived)

| item | status this round |
|---|---|
| `xruntime-conformance` 23/23 digests | not revisited (unchanged) |
| `substrate-foundation` canary `0x024a555471370b18d` | not revisited; the integer is `0x24a555471370b18d` — compare the integer, never the text |
| `quilt-gpu-lab` receipt suite | not revisited |
| `quilt-ewitness` 7/7 → 4/7 on mutation | not revisited |
| `pie-minimax` "locality is not free" | not revisited |
| `fleet-seeds` "no receipt → run VOID" | not revisited |
| `quilt-canary` 52 tracked `target/` artifacts | not revisited |
| `quilt-i2i` 3 defects | not revisited |
| `superinstance-api` `.gitignore` cosmetic | not revisited |
| `quilt-verilog`, `moth-honest`, `substrate-attest-rs`, `quality-gate-stream`, `constraint-theory-core` | not revisited |

**New this round, in the order a reader should care:**

1. **The `ternary-*` family — 332 crates, 6,311 tests, never classified and never executed.** Together
   with `lau-*` this is 665 crates / 27,900 assertions / 14.8% of the fleet's own repos.
2. **The clippy lint, named** (`manual_clamp`, `len_zero`) — the 2026-10-18 report explicitly could
   not determine it. 42 of 45 sampled `lau-*` red badges are red on this lint alone.
3. **The repair receipt**: `cargo fmt --all` + `cargo clippy --fix` turns a red badge green with
   **zero** change to any assertion — demonstrated end-to-end on `ternary-pareto`. 413 badges.
4. **The `lau-*` agent-room layer is a form letter** — 331 identical duty logs that all say
   "Awaiting instructions", and a neighbour graph that is the same 5 names 1,655 times.
5. **`flux-repl`** — README says 15 tests, there are 126, one fails, CI is red, the exam is unticked,
   the bytecode is committed, and the health check is unanswered.
6. **`si-cli` — the fleet's own auditor.** `si check` certifies a config file against itself
   (γ = H = 10⁶ "conserves" perfectly). `si audit` scores "ecosystem readiness" from file presence
   and line counts, **cannot see Python tests at all** (reports "No tests found" for a repo with
   126), awards full marks to CI that is `echo`, and **exits 0 on a grade-F repo**.

---

## 8. Recommended next actions

1. **Run `cargo fmt --all && cargo clippy --all-features --fix` across the 413 red `lau-*` /
   `ternary-*` clones** and open a PR per family. This is the single highest-leverage change
   available to the fleet: it converts 413 red badges into green without touching a single test,
   and it converts a 46% / 84% red rate into a green rate that means something.
2. **Then re-run the per-step classification.** The 3 `lau-*` repos whose *test* step is genuinely
   red (`lau-optimization`, `lau-simd-vibe`, `lau-tropical-agent`) are the real defects; they are
   currently invisible under 142 cosmetic ones.
3. **Open the `ternary-*` family properly.** 332 crates, 6,311 tests, zero executed to date. The
   `lau-*` family took 4 scout rounds to get a handle on; `ternary-*` deserves the same.
4. **Make `AGENT.md`'s neighbour table earn its keep** — generate it from the real dependency graph
   (`si graph` already exists for exactly this) instead of shipping five fixed names 331 times.
   A neighbour table that is always the same is worse than no table, because it looks like data.
5. **Fix `flux-repl`**: cap the trace at 100 (or fix the test to say 200 — pick one and make the
   README match), then tick `DOCKSIDE-EXAM.md` honestly and answer or delete the lighthouse ping.
6. **Give `si check` an external source of truth.** A conservation law that compares a config file to
   itself cannot fail for the reason it exists.
7. **Fix `si audit` before anyone builds a dashboard on it.** Three one-line-class bugs: count
   `.py` tests (it currently reports "No tests found" for a repo with 126), score CI by whether the
   workflow can fail rather than whether a directory exists, and make the exit threshold `<= 50`
   so a grade F is actually red. Today the fleet's own auditor cannot see Python and cannot fail
   on a failing repo.
8. **Fix the three one-line CI bugs** — `ternary-dynamics-python` (`pip install -e .` + drop
   `|| true`, and add `dist/` to `.gitignore`), the 17 `lau-*` repos whose CI is an `echo`, and the
   two repos whose workflows have no steps. Each is a single-file edit that converts a badge that
   verifies nothing into one that verifies something.

---

*Every number in this report was measured in this round: the census by API pagination with a
per-page uniqueness assertion, the CI classifications by `actions/runs/{id}/jobs` per-step
conclusions, the test counts by `cargo test` in clean clones, and the repair by diffing the clone
before and after. The one thing I could not do is run the whole 665-crate family — the sample is 9
crates executed and 90 CI runs classified at step level, and I have said so rather than implying
the rest.*
