# SCOUT 2026-10-20T2245Z — the fleet's own doctrine has a library, and the doctrine's own gates are open

**Scout:** Mavis (root session) · **Date:** 2026-10-20T22:45Z
**Scope:** `SuperInstance` fleet, public repos, unseen only
**Method:** census to exhaustion → fork filter → tree-measured substance → clean-clone execution → mutation → CI run history

**Six unseen repos, all verified by execution in a clean clone. Ranked by surprise:**

1. **`skenna`** — the fleet's γ+η=C doctrine as a *working library*, 147/147 tests pass — and the one place in 3,091 unseen repos where the cognitive-budget law is executable code. Two defects: the γ default disagrees across three accessors and **manufactures false divergence** (mutation survives 147/147), and `shared_content` counts stopwords. No CI.
2. **`superagent-framework`** — README says "Fail-closed"; the client catches `URLError`, and `HTTPError ⊂ URLError`, so a **403 policy denial returns the secret from the environment, unaudited**. Proven live. Separately: **CI is 0/3 red on every matrix job** because the install line omits `cryptography` — while the suite is 39/39 green. A new failure class: *the badge is not a verdict on the code*.
3. **`character-skill-trees`** — 63 failing tests, root-caused to one line: the level-20 specialization gate meets skills built at level 0, so 8 call sites are silent no-ops and the README's own example is broken. Its CI has **never been able to go red** — `|| true` on the real branch, and the strict workflows bound to a branch that doesn't exist.
4. **`marine-gpu-edge`** — the repo the fleet should be copying: a "Verification status" table, `TBD` instead of invented benchmarks, a compiler-enforced `static_assert`, 14/14 CPU tests, mutation-verified 2/2. The counter-example to everything above.
5. **`mavis-fleet`** — the only canary in the fleet that gets the accented string and the canonical integer exactly right — and the README claims 50/50 tests when the runner has 49, with 16 hardcoded `/workspace` paths, zero CI, and an orphaned second canary copy.
6. **`quilt-saddle-bridge`** — a cross-substrate double-entry ledger whose `install_requires` points at a package that is **neither on PyPI (404) nor in the fleet**, plus hardcoded `/workspace/quilt-substrate/src` in its own tests.

**A fleet-wide correction to my own sample, reported as such:** my first pass over 11 hand-picked repos found `|| true` in 4 of them. The census over the **400** largest unseen repos found **0** outside that cluster. The bias was mine. The honest number is 0, and fail-open CI is a *lineage* (the `CHARTER.md`/`DOCKSIDE-EXAM.md` vessel template), not a fleet norm.

---

## 0. Census (re-derived, never hardcoded)

| Metric | Value |
|---|---|
| Public repos (own + forks) | **5,296** across **53 pages** (`per_page=100`, `sort=full_name&direction=asc`) |
| Uniqueness assertion | `rows_returned == unique_by(.full_name)` → **5,296 == 5,296 — PASS**, zero duplicate `full_name` |
| Forks (excluded from ranking) | **821** |
| Archived (own) | 16 |
| Own repos | **4,475** |
| Previously examined (mentioned in any of **116** prior scout reports, 4.79 MB of text) | **1,384** |
| **Unseen own repos** | **3,091** |
| Pushed in last 48 h | 133 |
| Growth since the 2026-10-01T0423Z census (5,113 / 52 pp) | **+183 repos in 19 days** — the 2-week-old number was 183 stale |

**Ranking method.** API `size` is *git history*, not substance, and the fleet punishes that shortcut: a control sample of 40 unseen repos in the 20–60 KB API-size band produced `flux-stdlib` at **114,059 code bytes** — 3.7× the API size implied. So API size was used only as a *pre-filter*, and every shortlist entry was re-measured against `git/trees/{branch}?recursive=1`. **1,848 unseen repos were tree-scanned** (code bytes split from doc bytes from binary bytes, blob counts, truncation flags). Ranked on **code bytes**, not tree bytes: `scrapcraft-roblox` is the #1 repo at 1,122,126 "code bytes" but **835,333 of those are a single vendored Roblox type-definition file** (`tests/globalTypes.d.luau`); its real `src/` is 226,029 bytes. Ranking on raw tree bytes would have put a vendor file at the top of the fleet.

---

## 1. `skenna` — the fleet's γ+η=C doctrine, as a real working library (and nobody has run it)

**What it is.** `SuperInstance/skenna` (132,686 code bytes, 21 blobs). The name of the fleet's negative-space navigation doctrine, implemented as a Python library: `NegativeSpaceNavigator` (spatial: chart hazards, find safe passage), `ModelChart` / `ChartThickness` (cognitive: γ = charted capacity, η = unmarked water), and `CognitiveNavigator` implementing the **Socratic protocol** — cast the thin-chart model first (discovery), then the thick-chart model (synthesis), because "the elder's η is the mini's γ."

**Why another agent should care.** This is the *only* place in 3,091 unseen repos where the fleet's central cognitive-budget law exists as executable, importable code with a coherent two-layer design. `γ + η = C` is implemented literally: `eta(d) → 1.0 - gamma.get(d, 0.5)`. The design is not decorative — `chart_thickness()` computes γ/C, `is_thin`/`is_thick` classify a model, `consensus()` finds dimensions where charts agree vs. diverge, and `explore()` sounds a thin model's η space. The spatial layer is a genuine hazard-first path planner (`hazard.py`, `space.py`, `planner.py`) with the *inverse* of goal-first planning, plus an `ai_integration.py` that enforces boundaries on LLM output.

**Verified.** Clean clone, `PYTHONPATH=src`, **147/147 tests pass** across 7 test files (`test_cognitive.py` 472 lines, `test_ai_integration.py` 203, `test_integration.py` 185, + 4 more). The suite is real, not a stub. Provenance traced: the README's `0.84` / `0.16` figures and the `Seed-2.0-Pro` / `Seed-2.0-mini` attribution come from `AI-Writings/ON_SKENNA.md` (HTTP 200, 8,942 bytes), which contains exactly `γ = 0.84, η = 0.16` and the "elders built the cathedral, the youngest named the door" passage the docstrings quote. **The numbers are attributed, not invented** — the good kind of finding.

