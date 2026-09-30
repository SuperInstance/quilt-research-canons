#!/usr/bin/env python3
"""frame_gen.py — the FRAME law (superinstance.frame v2), sibling of the cell word.

Retires the T2 class permanently (debrief next-step): the discussion's u16 tick
wrapped every 18.2 min at 60fps, the doc's own detector missed one loss at wrap,
and row gates pinned stale rows. v2 fixes it by LAW, not by convention:
  - tick and row_tick are u32, big-endian (all multi-byte ints BE: retires T3 class too)
  - deltas use serial-number arithmetic: d = (b - a) mod 2^32 read as s32;
    forward-well-ordered iff 0 <= d < 2^31
  - shared wrap-boundary vectors across ALL targets (py/js today, rs on demand)

Emits:
  out/frame.py    — pack/parse/tick_delta + self-check against vectors
  out/frame.js    — same contract for the JS quilt canvas
  out/frame_conformance.json — shared vectors (frame hex + expectations + tick deltas)
Exits 1 on any law violation. Generated artifacts are never hand-edited.
"""
import json, pathlib, struct, sys

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

SPEC = {
    "law": "superinstance.frame",
    "version": 2,
    "doc": "Frame envelope for cell-word rows. u32 ticks with serial-number (wrap-safe) "
           "delta arithmetic; all multi-byte integers big-endian. Single source for every target.",
    "header": [{"name": "magic", "bytes": 4, "value": "QUF2"},
               {"name": "version", "bytes": 1, "value": 2},
               {"name": "rows", "bytes": 1},
               {"name": "tick", "bytes": 4, "order": "big-endian"}],
    "row_prefix": [{"name": "row_id", "bytes": 1},
                   {"name": "row_tick", "bytes": 4, "order": "big-endian"},
                   {"name": "count", "bytes": 2, "order": "big-endian"}],
    "row_payload": "count u32 cell words, big-endian",
    "invariants": ["magic === 'QUF2' && version === 2",
                   "tick_delta(a,b) is forward-well-ordered iff 0 <= ((b-a) mod 2^32 as s32) < 2^31",
                   "rows on one frame may carry independent row_tick (per-row tick slots)"],
}

def tick_delta(a: int, b: int) -> int:
    d = (b - a) & 0xFFFFFFFF
    return d - (1 << 32) if d >= (1 << 31) else d

def well_ordered(a: int, b: int) -> bool:
    d = (b - a) & 0xFFFFFFFF
    return 0 <= ((b - a) & 0xFFFFFFFF) < (1 << 31) and tick_delta(a, b) >= 0

def pack_frame(tick: int, rows: list) -> bytes:
    """rows: list of (row_id, row_tick, [words])"""
    assert 0 <= tick < (1 << 32)
    out = bytearray(b"QUF2")
    out.append(2)
    out.append(len(rows))
    out += struct.pack(">I", tick)
    for row_id, row_tick, words in rows:
        out.append(row_id & 0xFF)
        out += struct.pack(">I", row_tick & 0xFFFFFFFF)
        out += struct.pack(">H", len(words))
        for w in words:
            out += struct.pack(">I", w & 0xFFFFFFFF)
    return bytes(out)

def parse_frame(buf: bytes) -> dict:
    if buf[0:4] != b"QUF2":
        raise ValueError("bad magic (endianness or corruption — T3 class guard)")
    version, nrows = buf[4], buf[5]
    if version != 2:
        raise ValueError(f"unsupported frame version {version}")
    tick = struct.unpack(">I", buf[6:10])[0]
    rows, off = [], 10
    for _ in range(nrows):
        row_id = buf[off]
        row_tick = struct.unpack(">I", buf[off + 1:off + 5])[0]
        count = struct.unpack(">H", buf[off + 5:off + 7])[0]
        off += 7
        words = [struct.unpack(">I", buf[off + 4 * i: off + 4 * i + 4])[0] for i in range(count)]
        off += 4 * count
        rows.append({"row_id": row_id, "row_tick": row_tick, "words": words})
    if off != len(buf):
        raise ValueError(f"trailing bytes: {len(buf) - off}")
    return {"tick": tick, "rows": rows}

# ---------------------------------------------------------------- vectors
# canonical frames: two rows; words from the cellword conformance canon
cw = json.loads((ROOT / "out" / "conformance.json").read_text())
canon_words = [v["word"] for v in cw["vectors"][:6]]
frames = []
f1 = pack_frame(1000, [(1, 1000, canon_words[:3]), (2, 1000, canon_words[3:6])])
frames.append({"name": "two-rows-basic", "hex": f1.hex(),
               "expect": {"tick": 1000, "rows": [{"row_id": 1, "row_tick": 1000, "words": canon_words[:3]},
                                                  {"row_id": 2, "row_tick": 1000, "words": canon_words[3:6]}]}})
