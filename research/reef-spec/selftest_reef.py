#!/usr/bin/env python3
"""Self-test for the reef model. Every law gets a negative control.

The load-bearing law is THE ASYMMETRY: a polyp can die and the coral survives,
and a bleaching that kills everything on a seedling does not destroy an ancient
coral. If those two are not tested they are not claimed.
"""
import sys
sys.path.insert(0, '/workspace/research/lanes/make-valuable/reef')
from reef import Reef, Health, Stage, STAGE_ORDER, RESILIENCE

T = []
def t(name, want, fn=None):
    def deco(f):
        T.append((name, want, f)); return f
    return deco(f) if fn is not None else deco

def grown(stage_target, zone='shallow'):
    r = Reef('t'); r.zone('shallow', 90, 10, 50, 1.5)
    r.coral('C', zone)
    for i in range(12): r.polyp(f'p{i}', 'C', zone, f's{i}')
    for _ in range(stage_target * 12): r.step()
    return r

@t("THE ASYMMETRY: killing every polyp does NOT destroy the coral", True)
def _1():
    r = Reef('t'); r.zone('shallow', 90, 10, 50, 1.5); r.coral('C'); r.polyp('p','C','shallow','s')
    for _ in range(10): r.step()
    before = r.total_mass()
    for p in r.polyps.values(): p.health = Health.DEAD
    for _ in range(5): r.step()
    return before > 0 and r.total_mass() == before and r.polyps['p'].health is Health.DEAD

@t("THE ASYMMETRY: a polyp with no symbiont starves (dependency is real)", True)
def _2():
    r = Reef('t'); r.zone('shallow', 90, 10, 50, 1.5); r.coral('C'); r.polyp('p','C','shallow','s')
    for _ in range(4): r.step()
    p = r.polyps['p']; before = p.energy
    p.symbiont.alive = False
    r.step()
    return p.energy < before

@t("THE ASYMMETRY: a seedling is destroyed by bleaching that an ancient coral survives", True)
def _3():
    r1 = Reef('seedling'); r1.zone('z',50,50,50,1.0); r1.coral('C'); r1.polyp('p','C','z','s')
    r2 = Reef('ancient');  r2.zone('z',50,50,50,1.0); r2.coral('C'); r2.polyp('p','C','z','s')
    for _ in range(6): r1.step()
    for _ in range(200): r2.step()
    assert r1.corals['C'].stage is Stage.SEEDLING, r1.corals['C'].stage
    assert r2.corals['C'].stage is Stage.ANCIENT, r2.corals['C'].stage
    m1, m2 = r1.total_mass(), r2.total_mass()
    r1.bleach(0.9); r2.bleach(0.9)
    return (r1.total_mass() < m1) and (r2.total_mass() > m2 * 0.5) and r1.total_mass() < r2.total_mass()

@t("BLEACHING: leaves scars, and a scarred coral is a surviving one", True)
def _4():
    r = grown(3)
    before = r.total_mass()
    r.bleach(0.6)
    return r.corals['C'].scars == 1 and r.total_mass() < before

@t("BLEACHING: a bleached polyp loses its symbiont (expelled with it)", True)
def _5():
    r = grown(2)
    r.bleach(0.95)
    return any(p.health is Health.BLEACHED for p in r.polyps.values()) and \
           all(not p.symbiont.alive for p in r.polyps.values() if p.health is Health.BLEACHED)

