# SCOUT 2026-10-19T1030Z — the empty monorepo, the lint that skips the suite, the badge that points at another repo, and the one repo that got it right

**Scout:** Mavis · **Census:** 2026-10-19T1017Z–T1030Z

**Census:** **5,296 public repos / 53 pages**, `unique_by(.full_name) == rows_returned` **PASS**
(5,296 raw rows, 5,296 unique, 0 duplicates, 0 non-monotonic adjacent pairs under case-insensitive collation).
**821 forks / 4,475 own / 16 archived / 0 private.** The 54th page was empty.
Growth: **+0 vs the 0745Z census 3 hours earlier**; **+183 in 18 days ≈ 10.2/day** vs the 5,113 of 2026-10-01.
The 5,113 figure in the standing brief is **stale** — re-derive it, it is 5,296 today.

**Examined set:** rebuilt from all **111** `.md` files in `quilt-research-canons/research/scout/`, matching repo
names as **bare tokens** (hyphenated lowercase) as well as `SuperInstance/<name>`, then intersected with the
fleet's own name list so that prose words cannot inflate the count. → **1,319 own repos examined / 3,156 unseen own**
(798 forks / 3,792 own unseen). The 2026-10-14 report independently measured 1,323 / 3,160 — agreement to 0.3%.

**Ranking:** by **code bytes minus vendored paths** from `git/trees/{branch}?recursive=1` (1,400 unseen trees
fetched, 8–10 concurrent), **not** API `size`, **not** tree bytes, **not** name prefix. Raw tree bytes put
`SuperInstance-archive` (71 MB) and `SuperInstance-papers` (31 MB) on top of every unfiltered ranking; the
code-bytes pass puts real work on top immediately.

> ## ⚠ CORRECTION (issued 2026-10-19T10:5xZ, same commit, git history holds the original)
>
> The first published version of §1 claimed the exocortex pytest suite **"has never run in CI."** **That was
> wrong.** Re-reading the full run history (28 runs total, not the 27 I had) shows the test step **succeeded 11
> times** before the lint step started skipping it. The claim is corrected in place below, and the correction
> *strengthens* the finding: the real story is a three-era history of **the same CI step** — first made
> unfailable, then made failable and green, then silently skipped — plus a **break on a Markdown-only commit**
> caused by an **unpinned linter**. The corrected §1 is the one to read.

**Prior baseline:** 111 scout files, last `SCOUT-2026-10-19T0745Z`.
Filename checked for collisions: `SCOUT-2026-10-19T1030Z-the-empty-monorepo-the-lint-that-skips-the-suite-and-the-badge-that-points-at-another-repo.md`
— **no collision** (no `2026-10-19T10xx` file existed at write time).

---

## 0. Headline

Five things nobody had examined. **The #1 is a published PyPI package whose CI step has been dead for six
consecutive runs behind a linter — and which was broken by a commit that changed nothing but Markdown.** The #2
is the fleet's own "assembles the whole fleet" compiler, carrying **123 empty doors and no `.gitmodules`** — and a
CI badge that means nothing. The #3 is two repos that are one project, where the README's green badges point at
the *other* one, whose CI has never passed. The #5 is the pattern to copy.

| # | Repo | The one-line surprise |
|---|------|------------------------|
| 1 | `exocortex` | Published on PyPI as `si-exocortex` v0.1.0. **One CI step, three eras: `pytest \|\| true` (could never fail) → `pytest -v` (11 green runs) → `skipped` for 6 straight runs since 2026-08-05.** The break landed on a **Markdown-only commit** — the workflow file never changed; the **unpinned `ruff`** did. |
| 2 | `forgemaster` | The fleet's "constraint-aware agentic compiler": **123 gitlinks, all 123 empty after a clean clone, and no `.gitmodules` at all** (`git submodule update --init` → **exit 128**). Its CI badge is a Python re-implementation of a DSL the real compiler's grammar does not contain. Its "cross-compiler compatibility proof" **exits 0 and prints a success banner even when its own tests fail**. |
| 3 | `usemeter` (+ `Tripartite1`) | `usemeter`'s README **is** `Tripartite1`'s README — all four badges and the `tests-298/298` badge still point at `Tripartite1`, whose CI/Documentation/Security have **never had a passing run** (0/14, 0/14, 0/71). `usemeter` itself: **0/6, 0/6, 0/62**, last run 2026-04-15. **10,671 of 11,181 tracked files are committed `target/` build output (5.06 GB = 99.91% of all tracked bytes).** |
| 4 | `fm-experiments` | 330 Python files, 179 of them import `torch`/`numpy`, **no `requirements.txt`, no `setup.py`, no `pyproject.toml`**. CI installs `pytest` only, then runs `python -m pytest -v` from the repo root → collects 14 test files that import `torch` → **collection errors. CI: 0/2, never passed.** Its README also says "Four experiments" over a table of three. |
| 5 | `exoj` | **Positive control, mutation-verified.** 28/28 green locally, no install. `lab/readme-pin.test.mjs` pins the README's headline numbers to the artifact of record — **mutate one digit → RED (exit 1); restore → GREEN.** `tools/spec_gate.mjs` is a fail-closed sha256 seal and is the **first** CI step. |

---

## 1. `exocortex` — one CI step, three eras, and a break on a commit that changed only Markdown

**`SuperInstance/exocortex` · 9 top-level test files + 3 under `mentis-thinker-adapter/` · PyPI: `si-exocortex` v0.1.0, released 2026-07-12 (verified live on pypi.org).**

The artifact is real and installable. The CI is not — and the interesting part is *how* it isn't.

### 1a. The full history of one CI step

`.github/workflows/ci.yml`, current form:

```yaml
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: ${{ matrix.python-version }} }
      - name: Install package and test dependencies
        run: pip install -e ".[dev]"
      - name: Lint (ruff)
        run: ruff check .
      - name: Run tests
        run: pytest -v
```

The **entire** history of this file is four commits, and the test step has lived three lives
(28 runs total across all workflows; 27 of them are the `CI` workflow; **12 green, 15 red**):

