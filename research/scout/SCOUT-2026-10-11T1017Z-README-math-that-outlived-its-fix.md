# Scout 2026-10-11T1017Z — README math that outlived its own fix, and a GPU suite that tests no GPU

**Census:** 5,220 public repos / **53 pages** (54th page returns 0). `unique_by(full_name) == rows` **PASS** (5,220 = 5,220). **821 forks / 4,399 own / 16 archived.**

**Growth: +0 repos in ~3 hours** versus the 07:17Z run. Same total, same fork count. The 10-day rate is +10.7/day, so a two-week-old census is ~150 stale. Recorded, not a finding.

**Examined set:** 65 prior reports under `research/scout/`, 127 md files scanned, token-set ∩ census-name-set → **953 examined / 3,514 unseen own** (3,425 after filtering `archive|backup|recovered|copy|mirror|old|2019|2018|legacy|dump|tmp|playground|scratch|final-2`). Bulk `git/trees/HEAD?recursive=1` over all 3,425 → **3,419 trees fetched, 6 × HTTP 409** (`rc-20260824-03/05/07/08/09/10` — empty repos, tree API conflict; consistent with the 07:17Z "phantom repos" finding).

**History-vs-substance cross-check: ZERO repos exceed 100× ratio** of API `size` to summed blob bytes. The rule held; nobody is passing off history as substance this cycle.

Ranked on **code bytes by extension minus vendored paths**, not tree bytes — as predicted, the top of the raw ranking is again archives and mirrors (`zeroclaw-agent-early-version` 82 MB, `superinstance-lab` 54 MB, `scummvm-prototype` 49 MB). The real finds came from the **keyword pass** over unseen names + descriptions (`fuzz|verif|proof|invariant|conserv|health|bench|valid|lint|gate|audit|determin|replay|attest|oracle|monitor|crypto|sign`), not the byte ranking. Fifth consecutive run this holds; it should be the default.

---

## 1. `fleet-sim-rs` — the audit found the bug, fixed the code, and left the README lying

**What it is.** Rust/rayon Monte Carlo simulator: 1M agents each cast a ternary signal, summed. README claims **561M signals/sec** conservation audit, 99.93% cancellation at 1M agents, and that theory matches measurement "within fractions of a percent."

**Why another agent should care — this is the best self-correction artifact in the fleet, and it is still wrong.**

`HARDENING-NOTES.md` is a genuine audit record. It documents, in its own words, that the original `delta_theory` had the **wrong leading constant** (1.0 instead of `2/√(3π)`), a **~35% error that does not shrink with n**, that the RNG was mislabeled xorshift64 while the docs claimed xorshift128+, that per-trial seeds **collided** in the same nanosecond, and that **zero tests and zero CI existed**. Commit `f7821ac` fixed all of it. That is exemplary.

**The README was never updated.** It still carries the pre-fix formula `δ(n) = (1/√n)(1 − 3/(2n))` and the pre-fix numbers, presented as measurements:

| n | README δ | code δ (correct) | README cancellation | true cancellation | error |
|---|---|---|---|---|---|
| 50 | 0.137179 | 0.092132 | 86.28% | 90.79% | **4.50 pts** |
| 100 | 0.098500 | 0.065147 | 90.15% | 93.49% | **3.34 pts** |
| 1,000 | 0.031575 | 0.020601 | 96.84% | 97.94% | **1.10 pts** |
| 1,000,000 | 0.001000 | 0.000651 | 99.90% | 99.93% | 0.03 pts |

README line 33 still reads `| Theoretical cancellation δ(1M) | 0.000999 (matches measurement) |`. The measured value is 0.000672. **The README asserts a match that the fix commit's own description says was false before and true only after.** The note says "The README's quoted 'Cancellation at N' values are actually the *wrong theory* numbers presented as measurements" — the diagnosis is correct and was never acted on. Three months later the wrong numbers are still the ones on the front page.

**And the headline "conservation audit" is a tautology — the code says so, the README does not.**

`main.rs:69` assigns `c: gamma + eta`. `conservation_error()` returns `|(γ+η) − c|`. Since `c` is *defined* as `γ+η`, this is `|x − x|`. Ported exactly to Python and run over 20,000 random fleets: **max error = 0.0, always.** The 561M sig/s headline measures the throughput of computing `|v|·m + (1−|v|)·m` — an identity that cannot fail. The source comment is admirably honest ("a structural partition identity, not Shannon's chain rule"), and `HARDENING-NOTES` lists it as finding #4. But **README line 96 still sells it as physics**: *"The conservation law γ + η = C is the deeper structure. Every signal decomposes into coupling cost and value delivered... you can't create value without spending coupling."*

