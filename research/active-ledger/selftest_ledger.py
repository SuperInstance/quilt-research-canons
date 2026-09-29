#!/usr/bin/env python3
"""Self-test for the ActiveLedger.

The anti-GAN discipline: a discipline that only ever produces passing results is a
GAN with extra steps. Every law here gets a NEGATIVE CONTROL — a case that must FAIL.
A test that cannot fail is not a test.
"""
import sys
sys.path.insert(0, '/workspace/research/lanes/ledger')
from active_ledger import (Ledger, Unit, Plane, Pipeline, Route, FilterVerdict,
                           UnknownUnit, IncompatibleContext)

T = []
def t(name, want):
    def deco(fn):
        T.append((name, want, fn)); return fn
    return deco

@t("double-entry: a post produces a pair", True)
def _1():
    l = Ledger('a'); u = Unit('m','a')
    x, y = l.post(plane='p', to_cell='b', quantity='q', value=1.0, unit=u)
    return x.contra == y.id and y.contra == x.id and len(l.entries) == 2

@t("double-entry: balance detects an unpaired side", True)
def _2():
    l = Ledger('a'); u = Unit('m','a')
    x, y = l.post(plane='p', to_cell='b', quantity='q', value=1.0, unit=u)
    del l.entries[y.id]                       # tear out one side
    return l.balance()['balanced'] is False and l.balance()['unpaired'] == [x.id]

@t("double-entry: balance detects a twin pointing elsewhere", True)
def _3():
    l = Ledger('a'); u = Unit('m','a')
    x, y = l.post(plane='p', to_cell='b', quantity='q', value=1.0, unit=u)
    l.entries[y.id].contra = 'nowhere'          # corrupt the link
    return l.balance()['balanced'] is False

@t("units: a conversion is refused rather than guessed", True)
def _4():
    l = Ledger('a')
    l.define(Unit('c','a', to_owner_base=1.0))
    # asking a->a works
    assert l.translate('t', Unit('c','a'), 'a') == (1.0, 0.0, False)
    # asking a->b with no route raises
    try:
        l.translate('t', Unit('c','a'), 'b'); return False
    except UnknownUnit:
        return True

@t("units: a conditional conversion refuses out-of-context", True)
def _5():
    l = Ledger('a')
    l.define(Unit('c','a', to_owner_base=1.0, condition='in-water'))
    # in-context it works
    assert l.translate('t', Unit('c','a', condition='in-water'), 'a', context='in-water')
    # out of context it must refuse, and refuse SPECIFICALLY (IncompatibleContext, not a
    # generic miss) so a caller can tell "no route" from "wrong conditions"
    try:
        l.translate('t', Unit('c','a', condition='in-water'), 'a', context='in-air')
        return False
    except IncompatibleContext:
        return True
    except UnknownUnit:
        return False

@t("planes: entries are separated by plane, not merged", True)
def _6():
    l = Ledger('a'); u = Unit('hz','a')
    l.post(plane='structural', to_cell='s', quantity='v', value=47.0, unit=u)
    l.post(plane='acoustic',   to_cell='s', quantity='v', value=0.0,  unit=u)
    return len(l.plane_view('structural')) == 2 and len(l.plane_view('acoustic')) == 2

@t("planes: the same value reads differently per plane — THE LAW", True)
def _7():
    l = Ledger('a'); u = Unit('hz','a')
    l.post(plane='structural', to_cell='s', quantity='v', value=47.0, unit=u)
    l.post(plane='acoustic',   to_cell='s', quantity='v', value=0.0,  unit=u)
    s = {e.plane: e.value for e in l.entries.values() if e.cell_from == 'a'}
    return s['structural'] == 47.0 and s['acoustic'] == 0.0

@t("pipeline: a filter that blocks sends NOTHING across the gate to the STT cell", True)
def _8():
    p = Pipeline(Route('r'))
    for c in ['mic','filter','stt','llm']: p.add(c)
    p.filter_verdict(FilterVerdict('filter','noise',0.94,False,'below band'))
    # nothing may arrive at stt from the filter when the gate is closed
    arrivals = [e for e in p.ledgers['stt'].entries.values()
                if e.cell_from == 'filter' and e.cell_to == 'stt']
    return len(arrivals) == 0

@t("pipeline: a filter that passes carries a nonzero reading", True)
def _9():
    p = Pipeline(Route('r'))
    for c in ['mic','filter','stt']: p.add(c)
    p.filter_verdict(FilterVerdict('filter','speech',0.81,True,'speech-band energy'))
    v = [x for x in p.verdicts if x.decision == 'speech'][0]
    return v.passed_through and v.confidence > 0.7

@t("NEGATIVE: an unblocked noise signal MUST cross to the STT cell (proves _8 can fail)", True)
def _10():
    # Same pipeline, gate OPEN. If _8's mechanism were "nothing ever reaches stt" this
    # would fail and expose _8 as vacuous.
    p = Pipeline(Route('r'))
    for c in ['mic','filter','stt']: p.add(c)
    p.filter_verdict(FilterVerdict('filter','noise',0.94,True,'high band, resembles speech'))
    # double-entry: the post lands BOTH sides in the stt ledger (the from-side and
    # its mirror), so there are two entries, exactly one of which is the forward hop
    entries = [e for e in p.ledgers['stt'].entries.values()
               if 'filter' in (e.cell_from, e.cell_to) and 'stt' in (e.cell_from, e.cell_to)]
    forward = [e for e in entries if e.cell_from == 'filter' and e.cell_to == 'stt']
    mirror  = [e for e in entries if e.cell_from == 'stt' and e.cell_to == 'filter']
    return len(forward) == 1 and forward[0].value == 1.0 and len(mirror) == 1

@t("synoptic: shows the reading, not the arithmetic", True)
def _11():
    l = Ledger('c'); u = Unit('hz','c')
    l.post(plane='structural', to_cell='s', quantity='v', value=47.0, unit=u)
    txt = l.synoptic()
    return '47.0000' in txt and 'structural' in txt

@t("NEGATIVE: a corrupted balance DOES surface in the synoptic view", True)
def _12():
    l = Ledger('c'); u = Unit('hz','c')
    x, y = l.post(plane='p', to_cell='s', quantity='v', value=1.0, unit=u)
    l.entries[y.id].contra = 'nowhere'
    return 'balanced: False' in l.synoptic()

def main():
    print("ActiveLedger self-test")
    print("=" * 66)
    bad = 0
    for name, want, fn in T:
        try:
            ok = bool(fn()) == want
        except Exception as e:
            ok = False
            name += f"  [{type(e).__name__}: {e}]"
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * 66)
    print(f"selftest: {len(T)-bad}/{len(T)} legs correct")
    return 0 if bad == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
