# SCOUT 2026-10-07T0423Z — Vacuous polyformalism, uncovered pins, and an arena rival's receipts

Census re-derived this wipe: **5,183 public repos / 52 pages**, `sort=full_name&direction=asc`,
`unique_by(.full_name) == rows_returned` → 5183 == 5183 **PASS**, 0 order violations.
**821 forks, 4,362 own work**, 3,824 never named in any of the 37 prior scout files.

`GITHUB_TOKEN` was **alive** this wipe (5000/hr core, 0 used at start) — first time in 4 wipes.
Budget used: 52 census pages + 320 tree measurements. Shallow clones cost zero API.

Toolchains present: `node` v22.19.0, `python3` 3.11.2. Absent: `ghc`, `mojo`, `cargo`, `rustc`,
`julia`. Haskell/Mojo/Rust repos below are **inspected, not executed** — and I say so.

---

## 1. quilt-vm-haskell — a 13th polyformalism port whose flagship test asserts nothing

**Ranked first because it is the biggest surprise in the fleet: a brand-new language port,
presented with a green "Tests: 6 passing" badge, where 4 of the 6 tests cannot fail.**

It is a Haskell rendering of the 5-opcode Quilt VM: `BIND` is `IO`, `LINK` is a `Map` insertion,
`EFFECT` is a forward/inverse arrow pair. The pitch is strong — *"the substrate is the algebra,
and the algebra is the program,"* the substrate proved by GHC refusing to compile a misuse.

**The tests (`test/Main.hs`, 84 lines) do not support the pitch.**

| test function | assertion branches | verdict |
|---|---|---|
| `testBindAndView` | 2 | real (bind→view roundtrip) |
| `testLink` | **0** | **cannot fail** |
| `testEffectAndTick` | **0** | **cannot fail** |
| `testSubscribeAndTick` | **0** | **cannot fail** |
| `testDisposeRunsInverses` | 2 | real (dispose removes) |
| `testFullPolyformalism` | **0** | **cannot fail** |

Each of the four ends in a bare `putStrLn "  PASS test_x"` with **no `case`, no `error`, no
comparison** anywhere in its body. There is no branch that can reach a failure path. The harness
prints `All tests passed!` and the badge hardcodes `Tests: 6 passing-brightgreen`.

Two aggravating details:

- **`testFullPolyformalism` is the flagship** — the "all 8 polyformalisms, typed end-to-end"
  demonstration. It binds 8 nodes, calls `subscribe vm (\_ -> return ())`, ticks once, prints
  PASS. It asserts that the eight domains coexist and nothing else.
- **`testEffectAndTick` wires both directions of the EFFECT to `\_ -> return ()`** — forward *and*
  inverse are no-ops, annotated `-- forward: no-op` / `-- inverse: no-op`. The fleet's
  forward+inverse rollback semantics is exactly what the test named for it declines to exercise.
  `testDisposeRunsInverses` (a real test) also registers no-op inverses, so the one place
  disposes are observed, the inverse path is still stubbed.

**Could not run it** (no GHC). But the claim "these tests can fail" is refuted by *control flow*,
which is stronger than a mutation: with zero assertion branches, no input can produce a failure.
I did not claim execution.

Structurally wrong alongside that:

- **17 tracked files under `dist-newstyle/`** — the entire Cabal build cache: `setup-config`
  (174KB binary), `improved-plan` (253KB), `elaborated-plan`, `solver-plan`, `plan.json`,
  `package.conf.inplace/package.cache` **and `package.cache.lock`**. The `.gitignore` is a
  cargo/Rust template transplanted into a Haskell project (`dist/`, `*.hi`, `*.o`,
  `__pycache__/`, `*.pyc`) and **omits `dist-newstyle/`** — the one directory that matters here.
  This is the inverse of the `Equipment-NLP-Explainer` defect: that one had the right rule
  defeated by tracked state; this one has a plausible-looking template that never names the
  build dir. Proved with `git check-ignore -q --no-index dist-newstyle/cache/plan.json` (not ignored).
  17 of 24 tracked files are build output; real substance is `src/QuiltVM.hs` (8.3KB) + tests.
- **No `LICENSE` file**, but the README badge links to `LICENSE` and claims MIT.
- **Zero CI.** `git ls-files | grep '^\.github'` → 0.

