# The instrument registry

*Every failure this project has found was a failure of an instrument nobody had
characterised. This file exists so the next one is a known quantity.*

> An instrument is not an instrument because it returns a number. It is an
> instrument because it has been shown to return the **right** number on a case
> where the right number is already known.

Generated from `instruments.json` by `render.py`. Validate with `validate.py`.

## The three failure classes

**`context_starved`** — The instrument could not see the thing it was measuring about. It answered anyway. Fix: make the unseeable visible to the instrument (add the rule to the state, report the candidate count, stop filtering the corpus's own vocabulary).

**`context_saturated`** — The instrument saw plenty and returned a constant. No amount of extra context helps. Fix: replace the instrument, or demote it to advisory. Detect ONLY with a known-answer control.

**`uncharacterised`** — Never tested against a known answer. Everything is this until proven otherwise.

The first two are opposites, and you cannot tell them apart without a known-answer
control. That is the whole reason the control is not optional.

## What is actually working

### `jev.noul`

- **used for:** the fleet canon gate (p > 0.7)
- **known good:** discriminates in regime B (judgement vs stated criteria); subject-NAMED questions batch safely at 2.5x lower cost
- **known failure:** regime A1 returns 0.05 on unknowable facts - a confident NO about something it cannot know. Harmless for the canon gate, dangerous as a fact-checker.
- **KAT:** `AI-Writings/labs/jev-kat/jev_kat.mjs` → **PASS**

### `jev.choice`

- **used for:** multi-option triage, batched
- **known good:** batches safely; correct pick at confidence 1.00; survives inside a mixed-type batch where noul collapses
- **known failure:** the ARGMAX is the wrong readout - on a 4-option question the correct call picked the second-highest. Read the DISTRIBUTION.
- **KAT:** `AI-Writings/labs/jev-kat/jev_kat.mjs` → **PASS**

### `gate.semantic-rule-rich-batched`

- **used for:** CM1 arm B round 4
- **known good:** 12/12 with flow {12 DRAFT_PASS} - zero doubt, zero retry, zero pinch. 0.28s vs 6.9s (25x), jev 1559 vs 6965 (4.5x cheaper), calibration +0.119
- **known failure:** none measured yet
- **KAT:** `none - but 24 frozen named noul questions in ONE call is itself a known-answer control` → **INHERENT**
- **caveat:** r4 changed TWO factors vs r3 (rule-in-state AND batching). The claim 'rich state + batching' is confounded. An unbatched rule-rich arm would split it.

## What is quietly broken

These all return a number. That is the problem.

### `jev.score` — *context_saturated*

- **used for:** was proposed for a 5-level stranger-usability rubric; MUST NOT gate anything
- **failure:** near-constant. numpy 2.500, a reference port with 1285 passing assertions 2.485, an EMPTY SHELL 2.500. Rank-unstable across reps. Confidence sat at ~0.62 and DID NOT DROP to signal the failure.
- **evidence:** quilt-research-canons/research/jev-kat-result-2026-09-29.md

- **KAT:** FAIL_DISCRIMINATION (`AI-Writings/labs/jev-kat/jev_kat.mjs`)

### `content.aperture-matcher` — *context_starved*

- **used for:** frame-delta estimation for glyph/ascii video
- **failure:** on a repeating texture panned one cell it reported 33.2% unmatched where 100.0% of cells truly moved. 67 points under-report, looking reasonable. It returned A match, not THE match, and never said how many candidates existed.
- **still good at:** on aperiodic content it tracks ground truth
- **fix:** disambiguation check - report candidate count. A motion vector removes the ambiguity by construction.

- **KAT:** NONE

### `gate.semantic-rule-blind` — *context_starved*

- **used for:** CM1 arm B, quilt-gpu-lab round 3
- **failure:** asked whether a draft followed the rule while the rule was ABSENT from its state. Manufactured doubt on 9/12 correct drafts at p0.5 and 12/12 at p0.7. Accuracy stayed 12/12 so the harm was invisible; only the flow distribution showed it.
- **still good at:** rescues unparseable output when paired with a format gate
- **evidence:** SuperInstance/quilt-gpu-lab RESULTS.md CM1 r3/r4

- **KAT:** NONE

### `harness.rounds-2-label-leak` — *context_starved*

- **used for:** multi-voice chord, round 2
- **failure:** round 2 shipped the voice LABEL into the view; voices attacked each other's register descriptors instead of their arguments, and 3 of 6 collapsed onto one generic answer. A chorus that can attack labels has stopped disagreeing about the thing.
- **still good at:** round 1 with a fact seed diverged properly across 6 voices
- **fix:** shipped - anonymous attribution in the round-2 view, braid targets the argument

- **KAT:** NONE

### `search.mutate-pool` — *context_starved*

- **used for:** MicroMoth-quilt search engine, indel-insert class
- **failure:** the indel-insert pool is hard-wired to 2-wire, so insert can NEVER touch wire 2. Structurally silent: the engine reports draws it could not have made.
- **still good at:** the replace class does reach wire 2
- **evidence:** MicroMoth-quilt receipts/exp018-hard-root-autopsy.json

- **KAT:** NONE

### `keyword.the-wheel` — *context_starved*

- **used for:** projects/the-wheel - paper-to-artifact matching
- **failure:** the STOP list filtered the corpus's OWN vocabulary (quilt, cell, model, system, architecture, design) so papers could not see artifacts named with those words. A stop word is generic relative to the CORPUS; in this corpus those words are how the fleet names things.
- **still good at:** after the STOP-list fix, SUPPORTED 56->68 and papers-with-a-gap 27->23
- **residual (not fixed):** 23 of 28 papers still carry a GAP; the polarity is ~50% prevalent and carries little information. The real fix is to read the paper BODY for distinctive terms, not the filename.

- **KAT:** NONE

## The number that matters

**5 of 9 instruments in this registry have no known-answer control.**

That is the honest state of the fleet's measurement apparatus. It is also the whole
remaining work: not more instruments, and not more findings, but **the small test
that proves each existing one is telling the truth.**

Five of the six broken entries above were found by accident, by something downstream
noticing. A control turns an accident into a gate.

## Adding an instrument

```jsonc
{ "id": "...", "class": "characterised | BROKEN | characterised-partial | proposed",
  "failure_class": "context_starved | context_saturated | uncharacterised | null",
  "uses": "what depends on it",
  "known_good": "...", "known_failure": "...",
  "kat": "path or null", "kat_result": "PASS | FAIL_* | NONE | INHERENT",
  "evidence": "where the numbers are" }
```

`validate.py` fails (exit 2) if a `characterised` instrument names no KAT, if a
`BROKEN` one claims a passing KAT, if a failure class is outside the three, or if a
`known_failure` key is missing entirely. `validate.py --self-test` runs 6 legs
including one negative control per rule.

