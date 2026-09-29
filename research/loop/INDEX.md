# The loop — index

A research loop that gains instead of accumulating: every round pre-registers its
predictions with numbers, runs them, debriefs CONFIRMED/REFUTED, and carries the
refutations forward as the next round's design input.

**35 predictions, 24 confirmed, 11 refuted, across 11 rounds.** The refutations are the
value; a loop that only confirms cannot correct a belief.

| round | question | C | R |
|---|---|---|---|
| 1 | three questions about the gate worth asking | 2 | 1 |
| 2 | what the reproduction axis measures, why batched state collapses | 2 | 1 |
| 3 | was the 0.74/0.33 split the model being right or the setup being broken | 1 | 2 |
| 4 | is the batch limit about question count or state volume | 3 | 0 |
| 5 | is the two-axis gate valid, can lens-batching be made safe | 2 | 1 |
| 6 | the cost of the one-question rule, and whether any batching is safe | 1 | 2 |
| 7 | does the collapse hit choice and score, or only noul | 1 | 2 |
| 8 | can a choice question carry the two axes in one call | 2 | 1 |
| 9 | score-as-rubric, serving-vs-model, distinct-instruction batches | 3 | 0 |
| 10 | how far does the distinct-instruction fix go, and is it accurate | 2 | 1 |
| 11 | is the collapse about subject identification, not instruction dedup | 3 | 0 |

## The findings, in order of how much they changed practice

1. **Batching collapses for `noul` — unless each question names its subject.**
   Unnamed: spread 0.01. Subject-named: spread 0.57. Same four subjects, one call.
2. **`choice` and `score` batch safely**; the collapse is `noul`-specific, and it is a
   property of the model, not the client (raw HTTP reproduces it exactly).
3. **Read the DISTRIBUTION, never the argmax.** A `choice` question's argmax mislabels the
   "neither" case; `P(both_axes) > P(neither)` gets 3/3 where argmax gets 2/3.
4. **Batching is 2.5x cheaper than one-per-call** once the prefix is there (545 tokens vs
   1344 for four).
5. **The gate is a step, not a scale.** +0.690 in the one rung that adds the GUARANTEE
   statement. Evidence past that is inert.
6. **A bare guarantee question is a tautology tester, not a verifier** — 0.98 on a
   description that merely restates it.

## The operating rule

```
noul, subject NAMED in the question   -> batches safely. Cheapest path.
noul, subject unnamed                 -> collapses. Never do this.
choice                                -> batches safely. Read the DISTRIBUTION, not the argmax.
score                                 -> batches safely but is a constant generator; grades
                                        nothing you would want to gate on.
```

Two of those four lines are the opposite of what rounds 1-6 concluded.

## Files

| file | what |
|---|---|
| `research/loop/loop.py` | the loop: pre-register, run, debrief, carry refutations forward |
| `research/loop/loop_state.json` | all 11 rounds with predictions, results and debriefs |
| `research/loop/round1.py` .. `round11.py` | every experiment, re-runnable |
| `tools/jev_gate2.py` | one-call choice gate with a derived distribution rule |
| `tools/jev_batch.py` | safe batching: the prefix rule |
| `tools/jev_gate.py` | the two-noul-axis gate (two separate calls) |
| `research/jevlab/jev_gate.py` | the original KAT that found the score-type collapse |
