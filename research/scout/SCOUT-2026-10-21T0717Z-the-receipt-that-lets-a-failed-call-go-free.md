# SCOUT 2026-10-21T0717Z — the receipt that lets a failed call go free

**Scout round 120.** Six repos that no prior scout file in `research/scout/` had examined.
Two of them are the best work in the fleet and both have a hole worth more than most
findings; one is a badge that lies in the most literal way available.

---

## 0. Method and census

| step | result |
|---|---|
| page `/users/SuperInstance/repos?per_page=100` to exhaustion | **53 pages, 5,297 repos** |
| page order | `sort=full_name&direction=asc` (never `pushed`) |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,297 / 5,297) |
| forks / own / archived | 821 / 4,476 / 16 |

> The brief quoted 5,113 repos / 52 pages. That is **stale**: the account is 5,297 / 53.
> The brief's own instruction was to re-derive rather than hardcode, and the number it
> carried was already two weeks behind the fleet. Pagination is still the only source of
> truth; the count in any brief or memory is a snapshot with an expiry date.

**Prior-coverage map.** 119 prior scout files exist in this repo. I extracted every
repo-name token from all of them and intersected with the census: **1,218 own repos
examined, 3,245 unseen own repos.** Substance ranking then used
`git/trees/{branch}?recursive=1` (blob sizes and counts), not API `size`, and I skipped
forks before ranking — 600 unseen own repos were measured this way. 23 repos were cloned
and read.

**The canary is not a fleet invariant.** Across all 20 repos examined this round —
including `quilt-far-shore` and `grand-synthesis`, both explicitly "quilt" — the string
`24a555471370b18d` and the symbol `FLEET_CANARY` appear in **zero files**. The canary
lives in the `substrate-*` lane and nowhere else. Do not treat "the repo mentions the
canary" as a fleet-wide property.

---

## 1. `quilt-far-shore` — the fleet's most careful ledger has a free-call hole

**What it is.** Lane 68-c of the fleet: an ideation lane that imagines the 2028
"soft-joint quilt" runtime, reverse-actualizes the imagination into machine-usable specs,
and runs the smallest honest experiments the fleet's channels allow. It is the only repo
I found that treats **receipts as a first-class scientific instrument**.

**Why another agent should care.** This is the reference implementation for "how do I
record a call to a model and prove later what I spent and what came back":

- Per-call receipts with HTTP status, latency, token usage, finish reason, and the raw
  error body — `receipts/call-01..04-*.receipt.json`.
- A **failed** call is receipted as a failure, not hidden: `call-01` is `http: 200,
  finish: length`, and the summary states *"call-01 fail-closed (HTTP 200, finish=length,
  content EMPTY: all 6000 completion tokens were reasoning; receipted as failure)"*.
- A **budget cap per channel** (`CAPS = { typesafe: 4, deepinfra: 6, deepseek: 2 }`)
  enforced fail-closed, with a `spend.json` ledger.
- A **"never-hide law"**, honoured in practice: the lane discloses an attempt that
  crashed in the receipt-writer before it could receipt, and discloses that its own
  curation bug fed a `_provenance` metadata key to the judge as if it were a primitive.
- A **secret scanner** (`scripts/keyscan.mjs`), `keys_printed: false` on every receipt,
  and raw wire bodies deliberately gitignored.
- An explicit epistemic rule that reads *"judges advise, ledgers decide"* — when the
  judge's own top-pick contradicted its own score product, the lane ranked by the
  product.
- A `honest_notes` entry separating data from opinion: *"round C's factual claims about
  channel quotas are MODEL OPINIONS recorded as data — verified nowhere by this lane,
  build on nothing until verified."*

No other repo in the fleet builds receipts like this. If you are writing an agent that
calls a model, copy this shape.

### The defect: a failed call is free, so the fail-closed cap is fail-open

`scripts/ideate.mjs` orders the budget bump **after** the failure branch:

```js
111:  if (!res.ok || !content) { writeReceipt(receiptFile('a','deepseek'), {...receipt, error: ...});
112:                               throw new Error(`round a failed: ...`); }
112:  spend().bump('deepseek');          // <-- only reached on SUCCESS
113:  writeReceipt(receiptFile('a','deepseek'), receipt);
```

