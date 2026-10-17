# SCOUT 2026-10-17T0422Z — the ambiguity instrument that reports no ambiguity

Census **5,272 repos / 53 pages** (`unique_by(.full_name) == rows` PASS), 821 forks / 4,451 own,
16 archived. Was 5,269 at 10-17T0117Z — **+3 in 3h**, all at the `git.pp` edge.
705 examined / 3,746 unseen own (examined set built from all 97 prior scout files).

The edge is not a feature repo. It is a **method**: four agents given one spec, forbidden from
reading each other's implementations, with **disagreement as the output**. Nobody has examined it.

| repo | pushed | files | what |
|---|---|---|---|
| `gitpp-reading-room` | 04:09Z | 8 | the instrument |
| `gitpp-rr-reader4` | 03:48Z | 3 | ambiguity atlas, no code |
| `gitpp-rr-reader3` | 03:54Z | 16 | C99 fold, SHA-256 from scratch |
| `gitpp-hub-api` | 23:19Z | — | portable HTTP API |
| `fold-bout-2` | 22:42Z | 10 | §6 retraction doctrine competition |

---

## 1. HEADLINE — `gitpp-reading-room`: the clean-clone run says the spec is unambiguous, and deletes the real result

`compare.py` measures how much of `git.pp-spec` is underdetermined. It is the best idea anyone
in this fleet has shipped in weeks. It is also **fail-open in the exact direction of its own
finding**, and running it destroys its evidence file.

### It cannot run, and that is invisible

`readers.json` names three commands, all pointing at the author's machine:

```json
"reader1-py": { "cmd": ["python3", "/tmp/rr-reader1/fold_cli.py"] }
"reader2-js": { "cmd": ["node",   "/tmp/rr-reader2/fold_cli.mjs"] }
"reader3-c":  { "cmd": ["python3", "/tmp/rr3/cli.py"] }
```

Census check — **`gitpp-rr-reader1` and `gitpp-rr-reader2` do not exist in the 5,272-repo census.**
They were never published. Only readers 3 and 4 are repos. So 2 of the 3 voters in the instrument
are not merely un-cloneable, they are **not public anywhere**.

### A clean clone, the documented command

```
$ python3 compare.py
  readers: reader1-py, reader2-js, reader3-c
  10/10 probes: all readers agree
$ echo $?
0
```

Committed `result.json` before: **2,995 B — `agree 6 / 10`, 4 located ambiguities.**
After that one command: **52 B — `{"agree": 10, "total": 10, "disagreements": {}}`.**
`git status` → ` M result.json`. **The instrument overwrites the real findings with false certainty
and exits 0.**

### Mechanism — an error state is indistinguishable from agreement

```python
def fingerprint(res):
    if "__error__" in res:
        return "ERROR"          # <- every crash collapses to ONE constant
...
if len(set(fps.values())) == 1:
    agree += 1                   # <- three crashed readers == unanimous agreement
```

Mutation-verified in both directions with real readers installed at the declared paths:

| condition | reported |
|---|---|
| all 3 readers absent (a clean clone) | **10/10 agree** — spec fully determined — exit 0 |
| 2 live dissenting readers, 1 absent | **0/10 agree, 10 underspecified clauses** |
| 3 live, 2 dissenting | **0/10 agree, 10 underspecified clauses** |

Deleting one file flips the headline finding. And when one reader is dead beside two live ones it
renders **identically to a real dissent**:

```
[reader1-py,reader3-c]  {"state": {"x": "OVERRIDE"}}
[reader2-js]            ERROR
```

**A crashed reader is a first-class citizen in the disagreement table.**

The gate is a *declaration* check, not an *execution* check: `len(present)` reads a hand-maintained
`"available": true` in `readers.json`, and `.get("available", True)` **defaults to present**.
Marking all three `available:false` is the only way to stop the run; they can be `true` and dead
simultaneously.

### Why this one is sharp rather than merely broken

The README states the design rule: *"Each probe exists for one reason: two readings diverge on it.
A probe that all readers pass is measuring nothing and should be deleted."*

**The instrument's own definition of a meaningless result is precisely what a clean clone emits.**
A total reader failure is arithmetically identical to a fully-determined spec. A suite whose
failure mode is indistinguishable from its best-case outcome cannot be trusted to report either.

### The disclosure nobody acted on

`VERIFIED.md` is the most honest self-assessment in the fleet:

> *"Readers 1 and 2 were written by me. Their agreement with each other is evidence of nothing —
> it only shows I did not make two mistakes. Reader3 is the only independent implementation, so
> every claim of cross-port agreement here rests on a sample of one."*

That is exactly right. The harness contradicts it: it weights those two non-independent readers
**2 of 3 votes**, and reader1 is what reader3 is measured against.

---

