# Repro scripts — SCOUT 2026-10-24T1931Z

Companion to `research/scout/SCOUT-2026-10-24T1931Z-the-int8-family-that-disagrees-with-itself.md`.

Every claim in that report is reproducible with the files here.

## `constraint_family_differential.py` — the decisive receipt (§3)

    python3 constraint_family_differential.py

No arguments, no dependencies. It transcribes **verbatim** the two INT8
constraint contracts that the SuperInstance fleet ships under one name:

* **Contract A** — `SuperInstance/constraint-theory-rust-python/src/constraint.rs`
  (`sat8` clamps to [-127,+127]; 5-bit class error_mask; 4 severity levels;
  10% deadband). Its pure-Python fallback in
  `python/flux_constraint/__init__.py` is semantically identical.
* **Contract B** — `SuperInstance/cuda-constraint-checker/src/constraint_checker.cu`
  (native `int8_t`, **no saturation**; 1-bit packed error_mask; 3 severity
  levels; 25% deadband).

Observed output:

    cases where the two implementations disagree: 7/9

with three vectors flipping the PASS/FAIL verdict outright:

| input                          | A (Rust/Py) | B (CUDA/C++) |
|--------------------------------|-------------|--------------|
| v=-128, bounds [-127, 127]     | PASS        | VIOLATED     |
| v=-128, bounds [-200, 127]     | PASS        | VIOLATED     |
| v=127,  bounds [-127, 200]     | PASS        | VIOLATED     |

Contract A's source states the invariant this violates:
*"INT8 saturation — the core of zero-drift constraint checking. Every language
implementation must match this exactly."*

## `mutate_sat8.sh` — the off-by-one, and the suite that pins it (§1c)

    bash mutate_sat8.sh /path/to/constraint-theory-rust-python

Runs a full baseline → mutate → restore cycle against the repo's own Python
suite. **No Rust toolchain required** — the suite runs against the pure-Python
fallback, which is exactly what CI's "Pure Python fallback tests" step
exercises.

Expected on pristine `main`:

    [1] BASELINE      test_python.py 11 passed, 0 failed
                      test_edge_cases.py 41 passed, 0 failed
                      test_presets.py 25 passed, 0 failed
    [2] MUTATED       test_python.py 10 passed, 1 failed
                      test_edge_cases.py 38 passed, 3 failed
                      test_presets.py 25 passed, 0 failed
    [3] RESTORED      ...all green again, md5 == git blob

**The point:** `INT8_MIN` is `-127`; int8's floor is `-128`. Mutating the
constant *to the correct value* turns the suite RED, because
`tests/test_python.py:138` asserts `-127 <= r.saturated_value <= 127` with
`-128` in the test vector. The suite is not blind to the constant — it is
**defending the bug**.

**Two traps this script handles, both of which produced false results before
they were handled:**

1. `__pycache__` is cleared before every run. A same-length mutation
   (`-127` -> `-128`) combined with a same-second `git checkout` mtime lets
   Python reuse the **stale mutated bytecode** — the restore is byte-clean but
   not behavioural, and the suite reports RED when it should be GREEN.
2. The restore is verified by **md5 against the git blob**, never against a
   backup copy of the file you were about to mutate.

## `plato_mythos_stats_check.py` — a receipt that reproduces (§4)

    python3 plato_mythos_stats_check.py /path/to/plato-mythos

Recomputes every published statistic from `data/tiles.jsonl`. Result on the
committed tree: **all 37 `_stats.json` domain entries match, 0 mismatches,
0 missing** — and 12 domain names are duplicated by case, so the headline
"unique domains: 37" is **25** once case-folded.

## `wheel_import_probe.py` — the artifact that cannot be imported (§1b)

    python3 wheel_import_probe.py /path/to/constraint-theory-rust-python

Unzips the shipped `dist/*.whl` and probes it in a real interpreter. The
wheel installs a top-level **`_flux`** package — not `flux_constraint` (the
source package, absent from the wheel) and not `constraint_engine_rs` (the
README's import, which exists in no repo in the fleet). The extension is
tagged **cp310** against `requires-python = ">=3.8"`, so on Python 3.9/3.11/3.12
the import fails with `No module named '_flux._flux'`. CI never installs this
artifact — it uses `maturin develop` instead.
