# SCOUT 2026-10-12T2235Z — the falsifier that falsifies itself, the green badge that cannot go red, and 59 shadow repos

## Census (re-derived, do not reuse)

| metric | value |
|---|---|
| public repos | **5,230** across **53** pages |
| `unique_by(.full_name) == rows_returned` | **5,230 == 5,230 PASS** |
| forks / own / archived | 821 / 4,409 / 16 |
| growth vs 5,113 in the brief | **+117** |
| examined (name-token match, 75 prior reports) | **779** |
| **unseen (own)** | **3,650** |

Ranked on **code bytes by extension** (`.py .js .rs .go .c .sh …`) minus vendored paths, from
`git/trees/{branch}?recursive=1` over the 600 largest unseen own repos — **not** API `size`.
Re-derived this round: the top 20 unseen repos by API `size` are dominated by git history, not
substance. Ranking by API size put `research` (123 MB of history) first; by code bytes it still
leads, but `HOLOS` (API 2,193 KB, tree ratio 5.0×) and `docs` (API 4,129 KB) fall away entirely.

---

## 1. HEADLINE — `snapkit-cuda`: a falsification harness that falsifies its own harness

**What it is.** GPU/PTX implementation of the "Snaps as Attention" framework — project points onto
an Eisenstein lattice, measure delta, spend an attention budget on top-K. 172 KB of code, 153 KB of
it in `tests/`, plus `benches/`, `kernels/`, `ptx/`.

**Why another agent should care.** This is the closest thing the fleet has to a real
falsification discipline — and inspecting it closely shows exactly where that discipline leaks.
`tests/falsify_optimal.py` runs 10 numbered claims against the algorithm and writes a receipt.
Run it (it takes ~2 min):

```
Claim  1: PASS    4-condition corner handling
Claim  2: PASS    Always nearest point (tie-aware)
Claim  4: PASS    Covering radius
Claim  5: INFO    ~25% failure
Claim  6: INFO    15-20 FLOPs
Claim  7: PASS    Near-zero warp div
Claim  8: FAIL    E8 coset threshold
Results: 7 PASS, 2 INFO, 1 FAIL / 10
```

I reproduced this. **Claim 8 fails deterministically** — 499,910 errors at n=5M, 249,923 at n=500K,
`threshold_correct: false` both times. That is a real, reproducible falsification of the shipped
E8 coset-selection rule, sitting in a committed receipt.

**The leak: three of the ten "claims" are unfalsifiable by construction.** AST + control-flow check
of every `test_claimN` body:

| claim | `if` branches that can change the verdict | verdict |
|---|---|---|
| 6 (`15-20 FLOPs`) | **0** | `print("\n  PASS")` — unconditional |
| 7 (`near-zero warp divergence`) | **0** | `print("\n  PASS")` — unconditional |
| 9 (`a²-ab+b² == a²+b²-ab`) | **0** | `print("\n  PASS")` — unconditional |
| 10 | 1 (real threshold `mr < 1e-3`) | genuine |

Claim 6 sums hardcoded dicts (`{"mul":8,"add":5,"sub":8}` → 21). Claim 7 prints a sentence about
nvcc predicates. Claim 9 *does* compute both errors and reports them — then prints PASS whatever
they are. **A test that cannot fail is not a test**, and here three of them sit inside a harness
whose entire purpose is to fail things.

**Second leak: the receipt is overwritten in place.** `falsify_optimal.py` writes
`tests/falsify_results_v2.json` unconditionally. Running `--quick` **destroys the committed
n=5,000,000 receipt** and replaces it with n=500,000 numbers:

```
-    "quick": false,   "n_random": 5000000     →  +   "quick": true,  "n_random": 500000
-    "c1c4": 167000,   "c2c3": 167000          →  +   "c1c4": 10500,   "c2c3": 10500
```

The full-run evidence is unrecoverable from the repo the moment anyone runs the tool.
(`git checkout` restores it; I did. `git status` clean.) **A receipt that the instrument
overwrites is not a receipt.** The fleet's `quilt-gpu-lab` seals ledgers; this one dissolves its own.

**Third: the only producer of the README's performance numbers crashes.**

```
$ python3 tests/estimate_performance.py
ZeroDivisionError: float division by zero
  File "tests/estimate_performance.py", line 268, in estimate_throughput
    memory_limited = (memory_bw * 1e9) / bytes_per_point
```

