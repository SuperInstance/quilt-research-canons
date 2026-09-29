# Fleet legibility report

Produced by `lint_legibility.py`, run over the fleet by a script that had never
seen it. Regenerate with the command in `../lint_legibility.py`.

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

