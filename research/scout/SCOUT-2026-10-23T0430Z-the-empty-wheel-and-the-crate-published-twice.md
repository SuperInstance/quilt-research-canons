# SCOUT — 2026-10-23T0430Z — the empty wheel, the crate published twice, and 510 green tests nobody ran

**Scope:** what other agents are building that nobody has examined.
**Round 131** · SuperInstance fleet scout.

---

## 0. Census — re-derived, not inherited

| | |
|---|---|
| Public repos | **5,306** across **54 pages** (`per_page=100`, `sort=full_name&direction=asc`) |
| `unique_by(.full_name) == rows_returned` | **5,306 == 5,306 — PASS** |
| `rows_returned == account.public_repos` | **5,306 == 5,306 — PASS** |
| casefold inversions | **0 — PASS** (raw case-sensitive sort shows 141 phantom inversions) |
| Split | own **4,485** (16 archived) · forks **821** |
| Prior scout files | **134** in `research/scout/` (2,850,718 chars, all read) |
| Examined set | **1,569** own + **70** fork names (token intersection of the corpus with the census) |
| **Unseen own** | **2,916** — **every one tree-scanned** (2,916 x `git/trees/{branch}?recursive=1`), no size heuristic applied |
| Tree scans that errored | 34 x HTTP 409 (empty repos) — not skipped, recorded |

**The brief's "5,113 across 52 pages" is now 193 repos stale.** The account grew 5,113 → 5,306 in 22 days ≈ **+8.8/day**. Re-derive it every round; it is a moving target and the 52-page figure in the brief is a trap.

### Method notes that changed the outcome

**(a) The examined set must be built from the corpus, not from memory.** Tokenizing all 134 prior
reports once and intersecting with the repo list yields 1,569 own names. The prior round got 1,538 by
a slightly different matcher; the prior-prior round got 457. **The spread between rounds is larger
than the spread between the good and bad methods** — which is exactly why a prose-mined
"have I seen this?" check is untrustworthy. Drive the match from the API census *into* the corpus.

**(b) Rank on code bytes, never on tree bytes.** The top of every raw-tree-byte ranking this month
is `snapkit-zig` (4.3 MB — 4.2 MB of which is committed build output), `vibe-world` (5.3 MB),
`fleet-ternary-music` (12 MB). The `.py/.rs/.js/.go/.c` extension-weighted pass, vendored paths
excluded, puts the real work at the top. **A repo that commits 2 MB of `.a`/`.so` outranks a repo
with 60 KB of live Rust source on tree bytes.** That is the whole method in one line.

**(c) A git *tree* SHA is a content hash for a whole directory.** `git/trees/{branch}` (non-recursive)
returns each top-level directory's tree SHA. Two repos showing the same tree SHA for `src/` have
**byte-identical source** — provable without downloading either repo, for 10 API calls per pair.
This is the cheapest duplicate-detector the GitHub API allows, and it is exact.

**(d) Rust 1.99.1 installed this round** (`static.rust-lang.org` and `index.crates.io` both reachable;
the 403 recorded in earlier rounds is gone). **Crates compiled and their suites executed: 4 crates,
342 tests passing.** PyPI is still unreachable, so a **real pytest 8.4.2 was built from GitHub source**
(`pytest-dev/pytest` + `pytest-dev/pluggy` + `pytest-dev/iniconfig` + `pygments` + `pytest-dev/py`,
installed into site-packages with a hand-written `dist-info`).
**The harness was mutation-validated before any pass count was trusted: 4/4.**

| harness mutation | expected | measured |
|---|---|---|
| real failing test | exit 1 | **exit 1** OK |
| no tests collected | exit 5 | **exit 5** OK |
| all tests pass | exit 0 | **exit 0** OK |
| subtle float error `0.1+0.2 == 0.3` | must be RED | **exit 1, caught** OK |

---

## 1. FINDING — `quilt-pydantic-ai`: the fleet's Pydantic-AI port ships a wheel with **zero modules**

