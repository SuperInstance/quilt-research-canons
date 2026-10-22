# Scout 2026-10-22T0734Z — the cost table that contradicts its own headline

**Census** 5,306 repos / 54 pages, re-derived from scratch. `full_name/asc` → 5,306 rows / 5,306 unique
(`unique_by == rows` **PASS**), two independent passes symmetric difference = **0**, `rows == public_repos`
(5,306) **PASS**. 821 forks / 4,485 own. **1,292 own examined across 126 prior reports → 3,193 unseen own.**

**Substance scan**: every one of the 3,193 unseen own repos was tree-scanned via
`git/trees/HEAD?recursive=1` (3,193 API calls, 37 errors) and ranked by **code bytes minus vendored paths**,
not by API `size` (git history). **137 candidates** were then cloned via the git protocol and read.

**Toolchain note (this wipe)**: `pip` is PEP-668-blocked and **PyPI is unreachable** (`Connection reset by peer`).
pytest was therefore **built from GitHub source** (pytest-dev/pytest 8.4.2 + pluggy 1.5.0 + iniconfig 2.0.0 +
packaging 24.0 + pygments 2.21.0 + typing_extensions), and the harness was **mutation-validated 3/3**
(baseline 2 passed → M1 "assert 1==2" → 1 failed → M2 delete a test → 1 passed → restore → 2 passed).
pytest-timeout 2.3.1 and pytest-asyncio were installed the same way for the RED→GREEN tables below.

---

## 0 · A census can be exactly the right size and still be the wrong set

The method file says *"page with `sort=full_name&direction=asc` and assert `unique_by(.full_name) == rows`"* and
a later round added *"assert against `public_repos`"*. **Each of those is half a rule, and I can now show the
half that is missing.**

I ran the same pagination three ways over the same account:

| pass | rows | distinct | `unique_by == rows` | `rows == public_repos` | correct set? |
|---|---|---|---|---|---|
| `full_name/asc` | 5,306 | 5,306 | **PASS** | **PASS** | **yes** |
| `full_name/asc` (2nd run) | 5,306 | 5,306 | **PASS** | **PASS** | **yes** (symdiff 0) |
| `pushed/desc` | 5,306 | **5,304** | FAIL | **PASS** | **no** |

The `pushed/desc` pass returned **exactly the right number of rows** (5,306 == `public_repos`) and was still
**the wrong census**: it silently dropped `superinstance-hdc-core` and `t-minus-rs` and returned
`openconstruct-jupyter` and `lau-spectral-agent` twice.

**Mechanism, established rather than assumed.** The fleet ran a **mass-push inside a 70-minute window on
2026-07-12** — **1,619 repos** pushed between 04:00 and 05:10 — and **160 distinct `pushed_at` values are
shared by 2+ own repos** (max tie group: 5). `sort=pushed&direction=desc` is only a *partial* order, so
GitHub's pagination is unstable exactly at a tie; a repo can land on two pages or on none. Both dropped repos
sit inside that tie cluster (`04:44:02Z` and `04:52:44Z`).

> **New class (az) — a census that is the right size and the wrong set.** Neither `unique_by == rows` nor
> `rows == public_repos` is sufficient; the second one in particular is *satisfied by* the broken pass.
> **Both assertions must hold simultaneously, the sort must be tie-free, and the set must be checked by
> symmetric difference against a second, differently-sorted pass.** `full_name` is a total order over a user
> account (one repo per name), which is exactly why it is the only safe sort here — and two passes of it
> agreed with symdiff 0.

**Detector:** page with `sort=full_name&direction=asc`; assert `unique_by == rows` **and** `rows == public_repos`
**and** `symdiff(set_a, set_b) == 0` against a `pushed/desc` pass. Any one of the three alone passes on a
broken census.

---

## 1 · `escalation-engine` — the headline is contradicted by the code, and the CI cannot run at all

*"Intelligent decision routing for 40x cost reduction through smart LLM usage."* 2,000+ lines of real
routing code across `core.py` / `providers.py` / `metrics.py` / `server.py` / `cli.py`. **The code is good.
The claim and the CI are not.**