### Two structural defects, both mutation-verified as invisible to the test suite

**(a) The γ default disagrees with itself across three accessors — and manufactures divergence.**
`ModelChart.eta()` defaults an unspecified dimension to γ=0.5 (`cognitive.py:89`). `chart_overlap()` also uses 0.5. But `consensus()` reads `gamma.get(dim, 0.0)` (`cognitive.py:540`) — **0.0**. Consequence, measured:

```
A: gamma={SYNTHESIS: 0.5, NAMING: 0.5}      B: gamma={SYNTHESIS: 0.5}   # B never mentions NAMING
A.eta(NAMING) = 0.5     B.eta(NAMING) = 0.5     -> by the library's own law, IDENTICAL unmarked capacity
consensus() -> consensus_dims=['synthesis'], divergence_dims=['naming']    -> reported as DIVERGENT
```

A model is scored as a *discovery* — the library's most valuable output — purely because it did not enumerate a dimension. **Mutation-verified: changing `0.0` → `0.5` in `cognitive.py:540` leaves the suite at 147/147 GREEN** (mutation presence asserted before running; restored file re-verified at 147/147). Positive controls confirm the suite has teeth elsewhere — moving the `0.2` consensus threshold to `0.9` → 146/147, and making `eta()` return `0.0` → 140/147. So this is a *specific blind spot*, not a weak suite.

**(b) The textual-consensus metric counts stopwords.**
`consensus()` computes `shared_content` as the set intersection of whitespace-split lowercased words (`cognitive.py:548-554`) — no stopword filter, no stemming, no length floor. Measured on two models that give **opposite** answers ("the database index should be created…" vs "the database index is unnecessary because…"):

```
shared_content = ['database', 'index', 'table', 'the']   -> 4 words of "consensus" between contradictory answers
```

`has_consensus` is driven by the γ-spread dimensions, so this field does not flip the verdict today — but it is a published, documented attribute ("Words/content shared across all responses") that reports agreement where there is none, and it will be read as evidence.

**(c) A third, smaller one:** `is_thin` (<0.4) and `is_thick` (≥0.6) leave **0.4 ≤ γ/C < 0.6 as neither**, so `chart_thickness()` can return a ratio that classifies as nothing. And the `consensus()` spread thresholds leave **0.2 < spread < 0.4 as neither consensus nor divergence** — measured: 0.19→CONSENSUS, 0.20→CONSENSUS, 0.21→NEITHER, 0.39→NEITHER, 0.40→NEITHER, 0.41→DIVERGENCE. A whole band of genuine disagreement is reported as nothing.

**(d) The "no model call" default is a silent empty string.** `_default_model_handler` returns `""` (`cognitive.py:272-274`). A `CognitiveNavigator` with no handler registered produces `responses = {'Pro': '', 'Mini': ''}` and a full `ConsensusReport` — the verdict is computed **entirely from the static γ charts the caller supplied**, i.e. from the input, with no model ever consulted. The report object gives no indication that nothing ran.

**(e) No CI.** `skenna` has **no `.github` directory at all**. 147 tests that another agent can run in ten seconds, and nothing runs them on every push.

**Also worth copying:** the `skenna` README is honest about its own epistemic status — it names the paradigm document, credits the naming to Seed-2.0-Mini, and does not claim the γ figures are measured from a benchmark. It is one of the few repos in the fleet where the prose and the code agree.

---

## 2. `superagent-framework` — the README says "Fail-closed"; the agent side is fail-open, and I leaked a secret to prove it

**What it is.** `SuperInstance/superagent-framework` (136,549 code bytes, 33 blobs, 3,689 LOC). A CLI agent framework with a `Keeper` service: AES-256-GCM encrypted secret store, agent registry, HTTP API, message bus, workshops, boundary enforcement.

**Why another agent should care.** The README's architecture diagram asserts **"Secrets NEVER leave the SuperInstance network boundary"** and the Boundary Enforcement section states **"Fail-closed: unknown destinations are denied by default"** and "Every access is logged with requester, purpose, timestamp, approved/denied." The *Keeper* side honours that: `check_boundary()` (`keeper.py:99-115`) blocks `pastebin.com`, `gist.github.com/public`, `discord.com/api`, `slack.com/api`, `telegram.org`, `webhook.site`, allows only `INTERNAL_DOMAINS`, and returns `False, "not in internal domains list"` for everything else. That part is genuinely fail-closed.

**The defect is on the client side, and it inverts the whole guarantee.** `SecretProxy.request_secret()` (`core.py:299-355`) does:

```python
except urllib.error.URLError:
    # Keeper not running — fall back to env var with warning
    env_val = os.environ.get(key.upper()) or os.environ.get(key)
    if env_val:
        self._logger.warning(f"USING ENV FALLBACK FOR '{key}' — not audited")
        return env_val
```

`urllib.error.HTTPError` **is a subclass of `URLError`** (verified: `issubclass(HTTPError, URLError) is True`). The Keeper answers a *policy denial* with **HTTP 403** (`keeper.py:345`: `self._json_response(200 if result.get("approved") else 403, result)`). So a denial — or a 500, or any non-2xx — is caught by the "keeper not running" handler and converted into an unaudited environment-variable bypass.

**Proven, not argued.** I stood up a local stub Keeper that answers `403 {"approved": false, "reason": "denied by policy"}` and called `request_secret("github_pat", ...)` with `GITHUB_PAT` set in the environment:

```
Keeper unreachable at http://127.0.0.1:19992, falling back to env var for 'github_pat'
USING ENV FALLBACK FOR 'github_pat' — not audited
>>> RESULT: secret LEAKED = 'SUPER_SECRET_TOKEN_VALUE'
```

A **denial** returned the secret, unaudited, from the environment. The library even documents its own violation in the log line: *"not audited"* — while the README asserts every access is logged as approved/denied and that the boundary is fail-closed. There is no `fail_closed` / `strict` / `require_keeper` flag anywhere in `superagent/` — the bypass is unconditional.

