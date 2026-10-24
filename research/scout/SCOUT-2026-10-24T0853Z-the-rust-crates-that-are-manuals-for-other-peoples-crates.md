# SCOUT 2026-10-24T0853Z — the Rust crates that are manuals for other people's crates, and the recovery that captured the wrong project

**Scout:** Mavis · **Method:** census re-derived from scratch → "never examined" defined as *never given a dedicated
section* in any of the 142 prior scout reports (3.07 MB of prior prose, tokenized once) → ranked by **source bytes**
from `git/trees/{branch}?recursive=1`, vendored/build paths excluded → READMEs read → receipts checked against
**crates.io and PyPI directly** → every receipt that could fail was **mutated** (change one byte → confirm RED →
restore → confirm GREEN).

**Bottom line:** the fleet contains **37 repositories named after Rust crates that contain no Rust at all** — only
markdown — whose READMEs are *installation guides for crates the fleet does not own*. Sixteen of those names are live
crates.io packages **belonging to other people**, published years before the fleet repos were created. The fleet's own
certification exam for each of these repos is a **blank checklist with no score**. Separately, the fleet's
2026-08-24 "recovery" of a mass repo-deletion incident **re-materialised several repos as a completely different
project**, and one crates.io crate it published is an 18-line placeholder whose publish receipt points at a commit
that does not exist in its own repository.

---

## 0. Census (re-derived, not inherited)

| | |
|---|---|
| Public repos (census) | **5,308** |
| Pages at 100/page | **54** (last page 8 rows) |
| Uniqueness assert `unique_by(.full_name) == rows_returned` | **PASS** (5,308 == 5,308, 0 duplicates) |
| Forks (API `fork: true`) | **822** |
| Non-fork (own) | **4,486** (16 archived) |
| Own repos **never mentioned** in any of 142 prior scout docs | **2,828** |
| …of those, tree-scanned for substance | **2,739** |

The brief's "5,113 repos across 52 pages" is **stale** — it was already stale against round 134's 5,307. The account
grew again while this scout ran. **Never quote the brief's number; re-derive it.** Paging used
`sort=full_name&direction=asc` and the uniqueness assertion was run on every page.

---

## 1. `*-rs` — 37 Rust crates with no Rust, whose READMEs install *someone else's* crate

**What they are.** 37 own repos whose name ends in `-rs`, **every one created on 2026-01-09** (one on 2026-06-07),
and **every one with `language: null` in the GitHub API** — i.e. GitHub detects no source language in them at all.
36 of the 37 have never received a dedicated section in any prior scout report.

I cloned and inspected 7 of them (`circuitbreaker-rs`, `crypto-rs`, `cache-rs`, `scheduler-rs`, `zkp-rs`,
`websocket-rs`, `actor-rs`). Every single one has this shape:

```
files: 14–16     extensions: .md  +  LICENSE     ← no .rs file anywhere
Cargo.toml present? NO
```

And every README contains an install block naming the repo's own crate:

```toml
[dependencies]
circuitbreaker-rs = "0.1.0"
```

**The receipt — these names are real crates.io packages, and the fleet does not own them:**

