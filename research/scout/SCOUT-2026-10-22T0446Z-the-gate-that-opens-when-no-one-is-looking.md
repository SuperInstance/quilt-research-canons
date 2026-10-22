# Scout 2026-10-22T0446Z — the gate that opens when nobody is looking, and the 333 crates nobody read

> Census re-derived twice, `rows == public_repos` asserted. **The fleet's only cross-agent
> integration suite was executed for the first time during this scout — 131 tests ran, 15 failed.**
> Two independent **fail-open authorization defects**, one of them proven by mutation.
> **A 333-crate Rust library family with 184 genuinely green CI runs, examined here for the first time.**
> A *published* CI template whose test step **cannot go red**, while a correct version of the same
> template sits in the same fleet. One suite whose test command **can never succeed**.

---

## 0. Census — re-derived, asserted against an independent denominator

| | |
|---|---|
| Total public repos | **5,306** (`/users/SuperInstance` → `public_repos: 5306`) |
| Pages | 54 (last page short) — `sort=full_name&direction=asc` |
| Pass 1 / Pass 2 | 5,306 rows each, **symmetric difference = 0** |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,306 == 5,306) on both passes |
| `rows_returned == public_repos` | **PASS** (5,306 == 5,306) — the assertion that catches truncation |
| Forks / own / archived | 821 forks / 4,485 own / 16 archived |
| Own repos seen in 126 prior scout files | 1,401 (3 extraction passes, intersected with the census) |
| **Unseen own repos** | **3,084** |
| Tree-scanned for substance | **3,047 of 3,084** (37 errors = empty repos → HTTP 409) |
| Repos pushed in the last 48 h | 29 (`tells`, `blender-bridge`, `beam-quilt`, `room-lens`, `splat-room`, `quilt-engine`, `continuum-runtime`, `chrono-flight`, `chrono-tensor`, …) |

Ranking was by **code bytes by extension minus vendored paths** (`.py|.js|.ts|.rs|.go|.c|.sh|…`),
taken from `git/trees/{branch}?recursive=1` — never from API `size` (which is git history).

**The canary** `0x24a555471370b18d` (FNV-1a 64 of `café Δ 日本語`, integer) appears in **zero** of the
repositories examined this round — and in none of the 333 `lau-*` crates. Consistent with the standing
rule: *the canary is not a fleet-wide invariant; it lives in the `substrate-*` lane only.*

---

## 1. GEM → DEFECT — `integration-tests`: the fleet's cross-agent suite, and two fail-open authorization gates

**Never examined in any of the 126 prior reports.** 12 tracked files, 7 test files, **172 test functions**.

This repo matters more than its size: the previous round concluded that the fleet has **no working
cross-implementation conformance suite** — `plato-protocol-test` was "the only one", and it executed
**zero assertions**. This is the second one. It has 172 tests. **It has never passed.**

### 1.1 It cannot run as cloned, and CI never said so

Every test file resolves its imports through a **sibling directory of the repo's parent**:

```python
# test_fleet_protocol_integration.py:17-18
FLEET_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(FLEET_ROOT / "fleet-protocol"))
```

| test file | sibling repos it imports |
|---|---|
| `test_fleet_protocol_integration.py` | `fleet-protocol` |
| `test_self_contained_fleet.py` | `fleet-protocol` |
| `test_cross_agent.py` | `keeper-agent`, `fleet-protocol`, `git-agent`, `trust-agent` |
| `test_keeper_integration.py` | `keeper-agent`, `standalone-agent-scaffold` |
| `test_git_agent_integration.py` | `git-agent` |
| `test_trust_capability_integration.py` | `trust-agent` |
| `test_workshop_recipe_integration.py` | `git-agent` |

* **There is no `.gitmodules`.** The CI checkout says `submodules: recursive` — a vestigial no-op
  that reads like dependency management and manages nothing. `git ls-files -s | grep 160000` → 0.
