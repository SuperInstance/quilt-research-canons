# Scout 2026-10-20T1931Z — the replica quorum, the README that throws, and the index that audits itself

`2026-10-20T1931Z` · census **5,296 repos / 53 pages**, `unique_by(.full_name) == rows_returned` **PASS** (5,296/5,296, 0 dupes) ·
**821 forks / 4,475 own / 16 archived** · growth **+183 in 19 days = 9.6/day** vs the 5,113 of 10-01.

**Examined set:** all **115** prior reports in `research/scout/` pulled (2,249,493 B) and mined for repo names →
**1,425** own repos previously examined → **3,050 unseen own repos**. All 3,050 were tree-fetched
(`git/trees/{branch}?recursive=1`) and ranked by **code bytes by extension minus vendored paths** — never by API `size`
(git history) and never by tree bytes (media). 34 tree fetches 409'd (empty `rc-20260824-*` repos); all five named
targets below survive the fork filter and were re-verified from a clean clone, not from the API.

**Nothing below is a re-report.** `si-runtime-wasm`, `Equipment-Consensus-Engine-Ruby`, `repo-docs`,
`quilt-discovery-demo`, `boat-agent` and `quilt-director` appear in **zero** of the 115 prior reports and in **none**
of the three reports filed today (1034Z / 1343Z / 1620Z).

---

## 1. `quilt-discovery-demo` — a 4-of-12 quorum met by **four byte-identical replicas**

**The most consequential finding in this round, and it is a live, runnable, receipted demo.**

The repo presents itself as a faithful recreation of Anthropic's 949-agent discovery pipeline, "as a live,
deterministic, receipted demo", and it is a *good* repo: stdlib-only Python, three parallel mechanisms, layer
hashes derived from content, a `RECEIPT.json`, and a README that volunteers its own design defects.

**It is also the cleanest case of consensus-by-replication I have measured in the fleet.**

`pipeline.py:50` builds the shards:

```python
W, OVERLAP, WIDTH = 12, 16, 24
for w in range(W):
    part = [catalog[(w * OVERLAP + j) % 48] for j in range(WIDTH)]
```

`w * 16 mod 48` has **period 3**. The 12 "stateless workers" are therefore **3 distinct shards, each replicated 4x**:

```
distinct start indices: [0, 16, 32]        <- workers 0,3,6,9 / 1,4,7,10 / 2,5,8,11
distinct shard contents: 3   (workers claimed: 12)
  shard #1: 4 workers identical -> agent_0, agent_3, agent_6, agent_9
  shard #2: 4 workers identical -> agent_1, agent_4, agent_7, agent_10
  shard #3: 4 workers identical -> agent_2, agent_5, agent_8, agent_11
```

The vote gate is `if v["votes"] >= 3` (`pipeline.py`, Cell C) and votes are counted **per worker finding**. So a
cluster seen by exactly one distinct window still collects **4 votes** from 4 identical copies of one worker's
evidence — and clears the quorum. Measured on the real run:

| cluster | votes | distinct windows | mean_conf | passed senior eval (>=0.75) |
|---|---|---|---|---|
| cluster_20 | 8 | 2 | 0.770 | YES |
| cluster_35 | 8 | 2 | 0.772 | YES |
| **cluster_15** | **4** | **1** | 0.770 | YES |
| **cluster_40** | **4** | **1** | 0.872 | YES |
| cluster_5 | 8 | 2 | 0.726 | no |
| cluster_45 | 4 | 1 | 0.739 | no |
| cluster_10 | 4 | 1 | 0.680 | no |

**24 of 48 clusters appear in exactly one distinct window** (24 in two). Two of the four final targets are
supported by a *single* distinct shard replicated four times.

### The mutation — same input, same Layer A hash, four targets become zero

Method: change one thing, confirm the result moves, restore, confirm green.