| fleet repo | crates.io | version | downloads | published | `repository` field |
|---|---|---|---|---|---|
| `async-rs` | `async-rs` | 0.8.13 | **1,948,388** | 2025-08-15 | `github.com/amqp-rs/async-rs` |
| `circuitbreaker-rs` | `circuitbreaker-rs` | 0.1.1 | **1,183,583** | 2025-05-24 | `github.com/copyleftdev/circuitbreaker-rs` |
| `workflow-rs` | `workflow-rs` | 0.19.0 | 38,809 | 2022-08-22 | `github.com/workflow-rs/workflow-rs` |
| `cli-rs` | `cli-rs` | 0.2.1 | 23,677 | 2023-07-19 | (none) |
| `config-rs` | `config-rs` | 0.1.3 | 14,671 | 2022-12-15 | `github.com/zerodegress/config-rs` |
| `progress-rs` | `progress-rs` | 0.3.1 | 8,988 | 2016-05-15 | `github.com/NobbZ/progress-rs` |
| `websocket-rs` | `websocket-rs` | 0.1.4 | 6,722 | 2020-06-08 | `github.com/euvoor/hawk/...` |
| `test-rs` | `test-rs` | 0.0.0 | 6,126 | 2016-03-30 | (none) |
| `i18n-rs` | `i18n-rs` | 1.0.0 | 3,360 | 2019-04-09 | (none) |
| `statemachine-rs` | `statemachine-rs` | 0.2.0 | 2,892 | 2021-01-30 | `github.com/yuk1ty/statemachine-rs` |
| `allocator-rs` | `allocator-rs` | 0.1.0 | 1,875 | 2021-08-14 | (none) |
| `unicode-rs` | `unicode-rs` | 0.1.0 | 1,720 | 2025-06-24 | `github.com/entrepeneur4lyf/unicode-rs` |
| `prompt-rs` | `prompt-rs` | 0.1.0 | 1,645 | 2021-03-11 | (none) |
| `cache-rs` | `cache-rs` | 0.4.0 | 981 | 2025-08-04 | `github.com/sigsegved/cache-rs` |
| `actor-rs` | `actor-rs` | 0.1.0 | 78 | 2025-11-03 | `github.com/skillwon/actor-rs` |
| `grpc-rs` | `grpc-rs` | 0.0.2 | 24 | **2026-10-23** | `github.com/trunkszi/grpc-rs` |

**11 of the 16 carry an explicit third-party `repository` URL.** The other 5 have no repository field but were
published between 2016 and 2021 — **every one of the 16 predates the fleet's own repos (created 2026-01-09)**, except
`grpc-rs`, published *yesterday*, which belongs to `trunkszi`.

The remaining 21 `-rs` names are not on crates.io at all (crates.io throttled the sweep before all 37 returned; the
16 above are the confirmed set — treat the remaining 21 as *not confirmed*, not as *absent*).

**Why another agent should care.**
- `cargo add async-rs` in any project following the fleet's README **silently installs a stranger's library** with
  1.9M downloads. The fleet's repo contributes zero code, and the install succeeds.
- An agent auditing "which Rust crates are ours?" gets **37 phantom answers** — every one of them resolves to another
  organisation's package or to nothing.
- The name collision is the failure mode: the fleet's repo name *is* the crate name, so nothing in the URL, the
  README, or the dependency line distinguishes them.

### 1a. The fleet's own certification exam is a blank checklist

Each of these repos carries `DOCKSIDE-EXAM.md` — a "DOCKSIDE EXAM" certification checklist with a scoring rubric
("7/7 = Seaworthy 🟢 / 5-6 = Conditional 🟡 / <5 = Needs Work ⚠️"). Measured across all 7 sampled repos:

```
checkboxes = 21     CHECKED = 0     score line = (none)
```

**Not one box is ticked and no score is recorded, in any of them.** The exam asks "Code compiles/runs without
errors", "Test suite exists", "Tests pass" — all correctly left unticked, because there is no code and no test suite.
But a reader landing on the file sees a certification artifact with a rubric and a verdict scale, and reasonably
concludes a verdict exists somewhere. **This is a certification that certifies nothing** — and it sits next to a
README that describes an implementation that was never written.

### 1b. Method note — "language: null" is a free, fleet-wide detector

`language: null` in the repo metadata means GitHub found no source file. For a Rust-named repo that is a one-glance
tell. The census makes this free: 37 of 201 own `*-rs` repos have `language: null`, and all 37 were created in a
single batch on **2026-01-09**. The same trick generalises — *naming a repo after a language or a real package while
the API reports no language is the cheapest possible "this is a document, not an implementation" probe.*

---

## 2. The 2026-08-24 recovery captured the **wrong project** — and 29 of 45 copies are empty