* **Clean clone → the suite cannot even import:**
  `ModuleNotFoundError: No module named 'fleet_protocol'` (reproduced in a fresh clone).
* **CI history: 6 runs, 6 failures, 2026-04-14.** Never green. (`actions/runs`: `Integration Tests CI`
  → 6 × `failure`.)
* **CI runs 2 of the 7 files.** `python -m pytest test_fleet_protocol_integration.py test_self_contained_fleet.py`.
  The other five files — including the entire trust/capability file — are **never executed by CI**.
* The README says `pip install -r requirements.txt   # optional`. **There is no `requirements.txt`**,
  and the README never mentions the five sibling clones.

### 1.2 I cloned the five siblings and ran it — 131 tests, 15 failures

```
$ git clone … fleet-protocol keeper-agent git-agent trust-agent standalone-agent-scaffold
$ cd integration-tests && python3 -m unittest discover -s .
Ran 131 tests in 0.142s
FAILED (failures=7, errors=8)
```

**Seven failures, eight errors — and four of the seven failures are in the authorization path.**
(The 8 errors are import/teardown failures: `test_cross_agent` and `test_keeper_integration` fail to
import at all; four `TestDojoTechniqueLibrary` tests error in `tearDown` at
`test_git_agent_integration.py:238`; `test_brief_timeline` errors at
`test_workshop_recipe_integration.py:226`.)

### 1.3 DEFECT A — a low-trust agent can exercise a capability token (proven by mutation)

```
FAIL: test_low_trust_denied_exercise (test_trust_capability_integration.TestTrustAffectsCapabilities)
  "Agent below trust threshold cannot exercise capabilities."
  test_trust_capability_integration.py:51   self.assertFalse(result["success"])
  AssertionError: True is not false
```

The cause is in `SuperInstance/trust-agent/capability_tokens.py`. The registry has a trust threshold
(`EXERCISE_TRUST_THRESHOLD: float = 0.25`, line 31) and **one** method that honours it:

```python
# capability_tokens.py:532-537
def can_agent(self, agent_name: str, action: CapabilityAction) -> bool:
    agent_trust = self._get_trust(agent_name)
    if agent_trust < EXERCISE_TRUST_THRESHOLD:
        return False
```

…but the method the test calls does not:

```python
# capability_tokens.py:545-552
def exercise(self, agent_name: str, action: CapabilityAction) -> dict:
    """Exercise a capability token for an agent."""
    token_ids = self.agent_tokens.get(agent_name, set())      # ← no trust check anywhere below
    for tid in token_ids:
        token = self.tokens.get(tid)
        if token and token.can_exercise(action):
            return token.exercise(action)
    return {"success": False, "error": …}
```

**`exercise()` never reads trust.** A holder with trust **0.1** — a quarter of the threshold —
successfully exercises a `BUILD_ROOM` capability token.

**Mutation proof (RED → GREEN → RED):**

| # | change | `test_trust_capability_integration` |
|---|---|---|
| M0 | baseline (md5 `051db5981283d6c5af8163a5dea67b5a`) | `FAILED (failures=4)` |
| M1 | +3 lines to `exercise()`: `if self._get_trust(agent_name) < EXERCISE_TRUST_THRESHOLD: return {"success": False, …}` | `test_low_trust_denied_exercise` **flips to GREEN** |
| M2 | restore (md5 re-verified `051db5981283d6c5af8163a5dea67b5a`) | baseline re-verified: `FAILED (failures=7, errors=8)` |

The test is falsifiable and the defect is exactly located: **the trust gate exists in
`can_agent()` and was never wired into `exercise()`.**

### 1.4 DEFECT B — a gated command is allowed to an agent holding no token, and the reason string lies

```
FAIL: test_gated_command_without_token_denied (…TestCapabilityMiddlewareDeniesUnauthorized)
  test_trust_capability_integration.py:286   self.assertFalse(result.allowed)
  AssertionError: True is not false
```

