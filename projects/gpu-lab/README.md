# gpu-lab — what a GPU workstation can do with the material this session produced

Six experiments, all derived from real findings rather than invented workloads. Every one
has a CPU fallback so it runs without a GPU and reports which path it took — **a benchmark
that silently falls back to CPU and reports the CPU number as a GPU result is the exact
failure this lab exists to avoid.**

Run any of them with no arguments. Each prints what it did, what it measured, and what
result would refute it.

---

## 1. `exp1_aperture_gpu.py` — where exactly does the content matcher break?

**The finding it comes from.** A content-match delta reports 33.2% of cells unchanged on a
repeating texture when 100% of cells actually moved. Every cell has many perfect matches,
so the matcher returns *a* match instead of *the* match. The cheap answer is wrong and it
looks right.

**Why a GPU.** The matcher is `O(cells × (2r+1)²)` per frame. Sweeping lattice families ×
radii × noise levels × matcher rules is ~10^10 distance evaluations, which is nothing on a
GPU and an afternoon on a CPU. The point is not the speed — it is that a **continuous
sweep finds the exact regime boundary**, where integer-step testing only brackets it.

**What to look for.** The radius/noise curve where ground-truth error and matcher-reported
error diverge. The gap between them IS the blind spot, and a GPU makes the whole surface
visible instead of three points on it.

---

## 2. `exp2_mode_search.py` — the mode menu, searched rather than guessed

**The finding it comes from.** Three repos are building the same cell codec and **none of
them has a per-cell mode menu** — a transmitted choice among {literal, delta, skip, coarse}
where the mode itself is transmitted and `skip` is nearly free. `qthe-codec` has a 2-bit
per-cell mode field that is **dead code**: zero call sites outside its own definition.

**Why a GPU.** Choosing modes per cell under an explicit rate–distortion objective is a
coupled search. Brute force over mode assignments is exactly the shape a GPU is for, and the
coupling means the greedy answer is not the optimal one.

**What to look for.** How much a transmitted mode actually saves against a fixed-width
baseline, and where the aperture trap eats the gain. If the mode field costs more bits than
it saves, the honest answer is that the menu does not pay and that is worth knowing.

---

## 3. `exp3_barcode_gpu.py` — the thread I killed, run anyway

**The finding it comes from.** "A witness log IS a persistent-homology barcode" is
**numerology** — Cohen-Steiner et al. 2007 requires continuous *tame* functions, and a
witness log is a persistence module, so the stability bound does not transfer. That kill
was about *theory*.

**Why it still belongs on a GPU.** The theory failed; the *computation* did not. Computing
barcodes over real witness logs is the classic GPU workload (GUDHI/CUDA, simBa/OpenCL), and
a GPU makes "test the refuted idea empirically at scale, now" cheap enough that refusing on
theory alone is a weaker position than it looks.

**What to look for.** Whether the empirical barcode structure of a real witness log carries
signal the theory says it should not. **A negative here is as valuable as a positive** — it
would close the thread empirically instead of only mathematically.

---

## 4. `exp4_fleet_embed.py` — semantic readiness, to replace my keyword matcher

**The finding it comes from.** The wheel ranks 31 papers by **keyword matching**, and the
oracle calibration showed that matcher **under-counts**: three papers it called thin look
pressable. Keyword matching also cannot see a repo named after nothing the paper says.

**Why a GPU.** Embedding every README, white-paper, and ecosystem README in a 3,900-repo
fleet and clustering them is the canonical GPU job, and the clusters *are* the readiness
answer — semantically, not lexically.

**What to look for.** Whether semantic clusters agree with the keyword spine. Where they
diverge, the keyword matcher is wrong and the cluster is right. **This is the highest-value
experiment on the list** because it replaces the weakest instrument in the wheel.

---

## 5. `exp5_tie_sweep.py` — how many repeats does a glyph readout actually need?

**The finding it comes from.** The quantum encoder **breaks ties**: two cells with the same
input value come back different. So a single-shot readout cannot be trusted, and repeated
measurement is the proposed fix.

**Why a GPU.** `N repeats × M cells` is embarrassingly parallel and the expensive part is
the sweep over `N` — finding the **plateau**, the point where accuracy stops improving.
Getting that curve is what decides whether the quantum glyph path is viable at all.

**What to look for.** Where accuracy plateaus. **If it plateaus below 1.0, repeated
measurement does not rescue the readout and the quantum glyph codec is not viable** — which
is a real, useful, negative answer.

---

## 6. `exp6_kasteleyn.py` — the one exact calibration available

**The finding it comes from.** Everything tonight was calibrated against estimates. The
one closed form available is the dimer/Kasteleyn partition function:
`Z = |Pf K|` on a planar graph, and the honeycomb's entropy-maximising state is
`log((4+3√3)/2) ≈ 1.1989` per dimer. A cell lattice with a two-colouring *is* a dimer
graph.

**Why a GPU.** Exact Pfaffians on large lattices are sparse linear algebra — cuSOLVER. It
buys the ability to compare a measured compression cost against a number that is not an
estimate.

**What to look for.** Whether a measured cell-lattice residual entropy lands on a known
dimer entropy. If it does, compression is calibrated against a closed form for the first
time.

---

## Order to run them

| # | why first | needs GPU? |
|---|---|---|
| 4 | replaces the weakest instrument in the wheel | strongly benefits |
| 1 | turns a bracketed failure into a mapped boundary | strongly benefits |
| 5 | decides viability of a whole codec path | benefits |
| 2 | the largest single unbuilt capability | benefits |
| 3 | closes a refuted thread empirically | strongly benefits |
| 6 | the only exact anchor | CPU is fine |

## The rule for this lab

**Every script prints which path it took.** If it fell back to CPU, the report says CPU.
A number that came from the fallback must never be quoted as a GPU result — that is the
CRDT finding restated: a headline that cannot vary is not evidence, and neither is one
that varied for the wrong reason.
