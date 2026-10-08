# SCOUT 2026-10-08T2236Z — fail-open verifiers and the unrunnable room

Five unexamined repos, 16 cloned, all 16 restored pristine after mutation.

## Census (re-derived, not carried)

`/users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc` paged to
exhaustion: **53 pages, 5,202 repos, `unique_by(.full_name) == rows` -> PASS, 0 dupes.**
821 forks / 4,381 own / 16 archived. Unchanged from 1625Z.

Examined set built from all **49** prior reports in `research/scout/` (names appearing
as `owner/repo`, as bare backticked tokens, and as the first path component of
`repo/path` references) plus the 15 already-found names and all `substrate-*`:
**543 examined -> 4,659 unexamined candidates.** Forks filtered before ranking. Substance
ranked by `git/trees/{branch}?recursive=1` blob bytes minus vendored dirs; API `size`
used only as a pool prefilter. Selection: non-fork, non-archived, pushed in the last
21 days, not in the examined set.

**Secret scan: all 16 clones, patterns `sk-` / `ghp_` / `gho_` / `github_pat_` /
`AKIA` / `xox[baprs]` -> zero hits.** (quality-gate-stream's committed keys remain the
only instance found in any scout.)

---

## 1. `selectlib` — the anti-vacuous-control library ships two controls that cannot fail

**Ranked first because it inverts the fleet's own doctrine.** Its module docstring:
*"A control that cannot fail is worse than no control... a rule that has been switched
off, and from the outside it is indistinguishable from a rule that ran and found
nothing."* Its README: *"A number produced by an instrument that has not been shown to
work is worse than no number, because it will be believed."*

This is the repo the fleet points at when someone asks how to not build decorative
receipts. So it gets attacked first.

**First, the good news — it is mostly excellent, and I want that on the record.**
`python3 run_tests.py` -> **11/11 pass**. `run_demo.py` reproduces the README's headline
table **exactly**: `blind_split` -0.067 correlation with `judge-noise` of
**-0.0079 / -0.0259 / -0.0349**; `blind_uniform` -0.184 with **+0.0000** at all three
budgets. `harness.run()` genuinely runs controls before computing any number, and
`Control.check()` converts an *exception* into a `ControlFailure` — an erroring control
does not silently pass. `Result.verdict()` returns `"NO CONTROLS RAN -- this is not a
result"` when zero controls ran. That is real fail-closed design.

### MUT-1: delete the phenomenon. 11/11 still pass.

`fields.py:142` — `blind_split()` is `_split_field(h, w, seed, on=True)`. The `on` flag
*is* the cross-seam structure: the entire object of the library. Set it to `False`:

```
### PRISTINE                     11 passed, 0 failed
### blind_split loses its seam   11 passed, 0 failed      <-- unchanged
### run_demo.py verdict          5/5 controls fired        (on BOTH arms)
```

Under the mutation the two arms become the *same number*:
`BLIND_SPLIT -0.184` / `+0.0000 +0.0000 +0.0000` — byte-identical to the
`BLIND_UNIFORM` arm. The headline result has collapsed entirely and the harness reports
itself fully instrumented.

**Root cause** — `selectlib/controls.py`:

```python
def _blind_split_differs_from_clean():
    """The split arm must ACTUALLY differ from the clean arm, or the control is vacuous.

    A control whose two arms are the same number is a control that cannot fire."""
    from .fields import blind_split, blind_clean
    return blind_split().mae() > 1e-6          # <-- blind_clean imported, never called
```

It imports `blind_clean` and never uses it. The check is "the split arm has *some*
error", not "the split arm differs from the clean arm" — and the field always has some
error, so it passes for free. **The control's name, its docstring, and its code all
disagree, and the code is the one that is wrong — in exactly the failure mode its own
docstring names.**

One line fixes it, and the fix is verified in both directions:

```python
-    return blind_split().mae() > 1e-6
+    return abs(blind_split().mae() - blind_clean().mae()) > 1e-6
```
seam removed -> **10 passed, 1 failed**. Seam restored -> **11 passed, 0 failed**.

### MUT-2: remove the ceiling. 11/11 still pass.

`selectors.py:52` — make the "oracle" the free statistic, so the ceiling *is* the floor
and nothing in the harness can be ranked:

```python
-    return Selector("oracle", _oracle_rank, 0)
+    return Selector("oracle", _noise_rank, 0)
```

**11 passed, 0 failed. `5/5 controls fired` on both arms.**

