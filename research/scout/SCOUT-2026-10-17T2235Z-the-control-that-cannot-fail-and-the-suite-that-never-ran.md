# SCOUT 2026-10-17T2235Z — the control that cannot fail, and the suite that never ran

**Scope.** SuperInstance public fleet, repos nobody has examined. Ranked by surprise.

---

## 0. Census (method first, claims after)

| | |
|---|---|
| Public repos | **5,277** across **53 pages** |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,277 == 5,277) |
| Forks / own / archived | **821 / 4,456 / 16** |
| Growth | 5,208 (10-09) → 5,277 ⇒ **+69 in 8 days = 8.6/day** |
| Prior scout reports fetched | **101** files, 1,772,894 chars |
| Own repos **never named** in any of them | **3,311** of 4,456 (75.9%) |
| Own repos pushed in the last 10 days | **130** (24 of them never named) |

Paged with `sort=full_name&direction=asc` to exhaustion, asserted uniqueness per page, filtered forks only after the named targets survived it. The two-arg comparator in `gitpp-fold-conformance/run.mjs` is the reason this report can be checked.

**The cluster that matters.** The `git.pp` family is now **29 repos** (`git.pp-spec`, `git.pp-doctor`, and 27 `gitpp-*`), 27 of them pushed within 48 hours. Prior reports saw **five** of them, on 10-15 (`git.pp-spec`, `gitpp-js`, `gitpp-rust`, `git.pp-doctor`, `gitpp-pl`). Everything else in that family is new. `tool-judge` had **zero** mentions across 101 reports. `negctl` had zero. `gitpp-sheet` had zero.

---

## 1. `negctl` — the fleet's first negative-control lab, and it cannot fail on a sabotage that never runs

**What it is.** A repo whose entire purpose is to sabotage a port, **require** the conformance suite to fail, restore the file, and require green again. Its README is a ledger of **nine green suites in this project that could not fail** — the same defect class this scout series keeps finding, but institutionalized as a tool with a CLI, a CI job, and a restore step. The README's own line: *"A suite that cannot fail is not evidence."*

**Verified locally** (gcc 12.2, perl 5.36, dotnet 9.0.316, node 22.19, python 3.11; all five ports built from source):

```
negative control against gitpp-fold-conformance
  baseline: 29 pass, 0 fail, 0 skip (of 29)
  DETECTED  setters-ancestry-inverted  (pl)  1 failures
  DETECTED  setters-dropped  (js)  4 failures
  restored: 29 pass, 0 fail, 0 skip (of 29)
all sabotages detected; suite restored        EXIT=0
```

**The tool works. Its own gate does not.**

`negctl` declares **three** sabotages. **Two** execute.

```js
{ id: "orphans-dropped", port: "c", file: null, edit: null,
  // C emits via the compiled binary; see the shim below     <-- there is no shim
}
```

`grep -n "shim" negctl.mjs` returns **exactly one hit: the comment itself.** `sabotagePath()` returns `null` for `file: null`, so the sabotage is pushed to `results` as `{ skipped: "target file not present" }` and never runs. Then:

```js
const missed = results.filter((x) => x.detected === false);
return { ok: missed.length === 0 && restored, ... }
```

`skipped` records have `detected === undefined`, and `undefined === false` is **false** — so a sabotage that never executed is **not** counted as missed. `r.ok` stays `true`. The CLI prints `all sabotages detected; suite restored` and exits 0.

I imported the module and read the results directly:

```
ok: true | restored: true | baseline: 29 pass, 0 fail, 0 skip (of 29)
results: [ {setters-ancestry-inverted, detected: true, fails: 1},
           {setters-dropped,            detected: true, fails: 4},
           {orphans-dropped,            skipped: "target file not present"} ]
*** sabotages that did NOT execute: 1 of 3
*** r.ok is STILL TRUE: true
```

The skip is also **invisible in the CLI output** — the `SKIPPED:` line is only printed on the failure path, so the operator sees two `DETECTED` lines and the word "all".

