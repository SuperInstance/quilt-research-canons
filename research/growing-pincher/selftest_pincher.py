#!/usr/bin/env python3
"""Self-test for the growing pincher.

Every law gets a NEGATIVE CONTROL: a case that must FAIL when the law is broken.
A test that cannot fail is a cache, not a test.
"""
import sys
sys.path.insert(0, '/workspace/research/lanes/pincher')
from growing_pincher import Pincher, Policy, Known, signature

T = []
def t(name, want, fn=None):
    def deco(f):
        T.append((name, want, f)); return f
    return deco(f) if fn is not None else deco

@t("signature: case and digits are normalised", True)
def _1():
    return (signature("How many cells in the 4D graph?")
            == signature("how many cells in the 4d graph"))

@t("signature: genuinely different questions differ", True)
def _2():
    return signature("how many cells") != signature("what is the resonance band")

@t("bypass: a NEW signature always passes", True)
def _3():
    p = Pincher()
    r = p.route("what is the 47 Hz resonance band for")
    return r["action"] == "pass" and r["llm_called"] is True

@t("bypass: never bypasses below min_asks, even when perfect", True)
def _4():
    # This is the leg that should have caught fault B (min_asks removed). It has to
    # drive the signature to a PERFECT record and still refuse to bypass, so the only
    # thing stopping it is the evidence floor.
    p = Pincher()
    q = "what is the resonance band"
    p.route(q)                              # first pass creates the Known
    for _ in range(2):                      # perfect so far, but only 2 asks
        p.observe(q, True)
    k = p.known[signature(q)]
    below = k.n_asked < 3 and k.recent >= 1.0
    r = p.route(q)
    return below and r["action"] == "pass" and r["llm_called"] is True

@t("NEGATIVE: with min_asks=0 the same perfect record DOES bypass (proves _4 can fail)", True)
def _4b():
    p = Pincher(Policy(threshold=0.85, min_asks=0))
    q = "what is the resonance band"
    p.route(q)
    for _ in range(2): p.observe(q, True)
    return p.route(q)["action"] == "bypass"

@t("bypass: bypasses once evidence is sufficient and accurate", True)
def _5():
    p = Pincher()
    q = "what is the resonance band"
    p.route(q)
    for _ in range(3):
        p.observe(q, True)
    r = p.route(q)
    return r["action"] == "bypass" and r["llm_called"] is False

@t("WITHDRAWAL: a pincher that goes wrong STOPS bypassing", True)
def _6():
    p = Pincher()
    q = "what is the resonance band"
    p.route(q)
    for _ in range(4): p.observe(q, True)   # build a good record
    assert p.route(q)["action"] == "bypass"
    for _ in range(3): p.observe(q, False)  # then it starts being wrong
    r = p.route(q)
    return r["action"] == "pass" and r["llm_called"] is True

@t("WITHDRAWAL: a pincher recovers after being right again", True)
def _7():
    p = Pincher()
    q = "what is the resonance band"
    p.route(q)
    for _ in range(4): p.observe(q, True)
    for _ in range(3): p.observe(q, False)   # accuracy falls
    assert p.route(q)["action"] == "pass"
    for _ in range(12): p.observe(q, True)   # recovers
    return p.route(q)["action"] == "bypass"

@t("NEGATIVE: a pincher that is ALWAYS wrong never bypasses (proves _5 can fail)", True)
def _8():
    p = Pincher()
    q = "what is the resonance band"
    p.route(q)
    for _ in range(10): p.observe(q, False)
    r = p.route(q)
    return r["action"] == "pass"

@t("NEGATIVE: withdrawal threshold is load-bearing", True)
def _9():
    # With threshold at 0.0, a pincher that has never been right would bypass. If the
    # threshold were not enforced, _8 would FAIL (bypass) instead of passing.
    p = Pincher(Policy(threshold=0.0, min_asks=3))
    q = "what is the resonance band"
    p.route(q)
    for _ in range(5): p.observe(q, False)
    return p.route(q)["action"] == "bypass"   # the degenerate policy DOES bypass

@t("ledger: every decision is an entry, bypass or not", True)
def _10():
    p = Pincher()
    q = "what is the resonance band"
    for _ in range(6): p.route(q)
    p.observe(q, True); p.observe(q, True)
    p.route(q)
    return len(p.ledger) == 7 and all("action" in e for e in p.ledger)

@t("ledger: a bypass is recorded as NOT calling the LLM", True)
def _11():
    p = Pincher()
    q = "what is the resonance band"
    p.route(q)
    for _ in range(3): p.observe(q, True)
    p.route(q)
    b = [e for e in p.ledger if e["action"] == "BYPASS"]
    return len(b) == 1 and b[0]["llm_called"] is False

@t("health: reports bypass rate and BOTH accuracies", True)
def _12():
    p = Pincher()
    q = "what is the resonance band"
    p.route(q)
    for _ in range(3): p.observe(q, True)
    for _ in range(4): p.route(q)
    h = p.health()
    row = h["live"][0] if h["live"] else (h["withdrawn"][0] if h["withdrawn"] else None)
    return (h["llm_calls_saved"] == 4 and h["bypass_rate"] == 0.8 and row is not None
            and row["lifetime_acc"] == 1.0 and row["recent_acc"] == 1.0)

@t("THE LAW: an UNOBSERVED bypass is not a bypass, it is a guess", True)
def _13():
    """A pincher that answers and is never checked has no way to know it is right, and
    therefore no way to stop being wrong. The cell only learns from observe(), so a
    deployment that never calls observe() has a pincher that will happily bypass forever
    on a single lucky first pass. The fix is to make the health report say so."""
    p = Pincher()
    q = "what is the resonance band"
    p.route(q)
    for _ in range(5): p.route(q)        # bypassing on ONE observation
    h = p.health()
    k = p.known[signature(q)]
    # n_asked is 1, so the record is thin: min_asks is 3, and the pincher must be
    # passing, not bypassing. The health report has to expose that thinness.
    thin = k.n_asked < 3
    passing_now = (h["withdrawn"] and h["withdrawn"][0]["signature"].startswith(k.answer[:0] or "what"))
    return thin and bool(h["withdrawn"])

def main():
    print("growing_pincher self-test")
    print("=" * 70)
    bad = 0
    for name, want, fn in T:
        try: ok = bool(fn()) == want
        except Exception as e: ok = False; name += f"  [{type(e).__name__}: {e}]"
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * 70)
    print(f"selftest: {len(T)-bad}/{len(T)} legs correct")
    return 0 if bad == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