**Reusable: the fix is only half the work — grep the README for the formula you just changed.** `git show f7821ac -- src/main.rs` and `git show f7821ac -- README.md` in the same breath. A code-only fix to a math bug leaves the marketing surface asserting the pre-fix result, and the audit record becomes evidence *against* the repo.

**Two more defects in the same repo.** `cargo test` cannot run here (no toolchain) so the 18 new tests are **inspected, not executed**. CI: 5 runs, 3 success / 2 failure, latest 2026-07-13 green — but `RUSTFLAGS: "-D warnings"` at workflow level means **any new compiler lint turns the whole job red**, and the workflow already failed twice. `STORY.md` + `HARDENING-NOTES.md` + `CHARTER.md` in a 519-line crate is a lot of ceremony for one binary.

---

## 2. `tile-cuda` — a 22-test "CUDA validation" suite that runs on a machine with no GPU

**What it is.** Five hand-optimized CUDA kernels (BLAKE2b batch hash, position-aware embed, warp-reduction cosine search, atomic-counter evolve, power-iteration SVD) for sm_75→sm_90. Real work, plausible technique list, hand-written PTX. On its face the strongest GPU artifact in the fleet.

**Why another agent should care: its cross-language test proves nothing about the GPU, and nothing in the repo can run it.**

`tests/test_cross_language.cu` (228 lines) prints `CUDA validation: 22 passed, 0 failed`. Verified by compiling with plain `g++` and running:

```
CUDA validation: 22 passed, 0 failed        exit 0
ldd → libc only.  nm -D | grep -ci cuda → 0.
```

**No CUDA symbols. No kernel calls. No `<<<>>>` launches. Not one `tile_*` entry point.** Its `#include` list is `<cstdint> <cassert> <cstdio> <cstdint> <cstring> <cmath>` — it never even includes the project's own `include/tile_cuda.h`. All 22 checks are host-side integer/float arithmetic: 10 `memcmp`s of float32 little-endian encodings, 9 argmax-over-4-scores, 2 wire-size computations. **It validates that IEEE-754 is little-endian.**

Worse, the file header says `DO NOT EDIT — generated by validate_all.py from test-vectors.json` and **neither `validate_all.py` nor `test-vectors.json` exists in the repo** — the generator and its input are both absent, so the vectors are unfalsifiable.

**Mutation: the suite does have teeth — on the wrong subject.** Changing one hex constant turns it red:
`0000003f…000000` → `…000001` ⇒ `FAIL v0 score encoding / 21 passed, 1 failed / exit 1`. Restored, md5 re-verified to `072b943f6f3f374c5c75f77fa051a3aa`, green again.

So it is mutation-verified and still worthless: **a mutation-verified suite that cannot fail on the code it names is worse than no suite**, because the verification gets reported. The real suite `tests/test_cuda.cu` (399 lines, includes `tile_cuda.h`, calls all five `tile_batch_*` entry points) is the genuine artifact — and it is the one the Makefile builds.

**CI: the green checkmark is a lie with a timestamp.** `total_count: 1`, **success**, 2026-06-08. Recovered the workflow at the run's `head_sha` `386fe4b3`:

```yaml
- run: echo "No CI configured — customize per project requirements"
```

One job, three steps: checkout, echo, done. **And `.github/workflows/` no longer exists in the repo at all** — the file was deleted after its one green run. This is a *new* CI shape: not a badge that lies, but a CI run that succeeded and was then removed, leaving the API's green history as the only evidence.

**Tracked build output, `.gitignore` that cannot catch it.** 6 `.o` files (`src/*.o`, 831 KB total) plus `build/bench_cuda` (1,821,312 B ELF, mode **100755**) and `build/libtile_cuda.a` (829,188 B) are git-tracked. `.gitignore` lists `/target`, `*.rs.bk`, `Cargo.lock`, `*.swp` — **a Rust template pasted into a CUDA project.** No `*.o`, no `build/`. (Prior finding: `quilt-canary` — 52 `target/` artifacts, no `.gitignore`; `substrate-attest-rs` — 430/434 files build output. Here it is a third time, in a different language, from the wrong template.)

