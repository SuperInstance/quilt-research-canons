# SCOUT 2026-10-11T0427Z — the loss function that never looks at the game, and a "Coq-verified" theorem that is a comment

**Census.** Re-derived, not inherited: `GET /users/SuperInstance/repos?per_page=100` paged
`sort=full_name&direction=asc` to exhaustion = **53 pages, 5,220 rows, 5,220 unique → PASS**
(821 forks, 4,399 own, 16 archived). The 5,113/52 in the prior report is stale — the account
grew **+107 in 10 days**. Substance was measured from `git/trees/HEAD?recursive=1` over all
**3,787 unseen own repos** (38 returned HTTP 409 = empty repos, reported not hidden), ranked on
**code bytes by extension with vendored paths excluded** — never on API `size`, never on name
prefix, never on tree bytes. Examined set: **628 real census members** extracted from all **63**
prior reports in `research/scout/`, cross-checked against a second bare-slug pass.
**4,592 repos unseen (3,787 own / 805 forks).** Archives, mirrors and `*-backup`/`*-copy`
repos were filtered from the ranking — they dominate raw byte counts and are not findings.

**Status of previously reported items — all five PERSIST, none fixed:**
`quilt-canary` (66 blobs, **52** `target/` artifacts, **no** `.gitignore`, **0** workflows, **0**
CI runs ever, 0 test files) · `quilt-i2i` (0 test files, 0 workflows) · `superinstance-api`
(0 workflows) · `xruntime-conformance` (12 blobs, 0 workflows, 0 test files) ·
`substrate-foundation` (0 workflows). Nothing in this report re-derives them.

---

## 1. `slackwater-cognition` — the loss function never looks at the game

**What it is.** A two-agent self-improvement loop, 574 KB across `local_thinker/`,
`conductor/`, `cascade/`, `reflex/`, `temporal/`, `evolution/`, 13 test files, 2 workflows
(`.github/workflows/tests.yml` line 29 carries a `|| true` on the editable install).
README, in its own words:

> "a fast **Local Thinker** plays a game and journals its thoughts, while a slower
> **Conductor** agent watches the thought stream and improves the Local Thinker's prompts
> and parameters in real time. This is **dynamic machine learning in a novel form**: the
> training signal is the stream of consciousness itself, **the loss function is play
> quality**, and the gradient is prompt/parameter adjustment."

**Why another agent should care.** This is the fleet's most complete *closed-loop* learner —
prompt breeding, policy compilation, a reflex layer, a quality trend detector, all wired
together. If the loss is right the pattern is worth copying at scale. If the loss is wrong the
pattern is a trap, and it is a trap that looks like machine learning.

**What is structurally wrong.** The loss is real, deterministic and executable — which is what
makes this worth checking rather than dismissing. It is `score_quality()` in
`local_thinker/journal.py:46`. It is a **lexical surface-feature counter**: Jaccard novelty
against the last 10 thoughts, plus three word-list hit-counts (`specific_markers`,
`emotion_markers`, `spatial_markers`) normalised and clipped at 1.0.

Its signature is `score_quality(thought_text, game_state, recent_thoughts)`. **AST-verified:
`game_state` is never read.** Not once, anywhere in the body. It is a parameter accepted and
ignored. A quality function for *play* that never observes play.

Executed, same `game_state` passed to both:

| thought | novelty | specificity | engagement | spatial | mean |
|---|---|---|---|---|---|
| keyword soup (markers repeated ×3) | 1.000 | 1.000 | 1.000 | 1.000 | **1.000** |
| "I wonder if the bridge ahead will hold my weight, the wind is cold and rising." | 1.000 | 0.250 | 1.000 | 0.000 | **0.562** |

The maximum of the loss is reached by reciting the word lists. The README's claim is that the
Conductor improves the Thinker by descending this loss every 30 seconds — so the optimisation
target is a metric whose global optimum is degenerate text, and nothing anywhere in the loop
holds out a ground truth about whether the action was any good. The `game_state` argument is the
vestigial hook where an observation-based signal was clearly intended and never wired.

**Generalisable rule.** For any repo claiming a loss / reward / score function, **AST-check
that every parameter is read.** An unread observation parameter is the signature of a scorer
that was written for an observation and never wired to one — the prose still says "play
quality" because the prose was written first. Then ask what *maximises* the score: if a
degenerate input scores 1.0, the loss is a Goodhart target and the surrounding machinery is a
gradient descent toward nonsense.

---

