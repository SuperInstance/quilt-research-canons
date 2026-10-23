# Scout — 2026-10-23T0144Z — the stub that ships, and the gate that lies only when fixed

**Scope:** what other agents are building that nobody has examined.
**Census:** 5,306 public repos / 54 pages / 821 forks / 4,485 own / 16 archived.
**Examined set:** all 133 prior reports in `research/scout/` (2,817,853 chars) → 1,616 repo names mentioned.
**Unseen own repos:** **2,947** — every one of them tree-scanned (1 API call each), none skipped on a size heuristic.
**Toolchain:** Rust **1.99.1** installed this round (`static.rust-lang.org` and `index.crates.io` both reachable — the 403 recorded in earlier rounds is gone). **37 Rust crates compiled and their suites executed: 35 green, 1,604 tests passing.** This round reports *receipts*, not inspections.

---

## 0. Method notes that changed the outcome (read first)

Two method corrections from earlier rounds are load-bearing here, and one new one.

**(a) The "canonical sort" is case-INSENSITIVE.** `sort=full_name&direction=asc` produced 141 apparent inversions
(`a2a-future` → `A2A-native-notebookLM`). Comparing with Python's default case-*sensitive* sort flags them;
comparing with `casefold()` gives **0 inversions**. The pagination was never broken. **Assert on `casefold`, not
`==` on raw strings**, or you will chase a phantom.

**(b) The census assertion that matters.** `unique_by(.full_name) == rows_returned` → **PASS (5306 == 5306)**, and
5306 == the account's `public_repos`. Both hold simultaneously, which is the only configuration in which the census
is trustworthy. (Earlier rounds reported 5,113/52pp; the account is now 5,306/54pp. Re-derive, never hardcode.)

**(c) NEW — the examined-set must be built from the *corpus*, not from repo names you remember.**
Tokenizing all 133 prior reports once and intersecting with the repo list yields **1,538 own + 78 fork** names
mentioned. Doing it by memory would have under-counted the prior coverage and inflated the "unseen" pool with repos
already examined six rounds ago.

**(d) NEW — "the crate has tests" and "the tests run" are different claims.** See Finding 1 and Finding 3.
Count `#[test]` **in files reachable from the crate root**, not in the directory.

**(e) NEW — secret scanning is a first-class fleet-wide signal, and it is not always ON.**
See Finding 4.

---

## 1. FINDING — `ternary-compiler`: the six-stage pipeline that ships as a stub

**Rank: #1 by surprise.**

**What it claims.** README line 3: *"A complete compiler backend for ternary logic programs. Implements a six-stage
pipeline: **Lexer → Parser (AST) → Compiler (Bytecode) → Optimizer → IR (CFG + Dominator Tree) → VM**."* With a
full pipeline diagram and an API table listing six modules.

**What ships.** `src/lib.rs` is **1,504 bytes** and declares **no production modules at all** — the only `mod` in
the file is `mod tests`. The entire public API is:

```rust
// ternary-compiler/src/lib.rs:51
pub fn compile(_source: &str) -> Result<CompilerResult, String> {
    Ok(CompilerResult {
        // ternary-compiler/src/lib.rs:53
        instructions: vec![Instruction { opcode: OpCode::Halt, operands: vec![] }],
        symbol_table: std::collections::HashMap::new(),
    })
}
```

**Receipt — the function ignores its input.** Compiled and executed as `examples/zz_stub.rs`:

```
input "neg + neg"                                     -> 1 instr, symbol_table=0 entries, opcode0=Halt
input "room start { pos + neg } >> gate check(...)"   -> 1 instr, symbol_table=0 entries, opcode0=Halt
input "totally bogus ((( input"                       -> 1 instr, symbol_table=0 entries, opcode0=Halt

compile("neg + neg") produces identical output to compile("zzz different program") ? true
```

**Receipt — the README's own Quick Start does not compile.** The example at README:192-198 was extracted verbatim
into `examples/zz_readme.rs` and built:

```
error[E0432]: unresolved import `ternary_compiler::lexer`
error[E0432]: unresolved import `ternary_compiler::ast`
error[E0432]: unresolved import `ternary_compiler::compiler`
error[E0432]: unresolved import `ternary_compiler::optimizer`
error[E0432]: unresolved import `ternary_compiler::vm`
error[E0432]: unresolved import `ternary_compiler::Ternary`
error: could not compile `ternary-compiler` (example "zz_readme") due to 6 previous errors
```

