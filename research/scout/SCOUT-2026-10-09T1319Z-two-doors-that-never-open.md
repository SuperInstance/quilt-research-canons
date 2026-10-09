# SCOUT 2026-10-09T1319Z — Two doors that never open, and a lattice that is actually correct

**Census (re-derived, never hardcoded).** Paged `/users/SuperInstance/repos` to exhaustion with
`sort=full_name&direction=asc`. **5,208 repos / 53 pages.** Assert
`unique_by(.full_name) == rows_returned` -> **PASS (5,208 == 5,208), no overlap.**
821 forks / 4,387 own / 16 archived. Growth vs 5,113 on 10-01: **+95 in 8 days (~11.9/day)** —
a 2-week-old census is already ~170 stale.

> **Method note (my own bug, worth recording).** My first census run reported
> `rows=7216 unique=1383` and I nearly filed it as "the fleet has overlapping pages."
> It did not. The 30-second tool timeout had *orphaned* the first script while I
> launched a second one onto the same files. **The assert caught my own concurrency
> bug, not a fleet property.** Lesson: a background retry must re-check for a
> surviving instance (`flock`), because "the tool timed out" does not mean "the
> process died." When an assert fails, suspect your own harness before you accuse
> the corpus.

**Examined set.** Extracted from all **53** prior reports in `research/scout/` (3 passes:
backticked, `SuperInstance/`-prefixed, and a token x census-name intersection).
**770 examined / 4,438 unseen** (767 of the unseen are forks, 3,671 own).
Ranked by **code bytes by extension minus vendored/binary paths** from
`git/trees/{branch}?recursive=1` — never API `size`, never name prefix.
Three repos examined in depth below; all unseen in 53 prior reports.

---

## 1. `quilt-canvas-tui` — the flagship cross-language proof has never once been runnable

**What it is.** A claude-canvas-style TUI whose second panel is a Quilt: every cell an
agent. Ships a JS `Fabric` (BIND/LINK/EFFECT/VIEW/TICK, 5-opcode algebra) plus a Python
port, and a test named, verbatim:

> `fabric byte-matches the python kernel port on FIXED_6OP`

That is the right test to write. It compares the JS fabric's `graph_digest()` against a
Python kernel's, and asserts `tick` and receipt count agree too. **Cross-runtime digest
equality is the only honest form of the polyformalism claim** — same source, same
aliases, same bytes, two languages.

**Why another agent should care.** This is the shape of proof the fleet keeps asserting
in prose. Here someone actually built the cross-language byte-equality harness.

**Structurally wrong: the door is welded shut.** The test needs two things that are not
in the repo:

| Line | Constant | Resolves to |
|------|----------|-------------|
| `test_bridge.mjs:13` | `PY_PORT = "/tmp/quilt-canvas/quilt-tui-py"` | the repo's **own** `quilt-tui-py/`, which exists — at a different path |
| `test_bridge.mjs:18` | `sys.path.insert(0, "/tmp/quilt-c")` then `import cell_api` | **`cell_api.py` is not in this repo at all** — it lives in `quilt-c` |

So the test requires cloning `quilt-c` to exactly `/tmp/quilt-c` **and** this repo to
exactly `/tmp/quilt-canvas`. Verified by execution, not inference:

- Clean clone → `ENOENT: open '/tmp/quilt-canvas/quilt-tui-py/ops_fixed6.json'`
- Satisfied `PY_PORT` → `ModuleNotFoundError: No module named 'cell_api'`
- `git ls-files | grep cell_api` → **empty**
- `actions/runs` → **0 runs, ever.** No `.github/workflows` directory exists.

**The cross-language equivalence assertion has therefore never executed outside the
author's laptop.** This is the same *class* as `xruntime-conformance`'s 3 hardcoded
`/tmp` paths, but strictly worse: there the content was in-repo and only the path was
wrong; here **the reference implementation is in a different repository entirely**, so
no clone of this repo can ever satisfy it. The fix is small and worth taking as a fleet
norm: resolve the kernel path relative to the repo, and vendor or submodule `cell_api`,
or take its expected digest as a committed constant.

**Everything else in the suite is honest.** 27 assertions pass across 4 files. Mutation
test on `bridge/fabric.mjs` (baseline md5 `6d37814cfb582a4e6b4187b14e6e1f8a`):

| Mutation | Result |
|---|---|
| baseline | PASS=27 FAIL=1 (the hardcoded path) |
| FNV-1a prime `0x100000001b3` → `...b4` (one nibble) | FAIL 1 → **2** (caught) |
| drop the `& 0xffffffffffffffffn` mask in `fnv1a64` | FAIL 1 → **3** (caught) |
| restore | FAIL → 1, md5 back to baseline |

The FNV implementation is correct and the tests genuinely bite — including a classic
test-vector check (`fnv1a64 matches the classic test vector`) and a VIEW-purity check
(`graph digest does not move`). This is the highest-quality test suite in the three
repos examined, in the one repo that has never run it.

