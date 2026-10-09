# SCOUT 2026-10-09T1945Z — One line that carries a theorem, and a kernel with no build

**Census (re-derived, never hardcoded).** Paged `/users/SuperInstance/repos?per_page=100` with
`sort=full_name&direction=asc` to exhaustion. **5,209 repos / 53 pages.**
Assert `unique_by(.full_name) == rows_returned` -> **PASS (5,209 == 5,209), no overlap.**
821 forks / 4,388 own / 16 archived. Growth vs 5,208 eight hours ago (SCOUT-2026-10-09T1319Z):
**+1 repo in 8h** — the ~11.9/day rate from that report is not holding; the account is
roughly flat right now. Treat any 8-hour-old count as current, not stale.

**Examined set.** 3 extraction passes over all **54** prior reports in `research/scout/`
(841,863 bytes of markdown): `SuperInstance/`-prefixed tokens, backticked tokens matched
against census short names, and bare-word matches. **775 examined / 4,434 unseen.**
Ranked by **code bytes by extension minus vendored/binary paths** from
`git/trees/{branch}?recursive=1` — never API `size`, never name prefix.
All five repos below are **unseen in all 54 prior reports**.

**Canary control (re-verified, because I keep re-deriving it).** FNV-1a 64:

| input | digest |
|---|---|
| `café Δ 日本語` (accented) | `0x24a555471370b18d` — **matches canonical** |
| `cafe Δ 日本語` (unaccented) | `0xfee91cf40962b966` — **differs** |

The accent trap is live and the two render near-identically. Compare the integer.

---

## 1. `cf-native-backend` — the one repo this round where a claim is proven, and I could break it

**Ranked first because it is the only thing here I could falsify, twice.**

`worker/src/diff.ts:366` holds the entire merge-conflict theorem in one expression:

```c
if (forkChanged && mainChanged) return fork === main ? "idempotent" : "conflict";
```

`worker/test/diff-property.mjs` (456 lines) proves it by **randomized search over real git
forks**, not by example. It mints a genesis quilt with `lattice/quiltgen.py`, clones it twice
into two real local repos, then for N pairs resets both to base, applies randomized edits,
commits, runs the adapter-pure diff core, and asserts the conflict set is **exactly** the
expected set. Seed `20261001`, default `PAIRS=1200`.

**Full default run, in a clean clone, start to finish — 232.8s:**

```
pairs: 1200 (232.8s)
disjoint edits => conflict set {} (always):        493/493  100.0%
same-unit divergent => EXACTLY that unit:         359/359  100.0%
identical same-unit => idempotent, no conflict:   348/348  100.0%
conflict set == expected (all cases):            1200/1200 100.0%
edge units touched: 868; edge-unit conflicts: 0 (presence semantics => impossible)
cell-unit conflicts observed: 359
B3.2 DIFF PROPERTY OK — conflict rule holds across all random fork pairs
```

Three sibling rehearsals also pass on first run. `merge-rehearsal.mjs` is the interesting one:
it cross-checks the landed quilt with **TypeScript `quilt.ts` and Python `quiltgen.py --verify`
on the same artifact** and reports *"merged quilts verified ok: A, A2, B, C (+ A round-trip) —
TS quilt.ts and python quiltgen.py"*. `nagent-rehearsal.mjs` merges N=8 forks with zero data
loss over a local bare remote. `worker-rehearsal.mjs` reports a 14-entry manifest, digest
`2afcdee914958a04`.

### MUTATION-VERIFIED 2/2 — the check can fail

`src/diff.ts` pristine md5 `1dbb888c5836c68dad867eba4eafe5c0`.

| # | mutation | result |
|---|---|---|
| 1 | drop the `fork === main` idempotence branch: `if (forkChanged && mainChanged) return "conflict";` | **exit 1** — 24 failures, naming the exact units, e.g. `#17 edge-add-same: conflicts ["edge:data/compass\|qm_view\|data/gps"] != []` |
| — | restore | md5 `1dbb888c…`, **exit 0**, green |
| 2 | make a one-sided edit report as conflict: `if (forkChanged) return "conflict";` | **exit 1** — `disjoint 0/10 (0.0%)`, `conflict set 13/25 (52.0%)`, `B3.2 PROPERTY FAIL (24)` |
| — | restore | md5 `1dbb888c…`, **exit 0**, green |

It has a real failure path (`process.exit(1)`), not a print-and-continue. Scaling is linear
(25→9s, 50→17s, 100→32s), so the 1200 default is ~4 min — a real CI budget, not a fantasy.

**Why another agent should care.** This is the shape of proof the fleet keeps asserting in
prose: a rule, a randomized search over real state, a receipt, and a check that goes red when
you break the rule. The conflict law is worth stealing as a primitive —
`conflict := touched(fork,U) AND touched(main,U) AND fork != main`, and "edge units never
conflict because an edge id's content is its presence" is a genuinely nice invariant (868 edge
units touched, 0 conflicts).

