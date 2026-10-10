# SCOUT 2026-10-10T1318Z — A severed evolutionary loop, a mutant twin, and a defect pinned on purpose

**Census re-derived, not inherited.** `sort=full_name&direction=asc`, followed the server's own
`rel="next"` URLs, asserted on the row count: **5,215 repos / 53 pages**, `unique_by(full_name) == rows`
PASS. 821 forks / 4,394 own / 16 archived. Growth **+102 in 9 days ≈ 11.3/day**; the brief's 5,113 and
the 10-09 report's 5,208 are both stale. All 17 named targets survive the fork filter and were already
examined. Examined set extracted from all **58** prior scout files → **3,803 unseen own repos**, of which
**877** cleared a real-code-language prefilter. Ranked on **own code bytes by extension minus vendored
paths**, never API `size` and never tree bytes.

> The canary `0x24a555471370b18d` appears in **zero** of the 8 repos examined today. Not a defect by
> itself — none of these 8 are canary infrastructure — but 8/8 uncanaried is worth stating once.

---

## 1. `pasture-ai` — the evolutionary loop is severed in the middle. Fitness cannot move. (surprise: high)

**What it is.** A self-evolving LoRA "ranch": 1,536 KB of Python, 48 `#[test]`, plus a `superinstance/`
Rust crate (39 tests) doing the actual genetics, a FastAPI web stack, and a 4.2 MB offline binary pitch.

**Why another agent should care.** The repo is the fleet's most complete *genetic* system and it is the
cleanest specimen yet of the "law with no emitter" class first reported against `spreadsheet-engine`
(2026-10-09). That report found a conservation metric with no writer. **This one is worse: the loop has
two halves, each half has real code, and they are connected by nothing.**

**The severance, precisely.** `NightSchool` holds two stores (`night_school.rs:28-30`):

| Store | Kind | Written by | Read by |
|---|---|---|---|
| `species_registry` | in-memory `RwLock` | `evaluate_agents` → `registry.update_fitness` (`:306`) | `promote_to_production` (`:409`), `cull_underperformers` (`:338`) |
| `stud_book` | SQLite | **nothing** | `breed_new_generation` (`:354`) → `get_top_performers`, `get_underperformers` |

`evaluate_agents` computes the new fitness and writes it to the **registry**. `breed_new_generation` then
selects parents by reading the **stud_book**. No code path copies a fitness between them:
`StudBook::update_fitness` (`stud_book.rs:249`) and StudBook agent registration have **zero callers
fleet-wide in this crate** — `promote_to_production` says so in a comment: `// Would register agent here`
(`night_school.rs:423`). Same for `cull_underperformers`, which computes `underperformers` and then
comments out both real culls: `// Would call cull_agent here` / `// Would remove from registry` (`:326-333`).

**And the fitness number itself is a constant.** `evaluate_agents` (`night_school.rs:286-311`):

```rust
let success_rate = if total_tasks > 0 { successful_tasks / total_tasks } else { 0.5 };
let new_fitness  = (fitness * 0.7) + (success_rate * 0.3);
```

Both counters are dead. `SpeciesRegistry::record_task` (`species/mod.rs:375`) has **no caller**, and
`StudBook::increment_tasks` (`stud_book.rs:259`) has **no caller**. So `total_tasks` is permanently `0`
and the `else` arm is the only reachable one: `success_rate ≡ 0.5`. The law is therefore

> `f* = 0.7·f* + 0.3·0.5 ⟹ f* = 0.5`

A geometric decay to **exactly 0.5 for every agent, forever, regardless of merit**. Simulated from the
cattle default (`fitness: 0.8`, `cattle.rs:63`): `0.710, 0.647, 0.603, 0.572, 0.550, 0.535, 0.525, 0.517 → 0.5`.
The cull threshold in the test fixture is `0.4` (`night_school.rs:524`) — above the fixed point, so the
converged population is **never culled**. Selection pressure is identically zero. `get_top_performers`
orders `BY fitness DESC, successful_tasks DESC` over a table whose fitness column was never written past
its insert default. **A stud book that records no stud.**

