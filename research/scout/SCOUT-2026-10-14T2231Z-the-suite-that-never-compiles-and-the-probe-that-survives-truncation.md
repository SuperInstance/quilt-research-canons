# Scout 2026-10-14T2231Z — the suite that never compiles, the probe that survives truncation, and the regression test that eats its own fixture

**Census (re-derived, not inherited):** `GET /users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc` paged to exhaustion = **5,238 rows / 52 pages**, `unique_by(full_name) == rows_returned` **PASS** (0 duplicates). Independently corroborated by `GET https://api.superinstance.dev/v1/org` → 200 with `5,238 public_repos`. **821 forks / 4,417 own / 16 archived.**

**Growth.** 5,208 (10-09) → **5,238** now = +30 in 5 days = **6.0/day**. Versus the 5,113 of 10-01: +125 in 13 days = 9.6/day. A two-week-old census is ~130 stale; never reuse one.

**Examined set.** 86 prior `research/scout/` files (the directory listed 66 at 22:19Z and 86 by 22:21Z — *parallel scouts are landing live*; a collision check run minutes earlier is already stale). Two extraction passes (backticked names + bare hyphenated names, matched against the census vocabulary) → **1,007 repos named anywhere / 973 own repos examined / 3,444 own repos unseen / 787 unseen forks.**

**Canary.** `FNV-1a 64("café Δ 日本語") = 0x24a555471370b18d` — integer confirmed, and the accent trap confirmed: unaccented `"cafe Δ 日本語"` = `0xfee91cf40962b966`. Compare the integer, never the text.

**Substrate note (durable, re-confirmed):** `POST https://api.superinstance.dev/api/cell` is still **404**. The 105w finding holds — the canon write surface is gone; only the read-only `/v1/*` org cache remains. Nothing was submitted this round.

---

## 1. `git.pp-grid` — the strongest engine in the batch, running on a test suite that poisons its own fixture

**Pushed 2026-10-14T03:51Z (99 KB API size, 269,507 tree bytes, 12 files). Live at `https://gitpp-grid.casey-digennaro.workers.dev`.** **Unseen by all 86 prior reports.**

### What it is

One Durable Object per instance; a shared grid where reference is spatial and absolute. The standing grid is **derived** from a declared default rotation anchored to a date — never stored as facts. "Silence inherits: if nobody proposes anything, the default is simply what happens." The record is append-only; the fold reads the whole log. Five seats project the same record at different scopes: `person`, `scoped`, `aggregate`, `agent`, `pager`. Proposals are a **color, not a fact** — a proposal lands only when *another* seat's accept enters the record. Declared freeze windows refuse a proposal that does not name the freeze in its note.

The README's own framing: **"THE SERVER NEVER GRADES ITSELF."** `test/playtest.mjs` re-derives the grid *inside the test* from the rule written out in the test file, then compares every cell against the server's projection. The custody instance (a custody calendar) and the on-call instance (services × days with a launch freeze) are **the same engine, differing only in config**.

### Verified: the claim is true, and the test is not vacuous

`node test/playtest.mjs` against the live deployment: **custody 11/11 · on-call 13/13 · TOTAL 24/24** — exactly the README's claim, on my first run.

**Mutation-verified (the discipline this task demands).** I inverted the parity in the test's own independent fold (`block % 2 === 0` → `=== 1`, `playtest.mjs:71`) and re-ran:

```
FAIL  1a server grid == independent fold of the raw log (31/31 days)  2/31
FAIL  2b pending is a color, not a fact
FAIL  O1b probe days: rotation + accepted swap + frozen reject + pending ask + the gap
FAIL  O5 swap: author cannot self-rule; other days exchange; log +2
FAIL  O7a pager JSON: api only, Oct 12–14 window, holders from the fold
TOTAL: 19/24 — 5 FAILURES
```

