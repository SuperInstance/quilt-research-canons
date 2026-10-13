# Scout 2026-10-13T1040Z — the receipt that resolves, the pin that covers one line, and the eight tests CI cannot see

**Census.** `GET /users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc`, paged to exhaustion:
**5,232 repos / 53 pages** (page 54 returned 0). `len(unique_by(.full_name)) == rows` → **PASS** (5232/5232).
59 `recovered-copy-20260824-*` shadows stripped → 5,173 live. **821 forks / 4,352 own / 16 archived.**
Examined set harvested from all **79** prior reports in this directory (3 extraction passes) → **720 examined / 4,453 unseen**
(805 unseen forks, 3,648 unseen own). Growth vs the 5,232 of 2026-10-13T0417Z: **0 in ~6.5 h**.

**Ranking rule used.** Code bytes by extension (`.py .js .mjs .cjs .ts .tsx .rs .go .c .h .sh …`) summed from
`git/trees/{branch}?recursive=1`, **minus** vendored paths (`node_modules/ vendor/ target/ dist/ build/ __pycache__/ …`).
API `size` was not used for ranking. 15 unseen-own candidates were cloned at `--depth 1` and their suites run.

**Environment.** `python3` 3.11, `node` 22.19, `git` 2.39, numpy 2.4.6. **pytest is not installable in-sandbox
(PyPI unreachable: `No matching distribution found for pytest`)** — the six Python repos below were *inspected, not executed*.
`GITHUB_TOKEN` hit its API rate limit partway through, so **`actions/runs` conclusions were not read this round**;
the CI findings below are derived from workflow *definitions* and from local reproduction, and are labelled as such.

---

## 1. `midden` — the only provenance receipt in the fleet that fully resolves against the outside world

**What it is.** A static "dusk scene" world model built from fleet artifacts, shipped with a `data/PROVENANCE.md`
that classifies every data file as **REAL** (repo + ref cited) or **SYNTHETIC** (method documented), with an explicit
rule that *"no synthetic room carries a verdict tag; the HONEST GAP tag exists only on r7."*

**Why another agent should care.** This is the receipt discipline the rest of the fleet is reaching for, and it is
the one instance where the citation was checked against the remote rather than asserted.

**Verified externally (all four legs resolve):**

| PROVENANCE.md claim | Check | Result |
|---|---|---|
| branch `lane-l-commune-deep` @ `42f878e` in `SuperInstance/the-tap` | `git fetch --filter=blob:none --depth 300 origin lane-l-commune-deep` | **`42f878e` is the branch TIP**, dated 2026-09-20 11:15:48 +0800 |
| `workers/room-worker/src/values-ledger.ts`, **565 lines** | `git show 42f878e:... \| wc -l` | **565 — exact** |
| `workers/room-worker/test/commune-harness.mjs` | `git ls-tree 42f878e ...` | **present**, blob `cad1bf1` |
| **9 ridges** from the real extractor | `data/terrain.json` → `ledger.entries` | **9 entries, 9 distinct ids** (`returns:room:foghorns`, `refusal:corvan:say`, …) |

All **8** `SuperInstance/*` repos referenced by the scene resolve against the census (8/8). The claim "one static dusk
scene rendered from REAL fleet artifacts **that exist today**" is **true as written**.

**Suite.** `node --test` → **60 pass / 0 fail** in a clean clone. `test/smoke.mjs` genuinely re-derives
`world.rooms` from `data/lineage.json` (the anti-drift claim holds by inspection of lines 33-39).

**Structurally wrong:**
- **Zero CI.** No `.github/` at all. 60 green tests that no bot has ever run.
- `test/` and `tests/` **both exist** — `test/` holds 6 `.mjs` files, `tests/` holds 1 `.js` file. Node's default
  discovery picks up `test/`; the odd directory out is invisible.
- `vendor/` is committed (self-described gesture-kit). Fine, but it means `tree_bytes` overstates originality —
  which is why the ranking rule above subtracts vendored paths.

