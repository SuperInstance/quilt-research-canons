# §6 Doctrine — summary

This directory holds the design canon for the §6 retraction-doctrine question raised by PR #16 (`patchwork-quilt/git.pp-ng#16`, "spike: retraction (dispute+settlement) — doctrine flag open").

## The question

May a third party's accusation, once ratified (by a captain-class settlement), stain a record its author still stands behind?

## The three options

| # | Name | Bite | Surface marks contestation | Conformance cost |
|---|---|---|---|---|
| I | Pure self-retraction | Author only | Captain upholds a *warning* on the record | Zero new code |
| II | Captain-retract, no stain | Captain upholds = retract | Silent on captain vs self | Zero new code |
| III | Captain-retract, stain | Captain upholds = retract | The record is durably marked `contested`; the closure root includes the annotation; consumers must render it | New leaf domain, new corpus family |

## The recommendation

**Option II.** The captain's authority is a reasoned record (the settlement) that lives in the substrate; the record's content is its bite. No new magic. The captain's signature on the settlement is the existing accountability; adding a doctrinal mark to every captain action against a standing author pays a long-term cost for a short-term abstraction. Revisit when a contested case appears in production.

## The load-bearing invariant (any option must pass)

For any record `r` and a captain-class settlement `s` upholding a third-party dispute against `r`:

1. `derive(records \ {r})` produces `S'`; `derive(records)` produces `S''`; `S''` differs from `S'` *only* on keys `r` would have set.
2. Descendants of `r` are not orphaned; ancestry runs through `r`, but `r` lends no cleanliness.
3. A new record `r2` setting a key `r` would have set, with parents that include `r`, applies and wins by the existing class+ancestry rule. The captain retracts `r` once; re-disputing requires a new dispute.

## Files

- `DOCTRINE.md` — the full design doc (the three options in detail, the rationale, the "doctrine" framing, the conformance test, the "what to do now" checklist).
- `SANITY-CHECK.md` — a mechanical demonstration that the three options produce different observable behaviour (one concrete case where they diverge, side-by-side).
- `pr16-link.md` — the PR that surfaced the question.

## What to do now

The captain (Casey, or whoever is on desk) reads `DOCTRINE.md` and either:
- **Signs** the chosen option into `docs/RETRACTION-SPIKE.md` (in `patchwork-quilt/git.pp-ng`) and merges PR #16.
- **Counter-signs** with a different option; this doc then becomes the paper trail for the next review.
