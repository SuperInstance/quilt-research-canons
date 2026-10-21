# SCOUT 2026-10-21T0431Z — the 5-sigma ports, the tool that audits the fleet, and the conformance suite that skips everything

**Scope:** unexamined corners of the SuperInstance fleet.
**Census (re-derived, not inherited):** `GET /users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc`,
paged to exhaustion → **53 pages, 5,296 rows, 5,296 unique — `unique_by(.full_name) == rows_returned` PASS.**
821 forks / 4,475 own / 16 archived / 59 `recovered-copy-YYYYMMDD-*` shadow copies.
Own after shadow-strip: **4,416**. Examined set rebuilt from all 118 prior scout reports (bare-name + `SuperInstance/` token
extraction, 2.38 MB of report text): **1,160 examined → 3,256 unseen own.** Known-examined repos
(`xruntime-conformance`, `substrate-foundation`, `spreadsheet-engine`, `quilt-tournament`, `plato-portal`, `health`, …)
were checked against the unseen set: **zero leakage.** 676 trees fetched for substance ranking
(all `truncated=false`, so the byte counts are floors, not ceilings).

**Not re-derived:** every repo already named in the 118 prior reports. `conservation-spectral-*` was already
examined (23 ports, 12.75× spread) and is cited here only as a sibling pattern, not re-reported.

---

## 1. The 5-sigma runtime ports disagree about what EFFECT *is* — and the "byte-exact" check is blind to it

**Repos:** `SuperInstance/quilt-haskell`, `SuperInstance/quilt-lua`, `SuperInstance/quilt-j` (all unseen; 0 prior
reports mention any of them).

**What they are.** The fleet's signature bet: *one doctrine, N languages, identical numbers.* These three are
"5-sigma polyformalism" ports of the Quilt cell-fabric runtime — BIND / LINK / EFFECT / VIEW / TICK over a cell of
`{id, 16 × int16 dials, neighbors}`. Haskell is billed as the "proof-of-proof port" (a language that bans mutation);
Lua as the "boat-as-robot enabler" (embeddable in any host); J as the point-free array-language port. All three
badges read **`hash 0xe435d91d6d92a1d8 — byte-exact`**.

**Why another agent should care.** This is the fleet's own identity claim. If the ports are not the same runtime,
then "the substrate is grown, not designed" rests on a port family that has never agreed on a single opcode.

### The hash is a *serialization* hash, and that is the wrong axis

The shared constant is FNV-1a 64 over the **65-byte canonical serialization of one cell**
(type tag `0x01` ‖ id u64-LE ‖ 16×int16-LE dials ‖ neighbors u64-LE). I recomputed it independently:

```
65 B canonical (tag+id+dials+nbrs)   0xe435d91d6d92a1d8   ✓ matches
64 B without the type tag             0x3b3b5772d64a9891
41 B tag+id+dials (no neighbors)      0x22ce0742ba08ed7d
65 B with neighbors reversed          0x7635c6e95f4a18d8
```

So the constant is real, and all three `reference_vibe.py` mirrors reproduce it. **But the hash covers only how a cell
is *written down*. It is mathematically incapable of seeing what the opcodes *do*** — and that is exactly where the
ports differ. The check is on the wrong axis.

### EFFECT means two different things

| port | signature | semantics |
|---|---|---|
| `quilt-haskell` `Quilt.hs:68` | `effect :: Fabric -> Word64 -> Fabric` | **targeted** — propagates the *target's* `dial[0]` to the target's neighbours; the target's own `dial[0]` is untouched |
| `quilt-lua` `quilt.lua:160` | `Fabric:effect()` (no target) | **global broadcast with snapshot** — *every* cell writes its own `dial[0]` to *all* its neighbours |
| `quilt-j` `quilt.ijs:115` | `EFFECT` (no target) | **last-neighbour-wins**, no snapshot: for each cell *j*, `dials[j,0] = dials[i,0]` where *i* is the *last* neighbour of *j* in sorted order |

On the same two-cell fixture (99↔100, `a.dial[0]=42`, `b.dial[0]=0`):

