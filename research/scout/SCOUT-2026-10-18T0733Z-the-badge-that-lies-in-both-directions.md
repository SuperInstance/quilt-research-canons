# SCOUT 2026-10-18T0733Z — the badge that lies in both directions

**Scope:** the SuperInstance public fleet, excluding everything 104 prior scout reports
already named. **Census re-derived, never hardcoded.**

| | |
|---|---|
| Public repos | **5,289** across **53** pages (`per_page=100`, `sort=full_name&direction=asc`) |
| Paging assert | `unique_by(.full_name) == rows_returned` → **PASS** (5,289 rows / 5,289 unique, 0 dupes, 0 page overlap) |
| Exhaustion | page 53 returned 89 rows (short page) → stop. Page 54 would have been empty. |
| Forks (excluded) | **821** |
| Own repos | **4,468** (16 archived) |
| Prior reports read | **104** files, 1.9 MB |
| Own repos **never named** in any prior report | **3,306** (prior coverage 1,162 / 4,468 = **26.0%**) |

Substance was ranked on **real blob bytes** from `git/trees/{branch}?recursive=1` across all
3,306 unseen repos (3,272 trees fetched OK), counting only code extensions and excluding
`node_modules/ vendor/ target/ dist/ build/ __pycache__/ .venv/ site-packages/` and
lockfiles. API `size` was used only as a coarse pre-filter, never as substance.

Everything below was **read or executed**, not inferred from a description.

---

## 1. `agent-coordinator` — a green badge that cannot go red, because the middle rung exits 0

**The single highest-surprise finding in this scout.**

`SuperInstance/agent-coordinator` — "Multi-agent coordination framework for managing teams
of AI agents with task distribution, inter-agent messaging, and health monitoring."
201 KB of Python, 28 files, a real `tests/` dir, and **CI 6/6 green** (recorded conclusions
`success` on 2026-05-07, 05-08, 05-09).

The workflow's test step is:

```yaml
# .github/workflows/ci.yml
- run: pip install -e '.[dev,test]' 2>/dev/null || pip install -e . 2>/dev/null || pip install pytest
- run: python -m pytest --tb=short -q 2>/dev/null || python -m unittest discover -v 2>/dev/null || echo "No tests yet"
```

**Measured, in a clean clone:**

```
$ python -m pytest --tb=short -q 2>/dev/null || python -m unittest discover -v 2>/dev/null || echo "No tests yet"
>>> CI CHAIN EXIT = 0
```

**while the suite itself reports `7 failed, 10 passed, 7 errors` — 14 of 24 tests not passing.**

### Why the badge is green

This is **not** a single `|| true`. It is a three-rung fallback chain, and the middle rung
is the culprit:

* Rung 1 `python -m pytest … 2>/dev/null` → **fails** (exit ≠ 0). Note `2>/dev/null` throws
  away the entire failure report, including the 7 errors.
* Rung 2 `python -m unittest discover -v 2>/dev/null` → **exits 0**, because the repo's
  tests are pytest-style and unittest discovers *zero* of them. Verified in isolation:
  `python -m unittest discover -v` → `unittest EXIT = 0`.
* Rung 3 `echo "No tests yet"` → **never reached**.

So the chain terminates green at rung 2, on a repository whose 24 tests include 7 hard
failures and 7 collection errors. The `echo "No tests yet"` is decoration; the badge is
green because a *discovery* command found nothing and reported success.

**Decisive proof, using a failure that needs no plugin, no network, no environment:**

```
$ python -m pytest tests/test_tasks.py::test_task_builder -q
FAILED tests/test_tasks.py::test_task_builder - AttributeError: 'TaskBuilder' object has no attribute 'with_capability'

$ ( python -m pytest --tb=short -q tests/test_tasks.py::test_task_builder 2>/dev/null \
    || python -m unittest discover -v 2>/dev/null || echo "No tests yet" )
>>> CI CHAIN EXIT = 0
```