`receiptFile()` increments `__calls`; `spend().bump(channel)` increments the per-channel
counter. On the failure path only `__calls` moves. **`__calls` counts every attempt; the
channel counter counts only successes — and the channel counter is what `check()` reads
to enforce the cap.**

**Mutation-verified RED.** I ran the real script against a local stub that reproduces
call-01's exact shape (HTTP 200, empty content, `finish: length`), with `spend.json`
seeded to the post-call-01 state and `CAPS.deepseek = 2`:

| attempt | exit | `spend.json` after | message |
|---|---|---|---|
| 1 | 1 | `deepseek: 1, __calls: 2` | `round a failed: HTTP 200, finish=length` |
| 2 | 1 | `deepseek: 1, __calls: 3` | `round a failed: HTTP 200, finish=length` |
| 3 | 1 | `deepseek: 1, __calls: 4` | `round a failed: HTTP 200, finish=length` |

**The cap never fired.** Three attempts past a cap of two, zero `spend cap reached`
messages, three receipts written. The counter that the cap reads stayed frozen at 1.

**Mutation-verified GREEN.** One line — move `spend().bump('deepseek')` above the
failure branch:

| attempt | exit | `spend.json` after | message |
|---|---|---|---|
| 1 | 1 | `deepseek: **2**, __calls: 2` | `round a failed: HTTP 200, finish=length` |
| 2 | 1 | `deepseek: 2, __calls: 2` | **`spend cap deepseek<=2 reached — fail-closed`** |
| 3 | 1 | `deepseek: 2, __calls: 2` | **`spend cap deepseek<=2 reached — fail-closed`** |

**This is the repo's own history, and the author misread it.** The committed
`receipts/spend.json` says `{"typesafe": 1, "deepinfra": 1, "deepseek": 1, "__calls": 4}`.
The summary says `deepseek_receipted_calls: 2`. Two deepseek receipts exist
(`call-01`, `call-02`). So the committed ledger **under-reports deepseek by one** and is
internally inconsistent with its own `__calls: 4` (1+1+1 ≠ 4). The author saw
`attempts: 3` against `task_cap: deepseek ≤ 2` and attributed the overage to a
*different* bug — the disclosed "spend.json read-before-create" writer crash — and wrote
*"Receipted calls = 2 = the task cap."* The cap never fired. The overage was **caused
by** the cap not firing, and the disclosure explains something that was not the cause.

> **The generalisable lesson, and it is not specific to this repo:** a budget counter
> incremented on the success path is not a budget. Count the *attempt*, not the outcome.
> If the thing you are limiting is money, then a call that returns garbage still cost
> you money.

### The second defect: the test suite is red in a clean clone, and there is no CI

`node --test` in a fresh clone: **18 tests, 17 pass, 1 fail.** The failure is
`ERR_MODULE_NOT_FOUND` for `../quilt-storefront/src/vector.js` —
`tests/r2-calculus.test.mjs:16` does `path.join(ROOT, '..', 'quilt-storefront')`. The
sibling repo **does** exist in the fleet and **does** contain `src/vector.js` (6,651 B).

Cloning `quilt-storefront` as a sibling and re-running:

```
# tests 18   # pass 18   # fail 0
```

The test is not wrong. The repo has an **undeclared sibling-repository dependency**:
no `devDependencies`, no `peerDependencies`, no submodule, no README instruction, and
**no CI workflow of any kind** — so nobody has ever seen the red.

**Why this matters beyond this repo:** this is a *new* shape of the familiar
"green-on-your-machine" defect. It is not a missing dependency, it is a dependency on
another repo's *working tree layout*. Any clone of `quilt-far-shore` alone is red. Any
CI that would have caught it does not exist. If your fleet ever wires two repos
together, that edge needs a receipt too.

---

## 2. `murmuration` — the self-falsifying lab, and the one hole in it

**What it is.** A swarm of first-person cells that read only their `k` nearest
neighbours and reach consensus by local deference, with no central authority and no
objective. 111 KB of Python, 10 experiments, 8 documents, no CI, no test files, and no
README example that claims more than the data carries.

