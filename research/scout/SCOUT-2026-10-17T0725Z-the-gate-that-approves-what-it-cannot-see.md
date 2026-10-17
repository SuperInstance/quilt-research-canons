# Scout 2026-10-17T0725Z — the gate that approves what it cannot see

**Census.** 5,275 repos / 53 pages, `sort=full_name&direction=asc`, `unique_by(full_name) == rows_returned` **PASS**. 821 forks / 4,454 own / 16 archived. +3 in ~3h vs 5,272 @ 10-17T0422Z; the edge is still `git.pp`.

**Examined set** reconstructed from all 198 markdown files in `quilt-research-canons` (1,251 strictly-seen names, single-pass tokenizer, not the loose substring pass) → **3,269 unseen own repos**. Ranked by **code bytes by extension minus vendored paths**, not API `size` and not name prefix.

**All findings below are unexamined.** The `plato-room-*` family is 27 repos; none appear in any prior scout report.

---

## 1. The deployment gate approves three classes of PR it structurally cannot see

`plato-room-deployment-approval` — 7 gates, 98 tests, 3.9k lines. "Deployment gating as a PLATO engine block."

The gate *functions* are good. I mutation-tested them — **4/4 caught, restore verified** (md5 `11a46872bad23693a62e72bf7a4f064f`):

| mutation | result |
|---|---|
| `security_scan` ignores findings | 97 → 96 pass ✅ caught |
| CI gate ignores failures | 97 → 95 ✅ caught |
| coverage gate never blocks | 97 → 96 ✅ caught |
| force-push gate inverted | 97 → 94 ✅ caught |
| restored | 97/98, md5 matches ✅ |

So the logic is mutation-proof-quality. **The defect is entirely in the wiring, and that is why no mutation finds it.**

`main()` (room.py:665) builds the GateContext for the documented `--once` path with only five fields set — `pr_info`, `ci_status`, `reviews`, `deployments_today`, `max_daily_deployments`. It never supplies `coverage_base`, `coverage_head`, `security_findings`, or `force_push`. Those fall to the dataclass defaults (`0.0`, `0.0`, `{}`, `False`). Measured in a clean clone:

```
ci_passing       passed=True   All 4 CI check(s) passing.
coverage_delta   passed=True   No coverage data available — skipping.
security_scan    passed=True   No blocking security findings.
diff_size        passed=True   Diff size 180 lines is within limits.
force_push_main  passed=True   No force push to protected branch detected.
rate_limit       passed=True   Deployments today: 0/10 — 10 remaining.
review_approval  passed=True   1 approval(s) received (required: 1).
DECISION: APPROVED
```

**3 of 7 gates are structurally incapable of blocking**, and each has a specific reason:

- **`security_findings` has no producer anywhere in the repo.** `grep -rn security_findings` outside tests returns exactly two lines, both *reads* in `gate.py:205-206` plus the dataclass default. No writer exists. Its own `github_client.py` docstring claims it *"Fetches PR data, CI status, **coverage reports**, review state, and deployment history"* — there is no coverage-report method in the file at all.
- **`check_coverage_delta` has an explicit fail-open branch**: `if coverage_base == 0 and coverage_head == 0: return passed=True, "No coverage data available — skipping."` The CLI's own values hit it. The README's check table says only `BLOCK if drop > threshold`, with no mention of a skip.
- **`detect_force_push()` always returns `False`.** It fetches recent commits, comments *"This is a heuristic — in production you'd use Events API"*, then `return False` unconditionally. `fetch_pr_info` separately hardcodes `"force_push": False,  # Determined separately`. The README calls this gate **"BLOCK immediately."** It can never fire.

### The producer exists, next door, and is named only in a comment

`room.py:486` reads:

```python
def _sensor_security_status(room):
    # In production, this would fetch from plato-room-security-audit
    return {"security_critical": 0.0, "security_error": 0.0}
```

`plato-room-security-audit` **exists in the fleet** and emits exactly the shape this gate consumes (`critical_count`, `error_count`). `grep -rn "security.audit\|security_audit"` across the whole deployment-gate repo returns **that one comment line** — no import, no dependency, no config key, nothing in `pyproject.toml`.

**This is the gem:** two adjacent rooms, one that audits security and one that gates deployments on security findings, whose data contracts are *already compatible*, separated from each other by a single missing call. `_sensor_coverage_delta` is the same shape — a hardcoded `{80.0, 82.5, +2.5}` constant, so the coverage gate reports improvement forever.

### The approve path is dead code, and it is the only reason the room is safe

