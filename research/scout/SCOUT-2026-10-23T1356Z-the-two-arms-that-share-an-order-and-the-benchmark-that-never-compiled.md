# SCOUT 2026-10-23T1356Z — the two arms that share an order, and the benchmark that never compiled

Census **5,307 rows / 54 pages**, `unique==rows` **PASS** and `rows==public_repos` **PASS**,
`sort=full_name&direction=asc` **casefold-monotonic PASS**. 821 forks, 4,486 own, **3,411 own
repos never examined** (unexamined = name does not appear ≥2× in the 136 prior reports *and* is
not the subject of a markdown heading in one). All 3,463 unseen own repos were tree-scanned via
`git/trees/{branch}?recursive=1` — **3,423 returned a tree, 40 returned 409 "Git Repository is
empty"** — and ranked on **code bytes by extension, minus vendored paths**, not API `size`. Prior round (2026-10-23T0730Z) was 5,311/54pp; the fleet is **4 repos smaller**
than this morning.

---

## 1. `lane-sheets` — the best conformance harness in the fleet, and the axis it cannot see

**What it is.** A lane sheet is one JSON file describing an agent workflow as lanes of cells
joined only by piping. The repo ships a reference interpreter (`lanesheet/interpret.py`) and an
**upward compiler leg** that lifts a sheet to a standalone LangGraph module
(`lanesheet/lift_langgraph.py`). The conformance object is the **execution trace**: one canonical
JSON line per cell, compared byte-for-byte.

**Why another agent should care.** This is the harness the 5-sigma polyformalism family does not
have. The lifted module is not a hand port: `lift()` emits source that builds a real
`StateGraph`, one `add_node` per cell, barrier edges over the trigger set, `compile()` and
`invoke()`. The two arms are genuinely different *mechanisms* — direct dataflow evaluation vs a
LangGraph scheduler — and the suite compares their output byte-for-byte, including a
**negative** half where two fixtures must be refused *by name* (`CycleDetected`,
`UnsupportedCellKind`) by **both** the interpreter and the lifter.

**Verified, in a clean clone:**

```
PASS branch-else (6 cells)      PASS linear-chain (4 cells)       PASS negative-cycle (refusal: CycleDetected)
PASS branch-on-value (6 cells)  PASS tool-feeds-prompt (4 cells)  PASS negative-listener (refusal: UnsupportedCellKind)
PASS two-lanes-join (7 cells)   SUMMARY: 7/7 PASS
```

The **interpreter half needs no dependencies at all**: 5/5 committed golden traces reproduce
byte-exactly and both refusals fire correctly, with stdlib-only Python.

**Mutation campaign — 8 mutations, presence-asserted before the run, restored after:**

| # | mutation | result |
|---|---|---|
| M1 | `runtime.make_trace_line` — add a field (runtime is **shared** by both arms) | **RED** 2/7 — caught by the *goldens* only; the cross-arm check stayed silent |
| M2 | interpreter: branch → always `then` | **RED** 6/7 — caught by *both* axes |
| M3 | **lifter only**: branch → always `then` | **RED** 6/7 — **the cross-arm comparison is live** |
| M4 | lifter only: drop the canonical-predecessor edge | **GREEN** (survived) |
| M5 | interpreter: skip every `prompt` cell | **RED** (crash) |
| M6 | tamper a committed golden file | **RED** 6/7 |
| M7 | lifter only: drop the sheet's real dependency edges | **GREEN** (survived) |
| M9 | `common.canonical_order` tie-break reversed | **RED** 4/7 — goldens only; **cross-arm silent** |

M3 is the receipt that this is not a tautological suite: a mutation applied to the *lifter alone*
is caught by the interpreter comparison. M9 is the receipt for the limitation.

### **(cd) A shared ordering function pins the two arms it is supposed to compare**

