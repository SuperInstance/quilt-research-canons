---
title: Process Atlas — the fleet's thought patterns, and where they differ
date: 2026-09-29
subject: the agents are a quilt one abstraction level up; the structure is in the differences
---

## Why this document exists

Casey's instruction was to study **the processes of different agents**, and to find novel
thought patterns in the *differences* between how I and others approach the greater
project. That is the QUULT move applied one level up: if a qult is what a quilt becomes
when it learns to contain other quilts, then the agents' **methods** are a quilt, and the
interesting structure is not any single method but the disagreements between them.

So this is not a survey of what the fleet produced tonight. It is a survey of **how**, and
the deliverable is the difference.

## The roster and what each one actually did

Every one of these ran tonight, in the same session, on the same substrate. I watched the
traces, not just the outputs.

| agent | reaching move | what it found that mattered |
|---|---|---|
| **snowball-scout** | went to the **code**, not the README. Ran Syzygy's own 201-check suite. Grepped a 9,535-line seed blob for the full vocabulary. Then **checked call sites** and found `data_encode_full` has zero callers — the one mode-shaped thing in qthe-codec is dead code. | the mode menu is a 2-way alphabet selector, not a bit-cost menu, and it is not on the wire path |
| **herman-historian** | **downloaded the primary PDF** (9pp, 155KB) and verified the main theorem **verbatim**, then asked whether the hypotheses were met | killed a doctrine it was sympathetic to: the stability theorem needs *tame, continuous* functions, so the witness-log bridge is numerology |
| **General** (gpu-lab audit) | cloned read-only, read the whole pipeline end to end, compared prereg commit dates against the result commit, recomputed the binomial | 41/64 val clips byte-identical to train; the AUC is a training score wearing a holdout label |
| **wesley-mechanic** | wrote a script and ran it, iteratively | built 5 readout estimators + a sabotage estimator; found the shots ceiling empirically |
| **casper-critic** | did **not** check external correctness. It read for **internal contradiction** | caught a headline that its own body refutes two clauses later; caught an invented statistic in a report whose currency is checked numbers |
| **jevvy-auditor** | checked the **receipt's own machinery** | tautological receipt, mistyped arXiv id, a version label, a partly vacuous control |
| **owner (me)** | hashed a manifest instead of reading code | 30 seconds instead of a 30-minute audit — and found strictly more than the auditor |

## The pattern in the DIFFERENCES

Read across the table and one thing dominates: **the methods that worked all reached for
an artifact before forming a view.**

- herman-historian reached for the **paper**.
- I reached for the **hashes**.
- snowball-scout reached for the **source and its call sites**.
- casper-critic reached for the **report against itself**.

And the methods that produced wrong answers all did the same thing in reverse: formed a
view, then went looking for evidence to fit.

**ARTIFACT BEFORE NARRATIVE.** That is the transferable piece, and it is cheap — the
correct move in every case above was a *different first action*, not more effort.

## The failure mode is SHARED, and that is the finding

Tonight produced five instances of the same failure across four agents and the owner, in
five unrelated domains:

1. **owner** — wrote "structure costs nothing" into the family experiment *before running
   it*. The data said the opposite on both sides.
2. **owner** — concluded a glyph ramp "round-trips exactly" from **one monotone ramp**,
   which is the easiest possible input for an order-preserving map. A non-monotone field
   falsified it.
3. **owner** — wrote `4/196` where the formula wants `4/max(a,b)`: vertex count where side
   length was meant. A confident 30× error.
4. **snowball-scout** — headline "NO, none of the three has a per-cell mode menu", body
   two clauses later: qthe-codec has the only transmitted per-cell mode in any of the three.
5. **gpu-lab auditor** — per casper-critic, an invented headline statistic in a report whose
   whole premise is that numbers were checked.

The shape is not carelessness. It is **order**: conclusion first, evidence second, and the
evidence then read *through* the conclusion.

## The gate, and its honest limit

`grounding_lint.py` encodes the order as a mechanical check: **a claim is GROUNDED if the
artifact it rests on PREDATES the claim.** Timestamps, when receipts carry them.

Run against tonight's nine real claims:

```
GROUNDED 7   NARRATIVE_FIRST 0   UNSOURCED 2   (of 9)
```

**That result is not the one I expected, and it is more useful.** The problem was not
mostly *order*. It was **unsourced** claims (both of them mine) and **internal
inconsistency**.

And the linter's sharpest result is its own limit: `lane-u-headline` is timestamp-GROUNDED
— its receipt predates it — and it is still **wrong**, because the artifact it cites says
the opposite. **Timestamps catch ORDER, not SENSE.**

So the fleet needs **two gates that catch different things**:

| gate | catches | misses |
|---|---|---|
| **grounding lint** | a claim made before its evidence existed | a grounded claim whose evidence refutes it |
| **internal-consistency read** | a headline its own body refutes | a claim that is consistently wrong throughout |

Neither substitutes for the other. A receipt that predates a claim does not mean the claim
agrees with the receipt.

## Why the reviewers are a different KIND of cell

The producers and the verifiers are not the same process run twice. `casper-critic` and
`jevvy-auditor` were given the same artifacts and did something structurally different:
they checked the **claim against itself**, not against the world.

That is a distinct cell kind, and it is the one the fleet under-uses. Every finding in
tonight that was *caught* was caught by internal consistency, not by external checking —
because the external checks all passed while the internal ones failed.

**A fleet that only verifies outward will ship confidently wrong work at scale.** The
reviewers are the exocortex, but the exocortex of a *self*, not of the world.

## What this changes

1. **Write the prediction before the run, then make the run able to refute it.** The family
   experiment was *more* valuable for having a written-down wrong prediction than it would
   have been with none. That is the pre-registration doctrine, and it just earned its keep
   on a case where it was used by accident.
2. **Make the first action an artifact fetch.** Not a conclusion. The measure of a method
   is what it does first.
3. **Review inward as well as outward.** Give reviewers an explicit instruction to read
   each claim against the rest of its own report. Both of tonight's caught errors were
   visible that way and invisible from outside.
4. **Treat "grounded" as necessary, not sufficient.** A claim with a prior receipt is not
   thereby true. `grounding_lint.py` exists to be paired with a consistency read, and
   says so in its own output.