# wrap-boundary frame: tick one below 2^32, rows straddling the seam
f2 = pack_frame(0xFFFFFFFE, [(1, 0xFFFFFFFF, canon_words[:2]), (2, 0x00000000, canon_words[2:4])])
frames.append({"name": "wrap-boundary", "hex": f2.hex(),
               "expect": {"tick": 0xFFFFFFFE, "rows": [{"row_id": 1, "row_tick": 0xFFFFFFFF, "words": canon_words[:2]},
                                                        {"row_id": 2, "row_tick": 0x00000000, "words": canon_words[2:4]}]}})
# max-tick frame with full payload rows
f3 = pack_frame(0xFFFFFFFF, [(7, 0x80000000, canon_words)])
frames.append({"name": "max-tick-single-row", "hex": f3.hex(),
               "expect": {"tick": 0xFFFFFFFF, "rows": [{"row_id": 7, "row_tick": 0x80000000, "words": canon_words}]}})

deltas = [{"a": "0xFFFFFFFE", "b": "0xFFFFFFFF", "delta_s32": 1, "forward": True},
          {"a": "0xFFFFFFFF", "b": "0x00000000", "delta_s32": 1, "forward": True},
          {"a": "0x7FFFFFFF", "b": "0x80000000", "delta_s32": 1, "forward": True},
          {"a": "0x80000000", "b": "0x7FFFFFFF", "delta_s32": -1, "forward": False},
          {"a": "0x00000000", "b": "0xFFFFFFFF", "delta_s32": -1, "forward": False},
          {"a": "0xFFFFFFF0", "b": "0x00000010", "delta_s32": 32, "forward": True}]

conformance = {"law": SPEC["law"], "version": 2, "frames": frames, "tick_deltas": deltas}
(OUT / "frame_conformance.json").write_text(json.dumps(conformance, indent=1))

# ---------------------------------------------------------------- self-check
fails = 0
for fv in frames:
    got = parse_frame(bytes.fromhex(fv["hex"]))
    if got["tick"] != fv["expect"]["tick"]:
        print(f"[frame] FAIL {fv['name']}: tick {got['tick']} != {fv['expect']['tick']}"); fails += 1
    for gr, er in zip(got["rows"], fv["expect"]["rows"]):
        if gr != er:
            print(f"[frame] FAIL {fv['name']}: row mismatch {gr} != {er}"); fails += 1
for d in deltas:
    a, b = int(d["a"], 16), int(d["b"], 16)
    got = tick_delta(a, b)
    if got != d["delta_s32"] or well_ordered(a, b) != d["forward"]:
        print(f"[frame] FAIL delta {d['a']}->{d['b']}: got {got}, forward={well_ordered(a,b)}, want {d['delta_s32']}/{d['forward']}"); fails += 1
rt = 0
for fv in frames:
    if parse_frame(pack_frame(fv["expect"]["tick"], [(r["row_id"], r["row_tick"], r["words"]) for r in fv["expect"]["rows"]])) != parse_frame(bytes.fromhex(fv["hex"])):
        rt += 1
print(f"[frame] python reference: {len(frames)} frames, {len(deltas)} deltas, failures: {fails + rt}")
if fails + rt:
    sys.exit(1)

