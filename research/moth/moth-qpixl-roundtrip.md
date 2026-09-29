---
title: MOTH Quantum QPIXL round trip — a third-party check on the glyph-codec claim
date: 2026-09-29
subject: live runs against api.mothquantum.com, engine qpixl-v1
---

## Why this was worth running

`research/qpixl-ascii/` reduces a glyph frame by cancelling identity terms. That
reduction is classical and reproducible, which was the whole point — QuantumArtHack's
useful contribution is the *decomposition*, not the hardware. But a reduction that is
only ever checked against itself has not been checked.

This is the third-party run: the same values, encoded as qubit angles on a real
MOTH Quantum engine, decoded in a single measurement, and compared.

## The runs

Base `https://api.mothquantum.com/api/v1`, engine `qpixl-v1`, `mode: emu`,
`machine: aer`. Full request shape (it took four wrong guesses to find, and the
error messages are good enough to record):

```json
{"mode": "emu",
 "params": {"values": "[0.0,0.143,0.286,0.429,0.571,0.714,0.857,1.0]",
            "machine": "aer", "shots": 2048}}
```

**`values` is a STRING, and it must be wrapped in `[..]`.** A bare comma list fails
with `unparseable_values` and the message tells you so. A JSON array body fails with
`expected object` — the body is `{params, mode}`, not the array.

| job | input | result |
|---|---|---|
| `c65fbb02-f985-4877-ad61-fead4eaf72d2` | `[0.0, 0.143, …, 1.0]` (8 values) | **completed** |
| `a7c346c6-0555-46e9-be41-5f17325c6fe6` | `[[0.1,0.4],[0.7,1.0]]` (2×2) | **completed** |
| `dba3bb7c-ec61-4530-b790-5cbcb4c24fb7` | 4×4 grid | failed: `group_count_mismatch` |

The 4×4 failure is worth keeping: *"4 groups given but the machine has 5 groups; call
`list_groups(values, machine)`."* The qubit **grouping is a property of the machine,
not of your array's shape**, and you cannot infer it from the dimensions you sent.

## The result

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

- input strictly increasing: **True**
- output strictly increasing: **True**
- max |output − input|: **0.0467**
- values returned exactly: **2 / 8**

## The finding

**The quantum round trip is MONOTONE but not value-preserving.** No ordering is ever
inverted; the intensities are moved around by up to 0.047.

Now quantise both to an 8-level glyph ramp:

```
in : [0, 1, 2, 3, 4, 5, 6, 7]
out: [0, 1, 2, 3, 4, 5, 6, 7]     identical
```

**They are identical.** A glyph is a RANK, not a measurement. A monotone map
round-trips a glyph ramp exactly while mangling the underlying intensities. The
distortion that would destroy a pixel codec is invisible to a glyph codec.

This is the strongest available support for the Lane U claim, and it is a *third-party*
measurement rather than a self-consistency check. The 2×2 control shows the same
monotonicity per axis in two dimensions.

### What this does NOT establish

- One ramp is not a distribution. Monotonicity could hold on a monotone input and
  fail on a field where neighbouring values cross. **The test that matters next is a
  full glyph frame, not a ramp.**
- `aer` is a noiseless simulator. The interesting question is what real hardware
  does to monotonicity, and `mode: qpu` requires an explicit `backend_name`.
- 2/8 values returned exactly, so this is emphatically not "QPIXL is lossless."