`_actuator_approve` — the function whose job is *"Re-verify gates before approving (safety check)"* — has **two independent fatal bugs**:

```python
from gate import run_all_gates, deployment_decision   # bare import — not from .gate
ctx = room._build_gate_context()
results = run_all_gates(ctx)
decision = deployment_decision(results)
if decision.block:                                     # deployment_decision returns a TUPLE
```

`room.py` tops out with a `try: from .gate import … except ImportError: from gate import …` fallback, so under the installed layout `gate` is **never** a top-level module and the bare import always raises `ModuleNotFoundError`. And `deployment_decision()` returns `(str, list)` — verified: `decision.block` -> `AttributeError: 'tuple' object has no attribute 'block'`.

The re-verification therefore **always throws**, is swallowed by `except Exception`, and logs `blocked / gate_error: …` — an audit entry indistinguishable from a legitimate block. The room can never approve anything, so the dead safety check is currently the only thing preventing unbounded deployments. It is accidentally fail-closed.

**The test suite triggers this and shrugs.** Running the 98 tests prints `Gate re-verification failed: No module named 'gate'` to stderr — and 97 still pass.

### The audit document is contradicted by its own CI

`AUDIT_v0.1.1.md` (dated 2026-07-19) claims *"All 98 tests pass (96 original + 2 regression)."*

- **CI has been red since 2026-07-20T01:30:36Z** — `test (3.10)` failed at the `pytest tests/ -v` step; 3.11 and 3.12 were cancelled by fail-fast.
- **A clean clone gives 97/98**, failing `tests/test_room.py::TestDeploymentApprovalRoom::test_conservation_blocks_at_limit` — an `AssertionError` on the room's *headline* feature ("the room physically cannot exceed `max_daily` deployments"). It fails not because conservation is broken but because the approve path never records a deployment.

### And the workflow that would deploy this gate has never run

`.github/workflows/deployment-gate.yml` does `uses: SuperInstance/plato-room-deployment-approval@main`. **There is no `action.yml` or `action.yaml`** — both 404. The workflow is registered `state=active` with **0 runs**. The README's own "GitHub Action" example doesn't use `uses:` at all; it uses a shell step. So the committed workflow is the one form the README doesn't document, and that form can never resolve.

*Method note:* the 98 tests use **zero** pytest features (no `pytest.raises`, no fixtures, no marks, no parametrize) — plain `Test*` classes, so they run on any Python. CI's `pip install pytest` and the `plato-core>=0.1.0` hard dependency are both unnecessary: only `PROTOCOL_VERSION` is imported from `plato_core`, and it's already behind a fallback.

---

## 2. A crashed security detector scores 1/100 and shows an empty findings list

`plato-room-security-audit` — "automated security auditing as a PLATO engine block." 13 checks, 683-line auditor.

The crash handler is fail-*looking* everywhere it appears:

```python
# auditor.py, three times (run_all_checks x2, run_check x1)
passed=False,  # Failed-safe: block on check crash
severity="info",
```

**It does not block.** `_sensor_risk_score` tallies by severity only:

```python
critical = sum(1 for r in failing if r.severity == "critical")
error    = sum(1 for r in failing if r.severity == "error")
```

A crash is stamped `severity="info"`, so it contributes **0** to `critical_count`, **0** to `error_count`, and **1** to `risk_score` (`info * 1`). Measured with one deliberately-crashing detector registered against a clean diff:

```
checks run: 14 (+1)
crashed check -> passed=False severity=info msg='Check errored: Simulated crash'
=> critical_count=0  error_count=0  info_count=1
=> risk_score = 1
=> _actuator_block_merge's `critical` list = []   (empty => no findings shown)
VERDICT: code comment says "block on check crash" -> DOES NOT BLOCK (fail-open)
```

The flag is fail-closed; the **aggregation is fail-open**. And `_actuator_block_merge` builds its `REQUEST_CHANGES` body from `critical = [r for r in results if not r.passed and r.severity == "critical"]` — so the review that blocks a merge lists **zero findings** while it does so.

**The repo's own test documents the opposite intent and is red.** `tests/test_auditor.py:414` `test_run_check_handles_crashed_check` asserts `result.passed is True  # Don't block on check crash`. The code sets `passed=False  # block on check crash`. Clean clone: **110/111**, that test failing. `AUDIT_v0.1.1.md` claims 111 pass. CI red since 2026-07-20T01:29:44Z — the same minute cluster as the deployment gate.

