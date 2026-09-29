# Is a Witness Log a Persistent-Homology Barcode?

**Verdict: (c) NUMEROLOGY.** Not a theorem. Not even a useful heuristic with a name.
The bridge from "cells and time" to "points and scale" **fails**, and it fails in a way I can
demonstrate on the fleet's own real logs rather than by argument.

Date: 2026-09-29 · Author: herman-historian · Task: `witness-barcode`

---

## TL;DR

The CEH2007 theorem is real, correctly stated, and does **not** transfer. Two independent
failures, either of which is fatal:

1. **Category failure.** CEH07 is a theorem about *functions on a triangulable space*.
   A witness log is a *persistence module* — a functor, an abstract diagram. There is no
   space `X`, no function `f`, and no metric on logs. The bound is on `‖f − g‖∞`, a
   distance between **functions**. There is no distance between logs to put on the right.
2. **Empirical failure.** The real SuperInstance canon log has **no death events at all**.
   Every interval is essential `[t_birth, ∞)`. The persistence diagram is 2336 points at
   infinity — the diagonal, collapsed. `d_B` on such a log is provably a no-op that
   returns the timestamp perturbation and nothing else.

The hypothesis also fails the "prediction" test it was recruited for: the log contains
**no prediction field**, and its own `q02_witness_log_is_prediction` score is a constant
`0.936 ± 0.005` with zero drift over 80 rounds. It does not predict. It re-asserts.

---

## 1. The mapping, stated honestly

### What a barcode actually requires

Persistent homology needs four things. I will name all four and then say which the
witness log supplies.

| Ingredient | Needed for | Supplied by a witness log? |
|---|---|---|
| A point cloud `P ⊂ M` | the geometry | **NO** — see below |
| A **metric** on `M` | defines scale, defines the parameter | **NO** |
| A **filtration parameter** `t` (the "scale") | births/deaths live *on the t-axis* | **NO** — only *clock* time |
| Deaths | gives finite intervals | **NO** — no death field exists |

### 1a. The point cloud — this is the first hard stop

CEH07's application to data (§4, "Homology from point samples") is explicit. Given a
closed subset `X` of a metric space `M`, let `d_X : M → R` be the **distance function**,
mapping each point `p ∈ M` to its distance from `X`. The filtration is the **sublevel set
filtration of the distance function**, and the *parameter* is *distance in the ambient
metric space*. Persistence measures holes in a shape.

**A witness log has no shape.** There is no ambient metric space, no distance, no
sublevel sets, and therefore no holes. Two candidate bridges and why both fail:

**Bridge 1 — "the log is a point cloud in ℝ."**
Put each cell at `(t_i, y_i)`. But `y` has no meaning. If I set `y = 0` for all cells, the
cloud is 2336 collinear points, every neighborhood is contractible, and H₀ = 2336 with
**zero** H₁ and zero H₂. The barcode is 2336 trivial intervals. If I invent a `y` — a
score, a token count, a hash — I have manufactured the geometry, and the resulting
persistence measures *my invented axis*, not the log. Any H₁ that appears would be an
artifact of the invention. **This is the sound bridge and it yields nothing.**

**Bridge 2 — "the log is a filtration over clock time."**
Clock time is a *total order*, not a *scale*. Persistent homology needs the parameter to
be a filtration value where "small" has geometric content. Using `t = clock` is legal in
the purely algebraic sense (it yields a persistence module) but then the barcode is not a
*topological* invariant of anything — it is a restatement of "the events, sorted." See §4.

### 1b. The parameter — the conflation that makes the analogy seductive

The proposal says intervals `[birth, death)` have "exactly the shape of a thing that
existed from t_birth to t_death." Shape-wise, yes — that is why the analogy is tempting.
But in persistent homology, `birth` and `death` are values of a **scale parameter**, and
their *difference is the persistence*, which is the quantity the whole theory is built to
measure and to bound. In a witness log, `birth − death` would be a **duration in seconds**.
Bottleneck distance is measured with the `L∞` norm on `(birth, death)` pairs, so
`d_B` would be in units of seconds. **The proposed theorem would read: "witness logs
survive measurement noise, up to a few seconds."** That is not a claim about the
substrate's predictive content. It is a claim about clock jitter, and it is trivially
true of any timestamped event stream, including `ls -l`.

### 1c. Where the doctrine actually lives — and why the barcode can't see it

The Quilt doctrine's real content is that the canon is a **hash-linked chain**: each cell
commits to a `latest_ref`, making the log a *signed, ordered, tamper-evident* sequence.
A barcode is a **set of intervals**. Therefore:

> The chain — the one structural feature that makes a witness log a *canon* rather than
> a pile of timestamps — is **provably orthogonal to the barcode**. It cannot be detected
> by `d_B` at any `ε`.

This is not a gap in my analysis; it is a proof. Shuffling the log's order leaves the
multiset of birth times, hence the barcode, **exactly unchanged** (verified, §4 Test A).
A barcode cannot distinguish a signed chain from the same events randomly permuted.

---

## 2. The theorem — verified against the primary source, not memory

I downloaded the actual paper and extracted the text. Verbatim:

> **MAIN THEOREM.** Let `X` be a triangulable space with continuous **tame** functions
> `f, g : X → R`. Then the persistence diagrams satisfy `d_B(D(f), D(g)) ≤ ‖f − g‖∞`.

**Full citation:** David Cohen-Steiner, Herbert Edelsbrunner, John Harer. *Stability of
Persistence Diagrams.* **Discrete & Computational Geometry 37(1):103–120, 2007.**
DOI 10.1007/s00454-006-1276-5.
PDF verified: `math.uchicago.edu/.../Edelsbrunner,%20Harer,%20Stability.pdf` (9 pp.,
extracted 48,654 chars). Confirmed by the paper's own reference list in Edelsbrunner &
Morozov, *Persistent Homology — Theory and Practice*, which cites it as *Discrete Comput.
Geom. 37 (2007), 103–120*.

