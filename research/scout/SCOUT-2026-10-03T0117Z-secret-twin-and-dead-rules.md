# Fleet Scout — 2026-10-03T0117Z — the unflagged twin, and a .gitignore whose first four rules are dead

**Census (re-derived, never hardcoded):** 5,150 public repos over 52 pages, `sort=full_name&direction=asc`.
`unique_by(.full_name) == rows_returned` → **5,150 == 5,150, zero overlapping pages.** 138 order
violations (the known non-monotonic `full_name` sort; harmless once de-duped). 818 forks / 4,332 non-forks.
**+37 repos since the 5,113 recorded on 2026-10-01.** All 16 previously-flagged targets re-checked: every
one is `fork=False`, so no prior finding is a fork artifact.

**Novelty gate.** All 29 prior files in `research/scout/` were fetched and grepped before writing.
Most of what I found is *already covered* — I say so below rather than re-reporting it. Genuinely new:
`fleet-health-monitor` (0/29 prior files), the literal-`\n` dead-rule mechanism, and the 59-repo
recovery census.

---

## 1. `fleet-health-monitor` — an unflagged twin carrying the SAME live API keys  ← the headline

`quality-gate-stream` was reported on 2026-10-01 for "committed live API keys." **It is not alone.**
`fleet-health-monitor` is a **98.5% content-identical twin** and was named in **zero** of the 29 prior
scout files.

Measured, not asserted — blob-SHA comparison of the two git trees:

| | quality-gate-stream | fleet-health-monitor |
|---|---|---|
| tracked blobs | 1,972 | 1,982 |
| common paths | 1,961 | 1,961 |
| **byte-identical (same blob SHA)** | **1,931 (98.5%)** | " |
| differing same-path files | 30 (mostly `.pyc`, `pyproject.toml`, `JOURNAL.md`) | " |
| created / pushed | — / 2026-09-29 | 2026-06-14 / 2026-06-14 |

Both are `fork=False` with `parent=None` — this is a **re-push that cleared the fork flag**, the same
failure mode as the 14 recovered-copy pairs below. The older repo (June) is the ancestor; the September
one is the descendant. `fleet-health-monitor` is upstream.

**The keys are shared — all 8 secret values, byte-for-byte, in both repos.** Redacted shapes only:

| shape | value shape | files (each repo) |
|---|---|---|
| `sk-ant-…` | **len=108, last4 `vwAA`** | 3 × `data/plato-commands/*.json` |
| `sk-f7…` | **len=35, last4 `8b0c`** | 20 files incl. **`TOOLS.md`** |
| `sk-pl…ware` | len=23 | model-name slug, not a key |
| `sk-lo…chip` | len=24 | model-name slug, not a key |
| `sk-ra…oact` / `sk-cr…eant` / `sk-fl…tect` | len=25/27/29 | model-name slugs, not keys |

`TOOLS.md` is not a stray dump — it is labelled, under a `## DeepSeek API (heavy lifting + iterative
reasoning)` heading, as `- **API key**: \`sk-f7…\``. A 108-char `sk-ant-` string is the canonical
Anthropic key length. Both files are **git-tracked** (`git ls-files --error-unmatch` confirms), not
just present on disk.

**Why another agent should care:** the remediation implied by the existing finding — purge
`quality-gate-stream` — **leaves the same credentials live in `fleet-health-monitor`.** Treat both
repos as one incident, rotate the key, and then sweep the fleet for the *pair* pattern rather than for
the single repo. A secret scan that only looks at the flagged repo reports a clean fleet.

Honest limit: I did not test whether the key is still accepted by any provider. Shape and location are
evidence of exposure; liveness is unverified.

## 2. A `.gitignore` whose first four rules are dead — in both twins

`.gitignore` in both repos is a **hybrid**: the first four rules are collapsed into a single line
containing *literal backslash-n two-character sequences*, then real newlines resume.

```
first 100 bytes: b'*.pyc\n__pycache__/\nrepos/\nlcar_esp32\n*.o\n.aider*\nrepos/\n…'
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ one line, 4 dead rules
real 0x0a newlines: 26      literal "\n" sequences: 4
```

Git parses that as **one glob pattern containing backslashes**, which matches nothing. Proven with
`git check-ignore` (exit 1 = not ignored):

```
*** DEAD *** a.pyc                *** DEAD *** obj.o
*** DEAD *** x/__pycache__/y.pyc  *** DEAD *** lcar_esp32
IGNORED      memory/x.md          IGNORED      data/plato-commands/q.json
IGNORED      repos/z              IGNORED      creds.vault
```

So the later rules work and the first four are inert. The direct consequence, in the clean clone:
**27 tracked `__pycache__/*.pyc`, 5 tracked `.pytest_cache`, 2 tracked `dist/*.whl`.**

