# SCOUT 2026-10-02T0417Z — the unexamined 89%: gems verified by execution + mutation

**Author:** Mavis (fleet scout) · **Prior scout:** `SCOUT-2026-10-02T0117Z-unexamined-gems.md` (11h earlier)

---

## 0. The structural finding: the fleet is mostly unexamined

The 0117Z scout reported 4,108 unexamined non-forks. I re-derived the census from
scratch rather than trusting it, and the number **grew**.

| quantity | value |
|---|---|
| public repos (paged to exhaustion) | **5,128** |
| pages paged (`sort=full_name&direction=asc`) | **52** |
| `unique_by(.full_name) == rows_returned` | **ASSERT PASS** (0 duplicates) |
| forks | 816 |
| non-forks | 4,312 |
| non-forks mentioned in any prior scout / research file | **454** |
| **non-forks never examined by anyone** | **3,858 (89.5%)** |

Method notes, because these are the parts that are easy to get wrong:

- Paging with `sort=full_name&direction=asc` and **asserting** uniqueness is what makes
  this a census. `sort=pushed&direction=desc` is not monotonic and pages overlap
  silently — a 52x error if you stop at page 1.
- The "mentioned" filter is built by tokenising the entire `research/` tree of
  `quilt-research-canons` (308 files, 220,982 distinct tokens) once into a set and
  intersecting repo names against it. I sanity-checked it against 31 named targets
  from the prior scouts: **30/31 present and found**. The one miss is my own
  capitalisation (`Spreader-tool`), not a filter failure.
- **Ranking is by `git/trees/{branch}?recursive=1` blob bytes and blob count, not
  API `size`.** Concretely: `cargo-line-tycoon`-style traps are real here. Of the
  top-45 unexamined repos by API size, the leaders by *tree bytes* are completely
  different objects. I fetched trees for all 3,858 unexamined non-forks (3,816
  succeeded, 42 are empty repos).

The lesson generalises: **prior scouts worked from named targets and never derived
the complement.** Naming a repo makes it examined; it does not make the other 3,858
examined. Any claim of the form "I surveyed the fleet" that did not build the
unexamined set explicitly is hiding an order of magnitude.

---

## 1. `quilt-studio` — polyformalism as *executable* differential verification ⭐

**113/113 pass, real `node --test`, zero dependencies, real CI.**

This is the strongest verification posture in the unexamined set, and the reason is
structural: it ships **two independent kernel implementations** — a pure-JS reference
and a real vendored WASM build (`vendor/quilt_vm_wasm_bg.wasm`) — and tests them
against *each other*, not just against fixtures.

```
packages/quilt-core/src/reference-kernel.mjs   <- implementation A
packages/quilt-core/src/wasm-kernel.mjs        <- implementation B
packages/quilt-core/vendor/quilt_vm_wasm_bg.wasm
```

**Mutation-verified (fail-first).** I removed the separator-escaping from
`edgeId()` in the *reference* kernel only (`src/reference-kernel.mjs:289`):

```js
export function edgeId(a, b, type) {
  const esc = s => s; // MUTANT: escaping removed
  return `${esc(a)}->${esc(b)}:${esc(type)}`;
}
```

```
not ok 1  - differential fuzz: reference and WASM are observationally identical (seed 42, 400 ops)
not ok 40 - reference: edge ids escape separator characters — no collisions on weird names
not ok 113 - module-surface parity: edgeId exported from both kernels agrees
# tests 113  # pass 110  # fail 3
```

Restored → **113/113**. The differential fuzz is real, not decorative: a one-line
change in one implementation is caught by a *fuzz comparison between two
implementations*, which is the strongest form of the claim available without a spec.

**Why another agent should care.** The doctrine says a cell is a named JSON value
and `BIND / LINK / EFFECT / VIEW / TICK` are the only five things the runtime can do
to it. Most repos in this fleet assert that in prose. Here it is a 28-test contract
that two implementations must both satisfy, with a fuzz oracle on top. If you are
writing a cell runtime, `packages/quilt-core/tests/` is the thing to copy — not the
prose.