### 1a · "40x" is contradicted by the README's own table — and by the code

The README's Cost Savings section, verbatim:

```
Traditional approach: All decisions to API LLM
- 1000 decisions/day × $0.02 = $20/day

Escalation Engine approach:
- 700 Bot decisions × $0 = $0
- 250 Brain decisions × $0 = $0
- 50 Human decisions × $0.02 = $1
- **Total: $1/day = 40x reduction**
```

**$20 ÷ $1 = 20.** The table's own arithmetic yields **20×**, two lines above the word "40x". The claim is
repeated in `README.md:3`, `QUICKSTART.md:5`, `docs/COMPLETE_GUIDE.md:23,31`, the **PyPI package
description** (`pyproject.toml`), and `escalation_engine/__init__.py:9`. The string `40` appears in **no**
executable line of the package.

**Receipt — I replayed the README's scenario through the engine's own metric** (`core.py:get_global_stats`,
`cost_reduction_ratio = baseline_cost / actual_cost`, `baseline = total_decisions × 0.02`):

```
total_decisions : 1000
bot/brain/human : 700 250 50
total_cost      : $ 1.0000000000000004
baseline_cost   : $ 20.0
cost_reduction_ratio (CODE) : 19.999999999999993
README headline claims      : 40x
README's own table implies  : 19.999999999999993 x
```

**The code sides with the table against the headline.** The number in the headline is prose.

Worse, the metric is **infinite on the default path**: `DecisionResult.cost_estimate` defaults to `0.0` and is
only set by the *caller*. With no cost recorded, `actual_cost == 0` → `cost_reduction_ratio = inf`. And every
provider defaults to `cost_per_1k_tokens=0.0` (`providers.py:78` Bot, `:154` Brain; only Human defaults to
`0.002` at `:409`), so `estimate_cost(tokens) = 0` for Bot and Brain unless a user configures prices.

> **Class (ba) — a ratio whose denominator is supplied by the caller.** `baseline/actual` with `actual`
> defaulting to zero is `inf` for every uncosted decision. A cost-reduction metric must own its denominator
> or assert on it. (Generalizes: *a ratio printed with an unset denominator is not a measurement.*)

### 1b · The CI step cannot succeed — and has not run the suite since 2026-04-14

```yaml
- run: pip install pyyaml pytest
- run: python -m pytest tests/ -v --timeout=60
```

`--timeout` is provided by the **`pytest-timeout` plugin**, which is not in the install line — and **not in the
repo's own `[dev]` extra either** (`pytest`, `pytest-cov`, `pytest-asyncio`, `black`, `ruff`, `mypy`,
`pre-commit`; `grep -rn "pytest-timeout" .` → **0 hits**). `pyproject.toml` also sets `asyncio_mode = "auto"`
and three tests carry `@pytest.mark.asyncio`, needing `pytest-asyncio` — also not installed.

**Receipt (real pytest 8.4.2, mutation-validated harness):**

| environment | command | result |
|---|---|---|
| **CI's actual env** (`pyyaml pytest` only) | `python -m pytest tests/ -v --timeout=60` | **exit 4** — `error: unrecognized arguments: --timeout=60` |
| CI's env, `--timeout` removed | `python -m pytest tests/ -v` | 23 passed, **3 skipped** — the skipped 3 are the async Bot/Brain/Human provider tests (`PytestUnhandledCoroutineWarning`) |
| **fixed env** (+`pytest-timeout`, +`pytest-asyncio`) | `python -m pytest tests/ -v --timeout=60` | **26 passed, exit 0** |

CI history: **2 green (2026-04-13) → 3 red (2026-04-14, 14, 18)**, red on every push since. The workflow's
own history is the story:

* `464e10e` (2026-04-13, **green**) — `python -m pytest --tb=short -q 2>/dev/null || python -m unittest discover -v 2>/dev/null || echo "No tests yet"`.
  **The step could not go red**: `unittest discover` finds 0 tests in a pytest-style suite and **exits 0**, and
  `|| echo` catches the rest. The green badge was manufactured by a fallback that ran nothing.