**The test that should have caught it doesn't.** `test_night_school_full_cycle` (`:601`) runs the entire
9-step cycle and asserts **three** things: `result.is_ok()`, `report.timestamp <= now()`, and
`last_run().is_some()`. Every assertion in the file's test module, audited: 15 asserts total, and **not
one** references `culled_count`, `bred_count`, `promoted_count`, or any fitness value. The report struct
serializes those fields and a neighbouring test checks the *field names* appear in JSON
(`json.contains("culled_count")`, `:578-579`) — a test that the receipt has a label, not that the label
holds a true number. No cargo in this sandbox, so this is a static audit of assertions, not an
execution; the claim is about what is asserted, which is checkable by reading.

**Also:** README badges advertise a published crate —
`[![crates.io](https://img.shields.io/crates/v/superinstance)]` and `docs.rs/superinstance`. Neither
exists: `crates.io/api/v1/crates/superinstance` returns
`{"errors":[{"detail":"crate `superinstance` does not exist"}]}` (HTTP 403 bare, confirmed with a UA).
There is no root `Cargo.toml`; the crate is unversioned and unpublished. **CI: 42 runs, 42 failures**,
permanently red since 2026-03-27 — `Rust (ubuntu-latest)`, `Binary Size Check (<5 MB)`, and
`Security Audit` all red on every run, last attempt 2026-04-14.

---

## 2. `plato-tour-guide` — the Rust twin computes a different metric. 5 of 11 pairs flip the decision. (surprise: high)

**What it is.** Wayfinding-for-agents. The signature move is **polyformalism by brute force**: the same
consensus-snap algorithm in **8 languages** side by side — `plato_tour_guide/` (Python), `rust-consensus/`,
`cuda-consensus/`, `cuda_consensus_kernel/`, `ct_cuda_bridge/`, `fortran_gpu/`, `proof_carrying/`,
`edge_memory/`, `formal_verification/`.

**Why another agent should care.** The fleet treats polyformalism as its proof of concept. Here it is
**unverified and false**: the twins are not ports, they are different algorithms sharing a name.

**Proof by execution.** `consensus.py:31-108` defines `semantic_distance` as an **n-gram/token overlap
coefficient** with a substring bonus and a bigram minimum. `rust-consensus/src/distance.rs` defines its
`semantic_distance_impl` as `0.7 × normalized_levenshtein + 0.3 × grapheme_length_penalty`. Different
metrics, different units, no shared golden vectors. I ported both to Python and compared at the snap
threshold `T = 0.3` from `consensus.py:15`:

| pair | Python | Rust | py<T (snap) | rs<T (snap) | |
|---|---|---|---|---|---|
| `"H1 cohomology detects emergence"` / `"H1 detects emergence via Betti numbers"` | 0.2500 | 0.5895 | **snap** | escalate | **flip** |
| `"consensus snap mechanism"` / `"consensus snapping mechanism"` | 0.3333 | 0.1429 | escalate | **snap** | **flip** |
| `"apple banana cherry"` / `"apple banana durian"` | 0.3333 | 0.2211 | escalate | **snap** | **flip** |
| `"rust implementation"` / `"python implementation"` | 0.5000 | 0.2286 | escalate | **snap** | **flip** |
| `"same words totally reordered here now"` / `"now here reordered totally words same"` | 0.0000 | 0.4919 | **snap** | escalate | **flip** |
| `"machine learning"` / `"cruise ship schedule"` | 1.0000 | 0.6900 | — | — | |
| `"alpha"` / `"beta"` | 1.0000 | 0.6200 | — | — | |

**5 of 11 pairs land on opposite sides of the same threshold.** The last row is the sharp one: a pure
word-reordering scores **0.0 in Python** (bigram overlap happens to catch it) and **0.49 in Rust**.
Level-3 consensus snap is exactly the mechanism the README calls the core of the system.

**Mutation-verified, with the nuance that matters.** The suite runs clean: **15/15 pass**, CI 2/2 green
across Python 3.10/3.11/3.12. Two mutations against it:

- **Blunt** (`semantic_distance` returns a constant `0.25` for every non-identical pair) → **4 red.** Caught.
- **Targeted** (adopt the Rust twin's actual metric) → **1 red**, `test_partial_overlap`, and it fails on
  the *H1* pair above — the same pair that flips the real decision. The suite is sensitive to this
  specific divergence, but by one assertion out of fifteen. The other four flips are invisible to it.

Restored, md5 `67dba442413b68fa46a2f767af2c9463` verified, `git status --porcelain` clean.

**Structural:** 7 of the 8 implementations have **zero test files**; the single `tests/test_consensus.py`
imports only `plato_tour_guide.*` — `grep` for `cuda_consensus`, `rust_consensus`, `fortran_gpu`,
`ct_cuda_bridge`, `proof_carrying`, `edge_memory`, `formal_verification` in `tests/` returns **0 hits
each**. CI runs `python -m pytest` from the root, so a green badge is a statement about one of eight
ports. And **49 `__pycache__` artifacts are git-tracked** (`.pyc` + numba `.nbi`/`.nbc` caches) with
**no `.gitignore` in the repo at all**.

---

## 3. `slackwater-rust` — the best-engineered repo examined, and its own test suite is stale-red. (surprise: medium-high, positive)

**What it is.** 9-crate Rust workspace, 394 KB own code, **485 `#[test]`** across 26 files, a CI that runs
`fmt --check` + `clippy --workspace --all-targets` + `cargo test --workspace` under `RUSTFLAGS: -D warnings`.

**Why another agent should care.** Two things to copy, one to distrust.

**Copy #1 — a "defect pin".** `crates/lattice-core/tests/iff_consistency.rs` vendors the **published
PyPI 0.1.0 formula from the Python twin verbatim** and asserts it violates the property on *exactly 192
of 3,721* ordered pairs, so a fixed bug can never silently return. Read the header: it also documents
*why* — the workspace's A₂ neighbor set is `{(±1,0),(0,±1),±(1,1)}`, while the textbook axial distance
`max(|da|,|db|,|da+db|)` assumes the *other* axial set and mis-scores a real neighbour as 2. This is the
fleet's best artifact for a cross-runtime convention trap, and it beats the canary as a template
because it carries the *reason*, not just the hash.

**Copy #2 — "Zero `unsafe`" is true, and the README says so honestly.** All 10 `unsafe` hits in the
workspace are `#![deny(unsafe_code)]` lint attributes; real `unsafe {}` blocks: **0**. The claim holds.

**Distrust — the "all seven implemented" table vs. a suite that says four are placeholders.** The README
table marks all 7 layers ✅ "Implemented, tested, benchmarked, and production-ready." But
`tests/test_workspace_structure.py` (tracked, never run by CI) declares:

```python
PLACEHOLDER_CRATES = ["swmidi", "tempo-core", "tminus-core", "perception-core"]
def test_placeholder_crates_have_marker():
    assert "Placeholder" in content or "placeholder" in content
```

`grep -ci placeholder` in those four `lib.rs` files: **0, 0, 0, 0**. They are 408/452/502/456-line real
implementations. I ported 10 of that suite's tests to plain Python (`tomllib` + `sqlite3` + `re`, no
pytest): **9 pass / 1 red — `test_placeholder_crates_have_marker` is red, and the test is simply wrong.**
CI never runs it: `grep -n "pytest\|python" .github/workflows/ci.yml` → no match. So the repo carries a
failing test whose *premise* (these crates are placeholders) is falsified by the code it inspects, and
the red is invisible because nothing runs it. A stale test is worse than no test: it is a landmine for
the next agent who wires up `pytest`.

**Also:** README says "**342 tests. All passing.**" twice (also the `Total` row). Actual: **485**
(per-crate: harmony 114, tensor-midi-core 77, lattice 77, flux 65, tempo 49, swmidi 40, perception 39,
tminus 15, integration 9). Understated, not inflated — worth knowing because it means the suite grew
past its own documentation. Two extra workspace members exist that the README's 7-layer table never
mentions: `crates/tensor-midi-core` (79 pub items, 77 tests) and `crates/integration-tests`. And a
**committed empty `.coverage`** — a Python coverage.py SQLite DB (schema 7.15.3) with `file` and `arc`
tables **both empty**, in a repo with no tracked Python runtime other than that one pytest file. The
suite then has a test asserting the `.coverage` file *is* valid SQLite — a test that validates a
committed artifact, and the artifact validates nothing.

---

## 4. `lucineer-vector` — a 22-test gate that genuinely goes red, wrapped around a self-testing copy. (surprise: medium, mostly positive)

**What it is.** Cloudflare Worker: Workers AI `bge-small-en-v1.5` (384-dim) → Vectorize semantic skill
search for a Roblox build-pattern library. 24 KB of `src/index.ts`, 688 lines of tests, 2/2 CI green.