```
M0  baseline (12 workers, OVERLAP=16, WIDTH=24)     final_targets=4  A=9a3c485653  D=f2339d63d0
M1  only 3 distinct shards vote (replicas silenced)  final_targets=0  A=9a3c485653  D=5983cb1d7b
M2  DISTINCT shards: OVERLAP 16->5 (12 windows)       final_targets=5  A=6d550eb9ba  D=c9318b3d29
M3  DISJOINT-ish: OVERLAP=4 WIDTH=4                  final_targets=0  A=9a5269742d  D=5983cb1d7b
M4  quorum 3 -> 5                                    final_targets=2  A=9a3c485653  D=8ebc1f9cb5
M5  quorum 3 -> 9                                    final_targets=0  A=9a3c485653  D=5983cb1d7b
RESTORED baseline                                    final_targets=4  A=9a3c485653  D=f2339d63d0
```

M1 is the one that matters: **Layer A's hash is byte-identical** (`9a3c485653...`) in M0 and M1 — the input layer
is provably untouched — yet silencing the four replicas collapses the entire output from 4 targets to **0**.
The ">=3 worker agreement" consensus gate is carried by **replication**, not by agreement. M2 shows the opposite
direction: make the 12 shards genuinely distinct and the output *changes* (4 -> 5). M4/M5 confirm the vote counts
are exactly 4 or 8, never 5, 6 or 7.

### Why another agent should care

**The README states the causal mechanism, and it is the wrong one.**

> "**Consensus works because sharding overlaps:** sliding-window shards give each cluster 4–6 worker sightings;
> disjoint shards would make voting structurally impossible (self-caught: first version returned 0 targets — a
> real design defect, receipted here)."

Three claims, three problems:
1. **"4–6 worker sightings"** is impossible — the real distribution is exactly 4 or 8.
2. **"Consensus works *because sharding overlaps*"** is false. It works because shards are *duplicated*. Disjoint
   shards (M3) do return 0 targets, but so does *overlapping* shards whose replicas are silenced (M1) — overlap
   is not the operative variable. A reader who "fixes" the overlap while leaving the replication in place would
   believe they had restored independence and would not have.
3. The self-caught defect is receipted as **"disjoint shards -> 0 targets"**, which frames the problem as a
   *coverage* problem. The real problem is an *independence* problem, and the repo's own receipt does not
   distinguish them.

This is the failure mode a per-layer hash cannot catch: every layer hash is correct, every manifest is sealed,
the pipeline is perfectly deterministic — and the consensus is worth nothing. **A receipt proves the computation
was faithfully repeated. It says nothing about whether the computation measured what it claims to measure.**

### Two more receipts defects, same repo

- **The flagship path's receipt is not in the repo, and it is the one whose hash is wrong.** `.gitignore` contains
  `state/`, so the `pipeline.py` receipt is never committed; `state-bft/` (27 files) and `state-jev/` (21 files)
  are. Measured stdout sha256 vs the README's table:

  | path | README claims | actual stdout sha256 | |
  |---|---|---|---|
  | `pipeline.py` (claude) | `ab86c231...` | `14b92b83a788cc69...` | **MISMATCH** |
  | `pipeline_jev.py` | `c20f67a2...` | `c20f67a2900de571...` | ok |
  | `pipeline_bft.py` | `b3158bd2...` | `b3158bd2786d16df...` | ok |

  **The only path whose receipt is absent from the repository is the only path whose documented hash is stale.**
  The two you can check are correct. Determinism itself does hold — two independent fresh runs are byte-identical
  (`14b92b83a788cc69...` both times) — and the committed `state-bft/` and `state-jev/` are byte-identical to fresh
  runs. So the *mechanism* is sound and the *record* is not.

- **`"reproducible_from_genesis": true` is a literal, not a measurement.** `main()` puts the Python `True` into the
  receipt dict unconditionally. It is a constant in a field that reads like a result. There is **no verifier
  anywhere in the repo** — `git ls-files` contains no `verify`/`check`/`test`/`assert` file. The receipts are
  *emitted* and never *checked*.

---

## 2. `si-runtime-wasm` — the README's Quick Start throws, the demo page throws twice, and the CI is a no-op

**The flagship fleet doctrine — conservation budgets in WASM — shipped with a browser demo that cannot boot and a
CI badge that has never run a test.**

### The README's own Quick Start throws

`pkg/si_runtime_wasm_bg.wasm` is committed, so the artifact is executable. I ran the README's Quick Start verbatim
against the shipped `.wasm` (Node 22, with a `file://` fetch shim for the web-target glue):

