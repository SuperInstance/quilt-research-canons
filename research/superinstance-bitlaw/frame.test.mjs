#!/usr/bin/env node
// frame.test.mjs — node conformance for the frame law (superinstance.frame v2).
// Runs the JS codec against the SAME shared vectors the python reference passed.
// Exits 1 on any mismatch. Generated artifacts are never hand-edited.
import { readFileSync } from 'node:fs';
import { tickDelta, forwardWellOrdered, packFrame, parseFrame } from './out/frame.js';

const conf = JSON.parse(readFileSync('./out/frame_conformance.json', 'utf8'));
let fails = 0;

for (const fv of conf.frames) {
  const buf = Buffer.from(fv.hex, 'hex');
  let got;
  try { got = parseFrame(buf); } catch (e) { console.log(`[frame] FAIL ${fv.name}: parse threw ${e.message}`); fails++; continue; }
  if (got.tick !== fv.expect.tick) { console.log(`[frame] FAIL ${fv.name}: tick`); fails++; }
  got.rows.forEach((r, i) => {
    const e = fv.expect.rows[i];
    if (r.rowId !== e.row_id || r.rowTick !== e.row_tick ||
        r.words.length !== e.words.length || r.words.some((w, j) => w !== e.words[j])) {
      console.log(`[frame] FAIL ${fv.name}: row ${i} mismatch`); fails++;
    }
  });
  // round-trip: repack must reproduce the wire bytes
  const repacked = packFrame(got.tick, got.rows.map(r => [r.rowId, r.rowTick, r.words]));
  if (Buffer.compare(buf, repacked) !== 0) { console.log(`[frame] FAIL ${fv.name}: repack bytes differ`); fails++; }
}

for (const d of conf.tick_deltas) {
  const a = parseInt(d.a, 16), b = parseInt(d.b, 16);
  const got = tickDelta(a, b), fwd = forwardWellOrdered(a, b);
  if (got !== d.delta_s32 || fwd !== d.forward) {
    console.log(`[frame] FAIL delta ${d.a}->${d.b}: got ${got}/${fwd}, want ${d.delta_s32}/${d.forward}`); fails++;
  }
}

console.log(`[frame] node: ${conf.frames.length} frame vectors, ${conf.tick_deltas.length} wrap deltas, mismatches: ${fails}`);
process.exit(fails ? 1 : 0);
