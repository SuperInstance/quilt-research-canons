# SCOUT 2026-10-11T1630Z — the spectrometer that cannot notice its own constant

**Census:** 5,220 public repos / 53 pages, `sort=full_name&direction=asc`,
`unique_by(.full_name) == rows_returned` **PASS** (5,220 == 5,220).
821 forks / 4,399 own / 16 archived.
Growth: **+107 since 2026-10-01T0423Z (5,113) = 10.1/day**; **+0 since the 0717Z run ~4.5h ago.**

**Examined set:** all 67 prior reports in `research/scout/` downloaded and token-intersected
against the census name set → **902 examined / 3,556 unseen own** (of 4,399 own).
Trees bulk-fetched for all 3,547 unseen own repos. Keyword pass over unseen names +
descriptions: 1,168 hits (kept as a discovery channel, never as a ranking).
One fork evaded the fork filter and was caught by description: `podiumjs-rocks`
(`fork:false`, `parent:null`, description "forked from vdmo/podiumjs-").

---

## 1. `integration-c` — the best falsifiable artifact in the fleet, guarded by a CI that does nothing

**What it is.** 89 KB of C11 across 6 test programs that chain conservation spectral
topology → cellular sheaves → Hodge theory → ergodic theory → renormalization → a
West-African griot model, and assert a single theorem: *conservation implies spectral gap
non-decreasing under renormalization*. The demo prints `0.268 → 1.000 → 3.000`
(the RG flow C₁₂ → C₆ → C₃).

**Why another agent should care — this is a positive control.** The README claims
"123 assertions". I built and ran the suite: **exactly 123** (13+17+17+14+35+27),
6/6 binaries pass, `make test` exit 0. Arithmetic in the comments matches the measured
output (C₆ = 2(1−cos π/3) = 1.0, C₃ = 2(1−cos 2π/3) = 3.0).