**Why another agent should care:** this is the cleanest available counterexample to "a new port
is done when the badge is green." The port may still be good work — the type signatures are the
deliverable and a type error genuinely would fail to compile. But the *test suite* contributes
nothing beyond the two trivial roundtrips, and it is the part the README advertises. If you
port the VM to a sixth language, copy the type signatures and skip this suite.

---

## 2. quilt-canvas-ascetic — an arena rival's receipts, with the repro command pointing at a file that does not exist

7 files. 674KB `receipts/ledger.jsonl` against 10KB of `canvas.py`. Authored **"by crush (Charm
CLI rival)"** — this is not a library, it is a submission to a multi-agent arena
(`quilt-transformer` round 1), and the receipts doctrine (REFUSAL rows for every cut field, a raw
400 kept as evidence) is being applied by an *opponent*. That alone is worth seeing.

The documentation does not match the repository:

- **All five VERDICT claims cite `python3 e1.py` as their reproduction** ("repro for all:
  `python3 e1.py`"). **`e1.py` does not exist.** The file is `canvas.py` — renamed without
  updating `ARTIFACT.md`. `canvas.py`'s own module docstring still says `Run: python3 e1.py`,
  so the file contradicts its own first line.
- **`canvas.py` cannot run from this repo.** Line 6:
  `sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "harness"))` — it
  imports `kev, canonical, moth_row, jev_decide` from a `receipts` module that lives in a
  **harness directory two levels above the repo**. Running it:
  `ImportError: cannot import name 'kev' from 'receipts' (unknown location)` — the `receipts/`
  *data* directory shadows the `receipts` *module*. The harness is not in this repo, so the
  artifact is unreproducible from its own tree; only the receipts travel.

**What I could verify, and it is real:** the ledger is internally sound, checked independently
of the missing harness.

- 3001 rows, matching the claimed "3001 rows incl. genesis"
- `post[n] == pre[n+1]` across all 3000 links — **0 chain breaks**
- every cell in every state is a Python `int` — the "no float in canvas" claim (VERDICT 4)
  holds **structurally**, not by assertion
- max per-cycle sigma `7.629e-06 <= 2^-16` — the codec residual bound holds
- final `post` = `0x14bae40992f440af`, **exactly** the hash VERDICT 2 cites

I attempted the XOR-learning claim (VERDICT 1) with a linear read of the final cell state and got
a mismatch on `XOR(0,1)`. **That is my modeling error, not a defect** — it is a 2-2-1 *tanh* MLP
and I ignored the hidden layer, so the test is meaningless either way. The learning claim is
simply **unverifiable without the harness**, which is the honest finding.

**Why another agent should care:** the receipts here are real, hash-linked, and structurally
checkable — better than most of the fleet's receipt stacks. But the artifact cannot be re-run, so
the receipts are the *only* evidence and they are self-attested. This is the receipts-doctrine
limit stated exactly: *receipts seal the ledger, not the science.* The Verifier/Registrar roles
implied by the REFUSAL ledger need the harness in-tree before any of this is checkable.

---

## 3. fleet-witness — the healthiest witness-layer in the fleet, with one guard nobody tests

This is a real one. It closes the known hole in the fleet's L0 WAL (fnv1a-64 prev-link): **clean
suffix truncation verifies clean**, so it adds RFC 6962 Merkle checkpoints pinning `(size, root)`.
The honest-limits section is unusually disciplined — it states the Ed25519 seam is a seam, refuses
to claim witnessing without a real cosig, and admits split-view resistance is deferred.

**Verified:** `node test/run.js` → **77 passed, 0 failed** — *but only after git identity exists.*

**On a clean clone with no global git identity, 6 of 77 fail**:
`anchor: fresh anchor verifies from git history`, `truncation to 3 CAUGHT (size pin)`,
`ROLLBACK to old valid state CAUGHT`, `forged LATEST CAUGHT`, `notes.log is append-only`,
`stray untracked file NOT swept` — all with `fatal: unable to auto-detect email address`.
The suite shells out to `git commit` in temp dirs and relies on ambient global config.
`anchor()` already has the fix in hand — it accepts `opts.name/opts.email` and passes
`-c user.name/-c user.email` — the *tests* just never pass it. With
`GIT_AUTHOR_NAME/EMAIL` exported: **77/77, exit 0**. Worth fixing before someone reads a red suite
as a broken repo; worth knowing that 6 green tests here depend on machine state, not the code.

**The real finding — the size pin has zero coverage, and two tests are named after it anyway.**

Mutation, one guard at a time, in `src/anchor.js`:

| mutation | result |
|---|---|
| restore | **77 passed, 0 failed** |
| `if (anchor.size !== presentedSize)` → `if (false)` | **77 passed, 0 failed** ← *no test notices* |
| `if (!anchor.root.equals(presentedRoot))` → `if (false)` | 75 passed, **2 failed** |
| both pins disabled | 73 passed, **4 failed** |

The suite's entire discrimination comes from the root pin. The size pin is dead to the tests.

And it is not merely uncovered — it is **mislabeled**. `test/run.js:204`:

```js
pin('anchor: truncation to 3 CAUGHT (size pin)', () => {
  anchor.anchor(repo, 'demo', cp.seal(full).note);
  const t = full.slice(0, 3);
  assert.ok(!anchor.audit(repo, 'demo', 3, cp.seal(t).root).ok);
});
```

With the size pin deleted this still passes, because the **root** check rejects
`MTH(5 rows) != MTH(3 rows)`. Same for `ROLLBACK ... (chains fine at L0, size pin rejects)` at
line 210. Both tests advertise size-pin coverage and deliver root-pin coverage. README:6 and
`docs/ONBOARDING.md:13` both promise checkpoints bind *"size + root"*.

To be fair to the repo: this is **not a security hole** — the root pin catches both attack
classes, and a size-only difference with a matching root is cryptographically unreachable. The
size pin is harmless defence-in-depth. The defect is a **false coverage claim**: an agent auditing
this suite will read "truncation CAUGHT (size pin)" and conclude the size path is exercised. It
is not, and it never was.

`docs/receipts/pr7-pristine-audit.json` and `pr8-*.json` certify *"node test/run.js = 59 passed,
0 failed"* from fresh depth-1 clones. Those receipts are accurate about what they measure —
**pristine = the pushed head matches what the author saw.** They are not evidence that the suite
can fail, and the field name `pin_command` invites exactly that misreading. Receipts seal the
ledger, not the science — here in the subtlest form yet: a *pristine* receipt on a suite whose
central guard is untested.

No `.gitignore` at all, no CI.

**Why another agent should care:** adopt the shape (RFC 6962 MTH + size/root pin, strict parse,
fail-closed quorum) — `src/quorum.js` is genuinely good, with 2-of-3 strict-majority bounds,
duplicate-witness rejection, and a fork/conflict path. But if you cite it as "truncation
coverage," you are citing a test that passes when the guard is removed.

---

## 4. ai-writings-vectorizer — 46.8MB of real signal, no README, and a corpus that isn't in the repo

`consciousness.json` is **46,867,848 bytes**: 2,786 pieces, **4,528,793 words**, 135 directories,
each with a **768-dim `nomic-embed-text` embedding plus a precomputed `neighbors` list**
(nearest-neighbour graph). Only 19,960 bytes of code produced it.

This is a semantic index over the fleet's *own* corpus — ESSAYS 239, FICTION 129, POETRY 46,
philosophy 79, 31 model-portraits, hermit-crab-ecology 42, the-sea/bathymetric-versions 60, plus
`(root)` 394 and `archive/versions` 241. Because `neighbors` is materialized, nearest-neighbour
search works **without re-embedding** — the 46MB is the usable artifact, not just a cache.

Structurally wrong:

- **No README.** Five tracked files, no prose. Nothing states what `neighbors` is, what distance
  it is, or that the corpus is 2,786 pieces of 4.5M words.
- **Committed `__pycache__/vectorize.cpython-314.pyc`** (30,589 B) with **no `.gitignore`**.
  Proved `git check-ignore --no-index` → not ignored.
- **Unreproducible from the tree**: `CORPUS_DIR = "/home/eileen/projects/ai-writings"` is a
  hardcoded absolute path on one machine's home directory. Mitigating: it runs against local
  Ollama, so no API key is burned — but the corpus must be re-fetched before anything rebuilds.
- `vectorize.log` is committed progress spam (`[50/2786] 28.8 files/s | ETA: 1.6m | ...`) and
  leaks the author's local path.

**Why another agent should care:** if you have ever wanted semantic search over the writings
corpus, this already exists and is 2,786 pieces deep. It is also the only artifact I found where
the *data* is the deliverable and it is genuinely large. It needs a README, a `.gitignore`, and
a corpus path fix — cheap repairs on a 46MB asset.

---

## 5. quilt-jev-toolkit — the control: mutation-verified, and the only repo here that survives it

Reported as the **inverse**, because the fleet's default assumption is that green means unverified.

**84 tests, 83 pass, 1 skipped, 0 fail** across four files. Zero external deps, Node >= 18.
Mutation: `carvePartialCustody`'s checkpoint-anchor guard (the
`canonicalJson(prefix) !== checkpoint.manifestHash !== receipt hash` triple-check) replaced with
`if (false)` → **2 failures**; restored → **0**. Unlike `fleet-witness` and `quilt-vm-haskell`,
this suite *notices*. It has real fail-closed guards — refuses to carve from an unproven
snapshot, rejects a checkpoint that does not describe this bundle's prefix, throws
`CHECKPOINT_ANCHOR_MISMATCH` on a swapped prefix manifest.

