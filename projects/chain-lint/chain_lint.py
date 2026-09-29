#!/usr/bin/env python3
"""
chain_lint.py — is the witness chain in the DATA, or only in the schema?

THE CONVERGENCE THAT BUILT THIS

  1. process-signature: a `witness-chained` repo appears in 1 of the 60 largest repos.
  2. a scout read 550 live cells: prev_hash uniformly zero on every one.
  3. the DETAIL payload declares prev_hash. The field exists. The value does not.

    A field that exists is not a field that is used.

Every other instrument built tonight reads SHAPE. Shape cannot see a null. This reads VALUE,
and it exists because of two bugs I made in this file, both of which reported the chain
as PRESENT when it is absent:

  BUG 1  the zero-set enumerated one exact 64-zero string; the field carries 16 zeros,
        so every zero hash fell through and counted as a live link.
  BUG 2  a field that is MISSING from the payload was counted as linked, because
        is_zero("__MISSING__") is False and the caller only incremented on `not is_zero`.

BUG 2 is the more dangerous of the two and it is why this file now ships with a
self-test. A missing value and a live value are both "not zero" to a naive test, and the
naive test is the one that gets trusted.
"""
from __future__ import annotations
import json, os, ssl, sys, time, urllib.request, urllib.error

BASE = os.environ.get("CANON_BASE", "https://api.superinstance.dev")
UA = {"User-Agent": "chain-lint/1.0"}
CTX = ssl._create_unverified_context()
MISSING = object()          # a sentinel that is NOT a hash, so it can never be "live"


def get(path, tries=6, pause=2.5, timeout=20):
    """(status, payload_str, retries). The retry count is RETURNED and printed, never
    hidden: a 503 that silently became a zero is the bug this tool exists to report."""
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA),
                                        timeout=timeout, context=CTX) as r:
                return r.status, r.read().decode(), i
        except urllib.error.HTTPError as e:
            if e.code in (503, 502, 504, 429):
                time.sleep(pause); continue
            return e.code, "", i
        except Exception:
            time.sleep(pause); continue
    return 0, "", tries


def is_zero(v) -> bool:
    """A hash of any width that is all zeros means NO LINK."""
    if v is MISSING or v is None or v == "":
        return True
    s = str(v).strip().lower()
    if s.startswith("0x"):
        s = s[2:]
    return s.strip("0.") == ""


def classify(prev):
    """MISSING | ZERO | LINKED -- three states, never two.

    Two states is how the first version of this file shipped a false PASS: it folded
    MISSING into LINKED. A field that is absent and a field that is null are the same
    defect, and they are not the same as a live link."""
    if prev is MISSING or prev is None or prev == "":
        return "MISSING"
    return "ZERO" if is_zero(prev) else "LINKED"


def detail(cid):
    st, body, _ = get(f"/api/cell/{cid}", tries=4)
    if st != 200:
        return None, st
    try:
        return json.loads(body).get("cell", {}), 200
    except Exception:
        return None, st


def measure(limit=20):
    st, body, retries = get(f"/api/cells?limit={limit}")
    if st != 200:
        return None, {"error": f"index unavailable (status {st}, {retries} retries)"}
    try:
        cells = json.loads(body).get("cells", [])
    except Exception:
        return None, {"error": "index payload unparseable"}
    if not cells:
        return None, {"error": "index returned no cells"}
    counts = {"MISSING": 0, "ZERO": 0, "LINKED": 0}
    declared = False
    unreadable = 0
    rows = []
    for c in cells:
        cell, _s = detail(c.get("id"))
        if cell is None:
            unreadable += 1
            counts["MISSING"] += 1
            rows.append((c.get("id"), "UNREADABLE")); continue
        if "prev_hash" in cell:
            declared = True
        k = classify(cell.get("prev_hash", MISSING))
        counts[k] += 1
        rows.append((c.get("id"), str(cell.get("prev_hash", "<absent>"))))
    return dict(n=len(cells), counts=counts, declared=declared,
                retries=retries, unreadable=unreadable, rows=rows), None


def self_test():
    """The negative controls for the two bugs this file actually shipped with."""
    ok = True
    checks = [
        ("16-zero hash is ZERO, not LINKED", classify("0x" + "0" * 16) == "ZERO"),
        ("64-zero hash is ZERO (width-independent)", classify("0x" + "0" * 64) == "ZERO"),
        ("int 0 is ZERO", classify(0) == "ZERO"),
        ("None is MISSING not LINKED", classify(None) == "MISSING"),
        ("empty string is MISSING not LINKED", classify("") == "MISSING"),
        ("a real hash is LINKED", classify("0xdeadbeefcafe1234") == "LINKED"),
        ("the sentinel is MISSING", classify(MISSING) == "MISSING"),
    ]
    print("  SELF-TEST (the two bugs this file shipped with)")
    for name, passed in checks:
        print(f"    [{'PASS' if passed else 'FAIL'}] {name}")
        ok &= passed
    return ok


def main() -> int:
    print()
    print("  CHAIN LINT — is the witness chain in the DATA, or only in the schema?")
    print("  " + "=" * 70)
    if not self_test():
        print("\n  SELF-TEST FAILED — refusing to report a measurement from a broken tool.")
        return 2
    print()
    res, err = measure(int(sys.argv[1]) if len(sys.argv) > 1 else 20)
    if err:
        print("  could not measure:", err)
        print("  reported as UNMEASURED, never as a broken chain.")
        return 2
    c = res["counts"]; n = res["n"]
    print(f"  host                : {BASE}")
    print(f"  cells sampled       : {n}  (index retries: {res['retries']}, unreadable: {res['unreadable']})")
    print(f"  DETAIL declares prev_hash : {res['declared']}   (the index omits it; that is normal)")
    print(f"    LINKED {c['LINKED']:>4}   ZERO {c['ZERO']:>4}   MISSING {c['MISSING']:>4}")
    print()
    for cid, ph in res["rows"][:4]:
        print(f"    {str(cid)[:28]:28} prev_hash={ph}")
    if res["retries"]:
        print(f"\n  the host 503'd {res['retries']} time(s) and recovered. Printed, not hidden.")
    print()
    if res["declared"] and c["LINKED"] == 0 and c["ZERO"] + c["MISSING"] >= 1:
        print("  VERDICT: DECLARED-NOT-USED")
        print("  " + "-" * 70)
        print("  The field is in the payload and carries no link on any sampled cell.")
        print("  A reader who sees the field assumes the tamper-evidence exists.")
        return 1
    if c["LINKED"]:
        print(f"  VERDICT: CHAIN PRESENT on {100*c['LINKED']//n}% of sampled cells")
        return 0
    print("  VERDICT: NO CHAIN, and the payload does not declare one (a missing feature,")
    print("           which is a different defect from a broken promise)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
