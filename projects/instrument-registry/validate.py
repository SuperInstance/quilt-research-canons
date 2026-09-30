#!/usr/bin/env python3
"""validate.py — the registry must be able to FAIL.

A registry that only records what is known is decoration. This asserts four things,
and the first is the one that matters:

  1. An instrument declared `characterised` MUST name a KAT. An instrument with no
     test is a claim with a receipt attached.
  2. A `characterised` instrument must carry a `known_failure` or state that none is
     known. Silence is not the same as absence.
  3. Every `failure_class` must be one of the three declared classes. A new failure
     shape is a new row in the taxonomy, not a free-text escape hatch.
  4. BROKEN instruments may not be listed as having a passing KAT. A broken instrument
     whose KAT passes is worse than one with no KAT, because it has been trusted.

Exit 0 clean, exit 2 on any violation, with every violation named. A crash raises
rather than reporting clean - the failure mode this whole project keeps hitting is a
check that can only pass.
"""
import json, sys, os
from collections import Counter

VALID_CLASSES = {"context_starved", "context_saturated", "uncharacterised"}
BROKEN, CHARACTERISED = "BROKEN", "characterised"

def validate(reg: dict) -> list:
    v = []
    insts = reg.get("instruments", [])
    if not insts: v.append("registry has no instruments")
    ids = [i.get("id") for i in insts]
    dupes = [k for k, n in Counter(ids).items() if n > 1]
    for d in dupes: v.append(f"duplicate id: {d}")

    for i in insts:
        iid = i.get("id", "<no id>")
        cls = i.get("class")
        fc  = i.get("failure_class")
        if cls not in (BROKEN, CHARACTERISED, "characterised-partial", "proposed"):
            v.append(f"{iid}: unknown class {cls!r}")
        if cls == CHARACTERISED:
            if not i.get("kat"):
                v.append(f"{iid}: declared CHARACTERISED but names no KAT - "
                         f"a characterisation claim with no test is a receipt with nothing behind it")
            if i.get("kat_result") in ("PASS",) and not i.get("evidence"):
                v.append(f"{iid}: KAT passed but no evidence pointer")
        if cls == BROKEN:
            if i.get("kat_result") == "PASS":
                v.append(f"{iid}: BROKEN yet its KAT reports PASS - a broken instrument that "
                         f"passed its own control is the most dangerous state to be in")
            if not i.get("known_failure"):
                v.append(f"{iid}: BROKEN but states no known failure")
            if fc is None:
                v.append(f"{iid}: BROKEN but carries no failure_class")
        if fc is not None and fc not in VALID_CLASSES:
            v.append(f"{iid}: failure_class {fc!r} is not one of {sorted(VALID_CLASSES)}")
        if "known_failure" not in i:
            v.append(f"{iid}: missing known_failure key entirely (use null with an explicit "
                     f"'none measured' note, do not omit it)")
    return v

def selftest() -> int:
    base = json.load(open(os.path.join(os.path.dirname(__file__), "instruments.json")))
    legs = []
    def leg(name, mutate, must_fail):
        r = json.loads(json.dumps(base)); mutate(r)
        errs = validate(r)
        got = len(errs) > 0
        legs.append((name, got == must_fail, errs[:1]))
        return got

    leg("pristine registry is clean",            lambda r: None, False)
    leg("characterised without a KAT is caught",  lambda r: r["instruments"][0].__setitem__("kat", None), True)
    leg("broken-with-passing-KAT is caught",     lambda r: r["instruments"][2].__setitem__("kat_result","PASS"), True)
    leg("bogus failure_class is caught",         lambda r: r["instruments"][1].__setitem__("failure_class","vibes"), True)
    leg("duplicate id is caught",                lambda r: r["instruments"].append(r["instruments"][0]), True)
    def drop(r): r["instruments"][3].pop("known_failure", None)
    leg("omitted known_failure is caught",       drop, True)

    print(f"  self-test {sum(1 for _,ok,_ in legs if ok)}/{len(legs)}")
    for n, ok, e in legs:
        print(f"    {'ok  ' if ok else 'FAIL'} {n}" + (f"  -> {e[0][:70]}" if not ok and e else ""))
    return 0 if all(ok for _, ok, _ in legs) else 2

if __name__ == "__main__":
    if "--self-test" in sys.argv: sys.exit(selftest())
    reg = json.load(open(os.path.join(os.path.dirname(__file__), "instruments.json")))
    errs = validate(reg)
    c = Counter(i["class"] for i in reg["instruments"])
    print(f"  {len(reg['instruments'])} instruments: {dict(c)}")
    for e in errs: print(f"  VIOLATION  {e}")
    print("  REGISTRY CLEAN" if not errs else f"  {len(errs)} VIOLATION(S)")
    sys.exit(0 if not errs else 2)