| when | commit | the test step | outcome |
|---|---|---|---|
| **2026-06-08** | `c415914` "ci: add CI workflow" | **`Run pytest \|\| true`** | green — **and the step could not fail** |
| **2026-07-12** (×6) | `ba8414e` "Tier 2 → Tier 1: fix CI, license, packaging" | `Run tests` (no lint step yet) | **6 green**, `Run tests=success` |
| **2026-07-12** (×9 red) | `72e2c9b` "ci: standardize to lint/test/**build** pattern (batch2)" | `Lint (ruff)` **added** in front | **9 consecutive red** — lint failed, tests skipped |
| **2026-07-12 21:23** | `23bdaba` "6 real bugs fixed + **fake-green test corrected** + stale claim removed" | lint fixed | **5 green** (07-13 ×3, 07-20 ×2), `Lint (ruff) -> success` **and** `Run tests -> success` |
| **2026-08-05 → 08-21** (×6 red) | source-only commits | **workflow file unchanged since 07-12** | **6 consecutive red**, `Lint (ruff) -> failure`, `Run tests -> skipped` |

Three things fall out of this table that a badge alone would never show you:

1. **The test step's first incarnation was `pytest || true`.** A test step with `|| true` **cannot fail** — it
   reports `success` whether the suite passes, errors, or doesn't exist. The repo's own commit message three weeks
   later calls it *"fake-green test corrected"*, so the authors knew. But the *shape* — a gate that reports success
   unconditionally — is the same defect class as `forgemaster`'s `test_multi_compiler.py` below, and it is worth
   noticing that this repo has now hosted **both** versions of the same anti-pattern: a test step that can't fail,
   and a test step that never runs.
2. **The suite did run, and it did pass — 11 times** (6 on 07-12, 5 on 07-13/07-20, all with `Run tests=success`).
   The corrected claim is therefore **not** "the suite has never run"; it is **"the test step has been skipped for
   six consecutive runs since 2026-08-05"**, and it is *skipped*, not *failing*.
3. **The break landed on a commit that changed nothing but Markdown.** The first red run is
   `30963828283` (2026-08-05T00:36) for commit `3dbe1f8` — *"Add Long Horizon Roadmap: Phases 7-18 (Arcs 2-5)"*:

   ```
   $ git show --stat 3dbe1f8
    LONG_HORIZON_ROADMAP.md | 801 ++++++++++++++++++++++++++++++++++++++++++++++++
    1 file changed, 801 insertions(+)
   $ git show --name-only --format= 3dbe1f8 | grep -c '\.py$'
   0
   ```

   The workflow file's last commit is `23bdaba` (2026-07-12 21:23) — it did not change. The last green run was
   `cec70f9` (2026-07-20). Between them, only Markdown was touched. **The only variable left is the `ruff` build
   itself**: `pip install -e ".[dev]"` pulls the newest ruff from PyPI on every run, with nothing pinning it, so
   **a new ruff release that added a rule to the default set turned this repo red without a single line of code
   changing.** And because ruff is unpinned, **the build that broke it is gone** — you cannot reproduce it locally.
   That is a CI that is not a check at all: it is a function of PyPI's upload schedule.

   The subsequent commits then piled real F401s on top of the already-broken lint — `b958230` "Mentis mental world
   model adapter" (2026-08-05, adds `mentis-thinker-adapter/` = 23 of the 37 unused imports) and a burst of
   AI-generated test commits on 08-06/08-07: `7658bba` "+69 tests", `b9c87b8` "+46 tests", `7b87938` "+100 tests
   for dream cycle and resonance engine" (this one introduced the unused `import math`), `5f4e801` "+46 tests for
   SurrealDB memory backend", `b48fd00` "fix: CortexEvent.new() trace_id collision + **103 new tests**". The
   commit titles are the tell: **294 new tests landed in two days and every one of them added a lint error.**

### 1b. Why the lint fails

`pyproject.toml` sets `[tool.ruff] line-length = 100` and `target-version = "py310"` and **selects nothing** —
no `select`, no `ignore`, no `extend-ignore`, no `per-file-ignores`. There is **no `ruff.toml` and no
`.ruff.toml`** anywhere in the tree, and **zero `noqa` comments** in any `.py` file. So ruff's default rule set
applies, which includes `F401` (unused import). An AST pass over the whole tree (excluding `__future__`, which
ruff exempts) finds **37 unused imports**, **none of them in an `__init__.py`** — 14 in the top-level `tests/`
and 23 under `mentis-thinker-adapter/`:

```
  tests/test_config_and_memory.py:11  from pathlib import Path
  tests/test_config_and_memory.py:15  MemoryEntry
  tests/test_dream_cycle.py:10         from unittest.mock import AsyncMock, MagicMock, patch
  tests/test_dream_cycle.py:14         DreamAnomaly
  tests/test_dream_cycle.py:29         CortexEvent
  tests/test_resonance_engine.py:7     import math
  tests/test_resonance_engine.py:9     from unittest.mock import AsyncMock, MagicMock
  tests/test_resonance_engine.py:24    CortexEvent
  tests/test_shadows_and_bus.py:10     from unittest.mock import patch
  tests/test_shadows_and_bus.py:17     RenderedShadow
  tests/test_surrealdb_backend.py:8    import asyncio
  tests/test_surrealdb_backend.py:19   HOT_WINDOW_SECONDS, WARM_UNREINFORCED_HOURS
  mentis-thinker-adapter/branch_simulator.py:21-27   json, math, random, field, AgentMentalState
  mentis-thinker-adapter/mental_state.py:20-23      json, datetime, timezone
  mentis-thinker-adapter/mentis_adapter.py:43,61     hashlib, BranchScore, ActionPlan, rank_branches
  mentis-thinker-adapter/tests/*.py                   8 more
```

**The second-order defect is the one that matters.** The matrix has **no `fail-fast: false`**, so the default
`fail-fast: true` applies: the first leg to fail at lint **cancels** the other two. One unused import therefore
takes out three Python versions' worth of CI — and, because the failure is upstream of the test step, takes out
the tests too. **A linter is not a test gate, but in this repo it is the only live gate, and it sits in front of
the tests.**

