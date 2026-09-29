"""EXPERIMENT 1 — test-retest stability. Does the same question give the same p?

The gate is `p > 0.7` on ONE call. If repeat calls spread across 0.7, the gate is
sampling noise. This is the single most important property for a threshold gate.
"""
import sys, json
sys.path.insert(0, '/workspace/research/lanes/jevlab')
from harness import noul, summarize
from concurrent.futures import ThreadPoolExecutor, as_completed

# Claims chosen to straddle the 0.7 boundary on purpose — those are where a
# threshold gate actually does work or fail.
CLAIMS = [
 ("strong_true", "A registry file described as: every line is sealed with a sha256 of its own prediction text, the file is append-only, and a validator proves the old file is a byte-prefix of the new one across commits. Editing a sealed line is impossible without breaking the hash chain.", True),
 ("middling", "A CI workflow that runs a test suite and then publishes artifacts. The suite passes if no assertion fails.", True),
 ("weak_true", "A method documented with a comment describing what it does.", True),
 ("strong_false", "A registry file described as: the team is careful and does not usually change old entries.", False),
 ("middling_false", "A CI workflow that runs a test suite but has a step that always passes regardless of results.", False),
 ("clear_false", "A proof described as: verified by reading it once.", False),
]

CRIT = ("Yes, the description supports this.", "No, the description contradicts this or does not establish it.")

def probe(claim, truth, instr, tag):
    state, _, name = claim
    return noul(state, instr, CRIT[0], CRIT[1], tag)

def run_repeats(reps=6):
    jobs = []
    for c in CLAIMS:
        for i in range(reps):
            jobs.append((c, i))
    out = {c[0]: [] for c in CLAIMS}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(probe, c, c[1],
                          "Does the description support the following statement?",
                          f"q{i}"): c for c, i in jobs}
        for f in as_completed(futs):
            c = futs[f]
            try: out[c[0]].append(f.result())
            except Exception: out[c[0]].append(None)
    return out

if __name__ == "__main__":
    res = run_repeats(6)
    print("EXPERIMENT 1 — TEST-RETEST STABILITY (6 identical calls per claim)")
    print("=" * 92)
    print(f"  {'claim':16} {'truth':6} {'mean':>7} {'min':>7} {'max':>7} {'spread':>8} {'sd':>7}  crosses 0.7?")
    print("-" * 92)
    crossings = 0
    for c in CLAIMS:
        name, truth = c[0], c[1]
        vs = [v for v in res[name] if v is not None]
        if not vs: print(f"  {name:16} NO DATA"); continue
        import statistics
        mn, mx = min(vs), max(vs)
        crosses = mn < 0.7 < mx or (mn >= 0.7) != (mx >= 0.7)
        if crosses: crossings += 1
        print(f"  {name:16} {str(truth):6} {statistics.mean(vs):>7.3f} {mn:>7.3f} {mx:>7.3f} "
              f"{mx-mn:>8.3f} {statistics.pstdev(vs):>7.3f}  {'YES <-- GATE FLIPS' if crosses else 'no'}")
    print("-" * 92)
    print(f"  claims whose verdict flips across the 0.7 threshold on repeat: {crossings}/{len(CLAIMS)}")
    json.dump(res, open('/workspace/research/lanes/jevlab/exp1.json','w'), indent=2)
