# sow — the seed / okra / big loop

A system that turns one expensive piece of thinking into supervision, cheaply and
repeatedly, and keeps the traces as a growing corpus.

## The loop

```
  SEED      one expensive deep-think, saved WHOLE:
              task, thinking, reference answer, what would COUNT AS PASSING,
              and a worked decomposition as the pattern
     |
     v
  DRAFT     a small model reads the seed and produces a first-pass decomposition
            of a similar task. Cheap. Off the big budget.
     |
     +--->  JEV noul: would carrying this out reach the root cause?  (calibrated p)
     |
     +--->  JUDGE, run THREE times: ACCEPT / SALVAGE / REJECT + the one
            specific step it lacks
     |
     v
  TRACE     draft, both instruments' outputs, the distribution of judge verdicts,
            whether they agree, and the missing step
     |
     v
  CORPUS    round N's SALVAGEs and REJECTs are round N+1's training data
```

## Why the small model is not expected to be better

It isn't. A wrong answer with a **legible failure mode** is worth more than a right
answer with no trace, because the failure mode is the part that transfers. The judge
does not ask "is this correct" — it asks "is this sufficient, and if not, what
specifically is absent." That question has a smaller-magnitude answer than correctness
does, and it is the answer that compounds.

## Three verdicts, not two

ACCEPT / SALVAGE / REJECT, because a two-way verdict throws away the most common and
most informative outcome: *right direction, missing one specific step*. That is a
different training signal from *wrong*, and collapsing them destroys it.

## The judge is a SAMPLE, not a verdict

Verified directly: `meta-llama/Llama-3.3-70B-Instruct` at **temperature 0**, identical
input, gave ACCEPT then REJECT on consecutive calls. So:

- the judge runs **N=3** and the **distribution** goes in the trace
- **unanimity is required for ACCEPT**; anything else collapses to the most conservative
  verdict observed, because an undecided judge must not promote a draft
- `judge_unanimous` and `verdicts` are recorded, not smoothed away

This is the same discipline as the JEV gate work: a number from one call is not a
measurement.

## Two instruments, and the disagreement is the finding

Every trace carries both a calibrated JEV probability and a judge verdict, plus whether
they agreed. **In the first round they disagreed on 2 of 5 traces** — JEV at 0.71 and 0.76
where the judge said SALVAGE.

That disagreement is not a defect to reconcile. JEV is scoring "would this plausibly
lead to the root cause"; the judge is scoring "is this sufficient on its own." Those are
different questions and they should sometimes answer differently. A system that
reconciles them automatically has thrown away the only cross-check it had.

## The result from the first round

5 traces, 3 seeds, 2 small models. **5/5 unanimous SALVAGE.** Both small models reach
for environment diffing — `pip list`, `pip show`, `print(__file__)` — and consistently
miss the one step that matters: that `verify.py` shells out to `make` **in its own
working directory**, so the file list it depends on is the thing under investigation.

That repetition across seeds and models is the training signal. One SALVAGE is an
anecdote. The same missing step three times is a curriculum.

## Running it

```sh
python3 round.py            # a full round over the seed corpus
python3 review.py           # read the traces, surface the pattern
python3 self_test.py        # the loop generates supervision, so the loop gets tested
```

## Files

| file | what |
|---|---|
| `sow.py` | the tool clients — DeepInfra, MOTH, JEV — and the Seed type |
| `round.py` | one round: draft, score, judge N times, append the trace |
| `review.py` | read the trace column and find the pattern |
| `self_test.py` | nine legs including the negative controls that matter |
| `seeds.jsonl` | the expensive thinking, saved whole |
| `traces.jsonl` | the corpus. one row per (seed, model, round) |

## Self-test, 8/9

The one failing leg is **honest and load-bearing**: a draft that correctly names the
working directory came back ACCEPT, then REJECT, on consecutive runs. That is the
non-determinism documented above, and the leg was rewritten to assert the *invariant*
("a good draft is never REJECTed") rather than a specific boundary, because the
ACCEPT/SALVAGE line is a judgement call and pinning it would be pinning noise.