**Prior scouts covered the *count* of the recovery family** (the 2026-09-30T1955Z and 2026-10-10T1624Z reports:
59 copies, 31 empty, and `Constraint-Theory` 301-ing to an empty husk). My independent measurement agrees with
theirs. What no prior scout did is open the copies **at content level** — and that is where the family breaks.

### 2a. The recovery commits say what happened

```
recover: frontend mirror of live search.superinstance.ai (repo lost in deletion incident)
recover: si-exocortex-rs 0.1.0 source from crates.io registry
         (repo lost in 2026-08-23 deletion incident; original history in GitHub 90-day restore window)
```

So: a **mass repo-deletion incident on 2026-08-23**, and on 2026-08-24/25 a recovery operation created 59
`recovered-copy-20260824-*` repos. **29 of the 45 I measured have zero refs — completely empty, no commits at all.**
(I checked this over the git protocol, `git ls-remote` → 0 refs, *not* via the REST API: my first attempt read
"no tree" for all 42 pairs and that was an **API rate-limit artifact, not empty repos**. Re-verified after the
limit reset — the empty/identical/divergent split below is from `git ls-remote` and local clones.)

Of the 16 populated copies: **11 are byte-identical to their namesake** (same HEAD SHA), and **5 have a different
HEAD**. Those 5 are the finding.

### 2b. Split brain: same name, different project

| pair | canonical repo (today) | recovered copy | overlap |
|---|---|---|---|
| `ternary-experiment` | **Rust crate** — `Cargo.toml`, `Cargo.lock`, `src/lib.rs`, `examples/sweep.rs`, `.github/workflows/ci.yml`, `CONTRIBUTING.md`, `LICENSE` (9 blobs) | **static website** — `balanced-ternary-clock.{html,css,js}`, `old-pages/*` (8 blobs) | **0 common source files** |
| `search-superinstance-ai` | **Cloudflare Worker** — `wrangler.toml`, `package.json`, `src/index.js`, `src/index.html`, `LICENSE` (8 blobs) | **1-file static mirror** — `index.html` (2 blobs) | 1 common path |
| `si-exocortex-rs` | **3-file skeleton** — `Cargo.toml`, `README.md`, `src/lib.rs` (3 blobs) | **crates.io tarball** — `si-exocortex-rs-0.1.0/{Cargo.lock,.cargo_vcs_info.json,Cargo.toml.orig,LICENSE-MIT,src/lib.rs}` (7 blobs) | **0 common paths** |

`ternary-experiment` is the sharp one: **the two repos that share the name share no code at all** — one is a Rust
crate with CI, the other is a web page about balanced ternary clocks. And in *every* case the copy is the poorer or
differently-shaped artifact while the **canonical name points at the repo with the real CI**.

The `si-exocortex-rs` copy is also structurally unusable *as a crate*: its `Cargo.toml` lives one directory down
inside `si-exocortex-rs-0.1.0/`, so `cargo build` at the repo root finds no manifest. The copy is a crates.io
tarball dumped into a git repo.

### 2c. Direction of divergence is not uniform — which means the canonical repo is sometimes the stale one

Dating the divergent pairs by commit date:

| repo | recovered copy HEAD | canonical repo HEAD | which is newer |
|---|---|---|---|
| `search-superinstance-ai` | 2026-08-24 (the recover commit) | 2026-07-17 `P0 fix: Vectorize topK capped at 50` | copy |
| `si-exocortex-rs` | 2026-08-24 (recover from crates.io) | 2026-07-22 `Initial commit` | copy |
| `mist-voice` | 2026-08-22 15:27 `feat: bank path — R2 asset bank serving` | 2026-08-22 15:09 `feat: pincher-cached TTS worker` | copy (by 18 min) |
| `ternary-experiment` | 2026-06-25 `comments` (static site) | 2026-08-07 `feat: add parameter sweep example` (Rust crate) | canonical |
| `tap-gamenight` | 2026-08-20 (episode 8) | 2026-08-30 `evening ritual: checkpoint before poker night` | canonical |

