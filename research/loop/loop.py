#!/usr/bin/env python3
"""
loop.py — an experiment loop that gains instead of accumulating.

The failure mode of a research fleet is a pile of results with nothing carried between
them. Every experiment is a one-shot; the next one starts from scratch; the same ground
gets covered twice; findings die in the round that produced them.

This loop fixes three things:

  1. PRE-REGISTRATION. Every round's predictions are written down BEFORE the run, with
     the numeric prediction stated in advance. That is the AHE decision-observability
     pattern applied to my own research: an experiment that cannot be wrong teaches
     nothing, and I would not know the difference without writing the prediction first.

  2. DEBRIEF. After each round, every prediction is marked CONFIRMED / REFUTED / INCONCLUSIVE
     with the actual number. A refuted prediction is worth more than a confirmed one,
     because it is the only thing in the loop that can correct a belief.

  3. R&D BETWEEN ROUNDS. The debrief's refutations feed the next round's design. The loop
     is not a queue of experiments; it is a chain where each link is chosen by the last.

The knowledge file is append-only across rounds. Round 3 starts by reading rounds 1-2.
"""
import json, os, statistics, sys, time, urllib.request
from datetime import datetime, timezone

KEY = os.environ.get("TYPESAFEAI_KEY")
URL = "https://api.typesafe.ai/v1/systemone"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loop_state.json")


def _post(state, questions, model="jev-latest", retries=4):
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
            time.sleep(0.6 * 2 ** attempt)


def noul(state, instructions, model="jev-latest", name="q"):
    try:
        r = _post(state, {name: {"type": "noul", "instructions": instructions,
                                 "criteria": {"true": "Yes, this is genuinely the case.",
                                              "false": "No, this is not the case."}}}, model)
        return r["answers"][name].get("noul")
    except Exception:
        return None


def load():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {"rounds": [], "carried": []}


def save(s):
    json.dump(s, open(STATE, "w"), indent=2)


def pre_register(round_no, title, predictions):
    """Predictions must state a number in advance. A prediction without a number is a
    vibe, and the loop cannot refute a vibe."""
    s = load()
    rnd = {"round": round_no, "title": title,
           "registered_at": datetime.now(timezone.utc).isoformat(),
           "predictions": predictions, "results": None, "debrief": None}
    s["rounds"].append(rnd)
    save(s)
    return rnd


def debrief(round_no):
    """Mark every prediction CONFIRMED / REFUTED / INCONCLUSIVE against the actual data."""
    s = load()
    rnd = next(r for r in s["rounds"] if r["round"] == round_no)
    verdicts = []
    for p in rnd["predictions"]:
        actual = p["result"]
        pred = p["predict"]
        if "kind" not in p:
            p["kind"] = "bool" if isinstance(pred, bool) else "num"
        if actual is None:
            verdicts.append({"id": p["id"], "status": "INCONCLUSIVE", "predicted": pred})
            continue
        # BUG worth naming: in Python `isinstance(True, int)` is True, so a numeric
        # branch placed FIRST swallows every boolean prediction and grades it as 1 or 0.
        # The boolean check has to come first, or the loop reports refutations that are
        # artifacts of Python's type hierarchy. This is the fourth time this session that a
        # reporting bug masqueraded as a result, and the worst of them, because refutations
        # are the only output in a research loop that can correct a belief.
        is_bool = isinstance(pred, bool) or p.get("kind") == "bool"
        if is_bool:
            want = pred if isinstance(pred, bool) else bool(pred)
            verdicts.append({"id": p["id"], "kind": "bool",
                             "predicted": want, "actual": actual,
                             "status": "CONFIRMED" if actual == want else "REFUTED"})
        elif isinstance(pred, (int, float)) and isinstance(actual, (int, float)):
            tol = p.get("tolerance", 0.10)
            ok = abs(actual - pred) <= tol
            verdicts.append({"id": p["id"], "kind": "num", "predicted": pred, "actual": actual,
                             "delta": round(actual - pred, 4), "tolerance": tol,
                             "status": "CONFIRMED" if ok else "REFUTED"})
        else:
            verdicts.append({"id": p["id"], "predicted": pred, "actual": actual,
                             "status": "INCONCLUSIVE"})
    rnd["debrief"] = verdicts
    # Carry the refutations forward as open questions for the next round's design.
    for v in verdicts:
        if v["status"] == "REFUTED":
            s["carried"].append({"from_round": round_no, "id": v["id"],
                                 "predicted": v.get("predicted"), "actual": v.get("actual"),
                                 "note": "prediction was wrong; the belief it encoded is suspect"})
    save(s)
    return verdicts


def show(round_no):
    s = load()
    rnd = next(r for r in s["rounds"] if r["round"] == round_no)
    print(f"ROUND {round_no}: {rnd['title']}")
    print("=" * 78)
    if rnd["debrief"]:
        for v in rnd["debrief"]:
            mark = {"CONFIRMED": "+", "REFUTED": "X", "INCONCLUSIVE": "?"}[v["status"]]
            extra = ""
            if v.get("actual") is not None:
                extra = f"  predicted={v.get('predicted')}  actual={v['actual']}"
                if v.get("delta") is not None:
                    extra += f"  delta={v['delta']:+}"
            print(f"  [{mark}] {v['id']:34} {v['status']}{extra}")
        c = sum(1 for v in rnd["debrief"] if v["status"] == "CONFIRMED")
        r_ = sum(1 for v in rnd["debrief"] if v["status"] == "REFUTED")
        i = sum(1 for v in rnd["debrief"] if v["status"] == "INCONCLUSIVE")
        print(f"  -> {c} confirmed, {r_} refuted, {i} inconclusive")
    else:
        for p in rnd["predictions"]:
            print(f"  [ ] {p['id']:34} predicts {p['predict']}")
    if s["carried"]:
        print()
        print("  CARRIED FORWARD (refutations to design against):")
        for c in s["carried"]:
            print(f"    - r{c['from_round']}/{c['id']}: predicted {c['predicted']}, was {c['actual']}")