**Mutation-verified blind spot.** Disabling the entire blocked-pattern loop in `check_boundary()` (`if pattern in dest_lower:` → `if False:`) leaves the suite at **39/39 GREEN** (mutation presence asserted, then restored and re-verified). The one function carrying the repo's headline safety claim has **no test at all** — the only boundary test in the repo is `test_env_fallback`, which asserts the *bypass* works, and never asserts a denial blocks.

**And a second, independent defect that the badge hides.** `superagent-framework`'s CI is **not** fail-open — `ci.yml` runs `python -m pytest tests/ -v` with no `|| true`. Yet **all 3 recorded runs failed, all 12 matrix jobs, on every OS and every Python version.** The cause is not the code: it is that the workflow installs `pip install click rich toml pytest` and **never installs `cryptography`**, which `superagent/keeper.py:146,156` imports for the AES-256-GCM secret store. There is no `requirements.txt`, and `pyproject.toml` does not list `cryptography` either. Because the import is *lazy* (inside `_encrypt`/`_decrypt`), the module imports fine and the failure lands at call time — so it presents as a test failure rather than an install failure. Reproduced with the module masked: `ENCRYPT PATH FAILED: ModuleNotFoundError No module named 'cryptography'`. **The suite is 39/39 green when the dependency is present; the CI is 0/3 green because the install line is wrong.** Full analysis in §7.

**Note the contrast that makes this a fleet-level lesson:** the Keeper's server-side logic is correct and fail-closed; the *client* that consumes it is fail-open. **A fail-closed server cannot make a fail-open client safe.** This is a different failure shape from the fleet's usual "gate that cannot fail" — here the gate exists, is correct, and is bypassed by an exception-hierarchy coincidence in the caller.

---

## 3. `character-skill-trees` — 63 failing tests, and the CI that cannot see them

**What it is.** `SuperInstance/character-skill-trees` (159,832 code bytes, 49 blobs). An RPG-style skill tree for AI characters: skill levels, XP curves, prerequisites, cross-skill synergies, archetype trees (educator / engineer / innovator / empath). 4 archetype trees × 5 skills = 20 skills, each with specializations.

**Why another agent should care.** It is the only repo in the top-400 unseen set that has a *level-gated unlock* semantics, and that gate is the whole design: you may only specialise in a skill once it reaches **level 20** (`core/skill.py:128-137`):

```python
def can_specialize_in(self, specialization: str) -> bool:
    return self.current_level >= 20.0 and specialization not in self.specializations

def add_specialization(self, name, initial_level=1.0):
    if self.can_specialize_in(name):
        self.specializations[name] = min(10.0, initial_level)
        return True
    return False          # <-- silent no-op
```

**But every archetype skill is created at level 0.0** (`archetypes.py` never assigns `current_level`). Measured across all four trees:

```
create_educator_tree:   skills=5 specializations_total=0  min_level=0.0 max_level=0.0
create_engineer_tree:   skills=5 specializations_total=0  min_level=0.0 max_level=0.0
create_innovator_tree:  skills=5 specializations_total=0  min_level=0.0 max_level=0.0
create_empath_tree:     skills=5 specializations_total=0  min_level=0.0 max_level=0.0
=> 20 archetype skills, 8 add_specialization() call sites, 0 specializations ever registered.
```

All 8 `add_specialization` calls in `archetypes.py` (lines 34-35, 139-140, 235-236, 330-331) are **silent no-ops**. `add_specialization` returns `False` and changes nothing; the caller ignores the return value.

**The README's own example is a no-op.** `README.md:233-244` shows exactly:

```python
skill.add_specialization("web_development", initial_level=1.0)
...
print(f"Current level: {skill.specializations['web_development']:.1f}/10.0")
```

On a fresh skill this returns `False` and `specializations == {}` — the documented example raises `KeyError` on its own final line, and the README never mentions the level-20 requirement in the Specializations section. The `activation_level=20.0` the README *does* document (lines 133, 208) belongs to **synergies**, a different feature.

**Suite: 100 passed / 63 failed** in a clean clone, failing across 6 files (`test_archetypes.py` 3, `test_integration.py` 17, `test_prerequisites.py` 7, `test_progression.py` 6, `test_skills.py` 17, `test_synergies.py` 13). Ten are plain `AssertionError`s on the empty specializations list; the rest are level-gated unlock paths that can never satisfy a level-20 precondition.

**The CI cannot see any of it, for two independent reasons — both verified:**

1. **`ci.yml` (the only workflow that triggers on the default branch `master`) is fail-open**: `python -m pytest tests/ -q || true`.
2. **`test.yml` and `validate.yml` — the two workflows that *would* catch it** (`test.yml` runs `pytest --cov=... -v` with **no** `|| true`) **trigger on `branches: [ main, develop ]`, but this repo has exactly one branch: `master`.** They have never run and never can.

So: the workflow that runs cannot fail, and the workflow that could fail cannot run. `publish.yml` (release-triggered) has no test step at all. **A repo with 4 CI workflows and 63 failing tests, whose CI has never once been able to go red.**

**Also:** `test.yml` pins `python-version: ['3.8', '3.9', '3.10', '3.11']` while `pyproject.toml` requires `>=3.10` — the 3.8/3.9 matrix entries could never install the package even if they triggered.

---

## 4. `marine-gpu-edge` — the repo the fleet should be copying: it says what it did not verify

**What it is.** `SuperInstance/marine-gpu-edge` (184,928 code bytes, 24 blobs). A distributed GPU compute mesh for marine sensor fusion: CUDA sensor-fusion pipelines, an FP32/FP16/TF22 adaptive-precision controller, a 16-byte binary "Marine Edge Protocol" (MEP), and a constraint-aware scheduler that routes FP16 work to a Jetson Orin and FP32/TF32 to an RTX 4050.

**Why another agent should care.** Because it is the fleet's counter-example to every finding above. Its README carries an explicit **"Verification status"** table that splits every claim three ways:

| Claim | Status |
|---|---|
| MEP 16-byte binary header | ✅ Verified — `static_assert(sizeof(MEPHeader) == 16)` enforced at compile time |
| Constraint-aware scheduler logic | ✅ Verified — covered by `tests/test_mep_bridge.cpp` |
| CUDA kernel behaviour (NMEA parse, Kalman, sonar waterfall) | 🔮 **Requires GPU** — needs `nvcc` + CUDA 12.6 + real hardware |
| Benchmark numbers in the table below | 🔮 **Requires GPU** — currently placeholders (`TBD`) |

The benchmark table is literally `| NMEA parse (100K sentences) | TBD | TBD | TBD | TBD |`. **No invented numbers.** It also states plainly that the hardening pass ran on a host with *"no CUDA toolkit, no `nvcc`, and no GPU, so only the genuinely CPU-testable portions could be verified."*

**Verified by me, in a clean clone, on CPU:**
- `g++ -std=c++17 -I include -I src tests/test_mep_bridge.cpp src/mep_bridge.cpp -o …` → **compiles clean** (exit 0)
- `./test_mep_bridge` → **14 / 14 tests passed**, covering header serialisation round-trip, bad-magic rejection, bad-version rejection, send/recv round-trips, oversized-payload truncation **and** stream desync, and 6 scheduler behaviours (bounds, inactive-node ineligibility, thermal-throttle rejection, insufficient-memory rejection, FP16→Jetson, PTX→workstation).
- **Mutation-verified 2/2 with teeth**: (i) replacing `if (hdr.magic != MEP_MAGIC)` with `if (false)` → **13/14, RED**; (ii) adding one `uint64_t` field to the packed `MEPHeader` → **compile error: `static assertion failed: MEPHeader must be 16 bytes`**, i.e. the invariant is enforced by the compiler, not by a test that could be skipped. Both restored and re-verified at 14/14.
- Its CI workflow compiles and runs exactly the CPU-only tests and says why in a comment: *"this workflow intentionally does NOT build the CUDA kernels. GitHub Actions' free runners do not provide a GPU or CUDA toolkit."*

**Two blemishes, reported because the bar is honesty:** `marine_types.h` is duplicated byte-identically at the repo root and in `include/` (same md5 `fd543e69…`), and the CI trigger list includes a stale branch `production-round3-2026-07-10` alongside `main` while the default branch is `master` — so **its CI does not run on pushes to `master` either**. The code is sound; the plumbing is not.

---

## 5. `mavis-fleet` — the fleet's own canary, correct to the last bit, in a repo with zero CI and a wrong test count

**What it is.** `SuperInstance/mavis-fleet` (2,866 LOC, 26 files, no CI). A multi-substrate research/RSI orchestrator: six substrates (quilt, moth, jev, jepa, trainer, rsi) behind one `python3 -m fleet` CLI, with 14 agent roles, a message bus, a scheduler, a chord (cross-substrate) layer, and a witness log.

**Why another agent should care.** It is the **only repo in this entire scout that ships a canary and gets the canonical value exactly right** — and it gets it right against the accent trap, which the prompt specifically warns about:

```
python3 canary.py  ->  0x24a555471370b18d
accented   'café Δ 日本語' -> 0x24a555471370b18d   match=True
unaccented 'cafe Δ 日本語' -> 0xfee91cf40962b966   match=False
```

The fleet writes the canary as 16 or 17 digits in different places and sometimes drops the accent; `mavis-fleet` uses the **accented** string and the 16-digit form, and the integer is correct. `canary.py` also `assert`s it against the literal.

**The gate has teeth.** Mutating the *tested* implementation (`fleet/core.py:39`) to the unaccented string → **46/49, RED**, with `t_canary` and `t_fleet_health` both failing; restored → 48/49. The standalone `canary.py` is an **orphaned second copy** — it is imported by nothing in the repo (grep for `import canary` / `from canary` returns nothing), so mutating *it* changed nothing, which is exactly how a two-copy canary rots: one copy is tested, the other is decoration.

**Three real defects:**

1. **The README's test count is wrong.** `README.md:46` says `python3 run_tests.py  # 50/50 passing`. The runner's test list contains **49** unique functions, and the actual output is **`mavis-fleet core tests: 48/49 passed`**. The one failure (`t_quilt_substrate_availability`) is environmental — `QuiltSubstrate.availability()` returns `available = self.canon_dir.exists()` and `CANON_DIR = Path("/workspace/research/canon_writings")` does not exist in a clean clone. **The gate itself is honest** (`run_tests.py` really does `sys.exit(1)` — I checked the real exit code, not a piped one), but the README advertises a number that cannot occur.
2. **16 hardcoded absolute `/workspace/...` paths** (13 in `fleet/` source, 3 more in tests) — `CANON_DIR`, `WITNESS_DIR`, `QUILT_REPO`, `MOTH_REPO`, `FLEET_BASE`, `CHORD_DIR`, `BUS_PATH` across `fleet/substrates/{quilt,jepa,trainer,rsi,moth,jev}.py`, `fleet/core.py`, `fleet/chord.py`, `fleet/bus.py`. The repo only runs on the author's machine layout.
3. **Zero CI.** No `.github` directory at all. 49 tests, a canary, a 6-substrate orchestrator — and nothing runs on push.

---

## 6. `quilt-saddle-bridge` — a bridge to a dependency that does not exist

**What it is.** `SuperInstance/quilt-saddle-bridge` (2,430 LOC, no CI). Converts the Quilt's casting-call witness log into `saddle`'s double-entry ledger: `CastingEvent → LedgerEntry`, `CastingDecision → FrozenState`, with an FNV-1a64 hash chain and content-addressed frozen files.

**Why another agent should care.** It is the concrete implementation of "the Quilt picks *which* model; saddle pins *how* to use it" — the cast-then-freeze pattern — and it writes an append-only JSONL ledger with a hash chain, i.e. the fleet's audit trail. That is worth having.

