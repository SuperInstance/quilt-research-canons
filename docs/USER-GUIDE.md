# quilt-research-canons — User Guide
> For a researcher, analyst, or agent who wants to *use* the canon: run its instruments,
> quote its measurements, and extend its receipt chain — without becoming a developer of
> the fleet runtime.

## What you get

You get four distinct things, and it pays to know which one you are holding:

1. **A measured-claims library.** Dated reports that state a hypothesis, the run that
   tested it, and the verdict — e.g. the fleet-negation experiment (11/11 models
   measured negation-blind, pre-registered P1–P4, judge 3.73/4), the JEV gate
   experiments (the gate is a step function, not a scale), and the externalisability
   audit (10/10 sealed predictions had falsifiers, 0/10 were externally decidable).
2. **Runnable instruments.** Three JEV gate tools (`tools/`), a fault-injection-proven
   claim linter (`projects/artifact-first/`), a legibility scorer for READMEs
   (`projects/fleet-legend/`), a trained text-classifier for gameable claims
   (`projects/jev-lite/`), and a repo-process classifier (`projects/process-signature/`).
3. **A self-extending protocol.** The sprint lineage: every experiment script ends with
   the spec for its successor, so the roadmap lives in the directory, not in memory.
4. **A negative-results ledger.** Refutations are kept, not cleaned: 11 of 35
   pre-registered loop predictions were refuted, and those refutations rewrote the
   operating rules (see `research/loop/INDEX.md`).

## Install

There is nothing to install. The repo is Python-3-stdlib only for everything offline;
git-clone and run:

```bash
git clone https://github.com/SuperInstance/quilt-research-canons
cd quilt-research-canons
python3 --version   # anything >= 3.9 works for the offline instruments
```

For anything that calls the JEV oracle you additionally need an access key in the
environment (`export TYPESAFEAI_KEY=...` — value from your own account; none are
committed here).

## First success in 5 minutes

Run the artifact-first gate suite — it needs no network, no key, and demonstrates the
repo's core doctrine (conclusions ride on artifacts, and gates must be provably able to
fail):

```bash
python3 projects/artifact-first/tests/test_gates.py
```

Expected output (tail):

```
[PASS] grounded claim with a clean report PASSES the combined gate
[PASS] unsourced claim FAILS even with a clean report
[PASS] NEGATIVE: the combined gate is not just gate 1 -- a grounded claim can still fail it
============================================================
16/16 correct
```

Note the last `[PASS] NEGATIVE:` lines — the suite deliberately breaks a gate and checks
the suite notices. A passing suite that cannot fail is worse than no suite; this repo
tests that.

## Everyday usage

### 1. Ask whether an artifact claim passes the two-axis JEV gate

The current-generation gate (`jev_gate2.py`) asks one `choice`-type question with four
criteria and reads the probability distribution, avoiding the `noul` batching collapse:

```bash
export TYPESAFEAI_KEY=...   # required; the script calls api.typesafe.ai
python3 tools/jev_gate2.py --state '<artifact description text>'
# prints both/neither distribution + promote/kill verdict
# promote iff P(both_axes) > P(neither) and P(both_axes) > threshold
```

### 2. Batch several verdict questions safely

Batching is safe **only when each question names its subject** (spread 0.57 vs 0.01
unnamed — 11 rounds of loop evidence):

```bash
export TYPESAFEAI_KEY=...
python3 tools/jev_batch.py
# edit the QUESTIONS block first: each question must carry a fixed prefix naming
# the subject it is about; unnamed noul batches collapse to one number
```

### 3. Score a README (or any onboarding surface) for legibility

`fleet-legend` ships the scorer used on 100 live fleet repos, with the corpus and
verdicts it produced:

```bash
python3 projects/fleet-legend/lint_legibility.py <repo-path-or-url>
# verdict vocabulary: ENTERABLE-STRONG / ENTERABLE-WEAK / INVISIBLE (see verdicts.json)
```

### 4. Classify a claim's text as gameable vs measured

`jev-lite` is a 15-feature logistic regression trained on real oracle measurements, with
a known-answer control asserted at train time:

```bash
python3 projects/jev-lite/train.py     # retrains, asserts held-out AUC >= 0.85
# side effect: rewrites projects/jev-lite/weights.json — restore or commit after
python3 - <<'EOF'
import json, sys; sys.path.insert(0, "projects/jev-lite")
from features import extract
from weights import *   # or read weights.json directly; see collect.py for the scorer loop
EOF
```

### 5. Run a play-test of an instrument before trusting it

`toolchain-kar` is the worked example: an "is each tool up?" check that reported 4/11 and
was wrong, because three distinct failure classes were averaged into one number. Re-run
its probe and read how the classes separate:

```bash
python3 projects/toolchain-kar/probe.py   # reports IDENTITY / SHAPE / HEALTH classes per tool
```

### 6. Write your own receipt into the canon

Follow the sprint contract (`research/SPRINT-LINEAGE.md`): header docstring with lineage
id + doctrine + `NEXT-SPRINT SPEC`, an output artifact, and a trailer line
`>>> NEXT: write sprint-XXX-(NNN+1).py per the spec in this file's header <<<`. Then
append a dated report under `research/` and a row to `research/loop/loop_state.json` if
you pre-registered predictions.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `KeyError: 'TYPESAFEAI_KEY'` from a sprint or tool | The script reads the key from the env, deliberately | `export TYPESAFEAI_KEY=...`; never paste a key into a file or a receipt |
| Batched `noul` questions all return the same number | Unnamed subjects — the documented collapse (spread 0.01) | Prefix every question with the subject it concerns; see `tools/jev_batch.py` |
| A `score`-type gate passes an empty shell | `score` is a constant generator (~2.500) that grades nothing | Use `choice`/`noul` gates: `tools/jev_gate2.py`, `tools/jev_gate.py` |
| `train.py` leaves `weights.json` modified in git | Documented side effect of training | `git checkout -- projects/jev-lite/weights.json` (or commit deliberately) |
| Fresh `test_gates.py` says 16/16 but `test_output.txt` says 17/17 | Stored receipt predates a suite edit | Trust the fresh run; the discrepancy is flagged in docs, not silently reconciled |
| CI fails on `research/superinstance-bitlaw/**` pushes | Regenerated codecs must be byte-identical across two runs | Run `python3 gen.py && python3 frame_gen.py` (Node 22 available), commit the regenerated bytes |
| A claim in a report contradicts a number elsewhere | Real: some claims were corrected in place and corrections live in the receipts | Read the receipt and the correction section; cite the corrected form |

## FAQ

**Is this repo the fleet?** No. It is the research-artifact layer for one session line.
The fleet is ~4,856 repos (per the 2026-09-29 census in `research/HANDOFF.md`) and this
repo is deliberately not a census of it.

**Can I trust the numbers?** Each number is only as good as its receipt. Claims with a
`frontier_run` or `test_output` artifact are runnable checks; prose claims are not
independently verified, and the README says so in its "What this repository does NOT
do" section. The refutations in `research/loop/` are the most trustworthy content in
the repo, because they were paid for.

**Why are there two JEV gate tools (`jev_gate.py` and `jev_gate2.py`)?** They implement
two generations of the same idea under different constraints discovered by the loop:
`jev_gate.py` asks two `noul` questions in two separate calls and min-aggregates;
`jev_gate2.py` asks one `choice` question and reads the distribution, which survives
everything the loop learned about batching. Read both headers; they are the receipt.

**Why do refuted predictions stay in `loop_state.json` instead of being deleted?**
Because a loop that only confirms cannot correct a belief. 11 of 35 predictions were
refuted and two of the refutations reversed earlier operating rules ("one question per
call", "instruction dedup fixes batching"). Deleting them would re-arm the trap.

**Do I need a GPU?** No. `projects/gpu-lab/` experiments all have CPU fallbacks and — the
whole point — report which path they took. A benchmark that silently falls back to CPU
and reports the CPU number as a GPU result is the exact failure that project exists to
prevent.

**Where do the sprint outputs live if the scripts write to `/workspace/research/`?**
The founding-sprint outputs were committed into `research/` (`jev-velocity.json`,
`moth-fidelity-matrix.{json,md}`) after the run. On your machine, either create
`/workspace/research/` or edit the `OUT` constant at the top of the sprint script —
the path is declared in each header's `OUTPUT` section.
