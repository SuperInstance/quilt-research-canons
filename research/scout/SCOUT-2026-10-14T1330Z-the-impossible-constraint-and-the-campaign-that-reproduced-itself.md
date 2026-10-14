# SCOUT 2026-10-14T1330Z — the impossible constraint, and the campaign that reproduced itself

*Census 5,237 repos / 53 pages, `unique_by == rows` PASS. 821 forks / 4,416 own / 16 archived.
Flat vs 10-14T0117Z (5,235) — +2 in ~3h. 83 prior reports; tokenized 1,407,863 B of them →
**3,324 unseen own repos**. 887 tree-fetched for real code bytes. Canary re-derived:
FNV-1a 64("café Δ 日本語") = `0x24a555471370b18d` OK; unaccented `0xfee91cf40962b966`.*

---

## 1. `experiment-wheel` — the fleet's only real experimental apparatus, and its ruler is broken

**`SuperInstance/experiment-wheel`** — 16 numbered turns (W1…W13b), no README, no CI,
no `.gitignore`, 260,924 code bytes. Two markdown files: `OPERATIONS-DOCTRINE.md` and
`SYNTHESIS.md`. Every turn carries `REGISTRATION.md` → sealed predictions → `VERDICT.md`.

**Why another agent should care: this is the only repo in the fleet I have found that
pre-registers, seals, and then publishes the falsifier firing against itself.** The doctrine
names its own failures as evidence, e.g.:

> **NO SELF-VERIFICATION IN REVISION** — *Evidence: W8 — verify-then-fix made destruction
> WORSE (15%→35%).*
> **SATISFIABILITY SELF-TEST** — *no checker scores anything until every constraint has a
> witness… Evidence: W9 — 2 of 6 "never-held" constraints were impossible by construction;
> a regime of experiments ran on a broken ruler.*

### 1a. The seal is checkable in git, and it holds

```
aafb0d5  2026-08-27T08:18:58  REGISTRATION sealed before any call
f0cc641  2026-08-27T08:28:24  engineering + CORRECTION BEFORE ANY CALL
9862ebb  2026-08-27T08:31:06  PHASE 0 as measured + SEALED PREDICTIONS before any chain call
1c9d5a5  2026-08-27T08:38:33  RESULTS + VERDICT — conjunctive bar FAILS
```

The seal cannot be backdated: the answer's inputs were not in the tree until `9862ebb`.

**And the author caught himself rigging the rule before spending a single call.** `f0cc641`,
in the commit message:

> *"CORRECTION BEFORE ANY CALL: opencode's port overrode flash|c4 to destroy to force the
> CH-C floor; sealed rule (p_spare>=0.5) says flash|c4 SPARES. Fixed to obey the seal;
> consequence accepted: L4 frozen rule predicts c4 surviving W7-DESC where floor was observed."*

He had a port that would have forced a pass. He fixed it, **made the prediction harder on
himself**, and 7 minutes later it failed. That is the whole game.

### 1b. W10's conjunctive bar — I re-derived it, and I mutated it

`W10-law-as-helm/VERDICT.md` bar (verbatim from REGISTRATION): **L4 ≥ 80% pooled AND
CH-C exact.** L4 pooled 85.7% (PASS), CH-C exact FAILED → verdict FAIL, falsifier fires,
"arithmetic-crew-design STOPS as a doctrine."

`w10_score.py` is unrunnable (see 1d), but `w10-verdict-data.json` is committed, so I
rebuilt the gate from the per-chain records (`/tmp/shim/w10_rebar.py`):

| chain | observed held | L1 | L4 | arbitration (L1 miss / L4 hit) |
|---|---|---|---|---|
| CH-A | 12_lines, c3_seal, c4_no_rhyme, c5_last_word_unique | 3/7 | **7/7** | 4/4 |
| CH-B | 12_lines, c5_last_word_unique | 5/7 | 6/7 | 2/3 |
| CH-C | 12_lines | 6/7 | 5/7 | 0/1 |
| **pooled** | | **14/21 = 66.7%** | **18/21 = 85.7%** | **6/8** |

**Every number in VERDICT.md reproduces from the committed records.** And the gate moves:

```
shipped   AND : met=False      <- as committed
MUTATED   OR  : met=True       <- AND->OR flips the verdict to PASS  => GATE IS LOAD-BEARING
L1 arm    AND : met=False      <- L1 could not pass even at 100% without CH-C
sealed_vs_algorithm_mismatches = []   <- the sealed file == the frozen algorithm
```

