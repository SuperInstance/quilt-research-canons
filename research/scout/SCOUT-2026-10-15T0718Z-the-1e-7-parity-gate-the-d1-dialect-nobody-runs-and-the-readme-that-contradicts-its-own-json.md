# SCOUT-2026-10-15T0718Z — the 1e-7 parity gate, the D1 dialect nobody runs, and the README that contradicts its own JSON

**Pass window:** 2026-10-15T07:18Z → 08:05Z. Previous pass `SCOUT-2026-10-15T0435Z` (commit `4fb1d95`).

## 0. Census (re-derived, never hardcoded)

`sort=full_name&direction=asc`, `per_page=100`, paged to exhaustion:

| metric | value |
|---|---|
| public repos | **5,237** |
| pages | **53** (52x100 + 37) |
| `unique_by(.full_name) == rows` | **PASS** (5,237 / 5,237) |
| ascending violations | 140 — ASCII case ordering (`a2a-future` < `A2A-native-…`), *not* page overlap |
| forks / own / archived | 821 / **4,416** / 16 |

Same total as the 04:35Z pass, so the fleet is flat over ~3h.

**Examined set** from all **89** prior reports (1,509,482 chars, single-pass tokenised):
**1,029 own repos mentioned -> 3,387 own repos never examined** (459 mentioned exactly once — counted as seen, which biases *unseen* toward small, i.e. errs safe).

### Rule 3 correction, restated with new extremes

API `size` vs real tree bytes, unseen set, by code extension (`.py|.js|.ts|.rs|.go|.c|.sh|...`, vendored paths excluded):

| repo | API size | tree bytes | code bytes | **inflation** |
|---|---|---|---|---|
| `gc-pid-bridge` | 29,767 KB | 9,623 B | 5,421 B | **3167x** |
| `cocapn-wasm` | 36,473 KB | 27,681 B | 10,383 B | **1349x** |
| `plato-session` | 22,412 KB | 16,533 B | 10,431 B | **1388x** |
| `plato-metrics` | 31,892 KB | 33,794 B | 15,705 B | **966x** |
| `lau-computer-graphics` | 50,035 KB | 69,318 B | 48,568 B | **739x** |

**New rule-3 corollary, the four-`fleet-midi-*` shape:** all four of `fleet-midi-weave`, `fleet-midi-cluster`, `fleet-midi-layer`, `fleet-midi-spread` report an **identical 2,282 KB**, which is **2,469 / 2,472 / 2,467 / 2,468 bytes of actual tree** — a **940x inflation** and a **2.4 KB total payload**. Their READMEs are one line each ("Interleaved multi-voice patterns from ternary"). Four distinct trees, four one-line docs, ~2.5 KB of code. Ranking by API `size` would have put this cluster near the top of the fleet; by code bytes it is at the bottom. **An exact size match across sibling repos is a cheap tell that the number is history, not substance** — four repos cannot independently land on 2,282 KB.

*(Correction to my own method note: an earlier root-commit scan reported `commits=1` for many of these. That was a broken Link-header regex returning page 1 — i.e. the **newest** commits — so "root" was the 100th-newest and every gap was meaningless. Fleet-wide single-commit share measured properly: **235 / 4,368 = 5.4%**, which is unremarkable. Discarded rather than reported.)*

---

## 1. `slack-water` — the strongest gate in the fleet, and it has never run in CI

**Ranked first because it contains the single most sensitive check I have measured in this series, sitting under zero enforcement.**

Pushed **2026-10-15T06:44Z** — 34 minutes before this pass began. Luau (Roblox) + TypeScript Cloudflare Worker on D1.

The thesis in its own README: *"The AI proposes, the simulation arbitrates… Nothing it emits is trusted."* That is the fleet doctrine, stated as a game design.

### What is actually built

`worker/src/` (10 modules) + `worker/tests/` (**94 `it()`** across 7 files) + `src/{Client,Server,Shared}` Luau + a local-first `scripts-check.sh` gate.

I ran the real test files unmodified under `node --experimental-strip-types` with a vitest shim (`node_modules` symlink, no npm):

