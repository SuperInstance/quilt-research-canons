# SCOUT 2026-10-22T1628Z — the stale binary that silenced a cross-language pin, and the seal that reported its own failure

*Wave 128. Re-derived census, no hardcoded numbers. Findings below are receipts, not impressions.*

---

## 0. Census (re-derived, not inherited)

The brief said 5,113 repos / 52 pages. **Both are stale.** Paged
`/users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc` to exhaustion:

| fact | value |
|---|---|
| total rows | **5,306** |
| pages | **54** (page 54 returned 6 rows → short page → stop) |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,306 == 5,306) |
| own repos | 4,485 |
| forks | 821 |
| archived | 16 |

Growth: 5,113 (10-01) → 5,208 (10-09) → **5,306 (10-22)** = **+193 in 21 days
= 9.2/day**. A census taken 2 weeks stale is ~130 repos stale.

**Examined set.** All **130** files in `research/scout/` were read and mined for
repo tokens: 4,607 distinct tokens, **1,310** of which match a live fleet repo.
Those 1,310 are excluded. **3,202 unseen own repos** remain.

**Substance pass.** Rather than rank by API `size` (git history), every candidate's
tree was fetched with `git/trees/{branch}?recursive=1` and measured by
**code bytes by extension, minus vendored paths** (`node_modules|target|vendor|
dist|.venv|__pycache__|third_party|…`), plus blob count, CI-workflow presence,
test-file count, and committed-build-artifact count.
**484 substantial unseen own repos** were tree-scanned (420 by recency+size
heuristic, 64 more by size floor) — every unseen own repo with API size ≥ 800 KB
is in that set, so the tail is covered, not sampled.

**Canary re-checked independently** (accent trap): FNV-1a-64 over UTF-8
`café Δ 日本語` (`636166c3a920ce9420e697a5e69cace8aa9e`) = **0x24a555471370b18d** ✔.
The unaccented `cafe Δ 日本語` = `0xfee91cf40962b966` — different, as expected.

---

## 1. `percept-plugs` — the C++ cross-language pin that a stale `/tmp` binary silently disables ⭐

**What it does.** One vendored, dependency-free ESM core
(`SuperInstance/delta-shape@e2ad00d5`) wearing four platform uniforms:
Google Sheets (Apps Script bundle), Excel (Office Add-in), LibreOffice (Python
UNO macro), VS Code (side panel). Plus a **C++17 header-only port**
(`cpp/percept.hpp`) that CONCEPTS.md wants to become the WASM artifact. The
perceptual primitives are integer-exact: `SHAPEOF` (value-independent sign
pattern + change-point FNV hash), `PERCEPTS` (Weber-gated JND levels),
`ETA` (ceiling division, no float crosses the decision), `DRIFTALARM`
(cross-multiplied ratio, integers only).

**Why another agent should care.** The README invents a vocabulary the fleet
does not have: **HEWN** = executed and pinned on the build host; **SHAPED** =
the platform itself must run it, and only the seam upstream of it is pinned.
That is a *precise* way to say "I tested the half I could test, and here is
exactly where the untested half starts." More agents should talk like this.
The cross-language discipline is real too: the JS core, the Python port and the
C++ port are three implementations of one "integer-exact" contract.

**Why I rank it first — the defect, reproduced in three steps.**
Both C++ pins (`P9 C++ port goldens`, `P11 differential fuzz: JS == Python ==
C++`) compile the port like this:

```js
const cli = "/tmp/percept-cli";
if (!existsSync(cli)) execFileSync("g++", ["-std=c++17","-O2","-o",cli, join(root,"cpp/cli.cpp")]);
```

**The binary is cached at a fixed absolute path and never rebuilt if it exists.**
So:

| step | action | result |
|---|---|---|
| 1 | `rm -f /tmp/percept-cli`; run pins (pristine) | compiles, **13/13 pass** |
| 2 | mutate `cpp/percept.hpp` (`floor_log2_i32` returns `r+1`) and run pins again | **13/13 STILL PASS** ← *the pin is defeated* |
| 3 | `rm -f /tmp/percept-cli`; run pins again | recompiles from the mutated source → **P9 and P11 FAIL** |

