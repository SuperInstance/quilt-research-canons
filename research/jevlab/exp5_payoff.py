"""EXPERIMENT 5 — the payoff: does the decomposed gate catch the gameable claims?

The externalisability audit found 10/10 sealed predictions could be satisfied by
bookkeeping. Those are the claims the fleet ACTUALLY uses. If the decomposed gate
(mechanism AND guarantee, min-aggregated) rejects them where the composite accepted
them, the method is worth shipping. If it accepts them too, the method is decoration.

The adversarial cases are the auditors' own "cheapest way to satisfy this" answers.
"""
import sys, statistics
sys.path.insert(0, '/workspace/research/lanes/jevlab')
from harness import jev
from concurrent.futures import ThreadPoolExecutor, as_completed

T = "Yes, this is genuinely present and checkable by a third party."
F = "No, or it is only asserted/present-as-bookkeeping rather than substantiated."

def composite(state):
    try:
        r = jev(state, {"q": {"type": "noul",
            "instructions": "Is this a substantive, externally checkable claim rather than bookkeeping?",
            "criteria": {"true": T, "false": F}}})
        return r["answers"]["q"].get("noul")
    except Exception: return None

def decomposed(state):
    """Two orthogonal sub-questions, min-aggregated. The min is the point: a claim is
    only as strong as its weaker half, and the two halves fail for different reasons."""
    try:
        r = jev(state, {
          "mech": {"type": "noul",
            "instructions": "Is there a MECHANISM — something that would have to physically break for this to be false?",
            "criteria": {"true": T, "false": F}},
          "ext":  {"type": "noul",
            "instructions": "Could a third party with NO access to this project verify it, using only public information?",
            "criteria": {"true": T, "false": F}},
        })["answers"]
        m, e = r["mech"].get("noul"), r["ext"].get("noul")
        return m, e, (None if m is None or e is None else min(m, e))
    except Exception: return None, None, None

# The auditors' own "cheapest way to satisfy this" — the gameable phrasings.
GAMEABLE = [
 ("M1", "Every lane pre-registration cites a mine id, and registrations carry a nearest_prior + delta statement. (Satisfiable by appending the boilerplate to every file.)"),
 ("M4", "Every lane header carries a pre-registered budget cap and verdicts state spend. (Satisfiable by writing an unlimited cap line in every header.)"),
 ("M9", "At least half the wave-60 queue items cite a mine id. (Satisfiable by making the queue empty or redefining it.)"),
 ("M5", "Lane deaths plus mid-lane resumes fall to at most 1 per wave. (Satisfiable by not recording deaths.)"),
 ("M6", "The playtest lane opens a self-play-synthesized adversarial task harness as a gift PR. (Satisfiable by opening a PR with that word in the title.)"),
]
# A genuinely checkable claim, as a control.
SOLID = [
 ("S1", "The C99 reference port publishes a signed git tag whose message records the sha256 of the source tree, and recomputing the tree from a clean clone reproduces that hash. Any stranger can run this with git and sha256sum."),
 ("S2", "The release verifier recomputes the source-tree digest and the receipt hash and fails if either disagrees with what the tag records. It has a self-test covering a tampered receipt and a wrong tree hash."),
]

def unpack(r):
    """decompose() returns (mech, ext, min). Unpack defensively so a shape change shows
    up as -- rather than silently degrading the comparison."""
    d = r.get("dec")
    if isinstance(d, (list, tuple)) and len(d) == 3:
        return d[0], d[1], d[2]
    if isinstance(d, (int, float)):
        return None, None, d
    return None, None, None


def run(items):
    out = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {}
        for name, s in items:
            futs[ex.submit(composite, s)] = (name, "comp")
            futs[ex.submit(decomposed, s)] = (name, "dec")
        for f in as_completed(futs):
            name, kind = futs[f]
            out.setdefault(name, {})[kind] = f.result()
    return out

if __name__ == "__main__":
    res = run(GAMEABLE + SOLID)
    print("EXPERIMENT 5 — PAYOFF: decomposed gate vs composite on the fleet's OWN gameable claims")
    print("=" * 106)
    print(f"  {'claim':6} {'COMPOSITE':>11} {'DECOMP':>8} {'  mech':>7} {'  ext':>7}  {'comp>0.7':>9} {'dec>0.7':>8}")
    print("-" * 106)
    comp_bad = dec_bad = 0
    for name, s in GAMEABLE:
        r = res.get(name, {})
        c = r.get("comp"); d = r.get("dec")
        m, e, d = unpack(r)
        f = lambda x: f"{x:.3f}" if isinstance(x,(int,float)) else "  --  "
        cp = isinstance(c,(int,float)) and c > 0.7
        dp = isinstance(d,(int,float)) and d > 0.7
        comp_bad += cp; dec_bad += dp
        print(f"  {name:6} {f(c):>11} {f(d):>8} {f(m):>7} {f(e):>7}  {str(cp):>9} {str(dp):>8}  <- gameable")
    print("-" * 106)
    for name, s in SOLID:
        r = res.get(name, {})
        c, d = r.get("comp"), r.get("dec")
        m, e, d = unpack(r)
        f = lambda x: f"{x:.3f}" if isinstance(x,(int,float)) else "  --  "
        cp = isinstance(c,(int,float)) and c > 0.7
        dp = isinstance(d,(int,float)) and d > 0.7
        comp_bad += not cp; dec_bad += not dp
        print(f"  {name:6} {f(c):>11} {f(d):>8} {f(m):>7} {f(e):>7}  {str(cp):>9} {str(dp):>8}  <- SOLID control")
    print("-" * 106)
    print()
    print(f"  COMPOSITE gate misclassifies: {comp_bad}/{len(GAMEABLE)+len(SOLID)}")
    print(f"  DECOMPOSED gate misclassifies: {dec_bad}/{len(GAMEABLE)+len(SOLID)}")
    print()
    if dec_bad < comp_bad:
        print("  => The decomposed gate is STRICTLY BETTER on the fleet's own real claims.")
        print("     The sub-questions are also diagnostic: they say WHICH half is missing.")
    elif dec_bad == comp_bad:
        print("  => No improvement on these. The method is diagnostic, not stronger.")
    else:
        print("  => Decomposition made it WORSE here. Do not ship it as a gate.")
