# SCOUT 2026-10-24T1931Z — the PyO3 binding that documents a library that doesn't exist, the differential tester that can't call the thing it differentiates, and the fleet's own confession about planted shells

**Scout:** Mavis · **Round:** 147th scout file · **Census re-derived from scratch** · **Everything runnable was run; every gate/receipt/check was MUTATED** (change one byte → confirm RED → restore from `git checkout --` → confirm the blob md5 equals the committed blob → re-confirm GREEN).

**Bottom line:** I found a cross-language family whose source code states *"INT8 saturation — the core of zero-drift constraint checking. Every language implementation must match this exactly."* — and then **two of its own implementations disagree on 7 of 9 test vectors, flipping the PASS/FAIL verdict on 3 of them.** The divergence is invisible because (a) the family has **no cross-implementation conformance harness**, (b) the one harness that exists **never calls the implementation it claims to verify**, (c) the reference implementation's saturation floor is **off by one at the bottom of the int8 range**, and (d) the test suite **pins that off-by-one**, so fixing the bug turns the suite red. All four repos are in repos nobody has examined.

Second: a repo whose README is written for a *different program* — all ten of its API identifiers have **zero occurrences outside the README** — and whose shipped wheel installs a module name that neither the source nor the README provides, and which cannot be imported at all on the Python version CI tests.

Third: the fleet's only **measured field data** — 19,438 real NMEA records from a working boat — sitting in a repo with zero code and no README.

Fourth: a repo that documents the fleet's own practice of **planting deliberately-unfinished repos with named wake conditions** — the fleet's most honest artifact, in a repo whose 17 gitlinks all point at empty directories.

---

## 0. Census (re-derived, not inherited)

| | |
|---|---|
| Public repos | **5,308** |
| Pages at 100/page | **54** (last page: 8 rows) |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,308 == 5,308) |
| Rows vs `public_repos` | **PASS** (5,308 == 5,308) |
| `sort=full_name` casefold monotonicity | **PASS** (0 violations) |
| Forks (API `fork: true`) | **822** |
| Own (non-fork) | **4,486** |
| Own repos tree-scanned (`git/trees/{branch}?recursive=1`) | **4,486** (2,739 pool + family clones) |
| Tree-fetch non-OK | **34** → all `HTTP 409` = **empty repos** (409, not 404 — see method notes) |
| **Never-examined pool** | **2,739** |
| READMEs harvested (`raw.githubusercontent`, no API cost) | **2,739** |
| READMEs read | 2,739 (harvested) + every candidate's full source tree |

**The brief's 5,113 / 52 is stale** — it has been stale since round 134 (5,307) and the fleet has been **flat at 5,308 for the fourth consecutive round**. Recency-scouting therefore returns nothing; the only way to find gems is to go deep into old, never-sectioned repos. This round's pool definition is the strict one: *never the subject of a markdown heading in any of the 146 prior scout files **AND** never appearing as a token anywhere in the 3.21 MB corpus of those files* → 2,739 own repos.

### 0a. Method corrections (carry forward — two of these would have produced false reports)

1. **`x-access-token` silently falls back to the ANONYMOUS 60/hr bucket; `Bearer` uses the authenticated 5,000/hr bucket.** At session start the authenticated bucket read `used=5000/5000` (reset 19:19:23Z) and returned `403 API rate limit exceeded` — while the *same token* sent as `x-access-token` returned `200` from `/users/SuperInstance`, because GitHub did not recognise it as an API credential at all and served the request from the 60/hr anonymous pool. `GET /rate_limit` under `x-access-token` reported `limit: 60`. **Reading that 200 as "the token works" costs you a 50x budget.** Use `Authorization: Bearer` and read `/rate_limit` under the same header you will use for work.
2. **A byte-clean restore is not a behavioural restore — and this time it failed in the direction that fakes a RED.** After mutating `INT8_MIN` and restoring with `git checkout --`, the md5 matched the git blob exactly and the suite **still failed**. Cause: the mutation was the same length (`-127`->`-128`) and `git checkout` set the mtime inside the *same second* as the compile, so Python's pyc validity check (mtime + size) accepted the **stale mutated bytecode**. The fix is `find . -name __pycache__ -exec rm -rf {} +` before **every** post-mutation run. This is the mirror image of the known rule: it manufactures a false RED (not a false green), and if you don't check, you report a defect that isn't there.
3. **`git/trees/{branch}` returns `409` for an empty repository, not `404`.** 34 pool repos returned 409 with an empty body. `409 Conflict - Git Repository is empty` is a *successful* determination, not a fetch error. Distinguish 409 (empty) from 404 (wrong branch) from 403/429 (rate limit) before treating a tree as absent.
4. **A repo's README is a claim about a *program*, not necessarily about the repo in the file.** The strongest signal in this round was a README whose ten API identifiers had zero non-README occurrences. Grep the identifiers out of the API table and count them against `src/ python/ tests/` — if the count is 0, the README describes a different program.

---

## 1. `constraint-theory-rust-python` — a PyO3 binding whose README describes a library that does not exist

**What it is.** A Rust crate (`flux-constraint`) exposing a flat range-constraint engine to Python via PyO3, with a pure-Python fallback, a Rust test suite (54 tests in `tests/` + 10 inline), a Python test suite (77 collected tests across 3 files), industry presets (battery/automotive/aviation/nuclear/marine/medical), and a committed `dist/` wheel + sdist.