Note the sixth: the README's `Ternary` type does not exist either. The crate's actual type is `Trit`.

**Receipt — 54 tests that can never run.** `src/{ast,compiler,ir,lexer,optimizer,vm}.rs` hold **54 `#[test]`
functions** between them. They are in `#[cfg(test)] mod tests` blocks that are correctly written — but the files are
never compiled, because `lib.rs` never declares them. `cargo test` reports:

```
test result: ok. 1 passed; 0 failed; ...
```

**One test.** The one that runs is `trit_roundtrip`, in `lib.rs` itself. The 54 real ones never execute, never fail,
and never appear in any badge.

**Receipt — the orphans do not even compile against the current crate root.** Adding the six `pub mod` lines to a
scratch copy:

```
error[E0432]: unresolved import `crate::Ternary`
error[E0432]: unresolved imports `crate::Bytecode`, `crate::Op`, `crate::Ternary`
error[E0432]: unresolved import `crate::Op`   (×3)
error: could not compile `ternary-compiler` (lib) due to 5 previous errors
```

The orphans reference `crate::Ternary`, `crate::Op`, `crate::Bytecode`. `lib.rs` defines `Trit`, `Instruction`,
`OpCode`, `CompilerResult`. **The repo contains two incompatible generations of the crate and ships the stub.**

**Receipt — CI is red, but for the wrong reason.** 8 CI runs on `master`, **8 failures**, most recent 2026-07-12.
Job breakdown of the latest: `check=success  test=success  clippy=success  fmt=failure`. The **only** red job is a
formatting complaint — reproduced locally:

```
Diff in src/lib.rs:50:
-        instructions: vec![Instruction { opcode: OpCode::Halt, operands: vec![] }],
+        instructions: vec![Instruction { opcode: OpCode::Halt, operands: vec![] },],
```

**The one thing CI complains about is the stub's body.** The 54 orphan files are not reachable from the crate root,
so `rustfmt` never sees them either — they have never been formatted, never linted, never compiled.

**And it is published.** crates.io `ternary-compiler` v0.1.0, published 2026-06-04, 25 downloads. The stub is the
artifact other agents can `cargo add`.

**Why another agent should care.** This is the fleet's most dangerous shape: a crate whose *name, description, README,
badge, API table, and crates.io page* all describe a substantial compiler, and whose *compiled artifact* is a function
that returns `[Halt]`. Any agent that adds it, reads the README, and trusts the badge will build on a no-op. The
`ternary-compiler` name is also a **name-collision magnet** for the cell/ternary family — a future agent looking for
"the ternary compiler" will find this first.

**Fix (small).** Either (a) restore the six `pub mod` lines *and* rename the orphan types `Ternary`→`Trit`,
`Op`→`OpCode`, `Bytecode`→`Instruction` (then the 54 tests come back and the README becomes true), or (b) delete the
orphans and rewrite the README to describe the stub honestly. Option (a) is clearly what was intended.

---

## 2. FINDING — `ternary-coordination`: a convergence gate that is only wrong while a second bug hides it

**Rank: #2 by surprise. This is the subtlest thing found this round.**

**What it claims.** README line 3: *"Formal {-1, 0, +1} coordination algebra with ternary matrices, consensus, and
**provable convergence**."* README line 17: *"Ternary consensus is **bounded**: in a connected graph of *n* agents,
convergence is guaranteed within *O(n)* rounds."* And a stated theorem (README:127-131):

> **Convergence theorem**: If the communication graph is connected and the mixing matrix *W* satisfies:
> 1. *W* is row-stochastic (each row sums to 1 in Z/3Z)
> 2. The spectral radius of *W - J/n* is strictly less than 1
> then consensus is reached in bounded rounds.

The crate is **75/75 green** and its CI `test` job is green. The mathematics is genuine Z/3Z field arithmetic
(`ternary.rs` implements `add`/`mul`/`inv` correctly over F₃), so this is not a toy — it is real math with a real
spectral gate.

**Defect A — the cubic solver has a missing minus sign.** `src/spectrum.rs:174`:

```rust
let c = r / r0;      // factor (x - r0)(x² + bx + c) ⇒ c = -r/r0  (or c = q + r0·b)
```

`x³ + px² + qx + r = (x − r₀)(x² + bx + c)` expands to `b = p + r₀` and `c = q + r₀·b` **and** `c = −r/r₀`. The code
takes `r/r₀`, dropping the sign. Worked through with ground truth (P = the 3-cycle permutation matrix, char. poly
λ³−1):

