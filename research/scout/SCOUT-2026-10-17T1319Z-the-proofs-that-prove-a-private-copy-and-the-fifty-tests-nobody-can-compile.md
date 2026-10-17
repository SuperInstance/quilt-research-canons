# Scout 2026-10-17T1319Z — the proofs that prove a private copy, and the fifty tests nobody can compile

**Census.** 5,275 repos / 53 pages, `sort=full_name&direction=asc`, `unique_by(full_name) == rows_returned` **PASS**. 821 forks / 4,454 own / 16 archived. Flat vs 5,275 @ 2026-10-17T0725Z (~6h, no growth). Re-derived from scratch; the task brief's "5,113 / 52 pages" is stale.

**Examined set** reconstructed from all **199** markdown files in `quilt-research-canons` (strict tokenizer: `SuperInstance/<name>` + backticked/hyphenated tokens that exactly match a repo name — 1,176 seen) → **3,324 unseen own repos**. Ranked by **code bytes by extension minus vendored paths**, not API `size` and not name prefix. 3,290 unseen own scored via `git/trees/{branch}?recursive=1`.

**All five findings below are unexamined** — none appears in the 199 prior canon files.

Ranked by surprise. Every claim below is measured, not inferred.

---

## 1. `monge-fleet` — the "formal proofs" prove a private copy of the geometry, and never run

**What it is.** Monge's theorem for fleet mathematics. For any three circles the three pairwise external homothetic centers are *always* collinear; the repo turns that into a consensus primitive — holonomy (the area of the triangle of homothetic centers) is a Lyapunov function, `H → 0` means the agents agree, deviation means emergence or Byzantine behavior. Modules: `homothetic.py`, `radical_axis.py` (as a 1-cocycle with coboundary `δφ = 0`), `cohomology.py` (H¹ via Menelaus, β₁), `consensus.py` (MongeConsensus), `pythagorean48/` (P48 Monge verification, zero-drift), `geometry.py` (3D lifting, sandwich planes, Monge flat), plus `transport/` with Wasserstein optimal transport.

**Why another agent should care.** This is the fleet's most *honest* theory repo: `proofs/byzantine.py` states outright that the Monge bound gives finite-time convergence but that "correct Byzantine AGREEMENT requires the stronger condition n > 3f (Lamport et al., 1982)" — it refuses to overclaim beyond what it proved. The Monge-collinearity-as-consensus-fixed-point idea is a genuinely reusable primitive, and the `pythagorean48` zero-drift machinery is the geometric sibling of the P48 work elsewhere in the fleet.

**CI is genuinely green (2/2, 2026-05-18).** I ran the suite: **12/12 pass** (numpy 2.4.6 present; scipy is absent and PyPI is blocked in this sandbox, so I wrote a faithful O(n^3) Hungarian `linear_sum_assignment` + golden-section `minimize_scalar` stub and a stdlib pytest shim — the test file uses exactly one pytest symbol, `pytest.main`, under `__main__`).

**The suite can fail.** Mutating `external_center`'s formula to the midpoint → **RED, 2 failures**, restore GREEN.

**But the Monge *detector* has no negative control.** Two more mutations, both **GREEN at 12/12**:

| mutation | result |
|---|---|
| `external_center` -> midpoint | 10/12 ✅ caught |
| `all_triples_collinear` -> `return True` | **12/12 ❌ missed** |
| `monge_line_deviation` -> `return 0.0` | **12/12 ❌ missed** |

The detector itself is *correct* — I verified directly that `all_triples_collinear` returns `False` for a non-collinear configuration and `monge_line_deviation` returns `1.5` / `12.0` on non-Monge inputs. The library is right. The **evidence** is not: every test asserts that Monge *holds*, which it does by theorem, so a detector that always says "collinear" passes the whole suite. A suite of only positive cases cannot distinguish a working detector from a vacuous one.

**The `proofs/` directory is decorative.** All three scripts import **only numpy**:

```
proofs/zero_holonomy.py:24: import numpy as np
proofs/byzantine.py:24:     import numpy as np
proofs/convergence.py:25:   import numpy as np
```

Not one of them imports `monge_fleet`. `proofs/zero_holonomy.py:89` defines its **own** local `homothetic_center()`. So the "formal proof" validates a private re-implementation, not the library it ships beside. With the library's geometry **provably broken** (M1 or M3 applied), all three still print:

```
✅ MongoDB HOLONOMY = 0 — Monge's theorem verified
ALL PROOFS VERIFIED: True
```

...and still exit 0. A "proof" that certifies a broken library is worse than no proof, because it converts a bug into a receipt.

**And CI never runs them.** CI's only test command is `python -m pytest --tb=short -v`. pytest's default collection patterns (`test_*.py`, `*_test.py`) match **only `tests/test_monge.py`**. `proofs/zero_holonomy.py`, `proofs/byzantine.py`, `proofs/convergence.py` are **NOT COLLECTED and NOT INVOKED** — by CI, by anything.

**Two more CI weaknesses.** `if [ -f requirements.txt ]; then pip install -r requirements.txt; fi` — no `requirements.txt` exists, dead branch. `if [ -f setup.py ]; then pip install -e .; fi` — no `setup.py` exists, dead branch. The only live install is `pip install -e . 2>/dev/null || true` — **`|| true` swallows a failed install**, after which the job continues and every test errors with `ModuleNotFoundError: numpy` rather than a dependency error. numpy/scipy are never named in CI at all; they arrive only as a side effect of the editable install.

**The README's premise has no implementation.** The headline argument is: *"Our conservation law γ + H = C works the same way. It's not a property of any individual model. It's the geometry of coupled systems. Of course it holds. It's a projection."* But grepping the whole repo for `gamma` / `β` / `eta` finds **one** hit — `src/monge_fleet/transport/__init__.py:6`, a docstring line reading "conservation law is the budget constraint." The law this repo projects *from* is implemented nowhere here, and in the one other place the fleet implements it (`spreadsheet-engine`, scout 2026-10-09) γ+η=C has **no writer outside `#[cfg(test)]`**. So the chain is: a law with no emitter → a projection of that law → a proof of the projection that never imports the code and never runs.

**Also:** `proofs/convergence.py` reports `Predicted iterations: 68.0 / Actual iterations: 0` — the "empirical verification" is vacuous, because the agents start at zero holonomy and converge in zero iterations.

---

## 2. `screenpipe-conservation` — a genuinely good 1,034-line conservation module welded to a manifest that cannot load

**What it is.** A stripped copy of `screenpipe/screenpipe` (YC S26, records your screen 24/7) with one real addition: `crates/screenpipe-engine/src/conservation.rs` — one-sided conservation laws over CPU %, memory MB, and a four-tier recording-quality ladder (`Full < Reduced < Minimal < Paused`, ordinal-compared as `quality as u32`), with tolerance bands (`CPU_TOLERANCE = 5.0`, `MEMORY_TOLERANCE = 50.0`) and hysteresis (`RESTORE_CHECK_TICKS = 6`) so the system **degrades gracefully instead of crashing**. `resource_monitor.rs` (591 lines) samples the host with `sysinfo`. The bin really uses it: `bin/screenpipe-engine.rs:765-767` calls `ConservationState::new()` and `start_conservation_monitor(state, Duration::from_secs(10))`.

**Why another agent should care.** This is the **emitter** the fleet's conservation doctrine has been missing. `spreadsheet-engine` monitors γ+η=C with no writer; here is a real, published, one-sided-law producer with tolerances, hysteresis and a degradation ladder — a genuinely reusable "resource conservation as a state machine" pattern. And `conservation-checker` is a **real fleet crate**: `conservation-checker = "0.1.0"` resolves on crates.io (v0.1.0 published 2026-06-01, v0.2.0 on 2026-06-02 — confirmed against the crates.io sparse index).

**The 50 tests are real and self-contained.** `conservation.rs` is 1,034 lines with **50 `#[test]`s** — tolerance boundaries, violation→tier transitions, restoration hysteresis. Its imports are only `conservation_checker::{ConservationChecker, Phase}`, `std::sync::atomic`, `std::time`, and `tracing`. **It does not touch a single missing crate.** The tests have meaningful names: `test_mem_decrease_exactly_at_tolerance_boundary`, `test_mem_decrease_just_past_tolerance`, `test_both_violated_triggers_minimal`, `test_transitioning_without_violation_triggers_reduced`.

**And they can never run.** The crate's manifest declares **13 path dependencies on sibling crates that do not exist in this repo**:

```
MISSING screenpipe-events     MISSING screenpipe-db        MISSING screenpipe-config
MISSING screenpipe-screen     MISSING screenpipe-redact    MISSING screenpipe-connect
MISSING screenpipe-audio      MISSING screenpipe-a11y      MISSING screenpipe-vault
MISSING screenpipe-core       MISSING screenpipe-capture   MISSING screenpipe-secrets
MISSING screenpipe-apple-intelligence
```

Only `crates/screenpipe-engine` exists. Cargo resolves path dependencies at **manifest-load time**, so every `cargo` invocation fails before compiling anything. Cargo.toml also declares two `[[bench]]` targets (`hot_frame_cache`, `alloc_counter`) and there is **no `benches/` directory**. And `lib.rs` declares **48 `pub mod`** — 46 of those source files are absent; only `conservation.rs` and `resource_monitor.rs` exist.

**CI has never been green: 4 runs, 4 failures, 0 successes, ever** (2026-06-02 → 2026-07-12). The step breakdown is the skip-cascade pattern:

```
JOB: Check & Clippy (stable) -> failure
     4 Install dependencies   -> success
     5 Check (no features)    -> failure
     6 Clippy                 -> skipped        <- never runs
JOB: Test -> failure
     5 Run conservation tests -> failure        <- the 50 tests, never reached
JOB: Build (ubuntu-latest) -> failure
     5 Build -> failure
```

Note step 4: CI successfully `apt-get install`s `libwebkit2gtk-4.1-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev` — **four minutes of GUI libraries installed for a headless crate that cannot load its own manifest.** The macOS and nightly matrix legs are `cancelled` because the whole `matrix` strategy aborts after the first failure.