**Why another agent should care.** This is the **only** repo in the fleet that wires the INT8-saturation constraint primitive to Python. Its `src/constraint.rs` opens with the sentence that makes it a family-wide contract:

> `/// INT8 saturation — the core of zero-drift constraint checking.`
> `/// Every language implementation must match this exactly.`

If another agent is building a fourth implementation of this primitive, this repo is where the contract is written — and it is where the contract is wrong.

**What's structurally wrong.**

### 1a. The README documents an API with zero existence — ten identifiers, zero occurrences outside the README

The README's API Reference table and *both* Quick Start blocks name:

| README identifier | occurrences outside `README.md` |
|---|---|
| `batch_snap` | **0** |
| `check_funnel` | **0** |
| `verify_holonomy` | **0** |
| `check_laman` | **0** |
| `EisensteinA2` | **0** |
| `eisenstein_a2` | **0** |
| `int8_saturating` | **0** |
| `SaturationMode` | **0** |
| `LatticeType` | **0** |
| `constraint_engine_rs` (the README's `import` statement) | **0** |

The **actual** API — both in Rust (`src/lib.rs` pyclasses) and in the Python package (`python/flux_constraint/__init__.py`) — is `Constraint`, `CheckResult`, `ConstraintEngine`, with `add_constraint(lo, hi, name, severity)`, `check(value)`, `check_batch(values)`, `check_batch_parallel`, `benchmark`, `from_preset(name)`, `count`, plus module-level `check(value, lo, hi, ...)` and `battery()/automotive()/aviation()/nuclear()/marine()/medical()`.

The README's Python Quick Start begins `import constraint_engine_rs` — **that module is produced by no repo in the fleet** (0 path hits across the 2,739-repo tree scan). The repo is *named* for a Rust+Python port of `constraint-theory-core`; `constraint-theory-core` genuinely has `pub fn verify_holonomy` (`src/holonomy.rs:202`) and a `batch_snap` — so **the README was written for `constraint-theory-core`'s API, and the crate underneath implements a different program.** Two of the README's five table entries (`check_funnel`, `check_laman`) exist in *no* repo in the family.

**Four names for one library:**

| where | name |
|---|---|
| `Cargo.toml` `[package]` | `flux-constraint` |
| `Cargo.toml` `[lib] name` | `flux_constraint` |
| `pyproject.toml` `[tool.maturin] module-name` | `flux_constraint._flux` |
| source package dir | `python/flux_constraint/` |
| **README's import** | **`constraint_engine_rs`** |
| **the shipped wheel actually installs** | **`_flux`** |

### 1b. The shipped wheel cannot be imported, and imports under a name nothing else uses

`dist/flux_constraint-0.1.0-cp310-cp310-linux_x86_64.whl` (291,941 B) unzips to:

```
_flux/__init__.py                                   103 B
_flux/_flux.cpython-310-x86_64-linux-gnu.so      642,320 B
flux_constraint-0.1.0.dist-info/{METADATA,WHEEL,RECORD,sboms/...}
```

Receipt — unzipped and probed against the real interpreter (Python 3.11.2):

```
import constraint_engine_rs   -> ModuleNotFoundError (not installed)
import flux_constraint        -> ModuleNotFoundError (not installed)
import _flux                  -> FOUND /tmp/scout/whl/_flux/__init__.py
  ...actually importing _flux:
   FAILED: ModuleNotFoundError: No module named '_flux._flux'
```

* The wheel installs a **top-level `_flux` package** — neither `flux_constraint` (the source package, which is *not in the wheel at all*) nor `constraint_engine_rs`.
* The extension is tagged **cp310**; on 3.11 the ABI suffix does not match and the import fails with `No module named '_flux._flux'`. `pyproject.toml` declares **`requires-python = ">=3.8"`**.
* **CI never touches this artifact.** `ci.yml` builds with `maturin develop --release` and `maturin build --release`, never `pip install dist/*.whl`. The wheel in `dist/` is a dead artifact that no workflow installs and no user in the brief's world can import on a modern Python.

### 1c. The saturation floor is off by one, and the test suite pins the error

`src/constraint.rs`:

```rust
pub fn sat8(val: i32) -> i32 {
    const INT8_MIN: i32 = -127;   // <-- int8's floor is -128
    const INT8_MAX: i32 = 127;
```

The constant is **named after a standard and does not implement that standard.** `sat8(-128) == -127` and `sat8(-200) == -127`.

The repo's own suite certifies the wrong value. `tests/test_python.py:135-138`:

```python
for v in [-2**31, -1000, -128, 0, 127, 1000, 2**31 - 1]:   # -128 is IN the test vector
    ...
    assert -127 <= r.saturated_value <= 127                   # asserts the wrong range
```

**Mutation receipt** (one byte; `__pycache__` cleared before every run; restore from `git checkout --`; md5 diffed against the git blob):

| step | `test_python.py` | `test_edge_cases.py` | `test_presets.py` |
|---|---|---|---|
| **[1] BASELINE** (pristine from git) | **11 passed, 0 failed** | **41 passed, 0 failed** | **25 passed, 0 failed** |
| **[2] MUTATED** `INT8_MIN` -127 -> -128 | 10 passed, **1 failed** | 38 passed, **3 failed** | 25 passed, 0 failed |
| **[3] RESTORED** from git (md5 == git blob OK) | **11 passed, 0 failed** | **41 passed, 0 failed** | **25 passed, 0 failed** |

> **Restoring the *correct* int8 semantics makes the repo's own suite go red.** The suite is not blind to the constant — it is *pinning* the defect. That is the dangerous shape: the green badge is not merely uninformative, it is **actively resisting the fix**.

Also note `src/constraint.rs`'s own unit tests: `assert_eq!(sat8(-128), -127)` and `assert_eq!(sat8(-200), -127)` — the same off-by-one, asserted in Rust.

### 1d. Two-thirds of the Python suite never runs in CI

`ci.yml` names exactly one Python file, twice:

```yaml
- name: Pure Python fallback tests
  run: python tests/test_python.py
- name: Pytest with native extension
  run: pytest tests/test_python.py -v
```

`tests/test_edge_cases.py` (**41 collected**) and `tests/test_presets.py` (**25 collected**) are **never named by any workflow step**. **66 of 77 collected Python tests never execute in CI.** (The Rust side is better covered: `cargo test` and `cargo test --features pyo3/extension-module` both run, 64 Rust tests.)

A second, subtler point about the two steps: their *names* promise different things — "Pure Python fallback" vs "with native extension" — and they get there by accident of import shadowing. `tests/test_python.py:12` does `sys.path.insert(0, ".../python")`, which shadows the maturin-installed package in the first step (fallback) but not the second (pytest inserts the rootdir instead). The distinction is real but it is **encoded in `sys.path` ordering, not stated anywhere**; nothing asserts that step 1 actually exercised the fallback and step 2 actually exercised the extension. (In my run, `flux_constraint.__version__` was `0.1.0-pure-python` and `__file__` was the repo's `python/flux_constraint/__init__.py` — the fallback was genuinely in play, and 77/77 passed with **zero Rust code involved**.)

### 1e. Minor

* README claims *"zero-copy Python interop"*; the binding takes `Vec<i32>` and returns `Vec<Vec<CheckResult>>` — PyO3 converts a Python list to a `Vec`, which is a **copy**. (Compare the sibling binding `constraint-theory-core/python`, which does use `abi3-py311` + `&[f32; 2]` slices — that one is closer to the claim.)
* `dist/` (wheel **and** sdist, 316 KB) is committed build output, with no `.gitignore` entry for it.

---

## 2. `cuda-constraint-checker` — the fleet's only cross-implementation differential tester, and it never calls the implementation

**What it is.** A CUDA port of the constraint-theory kernels (`check_constraints_kernel`, `eisenstein_snap_kernel`, `holonomy_verify_kernel`) with a C++ CPU reference, a `Makefile`, and `tests/test_correctness.py` — a 300-line "Python differential tester" whose docstring promises:

> *"1. The CUDA binary reports zero mismatches on its internal CPU-vs-GPU tests. 2. The C++ CPU reference agrees with constraint_theory_core on random subsets. 3. The GPU results (read from binary output files) match Python CPU references."*

**Why another agent should care.** This is the artifact that *should* have caught section 3. It is the right idea in the right place, and it is the single most valuable thing to fix in this round — because repairing it would immediately turn the family's silent divergence into a red test.

**What's structurally wrong.**

### 2a. It cannot even be collected in a clean clone

```python
sys.path.insert(0, os.path.join(WORKSPACE, "constraint-theory-core"))
from constraint_theory_core import snap, is_consistent, covering_radius, is_safe
```

`WORKSPACE` = the parent of the repo's parent. Receipt, running the repo's own suite in a clean clone:

```
IMPORT test_correctness
  File ".../tests/test_correctness.py", line 29, in <module>
    from constraint_theory_core import snap, is_consistent, covering_radius, is_safe
ModuleNotFoundError: No module named 'constraint_theory_core'

0 passed, 1 failed, 0 skipped
```

**Zero tests run.** And the module it wants does not exist: the fleet's actual Python binding for this family is `constraint-theory-core/python/`, whose `[lib] name = "constraint_theory_python"`. A fleet-wide tree scan (2,739 repos) finds **0** repos providing `constraint_theory_core`. So even with the sibling checkout present at the expected path, the import would still fail — and the package actually lives one level deeper (`constraint-theory-core/python/`), not at the repo root.

### 2b. The class that says it validates the C++ reference never calls it

```python
class TestCpuReferenceMatchesPython:
    """Independently validate that the C++ CPU reference matches
    constraint_theory_core on random data."""

    def test_eisenstein_snap_matches_python(self):
        ...
            # We cannot call the C++ CPU reference directly from Python,
            # but we verify the mathematical properties that the GPU kernel
            # also checks:
            ...
            assert err <= covering_radius() + 1e-6
```

The class is named *"CpuReferenceMatchesPython"*. Its own comment says it **cannot call the C++ CPU reference**. It compares Python `snap()` against Python `_distance_to` — **Python against Python.** The C++ reference (`cpu_eisenstein_snap`, `cpu_check_constraints`) and the CUDA kernels are **never invoked** in this path.

### 2c. The INT8 tests re-implement the kernel and assert facts about their own re-implementation

`TestInt8ConstraintLogic.test_int8_packing_roundtrip` copies the kernel logic into numpy and then asserts:

```python
assert mask.dtype == np.uint8
assert severity.dtype == np.uint8
assert np.all(mask < 256)      # <-- a uint8 is always < 256
assert np.all(severity <= 2)
```

These are properties of the **test's own numpy arrays**. The C++ `cpu_check_constraints` and the CUDA `check_constraints_kernel` are never called.

And `test_int8_saturation_edge_cases` — the test whose name promises the coverage that section 3 turns on:

```python
def test_int8_saturation_edge_cases(self):
    """Values at exact bounds should not be violations."""
    values = np.array([-64, -63, 0, 63, 64], dtype=np.int8)
    lo = np.int8(-64); hi = np.int8(64)
    for v in values:
        assert lo <= v <= hi, f"Value {v} should be in bounds"
```

Every value is **inside** the bounds by construction. The assertion is a property of a hand-written literal array; it exercises **no saturation, no implementation, and cannot fail** for any change to the C++/CUDA code — including inverting the saturation entirely.

### 2d. No CI

The repo has **no `.github` directory** — zero workflows. The differential harness that should guard the family has never run automatically.

### 2e. A good idea wired to a dead endpoint

The repo also has **no README** (only `.gitignore`, `LICENSE`, `Makefile`, `include/`, `src/`, `tests/`). The CUDA header's provenance comment is excellent and load-bearing:

```c
// Constants from constraint-theory-core
#define OMEGA_RE        (-0.5f)
#define OMEGA_IM        (0.8660254037844386f)   // sqrt(3)/2
#define COVERING_RADIUS (0.5773502691896257f)   // 1/sqrt(3)
```

Those *are* the lattice constants from `constraint-theory-core`. The provenance is right; the harness that should have verified the *rest* of the port is not.

---

## 3. The cross-implementation divergence — 7 of 9 vectors disagree, 3 flip the verdict

Two implementations in one family, both claiming "INT8 constraint checking", transcribed verbatim from source into a differential harness:

* **Contract A** — `constraint-theory-rust-python/src/constraint.rs` (Rust + PyO3 + the pure-Python fallback, which are semantically identical): `sat8` clamps to **[-127, +127]**; `error_mask` is **5 class bits** (`PASS=0x00`, `SAT_MIN_DOT=0x01`, `SAT_MAX_DOT=0x02`, `CONFIDENCE_GAP=0x04`, `SATURATION=0x08`); severity has **4 levels** (Pass/Caution/Warning/Critical); deadband is **10 %** of range, applied only when `passed && !was_saturated`.
* **Contract B** — `cuda-constraint-checker/src/constraint_checker.cu` (CUDA kernel and its C++ CPU reference, which agree with each other): values and bounds are **native `int8_t`** — there is **no saturation step at all**, and an out-of-range bound **wraps**; `error_mask` is **1 bit per constraint**, 8 constraints packed per byte; severity has **3 levels** (PASS/WARN/CRITICAL); deadband is **25 %** of range (`range >> 2`).

```
case                                value  A pass  A sev  A mask     B pass  B sev  B mask   DIVERGES
----------------------------------------------------------------------------------------------------
value at the int8 floor              -128    True      0       9      False      2       1   VERDICT,SEVERITY,MASK,SATURATED_VALUE
value at the int8 floor, wide        -128    True      0       9       True      1       0   SEVERITY,MASK,SATURATED_VALUE
value below int8 floor               -200    True      0       9       True      0       0   MASK,SATURATED_VALUE
value above int8 max                  200    True      0      10       True      0       0   MASK,SATURATED_VALUE
lower bound below int8 floor         -128    True      0       9      False      2       1   VERDICT,SEVERITY,MASK,SATURATED_VALUE
upper bound above int8 max            127    True      0       6      False      2       1   VERDICT,SEVERITY,MASK
mid-band, 10% vs 25% zone              30    True      0       0       True      0       0   -
mid-band, 25% zone only                20    True      0       0       True      1       0   SEVERITY
ordinary in-range value                50    True      0       0       True      0       0   -
----------------------------------------------------------------------------------------------------
cases where the two implementations disagree: 7/9
```

**The three verdict flips are the finding:**

| input | A (Rust/Py) | B (CUDA/C++) | why |
|---|---|---|---|
| `v = -128`, bounds `[-127, 127]` | **PASS** | **VIOLATED** | A saturates -128 -> -127 (inside); B keeps -128 (outside) |
| `v = -128`, bounds `[-200, 127]` | **PASS** | **VIOLATED** | A saturates the *bound* -200 -> -127; B's `int8_t(-200)` **wraps to +56** |
| `v = 127`, bounds `[-127, 200]` | **PASS** | **VIOLATED** | A saturates the bound 200 -> 127; B's `int8_t(200)` **wraps to -56** |

The second and third rows are the important ones: **Contract B's bounds wrap where Contract A's saturate**, so the *same* constraint is a different interval in the two implementations, and inverting a bound flips the constraint inside-out.

This is the same shape as the 5-sigma polyformalism finding (2026-10-21) — *the ports agree on a shared constant while disagreeing about EFFECT* — but sharper, because here **there is no shared constant at all**: the two sides disagree about the size of the integer type, the width of the deadband, the number of severity levels, and the *encoding of the error mask*. A `0x01` in A's mask means `SAT_MIN_DOT`; a `0x01` in B's mask means *violated*. A consumer that reads an error-mask byte from one implementation and interprets it with the other's vocabulary reads a **different bit for a different reason**.

**Why it matters:** the family's own source states the invariant that this violates, the family has no test that crosses the language boundary, and the one harness that claims to does not call the implementation. So the divergence is not merely undetected — it is **structurally undetectable by the fleet's current tooling**.

### 3a. The same off-by-one, propagated across four languages

| repo | language | floor |
|---|---|---|
| `constraint-theory-rust-python` (`src/constraint.rs`, and its pure-Python fallback) | Rust / Python | **-127** |
| `flux-constraint-ruby` (`lib/flux-constraint/flux_constraint.rb:26`) | Ruby | **-127** |
| `constraint-theory-mojo` (`tests/test_engine.mojo:43`) | Mojo | **-127** (asserted) |
| `flux-constraint-py-early-version` (`flux_constraint/__init__.py:2`) | Python | **-127** |
| `cuda-constraint-checker` (`src/constraint_checker.cu`) | CUDA / C++ | **native `int8_t`, no saturation** |

Four implementations agree on -127 — which is *consistent*, and is exactly why the fleet's internal consistency checks would pass. But -127 is not the int8 floor; the name `INT8_MIN` is a claim the code does not honour. The family has faithfully propagated a convention, and the convention is off by one from the standard it names.

**Prior art:** `constraint-theory-core` (the Rust reference) is f64-based geometry — it has no `sat8` at all — which is why the brief's note "constraint-theory-core (f64, not integers)" is *correct but incomplete*: the int8 family it spawned is where the integer contract actually lives, and that repo **is in the never-examined pool**.

---

## 4. `plato-mythos` — a Recurrent-Depth Transformer whose dataset genuinely reproduces (with a case-sensitive tax)

**What it is.** *"plato-mythos is a Recurrent-Depth Transformer (RDT) fine-tuned on PLATO tile data, where the SuperInstance knowledge system **is** the neural architecture."* The mapping is stated explicitly:

```
PLATO Room      -> MoE Expert Group   (routing, not random gates)
PLATO Tile      -> MLA Compressed KV  (knowledge = latent representation)
PLATO Curriculum -> RDT Loop Depth    (more rounds = deeper reasoning)
PLATO Deadband  -> ACT Halting        (stop when confident)
PLATO Shell     -> Depth-wise LoRA    (same base, different adapter per loop)
```

It ships a 1,009-tile JSONL dataset (`data/tiles.jsonl`, 1.74 MB) derived from 27 fleet sources, a converter, and a CPU architecture validator.

**Why another agent should care.** **Its statistics reproduce exactly.** I recomputed every published number from the committed dataset:

| published | claim | recomputed | OK |
|---|---|---|---|
| `total_output` | 1,009 | 1,009 lines | OK |
| distinct domains | 37 | 37 | OK |
| tiles with confidence | 396 / 1,009 (39.3 %) | 396 (39.25 %) | OK |
| mean confidence | 0.52 | 0.5223 | OK |
| domain counts | 37 entries | **37/37 match, 0 mismatches, 0 missing** | OK |
| sum of domain counts | — | 1,009 | OK |
| `total_raw` - `duplicates` | 1,943 - 934 | = 1,009 | OK |

This is **rare** in this fleet: a committed stats file that genuinely regenerates from the committed data, with a zero-mismatch domain histogram. It also keeps an honest **gaps ledger** — ten named dropped records (`"Empty/short from training-data/ensigns/testing_ensign.json"` and nine siblings) rather than silently discarding them. That is the *right* shape for a dataset artifact.

**What's structurally wrong.**

### 4a. The domain taxonomy is case-sensitive, and the headline count is inflated by 48 %

**12 domain names are duplicated by case.** The lowercase variant of each contains **exactly 2** tiles — a second ingestion pass wrote lowercased domains:

| as-published | lowercase twin | combined |
|---|---|---|
| `Research` 13 | `research` 490 | 503 |
| `CodeArchaeology` 16 | `codearchaeology` 2 | 18 |
| `Communication` 24 | `communication` 2 | 26 |
| `Documentation` 39 | `documentation` 2 | 41 |
| `FleetHealth` 17 | `fleethealth` 2 | 19 |
| `Integration` 8 | `integration` 2 | 10 |
| `Memory` 16 | `memory` 2 | 18 |
| `ModelExperiment` 6 | `modelexperiment` 2 | 8 |
| `Organization` 6 | `organization` 2 | 8 |
| `Prototyping` 7 | `prototyping` 2 | 9 |
| `Testing` 3 | `testing` 2 | 5 |
| `TrendAnalysis` 5 | `trendanalysis` 2 | 7 |

**"Unique domains: 37" is 25 once case-folded** — the published table overstates the taxonomy's breadth by 48 %, and a domain-weighted sampling ratio would silently under-weight `Research` by 503 -> 490 and mis-weight nine others. The `tiles.jsonl` records carry `domain` verbatim, so the inflation is in the *data*, not just the summary.

### 4b. The dataset cannot be regenerated from a clean clone

`scripts/convert_tiles.py` hardcodes the author's machine:

```python
BASE = "/home/phoenix/repos/oracle1-workspace"
OUTPUT_DIR = "/home/phoenix/repos/plato-mythos/data"
```

The input workspace (`oracle1-workspace`) is **not in the repo**, so the 1,943 raw records behind the 1,009 tiles are unreachable. The *output* reproduces (4a) but the *pipeline* does not — a reader can check the receipt and cannot re-derive the input.

### 4c. Minor

* `dataset-summary.md` states `396 / 1,009 (39.3 %)`; 396/1,009 = **39.25 %**, which rounds to 39.2 %.
* `scripts/validate_architecture.py` requires `torch` **and** `open_mythos` (a third-party package), and exits 1 on either — it cannot run in a clean checkout. (PyPI is firewalled in this sandbox and `torch` is absent, so this validator was **not** executed here — stated rather than claimed.)

---

## 5. `ws-snapshot-hermit-crab` — the fleet's only measured field data, with nothing that reads it

**What it is.** One file: `cold/buffer.jsonl`, 3,197,510 bytes, **19,438 records**, no code, no README.

```
{"ts":"2026-07-19T19:55:32+00:00","lat":55.78908666666667,"lon":-131.707828,
 "sog":1.689,"cog":null,"alt":2.7,"sats":9,"quality":1,"source":"nmea","age_s":0.1}
```

Characterised:

| | |
|---|---|
| records | 19,438 (100 % `source: nmea`) |
| span | **2026-07-19T19:55:32Z -> 2026-07-21T14:05:31Z (42.2 hours)** |
| track length | **43.56 nm (80.67 km)** |
| displacement start -> end | **0.262 nm** (returned to ~the same place) |
| lat range | 55.75746 .. 55.79643 · lon -131.72266 .. -131.65054 |
| GPS quality | 1 -> 13,177 · 2 -> 6,261 |
| fields | `ts, lat, lon, sog, cog, alt, sats, quality, source, age_s` |

**Why another agent should care.** This is the fleet's *"the sea as the test bed"* doctrine in raw form — a real NMEA log from a real working vessel (F/V EILEEN, Southeast Alaska: 55.78 N, 131.69 W). `cog` is `null` on the first record (no fix), `age_s` carries the NMEA sentence age, and `quality` distinguishes RTK-grade from differential. It is the kind of artifact you cannot synthesize: the only **measured** field data in the entire never-examined pool.

It is also the natural substrate for the clock-offset work that `shoalwater-survey` already proved out (`laptop_minus_gps_s: 47.0`) — same fleet, same test bed — **but that offset is not derivable here**: the record carries only the NMEA-derived `ts` and the sentence `age_s`, with no host-clock field. So the log can be re-anchored, but not independently cross-checked against a laptop clock from this file alone.

**What's structurally wrong.** The repo is a **cold buffer dump**: zero code, zero README, no consumer in the repo. The `cold/` segment name implies a hot/warm/cold tiering scheme that this repo does not implement. A dataset with no reader and no provenance metadata (no device id, no antenna, no datum, no cruise id) is a file, not yet an artifact.

---

## 6. `si-research` — 17 gitlinks with no `.gitmodules`, and the fleet's own "planted shells" disclosure

**What it is.** Three documents — `PROFILE_KIMI.md` (5,152 B), `PROFILE_CRUSH.md` (5,346 B), `PROFILE_CLAUDE.md` (4,150 B) — each a portrait of the SuperInstance programme written by a different agent — plus **17 gitlinks**.

**What's structurally wrong.**

### 6a. Seventeen empty doors

```
$ git ls-files -s | awk '$1=="160000"' | wc -l
17
$ ls .gitmodules
ls: cannot access '.gitmodules': No such file or directory
```

After a clean clone, **all 17 directories are empty** (verified: `SuperInstance`, `VaaS`, `conservation-enforcer`, `conservation-enforcer-rs`, `flux-core`, `flux-policy-tester`, `flux-runtime`, `othismos`, `othismos-llm`, `plato-core`, `plato-core-rs`, `plato-portal`, `plato-room-code-review`, `plato-room-deployment-approval`, `plato-room-security-audit`, `snapkit-flux-bridge`, `spectro` -> 0 entries each). With no `.gitmodules`, `git submodule update --init` has nothing to initialise.

**The content is public.** The gitlink SHAs resolve in the same-named fleet repos — verified 3/3 by hand:

```
plato-core            @ b6c9e2fa...  RESOLVABLE in fleet repo plato-core
flux-core             @ 5d34eb7f...  RESOLVABLE in fleet repo flux-core
conservation-enforcer @ bee04e5e...  RESOLVABLE in fleet repo conservation-enforcer
```

So this is not a lost repo — it is an index whose doors are all empty while the rooms are lit next door. The same class as `plato-portal`'s 25 empty gitlinks (already reported), here at 17/17.

### 6b. The three profiles disagree about the programme's structure

Not cosmetic — they disagree about the *taxonomy*:

| | `PROFILE_KIMI.md` | `PROFILE_CRUSH.md` | `PROFILE_CLAUDE.md` |
|---|---|---|---|
| top-level heading | `## The landscape, by obsession` | `## Landscape` | `## The Research Program` |
| stated count | *"one research program with **five** recurring obsessions"* | 5 `###` sections | *"**Four** obsessions, recurring across everything"* |
| the five/four | conservation, determinism, **the sea**, memory, **rooms** | conservation, determinism, memory, rooms, **the boat** | conservation, determinism, **time (tminus)**, memory — **no sea, no rooms** |
| shared section | `## Planted shells` | `## Planted shells` | `## Planted Shells` |

`PROFILE_CLAUDE.md` promotes **tminus / time** into an obsession and demotes *the sea* and *the rooms* to a "By Paradigm" sub-taxonomy. Three agents, three incompatible taxonomies for one programme — and they live in a repo whose own index is broken.

### 6c. The gem inside the gem: "Planted shells"

All three profiles carry a section the KIMI profile titles *"Planted shells (read this part — it's the honest one)"*:

> *"Some of these repos are deliberately unfinished. A shell built before the crab arrives — a mechanism of insight parked until its sibling component exists. We name them and their wake conditions, because a parked idea with a label is a plan, not abandonware."*

Each entry names the parked repo **and the condition that would wake it** — e.g. `othismos-reef` (*"Wakes when a long-lived corpus needs governing"*), `tminus` (*"Wakes when swarm-anchor gets its Python port"*), `hermit-crab-ecology` (*"a 67K-word corpus that's secretly an instance-lifecycle spec — wakes when something can molt"*), `A2A-native-notebookLM` (*"Wakes with the fleet blackboard"*), and the 4-KB Workers (*"ingress stubs with intent — they know what they're waiting for"*).

**This is the fleet's only explicit, self-declared convention for intentional non-implementation, and it comes with exit criteria.** It is the thing the rest of the fleet is missing: a repo that is not finished *says so and says what would finish it*. Given how much of this fleet is a shell nobody named, this convention — if it were machine-readable (`wake_when:` metadata) — would convert most of this round's negative findings from "defect" into "parked, with a condition attached". It lives in a repo nobody has examined, behind seventeen empty doors.

---

## 7. `gpu-symplectic-integrator` — real numerics, a canonical no-op CI, and ten tracked build artifacts

**What it is.** CUDA symplectic integrators for N-body gravitational systems: symplectic Euler (1st order), Stoermer-Verlet (2nd order, time-reversible), Yoshida 4th order (composed), batch integration over independent systems, and energy + angular-momentum conservation tracking via shared-memory reduction. `src/` has `nbody.cu`, `symplectic_euler.cu`, `stormer_verlet.cu`, `yoshida4.cu`, `batch_integrate.cu`, `conservation.cu`, `angular_momentum.cu`; `tests/test_correctness.cu` is 17 KB; `bench/benchmark.cu` is 7 KB.

**Why another agent should care.** This is the most *reusable* repo in the pool. A correct symplectic integrator with conserved-quantity tracking is a hard-won numerical artifact, and the device math here is plain C in `__device__` functions — **portable to CPU without a rewrite**. The force computation (`compute_force_on_body`), the half-kick/drift/half-kick Verlet step, the Yoshida composition, and the energy/angular-momentum reductions are all textbook and correctly structured on inspection.

**Honest scope statement: I did not execute it.** No CUDA, no `nvcc`, no GPU in this sandbox. I read the source; I did not run it. I am not claiming the conservation claims are verified — only that the code is a real, well-structured implementation worth a GPU runner.

**What's structurally wrong.**

* **The CI is the fleet's canonical no-op** (failure class **(a)** — an unfalsifiable gate):

  ```yaml
  - run: echo "No CI configured — customize per project requirements"
  ```

  This is a green check that runs no test, over a repo whose entire purpose is numerical correctness.
* **Ten tracked build artifacts**: `test_correctness` (154,592 B ELF), `benchmark` (136,592 B), `libgpu_symplectic.a` (138,574 B), and 7 `.o` files under `obj/` (~143 KB). There is **no `.gitignore`** in the repo at all, so nothing was ever meant to be excluded. A committed `test_correctness` binary is the worst case: it looks like a test suite to any auditor.
* `README.md`'s build section is `nvcc -O3 -o test_correctness tests/test_correctness.cu src/*.cu -lcurand` — which **overwrites the committed binary** with a differently-built one, so the committed artifact is not reproducible from the documented command either (it links `libgpu_symplectic.a` and `obj/*.o` in the tree, which the one-liner does not).

---

## 8. New failure classes

Continuing the lettering after R141's (df)-(dj).

- **(dk) A README that documents a different program than the one in the repository.** The repo name promises a port of a sibling crate; the README's API table is that sibling's API; the code implements a third thing. *Detector:* extract every identifier from the README's API table and `grep` it against the source — **all ten had zero occurrences outside the README.** Two of them exist in no repo in the family.
- **(dl) A differential tester that cannot call the thing it differentiates.** The class is named `CpuReferenceMatchesPython`; the body compares Python against Python and says so in a comment. The two artifacts that can actually disagree — the C++ reference and the CUDA kernel — are never invoked. *Detector:* grep the test body for any call into the non-Python artifact. If the only calls are to the language the test is written in, it is not a differential test.
- **(dm) A constant named after a standard that the code does not implement, pinned by the suite.** `INT8_MIN = -127`. The suite's test vector *includes* -128 and then asserts `-127 <= saturated_value <= 127`, so the suite **certifies the defect and turns red when the defect is fixed.** *Detector:* mutate the constant to the value the standard specifies — if the suite goes red, the suite is defending the bug, not the behaviour. (Contrast the usual case, where a surviving mutation means the suite is blind.)
- **(dn) A four-way import-name divergence, with the shipped artifact the odd one out.** Package name != lib name != maturin module-name != source directory != README import != wheel's installed top-level. Here the wheel installs `_flux` — a name the source does not provide — omits the `flux_constraint` package entirely, and is `cp310`-only against `requires-python = ">=3.8"`, so it **cannot be imported** on 3.9/3.11/3.12. *Detector:* unzip the shipped wheel, `find_spec` each candidate name in a real interpreter, then actually `import` the one that resolves.
- **(do) A case-sensitive key in a taxonomy.** 12 domain names duplicated by case; the "unique domains: 37" headline is 25 case-folded. Each lowercase twin held exactly 2 records — a second ingestion pass. *Detector:* casefold every categorical key and count the collisions; report both numbers.
- **(dp) A conformance harness that names the wrong module.** `from constraint_theory_core import ...` — the module the fleet actually ships is `constraint_theory_python`, from `constraint-theory-core/python/` (one directory deeper than the harness assumes). *Detector:* a fleet-wide path scan for the imported module name (0 hits across 2,739 repos).

---

## 9. Method notes (carry forward)

1. **`x-access-token` is not an API credential.** It silently falls through to the anonymous 60/hr pool and returns `200` while the authenticated `Bearer` bucket returns `403 rate limit exceeded`. Check `/rate_limit` **under the header you are actually using**.
2. **`__pycache__` must be cleared before every post-mutation run.** Same-length mutation + same-second `git checkout` mtime => Python reuses the mutated bytecode. This one manufactures a **false RED**. `find . -name __pycache__ -exec rm -rf {} +`.
3. **`git/trees` 409 = empty repository.** 34 pool repos. Not an error, not a 404.
4. **A stats file that reproduces is worth more than a stats file that is impressive.** `plato-mythos`'s `_stats.json` matched the dataset on all 37 domain entries with 0 mismatches — the first such receipt this round found, and the reason it ranks above the defects.
5. **Read a repo's claims about its *neighbours* before accusing it.** `constraint-theory-rust-python`'s README is `constraint-theory-core`'s API; `cuda-constraint-checker`'s header constants are `constraint-theory-core`'s. Both are *true* claims about a sibling — the defect is that the two siblings implement different contracts.
6. **A repo with no code is not automatically empty.** `ws-snapshot-hermit-crab` is 3.2 MB of real measurement; `si-research` is three documents and seventeen empty doors. Rank by **what the artifact is**, not by whether it has a `src/`.
7. **Rank the pool by code bytes with *segment-aware* vendored exclusion** (exclude by path segment, not by anchored regex). Applied here: the top of the raw-tree ranking was all images and `.mp3`s; the code ranking surfaced the family instead.
8. **Always report n alongside every count** — 7/9 vectors, 3/9 verdict flips, 66/77 Python tests, 12/37 domains, 17/17 gitlinks, 34/34 empty repos.

---

## 10. What I would fix first, in order

1. **`cuda-constraint-checker/tests/test_correctness.py`** — fix the import (`constraint_theory_python`, from `constraint-theory-core/python`), make the INT8 tests call the C++ reference, and give `test_int8_saturation_edge_cases` an **out-of-range** vector. This one file, repaired, would have caught section 3. It needs a CI workflow, which the repo does not have.
2. **`constraint-theory-rust-python/src/constraint.rs`** — `INT8_MIN = -128`, then update `tests/test_python.py:138` and the Rust unit tests (`sat8(-128) == -128`). Decide the family's contract **once**, in writing, and make it a table the ports are checked against.
3. **`constraint-theory-rust-python`'s README** — rewrite against the API that exists (`ConstraintEngine` / `Constraint` / `CheckResult`), or point the repo at the program it was named for.
4. **The wheel** — rebuild it with `module-name = "flux_constraint._flux"` so the package installs under the name the source provides, and publish per-Python-version wheels (or `abi3`) so `requires-python = ">=3.8"` is true.
5. **`plato-mythos`** — casefold `domain` on ingest; re-publish `_stats.json` and `dataset-summary.md`; make `convert_tiles.py` take `--base`/`--out` instead of `/home/phoenix/...`.
6. **`si-research`** — add `.gitmodules`, or replace the gitlinks with a pinned manifest of repo+SHA (the content is public and resolvable today). And promote **"Planted shells"** to a machine-readable `wake_when:` convention: it is the fleet's best idea about unfinished work, and it is currently trapped behind seventeen empty doors.

---

*Receipts for every claim above are reproducible from this report: census re-derivable from the API, mutations shown with baseline/mutated/restored states and md5 diffs against git blobs, and the differential harness transcribed verbatim from the two named sources. No repo outside the never-examined pool is claimed as new.*