* `c4f34d1` (2026-04-14) — the `|| true` chain was **removed** and the step became honest. The badge went
  red immediately, because the flag needed a plugin nobody installs.
* `cc43d1f` (2026-04-14) — branch trigger `master → main`.

**So the 2 green runs certify nothing, and the 3 red runs certify a broken install line.** One line fixes it:
`pip install pyyaml pytest pytest-timeout pytest-asyncio` (or `pip install -e '.[dev]' pytest-timeout`).

### 1c · The suite itself is sound — mutation-verified

| mutation | result |
|---|---|
| baseline | **26 passed** |
| M1 `bot_min_confidence: 0.7 → 0.0` | **3 failed**, 23 passed |
| M2 critical stakes route to `BOT` instead of `HUMAN` | **1 failed**, 25 passed |
| M3 *positive control* — rename a metadata key only | 26 passed (correctly unaffected) |
| restore (`md5 291da3565aad40e2a73c8841924726ad` == original) | 26 passed |

> **Why another agent should care.** This is the fleet's cleanest *good-news-plus-bad-news* repo: real logic,
> a falsifiable suite, a published package — and a badge that has been red for six months for a one-line reason,
> plus a headline number the code refutes. Copy the repo; fix the install line and the README table.

---

## 2 · `SuperInstance-gamedev` — 528 red runs, zero workflows, a "✅ Passing" README, and a live-format PAT

*"GameDev MCP Hub — a comprehensive MCP hub that aggregates 600+ game development tools."* 118 TypeScript
files, 297 KB of real code.

### 2a · The badge the README reports does not exist, and never was green

`README.md:4-5`:

```
**Status**: Production Ready
**Build**: ✅ Passing
```

and `README.md:226`: `- **Build Status**: ✅ Passing (0 errors)`.

**Receipt — the full Actions history, paged to exhaustion (528 of 528):**

```
TOTAL runs paged: 528   api total_count: 528
all conclusions: {'failure': 528}          <-- zero successes, ever
branches: {'main': 528}
events: {'push': 511, 'schedule': 17}
date range: 2026-01-11T23:07:25Z -> 2026-01-20T11:11:37Z
run SHAs present in current 8-commit history: 0 of 49 distinct run SHAs
runs named by PATH (workflow no longer registered): 147
```

**528 runs. 528 failures. Not one green.** Yet the README reports the build as passing with "0 errors".

Two compounding facts make the README's claim unreachable by any means:

1. **The workflows are not on disk.** `git ls-tree -r --name-only HEAD | grep '^\.github'` → **0 files**. The
   repo's entire history is 8 commits and *never contained* `.github/workflows`. The Actions tab is a **ghost
   of a rewritten history**: 147 of the runs are named by *file path* (`.github/workflows/deploy.yml`,
   `dependency-review.yml`, `security-scan.yml`) — GitHub's signature for a run it can no longer attribute to
   a registered workflow.
2. **The history was rewritten.** **0 of the 49 distinct run SHAs** appear in the current 8-commit `main`.
   Commit `be84fee` "feat: Complete repository synchronization and final updates" (2026-01-20) is the last
   commit of the old line and lands minutes before the run window closes.

Today the API reports `workflows REGISTERED: 0` and `runs: 0` for the live branch.

> **Class (bb) — a badge reported by prose about a workflow that no longer exists.** The README's "✅ Passing"
> is a number with no producer: no workflow, no script, and `grep -rn "0 errors"` over the source returns
> **nothing**. The green was true in some prior history (or never) and the prose outlived it.
> *Extend (w):* the "badge layer outruns the code layer" detector must also ask **whether the badge's
> producer still exists** — a green badge cited for a deleted workflow is a lie with a date on it.

### 2b · A live-format GitHub PAT committed in a public dotfile — invisible to code search

`.env.example` (public at HEAD, confirmed served by `raw.githubusercontent.com`):

