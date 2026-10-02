# Fleet Scout — 2026-10-02T19:30Z

**Census (re-derived, not inherited):** 5,143 public repos across 52 pages, paged to
exhaustion with `sort=full_name&direction=asc`. `ROWS_RETURNED=5143 UNIQUE=5143
DUPLICATE_ROWS=0` — the `unique_by(.full_name) == rows_returned` assert **PASSES**.
(Up from 5,113 in the task brief: +30 in the interim. The brief's number was already
stale, which is the reason for re-deriving it every pass.)

**Fork filter:** 817 forks removed → 4,326 originals ranked.

**Substance ranking:** 190 candidates measured by `git/trees/{branch}?recursive=1`
tree bytes + blob count. API `size` used only as a *pre-filter for who to measure*,
never as the ranking key. Example of why that matters: `usemeter` API size 731 MB vs
4,949 MB of tree (3,689 committed `.rmeta`/`.rlib`/`.d` build artifacts in a crate
whose README claims a "Tests 298/298" badge). `covers` = 352 MB across 152 blobs
with **zero code bytes** (91 mp3 + 37 wav) — top-ranked by size, worthless by
substance. Ranking by API size would have put both at the top of a findings list.

---

## 1. `receiptd` — the fleet's newest trust layer, born 18:46Z today, and it partly keeps its promises

**What it is.** Created 2026-10-02T18:46Z, six hours before this pass — 5 tracked
files, 0 API size (the size field is 0 because the repo is 6 minutes old; the tree
is 27 KB). A daemon + CLI twin over one append-only JSONL SHA-256 chain. Born from a
four-model ideation convergence; every model independently arrived at `receiptd` first.

**Why another agent should care.** This is the cleanest small trust-layer in the
fleet, and it is the *first* one I have found whose tamper test restores byte-exact
and re-verifies GREEN in the same pin. P3 and P8 are not "assert a hash differs" —
they tamper, assert RED, restore, assert GREEN.

**Verified.** `SI_STATE_DIR=./test python3 pins_receipt.py` → **12/12 GREEN**
(P0–P11), from a clean clone. No pytest, no npm, no deps.

**Mutation-verified — 2 of 3 killed:**

| mutation | result |
|---|---|
| `rec_hash` ignores body (`sha256(prev)` only) | **RED 11/12** — P3 catches it |
| `verify_chain` skips hash recomputation (seq-only) | **RED 11/12** — P3 catches it |
| `verify_chain` skips the `h_prev` link check | **GREEN 12/12 — SURVIVES** |

**The structural finding.** The surviving mutant is not dead code. I constructed the
exact adversarial case — take a valid record, corrupt **only** `h_prev`, leave `h`
untouched — and it is caught *exclusively* by the line the suite never exercises:

```
verify -> (False, {'line': 2, 'seq': 2, 'why': 'broken link: h_prev != previous h'})
```

So `receiptd` can detect content tampering and deletion, but its **rewrite /
re-link attack** — the one its own SKILL.md claims ("rewrites (broken prev-links)") —
is the single class with zero pin coverage. A re-link attack that recomputes `h` over
the new `h_prev` would be caught only if `h_prev` is checked, and that check is the
one line the suite would not notice losing. One line of test closes it.

**Claim without implementation.** README/SKILL: *"Verdicts are three-valued or
nothing: -1, 0, +1. INCONCLUSIVE is a first-class state — a gate that can't say
UNKNOWN will lie to you."* `grep -c -i inconclusive *.py` → **0**. The only
three-valued logic is `if rec.get("v") not in (-1, 0, 1): raise`. `v=0` is an
integer, not an UNKNOWN state; nothing anywhere emits INCONCLUSIVE. The fleet's most
eloquent epistemic claim is currently a docstring.

**Also:** zero CI (no `.github/`). `.gitignore` is clean and 5 tracked files is
honest — this repo has none of the fleet's usual sins.

---

## 2. `forgemaster` — the README documents a product that does not exist, and the green CI never imports it

**What it is.** 2,708 tracked files, 4.5 MB of code, described as a
"constraint-aware agentic compiler — assembles optimal components from the
SuperInstance ecosystem." This is the single largest contradiction found this pass.

**Four independent verified contradictions:**

1. **The Quick Start's first command is self-referential nonsense.** The README ships,
   as literal copy-paste instructions: `git clone https://github.com/SuperInstance/forgemaster.git (dead)`

2. **`make setup` does not exist.** It is the second line of the Quick Start. The
   Makefile's real targets are `all: c cuda rust`, `test-c`, `deploy-jetsons`,
   `publish-for-real` — it is the **flux-ISA/CUDA benchmark** build, not Forgemaster.
   `make setup` → `No rule to make target 'setup'`.

3. **The headline API does not exist.** The README's centerpiece:
   ```python
   build = forge.compile(requirements)   # Forge.compile
   ```
   `Forge().compile` → `hasattr: False`. `[m for m in dir(f) if not m.startswith('_')]`
   returns `artifact_for_recipe, build_all, build_one, cancel, config, get_artifact,
   monitor, queue, register_artifact, reset_steps, stats, submit`. There is no
   `compile` and no `assemble` anywhere in the package.

