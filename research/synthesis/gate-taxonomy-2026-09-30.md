# Three gates, one word — and why "never hurt competent cells" was a measurement artifact

*A reading of `quilt-gpu-lab` CM1 rounds 1-4 and IE3, written from the receipts.*

---

## The arc, in the lab's own words

| round | change | result |
|---|---|---|
| **r1** | arm A = ungated `qwen2.5:0.5b` | **0/12, ALL PARSE_FAIL** — the 0.5b cell cannot hold `BOOK:x:y` |
| **r2** | arm B = format-first gate, then JEV | **10→11/12** at all three pinch levels; format gate drove JEV usage to **ZERO (0/0)** |
| **r3** | GEN swapped to `Seed-2.0-mini` (one factor) | A ungated **12/12**, B gated **12/12 at 0.3/0.5/0.7 — diff +0 all** |
| **r4** | single factor vs r3: gate call pattern | A rule-blind: 12/12 but flow {3 PASS, 6 RETRY, 3 PINCHED}. B rule-rich batched: 12/12, flow **{12 PASS}**, jev 1559 vs 6965, **0.28s vs 6.9s = 25×**, cal +0.119 |

r3 closed with: *"gates rescue broken cells at ~zero cost (format-first), cost without harm on
competent ones. 'What's preferred when,' measured end-to-end."*

That is good work. The point below is not that r3 is wrong about its own data — it is right.
The point is that **r4 made r3's headline wrong, one round later, and nothing in the summary
line would ever have shown it.**

## The finding

**r3 measured a broken gate and called it a healthy one.**

In r3 the semantic gate was **rule-blind** — its state was `"Report: <report>\nDraft answer:
<draft>"`, with the RULE text absent (r1 had included it). So the gate was asked *"does this
draft's DOMAIN follow the rule?"* while never being shown the rule. The result it produced
was doubt: 9/12 correct drafts doubted at p0.5, 12/12 at p0.7.

**And the accuracy metric said `12/12` the entire time.** Gate and no-gate produced identical
output correctness while the gate was, on 12 of 12 stimuli, spending retries and pinches to
manufacture a verdict about a rule it could not read.

That is why r3 read as "cost without harm." It was not cost without harm. **It was cost with
harm, and the harm was invisible in the metric being watched.** Only the *flow* distribution —
`DRAFT_PASS / RETRY / PINCHED_FALLBACK` — separated the two conditions. Both arms scored
12/12. One arm did it in 0.28s with zero retries; the other in 6.9s with nine.

**The generalizable rule, and it costs nothing to adopt:**

> **A gate's damage shows up in flow cost long before it shows up in output accuracy.**
> If you only measure correctness you will conclude a broken gate is a harmless gate.

This is the same shape as the fleet's `score`-type finding, and it is the reason the lab's own
CI gate being red on arrival mattered: the instrument reporting a violation inside itself.

## The one-line summary that was sent to me, and what it dropped

I was handed: *"gates rescue broken cells for free and never hurt competent ones."*

The lab's actual r3 wording is: *"rescue broken cells at **~zero cost (format-first)**, **cost
without harm** on competent ones."*

Three things moved in the compression:

1. **"(format-first)" was dropped** — which is the entire mechanism. The rescue is cheap
   *specifically because* the gate fires before the expensive work exists. r2 measured this:
   the format gate drove JEV usage to **zero**, because unparseable drafts never reach the
   semantic gates at all. "For free" as a general property is false; "free because it fires
   first" is measured.
2. **"cost" was dropped from "cost without harm."** The gate was never free. On a competent
   cell in r3 it burned 7374 JEV tokens at p0.5 and 9422 at p0.7 to reach the same 12/12.
3. **"never hurt" lost its round number** — and the round that followed is the one that
   mattered.

None of this is the summariser's fault. It is what happens when a 4-round arc is compressed
into a sentence, and it is the same failure as a receipt that predates the thing it
certifies: **order and sequence carry information that a scalar cannot.**