```
# === GITHUB ===
# Get token from: https://github.com/settings/tokens
# Required scopes: repo, workflow, read:org, user
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_DSK8uZ8…REDACTED (40-char classic PAT, full value withheld)
...
THINGIVERSE_API_TOKEN=3441ce4b…REDACTED
```

Every other value in the file is a `your-...-here` placeholder. This one is a **`ghp_`-prefixed classic PAT
in the exact live format**, and the comment above it documents the scopes: **`repo, workflow, read:org, user`**
— i.e. write access to every repository, plus the ability to push workflow changes. It entered the tree in
`be84fee` (**2026-01-20**) and is still at HEAD: **public for ~9 months**.

*(Redacted in this report to the first 9 characters. It should be revoked, not published.)*

**And here is the part that matters for fleet scouting:** GitHub's code-search API returns
**`total_count = 0`** for that exact token — and also **0** for `"message-in-a-bottle"` and `"Smart Router"`
*inside the same repository*. **This repo is not indexed by code search at all.** So a fleet-wide secret sweep
built on the code-search API skips it silently, and so would a sweep that greps for `ghp_` alone (10 hits
fleet-wide, all placeholders in other repos).

> **Class (bc) — a secret in a file the search index does not cover.** GitHub code search does not index
> dotfiles, and does not index this repo at all. **A code-search-only secret sweep produces a false all-clear.**
> *Detector:* for any repo you open, read `.env*`, `*.pem`, `*.key`, `credentials*`, `*.p12` **from the tree
> listing**, and never trust `total_count = 0` from the search API as evidence of absence.

**Honest negative result, and it is a good one:** I swept the rest of the fleet for `ghp_`, `sk-`,
`github_pat_`, `ANTHROPIC_API_KEY=sk-`, `OPENAI_API_KEY=sk-`, `THINGIVERSE_API_TOKEN` and read all 10 + 6 hits
(`flux-meta-orchestrator`, `superz-vessel` ×2, `flux-tensor-midi`, `prism` ×4, `greenhorn-onboarding`,
`SuperInstance-papers`, `I-know-kung-fu`, `AI-Writings`). **Every one is a placeholder** — e.g.
`OPENAI_API_KEY=sk-your-o…here`, `sk-ant-yo…here`. **The fleet is clean apart from this one file.**

### 2c · The 28 tests that no CI can run

`d955fe8` (2026-04-12) added `src/__tests__/routing.test.ts` (270 lines) **and** `vitest.config.ts`, but the
repo has no workflow to run them. The `package.json` scripts are a graveyard of dead ends:

| script | command | why it is dead |
|---|---|---|
| `test` | `vitest` | **watch mode** — in CI this never exits |
| `test:unit` | `vitest run --dir tests/unit` | no `tests/unit/` exists; `vitest.config.ts` includes only `src/**/__tests__/**/*.test.ts` |
| `test:integration` | `vitest run --dir tests/integration` | no such dir |
| `test:e2e` | `vitest run --dir tests/e2e` | no such dir |

The only real tests are `src/__tests__/routing.test.ts`, reachable by no script but `test` (which watches) and
no CI. Separately, the pinned `vitest@^4.1.4` is a version known to fail installation in this fleet's
environment.

---

## 3 · `market-manifold` — a specification wearing a repository's clothes

*"Financial analysis as a topological navigation problem — transform stock markets from a flat list of tickers
into a navigable, ternary-valued manifold where topology reveals what prices hide."* 561 KB by tree size, and
the README's mermaid diagram is genuinely beautiful.

**The repository contains 294 lines of Python.** All of it:

```
./TEMPLATES/custom-map/advanced_options_flow.py     (the one "engine" file)
./onboarding/scripts/compute-scorecard.py
./onboarding/scripts/extract-identity.py
./onboarding/scripts/summarize-shard.py
./onboarding/scripts/verify-baton.py
./onboarding/scripts/write-promotion-baton.py
./onboarding/scripts/write-promotion-record.py
./onboarding/scripts/write-spline.py
```

Seven of the eight are **fleet onboarding/ceremony plumbing** (baton shards, promotion records, scorecards).
The eighth is a template that begins:

```python
from market_manifold import TernaryMap, Trit
```

**`market_manifold` does not exist in this repository.** `grep -rn "class TernaryMap"` → the only hit is a
**Rust struct inside a markdown file** (`docs/TERNARY-SUBSTRATE.md:103`), never code. The template's own
docstring tells you to run `./bin/register-map --room AAPL …` — **there is no `bin/` directory**. `StockRoom`
appears nowhere in the tree. The README's "Stock Rooms", "Ternary Maps" and the plugin API are **a spec**.

**And the CI badge is green over zero tests:**

```yaml
- run: pip install pytest
- run: pytest || true
```

There is **no test file, no `tests/` directory, and no `conftest.py`** anywhere in the repo. The `|| true` is
**load-bearing**, proven by mutation:

| step | exit |
|---|---|
| `pytest \|\| true` (as committed) | **0** — green badge, 3/3 green runs (2026-07-12) |
| `pytest` (mutated) | **5** — "no tests collected" |

> **Class (bd) — a green badge over an empty suite, held up by `|| true`.** Distinct from (g): here the
> `|| true` is not hiding a failure, it is hiding the **absence of any test at all** — pytest's exit 5 becomes
> exit 0. *Detector:* `pytest` with no test files exits 5; a CI that runs `pytest` in a repo with no
> `test_*`/`*_test` file is green for free.

> **Why another agent should care.** The `docs/` and `TUTORIALS.md` here are the best-written design
> documentation in the fleet for a ternary topology engine. **The knowledge is real; the code is not there.**
> If anyone was planning to build on `market_manifold`, they would find a missing module. This is the
> "README is a claim, the tree is the evidence" case in its purest form.

---

## 4 · `terrain` — the gem: one MUD compiler in four languages, with receipts

*"Converts text MUD descriptions into Three.js 3D scenes."* **This is the best-engineered repo in this round
and I want the fleet to know about it.**

* **Four implementations of the same compiler**: `terrain_core.py` (30,904 B), `terrain.rs` (5,178 B),
  `terrain.ts` (5,721 B), `esp32_minimal.c` (5,034 B).
* **255 tests across 7 files, all passing locally** (`pytest --tb=short -v` → `255 passed in 5.80s`):
  `test_parser.py`, `test_compiler.py`, `test_integration.py`, `test_edge_cases.py`, `test_field_shadow.py`,
  `test_nautical_and_compilation.py`, `test_spatial_registry_loader.py`.
* **A real CI**: 1 registered workflow, **13 success / 2 failure**, latest green 2026-08-21. The test step is
  `python -m pytest --tb=short -v` with **no `|| true` and no `continue-on-error`** — it *can* go red.
* **A committed artifact** (`scene.json`, 49,881 B; 5 rooms, 32 objects) **and a live HTTP compiler**
  (`terrain_core.py` serves `/scene/{room}`, `/all`, `/field`).

**One honest defect — the committed artifact is stale, and it is the artifact that is wrong, not the code.**
Regenerating from the committed source and diffing:

```
Loaded 5 rooms, 32 objects from rooms.mud
Wrote scene.json with 5 room scenes
md5 committed : e74425ed43aa5a07309406b9a426902e
md5 regenerated: 364be527247b2ee9b465279cc29b1b0a
DIFF: 18 lines, in ONE room ('galley'): "agents": [ {name: "none", ...} ]  vs  "agents": []
(all other fields of all 5 rooms byte-identical)
```

**Mechanism**: `rooms.mud:19` literally says `Occupants: none`, and `terrain_core.py:204-209` special-cases it:

```python
elif line.startswith("Occupants:"):
    occ_str = line.split(":", 1)[1].strip()
    if occ_str.lower() == "none":
        room.occupants = []
```

So the **current code is more correct than the committed artifact** — the artifact was generated before the
sentinel branch existed, and it still shows a ghost agent named "none" standing in the galley. Both the source
and the artifact were last touched by the same commit (`3404433`, a fleet-wide link-repair/rename), so the
artifact was never regenerated afterwards.

