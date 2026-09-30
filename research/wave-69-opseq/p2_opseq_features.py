#!/usr/bin/env python3
"""Wave-69 P2 — contract-side opcode-sequence encoding (lane 69-c).

PRE-REGISTERED in README.md BEFORE running. Cheap sequence instruments over
the evaluation journal (identity-free encodings; no cell names, no payloads):

  ENC-1 oporder  : bare op token sequence per run (BIND/EFFECT/VIEW/TICK/LINK/FORGET)
  ENC-2 rolecode : op:ROLE tokens (route->ROUTING quf->FILTER time/world->PROJECTION
                   crdt->STATE proof->VERIFY engine->ITERATOR)  [cell-derived, weaker]

Instruments (5, registered): bigram-TF cos, trigram-TF cos, Levenshtein sim,
Needleman-Wunsch global-alignment sim, Smith-Waterman local-alignment sim.

TWO PRE-RUN AMENDMENTS (fixed BEFORE any instrument ran; causes are receipts,
not taste — see README DEVIATIONS section):

  AMEND-1 (liveness pair class). The registered P2-alpha statistic
  "mean sim(same cell, same seed, same sched) > mean sim(same cell, same seed,
  diff sched)" is ill-posed: there is exactly ONE doc per (cell, seed, sched),
  so the same-sched class is the doc against itself (trivial 1.0), and the
  within-(cell,seed) permutation null can never produce a same-label pair
  (4 distinct labels over 4 docs). Corrected liveness:
    L1 (PRIMARY, cross-cell): mean sim(diff cell, same sched) >
        mean sim(diff cell, diff sched); null = schedule-label permutation
        WITHIN each cell (labels stay balanced). Non-trivial question: does
        the schedule leave a cell-INDEPENDENT signature in the opcode sequence?
    L2 (within-cell, sanity): mean sim(same cell, diff seed, same sched) >
        mean sim(same cell, diff seed, diff sched); same null design. Under
        the receipted seed-degeneracy of op-token docs, same-sched pairs are
        IDENTICAL docs (sim exactly 1.0) — L2 is a degeneracy witness, not
        evidence of order sensitivity, and is reported as such.

  AMEND-2 (C1-trace pair class). Registered text: "same-cell cross-schedule
  pairs". Implemented literally: same cell AND different schedule. (Pooling in
  same-schedule identical-doc pairs would stuff 1.0s into the mean and blur
  the dialect read.)

Receipted corpus fact (census below): op-token docs are seed-degenerate —
exactly 1 unique op sequence per (cell, schedule), 28 unique docs per encoding.
Payload-bearing P1 variants (full/statesonly) are NOT degenerate.

Registered bar (unchanged): P2 CONFIRMED iff >=3/5 instruments pass BOTH
C1-cell (TRUE 3/3 split ranks #1 of all 20 assignments on ALL 4 schedules)
AND C1-trace (500-permutation cell-label-shuffle null, p<0.05), on ENC-1.
Otherwise KILLED and the wave-68 law extends to cheap sequence features.
Liveness gate (registered spirit, corrected statistic): >=3/5 instruments at
L1 p<0.05, else instruments are blind to order across cells and no dialect
verdict may be issued (kill is then attributed to instrument blindness).
"""
import itertools
import json
import os
import random
import subprocess
import time
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = f"{HERE}/trace_gram_sched"

CELLS = ["route", "crdt", "time", "quf", "world", "proof", "engine"]
DIALECT = ["route", "quf", "time", "crdt", "proof", "world"]
BETWEEN = ("route", "quf", "time")
INCELL = ("crdt", "proof", "world")
ROLE = {"route": "ROUTING", "quf": "FILTER", "time": "PROJECTION", "world": "PROJECTION",
        "crdt": "STATE", "proof": "VERIFY", "engine": "ITERATOR"}
SEEDS = list(range(101, 111))
SCHEDS = ["A", "B", "C", "D"]
N_PERM = 500

# ── corpus ──────────────────────────────────────────────────────────────
seqs = {}  # (cell, seed, sched, enc) -> token list
for cell in CELLS:
    for seed in SEEDS:
        for sched in SCHEDS:
            out = subprocess.run([BIN, cell, str(seed), sched],
                                 capture_output=True, text=True, timeout=30)
            steps = [json.loads(l) for l in out.stdout.splitlines() if l.strip()]
            seqs[(cell, seed, sched, "oporder")] = [s["op"] for s in steps]
            seqs[(cell, seed, sched, "rolecode")] = [f"{s['op']}:{ROLE[cell]}" for s in steps]

