---
title: The growing pincher — the cell that learns to bypass the LLM, and withdraws when it goes wrong
date: 2026-09-29
code: research/growing-pincher/growing_pincher.py (cd0c681636)
selftest: selftest_pincher.py (c70c7aa99b), 14/14 including four negative controls
---

In the route, the pincher sits between grammar-cleanup and the LLM. Its job starts as the
obvious one: pinch the route off when the answer is already known, so the LLM is not called
at all. The interesting part is what happens to a pincher that runs for weeks.

## The design

A pincher with a **policy**, not a cache:

- a **signature** that decides when two inputs are the same question
- a set of known answers, each with a **provenance** (a receipt, not a vibe)
- a per-signature accuracy record
- a **withdrawal rule**: a pincher that starts missing stops pinching

The withdrawal rule is the whole design. Without it this is a cache with extra steps.

## The signature is structural, on purpose

```
How many cells are in the 4D graph?     ->  many cells #d graph
how many cells are in the 4d graph      ->  many cells #d graph
What is the 47 Hz resonance band for?   ->  # hz resonance band
```

It normalises case, digits and a small stop list. That means it **under-matches** — two
genuinely different questions can share a signature, and the accuracy record catches that —
and it **never silently over-matches**, because you can read exactly what it ignored.

A semantic cache hides its decision. This one shows it. That matters because the whole
argument for a routing book is that a decision should be a reading you can read.

## What it is not

Not a vector store. The signature is inspectable, which means a wrong bypass can be
diagnosed by reading one line rather than by re-running an embedding search and hoping.

## The demonstration — a pincher that grows

```
phase 1  learning          every route passes, nothing is known yet
phase 2  confident         bypass  resonance band   recent 1.00 >= 0.85 (lifetime 1.00)
phase 3  the world drifts  pass    resonance band   recent 0.29 < 0.85 (lifetime 0.86)
         ^ it WITHDREW. A pincher that cannot be wrong is a pincher that is wrong.
phase 4  the answer holds  bypass  resonance band   recent 0.98 >= 0.85 (lifetime 0.78)
phase 5  what it knows:    live      resonance band  lifetime=0.78 recent=0.98
                           withdrawn  many cells graph  lifetime=0.00 recent=0.00
```

## The number that carries the design

At the end: **lifetime 0.78, recent 0.98.** The pincher is live.

A cumulative average would have read 0.78 — below the 0.85 threshold — and the pincher
would have stayed withdrawn forever, because a single mistake made early is still being
averaged in four hundred calls later. That is wrong for a cell in a live route: the decision
is about the *next* call, so recent behaviour is the only thing that predicts it.

So the policy decides on a **decayed** accuracy and reports both. The gap between them is
the story: this pincher was reliable, stopped being, and became reliable again.

## Two source bugs, both found by the self-test

1. **A double-counted denominator.** Both `route()` and `observe()` incremented `n_asked`.
   A route DECIDES; an observe REPORTS. Counting both meant every interaction inflated the
   denominator twice, so a perfectly reliable pincher could never accumulate enough
   evidence to bypass at all. The bypass path was unreachable in practice and the tests
   did not notice because they were checking the wrong field.
2. **Cumulative accuracy cannot express recovery.** See above. Fixed with an exponential
   moving accuracy, which is the correct semantics for a cell making a decision now.

## A test that could not fail, and how it was found

**Fault injection caught it.** Three faults were injected; two were caught. The third —
**removing `min_asks` entirely** — left all thirteen legs green.

The leg meant to cover it asserted that `observe()` before any `route()` is a no-op. That is
true, and it has nothing to do with the evidence floor inside the policy. So no test
exercised the law that a perfect record below `min_asks` still refuses to bypass.

Rewritten to drive a signature to a *perfect* record and still demand a pass, and paired
with a negative control that flips `min_asks=0` and demands the opposite. Both now fire.

> **A passing suite that cannot fail is worse than no suite, because it is consumed as
> evidence.** The only defence is to break the thing on purpose and confirm the suite
> notices.

## Fail-closed receipts

| injected fault | caught by |
|---|---|
| withdrawal rule removed | 3 legs (`STOPS bypassing`, `recovers`, `ALWAYS wrong never bypasses`) |
| `min_asks` removed | 1 leg, after the rewrite above |
| ledger stops recording | 3 legs (every decision recorded, bypass flags LLM, health counts) |

## What it costs

Three or four LLM calls avoided per confident signature, and one added back whenever the
pincher is wrong and does not know it yet. That is the entire trade, and the ledger is
where you can watch it happen rather than infer it from a bill.

```sh
python3 growing_pincher.py --self-test
python3 growing_pincher.py --demo
```

No dependencies. 14 legs. Every law has a negative control, and one of them exists only
because a fault injection got past the first version.
