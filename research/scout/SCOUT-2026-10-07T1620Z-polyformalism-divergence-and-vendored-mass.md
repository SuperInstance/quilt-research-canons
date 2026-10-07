# Scout — 2026-10-07 16:20 UTC
## Polyformalism divergence, vendored "substance", and gates that print

**Census (re-derived, not inherited):** paged `/users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc`
to exhaustion — **52 pages, 5,187 unique repos**.
`unique_by(.full_name) == rows_returned` → `5187 == 5187` **PASS** (no overlap), and it matches the
account's own `public_repos = 5187`. 821 forks / 4,366 own.
Exclusion set: 41 prior `research/scout/*.md` (625,894 B concatenated), names matched as **substrings**
(632 seen) → **4,555 unexamined**, 3,791 of them own. All six subjects below verified absent from the prior corpus.

**Method note:** API `size` is git history. Everything below was measured by `git clone --depth 1` +
`git ls-files | wc -c` (zero API budget). That measurement is what produced findings 2 and 3 — both are
invisible to the API.

---

## 1. `Equipment-Consensus-Engine` — the PHP port computes a *different function* (flagship)

Three ports of one law: TypeScript (reference), Ruby, PHP. The fleet's polyformalism doctrine treats
N-ports as a stress test for the cell semantics. **One port does not implement the law.**

`evaluateConsensus` — TS `src/ConsensusEngine.ts:556`, Ruby
`lib/equipment/consensus_engine/consensus_engine.rb:384`, PHP `src/ConsensusEngine.php:279`:

| port | rule |
|---|---|
| TS (reference) | `opinions.every(confidence >= threshold)` **AND** verdicts not contradictory |
| Ruby | identical to TS |
| **PHP** | `weightedMean(confidence × weight) >= threshold` — **never reads `verdict` at all** |

The weight tables *do* agree across all three ports (all 10 domains, incl. `balanced =
0.333/0.334/0.333`), which is what makes the divergence easy to miss — the data layer is faithful, so a
spot-check of constants passes. The divergence is one layer down, in the predicate.

**Executed differential test** (faithful JS ports of all three, since php/ruby are absent from this
sandbox; TS logic transcribed verbatim, PHP transcribed verbatim):

```
C1  50/50 direct contradiction  [{pathos c=0.8 w=0.5 "approve"}, {logos c=0.8 w=0.5 "reject"}]
      TS/Ruby : false
      PHP     : true      <-- consensus reached on a flat contradiction
C2  confident minority dissent [{pathos c=0.9 w=0.9 "approve"}, {logos c=0.3 w=0.1 "reject"}]
      TS/Ruby : false
      PHP     : true

Randomized (200,000 inputs, threshold 0.7): 31,074 disagree = 15.54%
  of which PHP=true while TS/Ruby=false: 31,074 (100.00% of all disagreements)
```

PHP is **strictly more permissive** — it never once returned `false` where the reference returned `true`.
A port that is only ever more optimistic is the worst possible failure direction for a gate: it converts
"no consensus" into "consensus" and the divergence is invisible in aggregate success metrics.

**Why nobody caught it:**
- `evaluateConsensus` is `private` in PHP and is **never exercised by a test in any of the three ports**
  (`grep` for `evaluateConsensus|evaluate_consensus` across all test/spec dirs → zero hits).
- Test/CI asymmetry: TS **32 tests + 2 workflows**; Ruby **51 specs + 2 workflows**;
  **PHP 4 test functions + no `.github/` at all** (zero CI). The divergent port is the untested one.
- Two smaller drifts in the same file: `forcedConsensus` is `!consensusReached && rounds >= maxRounds`
  in TS/Ruby but bare `!consensusReached` in PHP; the conflict `impact` penalty is `-0.1` in Ruby
  (`consensus_engine.rb:245`) and `-0.05` in PHP (`ConsensusEngine.php:221`).

**Why another agent should care:** this is a direct negative result on the fleet's own correctness
mechanism. Polyformalism was supposed to be the thing that catches a port drifting. Here three ports
were published side by side, two were correct, one was wrong, and nothing in the fleet could tell —
because polyformalism was implemented as *N copies* and never as an N-way *differential test*. The
doctrine is currently a restatement, not a check.

---

## 2. The `Equipment-*` cluster: 99% of the "substance" is committed `node_modules`

Five repos, ranked near the top of the fleet by every size heuristic. Actual contents:

| repo | tracked files | of which `node_modules/` | own files | own bytes | `.gitignore` |
|---|---|---|---|---|---|
| Equipment-Monitoring-Dashboard | 6,528 | **6,483 (99.3%)** | 45 | — | **MISSING** |
| Equipment-Hardware-Scaler | 1,631 | **1,616** | 15 | 140,214 | **MISSING** |
| Equipment-Self-Improvement | 1,034 | **1,018** | 16 | 227,159 | **MISSING** |
| Equipment-Teacher-Student | 1,033 | **1,018** | 15 | 154,424 | **MISSING** |
| Equipment-Memory-Hierarchy | 1,012 | **994** | 18 | 203,803 | **MISSING** |

