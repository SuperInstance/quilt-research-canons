---
title: Receipt 001 — the dependency-closed artifact now exists
date: 2026-09-29
repo: SuperInstance/quilt-c
commit: 21282474b3f2
---

## What shipped

`quilt-c` PR #2, merged. The first artifact in the fleet that meets the bar the
wider read set: clone, one command, verified receipt, under ten seconds.

```
git clone https://github.com/SuperInstance/quilt-c.git
cd quilt-c
make verify
```

**Measured cold, from GitHub, as a stranger:** 2.9 seconds clone-to-receipt.

## The receipt

```json
{
  "schema": "quilt-c/verify-receipt@v1",
  "verdict": "VERIFIED",
  "assertions_passed": 1285,
  "assertions_failed": 0,
  "suites": 7,
  "source_files": 28,
  "source_tree_sha256": "98ae6ba33bea66c58adf7e1c83e4f9994780fd76573400cd15918c8727299f58",
  "receipt_sha256": "8aded885bc61faf2d0b3bf125d885e97f017d835533c478cbbe187d1da548886"
}
```

Both hashes are **portable**: a cold clone from GitHub and the local working tree
that authored the commit produce byte-identical `source_tree_sha256` and
`receipt_sha256`. That is the reproducibility contract, actually holding rather
than asserted.

## What was actually wrong before

The C99 reference port had the strongest evidence in the fleet and none of it was
reachable:

1. CI ran 47 of 1,285 assertions. The workflow called `make test`, which is the
   engine suite only. The proof suite alone is 1,059 assertions. Coverage of the
   port's own evidence in CI: 3.7%, on the port the other 11 are byte-checked against.
2. The README test table listed the C99 port as `manual`. The suite is fully
   automated. Under-claiming the reference port teaches readers to distrust the
   strongest artifact in the set.
3. No single entry point. A stranger had to know `make`, then `make test-all`,
   then read the Makefile for the suite layout.

## Fail-closed receipts

Two independent fault classes were injected and confirmed caught:

| class | injection | result |
|---|---|---|
| behavioural | `e->tick += 2` at `src/engine.c:197` | 3 assertions fail, verdict FAILED, exit 2 |
| build | invalid C appended to `tests/test_engine.c` | 0 assertions, verdict FAILED, exit 2 |

Both reverted. Final run VERIFIED 1285/0.

## Two bugs self-caught while building it

- **Self-referential digest.** The first tree hash included `VERIFY_RECEIPT.json`,
  the file the script itself writes. Different hash every run. The receipt is the
  output, not an input.
- **Non-deterministic receipt.** The first receipt body carried per-suite wall-clock
  timings, so `receipt_sha256` changed on every run of an identical tree. A receipt
  is a claim about the artifact; timings are diagnostics about the run. Timings now
  print and do not hash.

Both found by running `make verify` three times and diffing, which is the discipline
the fleet preaches and, until this PR, had not applied to its own reference port.

## External verification

CI ran `make verify` on a fresh ubuntu-latest runner and passed. This is the first
time in this fleet's history that a claim about the substrate was checked by
something outside the substrate. It is a small instance of the 90-day chain's
Days 31-50 link (export verification), landed early because the port was already
dependency-closed and only the entry point was missing.

## The chain position

| link | status |
|---|---|
| Days 0-7 freeze and pin one canonical repo | **partial** — the runnable repo now exists; the freeze and the 4,836-repo archive do not |
| Days 8-30 one dependency-closed artifact | **done** |
| Days 31-50 export verification | **early partial** — green on a fresh runner, deterministic receipt, but no signed release and no second-substrate reader |
| Days 51-70 thin A2A cell API | not started |
| Days 71-90 sealed experiment vs public baseline | not started |

Next link, in order: sign the release so the receipt chain has a trust root, then
make a second reader on a genuinely different substrate. Same substrate twice is
still theater.
