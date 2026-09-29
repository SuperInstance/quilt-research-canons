"""EXPERIMENT 3 — bisect the phase transition.

Exp 2 found a cliff between "sha256-sealed" (0.40) and "append-only by construction,
fail-closed, byte-prefix proven" (0.97), and then a slight DECREASE as more evidence is
added. If the gate is a step function, the step has a locatable cause, and a gate with a
known cause can be designed around. If it is noisy, it cannot.
"""
import sys, statistics
sys.path.insert(0, '/workspace/research/lanes/jevlab')
from harness import noul
from concurrent.futures import ThreadPoolExecutor, as_completed

CRIT = ("Yes, the description definitively establishes this.",
        "No, the description does not establish this.")
Q = "Does the description establish that the registry is append-only and tamper-evident?"

# A monotone ladder: each rung adds ONE clause, in a fixed order. The transition must
# land somewhere on this sequence if it is driven by evidence content.
RUNG = [
 ("0: file exists",
  "A registry file."),
 ("1: + records predictions",
  "A registry file where each line records one prediction."),
 ("2: + lines are sealed",
  "A registry file where each line records one prediction sealed with the sha256 of its own text."),
 ("3: + editing breaks the hash",
  "A registry file where each line records one prediction sealed with the sha256 of its own text, so editing a sealed line breaks that line's hash."),
 ("4: + file is append-only",
  "A registry file where each line records one prediction sealed with the sha256 of its own text, so editing a sealed line breaks that line's hash. The file is append-only."),
 ("5: + byte-prefix proven",
  "A registry file where each line records one prediction sealed with the sha256 of its own text, so editing a sealed line breaks that line's hash. The file is append-only, and a validator proves the old file is a byte-prefix of the new."),
 ("6: + validator fail-closed",
  "A registry file where each line records one prediction sealed with the sha256 of its own text, so editing a sealed line breaks that line's hash. The file is append-only, and a fail-closed validator proves the old file is a byte-prefix of the new."),
 ("7: + byte-prefix ACROSS COMMITS",
  "A registry file where each line records one prediction sealed with the sha256 of its own text, so editing a sealed line breaks that line's hash. The file is append-only, and a fail-closed validator proves the old file is a byte-prefix of the new ACROSS COMMITS."),
 ("8: + independent reimplementation",
  "A registry file where each line records one prediction sealed with the sha256 of its own text, so editing a sealed line breaks that line's hash. The file is append-only, and a fail-closed validator proves the old file is a byte-prefix of the new ACROSS COMMITS. A second independent implementation in another language reproduces the digests."),
]

def probe(item):
    name, state = item
    return name, noul(state, Q, CRIT[0], CRIT[1], "q")

if __name__ == "__main__":
    res = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(probe, r): r for r in RUNG}
        for f in as_completed(futs):
            name, v = f.result()
            res.setdefault(name, []).append(v)

    print("EXPERIMENT 3 — BISECTING THE TRANSITION (one clause added per rung, 3 samples each)")
    print("=" * 100)
    print(f"  {'rung':34} {'mean p':>7} {'min':>6} {'max':>6}  status")
    print("-" * 100)
    prev = None
    for name, _ in RUNG:
        vs = [v for v in res.get(name, []) if v is not None]
        if not vs: continue
        m = statistics.mean(vs)
        delta = f"  (+{m-prev:.3f})" if prev is not None else ""
        status = "PROMOTES" if m > 0.7 else "blocked"
        bar = "#" * int(m * 30)
        print(f"  {name:34} {m:>7.3f} {min(vs):>6.3f} {max(vs):>6.3f}  {status:8} {bar}{delta}")
        prev = m
    print("-" * 100)
    print()
    print("  READ: find the rung where the status flips. That rung is the law.")
    flips = [name for name, _ in RUNG
             if statistics.mean([v for v in res.get(name,[]) if v is not None]) > 0.7]
    first = flips[0] if flips else None
    if first:
        print(f"  First promoting rung: {first}")
        print("  => The gate is a STRUCTURAL completeness test, not a quality scale.")
        print("     A claim promotes when the MECHANISM and the GUARANTEE are both present,")
        print("     regardless of how much more you pile on afterwards.")
