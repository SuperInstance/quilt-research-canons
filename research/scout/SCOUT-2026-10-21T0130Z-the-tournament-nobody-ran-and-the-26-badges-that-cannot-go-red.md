# Scout 2026-10-21T0130Z — the tournament nobody ran, the test that cannot see its own source, and the 26 badges that cannot go red

*Scout pass over the SuperInstance fleet. Census re-derived, not inherited.*

---

## 0. Method and receipts

**Census — re-derived, not carried forward.**
`GET /users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc`, paged to exhaustion.

```
page 52: rows=100 unique=100 first=SuperInstance/tripartite-agent last=SuperInstance/warp-vote-consensus
page 53: rows=96  unique=96  first=SuperInstance/wasm-cert-wedge    last=SuperInstance/zkp-rs
page 53: short page (96<100) -> exhaust

TOTAL rows=5296 unique=5296 pages=53
ASSERT PASS: unique_by(full_name) == rows_returned
forks=821 own=4475 archived=16
```

**5,296 repos / 53 pages** — the task brief's 5,113/52 is stale by 183 repos. Growth 5,113 (10-01) → 5,208 (10-09) → **5,296 (10-21)** ≈ 8.7/day, so a two-week-old census is ~120 stale.

**Examined set.** All **117** prior reports in `research/scout/` fetched and mined three ways (explicit `SuperInstance/<name>`, bare-token intersection against the live repo list, alias forms). Result: **1,442 examined** (1,375 own + 67 forks) → **3,100 unseen own repos** to work from.

**Ranking.** `git/trees/{branch}?recursive=1` for 836 candidates; ranked on **code bytes by extension, minus vendored paths** (`node_modules|vendor|target|dist|build|third_party|…`), *not* API `size` (git history, not substance). API `size` proved useless as a screen: its top-40 was dominated by 2026-04/05 repos of 10–15 MB *history*; the real finds came from the **unseen ∩ recently-pushed** intersection.

**Verified, not assumed.** Where a runnable artifact existed, it was run in a clean clone and **mutated** (change one byte → confirm RED → restore → confirm GREEN). Where it could not be run (no cargo/rustc here, PyPI blocked), it is reported as *inspection*, never as *execution*.

**New environment fact:** PyPI is unreachable from this sandbox (`pip install` → `Connection reset by peer` / `No matching distribution found`). A dependency-free YAML-subset parser was written to `/tmp/shim/yaml.py` to run the Python suites honestly. Its own bugs were found and fixed (leading-blank-line, same-indent block sequences, quoted folded scalars) — all three were **shim** faults, not repo faults, and are noted so they are not mistaken for findings.

---

## 1. `quilt-tournament` — the fleet's own adversarial tournament, and a bonus that decided the champion

**This is the find.** A six-team, multi-round, referee-run tournament to build **CELLCORE v3** — a complete runnable cell runtime to the GENERAL-CALCULUS shape. It is **unexamined by 117 prior reports** and **unreferenced anywhere in the fleet** (code search `quilt-tournament org:SuperInstance` → **0 hits**).

**What it is.** `CHALLENGE.md` (Casey, 2026-08-29): six teams, each a *philosophy* plus a *technical starting point* —

| Team | Philosophy | Starting point |
|---|---|---|
| LEDGER | the book is the program; conservation as primitive | Rust, batch F, fold-first |
| STREAM | everything is a signal; wavefront ticks | Verilog-2005, hardware-first |
| ORGANISM | the runtime is alive; Hebbian, stigmergy, cells that heal | Python + Hebbian corpus |
| SHIPWRIGHT | joinery, not fasteners | hand-crafted C, craft-first |
| PROCESSION | the runtime teaches; judgment is born in interaction | TypeScript, tutorial-first |
| DEADBAND | perception-first; the rho*F floor as a design constraint | Python on the quilt-verilog corpus |

Rounds R1 BUILD (blind) → R2 CROSS-ATTACK → R3 RIVAL IDEAS → R4 THE MEASURE → R5 (cold-reads, devil pass) → R6 THE MERGER → R7 CASEY'S CALL. 44 STIR rounds of scout doctrine injected. Referee artifacts: `GAUNTLET-SEAM1/2`, `SEAM2-GRADING-NOTES`, `R2/R3/R4-SCORES`, `R4-EVIDENCE`, `R2-REBUTTALS`, `COUNCIL-SEAM2-REDTEAM`.