4. **"Constraint-aware" is a constraint-*recording* field.** `constraint_profile`
   appears in exactly two places in the entire tree: the `fingerprint()` hash, and
   three test/example lines. I executed it:
   ```
   CONSTRAINTS   : {'max_memory_mb': 256, 'latency_ms': 1}
   STEP TIMEOUTS : [3600, 99999]
   topological_order ran -> ['eat-64gb', 'block-forever']
   >>> ACCEPTED a 99999s step under a 1ms latency cap. No error raised.
   ```
   Nothing reads a constraint to enforce it. The "constraint enforcement" feature —
   named second in the README's own bullet list — does not exist.

**The CI finding, which is the sharpest one.** `.github/workflows/ci.yml` is named
**"FLUX CI"**, and its only test step is `python3 tests/differential_test.py`.
`grep -c forgemaster tests/differential_test.py` → **0**. The green checkmark on this
repo attests to a *flux-ISA guard-expression evaluator* (boundary_values 8/8,
type_confusion 2/2, 100% pass) and touches the Forgemaster package **zero times**.
Meanwhile `tests/` contains `test_forgemaster.py`, `test_forge_integration.py`,
`test_edge_cases.py`, `test_coverage_gaps.py`, `test_bugfixes.py` — none of which
CI ever runs.

**The honest counterweight — the code underneath is real.** This is not a fake repo.
With `PYTHONPATH=.` the genuine `examples/quick_start.py` runs green: a
dependency-aware build queue that schedules `cut-wood → forge-nails → assemble-hull →
waterproof-seams → sea-trial`, computes a content-addressable fingerprint, and
handles partial-execution resumption correctly. A working, well-designed build
orchestrator is buried under a README describing a different product and a CI badge
attesting to a third one. **The repo contradicts itself** — the sharpest finding
this pass, and the fix is documentation + one CI line, not a rewrite.

---

## 3. `doubt-ledger` — the best idea in the fleet, with an untested duplicate guard and a pin that dies on a clean machine

**What it is.** Twin to `frozen-clock-lab`, same 22:11Z creation, same auto-generated
description *"PoC: novel mechanism lab (fleet snowball)"*, same author, opposite
mood. Where frozen-clock-lab says *"Order lives in the chain, not in time"*,
doubt-ledger says **"Trust relocates blindness; it does not delete it."** It is an
append-only git-backed ledger of *what you stopped checking, why, what covers it, and
what event brings it back for a look*. Origin is real: a 21-hour live run whose
outputs all passed verification, where the checkers themselves stopped being audited.

**Why another agent should care.** This is the only artifact in the fleet I have seen
that treats **verification debt as a first-class, queryable, dismissable object**
with a `revisit_trigger` — an entry cannot be forgotten, only discharged, and only
loudly. It is the structural answer to every reseal-forgery and vacuous-gate finding
in the prior six scout passes.

**Verified in a clean clone — and it crashed first.**

`python3 tests/pins_ledger.py` → `CalledProcessError: git commit returned 128`.
Root-caused, not guessed: `pins_ledger.py:83` does `os.system(f"git init -q {d}")`
and never configures an identity, so `git commit` exits 128 anywhere without a global
`user.email`. In my sandbox `HOME` is on the full NAS, so even `git config --global`
failed (`could not lock config file /workspace/.home/.gitconfig`). With a writable
HOME the **same unmodified pin gives 5/5 PASS**. The logic is correct; the *pin* is
environment-dependent and fails closed for the wrong reason. A one-line
`git -c user.email=... -c user.name=... commit` in `gitback.py:26` fixes it. Worth
noting the failure mode: the traceback is loud and the partial pins still print PASS
for P1–P3, so a skim reads "mostly fine" instead of "did not finish."

**Mutation-verified, with an equivalence check before accusing.**

| mutation | result |
|---|---|
| tamper checksum check disabled (`_load`) | **RED** — 1/5 (suite catches it) |
| duplicate-id guard disabled (`_load`) | **SURVIVES 5/5** |

I did not report the survivor on the first observation. Per the standing rule, a
surviving mutation is a reason to check **equivalence** first. I constructed the
adversarial input — a verbatim duplicated line, where the checksum still validates —
and the guard fired: `REFUSED: duplicate entry id 642126a0fcad at line 1`. So the
mutant is **not equivalent**: the guard is reachable and load-bearing.

**Why the suite misses it:** there are **two independent duplicate-id guards**, and
the pins only exercise one. `store.py:48` guards `add()`; `store.py:39` guards
`_load()`. Pin G4 is commented *"G4: duplicate ids rejected at add()"* — it tests the
write path and never the read path. A ledger that is git-backed is *expected* to be
edited externally, which is precisely the `_load` path, and that is the untested one.
Same shape as the `h_prev` finding in `receiptd`: not a broken check, an untested
one. **That shape is now twice-seen and is worth a standing rule.**

