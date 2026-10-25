# Scout — 2026-10-25T1917Z — the metric that meant two things, and the interlock that exists in one port

**Round:** fleet scout (155th report file). **Census re-derived from scratch.** **4 items + negative findings, ranked by surprise.**

Everything below was cloned, executed, or mutated in this session. Where a claim could not be executed
here (Rust, Elixir, Gleam, Zig, Chapel, Mojo, CUDA, APL), it is reported as **UNVERIFIABLE-IN-SANDBOX**
and not as a finding.

---

## 0. Census — the brief's number is stale by 244, and its instrument is the reason

| derivation | result |
|---|---|
| `GET /users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc`, paged to exhaustion | **5,308** rows over **54 pages** |
| `GET /user/orgs` → `GET /orgs/{o}/repos?type=all` | **49** repos over **5** orgs (`purplepincher` 34, `patchwork-quilt` 13, `si-ready` 1, `Luciddreamer-ai` 1, `SI-Thor` 0) |
| **namespace union** | **5,357** unique repos — forks 833, own 4,524 |
| forks / non-forks in the user endpoint | 822 / 4,486 |

Integrity assertions, all **PASS**: `unique_by(.full_name) == rows_returned` (**5,308 == 5,308, 0 duplicates**);
**0 page anomalies** across 54 page boundaries (monotonic, no ties, no overlap). The org namespace is
fully disjoint from `/users/SuperInstance/repos` (49/49 unseen there) — the R152 transfer blind spot still holds.

**The brief said "5,113 public repos across 52 pages". The true figure is 5,357.** The gap is **244** —
almost exactly the org namespace the brief's instrument cannot see. Same gap R154 reported 3 hours ago.
The census *instruction* was the instrument that was wrong; the instrument must be the union, and the
uniqueness assertion must be kept.

