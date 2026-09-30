# The CRDT results: one headline is an identity, and one number does not come back

**Paper**: `white-papers/CRDT_Research_Package` (30-round simulation, 196 runs, with stored
result JSONs and four rounds of peer review).
**Method**: fetched the simulations, ran them three times, diffed against the stored
summary. No writes to the repo. Token was dead for authenticated calls; the repo is public
and everything here was read unauthenticated.

## Finding 1 — the headline is a tautology, not a measurement

```
run1  Average Latency Reduction: 98.4%
run2  Average Latency Reduction: 98.4%
run3  Average Latency Reduction: 98.4%
stored (2026-03-13)  latency_reduction_pct = 98.37
```

**Bit-identical across three independent runs and across four months.** And the reason is
in the stored summary itself:

```
mesi_stats  avg_latency = 122.5757   min = 83.9887   max = 128.9088
crdt_stats  avg_latency =   2.0000   min =  2.0000   max =   2.0000
```

CRDT latency has **zero variance** — identical average, minimum and maximum across 98
simulations. That is not a simulated quantity; it is a constant the simulator compares a
*measured, varying* MESI latency against. So:

> **"98.4% latency reduction" is the arithmetic identity (122.58 → 2.0), not an experimental
> result.** It would be 98.4% if you ran the simulation once or a thousand times, and it
> would be 98.4% if the CRDT side were literally a hardcoded 2.

**A number that cannot vary is not evidence.** It is the same failure as the fleet's JEV
`score` primitive — a constant generator that looks exactly like a considered answer.

## Finding 2 — the second number does not come back, and it is not noise

```
run1  Average Traffic Reduction: 45.5%
run2  Average Traffic Reduction: 45.5%
run3  Average Traffic Reduction: 45.5%
stored (2026-03-13)  traffic_reduction_pct = 52.24
```

My first reading was that the stored result was simply stale. **It is worse than stale:**
the three runs agree *exactly* with each other at 45.5%, so 45.5 is the reproducible value
**in this environment** and the stored **52.24% is the outlier.** A seven-point gap that
is stable across runs is not variance.

`crdt_vs_mesi_simulator.py` contains **no seed anywhere** — the only seeded script in the
package is `rigorous_traffic_analysis.py` (`seed=42+i`). So the runs *should* be stochastic,
and yet three unseeded runs are bit-identical.

> **An unseeded "simulation" that is bit-reproducible is not simulating anything stochastic.**
> Either the randomness does not reach the reported quantities, or the pipeline is
> deterministic in a way its own framing does not admit.

## What the four review rounds did not catch

The package carries `iteration1_technical_review` through `iteration4_final_review`. Four
rounds of review did not identify that the headline is an identity, or that a headline
number is unstable. **A review trail measures how much reviewing happened, not what it
caught** — the same distinction `artifact-first` draws between a claim and the artifact
that backs it.

## What would settle it

1. Seed the simulator and run 100× — if traffic reduction has any real variance, it is a
   measurement; if it does not, the simulator is deterministic and the claim is a formula.
2. Replace the CRDT latency constant with a measured value, or state plainly that the
   CRDT side is assumed constant and the headline is therefore an assumption restated as a
   result.
3. Re-derive 52.24% or retract it. Right now the corpus's most quotable number cannot be
   produced by the code that ships beside it.

## Scope of this check

This is one paper, run three times, on one machine. It does not establish that the rest of
the corpus is unsound — **it establishes that the corpus contains at least one headline
result which is an identity rather than a measurement, which is enough to require that
every other headline be re-derived before it is quoted.** That is the check the wheel
called `runnable` and it is now the top open item.