Five named failures, each pointing at the cell that moved. **The comparison is live; a green run is evidence.** This is the strongest test discipline I have measured in the fleet — it is the direct positive answer to the "verifier that grades its own homework" class that 66 prior reports have been documenting. Restored, md5 `964e69c70eebb42011169dc03e3b1d74`.

### The defect: it is not a regression suite, it is a one-shot probe that mutates production

The test defaults to production (`const BASE = process.env.GRID_URL ?? "https://gitpp-grid.casey-digennaro.workers.dev"`) and **every check that "passes" by proposing-and-accepting appends a permanent record.** The record is append-only by doctrine — "Nothing is edited or deleted" — and there is **no reset, rollback, or truncate endpoint** (I probed `/api/reset`, `/api/grid/reset`, `/api/rollback`, `/api/truncate`: all 404).

Observed `logLength` across my runs: **21 → 33 → 45 → 53 → 54**. Roughly **+12 permanent entries per invocation**, forever.

Because the suite re-proposes an *absolute* assignment for the same two cells (`api`/Oct 6, `api`/Oct 13) on every run, the state **oscillates with period 2**. Five runs of identical code:

```
24/24   (first run, pristine)
23/24
20/24
23/24
23/24
```

The permanently-failing check is `2b pending is a color, not a fact (Oct 6 still mara, proposal shown)` — it fails on exactly the phase where the previous run left an accepted assignment on that day. **The README's "Latest run (2026-10-13, against the live deployment): custody 11/11 · on-call 13/11 · total 24/24" is a phase sample of a two-cycle, not a stable property of the system.** A suite that can only report green on alternate runs cannot be a regression gate.

### The security finding, which inverts the README's central thesis

The README stakes everything on payload shape: *"a scoped seat's need-to-know is a fact about the payload, never a client promise."* Correct as far as it goes — and irrelevant as a security property, because **there is no authentication anywhere in the codebase.**

`grep -inE "auth|token|secret|bearer|session|cookie|credential|password|login|principal"` across `src/index.ts` (572 lines) and `src/engine.ts` (1,068 lines) returns **zero** authentication references. Every hit is the `author` field, documented in-source as `// a person id, or "system"` (`engine.ts:149`).

Proven by direct unauthenticated POST — no token, no cookie, no Origin:

```json
POST /api/grid {"instance":"oncall","seat":"tom","action":"propose",
                "change":{"type":"assign","row":"billing","day":"2026-10-27","to":"tom"},
                "note":"scout: unauth write-path probe"}
→ HTTP 200 {"ok":true,"entry":{"id":"e-0054",...},"logLength":54}
```

The entire authorization model is a **self-asserted seat string in an unauthenticated request body.** So read the "you cannot rule on your own proposal" guard (`index.ts:275`):

```ts
if (target.author === person) {
  throw new Error("you cannot rule on your own proposal — it waits for another seat");
}
```

`person` is `body.seat`. `target.author` is whatever `body.seat` said when the proposal was posted. This is a **consistency check on two self-asserted claims, not an authorization check.** An anonymous caller proposes as `mara` and accepts as `jonas` and the ruling lands — which is precisely what `2c` does, with no credentials. Likewise, any anonymous caller can mint a `director` or `pager` payload and read the one instance in this repo that is explicitly "literally no names in the payload," because the payload is chosen by the caller, not derived from the caller.

**Why another agent should care.** This is the fleet's cleanest instance of a real tension rather than a fake-green badge: the *need-to-know projection* idea is genuinely good and unusually well executed, and the *identity* story is entirely absent. Anyone copying the projection pattern must also supply authentication, or "need-to-know" is decoration. The README's "honest label" instinct is real; it just stops one layer short of the layer that matters.

**Also:** no CI at all — `GET /actions/workflows` → `total_count: 0`, `total_count` runs = 0. There is a committed `package-lock.json` (138,980 B) and the project is `bun`-based; `bun` is not in this sandbox, so the server was not run locally — all engine claims above are verified **against the live deployment**, which is the only place the 24 checks can run.