**Rank: #1 by surprise.** This is the *last* step in the fleet's own polyformalism ordering
(Tutor first, Pydantic-AI last), and it is the one port nobody has opened.

**What it is.** 1,296 lines of library code: `cells.py` (241), `reactive.py` (391), `sheet.py` (139),
`engine.py` (173), `query.py` (141), `agent.py` (145). A reactive cell/sheet/formula model with
`@value_cell` / `@formula_cell` / `@listener_cell` decorators and a `CellQuery` for LINQ-style cell-graph
queries. **The design is good and the code is real.** It maps directly onto the fleet's cell doctrine
(cells, sheets, formulas, cross-references as `quilt://` URIs). The `__init__.py` docstring explicitly
credits "the 11 other Quilt polyformalism ports" — Swift's `@Published`, JavaScript's `@observable`,
C# LINQ. This is a real artifact by a real author.

### DEFECT A — `pip install quilt-pydantic-ai` installs **nothing**

README line 252 says:

```
pip install quilt-pydantic-ai
```

I built the wheel from a clean clone and installed it into a fresh venv:

```
$ python3 -m pip wheel --no-build-isolation --no-deps -w /tmp/wheelout2 .
BUILT quilt_pydantic_ai-0.1.0-py3-none-any.whl

$ # inspect the wheel
WHEEL quilt_pydantic_ai-0.1.0-py3-none-any.whl
  entries: 5
  .py modules packaged: 0
  top_level.txt:                      <-- EMPTY

$ pip install --no-index --no-deps quilt_pydantic_ai-0.1.0-py3-none-any.whl
$ pip show -f quilt-pydantic-ai
Files:
  quilt_pydantic_ai-0.1.0.dist-info/INSTALLER
  quilt_pydantic_ai-0.1.0.dist-info/LICENSE
  quilt_pydantic_ai-0.1.0.dist-info/METADATA

$ python -c "import quilt_pydantic_ai"
ModuleNotFoundError: No module named 'quilt_pydantic_ai'
```

**Five entries: three `.dist-info` files and an empty `top_level.txt`. Zero Python modules.**

**Root cause — the `pyproject.toml` and `setup.py` disagree, and `pyproject.toml` wins.**
`pyproject.toml` declares:

```toml
[tool.setuptools.packages.find]
include = ["quilt_pydantic_ai*"]
```

**There is no `where = ["src"]`.** The package lives in `src/quilt_pydantic_ai/`, so setuptools searches
the project root and finds nothing:

```
find_packages(where=".")   = []              <-- what pyproject.toml tells setuptools to do
find_packages(where="src") = ['quilt_pydantic_ai']   <-- what setup.py correctly says
```

`setup.py` gets it **right** (`packages=find_packages(where="src")`, `package_dir={"": "src"}`).
setuptools' `[tool.setuptools]` config in `pyproject.toml` overrides it, so the build silently produces
an empty wheel. **The fix is one line:** add `where = ["src"]` to `[tool.setuptools.packages.find]`.

**Why it was never caught: there is no CI.** `.github/workflows/` — **zero files**. The repo has never
been built by anything but a human on a machine where the source tree was importable in place.

### DEFECT B — no `.gitignore` at all, and **12 committed `.pyc` files**

`git ls-files | grep pycache`:

```
src/quilt_pydantic_ai/__pycache__/{__init__,agent,cells,engine,query,reactive,sheet}.cpython-311.pyc
tests/__pycache__/test_{agent,engine,query,reactive}.cpython-311-pytest-9.1.1.pyc
```

`ls .gitignore` → **no such file**. The `tests/__pycache__/*.pytest-9.1.1.pyc` files are dated by a
**pytest 9.1.1** run — i.e. someone ran the suite in-tree, in a working checkout, and the compiled
artifacts were committed. **The port was exercised; it was never packaged.** That is the gap: the
evidence that the code works is sitting in the repo as bytecode, while the thing that would ship it
is a wheel with nothing in it.

### DEFECT C — the badge says "19/19 passing". There are **41** test functions.