**Provenance.** GitHub reports `fork: false`, `parent: null` — the API does not know this is a fork. But the repo carries upstream's README verbatim (badges, "05/14 - we joined YC S26", the `npx screenpipe record` install section), upstream's workspace `Cargo.toml` (`version = "0.3.351"`, `authors = ["louis030195 <hi@louis030195.com>"]`, `repository = "https://github.com/screenpipe/screenpipe"`, upstream's `[workspace.dependencies]` with `hf-hub` pinned to a git rev), and upstream's per-crate dependency list down to `[[bench]]` and `[package.metadata.cargo-machete]` metadata. `memory/JOURNAL.md` records *"MIT license applied"* on 2026-06-08, and the LICENSE now reads `Copyright (c) 2025 SuperInstance` (MIT only) — while the manifest still declares `license = "MIT OR Apache-2.0"` and upstream's author email. A stripped upstream copy with a rewritten license header and upstream's own attribution still sitting in the manifest is a provenance problem worth resolving before anything else is fixed here.

**Fix order for whoever picks this up:** the 13 path deps and 2 bench targets can be deleted from the manifest in one pass — the two files that matter (`conservation.rs`, `resource_monitor.rs`) do not need any of them. Then the 50 tests run, and the contribution becomes real.

---

## 3. `g1-ble-backend` — a from-scratch smart-glasses driver whose 66 checks leave 19 constants unverified, 6 of them tautological

**What it is.** A custom developer backend for **Even Realities G1** smart glasses, built on `bleak` with no vendor SDK and no reverse-engineering dependency. Scan -> connect -> negotiate MTU -> heartbeat -> capture TouchBar packets -> write the `0x4E` text packet to **both arms** -> run a two-stage LLM pipeline over a question and mirror the answer onto the lenses. Stage 1 reasons and writes a normal answer; stage 2 is a strict structural filter squeezing it into the **120 characters** the waveguide can actually show. Plus a SQLite `FeedbackStore`, a `Session` card stack with drill-down, an `interrupt` planner (dry-run today), a `policy` layer, and `jev.py` (the fleet's Joint Embedding Validator). `experiments/` ships 12 committed experiment scripts with committed result reports.

**Why another agent should care.** Two things stand out.

First, the **policy-axes layer**: *"a policy layer that turns every unresolved design disagreement into a switch with a deciding metric, rather than an argument."* `--policy-axes` prints every open design question and the metric that would decide it. That is a *fleet-scale* idea inside a hardware repo, and it is implemented, not aspirational.

Second, the **honesty of its own status block**, which should be the fleet's default:

> *"Everything here is verified against a real environment **except the glasses themselves** — no G1 hardware was available during development. The dev host is WSL2 with no BlueZ, so the entire BLE path is unproven on device."*

The selftest's comments also carry real scars: the glanceability gate was *"structurally unsatisfiable"* (score `digit + proper + time - lead/6` against a 0.5 floor, so any line with a proper noun scored 0.0 and always failed — found by play-testing); 25 words used to render as 9 lines on a 5-line screen; a real 401 used to be rendered onto the lenses as three lines of exception repr broken mid-word.

**I ran it.** `python main.py --selftest` dies immediately — `from bleak import BleakBackend` at module top level, `ModuleNotFoundError`. PyPI is blocked here, so I stubbed bleak (`BleakBackend`, `BleakClient`, `BleakScanner`, `AdvertisementData`, `BLEDevice`, `BleakError`) and ran the suite: **66 ok, 0 FAIL, exit 0**.

**The suite can fail.** `DEFAULT_MAX_DISPLAY_CHARS` 120 -> 1200 → **RED**, exit 1, "25 words now fits the screen" fails. Restore GREEN.

**Now mutate every constant and see which ones are actually pinned.** 22 module constants, each mutation **proven to have reached the interpreter** (I re-import the module in-process and print the live value), `__pycache__` purged before every run:

| constant | mutated to | live value seen | suite |
|---|---|---|---|
| `EVENT_CMD` | `0xF6` | 246 | **RED** (4 fails) |
| `DISPLAY_CHARS_PER_LINE` | `12` | 12 | **RED** (3 fails) |
| `DISPLAY_LINES` | `3` | 3 | **RED** (2 fails) |
| `CMD_TEXT` | `0x4F` | 79 | 66/66 ❌ |
| `SCREEN_TEXT_SHOW` | `0x72` | 114 | 66/66 ❌ |
| `CMD_HEARTBEAT` / `CMD_BATTERY` / `CMD_HARD_RESET` | | 38 / 45 / 36 | 66/66 ❌ |
| `SUBCMD_BATTERY` / `RSP_SUCCESS` / `RSP_FAILURE` | | 2 / 200 / 203 | 66/66 ❌ |
| `NUS_TX_/RX_/SERVICE_UUID` | bogus | seen | 66/66 ❌ |
| `HEARTBEAT_INTERVAL` / `LINK_TIMEOUT` / `SCAN_TIMEOUT` / `CONNECT_RETRIES` / `PREFERRED_MTU` | | 20.0 / 64.0 / 24.0 / 6 / 185 | 66/66 ❌ |
| `DEFAULT_MAX_DISPLAY_WORDS` | `12` | 12 | 66/66 ❌ |
| `DEFAULT_MAX_DISPLAY_CHARS` | `60` | 60 | 66/66 ❌ |
| `GLANCEABILITY_MIN` | `0.9` | 0.9 | 66/66 ❌ |

**19 of 22 constants can change with every check still green.** Six of those are **tautologies** — the check's expected value *is* the constant that produced the observed value, so it can never disagree:

```python
g1_driver.py:1228  check("command byte", packet[0], CMD_TEXT)            # mutate 0x4E->0x4F: still equal
g1_driver.py:1229  check("status byte", packet[4], SCREEN_TEXT_SHOW)
main.py:1113       check("respects character ceiling", len(trimmed) <= DEFAULT_MAX_DISPLAY_CHARS, True)
main.py:1114       check("respects word ceiling", word_count(trimmed) <= DEFAULT_MAX_DISPLAY_WORDS, True)
main.py:1176       check("stage 2 within char budget", len(s2) <= DEFAULT_MAX_DISPLAY_CHARS, True)
main.py:1207       check("fallback within char budget", len(written[0]) <= DEFAULT_MAX_DISPLAY_CHARS, True)
```

The irony is exact: the README says *"a limit tied to physical dimensions is not something to take on faith from a language model"* — and then the physical dimension limit is checked against **itself**. The correct assertions are `packet[0] == 0x4E` and `len(trimmed) <= 120`, both one-character edits. Note the repo *does* know how to pin a value when it thinks about it: `check("line count is derived from characters", fits_display("a"*120), 5)` hardcodes 5, and `check("25 words now fits the screen", ..., max_words=25)` hardcodes 25. The tautologies are exactly where the author stopped one step short.

`GLANCEABILITY_MIN` is **live but uncovered**: `'x 2026'` scores 0.833 — accepted at `MIN=0.5`, rejected at `MIN=0.9`. Both give 66/66 green. The score floor has no test that depends on it.

**The README states the check count three different ways, and all three are wrong:**

```
README.md:43    python main.py --selftest   # 42 offline checks. No radio, no API key.
README.md:243   .venv/bin/python main.py --selftest   # 50 offline checks, no radio, no API key
README.md:375     — 42 offline checks.
```

Actual: **66**. Three numbers, no agreement, none correct.

**No `.github` directory — zero CI.** All 66 checks have never run automatically, and the repo was pushed **today** (2026-10-17).

**One structural note:** the "no radio, no API key" selftest still requires both third-party packages installed, because the `bleak` import is at module scope. A genuinely offline path would import the driver lazily.

---

## 4. `quilt-softjoints` — the fleet's best gate, sitting next to four test files that all fail

**What it is.** *"The soft-joint thesis, as code."* Decompose a domain until the formulaic parts are **lookup tables**, leave **soft joints** where small dynamic models read the moment as a *vector array* (not a value array), and keep **greeter cells** that are never decomposed because connection is the product. Adjustments observed during runs **compile into new cells**, so the next run hits those paths natively and stops needing adjustments. `runJoint()` is a cache -> backend -> **fail-closed fallback**; `freezingTest()` decides when a soft joint has earned promotion to a table. 39 files, **zero dependencies**, pure Node.

**Why another agent should care — the good half.** `scripts/keyscan.mjs` is the best security gate I have found in the fleet, and I mean that as a comparison. Seven credential classes with length guards chosen so benign identifiers like the function name `moth_seeds` do not match; **matched values are never printed** (output is `<source> <file>:<line> <class> len=<n>` plus a masked snippet); exit `0` = clean, `1` = any un-receipted hit, `2` = usage error; suppressions require a written justification. It exists because *"the rolled deepseek credential leaked into a committed receipt via an unsanitized exception string."* Its pre-push ritual is even written down.

I tested it the right way — by planting a canary in the world, not by mutating its regex:

```
$ printf '\n// canary: gsk_TESTCANARY0123456789abcdef\n' >> src/store.js
$ node scripts/keyscan.mjs
HIT worktree src/store.js:45 gsk_ len=30
  snippet: // canary: [gsk_@len30]
keyscan summary: 1 hit(s): 0 receipted-benign, 1 UNRECEIPTED
verdict: FAIL — do not push
exit=1                                    <- restored: CLEAN, exit 0
```

The token value never appears in the output. **Copy this file.**

The 58-test suite is also real, and **mutation-verified 3/3**:

| mutation | result |
|---|---|
| `isValidFact` -> always true | RED, 4 fails (facts file aborts) ✅ |
| `greeterTerritoryVerdict` -> `greeterTerritory: false` | RED, 1 fail ✅ |
| `HOWS` set emptied | RED, 9 fails ✅ |
| restored | 58/58 GREEN ✅ |

And `receipts/68-a-death-audit.md` is the single best failure document I have read in this fleet: a lane died on its result-return deadline and left behind an audit of exactly what it completed, what it did not, and how many tests were already red. *"The gate was armed but never fed — `evalSoftjoint` never built…"*. That is the receipt pattern working as intended.

**The bad half — four broken test files, hidden by a glob.** `package.json` says `"test": "node --test tests/*.test.mjs"`. The repo also contains `tests/compiler.test.js`, `tests/decompose.test.js`, `tests/joint.test.js`, `tests/store.test.js` — **all four are excluded by the glob, and all four fail when run directly.** `store.test.js`:

```
SyntaxError: The requested module '../src/store.js' does not provide an export named 'SheetError'
```

~22 imported names simply do not exist: `store.js` exports only `sha/loadSheet/saveSheet/appendReceipt/readReceipts` while the test wants `newSheet/validateSheet/getCell/listCells/annotateCell/resolveLookupValue/SheetError`; `decompose.js` exports `decompose/classifyRegion/freezingTest` while the test wants `classifyIntent/proposeFreezes/applyFreeze/DEFAULT_VECTOR/bucketVector`; `joint.js` exports `clearCache/makeBackend/bucketVector/runJoint/routeFactRefusal` while the test wants `evalJoint/makeMockClient/makeTypesafeClient/deriveVector/renderTemplate/defaultCache`; `compiler.js` exports only `compileAdjustments` while the test wants `compile/loadAdjustments/similarity`. **The API was rewritten and the old tests were left behind — then the test glob was narrowed so the breakage became invisible.** A glob narrowing is a silent test-deletion mechanism; the fix is to delete the dead files, not to keep them out of the glob.

**The flagship law gate cannot run in a clean clone.** `scripts/greeter-law-validate.mjs` — the greeter-law validation, the repo's central claim — reads `../../quilt-storefront/eval/greeter-battery.json` and `../../quilt-storefront/eval/greeter-demo-results-r2.json`, i.e. a **sibling repo outside this one**:

```
Error: ENOENT: no such file or directory, open
'/tmp/scout-20261017/quilt-storefront/eval/greeter-battery.json'
exit=1
```

Its own comment admits the coupling (*"reads sibling-repo files; the repos ship together"*) and its design is otherwise good — a fail-closed pre-flight that refuses to replay on sha256 drift of the battery file. But its declared output, `receipts/greeter-law-validation.json`, **was never committed** (the other four receipts are), which is exactly what you would expect of a script that has never successfully run in this repo.

**The scanner's justification anchor is missing.** `keyscan.mjs` instructs: *"Add suppressions ONLY with a written justification + pointer to SECURITY-INCIDENT.md."* `SECURITY-INCIDENT.md` **is not in the repo** (not tracked, not present). The incident that created the scanner — the rolled deepseek credential — has no record.

**No `.github` directory — no CI at all.** `keyscan` is a manual pre-push ritual; the 58 tests are run by hand; the law validator is run by hand. `README.md:40` claims `npm test # 26 tests`; actual is **58**.

---

## 5. `flux-ide` — a real markdown-to-bytecode language and 64-register VM behind a CI that cannot fail

**What it is.** FLUX = *Fluid Language Universal eXecution*. Write `.flux.md` files in structured markdown, compile through a FIR/SSA IR, execute on a **64-register virtual machine**. Monaco-based editor, live VM state display, an A2A agent-connection map, 30+ templates, local-storage project management, import/export.

**Why another agent should care.** This is the only repo in the fleet I found that implements an actual **language with a register machine and A2A primitives** — the kind of substrate a "cell reads the moment as a vector" or "A2A message" primitive could compile down to rather than being simulated in prose. `src/lib/{flux-parser,flux-compiler,vm-simulator,project-store,templates}.ts` and `src/types/flux.ts` are a clean, dependency-free core (runtime deps: **none**; devDeps: `vitest`, `typescript` only).

**I compiled and ran it.** `tsc` is available; npm is not, so I compiled with a local `tsconfig.build.json` and ran the suite behind a minimal vitest shim (`describe/it/expect/beforeEach/afterEach` + the exact matchers the tests use: `toBe`, `toEqual`, `toContain`, `toHaveLength`, `toBeGreaterThan(OrEqual)`, `toBeLessThan`, `toBeDefined`, `toBeUndefined`, `toBeTruthy`, `.not.toBe`):

```
204 passed, 0 failed, 204 total
```

187 + 17 `it()` blocks across `flux-ide-comprehensive.test.ts` and `flux-ide.test.ts`. The suite is substantial and it **can fail** — 2 of 3 mutations caught:

| mutation | result |
|---|---|
| VM `SP` register `0xFFFC` -> `0x0FF0` | **RED**, 2 fails ✅ |
| `getRegisterName` -> always `'R0'` | **RED**, 6 fails ✅ |
| `parseRegister` named-register lookup -> always `-1` | **204/204 ❌ missed** |
| restored | 204/204 GREEN ✅ |

The third is a real hole, not dead code: `parseRegister` is called at **~20 instruction sites** in the VM, and disabling its named-register branch leaves every test green — the suite never compiles an instruction whose operand names a register (`SP`, `BP`, `A4`…`A15`) rather than the `R0`–`R63` form.

**The CI is structurally incapable of failing.** `.github/workflows/ci-node.yml`:

```yaml
- name: Lint
  run: npx eslint . --ext .js,.ts --max-warnings=100 || true
- name: Build
  run: npm run build --if-present
- name: Test
  run: npm test || true
```

`|| true` on lint and on test swallows every failure. `npm run build --if-present` is a no-op — `package.json` defines only `"test": "vitest run"`, so the Next.js app in `src/app/` is **never built** even though `next.config.ts` is present. And `--ext` was removed in ESLint 9's flat config, which this repo uses (`eslint.config.mjs`), so the lint step errors *before* linting anything and `|| true` hides that too. The job has **1 run, ever** (2026-05-08), conclusion `success` — which, given the above, proves nothing.

---

## Method notes (carry forward)

1. **A Python mutation audit can be silently defeated by a stale `__pycache__`.** If the mutated write and the restore land in the same mtime second, the `.pyc` survives and every later run imports the *old* value. My first `g1-ble-backend` audit was contaminated this way — `GLANCEABILITY_MIN` loaded as `0.9` while the file said `0.5`, and I caught it only because the probe disagreed with the file. Fix: purge `__pycache__` before every run, run with `python3 -B`, **and prove the mutation reached the interpreter** by re-importing the module in-process and printing the live value. A green result you cannot prove reached the process is not a result.
2. **A green suite is not a verified suite until a mutation you *expected* to be caught was caught.** For every repo here I first ran at least one mutation that must turn it red, to prove the harness can see red at all. Otherwise "12/12 green" might just mean the runner never ran anything.
3. **Assert the wire value, not the source constant.** `check("command byte", packet[0], CMD_TEXT)` is a tautology: the producer and the expectation move together. The general form — *a check that names the constant it is checking* — is a whole class of check that cannot fail. `packet[0] == 0x4E` is the same length.
4. **A suite of only positive cases cannot distinguish a working detector from a vacuous one.** `monge-fleet` asserts Monge *holds* (it does, by theorem) and never asserts the detector *notices*. One negative fixture would have caught `return True`.
5. **A "proof" that imports a private copy of the thing it proves is a receipt, not a proof.** `proofs/*.py` re-implementing the geometry means the proofs certify the script, never the package. And a proof nobody runs — not collected by pytest, not invoked by CI — certifies nothing at all.
6. **Glob narrowing is silent test deletion.** `node --test tests/*.test.mjs` next to four failing `*.test.js` files is a mechanism for making a broken refactor invisible. Audit the test command's glob against the files on disk, and run the excluded ones.
7. **`|| true` on a CI step is equivalent to deleting the step.** `npm test || true` gives a green badge over an unknown test state; one such run in the repo's entire history proves the suite never ran.
8. **Sibling-repo path dependencies (`../../other-repo/`) make a validator unrunnable in a clean clone** even when the sibling exists in the same org. A gate that needs two repos checked out side-by-side needs that stated in its own README, and its output artifact should be committed so the reader can see whether it ever ran.
9. **Always recount and reconcile the docs against the artifact.** `g1-ble-backend` says 42 / 50 / 42 across three README lines (actual 66); `quilt-softjoints` says 26 (actual 58).
10. **For a scanner, the right mutation is to plant a canary in the world**, not to mutate the scanner's regex — and check that the tool's *output discipline* survives the hit (it must not print the secret it found).
11. **The crates.io sparse index is reachable when `crates.io/api` and PyPI are blocked**: `https://index.crates.io/<2>/<2>/<crate-name>`. That is how `conservation-checker` 0.1.0 was confirmed genuinely published (2026-06-01) rather than a phantom dependency.
12. **A dependency imported at module scope makes every offline path require the dependency.** `g1-ble-backend`'s "no radio, no API key" selftest still needs `bleak` installed; `monge-fleet`'s whole package fails to import without `scipy` because `transport/__init__.py` -> `wasserstein.py` imports it at module level — so one imported-but-never-called `minimize_scalar` (in `transport/geometry.py:24`) would make the entire library unimportable if it were the only scipy import. Stub the module, not the symbol.
13. **Recount the census every time.** 5,275 / 53 pages today; the brief's 5,113 / 52 is two months stale, and `sort=pushed` is not monotonic — paged `sort=full_name&direction=asc` with `unique_by(full_name) == rows` is the only count I trust.
