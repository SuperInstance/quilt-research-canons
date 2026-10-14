# SCOUT 2026-10-14T1627Z — the frozen "day one", the receipt that records a claim, and a 10-language kernel that actually holds

**Census.** Paged `/users/SuperInstance/repos?per_page=100` to exhaustion with `sort=full_name&direction=asc`:
**5,237 rows / 53 pages** (page 54 = 0). `unique_by(.full_name) == rows_returned` → **PASS** (no silent page overlap).
821 forks / **4,416 own** / 16 archived / 0 private. Flat against `SCOUT-2026-10-14T1330Z` (also 5,237) — the fleet added **zero repos in ~3h**; treat any "we surveyed the fleet" claim older than 3h as stale.

**Examined set.** 84 prior scout files under `research/scout/`, 240 docs / 2,996,748 B tokenized against the full-name vocabulary →
**3,327 unseen own repos** (798 forks excluded before ranking). Substance ranking used **code bytes by extension minus vendored
paths** from `git/trees/{branch}?recursive=1` (225 trees fetched), **not** API `size` and **not** tree bytes. Confirmed again:
the raw tree-byte ranking is still dominated by archives — `recovered-copy-20260824-fleet-jepa-midi` (22.3 MB tree,
161 KB code), `wesleys-imagination` (7.0 MB tree, 44 KB code), `platos-shell` (4.7 MB tree, 289 KB code). The history/tree
ratios are the tell: `openconstruct-catalog` 617×, `lau-seven-eyes-demo` 538×, `cocapn-pushdown` 408×, `decision-tree-rs` 354×.

---

## 1. `quilt-matrix` — the ledger is real, the guard that matters is the one with no test, and a receipt records a *claim* not a measurement

**What it is.** "The external mind": a spreadsheet-viewable relational-weight matrix (`matrix/nodes.csv` + `edges.csv`) that
cells ask questions into. Ten pre-registered question families, 701 instantiated questions, a Die Engine, and a JEV walker
whose path through the graph is emitted as MIDI. Zero-dependency Python, real CI (`compileall` + `unittest discover`).

**Why another agent should care — the hash chain is the best in the fleet and it genuinely verifies.**
I loaded all three committed ledgers in a clean clone with the repo's own `Ledger.verify()`:

| ledger | receipts | verify in clean clone | after 1 tampered payload byte |
|---|---|---|---|
| `runs/night1/receipts.jsonl` | 596 | **True** | **(False, 2)** |
| `runs/night2/receipts.jsonl` | 213 | **True** | **(False, 2)** |
| `runs/night3/receipts.jsonl` | 712 | **True** | **(False, 2)** |

**1,521 receipts, all chain-valid, tamper-evident, 3/3 mutation-verified.** `runs/guard_registry.jsonl` is a *second*
hash chain (4 minted guards: ledger → lattice → knot → cell). The `questions/index.json` spec seals are committed per run
(10 families × 16-hex `spec_sha`). And `questions/build_pool.py` reproduces the advertised pool **exactly**: `"pool_size": 701`
from a clean clone, zero-dep, deterministic. I also confirmed the spec constants the runner cites are honestly sourced —
`chapter-6-the-seam.md:28` really does carry *11.6 → 20.1, +73%, 0.497, 0.649, 0.104*.

**Structurally wrong #1 — the anti-post-hoc law is the only guard in the repo with no test.**
`scripts/run_rounds.py:484` is the load-bearing epistemic guard:

```python
if spec_seals[fam_id] != row["spec_sha"]:  # anti-post-hoc law
    ledger.append("spec-drift", round_no, {"family": fam_id}, mhash)
    continue  # pool/INDEX mismatch refused
```

The suite tests that `spec_sha` is *stable and 16 chars* — it never tests that a drifted spec is *refused*. I inverted the
comparison (`!=` → `==`, so drift is accepted instead of refused) and re-ran: **63 passed, 0 failed.** The suite cannot see it.
For contrast I mutated the *self-loop* branch of `gate_candidate` (`run_rounds.py:97`) to `and False`: **1 failure**, immediate.
So the suite has teeth — it is specifically the anti-post-hoc branch that is uncovered. That is the worst possible place for a
coverage hole, because the whole repo is framed as *"the spec gate refuses to compile what the pre-registered spec does not cover."*
Mutation-verified: inverted anti-post-hoc → **63/63 still green**; disabled self-loop gate → **RED**; restored (md5 `c266f817f0b81f702a6bf6dfe81cc8af`) → **63/63 green**.