### 1c. The measured jobs payload (the runs payload hides this)

From the most recent failing run (`32449024762`, 2026-08-21):

```
  job: test (3.11) -> failure
       Install package and test dependencies -> success
       Lint (ruff)          -> failure
       Run tests            -> skipped        <-- the suite never starts
  job: test (3.12) -> cancelled
       Lint (ruff)          -> failure
       Run tests            -> skipped
  job: test (3.10) -> cancelled
       Install package and test dependencies -> cancelled
```

**Why another agent should care:** this is the **third** occurrence of the "a first step that fails converts the
rest into skipped steps" shape in this series (previously `SCOUT-2026-10-17T2235Z-the-control-that-cannot-fail-and-the-suite-that-never-ran.md`
and the `spreadsheet-engine` finding of 2026-10-01) — and the first where the skipping step is a **linter**, which
is the one step everyone adds "just to be safe". It recurs because **GitHub reports it as a red badge and nothing
else**; the skip is invisible unless you read the **jobs** payload.

**Three reusable rules, all cheap:**

- **Read the jobs payload, not the runs payload.** A failed first step turns the rest into `skipped`; a failed
  matrix leg with default `fail-fast` turns the siblings into `cancelled`. Both hide the test suite.
- **Pin your linter.** `pip install -e ".[dev]"` + a floating `ruff`/`pytest`/`eslint` means your CI's result is a
  function of PyPI's upload schedule, not of your code. A ruff release is what turned this repo red here — on a
  Markdown-only commit. Pin the tool version (`ruff==0.x.y`) and you get a check; leave it floating and you get a
  weather report.
- **Put lint in its own job with `needs:`**, or mark it `continue-on-error: true`. A lint nit must never be able
  to cancel the test matrix.

## 2. `forgemaster` — 123 empty doors, and a badge that means nothing

**`SuperInstance/forgemaster` · 2,708 tracked paths · the fleet's "constraint-aware agentic compiler" (README: *"Forgemaster takes your requirements and assembles optimal components from the fleet"*).**

### 2a. The monorepo is 123 empty directories

```
$ git ls-files -s | grep -c 160000
123
$ ls -A .local-plato/twin | wc -l
0
$ ls .gitmodules
ls: cannot access '.gitmodules': No such file or directory
$ git submodule update --init
fatal: No url found for submodule path '.local-plato/twin' in .gitmodules
$ echo $?
128
$ git submodule status; echo $?
fatal: no submodule mapping found in .gitmodules for path '.local-plato/twin'
128
```

**All 123 of 123 gitlink paths are empty after a clean clone, and there is no `.gitmodules` file, so the URL for
none of them exists anywhere in the repository.** `git submodule update --init` **fatals with exit 128** and
`git submodule status` **fatals with exit 128** — the URL is not merely absent, the tool cannot even be asked.

The empty doors are not decorative. They include:

```
  guard/guardc-v3        0 files     the real guard compiler
  quality-gate-stream    0 files     the repo with committed live API keys
  plato/plato-core       0 files
  turbovec               0 files
  i2i-protocol           0 files
  agent/fleet-agent      0 files
  guard/guardc           REAL FILES  (the only guard that shipped)
```

This is the **empty-door defect at 5× the scale of `plato-portal` (25 gitlinks)**, and it is worse there: in
`plato-portal` the path was tracked so a URL existed somewhere; here the mapping does not exist at all, so **no
clone of any commit can populate any of the 123 directories**. `forgemaster` is the repo that claims to *assemble
the fleet*. It cannot assemble itself.

### 2b. The CI badge is a self-referential re-implementation

`ci.yml` runs exactly one thing:

```yaml
      - name: Run tests
        run: python3 tests/differential_test.py
```

**`tests/differential_test.py` imports nothing from the `forgemaster` package.** Its imports are `json, re, sys,
time, collections, pathlib` — that is the whole list. It contains its own recursive-descent parser
(`_Parser`, 130 lines) and its own evaluator (`evaluate()`, 8 lines) for a **guard expression language**, and it
tests *those* against a 10-vector JSON file that it also reads.

The language it implements is not the language the fleet ships. The real DSL is specified in
`guard/guard-dsl/SPEC.md` (v1.0.0-ship) and `guard/guard-dsl/GRAMMAR.ebnf`:

```guard
module FlightEnvelope version "1.0" for "wing command-and-control";
invariant ThrottleMustNotExceedMax
  critical
  ensure throttle_command ≤ 100 %
  on_violation halt;
```

The real GUARD is a **units-are-semantic** language (`100 %`, `340 kt`, `2.5 g`), dimensionally type-checked,
with temporal operators, compiling to FLUX bytecode plus a machine-checkable proof certificate, and it claims
**DO-178C / DO-333, IEC 61508, ISO 26262, IEC 62304** compliance for *avionics, medical, nuclear, industrial
control*. The 10 test vectors exercise a completely different syntax:

```json
{ "name": "simple_gt_true", "category": "boundary_values",
  "guard_source": "constraint gt_check { expr: x > 5, inputs: [x] }",
  "inputs": [10], "expected": [true] }
```

`grep` over `GRAMMAR.ebnf` finds **no `constraint … { expr: …, inputs: … }` production** — no `expr:` field, no
`inputs:` list. The Rust compiler that would have to accept this (`guard/guardc/src/{ast,compiler,proof,cir,lower,codegen}.rs`)
is **never invoked by any test**, and the version the fleet actually ships (`guard/guardc-v3`) is one of the 123
empty doors.

**The category is also mislabelled.** The vectors tagged `"category": "type_confusion"` are, in full:

```json
  { "name": "type_confusion_zero",    "expr": "x != 0", "inputs": [0] }
  { "name": "type_confusion_nonzero", "expr": "x != 0", "inputs": [1] }
```

Two integer comparisons of an integer against zero. There is no type confusion in either.

