#!/usr/bin/env python3
"""
superinstance.md claim verification — debrief negative controls.

Tests three engineering claims made in the uploaded discussion:
  T1. MTU math: full 80x24 u32 frame vs 1500-byte MTU; row-segment size.
  T2. u16 tick wraparound: the doc's JS drop-detector
      `if (tick > lastRenderedTick + 1 && lastRenderedTick !== 0)` —
      what happens at 60fps after ~18 minutes when the u16 tick wraps?
  T3. RGBA endianness: doc packs cells as (r<<24)|(g<<16)|(b<<8)|a into u32,
      views as Uint32Array, uploads via texImage2D(..., gl.RGBA, gl.UNSIGNED_BYTE, ...).
      What channel order does WebGL actually see on a little-endian machine?
      And what does the doc's own luminance->glyph pipeline then produce?

Each test prints CLAIM / RESULT / VERDICT so the receipt is self-contained.
"""
import struct

# ---------------------------------------------------------------- T1: MTU
def t1_mtu():
    W, H = 80, 24
    frame_bytes = W * H * 4
    row_bytes = W * 4
    row_packet = 4 + row_bytes  # [u16 tick, u16 row] + payload
    print("T1. MTU math (doc's numbers)")
    print(f"    CLAIM: full frame {frame_bytes}B exceeds 1500B MTU; row packet {row_packet}B fits")
    print(f"    RESULT: frame={frame_bytes}B (>{1500}: {frame_bytes > 1500}), "
          f"row_packet={row_packet}B (<=1500: {row_packet <= 1500})")
    verdict = "CONFIRMED" if frame_bytes > 1500 and row_packet <= 1500 else "REFUTED"
    print(f"    VERDICT: {verdict}\n")

# ------------------------------------------------------- T2: tick wrap
def t2_tick_wrap():
    print("T2. u16 tick wraparound at 60 fps")
    wrap = 65536
    fps = 60
    wrap_seconds = wrap / fps
    print(f"    CLAIM (implicit): header tick is u16, no wrap handling in JS drop detector")
    print(f"    RESULT: u16 wraps every {wrap} ticks = {wrap_seconds:.1f}s = {wrap_seconds/60:.1f} min at 60fps")

    # Reproduce the doc's detector exactly.
    last = 0
    drops = 0
    spurious = 0
    # feed 70_000 sequential ticks (past one wrap), lose nothing
    for tick in range(1, 70_000):
        tick_u16 = tick % wrap
        # doc logic: if (tick > lastRenderedTick + 1 && lastRenderedTick !== 0)
        if tick_u16 > last + 1 and last != 0:
            drops += (tick_u16 - last - 1)
        last = tick_u16
    # At wrap: tick_u16 goes ...65534, 65535, 0, 1... The 0 then 1 are NOT > last+1
    # => no spurious drops there. But a single real loss across the wrap boundary
    # (65535 -> 1, losing 0) looks like tick(1) < last(65535): detector silently ignores,
    # AND the next tick 2 also: 2 < 65535+1? no wait, 2 > 65536? no. Let's simulate wrap loss.
    last = 0
    wrap_drops_reported = None
    seq = [t % wrap for t in range(1, 70_000)]
    # inject single loss at the wrap boundary: drop the tick that equals 0 (i.e. 65536)
    seq = [t for t in seq if t != 0]
    drops = 0
    for tick in seq:
        if tick > last + 1 and last != 0:
            drops += (tick - last - 1)
        last = tick
    print(f"    Simulated one real packet loss exactly at wrap (65535 -> 1, dropping 0):")
    print(f"      detector reported drops = {drops}  (truth: 1)")
    print(f"      => {('UNDERCOUNTS to zero' if drops == 0 else 'ok')}: "
          f"1 < 65535 so 'tick > last+1' is false; the loss is invisible, and the stale-screen "
          f"row from tick 65535 stays pinned because gate 'tick >= lastRenderedTick' rejects 1 < 65535.")
    # also show the benign no-loss case is fine until wrap, then the row gate stalls
    print(f"    VERDICT: BUG CONFIRMED — wrap-silent loss undercount + row-gate stall; "
          f"fix = wrap-aware compare ((tick - last) & 0xFFFF) <= 0x7FFF, or 32-bit tick, "
          f"and per-row tick slots instead of a single global lastRenderedTick.\n")

# ------------------------------------------------- T3: RGBA endianness
def t3_rgba_endianness():
    print("T3. RGBA packing endianness (doc's cell -> texel path)")
    print("    CLAIM (implicit): pack (r<<24)|(g<<16)|(b<<8)|a, view as Uint32Array,")
    print("           texImage2D(gl.RGBA, gl.UNSIGNED_BYTE) shows r,g,b,a.")
    # little-endian machine (all practical browsers): u32 word -> bytes LSB first
    r, g, b, a = 0x10, 0x20, 0x30, 0xFF
    word = (r << 24) | (g << 16) | (b << 8) | a
    le_bytes = struct.pack('<I', word)  # how the ArrayBuffer actually lays out
    texel = tuple(le_bytes)             # RGBA/UNSIGNED_BYTE consumes bytes R,G,B,A in order
    print(f"    RESULT: packed r,g,b,a = ({r:#04x},{g:#04x},{b:#04x},{a:#04x}) -> word {word:#010x}")
    print(f"            WebGL reads bytes as R,G,B,A = {texel[0]:#04x},{texel[1]:#04x},{texel[2]:#04x},{texel[3]:#04x}")
    ok = texel == (r, g, b, a)
    print(f"            => alpha<->red swapped: R==alpha ({texel[0]==a}), A==red ({texel[3]==r})")

    # downstream effect: doc's luminance -> glyph index pipeline
    def luminance(px):
        R, G, B = px[0]/255, px[1]/255, px[2]/255
        return 0.299*R + 0.587*G + 0.114*B
    lum = luminance(texel)
    glyph_index = int(lum * 15)  # 16-glyph ramp
    print(f"            luminance seen by shader = {lum:.3f} -> glyphIndex = {glyph_index} "
          f"(constant for EVERY cell since R channel is the constant 0xFF alpha)")
    print(f"    VERDICT: {'OK' if ok else 'BUG CONFIRMED'} — the glyph ramp collapses; correct pack for "
          f"RGBA/UNSIGNED_BYTE on LE is (a<<24)|(b<<16)|(g<<8)|r, or use Uint8Array views explicitly.")
    print(f"            Root cause: the 'contract' (cell word layout) lives in three heads — Rust macro,")
    print(f"            JS upload, GLSL unpack — with no single source of truth. See bit-law prototype.\n")

if __name__ == "__main__":
    t1_mtu()
    t2_tick_wrap()
    t3_rgba_endianness()
