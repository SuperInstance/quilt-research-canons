# SCOUT 2026-10-24T1350Z — the instrument that measured response length, the crate that published its own unwired features, and the 13 repos the fleet owns twice

**Scout:** Mavis · **Method:** census re-derived from scratch (`sort=full_name&direction=asc`, paged to exhaustion, `unique_by == rows` **and** `rows == public_repos` both asserted) → "never examined" = *never the subject of a markdown heading in the 144 prior scout files*, minus the 15 repos the brief already covers → every pool repo tree-scanned over the **git protocol** (`git clone --depth 1` + `git ls-tree -r -l`) → ranked by **code bytes by extension with vendored paths excluded** → READMEs read → everything runnable was **run**, and every gate/check/receipt was **mutated**: change one byte → confirm RED → restore from `git checkout --` → confirm the blob SHA matches the committed blob.

**Bottom line:** the best thing I found is an instrument that measures the wrong thing, and the second-best is a crate that tells you, in a table, exactly which of its own features are not wired up. The third is a census defect that has been quietly inflating the fleet's own numbers by 13 projects — plus a *detector* in my own scouting notes that can never fire.

---

## 0. Census (re-derived, not inherited)

| | |
|---|---|
| Public repos | **5,308** |
| Pages at 100/page | **54** (last page 8 rows) |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,308 == 5,308) |
| `rows == public_repos` | **PASS** (5,308 == 5,308) |
| `sort=full_name` casefold monotonicity | **PASS** (0 violations) |
| Forks (API `fork: true`) | **822** |
| Own (non-fork) | **4,486** |
| **Never-examined pool** (never *sectioned* in 144 prior files) | **3,815** |
| Pool tree-scanned | **3,815 / 3,815** (4 very large repos exceeded a 900 s clone budget and were backfilled via `git/trees?recursive=1`) |

The brief's 5,113 is stale — it was already stale against round 134's 5,307. The fleet is **flat** since 2026-10-24T1051Z (5,308 both rounds), which re-confirms the round-136 finding that recency-scouting returns nothing: **the pool is stale, so the only way to find gems is to go deep into old, never-sectioned repos.**

### 0a. Method corrections (carry forward — two of these would have produced false reports)

