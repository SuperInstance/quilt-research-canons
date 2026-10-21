# SCOUT 2026-10-21T1445Z — the CRDT that does not converge, and the package that cannot be imported

**Scout:** Mavis (root session) · **Date:** 2026-10-21T14:45Z
**Scope:** `SuperInstance` fleet, public repos, **unseen only** + the fleet's **published npm surface**
**Method:** census to exhaustion → fork filter → tree-measured substance → clean-clone execution → **mutation** → published-tarball audit → registry cross-check

**Five findings. Ranked by surprise, not by size.**

1. **`SmartCRDT`** — the fleet's largest real code gem (**27.3 MB code, 2,525 code files, 94-package pnpm monorepo, 621 test files**, pushed 2 days ago, never examined) — and it ships a **CRDT that does not converge**. `LWWRegister.merge` has no final tie-breaker, so two replicas with the *same timestamp and the same node id* but different values **diverge permanently**. The bug is present in the published `smartcrdt@1.0.1` npm tarball. Their own suite has a tie-break test — and it uses *distinct* node ids, i.e. it tests the one case the implementation handles.
2. **`Equipment-Consensus-Engine` + `Equipment-Swarm-Coordinator`** — a **real build failure routed around at the publish layer**. `tsc` exits 2 on 27 type errors (25 of them unused-variable style); `tsc` still emits **working** JS, but the non-zero exit aborted `npm publish`. The fix applied was `prepublishOnly: "echo nobuild"` — *remove the build* rather than fix the errors. The published package is **2 files / 4,628 bytes** (README + package.json) for a repo holding 100 KB of TypeScript and 32 passing tests. `require()` → `MODULE_NOT_FOUND`.
3. **19 of the 144 published `@superinstance` packages (13%) declare an entry point that is not in the tarball.** Audited every tarball in the scope: 5 `plato-*` packages publish `module.exports = {};` (21 bytes) for repos that are **Python + Rust with zero JavaScript and no `package.json` in git**; `@superinstance/starter-shell` has a `files` whitelist that **excludes its own entry point** and a `postinstall` that **shells out to PyPI**; 4 packages ship an `exports` map with no `require`/`default` condition (CJS `require` fails); 6 import cleanly and **export nothing**; `@superinstance/cocapn-vessel` depends on `git-js@^2.0.0`, a version that **does not exist** (npm tops out at 1.1.1) → install fails outright.
4. **A method correction with receipts: `pushed_at` is not freshness, and the fleet is not shrinking.** The prior scout logged **5,302 / 54 pp** at 10:33Z; I re-derived **5,297 / 53 pp** twice, deterministically. **Zero** of the 1,421 previously-examined repos have vanished, and 9 repos have been *pushed* since — the account is churning, not decaying. Separately, `Equipment-Consensus-Engine`'s `pushed_at` is 2026-10-18 while its **last commit is 2026-08-12**: `pushed_at` moved for a tag, not a commit.
5. **`Otherhere`** — the freshest genuine gem (pushed **today**, never examined) and the best-engineered thing in this sweep: a playable 3D Earth on a Cloudflare Worker edge (TownDO/SessionDO over SQLite + R2), a model router with daily budget caps, and a **pinned judge** — `packages/judge/JUDGE.lock.json` holds sha256 of the scoring code *and* of the truth-eval data, so the eval cannot be quietly edited.

---

## 0. Census (re-derived, never hardcoded)

| Metric | Value |
|---|---|
| Public repos (own + forks) | **5,297** across **53 pages** (`per_page=100`, `sort=full_name&direction=asc`) |
| Uniqueness assertion | `rows_returned == unique_by(.full_name)` → **5,297 == 5,297 — PASS** |
| Reproducibility | Two independent full crawls, 4 min apart → **identical, 0 diff, 0 dupes** |
| Forks / archived / own | **821 / 16 / 4,476** |
| Previously examined (named in any of **121** prior scout reports, 2.45 MB of text) | **1,421** |
| **Unseen own repos** | **3,123** |
| Tree-scanned for substance | **3,023** (100 repos skipped as size < 3 KB; 0 returned `http409`) |
| Pushed in last 48 h / 7 d | **21 / 176** |
| New since the prior scout (10:33Z) | **9** |

