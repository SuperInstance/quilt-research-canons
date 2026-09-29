# Lane U — Three repos, one collision: does anyone have a per-cell MODE MENU?

**Scout:** snowball-scout · **Date:** 2026-09-29 · **Read-only.** Nothing was written to any of the three repos.

## The specific question, answered first

> A per-cell choice among `{literal, delta, skip, coarse}` **where the mode itself is transmitted**, as opposed to a per-cell coarse-to-fine **pyramid** (resolution budget, no choice of *how* to describe the cell).

### Verdict: **NO. None of the three implements or plans a per-cell mode menu.** This is a negative result, and it is a clean one.

I searched all three trees for the full vocabulary — `mode`, `menu`, `skip`, `delta`, `coarse`, `literal`, `pyramid`, `quantiz`, `residual`, `entropy`, `opcode`, `predict`, `temporal` — in every source, doc, and (for Syzygy) the 9,535-line seed blob. The three repos sit in three *different* places relative to the question, and none of them is in it:

| repo | has a **pyramid**? | has a **transmitted mode**? | is the mode a **bit-cost** choice? | has **SKIP**? |
|---|---|---|---|---|
| **Syzygy** | no | no | — | no (and cannot: see below) |
| **qthe-codec** | no | **yes — but 2-way, and not bit-cost** | no | no |
| **glyphcast** | **yes, explicitly** | no | — | no |

**The one that looks closest is qthe-codec, and it is worth being precise about why it is not the thing.** `qthe_codec.py` implements a per-cell escape: each cell carries a 2-bit marker selecting *which of two 64-symbol charsets* its 6 data bits index. That is genuinely a transmitted per-cell mode, and it is the only one in any of the three repos. But both modes cost exactly one byte. The menu does not choose *how much* to say, only *in which alphabet* to say it. There is no mode cheaper than a full byte, so there is nothing for the encoder to trade against, and `SKIP` — the specific capability at stake — is absent.

**The one that looks most like the question is glyphcast, and it is the exact opposite architecture.** Its README and Phase 1 both specify a **coarse-to-fine pyramid**: *"12×9 semantics → 48×36 glyph field → optional 96×72 detail."* That is precisely the "how much to spend" axis the question distinguishes itself from. It is also a **per-frame** ladder at three fixed resolutions, not a per-cell choice. glyphcast has a pyramid where the question asked about a menu. That is a real collision between these two designs, and it is the most interesting thing in this lane.

---

## Per-repo findings

### 1. SuperInstance/Syzygy — **ABSENT**, and structurally precluded

- **SHA read:** `e6c5b53bd9f0d5fd0aa889e33800633fad0f40d5` (Mon Sep 28 22:15:16 2026, "syzygy: land shard 0008 crdt-mesh (HEWN)")
- **Files read:** `include/syz_fused.h`, `syz_glyph.h`, `syz_fft.h`, `syz_braille.h`, `syz_arena.h`, `syz_crdt.h`, `syz_yuv.h`, `syz_ste.h`; `README.md`, `docs/marks/ARCHITECTURE.md`, `docs/marks/0005-fused.md`, `0008-crdt-mesh.md`, `docs/marks/ledger.csv`, `docs/seed/blob.md`
- **Mode/menu:** ❌ **absent.** Zero hits for `mode`/`menu`/`skip`/`coarse`/`pyramid`/`quantiz`/`residual` in any of the 8 headers, 7 test files, or 12 mark docs. Every hit in the tree is an unrelated word: `delta` as an FFT loop stride, `"literal"` in `"the seed's literal dY/dX"`.

**The lines that settle it:**

1. **Every cell is written literally, into three parallel planes, every frame.** `include/syz_fused.h:69-78`:
   ```c
   typedef struct {
       uint32_t cols, rows;
       size_t   cap;
       uint8_t  *mask;         /* cols*rows Braille masks (0001) */
       uint32_t *glyph;        /* cols*rows glyph scalars (0003) */
       uint8_t  *tone;         /* cols*rows STE ramp chars */
       int32_t  spec_re[16], spec_im[16];
   ```
   The cell loop at `syz_fused.h:116-137` stores `mask[ci]`, `glyph[ci]`, `tone[ci]` unconditionally for every `(cx,cy)`. There is no branch on content that suppresses a write, and no mode field to tell a decoder how to read it.