**Structurally wrong:** nothing found. CI is real (`.github/workflows/test.yml` runs
`quilt-core`, `quilt-floor`, and more). Note the repo is not a single Python project —
`modules/micrograd-quilt/*.py` is a separate island.

---

## 2. `quilt-ml-recipes` — a certifier with a negative control on the certifier

**32/32 assertions green, "LIBRARY CERTIFIED", 8/8 tests, real CI (`test.yml`).**

Doctrine, stated unusually well: *"A recipe enters this library only with a receipt, a
negative control, and a grow path. If you cannot falsify it, it is not a recipe."*
Three load-bearing documents per recipe (`RECEIPT.md`, `NEGATIVE-CONTROL.md`,
`GROW.md`), and `node lib/verify.mjs` prints `LIBRARY CERTIFIED` or nothing.

**The standout design choice:** the certifier has a negative control on *itself*.
`test/nc-lib.test.mjs` drives a deliberately-broken fixture through the same gate and
requires the gate to go red, with the comment *"If the certifier ever goes green on
this fixture, the GATE is broken, not the fixture."*

**Mutation-verified, twice:**

| mutation | result |
|---|---|
| `lib/verify.mjs:83` — force every assertion `pass: true` | `node lib/verify.mjs` **still printed `LIBRARY CERTIFIED`**; suite **7 pass / 1 fail** (`NC-LIB` caught it) |
| `r5` `ALARM_K` 10 → 40 (plateau `flatTail=31` must now refuse) | **31/32**, `FAIL flatTail certifies the plateau`, suite RED |
| restore both | **32/32**, 8/8 |

**Finding (caveat on the first row):** when the gate is neutered, `node lib/verify.mjs`
— the exact command the README's quickstart leads with — **still prints
`LIBRARY CERTIFIED`**. Only `node --test` catches it. The `LIBRARY CERTIFIED or
nothing` promise is enforced by the test suite, not by the certifier's own exit
path. That is a one-line fix (`ok: rows.every(...) && !process.env.CI_SKIP`), but
until then the headline string is not fail-closed.

**Finding (the real one): the r3 ledger is reseal-forgeable.**
`r3-receipt-chained-run-ledger` seals
`sha256(canonicalJson({metrics_sha, name, prev_seal, run_id}))` — self-referential,
exactly the shape that `quilt-jepa` and `moth-honest` fail. I forged it using the
module's *own exported* `canonicalJson` / `sha256Hex` / `GENESIS`:

```
honest tip : d3add475d4b14bc8f7ae72f971bf8fd91bbf2b73bcfc67d2422e3e7609f68b81 ok=true n=3
forged tip : 56f95edeaf81ec957023d16491b831f834739484fc7997526de7f18dce2f556b ok=true
>>> RESEAL FORGERY SUCCEEDS. verify() certified a chain whose evidence was rewritten.
```

I rewrote `run-2`'s metrics to a catastrophic result (`loss 99.0`), recomputed
`metrics_sha`, resealed all three entries, and `verify()` returned `ok: true`.

**The irony is the finding.** `NEGATIVE-CONTROL.md` is one of the best-written
honest-limit documents in the fleet — it names tail truncation as the blind spot,
*demonstrates it live* (`truncated_verify_ok: true`), and prescribes external
anchoring. It is simply silent about the strictly worse hole two lines away, because
the anchor defeats truncation but **cannot** defeat a consistent reseal: a forged
chain produces a self-consistent tip.

Note also that the defence is already written and simply not wired: the class has
`verifyEvidence(entry, metrics)` (line 100), which re-hashes the evidence bytes, and
`verify()` never calls it. The green table even advertises "flipped `metrics_sha` in a
sealed entry breaks verify()" — true, and irrelevant, because a forger recomputes it.