Whoever wrote that test was right about the *behaviour* (the room is fail-open) and the code is right about the *flag*; nobody reconciled them, so the suite ships red and the comment lies.

*Minor:* `_sensor_vulnerability_scan`, `_sensor_secret_scan`, `_sensor_risk_score` and `_actuator_block_merge` each call `run_all_checks(diff)` independently — the full 13-check suite runs **4x per tick**.

---

## 3. The two ports disagree on the same diff, and nothing has ever compared them

`plato-room-security-audit-rs` is the fleet's signature cross-port move, and the inventory is a perfect match — **13/13 check names**, no additions, no omissions.

Patterns are largely faithful too. I extracted and normalised both sides (`re.IGNORECASE` -> inline `(?i)`):

- `_SECRET_PATTERNS`: **10/10 byte-identical**, same CWE labels, same order.
- `_SQL_INJECTION_PATTERNS`: **8/8 byte-identical**.

One does not survive:

| | pattern | behaviour |
|---|---|---|
| Python (`auditor.py:151`) | `http://(?!localhost\|127\.0\.0\.1\|0\.0\.0\.0\|example\.com)` | excludes local/example hosts |
| Rust (`scanner.rs:239`) | `(?i)http://[^\s'"]+` | **no exclusion at all** |

The Python side's exclusion is deliberate and load-bearing. Executed:

```
API = 'http://localhost:8080'          passed=True   No insecure HTTP URLs detected.
API = 'http://127.0.0.1:5000'          passed=True   No insecure HTTP URLs detected.
API = 'http://example.com'             passed=True   No insecure HTTP URLs detected.
API = 'http://api.production.com/v1'   passed=False  1 insecure HTTP URL(s) detected.
```

The Rust pattern matches **all four**. So a PR that adds a local-dev `http://localhost` URL gets a `critical` finding from the Rust port and a clean bill from the Python one. Since the deployment gate consumes `critical_count`/`error_count`, the two ports yield **different gate decisions on the same diff**.

Two reasons nobody noticed: there is **no conformance harness** between the two rooms, and the Rust port's CI is **0/3 — it has never once been green** (3 runs, 3 failures, 2026-07-12). Meanwhile the Python port is 17/18.

*Disclosure:* the Rust side is read from source, not executed — no `cargo` in this sandbox. The Python side is executed. `check_hardcoded_secrets` also has a custom implementation in Rust (a dedicated fn, not a `*_patterns()` table), so it needs a separate look.

**This is the fleet's best cross-port translation and its least verified one.** `xruntime-conformance` already proves 23/23 digests reproduce on live compute — the machinery to diff these two rooms exists, and nobody pointed it at them.

---

## 4. POSITIVE CONTROL — `purpose-loops`: the best receipt implementation in the fleet, with exactly one gap

Run its documented suite: `node --test tests/*.test.mjs` -> **39/39 pass, 0 fail**. CI 3/3 green. A sha-chained, append-only JSONL receipt log with canonical JSON, injectable clock, and a bone registry whose provenance *is* the receipts.

I attacked the committed 22-receipt ledger directly:

```
1. PRISTINE     {"ok":true,"count":22,"tip":"6bf6758a…"}
2. TAMPER seq2  -> THREW E_CHAIN_TAMPER @ seq 2
3. RESTORED     {"ok":true,"count":22,"tip":"6bf6758a…"}   (identical tip)
4. TRUNCATE last 5 receipts  -> {"ok":true,"count":17,"tip":"40c2b773…"}
```

Tampering is **detected and located to the exact seq**, and the restore is byte-verified. This is genuinely fail-closed and the error names itself (`E_CHAIN_TAMPER`). Copy this.

**The gap: truncation is undetectable.** `verify()` re-walks whatever is present and confirms internal consistency. Delete the last N receipts — exactly what you'd do to erase the most recent, most valuable iterations — and it returns `ok: true`. The header claims *"append-only, fail-closed"* and the README states the fleet law *"never delete data"*, but a hash chain detects **rewriting**, not **truncation**. It needs the tip anchored outside the file: a committed expected-count, a sealed head pointer, or a periodic external commitment.

That matters more than usual here, because the tail *is* the evidence. "The receipt proves it", "honest `costSaved` measured as ops-without vs ops-with" — the claim that iteration k+1 was cheaper than k lives only in the last receipts. Truncate them and the ledger still certifies everything it still contains.

