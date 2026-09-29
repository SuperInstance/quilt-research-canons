# process-signature

**Read a repo's shape and report what PROCESS it is running.**

Not how good it is. What it does.

## Why

Casey asked for the *processes* of different agents to be studied, and for the novel
thinking patterns to be found in the **differences** between how I and others approach
this. The differences are real, and they are already in the fleet — but they are only
visible in the **artifacts** each process leaves behind, never in the prose describing it.

Read the fleet's own lineage and the process layer is obvious:

```
recipe → brewer → walker → receipts → schema-registry → fleet-snapshot → bootstrap → CLI
```

Other agents built a **recursive self-maintenance layer**: tools that ship the fleet's
own methods as artifacts, so a new machine can reconstruct the fleet rather than remember
it. Tonight I solved the same wipe problem from the other direction — pushing to git after
the 60th-odd reconstruction. Same problem, two architectures, and theirs is recursive: the
snapshot tool captures a fleet that *contains the snapshot tool*.

That difference is only visible if you look at what each one leaves on disk. Which is
what this does.

## The claim under test

A process archetype is **readable off the file tree**. A repo that pre-registers leaves a
registration file. A repo that chains witnesses leaves a `.jsonl` ledger. A repo that can
restore itself ships a bootstrap. A repo that falsifies leaves injections in its test
names. You do not need to read a word of prose to know which process is running.

The stronger claim, and the one worth the instrument:

> **A repo can describe a rigorous process in prose and still leave no trace of running one,
> and the two are mechanically separable.**

The legibility census found 55 repos that never say what they do *not* do, 59 that never
say what to do when they fail — while receipts were the *best*-kept obligation at only 14
missing. That asymmetry implies a class of repo that is heavily documented and barely
verified. This instrument says whether that class is detectable **without reading prose**.

## Path archetypes vs text archetypes

The distinction is load-bearing and it was learned by getting it wrong.

| | source | status when only a tree is available |
|---|---|---|
| **PATH** | filenames and directories | judged |
| **TEXT** | file contents | **UNKNOWN, never assumed absent** |

An earlier version matched field-name patterns like `prev_witness` against **file paths**,
so `witness-chained` could essentially never fire — a dead check wearing a real check's
name. Text archetypes now report `unknown` rather than guessing, because **an unmeasured
thing is not a missing thing**, and a linter that cannot fire is a decoration.

## Grades

Graded on **path evidence only**, so the whole sweep is reproducible from a tree listing
with no content fetch.

| grade | meaning |
|---|---|
| `SELF-AUDITING` | falsification-first + witness-chained |
| `PRE-REGISTERED+CHAINED` | pre-registered + witness-chained |
| `PUBLISHABLE` | externally-checkable or self-hosting |
| `RECEIPTED` | witness-chained or contract-enforcing |
| `PROCESS-PRESENT-UNCLASSIFIED` | process artifacts, no recognised combination |
| `NARRATIVE-FIRST` | code or docs, and **none** of the process artifacts |
| `EMPTY` | nothing |

## The controls

Both are in the module and both run on every invocation.

**Negative control** — a repo with real code, real docs, and prose that says *"we have a
receipt for every cell, the canon is verified, each witness is sealed, our schema is
enforced, see our pre-registration"* plus a Limitations section and a Troubleshooting
section. It must grade `NARRATIVE-FIRST`.

It does. **The prose says every word a rigorous repo would say and the path evidence still
says nothing happened.** That single control is the instrument's entire thesis.

**Positive control** — the same prose *plus* the artifacts: `Makefile`, `LICENSE`,
`tests/test_injection.py`, a CI workflow, `lode/registration.jsonl`,
`fleet/witnesses.jsonl`, `tools/release_verify.mjs`, `schema/cell.schema.json`. It must
clear the archetypes, and it grades `SELF-AUDITING`.

## Run it

```bash
python3 process_signature.py        # runs both controls
python3 sweep.py 60                 # sweep the 60 largest non-fork repos
```