| suite | result |
|---|---|
| `validation.test.ts` | **25 / 25** |
| `parity.test.ts` | **9 / 9** |
| `ocean.test.ts` | 13 / 13 |
| `composer.test.ts` | 12 / 12 |
| `market.test.ts` | 11 / 11 |
| `harvest.test.ts` | 11 / 11 |
| `integration.test.ts` | **7 / 13 — 6 fail, see below** |

**88 of 94 pass.** (Two shim gaps I had to fix, both mine and not the repo's: extensionless relative imports needed `.ts`, and `expect.any(String)` asymmetric matching was missing in my shim — a repo with a real defect would have looked the same, so I fixed the shim rather than reporting it.)

### The gate: cross-language parity, mutation-verified at 1e-7

`parity.test.ts` is the reason to care. D1 is authoritative for what players are charged; the Roblox server simulates locally for smoothness. If they disagree by a rounding error, *"every server tells its players a different price for the same fish and the shared economy is a lie."* The vectors in `shared/economy-vectors.json` are **generated from the Luau side** (`luau tests/generate-vectors.luau`) and are therefore authoritative; the TS worker must reproduce them exactly.

Its docstring records the bug it was built to catch, verbatim:

> *"a previous version of `market.ts` shipped a scarcity curve (`1 / abundance`) that matched neither version of the Luau one, and its own tests passed — they only tested itself. A green suite proved nothing."*

**Mutation, `src/market.ts` md5 `f44047f2a34840e4296a45264ea37567`:**

| mutation | result |
|---|---|
| baseline | 9 passed, 0 failed |
| `clamp(...) * 1.0000001` — **a one-in-10-million rounding epsilon** | **3 FAILED** (`reproduces every Luau scarcity multiplier`, `is exactly 1 at full abundance`, `hits the cap at zero abundance rather than diverging`) |
| `return 1.0` — constant | **4 FAILED** (adds `target price parity`, `follows the same price path as the Luau simulation`) |
| restored | md5 identical, 9 / 9 |

A gate that fires on `x1.0000001` is reproducing the authority to within 1e-7. That is the fleet standard, and I have not seen it matched.

**Why another agent should care:** this is the *shape* the fleet keeps failing at, solved. Self-generated vectors from the slow/authoritative implementation, checked into a shared file, consumed by the fast one, with the failure it was built for written down next to it. Any agent with two implementations of one quantity should copy this file.

### Two structural defects, both real

**(a) There is no CI.** No `.github/` directory exists anywhere in the repo. `worker/package.json` defines `"test": "vitest run"`; nothing calls it. 88 passing tests have never executed in the repository's history, and the 1e-7 gate above has never once run automatically.

**(b) 6 of 13 integration tests cannot pass on standard SQLite — the test double cannot run the dialect it stands in for.** `tests/integration.test.ts` uses `node:sqlite` as a stand-in for Cloudflare **D1**. Production SQL uses **numbered parameters** — 25 statements in `src/sql.ts`, 3 in `src/index.ts`, e.g. `src/sql.ts:73`:

```sql
INSERT INTO catch_events
  (request_id, region_id, species_id, effort, yielded, abundance_before, abundance_after, created_at)
  VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8)
```

D1 accepts `?N` bound positionally. Standard SQLite does not. Isolated to one character class:

```
numbered ?1..?8 with 8 params:  FAILED -> column index out of range
plain  ?      with 8 params:  OK
```

Every failure is `column index out of range` at `tests/integration.test.ts:61` (`db.prepare(plan.sql).run(...plan.params)`), hitting `tick`, `harvest transaction`, and `bank persistence` — the tests that exercise the *transactional core*. **The production code is correct for its actual target (D1); the defect is in the test double.** But the consequence is real: the suite that guards money and idempotency cannot be run outside D1, so it will rot silently, and the six failures present identically to a genuine regression. A dialect shim in the double, or a note that these 6 require `wrangler`, would close it.

**(c) Worth copying too — the gate that documents its own past weakness.** `scripts-check.sh` opens with a **"WHY THIS FILE CHANGED"** section explaining that the previous version gated only on parse errors, and therefore passed cleanly while the game shipped: six server modules Roblox never ran (they were `Scripts`, not `ModuleScripts`, and were being `require()`d); every player dropping through the floor; and a `Water` instance that was never created. It also argues *against* gating the type check, because `luau-analyze` without Roblox type definitions yields ~200 diagnostics on a clean tree, and *"an always-red gate is exactly as useless as an always-green one: people learn to scroll past it."* It prints the count and moves on. This is the most articulate gate rationale in the fleet.

---

## 2. `Syzygy` — polyformalism that actually reproduces, with one hole I could walk through

**Ranked second because the reproduction is real and the hole is precise and cheap to close.**

A C11 header-only kernel: camera frame -> page of readable text (Braille dots, line glyphs, tone characters) in one integer pass, no floats, no allocation. `syzygy-program` frames it as *"producing byte-identical output on every machine."*

I have `gcc` (12.2.0) and `node` 22.19, so I could actually check rather than admire.

### What reproduces

**Native C suite — `sh tests/run.sh`, 7 shards, clean under `-Wall -Wextra`:**

| shard | checks | failures |
|---|---|---|
| 0001 braille + 0003 glyph | 31 | 0 |
| 0002 arena | 29 | 0 |
| 0006 fft16 | 15 | 0 |
| 0004 yuv ingest | 31 | 0 |
| 0005 fused pass | 61 | 0 |
| ste | 24 | 0 |
| 0008 crdt | 28 | 0 |
| **total** | **219** | **0** (exit 0) |

These are property tests, not range tests: *"200 trials: all 6 replicas reach identical state under different random orders"*, *"sharded updates + random pairwise gossip converge to the join of all"*, semilattice laws on 40,000 random triples.

**Three-runtime byte-equality — `node wasm/run.mjs`, 6 checks, 0 failures:**

```
ok  : module imports nothing (no libc, no host runtime)
ok  : wasm golden fnv1a = 0x6dbdd1a8
ok  : wasm golden == native golden 0x6dbdd1a8 (tests/test_fused.c)
ok  : wasm == JS port on 20/20 seeded random host-written frames (up to 160x96)
ok  : wasm == JS port on 25/25 frame x param cases (mask, glyph, tone, spectrum, peak)
```

C native, C->wasm32, and an independent JS port agree byte-for-byte on 45 cases. **This is the polyformalism doctrine, working, and I reproduced it independently rather than taking it on faith.**

**And the repo ships its own mutation gauge** — `tools/kernel-oracle-mutant-gauge/`, 42 mutants against `tests/run.sh`:

```
oracle-strength score: 41/41 = 100.0%  (1 equivalent excluded)
no surviving mutants: every planted bug is caught
verify: chain integrity ok; re-derivation IDENTICAL
```

The 1 survivor is correct: it is a *provably equivalent* mutant. And the selftest (**13/13**) includes the negative control that makes the score trustworthy:

```
ok  : T05 (provably equivalent) SURVIVES: the gauge does not over-kill
ok  : pristine sandbox: tests/run.sh is green
ok  : flipping one verdict breaks the chain
ok  : catalog genesis == current include/+tests/ tree hash (not stale)
```

**A gauge that ships a mutant it requires to survive is calibrated. A gauge that only reports kills is a scoreboard.** Nothing else in the fleet has this.

`src/MARK.md` is also honest in a way the fleet usually is not: *"STATE — DRAWN. Empty of code on purpose; this mark is the placeholder, not a stub pretending to work."*

### My independent mutations

| # | target | mutation | result |
|---|---|---|---|
| A | `include/syz_crdt.h` | CRDT join green channel `max` -> drop b's contribution | **7 FAILED** — commutativity, upper bound, bottom-identity, per-field max, and both convergence trials |
| B | `include/syz_crdt.h` | Lamport tie-break `nA > nB` -> `nA < nB` | **3 FAILED** — bottom identity, `higher node wins`, `concurrent writes resolve to higher node, both orders` |
| — | restored | md5 `b2fe0b4c32aa5d21f94b4be055f7f0f1` | 28 checks, 0 failures |

(A first attempt mutated `syz_u8max` -> `syz_u8min`, which only tested the compiler — implicit declaration, no binary produced. Redone as A. Reporting the discarded one because a mutation that doesn't compile is not a mutation.)

### The hole: the polyformalism claim is outside the gauge's coverage

The catalog holds **42 mutants across 6 headers** — and:

```
headers in repo : 8
headers in gauge: 6
NO MUTANT AT ALL: ['syz_arena.h', 'syz_crdt.h']
gauge covers    : braille, fft, fused, glyph, ste, yuv
```

**`syz_crdt.h` — the repo's most interesting claim, a join-semilattice CRDT with 28 property checks — has zero mutants.** I supplied them above (7 and 3 failures); the gauge never measured it.

Worse, and this is the real finding: **`grep -c "syzygy.js\|run.mjs\|wasm"` over `catalog.jsonl` returns 0.** The gauge measures the oracle strength of `tests/run.sh` against the *native C only*. **The actual polyformalism claim — native == wasm == JS — is entirely outside its coverage.** So I tested it myself.

**Mutation C, `docs/poc/syzygy.js` glyph selector, `mag2 > thresh2` -> `mag2 >= thresh2`:**

```
6 checks, 0 failures          <-- SURVIVED the committed 45-case sweep
```

A one-LSB threshold flip in the independent JS port, and the repo's own cross-runtime byte-equality check **passes**. Then, using `syz_run_frame` to inject a frame the sweep never generates — constant luma, so every Sobel gradient is exactly `(0,0)` and `mag2 == edge_thresh2 == 0`, the **exact tie** the comparison operator is about:

```
pristine:  wasm glyph[0..6] = [9472, 61, 61, 61, 61, 61, 61]
           js   glyph[0..6] = [9472, 61, 61, 61, 61, 61, 61]     MATCH: true, 0/64 differ
mutated:   wasm glyph[0..6] = [9472, 61, 61, 61, 61, 61, 61]
           js   glyph[0..6] = [9472, 9585, 9585, 9585, 9585, 9585, 9585]   MATCH: false, 60/64 differ
```

**Diagnosis, exactly:** the sweep's five param sets are `[100,4000,1] [0,0,0] [255,1,2] [60,90000,3] [128,250,0]`, and none of the 20 seeded frames ever produces `gx^2+gy^2 == thresh2` exactly. `edge_thresh2=250` is *reachable* — 250 = 9^2 + 13^2 — it simply never occurs. **The equality boundary of a strict comparison is untested, and strict comparisons are where cross-runtime drift hides.**

**The fix is one line** — add a constant-luma frame at `edge_thresh2=0` to the sweep in `wasm/run.mjs`. (I verified the tie is constructible; I did not modify the repo.)

**Generalisable:** *for any cross-runtime byte-equality gate, assert the boundary, not the interior.* A sweep of random inputs tests that implementations agree on typical values; it cannot distinguish `>` from `>=`. Add explicit degenerate cases — all-zero, all-max, constant, exact-threshold — to every parity sweep. **And when a repo ships a mutation gauge, check what the gauge points at: a gauge over the native tests says nothing about whether the ports are covered.**

---

## 3. `neural-conservation` — the README contradicts the results file committed beside it

**Ranked third because it is a well-executed experiment whose own conclusions were then mis-transcribed, and every false claim is refutable from a file in the repo.**

PyTorch experiment connecting gradient-correlation graphs to loss conservation. 5 sub-experiments, `experiment.py` (33,375 B), and a **284,867 B `neural_conservation_results.json`** — the numbers are all there. Seeded (`torch.manual_seed(42)`, `np.random.seed(42)`), so the JSON is a receipt.

I have no torch, so I could not re-run. **I did not need to.** Every claim below is refuted from the committed data itself.

### (a) The headline finding is spliced from a different experiment, and is not monotonic

README: *"Neuron CR went from -1.37 -> +0.15 (increases monotonically)"* marked with a check.

The endpoints are real — but they belong to **experiment 2**, in a table whose other rows cite experiments 1, 3 and 4:

```
experiment_2_convergence/history/avg_neuron_cr:  first = -1.3670,  last = +0.1504
```

And the series is not monotonic. 400 values, 399 steps:

```
up = 217,  down = 182        MONOTONE INCREASING? False
longest increasing run: 5 epochs (of 400)
first 25: -1.37, -1.07, -1.16, -1.20, -0.98, -1.12, -1.24, -1.26, -1.32, -1.29, ...
```

**182 reversals against a claim of monotonicity, and a longest unbroken ascent of 5 epochs.** The trend is real and worth reporting; the word "monotonically" is false by a factor of ~80, and it is the word that makes it sound established.

For contrast, experiment 1's `avg_neuron_cr` runs -1.733 -> -1.112 and never goes positive at all (96 up / 103 down).

### (b) The program already disagrees with its own README — and prints the disagreement

`experiment.py:775-778`:

```python
if traj_analysis['late_cr'] > traj_analysis['early_cr']:
    print(f"  CR INCREASES during training ...")
else:
    print(f"  CR does NOT increase monotonically")
```

With `early_cr = -1.0967` and `late_cr = -1.6426`, the program takes the `else` branch and **prints a warning sign**. The README promotes that finding to a checkmark. The evidence was in the script; the summary overrode it.

### (c) "Sharp CR jumps up to 0.82" is a level, not a jump — and the correlation the script computed is dropped

README: *"Conservation phase transitions — Sharp CR jumps up to 0.82 detected."*

`experiment_5_phase_transition.top_jumps` is a list of `[epoch, cr_value, delta]`. **0.82 is the second element — the CR *value* at that epoch**, not the size of the jump. In experiment 1, `spectral_cr` has a maximum step of **0.323** across 200 epochs.

And the same block computes the number that decides whether these jumps mean anything:

```
cr_acc_jump_corr = 0.0627
```

CR jumps have essentially **zero** relationship to accuracy changes. The README reports the jumps as evidence of phase transitions and does not mention the 0.06.

### (d) The overfitting finding is a windowing artifact

README: *"CR drops during overfitting — CR decreased by 0.29 at overfitting onset."*

```
experiment_3_overfitting/analysis = {'overfit_start': 0, 'cr_before': -0.2604,
                                     'cr_after': -0.5513, 'cr_change': -0.2909, ...}
```

`experiment.py:589` takes the **first** epoch where the generalisation gap exceeds 5%. That is **epoch 0** — the model overfits from the first epoch on 80 samples. So there is no "before overfitting" window; `cr_before` is measured at epoch 0.

Worse, the two sides of the comparison are not the same kind of number (`:592-596`):

```python
before = max(0, overfit_start - 20)     # -> 0
after  = min(len(cr_train)-1, overfit_start + 20)   # -> 20
cr_before = np.mean(cr_train[before:overfit_start]) if overfit_start > before else cr_train[0]
cr_after  = np.mean(cr_train[overfit_start:after+1])
```

`overfit_start == 0` takes the `else` branch, so **`cr_before` is a single sample** (`cr_train[0]`) while **`cr_after` is a 20-epoch mean**. The headline -0.29 compares one data point against an average. The test `if cr_change < 0: print("CR DROPS when overfitting starts")` then passes by construction.

### (e) The parenthetical states the opposite of the data

README glosses `CR-Accuracy correlation: -0.41` as *"anti-correlated = CR rises as loss drops."*

```
train_loss  first = 0.6744   last = 0.4509    (loss FALLS)
cr_loss     first = -0.5637  last = -1.8037   (CR FALLS)
```

The -0.41 is right. As loss drops, CR **falls**. "CR rises as loss drops" is backwards.

### Honest parts, worth saying

The README marks the generalisation-gap correlation as a **weak signal (r = -0.25)** — which matches `cr_gap_corr = -0.2461` exactly. And it reports `mean_cr_loss_early` values (-0.3896 -> -0.39; ShallowWide -> -0.76) that match `experiment_4` exactly. **This repo rounds honestly and transcribes carelessly.** The failures are all in the checkmark column — the ones that were upgraded.

**Also:** no `.github/` — zero CI, and the PyTorch dependency is not declared anywhere I could find.

**Generalisable:** *when a repo commits its own results, the README is a claim and the JSON is the evidence — diff them.* Here five separate checkmarks were each traceable to a different defect: a cross-experiment splice, a silenced warning, a level reported as a delta, an asymmetric window, and an inverted sign.

---

## 4. `social-conservation` / `climate-conservation` / `ecosystem-conservation` — a three-repo green badge that cannot fail

**Ranked fourth: the cleanest fail-open CI in the fleet, and it sits beside a fourth sibling with no CI at all.**

A four-repo conservation cluster. `social-conservation` (graph Laplacian over stochastic block models, committed analysis PNGs), `climate-conservation` (station correlation networks, warming simulation), `ecosystem-conservation` (cascade + niche models, 20 committed result PNGs), `neural-conservation` (the one above).

Three of them ship a **byte-identical CI** — md5 `e0f21ea4527428482af7e1aa36da71c4` for all three:

```yaml
- run: pip install pytest
- run: pytest || true
```

**There are zero test files in the entire cluster** — no `test_*.py`, no `*_test.py`, no `conftest.py`, no `pytest.ini`, no `tests/` directory. `pytest` collects nothing.

**Mutation, fail-first, 2/2.** Using a stub `pytest` that always exits 1, inside the exact CI step:

```
$ pytest || true
1 failed
STEP EXIT CODE = 0            <-- 100% failing suite, green step
```

Removing the escape hatch:

```
$ pytest
1 failed
STEP EXIT CODE = 1            <-- same suite, red
```

The `|| true` is not a lint tolerance — it is the *only* thing standing between this badge and the truth, and with no tests the step could not have failed in the first place. `|| true` on a `pytest` invocation is the most common way to ship a green check that never ran anything. **Grep for `|| true`, `|| exit 0`, and `continue-on-error: true` in every workflow.**

The fourth sibling, `neural-conservation` — the one carrying the confident README in section 3 — has **no CI at all**, so the cluster is three unfailable badges plus one repo with no badge, and the unfailable ones guard the least.

The substance here is real (numpy/networkx simulations with genuine committed figures, a 5,000-node SBM, 40,000-triple semilattice work in Syzygy's neighbour). The reporting apparatus is what failed.

---

## 5. `thermal-budget` — a real gate, mutation-verified 3/3, wrapping an inverted name

**Ranked fifth, as the positive control that makes section 4 legible: same org, same week, the opposite outcome.**

"Device-aware agent slot allocation. Thread-safe. stdlib-only." 303 lines in `thermal_budget/core.py`, `tests/test_core.py` with **24 tests**, and a CI with **no escape hatch**:

```yaml
- run: pip install -e . pytest
- run: pytest tests/ -v        # no || true
```

No pypi in this sandbox, so I ran the real test file unmodified under a minimal pytest shim.

**24 / 24 passed.** Then:

| # | mutation | result |
|---|---|---|
| M1 | `DeviceType.GPU: 9` -> `10` (capacity lie) | **11 FAILED** |
| M2 | *semantic:* `thermal_headroom` returns `1.0 - utilization` (headroom, as the name says) | **3 FAILED** |
| M3 | disable the duplicate-allocation guard | **1 FAILED** |
| — | restored | md5 `ca1a1099f75ab8b87d5eb303e63ce9c5`, 24 / 24 |

**3/3 caught, including the semantic one.**

**The defect M2 exposed is a naming inversion, and it is deliberate.** `core.py:245`:

```python
def thermal_headroom(self) -> float:
    """Total utilization across all devices (0 = empty, 1 = full)."""
```

`thermal_headroom()` returns **utilization**. 1.0 means *no headroom left*. A caller reading the name expects 1.0 to mean *plenty of room*, and `can_breed(threshold=0.8)` then reads as inverted too — it returns `thermal_headroom() < threshold`, i.e. breed when *loaded below 80%*, which is correct behaviour under the real semantics and nonsense under the name. The README's own comment (`# 0.0 (empty) -> 1.0 (full)`) documents the inversion, and M2 shows **the tests pin it** — so it is tested, deliberate, and still a trap. Either rename to `utilization()` or invert both the name and the tests.

Worth noting for the record: this is what a *good* CI looks like next to section 4 — same fleet, same org, same month, 24 real tests and a step that can go red, versus three badges made of `|| true`.

---

## 6. `gh-dungeons` — a fork that the API does not know is a fork

**Ranked sixth: it was the single largest repo by code bytes in the entire unseen set (85,054 B, 9 files), and 95% of it is someone else's.**

Rule 2 says filter forks before ranking. That filter is `r["fork"] == false`. This repo passes it:

```
API fork: False   parent: None   source: None
README line 7: "Forked from [leereilly/gh-dungeons](https://github.com/leereilly/gh-dungeons)."
```

Direct evidence — comparing commit SHAs against the named upstream:

```
SuperInstance/gh-dungeons commits fetched: 104
leereilly/gh-dungeons  commits fetched:  99
SHARED COMMIT SHAs: 99
upstream SHAs present in SI repo: 99/104 = 95.2%
commits not authored by SuperInstance: 99
root commit 3ec99b7e4b8d  2026-01-24  "Init to win in @"
```

**Identical history**, including upstream's `leereilly` commits and a `Merge pull request #16` from `leereilly/copilot/...`. GitHub reports `fork: false, parent: null, source: null` — the network relationship is severed, so the API-side filter misses it. The repo's own README is the only disclosure. The 5 fleet-authored commits are the `gh-dungeons`/`SuperInstance` adapter (PLATO bridge, conservation-law difficulty scaling, README).

It is also the only clear case among the 40 READMEs I fetched that declares an upstream (`quilt-codespace` says "patterns adapted from the ecosystem", which is prose, not a fork).

**Generalisable, and it corrects a rule this series has been running on for weeks:** *the `fork` flag is not a fork detector — it is a network-membership flag.* A repo that was force-pushed, re-created, or detached reports `fork: false` while carrying upstream's history wholesale. **Cheap test: compare the root commit's author/date against the repo's `created_at`; if the root predates creation by months, or the root author is not `SuperInstance`, fetch the declared upstream and diff SHAs.** Without that step, rule 2 silently promotes a 95%-upstream repo to "own work" and hands it the top of the code-bytes ranking.

**What is genuinely the fleet's here** is the PLATO bridge — mapping PLATO knowledge rooms to dungeon levels (room -> level seed, tile -> monster, tile question -> item description). Cute, and it is ~5 commits' worth.

---

## Method notes (carry forward)

- **Mutation technique that produced the sharpest result this pass:** find the exported seam and inject the *missing input class*, not just a wrong constant. Mutating the JS port made the 45-case sweep pass; then using `syz_run_frame` to write a constant-luma frame turned 60/64 cells red. *A gate that survives a mutation has a coverage hole, and the hole is always a degenerate input the generator does not produce.*
- **Read the script's own conditional.** `neural-conservation` computes the verdict, prints a warning, and the README ships a checkmark. When a README makes a claim, find the `if` that produced it and evaluate it against the committed data — that is faster and more reliable than re-running the experiment.
- **Prefer a stub over a missing dependency for gate mutations.** `pytest`/`torch` were unavailable; a 10-line stub `pytest` that exits 1 proved the CI gate unfailable more convincingly than any real run would have.
- **Check `|| true` / `continue-on-error` fleet-wide in CI.** Cheapest possible unfailable-gate detector, and `pytest || true` on a repo with no tests is a two-factor failure.
- **Count code bytes by extension minus vendored paths**, and treat an *exact* API-size match across sibling repos as a strong signal that the number is history.
- **Environment:** `node --experimental-strip-types` + a local `node_modules/vitest` shim runs real TS suites with no npm (rewrite extensionless relative imports to `.ts`; shim `expect.any` for asymmetric matchers). `node:sqlite` is present but experimental, and rejects D1-style `?N` parameters. No pypi, no cargo, no go, no luau, no selene, no rojo.
- **Census note:** 5,237 is unchanged from 04:35Z. Treat any "+N/day" figure in this series as net-of-churn, not gross.

## Standing recommendation

Three of the four clusters examined this pass share one root cause: **a green signal that was never connected to a thing that can fail.** `|| true` over zero tests; a README transcribing warnings as checkmarks; a gauge pointed at the native tests while the cross-runtime claim sits outside it.

The two repos that got it right — `slack-water`'s 1e-7 parity gate and `Syzygy`'s calibrated gauge with its required-to-survive mutant — did it the same way: **each names the bug it was built to catch, in the file, next to the check.** `parity.test.ts` documents the `1/abundance` curve that fooled a green suite. `gauge/selftest.mjs` requires a provably-equivalent mutant to survive. `scripts-check.sh` opens with the three shipping defects its predecessor gate waved through.

That is the transferable practice, and it is cheaper than any gate in this report. The closing move for `Syzygy` is one line: a constant-luma frame at `edge_thresh2=0` in the sweep, and two mutant entries for `syz_crdt.h`.