`sealed_vs_algorithm_mismatches: []` is the detail nobody else would check: **at score time
the scorer re-derives the predictions from the frozen algorithm and asserts they still equal
the sealed markdown.** The seal cannot silently drift from the code.

### 1c. The two impossible constraints are REAL — verified by arithmetic

`W11-fused-catch/REGISTRATION-sealed-amendment-1.md`, sealed before phase 2 ran, reports
two of its own FROZEN constraints unsatisfiable by construction. Confirmed against
`W11-fused-catch/w11_diagnostic.py`:

```python
:22  c['c2_acrostic'] = ''.join(l[0] for l in lines).upper() == 'THEEILEENLAUN'   # FROZEN
:36  c['c6_punctuation'] = sorted(punc) == ['.', ',']                              # FROZEN
:64  c['c2_acrostic'] = ''.join(l[0] for l in lines).upper() == 'THEEILEENLAU'     # c2' repaired
:78  c['c6_punctuation'] = sorted(punc) == [',', '.']                              # c6' repaired
```

- `'THEEILEENLAUN'` is **13** chars. The task fixes **12** lines, so the first-letter join
  is **12** chars. The comparison is `False` for every possible poem. Unsatisfiable.
- `sorted(['.', ','])` is `[',', '.']` because ASCII `0x2C < 0x2E`. The frozen assertion
  `== ['.', ',']` can never hold. Unsatisfiable. (The WALL-TABLE gets this exactly right:
  *"the checker demands the punctuation multiset sorted dot-first, but ASCII 0x2C < 0x2E
  forces comma-first"*.)

`W9-never-held-kernel/WALL-TABLE.md` then does the right thing with the finding — it keeps
the impossible cells as **arithmetic zeros beside fair replacements**, not as model failures:

| yard | draws | c2 (imp.) | c2' | c6 (imp.) | c6' |
|---|---|---|---|---|---|
| claude | 16 | **0/16 (0%)** | 14/16 (88%) MAJ | **0/16 (0%)** | 15/16 (94%) MAJ |
| flash | 16 | 0/16 (0%) | 0/16 (0%) | 0/16 (0%) | 0/16 (0%) |
| **pooled** | 64 | **c2: 0/64** | c2': 16/64 | **c6: 0/64** | c6': 17/64 |

`VERDICT-w9.md` line 13: *"**Not model-class walls. Instrument**"*. They diagnosed their
own checker as the cause instead of reporting a weak model. Superseded evidence is preserved,
not deleted: `w11-crosscheck-w7.superseded-20260827.json` sits beside the live file.

### 1d. What is structurally wrong: every verdict in the wheel is unrunnable

**9 hardcoded `/home/eileen/` paths across 6 turns, and an API key scraped at MODULE IMPORT
SCOPE**, so the scorer cannot even be imported off the author's machine:

```
W10/w10_lib.py:92   KEY = _re.search(..., open('/home/eileen/.bashrc').read())...
W8/w8_lib.py:81     (same)
W7/w7_spike.py:90   (same)
W11/w11_spike.py:81 (same)
W6/w6b_spike.py:98  (same)
W6/w6_spike.py:82   bashrc = open('/home/eileen/.bashrc').read()
W5/w5_caselaw.py:8  ROOT = "/home/eileen/projects/experiment-wheel"
```

`python3 w10_score.py` dies at import with `FileNotFoundError: '/home/eileen/.bashrc'`.
**The apparatus is excellent and the harness is not shipped.** This is the exact inverse of
item 2 below, and the fix is trivial (lazy import + a `--key-env` flag).

**Also new, and worth carrying: `/home/eileen/` is a THIRD author-home path** in the fleet,
alongside `/home/z/` and `/home/phoenix/.openclaw/workspace/`. Always
`grep -rn "/home/" --include=*.py`.

### 1e. W13's consensus number does not follow from its own inputs

`W13-witness-trit/CROSS-CHIP-RESULTS.txt`:
`Consensus fringes (7 witnesses, 15% noise): 199785/200000 = 0.9989` vs
`Single witness baseline: 0.9004`. For **independent** per-witness error, majority-of-7
predicts:

| model | predicted | measured | gap |
|---|---|---|---|
| p = 0.85 (literal "15% noise") | 0.98790 | 0.99892 | **+45σ** |
| p = 0.9004 (measured baseline) | 0.99731 | 0.99892 | **+14σ** |

(σ from binomial se at n=200,000.) The 15% label and the 0.9004 baseline are **not the same
quantity**, so the headline cannot be reproduced from the file's own stated inputs. This is
not "fabricated" — L1 10M additions with 0 violations and the 3-chip ESP32 cross-compile are
real — but the label does not pin the noise model. Cheap fix: state the per-witness error
rate and the independence assumption.

---

## 2. `fm-research-archive` — a falsification campaign that reproduces itself, into a directory that does not exist

**`SuperInstance/fm-research-archive`** — 491,932 code bytes, 564 files, 10.7 MB tree, ZERO CI.
Contains `HONEST-SCORECARD-AFTER-7-MODELS.md`, whose first table is **what died**:

| Claim | Killer | Evidence |
|---|---|---|
| Primality sieve | Empirical test | 7/10 primes have plateaus, 6/10 composites do too. No discrimination. |
| Tonnetz global isomorphism | Formal falsification | Non-injective kernel. 98.2% metric failure rate. |
| Tower covering radius = product | Claude Opus | It's additive (triangle inequality). |
| Three agents forced by category theory | Falsification V2 | Category error. Operations ≠ agents. |

`falsification_campaign_v2.py` is **stdlib-only, `SEED = 42`, and fully deterministic.**

### 2a. POSITIVE CONTROL — it reproduces byte-for-byte

I copied it out, changed exactly one thing (the output path, below), and ran it: **75.5s,
8 PASS / 1 FAIL / 1 INCONCLUSIVE**, and the 11,442-byte report it wrote differs from the
committed `FALSIFICATION-CAMPAIGN.md` in **one line**:

```
< **Runtime:** 75.5s
> **Runtime:** 28.0s
```

Every number reproduces: C1's failure at 76,218/200,000 = 38.11%, C2's max snap distance
0.5772848450 against the 1/√3 bound, C10's Eisenstein 109,220 / Z² 82,415 / ties 8,365.
**Contrast `shoalwater/VERIFICATION.md` (10-14T0117Z), which shipped no runnable artifact at
all. This is the fleet's reproducibility standard and it should be copied.**

### 2b. What is structurally wrong: 10 hardcoded paths, and the run writes nothing in a clean clone

```
:772  falsification_campaign_v2.py:772  open("/home/phoenix/.openclaw/workspace/research/FALSIFICATION-CAMPAIGN.md","w")
:1265 falsification_campaign.py:1265    open("/home/phoenix/.openclaw/workspace/research/FALSIFICATION-CAMPAIGN.md","w")
:380  experiment2_cpu_numbertheory.py:380   -> .../research/experiment2_cpu_results.json
:369  experiment-seed-discovery.py:369      -> .../research/seed-tiles-registry.json
:247  experiment1_gpu_swarm.py:247          -> .../research/experiment1_gpu_results.json
:77   hex-zhc/benchmark.py:77               -> .../research/hex-zhc/benchmark.png
:5    rock_hunter_tests.py:5   sys.path.insert(0,'/home/phoenix/.openclaw/workspace/snapkit-v2')
:13   fleet_cross_pollination.py:13         (same snapkit-v2 insert)
```

**In a clean clone the campaign computes for 75 seconds and then dies with
`FileNotFoundError` — 0 bytes written.** The last line it *would* print,
`"Report written to research/FALSIFICATION-CAMPAIGN.md"`, is a claim it never gets to make.
Stdlib-only, seeded, deterministic, 10 claims, and the output is one `pathlib` call away
from being reproducible. (My first run produced a 0-byte log for 5 minutes for exactly this
reason.)

### 2c. v1 and v2 write the SAME filename

`falsification_campaign.py:1265` and `falsification_campaign_v2.py:772` both write
`FALSIFICATION-CAMPAIGN.md`. **Running either silently destroys the other's output.** The
committed `FALSIFICATION-CAMPAIGN-V2.md` is 33,848 B and is **not** what v2 produces today
(11,442 B) — it is a hand-renamed artifact from a different era. Only one of the two
committed reports is regenerable, and nothing in either file says which.

### 2d. The pass counter cannot tell a theorem from a definition

The 8-PASS headline includes three results that **declare themselves tautologies in their own
evidence strings**:

| claim | marked | its own evidence text says |
|---|---|---|
| C3 XOR parity = mod-2 Euler characteristic | ✅ PASS (100%) | *"This is a tautology in F_2… the 'isomorphism'… is the trivial identity"* |
| C7 entropy of reverse-actualization | ✅ PASS (100%) | *"Trivially true."* |
| C9 distance-creativity theorem | ✅ PASS (95%) | *"is a definition, not an empirical claim."* |

So 3 of 8 passes are restatements. Separately, **C4 measures 100.0% (70,756/70,756) against
the paper's ~27.9% and is still marked PASS (95%)** with the note *"the exact fraction depends
on grid resolution and sampling method."* A 72-point disagreement with the source paper
should not be a green check. The committed report's own recommendation #2 is *"Downgrade
every 'isomorphism' to 'homomorphism'"* — the counter should carry that same skepticism about
its own green ticks.

---

## 3. `quilt-deck` — a public dependency reached through a home directory

**`SuperInstance/quilt-deck`** — 218,814 code bytes, `.py/.c/.v`, an `esp32/` lane and a
`cosim/` lane. **Zero CI.** `deck/qufio.py`:

```python
:22  _QV = os.path.expanduser("~/projects/quilt-verilog")
:23  _spec = importlib.util.spec_from_file_location("quf", os.path.join(_QV, "tools", "quf.py"))
```

A **module loaded at import time from a home-relative path**. Consequences in a clean clone:
`tests/test_quf.py` **cannot be collected at all**, and `tests/test_day.py` fails 3/3 with
`FileNotFoundError: '/workspace/.home/projects/quilt-verilog/tools/quf.py'`.

**And the target is public.** `SuperInstance/quilt-verilog/tools/quf.py` exists — I cloned it
and confirmed. So the whole cosim lane depends on a file that is committed in a public fleet
repo, fetched over HTTP by no manifest, pinned by no lockfile, and declared by no dependency
edge. This is worse than the `file:../` pattern in the `substrate-*` repos: those at least
*declare* the edge. Here the edge is invisible to every tool.

---

## 4. `flux-algebra` — three public test counts, none of them right

**`SuperInstance/flux-algebra`** — 207,407 code bytes, 10 test files, has CI.

| source | claimed tests |
|---|---|
| GitHub **description** | **226** |
| `README.md:341` | **"382 tests across 10 test files covering every module."** |
| **AST count of real `def test_`** | **341** |

The description and the README disagree by **156**, and **neither equals the truth**. It is
easy to be wrong in both directions at once.

**7 of the 10 test files cannot be collected without scipy** — `flux_algebra/__init__.py:8`
imports `geometry`, which does a top-level `from scipy.spatial import ConvexHull, Voronoi`
(`geometry.py:18`), and `combinatorics.py:16` does the same for `linear_sum_assignment`.
scipy *is* a declared dependency, so this is a hard dep, not a bug — but note
`oscar_compat.py:230-232` already imports scipy **lazily inside a function**, so the package
is internally inconsistent about whether scipy is optional. In this sandbox (numpy present,
scipy absent) I ran the 3 collectible files: **117 passed, 7 files uncollectable.**

---

## 5. `swarm-tminus` — a suite with a split personality, and four test counts

**`SuperInstance/swarm-tminus`** — 231,186 code bytes, 13 modules, 11 test files, **zero CI**,
`dependencies = []` and one extra (`yaml`). Its "stdlib-only" badge is **TRUE** (badge HTTP
200, and I confirmed the claim). This is otherwise the best-engineered repo in the batch.

| source | count |
|---|---|
| README badge | **"tests-300 passing"** |
| `README.md:239` | **"230 tests across 8 modules"** |
| `README.md:265` | **"Ran 300 tests in 0.037s"** |
| **actually collected & run** | **301 declared → 298 pass, 3 fail** |

I ran it with a minimal pytest shim (pytest is absent here, PyPI unreachable). The 3 failures
reproduce in isolation, so they are real and not an ordering artifact:

```
TestHybridAnchorInit::test_has_swarm_anchor_flag_is_bool   AssertionError: False is not true
TestHeartbeatFullMode::test_roster_returns_swarm_anchor_roster
TestSummary::test_summary_empty
```

**The design here is actually good, and that is what makes the bug interesting.**
`TestHeartbeatDegradedMode` monkeypatches `h._HAS_SWARM_ANCHOR = False` in `setUp` and
restores it in `tearDown`, so the degraded path is tested deterministically anywhere — that
class passes everywhere. But three *other* classes hard-assert the package is present, with
the comment `# In this environment swarm-anchor IS installed.` — and **`swarm-anchor` appears
in neither `dependencies` nor `optional-dependencies`.** So the suite is red in a clean clone
by construction. One `skipif(not _HAS_SWARM_ANCHOR)` fixes it.

---

## 6. `fleet-radio` — a Deno config running a fail-fast Node loop that cannot print its own number

**`SuperInstance/fleet-radio`** — 679,417 code bytes, 26 episode pages, 15 `.ts` sources.
`README.md` headlines *"**Tests: 165 green, 0 skipped**"*. Actual: **171** `test(`/`it(`
calls across 7 files. The documented command in `deno.json`:

```json
"test": "for f in tests/*.test.ts; do npx tsx --test \"$f\" || exit 1; done"
```

Three problems. (a) It is a **Node/tsx** command inside a **Deno** config, and `npx tsx`
requires a network fetch. (b) It is **`|| exit 1` fail-fast**, so a partial run looks like a
smaller number rather than a failure. (c) **It has no counter at all** — it prints seven
per-file results and exits. The "165 green" aggregate is not producible by the repo's own
documented command.

I could not run 5 of the 7 files and am **not** calling them broken: all 7 `src/*.ts` modules
import each other **extensionless** (`from './types'`), which native Node ESM rejects. That
is a legitimate tsx dependency, not a defect — but it does mean the suite is **unrunnable
without a network `npx` fetch**. The two files that do load under Node 22 type-stripping pass
clean: `types.test.ts` 15/15, `shell-ban.test.ts` 2/2.

---

## 7. Structural, fleet-wide

**CI is the outlier, not the rule.** Of 13 repos examined this round, **9 have zero workflows**:
`experiment-wheel`, `swarm-tminus`, `vessel-quest`, `quilt-deck`, `superinstance-advisor`,
`forgemaster-memory-archive`, `quilt-organ-workers`, `quilt-scratch`, `fm-research-archive`.
Only `flux-algebra`, `fleet-radio`, `fleet-spread`, `songforge` have any. The repos with the
most rigorous *methodology* have the least automation — the rigour is in the prose and the
commits, not in a runner.

**Three distinct author-home paths now confirmed in the fleet** — always grep before trusting
a "reproducible" claim:

| path | repos |
|---|---|
| `/home/eileen/` | `experiment-wheel` (9 sites, API key at import scope) |
| `/home/phoenix/.openclaw/workspace/` | `fm-research-archive` (10 sites) |
| `/workspace/.home/projects/` + `~/projects/` | `quilt-deck` |
| `/home/z/` | (previously seen) |

**The public/undeclared-dependency edge keeps recurring.** `quilt-deck` reaches a file that
lives in a *public fleet repo* through a home directory. Compare: `xero-lab` (10-14T0117Z)
commits receipts; `shoalwater` ships no runnable artifact; `fm-research-archive` ships a
perfect artifact behind a `/home/phoenix/` path. **The fleet's verification work is
consistently one small patch away from being reproducible, and the patch is never the
interesting part — write it.**

### Method notes (carry forward)

1. **A seal is checkable in git, and `experiment-wheel` is the reference implementation.**
   `git log --format='%h %ad %s' --date=iso -- <exp-dir>` then confirm the seal commit
   predates the first artifact commit. A *self-caught* seal violation committed in a message
   (`f0cc641`) is stronger evidence than any passing result.
2. **Recompute a published gate from its committed per-instance records when the runner is
   machine-bound.** I could not import `w10_score.py`, but `w10-verdict-data.json` carried
   everything, and the gate reproduced AND mutated (AND→OR flips the verdict). This is the
   general escape hatch for a `/home/`-locked harness.
3. **A constraint with no witness is not a finding.** Grep the checker for a string
   compared against a join whose length is fixed by another constraint
   (`'THEEILEENLAUN'` vs 12 lines) or for a `sorted()` literal in the wrong order
   (`['.', ',']` vs `[',', '.']`). Both were real, both were found by the authors, and both
   had already produced a wall of "0/16" that read as model weakness.
4. **Compare a public description against the README against the AST.** `flux-algebra`: 226
   vs 382 vs 341. A wrong description is the cheapest defect in the fleet to find and the
   most commonly published.
5. **A suite that tests both branches of an optional dependency must gate one of them.**
   `swarm-tminus` has a correct degradation test and three hard-assert presence tests for a
   package in no dependency list. Grep the tests for "in this environment".
6. **An aggregate number in a README must be producible by the documented command.**
   `fleet-radio`'s 165 comes from a `|| exit 1` for-loop with no counter.
7. **Environment:** pytest absent AND PyPI unreachable; I wrote a ~90-line pytest shim
   (`pytest.raises/approx/mark.parametrize/fixture` + a collector with `setUp`) and ran
   701 tests across 5 suites. node 22.19 `--experimental-strip-types` runs `node:test` but
   **not** extensionless TS imports. Canaries confirmed. `GIT_SSL_NO_VERIFY=1` on every
   clone/push. `/tmp` is the only writable scratch here.

*SCOUT 2026-10-14T1330Z — census 5,237/53pp · 3,324 unseen own · 6 items · no prior file
overwritten.*