keys_all = [(c, s, ch) for c in CELLS for s in SEEDS for ch in SCHEDS]  # 280

# census: unique token sequences per (cell, sched) — degeneracy receipt
census = {}
for enc in ("oporder", "rolecode"):
    u = {}
    for c in CELLS:
        for ch in SCHEDS:
            u[f"{c}:{ch}"] = len({tuple(seqs[(c, s, ch, enc)]) for s in SEEDS})
    census[enc] = {"unique_per_cell_sched": u,
                   "n_unique_total": len({tuple(seqs[(c, s, ch, enc)]) for c in CELLS for s in SEEDS for ch in SCHEDS})}
print("census:", json.dumps({e: census[e]["n_unique_total"] for e in census}))

# ── instruments ─────────────────────────────────────────────────────────
def ngram_cos_matrix(docs_tokens, n):
    """log1p-TF of n-grams + L2; returns (keys, S) full cosine matrix."""
    keys = list(docs_tokens)
    vecs = []
    for toks in docs_tokens.values():
        grams = Counter(tuple(toks[i:i + n]) for i in range(len(toks) - n + 1))
        vecs.append(grams)
    vocab = sorted({g for v in vecs for g in v})
    vi = {g: i for i, g in enumerate(vocab)}
    M = np.zeros((len(keys), len(vocab)))
    for i, v in enumerate(vecs):
        for g, c in v.items():
            M[i, vi[g]] = c
    M = np.log1p(M)
    M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
    return keys, M @ M.T

def lev_dist(a, b):
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]

def lev_sim(a, b):
    return 1.0 - lev_dist(a, b) / max(len(a), len(b))

def nw_sim(a, b, match=1, mismatch=-1, gap=-1):
    """Global alignment score normalized by min(len) -> [-1, 1]."""
    na, nb = len(a), len(b)
    prev = [gap * j for j in range(nb + 1)]
    for i in range(1, na + 1):
        cur = [gap * i]
        ai = a[i - 1]
        for j in range(1, nb + 1):
            s = prev[j - 1] + (match if ai == b[j - 1] else mismatch)
            cur.append(max(s, prev[j] + gap, cur[j - 1] + gap))
        prev = cur
    return prev[nb] / min(na, nb)

def sw_sim(a, b, match=2, mismatch=-1, gap=-1):
    """Local alignment normalized by 2*min(len) -> [0, 1]."""
    na, nb = len(a), len(b)
    best = 0.0
    prev = [0.0] * (nb + 1)
    for i in range(1, na + 1):
        cur = [0.0]
        ai = a[i - 1]
        for j in range(1, nb + 1):
            s = prev[j - 1] + (match if ai == b[j - 1] else mismatch)
            v = max(0.0, s, prev[j] + gap, cur[j - 1] + gap)
            cur.append(v)
            if v > best:
                best = v
        prev = cur
    return best / (2 * min(na, nb))

INSTRUMENTS = ["bigram", "trigram", "levenshtein", "nw", "sw"]

def unique_sims(enc, instrument):
    """Compute sims on UNIQUE docs only; return (uids, U, uid->row)."""
    uids = sorted({(c, ch) for c in CELLS for ch in SCHEDS})
    utoks = {u: seqs[(u[0], SEEDS[0], u[1], enc)] for u in uids}  # seed-degenerate: any seed
    if instrument in ("bigram", "trigram"):
        _, U = ngram_cos_matrix(utoks, 2 if instrument == "bigram" else 3)
    else:
        fn = {"levenshtein": lev_sim, "nw": nw_sim, "sw": sw_sim}[instrument]
        n = len(uids)
        U = np.eye(n)
        for i in range(n):
            for j in range(i + 1, n):
                U[i, j] = U[j, i] = fn(utoks[uids[i]], utoks[uids[j]])
    ulook = {u: i for i, u in enumerate(uids)}
    return uids, U, ulook

# ── full 280x280 expansion ──────────────────────────────────────────────
doc_uid = [(k[0], k[2]) for k in keys_all]
tri_r, tri_c = np.triu_indices(len(keys_all), 1)

def expand(U, ulook):
    v = np.array([U[ulook[doc_uid[i]], ulook[doc_uid[j]]] for i, j in zip(tri_r, tri_c)])
    return v  # triu vector of sims

cell_arr = np.array([k[0] for k in keys_all])
sched_arr = np.array([k[2] for k in keys_all])
seed_arr = np.array([k[1] for k in keys_all])

def masked_mean(v, mask):
    return float(v[mask].mean()) if mask.any() else float("nan")

