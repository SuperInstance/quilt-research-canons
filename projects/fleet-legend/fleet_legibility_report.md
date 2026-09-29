# Fleet legibility report

Produced by `lint_legibility.py`, run over the fleet by a script that had never
seen it.

## Regenerate this

```
python3 run_complete2.py
```

Rewrites this report and `verdicts.json` from live API reads. It reads the GitHub tree
API only and never clones a repository — a clone of `AI-Writings` exceeded an 80-second
timeout and took down an entire run.

## What this report does NOT do

- **It is not the whole fleet.** The API enumerates 100 repos of a claimed 1300. Every
  number here is scoped to those 100 and to the default branch at read time.
- **It does not judge code quality.** Only whether a stranger can get in and recover.
- **L3/L4/L5 are keyword heuristics.** A repo can satisfy them by accident, and can fail
  them while being perfectly legible to a human. The grade is a prompt for a human look,
  not a verdict.
- **It does not read the code.** A repository with tests in an unconventional layout reads
  as having none.

## The number

| grade | count | meaning |
|---|---|---|
| ENTERABLE | 16 | read, run the first command, see a receipt |
| ENTERABLE-WEAK | 74 | has a command; missing receipt, negative space, or error surface |
| INVISIBLE | 9 | no runnable first command |
| NO-README | 1 | no README at all |
| **total** | **100** | |

## Which obligation is missing, across the whole fleet

| obligation | repos failing it |
|---|---|
| L1 | 20 |
| L2 | 9 |
| L3 | 14 |
| L4 | 55 |
| L5 | 59 |

L2 is the binding constraint: a repo with no runnable first command is invisible to a
zero-shot agent regardless of how well written its prose is.

## Not enterable, most-recently-pushed first

| repo | lang | description | grade | missing |
|---|---|---|---|---|
| `quilt-gpu-lab` | Python | **NO** | INVISIBLE | L1, L2, L4, L5 |
| `AI-Writings` | HTML | yes | INVISIBLE | L2 |
| `pong-quilt` | JavaScript | **NO** | INVISIBLE | L1, L2, L4 |
| `PuddnHead` | - | yes | INVISIBLE | L2, L5 |
| `qthe` | JavaScript | yes | INVISIBLE | L2, L4, L5 |
| `qthe-codec` | Python | **NO** | INVISIBLE | L1, L2, L4, L5 |
| `ternary-wiki` | Shell | **NO** | INVISIBLE | L1, L2, L4, L5 |
| `ropesight` | JavaScript | yes | INVISIBLE | L2, L5 |
| `quilt-fiction` | HTML | yes | NO-README | - |
| `SuperInstance.github.io` | HTML | yes | INVISIBLE | L2, L4, L5 |

_(10 total)_

## The cheapest possible fix

One fenced block, its first non-comment line runnable, plus one sentence saying what
output proves success. That converts INVISIBLE into ENTERABLE for a few minutes of
work, and it is the single highest-leverage change available to this fleet.