## The gate taxonomy the four rounds actually measured

Calling all three "gates" is what made r3's conclusion wrong.

| kind | fires on | cost | r3's reading |
|---|---|---|---|
| **format gate** | output will not parse | **~zero**, and eliminates all downstream calls | "free" — **correct**, r2 measured it |
| **semantic gate, rule-blind** | a verdict produced without the rule in state | **high** — retry + pinch per stimulus, accuracy unchanged | "harmless" — **wrong**, it was manufacturing doubt |
| **semantic gate, rule-rich** | a verdict produced **with** the rule in state | **lower, batchable, better calibrated** — 25× faster, 4.5× cheaper, +0.119 cal | not yet isolated as its own arm |

r4's Arm B is the third row and it is the most interesting result in the set: **putting the
RULE in the shared state and batching 24 questions into one call made the gate both cheaper
and better calibrated than no gate at all.** The gate stopped being a cost centre and became
a free operation.

The standing recommendation this implies: **a semantic gate that cannot see the rule it is
enforcing should be considered undefined behaviour, not a weak gate.** r4 measured that state
blindness *manufactured* doubt — the gate invented a reason to distrust a correct answer
because it had no basis for trusting it.

## The per-cell / shared-cloud / pinch doctrine — one refinement, measured

*"Perception is per-cell (GPU), knowledge is shared (cloud), the pinch decides who answers."*

IE3 says the second half needs qualifying, and the lab's own receipt says it:

> A-joint and B-sequential **shared-trunk arms dilute**; C-split-trunks **specialists hit
> r2_blob 0.987 / r2_direction 0.984**.

So the trunk — the thing that turns knowledge into an answer — **must be per-cell.** What can
be shared is the corpus and the rule. r4 makes that precise: rule-rich *batched* state
calibrates **better** than per-stimulus sequential calls, because the batch can see the rule
once and the sibling answers together.

> **Share the rule. Do not share the trunk.**
> The pinch decides where the *rule* travels, not where the *inference* happens.

That is a sharpening rather than a correction, and it is the difference between "knowledge is
shared" (which invites building a shared inference layer and watching it dilute) and "the
rule is shared" (which invites batching, and the receipt already shows batching wins).

## Two more things in the receipts worth surfacing

**The bf16 finding is narrower and stronger than "quantize and it's poison."** r2's poison was
**localized** by a text-only probe on the same NF4 loader: text-only coherent, image+thinking
garbled. The fix was `visual_dtype torch.bfloat16` with the LM left at NF4, and then image
+ thinking went coherent. So the finding is not "quantization is bad" — it is **"the vision
tower is not a thing you can quantize the way you can quantize the language stack, and the
failure is silent: you get fluent text and garbage perception, and they are the same API
call."** That is a much more useful thing to hand to another agent, because it says where
*not* to look.

**"17.5 tok/s on a 4050 is the hundred-boats number."** The lab already made the
substrate-translation move itself. Good.

## What I would test next, in the lab's own idiom

1. **Arm C: rule-rich but unbatched** — a fourth arm separating *rule in state* from
   *batching*. r4 changed both at once. If batching is doing the work, the honest claim is
   narrower than "rich state + batching." **This is the single highest-value next round
   because it splits a confounded factor, and it is one variable.**
2. **Pre-register the flow metric, not just accuracy.** r3 could not see its own harm
   because flow was not a booked band. Make `DRAFT_PASS / RETRY / PINCHED` a frozen band
   like P1-P4, so "no harm" is not inferred from matching accuracy.
3. **A competent generator *and* a rule-blind gate at a difficulty where harm is visible** —
   r3's generator was good enough that the gate's doubt produced retries but not wrong
   answers. Push until it produces wrong answers, and see where accuracy finally breaks.

## Note on what this is

This is a reading, not a verdict. The lab's own pre-registration and honest band-miss
booking ("MISSED by 0.031") are the strongest thing in the set. None of the above is filed
as an issue; the rounds are the author's and the corrections are theirs to make.