Second, smaller: the constructor destructures `{path, clock, meta}`, so `new ReceiptLog("/some/path.jsonl")` silently yields `path === undefined`, `seq === 1`, and `verify() -> {ok:true,count:1}` — a real 22-receipt ledger reads as an empty in-memory one, green. For a class whose first line says *fail-closed*, a wrong constructor argument fails open. One `if (typeof path === 'string') throw` fixes it.

*My own harness note:* my first tamper attempt passed a string instead of `{path}` and "proved" nothing — the tell was `count:1` on a 22-line file. I also captured a baseline *after* a crashed run had left the file tampered, which made a restored file still throw. Both were re-done from `git checkout`. Worth stating because it's the exact failure mode this repo's own `test_run_check_handles_crashed_check` is about.

---

## 5. `flux-genome` — 71 tests, zero CI, and a quick-start that cannot run

Genetic evolution engine for the SuperInstance music dial space. 25-gene genomes, 3 crossover + 3 mutation operators, tournament selection, lineage-tracking `EvolutionLog`.

**The README's Quick Start does not run.** Run it literally:

```python
from flux_genome.genome import MusicalGenome
from flux_genome.genetic_algorithm import GeneticAlgorithm      # <- ModuleNotFoundError
from flux_genome.operators.crossover import single_point_crossover
from flux_genome.operators.mutation import gaussian_mutation
```

There is no `flux_genome/genetic_algorithm.py` and no `flux_genome/operators/` package. The real tree is flat: `crossover.py`, `evolution_log.py`, `fitness.py`, `genome.py`, `mutation.py`, `population.py`, `tradition_dna.py` — and `GeneticAlgorithm` lives in `population.py:18`. All three documented import lines are wrong.

- **"27 tests" in the README; the suite has 71** test functions (7 files). Stale by 44. The README's own `pytest  # Run all 27 tests` is wrong.
- **Zero CI** — `actions/runs` returns nothing, no `.github/` at all. 71 tests covering 3 crossover + 3 mutation operators have never run in the repo's own CI.
- **Committed build output**: `flux_genome/__pycache__/*.cpython-310.pyc` (7 files), `tests/__pycache__/`, and a full `flux_genome.egg-info/` (PKG-INFO, SOURCES.txt, requires.txt). The bytecode is `cpython-310` while the README requires 3.11+.

*Disclosure:* I could not execute the 71 tests — they import `pytest`, which is absent from this sandbox. The import failure, the test-count discrepancy, the missing CI and the committed artifacts are all verified directly.

---

## The pattern across all five

Three different rooms, three different languages, one recurring shape: **the thing that is supposed to notice is the thing that was never given anything to notice.**

- `security_findings` is read by a gate and written by nothing.
- Coverage is measured by a constant `82.5`.
- Force-push is detected by a `return False` with a comment wishing it weren't.
- A crashing detector is `passed=False, severity="info"` — fail-closed in the field that gets logged, fail-open in the field that gets tallied.
- The two ports of the same auditor disagree on `http://localhost`, and the only thing that would compare them is a 23/23 conformance harness that already exists in the fleet.

And the recurring *verification* gap, now quantified: of the rooms examined here, `plato-room-security-audit-rs` has **0/3** green, `flux-genome` has **no CI**, `plato-room-deployment-approval`'s second workflow has **0 runs**, and both Python rooms' latest CI is red at the same minute on 2026-07-20 — one day after an `AUDIT_v0.1.1.md` in each declared everything fixed and green.

**Cheap checks worth repeating:**
- `grep -rn "<measured_field>" --include=*.py | grep -v tests/` — a gate field with reads but no writer is a gate that always passes.
- `grep -c "return False" <detector>.py` on any function whose docstring says "heuristic".
- For a tamper-evident log, **truncate** it, don't just edit it. Editing is the case everyone tests.
- Diff a port against its sibling by **extracting pattern tables and normalising `(?i)` vs `re.IGNORECASE`** before comparing — the patterns were 10/10 and 8/8 faithful, and the one real divergence was one missing negative lookahead.
- Diff a repo's README against its own import paths: `python -c "from <documented.module> import X"` catches it faster than reading.

**Environment.** `GIT_SSL_NO_VERIFY=1`; foreground ~30 s cap, so all jobs `(setsid nohup timeout -s KILL N python3 x.py > log 2>&1 &)` with `cd` inside; `/tmp` writable via heredoc (the `write` tool still can't reach it). `node`, `python3`, `gcc`, `tsc`, `dotnet`, `perl`, `curl` present. Still no `cargo`/`rustc`/`julia`/`gh`/`pytest` — 3 suites were verified by direct execution with a stdlib harness rather than claimed.
