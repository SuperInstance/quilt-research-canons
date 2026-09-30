// Rust-side conformance for the generated CellWord (bitlaw).
// Compiled flat: cat out/cellword.rs conformance.rs > conformance_full.rs
//   rustc --edition 2021 conformance_full.rs -o si_conformance_rust && ./si_conformance_rust
// Vectors are embedded by embed_vectors.py (vectors.rs) — no external crates.

include!("vectors.rs");

fn main() {
    let mut fails = 0usize;
    for v in VECTORS.iter() {
        let w = CellWord::pack(v.0, v.1, v.2, v.3, v.4).0;
        if w != v.5 {
            println!("PACK MISMATCH glyph={} route={} weight={} flags={} buzz={} got={} want={}",
                     v.0, v.1, v.2, v.3, v.4, w, v.5);
            fails += 1;
        }
        let (g, r, wt, f, b) = CellWord(v.5).unpack();
        if (g, r, wt, f, b) != (v.0, v.1, v.2, v.3, v.4) {
            println!("UNPACK MISMATCH word={} got=({},{},{},{},{}) want=({},{},{},{},{})",
                     v.5, g, r, wt, f, b, v.0, v.1, v.2, v.3, v.4);
            fails += 1;
        }
    }
    println!("[rust] {} vectors: pack/unpack mismatches: {}", VECTORS.len(), fails);
    std::process::exit(if fails > 0 { 1 } else { 0 });
}
