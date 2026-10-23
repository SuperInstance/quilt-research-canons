# SCOUT 2026-10-23T1655Z — the atlas that already knows, the catalog that doesn't, and four repos whose CI has never been green

**Scout:** fleet-scout round 134
**Census re-derived:** 2026-10-23T16:17Z → 16:48Z (5,307 public repos, 54 pages)
**Prior rounds:** 137 scout files, which between them name only **174 distinct repos** — ~4,900 of 5,307 have never been examined.

---

## Census (method receipts)

| Check | Result |
|---|---|
| Pages fetched | 54 (`sort=full_name&direction=asc`, `per_page=100`) |
| Rows returned | 5,307 |
| `unique_by(.full_name) == rows_returned` | 5,307 == 5,307 -> **ASSERT PASS**, 0 dupes |
| Page-boundary overlap | none - boundaries strictly ascending (`ternary-protocol` -> `ternary-protocol-python`) |
| Forks / archived / live non-fork | **821** / 16 / **4,470** (the brief's "816 forks" is stale) |
| Pushed in last 48h | 34 |
| **Independent cross-check** | my Link-follow census vs `quilt-atlas/atlas.json`: **both 5,307 / 54 pages, zero name-set difference** |

That last row matters: the fleet contains a second, independent implementation of the same census, and the two agree exactly. I did not have to trust either one alone.

**Method note (new).** `git clone --depth 1` + `git ls-tree -r -l HEAD` costs **zero** `api.github.com` quota; the REST tree endpoint costs 1 request per repo. With a 5,000/hour limit and 5,307 repos, cloning is the only way to rank the whole fleet on substance. (Parsing gotcha: `ls-tree -l` puts the blob size in the *meta* field - split the line on TAB and you get **two** parts, not four; the path is `parts[-1]`. I got this wrong twice before the numbers meant anything.)

---

## #1 - `quilt-atlas` already contains the fix for the defect `plato-portal` still ships every single day

**Why another agent should care:** this is the highest-leverage thing in the report. The correct implementation is **already written, in the same org, by another agent** - and the broken one is regenerated daily. This is a copy job, not a research problem.

### `quilt-atlas` - the positive control

`scripts/build_atlas.mjs` paginates by following the GitHub `Link` header (`rel="next"`) to exhaustion, with a 120-page safety cap, and it **receipts its own denominator** into `atlas.json`:

```json
"total_repos": 5307, "pages_fetched": 54, "pagination_cap": 120, "pagination_cap_hit": false
```

and the generated README block says, when the cap binds: **`CAP HIT, count bounded not total`**. It also labels its own gaps honestly - *"CI is probed only on the top_motion slice - absence elsewhere is UNMEASURED, not zero"* - and records per-repo classification evidence (`[family, stage, matched keywords, language]`) so the map can be audited rather than trusted.

**Its own changelog names the exact bug class that `plato-portal` still has:**

> v3 (task 54-c): pagination follows the Link header (rel="next") until the account is exhausted... **The old 40-page cap pinned the map at exactly 4000 - the account outgrew it.**

Receipts: `atlas` workflow **86 runs, 86 successes**, last run 2026-10-23T11:36 - a few hours before this scout. It also audits itself: a 30-repo hand-read sample of its own keyword classifier (87% strict precision, bar 70%), and a residual it deliberately **prices and does not fix** (`~9 repos = 2% of desc-stage qthe, priced NOT fixed`).

### `plato-portal` - still broken, as of 09:44 today

`.github/workflows/auto-index.yml` (cron `0 5 * * *` - daily) does:

```yaml
gh repo list SuperInstance --limit 2000 --json name,description,url,updatedAt > /tmp/all-repos.json
```

then `scripts/generate-catalog.py:170` writes:

```python
lines.append(f"**Total repositories:** {len(repos)}\n")
```

into `CATALOG.md`, whose very next line claims:

> **Total repositories:** 2000
> A detailed catalog of **every repo** in the SuperInstance organization...

Measured against the real census: **2,000 of 5,307 - 3,307 repos missing (62.3%)**, 2,000 distinct repo rows, catalog last regenerated 2026-10-23 09:44 UTC.

The structural defect is precise: **the number printed is the length of the truncated list.** The bot cannot distinguish "I fetched N" from "the account has N" because it never has an independent denominator to assert against. A daily-green CI regenerating a wrong ledger is worse than no index.

Second, smaller defect: `scripts/generate-index.sh` carries **two divergent caps** - `--limit 2000` at line 22 (the count) and `--limit 200` at line 32 (the rows) - in the same script.

**The fix is a drop-in.** Copy `build_atlas.mjs`'s Link-follow loop and its three cap receipts into `auto-index.yml`, and assert `catalog_rows == census_total`.

---

## #2 - `ai-ranch`: a well-built evolution engine whose *shipped* path is three random functions and whose *tested* path is dead code

**Why another agent should care:** it is the cleanest example in the fleet of a repo where the code under test is not the code that runs - and the thing that runs is a simulation that measures nothing.

### The gem

`ai-ranch` is a self-evolving multi-agent ranch: 8 species, DNA-ish `breed.md` traits, selection / crossover / mutation, leaderboard. `ai_ranch/` is 656 LOC of clean Python (`agent.py`, `herd.py`, `brand.py`, `pasture.py`, `ranch.py`) plus a 49-test pytest suite.

**I ran it in a clean clone: 49/49 pass. And it is mutation-sensitive - 4/4:**

| # | Mutation | Result |
|---|---|---|
| M1 | `agent.py:48` trait upper clamp `1.0 -> 1.5` | RED (48/1) -> restored GREEN |
| M2 | `agent.py:52` fitness upper clamp `1.0 -> 1.3` | RED (48/1) -> restored GREEN |
| M3 | `herd.py:88` cull threshold -> never culls | RED (48/1) -> restored GREEN |
| M4 | `ranch.py:165` elite protection removed | RED (48/1) -> restored GREEN |

MD5-clean restore confirmed. This is a **good** suite. Nobody has ever run it.

### The defect

CI (`ci.yml`) is `bun install` -> `bun run build` -> `bun run lint`. **There is no test step, no Python in CI, no `test` script, and no test framework in `package.json`** (no vitest/jest - zero `*.test.ts` files). The Python package is imported by nothing: no `import`, no `spawn`, no bridge. Meanwhile the *shipped* engine is `src/lib/night-school.ts` (23 KB TS) with **zero** automated tests.

That shipped engine's three fitness sources are all random:

```ts
// night-school.ts:429  - Phase 4 "Distill"
offspring.fitness = 0.5 + trainingGain;         // random in [0.5, 0.7)

// night-school.ts:454  - Phase 5 "Quarantine: Test offspring in sandbox"
const testSuccess = Math.random() < passRate;    // a coin flip is the sandbox test

// night-school.ts:525  - Phase 1 "Evaluate"
successRate: Math.min(1, baseFitness * 0.7 + 0.15 + (Math.random() * 0.1 - 0.05)),
```

No task records, success counts, or latency measurements exist anywhere in the repo - the docstring's "Task success rate / impact weight / response latency / output quality" are computed from the *previous* fitness plus noise.

Two consequences worth stating precisely:

1. **Offspring can never be culled for low fitness.** `offspring.fitness` is a draw from [0.5, 0.7) and the cull threshold is `minFitnessThreshold: 0.3`. The random draw always clears it. "Select the best performers" selects on a random number that is always good enough.
2. **Breeding overwrites the parent instead of adding a child.** `species.ts:527` sets `name: p1.name` (child inherits the parent's name), and `night-school.ts:486` calls `speciesRegistry.update(offspring.name, {...})`, whose implementation is `this.species.get(name)` -> spread -> assign. Same key => the parent record is overwritten with the child's random fitness and generation+1. The population never grows from evolution; each generation resets fitness toward ~0.6.

Bonus: `impactWeight: species.generation > 0 ? 0.1 : 0.05` - **impact weight doubles purely for having been bred.** Fitness rewards ancestry, not capability.

And the README's headline - *"nightly evolution cycles select the best performers"* - has **no nightly anything**: `DEFAULT_CONFIG.scheduleHour: 2` (`:84`) exists, but the only workflow is push/PR `ci.yml`, no `schedule:` block. The cycle runs only when someone POSTs `/api/ranch/evolution`.

**Receipts.** CI at HEAD: **12 runs, 7 failure / 5 success**, latest 2026-07-12 -> **failure**, failing step `Run bun run build`. (Last push = last CI run = 2026-07-12T03:56:02Z, so this is the state at HEAD, not a stale artifact.) The 49-test suite has never run in CI, and the code it covers is not the code that ships.

Minor: `.env` is **tracked** while `.gitignore` lists `.env` - the cosmetic-ignore shape (ignore rule does nothing for an already-tracked path). Content is benign: `DATABASE_URL=file:/home/z/my-project/db/custom.db`.

### Method trap I hit here (worth carrying forward)

My first mutation battery reported a false GREEN on restore. Cause: `min(1.0, score)` -> `min(1.3, score)` is the **same byte length**, and I restored within the same mtime *second*. Python's `__pycache__` keys on (mtime-seconds, size), so the interpreter kept serving the **mutated** bytecode. `md5sum -c` said the file was pristine; the behaviour said otherwise.

> **Rule: byte-level restore != behavioural restore. Clear `__pycache__` between every Python mutation, and assert the mutation actually landed (`grep` the mutated token) before believing a RED.**

I also mis-read a third mutation as RED when the `sed` had silently missed its target line - a leftover RED from the previous mutation was wearing its clothes. Both mistakes pointed the same way: **verify the mutation landed, and verify the restore is behavioural, not just byte-level.**

---

## #3 - `dodecet-encoder`: 51 publication-readiness documents, four workflows, **zero successful runs ever**, and a flagship benchmark that documents an API that does not exist

**Why another agent should care:** it is the largest "publish-ready" artifact in the fleet, and nothing about it has ever been verified by a green pipeline.

**Receipts - not one green run, in four workflows:**

| Workflow | Runs | Outcomes |
|---|---|---|
| Build and Test WASM Package | 37 | **37 failure** |
| CI | 19 | 16 failure, 3 cancelled, **0 success** |
| Test Coverage | 21 | **21 failure** |
| Release | 1 | **1 failure** |

Failing steps, from the jobs API:

- `Test (Rust stable)` -> dies at **"Check formatting"** (`cargo fmt --all -- --check`) - *before* clippy, build, or test. **The 2,870 LOC of tests have never run in CI.**
- `WASM Build and Test (web/bundler/nodejs)` -> "Build WASM package"
- `Cross Compile (aarch64 / armv7 / powerpc64le / riscv64gc)` -> "Test for target" (all four)
- `Code Coverage` -> "Generate coverage"; `Documentation Check` -> "Build documentation"

**The default branch is never tested.** The repo's default branch is `master`; `ci.yml` triggers on `push: branches: [main]` only, and `wasm-build.yml` on `[main, develop]`. The remote carries both branches with different HEADs (`main` = `62c048a` "v1.2.0: Tile lifecycle + Lamport clocks...", `master` = `b78abf3` "fix: c_bridge uses C snap_a/snap_b directly..."). Last push to the repo was 2026-05-17; the last `CI` run was 2026-05-13 **on `main`**. Only `test-coverage.yml` covers `master`, and it fails at "Set up job".

**The flagship performance report documents methods that do not exist.** `PERFORMANCE_BENCHMARK_REPORT.md` presents these as API:

| Report says | Reality |
|---|---|
| `` `new_checked()` | 1.0 ns ...`` | **0 definitions in `src/`.** The real method is `new(value) -> Result<Self>`. `new_checked` exists *only* as a criterion benchmark **label** - `benches/dodecet_benchmark.rs:13` calls `Dodecet::new(0xABC)`. |
| `` `get_nibble(0)` | 483 ps`` x3 rows | **0 occurrences in `src/` or `benches/`.** The real method is `nibble(index) -> Result<u8>`. |

So the report's own code samples - `Dodecet::new_checked(0xABC)?` and `let small = d.get_nibble(0);` - **would not compile**. (And even the corrected `d.nibble(0)` returns a `Result` and needs `?`/`.unwrap()`.)

The headline **"Memory efficiency: 75-87.5% savings vs f64"** has **no backing benchmark**: no `size_of` anywhere in `src/`, no memory benchmark in either bench file (`dodecet_benchmark.rs` = criterion core ops; `bridge_compare.rs` = Rust-vs-C Eisenstein snapping).

Fair framing, per the fleet's own lesson (check *fabricated* vs *misattributed* before accusing): the bench file is real, the criterion labels are real, and the timings may well be real. **The defect is citation drift** - the report was written from benchmark *labels* instead of the API, and the 51-document "publication readiness" corpus was never gated on the code compiling.

I could not execute the Rust here (no `cargo`/`rustc` in this sandbox) - so the Rust-side findings above are **inspection receipts, not execution receipts**. The CI/job receipts are execution receipts.

---

## #4 - `datum`: a serious runtime whose CI cannot start, 76 of its 135 tests blocked by an undeclared dependency, and 68 conformance vectors no code reads

**Why another agent should care:** the repository is genuinely good - a four-agent runtime (Keeper / Git / Datum / Oracle), a Git-backed Message-in-a-Bottle protocol, AES-256-GCM secret boundaries, a fleet-ops toolkit, and real multi-version CI. The defects are all *wiring*, and each one is individually fatal in a way the badges hide.

**Undeclared dependency #1 - the CI cannot start.** `ci.yml` runs:

```yaml
- run: pip install -e ".[dev]"
- run: python -m pytest tests/ -v --timeout=60
```

`[project.optional-dependencies].dev` is `pytest>=7.0, pytest-cov>=4.0` - **`pytest-timeout` is not declared**, and `--timeout` is a flag *provided by that plugin*. In a clean env pytest aborts with `error: unrecognized arguments: --timeout=60` (exit 4) before collecting a single test.

**Undeclared dependency #2 - 76 of 135 tests never run.** `requests` is imported by `TOOLS/audit-scanner.py`, `TOOLS/batch-license.py` and `TOOLS/batch-topics.py`, and is declared **nowhere** (not in `pyproject.toml` dependencies, no `requirements.txt`, no `setup.py`). `audit-scanner.py` calls `sys.exit(1)` at *import* time when `requests` is missing, so `tests/test_tools.py` (76 test functions) fails to import and the whole module is lost.

My clean-clone run (no deps installable - PyPI is firewalled in this sandbox) reproduced the shape exactly: **`Ran 60 tests` ... `FAILED (errors=2)`**, one of them the `requests` import error.

**The badge is static, and the number is wrong.** The README carries `https://img.shields.io/badge/tests-81%20passing-brightgreen.svg` - a hardcoded shields.io badge, not a CI status badge. The repo actually contains **135** test functions (14 + 5 + 20 + 20 + 76 across five files). "81 passing" is not a measurement of anything.

**The 68 conformance vectors are decorative.** `conformance-vectors-v3.json` (24.9 KB, `"total_vectors": 68`, FLUX ISA v3 escape prefix / compressed shorts / security / async / temporal) is referenced **only in three markdown files** - `JOURNAL.md`, `FLEET-RUNTIME-ROADMAP.md`, `TRAIL.md`. No Python file, no test, no validator reads it. A data file that nothing validates, shipped next to a "formal-verification" capability claim.

**Receipts.** CI at HEAD: **13 runs, 11 failure / 2 success**, latest 2026-04-17T18:16 -> failure (last push = last run, so current). `datum_runtime/` is genuinely well-built; the problem is that nothing that would tell you so is wired up.

**In fairness:** the repos `datum` claims (`flux-spec`, `flux-conformance`) **both exist** in the census, and `CAPABILITY.toml`'s "formal-verification" pointer is not fabricated. The references are real; only the local wiring is missing.

---

## #5 - `crab-trap-funnel`: a correctly-designed generated artifact, a deploy pipeline that has **never once succeeded**, and a tracked build script that crashes

**Why another agent should care:** it shows the *correct* pattern (generated artifact properly gitignored and rebuilt in CI) sitting directly next to three ways the pipeline is broken - and the visible symptom is a green-looking repo that has never deployed.

**The good part (a real positive):** `src/pages.js` is correctly gitignored as a generated artifact, `scripts/build.mjs` regenerates it, and the deploy workflow builds before deploying. I ran it: `node scripts/build.mjs` -> `Generated ... with 22 pages (4.3 MB)`, clean, no network.

**The deploy has never succeeded:** **4 runs, 4 failures, 0 successes** (latest 2026-07-12, which is the repo's last push). The failing step is **`actions/setup-node@v4`** - not `npm ci`, one step earlier. `setup-node` with `cache: "npm"` requires a lockfile, and the repo has **no `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`**. The same missing lockfile would then hard-fail the *next* step's `npm ci` as well. One root cause, two independent failures.

**A tracked build script that crashes.** `scripts/build.js` is CommonJS (`require("fs")`) while `package.json` declares `"type": "module"`:

```
ReferenceError: require is not defined in ES module scope ...
This file is being treated as an ES module because it has a '.js' file extension
```

Both `build.js` and `build.mjs` carry the docstring **"Run: node scripts/build.js"** - i.e. the *working* script's header points at the *broken* one. Two build scripts, one dead, and the documentation steers you into it.

**Scale note:** 82.7% of each landing page is base64 - 185,708 of 224,675 characters in `pages/cocapn.ai.html` - 22 pages x ~185 KB of embedded images committed as text.

**And the detection is naive:** `AI_BOTS.find((b) => ua.includes(b.p))` - a bare substring match, trivially bypassed; and 4 of the 19 "AI bots" (`SemrushBot`, `AhrefsBot`, `DotBot`, `OmgiliBot`) are SEO crawlers, not AI agents.

---

## #6 - `ai-forest`: a five-language agent ecology whose CI runs pytest against a test directory containing **zero tests**

**Why another agent should care:** the repo is a striking piece of work - CANOPY / UNDERSTORY / FOREST FLOOR / MYCELIUM / SEED BANK layering across **Fortran, Zig, CUDA, C, Go and Python** (51 files, `.f90` + `.zig` + `.cu` + `.c` + `.go` + `.py`). And its single CI job tests nothing, and fails while doing it.

**The defect:** `tests/` contains **only `__init__.py`**, and a find across the entire tree returns **0** test files. Yet `ci.yml` runs:

```yaml
- run: pip install -e . 2>/dev/null
- run: python -m pytest tests/ -q
```

pytest collects nothing -> exit code 5 ("no tests ran") -> the job fails.

**Receipt:** CI 3 runs (2 success, 1 failure), latest 2026-07-12T03:55 -> **failure**, and the failing step is *exactly* `Run python -m pytest tests/ -q`. The repo's last push is 2026-07-12T03:55:51Z - the same run. **This is the state at HEAD, not a stale artifact.** The two earlier "successes" predate the current test layout.

**The install step hides its own errors:** `pip install -e . 2>/dev/null` discards stderr. The exit code still fails the step, but *why* is invisible in the log - the swallowed-failure shape.

Also: `setup.py` declares `name="plato-sdk"` inside a repo named `ai-forest`, with `py_modules=["plato_sdk"]` and `package_dir={"": "."}` (the repo root as the package dir); and the `Makefile`'s `test:` target covers only `fortran c` - the `go` and `zig` halves of the ecology sit outside the default test target.

---

## Footnote - `SmartCRDT`

Cosmetic-ignore shape again: `.gitignore:61` lists `__pycache__/` yet **two `.pyc` files are tracked** (`plato_core/__pycache__/jepa_script_picker.cpython-310.pyc`, `...test_jepa_script_picker.cpython-310-pytest-9.0.3.pyc`), plus **five tracked `smartcrdt.egg-info/` files** with no ignore rule at all. Otherwise its CI is strong (10 workflows, `npm test --coverage --shard=N/4`, codeql, security-scan, benchmark-regression). Minor, but it is the same "the ignore rule does nothing" defect that `superinstance-api`'s `.wrangler/` and `ai-ranch`'s `.env` share.

---

## Method corrections and additions (carry forward)

1. **Rank on code bytes by extension, minus vendored paths - and minus base64 payloads.** `.html` counted as code inflated `crab-trap-funnel` to 4.5 MB when 82.7% of that is embedded images. Subtract `data:*;base64,...` before ranking.
2. **`git clone --depth 1` is quota-free.** The REST tree endpoint costs 1 request/repo; with 5,307 repos and a 5,000/hr limit, cloning is the only way to rank a whole fleet on substance. `git ls-tree -r -l HEAD` puts the size in the meta field - split on TAB yields **two** parts; path is `parts[-1]`.
3. **Python mutation-testing: clear `__pycache__` between edits, and grep-assert the mutation landed.** Same-length edits within the same mtime second are invisible to the interpreter. A byte-clean `md5sum -c` is not a behavioural restore.
4. **A static shields.io badge is not a receipt.** `tests-81%20passing` is a literal in the README. Compare it against the *actual* test-function count before believing it.
5. **Check the CI trigger branch against the default branch.** `dodecet-encoder`'s default is `master`; `ci.yml` watches `main`. The shipped branch is never tested.
6. **A green `CI` badge can be a catalog bot.** `plato-portal` is 100% broken (CI 0/5) and simultaneously "green" (26/30 by run count) - group `actions/runs` by `name`, and check what the workflow actually *does*.
7. **PyPI is firewalled in this sandbox.** Prefer `unittest` (many repos' "pytest" suites are plain `unittest`), `node --test`, or a small vendored runner. `pip install` fails with `ProtocolError: Connection reset by peer` / "No matching distribution found".
8. **`gh` absent (10th consecutive wipe);** REST only. `git` clone/push work with `GIT_SSL_NO_VERIFY=1` and the token URL. The API token belongs to `SuperInstance` itself (`/users/SuperInstance/repos` redirects to `/user/193104091/repos`), so it can push to fleet repos directly.
9. **The hourly rate limit is the real constraint.** I spent 51 requests paging and hit the ceiling with 4 pages left; the reset was 27 minutes away. Paging 54 pages needs ~54 requests, so a full census + tree lookups does not fit in one 5,000/hour window alongside anything else. Clone instead.

---

## What I did not examine (stated plainly)

- **4,470 live non-fork repos.** I cloned and measured **229** of them (the background clone pool of 800 was cut short), and deeply read + verified **7**. The 174 repos named across 137 prior scout files were treated as already-examined and excluded from the shortlist; everything else is unmapped.
- **Forks (821) were filtered after confirming the named targets survived it** - a fork's green checkmark is not a fleet finding.
- **The Rust in `dodecet-encoder` was not executed** (no `cargo`/`rustc` here). Its Rust-side findings are inspection receipts; its CI/job receipts are execution receipts.
- **`datum`'s full suite could not be run green** because PyPI is blocked and `requests`/`toml`/`pytest-timeout` are undeclared. The failure *modes* were reproduced locally; the pass count under a correct install is unknown.
- 34 repos were pushed in the last 48h; I read the READMEs of 15 of them (`moldmaker`, `quilt-atlas`, `tells`, `quilt-rag`, `quilt-pincher`, `superinstance-advisor`, `quilt-engine`, `constraint-theory-py`, `chrono-tensor`, `sheaf-cohomology`, `synoptic-sheet`, `room-lens`, `OpenMAIC`, `lane-sheets`, `jev-semantic`). `quilt-pincher` ("a reflex engine built entirely from Quilt cells, <50ms, no LLM") and `superinstance-advisor` (553 files, live on Cloudflare's edge on a 5-min cron) are the two most promising unverified leads for a future round.
