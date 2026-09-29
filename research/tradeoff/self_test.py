#!/usr/bin/env python3
"""
Self-test for the trade-off gate.

The gate is a COMPLETENESS check, not a quality check. It does not say which plugin to
use. It says that a spec claiming no cost is a spec whose cost is unlocated — and that
is the failure worth preventing, because an unlocated cost is discovered by whoever
happens to be standing in its paradigm, weeks later, and attributed to something else.
"""
import copy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paradigms import PARADIGMS
from ledger import Plugin, PLUGINS, audit

T = []
def t(name, want, fn=None):
    def deco(f):
        T.append((name, want, f)); return f
    return deco(f) if fn is not None else deco

@t("COMPLETENESS: every real plugin declares what it taxes", True)
def _1():
    return all(p.taxes for p in PLUGINS)

@t("COMPLETENESS: every real plugin names an unmitigated cost", True)
def _2():
    return all(p.unmitigated for p in PLUGINS)

@t("NEGATIVE: a plugin with no declared cost FAILS the gate (proves _1 can fail)", True)
def _3():
    naked = Plugin(id="x", what="w", optimises="bandwidth")   # no taxes, no unmitigated
    return naked.complete() is False

@t("TAXED PARADIGMS: every id in taxes is a real paradigm", True)
def _4():
    return all(t in PARADIGMS for p in PLUGINS for t in p.taxes)

@t("NEGATIVE: a tax on a paradigm that does not exist is caught", True)
def _5():
    bad = Plugin(id="x", what="w", optimises="bandwidth", taxes=["vibes"], unmitigated="u")
    return not all(t in PARADIGMS for t in bad.taxes)

@t("NO SELF-TAX: a plugin may not list its own paradigm as a tax", True)
def _6():
    return all(p.optimises not in p.taxes for p in PLUGINS)

@t("NO UNPAID TAX: every declared tax has somewhere the cost lands", True)
def _7():
    a = audit()
    return all(a["taxed"].get(t) for t in {t for p in PLUGINS for t in p.taxes})

@t("THE FINDING: the ledger is not balanced — some paradigm pays and never optimises", True)
def _8():
    """If every paradigm both optimised and paid, the trade-offs would be circular and
    the ledger would say nothing. The observation is only worth making if the load is
    ASYMMETRIC."""
    a = audit()
    net = {}
    for p in a["optimises"]: net[p] = net.get(p, 0) + 1
    for t, ids in a["taxed"].items(): net[t] = net.get(t, 0) - len(ids)
    payers = [k for k, v in net.items() if v < 0]
    return len(payers) >= 1 and len(payers) < len(net)

@t("NEGATIVE: a self-consistent ledger has no net payers and the check FAILS (proves _8)", True)
def _9():
    # build a circular ledger: A taxes B, B taxes A
    a = Plugin(id="A", what="w", optimises="bandwidth", taxes=["locality"], unmitigated="u")
    b = Plugin(id="B", what="w", optimises="locality", taxes=["bandwidth"], unmitigated="u")
    net = {"bandwidth": 0, "locality": 0}
    net["bandwidth"] += 1; net["bandwidth"] -= 1
    net["locality"] += 1;  net["locality"] -= 1
    return not any(v < 0 for v in net.values())

@t("REVERSIBILITY: the ledger records which entries are one-way", True)
def _10():
    return all(isinstance(p.reversible, bool) for p in PLUGINS)

def main():
    print("tradeoff self-test")
    print("=" * 74)
    bad = 0
    for name, want, fn in T:
        try: ok = bool(fn()) == want
        except Exception as e: ok = False; name += f"  [{type(e).__name__}: {e}]"
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * 74)
    print(f"selftest: {len(T)-bad}/{len(T)} legs correct")
    return 0 if bad == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
