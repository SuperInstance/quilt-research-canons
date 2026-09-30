// GENERATED from spec.json by bitlaw — do not edit by hand.
// Unpacks the authoritative u32 cell word inside the parallel GPU pipe.
struct CellFields {
    glyph : u32, route : u32, weight : u32, flags : u32, buzz : u32,
}

fn cellword_pack(glyph : u32, route : u32, weight : u32, flags : u32, buzz : u32) -> u32 {
    return 
        (glyph & 0xFFu)
        | ((route & 0xFFu) << 8u)
        | ((weight & 0xFFu) << 16u)
        | ((flags & 0xFu) << 24u)
        | ((buzz & 0xFu) << 28u)
    ;
}

fn cellword_unpack(w : u32) -> CellFields {
    var f : CellFields;
    f.glyph = (w >> 0u) & 0xFFu;
    f.route = (w >> 8u) & 0xFFu;
    f.weight = (w >> 16u) & 0xFFu;
    f.flags = (w >> 24u) & 0xFu;
    f.buzz = (w >> 28u) & 0xFu;
    return f;
}