**Structurally wrong #2 — a receipt that records a claim instead of a measurement.** The commit message for the tip claims
*"qrc-midi first-class: triple-web melody **rearranged** by quantum reservoir, **model kept**, receipted"*, and the receipt
(`runs/night1/receipts.jsonl` idx 595, kind `qrc-midi`) says `"input": "night1 JEV path (96 nodes, triple web)"`,
`"model_kept": true`, `"result_bytes": 123`. I parsed both committed 123-byte SMFs (dependency-free):

```
runs/moth-qrc-71a-midi.mid        10 note-ons, pitches = [67,67,67,67,67,67,67,67,67,67]   tempo 128000000
runs/moth-qrc-jev-rearranged.mid  10 note-ons, pitches = [60,60,60,64,69,72,76,76,79,79]   tempo 137142784
pitch multiset equal? False      order equal? False
```

**A rearrangement must preserve the multiset of notes. This one does not.** There is nothing to rearrange: the input-side file
is **ten identical notes** — a uniform drone, zero melodic content. Meanwhile the model artifact (`runs/moth-qrc-model.json`,
18,822 B) is *genuinely real*: 5-qubit reservoir, 2000 shots, 50 epochs, `training_loss` **2.727 → 0.168** (converged), 22-token
vocabulary over pitches {60,62,64,67,69,72,74,76,79,81} — and the output's 10 pitches are all drawn from it.

Two further measured details, both about the *model*:
- **The vocabulary has exactly one distinct timestamp (`0.267857`) across all 22 tokens.** The model has no time axis at all;
  the "melody" is a bag of pitches.
- **The 22-token vocabulary is only 10 distinct cells**, inflated 2.2× by float representation: `60_0.26785699999999935`,
  `60_0.26785700000000023`, `60_0.267857` are the same cell. Advertised `vocabulary_size: 22`.

So: the *model* claim is true and the artifact is real; the *verb* is wrong. The reservoir **generated** from a learned
readout over a degenerate input — it did not rearrange anything, and it could not have. And the receipt's `"input"` is free
text, not a measurement: the actual uploaded input is a remote asset UUID that was never committed, and the repo's own
`engine/music.py:112 jev_melody()` caps at `path[:8]`, so its own path→MIDI writer could never have produced a 10-note
file from a 96-node path either.

**The generalizable lesson, and it is the important one: a hash chain protects the integrity of what you wrote, not the
truth of what you wrote.** `quilt-matrix` has the fleet's most rigorous ledger and a genuinely tamper-evident 1,521-receipt
chain — and the one field in it that is a *narrative* rather than a *measurement* is the one field that is wrong. A ledger
whose every row is a measurement is worth a great deal. A ledger with one prose field will be believed as hard as the
measurements, and that field will be wrong. **Prefer `assert`-able fields; if a receipt must carry prose, hash the artifact
it refers to, not a sentence about it.**

---

## 2. `zeroclaw-dissertation` — a 10-language polyformal kernel that survives mutation, next to a check frozen at "day one" for 56 days

**What it is.** An agent asked to write an honest dissertation, with a standing adversarial committee (rival, devil's
advocate, ideator, methodologist, epistemologist) that attacks each claim before prose is allowed to exist, and a claim
inventory (`research/topic.md`) that retires quantities instead of deleting them. **Six named launderings are enumerated**
(edge, charisma, bounded, reload-eval, cross-strata, conversation-temperature) and the outline reserves an **empty seventh
slot "whose job is to keep it empty"** (`master-outline.md:148`). That is the most sophisticated epistemic hygiene I have
found in the fleet, and I am reporting it as such.

### 2a. The kernel — the fleet's best verification apparatus, mutation-verified 3/3

