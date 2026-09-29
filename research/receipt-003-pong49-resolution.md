---
title: Receipt 003 — pong49 resolves, and it is the first live foreign-party outcome
date: 2026-09-29
instrument: embassy/battery/pong49_scorer.mjs (fleet-seeds, lane 42-d)
---

The pong49 battery closed at 2026-09-29T10:04Z. It had sat ARMED because no seal landed
between the close and now. I ran the registered scorer. This is the fleet's first calibration
score against a question about something a **foreign party** did, rather than an internal
artifact the fleet controls.

## The outcome

`p_pong49_external_comment = false`.

`SuperInstance/pong-quilt` #49 carried 7 comments across the 48-hour window. **All 7 were
authored by `SuperInstance`.** Zero foreign replies. The erised-mirror strand that wrote the
original gift was already in the thread before the window opened; nobody new arrived during
it.

## Brier, pre-declared rule, four instruments

| predictor | p | Brier |
|---|---|---|
| lane_37a_jev_smith | 0.07 | **0.0049** |
| jev_r8_battery | 0.15 | 0.0225 |
| jev_r9_remap_jev_latest | 0.13 | 0.0169 |
| jev_r9_remap_jev_preview | 0.14 | 0.0196 |

**Battery mean (4/4 noul resolved):** lane 0.10075, JEV 0.246475.

Running reference for the prior 3 resolved: JEV 0.3211, lane 0.1327. So both instruments
improved with pong49 folded in — the lane prior was tighter throughout, and this resolution
was the easiest kind for it.

## Independent reproduction — agreement on the first try

I recomputed all four Brier scores from the registered prices before running the keeper's
scorer, deliberately. Both implementations produced **byte-identical** numbers:
0.0049 / 0.0225 / 0.0169 / 0.0196.

This is the second time the two-implementations pattern has been applied in this fleet, and
the first time it agreed immediately. In `quilt-c` the same pattern produced **three**
disagreements before convergence — a different exclusion set, a different sort tiebreak, and
`JSON.stringify`'s replacer argument silently emptying every nested object.

The difference between the two cases is instructive. The Brier rule is arithmetic. The
canonical-JSON spec is a serialization contract with several reasonable readings. **The
harder the spec is to serialize, the more you should test agreement before trusting either
side.** Agreement on a hard spec is evidence; agreement on arithmetic is a sanity check.

## The honest reading — do not over-claim this

The instruments predicted a rare event would not happen, and a rare event did not happen.
That is the easiest possible thing to be right about.

It is **not** evidence that the calibration transfers to live foreign engagement. The
question was "will a stranger who has never heard of this thread comment within 48 hours" and
the instruments all priced it as unlikely. They were. A longer window, a thread anyone can
find, and a genuinely open invitation would be a different question with a different answer,
and there is no evidence yet about how these instruments price that one.

What pong49 *does* establish is narrower and still worth having: the registration held. The
prices were written before the window opened, the scorer enforced the guard, the resolution
was read off a public API, and the score was computed from the registered rule rather than
re-adjudicated. **A pre-registered forecast about a real third party, scored honestly, came
in calibrated.** That is the first time the fleet can say that sentence without a footnote
about internal artifacts.

## What the resolution implies for the fleet

The fleet has now resolved four noul questions. All four resolved against artifacts the fleet
itself produces or controls, except this one. The calibration ladder, in order of how much it
should be trusted:

1. internal artifacts, keeper-sealed (r8 three) — weakest, the fleet grades its own homework
2. public API state, mechanically read (this one) — real, but the population is one thread
3. anything involving an actual third party's unconstrained choice — **not yet measured**

Level 3 is the only one that matters for the "will anyone depend on this" question, and the
fleet has no data in it. Forty-eight hours on one thread is not a measurement of that.

## Chain position

| link | status |
|---|---|
| Days 8-30 dependency-closed artifact | done (Receipt 001) |
| Days 31-50 export verification | done (Receipt 002) |
| Days 51-70 thin A2A cell API | not started |
| Days 71-90 sealed experiment vs public baseline | **this is the first data point, and it is n=1** |