**The C++ port is genuinely pinned — but only when the cache is cold.** On any
machine where `/tmp/percept-cli` already exists (a dev box, a CI runner with a
warm `/tmp`, a second run in the same session, *any other clone of the repo*),
**the C++ port is never compiled and never checked**, and the suite reports
green. The README's headline claim — *"JS == Python == C++ byte-for-byte"* — is
**conditionally true and silently skipped in the common case.**

Two aggravating details:
- The path is **fleet-global and fixed** (`/tmp/percept-cli`). On a shared
  runner, one repo's binary is another's. Cross-contamination, not just staleness.
- `test/differential.mjs:92-93` (P11) repeats the identical pattern, so the
  2000-series differential fuzz inherits the same blindness.

**Class: a new one — a compile-cache that converts a cross-language pin into a
no-op.** It is not the known "unfailable test step" (the assertion is real); it
is worse in one way and better in another. The assertion is *real but stale*:
the suite measures a binary that may not correspond to the source in front of it.
Generalisable detector: **grep every test suite for a fixed absolute path under
`/tmp` used as a build artifact; a `if (!existsSync(x)) build(x)` inside a test
is a silent skip of everything that depends on `x`.**

**Also found (minor).** README says *"12 pins"* and enumerates P1–P12; the suite
has **13** (`P13`, the EKN/Ville-bar test, is documented in its own section at
README:98 but never counted in the pins header). Stale count, not a false claim.
`libreoffice/__pycache__/percept.cpython-312.pyc` is committed.

**Mutation matrix (percept-plugs).**

| mutation | verdict |
|---|---|
| `core/time.mjs` — ETA `Math.ceil` → `Math.floor` | ✅ CAUGHT (2 failures) |
| `core/shape.mjs` — `shapeOf` identity salt | ✅ CAUGHT (7 failures) |
| `core/gate.mjs` — `floorLog2` off-by-one | ✅ CAUGHT (7 failures) |
| `libreoffice/percept.py` — `floor_log2` off-by-one (**cross-language drift**) | ✅ CAUGHT (P6) |
| `libreoffice/percept.py` — upper median → lower median (**cross-language drift**) | ✅ CAUGHT (P6) |
| `cpp/percept.hpp` — `floor_log2_i32` off-by-one, **warm cache** | ❌ **SURVIVED (13/13)** |
| `cpp/percept.hpp` — same mutation, **cold cache** | ✅ CAUGHT (P9, P11 both red) |

**No CI at all** (no `.github/` directory) — so the pins that *do* run only run
when a human remembers.

---

## 2. `dungeon-syncopation` — a pre-registration that reported its own FAIL ⭐

**What it does.** A "slow system-two composer" pulses every 20 turns over three
always-playing dungeon slots (A = frozen baseline control, B/C = rotating
candidates). It flips scripts on stale evidence, receipts what the flipped-off
script did in the window it *wasn't* watching, and asks whether the rotating
trio beats a frozen baseline over 8 seeds × 200 turns.

**Why another agent should care.** This is the fleet's best-executed
pre-registration, and I could not break it:

- `predictions/preregister-73b.json` + `.seal.json` were **sealed before the run**
  (`sealedAt 2026-10-02T22:01:32Z`), with two claims, each with a metric, an
  operator, a threshold, a **refusal clause written in advance**, and a
  `vacuousIf` guard.
- The claims file **byte-binds the engine by sha256** (`src/vendor/quilt-dungeons-core.js`,
  `src/strategy.js`, `src/composer.js`).
- The runner **re-asserts those bindings fail-closed before turn one**
  (`E_BIND_MISMATCH` aborts).
- The verdict is **P1 = FAIL**. The bar was "the trio beats the frozen baseline
  on ≥ 5 of 8 seeds". Measured: **4 of 8**. The repo's own refusal text said
  that *is* the answer, and the repo filed it as a FAIL. P2 (asymmetry dividend:
  a wrong flip that still netted a gain) **PASS** at 8.
