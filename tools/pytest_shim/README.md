# pytest_shim — run a fleet repo's assert-style test suite with PyPI firewalled

## Why this exists

PyPI is firewalled in the scout sandbox (`pip install pytest` →
`ProtocolError` → "No matching distribution found"). Many fleet repos have
real, valuable pytest suites that therefore cannot be run at all — so the
scout reports "I could not run it", or worse, counts the suite as green
without executing it.

This directory is a **minimal pytest API shim** plus a runner that uses it.
It lets the scout actually *execute* a suite and honestly report a number.

## Use

```bash
# from a cloned repo
python3 /path/to/pytest_shim/run_tests.py tests/test_foo.py [more files...]

# -k filters by substring
python3 /path/to/pytest_shim/run_tests.py -k deadband tests/
```

The runner adds its own directory to `sys.path`, so a test module's
`import pytest` resolves to the shim automatically. No PYTHONPATH juggling.

## What it supports

- module-level `test_*` functions and `Test*` classes
- `setUp` / `tearDown` on `unittest.TestCase` subclasses
- module- and class-level `@pytest.fixture`, including **fixture-to-fixture
  dependencies** and `yield` fixtures
- `@pytest.mark.parametrize` with **real expansion** (the runner calls the
  test once per parameter set and labels each `[i]`)
- `pytest.raises` (with `match=`), `pytest.approx`, `pytest.warns`,
  `pytest.skip`, `pytest.xfail`, `pytest.fail`, `pytest.importorskip`,
  `pytest.mark.skipif`, `pytest.mark.skip`
- `monkeypatch` (setattr / setitem / setenv / delenv / chdir / undo),
  `tmp_path`, `tmpdir`
- `unittest.SkipTest` is reported as **SKIP**, not FAIL

## What it does NOT support — read this before quoting a number

It is **not pytest**. It does not implement:

- `conftest.py` discovery (fixtures in a conftest will not be found)
- `capsys` / `capfd` / `caplog`, `tmp_path_factory`, `monkeypatch.context()`
- `pytest.approx` over numpy arrays or custom numeric types
- plugins, hooks, `pytest.ini` / `pyproject.toml` config, `--lf`/`--ff`
- async tests, `pytest-asyncio`, doctest collection
- parametrised **fixtures** (`@pytest.fixture(params=[...])`)

**Scope rule for reports:** every count produced by this tool is "tests
executed by the shim". If a suite needs a feature outside the list above,
the honest statement is *"not runnable under the shim"*, not a number.

## It has bugs — it was written under time pressure

Found and fixed while building it (do not reintroduce them):

1. It originally did **not call `setUp`**, so any suite using `setUp` for
   fixture state reported spurious failures (6 false failures in one repo).
2. It originally did **not resolve fixture-to-fixture dependencies**,
   so a fixture taking another fixture as an argument silently resolved to
   `None` (12 false failures in another repo).
3. `unittest.SkipTest` was counted as FAIL.
4. The runner originally executed every file **twice** (once to print, once
   to count) and double-counted failures.

If a suite fails under this shim, **check the shim first** — re-read the
traceback and ask whether the failure is in the repo or in the instrument.
Two of the three "failing suites" in the first round of the 2026-10-24T1641Z
scout were the shim's fault, not the repos'.

## Proven on

| repo | result |
|---|---|
| `slackwater-harmony` | 151 passed, 0 failed |
| `quilt-schema-registry` | 32 passed, 0 failed |
| `quilt-fold` | 28 passed, 0 failed |
| `quilt-egg` | 18 passed, 0 failed |
| `quilt-multi-oracle` | 7 passed, 0 failed, 3 skipped |
| `quilt-canon-witness` | (uses its own `run_tests.py`, not this) |