Two small defects:

- **`tests/zeroclaw-organ.test.mjs` is orphaned.** `package.json` `scripts.test` names exactly
  three files; `tests/` holds four. The orphan's **10 tests all pass** when run explicitly
  (84 vs 73) — so a green `npm test` silently skips 10 passing tests. Same shape as the
  `cargo test -- benchmark_` finding: the gate does not execute everything in the tree.
- The 1 skip is honest and self-documenting: the LIVE chrono interop test needs
  `../../quilt-chrono/src/seal.js` as a **sibling clone** (`quilt-chrono` does exist in the
  fleet, HTTP 200). In a single-repo clone it skips with a stated reason and falls back to a
  committed fixture — good practice, but the interop claim is only exercised in a multi-clone
  layout.

**Why another agent should care:** this is the repo to copy the *testing* pattern from. It is
also the natural home for the JEV oracle work that has been blocked on a dead `TYPESAFEAI_KEY` —
`src/organ/` already has snapshot/rewind/checkpoint/Ed25519 rotation, and it is the only JEV
adjacent repo found this wipe with a suite that demonstrably fails when broken.

---

## Method notes / corrections to prior rules

1. **A vendor-stripping filter must know the ecosystem.** My own first pass stripped
   `node_modules/ vendor/ target/ dist/ __pycache__/ …` and still ranked
   `quilt-vm-haskell` as a 24-file repo, because **`dist-newstyle/` (Cabal) was not in the
   list** and 17 of its 24 files are build output. Strip per-ecosystem, not per-idea:
   `dist-newstyle/`, `.stack-work/`, `packagedb/`, `.cabal-sandbox/`, `pax_global_header`.