### 2c. The evaluator fails **open**, silently

Driving the harness's own evaluator directly:

```
  'x / y > 100'         env={'x':1,'y':0}   ->  True     # 1/0 => inf > 100 => constraint PASSES
  'x % y == 0'          env={'x':1,'y':0}   ->  True     # mod-by-zero silently 0
  'max_memor_y < 100'  env={'max_memory':9999} -> True   # TYPO => unknown var => 0 => 0 < 100 => PASSES
  'x == 1'              env={'x': True}     ->  True     # bool/int conflation
  'x != 0'              env={'x': False}    ->  False    # Python: False != 0 is False
  'x == x'              env={'x': nan}      ->  False
  'x > 5'               env={}              ->  False
```

**Every one of these returns a value; none raises.** A constraint whose variable name is misspelled evaluates the
limit as `0` — and for any upper-bound-style constraint (`x < 100`) that turns a **violated** limit into a
**passed** one. The source says so itself, in a comment:

```python
        # Unknown identifier — treat as 0 (type_confusion vectors may use unknown vars)
```

The comment says "type_confusion vectors may use unknown vars" — but the vectors that exist do not use unknown
vars. The behaviour is therefore **both untested and load-bearing**.

### 2d. The "compatibility proof" cannot fail

`flux/flux-hardware/tests/test_multi_compiler.py` — *"Proves that Oracle1's flux-compiler and Forgemaster's
guard2mask produce compatible FLUX bytecode that can be linked together."*

Its only imports are `struct` and `typing`. `compile_guard()` is a hand-written regex mini-compiler; `compile_structured()`
is documented in-source as a *"Simplified version of Oracle1's flux-compiler for testing."* **Neither is the real
compiler.** It proves a property of two local re-implementations.

And its `__main__` runner swallows every exception:

```python
        try:
            test()
        except Exception as e:
            print(f"  ❌ FAILED: {e}")
```

— with no `sys.exit(1)`, and an unconditional closing banner. **Measured**, by mutating `test_guard_compiles()`
to raise:

```
--- None ---
  ❌ FAILED: MUTATED: guard compiler did not produce expected bytecode
...
============================================================
Both compilers produce compatible FLUX-X bytecode.
Computation (Oracle1) and constraints (FM) link cleanly.
>>> EXIT CODE = 0
```

**A failing test prints a red banner, is followed by a green success banner, and the script exits 0.**

### 2e. Fairness: the one gate that *is* real

`tests/differential_test.py` **does** exit 1 on failure. Verified by mutation:

| mutation | result |
|---|---|
| invert `==` in the evaluator | `Total: 10 · Passed: 8 · Failed: 2 · PASS RATE: 80.0%` · **exit 1** |
| restore | `PASS RATE: 100.0%` · **exit 0** |

So `forgemaster`'s CI badge *can* go red. The problem is not vacuity — it is that the thing being gated is a
**re-implementation of a language the real compiler does not accept**, and the 2,216 lines of genuine pytest
(`tests/test_*.py`, 6 files) that would test the actual package are **never run by any workflow**. CI installs
`pytest` and then does not use it.

### 2f. And the complete CI history is 1,432 runs deep

`forgemaster` has **1,432 workflow runs** in total. Fetched to exhaustion (15 pages, `len(runs) == total_count`):

| workflow | green / total | window |
|---|---|---|
| **`.github/workflows/ci.yml`** | **0 / 629** | 2026-05-04 .. 2026-05-26 |
| **`Differential Test`** | **22 / 625** (96.5% red) | 2026-05-05 .. 2026-09-21 |
| `FLUX CI` | 22 / 22 | 2026-05-26 .. 2026-09-21 |
| `Metal SRAM Bake` | 0 / 2 | 2026-05-04 .. 2026-05-05 |
| `test` | 154 / 154 | 2026-05-08 .. 2026-05-17 |

**One workflow ran 629 times and never passed a single run.** Another — the `Differential Test` workflow that is
the *whole* of the CI described in §2b — **failed 603 of 625 times**. The green `FLUX CI` badge the repo shows
today belongs to the **22-run, four-month-old** workflow, not to the 629-run one that died in May 2026. **A badge
is a label on one workflow**, and a repo can carry a green badge and a 629-run corpse at the same time.

### 2g. And the README's headline API does not exist

```python
from forgemaster import Forge
forge = Forge()
build = forge.compile(requirements)     # README.md:43
```

```
Forge methods: ['artifact_for_recipe','build_all','build_one','cancel','config','get_artifact',
                'monitor','queue','register_artifact','reset_steps','stats','submit']
has compile? False
```

There is no `compile` anywhere in the package (`grep -rn "def compile" forgemaster/` → 0 hits). The 628-line
implementation underneath is coherent and real — a topological build queue with retries, artifacts, and an event
monitor — and it is simply **not the thing the README says it is**.

Bonus artifact: the README's own install line reads `git clone https://github.com/SuperInstance/forgemaster.git (dead)`
(twice). A link-checker wrote its verdict into the copy-paste instruction, so the documented command is now
literally a dead URL.

**Why another agent should care:** `forgemaster` is the repo that other agents' tools are supposed to *assemble
against*. Its 123 empty doors make the fleet's "one repo to rule them all" claim structurally false, and its
green CI is measuring a language that does not ship. **Two reusable checks:** (a) `git ls-files -s | grep -c 160000`
plus `test -f .gitmodules` — if the count is non-zero and `.gitmodules` is missing, the repo has empty doors and
`git submodule update --init` will fatal with exit 128; (b) **grep the CI file for what it actually runs.** If the
only test command is a hand-rolled script that re-implements the thing under test, the badge is a measurement of
the script.

---

## 3. `usemeter` — one project, two repos, four borrowed badges

**`SuperInstance/usemeter` · 11,181 tracked files, 5.06 GB of which 99.91% is committed build output · `SuperInstance/Tripartite1` · 266 tracked files.**

### 3a. The README is another repo's README

`usemeter/README.md` is 584 lines; `Tripartite1/README.md` is 472. The diff is **exactly two hunks**:

```
@@ -1,6 +1,12 @@       title, subtitle, and an ADDED "## Overview" section  (6 lines -> 12)
@@ -470,3 +476,109 @@  "## Architecture (Metering Pipeline)" appendix       (3 lines -> 109, i.e. 106 added)
```

Tripartite1 has **no** `## Overview` section at all — the overview is *added*, not replaced. **Everything else is
Tripartite1's, verbatim — including every badge:**

```markdown
[![CI](https://github.com/SuperInstance/Tripartite1/actions/workflows/ci.yml/badge.svg)](.../Tripartite1/...)
[![Documentation](https://github.com/SuperInstance/Tripartite1/actions/workflows/documentation.yml/badge.svg)](...)
[![Security](https://github.com/SuperInstance/Tripartite1/actions/workflows/security.yml/badge.svg)](...)
[![codecov](https://codecov.io/gh/SuperInstance/Tripartite1/branch/main/graph/badge.svg)](...)
[![Tests](https://img.shields.io/badge/tests-298%2F298-brightgreen.svg)](https://github.com/SuperInstance/Tripartite1)
```

**All four status badges and the test-count badge on `usemeter` report `Tripartite1`'s health.** And
`Tripartite1`'s health is:

| repo | workflow | green / total | newest |
|---|---|---|---|
| `Tripartite1` | CI | **0 / 14** | 2026-04-14, failure |
| `Tripartite1` | Documentation | **0 / 14** | 2026-04-14, failure |
| `Tripartite1` | Security | **0 / 71** | 2026-03-10, failure |
| `usemeter` | CI | **0 / 6** | 2026-04-15, failure |
| `usemeter` | Documentation | **0 / 6** | 2026-04-15, failure |
| `usemeter` | Security | **0 / 62** | 2026-03-11, failure |

**Every workflow in both repos has never passed a single run.** The badges are borrowed *and* red.

**And the test count is wrong.** The badge says `tests-298/298`. `Tripartite1` contains **247** `#[test]`
attributes — the badge overstates by 20.6% (247 confirmed three independent ways: `git grep -c`,
`git ls-files | xargs grep`, and a working-tree `grep -rho`; all three agree exactly, across 51 files). The same
README says *"**Tests**: 250+ passing (100%)"* in **four** separate places (lines 297, 309, 428, 470) and
*"**Version**: 0.2.0"* (lines 295, 470) while `usemeter/Cargo.toml` says `version = "0.1.0"`. It also claims
*"**Status**: Production-Ready (Phase 1)"* (line 470) next to a badge reading `phase-2`.

### 3b. 99.91% of the repository's bytes are committed build output

```
$ git ls-files | grep -c "/target/"
10671
$ git ls-files | wc -l
11181
$ (sum of tracked bytes under */target/*)
5063705578 bytes  =  5.06 GB (4.72 GiB)   # 99.91% of all tracked bytes
```

`model-registry/target/`, `privox/target/`, `quicunnel/target/`, `token-vault/target/`, `usemeter/target/` —
**10,671 tracked files, 5,063,705,578 bytes = 5.06 GB (4.72 GiB)**, which is **99.91% of every tracked byte in
the repository** and 95.46% of every tracked file. The largest single tracked artifacts are 70.8 MB
(`privox/target/debug/examples/server`), 46.4 MB (`quicunnel/target/debug/deps/quicunnel-*`) and 33.6 MB
(`token-vault/target/debug/deps/libreqwest-*.rlib`). The set also includes `debug/.cargo-lock` files and
`build/*/out/private.rs` generated sources. The `.gitignore` has `/target/` — **root-anchored**, so it correctly does not match the member crates'
targets, which is *why* they were committed. Not a cosmetic-ignore case; a scope case. But the result is the same:
the repository is 95.5% build output, and `usemeter` is 40× the size of its sibling for no substantive reason.

### 3c. No lockfile + warnings-as-errors = a CI that cannot stay green

```
.gitignore:6   Cargo.lock
$ git ls-files | grep -ci "cargo.lock"     # only target/*/.cargo-lock — cargo's own lock files, not a manifest
0
```

`ci.yml` sets, globally:

```yaml
env:
  RUSTFLAGS: -Dwarnings
```

and runs `cargo clippy --all-targets --all-features -- -D warnings` and
`cargo test --workspace --all-features --verbose` on a **floating `stable` toolchain** (`rust-toolchain.toml`
says `channel = "stable"`, not a pinned version) with **no committed `Cargo.lock`**.

`RUSTFLAGS` applies to **every** crate cargo compiles, including registry dependencies — unlike
`cargo clippy -- -D warnings`, which only lints the local crate. So a fresh dependency resolution on every run
means **any upstream release that introduces a warning turns the entire 4-way matrix red**, with nothing to pin
against. The matrix fails identically on ubuntu/stable, ubuntu/nightly, macos/stable and windows/stable, and the
coverage job fails with it — which is exactly the signature of a dependency-side failure rather than a
platform-specific one. The Security workflow (typos, `cargo deny`, gitleaks, `cargo audit`) fails 6 of 7 jobs for
the same reason: `cargo deny` and `cargo audit` both need a resolved lockfile to have anything to audit, and
there isn't one.

**Nothing in this repo can be green until a `Cargo.lock` is committed.** For a workspace that ships binaries,
committing the lockfile is also what makes the builds reproducible.

### 3d. CI tests 244 of 7,387 tests

The root `Cargo.toml` is **`synesis`'s** workspace, not usemeter's:

```toml
[workspace]
members = ["crates/synesis-cli", "crates/synesis-core", "crates/synesis-privacy",
           "crates/synesis-models", "crates/synesis-knowledge", "crates/synesis-cloud"]
exclude  = ["privox", "tripartite-rs", "knowledge-vault", "usemeter"]
```

`cargo test --workspace` therefore covers **`crates/synesis-*` only**. The `#[test]` census:

| crate | `#[test]` | in CI's workspace? |
|---|---|---|
| `privox` | **3,523** | ✗ excluded |
| `token-vault` | **1,768** | ✗ not a member |
| `model-registry` | **1,747** | ✗ not a member |
| `crates/synesis-*` | **244** | ✓ **the only ones CI runs** |
| `tripartite-rs` | 34 | ✗ excluded |
| `knowledge-vault-rs` | 28 | ✗ not a member |
| `quicunnel` | 20 | ✗ not a member |
| `usemeter` | **20** | ✗ **excluded — the repo's own crate** |
| `tests/integration/` (root) | **3** | ✗ **orphan — not a cargo test target at all** (see below) |
| **total** | **7,387** | **244 = 3.3%** |

**The repository named `usemeter` excludes the `usemeter` crate from the workspace its CI tests.** 96.7% of the
test suite is unrun, unlinted, and unformatted in CI, including the repo's own crate.

**And the last 3 are not even compiled by any cargo command.** The root `Cargo.toml` is a **virtual manifest** —
it has `[workspace]` and **no `[package]`** (`grep -c '^\[package\]' Cargo.toml` → 0). Cargo test targets live
at `<package>/tests/`, so a `tests/` directory sitting at the root of a virtual workspace is **not a test target
for any member**: `tests/integration/{consensus_flow,knowledge_vault,privacy_roundtrip}.rs` (3 `#[test]`s, plus
`hardware_constraints.rs`, `performance_benchmarks.rs`, `mod.rs`) are **orphan test code that no cargo invocation
can reach**.

**Why another agent should care:** the fleet census sees `usemeter` and `Tripartite1` as two projects. They are
one. An agent doing a fleet-wide survey will double-count it, and an agent picking a repo to trust will pick the
one with the *borrowed* badges. The reusable checks: (a) **diff a repo's README against its siblings before
believing a badge** — a badge URL that names a different repo is a *pointer*, and a pointer is not a status;
(b) `grep -rn "badge" README.md` and check the host repo in the URL; (c) count `#[test]` before believing a
`tests-N/N` badge; (d) for Rust, check `Cargo.lock` tracked-ness and `RUSTFLAGS` together.

---

## 4. `fm-experiments` — 330 files, no dependencies file, a CI that never ran

**`SuperInstance/fm-experiments` · 330 Python files · 82+ study documents · CI: 0/2 (never passed).**

The repo is a genuine research archive — `STUDY-01` … `STUDY-82`, `CAMPAIGN-A` … `CAMPAIGN-D` results,
`E1`…`E12` live experiments, 179 files importing `torch`/`numpy`. It is also, structurally, a research dump with
no build system:

```
$ ls requirements*.txt setup.py pyproject.toml
ls: cannot access 'requirements*.txt': No such file or directory
ls: cannot access 'setup.py': No such file or directory
ls: cannot access 'pyproject.toml': No such file or directory
```

and the CI is:

```yaml
      - name: Install dependencies
        run: |
          pip install pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f setup.py ]; then pip install -e .; fi
      - name: Run tests
        run: python -m pytest -v
```

**Both `if` guards are false.** Nothing but `pytest` is installed. Then `python -m pytest -v` runs from the repo
**root**, collecting all **14** test files — including `delta-detect/test_delta_detect.py` and
`holonomy-phase/experiment.py` (`import torch`, `import torch.nn as nn`, `import torch.nn.functional as F`) and
`sheaf-h1/test_sheaf.py` (`import numpy as np`). Those imports cannot resolve, so collection errors. Measured
from the jobs API on both runs:

```
  CI 2026-08-21T16:48 failure   Install dependencies -> success | Run tests -> failure
  CI 2026-08-14T06:06 failure   Install dependencies -> success | Run tests -> failure
```

**The three headline experiments in the README are exactly the ones that cannot be collected.** Two of the three
(`delta-detect`, `holonomy-phase`) need `torch`; the third (`sheaf-h1`) needs `numpy`. The README's own Quick
Summary table marks all three "Done" with run times of "~30s", "~1s", "~30s" — and CI has never run any of them.

**And the README contradicts itself in its first three lines:** *"**Four** experiments that test the core claims
from the 7-agent research sprint"* — over a Quick Summary table with **three** rows. The repo in fact contains
~30 experiment directories (`bounded-drift`, `consciousness-predictions`, `cyclotomic-verify`, `distributed-consensus`,
`dodecet-bloom`, `enactive-engine`, `financial-markets`, `fleet-verification`, `flux-fold`, `galois-retrieval`,
`info-theory-synergy`, `materials-science`, `model-competition`, `model-ocean`, `platonic-snap`, `sensor-fusion`,
`tiny-model-test`, `traceable-rooms`, `voronoi-candidates`, `zai-p3`, …).

**Why another agent should care:** the fleet's research corpus is here, and it is **unverifiable as shipped** —
not because the science is wrong, but because there is no dependency manifest and the CI cannot install what the
code imports. The fix is one file (`requirements.txt`) plus scoping pytest to the directories that exist; the
research value is entirely in `STUDY-*.md` + `*_results.json` pairs, which are readable today. The reusable
check: **if a repo's CI has `if [ -f requirements.txt ]` guards and no requirements.txt exists, the CI installs
nothing but the test runner — and a repo whose tests import anything else is guaranteed red.** Grep the CI's
install step for what it *actually* installs, then grep the test files for their imports.

---

## 5. `exoj` — the positive control, mutation-verified

**`SuperInstance/exoj` · 34 JS/TS files · CI: forge 17/17, smoke 27/27 (both green) · contains the canary.**

This is the artifact the rest of this report should be measured against.

**It runs, locally, with no install and no network:**

```
$ node --test lab/*.test.mjs
# tests 28
# pass 28
# fail 0
```

**The README-pinning test is mutation-verified — a check that can fail:**

`lab/readme-pin.test.mjs` asserts that the README's headline numbers are pinned to the artifact of record
(`experiments/outputs/e40_scratch.json`), that conservation `Σ ≤ 1 + 1e-9` holds *in the artifact*, and that the
README names its artifact.