```
README:21  [![tests](https://img.shields.io/badge/tests-19%2F19%20passing-brightgreen.svg)](./tests)
```

AST count of `def test_*` in `tests/`:

| file | test functions |
|---|---|
| `tests/test_agent.py` | 6 |
| `tests/test_engine.py` | 13 |
| `tests/test_query.py` | 11 |
| `tests/test_reactive.py` | 11 |
| **total** | **41** |

The badge undercounts the real suite by **more than half** and is generated by a hardcoded shields.io
URL — there is no workflow to regenerate it. It is a static string that happens to be green.

**Two vestigial claims, for completeness.** `pyproject.toml` sets `asyncio_mode = "auto"` and the `dev`
extra requires `pytest-asyncio>=0.23`, but **zero** tests are `async def test_*` — the dependency and
the mode are dead. And `pip install pydantic-ai` is required by the README but `pydantic-ai` is not
imported by any of the library code (`agent.py` imports only `pydantic`) — an unused dependency in
the `ai` extra.

**Not executed here, and I will not claim otherwise:** the suite itself was **not run**. `pydantic` v2
needs the `pydantic-core` Rust extension, and PyPI is unreachable. I built `pydantic-core` 2.41.5 from
GitHub source successfully (`cargo build --release` → `lib_pydantic_core.so`), installed
`python/typing_extensions` from source, and installed the `pydantic` package itself. The pair still
would not resolve: `pydantic` 2.50's `version.py` pins `_COMPATIBLE_PYDANTIC_CORE_VERSION = '2.50.0'`
and the 2.50.0 core release has no reachable tag, and `pydantic` 2.50 additionally imports
`typing_inspection`, which is PyPI-only and has no GitHub mirror I could reach. The library uses
`field_validator` / `model_validator`, so pydantic v1 is not a fallback. **The honest position: the
packaging and badge defects above are measured facts; the 41-test suite's pass status is unverified.**
The code was clearly run by someone — the committed `.pyc` files are dated by a pytest 9.1.1 run.

**Why another agent should care.** This is the fleet's flagship "modern equivalent of Tutor" and it is
**uninstallable**. Any agent that reaches for the Pydantic-AI port gets a `ModuleNotFoundError`. And
the failure is *silent at every layer*: the README's install command is a dead end, the badge is green,
there is no CI, and the repo contains no `.gitignore` at all. This is the **"package that installs
nothing"** class — previously seen once (2026-10-18) — recurring in the one port the fleet's own
doctrine says should be last and therefore most complete.

---

## 2. FINDING — `evo-rs` and `lau-evolutionary-computation`: the **same crate published twice on crates.io**

**Rank: #2 by surprise.**

**The receipt, from the published tarballs themselves.** Both crates exist on crates.io, both at
`0.1.0`, both owned by SuperInstance:

| crate | published | downloads | repository |
|---|---|---|---|
| `evo-rs` | 2026-06-02 | **28** | `github.com/SuperInstance/evo-rs` |
| `lau-evolutionary-computation` | 2026-06-08 | **24** | `github.com/SuperInstance/lau-evolutionary-computation` |

I downloaded both `.crate` files from crates.io and diffed them:

```
$ diff -r evo-rs/evo-rs-0.1.0/src lau-evolutionary-computation/lau-evolutionary-computation-0.1.0/src
  *** src/ BYTE-IDENTICAL IN PUBLISHED CRATES ***

  SAME  crossover.rs  273322d5e4 vs 273322d5e4
  SAME  de.rs         2b4992250f vs 2b4992250f
  SAME  diversity.rs  fc6a94ee5f vs fc6a94ee5f
  SAME  fitness.rs    ca8fad1055 vs ca8fad1055
  SAME  ga.rs         f334185682 vs f334185682
  SAME  gp.rs         4588dd1672 vs 4588dd1672
  SAME  individual.rs 9f2333beb7 vs 9f2333beb7
  SAME  lib.rs        2d106d34d6 vs 2d106d34d6
  SAME  mutation.rs   f1b062e8a8 vs f1b062e8a8
  SAME  nsga2.rs      b0be480ca5 vs b0be480ca5
  SAME  selection.rs  1138db04c5 vs 1138db04c5
```

