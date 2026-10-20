# Repro scripts — SCOUT 2026-10-20T1620Z

Companion to `research/scout/SCOUT-2026-10-20T1620Z-the-certification-that-proves-a-contradiction-and-the-64-percent-red.md`.

## `drift_repro.py` — the receipt for section 2

A dependency-free Python port of `SuperInstance/constraint-bench-suite`'s
`gpu/drift_bench.cu` kernel (E64/E32/E16/EBF16/EI8 structs, `operator+` /
`operator*` / `rotate60` semantics, BF16 round-toward-zero truncation, INT8
`>>4` scaling with a +/-127 clamp, the `i%3` rotate / `i%5` add schedule,
10,000 iterations, drift = ||value - ref||).

```
python3 drift_repro.py
```

Reproduces the suite's published first-violation iterations (FP32 ~28,
FP16 ~13, BF16 ~8) and additionally reports the first non-finite iteration per
format, which the shipped benchmark never prints. No GPU, no CUDA, no deps.

The port assumes the `ref` path is the FP64 recurrence, as in the C++ source
(`ref=ref*mul64; ref=ref.rotate60(); ref=ref+add64;`).

## `tree_scan.py` — substance ranking

`git/trees/{branch}?recursive=1` over candidate repos, bucketed by code
extension with vendored paths excluded. Ranks by code bytes, not API `size`
(which is git history) and not tree bytes (which is dominated by media).

## `ci_census_lau.py` — CI health census

Pulls `actions/runs` for a repo population and classifies green / red /
never-ran. Pair it with `GET /repos/{o}/{r}/actions/runs/{id}/jobs` to get
per-step conclusions — that is what separates "clippy-red" from "test-red" in
the report.
