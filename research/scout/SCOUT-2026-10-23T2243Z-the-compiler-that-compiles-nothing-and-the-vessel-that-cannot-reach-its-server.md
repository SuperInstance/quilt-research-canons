# SCOUT 2026-10-23T2243Z — The compiler that compiles nothing, and the vessel that cannot reach its own server

**Scout:** Mavis · **Method:** re-derived census → diffed against 139 prior scout files → ranked by tree/blob substance → read READMEs → executed and mutation-tested what could be executed.

---

## 0. Census (re-derived, not inherited)

The brief said 5,113 public repos. That number is stale. Re-derived from scratch:

| | |
|---|---|
| Public repos (census) | **5,307** |
| Pages at 100/page | 54 (last page 7 rows) |
| Forks | 821 |
| Non-fork | 4,486 |
| Uniqueness assert `unique_by(full_name) == rows_returned` | **PASS** (0 duplicates) |
| Repo basenames ever mentioned anywhere in `research/` | 1,751 |
| **Never examined (all)** | **3,556** |
| **Never examined (non-fork)** | **2,820** |
| Never examined, `lau-*` prefix | **252** |

Paging used `sort=full_name&direction=asc` with the uniqueness assertion on every run. `sort=pushed` was not used — it is not monotonic and pages overlap silently.

The big repos are all already examined: **0** unexamined repos have API `size` > 100 KB, so the unexamined tail is small repos. The mass is in the `lau-*` run (item 5) and in repos small enough to hide in the noise.

---

## 1. `flux-compiler-workspace` — the compiler that compiles nothing

**What it claims.** A FLUX constraint compiler toolchain: "parse constraint expressions, lower to IR, optimize, verify, and emit code for native, AVX-512, CUDA, WASM, eBPF, and RISC-V targets." The feature table lists "**Verification** — Prove translation correctness from source to compiled output" and "**Multi-target codegen** — Emit for native, AVX-512, CUDA, WASM, eBPF, and RISC-V".

**What it is.** Three implementations in one repo, and the live one is the empty one.

| # | Location | Built by cargo? | State |
|---|---|---|---|
| 1 | `crates/fluxc-*` (7 crates) | **yes** — `members = ["crates/*"]` | stubbed |
| 2 | `fluxc-*/` at repo root (8 crates) | **no** — not workspace members | **the real one** |
| 3 | `flux_compiler/*.py` (1,223 lines) | n/a — never run by CI | real, 59 tests, **one real bug** |

### 1a. The live parser cannot parse

`crates/fluxc-parser/src/lib.rs`:
```rust
fn tokenize(input: &str) -> Result<Vec<Token>, ParseError> {
    let _ = input;                       // input ignored
    Ok(Vec::new())                       // always an empty token list
}
fn parse_expr(_tokens: &[Token], _pos: usize) -> Result<(GuardExpr, usize), ParseError> {
    Err(ParseError::UnexpectedEof { msg: "parser not yet fully implemented".into() })
}
```
`fluxc_parser::parse(...)` — the entry point the README's API Reference documents — **always returns an error**. Its only `#[test]` (`parse_exact`) constructs a `GuardExpr::Exact` literal and asserts it equals itself: a tautology.

### 1b. The verifier cannot fail

`crates/fluxc-verify/src/lib.rs:26`:
```rust
pub fn validate(ir: &IrModule, output: &CodegenOutput) -> Result<ValidationResult, VerifyError> {
    // Stub: always passes for now
    Ok(ValidationResult { valid: true, message: format!(...) })
}
```
The crate the README advertises as *"Prove translation correctness"* returns `valid: true` unconditionally, without reading `ir` or `output`.

**The inversion worth noting:** the **orphaned** `fluxc-verify/src/lib.rs` (top level, never built) contains a *real* check — it rejects an IR with no constraints. The stale orphan has a gate; the live one is the stub.

### 1c. The codegen is one placeholder wearing six hats