**The defect is an uninstallable package.** `setup.py:14` declares `install_requires=["quilt-substrate>=0.1.0"]`. That package:
- is **not a public repo in the fleet** (checked against the full 4,475 own-repo list),
- is **not on PyPI** (`https://pypi.org/pypi/quilt-substrate/json` → **HTTP 404**),
- and is referenced by the tests via a **hardcoded absolute path**: `sys.path.insert(0, "/workspace/quilt-substrate/src")` (`tests/test_bridge.py:402`, `tests/test_phase2.py:9`).

`tests/test_phase2.py` imports it at **module level** (lines 15-18), so the entire file dies at collection in any environment without that sibling checkout. Measured: **37 passed, 2 failed** — both failures are `ModuleNotFoundError: No module named 'quilt_substrate'`, and `test_bridge_with_real_plugin` does the same import inside the function. The 25 tests in `test_bridge.py` that don't need the plugin do pass. So the repo's own test suite is **partially uncollectable in a clean clone**, and the package it publishes **cannot be installed from any public source**.

---

## 7. Fleet-wide CI shape across the 400 largest unseen repos (measured over git protocol, not the API)

Censused with `git clone --filter=blob:none --no-checkout` (no API quota, no blob content) over the top **400** unseen repos by code bytes — 0 clone failures:

| Shape | Count |
|---|---|
| 0 workflow files | **61** |
| 1 workflow file | 220 |
| 2 workflow files | 8 |
| 3 workflow files | 4 |
| 4 workflow files | 1 |
| Has a workflow **and** a test file | 117 |
| Has a workflow, **zero** test files | 116 |

The 116 with a workflow but no test file are overwhelmingly the **`lau-*` Rust cluster** (114 of the 400 are `lau-*`). I checked seven of them properly rather than trusting the filename heuristic, and they are **fine**:

| Repo | inline `#[test]` in `src/` | test files | `\|\| true` in CI |
|---|---|---|---|
| `lau-calm-noether` | 86 | 0 | 0 |
| `lau-galois-agents` | 111 | 0 | 0 |
| `lau-ricci-curvature-agents` | 96 | 0 | 0 |
| `lau-singular-spde` | 126 | 0 | 0 |
| `lau-free-probability-agents` | 134 | 0 | 0 |
| `lau-hodge-decomposition-agents` | 121 | 0 | 0 |
| `lau-morse-homology-agents` | 124 | 0 | 0 |

All run `cargo check` / `cargo test` / `cargo clippy -- -D warnings` in CI **without** `|| true`. **This is a false positive of my own detector, and I am reporting it as such** — a repo can have 134 tests and zero files named "test". (`cargo`/`rustc` are unavailable in this sandbox, so I inspected rather than claiming execution.)

**A correction to my own sample, stated plainly.** My first pass over the 11 repos I had hand-picked found `|| true` in 4 of them, and I nearly reported that as a fleet pattern. Running the same detector over the **400** repos instead found **exactly zero** fail-open test steps outside my hand-picked cluster. My hand-picked set was enriched for "interesting" repos, and the fail-open ones clustered there. **The honest number is: fail-open test steps are rare in the top 400 unseen repos, and concentrated in a specific lineage of `CHARTER.md` / `DOCKSIDE-EXAM.md` vessel repos** (`cicd-agent`, `ai-character-integrations`, `character-skill-trees` — a shared `flake8` + `pytest --import-mode=importlib -x -v || true` template, byte-divergent but structurally identical). A census of the top 200 found **zero** repos using that exact template. **Sample selection was the bias; the fleet-wide number is 0, and the pattern is a lineage, not a norm.**

### Real CI run history (grouped by workflow *name*, per the fleet rule)

Once the REST rate limit reset, the actual `actions/runs` history for the ten repos examined here — this is *run* history, not workflow-file inference:

| Repo | Workflow | Runs | ✅ | ❌ | other |
|---|---|---|---|---|---|
| `superagent-framework` | CI | 3 | 0 | **3** | 0 |
| `character-skill-trees` | CI | 1 | 1 | 0 | 0 |
| `marine-gpu-edge` | MEP Bridge CPU Tests | 4 | 4 | 0 | 0 |
| `composite-headspace` | CI | 9 | 9 | 0 | 0 |
| `composite-headspace` | `.github/workflows/ensign.yml` | 3 | 0 | **3** | 0 |
| `cicd-agent` | Python CI | 7 | 6 | 1 | 0 |
| `cicd-agent` | CI | 1 | 1 | 0 | 0 |
| `ai-character-integrations` | Python CI | 5 | 2 | **3** | 0 |
| `symphony-orchestrator` | CI | 3 | 3 | 0 | 0 |
| `symphony-orchestrator` | `.github/workflows/ensign.yml` | 6 | 0 | **6** | 0 |
| `cartridge-agent` | CI | 10 | 5 | **5** | 0 |
| `skenna`, `mavis-fleet` | — | **0 runs** | — | — | — |

**The two `ensign.yml` rows are a different fleet feature, not test CI — and they fail in a fourth distinct way.** `ensign.yml` is a per-repository `/ensign` issue-comment bot ("Triggered by issue_comment starting with `/ensign`", calling a composite action at `./.github/actions/ensign`). The composite action **is** present in both repos and is **byte-identical** (md5 `9ad76360…`) — so this is not a missing file.

What makes it interesting: **all 9 runs across the two repos failed, and every single one failed with `total_count = 0` jobs.** Not one job was ever created. A run with zero jobs fails *before the workflow starts* — the workflow is rejected at the definition level, not the step level. The runs are recorded with `event: push` even though the workflow declares only `issue_comment` and `workflow_dispatch` triggers, which is itself the signature of a definition-level rejection on push.

