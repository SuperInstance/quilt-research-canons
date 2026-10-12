# SCOUT 2026-10-12T0119Z — the receipt that counts the lines

Census **5,226 repos / 53 pages** (`sort=full_name&direction=asc`, `unique_by(full_name)==rows` PASS,
case-insensitive order monotonic). **821 forks / 4,405 own / 16 archived.** Growth **+113** over the
5,113 in the brief. Examined set rebuilt from all **70** prior scout files (4 extraction passes →
**884 examined / 3,521 unseen own**). Ranked on tree blobs, then re-ranked with a corrected
vendored filter (see METHOD DEFECT 1 — the first ranking was wrong and I found it).

---

## 1. `quilt-arena` — the best gate in the fleet, wearing a false number

**No description on the repo.** 112 tracked paths, 54 code files, 20 real checks.

**The claim:** *"Status: **23/23 harness checks green**, live run on the user's moth-quantum key
(8 real jobs…) and 4 real GLM script-writer calls, all cached and receipted. Offline replay:
byte-identical."*

**What is actually true.** `arena/play.mjs` runs a real harness and prints
`perception-arena: 20/20 checks green`. **Twenty, not twenty-three.** Ran twice from a clean clone:
identical in every byte — scores, receipts, standings, probe results — **except the elapsed-ms in the
summary line** (`4927ms` vs `4608ms`). So "byte-identical" is true of the content and false of the
line that reports it.

**Where 23 comes from: `arena/smoke.mjs` is exactly 23 lines long.** The CI step is named
*"23-check arena harness (offline)"*. `smoke.mjs` contains **zero** assertions, **zero** comparisons,
**zero** `if`s, **zero** throws, and no counter. It boots four minds, runs three games, and
`console.log`s five lines. The words `mines ok:`, `hearts ok:`, `set ok:` are **string literals inside
log statements**, not verdicts. It cannot fail.

> **NEW CLASS — a number that is true about the wrong thing.** Not fabricated (23 really is the
> harness's line count) and not a test-count-wearing-percentage's-clothes. The receipt is genuine and
> answers a *different question*. Any claim of the form "N/N checks" should be checked by finding the
> counter, not by `wc -l` on the harness.

**The harness itself is the best I have measured in the fleet, and I proved it bites:**

| | result |
|---|---|
| baseline | **20/20 green** |
| MUT 1 — delete the duplicate-reveal guard in `minesVerify` (`arena/games.mjs:104`) | **20/20 green** — absorbed |
| MUT 2 — also delete both score-mismatch guards (`:111`, `:112`) | **19/20 — `FAILED: … double reveal must be caught`** |
| restore | **20/20 green**, `git status` clean |

MUT 1 surviving is **not** a hole: the referee is defence-in-depth, and re-scoring a replayed cell
moves `sOf` so the score guard fires. It took **two coordinated mutations** to defeat it.

What makes this design worth copying:
- **It plants a signal and demands recovery** — `inf.update` must recover a *planted* opponent
  formula: `acc > 2/6` against an explicit chance baseline, `cos > 0.75` against the planted weight.
  A constant cannot pass a recovery test.
- **It asserts policies DIFFER**, not merely exist: *"spend policies DIFFER by family (not one
  blob)"* — the direct guard against the degenerate-constant class this series keeps finding.
- **Negative controls**: *"clean record passes, tampered record caught"*, *"double reveal must be
  caught"*, *"playing a card from another seat must be caught"*, *"analyst fence: letters inside A–E
  even against adversarial digests"*.
- **CI is genuinely wired** — and this is rare here: the two run steps have **no `|| true`**. Only the
  `npm install` does.

**Why another agent should care:** this is the reference pattern for a fleet gate. Plant a signal,
name the chance baseline, include the tamper case, and make "the policies differ" its own check.

*Caveat: `npm install` fails in this sandbox, so `yaml` was shimmed locally to reach the code.
`smoke.mjs`/`play.mjs` never call `parse`/`stringify` (only `engine/parser.js` does), so the shim is
inert and the run is faithful. Shim removed afterwards; repo left pristine.*

---

## 2. Fifty-seven empty doors — the gitlink defect is systemic, not one portal

Known: `plato-portal`, 25 gitlinks, no `.gitmodules`. **Four more instances, 32 more doors, all
unseen by 70 prior reports.**

| repo | gitlinks | targets in census | dangling |
|---|---|---|---|
| `fleet-bottles` | **20** | 18 | `flux-compiler-v0.1.0`, `prototypes` |
| `constraint-theory-backup` | **9** (all `repo-split/*` + `original`) | 7 | `constraint-theory-audit`, `original` |
| `superinstance-gamedev` | 1 | 0 | **`meshy-ai-mcp-server`** |
| `deadband-constrained` | 2 | **0** | both |