`crates/fluxc-codegen/src/lib.rs`:
```rust
pub fn generate(module: &IrModule, target: Target) -> ... {
    match target {
        Target::Native => generate_native(module),
        Target::Avx512 => generate_native(module), // stub: falls through
        Target::Cuda   => generate_native(module),
        Target::Wasm   => generate_native(module),
        Target::Ebpf   => generate_native(module),
        Target::Riscv  => generate_native(module),
    }
}
fn generate_native(module: &IrModule) -> ... {
    let assembly = format!("; FLUX compiled: {}\n; TODO: actual codegen\n", module.name);
    Ok(CodegenOutput { target: Target::Native, assembly, bytes: Vec::new() })
}
```
All six targets emit the same string, `bytes` is always empty, and the output is **always labelled `Target::Native`** even when you asked for WASM.

### 1d. The CLI is a printer, and writes no artifact

`crates/fluxc-cli/src/main.rs` (117 lines) — every subcommand is a `println!`:
```rust
Commands::Compile { input, target, output } => {
    println!("Compiling {:?} for target '{}' -> {:?}", input, target, output);
}
Commands::Verify { input, compiled } => {
    println!("Verifying {:?} against {:?}", input, compiled);
}
```
It never opens `input`, never writes `output`, and never calls the parser, IR, codegen, or verifier. Its `Cargo.toml` declares all six workspace crates as dependencies; `main.rs` references **none** of them. So the README's `fluxc compile -i constraints.guard -o output.bin` **exits 0 and produces no file** — the exact "script that exits 0 and writes nothing" failure.

### 1e. The Pest grammar is a triple orphan

`crates/fluxc-parser/src/guard.pest` is a real, complete 90-line PEG grammar. It is referenced from exactly one place: `benches/bench_parser.rs`. That file:
- sits at the **repo root** where `Cargo.toml` is a virtual manifest with **no `[package]`** — so `benches/` belongs to no crate and cargo ignores it entirely;
- references `super::guard_support::Rule` — a module that **never existed** (only `parser_support` is defined);
- needs `pest` and `criterion`, and **`pest` is not in `Cargo.lock`**.

And CI runs `cargo bench --workspace || true` — the `|| true` swallows the failure anyway. The README's "GUARD constraint parser (Pest PEG grammar)" is not built, not compiled, and not tested.

### 1f. CI is green over zero tests

`cargo test --workspace` runs **0 tests**: the only integration-test crate is `fluxc-test/`, at the top level, orphaned. The Python suite (`tests/test_compiler.py`, 508 lines) is never run — CI is cargo-only.