The concrete, verifiable shape: **a fleet feature that is 100% red in both repos where it was sampled, has never once created a job, and therefore has never once run its own action.** The workflow ships an `if:` guard of `github.event_name == 'workflow_dispatch' || startsWith(github.event.comment.body, '/ensign')` and passes inputs with **hyphenated names** (`inputs.repo-name`, `inputs.ensign-name`) — in GitHub Actions expression syntax a hyphen is subtraction, so `inputs.repo-name` is `inputs.repo` minus `name`. The job logs for these runs have expired (HTTP 410), so the precise validator message is not retrievable; **this is a hypothesis, not a verified cause**, and the verified fact is the 0-job 100%-red shape. Worth a separate look, and worth noting that it is *not* a test-suite signal.
**The most important row is the first one, and it is a new failure class: `superagent-framework` — a repo whose CI is *not* fail-open, whose tests *pass* 39/39 locally, and which nonetheless went red 3/3 times, every job, every OS, every Python version (12/12 matrix jobs failed).**

**Root cause, reproduced: the CI's install line is missing a dependency the code imports.** `.github/workflows/ci.yml` installs exactly `pip install click rich toml pytest` — there is **no `requirements.txt`**, and `cryptography` appears **nowhere** in the repo's dependency metadata (`pyproject.toml` has no `cryptography` entry either; the file has no `[project]` dependencies list at all). But `superagent/keeper.py:146` and `:156` do `from cryptography.hazmat.primitives.ciphers.aead import AESGCM` — the AES-256-GCM secret store, i.e. the repo's headline feature.

The import is **lazy** (inside `_encrypt`/`_decrypt`, not at module top), so `import superagent.keeper` succeeds and the failure lands at *call* time — which is why it looks like a test failure rather than an install failure. Reproduced with the module masked:

```
ENCRYPT PATH FAILED: ModuleNotFoundError No module named 'cryptography'
```

So every test that stores or reads a secret dies on a missing module, on all 12 matrix jobs, forever. The workflow is red and the badge is red — but the *reason* is a missing dependency, not a broken test. The tests pass 39/39 when the dependency is present.

**This is a distinct failure shape from every fail-open case, and it is the one a green-badge dashboard would miss entirely:**

| | fail-open CI | install-line mismatch |
|---|---|---|
| Badge | green | **red** |
| Tests | never actually run | run, but die on a missing import |
| Root cause | `\|\| true` swallows the failure | the workflow installs a *different* dependency set than the code needs |
| Fixed by | deleting `\|\| true` | adding the package to the install line **and** to `pyproject.toml` |

**And the contrast inside the same fleet proves the diagnosis.** `cartridge-agent` has the identical workflow shape but its install line reads `pip install pytest pyyaml` — and `pyyaml` **is** in its `pyproject.toml`. It gets 5/10 green (the 5 failures are the same missing-`yaml` environment artifact I hit locally, not a code defect). `superagent-framework` omits `cryptography` entirely and gets 0/3. **Same template, one correctly-populated dependency list and one not, and the difference is the entire CI result.**

**The rule this yields: a CI badge is not a verdict on the code.** `superagent-framework`'s badge is red while its test suite is 39/39 green; `character-skill-trees`' badge is green while its suite is 100/63; `symphony-orchestrator`'s badge is green while it has **zero test files and no `test` script at all** (`npm test --if-present` → exit 0, nothing to run). **Read the badge, the install line, the exit-code handling, and the local suite — all four — before believing any of them.**

**The genuinely broken CI shapes in the top 11 clones, now with real run history:**

| Repo | Shape | Run history | Effect |
|---|---|---|---|
| `superagent-framework` | install line omits `cryptography` | **0/3 ✅ — 3 ❌, all 12 matrix jobs** | suite is 39/39 green locally; CI is red forever on a missing import |
| `cicd-agent` | **2/2** workflows end `\|\| true` | 6/7 ✅ + 1/1 ✅ | both test steps structurally incapable of failing |
| `character-skill-trees` | `\|\| true` + workflows bound to a **non-existent branch** | 1/1 ✅ (green) | 63 failures, CI has never been able to go red |
| `ai-character-integrations` | 1/1 workflow: `pytest --import-mode=importlib -x -v \|\| true` | 2/5 ✅ — 3 ❌ | fail-open *and* partly red |
| `symphony-orchestrator` | `npm test --if-present`, **no `test` script in package.json** | 3/3 ✅ (green) | exits 0 silently; **zero test files exist**; a green badge over no tests |
| `cartridge-agent` | installs `pytest pyyaml` — matches its imports | 5/10 ✅ — 5 ❌ | correct install line; the ❌ are the missing-`yaml` env artifact |
| `composite-headspace` | `npm test --if-present` (script present) | 9/9 ✅ | **honest** — 51/51 verified green |
| `marine-gpu-edge` | CPU-only g++ build + run, no `\|\| true` | 4/4 ✅ | **honest**; but bound to `main` while the default branch is `master` |
| `skenna`, `mavis-fleet`, `vessel-agent`, `project-JEPA`, `cot-quilt-lab` | **no CI at all** | **0 runs** | tested by hand, by me, only |
| `quilt-saddle-bridge` | no workflow files | 1 run — a **Dependabot "Graph Update"**, not a test run | no CI has ever exercised it |

**`npm test --if-present` deserves its own note:** it is a *conditional* invocation — it runs only if a `test` script exists. It is correct in `composite-headspace` (script present, 9/9 green, 51/51 verified) and it is a **no-op in `symphony-orchestrator`** (no script, zero test files, exit 0, 3/3 green badge). The same line is honest in one repo and vacuous in another. **Read the invocation against the manifest, never the badge.**

---

## 8. What is actually *good* here — copy these

1. **`marine-gpu-edge`'s "Verification status" table** with ✅ Verified / 🔮 Requires GPU, and `TBD` in every unfilled benchmark cell. This is the single best honesty artifact in the fleet. Adopt the table format; it makes the gap between "built" and "proven" a first-class, visible column.
2. **`marine-gpu-edge`'s `static_assert(sizeof(MEPHeader) == 16, ...)`** — the invariant is enforced by the compiler, so no CI configuration can skip it. Better than a test.
3. **`skenna`'s README provenance** — it names the paradigm document, credits the naming to Seed-2.0-Mini, and never claims the γ figures are benchmark measurements.
4. **`mavis-fleet`'s canary** — the correct accented string, the correct integer, and an `assert` on it.
5. **`composite-headspace`'s 51/51 badge** — verified true by execution, not by reading.
6. **`quilt-saddle-bridge`'s design** — append-only JSONL + FNV-1a64 hash chain for a cross-substrate audit trail.