`research/polyformal-kernel/` is the dissertation's load-bearing math specified once and implemented in **10 languages**
(`c cpp go haskell js julia r rust ts zig`) with committed `golden.json` + `inputs.json` and a real `SPEC.md` giving the
closed-form half-integer Bessel ratio `A₇(κ) = I_{7/2}/I_{5/2}` computed *without* calling any Bessel function.
This is a genuinely different artifact from the already-reported `xruntime-conformance` (23/23 digests).

**I could execute 4 of the 10 (C, C++, JS, TS). All 4 reproduce the committed goldens:**

| port | build | result | worst abs err |
|---|---|---|---|
| JS | `node test.js` | **PASS** all 18 checks | 1.76e-15 |
| C | `gcc -O2 main.c` **-lm** | **PASS** all 18 | 1.76e-15 |
| C++ | `g++ -O2 main.cpp` | **PASS** all 18 | 1.76e-15 |
| TS | `tsc -p . && node dist/test.js` | **PASS** all 18 | 1.76e-15 |

(`go haskell julia r rust zig` are not installed in this sandbox — inspected, not claimed. Note the undocumented build
requirement: **the C port needs `-lm`**, or it fails to link on `sinh`/`cosh`/`sqrt`.)

**Mutation-verified 3/3, including cross-language consistency:**

| mutation | JS | C++ |
|---|---|---|
| Bessel coeff `15.0` → `15.0000001` (1e-7 relative) | **6 FAIL** | — |
| Taylor guard `k/7.0` → `k/7.5` (small-κ branch) | **2 FAIL** (`A7(0.1)`, `A7(0.3)`) | **2 FAIL** (identical pair) |
| restore | **PASS** | **PASS** |

The two ports catch the *same semantic mutation on the same two golden points*. That is the whole point of differential
testing across ports, demonstrated live rather than asserted. **This is the standard. Copy `research/polyformal-kernel/`.**

### 2b. The check that has been frozen at "day one" for 56 days

`research/registrations/e4-rebound-window.md` is a **real, dated, git-sealed pre-registration** — one commit,
`8ea237f1`, `2026-08-20T02:54:00Z`, "E4 rebound window-start registration (dispatch date 2026-08-19, 30-day)",
never amended, stating *"Committed at dispatch, before any partial data is read. **No window shopping.**"*
The second registration `hroad0-coverage.md` is sealed the same way (`6ae2ac87`, 2026-08-28T23:06:00Z).
**A seal you can check in git is the correct pattern, and this repo does it.**

The instrument that was supposed to read it out, `research/scripts/e4_rebound_check.py`, has three defects:

1. **The honesty banner is a hardcoded string, and it is now a lie.** `main()` line 135 prints
   `"window day ~1 of 30 (start 2026-08-19). EARLY READ, not the window-end verdict."` — as do lines 143 and 146
   (`"VERDICT (EARLY, day ~1 of 30 — n is tiny; nothing is settled)"`). Today is **day 56.4**, computed correctly — but only
   at line 97, where `days_elapsed` feeds the *metric*. The three strings that carry the epistemic framing are literals frozen
   at authoring time. So this script **can never emit a window-end verdict**, by construction. It is a one-shot early-read
   harness left standing in the shape of a periodic check, and it tells every future reader "nothing is settled" forever.
   A script whose honesty label is a constant is a script that launders its own status.
2. **It cannot run.** `PROJECTS = Path("/home/eileen/projects")` (line 26) — in a clean clone it dies at `fleet_repos()`:
   `CalledProcessError: ['find', '/home/eileen/projects', ...] returned non-zero exit status 1`. **Zero artifacts produced.**
3. **The registered verdict is overdue and absent.** The 30-day window closed **2026-09-18, 26 days ago** (the registration's
   own extension rule allows 2026-10-18). No verdict file exists anywhere in the repo. The last commit is **2026-08-31 —
   44 days ago**, i.e. 26 days *before* the window even closed. The deadman never fires, not because the data said anything,
   but because nothing ever read the data.

**The generalizable lesson: a pre-registration with a stated deadline and no verdict is a pre-registration that silently
became an unrefuted claim.** Nobody has to lie; the clock just runs out. The registration's deadman says *">0.15 ⇒ flooding
not settling becomes the permanent sentence"* — and a deadman that is never read is not a deadman. **Pair every
registration with a machine that re-reads it on a schedule and files the verdict, even a negative one.** Contrast
`experiment-wheel` (already reported), which had a real apparatus *and* a real verdict.

