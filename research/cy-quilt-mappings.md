---
title: Calabi–Yau, quivers, tropical tie-loci, and the curvature of a cell lattice
date: 2026-09-29
subject: which mappings to manifolds are theorems, and which are only metaphors
---

## Why this document exists

Casey's instruction was to think in metaphors, analogies, and *even direct mappings* to
Calabi–Yau manifolds, and to research the cutting edge rather than decorate. That makes a
**sorting duty** the first deliverable, and the sorting is unfashionable:

| claim | status |
|---|---|
| A quiver **is** a finite graph | **THEOREM-BACKED CONSTRUCTION** (Nakajima) |
| Quiver varieties give Calabi–Yau threefolds | **THEOREM** (ADE fibre CY3s as quiver moduli) |
| Ollivier curvature converges to Ricci curvature | **THEOREM, with a required correction** |
| Non-negative curvature forbids expanders | **THEOREM** (Salez 2022; Hutchcroft–Münch 2025) |
| The tropical variety is a **tie locus** | **THEOREM** (definition) |
| A flop: one object, two presentations | **THEOREM** (Kollár–Mori) |
| 6D cell graph ↔ CY threefold (real dim 6) | **NUMEROLOGY. No mechanism found.** |

The last row matters. A CY threefold is real 6-dimensional, this fleet keeps saying "6D",
and that is *not* a derivation. Dimension matching is the cheapest possible coincidence and
I could not find a mechanism that would make it more than that. Everything below is
everything that survived being held to that standard.

---

## 1. A cell graph IS a quiver, and a quiver gives you a Calabi–Yau threefold

This is the strongest mapping and it is a construction, not an analogy.

A **quiver** is, by definition, *"a finite graph with possibly loops and multiple edges."*
That is a cell graph. Nothing is being reinterpreted — the objects coincide.

Nakajima then takes a quiver `Q` with a dimension vector and forms

```
M = T*(Rep Q) // G_v
```

a **symplectic reduction**, and (Bellamy–Schedler, arXiv:1602.00164) proves the smooth locus
is exactly the locus of θ-**polystable** points. And the payoff, from arXiv:math/0506301:

> *"small resolutions of ADE fibered Calabi–Yau threefolds are realized as moduli spaces
> of representations of `A_τ(Q)`"* — and
> *"X is Calabi–Yau if and only if Q has canonical determinant on C."*

So the chain is real and each link is a theorem:

```
cells + arrows  →  quiver  →  representation variety  →  symplectic resolution  →  CY threefold
```

**And the link that matters most for the fleet is a *stability condition*.** A metric on a
Kähler manifold exists if and only if the class is **K-polystable** (Yau–Tian–Donaldson).
Polystability is defined by the moment-map functional being convex and bounded below — a
**purely combinatorial condition on a quiver and a dimension vector.** The Hitchin–Kobayashi
correspondence's analogue: the analytic object exists exactly when the algebraic one passes
a test that has nothing to do with analysis.

> **A cell system admits a canonical metric iff a purely combinatorial stability condition
> holds.** That is a gate, and it is the same *shape* as the JEV gate — but K-polystability
> is a theorem rather than a calibrated threshold, which is the thing JEV is not.

There is a second, stranger link. arXiv:1812.07687 shows **"crab-shaped"** quivers give
character varieties of punctured Riemann surfaces, and that the whole package is a
**2-Calabi–Yau algebra**. A crab is a cell lattice with a puncture in the middle. The
punctured surface is the fleet's own substrate.

## 2. The tropical variety is the tie locus — which is the mode menu, in disguise

Tropicalization is a *limit* (large-`u` asymptotics) that turns a smooth object into a
piecewise-linear one. The definition that matters (arXiv:1410.4131 / standard refs):

```
V(f) = { x | f is not differentiable at x }  =  { x | AT LEAST TWO TERMS TIE FOR THE MAX }
```

A tropical variety is a **polyhedral complex whose cells are where two modes tie.** Its
Newton polytope has vertices in bijection with the connected components of the complement
of the amoeba (Passare–Rullgård), and the amoeba of a plane curve has area ≤ π² · area of
its Newton polytope — a *quantitative* statement about how much smooth structure a
polyhedral encoding can hide.