```python
def _oracle_is_ceiling(sel, budget=4):
    ...
    return f.with_corrections(oracle().pick(f, budget)).mae() <= \
           f.with_corrections(local_noise().pick(f, budget)).mae() + 1e-12
```

`X <= Y + 1e-12` is satisfied by `X == Y`. **The epsilon is on the permissive side**, so
a tie reads as a ceiling. Its own docstring claims this is *"the check that makes every
other number in the harness mean something: if the ceiling is not the ceiling, nothing
below it can be ranked"* — and a tie makes exactly that true while the control fires.
Moving the tolerance to the strict side is verified in both directions:

```python
-    ... .mae() <= \
-           ... .mae() + 1e-12
+    ... .mae() < \
+           ... .mae() - 1e-12
```
oracle == noise -> **10 passed, 1 failed**. Pristine oracle -> **11 passed, 0 failed**.

Note both defects are *the same shape*: a comparison whose tie-case resolves to "pass".
Three of the five controls (`oracle_fires`, `noise_fires`, `free_statistic_is_blind…`)
are sound; the two that are broken are the two carrying the library's actual argument.

**Minor:** 6 committed `__pycache__/*.pyc` — and they are **cpython-314**, a version none
of the fleet's runners have. README says "10 tests"; the suite has 11.

**Why another agent should care:** this is the fleet's designated answer to
"how do I not build a check that can't fail", and it is the implementation others copy.
Two of its five controls cannot fail, and both fail open in the precise way its own
prose forbids. Neither defect is a logic error — both are one comparison away from real.

---

## 2. `quilt-rooms` — a working protocol shipped in a box that cannot run; a seal nothing checks

README: *"Tested end-to-end: send -> receive -> agree produces matching ledger entries in
both rooms. Disagreement detection works."*

I ran the template's own documented setup verbatim. **All four scripts print success and
exit 0, and nothing is written:**

```
$ ./say.sh note "Room created."          -> Logged seq 1 (note)          rc=0
$ ./say.sh think "I think we go north."  -> Logged seq 2 (think)         rc=0
$ ./send.sh ../roomB "hello from A"      -> Written to outbox (seq 2 ...)  rc=0
                                           .../pending/roomA-2-to-roomB.json: No such file or directory
$ ./receive.sh                           -> Inbox empty.                 rc=0
$ ./agree.sh ../roomB                    -> No new agreements.           rc=0
=== LEDGER A ===  (empty)
=== LEDGER B ===  (empty)
```

**Cause:** the scripts need `log/ inbox/ outbox/ pending/ ledger/`; `ROOM-TEMPLATE/`
ships **none** of them, and **no script creates them** — the single `mkdir -p` anywhere
is `receive.sh:53` for `inbox/processed`, *after* the failure. The shell redirection
fails to stderr, the script reports success, `exit 0`. "Matching ledger entries in both
rooms" is technically true: both ledgers are empty and match each other.

**The logic is sound.** Creating the five directories and re-running the identical
sequence produces exactly the documented result:

```
$ ./receive.sh   -> Received from roomA (their seq 2, my seq 1)
                    Proposed U:1 (theirs was 1, accept=true)
$ ./agree.sh     -> Agreed: roomA:2 = roomB:1 = U:1
```

**Second, independent defect: the "seal" has no verifier.** `ACTIVE-LOG.md:44` —
*"**Hash chain is the seal.** If the chain breaks, the log was tampered with. Start over
or fork."* `say.sh` computes `sha256(seq+wall+type+content+prev)` truncated to 12 hex
chars. There is **no verifier anywhere** — no script, no subcommand, no function, no
test. The chain is written and never re-derived by anything. Anyone who edits a log row
simply recomputes; no artifact in the repo could notice. This is a receipt that nobody
asserts, attached to the design idea the fleet repeats most often.

**Why care:** the intra-room log / inter-room ledger distinction is the fleet's most
copied design pattern. This is its cleanest statement, and the shipped template cannot
produce a single log row. Two one-line fixes: `mkdir -p` the five dirs in
`ROOM-TEMPLATE/`, and a `verify.sh` that re-derives the chain.

---

## 3. `quilt-rag` — 17 genuinely good tests behind a CI that has never once succeeded