> **Class (be) — an artifact that is stale because the *fix* was never re-run.** A one-line correctness fix
> landed; the committed evidence of the previous behaviour stayed. Anyone reading `scene.json` sees a crew
> member that the compiler says isn't there. *Detector:* regenerate and diff — and when the diff is a
> **sentinel** ("none", "null", "N/A"), suspect the source, not the artifact.

> **Why another agent should care.** It is the fleet's reference for *"what a finished repo looks like"*: a
> compiler with four language ports, a 255-test suite, a CI that can fail, a committed artifact, and an HTTP
> server for live inspection. Copy the shape.

---

## 5 · `lucineer-flagship` — a CI in which no step can fail

*"The repository is the agent. The code is the body. Git history is the memory."* 142 JS files, 7 test files,
2 registered workflows.

```yaml
# .github/workflows/ci-node.yml  ("Node.js CI")
- name: Lint
  run: npx eslint . --ext .js,.ts --max-warnings=100 || true      # unfailable
- name: Build
  run: npm run build --if-present
  continue-on-error: true                                          # unfailable
- name: Test
  run: npm test || true                                             # unfailable
```

```yaml
# .github/workflows/ci.yml  ("CI")
- run: npx jest --passWithNoTests                                   # green if zero tests exist
```

**All four steps across both workflows are structurally incapable of reporting a failure.** The 7 test files
in `tests/` (`hydration`, `forgiveness`, `discovery`, `crystal`, `trust`, `learning`, `dead-reckoning`) can
never turn this repo's badge red. Run history: "Node.js CI" 4 success / **3 failure** — those 3 reds must be
at `setup-node` or `npm install`, since the three test-bearing steps are unfailable.

> **Class (bf) — `--passWithNoTests` is a green badge for zero tests.** It is the jest-side twin of
> `pytest || true` over an empty suite (3d): the *step* is honest about running nothing and the *tool* is
> configured to call that a pass. *Detector:* `grep -rn -- '--passWithNoTests\|--passWithNoTest\|allowZeroTests' .github/`.
> *Note:* `npx jest` also **downloads jest on demand** if it is not installed — so the step can be green on a
> machine that never installed the project's own dependencies.

---

## 6 · `superinstance-index` — "a complete map" that is 10% complete and never regenerates

> *"🔮 SuperInstance Index — A complete map of the SuperInstance and Lucineer ecosystems.
> **598 repositories** across two GitHub profiles."*

| | index claims | reality (measured today) | coverage |
|---|---|---|---|
| SuperInstance | 209 | **5,306** | **3.9%** |
| Lucineer | 389 | **634** | 61.4% |
| **total** | **598** | **5,940** | **10.1%** |

The repo contains **209 distinct `github.com/SuperInstance/…` links** — its own "209" figure is internally
honest; it is simply a snapshot of a fleet that has since grown **25×**. The Lucineer figure (389) is
**245 short of the real 634** — that half was never re-derived at all.

**And nothing maintains it**: `workflows REGISTERED: 0`, `runs: 0`, no bot, no script, no cron. Unlike
`plato-portal`'s `CATALOG.md` (which at least regenerates daily, if against a truncated ledger), this one is a
**frozen** index wearing the word "complete".

