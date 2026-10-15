# §6 doctrine sanity check

> A mechanical demonstration that the three §6 doctrine options produce different observable behaviour, so the captain's choice is not a no-op.

The §6 doctrine question (PR #16) is whether a captain upholding a third-party dispute against a record whose author still stands behind it should:
- **Option I (pure self-retraction):** not retract; mark as warning only
- **Option II (captain-retract, no stain):** retract; surface is silent on captain-vs-self
- **Option III (captain-retract, stain):** retract; surface marks the contestation

To prove these are distinct, this document shows a concrete case where the three options diverge.

## The case

- A writes `task-a` (a `task` record). `task-a.effects.config.timeout = 30`.
- B writes `dispute-1` (a `dispute` record) against `task-a`. `dispute-1.target = task-a`, `dispute-1.reason = "B accuses"`.
- C writes `settlement-1` (a `settlement` record) upholding B's dispute. `settlement-1.dispute = dispute-1`, `settlement-1.resolution = upheld`, `settlement-1.author = C` (captain).
- A does NOT write a retraction. A still stands behind `task-a`.
- D writes `task-d` (a `task` record) that depends on `task-a` setting `config.timeout = 30`.

## What the three options produce

| Option | `derive(records).state.config.timeout` | Surface marks contestation? |
|---|---|---|
| I (pure self-retraction) | **30** (from `task-a`, untouched) | Yes — `task-a.contestedBy = [B, C]` |
| II (captain-retract, no stain) | **?** (depends on what other records set the key) | No — surface is silent |
| III (captain-retract, stain) | **?** | Yes — `task-a.contested = true`, the closure root includes the contestation, the surface shows the dispute/settlement chain |

For Option II, the value depends on the rest of the record set:
- If no other record sets `config.timeout`, the value is `null` (the key is unset; the fold's per-key resolution only finds retracted records' values through their graph position, not their effects).
- If `task-d` (a descendant of `task-a`) sets `config.timeout = 99`, the value is `99` — `task-d`'s effects flow through the retracted `task-a` (graph position preserved, descendants not orphaned, no cleanliness loan).

For Option III, the value follows the same rule as II (the bite is identical), but the closure root is different because the leaf domain broadens to cover `dispute` and `settlement` records' `target` and `author` fields.

## Why this matters

If the three options produced the same observable state and the same closure root, the choice would be cosmetic. They do not:
- Option I leaves `config.timeout` set; Options II and III void it.
- Option II and III share the bite but differ on the surface and the closure root.
- Option I's "warning surface" needs a new field in the record set; Option III's "contested" annotation needs a leaf-domain change; Option II needs neither.

The right design is the one that matches the captain's intent. This sanity check is a mechanical demonstration that the choices are not interchangeable.

## What to do with this

- Read it alongside `DOCTRINE.md` in `quilt-research-canons/research/retraction-doctrine-2026-10-15/`.
- Pick an option.
- The choice is recorded in `docs/RETRACTION-SPIKE.md` (in `patchwork-quilt/git.pp-ng`) and PR #16 graduates.