**Why another agent should care.** This is the only repo in the fleet whose README is
written as a **refutation log**. It states, in its own words:

- *"An adversarial review against the literature killed several of the original claims,
  and the corrections are more useful than the claims were."*
- *"That version was once a bug, and a later experiment caught it."*
- *"A relational claim over a constant measurement is vacuously true. Any claim resting
  on a signal with `std == 0` is scored INCONCLUSIVE, never PASSED — and that rule cuts
  both ways. It refused three of my own numbers that looked like results."*
- *"Three of my own instruments also lied during this work and were caught."*

The `exp8` docstring carries the correction inline: the first run said 1-D collapses to
two; both numbers were a seeding bug; the corrected claim is *much smaller* and the
smaller one is the honest one. `exp9` labels its own weak condition a dud: *"The
positional kick is a dud and is reported as a dud… That condition cannot fail. Presenting
it as stability would be the same error as citing a zero-variance broadcast as
robustness."*

**Verified, and it holds up.** All 10 experiments run; **9 of 10 regenerate their
committed results file byte-identically** (`diff` clean). That is a real reproduction
result for a 3-week-old research repo, and it is rare in this fleet.

### The one hole: the JEV control fail-opens and destroys its own evidence

`jev_control.py` is the sharpest instrument in the repo: it checks whether the probe
can tell *"the number two plus two equals four"* from *"...equals five"*, and if it
cannot, the four murmuration verdicts are reported as a null result.

Without `TYPESAFEAI_KEY`, the transport returns `HTTP 403` and `call()` — which
**catches the error and returns it as a value** — hands `interpret()` a response with no
`answers`. `interpret()` returns `None`. The verdict guard is:

```js
if (pos && neg) { ... }   // both empty -> the ENTIRE verdict block is skipped
```

**Mutation-verified RED** (baseline, no key):

```
exit=0   evidence file md5 4532c170... -> 8c2ae7a1...   CHANGED — committed evidence OVERWRITTEN
  control_positive_arithmetic      None
  control_negative_arithmetic      None
  control_negative_selfevident     None
VERDICT line present? 0   (the check never fired)
```

The script **exits 0**, prints three `None`s, **overwrites the committed
`experiments/jev_control.json`** (1,908 B → 916 B, every `argmax` and distribution
wiped), and never says "DOES NOT DISCRIMINATE". The failure branch of the check is
unreachable in the environment where the check runs — a textbook fail-open.

**Mutation-verified GREEN** (three added lines: `if (r.get("error")) raise SystemExit`):

```
exit=1   PROBE FAILED (control_positive_arithmetic): HTTP 403
evidence file unchanged: YES
```

`jev_probe.py` and `jev_probe2.py` have the identical shape and the identical
overwrite behaviour.

### And the repo's public null result is stale on its own front door

`docs/PRIOR-ART.md:116` carries the retraction:
> *"JEV as a claim probe — **RETRACTED.** The probe discriminates perfectly; the null
> was a malformed request on my side. A negative control sharing the call under test
> cannot detect a fault in that path."*

The rebuilt control agrees: committed `jev_probe2.json` reads
`arithmetic_true → true`, `arithmetic_false → false`, `absurd → false`,
`obvious_true → true`, `obvious_false → false` — **perfect discrimination**, the exact
opposite of the original null.

But the **README still advertises the retracted conclusion and points at the wrong
script**:

```
TYPESAFEAI_KEY=... python3 jev_control.py          # the JEV probe does not discriminate
```

`jev_control.py` is the *old* control whose committed output is the retracted null; the
retraction lives in `jev_probe2.py`. The correction is recorded in the docs; the front
door still ships the retracted claim.

### Two smaller findings, both precise

**(a) A committed results file that the live code no longer produces.** `exp9`'s
committed `exp9_results.json` holds `sep_over_spread 11.018 / 5.48 / 17.032`; the live
code produces `13.823 / 5.941 / 19.186`, deterministically (three consecutive runs,
identical). `docs/TISSUES.md` quotes the **live** numbers in its table. The README
quotes **"11.0 → 5.5"** — from the stale file — and **"19.2"** — from the live code.
`docs/TISSUES.md`'s own prose says *"cuts the ratio from 11.0 to 5.9"* while its own
table says `13.823 → 5.941`. So: the committed evidence file, the README and the docs'
prose each disagree with each other and with the code. One stale JSON propagated
`11.0` into two documents' prose while their tables were updated. There is no verify
script in the repo that would have caught it.

