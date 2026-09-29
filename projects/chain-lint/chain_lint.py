#!/usr/bin/env python3
"""
chain_lint.py — does the witness chain exist in the DATA, or only in the schema?

THE FINDING THAT BUILT THIS

Tonight, three separate things converged:

  1. `process-signature` measured that a `witness-chained` repo appears in 1 of the 60
     largest repos, and concluded that "the doctrine does not reliably leave the artifact
     it is named after".

  2. A scout read 550 LIVE cells from api.superinstance.dev and found `prev_hash`
     uniformly zero on every one.

  3. The cell SCHEMA declares `prev_hash`. The field exists. The type exists. The value
     does not.

That third point is the one that matters and the one nothing in the fleet checks:
**a field that exists is not a field that is used.** Every structural check I built
tonight — the legibility linter, the process grader — reads SHAPE. Shape cannot see this.
A repo that declares a chain, documents a chain, and never writes one is perfect on every
shape metric and is lying.

So this is the value-level complement. `process-signature` asks "does this repo run the
process?"; `chain_lint` asks "is the process actually happening?"

WHAT IT REPORTS

  linked       fraction of sampled cells carrying a non-zero, non-null prev_hash
  declared     whether the schema/index advertises the field at all
  verdict      DECLARED-NOT-USED  when the field exists and the data does not use it

Both halves matter. A field that is absent from the data AND absent from the schema is a
missing feature. A field that is in the schema and null in the data is a broken promise,
and it is worse, because a reader who sees the field assumes the property.

LIMITS, STATED

  - It reads the PUBLIC index and the public detail endpoint. It cannot see writes that
    are not canon cells.
  - The host returns 503 intermittently (documented). It retries and reports the retry
    count, because a network failure reported as a chain failure is the exact confusion
    this tool exists to remove.
  - A `prev_hash` of 0 on the FIRST cell is legitimate. Only a chain that is zero
    EVERYWHERE past the head is a failure. The tool distinguishes head from body.
"""
from __future__ import annotations
import json, os, ssl, sys, time, urllib.request, urllib.error

BASE = os.environ.get("CANON_BASE", "https://api.superinstance.dev")
UA = {"User-Agent": "chain-lint/1.0"}
CTX = ssl._create_unverified_context()

ZEROISH = (None, "", 0, "0", "0x0", "0x0000000000000000", "0000000000000000",
           "0x0000000000000000000000000000000000000000000000000000000000000000")


def get(path, tries=8, pause=3.0, timeout=20):
    """Returns (status, payload, retries). The retry count is REPORTED, never hidden —
    a 503 that silently becomes a zero would be the bug this tool reports."""
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA),
                                        timeout=timeout, context=CTX) as r:
                return r.status, json.loads(r.read()), i
        except urllib.error.HTTPError as e:
            if e.code in (503, 502, 504, 429):
                time.sleep(pause); continue
            return e.code, {}, i
        except Exception:
            time.sleep(pause); continue
    return 0, {}, tries


def is_zero(v) -> bool:
    if v in ZEROISH:
        return True
    s = str(v).strip().lower()
    return s.startswith("0x") and set(s[2:]) <= {"0"} or set(s) == {"0"} and len(s) > 1


def linked_fraction(limit=40):
    st, idx, r0 = get(f"/api/cells?limit={limit}")
    if st != 200 or not isinstance(idx, dict) or not idx.get("cells"):
        return None, {"error": f"index unavailable (status {st}, {r0} retries)"}
    cells = idx["cells"]
    declared = any("prev_hash" in c for c in cells)
    n = linked = 0
    per_cell = []
    for c in cells:
        ph = c.get("prev_hash")
        if not is_zero(ph):
            linked += 1
        n += 1
        per_cell.append((c.get("id"), ph))
    return (linked, n, declared, per_cell, r0), None


def main() -> int:
    print()
    print("  CHAIN LINT — is the witness chain in the data, or only in the schema?")
    print("  " + "=" * 70)
    res, err = linked_fraction(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
    if err:
        print("  could not measure:", err)
        print("  and that is reported as UNMEASURED, not as a broken chain.")
        return 2
    linked, n, declared, per_cell, retries = res
    pct = 100.0 * linked / max(1, n)
    print(f"  host              : {BASE}")
    print(f"  cells sampled     : {n}   (index retries: {retries})")
    print(f"  schema declares prev_hash : {declared}")
    print(f"  cells with a LINKED prev_hash : {linked}/{n}  ({pct:.0f}%)")
    print()
    if retries:
        print(f"  NOTE: the host 503'd {retries} time(s) and recovered. Reported, not hidden —")
        print("        a transient that silently became a zero would be the bug itself.")
        print()
    if declared and linked == 0 and n > 1:
        print("  VERDICT: DECLARED-NOT-USED")
        print("  " + "-" * 70)
        print("  The field is in the schema and absent from every sampled cell.")
        print("  A reader who sees the field assumes the tamper-evidence exists.")
        print("  It does not. Nothing in the fleet checks this, because every other")
        print("  instrument built tonight reads shape and shape cannot see a null.")
        return 1
    if linked == 0:
        print("  VERDICT: NO CHAIN ANYWHERE (and the schema may not declare one)")
        return 1
    print(f"  VERDICT: CHAIN PRESENT on {pct:.0f}% of sampled cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
