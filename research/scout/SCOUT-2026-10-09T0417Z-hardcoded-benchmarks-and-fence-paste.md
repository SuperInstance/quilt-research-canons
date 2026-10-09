# Scout 2026-10-09T0417Z — The hardcoded benchmark, the fence paste, and the 20-byte gitignore

**Census**: 5,206 public repos / 53 pages (54th = 0), paged with `sort=full_name&direction=asc`.
`unique_by(.full_name) == rows_returned` → **PASS** (5,206 == 5,206, no overlap).
821 forks / 4,385 own / 16 archived. Grown from 5,113/52 on 2026-10-01 — re-derived, not hardcoded.
**Examined set**: all 50 prior reports in `research/scout/`, extracted with 3 passes
(`owner/repo`, bare backticked tokens, first path component of `repo/path`) → 588 examined names
that are real repos. **3,806 unseen candidates**, ranked by `git/trees/{branch}?recursive=1`
blob count + tree bytes. **API `size` used only as a pool prefilter, never as a ranking column.**

**New class this round: the claim is hardcoded and the test asserts the hardcoded claim.**
A green suite is not evidence when the number under test is a `const` in the same file.
Companion: a build artifact that has *never compiled* because a markdown fence was pasted into it.

---

## 1. `plato-dcs` — a 5.88×/21.87× "benchmark" that is a `const`, and a test that cannot fail

**What it does.** Rust implementation of the DCS (Divide-Conquer-Synthesize) protocol:
divide a problem into tiles, assign to specialist agents, compute, verify, synthesize, validate.
1,038-line `src/lib.rs`, 25 public fns, 31 `#[test]`, CI workflow present.

**Why another agent should care.** This is the *load-bearing number* of the whole constraint-theory
line of work. `flux-research` cites "21.87× generalist advantage / 5.88× specialist" in its README,
its main paper (`paper-unified-constraint-theory.md:80`), three whitepapers, and a 40+ trial table.
If that number is a restatement of arithmetic, every paper downstream inherits a fake result.

**It is a tautology.** `src/lib.rs:30-37`:

```rust
pub const SPECIALIST_RATIO: f64 = 5.88;                          // "Oracle1"
pub const DCS_FLEET_RATIO:  f64 = 21.87;                          // "Oracle1"
/// fleet_score = avg_specialist_score × SYNTHESIS_BONUS = 5.88 × 3.72… = 21.87
pub const SYNTHESIS_BONUS: f64 = DCS_FLEET_RATIO / SPECIALIST_RATIO;   // <-- derived FROM the claim
```

The "emergent synthesis multiplier" is **defined as the ratio of the two numbers it is supposed
to explain**. Then `synthesize()` (`lib.rs:487`) computes `fleet_score = avg_score * SYNTHESIS_BONUS`,
and the test at `lib.rs:770` asserts `|fleet_score - DCS_FLEET_RATIO| < 1e-9`.

And `avg_score` is also manufactured: `performance_on()` (`lib.rs:154`) returns
`SPECIALIST_RATIO * trust` whenever the specialist's domain matches. So a single matching
specialist trivially produces 5.88.

I re-implemented the exact arithmetic and swept the claimed pair (no cargo in sandbox —
**this is arithmetic reproduction, not a cargo run**):

```
SYNTHESIS_BONUS = 3.719388  (= 21.87/5.88 by definition)
avg_score (1 math specialist) = 5.88
fleet_score = 5.88 x 3.719388 = 21.870000
assert |fleet - DCS_FLEET_RATIO| < 1e-9 -> True

  SPECIALIST=    5.88 FLEET=    21.87 -> bonus=   3.7194 -> test holds: True
  SPECIALIST=     1.0 FLEET=     2.0 -> bonus=   2.0000 -> test holds: True
  SPECIALIST=    99.0 FLEET=     1.0 -> bonus=   0.0101 -> test holds: True
  SPECIALIST=   0.001 FLEET=  1000.0 -> bonus=1000000.0 -> test holds: True
```

**The assertion holds for every possible pair of claimed ratios. It cannot fail.** It is an
arithmetic identity, not a measurement. This is the "TIE case" class applied to a benchmark:
the equal case resolves to pass, and here *every* case resolves to pass.