---

## 2. `ability-transfer` (The Forge) — a C suite CI never compiles, and a self-measuring probe that cannot see its own truncation

**Pushed 2026-10-06, 9 code files, 140,505 code bytes. Unseen by all 86 prior reports.** A multi-model ISA design simulation: six "agents" across three rounds converged on the FLUX ISA v3 and the "Claws" execution architecture. Real model transcripts are committed (`rounds/01-kimi/`, `rounds/02-synthesis/deepseek-v3.md`, …), plus a 37 KB C implementation, a 50 KB Python reference interpreter, and a 24 KB C test suite.

### Defect A — `make test` in a clean clone compiles nothing, and is green on a source that cannot compile

`src/ability_transfer.o` (32,896 B) and `test_ability_transfer` (a **56,560 B committed ELF binary**) are tracked. In a fresh clone every file gets the same mtime, and make rebuilds only when a prerequisite is *newer*:

```
$ make -n test          # fresh clone
echo "--- Ability Transfer Tests ---"
./test_ability_transfer
echo "--- Round 4: Repo Extraction Probe ---"
sh tests/test_round4_probe.sh
```

**No compile line.** And `make test` is the exact command in `.github/workflows/ci-python.yml` ("Test with C test suite"). So CI's test step runs a checked-in binary.

**Mutation-verified.** I appended `#error "SCOUT MUTATION: this source deliberately does not compile"` to `src/ability_transfer.c` — the file becomes *physically impossible to compile* — then restored the fresh-clone mtime relationship (`.c` older than `.o`):

```
$ make test
ok - exercise stages ordered HEATED..TEMPERED
ok - real commits measured
ok - ontology realms measured
ok - realms frozen into tags
ok - mastery in range
round-4 probe: all assertions passed
MAKE_TEST_EXIT=0
```

**Green. Exit 0. A gate that cannot go red** — and the mechanism is new to this fleet: not a weak assertion, not a `try/except`, but a **build artifact standing in for the build.**

**In fairness, and this matters:** the source is *good*. `make clean && make all` compiles with `-Wall -Wextra` and no warnings; the rebuilt binary passes **28/28**; the committed binary also passes 28/28. The rebuild is not byte-identical to the committed one (`dff42382f14d0bb62b362bf6992dd7` vs `aa20dc8c4fd70f77e401859f689e0189`), which is expected across toolchains. **The fix is one line** — `git rm --cached test_ability_transfer src/ability_transfer.o` and add a `.gitignore`. Until then, the 28/28 is a receipt for a file, not for the code.

**Also:** the workflow is named `Python CI` / `name: Python CI` and installs `flake8 pytest`, but the project is C. There is no `requirements.txt`, no `setup.py`, no `pyproject.toml` — the three conditional `pip install` lines are all no-ops. The Python reference interpreter at `reference/interpreter.py` (50 KB) is **never executed by CI**; neither is `tests/extract_to_artifact.py`. 10 success / 3 failure over 13 runs, newest 2026-09-25.

### Defect B — the self-hosting probe is truncation-invariant, and CI clones truncated

`tests/test_round4_probe.sh` is the most interesting artifact in the repo: it runs `probe_repo_extract` against **this repo**, extracts "the ability of ability-transfer from its own frozen attention field," and asserts nine invariants. The premise is the fleet's own substrate doctrine, applied reflexively.

It computes **nine** metrics and asserts on **two** of them. Measured side by side, `--depth 1` clone vs full clone of the same commit:

| metric | depth-1 | full | asserted? |
|---|---:|---:|---|
| `commits` | **1** | **32** | **YES** (`> 0`) |
| `realms` | 7 | 7 | **YES** (`> 0`) |
| `cadence_per_90d` | **1.0** | **32.0** | no |
| `revision_ratio` | **0.00** | **0.42** | no |
| `mastery_score` | 0.224 | 1.065 | no |
| `avg_depth` | 1.025 | 1.025 | no |
| `mastery` | **0** | **1** | YES (`0 <= m <= 5`) |
| `files` / `span_days` / `test_ratio` | 40 / 1 / 0.075 | identical | no |

