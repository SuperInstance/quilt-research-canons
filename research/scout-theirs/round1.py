"""ROUND 1 (pointed outward) — who is actually producing, and can a stranger tell?

PRE-REGISTERED. My predictions about THEIR work, written before measuring, so the round
can be wrong about them.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/scout-theirs')
from loop2 import pr, debrief, show, gh, load, save

pr(1, "who is producing, and can a stranger bind a commit to an author", [
  {"id": "unauth-share-high", "kind": "num", "predict": 0.5, "tolerance": 0.25,
   "claim": "Across the 8 live repos, MORE THAN HALF of the recent commits have no "
            "GitHub-authenticated login attached, because the fleet writes with a PAT. "
            "That is the 791-commits-0-signed problem, visible per-repo.",
   "result": None},
  {"id": "distinct-authors-wide", "kind": "num", "predict": 6.0, "tolerance": 3.0,
   "claim": "There are at least SIX distinct self-asserted author names across the live "
            "repos — not five, and not one. Fragmentation, not identity.",
   "result": None},
  {"id": "signed-still-zero", "kind": "num", "predict": 0.0, "tolerance": 0.0,
   "claim": "ZERO of the recent commits carry a cryptographic signature. The key was "
            "published at 15:08Z today; whether anyone has adopted it is the question.",
   "result": None},
  {"id": "keeper-not-blocked", "kind": "bool", "predict": True,
   "claim": "fleet-seeds (the keeper) is still committing, i.e. the pool-driver hangs that "
            "block Taps do NOT block the keeper loop. The two agents fail differently.",
   "result": None},
  {"id": "claude-mostly-ai-writings", "kind": "bool", "predict": True,
   "claim": "Claude's recent commits are concentrated in AI-Writings and Syzygy, i.e. the "
            "prose/corpus lanes rather than the substrate lanes.",
   "result": None},
])

REPOS = ['fleet-seeds','quilt-gpu-lab','quilt-jepa','AI-Writings','MicroMoth-quilt',
         'Syzygy','chiaroscuro','quilt']
all_auth_logins, all_names, total, signed, per = [], set(), 0, 0, {}
for repo in REPOS:
    c = gh(f'/repos/SuperInstance/{repo}/commits?per_page=15')
    if isinstance(c, dict): continue
    names, logins, s = {}, {}, 0
    for x in c:
        names[(x['commit'].get('author') or {}).get('name','?')] = 1
        lg = (x.get('author') or {}).get('login')
        logins[lg or '?'] = logins.get(lg or '?', 0) + 1
        if (x.get('verification') or {}).get('verified'): s += 1
    per[repo] = {'names': sorted(names), 'logins': logins, 'signed': s, 'newest': c[0]['commit']['committer']['date'] if c else None}
    all_names |= set(names)
    all_auth_logins += [k for k in logins if k != '?']
    signed += s; total += len(c)

unauth = sum(1 for r in per.values() for k, v in r['logins'].items() if k == '?')
print(f"  commits scanned: {total}   signed: {signed}")
print(f"  unauthenticated (no GH login): {unauth}  ({unauth/total:.2f})")
print(f"  distinct self-asserted names: {len(all_names)} -> {sorted(all_names)}")
print()
for r, d in per.items():
    print(f"  {r:20} signed={d['signed']:>2}  newest={str(d['newest'])[:16]}  logins={d['logins']}")

keeper_moving = per.get('fleet-seeds', {}).get('newest') is not None
claude_conc = per.get('AI-Writings', {}).get('logins', {}).get('claude', 0) + per.get('Syzygy', {}).get('logins', {}).get('claude', 0)

s = load(); rnd = s['rounds'][-1]
rnd['predictions'][0]['result'] = round(unauth/total, 3)
rnd['predictions'][1]['result'] = float(len(all_names))
rnd['predictions'][2]['result'] = float(signed)
rnd['predictions'][3]['result'] = bool(keeper_moving)
rnd['predictions'][4]['result'] = bool(claude_conc > 0 and all(
    'claude' not in per.get(r, {}).get('logins', {}) for r in ('fleet-seeds','quilt-gpu-lab')))
rnd['data'] = {'per_repo': per, 'total': total, 'signed': signed, 'unauth': unauth,
               'distinct_names': sorted(all_names), 'claude_writings_syzygy': claude_conc}
save(s)
print()
debrief(1); show(1)