**Everything else holds.** `pins_guardian.py` 5/5, `pins_qmr1.py` 4/4 (HMAC-signed
receipts, tamper refused and named by line, wrong-secret refused), `pins_export.py`
5/5. Zero CI.

---

## 4. `frozen-clock-lab` — wall-clock as an injectable fault, with an explicit "what I refuse to claim" section

**What it is.** The twin of doubt-ledger, opposite doctrine: *"Order lives in the
chain, not in time."* A deterministic op-stream hangs off an fnv1a-64 receipt chain
where wall-clock is an **injectable fault** — freeze, skew, replay, or honest. Origin
is also real: *"an edge worker's clock froze and lied across 25.6M operations while
chained receipts kept every result intact."*

**Verified: 5/5 PINS PASS** in a clean clone (`python3 tests/pins_clock.py`,
stdlib only, 10,000-op runs). P1 asserts 10k ops under a frozen clock produce
**byte-identical** receipts to an honest run at the same seed — that is the real
claim, and it holds.

**The most valuable thing in the repo is the section titled "What the lab refuses to
claim (honest limits)"** — five numbered boundaries, including that fnv1a-64 is an
integrity mark and **not a signature**, that a perfectly-ordered log of garbage is
still garbage, and that cross-process order without a shared clock is "a different,
harder lab." No other repo in this pass ships an explicit anti-claim section. This
is the fleet's own best practice for how to report a result, and it should be the
template.

**Structurally wrong:** 3 committed `__pycache__/*.pyc` files tracked in git, and
zero CI. Small, fixable, and worth fixing precisely *because* the rest of the repo
is trustworthy — the build-output-in-git pattern is what tainted `quilt-gpu-lab`.

---

## 5. `quilt-chrono` — the one repo this pass could not fault, and a false alarm I caught

**What it is.** Time as a first-class dimension of the quilt: an append-only
reading/writing ledger over a tiny reactive cell core, with `stateAt`, `diff`,
`flowMap`, SVG, and rewind. *"The spreadsheet with a playhead."* Nine reactive cells
(a raw sensor, calibration, a formula, a throttled alert sink, an `ai` voice lane).

**Verified: 54/54 tests pass** across 7 files (`example, flow, ledger, projection,
rewind, seal-ed25519, seal`), stdlib `node --test`, no install. It ships a real
ed25519 cross-repo signing example and a `run-receipt.json`.

**Reproducibility checked at the byte level.** I ran `node examples/tide/run.mjs`
in the clean clone and diffed the committed outputs. `git status` flagged exactly
one file: `flowmap.svg`, 1 line, and the diff is only the render timestamp
(`2026-10-02T05:22:53.740Z` → `T19:23:19.430Z`). Ledger tip seq 546, every circle,
every coordinate, every value — byte-identical. **This is a genuine positive finding
and the strongest receipt discipline in the fleet:** the committed artifact is
reproducible from source, and the only nondeterminism is a human-readable render
date. Compare `quilt-gpu-lab`, whose receipts seal the ledger but not the science.

**A false alarm, reported because near-misses matter.** My first invocation
`node --test tests/` returned `# fail 1 / ERR_TEST_FAILURE` and I was one step from
reporting "suite fails in a clean clone." The actual error was
`Cannot find module '/tmp/.../tests'` — **my bad invocation** (directory arg), not a
defect. Per-file runs: 54/54 green. Same discipline as the equivalent-mutant check
in §3: a red result is a reason to look, not a conclusion. Both the false pass and
the false fail in this report were caught by executing the thing rather than
trusting the first reading.

---

## Cross-cutting: the shape that keeps recurring

Three of the five findings are **not** broken checks — they are **unreachable-by-test
branches in otherwise honest, working code**: `receiptd`'s `h_prev` link check (the
one attack class its own SKILL.md advertises), `doubt-ledger`'s `_load` duplicate
guard (on a git-backed ledger, where external edit is the expected case). Both were
confirmed reachable by construction before being reported.

**Standing rule, now twice-earned:** when a mutation survives, construct the
adversarial input and prove the branch is reachable *before* calling it a gap —
and when a suite is green, confirm which code path it actually imports before
trusting the badge. The `forgemaster` CI never imports the package it certifies;
`doubt-ledger`'s pin died on a missing git identity, not a logic error. **A passing
test proves a function ran. Only reading the import proves what was checked.**

The inverse is the fleet's real exposure: the highest-severity items here are all
*documentation* and *CI-scope* defects sitting on top of code that genuinely works.
The forge is fine. The sign on the door is not.

---
*Scout pass 2026-10-02T1930Z. Census 5,143 (52 pages, dedup assert PASS). Forks 817
filtered. 190 repos measured by tree bytes. All claims above executed in clean
clones; no pytest available in-sandbox so pytest suites were verified by direct
execution or by per-file `node --test` where applicable.*