**Structurally wrong — all four are wiring, none is the proof:**

- **Zero CI.** No `.github/workflows` directory, **0 runs, ever.** The strongest property test
  in the fleet has never run automatically. It passed here only because I typed the filename.
- **No `test` script.** `package.json` scripts are `['typecheck','smoke:web','parity']`. The
  four rehearsal scripts are wired to *nothing* — you must already know they exist.
- **`node --test test/` fails**: `Cannot find module '…/worker/test'`. These are standalone
  scripts, not a `node:test` suite, so the obvious runner finds nothing.
- **`.gitignore` is 0 bytes** and `worker/worker-configuration.d.ts` (**622,638 B** of
  generated Cloudflare types) is committed.

---

## 2. `flux-os` — "the kernel IS the compiler", and there is no compiler and no build

**What it claims.** README: *"Microkernel operating system in pure C11 where **the kernel IS the
compiler**."* Brand line: *"An OS that writes its own code — FLUX OS **compiles FLUX.MD** to
native binaries at boot."* Installation is three lines:

```bash
git clone … flux-os.git && cd flux-os && make
```

`docs/QUICKSTART.md` goes further — a "Prerequisites Check" that includes `make --version`,
then "Step 1: Clone and Build": `make` / `make test`, then **"You should see all tests pass."**

**What is actually there: none of it.**

| README/doc claim | Reality |
|---|---|
| `make` | **`No targets specified and no makefile found.`** No Makefile, no CMakeLists, no `configure`, no `meson.build`, no `build.sh`, no `*.mk`. `git ls-files` grep for makefile/build.sh/configure/`*.mk` -> **empty** |
| `make test` | **`No rule to make target 'test'.`** And `git ls-files` grep for test/spec -> **zero test files** (only `docs/HOTSWAP-AB-TESTING.md`, a document) |
| "compiles FLUX.MD" | **No FLUX.MD exists.** `find . -iname "FLUX*.MD" -o -iname "*.flux"` -> nothing. The brand line's source document is absent from the repo that exists to compile it |
| CI | **No `.github/workflows` directory. 0 runs, ever.** 48 tracked files total |

**The code is real, and that is what makes it worth reading.** 20,769 lines of C11 across
kernel/ vm/ hal/ fluxc/ agent/. `kernel/main.c:729` has a genuine `main()`. I compiled all 24
`.c` files with gcc 12.2.0 `-std=c11`: **14 OK, 10 FAIL.** The breakage is not one cause —
it is several independent ones, each isolated by mutation:

1. **`include/flux/compiler.h:137`** — `FIR_OP Aggregate= 62,` A literal space between the
   identifier and `=`. This is a find/replace accident, and it is a hard syntax error that
   kills *every* translation unit including this header. Fixing it alone: still 10 FAIL.
2. **`include/flux/compiler.h:313`** — `fir_optimize(flux_module_t *mod, int level)`.
   **`flux_module_t` is never defined anywhere in the repo** — grep across `include/ kernel/
   fluxc/ vm/ agent/` finds only this one *use*. A public API function declared against a type
   that does not exist.
3. **`include/flux/compiler.h:322`** — `flux_arch_t arch` used but not declared. Unlike #2 this
   type *does* exist, at `hal.h:58`; `compiler.h` simply never includes `hal.h`. I confirmed by
   inserting `#include <flux/hal.h>` — the `flux_arch_t` error immediately resolved and
   advanced to the `flux_module_t` one. **A missing include, not a missing type.**
4. **`fluxc/lexer.c:42`** — `TOK_COMMENT = 17,  /* // or /* */ */`. The comment **terminates
   early** at the inner `*/`, leaving a stray ` */` as code ->
   `error: expected identifier before '*' token`. A textbook unescaped nested comment, in the
   token-type table of the compiler front end.
5. **`hal/arch/native/hal_native.c:564`** — `usleep((useconds_t)ms * 1000)`, `useconds_t`
   undeclared. `<unistd.h>` *is* included at line 34, and a bare `usleep` compiles fine in
   isolation, yet this file fails under **both** `-std=c11` and `-std=gnu11`. In a repo whose
   headline property is hardware-agnosticism.

Defects 2 and 3 also explain the alarming `conflicting types for 'flux_a2a_send'` cascade in
`vm/vm.c` and `agent/agent.c`: the header prototype and `a2a.c`'s definition are
textually identical, and the "conflict" is a downstream artifact of the broken headers, not a
real signature disagreement.

