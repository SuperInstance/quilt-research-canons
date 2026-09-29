---
title: MOTH Quantum QPIXL round trip — a third-party check, AND ITS OWN CORRECTION
date: 2026-09-29
subject: live runs against api.mothquantum.com, engine qpixl-v1
---

## Status: PARTIALLY CORRECTED

This document was first written claiming that a glyph ramp round-trips **exactly** through
the QPIXL encode/decode. A follow-up run on non-monotone 2-D fields **falsified that
generalisation**. The correction is recorded below rather than quietly edited out, because
the first claim was shipped and the failure mode is the useful part.

## Why this was worth running

`research/qpixl-ascii/` reduces a glyph frame by cancelling identity terms. That
reduction is classical and reproducible — but a reduction only ever checked against
itself has not been checked. This is the third-party run.

## API contract (four wrong guesses to find; the errors are legible enough to record)

```json
{"mode": "emu",
 "params": {"values": "[0.0,0.143,0.286,0.429,0.571,0.714,0.857,1.0]",
            "machine": "aer", "shots": 2048}}
```

- `values` is a **STRING** and must be **wrapped in `[..]`**. A bare comma list fails
  `unparseable_values`; a bare JSON array body fails `expected object`.
- 4×4 fails `group_count_mismatch`: *"4 groups given but the machine has 5 groups; call
  `list_groups(values, machine)`."* **The qubit grouping is a property of the MACHINE, not
  of your array's shape, and cannot be inferred from dimensions.**
- 1×5 fails `insufficient_qubits`: *"5 values exceed aer's data-qubit capacity of 1."*
- `is_async: false`, yet a `job_id` is still returned and must be polled. A failed job's
  `/result` returns a bare **409**; the useful detail is in `status.progress.detail` and
  `status.error.message`.

## Run 1 — the 1-D ramp (this is what I first claimed from)

```
 i  input i/7     output     delta
 0     0.0000     0.0000   +0.0000
 1     0.1429     0.1372   -0.0057
 2     0.2857     0.2729   -0.0128
 3     0.4286     0.4016   -0.0270
 4     0.5714     0.6182   +0.0467
 5     0.7143     0.7002   -0.0141
 6     0.8571     0.8514   -0.0058
 7     1.0000     1.0000   +0.0000
```

max |out−in| = 0.0467, only 2/8 exact, **output strictly increasing**. On this input an
8-level ramp round-trips exactly.

## Run 2 — the hard case, and the correction

A monotone ramp is the easiest possible input for an order-preserving map. These fields
have crossing neighbours and ties.

| case | order inversions | nearest-level glyphs identical? |
|---|---|---|
| 2×2 checker | **0** | yes |
| 2×2 ramp | **0** | **NO** |
| 2×3 crossing | **0** | yes |
| 2×4 crossing | **0** | **NO** |

**1. Order IS preserved.** Zero inversions in every field tested, including 2×4 with
crossing neighbours. This part is real and it is the useful part: the map does not
scramble a frame.

**2. Ties are BROKEN.** `[0.0, 0.5, 1.0, 1.0, 0.5, 0.0]` came back as
`[0, 0.504, 1, 1, 0.524, 0]`. The two inputs that were both exactly 0.5 are now 0.504
and 0.524. The quantum step is noisy in magnitude, so identical inputs land at different
outputs and **which output belongs to which input is not recoverable from the order
information.**

**3. That kills the elegant argument.** "A glyph is a rank, not a measurement" was the
reasoning behind the first claim. But a real glyph frame is mostly *repeated* values —
repeated glyphs are ties, and ties are exactly what gets destroyed. **Rank-based readout
is ill-defined precisely where glyph streams live.** I proposed rank-based
re-quantisation as the fix; it fails on every tied case.

**4. Nearest-level readout fails near boundaries.** In the 2×4 case all four cells of the
second row dropped a ramp level despite zero inversions.

## The corrected claim

**What survives:**
- the QPIXL round trip **preserves order** — it does not scramble a field
- it does **not** preserve enough magnitude for nearest-level glyphs
- it **breaks ties**, which is fatal for repeated glyphs

**What I got wrong:** "quantise to a glyph ramp and it round-trips exactly" held for the
one ramp I happened to test and does not hold in general. A single test on a monotone
input is exactly the kind of demonstration that cannot fail.

**What this actually argues for:** not a single-shot glyph codec, but a per-cell
confidence, or a repeated measurement, or a readout that tolerates tie-breaking noise.
The order-preservation result is still a genuine positive — it means the frame's
*topology* survives even where its glyphs do not.

## Limits, stated rather than hedged

- `aer` is a **noiseless simulator**. The load-bearing unknown is whether order
  preservation survives real hardware noise. Untested.
- Fields only up to 2×4 — 4×4 and 1×5 are rejected by the machine's own capacity rules.
- One ramp, one machine, 2048–4096 shots, no repeated trials.

## Files

- `moth_frame_test.py` — the hard-case harness (this document's second half)
- `frame_test.log` — its output, unmodified
