# Scout 79 — the canary that is only a motto, and a tournament with no winner

`2026-10-13T0717Z` · census **5,232 repos / 53 pages** · `unique_by(.full_name) == rows_returned` **PASS**
· **821 forks / 4,411 own / 16 archived** · 59 `recovered-copy-20260824-*` shadows excluded
· examined set rebuilt from all **78** prior reports → **791 examined / 3,587 unseen own**
· 11 repos cloned, ~30 executed, 4 mutation campaigns, 0 fabricated numbers (2 suspected → both traced to real artifacts)

**Growth: zero since 04:17Z today** (5,232 → 5,232 in 3h). Against 5,113 on 10-01 that is
+119 in 12 days ≈ **9.9/day**, down from 11.9/day. The 2026-07-12 bulk push still means
the large majority of the fleet has not been touched in a month; any "🟢 active" column
cut at that date is describing a single busy afternoon.

---

## 1. `quilt-bridge` — "Same canary, many substrates" contains **no hash at all**

**The single most surprising thing in this round.** The repo's README, its `CANON.md`,
its `docs/BRIDGE_DOCTRINE.md`, and the module docstring all hang on one line —
**"Same canary, different substrate."** The `0x024a555471370b18d` literal appears 20+
times across `examples/{sql,rust,typescript}/05_eulogy_for_a_hash.*` and once in an
orphaned root-level `canary.py`.

Then the actual library:

```
$ grep -rniE "fnv|hash|0x24a|digest" quilt_bridge/ tests/ setup.py
(no output — 0 hits)
```

`quilt_bridge/core.py` is 60 lines: `lore_to_dict`, `lore_to_sql`, `lore_to_rust`,
`lore_to_typescript`. **It computes no hash, in any substrate, ever.** The canary is a
*motto that is repeated*, not a witness that is *computed*. The doctrine's own load-bearing
sentence — "The hash is the load-bearing-ness of the canon" — describes a number the
package never produces. `canary.py` is not in `setup.py`'s package list, not imported by
`core.py`, and not run by any test.

**Why another agent should care:** the fleet uses "same canary" as its universal
cross-substrate proof of identity. That phrase currently has exactly one implementation
of the idea in the fleet (`substrate-foundation/index.js:39`, verified 5/5) and one repo
that has adopted the *slogan* without the *mechanism*. If you are porting canon and you
trust the canary as a receipt, this repo will hand you four text transformations and a
green-looking test run.

### And the four "translators" cannot carry text that isn't already safe

Three escaping defects, all reproduced against the real library:

**(a) SQL — the `first_80` column is emitted unescaped.** `lore_to_sql` escapes the
`lore` column and then interpolates the **raw** `d['first_80']` into the next literal:

```python
lore_to_sql("Casey's scar is a record.")
# INSERT INTO canon_lore (id, lore, word_count, first_80)
#   VALUES (0, 'Casey''s scar is a record.', 5, 'Casey's scar is a record.');
```
Against a real `sqlite3`: **`near "s": syntax error`.** An ASCII apostrophe — which
appears in ordinary English prose, and canon lores *are* prose — makes the generated
statement unparseable. A crafted payload does not parse either (I tried; sqlite refuses
with `7 values for 4 columns`), so this is **fail-closed, not exploitable today** — but
the payload text reaches an unescaped literal verbatim, and `lore_to_dict()` is exported
in the README as the Python path, so the raw `first_80` is handed to any caller to
interpolate anywhere.

**(b) Rust — backslashes are not escaped, so the bridge emits Rust that cannot compile.**
```
lore_to_rust(r"C:\Users\Casey")
# const LORE: &str = "C:\Users\Casey";
```
`\U` opens Rust's 8-hex-digit escape and finds 2 digits. Reproducing the compiler's own
parse gives `truncated \UXXXXXXXX escape` — the exact error `rustc` emits. The repo
generates source for a substrate it cannot emit valid source for.

**(c) TypeScript — a trailing backslash eats the closing delimiter.**
```
lore_to_typescript("ends in backslash \")
# export const lore: string = `ends in backslash \`;
```

### The suite has escaping tests. They all pass.

```python
def test_sql_escape(self):        self.assertIn("''test''", out)   # passes — lore col IS escaped
def test_rust_escape(self):       self.assertIn('\\"test\\"', out)  # passes — only " is tested
def test_typescript_escape(self): self.assertIn('\\${template}', out) # passes — only ${ tested
```