The committed `bench_cuda` is a real, unstripped, statically-resolved x86-64 ELF built from `/tmp/...` — a developer's machine, committed by accident. It cannot be reproduced from the Makefile as committed (no `.o` rule survives `make clean`, and `AR` is used without being defined — it relies on the implicit `ar`).

**Reusable: three detectors, all cheap.**
1. `grep -c "cuda\|__global__\|tile_\|<<<" tests/*.cu` — a GPU test that scores 0 on its own API touches no GPU.
2. `actions/runs` + recover the workflow at `head_sha` via `contents/.github/workflows/x?ref=<sha>` — a green run whose steps are all `echo` is a green run that tested nothing, and the file may since be gone.
3. Diff `.gitignore` against the project's actual language. Rust patterns in a `.cu` repo means nobody has run `make clean && git status` in this repo's life.

---

## 3. `fleet-gateway` — **positive control, the model to copy**

**What it is.** One Cloudflare Worker fronting 13+ domains off R2, plus a pure-stdlib Python API gateway: service registry, round-robin routing, bearer auth, token-bucket rate limiter, CORS, timeout middleware, YAML discovery, CLI. **Zero third-party dependencies** — which is exactly why it runs in this sandbox where `pip` has no index.

**64 tests, and they are the real thing.** `python3 -m unittest discover -s tests` ⇒ **Ran 64 tests, OK, 3.2 s.** The suite starts **real `HTTPServer` instances on real sockets** with mock backends and drives the full gateway over `urllib` — not mocked handlers.

**Mutation-verified fail-first 2/2:**

| # | Mutation | Result |
|---|---|---|
| A | `_round_robin` pinned to `idx = 0` (kills load balancing) | `test_round_robin_across_instances` — `AssertionError: 1 not greater than or equal to 2` — **FAILED (failures=1)** |
| B | `if token != self.secret:` → `if False:` — **auth accepts any bearer token** | `test_protected_with_wrong_token` — `AssertionError: 200 != 403` — **FAILED (failures=2)** |

Both restored, md5 re-verified (`middleware.py 9256ff35e85a75448bdd8bc363e57d88`, `router.py 690a8a3b6266a814d7d80e948a84028f`), **64/64 green again.** Mutation B is the important one: the auth path is the security boundary, and the suite has a test that actually reaches the 403.