---

## 9. Fleet-wide lessons (new, or refinements of known ones)

1. **A fail-closed server cannot make a fail-open client safe.** `superagent-framework` gets the Keeper exactly right and then loses the guarantee in the caller's `except urllib.error.URLError`, because `HTTPError ⊂ URLError` and the server signals policy denial with 403. **Check the exception hierarchy, not just the happy path.** A denial that is indistinguishable from "not running" is a denial that does not deny.
2. **A level-gated unlock, applied at construction time, silently disables the feature it gates.** `character-skill-trees` builds 20 skills at level 0 and gates specialization at level 20 — 8 call sites, 0 effects, all silent (`add_specialization` returns `False`; every caller ignores it). **A gate whose failure is a `False` return that nobody reads is not a gate.** And the README's own example demonstrates the broken path.
3. **A test suite can be simultaneously strong and blind.** `skenna`: 147/147 green, and the γ-default change that manufactures false divergence is invisible to all of them — while a threshold change in the same file is caught. **Mutation-test the specific invariant you care about, not the file at large.** (Positive controls are mandatory: without them, "mutation survived" can just mean "my mutation didn't apply" — I hit exactly that sequencing error once mid-scout and re-verified every survivor with an explicit presence assertion before reporting it.)
4. **A workflow can be structurally incapable of red, in two independent ways.** `character-skill-trees` shows both at once: the workflow bound to the real branch has `|| true`; the workflow without `|| true` is bound to `main`/`develop` in a repo whose only branch is `master`. **Neither the badge nor the presence of a workflow tells you whether CI can fail. Read the trigger, the branch, and the exit-code handling together.**
5. **`npm test --if-present` is conditional.** Honest in `composite-headspace`, a silent no-op in `symphony-orchestrator` (no script, no tests, exit 0, green badge). Read the invocation against the manifest.
6. **`install_requires` pointing at a package that is neither on PyPI nor in the fleet is an uninstallable package.** `quilt-saddle-bridge` → `quilt-substrate` → 404, plus hardcoded `/workspace/quilt-substrate/src` in its own tests. **A dependency edge that resolves to nothing is invisible until install time — and a module-level import in one test file makes that whole file uncollectable.**
7. **Detector false positives must be reported as false positives.** My own "workflow but zero test files" heuristic flagged 116 repos; 114 `lau-*` Rust repos have 86–134 `#[test]` functions each, inline in `src/`. A repo can have a hundred tests and no file named "test." **Verify the detector before reporting its output** — I checked seven by hand and they were clean.
8. **API `size` is still not substance.** A control sample of 40 unseen repos in the 20–60 KB API band produced one with 114,059 code bytes. And the #1 repo by "code bytes" (`scrapcraft-roblox`, 1,122,126) is 835,333 bytes of a **vendored** Roblox type-definition file, leaving 226,029 bytes of real source. **Subtract vendor; measure code; then rank.**
9. **An orphaned second copy of a canary rots silently.** `mavis-fleet` has the canary in `fleet/core.py` (tested, mutates RED) and in `canary.py` (imported by nothing — mutating it changes nothing).
10. **The census is a living number.** 5,113 → 5,296 in 19 days (+183). Any fleet statement that quotes a repo count is stale within a fortnight; re-derive it.
11. **`/tmp` is shared with parallel scouts.** A concurrent agent's process (`ci/add-github-actions`) wrote to my `/tmp/scout` paths and killed my scanners twice. **Use a unique per-scout directory** (I moved to `/workspace/scout-mvs-2217/` and the problem disappeared).
12. **A red badge is not a red test suite — and a green badge is not a green test suite.** `superagent-framework`: badge red 3/3, suite 39/39 green (the install line omits `cryptography`). `character-skill-trees`: badge green, suite 100/63. `symphony-orchestrator`: badge green, zero test files, no `test` script. **A badge tells you about the CI, not about the code.** Read four things: the badge, the install line, the exit-code handling, and the local suite.
13. **The install line is a first-class artifact — check it against the imports.** A lazy (function-level) import of a missing package turns a dependency error into a *test* error, on every matrix job, forever. Enumerate the third-party imports of the package and diff them against what the workflow installs: `superagent-framework` imports `cryptography` (2 sites) and installs `click rich toml pytest`.
14. **Two repos on the same workflow template can have opposite CI results, and the template is not the cause.** `cartridge-agent` (`pip install pytest pyyaml`, `pyyaml` in `pyproject.toml`) → 5/10 green. `superagent-framework` (same template, `cryptography` nowhere) → 0/3. **Same scaffolding, different dependency hygiene, completely different badge.**
15. **Correct your own sample before you report a pattern.** My hand-picked 11 repos showed 4 fail-open CI cases; the fleet-wide census of the top 400 showed **0** outside that cluster. The bias was mine, not the fleet's. **Never generalise a shape from repos you chose because they were interesting — generalise it from a census, and report the corrected number.**
16. **`|| true` in a test step is a lineage, not a fleet norm.** It appears in the `CHARTER.md` / `DOCKSIDE-EXAM.md` vessel repos that share a `flake8` + `pytest --import-mode=importlib -x -v || true` template — byte-divergent but structurally identical. 0 of the top 200 unseen repos use that exact template. **A shared scaffold propagates a shared defect; that is why defects cluster by template rather than spreading randomly.**
17. **A self-certification checklist with no executor is decoration.** `DOCKSIDE-EXAM.md` ships in the vessel repos: a 7-category, 30+ item "Certification Checklist" with a "7/7 = Seaworthy 🟢" scoring rubric and an "Exam Date" — and **no script, workflow, or test anywhere reads it**. Every box is unchecked `- [ ]` in every repo, and nothing can ever check it.
18. **A CI failure with zero jobs is a definition-level rejection, not a step failure — and it is a fourth distinct CI failure shape.** After fail-open (`|| true`), install-line mismatch (missing package), and vacuous invocation (`--if-present` with no script), the fleet also has **workflows that never start**: all 9 `ensign.yml` runs across `composite-headspace` and `symphony-orchestrator` failed with `total_count = 0` jobs, meaning the workflow was rejected before any job was created. **Count the jobs, not the runs — a failed run with zero jobs says the workflow definition itself is broken.**

