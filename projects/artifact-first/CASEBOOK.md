# CASEBOOK — the real failures, and which gate catches each

Every entry is a real instance from one session. None is hypothetical. "Caught by" is
accurate: it means this gate *did* catch it, or that nothing mechanical did.

---

## 1. Conclusion written before the run

**What happened.** A lattice-expansion experiment was given a printed conclusion before it
was executed: structured tori "also expand fine", structure costs nothing in expansion.

**What the data said.** The opposite, on both sides.

```
TORUS  C_a x C_b   kappa = 0.000 exactly   cond 1.000 -> 0.612  DECAYS
GRID   a x b       kappa = 0.000 exactly   cond 0.500 -> 0.319  DECAYS
RANDOM 3-regular   kappa < 0              cond 0.500 -> 0.603  FLAT
RANDOM 4-regular   kappa < 0              cond 0.800 -> 1.000  FLAT/GROWS
```

Non-negatively curved families lose their expansion as they grow; negatively curved random
ones keep it. That is Salez's theorem confirmed on both sides — the opposite of the
prediction.

**Caught by.** Nothing mechanical. Corrected by reading the data against the prose.

**Lesson.** The experiment was worth *more* for the wrong prediction being written down.
That is pre-registration, used by accident.

---

## 2. A test on the easiest possible input

**What happened.** A quantum encode/decode round trip was measured on a **monotone ramp**
and reported as "quantised to an 8-level glyph ramp, it round-trips exactly."

**What the data said.** A 2-D field with crossing neighbours and ties:

```
order inversions : 0     (order IS preserved)
nearest-level glyphs identical : NO, in 2 of 4 fields
ties broken : [0,0.5,1.0,1.0,0.5,0.0] -> [0,0.504,1,1,0.524,0]
```

A monotone ramp is the *easiest* case for an order-preserving map. The test could not
fail. The generalisation was false.

**Caught by.** Running the case the claim was about. The later live probe then showed the
engine is **stochastic at fixed shots** — three identical calls returned boundary cells
spread 0.4900–0.5216 — which means even the surviving "order is preserved" result is one
draw from a noisy process.

**Lesson.** A demonstration is not a test. And a result from a process later found to be
noisy needs re-measuring, not defending.

---

## 3. Right formula, wrong unit

**What happened.** The exact conductance of the flat torus was quoted as `4/196 = 0.0204`
and the measurement called "30× loose."

**What the data said.** The formula is `h(C_a × C_b) = 4/max(a,b)`. The denominator is the
**side length**. At a=14 the truth is `4/14 = 0.2857` and the measurement was **2.1×** loose.

**Caught by.** An independent instrument that measured against the closed form and found
`ratio = 1.000000000000` at every size from a=6 to a=16.

**Lesson.** Same number, wrong quantity. A confident error with a real formula behind it
is the hardest kind to see, because the shape is right.

---

## 4. The headline its own body refutes

**What happened.** A scouting report's lead read:

> **NO. None of the three implements or plans a per-cell mode menu.**

Two clauses later:

> That is genuinely a transmitted per-cell mode, and it is the only one in any of the
> three repos.

**Caught by.** `casper-critic`, reading the report against itself — and then by
`consistency.py` check **C1**, which rediscovers it in the shipped file. That
rediscovery is an assertion in `tests/test_gates.py`.

**Why this is the case that forced gate 2.** The receipt for that headline predates the
headline. **Gate 1 passes it.** Timestamps catch order; this failure is not about order.

---

## 5. An invented statistic in a checked-numbers report

**What happened.** An audit of another agent's "val AUC 1.0 (64/64)" concluded EVAL-BUG —
correctly — and in the process reported a headline statistic its own evidence did not
support, per its reviewer.

**Caught by.** `casper-critic`, on internal consistency.

**Independently confirmed anyway.** The core finding was re-derived from ground truth
without reference to the audit: the manifest records a SHA-256 per clip, and counting
gave 32/32 val real clips byte-identical to train, 41/64 overall, zero unseen. Thirty
seconds, and strictly more than the audit produced.

**Lesson.** Verify the *data* claim in one query; re-derive the *code* claim from source.
A subagent's negative finding about code is worth re-deriving. Its claim about recorded
data is worth confirming in a single query — because the data is already hashed.

---

## 6. The linter's own blind spot

**What happened.** `consistency.py` wrapped each check in a bare `try/except` and appended
exceptions to the findings list. A `NameError` inside check C4 was therefore
**indistinguishable from a clean result**, and the linter reported clean through an entire
session with a dead check inside it.

**Caught by.** The C4 test failing and refusing to be explained away.

**Fix.** Checks now raise `LinterCrashed`. A crash is louder than a pass.

**Lesson.** The safety net you write to keep a tool running can be the thing that hides the
tool is broken.
