#!/usr/bin/env python3
"""loop2 — the same discipline, pointed at OTHER agents' work.

Everything in loop.py was applied to my own artifacts. That is a second reader in a
second language, which is better than nothing and is still not external. This loop
applies the same rules to the work of keeper, Claude and CCC — which is the first time
the fleet's instruments point outward at all.

Same three properties, and the reason for them is unchanged:
  PRE-REGISTER with numbers, so a round can be wrong
  DEBRIEF each prediction as CONFIRMED / REFUTED / INCONCLUSIVE
  CARRY the refutations into the next round's design
"""
import json, os, sys, urllib.request
from datetime import datetime, timezone

KEY = os.environ.get("GITHUB_TOKEN")
H = {'Authorization': f'Bearer {KEY}', 'Accept': 'application/vnd.github+json', 'User-Agent': 'mavis-scout'}
API = 'https://api.github.com/repos/SuperInstance'
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'loop2_state.json')

def gh(path):
    try:
        req = urllib.request.Request(f'https://api.github.com{path}', headers=H)
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'__err': str(e)[:80]}

def raw(repo, path, ref='main'):
    for b in (ref, 'main', 'master'):
        try:
            req = urllib.request.Request(f'https://raw.githubusercontent.com/SuperInstance/{repo}/{b}/{path}',
                                         headers={'User-Agent': 'mavis-scout'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception:
            continue
    return None

def load():
    return json.load(open(STATE)) if os.path.exists(STATE) else {'rounds': [], 'carried': []}
def save(s): json.dump(s, open(STATE, 'w'), indent=2)

def pr(round_no, title, predictions):
    s = load()
    rnd = {'round': round_no, 'title': title,
           'registered_at': datetime.now(timezone.utc).isoformat(),
           'predictions': predictions, 'debrief': None}
    s['rounds'].append(rnd); save(s); return rnd

def debrief(round_no):
    s = load()
    rnd = next(r for r in s['rounds'] if r['round'] == round_no)
    out = []
    for p in rnd['predictions']:
        pred, act = p['predict'], p['result']
        kind = p.get('kind') or ('bool' if isinstance(pred, bool) else 'num')
        if act is None:
            out.append({'id': p['id'], 'status': 'INCONCLUSIVE', 'predicted': pred}); continue
        if kind == 'bool':
            want = pred if isinstance(pred, bool) else bool(pred)
            st = 'CONFIRMED' if act == want else 'REFUTED'
        else:
            tol = p.get('tolerance', 0.10)
            st = 'CONFIRMED' if isinstance(act, (int, float)) and abs(act - pred) <= tol else 'REFUTED'
        out.append({'id': p['id'], 'kind': kind, 'predicted': pred, 'actual': act, 'status': st})
    rnd['debrief'] = out
    for v in out:
        if v['status'] == 'REFUTED':
            s['carried'].append({'from_round': round_no, 'id': v['id'],
                                 'predicted': v['predicted'], 'actual': v['actual'],
                                 'note': 'my belief about THEIR work was wrong'})
    save(s); return out

def show(n):
    s = load()
    r = next(x for x in s['rounds'] if x['round'] == n)
    print(f"ROUND {n}: {r['title']}")
    print('=' * 84)
    if r['debrief']:
        for v in r['debrief']:
            m = {'CONFIRMED': '+', 'REFUTED': 'X', 'INCONCLUSIVE': '?'}[v['status']]
            print(f"  [{m}] {v['id']:40} {v['status']:12} pred={v.get('predicted')} act={v.get('actual')}")
        c = sum(1 for v in r['debrief'] if v['status'] == 'CONFIRMED')
        x = sum(1 for v in r['debrief'] if v['status'] == 'REFUTED')
        print(f"  -> {c} confirmed, {x} refuted")
    else:
        for p in r['predictions']:
            print(f"  [ ] {p['id']:40} predicts {p['predict']}")
    if s['carried']:
        print("\n  CARRIED FORWARD:")
        for c in s['carried']:
            print(f"    - r{c['from_round']}/{c['id']}: predicted {c['predicted']}, was {c['actual']}")