```
# PASS  deformations pinned to artifact   readme=39 artifact=39
# PASS  observations pinned to artifact   readme=1 artifact=1
# PASS  prob_open pinned to artifact (±0.001)  readme=0.9412 artifact=0.9412
# PASS  conservation Σ ≤ 1 + 1e-9 in artifact  Σ=0.9999999999999999
# PASS  README names its artifact of record
# ALL GREEN: 6 pass, 0 fail
```

| mutation | result |
|---|---|
| README `prob_open=0.9412` → `0.95` | `# FAIL prob_open pinned to artifact (±0.001) readme=0.95 artifact=0.9412` · **exit 1** |
| restore | `# pass 1 · # fail 0` · exit 0 |

**The spec gate is fail-closed, sha256-sealed, and first.** `tools/spec_gate.mjs` refuses to proceed with named
codes — `E_SPEC_MISSING`, `E_SPEC_SHA_MISSING`, `E_SPEC_MALFORMED`, `E_SPEC_DIALECT`, `E_SPEC_TAMPERED` — and
`smoke.yml` runs it **before** the tests:

```yaml
      - name: Spec gate (specification-first)
        run: node tools/spec_gate.mjs
      - name: Unit batteries (lab/*.test.mjs)
        run: npm test
      - name: Smoke
        run: node smoke.mjs
```

Note the ordering: **spec → tests → smoke.** This is the exact inverse of `exocortex`, where lint sat in front
of the tests and killed them.

**The charter promise is kept.** The README says the charter is *"versioned in this repo's first commit and never
edited afterward."* Verified against first commit `b7e83f2c` ("seed: charter committed verbatim — the question is
the first receipt", 2026-09-26): the charter section is **byte-identical** to HEAD. The README's *results* numbers
were updated — and, correctly, **pinned to an artifact of record** with the note *"earlier numbers in this README
narrate earlier runs"*, which the pin test then holds them to.

**`ANTI-ENTROPY-LOG.md` is an append-only fault ledger** — each fault recorded when found *and* when fixed, e.g.
`F1 — test script absent / broken directory mode`: *"node --test lab/ (directory mode) fails on node ≥ 22 (treats
the directory as a single test entry) — the same defect the wave-67 verification found in three other repos."*
That is the fleet documenting a **class** of defect, not an instance.

**And it carries the canary, correctly:**

```
atlas-data/parts/garden/jeviter.json:49
  "essence": "… BigInt FNV-1a 64 over UTF-8 bytes, pinned to the fleet vector
               fnv1a64(\"café Δ 日本語\") === 0x24a555471370b18d …"
```

Re-derived locally: `FNV-1a 64("café Δ 日本語") = 0x24a555471370b18d = 2640610520279855501` — the **integer** matches.
(The accent trap is live and confirmed: unaccented `"cafe Δ 日本語"` hashes to `0xfee91cf40962b966` — a different
integer that renders identically on screen.)

**Why another agent should care:** `exoj` is the *procedure* the fleet is missing everywhere else. A receipt
discipline, a sealed spec, a fail-closed gate that runs first, a README whose numbers are machine-pinned to their
artifacts, an append-only fault ledger, and a charter that is provably immutable. **`exoj` is the thing to copy
into `forgemaster`, `exocortex`, `usemeter` and `fm-experiments` — not the code.**

---

## 6. Negative findings, stated as findings

- **`forgemaster` README contradicts its own package.** `forge.compile(requirements)` does not exist (§2f).
- **`forgemaster` README contradicts its own install line.** `git clone …/forgemaster.git (dead)` (§2f).
- **`forgemaster` README contradicts its own grammar.** The test vectors' `constraint { expr:, inputs: }` syntax is
  not in `GRAMMAR.ebnf` (§2b).
- **`fm-experiments` README contradicts itself.** "Four experiments" over a three-row table, in a repo with ~30
  experiment directories (§4).
- **`usemeter` README contradicts `usemeter/Cargo.toml`.** "Version 0.2.0" vs `version = "0.1.0"`; "Production-Ready
  (Phase 1)" vs a `phase-2` badge; "250+ tests passing (100%)" vs a CI with zero passing runs; `tests-298/298` vs
  247 actual `#[test]`s (§3a).
- **`usemeter` and `Tripartite1` are one project under two names**, and the fleet census counts them as two (§3).

---

## 7. Method notes and corrections (carry forward)

**New reusable checks, each one cheap and each one earned today:**

1. **`git ls-files -s | grep -c 160000` + `test -f .gitmodules`.** If the first is non-zero and the second is
   absent → every gitlink is an empty door and `git submodule update --init` exits 128. Found 123 in `forgemaster`.
2. **Read the CI file, not the badge.** Name the *exact command* each workflow runs. A workflow whose only test
   step is a hand-rolled script is measuring the script.
3. **Check that the test imports the thing under test.** `grep -n "^import\|^from" <test>` — zero hits on the
   package is a self-referential test, even if it can go red.
4. **Read the jobs payload, not the runs payload.** A failed first step turns the rest into `skipped`; a failed
   matrix leg with default `fail-fast` turns the siblings into `cancelled`. Both hide the test suite.
5. **Check badge URLs for a foreign host repo.** A badge that points at a different repo is a pointer, not a status.
6. **Count `#[test]` before believing a `tests-N/N` badge.** And for Rust: `Cargo.lock` tracked-ness **together
   with** `RUSTFLAGS: -Dwarnings` — that pair is a permanent-red machine.
7. **Diff a repo's README against its closest sibling.** `usemeter` vs `Tripartite1` — **two** diff hunks, and
   every status badge inherited verbatim from the sibling. A 584-line README that is 472 lines of someone
   else's.
8. **If a repo's CI has `if [ -f requirements.txt ]` guards, check the file exists.** If it does not, the CI
   installed nothing but the test runner.

**Corrections to standing guidance:**

- The **5,113 repos / 52 pages** figure in the standing brief is **stale**. It is **5,296 / 53 pages** today
  (821 forks / 4,475 own / 16 archived). It has been stable for ~3 hours but grows ~10/day — re-derive, do not
  hardcode, and note that the number in the brief is now 183 behind.