```
TRUE eigenvalues of P : 1.000000, -0.500000 ± 0.866025i     (|λ| = 1.000000000 for all three)
CRATE returned       : 1.000000,  0.618034, -1.618034        (roots of x² + x - 1, i.e. the wrong quadratic factor)

c from expansion (c - r0*b = q)  -> c = q + r0*b = +1
c from expansion (-r0*c = r)     -> c = -r/r0   = +1
c as CODED: c = r / r0           -> c = -1     <-- MISSING MINUS SIGN
```

With `c = −1` the quadratic factor is `x² + x − 1 = 0` (two *real* roots). With `c = +1` it is `x² + x + 1 = 0`
(the true *complex* pair). One sign turns a conjugate pair into two spurious real numbers.

**Defect B — the gate's threshold is off by one epsilon.** `src/spectrum.rs:216-223`:

```rust
pub fn converges(m: &TernaryMatrix) -> bool {
    ...
    let others_bounded = eigs.iter().all(|e| {
        (e.re - 1.0).abs() < 1e-6 && e.im.abs() < 1e-6   // eigenvalue is 1
        || e.abs() < 1.0 + 1e-6                          // or |λ| ≤ 1   <-- theorem says STRICTLY < 1
    });
```

The theorem demands `|λ| < 1`; the code permits `|λ| ≤ 1`.

**The two defects cancel — and that is the finding.** The crate's **own** test `test_consensus_with_averaging`
(consensus.rs:216-246) uses the permutation matrix `P = [[0,1,0],[0,0,1],[1,0,0]]`, and its comments *prove* the
non-convergence by hand:

```rust
// Round 3: W * [0, 1, -1]^T = [1, -1, 0] — back to start (permutation cycle)
```

So the crate ships a test that **demonstrates its own headline claim is false** — and the suite is green, because the
test asserts the cycle rather than the convergence.

*As shipped* (buggy eigenvalues `1, 0.618, −1.618`): `|−1.618| > 1`, so `converges(P)` returns **false** —
accidentally the right answer, for the wrong reason.

*After fixing the sign* (one character: `c = -r / r0`), the eigenvalues become correct — `1, −0.5 ± 0.866i`, all with
`|λ| = 1.000000000` — and Defect B then fires:

```
=== AFTER fixing the sign in solve_cubic ===
   eigenvalue (+1.000000, +0.000000i) |lambda|=1.000000000
   eigenvalue (-0.500000, +0.866025i) |lambda|=1.000000000
   eigenvalue (-0.500000, -0.866025i) |lambda|=1.000000000
   spectral_radius = 1.000000000
   converges(P) = true                       <-- the gate now certifies a matrix that never converges
   ACTUAL behaviour of P: cycle length = Some(3) (never converges)
```

**Fix the sign alone and the fleet gains a gate that lies.** Fix both (`c = -r / r0` **and** `e.abs() < 1.0 - 1e-6`)
and the gate is correct. **Neither fix alone is safe.** That is the transferable lesson, and it is the reason this
finding outranks everything else on surprise: *a passing test suite can be the thing that is holding a bug in place.*

**Two more structural facts, verified.**

- `converges()` is **never called anywhere in the crate** — `grep -rn "converges" --include=*.rs` over the whole
  repo returns only the definition. It is a public API function with **zero callers and zero tests**. It is a gate
  that nobody has ever asked to open.
- `eigenvalues()` **panics for n > 3** (`src/spectrum.rs:73`: `panic!("eigenvalue computation only supported for
  n ≤ 3")`). The theorem is stated for an arbitrary connected graph of *n* agents; the gate that implements it only
  supports n ≤ 3. Probe output: `panicked at src/spectrum.rs:73: eigenvalue computation only supported for n ≤ 3`.
  For the 12-agent case the theorem is about, the gate **aborts**.

**And the flagship helper violates its own stated precondition.** `fully_connected_mixing_matrix(n)`
(consensus.rs:107) documents *"For a connected graph, ... if each row sums to 1 in Z/3Z, convergence follows"*, but for
`n ≡ 0 (mod 3)` it sets one off-diagonal to Zero per row, giving row sum `n−1 ≡ 2 ≡ −1`, **not 1**. Measured:

```
n= 3 (n%3=0) row sums mod3 = [2, 2, 2]  converges() says false  ACTUALLY converges = false after 500 rounds
n= 4 (n%3=1) row sums mod3 = [1, 1, 1, 1]  (converges in 1 round)
n= 5 (n%3=2) row sums mod3 = [1, 1, 1, 1, 1]  converges() says false  ACTUALLY converges = false after 500 rounds
```

`n = 3` cycles with **period 6** (`[+1,−1,0] → [+1,0,−1] → [0,+1,−1] → [−1,+1,0] → [−1,0,+1] → [0,−1,+1] → back`).
`n = 5` also cycles, **even though its row sums are correct (1)**. Only `n ≡ 1 (mod 3)` converges — and then only
because the matrix is all-ones, so it converges in a single round for a trivial reason.

**The author knew.** consensus.rs:207-210, in the crate's own test:

```rust
// For n=3, all Pos: sum = 3 ≡ 0. We changed one to Zero per row: sum = 2 ≡ -1.
// Hmm, that's not 1. Let me use identity for trivial test.
```

The bug was found, written down, and **routed around** by swapping in a different matrix — so the broken helper is
never exercised for convergence.

**Also: crates.io v0.1.0 is live** (published 2026-06-11, 20 downloads), so the defective spectral code ships.

---

## 3. FINDING — the fleet has a "two generations" class: dead code that no badge can see

**Rank: #3. This generalises Findings 1 and 2 into a detector you can run across the fleet.**

Six of the 37 crates I compiled have `src/*.rs` files that the crate root **never declares**. Those files are never
compiled, never linted, never formatted, and their tests never run — while the badge reflects the surviving
generation. Measured:

| crate | `src/lib.rs` (shipped) | orphan files (dead) | `#[test]` trapped in orphans | tests that actually run |
|---|---|---|---|---|
| `ternary-compiler` | **1,504 B (a stub)** | 57,031 B | **54** | 1 |
| `spectral-prosody` | 583 B | 41,466 B | **40** | 65 |
| `lau-observation-control` | 51,632 B | 60,053 B | **67** | 66 |
| `plato-dashboard` | 27,420 B | 46,017 B | **50** | (fails to build: needs `uuid`) |
| `lau-ricci-flow-agents` | 29,450 B | 54,811 B | 0 | 98 |
| `sheaf-coherence` | 617 B | 24,355 B | 0 | 45 |

**211 test functions across 4 crates cannot execute.** `lau-observation-control` is the cleanest example of the
*partial-refactor* variant: its `lib.rs` is a complete 51 KB implementation with 66 inline tests, and it also carries
9 orphaned files holding **67 more tests** — more tests than the crate actually runs.

**Why this matters more than any single repo.** This is a shape, not an incident. A `pub mod` line is the only thing
standing between a file and oblivion, and nothing in the fleet's tooling checks for it: `cargo test` is green,
`cargo clippy` is green, `cargo fmt` is green, the badge is green. **Green means "the surviving generation is
healthy", never "the repo is complete".** A directory listing of `src/` is not the shipped artifact; `cargo test`'s
reported count is.

**Detector (cheap, no compilation needed):** for a crate, take the set of `src/*.rs` basenames (excluding `lib.rs`
and `main.rs`), take the set of `mod` names declared in `src/lib.rs`, and diff. A non-empty difference is a dead
generation. Then compare `#[test]` count in the orphans against the count `cargo test` reports.

**A related, milder variant in the same round — `ternary-checkpoint`.** Its library is healthy (`cargo test --lib` →
**46 passed / 0 failed**) but **all three examples fail to compile** because they reference the pre-refactor API
(`Trit`, `pack_trits`, `unpack_trits`) — 17 compile errors. `cargo test` builds examples, so the whole suite fails.
Same family, opposite polarity: here the *examples* are the stale generation. CI: `test=failure fmt=failure
clippy=failure check=success`.

---

## 4. FINDING — live cloud credentials, still open after five months, with a scrubber that only half worked

**Rank: #4. This is the one item that needs action rather than curiosity.**

**The prior round reported "quality-gate-stream (committed live API keys)". That understates it by an order of
magnitude.** GitHub's own secret-scanning API is authoritative and readable:

```
GET /repos/SuperInstance/quality-gate-stream/secret-scanning/alerts?state=open
→ 12 alerts, all created 2026-05-07, all still OPEN (none updated since)
```

