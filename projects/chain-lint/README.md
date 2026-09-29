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

## Measured, and the honest boundary

```
host                    : https://api.superinstance.dev
cells sampled           : 30    (index retries: 0)
schema declares prev_hash on the INDEX : False
cells with a LINKED prev_hash          : 0/30  (0%)
verdict                 : NO CHAIN ANYWHERE (and the index does not declare one)
```

**What that does and does not establish.** On the **index** endpoint the field is not
present in responses at all, and no cell carries a link. The stronger claim — *the schema
declares `prev_hash` and every sampled cell's value is zero* — comes from the **detail**
endpoint, where a separate 550-cell read found the declaration and the zeros.

**I could not reproduce the detail read.** `GET /api/cell/<id>` returned a payload with
none of the expected fields populated for me, so my own confirmation rests on the index
plus that other read. **The first thing anyone re-checking this should do is pin down the
detail endpoint's actual response shape** — a tool that reports "no chain" when the real
situation is "declared but unused" is under-reporting in the safe direction, which is the
right direction to be wrong in, but it is still wrong.

## Run it

```bash
python3 chain_lint.py 40          # sample 40 cells
CANON_BASE=https://elsewhere python3 chain_lint.py 40
```

Exit 0 = chain present, 1 = no chain, 2 = **unmeasurable** (and it says so, rather than
guessing).
