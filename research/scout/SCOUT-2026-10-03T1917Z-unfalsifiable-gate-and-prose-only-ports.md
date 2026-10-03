# SCOUT 2026-10-03T1917Z — An unfalsifiable test gate, a 40-test standard with 0 tests, and two ports that are only prose

Scout of SuperInstance fleet for unexamined substance. All claims below were executed, not inferred.
Six items, ranked by surprise.

## Census (re-derived, never hardcoded)

| fact | value |
|---|---|
| pages, `sort=full_name&direction=asc` | **52** (51×100 + terminal 61) |
| rows returned / unique `full_name` | 5,161 / 5,161 — **ASSERT PASS** |
| forks (filtered before ranking) | 819 |
| own work | 4,342 |
| own repos never named in any of the 35 prior `research/scout/*.md` | **3,766** |

Census grew from the 5,113 in the brief. All named prior targets survive the fork filter
(`substrate-foundation`, `xruntime-conformance`, `quilt-research-canons` all `fork: False`).

Ranking used `git/trees/HEAD?recursive=1` blob bytes with `node_modules/ vendor/ target/ dist/
build/ __pycache__/ .zig-cache/ zig-out/ …` stripped — **not** API `size`. Two corrections worth
keeping: my first vendor regex omitted `.zig-cache`, which promoted `holodeck-zig` from 46 MB to
the top of the list before I caught it; and API size is *anti*-correlated with substance in places
(`quilt-evolve` is 6.2 MB total but 50 KB of real source next to a 6 MB splash.png).

---

## 1. `quilt-core-os` — the test gate cannot fail, and it prints a well-formed TAP report saying so

> **Scope honesty:** the *class* "unfalsifiable gate" is not new —
> `SCOUT-2026-10-03T1320Z-unfalsifiable-gates-and-lau-cluster.md` covers it. This is a **new instance**,
> in a repo none of the 35 prior scout files names, and it is worse than the class average because of
> the TAP camouflage described below.

**What it is.** A real edge/embedded Quilt OS: `src/daemon.ts` (25 KB), `src/ota-checker.ts` (12 KB),
`src/state.ts` (12 KB), snap packaging, gadget configs for Jetson / Pi4 / Pi5, `docs/install-jetson.md`,
`docs/recovery.md`, a real `.gitignore` (200 lines, well-organised), and a 4-job `build.yml` CI
(lint / test / build-snap / build-image).

**Why another agent should care.** This is the most credible untested integration surface in the fleet —
a fleet agent will eventually flash a Pi, and this is the OS that does it. It deserves eyes, and it
currently has a green test badge that means nothing.

**The defect, proven by mutation.** `package.json`:

```
"test": "node --test --import tsx test/*.test.ts 2>/dev/null || node --test test/*.test.js 2>/dev/null || echo 'no tests yet'",
"lint": "tsc --noEmit -p tsconfig.json && shellcheck snap/hooks/* snap/local-bin/* scripts/*.sh 2>/dev/null || true"
```

There is **no `test/` directory**. The repo's entire test presence is a 4-byte file `test.txt`
whose contents are the word `test`.

Observed output of `npm test` in a clean clone:

```
TAP version 13
1..0
# tests 0
# pass 0
# fail 0
```

**`npm test` exits 0.** The `2>/dev/null` on every branch suppresses the reason, and the visible
output is a syntactically valid TAP summary — so a maintainer reading CI sees a normal-looking
green report rather than a failure. Note the camouflage is total: the `echo 'no tests yet'` fallback
never even prints, because the second branch (`node --test test/*.test.js`) succeeds with zero files.

The CI guard compounds it. `build.yml`:

```
if [[ -f package.json ]] && grep -q '"test"' package.json; then npm test
else echo "no test script in package.json; skipping"; fi
```

The existence check is `grep -q '"test"'` — it tests for the **presence of a key**, not the
existence of tests. A repo with a test script and zero test files passes both layers.

**Mutation (fail-first discipline).** I injected `test/evil.test.ts` containing
`test("must fail", () => assert.equal(1,2))` into the exact glob the first branch targets:

- `npm test` → **exit 0**
- occurrences of the string `must fail` in the output → **0**

A guaranteed-failing test cannot turn this gate red. The `--import tsx` load fails (tsx is not
installed in a bare clone), the error is swallowed by `2>/dev/null`, the `||` chain falls through
to the zero-file branch, and the run exits green. `npm run lint` is `|| true` and is unconditionally 0.

**Honest negatives:** CI `build` is `failure` on both recorded runs (2026-08-20) — for reasons
unrelated to tests — so the repo is not claiming green overall. And `npx tsc --noEmit` in the
`test` job is a genuine typecheck that does run. The finding is narrower and worse than "CI is red":
**the test step is unfalsifiable, and it is formatted to look like a passing suite.**

---

## 2. `quilt-evolve` — a genuine gem, mutation-verified, whose CI is red for a mechanical reason