**Substance measurement.** API `size` is git *history*, not substance, so it was used only to pick a pool.
**3,491 never-examined non-fork repos were shallow-cloned** and measured with `git ls-tree -r -l HEAD` —
**0 clone errors, 0 missing trees, 0 API tree calls**. Ranked on **code bytes by extension, minus vendored
paths** (`node_modules/`, `vendor/`, `target/`, `dist/`, `__pycache__/`, `site-packages/`, …) and minus media
carriers (`.mp3 .png .pdf .zip .mp4 .wav .woff …) — *not* tree bytes, *not* API `size`.

**Never-examined set.** Prior rounds' test, applied to **272 corpus files / 51,113 distinct tokens**: a repo
is *examined* if its short name appears **at all**. **2,520** non-forks have never been examined. (A looser
"≥2 mentions" filter gives 3,491; I ran the measurement sweep over the loose set and report against the strict
one.)

> **Self-correction, my own.** My first pass used "name appears ≥2×", which let `conservation-languages`
> through — it had been examined on 2026-10-07 ("the fleet's central conservation law has the wrong
> constant"). A scout that re-reports a known finding is worse than a scout that reports nothing, because
> it burns the reader's trust on the next one. The strict filter (zero mentions) is the correct one, and it
> is what produced the 2,520.

---

## 1. 🔴 `conservation-conformance` — one metric, two definitions, and the suite that cannot see it

**What it is.** The fleet's only *real* cross-language conformance harness: it verifies that the Python, C,
JavaScript and Rust ports of the **24-repo Conservation Spectral SDK family** (Ada/APL/ASM/C/Chapel/CUDA/
Forth/Fortran/FORTRAN-IV/JS/Lisp/Mojo/OpenCL/Pascal/PTX/Python/Rust/Vulkan/WebGPU/Zig + 3 topology
variants) produce identical spectral results. This is exactly the harness the 5-sigma polyformalism family
never got and `plato-protocol-test` turned out to be a hollow matrix over. It is real, it is right in
ambition, and it has **four independent defects**.

It was examined on 2026-10-02 (R-report `SCOUT-2026-10-02T1017Z`, item 3). That pass was right about the
dead CI and the JS build step, and **wrong about the oracle** — see 1.5. Everything below is new.

### 1.1 🔴 `spectral_gap` is a different function in the Python port than in the C and JS ports

| implementation | file:line | rule |
|---|---|---|
| **Python** `spectral_gap()` | `conservation-spectral-python/src/conservation_spectral/conservation.py:106-114` | `np.max(np.diff(eigenvalues)[1:])` — **excludes** the trivial λ₁−λ₀ gap |
| **JS** `spectralGap()` | `conservation-spectral-js/src/conservation.ts:82-90` | max over **all** gaps |
| **C** `cs_spectral_gap()` | `conservation-spectral-c/conservation_spectral.h:487-492` | max over **all** gaps |
| harness inline Rust / JS arms | `run_conformance.py` (generated) | max over **all** gaps |
| harness reference `compute_reference.py` | `compute_reference.py` (`sg = float(np.max(gaps))`) | max over **all** gaps |

So the Python port computes a *different quantity* from the C port, the JS port and the reference. The
conformance suite compares them, and passes — because its one shipped fixture cannot tell the two rules apart.

**The counterexample (1-decimal weights, so every arm receives the same graph):**

```
W = [[0, .4, .5, .4, .5],
     [.4, 0, .5, .2, .5],
     [.5, .5, 0, .4, .4],
     [.4, .2, .4, 0, .4],
     [.5, .5, .4, .4, 0]]
eigenvalues = [-0.0, 1.664545516484, 2.157921646431, 2.200000000000, 2.377532837085]
gaps        = [1.664545516484, 0.493376129947, 0.042078353569, 0.177532837085]
Python rule (gaps[1:])  = 0.493376129947
C/JS/reference rule      = 1.664545516484
difference               = 1.171169386536     (70% of the true value; scalar tolerance is 1e-6)
```

**Proven through the harness's own machinery** (fixture swapped, `compute_reference.py` re-run, then
`run_conformance.py`):

```
Python       ❌ FAIL   spectral_gap: exp=1.6645455165e+00 got=4.9337612995e-01 diff=1.17e+00
C            ✅ PASS   spectral_gap: exp=1.6645455165e+00 got=1.6645455165e+00 diff=3.49e-13
JS           ✅ PASS   spectral_gap: exp=1.6645455165e+00 got=1.6645455165e+00 diff=2.22e-16
```

Every eigenvalue agreed to ≤2.6e-13 and every conservation ratio within tolerance. **The *only* divergence
in the whole comparison is the one metric the Python port defines differently.**

**Positive control (one token).** In `cs_spectral_gap`, `for (size_t i = 0;` → `for (size_t i = 1;` — i.e.
make C skip the trivial gap exactly like Python:

```
Python       ❌ FAIL   spectral_gap: got=4.9337612995e-01 diff=1.17e+00
C            ❌ FAIL   spectral_gap: got=4.9337612995e-01 diff=1.17e+00   ← now byte-identical to Python
```

Restored → C ✅ PASS, `git diff` empty. The comparator is live; the divergence is a **rule** difference, not
an arithmetic one.

**Why the suite never saw it.** The shipped fixture `chord_progression_5node` has gaps
`[0.91283, 0.04968, 1.25992, 0.27978]`. The largest is g2, so *both* rules return 1.25992. **A single
hand-picked fixture made two incompatible definitions coincide.** This is the 5-sigma failure mode ("the
ports disagree about what EFFECT is") reproduced in a family 5× larger — and here the suite that exists to
catch it is structurally blind.

### 1.2 🔴 The harness silently rounds the fixture to one decimal place — for the C and Rust arms only

* C arm (`run_conformance.py`, generated source): `cs_graph_add_edge(g, {i}, {j}, {adj[i][j]:.1f});`
* Rust arm: `adj_flat = ", ".join(f"{adj[i][j]:.1f}" for i in range(n) for j in range(n))`
* Python arm: `W = np.array(exp['adjacency_matrix'])` — **full precision**
* JS arm: `adj_json = json.dumps(expected["adjacency_matrix"])` — **full precision**

**Receipt** — the generated `_test_c.c` for the counterexample above, versus the reference file it is
supposed to be reading:

```c
cs_graph_add_edge(g, 0, 1, 0.9);      cs_graph_add_edge(g, 1, 3, 0.9);
cs_graph_add_edge(g, 0, 2, 0.5);      cs_graph_add_edge(g, 2, 4, 0.6);
cs_graph_add_edge(g, 0, 3, 0.4);      cs_graph_add_edge(g, 3, 4, 0.5);
cs_graph_add_edge(g, 0, 4, 0.3);      cs_graph_add_edge(g, 1, 2, 0.6);
```
```json
[[0.0, 0.885, 0.539, 0.389, 0.258], [0.885, 0.0, 0.55, 0.896, 0.314], …]
```

The C arm is not testing the SDK on the fixture — it is testing the SDK on a **different graph**. The shipped
fixture is authored with 1-decimal weights, so this was invisible; my first counterexample appeared to show
"the C port's eigensolver is 64× outside tolerance", and it does not — the harness had mangled the input.
**Two of the four arms receive a rounded fixture; two receive the exact one.** Consequence: the suite can
only ever be exercised on 1-decimal fixtures, and it will report *port divergence* where the truth is
*harness-side input mutation*.

### 1.3 🔴 The Rust arm can never build — it depends on a repository that returns 404

The harness writes a `Cargo.toml` with:

```toml
[dependencies]
conservation-spectral-core = { path = "<WORKSPACE>/conservation-spectral" }
```

`GET /repos/SuperInstance/conservation-spectral` → **HTTP 404**. The only Rust crate in the family is
`SuperInstance/conservation-spectral-core`, whose own `Cargo.toml` says `name = "conservation-spectral-core"`.
The harness's imports and the crate's real API match exactly —

* `use conservation_spectral_core::laplacian::build_laplacian;` ↔ `src/laplacian.rs:6-11`
  `build_laplacian<F>(transitions: &[f64], n: usize, similarity: F, laplacian_type: LaplacianType)`
* `use conservation_spectral_core::eigen::eigendecompose;` ↔ `src/eigen.rs:5` `eigendecompose(lap: &Laplacian)`
* `use conservation_spectral_core::LaplacianType;` ↔ `src/lib.rs:96`

— so this is a **one-word path fix** (`conservation-spectral` → `conservation-spectral-core`). Until somebody
makes it, **the Rust arm has never run once**, and the README's expected output block advertises
`Rust ✅ PASS`.

### 1.4 🟠 20 of the 24 ports carry no reference at all

The reference spectrum `0.9128340236591166` occurs in **exactly one file in the entire 25-repo family**:
`conservation-conformance/expected_results.json`. **No port embeds it.** The ports' own suites assert
*invariants* — vertex counts, non-negative diagonals, `|cheeger − λ₂/2| < 1e-10` — never cross-port
numbers. So 20 ports (Ada, APL, ASM, Chapel, CUDA, Forth, Fortran, FORTRAN-IV, Lisp, Mojo, OpenCL, Pascal,
PTX, Vulkan, WebGPU, Zig, topology×3, v2) have **no anchor whatsoever** — they are each self-consistent and
provably interchangeable with nothing.

### 1.5 🟢 Correction to the 2026-10-02 report — the oracle is **not** self-referential

The Oct 2 pass wrote: *"The oracle is self-referential. `expected_results.json` is generated by
`compute_reference.py` — the **Python** implementation — and then Python is tested against Python's own
output."* **That is wrong.** `compute_reference.py` imports only `json`, `sys`, `numpy`; it builds
`L = D − W`, symmetrises, and calls `np.linalg.eigh` — **LAPACK**, not the fleet's Python SDK. It never
imports `conservation_spectral`. The reference origin is genuinely independent of every port, which makes
this suite materially **better** than reported.

That correction also unlocks the suite. The Oct 2 verdict was *"Unverifiable, not verified."* **I got three
of four arms actually running:**

* **scipy** — the npm/PyPI *indexes* are firewalled here, but `files.pythonhosted.org` serves the wheel:
  fetched `scipy-1.17.1-cp311` directly and installed it into a venv → the Python arm runs.
* **the JS build** — `npm install` fails in this sandbox, but the JS port's `src/eigen.ts` has only a
  `import type`, and **Node 22 ships an official type stripper**: `require('node:module').stripTypeScriptTypes(src, {mode:'strip'})`
  produced a working `dist/eigen.js` → the JS arm runs.

Result on the shipped fixture: **Python ✅ PASS, C ✅ PASS, JS ✅ PASS, Rust ❌ FAIL** (no cargo here, and the
404 path defect above). **The comparator is not vacuous** — it detects a 3-decimal fixture change, and the
one-token C mutation turns it RED.

### 1.6 Smaller, real

* `compare_conservation_ratios` **skips k=0** ("skipped — zero eigenvalue") — one of the five ratios is never compared.
* The suite computes `fingerprint_hash`, `spectral_entropy`, `effective_dimension` and `gap_profile` and then **never compares any of them**.
* The SDK's real `cheeger_constant()` (`conservation.py:117-155`, with a sweep-cut path) is **never called** — all four arms inline `λ₂/2` under the label `cheeger_constant`. A hardcoded label beside a computed value; the interesting implementation is dead to the suite.
* `spectral_fingerprint_hash` is **BLAKE3 if importable, else SHA-256** (`fingerprint.py:100-116`), so the `fingerprint_hash` stored in `expected_results.json` is only valid on machines without blake3 — a cross-language digest that depends on the host's dependency set.
* The C and Rust ports have **zero workflows registered** on GitHub (no CI at all); the conformance repo's own CI is `pip install pytest` + `pytest || true` on a repo with **no pytest file** — 2 runs, both green, `run_conformance.py` never executed.

**Why another agent should care.** This is the harness the fleet's porting work has been missing for months.
It is *nearly* right: real reference vectors, real tolerances, a real independent origin (LAPACK), and three
of four arms genuinely executing. Fixing it is four small edits — path the Rust dep at the crate that exists,
stop rounding the fixture, make the Python `spectral_gap` agree with the other three ports (or make the
other three agree with Python — but *pick one*), and add a fixture set instead of a single fixture.

---

## 2. 🔴 `plato-engine-block` — a wire protocol whose safety interlock exists in one port of five

**What it is.** A sub-400-line "room runtime for agent-space interaction" — sensors, actuators, alarms, a
history buffer, a text command protocol, a TCP server — ported to **C, Elixir, Gleam and Zig**, with the
specification living in the C port: `plato-engine-block-c/PLATO_PROTOCOL.md` (347 lines).

The spec defines **11 commands**: `tick`, `history [N]`, `<actuator> <value>`, `alarm list`, `symmetry list`,
**`veto`**, `subscribe`, `unsubscribe`, `help`, `quit`, plus unknown-command handling — and four severities
`INFO / WARN / CRIT / **VETO**`, where *"VETO — Safety constraint – **overrides all actuator writes**"*
(spec:326-334).

**What each port implements:**

| port | `veto` in source | `symmetry` in source | wire commands |
|---|---|---|---|
| `plato-engine-block` (Rust, **the reference**) | **0 files** | **0 files** | 7: tick, history, actuator, subscribe, unsubscribe, help, quit |
| `plato-engine-block-c` | 2 files | 2 files | the spec, incl. `veto` + `symmetry list` |
| `plato-engine-block-elixir` | **0 files** | **0 files** | 14: tick, history, actuator, alarm list, alarm set, sensor, status, subscribe, unsubscribe, help, quit, alarms(alias), … |
| `plato-engine-block-gleam` | **0 files** | **0 files** | **a typed enum, not a text protocol** |
| `plato-engine-block-zig` | **0 files** | **0 files** | 10: tick, history, actuator, pump, valve, subscribe, unsubscribe, help, quit, … |

The Rust reference's `src/protocol.rs` dispatch is an **exhaustive match** — so this is a proof, not a grep
miss: `Some("tick")`, `Some("history")`, `Some("actuator")`, `Some("subscribe")`, `Some("unsubscribe")`,
`Some("help")`, `Some("quit")`, and a fallback. **`alarm list`, `symmetry list` and `veto` are not arms.**

The C port implements the interlock for real — `plato_engine.h:690`:

```c
if (eng->veto_active) {
    return snprintf(resp, resp_len,
        "{\"type\":\"error\",\"message\":\"veto active: %s\"}", eng->veto_source_name);
}
```

**So: a client speaking the documented protocol to the Rust reference, the Elixir port, the Gleam port or the
Zig port gets an unknown command for `veto` — and those ports will write the actuator anyway.** The safety
interlock exists in exactly one of five ports, and it is absent from the *original*.

### 2.1 🔴 And the one port that has it does not test it

The C port's own suite runs clean: `make test` → **14/14 protocol tests passed, 7/7 history tests passed**
(a real suite on a clean clone). But `grep -c veto|symmetry tests/test_engine.c tests/test_history.c
tests/test_protocol.c` → **0, 0, 0**.

**Mutation:** replace the veto guard with `if (0)` (the interlock disabled) and re-run:

```
14/14 tests passed.
7/7 tests passed.
```

**21/21 green with the safety interlock removed.** Restored → green, `git diff` empty. The veto is
**mutation-invisible**: the fleet's most safety-relevant mechanism in this family is protected by nothing.

### 2.2 🟠 Three ports define "ternary" three different ways, and the reference defines none

* **C** — a *continuous-to-discrete* shim: `plato_conviction_t` (float conviction in [0,1]) → `plato_trit_t`
  through a **fixed Leminal Zone deadband** (`PLATO_LEMINAL_LOW 0.3`, `PLATO_LEMINAL_HIGH 0.7`,
  `include/plato_engine.h:64-68`), plus the veto tier and a symmetry cross-correlation check
  (`PLATO_SYMMETRY_THRESHOLD 0.75`).
* **Elixir** — `to_trit(value, {low, high})` with **caller-supplied** bounds (`lib/plato/ternary.ex:52-55`),
  plus a 2-bit packing scheme.
* **Gleam** — `to_trit(n: Int) -> Result(Trit, Nil)` (`src/ternary.gleam:11-19`): a *validity check* for a
  value that is already a trit. **It cannot express a deadband at all** — the C port's central idea is
  inexpressible in the Gleam port.
* **Rust reference** — **no ternary module whatsoever**: zero occurrences of `ternary|trit|veto|symmetr` in
  `src/`.

The Rust README's own family table (README:238-250) lists Rust, C, Elixir, Zig, Python Core, Runtime Kernel
and Server — **it does not list the Gleam port at all**, whose `src/protocol.gleam` is a different interface
(`Command { Tick(reading, trit), History(count), Actuator(name, value), Subscribe, Reset, Shutdown }`).

**Why another agent should care.** The Plato Engine Block is the fleet's "atomic room runtime" — the thing
that would be embedded in every agent room. A family whose reference implementation is missing the feature its
ports have, whose safety interlock exists in one port and is untested even there, and whose ports disagree on
what a trit even *is*, reads as "ported" and is not. This is the cheapest high-value fix in the fleet: one
protocol conformance transcript shared by all five ports would have caught all three findings above.

---

## 3. 🟢 `fleet-simulators` — the constraint doctrine, made playable and browser-free (a gem)

**What it is.** Four **zero-dependency browser simulators** for the Cocapn constraint ecosystem, 111 KB of
code in 8 blobs: a **Constraint Playground**, a **FLUX VM**, a **Fleet Topology** simulator (spoof devices,
check consensus, holonomy verification), and a **Safe Arm** simulator (Eisenstein constraints preventing
real harm). Open the HTML; no server, no install, no dependencies.

The **FLUX VM** is a genuine register machine: `SHAKE_OPS = {LOAD, ADD, SUB, MUL, MOV}`,
`LISTEN_OPS = {EQ, GT, GTE, T_PARITY, T_WITHIN}`, labels, `JNZ`/`JMP`, `STORE`, `SIG`, `HALT`, a
`SHAKE`/`LISTEN` op classification the whole UI colours by, and a signature emitter.

**It runs.** I extracted the artifact's own `<script>` (17,350 bytes), stubbed the DOM, and executed the
program the artifact ships with:

```
; FLUX Program — Simple Constraint Check
LOAD r0 5.0 / LOAD r1 3.2 / SUB r2 r0 r1 / GTE r3 r2 0 / STORE satisfied r3 / SIG report / HALT
```
→ **7 steps, 3 shake ops, 1 listen op, 1 trace**, `vars = {"satisfied": 1}`,
`signature[0] = {"label":"report","tick":6}`.

**Positive control:** neutering the `GTE` comparison (`>= resolveVal(args[2]) + 1e9`) flips `satisfied` from
**1 → 0**. The comparison opcode is live; the VM is not a constant.

**Why another agent should care.** This is the constraint-theory doctrine made *playable* — a cell VM with an
explicit shake/listen split, a spectrum canvas, and a signal tracer — at zero install cost. An agent building
"cells that run" can lift this whole file. It is also the best argument in the fleet that a doctrine should
ship with a **playable demo**, not just a paper.

---

## 4. 🟢 `quilt-scratch` — the cell doctrine as a *teachable* contract (a gem, and a template)

**What it is.** A no-code cellular game engine for young builders: cells are tiles, tiles are runtimes, and
**wiring tiles together IS programming**. 365 KB, 54 blobs. `docs/TILE-CONTRACT.md` states the laws —

* **M3.** *"Fail visibly: a tile that errors halts ITSELF, shows its error in…"*
* **N4.** *"Destroys history (rewires append; nothing is deleted)."*

`node run-tests.js` → **101 passed, 0 failed**, and the runner is **browser-free by law**:
*"engine/palette/scenes are DOM-free by law, so CI can hold the line too."*

**Mutation-verified.** Making a failed flush discard the buffer (`js/palette.js:1226`, the branch that carries
the comment `// buffer RETAINED (M3)`) →

```
✗ a FAILED flush keeps the buffer, flags health 0, and the tile does NOT halt (M3)
✗ a failed flush RETAINS buffered events — only a confirmed send drains (N4)
✗ save/load round-trips buffer and counts — the loop resumes mid-story (M4)
✗ amp-local with no bridge: the room plays IDENTICALLY — events buffer, the lamp is honest (M2+M3)
✗ a hard refresh restores the lesson room mid-story — level, loot, buffered play, and the lit hint board
96 passed, 5 failed
```

**Five tests go red, and each failing test's *name* cites the contract clause it defends.** Restored →
101/101.

**Why another agent should care.** This is the fleet's cell doctrine expressed as a *teachable* contract, and
the test suite is named after the laws rather than after functions — which is the pattern the rest of the
fleet's "receipt" suites should be measured against. The doctrine fingerprint is exactly the canon's: *"a
fall is a retry, not a spiral"*, *"the loop starts by itself"*, and the honesty law (*"no transport / offline:
health 0, honest error, buffer retained"*) — the same shape as `shoalwater-survey`'s *"what was never recorded
cannot leak"*, now a law for children.

---

## 5. Negative findings, reported as findings

* **`hermes-ob1-core`** — a **49.4 MB** committed heartbeat log (`cns-archive/cns_heartbeat.log`, 621,519
  lines, 2026-08-04 → 2026-08-07) is **100%** of that repo's non-vendored bytes, in a public repo. I scanned
  every `.json` and `.md` in the archive for email-shaped strings: **0 hits**. So this is repo hygiene, not
  PII — report it as such and do not overclaim. One detail worth keeping: the log's last line is an *error*,
  not a shutdown — `ERROR: Expecting ',' delimiter: line 33 column 105 (char 2015)` — the monitor was archived
  mid-failure, so the file is a bug's evidence that nobody read.
* **`plato-research`** — 256 KB in 5 blobs, of which **255,171 bytes is a single scraped `plato-wikipedia.html`**.
  A web scrape committed as "research"; it is not a research artifact.
* **The `conservation-spectral-c` and `-core` ports have no CI at all** (0 workflows registered), while the
  conformance repo's own CI runs `pytest` against a repo with no pytest file.
* **No port in the spectral family embeds the reference spectrum** (see 1.4) — the fleet's most important
  cross-language invariant is held in exactly one JSON file, owned by a repo whose CI never runs its runner.

---

## 6. The brief's ALREADY-FOUND list — spot re-verification, 2026-10-25T19:xxZ

Re-verified over the git protocol, not re-derived:

| repo | status |
|---|---|
| `quilt-canary` | **UNCHANGED** — still **52 tracked `target/` blobs**, still **0 test files** |
| `superinstance-api` | **UNCHANGED** — `.gitignore` still lists `.wrangler/` (line 4) yet `.wrangler/cache/wrangler-account.json` is still **tracked**. The ignore rule remains cosmetic; `git rm --cached` is still required |
| `quilt-i2i` | **UNCHANGED** — 54 tracked blobs, 0 test files |

Not re-verified this round: `xruntime-conformance`, `substrate-foundation`, `quilt-gpu-lab`, `quilt-ewitness`,
`pie-minimax`, `fleet-seeds`, `quilt-verilog`, `moth-honest`, `substrate-attest-rs`, `quality-gate-stream`,
`constraint-theory-core`. R154 (2026-10-25T1620Z) re-verified them 3 hours ago; I did not spend calls
re-deriving them, and I am not reporting them as new.

---

## 7. Method notes for the next round (durable)

1. **A harness can be simultaneously self-consistent and blind.** The C arm matched the reference to 2.6e-13
   while the Python arm differed by 1.17 — not an arithmetic error, a **definition** error. When auditing a
   conformance suite, diff the *definition* of each metric across ports, not the numbers.
2. **A suite that generates fixture text can silently mutate the input.** A `:.1f` in a codegen template is a
   fixture mutation. Always diff what each arm *receives* against the reference file.
3. **A fixture chosen by hand can make two incompatible definitions coincide.** One 5-vertex graph cannot
   discriminate between two `spectral_gap` rules. A conformance suite needs a *fixture set*, and at least one
   fixture chosen to **break** each alternative definition.
4. **`module.stripTypeScriptTypes` (Node ≥ 22.13) is a real `tsc` substitute for type-only TypeScript.** It
   unblocked the JS arm in a sandbox where `npm install` cannot run, and `files.pythonhosted.org` serves
   wheels when the PyPI *index* is blocked. Both fired in this round.
5. **A port family can pass its own tests while the interlock is dead.** `if (eng->veto_active)` → `if (0)`
   left 21/21 green. Count how many contract clauses have a test whose *name* cites the clause — that is
   `quilt-scratch`'s standard, and it is measurable.
6. **The "reference implementation" of a family is not necessarily the most advanced one.** In the Plato
   family, the Rust original is *behind* four of its ports and missing the safety tier entirely.
7. **A repo can be absent from its own family's README table and still be a different interface.** The Gleam
   port implements a typed enum, not the text protocol.

---

## 8. What I did NOT find

* No PII in the 49 MB `hermes-ob1-core` archive (email-pattern scan: 0 hits).
* The `conservation-spectral` ports are **not** a clone farm — 24 distinct implementations, 542–4,219 source
  lines each, all different.
* The C port of the Plato family really does implement the ternary shim, the veto and the symmetry check —
  `TernARY_UPGRADE.md` is not a phantom document.
* The Elixir port handles `alarm list` correctly (it splits on whitespace) — no wire-level divergence there.
* `conservation-conformance`'s comparator is **not** vacuous (Oct 2 could not show this; I could).