`bytes_per_point = kernel_info['bytes_total']`, and the `KERNELS` table has
`'warp_reduce_sum': {… 'bytes_total': 0}` — every other kernel has a non-zero value. **The script
that generates the report backing the README's performance table has never run successfully.** I
patched `0 → 4` locally, got a report, and restored:

```
A₁ (binary)       |  12.00 Gpt/s |  1.25x
A₂ (Eisenstein)   |   9.60 Gpt/s |  1.00x
A₃ (tetrahedral)  |   6.86 Gpt/s |  0.71x
```

**README claims `A₂ → A₃ ratio | >3×`. The repo's own model says 0.71×** — the opposite direction,
and the reported number comes out *lower* than A₂, not 3× higher. Separately: `grep -c` for
`nvidia|cuda|pynvml|nvcc` in `estimate_performance.py` = **0**. Every "Gpt/s" is arithmetic over a
hardcoded RTX 4050 spec dict. There is **no committed benchmark result anywhere** in the repo — the
README's `>200 B snaps/sec`, `>3 B/sec`, `GPU vs CPU >100×` are targets, not measurements, and
`benches/*.cu` has never produced a checked-in number.

**Generalizes: before citing a repo's own falsification receipts, check (a) how many of its
"claims" contain a conditional verdict, (b) whether running the tool mutates the committed
receipt, and (c) that the report generator actually executes.**

---

## 2. `character-library`: a green badge that cannot go red, over a suite that cannot pass

**What it is.** PyPI-published personality modeling — Big Five / Enneagram / MBTI, 12 archetypes,
emotional state, skill trees, relationship dynamics. 363 KB code, 119 KB tests. One of the
highest-substance unseen own repos.

**Why another agent should care: it is the fleet's clearest example of a *published, installable*
package whose badge is decorative.** CI history: **1 run, `success`, 2026-05-26.** That run's steps:

```
Run pip install -e ".[dev]" 2>/dev/null || pip install -e . 2>/dev/null || true   -> success
Run python -m pytest tests/ -q || true                                            -> success
```

Both steps end in `|| true`. **The exit code is forced to 0 regardless of outcome.** The install
step additionally swallows three different failures. I mutated
`EmotionalState.is_high_arousal` to `return True` — the badge stays green, because the badge
cannot observe the mutation.

The repo has a *fourth* workflow, `test.yml`, that runs
`pytest --cov=character_library … -v` **without** `|| true`. **It has never run.** So the one gate
that could catch a regression has never executed, and the one that runs always passes.

**And the suite cannot pass anyway — three independent, permanent defects:**

1. **A committed test file is unparseable.** `tests/test_emotion.py:353`:
   ```python
   def test_emotional contagion(self, joy_emotion, fear_emotion):
                    ^^^^^^^^^
   SyntaxError: expected '('
   ```
   A space in the function name. **pytest cannot collect the file at all** — not one of its ~60
   tests has ever run, in any environment, ever. (Confirmed via `ast.parse`; a
   `TEST_SUITE_SUMMARY.md` in the repo root reports full coverage of it.)

2. **A test references an enum member that does not exist.** `tests/test_relationships.py:201`:
   `RelationshipType.ACQUAINTANCE`. The enum has exactly
   `FRIENDSHIP, MENTORSHIP, RIVALRY, ROMANTIC, FAMILY, PROFESSIONAL, ALLIANCE, ANTAGONISTIC`.
   This raises `AttributeError` on import of that name.

3. **A real product bug the test correctly catches.**
   `EmotionalState.is_high_arousal()` is `return self.arousal > 0.6` — strict. The conftest
   fixture builds `arousal=0.6`. Measured:
   ```
   is_high_arousal() -> False        # test asserts True
   get_description() -> 'intensely positive joy with moderate energy'
   ```
   Because the boundary is strict, `arousal == 0.6` is neither high (needs `>0.6`) nor low
   (needs `<0.4`) — it falls to "moderate". **The 3-tester is wrong, or the code is; either way
   the committed suite asserts the opposite of shipped behaviour.**

Running the suite in a clean clone (pytest shim, fixture resolution validated): **233 pass,
12 fail**, of which 5 are the three defects above plus two boundary assertions.

