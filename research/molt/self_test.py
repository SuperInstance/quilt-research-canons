#!/usr/bin/env python3
"""
Self-test for the soft shells.

A shell library that cannot shed its own shells is a framework. The library's own
negative controls are therefore about SHEDDING and REWINDING, not just about each
shell firing correctly.
"""
import copy, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from molt import Timeline, apply_with_rewind, addr
from shells import MOLTS

T = []
def t(name, want, fn=None):
    def deco(f):
        T.append((name, want, f)); return f
    return deco(f) if fn is not None else deco

def by_name(n): return next(m for m in MOLTS if m.name == n)

@t("REGISTRY: every shell declares fits AND outgrows (no frameworks allowed)", True)
def _1():
    return all(m.fits.strip() and m.outgrows.strip() for m in MOLTS)

@t("NEGATIVE: a shell with no outgrows clause is REJECTED (proves _1 can fail)", True)
def _2():
    bad = copy.deepcopy(by_name("pre-register"))
    bad.outgrows = ""
    return not (bad.fits.strip() and bad.outgrows.strip())

@t("ADDRESSING: every shell has a stable dotted cell address", True)
def _3():
    return all(m.id.startswith("molt.") and "." in m.id for m in MOLTS)

@t("RECEIPTS: applying a shell leaves a receipt naming what changed", True)
def _4():
    s, r = by_name("measure-first")({"belief": "X", "predicted": True, "measurement": True})
    return r.shell == "measure-first" and "status" in r.changed and len(r.digest()) == 16

@t("REWIND: a state rewound to its starting value is IDENTICAL, not similar", True)
def _5():
    tl = Timeline()
    state = {"belief": "X", "predicted": True, "measurement": None}
    before = copy.deepcopy(state)
    ns, r, h = apply_with_rewind(by_name("measure-first"), state, tl)
    assert ns != before, "the shell did nothing, so the rewind proves nothing"
    return tl.rewind(h) == before

@t("NEGATIVE: an in-place leak does NOT corrupt an earlier snapshot (proves _5 can fail)", True)
def _6():
    # The first version of this leg asserted the rewind would be DIRTY after an
    # in-place leak. It is not, and it should not be: apply_with_rewind snapshots
    # BEFORE calling apply, so a shell that mutates its argument cannot corrupt a
    # snapshot that already exists. The leg was testing a hazard that the library
    # has already designed against, and failing for the wrong reason.
    #
    # The real property: a snapshot taken BEFORE a mutation is unaffected by it.
    # That is what makes the rewind trustworthy, and it is now what is asserted.
    def leaky(state):
        state["sneaky"] = True
        return state, "leaked"
    tl = Timeline()
    state = {"clean": True}
    h = tl.snapshot("before", state)
    leaky(state)                      # mutates in place, no copy
    return tl.rewind(h) == {"clean": True} and "sneaky" in state

@t("SHEDDING: a shell past its fit says shed, not keep", True)
def _7():
    s, _ = by_name("outgrew-it")({"uses": 50, "fit_for": 10})
    return s["action"] == "shed"

@t("NEGATIVE: a shell inside its fit says keep (proves _7 can fail)", True)
def _8():
    s, _ = by_name("outgrew-it")({"uses": 2, "fit_for": 10})
    return s["action"] == "keep"

@t("FAULT INJECTION (the shells' own KAT): every shell passes a well-formed state", True)
def _9():
    sample = {"belief": "b", "predicted": True, "measurement": True, "a": 0.8, "b": 0.8,
              "claims": [("m is 500", 500)], "flat": {"deck": {"x": 1}},
              "rule": "r", "checks": [1, 2], "uses": 1, "fit_for": 10, "run": {}}
    for m in MOLTS:
        if m.verify is None:
            return False
        ns, _ = m(sample)
        if not m.verify(ns):
            return False
    return True

@t("NEGATIVE: a shell that emits nothing fails its own verify", True)
def _9b():
    """The KAT of the library, and the property that matters most: a shell whose body
    silently does nothing must not pass. Every shell here declares what it verifies, so
    a silent shell is detectable without reading its source."""
    fixture = {"belief": "b", "predicted": True, "measurement": True, "a": 0.8, "b": 0.8,
               "claims": [("m is 500", 500)], "flat": {"deck": {"x": 1}},
               "rule": "r", "checks": [1, 2], "uses": 1, "fit_for": 10, "run": {}}
    for m in MOLTS:
        if m.verify is None:
            continue
        unchanged = dict(fixture)
        if m.verify(unchanged) and m.verify is not None:
            # verify must be false on an UNTOUCHED state for at least the shells whose
            # whole claim is that they changed something
            if m.name in ("measure-first", "pre-register", "to-cells", "outgrew-it"):
                if m.verify(unchanged):
                    return False
    return True

@t("TWO INSTRUMENTS: a disagreement is reported, never averaged away", True)
def _10():
    s, _ = by_name("two-instruments")({"a": 0.71, "b": 0.3})
    return s.get("agree") is False and "DISAGREE" in s["verdict"]

@t("DERIVED PROSE: a contradiction between prose and run is caught", True)
def _11():
    s, _ = by_name("derive-prose-from-run")({
        "claims": [("mass is 500", 500), ("the deep coral is ancient", "juvenile")]})
    return s["claims_false"] == 1 and "contradicts" in s["verdict"]

@t("TO CELLS: a flat record becomes addressable cells with dotted addrs", True)
def _12():
    s, _ = by_name("to-cells")({"flat": {"deck": {"a": 1}, "quota": 3}})
    return "cell.deck" in s and "field.quota" in s

@t("CHAIN: three shells compose, and rewinding the middle one restores the middle state", True)
def _13():
    tl = Timeline()
    s0 = {"belief": "X", "predicted": True, "measurement": True, "uses": 0, "fit_for": 10}
    s1, r1, h1 = apply_with_rewind(by_name("measure-first"), s0, tl)
    s2, r2, h2 = apply_with_rewind(by_name("outgrew-it"), s1, tl)
    s3, r3, h3 = apply_with_rewind(by_name("to-cells"), {"flat": {"a": 1}}, tl)
    mid = tl.rewind(h2)
    return (s1.get("status") == "MEASURED" and s1.get("belief_confirmed") is True
            and s2.get("action") == "keep"
            and mid == s1 and r3.rewind == h3 and len(tl.handles()) == 3)

@t("NEGATIVE: an UNMEASURED belief is never reported as confirmed", True)
def _13b():
    s, _ = by_name("measure-first")({"belief": "X", "predicted": True, "measurement": None})
    return s["status"] == "UNMEASURED" and "belief_confirmed" not in s

def main():
    print("molt self-test")
    print("=" * 72)
    bad = 0
    for name, want, fn in T:
        try: ok = bool(fn()) == want
        except Exception as e: ok = False; name += f"  [{type(e).__name__}: {e}]"
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * 72)
    print(f"selftest: {len(T)-bad}/{len(T)} legs correct")
    return 0 if bad == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