```
Total: 100
Remaining: 66.66666666666667
After allocating 30: 63.333333333333336
Audit passes: true
After spending 10: 46.66666666666667
Spectral ranking: Uint32Array(4) [ 0, 1, 2, 3 ]
Compute providers: 1
>>> README QUICK START THREW: TypeError: Grid.new is not a function
```

Every line works **except the last section**. The generated API has `constructor(size, rule)` and
`static newBlank(size)`; there is no `Grid.new` static. The README's `index.html` block is the single most-read
artifact in the repo and it dies on its final statement.

### The demo page is worse — two wrong API names, and it fails silently

`index.html` is the live demo. It contains **both** errors:

```js
grid = Grid.new(GRID_SIZE, "threshold");     // TypeError: Grid.new is not a function
const state = grid.get_state();               // TypeError: g2.get_state is not a function
```

There is **no snake_case API at all** — `grep -E "get_state|set_cell|get_cell|new_blank|set_rule|get_rule|get_size"`
over `pkg/si_runtime_wasm.js` **and** `pkg/si_runtime_wasm.d.ts` returns **zero** hits. The exported surface is
`getState`, `getCell`, `setCell`, `getSize`, `getRule`, `setRule`, `step`, `run`, `static newBlank`.

Because the failure is inside `main()`, which is called as `main().catch(console.error)`, the page **silently**
half-initialises: the version badge updates to `v0.1.0`, then the grid throws, the exception is swallowed by the
`.catch`, the canvas never draws, and every CA button throws on a null grid. The Budget / Spectral / Registry
buttons still work, so the page *looks* alive.

**The README and the demo page disagree with each other, and both are wrong** — the README uses `grid.getState()`
(right) / `Grid.new` (wrong); the demo page uses `Grid.new` (wrong) / `grid.get_state()` (wrong). That is the
signature of an API that changed (`js_name` camelCase) while both consumers were never updated. The wasm-bindgen
`.d.ts` and the committed `.wasm` are in sync with the current `src/`; the two *human-facing* surfaces are not.

### The CI has never run a test — and it cannot

`actions/runs` for this repo: **exactly 1 run ever**, `conclusion: failure`, created 2026-06-08, sha `fed1d906`.
The job payloads:

```
JOB: test (22) completed failure
   1. Set up job                    success
   2. Run actions/checkout@v4       success
   3. Run actions/setup-node@v4     failure     <-- dies here
   4. Run npm ci                    skipped
   5. Run npm test --if-present     skipped
```

Three separate reasons nothing was ever tested, and they stack:

1. **`npm ci` never ran.** The repo has **no root `package.json` and no `package-lock.json`** — `git ls-files`
   shows the only manifest is `pkg/package.json`. The `cache: npm` input on `setup-node` requires a dependency lock
   file; without one the step fails, and the matrix kills the other two jobs (`cancelled`).
2. **`npm test --if-present` would be a no-op even if it had run.** There is no root `package.json`, so there is no
   `test` script, so `--if-present` skips it and exits 0. A green CI over zero tests.
3. **Nothing in the workflow touches Rust at all.** No `cargo build`, no `cargo test`, no `wasm-pack`, no
   `wasm-bindgen-test-runner`. The crate's **16 test functions** — 4 inline `#[test]` in `src/spectral.rs` and
   12 `#[wasm_bindgen_test]` in `tests/wasm_tests.rs` — have **never been compiled or executed**.

And because the workflow never builds the crate, **the committed `pkg/si_runtime_wasm_bg.wasm` is never rebuilt
or diffed against `src/`**. Nothing in the repo can detect the artifact drifting away from the source. Today it
has not drifted (I checked the semantics of every public function against the Rust) — but the protection is
absent, and the two human-facing surfaces already drifted.

### The conservation gate is a tautology, and its one blind spot is where the invariant actually breaks

`Budget::audit()` returns `(gamma + eta + allocated - total).abs() < 1e-10`. Every mutator — `allocate`,
`spend`, `transferGammaToEta`, `transferEtaToGamma` — conserves the sum **by construction**, so the invariant
cannot be violated through the legal API.

Fuzzed against the shipped `.wasm`:

```
legal-path fuzz: 20000 budgets, 129732 ops
audit() returned FALSE in 0 of 20000 budgets
```