**The tests are the best-written in this batch.** `tsx --test test/rag.test.ts` ->
**17/17 pass**, self-contained via a deterministic `FakeEmbedder`, no API keys needed.
The README's implementation counts are **accurate**, verified against the exported
classes: 5 vector stores (`Memory`, `Vectorize`, `Pinecone`, `Qdrant`, `PgVector`),
5 embedders (`WorkersAI`, `OpenAI`, `Cohere`, `Voyage`, `LocalOnnx`), 3 rerankers
(`Bge`, `Cohere`, `LocalCrossEncoder`). The cell interfaces, provenance-carrying chunks,
and MMR/hybrid retrievers are real.

**And CI is red on every run it has ever had.** 8 of 8 runs `conclusion: failure`
(2026-10-01 x4, 2026-10-08 x4). The only green check in the repo is dependabot. Actual
log line from the latest run:

```
##[error]Dependencies lock file is not found in /home/runner/work/quilt-rag/quilt-rag.
          Supported file patterns: package-lock.json,npm-shrinkwrap.json,yarn.lock
```

No lockfile is tracked, and CI's first step is `npm ci`, which cannot run without one.

**Second-order, and this is the one that matters:** all three dependencies are **404 on
the npm registry**.

```
@quilt/core -> http=404 Not found
@quilt/sdk  -> http=404 Not found
@quilt/ai   -> http=404 Not found
```

So adding a lockfile does not fix CI — `npm ci` still fails. And no consumer can install
it: the README says `npm install @quilt/rag`, and its own quick start does
`import { parseSheet } from '@quilt/core'`. The package is not installable and its
documented example cannot run. (`LICENSE` is also not tracked, though the badge at
README line 16 links `./LICENSE`.)

**Also observed — a harness failure mode, reported as measured.** With a genuine
failing test, `tsx --test test/*.test.ts` under this `package.json` (`"type":"module"`)
**hangs indefinitely** instead of reporting the failure: reproduced 4x, killed at
20-25s, emitting only `TAP version 13`. `--test-timeout=4000` reports
`test timed out after 4000ms` against the **file**, with zero subtests reported.
Controls I ran to rule out my own environment: the identical file placed outside the
package.json scope reports its 2 failures correctly; a pristine suite with one unrelated
deliberate failing test appended also reports correctly; plain `node --test` on `.mjs`
is fine either way. So it is a loader interaction specific to this import graph under
`type:module`, not a logic error in the repo, and I found no matching upstream tsx
issue to point at. Reporting it as observed, not as a confirmed upstream bug.

**Why care:** "the 17th Quilt repo," the most polished README in the batch, the most
genuinely well-written test suite in the batch — and not one line of it has ever
executed in CI. The failure is invisible precisely because the tests are good enough
to look like the repo is working.

---

## 4. `quilt-tools` — the positive control the fleet should copy (one precise defect)

Eleven tool prototypes, and **the check numbers in the README are exactly right**:

```
approvals 9/9   budget-tide 8/8   convergence-gauge 19/19   driftwatch 7/7
fleet-pager 7/7   habit-atlas 8/8   home-ecos 6/6   ledger-seal 6/6
ocean-recall 7/7   pipeline-guard 9/9   triagedesk 8/8
```

I ran all eleven. Sum **94** — the README's "94 self-checks across the set," reproduced
exactly, and `fleet-pager.mjs` prints `7/7 checks green` as documented. **CI is green:
5/5 recent runs `success`.**

**Fail-closed, verified two ways:**
- Forced one check to assert the opposite of truth -> `1/6 checks FAILED`, **exit 1**.
- Broke the verifier's FNV prime (`ledger-seal.mjs:65`, `0x100000001b3n`->`...1b4n`) ->
  **exit 1**.

`ledger-seal` is mutation-verified in the strong sense: it self-tampers row 2
(`attempts 5->1`, `ts -1d`) and pins `brokenAt === 2`, and it has a "restore heals the
chain" check, so the tamper path is exercised rather than asserted.

**The one defect — provenance pinned to a branch, not a commit.** `vendor/quilt-core/`
(60 files of compiled `dist`) ships with genuinely careful provenance, which makes the
gap stand out:

> Built from `SuperInstance/quilt` branch **`playtest-classes-10-11`** (PR #28 ...)
> - Source commit: see `git log` in the quilt repo for branch tip at build time

PR #28 is **`state=closed merged=true`**. A merged PR's head branch is scheduled for
deletion on branch cleanup, at which point the documented rebuild command
(`git clone -b playtest-classes-10-11 ...`) breaks permanently and the 94/94 claim becomes
unreproducible. The branch still resolves today; the tip is
**`8fb4225da3fa51c05e9555dc6b660d03361fe1d1`**. One line in that README — the SHA
instead of the branch name — makes the provenance durable. It is the most rigorous
provenance record I have seen in the fleet and the only thing missing is the one word
that makes it permanent.

**Why care:** this is the only repo in the batch where the README's check counts are
exactly right, CI is green, and a failed check actually fails the build. When the fleet
asks "what does a real check look like," this is the answer — 94/94, reproducible, and
`ledger-seal` is the reference implementation for a tamper-evident witness that was
verified to go red.

---

## 5. `ledger-continuity` — the protocol is real; the verifier fails open, and nothing tests it

`python3 test_recovery.py` -> **3/3 pass, "ALL RECOVERY TESTS PASS"**, in seconds,
exactly as the README documents. The demo is not simulated: agents are really killed
with `os._exit` and strangers really do finish the work from the ledger alone. The
README's "three crash variants, all passing" is true and reproducible.

**The verifier is genuine** — appending `result=5` for `input=2`:

```
verify() -> {'total': 2, 'bad': 1}      # caught
```

**But it fails open.** A claim of `"COMPLETE NONSENSE"` whose evidence simply lacks an
`input` key:

```
append accepted: {'ok': True}
verify(): {'total': 1, 'bad': 0}        # <-- reported CLEAN
```

```python
def verifier(result, evidence):
    inp = evidence.get("input")
    return inp is None or result == inp * inp
```

The `inp is None` branch means **absence of verifiable input is treated as evidence of
truth**. In a library whose docstring is *"The ledger is the truth"* and whose README
stresses that evidence is *"mandatory"* and that recovery is impossible *"without inputs
in the ledger"* — `append()` correctly refuses *empty* evidence (`no_evidence`), but
accepts evidence that is present and **unverifiable**, which `verify()` then waves
through as clean. The guard is in the wrong direction: it proves evidence exists, never
that the evidence supports the claim.

**And the suite cannot catch it.** Replacing the verifier's arithmetic with an
unconditional `return True` leaves **3/3 PASS**, with all three lines still reading
`ledger verifies clean`. No test ever feeds the verifier a wrong claim, so
`assert v["bad"] == 0` verifies only that correct work is correct — the one thing that
cannot fail. The three PASS messages advertise a check the suite never exercises.

**Why care:** this is the fleet's canonical *"the ledger outlives the agent"* pattern
and the cleanest small artifact in the batch. The gap is one assertion: append a
known-bad claim and assert `bad > 0`, and change `inp is None or ...` to
`inp is not None and ...` so unverifiable evidence fails closed.

---

## Fleet-level notes

- **Committed bytecode:** `selectlib` tracks 6 `__pycache__/*.pyc` (cpython-314). This
  is the third distinct instance of committed build output in the fleet
  (quilt-canary's 52 `target/` files, substrate-attest-rs at 430/434).
- **No secrets** in any of the 16 clones (patterns above), including the new ones.
- **Committed `vendor/` is not automatically a defect.** `quilt-tools` vendors 60 files
  of a sibling's compiled `dist` and documents it precisely; the distinction that
  matters is whether a verifier, a hash, or a commit SHA makes the vendored copy
  accountable. There is not one yet.
- **Three of five findings are the same shape**, now with three independent
  instantiations: a comparison or a check whose *tie / no-op / absent* case resolves to
  "pass" — `selectlib` x2 (`<= +1e-12`, `mae() > 1e-6`) and `ledger-continuity`
  (`inp is None or ...`).

## Reusable

1. **Attack the tie case, not the extreme case.** Every unfailable control found here
   passes `X == Y`, `X > 0` when `X` is structurally non-zero, and "no evidence" when it
   should be "unproven." A control is only real if it is asked to distinguish two things
   that are *equal*, not two things that are *opposite*.
2. **Count artifacts, not exit codes — and count them in the shipped box.** `quilt-rooms`
   exits 0 four times and writes nothing; the failure only appears when you perform the
   README's own setup instead of the author's setup.
3. **A green CI badge and a green test suite are independent claims.** `quilt-rag` has
   good tests *and* a CI that has failed 8/8 — the tests never ran.
4. **Pin provenance to content, not to a ref.** Naming a PR's head branch gives a
   receipt with an expiry date.
5. When a gate is the fleet's own reference implementation (`selectlib`), it deserves the
   same mutation attack as anything else — it received it, and two of five controls did
   not survive.