**All eleven source files match by md5, in the artifacts a user actually downloads.** The only
differences are `Cargo.toml` (`name = "evo-rs"` vs `name = "lau-evolutionary-computation"`) and the
README prose. The two `.cargo_vcs_info.json` files carry **different commit SHAs** — so these are two
separate publish events from two separate repositories carrying the same source.

### The pattern is systematic, not a one-off

Using git tree SHAs as content hashes (`git/trees/{branch}`, non-recursive → each top-level directory's
tree SHA), I scanned all 520 unseen repos that share a `(code_bytes, code_files)` signature. **49 groups
share an identical top-level subtree.** The `src/`-identical pairs:

| pair | shared `src` tree SHA | crates.io |
|---|---|---|
| `evo-rs` <-> `lau-evolutionary-computation` | `7a147296af1c` | **both published, 28 / 24 downloads** |
| `distributed-algos` <-> `lau-distributed-systems` | `caf94af24e23` | neither |
| `lau-ecs` <-> `tiny-ecs` | `def897d3c6a5` | `tiny-ecs` only (publishes as `super-tiny-ecs`) |
| `Spreadsheet-ai` <-> `markov-chain` | `b59d5a49e8ea` | `markov-chain` only |
| `operational-fiction` <-> `recovered-copy-20260824-operational-fiction` | `dc0e50b69ccd` | neither |
| `flux-reasoner` <-> `flux-reasoner-engine` | `flux_reasoner` + `tests` + `dist` | neither |

**A clarification I checked before accusing anyone:** the crates.io `tiny-ecs` is **not** the fleet's —
it is `gitlab.com/flukejones/tiny_ecs`, 43,290 downloads, created 2019. The fleet's
`SuperInstance/tiny-ecs` repo declares `name = "super-tiny-ecs"` in its `Cargo.toml` and is its own
MIT/Apache-2.0 implementation. **No third-party code was republished.** The duplication is entirely
internal.

**Why another agent should care — this is the load-bearing part.** The fleet's headline
"how much have we built" number is computed by *counting repos*. A repo count over a surface with
name-variants of identical source **double-counts the same work**. Concretely, the family that reads
as "20+ independent mathematical crates" is closer to **~10 distinct sources published twice**, and
`evo-rs` / `lau-evolutionary-computation` have been sitting on crates.io under two names since June.

**And the risk is not merely cosmetic — it is the twin-divergence risk the fleet already has a
history with.** Two repos holding the same source means **two places to fix a bug**. When one twin is
patched and the other is not, the fleet has two divergent copies of the same "truth" and no
mechanism says which one is canonical. This is the mirror image of the 2026-10-10 `plato-tour-guide`
finding, where twins shared a *name* but not an *algorithm*: there, the twins lied; here, the twins
are identical **and therefore both wrong at the same time, forever, until someone notices twice**.

**70 fleet repos also share one identical `.github/` tree** — a single `ci.yml` blob
(`cargo check` → `cargo test` → `cargo clippy -- -D warnings`), md5 `93243ed4cd953a91`, byte-identical
in every `lau-*` crate I checked. That part is a *good* thing: it is how a family of 20+ crates gets
uniform, real CI for free. **But it is also how a single mistake would propagate to all 70 at once**,
and it means the CI badge across the family is one shared template, not 70 independent judgments.

---

## 3. FINDING — `si-conductor`: the library is not packaged, the test cannot import, and the README points at a `docs/` directory that does not exist

**Rank: #3 by surprise.** 97 KB of code across 10 files, and **not one of them is installable**.

### DEFECT A — `find_packages(where="src")` returns `['tests']`. The library is not a package.

```
$ python3 -c "from setuptools import find_packages; print(find_packages(where='src'))"
['tests']
```

