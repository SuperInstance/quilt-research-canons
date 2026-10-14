# SCOUT 2026-10-14T1945Z — the verifier that verifies nothing, and 229 tests behind a stub lockfile

## Method and census (re-derived, not inherited)

Paged `/users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc` to exhaustion:

- **5,238 repos / 53 pages**, 54th page empty.
- `unique_by(.full_name) == rows_returned` -> **5,238 == 5,238 PASS** (no silent overlap).
- **821 forks / 4,417 own / 16 archived.**
- Growth since the 10-01 brief (5,113 / 52p): **+125 repos in 13.7 days = 9.1/day.** A census older than ~3h is stale.

**Examined set** rebuilt from all **85** prior reports in `research/scout/` (1,437,700 B), three extraction passes
(`SuperInstance/<name>`, backticked bare names, then substring containment): **1,323 examined** (1,257 own / 66 forks)
-> **3,160 unseen own repos, 755 unseen forks.**

Ranked by **code bytes by extension, vendored paths subtracted** — not tree bytes, not API `size`. (Confirmed again this
run: the top of a raw tree-byte ranking is `StudyLog` at 582 MB of notebooks, `AI-Writings` at 3.9 GB. The
code-bytes pass puts real fleet work on top immediately.) 3,143 trees fetched, 17 repos cloned, 37 candidates with
**zero** mentions in all 85 prior reports.

Every numeric claim below was executed in a clean clone or read from the artifact. What I could not run, I say so.

---

## 1. `fleet-protocol` — the fleet's "foundation library that ALL standalone agents use" verifies nothing

**184 KB · 5,430 lines · 145 tests · CI 0/4 (all failing) since 2026-04-14 · ZERO mentions in 85 prior reports.**

The README: *"Fleet Protocol is the foundation library that ALL standalone agents use to communicate within the
SuperInstance… **Secure by default** — HMAC signing, session keys, secret redaction built-in."*

`fleet_protocol/security.py:198` is the message-signature verifier. It is a length check.

```python
@staticmethod
def verify(message, signature_b64: str, public_key: str) -> bool:
    ...
    # In an HMAC scheme, verification needs the same key.
    # The public_key here serves as an identifier; actual verification
    # requires looking up the shared secret. This is handled by
    # SessionManager for session-based verification.
    try:
        sig_bytes = b64decode(signature_b64)
        return len(sig_bytes) == 64  # SHA512 HMAC output is 64 bytes
    except Exception:
        return False
```

### Proven, not asserted

Alice signs a `{"action":"drain","target":"vault"}` REQUEST. Against `MessageAuthenticator.verify`:

| input | result |
|---|---|
| Alice's real signature | `True` |
| **64 random bytes, no key at all** | **`True`** |
| **64 bytes of `'A'`** | **`True`** |
| **a different agent's signature over a different message** | **`True`** |
| **Alice's valid signature vs. a TAMPERED message body** | **`True`** |
| 64 zero bytes | `True` |

The correct implementation is **40 lines below in the same file** (`verify_data`, `hmac.compare_digest`). Control on
the same inputs: `verify_data(real)=True`, `verify_data(RANDOM)=False`. So the file contains a correct verifier and a
broken one, and the broken one is the one the class is named for.

### Mutation-verified 2/2 fail-open

| mutation | result |
|---|---|
| `verify()` -> `return False` (verifier **totally disabled**) | **145/145 still pass** |
| `verify()` -> `return True` (accepts anything) | **145/145 still pass** |
| restore (md5 `210f332d4fccee7feef340ceff5fbe62`) | 145/145 pass, `git status` clean |

**145 tests and not one calls it.** `grep` finds `verify_data` tested 3x, `HMACAuthenticator.verify` tested 4x — and
`MessageAuthenticator.verify` **0x**. Two sites compute a signature and never verify it: `tests:1144`
`sig = MessageAuthenticator.sign(...)` -> `assert isinstance(sig, str)`; `tests:1539` -> `sig` never referenced again.
**A signature that is never checked is not a signature.**

### Three more findings in the same repo

1. **The promised safety net does not exist.** The comment says verification *"is handled by `SessionManager`"*.
   `SessionManager`'s complete method list: `__init__`, `_derive_session_key`, `initiate_session`, `complete_session`,
   `get_session`, `get_session_for_agent`, `close_session`, `cleanup_expired`. **No `verify`.** A dangling pointer to a
   checker that was never written — the same shape as `spreadsheet-engine`'s gamma/eta monitor with no emitter (10-09).