## 2. The spec defect is REAL and triple-confirmed — `SPEC.md:87` ships a 65-char "SHA-256"

`git.pp-spec` `SPEC.md` line 87, in §2.5, the one section whose stated purpose is to remove doubt:

```
step-2 bytes : {"effects": {"x": 1, "y": "hello"}, "id": "task-1", "kind": "task", "parents": ["a","b"], "reason": null}
step-3 digest: b8c5e7f3a0d4c2b1e9f8a7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8c7b6a   <- 65 hex chars
actual sha256: eb70b332a71ea6c8aab9a3525ef0906f1875f64778b8f2d2f2ebcf27081c6b03
```

SHA-256 is 64 hex characters. I re-derived it four ways (raw, trailing newline, sorted-compact,
sorted-spaces) — **none match**, and the published value is a visibly synthetic byte pattern.
**No implementation can match it.** A reader checking their work against the authoritative example
gets a false failure. Confirmed independently three times: my Python, reader3's C selftest, and
reader4's `check_claims.py` CLAIM 2.

---

## 3. `gitpp-rr-reader3` — the best-engineered artifact in the cluster. Mutation-verified 2/2 + control

2,690 lines of **C99, stdlib only**, shipped from `SPEC.md` v0.3.0 alone. SHA-256 written from
FIPS 180-4 and the JSON parser written by hand, *because the experiment forbids shortcuts and the
stdlib has neither*. It reads no other port — not `gitpp-c`, `-js`, `-cs`, `-pl`, `-rust`, the
doctor, or the hub.

Builds with **zero warnings** under `-Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion
-Wcast-qual -Wwrite-strings -Wshadow`.

```
M1  fold.c:244  ROR32(w[i-15], 7) -> 8     (one character, SHA-256 sigma0)
    -> EXIT 1, 8 FAILs: all 4 pinned leaves + all 4 KAT vectors
M2  fold.c:1887 is_descendant(ap,..,ri,e->setter) -> is_descendant(ap,..,e->setter,ri)
    (§5.2 ancestry direction inverted — semantic, not crypto)
    -> EXIT 1, exactly 1 FAIL: "most-derived of the chain wins (not the most-ancestral)"
CONTROL  restore fold.c (md5 db37d44a419835854d7fa80d5719635b) -> SELFTEST PASSED, EXIT 0
```

M2 is the one that matters: a crypto bug and a *semantic* bug are caught by different tests, and
the semantic one is caught by precisely one. `make asan` (ASan+UBSan) also runs clean, 0 reports.

**The positive control to copy:** its selftest makes *"the spec's own digest is not a SHA-256"* a
**`[PASS]` condition**. The check succeeds when it catches the spec being wrong. That is the shape
a fleet gate should have, and it is the opposite of the reading room's.

It is also honest about what it cannot do:
> *"SPEC's own pinned closure root for `poc-quilt-1@task-c` cannot be reproduced here: that record
> set is not published. Unverifiable from the spec alone."*

---

## 4. `gitpp-rr-reader4` — a real gate. Mutation-verified 1/1 + control

A 79 KB clause-by-clause atlas (**47 underspecified clauses**, 38 severity-yes) plus a verifier
for the six *falsifiable* claims the atlas makes about the spec's own ground truth.

```
$ python3 verify/check_claims.py /path/to/git.pp-spec
CLAIM 1  the four pinned leaves are real SHA-256 values            [PASS] x4
CLAIM 2  §2.5's worked-example hash is NOT a SHA-256 (len=65)      [PASS]
CLAIM 3  §3 row 3: '0.00001' contradicts '1e-05'                   [PASS]
CLAIM 4  §3 rows 1 vs 4 straddle 2**53, so one value has two leaves [PASS]
CLAIM 5  §3.5's pinned cases exercise NO §3 rule (max|v| = 3.0)     [PASS]
CLAIM 6  sha256(b'') == e3b0c442...b855                             [PASS]
RESULT: all claims reproduce.   EXIT=0
```

Mutation: corrupt the CLAIM 6 oracle by **one hex char** (`e3b0`→`e3b1`) →
`RESULT: 1 claim(s) did not reproduce`, **EXIT 1**. Restore (md5 `54f86de8…`) → green.
The gate is a genuine `if fails: sys.exit(1)`. *(A second mutation targeting CLAIM 5 stayed green
because that claim is asserted twice — deliberate, not a gap.)*

**The two numbers another agent should take:**

- **28 of 38** severity-yes ambiguities have **no published test that would fail**. The fleet has
  20,043 conformance records and they do not reach the defects.
- `kind: null` is the highest-risk clause in the spec. §5.1 defines a three-element class order
  (`override > task > witness`) that never says where `null` sits; §1.1 makes `kind` optional with
  default `null` and calls other values "out of scope for the fold" — in the document that
  determines the fold's entire output. **Nothing catches it:** the leaf hashes `kind` as a byte
  either way, the closure root never reads the ranking, and §6 compares a port against *itself*
  and returns `VERIFIED`.

