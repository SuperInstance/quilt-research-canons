#!/usr/bin/env python3
"""Receipt: plato-mythos' _stats.json REPRODUCES from the committed dataset
(all 37 domain entries match, 0 mismatches) — but 12 domain names are
duplicated by case, so "unique domains: 37" is 25 once case-folded.

    python3 plato_mythos_stats_check.py /path/to/plato-mythos
"""
import json, collections, statistics, sys, os
REPO = sys.argv[1] if len(sys.argv) > 1 else "."
rows = [json.loads(l) for l in open(os.path.join(REPO, "data/tiles.jsonl")) if l.strip()]
st = json.load(open(os.path.join(REPO, "data/_stats.json")))
doms = collections.Counter(r.get("domain", "") for r in rows)
conf = [r["confidence"] for r in rows if isinstance(r.get("confidence"), (int, float))]
print(f"lines                    {len(rows)}      claimed total_output={st['total_output']}")
print(f"distinct domain strings  {len(doms)}       claimed unique domains=37")
print(f"tiles with confidence    {len(conf)}      claimed 396")
print(f"mean confidence          {statistics.mean(conf):.4f}    claimed 0.52")
mism = [(k, c, doms.get(k, 0)) for k, c in st["domains"].items() if doms.get(k, 0) != c]
print(f"_stats.json domains      {len(st['domains'])} entries, {len(mism)} mismatching")
fold = collections.Counter()
for d, c in doms.items(): fold[d.lower()] += c
print(f"case-folded unique domains {len(fold)}   <-- the real breadth")
for k in sorted(fold):
    v = {d: doms[d] for d in doms if d.lower() == k}
    if len(v) > 1: print(f"   '{k}': {v}")
