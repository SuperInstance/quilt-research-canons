// Cross-language conformance: generated JS vs canonical vectors.
// Run: node conformance.test.mjs   (exit 0 = all targets agree)
import { packCellWord, unpackCellWord } from './out/cellword.js';
import { readFileSync } from 'node:fs';

const { vectors } = JSON.parse(readFileSync(new URL('./out/conformance.json', import.meta.url)));

let fails = 0;
for (const v of vectors) {
  const w = packCellWord(v);
  if (w !== (v.word >>> 0)) { console.log(`PACK MISMATCH ${JSON.stringify(v)} -> ${w}`); fails++; }
  const b = unpackCellWord(v.word);
  for (const f of ['glyph', 'route', 'weight', 'flags', 'buzz']) {
    if (b[f] !== v[f]) { console.log(`UNPACK MISMATCH word=${v.word} field=${f} got=${b[f]} want=${v[f]}`); fails++; }
  }
}
console.log(`[node] ${vectors.length} vectors: pack/unpack mismatches: ${fails}`);
process.exit(fails ? 1 : 0);
