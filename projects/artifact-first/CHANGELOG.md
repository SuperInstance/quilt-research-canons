# Changelog

## 0.1.0 — first release

Two gates, built from one session's failures.

- **gate 1, grounding.** A claim is GROUNDED if its receipt predates it. Three states,
  not two: `UNSOURCED` is distinct from `NARRATIVE_FIRST` because an unsourced claim is
  ungrounded, not false.
- **gate 2, consistency.** Four shapes of self-contradiction (C1 universal-vs-exception,
  C2 summary-only statistic, C3 polarity flip, C4 count disagreement), each chosen because
  it really occurred. Validated by rediscovering a known defect in a shipped report.
- **`LinterCrashed`.** A check that raises no longer returns "no findings." An earlier
  bare `try/except` made a `NameError` indistinguishable from a clean result and the
  linter reported clean with a dead check inside it.
- **17 tests**, every positive assertion paired with a negative control, including one
  that asserts the linter still finds the real defect in the real fleet report.
- **Documented limits are tested, not hidden** — a headingless report cannot fire C1, and
  there is a test saying so.