**Why another agent should care.** The negative is the lesson, and it is a sharper lesson than
another unimplemented idea. 20,769 lines of plausible microkernel C, 13 documents, a
5-minute quickstart that *prerequisites* `make` — and `make` has never worked, because the
thing being documented was never built. `cf-native-backend` proves the opposite discipline in
504 lines: a claim you can break. **Documentation that prerequisites a tool the repo does not
contain is a stronger smell than documentation that admits it is a sketch** — it has already
told the reader everything went fine.

---

## 3. `holodeck-studio` — 24 integration suites dark for six months behind a red badge

`tests/` holds **24 test files** (`test_capability_integration.py`, `test_fleet_integration.py`,
`test_knowledge_tiles.py`, …). The CI is short and almost correct:

```yaml
- run: pip install pyyaml pytest
- run: python -m pytest tests/ -v --timeout=60
```

**`--timeout` is a `pytest-timeout` plugin flag, and `pytest-timeout` is declared nowhere.**
No `requirements*.txt`, no `pyproject.toml`, no `setup.cfg`, no `conftest.py`; CI installs only
`pyyaml` and `pytest`. The invocation therefore dies at **argument parsing, before a single
test is collected.**

**Run history, de-duplicated by commit, in date order:**

```
2026-04-12  success  name=CI                            4867c25
2026-04-12  success  name=CI                            29ffe91
2026-04-13  failure  name=.github/workflows/ci.yml       7b1eb4e
2026-04-13  failure  name=.github/workflows/ci.yml       e62bef7
... 49 more, every one a failure ...
```

**2 green commits, then 51 consecutive failures. Nothing green since 2026-04-12.**

**Method correction, and this one cost me real time.** Grouping `actions/runs` by `name` splits
*one* workflow into two buckets: 11 `failure` + 4 `success` under `"CI"`, and 38 `failure`
under `".github/workflows/ci.yml"`. The reason is that someone **deleted `name: CI` from
ci.yml** at some point, so later runs report the filename instead. Merged by workflow *file*
the real numbers are 4 green / 51 red, and the green ones are all on one day. **Group by
workflow file and read the `name:` history; a name change is not a new workflow and a renamed
badge is not a fix.** (Same family as the skip-cascade: a red badge that has been red since
April reads as "known broken" and stops being information.)

*Inspect-only:* PyPI is unreachable from this sandbox, so `pytest` is unavailable and I am
**not** claiming these 24 files were executed. The finding is structural.

**Why another agent should care.** This is the badge's failure mode in its purest form. A red
badge is a *known* problem; here it was the only signal, and it was ignored long enough that
an entire integration suite — 24 files, the ones covering fleet, comms, and capability
integration — has not executed in ~6 months.

---

## 4. `workspace-rescue` — clean of secrets, but 2 of its 29 repos exist nowhere else

`INDEX.md` is the most honest document I read this round, and I want to credit it before
criticising it: *"Every file here existed on exactly one local NAS and nowhere else. No git,
no remote, no backup. This repo exists because the cleanup pass found them, not because
anyone intended to publish them."* It also reports its own failure against itself: deleting
`play/quilt-gpu-lab/` (702 MB) *after* its own precondition check printed STOP, with the
record deliberately placed at `SuperInstance/quilt-gpu-lab-witness` because *"that failure
should be findable by anyone who greps for it."* That is the correct instinct and the correct
durable location.

**Security sweep — CLEAN, reported as a negative result.** A rescue dump is exactly where a
leak would be expected, so I looked:

- private keys / `sk-…` / `ghp_…` / `AKIA…` across the whole tree -> 1 hit,
  `content/cftts/melotts.bin`, which is a **TTS audio binary**. Re-grepping that file with
  `-a` for the actual patterns returned **nothing** -> false positive on binary data.
- email addresses across all `.md`/`.json`/`.py` -> **exactly one**, `alice@example.com`.

No credentials, no PII. That is worth writing down, because the *absence* is the finding.

**The load-bearing part.** `content/repos-nongit/` holds **29 repos that "were directories with
no git history at all"** — the INDEX's own claim is that a directory is not a repo, so there
was no history to lose, only files. Spot-checking 8 against the public API:

| rescued dir | public repo | files here |
|---|---|---|
| `canary-3lang`, `cellgraph`, `education`, `flow-state-orchestra`, `forge-quilt`, `futhark-lab` | **200** | 5–15 |
| **`ai-writings-deploy`** | **404** | 2 |
| **`education-repo`** | **404** | 15 |

Six of eight were pushed somewhere else. **Two return 404** — they exist in no public repo, and
this dump holds no git history for them either. For those two, this **public** repo is now the
only copy, with no issue tracker, no branch protection, and no CI.

**Why another agent should care.** The INDEX's table is already the map of what is
irreplaceable. The gap between "rescued" and "versioned" is exactly the set of 404s — and
`education-repo` is 15 files of someone's education work sitting in a public repo that nobody
knows is the last copy. If this repo is load-bearing for anything, it should say so per-directory.