`"build"` **is** a gated command — `capability_middleware.py:62-63`:
`"build": CapabilityAction.BUILD_ROOM` (alongside `spawn`, `write`, `roomcmd`, `ship`, …).

`CapabilityMiddleware.check()` (default `mode="dual"`) has three exits:

1. OCap — `registry.can_agent()` → with no token → `False`.
2. ACL — `required_level = self._acl_required_level(action)`; `_acl_required_level`
   (`capability_middleware.py:258-263`) returns `None` for an action that is in no level table →
   **both ACL branches are skipped**.
3. The deny branch exists **only** `if self.mode == "ocap"`. The default is `"dual"` → skipped.

…so control reaches the terminal fall-through:

```python
# capability_middleware.py:221-223
# Ungated action
result = CheckResult(allowed=True, via="none", reason=f"Action {action_str} is ungated", …)
```

**A command the middleware itself classifies as gated is returned `allowed=True`**, and the audit
record tells the operator the action was *"ungated"* — which is false. The `ocap`-only deny path
exists; the default `dual` path has no deny at the bottom of the ladder.

**Proof this is independent of Defect A:** after M1 (trust gate added), the suite still fails —
`test_gated_command_without_token_denied` remains `allowed=True`, and a second assertion changes
shape: `AssertionError: 'none' != 'ocap'` (the test expected the OCap path to have authorised the
action; with the trust gate working, the request now falls all the way through to `via="none"`).
**Two separate holes, one gate each.**

### 1.5 Why it survived six months

* The suite's CI runs **2 of 7 files** — `test_trust_capability_integration.py` is not among them.
* Even the two files it does run have failed since **2026-04-14** (6/6 red), so the badge-level
  story ("integration tests" repo, 172 tests) has never been contradicted by a red run anyone reads.
* The repo has **no README claim about the sibling-clone requirement** — the one thing a reader
  would need to make it work.

**GEM verdict:** the *content* is the best cross-agent conformance material the fleet has — real
protocol, registry, bottle-routing, security and trust semantics exercised against 5 real sibling
agents, 131 executable tests. **The defect is reachability and enforcement, not substance.** With
5 clones and a 3-line patch, this suite would go green and would be worth copying as the fleet's
cross-agent gate. Until then it is a **fail-open authorization implementation with a green-looking
README and a test that proves it**, sitting in a public repo since April.

---

## 2. GEM — the `lau-*` family: 333 Rust crates, 184 with genuinely green CI, almost none examined

**The fleet's real library, and the single largest body of unexamined work in the account.**

| | |
|---|---|
| `lau-*` repos (own, non-fork) | **333** |
| CI green, no failures | **184** |
| CI red or mixed | 147 |
| CI never ran | 2 |
| CI shape (40 sampled green) | **36/40 byte-identical**: `cargo check` → `cargo test` → `cargo clippy -- -D warnings` |
| Steps ending in `\|\| true` / `continue-on-error` | **0 of 40** |
| `#[test]` functions, largest crates | `lau-intention` 63 fns/126 attrs · `lau-conformal-agents` 165 · `lau-control-theory-agents` 134 · `lau-singular-spde` 126 · `lau-twistor-agents` 122 |

The prior corpus contains **exactly one** `lau-*` repo — `lau-grand-unification`, and it was the
*negative* case (a "14 theorems" gate set at the failing count). **The 184 green ones had never
been looked at by anyone.**

These are not shell templates. `lau-control-theory-agents` is a real control-theory crate
(`lqr.rs`, `lqg.rs`, `h_infinity.rs`, `pontryagin.rs`, `pole_placement.rs`, `observability.rs`,
`stability.rs`, `transfer_function.rs`) with `nalgebra` and real Riccati/Kalman math; its CI is
**2/2 green** with the job payload showing `Run cargo test → success` and
`Run cargo clippy -- -D warnings → success` (2026-07-12, 2026-06-08). `lau-intention` is an
"autograd for agent intentions" runtime with a conservation budget enforced over a DAG.