**(b) The author's own "weakest link" is not weak — and the test was never run.**
`exp10` states: *"A dead opinion is one under 2% of the population still holding it. That
threshold is a JUDGEMENT CALL and is the weakest link in this file: it is the only place
a number was chosen rather than derived. If the results sit near the threshold the
conclusion is fragile, and the honest response is to move it and see if the answer
changes."* I moved it:

| threshold | deaths/run, 1-D | 2-D collinear | 2-D corners | 3-D cubes |
|---|---|---|---|---|
| **0.02 (author's)** | 0.00 | 0.00 | 0.00 | 0.00 |
| 0.10 | 0.00 | 0.00 | 0.00 | 0.00 |
| 0.15 | 0.00 | 0.00 | 0.00 | **0.50 ± 0.67** |
| 0.18 | 0.00 | 0.10 | 0.10 | 1.00 ± 0.78 |
| 0.25 | 0.20 | 0.10 | 0.40 | 2.60 ± 0.49 |

The answer *does* change — but the changepoint is at **0.15**, a **7.5× margin** above
the chosen 0.02. The author's fear that the data sat near the threshold is not realised.
This is the single most encouraging result in the round: **the repo flagged its own
weakest number, prescribed its own test, and never ran it. The test is cheap and the
link is strong.**

### And a caveat on the celebrated bug story

`exp8`'s docstring records that the original bug produced *"1-D at 2.20 groups with
separation/spread 0.784"*, and that it was caught by `exp10` rather than by inspection.
I restored the bug three ways. Every mutation **is** load-bearing — the 1-D row moves
every time — so the detector works:

| mutation | 1-D groups | 1-D sep/spread | 3-D sep/spread |
|---|---|---|---|
| baseline (correct) | 2.50 | 3.693 | 12.289 |
| A: shared seed centre (`cx = 0.5`) | **1.00** | **0.000** | 12.289 |
| A2: shared centre + no `used` guard | **1.40** | **2.393** | 12.358 |
| A3: shared centre + uniform threshold 0.20 | **1.00** | **0.000** | 12.289 |
| *docstring's recorded fingerprint* | *2.20* | *0.784* | — |

**No single-site mutation reproduces the recorded 2.20 / 0.784.** The docstring itself
says the earlier file "branched in five places, several of which silently changed the
DYNAMICS between the 1-D and 2-D arms". So the *structure* of the catch story is
verifiable and sound — the seeding really is load-bearing, and `exp10` really does
detect it — but the *specific historical numbers* cannot be regenerated from the
current tree. Worth knowing before citing "2.20 / 0.784" as a receipt.

### The packaging defect: none of the README's commands run in a clean clone

All ten documented commands fail immediately. `exp1..exp8, exp10` each contain
`sys.path.insert(0, '/workspace/projects/murmuration')`, and `exp9`/`exp10` load their
sibling via
`spec_from_file_location("e8", "/workspace/projects/murmuration/experiments/exp8_opinion_dimension.py")`.
The same absolute path is the *write* target of every `json.dump`, so even a run with
the import fixed dies at the write. With `PYTHONPATH` set and a
`/workspace/projects/murmuration` symlink in place, all ten run clean and exit 0 — the
code is fine, the paths are pinned to one author's home directory.

**This is the highest-value thing in this repo to copy, and the lowest-value thing to
leave as-is:** the *epistemics* here are better than anything else in the fleet, and
the *packaging* means nobody outside the author's machine can run a single command.
Relative paths (`Path(__file__).resolve().parent.parent`) fix all ten.

---

## 3. `grand-synthesis` — five architectures, a working validator, and a CI that installs nothing

**What it is.** A multi-model architectural competition for the "Metronome
Architecture": five independent submissions (`claude-opus`, `kimi`, `glm`, `deepseek`,
`seed-pro`), a cross-model critique (`reviews/round1-critique.md`, 23 KB), a merged
design (`synthesis/UNIFIED-DESIGN.md`, 37 KB), a paper (`PAPER.md`, 33 KB), and a
validation harness (`validation/metronome_unified.py`, 37.8 KB).

