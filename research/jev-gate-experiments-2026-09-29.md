---
title: Six experiments on the canon gate — and a replacement for it
date: 2026-09-29
instrument: jev_gate.py
subject: "the fleet's canon gate is `p > 0.7` on a single JEV noul call"
---

The fleet has used `p > 0.7` on one `noul` call as its canon gate since the doctrine was
written. It had never been characterised beyond the question types themselves. Six
experiments, ~90 API calls, on the fleet's own claims.

## 1 — Test-retest stability: the gate does not need averaging

Six identical calls per claim, six claims chosen to straddle 0.7.

| claim | mean | min | max | sd | flips across 0.7? |
|---|---|---|---|---|---|
| sha256 + append-only + byte-prefix | 0.598 | 0.590 | 0.620 | 0.011 | no |
| test suite + artifact publish | 0.357 | 0.350 | 0.370 | 0.007 | no |
| method with a comment | 0.495 | 0.490 | 0.500 | 0.005 | no |
| "the team is careful" | 0.215 | 0.210 | 0.220 | 0.005 | no |
| suite with an always-pass step | 0.290 | 0.280 | 0.300 | 0.008 | no |
| "verified by reading it once" | 0.223 | 0.210 | 0.230 | 0.007 | no |

**0/6 claims flipped the verdict on repeat. sd 0.005-0.011.** Repeat-calling to reduce
noise buys essentially nothing. Do not average ten calls; you will pay 10x for 1.005x.

## 2 — The scale has a ceiling AND a step in it

A ladder from nonsense to a Lean 4 proof of the property, all one question shape:

| designed strength | p |
|---|---|
| nothing relevant | 0.123 |
| a file exists | 0.090 |
| lines sorted alphabetically | 0.080 |
| lines record a prediction | 0.290 |
| lines are sha256-sealed | 0.403 |
| + append-only by construction, fail-closed, byte-prefix proven | **0.970** |
| + second independent implementation, conformance test | 0.950 |
| + published machine-checked Lean 4 proof | 0.933 |

Two findings. **Non-monotonic at the bottom** — a file that is merely "sorted alphabetically"
is more confidently *not* tamper-evident than a file that merely exists, which is correct
discrimination. And **non-monotonic at the top** — adding a kernel-checked proof *lowers*
the score. The scale saturates.

## 3 — The transition is caused, and the cause is the guarantee

One clause added per rung, monotone, 3 samples each:

| rung | p | |
|---|---|---|
| a registry file | 0.030 | |
| + records one prediction | 0.050 | |
| + lines sha256-sealed | 0.300 | |
| + editing breaks the hash | 0.240 | |
| **+ the file is append-only** | **0.930** | **+0.690** |
| + validator proves byte-prefix | 0.930 | +0.000 |
| + validator fail-closed | 0.940 | +0.010 |
| + byte-prefix across commits | 0.940 | +0.000 |
| + independent reimplementation | 0.920 | -0.020 |

**The gate is a structural completeness test, not a quality scale.** It fires when the
description contains a mechanism AND an explicit guarantee. Everything after that is inert:
byte-prefix proof, fail-closed validation, a second implementation — all worth doing, all
worth nothing to this instrument.

## 4 — A single question is a tautology tester, not a verifier

Four question shapes x four evidence states.

| evidence | composite | primed | decomposed (min) | bare guarantee |
|---|---|---|---|---|
| mechanism + guarantee | 0.960 | 0.950 | 0.940 | 0.980 |
| mechanism only | 0.620 | 0.460 | 0.200 | 0.520 |
| **guarantee only** | 0.270 | 0.210 | 0.190 | **0.980** |
| neither | 0.080 | 0.120 | 0.060 | 0.110 |

The bare column is the finding. Ask "Is the registry append-only?" of a description that
says *"a registry that is append-only"* and it returns **0.980**. A single-question gate
cannot distinguish a claim from a restatement of itself.

**The status quo (composite) is the best of the three usable shapes.** Priming the wording
made it slightly worse. Decomposition is equal on this set and better on the next one.

## 5 — The payoff: decomposed, min-aggregated, on the fleet's OWN gameable claims

