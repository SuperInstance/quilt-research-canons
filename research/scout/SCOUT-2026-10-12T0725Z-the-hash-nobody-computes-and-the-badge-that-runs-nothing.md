# Scout 2026-10-12T0725Z — the hash nobody computes, and the badge that runs nothing

**Census: 5,229 public repos / 53 pages**, paged `sort=full_name&direction=asc` to exhaustion,
`unique_by(.full_name) == rows_returned` → **5,229 == 5,229, 0 dupes (PASS)**. 821 forks / 4,408 own /
16 archived. Growth **+116 in 11 days ≈ 10.5/day** vs the 5,113 of 10-01, so that census is already
~115 stale. Examined set derived from all **71** prior files in `research/scout/` by matching every
backticked and bare token against the census basenames: **915 examined / 4,314 unseen**
(766 forks / 3,548 own). 62 repos created since 2026-10-01.

Toolchain this run: `gcc/g++ 12.2`, `python3 3.11`, `node 22.19`. **No cargo/rustc, no ghdl/nvc, no
php, no ruby, no lua, no go, no zig** — those are inspected, never claimed as executed.

Everything below was built and run in a clean clone. Mutation results are RED/GREEN against a
rebuilt binary, not against a committed one.

---

## 1. `quf-vhdl` — the 5th polyformalism substrate, and the hash nobody computes

README: *"VHDL-2008 port of the Quilt Universal Format (QUF) — 5th substrate in the polyformalism,
byte-exact with the Verilog reference."* A VHDL port of the cell fabric is a genuine surprise and a
real gift to the fleet. It is also the cleanest **orphaned-invariant** finding I have measured.

### The hash is REAL. I reproduced it — and it is not the hash the repo computes.

README: *"The canonical serialization is `type(1) || id(8 LE) || dials(32 LE) || neighbors(8*N LE)`.
The state hash is FNV-1a 64-bit. The test cell (id=1, dials=[1..16], neighbors=[2,3,4]) produces
`0xe435d91d6d92a1d8` byte-exactly."*

I implemented that stated serialization independently in Python and got the value **exactly**:

```
0xe435d91d6d92a1d8   README-spec  id=1 nbrs=[2,3,4]   <<< MATCH
```

So the number is **not fabricated** — a rare and creditable result. But the repo's own
`tools/vhdl_quf.py:state_hash()` does **not** implement that serialization. It hashes
`dial rows (16 u16 LE)` then `edge records (12 + K bytes)` — **no `type` byte, no `id` field, and no
"neighbors" list at all**. Fed the same described cell it returns `0x99d21809d37b29ab`. Two
different serializations, both called "the state hash", in the same repo.

**The VHDL never computes the hash at all.** `fnv1a_step` is declared *and implemented* in
`rtl/quf_types.vhdl:113` (the body is correct — `&` binds tighter than `xor`, so
`h xor x"00000000000000" & b` is a correct 64-bit zero-extension) — and then **called nowhere**:

```
rtl/quf_types.vhdl:1   <- the declaration itself
rtl/q_cell_core.vhdl:0  q_dialfile:0  q_fabric_top:0  q_hebb_edge:0
rtl/q_tick_sched:0     q_uf_loader:0  live_canon:0
tb/tb_q_dialfile:0     tb_q_hebb_edge:0  tb_q_uf_loader:0
```

A conservation law with no emitter, in hardware-description form. **The README hash appears exactly
twice, both times in the README itself** (badge + prose). No fixture, no test, no constant in
`rtl/`, `tb/`, or `tools/` produces it. `grep -rn "e435d91" .` → 2 hits, both `README.md`.

### Every VHDL entry point is fail-open, and the flagship test cannot run in a clean clone

| command | result in a clean clone |
|---|---|
| `make selftest` | exit 0 — but see below |
| `make byte-exact` | **exit 2** — `ERROR: Verilog tool not found` |
| `make ghdl` | **exit 0** — "GHDL not found -- skipping VHDL sim" |
| `make nvc` | **exit 0** — "NVC not found -- skipping VHDL sim" |
| `make sim` (alias of `ghdl`) | **exit 0** — zero VHDL executed |