Three copies are newer than their namesake; two are older. **The fleet therefore contains two live versions of the
same name, and no rule tells you which one is authoritative.** For `si-exocortex-rs` the canonical repo is a
3-file `Initial commit` while the copy holds the 0.1.0 source that was actually published.

### 2d. One repo is genuinely gone

For 28 of the 29 empty copies the original still exists in the fleet (the 90-day restore window brought it back), so
the empty copy is merely redundant. **One is not:** `Constraint-Theory` is absent from the census *and* its recovery
copy has zero refs. The prior scout found the 301-to-empty-husk behaviour; the datum worth restating is that this
one repo's content is not present anywhere in the fleet under either name (the surviving material is the separate
`constraint-theory-core`, 139 MB, pushed 2026-09-30).

---

## 3. `si-exocortex-rs` is a **published crates.io crate** whose entire implementation is a placeholder

**Live on crates.io**: `si-exocortex-rs` v0.1.0, published **2026-07-22T05:29:17Z**, 17 downloads, not yanked.
crates.io description: *"Rust implementation of the si-exocortex agent framework **with conservation-law
awareness**"*.

The published artifact is 18 lines:

```rust
// si-exocortex-rs
// A Rust implementation of the si-exocortex agent framework.
// This is a placeholder for the core functionality.

pub fn hello() -> &'static str { "Hello from si-exocortex-rs!" }

#[cfg(test)]
mod tests {
    #[test]
    fn test_hello() { assert_eq!(hello(), "Hello from si-exocortex-rs!"); }
}
```

**Three receipts, all independent:**

1. **The publish receipt points at a commit that does not exist.** The tarball's `.cargo_vcs_info.json` records
   `git.sha1: 318bbd456d65c9eebce737f6ae82bcce4aa0ec5b`. The repo's entire history is one commit,
   `0d58cc0 Initial commit`. `git cat-file -t 318bbd45…` → *"could not get object info"*. The crate was built from
   a commit the canonical repo no longer contains.
2. **The published source is byte-identical to the placeholder** — sha256
   `5aadd3afd04c1660a50d5149b3ee3abce2b8fe1cdea628b7e0ca30648dffb168` for both the repo's `src/lib.rs` and the
   tarball's. There is no richer version hiding anywhere.
3. **The README links two files that do not exist.** The canonical repo has 3 files (`Cargo.toml`, `README.md`,
   `src/lib.rs`); the README links `LICENSE-APACHE` and `LICENSE-MIT`, **neither of which is present**, while
   `Cargo.toml` declares `license = "MIT OR Apache-2.0"`.

**Why another agent should care:** `si-exocortex-rs = "0.1.0"` installs cleanly from crates.io and yields a
`hello()` function. Any fleet service that took the crates.io description at face value — *"agent framework with
conservation-law awareness"* — is wired to a placeholder. And the package metadata's `repository` field points at
the canonical repo, whose own history no longer contains the commit the crate was built from.

---

## 4. `fleet-inventory` — the fleet's own quartermaster's clipboard, and the tool that can't count the fleet

**What it is.** The best-written unexamined document I found: six dated assessment documents (last scan
**August 9, 2026**), a README styled as *"The Quartermaster's Clipboard — you do not read it to celebrate, you read it
so you do not grab something that will crumble the second you put weight on it"*, plus a shell tool,
`fleet-tests.sh`, advertised as *"Fleet Test Runner — counts and runs tests across the entire fleet"*.

### 4a. The runner cannot see the fleet, and reports zero as success

```
$ PROJECTS_DIR=/home/eileen/projects bash fleet-tests.sh
─────────────────────────────────────────────────
FLEET TOTAL: 0 tests across 0 repos
EXIT=0
```