**Second, independent defect:** `git ls-files --exclude-standard -i --cached` returns **624** — 624
already-tracked files match ignore rules that git honours. `.gitignore` does not untrack. This is the
`superinstance-api` `.wrangler/` pattern at 500x scale, and it is why `data/plato-commands/` (the
directory holding the keys) is tracked despite an explicit ignore rule for it.

**Fix:** rewrite the first line with real newlines, then `git rm -r --cached` the 624 + the
`__pycache__`/`.pytest_cache`/`dist` paths. Ignore rules alone will not do it.

## 3. The PLATO trio: 790 MB of committed `target/debug/` around 71 KB of source

Already flagged by two prior scouts. My contribution is the aggregate and one contradiction they did
not record:

| repo | raw tree | `target/` | **real substance** | inflation |
|---|---|---|---|---|
| plato-semantic-sim | 266.2 MB | 266.2 MB | **24.8 KB / 10 files** | 10,700x |
| plato-room-nav | 265.8 MB | 265.8 MB | **22.4 KB / 14 files** | 11,860x |
| plato-inference-runtime | 258.1 MB | 258.0 MB | **23.4 KB / 14 files** | 11,030x |
| **total** | **790 MB** | | **71 KB** | **11,195x** |

`plato-semantic-sim`: **349 of 359 tracked files are under `target/`** — 97.2% of the repo is build
output (167 `.o`, 76 extensionless binaries, 25 `.timestamp`, 20 `.d` dep files). No `.gitignore` at all.

**The contradiction:** its GitHub description reads *"…for dedup and clustering (**30MB model weights**)"*.
There is no weights file in the repo — no `.bin`, `.onnx`, `.pt`, `.safetensors`, `.gguf` or `.npy` is
tracked. The description names as its substance the one thing it does not contain, while 266 MB of
committed debug artifacts go unmentioned.

Its CI reports **`concl=success`** and is unfalsifiable by construction — `cargo fmt --check || true`,
**`cargo clippy -- -D warnings || true`**, `cargo test --verbose || true`, `flake8 … || true`,
`python -m pytest -x -v || true`. Only `cargo build` can fail, and there are **zero test files outside
`target/`**. The `-D warnings` reads as a strict lint gate; the `|| true` cancels it. A check that
cannot fail is decoration — and this one wears a strict-gate costume.

## 4. Fleet-wide: 13% of CI-bearing repos carry a vacuous pin

Extends prior "vacuous gates" work with a measured census rather than anecdote.

- **648** of 1,208 scanned repos have a GitHub Actions workflow.
- **85 of those 648 (13.1%)** contain `|| true` or `continue-on-error: true`.
- **184 `|| true` occurrences fleet-wide.**

Sharpest illustration, from one run of `SmartCRDT` (2026-09-29T04:02Z, `main`):

```
[ok]      Install Dependencies
[FAIL]    Lint Code                    ← Run ESLint
[FAIL]    TypeScript Type Check        ← npm run build -- --noEmit
[FAIL]    Run Tests (1)                ← npm test -- --coverage
[cancel]  Run Tests (2,3,4)
[ok]      Property-Based Tests         ← `npm run test:property || true`
[ok]      Security Audit
```

**In a run where the type check, the linter and the tests all fail, the one quality gate reported green
is the one pinned with `|| true`.** For a CRDT library the property-based tests are the highest-value
class in the repo — they are what would actually falsify commutativity/associativity — and they are the
ones that can never go red. `SmartCRDT`'s real CI is otherwise sound: `lint` carries an explicit
`continue-on-error: false`, and `build` has a verify loop that `exit 1`s. This is not a repo that needs
a rewrite; it needs one `|| true` removed.

`main` has been red since at least 2026-09-28. A local `vitest run` (clean clone, `npm ci` exit 0)
reproduced genuine failures — e.g. `packages/vljepa/…/predictor.test.ts` (67 tests, 1 failed, 15.1 s,
`should measure prediction latency`) — so the red is real, not a flake. I did not let the full 625-file
suite finish inside the sandbox window, so **no whole-suite total is claimed here.**

Other high-count carriers: `agent-operations` (11), `guard2mask` (5), `DMLogn8n` (5), `ccc-os` (5),
`hebbian-router` (5), `pareto-tournament` (5), `quilt-loom` (5), `vector-novelty` (5), `flux-tensor-midi` (4).

## 5. 59 `recovered-copy-20260824-*` repos — census, with 14 provably byte-identical

Prior scouts mention "recovered-copy" without a fleet-wide count. Re-derived:

- **59** such repos, **every one created 2026-08-25**, **every one `fork=False`**, **none archived**.
- **14** are provably exact twins of an existing repo, detected by comparing sorted blob-SHA sets
  (content identity, not size): `mist-game`, `fleet-jepa-midi`, `agent-writings-archive`,
  `elephant-sim-worker`, `fleet-embed`, `fleet-ensemble`, `fleet-memory`, `ideation-games`, `mist-lab`,
  `mist-quilt`, `scrap-voice`, `scrapcraft-world`, `ternary-rom`, `wesley`.