The five claims the externalisability audit found satisfiable by bookkeeping, plus two
solid controls. Both axes asked in one call.

| claim | composite | two-axis (min) | mech | ext | composite gate | two-axis gate |
|---|---|---|---|---|---|---|
| M1 cite a mine id + boilerplate | 0.180 | 0.170 | 0.250 | 0.170 | blocks | blocks |
| M4 budget cap line in every header | 0.130 | 0.100 | 0.170 | 0.100 | blocks | blocks |
| M9 at least half the queue | 0.180 | 0.070 | 0.160 | 0.070 | blocks | blocks |
| M5 at most 1 death per wave | 0.110 | 0.090 | 0.170 | 0.090 | blocks | blocks |
| M6 opens a PR with the right words | 0.240 | 0.280 | 0.280 | 0.280 | blocks | blocks |
| **S1 signed tag, clean clone reproduces** | 0.700 | **0.760** | 0.760 | 0.760 | **blocks** | **promotes** |
| S2 release verifier + self-test | 0.540 | 0.290 | 0.530 | 0.290 | blocks | blocks |

**Composite misclassifies 2/7. Two-axis misclassifies 1/7.** The two-axis gate promoted the
signed-tag claim at 0.760 that the composite capped at exactly 0.700, and the sub-answers
say which half failed rather than returning a bare number that cannot be argued with.

## 6 — Batch order: safe, with a caveat

Five claims, each asked in five batches at five different positions.

| claim | mean | range | p by slot |
|---|---|---|---|
| C1 signed tag | 0.326 | 0.120 | 0.31 0.40 0.34 0.28 0.30 |
| C2 budget cap | 0.324 | 0.110 | 0.31 0.39 0.34 0.28 0.30 |
| C3 byte-prefix validator | 0.324 | 0.120 | 0.31 0.39 0.34 0.27 0.31 |
| C4 nearest prior | 0.322 | 0.110 | 0.31 0.39 0.33 0.28 0.30 |
| C5 second implementation | 0.332 | 0.120 | 0.32 0.40 0.35 0.28 0.31 |

There IS a small position effect (range ~0.12) — **but it is identical across all five
claims in a batch.** Slot 2 is always highest, slot 4 always lowest. So:

- comparing claims **within one call**: ranking is exact, position cancels
- comparing a claim **across calls at different positions**: ±0.06 of noise

**Rule: always compare claims asked in the same call. Never compare across calls.**

## The replacement gate

```
axis 1  MECHANISM     is there something that would physically have to break for this to be false?
axis 2  EXTERNALITY   could a stranger verify it with no access to this project?
gate    min(axis1, axis2) > 0.7
```

`min` is the point. A claim is only as strong as its weaker half, and the halves fail for
unrelated reasons: a real mechanism nobody outside can reach (a signed tag on a private
repo), or full external reach with no mechanism (a public dashboard asserting a number).

Shipped as `jev_gate.py`, self-test 7/7, with a circularity pre-filter that asks the claim's
own guarantee back at it.

## The honest limit

Run live, the solid claim S1 scored **0.68** where the experiment scored 0.78. A 0.10 swing
from phrasing alone. The two-axis gate is better than the composite, not reliable: claims
sitting near 0.7 will flip on rewording, and rewording is cheap.

**So the gate should be used for ranking and diagnosis, not as a single yes/no.** Its real
value is that it says *which* half failed, which is the thing a single number cannot.

## What I would test next

- **Does the inert region carry signal?** Experiment 3 showed evidence past the guarantee is
  inert. If the instrument is provably insensitive to independent reimplementation, then a
  second axis asking specifically about independent reproduction should show a response where
  the composite showed none. If it does, the two axes are complementary rather than
  redundant.
- **Threshold placement.** Given 0.10 of phrasing noise, is 0.7 the right cut, or should
  promotion require 0.85 plus both axes clear? The corpus is small; this needs more.
- **Cross-model agreement.** Ask both axes on `jev-latest` and `jev-preview` and require
  both to clear. Two models agreeing is a stronger gate than one model twice, and it is
  cheap.