`sweep.py` ranks by **file count, never by name prefix** — the rule this session paid for.
`claw` (7,445 files) never appeared in a single prefix search all day and is the proof that
the search strategy, not the difficulty, was the problem.

## What this does not do

- It does not judge quality. A repo with a perfect process signature can still be
  worthless; `claw` has a rich process surface and a README claiming three mechanisms
  that appear zero times in 7,445 files.
- It does not read code. It reads **shape**. Two repos with identical structure and
  opposite quality are indistinguishable here, and that is a deliberate limit — shape is
  cheap to check and the point is to make the first pass cheap.
- The sweep is a **sample**, and the sample is size-ranked, so it is biased toward large
  repos. Every number it prints is scoped to the repos it actually fetched.

---

## The measured result — 60 largest non-fork repos

```
GRADE DISTRIBUTION (path evidence only, reproducible from a tree listing)
  NARRATIVE-FIRST                 28  ############################
  PUBLISHABLE                     20  ####################
  RECEIPTED                        6  ######
  PROCESS-PRESENT-UNCLASSIFIED     5  #####
  SELF-AUDITING                    1  #

PATH EVIDENCE FREQUENCY
  recipe-grown            22/60  (37%)
  contract-enforcing      20/60  (33%)
  self-hosting            20/60  (33%)
  single-command          17/60  (28%)
  falsification-first     13/60  (22%)
  externally-checkable     4/60  (7%)
  pre-registered           3/60  (5%)
  witness-chained          1/60  (2%)   <-- the fleet's central doctrine
```

**`witness-chained` fires on one repo in sixty.** The witness log is the fleet's central
doctrine — cells are scars, the witness log *is* a prediction, every receipt carries
`prev_witness_id`. And it appears as a path artifact in 2% of the largest repos.

**Read that number as a FLOOR, not a measurement.** The pattern is
`ledger.jsonl$ | history.jsonl$ | witnesses.jsonl$`, so a repo that keeps its witness chain
in a database, or under a different name, is invisible to it. The claim is not "the
doctrine is rare." The claim is that **the doctrine does not reliably leave the artifact
it is named after**, and a reader looking for it will usually not find it.

**The twelve that describe a rigorous process in prose and leave no path trace of running
one** — 12 of 60, and they are not random:

```
fleet-coordinate              murmur-plato-bridge            lau-algebraic-geometry
fleet-resonance               quicunnel                      lau-computer-graphics
lau-leverage-singularity      conservation-law-rs            lau-ffi-bindings
si-variational-bayes          lau-logic-foundations          beta-test-elena
```

**Six are `lau-*`.** That is a *cohort* — a named research programme, each repo small
(9-15 code files, 1-4 docs), each stating an error surface in prose and usually its
negative space, and **none** leaving a machine-checkable trace. It is not sloppy: it
satisfies the two obligations the legibility census found most missing (L4 negative space,
L5 error surface), in words, with no receipt.

## The processes, and the differences

That cohort is the answer to the question, and it is not what I expected.

| archetype | who runs it | how it shows up |
|---|---|---|
| **receipt-first** | me, keeper | 11 opcodes, witness chains, forge seals, pre-registration — the process IS the files |
| **recursive self-hosting** | the brewer/bootstrap lineage | `recipe → brewer → walker → receipts → schema → snapshot → bootstrap → CLI`, where the snapshot captures a fleet containing the snapshot tool |
| **prose-first research** | the `lau-*` cohort | states limits and failure modes in words, ships no receipt, and is *not* thereby worse — it answers a different question |
| **publishable** | 20/60 | a real external surface: a release, a verifier, a bootstrap |

The novel pattern in the difference is not that one of these is better. It is that **the
same fleet holds all four, and only one of them is visible to a reviewer who reads prose.**
Two of the four leave the same artifacts for the same reasons. One of them — mine — is
the one that mistakes its own receipts for a shared language, when the `lau-*` cohort is
running a genuinely different research process four directories away and nobody is
cross-reading either direction.

That is a real thing to fix, and it is fixable without changing anybody's method: the
difference should be *readable*, not just present.