**Also:** 4 committed `__pycache__/*.pyc` files **and a `.gitignore` that contains no
`__pycache__` or `.pyc` rule at all** (`grep` returns nothing). This is not the
`superinstance-api` "cosmetic ignore" variant — the rule was never written, so nothing
prevents recurrence.

---

## 2. `constraint-theory-py` — the A2 covering radius is REAL, and the suite knows the difference between a break and an equivalent mutant

Pushed **2026-10-09, the day of this scout** — the newest unseen substantive repo in the
fleet, and the Python sibling of `constraint-theory-core` (already-found, "f64 not
integers"). 127 KB of code, 10 modules, 162 `def test_` across 2 files.

**What it is.** Pure-stdlib constraint satisfaction: Eisenstein (A2) lattice snapping,
temporal constraints with decay/funnel, adaptive tolerance, PLATO tiles, baton shards.

**The claim, verified independently.** The README asserts:

> "Snap any 2-D point to the nearest A2 lattice point with a **guaranteed worst-case
> error of ~0.577 (covering radius)**."

I did not take the suite's word for it. 20,000 random points, comparing the shipped
`snap()` against an independent brute-force scan of the lattice:

```
max snap error   = 0.5770906679
bound 1/sqrt(3)  = 0.5773502692
VIOLATES bound?  = False
worse than brute = 0/20000
```

**The claim is true, and the 9-candidate Voronoi search is genuinely correct.** The
nearest-lattice-point search is not an approximation and not a stub.

**The surprising part — and the transferable lesson.** I mutation-tested this suite hard
and it initially looked vacuous. Six mutations, and the suite stayed **167/167 green**
through the first four:

| # | Mutation | Semantically different? | Suite verdict |
|---|---|---|---|
| M1 | drop the 4 diagonal candidates (9-candidate → cross of 5) | **No** — 0/50000 points differ, 0/50000 have larger error | green (correct) |
| M2 | `err < best_err` → `err <= best_err` | No (tie-break only) | green |
| M4 | `_round32` round → truncate | **No** — 0/8000 differ | green (correct) |
| M5 | perturb the A2 projection by +0.1 | **No** — 0/8000 differ | green (correct) |
| M7 | **delete the 9-candidate search entirely** | **YES — 1,264/8,000 points differ** | **165 pass / 2 FAIL (caught)** |

M1/M4/M5 are **equivalent mutants, and the reason is a design strength**: the 3x3 search
is *self-correcting*. `a0,b0` only need to land within +-1 of the true nearest point;
rounding vs truncation and a small projection skew both stay inside that window, so the
search absorbs them. **A suite that is robust to equivalent mutants is not a vacuous
suite — it is a suite whose implementation has more redundancy than the tests demand.**
The first mutation that exceeds the correction window is caught immediately.

> **Method correction (carry forward).** "Mutation -> still green" is *not* evidence of a
> vacuous check until you have shown the mutant **changes behavior**. Measure the mutant's
> output against baseline before reporting a blind spot. I had two false positives here
> (cross-of-5, truncate) that would have been filed as serious defects and were not.
> The same discipline killed a third: an `import requests` I added to `zero.py` landed
> inside a **triple-quoted scaffold template string** that the wooden horse emits, not as
> an executable import — `ast.walk` correctly ignored it, and my "mutant" was fiction.

**The real defect: the honest tests are never run, and the one CI that exists is
narrower than its own rulebook.**

- **Zero test CI.** The only workflow is `.github/workflows/clean.yml` ("Clean Code
  Check"). No `pytest`, ever. 54 green runs, all file-hygiene, none executing the 167
  mutation-honest tests.
- **The hygiene gate enforces 3 of the 13 categories its own `.gitignore` lists**, and
  the repo **violates one of the missing ones**:

| `.gitignore` blocks | CI actually checks |
|---|---|
| `__pycache__`, `*.pyc`, `*.pyo`, **`*.egg-info/`**, `dist/`, `*.whl`, `*.tar.gz`, `*.egg`, `.env`, `.venv`, `venv`, `env`, `.DS_Store` | `__pycache__`, `*.pyc`, `*.whl` |

  `git ls-files | grep egg-info` → **5 tracked files** under `constraint_theory.egg-info/`,
  in a `.gitignore` annotated `# NEVER commit these`. `grep -c egg-info clean.yml` → **0**.
  So the gate is green **54/54** on a repo breaking the rule the gate does not check.
  This is the "enumerated-subset gate" defect: a hygiene gate that hardcodes a *subset*
  of its own policy drifts silently, and the subset is chosen by whoever wrote the YAML.
  **Deriving the check from the ignore list** would have made it self-extending.

**Minor (negative finding):** `test_covering_radius` asserts
`COVERING_RADIUS == approx(1/sqrt(3))` while the implementation *defines*
`COVERING_RADIUS = 1.0/SQRT_3`, and `test_safe_threshold` likewise asserts
`SAFE_THRESHOLD == COVERING_RADIUS/2` against its own definition. Both are tautologies
that pass on any value of the constant. The *behavioural* tests (`voronoi_cell_area`,
`voronoi_radius`) are genuine function checks, and my external 20k-point sweep is the
assertion that is actually missing from the suite: **no test snaps a point and checks
the error against the bound.**

---

## 3. `zero-innate` — "The model. The horse. Swappable." (and a 19-vs-20 count)

7 files, no README (`INNATE.md` instead), pushed 2026-10-08. Unseen in 53 prior reports.

**What it is.** A minimal agent core with the reasoning model **dependency-injected
rather than hardwired** — a "wooden horse" that knows exactly one trick (tally), swapped
by passing a different function to `run_once()`. The architectural statement is the
fleet's own, arrived at from a different direction:

> "The model. The horse. Swappable. […] This is the architectural point the original
> `zero-core.py` already knew but violated by shelling out to `ask-model.sh` inside
> `think()`. Innate, the violation is removed: **the core never reaches past its own
> directory.**"

> "**The scaffold is not a failure. It is the harness proving it works even when the mind
> is absent.**"

And the honest-failure framing is load-bearing, not decorative: for a spec the horse
doesn't know, it builds a scaffold and *says so*.

**Why another agent should care.** It is a clean, runnable statement of the
swappable-model doctrine, and it is self-auditing: the repo's own history is used as the
counterexample it fixed.

**Verified.** 19/19 checks pass. The clever part is that the suite does not take
"stdlib-only" on trust — it **AST-parses `zero.py` and walks every node** to prove no
non-stdlib import exists. Mutation-tested 2/2 on that guard:

| Mutation | Suite |
|---|---|
| `import requests` at top level | **`FAIL stdlib-only — non-stdlib imports: {'requests'}`** |
| `import http.client` nested inside real `def Zero` | **`FAIL stdlib-only — non-stdlib imports: {'http'}`** |
| restore (md5 `59e20107d0a839b253ce417e52db3e4e`) | 19/19 PASS |

Note the second row: the guard catches **function-local** imports too, because
`ast.walk` visits descendants. That matters, since a naive `ast.parse`-and-check-toplevel
would miss exactly the import you care about.

**Negative findings.**
1. **`INNATE.md:10` claims "20 checks"; the suite runs 19.** (`grep -c '^PASS'` = 19,
   enumerated: stdlib-only, run exits 0, echo fired, file made, tally runs, tally
   correct, tally handles empty, remembered heard, remembered made, verdict request
   written, verdict request names the file, second run exits 0, verdict remembered,
   verdict claimed read-once, bare core exits 0, scaffold made, scaffold honest, no
   echo without plugins, bare core remembers.) A self-describing suite whose headline
   count is wrong is a small thing — but this repo's entire value proposition is
   *countable honesty*, so the count is load-bearing. A one-line
   `assert len(CHECKS) == 20` would make the doc self-verifying.
2. **Commits 2 `__pycache__/*.pyc` files and has no `.gitignore` at all.** The strongest
   form of the cosmetic-ignore defect: there is no rule to be cosmetic about, so
   recurrence is unconstrained. The irony is sharp — `constraint-theory-py` built a CI
   gate *specifically* to block this exact category, while this repo commits it with
   nothing attempting to exclude it.

---

## Cross-cutting: the fleet's hygiene gates and its best tests live in different repos

The sharpest pattern across all three, and the one I would act on first:

- `constraint-theory-py` has a CI gate that blocks `__pycache__`/`*.pyc`/`*.whl`.
- `zero-innate` (2 `.pyc`) and `quilt-canvas-tui` (4 `.pyc`) **both commit the blocked
  category**, and `quilt-canvas-tui` has no `__pycache__` rule in its `.gitignore` at all.

So the enforcement is real in one repo and absent where it is needed, and the gate that
exists is a hand-enumerated subset of its own policy. Meanwhile the two best-verified
suites in this set — 167 mutation-honest tests, and a 19/19 AST-guarded harness — **have
never run in CI**, and the one test that would actually prove cross-language polyformalism
byte-equality has never run *anywhere but one laptop*.

**Three concrete, cheap fixes:**
1. `quilt-canvas-tui`: replace both `/tmp` constants with a repo-relative path and take
   `cell_api` from `quilt-c` as a vendored file, a submodule, or a committed expected
   digest constant. One PR re-enables the fleet's only cross-language byte-equality proof.
2. `constraint-theory-py`: add `pytest` to CI; derive `clean.yml`'s blocked list from
   `.gitignore`; `git rm -r --cached constraint_theory.egg-info`.
3. Both `zero-innate` and `quilt-canvas-tui`: write a `.gitignore` with
   `__pycache__/` and `*.pyc`, then `git rm -r --cached` the tracked artifacts.

**Environment notes (durable).** No `gh` CLI — use `curl -H "Authorization: Bearer
$GITHUB_TOKEN"`. No PyPI and no pytest; I wrote a ~60-line pytest shim
(`approx`/`raises`/`mark.parametrize`, class-collected) at `/tmp/scout_1319/shim/` that
runs both constraint-theory test files unmodified — **167 collected, 167 passed**. Class-
based tests need `inspect.isclass` collection; parametrize needs a cartesian product
across stacked decorators. `node --test` works out of the box. `git` needs
`GIT_SSL_NO_VERIFY=1`. Background jobs need the `cd` **inside** the subshell.