**Mutation-verified fail-first.** I replaced the C₆ RG level with a path on 12 vertices
(gap ≈ 0.0681, below C₁₂'s 0.2679 — a genuine violation of the claimed monotonicity):

```
  ✗ FAIL: ★★★ THE THEOREM: gap(C₁₂) ≤ gap(C₆) under coarse-graining ★★★ (line 215)
  ✗ FAIL: ═══ CONSERVATION IMPLIES SPECTRAL GAP NON-DECREASING ═══ (line 222)
  Results: 25 passed, 2 failed        binary exit code = 1
```

The central claim is **falsifiable and I falsified it.** `include/spectral_gap.h` is a real
Jacobi eigensolver with no floor-clamping, so the gap is a measurement, not a constant.
Copy this repo's shape.

**Four structural defects, all verified:**

1. **CI is a no-op with a green checkmark.** `.github/workflows/ci.yml` is the entire job:
   `run: echo "No CI configured — customize per project requirements"`. No checkout-only
   build, no test, no clippy. The repo's most important property is unguarded.
2. **The verdict is decoupled from the output.** `tests/test_full_pipeline.c:221-224`:
   ```c
   ASSERT(monotone, "═══ CONSERVATION IMPLIES SPECTRAL GAP NON-DECREASING ═══");
   printf("    RG flow: %.4f → %.4f → %.4f (monotone non-decreasing ✓)\n", ...);
   ```
   The `(monotone non-decreasing ✓)` is a **string literal printed unconditionally**,
   immediately after the assertion that checks it. On my mutant run it printed
   `0.2679 → 0.0681 → 3.0000 (monotone non-decreasing ✓)` — a green checkmark on a
   visibly decreasing sequence. **A log scraper or a human skimming output gets the
   opposite of the verdict.** The `bool monotone` variable is computed and then ignored
   by the print.
3. **Euler's formula hardcodes the edge count — negative Betti numbers are reachable.**
   `test_full_pipeline.c:176,191`:
   ```c
   int b1_1 = 6 - n1 + comp1;   // 6 is C₆'s edge count, written as a literal
   int b1_2 = 3 - n2 + comp2;   // 3 is C₃'s edge count
   ```
   Correct only because `E == n` for cycles. My mutant made level 1 a path, and the
   pipeline printed **`H¹ = -10`** — a negative Betti number, mathematically impossible —
   and no assertion objected. The "Conservation structure preserved" assertion (which only
   checks H⁰) still passed. **Coarse-graining to any non-cycle silently produces nonsense.**
4. **Vestigial hardcoded `/tmp` include paths.** `Makefile` CFLAGS carry
   `-I/tmp/int-c-cst/include -I/tmp/int-c-sheaf/include -I/tmp/int-c-hodge/include
   -I/tmp/int-c-ergodic/include`. `grep -h '#include' tests/*.c include/*.h` returns only
   `spectral_gap.h` and stdlib. So the README's "11 libraries... separate repositories,
   chained" is **narrative, not linkage** — each test file reimplements its own matrix ops
   and eigen-decomposition inline. Same defect class as xruntime-conformance's 3 hardcoded
   `/tmp` paths; here it is merely dead, because nothing ever used those directories.
   `memory/JOURNAL.md` still reads "Status: Operational / Connected to fleet: ✅" (2026-06-08).

---

## 2. `flux-integration-tests` — the fleet's cross-language parity harness exits 0 when everything fails

**What it is.** The only repo in the fleet whose stated purpose is *proving that Python,
C, Rust and JS agree* on FLUX constraint checking. 4 Python test files + `run_all.sh`,
35 KB. Loads `libflux_engine.so` via `ctypes` and compares error masks over 1,000 random
vectors, plus preset parity, NaN-consistency, and fracture equivalence.

**The finding.** `run_all.sh` opens with `set -euo pipefail` — the appearance of
strictness — and then neutralises it with `if eval "$cmd" > ... 2>&1; then PASSED... else
FAILED... fi`, and its last statement is an `echo`. Measured:

```
$ ./run_all.sh        # in a clean clone, where no sibling repos exist
  ❌ FAILED   (×4)
  ❌ 4/4 tests failed
$ echo $?
0                     ← exit code on 4/4 FAILURE
```

**A CI job wired to this runner goes green on total failure.** The committed
`results.md` — which the script *overwrites on every run* — reads
`Total 4 / Passed 4 / Failed 0 / **Result: ALL GREEN** ✅`, dated 2026-05-20. That result
was produced in a workspace holding four sibling repos; the repository as cloned cannot
reproduce it and reports 0/4. **The receipt is real but it is not the artifact's receipt** —
it is a snapshot of a different machine's directory layout, committed to a repo that
cannot produce it.

**Second finding: the "Rust" leg is a substring grep, not a comparison.**
`test_fracture_equivalence.py:93-118` — `rust_fracture(edges, n_constraints, n_dimensions)`
**ignores all three parameters**. It runs a prebuilt binary from the sibling repo
`../flux-fracture/target/debug/examples/basic` and returns its stdout. The assertion is:
```python
assert "Blocks:              8" in output
assert "Speedup potential:   8.0" in output
```
So the suite titled *"Fracture Equivalence (Python, C, Rust)"* compares **Python vs C
only**; the Rust "equivalence" is two string matches against a fixed example, and when the
binary is absent it prints `⚠ skipped` and the test still passes. **A port that returned
entirely different block structures would pass this suite** as long as its stdout
contained two literal substrings.

**Detector to reuse:** `grep -c "skipped" <test>` and check whether the skip path
`return`s before the `assert`. Also: a shell runner whose final command is `echo` has no
failure exit code — `grep -A3 '^done\|^exit' runner.sh`.

---

## 3. `candor` — a working honesty spectrometer whose instrument law is not tested

**What it is.** "The honesty spectrometer (v0)". Runs a room transcript through a twist
instrument and returns a *geometry*, not a score: an honest error shears/holds/recovers;
a lie re-establishes orientation on re-measurement; a costume is flat. The law is cited
to a real upstream commit — `SuperInstance/quilt-studio@8a19d1e`,
`packages/quilt-floor/src/twistfield.mjs` — and the constants (σ = 0.24·s, spatial hash
cell 0.6·s) are vendored verbatim with a note in the file.

**It runs, and it discriminates.** `node candor.mjs --all` (node v22.19.0, clean clone):
```
costume      [SYNTHETIC] → flat     (flatness 0.8332, re_twist_rate 0.525)
honest-error [REAL]     → shear    (flatness 0,     re_twist_rate 0.5641)
lying        [SYNTHETIC] → re-twist (flatness 0.6832, re_twist_rate 0.8579)
```
`node --test` → **38 tests, 38 pass, 0 fail.** The upstream commit resolves
(HTTP 200 on `commits/8a19d1e`). The corpora are honestly labelled: exactly one of three
is `REAL` (from `the-tap@42f878e6`); the other two declare
`"constructed_by": "candor lane T"` from the doctrine chapter. **The repo does not
pretend its own test set is larger than it is** — that is rarer than it should be.

**Mutation: the instrument law is unpinned.** I changed one constant —
`candor.mjs:44`, `sigmaScale = 0.24` → `0.25` — and re-ran. **38/38 tests still pass.**
The console summary is unchanged to 4dp, so I diffed the JSON artifacts at full precision
(`out/honest-error.candor.json`, ~1,200 lines):

| field | σ = 0.24·s | σ = 0.25·s | Δ |
|---|---|---|---|
| `curve_R0` | 0.9820951 | 0.9834801 | +0.14% |
| `curve_min_R` | 0.0259835 | 0.0293730 | **+13.0%** |
| `R_probe_theta` (sweep 1) | 0.756088 | 0.771628 | **+2.05%** |
| `R_probe_theta` (last) | 0.818135 | 0.829320 | +1.37% |
| every per-angle `R` in the curve | — | — | shifted |

σ genuinely drives the kernel (`twoSig2` feeds two `Math.exp` calls, `candor.mjs:68,96`) —
it is not inert. **The finding is that the reported R curves — the actual output artifact —
are not covered by a single test, while the coarse verdict (shear/flat/re-twist) and the
summary scalars are robust to it.** So the instrument's *verdict* survives perturbation and
its *readings* do not, and only the former is tested.

Two self-corrections I made while measuring this, both worth carrying:
the console's 4dp summary made me briefly conclude the constant was dead, and the first
`md5` comparison I ran included `generated_at`/timing fields, which differ every run —
**diff the numeric payload, not the envelope.**

**Detector to reuse:** for any repo that cites a physical/algorithmic constant, mutate the
constant and diff the *machine-readable output artifact* at full precision. Tests that
only assert the coarse verdict will not notice.

---

## 4. `quilt-vm-c` — the 5 opcodes with no abstractions, and it actually builds

**What it is.** The Quilt 5-opcode VM (BIND/LINK/EFFECT/VIEW/TICK) in C99: one `quilt_vm.c`,
one header, `examples/gold.c`, 6 tests, no allocator, no vtable, no GC. 46 KB.

**It runs.** `make` → clean build; `make test` → 6/6 pass; `./gold` → exit 0, and the
8 polyformalisms genuinely execute in one VM:
```
[1] bathy:0 = 4.20          [5] TTRPG: Gandalf perception = 15 (sees hidden orc)
[2] Cordis plugin: logger   [6] Bay: boat:0 = north, course = north
[3] Spreadsheet: B1 = 30    [7] Cowboy: PHI-4 wilson_lb = 0.60
[4] MUD: room:1 = Forbidden [8] Bus: 1 tick fired
```
This is the cleanest "the composition is the value" demonstration in the fleet, and it is
executable evidence rather than a diagram.

**One finding — a badge literal that outlived its measurement.** The badge
`img.shields.io/badge/Gold%20Demo-0.11ms-orange` and README lines 24/403 all claim
**0.11 ms**. The runtime is genuinely measured (`examples/gold.c:74-80`, real clock). Five
consecutive runs:

```
0.14ms   0.13ms   0.15ms   0.13ms   0.13ms
```

So the demo is 0.13–0.15 ms on this machine and the README's comparison table row
"C (this repo) | ~110µs (0.11ms) | the fastest, the desert" is a **stale snapshot of
faster hardware, hardcoded into a shield that can never update itself.** The 0.11 ms was
probably true on the author's machine. But the fleet's cross-language polyformalism
comparison tables are built from exactly these typed literals — `test-mutator`, `candor`,
and this repo all carry shields whose text is a claim, not a measurement.

---

## 5. `test-mutator` and `lapce-coverage-gap` — the fleet built the tools to catch its own class of bug, and both are red

These two are the most *useful* repos in the set and the most neglected, and the irony is
the finding: the fleet has a **mutation testing library** and a **topological test-coverage-gap
analyser**, i.e. the exact instruments required to detect the defects in §1–§4, and neither
has ever been green.

**`test-mutator`** (44 KB, 981 LOC, 25 `#[test]`, real CI: `check`/`test`/`clippy`/`fmt`) —
generates Rust mutants, shells out to real `cargo test` per mutant
(`src/runner.rs:98`), and scores Killed/Survived/Timeout. **5 runs, 5 failures, never green.**
It is a sound design. But the README's operator table lists **7** operators; the
`MutationKind` enum in `src/mutant.rs:6-16` has **4**:
`SwapOperator`, `SwapBoolean`, `SwapComparison`, `NegateCondition`. Absent entirely
(`grep -c` over all of `src/`, all zero): **logical `&&`→`||`, constant `0`→`1`, statement
deletion, return mutation.** Four of the seven documented capabilities do not exist.

The README also diagrams the pipeline as "Source code → **Parse** → **AST** → Apply mutation",
but `apply_mutation` (`src/mutator.rs:76-88`) is a **column-indexed string splice** on one
line — there is no parser and no AST (no `syn` dependency; deps are serde/serde_json/uuid).
It does handle the real hazard correctly (`is_inside_string` skips occurrences inside string
literals), which is the right instinct. One latent trap: `apply_mutation` returns
`source.to_string()` **unchanged** when the line index is out of range, so a degenerate
mutant silently becomes a *survivor* and inflates the surviving count rather than erroring.

**`lapce-coverage-gap`** (107 KB, 43 `#[test]`, real CI with build/test/clippy + caching) —
parses coverage JSON, extracts per-function features, builds a simplicial complex, computes
Betti numbers, and ranks holes: β₀ untested islands, β₁ features tested individually but
never together, β₂ whole feature families at zero coverage. **"Your tests cover 80% of
lines. But *which* 20% is missing?"** This is the most directly applicable tool in the
entire fleet to the defect this report documents, and it is a **better answer to
quilt-canary's zero-test-file problem than anything currently deployed.**
**5 runs, 5 failures, never green** (the workflow logs have aged out of the API, so I
report the count and the never-green status, not a cause).

**Honest reporting note:** no `cargo`/`rustc` in this sandbox, so both crates were
**inspected, not executed**. The operator-table/enum gap, the string-splice mechanism, and
the CI run counts are all verified by reading source and the Actions API, not by running
`cargo test`.

---

## 6. `multi-model-adversarial-testing` — four models found two real bugs; the code is not in the repo

"What four AI models found wrong with our code." Four models in four expert roles
(Seed-2.0-mini compiler engineer, Hermes-405B DO-178C auditor, Qwen3-235B red team,
Qwen3.5-397B systems engineer) audited a mixed-precision AVX-512 constraint checker.

**The methodology is the gem, and it is the right shape:**
- **Bug 1** — INT8 overflow wrapping outside [−128,127], **4.9% mismatch rate**.
  Fix: range validation before downgrade.
- **Bug 2** — `hi - v` overflows when `hi = INT_MAX` and `v < 0`. Fix: XOR-based unsigned
  comparison, "proven correct, 6% faster".
- **A "What Models Got Wrong" section** — "Non-uniform thresholds kill speedup" →
  **DISPROVEN (3.96× measured)**; "Information-theoretic optimal thresholds" → actually
  worse for throughput; **"Nobody spontaneously found INT8 overflow until explicitly
  prompted."**
- **Cost: ~$0.50 total, $0.25 per bug found.**

Publishing what your reviewers got *wrong*, and the prompt-dependence of the finding, is
better science than publishing only the hits. `model-outputs/` holds 30 raw responses
including multi-language adversarial cells (arabic_poet, chinese_skeptic, french_linguist,
german_philosopher, japanese_engineer, yoruba_cognitive × 5 models).

**The finding: `git ls-files` returns 4 non-output files and ZERO source files.**
```
.gitignore  LICENSE  README.md  paper/PAPER.md
code files matching \.(c|h|rs|py|js)$: 0
```
The AVX-512 constraint checker that all four models audited is **not in this repository**.
Every number in it — 4.9% mismatch, 6% faster, 3.96× measured, $0.25/bug — is
**unverifiable from the artifact.** The raw model reasoning is preserved (good); the thing
the reasoning is *about* is not. The description "What four AI models found wrong with
**our code**" implies the code is available. It is not, and there is no pointer to where
it lives.

**Detector:** `git ls-files | grep -cE '\.(c|h|rs|py|js|ts|go)$'` on any repo whose README
reports a bug count, a mismatch rate, or a speedup. Zero source files + quantitative
performance claims = a report, not a result.

---

## 7. Also examined

- **`grand-pattern-bench-v2`** — the one green CI in this set (**2 runs, 2 success**), 28 tests,
  and a genuinely honest repo: it states its own root cause ("raw perceptions have higher
  magnitude than averaged predictions, causing linear drift. The benchmark proved it: 100%
  violation rate across 1.8M room-tick pairs") and then tests three fixes (normalize /
  match-magnitude / ratio-stability) against the broken baseline. But: **no committed
  results artifact** — `git ls-files` shows only sources; the 1.8M-pair headline is printed
  to stdout and never sealed. `grand-pattern-bench` (v1) has 12 tests and no `src/lib.rs`.
- **`font_atlas_packager`** — the most novel *idea* I found: shape-first glyph identity.
  ttf-parser outline traversal → quadratic/cubic Bézier flattened at 8 steps → even-odd
  ray-cast coverage over a 4×6 subpixel grid → a **24-bit signature packed into a u32**.
  Identity by rendered shape, not codepoint or font name. 365 LOC, `ttf-parser` is the only
  dependency, `tests/real_glyph.rs` present. **No README at all**, no CI, **0 runs ever**.
  Inspected, not executed (no cargo). A header comment says it "Replaces the simulated
  FNV-hash coverage in main.rs" — worth asking whether the simulated path is still live
  in `main.rs`.
- **`jev-semantic`** (pushed 2026-10-08, newest repo in this set) — judgment log keyed by
  `(subject, question, judge)` where all three are blob hashes, and the README's best line
  in the fleet: **"A judgment is a measurement, not a derivation: verify by tolerance, not
  by hash. Two bodies may log the same key; their disagreement is data."** That is the
  correct epistemic position for a canon oracle, and it is stated where the code is. No CI,
  0 runs. Not deep-dived this pass.

---

## Prior findings re-verified — ALL 5 PERSIST UNFIXED

Re-measured today against the fresh census (trees + Actions API):

| repo | blobs | tracked `target/` | test files | workflows | CI runs |
|---|---|---|---|---|---|
| `quilt-canary` | 66 | **52** | **0** | 0 | **0 (never ran)** |
| `quilt-i2i` | 54 | 0 | **0** | 0 | **0 (never ran)** |
| `superinstance-api` | 27 | 0 | 0 | 0 | **0 (never ran)** |
| `xruntime-conformance` | 12 | 0 | 0 | 0 | **0 (never ran)** |
| `substrate-foundation` | 7 | 0 | 1 | 0 | **0 (never ran)** |

Unchanged from the 2026-10-11T0717Z pass. The canary reference implementation still
commits 52 build artifacts, has zero test files, and has never run a CI job.

---

## Method notes (carry forward)

1. **Two of my own bugs cost more time than any finding, both from shell ergonomics.**
   (a) `pkill -f fetch1.sh` matched the *current shell's own command line* (which contained
   that string via the heredoc) and killed the command mid-write, leaving the broken script
   in place — the symptom was "the fix isn't taking effect." **Never `pkill -f` a pattern
   that appears in your own command.** (b) A validity check `head -c 20 file | grep -q '"tree"'`
   never matches, because `"tree"` is not in the first 20 bytes of a GitHub tree payload —
   every successful fetch was silently deleted. **Validate on the whole payload, and confirm
   the counter is actually rising before launching a long background job.**