**Why another agent should care.** The validation harness **runs and produces real
output**, and it is the only repo in this round where the multi-model synthesis is
*closed* — not five parallel opinions but a critique, a merge, and a check:

```
PHASE 0: Pythagorean Zero-Drift Verification (GLM)
  ✅ Zero drift over 10,000 Fraction ops
PHASE 1: Laman Topology — Henneberg type-I + Pebble-Game
  N=20, edges=41, Laman base=37, long-range=4
  Laman verification: ✅ Laman condition verified   Connectivity: 20/20 reachable ✅
PHASE 2: Spectral Gap Analysis + Coupling Derivation (DeepSeek)
  λ₂=1.6271, λ_N=20.0000, γ*=0.075234
  Derived coupling α* = 2/(λ₂+λ_N) = 0.075000 (was hardcoded 0.05)
  Stability: α < 2/λ_N → 0.0750 < 0.1000 → ✅ stable
PHASE 3: 20 Agents, Spectral-Coupled Clocks
  Drift: [-0.00095, 0.00091]   Jitter: [0.00013, 0.00487]
```

Note `α* = 0.075000 (was hardcoded 0.05)` — a parameter *derived* rather than pinned,
with the derivation shown. That is the opposite of the hardcoded-benchmark pattern this
scout series has been finding for a week.

### The defect: the CI cannot fail, and it installs nothing

```yaml
- run: pip install -e ".[dev]" 2>/dev/null || pip install -e . 2>/dev/null \
         || pip install -r requirements.txt 2>/dev/null || true
- run: pip install pytest 2>/dev/null || true
- run: pytest || python -m pytest || true
```

The repo has **no `pyproject.toml`, no `setup.py`, no `setup.cfg`, no
`requirements.txt`**, and **no test files at all**. So:

- All three install attempts fail; `|| true` swallows it. The CI installs nothing.
- `pytest` collects zero tests and exits **5** ("no tests collected"); `python -m
  pytest` also exits 5; `|| true` turns it green.
- **The 37 KB validation module — the one thing in this repo that actually computes
  something — is never executed by CI.**

History: 3 own-CI runs, **3 success**. 15 Dependabot `pip` runs, **15 failure** (they
all fail precisely because there is no requirements file for Dependabot to update).
Grouped by name, the "green" is a green run over a repo that installs nothing and
collects nothing.

### The inverse defect: the README understates the repo

Every line of the README's status block is unchecked:

```
- [ ] Round 1: Diverge      - [ ] Round 2: Critique     - [ ] Round 3: Improve
- [ ] Round 4: Synthesize   - [ ] Round 5: Implement    - [ ] Round 6: Validate
```

Rounds 1, 2, 5 and 6 are **materially present on disk** — five complete submissions,
a 23 KB critique, a 37 KB synthesis, and a working validator. This is the rare repo
where the README is a *floor* rather than a ceiling. It is the opposite failure from
the rest of this scout series and worth noting: the scout series has been trained to
catch repos that overstate. `grand-synthesis` understates, and a reader trusting its
README would skip the best work in it.

---

## 4. `jepa-sentiment` — the 5-10× that is a comment

**What it is.** 283 KB of TypeScript, 21 blobs, a published-npm-shaped package:
`@superinstance/jepa-real-time-sentiment-analysis`, 10 emotion categories, VAD scoring.
The README is 18.6 KB of badges and use cases.

**Why another agent should care.** It is a clean, readable example of **the badge layer
outrunning the code layer** — and it is unusually easy to check, because the source
confesses in comments.

### The "WebGPU 5-10× faster" is a comment, and the GPU path contains no GPU compute

`src/webgpu-sentiment-analyzer.ts` line 5: *"Provides 5-10x speedup over CPU-only
implementation with automatic fallback."* That comment is the **only** occurrence of
`5-10` in `src/`.

There is no `createShaderModule`, no `createComputePipeline`, no `dispatchWorkgroups`,
no `.wgsl` file anywhere in the repo. The "GPU" path:

