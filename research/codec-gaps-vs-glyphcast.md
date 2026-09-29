---
title: Codec techniques as quilts — a gap map against glyphcast's roadmap
date: 2026-09-29
subject: what a video codec has that a cell graph does not
---

## First: the fleet already has the answer to most of the question

`SuperInstance/glyphcast` — *"Next-frame prediction and frame-rate synthesis for
glyph-domain video streams (chiaroscuro ASCII as token-array video)"* — is a five-phase
receipt-gated roadmap for exactly this. It already specifies:

- coarse-to-fine heads (12×9 semantics → 48×36 glyph field → optional 96×72 detail)
- cross-entropy per cell from day one, no regression heads
- scheduled sampling from the start (Bengio 2015) to avoid exposure bias
- three baseline arms — persistence, per-cell flow extrapolation, tiny transformer
- **RIFE-style interpolation**: per-cell flow, in-betweens by flow-guided palette
  sampling, imagination reserved for occlusion edges
- a `score` harness so improvements are receipts, not vibes
- a clear claim to test: *at 178× fewer samples per frame than the pixel stream, the
  glyph interpolator's effective temporal resolution overtakes what the pixel side can
  transport on the same wire*

**So the scouting question is not "what can we borrow from video" — it is "what do codecs
have that glyphcast's roadmap does not mention."** That is a much shorter list than it
looks like, and it is concentrated in one idea.

---

## The gap map

| codec technique | what it is | glyphcast has it? | what it would buy |
|---|---|---|---|
| **per-block MODE SELECTION** | every block picks from {skip, direct, forward, bi, left, right, above…} and **the mode itself is coded** | **NO** — the heads are a *pyramid*, not a *menu* | the 6D question, answered |
| **motion vectors** | a displacement field, not a match | partially, as "per-cell flow" in Phase 3 | the L1 aperture fix |
| **AMVP (MV prediction)** | MVs predicted from neighbours, not sent raw | **NO** | delta-of-delta; the single biggest modern win |
| **rate–distortion optimisation** | every decision is *bits spent vs distortion lost* | cross-entropy per cell is the same idea, but there is no explicit **per-cell** cost | a cell that can say "I am not worth describing" |
| **closed GOP / reordering** | display order ≠ coding order | **NO** | rewind as a property of the stream, not of the viewer |
| **loop filters (deblocking, SAO)** | the reconstruction is deliberately NOT the source | **NO** | a filter state per cell |
| **quantisation parameter, adaptive** | QP varies per block by content complexity | **NO** — the ramp is fixed | this IS the "learned font": choose the alphabet per camera |

### The one that matters

Everything above is a variation on a single idea:

> **A cell's ENCODING is a per-cell decision with its own cost, and the decision itself is
> transmitted.**

glyphcast's coarse-to-fine heads are a **pyramid**: they say how much resolution to spend.
A codec's mode selection is a **menu**: it says which of several ways to describe this
cell, and it *pays for the choice*. A pyramid has three rungs. A menu has a mode per cell,
including a mode that means **skip**, which is nearly free.

That is the 6D question, and a video codec answers it in a few bits of header that nobody
has written down for cells.

---

## The measured part: where content-match delta fails

The `qpixl_ascii` reduction beats a positional delta by a factor of ~40 on ordinary motion
(2.2% vs 85% of cells changed under a small pan). `delta_limit.py` then found the
boundaries, and one of them fails in the dangerous direction:

**L1 APERTURE — a repeating texture.**

```
positional   100.0%  unmatched
content       33.2%  unmatched   <- the trap: looks free
ground truth 100.0%  of cells ACTUALLY moved
```

Every cell in a periodic texture has many perfect matches. The matcher returns *a* match,
it is not *the* match, and the cost comes back 67 points too low. **The cheap answer here is
wrong and it looks right.** That is the worst failure mode available: not a wrong number you
can check, but a right-looking number that is wrong.

A codec does not have this failure because it does not search for matches. It transmits a
**motion vector** — a displacement — which on a repeating texture is the true one-cell shift
and costs the same as any other. The search is what creates the ambiguity; the vector does
not.

**L3 OCCLUSION** — content that leaves the frame has no match at all and is charged as
though it had a bad one. A codec codes those blocks as **SKIP**, which is nearly free. This
has no mode where "absent" is cheaper than "present and wrong."

**TWO LIMITS ARE NOT YET MEASURED**, and are marked as such rather than faked:

- **L2 RADIAL SPEED.** The obvious test (identical frames at increasing radius) is
  degenerate — identical frames match at radius 0, so every radius returns 0.0% and the test
  cannot fail. Exercising it needs a displacement that exceeds the radius with no in-frame
  substitute, which a periodic scene always has.
- **L4 ALIASING.** A glyph *is* a quantisation, so intensity carries no information below
  the ramp step while colour does. The two keys compared are both total on single
  characters and cannot disagree. A real test needs a renderer whose colour channel varies
  independently of its glyph channel — a colour-ramped grid. That is a **chiaroscuro engine
  question**, not a matcher question, and it is the concrete thing to build next.

---

## What a bitmap is, restated as a quilt

A bitmap is usually described as a grid of pixels. That undersells it. It is a matrix of
**encodings in a collective system**: each sample's meaning comes from the palette, its
position, and the values around it. Change the palette and every sample changes meaning
without changing a bit. That is a quilt already — a cell whose value is a function of its
frame.

So the four things a glyph stream carries that a pixel stream surrendered, per glyphcast's
own canon, are not aesthetic preferences:

- **shape** — a glyph is a contour, not a sample
- **time** — the same cell across frames is the same object, addressably
- **trainability** — the target is categorical, so cross-entropy bites
- **space** — the lattice is the address space, not a convenience over it

## The compression question

Compression is not a separate thing from a quilt. A good compressor finds the structure
that already exists and refuses to spend bits on what is already implied. That is exactly
what the `qpixl_ascii` reduction does: it cancels constant rows, uniform intensity, absent
colour channels and unchanged cells, and reports **what is left**. A codec does the same
thing with modes instead of cancellation, and it is better at it for the reasons above.

**The interesting limit neither has solved**: both cancel structure, and both pay full price
for anything that is genuinely new. Neither can tell "this cell is new and important" from
"this cell is new and boring" without something to compare against. That something is a
model — which is the whole argument for putting the learned part in the *mode choice*
rather than the *renderer*.

## The order that would actually build this

1. **The colour-ramped glyph lattice** (unblocks L4, and is a `chiaroscuro` engine change)
2. **A mode menu, not a pyramid** — per cell, one of {literal, delta, skip, coarse} — with the
   mode itself transmitted. This is the 6D question in one structure.
3. **Motion vectors alongside matches** — cheap to add, removes the L1 trap
4. **Predict the mode from the neighbours** (AMVP) — the mode is small, so its prediction is
   cheap, and this is where the modern wins came from
5. Only then: the learned font, because by then there is a place to put what it learns

Steps 2–4 are a few hundred lines and a receipt. That is the gap between the roadmap and
a working encoder, and it is narrower than it looks.
