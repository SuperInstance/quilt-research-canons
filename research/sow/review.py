#!/usr/bin/env python3
"""
review.py — read the traces and find the pattern.

The traces accumulate one row per (seed, model, round). The point is not any single
row. The point is what the COLUMN of rows says about the small models: which
approaches they reach for, which step they consistently miss, and whether the
instruments agree.

This is where the supervision actually becomes usable. A SALVAGE that says "missing:
the working directory" three times across two models is a training signal. A single
SALVAGE is an anecdote.
"""
import json, os, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TRACES = os.path.join(HERE, "traces.jsonl")

def load():
    if not os.path.exists(TRACES): return []
    return [json.loads(l) for l in open(TRACES) if l.strip()]

def main():
    rows = load()
    if not rows:
        print("no traces yet — run `python3 round.py` first"); return 0
    print(f"  {len(rows)} traces")
    print()
    print("  verdict distribution")
    for v, c in Counter(r['verdict'] for r in rows).most_common():
        print(f"    {v:10} {c:>3}  {'#'*c}")
    print()
    print("  judge unanimity (the judge is a SAMPLE, not a verdict)")
    unan = sum(1 for r in rows if r.get('judge_unanimous'))
    print(f"    unanimous: {unan}/{len(rows)}")
    for r in rows:
        if not r.get('judge_unanimous'):
            print(f"      {r['seed_id']}: {r['verdicts']}")
    print()
    print("  JEV vs judge agreement")
    ag = sum(1 for r in rows if r.get('agree'))
    print(f"    agree: {ag}/{len(rows)}")
    for r in rows:
        if not r.get('agree'):
            print(f"      {r['seed_id']:28} jev={r['jev_acceptability']:.2f} judge={r['verdict']}")
    print()
    ps = [r['jev_acceptability'] for r in rows if isinstance(r.get('jev_acceptability'), (int,float))]
    if ps:
        print(f"  JEV acceptability: min={min(ps):.2f} max={max(ps):.2f} mean={sum(ps)/len(ps):.2f}")
    print()
    print("  the recurring MISSING step (this is the training signal)")
    by = defaultdict(list)
    for r in rows:
        if r.get('missing') and r['missing'] != 'NONE':
            by[r['seed_id']].append(r['missing'][:70])
    for seed, ms in by.items():
        print(f"    {seed}:")
        for m, c in Counter(ms).most_common():
            print(f"      {c}x  {m}")
    print()
    print("  per-model draft length (a proxy for how much the model is actually thinking)")
    for m, c in Counter(r['model'].split('/')[-1] for r in rows).most_common():
        lens = [len(r['draft']) for r in rows if r['model'].split('/')[-1] == m]
        print(f"    {m:28} n={c}  mean draft {sum(lens)//len(lens)} chars")
    return 0

if __name__ == "__main__":
    sys.exit(main())