# ── tests ───────────────────────────────────────────────────────────────
def l1_stat(v, sl):
    """cross-cell same-sched minus cross-cell diff-sched (triu vector)."""
    cc = cell_arr[tri_r] != cell_arr[tri_c]
    ss = sl[tri_r] == sl[tri_c]
    same = cc & ss
    diff = cc & ~ss
    return masked_mean(v, same), masked_mean(v, diff)

def l1_null(v, n_perm=N_PERM, seed=692):
    """Permute schedule labels WITHIN each cell (balanced 10/10/10/10)."""
    rng = random.Random(seed)
    sl = sched_arr.copy()
    stats = []
    for _ in range(n_perm):
        for c in CELLS:
            idxs = np.where(cell_arr == c)[0]
            labs = SCHEDS * 10
            rng.shuffle(labs)
            sl[idxs] = labs
        s, _ = l1_stat(v, sl)
        stats.append(s)
    return np.array(stats)

def l2_stat(v, sl):
    """within-cell, cross-seed: same-sched minus diff-sched."""
    sc = cell_arr[tri_r] == cell_arr[tri_c]
    ds = seed_arr[tri_r] != seed_arr[tri_c]
    ss = sl[tri_r] == sl[tri_c]
    base = sc & ds
    return masked_mean(v, base & ss), masked_mean(v, base & ~ss)

def c1_trace_stat(v, cl):
    """AMEND-2: same cell AND different schedule; BETWEEN minus INCELL.
    Registered direction: dialect recovery = BETWEEN-organs cluster TIGHTER,
    i.e. value > 0 (right tail of the null)."""
    sc = cl[tri_r] == cl[tri_c]
    xs = sched_arr[tri_r] != sched_arr[tri_c]
    same = sc & xs
    bet = same & np.isin(cl[tri_r], BETWEEN)
    inc = same & np.isin(cl[tri_r], INCELL)
    return masked_mean(v, bet), masked_mean(v, inc)