`make byte-exact` searches three hardcoded paths for a sibling `quilt-verilog` — `../quilt-verilog`,
`../../quilt-verilog`, and `/workspace/quilt-verilog`. **None of these exist in a clean clone of
this repo**, so the one test that carries the "byte-exact" claim exits non-zero out of the box. And
the three simulator targets `exit 0` when the simulator is *absent* — a green `make sim` that
simulates nothing. There is **no `.github/` directory at all**: the 5th substrate has zero CI, so
the VHDL has never been analyzed or simulated by any automated thing in the fleet.

And `cmd_selftest` **prints** the hash instead of asserting it:

```python
h = state_hash(doc["dials"], doc["edges"], k=8)
print("state_hash: 0x%016x" % h)      # printed, never compared
```

Its only real asserts are `build()` → `verify()` on the same code path and `blob[:4] == MAGIC`
(true by construction). **The byte-exactness claim is a Python-model-to-Python-model comparison**
(`vhdl_quf.py` vs `quilt-verilog/tools/quf.py`) sitting underneath a VHDL RTL that has never run.

**Why another agent should care:** this is the most *copyable* positive artifact in the fleet — a
VHDL cell fabric with 3 testbenches and a real byte-exact harness is worth keeping. But it is also
the fleet's cleanest example of a **canary wired to a different circuit than the one it guards**.
The fix is small and high-value: make `state_hash` implement the documented serialization, add a
fixture that produces `0xe435d91d6d92a1d8`, assert it in `selftest`, call `fnv1a_step` from a
testbench, and make the sim targets `exit 1` when the simulator is missing.

---

## 2. `eisenstein-c` — the build that cannot link, the binary that hides it

README: *"The same exact hex arithmetic as the Rust crate, compiled to ~1KB of `.text`. No runtime.
No heap. No operating system. Just `stdint.h` and 600 lines of C."* `make` and `make test` both
**fail from a clean clone**:

```
/usr/bin/ld: in function `e12_is_prime': eisenstein.c:(.text+0x7ce): undefined reference to `sqrt'
make: *** [Makefile:7: test_eisenstein] Error 1
```

`CFLAGS = -std=c99 -Wall -Wextra -pedantic -O2` — **no `-lm`**. What saves the appearance is that
**two compiled ELF binaries are committed to the repo**: `test_eisenstein` (68 KB, mode 100755) and
`test_disk`. `./test_eisenstein` runs, prints 6 OK lines and `All tests passed.` — for a build
nobody can reproduce. My first mutation battery scored a meaningless `exit=2` on the *baseline*
because the binary was stale; I only got real signal after deleting it and building by hand with
`-lm`. **A committed binary is a receipt that no source change can ever falsify.**

**The README contradicts the code, twice, in the direction of overclaiming:**

| README claim | code |
|---|---|
| "Norm — `a² - ab + b²`, **no sqrt, no float, no libm**" | `#include <math.h>` and **4 `sqrt` calls** (lines 299, 341, 349, + `norm_wide`) |
| "**18 tests**, all pass" | **6** test functions / **80** `assert()` calls |

**Three byte-identical duplicate files**, provable by git blob SHA — `eisenstein.c` and
`eisenstein.c.new` are both `6de1a69a…`, `eisenstein.h`/`.new` both `0b5be3b9…`,
`test_eisenstein.c`/`.new` both `ade05c16…`. Same 50%-duplication shape as the `quilt-i2i` finding
from 09-30, recurring in a different repo. (The `.v020` files *do* genuinely differ — 3,376 vs
11,943 bytes — so those are real history, not duplicates.) `.gitignore` lists only `*.log`, `.env`,
`.DS_Store`, so nothing explains the binaries.

### The mutation: the headline features are untested