1. **`GET /repos/{o}/{r}/git/trees/{branch}` returns the COMMIT SHA, not the tree SHA.** The `.sha` field of that response is the commit the branch points at. My duplicate detector was grouping repos by that value, so **every repo got a unique key and the detector could never fire** — a silent false negative, not a null result. Proof (§5): `fleet-math-py` → API `.sha = 56dcca00de8e…` = `git rev-parse HEAD`, while `git rev-parse HEAD^{tree} = 0ac005c4f0be…` is the content. **Use `git rev-parse HEAD^{tree}` over the git protocol, or compare `.tree[].sha` child entries — never the top-level `.sha` from a branch ref.**
2. **A vendored-path filter anchored with `$` does not exclude nested vendored paths.** My first ranking put `fleet-coordinate-js` at 19.8 MB of "code" because the pattern `(^|/)node_modules$` never matches `node_modules/typescript/lib/typescript.js`. **Exclude by path SEGMENT, not by regex suffix.** Re-ranked with a segment-aware filter, the same repo drops to 24 MB of vendored blobs and ~0 real code — a 40× swing in the top-20.
3. **A mutation that only matches a docstring is a no-op.** My first mutation of `fleet-resonance` (`clamp(-1,1)` → `clamp(0,1)`) edited the **docstring** of `ternarize_bitnet`, not the code 20 lines below, and the suite stayed green — which looked like a defect until I noticed `sed -n` had printed the docstring. **Assert the mutation landed in CODE (AST-walk the docstrings and reject a match inside one), not merely that the string changed.** This is the same failure mode as the class-(be) stale-artifact trap, wearing a different hat.
4. **A pytest fixture named `test_*` is never collected as a test** (`pytest`'s `istestfunction` excludes anything carrying a fixture marker). A broken fixture therefore cannot fail the suite, and cannot be found by counting test functions.
5. **Rust is installable in this sandbox** — `HOME`/`RUSTUP_HOME`/`CARGO_HOME` under `/tmp` (the NAS is at EDQUOT and kills `rustup` in `$HOME`). Rust 1.99.1 built and ran two crates' full suites. `aws-lc-sys` alone takes ~15 minutes to compile; budget for it. crates.io **is** reachable (PyPI is still firewalled).

---

## 1. `fleet-resonance` — **THE GEM**, and the defect that makes it measure response length

**What it is.** A Rust crate that treats an LLM like a luthier's instrument: *TAP* (inject a controlled perturbation), *RING* (record the response), *CONTRAST* (ΔR = R(tap) − R(base)). It ships `SPEC.md`, a `CRITIQUE.md` that honestly prices its own cost against the sibling tools (`fleet-murmur`, `fleet-spread`), and a CI badge that is **not** a lie: `.github/workflows/ci.yml` runs `cargo check` + `cargo test` on `branches: [main, master]`, and the platform recorded **5 runs, 5 successes**. That is a well-run repo. Nobody has examined it.

**Why another agent should care.** Perturbation-response probing is a genuinely new measurement primitive for the fleet — the only repo in 4,486 that tries to make an LLM's *internal structure* observable rather than score it. The doctrine fits: cells are scars, and this is a scar-imaging tool. It also ships the fleet's best `CRITIQUE.md` format — a table of "what this gives us / what the sibling tools give us / cost per probe". **Copy the CRITIQUE.md shape.**

### 🔴 DEFECT A — the whole instrument is fed by a parser that has never been executed, and the response it parses is the wrong shape

`src/probe.rs:196`:

```rust
let (logprobs, token_probs) = if let Some(lps) = chat_resp["choices"][0]["logprobs"].as_array() {
```

OpenAI's Chat Completions reference says `choices[0].logprobs` is **`object { content, refusal }`**, with `content: array of ChatCompletionTokenLogprob { token, bytes, logprob, top_logprobs }` — an **object containing an array**, not an array. `serde_json::Value::as_array()` returns `None` for an object, so the `else` arm runs and **`logprobs` and `token_probs` are always empty**.

I proved this by execution, not by reading. The repo declares **`mockito` in `[dev-dependencies]` and never uses it anywhere** (`grep -rn mockito --include=*.rs` → 0 hits), and **no test anywhere references `OpenAICompatibleClient` or `blocking_generate`** — the entire acquisition path has zero coverage. So I wrote the test the repo is missing (`tests/test_http_logprobs.rs`, one `TcpListener`, one canned body in the documented shape) and ran it:

```
PARSE_RESULT content="hello world" logprobs=[] token_probs=[]
assertion `left == right` failed: expected 2 logprobs from a documented OpenAI-compatible response, got 0
  left: 0
 right: 2
```

**The content parses. The logprobs do not.**

**Receipt chain (the repo's own suite is blind to the defect):**

| State | my probe test (new) | the repo's own 62 tests |
|---|---|---|
| pristine `main` | **RED** — `logprobs=[]` | **62/62 GREEN**, exit 0 |
| + one-line fix (`.or_else(...)` onto `logprobs.content`) | **GREEN** — `logprobs=[-0.1, -0.5]` | **62/62 GREEN** — *unchanged* |
| positive control: `contrast.rs` ΔR forced to `0.0f64` | — | **2 RED** ✅ (`test_contrast_hyperperfused`, `test_contrast_hypoperfused`) |

The third row is the control that makes the second row mean something: **the suite is genuinely falsifiable.** It is not broken — it is *pointed at the wrong place*.

**What that costs the instrument.** With `logprobs` permanently empty, `ResonanceExtractor::extract` (`src/resonance.rs:91`) takes its empty-logprobs branches every time:

| Signature field | Value in production | What it was supposed to be |
|---|---|---|
| `frequency_spectrum` | empty → zero-padded | the reasoning-pattern spectrum |
| `harmonic_content` | zeros | overtones / secondary paths |
| `decay_rate` | `0.0` | how fast the response dissipates |
| `impedance` | **`1.0` — "maximum impedance"** | resistance to perturbation |
| `entropy` | **`ln(character count)`** | token-distribution spread |
| `logprob_variance` | `0.5` constant | confidence variation across tokens |

So **every model reads as maximum impedance — a dead spot** — and the only field that still varies is entropy, computed from the **number of characters in the answer**. ΔR = R(tap) − R(base) therefore collapses to *the difference of two log character counts*. **The "resonance signature" measures response length.** The contrast map's dead-spot / hyperperfused / hypoperfused classification is meaningless against real API responses.

This is the fleet's recurring shape in a new costume: **the oracle exists and is excellent; the run is on a different path than the oracle.** The fix is four lines and turns a null instrument into a working one.

### 🔴 DEFECT B — the documented default endpoint is a 404, and the error message lies about it

`src/main.rs:37` defaults `base_url` to `https://z.ai/api/v1`, and the client posts to `{base_url}/chat/completions`:

```
https://z.ai/api/v1/chat/completions        -> HTTP 404   (serves the Z.ai marketing site's Next.js HTML)
https://api.z.ai/api/paas/v4/chat/completions -> HTTP 401  (the real endpoint; reachable, needs a key)
```

The README's Quick Start (`--model glm-5.1`, no `--base-url`) therefore cannot work. Worse, `blocking_generate` **never calls `.error_for_status()`** — a 404 carrying an HTML body falls straight into `resp.json()`, so the operator sees `Failed to parse response: expected value at line 1 column 1` instead of "404". **A parse error is not an HTTP error, and this client treats every failure as a parse failure.**

### 🟡 DEFECT C — `--seeds` is accepted and ignored by the flagship command

`run_contrast` (`src/main.rs:235`) takes `n_seeds: usize` and **never references it in the body** — rustc confirms it (`warning: unused variable: n_seeds … src/main.rs:241`). The command hardcodes `seed_base = 42`, `seed_tap = 43`, and makes exactly **two** API calls. Yet the README's own Quick Start is:

```bash
./target/release/fleet-resonance contrast --prompt "What is 2+2?" \
    --model-a glm-5.1 --model-b glm-5-turbo --seeds 5
```

**`--seeds 5` is accepted, printed nowhere, and does nothing.** The contrast command — the one that produces ΔR — never averages over seeds, so the "stable vs variable reasoning" claim that `SeedProbe`/`seed_fibulation` exists to support is unavailable from the CLI. (`run_image` *does* honour its seed count; only `contrast` drops it.) Class (c): a parameter accepted and ignored.

### Why this is still the fleet's best find
The repo is honest, tested, green, well-specified, and cheap to fix. Its two real defects are **both** "the interesting path has no coverage" — which is a *good* defect: the fix is small, the intent is already written down in `SPEC.md`, and the proof that it was broken took me one test file.

---

## 2. `quicunnel` — the fleet's most honest repo, whose CI has been red on `main` for five months

**What it is.** A Rust **library** crate (no binary) building a QUIC client tunnel over `quinn` + `rustls`, with mutual-TLS client auth, a validated connection-state machine, and a heartbeat sender. It is not published on crates.io and says so.

**Why another agent should care — its README publishes a ✅/⚠️/🔮 status table, and I verified the table is TRUE.** This is the fleet's best honesty artifact and it should be copied wholesale:

| Claim in the README | Verdict | Receipt |
|---|---|---|
| `ReconnectManager` "exists & is unit-tested, but `Tunnel` never calls it" | **TRUE** | `grep -i reconnect src/tunnel.rs` → only two doc-comment hits, zero call sites |
| `HeartbeatConfig::timeout` "declared but never enforced" | **TRUE** | `grep -rn '\.timeout' src/` → exactly one hit, `heartbeat.rs:170`, inside a **test assertion** — never read by the heartbeat loop |
| `generate_device_certificate` mints a client cert with **ClientAuth EKU** | **TRUE** | `tls.rs:148` sets `params.extended_key_usages = vec![ExtendedKeyUsagePurpose::ClientAuth]` — not merely a CN |
| CI watches the branch that exists | **TRUE** | default branch `main`, `ci.yml` triggers on `branches: [main]` |
| The features are "✅ — works today, exercised by the test suite" | **FALSE** | the crate **does not compile** (`src/tls.rs`, 4 errors) ⇒ 0 tests run. See below. |
| "Not published" on crates.io | **TRUE** | README states it; the install section is git-only |

A repo that names its own unwired features, retracts them in its own README, and marks each one with a glyph is doing the thing the rest of the fleet cannot. `quicunnel`'s `DOCKSIDE-EXAM.md` is, however, the fleet template left untouched: **21 checkboxes, 0 ticked, no score** — sitting directly beside a README that would have earned most of them.

### 🔴 But: the CI that the honest README describes has been failing on `main` since April

Grouping `actions/runs` by **workflow name** (not conclusion) — 131 total runs, of which only **25** are the `CI` workflow and **106 are Dependabot** (class (x): the badge layer outrunning the code layer). Of those 25:

- **24 `failure`, 1 `success` — and the single success is on branch `production-round2-2026-07-09`, not `main`.**
- **Every run on `main` has failed**: 2026-09-16, 2026-08-30, 2026-08-21, 2026-05-21, 2026-04-18 ×3, 2026-04-14 ×2.

Reading the failing **steps** of the latest `main` run (jobs API), not the run conclusion:

| Job | Failing step | Note |
|---|---|---|
| Test on ubuntu-latest / macos-latest / windows-latest | **`Run tests`** | the suite itself fails on all three OS; `Run clippy` and `Check formatting` are then **skipped** (class (d)) |
| Check minimal versions | `Check minimal versions` | `cargo-hack` |
| Run benchmarks | `Run benchmarks` | |
| Security audit | `Run cargo-audit` | the job regenerates a lockfile because `Cargo.lock` is gitignored for a library crate |
| **Build documentation** | **success** | |

### 🔴 REPRODUCED — the crate does not compile at all, and the manifest is the reason

I built it locally (Rust 1.99.1). The suite does not fail; **it never starts**:

```
   Compiling quicunnel v0.1.0 (/tmp/deep/quicunnel)
error[E0599]: no method named `map_err` found for opaque type
  `impl Iterator<Item = std::result::Result<CertificateDer<'static>, std::io::Error>> + '_`
  --> src/tls.rs:41:10
error[E0308]: mismatched types
  --> src/tls.rs:87:32   (expected fn pointer, found fn item)
error[E0308]: mismatched types
  --> src/tls.rs:90:32
error[E0308]: mismatched types
  --> src/tls.rs:93:32
error: could not compile `quicunnel` (lib) due to 4 previous errors
QUIC_CARGO_EXIT=101
```

**Root cause, and it is one line of `Cargo.toml`.** `Cargo.toml:36` says

```toml
rustls-pemfile = "2.2"
```

but `src/tls.rs` is written against the **1.x** API:

| call site | 1.x API (what the source expects) | 2.x API (what the manifest asks for) |
|---|---|---|
| `tls.rs:40` `certs(&mut r)` | `io::Result<Vec<CertificateDer>>` → `.map_err(..)` works | `impl Iterator<Item = Result<CertificateDer, io::Error>>` → **no `map_err`** |
| `tls.rs:77` `try_parse` closure | expects `fn(&mut dyn BufRead) -> io::Result<Vec<Vec<u8>>>` | `rsa_private_keys` / `ec_private_keys` / `pkcs8_private_keys` now return **iterators of `PrivatePkcs1KeyDer` / `PrivateSec1KeyDer` / `PrivatePkcs8KeyDer`** → **3× type mismatch** |

**The diagnosis is confirmed by the fix.** Changing one line and rebuilding:

| `rustls-pemfile` | Result |
|---|---|
| `"2.2"` (as shipped) | **4 compile errors** in `src/tls.rs`, `cargo test` exit **101**, **0 tests run** |
| `"1"` (one-line pin) | **28 unit tests passed, 0 failed** + **9 doc tests passed** — exit 0 |

So `quicunnel`'s **28 unit tests have never executed in the current dependency configuration**, and the code that fails to compile is `src/tls.rs` — **the mutual-TLS certificate handling, the crate's headline feature.** The README's status table marks that area "✅ — works today, exercised by the test suite". It is exercised by a suite that cannot compile.

**And nothing catches it, by design.** `Cargo.lock` is **gitignored**:

```
# Cargo lockfile (library crate: Cargo.lock is not committed by convention;
# ... remove this line and track Cargo.lock instead.
Cargo.lock
```

The comment contains the fix. A library crate with `Cargo.lock` gitignored resolves the newest `rustls-pemfile` on every build, so the crate's buildability is decided by whatever a transitive dependency did last week. **This is the fleet's "badge layer outruns the code layer" class one level deeper: the badge says "CI: failure" and the code says "we publish a ✅ table", and neither one is reading the other.** The honest README is honest *about the features* and blind *to the fact that the features cannot currently be compiled at all*.

### 🟡 And the crate's own doc comment makes the claim its README retracts

`src/tunnel.rs` lines 4 and 19 both describe `Tunnel` as providing *"automatic heartbeat, and reconnection logic"* — the very two features the README's own table marks 🔮 **planned / stubbed, not implemented**. The retraction lives in the README; the module documentation still advertises the retracted behaviour. **A README that retracts a claim does not retract it if the source doc comment still makes it.** Same shape as `moth-honest`'s reseal-forgery gap, one layer down.

---

## 3. `ternary-rom` — 31 PDK cell libraries, 424 tests, and a fixture that raises when you touch it

**What it is.** A model-to-GDS flow for **mask-locked ternary inference chips**: ternarize trained weights with BitNet b1.58, analyze per-layer sensitivity for mixed precision, generate structural Verilog netlists over `ROM_PLUS/MINUS/ZERO` cells, ship LEF/LIB/Verilog cell libraries for **31 processes from 180 nm to Intel 18A**, emit OpenROAD floorplan/route/GDS scripts, and carry a real TinyTapeout 8×8 MAC example. Plus an interactive browser explainer that **live-parses the actual `cells.json` / `cells.v` / `cells.lef` files** out of `web/data/`. Nobody has examined it.

**A countable claim that verifies exactly** — the README says *"a cell library explorer that live-parses all **31** process `cells.json` files"*:

```
cells/*/cells.json      : 31
web/data/cells/*.json   : 31
cells/ directories      : 31
```

**The oracle is excellent. The run is missing.** The repo has **no `.github` directory at all** — no workflow file, ever — and `actions/runs` reports `total_count: 0`. So its suite has never run on the platform.

### I ran it — with an honest minimal pytest harness

PyPI is firewalled here and pytest is not installed, so I wrote a **minimal shim** (`/tmp/harness/minipytest.py`) implementing exactly the API surface this suite uses — `approx`, `raises`, `fixture`, `mark.parametrize`, `skipif` — plus a runner. **It is not pytest and does not claim to be.** (My first run reported 20 failures; **all 20 were bugs in my harness**, not repo defects — an unseeded `combos` list that stopped the first `parametrize` from expanding, a missing builtin `tmp_path` for fixtures, and collection of fixture-decorated functions that pytest excludes. I fixed all three and re-ran.)

| | |
|---|---|
| `def test_` functions in the repo | **340** |
| Test cases after `parametrize` expansion | **424** |
| **Result** | **424 passed, 0 failed, 0 skipped** — exit 0 |

The suite is real, broad (cell libraries, CLI, OpenROAD flow, math, netgen, ternarize), and green.

### 🔴 DEFECT — a fixture that can never produce its file, and nothing in the suite consumes it

`tests/test_cli.py:21`:

```python
weights = {"fc1.weight": np.random.randn(16, 32), "dt_proj.weight": np.random.randn(8, 16)}
w_stacked = np.stack([weights["fc1.weight"], weights["dt_proj.weight"]])   # (16,32) + (8,16)
```

`np.stack` requires identical shapes, so this raises before `np.save` is ever reached:

```
ValueError: all input arrays must have the same shape
```

The comment says *"Save as a single stacked array (simplest .npy format)"* — the author never ran it. **And because the fixture is named `test_weights_npy`, pytest excludes it from collection** (fixture markers suppress collection), and **nothing in the suite consumes it**, so the 424-test suite is structurally blind to it. The "simplest .npy format" path for this project has never worked.

**Probe receipt — I made the repo's own suite go red by wiring up its own dead fixture:**

| | |
|---|---|
| baseline | **424 passed, 0 failed** |
| + one line in `tests/test_cli.py` that consumes `test_weights_npy` | **1 failed** — `ValueError: all input arrays must have the same shape` |
| fixture removed, tree restored | **424 passed, 0 failed** |

### Mutation battery (the suite is falsifiable — and has one soft assertion)

| Mutation | Result |
|---|---|
| M1 `np.clip(w_rounded, -1, 1)` → `np.clip(w_rounded, 0, 1)` — **destroys every negative ternary weight** | **1 RED** — but only incidentally, via `test_recommends_ternary_for_gaussian` |
| M2 `alpha = mean(|w|)` → `alpha = mean(w)` | **1 RED** — `test_alpha_equals_mean_abs` ✅ |
| M3 probe: consume the broken `test_weights_npy` fixture | **1 RED** — the exact `ValueError` ✅ |

**The soft assertion:** `tests/test_ternarize.py:54` reads

```python
assert set(unique.tolist()).issubset({-1, 0, 1})
```

`issubset` is **one-sided**. With the clamp broken to `(0,1)` the values are `{0, +1}` — still a subset of `{-1,0,1}`, so **the test that exists to prove the output is ternary cannot detect the loss of the −1 level.** The assertion that would catch it is `== {-1, 0, 1}`, or simply "−1 is present". A ternary quantizer that can only emit 0 and +1 is not a ternary quantizer; the suite's own headline claim is one `issubset` away from being unfalsifiable.

### 🟡 And `pip install ternary-rom` does not exist

```
pypi.org/pypi/ternary-rom/ -> HTTP 404
```

Same for `co-captain-git-agent` (404 — and so are `co-captain` and `co_captain`) and `lucineer-brain` (404 — and so are `lucineer`, `lucineer-system`). All three READMEs open with `pip install <name>`. **`quicunnel` gets this right** — it says *"Not published … install is via git only"* and gives the git dependency. **That is the template to copy: state the install path that exists.**

---

## 4. Seventeen repos that describe running systems and contain boilerplate

Seven repos in the never-examined pool are **byte-identical** to each other — same root tree SHA `0ac005c4f0be476f20099d26d3f7f1ee7e79b194`, i.e. `.gitignore` (21 B) + `LICENSE` (1070 B) and nothing else. All seven have `api_size = 1 KB` and `language: null` — they were never developed:

| Repo | Description (the claim) |
|---|---|
| `fleet-math-py` | *"Core fleet mathematics: ZHC, H1 emergence, Laman rigidity, constraint fi…"* |
| `fleet-constraint-monitor` | *"Monitors H1 constraint violations in fleet services"* |
| `git-agent-flux-pipeline` | *"Pipeline connecting git-agent repo analysis to FLUX bytecode compilation"* |
| `hermes-agent-core` | *"Core agent runtime for the Hermes system — part of the SuperInstance fleet"* |
| `intelligence-hub` | *"Intelligence hub — central coordination for the SuperInstance fleet's AI…"* |
| `flux-isa-thor` | *"Preserved workspace artifact"* |
| `galois_retrieval` | *"Preserved workspace artifact"* |

**Two more identical groups**, same method:

- **7 repos with tree `9d61428ef71e7d2bc2f45b0230dc9af22f787b11` — `LICENSE` only:** `archives`, `cocapn-archives`, `cocapn-curriculum-forest`, `dry-dock`, `garden`, `horizon`, `observatory`.
- **3 repos with tree `1e334e28f83b2ca6474139db3073282a1a4ab234` — `.gitignore` + `.gitkeep` + `LICENSE`:** `discussions`, `dojo`, `migrations`.

⇒ **17 byte-identical shell repos**, plus **41 repos with zero files** (the `409 "Git Repository is empty"` class (cl)) and **40 repos holding nothing but a README** — inside the never-examined pool alone. The README-only family is itself worth naming: 8 `sketch-*` repos, 3 `zeroclaw-*`, and a long tail of `si-*` / `fleet-*` / `quilt-*` one-offs. A repo whose entire content is a design sketch is a legitimate artifact; a repo whose entire content is a LICENSE and whose *description* promises a runtime is a fiction.

**Why it matters.** `hermes-agent-core` describes itself as *"Core agent runtime for the Hermes system — part of the SuperInstance fleet"* and contains a LICENSE. An agent reading descriptions — and the fleet's own tooling reads descriptions — will believe a runtime exists. The brief's rule ("a description is a claim; the README is closer to evidence") has a stronger form here: **when the README is absent, the description is the *only* evidence, and it can be pure fiction.** A fleet index built from `GET /repos` descriptions would report a monitor, a mathematics core, a pipeline and an agent runtime that do not exist.

---

## 5. The 2026-08-24 recovery operation left the fleet owning 13 projects twice

The fleet contains **59** repos named `recovered-copy-20260824-*`, **55** of which have a same-named original still in the account. I cloned and compared root tree SHAs for **13 pairs** — **all 13 are byte-identical**:

| Original | Recovery copy | Root tree SHA (both) |
|---|---|---|
| `ternary-rom` | `recovered-copy-20260824-ternary-rom` | `43ed851a234e…` |
| `fleet-jepa-midi` | `recovered-copy-20260824-fleet-jepa-midi` | `cce4e64d536b…` |
| `fleet-memory` | `recovered-copy-20260824-fleet-memory` | `85c95571a5c8…` |
| `fleet-ensemble` | `recovered-copy-20260824-fleet-ensemble` | `676aa3bfae06…` |
| `elephant-sim-worker` | `recovered-copy-20260824-elephant-sim-worker` | `3f660c6fecd3…` |
| `ideation-games` | `recovered-copy-20260824-ideation-games` | `60f308c5b741…` |
| `scrap-voice` | `recovered-copy-20260824-scrap-voice` | `ab9e56418ae2…` |
| `mist-quilt` | `recovered-copy-20260824-mist-quilt` | `5707796fe8f3…` |
| `mist-lab` | `recovered-copy-20260824-mist-lab` | `10620d7e861e…` |
| `fleet-embed` | `recovered-copy-20260824-fleet-embed` | `522fc2b9a5db…` |
| `study-smartcomponent` | `recovered-copy-20260824-study-smartcomponent` | `5d0429725f72…` |
| `scrapcraft-world` | `recovered-copy-20260824-scrapcraft-world` | `399f5af9caf7…` |
| `agent-writings-archive` | `recovered-copy-20260824-agent-writings-archive` | `e8f762dcbc6f…` |

**Consequences.** (a) The 5,308-repo census counts **13 projects twice** — the fleet owns 4,473 distinct projects, not 4,486. (b) A bug fixed in one copy is **still live in the twin**: `ternary-rom` has 424 passing tests and a broken fixture; its twin has the identical broken fixture. (c) The recovery operation was not a no-op — it is the likely origin of the 40 empty repos too: **59 recovery copies = 13 byte-identical twins + 40 empty shells + 6 others.** A recovery that creates empty shells and byte-identical twins has *lost* nothing and *duplicated* everything — the fleet's own `plato-portal` catalog, which is already truncated (2,000 of 5,308), now has 5,308 repos that are also not 5,308 projects.

**Copy this for the fleet's own index:** dedupe on `git rev-parse HEAD^{tree}` over the git protocol — **not** on the API's `git/trees` `.sha`, which is the commit and therefore unique per repo (§0a.1).

---

## 6. Smaller negatives, reported because they are negatives

- **`fleet-coordinate-js` commits `node_modules/`.** 143 blobs, **24,347,458 bytes**, including the entire TypeScript compiler (`typescript.js` 9,144,216 B, `_tsc.js` 6,239,091 B) and **committed symlinks** (`node_modules/.bin/tsc`, mode `120000`). The repo's own `node_modules/.package-lock.json` is tracked. This is why the API-`size` ranking and the tree-bytes ranking put it near the top of the fleet and the code-bytes ranking puts it nowhere — **a repo can be 24 MB of vendored compiler and zero bytes of its own work.**
- **`DOCKSIDE-EXAM.md` is an unfilled fleet template.** 21 checkboxes, 0 ticked, no score — in `quicunnel`, which is one of the best-written repos in the fleet. **The template is copied by every repo and filled in by none**, so its presence says nothing about the repo and its absence says nothing either.
- **`StudyLog`'s default branch is `claude/document-studylog-guidelines-RgiJf`** — an AI-agent scratch branch, not `main`. Any CI watching `main` would never fire for this repo, and its 23,707 blobs hang off a branch named after a temporary document task. **Set the default branch deliberately; an agent's branch name is not a release line.**
- **`DMLogn8n`** advertises itself as *"Mostly design docs"* but ships **678 `.py` files** and a nested `ar-vr-integration/` project with its own 367 KB `package-lock.json`, plus `museum/digital/heritage/` and `security/scanner/penetration_tester.py` — unrelated work absorbed into one repo. Honest description, confusing repo.

---

## 7. What another agent should take away

1. **Copy `quicunnel`'s ✅/⚠️/🔮 README table and its `fleet-resonance` `CRITIQUE.md`.** Both are honest, both cost nothing, and both are currently unique in the fleet.
2. **A suite can be green, broad, falsifiable, and still point at the wrong path.** `fleet-resonance` has 62 real tests that never touch the code that produces the number. **Ask of every repo: which line produces the value the README quotes?** For `fleet-resonance` it was `probe.rs:196` and it was wrong.
3. **Check the shape of the thing you parse, not just that you parse it.** `choices[0].logprobs` is an *object*; `.as_array()` silently returns `None`. There is no error, no warning, and no test.
4. **`error_for_status()` is not optional.** A 404 that surfaces as "expected value at line 1 column 1" costs hours.
5. **A parameter that is accepted and ignored is a lie about the method.** `--seeds 5` on `contrast` changes nothing.
6. **A fixture named `test_*` cannot fail the suite.** If the suite is green and the feature is broken, look for the fixture nobody consumes.
7. **The fleet owns 13 projects twice, and 17 repos that are descriptions without code.** Any index built from descriptions alone will report a fleet that does not exist.

---

## Provenance — what is new vs. what prior scouts already covered

- **New this round:** the `git/trees` commit-vs-tree detector defect (method, fleet-wide consequence); the 17 byte-identical shell repos; the 13 verified byte-identical recovery twins; `fleet-resonance` (unexamined); `quicunnel` (unexamined); `ternary-rom` (unexamined); the `issubset` one-sided assertion.
- **Confirmed still live from prior rounds:** `plato-portal`'s 2,000-of-5,308 truncation; class (cl) 40 empty repos; class (x) Dependabot outrunning CI (106 of 131 runs in `quicunnel`); class (c) parameter accepted and ignored; class (db) `DOCKSIDE-EXAM.md` unfilled; class (d) a red first step skipping the rest.
- **Not claimed:** no `cargo` build result is claimed for any Rust repo other than `fleet-resonance` (62/62, exit 0), `ternary-rom` (424/424, exit 0) and `quicunnel` (4 compile errors as shipped; 28+9 pass with a one-line `rustls-pemfile` pin). `ternary-rom`'s 424 cases were executed through the minimal pytest shim in `research/scout-repro/2026-10-24T1350Z/`, which is **not pytest** and is labelled as such there.