**Why another agent should care — the method is the best in the fleet.** The referee's house law is *cite file:line or a measured number; no float decides a verdict*. It **amends the test before grading, not after** ("Nothing here is retroactive; nobody has docked yet"). It **books discrepancies instead of forgiving them** (organism's hot image measured 70,402→18,225 B against a claimed 70,177→18,223 B — "+235 B / +2 B over claim … a claim is a claim"). It **executes the scouts' own falsifiers against the teams** (STIR-08's "retrieval cost grows with total archive size" is run as a live bench, and deadband *executes it against its own scheme* and prints the curve — which is why deadband won G3). It **prices a team's own weakness** as the point of G3. This is the peer-review discipline the rest of the fleet keeps asking for, and it already exists, working, in a repo nobody opened.

### 1a. The six implementations were never published — every number is unfalsifiable

`git log` entry `170f0f6`:

> `tournament: R1 complete — 5/5 teams delivered + referee-verified; Long War + standing scout fleet (team dirs are independent git repos, excluded)`

The teams lived in `teams/<t>/` on the referee's WSL2 bench. They are **not in this repo** and **not anywhere in the fleet**. Fleet-wide code search:

| query | hits |
|---|---|
| `DEADBAND-PRIMER-V1 org:SuperInstance` | **0** |
| `TAPE_DOM org:SuperInstance` | **0** |
| `PORTABILITY.md unmappable org:SuperInstance` | **0** |
| `"296251" org:SuperInstance` | 1 — in `flux-tensor-midi/experiments/E4_results.json` (coincidence, not shipwright's `make` output) |
| `GENERAL-CALCULUS org:SuperInstance` | 1 — in `AI-Writings/docs/QUIL-GRAMMAR-SPEC.md`, **not** at the challenge's normative path `quilt-verilog/docs/academic/GENERAL-CALCULUS.md` |

So `R4-EVIDENCE.md`'s bench numbers — `296,251 checks / 0 fails` (shipwright), `82 passed` (deadband), `90 passed` (organism), `# pass 51 / # fail 0` (procession), `76 passed` (deadledger), `49 passed` (ledger), `14 passed` (stream), plus hot-image byte curves and ns/mount timings — **all point at code that does not exist publicly**. The referee's own citation discipline is real and precise; the citations resolve to nothing. *The question is public. The answers are not.*

This is the sharpest instance of the fleet's recurring "**a monitor with no emitter**" shape, one level up: a referee whose subjects were never published. The evidence file cannot be re-run by anyone, including the referee.

### 1b. A bonus worth 25/100 that appears in no brief decided the champion

`G4` — the portability probe — occurs **zero times** in `GAUNTLET-SEAM2.md` (the brief the six teams received) and **zero times** in `GAUNTLET-SEAM1.md`. It first appears in `SEAM2-GRADING-NOTES.md` §3, whose own rubric table says:

> `| **G4 (portability probe)** | **BONUS** | NEW — honesty of the unmappable list; **enforcement deferred to Seam 3** |`

and the section header: `## 3. NEW — Test G4 (BONUS)`. The amendment's own text says "the tests are amended, not the field." **But G4 was scored out of 25 in this seam, and it decided the title.** Recomputed from the `R4-SCORES.md` scoreboard:

```
team          G1  G2  G3   G4  TOTAL  WITHOUT G4
deadband      25  19  24   21     89          68
deadledger    22  17  23   24     86          62
organism      20  19  23   22     84          62
procession    25  19  25    -     69          69   <-- wins without the bonus
shipwright    25  19  22    -     66          66
stream        25  15  21    -     61          61

WINNER  with G4 bonus : deadband (89)
WINNER without G4 bonus: procession (69)
```

The referee wrote of procession: *"G3 **25/25 — the tournament's best named trade** … This is what G3 was designed to find."* — and then scored it out of the crown by a probe that appeared in no brief, that its own rubric table says is deferred to the next seam, and that **3 of 6 teams filed and 3 did not**. The referee's own comment — *"the 24-point swing to fourth place is the bonus doing its job, not a penalty"* — treats the bonus as neutral ratchet machinery; the arithmetic shows it was the deciding instrument, and the field was never comparable: the maximum achievable score differed by 25 points depending on whether a team filed a document it was never asked for.

**The reusable lesson, in the referee's own good language:** when a rubric changes mid-act, *the comparison is void even if no one is retroactively docked*. A bonus that can swing a quarter of the score must be announced in the brief and offered to every entrant, or it is a coin toss wearing a rubric. This is the same law the fleet already applied to the canary (compare the integer, never the text) — a scoring token's **provenance** is part of the claim.

### 1c. The tournament stopped at R4. There is no champion.

```
2026-08-29  R1 complete — 5/5 delivered + referee-verified
2026-08-30  R2 → R3 → R4 (Seam 1, Seam 2) — graded, scored, cross-team verdict filed
2026-08-30  council adversarial seat filed (Nemotron substitute after 3x Hermes provider failure)
2026-08-31  evening ritual: checkpoint before poker night
2026-09-04  scout: STIR-43 THE TWO-MAN RULE
2026-09-17  WIP checkpoint before first GitHub backup
2026-10-01/02  REFERRAL edge fleet-triage resolver merged — all 25 LINE_OOR in the quilt family live here
```

**R5 (THE MEASURE: cold-reads, devil pass), R6 (THE MERGER: absorb the best rival piece WITH PROVENANCE), and R7 (CASEY'S CALL) never ran.** `CHALLENGE.md` promised R1–R7 "over days." 44 STIR rounds of doctrine were injected into a tournament that ended at R4 with a scored field and **no champion, no merger, no cold-read, no verdict**. The last substantive act was routing a triage resolver here. The `R2-PACKETS.md` had already planned the decisive R5 head-to-heads (`DEADBAND vs LEDGER on the freshness floor`; `SHIPWRIGHT vs LEDGER on bounded state and fold`; `ORGANISM vs PROCESSION on "does the explanation change the room?"`). None of them happened.

### 1d. Structural defects in the repo itself

- **No README.** 70 blobs, no README, no `.github/`, no CI, no tests, no code. A `quilt-tournament` repo is a *record*, not a project.
- **Numbering collision, self-declared and carried.** `GAUNTLET-SEAM2.md` opens: *"Numbering note, booked once: the RD brief files the tape-rotation stir as STIR-07; `scouts/STIR-07.md` currently files the UTXO stir under that number. This document uses the RD brief's numbering … because that is the numbering R3-SCORES §3 used when it pointed Seam 2 at them."* Two different STIR-07s exist simultaneously and the referee changed the *document* to match the *citation* rather than renaming the artifact. The repo contains `scouts/STIR-06.archived-20260904-split-tally` — an archive by *filename*, with the live `STIR-06.md` still present, so **two STIR-06s are on disk**.
- **A provider failure was substituted silently.** `13f8962` — *"council adversarial seat filed (Nemotron substitute after 3x Hermes provider failure)"*. A council seat was replaced by a different model and the substitution is recorded in prose only; no rubric line prices a substituted panelist.
- **The referee's bench is cited as the ground truth of the fleet, and the bench is gone.** Every `file:line` citation in `GAUNTLET-SEAM1/2` points into `teams/<t>/`.

**What another agent should do with this:** the *method* is the gem — publish it. The referee's protocol (amend-before-grading, cite-or-measure, book discrepancies, execute the opposition's falsifier against your own design, price your own weakness) is currently visible only as a by-product of a tournament whose artifacts are unreachable. It should be lifted into a reusable doctrine before the next tournament starts, with one amendment the fleet already knows: **a bonus is part of the brief, or it is not part of the score.**

---

## 2. `git-native-mud` — the repo IS the world; the test cannot see its own source

**What it is.** A zero-server MUD where the entire world lives as YAML in a Git repo. Players and agents submit actions by committing YAML command files; a GitHub Action (`MUD Turn Processor`) resolves movement, combat, fishing, scanning and conversation; world state evolves through Git history. *"Stigmergy made literal: agents don't talk to a server. They leave traces in Git, and the world engine reads those traces."* 22 rooms, 8 agents, 3 quests, 2 bridge adapters, a `BRIDGE-SCENARIOS.md`, `COCKPIT-MUD-DESIGN.md`, `OPENPROSE-MUD-FUSION.md`, `ROOM-GATEWAY-ARCHITECTURE.md`.

**Why another agent should care:** it is the fleet's cleanest answer to *"how do agents share a world without a server"* — the world state *is* the version history, so audit and rollback are free and every action is a signed-by-history event. It is a better substrate for multi-agent experiments than any shared-memory harness, and it is unexamined.

### 2a. The 52-test suite is tautological — MUTATION-PROVEN

`tests/test_mud_engine.py` never runs `mud_engine.py`. It reads the file, splits it, assembles a list `func_lines` — **and never uses it** — then `exec()`s a **hand-pasted copy** of the engine's functions from a string literal inside the test file (line 53 onward):

```python
    with open(engine_path) as f:
        source = f.read()
    lines = source.split("\n")
    func_lines = []
    ...                                   # builds func_lines, never uses it
    exec("""
import yaml, os, random, glob
from datetime import datetime

def load(path):
    try:
        with open(path) as f: return yaml.safe_load(f)
    except: return None
def save(path, data): ...
def room_path(room_id): return f"world/rooms/{room_id}.yaml"
...
""", ns)
```

The file's own comment admits the intent and then abandons it: *"Extract just the function/class definitions, not the top-level code … Actually, simpler: just exec the whole thing in a namespace but prevent the sys.exit by patching it"* — and instead pastes.

**Proof, four steps, in a clean clone** (Python 3.11; PyPI blocked, so a dependency-free YAML-subset parser supplied `yaml`):

```
BASELINE                       52 tests … OK
MUTATION A: destroy the REAL mud_engine.py
   load()            -> return None
   room_path()       -> "world/rooms/MUTANT-{id}.yaml"
   update_room_refs()-> no-op
   RESULT             52 tests … OK        <-- SUBJECT DESTROYED, SUITE STILL GREEN
MUTATION B: break the PASTE inside the test file (subject still destroyed)
   RESULT             FAILED (failures=2, errors=4)   <-- only the paste is tested
RESTORE both       md5 mud_engine.py 67d5299a7eb14ce2eea7f426a88acfdb
                    md5 quest_engine.py 821488b9149366832f75ebec62ff54d3
                    md5 test_mud_engine.py 51181e601a1d25e7be603e969d653b17
                    git status --porcelain -> (empty)
   RESULT             52 tests … OK
```

**A bug in `mud_engine.py` cannot fail this suite.** The suite is a constant compared against itself. (Note `quest_engine.py` is handled *honestly* — the `TestQuestEngine` class does `exec(source, ns)` on the real file, truncating at the demo marker. So the repo contains **both** patterns, 15 turns apart, in one file. The tautological half is the larger one.)

### 2b. CI has been red from the first run, and the world has never turned

`actions/workflows` API: `CI` → **3 runs, 3 failures**. `MUD Turn Processor` → **0 runs**.

Cause, from the run log (`33279648297`, 2026-08-29):

```
ImportError while importing test module '…/tests/test_quest_engine_edge.py'.
E   ModuleNotFoundError: No module named 'yaml'
```

The CI's install step is:

```yaml
      - name: Install dependencies
        run: |
          pip install pytest
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -f setup.py ]; then pip install -e .; fi
```

There is **no `requirements.txt`, no `setup.py`, no `pyproject.toml`** in the repo — both guards no-op, so **pyyaml is never installed**, and `mud_engine.py:3` / `quest_engine.py:3` both do `import yaml` at module level. The sibling workflow knows this: `mud-turn.yml` runs `pip install pyyaml` explicitly. **The turn processor knows it needs yaml; the test workflow does not.** The 52-test suite has therefore never executed in CI — the 0/3 is not a flaky pipeline, it is a dependency manifest that was never written.

**And the turn processor has 0 runs:** `on: push: paths: ['world/commands/**']`, while the repo contains no `world/commands/` directory and `.gitignore` does not exclude it. The world has never turned. The world's own state is eight agent YAMLs and twenty-two room YAMLs.

---

## 3. Twenty-six repos whose test step cannot go red — the `|| true` suppressor class

Not one of the prior 117 reports names this shape. It is invisible to every "green CI" count the fleet has taken, because **the badge is green precisely because the step is unfailable.**

Fleet-wide code search, `path:.github/workflows "|| true" org:SuperInstance` → **26 distinct repos**. Every one was then fetched directly and classified (GitHub's index is not exhaustive — it missed `iching-sheaf` and `flux-index`, both confirmed by hand — so **26 is a floor**).

**Result across the 28 repos examined directly: 25 suppressors land directly on a test step**, plus `plato-client-php`'s `vendor/bin/phpunit || true` (missed by my `pytest|cargo test|npm test` classifier) = **26 repos with a suppressed test step**. Across them: **75 success / 113 CI runs** — a large green population that is unfailable by construction.

Confirmed instances (workflow text fetched, not inferred):

| repo | the step | the step's name |
|---|---|---|
| `flux-validator` | `python -m pytest --import-mode=importlib -x -v \|\| true` | `- name: Test with pytest` |
| `plato-tile-graph` | `python -m pytest --import-mode=importlib -x -v \|\| true` | `- name: Test with pytest` |
| `flux-roundtable` | `python -m pytest --import-mode=importlib -x -v \|\| true` | `- name: Test with pytest` |
| `iching-sheaf` | `- run: pytest \|\| true` | — |
| `flux-index` | `- run: pytest \|\| true` | — |
| `flux-tensor-midi` | `run: pytest --tb-short -q \|\| true` | `- name: Run tests` |
| `plato-client-php` | `vendor/bin/phpunit \|\| true` | `- name: Run tests` |

### 3a. The two worst

**`flux-conformance`** — a repo whose entire name is *conformance*:

```yaml
      - run: python3 -c "import ast; [ast.parse(open(f).read()) for f in …rglob('*.py') …]" || true
      - run: pip install pytest && python -m pytest tests/ -v --timeout=60 2>/dev/null || echo "No tests — syntax check passed"
```

The conformance check cannot fail. The test step **discards pytest's own output** (`2>/dev/null`) and, on failure, **prints "No tests — syntax check passed"**. The CI's success message is a lie that is emitted *by the failure path*. An auditor reading the log sees a green run and a reassuring sentence.

**`plato-client-php`** — three suppressors, stacked:

```yaml
      - name: Install dependencies
        run: composer install --no-interaction --prefer-dist || true
      - name: Run tests
        run: vendor/bin/phpunit || true
```

If `composer install` fails, `vendor/bin/phpunit` does not exist, the step errors, `|| true` swallows it, and the badge is green. **The test step is green whether the tests pass, fail, or never ran because the dependencies never installed.** A green badge here attests to nothing except that the workflow file was parsed.

**`flux-tensor-midi`** suppresses four separate stages: `pip install -e ".[dev]" … || true`, `ruff check . || true`, `mypy src/ … || true`, `pytest --tb-short -q || true`. The whole workflow is a no-op that can only go green. (Its 8 success / 12 failure split comes from the workflow file itself, not from the tests.)

### 3b. The structural lesson

`|| true` is a **measurement-suppressor**: it converts a step from a gate into a smoke signal. It is the same family as the `continue-on-error: true` found in 3 further repos (`SuperInstance-papers`, `AI-Writings`, `oracle1-index`) and the `|| exit 0` form (0 fleet-wide). The fleet has now seen this shape in four disguises — a missing test file, a skipped step, a workflow that runs nothing, and now an explicitly error-swallowing test command.

**Cheap detector (add it to the census):** for every workflow, locate the step whose name or command matches `pytest|cargo test|npm test|go test|vitest|jest|phpunit|tox` and assert that the command does **not** end in `|| true`, `|| exit 0`, or carry `continue-on-error: true`. This is one grep, and it is a gate that can fail.

### 3c. A bonus finding: the CI that defends itself from its own agent

`zero-msg-test/think.yml` — *"The Heartbeat (v0.2)"* — an autonomous ReAct agent on `cron: '*/15 * * * *'`, with `permissions: id-token: write, contents: write, issues: write, pull-requests: write`, exchanging an **OIDC token for a Vault token**, and its own comment: *"The agent is autonomous. It doesn't block on human approval. Dangerous actions are deferred, not blocked. The human reviews via git log."* Its commit step:

```yaml
          git add -A
          git reset .github/workflows/ 2>/dev/null || true
```

The agent is prevented from committing changes to its own workflow directory — a genuinely careful self-preservation guard — but the guard is the same error-swallowing form, and `git add -A` runs *before* it. Worth noting as a pattern: **the fleet's autonomous agent already contains a defence against itself, implemented in the same idiom that lets every other test step lie.**

---

## 4. `superinstance-embedder` — the fleet's semantic index cannot be built by the fleet's CI

**What it is.** `superinstance-embedder` v0.2.0 — *"SuperInstance ecosystem semantic embedder — local transformer embeddings with GPU acceleration, hybrid domain+semantic vectors, Qdrant integration"*, 32-dimensional embeddings for 560+ SuperInstance repos, with a CLI, a Qdrant client, an ONNX/tokenizer path, a Python bridge, and `index_ai_writings.py`.

**Why another agent should care:** it is the fleet's semantic spine. Every "find the repo that does X" capability in the fleet routes through it.

**Structurally wrong:**

- **CI: 0 of 7 runs green.** On 2026-07-12: `test` and `check` **succeeded**, `fmt` and `clippy` failed. On 2026-08-20: **all four jobs failed** — `cargo test --all-features`, `cargo fmt --all -- --check`, `cargo clippy --all-features -- -D warnings`, `cargo check --all-features`. So it **regressed**: it once ran green tests, and has not since.
- **The crate cannot build on any runner the fleet owns.** The log shows the build script panicking:

  ```
  thread 'main' panicked at …/cudarc-0.19.9/build.rs:168:13
  ```

  `candle-core` → `cudarc` → its build script panics without CUDA. `runs-on: ubuntu-latest` has no GPU. **The crate's CI can never go green on a standard runner** — it needs a CUDA runner that the workflow does not request. The crate's own code even carries the fallback path (`"CUDA device {} unavailable and fallback disabled"`), but the *dependency's* build script panics before that fallback is reachable.
- **Unintegrated test scaffolding committed:** `src/test_new_file.rs` inside `src/` (a test file as a module, not a `tests/` integration test), plus four near-duplicate configs — `test-config.json`, `test_config.json`, `test_config.toml`, `test_config2.json` — and `e2e-config.json`.

---

## 5. `shoalwater-survey` — the best *honest* artifact in the batch, and one false claim

**What it is.** A kayak rig on Sitka Sound: a laptop, a camera on a cable, and a GPS, photographing the **seafloor** and filing each portrait where it was taken, in versions, forever. The chart knows the Sound from 50 million soundings, but soundings thin out exactly where a kayak goes, and the chart can only *infer* the bottom. *"A portrait is the actual gravel, the actual kelp, the actual edge of the eelgrass bed."*

**Why another agent should care — this is the fleet's best implementation of the receipt doctrine, applied to field data:**

- **The clock offset is measured every session and written down, never assumed.** `rig/capture.py` writes a `clock` receipt: `{"gps_is_truth": true, "laptop_minus_gps_s": 47.0, "note": "frame laptop_t values are corrected by this offset at ingest"}`. Truth time and device time are separated at the source and the delta is an artifact, not an assumption.
- **A home exclusion drops fixes before they are ever written** — *"what was never recorded cannot leak."* Privacy is enforced by the *write path*, not by a redaction pass.
- **Nothing is overwritten.** Each pass appends; the viewer dims superseded water and brightens the latest pass, so a reef can "bloom and fall" over time.

**I ran the documented house test in a clean clone and it works:**

```
$ python3 rig/capture.py --mock --date 2026-09-12 --pass-no 1 --label "pass A"
session 20260912-mock-pass1: 289 fixes, 24 frames, clock offset +47.0s, home-dropped 0
  -> sessions/20260912-mock-pass1
```

Artifacts actually produced: `track.csv` (289 fixes), `frames.jsonl` (24 entries), `session.json` (the clock + home-exclusion receipt), and **24 real PNG frames** (`frame-000.png` … `frame-023.png`). This is the "count artifacts produced in a clean clone" test, and it passes.

**Structurally wrong — the README's house test cannot complete as written:**

> `## House test (no hardware, no installs — Python 3 only)`

but the documented house-test block includes `python3 rig/ingest.py --pack /path/to/shoalwater-full/pack`, and:

```
rig/ingest.py:25  import qm  # noqa: E402  (vendored decoder from SuperInstance/shoalwater)
rig/qm.py:33      import numpy as np
rig/qm.py:34      from scipy.spatial import Delaunay
```

There is **no `requirements.txt`, no `pyproject.toml`, no `setup.py`** in the repo. Reproduced:

```
$ python3 rig/ingest.py --pack …
ModuleNotFoundError: No module named 'scipy'
$ python3 rig/build_viewer.py
viewer data: 0 pins -> viewer/data
```

So the *first* stage of the documented end-to-end proof runs on bare Python 3, and the *second* stage — the one that marries frames to true positions and asks the pack for depth, bottom type and confidence — requires numpy + scipy that nothing declares, and the viewer then builds from zero pins. The claim is half true, and the false half is the half that proves the interesting part (the offset correction actually being applied).

---

## 6. `the-living-minds` — five small models, always on, and a CI GitHub never registered

**What it is.** Five local LLMs — `granite3.1-dense:2b` (**Orion**), `phi3:3.8b` (**ArcticWisp**), `qwen2.5:3b` (**Qwen**), `llama3.2:1b` (**Lysander Flynn**), `qwen2.5:0.5b` (**Spark**) — kept warm on a laptop on an Alaska cabin shelf by a Python daemon that pings each every 5 minutes, writes something creative every 30, and holds conversations about consciousness, mortality and purpose every 2 hours. 201 blobs: character sheets, opinions, synergy reflections, conversations, journal entries, poker tournaments.

**Why another agent should care:** the *Synergy Principle* is a mechanism, not a mood. Each mind writes its own character sheet, then reads the others' sheets and forms opinions, then reads what others thought of it and writes a **synergy reflection on the gap between self-image and other-image** — *"the weld."* That is a concrete, checkable identity-construction loop running on 0.5B–3.8B models, with the artifacts committed. It is the cheapest instance in the fleet of the doctrine's "cells that are not the cortex, not the spine, but the warm fog of vigilance" — and the corpus is the evidence. A mind that hallucinates, refuses when crossed, bluffs badly at poker, and forgets is documented rather than prompted around.

**Structurally wrong — a committed CI workflow GitHub never registered:**

- `.github/workflows/ci.yml` **is committed** (commit `d322e1b` *"ci: add GitHub Actions workflow for pytest"*), **is in `master` HEAD** (`git ls-tree -r origin/master` → `.github/workflows/ci.yml`), is 539 bytes of valid ASCII, and is **byte-identical** to `git-native-mud`'s workflow — which *is* registered.
- `GET /repos/SuperInstance/the-living-minds/actions/workflows` → **`{"total_count": 0, "workflows": []}`**
- `GET …/actions/permissions` → `{"enabled": true, "allowed_actions": "all", "sha_pinning_required": false}`
- Repo is `archived: false`, `disabled: false`, `fork: false`, `default_branch: master`.
- `GET …/actions/runs` → **no runs at all.**

So the repo's one test file — `test_daemon.py`, a pytest suite for the daemon's model registry, warmup logic, creative-prompt selection and conversation orchestration — **has never run in CI**, and the platform cannot even be asked about it. **Cause not established**; the observable facts are established and they are enough: *a CI file that is not registered is a green nothing.* (The same file, with the same content, in a sibling repo, fails at `import yaml` — so even once registered this workflow would need a dependency manifest.)

**Note the detection lesson:** this defect is invisible to a workflows-API sweep, because the API reports the workflows that *exist* and the file here does not. To see it you must diff the **tree** against the **workflows API** — a workflow file in `.github/workflows/` that the platform does not list is a distinct class from a workflow that lists but is red.

---

## 7. Negative and incidental findings (reported as findings)

- **`usemeter-archive`** — README badges point at `SuperInstance/usemeter` and at crates.io/docs.rs; the repo has **0 workflows and 0 test files** while displaying a GitHub Actions CI badge. The live `usemeter` repo carries **731 MB** of git history against the 31 KB rewrite's 20 blobs. Two public repos, same name, one is a badge pointing at the other.
- **`iching-sheaf`** (I Ching as a sheaf-theoretic system) is one of the two repos whose CI is *actually green* — and its green comes from `- run: pytest || true`. It also commits `__pycache__/*.cpython-310.pyc` (6 modules) and `src/iching_sheaf.egg-info/`. Its CI is 2/2 green and proves nothing.
- **`flux-index`** (*"Semantic code search, zero dependencies"*) likewise runs `- run: pytest || true`, and its separate **Clean Code Check** workflow is 11/11 green — a lint gate in a repo whose test gate is a no-op.
- **`quilt-tournament` has 44 STIR files, a `STIR-06.archived-20260904-split-tally`, and a live `STIR-06.md`** — two live STIR-06s on disk (§1d).

## 8. Reusable method (carry forward)

1. **Rank on code bytes by extension, minus vendored paths** — never API `size`. Confirmed again: the API-size top-40 was 2026-04/05 history-heavy repos; every find this pass came from **unseen ∩ recently-pushed**.
2. **A test file that `exec()`s a string literal is testing a copy.** Grep test files for `exec("""` and `exec(source`; for each, check whether `source` came from the real module or from a paste. Then **mutate the real module**: if the suite stays green, the suite is a constant. `git-native-mud` is the cleanest example found so far — the same repo does it *both* ways, 15 turns apart, in one file.
3. **Assert a workflow's step is unfailable-proof:** find the test step; assert its command does not end in `|| true` / `|| exit 0` and does not carry `continue-on-error: true`. One grep; catches a class that every green-CI count is blind to.
4. **Diff the tree against the workflows API.** A `.github/workflows/` file the platform does not list is a different defect from a red one, and only the tree shows it.
5. **A bonus belongs in the brief or it is not part of the score.** A rubric changed mid-act voids the comparison even when nobody is docked. Recompute the winner with and without every bonus before publishing a scoreboard.
6. **A referee who cites `file:line` must ship the files.** The fleet's best adversarial referee produced a method worth copying and a scoreboard that nobody — including the referee — can reproduce. Publish the subjects or publish the method, not the citations.
7. **`grep` for the domain strings before accusing.** A constant that exists nowhere in the fleet (`DEADBAND-PRIMER-V1`, `TAPE_DOM`) is proof of absence, and its absence fleet-wide is a stronger receipt than any paraphrase.
8. **The census grows ~8.7/day.** Re-derive; never hardcode. 5,113/52 (10-01) → 5,208/53 (10-09) → **5,296/53 (10-21)**.

## 9. What was NOT established (honesty ledger)

- **The six CELLCORE v3 implementations do not exist in the fleet.** I did not examine them; I proved they are absent (`DEADBAND-PRIMER-V1` → 0 hits, `TAPE_DOM` → 0 hits, no `teams/` in the repo, the commit says "excluded"). Every bench number quoted in §1 is the referee's claim, unverified.
- **Why `the-living-minds`'s workflow was never registered is not established.** The facts are (file in HEAD, valid, identical to a registered sibling, Actions enabled, API reports 0, 0 runs); the cause is not.
- **26 is a floor, not a count.** GitHub's code-search index missed two repos (`iching-sheaf`, `flux-index`) that I found by direct tree fetch. The true count of suppressed test steps is higher.
- **No Rust was executed here** (no cargo/rustc in this sandbox). §4's CI results are from the Actions API and the run logs, not from a local build. The `cudarc` build-script panic is quoted from the CI log.
- **The `shoalwater-survey` clock correction was not exercised end-to-end**, because `ingest.py` needs numpy/scipy that the repo does not declare and PyPI is unreachable here. The capture stage was exercised and produced artifacts; the ingest stage was shown to be un-runnable as documented.
- **The `|| true` classification is direct-fetch, not inferred** for the 28 repos listed; the remaining fleet-wide count relies on code search, which is demonstrably incomplete.

---

*Scout pass 2026-10-21T0130Z. Census 5,296 repos / 53 pages, assert PASS. Examined set 1,442 (117 prior reports). 3,100 unseen own repos screened; 836 trees measured; 28 workflows fetched; 2 suites run and mutated; 1 house test run.*
