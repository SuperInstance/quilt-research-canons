import sys, json, os
sys.path.insert(0, '/workspace/fleet-legend')
from legibility.complete import (from_github, file_head, FORBIDDEN,
    draft_limitations, draft_failures, draft_receipt, render)
import re

def evidence_from_api(repo, files):
    ev = []
    ci = [f for f in files if f.startswith(('.github/workflows/', '.gitlab-ci')) or f == 'Jenkinsfile']
    ev.append((f"there is {len(ci)} CI workflow file(s) here" if ci else
               "there is no CI configuration in this repository, so nothing here is checked automatically on push",
               ci[0] if ci else "(no CI config found)", 'positive' if ci else 'negative'))
    tests = [f for f in files if re.search(r"(^|/)(test|tests|spec)/|_test\.|test_|\.test\.|\.spec\.", f, re.I)]
    ev.append((f"it ships {len(tests)} test file(s)" if tests else
               "it ships no automated tests, so the example command is the only check available",
               tests[0] if tests else "(no test files found)", 'positive' if tests else 'negative'))
    lic = [f for f in files if re.match(r'^(LICENSE|COPYING)', f, re.I)]
    ev.append(("it carries a LICENSE" if lic else "it carries no LICENSE file",
               lic[0] if lic else "(no LICENSE file)", 'positive' if lic else 'negative'))
    ci_like = [f for f in files if f == 'Makefile' or f == 'justfile' or f in ('package.json','pyproject.toml','Cargo.toml','go.mod')]
    ev.append((f"its canonical command is defined in `{ci_like[0]}`" if ci_like else
               "no standard build or test file is present, so there is no canonical command to point a reader at",
               ci_like[0] if ci_like else "(no build file found)", 'positive' if ci_like else 'negative'))
    return ev

targets = [r['name'] for r in json.load(open('/workspace/fleet-legend/verdicts.json'))
           if r['v'] in ('INVISIBLE', 'NO-README')]
print("  DRAFTING THE MISSING SECTIONS, VIA THE API, NO CLONES")
print("  " + "=" * 76)
summary = []
for name in targets:
    try:
        files, _ = from_github(name)
    except Exception as e:
        print(f"  {name}: read failed ({type(e).__name__})"); continue
    if not files:
        print(f"  {name}: tree unavailable"); continue
    ev = evidence_from_api(name, files)
    negs = [e for e in ev if e[2] == 'negative']
    canon = [e for e in ev if e[2] == 'positive' and 'canonical command' in e[0]]
    summary.append((name, len(files), len(negs), canon[0][0] if canon else None))
    print(f"\n  === {name} — {len(files)} files, {len(negs)} verified limitations ===")
    for fact, art, _k in negs:
        print(f"    - {fact}  _(`{art}`)_")
    if canon:
        print(f"    [L3 CAN BE DERIVED] {canon[0][0]}")
    else:
        print(f"    [L3 NEEDS A HUMAN] no build file, so the receipt cannot be guessed")
    print(f"    [L5 NEEDS A HUMAN] failure modes are not derivable from a file listing")
json.dump(summary, open('/workspace/fleet-legend/completion_summary.json','w'), indent=1)
print(f"\n  {len(summary)} repos analysed; {sum(1 for s in summary if s[3])} have a derivable L3")