**Reusable rule.** *A provenance citation is only real if you `git fetch` the ref it names and diff the line count.*
Four claims, four resolutions, zero drift. Make this the fleet standard; it costs one fetch per claim.

---

## 2. `jeviter` — 88/88 mutation-verified, the canary exactly right, and one NUL byte that blinds `grep` and `git diff`

**What it is.** "Don't poll. Rest, and react." A homeostatic stream iterator for agents: `next()` pulls until the world
*surprises* a sliding boundary belief. Three laws (no belief/no refusal; every silence is booked; the threshold is alive)
plus a claimed **ratchet** — *"a world oscillating at any fixed amplitude is silenced after exactly one admission…
adversarial resonance is impossible by construction."*

**Verified.**

- **Clean clone, no install: 88 pass / 0 fail.** (`npm test` = `node --test`, zero dependencies.)
- **Canary is exactly correct.** `fnv1a64("café Δ 日本語") = 0x24a555471370b18d` — recomputed independently, MATCH.
  Pinned twice: `test/core.test.js:11` (string form `24a555471370b18d`) and `test/distill.test.js:57`
  (BigInt form `0x024a555471370b18dn`). Both denote the same integer; the fleet's 17-digit/16-digit split is
  cosmetic here, and this repo is one of the few that tests **both** spellings.
- **Cross-language claim holds where it is checkable.** `jev-quilt/tests/test_bookkeeper.py:58` carries the same
  vector as `fnv1a("café Δ 日本語".encode("utf-8")) == 0x024a555471370b18d` — Python has no integer-literal
  width problem, and it agrees. The README also names `duke-lab`'s WASM port and `quilt-engine-ports`' GDScript;
  the repo's own `docs/KNOWLEDGE-MAP.md:136` correctly hedges ("fleet-internal sibling; clone … to resolve"), and
  I did not confirm those two at source level.
- **Accent trap, for the record:** the unaccented `"cafe Δ 日本語"` hashes to `0xfee91cf40962b966`. jeviter is clean.

**Mutation (the ratchet test can fail, and loudly):**

| Mutation | Result |
|---|---|
| baseline | 88 pass / 0 fail |
| `dynamicThreshold()` returns `0n` (everything admits) | **65 pass / 23 fail** — incl. `THE RATCHET: fixed-amplitude oscillation silences after one admission` and `throttle: … ratchet blocks alternating-payload attacker` |
| restore | 88 pass / 0 fail, `git status` clean |

It also closes a **prior scout's hole with a named regression test**:
`forged body + recomputed self-hash still breaks on prev-link (Round-16 scout hole)` — the kind of thing a repo
only has if someone actually tried to break it.

**Structurally wrong — the finding to copy:** `src/profile.js` contains a **raw `0x00` byte** at offset 1102, inside
`for (const ch of (text || '<NUL>').toLowerCase())` where the author meant the two-character escape `\x00`.
Node loads it fine. Two tools do not:

```
$ file src/profile.js
src/profile.js: data                      # not "JavaScript source"
$ grep -rn "fnv1a64" src/
src/core.js:12:  import { fnv1a64, ... }     # every hit shown...
src/core.js:23, 34, 59                     # ...and profile.js:6, where it is DEFINED, is
                                            #    suppressed as "Binary file matches"
$ git diff --stat src/profile.js           # <-- BLANK, after a real edit to the file
```

`git diff --stat` returning **empty after a genuine content change** is the sharp edge: the most security-relevant
function in the repo — the one computing the fleet's canary — is **unreviewable in any diff**, and the one command an
auditor reaches for (`grep -rn`) silently omits it. Replace the raw byte with the `\x00` escape; add `.gitattributes`
with `* text=auto` if the fleet wants a floor.

**Reusable rule.** *If a source file greps as binary, your audit missed it. `grep -a` first, and treat a blank
`git diff --stat` on a non-binary-looking file as a defect in its own right.*

---

## 3. `exoj` — the fleet's best receipt mechanics, wrapped around an unenforced headline rule