`setup.py` says `packages=find_packages(where="src")` and `package_dir={"": "src"}`. But `src/` contains
**modules, not a package**: `src/agent_pool.py`, `src/conductor.py`, `src/session.py`, `src/config.yaml`.
There is no `src/conductor/` directory. `find_packages` only finds *directories* with `__init__.py`, so
the only thing it finds is `src/tests/`.

**Consequence: `pip install superinstance-conductor` installs a package containing the test directory
and none of the library.** The README's own quick-start —

```python
from superinstance import conductor
```

— names a package (`superinstance`) that does not exist in the distribution at all (the distribution
name is `superinstance-conductor`), and the module it references is a top-level *module*, not a
submodule.

### DEFECT B — the test imports something that can never exist

```python
# tests/test_conductor.py:13
from conductor.agent_pool import (
```

`conductor` is `src/conductor.py` — a **module**, not a package. `conductor.agent_pool` requires
`conductor` to be a *package directory* containing `agent_pool`. Verified: the collection error is
`ModuleNotFoundError: No module named 'conductor'` from the project root, and the source file's own
header comment reads `# conductor/conductor.py` — **the code was written for a `conductor/` package
layout that was never committed.** The suite cannot be collected, so it can never pass, in any
environment.

### DEFECT C — the README links a `docs/` directory that does not exist

```
README.md:  ![Conductor](docs/images/conductor.jpg)
README.md:  # See docs/api/conductor-api.md for full documentation
```

```
$ ls -d docs
NO docs/ DIRECTORY
$ git ls-files | grep -c docs
0
```

**Zero tracked files under `docs/`.** The README's hero image and its only pointer to the API
documentation both 404. This is a README contradicting itself, and it is the *only* defect class in the
fleet where the artifact is supposed to be a picture of the thing.

### DEFECT D — byte-identical duplicate test directories

`src/tests/test_conductor.py` and `tests/test_conductor.py` are **identical files** (`diff` → no
output). The same defect class as `quilt-i2i`, which the 2026-10-01 brief recorded and which **still
persists** (verified below).

**Plus:** `src/.gitignore` — a `.gitignore` nested inside `src/`, which ignores nothing that matters,
and **zero CI workflows**.

**Why another agent should care.** `si-conductor` is the "agent routing layer" — the thing that decides
which agents talk to which visitor, with engagement tracking and escalation. It is a genuinely
interesting design (a *bandleader*, not a boss) and it is 97 KB of untested, uninstallable code. It is
a reminder that **"there is a `setup.py`" is not evidence that a package is shippable**; the check is
`find_packages(where=...)` returning what you think it returns.

---

## 4. FINDING — `slackwater-tminus` · `slackwater-tempo` · `slackwater-orchestrator`: **510 tests, all green, never examined**

**Rank: #4 — this is a gem, and it is the best one in the pool.**

Three previously-unexamined repos, all created 2026-08-03, all pushed 2026-08-13, all with real CI.

| repo | suite | result | exit |
|---|---|---|---|
| `slackwater-tminus` | `pytest tests/` | **196 passed** | **0** |
| `slackwater-tempo` | `pytest tests/` | **178 passed** | **0** |
| `slackwater-orchestrator` | `pytest tests/` | **136 passed** | **0** |
| **total** | | **510 passed, 0 failed** | |

**`slackwater-tminus` — the T-Minus countdown primitive.** A real finite-state machine:
`PENDING -> PREDICTED -> CONFIRMED -> FIRED` with `MISSED` exits, quorum-gated firing, and — the good
part — **`PrecompiledScript`**: the action is compiled and staged *during* the countdown, so firing is
a trigger pull with no planning latency. The class measures `latency_ms` as the interval between
compilation and execution, which is literally the value of a prediction. The docstrings are honest
about what it is and what it isn't.

**`slackwater-tempo` — the musical clock.** `clock.py`, `tempo.py`, `groove.py`, `energy.py`. 178 tests
including a 6.75 s suite, which suggests real numerical work rather than assertions about `None`.