**Tame (verbatim from the paper's DEFINITION):**
> A function `f : X → R` is tame if it has a **finite number of homological critical
> values** and the homology groups `H_k(f⁻¹(−∞, a])` are finite-dimensional for all
> `k ∈ Z` and `a ∈ R`.

**Hypotheses the task statement omitted** (all from the paper, all required):
- `X` is a **triangulable** space (homeomorphic to a finite simplicial complex);
- `f, g` are **continuous** and **tame**;
- the diagrams are of **sublevel-set filtrations of functions**, not of arbitrary modules.

### Does stability transfer? **No. Here is the precise obstruction.**

The bound's right-hand side is `‖f − g‖∞` — a distance **between two functions on a
space**. To apply it to a witness log I would need a metric `d(log₁, log₂)` with
`d_B(barcode(log₁), barcode(log₂)) ≤ d(log₁, log₂)`. There is no canonical such `d`,
because a log is not a function and has no ambient geometry. Any `d` I invent is
manufactured, and the resulting inequality is a tautology about my invention, not a
theorem about the substrate. **The right-hand side of the proposed theorem does not
exist.** This is the whole argument, and it is a category error, not a technicality.

There *is* a module-level stability theory, and I checked it rather than assuming:

> **Isometry Theorem** (Lesnick, *The Theory of the Interleaving Distance on
> Multidimensional Persistence Modules*, arXiv:1108.4815, Thm 3.4): For `ε ≥ 0`, p.f.d.
> 1-modules `M, N` are `ε`-interleaved **iff** there exists an `ε`-matching between
> `B_M` and `B_N`; in particular `d_I(M, N) = d_B(M, N)`.

This is the **algebraic stability** theorem, and it is *different in kind* from CEH07. It
says: barcode distance **equals** interleaving distance. It gives no `ε`-bound from any
noise model, because it takes no noisy data as input — it compares two already-built
modules. To use it you must already have two modules and a way to interleave them. It
cannot manufacture a "witness logs survive noise" theorem, because it says nothing about
where a module comes from. **CEH07 links barcode distance to data noise; the isometry
theorem does not.** The hypothesis needed the former and got only the latter.

The transfer therefore requires: (i) a space `X`, (ii) a tame function `f` on it, (iii)
`g` within `ε` of `f`. A witness log supplies **none** of the three.

---

## 3. The real witness log — what I found and what I computed

### Source A — the live canon ledger (primary)

`GET https://api.superinstance.dev/api/cells?limit=10000` → **2,336 real cells**,
2026-09-22 04:45:13 → 2026-09-29 21:25:53 (span **7.695 days**). Public, no auth.

Exact schema — **every field, exhaustively**:
```
id, type, timestamp, created_at, source
```
- `type`: `canon` (2,335), `visitor-contribution` (1)
- `source`: `cron` (2,217), `taps-creative-break` (84), `api` (20),
  `no-deletion-archive` (4), `taps-creative-break-fallback` (3), and 8 singletons

### THE KILL: there is no death field. Ever.

```python
records with a death/expiry/end/status field:  0   # of 2336
```

So every cell yields an **essential** interval `[t_birth, ∞)`.

- **n essential intervals = 2,336 of 2,336.**
- `rank(t)` = number of cells born at or before `t`. A strictly increasing staircase
  1…2336. Monotone by construction.
- The persistence diagram is **2,336 points at infinity** — the diagonal, collapsed. There
  are no finite features, no H₁, nothing for a barcode to say.

**And `d_B` is provably a no-op here.** Compare the log to a copy of itself with every
timestamp shifted by `Δ`:

| shift `Δ` | measured `d_B` |
|---|---|
| 100 ms | 0.100 s |
| 1 s | 1.000 s |
| 60 s | 60.000 s |

`d_B = Δ`, always. Every point moves by exactly the shift and nothing else. The metric
cannot detect content, order, source, chain, or canon-ness. Any "stability" it reports is
**trivially true and carries zero information.** This is the direct empirical
counterexample to the stability claim.

### Source B — `jev-quilt/continuous/example_run/history.jsonl` (80 rounds, 27,464 bytes)

Fetched via the raw tree API (`git/trees/main?recursive=1`, 810 blobs, untruncated). This
log's structure is `{round, ts, sampled_qids, verdicts{qid: float}}` — **5 verdicts
sampled per round from a pool of 22 qids, 80 rounds.**

Timestamps: 19 distinct values over an **18-second** span (16:44:27→16:44:45), strictly
monotonic, in clean groups of 4–5 rounds. Honest note: 18 seconds of wall clock is a
**thin** time axis for a persistence argument; I flag this rather than dress it up.

**The only interval structure present** is first-sample to last-sample per qid. 22
intervals, all spanning most of the run:

```
persist durations: min=65  max=80  mean=74.18  median=74.5   (out of 80 rounds)
5 of 22 intervals are still open at round 80
```

**Null-model test (does this structure mean anything?).** If 5 of 22 qids are sampled per
round uniformly at random, what "lifetimes" do you get? 20,000 trials:

```
OBSERVED  persistence: mean=74.18  sd=3.66  min=65  max=80
NULL      persistence: mean=73.20  sd=5.48  min=25  max=80
z = +0.179  -> INDISTINGUISHABLE
obs intervals inside null 1st-99th percentile [55,80]:  22/22
```

> **The "lifetimes" are a sampling artifact.** A 22-question quiz that samples 5 questions
> per round will make *every* question look long-lived, because each one keeps getting
> re-drawn. The observed spread is entirely explained by the null. Reading persistence
> here would be reading the sampling rate, wearing a topology costume.

### Task 3c — can a logged expectation be scored against a later observation?

**No.** Searched every key in every record for `pred|expect|forecast|anticip|project`:
**zero hits.** The log contains no prediction field. A prediction requires a value recorded
*before* the outcome; this log records only verdicts, each computed from the round it
belongs to.

The near-match is `q02_witness_log_is_prediction` — but that is a **question ID scored by
an LLM judge**, i.e. an opinion *about* the doctrine, not a prediction *by* the substrate
that a later record could falsify. 13 observations across rounds 1–80:

```
[0.93, 0.94, 0.94, 0.94, 0.94, 0.93, 0.93, 0.94, 0.94, 0.93, 0.94, 0.94, 0.93]
mean=0.936  sd=0.005  min=0.93  max=0.94
Pearson r(round, score) = -0.053   (n=13)
```

**The log does not predict. It re-asserts**, at a fixed 0.936, with no drift across 80
rounds. A signal that is constant is a signal that is not measuring the thing it names.
Note also: 0.005 sd on an LLM judge scoring the *same question* is within the noise floor
of the judge, not evidence of substrate-level constancy.

---

## 4. Four tests, all failed

| # | Test | Result |
|---|---|---|
| A | Shuffle log order, keep birth-time multiset | Barcode **identical** (`True`). Barcode is order-invariant by construction. |
| B | Replace every `source` label with `x` | Barcode **unchanged** — `source` is not a field of an interval. |
| C | Same birth times, different chain links | Barcode **identical**. The canon chain is invisible to `d_B`. |
| D | Is "rewind = restrict to `t ≤ τ`" true? | **Circular** — see below. |

**On Test D (rewind), carefully.** Restricting a barcode to `t ≤ τ` does give intervals
`[b, min(d, τ))`. But a restricted log is *not* the same as a re-observed log. At `t = τ`
you genuinely do not know which cells would have died after `τ`; restriction **truncates
deaths to τ, manufacturing deaths that never happened.** The identity holds only if the
deaths are *already known* at rewind time — i.e. only if the log is a **completed** log,
not a live one. The identity is circular: it requires the future to already be in the log.
For the live canon ledger, where nothing ever dies, "rewind" produces `2,336` intervals
that all become fake deaths at `τ` at once.

---

## 5. Verdict

### (c) NUMEROLOGY.

I pick (c) and defend it, because the alternative readings fail on evidence I can point at
rather than on taste:

- **Not a theorem.** CEH07 is a theorem about tame functions on a triangulable space. The
  right-hand side `‖f − g‖∞` has no meaning for a log. The proposed bound cannot be
  written down, let alone proved. The module-level stability theory (isometry theorem)
  does not fill the gap — it takes no noisy data as input.
- **Not a useful heuristic.** A heuristic must carry information. On the real 2,336-cell
  ledger, `d_B` returns the timestamp shift and nothing else (§3). On the 80-round probe
  log, the apparent "lifetimes" are indistinguishable from a random-sampling null at
  `z = +0.18` (§3). In both cases the metric is *measuring the sampling, not the substrate*.
- **It is numerology** — a real mathematical structure (intervals, births, deaths,
  stability) laid over data that does not contain the quantities those structures consume.

### The two honest things the analogy got right

I will not pretend it is worthless, because two pieces are genuinely right and worth
keeping as *engineering* practice, deliberately uncoupled from the topology claim:

1. **A witness log *is* a persistence module.** Formally true: a partially ordered set
   (time) with linear maps. That is a legitimate algebraic object, and its barcode is
   well-defined. It is just a **relabeling**, not a discovery — and the isometry theorem
   applies to it in a way that is true but *vacuous* for prediction.
2. **Stability framing is a good instinct.** "Our log should degrade gracefully under
   measurement noise" is a sound engineering goal for any record system. It just needs
   `d_B` defined on logs to be *useful*, and by §3 that is the part that fails.

### What would be needed to revive this as a theorem

Stated so the next thread does not re-grind it:

- a genuine **ambient metric** on the cell space (not clock time) — this is the missing
  concept, and I do not believe one exists in the substrate today;
- a **death event** in the schema, so intervals are finite and the diagram has off-diagonal
  mass to measure;
- a **tame function** on a triangulable `X` whose sublevel filtration the log actually is;
- a **prediction field** — a value recorded before its outcome — so there is something to
  score.

Absent all four, the thread is closed. Recording it as closed, with the receipts, is the
historian's job.

---

## Provenance — every artifact, re-checkable

| Artifact | How obtained |
|---|---|
| CEH2007 primary PDF | `math.uchicago.edu/~shmuel/AAT-readings/Data Analysis/Edelsbrunner, Harer, Stability.pdf` (9 pp., 155,035 bytes); text extracted, MAIN THEOREM + tame DEFINITION quoted verbatim |
| Isometry theorem | Lesnick, arXiv:1108.4815, Thm 3.4 (via ar5iv full text) |
| Canon tree | `GET api.github.com/repos/SuperInstance/quilt-research-canons/git/trees/main?recursive=1` — 106 blobs, `truncated: false` |
| JEV tree | `GET api.github.com/repos/SuperInstance/jev-quilt/git/trees/main?recursive=1` — 810 blobs, `truncated: false` |
| Real witness log | `GET api.superinstance.dev/api/cells?limit=10000` — 2,336 records, 282,055 bytes |
| Probe log | `raw.githubusercontent.com/SuperInstance/jev-quilt/main/continuous/example_run/history.jsonl` — 27,464 bytes, 80 rounds |
| Null model | 20,000-trial uniform-5-of-22 sampling simulation, seed 0 (full script alongside this report) |

**Local copies:** `/tmp/scout_out/` — `ceh07.pdf`, `ceh07.txt`, `cells.json`,
`jev_continuous_example_run_history.jsonl`, `canons_active_ledger.md`,
`jev_essays_witness_log_prediction.md`, plus the two analysis scripts.

**Also read, for the doctrine's own words** (not used as evidence, cited as the claim
under test): `jev-quilt/essays/witness_log_prediction.md` — a four-voice essay whose
central image is sedimentary strata constraining future layers. That image is about
*causal constraint*, which is a real and interesting idea. It is not about persistence,
and it does not need the barcode to stand up. Stripping the numerology does not damage
the doctrine; it removes a false support it was leaning on.