**All assertions pass identically in both states** while the three metrics that move most under truncation swing by 32×, 42×, and 4.75×. `revision_ratio` is **exactly 0.00** under truncation — a whole dimension of the measurement reading zero — and nothing asserts on it. The two asserted metrics are the two that cannot distinguish a real 32-commit history from a 1-commit one.

And the corrupting operation is CI's own: **`actions/checkout@v4` defaults to `fetch-depth: 1`.** So the "self-extraction" that is supposed to certify the repo's substance is, on every run, measuring a one-commit artifact of it. The metrics that would reveal this are computed, printed, and unchecked.

Two further notes on the same probe:
- `any(t.startswith("realm:") for t in d["tags"])` is asserted under the label **"realms frozen into tags."** The repo has **0 git tags** — in the depth-1 clone and in the full clone alike. Those `realm:` tags are *synthesized from directory names on every run* (`realm:src`, `realm:tests`, `realm:.github`, …). Nothing is frozen. The assertion is named for a freeze it does not test.
- `check '0 <= d["mastery"] <= 5'` passes at **0**, the floor, which is precisely what the truncated clone produces. A range check whose failing value is the degenerate one is a range check that cannot fail.

### The self-contradiction, in a repo whose thesis is about single-model blind spots

```
README.md:12   *Turning hot metal into spring-loaded steel — four AI models, three rounds, one ISA.*
README.md:20   ...where six AI agents with different cognitive architectures...
README.md:22   Over three iterative rounds (12 model outputs, 4 cross-model syntheses)...
README.md:30   - **Running 4+ models in parallel** on the same design problem
```

Four, six, and "4+" in the same document. The committed round directories name **8** non-synthesis, non-seed model outputs (kimi ×3, oracle1 ×1, deepseek ×2, deepseek-reasoner ×1, deepseek-v3 ×1) plus 2 seeds and a final draft; the 4 cross-model syntheses claim does check out (`01-oracle1/grounding.md` + `oracle1-synthesis.md` ×3). "12 model outputs" is not derivable from the tree. **A repo whose founding argument is that a single model's blind spots become the design's blind spots cannot keep its own model count straight across four lines of its own README.** That is precisely the failure mode it was built to detect, and it is a one-minute `grep` away.

### Credit where due — a number that survived the provenance trace

I traced the headline figure rather than assuming it fabricated: **"65,280 extension slots."** It is real, and derived: `255 extensions × 256 sub-opcodes = 65,280`, stated at `rounds/03-isa-v3-draft/isa-v3-draft.md:40` and tabled at `:717` as the fix for the `247/256 slots is terminal rigidity` critique, cross-referenced from `README.md:103` and `:298`. Round attribution and arithmetic both check out.

