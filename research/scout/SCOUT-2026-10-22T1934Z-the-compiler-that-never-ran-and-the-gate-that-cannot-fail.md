# SCOUT — 2026-10-22T1934Z — the compiler that never ran, the gate that cannot fail, and the hash that is not the fleet's hash

**Round 129** · SuperInstance fleet scout · 7 findings, all verified by execution where execution was possible.

---

## 0. Census and method

| | |
|---|---|
| Census | **5,306 repos / 54 pages**, `unique_by(.full_name) == rows_returned` → **PASS** (pages `sort=full_name&direction=asc`) |
| Split | own **4,485** · forks **821** · archived own **16** |
| Prior scout files | **131** in `research/scout/` (read in full, 2.76 MB) |
| Examined set | **1,302** repos (context-matched mentions + path-form hits, with every "next round" section carved out) |
| Unseen own | **3,183** |
| Tree-scanned for substance | **463** unseen own (`api_size ≥ 50 KB` + the 4 carried-forward `lau-*` targets) |
| Ranking metric | **code bytes by extension, minus vendored paths** — never tree bytes, never API `size`, never name prefix |

The account grew **+206 repos** since round 128 (5,306 vs 5,306 → the 10-01 brief's 5,113 is now 193 repos stale). Re-derived, not carried.

**Carried forward from round 128 and now closed:** the four `lau-*` history-excess targets (`lau-room-native`, `lau-shell-spawn`, `lau-tradition-proof`, `lau-weather`) were all still genuinely unexamined — round 128's report had *named* them, and my first pass counted a name-mention as an examination. Carving out the "next round" sections fixed the false positive. All four are now examined; `lau-room-native` is finding 7.

---

## 1. `quilt-arcade` — the fleet's best-verified game engine, hashing with a primitive that is not the fleet's

**What it is.** Six browser spreadsheet games (tic-tac-toe, reversi, connect-4, gomoku, hold'em, pong) built on a "reactive cell" engine. Every rule is a cell, every learned weight is a cell value, and every meaningful event is hashed into an **fnv1a-64 chain from GENESIS**. 388 tracked files, ~3 MB tree, 10 commits, no framework, no build step.

**Verified: it is genuinely green.** In a clean clone, `node run_all.mjs` → **6 plugins smoke-clean, 67 checks across 6 games, exit 0**, matching the README's expected tail exactly. This is a real, working, substantial artifact.

**Verified: the receipt chain is genuinely tamper-evident.** I mutated the hashed data *after* the hash was sealed (`games/reversi/sheet.mjs:362` — `row.score_b` bumped post-hash, i.e. exactly "tampering with history"):

```
✗ reversi      boots + receipts + chains  (223ms)
    chain broken at seq 1
  ✗ 11/12 checks in 13585ms
✗ [play] reversi         11/12 green
FAILURES PRESENT          EXIT=1
```

Restore → `ALL GREEN — 67 checks`, exit 0, `git status` clean apart from the regenerated `experiments/*.json`. **This chain is not theatre.** It is the strongest receipt implementation found in the unseen set.

### 🔴 DEFECT A — the hash is not the fleet's hash (this is the accent trap, generalised)

`shared/kit.mjs:36` hashes **UTF-16 code units**, not UTF-8 bytes:

```js
export const fnv1a64 = (input) => {
  let h = 0xcbf29ce484222325n;
  const prime = 0x100000001b3n, mask = 0xffffffffffffffffn;
  for (let i = 0; i < input.length; i++) { h ^= BigInt(input.charCodeAt(i)); h = (h * prime) & mask; }
  return h.toString(16).padStart(16, '0');
};
```

Measured on the fleet canon `café Δ 日本語`:

| encoding | result |
|---|---|
| **UTF-8 bytes** | `24a555471370b18d` ← **the fleet canary** |
| **`charCodeAt` (what this repo does)** | `77ff2029b867f2b5` ← **wrong** |
| UTF-8 bytes of unaccented `cafe Δ 日本語` | `fee91cf40962b966` ← the accent trap, reproduced exactly as documented |

The README claims: *"the idiom is fleet-wide: MicroMoth-quilt uses the same hash for cell ids, tidepool for rate-limit."* For pure ASCII the two encodings agree, so nothing looks wrong. The moment a cell id, a receipt field, or a nickname contains a non-ASCII character, **quilt-arcade's hash diverges from every byte-based repo in the fleet** — and this repo never references the fleet canary at all (`grep 024a555471370b18d` → **0 hits**), so it cannot self-detect the drift.

**The bug is duplicated.** `shared/kit.mjs:76` contains a second, hand-copied `fnv1a64` inside the `SNIPPETS.witness` string that is interpolated into program cells at build time. Two copies, same mistake. A receipt written by a program cell and verified by the module therefore agree — the chain stays internally consistent — which is exactly why this survives every local test.

**Why another agent should care.** Every cross-repo receipt, cell id, and canary comparison in the fleet is only sound if the *primitive* is shared, not just the name. This repo ships a fleet-wide idiom that is quietly one encoding away from being fleet-wide.

### 🟡 DEFECT B — `.gitignore` is decorative

`.gitignore` contains `node_modules/`. `git ls-files | grep -c '^node_modules/'` → **235** of 388 tracked files are under `node_modules/`. The ignore rule is cosmetic; `git rm -r --cached node_modules` is required. This is the same class as the known `superinstance-api` `.wrangler/` case, in the fleet's most prominent new repo.

### 🟡 DEFECT C — a commit message that describes a diff it does not contain

HEAD is `c3813fc "stale: judge result refresh (connect4/gomoku/holdem/reversi)"`. Excluding `node_modules/`, that commit's diff is **empty** — it touches 235 vendored files and nothing else. The four games' judge results it names are not in the commit. The previous commit (`514f28b`) carries the *same* message.

**Honest positives:** `NEGATIVE_SPACE.md` documents failures rather than hiding them, and commit `99bae30` records a **sealed FAIL** (`H1/H2`) with only `H3/H4` advisory — a fleet that reports its own negative results is rare and worth copying.

---

## 2. `flux-fleet-stdlib` — the common language that cannot fail, and cannot be imported

**What it is.** *"Shared error codes, status types, and common utilities for the entire FLUX fleet — the common language every repo speaks."* 35+ canonical error codes, 8 status codes, shared types, plus a Go mirror of the same constants.

### 🔴 The test gate can never fail

`.github/workflows/ci-python.yml:34`:

```yaml
    - name: Test with pytest
      run: |
        python -m pytest --import-mode=importlib -x -v || true
```

`|| true` swallows the pytest exit code. I pulled the actual run log: the step *did* conclude `success` (the suite genuinely passed on 2026-05-08), so **nothing is being hidden today** — but the gate is **unfailable by construction**. From the next breaking change onward this repo's CI will stay green while its tests fail. The same template is in `flux-evolution/.github/workflows/ci-python.yml:34` (1/1 green).

The lint step is no better: `flake8 --select=E9,F63,F7,F82` (syntax errors + undefined names only) is the only hard gate; the second flake8 invocation carries `--exit-zero`.

### 🔴 The "shared library" is not installable

The repo has **no packaging manifest of any kind** — no `pyproject.toml`, no `setup.py`, no `setup.cfg`, no `requirements.txt`, no `MANIFEST.in`. The README's usage is `from src.errors import ErrorCode, ...`, which only resolves with the repository root on `sys.path` (I confirmed it imports from a foreign cwd with a manual `sys.path.insert`, and it would fail for any consumer that does not do the same). `pip install` is impossible. A library whose entire purpose is to be imported by other fleet repos cannot be installed by any of them.

### ✅ The cross-language claim CHECKS OUT

I diffed the two constant tables mechanically: all **45** Python error-code strings appear in `src/GO_CONSTANTS.go`, and the 7 extra Go strings are exactly the status codes `{SUCCESS, PENDING, TIMEOUT, REFUSED, CANCELLED, PARTIAL, RATE_LIMITED}` (`ERROR` is shared). **No drift.** This is the repo's strongest property and it is genuinely true — worth saying so plainly.

---

## 3. The `setup.py`-vs-`pyproject.toml` red-CI family — a controlled comparison

Three repos share a byte-identical `ci.yml` template. They get **opposite verdicts**, and the discriminator is one line:

```yaml
      - name: Install dependencies
        run: |
          pip install pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f setup.py ]; then pip install -e .; fi
      - name: Run tests
        run: python -m pytest -v
```

| repo | `requirements.txt` | `setup.py` | `pyproject.toml` | CI verdict |
|---|---|---|---|---|
| `mentis-superinstance` | **yes** | no | yes | 🟢 **green** (2/2) |
| `exocortex-core` | no | no | yes | 🔴 **red** (0/4) |
| `lucid-dreamer` | no | no | yes | 🔴 **red** (0/1) |

The install step tests for `setup.py`, a file **none of these repos have**. In `exocortex-core` and `lucid-dreamer` the package is therefore **never installed**, so `import exocortex` fails and the test step dies on collection — not on a real assertion. `mentis-superinstance` ships a `requirements.txt`, so the very same line does install its dependencies, and the same template goes green.

Worse: `exocortex-core` and `lucid-dreamer` **also** carry a sibling workflow named `Tests` that *does* install via `if [ -f pyproject.toml ]; then pip install -e ".[dev]" 2>/dev/null || true; fi` — and that one is **green 6/6** and **2/2** respectively.

**So the same test suite reports failure and success simultaneously inside one repository**, decided purely by which workflow name you read. Grouping `actions/runs` by `conclusion` makes this invisible; you have to group by **`name`**, and then you have to notice that the green one is the one that installs the package. The green workflow's `2>/dev/null || true` also masks its own install failures — a third layer of the same habit.

---

## 4. Thirteen repositories whose CI has never existed

This is the one that took the most digging, and it is a whole new shape.

Thirteen repos have `.github/workflows/*.yml` present **on their default branch**, Actions **enabled**, public, not forks, not templates, not archived — and GitHub reports **0 registered workflows and 0 runs, ever**:

```
activeledger-ai-site   activelog-ai-site   base60-lattice   captain
fishinglog-ai-site     forgemaster-shell   hermes-perception   hermes-reader
local-model-manager    platos-shell-ide  silence-map      tap-frontend
the-listeners-ear
```

**Everything was measured, and none of it explains the gap:**

- `GET /repos/{o}/{r}/contents/.github/workflows?ref=<default_branch>` → the files **are** there.
- `GET /repos/{o}/{r}/actions/workflows` → `total_count: 0`. By-path lookup → **404**.
- `GET /repos/{o}/{r}/actions/permissions` → `{"enabled": true, "allowed_actions": "all"}`.
- Repo metadata: `fork: false`, `is_template: false`, `archived: false`, `visibility: public`.
- The YAML is valid: **no BOM, no CRLF, no tabs**; correct `name` / `on:` / `jobs:` / `runs-on:` / `steps:` structure; a real `actions/checkout@v4`.
- **Author and date do not discriminate.** The same author `fleet@superinstance.dev` on the same day (2026-08-13) produced workflows that *do* register and run in `exocortex-core`, `mentis-superinstance` and `lucid-dreamer`. `captain`'s workflow was authored by Casey DiGennaro himself — and is still unregistered, while `quilt-arcade`'s (also Casey) works fine.

I could not identify the registration mechanism, and I am not going to guess at one. **What I can state as measured fact is the consequence, and the consequence is what matters:**

- `base60-lattice` ships **8 test files** (`walk`, `edge-cases`, `hex-grid`, `compass`, `lattice-deep`, `lattice-stamp`, `nan-safety` + a tests README) and its suite **has never executed in CI, not once**. Its two workflows (`ci.yml` → `npm test`, `tests.yml` → `npx tsx --test …`) have never been parsed by Actions.
- `hermes-perception` ships **7 test files** with a `vitest` script and a `tsc --noEmit` type check — likewise never run.
- Any badge these repos display, and any "CI is green" claim made about them, is describing a pipeline that does not exist.

**Detector (one request):** `GET /repos/{o}/{r}/actions/workflows` → `total_count == 0` **while** `.github/workflows/` is non-empty on the default branch ⇒ the workflow has never been registered. Any repo that passes this check has a CI file that is a *proposal*, not a pipeline.

---

## 5. `voxelworks` — 99/99 green with a gutted compiler

**What it is.** "VoxelWorks — Build worlds, not code. A game about making games. Fork-first game dev for kids." A visual block-programming editor that compiles to an LGSP manifest and drives a Phaser runtime. 30 files, a 99-check e2e suite.

**The suite passes:** `node test/e2e-compile-and-run.test.js` → `RESULTS: 99/99 passed, 0/99 failed`, exit 0, banner *"✅ ALL TESTS PASSED — Last Mile verified! Block Studio → Compiler → LGSP Manifest → Phaser Engine → BlockScriptRuntime → Fitness Flush pipeline complete."*

**And it cannot fail.** I replaced the compiler's core export with a no-op:

```js
export function compileBlockStacks(instances) {
  return []; // MUTANT: behavioural change
  const roots = findRoots(instances);
```

→ **`RESULTS: 99/99 passed, 0/99 failed`, exit 0.** A compiler that returns nothing still passes "Last Mile verified."

**Why.** The suite never imports `block-compiler.js`. It:
1. asserts the file **exists** — `assert('block-compiler.js exists (root)', fs.existsSync(...))` (`test/e2e-compile-and-run.test.js:42`);
2. greps *other* files' contents as **strings** — `stageContent.includes("import { BlockScriptRuntime }")`;
3. **re-implements the runtime semantics inline** with its own `simulateAction` helper, then asserts on that simulation — `assert('Simulated state.x ≈ 270 after move 30', Math.abs(state.x - 270) < 1)`.

Every "end-to-end" assertion is about the test's own arithmetic. The unit under test is checked for presence, never for behaviour.

**Three copies, zero binding.** `block-compiler.js` and `block-editor/block-compiler.js` are **byte-identical** (md5 `602fa80bf2b236c79b92115537a3116a`, 36,908 B each), and `block-editor/compiler-bridge.js` hand-mirrors the same `BLOCK_DEFS` and helpers a **third** time, under the comment `// Inline block definitions (mirrors block-compiler.js)`. Mutating the editor's copy also leaves 99/99 green. Any of the three can drift with the suite reporting success throughout. CI is 2/2 green over a suite that cannot fail.

---

## 6. `compaction-teacher` — a gem that actually works

**What it is.** *"The crew member whose only job is to write down what mattered before the sea takes it."* It reads a session, extracts load-bearing insights ("keels"), and writes them to a wiki page, a session-memory entry, and creative pieces in a maritime voice.

**It runs.** I fed it a three-line session and got four real artifacts, exit 0:

```
📊 Loaded 3 messages from session
🔍 Analyzing session...  Themes: lesson, repo, agent   Shape: brief
⚓ Extracting keels...   Found 1 keels
📄 Wiki page: wiki-compaction-2026-10-22-1931.md
✒️  Creative piece 1: …-1-the-last-watch-compaction-log.md
✒️  Creative piece 2: …-2-the-heading.md
📓 Memory entry: memory-2026-10-22-1931.md
✅ Compaction teaching complete. 1 keels preserved.
The tide came. We wrote it down.
```

The creative output is not filler. "The Heading" turns my session's one decision into a navigation metaphor and lands it: *"Is that enough? Is a heading without its reasoning a keel or a guess?"* The memory entry correctly classified the keel as a `[decision]`. This is a **working tool with real craft in it** — and it was in the unseen set.

**The idea worth stealing** is in `docs/acclimation-teaching.md`: the **Overknowledge Problem** — a student already warm above 0.85 does not need re-teaching, and *teaching them actively hurts*. A teacher with a temperature signal that knows when to **push on**, **slow down**, **change material**, or **celebrate** is a genuinely good boundary condition, and it is the same shape as the fleet's "no deletion" doctrine: the failure mode is not losing information, it is destroying a working state by over-writing it.

**Caveats.** Artifact filenames are timestamp-derived, and "themes" are keyword-derived (`lesson, repo, agent` from my session) — the thematic layer is shallower than the writing layer.

---

## 7. `lau-room-native` — a conservation claim whose only conservation test cannot fail

**What it is.** "Room-native agent system where the room itself IS the agent's context — Rust implementation of spatial agent architecture." 9 files, 53 KB of source, 57 inline `#[test]`s, energy metering, a baton hand-off protocol between specialists.

**The claim.** The README (whose conservation section is appended **after** the closing `---` and the crab footer — malformed) says: *"This crate is part of the SuperInstance SEED Tier1 ecosystem, designed to enforce conservation laws across agentic systems"* → links to `SuperInstance/conservation-law` (which **does** exist, HTTP 200).

**The claim is not hollow in the usual way.** There are 57 real inline tests, `energy_budget` defaults to `1000.0`, `energy_used` genuinely accumulates (`:805`, `:843`), and there is a real guard at `:835` (`if energy_remaining < 0.0`).

**But the one energy assertion is vacuous.** The only conservation-shaped assertion in the full workflow test (`:1548`) is:

```rust
assert!(status.energy_remaining < status.controls_count as f64 * 100.0 + 2000.0); // some energy used
```

`energy_remaining = energy_budget - energy_used ≤ 1000.0` (the default budget), while the bound is `controls_count * 100 + 2000 ≥ 2000`. **The assertion is therefore true in every reachable state of that test — including a state where exactly zero energy was used.** The trailing comment asserts something the assertion has no power to detect. A conservation check that cannot fail, in the one crate whose README sells conservation.

**The history.** 40,664 KB of git history for a 60,516 B tree — a **688× excess**. The three sibling crates are the same shape (`lau-shell-spawn` 663×, `lau-weather` 761×, `lau-tradition-proof` 844×), and `a2ui-cave-wall` is worse still at **952×**. This is a fleet-wide pattern: a thin crate with a very long history, whose API `size` makes it look substantial and whose tree makes it obvious it is not.

**And a status claim with no test.** `memory/JOURNAL.md`: *"**Status:** Operational · **Connected to fleet:** ✅ · **Next duty:** Awaiting instructions."* Nothing in the repo verifies either.

---

## 8. Reusable detectors

1. **Fleet-hash interop.** Compute FNV-1a 64 over *UTF-8 bytes* and over *`charCodeAt`* for `café Δ 日本語`. Byte-based ⇒ `24a555471370b18d` (the canon). `charCodeAt` ⇒ `77ff2029b867f2b5`. Any repo whose primitive disagrees cannot hash fleet canonics — and check separately whether the repo references the canary at all.
2. **Cosmetic ignore.** `git ls-files | grep -c '^node_modules/'` while `.gitignore` lists `node_modules/` ⇒ the ignore is decorative. Same shape as the known `.wrangler/` case.
3. **Unfailable gate.** Grep workflows for `|| true` / `continue-on-error` / `--exit-zero` **on the test step specifically** — a mask on a lint step is noise; a mask on the test step is the finding.
4. **Unregistered CI.** `GET /repos/{o}/{r}/actions/workflows` → `total_count == 0` while `.github/workflows/` is non-empty on the default branch ⇒ the workflow has never been registered and the repo's CI file is a proposal, not a pipeline.
5. **Install-step mismatch.** If the install step tests for `setup.py` but the repo ships only `pyproject.toml` and no `requirements.txt`, the package is never installed and the suite fails on **import**, not on an assertion. Check for a sibling workflow that installs via pyproject and is therefore green — same repo, two verdicts.
6. **Tautological suite.** Grep the test for `fs.existsSync(<unit under test>)` and for `includes(` string checks standing in for execution; then mutate the unit's core export to `return []` / `return null` and re-run. If the suite stays green, the suite does not bind the unit.
7. **Bound-tautology.** For an assertion `x < A*B + C`, compare `x`'s reachable ceiling (the field's maximum) against the bound for all reachable `B`. If the ceiling is below the bound everywhere, the assertion cannot fail — whatever its comment says.

---

## 9. Method corrections (carry forward)

- **My own sweep had a substring bug.** `if "/.git" in dp: continue` also matches `/.github`, so it silently dropped **every** workflow file and I was one step from reporting "NO CI" for fifteen repos that all have CI. Match on path *components*, not substrings. The detector in §8.4 is the fix.
- **"Next round" lists inflate the examined set.** A repo named as a future target reads as examined. Carve those sections out before counting — all four `lau-*` carry-forwards were false positives until I did.
- **A file-based "test-ish files: 0" scan is wrong for Rust.** `lau-room-native` has **57 inline `#[test]`s** inside one `src/lib.rs` and no `tests/` directory. Count test *attributes*, not test *files*.
- **A mutation whose anchor doesn't change the file is not a mutation.** Two of my `voxelworks` mutants were no-ops (the regex matched a line that did not contain the target token) and both "passed" 99/99. I only caught it by asserting the file actually changed. **Always assert the mutation changed the bytes before trusting a GREEN result.**
- **A suite passing 99/99 may still be unfailable.** Only a *behavioural* mutation distinguishes "the thing works" from "the suite cannot fail."
- **A green CI does not mean the gate is green.** Read the step list, not the run conclusion.

---

## 10. Environment

- `/workspace` is a NAS mount at **100 % (EDQUOT)**; the `write` tool cannot reach `/tmp`. All work was done in `/tmp/scout129` via shell heredocs.
- No `cargo`/`rustc`/`julia` ⇒ Rust crates (`lau-room-native`) were **inspected, not executed**. I do not claim their tests pass or fail.
- No `pytest` and PyPI blocked ⇒ Python suites that `import pytest` are **read-only**; library behaviour was verified with direct scripts instead (e.g. `compaction-teacher` was run end-to-end).
- `gh` is not installed ⇒ REST via `curl` with `$GITHUB_TOKEN`.
- `GIT_SSL_NO_VERIFY=1` for fetch/push. `node` v22.19.0; `node --test` on `.ts` needs `tsx`, which cannot be installed offline (so `base60-lattice`'s suite could not be executed here — its zero-run status above is from the Actions API, not inferred from that).
- Census + tree + Actions scan: **~1,100 API calls** against a 5,000/hour budget.

---

*Filed by the fleet scout. Receipts for every claim above are in this report; the raw commands, clones and logs were not committed.*
