// Minimal Jest-compatible harness (independent of jest itself).
const state = { suites: [], cur: null, results: [], rootBeforeAll: [], rootAfterAll: [] };
function mkSuite(name, parent) {
  const s = { name, parent, children: [], tests: [], beforeAll: [], afterAll: [], beforeEach: [], afterEach: [] };
  if (parent) parent.children.push(s); else state.suites.push(s);
  return s;
}
let current = null;
globalThis.describe = (name, fn) => { const s = mkSuite(name, current); const prev = current; current = s; try { fn(); } finally { current = prev; } };
globalThis.describe.only = globalThis.describe;
globalThis.describe.skip = (name, fn) => { const s = mkSuite(name, current); s.skipped = true; };
globalThis.it = (name, fn) => { if (current) current.tests.push({ name, fn, skipped: false }); };
globalThis.it.only = globalThis.it;
globalThis.it.skip = (n, f) => { if (current) current.tests.push({ name: n, fn: f, skipped: true }); };
globalThis.test = globalThis.it;
globalThis.beforeAll = (fn) => { if (current) current.beforeAll.push(fn); else state.rootBeforeAll.push(fn); };
globalThis.afterAll = (fn) => { if (current) current.afterAll.push(fn); else state.rootAfterAll.push(fn); };
globalThis.beforeEach = (fn) => { if (current) current.beforeEach.push(fn); };
globalThis.afterEach = (fn) => { if (current) current.afterEach.push(fn); };

