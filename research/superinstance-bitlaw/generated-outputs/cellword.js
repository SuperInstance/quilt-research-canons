// GENERATED from spec.json by bitlaw — do not edit by hand.
// Pack on the JS side must mirror the wire layout EXACTLY (see T3 debrief).
export const CELLWORD = {
  GLYPH_SHIFT: 0,
  GLYPH_MASK: 0xFF,
  ROUTE_SHIFT: 8,
  ROUTE_MASK: 0xFF,
  WEIGHT_SHIFT: 16,
  WEIGHT_MASK: 0xFF,
  FLAGS_SHIFT: 24,
  FLAGS_MASK: 0xF,
  BUZZ_SHIFT: 28,
  BUZZ_MASK: 0xF,
};

// NOTE: first term rides on the `return` line — ASI after a bare `return`
// silently yields undefined (caught by conformance harness, 2026-09-30).
// All-Number arithmetic: u32 words fit in double precision; no BigInt mixing.
// >>> 0 on the fold: JS bitwise ops return SIGNED int32, so any word with
// bit 31 set comes back negative without the coercion (caught by harness).
export function packCellWord({ glyph, route, weight, flags, buzz }) {
  return (((glyph & 0xFF))
       | ((route & 0xFF) << 8)
       | ((weight & 0xFF) << 16)
       | ((flags & 0xF) << 24)
       | ((buzz & 0xF) << 28)
  ) >>> 0;  // signed-int32 -> uint32
}

export function unpackCellWord(word) {
  word = word >>> 0;  // coerce to uint32
  return {
    glyph: ((word >>> 0) & 0xFF),
    route: ((word >>> 8) & 0xFF),
    weight: ((word >>> 16) & 0xFF),
    flags: ((word >>> 24) & 0xF),
    buzz: ((word >>> 28) & 0xF),
  };
}