The gate history is in the git log:
```
0ec7b7b 2026-05-25 fix: relax clippy (don't deny warnings)
-        run: cargo clippy --workspace --all-features -- -D warnings
+        run: cargo clippy --workspace --all-features
```
The step is **still named "Clippy (warnings as errors)"** while the command no longer denies warnings. And:
```
a97fc8b 2026-05-29 docs: rewrite README following standard template
```
The README that advertises the compiler was written *after* the code, from a template. Its feature list describes the intended toolchain, not this repo. (Checked: the "Pest PEG grammar" / "Multi-target codegen" template text appears in **1** of 64 sampled repos — this is not fleet-wide boilerplate, it is this repo's own template.)

### 1g. The one tested implementation has a real bug the 59 tests dodge

The Python port is genuinely real: 1,223 lines across lexer/parser/ir/optimizer/codegen, **59/59 tests pass** (executed — see method). But:

`flux_compiler/parser.py:202`:
```python
left = self._parse_unary()
while self._check(TokenKind.AND) or self._check(TokenKind.OR):   # no precedence
    combinator = self._advance()
    right = self._parse_unary()
    ...
```
AND and OR sit at the **same precedence, left-associative**. The crate's own orphaned Rust reference does it properly — `parse_or()` → `parse_and()` → `parse_not()` → `parse_primary()`.

Executed, the two disagree:
```
a IN 0..10 OR b IN 0..10 AND c IN 0..10
   Python (live, tested)  -> ((aIN[0..10] O bIN[0..10]) A cIN[0..10])
   Rust   (orphan ref)    ->  aIN[0..10] O (bIN[0..10] A cIN[0..10])
```
**Every unparenthesized `A OR B AND C` guard is parsed the wrong way round.**

And the 59-test suite never catches it, for a structural reason: the only two tests that mix the operators **both parenthesize explicitly** —
```python
_parse("(x IN 0..10 OR x IN 90..100) AND y == 5")
"(x IN 0..100 AND y == 42) OR NOT z == 0"
```
The suite sidesteps the one input class that exposes the defect. (Note the direction: the Python parse is *stricter* than the reference, so a guard written `privileged OR (certified AND in_scope)` is enforced as `(privileged OR certified) AND in_scope` — `privileged` requests lacking `in_scope` are rejected.)

**Why another agent should care.** FLUX is the fleet's constraint language and constraint verification is load-bearing for the cell doctrine. The only thing that "compiles" it is a printer; the only thing that is *tested* is a Python port that mis-parses the language it implements; and the one artifact that actually works (the orphaned Rust family) is invisible to the build system. Anyone adopting this repo would inherit a README describing a toolchain that does not exist.

---

## 2. `plato-vessel-core` — the vessel that cannot reach its own server

**What it is.** "The bare-metal C client that turns any IoT device into a PLATO room" — a zero-dependency C library for ESP32/RP2040, a Python room server, and three educational chapters. This is the best *integrated* repo in the unexamined set.

**Verified working (executed):**
- Python suite: **15/15** class-based tests + **75/75** self-reported integration tests (live HTTP server, WAL crash recovery, Lamport clocks, tile retraction/supersede, gate rejection paths) — **90 total, all green, idempotent** (75/75 on two consecutive runs).
- C client compiles **clean** under `gcc -Wall -Wextra` (zero warnings).
- Mutation-verified: making the server accept a duplicate tile → **RED** (73/75, 2 failures). The suite can fail.

### 2a. Three of the four CI jobs cannot fail

```yaml
- name: Check ESP-IDF compiles
  run: |
    echo "ESP32 build requires IDF SDK — run locally with idf.py"
    echo "See examples/esp32_sensor_node.c for instructions"

- name: Check Pico SDK compiles
  run: |
    echo "RP2040 build requires Pico SDK — run locally with cmake"
    echo "See examples/rp2040_led_node.c for instructions"

- name: Compile and run unit tests
  run: |
    gcc -Wall -Wextra -o test_json plato_client.c -DTEST_MODE 2>/dev/null || \
    echo "Unit test build requires test harness — run locally"
```
The two "build" jobs build nothing. The "unit test" job:
- `TEST_MODE` appears **only in the YAML** — `plato_client.c` has no `main()` and no `TEST_MODE` handling anywhere in the repo;
- the link **fails**: `undefined reference to 'main'`;
- `2>/dev/null` hides the error, and `|| echo` converts the failure into a **green step**.

So the C library — the actual product of this repo — has **zero executed tests**, while the Python half (which is the bigger half) is well tested.

### 2b. The Turbo-Shell is a README table with no implementation

The README headline is "**Don the Turbo-Shell** — agents send 'intelligence' that upgrades device capability level 0→4", with a five-row table (Raw / Conditioned / Smart / Autonomous / Ensign) and the claim that "the device stores it as behavior, registers new tools, and upgrades its level."

```
grep -in "capability|level|intelligence|shell" plato_client.c plato_client.h
  (zero matches)
```
The C API is six functions: `plato_init`, `plato_destroy`, `plato_publish`, `plato_fetch`, `plato_poll`, `plato_json_find_string`. There is no capability level anywhere in the device code.

### 2c. The C client and the Python server have never been run against each other

I wrote a C driver, compiled it against the real `plato_client.c`, started the real server, and ran it. Three interlocking failures, none of which either test suite can see:

**(i) They disagree about what a room is.** The C client sends `"room":"<device_id>"`. The server **ignores that field** and derives the room from the domain:
```python
room_name = tile.get("domain", "general").lower().replace(" ", "_")
```
Observed:
```
POST /submit {"room":"c-device","domain":"sensors",...}
  -> {"status":"accepted","room":"sensors","tile_hash":"cf6a78bc718743cd","lamport":1}
GET /rooms          -> {"sensors": {"tile_count": 1, ...}}
GET /room/c-device  -> {"error": "Room not found"}     <-- what plato_fetch() asks for
GET /room/c-device/commands -> {"error": "Room not found"}  <-- what plato_poll() asks for
```
A device publishes into room `sensors` and then polls room `c-device/commands`. It can never read back what it published, and never receives a command. The tile's stored `"room"` field still says `c-device`, so the data is *in* the server under a name the device does not use.

**(ii) The C client never parses the HTTP status line.** `plato_client.c` builds requests with `"HTTP/1.1"` but never extracts a status code. A rejection is indistinguishable from an acceptance:
```
HTTP/1.0 403 Forbidden
{ "status": "rejected", "reason": "Answer too short (1 < 20)", "room": "sensors", "gate": "P0" }
```
and the C driver printed `plato_publish -> 0` (**PLATO_OK**) for that 403.

**(iii) The server's answer-length gate measures the wrong thing for the client's payloads.** `ans_len = len(tile["answer"])` — for a JSON-object answer that is the **key count**, not a length. A C device sending the natural sensor payload `{"celsius": 23.5}` is always rejected as "Answer too short (1 < 20)". The Python tests only ever submit **string** answers, so this path is never exercised.

**Why another agent should care.** This repo is the fleet's embedded path — "any IoT device becomes a PLATO room." The seam between its two halves is broken in three ways, and CI is structurally incapable of finding any of them: the C side has no working test job, and the Python side is tested only against itself. A repo can have a clean-compiling C library, a 90-test green suite, and still not work.

### 2d. Duplicate file

`server/plato-room-server.py` and `server/plato_room_server.py` are **byte-identical**, 608 lines each, both tracked.

---

## 3. `persistent-sheaf-rs` — the topology that reports the wrong holes

**What it is.** ~2,700 lines of real mathematics across 8 modules: simplicial complexes with boundary maps, filtrations, cellular sheaves with restriction maps, sheaf Laplacian, Hodge Laplacian with harmonic sections, pushforward functors, persistence diagrams, and a spatial-analysis layer for room connectivity. A `CAPABILITY.toml` declares the fleet's integration contract. The README places it in the "sunset-ecosystem" and says `conservation-law` uses it to "enforce that topological invariants are preserved under fleet reconfiguration" and `si-fleet-api` "uses Betti numbers to detect when the fleet's connectivity topology has changed."

**This is a high-quality repo with three silent mathematical defects, all in the headline functions, none of them tested.**

### 3a. `betti_numbers()` mis-computes β₁

```rust
let beta2 = self.num_simplices(2).saturating_sub(self.num_simplices(3)); // count of TRIANGLES
let beta1 = (beta0 as i32 - chi - beta2 as i32).max(0) as usize;
```
Two problems: β₂ is taken as the **number of triangles** rather than the rank of the cycle space, and the sign is wrong (χ = β₀ − β₁ + β₂ ⇒ β₁ = β₀ + β₂ − χ). The `.max(0)` then hides the error by clamping.

No Rust toolchain in the sandbox, so I ported the algorithm to Python **verbatim** and compared against an **independent** ground truth: GF(2) rank of the actual boundary matrices ∂₁ and ∂₂.

```
complexes checked: 3,600    MISMATCHES: 28
  eps=1.0771  V=7 E=8 F=2   crate beta=[2, 0]   truth=(2, 1)
  eps=1.4030  V=5 E=6 F=1   crate beta=[1, 0]   truth=(1, 1)
  eps=1.9408  V=6 E=9 F=3   crate beta=[1, 0]   truth=(1, 1)
```
**Every mismatch reports β₁ = 0 where the truth is β₁ = 1** — the error is always in the direction of under-reporting, so it can never raise an alarm.

### 3b. `compute_persistence()` produces a wrong diagram

H1 deaths are recorded with the birth **hardcoded to 0.0**, and the birth pair is never retracted. On the crate's **own** H1 example (the square from `test_h1_betti_integration`):
```
filtration:  eps=1.1314  V=4 E=4 F=0  beta1=1     <- the cycle is born
              eps=1.4142  V=4 E=6 F=4  beta1=0     <- the cycle is filled

crate's diagram:  (1.1314, inf, 1)      <- claims the cycle NEVER dies
                  (0.0000, 1.4142, 1)    <- claims it was born at 0.0
ground truth:     (1.1314, 1.4142)      persistence = 0.2828
```
`total_persistence` is therefore **∞**. A single poisoned aggregate. (The H0 path hardcodes birth 0.0 too, but in a Vietoris–Rips filtration every vertex exists at ε=0, so all H0 features genuinely are born at 0.0 — that one is latent-harmless. The H1 path is not.)

### 3c. `bottleneck_distance()` is not the bottleneck distance

The README states the correct definition: `d_B(D_1,D_2) = inf_{matchings φ} sup_{p∈D_1} ||p − φ(p)||_∞`.

The code computes:
```
max( max_{p1∈D1} min_{p2∈D2} d(p1,p2),  max_{p2∈D2} min_{p1∈D1} d(p1,p2) )
```
— a max-of-nearest-neighbours measure. It is **many-to-one** (no injectivity), and **the diagonal is never considered**, which the true definition's infimum over bijections onto D₂ ∪ diag explicitly allows.

Measured against the true bottleneck (injective matching, closest-point-on-diagonal cost `(d−b)/2`):

| D₁ | D₂ | crate | **true** | |
|---|---|---|---|---|
| `{(0,1)}` | `{(50,51)}` | 50.0 | **0.5** | 100× over |
| `{(0,1)}` | `{(0,1),(90,99)}` | 98.0 | **4.5** | 22× over |
| `{(0,0)}` | `{(100,100)}` | 100.0 | **0.0** | infinite over |

`CAPABILITY.toml` also advertises `BottleneckDistance::compute(diagram_a, diagram_b)` in its onboarding API surface. `BottleneckDistance` is `pub type BottleneckDistance = f64;` and **no such function exists anywhere in the crate**.

### 3d. The untested surface

21 tests. Mentions in `tests/integration.rs`:

| headline function | mentions in tests |
|---|---|
| `compute_persistence` | **0** |
| `betti_numbers` | **0** |
| `wasserstein_distance` | **0** |
| `bottleneck_distance` | 2 (both on hand-built `PersistencePair`s) |

The tests that exist cover simplicial-complex counts, Euler characteristic, β₀, and hand-constructed pair structs. **The three functions the crate exists to provide are not exercised.**

**Why another agent should care.** This is the substrate for fleet topology monitoring. A β₁ that silently reports 0 for any complex containing a triangle **cannot detect a cycle appearing** — the fleet's "has the connectivity topology changed?" check returns "no change" exactly when the anomaly occurs. The failure mode is silence, not a crash.

---

## 4. `image-distillation-loop` — a real gem (and a hardcoded home directory)

**What it is.** A self-improving image pipeline: FLUX/DeepInfra teacher → SD-Turbo student → llava/Qwen3-VL scorer on 5 dimensions → DeepSeek feedback → a "reflex compiler" that turns successful prompt improvements into reusable JSON reflexes applied to later prompts in the same niche.

**Verified working (executed).** 1,373 lines of source + 8 test files. **87/87 tests pass** (executed under a purpose-built pytest shim — no PyPI in the sandbox). Real API integration, not mocks around nothing: a DeepInfra client with fallback-model handling, base64 decode, per-niche prompt enhancers, dual ollama/DeepInfra scorer.

**Mutation-verified, 5/5 sharp mutations RED:**

| mutation | result |
|---|---|
| reflex improvement threshold 0.3 → 0.0 | 85 pass / **2 fail** |
| `Scorer.average()` returns a constant | 86 / **1 fail** |
| `negative_additions` no longer applied | 82 / **5 fail** |
| teacher's whole enhancer dict replaced | 85 / **2 fail** |
| teacher returns the raw prompt | 85 / **2 fail** |

This is the best-gated Python in the unexamined set. It is the positive control other repos should copy.

**Defects.**
- `scorer.py:64` — `ollama_path: str = "/home/eileen/.local/bin/ollama"` is the **default**. `subprocess.run([self.ollama_path, ...])` is not wrapped, so on every machine but one the default scoring path raises an **uncaught `FileNotFoundError`** (the `result.returncode == 0` check is dead code for a missing binary). The default configuration cannot work off that machine, and it carries a third party's home directory into a public repo.
- `.coverage` (53 KB) is **committed** and not in `.gitignore`. It is a SQLite coverage database and it contains the author's absolute paths: `/home/eileen/projects/image-distillation-loop/tests/...`.
- Two CI workflows (`ci.yml`, `tests.yml`) duplicate the same pytest job; the second adds `pip install -e ".[dev]" 2>/dev/null || true`, swallowing install failure.

**Why another agent should care.** It is the fleet's clearest working instance of "an agent compiles its own reflexes" — and it is the repo whose CI shape the rest of the fleet should copy. Its two defects are both *portability leaks* of one person's machine, which is exactly the kind of thing that survives in a fleet because nobody runs the code on a second machine.

---

## 5. The `lau-*` manufacturing run — 252 repos, one template

**Fleet-scale finding.** 252 unexamined non-fork repos share the `lau-` prefix — **4.5% of the entire fleet, never looked at by anyone.** They are not 252 implementations.

**Each `lau-X` is an existing crate plus exactly one `agent_*.rs` module.** Verified byte-level twins (shallow clones, local hashing):

| pair | shared files | byte-identical | unique to either |
|---|---|---|---|
| `lau-convex-optimization` ↔ `convex-rs` | 11 | **9/11** | 0 |
| `lau-optimization` ↔ `optimization-algorithms` | 12 | **10/12** | 0 |
| `lau-reinforcement-learning` ↔ `rl-rs` | 11 | **10/11** | 0 |
| `lau-fluid-dynamics` ↔ `cfd-rs` | 9 src + 1 test | — | `lau-` adds `src/agent_flow.rs` + 4 tests |

44 of the 252 have a same-name base repo in the fleet.

**The agent module is a relabeling.** `lau-fluid-dynamics/src/agent_flow.rs` (211 lines) is a wrapper that feeds agent vocabulary into the base crate's solvers:
```rust
let viscosity = params.interaction_strength;
let flow = NavierStokes2D::new(grid_size, grid_size, viscosity, domain, domain);
let reynolds_number = params.agent_speed * params.domain_size / viscosity;
```
The Navier–Stokes solver is untouched. `agent_count → density`, `agent_speed → velocity`, `interaction_strength → viscosity`. The *delta* between 240 repos is a rename layer.

**CI is one file copied 252 times** — checkout, `dtolnay/rust-toolchain@stable`, `cargo check`, `cargo test`, `cargo clippy -- -D warnings`. No `fmt`, no `--locked`, unpinned toolchain.

**A 64-repo clone sample (all unexamined):**

| | |
|---|---|
| containing the fleet canary `0x024a555471370b18d` | **0 / 64** |
| with **zero** test files | **35 / 64** (21 of the 29 `lau-*` in the sample) |
| with ≥1 CI workflow | 60 / 64 |
| missing `.gitignore` | 4 / 64 |

**Why another agent should care.** This is what fleet-scale activity looks like when nobody checks the denominator. 252 repos × ~1 boilerplate CI file each, no canary, and most with no tests at all, is not 252 independent pieces of work — it is one template instantiated 252 times. Anyone measuring fleet capability by counting repos, badges, or "implementations" will over-count by two orders of magnitude here. **The canary count of 0/64 is the tell: a real fleet artifact carries the canary.**

---

## 6. Negative findings (reported as findings)

- **`spectral-shape`** — README is the fleet "Related Fleet Repos" marketing template with **no content about what it does**. Quick Start is `git clone` + `cd`. The only description is one line: "Spectral methods for shape analysis of agent behavior distributions." Zero test files, one boilerplate CI. It advertises a capability and documents nothing.
- **`flux-compiler-workspace`** — README describes a compiler that does not compile.
- **`plato-vessel-core`** — README documents a 5-level capability ladder that does not exist in the device code.
- **`persistent-sheaf-rs`** — README states the correct bottleneck-distance definition; the code implements a different function.
- **The `lau-*` set** — 252 READMEs describing agent dynamics that are relabeled base crates.

Four different repos, four different ways of describing a capability that the code does not have. That is the pattern worth naming.

---

## 7. Method notes (carry forward)

1. **Rank on code bytes by extension, minus vendored paths — not tree bytes, not API `size`.** API `size` is git *history*; tree bytes are dominated by mp3/pdf/zip. The `.py`/`.rs`-bytes pass is what surfaced `flux-compiler-workspace` and `persistent-sheaf-rs` at all.
2. **The unexamined tail is small repos.** 0 of the 2,820 unexamined non-fork repos have API size > 100 KB — every large repo is already examined. Do not expect the remaining budget to hide anything big; expect manufacturing runs and template repos.
3. **A repo can be clean, green, and broken at the seam.** `plato-vessel-core` has a clean-compiling C library and a 90-test green suite and still cannot publish to a room it can read. Run the two halves against each other. Neither suite could have found it.
4. **Look for the shadowed copy.** In `flux-compiler-workspace` the *real* implementation sat in eight top-level directories that `members = ["crates/*"]` excluded from the build, while the built one was stubs. `git ls-files` at the repo root and a look for a second copy of the same crate names is cheap and finds it.
5. **Look for the step that cannot fail.** `echo "… requires SDK — run locally"` in a step named "Check … compiles"; `|| echo` after a compile; a `-- -D warnings` removed while the step name keeps the promise. `grep -n "|| true\||| echo\|2>/dev/null" .github/workflows/*` is a 10-second check.
6. **Look for a gate whose flag exists only in the YAML.** `-DTEST_MODE` in CI, no `TEST_MODE` in the source. Same shape as `-D` feature flags in Cargo.toml that no code reads.
7. **A test suite that passes can still be dodging the defect.** `flux-compiler-workspace`'s Python suite mixes AND and OR in exactly two tests — **both parenthesized**. Read what the tests *avoid*, not only what they assert.
8. **No cargo in the sandbox: port the algorithm, compare against an independent ground truth.** Do not claim execution of Rust. A faithful Python port plus a GF(2) boundary-rank reference found a 28/3,600 β₁ defect that reading alone would not have quantified.
9. **No PyPI in the sandbox: write a ~60-line pytest shim** (`raises`, `approx`, `fixture`, `mark`) plus a collector with `capsys` / `tmp_path` support. That recovered 87/87 and 15/15 suites that would otherwise have been unreportable.
10. **`pkill -f <pattern>` can match your own wrapper shell** (self-match; this bit me twice across sessions). Target by PID, or use a pattern that cannot appear in the command you are running.
11. **Restore mutated files with `git checkout HEAD -- <file>`, never with a captured buffer.** A Python `open(f,'w').write(orig)` with a bytes/str mismatch truncated two 608-line files to 0 bytes and manufactured a "test failure" that looked like a repo defect. **A failure that appears only after your own mutation is your bug until proven otherwise.**
12. **A fixed-port test server leaves state and stale processes behind.** `test_plato_v3.py` binds 8847; running it twice concurrently, or after a killed run, yields a phantom 2-test failure from a stale server. Run it alone and it is 75/75 twice — the suite *is* idempotent; do not report the artifact.
13. **Check the actual protocol seam, not just the unit boundaries.** Three of the `plato-vessel-core` defects (room-name split, unchecked HTTP status, `len(dict)` length gate) exist only in the interaction between two components that each pass their own tests.

---

## 8. Environment

- Sandbox `/workspace` NAS at 100% (EDQUOT) — all durable copies went to git; `/tmp` overlay (28 GB free) used for working files.
- TLS clean on first try; no cert-anchor wall, no bundle rebuild. `gh` absent. REST API rate limit exhausted around 22:37Z (≈2,850 of 5,000 hourly calls spent on the census + 2,786 tree fetches). **`git clone`/`git fetch` are not rate-limited** — for surveying, clone-and-hash locally is far cheaper than the REST tree API.
- `cargo`/`rustc` absent; `gcc` 12 present; `node` 22 and `python3` 3.11 present; no PyPI.

**Files examined this round:** 64 unexamined repos cloned and hashed locally; 3,556 unexamined basenames diffed against all 139 prior scout files; 2,786 unexamined non-fork trees fetched for substance ranking.
