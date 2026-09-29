#!/usr/bin/env python3
"""
sweep.py — run process_signature over the fleet, ranked by size.

The ranking rule is the one this session paid for: rank by file/test count and recent
push, never by name prefix. `claw` is the proof -- 7,445 files, invisible to every prefix
search run today.
"""
import json, os, sys, urllib.request, urllib.error, time
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from process_signature import signature

TOK = os.environ.get("GITHUB_TOKEN", "")
H = {"Authorization": f"Bearer {TOK}", "Accept": "application/vnd.github+json",
     "User-Agent": "process-signature"}
B = "https://api.github.com"

def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:
        return 0, {}

def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    rows = json.load(open("/workspace/fleet-count.json"))
    # rank by declared size (KB) then fork-free; the census field is the API's own size
    rows = [r for r in rows if not r.get("fork")]
    rows.sort(key=lambda r: -(r.get("size") or 0))
    sample = rows[:limit]
    print(f"  PROCESS SIGNATURE SWEEP — top {len(sample)} non-fork repos by size")
    print("  " + "=" * 70)
    out = []
    for r in sample:
        st, tree = get(f"{B}/repos/SuperInstance/{r['name']}/git/trees/HEAD?recursive=1")
        if st != 200 or "tree" not in tree:
            print(f"    {r['name'][:30]:30} tree unavailable ({st})"); continue
        files = [e["path"] for e in tree["tree"] if e["type"] == "blob"]
        # fetch a small slice of text for the TEXT archetypes only (bounded)
        text = ""
        for cand in [f for f in files if f.lower().endswith((".md", ".jsonl", ".json"))][:3]:
            st2, b2 = get(f"{B}/repos/SuperInstance/{r['name']}/contents/{cand}")
            if st2 == 200 and "content" in b2:
                import base64
                try: text += base64.b64decode(b2["content"]).decode("utf-8", "replace")[:20000]
                except Exception: pass
        s = signature(r["name"], files, text)
        out.append(s)
        time.sleep(0.12)
    grades = Counter(s.grade() for s in out)
    print()
    print("  GRADE DISTRIBUTION (path evidence only, reproducible from a tree listing)")
    print("  " + "=" * 70)
    for g, n in grades.most_common():
        print(f"    {g:30} {n:>3}  {'#' * n}")
    print()
    print("  PATH EVIDENCE FREQUENCY — how many of these repos leave each trace")
    print("  " + "=" * 70)
    freq = Counter()
    for s in out:
        for a in s.path_archetypes(): freq[a] += 1
    for a, n in freq.most_common():
        print(f"    {a:30} {n:>3} / {len(out)}  ({100*n/len(out):.0f}%)")
    print()
    print("  TEXT EVIDENCE FREQUENCY — only counted where content was fetched")
    print("  " + "=" * 60)
    tf = Counter()
    supplied = sum(1 for s in out if s.text_supplied)
    for s in out:
        for a in s.text_archetypes(): tf[a] += 1
    for a, n in tf.most_common():
        print(f"    {a:30} {n:>3} / {supplied} with text  ({100*n/max(1,supplied):.0f}%)")
    print()
    print("  THE NOVEL PART: repos that describe a rigorous process in PROSE and")
    print("  leave no PATH trace of running one. Those are the NARRATIVE-FIRST rows with")
    print("  text evidence present. They are invisible to a code reviewer and to a reader.")
    phantom = [s for s in out if s.grade() == "NARRATIVE-FIRST" and s.text_archetypes()]
    print(f"    count: {len(phantom)} of {len(out)}")
    for s in phantom[:12]:
        print(f"      {s.repo[:34]:34} {s.n_docs:>4} docs  {s.n_code:>5} code  text-ev: {s.text_archetypes()}")
    json.dump([dict(repo=s.repo, grade=s.grade(), path=s.path_archetypes(),
                    text=s.text_archetypes(), files=s.n_files, code=s.n_code,
                    docs=s.n_docs, tests=s.n_tests, ci=s.n_ci, jsonl=s.n_jsonl,
                    gap=s.gap()) for s in out],
              open("/workspace/projects/process-signature/fleet_sweep.json", "w"), indent=1)
    print("\n  wrote fleet_sweep.json")

if __name__ == "__main__":
    main()