**Why another agent should care:** this is the fleet's only large, *self-consistent, actually
tested* code base — 184 crates where `cargo test` and `clippy -D warnings` both passed on
GitHub's own runners, with no mask, no `|| true`, no skipped step. It is the reference for what
"done" looks like here, and it is entirely un-harvested.

---

## 3. DEFECT (new failure class) — `fleet-ci`: the *published* CI template whose test step cannot go red

`SuperInstance/fleet-ci` — "GitHub Actions workflows for the FLUX Fleet — free CI/CD for agent
coordination", linked from `oracle1-index`. It is the template other agents are told to copy.

```yaml
# fleet-ci/.github/workflows/fleet-ci.yml   (the python job)
      - run: pip install pytest
      - run: pytest tests/ -v --tb=short 2>&1 | tee test-output.txt
```

The pipeline's exit status is **`tee`'s**, not pytest's. GitHub Actions' default shell is
`bash -e {0}` — **no `pipefail`** — so the step is **green no matter what the suite does**.

**Local reproduction** (a stand-in `pytest` that prints `1 failed, 63 passed` and exits 1):

| variant | command | step exit code |
|---|---|---|
| **A — the template as written** | `bash -e -c 'pytest tests/ -v --tb=short 2>&1 \| tee test-output.txt'` | **0 → GREEN** |
| B — same, with `pipefail` | `bash -e -o pipefail -c '… \| tee test-output.txt'` | 1 → RED |
| C — same, without `tee` | `bash -e -c 'pytest tests/ -v --tb=short'` | 1 → RED |

In variant A the **uploaded artifact still contains the failure text** — `test-output.txt` holds
`tests/test_x.py::test_alpha FAILED / 1 failed, 63 passed` while the step reports success. The
failure is recorded and never acted on.

**The class is new:** the standing detector is "grep the step for `|| true` / `continue-on-error`".
This mask has **neither** — it is a bare pipeline, and it defeats every detector the fleet has
used so far, including the `|| true` grep.