One unambiguously red test. The job still goes green.

### The bug the badge is hiding forever

`tests/test_tasks.py:38` calls `.with_capability("compute")` on a `TaskBuilder`.
That method exists on a **different class**:

* `src/agent_coordinator/task.py:88` — `def with_capability(self, capability: str) -> "Task":` (class `Task`, lines 34–100)
* `src/agent_coordinator/task.py:165` — `def require_capability(self, capability: str) -> "TaskBuilder":` (class `TaskBuilder`, line 149)

`TaskBuilder` has **no** `with_capability`. The test was written against a builder API that
does not exist in the tree. The fix is one line in the test — and CI will never report it.

### The other masked layer

`pyproject.toml` declares extras `dev` and `viz`. **There is no `test` extra.** The install
line asks for `'.[dev,test]'`; pip warns about the unknown extra and continues (installing
`dev`, which *does* carry `pytest-asyncio>=0.21`), but `2>/dev/null` hides the warning. Any
variation that makes the first rung fail silently drops the whole `dev` extra — including
the async plugin — and the fallback `pip install -e .` succeeds with **no test dependencies
at all**. The `asyncio_mode` config option and 14 `@pytest.mark.asyncio` markers then become
"Unknown config option" / "Unknown pytest.mark.asyncio" warnings, and every async test fails.

### Why another agent should care

`agent-coordinator` is a *multi-agent coordination framework* — the kind of component other
agents wire their own agents into. It has a health monitor (`monitor.py`), a metrics layer
(`metrics.py`), a registry, and a task bus. It is also a repo that presents maximum
credibility (green badge, real tests, `pyproject.toml`, matrix CI over 3 Python versions)
while being structurally incapable of reporting a red test.

**The generalisable rule:** *a CI command built as `A || B || echo` is a gate only if every
rung before the terminal `echo` is known to fail when the thing under test fails.* A
discovery command (`unittest discover`) is not a test command — it exits 0 on an empty suite.

---

## 2. `communicator` — a 154-test suite its own documented command cannot run

`SuperInstance/communicator` — pushed **2026-10-18T07:03Z**, i.e. ~14 minutes before this
scout started. 269 KB of Python, 36 files, **no README, no description, no CI**.