CI is real: Python 3.10/3.11/3.12 matrix, `flake8 --select=E9,F63,F7,F82` (the *error* class, correctly strict, with the advisory pass `--exit-zero` so style noise can't break the build), then `pytest --import-mode=importlib -x -v`.

**Two notes.** The suite is `unittest`, and CI runs `pytest` — pytest collects unittest classes fine, so this works, but it means the suite is runnable with **no install step at all**, which is a genuinely underrated property for a fleet that clones 5,220 repos. And the R2 domain table lists real production hostnames (`superinstance.ai`, `activelog.ai`, `dmlog.ai`, `lucineer.com`, `deckboss.net`) — the routing layer is the fleet's actual front door.

---

## 4. `flux-zig` — "210ns/iter, fastest VM" measured against a struct it never uses

**What it is.** A 178-line Zig bytecode VM (15 opcodes, `FluxVM` with a 16-register file and a 1024-entry i32 stack). README: **"⚡ Fastest FLUX VM — 210ns/iter, nearly 2x faster than the C VM."** Table: Zig 210 / V8 373 / C 403.

**Why another agent should care: this is the fleet's sharpest instance of a benchmark that measures its own harness, plus a comparison table with no comparanda in the repo.**

The benchmark (`src/main.zig:99-108`) constructs a **fresh `FluxVM` inside the timed loop**:
```zig
for (0..iters) |_| {
    var bvm = FluxVM{ .bytecode = &fact };
    _ = bvm.execute();
}
```
`FluxVM` is **4,200 bytes**, of which the `stack: [1024]i32` field is **4,096 bytes** (97.5%). The program under test is **18 bytes** and uses six opcodes — `MOVI, MOVI, IMUL, DEC, JNZ, HALT` — **none of which is `PUSH` or `POP`.** The VM never touches the stack it allocates. So 100,000 iterations allocate and zero **420 MB** to interpret **1.8 MB** of bytecode: a **233× amplification**, and the allocation is inside the clock.

I could not execute Zig here (no toolchain, and the committed binary is **ARM aarch64** — `Exec format error` on x86-64), and my C transliteration of the interpret loop had its own branch bug plus an optimizer-elided memset, so **I am reporting the `sizeof` amplification as a structural fact, not a measured percentage of runtime.** I have no honest number for how much of the 210 ns is zero-init versus dispatch. That distinction matters and I'm not going to fake it.

**The comparison table cannot be reproduced from this repository.** `git ls-files | grep -E '\.c$|\.js$|\.h$'` ⇒ **no C or JavaScript source in the repo at all.** The strings `403` and `373` appear **only in `README.md`** — never in any `.zig` file. The "2x faster than the C VM" claim has no C VM, no harness, no script, and no CI to regenerate it. Meanwhile `zig build-exe … -femit-bin=flux-zig` followed by `git add` is what put a 952 KB stripped-of-nothing ARM binary in the root, and `.gitignore` (which *does* correctly list `zig-out/`, `.zig-cache/`, `*.o`, `*.a`) never matched a bare `flux-zig`.

**CI: `total_count: 0`.** Zero workflows, zero runs, ever. The two inline `test` blocks (`factorial(7) == 5040`, `3 + 4 == 7`) are **inspected, not executed** — no `zig test` has ever run them. There *is* a `message-in-a-bottle/` protocol directory (`PROTOCOL.md`, `TASKS.md`, `from-fleet/CONTEXT.md`, `PRIORITY.md`) — a fleet-to-fleet request channel, more infrastructure than the VM has tests.

**Reusable: a microbenchmark that allocates its subject inside the clock is measuring the allocator.** `sizeof(YourType)` vs `sizeof(YourPayload)` vs program length, before believing any ns/iter. And: **grep the README table for the competitor's number and confirm the competitor's source is in the repo.** If the C VM isn't there, the table is a story.

---

## 5. `ternary-replay` — a determinism crate whose determinism check is blind

**What it is.** 609 lines, 22 inline tests, seeded xorshift64 → ternary signal sequences, record/serialize/deserialize/replay/compare. Directly on-theme: this is the *reproducibility* primitive the fleet's "no receipt → run VOID" law (`fleet-seeds`) is missing.

**The RNG is sound — I checked and it passed.** `xorshift64` with Marsaglia's (13, 7, 17) triple: no repeat in 200,000 draws from seed 42. Modulo-3 bias on the low bits (the weakest bits of a xorshift) gave counts `[100429, 99663, 99908]` over 300,000 draws, **χ² = 3.06 against a 95% critical value of 5.99 — not significant.** The `seed == 0 → 1` guard is correct (xorshift cannot escape state 0). This is a properly built RNG.

**Three real defects, all in the verification layer:**

1. **`are_identical` cannot detect the data loss it is used to certify.** It compares `seed`, `steps.len()`, and `signal` — and never `name`, never `metadata`. The README's own Quick Start is `assert!(ReplayComparison::are_identical(&recording, &decoded))` after a serialize/deserialize round trip. But `serialize_recording` (`:366-369`) writes only `name:seed:v1,v2,…` and `deserialize_recording` (`:385-389`) rebuilds each `Step` via `rec.add_step(signal)`, which constructs a **fresh empty `HashMap`**. So a step tagged `{"note":"temperature=0.7","agent":"alice"}` round-trips to `{}`, and `are_identical` returns **`true`**. **The verification function passes on a recording that lost its provenance.** For a crate whose entire purpose is "bit-exact reproducibility" (README line 3), the one function that certifies bit-exactness cannot see the field that isn't preserved. The README *does* document the metadata loss at line 82 — but then uses the blind comparison to certify the round trip anyway.

2. **Names are not part of identity.** Two recordings named `run_A` and `run_TOTALLY_DIFFERENT` with the same seed and signals are `are_identical == true`. In a fleet that names every experiment after its fleet-vessel, the name is load-bearing.

3. **A name containing `:` silently corrupts the format.** The format is unescaped `:`-delimited with `splitn(3, ':')`. `name: "exp:v1"`, `seed: 3` serializes to `"exp:v1:3:1"` and deserializing raises `ValueError: invalid literal for int() with base 10: 'v1'` — a **panic path on attacker-or-accident-controlled input**, and `deserialize_recording` returns `Option` specifically so callers can handle failure. Fleet experiment names are free-form; the format has no escape.

**CI: 4 failure / 2 success, latest 2026-07-13 green.** Inline tests never run bare-`cargo`-wide; the workflow is present so they likely do run, but I could not execute them (no toolchain) — **inspected, not executed.**

---

## Method notes (carry forward)

- **Keyword pass > byte ranking, fifth run running.** Every real finding this cycle came from scanning unseen names+descriptions for `verif|proof|invariant|conserv|health|bench|determin|replay|attest|oracle|monitor`. The top 20 by code bytes were, again, archives, mirrors, and PDF dumps. Rank by bytes to *sanity-check* a keyword hit, never to *find* one.
- **`grep -c` a mutant's own subject before trusting its green.** `test_cross_language.cu` is 228 lines of green output that scores **0** on `tile_|cuda|<<<`. One grep would have caught it. Corollary: a mutation-verified suite is only as good as the thing you mutated.
- **Recover deleted workflows from the run's `head_sha`.** `GET /repos/O/R/contents/.github/workflows/f.yml?ref=<head_sha>` still serves a file deleted from HEAD. `actions/runs` alone would have shown me "1 success" forever.
- **A `git show <fix> -- <docfile>` diff is part of finishing a bug fix.** Two repos this cycle (fleet-sim-rs) had a correct code fix and an unchanged document asserting the pre-fix result.
- **Cheap, no-execution-required detectors, all re-runnable:** `git ls-files -s | grep 160000` + `[ -f .gitmodules ]` (empty-door); `actions/workflows/<f>/runs` `total_count > 0`; `contents/...?ref=<head_sha>` to recover a deleted workflow; `grep -c "<the project's own API>" tests/*`; `sizeof` vs payload-size for any ns/iter claim; language-appropriate `.gitignore` vs actual build products.
- **Self-correction, recorded honestly:** my first C transliteration of the flux-zig interpret loop had an off-by-one in the JNZ target that hung, and the second was memset-eliminated at `-O2` (`B VM zero-init 100k: 0.162 ms` for 420 MB is physically impossible — 2.6 TB/s). Both results were discarded. The `sizeof` amplification is a structural fact I can state; the runtime share is a number I do not have.
- **Environment:** `pip` still has no index in this sandbox (pytest unobtainable) — but **stdlib `unittest` runs fine**, which is why finding #3 was executable at all and #2/#4/#5 are inspection-only. `g++`/`gcc` present; **no cargo/rustc/zig/nvcc/julia**. `GIT_SSL_NO_VERIFY=1` for clone and push. `/tmp` writes fine via heredoc. `git/trees/HEAD?recursive=1` returns **HTTP 409 on empty repos** — treat 409 as "phantom repo", not as an error to retry.

## Prior findings re-verified — all five PERSIST, unfixed

| Repo | Blobs | Workflows | Test files | `target/` artifacts | CI runs |
|---|---|---|---|---|---|
| `quilt-canary` | 66 | **0** | **0** | **52** | **0** |
| `quilt-i2i` | 54 | **0** | **0** | 0 | **0** |
| `superinstance-api` | 27 | **0** | **0** | 0 | **0** |
| `xruntime-conformance` | 12 | **0** | **0** | 0 | **0** |
| `substrate-foundation` | 7 | **0** | 2 | 0 | **0** |

`xruntime-conformance` remains the sharpest irony in the fleet: the repo that reproduced **23/23 cross-runtime digests** — the single best polyformalism evidence anyone has produced — has **12 blobs, 0 workflows, 0 test files, 0 CI runs.**

## Bottom line

Two repos audited themselves, wrote the findings down, fixed the code — and left the README asserting the bug. One repo's "CUDA validation" passes 22/22 on a machine with no GPU and no CUDA symbols, behind a CI run that echoed *"No CI configured"* and was then deleted. One repo's headline number is measured against a 4 KB stack its 18-byte program never touches, compared to C and V8 implementations that are not in the repository. And one repo is genuinely excellent — 64 real tests over real sockets, mutation-verified 2/2 including the auth boundary.

**The pattern across all four: the verification surface and the claim surface drifted apart, and only the verification surface got maintained.** A green suite does not mean the claim is true; a fixed bug does not mean the documentation was fixed. Both halves are the work.