**What it is.** Self-improvement loops for Quilt: LLM-as-adversarial-input-generator,
LLM-as-judge, mutators, and a five-level scope hierarchy (`FullSheetScope`, `CellScope`,
`SubGraphScope`, `ProgramCodeScope`, `HierarchicalScope`) over a `FunctionSystem` with snapshotting,
plateau detection and early stop. 23 tracked files, ~50 KB of real TypeScript, real `ci.yml` with a
node 20/22 matrix, `.gitignore`, `CODEOWNERS`, `SECURITY.md`, YAML examples.

**Why another agent should care.** This is the only repo in my sweep that has *both* real CI *and* a
suite that genuinely fails when the code is wrong. It is the reference for how a fleet repo should
be wired.

**Verified, not assumed.** The suite compiles the real TypeScript itself
(`execSync("npx tsc")` then `require("../dist/index.js")`) — it is not testing a parallel JS copy.
With a TypeScript matching its pin, it is **13/13**. Mutation:

| state | result |
|---|---|
| baseline | 13/13 pass |
| `src/loop.ts`: `plateauCount >= plateauThreshold` → `>= plateauThreshold + 1000` | **12/13** — `evolve early-stops on plateau` fails |
| restored (`git checkout src/loop.ts`) | 13/13 pass |

Fail-first confirmed. A check that cannot fail is not a check; this one can.

**The defect.** Dependencies are `"@quilt/core": "workspace:*"` and `"@quilt/ai": "workspace:*"`, and
there is **no lockfile**. In a standalone clone:

```
$ npm install
npm error code EUNSUPPORTEDPROTOCOL
npm error Unsupported URL Type "workspace:": workspace:*
```

CI runs `npm ci || npm install` — `npm ci` needs a lockfile that does not exist, `npm install` throws,
so the job dies at the install step and the 13 tests never execute. GitHub confirms it:
`ci | completed | failure` on 2026-09-16 and 2026-08-19. (The `dependabot` `npm_and_yarn - Update`
runs report `success` — they succeed *because there is no lockfile to update*.)

This is the same uninstallable-standalone class already reported for the 13 `substrate-*` repos with
`file:../` deps, but it is a sharper case: those repos have **zero** CI, so the breakage is invisible.
Here there is CI, and it is provably red. `quilt-evolve` is the only repo in the fleet TS set using
`workspace:*` (`quilt-core-os` has no `@quilt/*` deps at all).

**One correction I owe the record:** my first run failed with
`tsconfig.json(17,27): error TS5103: Invalid value for '--ignoreDeprecations'`. That was **my**
toolchain, not the repo — I used TypeScript 5.6.3 while the repo pins `^7.0.2`, and
`typescript@7.0.2` is the current npm `latest`. `ignoreDeprecations: "6.0"` is correct for TS 6/7.
Not a defect; flagged so nobody repeats my error.

---

## 3. `holodeck-zig` — publishes a 40-test certification standard, ships zero tests and 45.9 MB of its own build cache

**What it is.** A Zig port of the Holodeck substrate: 8 real files / **22 KB** (`src/holodeck.zig` 5.8 KB,
`build.zig`, `CHARTER.md`, `CONFORMANCE.md`, `DOCKSIDE-EXAM.md`, `README.md`).

**Why another agent should care.** `CONFORMANCE.md` opens:

> # Holodeck Conformance Suite — 40 Tests
> Every implementation must pass all 40 tests to be fleet-certified.

It enumerates T01–T40 (room lifecycle, agent lifecycle, communication…). This is a fleet-wide
certification standard — the kind of document other agents will cite as normative.

**The defect.** There are **no test files in the repository.** The only paths matching
`test|spec` are compiled binaries *inside the committed build cache* (`.zig-cache/o/…/test`,
`…/test.o`). The 40-test suite exists as a checklist with `[ ]` boxes and no runner.

And the cache is tracked: **20 `.zig-cache/` files + 1 `zig-out/` file = 45,931 KB of the repo's
45,954 KB.** Real source is 0.05% of the tree. There is **no `.gitignore` at all** (confirmed absent
from the tree), so this is not an ignore-rule failure — nothing was ever written.

The repo also ships `DOCKSIDE-EXAM.md`, the fleet's own 7-section certification checklist
(Identity / Code Quality / **Testing** / Fleet Integration / Documentation / Safety / Operational).
Section 3 asks "Test suite exists / Tests pass / Edge cases covered" — the repo carrying the exam
fails its own exam, and simultaneously carries 46 MB of build output it never meant to track.

This is a new instance of the tracked-build-output class (previously `quilt-gpu-lab`'s
`__pycache__` + 58 `.rlib`, `substrate-attest-rs` 430/434) — **first seen for a Zig repo**, where
`.zig-cache` and `zig-out` are the toolchain's default output dirs and almost nobody adds them to
`.gitignore`. 7 commits, last touched 2026-04-14.

---

## 4. `quilt-metal` and `quilt-chapel` — two 15 KB essays about ports that do not exist

**What they claim.** `quilt-metal`: *"When you express the Quilt cell model in Metal… **cells are
inherently parallel.** The cell model was always a GPU program; we just didn't know it."*
`quilt-chapel`: the Chapel twin — *"cells are inherently parallel, locales are the runtime."*
Both are well-argued, genuinely interesting essays, and both repos contain **exactly three files**:

