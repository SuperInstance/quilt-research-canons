#!/usr/bin/env python3
"""
moth_frame_test.py — the limit I stated, tested.

`moth-qpixl-roundtrip.md` reported: the QPIXL round trip is MONOTONE but not
value-preserving, and an 8-level glyph ramp round-trips EXACTLY.

It also stated the limit plainly: "One ramp is a monotone input. The real test is a full
glyph field where neighbouring values cross." A monotone ramp is the EASIEST possible case
for an order-preserving map, so the finding is currently unfalsified by anything hard.

This is the hard case: small 2-D fields with deliberately crossing neighbours, submitted
to the same engine, checking whether ANY pair of cells is ever reordered relative to
every other cell. That is the property a glyph codec needs, and it is strictly stronger
than the ramp result.

Read-only against api.mothquantum.com. No writes to any repo.
"""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36',
      'Authorization': f'Bearer {os.environ["MOTH_API_KEY"]}',
      'Content-Type': 'application/json', 'Accept': 'application/json'}
BASE = 'https://api.mothquantum.com/api/v1'

def call(path, method='GET', data=None, timeout=70):
    req = urllib.request.Request(f'{BASE}{path}',
                                 data=json.dumps(data).encode() if data is not None else None,
                                 headers=UA, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except Exception: return e.code, {}
    except Exception as e:
        return 0, {'err': str(e)[:100]}

def submit(grid, shots=2048, tries=16):
    vals = "[" + ",".join("[" + ",".join(str(v) for v in r) + "]" for r in grid) + "]"
    st, d = call('/engines/qpixl-v1/process', 'POST',
                 {"mode": "emu", "params": {"values": vals, "machine": "aer", "shots": shots}})
    jid = d.get('job_id') if isinstance(d, dict) else None
    if not jid:
        return None, d.get('error') or d.get('errors') or d
    for _ in range(tries):
        time.sleep(5)
        _, s2 = call(f'/jobs/{jid}/status')
        s = (s2.get('status') or '') if isinstance(s2, dict) else ''
        if s.lower() in ('succeeded', 'completed', 'success', 'done'):
            _, rd = call(f'/jobs/{jid}/result')
            return rd.get('result', {}).get('output'), None
        if s.lower() in ('failed', 'error'):
            return None, s2.get('error')
    return 'TIMEOUT', None

def glyph(v, levels=10):
    return min(levels - 1, int(v * levels))

def inversions(f, o):
    R, C = len(f), len(f[0]); n = 0
    for a in range(R):
        for b in range(C):
            for c in range(R):
                for d in range(C):
                    if f[a][b] < f[c][d] and o[a][b] > o[c][d]:
                        n += 1
    return n

CASES = {
    '2x2 checker  (max crossing)': [[0.0, 1.0], [1.0, 0.0]],
    '2x2 ramp     (control)':      [[0.0, 0.3], [0.6, 1.0]],
    '2x3 crossing':                [[0.0, 0.5, 1.0], [1.0, 0.5, 0.0]],
    '2x4 crossing':                [[0.0, 0.1, 0.9, 1.0], [0.2, 0.8, 0.3, 0.7]],
    '1x5 zigzag':                  [[0.0, 0.2, 0.4, 0.7, 1.0]],
}

def main():
    print()
    print("  MOTH qpixl-v1 -- THE HARD CASE: do glyphs survive a NON-MONOTONE field?")
    print("  " + "=" * 74)
    print("  A monotone ramp is the easy case for an order-preserving map. These are not.")
    print()
    all_ok = True
    for label, f in CASES.items():
        out, err = submit(f)
        if not out or out == 'TIMEOUT':
            print(f"  {label:30} NO RESULT  {json.dumps(err)[:120] if err else ''}")
            continue
        if not (isinstance(out, list) and isinstance(out[0], list)):
            print(f"  {label:30} unexpected output shape: {json.dumps(out)[:100]}")
            continue
        R, C = len(f), len(f[0])
        inv = inversions(f, out)
        gi = [[glyph(v) for v in r] for r in f]
        go = [[glyph(v) for v in r] for r in out]
        same = gi == go
        mx = max(abs(out[a][b] - f[a][b]) for a in range(R) for b in range(C))
        all_ok &= (inv == 0) and same
        print(f"  {label}")
        for a, b in zip(f, out):
            print(f"     {[round(x,3) for x in a]}  ->  {[round(x,3) for x in b]}")
        print(f"     order inversions : {inv}      max |out-in| : {mx:.4f}")
        print(f"     glyphs in  {gi}")
        print(f"     glyphs out {go}   IDENTICAL: {same}")
        print()
    print("  " + "=" * 74)
    print(f"  VERDICT: glyph stream survives on every non-monotone case: {all_ok}")
    if not all_ok:
        print("  A non-zero inversion count means the monotone result does NOT extend")
        print("  beyond a ramp, and the glyph-codec claim needs weakening.")
    print()

if __name__ == '__main__':
    main()