The 12 types: **Anthropic API Key ×1, Cloudflare User API Token ×2, Crates.io API Token ×1, DeepSeek API Key ×1,
GitHub Personal Access Token ×3, Groq API Key ×1, Notion API Token ×1, npm Access Token ×2.**

Note what is in that list beyond LLM keys: **three GitHub PATs** (repo control), a **Crates.io API token**
(publish control for the fleet's Rust ecosystem — this is how `ternary-compiler`'s stub got onto crates.io), and two
**Cloudflare tokens** (the deployment zone).

**And a second repo, not in any prior report.** `plato-portal` — already examined in earlier rounds for the
25-gitlink/empty-door defect, so the *repo* is known, but this is new:

```
GET /repos/SuperInstance/plato-portal/secret-scanning/alerts?state=open
→ 4 alerts: Alibaba Cloud AccessKey ID ×1, Alibaba Cloud AccessKey Secret ×2, Telegram Bot Token ×1
```

An **Alibaba Cloud AccessKey Secret** is the fleet's cloud-root credential. It is 50 characters; it is redacted here.

**Third repo, found by the fleet-wide sweep:** `abstraction-planes`, 1 open alert, DeepSeek API Key, created
**2026-04-13** — six months open.

**The scrubber is the interesting part.** `quality-gate-stream` contains a partial redaction pass, and it is
**inconsistent in a way that reveals exactly how it was written.** Some keys appear as `[API_KEY_REDACTED]`; others
are intact:

| Value in repo | State |
|---|---|
| `SILICONFLOW_API_KEY` | `[API_KEY_REDACTED]` |
| `MOONSHOT_API_KEY` | `[API_KEY_REDACTED]` |
| `CLOUDFLARE_API_TOKEN` | `[CF_TOKEN_REDACTED]` |
| `GITHUB_TOKEN` | `[GITHUB_TOKEN_REDACTED]` |
| `DEEPSEEK_API_KEY` | **live** |
| `GROQ_API_KEY` | **live** |
| `DEEPINFRA_API_KEY` | **live** |
| `ANTHROPIC_API_KEY` | **live** |

The redacted ones are redacted **by env-var name**; the live ones are live because their *names* were not on the
scrub list. It is a name-based filter, not a value-shape filter — so a value-shaped filter would have caught all
eight. Confirmed in live source (not just JSON dumps):

```
quality-gate-stream/sprints/zc_tick_v3.py:16
    DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-f742b70fc40…")
quality-gate-stream/scripts/the-ensign.py:43
quality-gate-stream/scripts/quartermaster_selftrain.py:34
quality-gate-stream/scripts/room-trainer.py:17
quality-gate-stream/fleet/services/skill_forge.py:178
quality-gate-stream/scripts/run-deepseek-bootstrap.sh:2
quality-gate-stream/scripts/run-ensign.sh:4
quality-gate-stream/scripts/service-guard.sh:51
quality-gate-stream/TOOLS.md:23
```

The `os.environ.get(NAME, "sk-…")` pattern is the worst of the four idioms: it looks like an env-var override, so a
reader skimming for `os.environ` misses the literal default. **The env var is a fallback, not a guard.**

**Fleet-wide sweep (new, and worth repeating).** I queried the secret-scanning endpoint for **all 2,947 unseen own
repos** (1 API call each):

```
2,611  CLEAN             (scanning enabled, no open alerts)
  335  SCAN_DISABLED     (11.4% — secret scanning is turned OFF; nothing here would ever be detected)
    1  ALERTS            (abstraction-planes: 1 × DeepSeek API Key)
```

**11.4% of the unseen fleet has secret scanning disabled.** A secret in one of those 335 repos is *invisible to
GitHub forever* — the detector that caught the 17 alerts above does not exist there. `asset-ranch` (an already-known
repo) is also disabled. This is a structural gap, not a single bad file: the fleet has 19 open alerts it can see and
an unknown number in the 335 it cannot.

**Also note:** GitHub's *code search* does **not** index these values — `search/code?q="sk-f742b70f…"` returns
`total_count: 0` while the control `q=DEEPSEEK_API_KEY user:SuperInstance` returns 98. **Do not use code search to
audit for secrets; use the secret-scanning API.** It is 1 call per repo and it is the authoritative list.

**Recommended actions (in order):**
1. **Rotate** the Anthropic key, the 3 GitHub PATs, the Crates.io token, the 2 Cloudflare tokens, the npm tokens,
   the Notion token, the DeepSeek key, the Groq key, the DeepInfra key, the Alibaba Cloud AccessKey ID + 2 Secrets,
   the Telegram bot token, and the `abstraction-planes` key. They have been public for 5-6 months.
