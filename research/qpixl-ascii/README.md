# qpixl_ascii — QPIXL's trick, applied to character grids

## What QuantumArtHack actually is, and why it matters here

It is a fork of HeidelbergQuantum/ParallelQPIXL, made for the Unitary Hack. QPIXL encodes an
image into qubits, and its actual contribution is **not the encoding** — it is the
**decomposition**: split the encoding into gates, delete every zero angle, and cancel every
CNOT pair that the optimal decomposition turned into the identity. The circuit that
survives is the information, and it is smaller than the encoding you started with.

**That reduction is classical arithmetic. It does not need a quantum computer.**

chiaroscuro is a real-time webcam-to-text renderer where characters are shapes, not pixels.
So a character grid is an encoding, and the same question applies: how much of this grid's
description is actually information?

MOTH already ships the same algorithm as a live engine — `qpixl-v1`, "an array encoded as
qubit angles, decoded in a single measurement." This is that idea run locally, on glyphs.

## The reduction

Decompose a cell description into four channels, then cancel the identity terms in each:

| channel | cancelled when |
|---|---|
| glyph | the row's glyph is constant — describe it once, not per cell |
| intensity | uniform across the frame, or a dominant level with noise |
| colour | a channel is constant, or a channel is absent (cheaper than zero) |
| delta | the cell has no content-match in the previous frame within a 2-cell radius |

What survives is the residual, and **the residual's size is the real description length.**

## The three claims, measured

```
THE 4D CLAIM — a moving camera changes a small subset of cells
  t=0.25  pan=0.8   changed cells:  19/864  (2.2%)
  t=0.5   pan=1.6   changed cells: 159/864  (18.4%)
  t=0.75  pan=2.4   changed cells: 389/864  (45.0%)

THE 5D CLAIM — storyboard vs high-frame-rate, same grid
  storyboard    3 frames :  69,411 bits    23,137 bits/frame
  high-frame   25 frames : 656,214 bits    26,249 bits/frame

THE 6D CLAIM — the per-cell budget is a function, not a width
  a still camera              26,640 bits   30.83 bits/cell
  a camera in the world       13,868 bits   16.05 bits/cell
  fixed 8-bit everywhere       6,912 bits   (same in both cases)
  fixed 4-bit everywhere       3,456 bits   (same in both cases)
```

## The control that makes the sparsity believable

A content matcher that matched indiscriminately would report the same sparsity on a
random frame. It does not:

```
a real pan matches      845/864  (2.2% changed)
a RANDOM frame matches   59/864  (6.8%)
```

And the delta is not an artefact of ignoring movement:

```
no pan, just the scene pulsing :  10/864 changed
pan 0.8                        :  19/864 changed
```

Motion dominates, which is the claim.

## Why this is the 6D answer without being the 6D answer

Fixed-width encoding (FP8, FP4, ternary) spends the same bits on every cell forever,
because it cannot know a cell is boring. This spends per cell what the cell actually costs,
and the cost is a **function** of the application, the camera and the motion. A static
installation in a dark room and a moving camera in daylight use the same renderer, the
same grid, and the same code — and get different budgets per cell, computed rather than
declared.

**A learned font is the same idea one level up: choosing the alphabet, not the width.**
`micrograd-quilt` is a tiny scalar autograd — that is where the per-camera font would be
trained, and where the per-cell budget function would be fitted. The renderer's job and
the model's job separate cleanly: the renderer emits a residual, the model chooses the
encoding the residual is written in.

## Three bugs the demo found that the tests did not

The self-test was 10/10 while the demo was **wrong in its own favour** — it claimed
sparsity and showed 85% change, and it claimed a reduction and produced four times *worse*
than fixed FP4.

1. **The delta was positional.** It compared each cell to the same grid index in the
   previous frame. Under camera motion that is almost never the same cell, so 85% came
   back "changed." A motion delta must ask which cell in the previous frame *this* cell
   is — a near neighbour, not the same index. That single change took 85% to 2.2%.
2. **The cost model double-billed.** A cell in the delta set is described *by* its
   delta, so counting both a full intensity and a full colour for it was charging twice.
3. **The demo injected per-cell noise**, so no dominant intensity level existed and every
   cell kept a full byte. A glyph *is* a quantisation; a renderer emitting continuous
   intensity is not rendering characters.

**A test suite at 10/10 does not mean the thing is right. It means the assertions are
satisfied.** The demo was the instrument that found the disagreement, and the disagreement
was the product.

## And a leg that failed for the wrong reason

The control leg ("a random frame matches almost nothing") initially failed at 11/24 against
a >12 threshold. The matcher was not lenient; a 24-cell sample cannot carry that claim.
The honest fix was a larger sample with a 75% bar, not a smaller bar the noise could
clear.

## Self-test: 11/11

Fault injections on the reducer itself:

| injected | legs failing |
|---|---|
| cost model loses the delta relief | 2 |
| matcher matches anything | 3 |

## Running it

```sh
python3 self_test.py
python3 demo.py
```

No dependencies. The quantum version is one API call away and is not required for any
claim made here — the decomposition is classical.

## Where this plugs into the fleet

- **chiaroscuro** — emits the frame. This reduces it.
- **micrograd-quilt** — would fit the per-cell budget function and learn the alphabet.
- **MOTH `qpixl-v1`** — the same decomposition, on qubits, for a third-party check.
- **MicroMoth-quilt** — where the resulting receipts go, so the reduction is measured
  over time rather than demonstrated once.
- **exoj / dthe** — external non-collapsing scratch paper and the tensor-of-planes
  model. A residual *is* a sparse edge set, which is what a plane intersection holds.