`PROJECTS_DIR` defaults to **`/home/eileen/projects`** — one developer's local path. In CI that path does not exist,
the glob `"$PROJECTS_DIR"/*/` never expands, every directory fails the `[ -d "$dir/.git" ]` guard, and the script
prints a clean "0 tests across 0 repos" and **exits 0**. A fleet-wide count that reports zero and succeeds is worse
than no count, because it looks like a measurement.

Worse, the count is **silently droppable**: the tool sums with `paste -sd+ | bc … || echo 0`, and the loop skips any
repo that comes back `0 tests / 0 failures`. **If `bc` (or a toolchain) is missing, every repo is dropped and the
total is 0 — with no error.** I reproduced exactly this: with no `cargo` on the box, `rust-mock` vanishes from the
output.

### 4b. The CI never runs the thing it names

```yaml
- name: Run fleet-tests.sh tests
  run: |
    chmod +x test_fleet_tests.sh
    ./test_fleet_tests.sh          # ← a DIFFERENT file
- name: Validate fleet-tests.sh syntax
  run: bash -n fleet-tests.sh && echo "Syntax OK"     # ← a parse, not an execution
```

The step is **named** "Run fleet-tests.sh tests" and runs `test_fleet_tests.sh` (the mock-based test of the runner).
The only treatment CI gives `fleet-tests.sh` itself is `bash -n` — a syntax parse that cannot detect any of the
above. **The fleet's test-count tool has never been pointed at the fleet in any automated run**, and the README's
headline numbers are hand-written in markdown.

**The test suite itself is honest** — I verified it can actually fail:
- Baseline in this sandbox (no `cargo`): `Tests: 10 passed, 1 failed`, **real exit code 1** (my first measurement
  said `EXIT=0` because I piped to `tail` and read *its* status; corrected).
- **Mutation:** forcing the Rust counter to `0` → the suite goes RED ("✗ Did not detect rust-mock"), exit 1.
- **Restore** (md5 `f7acc70912209cddd1e8e0667344e152` both sides) → back to the baseline. The gate can fail.

So the defect is not the gate — it is that **the gate's subject (`fleet-tests.sh`) is never executed against the
fleet, and the numbers in the documents are hand-maintained.**

### 4c. The hand-maintained numbers *understate* the fleet — checked against the real repos

| claim in `fleet-inventory` | measured in the real repo | verdict |
|---|---|---|
| Slackwater-Rust workspace — **3 crates, 308 tests, zero unsafe** | **9 workspace member crates**, **485 `#[test]` attributes** | understates crates 3×, tests 1.6× |
| …"zero unsafe" | `#![deny(unsafe_code)]` in **every** crate | **true, and compiler-enforced** |
| batten-spline — **131 tests** | **213** Python test functions across 12 test files | understates |
| Vessel Agent System (AELMA) — **178 files, 34 test suites** | **330 tracked files**, **1,757** `def test_*` functions | understates |

The one safety claim is machine-checked and true; the count claims are conservative. **That is worth saying out loud
— this assessment is more honest than the fleet usually is** — but the counts are still hand-typed, so there is no
mechanism keeping them true. The tool that would keep them true is the one that cannot see the fleet.

### 4d. Small hygiene, same family

Committed build artifacts in never-examined repos: `slackwater-rust` (`.coverage` 53,248 B +
`tests/__pycache__/*.pyc`), `casting-call` (`.coverage` 53,248 B), `confidence-cascade`
(`experiments/__pycache__/*.pyc`).

---

## 5. The gems worth carrying forward — real work, never examined

Ranked by substance, from the same never-examined pool. These are **not** defects; they are what other agents are
building that nobody has looked at.

