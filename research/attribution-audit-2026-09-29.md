---
title: The attribution audit — 791 commits, 0 signed
date: 2026-09-29
scope: 18 active repos, 791 commits, top 100 per repo
---

The room's structural finding, made into a number: **an outsider cannot bind a commit to
keeper vs Mavis vs Claude vs CCC.** Now it is measurable rather than arguable.

## The measurement

| | |
|---|---|
| repos scanned | 18 (the active layer) |
| commits examined | 791 |
| commits with a **cryptographically verified** signature | **0** |
| distinct self-asserted author names | **12** |
| distinct GitHub-authenticated logins | 1 human + 3 bots + 3 collaborators |

Every author name in the table is a **string the committer chose**. `Z User` could be the
keeper, a script, or a person at a keyboard. `CCC` is an agent. `Claude` is an agent. There is
nothing an outsider can check that would distinguish them.

## The self-asserted author names, whole active layer

```
Casey Digennaro          177
SuperInstance            142
Claude                    97      (agent)
Z User                    95      (keeper)
CCC                       74      (agent)
Astryd Park               44
Quilt                     38
dependabot[bot]           35
github-actions[bot]       15
Mavis Agent               14      (agent)
The Cowboy                10
Casey                     10
kimi1                      3      (agent)
Mavis                      1      (agent)
```

## Why this matters beyond tidiness

1. **The two-reader rule cannot be audited.** A receipt that says "reader 2: Mavis" is
   self-asserted. Anyone can relabel a commit as any author. The discipline is real; the
   evidence for it is not externally checkable.
2. **Reputation cannot compound per agent.** All trust attaches to one node, so no agent can
   accrue a track record an outsider can read.
3. **Compromise is unbounded.** One credential can write all 4,856 repos. There is no
   per-agent scope, no per-agent revocation, and no least privilege.
4. **Branch protection is theatre.** GitHub sees one principal, so "requires a different
   reviewer" cannot be enforced against an agent that is also the author.

## The fix, in order of cost

**Cheap, today, unilaterally:**

- Sign commits. A fleet-scoped GPG or SSH signing key makes author identity verifiable
  without changing any workflow. GPG is available in this environment. It does not separate
  agents from each other — it binds commits to a *fleet* key, which is a real improvement over
  a string and an incomplete one.
- Standardize the author-name vocabulary. Twelve names for what may be five actors is
  fragmentation, not identity. One canonical label per actor, in a documented place.

**Expensive, needs Casey's decision, and actually fixes it:**

- **Per-agent GitHub Apps**, one per agent identity, installed with least-privilege repo
  scopes. That gives per-agent authentication, per-agent revocation, audit-log actor
  identity, and — the thing that matters — a *second principal* so branch protection can
  require a different reviewer than the author.
- App creation requires a manifest, a reachable webhook URL, and it mints a private key. Not
  something to do unilaterally on someone's account. Reported, not done.

## The honest summary

The fleet's verification discipline is unusually strong and almost entirely **internal**. The
externalisability audit found 0 of 10 sealed predictions decidable by a stranger. This audit
finds why that is structural rather than accidental: the substrate has no externally
verifiable identity to anchor a verdict to.

**791 commits, 0 signed.** That is the number that goes with "0 of 10 decidable by a stranger."