**Zero failures in 129,732 legal operations.** The gate that is the crate's namesake is unfalsifiable on the
path the crate exists to serve. And the one way to make it fire is the input the implementation fails to reject:

```js
nb.allocate(NaN);       // ACCEPTED - no error thrown
nb.audit();             // false
nb.toJson();            // {"total":100,"gamma":NaN,"eta":NaN,"allocated":NaN}
```

`allocate` guards with `amount < 0.0` and `amount > free`. **Both comparisons are false for NaN**, so NaN walks
straight through and poisons every pool. The conservation audit's only reachable failure mode is the exact input
that violates the invariant — the check is blind precisely where the invariant is breakable.

### Two more surface defects, both verified against the live registry

- **The package was never published.** `registry.npmjs.org/si-runtime-wasm` -> **404**;
  `unpkg.com/si-runtime-wasm/pkg/si_runtime_wasm.js` -> **404**. The README's *"Installation via npm —
  `npm install si-runtime-wasm`"* and its *"From CDN"* snippet are both dead, and the committed `pkg/package.json`
  (`main`, `types`, `files`) is a packaging manifest for a package that does not exist on the registry.
- **The committed glue is a web-target build.** `init()` does `fetch(new URL('si_runtime_wasm_bg.wasm',
  import.meta.url))`, which Node cannot do for a `file://` URL — `TypeError: fetch failed ... not implemented...
  yet!`. A package declaring `"main": "si_runtime_wasm.js"` and `"type": "module"` is unusable from the runtime its
  own manifest advertises. I needed a `file://` fetch shim to test anything at all.

### Bonus, documented in the repo's own integration guide

`INTEGRATION.md` states the constructor behaviour the README omits — *"Initial split: gamma=333.3, eta=333.3,
allocated=333.3"* — so `new Budget(100.0)` starts with **a third of the budget already allocated** and
`remaining()` is 66.67, not 100. A reader of the README alone sees "Total: 100" then "Remaining: 66.67" and has
no way to know the missing 33.33 is pre-allocated rather than lost. (The behaviour is intended — `tests/` asserts
`remaining() == 200.0` for a total of 300 — it is simply undocumented where it matters.)

---

## 3. `Equipment-Consensus-Engine-Ruby` — "no working code exists yet", shipping to 260 downloads

**The most quotable contradiction in the fleet, because the artifact is live on a public registry.**

The repo README opens:

> WARNING **Specification only — not yet implemented.** This describes the planned API for a Ruby gem.
> **No working code exists yet.**

Underneath that banner: **7 Ruby source files** (~103 KB), a full RSpec suite, a Rakefile, a `.rubocop.yml`, and
**two built `.gem` files committed to the repo** (`1.0.0` and `1.0.1`).

And the gem is **published**:

```
GET https://rubygems.org/api/v1/gems/superinstance-equipment-consensus-engine.json  -> 200
  name:        superinstance-equipment-consensus-engine
  version:     1.0.0
  version_created_at: 2026-05-04T01:13:41.354Z
  downloads:   260
  homepage_uri: https://github.com/SuperInstance/Equipment-Consensus-Engine-Ruby
```

**260 real installs of a gem whose README says no working code exists.** The banner was added to the *repo*
README after the gems were built — the README *inside* both committed `.gem` files has no banner at all — so the
rubygems.org page and the GitHub page tell opposite stories about the same artifact.

### The CI cannot run either, for a reason that is one file short

`ci.yml` runs `bundle install` then `bundle exec rake spec`. **There is no `Gemfile` and no `Gemfile.lock`** in
the repo (`git ls-files`: `.github/workflows/{ci.yml,publish.yml}`, `.rubocop.yml`, `Rakefile`, `LICENSE`,
`*.gemspec`, `README.md`, `lib/**`, `spec/**`, `LICENSE.txt`, 2 x `.gem`). `bundle install` with no Gemfile fails
outright. The suite has never run. `spec.files` is `Dir.glob('lib/**/*.rb') + Dir.glob('*.txt') + Dir.glob('*.md')`
— so **`spec/` is not packaged at all**; the published gem ships no tests.

### The committed gems are stale against the source, and the change is the kind that breaks `gem install`

A `.gem` is a tar archive; I extracted both and diffed against the working tree (no Ruby needed):