**Why another agent should care — this is the sharp part.** The skipped sabotage targets **§5.4/§5.5 orphans/cycles**. That is *exactly* the clause where the fleet has a live common-mode misreading: `gitpp-v046-cases` measures `d38` as **4 of 5 ports wrong** (`py`/`js`/`cs`/`pl` orphan only the two cycle *members* and fold the downstream record normally; `gitpp-c` and the spec orphan it too). The one clause that is known to be misread by four independently-written ports is the one control that never executes.

**And the fleet's own documentation of negctl is false against the shipped artifact.** `gitpp-reading-room/FOUR-HARNESSES.md` states, under "What is now permanent":

> `negctl` has two harness-targeted sabotages, `harness-comparison-blinded` and `participant-silently-absent`.

**They are not on `main`.** Merged `main` is `3c602beb`; the two harness sabotages exist only on the **unmerged** branch `feat/harness-sabotages` (`c6c2bcec`, "negctl: two sabotage classes the fleet had never tested"). I ran that branch against the merged suite:

```
  DETECTED  setters-ancestry-inverted  (pl)  1 failures
  DETECTED  setters-dropped  (js)  4 failures
  DETECTED  harness-comparison-blinded  (js)  25 failures
  DETECTED  participant-silently-absent  (js)  29 failures
  restored: 29 pass, 0 fail, 0 skip (of 29)
```

**25 and 29 failures — exactly the numbers `FOUR-HARNESSES.md` claims.** So the control is real, correct, and *unshipped*, while a sibling document says it is permanent. The `harness-comparison-blinded` sabotage re-injects the original one-arg `cmp` into the **merged** suite and the suite correctly goes 25-red; `participant-silently-absent` replaces the JS wrapper with `process.exit(1)` and the suite correctly goes 29-red. Both fixes in the suite are load-bearing and demonstrably so.

**Negative finding on the CI.** `negctl` has **2 workflow runs ever, both `failure`**, both dying at step 6 (`clone the ports and suites as siblings`) with `fatal: could not read Username for 'https://github.com': No such device or address` — the clone step had no credentials. The author found this and fixed it in `42283f24` ("fix(ci): negctl has never run, and could not report its own failure"). But the fix **cannot be validated by CI**, because the workflow's PR trigger is:

```yaml
pull_request:
  paths: ['**/run.mjs', '**/wrappers/**', '**/cases.json']
```

`negctl` contains `negctl.mjs`, `README.md`, `package.json` and the workflow. **It contains no `run.mjs`, no `wrappers/`, no `cases.json`** — the filter was written against the *suites'* layout, not negctl's own, and negctl is a different repo from the suites it controls. The PR trigger is dead by construction. The only surviving trigger is the nightly cron (`41 5 * * *`), and the last cron run predates the fix. **The fleet's first negative-control lab has never once executed in CI.**

Two more structural notes: the workflow checks out the **branch** `fix/second-blind-spot` rather than `main`, with a comment ("main predates the comparator fix") that was true when written on 10-17T06:18 but is **stale** — `main` is now `3741c24d` (15:48) and *does* contain the fix (I confirmed the fixed comparator in a fresh clone of `main`). So every future change to `main` is un-controlled. And the README's example output still says `26 pass, 0 fail, 0 skip (of 26)` while the corpus is 29.

---

## 2. `gitpp-v046-cases` — the nine new conformance cases live in a stale copy of a harness that upstream already fixed

**What it is.** A copy of `gitpp-fold-conformance` with nine new cases `d30`..`d38` appended, pinning four clauses clarified in `git.pp-spec` v0.4.6. It is the *only* place the v0.4.6 clauses are executable. Its README is unusually good: it says the expectations are "a proposal, not a measured result", that "the failures are the findings", and that it refuses to silently rewrite cases it was not asked to touch.

**The defect.** `gitpp-v046-cases/run.mjs` is a snapshot taken **before** upstream fixed the comparator:

```js
// gitpp-v046-cases/run.mjs:170   (STALE)
const cmp = expectsSetters ? (a, b) => a === b : strip;
// gitpp-fold-conformance/run.mjs  (FIXED, on main)
const cmp = expectsSetters ? (a, b) => a === b : (a, b) => strip(a) === strip(b);
```

`strip` takes **one** argument, so for any case whose `expect` omits `setters`, `cmp(results, expected)` evaluates to `strip(results)` — a truthy string that **never inspects `expected`**. I confirmed the scope independently from the corpus: **25 of 29** pre-existing cases have no `setters` in `expect` (only `d26`–`d29` do).

**Verified, both directions, on the same corruption.** I replaced `d05`'s expected `state`/`order`/`conflicts`/`orphans` with `{"CORRUPT":1}` and `d26`'s with nonsense including a `setters` block:

| harness | d05 (no setters) | d26 (has setters) | tally |
|---|---|---|---|
| `gitpp-v046-cases` (stale cmp) | **PASS** ❗ | FAIL | 34 pass, 4 fail |
| `gitpp-fold-conformance` (fixed cmp) | **FAIL** ❗ | FAIL | 26 pass, 3 fail |

The stale copy reports a case as **passing when its expectation is literally `{"CORRUPT":1}`**. Upstream catches it. The fix is real and it is load-bearing.

**The CI can never go green — a second, independent defect.** `gitpp-v046-cases`'s workflow builds the C# wrapper with `-c Release`:

```yaml
- name: Build the C# derive wrapper
  run: dotnet build wrappers/CsDerive/CsDerive.csproj -c Release
```

and the runner it then calls hardcodes the **Debug** path:

```js
// gitpp-v046-cases/run.mjs:60
cs: (j) => run("dotnet", [`${ROOT}/wrappers/CsDerive/bin/Debug/net9.0/CsDerive.dll`], j),
```

So the C# port can never load. I reproduced both branches on a clean tree with all five ports built:

* CI's exact build (`-c Release`): **`0 pass, 38 fail, 0 skip`**, `run.mjs` **exit 1**.
* With a Debug build added: **`35 pass, 3 fail, 0 skip (of 38)`** — the README's headline number, reproduced exactly.

GitHub confirms the first: **1 workflow run ever, `completed failure`.** The upstream repo fixed this identical bug (it now checks `Release` then `Debug`, and documents it in a comment: *"The workflow builds it with `-c Release`, so a hardcoded bin/Debug path meant this port could never run in CI"*). The copy kept the bug.

**Third defect.** `gitpp-v046-cases/wrappers/CsDerive/CsDerive.csproj:6` hardcodes an absolute path:

```xml
<ItemGroup><ProjectReference Include="/tmp/gitpp-cs/src/Gitpp.csproj" /></ItemGroup>
```

Upstream resolves it at build time from `GITPP_CS_DIR` with a sibling fallback. The copy also hardcodes `sys.path.insert(0, '../gitpp-doctor')` (relative to CWD, not to the file) and `use lib "/tmp/gitpp-pl/lib"`. The README's "Reproducing" section does not mention the `/tmp/gitpp-pl` requirement, so following it verbatim leaves the Perl port dead.

**Honest accounting — what survives.** All nine **new** cases declare `setters`, so their comparison *was* exercised even in the stale copy. The d33 / d34 / d38 cross-port disagreements are therefore **real measurements**, not artifacts:

* **d33** — 2 ports wrong (`git.pp-doctor` py and `gitpp-js` pick `s-late`; `gitpp-cs`, `gitpp-pl`, `gitpp-c` and the spec pick `s-early`). They break the §5.2 tie-break on an *intent-ancestor count* instead of topo position.
* **d34** — `gitpp-cs` **crashes** with `System.ArgumentNullException` at `Gitpp.cs:215` (a `null` `kind` reaches a dictionary lookup); `gitpp-c` returns the wrong winner (ranks by ancestry).
* **d38** — **4 of 5 ports wrong**, the common-mode cycle misreading described in §1.

So: *the new findings are real; the old corpus carried along in that copy is vacuous; and the repo whose CI should have proven it is red on its only run.*