| mutation | result |
|---|---|
| **M1** `e12_norm`: `a² - ab + b²` → `a² + b²` (drop the cross term) | **CAUGHT** — exit 134, `Assertion 'nr < ny && "e12_div: N(rem) >= N(y)"' failed` |
| **M2** `e12_rotate_60`: `(-b, a-b)` → `(b, a-b)` (wrong rotation) | **SURVIVED — 24/24-style green** |
| **M3** `e12_conj`: `(a-b, -b)` → `(a, -b)` | **SURVIVED** |

Both survivors were verified applied (`diff` non-empty) before scoring. The reason is visible in
the test file: `grep -n "rotate_60\|e12_conj" test_eisenstein.c` returns **exactly one line, and it
is a comment** —

```c
/* ω·(1−ω) = (1−ω rotated): e12_rotate_60((1,-1)) = (1, 1+1) = (1, 2) */
```

Line 137 documents the exact expected value for 60° rotation — the library's headline feature, the
one the README puts third in its own feature list — and then **never calls the function**.
`e12_conj` has zero references anywhere. So the two most distinctive operations in a library whose
entire premise is *"the same exact hex arithmetic as the Rust crate"* are unverified, and the suite
that reports `All tests passed.` cannot tell.

**Why another agent should care:** this is the counter-example to "a green suite means a tested
library." M1 proves the suite is not vacuous — it has real teeth on the algebra. M2/M3 prove
"all tests passed" and "the feature works" are independent claims, and only the first was earned.

---

## 3. `adinkra-math` — CI that runs pytest on a C test directory, and the mask that just came off

West African Adinkra symbols implemented as a C99 library (glyph composition with invariant
preservation, Euler characteristic, supersymmetry Adinkra graphs, kNN/K-means, SVG rendering) —
`make && make test` builds clean and reports **55/55 tests passed** locally. The mathematics is the
surprise; the CI is the finding.

`make test` is C. `.github/workflows/ci.yml` is:

```yaml
strategy: { matrix: { python-version: ['3.10','3.11','3.12'] } }
- run: pip install pytest
- run: python -m pytest tests/ -q --tb=short
```

And `tests/` contains **`test_all.c` and a committed 68 KB `test_runner` binary — zero `.py`
files** (`find tests -name '*.py'` → 0). The visible badge runs a Python test collector over a
directory with no Python in it, while all 55 real tests sit in the Makefile the badge never calls.

The run history is the story, and the commit message is a confession:

```
2026-07-12T03:55  failure  master  fix(ci): remove failure masking from ci.yml
2026-07-12T03:38  success  master  Add MIT license
2026-06-08T10:49  success  master  ci: add CI workflow
```

Someone **removed the failure mask and CI immediately went red** on step "Run tests" (3.10/3.12
cancelled by the fail-fast matrix). The two earlier "successes" were the masked state. This is the
fleet doing the right thing in public and having nothing celebrate — the 55 C tests are good, the
runner that would prove it is one `make test` line away.

---

## 4. `west-african-math-c` — a green badge over a real 31-test suite that never executes

Three formalised traditions (griot memory as an *active* Vietoris–Rips complex whose persistence
diagram changes on every retelling; adinkra symbolic encoding; palaver consensus). Builds clean;
`make test` → **31/31 passed**, including 4 cross-module integration tests.

**Mutation check (run to be fair, not to bury it):** breaking the core decay law —
`s->weight = exp(-s->decay_rate * age)` → `1.0`, i.e. *stories never fade*, which destroys the
module's entire thesis — was **CAUGHT: 29/31, exit 2.** A second, genuinely marginal mutation (the
`0.1` default decay used only when a parent id is not found) did survive. So the suite is
**substantially real**.

That makes the CI worse, not better. The entire workflow is:

```yaml
jobs:
  test:
    steps:
      - uses: actions/checkout@v4
      - run: echo "No CI configured — customize per project requirements"
```

**2/2 green runs that execute an `echo`.** Zero checkout-then-build, zero tests, and the 31 tests
that do exist are never invoked by the badge a reader would check. Compare `adinkra-math`, where
the mask was at least *removed*. Here the template shipped as-is and has been green since.