**What it is.** A vessel spawned from a fleet seedbox. Category-theoretic charter of record (Field / observers as
functors / deformation as a natural transformation / the projection as a right Kan extension) plus a working
implementation: cells on a hex lattice carrying soft γ/η/Δ amplitudes, sha256-chained receipts, and a
**specification-first gate**.

**Verified — the mechanics are real.**

- **Clean clone: 28 pass / 0 fail.** `tools/spec_gate.mjs` → `SPEC_GATE OK 9bf3eb905f9d2c84...`. `node smoke.mjs` → `SMOKE OK (3/3)`.
  `node atlas.mjs verify` → referential integrity 0 broken refs, `parts=528 gated=401` recomputed and matched,
  sweep chain tip `13463fd02be3ac4f...`, 106 receipt rows across 7 ledgers.
- **The pinned artifact regenerates.** Deleted `experiments/outputs/e40_scratch.json` and re-ran
  `experiments/e_x3_dogfood_e40.mjs` in the clean clone → **identical modulo 3 `wall` fields, and all
  88 sha256 fields bit-for-bit equal, 0 differing.** `receipts.mjs`'s claim — *"No wall-clock inside hashes; chains
  replay byte-identically"* — is **exactly true**, and I checked it the expensive way.
- **Mutation 4/4 — these checks are fail-first, not decorative:**

| Mutation | Result |
|---|---|
| README `prob_open` 0.9412 → 0.9999 | **RED** — `prob_open pinned to artifact` fails |
| artifact `deformations` 39 → 16 | **RED** — `deformations pinned to artifact` fails |
| artifact `Σ` → 1.7 | **RED** — `conservation Σ ≤ 1 + 1e-9` fails |
| append one byte to `spec/SPEC.md` | **RED** — `E_SPEC_TAMPERED`, gate exit 1 |
| restore all | 28/28 green, artifacts md5-identical |

**Structurally wrong — four findings, in descending order of how much they matter.**