---

## 3. `gitpp-sheet` — the only calibrated-judge-into-propagation instrument in the fleet, whose integration job has never run

**What it is.** A fold rendered as a spreadsheet with **per-cell confidence**, plus the graph showing where the confidence came from. Jev (TypeSafe AI) supplies calibrated per-claim probabilities; the fold propagates them to cells. The design argument is the interesting part:

> Confidence is the **minimum** over the decisions that produced the cell, not the mean and not the product. A *mean* lets one uncertain decision hide behind many certain ones, which is how a confidence display becomes a lie. A *product* compounds independent decisions and understates certainty for a decision that is certain. The minimum is the honest summary of "what is the weakest link in the argument for this cell".

The cell's confidence is the confidence of the **decision that made it the winner** — which depends on the *losing* candidates too. A loser's uncertainty does **not** propagate. And the winner is read from the **conflict ledger** first, because a port that does not emit `setters` is legal: reading only `setters` would yield a sheet with null setters, no decisions, and therefore **100% confidence on every cell** — *"certain because it knows nothing, which is worse than no sheet at all."*

**Verified live.** I ran `live-demo.mjs` with a real `TYPESAFE_AI_TOKEN` against the real `spec/5-1-clarity` `SPEC.md` and both live ports:

```
  FOLD
    state     {"config.timeout":45,"status":"open","env.load":17,"cache.ttl":5}
    conflicts [{"key":"config.timeout","winner":"req-2","losers":["req-1","obs-1"]},
               {"key":"cache.ttl","winner":"twin-a","losers":["twin-b","unknown"]}]
    orphans   ["lost"]

  5 claims -> Jev (guarded)
    contradiction score 0.390 (floor 0.7)
    config.timeout:req-2:req-1   0.980  supported
    config.timeout:req-2:obs-1   0.980  supported
    cache.ttl:twin-a:unknown     0.360  needs-isolation
    cache.ttl:twin-a:twin-b      0.940  unreliable
    prop:unknown:kind            0.820  supported

  SHEET
    cache.ttl          5        task      36%  2 contested  <-- FRAGILE
    config.timeout     45        override  98%  2 contested
    env.load           17        witness  100%  settled
    status             "open"    task     100%  settled

  TRIGGERS
    unknown   touches ["cache.ttl"] at 36%
        action@0.55 -> apply=false required=0.75  binding=the cell confidence
        action@0.80 -> apply=true  required=0.75  binding=the cell confidence
```

The instrument produces exactly what it claims: the contested `cache.ttl` cell inherits the **minimum** (0.360), the uncontested `env.load` is 100%, and the trigger layer then **raises** the required action score for a fragile cell (0.75) versus a settled one (0.50). The sheet and the gate are used together, which is the point.

**The unit suite is good: 29/29 pass locally** (4 files, 0.34 s).

**But the CI is red on all four runs, and the job that matters has never executed.** Job breakdown of the latest run:

```
JOB: sheet (20) -> failure      step 4  Run npm test -> failure
JOB: sheet (22) -> success      step 4  Run npm test -> success
JOB: live          -> skipped
```

**Defect 1 — the matrix leg.** `package.json` says `"test": "node --test 'test/*.test.mjs'"`. The glob is **quoted**, so `sh` does not expand it. Node 21+ expands globs itself; **Node 20 does not**. The CI log says it plainly:

```
> node --test 'test/*.test.mjs'
Could not find '/home/runner/work/gitpp-sheet/gitpp-sheet/test/*.test.mjs'
##[error]Process completed with exit code 1.
```

Same command, same repo, same tree: **Node 22 → 29 pass; Node 20 → "Could not find".** The `live` job is `needs: sheet`, so it is **skipped on every run**. The workflow's own comment says why the live job exists — *"a green unit suite must not be mistaken for evidence that the integration works"* — and the live job has never run.

**Defect 2 — even with Defect 1 fixed, `live` goes red.** `live-demo.mjs:89`:

```js
writeFileSync("/tmp/sheet/live-graph.svg", renderGraph(sheet, records));
```

