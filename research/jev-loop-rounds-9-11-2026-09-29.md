---
title: Rounds 9-11 — the collapse is subject identification, and batching is recovered
date: 2026-09-29
scoreboard: 35 predictions, 24 confirmed, 11 refuted
---

Rounds 1-8 established that a `noul` batch collapses. Rounds 9-11 find out why, and remove it.

## Round 9 — three questions, three answers

**The collapse is the MODEL, not the client.** A raw HTTP request with a byte-identical
body gives A=0.38, B=0.38, spread **0.00** — identical to the client. Nothing in the
request path is reshaping anything.

**A `score` question whose rubric LEVELS are the two axes works.** Graded distributions,
correctly ordered:

| case | score | top level | probabilities |
|---|---|---|---|
| both | 2.53 | 3 | `{0:0.00, 1:0.03, 2:0.40, 3:0.57}` |
| one | 1.02 | 1 | `{0:0.01, 1:0.97, 2:0.01, 3:0.01}` |
| neither | 0.98 | 1 | `{0:0.03, 1:0.96, 2:0.01, 3:0.00}` |

A third gate option with no `noul` in it.

**Distinct instructions appeared to fix the collapse** — spread 0.24 against 0.00. That
looked like the end of it.

## Round 10 — the fix was not the fix

Distinct instructions at batch size 2: spread **0.03**. Collapsed. At 3 and 4: 0.80 and
0.79. And — the result that broke the theory — with the **same** instruction for all four
questions, the batch survived at spread 0.86.

Round 6 said identical instructions collapse. Round 10 said they do not. Both were measured.
The difference is structural, and it is not the wording.

## Round 11 — the mechanism

The one thing round 10's questions had that round 6's did not: **each question named its
subject.**

| batch | spread |
|---|---|
| identical wording, **unnamed** | **0.01** (collapses — round 6's shape) |
| identical wording, **subject-named** via a fixed prefix | **0.57** (works) |
| identical wording, but the prefix names the wrong subject | collapsed |
| one named question in a batch of four unnamed ones | the unnamed ones still collapse |

> **A question that applies to the whole state gets the whole state's answer, and N of
> those are the same answer. A question that says which part of the state it is about gets
> evaluated against that part. The instruction text does not have to differ — it only has
> to POINT.**

Same subjects, one call, four named questions:

```
{'A': 0.77, 'B': 0.77, 'C': 0.14, 'D': 0.14}   spread 0.63
```

Round 6 ran the identical four subjects unnamed and got 0.44/0.43/0.44/0.44, spread 0.01.

## The rule, finally

It was never "one question per call". It is **one QUESTIONED SUBJECT per question**, and
the subject has to be named.

```python
state = "; ".join(f"Subject {n}: {text}" for n, text in items)
questions = {
    n: {"type": "noul",
        "instructions": f"Regarding Subject {n}: {instructions}",
        "criteria": {...}}
    for n, _ in items
}
```

Shipped as `tools/jev_batch.py`, self-test 5/5, verified live.

## Why this was worth eleven rounds

A 4-question batch costs 545 input tokens against 336 for one. Four separate calls cost
1,344. So batching is **2.5x cheaper** than the "safe" one-per-call rule it replaced, at
the same ~200ms wall-clock — and the recovered values are accurate: max error 0.12 against
separate calls, well inside the 0.10-0.15 phrasing noise measured in round 1.

Every round from 1 to 6 was correct about the observation and wrong about the cause. The
refutations are what got here: R10's refutation ("survives at 3 and 4") forced the
question of why n=2 behaved differently, and that question turned out to be the wrong one.
The real question — "what is different about round 10's batches?" — was only visible
because a prediction had failed.

## A bug in the batch tool, caught by its own self-test

The first `jev_batch.py` rendered the prefix as `"Regarding {name}: "` while the state
labelled subjects `"Subject {name}: "`. The pointer pointed at a label that did not exist.
The live spread was fine, because the live instructions went through the same wrong
template consistently — so only the prefix-versus-state agreement was untested.

**A pointer that points at nothing is exactly the failure this rule exists to prevent**, so
it is now asserted. Fifth harness-failure-as-result this session. The pattern is consistent
enough to name as a rule:

> **Every rule you ship needs a negative control that exercises the rule's own failure mode,
> not a restatement of the happy path.** Six of the seven bugs this session were found by a
> check that could have passed while the rule was broken.

## The full rule set after eleven rounds

```
noul, subject NAMED in the question   -> batches safely. Cheapest path.
noul, subject unnamed                 -> collapses. Never do this.
choice                                -> batches safely. Read the DISTRIBUTION, not the argmax.
score                                 -> batches safely but is a constant generator; grades
                                        nothing you would want to gate on.
cost                                  -> a 4-question batch is 545 tokens vs 1344 for four
                                        separate calls. Batch.
```

Two of those four lines are the opposite of what rounds 1-6 concluded. That is the loop
working: eleven rounds, thirty-five predictions, eleven refutations, and the last three
rounds each overturned the previous round's conclusion.