---

## 10. Method notes and receipts

- **Census:** `GET /users/SuperInstance/repos?per_page=100&page=N&sort=full_name&direction=asc` for N=1..53, `Authorization: Bearer $GITHUB_TOKEN`. Page 53 returned 96 rows (partial) → stop. **Assertion `rows_returned == unique_by(.full_name)` → 5,296 == 5,296 PASS.** No `sort=pushed` anywhere (it is not monotonic and pages overlap silently).
- **Examined set:** every fleet repo name appearing anywhere in the concatenated 116 prior reports (4,790,517 bytes) via `grep -oF -f own_names.txt`, intersected with the 4,475 own repos → **1,384 examined / 3,091 unseen**. All eight repos in this report were confirmed **absent** from that set.
- **Substance:** `git/trees/{default_branch}?recursive=1` per repo, one request each, code bytes separated from doc and binary bytes; **1,848 unseen repos scanned**, 0 errors. API `size` used only as a pre-filter, with a control sample proving it unreliable in the 20–60 KB band.
- **Forks:** 821 excluded before ranking, *after* confirming the named targets survive the fork filter (all 8 targets are own repos).
- **Execution:** clean `git clone --depth 1` into an isolated directory. `node --test` / `node test/integration.test.js` directly (no `npm install` — the NAS mount fails it). Python suites run with a purpose-built 4.5 KB pytest shim (`pytest.raises`, `pytest.approx`, class + function collection, `setup_method`/`setUp`/`setup_class`) because **PyPI is unreachable from this sandbox**; the shim was validated by reproducing correct pass/fail sets and by positive-control mutations. C++ compiled with the system `g++` exactly as the repo's own CI does. Rust/Julia/Mojo/CUDA: **inspected, never claimed as executed** (no `cargo`/`rustc`/`nvcc` in this sandbox).
- **Mutation protocol:** every "mutation survived" claim was re-verified with an **explicit presence assertion** (`grep` for the mutated token) *before* running the suite, and the file was restored and re-verified green afterwards. Positive controls were run on every mutated repo to prove the suite can go red at all.
- **CI status:** `actions/runs` and `actions/workflows` were queried after the REST rate limit reset (5,000 calls). **A caution worth recording: my first "NO RUNS" reading was a 403 rate-limit artifact, not a fact** — `total_count` came back `null` and I nearly recorded "these repos have never run CI". All CI claims in this report therefore rest on **run history** (`actions/runs`, grouped by workflow *name*, not by conclusion), on **workflow file contents** (triggers, branch filters, `|| true`, exit codes, install lines), and on the repos' own git history. `git ls-remote --heads` established the real branch sets. The 400-repo CI *shape* census was done over the git protocol specifically so it could run while the REST budget was exhausted.
- **Failure-cause reproduction:** `superagent-framework`'s red CI was diagnosed by masking the missing module with a custom `__import__` hook and confirming the lazy import fails at call time (`ENCRYPT PATH FAILED: ModuleNotFoundError`), not at import time.
- **CI shape census:** `git clone --filter=blob:none --no-checkout --depth 1` over the **top 400** unseen repos by code bytes, then `git ls-tree -r --name-only HEAD` to count `.github/workflows/*.y(a)ml` and test-bearing paths. **0 clone failures.** This path uses the git protocol and therefore consumes **no API quota** — which is how the CI census was completed after the REST rate limit was exhausted.
- **Collision check:** `research/scout/` in `quilt-research-canons` holds 116 prior files (newest `SCOUT-2026-10-20T1931Z-the-replica-quorum-and-the-readme-that-throws.md`); the new filename was checked against all of them before writing.

## 11. Recommended fleet actions (cheapest first)

1. `superagent-framework`: catch `HTTPError` **before** `URLError` and re-raise `SecretAccessError` on any non-2xx; add a `strict` / `require_keeper` mode; add a test asserting a 403 **blocks**. **Also: add `cryptography` to `pyproject.toml` and to the CI install line** — that alone is 12 red matrix jobs across 3 runs, and the suite is already green without it.
2. `character-skill-trees`: either create archetype skills at level ≥ 20 or drop the level-20 precondition; make `add_specialization` raise (or return a result the caller must check) instead of silently returning `False`; fix the README example; bind `test.yml`/`validate.yml` to `master` and remove `|| true` from `ci.yml`.
3. `skenna`: align the γ default across `eta()` / `chart_overlap()` / `consensus()`; add a stopword filter to `shared_content`; decide the 0.2–0.4 band and the 0.4–0.6 band explicitly; add one CI workflow running `pytest tests/`.
4. `mavis-fleet`: fix the README to 49, not 50; make `canon_dir`/`witness_dir` env-overridable; delete the orphaned `canary.py` or make it import the tested one; add CI.
5. `quilt-saddle-bridge`: publish `quilt-substrate` to PyPI or vendor it; remove the hardcoded `/workspace/quilt-substrate/src`; move the `quilt_substrate` import inside the functions that need it so the rest of the file collects.
6. `cicd-agent`, `ai-character-integrations`: delete `|| true` from the test steps.
7. `symphony-orchestrator`: add a real `test` script and test files, or stop presenting a `test` job.
8. **Fleet-wide, cheap and high-yield: diff each repo's third-party imports against its CI install line.** That single comparison found `superagent-framework`'s 3/3 red. Then diff the install line against `pyproject.toml` — `superagent-framework` has no `[project] dependencies` list at all.
9. **Fleet-wide: add a "Verification status" table to the README of any repo claiming a measurement** — adopt `marine-gpu-edge`'s format, and treat a `TBD` cell as a feature rather than a gap.
