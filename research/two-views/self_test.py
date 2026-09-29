#!/usr/bin/env python3
"""
Self-test for the two-view substrate and the page that renders it.

The claim under test: the human view and the agent view are generated from the same
cells in the same pass, so they CANNOT drift. A test that does not attack that with a
deliberate disagreement proves nothing.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from view import Substrate

HERE = os.path.dirname(os.path.abspath(__file__))
T = []
def t(name, want, fn=None):
    def deco(f):
        T.append((name, want, f)); return f
    return deco(f) if fn is not None else deco

def demo_substrate():
    s = Substrate()
    s.bind('a', 1, 'n', 'seed'); s.bind('b', 2, 'n', 'seed')
    s.link('a', 'b', 'n', 'wire'); s.effect('a', 3, 'n', 'eff'); s.tick('t1')
    return s

@t("VIEWS AGREE: both projections list the same cells at every frame", True)
def _1():
    s = demo_substrate()
    for n in range(len(s.frames)):
        h, a = s.project_human(n), s.project_agent(n)
        if [r['cell'] for r in h['rows']] != [c['addr'] for c in a['cells']]:
            return False
    return True

@t("NEGATIVE: if one view is edited, the check FAILS (proves _1 can fail)", True)
def _2():
    s = demo_substrate()
    h = s.project_human(4)
    h['rows'].append({"cell": "ghost", "kind": "leaf", "op": "BIND", "value": 0,
                      "receipt": "x", "age": 0, "note": ""})
    a = s.project_agent(4)
    return [r['cell'] for r in h['rows']] != [c['addr'] for c in a['cells']]

@t("RECEIPTS: every cell carries a receipt", True)
def _3():
    h = demo_substrate().project_human(4)
    return all(r['receipt'] for r in h['rows'])

@t("RECEIPT STABILITY: a cell's receipt does not change as other cells move", True)
def _4():
    s = demo_substrate()
    a = s.project_human(3)
    ra = {r['cell']: r['receipt'] for r in a['rows']}
    s.effect('b', 99, 'changed', 'eff')
    b = s.project_human(len(s.frames)-1)
    rb = {r['cell']: r['receipt'] for r in b['rows']}
    return ra['a'] == rb['a']   # 'a' was not touched, so its receipt must be identical

@t("RECEIPT SENSITIVITY: changing a cell's value changes ITS receipt", True)
def _5():
    s = Substrate()
    s.bind('x', 1)
    r1 = s.view('x').receipt
    s.effect('x', 2)
    r2 = s.view('x').receipt
    return r1 != r2

@t("REWIND: an earlier frame has strictly fewer cells", True)
def _6():
    s = demo_substrate()
    return len(s.project_human(0)['rows']) < len(s.project_human(4)['rows'])

@t("NEGATIVE: rewind past the end raises (proves _6 is not vacuous)", True)
def _7():
    s = demo_substrate()
    try:
        s.rewind(999); return False
    except IndexError:
        return True

@t("APPEND-ONLY: a rewound frame is unchanged after later writes (no deletion)", True)
def _8():
    s = demo_substrate()
    before = dict(s.rewind(1).cells)
    s.effect('a', 777, 'much later', 'eff')
    after = s.rewind(1).cells
    return before['a'].value == after['a'].value

@t("AGENT CONTRACT: the payload declares its error shape and codes", True)
def _9():
    a = demo_substrate().project_agent(0)
    e = a['errors']
    return (set(e) == {'shape', 'codes', 'retry'}
            and 'UNKNOWN_CELL' in e['codes'] and e['shape'].get('error') == 'str')

@t("AGENT CONTRACT: cells carry a stable addr and a digest over them", True)
def _10():
    a = demo_substrate().project_agent(0)
    return (all(c.get('addr') for c in a['cells'])
            and isinstance(a.get('digest'), str) and len(a['digest']) == 16)

@t("PAGE: the shipped html carries a rewind control AND loads the frozen frame", True)
def _11():
    h = open(os.path.join(HERE, 'index.html')).read()
    return ("const FRAMES = " in h
            and "DATA = FRAMES[frame].human" in h
            and "id=\"prev\"" in h and "id=\"next\"" in h)

@t("NEGATIVE: a page whose rewind only moves a counter FAILS (proves _11 can fail)", True)
def _12():
    """The first version of this leg asserted a property of the CURRENT file, which is
    the same thing _11 already checks, so it could never fail independently — it was a
    restatement wearing a negative control's clothes.

    A negative control has to demonstrate the DETECTOR works on a counter-example. So:
    take the real page, corrupt its rewind into the counter-only version, and assert the
    detector then fails. If that does not hold, _11 is not detecting anything."""
    good = open(os.path.join(HERE, 'index.html')).read()
    broken = good.replace("DATA = FRAMES[frame].human",
                          "DATA.human.frame=frame; DATA.agent.frame=frame")  # counter only
    if broken == good:
        return False                     # could not construct the counter-example
    for src, want_detect in ((good, True), (broken, False)):
        detected = "DATA = FRAMES[frame].human" in src
        if detected != want_detect:
            return False
    return True

@t("PAGE: both projections are actually present in the payload, and they agree", True)
def _13():
    h = open(os.path.join(HERE, 'index.html')).read()
    i = h.index('const FRAMES = ') + len('const FRAMES = ')
    j = h.index(';\n', i)
    fr = json.loads(h[i:j])['frames']
    return all([r['cell'] for r in f['human']['rows']] == [c['addr'] for c in f['agent']['cells']]
               for f in fr)

@t("PAGE: the timeline actually GROWS, so rewind shows something different", True)
def _14():
    h = open(os.path.join(HERE, 'index.html')).read()
    i = h.index('const FRAMES = ') + len('const FRAMES = ')
    j = h.index(';\n', i)
    fr = json.loads(h[i:j])['frames']
    sizes = [len(f['human']['rows']) for f in fr]
    return sizes[0] < sizes[-1] and len(set(sizes)) > 2

@t("RENDER: disabling render() must FAIL the suite (proves the page is not hollow)", True)
def _15():
    """The honest gap, found by injecting a fault that nothing caught. A page whose
    render() returns immediately — rendering NOTHING — passed all 14 legs, because
    every leg checked the DATA and the WIRING and none checked the RENDER.

    Closing it properly needs a DOM, and there is no browser here. What IS checkable
    without one: the render path must emit a non-empty table body for a non-empty
    frame, and the tab controller must actually toggle the panels. Both are static
    properties of the shipped file, and both are checkable."""
    h = open(os.path.join(HERE, 'index.html')).read()
    # render() must write into the table body, not just exist
    writes_body = "$('hbody').innerHTML" in h
    writes_json  = "$('json').textContent" in h
    # the tab controller must actually toggle, not just exist
    toggles = "classList.remove('on')" in h and "classList.add('on')" in h
    # and the render function must not be short-circuited at its top
    hollow = re.search(r"function render\(\)\s*\{\s*return\s*;", h) is not None
    return (writes_body and writes_json and toggles) and not hollow

def main():
    print("frontend self-test")
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
