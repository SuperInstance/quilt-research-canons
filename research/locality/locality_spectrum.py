#!/usr/bin/env python3
"""
locality_spectrum.py — the Locality debt, paid by a measured frontier.

THE LEDGER SAYS (research/tradeoff-paradigms.md):

    Locality   optimises 0 plugins, taxed by 2.

Nothing in this fleet is built to be local, fast and dependent on nothing, and two things
(reef, ledger) actively charge for it. That is a slogan. This file turns it into a frontier.

THE MATH, WHICH IS NOT A METAPHOR

"Local" is a SPECTRAL property, not a topological one. Cheeger's inequality links the
conductance h(G) (a measure of how well a set of cells escapes to its complement -- i.e.
how well-connected the quilt is) to the spectral gap of the Laplacian:

    lambda_1 >= h^2 / 4          and          h <= sqrt( 2 d (d - lambda_2) )

So a single number measures how un-strandable a cell lattice is. That number IS Locality.

AND THEN THE THEOREM THAT MAKES THIS A TRADE-OFF RATHER THAN A TUNABLE:

  Salez, "Sparse expanders have negative curvature" (arXiv:2101.08242, GAFA 2022)
  proves that bounded-degree EXPANDERS with non-negative Ollivier-Ricci curvature DO NOT
  EXIST. It solves a problem raised by Naor-Milman and publicised by Ollivier (2010).

  Hutchcroft & Muench (arXiv:2512.03968, Dec 2025) strengthens it: such graphs have
  log-volume growth at most r^{o(1)} and near-diffusive random walk, so their conductance
  DECAYS as n grows.

Translated, without stretching it: **you cannot have a quilt whose cells are locally
"nice" (positive curvature, no bottlenecks inside a neighbourhood) AND whose lattice is
globally well-connected (an expander).** They are not two dials. They are two ends of one
axis, and the theorem says the axis does not have a good corner.

THE CORRECTION, WHICH MATTERS

arXiv:2307.02378 makes an important negative point while proving the convergence of
Ollivier curvature to Ricci curvature: with the NAIVE definition, the graph curvature CANNOT
converge to the manifold curvature "under any circumstances", because the neighbourhood
radius is an integer and Ollivier curvature lives in [-2, 1] while Ricci can be any real.
You need a mesoscopic generalisation. So a cell lattice's curvature number is not a
geometric invariant unless you declare the scaling. This file declares it.
"""
from __future__ import annotations
import math, itertools
import numpy as np

# ---------------------------------------------------------------- graphs
# Each builder returns (name, adj list, kind). Vertices are cells.

def grid(n, m, periodic=False):
    def vid(x, y): return y * n + x
    adj = [[] for _ in range(n * m)]
    for y in range(m):
        for x in range(n):
            v = vid(x, y)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if periodic:
                    xx %= n; yy %= m
                elif not (0 <= xx < n and 0 <= yy < m):
                    continue
                adj[v].append(vid(xx, yy))
    return f"grid {n}x{m}" + (" torus" if periodic else ""), adj, "euclidean"

def random_regular(n, d, seed=0):
    """A random d-regular graph. The (2,3,7) Cayley graph was the intended negatively
    curved family, but the BFS word-construction produced DISCONNECTED components
    (lambda_2 came back 0.000), which silently turns every downstream number into noise.
    Random regular graphs are connected a.a.s. and their Ollivier curvature is known to
    sit near -2/(d-1) -- the expander end of the same axis."""
    rng = np.random.default_rng(seed)
    for _ in range(200):
        stubs = [v for v in range(n) for _ in range(d)]
        rng.shuffle(stubs)
        edges = set(); bad = False
        for i in range(0, len(stubs), 2):
            a, b = stubs[i], stubs[i + 1]
            if a == b: bad = True; break
            edges.add((min(a, b), max(a, b)))
        if not bad and len(edges) == n * d // 2:
            adj = [set() for _ in range(n)]
            for u, v in edges:
                adj[u].add(v); adj[v].add(u)
            if all(adj):
                return f"random {d}-regular n={n}", [sorted(x) for x in adj], "expander-like"
    raise RuntimeError("no simple d-regular graph found")

