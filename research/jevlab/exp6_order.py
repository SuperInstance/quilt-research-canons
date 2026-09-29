"""EXPERIMENT 6 — batch order. Does a question's POSITION in the batch move it?

The API accepts many questions in one call, and the fleet sends several. If position
bias exists, a claim can promote or fail depending on where it happened to land — which
would make every multi-question gate order-dependent and its receipts irreproducible.
This is cheap to test and, if it bites, it invalidates a whole class of usage.
"""
import sys, statistics
sys.path.insert(0, '/workspace/research/lanes/jevlab')
from harness import jev
from concurrent.futures import ThreadPoolExecutor, as_completed

T = "Yes, this is genuinely present and checkable."
F = "No, or it is only asserted rather than substantiated."

# Five claims, each asked in a batch of five, at a DIFFERENT position each round.
# If there is no position effect, every claim's number should be flat across rounds.
CLAIMS = {
 "C1": "A signed git tag whose message records the sha256 of the source tree; recomputing the tree from a clean clone reproduces that hash.",
 "C2": "Every lane header carries a pre-registered budget cap and each verdict states spend against it.",
 "C3": "A validator proves the old registry file is a byte-prefix of the new one across commits, and fails closed.",
 "C4": "Every registration cites its nearest prior and states the delta.",
 "C5": "A second independent implementation in a different language reproduces every digest, and both are public.",
}

def batch_round(order):
    q = {c: {"type": "noul",
            "instructions": "Is this claim genuinely present and checkable by a third party?",
            "criteria": {"true": T, "false": F}} for c in order}
    try:
        r = jev("; ".join(f"{c}: {CLAIMS[c]}" for c in order), q)["answers"]
        return {c: r[c].get("noul") for c in order}
    except Exception:
        return {c: None for c in order}

if __name__ == "__main__":
    keys = list(CLAIMS)
    rotations = [keys[i:] + keys[:i] for i in range(len(keys))]  # 5 rotations, each claim at each position
    rounds = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = {ex.submit(batch_round, rot): ri for ri, rot in enumerate(rotations)}
        for f in as_completed(futs):
            rounds.append(f.result())

    per = {c: [] for c in keys}
    pos  = {c: [] for c in keys}
    for ri, r in enumerate(rounds):
        for slot, c in enumerate(keys):
            if isinstance(r.get(c), (int, float)):
                per[c].append(r[c])
                pos[c].append((ri, slot, r[c]))

    print("EXPERIMENT 6 — POSITION EFFECT: each claim asked in 5 batches, at 5 different positions")
    print("=" * 92)
    print(f"  {'claim':6} {'n':>2} {'mean':>7} {'min':>6} {'max':>6} {'range':>7}  p by position")
    print("-" * 92)
    worst = 0.0
    for c in keys:
        vs = per[c]
        if not vs: print(f"  {c:6} NO DATA"); continue
        rng = max(vs) - min(vs)
        worst = max(worst, rng)
        by = " ".join(f"{v:.2f}" for _, _, v in sorted(pos[c], key=lambda x: x[1]))
        print(f"  {c:6} {len(vs):>2} {statistics.mean(vs):>7.3f} {min(vs):>6.3f} {max(vs):>6.3f} {rng:>7.3f}  {by}")
    print("-" * 92)
    print(f"  worst within-claim range across positions: {worst:.3f}")
    print()
    if worst < 0.15:
        print("  => NO material position effect. Batch order is safe to ignore.")
        print("     Multi-question receipts are reproducible regardless of ordering.")
    else:
        print("  => POSITION EFFECT PRESENT. Multi-question gates are order-dependent and")
        print("     their receipts are not reproducible. Fix: one question per call, or randomise.")
