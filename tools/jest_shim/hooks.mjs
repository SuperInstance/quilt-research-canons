import fs from 'node:fs';

export async function resolve(specifier, context, nextResolve) {
  if ((specifier.startsWith('./') || specifier.startsWith('../')) && !/\.[cm]?[jt]sx?$/.test(specifier)) {
    for (const ext of ['.ts', '.tsx', '/index.ts']) {
      try { return await nextResolve(specifier + ext, context); } catch {}
    }
  }
  return nextResolve(specifier, context);
}

// TS + ESM interop repairs, applied to every .ts file:
//  (1) exported types/interfaces get a runtime binding (TS allows `type X` + `const X`);
//  (2) a .ts file that declares exports is forced to ESM, because type-stripping can
//      erase every `export` marker and push Node's syntax detection into CommonJS.
const TYPE_RE = /^[ \t]*(?:export\s+)?(?:declare\s+)?(?:interface|type)\s+([A-Za-z_$][\w$]*)/gm;
const EXPORT_RE = /^[ \t]*export\b/m;
export async function load(url, context, nextLoad) {
  const r = await nextLoad(url, context);
  if (!url.endsWith('.ts') && !url.endsWith('.tsx')) return r;
  let src = r.source && r.source.toString ? r.source.toString() : (r.source ? String(r.source) : '');
  if (!src) return r;
  const hadExports = EXPORT_RE.test(src);
  const names = new Set();
  let m; TYPE_RE.lastIndex = 0;
  while ((m = TYPE_RE.exec(src)) !== null) names.add(m[1]);
  const decls = [...names]
    .filter(n => !new RegExp(`\\b(?:const|let|var|function|class)\\s+${n}\\b`).test(src))
    .map(n => `export const ${n} = undefined;`).join('\n');
  const out = { ...r, source: src + (decls ? '\n' + decls + '\n' : '\n') };
  if (hadExports && String(r.format).includes('commonjs')) out.format = 'module-typescript';
  return out;
}
