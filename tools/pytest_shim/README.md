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

## v2 — what changed (2026-10-25T0436Z)

The previous shim could not resolve **class-scoped fixtures**, **generator fixtures**,
**`setup_method`**, **`unittest.TestCase.setUp`**, or **`capsys`**, and it crashed
(`AttributeError: 'NoneType' object has no attribute 'loader'`) when handed a
**directory** instead of explicit files. A suite that uses any of those was reported
as failing tests — a *shim* artefact mistaken for a *repo* defect.

v2 adds:

| capability | why it matters |
|---|---|
| class-scoped + module-scoped fixtures | the common `def store(self)` style |
| **generator** fixtures (`yield`) | `tmp_store` in `spreader-tool` |
| `setup_method` / `teardown_method` | pytest xunit-style setup |
| `unittest.TestCase.setUp` / `tearDown` | `training-data-collector` is a `TestCase` |
| `parametrize` | expands each case |
| `capsys` | CLI tests; **must be closed after each test** or it swallows all stdout |
| directory arguments | `run_tests.py tests/` now works |
| project-root + `src/` on `sys.path` | flat-layout *and* src-layout repos both import |
| `raises` / `approx` / `warns` / `skip` / `importorskip` / `fail` | as before |

### Measured effect (same repos, same clones, old shim vs v2)

| repo | old shim | **v2** | delta |
|---|---|---|---|
| `spreader-tool` | 278 passed, 59 failed | **337 passed, 0 failed** | **+59** |
| `Baton` | 35 passed, 27 failed | **61 passed, 1 failed** | **+26** |
| `edge-relay-agent` | 82 passed, 0 failed | **82 passed, 0 failed** | = |
| `flux-vm-agent` | 56 passed, 0 failed | **56 passed, 0 failed** | = |
| `training-data-collector` | 18 passed, 0 failed | **18 passed, 0 failed** | = |

**+85 tests recovered, 0 regressions.** The one remaining `Baton` failure is a *real*
repo defect, not a shim gap: `tests/test_lineage_bridge.py` imports `lineage_tracker`,
which exists in neither the repo, nor `pyproject.toml`, nor PyPI.

> **Before reporting "N tests fail", confirm the failures are the repo's.** Run the
> suite through v2 first; a shim gap and a broken repo produce the same output shape.