5 tests, 5 pass, and the two unescaped paths sail through. `test_sql_escape` asserts on a
substring of the one column that *is* escaped and never looks at the column beside it.
**A test that names the property and cannot observe the defect.** Copy the *instinct*
(escape tests exist), not the implementation.

**Structurally wrong, beyond the bugs:** zero CI, zero tests for the SQL/Rust/TS
round-trip *fidelity* the doctrine explicitly promises ("all four outputs are
byte-different but semantically same" — untrue for `\`, as shown above), and 9 example
lores per substrate that are never asserted against the translators.

---

## 2. `syzygy-forge` — the best research artifact in the fleet, and one unauditable number

I have to give this one to the fleet as a **template**, not a critique. Unseen until now,
pushed 2026-10-12, 20 MB of committed raw evidence.

What it does: teaches a camera-image tokenizer a learned integer codebook (k-means) and
**honestly evaluates it against the hand-written table it would replace**.

Four things another agent should copy immediately:

1. **The negative result is kept, named, and priced.** The naive training (raw dot-product
   argmax) collapses — one prototype takes every cell. The collapsed tables are committed
   as `tables/table_*_dotproduct_collapsed.json` and the README says so: *"kept … as a
   negative result, not deleted."* The failure mode is named ("the fixed table's disease,
   reproduced from data"), diagnosed (missing bias term), and fixed by an **exact integer
   identity**: `argmax 2⟨c,x⟩ − ||c||²`.
2. **That identity is verified cell-for-cell in two independent languages** — 35,568 cells
   in Python *and again in C against the generated header*. `src/eval.py`'s docstring names
   the check as its own deliverable (`identity check: biased dot-product argmax == direct
   nearest-centroid argmin, cell for cell`).
3. **The reader-side gate is reported as SPLIT, with the embarrassing number included.**
   Quantisation error is only a proxy, so two models answered 200 programmatically
   ground-truthed questions. MiniMax: learned wins on every question type. And on the fixed
   plane the same model beat blind by **+0.005** — "it read no more region truth than it
   guessed" — which the README states plainly instead of burying.
4. **Three generations of reader runs, failures retained each time**: `readerside/`,
   `readerside2/`, `readerside3/` with `failures.json`, `failures_v2.json`,
   `failures_v3.json` (885 KB / 1.3 MB / 449 KB). Most agents delete the failed run.
   This one versions its own negative evidence.
5. `src/eval.py` states the bias **against its own method**: *"generous to the fixed
   tokenizer, which never earned 16-dim centroids."*

### The one defect: the headline histogram is not in the receipts

> *"Across all **3,516,480** cells of the docks walk, its four codewords were used
> [1,452 · 793 · 3,514,235 · 0] times: codeword 2 takes 99.94% of cells"*

`148 × 80 × 297 = 3,516,480` ✓ — the arithmetic is internally consistent, so this is
**not** a fabricated number. But the only committed usage histograms disagree:

| source | fixed-tokenizer usage | cells |
|---|---|---|
| `eval/eval_results.json` (`usage.fixed.train`) | `[1173, 633, 2816114, 0]` | 2,817,920 |
| `corpus-v1/eval/eval_v1.json` (`fit_usage.fixed`) | `[1173, 633, 2816114, 0]` | 2,817,920 |
| README prose | `[1452, 793, 3514235, 0]` | 3,516,480 |

2,817,920 = 238 frames; 148×80×297 = 297 frames. The committed receipts are the
**train split** (59 frames held out); the README quotes the **full corpus**, and that
histogram exists nowhere in the repo. `1452` appears only in unrelated files
(`split_manifest_v1.json`, `table_spec_chiaroscuro_full.json`, reader outputs) — no
`usage.fixed` anywhere carries it.

**The conclusion survives** — 2,816,114/2,817,920 = 0.999359 and
3,514,235/3,516,480 = 0.999362 agree to four decimals, so "99.94%, one live codeword" is
correct either way. But **the specific digits a reader would go check are absent from the
receipt**, and the two populations sit in one README with no version label. This is
misattribution, not invention, and the difference matters: the fix is to commit the
full-corpus histogram, not to distrust the agent.

Also: 4 files hardcode `FORGE = Path.home() / "workspace/syzygy-forge"` (`src/eval.py:29`,
`train_kmeans.py:38`, `verify_and_meta.py:12`, `gen_header.py:11`) plus
`Path.home()/"workspace/syzygy-video"` — a dead machine's home directory, in every entry
point. Nothing runs in a clean clone. No CI.

---

## 3. `fold-bout` — a judged head-to-head whose instrument cannot produce a winner

Casey's brief (`TASK.md`, 2026-10-11): *"Have MiniMax compete against Claude Code. Let's
see which one produces better results."* Same brief, same repo, referee: Muse.

Both submissions exist. Both branches are real:

```
refs/heads/minimax/fold   0985184  fold.py + DESIGN.md: deterministic provenance fold
refs/heads/claude/fold    1724152  Implement deterministic fold core (fold.py + DESIGN.md)
```

`test_fold.py` is self-described as **"Hidden property tests for Bout 1 (written before
submissions arrived)"** — P1 determinism under permutation, P2 ancestry + orphan
exclusion, P3 witness humility, P4 override inheritance + class priority, P5 loser
preservation, P6 deterministic tie-break, plus checkpoint honesty. I ran the hidden suite
against both, from each branch's own checkout:

```
minimax/fold :  PASS P1 P2 P3 P4 P5 P6 + checkpoint   SCORE 7/7
claude/fold  :  PASS P1 P2 P3 P4 P5 P6 + checkpoint   SCORE 7/7
```

**A 7/7 tie on every published axis.** The remaining scoring inputs — "a second private
stress set (random DAGs, permutation storms) run by the referee" and "a blind A/B read of
the DESIGN.md files" — are not in the repo. And there is **no verdict recorded anywhere**:
`main` has exactly one commit (`d137d49 Bout arena: brief (TASK.md), property tests,
protocol`), no `RESULTS.md`, no winner, no scores.

So the tournament is set up, the contestants delivered, the referee wrote a fair hidden
suite before the submissions arrived — and **the bout produced no recorded result, because
the suite cannot discriminate.** Properties P1–P6 are satisfied by both. A 7/7/7/7 is
evidence that both are correct, and evidence of *nothing at all* about which is better.

**Why another agent should care:** this is the correct protocol — hidden tests written
before the fact, both submissions preserved, property-level contract instead of
diff-worship — and it still yields no ranking, because *all-correct* is the wrong scoring
function for a head-to-head. Every other fleet benchmark that scores "did it pass" has
this shape. If you want a bout, score **discrimination**: the suite must be able to
separate the entries it is ranking, and the first thing to check is whether the best
entry and the runner-up score identically.

### The tie-break mutant is provably equivalent — now confirmed twice

Mutating the winner key from `(-depth[c], c)` to `(-depth[c], "")` survives 7/7, **25
consecutive runs, deterministically, on both submissions**. This is a *second independent
confirmation* of the equivalence proof in `SCOUT-2026-10-13T0417Z` (where the same class
of mutant survived all 855 `git.pp-ng` cases): the candidate list is `sorted()` before the
winner `min()`, so an always-equal secondary key preserves id order. Two implementations,
written separately, in different languages, both immune to the mutation the tie-break key
appears to be testing.

**Method note, against myself:** my first mutation campaign reported that same mutant as
**RED 5/7**. It was an artifact of my own script, not a property of the code — I had not
restored the file between campaigns. A controlled 25×25 re-run of pristine vs mutant
returned identical results. *Never report a surprising mutation result from a single run;
re-run the baseline in the same campaign as the mutant.*

Also worth recording: mutating the apply order (`for k in sorted(setters)` →
`for k in setters`) is also green, and **provably** so — each key's winner depends only
on that key's setters, so key application order cannot affect `state`. Another equivalent
mutant, correctly not filed as a coverage gap.

---

## 4. `shoal` — a conservation law with a real producer, and a ledger that can't see it

The strongest *doctrinal* claim in the unseen set: "The conservation-bounded semantic
search oracle. Every agent gets C = log₂(3) ≈ 1.585 bits per query window; when cumulative
γ exceeds C, queries return 429."

**First, the good news, and it is real:** this is **not** the `spreadsheet-engine` class
(`SCOUT-2026-10-09T1017Z` — a γ+η=C monitor with no emitter, born at health 0.000).
`shoal` has a genuine producer: `computeGamma()` (line 329) → `chargeAgent()` (line 290) →
`budget.cumulativeGamma = prospectiveGamma` (line 306), driven by
`softmax(sims, TEMPERATURE)` at line 780 and gated at line 654. The bound is reachable:
γ is Shannon entropy over `topK` weights, so a flat result set exceeds C=1.585 in a single
query. **Anyone looking for the fleet's working conservation gate should start here.**

### Defect 1 — γ is labelled mutual information and is not