Now recall Lane U. The codec needs a **mode menu**: per cell, one of {literal, delta, skip,
coarse}, with the mode transmitted. A pyramid says how much to spend; a menu says which way
to describe this cell.

> **The tropical variety IS the mode menu's boundary.** A cell is unconstrained where one
> term strictly dominates — that is the interior of a mode region, and it is cheap. A cell
> is *interesting* exactly where two modes tie, and that is the polyhedral complex.

So the polyhedral cell complex a glyph lattice is **not** a discretisation of a continuous
field. It is the tie-locus of competing descriptions, and its combinatorial type (the
Newton polytope) bounds how much the continuous version can be doing. Passare–Rullgård
gives the bound. **The cell count is not the information content; the tie structure is.**

## 3. One object, two presentations: flops

arXiv:2512.14817 (Dec 2025) states it cleanly: the extended Kähler cone decomposes into
chambers, and

> *"crossing a facet (codimension-one face) separating two chambers enacts a **flop** between
> the two CY manifolds, an elementary type of birational map."*

Two Kähler classes on one complex manifold, not deformation-equivalent, **preserving all
Betti numbers**, related by a birational map. The object is fixed; the presentation changes.

That is `two-views` with a theorem behind it. The human projection and the agent projection
are two chambers over one substrate, and a flop is the operation that moves between them
without changing what is underneath. The polyformalism/typed-runtime split the fleet keeps
separate is a flop that has not been performed.

## 4. The correction: cell curvature is not a geometric invariant until you declare the walk

arXiv:2307.02378 proves Ollivier curvature of random geometric graphs converges to the
Ricci curvature of the latent manifold, rescaled:

```
lim  [ κ_G(x,y) / (δ²n)  −  Ric(v,v) / (2(D+2)) ]  =  0
```

and, in the same breath, makes a point I had to be shown twice today:

> *"Ollivier curvature of graphs as defined above **cannot** converge to Ricci curvature of
> manifolds under any circumstances, simply because δ is no longer real but integer, so
> that lim_{δ→0} makes no sense, and because Ollivier graph curvature is always between −2
> and 1, while Ricci curvature can be any real number."*

**A cell lattice's curvature is a function of the walk, and the walk must be part of the
claim.** `locality_spectrum.py` swept it: at stay-put mass p=0.5 the same grid reads
κ=+0.033; at p=0.2, +0.052; at p=0, **0.000**. A walk that never moves reports κ=1 for
every lattice in existence.

## 5. The finding: Locality is a spectral property, and it is in tension with expansion

This is the one that pays a debt. The trade-off ledger says **Locality: optimised by 0
plugins, taxed by 2.** A slogan. Cheeger's inequality makes it a measurement:

```
lambda_1 >= h² / 4        h(G) = min over |S|<=n/2 of |∂S| / min(|S|, |Sbar|)
```

`h` measures how well a set of cells escapes to its complement — how un-strandable the
lattice is. That number *is* Locality, and it is a spectral quantity, not a vibe.

And then the theorem that makes it a trade-off rather than a tunable:

> **Salez, "Sparse expanders have negative curvature" (arXiv:2101.08242, GAFA 2022):
> bounded-degree expanders with non-negative Ollivier–Ricci curvature do not exist.**
> It solves a problem raised by Naor–Milman and publicised by Ollivier in 2010.
>
> **Hutchcroft–Münch (arXiv:2512.03968, Dec 2025)** strengthens it: such graphs have
> log-volume growth at most `r^{o(1)}` and near-diffusive random walk, so conductance
> *decays* as n grows.

Local niceness and global connectivity are **two ends of one axis, not two dials.** A
lattice that wants to be locally well-behaved cannot also be a good expander, and the
theorem says so at bounded degree.

### What the instrument actually found (and what it did not)

`locality_spectrum.py`, curvature **exact** (all-pairs distance + LP optimal transport),
`n ≤ 60`:

```
lattice                   deg  kappa(p=0)    cond
grid 8x7                    4       0.000   0.464
grid 8x7 torus              4       0.000   1.000
random 3-regular n=60       4      -0.533   0.467
random 4-regular n=60       4      -0.592   1.000
knn-expander k=4 n=60       4       0.224   0.261
complete K40               39       0.974   1.000   <- out of scope, unbounded degree
```

Two things worth stating and one worth refusing to state.