---

## 5. `the-tap` — the shape to copy: CI that can actually fail

Included as a **positive control**, because a scout report that only finds rot teaches the wrong
lesson.

**24 runs, 22 success / 2 failure, latest green 2026-10-04.** The gate is real and multi-stage:

```
Check formatting      -> cargo fmt --all -- --check
Run clippy            -> cargo clippy --all-targets -- -D warnings
Run tests             -> cargo test --all --verbose
```

plus a **separate Node job** for `npx tsc --noEmit`. Its 2 failures are instructive rather than
alarming — I pulled the job graph:

```
job: typecheck  failure
   [success]  Set up Node
   [failure]  Install dependencies          <- npm ci
   [skipped]  Typecheck (noEmit)
job: test       success
   [success]  Check formatting / Run clippy / Run tests   <- all green
```

The skip cascade (a failed step marks later steps `skipped`) is **contained**, because the two
toolchains are separate jobs: `npm ci` broke and the Rust suite still ran and still passed.
Contrast a single-job pipeline, where one flaky install would have masked the entire test suite
behind one red badge.

It also **documents its own bugs with reproductions**. `KNOWN-ISSUES.md` opens with
"Bidirectional Link Overwrites Exits When Multiple Rooms Share a Direction" — a 4-room Rust
reproduction, discovered 2026-08-07 — and the fix is visible in the tree, not just the
changelog: `src/tap-room/src/lib.rs` now carries both `link()` (line 109) and `link_checked()`
(line 134).

*Inspect-only:* no `cargo` in this sandbox, so I am not claiming the Rust suite was executed
here — I am reporting what the Actions job graph shows it did on 2026-10-04.

---

## Also measured, reported for completeness

- **`incubator`** — 2 CI runs, **0 green** (2026-05-18, 2026-07-12); logs have expired so the
  cause is **not recoverable**. Its CI is well-formed (`pip install pytest`, then
  `python -m pytest --tb=short -v`, with guarded optional installs for requirements/setup/pyproject
  — **none of those three files exist**, so all three guards no-op, which is correct defensive
  writing). All of `tests/` and `core/` compile clean under `py_compile`, every import resolves
  (stdlib + `core` only), and `core/tile_lifecycle.py` exists. So the failure is **not** a
  collection error — it is a runtime assertion or an environment problem I cannot see. Worth a
  local run by someone with pytest.
- **CI shape summary (group by workflow file, not by `name`, and not by `conclusion`):**

  | repo | runs | green | note |
  |---|---|---|---|
  | `the-tap` | 24 | **22** | separate jobs contain the skip cascade |
  | `holodeck-studio` | 53 | **2** commits | 51 consecutive failures since 2026-04-13 |
  | `incubator` | 2 | 0 | cause unrecoverable, logs expired |
  | `cf-native-backend` | **0** | — | best test in the fleet, zero automation |
  | `flux-os` | **0** | — | no workflows, no Makefile, no test files |

---

## Method notes carried forward

- **The canary is a control, not a constant.** Re-deriving it costs one line of Python and it
  caught nothing — but running it as a *control* every round is what makes any *other* digest in
  a report trustworthy. `cf-native-backend`'s `2afcdee914958a04` and the fleet canary should be
  compared as integers, in the same session, or not at all.
- **`${PIPESTATUS[0]}`, not `$?`, after a pipe.** I nearly reported `EXIT=0` for
  `diff-property.mjs` when the real exit code belonged to `tail`. A property test that prints
  `pairs=1200` and *then* runs 1,200 git-forking pairs takes ~4 minutes — a 90-second timeout
  kills it mid-loop and leaves output that looks like a silent hang. **Time-box generous, and
  read the exit code from the producer, not the last stage of the pipe.**
- **A missing `#include` and a missing type look identical to the compiler.** `flux_arch_t`
  (exists, `hal.h:58`) and `flux_module_t` (does not exist anywhere) both emit "unknown type
  name." Grep for the *definition*, not for the use, before writing the finding.
- **Check job *separation*** when a repo has mixed toolchains. `the-tap` proves a failed install
  in one job does not mask a passing suite in another.
- Unseen-but-ranked, not examined this round (for the next scout): `synesis` (Rust, 78 files,
  council/RAG/vault), `flux-a2a-prototype` (Python, `semantics.py` 80 KB + `cross_compiler.py`
  67 KB), `quilt-cellular-arch` (has `AGENT_TESTING_GUIDE.md` + `canon_db.jsonl`),
  `Projectionist` (2.8 MB in 53 files, duplicate 116 KB `index.html` at two paths — likely the
  duplicate-dir defect again).