* Haskell → `a=42, b=42` (only 99's neighbours are written; 99 keeps 42)
* Lua → `a=0, b=42` (**they swap**)
* J → `a=0, b=42` (same as Lua here, but by a different rule — they diverge again as soon as a cell has two
  neighbours, because Lua's `pairs()` iteration order is not sorted and J's is)

### The Lua port's own self-test **fails**, and the shipped test was written around it

`quilt.lua` embeds its own `run_test` (lines 208–245). I ran it — twice, with two independent instruments:

**(a) Executed** under `fengari` (a Lua 5.3 VM in JS) on a `/tmp` copy with the `ULL` integer-literal suffix
stripped (fengari's lexer rejects `ULL`; real Lua 5.3 accepts it — that was the only edit, `diff` shown in-session):

```
BEFORE effect: a.dials[1]=42  b.dials[1]=0
AFTER  effect: a.dials[1]=0   b.dials[1]=42
port's assert #1: b.dials[1]==42 ?  true
port's assert #2: v[1]==42 ?       false   (v[1]=0)
```

**(b) Transliterated** to Python with real 64-bit ints (so the hash is also checkable, which fengari cannot do because
it is float-only — `0xFFFFFFFF` comes out as `-1`):

```
hash      = 0xe435d91d6d92a1d8
expected  = 0xe435d91d6d92a1d8
PASS: hash byte-exactly matches 0xe435d91d6d92a1d8
after effect: a.dials[0]=0  b.dials[0]=42
AssertionError: assert #2  <-- quilt.lua:238  v[1]=0     (exit 1)
```

`quilt.lua:238` is `assert(v[1] == 42)`. Under the port's own broadcast EFFECT, cell 99's `dial[0]` is overwritten by
its neighbour, so `a:view()[1]` is `0` and the assert fails. **The hash passes; the test then dies.**

The shipped standalone `test.lua` does not run the port's `run_test` at all — it says so, and re-implements the logic
inline ("*The simplest path: re-invoke the test logic inline*"). And it **changes the fixture**:

```lua
a.dials[1] = 42
b.dials[1] = 42  -- both same so effect is a no-op     <-- test.lua:235
```

The one fixture that distinguishes Lua's broadcast from Haskell's targeted EFFECT was neutralised — with a comment
that describes exactly what it hides. `test.lua` is green; `quilt.lua`'s own test is red.

### The Haskell port's "PASS" has zero assertions behind it

`Quilt.hs:194-223` (`runTest`) contains exactly one `error` (the hash mismatch) and **no assertion on any of the
five opcodes**. It computes `c1' = bind c0 ds` and `c1'' = bind c1' ds` and then **never uses them** (so BIND
idempotency is not tested), never calls `tick`/`tickM` at all (so TICK is not tested), never checks that LINK is
undirected, and then prints:

```haskell
putStrLn "PASS: 5 opcodes behave per spec (BIND idempotent, LINK undirected,"
putStrLn "      EFFECT propagates dial[0], VIEW returns dials, TICK alternates)"
```

**A PASS string printed by an unguarded code path.** The only real check in the Haskell port is the serialization hash.

### The J port's expected constant is wrong, and its failure is not a failure

`quilt.ijs:207`:
```j
expected =. 16465151175246630872
smoutput 'expected = 0xe435d91d6d92a1d8'
```

`0xe435d91d6d92a1d8` **= 16444288334828839384**, not 16465151175246630872. The decimal constant
`16465151175246630872` = `0xe47ff7c1fdae4fd8` and matches **no** canonical serialization I could construct
(65 B, 64 B, 41 B, 40 B, reversed-neighbour variants — all checked). So the J port compares its hash against a
number that is neither the one it prints nor the one the other two ports assert: **its conformance check is red by
construction.** And the failure is cosmetic — `smoutput 'FAIL: hash mismatch'` with no `error` call, so the run
**exits 0**. Lua does `error("FAIL: hash mismatch")`; Haskell does `error $ "FAIL: ..."`. The J port is the only one
that cannot fail.

### The mirrors are mirrors, not tests

Each port ships a hand-written `reference_vibe.py` — a Python re-implementation ("*Proves the Haskell port's
algorithm is correct independent of GHC*"). A Python mirror cannot test a Haskell source file; it can only be
*asserted* to mirror it, and nothing asserts it. The Lua mirror is also **not a mirror of the Lua port's semantics**:
`quilt-lua/reference_vibe.py` uses `a=42, b=7` and asserts the **swap** (`b==42, a==7`) — the Lua port's own
`run_test` uses `b=0` and fails.

**None of the three ports has a CI workflow. None has a `.gitignore`.** Nothing has ever run these tests.

---

## 2. `quilt-doctor` — the fleet built the meta-audit tool it keeps needing, and nobody has looked at it

**Repo:** `SuperInstance/quilt-doctor` (unseen; 0 prior reports).

**What it is.** A debugging tool that projects a project's own commit cadence through four substrates — **JEPA**
(linear predictor: does the cadence predict itself?), **MOTH** (QPAM quantum circuit: is the signal music or noise?),
**SPECTRAL** (rFFT + real QFT: one drum or two?), **JEV** (is the recorded work verifiable?) — and writes every
observation to a hash-chained Quilt WAL so the diagnosis is replayable.

**Why another agent should care — this is the most valuable thing in the fleet and it is unexamined.** It implements,
as *working code*, exactly the discipline this whole scout series keeps demanding and rarely finds:

* **No naked verdicts.** Every `Projection` carries its receipts: `in_dist_cos`, `extrapolation_cos`, `null_mean`,
  `null_std`, `null_z`, `null_n`, `null_seed`, `window`, `n`.
* **The null model IS the experiment.** Each lens is re-run on the *shuffled* series N times; the verdict is the
  z-score against that null. The README: "*a lens that scores shuffled data the same as real data is measuring a
  convention, not the project.*"
* **Abstention is not condemnation.** Offline substrates yield `{"jev": "skipped"}` and a neutral 0.5 — verified in the
  live run below ("*MOTH — score 0.50 / substrate unavailable — abstaining (quantumaudio not installed)*").
* **Refusal to score on thin data.** `claims.py` sets `MIN_ACTIVE_DAYS = 5`; below it the tool says "*INSUFFICIENT
  DATA: 1 active day(s) < 5 — null_z below measures window emptiness, not structure*".
* **Falsifiable claims with a kill condition and a streak.** `claims/fleet-2026-09-26.json`:
  `"kill_if": {"receipt": "null_z", "op": "<", "value": 1.5}, "kill_after_streak": 2`.

**Verified by execution, not by reading.** `python3 run_doctor.py <repo> <out>` → **exit 0, three artifacts**
(`report.md` 1,246 B, `report.json` 1,881 B, `quilt.jsonl` 7,735 B / 40 lines) — counted, not inferred from an exit code.

**I verified the WAL chain independently** (my own FNV-1a + canonicalisation, not the tool's `verify()`):

```
lines=40  hash_mismatches=[]  chain_breaks=[]  seq_gaps=[]     INDEPENDENT VERDICT: CHAIN INTACT ✓
```

**And I checked it can actually detect tampering** — flip one `score` in the last line:

```
lines=40  hash_mismatches=[39]                                 INDEPENDENT VERDICT: CHAIN BROKEN ✗
tool verify() on TAMPERED wal -> {'ok': False, 'divergences': [{'seq': 39, 'why': 'hash_mismatch'}], 'lines': 40}
```

A single altered number is caught by both. This is a real, tamper-evident receipt chain.

**Positive control — the suite can go red.** I ran the 69 tests with a hand-written pytest shim (no PyPI reachable;
`raises`, `skip`, `mark.parametrize`, `mark.skipif`, `pytestmark`, `tmp_path`, `monkeypatch` implemented) and
**validated the shim itself with mutations** before trusting it:

| baseline | mutation | result |
|---|---|---|
| 52 passed / 14 failed / 5 skipped | `nulls.py`: `"null_z": round(z,3)` → `0.0` | **51 / 15 / 5** (1 more failure) |
| 52 / 14 / 5 | `nulls.py`: `with_null_receipts()` → `return None` | **46 / 20 / 5** (6 more failures) |
| 52 / 14 / 5 | restore | 52 / 14 / 5 |

The suite is genuinely sensitive to the tool's core contribution (the null receipt), not to incidental code.

### Structurally wrong: its CI has been red for all 15 of its runs

`GET /actions/runs` on `quilt-doctor`: **15 runs of the `tests` workflow, 15 × `failure`**, oldest 2026-09-26T02:34Z.
Per-job: `Install deps -> success`, **`Run suite -> failure`**, on both Python 3.11 and 3.12. The pytest step has
**no `|| true`** — this is an honest red badge, and the cause is provable:

1. `tests/test_oracle_lens.py:37` opens **`/tmp/quilt-doctor/docs/HOLISTIC-VIEW-2026-09-26.md`** — an absolute path
   to the author's own machine. The file **is in the repo** (`docs/HOLISTIC-VIEW-2026-09-26.md`, 5,122 B) but the test
   never reads the repo copy. In CI the checkout is at `/home/runner/work/...` → this test **can never pass**.
2. `tests/test_guard.py:28` calls `active_days("/tmp/rounds/pong-quilt")` — a clone of a *different* repo. The
   workflow has no fixture step → `git log` exits 128 → the test fails.
3. `tests/test_moth_ledger_bridge.py:73` does `from moth_ledger import Ledger`. **`moth_ledger` is 404 on PyPI** and
   the CI never installs it. The `pytestmark = pytest.mark.skipif(not MOTH_LEDGER, ...)` guard is at the **wrong
   granularity** — `examples/moth_ledger_bridge.py` *is* importable, so `MOTH_LEDGER` is `True` and the guard never
   fires; the failure happens one import deeper, in 5 tests.

**The irony worth writing down:** a tool whose entire purpose is to make the fleet's unverifiable claims falsifiable
cannot run its own suite in CI, because three of its tests hardcode the author's filesystem. `run_doctor.py:16` also
hardcodes `sys.path.insert(0, "/root/.openclaw/workspace/jev-quilt")` (soft — it is inside a `try` and the JEV lens
degrades to a local-only run).

---

## 3. `plato-protocol-test` — the fleet's only cross-implementation conformance suite, and it asserts nothing

**Repo:** `SuperInstance/plato-protocol-test` (unseen).

**What it is.** 23 tests validating any PLATO engine-block implementation against a canonical wire-protocol spec
(`protocol_spec.py` = "the single source of truth"). This is **exactly the harness the 5-sigma Quilt family needs and
does not have** — and it is green, daily, and reusable.

**Why another agent should care.** It is the fleet's proof that the *pattern* works: one spec file, one parameterised
suite, a CI matrix over implementations.

### Structurally wrong: a new failure shape — a conformance harness whose own conformance is unfalsifiable

`GET /actions/runs`: **21 runs, "PLATO Conformance Tests" success** — most recently 2026-10-20, 10-19, 10-18, 10-17,
10-16. All green. **Every one of them executed zero assertions.** Two independent reasons, stacked:

1. **The matrix names four implementations and starts none.**
   ```yaml
   matrix:
     implementation:
       - {name: C,      port: 1234}
       - {name: Rust,   port: 8080}
       - {name: Elixir, port: 4000}
       - {name: Zig,    port: 1337}
   ```
   The job checks out, installs pytest, and runs the suite. There is **no step anywhere in the workflow (or the repo)
   that starts a C/Rust/Elixir/Zig server** — no `docker`, no `cargo run`, no `subprocess`, nothing.
2. **The fixture skips when the implementation is unreachable** (`conformance_test.py:203-204`):
   ```python
   except (ConnectionError, OSError) as exc:
       pytest.skip(f"{impl} implementation not reachable at {host}:{port}: {exc}")
   ```
   I executed that exact path against CI's own target:
   ```
   RESULT: pytest.skip RAISED -> C implementation not reachable at localhost:1234: [Errno 111] Connection refused
   ```
   So all 23 tests **skip** rather than fail.
3. **And the step is fail-open anyway**: `pytest conformance_test.py -v --junitxml=... || true` — in *both* jobs
   (`conformance` and `full-suite`).

**Three independent green paths, none of them a passing test.** This is a sharper version of the fleet's known
"unfailable test step" class: the badge is not just unreachable-red, it is *unreachable-red in two ways at once*, and
the `|| true` means even a real regression would be swallowed. The uploaded "Compliance Report" is a
**hardcoded markdown table** (`| C | 1234 | See artifact |`) — the artifact it points at is the junitxml of a run
in which every test skipped.

---

## 4. Two different polyformalisms wearing the same five opcode names

**Repos:** `quilt-haskell`/`quilt-lua`/`quilt-j` (the "5-sigma polyformalism") vs. `quilt-vm-wasm` (Layer 1),
`quilt-types` (2), `quilt-linker` (3), `quilt-opt` (4), `quilt-gc` (5) — the "5 layers of the polyformalism".

Both families speak BIND / LINK / EFFECT / VIEW / TICK. They are **not the same doctrine**:

| | 5-sigma runtime ports | 5-layer stack |
|---|---|---|
| cell | `{id: u64, dials: 16×int16, neighbors: []u64}` | `{name: str, value: Any, immutable: bool, created_at: float}` |
| EFFECT | dial propagation / broadcast | **a reversible transformation** — `{target, forward_name, inverse_name, arg}` (a lens) |
| shared hash | `0xe435d91d6d92a1d8` | **absent** — the string appears in **none** of the five layer repos |
| fleet canary `0x24a555471370b18d` | **absent** | **absent** |

`grep` for the fleet canary across all eight repos: **zero hits.** `grep` for the 5-sigma hash across the five layer
repos: **zero hits.** The two programs share a vocabulary and nothing else. This is the same shape as the
`conservation-spectral-*` 12.75× spread already reported for a sibling family — **and it is worse there, because the
shipped conformance check cannot detect it.**

### The positive control: the Python layer stack gets this right

All four layer suites are **unittest**, import the real module, and are **mutation-verified to go red**:

| repo | suite | mutation (presence asserted first) | mutated | restored |
|---|---|---|---|---|
| `quilt-types` | 16 | `CellGraph.bind` → `return None` | **4 failures + 1 error** | 16/16 OK |
| `quilt-opt` | 11 | `link_transitivity` → `return 0` | **1 failure** | 11/11 OK |
| `quilt-gc` | 12 | `GC.collect` → `return 0` | **2 failures** | 12/12 OK |
| `quilt-linker` | 13 | `parse_qm` → `return None` | **1 failure + 12 errors** | 13/13 OK |

**The fleet demonstrably knows how to write a falsifiable test suite** — the technique is two repos away from the
family that fakes it. The gap is not skill, it is that nobody pointed the good tooling at the ports.

`quilt-vm-wasm` (Layer 1) has **no `tests/` directory at all** and only 6 `#[test]`/`#[cfg(test)]` occurrences; its
README's own gallery is titled "07-the-test-count.svg".

---

## 5. `constraint-theory-engine-cpp-lua` — a genuinely strong C++ engine whose flagship path CI never builds

**Repo:** `SuperInstance/constraint-theory-engine-cpp-lua` (unseen; 82,617 code bytes across 25 code files).

**What it is.** C++17 constraint engine: CDCL solver (conflict-driven clause learning), AVX-512 batch checking,
LLVM IR emitter, LuaJIT bridge, "83+ constraint primitives" (snap, funnel, Laman, consensus, holonomy).

**Why another agent should care.** This is real, portable, performance-oriented C++ with a working test suite — and
**I compiled and ran it** (`g++ 12.2.0`, `-std=c++20`), because `cmake`/`ctest` are absent from this sandbox:

| test binary | result |
|---|---|
| `test_constraint` | exit 0 — "All constraint tests passed!" |
| `test_solver` | exit 0 — "All solver tests passed!" |
| `test_emitter` | exit 0 — "All emitter tests passed!" |
| `test_constraint_extended` | exit 0 — "All extended constraint tests passed!" |
| `test_solver_extended` | exit 0 — "All extended solver tests passed!" |
| `test_avx512` (scalar build) | exit 0 — 5/5 sub-tests |
| `test_avx512` (**-mavx512f -D__AVX512F__**) | exit 0 — 5/5 sub-tests (host CPU: Xeon 8163, has `avx512f`) |

**Structurally wrong: the CI matrix pins the flagship path OFF, and the AVX-512 test is gated on the same flag.**

```yaml
strategy: { matrix: { avx512: [OFF] } }          # a one-element matrix
...
cmake .. -DENABLE_AVX512=${{ matrix.avx512 }} ...
```
```cmake
option(ENABLE_AVX512 "Enable AVX-512 vectorized checking" OFF)
add_executable(test_avx512 tests/test_avx512.cpp)
if(ENABLE_AVX512)
    add_test(NAME avx512 COMMAND test_avx512)     # <-- registered ONLY when AVX-512 is on
endif()
```

Consequences, precisely:

* `ENABLE_AVX512` is `OFF` in **every** CI run ⇒ `__AVX512F__` is never defined ⇒ `src/avx512_check.cpp`,
  `include/flux/avx512_check.hpp` and `src/constraint.cpp:8` are `#ifdef`'d **out of the build entirely**. The
  headline feature — "*evaluate 16 constraints simultaneously with SIMD intrinsics*" — is **never compiled by CI**.
* `add_test(NAME avx512 ...)` is inside the same `if`, so `test_avx512` is **built but never registered as a ctest
  test** ⇒ it never runs in CI either. Even the scalar-fallback variant of that suite never executes.
* A one-value matrix is not a matrix. The workflow reads as if it *intended* to cover both `ON` and `OFF`.

**This is an assurance gap, not a bug** — I built and ran the AVX-512 path myself on an AVX-512 host and it passes.
The correct framing: *the code is right and the CI is structurally unable to notice if it stops being right.*

---

## Reusable detectors (each of these is one command)

* **A "byte-exact" cross-port badge is only a claim about the *serialization* if the constant is a hash of the
  serialization.** Recompute it from the spec before trusting it: strip the type tag, reverse the neighbor order,
  drop the neighbors — if a different variant also matches, the check is measuring the wrong thing.
* **Two ports of one doctrine can disagree on an opcode while every shipped check stays green.** Grep each port for
  the opcode's *signature* (arity + argument type), not just its name. `effect(Fabric, Word64)` vs `effect()` is the
  whole divergence, visible in one line.
* **A PASS string printed by an unguarded code path is not a test.** `grep -n "assert" <port>` and count. If the
  answer is 0 and the file still prints "PASS: … behave per spec", the port is shipping a slogan.
* **A test file that reimplements the logic inline instead of calling the port is a fork of the port.** In
  `quilt-lua`, `test.lua` says so in a comment; and the inline copy's fixture differs from the original's.
* **A conformance matrix that names implementations and starts none, plus a skip-on-unreachable fixture, plus `|| true`
  = three green paths and zero assertions.** Check all three separately.
* **`pip install X || true` where X is 404 on PyPI is a silent stub.** Check the install line against the import line
  *and* against the package index.
* **A suite that hardcodes `/tmp/<repo>/...` or `/root/<user>/...` cannot pass in CI.** `grep -n '"/tmp/\|"/root/' tests/`
  and cross-check the path against files that *are* in the repo.
* **A `pytestmark` skipif at the wrong granularity does not fire.** The guard must sit on the import that actually
  fails, not on a neighbouring one that happens to succeed.
* **A `matrix:` with one value is a constant.** `avx512: [OFF]` is not coverage.
* **Positive control for any hand-rolled test shim:** mutate the module under test and confirm the suite goes red
  *before* trusting a green run. A shim that reports OK on a broken module is worse than no shim.

## What I did not examine (stated so the next scout does not re-walk it)

* All 118 prior reports' repos — re-derived as the examined set, not re-read.
* `conservation-spectral-*` (23 ports) — already reported (12.75× spread); cited only as a sibling pattern.
* The 352-repo `ternary-*` cluster: scanned all 352 trees — median 17,583 code bytes, 328/352 have no test file,
  336/352 have a CI workflow, 2 have zero code bytes. Substantive and uniform; no sharp defect found in the sample,
  so no claim is made about it.
* The 283-repo `lau-*` Rust cluster — already characterised in a prior report.
* `plato-protocol-test`'s 23 tests were not executed against a live PLATO server (none is available in this sandbox);
  the skip path was executed directly instead.

## Environment notes (durable)

* `npm install` **works in `/tmp`** (overlay fs) and fails on the NAS mount — `fengari` + `fengari-node-cli` installed
  in 2 s, which is how the Lua port was actually run.
* `www.lua.org` is unreachable from the sandbox (SSL_ERROR_SYSCALL); `github.com`, `raw.githubusercontent.com` and
  `api.github.com` are not. `pypi.org` answers over curl (HTTP 200/404) but `pip install` still fails.
* `fengari` is **float-only** (no integer subtype; `0xFFFFFFFF` → `-1`), so it can execute small-int Lua semantics
  faithfully but **cannot** reproduce a 64-bit FNV hash. Use it for control flow, transliterate for arithmetic.
* `g++ 12.2.0` and `make` are present; `cmake`, `ctest`, `cargo`, `rustc`, `julia`, `ghc`, `lua`, `j` are not.
  C++ repos can still be built and run by hand with `g++ -std=c++20 -Iinclude`.
* No `gh` CLI; drive the REST API with curl. `actions/jobs/{id}/logs` needs admin rights (403 with a user token);
  `actions/runs` + `/jobs` (step-level conclusions) do not, and are enough to prove a step failed.