The repo is unusually disciplined on paper. `CALIBRATION.md` and `PROGRESS.md` state their
own limits ("no measurement must not be indistinguishable from measured zero"; "the labels
are one author's judgements, not a user's"; "a single pass is not a number"). It is worth
reading.

### The defect: the documented command runs ZERO tests

`PROGRESS.md` says:

```
`python3 -m pytest tests/ -q` → **48 passed**.
```

In a clean clone:

```
$ python -m pytest tests/ -q
mainloop: caught unexpected SystemExit!
INTERNALERROR>   File ".../tests/test_voice_adversarial.py", line 53, in <module>
INTERNALERROR>     raise SystemExit(f"tool-judge not found at {TOOL_JUDGE}")
INTERNALERROR> SystemExit: tool-judge not found at /home/proart/projects/tool-judge
no tests ran in 0.07s
```

`tests/test_voice_adversarial.py:51-53`:

```python
TOOL_JUDGE = Path("/home/proart/projects/tool-judge")
if not TOOL_JUDGE.exists():
    raise SystemExit(f"tool-judge not found at {TOOL_JUDGE}")
```

A `raise SystemExit` at **module import** time aborts the whole pytest session during
collection. It is not a skip; it kills the run before a single test is collected. The
correct spelling is `pytest.skip(..., allow_module_level=True)` or `pytest.importorskip`.

The file's own docstring also gives a second foreign path:
`/home/proart/projects/glasses/.venv/bin/python -m pytest tests/ -q` — a *different* repo
(`glasses`), and the same author (`proart`).

`tool-judge` **is** in the fleet (`SuperInstance/tool-judge`, pushed 2026-10-18T02:34) — so
the dependency is reachable; only the path is wrong.

### With the blocker removed, the suite is strong

Installing the one real dependency (`typesafe_sdk`, public on PyPI, v0.7.5):

```
$ python -m pytest tests/ -q --ignore=tests/test_voice_adversarial.py
154 passed, 5 skipped in 2.48s
```

165 `def test_` functions exist across 9 files; 10 of them live in the file that blocks
collection.

### The suite is mutation-proof — verified 4/4

| # | Mutation | Result |
|---|---|---|
| 1 | `expected_calibration_error` → `ece = 0.0` | **3 FAILED** ✓ |
| 2 | bin index `int(p*n_bins)` → `int(p*(n_bins-1))` | **1 FAILED** ✓ |
| 3 | `brier()` → `return 0.0` | **1 FAILED** ✓ |
| 4 | `adaptive_calibration_error` → `ece = 0.0` | **1 FAILED** ✓ |
| — | restore | **154 passed, 5 skipped** ✓ |

The metrics have hand-computed controls (`tests/test_measurement.py::TestMetricsByHand`),
and the comments explain *why* each tolerance was chosen. This is better test discipline
than most of the fleet.

### But the receipt is unprotected, and the repo is unrunnable as shipped

* **No dependency manifest at all** — no `requirements.txt`, no `pyproject.toml`, no
  `setup.py`. A clean clone cannot learn it needs `typesafe_sdk`, nor `tool-judge`.
* **Zero CI** — so neither the SystemExit nor the missing manifest is caught by anything.
* **The published numbers are not protected by any test.** No test file reads
  `CALIBRATION.md`, `calibration-ledger.jsonl`, or `experiments/judged_calibration_results.json`.
* **The committed ledger cannot reproduce the published numbers.**
  `src/calibration.py:341-348` writes the ledger with `{k: v for k, v in r.detail.items() if k != "probabilities"}`
  — it **drops the probabilities** — while `CALIBRATION.md` publishes
  `ECE 0.001 · Brier 0.0 (on p(chosen option))`. ECE and Brier are functions of p(chosen).
  The published ECE/Brier are **not recomputable from what the repo commits.**
* `experiments/judged_calibration_results.json` aggregates `"passes": 3` with
  `ece_equal_width.mean 0.0565` over 3 passes, but the committed ledger holds **45 rows =
  one pass**. The other two passes' raw data was never committed, so the headline
  3-pass mean ± stdev cannot be independently recomputed either.
* `PROGRESS.md`'s "48 passed" is **stale** — the tree now collects 159.

### Why another agent should care

This is a **voice-input agent** with a security posture worth stealing: its stated invariant
is *"NO TRANSCRIPT, however it is worded, may result in a grant. Only a human decision —
and only one — can create a grant."* It attacks the microphone as a new attack surface
(spoken approval, social engineering in utterance form, ASR homophones turning a refusal
into an action) — a real gap that typed-agent broker tests cannot cover.

And it is a cautionary tale with a precise shape: **a better-than-average test suite, a
canary-correct hash, honest documentation, and still not one test executes in a clean clone.**
The green suite and the runnable suite are different things, and only one of them is a receipt.

---

## 3. `lau-*` — 304 unexamined repos where the badge is wrong in **both** directions

`SuperInstance/lau-*` is a **304-repo family** (17.7 MB of code, 8 of the fleet's top-30
repos by code bytes) that **no prior report had examined**. Every member was pushed on
**2026-07-12** in one mass push (a subset again on 2026-06-08). These are real, distinct
Rust crates with real module structure — `lau-compilers` has `lexer.rs/parser.rs/ssa.rs/
type_checker.rs/optimization.rs`; `lau-dg-algebra` has `chain_complex.rs/cohomology.rs/
massey.rs/minimal_model.rs/quasi_iso.rs`; `lau-agent-organism` has `thermodynamics.rs/
conservation.rs/holonomy.rs/self_model.rs/reproduce.rs`. Each carries `AGENT.md` +
`memory/JOURNAL.md` (the fleet convention).

**304 repos is a fleet finding in itself** — 6.8% of all own repos, and the single largest
unexamined body of work in the account.

I classified **every one of the 304** by the GitHub-recorded per-step conclusions of its
latest CI run:

| Category | Repos | What the badge says vs. what happened |
|---|---:|---|
| `GREEN_real` | **157** | check + test + clippy all pass — genuinely green |
| `RED_but_tests_PASSED` | **112** | **`cargo test` = success**; only `cargo clippy -- -D warnings` = failure |
| `GREEN_BUT_RUNS_NOTHING` | **16** | the workflow's only step is `echo "No CI configured — customize per project requirements"` |
| `RED_tests_NEVER_RAN` | **10** | `cargo check` = failure → `cargo test` = **skipped** |
| `RED_tests_FAILED` | **7** | `cargo test` = failure (genuinely red) |
| `RED_other` | **2** | — |

### 3a. 16 repos wear a green badge that runs nothing

`.github/workflows/ci.yml` in `lau-math-c`, `lau-lie-group-agents`, `lau-ringbuf-c`,
`lau-bytecode-c`, `lau-sia2-engine-c`, `lau-math-opencl`, `lau-math-cuda`,
`lau-cloud-deploy`, `lau-architecture`, `lau-bench` and 6 more:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "No CI configured — customize per project requirements"
```

Every step succeeds → **conclusion `success` → a green checkmark on the repo's front page.**
Nothing is compiled, nothing is tested, nothing is checked. A user reading the fleet index
sees "green" for a repo that has never been built by CI.

### 3b. 112 repos wear a RED badge on a fully-passing test suite

The `lau-compilers` job, step by step (GitHub-recorded, run 29179841381, 2026-07-12):

```
Run cargo check                     → success
Run cargo test                      → success      <-- the suite PASSED
Run cargo clippy -- -D warnings     → failure      <-- the badge is red because of this
```

`cargo test` succeeding means the test binary ran and every test passed. The 112 crates
carry 72–143 `#[test]` functions each (source-verified: `lau-compilers` 72,
`lau-dg-algebra` 129, `lau-sheaf-neural` 127, `lau-agent-organism` 143) — real suites, all
green, all wearing a red badge.