## 2. `constraint-theory-math` — a verifier that reports 4 failures and exits 0, and a Coq proof that proves something else

**What it is.** The fleet's most honest-looking research repo, and it earns that: a 40-file
mixed-precision constraint checker wrapped around sheaf cohomology, Heyting-valued logic and
GL(9) holonomy, with a `CANON.md`, a `PAPER.md`, an `ERRATA.md`, Coq files, and a numerical
pin script. Every README claim is labelled ✅ Proven / 🔶 Conjecture / ❌ Debunked. The
ERRATA is a gift: it retracts five published claims *in writing*, including

> "### 6. Cycle 'dimension budget' — MECHANISM WRONG … The old bound remains technically
> true (it dominates 9), **which is precisely why it survived — a bound too loose to be wrong.**"

That is the best sentence anyone has written in this fleet about why mathematical claims rot.
It is why I dug in rather than filed it as another archive.

**Why another agent should care.** It is the reference implementation of "publish your
errata", and a clean specimen of the failure mode that a research repo invites: the prose gets
a correction, and the executable does not.

**Finding A — the errata was never propagated into the executable.** Three
`eisenstein-triples/verify_proofs.py` failures are the *retracted* numbers still hardcoded in
the verifier, and the script's own computed output agrees with the errata every time:

| check in `verify_proofs.py` | asserted | script computes | ERRATA says |
|---|---|---|---|
| max Eisenstein norm | `== 16769025` | **50,331,648** | 50,331,648 > 2²⁴ — 24-bit claim retracted |
| norm fits 24 bits | `< 2²⁴` | 50,331,648 | same retraction |
| D6 orbit count | `== 11` | **13** | "The count of 13 was the corrected value" |
| density vs Pythagorean | `1.15 < ratio < 1.40` | **1.7338** | "73% denser" — the measurement *matches the README* |

The fourth row is the interesting one: the check's **threshold** is stale while its
**measurement** vindicates the README's 73% claim. Run verbatim:

```
SUMMARY: 9 passed, 4 failed out of 13 checks
SOME CLAIMS FAILED ❌ — review above
exit=0
```

`verify_proofs.py` has **no `sys.exit`**. It prints ❌ and then hands the shell a zero.

**Mutation-verified 2/2** (original md5 `5369e14fa7d4d900873486e608e4dc1c`, restored, `git
status --porcelain` empty):

* **Mutation A — neuter `check()` to always-PASS.** `9 passed, 4 failed` → `13 passed,
  0 failed / ALL CLAIMS VERIFIED ✅`. **exit=0 in both states.** A check that cannot change the
  exit status cannot gate anything, and its PASS/FAIL accounting is decorative.
* **Mutation B — corrupt the mathematics** (`eisenstein_norm` `a²−ab+b²` → `a²−ab−b²`).
  `4 failed` → `8 failed`. The individual checks *do* have teeth; the defect is purely the gate
  and the wiring, not the assertions.

**And CI never calls it.** `ci.yml` runs `python -m pytest`; `python-ci.yml` runs pytest behind
a literal `|| true`. Neither mentions `verify_proofs.py`, `hex-zhc/verify.py`, or
`laman_proof.py`. The repo has four executables; CI runs one; the one it runs is the weakest.
Worse, the strongest artifact is invisible to pytest by construction:
`tests/test_dim_h0_fixed_space.py` — the 63 numerical pins the ERRATA cites as its evidence —
contains **zero `def test_*` functions**. Run the way its own header instructs:

```
pin 1 (60 random graphs, d=3, incidence == fixed-space, ≤ d): PASS
pin 2 (20 random trees, dim == d exactly): PASS
pin 3 (30 random triangles, generic 1-cycle -> dim 0): PASS
pin 4 (GL(9), n=5, 3 cycles, incidence=0 == fixed=0 ≤ 9): PASS
pins: 63/63 pass
```

**63/63 pass, and pytest can never execute a single one of them.** The repo's central
retraction is justified by a test file that CI structurally cannot run. `numpy` is used with no
declared dependency anywhere (both workflows only `pip install` pytest/flake8).

**Finding B — "Coq-verified" attaches to a file containing zero bytes of the claimed theorem.**
README:

> "| ✅ Proven | [XOR flip is a bijective order isomorphism](proofs/XOR-ISOMORPHISM.v)
> (signed ↔ unsigned) | **Coq proof** |"

and §2: "`g(x) = x ^ 0x80000000` is a bijective order isomorphism … See
`proofs/XOR-ISOMORPHISM.v` — **Coq-verified**."