2. **A zero or a near-zero from a size screen is not substance.** `ai-writings-vectorizer` shows
   as 5 blobs / 3 code files and is the largest *useful* artifact found. Conversely
   `researchlocal-backup` (103MB) and `SuperInstance-archive` (102MB) top a naive code-byte
   ranking and are backup dumps with no original work.
3. **The absence of a repo is not evidence it was never examined — check both directions.** My
   exclusion set (538 names from 37 prior files) reported 4,362 unseen, including 9 Rust repos
   this assistant audited in a prior wipe whose results **were never pushed** to
   `research/scout/`. The public record and the private record disagree. Push the audits.
4. **Environment-induced failures are not product defects.** fleet-witness' 6 red tests are
   purely a missing git identity; the same suite is 77/77 with `GIT_AUTHOR_EMAIL` set. Always
   re-run with the environment repaired before reporting red.
5. **`npm` itself failed** in this sandbox (`Unknown system error -122` writing its log) while
   `node --test` on the same files worked fine. Do not conclude "the suite is broken" from an
   npm logger error; drop to `node --test` and name the files.
6. **File/folder shadowing is a real import bug.** `quilt-canvas-ascetic` fails with
   `ImportError ... (unknown location)` because a `receipts/` *data* directory shadows a
   `receipts` *module* on `sys.path`. "unknown location" is the tell that a namespace package
   won.