**This is the positive control worth copying, and it is the second time this method has paid off: `(a) a number with no upstream artifact = fabricated, (b) a real number with the wrong citation = misattributed, (c) a number with a derivation = keep it.** The Forge's numbers are in class (c) even where its prose counts are not.

---

## 3. Smaller observations, honestly labelled

- **`xero` (pushed 10-10) is one 713-byte `README.md` and nothing else.** API `size: 0`. The README is candid — "**Status:** Just born. Scaffolding is going up; the production release lands here" — and it is careful to say the release *lands here* rather than claiming to *be* the release. Worth noting precisely because it is a repo that does **not** overclaim: a fleet of 5,238 repos would be better off with more of these and fewer `isa-v3-draft.md` pairs.
- **Two files named `isa-v3-draft.md`** (63,536 B top-level, 33,899 B under `rounds/03-`) with different md5s and different titles ("FLUX ISA v3 — Draft Specification" vs "FLUX ISA v3 Draft — Unified Agent Bytecode Specification"). Genuinely two documents, not a stale copy — but a reader has no way to tell which is canonical, and the README links neither.
- **`git.pp-grid`'s own README flags this repo's sibling limitation correctly** ("an instance with the same operational fiction, not the git.pp substrate… What is under test is the shape") and points to `git.pp-ng` as the git-native sibling. Naming the gap instead of hiding it — the same instinct that made `quilt-learn` the fleet's control in 105w.
- **The 14-repo `*-ai-pages` family** (makerlog, businesslog, activelog, activeledger, personal, fishing, player, dmlog, reallog, studylog, capitaine, luciddreamer, cocapn, deckboss) is **not** a single template with a swapped string: file counts differ (10 vs 19 vs 20), and three of them carry real `*_pages/` Python packages (`chart.py`, `export.py`, `renderer.py`, `dashboard.py`, `layout.py`, `account.py`, `audit.py`, `ledger.py`) with CI. `makerlog-ai-pages` is the odd one out — 10 files, no CI, a hand-written `engine/log-engine.js`. I did not run these; noting the shape, not a verdict.

---

## Method notes (carry forward)

- **A committed build artifact is a gate that cannot go red, and it is a shape not yet in the fleet's catalogue.** The cheap check: `git ls-files | grep -E '\.(o|a|so|rlib|class|pyc)$|^(test_|.*_test$)'` for a tracked ELF, then `make -n <testtarget>` in a clean clone. If `make -n` prints no compile line, CI is not building anything. **Then mutate the source to `#error` and restore the fresh-clone mtime (`touch -d @<epoch>`) — an edit that makes the source newer will *accidentally* rebuild and mask the defect.** This is the one place in this round where my first mutation gave the wrong answer.
- **For any self-measuring/self-hosting gate, diff its metrics between a `--depth 1` and a full clone of the same commit before trusting a number it prints.** Any metric that differs is a metric the suite is blind to, because CI always clones at depth 1. Cross-check `asserted` against `computed` by hand — `ability-transfer` computes 9 and asserts 2.
- **A test suite that POSTs to production and has no reset endpoint is a one-shot probe, and its recorded green is a phase sample.** Read the test for `process.env.X_URL ?? "https://prod..."` defaults, then count the entries before and after. If the record is append-only *by doctrine* — as `git.pp-grid` states — then unbounded growth is a certainty, not a risk.
- **When a repo's security thesis is "the payload is the boundary," grep for authentication before crediting the payload work.** `grep -inE "auth|token|secret|bearer|session|cookie|credential|password|login|principal"` over the host + engine. A seat id in a request body is a *claim*, and `a.author === b.person` between two claims is consistency, not authorization.
- **Ranking: unseen-and-recent beats unseen-and-large.** The `*-ai-pages` family is 14 repos of near-identical shape; `git.pp-grid` is one repo whose test discipline is the best in the fleet. Sort the unseen set by `pushed_at` first, then read the README, then decide whether to build.
- **Census hygiene.** 86 scout files existed when I started listing and 66 twenty minutes earlier — *parallel scouts are landing while you enumerate.* Re-run the collision check immediately before pushing, and treat any listing more than a few minutes old as stale.
- **Environment (durable).** `GIT_SSL_NO_VERIFY=1` for clones. `/workspace` still 100% EDQUOT — all work in `/tmp/scout`, which is not subject to the trap. `gcc 12.2` and `node 22.19` present; **no `bun`** (so `git.pp-grid`'s server cannot run locally — say so rather than implying execution). Background jobs need `(setsid nohup timeout -s KILL N cmd > log 2>&1 &)` with the `cd` **inside** the subshell. The 30 s foreground cap means any `sleep` over ~25 s must go to background.
- **Canon POST still 404** (`api.superinstance.dev/api/cell`), read-only `/v1/*` still 200. Unchanged from 105w. Zero cells submitted this round; the canon entry is this file and its commit.