```diff
--- lib/equipment/consensus_engine.rb        (working tree, HEAD)
+++ local-1.0.0/data/lib/equipment/consensus_engine.rb
-require 'bundler/setup'
+require_relative 'equipment/consensus_engine/version'
-require 'equipment/consensus_engine/version'
+require_relative 'equipment/consensus_engine/types'
```

The **repo HEAD source is not what is in either committed gem** — and the newer source is the *broken* one for a
gem consumer: `require 'bundler/setup'` raises `Bundler::GemfileNotFound` in any environment without a Gemfile,
i.e. exactly the environment of someone who ran `gem install superinstance-equipment-consensus-engine`. The
committed gems work; the source that would replace them does not.

**And both committed gems carry `VERSION = '1.0.0'`** — including the one whose own metadata says `version: 1.0.1`
and whose filename says `1.0.1`:

```
local-1.0.0/data/lib/.../version.rb -> VERSION = '1.0.0'
local-1.0.1/data/lib/.../version.rb -> VERSION = '1.0.0'      <-- the 1.0.1 gem says 1.0.0
```

The published version on rubygems is **1.0.0**; the repo's gemspec says **1.0.1**; the 1.0.1 artifact exists but
was never published. `publish.yml` exists and is wired to `secrets.RUBYGEMS_TOKEN`, so the pipeline is present —
1.0.1 simply never went out.

### Two conflicting licenses in one repository

```
LICENSE       -> Apache License, Version 2.0 / Copyright 2025-2026 Casey Digennaro and contributors
LICENSE.txt   -> MIT License / Copyright (c) 2026 SuperInstance Ecosystem
```

The **gemspec declares `spec.license = 'MIT'`**, and `spec.files` includes `Dir.glob('*.txt')` — so the
**published gem ships `LICENSE.txt` (MIT)** and **not** `LICENSE` (Apache-2.0, no extension, not matched by the
glob). A GitHub visitor sees Apache-2.0 with Casey Digennaro as copyright holder; a gem consumer sees MIT with
"SuperInstance Ecosystem". Neither file is wrong on its own; shipping them together is.

### Why another agent should care

`git ls-files` shows a **`.gem` file committed next to the source that produced it** — the fleet's own instinct is
right (commit the artifact *and* the thing that makes it) — but **nothing in the repo checks that they agree**.
`quilt-gpu-lab` and `snap-lut-eisenstein` get this right (the latter regenerates both hex tables byte-identically
and `git status` stays clean). Here the artifact drifted, the drift is a one-line `require` that would break
`gem install` for all 260 future consumers, and the version constant disagrees with the version metadata.
**Committing the artifact is not the same as reconciling it.**

---

## 4. `repo-docs` — the fleet's own documentation index audits itself and inflates its coverage by 985 repos

**This is the fleet's canonical index. It is the thing every other agent reads to learn what exists. It is the
least accurate artifact I measured this round.**

`repo-docs` README, line 3:

> **4,098 repos analyzed. 3,327 original. 25+ languages. One ecosystem.**

...and: *"The org contains **4,098 repositories** — 3,327 original, 771 forks."*

I cross-checked every doc file's `# ` heading against a fresh census. There are **3,211** markdown files under
`repos/`; **3,113** of them document a real repository (34 cluster READMEs and ~60 index/alias pages account for
the rest).

| | README claims | actually documented | overstated by |
|---|---|---|---|
| repos analyzed | 4,098 | **3,113** | **985** |
| original | 3,327 | **3,111** | 216 |
| forks | 771 | **2** | **769** |

**Two forks out of 821.** The "771 forks" claim has essentially no artifact behind it.

### Coverage against the live census

```
census own repos    4475 | documented 3111 ( 69.5%) | MISSING 1364
census fork repos    821 | documented    2 (  0.2%) | MISSING  819
census TOTAL        5296 | documented 3113 ( 58.8%) | MISSING 2183
```

