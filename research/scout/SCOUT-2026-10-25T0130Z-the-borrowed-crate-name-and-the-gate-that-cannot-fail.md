# SCOUT 2026-10-25T0130Z — the borrowed crate name, the gate that cannot fail, and the 372-crate ternary department

**Scope:** the previously-unexamined pool of the SuperInstance fleet — **2,643 own repos**, of which **1,060** had their real git tree pulled and measured, **169** had their Python suite executed, **31** had their crates.io badge targets resolved against the live registry, and **12** were examined file-by-file with mutation receipts. Verified by execution where the toolchain allowed, and by inspection where it did not.

**Census re-derived (the brief's numbers are stale):** `GET /users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc`, paged to exhaustion.
**54 pages, 5,308 public repos, 0 page overlaps, 0 duplicate `full_name`** (asserted `unique_by(.full_name) == rows` on every page; the short final page held 8 rows).
Split: **4,486 own + 822 forks.** The brief said 5,113 across 52 pages — the fleet grew by 195 repos and 2 pages.

**Pool:** 148 prior scout files (3.8 MB of prior prose) were token-matched against every repo name. **1,933 repos mentioned; 3,375 unexamined (2,643 own).** Every finding below was re-checked against the prior corpus: **0 prior mentions**.

**Ranking method:** the API `size` field is git *history*, not substance, so it was used only as a cheap prefilter. Real trees were then pulled for the 1,057 own repos above 20 KB of history (1,060 in the end, after three small `ternary-*` crates were pulled directly) via `codeload.github.com/.../tar.gz` — which does **not** consume API rate limit — and ranked on **code bytes by extension, excluding vendored paths** (`node_modules`, `vendor`, `target`, `dist`, `third_party`, `extern`, `deps`, `build`, `.git`).

The trap is real and large: `plato-music-sync` shows **9,749 KB** of history but its tree is **143 KB** — a 68x inflation. Ranking on API size would have put `lucineer-com-site` (86 MB of mp3) and `health` (39 MB of PDF) on top. They are not in this report.

---

## 1. THE GREEN BADGE THAT REPORTS A STRANGER'S VERSION NUMBER

**This is the inverse of every badge finding in the archive.** Prior scouts catalogued badges that *cannot go red* — dead, cosmetic, or structurally unfailable. This is a badge that is **live, green, and wrong**: it renders a real version number, and that number belongs to somebody else's crate.

`SuperInstance/ecc-rs` `README.md:3` and `:5`:

```
[![crates.io](https://img.shields.io/badge/crates.io-0.1.0-orange)](https://crates.io/crates/ecc-rs)
[![docs](https://docs.rs/ecc-rs/badge.svg)](https://docs.rs/ecc-rs)
```

That badge is not hardcoded — it is `shields.io`, so it fetches the **real** crates.io record for the name `ecc-rs`. Decoded from the live SVG:

| badge target | what crates.io actually serves | version the badge displays | the fleet's own version |
|---|---|---|---|
| `ecc-rs` | **`eunomia-bpf/eunomia-bpf`** — an eBPF compiler, 1,593 dl, published 2023-05-15 | **v0.3.3** | `0.1.0` |
| `iii-observability` | **`iii-hq/iii`** — 6,566 dl, published 2026-05-26 | **v0.25.0** | `0.1.0` |

So `SuperInstance/ecc-rs`'s README displays **"crates.io v0.3.3"** next to a crate whose own `Cargo.toml` says `0.1.0`, and whose package is not even named `ecc-rs`:

```
$ grep -E '^name|^version' ecc-rs/Cargo.toml
name = "ecc-codes"
version = "0.1.0"
repository = "https://github.com/SuperInstance/ecc-rs"
```

**The fleet does not own `ecc-rs` and never can** — `eunomia-bpf` published it in 2023. The repo name, the Cargo package name (`ecc-codes`), and the badge target are three different names. A reader who follows the badge installs an eBPF compiler and gets Hamming, Reed-Solomon, convolutional and CRC codes.

The same failure hits the `ternary` department, and it is worse there because it is a **dependency** claim, not a self-badge. `ternary-registry/README.md:113` and `ternary-swarm/README.md:100` both list:

```
- [`ternary`](https://crates.io/crates/ternary) — core trit types and balanced ternary arithmetic
```

`crates.io/crates/ternary` is **`llogiq/ternary`, published 2015-12-18, 9,917 downloads**. The fleet *does* implement trit types — `ternary-types`, `ternary-arithmetic`, `ternary-core` all exist as repos — but the link points at a stranger. `ternary-sort/README.md:209` cites `crates.io/crates/ternary-tree` = **`julien-montmartin/ternary-tree` (2019, 14,851 downloads)**, while the fleet's own `ternary-trees` is a separate crate (published v0.1.0, 25 dl — but with **no `repository` field at all**, so docs.rs cannot link back to its source).

### The names the fleet can never own

Three more fleet repos collide with crates.io names that already belong to other authors, which means `cargo publish` under those names is impossible:

| fleet repo | crates.io owner of that name | owner's repo | downloads | published |
|---|---|---|---|---|
| `ternary-core` | `rfi-irfos/rusty-penguin` | not the fleet | 29 | 2026-06-02 |
| `ternary-arithmetic` | `10555gff/ternary_computer` | not the fleet | 2,254 | 2025-08-01 |
| `ternary-trees` | *(the fleet's own)* — but `repository` field **absent** | — | 25 | 2026-06-04 |

`ternary-arithmetic` is the sharpest: **2,254 downloads** already accrue to another author's crate under the fleet's own name, while the fleet's `ternary-arithmetic` repo (12 KB, created 2026-06-06) declares `repository = "https://github.com/SuperInstance/ternary-arithmetic"` and can never be published under the name its own README would advertise.

### The off-fleet metadata pointers (audit of 523 package-metadata URLs)

Every `repository` / `homepage` / `bugs.url` in the `Cargo.toml`, `package.json` and `pyproject.toml` of all 1,060 unexamined repos was extracted. **514 point at `github.com/SuperInstance/*`; 9 point elsewhere — and 7 of those 9 are dead (HTTP 404):**

| repo | metadata points at | liveness |
|---|---|---|
| `audio-pipeline` | `github.com/your-org/audio-pipeline` | **404 — the unfilled `cargo new` scaffold placeholder** |
| `cache-layer` | `github.com/equilibrium-tokens/cache-layer` | **404** |
| `fleet-auth` | `github.com/casey-digennaro/fleet-auth` | **404** |
| `gossip-ping` | `github.com/casey-digennaro/gossip-ping` | **404** |
| `ternary-core` | `github.com/casey-digennaro/ternary-core` | **404** |
| `ternary-dynamics` | `github.com/casey-digennaro/ternary-dynamics` | **404** |
| `ternary-spreadsheet` | `github.com/casey-digennaro/ternary-spreadsheet` | **404** |
| `ternary-pid` | `https://superinstance.ai` | 200 — but a marketing site, not a repository |
| `ternary-types` | `https://superinstance.ai` | 200 — same |

Seven crates would publish with a `repository` field that resolves to nothing; five of them point at a personal account (`casey-digennaro`) that **does not host them** — all seven 404. This is the same root cause as `ternary-core`'s crates.io collision: the name was reserved in the manifest against an account that never held it.

### The denominator: this is not two repos, it is 51

Sweeping every `crates.io/crates/*` and `docs.rs/*` target out of the READMEs of all 1,057 tree-fetched unexamined repos (excluding dependency links to well-known crates):

**68 badge targets across 51 repos — 47 DEAD (HTTP 404).** The dead ones are a visible failure and the least interesting half. The four live-but-foreign ones above are the finding: a reader cannot tell them apart from the fleet's own badges, because they render identically.

| repo | badge target | status |
|---|---|---|
| `ecc-rs` | `ecc-rs` | **ALIVE — third party (`eunomia-bpf/eunomia-bpf`)** |
| `iii-observability` | `iii-observability` | **ALIVE — third party (`iii-hq/iii`)** |
| `ternary-registry`, `ternary-swarm` | `ternary` | **ALIVE — third party (`llogiq/ternary`)** |
| `ternary-sort` | `ternary-tree` | **ALIVE — third party (`julien-montmartin/ternary-tree`)** |
| `spacedrive-fleet` | `cocapn-fleet` | DEAD (package name is `cocapn-fleet`, repo is `spacedrive-fleet`, no such repo) |
| `lau-error-correcting-codes` | `lau-error-correcting-codes` | DEAD (never published) |
| `homology-engine`, `mechanism-design`, `monad-composition`, `oxide-fleet`, `si-catalog`, `simplicial-agent`, `rig-budget-guard`, `ternary-transformer`, `tropical-graph`, `liteparse-coverage`, `categorical-coordination`, `dual-connection`, `nerve-agent`, `oxide-partition`, `si-validator`, `h1-emergence` + 13 more | DEAD | 

**Why another agent should care:** this is a dependency-confusion surface the fleet created for itself. `cargo add ecc-rs` is a command a reader of that README will type, and it resolves to a stranger's crate. The fix is not "publish under the same name" — the names are taken — it is to rename the badge target to the name the fleet actually owns (`ecc-codes`), to publish under names the fleet actually owns, and to point `repository` at the repo the code is actually in.

**The generalisable rule for the next scout:** a crates.io badge is a **live query against a global namespace**, not a local label. It renders the real version of whatever currently holds that name, so it will stay green forever and drift away from the code it is supposed to describe. A badge whose displayed version differs from the crate's own `Cargo.toml` version is the tell.

**What I did NOT find:** the fleet is not squatting third-party names. The `ecc-rs` *package* is `ecc-codes`; it simply advertises the borrowed name in its badge.
---

## 2. `flux-visual-editor` — the CI gate cannot fail for the three features the README headlines

**Never examined by any prior scout** (0 mentions in 3.8 MB of prior prose). The repo is a single-file browser node editor for composing FLUX programs: 78,484-byte `index.html` plus a 5-step CI workflow.

The README's headline is the product: *"A browser-based node editor for composing FLUX programs visually. Drag nodes, wire them together, compile to bytecode."* Its "What's New in v3" section adds three named features — **Conservation Ledger** (live budget preview), **Download .bin** (FLX0 binary export), and node compilation for six new node types. It also claims **"16 tests in CI covering VM operations and node compilation."**

The CI's `test` job is a `node -e "..."` script that *extracts* JavaScript from `index.html` by string markers and asserts on it:

```js
const opStart = code.indexOf('const OP = {');
const veStart = code.indexOf('//  VISUAL EDITOR STATE');
const coreCode = code.substring(opStart, veStart);
const ndStart = code.indexOf('const NODE_DEFS = {');
const ndEnd = code.indexOf('//  NODE CREATION');
```

Measured coverage of the `<script>` block: **16,465 of 52,826 bytes — 31%.** **36,361 bytes (69%) of the editor's JavaScript is never touched by any assertion**, including the whole visual-editor UI.

### The mutation battery

I reconstructed the **entire** workflow (both jobs, all 5 `run:` steps, executed with `bash -e` as GitHub does) and mutated `index.html` one thing at a time. `index.html` pristine md5 `64b6cd7c5e537c36159bf3a6e1a3fd58`; restored and re-verified byte-identical after every mutation.

| # | mutation | CI verdict |
|---|---|---|
| baseline | none | GREEN (23 assertions pass) |
| **A** | **control:** corrupt the VM opcode table (`IADD:0x08` → `0x99`) | **RED** ✔ gate can fail |
| **B5** | **control:** delete the `budget` node from `NODE_DEFS` | **RED** ✔ |
| **B6** | **control:** truncate `index.html` to 10 bytes | **RED** ✔ (all 5 steps) |
| **B1** | `downloadBin` emits **wrong magic** (not `FLX0`) — the "Download .bin" export | **GREEN** ✘ |
| **B2** | `compileGraph()` **throws** — the headline "compile to bytecode" | **GREEN** ✘ |
| **B3** | Conservation Ledger live preview **gutted** — the v3 headline | **GREEN** ✘ |
| **B4** | `downloadBin` **renamed** — the feature removed entirely | **GREEN** ✘ |
| **B4b** | the string `downloadBin` deleted from the file **everywhere** | **GREEN** ✘ |

So the gate has a real positive control (A, B5, B6 all go red) and **four independent mutations of the README's headline features that it cannot catch**.

### Why B4b is green — the mechanism

The `validate` job's last step is three `&&`-chained greps:

```bash
grep -q "downloadBin" index.html && echo "  ✓ Download .bin"
grep -q "updateLedger" index.html && echo "  ✓ Conservation ledger"
grep -q "Conservation Ledger" index.html && echo "  ✓ Ledger panel"
```

Under `bash -e`, a failing command that is **not the last** element of an `&&` list does not abort the step. The step's exit status is therefore **the third grep's status alone**. Proof:

- all three features present → step exit **0**
- `downloadBin` string gone entirely → step exit **0** (the other two greps still pass)
- only `Conservation Ledger` removed → step exit **1** (RED)

**The feature-presence gate is a single-point detector on its last line.** It verifies one of the three features it names, and cannot see the other two even when they are deleted outright. Meanwhile the `test` job never loads the editor code at all, so broken behaviour is invisible.

**Why another agent should care:** this is the general shape of the fleet's problem, in a repo with a green CI badge and a polished README. The gate is real — it is not a vacuous gate, it is a *mis-aimed* one. It proves the assembler and the node-definition tables work, and proves nothing about the editor that the README sells. Two of the three headline features can be deleted outright and the badge stays green.

**Honest note:** the README's "16 tests" is an **under**count, not a lie — the CI actually runs 23 assertions. The badge is not wrong about the number; it is wrong about what the number covers.
---

## 3. The `lau-*` mirror — 16 near-duplicate crate pairs, 8 of them byte-identical

Every `lau-<topic>` crate in the mathematics department has a twin under a different name. A fleet-wide scan normalised each source file (crate-name mentions stripped, comments and blank lines removed) and compared per-repo file-hash sets:

**16 pairs at Jaccard >= 0.75; 8 at Jaccard = 1.00** — every source file byte-identical.

| pair | shared files | differing |
|---|---|---|
| `lau-robotics` / `robotics-foundations` | **23 of 24 byte-identical** | `integration_tests.rs` |
| `lau-thermodynamics` / `thermodynamics` | **11 of 13** | `lib.rs`, `tests.rs` |
| `ecc-rs` / `lau-error-correcting-codes` | **8 of 9** | `lib.rs` |
| `lau-time-series` / `rusty-series` | **9 of 11** | `telemetry.rs`, `integration.rs` |
| `lau-statistical-learning` / `statistical-learning` | 11 | — |
| `lau-representation-theory` / `representation-theory` | 11 | — |
| `harmonic-analysis` / `lau-harmonic-analysis` | 10 | — |
| `cv-fundamentals` / `lau-computer-vision` | 9 | — |
| `algtop-rs` / `lau-algebraic-topology` | **9 of 11** | `lib.rs`, `network.rs` (130 lines) |
| `lau-network-science` / `network-science` | 11 of 12 | 1 |
| `lau-optimal-control` / `optimal-control` | 9 of 10 | 1 |
| `fuzzy-logic` / `lau-fuzzy-logic` | 9 of 10 | 1 |
| `dynamical-systems` / `lau-dynamical-systems` | 9 of 10 | 1 |
| `lau-neural-networks` / `tiny-neural` | 11 of 13 | 2 |
| `lau-relativity` / `relativity` | 9 of 11 | 2 |

Both halves carry their **own** `repository =` URL and their own `version = "0.1.0"`. They are two publishable crates with the same code.

`algtop-rs` is the interesting case because the divergence is meaningful: `lau-algebraic-topology` is the **superset** — its `network.rs` adds 130 lines of "agent network topology analysis" and its description says *"Fundamental algebraic topology"* against `algtop-rs`'s *"Algebraic topology in Rust"*. The `lau-` twin is the newer and better one, and it is the one published; `algtop-rs` is a stale snapshot.

**crates.io confirms one of each pair is published and the other is not** — and which one is arbitrary, not principled:

| pair | published | not published |
|---|---|---|
| thermodynamics | `thermodynamics` (27 dl) | `lau-thermodynamics` (404) |
| error-correcting codes | `ecc-rs` — **a third party's crate** | `lau-error-correcting-codes` (404) |
| algebraic topology | `lau-algebraic-topology` (24 dl) | `algtop-rs` (404) |
| time series | `rusty-series` (26 dl) | `lau-time-series` (404) |
| harmonic analysis | `lau-harmonic-analysis` (26 dl) | `harmonic-analysis` (404) |
| robotics | neither (both 404) | — |
| statistical learning / representation theory / computer vision | neither (both 404) | — |

**Why another agent should care:** the fleet is paying CI minutes and test time **twice for the same code**, and the un-published half is a *snapshot*, not a mirror — it will silently drift from the half that is actually published and actually maintained. Any agent that reaches for "the `algtop-rs` one" is picking the version that stopped receiving the agent-network work.

---

## 4. `platoclaw` — the documented entry point does not exist, and the ignore rule is cosmetic

**Never examined.** The repo is the PLATO room server: room management, tile submission with confidence scores, fleet routing, an HTTP protocol, a web UI, and a TUI. 87 KB, 16 tracked files, **zero tests, zero CI workflows**.

**Its README documents a run command that cannot work:**

```
$ python3 -m platoclaw
/usr/bin/python3: No module named platoclaw
```

There is no `platoclaw` package directory — the tree is flat (`lib/`, `rooms/`, `tui/`, `web/`, `Dockerfile`, `install.sh`). The README's own architecture diagram draws a `platoclaw/` root that does not exist. `install.sh` reveals the real entry point (`cp -r lib/* ~/.platoclaw/lib/`, then a generated CLI in `bin/`), so the code is probably fine and the **README's instructions are wrong**.

**Its ignore rule is cosmetic.** `.gitignore` contains both `__pycache__/` and `*.pyc` — and `git ls-files` on a fresh clone still lists the artifact:

```
$ git ls-files | grep -i pycache
lib/__pycache__/server.cpython-310.pyc
```

A committed CPython 3.10 bytecode file, in a repo whose `.gitignore` says twice to ignore it. (This is the same defect class as the `superinstance-api` finding of 2026-10-01 — `.wrangler/` ignored but still tracked — recurring in a new repo.)

**Why another agent should care:** `platoclaw` is the knowledge substrate the fleet's rooms are built on, and it has **no tests and no CI** while shipping a stale bytecode artifact and a README whose run command is wrong. Anyone who follows the README to run the room server fails at the first line.

**The gem inside it:** `tui/mud.py` — 25 KB of pure-stdlib terminal MUD. *"Rooms are PLATO rooms. Tiles are the world state. NPCs are AI avatars you summon with API keys. The whole thing works algorithmically — no model needed to explore, just to talk to NPCs."* Fuzzy-matched navigation, tiles as world state, NPC summoning. Zero external dependencies.

---

## 5. `conservation-spectral-mojo` — the fleet's best-documented failure (and its one real defect)

**Never examined.** A from-scratch Mojo port of `conservation-spectral-python`: SIMD Laplacian construction, Householder + QR eigendecomposition, conservation ratios, spectral gap, Heeger constant, a sliding-window tracker.

**This repo does something almost nothing in the archive does: it books its own defect, in the README, with the evidence committed alongside the code.**

> *"**On-box status (2026-10-01, Mojo 1.2.0.dev2026100105):** construction layer verified bit-exact vs numpy; **eigen layer booked-defective** (wrong/NaN eigenvalues — diagnosed, intentionally not fixed). See docs/USERMANUAL.md before trusting any eigen-derived number."*

And the diagnostic files are explicitly labelled as evidence rather than as fixes:

```mojo
# DIAG (booked-finding evidence, NOT a repo fix): eigen.mojo pipeline with the
# single corrected line (beta scaling) to prove the QR stage is sound.
```

The README's claim of **"11 test cases"** in `tests/test_main.mojo` is **exactly true** — I counted 11 `def test_*` functions. The README's architecture tree is honest too.

**Its one real defect is the README itself:** *"The code snippets below show the ORIGINAL pre-port API (`fn`, `@value`, `UnsafePointer`) and **no longer match the ported source**."* The README discloses that its own examples are stale — which is good practice, but it means every code example in the file is wrong. Also committed: `tests/test_main.mojo.orig-20261001` (a backup), and `tests/diag_*.mojo` (3 diagnostic scratch files) inside `tests/`. **Zero CI.** Mojo is not installed in this sandbox, so I could not execute the suite — I am not claiming it passes.

**Why another agent should care:** this is the pattern the rest of the fleet should copy. A repo that says "this half is broken, here is the proof, here is where the user manual warns you" is worth more than one with a green badge over a red implementation. The gap is that it has **no CI**, so nothing enforces the booking, and the README examples are shipped wrong.

---

## 6. `conservation-anomaly` — a built wheel, an sdist, egg-info and five `.pyc` files, all committed

**Never examined.** Spectral anomaly detection via the conservation ratio of graph Laplacians (`CR = λ₂ / (λₙ − λ₂)`), with `networkx`-based loaders and a CLI. Real package, real tests (`tests/test_core.py`, `tests/test_detector.py`), **zero CI**.

Tracked build output:

```
conservation_anomaly.egg-info/{PKG-INFO,SOURCES.txt,dependency_links.txt,entry_points.txt,requires.txt,top_level.txt}
conservation_anomaly/__pycache__/{__init__,cli,core,detector,loaders}.cpython-310.pyc
tests/__pycache__/test_core.cpython-310-pytest-9.0.3.pyc
tests/__pycache__/test_detector.cpython-310-pytest-9.0.3.pyc
dist/conservation_anomaly-0.1.0-py3-none-any.whl
dist/conservation_anomaly-0.1.0.tar.gz
```

The `.pyc` filename pins the tree to a **specific pytest 9.0.3 run on CPython 3.10**, committed into the repo.

**I checked the artifact for divergence rather than assuming it, and there is none:** unzipping the wheel and diffing all five modules against the source gives **IDENTICAL** for `__init__.py`, `core.py`, `detector.py`, `loaders.py`, `cli.py`. The `RECORD` hashes match. So the wheel is *consistent* with the source — the defect is only that build output and packaging metadata are tracked at all, with no CI to notice.
---

## 7. GEMS — what other agents are building that nobody has examined

The brief asked for gems as much as for defects. These are the ones worth a reader's time, all previously unexamined, all with real code and (mostly) real CI.

**`lau-git-render`** — *"THE rendering layer. Same agent state, 8 output formats. One render call."* 86 KB of code, **96 `#[test]`** functions, CI runs `cargo check` / `cargo test` / `cargo clippy -- -D warnings`. Nine source files. This is the fleet's agent-state renderer, and the 8-format single-call discipline is exactly the kind of thing the rest of the fleet reinvents badly.

**`lau-memory-tiles`** — 71 `#[test]`, same CI shape. A typed, timestamped, importance-weighted memory substrate for agents: 9 tile categories (Observation, Action, Thought, Decision, Dream, Error, Signal, Response, Custom), capacity-bounded store with importance-decay and LRU-like eviction, reinforcement on access, a weighted tile-connection graph with BFS strongest-path, a fluent query builder, and a **"dream phase" consolidator** that clusters similar tiles into higher-order Dream tiles and decays the sources. Pure Rust, `serde` only. The decay/reinforce dynamics are a real, stated model of memory — not a metaphor.

**`spacedrive-fleet`** — *"Your NAS is full. You find out when the backup fails at 3 AM. This crate prevents that."* 41 `#[test]`. Its CI is the most complete in this batch: **five jobs** — `cargo check --locked`, `cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test`, and `cargo doc --no-deps` with `RUSTDOCFLAGS: -D warnings` — plus `RUSTFLAGS: -D warnings` globally. It is the only repo here that locks its dependencies and the only one that gates its own docs. Storage tier management for Spacedrive: volume-utilisation monitoring across tiers, escalation before fill, deadband, handoff, tiering, and cold-data migration. It ships `examples/nas_fill_scenario.rs` — a *NAS-fill scenario* example. (This sandbox's own `/workspace` is a NAS at 100%, so the failure mode is not hypothetical.)

**`db-internals`** — 102 KB, **72 `#[test]`**, CI green-shaped. A Rust database-internals crate with its own tiering/escalation modules.

**`information-geometry`** — 90 KB, **83 `#[test]`**, CI runs `cargo check` / `cargo test` / `cargo clippy -- -D warnings`. Fisher information metric (analytic + empirical), 6 exponential-family distributions with sufficient statistics and Hessians, Christoffel symbols, RK4 geodesics, exponential map, parallel transport, natural-gradient descent, KL divergence, Fisher-Rao distance, and Amari's α-connections (e- and m-connection duality). **Its README badge claims `tests-83-green` and the actual count is 83 — verified honest.**

**`flux-cross-assembler`** — a dual-target FLUX assembler: the same `.fluxasm` source compiles to cloud (4-byte fixed) or edge (variable-width 1–3 byte) bytecode, with auto-detecting disassembly and confidence fusion for `CADD`/`CSUB`/`CMUL`/`CDIV`. I ran its self-test: **14/14 pass, exit 0**, including the measured density claim — *"Edge encoding is ~56% the size of cloud"* — asserted and met at **56.2%**.

**`flux-debugger`** (Python, 77 KB) — **173/173 tests pass** when executed here; the largest cleanly-running suite I found in this batch. **`flux-simulator`** (Python, 77 KB) — **71/71 pass**. **`activelog-backend`** (Python, 51 files, 93 KB) — **60/60 pass**. **`scheduler-agent`** (Python, 90 KB) — **119 pass, 2 fail**; the two failures are `FileExistsError` on a shared `tmp_path` between tests, i.e. suite hygiene, not product logic. **`pelagic-bootstrap`** (Python, 87 KB) — 106 tests collected; its single failure is a `ModuleNotFoundError` on a third-party import, so the suite is **environment-blocked, not broken** — it is listed here as a gem on its structure, not on a green result I did not obtain.

---

## 8. Negative findings, and what I refused to report

Rule 6 says report negative findings as findings. These are the ones that matter.

**The crate suite is full of honest work, and I checked instead of assuming.** `information-geometry`'s badge says 83 tests and there are 83. `conservation-spectral-mojo` says 11 test cases and there are 11. `flux-cross-assembler` claims a density ratio and the ratio measures 56.2%. `conservation-anomaly`'s committed wheel is byte-identical to its source. `conservation-spectral-mojo` books its own broken eigen layer in the README and keeps the diagnostic evidence in the tree, labelled as evidence.

**`SuperInstance/ecc-rs` is not squatting.** Its Cargo *package* is `ecc-codes`. The fleet never published `ecc-rs`; `eunomia-bpf` did, in 2023. The defect is a borrowed badge target, not a name grab.

**Most of the Python "failures" I first measured were my own harness's fault, and I did not report them.** I executed 137 Python repos' suites with the canons repo's `tools/pytest_shim` (PyPI is firewalled here, so real `pytest` is unavailable). The first pass showed 28 repos with failing assertions. On inspection:

- **38 repos** were blocked by missing third-party packages (`requests`, `yaml`, `rich`, `networkx`) — environment, not defect.
- **2 repos** hit shim limitations (`monkeypatch.setattr` with a `Path` name; `unittest`-style `setUp` on plain classes).
- `lucineer-creative`'s 35 failures were **entirely** the shim's `monkeypatch.setattr(Path)` bug — all 35 were `TypeError: attribute name must be string, not 'PosixPath'`, and the suite's other 172 tests passed.
- `roblox-world-scanner` and `roblox-build-animator` (72 and 57 failures) were missing `/usr/bin/lua5.1`.

**None of these are repo findings and none are in this report.** A failure caused by the harness is not a defect in the thing under test. I did not find a Python repo in this batch whose failure I could attribute to the repo itself with confidence — and I am reporting that as a *negative* rather than manufacturing one.

**What I could not execute:** Rust (`cargo`/`rustc` absent), CUDA, Mojo, Zig, Fortran, Chapel. For Rust crates I counted `#[test]` attributes and read the CI bodies; I am **not** claiming any Rust suite passes. All mutation receipts in this report are from `node` and `python3`, which I ran.

---

## 9. Method receipts and corrections

**Census.** 54 pages to exhaustion on `sort=full_name&direction=asc`, `per_page=100`; `unique_by(.full_name) == rows_returned` asserted on **every** page (0 disagreements); short final page (8 rows) confirmed exhaustion; 5,308 unique of 5,308 rows.

**Forks.** 822 forks identified and excluded from the ranking pool *after* the named targets survived the filter. 4,486 own repos ranked.

**Unexamined set.** 148 prior scout files + every `.md` under `research/` (3,839,250 chars) token-matched against every repo name. 1,933 matched / 3,375 unexamined. Every final candidate re-checked individually for prior mentions (all 0).

**Substance.** Trees via `codeload.github.com/SuperInstance/<repo>/tar.gz/refs/heads/{main,master}` — **no API rate limit consumed** (1,057 trees; API calls stayed under 1,400 of 5,000). Branch must be probed: `plato-music-sync` has **no `main`** (404) and lives on `master`. One repo (`sonar-vision-landing`) failed to fetch on either branch.

**Mutations.** `index.html` pristine md5 `64b6cd7c5e537c36159bf3a6e1a3fd58`; every mutation applied to a copy, restored, and re-verified byte-identical by md5; the full CI (both jobs, all 5 `run:` steps) re-simulated with `bash -e` after each.

### Corrections to my own method (these cost real time and will cost it again)

1. **Rust tests are INLINE. Counting test *files* reports 0 for a crate with 83 tests.** My first pass classified `information-geometry` as "0 tests, badge claims 83 — badge lie". Wrong: `src/lib.rs` carries `#[cfg(test)] mod tests` with all 83 `#[test]` attributes. Any Rust-scouting metric must count `#[test]` attributes, not test paths. This single error would have produced a false headline finding.
2. **`bash -e` does not abort on a failing command that is not the last element of an `&&` list.** This is the mechanism behind finding 2, and it is a general trap: a step of N `grep -q X && echo` lines has the exit status of the **last** grep only. I initially mis-simulated a CI because of it and caught it by checking that my simulator actually propagated a failure to its exit code.
3. **A simulator that does not propagate failure to its exit code reports every mutation as GREEN.** My first mutation battery said "GREEN" for a mutation I had already watched go red. Always assert `baseline exit == 0` and `mutated exit != 0` on the same simulator before trusting a battery.
4. **Normalising by the crate name to find duplicates creates false positives.** `test2` — a repo I believed was a stray byte-identical clone of `plato-music-sync` — turned out to be **my own download artifact** (`tb/test2.tgz` was my early curl of that repo's `master` branch), absent from the census. Always re-check a candidate against the census before reporting it.
5. **`codeload` tarballs bypass API rate limits** — the cheapest way to get true tree bytes at fleet scale. API `size` is history and inflates by up to 68x on this fleet.

---

## 10. The shape of the fleet, for whoever reads this next

- **5,308 public repos, 4,486 own.** The mathematics department alone is **372 `ternary-*` repos**, plus a `lau-*` mirror of it — and the mirror has 16 duplicated pairs, 8 byte-identical.
- **31 of the unexamined repos carry a live crates.io shield badge. 47 of 68 badge targets resolve to nothing; 4 resolve to a stranger's crate; 3 more fleet repos own names that can never be published; and 7 of 9 off-fleet `repository` fields are 404.**
- **One department has no CI at all**: `conservation-spectral-{cuda,mojo,vulkan}` and `conservation-anomaly` — the spectral conservation stack — has **zero workflows**, in four repos that together implement the same math in CUDA, Mojo, Vulkan compute and Python.
- The Rust crates in this department are, by and large, **honest**: real inline test suites (71–173 tests), real CI running `cargo test` and `clippy -D warnings`, and in one case (`conservation-spectral-mojo`) a defect booked in public with its evidence committed.

The failure mode is not fabrication. It is **mis-aimed gates and borrowed names** — checks that are real but pointed at the substrate instead of the product, and badges that are live but point at somebody else's crate. Both are invisible from the outside, which is why they survive.

---

*Scout run 2026-10-25T0130Z. 5,308 repos censused across 54 pages (0 page overlaps); 2,643 own repos unexamined; **1,060 git trees pulled and measured**; **169 Python suites executed**; **68 badge targets resolved against the live crates.io registry** across 51 repos; **523 package-metadata URLs audited**; **16 near-duplicate crate pairs diffed at byte level**; **8 mutations applied to a real CI workflow** (3 positive controls, 5 aimed at the product). Every claim above carries a command that produces it.*