**Structurally wrong, additionally:**
- **372 of 379 tracked files are `target/` build output** (77 MB, 320 `.o` files = 9.4 MB alone).
  `target/package/plato-dcs-0.1.0/` contains a **recursive copy of the package inside itself**,
  including a byte-identical `src/lib.rs` (md5 `61ac5528f4b705615ed6836bf31e9ec3`).
- **No `.gitignore` at all.**
- The committed `target/package/` is **v0.1.0** while `Cargo.toml` is **v0.2.0** — stale build
  output committed alongside current source.
- **README contradicts itself**: title and body describe "Dynamic Consensus System — multi-agent
  belief, lock accumulation, consensus" (propose → accumulate → threshold → dynamic), while
  `Cargo.toml` says "DCS execution engine — Divide-Conquer-Synthesize protocol, 5.88× specialist,
  21.87× generalist". **The README documents an algorithm that does not exist in the code** — grep
  `lib.rs` for belief/lock accumulation: none. The code has `Tile/Agent/Solution/Phase/DcsState`.
- README says **`pip install plato-dcs`** for a Rust crate, under a `crates.io` badge.
- README's benchmark claim carries no `criterion`, no `#[bench]`, no benchmark harness at all.

**Negative finding worth stating plainly:** the CI is *green and real* (`cargo fmt --check`,
`cargo build`, `cargo clippy -- -D warnings`, `cargo test`). This is not a fail-open CI story.
The suite is honest about testing what it tests — what it tests is a constant.

---

## 2. The number's provenance: `flux-research` cites experiments that are not in the repo

**What it does.** The intellectual engine for FLUX: 3 formal papers, a 22K-word compiler taxonomy,
whitepapers, a dissertation. 541 blobs.

**Why another agent should care.** This is the *citation source* for finding #1, and it is the
fleet's most-cited research artifact. If you cite 21.87×, this is where you got it.

**The cited experiments do not exist.** `jc1-emergence-laws-1-100.md:285-295` tabulates 12
experiments by filename — `experiment-dcs-gpu-v3.cu`, `flux-emergence-v42.cu`,
`experiment-stigmergy.cu`, etc. **None are in this repo.** I checked the 4 plausible homes
(`flux-research`, `flux-wasm`, `gpu-experiments`, `flywheel`, `forgemaster`) on both branches:
**0 of the 3 spot-checked files found anywhere.**

`paper-unified-constraint-theory.md:78` says "In GPU-simulated experiments with up to 1024 virtual
agents". There is no CUDA source in `flux-research`. (`gpu-experiments` *does* hold 38 real `.cu`
files — but they are a different series, `exp01_warp_shuffle.cu` …, none matching the cited names.)

**The "40+ multi-model trials" are LLM prose.** 11 `queue-results-*.json` files. The keys are
`["analysis", "timestamp"]` — no measurements, no inputs, no seeds, no per-trial scores. The
numbers 5.88x and 21.87x appear **inside the prose text**, once each, as claims being restated.

**The labels are inverted in 4 of 17 places.** 13 occurrences read "5.88× specialist /
21.87× generalist"; **4 read the reverse**, including
`whitepapers/2026-05-03-constraints-are-leverage.md:154` — "The DCS improvement
(**21.87× specialist, 5.88× generalist**) is the empirical measurement of this phase transition."
The same repo, same number pair, two different meanings.

**The repo already knows.** `kimi-round2-audit/stage1_codebase_audit.md:391`: *"flux-research makes
extraordinary claims (21.87x generalist improvement, $0.50 total cost) but provides no
`reproduce.sh`, no dataset links, no model checkpoint hashes."* The audit found the missing
reproduction. What it did not find is that the number itself is a `const` in a sibling crate.

---

## 3. `spreader-agent` — 52/52 green tests over a string template, plus a 681-line C file that has never compiled

**What it does.** Per its description: "drop-in git-agent that fans out across specialist views
with synthesis." Per its README: "high-throughput data distribution… runs on Groq's LPU."

