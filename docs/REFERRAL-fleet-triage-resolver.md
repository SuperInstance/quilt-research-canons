# REFERRAL — fleet-triage resolver (PENDING, CANDIDATE per weight law)

Source lane: **SuperInstance/fleet-triage** — `resolver.py` (3-stage doc
citation resolver: index → scan → audit), scoped quilt-family run executed
2026-10-02 over a 244-repo census (226 `quilt-` prefixed), 243 repos
shallow-cloned and indexed (15,880 files), 5,852 docs / 7,790 citation
sites scanned in 162s. Digest: `docs/QUILT-FAMILY-TRIAGE-2026-10-02.md` on
branch `quilt-family-triage-2026-10-02`, PR fleet-triage#2 (open,
Casey-gated). Audit subcommand independently re-verified 513 findings by
filesystem scan: hard outcomes (FILE_MISSING / REPO_UNKNOWN / REPO_MISMATCH /
LINE_OOR / numeric) audited at **0.0% false-positive**.

## Why this repo

This repo is the quilt family's citation backbone, and the scoped run put
it at the top of the honesty-fix surface:

| outcome | count |
|---|---|
| RESOLVES | 192 |
| PATH_PRECISE_ONLY (advisory-only, 49.2% FP on audit) | 56 |
| **FILE_MISSING** | **222** |
| AMBIGUOUS | 113 |
| REPO_UNKNOWN | 9 |
| REPO_MISMATCH | 3 |

222 FILE_MISSING citations in the canon cluster are the cheapest honesty
fixes in the org: every one is a doc→file claim that no longer resolves,
i.e. the doc layer drifted from the code layer. Under the weight law this
edge is **PENDING until a merged PR in the TARGET repo (this repo) cites
the technique**; never self-upgraded.

## Suggested consumption (consume, don't rival)

1. Adopt a resolver-scan gate over `projects/`, `research/`, `sprints/`:
   `RESOLVER_STATE=<state> resolver.py index && resolver.py scan
   --no-external --no-urls`, then work the FILE_MISSING list.
   quilt-tools #23 (citation-verify GUARD, MERGED) already protects the
   fleet against fuzzy gh-search false positives on this class.
2. One sweep here fixes the family's largest single FILE_MISSING surface.
   (For the record: all 25 family-wide LINE_OOR sites live in
   quilt-tournament — separate referral doc suggested there.)

## Honest boundary notes

- Index is shallow-HEAD: citations to files that only ever lived on
  non-default branches will read as FILE_MISSING (verify before deleting
  prose, prefer re-pointing over deleting).
- PATH_PRECISE_ONLY outcomes were 49.2% FP on independent audit and are
  advisory-only; do not batch-fix them.
- The resolver is a citation instrument, not a truth instrument: a
  RESOLVE means the file exists at the cited path, nothing more.

Filed by the kimi1 snowball lane from the quilt-family triage run; main
untouched; merge of this PR mints the edge CANDIDATE (target-side citation
present), and the quilt-tools referral graph flips it VERIFIED per the
weight law.