**Worth stating:** the two lattices with the *best* conductance are the ones with the
*largest degree and smallest diameter*. At this size that is a **degree effect**, not
curvature alone. And the random `d`-regular graphs — the genuine expanders — are exactly
the **negatively** curved ones, which is the theorem's signature.

**Refusing to state:** this is **not a test of Salez's theorem.** A single fixed-size graph
cannot test an asymptotic claim, and K40 has degree 39 so it is outside the bounded-degree
hypothesis entirely. My first version of this check demanded a biconditional and printed
*instrument suspect* on a correct measurement; the check was wrong, not the data. The
honest version of the experiment is to hold a lattice **family** fixed in shape, let n
grow, and watch conductance decay while curvature stays non-negative — which
Hutchcroft–Münch already proved happens.

### Four bugs this instrument had, all of which produced confident wrong numbers

Recorded because the pattern is the point, not the individual mistakes:

1. **A `str.replace` that silently no-op'd** on whitespace mismatch, leaving the old
   formula in place. Every number after it was void and looked fine.
2. **W1 by Kantorovich dual testing only `+d(·,v)`** — `-d(·,v)` is also 1-Lipschitz, so
   the "max" was pinned at 0 and curvature read **1.000 on every lattice**.
3. **Passing a single-source BFS where pairwise distance `d(i,j)` was required.** The
   transport LP saw a cost matrix with a free column and returned `W1 = d(x,y)` for every
   pair, so curvature read **identically 0.000**.
4. **The idleness parameter read backwards** — `p` is the stay-put mass, so `p=0` is
   neighbour-uniform (what the theorems use) and `p=1` is a walk that never moves.

Two of those four made a real phenomenon look like a result: #2 made a flat lattice look
positively curved, and #4's first form made a *positively* curved lattice look flat. A
measurement that cannot produce a wrong sign is not a measurement.

## 6. Exactly solvable cell lattices: Kasteleyn

For planar bipartite graphs the dimer partition function is `Z = |det K|`; for planar
graphs generally `Z = |Pf K|`; on a genus-`g` surface it is a sum of `2^{2g}` Pfaffians.
Polynomial time either way (Kasteleyn 1961, Temperley–Fisher).

A **cell lattice with a two-colouring is a dimer graph**, and a checkerboard is a Kasteleyn
orientation. The log-partition function is a convex, plurisubharmonic potential — the same
object as the "calibration" the ledger's Calibration paradigm is trying to build, except
this one is **exact and has a closed form** for the entropy-maximising state (honeycomb:
`log((4+3√3)/2) ≈ 1.1989` per dimer).

This is the one place in the fleet where an entropy is *solvable* rather than estimated.
It is a small, sharp, checkable target: **find the cell lattice whose residual entropy
matches a known dimer entropy**, and you have calibrated compression against an exact
answer rather than against an intuition.

## 7. What I did not find

- **A mechanism** connecting "6D" to CY threefolds. Dimension matching. Left as
  numerology, deliberately.
- **A mirror-symmetry statement for two projections of one substrate.** Mirror symmetry
  (`h^{p,q} ↔ h^{3-p,q}`) is the nearest thing in mathematics to "one object, two
  presentations," and I looked for the transport to `two-views` and did not find one.
  Flops are the honest substitute; mirror symmetry is not, yet.
- **A Hodge-theoretic reading of the witness log.** A cell's history as a bar segment in a
  barcode is *very* close to persistent homology, and the stability theorem would make
  "witness log as prediction" rigorous. I did not verify that connection, so it is not
  claimed here. It is the most promising thread I did not pull.

## 8. The build order this implies

1. **Declare the walk with every curvature claim.** Cheap, and today's instrument was
   wrong three times because this was left implicit.
2. **Grow a lattice family and measure the conductance decay** (tori, fixed-`d` regular
   graphs, n → ∞). That is the real experiment behind the real theorem, and it produces the
   Locality row of the ledger as a curve rather than an opinion.
3. **K-polystability as the gate.** It is the JEV gate's shape with a theorem behind it
   instead of a calibrated threshold. The obvious first instance: a quiver's dimension
   vector, and the question "does a canonical metric exist?"
4. **The tie-locus as the mode menu.** The tropical variety is already the boundary
   between descriptions; the codec wants that boundary and does not know it has a name.
5. **A cell lattice with a known dimer entropy** — the one exact calibration available.
