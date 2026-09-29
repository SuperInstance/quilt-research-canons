"""EXPERIMENT 2 — is 0.7 reachable AT ALL?

Experiment 1 found something more important than instability: the STRONGEST possible
description (sha256-sealed, append-only, byte-prefix proven) scored 0.598 and never
crossed 0.7 in 6 calls. If the top of the scale is ~0.6, then `p > 0.7` promotes almost
nothing, and the fleet's canon gate has been operating below its own ceiling.

This maps the whole scale: from absurdly weak to absurdly strong evidence.
"""
import sys, statistics
sys.path.insert(0, '/workspace/research/lanes/jevlab')
from harness import noul
from concurrent.futures import ThreadPoolExecutor, as_completed

CRIT = ("Yes, the description definitively establishes this.",
        "No, the description does not establish this.")

# A ladder from nonsense to mathematical proof, all the same question shape.
LADDER = [
 (0.00, "Nothing relevant. The file is a folder of unrelated notes.", "A registry is append-only and tamper-evident."),
 (0.15, "A registry file. It exists.", "A registry is append-only and tamper-evident."),
 (0.30, "A registry file where lines are sorted alphabetically.", "A registry is append-only and tamper-evident."),
 (0.45, "A registry file where each line records a prediction. A README says lines should not be edited.", "A registry is append-only and tamper-evident."),
 (0.60, "A registry file where each line is sealed with a sha256 of its own text. Editing a line breaks its own hash.", "A registry is append-only and tamper-evident."),
 (0.75, "A registry file where each line is sealed with sha256, the file is append-only by construction, and a fail-closed validator proves the old file is a byte-prefix of the new across every commit. Editing a sealed line is impossible without breaking the hash chain.", "A registry is append-only and tamper-evident."),
 (0.90, "A registry file where every line is sha256-sealed, append-only by construction, with a fail-closed validator proving byte-prefix preservation across all commits, AND a second independent implementation in a different language reproduces every digest, AND both implementations are public with a passing conformance test.", "A registry is append-only and tamper-evident."),
 (1.00, "A registry file where every line is sha256-sealed, append-only by construction, fail-closed validated for byte-prefix preservation, independently reproduced by a second implementation, publicly available, conformance-tested, AND the property is checked by a small Lean 4 proof that the validator's byte-prefix check implies append-onlyness, published and kernel-checked.", "A registry is append-only and tamper-evident."),
]

def probe(item):
    lvl, state, instr = item
    v = noul(state, instr, CRIT[0], CRIT[1], f"q{lvl}")
    return lvl, v

if __name__ == "__main__":
    # 3 samples per rung, report mean
    jobs = [(lvl, s, i) for lvl, s, _ in LADDER for i in range(3)]
    res = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {}
        for lvl, s, i in jobs:
            _, _, instr = next(x for x in LADDER if x[0] == lvl)
            futs[ex.submit(noul, s, instr, CRIT[0], CRIT[1], f"q{i}")] = lvl
        for f in as_completed(futs):
            res.setdefault(futs[f], []).append(f.result())

    print("EXPERIMENT 2 — THE SCALE CEILING: how strong must evidence be to clear 0.7?")
    print("=" * 96)
    print(f"  {'designed strength':>18}  {'mean p':>7}  {'min':>6} {'max':>6}  evidence added")
    print("-" * 96)
    for lvl, s, _ in LADDER:
        vs = [v for v in res.get(lvl, []) if v is not None]
        if not vs: continue
        short = s[:64]
        flag = "  <-- CLEARS 0.7" if statistics.mean(vs) > 0.7 else ""
        print(f"  {lvl:>18.2f}  {statistics.mean(vs):>7.3f}  {min(vs):>6.3f} {max(vs):>6.3f}  {short}{flag}")
    print("-" * 96)
    top = statistics.mean([v for v in res[1.00] if v is not None])
    print(f"  MAX ACHIEVABLE (Lean-4-proof, dual implementation, published): {top:.3f}")
    print()
    if top < 0.7:
        print("  => The fleet's canon gate `p > 0.7` is ABOVE the instrument's ceiling.")
        print("     Evidence stronger than a machine-checked proof of the property still")
        print("     cannot promote. The gate is not measuring quality; it is measuring")
        print("     nothing, and the ones that DID promote were weaker claims.")