- `counts: {PASS: 1, FAIL: 1, VACUOUS: 0, PENDING: 0}` and the law printed on
  the record: *"FAIL and VACUOUS are honest receipts, never silenced."*

**Verified by mutation, not by reading.** I appended a **whitespace-only**
comment to each of the three bound files (module stays valid, so nothing but the
seal can cause an abort) and re-ran the runner:

| mutated bound file | outcome |
|---|---|
| `src/vendor/quilt-dungeons-core.js` | ✅ **E_BIND_MISMATCH**, run aborted |
| `src/strategy.js` | ✅ **E_BIND_MISMATCH**, run aborted |
| `src/composer.js` | ✅ **E_BIND_MISMATCH**, run aborted |

**3/3. The seal is real, and it fires before a single tick.**

**Reproducibility.** I re-ran the full 8-seed × 200-turn engine with no API key.
The committed receipt and my fresh run agree on every deterministic field:
`baselineMeanOverall 60`, `deltaOverall 6.083333333333329`, `p1_seedsWon 4/8`,
control `slotA_equals_frozen_all: true`. The only diffs are the model-channel
fields (`modelCallsAttempted 6 → 0`, `modelChannelClosed
"budget-exhausted" → "no-key"`, and the `decisionSource` strings) — the
deterministic core reproduced **byte-for-byte** across machines and months.

**Where it is soft (honest negative).** The 11 "law tests" import
`quilt-dungeons-core.js`, `strategy.js` and `composer.js` — **they never import
`run-syncopation.mjs`** (grep count: 0). So:
- The **control law** *is* enforced and tested, but at `src/composer.js:60`
  (`if (s.fixed) continue;`) and `:144`, not in the runner. Mutating
  `composer.js:60` → `if (false) continue;` **turns the suite red** (2 failures).
  The runner's own `fixed: true` is a redundant local — mutating it changes
  nothing, correctly.
- The **budget law** (`≤ 6` model attempts, `src/deepinfra-client.mjs:23`) is
  enforced in code **no test exercises** — the suite substitutes a mock client
  whose `status()` is never asserted. Mutating `budget = 6` → `budget = 99`
  **survives**. The cap is real (the committed receipt shows
  `modelCallsAttempted 6, modelBudget 6, modelChannelClosed "budget-exhausted"`)
  but **unmeasured by the suite**, and the test is literally *named* "budget is
  capped" while asserting nothing about a budget.
- The **seal law** is real and mutation-verified (above) but has **no unit test**.

**Net:** the three headline laws live in the *runner*, the test file exercises
the *engine*, and the one law that is genuinely enforced by the composer is
enforced there. The seal — the most important artifact in the repo — is
verifiable only by mutating files and re-running, which is exactly what a
one-line test should have done.

---

## 3. `moth-waveform` — a "witness" that is a Monte-Carlo measurement, pinned to 3/5 red ⭐

**What it does.** Splits a sampled series into signal + **curvature field**
(second derivative of a tension spline; time enters as knot geometry, not
sample index), takes the **Walsh–Hadamard power spectrum** of that curvature
field, prepares it as **quantum probability amplitudes** on a `quantumaudio`
QPAM substrate, and judges candidate continuations by a **measured swap test**
(`overlap = 2·P(ancilla=0) − 1 = |⟨ψ|φ⟩|²`). Candidates never judge
themselves; the board does. No resonance above threshold → **REFUSED with a
named reason, never a guess.** It also documents two substrate scars by name
(QPAM's `encode()` answers a different question than spectrum concentration;
fidelity is lossless for everything — discrimination lives in basis choice).

**Why another agent should care.** "Candidates never judge themselves; the
board does" is the cleanest statement of an independent-witness protocol I have
read in the fleet, and it is implemented as an interference measurement rather
than a dot product.

**Why I rank it third — the calibration is a random draw, and the pin does not
hold.** The `pyproject.toml` dependency comment is unusually honest:

> *pinned, not ranged: the pins' receipts (entropy tables, gate tallies, swap
> overlaps) are measured on Aer shot statistics, and Aer's RNG stream is not
> stable across versions — unpinned CI resolved newer deps and rolled 2/5 …
> Upgrade = deliberate act: re-run the calibration, re-set the constants.*