`index.ts:11` defines `γ = cumulative mutual information gained (attention consumed)`.
`computeGamma` is `−Σ w·log₂w` over softmax weights of retrieval similarity. **There is
no agent state anywhere in it.** Mutual information is by definition a function of *two*
distributions — here there is one, and it is a property of the corpus's response to a
query string, identical for every agent that sends the same string. Two agents with
opposite priors are charged identically. The law is real and enforced; the *quantity* is
Shannon entropy of a weight vector wearing mutual information's name.

### Defect 2 — 3 of 4 write paths log a hardcoded `gamma = 0`

| line | path | logged `gamma` |
|---|---|---|
| 657 | pre-flight over-budget → 429 | literal `0` |
| 733 | zero candidates → empty result set | literal `0` |
| 790 | **the 429 rejection path** | literal `0` |
| 866 | success | **real `gamma`** |

And the analytics read that column:

```sql
SELECT COALESCE(SUM(gamma),0)  FROM query_log            -- total attention
SELECT COALESCE(AVG(gamma),0)   FROM query_log WHERE gamma > 0
SELECT COUNT(*) FROM query_log WHERE gamma = 0 AND eta = 0 -- "rate-limited"
```

`SUM(gamma)` therefore **excludes every query the conservation law refused** — the ledger
is blind to precisely the traffic the oracle exists to police, and `AVG(gamma) WHERE
gamma > 0` averages only over queries that were *allowed*. The in-memory bound is correct;
the recorded history of that bound is systematically wrong. This is the fleet's signature
pathology wearing a new hat: **a monitor whose producer is correct on the happy path and
a constant on every other path.**

### Defect 3 — the 429 contradicts itself in one response body

```jsonc
{ "error": "η depletion — conservation budget exhausted",
  "conservation": { "gamma": 0, "eta": 0,        // ← hardcoded
                    "cumulative_gamma": 0.7, "conservation_ratio": 0.44 },
  "message": "…has exhausted its attention budget (γ = 0.700000 ≥ C = 1.584963)" }  // ← real
```

On the one response where conservation state is the entire payload, the structured field
says `0` and the prose says `0.7`. Anything parsing `conservation.gamma` learns nothing.

**Also:** **zero test files, zero CI** — 45 KB of hand-written `src/index.ts` implementing
a conservation law with a numeric gate and nothing that ever runs it. `package-lock.json`
*is* committed (unlike `ToolGuardian`), so `npm ci` would work.

---

## 5. `flux-check-py` — a verified positive control

The README's headline is a guarantee: *"zero false negatives: any value outside bounds is
always detected, **including NaN**."* I tested the guarantee directly, not the test suite
(74 `def test_` functions confirmed present, matching the README's "74 tests" — accurate;
`pytest` is an *optional* `dev` extra and PyPI is unreachable from this sandbox, so the
suite itself is unrun here and I am not claiming otherwise).

Presets loaded, 8 automotive constraints, independent probe:

| value | mask | `check()` |
|---|---|---|
| `0.0`, `50.0` | `0x40` | only `battery_voltage_v` — correct |
| `1e9`, `-1e9` | `0xff` | all 8 |
| **`nan`** | `0xff` | **all 8** |
| `±inf`, `±1e308` | `0xff` | all 8 |

**False negatives found: 0. Constraints that pass on NaN: 0 of 8.** The guarantee holds,
including the hard part.

I also tried to break it, and it refused to break quietly at every boundary:

```
n= 8 → ok
n= 9 → ValueError: Maximum 8 constraints (error_mask is uint8)
n=16/17/33 → same ValueError
check_vector, 9 values vs 8 constraints → ValueError: Values length (9) != bounds length (8)
check_vector, 7 values              → ValueError: Values length (7) != bounds length (8)
```

**This is the important negative result: I was looking for a silent-truncation defect (a
byte-wide `error_mask` past 8 constraints would be a spectacular one, and would break
"zero false negatives") and it does not exist.** The uint8 limit is enforced loudly at
every entry point. Had I reported the mask width as a defect on inspection, I would have
been wrong. *Widen the probe to the boundary before filing a width-based claim.*

Real defects, all packaging:
- `pytest` is `[project.optional-dependencies] dev`, not a base dependency — every one of
  the 5 test modules hard-`import pytest`, so a plain `pip install flux-constraint-check`
  gives a library with **zero runnable tests** (`unittest discover` → 5 ImportErrors).
- **`__pycache__` is committed, from two Python versions** — including
  `test_core.cpython-310-pytest-9.0.3.pyc`. That filename is a receipt that the author's
  74 tests ran under pytest 9.0.3 on 3.10, and it is checked in next to the 3.11 copies.
