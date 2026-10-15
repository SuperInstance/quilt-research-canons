# PR #16 — the spike that surfaced §6

**Repo:** `patchwork-quilt/git.pp-ng`
**PR:** [#16](https://github.com/patchwork-quilt/git.pp-ng/pull/16)
**Title:** spike: retraction (dispute+settlement) — doctrine flag open
**Author:** SuperInstance
**Created:** 2026-10-15
**Status:** Draft, "for referee review only. Do not merge."

## What the PR ships

- `dispute` and `settlement` as new record kinds
- A settlement pass that computes the retracted set from the record set alone, before the fold runs on what stands
- The settlement's `authoritative` predicate: the target's author (self-disavowal) OR captain-class (author of an applied override in the set — the spike's set-internal proxy for the duel's captain-only settlement)
- Voiding on upheld; graph position preserved; descendants not orphaned; meta records excluded from `order`, tallies, `recordsBehind`
- 1151/1151 conformance (863 pre-existing + 30 retraction families + 258 sprinkled variants)
- 28 pinned answers (`RET_EXPECTED`) for the bite cases
- 297 retraction statuses asserted

## What the PR explicitly does not do

- It does not commit to a doctrine for §6. The mechanics support all three options; the surface is silent on the difference.
- The PR body says: *"§6 of the design duel: may a third party's accusation, once ratified, stain a record its author still stands behind? This spike implements the mechanics (a captain-class settlement upholding a third party's dispute does retract the target — `ret-captain-upheld`) without the stain: no output marks a retraction as contested, and nothing distinguishes self-retraction from ratified accusation in any surface. The mechanics are built so either ruling can land later; the flag is recorded here and in `docs/RETRACTION-SPIKE.md` rather than resolved by the fold."*

## What the captain's verdict looks like

See `../DOCTRINE.md` for the three options and the recommendation. The PR graduates from "spike, do not merge" to "merge as §6 doctrine: Option {I,II,III}" once the captain signs.