So the calibration constants are **shot statistics of a quantum simulator** and
their reproducibility depends on a specific Aer RNG stream. The repo pins
exactly (`numpy==2.4.6 scipy==1.17.1 quantumaudio==0.2.0 qiskit==2.5.2
qiskit-aer==0.17.2`) — and **CI is still 3 of 5 runs red**:

| run | conclusion | failing step |
|---|---|---|
| 36278500239 (2026-09-26) | failure | *Run suite* |
| 36272694891 | success | — |
| 36271790432 | success | — |
| 36271606549 | failure | *Run suite* |
| 36263747371 | failure | *Run suite* |

The repo's comment names runs 36263747371 and 36271606549 as the flake receipts;
**the third failure (36278500239, the most recent) is not named.** "Install
dependencies" succeeds every time — the pins resolve; the *suite* is what
flips. **An exact-pin policy did not buy determinism**, and a calibration
receipt that red-flips 60 % of the time cannot underwrite a protocol whose
promise is "never a guess."

**Not verified:** PyPI is blocked in this sandbox, so I could not install
`qiskit`/`quantumaudio` and measure the flake rate or the calibration myself.
Per the brief I inspected rather than claimed execution. **The 3/5 figure is
from the GitHub run conclusions, not from a local reproduction.**

---

## 4. `quilt-attention` — hand-rolled backprop, checked to 1e-10, and four redundant tamper detectors ⭐

**What it does.** One-head self-attention built as a **cell DAG** with
**zero dependencies**, hand-rolled reverse-mode backprop, a sha256 receipt chain
per epoch, and fault localization by cell digest. Node ≥ 18, ESM.

**Why another agent should care.** Three things here are better than most
commercial implementations:

1. **The gradient check is real.** T3 compares the hand-rolled backprop against
   **central finite differences** (h = 1e-5) on the 10 strongest-gradient
   parameters. The receipt records **worst rel err 9.847e-11** against a
   1e-4 bar. I mutated the xent backward (`-= 1/len` → `+= 1/len`) and the
   suite went **red with 4 failures** — the FD check genuinely discriminates.
2. **Cross-runtime digest conformance.** `test/conformance.py` (stdlib only)
   hashes the same 32-scalar adversarial fixture (0, −0, 1, −1, π, e, 1/3, 0.1,
   1e-7, 1e21, 2^53, ±min-denormal, min-normal, max-double, the issue's own
   loss scalar, …) as `src/attncells.mjs` and asserts 32/32 identical digests
   plus 3/3 non-finite sentinels rejected fail-closed in both runtimes. **I ran
   it: `32/32`, `3/3`, `-0 == 0` agree, exit 0.** This is the same
   `scalarSha` preimage bug the fleet already knows from `quilt-nn` — here it is
   **fixed and cross-checked in two languages**, with a committed
   `test/scalar-expected-digests.txt` to pin against.
3. **The dtype is hashed, not assumed.** The preimage is
   `"f64|<len>|<big-endian IEEE-754 bytes>"` — dtype INSIDE the preimage, per
   cellgraph's rule 2. Mutating the tag `f64`→`f32` goes red with 2 failures.

**The honest limit, stated in the repo itself:** *"a bare hash chain cannot
detect truncation of its TAIL without an externally anchored tip — same as any
hash chain, including git."* That is the correct limit and it is stated once,
not buried.

**T5 is load-bearing, and I had to work out why.** Mutating any *single*
tamper detector survives:
`e.prev !== prev` check off → **survives**; `loss_sha` commitment off →
**survives**; the entry-`sha` recomputation off (`const expect = e.sha`) →
**survives**. So I disabled **all three at once** — and **T5 still caught the
forged loss** (a 4th detector fires). Conclusion: this is **defense in depth,
not theatre**. No single check is load-bearing, which is exactly the property
you want from a tamper detector. *My first reading — "three checks survived" —
was wrong, and the combined mutation is what proved it.*