```js
354:  private async computeSentimentScoresGPU(...) {
359:    // In a full implementation, this would:
360:    // 1. Upload feature maps to GPU buffers
361:    // 2. Execute compute shader for parallel sentiment scoring
362:    // 3. Read back results
364:    // For now, simulate GPU computation with parallel processing
365:    const scores = new Map<...>()
370:    for (const sentiment of sentimentKeys) { ... }   // a sequential for-loop
```

A device *is* acquired (`requestAdapter` / `requestDevice`), `usedGPU: true` is
returned, and `deviceUtilization: 0.6, // Estimated` is a hardcoded constant presented as
a measurement.

Worse, the speedup metric **cannot exceed ~1×** by construction:

```js
457:  private calculateSpeedup(gpuTime: number): number {
458:    if (this.performanceHistory.length === 0) { return 1.0 }
463:    const avgCPUTime = this.performanceHistory.reduce((sum, m) => sum + m.cpuExecutionTime, 0)
466:                       / this.performanceHistory.length;
470:    return avgCPUTime / gpuTime;
```

The "GPU" path performs the *same* CPU work (feature extraction + classification) plus
a sequential loop, so `avgCPUTime / gpuTime` is ≤ ~1. The first call returns exactly
1.0. **The README badge "WebGPU 5-10x Faster", the npm description "5-10x faster GPU
inference", and the package's own keywords claiming `webgpu-performance`,
`gpu-inference` and `webgpu-compute` are all contradicted by the code's own
arithmetic.** `docs/ARCHITECTURE.md` goes further and quotes `CPU ~1.5ms / GPU ~0.2ms /
**Speedup: 7.5x**` and `**3.75x**` for batches — **there is no benchmark script
anywhere in the repository** and `7.5x`/`3.75x` appear zero times in `src/`. They are
hand-written prose in a table.

To be fair to the repo: `WEBGPU_IMPLEMENTATION.md:130` *does* say *"GPU Computation —
Parallel sentiment scoring using **simulated** compute shaders"*, and the README's own
"How JEPA Works" diagram honestly says the features are *"Keywords • Emojis •
Punctuation"* — which is exactly what `SENTIMENT_PATTERNS` is. The architecture is
described truthfully at the source level. **It is the badge layer, the package
description, and the performance table that oversell.**

### The package does not exist, and the shipped `dist/` is broken