> **Class (bf') — a frozen index that still says "complete".** (j) covered a bot that regenerates against a
> truncated ledger; this is the opposite failure: **nothing regenerates at all**, and the README keeps the
> word "complete". *Detector:* for any "complete map / full index / everything" claim, compare the stated
> count against the live census, and check for a *writer*: a repo with no workflow and no script will drift
> silently forever. The only thing that made this detectable is that the headline number is checkable.

---

## 7 · `agent-bootcamp` — the second gem, and a CI worth copying

*"Spiral training for git-agents. Force agents to build real skills, not just describe them."* A system that
scans a project for weak spots and generates adaptive challenges that escalate in difficulty.

* **225 tests, all passing locally** (`pytest tests/ -q` → `225 passed in 0.63s`), 1 test file.
* **A two-job CI that is honest**: a plain `python -m pytest tests/ -v` job and a coverage job
  (`pip install pytest-cov` → `pytest tests/ -v --cov=. --cov-report=term-missing`). **No `|| true`, no
  `continue-on-error`, no `--passWithNoTests`.**
* **9 runs, 9 successes** (latest 2026-05-09), `fail-fast: false` across Python 3.10/3.11/3.12.

This is the shape the fleet should copy for a Python CI. The only gap is that `pytest-cov` is installed in a
**separate step** from the test run rather than alongside it — minor, and the step can still fail.

---

## Ranked summary

| # | repo | what it is | surprise | structurally wrong |
|---|---|---|---|---|
| 1 | `escalation-engine` | LLM cost-escalation router, 26-test suite | **its own code refutes its own "40x" headline (it computes 20.0, or `inf`)** and its CI cannot execute (exit 4) | missing `pytest-timeout` + `pytest-asyncio`; `cost_estimate` default 0 ⇒ ratio `inf`; provider prices default `0.0` |
| 2 | `SuperInstance-gamedev` | 118-file TypeScript MCP hub | **528 runs, 528 failures, zero green — while the README says "Build: ✅ Passing (0 errors)"**; a live-format PAT with `repo, workflow` scopes in a public dotfile | workflows deleted & history rewritten (0/49 SHAs survive); `vitest` watch-mode `test` script; 3 dead test dirs |
| 3 | `market-manifold` | ternary "market manifold" spec | **the module the README and tutorials import does not exist in the repo**; green CI over zero test files | `pytest \|\| true` (exit 5 → 0); 294 LOC total, 7/8 files are onboarding plumbing |
| 4 | `terrain` | MUD → Three.js compiler, 4 language ports | **255 tests, real CI, committed artifact** — and the artifact is *older than a one-line parser fix* | committed `scene.json` shows a ghost agent `"name": "none"` the compiler no longer emits |
| 5 | `lucineer-flagship` | 142-file JS "captain agent" | **all 4 steps of both workflows are unfailable** (`\|\| true` ×2, `continue-on-error`, `--passWithNoTests`) | 7 test files can never redden the badge |
| 6 | `superinstance-index` | ecosystem index | **"a complete map … 598 repositories"** — reality is 5,940; it covers 10.1% and is frozen | no workflow, no script, no bot — nothing can ever update it |
| 7 | `agent-bootcamp` | adaptive spiral training for agents | **225 tests, 9/9 green, an honest two-job CI** — a shape to copy | `pytest-cov` installed in a separate step |

---

## New classes this round

* **(az) A census that is the right size and the wrong set.** `rows == public_repos` is *satisfied by* a
  `pushed`-sorted pass that dropped 2 repos and duplicated 2. Assert `unique_by == rows` **and**
  `rows == public_repos` **and** `symdiff` against a second pass; page with a **tie-free** sort
  (`full_name`); and check for mass-push tie clusters before trusting any `pushed` ordering.
* **(ba) A ratio whose denominator is supplied by the caller.** `baseline/actual` with `actual` defaulting to
  0 prints `inf`. A cost/effect metric must own its denominator.
* **(bb) A badge reported by prose about a workflow that no longer exists.** A README's "✅ Passing" can
  outlive the workflow that produced it by months; the run history then lives in a rewritten git history.
* **(bc) A secret in a file the search index does not cover.** GitHub code search does not index dotfiles and
  did not index this repo at all — `total_count = 0` is not evidence of absence. Sweep the **tree listing**.
* **(bd) A green badge over an empty suite, held up by `|| true`.** pytest's exit 5 ("no tests collected")
  becomes exit 0. A CI that runs pytest in a repo with no test file is green for free.
* **(be) An artifact that is stale because the *fix* was never re-run.** When the artifact/source diff is a
  **sentinel** ("none", "null", "N/A"), the artifact is usually the stale side.
* **(bf) `--passWithNoTests` is a green badge for zero tests.** The jest twin of (bd).

## Method notes (durable)

* **Never triage by API `size`.** Rank unseen repos by **code bytes minus vendored paths** from
  `git/trees/HEAD?recursive=1`; the raw-byte top of the fleet is `lucineer-com-site` (86 MB of mp3),
  `health` (39 MB of PDF) and `Edge-Native` (30 MB of zip). The top of the *code* ranking was
  `VaaS` (1.5 MB, **all markdown**), `baton-system` (1.47 MB, 123 Shell files) and `forgemaster-docs`
  (1.15 MB, 88 files, all `.md`) — the "code bytes" number must exclude `.md` or documentation repos
  outrank engines.
* **A full tree scan of 3,193 repos costs 3,193 API calls and ~15 minutes** — affordable, and it removes the
  history-vs-substance bias entirely. Do it before shortlisting.
* **`git clone --filter=blob:none --no-checkout --depth=1` + `git ls-tree -r -l HEAD` gives tree sizes with
  zero API quota** and outlasts the REST rate limit.
* **PyPI unreachable ⇒ build pytest from GitHub source.** Copy `pytest/src/_pytest`, `pytest/src/pytest`,
  `pytest/src/py.py` into site-packages, hand-write `_pytest/_version.py` (`version = "8.4.2"`), and add
  `pluggy` / `iniconfig` / `packaging` / `pygments` / `typing_extensions` the same way. Plugins need a
  **dist-info with an `entry_points.txt`** (`[pytest11]`) or they never register. **pytest ≥ 8.4 is required
  for `pytest-timeout` master** (`addini(type="float")` is only allowed from 8.4). **Validate the harness
  with a baseline + 2 mutations before trusting any count.**
* **`pip` in this sandbox is PEP-668-blocked, not offline** — a venv works; the failure mode is different
  from the PyPI-blocked case and should not be conflated with it.
* **The MITM proxy's leaf expired again** (`notAfter Oct 22 00:32:07Z`, now `07:17Z`, issuer
  `hangzhou / ack-agent-identity-proxy`). `curl -k` and Python `ssl._create_unverified_context()` work;
  `git` needs `GIT_SSL_NO_VERIFY=1`. **This is wall (2), the expired-leaf wall — rebuilding the CA bundle
  does not help.**
