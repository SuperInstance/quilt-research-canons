# jest_shim — run a fleet repo's jest/TypeScript suite with npm firewalled

## Why this exists

`npm ci` dies in the scout sandbox with `Unknown system error -122` on `close`
(graceful-fs), so a repo with a real, valuable jest suite cannot be executed at
all. The scout then reports "I could not run it" — or, worse, counts the suite
as green without ever executing it.

This directory is a **minimal jest API shim** plus a runner that uses it. It
lets the scout actually *execute* a TypeScript suite and honestly report a
number. It is the TypeScript counterpart of `tools/pytest_shim`.

A pass under this runner means **"the suite passes under an independent
harness"** — it is not the same claim as "jest ran". Say it that way.

## Use

```bash
# from a cloned repo (needs node >= 22)
node --experimental-transform-types \
     --import /path/to/jest_shim/register.mjs \
     /path/to/jest_shim/runner.mjs "$PWD/tests"
```

The runner prints `=== N passed, M failed, K skipped (F files) ===` and lists
each failure as `FAIL [suite] test name` + the message. Exit code is non-zero
when anything fails.

## What it supports

- `describe` / `it` / `test` (and `.only` / `.skip`), nested suites
- `beforeAll` / `afterAll` / `beforeEach` / `afterEach`
- `expect(...).toBe / toEqual / toStrictEqual / toBeCloseTo / toBeGreaterThan /
  toBeLessThan / toBeGreaterThanOrEqual / toBeLessThanOrEqual / toBeDefined /
  toBeUndefined / toBeNull / toBeTruthy / toBeFalsy / toBeNaN / toMatch /
  toContain / toHaveLength / toHaveProperty / toThrow`
- `.not` on every matcher, and `await expect(promise).resolves/.rejects`
- `jest.fn()` with `.mock.calls`

## The three repairs that make it work (each is a real Node/TS trap)

1. **Extensionless relative imports.** A jest/ts-jest repo writes
   `import { x } from '../src/compute/stats'`. Node ESM requires the
   extension, so `hooks.mjs` retries the resolve with `.ts`, `.tsx`,
   `/index.ts`.

2. **Type-only imports break ESM linking.** `import { ComputeKernel } from
   '../types'` fails with *"does not provide an export named 'ComputeKernel'"*
   because `ComputeKernel` is an `interface` and has no runtime binding. The
   `load` hook appends `export const <Name> = undefined;` for every exported
   `type`/`interface` — TypeScript permits a `type X` and a `const X` to
   coexist, so the type position still resolves.

3. **Type-stripping erases every `export` marker from a pure-type module.**
   `src/types.ts` containing only `export interface`/`export type` becomes
   syntactically CommonJS after stripping, so Node's module-syntax detection
   classifies it as CJS and its named exports vanish. The `load` hook forces
   the format back to `module-typescript` for any `.ts` file that declares
   exports.

Also: a **top-level `beforeAll`** (outside any `describe`) is silently dropped
if you only attach hooks to the current suite — that produces a wall of
`ECONNREFUSED` failures that look like a repo defect but are the harness's
fault. The shim keeps root-level `beforeAll`/`afterAll` and runs them around
the whole file.

## Measured

`exocortex-mcp-ts` (89 tests, 7 files) → **89 passed, 0 failed** under this
shim; `npm ci` cannot run in the sandbox at all. Mutations M1/M2/M3 of that
repo's suite go RED under it; M4 survives (see the 2026-10-25T0810Z scout
report).