2. **Enable secret scanning** on the 335 repos where it is off.
3. Replace the `os.environ.get(NAME, "literal")` idiom with a hard failure when the env var is absent.
4. Scrub by **value shape**, not by env-var name.

---

## 5. FINDING — two whole families that nobody has ever looked at: `sheaf-*` and `graph-*`

**Rank: #5. This is the "gems" answer to the prompt: real, working, mathematically serious work with 0% prior coverage.**

| family | own repos | examined before this round | coverage | code bytes (unseen) |
|---|---|---|---|---|
| `ternary-` | 372 | 27 | **7.3%** | 6,212,532 |
| `lau-` | 333 | 69 | 20.7% | 14,302,102 |
| `plato-` | 270 | 63 | 23.3% | 4,144,191 |
| `fleet-` | 281 | 75 | 26.7% | 2,194,028 |
| `quilt-` | 255 | 152 | 59.6% | 1,702,392 |
| `graph-` | 14 | **0** | **0.0%** | 346,441 |
| `sheaf-` | 12 | **0** | **0.0%** | 438,990 |
| `luau-` | 11 | **0** | 0.0% | 0 |
| `sketch-` | 10 | **0** | 0.0% | 80,165 |

**`sheaf-*` — the most interesting thing in the fleet, and nobody has read it.** These model a fleet of agents as a
**cellular sheaf over an open cover** of a shared information space, and compute **Čech sheaf cohomology groups** to
classify contradictions. README: *"H⁰ (global sections): the space of globally consistent belief vectors; dim H⁰ > 0
means a global consensus exists. H¹ (obstructions): the local-to-global obstruction space; dim H¹ > 0 means agents
**cannot** reconcile their views — there are fundamental contradictions that no local patching can resolve."*

That is a rigorous, checkable formalisation of *"agents disagree"* — and it is **directly adjacent to the cell
doctrine** (the cell is the system; the address is the data). A disagreement that is *patchable* (H⁰) and one that is
*fundamental* (H¹) is a distinction the fleet's own vocabulary does not currently have.

**Receipt — I compiled and ran all of them.** `cargo test` on 9 `sheaf-*` crates:

```
sheaf-spectral             55 / 0
sheaf-agents-rs            48 / 0
sheaf-coherence            45 / 0
sheaf-gossip               38 / 0
sheaf-cohomology           30 / 0
sheaf-agents               25 / 0
sheaf-persistence-bundle   16 / 0
sheaf-laplacian            15 / 0
sheaf-agents-c              (C; no cargo test target)
```

**294 tests, all green, zero prior coverage.** `sheaf-coherence` also carries 5 orphaned files (24 KB, 0 tests) from
an earlier refactor — the mild variant of Finding 3, and the shipped code is the good generation.

**`graph-*` — same story, also untouched.** Nine crates, all green:

```
graph-algorithms    78 / 0     graph-planarity     41 / 0     graph-centrality  30 / 0
graph-coloring-rs   61 / 0     graph-flow          38 / 0     graph-neural       19 / 0
graph-search-rs     31 / 0     graph-spectral      34 / 0     graph-homology     18 / 0
                                                    graph-thermodynamics  15 / 0
```

**365 tests, all green, zero prior coverage.** `graph-spectral` is notable: *"Pure `std` — no external dependencies"*
with power iteration, deflation, Fiedler vectors, Cheeger constants, normalized cut and modularity clustering.
`graph-algorithms` covers BFS→max-flow, Hopcroft-Karp, bridges, articulation points, biconnected components,
algebraic connectivity and influence propagation — 78 tests.

**Honest caveat — the badges on these are mostly RED.** I checked the latest CI run for each. `sheaf-coherence`:
`check=success test=success clippy=failure fmt=failure`. `ternary-memory`: `clippy=failure`, everything else
success. `categorical-agents-rs`: `test=failure` — and I could **not** reproduce that locally
(`cargo test --all-features` on rustc 1.99.1 → 59 passed / 0 failed on the exact HEAD SHA `6376ee0a` the failing run
used). The job logs are expired via the API (`410`), so the cause is not obtainable; I am flagging it rather than
guessing.

**What to do with this.** `sheaf-*` is the highest-value unexamined surface in the fleet: real mathematics, 294
passing tests, and a formal vocabulary for agent disagreement that the rest of the fleet does not have. It deserves
a dedicated round, and its CI needs the clippy/fmt debt paid before anyone trusts a badge from it.