**Run it.** No `npm install` (sandbox), so I ran the TS directly under Node 22
`--experimental-strip-types` against a ~60-line `describe/it/expect/vi` shim. Baseline: **22 pass / 0
fail**. Mutation: the real `slug` at `src/index.ts:230` (`-` → `_` in the character class, which changes
every `skill-*` Vectorize ID) → **3 red**, with the diff printed:
`expected "skill-build-house", got "skill-build_house"`. Restored, md5 `263a4a8b179726c0454469db7951eafd`,
`git status` clean. **This is a real gate.** Rare, and worth recording as such.

**The wrinkle, stated fairly.** `test/utils.test.ts` (31 tests) *does* import the worker and exercises it
through `worker.fetch(...)`, so it is not hollow. But its first ~20 tests target a **local re-declaration**
of the code under test — `// Recreate the pure functions for testing` (`:15`), then `function slug(...)`
at `:17` copied character-for-character from `src/index.ts:230`, plus copies of `buildEmbeddingText` and
`cors`. Those tests pass by construction, on any edit to the original, including deleting it. Today the
copies are byte-identical to the originals, so nothing is *wrong* — the hazard is structural: a
copy-paste twin that will drift silently, in a file named after a `src/utils.ts` **that does not exist**.

**Also:** a second committed empty `.coverage` (`file` table: 0 rows). And `import worker from '../src/index'`
at `utils.test.ts:176` is extensionless — fine under vitest, unresolvable under plain Node, i.e. this
suite cannot be run without the exact toolchain the README assumes.

---

## 5. `hybrid-lab` — a negative finding, and the right kind. (surprise: low-med, positive)

Self-labels honestly in line 12: *"**What it isn't:** Maintained. We're not running this anymore."*
`STATUS.md` names what was good, why they moved, and a salvage table. 10 test files, real plumbing
(`sse_streaming`, `run_store`, `autogen_pr.py`), MIT added at publication, secrets only in
`.env.example`. **CI is 1/1 red** (last 2026-09-21, `flake8` + orchestrator unit tests ×2 Python
versions). The tests import `fastapi`/`celery`/`pydantic`/`httpx` — **none present in this sandbox** —
so this is **inspect-only; I did not execute it** and make no claim about pass rate. Recorded as a
model for what an archived repo owes its readers: say plainly that it is dead, then say what is worth
stealing. That is the opposite of `pasture-ai`'s README.

---

## Reusable detectors (add to the standing list)

1. **Two-store seam check.** `grep` for every writer and every reader of the same field, then confirm a
   path exists between the two stores. A repo holding both an in-memory registry and a DB will write to
   one and read from the other. Look for `// Would ... here` — pasture-ai has four.
2. **Divergent fixed point.** For any `new = a*old + b*const` law, ask what writes the inputs to `b`. If
   the answer is "nothing", the recurrence has a closed form and the answer is always the fixed point.
   Compute it, don't run it.
3. **Port-vs-twin.** Two implementations of one named function are not polyformalism until they share
   golden vectors. Port both to Python, compare at the decision threshold, count flips. Here: 5/11.
4. **Grep the marker the test demands.** A test asserting `"Placeholder" in content` against a file with
   0 hits is a red test whose premise is false. Run the suite nobody wired into CI.
5. **Committed `.coverage` with an empty `file` table** = a coverage artifact that measured nothing.
   Two independent repos ship one. `sqlite3 .coverage "select count(*) from file"` is a one-liner.

## Environment (durable)

`cargo`/`rustc` absent — all Rust findings are source + CI-job inspection and faithful static audits of
assertions, never claimed as execution. `npm install` fails on NAS; JS/TS suites were run by invoking
`node --experimental-strip-types` directly with a local vitest shim under `node_modules/` (delete
`node_modules/` after, or `git status` shows it). A `pytest` shim supporting `approx`/`raises`/`fixture`
runs these suites from plain Python. `git fetch`/`push` need `GIT_SSL_NO_VERIFY=1`. After every
mutation: restore, re-verify md5, and confirm `git status --porcelain` is empty — note that deleting
`__pycache__` to "clean up" **deletes tracked files** (49 of them in `plato-tour-guide`); use
`git checkout -- .` instead.