def c1_trace_null(v, n_perm=N_PERM, seed=691):
    """Registered NC: 500 doc-level cell-label shuffles. AMEND-3-consistent:
    DOC-level permutation (breaking cell-doc association), not a label-set
    bijection (which preserves equality structure and is a no-op for the
    same-cell mask)."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_perm):
        cl = cell_arr[rng.permutation(len(cell_arr))]
        b, _ = c1_trace_stat(v, cl)
        vals.append(b)
    return np.array(vals)

def c1_cell_rank(enc, instrument, U, ulook):
    """Per schedule: C1-cell on the 6 unique dialect docs; TRUE split rank of 20."""
    per_sched, ranks, bet_m, inc_m = [], [], [], []
    for sched in SCHEDS:
        docs6 = [(c, sched) for c in DIALECT]
        n = 6
        S6 = np.array([[U[ulook[a], ulook[b]] for b in docs6] for a in docs6])
        def split_score(combo):
            bet, inc = [], []
            for i in range(n):
                for j in range(i + 1, n):
                    g = {docs6[i][0], docs6[j][0]}
                    if len(g) < 2:
                        continue
                    if g <= set(combo):
                        bet.append(S6[i, j])
                    elif not (set(combo) & g):
                        inc.append(S6[i, j])
            return float(np.mean(bet) - np.mean(inc))
        true_c1 = split_score(set(BETWEEN))
        scores = [split_score(set(cb)) for cb in itertools.combinations(DIALECT, 3)]
        rank = 1 + sum(1 for s in scores if s > true_c1 + 1e-15)
        per_sched.append(true_c1)
        ranks.append(rank)
        # within/between decomposition for the receipt
        b = [S6[i, j] for i in range(n) for j in range(i + 1, n)
             if {docs6[i][0], docs6[j][0]} <= set(BETWEEN)]
        ic = [S6[i, j] for i in range(n) for j in range(i + 1, n)
              if {docs6[i][0], docs6[j][0]} <= set(INCELL)]
        bet_m.append(float(np.mean(b)))
        inc_m.append(float(np.mean(ic)))
    return {"per_sched": [round(x, 4) for x in per_sched], "mean": float(np.mean(per_sched)),
            "ranks": ranks, "between_mean": float(np.mean(bet_m)), "incell_mean": float(np.mean(inc_m))}

# ── determinism self-check (cheap-instrument analogue of NC-2) ──────────
def determinism_check(enc):
    uids, U, ulook = unique_sims(enc, "levenshtein")
    a, b = uids[0], uids[-1]
    return bool(abs(lev_sim(seqs[(a[0], SEEDS[3], a[1], enc)],   # different seed, same uid
                       seqs[(b[0], SEEDS[7], b[1], enc)]) - U[ulook[a], ulook[b]]) < 1e-12)

# ── main ────────────────────────────────────────────────────────────────
receipt = {"pre_registered": "README.md (before any call)",
           "amendments": ["AMEND-1 liveness pair class (see docstring)",
                          "AMEND-2 C1-trace = same-cell CROSS-SCHEDULE pairs"],
           "census": census, "encodings": {}, "notes": []}

for enc in ("oporder", "rolecode"):
    enc_res = receipt["encodings"].setdefault(enc, {})
    enc_res["determinism_recompute_ok"] = bool(determinism_check(enc))
    for inst in INSTRUMENTS:
        t0 = time.time()
        uids, U, ulook = unique_sims(enc, inst)
        v = expand(U, ulook)
        res = {"instrument": inst, "n_docs": len(keys_all),
               "n_unique_docs": len(uids), "compute_s": round(time.time() - t0, 1)}
        # L1 primary liveness
        s1, d1 = l1_stat(v, sched_arr)
        nullL1 = l1_null(v)
        p1_ = float((np.sum(nullL1 >= s1) + 1) / (len(nullL1) + 1))
        res["L1_cross_cell"] = {"same_sched_mean": s1, "diff_sched_mean": d1, "gap": s1 - d1,
                                "p": p1_, "null_mean": float(nullL1.mean())}
        # L2 degeneracy witness
        s2, d2 = l2_stat(v, sched_arr)
        res["L2_within_cell"] = {"same_sched_mean": s2, "diff_sched_mean": d2, "gap": s2 - d2}
        # C1-cell rank among 20 assignments
        res["c1_cell"] = c1_cell_rank(enc, inst, U, ulook)
        # C1-trace + registered null
        b1, i1 = c1_trace_stat(v, cell_arr)
        nullC = c1_trace_null(v)
        pt = float((np.sum(nullC >= b1) + 1) / (len(nullC) + 1))
        res["c1_trace"] = {"between_mean": b1, "incell_mean": i1, "value": b1 - i1,
                           "p": pt, "null_mean": float(nullC.mean()), "null_sd": float(nullC.std())}
        enc_res[inst] = res
        print(f"[{enc}] {inst}: L1 {s1 - d1:+.4f} (p {p1_:.3f}) | L2 gap {s2 - d2:+.4f} | "
              f"C1-cell {np.mean(res['c1_cell']['per_sched']):+.4f} (ranks {res['c1_cell']['ranks']}) | "
              f"C1-trace {b1 - i1:+.4f} (p {pt:.3f})  [{res['compute_s']}s]", flush=True)

# embedding comparator from P1 receipt (same corpus, same encodings)
try:
    with open(f"{HERE}/p1_receipt.json") as f:
        p1 = json.load(f)
    comp = {}
    for model, row in p1["panel"].items():
        comp[model] = {v: {"C1": row[v]["C1"], "C1_p": row[v]["C1_p"],
                           "S1": row[v]["S1"], "S1_p": row[v]["S1_p"],
                           "T1": row[v]["T1"]}
                       for v in ("oporder", "rolecode") if v in row}
    receipt["embedding_comparator"] = comp
except FileNotFoundError:
    receipt["notes"].append("p1_receipt.json not found; comparator omitted")

# verdict arithmetic (registered bars; L1 as corrected liveness gate)
verdict = {}
for enc in ("oporder", "rolecode"):
    R = receipt["encodings"][enc]
    liveness = [i for i in INSTRUMENTS if R[i]["L1_cross_cell"]["p"] < 0.05]
    c1cell = [i for i in INSTRUMENTS if all(r == 1 for r in R[i]["c1_cell"]["ranks"])]
    c1trace = [i for i in INSTRUMENTS
               if R[i]["c1_trace"]["p"] < 0.05 and R[i]["c1_trace"]["value"] > 0]
    both = [i for i in INSTRUMENTS if i in c1cell and i in c1trace]
    verdict[enc] = {"liveness_L1_ge3": len(liveness) >= 3, "liveness_L1": liveness,
                    "c1_cell_rank1_all_scheds": c1cell, "c1_trace_p05": c1trace,
                    "dialect_ge3_both": len(both) >= 3, "both": both}
receipt["verdict"] = verdict
with open(f"{HERE}/p2_receipt.json", "w") as f:
    json.dump(receipt, f, indent=1)
print(json.dumps(verdict, indent=1))
print("receipt written")