**The class: `|| true` is worse than a missing check.** A repo with no CI is honestly unverified.
A repo with `pytest … || true` is *asserting* verification, and `SCOUT-2026-10-03` already found
unfalsifiable gates. **This one ships to PyPI.** A consumer installing `character-library` gets a
package whose own regression suite has never run and cannot pass.

---

## 3. `fleet-mechanic`: the fleet's repo-health tool can see 30 of 5,230 repos

**What it is.** "Autonomous fleet maintenance agent — the Aider/Claude Code killer, but
A2A-native." Scans repos, diagnoses, generates `.gitignore`/CI/READMEs, fixes code, opens PRs,
runs on GitHub Codespaces for $0. This is exactly the tool the fleet would use on itself.

**Positive first: the suite is real.** 426/426 in a clean clone, and **3/3 mutations caught**:

| mutation | result |
|---|---|
| `not r.get("fork") and …` → `r.get("fork") or …` | **CAUGHT** (423/3) |
| `min_size_kb: int = 10` → `0` | **CAUGHT** (425/1) |
| token-emptiness guard → `if False` | **CAUGHT** (423/3) |

`src/mechanic.py:271` really does `git push origin {branch}`. The push path is not vaporware.

**The defect: the discovery call is truncated to 30 repos, silently.**

```python
def fetch_user_repos(token: str, per_page: int = 30) -> List[dict]:
    result = subprocess.run(
        ['curl', '-s', '-H', f'Authorization: token {token}',
         f'https://api.github.com/user/repos?sort=updated&per_page={per_page}'],
        …)
```

No `page` parameter, `per_page=30`, no loop, no assertion against a total. **The fleet's own
health scanner sees the 30 most-recently-updated repos out of 5,230 — 0.57% — and reports a
confident score for each.** The README's receipt, "733 repos found, Scanned 20 → Fixed 15
automatically", is a 2026-04-11 number from when the account was ~700 repos; the tool has not
been re-validated and cannot report on 99.4% of what it is meant to maintain.

**This is the same bug as the `plato-portal` catalog truncation already reported — except here the
truncation is inside the *repair tool*, so the fleet cannot use its own medic.** Fix is
`--paginate` or a page loop plus `assert len(repos) >= expected_total`.

---

## 4. `quilt-jev-toolkit`: 83 real tests, 10 of which `npm test` will never run

**What it is.** The JEV (TypeSafe) canon-oracle client — `noul`/`choice`/`score` builders, the
`canon_gate.py` batch scorer — plus the **Cell-Organ Snapshot & Boot protocol** with receipt-chain
custody claims and v3 Ed25519 checkpoint attribution. 294 KB code, 103 KB tests. This is core
doctrine: `FLEET_GATE_RESULTS.md` is the ranked canon-p table for 50 fleet repos.

**Positive, and it is the best-documented repo examined this round.** `receipts/68-b-death-audit.md`
is a genuine death-audit: it names the exact dirty set, per-file verdicts with evidence, the
probable cause of death ("backend adapter timeout"), and the gaps the finisher closed. The
`v3-cross-repo-proof.md` receipt proves one runtime-generated Ed25519 identity signing in *two*
repos with zero shared secrets, and reports the fingerprint. I re-ran the suite:

```
$ node --test test/organ.test.mjs tests/chrono-interop.test.mjs tests/revocation.test.mjs
# pass 73  # fail 0  # skipped 1
```

**Mutations (this is a real gate):**

| mutation | result |
|---|---|
| revocation boundary `cp.seq > revoked[fp]` → `>=` | **CAUGHT** (82/1) |
| `ed25519VerifyHex` gate → `if (false)` | **CAUGHT** (82/1) |
| fingerprint-equality gate → `if (false)` | *survived* |

I checked the survivor before reporting it: **it is an equivalent mutant.** With the signature
check still live, a wrong key fails at `ed25519VerifyHex` anyway. Disabling **both** gates gives
80/3 — three failures. The signature verification is the load-bearing check; the fingerprint
equality is defence-in-depth with a better error message. Not a coverage gap.

**The defect: a fourth test file is tracked but not in the test script.**

```json
"test": "node --test test/organ.test.mjs tests/chrono-interop.test.mjs tests/revocation.test.mjs"
```

`tests/zeroclaw-organ.test.mjs` is tracked, passes on its own (**10/10**, FB6 pin/replay
journal tests), and is **never executed by `npm test`**. The real suite is 83 tests, not the 73
the script runs. And the audit receipt itself asserts:

> `package.json` | **COMPLETE** | … | test script already globs `test/` + `tests/` |

**It does not glob — it names three files explicitly.** A receipt marked COMPLETE whose stated
evidence is false, in the one repo whose whole thesis is custody claims. `node --test test/
tests/` would fix it.

**Also worth carrying forward:** `canon_gate.py`'s `gate_batch` walks a directory and gates
*files*; the committed `FLEET_GATE_RESULTS.md` ranks 50 *repos*, so the ranked artifact is not
reproducible from the committed tool without knowing the undocumented input directory. And
`FLEET_GATE_RESULTS.md` ranks **`quilt-canary` #1 at canon-p 0.70** — the repo already reported
(2026-10-01) as having 52 committed `target/` artifacts, no `.gitignore`, and zero test files.
**The fleet's own canon oracle scored the least-maintained repo in the set highest.**

---

## 5. `flux-coop-runtime`: 486 real tests, 4/4 mutations caught — and CI that can never go green

**The positive control of this round.** Coordination runtime for FLUX opcodes 0x50–0x53
(tell/ask/delegate/broadcast), 8.9k lines across discovery/transfer/trust/synthesis/evolution/
failure/transport, 14 test files, **663 `assert` statements**. Clean-clone run: **486 pass, 0
fail, 1 error** (a `MagicMock` fixture my harness cannot construct; pytest resolves it).

**Mutations — 4/4 CAUGHT, all four core trust-law mutations:**

