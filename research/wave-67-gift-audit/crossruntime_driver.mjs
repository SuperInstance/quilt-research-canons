
import { readFileSync, writeFileSync } from 'node:fs';
import { parseFrame } from '/home/z/my-project/quilt-research-canons/research/superinstance-bitlaw/out/frame.js';
const frames = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const out = frames.map(f => {
  const pf = parseFrame(Buffer.from(f.hex, 'hex'));
  const w0 = pf.rows[0].words[0];
  const w10 = pf.rows[0].words[10];   // the gift's special cell lives at col 10
  return { tick: pf.tick, row0FirstWord: w0,
           col10: { word: w10, glyph: w10 & 0xFF, route: (w10 >>> 8) & 0xFF,
                    weight: (w10 >>> 16) & 0xFF, flags: (w10 >>> 24) & 0x0F, buzz: (w10 >>> 28) & 0x0F } };
});
writeFileSync(process.argv[3], JSON.stringify(out));
