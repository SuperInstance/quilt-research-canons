#!/usr/bin/env python3
"""Wave-69 P1 — schedule-varying trace-gram rerun (lane 69-c).

PRE-REGISTERED in README.md (same dir) BEFORE any embedding call:
  P1-a identity schedule-invariant (T1-F > 0, 5/5, outside label-shuffle null)
  P1-b schedule blindness (S1 inside schedule-shuffle null, >=4/5, full+rfull)
  P1-c order-twin collapse (mean cos(doc, order-twin) >= 0.99 per embedder)
  P1-d dialect stays dead on non-degenerate corpus (C1-F, C1-O inside null, 5/5)
  P1-e TF histograms separate variants, order-twins exactly 1.0
  NC-1 doc-label-shuffle nulls (500 perms) for T1 and C1
  NC-2 batch-noise floor, 20x margin on every claimed gap
Kill criteria: see README.md. No post-hoc repairs.

AMEND-3 (pre-judgment, documented in README DEVIATIONS): the first-coded
NC-1/NC-1' nulls permuted labels by a BIJECTION OF THE LABEL SET, which is a
no-op null (label equality is invariant under relabeling; every null draw
equaled the real statistic, producing z ~= 1.0 artifacts). Fixed to TRUE
doc-level label shuffles before any claim was judged. A duplicate-aware
T1_uniq diagnostic (unique full docs only) was added at the same time.

role_of: field-role tokens from cell-word anatomy (wave-67): route->ROUTING,
quf->FILTER, time/world->PROJECTION, crdt->STATE, proof->VERIFY, engine->ITERATOR.
"""
import json
import os
import random
import re
import subprocess
import time
import urllib.request
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = f"{HERE}/trace_gram_sched"
DI = os.environ["DEEPINFRA_TOKEN"]

PANEL = ["Qwen/Qwen3-Embedding-8B", "Qwen/Qwen3-Embedding-0.6B", "BAAI/bge-m3",
         "intfloat/multilingual-e5-large-instruct", "sentence-transformers/all-mpnet-base-v2"]
CELLS = ["route", "crdt", "time", "quf", "world", "proof", "engine"]
BETWEEN = ("route", "quf", "time")
INCELL = ("crdt", "proof", "world")
ROLE = {"route": "ROUTING", "quf": "FILTER", "time": "PROJECTION", "world": "PROJECTION",
        "crdt": "STATE", "proof": "VERIFY", "engine": "ITERATOR"}
SEEDS = list(range(101, 111))
SCHEDS = ["A", "B", "C", "D"]
N_PERM = 500
RECEIPT_PATH = f"{HERE}/p1_receipt.json"

# ── 1. corpus ───────────────────────────────────────────────────────────
t0 = time.time()
traces = {}
for cell in CELLS:
    for seed in SEEDS:
        for sched in SCHEDS:
            for reseed in (0, 1):
                out = subprocess.run([BIN, cell, str(seed), sched] + (["reseed"] if reseed else []),
                                     capture_output=True, text=True, timeout=30)
                traces[(cell, seed, sched, reseed)] = [json.loads(l) for l in out.stdout.splitlines() if l.strip()]
print(f"corpus: {len(traces)} runs in {time.time()-t0:.0f}s; "
      f"steps/run {min(len(v) for v in traces.values())}..{max(len(v) for v in traces.values())}")

# construction receipt: payload/op multiset provably schedule-invariant
invar_viol = []
for cell in CELLS:
    for seed in SEEDS:
        ref = Counter((s["op"], s["call"], s["args"], s["state"]) for s in traces[(cell, seed, "A", 0)])
        for sched in SCHEDS:
            run = Counter((s["op"], s["call"], s["args"], s["state"]) for s in traces[(cell, seed, sched, 0)])
            if ref != run:
                invar_viol.append(f"{cell}:{seed}:{sched}")
print(f"multiset schedule-invariance: {'OK (0 violations)' if not invar_viol else 'VIOLATED ' + str(invar_viol[:5])}")