2. **The decoder-facing CRDT explicitly disclaims delta coding — twice.**
   `include/syz_crdt.h:16-17`:
   > `SHORTCUT : Pure algebra, in memory. State-based (whole-cell) merge only; **no delta encoding**, no wire packet, no UDP (next shard).`
   `docs/marks/0008-crdt-mesh.md`, SHORTCUT:
   > "Whole-cell state-based merge (**no deltas**)."

3. **The fused pass is stateless across time — this is the decisive one.** `syz_fused.h:102`:
   ```c
   static inline int syz_fused(SyzArena *a, const SyzNv12 *src,
                               const SyzFusedParams *p, SyzFusedOut *out)
   ```
   I grepped `include/` and `tests/` for `prev|prior|last_?frame|carry|stateful` — **no temporal state exists anywhere in the repo**. The function never sees frame *t-1*. `DELTA` and `SKIP` are *temporal* modes; they are literally undefined in this kernel. A mode menu here is not an edit, it is a new invariant.

4. **The closest near-miss is `syz_glyph_select` — and it is a content menu, not a bit-cost menu.** `include/syz_glyph.h:98-106` picks a directional glyph on a strong edge, else a tone-ramp char. That is a genuine per-cell branch — but (a) it is chosen by the *image*, never *transmitted*, so a decoder must recompute it rather than read it; (b) both branches write a full `uint32_t` into `glyph[]`, so it saves nothing on the wire; (c) it selects a *character*, not a *description strategy*. This is a selector, not a menu.

- **Frame/stream model:** **per-frame**, and per-*shard* in the build sense (0001…0008 are build units, not time units). One `syz_fused` call = one frame; scratch is reclaimed by `syz_arena_mark`/`rollback`. The 16-pt FFT window is **one cell row, first 16 cells only** (`syz_fused.h:28-29`, `135`) — so the spectral path covers 16 cells of a whole frame, not a time series. Syzygy is currently a *spatial* codec with a decorative spectral tap, not a temporal codec.
- **Actual compression mechanism:** **none, in the entropy-coding sense.** It is a *quantizer*: per-cell luminance → 1-bit Braille threshold into an 8-bit mask (`syz_braille_pack`); Sobel → 4-way quantized direction or 10-step ramp (`syz_glyph_select`); int64 dot-product argmax over a hardcoded `[4][4]` basis → ramp index (`syz_fused_tone` → `syz_ste_select4`); plus a 16-pt Q14 fixed-point FFT. The lossiness is doing the compressing; the byte layer is uncompressed literals. Confirmed: `syz_braille_utf8` serializes a codepoint to exactly 3 bytes and has no skip path.
- **Maturity:** **shipped, tested, and the best-verified of the three.** `sh tests/run.sh` → **201 checks, 0 failures** across 7 suites (braille 31, arena 29, fft 15, yuv 31, fused 43, ste 24, crdt 28). I ran it. The keystone receipt is real: `tests/test_fused.c` proves `fused == composed` byte-identical on 5 frames, with a pinned FNV-1a golden `0x6dbdd1a8` that matches at both `-O0` and `-O2`.

**README vs code (two disagreements, both in the honest direction):**
- The README status table still marks 0002/0004/0005/0006/0007 **DRAWN** and says *"Expect `=== 31 checks, 0 failures ===`. That is the whole current claim."* Reality: all eight shards are **HEWN** per `ledger.csv` and the suite is **201 checks**. The README understates the work.
- The README architecture diagram lists *"1. 3x3 spatial convolution (fixed-point / SIMD)"* as a stage of the fused pass. `syz_fused.h:45-46` says the opposite: *"the 3x3 convolution is **dropped**: the 0004 luma is the source."* The README advertises a stage the code deliberately removed.
- A *third*, cosmetic: `test_fused` and `test_ste` print their banner as `test_fused: 43 checks` rather than the `=== 43 checks ===` used by the other five suites, so naive tallying of `===` banners undercounts by 67. The ledger's 201 is correct; I only mention it because it briefly looked like a missing keystone test and wasn't.

---

### 2. SuperInstance/qthe-codec — **PARTIAL: a transmitted 2-way escape exists; a bit-cost menu and SKIP do not**

- **SHA read:** `aba5b84f747b463d24345d192fcb7c0299c699a0` (Sun Sep 27 21:44:51 2026, "examples/4_tone_embedding: falsify 'embedder = tone fingerprint' claim")
- **Files read:** `qthe_codec.py` (226), `qthe_compiler.py` (185), `qthe_embedder.py` (123), `qthe_transformer.py` (128), `README.md`, `docs/VISION.md`, `examples/4_tone_embedding/HOW_IT_WORKS.md`
- **Mode/menu:** ⚠️ **partial.** A transmitted per-cell mode exists in `qthe_codec.py` and is *not* wired into the compiler. It is a 2-way alphabet selector with no bit-cost gradient and no `SKIP`.