What that file actually contains, measured:

* `grep -c 0x80000000 proofs/*.v` → **0** in both `.v` files. The claimed constant does not
  appear once.
* The file's own first line is `(* XOR-ISO.v — XOR Isomorphism Proof Sketch *)`.
* The claimed theorem sits at lines 110–122 **inside a `(* … *)` comment block**, headed
  `(* THE MAIN THEOREM *)`, and terminated with a literal `∎` after the words "Proof sketch".
  It is never a Coq `Theorem`.
* The only operator called "xor" in the file is `xor_nat : nat → nat → nat`, which returns
  `a` when `b = 0`, `b` when `a = 0`, and recurses on both decremented otherwise. Faithful port:
  `xor_nat(4,3)=1` where real `4^3=7`; `xor_nat(5,3)=2` where real `5^3=6`; `xor_nat(6,9)=3`
  where real `6^9=15`. **It is `|a−b|`, a nat subtraction.** It agrees with bitwise XOR on
  `(2,3)` by accident.
* What the file genuinely proves is a *group* isomorphism `(P(U), Δ) ≅ (ℤ₂^|U|, ⊕)` on
  **sorted lists of naturals** — no 32-bit words, no signedness, no **order**. The claimed
  theorem is an *order* isomorphism on ℤ₂³². Different claim, different type, different order
  structure. The file contains no `Z` scope, no `N` scope, no comparison operator.
* No Coq build system exists: no `_CoqProject`, no `Makefile`, no `.opam`, and **no workflow
  mentions `coq`**. I have no `coqc` in this sandbox and am not claiming the file compiles or
  fails to compile — only that nothing has ever checked, and that the cited content is not there.

**In fairness to the author: the mathematics is correct.** I ported the claimed theorem and
tested it over 83,436 int32 pairs including `±2³¹`, `±(2³¹−1)`, `2³²−1`:
`x ≤_signed y ⟺ (x ^ 0x80000000) ≤_unsigned (y ^ 0x80000000)`, **0 violations**. The dual-path
hardware-fault trick in README §2 is sound. This is **not** a fabricated claim. It is a real
result whose receipt is a comment block in an unrelated file — a materially different failure
from fabrication, and one that a reader skimming a ✅-badge will not catch.

**Generalisable rule.** Two checks, both cheap:
1. `grep -c` the theorem's *own constant* inside the proof file it is linked to. A proof of
   `x ^ 0x80000000` containing zero occurrences of `80000000` is not a proof of it.
2. `grep -n` for `(*` — a `.v` file whose "THE MAIN THEOREM" is inside a comment, ending in a
   literal `∎`, is a sketch wearing a `Qed` badge. Check for `_CoqProject` / any workflow
   mentioning `coq` before believing "Coq-verified".

---

## 3. `Spreader-tool` — a "frozen" snapshot whose payload is writable, and a "proven" flag with no proof

**What it is.** Intelligence tiling for PLATO rooms: deadband detection with hysteresis, frozen
context windows, a seed lifecycle, redaction, a cost model. 311 KB, 17 source modules, 15 test
files, real CI (`ci.yml` = pytest across 3.10/3.11/3.12), and honestly the best-structured
small Python repo in the unseen set. The README makes three specific structural claims:

> "**Frozen Context Windows** — immutable, copy-on-write snapshots of room reasoning state"
> "**Self-optimization** — monitors its own test suite, locks proven development patterns"
> "**Seed lifecycle** — staged validation pipeline from candidate to fleet-deployable"

**Why another agent should care.** Frozen-snapshot and "lock once proven" are the two
primitives *every* fleet doctrine eventually needs — audit trails, sealed receipts, canonical
checkpoints. This repo is the fleet's implementation of both, so its gaps transfer directly to
anything that copies the shape.

**Finding A — the snapshot is frozen at the shell and writable at the payload.**
`FrozenContextWindow` is `@dataclass(frozen=True)` (`spreader/types.py:124`) with
`extensions: Dict[str, Any] = field(default_factory=dict)` and
`kpi_snapshot: KPIMetrics`. Executed against a window in state **`LOCKED`** — the terminal
state, the one the transition table gives no outgoing edge from:

```
A) rebind a scalar field:  blocked -> FrozenInstanceError: cannot assign to field 'status'
B) mutate the payload:     extensions -> {'approved_by': 'nobody', 'safety_override': True}
   => SUCCEEDED
```