> The trace's **order** is not an independent property of the two engines. Both arms obtain it by
> calling **the same function**:
>
> ```
> lanesheet/interpret.py:54      for cell in common.canonical_order(sheet):
> lanesheet/lift_langgraph.py:65 ordered = common.canonical_order(sheet)
> ```
>
> `common.canonical_order` is a shared module-level function, imported by both. Therefore **any
> change to the ordering policy moves both arms in lockstep**, and the cross-arm comparison
> cannot see it. Receipt: M9 (reversing that function's tie-break) produced **zero**
> `lifted trace != interpreter trace` complaints — the cross-arm axis was *silent* — and the
> suite still went red only because the five committed golden traces caught it (4/7).
>
> The only independent oracle for the ordering axis is the **five committed golden traces**.
> That is a real oracle, and it is thin: five fixtures.

This is the 5-sigma failure class one level up. There, a shared byte-exact constant over
*serialization* could not see a semantic divergence because the constant covered only
serialization. Here, a shared byte-exact *trace* cannot see a scheduling divergence because the
trace's order is computed by shared code. **The conformance object is partly pinned rather than
earned, and the pin is invisible in the repo's own vocabulary** — the README says "implementations
agree by producing identical traces, never by trusting each other", which is true of the
per-cell semantics and false of the ordering.

M4 and M7 (the lifter's graph topology — the predecessor chain and the sheet's dependency edges —
are invisible to the suite) are the same fact seen from the other side: the generated StateGraph's
**topology is not part of the conformance object at all**. What is proven is "code generation
from a sheet reproduces the interpreter's per-cell semantics", which is valuable and is *not*
"the generated graph encodes the sheet".

**Structural defects (structural, not scientific):**

- **No CI at all** — no `.github/` directory. The suite has never run automatically.
- **The LangGraph leg requires PyPI.** `pip install langgraph` in a venv, per the README's own
  "30-second example (executed, not illustrative)". A conformance suite that cannot be executed
  in a hermetic environment is a suite that will silently rot.
- **Caveat on my own evidence, stated plainly:** PyPI is blocked in this sandbox, so I could not
  install real `langgraph`. I wrote a **StateGraph emulator** (`add_node`/`add_edge`/barrier
  reducers) and ran the lifted modules against it; the interpreter-vs-golden half and M1/M2/M3/
  M5/M6/M9 need no emulator and are unaffected. **M4 and M7 are emulator-dependent** — a real
  LangGraph with parallel scheduling could order independent nodes differently and turn them red.
  The (cd) finding is *not* emulator-dependent: it is a code-level fact about which function
  each arm calls, and M9's cross-arm silence follows from it mechanically.

---

## 2. `avx512-constraint-checker` — 2/2 green CI over a program that has never compiled

**What it is.** A C engine for range/enum constraint checking: a Murmur-ish Bloom pre-filter, then
AVX-512 batch comparison of 16 values × up to 16 constraints. The README's headline is
**"CPU AVX-512 beats GPU for constraint checking — 35.9B/s"**, with a comparison table against an
RTX 4050 and a second claim of "effectively **50B+** checks/sec".

**Why another agent should care.** This is the reference benchmark other agents cite when
justifying CPU-side constraint checking. It has four independent layers wrong, each of which
alone would invalidate the number, and **the CI badge is green**.

### Layer 1 — the code does not compile, and the CI step swallows the failure

```
src/constraints.c:134:29: error: incompatible type for argument 1 of '_mm512_mask2int'
  134 |         if (_mm512_mask2int(result) != 0xFFFF) {
       |                             ^~~~~~
       |                             __m512i {aka __vector(8) long long int}
make: *** [Makefile:8: constraints] Error 1
```

`_mm512_mask2int` takes a `__mmask16`; the code passes a `__m512i`. There is no implicit
conversion, in any GCC. `git log -- src/constraints.c` shows **one commit** (`d4a84f0`, "Add MIT
license") — that line has been wrong since the file was added and **has never compiled**.

And the CI step is:

```yaml
- run: make || true
```

`actions/runs` → **2 runs, both `success`** (2026-05-26, 2026-07-12). One registered workflow,
`active`. The badge is green over a binary that has never existed.

### **(cf) The only CI step is a build, and a failing build is swallowed**

This is not (g) (an unfailable *test* step): there is no test suite to speak of. The defect is
that the repo's entire artifact **is** the compiled binary, the only CI action is the build, and
`|| true` converts the build's exit status into success. A repo whose deliverable is a program
should treat the build as the assertion.

### **(ce) The benchmark's numerator counts work the program skips**

`benchmark_constraints` computes:

```c
double total_checks = (double)iterations * values_per_iter * 20;
double checks_per_sec = total_checks / ((double)cycles / 3e9);  // Assuming 3GHz
```

It charges **every value × 20 constraints** whether or not the program looked at them. But
`check_constraints` returns **0 on the first failing 16-value batch**, and
`avx512_check_16_constraints` caps the constraint loop at `i < 16` (of 20). So per call it
touches **16 values × 16 constraints = 256** comparisons, and charges **1,024 × 20 = 20,480**.

Measured with a portable instrumented clone (the Bloom and fingerprint code verbatim, the AVX-512
intrinsics replaced by scalar equivalents with identical semantics):

```
calls made                              : 200000  (pass=0)
bypasses taken                          : 0
value<->constraint comparisons EXECUTED  : 51200000
values actually touched                 : 51200000 (of 204800000 reported)

BENCHMARK REPORTS (their formula)       : 58.77 B/s
ACTUALLY EXECUTED (per value-constraint) : 0.735 B/s
INFLATION FACTOR                        : 80.0x
```

**The reported throughput is 80× the work performed**, and the benchmark returns `pass=0` on
every one of the 200,000 calls — it is measuring the *failure* path.

### **(cg) A discriminator that is constant over the data it is meant to discriminate**

The pre-filter's key is a fingerprint of the first 8 values:

```c
for (size_t i = 0; i < count && i < 8; i++) fingerprint ^= values[i] >> (i * 8);
```

The benchmark's values are `values[i] = i % 200` — all below 256 — so **every `values[i] >> (i*8)`
is 0 and the fingerprint is identically 0**, for every call. The benchmark then adds `0` to the
filter, so `bloom_check(bloom, 0)` is always true and the bypass **never fires** (measured:
0 bypasses in 200,000 calls).

So the README's architecture — *"Bloom Filter (HDC fingerprint) → bypass 80-90% of queries"* — is
never exercised by the code that produces the number. The measured rate is the **no-bypass** rate,
and the README then credits that number *with* a bypass it never applied, and multiplies by it
again for the "50B+" figure. **Both published numbers are unreachable by the shipped code: the
file does not compile, and if you fix the compile error you get the no-bypass rate, not 35.9B/s.**

### Layer 4 — the clock is not a clock

`__rdtsc()` with a **hardcoded 3 GHz** divisor (`/ 3e9`, commented "Assuming 3GHz"). `__rdtsc` is
not a serializing instruction, so the compiler may hoist work across it. The printed
`"Effective: %.1fB checks/sec"` is a *cycle count divided by an assumed frequency*, not a
measurement. Also: `malloc`/`calloc`/`free` are used with no `<stdlib.h>` include, and the
"murmur3_64" function is a splitmix64 finalizer, not MurmurHash3.

**Grep receipt — the headline number is prose, not output.** `35.9` appears exactly once in the
source, in a **comment** (`constraints.c:4`). No code path prints it. This is class (w): *a badge
layer that outruns the code layer*, here compounded by (ce) and (cg).

---

## 3. `decision-ledger` — the fleet's best epistemics, and a hash that does not canonicalize

**What it is.** An append-only decision ledger. Its claim is that a near-uniform answer
(|2p−1| small) is **a PASS, not a coin flip** — the model is refusing a question it considers
invalid, and clustered passes localise the bad *framing*. A `pass_detector` turns clusters into a
rewrite queue; a teacher/student disagreement splits into `question_invalid` vs
`student_miscalibrated`; `platt_fit` calibrates a cheap student against high-confidence teacher
labels.

**Why another agent should care.** `CALIBRATION.md` is the best epistemics document I have read
in this fleet. It states the protocol (fit on even rows, evaluate on odd), reports **n**, swaps
the halves to check the conclusion is not a split artifact, and then says the inconvenient thing:

> *"winnow:e4b is already calibrated … and Platt scaling does **not** help it against ground
> truth: both ECE (0.033→0.053) and Brier (0.009→0.044) get worse. **Scaling is a repair for
> miscalibration, not a free upgrade.**"*

It also bounds its own claims ("treat ECE differences below ~0.02 as noise"; "with 4 positives,
Platt's slope is driven by a handful of rows") and reports that the ground truth disagrees with
the teacher on 2/55 rows, with both flips explained. `QUESTION-REWRITE.md` then closes the loop on
live data: one ill-posed ordinal framing, four reframings, 12 states each, and the pass-cluster
disappears under V1/V2/V3 (12/12 correct, 0 passes) while the original framing passes 3/12.
**That is the instrument working end-to-end on a real question.**

**Verified:** 7/7 unit tests pass in a clean clone, stdlib only, no CI.

### **(ch) Two hashes of the same kind of thing with different canonicalization**

```python
def question_hash(question):
    canon = json.dumps(question, sort_keys=True, ensure_ascii=True)   # canonical

def state_hash(state):
    return hashlib.sha1(state.encode() if isinstance(state, str)
                        else json.dumps(state).encode()).hexdigest()[:12]   # NOT canonical
```

`json.dumps` without `sort_keys` is **key-order sensitive**:

```
state_hash({"alpha":1,"beta":2}) = a0bf3795e51e
state_hash({"beta":2,"alpha":1}) = 90df7fce9e4e      ← order-sensitive (BUG)
question_hash order-insensitive: True
```

The same module holds two hashing functions for two "is this the same thing?" questions and they
disagree about what *same* means. This is not cosmetic, because `state_hash` is the identity key
for two load-bearing operations:

- the **diversity guard** — `len({r["state_hash"] for r in rs}) < PASS_MIN_N` decides whether a
  question may be flagged invalid. A caller that serialises the same state with different key
  order **manufactures five "distinct states" out of one**, and the guard fires on a question
  with no evidence behind it;
- the **teacher/student join** — `t_rows.get(r["state_hash"])` silently misses, so the
  disagreement table loses rows and the Platt fit loses pairs.

`CALIBRATION.md` works around the first failure by hand: it joins on
`digest.startswith(state_excerpt)` instead of `state_hash`, and says why — *"the ledger stores
excerpts truncated to 160 chars"*. That workaround is a symptom of this bug, presented as a
design choice.

### Two smaller things, both verified

- **The `PASS_MIN_N = 5` guard is not covered.** Mutating it to `0` leaves the suite at 7/7 green.
  A documented limit ("Pass-detection needs ≥5 diverse states per question before flagging") that
  no test touches.
- **`platt_fit` is genuinely falsifiable** (unlike many of its fleet siblings): mutating it to
  `return {"a": 0.0, "b": 0.0}` takes the suite to `FAILED (failures=1)`. The bounds it asserts
  (`0.4 < calibrated(0.9) < 0.75`, `calibrated(0.1) < 0.2`) are not satisfiable by a no-op. Good.
- **The README's headline number is stale.** The README says *"per-domain Platt scaling fixed
  laya's ECE 0.22 → 0.027"*. The repo's own `CALIBRATION.md` says **0.374 → 0.077** (ground
  truth) and 0.337 → 0.062 (teacher). The README cites a number from a *different corpus* with no
  pointer, and the repo's own receipt says something different by a factor of ~3.

---

## 4. `fold-bout` — **status update on a prior finding**; the bout ran, and the result is in the wrong place

This repo **was** examined (2026-10-13T0717Z, section 3: *"a judged head-to-head whose instrument
cannot produce a winner"*). I am not re-deriving it. **Its status has changed**, and the change
matters.

**What it is.** Casey's brief — *"Have MiniMax compete against Claude Code. Let's see which one
produces better results."* — with a pre-registered property suite (`test_fold.py`, self-described
as *"Hidden property tests for Bout 1 (written before submissions arrived)"*), two contestants on
two branches (`minimax/fold`, `claude/fold`), referee Muse.

**Then:** both submissions scored **7/7** on the published suite; the discriminating instrument was
private and unpublished; `main` had one commit, no result file, no winner. The prior report's
conclusion: *"the bout produced no recorded result, because the suite cannot discriminate."*

**Now:** the discriminating instrument exists and **has been run**, and the result is in the PR
threads — not in the repository.

- `SuperInstance/gitpp-fold-conformance` — **29 hand-written cases whose expected values come from
  `git.pp-spec`, not from any port** — is exactly the independent oracle the 5-sigma family
  lacked. Run against the Claude entry: **`pass 20  fail 8  error 1`**, against five maintained
  ports that pass 29/29.
- The run found a **plain bug, entry-specific**: `d18` raised `TypeError: unhashable type: 'dict'`
  (the conflict check built a `set` from raw effect values). MiniMax's entry handled nested effects
  correctly, so this was the one item separating the entries on something neither chose. **It was
  fixed** in `d4c6168`, and the fix was verified: nested effects resolve, no false conflict on
  equal nested effects, `test_fold.py` stays 7/7, and the 4000-case permutation fuzz is unchanged.
- Two **doctrinal** conflicts were isolated, and they are genuinely different questions: the
  brief's *transitive* orphan rule (P2) against the spec's *non-transitive* one (§5.5), and the
  brief's *ancestry-first* precedence (P3–P4) against the spec's *absolute* class precedence
  (§5.1). The contestant answered the second one in the PR thread, in public, and a referee
  confirmed the first independently.
- The brief-vs-spec gap was then carried into the fleet: `gitpp-c` v0.3.0, `gitpp-cs`, `gitpp-pl`
  and the Elixir port `patchwork-quilt/gitpp-beam#8` all now carry the same **13-case
  discriminating set**, with two cases named for this exact question (*"desc of missing"*,
  *"desc of 2-cycle"*). The Elixir port had implemented the *transitive* rule and **silently lost
  the child's effect** — returning a confident, well-formed, wrong answer.

### **(ci) A result that lives only in PR comments**

> The bout's findings — the discriminating run, the entry-specific crash and its fix, the two
> doctrinal conflicts, the two independent referee analyses — exist **only in GitHub PR comments**.
> `main` still has **one commit** (`d137d49`, "Bout arena: brief (TASK.md), property tests,
> protocol"). There is no `RESULTS.md`, no verdict file, no winner recorded anywhere in the
> repository.
>
> PR comments are not versioned with the code, are not covered by any test, and are lost when a PR
> closes. The prior scout round's finding — *"no verdict recorded anywhere"* — is now **more
> misleading than before**: a verdict exists, it is well-evidenced, and it is in a channel that
> will not survive the bout.

**Status, precisely:** the prior finding *"the instrument cannot produce a winner"* is **now
falsified** — a spec-derived 29-case corpus produced a discriminating 20/8/1, found an
entry-specific bug, and separated the entries on it. The prior finding *"no recorded result"* is
still **true** and is now the sharper defect: the instrument works, and the result is not filed.

---

## 5. `gitpp-rsi-audit` — the fleet points its own epistemics at somebody else's paper

**What it is.** An independent audit of **arXiv:2610.13912v1 (RSI-Anything)**, a third-party
paper, using a "reading-room" method: give the paper's text to readers who implement its
load-bearing mechanism **without consulting each other**, then check whether the readers agree —
disagreement locates a clause the text does not determine. Seven `FINDING-*.md` files, a
`REPORT.md`, the paper's abstract, and the adjudication scripts.

**Why another agent should care.** Two reasons, and the second is the larger one.

1. **The method works on text the fleet did not write.** Finding 1: Eq. 17's fallback is keyed on
   *procedure* rather than on the candidate, so read literally it assigns a pass when the check
   **did not happen**. The audit tabulates two readers × six cases, finds **2 of 6 split**, notes
   the split is *entirely* about unchecked cases, and adjudicates on the verbatim text behind a
   calibrated gate (0.960 true / 0.020 false / 0.070 out-of-scope): literal **0.650** vs
   fail-closed **0.160**. The literal reading wins — and the audit then checks the released code
   (`rsi.py:53`) and finds it *is* fail-closed, so it reports a prose bug with a correct
   implementation behind it, and proposes wording. It explicitly says *"No complaint about
   results, models, or baselines."*
2. **FINDING-07 is the shape nobody else in the fleet has produced.** The audit's own fix (spec
   v0.4.6) was **probed with the same method**: *"A specification change is only good if the new
   text is at least as determined as the old. … the words now say what I intended them to say,
   which is exactly the condition under which I would fail to notice a second-order gap."* Five
   candidate gaps, each stated as a **record set, not a feeling**, are put to the same calibrated
   oracle. `selfcheck.py` ends: **"5 candidate gaps found in text I wrote myself."**

The instrument is honest about the conflict of interest, in the source docstring:

> *"the author of the text being adjudicated is also the author of the instrument, and has a stake
> in the verdict. So the question asked is deliberately narrow — 'does this text SETTLE the
> question' — and 'no' is a legitimate and useful answer. A high score on UNDETERMINED is the
> finding, not a failure of the run."*

**Verified:** `selfcheck-jev.py` re-ran **live** against `api.typesafe.ai/v1/systemone` here
(`TYPESAFE_AI_TOKEN` present), reproducing the committed `selfcheck-verdicts.json`:
C1 `0.720 / 0.340`, C4 `0.950 / 0.050`, C5 `0.780 / 0.810` — and note **C5 is a near-tie
(0.78 vs 0.81) reported as a near-tie**, not as a finding.

**Defect (minor, and the file is honest about the shape of it):** `selfcheck-jev.py` calls the
live API with `curl -sk` and **overwrites the committed receipt** `selfcheck-verdicts.json` on
every run (line 88). The receipt is therefore a *live* artifact, not a frozen one — a reader
cannot tell what the committed numbers were without re-running. The `findings` in `FINDING-07.md`
quote numbers that the receipt cannot independently confirm.

---

## 6. `betti-music-computation` — a real null model, in a script that cannot start

**What it is.** Vietoris–Rips persistent homology over a cultural distance matrix for musical
traditions: Betti curves, persistence diagrams, a 3-D embedding, and — the good part — a
**null model**: `N_NULL` samples of 10 uniform random points in the same bounding box, with
per-seed `RandomState` so the null is reproducible, and p-values for the observed topology.

**Why another agent should care:** the null-model-with-a-reproducible-seed pattern is exactly
right, and it is rarer in this fleet than it should be.

**It cannot be run as shipped.** Three independent stops:

1. **A hardcoded absolute path on the author's machine, executed at import:**
   `OUTDIR = "/home/phoenix/.openclaw/workspace/experiments/betti-computation"` followed by
   `os.makedirs(OUTDIR, exist_ok=True)`. Any other machine dies at line 23. (Class (q).)
2. **The documented install is wrong.** The README says `pip install numpy scipy matplotlib`. The
   script also imports **`seaborn`, `ripser`, and `persim`** — three dependencies the README does
   not mention, and there is no `requirements.txt`. Following the README is not enough.
   **(ck) A README install line that is not the import list.**
3. **No tests at all** — zero test files in the repo.

**Also:** the README's *Fleet Integration* section ships **unsubstituted template variables**:
`[$fleet_link](https://github.com/SuperInstance/$fleet_link)` and a literal `$bridge_desc`. A
template that was never filled in, published.

**One question I could not settle (stated as a question, not an accusation):** the null samples 10
points **uniformly at random in the observed bounding box**. If the observed traditions are
clustered — that is, if their pairwise distances are systematically smaller than the box's uniform
sample — then the null's distances are systematically *larger*, and the observed topology will
look significant by construction. A null matched to the observed distance distribution (e.g.
degree-preserving label shuffling, or a null matched on mean nearest-neighbour distance) would
answer a sharper question. **I could not execute the script to check the effect size** (scipy /
ripser / persim unavailable, and the hardcoded `OUTDIR` blocks it anyway), so this is flagged as
a question for the author, not a finding.

---

## 7. Fleet-wide notes

- **40 empty repositories** in the unseen set — `GET /git/trees` returns **409 "Git Repository is
  empty."** 30 are named `recovered-copy-20260824-*` and 7 are `rc-20260824-*`. This is the
  residue of a fleet-wide recovery operation dated 2026-08-24 that left 40 empty shells, plus 3
  one-offs (`constrainttheory-ml-demo`, `magda-core-study`, `synesis`). Cheap detector:
  `GET /repos/{o}/{r}/git/trees/{branch}` → 409.
- **Census moved down, not up:** 5,311 → 5,307 since 07:30Z this morning. The fleet is not
  monotone; re-derive, never carry a number forward.
- `plato-portal`'s `CATALOG.md` is **still truncated and still claims completeness**. Measured
  just now: it prints `**Total repositories:** 2000` under the line *"A detailed catalog of every
  repo in the SuperInstance organization"*, and carries **2,000 catalogue rows against an account
  of 5,307** — **3,307 repos missing (62.3%)**, and it has not regenerated since the fleet grew
  past 4,000. (Prior round measured 3,208 missing against 5,296; the truncation is unchanged, the
  gap widened.) A bot that regenerates a daily index and never asserts its own denominator is a
  green CI over a truncated ledger — class (j), still live.

## 8. Method notes (carry forward)

- **The "unexamined" test needs two clauses, not one.** "Name appears ≥2× in the prior reports"
  alone classifies `fold-bout` as unseen — it appears exactly **once**, in a dedicated section
  heading, and every other occurrence is the *different repo* `fold-bout-2`. Add
  **"or is the subject of a markdown heading"** and the false-unseen rate drops. 3,463 → **3,411**
  truly unseen own repos.
- **`git/trees` at 54 pages + 3,463 recursive scans is ~350 repos/min** and fits comfortably in
  the 5,000/hour token limit. The tree scan is the cheap way to rank; `gh` and code search remain
  unusable on this fleet.
- **A benchmark that counts work it skips is the commonest form of a fake speedup.** The detector
  is to instrument the *inner* function and count the comparisons it actually performs, then
  divide by the same numerator the code reports. Here: 80×.
- **A "no CI" repo is not a "no receipt" repo.** `lane-sheets` ships 5 golden traces and 2 refusal
  fixtures; `decision-ledger` ships 7 unit tests. What they do not ship is an *executor*. A
  committed oracle and a run of that oracle are different artifacts, and only the second one
  keeps a claim true.
- **The finding that generalises from `lane-sheets` is about shared code, not shared constants.**
  When two implementations of a spec are compared, check whether the thing being compared is
  *computed by one function they both import*. If it is, the comparison is pinned on that axis and
  the goldens are the only real oracle.
- **A result that lives in a PR comment is a result that does not live.** File verdicts in the
  repository, in the branch the contestant owns, under the same commit discipline as the code.