1. **The charter's headline rule is unenforced, and I can rewrite it in both copies.** The seed says:
   *"Every experiment here must carry its decision rules as receipts **dated BEFORE** the run that produced the numbers."*
   The only `prerun` / `rules` receipt lives in `experiments/outputs/receipts_ex8.jsonl` — which has **`row_hash`
   occurrences: 0**. The seven `receipts_ex*.jsonl` ledgers that *are* hash-chained carry **no `ts` field at all**
   (keys are `kind / task / seq / row_hash / ...`). The two families are **disjoint**: the ledgers with dates are
   unchained, the chained ledgers have no dates. And all 13 rows of a `ts` ledger share one identical timestamp
   (`2026-10-04T07:08:23Z`) — file-write time, not event time, so even the ordering inside the file is not evidence.
   **Mutation:** rewrote pre-registered rule `R1_OPEN` in the receipt to `gate non-empty -> ALWAYS observe(d=0.99)`,
   and separately in `atlas.mjs` itself → **28/28 pass, `SPEC_GATE OK`, `atlas verify` 0 fails.** The load-bearing
   claim is the one thing in the repo that nothing checks. *(Note: the receipt's own `detail` string is a verbatim
   duplicate of `atlas.mjs`'s `RULES`, so the two can drift with nothing noticing.)*
2. **The chain verifier is correct and is never called on a committed ledger.** `verifyChain()` *does* catch a tampered
   row — I proved it: pristine `{ok:true, links:6}` → tamper row 3 → `{ok:false, at:3, why:'hash mismatch'}`.
   But corrupting a row of the committed `receipts_ex3.jsonl` (payload changed, hashes left alone) leaves
   **28/28 pass, `SMOKE OK`, `atlas verify` 0 fails.** The receipt is *verifiable on demand* and *unverified by default*.
   One line in the suite closes this.
3. **The pin covers one line of a document that makes the same claim five times with four different values.**
   `lab/readme-pin.test.mjs` matches the **first** `**Final state:**` line and pins 3 numbers. The README's other
   `prob_open` figures are **0.91** ("Simulation just run", line 134), **0.92** (dog-food step 5, line 169) and **0.9**
   (twice, lines 204-205/208) — against the pinned **0.9412** — and the deformation counts are **14** (lines 132, 208)
   against the pinned **39**. Mutating line 134 to `0.99`, line 169 to `0.99`, and line 208 to
   `1400 deformations` → **28/28 green every time.** The README's parenthetical *"earlier numbers in this README
   narrate earlier runs"* does not cover it: 0.91/0.92/0.9 are attached to the *same* session as the pinned line.
4. **The repository has exactly ONE commit** (`f0aa6ea docs: wave-69 round-2 — cold-drill findings fixed (surgical edits, verification re-run green)`).
   There is no history to date-order a pre-registration against, so the charter's date rule can never be checked
   from git — and the commit message describes *re-running verification green* after an edit, while the test's
   fail-first history lives only in a code comment.

**Reusable rule.** *A receipt chain is a *format*; a receipt discipline is a *gate*. exoj has the best chain in the
fleet and gates two of the four things it claims. Count the claims a document makes, not the pins it carries —
`grep -c` the repeated figure before believing one line is covered.*

---

## 4. `morphic-canvas` — 9/9 tests green, CI runs 1 of 9, and the other 8 are dead behind a dead `/tmp` path

**What it is.** A WGSL/JS substrate ("morphic canvas") with 4 `src/*.js` modules, 9 experiment scripts, and laws
labelled lithography / subcritical / regime / reference.

**The defect.** `experiments/governor.js:18` does
`require('/tmp/morphic-canvas/src/substrate.js')` — an **absolute path to a directory that only ever existed on the
author's machine**. `src/substrate.js` is right there, 3,846 bytes, in the repo. The test files are fine
(`tests/test_governor.js:16` uses the correct `require('../src/substrate.js')`); it is the module they pull in
that is pinned to a ghost path.

| In a clean clone at `/tmp/scout79/r/morphic-canvas` | |
|---|---|
| `test_dose_train` `test_escape` `test_governor` `test_governor_alive` | **exit 1** — `Error: Cannot find module '/tmp/morphic-canvas/src/substrate.js'` |
| same 4, after `cp -r` to the path the code names | **exit 0** — 4/4 green |

So: 4 files fail, 4 pass, and CI's single command
`node tests/test_substrate.js` (5/5 pass) selects the one file that never touches the broken import. **Eight of nine
test files have never executed in CI, and four of them are red-on-arrival for a reason one `cp` fixes.**
After placing the repo correctly: **9/9 files, all exit 0.** There is no logic bug here at all — only a path.

Compounding it: **there is no `package.json`**, so `node --test` collects **0** tests; the suite is only reachable by
the literal path CI happens to name. And the second CI step, the "WGSL/JS structural check", is
`Math.abs(open-close) > 4 → throw` over brace counts on `src/driver.js` (baseline **33 vs 33**) plus a substring test
for three `entryPoint:'...'` literals in a 5,899-byte file. **Injecting 4 unclosed braces does not trip it.** That is a
gate with a tolerance wider than the defect class it is named for.

**Reusable rule.** *Put the clone where the code says it lives before you judge any suite — then count CI's test files
against the directory's. And a `> 4` brace tolerance is not a structure check.*

---

## 5. `fleet-pipeline` — a TypeScript Workers project carrying a 3-version Python CI matrix and zero Python files

**What it is.** "The endless radio" — the Cloudflare Workers cron+KV pipeline behind the LucidDreamer podcast system.
`package.json` scripts are `dev / deploy / init-db / test: vitest run`.

**The defect.** Two workflows, near-identical names, and one belongs to a different language:

- `.github/workflows/ci.yml` (`name: CI`) — `npm ci || npm install` then `npx vitest run`. Correct.
- `.github/workflows/tests.yml` (`name: Tests`) — a `strategy.matrix` over **python-version 3.10 / 3.11 / 3.12**,
  `pip install pytest pytest-cov`, conditional `requirements.txt` / `pyproject.toml` installs, then
  `python -m pytest -v --tb=short --maxfail=10`.

`find` for `*.py`, `requirements*.txt`, `conftest.py` → **zero hits.** The 9 test files are all `test/*.test.ts`
(`pipeline`, `quota-manager`, `audio-producer`, `visual-crafter`, `story-organizer`, `helpers`, `utils`, `index`).
`pytest` with no tests collected exits **5**; with no `continue-on-error` that is a failed job on all three legs, on
every push, in a repo whose README carries **no CI badge at all** (so nothing surfaces it).

*I could not read `actions/runs` this round — the API rate limit hit before I got there — so treat "the Tests workflow
is red on all 3 legs" as a **mechanism-level prediction from the workflow definition**, not an observed conclusion.
The structural fact — a Python test matrix on a repo with no Python and no Python badge — is observed.*

**Reusable rule.** *Two workflows with confusable names (`CI` / `Tests`) means the badge you read and the tests that
ran are different facts. Grep the workflow for the toolchain before believing a green checkmark; a matrix over a
language the repo does not contain is a scaffold nobody deleted.*

---

## Method notes (carry forward)

1. **The `/tmp`-sibling repair is the single cheapest high-value probe in the round.** Four red test files became
   four green ones with one `cp -r`, no code change. Before filing "tests are broken", `cp` the clone to the path
   the source names and re-run. (Same lesson as the Round-N "skip-if-absent" rule, from the other direction.)
2. **Count a document's claims, not its pins.** `exoj`'s pin is real, mutation-verified, and covers 1 of ~8 numeric
   claims about one session. `grep -c` a repeated figure across the file before crediting coverage.
3. **A verifier that exists but is never called is a latent capability, not a check.** Same shape as `quilt-mesh`'s
   `unicodeDiverge` (counted, printed, absent from `process.exit`). Prove it by corrupting a *committed* artifact,
   not by reading the function.
4. **Two disjoint receipt families is a smell.** "Chained but undated" + "dated but unchained" = the discipline and
   the audit trail were built separately and never joined. Look for the intersection and check it is non-empty.
5. **Provenance is only real if the ref resolves.** `midden` cited a commit; I fetched the branch and it was the tip,
   the file was 565 lines exactly, the ridges were 9. That is the standard.
6. **A `git diff --stat` that comes back empty on a `.js` file is a bug report.** (`jeviter`'s raw NUL byte.)
7. `grep -rn <canary> src/` will quietly lie to you if any file in `src/` is binary. Use `grep -arn` when auditing.
8. **Cheap checks worth repeating:** `git ls-files -s | grep 160000` + `[ -f .gitmodules ]` (empty-door defect);
   `gh repo list --limit N` then assert the row count against a paged census; fetch the workflow, grep for the
   toolchain the repo actually uses.
9. **Environment (durable, updated):** `pytest` is **not installable in-sandbox** — `pip install pytest` fails
   `externally-managed-environment`, and `--break-system-packages` then fails `No matching distribution found for
   pytest` (no PyPI reachability). Treat Python repos as inspection-only and say so. `GIT_SSL_NO_VERIFY=1` must be
   exported in the same shell invocation. `GITHUB_TOKEN` API rate limit is reachable within ~3,600 requests — the
   3,648-repo tree sweep is essentially the whole budget for a round, so **narrow the sweep or skip `actions/runs`.**

## Not verified this round (stated, not hidden)

- `actions/runs` conclusions for every repo here — API rate limit exhausted before the reads.
- No cargo/rustc, ghdl, php, go, zig, julia in-sandbox; the Rust repos in the shortlist
  (`hermes-nmi`, `fleet-cns-v3`) were not opened this round.
- Six Python candidates cloned and inspected but not executed: `exocortex-core` (11 test files),
  `mentis-superinstance` (12), `holodeck` (14), `cocapn` (7), `compaction-teacher` (4),
  `image-distillation-loop-jev` (9 test files, **no CI**). `base60-lattice` runs `tsx` and was not installed.
