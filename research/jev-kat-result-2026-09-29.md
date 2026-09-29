---
title: JEV known-answer control — the canon gate instrument, finally measured
date: 2026-09-29
instrument: labs/jev-kat/jev_kat.mjs (AI-Writings PR #70)
---

## Why this exists

The fleet promotes a claim to canon when the JEV oracle returns p > 0.7. That is a
gate, and a gate is only as good as the instrument behind it. The instrument offers three
question types. Until today, exactly one of them had ever been used, and none of them had
ever been characterised.

A known-answer control is the cheapest possible test of an instrument: feed it cases whose
correct answer you already know, and see whether it finds them. The keeper's own lode
protocol already requires this of its Elo scorer — "the scorer itself is deterministic and
stranger-verifiable", KAT 1/1. JEV had no equivalent.

## Result

| type | verdict | bar |
|---|---|---|
| `noul` | **PASS** | regime B (judgement vs stated criteria) 3/3, spread 0.85, strongest ranked highest |
| `choice` | **PASS** | correct pick, confidence 1.00, probability spread 1.00 |
| `score` | **FAIL — does not discriminate** | spread 0.015-0.035 across a range that should span the rubric |

### `score` does not discriminate — replicated twice

| subject | run 1 | run 2 |
|---|---|---|
| numpy | 2.500 | 2.505 |
| c99_ref_port (1,285 assertions, green CI, one-command verify) | 2.485 | 2.520 |
| empty_shell (one README, "work in progress", no code) | 2.500 | 2.485 |

Expected ordering `numpy > ref_port > shell`. Actual ordering **wrong in both runs**, and
**rank-unstable across repetitions**. An empty shell scores the same as NumPy.

The confidence sat at ~0.62 in every case and **did not drop to signal the failure**, which
is exactly what a considered answer looks like. This is the same number the fleet's own
ONBOARDING.md warns about — "trust the ranking, not the confidence level" — now with a
measurement behind it.

### `noul` is good in the regime the gate uses, and bad in a regime the gate avoids

Regime B (judgement against stated criteria) is where the p>0.7 gate lives. It scored 3/3
with 0.85 spread, and the discriminator works: a byte-prefix-verified registry description
scored 0.89, while a strawman saying "the team is careful and does not usually change old
entries" scored 0.04. That is the gate biting.

Regime A1 (facts the model cannot possibly know) is where it fails. Asked whether an unknown
private repo has more than 1000 stars, it returned 0.05 — a confident "no" about something it
cannot know. **Harmless for the canon gate, which asks questions answerable from the
description. Dangerous for any use as a fact-checker.**

The verdict is therefore per-regime, not per-type. A KAT that collapsed the regimes reported a
false "noul is broken."

## The generalisable lesson

> **Discrimination and rank-stability are different properties. Measure the one you depend on.**

A constant output cannot serve an absolute threshold gate (`p > 0.7`) because the threshold has
nothing to bite on. It may still serve a *ranking* gate if the ordering survives repetition.
`score` fails both here, but the distinction matters the next time one of these types looks
degenerate: the first question is not "is this broken" but "which property am I depending on."

This is also the second independent measurement of JEV misbehaving. The first was the oracle
scoring its own best 90-day recommendation at 0.69 — below the fleet's own 0.7 gate.

## Two bugs this KAT found in itself

Both would have been reported as instrument failures. Neither touched the model.

1. **Wrong expected value.** The first version bucketed "no prior, genuinely unknowable" together
   with "no prior, but widely known" (numpy), and scored the model's *correct* confidence in the
   second as an overconfidence failure. A KAT whose expectations are wrong is worse than no KAT,
   because it reports false failures with the authority of a test.
2. **Meta-question instead of fact.** Regime A1 was originally phrased "can it be *determined*
   whether this repo has 1000 stars?" — which invites a confident "no", and a confident "no" there
   is the right answer, which the test then scored as overconfidence. A calibration probe must ask
   about the fact, not about the knowability of the fact.

Both are the same lesson from a different direction: the KAT is a measurement, and a measurement
has to be checked before it is believed.

## What this does and does not change

**Does not change:** no existing gate is broken. A fleet-wide grep found no `systemone`
`score`-based gating path in use.

**Does change:** `score` is load-bearing in the docs and unverified. The fix is cheap — run this
KAT in CI before anything is allowed to gate on `score`. That is the same discipline the keeper
already applied to its own scorer, applied to an instrument the keeper does not own.

## Reproduce

```sh
export TYPESAFEAI_KEY=...
node labs/jev-kat/jev_kat.mjs
```

Retries on 503 with backoff and reports the retry count. A control harness that aborts on a
transient edge blip measures the network, not the instrument — that is a bug this harness had
and fixed during the run.