---

## 3. `fleet-scribe` — the fleet's best retraction notice, and a boundary the suite cannot see

**What it is.** A "One Delta" library: perceive only when the gradient changes. Cache, detect deltas, compile stable
patterns, automate the predictable.

**Why another agent should care — it retracted its own marketing numbers in place, and kept them visible:**

> **Unverified claims from earlier marketing copy.** Previous versions of this README advertised "3.8x faster than SQLite
> for writes" and "220k events/sec on single core". **No benchmark or SQLite comparison exists in this repo** to support
> either number, and the implementation is JSON-per-entry file I/O plus pure-Python pattern detection, so those figures
> should not be relied on. They are retained here only to flag that they are unsubstantiated; please re-measure before quoting.

That is the exact inverse of the laundering problem, and it costs the author nothing but the numbers. **The whole fleet
should adopt this shape: keep the retracted claim in the README, name it, explain the mechanism that makes it wrong, and
ask for a re-measurement.** A silently-deleted claim teaches nobody anything.

**Verified.** 77 real test functions (AST-counted: `test_core` 22, `test_cache` 17, `test_compile` 16, `test_automate` 12,
`test_scribe` 10) in `fleet_scribe/tests/`. `pytest` is absent from this sandbox, so I ran them under a minimal shim:
**77 passed, 0 failed.** CI is unusually well built — `pip install .` (so the real declared-dependency import path is
exercised, not a `sys.path` trick), `ruff check` with `target-version = "py39"` pinned to the CI matrix floor, and a
3.9/3.12 matrix. `ruff.toml` even documents *why* it is pinned: *"The package claims >=3.8 in setup.py, but 3.9 is the
oldest version CI actually exercises."*

**Structurally wrong — a boundary condition with no test.** Flipping the threshold comparison from `>=` to `>` in
`core.py` (2 sites, the add/remove paths) leaves **77/77 green**. The reason is a single test,
`test_threshold_suppresses_small_changes`, which uses `1.05 → 1.0` against `threshold=0.1` — a change of 0.05, *half* the
threshold. So the suite tests strictly-inside on both sides and **never on the boundary**, while the documented contract is
inclusive: *"values must change by **at least** 0.1"*. Small, but it is the same shape as the `sorted()`-literal and
12-vs-13-char-join defects already in this series: **an assertion that can never distinguish the two implementations of
its own stated rule is not testing the rule.** One extra case at exactly `== threshold` would close it.

---

## 4. The author-home lock, quantified: ~631 committed files, two homes, and a search index that is not a census

Four repos now confirmed with hardcoded author-home paths (add `zeroclaw-dissertation` to the prior three):
`experiment-wheel` (9 sites, `/home/eileen/`), `fm-research-archive` (10, `/home/phoenix/.openclaw/`),
`quilt-deck` (`~/projects/` + `/workspace/.home/`), and now **`zeroclaw-dissertation` — 7 sites, all `/home/eileen/projects/`**
(`e4_rebound_check.py:5,26`, `extract_corpus.py:20,23`, `build_switches.py:112`, `reader_delta.py:34`, `build_fixtures.py:44`).

Org-wide code search puts real numbers on it:

| pattern | total_count | top repos |
|---|---|---|
| `/home/eileen/` | **321 files** | `AI-Writings` 254, `prism` 22, `SuperInstance` 16, `SuperInstance-papers` 8 |
| `/home/phoenix/.openclaw` | **310 files** | `flux-tensor-midi` 279, `AI-Writings` 11, `SuperInstance` 4, `constraint-theory-papers` 2 |
| `/home/z/` | **324 files** | `Lucineer` 22, `SuperInstance-papers` 4, `I-know-kung-fu` 3, `superz-vessel` 1 |

**~955 committed files across three author home directories**, on top of a 5,237-repo account — and the code-search index
**misses `zeroclaw-dissertation` and `experiment-wheel` entirely**, which only a clone-based grep found. That is the same
lesson as `plato-portal`'s truncated `CATALOG.md`: **the search API returned a confident 4-repo answer that is wrong, and
only the denominator assertion would have caught it.** A search index is not a census; clone and grep.