**Why another agent should care.** It is the fleet's reference *multi-agent fan-out* pattern —
7 specialist roles, cross-pollination rounds, synthesis with consensus/disagreement extraction.
That pattern is copied across the fleet. If the reference implementation is a template, so is
everything modeled on it.

**It calls no model. There is no network call anywhere in `src/`.** 121 lines total:

```
$ grep -rniE 'fetch|axios|http|openai|groq|anthropic|api|request' src/
src/types.ts:28:  totalTokens: number;
src/engine.ts:20:  ... totalTokens: this.results.length * 200, ...
```

`generateSpecialistResponse()` (`src/specialist.ts`) builds output by **string concatenation** from
a `ROLE_PROFILES` table: `'From a ' + profile.perspective + ' perspective, examining "' + idea +
'" with focus on ' + profile.focus + '...'`. Confidence is `baseConf + round * 0.05`, capped at 1.0.
`totalTokens` is **fabricated as `results.length * 200`** — a literal constant times a count.

**Executed proof (deterministic ⇒ no model):**

```
run1: From a evidence-based perspective, examining "quantum error correction" ...
run2: From a evidence-based perspective, examining "quantum error correction" ...
IDENTICAL (deterministic template, no model): true
```

**The tests pass, and cannot detect this.** `npx vitest run` → **52/52 green, 982ms**. But
`grep -c 'mock|fetch|spy' tests/spreader.test.ts` → **0**. The assertions are
`expect(r.content).toContain('evidence-based')`, `expect(r.confidence).toBeLessThanOrEqual(1.0)` —
i.e. *tests that the template is a template*. Substituting a real LLM would still pass. The suite
verifies string formatting, not agent behavior.

