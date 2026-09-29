---
title: Six rounds of pre-registered experiments on the JEV oracle
date: 2026-09-29
loop: research/loop/loop.py
gate: tools/jev_gate.py
scoreboard: 18 predictions, 11 confirmed, 7 refuted
---

A research loop that gains instead of accumulating. Every round pre-registers its
predictions with numbers, runs them, debriefs, and the **refutations are carried forward
as the next round's design input**. Seven of eighteen predictions were wrong. The wrong
ones are the point — a loop that only confirms is a loop that cannot correct a belief.

## The result that matters

**Batching is categorically broken, and the fleet has been using it.**

| questions in one call | per-item spread | input tokens | wall-clock |
|---|---|---|---|
| 1 | — | 336 | 229 ms |
| 2 | **0.00** | 410 | 217 ms |
| 3 | 0.01 | 477 | 192 ms |
| 4 | 0.01 | 545 | 199 ms |

The API scores the **whole request** and reports it once per question. Two questions
in one call return the same number to two decimal places. And a 4-question call costs
**1.7x the tokens at the same wall-clock** for one number instead of four.

Batching is strictly worse on both axes. **One question per call, always.**

### What this invalidated

`jev_gate.py` asked its two axes in ONE call. That was not two axes — it was one
measurement reported twice, and the "min" of a number with itself is the number. The gate
has been fixed to make two separate calls, and re-verified live (mechanism 0.76,
externality 0.65, correctly diagnosed `weak on: ext`).

## The mechanism, located

Round 3 asked a whole-batch question alongside the per-claim questions in the same call:

```
per-claim : 0.44  0.44  0.44  0.45
whole-batch: 0.43
mean      : 0.4425
```

The per-claim answers are indistinguishable from each other AND from the answer to a
question about the entire batch. **The model is scoring one thing and reporting it N times.**

Round 5 tested whether "lens batching" rescues this — different questions, one state.
REFUTED: lens spread 0.20 vs subject spread 0.12. Lenses spread *more*, not less. There is
no framing that makes a multi-question call safe.

## What survives, confirmed

**The two-axis gate is honest.** On a claim where only the mechanism holds:

```
mechanism 0.66   externality 0.10   spread 0.56
```

It is not reporting one value twice. And asking each axis in its own separate call
reproduces the batched value within 0.03, so the fix is free of accuracy cost — it only
costs the extra call.

**The reproduction axis is not vestigial.** Round 1 predicted the axes were not
complementary; round 2 refuted that prediction by adding real independent reproduction to
an evidence description and watching the reproduction axis move **+0.63** (0.17 → 0.80)
while externality moved +0.09. The axis responds to the thing it names.

**Order does not matter across separate calls.** Reversing the order of four claims
preserved each score (0.51↔0.51, 0.54↔0.55, 0.41↔0.39, 0.31↔0.31).

## The refuted predictions, kept

Seven of eighteen. They are the reason the loop is worth running:

| round | predicted | was | the belief it encoded |
|---|---|---|---|
| R1 | axes not complementary (0.6) | 0.18 | the two axes carry the same information |
| R2 | separation recovers to 0.25 | 0.74 | separation helps less than expected — it fully recovers |
| R3 | externality explains the 0.74/0.33 split | False | it did not; the split was batching |
| R3 | order is not the cause | False | order does move things, by up to 0.20 |
| R5 | lens batching is safe | False | no framing of a batch is safe |
| R6 | usage is flat per call | False | usage scales ~70 input tokens per question |
| R6 | some safe batch size exists | False | no safe k exists; the rule is absolute |

## A bug in the loop itself, and what it says

Round 2's debrief reported two refutations that were artifacts. The scorer compared
predictions numerically, so a belief recorded as boolean `True` was graded as if it had
been the number 1. The fix ran into Python's type hierarchy: `isinstance(True, int)` is
`True`, so a numeric branch placed first swallows every boolean. **Refutations are the
only output in a research loop that can correct a belief, and the scorer was fabricating
them from a type error.**

This is the fourth time this session a reporting bug masqueraded as a result, and the
worst, because the others cost a column of output and this one cost the loop's integrity.

## The operating rule

```sh
# one question per call, always
p_mech = ask(claim, "is there a mechanism that would have to break?")
p_ext  = ask(claim, "could a stranger verify this with no access?")
score  = min(p_mech, p_ext)
promote = score > 0.7
```

Shipped as `tools/jev_gate.py`, self-test 7/7, and re-verified live after the fix.

## Round-by-round

### Round 1 — three questions about the gate that were worth asking  (2 confirmed, 1 refuted)

- **inert-axis-responsiveness** — CONFIRMED (predicted 0.3, actual=0.25)
- **preview-agreements** — CONFIRMED (predicted 0.2, actual=0)
- **axis-complementarity** — REFUTED (predicted 0.6, actual=0.18)

### Round 2 — what the reproduction axis measures, and why batched state collapses  (2 confirmed, 1 refuted)

- **repro-is-vestigial** — CONFIRMED (predicted 0.4, actual=0.63)
- **batching-is-a-dilution** — CONFIRMED (predicted True, actual=1)
- **separation-is-the-remedy** — REFUTED (predicted 0.25, actual=0.74)

### Round 3 — was the 0.74/0.33 split the model being right, or the setup being broken  (1 confirmed, 2 refuted)

- **externality-not-position** — REFUTED (predicted True, actual=False)
- **order-is-not-the-cause** — REFUTED (predicted True, actual=False)
- **batch-scores-the-batch** — CONFIRMED (predicted True, actual=True)

### Round 4 — is the batch limit about question count or state volume  (3 confirmed, 0 refuted)

- **count-is-the-culprit** — CONFIRMED (predicted True, actual=True)
- **two-questions-are-safe** — CONFIRMED (predicted False, actual=False)
- **separate-beats-batch** — CONFIRMED (predicted True, actual=True)

### Round 5 — is the two-axis gate valid, and can lens-batching be made safe  (2 confirmed, 1 refuted)

- **lens-batching-is-valid** — REFUTED (predicted True, actual=False)
- **two-axis-gate-is-honest** — CONFIRMED (predicted True, actual=True)
- **agreement-under-repetition** — CONFIRMED (predicted True, actual=True)

### Round 6 — the cost of the one-question rule, and whether any batching is safe  (1 confirmed, 2 refuted)

- **n-questions-cost-is-flat** — CONFIRMED (predicted True, actual=True)
- **usage-reports-per-question** — REFUTED (predicted True, actual=False)
- **three-questions-are-safe** — REFUTED (predicted False, actual=True)

## What I would run next

- **Does the collapse apply to `choice` and `score` too, or only `noul`?** Everything above
  is `noul`. If `choice` discriminates inside a batch, a multi-axis gate is recoverable
  with a mixed-type call.
- **Is the collapse a serving artifact or a property of the model?** A batched call where
  the questions are on *completely different topics* (not near-duplicates) would separate
  "averaging" from "the model only reads the first instruction."
- **Does a longer `instructions` field break the collapse?** If the collapse is a
  last-instruction-wins artifact, a per-question disambiguation prefix may fix it — and
  that would restore batching at no accuracy cost.