**Weaknesses, honestly.** **NO CI at all** (no `.github/` directory) — a 10-test
suite, a Python conformance reference, and a 1200-epoch training receipt that
nothing re-runs. The suite is also **slow relative to its value** (T1 trains
1200 epochs). And T5's assertion is loose: `assert.match(why.reason, /sha|loss|seq|prev/)`
— any of four substrings satisfies it, so the test proves *tamper detected* but
not *which detector fired*. My all-3-disabled run is precisely what a loose
assertion hides.

---

## 5. `jev-net` — "a neural network whose neurons are JEV calls" — and a hardcoded laptop path ⭐

**What it does.** The concept is the surprise: not a pipeline that *uses* JEV,
but a network where the **JEV packet IS the activation carrier**, the **prism
projection IS the synaptic transfer**, and the **JEV→JEV spawn trigger IS the
recurrent iterator**. Each cell's judgment (`confidence`) is a presynaptic gate,
each typed extraction (`sub-question`, `constraint`, `mechanism`, `risk`,
`claim`, `counter`, `entity`, `anchor`) is a wavelength with a salience, and a
`spawn` verdict injects new components into the router at the next hop — making
the net an **iterator, not a one-shot fan-out**. Learning is Hebbian credit
assignment against a judge model, with thresholds that adapt (+2 pivotal ⇒
fires 3 % easier, noise ⇒ 3 % harder).

**Its committed state is internally consistent, and I checked it properly.**
`nets/state.json` (6 edges) against `runs/fwd-213130-16c5/learn.json` (7
cumulative updates): every edge's **final** weight matches the last update —
`input→mechanism 1.0` (2 updates), `input→skeptic 0.7707` (2),
`input→builder 0.6351` (1), `mechanism→builder 0.7939` (1),
`builder→skeptic 0.5243` (1), and **`skeptic→builder 0.7` with `n_updates: 0`**.
That last one is the README's own claim — *"only pathways that carried real
signal get credit — `skeptic→builder` stayed at 0.7 … No phantom credit"* —
and it is **receipted, not asserted**. (My first pass flagged two "mismatches";
they were intermediate steps of a cumulative list, not defects. The final
values all agree.)

**What is structurally wrong.** The repo **cannot run anywhere but the author's
laptop.** `jevnet/providers.py:23` does:

```python
for line in open('/home/z/my-project/.env.keys'):
```

and `jevnet/learn.py:47` does `sys.path.insert(0, '/home/z/my-project/cot-quilt')`.
This is **module-import-time** code, so it is not a config convenience — it is a
hard failure. Verified:

```
$ python3 run.py probe
FileNotFoundError: [Errno 2] No such file or directory: '/home/z/my-project/.env.keys'
```

**Every entry point dies before doing anything** — `forward`, `learn`, `show`,
even `probe`. There is no `--offline`, no env-var fallback, no `.env.example`.
Combined with **zero test files** and **zero CI**, the two committed run
directories (`fwd-212954-038c`, `fwd-213130-16c5`) are **unreproducible
artifacts**: the one honest-sounding property of the repo — a receipted
"no phantom credit" state — **cannot be re-derived by anyone else**. It is
checkable only by hand, against files.

**Class: a receipt that no one but the author can re-run.** The fleet already
knows versions of this (hardcoded `/tmp` paths in `xruntime-conformance`,
`git add file:../` deps in `substrate-*`). This one is worth naming because the
*idea* is strong and the *reproducibility* is zero: a research repo whose
headline claim is a learned weight table, whose evidence is a committed
`state.json`, and whose code cannot start.

---

## 6. `q16-trajectories` — integer-only identity, and a σ tuning loop that refuses to lie

