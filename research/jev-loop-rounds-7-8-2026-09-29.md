---
title: Rounds 7-8 — the collapse is noul-specific, and there is a one-call recovery
date: 2026-09-29
scoreboard: 26 predictions, 15 confirmed, 11 refuted
---

Rounds 1-6 established that `noul` collapses in a batch. Rounds 7 and 8 ask whether that is
a property of the CALL or of the TYPE, and whether batching is recoverable.

## Round 7 — the collapse is `noul`-specific

| type | separate calls | one batched call | verdict |
|---|---|---|---|
| `noul`, related subjects | 0.62 / 0.31 | 0.25 / 0.25 | collapses |
| `noul`, **completely unrelated topics** (a software registry and a fishing catch log) | 0.58 / 0.55 | 0.43 / 0.43 | collapses |
| `choice`, two different questions | verifiable / bookkeeping | **verifiable / bookkeeping** | **survives** |
| `score`, strong vs empty shell | 2.59 / 1.56 | **2.90 / 1.05** | **survives** |

The `choice` probabilities inside a single call were **1.0 / 0.0** and **0.0 / 1.0** — that
is maximal separation, not a collapsed value. And `score`'s gap was *wider* batched (1.85)
than separate (1.03).

**The unrelated-topics row is the important one.** A software registry and a fishing
catch log have nothing to average over, and they collapse identically to two related
claims. So it is not averaging, and it is not position. The call returns one answer for
`noul` questions specifically.

## Round 8 — the one-call recovery

If only `noul` collapses, a two-axis gate can be built from ONE `choice` question whose
four criteria are the two axes plus the two single-axis cases. The `criteria` field is a
per-question specification, and it may be exactly what `noul` lacks.

```
both_axes        has a mechanism that could physically break AND a stranger could verify it
mechanism_only  has a real mechanism, but no stranger can verify it
externality_only a stranger could verify it, but there is no mechanism
neither          bookkeeping — asserted, with neither
```

**The argmax failed.** On the "neither" case the model picked `mechanism_only` at 0.56 over
`neither` at 0.43 — the second-highest. The signal was present in the distribution; the
argmax was the wrong readout.

**The derived rule got 3/3 where argmax got 2/3:**

```
promote  iff  P(both_axes) > P(neither)  and  P(both_axes) > threshold
```

| case | P(both) | P(neither) | derived | argmax |
|---|---|---|---|---|
| both | 0.77 | 0.00 | PROMOTES | both_axes |
| one | 0.00 | 0.01 | blocks | mechanism_only |
| **neither** | 0.00 | 0.43 | **blocks** | **mechanism_only** |

**And the collapse follows the type, not the call.** A single call mixing one `noul` with
one `choice`: the `noul` came back 0.39 — which is the batch mean of the two separate-call
values (0.71, 0.13) — while the `choice` in the same call survived intact. One call, two
types, one collapsed and one did not.

## The gate that follows

```python
# ONE call. choice type. Read the distribution, not the argmax.
r = post(state, {"c": {"type": "choice",
                       "instructions": "Which best describes the claim?",
                       "criteria": CRITERIA}})
p = r.answers.c.probabilities
promote = p["both_axes"] > p["neither"] and p["both_axes"] > 0.7
```

Live on the fleet's own three cases, one call each:

```
both      both=0.81 neither=0.00  PROMOTES
one       both=0.00 neither=0.01  BLOCKED (bookkeeping-leaning)
neither   both=0.00 neither=0.43  BLOCKED (bookkeeping-leaning)
```

Shipped as `tools/jev_gate2.py`, self-test 5/5, one call instead of two.

## What this changes about the operating rule

The rule from rounds 1-6 was "one question per call, always." That was correct for
`noul` and over-general: `choice` and `score` batch safely, and the collapse follows the
type rather than the call.

```
noul    -> one per call, always. Non-negotiable.
choice  -> batches safely. Read the DISTRIBUTION, never the argmax.
score   -> batches safely, but is a constant generator (see the KAT), so it grades
           nothing you would want to gate on.
mixed   -> safe if the gate does not depend on a noul in the batch.
```

## The eleven refuted predictions, all of them mine

| round | predicted | was |
|---|---|---|
| R1 | axes not complementary (0.6) | 0.18 |
| R2 | separation recovers to 0.25 | 0.74 |
| R3 | externality explains the 0.74/0.33 split | False |
| R3 | order is not the cause | False (moves up to 0.20) |
| R5 | lens batching is safe | False (lenses spread MORE) |
| R6 | usage is flat per call | False (~70 tokens/question) |
| R6 | some safe batch size exists | False (absolute) |
| R7 | the collapse hits choice | **False** |
| R7 | the collapse hits score | **False** |
| R8 | choice can label which axis is missing | **False** (argmax 2/3) |
| R8 | noul collapses even when mixed | True |

R7 and R8 are the ones that mattered: they refuted the rule I had just written down.
**Rounds 1-6 concluded "never batch". Rounds 7-8 found that was true for one type out of
three, and shipped a gate that is one call instead of two.**

## What I would run next

- **Does the same distribution trick work with a `score` question?** `score` returns
  per-level probabilities for a rubric. If a rubric whose levels are the two axes yields
  a usable graded signal, that is a third option with no `noul` in it.
- **Is the `noul` collapse a serving artifact?** It is suspicious that one type out of
  three is broken and the other two are fine. A direct API call with a raw HTTP client
  (bypassing anything that might reshape the request) would separate "the model does this"
  from "the endpoint does this".
- **What is the smallest `noul` batch that survives?** R6 found 2, 3, and 4 all collapse.
  But every one of those batches used the SAME instruction for all questions. If the
  collapse is an instruction-dedup artifact, distinct instructions per question might
  survive. That is the cheapest remaining test and would be the biggest win if true —
  it would restore batching at no accuracy cost.