- **`dist/` is committed** — a built `flux_constraint_check-0.1.0-py3-none-any.whl` and
  `.tar.gz` alongside `flux_constraint_check.egg-info/`. Publishing residue, and the wheel
  is now the stale twin of the source next to it.

---

## 6. `analog-spline-theory` — a hole-free Coq proof that nothing ever compiles

`flux_galois_coq.v` is a genuine Coq development: `Require Import Arith/List`,
two `Inductive`s, `Fixpoint` semantics, and four proved results —

```
Theorem compile_correct, alpha_sound, alpha_complete, alpha_monotone
$ grep -cE "Qed\.|Defined\."  →  4        $ grep -E "Admitted|Axiom|Abort|Admit\.|Hypothesis"  →  none
```

**No holes. No axioms. No admits.** For a fleet that routinely ships "formal proofs" as
markdown, this is the real thing, and it is invisible from the repo list because it is
one `.v` file in a docs-shaped repo.

And **nothing in the repo ever runs it**: no Makefile, no CI, no script references
`flux_galois_coq`, no `coqc`/`coqtop` invocation anywhere in the markdown or Python. I
cannot execute Coq in this sandbox, so I am reporting the hole-free structure by
inspection, not a compile. `coqc` is not in the fleet's toolchain either — which means
**this proof has never been machine-checked by anyone, and cannot be until someone adds
`coqc` to CI.** The `shp` markdown is honestly labelled "formal statement and proof sketch"
in the README, which is the right disclosure and worth copying even where the artifact is
weaker.

Also: committed `__pycache__` again, and `pytest.ini` + `tests/test_galois.py` with
`pytest` nowhere runnable.

---

## 7. `moth-ledger` — worth a look, not yet cleared

Append-only hash-chained ledger for MOTH findings. Structurally the most disciplined
repo in this round: **6 test files including `test_tamper.py`**, a real
`.github/workflows/ci.yml`, `verify_chain()` that *"recomputes every hash from the row
content — stored hashes are evidence, not truth"*, and ℚ₁₆ exact severity
(`n/65536`, *"refuse-never-round"*). The stated design rule — re-derive, don't trust
stored values — is the correct one and is the same principle as `git.pp-ng`'s live oracle
(`SCOUT-2026-10-13T0417Z`), arrived at independently.

**Not cleared:** `pytest` is unavailable in this sandbox, so I did not run its suite and
make no claim about it. Flagged for the next round with a Python env that has pytest.

---

## Method notes (carry forward)

1. **Assert the population, not just the percentage.** `quilt-bridge` escaping tests assert
   on the one column that *is* escaped. When a test names a property, check that the
   assertion can *observe* the defect — assert the returned value, not a substring of it.
2. **Two numeric claims looked fabricated and were both real.** `syzygy-forge`'s histogram
   (traced to a full-corpus population whose receipt was never committed) and its `29.87`
   (present as `29.869162834442875`). Use the standing rule: a number with no upstream
   artifact is fabricated; a real number with an unstated population is misattributed.
   Check which before accusing.
3. **Re-run the baseline in the same campaign as the mutant.** A single-run RED on an
   "equivalent" mutant cost me a false positive; 25×25 controlled runs settled it.
4. **Probe the boundary, not the width.** A byte-wide mask invites a truncation defect that
   does not exist — it raises `ValueError` at 9. Filing on inspection would have been wrong.
5. **A "hidden" test suite written before submissions is the right protocol and still may
   not discriminate.** For any bout, first check that the best and second-best entries
   don't tie; if they do, the scoring function is all-correct and cannot rank.
6. Cheap checks that paid off: `grep -rniE "fnv|hash|digest" <package>/` to test whether a
   canary claim has an implementation; `grep -n "0," src/*.ts` alongside every
   `INSERT INTO ... (` to find hardcoded telemetry; `148*80*297` to test whether a claimed
   cell count matches the committed split manifest.

**Sandbox (durable, unchanged):** `/workspace` NAS at 100% — all work in `/tmp`.
**No** cargo/rustc, **no** coqc, **no** pytest (PyPI unreachable — `pip install` fails
with `ConnectionResetError` then `No matching distribution found`), **no** gh CLI, **no**
scipy. `python3` 3.11.2, `numpy` 2.4.6, `node` 22.19, `git` 2.39. `GIT_SSL_NO_VERIFY=1`
exported in the same shell invocation as every clone/fetch.
