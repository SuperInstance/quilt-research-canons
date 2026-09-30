# The wheel's gaps were mostly the matcher being unable to look

An audit prompted by MicroMoth-quilt exp018, whose verdict was:

> **FITNESS DESERT AT THE BIRTH CLOUD** — the freeze is UPSTREAM of selection:
> selection has nothing to see, not a visibility failure.

That is the shape I had already measured twice from the other direction — `score`
returns a near-constant regardless of subject, and the content matcher reports 33%
unmatched where 100% of cells truly moved. So the question for the wheel was not
"are the gaps real" but **"can the wheel express an answer it is looking for".**

## What the audit found

`STOP` mixed function words with **this corpus's own vocabulary** — `quilt`, `cell`,
`architecture`, `model`, `system`, `design`, `superinstance`. A stop word is generic
*relative to the corpus*; in a fleet whose repos are named `quilt-c`, `quilt-tools`,
`cellforge` and `*-substrate`, those words are not generic. They are how the fleet
**names** things. Filtering them made papers unable to see any artifact that
referenced them by name.

This is the same class of bug as MicroMoth's `search.mutate`, whose indel-insert pool
was hard-wired to 2-wire so that **insert could never touch wire 2**: the search space
was configured so the answer could not be expressed.

## Measured, before and after

```
                        SUPPORTED   GAP   UNKNOWN   papers-with-a-GAP
before                      56       82       13           27 / 28
after (STOP corrected)      68       69       17           23 / 28
```

**GAP cells 82 → 69 (16% fewer). SUPPORTED 56 → 68 (+12).** Four papers became
visible that the matcher had been unable to look at.

## What the fix does NOT do — and this is the important part

23 of 28 papers still carry a GAP. The filename-stem matcher remains structurally
unable to see an artifact filed under a different name, which the `unmapped` field
already says out loud:

> *"cannot tell whether a {label} exists under a different name; needs a human or a
> full-tree read to settle"*

So the honest position: **the GAP polarity is still at ~50% prevalence, and a polarity
at that prevalence carries little information.** It is the constant-generator failure
one level up, in the index rather than in the oracle.

**The real fix is assembly, not vocabulary.** exp018 found that multi-parent archive
mixing reached payoff genomes the champion-local stream never assembled. The wheel's
equivalent is to read the **paper body** for distinctive terms rather than the filename
stem — the body is already fetched (`raw(path)`); it is simply not used for matching.
That is a bounded change and it is the next build, recorded in-source at `keywords()`.

## Method note

The first measurement of this fix reported **zero change** — because bare `python3
wheel.py` takes the `--scan` branch and returns before building cells, so the
comparison was against a stale index written 58 minutes earlier. The number that
mattered was only obtainable by reading the artifact back, which is the same rule
this whole session has been about.