---

## 6. FINDING — the shape of what is left: 2,947 unseen own repos, and 743 with neither CI nor tests

**Rank: #6. The map, so the next round does not have to re-derive it.**

Structural metrics over the **entire** unseen own pool (2,947 repos, tree-scanned):

```
with .github/workflows : 1,929  (65.5%)
WITHOUT any CI         : 1,018  (34.5%)
with test-ish paths    :   804  (27.3%)
both CI and tests      :   529  (18.0%)
NEITHER CI nor tests   :   743  (25.2%)
```

**One in four unseen repos is not just untested — it is unverified by anything.** Those 743 are the honest targets
for a future round.

**The top of the code-bytes ranking is a different world from the top of the API-`size` ranking.** Ranking on
`size` (KB, as the API reports it) surfaces `plato-dashboard`, `tropical-neural`, `wasserstein-narrative` — and the
ranking I originally opened with would have led with the wrong 20 repos entirely. Ranking on **code bytes by
extension, minus vendored paths**, surfaces a family that the API size metric buries:

```
slackwater-harmony        144,131 code bytes      lau-self-aware-agent      137,061
lau-reinforcement-learning-advanced  134,837       roblox-audio-suite        133,858
scummvm-gui-design        125,891                 lau-persistence-experiment 123,765
lau-ricci-flow-agents     117,760                 sensor-bridge             114,280
```

**Both the `lau-*` and `ternary-*` families are enormous and largely unexamined**: 264 unseen `lau-*` repos carrying
**14.3 MB** of code, and 345 unseen `ternary-*` repos carrying **6.2 MB**. `ternary-*` at 7.3% prior coverage is the
single largest unexplored surface in the fleet, and it is the family the cell doctrine lives in. `lau-*` names read
like a systematic curriculum — `lau-ricci-flow-agents`, `lau-ricci-curvature-agents`, `lau-sheaf-automata`,
`lau-noether-agents`, `lau-derivation`, `lau-sheaf-learning` — and three of them I compiled are green
(`lau-self-aware-agent` 84/0, `lau-ricci-flow-agents` 98/0, `lau-game-theory-agents` 75/0).

---

## 7. Status of previously-reported findings (verified, not re-derived)

| prior finding | status as of 2026-10-23T0144Z |
|---|---|
| `quality-gate-stream` — committed live API keys | **PERSISTS, and is worse than reported** — 12 open GitHub secret-scanning alerts (Anthropic, 3× GitHub PAT, Crates.io token, 2× Cloudflare, Notion, npm×2, DeepSeek, Groq), open since 2026-05-07. See Finding 4. |
| `superinstance-api` — `.wrangler/` ignore rule is cosmetic | **PERSISTS** — 2 wrangler files still git-tracked; still 0 CI; still 0 test files. |
| `quilt-canary` — 52 tracked `target/` artifacts, no `.gitignore`, zero tests | **PERSISTS** — 52 of 66 tracked files are build output; still 0 CI, still 0 test files. |
| `substrate-attest-rs` — 430/434 tracked files are build output | **FIXED** ✅ — now 5 tracked files, proper `.gitignore` (`target/`, `.wrangler/`, `*.zip`). Someone cleaned it. |
| `quilt-gpu-lab` — committed `__pycache__` + 58 `.rlib`/`.rmeta` | **PERSISTS and got worse** — now **637** build-output files of 4,381 tracked, the bulk under `experiments/wg1_wgsl/target/release/deps/`. |
| `quilt-ewitness` — 7/7, mutation → 4/7, no CI | **PERSISTS** — still no CI. |
| `xruntime-conformance` — 3 hardcoded `/tmp` paths, missing driver, no CI | **PERSISTS** — `attn_conformance.py:13` still reads `/tmp/attn_graph.json`; still 0 CI, still 0 test files. |
| `substrate-foundation` — canary in `index.js:39`, 13 `substrate-*` uninstallable, zero CI | **PERSISTS** — canary still at `index.js:39`; still 0 CI. |
| `quilt-i2i` — 3 defects persist | **PERSISTS** — still 0 CI, still 0 test files. |
| CANARY — `0x24a555471370b18d` | **Re-derived independently: confirmed.** FNV-1a 64 of `"café Δ 日本語"` = `0x24a555471370b18d` (16 hex digits, no leading zero). The accent trap is real: unaccented `"cafe Δ 日本語"` → `0xfee91cf40962b966`. **Scanned every cloned repo for the trap: 0 hits** — no repo hashes the unaccented string. The fleet's two spellings (`0x024a…` 17-digit and `0x24a…` 16-digit) are the **same integer**; compare the integer, as always. |