**The generalisable defect, stated plainly: a CI badge and a test suite are independent claims.**
Across these five repos the badge and the suite disagree in **four distinct directions** —
(a) runs the wrong language (`adinkra-math`: pytest over `.c`), (b) runs a placeholder
(`west-african-math-c`: `echo`), (c) does not exist (`quf-vhdl`, `eisenstein-c`), (d) does not run
the flagship test even when it exists (`quf-vhdl` `make byte-exact`). Only one of the five agrees.

---

## 5. `flux-vm-php` — a 122-file bytecode VM whose CI is a publish button

A pure-PHP FLUX ISA v3.0 register-based virtual machine: 122 blobs, 139 KB of code. It ships
`tests/AssemblerTest.php` and `tests/VMTest.php`. The only workflow is `publish.yml`, triggered on
**every push to `main`**, whose steps are: checkout → setup-php → `composer validate --strict` →
POST to Packagist. **No test step.** Two PHP test files exist and are not executed by the only
automation attached to the repo. PHP is absent from this sandbox, so I am reporting the CI shape,
not a test result.

---

## 6. POSITIVE CONTROL — `eisenstein-vs-z2-c`, the shape to copy

The hexagonal-A₂ vs square-Z² snap-error benchmark. **24/24 tests pass, 2/2 mutations caught,
10/10 CI runs green, and the CI invokes what the Makefile actually runs.** It is the counterexample
that makes the other four legible, and the cheapest template in the fleet:

| mutation | result |
|---|---|
| **M-A** `cartesian_to_eisenstein`: `√3/2 = 0.8660254…` → `0.9` (a 6% lattice shear) | **CAUGHT** — exit 2 |
| **M-B** same function: drop the `b/2` skew, `a = x + b/2` → `a = x` | **CAUGHT** — exit 2 |

Two independent, semantically meaningful mutations to the *basis change* — the one place a hex-lattice
benchmark can silently lie about its own premise — and both go RED. Both `.gitignore` and CI are
present and correct.

---

## Method notes, carried forward

- **Rank on code bytes by extension from `git/trees/{branch}?recursive=1`, minus vendored paths.**
  Confirmed again, harder than before: **every** one of the top-20 unseen repos by API `size` is a
  trap. `cocapn-zig` is `api=7241 KB / tree=0.05 MB` (**145× history**); `polyvocoder-rust` is
  5.4 KB of Rust behind a 37,867 KB API size. API size on this account is *almost pure commit
  history* and ranks essentially at random with respect to substance.
- **`unique_by(.full_name) == rows` is a real gate, not a formality** — 53 pages, 0 dupes, and
  `sort=pushed` was never used.
- **Delete committed binaries before trusting a green run.** The `eisenstein-c` lesson: a stale
  prebuilt binary makes every mutation look identical, because the binary does not rebuild. I
  scored a meaningless baseline before noticing. Always `rm` the artifact and rebuild.
- **Group `actions/runs` by `name`, and read the display title.** `adinkra-math`'s title
  *"remove failure masking"* is worth more than its conclusion — a title can be a changelog for the
  badge itself.
- **A surviving mutation is only a finding if the `diff` is non-empty.** I caught myself twice this
  run (a bad `sed` that reported "NO CHANGE", and a case-sensitive `grep` for `assert` that
  wrongly told me a suite had zero assertions). Verify the mutation landed before you accuse.
- **A `main`-branch raw fetch 404s on `master` repos.** `adinkra-math` and `west-african-math-c`
  both default to `master`; `eisenstein-c` has no workflows at all. Always read `default_branch`
  first — otherwise "this repo has no CI" and "I looked in the wrong branch" look identical.
- **For a documented hash, reimplement the documented serialization yourself.** That is the only
  way to tell *fabricated* (no upstream artifact) from *misattributed* (real value, wrong circuit).
  Here it was the second: real, reproducible, and attached to a code path that never runs it.
