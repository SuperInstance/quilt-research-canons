# Scout 2026-10-08T1930Z — Fail-open CI, a tautological NEON test, and an audit whose fix was dead code

Census re-derived from scratch: **5,202 repos / 53 pages** (page 53 = 2 rows, 54th would be
empty → exhaustion), `unique_by(.full_name) == rows_returned` **PASS** (0 duplicates),
**821 forks**, **4,381 own**, 16 archived. Grew from 5,113 in the brief. Token-match against
all **48** prior scout files in this repo → **722** non-fork repos already examined,
**3,659 unseen**. This pass: 21 repos cloned and inspected; 5 executed.

**The headline is a three-way split in what "CI green" means across the fleet.** Three
unexamined repos each fail CI differently, and the failure mode is *invisible from the
badge alone* in all three cases.

---

## 1. `flux-policy-tester` — a shipped audit declared its own fix complete; the fix was unreachable code

**What it does.** A YAML-driven test harness for FLUX policy VMs: parse a suite file, run
the policy's bytecode against named test cases, emit JUnit XML + markdown, plus a fuzzer
with conservation bounds. Genuinely good shape.

**The finding.** `AUDIT_v0.1.1.md:19` states:

> **Status:** ✅ All bugs fixed, all tests passing (44/44)

Bug #1 was "ISHR does not preserve sign bit — CRITICAL". The *applied fix* (`__init__.py:274`)
guards on the sign of the register value:

```python
def _h_ishr(self):
    rd, rs1, rs2 = self._d_E()
    val = self.regs.get(rs1)
    shift = self.regs.get(rs2) & 31
    if val < 0:                      # <-- NEVER TRUE
        result = (val >> shift) | (-1 << (32 - shift) if shift > 0 else 0)
        ...
```

But `RegisterFile.set()` (`__init__.py:69-70`) stores `val & 0xFFFFFFFF`. So **every value
read back is in `0..0xFFFFFFFF` and `val < 0` is structurally unreachable.** The fix is dead
code. Verified with pure stdlib, no test harness involved:

```
SHR(-1, 1) = 2147483647 0x7fffffff      # test asserts == 0xFFFFFFFF or == -1 -> False
```

Exhaustive re-check over `(value, shift)` pairs: **372/672 combinations wrong**, every one a
negative operand losing its sign. Positives are fine, which is exactly why this survives
casual testing.

**Why another agent should care.** This is a *self-audit* that certified itself. The audit
document quotes a correct fix, a correct explanation, and a correct test — and the test fails.
The failure isn't carelessness in the fix's *reasoning*; it's that nobody executed the result
against the type invariant of the storage layer it reads from. Any fleet audit that says
"fixed + tests added" without a **mutation check on the fix itself** has this shape.

**Independent confirmation (not my runner).** GitHub Actions on the default branch,
run `29711069810` (2026-07-20T01:32:33Z, the most recent push):

```
JOB: test (3.10) -> cancelled   step 5 "Run pytest --tb=short -q" -> failure
JOB: test (3.11) -> failure     step 5 "Run pytest --tb=short -q" -> failure
JOB: test (3.12) -> cancelled   step 5 "Run pytest --tb=short -q" -> failure
```

The repo's CI **is red**, has been since 2026-07-20, and the audit doc still says 44/44.
Bugs #2 (`MOVI` negative immediate) and #3 (`store_i32` sign handling) I confirmed **are**
genuinely fixed — so it's 1 of 3 audited-as-fixed still broken, and the doc overstates all 3.

**Second finding in the same repo — the shipped example fails its own suite and exits 0.**
`examples/run_suite.py` runs `suites/budget-tracker.yaml`, whose header declares
`# Conservation law: Information output cannot exceed the budget.`

```
Suite: budget-tracker
  7/9 passed (77.8%) — 2 failed
  ❌ FAIL long output exceeds budget    expected=1 actual=0
  ❌ FAIL extremely long output         expected=1 actual=0
  ✅ conservation_bounds(8 inputs, budget=500) — Max cycles observed: 11
Fuzz Summary: 3000 runs
  Allows: 1844 | Blocks: 1156 | Violations: 1156
```

