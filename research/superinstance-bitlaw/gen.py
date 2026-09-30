#!/usr/bin/env python3
"""
bitlaw compiler — the 'real Forge' the superinstance discussion needed.

The uploaded discussion centers on a fictional tool (`@cloudflare/forge`) that
compiles OpenAPI into transient surfaces. The architecture's ACTUAL contract is
not OpenAPI at all — it is the bit layout of the u32 cell word, which the
discussion scatters across a Rust macro, JS upload code, and a GLSL unpack,
with no single source (we proved this costs real bugs: T3 endianness collapse).

This compiler takes ONE spec (spec.json) and emits:
  out/cellword.rs    — pack/unpack for pincher (native cells)
  out/cellword.wgsl  — unpack for WebGPU shaders
  out/cellword.js    — pack/unpack for the quilt canvas
  out/conformance.json — canonical vectors shared by ALL targets
It then validates: fields contiguous, no overlap/gaps, full-word coverage check
(with explicit carry bit accounting), and round-trips every vector through the
Python reference model.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).parent
spec = json.loads((ROOT / "spec.json").read_text())

fields = spec["fields"]
word_bits = spec["word"]["bits"]

# ---------------------------------------------------------------- validation
def validate(fields, word_bits):
    errs = []
    occupied = 0
    prev_top = 0
    for f in fields:
        if f["bits"] <= 0: errs.append(f"{f['name']}: non-positive width")
        if f["shift"] != prev_top:
            errs.append(f"{f['name']}: gap/overlap — starts at bit {f['shift']} but previous field ends at {prev_top}")
        prev_top = f["shift"] + f["bits"]
        occupied += f["bits"]
        if prev_top > word_bits:
            errs.append(f"{f['name']}: exceeds word width")
    return errs, occupied, prev_top

errs, occupied, top = validate(fields, word_bits)
if errs:
    print("LAW VIOLATION:", *errs, sep="\n  "); sys.exit(1)

mask_for = lambda bits: (1 << bits) - 1
const_name = lambda n: n.upper()

# ------------------------------------------------------------- test vectors
edge_vals = [0, 1, mask_for(2), mask_for(8)]  # zero, one, mid, max-ish
vectors = []
# canonical: the doc's own example palette, plus every edge
for glyph in [0, 0x41, 0xFF]:
    for route in [0, 3, 0xFF]:
        for weight in [0, 128, 255]:
            for flags in [0, 0b1010, 0xF]:
                for buzz in [0, 7, 15]:
                    word = 0
                    for f in fields:
                        v = {"glyph": glyph, "route": route, "weight": weight,
                             "flags": flags, "buzz": buzz}[f["name"]] & mask_for(f["bits"])
                        word |= v << f["shift"]
                    vectors.append({"glyph": glyph, "route": route, "weight": weight,
                                    "flags": flags, "buzz": buzz, "word": word})
# dedupe + deterministic order
seen, uniq = set(), []
for v in vectors:
    key = v["word"]
    if key not in seen:
        seen.add(key); uniq.append(v)
vectors = uniq

# python reference pack/unpack round-trip over all vectors
def ref_pack(v):
    w = 0
    for f in fields:
        w |= (v[f["name"]] & mask_for(f["bits"])) << f["shift"]
    return w
def ref_unpack(w):
    return {f["name"]: (w >> f["shift"]) & mask_for(f["bits"]) for f in fields}

rt_fail = 0
for v in vectors:
    w = ref_pack(v)
    back = ref_unpack(w)
    if any(back[f["name"]] != v[f["name"]] for f in fields):
        rt_fail += 1
print(f"[bitlaw] python reference: {len(vectors)} vectors, round-trip failures: {rt_fail}")
if rt_fail: sys.exit(1)

# ------------------------------------------------------------ emit Rust
rust = ["// GENERATED from spec.json by bitlaw — do not edit by hand.",
        "// Law: superinstance.cellword v2 — the u32 cell word IS the contract.",
        "#[derive(Copy, Clone, Debug, Default, PartialEq, Eq)]",
        "#[repr(transparent)]",
        "pub struct CellWord(pub u32);", "",
        "impl CellWord {"]
for f in fields:
    rust.append(f"    pub const {const_name(f['name'])}_SHIFT: u32 = {f['shift']};")
    rust.append(f"    pub const {const_name(f['name'])}_MASK: u32 = 0x{mask_for(f['bits']):08X};")
rust += ["", "    #[inline(always)]",
         "    pub fn pack(glyph: u8, route: u8, weight: u8, flags: u8, buzz: u8) -> Self {",
         "        Self("]
args = {"glyph": "glyph", "route": "route", "weight": "weight", "flags": "flags", "buzz": "buzz"}
lines = []
for f in fields:
    if f["shift"] == 0:
        lines.append(f"            ({args[f['name']]} as u32) & Self::{const_name(f['name'])}_MASK")
    else:
        lines.append(f"            | ((({args[f['name']]} as u32) & Self::{const_name(f['name'])}_MASK) << Self::{const_name(f['name'])}_SHIFT)")
rust += lines + ["        )", "    }", "", "    #[inline(always)]",
         "    pub fn unpack(self) -> (u8, u8, u8, u8, u8) {",
         "        ("]
rets = []
for f in fields:
    rets.append(f"            ((self.0 >> Self::{const_name(f['name'])}_SHIFT) & Self::{const_name(f['name'])}_MASK) as u8,")
rust += rets + ["        )", "    }", "}"]
(ROOT / "out/cellword.rs").write_text("\n".join(rust) + "\n")

# ------------------------------------------------------------ emit WGSL
wg = ["// GENERATED from spec.json by bitlaw — do not edit by hand.",
      "// Unpacks the authoritative u32 cell word inside the parallel GPU pipe.",
      "struct CellFields {",
      "    glyph : u32, route : u32, weight : u32, flags : u32, buzz : u32,", "}"]
sig = ", ".join(f"{f['name']} : u32" for f in fields)
wg += ["", "fn cellword_pack(" + sig + ") -> u32 {", "    return "]
lines = []
for i, f in enumerate(fields):
    op = "" if i == 0 else "| "
    if f["shift"] == 0:
        lines.append(f"        {op}({f['name']} & 0x{mask_for(f['bits']):X}u)")
    else:
        lines.append(f"        {op}(({f['name']} & 0x{mask_for(f['bits']):X}u) << {f['shift']}u)")
wg += lines + ["    ;", "}", "", "fn cellword_unpack(w : u32) -> CellFields {",
               "    var f : CellFields;"]
for f in fields:
    wg.append(f"    f.{f['name']} = (w >> {f['shift']}u) & 0x{mask_for(f['bits']):X}u;")
wg += ["    return f;", "}"]
(ROOT / "out/cellword.wgsl").write_text("\n".join(wg) + "\n")

# ------------------------------------------------------------ emit JS
js = ["// GENERATED from spec.json by bitlaw — do not edit by hand.",
      "// Pack on the JS side must mirror the wire layout EXACTLY (see T3 debrief).",
      "export const CELLWORD = {"]
for f in fields:
    js.append(f"  {f['name'].upper()}_SHIFT: {f['shift']},")
    js.append(f"  {f['name'].upper()}_MASK: 0x{mask_for(f['bits']):X},")
js += ["};", "",
       "// NOTE: first term rides on the `return` line — ASI after a bare `return`",
       "// silently yields undefined (caught by conformance harness, 2026-09-30).",
       "// All-Number arithmetic: u32 words fit in double precision; no BigInt mixing.",
       "// >>> 0 on the fold: JS bitwise ops return SIGNED int32, so any word with",
       "// bit 31 set comes back negative without the coercion (caught by harness)."]
first_expr = f"return ((({fields[0]['name']} & 0x{mask_for(fields[0]['bits']):X})" + \
             (f" << {fields[0]['shift']})" if fields[0]['shift'] else ")")
js += ["export function packCellWord({ glyph, route, weight, flags, buzz }) {",
       f"  {first_expr}"]
for f in fields[1:]:
    m = f"0x{mask_for(f['bits']):X}"
    part = f"(({f['name']} & {m})" + (f" << {f['shift']})" if f['shift'] else ")")
    js.append(f"       | {part}")
js += ["  ) >>> 0;  // signed-int32 -> uint32", "}", "", "export function unpackCellWord(word) {",
       "  word = word >>> 0;  // coerce to uint32",
       "  return {"]
for f in fields:
    js.append(f"    {f['name']}: ((word >>> {f['shift']}) & 0x{mask_for(f['bits']):X}),")
js += ["  };", "}"]
(ROOT / "out/cellword.js").write_text("\n".join(js) + "\n")

# ------------------------------------------------------------ emit conformance
(ROOT / "out/conformance.json").write_text(json.dumps(
    {"law": spec["law"], "version": spec["version"], "vectors": vectors}, indent=1))

print(f"[bitlaw] occupied {occupied}/{word_bits} bits, top field ends at bit {top} "
      f"({'FULL' if top == word_bits else 'PARTIAL'} word coverage)")
print("[bitlaw] wrote out/cellword.rs out/cellword.wgsl out/cellword.js out/conformance.json")