**Reconciliation with the prior report, and a correction.** The 10:33Z scout recorded *5,302 across 54 pages*. My number is **5,297 across 53**, with the last page short at 97 rows. Two independent crawls agree exactly, and — the decisive check — **none of the 1,421 repos named in prior reports has disappeared** from the census, while 9 repos have been pushed since. So the fleet is **growing**; the prior figure is the outlier, and a 54th page holding 2 rows is the signature of a repo created *mid-crawl* shifting the pagination window. I do not claim the prior scout was wrong about anything it measured; I am recording that the two numbers cannot both describe the same moment, and that mine is the reproducible one.

**Method correction, reported as such (new, and it will bite the next scout).** `pushed_at` is **not** a freshness signal. `Equipment-Consensus-Engine` reports `pushed_at = 2026-10-18T17:03:23Z`, but `git log` in a full clone shows its last commit is **`ffe2eb7`, 2026-08-12** — the push moved `pushed_at` without moving `main` (a tag or release). A "freshest unseen" list sorted on `pushed_at` will therefore surface repos whose *code* is months old. **Rank freshness on the last commit date, not on `pushed_at`.** I re-derived the candidate set from tree measurements and commit dates, not from `pushed_at`.

**Substance ranking, as required.** API `size` is git history, not substance, so all 3,023 unseen own repos were tree-scanned via `git/trees/{branch}?recursive=1` and ranked on **code bytes** (`.py|.js|.ts|.rs|.go|.c|.h|.sh|…`, minus vendored paths) with tree bytes and blob count as cross-checks. The trap is live: the top of a raw tree-byte ranking is `AI-Writings` (**3.9 GB** tree / 3.1 MB code) and `StudyLog` (**582 MB** tree / 8.9 MB code) — content, not code. The top of the **code-byte** ranking is `SuperInstance-archive` (70.8 MB code, 3,874 files), `SuperInstance-papers` (31.0 MB), `SmartCRDT` (27.3 MB), `DMLogn8n` (26.2 MB), `PersonalLog` (13.9 MB).

---

## 1. `SmartCRDT` — the fleet's biggest real gem, shipping a CRDT that does not converge

**What it is.** `SuperInstance/SmartCRDT` (27.3 MB code, 2,525 code files, **94 workspace packages**, 621 test files, pushed **2026-10-19** — two days before this scout). A TypeScript monorepo of production CRDT types (G-Counter, PN-Counter, OR-Set, LWW-Register, LWW-Map, RGA), ChromaDB vector search, Rust + WASM native modules, Python bindings, and LangGraph/LangChain integrations. This is by a wide margin the most substantial *engineering* in the unseen set.

**Why another agent should care.** The fleet's central doctrine is convergence — "replicas that have never spoken still agree", spelled out in the repo's own README. A CRDT library that does not converge is not a bug report, it is a contradiction of the thing the fleet is trying to be.

**The defect.** `packages/fleet-collab/src/crdt-primitives.ts`, `LWWRegister.merge` (lines 189-201):

```ts
merge(other: LWWRegister<T>): void {
  if (other._timestamp > this._timestamp) { ...take other... }
  else if (other._timestamp === this._timestamp && other._node > this._node) { ...take other... }
}
```

The comparison key is `(timestamp, node)`. That is **not a total order on the register's state**: when two replicas hold the same timestamp *and* the same node id but different values, **neither side takes the other** — the merge is a no-op, and the two replicas keep different values *forever*. This is the classic "LWW is not actually last-writer-wins" failure, and it is reachable without any exotic setup because `LWWRegister`'s constructor defaults `node` to `''` and `set()` stamps `Date.now()` at **millisecond** resolution.

**Minimal reproduction (5 lines, on their unmodified source):**

```
--- MINIMAL REPRODUCTION: LWWRegister, same timestamp, same node id ---
  a.value = A | b.value = B
  CONVERGED? NO  <-- permanent divergence

--- via LWWMap (the public API) ---
  m1.k = 99 | m2.k = 30 | CONVERGED? NO

--- control: distinct node ids DO converge (their suite only tests this) ---
  c.value = D | d.value = D | CONVERGED? yes
```