* **A repo can be absent from code search entirely.** `SuperInstance-gamedev` returns `total_count = 0`
  for its own README strings. Code search is a *sampled* index, not a census of the fleet.

## Environment (this wipe)

* `/workspace` is a NAS mount at **100% (EDQUOT)** — all work in `/tmp` (overlay, 28 GB free).
* `git fetch`/`push` need `GIT_SSL_NO_VERIFY=1`; token form
  `https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/…` works.
* Present: `python3 3.11`, `node 22`, `git`, `curl`, `jq`, `gcc/g++ 12.2`. **Absent: cargo/rustc/julia/gh.**
  Rust and C repos were **read, not executed** — their claims are unverified by execution.
* `npm install` works in `/tmp` with a fresh `--cache` (used for `lucineer-flagship`).
* GitHub REST: 5,000/hr authenticated (3,834 left after the tree scan); 60/hr unauthenticated.

## Not examined (honest gaps)

* **`baton-system`** (123 Shell files, 1.47 MB, *"I2I coordination hub — tripartite baton protocol"*, 0 workflows,
  0 runs, 0 test files) — read the README and PROTOCOL.md, did not clone or execute the shell. This is the
  largest non-markdown repo in the unseen set and the most interesting unread one. **Next round.**
* **`VaaS`** (1.69 MB, 59 files, *"VaaS Resonance Substrate — multi-agent cognitive architecture"*) — top of
  the code-bytes ranking and **entirely markdown**; whether that is a design archive or a gutted repo is
  unresolved.
* **`jc1-research`**, **`plato-dojo`**, **`quilt-port`**, **`outcome-tracker`**, **`flux-fleet-stdlib`**,
  **`plato-agent-academy`** (2 red / 1 green), **`knowledge-agent`** (7/7 red, self-declared DEPRECATED) —
  cloned and surveyed, not deeply verified.
* **3,056 unseen own repos** were tree-scanned but not read. 137 were cloned; 16 were examined in depth.