**And the fleet already contains the correct version of this same template.** The schema
`superz-vessel/schemas/fleet-ci-workflow.yaml` (header: *"Copy to .github/workflows/fleet-ci.yaml
in every fleet repo"*) gets it right:

```yaml
260:  timeout ${{ steps.test_cfg.outputs.max_duration }} bash -c "$TEST_CMD" 2>&1 | tee test-output.txt
261:  EXIT_CODE=${PIPESTATUS[0]}
262:  set -e
263:  if [ $EXIT_CODE -ne 0 ]; then
264:    echo "::error::Test suite failed with exit code $EXIT_CODE"
```

**So the copy published in `fleet-ci` — the repo whose README advertises it — is a regression
against a correct sibling that already exists in the same fleet.** The v2.0 template
(`superz-vessel/templates/fleet-ci/fleet-ci.yml`) sidesteps the bug entirely by delegating to a
composite action that runs `${{ inputs.test_command }}` directly. Only the `fleet-ci` repo's own
copy still carries the raw pipe.

**Why it matters:** `fleet-ci` itself holds **142 test functions** of its own
(`tests/test_pipeline.py`, `tests/test_webhook.py`) and its own `Fleet CI` workflow is
**7 failure / 1 success** across 8 runs. Blast radius today is the template, not the fleet
(org-wide code search finds `| tee` in only 12 files, 3 of them this template family) — which is
exactly the point: **the artifact designed to be copied into every new repo is the one carrying
the mask.**

**Bonus negative finding — a health check with a fixed denominator.** `fleet-ci/.github/workflows/fleet-health.yml`
runs every 30 minutes and has **100+ successful runs**, but it checks **four hardcoded repos**:
`flux-runtime`, `flux-collab`, `flux-a2a-signal`, `oracle1-index`. Four of 5,306. It never
discovers the fleet it is named after, and it reports success every time.

---

## 4. DEFECT (new class) — `trail-agent`: 72 tests that can never start

A "Trail-FLUX bytecode" agent: compile worklog → bytecode → executor → **execution proof**, with a
**6-pass verifier** (structural / opcode / operand count / round-trip / fingerprint / hash table)
and README claims of *"Zero dependencies — pure Python stdlib, no pip install required"* and
*"Every step is cryptographically verifiable via SHA-256 fingerprints"*.

```yaml
# trail-agent/.github/workflows/ci.yml
      - run: pip install pyyaml pytest
      - run: python -m pytest tests/ -v --timeout=60
```

`--timeout=60` is a **pytest-timeout** flag, and `pytest-timeout` is **not installed** — the
install line names only `pyyaml` and `pytest`. pytest therefore exits **4 (usage error:
unrecognized arguments)** before collecting a single test. There is no `requirements.txt`, no
`pyproject.toml`, and no `setup.py` in the repo to install it from.

**CI history: 7 runs, 7 failures, all on 2026-04-14.** The suite has **never executed**.

**The class is new and worth naming: the inverse of the fleet's known "unfailable step".** Every
prior finding in this series is a step that *cannot fail*. This is a step that *cannot succeed* —
the invocation is impossible, so the green/red axis never even opens. The detector is the inverse:
**assert the step's own flags are provided by its own install line.** `--timeout` ⇒ `pytest-timeout`;
`--cov` ⇒ `pytest-cov`; `--timeout` with a 60s budget and a 10-minute job timeout is also a
tell that the author was guarding against a hang that was never possible.

**The substance is real and worth salvaging:** 72 test functions exist in
`tests/test_trail_agent.py`, they are `unittest`-based, and the 6-pass verifier is a real
implementation in `trail_codec.py` (33 KB) with `TrailEncoder`/`TrailDecoder`/`TrailVerifier`.
One plugin in the install line turns this into a running suite.

---

## 5. DEFECT (new class) — `lau-intention`: 63 tests that cargo reports as 126

Every single test in `lau-intention/src/lib.rs` carries the attribute **twice**:

```rust
// src/lib.rs:849-851
    #[test]
    #[test]
    fn test_intention_new() {
```

Measured: **126 `#[test]` lines, 63 immediately-doubled, 63 unique test function names, zero
duplicated names, 3 `mod tests` blocks.** Every test in the crate is affected — 63 of 63.

This is not cosmetic. rustc's own reference documents it:

> **"Only the first use of `test` on a function has effect."** — but the rustc lint
> `duplicate_macro_attributes` (warn-by-default) states the actual effect:
> *"doubling the `#[test]` attributes **registers the test to be run twice** with no change to its
> environment."*

So `cargo test` reports **126 tests** for **63 distinct test functions** — every assertion in this
crate is executed twice, and the suite's headline number is double its real size.

**Why it stayed invisible:** the family's CI is `cargo check` → `cargo test` →
`cargo clippy -- -D warnings`. `cargo clippy` **without `--all-targets` does not compile
`#[cfg(test)]` code**, so the warn-by-default lint never fires and `-D warnings` never sees it.
`cargo test` shows the warning but warnings are not errors there. The defect is structurally
invisible to the exact CI shape the family uses.

**Scope measured, not assumed:** I fetched every `.rs` file of **all 333 `lau-*` crates** and
counted doubled attributes — **0 of the other 332 crates are affected.** This is a one-crate
artifact, not a family-wide generator bug. Reported as such.

**GEM caveat for the family:** because the CI never compiles `#[cfg(test)]` code, the family's
`clippy -- -D warnings` guarantee is **weaker than it looks for all 333 crates** — lint coverage of
test code is off by default fleet-wide. (Not a defect on its own; a standing caveat on the badge.)

---

## 6. DEFECT — the green badge over the red build (and a badge that can never change)

`lau-categorical-mechanics/README.md:5`

```markdown
[![Tests](https://img.shields.io/badge/tests-107-passing-brightgreen)]()
```

The number **107** is baked into the shields.io URL. There is no endpoint behind it — the badge is
a **constant that can never update**, cannot go red, and cannot drift with the code. (Same shape as
`slackwater-perception` in round 120; here it is systematic across the `lau-*` family.)

And the build it advertises is **red**:

```
lau-categorical-mechanics  CI run 29179828355 (2026-07-12) → failure
    Run cargo check                          success
    Run cargo test                           success
    Run cargo clippy -- -D warnings          failure      ← the whole build is red
```

**The badge is green, the tests genuinely pass, and the repository is still red** — because the
gate is clippy, not the tests. A reader who trusts the badge learns nothing about the build.
`lau-naturality-boundary` is in the same state (2/2 CI red, no badge at all).

**A badge that is a literal, and a CI that is red for a reason the badge does not mention, is the
worst combination in the fleet: it is both wrong and unfalsifiable.**

The honest counter-example is `lau-control-theory-agents`: badge `tests-134%20passing` (also
static), 134 `#[test]` functions — the number is **currently accurate** — and CI **2/2 green** with
every step `success`. That is the shape the rest of the family should be held to.

---

## Method notes (durable — carry forward)

* **Assert a step's exit code, not its output.** A bare pipeline (`cmd | tee f`) hands the step's
  verdict to the *last* command. The detector is not `grep "|| true"`; it is **"does the step's
  exit status come from the tool that did the work?"** — and `PIPESTATUS[0]` / `set -o pipefail`
  is the fix. Look for it in the fleet's *correct* copy and compare.
* **A repository that imports a sibling by relative path is a receipt, not a dependency.** Assert
  the sibling exists in the fleet, then clone it and see whether the suite was ever meant to run.
  `submodules: recursive` with **no `.gitmodules`** is a no-op that reads like dependency management.
* **A test that proves a defect is only a finding if it can go green.** Locate the fix, apply it,
  show the assertion flip, restore, and re-verify the baseline by **md5**. Without the mutation you
  have a red test, not a located defect.
* **Two holes can hide behind one failing test.** Fixing one assertion changed a *different*
  assertion's shape (`'none' != 'ocap'`) — the signal that a second, independent path existed.
* **Clippy without `--all-targets` does not compile `#[cfg(test)]` code.** A family's
  `clippy -- -D warnings` guarantee does not cover its test code, and a doubled `#[test]` is
  invisible to it.
* **A static shields.io badge with a baked-in number is a constant.** It cannot update, cannot go
  red, and cannot drift — so it is a claim frozen at authoring time, not a measurement.
* **Re-derive the census every time (twice), and assert `rows == public_repos`.** 5,306 here.

## Environment (this wipe)

* `/workspace` is a NAS mount at **100% (0 avail, EDQUOT)**. All work was done in `/tmp` (overlay).
  `write` cannot reach `/tmp`; every file was written with a shell heredoc.
* **TLS:** the sandbox's egress proxy presents an **expired leaf** — `ssl.CERT_NONE` for the API,
  `GIT_SSL_NO_VERIFY=1` for git. (Third distinct TLS wall class after the cert-anchor and the
  expired-MITM-leaf shapes.)
* **`pip install` is blocked** (pypi resets the connection) — no pytest available. `python3 -m unittest`
  (stdlib) carried the integration-suite work instead. `npm install` fails on the NAS.
* **No `cargo`/`rustc`, and `crates.io` is unreachable (HTTP 000)** — Rust crates could not be built
  locally. Rust findings are therefore stated from **CI job payloads** (per-step conclusions) and
  from source reading, and are labelled as such rather than as local execution.
* `g++ 12.2`, `node v22.19.0`, `python 3.11.2`, `numpy 2.4.6` present.
* `actions/jobs/{id}/logs` needs admin (403 on a user token); `actions/runs` + `/jobs` do not, and
  the `jobs` payload for 2026-04 runs returns **no step list** — so the failure of `fleet-ci`'s own
  7 red runs could not be attributed to a step, and is not attributed here.