**The lines that settle it:**

1. **The per-cell escape — the only transmitted per-cell mode in any of the three repos.** `qthe_codec.py:157-188`:
   ```python
   # ── the 7th bit: the abstain state as an ESCAPE hatch (Casey, 2026-09-27) ─
   # ...when a cell is in ABSTAIN (timbre=3, "no hidden information"), its 6 data
   # bits stop being a base symbol and instead index a SECOND 64-symbol charset.
   # ...You trade tone for alphabet, one cell at a time.
   def data_encode_full(text: str) -> list[tuple[int, int]]:
       out = []
       for ch in text:
           if ch in SYM_TO_IDX:
               out.append((SYM_TO_IDX[ch], 0))     # mode 0: base plane
           elif ch in RARE_TO_IDX:
               out.append((RARE_TO_IDX[ch], 3))    # mode 3: rare plane
   ```
   This is a real, working, per-cell, transmitted mode — `out` is a list of `(data, mode)` pairs and `data_decode_full` branches on the mode per cell. **Why it is not the menu:** it is a *charset* choice, not a *description-cost* choice. Both branches emit one cell of one byte. Nothing is cheaper. There is no `skip`, no `delta`, no `coarse`, and no notion of paying for the choice.

2. **The escape is dead code with respect to the compiler.** `qthe_compiler.compile()` (`qthe_compiler.py:62-80`) takes a raw byte stream and does `data = [b & 0x3F for b in stream]` — it cannot represent a two-plane stream at all. I grepped every caller: `data_encode_full` has **zero call sites** outside its own definition; the compiler and all four examples use plain `data_encode`. So the one menu-shaped thing in the repo is not on the wire path.

3. **The RLE is a per-RUN implicit length prefix, and the compress/verbatim choice is made once per *plane*, not per cell.** `qthe_compiler.py:36-50`:
   ```python
   def _rle_encode(values: list[int]) -> bytes:
       """...Each run: (count<<2 | value) as one byte, count in 1..64."""
   ```
   and `qthe_compiler.py:9-13`:
   > "the compiler separates the two planes and RUN-LENGTH-ENCODES the timbre plane (the tone) while keeping the data plane (the text) verbatim."

   The data plane is packed 4-tokens-per-3-bytes (`_pack6`); the momentum plane is RLE'd. **The mode is chosen once for the entire message**, at plane granularity. That is a 1-bit menu with two settings, applied globally. Making it per-cell is exactly the generalization the question is asking about — and it has not been made.

4. **Honest, and it matters for the recommendation: the compiler currently makes short messages BIGGER.** I ran it. `QTC1` costs **17 fixed bytes** (magic 4 + width 1 + 2×length 4 + crc 4) before any payload:
   - `"I love you"` → raw 12 B → compiled 29 B (**2.42× expansion**)
   - 73-char text → raw 74 B → compiled 78 B (**1.05× expansion**)

   The *signal* compresses hard — decoded-momentum RLE alone hits **0.25×** and **0.054×** — but the container eats the entire gain. This is the textbook motivation for a mode menu, and it is *measured inside the repo's own code*.

- **Frame/stream model:** **per-token, per-message.** There are no frames or ticks; the atom is one 6-bit data token + 2-bit timbre = 1 byte, with `EOS` as terminator. RLE runs are capped at 64 cells and split beyond that (`qthe_compiler.py:45`). A "cell" here is a character, not a space.
- **Actual compression mechanism:** **RLE (run-length) on one plane + 6-bit bit-packing on the other + CRC32.** No entropy coder, no dictionary, no delta, no prediction, nothing learned. `zlib` is used for `crc32` only — not for compression. The "embedder" is 4 hand-written deterministic feature families (histogram / 3-segment arc / max-run / sign-flip spectral) → L2-normalized vector; it is **not** learned and does not participate in coding.
- **Maturity:** **shipped reference modules, but with a real defect.** `qthe_codec.py` runs clean. `qthe_compiler.py`'s core functions work — roundtrip passes and corruption is detected — but **the module's own `__main__` self-test crashes**:
  ```
  $ python3 qthe_compiler.py
  corruption detected: checksum mismatch — stream corrupted
  raw 12 -> compiled 30 bytes (ratio 2.5)
  KeyError: 'timbre_raw_bytes'      # qthe_compiler.py:183
  ```
  `compression_ratio()` returns `wire_timbre_rle_bytes` / `momentum_rle_bytes`; line 183 asks for `timbre_raw_bytes` / `timbre_rle_bytes`. The README's "✅ pack+RLE+checksum, corruption-detecting" is true of the *functions* and unverified by running the module. Trivial fix; worth reporting because this repo's credibility rests on being runnable.
