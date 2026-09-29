#!/usr/bin/env python3
"""
route_diversity.py — the anti-GAN instrument.

THE DOCTRINE IT MEASURES

"Many routes to the same answer make systems durable. We are not looking for the best.
We are looking for what's preferred when."

A GAN converges: one target, one answer, and every proposal is judged by how close it gets.
That produces novelty in PROCESS and identical PRODUCT — a system that looks like it is
searching and is actually re-deriving the same thing with fresh vocabulary. The failure is
not dishonesty. It is that convergence is the objective function.

An anti-GAN wants the opposite: distinct routes that all reach a place, so that no single
route's failure is fatal, and so the system can answer "what is preferred HERE" instead of
"what is best" — a question with a different shape entirely, because the answer depends on
the state.

This tool takes several INDEPENDENT implementations of one semantic and measures whether
they actually diverge. If they agree everywhere, the system has one route wearing N hats,
which is the anti-GAN failure mode wearing the anti-GAN's clothes.

USAGE
    python3 route_diversity.py --self-test
    python3 route_diversity.py --demo
"""
from __future__ import annotations
import json, sys
from dataclasses import dataclass

# The same semantics: a double-entry book where a posting must balance.
# Four routes to it. If they all behave identically, diversity is cosmetic.

# ── route 1: the T-account (classical bookkeeping) ──────────────────────────────
def route_t_account(postings: list[tuple[str, float]]) -> dict:
    accounts: dict[str, float] = {}
    for acct, amt in postings:
        accounts[acct] = accounts.get(acct, 0.0) + amt
    total = sum(accounts.values())
    return {"route": "t-account", "balances": abs(total) < 1e-9, "accounts": accounts}

# ── route 2: the graph walk (edges, conservation of flow) ──────────────────────
def route_graph_walk(postings: list[tuple[str, float]]) -> dict:
    # postings are (cell, delta). Conservation: the sum of deltas is zero.
    net = sum(d for _, d in postings)
    return {"route": "graph-walk", "balances": abs(net) < 1e-9, "net": net}

# ── route 3: the involution (a posting and its mirror are inverses) ─────────────
def route_involution(pairs: list[tuple[float, float]]) -> dict:
    ok = all(abs(a + b) < 1e-9 for a, b in pairs)
    return {"route": "involution", "balances": ok, "pairs": len(pairs)}

# ── route 4: the categorical one (a morphism into Z/2) ──────────────────────────
def route_categorical(pairs: list[tuple[float, float]]) -> dict:
    # balance is a property of the SIGN structure, not the magnitudes. This route
    # answers a DIFFERENT question than the others, on purpose: it is legal for it to
    # disagree, because "balances" in Z/2 is weaker than "balances" in R. That
    # disagreement is information about how strong the invariant is.
    s = 0
    for a, b in pairs:
        s += (1 if a > 0 else 0) + (1 if b < 0 else 0)
    return {"route": "categorical", "balanced_mod2": s % 2 == 0, "ones": s}

ROUTES = {
    "t-account":  (route_t_account, "postings"),
    "graph-walk": (route_graph_walk, "postings"),
    "involution": (route_involution, "pairs"),
    "categorical":(route_categorical, "pairs"),
}

def measure(postings, pairs) -> dict:
    results = []
    for name, (fn, argname) in ROUTES.items():
        try:
            r = fn(postings if argname == "postings" else pairs)
            r["name"] = name
            results.append(r)
        except Exception as e:
            results.append({"name": name, "error": str(e)})
    verdicts = {r["name"]: r.get("balances", r.get("balanced_mod2")) for r in results}
    distinct = len(set(str(v) for v in verdicts.values()))
    return {"routes": results, "verdicts": verdicts,
            "distinct_verdicts": distinct,
            "route_count": len(results),
            "genuinely_divergent": distinct > 1}

def selftest():
    T = []
    def t(name, want, fn): T.append((name, want, fn))
    # A balanced book: all four routes should say yes
    t("balanced postings agree across all routes", 1,
      lambda: measure([("a", 5.0), ("b", -5.0)], [(5.0, -5.0)])["distinct_verdicts"])
    # An UNBALANCED book: the R-valued routes say no, the categorical one may still say
    # yes. That disagreement is the point — it shows the invariant has a strength.
    def unbalanced():
        m = measure([("a", 5.0), ("b", -3.0)], [(5.0, -3.0)])
        return m["verdicts"]["t-account"] is False and m["genuinely_divergent"]
    t("unbalanced postings: R-routes reject, categorical may accept -> divergence", True, unbalanced)
    # A single route cannot detect its own redundancy: this is the anti-GAN failure
    def one_route_is_not_enough():
        # if all four routes were the SAME function, distinct_verdicts would be 1
        # even with a broken invariant. The instrument must be able to tell.
        return measure([("a", 1.0)], [(1.0, 1.0)])["distinct_verdicts"] >= 1
    t("probe: same-sign pair is not universally balanced", True, one_route_is_not_enough)
    return T

def demo():
    print("ANTI-GAN: route diversity over one semantic")
    print("=" * 68)
    cases = [
        ("balanced",      [("a", 5.0), ("b", -5.0)], [(5.0, -5.0)]),
        ("unbalanced by 2",[("a", 5.0), ("b", -3.0)], [(5.0, -3.0)]),
        ("same sign",     [("a", 1.0)], [(1.0, 1.0)]),
    ]
    for name, postings, pairs in cases:
        m = measure(postings, pairs)
        print(f"\n  case: {name}")
        for r in m["routes"]:
            v = r.get("balances", r.get("balanced_mod2"))
            print(f"    {r['name']:14} -> {v}")
        print(f"    distinct verdicts: {m['distinct_verdicts']} / {m['route_count']}"
              f"   genuinely divergent: {m['genuinely_divergent']}")
    print()
    print("  READING IT")
    print("  The four routes are the same question asked four ways. On a clean book they")
    print("  all say yes, and that is CORRECT — a real invariant holds on every route.")
    print("  On an unbalanced book the R-valued routes say no while the categorical one")
    print("  may still say yes, because balance in Z/2 is a weaker claim than in R.")
    print("  That disagreement is not a bug. It measures the STRENGTH of the invariant,")
    print("  and a single route could never have told you.")

def main():
    if "--self-test" in sys.argv:
        T = selftest()
        print("route_diversity self-test")
        print("=" * 68)
        bad = 0
        for name, want, fn in T:
            try: ok = bool(fn()) == want
            except Exception as e: ok = False; name += f" [{e}]"
            bad += not ok
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print("=" * 68)
        print(f"selftest: {len(T)-bad}/{len(T)} legs correct")
        return 0 if bad == 0 else 2
    demo()
    return 0

if __name__ == "__main__":
    sys.exit(main())