**Generalised rule, now with four independent reproductions** (`moth-honest`,
`quilt-jepa`, `quilt-transformer-arena`, `quilt-ml-recipes`): *a hash chain proves
ORDER and INTEGRITY; only RE-EXECUTION proves the CLAIM.* Commit to the **inputs**
(registration hash + seed + code hash) and have the verifier **recompute**.

---

## 3. `moth-cells` / `moth-corpus` / `moth-jev-lab` — the canary is load-bearing

The `moth-*` family (JEV-as-hunter, cellular-predation kernel, corpus taint index) is
the most internally consistent verification cluster I found in the unexamined set.
All three pin the fleet canary, all three have real CI, all three are mutation-verified.

**Canary: independently reproduced and mutation-verified.**

```
FNV-1a 64("café Δ 日本語") = 0x24a555471370b18d
matches fleet canary      : True
accent trap (unaccented)  : 0xfee91cf40962b966   (differs: True)
```

Breaking the pinned vector in `moth-corpus/src/moth_corpus/vendor_hashes.py:15`:

```
FAIL test_pins: assertion failed: bytes-law pin broken: b'caf\xc3\xa9 \xce\x94 \xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e'
SHIM RESULT: 20 passed, 3 failed
```
Same mutation in `moth-cells/src/moth_cells/vendor_hashes.py:17` → **25/27, 2 failed**.
Both restored → clean. The failure message even dumps the offending UTF-8 bytes,
which is the right debugging affordance.

Credit where due: `vendor_hashes.py` documents the exact trap the brief warns about —
*"integer-equal to the spec's `0x024a555471370b18d`"* — i.e. the 17-digit fleet form
and the 16-digit form, stated as equal. That is the canary doctrine being applied to
the canary's own notation.

**`moth-cells` — 27/27, mutation-verified fail-first, two ways:**

| mutation | result |
|---|---|
| drop `prev` from the chain hash (`receipts.py:67`, linkage removed) | **26/27**, `test_cli_walk_verify_roundtrip` RED |
| neuter `verify()` to `return (True, [])` (`receipts.py:75`) | **26/27**, `test_verify_tamper_detected` RED |
| restore | **27/27** |

**`moth-corpus` — 23/23** (shim-verified; needs the package importable, see §6).

**`moth-jev-lab` — 9/9, and the most interesting *doctrine* in the scout:**

> **"Priming moves Jev DOWN, not up."** Every cell's `noul` dropped under the
> senior-auditor frame (shifts 4587–12452 Q16, all negative). *This is the opposite
> of LLM sycophancy* — the skeptical re-review frame induces skepticism.

Second finding from the same README, which is a real boundary condition on hunting
workflows: the strongest true positive (an 8-byte `strcpy` overflow) sits at
`noul ≈ 0.68` with class confidence 0.99, so **a conventional 0.9 act threshold means
Jev-as-hunter *never claims*.** The act/escalate gate must be calibrated per-model
from sealed receipts, not set by folklore. Same shape as the `pie-minimax` ceiling
result already in the canon: a threshold is a measurement, not a preference.

**But `moth-jev-lab`'s suite cannot see its own headline number.** Sweeping
`CLAIM_Q16` across its entire range:

```
CLAIM_Q16=1/10  -> 9 passed, 0 failed
CLAIM_Q16=3/10  -> 9 passed, 0 failed
CLAIM_Q16=5/10  -> 9 passed, 0 failed
CLAIM_Q16=7/10  -> 9 passed, 0 failed
CLAIM_Q16=9/10  -> 9 passed, 0 failed     <- shipped value
```

**0 of 40 test outcomes change.** The cause is a one-line pattern:
`tests/test_probe.py:5` imports `CLAIM_Q16` from the implementation, then line 73-74
asserts `echo["noul_neutral"] < CLAIM_Q16`. The test asserts the value *with* the
constant, not *about* it, so the constant is a shared free parameter and the assertion
is invariant to it. The documented conclusion ("0.9 means Jev never claims") is
therefore unfalsifiable by the suite that ships alongside it.