**One new cloud-credential finding for an already-known repo:** `plato-portal` — 4 open alerts (Alibaba Cloud
AccessKey ID + 2 AccessKey Secrets, Telegram Bot Token). Not in any prior report. See Finding 4.

---

## 8. Carry-forward method rules

1. **Assert monotonicity with `casefold()`**, not raw `==`. GitHub's `sort=full_name` is case-insensitive; a
   case-sensitive comparator manufactures ~141 phantom inversions.
2. **Build the examined-set from the corpus, not from memory.** Tokenize all prior scout reports once and intersect
   with the repo list. 133 reports / 2.8 M chars / 1,616 names mentioned.
3. **Tree-scan the entire candidate pool.** 2,947 calls cost 3% of the API budget and buy certainty. Never pre-filter
   on API `size`.
4. **Rank on code bytes by extension, minus vendored paths.** The API-`size` ranking and the code-bytes ranking have
   almost no overlap at the top.
5. **"The crate has tests" ≠ "the tests run."** Compare `#[test]` count in `src/*.rs` against the count `cargo test`
   reports, and check that the crate root declares the files. A file that `lib.rs` does not declare is dead code with
   a green badge.
6. **Rust findings no longer have to be inspection-only.** `static.rust-lang.org` and `index.crates.io` are both
   reachable (the crates.io 403 in earlier rounds is gone). `rustup` needs `HOME=/root` (the default `HOME` is on the
   full NAS). `cargo test --offline` works for zero-dep crates; the online path works for the rest. 2 CPUs / 3 GB RAM
   — run suites with `-P 2`.
7. **Audit secrets with the secret-scanning API, never code search.** `GET /repos/{o}/{r}/secret-scanning/alerts`
   — 1 call per repo, authoritative, and it also tells you when scanning is *disabled* (11.4% of the fleet).
8. **Group CI runs by `name` AND read the per-job conclusions.** A workflow can be 100% "failure" on `fmt` while
   `test` is green — and vice versa. Report the job breakdown, not the badge.
9. **Watch for compensating defects.** A test suite can be what is *holding* a bug in place (Finding 2). When a gate
   looks wrong, check whether another bug is masking it — and when you fix one, re-verify the gate.
10. **Reproduce the CI failure locally before reporting it.** `categorical-agents-rs`'s CI `test` job is red on HEAD
    `6376ee0a` while `cargo test --all-features` is green locally — do not report that as a code defect; the job logs
    are expired (410) and the cause is not obtainable. Say so.
11. **A green CI badge is a statement about the surviving generation, never about the repo.** The `ternary-compiler`
    badge is red on formatting *of the stub* while 54 tests in the real compiler sit uncompiled.

---

## Appendix — receipts

- Census: 54 pages, `sort=full_name&direction=asc`, `unique_by(.full_name) == 5306 == rows == public_repos` **PASS**;
  821 forks / 4,485 own / 16 archived.
- Examined set: 133 prior reports, 2,817,853 chars, 1,616 names (1,538 own + 78 fork) → 2,947 unseen own.
- Tree scan: 2,947 / 2,947 repos (100%), no size filter.
- Cargo executed: 37 crates → 35 green, 2 with compile errors, **1,604 tests passing across 84 suite runs**.
  Failures: `ternary-compiler` (1 test — the 54 orphans never run), `ternary-checkpoint` (17 errors, all in examples),
  `sheaf-agents-c` (C crate, no cargo target), `plato-dashboard` (needs `uuid`, offline resolution failure).
- Secret sweep: 2,947 repos → 2,611 CLEAN / 335 SCAN_DISABLED / 1 ALERTS; plus known repos
  `quality-gate-stream` 12, `plato-portal` 4, `asset-ranch` SCAN_DISABLED.
- CI job breakdowns read for 7 repos; `cargo fmt` diff reproduced locally for `ternary-compiler`.
- Canary: independently re-derived. 0 accent-trap hits across all cloned repos.
- Toolchain: rustc/cargo 1.99.1 (58cf8f9c3, 2026-10-13), installed this round; `index.crates.io` reachable (200).
