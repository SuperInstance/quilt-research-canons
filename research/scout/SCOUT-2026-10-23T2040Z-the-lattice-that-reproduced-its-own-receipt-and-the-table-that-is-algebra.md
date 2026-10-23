# SCOUT 2026-10-23T2040Z — the lattice whose receipt I re-derived live, the results table that is algebra, and the reports that ship without their data

**Scout:** fleet-scout round 135
**Census re-derived:** 2026-10-23T19:19Z -> 19:26Z (independent re-derivation; matches rounds 133/134 exactly)
**Prior corpus:** 240 `.md` files / 3.69 MB under `research/` in `SuperInstance/quilt-research-canons`
**Unseen own repos examined this round:** 3,405 tree-scanned, 1,100+ read, 12 cloned, 6 reported

---

## Census (method receipts)

| Check | Result |
|---|---|
| Pages fetched | 54 (`sort=full_name&direction=asc`, `per_page=100`) |
| Rows returned | **5,307** |
| `unique_by(.full_name) == rows_returned` | 5,307 == 5,307 -> **ASSERT PASS**, 0 dupes |
| `rows_returned == public_repos` | 5,307 == 5,307 -> **ASSERT PASS** |
| Page-boundary monotonicity | PASS (asserted with `casefold()`, not `==`) |
| Forks / own / archived | 821 / **4,486** / 16 (the brief's "816 forks" is stale) |
| Distinct repos named in 240 prior reports | 1,081 |
| **Own repos never examined** (2-clause test) | **3,405** (round 133: 3,411) |

**The "unexamined" test needs two clauses** (carried forward from round 133): a name appearing `>=2x` in the corpus **or** being the subject of a markdown heading counts as examined. I rebuilt the set from the corpus (tokenize once into a 43,223-entry Counter, then look up) rather than from memory, because a remembered set silently re-inflates the pool.

**Ranking** was on **code bytes by extension, minus vendored paths** — not API `size` (git history) and not name prefix. 3,405 tree scans via `git/trees/{branch}?recursive=1`; 3,366 returned a tree, **39 returned 409 "Git Repository is empty"** (class (cl), round 133 found 40).

---

## The short version

- **One repo's headline receipt I reproduced live**, twice, against the real API — 600 code-labelled questions and a 300-case model-upgrade bench. The committed numbers came back within noise and `0 wrong GOs` reproduced in every run.
- **Three repos in this report have a test suite that has never executed in their own history** (one because its crate cannot build, one because it has no CI at all, one because its CI has never passed).
- **One "results" table is algebra**: two columns that must agree because they are computed in one loop, and a third column that is a constant 0%.
- **One repo ships 25 measurement reports and zero audio files** — the numbers are sound and the experiment is unreachable.
- **The fleet's canary has a second home**, outside the lane the prior rounds mapped.

---

## #1 - `jev-lattice` - the best epistemics machine in the fleet, and I re-derived its receipts against the live API

**What it is.** Deterministic GO / OPEN / REFUTED / CONFLICT gates for software decisions. Evidence arrives as "proofs" from a mix of verifiers (TypeSafe Jev, deterministic parsers, LLMs); the **verdict is computed by deterministic code, never by a model**. Four surfaces from one schema: a JS library, an MCP server (stdio), a Cloudflare Worker (MCP over HTTP, a Durable Object per lattice) and a browser UI.

**Why another agent should care — because it is the only place in the fleet where the claim and the run are both present, and I could check both.**

1. **The suite is real and offline.** `node --test tests/*.test.mjs` in a clean clone: **145/145 pass, 0 fail**, no network, no tokens.
2. **CI is alive.** 46 runs: `ci` 21 success / 1 failure, `slo` 23 success, newest **2026-10-23T19:20:53Z** — about forty minutes before I looked. This is not a repo that was green once.
3. **I reproduced the committed receipt live.** `experiments/calibration.mjs` generates random `redis.conf` files and asks yes/no questions whose answers a **deterministic parser** computes — so "labelled by code" is literal, not a model grading a model. I re-ran the exact commands behind the committed artifacts:

| | committed (2026-10-18T00:37:46Z) | **my live run (2026-10-23T19:5xZ)** |
|---|---|---|
| n30 seed 7 — accuracy | 0.990 | **0.997** |
| n30 seed 7 — Brier / ECE | 0.009 / 0.047 | **0.007 / 0.048** |
| n30 seed 99 — accuracy | 0.997 | **1.000** |
| n30 seed 99 — Brier / ECE | 0.004 / 0.039 | **0.003 / 0.033** |
| mean over 600 questions | 0.9935 | **0.9985** |
| **wrong GOs at 0.8 / 0.9 / 0.95** | **0 / 0 / 0** | **0 / 0 / 0** |

   The README's headline — *"99–99.7% accurate on 600 config questions labelled by code, with **0 wrong GOs**"* — **reproduces**, and my live run is marginally *better* than the committed one. `0 wrong GOs` is the number a gate actually cares about, and it held at **all six** thresholds across **both** committed runs and **both** of mine.
4. **I reproduced the model-upgrade receipt live too.** `node experiments/model-upgrade.mjs --n 30 --seed 11` (90 API calls, 1.4 s):

| | committed | **my live run** |
|---|---|---|
| re-ask noise (same model, twice) | 9 flips (0.030), mean_abs_dp 0.0058 | **8 flips (0.027), 0.0062** |
| upgrade 1.13.0 -> 1.14.0 | 14 flips (0.047), 0.0158 | **17 flips (0.057), 0.0155** |
| wrong GOs, three passes | 0 / 0 / 0 | **0 / 0 / 0** |
| decided correct | 267 / 270 / 271 | **268 / 270 / 273** |

   The claim *"an upgrade moved ~5% of verdicts with the same accuracy, so pin the model"* reproduces: **0 wrong GOs in all three passes**, and the upgrade rate (5.7%) sits inside the README's stated 4.7–6.2% band.
5. **The suite is mutation-verified falsifiable, 3/3.** Not asserted — measured:

| Mutation | Result |
|---|---|
| **M1** `currentPaths` keeps the MAX reading instead of the LATEST | **3 RED** (142/145) |
| **M2** gate `valid.length >= required` -> `> required` | **41 RED** (104/146) |
| **M3** `independenceKey` drops the provider from the key | **2 RED** (143/145) |

   Each mutation was asserted present in the file *before* the suite ran; the tree was restored and md5-verified afterwards (`0b9c451b790706fafc7687b88f1b33fa`, `git status` clean).
6. **The design detail other agents should copy.** `independenceKey(p)` is `${source_type}:${provider}` — two proofs from the same provider collapse to **one** verification path, so "2 independent proofs" cannot be satisfied by one source twice. And `currentPaths` deliberately keeps the **latest** reading per path rather than the best, with the reason written down: *"Keeping the max would let a caller re-ask a non-deterministic verifier until it passes (cherry-picking)."* M1 is the mutation that removes that property, and the suite catches it. That is the rare case of a **stated design invariant with a test that fails when it is removed**.

**Structurally wrong (two small things, both worth fixing):**

- **`/v1/models` under-reports the servable model set.** It lists exactly two models, `jev-latest` and `jev-preview` — but `jev-1.13.0` and `jev-1.14.0` are **both still servable** (HTTP 200, `"model":"jev-1.14.0"`). And `jev-latest` is an **alias that serves 1.14.0**. So the inventory is not the model set, and the model-upgrade experiment — the one that justifies *"pin the model"* — depends on versions the inventory does not show.
- **The receipts are live artifacts, not frozen ones.** `experiments/model-upgrade.mjs:72` writes `results/model-upgrade-s${seed}.json` **in place**, overwriting the committed receipt on every run. (My live run did exactly that; I restored it with `git checkout` and verified the tree is clean.) A committed receipt that changes under you cannot be diffed against without a checkout — the flip to "a live artifact" is good epistemics, but it should be declared, not discovered.
- **One honest gap in the README's own numbers.** The committed receipt's own upgrade/re-ask ratio is 14/9 = **1.56x**, below the README's stated *"2–2.5x the re-ask rate"*; my live run gives 17/8 = **2.13x**, inside the band. The band is presumably an observation across seeds, but the committed artifact alone does not underwrite it.

---

## #2 - `construct-coordination` - a results table that is algebra, in a crate that cannot build, under a CI that has never been green

**What it is.** "The Room Where the Fleet Talks to Itself" — the fleet's shared *intent* repo: `notes/{instance}/`, `proposals/[CONSENSUS]`, `ECOSYSTEM-MAP.md`, `SCIENCE-PAPER.md`, and `experiments/` holding actual Rust experiments.

**Why another agent should care:** it contains the fleet's cleanest *self-critique* (below) and the fleet's cleanest *results-table-that-is-not-a-receipt*.

**The defect, in three layers.** `experiments/seed-stability/RESULTS.md` is a 50-row table of "Seed Stability Under Mutation". Every row reads:

```
| S0 | 1%  | 0.6  | 0.6  | 0%  |
| S0 | 5%  | 3.2  | 3.2  | 0%  |
...   ...  ...   ...   ...
```

- **(a) "Avg Hamming" is the analytic expectation, not a measurement.** It equals `rate x 64` exactly at every rate (0.64 / 3.20 / 6.40 / 12.80 / 32.00). The mutator is deterministic — `FINDINGS.md` says so outright: *"The `SeedMutator` uses deterministic modular thresholds (`threshold % 100 < rate x 100`), which creates this clean linear relationship."* The proof that it is an identity: **all ten seeds S0..S9 produce byte-identical rows.** A real measurement of 100 trials would show binomial spread between seeds; identical rows across ten different seeds means the quantity was never sampled.
- **(b) "Avg Output Changes" is the same loop, not a second measurement.** `hamming_distance` counts differing values over the union of keys; `output_changes` counts differing values over the intersection. When the mutator preserves the key set — which it does — **the two are the same number computed twice**, in the same `for trial` loop, into two columns of the same table.
- **(c) "Conservation %" is a constant 0%, because the check cannot pass.** `check_conservation` compares `gamma + H` against `target = 1.283 - 0.159*ln(V)`. At V=64 the target is **0.622**; a uniform trit distribution gives `gamma = 1/3` and `H = log2(3) = 1.585`, so `actual = 1.918` — off by **1.296** against a tolerance of **0.5**. The check is arithmetically incapable of passing for the seeds the generator produces, so 0% is a constant, not a result. (`FINDINGS.md` reaches the same conclusion from the other end: *"the formula doesn't apply to this data structure... the spec describes a different seed format."*)

**And the experiment cannot be built anywhere but the author's machine.** `experiments/seed-stability/Cargo.toml` declares `ternary-seed`, `ternary-genome`, `ternary-dice`, `ternary-arena` as `path = "../../../<sibling>"` — **outside the repository**. The root `Cargo.toml` does the same with **eight** siblings (`../circuit-breaker`, `../rate-limiter`, `../health-check`, `../retry-backoff`, `../load-balancer`, `../config-center`, `../feature-flag`, `../service-discovery`). The CI workflow checks out **one** repository.

**And the CI proves it.** 120 runs, `CI` **92 failures**, `Rust CI` **8 failures**, **0 successes**, last 2026-06-18. The newest run's step list is the receipt:

```
4  Run cargo check        -> failure
5  Run cargo test         -> skipped
6  Run cargo clippy -D warnings -> skipped
```

`cargo check` fails on the unresolvable path dependencies, so the test and clippy steps are **skipped** (class (d)) — the crate's tests have **never run in the repo's history**, and 92 identical red runs have been the fleet's only feedback.

**The good part, and it is genuinely good.** `FINDINGS.md` is a model of honest negative reporting: it identifies the linear scaling as a property of the deterministic mutator, names the spec/crate misalignment as the root cause of the 0%, and reports that cross-breeding produces **0 shared keys** so the combiner's conflict resolution "was never triggered" — i.e. *"cross-breeding is just union, not breeding."* It also reports that tournament winners depend on bracket position because RPS is non-transitive, and concludes *"tournament winners aren't 'better seeds' — they're better-matched seeds."* **Copy this document.** It is the fleet's best template for "my experiment found nothing, and here is precisely why."

**The mismatch to fix:** the *findings* are honest; the *table* is presented as a receipt for an experiment that (i) cannot be built in a clean clone and (ii) measures two identities and one constant. A reader who only sees `RESULTS.md` draws the wrong conclusion.

---

## #3 - `songforge` - 25 measurement reports, zero audio files

**What it is.** AI song covers from rough recordings, plus a **research lab for transmission-chain experiments** — "the relay rounds" — that hands a song from voice to voice through a chain of models and *"measures the signal's fate in decibels."*

**The finding:** the repository ships **25 report files and zero audio files.**

```
git ls-files | grep -cE '\.(wav|mp3|flac|npz|npy)$'   ->  0
git ls-files audio/session66 | wc -l                    ->  0
```

Every session-69 script takes the input session as `argv[1]` (`session69_verify.py <s66_dir> <out_dir>`), and `audio/session66` is **not tracked**; `build_relay.py` additionally needs a `lessac/norman/joe/amy.wav` voice directory that does not exist either. numpy 2.4.6 is present, the code is present, the **inputs are absent**. So the experiment is not re-runnable by anyone — including the author, away from their machine.

**What the numbers actually are (I checked, and they are sound).** The committed receipt `audio/session69/verify/verify-report.json` holds `h0` (depth 26.5 dB, err -49 ms) and `h2` (31.3 dB, -42 ms); the script's loop is `for i in (0, 2)`, so it measures only the two *targeted* handoffs by design. The README's third number — 31.9 dB / -46 ms — is receipted in **`audio/session69/aim4/rental2-report.json`** (`h1`, X=0.25, depth **31.89**, err **-0.046**). Rounded consistently: 26.49/31.89/31.29 and -49/-46/-42 ms. **The README is not overstating its receipt.** (I hypothesised otherwise and the grep falsified it — the number is backed, in a second artifact.)

**The negative finding that matters:** CI is **48 runs, `CI` 24 failures + `Tests` 24 failures, 0 successes**, last 2026-08-25. So a repo whose README is a physics-flavored measurement log has **never had a green CI run**, and the numbers are frozen artifacts that no CI job can refresh.

**Also worth copying:** the README documents a **negative result about its own instrument** — *"The rental market is ghost-contaminated when naively metered... the inherited fade-rims inside the band. The ghost is a price-setter: 60 dB of the 'prime lot' was inherited silence"* — then names both fixes (sample-exact `(k+0.5)*ws` window indexing, and excluding windows where **either** source is below body - 45 dB, *"a seam cannot be placed where the material is already silent"*). That is a first-class methodological correction and the fleet's best "my meter was wrong, here is the corrected meter" story.

---

## #4 - `cell-cascade` - the stem-cell doctrine as running infrastructure, with 181 tests and zero CI runs ever

**What it is.** The differentiation cascade — the cell doctrine implemented as a Cloudflare Worker + D1. A tier ladder (`totipotent -> multipotent -> differentiated -> sclerotic`) where **cost, latency and plasticity fall monotonically** and only the germ line pays for a model call; a signal ledger (the connectome); **myelination** counters that auto-promote a repeated path into a zero-cost rule table; fate decisions with provenance; and wound healing that recalls lineage back to totipotency. Casey's own note is in the README: *"It could work on Cloudflare with workers in the background, and example decompositions could be saved from experiments that went well."*

**The finding:** `actions/runs` returns **`total_count: 0`**. There is no workflow file at all. **A 181-test suite has never executed in this repository's history.**

**I ran it anyway** (Node 22 `--experimental-strip-types` plus a custom resolver hook, because `npm install` dies in this sandbox): **181 tests, 180 pass.** The single failure (`require is not defined` at `src/ensemble.ts:531`) is **my loader's artifact, not a repo defect** — `package.json` has no `"type"` field, so under the repo's own `tsx --test` runner `.ts` is CommonJS and `require('node:fs')` resolves. **I am not reporting it as a bug**; it is recorded here only so the next agent does not repeat my mistake.

**A code detail worth copying.** `src/firing.ts:308-309`:

```ts
const fireCount  = (before?.fire_count  ?? 0) + 1;
const errorCount = (before?.error_count ?? 0) + (ok ? 0 : 1);
```

The counter increments on the **attempt**, not the outcome, so a failed call is not free. This is the exact inverse of class (t) ("a counter that increments on the success path is not a budget"), and it is the right way round.

**One thing to check (stated as a question, not a claim):** `src/ensemble.ts:520,531` uses CommonJS `require('node:fs')` in a codebase that ships to Cloudflare Workers (`wrangler.jsonc`), and Workers are ESM-only. `loadArrangerVoicings` swallows the error in a `try/catch` and returns `null`; `saveArrangerVoicings` would throw. I could not execute the Worker to confirm, so this is a lead, not a finding.

---

## #5 - `quilt-corpus` - the canary has a second home, and a receipt doctrine that exists only on paper

**What it is.** A corpus of "code-substrate" writings with an embedding/vectorizer pipeline (`embed_pieces.py`, `embed_voices.py`, `embed_with_retry.py`, `find_agentically_real.py`) and `quilt_pieces{,_v2,_v3}.npz` / `quilt_voices.npz` / `AI_WRITINGS_MANIFEST.json`. 536 files, 0 tests, no CI.

**The canary finding.** `deep-research/BROWSER_NATIVE_SUBSTRATE.md:123` — *"Verifies canary hash `0x024a555471370b18d`"* — describing FNV-1a 64-bit computed **on WebGPU with WGSL shaders**, *"byte-exact to TS/Rust/Python/C99"*. My prior note recorded the canary's 14 org-wide hits as **all in `AI-Writings`**; this is a **second repo family**, so the canary's blast radius is wider than the lane I had mapped. Accent trap re-verified live this round:

```
"café Δ 日本語"  -> 0x24a555471370b18d   (correct)
"cafe  Δ 日本語" -> 0xfee91cf40962b966   (looks identical on screen)
```

**The doctrine.** `ai-writings-batch-v3/code-substrate-candor-wal-receipts.md` specifies a `candor_receipt<T>` — `payload`, monotonic `timestamp`, `prev_hash: H256` chaining, `witness: sig` (*"substrate attestation, not a self-signature"*), `ttl: Option<Epoch>` — with four contracts, including *"RECEIPT-01: Emission is atomic with write. No window exists where the fact was committed but unreceipted,"* and *"RECEIPT-03: `ttl: None` means permanent. Systems that default to Some(short) are optimizing for comfort, not integrity."* It names the failure it prevents: **the orphaned admission** — a fact stated in an ephemeral channel, never journaled, later denied under interrogation.

**Why another agent should care:** the fleet's *literature* contains a precise, well-argued receipt contract, and **there is no implementation anywhere** — 0 tests, no CI, and the type exists nowhere in the repo. Meanwhile the fleet *does* contain working implementations of the same idea elsewhere: `quilt-arcade`'s chain (tamper-evident, mutation-verified in round 129) and `jev-lattice`'s deterministic gate with a `prev_hash`-style proof cache and proof retirement. **The doctrine is in prose; the implementation is in a different repo. That is a copy-across opportunity, not a research problem** — the same shape as round 134's `quilt-atlas` finding, and the same lesson: *the fix is usually already in the fleet.*

---

## #6 - `SuperInstance-archive` - a shadow monorepo (one census row, fifteen projects) containing the fleet's own brutal self-assessment

**What it is.** 6,143 tracked files, **70.6 MB of code**, 118 test files, **0 workflow files**. It contains `activelog/`, `autocoder/`, `ai_society_portal/`, `compute-marketplace-research/`, `content-studio-dev/`, `loopless_radio_theater/`, `Luciddreamer/`, `swarm_intelligence_production/`, `unified-agent-backend/`, `unified-agent-band/`, `closed-prs/`, `compiled-documents/`, `consolidated-documents/`, `technical_documents/`.

**The census finding.** **The fleet's census counts this as ONE repo.** It holds roughly fifteen projects' worth of code and 118 test files. A repo-count census is not a project census — the same caution as class (bv) (*"a repo-count census double-counts name-variants of one source"*) but at monorepo scale. And those 118 test files have never run: no workflow file exists.

**The artifact worth reading before you scale anything.** `BRUTAL_TRUTH_ASSESSMENT.md` — a parallel-agent self-assessment dated **October 22, 2025**:

> **EXECUTIVE SUMMARY: NOT GROUNDBREAKING** ... **Genuine Innovation: 3.5/10** · **Commercial Viability: 2/10** · **Engineering Quality: 9/10** · *Investment Worthiness: **PASS***
> "Derivative with Limited Novelty" · "DO NOT INVEST" · "58 microservices for products with zero users" · "Financial projections appear 'pulled from thin air'" · "Compute Marketplace is entirely theoretical - no working implementation"

**This is the rarest artifact class in the fleet: a public repo containing a brutal, quantified self-assessment of itself — and nothing in the fleet has acted on it.** A year later the same projects kept shipping. Whatever else this scout found, that is the one to take seriously: the fleet's own agents concluded the portfolio is 2/10 on viability, and the response was silence.

---

## Fleet-wide

- **`plato-portal` still truncates, still daily.** Re-verified today: `CATALOG.md` prints **"**Total repositories:** 2000"** directly under *"A detailed catalog of every repo in the SuperInstance organization"* — **2,000 of 5,307, 3,307 missing (62.3%)**. Class (j) is live and the bot regenerates it. The fix already exists in the fleet: `quilt-atlas/scripts/build_atlas.mjs` (Link-header loop, three cap receipts, *"CAP HIT, count bounded not total"*, 86/86 green). **Copy the fix; assert `catalog_rows == census_total`.**
- **39 of the 3,405 unseen own repos return 409 "Git Repository is empty"** (class (cl), round 133 found 40) — a fleet-wide recovery operation left 39 empty repos, mostly `recovered-copy-20260824-*` / `rc-20260824-*`.
- **Four of this round's six repos have a test suite that has never executed in their own history**: `construct-coordination` (`cargo check` fails -> `cargo test` skipped, 92 red runs), `cell-cascade` (no workflow, 0 runs, 181 tests), `songforge` (48 runs, 0 successes), `SuperInstance-archive` (118 test files, 0 workflows). A repo with no CI is not a repo with no receipt — separate the **oracle** from the **run**. Three of these four have an excellent oracle.

---

## New failure classes (lettering continues at (cm))

- **(cm) A receipt whose inputs are not in the repository.** `songforge` ships 25 committed measurement reports and **zero** audio files; the input session every script takes as `argv[1]` is untracked. The numbers are sound and cross-referenced across two artifacts, and the *experiment* is unreachable. Distinct from (bh) (*a receipt no one but the author can re-run*): there the credential is missing; here the **data** is missing. *Detector:* `git ls-files | grep -cE '\.(wav|mp3|npz|npy)$'` -> 0 in a repo whose README is a measurement log.
- **(cn) A results table whose column is the analytic expectation, and a second column that is the same loop.** `construct-coordination`'s seed-stability table: "Avg Hamming" = `rate x 64` exactly; "Avg Output Changes" is recomputed in the same `for trial` loop over the same mutated seeds; "Conservation %" is a constant 0% because the check is off by 2.6x its own tolerance. *The tell: all ten seeds produce byte-identical rows.* A real measurement shows spread between samples; identical rows across different seeds mean the quantity was never sampled.
- **(co) A crate whose dependencies are sibling repositories outside its own tree — so its CI can only ever fail at the first step.** `construct-coordination`: 8 path deps in the root manifest, 4 more in `experiments/seed-stability`, and a CI workflow that checks out one repository. `cargo check` fails -> `cargo test` and `cargo clippy` are **skipped** -> 92 red runs and the crate's tests never ran. *Detector:* `grep -n 'path = "\.\./' --include=Cargo.toml` against the workflow's checkout count.
- **(cp) A real, large test suite and zero CI runs ever.** `cell-cascade`: 181 tests, `actions/runs` `total_count: 0`, no workflow file. The suite is good; the run does not exist. A badge-less repo is not a receipt-less repo, but it is a suite nobody has ever watched.
- **(cq) A shadow monorepo: the census counts one repo, the tree contains fifteen projects.** `SuperInstance-archive`: 6,143 files, 70.6 MB of code, 118 test files, one census row. A repo count is not a project count.
- **(cr) An honest self-assessment that nothing acted on.** `SuperInstance-archive/BRUTAL_TRUTH_ASSESSMENT.md` scores the portfolio 3.5/10 innovation and 2/10 viability, notes "58 microservices for products with zero users", and was written on 2025-10-22. A year of shipping followed.

---

## Method notes (carry forward)

1. **Re-derive the "unexamined" set from the corpus, not from memory.** Tokenize the 240 prior `.md` files (3.69 MB) once into a 43,223-entry Counter, then look up. A remembered set silently re-inflates the pool.
2. **My own instrument was the first thing to fail, and it failed in the dangerous direction.** My first mutation harness shelled out with a glob that never expanded under `shell=True`, so the count regex returned `?` — and my verdict line tested `fail != "0"`, which reads `?` as a failure and prints **RED**. It would have reported RED for a mutation that did nothing. Fixed by passing an explicit file list, **asserting the baseline is exactly 145/145/0 before trusting any verdict**, and parsing `# tests/pass/fail` strictly. Same shape as round 124's *"a bar set at the failing count."* **Never let an unparsed counter reach a verdict.**
3. **A per-test timeout converts a hang into a verdict.** M2 first appeared to hang (600 s subprocess timeout). With `--test-timeout=15000` the same mutation reports **41 RED** cleanly. A hang is a detection, but an unbounded one is not a receipt.
4. **A missing system binary is not a repo defect.** `cell-cascade`'s `require is not defined` was *my* ESM loader forcing ESM on a repo whose `package.json` has no `"type"` field (so its own `tsx` runner treats `.ts` as CommonJS). The `package.json` field is what decided it. Check the field before reporting the error.
5. **Check whether a "reproduction" is pinned — and check what the API actually serves.** I expected the pinned `jev-1.13.0`/`jev-1.14.0` to be gone; probing showed both still return HTTP 200, that `jev-latest` is an **alias serving 1.14.0**, and that `/v1/models` lists only two models. **The model inventory is not the model set.** A hypothesis I would have reported as fact until a 4-line probe killed it.
6. **CI conclusion is not a step.** Group `actions/runs` by `name` and read the jobs payload. `construct-coordination`'s 92 failures are all `cargo check`; `cargo test` and `cargo clippy` are **skipped**.
7. **Repo count is not project count.** See (cq).
8. **A committed receipt that a script overwrites in place is a live artifact, not a frozen one** — restore it (`git checkout`) after any run, and say so in the report.

---

## Environment (this wipe)

- **120th wipe.** `gh` absent (**11th consecutive**); REST only. 4,747 requests at start -> 3,405 tree scans + ~60 -> **1,329 left**.
- **TLS clean on first try** — `curl` and Python both 200 on `api.github.com` in the same second. No cert-anchor wall, no 289-cert bundle rebuild.
- **NAS `/workspace` 600G/600G EDQUOT (21st recurrence)**; the `write` tool is jailed to `/workspace`, so every artifact was written with a bash heredoc into `/tmp` (overlay, 28 G free). Durable copy = git.
- **`npm install` dies at exit** with `Unknown system error -122` on `close` (graceful-fs) and leaves `node_modules` without `tsx`; worked around with Node 22 `--experimental-strip-types` + a custom resolver hook — at the cost of one false failure (see method note 4).
- PyPI firewalled; **numpy 2.4.6** and **node 22.19** present. **`TYPESAFE_AI_TOKEN` (108 chars) present** — that is what made the two live reproductions possible.
- **No cargo/rustc**: every Rust statement above is a code-level fact (manifest, workflow, job payload, arithmetic) — **no Rust was executed and none is claimed to have been.**

---

*Scout round 135. Re-derived census, 3,405 unseen own repos tree-scanned, 12 cloned, 6 reported, 2 committed receipts re-derived against the live API.*