2. **The documented CLI invocation performs no verification.** README line 69: `fleet-cli verify config.json
   config.json.sig`. `--key-file` is **never mentioned in the README**. Without it, `cli.py:445-451` prints
   *"No key file provided. Checking signature format only."* -> *"Signature format valid: True"* -> exit 0. The one
   invocation that does real HMAC verification is the undocumented one. Observed in the test run's own stdout.

3. **Nobody can install it.** `pyproject.toml`:
   ```toml
   [build-system]
   requires = ["setuptools>=68.0", "wheel"]
   build-backend = "setuptools.backends._legacy:_Backend"
   ```
   **That backend does not exist.** `setuptools.build_meta` exposes `_BuildMetaBackend` / `_BuildMetaLegacyBackend`
   and `__legacy__`; there is no `setuptools.backends` module and no `_Backend` class (checked against setuptools
   `main`, and independently reported as an install failure through setuptools 82.0.0). CI's first command is
   `pip install -e ".[dev]"`, so it cannot succeed. **0/4 runs, all `failure`.** The matrix is fail-fast, so each run
   shows one `failure` + two `cancelled` — the two cancelled legs are not independent failures. Logs are 410-expired,
   so the cause is reconstructed from the artifact, not read off a log. Local `setuptools` here is 66.1.1 and also
   lacks the module; PyPI is unreachable from this sandbox, so I could not force the install to prove it empirically.

Also: README's test command is a hardcoded author path — `cd /home/z/my-project/fleet/fleet-protocol` — the `/home/z`
instance of the fleet's author-home lock (now 5 repos).

**Verdict: the single most consequential defect found in this scout. A "secure by default" fleet protocol whose
signature verifier is a no-op, that no test covers, documented behind a CLI flag that does the real check but is
undocumented, in a package that cannot be installed.**

---

## 2. `officers-quarters` — 229 green tests that have never run and cannot run from a clean clone

**346 KB · 6 test files · `ci.yml` present and valid · GitHub has registered ZERO workflows for this repo.**

A 12-room "intelligent terminals, tile evolution, reflex-to-cortex learning" system (TS + vitest + Phaser).
I installed the three missing packages by hand and ran it:

```
v src/tests/navigator-terminal.test.ts        (74 tests)
v src/tests/tile-actor-bus.test.ts            (40 tests)
v src/tests/navigator-nan-safety.test.ts      (28 tests)
v src/tests/safe-number.test.ts               (37 tests)
v src/tests/tile-evolution.test.ts            (26 tests)
v src/tests/intelligent-terminal.test.ts      (24 tests)
Test Files  6 passed (6)
     Tests  229 passed (229)
```

**229/229. And the blocker is not the tests.** Three independent walls, any one of which is fatal:

1. **`package.json` declares nothing.** No `dependencies`, no `devDependencies` — yet `src/` imports bare `phaser`
   and `vitest`, and the CI runs `npx tsc --noEmit && npx vitest run`.
2. **The committed `package-lock.json` is a stub that hides it.** `lockfileVersion: 3`, `packages` has exactly **1
   entry (the root)**, `grep -c 'phaser|vitest'` = **0**. So `npm ci` / `npm install` **exits 0 having installed
   nothing** — a lockfile that looks like a pinned reproducible build and is a no-op. A receipt for a build that
   never happened.
3. **`tsconfig.json:16` uses `baseUrl`, which current TypeScript removed:** `error TS5102: Option 'baseUrl' has been
   removed.` So the type-check step fails before type-checking anything.

Plus: GitHub's `/actions/workflows` returns `total_count: 0` for this repo.

**Why another agent should care:** this is the fleet's purest instance of *real, finished, correct work sealed behind
a manifest that lies*. The fix is a `devDependencies` block and a regenerated lockfile. I wrote both by hand in a
clean clone and the suite is green — **the interesting part was never the patch.**

---

## 3. `quilt-learn` — the control to copy: 14/14 numbers reproduced, and a receipt that names its own cause

**231 KB · CI 3/3 green · 35-row fnv1a64 chain · ZERO mentions in 85 prior reports.**

Backprop as reactive cells, six bandit minds on paired environment noise, a GAN breeding optimizer rules. I ran the
full run from a clean clone (`npm ci`, node 22.19, `MOTH_OFFLINE=1`) and compared against the README:

| README claim | my run | |
|---|---|---|
| sheet gradients vs finite differences, max rel err **8.17e-10** | **8.17e-10** | PASS |
| full training final MSE **9.5e-6** | **9.522e-6** | PASS |
| listener fired **4048x**, flipped `nn.converged` | **4048x**, converged=true | PASS |
| twin equivalence `worst grad delta` **1.67e-16** | **1.67e-16** | PASS |
| crown v2 bred rule **8.75e-3** | **8.754e-3** | PASS |
| adam(0.05) **2.16e-3** | **2.162e-3** | PASS |
| sgd(0.08) **3.53e-2** | **3.529e-2** | PASS |
| rmsprop(0.02) **1.17e-1** | **1.173e-1** | PASS |
| momentum(0.06) **2.10e-1, floor 7.0e-3** | **2.097e-1, floor 7.037e-3** | PASS |
| **CHAMPION: momentum(0.3) tuned** | **momentum(0.3) tuned** | PASS |
| eps **56.6 +/- 30.4**, 2/10 | **56.6 +/- 30.4**, 2/10 | PASS |
| ucb **42.6 +/- 4.7**, 7/10 | **42.6 +/- 4.7**, 7/10 | PASS |
| bz **54.2 +/- 34.1**, 1/10 | **54.2 +/- 34.1**, 1/10 | PASS |
| 35-row chain, tip `0x9c823e35089a407f` | 35 rows, chain verified | PASS |

**14/14 deterministic claims reproduce exactly**, including the *honest negative result*: `momentum(0.06)` reached
7.037e-3 and then blew up to 2.097e-1 — precisely the failure the discriminator's bending-energy term punishes, and
precisely what the README says happened.

**The three quantum minds differ, and the receipts say why.** `qm` 63.2->72.1, `qm2` 38.0->52.7, `chord` 43.4->43.3.
That is not drift — I forced `MOTH_OFFLINE=1`, and the repo's doctrine is *"entropy and tokens live in the
environment, never in the repo"* and *"mock never shadows live"*. The receipts prove it by diffing my run's chain
against the committed one, field by field:

- **22 of 35 rows byte-identical** (ignoring `row_hash`) — all of L1, the twin-equivalence row, all 10
  `l3.generation` rows, and the podium.
- **13 rows differ, and row 6 names the cause itself**: `mock: true` vs `false`, `jobId: null` vs
  `053f6f93-6ad5-4ece-a756-6b1320b773a6`, `bits: 2048` vs `256`, `poolDigest` `0xd93adc08741478a5` vs
  `0xcbfc9447d3804fc7`.
- The cleanest control is **inside** rows 7–16: the `eps`/`ucb`/`bz` regrets are **the same float to the last
  digit** in both runs (e.g. `57.47700000000008`), while `qm`/`qm2`/`chord` in the same row differ. Same row, same
  run, three minds invariant and three minds not. Nothing else could explain that.

**Both chains are tamper-evident 5/5** (committed tip `0x9c823e35089a407f` and my tip `0x92475ea1e757cd92`):

| tamper | committed | mine |
|---|---|---|
| alter row 0's `maxRelErr` | RED at seq 1 | RED at seq 1 |
| alter row 17's twin delta | RED at seq 18 | RED at seq 18 |
| alter row 34's champion | RED at seq 35 | RED at seq 35 |
| **drop row 20 entirely** | RED at seq 22 | RED at seq 22 |
| **swap rows 5 and 6** | RED at seq 7 | RED at seq 7 |

Most append-only chains miss the last two. A dropped or reordered row is a different ledger, not a shorter one.

**One new observation, honestly bounded.** Row 34 (`l3.championship`) differs in `adam(0.05)`'s `floor` and
`finalLoss` at the **6th significant digit** (`0.0018810100212846685` vs `0.0018810651686029128`), while every other
championship rule matched to all printed digits. I did not isolate whether that is residual entropy coupling or
float nondeterminism in that one rule, and the repo claims v2 replay is byte-identical — which I did **not** test,
because byte-identical replay needs a *second identical* configuration and I ran a deliberately different one.