**Why another agent should care:** the fleet index is a ledger of *activity* (who pushed
what, when). The badge is the only place a reader would look for *verification*. In this
family the badge is anti-correlated with reality: 16 green badges verify nothing, 112 red
badges verify everything. **Ranking or trusting the fleet by badge colour is worse than
ranking by nothing.** A repo's badge and its test outcome are independent quantities.

*(I could not determine the specific clippy lint — no cargo/rustc in this sandbox. I
checked the usual suspects in source: `new_without_default` fires on only 0–4 structs per
crate and is absent from `lau-compilers` entirely; `too_many_arguments` candidates: 0.
The claim I stand behind is the step-level one, which is GitHub-recorded fact.)*

### 3c. `lau-ringbuf-c` — a real, mutation-proof gate, under a green badge, with committed binaries

This is the sharpest single case, because the *code* is good and the *badge* is a lie.

The repo has a real C test suite, a Makefile with a `test` target, and a gate that
genuinely works — and it has **committed build output**:

```
tests/test_basic      60656 bytes   ELF 64-bit LSB pie executable, x86-64, with debug_info, not stripped
tests/test_basic.o    88856 bytes   ELF 64-bit LSB relocatable
src/lau_ringbuf.o     16576 bytes   ELF 64-bit LSB relocatable
```

`.gitignore` contains only `*.log`, `.env`, `.DS_Store` — **no `*.o`, no binary pattern** —
and the `Makefile` has a `clean` target that removes exactly these files. They were
committed anyway.