# ---------------------------------------------------------------- emit JS
js = ["// GENERATED from the frame law (superinstance.frame v2) — do not edit by hand.",
      "// u32 ticks + serial-number deltas; all multi-byte ints big-endian (T2/T3 class guards).",
      "import { DataView } from 'node:util' /* noop shim for bundlers */;" if False else
      "// Uses DataView; no BigInt mixing (all-Number u32 arithmetic, >>> 0 coercions).",
      "export const FRAME = { MAGIC: [0x51,0x55,0x46,0x32], VERSION: 2 };", "",
      "export function tickDelta(a, b) {",
      "  a = a >>> 0; b = b >>> 0;",
      "  let d = (b - a) & 0xFFFFFFFF;   // already u32 via ToInt32 -> use unsigned compare path",
      "  d = d >>> 0;",
      "  return d >= 0x80000000 ? d - 0x100000000 : d;",
      "}",
      "",
      "export function forwardWellOrdered(a, b) {",
      "  const d = tickDelta(a, b);",
      "  return d >= 0 && d < 0x80000000;",
      "}",
      "",
      "export function packFrame(tick, rows) {",
      "  const parts = [0x51, 0x55, 0x46, 0x32, 2, rows.length,",
      "                 (tick >>> 24) & 0xFF, (tick >>> 16) & 0xFF, (tick >>> 8) & 0xFF, tick & 0xFF];",
      "  for (const [rowId, rowTick, words] of rows) {",
      "    parts.push(rowId & 0xFF,",
      "      (rowTick >>> 24) & 0xFF, (rowTick >>> 16) & 0xFF, (rowTick >>> 8) & 0xFF, rowTick & 0xFF,",
      "      (words.length >>> 8) & 0xFF, words.length & 0xFF);",
      "    for (const w of words) parts.push((w >>> 24) & 0xFF, (w >>> 16) & 0xFF, (w >>> 8) & 0xFF, w & 0xFF);",
      "  }",
      "  return new Uint8Array(parts);",
      "}",
      "",
      "export function parseFrame(buf) {",
      "  const dv = buf instanceof DataView ? buf : new DataView(buf.buffer, buf.byteOffset, buf.byteLength);",
      "  if (dv.getUint8(0) !== 0x51 || dv.getUint8(1) !== 0x55 || dv.getUint8(2) !== 0x46 || dv.getUint8(3) !== 0x32)",
      "    throw new Error('bad magic (endianness or corruption — T3 class guard)');",
      "  const version = dv.getUint8(4);",
      "  if (version !== 2) throw new Error('unsupported frame version ' + version);",
      "  const nrows = dv.getUint8(5);",
      "  const tick = dv.getUint32(6, false);   // big-endian",
      "  let off = 10; const rows = [];",
      "  for (let i = 0; i < nrows; i++) {",
      "    const rowId = dv.getUint8(off);",
      "    const rowTick = dv.getUint32(off + 1, false);",
      "    const count = dv.getUint16(off + 5, false);",
      "    off += 7;",
      "    const words = [];",
      "    for (let j = 0; j < count; j++) { words.push(dv.getUint32(off + 4 * j, false)); }",
      "    off += 4 * count;",
      "    rows.push({ rowId, rowTick, words });",
      "  }",
      "  if (off !== dv.byteLength) throw new Error('trailing bytes: ' + (dv.byteLength - off));",
      "  return { tick, rows };",
      "}"]
(OUT / "frame.js").write_text("\n".join(js) + "\n")

# ---------------------------------------------------------------- emit PY module
pymod = ['"""GENERATED from the frame law (superinstance.frame v2) — do not edit by hand.',
         'u32 ticks + serial-number deltas; all multi-byte ints big-endian (T2/T3 class guards)."""',
         "import struct", "",
         "def tick_delta(a: int, b: int) -> int:",
         "    d = (b - a) & 0xFFFFFFFF",
         "    return d - (1 << 32) if d >= (1 << 31) else d",
         "",
         "def forward_well_ordered(a: int, b: int) -> bool:",
         "    return 0 <= tick_delta(a, b) < (1 << 31)",
         "",
         "def pack_frame(tick: int, rows: list) -> bytes:",
         "    out = bytearray(b'QUF2')",
         "    out.append(2); out.append(len(rows))",
         "    out += struct.pack('>I', tick & 0xFFFFFFFF)",
         "    for row_id, row_tick, words in rows:",
         "        out.append(row_id & 0xFF)",
         "        out += struct.pack('>I', row_tick & 0xFFFFFFFF)",
         "        out += struct.pack('>H', len(words))",
         "        for w in words: out += struct.pack('>I', w & 0xFFFFFFFF)",
         "    return bytes(out)",
         "",
         "def parse_frame(buf: bytes) -> dict:",
         "    if buf[0:4] != b'QUF2': raise ValueError('bad magic (endianness or corruption — T3 class guard)')",
         "    version, nrows = buf[4], buf[5]",
         "    if version != 2: raise ValueError(f'unsupported frame version {version}')",
         "    tick = struct.unpack('>I', buf[6:10])[0]",
         "    rows, off = [], 10",
         "    for _ in range(nrows):",
         "        row_id = buf[off]",
         "        row_tick = struct.unpack('>I', buf[off+1:off+5])[0]",
         "        count = struct.unpack('>H', buf[off+5:off+7])[0]",
         "        off += 7",
         "        words = [struct.unpack('>I', buf[off+4*i:off+4*i+4])[0] for i in range(count)]",
         "        off += 4 * count",
         "        rows.append({'row_id': row_id, 'row_tick': row_tick, 'words': words})",
         "    if off != len(buf): raise ValueError(f'trailing bytes: {len(buf) - off}')",
         "    return {'tick': tick, 'rows': rows}"]
(OUT / "frame.py").write_text("\n".join(pymod) + "\n")

print(f"[frame] wrote out/frame.py out/frame.js out/frame_conformance.json "
      f"({len(frames)} frame vectors, {len(deltas)} wrap deltas)")
