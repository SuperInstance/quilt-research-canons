# Wave-67 gift audit — the operator's agent artifacts, mechanically verified

**Received 2026-09-30 (IM):** dashboard panel toggle (app.js), SSD chronologger (elephant_sync.rs), fragment shader (fragment.glsl), "memory layout proof" ×2 (python), thread-affinity pinning (affinity.rs) + core map, ASCII sparklines. Framed by the sender as: "The System Core is Weaponized… the proof is absolute… ready to be weaponized."
**Method:** run what runs, compile what compiles, measure what was asserted. Same play as the superinstance.md debrief; new specimens preserved verbatim in `gifts-original/`, hardened rewrites in `fixed/`, reusable auditor: `gift_lint.py`.

---

## 1. Verdict table (every claim, every receipt)

| # | Gift claim | Verdict | Receipt |
|---|---|---|---|
| 1 | 7696-byte layout arithmetic (80×24×4B + 16B header; glyph:8\|color:8\|weight:8\|flags:4\|buzz:4) | **CORRECT** | both python proofs run verbatim, exit 0; word `0x81C8027E` unpacks field-perfect through our *generated* bitlaw codec |
| 2 | "proof that the native host compiler lines up byte-for-byte with the WebGL textures on the GPU" | **FICTION** | the proof round-trips python through python — zero runtime boundaries crossed. No Rust compiled, no GPU touched, no `texSubImage2D` run. Our true cross-runtime proof (gift data → frame-law wire → parsed by python **and** node) passes — and the GPU boundary remains honestly open |
| 3 | cell-word field order | **INDEPENDENT RE-DERIVATION of our law** | gift "color" = our "route", same bit position; convergent evolution of the same contract — the strongest evidence yet that the cell word is the natural shape |
| 4 | gift frame header (16B, LE `<IIII`, no magic) | **TWO-HEADS DRIFT** | frame law rejects gift header (`bad magic`); gift eyes read our law header as `0x32465551` garbage. The exact scattered-contract disease the bit law was built to kill, re-arriving in a gift |
| 5 | elephant_sync.rs "asynchronous task lanes" | **DOES NOT COMPILE** | rustc E0425 `cannot find value this` ×2 (rustc itself suggests `self`); also `tokio::spawn` of blocking file I/O = executor-stalling anti-pattern; `/mnt/vessel_ssd` assumed present |
| 6 | affinity.rs pinning | **DOES NOT COMPILE AS SHIPPED; CORRECT ONCE DEPENDENCY DECLARED** | rustc E0432 unresolved crate `libc` (no manifest shipped); fairness check: with `libc = "0.2"` declared, compiles clean (1 warning). Our zero-dep rewrite compiles and RUNS: `Cpus_allowed_list: 0-1 → 0`, kernel-verified |
| 7 | "Core #1 L1/L2 Cache Hit Rate: 99.84% [PASS], Jitter < 4μs [PASS]" | **FICTION** | no code in the gift could produce those numbers; our real measurement of the same 60Hz sleep loop on this host: **mean 16729μs, stdev 9μs, max 16756μs** — the claim was never measured |
| 8 | fragment.glsl | **DOES NOT COMPILE + DEAD CODE** | `floatUnpackedBuzz` never declared (compile error); the "high-frequency ripple" writes `dynamicCoords.x` but the sampler reads `v_texCoord` — zero visual effect; "reclaims canvas real estate instantly" is false (a fragment shader recolors; it reclaims nothing) |
| 9 | "zero-heap / zero-allocation" sparklines, "zero memory copies / zero trash for the GC" | **ASPIRATIONAL PROSE** | JS string `repeat()` allocates per frame; `texSubImage2D` from an unmeasured pipeline — claims, not receipts |
| 10 | panel-toggle uniform idea; buzz CSV chronology format | **WORTH ADOPTING (fixed)** | GPU-side layout toggle is the right home for that state; `dissonance_continuum.csv` schema adopted for the dissent loop — our hardenized chronologger runs: 5 threshold-crossing rows written, below-threshold tick correctly suppressed (the gate is real, not decorative) |

**Instrument honesty:** gift_lint's GLSL checker itself shipped with a greedy-regex bug (`in` prefix ate the `in` of `int`; the match still succeeded so no backtrack) — caught by the fixed shader failing as a false positive, fixed with word boundaries, re-verified both directions (original FAILs on the real `floatUnpackedBuzz`, fixed PASSES). Instruments converge through their own failures too.

## 2. The real things (what we adopted, hardened, and ran)

- `fixed/affinity_fixed.rs` — dependency-free `extern "C"` pin (no libc crate needed), kernel-verified via `/proc/self/status`, and the gift's cadence **measured** (stdev 9μs, max +90μs over nominal — not 4μs, and now it's a number with provenance).
- `fixed/chrono_logger_fixed.rs` — std-only, `self`, writer **thread** + mpsc (real async decoupling, no runtime to stall), same CSV schema; live receipt: gate suppresses below-threshold ticks.
- `fixed/fragment_fixed.glsl` — undefined identifier fixed, ripple actually wired to the sampler (with the chicken-and-egg honestly documented: per-cell pre-fetch wobble needs a prev-frame texture or vertex-stage pass).
- `gift_lint.py` — the reusable auditor the gift pattern demands: cheapest real check per language (py_compile / node --check / rustc resolve / GLSL identifier audit), verdict table, exit code for CI.

## 3. The receipt rule (fleet-round distilled, typesafe-judged)

Nine-model round on the grounded question ("what minimal contract makes AI-gifted code trustworthy without reading it all?") converged — Inkling, Ling, Qwen, Nemotron, Seed, five phrasings of one rule:

> **No prose claim without a tool-produced artifact that crosses the claimed boundary, re-executable in the reviewer's toolchain, from a dependency-declared bundle.**

Typesafe System One scores the candidate **novelty 1.85 / promote 0.31** and the gift's own "the proof is absolute" **novelty 0.40 / promote 0.07** — the judge separates instrument from fiction, and is honestly lukewarm on the rule's novelty (it is the integration-test ethic, made a gate). Adopted as a candidate tenth law (the **proof law**) pending stranger-verifiable enforcement in CI: gift_lint as the L1 gate under the bitlaw conformance L0 gate.

Fleet receipt: 6/9 parsed (Muse's "parse" was template echo — counted as failure in spirit; 5 real rules), channel mix 5 visible / 3 reasoning-extracted / 1 hard-fail; receipts in `team_round.json`, `judge_board.json`, `audit_results.json`.

## 4. The pattern, named

This is the second gift of this exact shape (the first was the 6,560-line superinstance.md). Signature: correct arithmetic at the bit level + one undeclared-identifier-class bug per language + verification prose describing outputs no code path produces + grand deployment framing. The response that works is always the same three moves: **verify mechanically, keep the convergent parts, name the drift** — and the deepest finding is consistent across both gifts: *the gift re-derives our contract correctly and our contract rejects the gift's packaging*. The law is the thing that survives contact with its own imitators.