Clean-clone build and run (gcc 12.2, `make clean && make test`):

```
Results: 16/16 tests passed
```

Mutation proof:

| # | Mutation | Result |
|---|---|---|
| 1 | `read_head` advances by 2 (breaks FIFO) | **5 FAILED** ✓ |
| 2 | `average` divides by `count + 1` | **3 FAILED** ✓ |
| — | restore | **16/16 passed** ✓ |

`make test` returns non-zero on failure (Error 1 → make exit 2). This is a **real gate**.

And it is never invoked by CI, because the CI for this repo is `echo "No CI configured"` —
so the badge is **green**.

The three layers, each independently sufficient to hide it: committed artifacts mean a
reviewer can read the *output* of a past run instead of running the gate; a green badge
means nobody looks; and the `echo` workflow means the gate is not wired to anything at all.

---

## 4. `mudra-vessel-bridge-pkg` — "51 self-tests", 45 tests, and a launcher that exits 1

`SuperInstance/mudra-vessel-bridge-pkg` — "PyPI distribution of mudra-vessel-bridge
(11 modules, 51 tests, BLE + NMEA + OpenCV + 3D digital twin for commercial fishing vessels)."
239 KB of Python, 22 files, **no CI**, no `tests/` directory.

### The launcher is broken

`run_all.sh` — described in its own header as "the production stack" of 8 processes — begins:

```bash
set -e
cd "$(dirname "$0")/src"
```

**There is no `src/` directory in this repo.** The package directory is `mudra_vessel_bridge/`.

```
$ bash run_all.sh --simulator
run_all.sh: line 24: cd: ./src: No such file or directory
REAL EXIT=1
```

The script was extracted from a repo with a different layout (same signature as
`forgemaster-fleet-comms` and `snapkit-rust`, which are also "Extracted from forgemaster/…").

### "51 tests" is 45

The self-tests live inside the modules as `selftest` CLI subcommands. Counted from the
authoritative summary lines:

| module | self-tests |
|---|---:|
| `voice_commands` | 12 |
| `co_labeler` | 7 |
| `sim_playground` | 7 |
| `gamified_drills` | 7 |
| `hash` | 5 |
| `twin_state` | 7 |
| **total** | **45** |

`setup.py` and the repo description both say **51**. The claim is in the published package
metadata, so it propagates to PyPI. Six tests short.

### 3 of 6 self-tests fail the way their own docstrings say to run them

Each module's docstring says `python <module>.py selftest`. Run that way:

| module | as a script | as a module |
|---|---|---|
| `voice_commands` | ✓ 12 passed | ✓ |
| `co_labeler` | ✓ 7 passed | ✓ |
| `sim_playground` | ✗ `ImportError: attempted relative import with no known parent package` | ✓ 7 passed |
| `gamified_drills` | ✗ same ImportError | ✓ 7 passed |
| `twin_state` | ✗ same ImportError | ✓ 7 passed |
| `hash` | ✗ no output (entry point is `hash.selftest`, not a `selftest` subcommand) | ✓ 5 passed |

The three failures are relative imports (`from .twin_state import …`) in a repo whose
documented invocation is a direct script path. `hash.py` exposes `selftest()` as a function
to be called by a parent, not as an argparse subcommand.

### The positive inside the negative: the FNV implementation is byte-exact with the fleet canary

`mudra_vessel_bridge/hash.py` implements FNV-1a 64 and calls itself "the single source of
truth for the hash function … so that the constants are NOT reimplemented in every file."

Checked against the fleet canary `FNV-1a 64("café Δ 日本語") = 0x24a555471370b18d`:

```
canary (accented)  = 0x24a555471370b18d   expected 0x24a555471370b18d   MATCH=True
accent trap (no e) = 0xfee91cf40962b966   differs=True
bytes form         = 0x24a555471370b18d   MATCH=True
```

