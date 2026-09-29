# What these gates establish, and what they do not

## Gate 1 — grounding

**Claim.** A claim is `GROUNDED` if the artifact it cites was produced at or before the
moment the claim was written.

**What it establishes.** A *temporal* fact: the author could not have had this evidence
when they formed the view, because it did not exist yet. This is the tightest possible
statement and it is still useful, because conclusion-before-evidence is the single most
common way a confident wrong answer gets produced.

**What it does not establish.**

- That the claim is *true*. A grounded claim can be false, and a false one is worse than
  an ungrounded one because it carries borrowed credibility.
- That the claim *agrees* with its receipt. Gate 1 cannot read the receipt. The
  lane-u-collision headline is timestamp-grounded and refuted by the artifact it cites.
- Anything at all without a timestamp on the receipt.

**Why the three states and not two.** `UNSOURCED` is deliberately distinct from
`NARRATIVE_FIRST`. An unsourced claim is *ungrounded*; it is not *wrong*. A gate that
conflates them produces confident false accusations, and a linter that cries wolf gets
switched off — which is strictly worse than having no linter.

## Gate 2 — consistency

**Claim.** A report is *self-inconsistent* if it exhibits one of four specific shapes:
a universal negative contradicted by a unique instance (C1), a summary statistic absent
from the body (C2), a term negated in the summary and affirmed in the body (C3), or a
count disagreement on a shared denominator (C4).

**What it establishes.** A *logical* fact about the report's own text: these two
statements cannot both be true of the report's subject. No external knowledge required.

**What it does not establish.**

- That the report is consistent when it passes. Passing means *these four shapes were not
  found*. The shapes are a sample, chosen because they occurred. There are infinitely
  other ways to contradict yourself and this gate is blind to all of them.
- Anything about whether the report is *right*.

**Why the vocabularies are narrow.** A broad word list produces confident false positives.
A linter that cries wolf gets switched off, and a switched-off linter is worse than none
because it was bought with attention. The regexes are deliberately small: six
universal-negative forms, five unique-existence forms, seven negatable terms.

## The composition

```
clears both gates  ⟺  the artifact predates the claim
                   AND the report does not contradict itself in one of four ways
```

This is the strongest statement the toolkit makes, and it is still far short of "true".

**The two gates are independent and neither substitutes for the other.** A report can be
perfectly grounded and self-contradictory (the fleet's own case). A report can be
internally consistent and ungrounded (a confident claim citing nothing). Both failures
occurred in one session, in the same fleet, and the second one is invisible to the first
gate entirely.

## The crash contract

A check that raises does not return "no findings." It raises `LinterCrashed`.

This is not pedantry. An earlier version of this linter caught every exception and
appended it as a finding, so a `NameError` inside a check was indistinguishable from a
clean result — and the linter reported clean through a whole session with a dead check
inside it.

**A crash must be louder than a pass.**