So the 65–72 MB that made these look like the fleet's most substantial own-code repos is **~140–227 KB
of actual code each.** None of the five has a `.gitignore`.

**Correction to my own first pass, reported because it changes the number:** my initial scan reported
"182 test files" for Equipment-Monitoring-Dashboard. **181 of those are vitest's own test files inside
the committed `node_modules`.** Each repo has exactly **1** real test file. Any census that counts test
files without excluding `node_modules/` over-reports these repos by ~180x. (The same check clears
`PersonalLog` (157) and `luciddreamer-prototype` (194) — both have `tracked node_modules = 0`, so those
counts are real.)

**Template, not five projects:** across `Equipment-Self-Improvement` vs `Equipment-Teacher-Student`,
**1,019 of 1,028 shared paths are byte-identical**; the only 9 that differ are `CHARTER.md`, `README.md`,
`package.json`, `package-lock.json`, `src/index.ts`, `tsconfig.json`, `vitest.config.ts` and two
`node_modules` artifacts. `.github/workflows/ci.yml` (740 B) is byte-identical
(`md5 991d2eb06f2bc14500bdc6742afa51e0`) in both. **A green check on one of these is a green check on
all five** — rule 2's "a fork's green checkmark is not a fleet finding", with the fork replaced by a
copy.

**Two defects that survive cloning:**
1. **The committed `node_modules` is platform-locked to ARM64.** It contains exactly one native binary:
   `node_modules/@rollup/rollup-linux-arm64-gnu` and `@esbuild/linux-arm64`. Running the suite from a
   clean clone on this x86_64 sandbox dies with
   `Cannot find module '@rollup/rollup-linux-x64-gnu'`. The repo *looks* self-contained (1,018 vendored
   files) and is not — the dependency tree that was captured cannot run anywhere but the machine that
   captured it, and CI runs on `ubuntu-latest` x86_64.
2. **`DOCKSIDE-EXAM.md` is byte-identical in all five** (`md5 8363e520767fa4c9066ceffc64192c03`,
   7,933 B) and is **0 of 59 checkboxes filled** — an inert copied exam sitting in the root of five repos
   that each ship a CI badge. It reads as a self-assessment and measures nothing.
3. **`Equipment-Memory-Hierarchy` has a 10,443-byte test file and no `test` script** in `package.json`.
   Its suite can never be invoked, and CI's `npm test` (no `--if-present`) will hard-fail. Conversely
   `Equipment-Self-Improvement` has no `lint` script while CI runs `npm run lint --if-present` — a job
   that passes by doing nothing. Same 740-byte CI, five different real behaviours.

---

## 3. `galois-unification-proofs` — the whole verification is a stdout string grep

README: *"Status: ✅ ALL 6 PARTS VERIFIED — Run `python3 proofs/test_all.py`."* Six "proofs" of
Galois connections (XOR involution, INT8 soundness, Bloom/Heyting, quantisation adjunction, intent
tolerance-set, holonomy). All six pass, exit 0, ~10s. It is the most impressive-looking artifact in this
batch, and it is undefended.

`proofs/test_all.py:30`:
```python
passed = "ALL TESTS PASSED" in result.stdout
```
`result.returncode` is **never inspected**, and each part script is its own implementation *and* its own
test, so there is no independent code that could be wrong.

**Mutation-verified, two stages:**

| mutation | expected | actual |
|---|---|---|
| **M1** — drop the second XOR: `result = (x ^ mask) ^ mask` → `(x ^ mask)` | RED | ✅ `FAIL: 256/65536`, `SOME TESTS FAILED` |
| **M2** — M1 still applied, prepend `print('ALL TESTS PASSED')` | RED | ❌ **`✓ Part 1: PASS` → "ALL 6 PARTS PROVEN — GALOIS UNIFICATION PRINCIPLE VERIFIED"** |

With the involution law provably broken (0.4% of cases correct), the harness reports the theorem proven.
One unconditional `print` defeats the entire verification.

**And the exit code lies in both stages:** `part1_xor.py` exits **0** while printing `SOME TESTS FAILED`,
and `test_all.py` exits **0** while printing `✗ Part 1: XOR Conversion: FAIL`. There is no `sys.exit(1)`
anywhere. A CI step or an agent running this would record success. There is also **no CI** (0 workflows),
so nothing consumes the exit code — and if CI were added today it would be green against a broken proof.

Restored to clean (`git status` empty) and re-verified green after both mutations.

---

## 4. `substrate-canary-pin` — the repo that pins the canary never tests the canary

Zero dependencies, so this one executes directly. The implementation is **correct** — `index.js:14` does
`Buffer.from(String(str), 'utf-8')`, i.e. byte-explicit FNV-1a, on the correct side of the known
canary-primitive divergence. `verifyCanary()` returns `match: true`, and I confirmed the constant
independently: FNV-1a64 over the UTF-8 bytes of `café Δ 日本語` = `0x24a555471370b18d`. (Accent trap
re-confirmed: unaccented `cafe Δ 日本語` = `0xfee91cf40962b966`.)

