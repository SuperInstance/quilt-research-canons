# Research canon — index

> A navigable map of the dated artifacts in `quilt-research-canons/research/`. Updated 2026-10-15.

The canon holds ~60 dated artifact directories, one per lane per receipt. Newest are at the top of the directory listing; this index groups them by topic for navigation.

## By topic

### Doctrines and design choices

- `retraction-doctrine-2026-10-15/` — **§6 doctrine.** Three options (pure self-retraction / captain-retract-no-stain / captain-retract-and-stain), recommended Option II, with the load-bearing invariant (the retract-then-supersede cycle test). The captain's call.

### Quarterly-style state reports

- `state-of-the-quilt-2026-10-15/` — **The current report.** What's merged in the active stream, what's open, what was built in this session, the open design questions, the honest assessment.

### Creative-break (Taps) entries

- `taps-fallback-2026-10-21T030133Z.md` — **Fallback, single-author.** The three-voice Taps round could not convene (harness absent from a wiped workspace; no voice credentials). Written under the task's fallback clause; no voices ran, no citation graph. Reads as one voice on why the value of a round is the friction at the join.

### Substrate canon (project architecture)

- `HANDOFF.md` — The keeper's handoff. What's known, what's open, what to not rebuild. Section 3 lists the captain's-call items.
- `SPRINT-LINEAGE.md` — The protocol for how each API call leaves a Python run for the next sprint.
- `KEY-ROTATION-2026-10-04.md` — The fleet signing key and rotation policy.
- `active-ledger.md`, `active-ledger/` — The live ledger of agent work.
- `active-repos-report.md` — The active-repos census (this is one of the few that lives flat at `research/`).

### The 2026-09-24 founding snapshot

- `2026-09-24-novel-problems-report.md` — Fork / Reveal / Chorale: H1 falsified+refined, H2 confirmed at 85%, H3 confirmed.
- `SPRINT-LINEAGE.md`, `jev-velocity.json`, `moth-fidelity-matrix.json` — see above.

### Tripartite canon (the three things being held in tension)

- `2026-10-02-tripartite-canon/` — The three-canon report: the substrate, the JEV, the MOTH.

### Substrate-specific deep-dives

- `atlas/` — The atlas of the substrate.
- `codec-gaps/` — Where the substrate's codecs disagree.
- `family/` — The family of related artifacts.
- `growing-pincher/` — How pincher (the reflex engine) grew.
- `jevlab/` — The JEV lab.
- `locality/` — The locality principle in substrate design.
- `loop/` — The loop architecture.
- `2026-10-02-tripartite-canon/` — see above.
- `active-ledger.md` / `active-ledger/` — see above.

### Date-stamped lanes (newest first)

- `state-of-the-quilt-2026-10-15/` — current
- `retraction-doctrine-2026-10-15/` — current
- `2026-10-02-tripartite-canon/` — 13 days ago
- `KEY-ROTATION-2026-10-04.md` — 11 days ago
- `active-ledger.md` — recent
- `active-repos-report.md` — recent
- `2026-09-24-novel-problems-report.md` — founding snapshot, 21 days ago

## By author / bot

- **Mavis (this session, 2026-10-15):** `retraction-doctrine-2026-10-15/`, `state-of-the-quilt-2026-10-15/`, plus updates to `HANDOFF.md` §3.
- **Mavis × Casey session line (ongoing):** all of the above, plus the 53+ scout reports in the repo root (`SCOUT-*.md`).
- **keeper:** the `active-ledger.md` and the JEV / MOTH artifacts.

## How to use this index

- For the **§6 doctrine question:** go to `retraction-doctrine-2026-10-15/`.
- For **what's happening right now:** go to `state-of-the-quilt-2026-10-15/`.
- For the **keeper's handoff** (canonical "what is open, what to not rebuild"): `HANDOFF.md`.
- For **specific subject matter:** drill into the topic directories (atlas, jevlab, moth, etc.).
- For **chronological order:** `ls -lt` in the `research/` directory.

## The two custodian rules

1. **No naked verdicts.** Every claim in this canon has a receipt — a number, a file, a commit SHA. Verdicts without receipts are not canon.
2. **The null model IS the experiment.** Every measurement here is paired with a shuffled-baseline run; if a metric doesn't separate real from shuffled, the metric is a convention, not a signal. The convention is documented as a finding, not promoted to canon.