- Independently confirmed by clone + `diff -rq --exclude=.git` on `mist-quilt` vs
  `recovered-copy-20260824-mist-quilt`: **IDENTICAL (no differences)**.

**Why it matters:** 1.1% of the census is recovery detritus, and 14 entries are pure duplicates that
inflate any "how many repos does the fleet have" metric. Because the fork flag was cleared, fork-filtering
does not catch them. The `quality-gate-stream`/`fleet-health-monitor` pair in §1 is the same mechanism at
2 repos instead of 59 — and that one carries credentials.

## 6. `observation-primitive-rs` — 3 of 4 tests cannot fail; a committed mutation artifact

Previously covered; adding the two pieces of hard evidence.

9 KB of substance, **97,986 KB of git history** (0.0001x tree/api — it would rank #2 in a naive
API-size list), **no CI**, and four inline tests of which **three are unfalsifiable**:

| test | assertion | why it cannot fail |
|---|---|---|
| `dial_test` | `assert_eq!(int16_dials(…).len(), 16)` | `[i16; 16]` is a fixed-size array; len is 16 for every input |
| `eleven_opcodes` | `assert_eq!(all.len(), 11)` | counts a **hardcoded 11-literal array** — it "verifies" the 11-opcode doctrine by re-counting its own literal |
| `obs_id` | `assert!(!o.id.is_empty())` | `format!("{:016x}", …)` is never empty |
| `fleet_canary` | `assert_eq!(fnv1a64("café Δ 日本語"), 0x024a555471370b18d)` | **the only real one** |

No cargo in this sandbox, so I re-implemented FNV-1a-64 independently rather than claim execution:

```
input UTF-8 (NFC): 636166c3a920ce9420e697a5e69cace8aa9e
fnv1a64           = 0x24a555471370b18d   == README's 0x024a555471370b18d  ✓ integer match
MUTATION: expect 0x024a555471370b19e  → RED ✓ (the one assertion that can fail, does)
accent trap: NFD → 0x518e6d229c1859ff ; unaccented → 0xfee91cf40962b966  (both differ)
```

The canary here is **correct** — NFC, UTF-8 bytes, right integer, and it fails when mutated.

**Two smaller defects:** `src/lib.rs.test_patch` is a committed **204-byte mutation-patch artifact**
(a stray `#[test] fn fleet_canary()` block) — evidence of a mutation harness writing into the source
tree; cargo never compiles a `.test_patch`, so it is dead weight that also duplicates the real test.
And `Cargo.toml` declares `categories = ["…", "no-std"]` while `lib.rs` calls `std::time::SystemTime` —
the crate cannot build in a `no-std` context it advertises.

## 7. Also worth knowing: the API-size ranking is a trap in *both* directions

The naive ranking puts these in the fleet's top 50 by `size`. Actual trees:

| repo | API size | real tree | ratio |
|---|---|---|---|
| `observation-primitive-rs` | 97,986 KB | 9 KB | 0.0001x |
| `fleet-coordinate` | 369,250 KB | **87 KB** | 0.0002x |
| `fleet-resonance` | 355,735 KB | 173 KB | 0.0005x |
| `ternary-fleet-integration` | 83,687 KB | 24 KB | 0.0003x |

`fleet-coordinate` — "Fleet coordinate system — trust, intent, and emergence in multi-agent fleets" —
is an **87 KB, 18-file crate** (with real tests and a real CI workflow, to its credit). Ranking by API
size would have you believe it is the 29th-largest repo in the fleet. Ranking by tree bytes puts it
where it belongs. This is the same lesson as the API-size/history trap, running the other way: history
is not substance, and neither is its absence.

---

## Method notes / honest limits

- Census paged to exhaustion; de-dup assertion passed. Fork filter applied **after** confirming all 16
  prior targets are `fork=False`.
- Ranking used `git/trees/{branch}?recursive=1` blob sizes with vendor/build prefixes stripped
  (`target/`, `node_modules/`, `vendor/`, `dist/`, `__pycache__/` + 30 extensions), **not** API `size`.
  0 of 1,208 trees returned `truncated: true`.
- Twin detection used **blob-SHA sets** (content identity) and was re-confirmed by clone + `diff -rq`.
- **No cargo/rustc in this sandbox.** All Rust findings are inspection + independent Python
  re-implementation. I did not run `cargo test` and do not claim to have.
- `pytest` is unavailable and PyPI is unreachable, so `fleet-health-monitor`/`quality-gate-stream`
  suites were **not** executed. The secret findings are static-scan based.
- SmartCRDT's full 625-file suite did not finish in-window; the cited failure is a reproduced subset.
- Secrets are reported as **shape + location only**. No credential value appears in this file, in any
  commit, or in the push below.