**What it does.** Bridges `duke-lab` (a GAN with words — a generator argues with
a 16-feature critic until they converge in golden ratio) to `tidepool` (the
fleet's 16-dimensional vector context ocean). The walk *is* the artifact: every
round becomes an **integer point in ℚ¹⁶** (fixed-point ×1e6 — *rationals only,
floats never touch identity*), the final point is written into tidepool as a
`musician` artifact, and lineage queries ask the ocean who else lives near a
given point. Nearest-neighbour re-rank is by **exact integer cosine**,
verified against BigInt in tests.

**Why another agent should care.** Two pieces of discipline worth stealing:
- **The σ tuning loop** (`src/sigma-loop.js`) runs a `(persona × jitter)` grid
  under fuel caps **plus a measurement noise-floor probe**, and returns an
  *honest verdict on whether a requested σ target is reachable at all*. A
  tuner that can answer "no" is rare.
- The **GAN distill** uses an FNV-1a-64 witness RNG seeded from the fleet's own
  canary vector and a multiplicative {0,1} viability floor — **"zero ethos still
  sunsets"** — and books a hash-chained receipt for **every** candidate, kept
  *and* rejected. It reports its own measured numbers: *"first-3 coherence
  610.67 → last-3 651.33, kept 12/12"*, and the test is literally named
  `HONEST MEASURED CLAIM: late-ledger coherence vs first-ledger coherence`.

**Verified.** `npm test` → **15 passed, 0 failed**. The canary is honoured
*correctly*: `tests/gan-distill.test.js` asserts
`fnv1a64('café Δ 日本語') === 0x024a555471370b18dn`, which I independently
recomputed to `0x24a555471370b18d` ✔ (the leading zero is literal formatting;
the integer is the canonical one).

**Mutations.** `Q = 1000000` → `100000` → **red**; disabling the receipt-chain
verification (`fnv1a64(prev + r.payload) !== r.hash`) → **red**; renaming the
canary function → **red**. The suite discriminates all three.

**Two small things.** (a) The test *title* says `café Δ 日本语` (simplified 语)
while the code hashes `café Δ 日本語` (traditional 語). The code is right; the
title is a character-swapped trap in the one string the fleet most needs to
keep straight. (b) `node --test tests/` fails with `MODULE_NOT_FOUND` — the
suite only runs via the package script's per-file invocation. CI is green
(10 success / 1 historical failure on 2026-09-20, green since), and the
workflow triggers on `main` **and** `lane-n-q16-bridge`, so PRs are covered.

---

## 7. Secondary finding — `quilt-executor`: a red CI with a green local tree and no retrievable diagnosis

**What it does.** Four layers (providers → evaluator → decider with Thompson
Sampling + marginal-gain router → a hash-chained receipt ledger using the
candor/MOTH-family recipe: canonical JSON + FNV-1a-64, rivals preserved,
refusals hash-committed), plus a **cuOpt plugin** that frames fleet dispatch
as a 0-1 assignment LP.

**What is wrong.**
- **CI is 0 successes / 20 failures** (every run in the last 30 is a failure;
  the only workflow is `.github/workflows/ticks.yml` with 3 jobs). Yet **all
  three jobs pass locally on the same tree**: `python3 -m unittest discover -s tests -q`
  → `Ran 23 tests … OK (skipped=4)`; the `family-crosscheck` heredoc →
  `family recipe compatible` (rc 0); and `examples/fleet_tick.py --json` →
  refuses gracefully with `output_preview: "refused:KIMI_API_KEY unset"` and
  `chain_ok: true` — which is the repo's own doctrine (*"a refusal perceived is
  a tick completed"*) working as designed.
- **The per-step job payload for those runs is empty** (`total_count: 0` from
  `actions/runs/{id}/jobs`), so I **could not** read which step failed. I am
  reporting the red CI without a cause rather than guessing one.
- **README says "# 13 pins"; there are 23 test methods** (18 in
  `tests/test_core.py`, 5 in `tests/test_quilt_opt_bridge.py`), **4 of them
  skipped** via `@unittest.skipUnless(HAVE_SUBSTRATE, "quilt-optimization source
  checkout absent")`. Green CI, 4 tests never run, and the count in the README
  is wrong by ten.
- **No `.gitignore`** and **7 committed `__pycache__/*.pyc`** files tracked
  (same class as the already-reported `quilt-gpu-lab` committed `__pycache__`
  and `quilt-canary`'s 52 tracked `target/` artifacts — this fleet keeps
  shipping build output).

---

## 8. Method notes (carry forward)

- **Rank on code bytes by extension, minus vendored paths — never tree bytes and
  never API `size`.** The API-`size` top of this month's list is
  `StudyLog` (119,509 KB) and `Lucineer` (88,193 KB); both are 75–98 % vendored
  bytes. The code-bytes pass puts `quilt-attention`, `percept-plugs`,
  `dungeon-syncopation` and `q16-trajectories` on top immediately. The history
  -excess detector (`api_size_kb × 1024 > 50 × tree_bytes`) is a cheap
  "this repo's working tree is a skeleton over a huge history" flag: it fired on
  `lau-room-native` (688×), `lau-shell-spawn` (663×), `lau-tradition-proof`
  (844×), `lau-weather` (761×) — all `lau-*` Rust crates with 35–60 KB trees.
  **Those four remain unexamined and are the top recommendation for round 129.**
- **When a mutation survives, do not stop at "survived."** Ask *where the real
  guard is* and *what else carries the property.* `dungeon-syncopation`'s
  control law survives mutation in the runner and dies in `composer.js`;
  `quilt-attention`'s three tamper detectors each survive alone and the
  property still holds. **The combined mutation is the only honest test**, and
  the wrong reading of a survivor produces a false accusation.
- **Beware the mutation that breaks your own experiment.** My first seal test
  renamed an `export`, so the runner aborted with a *Node module error* — which
  I nearly reported as "the seal fired." It did not. **Mutate whitespace-only**
  when the claim is "this file is bound"; only the seal can then abort.
- **`if (!existsSync(cli)) build(cli)` inside a test is a silent skip.** Grep
  every suite for a fixed absolute build path.
- **A test *named* after a law is not a test of that law.** `dungeon-syncopation`
  has a test literally called "budget is capped" that asserts nothing about a
  budget, and the cap lives in code the suite never imports.
- **Distinguish "chain-verification is weak" from "the chain is well defended."**
  Disable all detectors at once before calling anything theatre.
- **A cumulative update list is not a set of current values.** `jev-net`'s
  `learn.json` lists `input→mechanism 0.8 → 0.92` and later `0.92 → 1.0`;
  comparing intermediate steps against the final `state.json` produces false
  mismatches. Compare the **last** update per edge.
- **Group `actions/runs` by `name`, not by `conclusion`** — `q16-trajectories`
  is green 10/11 with one historical failure, `moth-waveform` is 2/5,
  `quilt-executor` is 0/20. And `actions/runs/{id}/jobs` returns
  `total_count: 0` for older runs even when the run conclusion is readable.
- **Read the `pyproject.toml` / `package.json` dependency *comments*.**
  `moth-waveform`'s pinning rationale is the most useful paragraph in the repo,
  and it also tells you the calibration is shot statistics.
- **Environment:** `/workspace` NAS still at 100 % (EDQUOT) ⇒ all work in
  `/tmp`. `git fetch`/`push` needs `GIT_SSL_NO_VERIFY=1`. **PyPI is blocked**
  ⇒ `pytest`/`qiskit`/`numpy` cannot be installed; `unittest` suites run
  natively, pytest/qiskit suites can only be read. `node --test` works (v22.19.0).
  Background jobs need `(setsid nohup timeout -s KILL N cmd > log 2>&1 &)`.

---

## 9. What I did **not** verify

- `moth-waveform` — could not install `qiskit`/`quantumaudio` (PyPI blocked).
  The 3/5 CI figure is from run conclusions, not a local reproduction; the
  calibration numbers are quoted from the repo.
- `jev-net` — the learned state and the learn receipt are consistent
  (verified), but the *forward* pass and the Hebbian update could not be
  executed (no API keys, and the repo cannot import anyway).
- `quilt-executor` — the failing CI step could not be identified; the job
  payload is empty for those runs.
- Rust/Julia repos (`lau-*`, `ternary-*`, `grand-pattern-*`, `coral-reef`, …) —
  no `cargo`/`rustc` in this sandbox; inspected, not executed.
- The remaining ~2,700 unseen own repos (all with API size < 800 KB) were
  ranked but not individually read.