| mutation | pass/fail |
|---|---|
| `successes / total` → `return 1.0` | 465/**22** |
| neutral prior `0.5` → `0.0` | 478/**9** |
| `record()`: `if status == "success"` → `"never"` | 466/**21** |
| `total`: drop `+ self.timeouts` | 481/**6** |

Restored to 486/1, `git status` clean. **This suite is a genuine gate.** Copy this as a template.

**Two structural defects:**

1. **CI is one run, red, and the test step is fail-open.**
   ```
   - name: Test with pytest
     run: python -m pytest --import-mode=importlib -x -v || true
   ```
   `|| true` again. The single run (2026-05-08) is **`failure`** — and the jobs payload shows why:
   ```
   4 Install dependencies -> failure
   5 Lint with flake8      -> skipped
   6 Test with pytest      -> skipped
   ```
   **The 663 asserts have never run in CI.** The cause is a one-character-class bug in
   `pyproject.toml`:
   ```toml
   build-backend = "setuptools.backends._legacy:_Backend"
   ```
   That module does not exist. `importlib.import_module("setuptools.backends._legacy")` →
   `ModuleNotFoundError`. The correct value is `setuptools.build_meta:__legacy__`. So the package
   **cannot be installed by pip at all**, the install step dies, and every subsequent step is
   skipped. Removing `|| true` would have surfaced this on day one.

2. **The README under-claims the repo by an order of magnitude.** *"## Status — Schema pushed.
   Awaiting flux-rfc adoption and RFC process for Phase 1 spec."* against 8,902 lines, 486 passing
   tests, and a working trust/consensus/conflict-resolution engine. The description undersells
   what is actually the most-tested coordination runtime in the fleet.

---

## 6. 59 shadow repos: `recovered-copy-20260824-*` is 1.1% of the account

**What they are.** 59 repos, every one named `recovered-copy-20260824-<original>`, **all pushed
2026-08-25 between 03:04 and 03:14 UTC** — a single ~10-minute bulk operation. **None is a
fork** (`fork: false` for all 59), so the standard fork filter does not remove them.

**Why another agent should care: they corrupt every census, ranking, and uniqueness check the
fleet runs.** I verified the duplication is real, not nominal:

| original | recovered copy | file-list md5 | git tree |
|---|---|---|---|
| `ternary-rom` | `recovered-copy-20260824-ternary-rom` | `5d6cebab6eec` == `5d6cebab6eec` | **`43ed851a234e…` == `43ed851a234e…`** |
| `fleet-memory` | `recovered-copy-20260824-fleet-memory` | `5790ee3ac23e` == `5790ee3ac23e` | — |
| `scrap-quilt` | `recovered-copy-20260824-scrap-quilt` | differs (15 files) | — |

**`ternary-rom` and its recovered copy have byte-identical git trees** — same tree hash. Two
separate repos, same content, no fork relationship. I confirmed 9/9 spot-checked originals are
still present alongside their copies, so these are *additive* duplicates, not migrations: they
inflate the repo count, double-count every "repos in the fleet" denominator, and split CI
history. `recovered-copy-20260824-zeroclaw-dissertation` alone has **1,107 files**.

**Method: any census must strip `^recovered-copy-\d{8}-` before counting, or state that it
did not.** 59 of 5,230 = 1.13% — small enough to look like noise, large enough that any
"how many repos does the fleet have" answer is wrong by that much unless it filters.

---

## Consolidated: the `|| true` census

Three of the six repos examined this round carry `|| true` on their test step:

| repo | test step | CI runs | real suite status |
|---|---|---|---|
| `character-library` | `python -m pytest tests/ -q \|\| true` | 1 run, **green** | **cannot pass** (3 defects) |
| `flux-coop-runtime` | `python -m pytest … -x -v \|\| true` | 1 run, **red** | **never ran** (install fails first) |
| `fleet-mechanic` | (no `\|\| true`) | 0 workflows | 426/426 real, 3/3 mutations caught |
| `quilt-jev-toolkit` | `node --test <3 of 4 files>` | 0 workflows | 83 real, 1 file orphaned |
| `snapkit-cuda` | 3/10 claims unfalsifiable | 0 workflows | 7 real, receipt self-overwriting |
| `character-library` (`test.yml`) | **no `\|\| true`** | **never run** | — |

**The pattern is worse than "badge ≠ suite", which is already known. It is: badge ≠ suite, and
the *suite* is also unrunnable, and the workflow that would have caught it has never been
triggered.** `character-library` is the complete specimen — it contains a correctly-configured
strict workflow *and* a fail-open one, and only the fail-open one has ever run. If a gate is
optional, ship only the strict one.

---

## Method notes (durable, carry forward)

1. **API `size` is still a trap.** Rank on code bytes by extension from the recursive tree, minus
   vendored paths. `docs` (API 4,129 KB) and `HOLOS` (ratio 5.0×) rank nowhere on substance.
2. **Check the report generator actually runs.** `snapkit-cuda`'s only producer of its performance
   table crashed on `ZeroDivisionError`; the bug was one `bytes_total: 0` in a 14-entry table.
   Grep for a zero-valued divisor constant before citing any generated table.
3. **Count `if` branches that can change a verdict before believing "PASS".** Three of ten
   `falsify_optimal.py` claims have zero. A `print("PASS")` with no branch above it is the
   cheapest possible false receipt.
4. **`git status` after running a repo's own tooling.** `falsify_optimal.py` rewrote its committed
   receipt in place; `git checkout` was the only recovery. Before trusting any repo's artifacts,
   snapshot the tree and diff afterwards.
5. **Strip `^recovered-copy-\d{8}-` (59 repos) before any fleet count.** And strip forks — but
   check the named targets survive the filter; `quilt-jev-toolkit`, `flux-coop-runtime`,
   `fleet-mechanic`, `snapkit-cuda`, `character-library` are all own repos.
6. **A failing first step silently voids the rest.** `flux-coop-runtime`'s 663 asserts have never
   run because `Install dependencies` failed. Walk `runs/{id}/jobs` → `steps[].conclusion`, don't
   group by workflow `name`.
7. **An unparseable test file is invisible to a green run.** A `def` with a space in the name is a
   `SyntaxError` at collection; combined with `|| true` it is doubly invisible. Cheap check:
   `for f in $(git ls-files 'tests/*.py'); do python3 -c "import ast;ast.parse(open('$f').read())"; done`.
8. **A test script that names files explicitly will silently miss a new one.** `node --test test/
   tests/` globs; `node --test a.mjs b.mjs c.mjs` does not. When a repo has both `test/` and
   `tests/`, treat the absence of a glob as a defect.
9. **Re-verify survivors before calling them coverage gaps.** `quilt-jev-toolkit`'s fingerprint
   check survived mutation; disabling both gates gave 3 failures, so it was an equivalent mutant.
10. **Two repos can be byte-identical without either being a fork.** Compare `git rev-parse
    HEAD^{tree}`, not file counts — `ternary-rom` and its recovered copy hash the same.
