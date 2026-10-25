import { runAll } from './shim.mjs';
import { pathToFileURL } from 'node:url';
import fs from 'node:fs';
const dir = process.argv[2];
const files = fs.readdirSync(dir).filter(f => f.endsWith('.test.ts')).sort();
for (const f of files) {
  try { await import(pathToFileURL(`${dir}/${f}`).href); }
  catch (e) { console.log(`IMPORT_ERROR ${f}: ${e && e.message}`); }
}
const r = await runAll();
console.log(`\n=== ${r.pass} passed, ${r.fail} failed, ${r.skip} skipped (${files.length} files) ===`);
for (const f of r.failures) console.log(`FAIL [${f.suite}] ${f.test}\n      ${f.err}`);
process.exit(r.fail ? 1 : 0);