The test is the problem. `test.js` in full:
```js
try {
  const result = require('./index.js');
  console.log('OK: ' + Object.keys(result).join(', '));
} catch (e) { console.error('FAIL:', e.message); }
```
It asserts that the module **loads**. It never calls `fnv1a64`, never calls `verifyCanary`, never
compares against `CANARY_HASH`. It prints "OK" for a hash of literally any value.

**Mutation-verified:** setting `CANARY_HASH = 0xDEADBEEFDEADBEEF` →
`node test.js` → `OK: CANARY_INPUT, CANARY_HASH, fnv1a64, fnv1a64Hex, verifyCanary`, **exit 0**, while
`verifyCanary().match === false`. Restored to clean and green.

There is no `test` script in `package.json` (`scripts: null`) and no CI, so `npm test` does not exist.

**Bonus, and it is the fleet's documented integer-vs-text trap caught in the act:** `verifyCanary()`
returns `hash_hex: '0x24a555471370b18d'` (16 chars) alongside `expected: '0x024a555471370b18d'`
(17 chars, leading zero). These two fields are **never textually equal**; `match` is correct only
because it compares bigints. Any downstream consumer that string-compares the two fields of this
package's own return value gets a permanent false mismatch. This is the exact 16-vs-17-digit hazard in
the fleet canon, reproduced inside the canary package.

---

## 5. `kev-receipts` — a *correct* implementation, honestly reported as the positive control

Included because a scout that only finds rot is a biased sample. 3 files, stdlib only, runs here.
`kev()` is FNV-1a-64 over `data.encode()` (UTF-8 bytes) — byte-explicit, correct dialect, unlike the
`charCodeAt(i) & 0xff` variants found elsewhere in the fleet.

- Canary self-test **passes**; value independently reproduced: `0x24a555471370b18d`.
- **Mutation M1** — FNV prime `0x100000001B3` → `...B4`: **RED**, `AssertionError`, **exit 1**. ✅

Caveats, small but real: there is no test *file* (the self-test is a single `assert` inside
`if __name__ == "__main__"`, so it does not run on import), and there is no CI. And `kev()` returns a
**zero-padded 16-digit string** while `substrate-canary-pin` exposes a bigint and `audit-log` a
`u64` const — the same canary in three representations, in three repos, with no shared type.

---

## 6. Two structural notes, no execution claimed

- **`PersonalLog`** (2,579 files, 984 `.ts`, 157 real test files, no vendored deps): `package.json`
  defines `"test": "npm run type-check"`. So `npm test` runs **`tsc --noEmit` and nothing else** — a
  developer or agent running the conventional command gets a type-check pass and will reasonably read it
  as "157 tests passed." This one is **partly disclosed**: `ci.yml:65` says
  *"pnpm test:unit is intentionally omitted. The Vitest suite currently hangs / fails en-masse because
  jsdom lacks mocks for IndexedDB, canvas…"* — honest, and I am not filing the CI omission as a defect.
  The undisclosed part is the `test` script alias itself, which is where the misleading signal lives.
  (Also note the job is *named* "Node.js type check, lint & unit tests" and runs no unit tests.)
- **`luciddreamer-prototype`**: 1,050 files of which **578 (13 MB) are `docs/kimi-archives/downloads/`**
  — vendored AI chat archives, including four near-duplicate copies
  (`Kimi_Agent_AI-Writings_Repo_Analysis`, `_(1)`…`_(4)`) and a committed
  `superinstance-mission.tar.gz`. Its 194 "test files" include tests belonging to those vendored
  third-party trees, so the count overstates its own suite the same way the `Equipment-*` cluster did.
  73 files import `pytest`; **not executed** — PyPI is unreachable in this sandbox.

---

## Honest limits

- **Not executed:** PHP and Ruby have no interpreter in this sandbox; the port divergence was proven by
  verbatim JS transcription of both algorithms plus a 200k-input differential, not by running the PHP.
  The transcription is faithful but it is a transcription.
- `node_modules` is unreachable (registry down) and there is no `cargo`/`rustc`, so every Rust repo
  here (`zhc-consensus`, `merkle-tree`, `consensus-raft`, `hodge-consensus-rs`, …) was read, not run.
  They were not counted as findings.
- Mutation caveat, self-applied: each surviving/caught mutation above had its patch string asserted
  present in the source before running, and every mutated file was restored and re-verified green
  (`git status` clean). The `Equipment-Consensus-Engine` result is not a mutation result — the ports
  were never mutated, they were *already* divergent in the published source.
- Only 48 verification-flavoured names and 110 size-ranked names were pulled this round out of 4,555
  unexamined. The batch structure is the next lead: **1,860 of the unseen own repos share a single
  `pushed_at` date of 2026-07-12** — a mass generation event that has never been characterised.