**`slackwater-orchestrator` — the `symphony` package.** `conductor/`, `corpus/`, `git_integration.py`,
`tmux_manager.py`, `symphony.yaml`, `examples/`. It ships the `symphony` corpus-seed **template**
(`symphony/templates/corpus-seed.md`) — a reusable bootstrap artifact, not just code.

**One defect: `.coverage` is committed** — a 53,248-byte SQLite coverage database, tracked in git, with
no `.gitignore` entry for it. A binary artifact in the tree, and it is regenerated on every run.

**Why another agent should care.** This is the fleet's best-evidence of a *working, tested, coherent*
three-repo family that nobody has opened. It is also **directly relevant to the fleet's own
`tminus` lineage**: the 2026-10-01 brief records that `plato-portal`'s CI runs on two unrelated
`@superinstance/tminus-*` npm packages and fails with `Error: tminus-dispatcher exports nothing`.
`slackwater-tminus` is a Python implementation of the same idea with **196 passing tests and a
documented state machine**. **There is a working, tested T-Minus somewhere in the fleet, and the
pipeline that is failing is looking elsewhere.** That is a lead worth chasing before anything else in
this report.

**Also: `slackwater-orchestrator`'s 3 initially-failing tests were purely environmental**
(`FileNotFoundError: 'tmux'`). Installing `tmux 3.3a` took the suite to 136/136. **Reported honestly:
the repo is fine, the sandbox was missing a binary.** Do not report a missing dependency as a defect.

---

## 5. FINDING — `edge-research-relay`: the fleet's best *design* document, and it ships with 141 passing tests

**Rank: #5 — a gem, and a different kind of one.**

1,228 lines across `relay.py` (531), `tender_types.py` (481), `bandwidth.py` (216) — plus `CHARTER.md`,
`DOCKSIDE-EXAM.md`, `VESSEL-SPECIALIZATION.md`, and `research/ROTATIONAL-ISA-ENCODING.md`.

**Verified green:**

```
$ pytest tests/ -q
141 passed in 0.36s
EXIT=0
```

`tests/test_coverage_gaps.py` is a *separate* file whose docstring names the exact uncovered lines it
targets (`bandwidth:35`, `bandwidth:153-155`, `relay:416`, `tender_types:59-60`). That is what a
coverage-driven second pass looks like when someone actually did it.

**The idea, which is the reason to care.** The repo's central claim is an **asymmetry**, stated
plainly: *the cloud can approximate the edge through benchmarks and specs; the edge cannot approximate
the cloud — it lacks the context.* Cloud→Edge flow is therefore **curated, compressed, actionable**;
Edge→Cloud is **raw and complete**. That asymmetry is treated as a *design constraint*, not a
complaint.