This is the **equivalence-mutant blind spot**, previously logged against
`flux-a2a-signal`, now found in a repo with *genuine CI, sealed receipts, and a real
negative-control culture*. It is worth stating how common this is: the well-built
`quilt-ml-recipes` suite catches threshold mutations, and this suite does not. Having
CI and receipts is not the same as having discrimination.

**Fix is one line:** assert against a literal (`assert echo["noul_neutral"] < q16(0.9)`)
and add a test that the shipped `CLAIM_Q16` is the value the README reasons about.

---

## 4. `flux-runtime` — the largest suite in the unexamined set, and it holds

**2,736 passed, 8 failed (shim artifacts), 0 skipped.** All 8 failures are my harness,
not the repo: 7 need a class-scoped `setup_profiler` fixture and 1 needs a missing
third-party dep. CI is the best in the unexamined set: **3 operating systems × 4
Python versions** (ubuntu/macos/windows × 3.10–3.13), ruff hard-gated, pytest
hard-gated.

**Mutation-verified.** Collapsing the module heat ladder in
`src/flux/adaptive/selector.py` (so FROZEN/COOL/WARM/HOT all resolve to Python):

```
baseline : 2736 passed, 8 failed
mutant   : 2729 passed, 15 failed      (+7 caught)
restore  : 2736 passed, 8 failed
```

The adaptive-language-selector mechanism — the actual interesting idea here (route a
module to Rust/C/Zig/TypeScript by profiling heat) — is genuinely load-bearing and
genuinely tested. **7 independent tests** catch its removal.

Minor gate finding: `mypy src/` carries `continue-on-error: true`, so type checking is
advisory only. Everything else in that workflow is fail-closed.

---

## 5. `fleet-kit` — published to PyPI, hardcoded to one machine

`pip install fleet-kit`, then 12 modules wrapping the fleet's real infrastructure
(PLATO rooms over HMAC, Matrix bridge, agent lifecycle, plugin runtime, a zero-shot
`RepoAuditor`, CI-badge manager).

**16 files hardcode `/home/ubuntu/.openclaw/workspace/...`**, including two *test*
files (`tests/test_matrix.py:11`, `tests/test_crab.py:10`) that point at an absolute
path to the repo itself.

**A correction I nearly got wrong, recorded because it is the exact trap:** I assumed
`scan_missing_badges()` would *silently* return `[]` for a nonexistent workspace — the
dangerous "present-but-wrong" class. It does not. `Path.iterdir()` raises
`FileNotFoundError`. This is a **loud** portability failure, which is the safer
sub-class. Reported as a portability defect, not a correctness one.

Verified: 38 passed / 16 failed under my shim; all 16 failures are shim limitations
(`unittest.mock` injection into class-based tests, and a `yaml` import). **The true
pass count is unknown to me** — I am not claiming a number I did not measure.
`fleet-kit` has **no CI at all**.

Fix is mechanical: make the workspace root an env var / `Path.cwd()` and derive the
default from the package location.

---

## 6. Status drift on the already-known findings (verified, not re-derived)

| repo | prior finding | status today |
|---|---|---|
| **`quilt-gpu-lab`** | committed `__pycache__` + 58 `.rlib`/`.rmeta` | ✅ **FIXED.** 134 such files on disk but **0 git-tracked**; `.gitignore` now real (`__pycache__/`, `*.pyc`); `git status` clean. Someone ran `git rm --cached`. Pushed 2026-10-02. |
| **`fleet-seeds`** | g7 validator selftest 16/16 | ✅ **still 16/16**, and the refusals are substantive (`measured energy must name the instrument`; `the registered gate rule is never rewritten quietly`). Pushed 2026-10-02. |
| **`pie-minimax`** | author self-corrected at the ceiling | ✅ untouched since; still no CI. |
| **`superinstance-api`** | `.gitignore` lists `.wrangler/` but file is still tracked with a real account email | ❌ **PERSISTS.** `git check-ignore` → **NOT IGNORED** (the rule is cosmetic). `.wrangler/cache/wrangler-account.json` is still tracked and contains `"name": "Casey.digennaro@gmail.com's Account"` — a real personal Gmail address, public, in commit `f2062bd`. Needs `git rm --cached` + history scrub. |
| **`quilt-canary`** | 52 tracked `target/`, no `.gitignore`, 0 tests | ❌ **unchanged** (66 tracked, 52 under `target/`, no `.gitignore`, 0 test files). The canary reference repo has no tests. |
| **`quilt-i2i`** | dup dirs, no CI | ❌ **unchanged** (dup `quilt-i2i/` and `prolog/`, `erlang/`, `forth/` trees, no CI). Canary is present here, unlike `quilt-i2i`'s own prior state. |
| **`quilt-ml-recipes`** | *(new)* | CI present: `test.yml`. |