- **The falsification culture is real and is this repo's main asset.** `examples/4_tone_embedding/HOW_IT_WORKS.md` reports its own negative result with numbers — max cross-tone cosine **0.9696** (coy vs wink) against a noise floor of **0.8386** — and ships a demo that **exits 1 deliberately**: *"Verdict: FALSIFIED — and the failure is diagnostic, not accidental."* `docs/VISION.md` gives each of three layers a KILLable first experiment with a numeric threshold. Any proposal here will be tested rather than accepted on assertion, which is exactly the right home for a risky new coding mode.

---

### 3. SuperInstance/glyphcast — **ABSENT, and it is the only one that has the PYRAMID**

- **SHA read:** `1493eba5c6075df8e5a31fb11619cc96fd2beb4b` (Tue Sep 29 01:46:21 2026, "glyphcast: receipt-gated roadmap (Phases 0-4, FAIL-first pins)"). Repo has **2 commits total** and **2 files**: `README.md`, `docs/ROADMAP.md`. No code, no tests, no `pyproject.toml` (the README's `pip install -e .` quickstart has nothing to install).
- **Mode/menu:** ❌ **absent.** But ❗**the pyramid is there, explicitly, in both files** — and it is the alternative the question is contrasting against.

**The lines that settle it:**

1. **The pyramid, in the README.** `README.md`, "The three jobs" #1:
   > "**Project** the next grid from recent grids + the event sidecar (`predict`). **Coarse-to-fine: semantics first (what, where, moving how), texture second, detail third** — resolution flows to wherever the bandwidth moment needs it."

2. **The pyramid, made concrete and per-cell, in the roadmap.** `docs/ROADMAP.md`, Phase 1:
   > "**Coarse-to-fine heads: 12×9 semantics → 48×36 glyph field → optional 96×72 detail. Cross-entropy per cell from day one; no regression heads.**"

   Read this carefully: there **is** per-cell structure — *every cell gets a full categorical distribution, at three resolutions*. What is missing is exactly the menu. A cell is scored at 12×9, again at 48×36, again at 96×72. It does not get to say "I'm unchanged" or "send me a delta" or "I'm blank." The three heads are three *whole-frame* passes; there is no per-cell switch between them, and no field to carry such a switch.

3. **The three modes already exist — as whole-model baseline arms.** `docs/ROADMAP.md`, Phase 1:
   > "Baseline arms, per fleet doctrine: (a) **persistence** (repeat last grid), (b) **per-cell flow extrapolation** (no learned weights), (c) **the tiny transformer**. Every claim compares against all three."

   This is the finding I would most want the fleet to see. `(a) persistence` ≈ **SKIP**. `(b) per-cell flow extrapolation` ≈ **DELTA**. `(c) the transformer` ≈ **LITERAL**. The three arms of the `{literal, delta, skip, coarse}` menu **are already specified in this repo** — as three *models*, selected globally for the whole benchmark. A per-cell mode menu is precisely the move from "choose one arm for the whole benchmark" to "let the trained model choose among its own arms per cell." The design is 90% present; it just has not been made per-cell.

4. **A fourth channel exists and is orthogonal.** Phase 0 specifies a **sidecar**: a discrete event stream *"to announce births, deaths, flips, crossings — because exp002 measured that discrete events do not cross a glyph stream unless the producer announces them."* This is a genuine second, sparse stream riding alongside the grid. It is the most natural host for a `SKIP`-class signal (an announced unchanged region), but as written it announces *semantic events*, not *encoding modes*.

- **Frame/stream model:** **per-frame on a fixed cell lattice**, with a JEV-shaped discrete sidecar per frame. Frame headers carry an engine version hash for determinism. Phase 3 adds in-betweens at the same lattice (glyph-RIFE). This is the only one of the three repos whose *unit of work is a frame over a spatial grid over time* — i.e. the only one where `{literal, delta, skip, coarse}` is even a well-posed question.
- **Actual compression mechanism:** **none — not built.** The planned mechanism is learned next-grid cross-entropy prediction (small transformer, "a few-million-parameter", QLoRA-adjacent scale, scheduled sampling) plus flow-guided palette sampling for in-betweens. Persistence and flow extrapolation are the no-learning baselines. Nothing is implemented; the README says so plainly: *"**Proposal stage.** No model weights exist yet."*
- **Maturity:** **roadmap prose only.** And the prose is unusually disciplined about it: *"Everything in this repo that describes **results** is labeled as measured, simulated, or wagered"*, and the standing rules include *"**FAIL-first: every gate's pins must FAIL on the pre-change tree and PASS after, or the gate is theater**"* and *"Numbers carry denominators: 'crossed 4/8', never 'crosses'."* The `docs/ARCHITECTURE.md` and `docs/DEVELOPER-GUIDE.md` referenced by the module map **do not exist in the repo**.

---

## Summary table

| | **Syzygy** | **qthe-codec** | **glyphcast** |
|---|---|---|---|
| **SHA** | `e6c5b53` | `aba5b84` | `1493eba` |
| **Mode menu** | ❌ absent | ⚠️ 2-way alphabet escape, not bit-cost, not on the wire path | ❌ absent — **has a pyramid instead** |
| **Pyramid** | ❌ | ❌ | ✅ 12×9 → 48×36 → 96×72, per-cell x-entropy |
| **`SKIP` exists?** | ❌ (structurally impossible — stateless) | ❌ | ⚠️ as whole-model arm (a) persistence |
| **Mode transmitted?** | n/a | ✅ timbre bits, 2 values | n/a |
| **Unit** | per-frame (2×4-px cell), per-shard | per-token (1 char = 1 byte) | per-frame grid + sidecar |
| **Temporal state** | ❌ **none anywhere** | message-local runs (≤64) | ✅ recent grids + sidecar |
| **Mechanism** | quantizer (Braille/Sobel/argmax) + 16-pt Q14 FFT; **no entropy coding** | RLE (1 plane) + 6-bit pack (1 plane) + CRC32; **no prediction** | planned learned next-grid x-entropy; **unbuilt** |
| **Maturity** | ✅ shipped, **201 checks 0 fail** (I ran it) | ⚠️ shipped w/ a `KeyError` in the compiler self-test | ❌ roadmap only, 2 files |
| **Where a menu would go** | ❌ wrong layer, breaks I1/I2 | ✅ cheapest prototype | ✅ design of record |

---

## WHERE SHOULD A MODE MENU LAND?

**Recommendation: land it in glyphcast as a Phase 1 gate, and prototype it in qthe-codec first. Do not put it in Syzygy.**

### Why glyphcast is the design of record

It is the only repo whose question is *a stream over time on a cell lattice* — the only domain where `{literal, delta, skip, coarse}` is well-posed rather than decorative. And it already contains the menu's entire vocabulary as three whole-model baseline arms: **persistence = SKIP**, **per-cell flow extrapolation = DELTA**, **the tiny transformer = LITERAL**. The gap is not conceptual, it is one axis of generalization: these are currently selected once per benchmark; a menu makes the selection per cell. The 3-head coarse-to-fine pyramid is the *other* axis — how much resolution — and the two compose without conflict. A cell that `SKIP`s at 48×36 and a cell that goes full 96×72 are both well-defined.

Critically, the menu is **falsifiable in their own format**, which is the strongest argument for it. The Phase 1 gate receipt is already "held-out next-grid accuracy per palette class, per engine preset." Add one column: *per-cell mode selection vs. the best single fixed mode, with a denominator.* If per-cell selection does not beat the best arm, the menu is dead and the fleet has spent a phase. If it does, the number is the receipt. That is a question this repo's doctrine is built to answer, and it is the one repo here that would actually answer it.

**One caveat that must be honored:** glyphcast's standing rule is *FAIL-first — every gate's pins must FAIL on the pre-change tree and PASS after, or the gate is theater.* A mode menu slipped in without a failing pin violates their own constitution. It has to arrive as a **gate**, with the falsification written before the implementation.

### Why qthe-codec is where to prototype it

qthe has the two things a prototype needs and neither of the other repos has together: **a transmitted per-cell mode field that already works** (`data_encode_full`'s 2-bit marker), and **a culture that kills its own claims with numbers** (example 4 ships a falsification and exits 1). Going from 2 modes to 4 — `base`/`rare` → `literal`/`delta`/`skip`/`coarse` — is an extension of a field that is already transmitted, not a new channel. And there is a measured reason to want `SKIP` *today*: the compiler's own numbers show a 17-byte fixed container that **expands** messages by 1.05×–2.42× while the real signal sits at 0.05×–0.25×. A per-cell `SKIP` is the obvious cure for a codec that currently pays RLE unconditionally on messages with no runs. Fix the `KeyError` at `qthe_compiler.py:183` first, and wire `data_encode_full` into `compile()` so the mode field is actually on the wire — the escape hatch is currently dead code.

**Cost: roughly a day.** No camera, no arena invariants, no CRDT algebra, no model weights. A falsifiable pin is writable in an afternoon, and this repo will run it.

### Why Syzygy is the wrong home — three reasons from the code, not the philosophy

1. **It cannot express the mode.** `syz_fused` is stateless across time — no `prev`/`prior`/`last_frame` anywhere in `include/` or `tests/`. `DELTA` and `SKIP` are temporal modes; they are *undefined* without frame *t-1*. Adding a menu means adding history to a kernel whose entire architecture is one read, one write, with per-frame `syz_arena_mark`/`rollback` (I1) and register-residency (I2). That is a change to the invariants, not to the code.
2. **It would break the keystone receipt.** `tests/test_fused.c` proves `fused == composed` byte-identical across 5 frames, pinned by FNV-1a `0x6dbdd1a8` at `-O0` and `-O2`. A temporal mode makes the fused output depend on a history the composed reference path does not have — the equality that earns invariant I2 would no longer hold, and the repo would lose its strongest evidence.
3. **Delta mode is in direct conflict with the CRDT's algebra.** `syz_crdt.h:17` already resolved this once, explicitly: *"State-based (whole-cell) merge only; **no delta encoding**."* The join must be idempotent, commutative, and associative; deltas do not commute. Reopening it means re-deriving the semilattice and re-validating 40,000-triple law tests and 6-replica convergence. The repo chose whole-cell LWW for a reason, and the reason is written down.

**And the layering point, which is the real one:** Syzygy is an *encoder* — sensor bytes in, quantized cells out. It has a *serializer* (`syz_braille_utf8`: codepoint → exactly 3 bytes) but no *codec*: nothing in it ever decides **whether** to send 3 bytes, 0 bytes, or 1 delta byte. A mode menu is a codec concern. Putting it in the encoder is the layering error. The wire it would have to carry it does not exist yet — 0009 is specified as a fixed `[seq | bins | cells...]` layout with 12-byte or 4-byte cells and no mode field.

**What Syzygy *should* do, cheaply and as a prerequisite:** stop writing 4 bytes per cell for a scalar that is always ≤ 0x28FF. `SyzFusedOut.glyph` is `uint32_t *` (`syz_fused.h:73`) holding a Unicode scalar in `U+0020..U+2572` — 2 bytes is always enough, 1 byte for the ramp branch. That is a genuine ~2× reduction on the largest plane, it is *not* a mode menu, and it does not touch the fused loop's shape. Fold it into 0009 when the wire format lands. `SyzCell` even has a spare `code` byte where a mode field would eventually fit — but by then it should be **importing** a spec, not inventing one.

### The one-line version

**glyphcast owns the question and has the pyramid where the menu should be; qthe-codec has the transmitted mode field and the culture to falsify it cheaply; Syzygy is a stateless single-pass quantizer whose invariants forbid it. Prototype in qthe, specify in glyphcast, and let Syzygy consume the spec when its wire exists.**

---

## Method and honesty notes

- All three repos cloned read-only to `/tmp/scout-{syzygy,qthe,glyphcast}/`; **nothing was written to any of them**. No PRs, no issues, no pushes.
- SHAs pinned above are the exact commits read; glyphcast has only 2 commits in total, so `1493eba` is its HEAD and final state.
- Every negative claim ("absent") is backed by an exhaustive vocabulary grep across all source, all docs, and — for Syzygy — the 9,535-line `docs/seed/blob.md`, not by reading the README and concluding.
- Where a README claim and the code disagree, both are reported (§Syzygy: two disagreements; §qthe: a crash in the module the README marks ✅). Syzygy's README **understates** its own maturity; glyphcast's roadmap is candid that it has no code; qthe's is accurate about its functions but unverified at the module level.
- **I was wrong once mid-investigation and corrected it:** the Syzygy suite appeared to total 134, not the ledger's 201, because `test_fused`/`test_ste` print a different banner format. Both run fully green; 201 is correct. Flagged above so a verifier doesn't repeat the false alarm.
- Compression ratios in §qthe were measured by running the code in this sandbox, not quoted from the docs.