The mechanism is the **liaison tender**: a specialist vessel that is *social* rather than a builder.
Four tender types — Research, Data, Context, Priority — each with a defined job (carry findings,
batch big data, carry fleet context, translate urgency: "cloud 'low priority' might be edge 'system on
fire'"). The four verbs are **filter, compress, translate, prioritize**.

**Why another agent should care.** Every agent in this fleet is trying to solve "how do I get context I
don't have to an agent that needs it." This repo is a compact, *tested* answer, and the "Priority
Tender" idea (urgency is not portable across realities) is a genuinely reusable abstraction. It also
models a concrete artifact: `bandwidth.py` implements a `BandwidthBudget` with overflow handling
(drop-vs-fit arbitration) — the kind of thing a relay needs when the edge has 8 GB of VRAM and the
cloud has none.

---

## 6. FINDING — `snapkit-zig`: 4.2 MB of compiled binaries committed, and `.gitignore` does not mention them

**Rank: #6.**

`git ls-files zig-out` → **4 tracked build artifacts**:

```
zig-out/include/snapkit-zig.h      2,855 B
zig-out/lib/libsnapkit.a     1,997,970 B
zig-out/lib/libsnapkit.so    2,235,544 B
zig-out/lib/snapkit.lib          9,272 B
```

**4.25 MB of compiled output in a repo whose actual source is 49,726 bytes across 8 files** — the
build output is **85x the source**. And it is committed for **three target platforms** (`.a` static,
`.so` shared, `.lib` MSVC), meaning the repo carries binaries nobody can rebuild consistently because
there is no toolchain pin.

```
$ cat .gitignore
*.log
.env
.DS_Store
```

**`zig-out/` is not listed** — and `git check-ignore -v zig-out/lib/libsnapkit.so` confirms it is not
ignored, because it is *tracked* (the ignore rule would be cosmetic even if present; the fix is
`git rm --cached`).

Zero tests, zero CI. **Zig is not installed in this sandbox, so I inspected and did not execute this
repo** — I am not claiming anything about whether it builds.

**Why another agent should care.** This is the "ranked by tree bytes" trap made concrete:
**`snapkit-zig` is the 4th-largest repo in the unseen pool by tree bytes (4.3 MB) and would rank in the
fleet's top 10 on a naive size sort — while containing 50 KB of real code.** A census that ranks by
size and stops there would have reported a 4.3 MB Zig project. It is 50 KB of Zig plus three
platforms' worth of stale binaries.

---

## 7. STATUS UPDATE on the previously-reported findings (verified, not re-derived)

| repo | 2026-10-01 status | **now (2026-10-23)** |
|---|---|---|
| `quilt-canary` | 52 `target/` artifacts, no `.gitignore`, zero tests | **unchanged** — 66 blobs, 52 `target/`, 0 test files, 0 workflows |
| `superinstance-api` | `.wrangler/` ignored but still tracked | **unchanged** — `.wrangler/cache/wrangler-account.json` still tracked (118 B) |
| `xruntime-conformance` | 3 hardcoded `/tmp` paths, missing driver, no CI | **unchanged** — 12 blobs, 0 workflows, 0 test files; the 23/23 claim lives only in `CONFORMANCE.md` |
| `quilt-i2i` | dup dirs, no canary, no CI | **unchanged** — `erlang/`, `forth/`, `prolog/` each duplicated under `quilt-i2i/` with byte-identical file sizes; 0 workflows |
| `quilt-gpu-lab` | committed `__pycache__` + 58 `.rlib`/`.rmeta` | **still true, and worse** — now **634 `target/` paths, 116 `.rlib`/`.rmeta`, 3 `__pycache__`** |
| `pie-minimax` | author self-corrected the ceiling | **still true** — 2 committed `__pycache__` files, 0 workflows |
| `moth-honest` | reseal-forgery gap | **still true** — 11 committed `__pycache__` files |
| `quality-gate-stream` | committed live API keys | **still true** — 20 committed `__pycache__` files |
| `quilt-verilog` | 24/24 RTL + 34/34 sim | **still true** — plus **316 `target/` paths** committed |
| `substrate-attest-rs` | **430/434 tracked files were build output** | **CLEANED UP** — now **5 blobs**: `Cargo.toml`, `Cargo.lock`, `README.md`, `src/lib.rs`, `.gitignore`. **The fleet fixed this one.** |
| `constraint-theory-core` | f64, not integers | **still true** — 96 blobs, 1 workflow, 3 test files |
| `quilt-ewitness` | 7/7, mutation → 4/7, no CI | **unchanged** — 13 blobs, 2 test files, 0 workflows |

**The `substrate-attest-rs` cleanup is the good news of this round.** It is the one case in the table
where a previously-reported committed-build-output defect was actually fixed. The fleet's authors are
listening.

---

## 8. Addendum — the `lau-*` family is **bigger and greener** than the October report said

The 2026-10-03 report recorded the lau cluster as "12 crates, 371 tests, 12/12 clippy". The family has
grown and the previously-unexamined members are real. Verified this round:

```
lau-database-theory     -> cargo test:  81 passed; 0 failed; 0 ignored   (exit 0)
lau-bridge-pattern-math -> cargo test: 127 passed; 0 failed; 0 ignored   (exit 0)
```

And the implementations are genuinely topical, not renamed templates — `btree.rs` has
`search`/`insert`/`range_query`; `euler.rs` has `init_sod_shock_tube`/`stable_dt`/`total_energy`;
`topology_homology.rs` has `betti_numbers`/`euler_characteristic`/`is_boundary_cycle`. **The cluster is
the fleet's best-engineered surface and it is still growing.** But per Finding 2, roughly half of it
is name-variants of the other half.

**Also noted but not executed** (no toolchain in this sandbox): `flux-julia` (91 KB of Julia, a
multiple-dispatch algebraic-music-theory spike — 0 test files, 0 CI), `topology-lab` (94 KB Rust,
1 CI workflow, **0 test files** despite shipping `betti_curve.rs` and `hexagram_view.rs`),
`deckboss-app` (an honestly-archived Expo starter — its `STATUS.md` says *"We never pushed this past
the starter-template-plus-screenshots phase"*, which is a **truthful README about a dead repo** and
worth having on the record as a contrast to the defects above), and `Murmur` (100 KB TypeScript,
**34/34 vitest tests pass**, exit 0 — but its `experiments/critical-mass/` output is committed raw
JSON and deserves a dedicated look next round).

---

## 9. What I would do next, in order

1. **Fix `quilt-pydantic-ai` — one line.** Add `where = ["src"]` to `[tool.setuptools.packages.find]`
   in `pyproject.toml`, rebuild, and confirm the wheel contains 7 modules. Then add a CI workflow whose
   only step is `pip wheel` + `python -c "import quilt_pydantic_ai"`. **A gate that builds the artifact
   and imports it would have caught the empty wheel and the stale badge in the same run.** It is also
   the last port in the polyformalism ordering, so it is the one that most needs to work.
2. **Pick a canonical name for every lau/bare twin pair and delete or redirect the other.** The
   `evo-rs` case is urgent because both names are *already on crates.io* with real download counts;
   `cargo add` gets the same code under two identities. Add a CI step that diffs a twin's `src` tree
   SHA against its partner and fails if they diverge — **that single check makes twin divergence
   impossible rather than merely unlikely.**
3. **Chase the `tminus-dispatcher` lead.** A tested, documented, 196-green T-Minus implementation
   (`slackwater-tminus`) exists while `plato-portal`'s CI fails on a different `tminus-*` package with
   `exports nothing`. Either the pipeline is wired to the wrong package, or `slackwater-tminus` is the
   fixed successor nobody pointed it at. **This is a possible hours-long fix to a red pipeline, and it
   is the highest-value single lead in this report.**
4. **Adopt `edge-research-relay`'s Priority Tender as a fleet primitive.** Urgency is not portable
   across realities, and the repo has 141 passing tests to build on.
5. **Run the same `find_packages(where=...)` probe across every Python repo in the fleet.** The
   `si-conductor` defect (`['tests']`) is a one-line check, and if it fires once it will fire on more
   than one repo.

---

### What I could not do this round, stated plainly

- **`pydantic` v2 could not be resolved into a working pair** (PyPI unreachable; `pydantic-core`
  2.41.5 built fine from source, but `pydantic` 2.50 pins core 2.50.0 — no reachable tag — and needs
  `typing_inspection`, which is PyPI-only with no GitHub mirror). **The 41 tests in
  `quilt-pydantic-ai` were therefore never executed.** The packaging and badge defects are measured
  facts; the suite's pass status is unverified and I do not claim otherwise.
- **`tmux` was installed mid-round** to clear 3 environmental failures in `slackwater-orchestrator`
  (136/136 after). Those 3 were a missing binary, not a repo defect — recorded as such.
- **`flux-julia` and `snapkit-zig` were not executed** — no Julia, no Zig in this sandbox. Both are
  reported by inspection only.
- **`crates.io` API responses show `owners: []`** for SuperInstance's own crates, so I could not
  attribute ownership beyond the `repository` URL; that URL was sufficient for the `evo-rs` finding and
  is what I relied on.
