# quilt-research-canons — CTO Brief
> Executive summary. Read time: ~5 minutes.

## One-paragraph value statement

`quilt-research-canons` is the knowledge-transfer asset of the SuperInstance research
line: a receipted bundle of ~60 experiment directories, 12 self-contained instrument
toolkits, a self-extending sprint protocol, and three tuned JEV gate tools. Its value is
measured in avoided re-derivation — it converts findings that would otherwise die in
session memory (and did, across 60+ agent wipes) into artifacts a zero-shot newcomer can
verify in minutes. It is the repo other agents are pointed at first, and it holds the
fleet's most load-bearing negative results.

## What it does & for whom

- **For incoming agents**: a verified onboarding path (README → HANDOFF → loop index)
  that states what is known, what is open, and what must not be re-derived.
- **For researchers**: measured claims with runnable checks — e.g. the JEV batching
  collapse and its fix (subject-naming), the gate-as-step-function finding, the
  externalisability audit, the fleet-negation result (11/11 models).
- **For the fleet's engineering discipline**: instruments that turned findings into
  tooling — the conclusion-before-evidence linter (artifact-first), the README
  legibility scorer (fleet-legend, L1–L5 obligations), the repo-process classifier,
  and the instrument registry (an instrument counts only after it returns the right
  number on a known-answer case).
- **For diligence**: every claim is graded by its receipt; unverified prose is labelled
  as such in the README's own "does NOT do" section.

## Maturity assessment

**Working prototype at "receipted" grade — not a hardened product, by design.**

Evidence for: all offline instruments run green from a fresh clone (16/16 gate tests,
15/15 molt legs, jev-lite held-out AUC 1.000 vs ≥0.85 bar, re-verified wave-69); CI runs
a determinism gate on the bitlaw codecs; the JEV tools carry committed output receipts
and eleven pre-registered loop rounds behind them.

Evidence against: the API-facing sprints require keys and were run on-demand, not
continuously; one stored test receipt (17/17) disagrees with a fresh run (16/16) and the
cause is unexplained; the README's directory tree is a stale founding snapshot; a nested
duplicate directory is lineage noise. The repo is honest about all of this in-repo.

## Risks

| Risk | Severity | Mitigation status |
|---|---|---|
| Stale snapshots quoted as current (externalisability 0/10 → 3/11 in hours) | Medium | Partially mitigated: corrections are appended in receipts (HANDOFF §9); readers must date-stamp what they quote |
| Silent measurement corruption via unnamed-subject batching | High if ignored | Mitigated: rule documented in three places, tool (`jev_batch.py`) implements the fix |
| `score`-type gates fail open | High if ignored | Mitigated: KAT exists (`research/jevlab/`), "do not gate on score" is a standing fleet rule |
| Credential leakage through receipts | High if it occurs | Mitigated by protocol: env-var names only, key-scan before push; rotation receipt format exists (`research/KEY-ROTATION-2026-10-04.md`) |
| Single-account API dependency (Typesafe.ai) for the gate tools | Medium | Accepted: the loop receipts are the moat; porting the gate format to another judge is untested — unverified |
| Unexplained 16/16 vs 17/17 test discrepancy | Low | Flagged in docs; regenerate receipt only alongside a deliberate suite change |

## Cost profile

Near-zero infrastructure cost: a static git repo, one CI workflow (GitHub-hosted
runners, minutes per push), and Cloudflare Workers free tier for the KV-backed index in
`projects/gpu-lab/`. Variable cost is API spend on the judge/oracle calls (Typesafe.ai
`/v1/systemone`); measured envelope: 545 tokens per 4-question batch vs 1,344 for
separate calls (2.5x cheaper), ~200 ms per call. No databases, no servers, no paid
services beyond API usage.

## Strategic options

- **Invest (recommended for one lane)**: close HANDOFF §6 open items — PyPI/OIDC
  trusted publisher and calibration rung 3 are the two with the highest
  information-per-round; both convert internal claims into externally checkable ones.
- **Maintain**: the repo's own doctrine. Append receipts, keep the loop running, keep
  KNOWLEDGE-MAP current. Low cost, high retention value.
- **Harvest learnings**: the L1–L5 legibility obligations and the negative-control
  discipline are directly exportable to any engineering org; the two-axis gate is
  exportable to any LLM-judged pipeline.
- **Retire**: not recommended — the repo is the account's citation backbone (192
  citation resolutions in the wave triage scan) and the only consolidated record of
  several load-bearing negative results.

## Integration surface

- **Upstream in the fleet**: `jev-quilt` (JEV canonical SDK the tools predate/parallel),
  `quilt-c` (the dependency-closed artifact its receipts document), `fleet-seeds`
  (externalisability gate, audited from here), `quilt-gpu-lab` (GPU characterization;
  sibling code in `projects/gpu-lab`).
- **Downstream consumers**: any agent onboarding lane (this repo is the pointed-to
  entry), `fleet-triage` (its resolver resolved 192 citation outcomes against files
  here), the journal (`superinstance-lab/worklog.md` references its lanes repeatedly).
- **External**: audits of outside work — `claw` (9% of account code, README wrong),
  CRDT white-paper results (headline is an identity, one number does not reproduce).