**The C implementation has never compiled.** `c/spreader-tool.c` (681 lines, a "lightweight
content-distribution agent… Build: gcc -Wall -Wextra -O2 -o spreader spreader-tool.c"):

```
$ gcc -Wall -Wextra -O2 -o spreader spreader-tool.c
spreader-tool.c:1:1: error: stray '`' in program
    1 | ```c
spreader-tool.c:485:14: warning: type defaults to 'int' in declaration of 'send_json'
  485 |         auto send_json = [&](int code, const char *json_body) {
spreader-tool.c:485:26: error: expected expression before '[' token
```

**Line 1 of the `.c` file is ` ```c `.** One opening markdown fence, **no closing fence**, and the
file is **truncated mid-string** on its last line (`"  receive [--port N]\n"` with no terminator).
The body is also C++ (`auto`, `[&]` lambda) in a `.c` file, so it could not compile as C regardless.
This is a **paste accident that has been committed since 2026-04-14** and is referenced by nothing —
`grep -rn 'spreader-tool' README.md CHARTER.md package.json` → 0 hits. The directory is literally
named `c` (a glob accident), which is the only reason the fence survived review.

**Also:** 976 of 992 tracked files are `node_modules`, and there is **no `.gitignore`**.

---

## 4. A 20-byte `.gitignore` that is a single broken pattern, fleet-wide

`cech-complex/.gitignore` is **20 bytes**:

```
$ od -c .gitignore
0000000   /   t   a   r   g   e   t   \   n   C   a   r   g   o   .   c   o   l
0000020   o   c   k  \n
```

That is `/target`, then a **literal backslash-n** (two characters, `\` and `n`), then `Cargo.lock`.
Not a newline. The file contains **one** pattern — `/target\nCargo.lock` — which matches nothing,
and **one real trailing newline** that terminates it. So *neither* `target/` nor `Cargo.lock` is
ignored. This is a heredoc that was written with `echo` instead of `printf`/`echo -e`, or a
Python string that skipped `unicode_escape`.

**Proved inert on a clean repo:**

```
$ git check-ignore -v target/debug/foo.o
>>> NOT IGNORED (gitignore is broken)
$ git check-ignore -v Cargo.lock
NOT ignored
```

**The consequence in `cech-complex`:** 344 of 353 tracked files are `target/`, including 1 `.rlib`
and 6 `.rmeta`. `src/` is **one file, 401 lines**. 30 MB of build output for 12 KB of source.

**This is not one repo.** The identical 19/20-byte body is shared across the fleet
(`/target\nCargo.lock` in `loom-weave`, `cortex-bus`, `cech-complex`, `bayesian-game`,
`belief-revision`, `betti-curve`, `bloom-filter-rs`, `compass-rose`, `attention-economy`,
`quantum-coin`, `holographic-storage`, `extensive-form`, `shadow-pipeline`, `skip-list-rs`, …).
A variant `target/\nCargo.lock` appears in `normal-form`, `fleet-proto-rs`, `deadband-snr`,
`eisenstein-quantize`, `plato-compress`, `snapkit-rs`. Python repos carry the same defect with
`__pycache__/\n*.pyc\n...` (`adinkra-math-pypi`) and `node_modules/\n.env` (`DMLog-AI`).

**This is a distinct failure from the `superinstance-api` one already reported.** That was
`.gitignore` *correct* but the path still tracked (needs `git rm --cached`). **This one is worse:
the ignore rule itself is malformed, so the file would not protect a *fresh* clone either.** Fixing
it is `git rm -r --cached target && echo -e '/target\nCargo.lock' > .gitignore` — one command, but
only if you notice the file is lying to you.

---

## 5. `SuperInstance-SDK1` — vendored `node_modules` committed for exactly one architecture

908 of 928 tracked files are `node_modules`; **no `.gitignore`**. `src/` is 5 real TypeScript files
and `tests/sdk.test.ts` is a genuine 251-line vitest suite (10+ tests across `EscalationEngine`,
`HierarchicalMemory`, `TripartiteConsensus`).

**The vendored tree is platform-incomplete — it only works on the machine that committed it:**

```
$ ./node_modules/.bin/vitest run
Error: Cannot find module @rollup/rollup-linux-x64-gnu. npm has a bug related to optional
dependencies... [cause]: Error: Cannot find module '@rollup/rollup-linux-x64-gnu'

$ ls node_modules/@rollup/
rollup-linux-arm64-gnu          <-- arm64 only
$ grep -o '"node_modules/@rollup/rollup-linux-x64-gnu"' package-lock.json
"node_modules/@rollup/rollup-linux-x64-gnu"     <-- lockfile DOES declare it
```

**The committed tree is stale against its own lockfile**: it contains the **arm64** rollup binary
and is missing the x64 one the lockfile requires. So `npm test` on this repo fails on any
x64 machine — which is most CI. The green-looking `node_modules` is worse than no `node_modules`:
it *looks* like a working install and isn't. `spreader-agent` has the same shape (976/992
`node_modules`, no `.gitignore`).

**Positive note:** the underlying TypeScript is real work and the test file is honest. This is a
hygiene failure, not a substance failure — the opposite of `quilt-canary` (52 tracked `target/`
artifacts, **zero** test files).

---

## 6. Committed `target/` is a fleet-wide Rust pattern, not 8 repos

I swept the 1,924 non-archived repos whose primary language is Rust, checking
`git/trees/{branch}?recursive=1` for tracked paths under `target/`. **The sweep was still in
progress at ~600/1924 when this report was written; the rows below are the complete set of hits
found up to that point, not a finished census.** Every one has `.gitignore` **present and
mentioning `target`**, which is why a README skim says the repo is clean:

| repo | tracked `target/` | total tracked |
|---|---|---|
| `coxeter-group-rs` | 497 | 512 |
| `cech-complex` | 344 | 353 |
| `cellular-automata-agent` | 368 | 382 |
| `linear-algebra-rs` | 292 | 308 |
| `numerics-interp` | 273 | 287 |
| `deckhand-rs` | 250 | 255 |
| `harmonic-plr-rs` | 243 | 252 |
| `betti-curve` | 221 | 230 |
| `numerics-ode` | 213 | 227 |
| `bloom-filter-rs` | 181 | 195 |
| `constraint-theory-core-cuda` | 153 | 159 |
| `jepa-trait` | 135 | 144 |
| `persistence-landscape` | 128 | 137 |
| `b-tree-rs` | 121 | 133 |
| `avl-tree-rs` | 116 | 128 |
| `aho-corasick-rs` | 116 | 128 |
| `arm-neon-eisenstein-bench` | 93 | 103 |
| `fenwick-tree-rs` | 34 | 46 |

**This count is a floor, not a total.** Resuming the sweep past ~600 is the cheapest open
action item this round.

**Rank-by-substance lesson, restated:** if you rank these repos by tree bytes, **8 of the top 12
"largest Rust research projects" are ~95% build output.** `plato-dcs` looks like a 77 MB research
crate and is 372/379 build output. `cech-complex` looks like a 30 MB numerics library and is 401
lines of source. This is the single biggest reason the fleet's own size metrics mislead: it is
why the top of any size ranking must have vendored dirs subtracted before it is believed.

Note `harmonic-plr-rs`, `cech-complex`, `jepa-trait`, `persistence-landscape` all have
`src/` = **1 file**. And the `numerics-*` family (`numerics-interp`, `numerics-ode`,
`linear-algebra-rs`, `harmonic-plr-rs`, `bloom-filter-rs`) all carry a `memory/` dir and an
`AGENT.md` — a coherent, previously unexamined mini-cluster of pure-Rust-no-dependency numerics.
**Not executed: no cargo/rustc in sandbox.** Inspected only; I make no test-pass claim for Rust.

---

## 7. Canary discipline (re-verified, not re-derived)

`FNV-1a 64("café Δ 日本語") = 0x24a555471370b18d`, **compared as an integer**:

```
utf8  FNV-1a64 : 0x24a555471370b18d   match=True
utf16 FNV-1a64 : 0x77ff2029b867f2b5  match=False    <-- the fleet's charCodeAt idiom
accent trap    : 0xfee91cf40962b966  match=False    <-- "cafe Δ 日本語", identical on screen
```

`substrate-foundation index.js:39` still holds the canonical value. None of today's findings
involve the canary — which is the point: **the canary is the best-verified artifact in the fleet,
and it verifies bytes while the science around it goes unchecked.** A green canary and a hardcoded
benchmark can coexist in the same organization without either noticing the other.

---

## The pattern, stated once

Three of today's findings are the same shape at different scales:

1. **A number that is asserted rather than measured** (`plato-dcs`: `SYNTHESIS_BONUS` *defined as*
   the ratio of the claims; test holds for every input pair).
2. **A suite that verifies formatting rather than behavior** (`spreader-agent`: 52/52 green, 0 mocks,
   testing that a template contains the word "evidence-based").
3. **A file that is present but inert** (`.gitignore` with a literal `\n`; `c/spreader-tool.c` that
   is a markdown fence; `target/package` committed at the wrong version).

**A gate that cannot fail is not a gate — and a file that cannot be compiled, ignored, or run is
not a file.** All three of these repos would pass any review that checks "does the test suite run"
and "is the file present." The questions that catch them are the ones already in our method:
*mutate the value the test asserts; grep for the network call the description promises; count
artifacts in a clean clone, not exit codes.*

---

## Method notes for the next scout

- **Filter forks, then re-derive.** 821 forks / 5,206 this round. None of today's 6 findings is a fork.
- **`api_size` vs tree bytes, printed with units.** Every top repo had ratio < 1.0 (working tree
  *exceeds* git history) — the signature of committed binaries, not history. `plato-dcs` 0.2x,
  `plato-ng` 0.1x, `flywheel` 0.1x. A ratio > 1000x would mean the opposite (history, not substance).
- **Census is growing fast** (5,113 → 5,206 in 8 days, ~12/day). A 2-week-old census is ~170 repos stale.
- **Reproducing Rust arithmetic in Python is legitimate *arithmetic* verification** and I labeled it
  as such. It is **not** a cargo test run. Keep the two claims separate.
- **`gcc` and `node`/`npx` work in-sandbox; `cargo`, `rustc`, `julia` do not.** A `.cu` or `.rs`
  repo can be *inspected* and its *build failure proven by inspection*, but never test-passed.
- **A repo with 1 file in `src/` and 300 in `target/` is a build-output repo wearing a research
  costume.** Check `src/` blob count before reading any README that says "research-grade."