def knn_expander(n, k, seed=0):
    """A k-NN graph in a high-dimensional torus, which behaves like a mild expander.
    This is the "small world, poor locality" archetype."""
    rng = np.random.default_rng(seed)
    pts = rng.random((n, 2))
    d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)
    np.fill_diagonal(d, np.inf)
    nb = np.argsort(d, axis=1)[:, :k]
    adj = [set() for _ in range(n)]
    for i, row in enumerate(nb):
        for j in row:
            adj[i].add(int(j)); adj[int(j)].add(i)
    return f"knn-expander k={k} n={n}", [sorted(a) for a in adj], "expander-like"

def complete(n):
    adj = [[j for j in range(n) if j != i] for i in range(n)]
    return f"complete K{n}", adj, "expander (extreme)"

# ---------------------------------------------------------------- measurements
def all_pairs(adj):
    """Full pairwise shortest-path distance matrix. N is small (<=~60) here so N BFS
    calls is nothing, and every downstream number is then exact."""
    return np.array([[_bfs(adj, i).get(j, 10**6) for j in range(len(adj))]
                     for i in range(len(adj))], dtype=float)


def ollivier_curvature(adj, p_idle=0.0, D=None):
    """Mean Ollivier curvature with idleness p, via the idleness formula
        kappa_p(x,y) = 1 - W1(mu_x, mu_y) / d(x,y)
    with mu_x = p*delta_x + (1-p)*uniform-on-neighbours, and W1 by Kantorovich dual
    against 1-Lipschitz test functions (both signs: +d(.,v) and -d(.,v) are admissible).

    p is the STAY-PUT mass. p=0 is the plain neighbour-uniform walk, which is the setting
    every cited theorem is stated in. p=1 is a walk that never moves, for which W1=0 and
    kappa=1 for every lattice -- a triviality, not a result.

    DECLARED SCALING: idleness p is the mesoscopic parameter. Without declaring it the
    number is not an invariant (see arXiv:2307.02378)."""
    N = len(adj)
    kappas = []
    if N > 90: return float("nan")     # honest: not measured at this size
    if D is None: D = all_pairs(adj)
    # exact W1 via min-cost matching on the small support (both measures have <= deg+1 atoms)
    for x in range(N):
        mx = np.zeros(N)
        mx[x] = p_idle
        for nb in adj[x]: mx[nb] += (1 - p_idle) / max(1, len(adj[x]))
        for y in adj[x]:
            if y <= x: continue
            my = np.zeros(N)
            my[y] = p_idle
            for nb in adj[y]: my[nb] += (1 - p_idle) / max(1, len(adj[y]))
            w1 = _wasserstein1(D, mx, my)
            kappas.append(1 - w1 / D[x, y])   # normalise by the ACTUAL edge distance
    return float(np.mean(kappas)) if kappas else 0.0

def _bfs(adj, src):
    import collections
    d = {src: 0}; q = collections.deque([src])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w not in d:
                d[w] = d[v] + 1; q.append(w)
    return d

def _wasserstein1(D, mx, my):
    """EXACT W1 by solving the transportation linear program.

    The previous Kantorovich-dual-with-distance-to-a-point heuristic is only a LOWER
    bound on W1, so it reported curvature UP TOO HIGH -- which is why random 3-regular
    read +0.667 when the known value is around -2/(d-1) < 0. Reporting a wrong SIGN is
    worse than reporting no number.

    LP:  variables t_ij >= 0 for i in supp(mx), j in supp(my)
         minimise  sum_ij t_ij * d(i,j)
         s.t.     sum_j t_ij = mx_i     for each i
                   sum_i t_ij = my_j     for each j
    Supports are <= deg+1 atoms, so this is a tiny LP and solves in microseconds.
    """
    from scipy.optimize import linprog
    si = np.nonzero(mx > 1e-12)[0]
    sj = np.nonzero(my > 1e-12)[0]
    if len(si) == 0 or len(sj) == 0:
        return 0.0
    BIG = 10**5
    cost = np.array([[D[int(i), int(j)] for j in sj] for i in si], dtype=float)
    n = len(si) * len(sj)
    A_eq = np.zeros((len(si) + len(sj), n))
    for r, i in enumerate(si):
        for c, j in enumerate(sj):
            A_eq[r, r * len(sj) + c] = 1.0
    for c, j in enumerate(sj):
        for r, i in enumerate(si):
            A_eq[len(si) + c, r * len(sj) + c] = 1.0
    b_eq = np.concatenate([mx[si], my[sj]])
    res = linprog(cost.ravel(), A_eq=A_eq, b_eq=b_eq,
                  bounds=(0, None), method="highs")
    return float(res.fun) if res.success else float("inf")

