# quilt-widening

**A quilt that decomposes itself into wider arrays, where every widening is a named,
rewindable, observable action** — and every widening is graded on whether it added
*structure* or *restatement*.

## The loop

```
seed-state  ->  propose decomposition  ->  NAME every child  ->  observe (one batched call)
    ^                                                                          |
    +------------------------- rewind <--- nudge <--- did it add anything? -----+
```

The trace of that loop **is** the seed-state material for the next generation.

## The two things that had to be right

**1. The subject must be named, and the API enforces it.** `POST /v1/systemone` rejects a
request with no top-level `state` field (422, `body.state required`). The array is a
first-class part of the request, and each question has to say **which element** it is about:

```json
{"model": "jev-latest",
 "state": "Subject 0: .... Subject 1: ....",
 "questions": {"subject_0": {"type": "noul",
                             "instructions": "Regarding Subject 0: <question>",
                             "criteria": {"true": "yes", "false": "no"}}}}
```

This is not a style preference. It is the operational contract found across eleven
pre-registered rounds: a question that applies to the whole array and does not point at a
part gets the whole array's answer, N times.

**2. The verdict is NOT spread.** This is the correction that made the instrument real.

My first version printed "subjects DO NOT DISCRIMINATE" off a low within-array spread and
reported the oracle as flat. Measured live, the spreads were **0.04 and 0.05** for a
redundant array and a distinct one — indistinguishable — while the **levels were 0.19 and
0.86**. The oracle was not flat. **It was correctly reporting that my own decomposition
had produced restatement.**

So the statistic is discrimination **between** arrays, not heterogeneity **within** one:

```
discrimination = | level(real array) - level(homogeneous control array) |
```

A homogeneous control array — every element saying the same thing — is asked in the same
call. If the real array scores the same, the array carries no information. That is
measurable, and it is a statement about the DECOMPOSITION rather than about the oracle.

## Measured, live

```
round 2  width 5  level=0.488  control=0.292  discrimination=0.20  spread=0.39
         array is REDUNDANT -- this decomposition added restatement, not structure
round 3  width 6  level=0.488  control=0.282  discrimination=0.21  spread=0.40
         array carries INFORMATION
```

Two rounds of self-decomposition added nothing. The third crossed the threshold. **That is
the instrument working**: a widening that adds restatement is reported as restatement, so
the next generation's seed-state is not quietly worse than its parent's.

## Rewind

The trail is append-only and the head is a **prefix length**. `rewind(to_seq)` shortens the
prefix; nothing is deleted, because the record of having tried is the point.

This cost one bug worth recording: the first implementation appended the rewind marker
*inside* the prefix, so replaying re-applied the very action it was undoing — a rewind that
rewound nothing, which is the worst version of that bug because it looks like it worked.
The live trace shows the real behaviour: `4 -> 3 live cells, 4 actions retained`.

## Run it

```bash
python3 widening.py --dry --rounds 3          # no oracle calls
python3 widening.py --rounds 4 --width 3 --split 2
```

Writes `widening_trace.json` — actions, cells, and the rewind history.

## Limits

- One oracle, one model, one question shape. The discrimination ratio is a property of the
  question and the array together, not of the array alone.
- Subjects are generated, not learned. The seed text is fixed, so this measures whether the
  *instrument* can tell structure from restatement — not yet whether a decomposition it
  invents is a good one.
- The control costs one extra call per round. That is the price of not fooling yourself,
  and it is cheaper than shipping a redundant array and calling it an insight.