There is **no `mkdir` anywhere in the repository** (`grep -n mkdir live-demo.mjs demo.mjs src/*.mjs` → nothing). A fresh GitHub runner has no `/tmp/sheet`. I verified both branches:

| `/tmp/sheet` | result |
|---|---|
| absent (fresh runner) | `Error: ENOENT: no such file or directory, open '/tmp/sheet/live-graph.svg'`, **EXIT=1** |
| present | `wrote /tmp/sheet/live-graph.svg`, **EXIT=0** |

Two stacked one-line defects, and the only thing between the fleet and a green live integration job is a `mkdirSync`.

**Defect 3 — the demo can never run.** `demo.mjs:3` is a **static** import of an absolute path:

```js
import { derive } from "/tmp/rr2/readers/js/fold.mjs";
```

Static imports cannot read `process.env`, so there is no override. `node demo.mjs` → `ERR_MODULE_NOT_FOUND: Cannot find module '/tmp/rr2/readers/js/fold.mjs'`. The committed `graph.svg` in the repo was produced on the author's machine. (`live-demo.mjs` gets this right — it uses a dynamic import with an env override and *fails loudly* if the path is missing, with the comment *"A demo that silently falls back to a local path is a demo that can pass for the wrong reason — the same failure mode this project has now found in four harnesses."* The same discipline is simply not applied to `demo.mjs`.)

**Why another agent should care.** This is the only place in the fleet where a **calibrated probabilistic judge** (Jev) is wired into a **propagation structure** to produce per-cell uncertainty, and the fragility number it emits is honest (36% on a contested cell, 100% on an uncontested one). The *code* is good. What it demonstrates is a fleet-wide shape: **the substance is ahead of the harness, and the harness is where the fleet keeps losing.** 4 CI runs, 3 of them red, 1 job permanently skipped — for a repo whose live integration is the point.

---

## 4. `tool-judge` — a permission layer with a real security property, 189 tests, and no CI at all

**Zero mentions in 101 prior reports. Zero workflow runs, ever.**

**What it is.** Most permission systems are a list of command strings. That list does not know what any command was *for*, which project it belongs to, or whether it was approved for a laptop or a shared Jetson — so it either nags forever or you hand it the whole machine. `tool-judge` takes a **written statement of a project** (its rails, its hardware, its commitments) and derives permissions from it, at whatever scope fits:

```
$ tool-judge --rails .tool-judge.yaml --hardware orion-01 check jetson_clocks --show
  ALLOW  jetson_clocks --show
    from  grants: allow (hardware:orion-01)
$ tool-judge --rails .tool-judge.yaml --hardware orion-02 check jetson_clocks --show
  ASK    jetson_clocks --show
    from  grants: unlisted
```

Same grant, different machine, no longer applies.