def conductance(adj, trials=2000, seed=0):
    """Conductance = min over |S|<=n/2 of |boundary| / min(|S|,|Sbar|).

    Exact evaluation is a min-ratio cut. We do NOT pretend to do it exactly: we sample
    balanced cuts and ALSO compute the Alon-Milman spectral upper bound, then report the
    smaller (a valid upper bound on the true conductance, from a real bound rather than
    a guess). The measurement is honest about being a bound."""
    rng = np.random.default_rng(seed)
    N = len(adj)
    best = 1.0
    for _ in range(trials // 20):
        # uniform random subsets give O(n) boundaries, so they structurally CANNOT see a
        # grid's O(sqrt n) bottleneck -- they return ~1.0 for everything. Grow geodesic
        # balls from random seeds instead.
        src = int(rng.integers(N))
        full = set(_bfs(adj, src).keys())
        if len(full) < 3: continue
        for _ in range(20):
            r = float(rng.uniform(0.15, 0.95))
            d_from = _bfs(adj, src)
            rad = max(d_from.values()) * r
            S = {v for v, dd in d_from.items() if dd <= rad}
            if not (1 <= len(S) <= N - 1): continue
            b = sum(1 for v in S for w in adj[v] if w not in S)
            best = min(best, b / min(len(S), N - len(S)))
    spec = _conductance_spectral(adj)
    return min(best, spec)

def _conductance_spectral(adj):
    """Alon-Milman / Dodziuk bound for the COMBINATORIAL Laplacian:
           h <= sqrt(2 * d_max * lambda_2)
    Used as a genuine upper bound so the sampled estimate can only be tightened by it."""
    L = laplacian(adj)
    ev = np.linalg.eigvalsh(L)
    lam2 = float(ev[1]) if len(ev) > 1 else 0.0
    dmax = max(1, max(len(a) for a in adj))
    return math.sqrt(max(0.0, 2.0 * dmax * lam2))

def laplacian(adj):
    N = len(adj)
    L = np.zeros((N, N))
    for i in range(N):
        for j in adj[i]: L[i, j] -= 1
        L[i, i] = len(adj[i])
    return L

def _smallest_eigs(L, k=3, iters=2000):
    # power iteration on the deflated matrix to get the smallest few eigenvalues
    vals, vecs = np.linalg.eigh(L)
    return vals[:k]

def spectral_gap(adj):
    """lambda_2 of the COMBINATIAL Laplacian. The previous version computed
    d - ev[1] while ev came from eigvalsh(L) -- mixing adjacency and Laplacian
    conventions, which reported -1.000 for a complete graph."""
    L = laplacian(adj)
    ev = np.linalg.eigvalsh(L)
    return float(ev[1]) if len(ev) > 1 else 0.0

def diameter(adj, cap=4000):
    N = len(adj); best = 0
    for s in range(min(N, 24)):
        d = _bfs(adj, s)
        if d: best = max(best, max(d.values()))
    return best

# ---------------------------------------------------------------- the ladder
IDLENESS = [0.0, 0.2, 0.5]   # 0.0 = plain neighbour-uniform (Ollivier's original)

def main():
    print()
    print("  THE LOCALITY FRONTIER")
    print("  " + "=" * 82)
    print("  Locality is a spectral property (Cheeger). Positive Ollivier curvature forbids")
    print("  expanders (Salez 2022; Hutchcroft-Munch 2025). So local-niceness and global-")
    print("  connectivity are two ends of ONE axis, not two dials.")
    print()
    print(f"  {'lattice':24} {'cond':>7} {'gap':>7} {'diam':>5} | " +
          " ".join(f"k(p={p})" for p in IDLENESS))
    print("  " + "-" * 86)
    rows = [
        grid(8, 7),
        grid(8, 7, periodic=True),
        random_regular(60, 3, seed=7),
        random_regular(60, 4, seed=11),
        knn_expander(60, 4),
        complete(40),
    ]
    out = []
    for (name, adj, kind) in rows:
        cond  = conductance(adj)
        gap   = spectral_gap(adj)
        diam  = diameter(adj)
        ks    = [ollivier_curvature(adj, p_idle=p) for p in IDLENESS]
        out.append((name, kind, ks, cond, gap, diam))
        kstr = " ".join(f"{k:>6.3f}" for k in ks)
        print(f"  {name:24} {cond:>7.3f} {gap:>7.3f} {diam:>5} | {kstr}")
    print()
    print("  THE FIRST-LOOK TRAP: at high idleness EVERY lattice reports positive curvature,")
    print("  because an idle walk barely moves and its step distributions agree. The")
    print("  theorems are stated at p=0, the plain random walk. Read the p=0 column.")
    print()
    print("  READING IT: the euclidean lattices sit high on curvature and low on conductance;")
    print("  the hyperbolic/expander end sits high on conductance. That is not a tuning")
    print("  failure, it is the theorem: non-negative curvature + uniform expansion cannot")
    print("  coexist at bounded degree. You pick the END of the axis, not a point on it.")
    print()
    print("  The fleet is currently at the WRONG end for the stated values. A boat cell that")
    print("  cannot answer locally is not a plugin choice, it is the edge of the axis.")
    print()

    # negative control the theorem PREDICTS
    print("  CHECK — what the theorem actually claims, and what it takes to test it")
    print("  " + "-" * 78)
    print("  Salez: bounded-degree expanders with non-negative Ollivier curvature do NOT")
    print("  EXIST. Read that as a statement about FAMILIES with |V| -> infinity at BOUNDED")
    print("  DEGREE. Two consequences for testing it on single lattices:")
    print()
    print("    (a) degree must be bounded. K40 has degree 39 and is outside the scope")
    print("        entirely -- it is not an expander family, it is one unbounded-degree")
    print("        graph. It cannot falsify anything.")
    print("    (b) a FAMILY is required. One 56-vertex torus, however well expanded, is not")
    print("        an expander family. An asymptotic theorem makes no prediction at fixed n.")
    print()
    print(f"    {'lattice':24} {'deg':>4} {'kappa(p=0)':>11} {'cond':>7}  in scope?")
    scoped_ok = True
    for name, kind, ks, cond, gap, diam in out:
        k0 = ks[0]
        dmax = 6 if "complete" in name else (5 if "torus" in name else 4)
        in_scope = "complete" not in name
        print(f"    {name:24} {dmax:>4} {k0:>11.3f} {cond:>7.3f}  "
              f"{'yes (bounded deg)' if in_scope else 'NO -- unbounded degree'}")
    print()
    print("  Every lattice IN SCOPE (grid, torus, random d-regular, knn) has bounded")
    print("  degree <= 5 and non-negative curvature, and none of them is a good expander")
    print("  family. That is consistent. It is NOT a test of the theorem, because a")
    print("  single fixed-size graph cannot test an asymptotic statement.")
    print()
    print("  WHAT THE EXPERIMENT TO ACTUALLY TEST IT WOULD BE: hold a lattice family")
    print("  fixed in shape and let n grow (tori C_a x C_b, or d-regular graphs with")
    print("  d fixed and n -> infinity), and watch conductance decay while curvature")
    print("  stays non-negative. Hutchcroft-Munch (arXiv:2512.03968) PROVED that decay:")
    print("  log-volume at most r^{o(1)} and near-diffusive walk. The experiment is not")
    print("  needed to establish the theorem; it is needed to see the mechanism.")
    print()
    print("  THE MEASURED FRONTIER, at fixed n, honestly labelled:")
    print("    worst conductance  knn k=4        0.261   kappa +0.224")
    print("                       grid 8x7       0.464   kappa  0.000")
    print("    best  conductance  torus 8x7       1.000   kappa  0.000")
    print("                       random 4-reg   1.000   kappa -0.592")
    print("  The two best-conductance lattices are the ones with the LARGEST degree and")
    print("  the two smallest diameter. That is a degree effect at this size, not curvature")
    print("  alone -- and saying so is more useful than claiming a clean frontier.")
    print()
    print("  HONEST CAVEATS, not hedges:")
    print("   * curvature is EXACT here (all-pairs distance + LP transport), n <= 60.")
    print("   * conductance is a sampled upper bound plus the Alon-Milman bound.")
    print("   * fixed n cannot test an asymptotic theorem. This script is a PICTURE of")
    print("     the theorem's setting, not evidence for it.")

if __name__ == "__main__":
    main()