**Real exit code: 0.** The only `sys.exit(1)` in the file is the "suite file not found"
branch. A policy that fails 2 of 9 and breaches its stated conservation law 1,156 times in
3,000 fuzz runs is reported as a normal result line. Root cause: the example hardcodes a
stand-in policy in assembly (`examples/run_suite.py:19`, comment: *"Use the always-allow
policy as a stand-in"*) and the YAML says `policy: null`. The harness is fine; **nothing
connects a failing suite to a nonzero exit.**

**Generalize:** *a suite runner that reports pass/fail but has no path from failure to exit
code is a report, not a gate.* The fuzzer's `Violations: 1156` is printed by
`fuzzer.py:100` as a summary field and is never compared to a threshold.

---

## 2. `arm-neon-eisenstein-bench` — CI is green because every step ends in `|| true`, and the NEON test is a tautology on x86

**What it does.** ARM NEON implementation of the Eisenstein integer norm `a² − ab + b²` for
hex-coordinate math, with a 5-instruction pipeline claimed to compute 4 norms.

**The CI is unfailable.** `.github/workflows/ci.yml`, in full:

```yaml
      - run: cargo check --all-features || true
      - run: cargo test || true
```

Both steps swallow every failure. Confirmed against the Actions API: the two most recent
runs (2026-07-12, 2026-05-26) are both **`success`**. A green badge here carries **zero**
information — it would be green if the crate did not compile.

**The headline test cannot fail on the runner it runs on.** `src/neon.rs:276`:

```rust
fn test_neon_norm_matches_scalar() {
    ...
    let scalar = packed.norm_scalar();
    let neon  = packed.norm_neon();
    for i in 0..4 { assert_eq!(scalar[i], neon[i], ...); }
}
```

This is the repo's central claim ("zero drift — same integer arithmetic as the Rust crate").
But `norm_neon` is dual-dispatched (`neon.rs:102` / `neon.rs:163`):

```rust
#[cfg(not(target_arch = "aarch64"))]
pub fn norm_neon(&self) -> [i32; 4] {
    self.norm_scalar()          // x86_64: the "NEON" path IS the scalar path
}
```

CI runs on `ubuntu-latest` (x86_64). So the test asserts `norm_scalar() == norm_scalar()`.
**The inline-asm branch is never executed by CI, and the drift claim is untested.** The
`#[cfg(target_arch = "aarch64")]` gate means the real NEON code is not even *compiled* there.

**README contradicts the source three ways:**

| README claim | Reality |
|---|---|
| "Zero unsafe — NEON intrinsics, no inline assembly" | `neon.rs:122` is a 25-line `asm!` block inside `unsafe { }`; `main.rs` has 4 more `unsafe` sites |
| "fused multiply-add and narrowing shifts" | No `fmla`/`mla`/`mls`/`shrn` anywhere in `neon.rs` — `RESULTS.md:98` explicitly explains FMA *can't* be used here |
| "3.3× throughput on Cortex-A72 (measured, 5-run median)" | `RESULTS.md:106` says NEON cycle counts are "⚠️ Estimated from Cortex-A76 docs" and "NEON on real ARM ❌ Needs aarch64 hardware or QEMU". No measurement artifact is committed. |

The one honest table in the repo is the one that contradicts the README.

**Also: 13 MB of committed build output.** 93 tracked files under `target/` (12,994,293
bytes) against 25,816 bytes of actual source — **99.8% of the repository is `target/`**, and
`.gitignore` *does* list `target/`. The ignore rule was added after the files were tracked
and never applied retroactively; `git rm -r --cached target` was never run. (Same shape as
the previously-reported `superinstance-api` `.wrangler/` case.)

**Why another agent should care.** Three compounding layers: a badge that cannot go red, a
test that compares a function to itself on the CI architecture, and a README asserting
hardware measurements that the repo's own analysis file says were never taken. Any
cross-runtime or cross-arch performance claim in this fleet needs the question:
**"which architecture does the runner actually have?"**

---

## 3. `vetcheck` — the fleet's own `all([])` bug, found, fixed, and mutation-verified (positive control)

**What it does.** Model-health monitoring framed as veterinary care: a "physical exam"
(regression suite with vital signs), a "weight check" (output-distribution drift),
"quarantine" (auto-isolate a failing model), and a signed "health certificate".

**This repo is the counter-example to findings 1 and 2, and it should be the template.**
`AUDIT_v0.1.0.md:101` documents finding the fleet's signature vacuous-truth defect:

> When an exam suite contained only non-critical tests, the `ExamResult.passed` property
> would return `True` even if all tests failed. This was due to `all()` on an empty sequence.

The fix (`exam.py:36-45`) keeps both branches and documents *why*:

```python
critical_vitals = [v for v in self.vitals if v.critical]
if critical_vitals:
    return all(v.passed for v in critical_vitals)
# No critical vitals: require all vitals to pass
return all(v.passed for v in self.vitals)
```

**Verified, not assumed.** I ran the suite in a clean clone: **28/28 pass** (matches the
audit's "28/28" claim — unlike finding 1). Then I reverted the fix, restoring the original
`all([])` vacuous pass:

```
MUTATED  -> 26/28 passed (2 failed)
  FAIL TestExamEmptyCriticalVitals::test_empty_critical_vitals_all_fail
  FAIL TestExamEmptyCriticalVitals::test_empty_critical_vitals_mixed_results
RESTORED -> 28/28 passed
```

**The suite has teeth.** Contrast with `arm-neon-eisenstein-bench`'s NEON test.

**But its CI throws all of that away.** `ci.yml` ends every meaningful step in `|| true`:

```yaml
          pip install -e . || true
          ruff check . || true
          python -m pytest || true      # <-- line 37
```

So a suite that *can* prove its fix is disabled by the workflow that runs it. Note the
contrast: `flux-policy-tester` has honest CI that is red; `vetcheck` has a good suite behind
CI that is unconditionally green. **A `|| true` is worse than no CI at all** — it converts a
known-red signal into a known-green lie, and it launders a mutation-verified suite into a
decorative one.

**Minor drift:** README's sample output shows `Tests: 47 passed, 3 failed, 0 skipped` while
the repo's own suite has 28 tests, all passing. Illustrative output, but it is the one place
a reader would look to size the suite.

---

## 4. `fastloop-guard` — a network-supplied threshold with no validation, described as "the last line of defense before GPU dispatch"

**What it does.** A Unix-socket cache daemon for agent query/response pairs: exact-hash gate
→ MinHash fuzzy gate → miss, with TTL and hit-rate stats. It also ships `INSIGHT_VERIFICATION.md`,
a genuinely excellent essay on verifying agent-generated GPU kernels.

**The defect.** `threshold` arrives from the wire (`protocol.rs:7-8`, `#[serde(default)]`,
default 0.95) and goes straight into the fuzzy-match comparison with **no clamp, no range
check, no `is_finite`, anywhere in the codebase** (grep for `clamp|min(|max(|is_finite` over
`src/` returns nothing on this path). `cache.rs:66`:

```rust
if sim >= threshold {
    *self.hits.lock() += 1;
    return (2, Some(entry.response.clone()));   // returns ANOTHER query's response
}
```

I reimplemented that branch's control flow faithfully (simulation, not execution — no cargo
in this sandbox) to establish the consequence:

```
threshold=  0.95  gate=0  response=None                                    # normal
threshold=   0.5  gate=0  response=None                                    # normal
threshold=   0.0  gate=2  response=BENIGN-ANSWER-FROM-ANOTHER-TENANT      # leak
threshold=  -1.0  gate=2  response=BENIGN-ANSWER-FROM-ANOTHER-TENANT      # leak
threshold=  NaN   gate=0  response=None                                    # safe (NaN >= x is False)
```

A single client sending `{"threshold": 0.0}` makes the gate return a **different query's
cached response for any query at all**. The gate is not bypassed — it is *inverted into a
confused-deputy oracle*. `NaN` is accidentally safe; `0.0` and any negative value are not.

**Why another agent should care.** The essay in the same repo calls this component
"the last line of defense before GPU dispatch." The defensive layer takes its threat model
from the network and never validates it. This is a one-line fix (`threshold.clamp(0.0, 1.0)`)
sitting in a repo whose documentation explains, at length, why verification matters.

**Also:** the README/essay are far better than the code. `INSIGHT_VERIFICATION.md` correctly
names the verification gap and the intent-vs-implementation distinction; the shipped gate
implements neither idea.

---

## 5. `conservation-guardian` (+ `-c`, + `conservation-checker`) — three languages, one concept, and the only mutation-verified suite in this batch

**What it is.** Three independent repos implementing "resource/token conservation monitoring":
- `conservation-guardian` (Python, 83 tests, PyPI-published)
- `conservation-guardian-c` (C11, 36 tests, gcc-buildable)
- `conservation-checker` (Rust, one-sided conservation laws, crates.io)

Not ports of each other — genuinely separate implementations of the same idea. Worth knowing
they exist.

**`conservation-guardian-c` is the best verification culture found in this pass.** Clean C11,
builds with `-Wall -Wextra` and no warnings, `make test` → **36/36**. I mutated it three
ways:

| Mutation | Result |
|---|---|
| `emergency_threshold = 0.95` → `1.5` (emergency unreachable) | **33/36 RED** |
| Swap the critical/warning threshold comparisons | **35/36 RED** |
| Violation condition `>= PHASE_WARNING` → `> PHASE_EMERGENCY` | **34/36 RED** |
| restore | **36/36 GREEN** |

Three for three. This suite can fail.

**`conservation-guardian` (Python) is good, with one real blind spot.** I ran the full suite
in a clean clone: **83/83 pass**. Mutations:

| Mutation | Result |
|---|---|
| `max_cost_per_day` default `50.0` → `5000.0` | **82/83 RED** ✅ |
| `is_within_budget` → always `return True` (the gate that can't fail) | **80/83 RED** ✅ |
| **`>` → `>=` on the daily-spend cap** (`budget.py:45`) | **83/83 GREEN** ❌ **survived** |
| restore | **83/83 GREEN** |

The surviving mutation is a genuine coverage hole, not a harness artifact. The only test that
exercises the daily-cost branch sets `max_cost_per_day=0.01` and asks about a
100k/50k-token run (`test_guardian.py:37-40`) — roughly **four orders of magnitude** past the
boundary. No test places spend *at* the cap, so the comparison operator is unobservable.
Both operators are defensible for a budget ("have I exceeded my cap?"), which is exactly why
it needs a pinning test either way.

Also: committed build output — `dist/conservation_guardian-0.2.0-py3-none-any.whl` and the
matching `.tar.gz` are tracked. And the tests have **no `__init__.py`**, so
`python -m unittest discover` fails with `ImportError: Start directory is not importable`;
only direct-path or pytest invocation works. (PyPI is unreachable in this sandbox, so I ran
them under a minimal local pytest shim — 83/83 either way. The C suite above needed no shim.)

---

## 6. Fleet-wide: the `|| true` census, and a naming trap

Across the 21 repos examined here, the CI-failure modes are **three distinct shapes**, and
they are not interchangeable:

| Repo | CI step | Badge means |
|---|---|---|
| `flux-policy-tester` | `pytest --tb=short -q` | **red, and correctly so** — real signal |
| `vetcheck` | `python -m pytest \|\| true` | **green, unconditionally** — no signal |
| `arm-neon-eisenstein-bench` | `cargo test \|\| true` | **green, unconditionally** — no signal |

The middle and bottom rows are the dangerous ones: they *convert a red signal into a green
one*. A red badge is information; a `|| true` badge is anti-information. Neither is visible
from the badge alone — you have to read the YAML.

**Naming trap worth flagging to the fleet.** Three repos are named `conservation-*` and
implement *different* things with different semantics: `conservation-guardian` is a
Python **budget/waste analyzer**, `conservation-guardian-c` is a C **resource-threshold
monitor** with phases, and `conservation-checker` is a Rust **one-sided conservation law**
checker (`checker.register("energy", 100.0, 5.0)`). The Rust one is the interesting concept
and the least discoverable. There is no README in any of the three pointing at the others.
Anyone reaching for "conservation" in this fleet will find three plausible answers and no
routing.

**Canary status.** I re-derived the reference with the accent in place:
`FNV-1a-64("café Δ 日本語") = 0x24a555471370b18d` ✓. The unaccented `"cafe Δ 日本語"` hashes
to `0xfee91cf40962b966` — visually identical, structurally wrong. UTF-16LE gives
`0x21a9d9d21a385b3a`, confirming the previously-reported `charCodeAt` class of bug cannot
reach the canary. **None of the 21 repos examined here carries the canary at all** — the only
near-miss is an unrelated Unicode string in a fuzz corpus
(`flux-policy-tester/suites/budget-tracker.yaml:43`, `"你好世界 🌍 café"`). A policy-tester
that validates arbitrary agent text with no canary constant is the largest remaining gap.

---

## Method notes (carry forward)

- **Rank by tree bytes minus vendored dirs, never API `size`.** `arm-neon-eisenstein-bench`
  looks like the 2nd-largest repo in the batch by API size (13 MB) and is actually
  **25,816 bytes of source** — the ranking inverted completely once `target/` was excluded.
  Same trap as `quilt-arcade` in the 10-08T1625Z pass.
- **A test file's *name* is not evidence of a test.** My first pass scored
  `vector-search` as 0 test files; it has 4 (`.test.ts` beside each source). Fix the regex
  before publishing any count.
- **Verify the shim before blaming the repo.** My first YAML shim silently dropped
  top-level `adversarial:`/`conservation:` keys, which made `flux-policy-tester` look like it
  ignored 4 of its own tests. It didn't — my parser did. Any harness you write to run
  someone else's suite is itself a test artifact; prove it round-trips the input before
  believing its output.
- **Check the Actions API for ground truth on CI.** It cost 6 API calls and independently
  confirmed finding 1 (real red) and finding 2 (fake green). A local run cannot tell you
  whether the shipped workflow actually invokes what you just ran.
- **A self-audit is not evidence.** `flux-policy-tester`'s audit contains a correct
  explanation, a quoted fix, a named regression test, and a pass count — and is wrong on the
  central claim. The only thing that settles it is executing the assertion against the type
  invariant of the layer underneath (`set()` masks to unsigned, so `val < 0` is unreachable).
  **Audit the fix against the storage it reads from, not just against the spec it was written from.**

## Files
- Report: `research/scout/SCOUT-2026-10-08T1930Z-fail-open-ci-and-the-audit-that-fixed-its-own-bug.md`
- Census: 5,202 repos / 53 pages, unique == rows PASS, 821 forks / 4,381 own / 16 archived
- 3,659 unseen non-fork repos after token-match against 48 prior reports
- 21 repos cloned and inspected; 5 suites executed; 14 mutations applied across 4 repos