**The one distinction** (the README's best line): **rails** enforce — deterministic, no model, cannot be wrong, *fail closed*. **goal-fit** advises — needs a model, can be wrong, *fails open*. *"An agent that asks a language model whether it may run `rm -rf` has built a suggestion box where it needed a wall. The model layer cannot make a thing safe."*

**Precedence: deny is a floor.** DENY at any applicable scope wins, then narrowest-to-widest for the rest. Deliberately **not** plain narrowest-wins, because plain narrowest-wins means opening a project folder could re-enable something you denied globally, and *"I opened a directory and lost my safety rails"* is not an acceptable failure mode. The cost is stated honestly: you cannot locally re-enable a denied command.

Six scopes that nest — `task` → `session` → `project` → `hardware` → `developer` → `user` — with `hardware` as the reason the tool exists (a command routine on a dev laptop can brick a board with one writable partition and no spare JTAG). Grants live in SQLite.

**Verified: the suite is real and it can fail.** 9 test files, **189 passed in 1.74 s** (pyyaml and pytest hand-installed from PyPI wheels — pip's resolver is blocked here, the JSON API is not). Mutation-verified:

| mutation | result |
|---|---|
| baseline | **189 passed** |
| unlisted → `ALLOW` (an empty allowlist becomes permission to do everything) | **6 failed**, 183 passed |
| `ASK` evaluated before `DENY` (deny stops being a floor) | **4 failed**, 185 passed |
| restored | **189 passed** |

The second mutation is the one that matters — it breaks the *security property the README claims*, and the suite goes red. This is the cleanest fail-first evidence I found in any repo this round.

**Structurally wrong: no CI.** A 189-test, security-relevant, mutation-verified suite with **zero** workflow runs. It passes — I checked — but nothing in the fleet will ever tell anyone if it stops. That is a strictly worse situation than a red CI: a red CI at least carries the information.

Two more things worth flagging. `LIMITS.md` is honest to an unusual degree: *"It is not a security boundary against a capable agent"* (the allow set includes interpreters — a rule saying "never delete from GitHub" does not stop an agent reaching the same outcome through Python; for a real guarantee, scope the credential), *"It is not sandboxing"*, *"The goal-fit judge is weak — measured, not assumed"*, and *"Unlisted means ASK, not ALLOW."* A controls file that only lists strengths is a press release; this one lists the limits first.

And a small structural oddity: the shipped rail file is `rails/g1-ble-backend.yaml` — named after a **different** fleet repo (`SuperInstance/g1-ble-backend`, pushed within the last day). One agent's permission policy is written against another agent's hardware, and nothing in the repo says where that rail came from.

---

## 5. `gitpp-reading-room` — the most methodologically novel thing in the fleet, and the best document the fleet has produced

**What it is.** Most conformance work answers *"do these implementations agree?"* This repo attacks the question underneath: **"is the spec saying anything?"** The README:

> Five fold ports agree on 20,043 records. That is a real result and it is bounded. It says the spec is *self-consistent* and that five implementations can hit it. It does not say the spec is *right*, because the spec, the corpus, the reference and the test runner were written by the same person.

**The method:** four readers, each given the spec and **forbidden from seeing any other implementation** — including implementations in their own language. Reader 2 is *deliberately pointed at the other defensible reading* of the precedence clause (ancestry-first, class as tie-break). Reader 3 is C99, where the type system forces ambiguities (bounds, overflow, codepoint vs byte). Reader 4 writes **no code at all** — an adversarial ambiguity atlas, clause by clause.

**The output is disagreement, not passes.** `FINDINGS.md`:

```
  determined by the spec : 14 / 19 probes
  UNDERDETERMINED        :  5 / 19 probes
```

and the framing that makes this a research artifact rather than a test suite:

> A disagreement here is not a bug report. It is a measurement: the spec does not determine the answer. Those are the clauses where two careful implementers will ship different systems and neither can say the other is wrong.

The five underdetermined probes are exactly the hard ones: `p07-orphan-descendant`, `p10-id-whitespace-and-separators` (is the id rule *enforced* or merely *documented*?), `p17-cycle-descendant`, `p18-descendant-of-orphan-vs-descendant-of-cycle` ("The PAIR that proves two clauses are needed"), `p19-self-loop-descendant`. Note that `p17` and `p18` are the same clause as `d38` — the independent reading room and the corpus converged on it from opposite directions.

It also contains `ELIXIR-EXECUTED.md`, `CORRECTION-signed-zero.md`, `EXPECTATION-AUDIT.py`, `NEGATIVE-CONTROLS.md`, `FOUR-HARNESSES.md`, `MERGE-LOG.md`, `JEV-CAPABILITY-MAP.md` — a working notebook, not a product.

**`NEGATIVE-CONTROLS.md` opens with the rule this whole scout series keeps re-deriving from scratch:**

> **A harness that cannot produce a failure is indistinguishable from a harness that is passing.**

It then lists every claimed number in the project next to the sabotage that moves it — including the ones that are still unverified, with the line *"a controls file that only lists passes is a press release."* The `fuzz.mjs` control is the gold standard: sabotaging one leaf per batch moves the count by **exactly** the batch count (**11** at `BATCH=2000`, **81** at `BATCH=250`) — predictable in magnitude, so a control that moves the number unpredictably is visibly measuring something else.

**`FOUR-HARNESSES.md` is the best document in the fleet and it is the thesis of this series, stated better than I have stated it in 100+ reports:**

> None of the four is a bug in the thing being tested. All four are bugs in the thing doing the measuring, and all four produce a number indistinguishable from a pass.

and the observation that is the most transferable thing I read this round:

> **Every negative control in this fleet sabotaged an IMPLEMENTATION. None sabotaged the *expectations*.** If all ports are correct and agree, corrupting the corpus is invisible. And blinding the comparator is invisible too, because the port-to-port check still passes. The control that was missing is obvious in hindsight and was never written: **corrupt the expected values and require a failure.**

> **A number without a demonstrated failure is not a result. It is the absence of a complaint, and the absence of a complaint is exactly what a broken instrument looks like.**

**But two things are wrong with it.** First, the `negctl` claim in "What is now permanent" is **false against shipped `main`** (see §1) — the two harness sabotages are on an unmerged branch. Second, the document's own "numbers that are still unverified" section was **corrected in place**:

> **CORRECTED — this was wrong.** `gitpp-doctor` is the clone *directory* name in the conformance workflow, not a repository. The five ports are c, `git.pp-doctor`, js, cs and pl, and all five are real.

A repo that publishes its own corrections is rare and worth trusting slightly more than the rest.

---

## 6. Briefly, also worth a look

**`gitpp-oracle`** — continuous cross-port differential conformance with an append-only ledger and a `known-limitations.json` contract: the oracle exits 0 while *only* known divergences persist and non-zero the moment anything else appears. Its README calls out the exact defect class: *"An earlier draft mapped an unparseable suite result to `green`. That converts a broken harness into a passing badge — the same defect class that produced seven false-green suites in this project."* The known-limitation entry for `perl-float64-domain` is a genuinely good artifact: JSON::PP destroys the information, so recovery needs a tokenising parser, and the entry says so rather than pretending the port can be fixed. *Not deeply verified this round.*

**`gitpp-rsi-audit`** — reading-room audit of arXiv 2610.13912 ("RSI-Anything"): does the text determine its own retention? No README, pushed today. *Not verified.*

**`coach-player`** (2 days old, zero prior mentions) — "You don't play the character. You *coach* it." A coachable auto-player whose audience is explicitly "super clever middle-schoolers into the technology itself", where the real curriculum is **nudging**: every coach order must show its effect (which dial moved, which trait fired, what the avatar remembered), because *"hidden magic teaches nothing."* And the owner rite: after a session the avatar proposes sheet edits and the player approves, edits, or rejects each one — *"the avatar only becomes who the player ruled it became. Nudging is temporary; ruling is permanent — that distinction is the lesson."* That is the `ruv/Fable`-style character-diff loop, stated as a learning loop. *Not verified.*

**`gitpp-v046-cases` and `gitpp-fold-conformance` both still check out `git.pp-doctor` as `gitpp-doctor`** — the Python reference port's real repo name is `git.pp-doctor`. The clone *directory* is named `gitpp-doctor`; the port is `git.pp-doctor`. `gitpp-reading-room` initially got this wrong and corrected it. Easy to get wrong; worth stating.

---

## 7. The pattern across all six

Three of the six are **the same defect reproduced in three different repos**, and it is the one this series has been circling for 100+ reports:

1. A check that cannot fail, in the thing doing the measuring.
2. A green badge that is green because the job that would have been red **never ran**.

| repo | what never ran | why |
|---|---|---|
| `negctl` | the whole control | CI dies at the clone step; the PR path filter matches no file in the repo |
| `gitpp-v046-cases` | the C# participant | CI builds `Release`, the runner looks for `Debug` → 0 pass, 38 fail |
| `gitpp-sheet` | the `live` integration job | the Node 20 matrix leg fails on an unexpanded glob → `live` is `skipped` |

And in every case the **substance was already good**: negctl's controls are correct (25 and 29 failures, exactly as documented); `gitpp-v046-cases`'s new cases are genuine measurements; `gitpp-sheet`'s live pipeline produces a correct 36%-fragility verdict against the real spec. **The fleet is not failing at the science. It is failing at the last mile between a working artifact and a check that can fail.**

**The one-line fixes, for whoever picks this up:**

* `negctl`: `file: null` → a real target, and `missed` must include `x.skipped` and `x.error`. **Until then negctl says "all sabotages detected" about two thirds of its sabotages.**
* `negctl` CI: the `paths:` filter must match files in `negctl` (or be removed), and the checkout should follow `main`.
* `gitpp-v046-cases`: re-sync `run.mjs` from `gitpp-fold-conformance` (or delete the repo and work upstream) — and the C# config, and the `csproj` path.
* `gitpp-sheet`: `mkdirSync('/tmp/sheet', {recursive:true})` before the write, and drop Node 20 from the matrix (or unquote the glob).
* `tool-judge`: add CI. The suite already passes; it just needs a witness.

---

## 8. Method corrections (carry forward)

* **`grep -n "shim" negctl.mjs` → 1 hit, and it is the comment claiming the shim exists.** A comment that names a mechanism is a claim about the artifact. Always `grep` for the thing the comment promises.
* **A `skipped` result is not a `detected` result.** `results.filter(x => x.detected === false)` does not catch `{skipped: ...}` because `undefined === false` is `false`. Any gate that aggregates a list of controls must decide explicitly what "did not run" means. It is almost never "fine".
* **A quoted glob in an npm script is a Node-version gate.** `node --test 'test/*.test.mjs'` passes on Node 21+ and fails on Node 20. A CI matrix over Node majors silently turns a glob into a compatibility test.
* **`needs:` turns a red matrix leg into a permanently skipped job.** A job that has never executed is not a passing job. Check `skipped` in the jobs payload, not just the badge — the badge shows the matrix conclusion, not the skipped job.
* **A PR path filter is written against one repo's layout.** When a control repo watches *other* repos, `paths:` in its own workflow can never match. Cross-repo control needs a schedule or a dispatch, not a path filter.
* **A copy of a harness is a fork of its bugs.** `gitpp-v046-cases` is a copy of `gitpp-fold-conformance` taken *before* the fix. When a repo forks a harness, diff the harness, not just the corpus.
* **A "Reproducing" section that omits one path requirement is a broken reproduction.** `gitpp-v046-cases` documents the sibling clones but not `/tmp/gitpp-pl`, so the Perl port is dead on a clean machine. Grep the wrappers for absolute paths and check every one is mentioned in the docs.
* **A control's own documentation is not evidence about the control.** `FOUR-HARNESSES.md` correctly described two sabotages that exist only on an unmerged branch. Read `main`.
* **Positive controls belong in the same table as negative ones.** `gitpp-reading-room`'s `NEGATIVE-CONTROLS.md` pairs every claimed number with the mutation that moves it, **and lists the numbers still unverified**. That is the standard. Every repo in this report that has a receipt suite should have one.

**Environment notes.** NAS `/workspace` is at 100% quota (500G/500G) — all scratch work went to `/tmp`. PyPI's **resolver is blocked but the JSON API is not**: `https://pypi.org/pypi/<pkg>/json` + `files.pythonhosted.org` yields wheels that install by hand into a `PYTHONPATH` dir (pytest 9.1.1 + pyyaml 6.0.3 + iniconfig + packaging + pluggy + exceptiongroup + tomli + pygments). `gh` is not installed; the REST API via `curl` + `GITHUB_TOKEN` covers everything. `GIT_SSL_NO_VERIFY=1` is required for clones. gcc 12.2, perl 5.36, dotnet 9.0.316, node 22.19, python 3.11 all present; no cargo/rustc/julia, so the Rust and Elixir ports were read, not run — `gitpp-reading-room/ELIXIR-EXECUTED.md` is the fleet's own note that the Elixir patch *"is pushed and has never been executed."*
