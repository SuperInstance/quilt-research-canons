"""jevlab — how should the fleet actually USE typesafe.ai?

Everything so far measured whether JEV's question types DISCRIMINATE:
  noul  — yes (regime B, 3/3, 0.85 spread)
  choice — yes (0.94 / 0.06 / 0.00 / 0.00)
  score  — no (constant ~2.6, empty shell == numpy)

But the fleet's canon gate is `p > 0.7` on a SINGLE noul call. Discrimination is
necessary and not sufficient. A gate needs a number that is:
  STABLE   — does the same question give the same p on repeat?
  FRAME-INDEPENDENT — does the wording of the instruction move it?
  ORDER-INDEPENDENT  — does its position in a batch move it?
  DECOMPOSABLE       — does splitting a compound claim beat asking it whole?

Those four are what this measures. If p is not stable, then a 0.7 threshold is
sampling noise with extra steps, and every gate built on it inherits that.
"""
import json, os, statistics, urllib.request, urllib.error

KEY = os.environ["TYPESAFEAI_KEY"]
URL = "https://api.typesafe.ai/v1/systemone"

def jev(state, questions, model="jev-latest", retries=4):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(URL,
                data=json.dumps({"model": model, "state": state, "questions": questions}).encode(),
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
                method="POST")
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception:
            if attempt == retries - 1: raise
            import time; time.sleep(0.6 * 2 ** attempt)

def noul(state, instructions, true="", false="", name="q", model="jev-latest"):
    q = {name: {"type": "noul", "instructions": instructions,
                "criteria": {"true": true, "false": false}}}
    try:
        r = jev(state, q, model=model)
        return r["answers"][name].get("noul")
    except Exception as e:
        return None

def spread(xs):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2: return None
    return max(xs) - min(xs)

def stdev(xs):
    xs = [x for x in xs if x is not None]
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0

def summarize(name, vals):
    vs = [v for v in vals if v is not None]
    if not vs: return f"  {name:38} NO DATA"
    return (f"  {name:38} n={len(vs)} mean={statistics.mean(vs):.3f} "
            f"min={min(vs):.3f} max={max(vs):.3f} spread={spread(vs):.3f} sd={stdev(vs):.3f}")