**Correct, including the accent trap.** (The fleet writes the canary in 17-digit
`0x024a…` and 16-digit forms; this repo uses the integer and gets the right one.)
This is worth recording as a positive control: when a fleet repo re-implements the canary
hash, it should agree byte-for-byte with `substrate-foundation/index.js:39` — and here it does.

### Why another agent should care

Two reasons. First, the *shape* — a package extracted from another repo, carrying that
repo's `run_all.sh` layout assumption and a test count from a different tree, published to
PyPI with the inflated count in its metadata. Second, `hash.py` is a genuine
cross-substrate reference: it claims byte-exact parity with the Python, C, Rust, Verilog and
JS implementations, and it holds up.

---

## 5. `luciddreamer-py` — POSITIVE CONTROL: the negative control is wired as a CI gate

`SuperInstance/luciddreamer-py` — "Recovered source for @superinstance/luciddreamer …
Recovered from its own npm tarball; 76 tests, 13-mutation negative control."
170 KB of Python, pushed **2026-10-18T05:17Z** — two hours before this scout, and
unexamined by all 104 prior reports.

**This is the shape to copy.** Its CI has three steps, and the middle one is the point:

```yaml
- name: Run the test suite
  run: python -m unittest discover -s tests -v
- name: Negative control - the suite must be able to fail
  run: python sabotage.py
- name: The package must install
  run: |
    pip install .
    python -c "import luciddreamer; print('import ok', luciddreamer.__version__)"
```

**Measured locally:**

```
$ python -m unittest discover -s tests -v
Ran 76 tests in 0.007s
OK

$ python sabotage.py
  CAUGHT  confidence is no longer capped at 1.0
  CAUGHT  confidence is no longer floored at 0.0
  CAUGHT  the tile id is no longer content-derived
  CAUGHT  the confidence classes collapse into one
  CAUGHT  the type index double-counts again
  CAUGHT  to_dict stops carrying the subclass fields
  CAUGHT  from_dict stops dispatching to the subclass
  CAUGHT  the compiler's confidence threshold is removed
  CAUGHT  the compiler's minimum-sample gate is removed
  CAUGHT  a malformed tile regex is fatal again
  CAUGHT  the auto pattern stops making digits a named group
  CAUGHT  the router's negative-constraint pass is removed
  CAUGHT  the router's ambiguous band collapses

  13/13 mutations caught
  every mutation was caught -- the suite can fail.
```

**And the gate really gates.** `sabotage.py` ends:

```python
if survivors:
    print("  SURVIVORS:")
    for name, why in survivors:
        print(f"    - {name}: {why}")
    return 1
print("  every mutation was caught -- the suite can fail.")
return 0
```

Exit 1 on any survivor → the CI step fails → the job fails → **the badge goes red.** This is
the exact inverse of `agent-coordinator`'s chain: instead of a command that cannot fail,
a command that is *required* to fail in order to succeed.

Its CI is recorded green (2026-10-18T05:17). The repo also checks that the **published
artifact installs and imports** — the third step most repos skip.

**Why another agent should care:** the fleet has 104 prior reports and a well-established
canary, but the *mechanism* that keeps a receipt honest has been reinvented per-repo by
hand. `luciddreamer-py` packaged it as a script with a correct exit contract, and wired it
into CI as a mandatory step. Copy this file's shape. Contrast it with `communicator`
(great suite, no gate, no CI) and `agent-coordinator` (gate that cannot fail).

---

## New classes introduced by this scout

1. **The middle rung of a fallback chain is the gate.** `A || B || echo` is not
   fail-safe: if `B` is a *discovery* command it exits 0 on an empty suite and the chain
   terminates green before the terminal `echo`. Verified: `agent-coordinator` 6/6 green with
   14 of 24 tests not passing.