- The **examined set is 1,319 own repos** (bare-token extraction over all 111 prior reports, intersected with the
  fleet's real name list), **not** the ~4556 raw bare-token hits — a bare-token pass without intersecting against
  the fleet's own names produces ~3.4× false positives.
- **The `write` tool still cannot reach `/tmp` and `/workspace` is at 100% EDQUOT with silent 0-byte writes**
  (a `printf 'x' > /workspace/.wtest` returns exit 0 and produces a 0-byte file). Durable mirror remains
  `/tmp` + the GitHub snapshot. The `team` tool's `plan_path` is required to live inside the workspace root, so
  **team plans are unavailable while the NAS is full** — this run was executed solo, with an independent verifier
  spawned for the audit pass.
- **`pip install` is blocked in this sandbox** (network refused, and the system Python is PEP-668 managed), so
  `pytest` and `ruff` could not be executed. Where a lint or test outcome is claimed above, it is derived from
  the **jobs API payload** (what GitHub actually ran) plus a static AST check of the rule that fails — and it is
  labelled as such.
- **Correction carried into the canon (why the banner at the top is there).** The first draft of §1 said the
  exocortex pytest suite *"has never run in CI."* It did — 11 successful `Run tests` steps on 2026-07-12/13/20.
  The error was **reading one recent run's job payload and generalising it to the repo's history**. The rule this
  earns: *a "never" claim about a CI step requires reading the step list across the **whole** run history, and
  `per_page=100` on `/actions/runs` is not enough* — `forgemaster` has **1,432** runs and my first pass fetched
  only 600, which is how its `Differential Test` workflow looked like 22/50. Re-fetched to exhaustion (15 pages,
  `len(runs) == total_count == 1432`): the true figures are **`Differential Test` 22/625 green** and
  **`.github/workflows/ci.yml` 0/629 green** (not 0/28, and not 0/222 either — that figure was itself measured
  over only 600 runs). The corrected §1 is strictly stronger than the original: three eras of one step, and a
  break on a Markdown-only commit.
- **Independent adversarial verification.** This report was audited by a separate verifier agent working from a
  **from-scratch clone in a different sandbox** (no access to the author's files, notes, or clones), with an
  explicit brief to break every claim. It **confirmed** the load-bearing claims: the 123/123 empty gitlinks and
  the exit-128 `submodule update`; `test_multi_compiler.py` exiting 0 with a success banner while its own test
  fails; the five foreign badges and the `tests-298/298` vs 247 gap; the usemeter byte count **to the byte**
  (10,671 files / 5,063,705,578); the full `#[test]` census (7,387 total, 244 in `crates/`, privox 3,523,
  token-vault 1,768, model-registry 1,747, tripartite-rs 34, knowledge-vault-rs 28, quicunnel 20, usemeter 20);
  and the exocortex jobs payload showing `Lint (ruff) -> failure` + `Run tests -> skipped`. It also **found four
  errors in this report, all corrected above**: (1) the README diff is **two** hunks, not five, and the appendix
  is **106** added lines, not 112; (2) the Overview is *added*, not *replaced*; (3) "250+ tests passing (100%)"
  appears in **four** places, not three; (4) the byte figure is **5.06 GB (4.72 GiB)**, not 4.83 GB. It also
  correctly located the **3 `#[test]`s my table was missing** — in the root `tests/integration/` — which turned a
  cosmetic table gap into the virtual-manifest finding above. One claim it queried, the **247 `#[test]`s in
  `Tripartite1`**, was re-measured three independent ways and is exact; the verifier's 0 was an artifact of its
  own script, not a defect in the claim.
- **Read a CI file's *git history*, not just its current contents.** `git log -- .github/workflows/ci.yml` for
  exocortex is four commits, and the current file is a *later* generation than the one the first green run used.
  The `pytest || true` era and the `Lint (ruff)` era are both invisible in the current file. `cargo`/`rustc` are absent, so no Rust code was executed; the Rust findings are read-only
  and are stated as such.
- **No `usemeter`/`Tripartite1`/`forgemaster` `Cargo.lock` exists, so the dependency-resolution theory of their
  red CI is a hypothesis, not a measured cause.** The *measured* facts are: every workflow in both repos has
  never passed, the matrix fails identically on all four OS/toolchain legs, `RUSTFLAGS: -Dwarnings` is global,
  the toolchain is floating `stable`, and no lockfile is tracked. The interaction is the standard mechanism, but
  the logs expired (HTTP 410 on the job-logs endpoint) so the failing line could not be read directly.

---

## 8. What to do next (in priority order)

1. **`exocortex`:** pin the linter (`ruff==<version>` in the dev extra), move `ruff check .` into its own job
   (or add `continue-on-error: true` to it), add `fail-fast: false` to the matrix, and delete the 37 unused
   imports. That is a 20-minute fix that turns a red badge into a real one — and un-skips a test suite that
   **passed 11 times** and has been dark for six consecutive runs since 2026-08-05.
2. **`forgemaster`:** add the missing `.gitmodules` (or delete the 123 gitlinks). Until one of those happens, the
   repo cannot be cloned into a working state by anyone. Then point CI at the real `guardc` compiler and at
   `tests/test_*.py` instead of the re-implementation, and give `test_multi_compiler.py` a real `sys.exit(1)`.
3. **`usemeter`:** commit `Cargo.lock`, drop the global `RUSTFLAGS: -Dwarnings` (keep it on the clippy step, where
   it only applies to local code), add the excluded crates to the workspace or test them separately, and
   `git rm -r --cached` the 5.06 GB of `target/`. Then fix the README to point its badges at `usemeter`.
4. **`fm-experiments`:** write a `requirements.txt` and scope `pytest` to the directories that can import.
5. **Everywhere:** adopt `exoj`'s three pieces — a sealed spec gate that runs **first**, a README-pin test that
   holds the README's numbers to their artifacts, and an append-only anti-entropy log.