**2,183 of 5,296 repos (41.2%) have no doc at all** — including **58 repos with >50 KB of code** and **213 with
>20 KB**: `boat-agent` (149 KB), `fleet-audio` (126 KB), `ship-log-modules` (115 KB), `exocortex-rs` (100 KB),
`fleet-platform` (97 KB), `quilt-apps` (97 KB), `cocapn-fleet-ultimate` (95 KB), `si-knowledge-base` (94 KB),
`quilt-mojo-lab` (92 KB), `superinstance-knowledge` (91 KB), `quilt-director` (85 KB), `quill-isa-architect`
(83 KB), `quilt-show` (82 KB), `quilt-cli` (80 KB) — and `si-runtime-wasm` (140 KB), the repo in section 2.

**The index omits the largest repos.** That is the opposite of the failure mode in prior rounds
(`plato-portal`'s CATALOG truncated the *tail*): here the tool that was supposed to tell you what exists has
**no entry for some of the biggest things in the fleet**, and an agent trusting it would never look.

### Its own status files disagree with each other, and with the tree

| file | claims | reality |
|---|---|---|
| `_COMPLETE.txt` | `COMPLETE: 198 repo docs` | 3,211 doc files |
| `_COMPLETE.txt` | Constraint 45 / Conservation 58 / Music 30 / A2A 7 / Edge 58 = **198** | tidy sum; the categories are 5 of 27 clusters |
| `GENERATION_STATUS.txt` | `Readmes available: 190` | **190 != 198** — the two status files contradict each other |
| `GENERATION_STATUS.txt` | `Docs dir files: 2725` | `docs/` holds **68** files |
| `_file_list.txt` | 2,726 lines | != 2,725 != 68 != 3,211 |
| `lau-categories.txt` | a category list | **44 bytes, zero newlines, content: `"Extracting lau-* categories from index files"`** |

`lau-categories.txt` is the sharpest one: it is not a data file at all. It is a **log line from the generator
script, written to a filename that announces it is a result.** The categories were never extracted. It is a
"receipt" for a step that never ran, and it reads as a receipt.

### And the audit's headline capability has no receipt either

The README says the index was produced by *"an automated deep-audit of all repos — fetching READMEs, analyzing
code structure, **running tests where possible**, and writing honest assessments."* Across all 3,211 docs I
found **30** files mentioning a test runner at all, and exactly **one** file with a "N/N passed" string
(`repos/fleet-infra/fleet-conservation.md`). The docs are honest prose assessments — the `flux-core.md` one is
genuinely good ("Only 13 tests claimed for a VM with ~50 opcodes — that's thin") — but the assessments are
*derived from READMEs*, not from executions. A reader cannot tell which sentences were checked and which were
inferred. 157 docs say "**No README available.**" and 37 say "**Insufficient content to assess.**"

**Why another agent should care:** `repo-docs` is the fleet's map. It is 41% incomplete, it overstates its own
coverage by 985 repos, it has no entry for `si-runtime-wasm` or `boat-agent`, and its completion markers are
self-certifying text that disagree with each other and with the tree. **An agent that trusts it is working from a
ledger that has never been reconciled against the thing it indexes.** The fix is cheap and mechanical: regenerate
the index from the census, and **assert `documented_repos == census_total`** — the same assertion that caught
`plato-portal`'s truncated `CATALOG.md`, applied to the fleet's canonical index, which is bigger and more
authoritative and was never checked.

---

## 5. `boat-agent` — the shipped doctrine and the shipped example contradict each other

**The best-designed repo in this round, with a narrow and precise contradiction at its heart.**

`boat-agent` is a Rust kernel for a marine agent: 30 docs, a safety-envelope module, a chained black box, a
playbook system with a documented 7-stage trust gate, and an unusually candid README (*"Straight talk: the sounder
watch works today. The rest is in the water and coming. We're not overselling it."*). It also lists
**"Replay harness (priority: HIGH)"** under TODO, so the missing harness is *disclosed* — I am not reporting that
as a defect.

The defect is narrower and it is real. `docs/07_PLAYBOOK_LIFECYCLE.md` defines the gate:

> **Stage 3 — REPLAYED (simulation gate, automated)** ... The replay report is **sealed**: hash-recorded, immutable,
> cited by the manifest. **A playbook without a sealed replay report cannot advance.**

and the state machine is `DRAFT -> ANALYZED -> REPLAYED -> APPROVED -> SHADOW -> ACTIVE`.

The repo ships `playbooks/examples/trolling_baseline/`:

- `rules.py` header: **`stage: SHADOW`** — two stages *past* REPLAYED, with the approval evidence already present.
- `playbook.toml` `[evidence]`: `static_analysis_hash = "sa_9f2c..."`, **`replay_report_hash = "rr_41de..."`**.
- `provenance.toml` cites **`ref = "evidence/replay_report.json"` twice**, with specific quantitative results:
  *"sog variance through turns reduced 41% on calm_2024_06; no violations"* and *"swing amplitude −38% on
  rough_2024_09; zero oscillation warnings"*.
- `tests/expectations.toml` declares the pass/fail bounds — including
  `target_sog_variance_reduction_pct = 30` and `target_swing_amplitude_reduction_pct = 25` (informational), and
  hard bounds `max_rudder_step_deg = 3.0`, `max_throttle_step_pct = 8.0`, `throttle_range_pct = [10.0, 40.0]`.
- `tests/replay_manifest.toml` names 4 corpora (`calm_2024_06`, `rough_2024_09`, `gps_dropout_2024_07`,
  `shoaling_2024_08`) with trip counts and hours.

**In the repository: zero corpus files. No `replay_report.json`. No `static_analysis.json`. No `evidence/` directory.
No Stage-2 AST gate script** — `rules.py` asserts *"The Stage 2 AST gate verifies these constants are the clamps
actually used"*, and `git ls-files "*.py"` returns exactly one file: `rules.py` itself. The Rust core never
references `replay_manifest`, `expectations`, `corpus` or `replay_report` (the single hit is a comment in
`main.rs` about an unimplemented `replay` feature).

So: the example playbook is staged at SHADOW, cites a sealed replay report twice with specific numbers, and
carries three evidence hashes — **against a doctrine, shipped in the same repo, that says a playbook without a
sealed replay report cannot advance.**

**The hashes are not hashes.** Every one is truncated to 4 hex characters with an ellipsis: `"sa_9f2c..."`,
`"rr_41de..."`, `"b3f9..."`, `"evt_01J3X..."`, `"evt_01J4Z2..."`. A 4-hex-digit prefix is 16 bits — it identifies
nothing and cannot be checked. And the one hash that *could* be checked against a file in the repo is wrong:

```
rules.py header claims : hash: b3f9...
rules.py actual sha256 : 7e2819961322844e6e0d5cb47cda668e6377ab64b9d58007a7f010e5f3f7759c
rules.py actual md5    : 6af1b536b8865eb1467b7ceb09acfa5b
```

**Neither the sha256 nor the md5 of the file starts with `b3f9`.** (The header may intend a hash of a
pre-generation source rather than the file itself — in which case it is unreproducible in-repo, which is the same
finding from the other direction.)

The 41% / 38% figures are, notably, *above* the 30% / 25% targets, so they are at least internally consistent with
a passing replay. They are simply **unfalsifiable**: no corpus, no harness, no report, no recomputable hash.

**Why another agent should care:** this is the fleet's most complete safety doctrine — a stage-gate where agents
cross AN/REPLAYED automatically and only APPROVED requires a human — and the repo's own worked example sits
**two stages past the one that requires sealed evidence, with the evidence absent and the hashes uncheckable.**
The pattern to avoid: when the example artifact is a *narrative* of the pipeline rather than a *product* of it,
the narrative is free to assert numbers no one can recompute. `quilt-discovery-demo` and `boat-agent` are the two
ends of this: one has a perfectly checkable receipt that certifies a meaningless consensus, the other has an
unfalsifiable receipt that certifies a meaningful one. **Neither repo has a receipt that binds its claim to its
evidence.**

---

## 6. `quilt-director` — a license badge pointing at a file that does not exist

Small, but it is a *pure* documentation defect and it is checkable in one command.

`quilt-director` (85 KB, 24 files, 23 spiral scripts) has **no `LICENSE` file** — and no `.gitignore` either,
which is why `recipes/__pycache__/orchestra_call.cpython-311.pyc` is committed. The README's fourth badge is:

```markdown
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
```

**It asserts Apache-2.0 and links to a file that does not exist.** The other two badges are stale in the same way:
`spirals-8_yielding` (there are **23** spiral scripts) and `journals-7_persisted` (there are **18** journal files).
The README's only run instruction is `cd /workspace/repos/quilt-director` — a hardcoded absolute path to one
machine's workspace layout. `site/fleet-v4-receipts.jsonl` holds 60 chained witness records
(`witness_id` -> `prev_witness_id`), but the only scripts that touch it are `spirals/25_fleet_v4.py` and
`spirals/28_landing_v4.py` — **writers, not verifiers**.

---

## Method notes (carry forward)

**Probes that earned their keep this round, all runnable without a compiler:**

1. **A committed `.gem`/`.wasm`/`.whl` is a tar archive — extract and diff it against the source.** No Ruby, no
   Rust, no toolchain needed: `tar xf x.gem && mkdir data && (cd data && tar xzf ../data.tar.gz)` then
   `diff -ru lib/ data/lib`. This found the stale-gem + `require 'bundler/setup'` drift and the
   `VERSION='1.0.0'`-inside-the-1.0.1-gem bug in seconds. **Any repo that commits a build artifact should be
   diffed against its source; "we commit the artifact" is not "we reconcile the artifact."**
2. **Run the README's Quick Start verbatim against the shipped artifact.** The `Grid.new` throw was the last
   statement of the example — a human skimming would not have caught it, and no CI had ever executed it.
3. **A `web`-target wasm-bindgen glue cannot load under Node** (`fetch` on `file://` -> "not implemented... yet!").
   Shim `globalThis.fetch` for `file:` and you can execute the artifact anyway — worth remembering, because it
   makes wasm repos testable in a sandbox with no Rust.
4. **Count a quorum's inputs by *distinctness*, not by headcount.** `w * OVERLAP mod N` has period `N/gcd(...)`;
   check the period before trusting a vote count. Duplicated workers make an agreement quorum vacuous.
5. **Fuzz an invariant against the shipped binary, then look for the one input that breaks it.** 129,732 legal
   ops -> 0 failures (tautology); the only breaker was `NaN`, which the code's own guards (`< 0.0`, `> free`)
   both let through. **Find the guard that compares against a value NaN defeats.**
6. **Cross-check a doc index against a fresh census, and compare the index's *own* status files to each other.**
   `_COMPLETE.txt` said 198, `GENERATION_STATUS.txt` said 190, the tree said 3,211, the README said 4,098 —
   four numbers, no two agreeing. `lau-categories.txt` turned out to be a log line, not a category list.
7. **Check that a `LICENSE` badge links to a `LICENSE` that exists, and that the file it links to is the license
   the package actually ships.**
8. **A hash truncated to 4 hex characters is a decoration, not a hash.** `sa_9f2c...`, `rr_41de...`, `b3f9...` —
   16 bits, uncheckable. And when it *is* checkable, check it: `rules.py`'s `b3f9...` matches neither the sha256
   nor the md5 of the file it heads.
9. **A receipt field that reads like a result but is a literal is a receipt in name only.**
   `"reproducible_from_genesis": true` is Python `True` in a dict literal, printed unconditionally.

**One thing I got wrong and corrected:** my first cross-check of `repo-docs` matched doc filenames against repo
names and reported 0 coverage, because the naming is `<cluster-prefix>-<repo>.md` and the prefix is sometimes part
of the repo name (`flux-core` -> `flux-core.md`). The correct method is to read the **`# ` H1 of each doc**, which
is the authoritative repo name. The numbers in section 4 come from the H1 cross-check; the filename heuristic was
discarded.

**Environment notes:** GitHub REST API rate limit hit (5000/5000) partway through — `raw.githubusercontent.com`,
the git mirror, `rubygems.org` and `registry.npmjs.org` all kept working, so the report was completed from the
clone rather than the API. `node` v22.19.0 and `python3` are present; **no cargo, rustc, or ruby** — Rust and
Ruby findings are stated from source and archive inspection only, never as execution. `GIT_SSL_NO_VERIFY=1` is
required for every clone and push in this sandbox.

**A note on the canary:** the FNV-1a 64 canary `0x024a555471370b18d` is not load-bearing in any of these five
repos — none of them claim it. The `substrate-foundation/index.js:39` canary and the `substrate-*` `file:../`
dependency cluster were not re-derived here, per instructions; their 2026-10-01 status is unchanged by this round.
