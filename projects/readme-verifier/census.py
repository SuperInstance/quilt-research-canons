#!/usr/bin/env python3
"""census.py — is README drift 2-of-2, or 2-of-N?

"A README is an executable claim nobody ran" is only interesting if you know the
rate. Two hand-found defects out of two repos examined is a story, not a measurement.
This runs the verifier across a sample and reports the rate.

Sample is `pushed_at` descending (the repos most likely to be live), forks excluded
because a fork's README is upstream's. It is NOT a random sample of the account and
must not be reported as one.
"""
import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
import verify

def pick(n):
    repos, seen = [], set()
    for page in range(1, 8):
        d = verify.api(f"/users/SuperInstance/repos?per_page=100&page={page}&sort=pushed&direction=desc")
        if not isinstance(d, list) or not d: break
        for r in d:
            if r["name"] in seen: continue
            seen.add(r["name"])
            if r.get("fork") or r.get("archived"): continue
            repos.append(r["full_name"])
            if len(repos) >= n: return repos
    return repos

def one(repo):
    t0 = time.time()
    try:
        res = verify.analyse(repo, sample=180)
    except Exception as e:
        res = {"repo": repo, "verdict": "ERROR", "err": str(e)[:80]}
    res["secs"] = round(time.time() - t0, 1)
    return res

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 25
    repos = pick(n)
    print(f"  census over {len(repos)} non-fork repos, most-recently-pushed first")
    if verify._auth_state.get("token_dead"):
        print("  NOTE: GITHUB_TOKEN returned 401; running unauthenticated on public reads only.")
        print("        That is sufficient for this check -- READMEs and source are public --")
        print("        but push, PR review, and CI logs are unavailable until it is refreshed.")
    with ThreadPoolExecutor(max_workers=4) as ex:
        out = list(ex.map(one, repos))
    out.sort(key=lambda r: r.get("repo", ""))
    json.dump(out, open("/workspace/research/scout/readme-census.json", "w"), indent=1)
    drifted = [r for r in out if r.get("verdict") == "DRIFTED"]
    clean   = [r for r in out if r.get("verdict") == "CLEAN"]
    other   = [r for r in out if r.get("verdict") not in ("DRIFTED", "CLEAN")]
    # A repo whose check could not RUN is not a repo that is fine. Count it as
    # UNREADABLE and refuse to publish a rate that silently drops them.
    n = len(out)
    if other:
        print(f"\n  {len(other)} of {n} repos could not be read. NOT publishing a rate:")
        print("  a drift percentage over the readable remainder would be a number produced")
        print("  by excluding the failures from the denominator, which is the thing this")
        print("  whole project exists to catch. Fix the reader, then re-run.")
        for r in other[:8]: print(f"    {r['repo'].replace('SuperInstance/',''):26} {str(r.get('err') or r.get('readme') or '')[:50]}")
        json.dump(out, open("/workspace/research/scout/readme-census.json", "w"), indent=1)
        sys.exit(2)
    print(f"\n  DRIFTED {len(drifted)}   CLEAN {len(clean)} of {n} read"
          f"   -> {100*len(drifted)/max(1,n):.0f}% drifted\n")
    for r in drifted:
        bits = []
        if r.get("missing_symbols"):     bits.append("sym:" + ",".join(r["missing_symbols"][:3]))
        if r.get("missing_mechanisms"): bits.append("mech:" + ",".join(r["missing_mechanisms"][:2]))
        if r.get("missing_paths"):      bits.append("path:" + ",".join(r["missing_paths"][:2]))
        print(f"    {r['repo'].replace('SuperInstance/',''):28} {' | '.join(bits)[:88]}")
    print("\n  table: /workspace/research/scout/readme-census.json")