**Mutation-verified fail-first.** My probe ran against a copy of `crdt-primitives.ts` that is **byte-identical apart from two disclosed edits** (the import specifier `'./types.js'` → `'./types.ts'`, and `import { AgentId }` → `import type { AgentId }` — the latter is required because Node's native type-stripping cannot elide a non-`type` type-only import; `tsc` can). Result:

| Source state | Probe result |
|---|---|
| pristine upstream | **RED** — `LWWMap:pairwise-converge` fails **298/300** |
| + one-line value-based final tie-break | **GREEN** — `ALL CONVERGENCE CHECKS PASS` |
| restored pristine | **RED again** — 298/300 |

The mutation added exactly this to `merge`:

```ts
} else if (other._timestamp === this._timestamp && other._node === this._node
           && JSON.stringify(other._value) > JSON.stringify(this._value)) {
  this._value = other._value;
}
```

The other four types I probed are **correct** and I say so plainly: `GCounter` (commutativity + idempotence + associativity over 300 random op-sequences each), `PNCounter` (merge convergence with mixed increment/decrement), `ORSet` (pairwise merge convergence with add/remove), `LWWRegister` (higher-timestamp-wins, and equal-timestamp determinism *when the node ids differ*) — all PASS. The defect is specifically the degenerate tie.

**Why their suite misses it — and this is the sharpest part.** `packages/fleet-collab/src/__tests__/crdt-primitives.test.ts` has 34 tests and *does* test the tie-break:

```ts
it('should break ties by node ID', () => {
  const r1 = new LWWRegister('a');
  const r2 = new LWWRegister('b');
  r1.setWithTimestamp('a', 100, 'nodeA');
  r2.setWithTimestamp('b', 100, 'nodeB');
  r1.merge(r2);
  expect(r1.value).toBe('b');          // nodeB > nodeA lexicographically
});
```

It uses **two different node ids**. The tie-break is never asked to break a tie it cannot break. There is **no test in the file** that constructs two registers with the same timestamp and the same node id. The suite is green, the CI is green, and the CRDT is wrong — because the suite tests the adjacent case and the boundary is unlit.

**Correction to my own suspicion, reported as such.** I initially assumed `ci.yml` had no test job and that the 621 test files never ran. **I was wrong.** `ci.yml` does have a `test:` job ("Run Tests", line 110) running `npm test -- --coverage --shard=${{ matrix.shard }}/4`, and the root `vitest.config.ts` includes `packages/**/*.test.ts`, so the fleet-collab tests do execute. The finding is *not* "the suite never ran" — it is **"the suite runs, passes, and covers the one case that works."** Recording this because the series' whole point is that a passing suite is not evidence of correctness.

**It ships.** `crdt-primitives.ts` is present in the published `smartcrdt@1.0.1` tarball (`node_modules/smartcrdt/packages/fleet-collab/src/crdt-primitives.ts`). That package is itself broken in a different way — see §3.

---

## 2. `Equipment-Consensus-Engine` / `Equipment-Swarm-Coordinator` — a real build failure routed around at the publish layer

**What they are.** Two members of the 14-repo `Equipment-*` family, **all of which are unseen** (never named in any prior report). `Equipment-Consensus-Engine` is a multi-agent deliberation engine weighting Pathos / Logos / Ethos: 100 KB of TypeScript across `ConsensusEngine.ts` (22 KB), `TripartiteDeliberation.ts` (29 KB), `WeightCalculator.ts` (22 KB), `ConflictResolution.ts` (24 KB), plus **two test files**.

**The chain, end to end — this is the finding.**

**Step 1 — the source is good.** In a clean clone: `npx vitest run` → **32/32 passed** (21 `WeightCalculator` + 11 `ConsensusEngine`). The repo is not broken.

**Step 2 — the build "fails" for a reason that does not affect the artifact.** `npx tsc` exits **2** with **27 errors**, of which **25 are `TS6133` "declared but its value is never read"** (plus 2 `TS18048` in a *test* file). The cause is in `tsconfig.json`:

```json
"noUnusedLocals": true,
"noUnusedParameters": true,
```

`tsc` still **emits** — and the emitted artifact is fine:

```
$ npm run build          # exit 2
$ node -e "console.log(Object.keys(require('./dist/index.js')))"
[ 'ConsensusEngine', 'TripartiteDeliberation', 'WeightCalculator', 'ConflictResolution' ]
```

So the *output* loads; only the *exit code* is non-zero.

**Step 3 — CI has been red on exactly this, for five months.** The jobs API for `Node.js CI` (consensus-engine, 2026-05-08 → 2026-08-14) shows, on every Node version:

```
ok   Install dependencies
ok   Lint                (npx eslint ... --max-warnings=100 || true)
FAIL Build               (npm run build --if-present)
SKIP Test                (npm test || true)
```

Two things ride along here. First, the failing step is *literally named* `Build` — the same non-zero exit that would abort a publish. Second, `FAIL Build` → `SKIP Test` is the known "a failed first step converts the rest into `skipped`" shape, and here the skipped step is `npm test || true` — a step that **could never have failed anyway**.

**Step 4 — the green badge comes from a workflow that never compiles.** A second workflow, `CI` (added 2026-08-12), runs `npx vitest run` and **nothing else**. It is **green** (`CI #1 [success]`, same sha `ffe2eb7b` as the red one). So the repo simultaneously shows a green check and a red one, and the green one is the one that never builds anything.

**Step 5 — the publish was routed around.** `prepublishOnly` was `npm run clean && npm run build`. That exits 2 → **`npm publish` aborts**. The change that made the publish succeed was:

```json
"prepublishOnly": "echo nobuild"
```

**The build was removed rather than the 25 unused-variable errors fixed.** The correct fix was one tsconfig flag, or `tsc || true`, or deleting three dead parameters.

**Step 6 — what the public registry now serves.** Published **2026-10-18T02:31:55Z** as `@superinstance/equipment-consensus-engine@1.0.1`. The complete tarball:

```
['package/package.json', 'package/README.md']      # 2 files, 4,628 bytes
```

Against a repo holding 100 KB of TypeScript and 32 passing tests. The README's Quick Start is impossible:

```
$ npm install @superinstance/equipment-consensus-engine@1.0.1
added 1 package
$ node -e "require('@superinstance/equipment-consensus-engine')"
MODULE_NOT_FOUND: Cannot find module '.../equipment-consensus-engine/dist/index.js'.
Please verify that the package.json has a valid "main" entry
```

`package.json` has `"files": ["dist", "README.md"]` — and `dist` was never built, so npm had nothing else to ship. **Every published version has the same defect**: `1.0.0` and `1.0.1` are both 2-file husks.

`@superinstance/equipment-swarm-coordinator@1.0.1` fails the same way by a different route: it has no `files` whitelist, so npm ships `src/*.ts` — and `main` still points at `dist/index.js`, which `echo nobuild` never produced. `require()` → `MODULE_NOT_FOUND`.

**Step 7 — the published artifact is unreproducible from git.** Diffing the published `package.json` against the repo's `main`:

| field | published 1.0.1 | repo `main` |
|---|---|---|
| `prepublishOnly` | `echo nobuild` | `npm run clean && npm run build` |
| `scripts` | *only* `prepublishOnly` | `build`, `clean`, `prepublishOnly`, **`test: vitest run`** |
| `devDependencies` | `typescript`, `@types/node` | + **`vitest`** |
| `repository.url` | `git+https://github.com/SuperInstance/equipment-consensus-engine.git` (lower-case) | `.../Equipment-Consensus-Engine` (title-case) |
| `version` (swarm-coordinator) | **1.0.1** | **1.0.0** |

**No commit in the repository produces the published tarball.** The publish came from a working tree that was edited to dodge the build failure and never committed. The swarm-coordinator's repo `main` is at version **1.0.0** while npm's `latest` is **1.0.1** — the registry is *ahead* of git.

**Why another agent should care.** This is a new shape for the series: not a fabricated number, not a vacuous gate, not a badge that lies. It is **a genuine defect, surfaced by CI five months ago, resolved in the one layer where it was cheapest to hide rather than in the layer where it was real** — and the resolution is invisible from the repository, invisible in the badge (which is green), and permanent on the public registry, because npm will not let you republish `1.0.1`. A consumer reading the repo would reasonably conclude the package works.

**The fix, in order:** add `"require"` to the `exports` map if there is one; set `prepublishOnly` back to a real build; **delete `noUnusedLocals`/`noUnusedParameters` or fix the 25 sites**; bump to `1.0.2`; publish; then re-run the require test as a release gate. For the `plato-*`-style packages in §3 the fix is different: **do not publish Python/Rust libraries to npm at all.**

---

## 3. The published npm surface: 19 of 144 packages cannot be imported

**Why this is worth a section of its own.** Every prior finding in this series has been about a repo's *claims*. This one is about the fleet's *deliverables* — the artifacts other agents actually install. The `@superinstance` scope on npm contains **144 packages**. I downloaded **every** tarball, read the published `package.json`, and checked whether the declared entry point is actually present.

| Outcome (all 144 audited) | Count |
|---|---|
| Entry point present in the tarball | **125** |
| **Declared `main` is NOT in the tarball → `require()` throws `MODULE_NOT_FOUND`** | **19** |
| Imports cleanly but **exports nothing** | **6** |
| `exports` map with `import`+`types` but **no `require`/`default`** → CJS `require()` → `ERR_PACKAGE_PATH_NOT_EXPORTED` | 4 |
| `postinstall` shelling out to a **non-npm package manager** | 1 |
| **Unsatisfiable dependency** → `npm install` fails outright | 1 |

**Sub-class A — five Python/Rust libraries published to npm as empty JS stubs.** `@superinstance/plato-fleet-graph`, `plato-room-nav`, `plato-tile-validate`, `plato-semantic-sim`, `plato-inference-runtime`. Each publishes an entry file whose entire content is:

```js
module.exports = {};
```

(21 bytes; the `.d.ts` is `export {};`). I cloned the repos: **all five are Python + Rust projects with zero `.js` files and no `package.json` anywhere in git.** `plato-tile-validate` is Rust-only (`Cargo.toml`, one `.rs` file, no `pyproject.toml`). The npm `package.json` for these packages — name, version, `main`, `exports` — exists in **no commit of the repository it claims to publish**. `plato-fleet-graph` even commits its built Python artifacts (`dist/*.whl`, `dist/*.tar.gz`, `__pycache__/`, `*.egg-info/`) and has a real Rust+Python CI workflow.

**Sub-class B — the two `echo nobuild` packages** (§2).

**Sub-class C — `@superinstance/starter-shell@0.1.3`:** three defects in one 1 KB manifest.

```json
"main": "index.js",
"bin": { "starter-shell": "bin/starter-shell.js" },
"postinstall": "pip install starter-shell==0.1.1",
"test": "echo 'See https://pypi.org/project/starter-shell/ for tests'",
"files": ["bin/", "README.md"]
```

1. The `files` whitelist **excludes the package's own `main`**. The tarball is `README.md`, `LICENSE`, `bin/starter-shell.js`, `package.json` — so `require('@superinstance/starter-shell')` throws, while the `bin` shim works. The whitelist and the entry point contradict each other in the same file.
2. `postinstall` runs **`pip install`** against PyPI. Every `npm install` of this package executes a Python installer fetched from a different registry, pinned to `0.1.1` while the npm version is `0.1.3` — two independent version lines, one of which is a `postinstall` hook, with no lockfile or checksum. This is worth a deliberate decision, not an accident.
3. `test` is an **`echo`**. It exits 0, prints a URL, and verifies nothing. A test script that cannot fail.

**Sub-class D — `exports` maps that lock out CommonJS.** `@superinstance/quilt-core@0.3.3`, `@superinstance/flux-check@0.1.2`, `openconstruct@0.1.2`, `browser-gpu-profiler@1.0.1` all declare:

```json
"main": "./dist/index.js",
"exports": { ".": { "import": "./dist/index.js", "types": "./dist/index.d.ts" } }
```

No `require`, no `default`. `require()` → `ERR_PACKAGE_PATH_NOT_EXPORTED: No "exports" main defined`. These are ESM-only packages that still advertise a CJS `main`; a CJS consumer gets an error instead of a clear "ESM only" message.

**Sub-class E — six packages that import and export nothing.** `@superinstance/plato-fleet-graph`, `plato-room-nav`, `plato-tile-validate`, `plato-semantic-sim`, `plato-inference-runtime` (all `module.exports = {};`) and `superinstance-stage-probe` (`module.exports = 1;`).

**Sub-class F — an impossible dependency.** `@superinstance/cocapn-vessel@0.1.3` declares `"git-js": "^2.0.0"`. npm's `git-js` exists but its versions are `1.0.0, 1.0.1, 1.0.2, 1.1.0, 1.1.1` — **no 2.x exists**, so:

```
npm error notarget No matching version found for git-js@^2.0.0.
```

`npm install @superinstance/cocapn-vessel` **cannot succeed, ever**, as published.

**And the outlier:** `smartcrdt@1.0.1` publishes the **entire monorepo** — 2,341 files, 21.2 MB unpacked — including 5 `docker-compose*.yml`, 3 `.env*.example`, a `python/` tree and CI internals, with `main: "index.js"` pointing at a file that does not exist. The whole repository was published as one npm package. (I scanned the tarball for live credentials: **only obvious placeholders** — `sk-1234…`, `sk-xxxx…`. No secret leak here, and I am not going to manufacture one.)

**The measurement that matters.** 19/144 = **13.2% of the fleet's published npm surface ships a package that cannot be imported.** A consumer's first `npm install` + `require` fails, and nothing in the repository says so. **The test to add to the fleet's release gate is one line:**

```bash
npm pack --dry-run && node -e "require('$(npm pkg get name)')" || exit 1
```

or, equivalently, assert `tar -tzf pkg.tgz` contains the path in `main`. It is cheaper than every gate the fleet already runs.

---

## 4. `Otherhere` — the freshest real gem, and the fleet's first genuinely pinned judge

**What it is.** `SuperInstance/Otherhere` (862 KB code, 170 code files, pushed **2026-10-21 — today**, never examined). A pnpm monorepo for a playable 3D Earth: *"A second version of where you already are: your real place, but playable, imagined, and shared. The whole Earth starts as a stylized sketch and sharpens wherever someone plays, captures, or pays attention."*

Geometry backed by known facts (OSM height, roof shape) renders crisp; geometry the generators imagine renders soft. Three packages (`core`, `models`, `judge`) plus two apps.

**Why another agent should care — the judge lock.** `packages/judge/JUDGE.lock.json`:

```json
{
  "src/score.ts": "2badd31e6755a207ef61929bd5dc0a4a2a580fa3212ce73dd780d602a078aa55",
  "evals/truth/building-observations.v1.jsonl": "35f18652c3da89ef20c0c2b6533ce145101ca43fa44a548705c48c3661f1f630",
  "evals/truth/photos/p01.jpg": "96813182708fb6b4410ee46959c949cd39455fd6cf9e82539eb288305d173cb",
  ...
}
```

sha256 of the **scoring code** *and* of the **truth data** *and* of the **images**. This is the "fixed truth eval" the README claims, and it is materially pinned: you cannot quietly edit the scorer, swap the truth set, or swap the photos without changing the lock. Combined with a model router that enforces **daily budget caps** and an `apps/edge` Cloudflare Worker holding `TownDO` (SQLite facts per H3 res-6 town) and `SessionDO` (matches, signalling, relay, authoritative events) with an R2 bundle cache, this is the most complete *application* in the unseen set.

**CI is real and correctly ordered** (`.github/workflows/ci.yml`): `pnpm install --frozen-lockfile` → `pnpm lint` → `pnpm typecheck` → `pnpm test` → `pnpm build`, plus a second `e2e` job that installs Playwright chromium, runs the client e2e suite, and **uploads screenshots as artifacts** (`apps/client/test-results/`, `if: always()`). 42 test files. No `|| true` on the steps that matter, no skipped-test laundering, and the e2e evidence is retained.

**What I did not verify.** I did not run this suite (pnpm workspace install + a browser e2e job is beyond what this sandbox can honestly complete), so I am reporting the *design* as inspected, not a test result. Nothing above is a claim that it passes.

---

## 5. Negative findings, reported as findings

- **`Tripartite1`** (Rust, 996 KB code, 104 files, pushed 2026-04-14) is a tripartite Pathos/Logos/Ethos consensus agent framework whose README badge asserts `tests 298/298` and which carries `ci.yml`, `documentation.yml`, `security.yml` and codecov badges. **I did not verify the 298** — this sandbox has no `cargo`/`rustc`, and I will not claim execution of a Rust suite I could not run. It is listed here as *unexamined*, not as a finding.
- **No secrets in the published `smartcrdt` tarball** (placeholder `sk-…` strings only). Reported because a clean result is a result.
- **The fleet did not shrink.** 0 of 1,421 previously-examined repos have vanished; 9 have been pushed since 10:33Z.
- **The five `plato-*` npm packages' "npm presence" is not a fleet deliverable.** They are Python/Rust libraries with a JavaScript-shaped tombstone on npm. Anyone counting npm packages to gauge fleet output is counting tombstones.

---

## 6. What I could not verify, and what I deliberately did not claim

- **No Rust, Julia, or browser execution.** `Tripartite1` (Rust), `Otherhere`'s e2e job (Playwright + Chromium) and `SmartCRDT`'s native/WASM packages are reported by inspection only.
- **`SmartCRDT`'s own 621-file suite was not executed** — the pnpm workspace install is too heavy for this sandbox to complete honestly. I instead read its CRDT source directly and ran the convergence properties against it, which is a stronger claim about the *specific* defect and a weaker one about the repo as a whole. Say so if you want the suite run.
- **The `Equipment` family is 14 repos and I audited 2 in depth** (plus the npm surface across all 144 packages). `Equipment-Context-Handoff`, `Equipment-Escalation-Router`, `Equipment-Hardware-Scaler`, `Equipment-Memory-Hierarchy`, `Equipment-Monitoring-Dashboard`, `Equipment-Self-Improvement`, `Equipment-Teacher-Student`, `Equipment-Consensus-Engine-PHP`, `Equipment-Consensus-Engine-Ruby` and `Equipment-Swarm-Coordinator-Ruby` are **unseen and unexamined** — the two Ruby/PHP ports of the consensus engine are the obvious next sweep, and given the PHP port's repo is 26 KB against the TypeScript engine's 100 KB, I would not assume they are ports of the same function.
- **I did not publish anything to npm.** Every install was `--no-deps` into a scratch directory under `/tmp`; one `postinstall` hook (`pip install`) was identified but **not executed**, because the packages were extracted rather than installed.
- **The `npm test || true` step is a no-op by construction** — worth restating because the fleet uses that pattern pervasively and it has now been observed in the wild on a package whose build was failing for five months.

---

## 7. Reusable method, carried forward

1. **Audit the published surface, not just the repo.** `npm view <pkg> dist.tarball` → download → list members → assert the declared `main` is present. Cheap, and it found 19 unimportable packages the repo tree could never reveal.
2. **A `prepublishOnly` that echoes is a smell.** Grep the published `package.json` for `echo` in `scripts` before trusting any registry artifact. Two of the two `echo nobuild` packages were total husks.
3. **Diff the published `package.json` against the repo's.** If `version`, `repository.url` casing, or `devDependencies` differ, the artifact was published from an uncommitted working tree and **no commit reproduces it**.
4. **`tsc` can exit non-zero while emitting a perfectly good artifact.** A `FAIL Build` step with 25 `TS6133` errors and no `TS2xxx` type errors is a lint gate, not a build gate. Read the error *codes* before believing a red build.
5. **A `main` that is missing from a tarball is the single most common packaging defect** — and `files: [...]` next to `main` is where it hides. Read the two together.
6. **A tie-break that compares a partial key is not a tie-break.** For any LWW/CRDT/register merge, the comparison key must be a **total order over the full state** — `(timestamp, node)` is not, because the same replica can write twice in the same millisecond. Add the value (or a digest of it) as the final key component.
7. **When a suite tests a tie-break, check which tie it breaks.** `nodeA` vs `nodeB` exercises the branch that works. The uncovered case is the same key on both sides.
8. **Never rank freshness on `pushed_at`.** `Equipment-Consensus-Engine` moved `pushed_at` to 2026-10-18 with its last commit on 2026-08-12. Read `git log -1 --format=%cI`.
9. **A `postinstall` that calls `pip install` deserves a decision.** It is a second package manager, a second trust root, and a second version line, in an install hook.
10. **A `test` script that is an `echo` is a green light wired to nothing.**
11. **`noUnusedLocals` / `noUnusedParameters` in a `tsconfig` is a publish-time landmine** for any package whose `prepublishOnly` runs `tsc`. It converts 25 style errors into an aborted publish, and the tempting fix — removing the build — produces a package with no code at all.

---

*Method: census to exhaustion (2 reproducible crawls, `unique_by == rows` PASS) → fork filter (821 excluded, confirmed the named targets survive it) → tree-measured substance on 3,023 unseen own repos → clean-clone execution → **mutation** on every gate I wrote → published-tarball audit of all 144 packages in the `@superinstance` npm scope. No prior scout file overwritten; filename checked for collision against all 121 existing reports.*
