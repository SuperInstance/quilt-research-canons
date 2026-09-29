"""ROUND 2 (pointed outward) — does keeper's own lode survive the gate I wrote?

My instrument, their claims. The first real outward test of either.

PRE-REGISTERED, and two of the four were wrong.
"""
import sys, json, subprocess
sys.path.insert(0, '/workspace/research/lanes/scout-theirs')
from loop2 import pr, debrief, show, raw, load, save

pr(2, "does keeper's own lode survive the externalisability gate I wrote", [
  {"id": "brier-null", "kind": "bool", "predict": True,
   "claim": "Every resolved entry in keeper's registry.jsonl has brier: null, meaning the "
            "calibration is RECORDED but never SCORED. The fleet predicts at p and records "
            "the outcome, and never computes the number that would tell it whether the "
            "prediction was any good.",
   "result": None},
  {"id": "honest-fail-present", "kind": "bool", "predict": True,
   "claim": "The registry contains at least one FAIL verdict carried forward, i.e. keeper "
            "is keeping losing runs rather than only wins.",
   "result": None},
  {"id": "mines-still-undeciable", "kind": "num", "predict": 0.0, "tolerance": 0.2,
   "claim": "Applying my own externalisability gate to keeper's CURRENT mines will still "
            "return ~0 externally decidable. Six hours of new work has not changed the shape.",
   "result": None},
  {"id": "pong49-folds", "kind": "bool", "predict": True,
   "claim": "PONG49-BATTERY will still read ARMED in the registry — the outcome resolved "
            "earlier today has not been folded in by the keeper.",
   "result": None},
])

import glob
cands = glob.glob('/workspace/research/**/lode_externalisability.mjs', recursive=True)
gate = cands[0] if cands else None
if not gate:
    src = raw('fleet-seeds', 'scripts/lode_externalisability.mjs', ref='mavis/externalisability-gate')
    if src:
        open('/tmp/lode_ext.mjs', 'w').write(src)
        gate = '/tmp/lode_ext.mjs'

reg = [json.loads(l) for l in raw('fleet-seeds', 'lode/registry.jsonl').split('\n') if l.strip()]
nulls = sum(1 for r in reg if r.get('brier') is None)
scored = [r for r in reg if r.get('brier') is not None]
fails = [r for r in reg if r.get('verdict') == 'FAIL']
armed = any('PONG49' in str(r.get('set_id', '')) and r.get('verdict') == 'ARMED' for r in reg)

open('/tmp/keeper_mines.jsonl', 'w').write(raw('fleet-seeds', 'lode/mines.jsonl'))
ext = None
if gate:
    p = subprocess.run(['node', gate, '/tmp/keeper_mines.jsonl'], capture_output=True, text=True)
    import re
    m = re.search(r'externally decidable:\s*(\d+)', p.stdout)
    if m: ext = int(m.group(1))

s = load(); rnd = s['rounds'][-1]
rnd['predictions'][0]['result'] = (nulls == len(reg) and len(reg) > 0)
rnd['predictions'][1]['result'] = bool(fails)
rnd['predictions'][2]['result'] = float(ext if ext is not None else -1.0)
rnd['predictions'][3]['result'] = armed
rnd['data'] = {'registry': len(reg), 'brier_null': nulls,
               'brier_scored': [(r['set_id'], r['brier']) for r in scored],
               'fails': [f.get('set_id') for f in fails],
               'externally_decidable': ext, 'pong49_armed': armed}
save(s)
debrief(2); show(2)