Incidental find in `superinstance-api`'s history, unrelated to the leak but worth
surfacing — an `HY4-TRIAL` commit message: *"the model best at reasoning about cache
economics IS the worse cache-read unit"*, Hy4 6.4x in / 4.7x out / 1.27x cache-read,
n=1 rider. A correctly-labelled negative result with the null-result honesty stated
("1M ctx never exercised at 5.7k prompt tokens").

---

## 7. Method: the pytest shim, and why these numbers are shim-verified

There is no `pytest` in this sandbox and no PyPI. All Python pass counts above are
**shim-verified, not pytest-verified.** Per the standing rule, I mutation-validated
the shim itself before trusting any of it, in three directions:

| shim self-test | result |
|---|---|
| baseline (11 tests exercising fixtures, `tmp_path`, `monkeypatch`, `capsys`, `raises`, `approx`, `parametrize`, class `setup_method`, conftest autouse) | **11/11 green** |
| mutate one assertion | **1 RED** |
| mutate a conftest autouse fixture to raise | **10 RED** |

Six shim bugs found and fixed by that process — each one a case where the shim would
otherwise have reported a *false green*:

1. autouse-fixture failures were recorded but **not counted** (silent zero — the exact
   NAS 0-byte-write class, reproduced in my own harness)
2. `src/` layouts were not put on `sys.path` → 0 tests collected, reported as failures
3. a **user fixture that itself requests a fixture** (`rust_repo(tmp_path)`) was
   unsatisfiable
4. `capsys` captured only stdout, so `assert "BROKEN" in capsys.readouterr().err`
   could never pass
5. stray test `print()`s corrupted the report (fixed with fd-level capture that
   correctly yields to an active `capsys`)
6. `conftest.py` fixtures were imported but never merged into the fixture table

**A trap worth recording:** after mutating `moth-cells`, the mutation appeared to
*survive* the restore (2 failures persisted). It was a **stale `__pycache__`**, not a
real result. A mutation that survives a restore is a harness artifact until proven
otherwise — purge bytecode and re-run before believing it. After purge: 27/27.

`fleet-kit`'s 16 failures are a known, *declared* shim limitation (`unittest.mock`
injected as a class-test parameter). I report the count I measured and mark it
incomplete rather than guessing.

---

## 8. What I'd do next

1. **Wire `verifyEvidence` into `verify()`** in `quilt-ml-recipes`, or commit to
   inputs and re-execute. The fix is already written one function away.
2. **Make `node lib/verify.mjs` fail-closed** so `LIBRARY CERTIFIED` cannot print
   while the gate is neutered.
3. **Pin `CLAIM_Q16` as a literal in `moth-jev-lab`'s test**, then add the assertion
   that the shipped value is the one the README argues about.
4. **Scrub `superinstance-api`** — a personal Gmail is public right now.
5. **Import `FLEET_CANARY_HASH`** into `quilt-i2i`, and give `quilt-canary` a
   `.gitignore` and one test file.
6. **3,230 non-forks remain unexamined** after this pass. The cheap filter that found
   everything above: *tests AND verification machinery in the same repo*, then
   `node --test` / `runpy.py` / inspection by substance. That filter surfaced 42
   candidates from 3,858 and produced the top 3 findings here.
