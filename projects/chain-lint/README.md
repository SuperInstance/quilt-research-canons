# chain-lint

**Is the witness chain in the data, or only in the schema?**

## What it is for

Three things converged tonight and the third is the one nobody checks.

1. `process-signature` measured that a `witness-chained` repo appears in **1 of the 60**
   largest repos.
2. A scout read **550 live cells** from `api.superinstance.dev` and found `prev_hash`
   uniformly zero on every one.
3. **The cell schema declares `prev_hash`.** The field exists. The type exists. The value
   does not.

> **A field that exists is not a field that is used.**

Every other instrument built tonight reads **shape** — filenames, directory structure,
declared fields. Shape cannot see a null. A repo that declares a chain, documents a chain,
and never writes one scores perfectly on every structural metric in this fleet and is
quietly lying. This is the value-level complement:

| | asks |
|---|---|
| `process-signature` | does this repo **run** the process? |
| `chain-lint` | is the process **actually happening**? |

## What it reports

- `linked` — fraction of sampled cells carrying a non-zero, non-null `prev_hash`
- `declared` — whether the endpoint advertises the field at all
- verdict — `DECLARED-NOT-USED` (the broken-promise case) vs `NO CHAIN ANYWHERE` (a
  missing feature). **These are different failures and the tool refuses to merge them.**

## Two things it will not do

**It will not hide a network failure as a chain failure.** The host 503s intermittently —
documented, and it recovers on retry. The retry count is *printed*. A transient that
silently became a zero would be precisely the bug this tool exists to report, and an
earlier version of a sibling tool in this fleet made that exact mistake.

**It will not call the head a failure.** A `prev_hash` of zero on the *first* cell is
correct. Only a chain that is zero everywhere past the head is a defect.

## Measured, and the boundary resolved

The open question from the first run was the **detail endpoint's response shape**. It is:

```
GET /api/cell/<id>  ->  {"ok":true,"cell":{ id, type, state, embedding_id,
                                           prev_hash, timestamp, created_at, source }}
```

and **`state` is a JSON *string*, not an object.** That single fact is why the first
version of this tool read zero keys back: it called `.keys()` on a string. The index
endpoint (`/api/cells?limit=N`) legitimately omits `prev_hash`; the declaration is judged
on the detail payload, not the index, because reading it off the index understates the
problem.

With that resolved, the measurement is unambiguous:

```
cells sampled                    : 14   (retries 0, unreadable 0)
DETAIL payload declares prev_hash: True
  LINKED 0   ZERO 14   MISSING 0
  cron-1790722551544   prev_hash=0x0000000000000000
  cron-1790722253261   prev_hash=0x0000000000000000
  cron-1790721963076   prev_hash=0x0000000000000000
VERDICT: DECLARED-NOT-USED
```

**The field is in the payload of every sampled cell and carries no link on any of them.**
This reproduces a separate 550-cell read by a different agent, through a different path.

## This tool shipped two bugs, and they are the finding

Both bugs reported the chain as **PRESENT** when it is absent. Both are in the
self-test now.

1. **Zero-detection was width-dependent.** The zero-set enumerated one exact 64-zero
   string; the field carries 16 zeros, so every zero hash fell through and counted as a
   live link. Fixed by asking whether the digits are *all* zero, which makes width
   irrelevant — which was the point.

2. **`MISSING` was counted as `LINKED`.** A field absent from the payload and a field
   holding `None` are both "not zero" to a naive test, and the caller incremented on
   `not is_zero`. Fixed with a three-state classifier — `MISSING / ZERO / LINKED`, never
   two — because **a missing value and a live value are different facts**.

Bug 2 is the one worth dwelling on. This tool exists to say *a field that exists is not a
field that is used*, and in its first form it made the same class of mistake in the
opposite direction: it treated a value that is not there as a value that is fine. **A
measurement that cannot be wrong is not a measurement, and neither is a tool that
confidently gets the direction wrong.**

## Run it

```bash
python3 chain_lint.py 40          # sample 40 cells
CANON_BASE=https://elsewhere python3 chain_lint.py 40
```

Exit 0 = chain present, 1 = no chain, 2 = **unmeasurable** (and it says so, rather than
guessing).