# ── 2. docs ─────────────────────────────────────────────────────────────
docs = {}
for cell in CELLS:
    for seed in SEEDS:
        for sched in SCHEDS:
            st = traces[(cell, seed, sched, 0)]
            docs[f"full:{cell}:{seed}:{sched}"] = " | ".join(
                f"{s['op']} {s['call']}({s['args']}) -> {s['state']}" for s in st)
            docs[f"opsonly:{cell}:{seed}:{sched}"] = " | ".join(f"{s['op']} {cell}" for s in st)
            docs[f"oporder:{cell}:{seed}:{sched}"] = " ".join(s["op"] for s in st)
            docs[f"rolecode:{cell}:{seed}:{sched}"] = " ".join(f"{s['op']}:{ROLE[cell]}" for s in st)
        stA = traces[(cell, seed, "A", 0)]
        docs[f"statesonly:{cell}:{seed}:A"] = " | ".join(f"{s['args']} -> {s['state']}" for s in stA if s["state"])
        for sched in ("A", "B"):
            st = traces[(cell, seed, sched, 1)]
            docs[f"rfull:{cell}:{seed}:{sched}"] = " | ".join(
                f"{s['op']} {s['call']}({s['args']}) -> {s['state']}" for s in st)
            docs[f"roporder:{cell}:{seed}:{sched}"] = " ".join(s["op"] for s in st)
rng69 = random.Random(69)
for cell in CELLS:
    for seed in SEEDS:
        st = traces[(cell, seed, "A", 0)][:]
        rng69.shuffle(st)
        docs[f"shuf:{cell}:{seed}:A"] = " | ".join(
            f"{s['op']} {s['call']}({s['args']}) -> {s['state']}" for s in st)
print(f"docs: {len(docs)}")

# degeneracy census (pre-run amendment): unique doc texts per (cell, 4 scheds)
census = {}
for cell in CELLS:
    for variant in ("full", "opsonly", "oporder", "rolecode"):
        census[f"{variant}:{cell}"] = len({docs[f"{variant}:{cell}:{s}:{ch}"] for s in SEEDS for ch in SCHEDS})
print("unique-text census per (cell, 4 scheds; max 40):",
      {v: sorted({census[f"{v}:{c}"] for c in CELLS}) for v in ("full", "opsonly", "oporder", "rolecode")})

keys = list(docs)
def parts(k):
    variant, cell, seed, sched = k.split(":")
    return variant, cell, int(seed), sched
VAR = {k: parts(k)[0] for k in keys}
CELLK = {k: parts(k)[1] for k in keys}
SCHEDK = {k: parts(k)[3] for k in keys}

