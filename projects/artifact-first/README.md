# artifact-first

**Reach for the artifact before you form the view.**

Most wrong claims are not wrong because someone was careless. They are wrong because a
conclusion was formed first and the evidence was then gathered to fit — and evidence read
through a conclusion looks like confirmation.

This is a small toolkit for making that ordering visible, and for catching the other
failure that timestamps cannot see: a well-grounded claim that the artifact refutes.

```
pip install -e .        # or just put the package on your path
python tests/test_gates.py
```

---

## The two gates

A claim is a statement, the artifact it rests on, and **the order in which the two
existed**. Order is the whole point, and it is the thing usually lost.

| | gate | asks | catches | misses |
|---|---|---|---|---|
| 1 | **grounding** | did the artifact exist before the claim was written? | a conclusion formed before the evidence | a grounded claim its own evidence refutes |
| 2 | **consistency** | does the report contradict itself? | a headline its body refutes | a report that is consistently wrong throughout |

They are not interchangeable. **A receipt that predates a claim does not mean the claim
agrees with the receipt.** Gate 2 exists because of exactly that.

## The case that forced gate 2

From the fleet's own lane-u-collision report:

> **NO. None of the three implements or plans a per-cell mode menu.**

Two clauses later, in the same report:

> That is genuinely a transmitted per-cell mode, and it is the only one in any of the
> three repos.

The receipt for that headline predates the headline. **Gate 1 passes it. It is still
wrong**, and wrong in the most expensive way: a reader who stops at the lead draws the
opposite conclusion from the one the report supports.

`tests/test_gates.py` runs the linter against that real report and asserts it rediscovers
the defect. A linter that cannot find a known, shipped error is a decoration.

## Usage

```python
from artifact_first.claim import Claim, GROUNDED, NARRATIVE_FIRST, UNSOURCED
from artifact_first.gates import check_claim, check_all, report

c = Claim(
    id="torus-conductance",
    text="The true conductance at a=14 is 4/196 = 0.0204.",
    said_at="2026-09-29T20:55:00Z",
    receipt="research/family/family_run.txt",
    receipt_at="2026-09-29T20:47:00Z",   # evidence came first
    author="owner",
)

print(c.grounding())          # UNSOURCED -> the claim cites nothing that resolves
print(c.lag_seconds())        # None
print(check_claim(c, open("report.md").read()).summary())
```

Claims load from JSONL, one per line:

```json
{"id":"gpu-lab-evalbug","text":"...","said_at":"...","receipt":"...","receipt_at":"...","author":"team"}
```

## What gate 2 actually checks

Four shapes, each chosen because it really occurred. This is **not** a truth-checker and
does not pretend to be — it is a sample of the ways a report contradicts itself, and a
pass means *these four shapes were not found*, which is a much smaller claim than
*consistent*.

| check | shape | real instance |
|---|---|---|
| **C1** | universal negative in the summary, unique instance in the body | "none of the three" / "the only one in any of the three" |
| **C2** | a summary statistic that appears nowhere in the body | an invented headline number |
| **C3** | summary negates a term the body affirms | "not lossless" / "the result is lossless" |
| **C4** | summary and body disagree on a count for the same denominator | 41 of 64 vs 33 of 64 |

## Known limits, stated rather than buried

- **A headingless report has no body**, so C1 cannot fire. Tested explicitly rather than
  hidden. Give your reports `##` structure.
- **Gate 1 needs timestamps on receipts.** Without them every claim is `UNSOURCED`, which
  is a true and useful answer but a blunt one.
- **`UNSOURCED` is not `FALSE`.** An unsourced claim is ungrounded, not wrong. Conflating
  those is how a linter starts lying.
- **Neither gate proves a claim is true.** They check order and self-consistency. A
  consistently wrong report passes both.

## The bug this repo's own linter had

Worth reading, because it is the exact failure the project exists to prevent — committed
by the instrument itself.

An early version wrapped every check in a bare `try/except` and appended any exception to
the findings list as an `ERR` finding. A `NameError` inside the C4 check therefore looked
**identical to "C4 found nothing."** The linter had a silent blind spot and reported clean
for a whole session.

A crash must be louder than a pass. Checks now raise `LinterCrashed`, and the test suite
asserts all four fire.

Two more from the same session, same class:

- The summary/body split counted lines, which swallowed whole documents when a body
  followed the verdict immediately. **Every check except C2 had silently become vacuous.**
  It is now split on the second `##`, calibrated against the real report.
- A `str.replace` no-op'd on a whitespace mismatch, leaving the old formula in place, and
  an instrument happily reported `0.000` for every input.

**A measurement that cannot produce a wrong answer is not a measurement.** Every test here
has a negative control beside its positive assertion.

## Why this is a qult, not a quilt

A qult is what a quilt becomes when it learns to contain other quilts. This repo is a
quilt of *methods* — the scout's "go to the source and check the call sites," the
historian's "download the paper and quote it verbatim," the reviewer's "read the headline
against the body" — lifted out of individual agents and made reusable.

The fleet's dominant failure is shared: conclusion first, evidence second. The reviewers
are the only cell kind that catches it, and they catch it *inward*, by reading a claim
against itself rather than against the world. **A fleet that only verifies outward will
ship confidently wrong work at scale.** These two gates make the inward check mechanical.

## See also

- `PROOF.md` — what the gates do and do not establish
- `METHOD.md` — the process study this came from, across five agents
- `CASEBOOK.md` — the real failures, and which gate catches each