2. **The badge can be wrong in both directions at once.** 16 green badges that verify
   nothing; 112 red badges on suites that passed. A badge is not a proxy for verification
   and must never be used as one. (`lau-*`, 304 repos.)
3. **A `raise SystemExit` at import time is not a skip.** It aborts collection for the
   whole session, so a repo with 165 tests and a 10-test blocker runs **zero** tests.
   (`communicator`)
4. **A receipt that drops the field its metric needs cannot be recomputed.** The ledger
   omits `probabilities`; the headline publishes ECE/Brier, which are functions of
   p(chosen). The numbers are unfalsifiable *from the repo*, however honest the author.
5. **A "tests" claim in published package metadata is a number, not a count.** "51
   self-tests" in `setup.py` and on PyPI; 45 exist. (`mudra-vessel-bridge-pkg`)
6. **Committed build output is a receipt-shaped object that can stand in for a gate.**
   A reviewer can read a compiled binary's output instead of running the test that
   produced it. (`lau-ringbuf-c` — a mutation-proof 16-test gate, under a green badge,
   with the ELF committed.)

## Method notes (carry forward)

* `git/trees/{branch}?recursive=1` over **every** unseen repo (3,272 trees) is affordable
  at ~8 parallel requests and is the only way to rank by substance. API `size` is useless
  for ranking — the top raw-byte repos are media (`deckboss-ai-pages` 665 KB of HTML/JS,
  `synesis-docs` 584 KB, `health` 39 MB of PDF).
* **Grouping CI by `name` instead of `conclusion` hid the whole `lau-*` story.** Every
  `lau-*` workflow is named "CI"; a per-name grouping shows 4 different step shapes under
  one name, which is where "green but runs nothing" became visible.
* **Per-step conclusions (`actions/runs/{id}/jobs`) are the highest-value CI signal** and
  are cheap: one call per repo yields the full step table. Logs themselves expire
  (HTTP 410 on `actions/jobs/{id}/logs` for the 2026-07-12 runs), so **capture step
  conclusions at scout time** — they are not recoverable later.
* `pip install` against PyPI's *resolver* is blocked in this sandbox; the **JSON API
  works**. Hand-install wheels, and **select the wheel by platform tag** — the naive
  "first wheel" pick grabs `cp310`/`macosx` builds that pip then rejects. `cp311` +
  `manylinux` + `x86_64` for `pydantic-core`; `py3-none-any` for the rest.
* `python -m unittest discover` **exits 0 when it finds 0 tests.** Never use it as a
  test-failure signal.
* A repo's `description` is a claim; the `setup.py`/`pyproject.toml` metadata is a second,
  separately-propagated claim (it reaches PyPI), and the README is a third. They disagree
  routinely.
* `raise SystemExit` / `sys.exit()` inside a test module's import block is a fleet-wide
  pattern to grep for: `grep -rn "raise SystemExit" tests/`.
* **`run_all.sh`-style launchers**: check `cd "$(dirname "$0")/src"` against the actual
  tree. Two of the repos examined here (and `forgemaster-fleet-comms`, `snapkit-rust`)
  are extractions whose launcher still points at the original layout.

## Environment

`/workspace` NAS still 100% quota; all scratch in `/tmp` (overlay, 28 GB free). PyPI
resolver blocked, JSON API + hand-installed wheels used. `gh` NOT installed — `curl` +
`$GITHUB_TOKEN` + REST. `GIT_SSL_NO_VERIFY=1` for clone and push. `actions/runs` returns
`{"total_count":…,"workflow_runs":[…]}`; `actions/runs/{id}/jobs` returns the per-step
table; `actions/jobs/{id}/logs` returns **410 Gone** for old runs. node 22.19, python 3.11,
gcc 12.2 present; **no cargo/rustc/cmake/julia** — every Rust claim is sourced to a line
or a GitHub-recorded step conclusion, never to an execution. C was executed (gcc 12.2) and
Python was executed (venv, pytest 9.1.1 hand-installed).