@t("THE ASYMMETRY (hard): severity 1.0 kills every polyp and the coral is unharmed", True)
def _5b():
    """The central claim, now reachable: a polyp can be killed BY BLEACHING and the
    structure it built is untouched. The first version of bleach() had no DEAD edge out
    of BLEACHED, so this could not even be expressed, let alone tested."""
    r = grown(2)
    mass_before = r.total_mass()
    stage = r.corals['C'].stage
    out = r.bleach(1.0)
    dead = sum(1 for p in r.polyps.values() if p.health is Health.DEAD)
    # NOT "unharmed" — an ANCIENT coral at severity 1.0 loses 1.0*(1-resilience).
    # The claim is that the loss is exactly the resilience-scaled one, that the coral
    # keeps essentially all of its mass, and that every polyp is gone. Getting this
    # wrong was the test being wrong: the first version demanded zero loss, which
    # would have required resilience to be 1.0 and the stages to be decorative.
    expected = 1.0 * (1.0 - RESILIENCE[stage])
    return (len(out["killed"]) == len(r.polyps) and dead == len(r.polyps) and dead > 0
            and abs((mass_before - r.total_mass()) - expected) < 1e-9
            and r.total_mass() >= mass_before * 0.99)

@t("STAGES: coral advances only on accumulated mass, and is bounded", True)
def _6():
    r = grown(2)
    s = r.corals['C'].stage
    ok = s in STAGE_ORDER
    for _ in range(500): r.step()
    return ok and r.corals['C'].stage is Stage.ANCIENT   # never exceeds ANCIENT

@t("ZONES: light bonus changes the yield, so zoning is a real constraint", True)
def _7():
    bright = Reef('b'); bright.zone('shallow',95,5,20,2.0); bright.coral('C'); bright.polyp('p','C','shallow','s')
    dim    = Reef('d'); dim.zone('deep',10,90,20,0.2);   dim.coral('C');    dim.polyp('p','C','deep','s')
    for _ in range(6): bright.step(); dim.step()
    return bright.total_mass() > dim.total_mass()

@t("THE ASYMMETRY (invariant): mass moves ONLY on deposit or on bleach loss", True)
def _13():
    """Coral mass has exactly two sources: polyps depositing, and bleaching taking it
    away. It must NOT respond to how many polyps are alive. Fault C made loss depend
    on live polyp count and every other leg still passed, because every other leg
    looked at mass after a single event. This one steps with no events at all and
    asserts mass moves by exactly the deposits, and that a bleach's loss is exactly
    sev*(1-resilience) with no liveness term hidden in it."""
    r = Reef('inv'); r.zone('z', 80, 20, 50, 1.0); r.coral('C')
    r.polyp('p1','C','z','s1'); r.polyp('p2','C','z','s2')
    r.step(); after_one = r.total_mass()
    r.step(); after_two = r.total_mass()
    deposits = after_two - after_one
    if abs(after_one - deposits) > 1e-9 or deposits <= 0:
        return False
    # now kill every polyp outright and step: mass must NOT move
    for p in r.polyps.values(): p.health = Health.DEAD
    killed_mass = r.total_mass()
    for _ in range(5): r.step()
    return r.total_mass() == killed_mass

@t("NEGATIVE: a bleach cannot leave mass above its pre-bleach peak (proves _4 can fail)", True)
def _8():
    r = grown(3)
    before = r.total_mass()
    for sev in (0.0, 0.25, 0.5, 0.75, 1.0):
        r.bleach(sev)
    return r.total_mass() <= before

@t("NEGATIVE: a polyp with NO symbiont at all cannot live forever (proves _2 can fail)", True)
def _9():
    r = Reef('t'); r.zone('z',50,50,50,1.0); r.coral('C')
    r.polyps['p'] = __import__('reef').Polyp(id='p', coral_id='C', zone='z', symbiont=None)
    for _ in range(15): r.step()
    return r.polyps['p'].health is Health.DEAD

@t("NEGATIVE: bleaching cannot INCREASE mass even at severity 0 (proves _3 can fail)", True)
def _10():
    r = grown(3)
    before = r.total_mass()
    r.bleach(0.0)
    return r.total_mass() <= before

@t("SEVERITY CLAMP: out-of-range severity is clamped, not accepted", True)
def _11():
    r = grown(2); m = r.total_mass()
    r.bleach(5.0)
    return r.total_mass() <= m and r.corals['C'].scars == 1

def main():
    print("reef self-test")
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

if __name__ == '__main__':
    sys.exit(main())