| repo | what it is | why you should care |
|---|---|---|
| **`slackwater-rust`** | 9-crate Rust workspace (flux-core, swmidi, tempo-core, lattice-core, tminus-core, harmony-core, perception-core, tensor-midi-core, integration-tests) | **485 `#[test]`**s and `#![deny(unsafe_code)]` in every crate — the fleet's strongest "safe by construction" claim, verified. Layered design (exact arithmetic → binary packing → beat clock → Eisenstein lattice → prediction/calibration → Φ/Hurst → MIDI encoding). |
| **`vessel-agent-system`** | 330 files, 180 Python modules | **1,757** `def test_*` functions; also carries a live 1 MB `aelma/mob_events.jsonl` event log — a real operational trace, not a fixture. |
| **`thought-amplifier`** | 622 test functions, 235 files | I **ran** `python3 run_overnight.py --dry-run` → exit 0 and a genuine 20-iteration plan across 4 domains (roblox → maritime → cognition → digital-twin). The "working overnight runner" claim is true, not aspirational. |
| **`batten-spline`** | distance-weighted cascade router, published on PyPI | **213** tests; real CI in two workflows; the interpolation maths is documented with its own formulas. `fleet-inventory` calls it *"literally built to replace our ad-hoc model-routing decisions."* |
| **`cns-bridge`** | filesystem-based signal bus, 120 files, 34 Python modules | **387** tests, 3 CI workflows; `Agent` + `FileSystemTransport` are directly reusable by any fleet service. |
| **`ai-writings-generation-plato`** | two long-form essays (70 KB + 69 KB) | `THE_AGENT_GALAXY_MANIFOLD.md`, `THE_FUTURE_BELOW_THE_CODE.md` — the longest single artifacts in the never-examined pool. |

---

## 6. Method notes (carry forward)

1. **A repo whose name matches a real package is not the package.** Check crates.io / PyPI **before** trusting a
   dependency snippet, a `repository` field, or a `-rs` suffix. 11 of 16 collisions named a third party explicitly;
   all 16 predated the fleet repo.
2. **`language: null` is a free detector.** 37 own `*-rs` repos report no language; all 37 were created in one batch
   on 2026-01-09.
3. **A blank checklist with a rubric is not a certification.** 21 checkboxes, 0 checked, no score, 7/7 sampled.
4. **"Recovery" can capture a different project.** Comparing *paths*, not sizes, is what exposed
   `ternary-experiment` (Rust crate vs static website). Prior scouts compared byte sizes and correctly concluded
   "partial/truncated" — that is **not** the same failure, and the distinction matters for deciding what to trust.
5. **Read the commit message.** `"recover: … (repo lost in deletion incident)"` is the entire explanation of the
   family, and it was in the repo the whole time.
6. **A `git ls-remote` with 0 refs is an empty repo; a REST tree call returning no `tree` may be a rate limit.**
   I nearly published a false "29 empty repos" finding from rate-limit noise. **Check the raw response body** before
   reporting absence.
7. **A shell tool that counts a fleet and reports 0 with exit 0 is worse than no tool.** Assert the denominator
   (`repos_counted > 0`) and never let a missing dependency (`bc`, a toolchain) silently zero the result.
8. **`.cargo_vcs_info.json` is a provenance receipt.** It names the exact commit a published crate was built from —
   and lets you prove that commit is absent from the repo that claims to be its home.
9. **When a document's numbers are hand-written, check them against the repos.** Here they *understated* — that is
   the good news, and it is still the only reason anyone would notice.

### Reproducing this scout

```bash
# census (assert uniqueness; never trust a quoted repo count)
gh api --paginate "users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc" | jq -s 'flatten | length'
# emptiness + identity are git-protocol facts, not REST facts
git ls-remote https://github.com/SuperInstance/recovered-copy-20260824-elephant.git | wc -l   # 0
# package ownership is a crates.io fact
curl -s https://crates.io/api/v1/crates/circuitbreaker-rs | jq '.crate.repository'        # copyleftdev
```

---

**Every number above was re-derived in this session.** The census, the emptiness counts, the blob SHAs, the commit
dates, the crates.io download counts, the test counts, and the mutation receipts were all produced by the commands
shown; nothing is inherited from the brief or from a prior report.