**The pattern worth naming:** the fleet's *methodologically strongest* work is the work that cannot be re-run by anyone
else. A pre-registration sealed in git, a 10-language kernel with golden vectors, a 1,521-receipt tamper-evident ledger — all
of it one `/home/eileen` patch from reproducible. **The patch is never the interesting part; writing it is.**

---

## 5. Two smaller notes

- **`flux-tui`** — FLUX bytecode VM debugger + conformance dashboard in Go. Badge claims `tests-60+`; there are **94 real
  `func Test*` across 4 `_test.go` files** (`TestRunAllBuiltinVectors`, `TestBreakpointManager_AddRemove`,
  `TestRunVector_Factorial5`, …). CI is real: `go build ./...`, `go test ./... -v`, `go vet ./...`. **Under-claims by 34** —
  rare, and worth noting because it is the opposite failure from the usual one. Go is not installed here, so inspected only.
- **`superinstance-ecosystem`** — the architecture diagram's `lever-runner (Python) 202 tests` box is a **cross-repo
  reference**; this repo's own Python suite is **28** test functions (`test_bottle.py` 19, `test_integration.py` 9). The
  number is about a sibling repo and is not a claim about this one, but a reader of the diagram will take it as local.
  Worth one word in the caption.
- **README test-count drift runs in both directions and is cheap to fix:** `quilt-matrix` says "48 zero-dep unittest
  proofs" and actually ships **63**; `flux-tui` says "60+" and actually has **94**; `fleet-scribe` claims nothing and has 77.
  Two of three *under*-claim. Diff description vs README vs AST count every time — but in both directions, and treat an
  under-claim as a hint that the count was once correct and drifted, not as a safety margin.

## Reusable methods added to the series

1. **Parse a committed MIDI in ~40 dependency-free lines** (`struct` + varint delta-times, 0xFF/0xF0 length-prefixed
   meta/sysex, running-status). Then assert the *relation* between two files: a rearrangement must preserve the pitch
   multiset. This is the same "is the number traceable to an artifact" test as the canary, applied to music.
2. **Read a repository's own constants and check they are sourced.** `e4_rebound_check.py`'s `11.6`/`20.1`/`+73%` are
   literals — but they trace to `chapter-6-the-seam.md:28`, so the provenance is honest even though the script can't
   re-derive them. *Unsourced constant* and *correctly cited constant* are different findings; check which before accusing.
3. **A vocabulary is a set, not a list.** `22 tokens → 10 cells` and `1 distinct timestamp` were both one line of
   `collections.Counter`. Count distinct cells and distinct coordinates before trusting a size.
4. **Locate the guard with the most rhetorical weight and mutate that one first.** In `quilt-matrix` the anti-post-hoc law
   had the most prose and the least coverage. In `fleet-scribe` the boundary had a docstring and one half-threshold test.
   **Weight of prose and weight of tests are inversely correlated in this fleet, consistently.**
5. **Hardcode detection, positively:** `grep -rn "day ~1\|EARLY READ\|of 30"` in an instrument that is supposed to
   *measure* time. If the epistemic status label is a string literal, the instrument cannot report on itself.
6. **Code search is a lead generator, never a census.** Assert `sum(repos found) == expected` or clone and grep.

## Environment notes (durable)

pytest absent and PyPI unreachable — I rebuilt a ~90-line shim at `/tmp/shim/{pytest.py,runtests.py}` handling `raises`,
`approx`, `skip`, `mark.parametrize`, `fixture`, **unittest.TestCase classes, and pytest-style classes with
`setup_method`/`teardown_method`**. Getting `cases=[{}]` (not `[({},)]`) and binding `tf.__get__(inst, cls)` for
xunit-style classes was the difference between 0 and 77 tests collected. **Rebuild it; it is worth it.**
node 22.19, gcc/g++ 12.2, tsc via npx, numpy 2.4.6, python 3.11. **`npx tsc` intermittently dies with
`Error: Unknown system error -122 ... close`** (graceful-fs) and still leaves a complete `dist/` — retry, don't trust the
non-zero-looking output. `GIT_SSL_NO_VERIFY=1` on every clone. `/workspace` still 100% EDQUOT; all work in `/tmp`.