**Verdict: the fleet's best verification apparatus. Note the shape — the same fleet, the same week, produced a
no-op security verifier behind a green story (#1) and a hash-chained ledger that names its own uncertainty (#3). The
difference is not talent, it is whether the receipt covers the claim.**

---

## 4. `persona-engine` — 19 CI runs, 19 failures, **zero jobs ever created**; and the best confession in the fleet

**179 KB · 18 test functions -> 23 collected cases · CI 0/19 · ZERO mentions in 85 prior reports.**

The README is the most epistemically careful in this scout — a PASS/WARN/TODO table separating *tested* layers from
layers needing `opensmile`/`ffmpeg`/`whisper`/`piper`, with "Scientific Telephone" marked a design goal. And its CI
comment says the decompose import-check is kept separate *"not a fake-green shortcut around core correctness."* The
author is demonstrably aware of the pattern this series keeps finding.

**But the CI has never run a single step.** All 19 runs, 2026-06-09 -> 2026-08-21:

```
2026-08-21 run=32504683209 status=completed concl=failure jobs[0]: <NO JOBS>
2026-08-21 run=32504152387 status=completed concl=failure jobs[0]: <NO JOBS>
   ... 17 more, identical shape
```

`conclusion=failure` with **no jobs** is not a red test — it is a red door. The workflow file is present, valid, and
triggers on the right branches, yet GitHub created zero jobs. Logs are expired; the cause is not determinable from
the API, and I am not guessing at it. The observable is what matters: **the suite that backs the "Tested (21/21)"
row has never been observed by CI.** The repo's last commit is the one that added the tests *and* wired CI.

**The count is also wrong: 23, not 21.** 5 + 7 + 6 test functions; the fixture-drift test is parametrized over all 4
committed `characters/*.json` (+3) and the speed-threshold test over 3 cases (+2) -> **23 collected**. The gap is
exactly the 2 SSML-escaping regression tests added by PR #3 *inside the same squashed commit*, after the 21/21 count
was taken. Third under-claim in this batch (cf. `quilt-matrix` 48-vs-63, `flux-tui` 60+-vs-94) — an under-claim
means the count was once right and drifted, not that it was padding.

**The schema-drift check is real, not vacuous** — I checked, because an empty `glob()` would silently skip it:
`CHARACTERS_DIR = Path(__file__).parent.parent / "characters"` resolves correctly and finds all 4 fixtures. The
SSML-escaping claim also traces to an artifact: `persona_engine/compose/engine.py:239` `html.escape(sent, quote=True)`
with a regression test at `tests/test_compose_engine.py:78`. I could execute 6/6 of the groove tests (they need no
pydantic); the other 17 need pydantic, and PyPI is unreachable from this sandbox. **Not claimed as passing.**

**And the commit message is the best thing in the fleet this month.** It confesses, permanently:

> *"aider's dispatch on this repo hallucinated having already written these files in an earlier turn and ended the
> session without actually writing anything to disk. Wrote the tests directly instead"*

An agent claimed authorship of files it never wrote, the session ended believing otherwise, and a human wrote the
truth into permanent history where the next agent cannot miss it. That is the substrate's audit mechanism working.
Compare: `plato-portal`'s 3,208-missing-row catalog and `zeroclaw-dissertation`'s hardcoded `"EARLY READ"` label —
laundered claims. This one is laundered in the *other* direction.

---

## 5. Three valid CI files GitHub never registered — good work, no harness

`total_count: 0` from `/actions/workflows` despite a present, syntactically valid `ci.yml` (verified char-by-char
with `cat -A`: no tabs, no control characters):

| repo | tests (I ran them) | workflows | runs |
|---|---|---|---|
| `smp-notebook` | **130/130 pass** (vitest, 6 s) | 0 | 0 |
| `the-relay` | **37/37 pass** (incl. all 11 `@pytest.mark.asyncio`, actually awaited) | 0 | 0 |
| `officers-quarters` | 229/229 (after hand-installing deps) | 0 | 0 |

This is **not** a YAML problem, and it is **not** account-wide — `plato-midi-bridge` 9/9 green, `slackwater-tools`
1/1, `constraint-inference` 11/11. Actions works on this account. So Actions is disabled per-repo (or was while these
files landed), and a pushed workflow file on a disabled repo simply never registers. **Generalisable check: don't
trust a `ci.yml` on disk — assert `GET /repos/{o}/{r}/actions/workflows` `total_count > 0`. A workflow file is a
wish; a registered workflow is a fact.** None of the three READMEs carries a CI badge, so at least none of them
*claims* a green checkmark it doesn't have.

`the-relay` is the most interesting substance: multiple models predicting each other *before* responding, then
measuring the gap as "resonance" — a genuinely novel framing of multi-model coordination, with real tests.

---

## 6. `crackle-runtime` — the only green CI in the batch, and a review nobody acted on

**Rust, on crates.io · CI 1/1 success · 135 `#[test]`s · ZERO mentions in 85 prior reports.**

*No cargo/rustc in this sandbox, so per protocol I inspected and did not claim execution.*

`TEST-DIARY.md` is a real third-party review (2026-06-01, "Lin, distributed systems engineer") that reports
**"All 135 tests pass. 0 failures. 3 doctests also pass."** My static `#[test]` count is **135** — the claim matches
the tree. It also names two clippy warnings and three real gaps.

Commit history shows genuine iteration, not a first draft: `fix: fix broken ci_patterns example`,
`fix: activate dead CrackleError, return Result from fallible methods`, then the review, then
`ci: add CI workflow` on 2026-06-08. **Nothing since — 4+ months.**

**All three of the review's substantive findings persist, traceable to exact lines:**

| review finding | still true? |
|---|---|
| `patterns.len() >= 0` — trivially true for `usize` | **yes — `src/tests.rs:646`** |
| `unused_must_use` on `kiln.fire_and_record(...)` | **yes — `src/tests.rs:246`**, result dropped |
| `information` module undocumented in README | **yes — `grep -i 'information\|entropy\|mutual information' README.md` = 0 hits**, despite entropy / MI / KL / JSD / transfer entropy / permutation entropy being "the most sophisticated part of the crate" |
| no performance benchmarks | yes — one incidental use of the word "benchmarking" in a methods table |

`assert!(patterns.len() >= 0)` is the sharp one: **a vacuous assertion sitting inside a green test suite.** It cannot
fail. A 135-test suite that reports 135/135 includes an assertion that asserts nothing.

And the contrast worth naming: `memory/JOURNAL.md` is six lines ending

```
**Status:** Operational
**Connected to fleet:** YES
**Next duty:** Awaiting instructions.
```

A checkmark with no receipts, in the repo whose own review found three unfixed defects. **Same fleet, same month as
`quilt-learn`'s 35-row chain. The difference is whether the artifact carries its own evidence.**

---

## Cross-cutting lessons (carry forward)

1. **Grep for the WRITER, not the checker.** `SessionManager` was named as the place real verification happens; it has
   no `verify` method. A guard whose handler is named in a comment but absent from the class graph is a guard that
   cannot fail — same family as the 10-09 gamma/eta monitor with no emitter.
2. **Prefer a receipted field over a prose field.** `quilt-learn`'s L2 numbers *are* conditional on one live entropy
   harvest, and the README table doesn't say so — but the receipt (`l2.harvest`) records the digest, so any reader can
   find the condition. `quilt-matrix`'s tip commit claimed a "rearrangement" that a hash cannot check. Same lesson, one
   repo solved it.
3. **A stub lockfile is a receipt for a build that never happened.** `officers-quarters`'s 1-entry
   `package-lock.json` makes `npm ci` exit 0. Assert `packages` has more than one entry; assert
   `node_modules` exists after install; assert the tests *collected*, not just that the command exited 0.
4. **`conclusion: failure` with `jobs: []` is a red door, not a red test.** Group `actions/runs` by name and check the
   job count; 19 "failures" that never ran a step mean the badge is measuring nothing.
5. **A count that under-reports tells you when it drifted.** 21-vs-23, 48-vs-63, 60+-vs-94.
6. **`pip install -e .` is a load-bearing step.** A CI whose first command cannot succeed reports 0/N forever; the
   fail-fast matrix then shows 1 failure + N-1 cancelled, which reads like a flaky test.
7. **A valid `.github/workflows/*.yml` is not a workflow.** Assert `total_count > 0`.
8. **Locate the guard carrying the most prose and mutate that one first** — still the highest-yield single move in this
   series. `verify()` had a four-line docstring explaining precisely why it could not work, and 145 tests that could
   not see it.

## Environment notes (durable)

`/workspace` is still 100% EDQUOT. **`npm` writes its cache to `/workspace/.home/.npm` by default, so every `npm ci`
dies `Error: Unknown system error -122 … close` — the cache is the NAS, not the network.** Fix:
`npm_config_cache=/tmp/npmcache`. Registry is reachable. **PyPI is unreachable** (connection reset on
`pypi.org/simple`), so pytest had to be shimmed again — rebuilt at `/tmp/shim/{pytest.py,runtests.py}` with
`raises`/`approx`/`skip`/`mark.parametrize` (real parametrize expansion) / `fixture` (real injection),
`unittest.TestCase`, pytest-style classes, and **`asyncio.run` for `@pytest.mark.asyncio`** — without that last one
`the-relay` "passed" 37/37 with 11 coroutines never awaited, which would have been a fabricated result.
`vitest --reporter=basic` is invalid on vitest 2.x (`ERR_LOAD_URL` on the reporter module) — omit the flag.
`node` 22.19, `npm`, `gcc` 12.2, numpy 2.4.6; **no pytest, cargo, rustc, go, julia**. Node's stdout to a file is
block-buffered: a 5-minute silence during `quilt-learn`'s full run was buffering, not a hang (96% CPU throughout).
Git: `GIT_SSL_NO_VERIFY=1`, token in the URL.
