#!/usr/bin/env python3
"""
calibrate.py — the `calibrate` angle, wired.

THE ARGUMENT FOR DELEGATING THIS TO THE ORACLE

The wheel ranks the spine by a KEYWORD MATCHER I wrote. I am therefore the worst possible
instrument to grade my own matcher: I built it, I read the same tree it read, and I am
overconfident about which papers are pressable because pressable is the thing I have wanted
to be true all night.

The oracle is a different instrument on the same question. So ask BOTH and look at the
DISAGREEMENT. Where they differ, one of them is wrong and the disagreement says which part
of the matcher to distrust. That is the anti-GAN doctrine applied to my own tooling: many
routes to the same answer make the answer durable, and a single route has nothing to
disagree with.

THE CONTRACT, EARNED IN ELEVEN PRE-REGISTERED ROUNDS

  - the state is a FIRST-CLASS body field, not something buried in the instructions
  - every question NAMES its subject, or a batched noul collapses to one answer
  - `noul` is the gate regime and works; `score` is a near-constant generator and is NOT
    used here, because a constant cannot rank anything
  - the useful number for a batch is the DISTRIBUTION across subjects, not any one answer
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wheel import scan, ANGLES

API = os.environ.get("JEV_BASE", "https://api.typesafe.ai") + "/v1/systemone"
KEY = os.environ.get("TYPESAFEAI_KEY", "")
H = {"User-Agent": "wheel-calibrate/1.0", "Authorization": f"Bearer {KEY}",
     "Content-Type": "application/json"}

QUESTION = ("Does this paper have a concrete artifact attached — runnable code, a small "
            "repository, or stored results — that someone could run or check right now, "
            "rather than only a description of an idea?")


def ask(subjects, tries=4):
    if not KEY:
        return {}, 0
    state = ". ".join(f"Subject {i}: {s}" for i, s in enumerate(subjects)) + "."
    payload = {"model": "jev-latest", "state": state, "questions": {}}
    for i in range(len(subjects)):
        payload["questions"][f"subject_{i}"] = {
            "type": "noul",
            "instructions": f"Regarding Subject {i}: {QUESTION}",
            "criteria": {"true": "yes, there is a checkable artifact",
                         "false": "no, it is only a description"},
        }
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(
                    API, data=json.dumps(payload).encode(), headers=H), timeout=60) as r:
                d = json.loads(r.read())
            out = {}
            for i in range(len(subjects)):
                v = d.get("answers", {}).get(f"subject_{i}", {}).get("noul")
                if isinstance(v, dict):
                    v = v.get("probability")
                try: out[i] = float(v)
                except (TypeError, ValueError): out[i] = None
            return out, attempt
        except Exception:
            time.sleep(2 + attempt)
    return {}, tries


def main():
    items = scan()
    top = items[:12]
    subs = []
    for it in top:
        ev = []
        if it["ecosystem"]: ev.append(f"attached repo {it['ecosystem'][0]}")
        if it["code"]: ev.append(f"{len(it['code'])} code path(s)")
        if it["results"]: ev.append(f"{len(it['results'])} stored result file(s)")
        if it["appendix"]: ev.append(f"{it['appendix']} math appendix file(s)")
        subs.append(f"paper {it['name']}, evidence: " + ("; ".join(ev) if ev else "none found"))

    print("\n  CALIBRATE — the oracle ranks the spine; my keyword matcher already did")
    print("  " * 30)
    print(f"  question: {QUESTION}\n")
    sc, r = ask(subs)
    if not sc:
        print("  no oracle response (missing key or endpoint down) — reported, not guessed")
        return 2
    rows = []
    for i, it in enumerate(top):
        rows.append((sc.get(i), it["score"], it["name"]))
    rows.sort(key=lambda t: (-(t[0] or 0), -t[1]))
    print(f"  {'oracle':>7} {'matcher':>8}  paper")
    print("  " + "-" * 70)
    for p, m, n in rows:
        ps = f"{p:.3f}" if isinstance(p, float) else "  --  "
        flag = "  <-- DISAGREE" if isinstance(p, float) and ((p > 0.6) != (m >= 20)) else ""
        print(f"  {ps:>7} {m:>8}  {n[:44]:44}{flag}")
    agree = sum(1 for p, m, _ in rows if isinstance(p, float) and ((p > 0.6) == (m >= 20)))
    print(f"\n  agreement on press/no-press: {agree}/{len(rows)}")
    print("  DISAGREEMENTS are the deliverable. A single route has nothing to disagree with;")
    print("  that is the whole reason to ask the oracle rather than to re-read my own list.")
    json.dump([{'oracle_p': p, 'matcher_score': m, 'paper': n} for p, m, n in rows],
              open("out/calibration.json", "w"), indent=1)
    print("  wrote out/calibration.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
