# fleet-legend

**A repo's frontend is not its README. It is its first error message.**

A README is only read by someone who already arrived. An error is read by someone who just
show up and got it wrong. This is the observation the whole thing is built on, and it has
direct evidence from one session — see `ERRORS.md`.

## The measured problem

A script with no prior knowledge of the fleet fetched and scored 100 repos:

| | |
|---|---|
| repos with a README | **98 / 100** |
| repos with a runnable first command | **68 / 100** (strict measure) |
| repos with no description | **20 / 100** — invisible to search |
| **ENTERABLE** (read → run → receipt, in 30s) | **90 / 100** (loose measure) |

Those two command counts are **different measures and they do not agree**, deliberately:
the strict one looks only at the first fenced block, the loose one scans all of them.
Both are reported because reporting only the flattering one would be the failure this
project exists to catch.

Almost every repo *looks* documented. The binding constraint is that the first command is
often missing, and that nothing says what output means success.

## The five obligations

| | obligation | why |
|---|---|---|
| **L1** | description | a repo with no description is unsearchable |
| **L2** | a fenced block whose first non-comment line runs | without this the repo is INVISIBLE, however good the prose |
| **L3** | what output proves it worked | an agent that cannot tell success from failure will report noise as a result |
| **L4** | what it does NOT do | the single most useful line in most READMEs, and the most absent |
| **L5** | an error surface that names the fix | see `ERRORS.md`; this is the expensive one |

```bash
python3 lint_legibility.py README.md
```

## Grades

- `ENTERABLE` — all five met
- `ENTERABLE-WEAK` — has a command, missing receipt / negative space / error surface
- `INVISIBLE` — no runnable first command

L2 decides the first grade, because a repo with no command is invisible to an agent no
matter how well it is written.

## What this does NOT do

- It does not judge whether the code is good. It judges whether a stranger can get in.
- It is a heuristic, and the L3/L4/L5 checks are keyword-based. Narrow vocabularies on
  purpose: a linter that cries wolf gets switched off.
- Short READMEs are skipped for L3/L4/L5 by a length gate, so a three-line repo is not
  punished for having no "limitations" section. That gate is also why the `ENTERABLE-WEAK`
  grade needs a >200 character document to be reachable — which is itself worth knowing.

## The dead branch

`verdict()` originally returned `ENTERABLE` before it could reach the `WEAK` branch, so
`ENTERABLE-WEAK` was **unreachable** — and the first fleet report printed *"0 are
ENTERABLE-WEAK"* as though it were a finding about the fleet. It was a finding about the
instrument.

That is the sixth dead-check-or-wrong-number bug this session, and the reason `CASEBOOK`
in `artifact-first` exists. **A linter that cannot produce a wrong grade is not a linter.**
