---
title: The claw audit — the biggest repo in the fleet, and the README is wrong
date: 2026-09-29
subject: SuperInstance/claw
files: 7,445   size: 402 MB   license: MIT   pushed: 2026-08-24
---

The census found it: 6,089 TypeScript files, 2,757 tests, 402 MB. Nine percent of the
account's code in one repository. It has never appeared in a single scout result all day,
**because it does not start with `quilt` and every search this session was a prefix search.**

## What it actually is

A fork of [OpenClaw](https://github.com/openclaw/openclaw) — a real multi-channel AI
gateway (Telegram, LINE, WhatsApp, Discord, web) with channel adapters, a plugin SDK, a
skill system, cron, heartbeat, subagent spawning, and a two-tier memory model
(`memory/YYYY-MM-DD.md` daily notes, `MEMORY.md` curated).

Plus a Rust crate, `claw-engine/`, with `claw-core` and `claw-runtime`:

```
src/agents 883 · src/infra 488 · src/commands 379 · src/gateway 368
src/auto-reply 296 · src/cli 292 · src/channels 159 · src/plugins 114
src/plugin-sdk 111 · src/cron 109 · src/memory 103 · src/media-understanding 65
docs/ 667 markdown files · skills/ 54 skills
```

## The finding: the README claims three mechanisms that are not in the repository

The README says:

> This fork extends OpenClaw with fleet-native integrations: **ternary action routing,
> conservation-aware scheduling, and the γ + η = C enforcement** that keeps the agent
> population in healthy equilibrium.

Measured across all 7,445 files, by filename and by content:

| claimed mechanism | files matching |
|---|---|
| ternary action routing | **0** |
| conservation-aware scheduling | **0** |
| γ + η = C enforcement | **0** |
| quilt | **0** |
| superinstance | **0** |
| cell | **0** |

`package.json` — 24 KB of it — contains none of the terms either. GitHub code search across
the repo returns 0 for each.

## And the one real integration points the OTHER WAY

The SuperInstance surface is **three files**:

```
skills/cocapn-fleet/SKILL.md
skills/cocapn-fleet/scripts/claw_fleet_bridge.py
skills/cocapn-fleet/scripts/test_claw_fleet_bridge.py
```

And the bridge's own docstring says what it is:

> """Fleet Bridge — HTTP API exposing **sunset-ecosystem modules to Claw**."""

So the direction is **sunset-ecosystem → claw**, not claw → fleet. The README frames claw as
extending into the fleet; the code has the fleet's ecosystem being served to claw. A reader
checking the claim would find the opposite relationship. That is worse than an overclaim,
because it is an overclaim with the direction reversed.

## The genuinely important thing, in the place nobody looked

`claw-engine/crates/claw-runtime/src/triggers.rs`:

```rust
pub enum TriggerEvent {
    Timer,
    CellChange(String), // Cell ID
    Message(String),
    Custom(String),
}
```

**`CellChange(String)` is a cell-graph event wired into a real agent runtime's trigger
system.** The cell is not a metaphor in a document here; it is a variant in a Rust enum that
a scheduler matches on. That is the fleet doctrine ("the cell is a scar, the watch is the
user") realised in the one file no scout had opened, inside the one repo no prefix search
had found.

## What this changes about how to scout

The census said the interesting repos are invisible to prefix search. It understated it.
`claw` is not a hard repo to find — it is 6,089 TypeScript files of a real product with 667
docs. It was invisible because **the search strategy was wrong, not because the repo is
weird.**

Concretely: every scout today searched `user:SuperInstance <prefix>`. The three most
substantial repositories in the account by file count are `claw` (6,089 ts),
`hermes-construct`, and `rune-quilt` — and the first does not match the prefix at all.

**The rule that replaces it: rank by file count and test count, then open the top twenty.**
A census already computes both. The search was doing work the census had already done.

## Maintainer notes on a 402 MB fork

Not accusations, just the questions a successor inherits:

- **Upstream sync.** It is a fork of a live project. There is no visible record here of when
  it was last synced, and 402 MB of a moving target is a lot to rebase.
- **Licence.** MIT, correct and detectable — one of only 12 of 700 scanned repos with a
  clean licence, and worth noting that it is one.
- **The README.** Three claimed mechanisms and zero implementations is a documentation
  defect that will cost the next reader an hour, and it is the first thing the `skeptic` user
  in the five-user review would have found.

## What I am not doing

I have not opened an issue on `claw` and I have not edited its README. The README author may
have a branch with the work, or a plan, or a reason. **This is a reading, not a verdict** —
and the honest way to record a reading is to say what was measured and let the author answer.
