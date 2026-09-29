# METHOD — the process study this came from

A single session, five agents, one owner, five unrelated domains. This is the study of
**how**, because a qult is what a quilt becomes when it contains other quilts — and if the
agents' *methods* are the quilt, the interesting structure is the disagreement between
them.

## The roster, by first move

Every one of these ran on the same substrate at the same time. What separates them is the
*first action*, not the effort.

| agent | first move | what that bought |
|---|---|---|
| **herman-historian** | downloaded the CEH 2007 primary PDF, 9pp | verified the main theorem **verbatim**, then asked whether the hypotheses held — and killed a doctrine it was sympathetic to |
| **owner** | hashed `data/c3/manifest.json` | 30 seconds instead of a 30-minute audit, and found **strictly more** than the auditor did |
| **snowball-scout** | read the source and **its call sites** | found `data_encode_full` has zero callers — the one mode-shaped thing in the repo is dead code |
| **casper-critic** | read the report **against itself** | caught a headline its own body refutes two clauses later |
| **jevvy-auditor** | checked the receipt's **own machinery** | a tautological receipt, a mistyped arXiv id, a partly vacuous control |
| **wesley-mechanic** | wrote a script, ran it, iterated | 5 estimators plus a sabotage estimator; found the shots ceiling empirically |

## The pattern in the differences

**Every method that worked reached for an artifact before forming a view.** The historian
reached for the paper. I reached for the hashes. The scout reached for the source and its
call sites. The critic reached for the report against itself.

And every method that produced a wrong answer did the same thing in reverse: formed a
view, then went looking for evidence to fit.

**ARTIFACT BEFORE NARRATIVE.** The correct move in every good case above was a *different
first action*, not more effort. That is why it is cheap to adopt.

## The failure mode is shared, and that is the finding

Five instances, four agents, five unrelated domains, one session.

1. **owner** — wrote "structure costs nothing" into the family experiment *before running
   it*. The data said the opposite on both sides.
2. **owner** — concluded a glyph ramp "round-trips exactly" from **one monotone ramp**,
   which is the easiest possible input for an order-preserving map. A non-monotone field
   falsified it two rounds later.
3. **owner** — wrote `4/196` where the formula wants `4/max(a,b)`: vertex count where side
   length was meant. A confident 30× error, caught by an independent instrument.
4. **snowball-scout** — headline "NO, none of the three has a per-cell mode menu"; body,
   two clauses later: qthe-codec has the only transmitted per-cell mode in any of the three.
5. **gpu-lab auditor** — per casper-critic, an invented headline statistic in a report
   whose entire premise is that the numbers were checked.

The shape is not carelessness. It is **order**: conclusion first, evidence second, and the
evidence then read *through* the conclusion.

## Why the reviewers are a different kind of cell

Producers and verifiers are not the same process run twice. Given the same artifacts,
`casper-critic` and `jevvy-auditor` did something structurally different: they checked
each claim **against itself**, not against the world.

**Every error caught in this session was caught by internal consistency.** The external
checks all passed while the internal ones failed. That is not a coincidence — an invented
statistic is invisible from outside, because nothing outside contradicts it. Only reading
the summary against the body shows it.

A fleet that verifies only outward will ship confidently wrong work at scale, and will do
it faster than a small team that does not. The reviewer is the exocortex — but of the
*self*.

## What this changed

1. **Write the prediction before the run, then make the run able to refute it.** The family
   experiment was worth *more* for having a written-down wrong prediction than it would
   have been with none. The pre-registration doctrine earning its keep by accident.
2. **Make the first action an artifact fetch.** The measure of a method is what it does
   first.
3. **Review inward as well as outward.** Give reviewers an explicit instruction to read
   each claim against the rest of its own report.
4. **Treat "grounded" as necessary, not sufficient.** Which is what `PROOF.md` says, and
   what gate 2 exists for.