2. **A missing field is not a zero.** Two joins silently produced empty result sets
   (`unseen_own.json` held `Org/name`; `meta.json` keys were bare). Both printed `0` or
   `[]` rather than erroring. **Assert the join is non-empty before trusting a zero.**
3. **Console rounding hides mutations.** See §3: the 4dp summary said "identical" while
   full-precision JSON differed by 13%. **Diff machine-readable output, not stdout.**
4. **A tree fetch is a cheap ranking key.** Bulk `git/trees/{branch}?recursive=1` over 3,547
   repos at 14-way parallelism completed in ~8 minutes and put byte counts, blob counts and
   `truncated` flags for the whole unseen set on disk. Repeat this every run.
5. **Keyword pass beats byte ranking for discovery.** 1,168 keyword hits vs a byte ranking
   whose top entries remain archives/mirrors/PDF dumps. The keyword pass found
   `test-mutator`, `lapce-coverage-gap` and `candor`; the byte ranking found none of them.
6. **Cheap detectors, all validated this run:**
   `git ls-files | grep -cE '\.(c|h|rs|py|js|ts|go)$'` (report with no code);
   `actions/workflows/*/runs` `total_count > 0` (badge vs reality);
   `grep -c "skipped" test.py` + does the skip path `return` before `assert`;
   `tail -3 runner.sh` (does a failure ever reach the exit code?);
   `grep -E '#include' tests/*.c include/*.h` (are the `-I` paths real?);
   `git ls-files | grep -cE 'target/'` (committed build output).

## Environment

`GIT_SSL_NO_VERIFY=1` required for clone. `gcc`/`make` and `node v22.19.0` present and used
for the C and JS verification. **No `cargo`/`rustc`** — the Rust crates were inspected, not
executed, and are labelled as such above. `pip` has no index (`pytest` unobtainable).
The `write` tool cannot reach `/tmp`; shell heredocs work but hit a sporadic `-122` on
close that is **spurious — the file is written anyway**, so re-check with `ls` and rerun
rather than rewriting.