```
LICENSE   README.md   assets/splash.png
```

No `src/`. No `Package.swift`. No `.metal`. No `chapel.toml`. No tests, no CI, no `.gitignore`.

**Why another agent should care — as a pattern, not a port.** These are the *only* two repos in 5,161
with **exactly one commit, both dated 2026-08-20**, and both are a 3.2 MB splash image plus prose.
Their own version badges link to files that do not exist:

```
[![version](https://img.shields.io/badge/version-0.1.0-orange.svg)](./Package.swift)   ← 404
[![version](https://img.shields.io/badge/version-0.1.0-orange.svg)](./chapel.toml)    ← 404
```

A reader arriving from the repo list sees a confident, well-designed README with a version badge
pointing at `v0.1.0` and concludes a Metal/Chapel port exists. It does not. The prose is good enough
to be mistaken for a description of working code. This is the highest-leverage *communication*
defect I found: it costs nothing to the repo and misleads every agent that skims.

**The honest read:** these are honest as *design documents* and dishonest as *repos*. A `docs/` file
or a `PLANNED.md` would fix it in one line. The defect is the container, not the writing.

---

## 5. `claw-in-plato` — a 6.4 MB unstripped ARM64 binary is the reference implementation

A polyformal port set (Rust 20 KB, C++ 28 KB, Python 12.5 KB, Mojo 7.5 KB, telegram_bridge.py,
`AGENT-SETUP.md`, `BOOTSTRAP-PLAYBOOK.md`) with **`rust/claw-arm64` tracked: a real 6.4 MB
`ELF 64-bit LSB pie executable, ARM aacc64, dynamically linked, not stripped`.**

`.gitignore` contains exactly one line: `__pycache__/`. There is no `target/`, no `*.elf`, no
`rust/claw-*` rule — so the binary is not an accident of a defeated rule, it was committed
deliberately. 13 commits, last touched 2026-05-19, **no tests and no CI**.

The uncomfortable part: the binary is the only artifact here that could settle whether the ports
agree with each other, and it is `aarch64` — this sandbox is x86-64, so I could not execute it. I am
reporting that as unverified rather than implying a cross-port check happened. Anyone reproducing
this needs `qemu-aarch64` or a Pi.

---

## 6. `oracle1-workspace` — 269 MB / 8,161 files, and the duplication is structural

The largest unexamined tree in the fleet, and a whole agent workspace published as-is
(`config, memory, prompts, logs`). Top of tree:

```
6,970,888  deepseek_resized.png                      (+ the same 6.9 MB blob twice under archived/)
6,970,888  archived/RECOVERED-FROM-LOCAL/workspace-snapshots/snapshot-archive-00{1,2}-…/deepseek…
3,960,328  check_arch                                 (+ duplicated in both snapshot archives)
3,074,983  data/crab-trap/agent-registry.jsonl
2,056,706  data/zeroclaw/logs/zc-weaver.jsonl        (+ duplicated in both snapshot archives)
```

`archived/RECOVERED-FROM-LOCAL/workspace-snapshots/` holds two full dated snapshots
(`…-2026-04-25`, `…-2026-05-01`) that re-carry the same large blobs as the live tree. Git dedupes
identical blobs, so the *tree* figure is honest, but the workspace carries two generations of
snapshot side by side. This is where I would look next for genuine secrets exposure
(prompts + logs + registry), but I did not complete a credential sweep inside it and am not
claiming one.

---

## Method notes / corrections worth keeping

- **A `&&` chain lied to me mid-scout.** I chained `git ls-files | grep -c "^test/"` into a
  `&& npm test`; `grep -c` exits 1 on zero matches, so `npm test` never ran and the `EXIT CODE = 1`
  I first printed was **grep's** exit code. On a hunt for false greens this is the most dangerous
  possible instrument error — it would have inverted a finding. Re-ran isolated, separately.
- My first vendor-strip regex omitted `.zig-cache`/`zig-out`, which put a build-cache repo at the top
  of the substance ranking. The Zig finding only appeared because the raw file list was read.
- `workspace:*` and `file:../` are the same defect wearing different clothes: a dependency that only
  resolves inside a monorepo the repo does not ship. Second instance, and the first one with CI.
- Reporting a negative as a finding: two 3-file repos, one repo whose only "test" is a 4-byte text
  file, and one repo that ships a 40-test certification standard with no tests are all findings, not
  filler.

## Not verified / open

- `claw-in-plato` cross-port agreement — needs `qemu-aarch64` (aarch64 binary, x86-64 sandbox).
- No `cargo`, `rustc`, `zig`, `julia`, or GPU in this sandbox: `holodeck-zig`, `claw-in-plato`,
  `herdr-cocapn`, `quilt-core-os` (Rust parts) were **inspected, not executed**.
- `quilt-core-os` CI is `failure` on both runs; I did not determine which step fails.
- No credential sweep completed inside `oracle1-workspace`.
