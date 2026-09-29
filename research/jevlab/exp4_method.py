"""EXPERIMENT 4 — can we USE the step function?

Exp 3 found the gate is a STRUCTURAL completeness test: mechanism alone never promotes,
mechanism + an explicit guarantee always promotes, and extra evidence after that is inert.

If that is the shape, the useful question is not "what threshold" but "what do we ASK".
Three candidate methods, each a different way of reshaping the question set:

  A. COMPOSITE   one question covering the whole claim          (status quo)
  B. DECOMPOSE   split into sub-claims, AND them (min)          (does splitting help?)
  C. PRIME       restate the claim so the guarantee is explicit (does wording help?)
  D. REDUCE      strip to the bare guarantee only              (is the mechanism load-bearing?)

If D promotes a claim whose mechanism is absent, the instrument is scoring the GUARANTEE
STATEMENT, not the evidence — and the gate is theater in a very specific way.
"""
import sys, statistics
sys.path.insert(0, '/workspace/research/lanes/jevlab')
from harness import jev
from concurrent.futures import ThreadPoolExecutor, as_completed

TRUE_ = "Yes, the description establishes this."
FALSE = "No, the description does not establish this."

# Four states, varying whether the MECHANISM is present and whether the GUARANTEE is stated.
STATES = {
 "mech+guar": "A registry where each line is sha256-sealed and the file is append-only.",
 "mech only": "A registry where each line is sha256-sealed with the sha256 of its own text.",
 "guar only": "A registry that is append-only.",
 "neither":   "A registry file.",
}

Q_COMPOSITE = "Is the registry append-only and tamper-evident?"
Q_PRIME     = "Is the registry append-only and tamper-evident? The description states the guarantee explicitly."
Q_BARE      = "Is the registry append-only?"

def ask(state, instructions, name, criteria=(TRUE_, FALSE)):
    q = {name: {"type": "noul", "instructions": instructions, "criteria": {"true": criteria[0], "false": criteria[1]}}}
    try:
        return jev(state, q)["answers"][name].get("noul")
    except Exception:
        return None

def decompose(state):
    """Ask the two halves separately, AND them with min (the conservative aggregator)."""
    q = {
        "m": {"type": "noul", "instructions": "Is the tamper-evidence mechanism present? (hashes, sealing, verification)",
              "criteria": {"true": TRUE_, "false": FALSE}},
        "g": {"type": "noul", "instructions": "Is append-only-ness explicitly guaranteed and stated?",
              "criteria": {"true": TRUE_, "false": FALSE}},
    }
    try:
        a = jev(state, q)["answers"]
        m, g = a["m"].get("noul"), a["g"].get("noul")
        return m, g, None if (m is None or g is None) else min(m, g)
    except Exception:
        return None, None, None

def cell(sname, s):
    return {
        "composite":  ask(s, Q_COMPOSITE, "q"),
        "prime":      ask(s, Q_PRIME,     "q"),
        "bare":       ask(s, Q_BARE,      "q"),
        "decomp":     decompose(s)[2],
        "dec_m":      decompose(s)[0],
        "dec_g":      decompose(s)[1],
    }

if __name__ == "__main__":
    res = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(cell, k, v): k for k, v in STATES.items()}
        for f in as_completed(futs):
            res[futs[f]] = f.result()

    print("EXPERIMENT 4 — FOUR QUESTION SHAPES x FOUR EVIDENCE STATES")
    print("=" * 104)
    print(f"  {'evidence state':12} {'COMPOSITE':>10} {'PRIMED':>8} {'DECOMP(min)':>12} {'  m':>6} {'  g':>6} {'BARE guar':>10}")
    print("-" * 104)
    for sname in ["mech+guar", "mech only", "guar only", "neither"]:
        r = res.get(sname, {})
        f = lambda x: f"{x:.3f}" if isinstance(x,(int,float)) else "  --  "
        print(f"  {sname:12} {f(r.get('composite')):>10} {f(r.get('prime')):>8} {f(r.get('decomp')):>12} "
              f"{f(r.get('dec_m')):>6} {f(r.get('dec_g')):>6} {f(r.get('bare')):>10}")
    print("-" * 104)
    print()
    print("  PROMOTE (p>0.7) under each method:")
    for meth, key in [("composite","composite"),("primed","prime"),("decomposed(min)","decomp"),("bare-guarantee","bare")]:
        pro = [s for s in STATES if isinstance(res.get(s,{}).get(key),(int,float)) and res[s][key] > 0.7]
        print(f"    {meth:16} -> {pro if pro else 'nothing promotes'}")
    print()
    bare_guar = res.get("guar only", {}).get("bare")
    if isinstance(bare_guar, (int,float)) and bare_guar > 0.7:
        print("  *** FINDING: asking ONLY the guarantee promotes a claim with NO MECHANISM. ***")
        print("      The instrument scores the GUARANTEE STATEMENT, not the evidence behind it.")
        print("      'the registry is append-only' with nothing sealing or validating it still")
        print("      promotes. The gate cannot distinguish a claim from a restatement.")