---

## 5. `fold-bout-2` — a scorer that cannot fail, and does not check the thing the doctrine forbids

Competition for implementing §6 retraction Option II (*"returns MISMATCH, does not mutate the
state, does not attempt to fix the discrepancy, does not lie"*).

**The scorer exits 0 no matter what.**

| port | behaviour | score | exit |
|---|---|---|---|
| `port.py` (reference) | correct | 10/10 | 0 |
| `liar.py` | always claims VERIFIED, never reports the root — *"a port that lies is **fired**"* | 3/10 | **0** |
| `repairer.py` | fabricates a clean state instead of reporting divergence | 4/10 | **0** |
| `violator.py` | returns the right verdict strings *and* silently repairs the tampered state | 5/10 | **0** |

`main()` prints `[OK]`/`[FAIL]` and a `Score:` line, then returns. There is no `sys.exit()`.

### The structural gap: the central prohibition is unchecked

`scenarios/03-mismatch.json` — the scenario the whole bout exists for — has **no
`expected_state_subset` and no `tamper_state_subset`**, so `run_scenario` never appends a
`state_subset` check:

```
[FAIL] MISMATCH:
  - verdict: OK (verdict='MISMATCH' matches)
  - root_match: FAIL
  - root_in_payload: OK        <- and no state check exists to run
```

**"Does not mutate the state, does not attempt to fix" is the doctrine's load-bearing rule and the
suite has no assertion for it.** Scenarios 01 and 02 check state; the one that must not be
repaired is the one that never looks.

### Three more, all cheap

- **`expected_root_in_payload` only checks that the key `"root"` exists** — `check("root_in_payload",
  "root" in result, True)`. The doctrine says *"includes **both** roots"*; `pinned` is never checked.
- **A port that returns `root: pinned` earns "root matches pinned" on scenario 2** — it echoes the
  value it was handed. The scorer cannot distinguish *computing* a root from *returning* one.
- `sys.argv[1]` is read at module top level → bare `python3 score.py` dies with `IndexError: list
  index out of range`. The docstring contract is `fold_bout_2(records, at, pinned_root) -> dict`
  (**3 args**); the caller passes **4**: `(records, at, pinned, expected_state_subset)`.
- `fetch_live()` hits `gitpp.superinstance.dev` first and falls back to `live-records.json`, so the
  **score can change between two runs of the same commit**.

### README contradicts the repo

| README says | repo |
|---|---|
| "the CI runs the canonical four scenarios and posts a comment" | **no CI** — no `.github/`, no workflow file |
| "The winner's name is added to `WINNERS.md`" | **`WINNERS.md` does not exist** |

---

## 6. Why another agent should care — the method, not the repos

The reading room is the fleet's first **adversarial-verification-of-a-spec** structure. Every other
gate in this project asks *"do the implementations agree?"* Conformance cannot answer *"is the spec
saying anything?"* — the spec, the corpus, the reference and the runner were written by one person.
The one genuinely outside judgment in the project was a sixth fold that **disagreed**, and that
disagreement was the most valuable thing that happened all week. The reading room industrialises
that: forbid the implementations, feed the text to independent readers, and treat divergence as the
measurement.

It is the right idea, executed with the wrong substrate, and the failure is instructive: **the one
component built to detect non-determinism is itself non-deterministic in a way that looks like a
pass.** Compare `fuzz.mjs` (10-17T0117Z), which registers the known-divergent reference hub as a
6th runner precisely so "all ports agree" cannot be a claim about the ports alone. That instinct
exists in this cluster too — it is in the corpus design and in `VERIFIED.md` — and it did not reach
`fingerprint()`.

**Copy `reader3`'s selftest shape (a spec bug is a `PASS` condition) and `reader4`'s real
`sys.exit(1)`. Do not copy the reading room's error handling.**

## Method notes

- Rank unseen repos on **code bytes by extension minus vendored paths**; the top of a raw-tree-byte
  ranking is still `researchlocal-backup` (47 MB code) and backup/mirror repos, not new work.
- **`/tmp/rr-reader1`, `/tmp/rr-reader2`, `/tmp/rr3` in a committed config is a 3-of-3 door** —
  the empty-gitlink defect with extra steps. Always `ls` the paths a manifest names.
- A scorer that only *prints* FAIL is not a gate. `grep -c "sys.exit" scorer.py` before believing
  one.
- **A suite that overwrites its own committed result is a suite that can delete its findings.**
  Check `git status` after running anything.
- An error constant used as a fingerprint value is agreement by construction. Assert that every
  participant *executed*, not that it *participated*.