const eq = (a, b) => {
  if (Object.is(a, b)) return true;
  if (typeof a !== typeof b) return false;
  if (a === null || b === null || typeof a !== 'object') return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) return false;
  return ka.every(k => Object.prototype.hasOwnProperty.call(b, k) && eq(a[k], b[k]));
};
function getPath(obj, path) {
  const parts = String(path).replace(/\[(\d+)\]/g, '.$1').split('.').filter(Boolean);
  let cur = obj;
  for (const p of parts) { if (cur == null) return { ok: false, val: undefined }; cur = cur[p]; }
  return { ok: true, val: cur };
}
function fail(msg) { const e = new Error(msg); e.__assert = true; throw e; }
function build(actual, negated) {
  const chk = (pass, msg) => { if (negated ? pass : !pass) fail((negated ? 'NOT ' : '') + msg); };
  const o = {
    toBe(e) { chk(Object.is(actual, e), `expected ${JSON.stringify(actual)} to be ${JSON.stringify(e)}`); },
    toEqual(e) { chk(eq(actual, e), `expected ${JSON.stringify(actual)} to equal ${JSON.stringify(e)}`); },
    toStrictEqual(e) { o.toEqual(e); },
    toBeCloseTo(e, prec = 2) { chk(Math.abs(actual - e) < Math.pow(10, -prec) / 2, `expected ${actual} to be close to ${e} (±${prec})`); },
    toBeGreaterThan(e) { chk(actual > e, `expected ${actual} > ${e}`); },
    toBeGreaterThanOrEqual(e) { chk(actual >= e, `expected ${actual} >= ${e}`); },
    toBeLessThan(e) { chk(actual < e, `expected ${actual} < ${e}`); },
    toBeLessThanOrEqual(e) { chk(actual <= e, `expected ${actual} <= ${e}`); },
    toBeDefined() { chk(actual !== undefined, `expected value to be defined`); },
    toBeUndefined() { chk(actual === undefined, `expected value to be undefined`); },
    toBeNull() { chk(actual === null, `expected ${JSON.stringify(actual)} to be null`); },
    toBeTruthy() { chk(!!actual, `expected ${JSON.stringify(actual)} to be truthy`); },
    toBeFalsy() { chk(!actual, `expected ${JSON.stringify(actual)} to be falsy`); },
    toBeNaN() { chk(Number.isNaN(actual), `expected NaN`); },
    toMatch(re) { const ok = typeof re === 'string' ? String(actual).includes(re) : re.test(String(actual)); chk(ok, `expected ${JSON.stringify(actual)} to match ${re}`); },
    toContain(x) { chk(actual != null && (Array.isArray(actual) ? actual.includes(x) : String(actual).includes(x)), `expected ${JSON.stringify(actual)} to contain ${JSON.stringify(x)}`); },
    toHaveLength(n) { chk(actual != null && actual.length === n, `expected length ${actual && actual.length} to be ${n}`); },
    toHaveProperty(path, value) {
      const r = getPath(actual, path);
      if (arguments.length > 1) chk(r.ok && eq(r.val, value), `expected property ${path} to equal ${JSON.stringify(value)} (got ${JSON.stringify(r.val)})`);
      else chk(r.ok, `expected object to have property ${path}`);
    },
    toThrow(m) {
      let threw = false, err;
      try { actual(); } catch (e) { threw = true; err = e; }
      if (m === undefined) chk(threw, `expected function to throw`);
      else if (typeof m === 'string') chk(threw && String(err && err.message).includes(m), `expected throw message to include ${m}, got ${err && err.message}`);
      else if (m instanceof RegExp) chk(threw && m.test(String(err && err.message)), `expected throw to match ${m}`);
      else if (typeof m === 'function') chk(threw && err instanceof m, `expected throw of type ${m.name}`);
    },
    toHaveBeenCalled() { chk(actual.mock && actual.mock.calls.length > 0, `expected mock to have been called`); },
  };
  if (!negated) Object.defineProperty(o, 'not', { get: () => build(actual, true) });
  if (actual && typeof actual.then === 'function') {
    Object.defineProperty(o, 'resolves', { get: () => asyncMatchers(actual, false) });
    Object.defineProperty(o, 'rejects', { get: () => asyncMatchers(actual, true) });
  }
  return o;
}
const ASYNC_NAMES = ['toBe','toEqual','toStrictEqual','toBeCloseTo','toBeGreaterThan','toBeGreaterThanOrEqual','toBeLessThan','toBeLessThanOrEqual','toBeDefined','toBeUndefined','toBeNull','toBeTruthy','toBeFalsy','toBeNaN','toMatch','toContain','toHaveLength','toHaveProperty'];
function asyncMatchers(promise, isReject) {
  const o = {};
  for (const n of ASYNC_NAMES) {
    o[n] = async (...args) => {
      let val, err;
      try { val = await promise; } catch (e) { err = e; }
      if (isReject) {
        if (!err) fail(`expected promise to reject, but it resolved with ${JSON.stringify(val)}`);
        return build(err, false)[n](...args);
      }
      if (err) fail(`expected promise to resolve, but it rejected with ${err && err.message}`);
      return build(val, false)[n](...args);
    };
  }
  o.toThrow = async (...args) => {
    let err;
    try { await promise; } catch (e) { err = e; }
    if (!isReject) { if (err) return; fail('expected promise to resolve but it threw'); }
    if (!err) fail('expected promise to reject, but it resolved');
    const m = args[0];
    if (m === undefined) return;
    if (typeof m === 'string') { if (!String(err && err.message).includes(m)) fail(`expected rejection message to include ${m}, got ${err && err.message}`); return; }
    if (m instanceof RegExp) { if (!m.test(String(err && err.message))) fail(`expected rejection to match ${m}`); return; }
    if (typeof m === 'function') { if (!(err instanceof m)) fail(`expected rejection of type ${m.name}`); return; }
  };
  return o;
}
globalThis.expect = (a) => build(a, false);
globalThis.jest = { fn: (impl) => { const f = (...args) => { f.mock.calls.push(args); return impl ? impl(...args) : undefined; }; f.mock = { calls: [] }; return f; } };
export async function runAll() {
  const out = { pass: 0, fail: 0, skip: 0, failures: [] };
  async function runSuite(s, inheritedEach = []) {
    if (s.skipped) { out.skip += s.tests.length; return; }
    for (const h of s.beforeAll) await h();
    const each = [...inheritedEach, ...s.beforeEach];
    for (const t of s.tests) {
      if (t.skipped) { out.skip++; continue; }
      try {
        for (const h of each) await h();
        await t.fn();
        for (const h of s.afterEach) await h();
        out.pass++;
      } catch (e) {
        out.fail++;
        out.failures.push({ suite: s.name, test: t.name, err: (e && e.message) || String(e) });
      }
    }
    for (const c of s.children) await runSuite(c, each);
    for (const h of s.afterAll) await h();
  }
  for (const h of state.rootBeforeAll) await h();
  for (const s of state.suites) await runSuite(s);
  for (const h of state.rootAfterAll) await h();
  return out;
}