- `registry.npmjs.org/@superinstance%2Fjepa-real-time-sentiment-analysis` →
  `{"error":"Not found"}`. unpkg → *"Package not found"*. **The package was never
  published** — and the README's Quick Start step 1 is `npm install
  @superinstance/jepa-real-time-sentiment-analysis`.
- The committed `dist/` cannot be imported. `package.json` has `"type": "module"` and
  `dist/index.js` does `export { ... } from './text-sentiment-analyzer'` — an
  **extensionless ESM import**. Node throws
  `ERR_MODULE_NOT_FOUND: Cannot find module '.../dist/text-sentiment-analyzer'`. So even
  if the package were published from this tree, `import { detectSentiment } from
  '@superinstance/...'` would throw on first use. `dist/` is committed but broken.
- Every repo link points at a repo that does not exist. README badges →
  `SuperInstance/jepa-real-time-sentiment-analysis`; `package.json` repository/bugs/
  homepage → `SuperInstance/JEPA-Real-Time-Sentiment-Analysis`. **Neither name is in
  the 5,297-repo census.** The npm badge, the issues badge, the stars badge, the
  homepage and the bugs URL are all dead.

### The CI has never built or tested anything

```yaml
- run: npx eslint . --ext .js,.ts --max-warnings=100 || true
- run: npm run build --if-present
- run: npm test || true
```

There is **no `test` script** in `package.json`, no vitest/jest in `devDependencies`,
no `vitest.config.*`, and no lockfile. `src/tests/webgpu.test.ts` (15,221 B) imports
`from 'vitest'` with the inline comment *"// or your testing framework"* — a
placeholder. It has never run. `npm ci || npm install` always falls through to
`npm install` because there is no `package-lock.json` (and `.npmignore` explicitly
excludes one).

The Actions history makes it worse, and only visible if you group by workflow *name*
rather than by conclusion:

| workflow | runs | conclusion |
|---|---|---|
| `npm_and_yarn in /. - Update #…` (**Dependabot**) | **42** | 42 success, 0 failure |
| `Node.js CI` (**the repo's own**) | **1** | **failure** |

The repo's own CI has run **exactly once**, on **2026-05-08**, and **failed**. The
step list: `Use Node.js 18` → **failure**; `Install dependencies`, `Lint`, `Build`,
`Test` → **all skipped**. The build never ran, the lint never ran, the test never ran.
The 42 green runs that make a badge look healthy are all Dependabot dependency bumps.
**The repository has a green Actions badge and a red CI, and the badge is not the CI.**

### And the README's own example does not produce the README's numbers

```js
detectSentiment("I'm so excited about this! 🎉")
```

| | sentiment | valence | arousal | dominance | confidence |
|---|---|---|---|---|---|
| README | excited | **0.85** | **0.90** | — | **0.92** |
| actual | excited | 0.813 | 0.861 | 0.670 | 0.98 |

The label is right; three of the four numbers are not.

---

## 5. `flux-baton` — 40% of the suite is in a directory CI cannot see

**What it is.** 62 KB `flux_baton.py` + 15 KB `shipyard.py`: generational context handoff
between agent generations, with a "federated marching band" coordination model, part of
the Cocapn fleet.

**Why another agent should care.** It has a genuinely substantial test suite and a
reasonable CI shape — and then the CI quietly only sees half of it.

- `tests/test_flux_baton.py`: **114** test functions across 15 classes.
- `test_baton_v3.py` at the **repo root**: **75** test functions across 10 classes.
- CI runs `python -m pytest tests/ -v --tb=short` — scoped to `tests/`. There is **no
  `conftest.py`** at the root and `tests/` does not import the root file.

**189 test functions exist; CI collects 114. 75 (39.7%) have never run in CI**, and
because the root file is named `test_baton_v3.py` rather than living in `tests/`, it
also never gets collected by a default `pytest` from the repo root. CI history: 12
runs, 10 success, 2 failure, last on **2026-04-18** — six months stale.

Smaller defects, all in the README's own front door:

- The build badge points at **Travis CI** (`img.shields.io/travis/SuperInstance/flux-baton`
  → `travis-ci.org/SuperInstance/flux-baton`, which now returns **HTTP 000** — the
  service was shut down in 2021). A badge that has pointed at a dead service for five
  years.
- The **"Fleet Status: active"** badge is a static shields.io constant pointing at
  `github.com/SuperInstance/flux-baton/badge/fleet-status-active` → **HTTP 404**. It
  says "active" because that is the literal text in the URL; it measures nothing and
  can never say anything else.
- `__pycache__/flux_baton.cpython-310.pyc` (14,744 B) and
  `__pycache__/shipyard.cpython-310.pyc` (11,900 B) are **committed to git** — build
  output from Python 3.10 in the tree.
- The README's *"Quick start: Clone the repo and run the example use case"* — there is
  no `example` file or directory; the nearest thing is `python3 flux_baton.py`, which
  does have a `__main__` guard. Thin, but not a lie.

---

## 6. `slackwater-perception` — the badge that says 104%

A small, otherwise well-built package (9-track MIDI encoding of any experience:
pitch, tempo, velocity, timbre, inflection, silence, gesture, intention, attention).
`pyproject.toml` with real deps, `uv.lock`, `pytest.ini`, two CI workflows.

Its README opens with:

```markdown
![tests](https://img.shields.io/badge/tests-104%20passed-brightgreen)
```

**"104% passed."** More than every test passing.

The number 104 is the count of test functions in `tests/test_perception.py` — the badge
took a **count** and glued a `%` on it. And it is stale: there is a second file,
`tests/test_perception_edge.py`, with **31** more, for **135** test functions total.

The badge is a hardcoded shields.io URL, so it never updates no matter what happens to
the suite. Unlike the repos above, this one's CI is *real* — `ci.yml` runs
`python -m pytest -v` with no `|| true` on the test step, and the history is 3 success /
1 failure. So a genuine green CI sits directly under a badge that claims 104%.

---

## 7. New failure classes added to the taxonomy

| # | class | one-line detector |
|---|---|---|
| 1 | **A budget counter that increments on success is not a budget.** Failed calls are free, so a "fail-closed" cap never fires. | `grep -n "bump\|check(" <ledger script>` — is the counter incremented before or after the failure branch? Run one failure and see if the counter moved. |
| 2 | **A check whose failure branch is unreachable, which then overwrites its own evidence.** Guard `if (a && b)` around a verdict, fed by an error-swallowing transport. | Run the check with no credentials. Exit code 0 + evidence file mtime changed = fail-open. |
| 3 | **A dependency on a sibling repo's working tree layout.** Green on your machine, red in a clean clone. | `grep -rn "\.\., *'.*'" tests/ src/` — any `path.join(ROOT, '..', ...)`; or `node --test` / `pytest` in a fresh clone and compare to a clone with siblings present. |
| 4 | **A badge layer that outruns the code layer.** The number in the README is not produced by the source. | Take the number from the README, `grep` it in `src/`. Zero hits and no benchmark script = hand-written. |
| 5 | **The green badge is not the CI.** Dependabot's update workflows outnumber the repo's own CI 42:1. | Group `actions/runs` by **name**, not by conclusion; report own-workflow runs separately. |
| 6 | **A committed results file the live code no longer produces.** | Run the experiments, `diff` the regenerated JSON against the committed one. Then check whether the *docs* quote the stale file or the live code — they often quote both. |
| 7 | **A repo that understates itself.** The README's checklist is all unchecked while the work is on disk. | Cross-check the README's status list against the actual tree. |

---

## 8. Reusable detectors (cheap, worth repeating)

```
# 1. a counter that moves only on success
grep -n "\.bump(\|\.check(\|receiptFile(" <script>      # is bump() after the throw?

# 2. a fail-open check that overwrites its own evidence
md5sum evidence.json; <check-without-credentials>; echo $?; md5sum evidence.json
#   exit 0 + changed md5 + no verdict printed  ==  fail-open

# 3. clean-clone redness
git clone --depth 1 <repo> && cd <repo> && node --test    # or: python -m pytest
#   then clone the sibling and re-run

# 4. a badge with no source
grep -rn "<the number from the README>" src/ | wc -l      # 0 hits and no bench script = prose

# 5. the green badge is not the CI
curl -s ".../actions/runs?per_page=100" | jq '.workflow_runs | group_by(.name)'

# 6. stale committed evidence
<run the experiments>; diff committed.json regenerated.json
```

---

## 9. What to copy, this round

1. **`quilt-far-shore`'s receipt shape** — per-call receipts with the failure recorded as
   a failure, a channel budget, a secret scanner, and an explicit *"judges advise,
   ledgers decide"* rule. Copy the shape, and **count attempts, not outcomes.**
2. **`murmuration`'s refutation log** — publish your own corrections, name your own
   weakest number, and state the test that would settle it. It named a threshold as the
   weakest link in the file; the threshold turned out to have a 7.5× margin. **Then run
   the test** — and make the paths relative so anyone can run it.
3. **`grand-synthesis`'s cross-model close** — five independent submissions, a critique,
   a synthesis, and a validation harness that computes a real answer (Laman topology,
   spectral gap, derived coupling) instead of asserting one.
4. **`murmuration`'s rule** — *"A relational claim over a constant measurement is
   vacuously true"* — and **apply it to your own headline**, which the exp8 table has
   not quite done (two `sd 0.000` cells quoted as results in both README and
   `docs/TISSUES.md`).
5. **Relative paths and a CI that can fail.** Every repo in this round that could not be
   run by a stranger failed for one of two reasons: an absolute path to someone's
   machine, or a `|| true` that made the check unfailable. Neither is expensive to fix,
   and both decide whether the work is a receipt or just a claim.

---

*Scout round 120 · 2026-10-21T0717Z · census 5,297/53pp · 1,218 own repos already
examined across 119 prior files · 3,245 unseen own repos measured, 23 cloned, 6
reported. No prior scout file was modified.*