# ── 3. embeddings ───────────────────────────────────────────────────────
def embed(model, texts, batch=64):
    out = []
    for i in range(0, len(texts), batch):
        for attempt in range(4):
            try:
                req = urllib.request.Request(
                    "https://api.deepinfra.com/v1/openai/embeddings",
                    data=json.dumps({"model": model, "input": texts[i:i + batch]}).encode(),
                    headers={"Authorization": f"Bearer {DI}", "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=180) as r:
                    data = json.loads(r.read())["data"]
                out.extend(d["embedding"] for d in sorted(data, key=lambda x: x["index"]))
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
    return np.array(out, dtype=np.float32)

dup_idx = list(range(0, len(keys), max(1, len(keys) // 40)))[:40]
dup_keys = [keys[i] for i in dup_idx]
emb_store = {}
DRY = os.environ.get("P1_DRYRUN") == "1"
CACHE = f"{HERE}/emb_cache"
os.makedirs(CACHE, exist_ok=True)
for model in ([] if DRY else PANEL):
    csafe = model.replace("/", "_")
    if os.path.exists(f"{CACHE}/{csafe}.npz"):
        z = np.load(f"{CACHE}/{csafe}.npz")
        emb_store[model] = {"V": z["V"], "noise": json.loads(str(z["noise"]))}
        print(f"{model}: cache hit", flush=True)
        continue
    t0 = time.time()
    V = embed(model, [docs[k] for k in keys])
    V = V / (np.linalg.norm(V, axis=1, keepdims=True) + 1e-12)
    # NC-2: re-embed dup subset with different batch grouping
    V2 = embed(model, [docs[k] for k in dup_keys], batch=7)
    V2 = V2 / (np.linalg.norm(V2, axis=1, keepdims=True) + 1e-12)
    idx = {k: i for i, k in enumerate(keys)}
    self1 = np.array([float(V[idx[k]] @ V2[j]) for j, k in enumerate(dup_keys)])
    noise = {"eps_mean": float(1 - self1.mean()), "eps_p99": float(np.percentile(1 - self1, 99))}
    emb_store[model] = {"V": V, "noise": noise}
    np.savez_compressed(f"{CACHE}/{csafe}.npz", V=V, noise=json.dumps(noise))
    print(f"{model}: embedded {len(keys)} docs ({time.time()-t0:.0f}s), batch-noise eps={noise['eps_mean']:.5f}", flush=True)

# ── 4. metrics ──────────────────────────────────────────────────────────
def pair_masks(ks, labfn):
    n = len(ks)
    same_cell = np.zeros((n, n), bool)
    same_sched = np.zeros((n, n), bool)
    diff_seed = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            ci, si, di = CELLK[ks[i]], SCHEDK[ks[i]], parts(ks[i])[2]
            cj, sj, dj = CELLK[ks[j]], SCHEDK[ks[j]], parts(ks[j])[2]
            same_cell[i, j] = ci == cj
            same_sched[i, j] = si == sj
            diff_seed[i, j] = di != dj
    return same_cell, same_sched, diff_seed

def t1_c1_from_matrix(C, ks, cell_lab):
    """T1 = same-cell - between-cell. C1 = same-cell-pairs in BETWEEN - in INCELL.
    cell_lab: dict doc->cell (permutable for nulls)."""
    n = len(ks)
    r, c = np.triu_indices(n, 1)
    labs = np.array([cell_lab[k] for k in ks])
    lr, lc = labs[r], labs[c]
    same = lr == lc
    cos = C[r, c]
    t1 = float(cos[same].mean() - cos[~same].mean())
    # same-cell pairs whose (shared) cell is in BETWEEN / INCELL
    m_bet = same & np.isin(lr, list(BETWEEN))
    m_inc = same & np.isin(lr, list(INCELL))
    c1 = float(cos[m_bet].mean() - cos[m_inc].mean())
    return t1, c1, float(cos[same].mean()), float(cos[~same].mean())

def shuffle_null(C, ks, metric, n_perm=N_PERM, seed=691):
    """NC-1, AMEND-3 (pre-judgment fix): DOC-level label shuffle — permute the
    label VECTOR across docs, breaking cell-doc association while keeping label
    counts. The previously coded label-set bijection is a no-op null (equality
    of labels is invariant under any bijection of the label set), so every
    'null' draw equaled the real statistic; discovered during corpus triage
    BEFORE judging any claim, documented in README DEVIATIONS."""
    rng = np.random.default_rng(seed)
    labs0 = np.array([CELLK[k] for k in ks])
    vals = []
    for _ in range(n_perm):
        lab = dict(zip(ks, labs0[rng.permutation(len(ks))]))
        vals.append(t1_c1_from_matrix(C, ks, lab)[0 if metric == "T1" else 1])
    return np.array(vals)

def sched_null(C, ks, n_perm=N_PERM, seed=692):
    """Null for S1, AMEND-3: DOC-level schedule-label shuffle (same fix)."""
    rng = np.random.default_rng(seed)
    labs0 = np.array([SCHEDK[k] for k in ks])
    vals = []
    for _ in range(n_perm):
        sl = dict(zip(ks, labs0[rng.permutation(len(ks))]))
        vals.append(s1_from_matrix(C, ks, sl))
    return np.array(vals)

def s1_from_matrix(C, ks, sched_lab):
    n = len(ks)
    tri = np.triu_indices(n, 1)
    cl = np.array([CELLK[k] for k in ks])
    sl = np.array([sched_lab[k] for k in ks])
    same_cell = cl[:, None] == cl[None, :]
    same_sched = sl[:, None] == sl[None, :]
    M = same_cell[tri] & same_sched[tri]
    X = same_cell[tri] & ~same_sched[tri]
    cos = C[tri]
    return float(cos[M].mean() - cos[X].mean())

def order_twin_stats(model, variant):
    ks = [k for k in keys if VAR[k] == variant]
    V = emb_store[model]["V"]
    idx = {k: i for i, k in enumerate(keys)}
    vals = []
    for cell in CELLS:
        for seed in SEEDS:
            a, b = f"{variant}:{cell}:{seed}:A", f"{variant}:{cell}:{seed}:B"
            if a in idx and b in idx:
                vals.append(float(V[idx[a]] @ V[idx[b]]))
    return float(np.mean(vals)), float(np.min(vals))

# text-level order-twin check (exact multiset identity already receipted above)
receipt = {"pre_registered": "README.md (before any call)", "n_docs": len(docs),
           "multiset_invariance_ok": not invar_viol, "census_unique_per_cell": census,
           "panel": {}, "tf": {}}

for model in ([] if DRY else PANEL):
    V = emb_store[model]["V"]
    C_full_cache = {}

    def C_for(prefix):
        if prefix not in C_full_cache:
            ks = [k for k in keys if VAR[k] == prefix]
            C_full_cache[prefix] = (ks, V[[keys.index(k) for k in ks]] @
                                            V[[keys.index(k) for k in ks]].T)
        return C_full_cache[prefix]

    row = {}
    for prefix in ("full", "opsonly", "oporder", "rolecode", "rfull"):
        ks, C = C_for(prefix)
        t1, c1, w, b = t1_c1_from_matrix(C, ks, CELLK)
        nullT = shuffle_null(C, ks, "T1")
        nullC = shuffle_null(C, ks, "C1")
        zT = (t1 - nullT.mean()) / (nullT.std() + 1e-12)
        zC = (c1 - nullC.mean()) / (nullC.std() + 1e-12)
        pC = float((np.sum(nullC >= c1) + 1) / (len(nullC) + 1))
        s1 = s1_from_matrix(C, ks, SCHEDK)
        nullS = sched_null(C, ks)
        pS = float((np.sum(nullS >= s1) + 1) / (len(nullS) + 1))
        # AMEND-3 diagnostic: duplicate-aware S1 on UNIQUE docs of this prefix
        seen, urep = set(), []
        for k in ks:
            t = docs[k]
            if t not in seen:
                seen.add(t)
                urep.append(k)
        Vu = V[[keys.index(k) for k in urep]]
        Cu = Vu @ Vu.T
        s1u = s1_from_matrix(Cu, urep, SCHEDK)
        nullSu = sched_null(Cu, urep)
        pSu = float((np.sum(nullSu >= s1u) + 1) / (len(nullSu) + 1))
        t1u, _, _, _ = t1_c1_from_matrix(Cu, urep, CELLK)
        nullTu = shuffle_null(Cu, urep, "T1")
        pTu = float((np.sum(nullTu >= t1u) + 1) / (len(nullTu) + 1))
        row[prefix] = {"T1": t1, "T1_z": float(zT), "T1_p": float((np.sum(nullT >= t1) + 1) / (len(nullT) + 1)),
                       "T1_null_mean": float(nullT.mean()), "T1_null_sd": float(nullT.std()),
                       "C1": c1, "C1_z": float(zC), "C1_p": pC,
                       "C1_null_mean": float(nullC.mean()), "C1_null_sd": float(nullC.std()),
                       "within": w, "between": b,
                       "S1": s1, "S1_p": pS, "S1_null_mean": float(nullS.mean()),
                       "S1_null_sd": float(nullS.std()),
                       "S1_uniq": s1u, "S1_uniq_p": pSu, "S1_uniq_null_sd": float(nullSu.std()),
                       "T1_uniq": t1u, "T1_uniq_p": pTu,
                       "n_unique_docs": len(urep),
                       "noise": emb_store[model]["noise"]}
        if prefix == "full":
            ks2, C2 = C_for("shuf")
            t1s, _, _, _ = t1_c1_from_matrix(C2, ks2, CELLK)
            row["T1_shuf"] = float(t1s)
    row["order_twin_full_AB"], _ = order_twin_stats(model, "full")
    row["order_twin_oporder_AB"], _ = order_twin_stats(model, "oporder")
    receipt["panel"][model] = row
    print(f"{model}:\n" + "\n".join(
        f"  {p}: T1 {row[p]['T1']:+.4f} (z {row[p]['T1_z']:+.1f}) | C1 {row[p]['C1']:+.4f} (p {row[p]['C1_p']:.3f}) | "
        f"S1 {row[p]['S1']:+.4f} (p {row[p]['S1_p']:.3f})" for p in ("full", "opsonly", "oporder", "rfull")) +
        f"\n  order-twin cos: full {row['order_twin_full_AB']:.4f} oporder {row['order_twin_oporder_AB']:.4f} | T1_shuf {row['T1_shuf']:+.4f}")

# ── 5. TF instrument (P1-e) ─────────────────────────────────────────────
def tf_vec(text):
    return Counter(re.findall(r"[a-zA-Z_0-9=.:%]+", text))

tf_keys = [k for k in keys if VAR[k] in ("full", "opsonly", "oporder", "statesonly", "rolecode") and SCHEDK[k] == "A"]
vecs = {k: tf_vec(docs[k]) for k in tf_keys}
vocab = sorted({t for v in vecs.values() for t in v})
M = np.zeros((len(tf_keys), len(vocab)))
for i, k in enumerate(tf_keys):
    for t, c in vecs[k].items():
        M[i, vocab.index(t)] = c
M = np.log1p(M)
df = (M > 0).sum(axis=0)
M = M * np.log((1 + len(tf_keys)) / (1 + df) + 1)
M = M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-12)
Ctf = M @ M.T
idx_tf = {k: i for i, k in enumerate(tf_keys)}
variants = ["full", "opsonly", "oporder", "statesonly", "rolecode"]
vmat = {}
for v1 in variants:
    for v2 in variants:
        vals = [float(Ctf[idx_tf[f"{v1}:{c}:{s}:A"], idx_tf[f"{v2}:{c}:{s}:A"]])
                for c in CELLS for s in SEEDS if f"{v2}:{c}:{s}:A" in idx_tf]
        vmat[f"{v1}|{v2}"] = float(np.mean(vals))
# TF C1/T1 on full docs (comparability with r3b)
ksf = [k for k in tf_keys if VAR[k] == "full"]
Ctf_full = Ctf[[idx_tf[k] for k in ksf]][:, [idx_tf[k] for k in ksf]]
t1tf, c1tf, wtf, btf = t1_c1_from_matrix(Ctf_full, ksf, CELLK)
# P1-e operationalized (pre-run amendment, BEFORE run): TF order-twin = full-A
# vs full-B in unigram-TF space. Same token multiset by the construction
# receipt above, so cos must be EXACTLY 1.0 if the histogram is order-blind.
tf_keys_B = [k for k in keys if VAR[k] == "full" and SCHEDK[k] == "B"]
all_tf = tf_keys + tf_keys_B
vecs_B = {k: tf_vec(docs[k]) for k in tf_keys_B}
vocab2 = sorted({t for v in list(vecs.values()) + list(vecs_B.values()) for t in v})
M2 = np.zeros((len(all_tf), len(vocab2)))
vi2 = {t: i for i, t in enumerate(vocab2)}
for i, k in enumerate(all_tf):
    for t, c in (vecs[k] if k in vecs else vecs_B[k]).items():
        M2[i, vi2[t]] = c
M2 = np.log1p(M2)
df2 = (M2 > 0).sum(axis=0)
M2 = M2 * np.log((1 + len(all_tf)) / (1 + df2) + 1)
M2 = M2 / (np.linalg.norm(M2, axis=1, keepdims=True) + 1e-12)
Ctf2 = M2 @ M2.T
idxF = {k: i for i, k in enumerate(all_tf)}
twins = [float(Ctf2[idxF[f"full:{c}:{s}:A"], idxF[f"full:{c}:{s}:B"]]) for c in CELLS for s in SEEDS]
receipt["tf"] = {"variant_matrix_mean_cos": vmat, "T1_full": t1tf, "C1_full": c1tf,
                 "within": wtf, "between": btf,
                 "order_twin_fullAB_mean": float(np.mean(twins)),
                 "order_twin_fullAB_min": float(np.min(twins))}
print(f"TF: T1 {t1tf:+.4f} C1 {c1tf:+.4f} | full|full {vmat['full|full']:.4f} "
      f"full|opsonly {vmat['full|opsonly']:.4f} full|oporder {vmat['full|oporder']:.4f} "
      f"full|statesonly {vmat['full|statesonly']:.4f} | order-twin A|B min {min(twins):.6f}")

with open(RECEIPT_PATH, "w") as f:
    json.dump(receipt, f, indent=1)
print("receipt written:", RECEIPT_PATH)