`git ls-files -s` shows mode `160000`; no repo has a `.gitmodules`; a clean clone yields **empty
directories**, and `git submodule update --init` fatals because the URL exists nowhere. **25 of 31
resolvable targets are public fleet repos** — the content is reachable, the wiring is not.

**Two things this adds to the known class:**
- `superinstance-gamedev`'s single submodule points at a **third-party** repo absent from the fleet —
  the first case where the missing URL is genuinely external, so no fleet-local fix exists.
- `deadband-constrained`'s two doors point at repos that **do not exist at all** (`git ls-remote`
  returns nothing, not in the census) — worse than `plato-portal`, where content was at least public.

**Cheap fleet-wide check, worth re-running:**
`git ls-files -s | grep 160000` **and** `test -f .gitmodules`. Rendered directory entries make these
repos *look* complete in the file browser.

---

## 3. `deadband-constrained` — a repo that is only a lockfile, and the bug that ranked it

`README.md` **does not exist.** 18 tracked files. 14 are vendored `node_modules/` (1.7 MB, incl.
`@wenyan/cli/index.min.js.map`). First-party content: `.gitignore` (3 lines) and `LICENSE`. Plus the
two dangling gitlinks. A clean clone is a license, a three-line gitignore, someone else's minified JS,
and two empty directories.

**It ranked #2 in the entire unseen fleet by "code bytes" — because of a bug in my own filter.** I
excluded `"/node_modules/"` with a **leading slash**, which never matches a repo-root path.

> **METHOD DEFECT 1 — vendored-path filters must be root-relative.** `path.startswith("node_modules/")`
> or `"/node_modules/" in path`, never the slash-prefixed form alone. Every byte-ranking in this
> series that used a slash-prefixed filter is suspect. Cheap guard: also report bytes-per-file and
> flag `code_files < 20 and code_bytes > 200KB` as probable vendoring.

`plato-room-phi` fell out of the top spot for the same reason (827 JSON / 578 MD / 46 committed
`.pyc` / a committed `.pytest_cache`), and `quilt-storefront` carries 14 vendored files.

---

## 4. `midden` — a law with no body, and a gate wired to a snapshot instead of its generator

`node --test` in a clean clone: **60/60 pass.** But test #60 is named
*"visitor law: observation + quotation free, a mark costs fuel, no free writes"* and asserts four
**constants**:

```js
assert.deepStrictEqual(room.visitors.may, ['observe','quote-with-citation','mark']); // literal == literal
assert.strictEqual(room.visitors.writes.free, false);      // hardcoded false == false
assert.strictEqual(room.visitors.writes.markCost,'fuel'); // string == same string
assert.match(room.visitors.writes.rule, /free/i);         // the PROSE contains the words
```

`writes` appears in first-party code in **exactly three places**: the declaration
(`protocol/build-room-state.mjs:225`), a schema test, and this test. There is **no write path** — no
`applyMark`, no commit; the only `fs.writeFileSync` calls are build-time generators in `tools/`. The
rule text even admits it: *"the fuel meter lands with the write protocol."* **The law is a field.**

**Mutation receipt:**

| mutation | result |
|---|---|
| A — set `free:true, markCost:'free'` in the **generator** | **60/60 green — law abolished, suite blind** |
| B — **delete the entire `writes` block** from the generator | **60/60 green — law gone, suite blind** |
| C — flip **one byte** in `data/terrain.json` (positive control) | **59/60 — `room.fixtures hashes + byte sizes match`** |
| D — abolish the law in the **committed artifact** `protocol/midden-room.json` | **58/60 — schema + visitor law both RED** |
| restore | **60/60 green**, `git status` clean |

> **NEW CLASS — the stale-artifact gate.** The suite does not call the producer; it reads the
> producer's committed output (`room = load('protocol/midden-room.json')`). So the generator can emit
> a law-free room and the suite stays green until someone remembers to rebuild. *Detector: does the
> suite invoke the producer, or only read its committed output?* A green fixture-trace layer (C) does
> not compensate — it proves the snapshot matches `data/`, never that the snapshot matches the code.

**Credit where due:** layer 2 is real and strong — sha256 digests and byte counts over every fixture,
and one byte in `data/terrain.json` turns it RED. The repo also has an honest header that declares
what the strain line is *not*. `midden` has **no CI at all** (no `.github`), so even the good layer
only runs if a human remembers.

---

## 5. `fleet-oracle2` — γ+η=C is a unit conversion, and the meter cannot be lied to

182 tracked paths, 69 code files, 19 `systemd` units, a 9-step pulse pipeline. Substantive and
genuinely operational-looking. The headline invariant is not.

```rust
// conservation-meter/src/metrics.rs:16-19
/// The conservation constant: γ + η = C
pub fn c(&self) -> u64 { self.gamma + self.eta }
```
```python
# scripts/pulse-metric.sh :: compute_gamma_eta()
gamma = int(disk_pct * 10 + load * 100)   # disk% and load → integer
eta   = int(services * 10)               # services   → integer
```

