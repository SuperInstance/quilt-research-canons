# Zeroshot-agent frontend audit — 2026-09-30

Lens: an agent with zero context lands on the repo's front door. Can it answer, in one screenful:
**(1)** what is this and what paradigm does it serve, **(2)** what can I run in under five minutes,
**(3)** what receipts prove the claims, **(4)** what is my next action? A frontend that answers all four
converts a stranger into a contributor; anything less converts them into an archaeologist.

## Scores (8 load-bearing repos)

| repo | what/why | <5-min run | receipts | next action | verdict |
|---|---|---|---|---|---|
| MicroMoth-quilt | ✓✓ two-things-up-front, stranger's-60s version | ✓ | ✓ receipt ledger | implicit | **exemplary** |
| fleet-seeds | ✓✓ one-idea framing, seed-drill metaphor | ✓ | ✓ charter+smoke | ✓ | **exemplary** |
| quilt-research-canons | ✓ hub framing | ✓ sprints | ✓ linked | ✓ SPRINT-LINEAGE | **stale** — founding-snapshot tree + "all artifacts dated 2026-09-24" misled agents past ~60 newer receipts → FIXED this audit (rolling pointers + snapshot label) |
| quilt-jev-toolkit | ✓ quickstart | ✓ | partial | partial | **env-name trap** — README/code required `TYPESAFEAI_KEY`; fleet keyfile standardizes `TYPESAFE_API_KEY`; agents following the fleet standard hit KeyError → FIXED (accept both, README renamed) |
| kvrs | ✓✓ crates-grade badges | ✓ | ✓ CI badges | via docs.rs | good |
| quilt-codespace | ✓ diagram-first | ✓ | partial | partial | good |
| quilt-pincher | ✓ ASCII identity, tier framing | ✓ | ✓ CODEOWNERS/SECURITY | partial | good |
| quilt-c | ✓ charter link | ✓ | ✓ byte-exact hash badge | ✓ | **truncated sentence** mid-README ("byte-exact with the rest of the polyformalism." + stray backtick) → FIXED |

## Patterns worth keeping (do these everywhere)

1. **Two-things-up-front** (MicroMoth): name what the repo is AND what the fleet added, above the fold.
2. **Stranger's-60-second version** (MicroMoth): one paragraph a stranger can verify without our vocabulary.
3. **Rolling pointers over frozen trees** (canons, now): "start here" links must be kept current or labeled as snapshot; a stale map is worse than no map for an agent (it trusts maps).
4. **Fleet-standard env names with legacy fallback** (jev-toolkit, now): an agent with the fleet keyfile should never KeyError on the front door.

## Gaps deferred (recorded, not fixed this round)

- PersonalLog's frontend is app-user-facing, not agent-facing — acceptable for its role; revisit if agents will operate it.
- Archived repos (edge-native-paper) still surface phantom open PRs in account-wide queries — note in org docs that archived ≠ merged.
- quilt-pincher "next action" could name the canonical first pinch command explicitly.

## Crosspollination notes (team signals from the PR sweep)

- **Mavis Agent** performs CI/deps maintenance (actions bumps, axe-core drift) — the CI-repair lane complements its cadence.
- **dependabot** labels missing repo-wide (`dependencies`, `npm`) — small org-level `.github` fix candidate for whoever holds the label keys.
- **Casey** merges with receipt-style titles — fleet convention holds across humans and agents.
- Archived `edge-native-paper` PRs #1/#2 contain completed honesty work that never landed (repo archived mid-flight); their fact-check content survives only in the PR branch. If anyone unarchives, merge before anything else.