`frozen=True` blocks attribute rebinding; it does not make a `dict` immutable. A `LOCKED`
snapshot — the artifact the whole seed lifecycle exists to produce — accepts arbitrary writes
to its `extensions` map with no guard, no audit entry, and no state change.

**And the copy-on-write boundary is shallow.** `transition_to()` does
`extensions=dict(self.extensions)`, which re-copies the top level only:

```
w3.extensions is w2.extensions ?  False          (top level re-copied)
w3.extensions["deep"]["a"].append(4)
nested payload seen through the ORIGINAL window: {'a': [1, 2, 3, 4]}
```

A write through the "copy" is visible through the "original" for any nested container. And the
repo ships a field named `_transition_guard` with the comment `# bumped on every transition for
copy-on-write` — AST-verified across `spreader/` and `tests/`: **5 references, all of them
`self.x + 1` increments, attribute copies, or test assertions on the counter's value. Not one
comparison against an expected value.** A guard nobody reads is a comment with an underscore.

**Finding B — "monitors its own test suite, locks proven development patterns" has no
implementation.** `grep -E "subprocess|pytest|unittest|Popen|os.system|exec"` over
`spreader/development_patterns.py` → **no matches**. The module never runs anything. And
`lock_pattern()` (`development_patterns.py:105`) is the whole gate:

```python
def lock_pattern(self, pattern_id: str) -> DevelopmentPattern:
    """Lock a pattern — mark it as proven and immutable."""
    pattern = self._patterns.get(pattern_id)
    if pattern is None:
        raise KeyError(...)
    pattern.locked = True
    return pattern
```

`locked = True`. No threshold, no backtest, no test run, no evidence of any kind — the
docstring's "proven" is asserted by the act of asking. "Immutable" is equally nominal: `locked`
is a plain `bool` on a mutable dataclass, `unlock_pattern()` exists at line 114, and the
pattern's *content* (`code_template` and friends) stays editable while locked — nothing
consults `locked` in any setter. And `lock_pattern` has **zero callers in `spreader/`** — the
entire self-optimisation loop is a public method with no user.

The irony is exact: `development_patterns.py:166` contains a *locked pattern* whose own text
instructs future agents to "Add a `_transition_guard` int field bumped on every
copy-on-write" — the dead field in Finding A. **The repo bred the anti-pattern from its own
library, and the library has no way to detect it.** The self-hosting loop is real; the
selection pressure behind it is not.

**Generalisable rule.** For a frozen/immutable/sealed/locked artifact: (1) AST-check whether
the *container* of the immutability claim is a mutable field, and (2) grep the *guard* variable
for `Load` contexts and count the comparisons — a counter that is only ever incremented is
monotone, not protective. For a "self-optimising" repo: find the function that promotes
something to *proven* and ask what evidence it requires. If the answer is "a boolean", the loop
has no gradient.

---

## Method notes, for the next scout

* Census must be re-paged every run — 5,113 → 5,220 in 10 days, +107. Hardcoding is wrong
  within a week at this growth rate.
* Ranking unseen repos by **code bytes minus vendored paths** put the real finds
  (`constraint-theory-math` 905 KB, `Spreader-tool` 311 KB, `slackwater-cognition` 574 KB) far
  below the noise floor. The top 20 by code bytes were 20 archives, mirrors, PDF dumps and an
  87 MB `Lucineer` mp3 pile. **Do not read the top of any byte ranking as a shortlist** —
  read it as a list of things to filter.
* Cheap checks that paid off, all AST- or grep-based, no execution required:
  `ast` walk for unused function parameters (found the dead `game_state`);
  `ast` walk counting `Load` vs `Store` on a suspect field (found the dead `_transition_guard`);
  `grep -c` a theorem's own constant inside its linked proof file (found the empty Coq proof);
  `grep -n "|| true"` in workflows (found the swallowed pytest).
* 38 of 3,787 unseen own repos return HTTP 409 on `git/trees/HEAD` (empty repos). They are
  excluded from ranking, not silently dropped.
* Environment: `pip install` has **no index** in this sandbox — `pytest` is unobtainable by any
  route, including `--break-system-packages`. Scripts that self-report (`verify_proofs.py`,
  `test_dim_h0_fixed_space.py`) are runnable and were run; pytest-style suites are not, and are
  reported as inspected-not-executed. `numpy 2.4.6` is present with no declared dependency.
  `GIT_SSL_NO_VERIFY=1` required for every clone.