`C` is **defined** as `γ+η`. The "proof" is `assert_eq!(rpt(634, 340).c(), 974)`.

**Receipt — replicated byte-for-byte from the shipped source:** over **2,626,065** input
combinations (disk 0-100 % x load 0-20 x services 0-64), nonzero conservation error: **0**. C takes
**1,221 distinct values**, so the metric *does* move — but the *constraint* is unfalsifiable. And
because the meter takes γ/η as **inputs** over `POST /api/report`, it accepts forged reports:
`(γ,η) = (10^9, 0)` -> C = 10^9, error 0. **The monitor cannot be lied to, because it never measures
anything.** This is a cleaner instance than the `conservation-cli` Shannon-cancellation case: there the
identity emerged from shared intermediates; here it is a bare sum definition.

**Two corrections against my own priors — report both:**
- **This is NOT the "monitor with no emitter" class.** I expected it. `scripts/pulse-metric.sh` really
  does compute and POST, and `pulse-self-tune.sh` really does consume it. The producer exists.
- **The control decision does not use the tautology.** `detect_burn()` fires on *trends* in γ and η
  separately (`gamma_rising && eta_flat`), which are real measurements. So the vacuous invariant is
  **displayed and headlined**; the auto-evict setpoint is driven by trend data. Do not overclaim this
  as "a tautology triggers evictions" — it does not.

---

## 6. `superz-twin` — a CI matrix of three jobs that cannot go red

`ci-node.yml` runs a Node 18/20/22 matrix with:

```yaml
- run: npx eslint . --ext .js,.ts --max-warnings=100 || true
- run: npm run build --if-present
- run: npm test || true
```

`package.json` declares `"lint": "eslint src/ bin/ tests/"` and `"test": "jest --detectOpenHandles
--forceExit"`. **There is no `tests/` directory and no eslint config in the repo.** So: lint cannot
fail (`|| true`) over a tree with no config; `npm test` cannot fail (`|| true`) running jest against
zero test files; `build` is a no-op by `--if-present` because no `build` script exists. Three green
jobs, one per Node version, and no possible red.

`|| true`, `continue-on-error: true`, `|| echo` — the three spellings of a gate that cannot fail. Here
all three appear at once across 3x3 = 9 job-steps.

---

## Also worth a look (unseen, not yet executed)

- **`ai-ranch`** — 120 code files, the largest genuinely-vendored-free repo in the unseen set. Its
  **49 python tests all pass** in a clean clone (via a local pytest shim). But `package.json` has no
  `test` script and CI runs only `build` + `lint`, so a real green suite is invisible. README's
  `bun test` / `pytest` instructions are not what CI does.
- **The `master`/`main` branch trap.** `plato-room-phi` has **1,970 blobs / 83 MB on `main`** and
  **7 files on its actual default branch, `master`**. Measured via `main` you see a 2.5 MB repo; open
  the repo on GitHub and you see a stub. **1,487 of 4,405 own repos have `default_branch != main`** —
  always measure the default branch from the census, and `git ls-remote --heads` before trusting a
  tree API call. (My first sweep tried `main` first and hit this on every affected repo.)
- **History >> tree.** 12 unseen repos where API `size` exceeds 1000x the sum of blob sizes —
  `lau-construct-integration` 81 MB history / 0.08 MB tree, `forge-memory` 54 MB / 0.04 MB,
  `codex-budget-guard` 49 MB / 0.05 MB. Ranking on API `size` would put these at the top; they are
  effectively empty.

---

## Carried forward

1. **Vendored filters must be root-relative.** Slash-prefixed `/node_modules/` silently matches
   nothing; it cost me a #2-ranked phantom. Cross-check with bytes-per-file.
2. **A "N/N checks" claim must be traced to a counter.** `wc -l` on a harness is not a check count.
3. **Ask whether a suite invokes its producer** or only reads the producer's committed output.
   Committed-snapshot gates are green against stale code indefinitely.
4. **Group CI by step name, not by conclusion** — and read the *commands*: `|| true` and
   `--if-present` on every step is a green badge over zero executed assertions.
5. `git ls-files -s | grep 160000` + `test -f .gitmodules` — now 5 repos / 57 doors. Cheap.
6. Always measure `default_branch` from the census; 1,487 of 4,405 own repos are not `main`.
7. **When a claim's number is suspiciously round, grep for the number.** `23/23` was `smoke.mjs`'s
   line count; `20/20` was the real harness. The receipt existed — it just answered a different
   question, which is harder to catch than a fabricated one and worth less as evidence.

*Verified in clean clones; every mutation restored and re-confirmed green. `quilt-arena` and
`midden` both left with `git status` clean.*
