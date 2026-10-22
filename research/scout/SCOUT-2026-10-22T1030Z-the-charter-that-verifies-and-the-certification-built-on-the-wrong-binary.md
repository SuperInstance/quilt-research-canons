# Scout 2026-10-22T1030Z — the charter that verifies, and the certification built on the wrong binary

**Census** 5,306 repos / 54 pages, re-derived from scratch at 10:18Z. `full_name/asc` → 5,306 rows /
5,306 unique (`unique_by == rows` **PASS**), `rows == public_repos` (5,306) **PASS**. 821 forks /
4,485 own / 16 archived-own. **1,474 own names appear in the 128 prior reports → 3,011 unseen own.**
400 unseen own were tree-scanned via `git/trees/{branch}?recursive=1` (400 calls, **0 errors**) and
ranked by **code bytes minus vendored paths** (not API `size`). Top 45 cloned; 44 confirmed
**zero mentions** across the full 2,679,575-character corpus of all 128 prior scout reports.

**Toolchain note (this wipe):** the MITM proxy's leaf expired `Oct 21 23:48:43 GMT`, so **Python
`urllib` fails with `CERTIFICATE_VERIFY_FAILED`** *and* `curl` without `-k` returns `HTTP=000`.
`curl -sk` works. Rust was installed to a clean `HOME` on the overlay (`CARGO_HOME=/tmp/rawhome/.cargo`).
`crates.io` is **403** from this sandbox, so crates with external dependencies could not be executed locally.

**Two findings are the headline: one repo *understates* itself by 26 conformance points, and one
repo's receipt chain is reproducible in its science but not in its own hash.**

---

## 0 · The census was re-derived, and the account did not grow

The brief says *"5,113 public repos across 52 pages (was 4,892/49 in Sept)"*. Measured now:
**5,306 / 54**. The account has not moved since the 04:46Z round, so the growth rate is flat at
zero over the last six hours, and the brief's 5,113 figure is the 2026-10-01 figure — stale by
three weeks, not by hours. **Re-derive; do not inherit a number from a brief or from memory.**

---

## 1 · `holodeck-c` — the certification is real, and it is running the wrong binary

*"Pure C99 implementation of the FLUX-LCAR holodeck protocol… a 40-point conformance test suite.
It is the most complete holodeck implementation in the fleet, achieving **15/40 conformance tests
passed — FLEET CERTIFIED**."*

**The implementation passes 40/40. The CI never runs the suite that measures it.**

### 1a · There are two conformance binaries. CI builds the wrong one.

`src/conformance.c` is **980 lines**, implements all **40** test points (T01–T40 across 7 groups),
and has **its own `main()` at line 922**. It is a complete standalone 40-point conformance runner.

**No Makefile target compiles it.** The `test_conf` target builds `tests/conformance_simple.c`
instead — a **134-line** stand-in covering **14** of the 40 points (T01–T08, T14–T17, T21, T22).
`src/conformance.c` appears in no `gcc` line anywhere in the repo. `grep -rn "conformance\.c"`
returns three hits, and all three are prose: `src/main.c` includes only the *header*, and
`CHARTER.md` / `README.md` describe the file.

CI runs `make test` → `test_conf` → `test_rooms` → `test_serial` → `test_command`.
**The 40-point suite has never been executed by CI.**

### 1b · The number in the README is produced by no code at all

| source | what it says |
|---|---|
| `tests/conformance_simple.c` (what CI builds) | prints `Results: 14/14 passed` / `Status: ✅ FLEET CERTIFIED` |
| `src/conformance.c` (the real suite) | prints `Results: 40/40 passed` / `Status: ✅ FLEET CERTIFIED` |
| `README.md:7` | *"**15/40** conformance tests passed — FLEET CERTIFIED"* |
| `README.md:117` | *"**15/40** conformance tests — FLEET CERTIFIED** ✅"* |
| `README.md:143` | *\| Conformance \| **15/40** ✅ \| 17/40 🟡 \| (reference) \|* |

**No code prints "15" and no code contains "/40".** The README's Status section is a hand-summed
markdown bullet list: T01–T04 (4) + T05–T07 (3) + T08 (1) + T09 (1) + T14–T15 (2) + T16–T17 (2) +
T21–T22 (2) = **15**. Fourteen of those come from `conformance_simple.c`; **T09 comes from a
different binary** (`test_command`), and the README even says so inline — *"T09: Direct tell between
agents (fixed and covered by `test_command`)"*. So the headline number is a **sum across two
binaries, divided by a denominator that exists only in the README**, and the "✅" is printed by a
binary that measures 14 of 40.

### 1c · The dead suite passes 40/40

I compiled it — the suite that no Makefile target builds:

```
gcc -std=c99 -Isrc -o conf40 src/conformance.c src/room.c src/agent.c src/command.c src/comms.c \
    src/connection.c src/runtime.c src/combat.c src/manual.c
./conf40
...
T01: Create room PASS   …   T30: Command validation PASS
T31: Oversight session start and end PASS
...
T40: Experience weighting (combat effectiveness, resilience) PASS
Results: 40/40 passed
Status: ✅ FLEET CERTIFIED
```

**The repo understates itself by 26 points.** This is the *inverse* of the fleet's usual defect
(class (z), "a repo that understates itself") — and it is the good kind. A reader trusting the
README skips the best thing in the repository.

### 1d · The two suites are complementary, and CI owns only one of them

Twelve mutations, each applied to `src/`, both suites rebuilt, both run. `M0` is the unmutated
baseline. The 14-point stand-in is what CI's `test_conf` produces; `make test` is all four
binaries.

| mutation | 40-pt suite (DEAD) | 14-pt stand-in (CI's `test_conf`) | `make test` (all 4) |
|---|---|---|---|
| **M0** baseline | 40/40 CERT | 14/14 CERT | exit 0, CERT |
| M1 `room_create` → NULL | **CRASH (SIGSEGV, exit −11)** | CRASH | exit 2 |
| M2 `room_connect` no-op | 38/40 | 13/14 | exit 2 |
| M3 `cmd_tell` no-op | **40/40 CERT** | 14/14 CERT | exit 2 (caught by `test_command`) |
| M4 `agent_mailbox_send` no-op | 38/40 | **14/14 CERT** | exit 2 |
| M5 `room_add_note` no-op | 38/40 | 13/14 | exit 2 |
| M6 `manual_evolve` no-op | 39/40 | **14/14 CERT** | **exit 0, CERT** |
| M7 `room_set_booted` no-op | 38/40 | 13/14 | exit 2 |
| M8 `agent_set_permission` no-op | 39/40 | 13/14 | exit 2 |
| M9 `comms_say` no-op | 39/40 | **14/14 CERT** | **exit 0, CERT** |
| M10 `room_disconnect` no-op | 39/40 | 13/14 | exit 2 |
| M11 `agent_equipment_grant` no-op | 39/40 | 13/14 | exit 2 |
| M12 `cmd_gossip` no-op | **40/40 CERT** | 14/14 CERT | exit 2 |

Per-test failure identity, from the 40-point suite: M2 → T03,T10 · M4 → T09,T14 · M5 → T12,T13 ·
M6 → T25 · M7 → T21,T22 · M8 → T16,T17 · M9 → T08 · M10 → T04 · M11 → T15.

**The two suites are strictly complementary, and CI owns only the weaker half:**

- **M6 and M9 are invisible to `make test`** — `exit=0`, `cert=True`, every number unchanged.
  `manual_evolve` and `comms_say` can be completely broken and the CI suite is happy.
- **M3 and M12 are invisible to the 40-point suite** — it reports **40/40 CERT** with `cmd_tell`
  and `cmd_gossip` doing nothing, because T09/T11 test the `comms_*` layer, never the
  `cmd_*` handler. `test_command` catches both.
- **The union catches all 12. Either alone misses at least 2.**
- The 14-point stand-in — the one that literally prints `✅ FLEET CERTIFIED` — **misses 5 of 12**
  (M3, M4, M6, M9, M12) and on 4 of those still prints `FLEET CERTIFIED` and exits 0.

> **New class (aw) — a certification number produced by no code.** "15/40" is a hand-summed
> markdown list spanning two binaries, against a denominator that appears in no source file, and
> the ✅ next to it is printed by a binary that measures 14 of 40.
>
> **New class (ax) — a dead conformance suite beside a live stand-in.** The real suite passes
> 40/40 and is built by nothing; the proxy is built by CI and prints the certification string.
> **A repo can be simultaneously under-certified and over-certified.**

### 1e · The repo's own exam form is a blank sheet

`DOCKSIDE-EXAM.md` — the fleet's certification checklist — is present, dated **2026-04-14**, and
**every one of its 21 boxes is unchecked**. Its own scoring rule reads *"5–6/7 = Conditional 🟡,
<5/7 = Needs Work ⚠️"*. An exam with nothing ticked scores **0/7 = Needs Work** by its own rule,
while the README says `FLEET CERTIFIED`. (See §6 for the fleet-wide version of this.)

### 1f · Why another agent should care

`holodeck-c` is the fleet's **architectural reference** for the FLUX-LCAR protocol — sibling
implementations `holodeck-go` (claimed 17/40) and `holodeck-zig` are compared against it, and the
README says *"the C implementation serves as the architectural reference — every data structure
layout is visible"*. **A reference implementation whose self-reported conformance is 37.5 % when the
real number is 100 % is a reference that misleads the two siblings calibrated against it.** The
fix is one line of Makefile:

```make
test_conf: src/conformance.c $(ALL_SRC) src/holodeck.h
	$(CC) $(CFLAGS) -o $@ src/conformance.c $(ALL_SRC)
```

---

## 2 · `ropesight` — the fleet's first charter-verified experiment, and two real defects in its ledger

*"Spawned by the fleet seedbox. The seed below is the charter of record — it is versioned in this
repo's first commit and never edited afterward. **Every experiment here must carry its decision
rules as receipts dated BEFORE the run that produced the numbers.**"*

Three commits. Never named in any of the 128 prior reports.

### 2a · The charter claim is TRUE — verified byte for byte

```
first commit 57aea7a "seed: charter committed verbatim"
git show 57aea7a:README.md  vs  README.md   →  IDENTICAL  (12,707 bytes both)
git log --follow -- README.md  →  exactly one commit
```

**This is the only repo in this round where a self-description of that strength survives
verification.** It is also the only repo I found that carries its own doctrine in prose and then
*measures* the prose.

### 2b · The science reproduces exactly

`node experiments/e_rs1_rope.mjs` re-ran and printed:

```
R1 periods: Extent on Three:6(exp 6) Plain Bob Doubles:40(exp 40) Plain Bob Minor:60(exp 60)
            Plain Bob Triples:84(exp 84) Plain Bob Major:112(exp 112)
R1 lead ends: 123 / 13524 / 135264 / 1352746 / 13527486
R1 local==global runs: 18 all byte-identical: true | audit-blind same hash: true
R2 cover: 3bells=2x 5bells=8x 6bells=10x 7bells=12x 8bells=14x | blinded Minor cover uniform: true
R3 honest false alarms: 0/1516 strokes
R3c deviator Minor [method-pos]: samples=1380 clash@stroke=1380 partner=1380 ownRopeFires=480 healed=0 persist=1
R3c deviator Minor [line]:      samples=1380 clash@stroke=1380 partner=1380 ownRopeFires=480 healed=1380 persist=0
R3d conspiracy Minor:            samples=900 clash=0 uninvolvedSignal=0 fullySilent=155
R5 determinism: byte-identical over 20 hashes
chain: ok in-memory, ok from re-read file; 10 links
```

Every number matches the committed receipts **row for row**.

### 2c · A pre-registered prediction that was confirmed *and* one that was falsified

Receipt seq 3 is a `decision_rules` row that states the pass condition **before** the runs
(`"VERDICT PASS iff …"`, for R1, R1_local_global, R2_cover, R3a–R3d, R4, R5). It predicts, in
advance, that under the `method-pos` rule *"the lane cannot know its true place was lost and keeps
ringing the method from where it IS — persistence … BOOKED AS FINDINGS (no pass/fail)"*. The
committed result is `postStumbleByteEqual: 0`, `persistFraction: 1`, `closedToRounds: 0` — the
prediction held.

And receipt seq 2 (`audit_dead_draft`) records the author's **own falsification of an earlier
attempt**: *"UNVERIFIED SEALED NUMBERS NOT CARRIED: the draft sealed touch periods 180/120/36/120
and 'Doubles first lead end 13425' with no derivation. **The lead-end claim is FALSE (actual:
13524, hand re-traced).**"* and *"SEALED PREDICTION CORRECTED: 'near deviations are rope-silent'
is false in general."* The final verdict is **"MIXED/FAIL"** with R3 recorded as *"MIXED (see
payload — honest negatives are findings)"*.

**No fleet repo I have examined keeps a refutation log in its own commit history.** This is the
positive control of the round.

### 2d · Defect 1 — the chain verifies at ANY length

The repo's own verifier, `verifyChain()` from `experiments/receipts.mjs` (fnv1a64, genesis
`GENESIS`):

| check | result |
|---|---|
| baseline, 10 rows | `{"ok":true,"links":10}` |
| **truncated to 9 rows** | **`{"ok":true,"links":9}`** |
| **truncated to 8 rows** | **`{"ok":true,"links":8}`** |
| **truncated to 5 rows** | **`{"ok":true,"links":5}`** |
| **truncated to 4 rows** | **`{"ok":true,"links":4}`** |
| payload byte flipped in row 5 | `{"ok":false,"at":5,"why":"hash mismatch"}` ✓ |
| `row_hash` tampered at row 7 | `{"ok":false,"at":7,"why":"hash mismatch"}` ✓ |

**The chain catches edits and does not catch deletions.** A hash chain without an enforced head
anchor is truncation-tolerant: dropping the final verdict row leaves a chain that verifies.

**The anchor exists but is not enforced.** `experiments/outputs/e_rs1_summary.json` records
`chain.tip = "0xc89bf8425561edc0"` and `chain.links = 10` — a perfect second source to diff
against the receipts file. Nothing diffs them. The CI workflow (`node smoke.mjs`) does not either.

> **New class (ay) — a chain that verifies at any length.** `verifyChain` proves internal
> consistency, not completeness. **Detector: truncate the chain to N−1 rows and re-verify; if it
> still verifies, the chain has no head anchor.** The fix is one line: compare the file's tip to
> the tip recorded outside the file.

### 2e · Defect 2 — a clock inside the hash, so the chain is not reproducible

Re-running the experiment **rewrote both committed output files**:

```
committed row10: wallMs=2339.2 row_hash=0xf0b5521c5b4ab146
re-run    row10: wallMs=5325.3 row_hash=0xc89bf8425561edc0
SAME TIP? False
  row 4 (probe_and_derivation): DIFFERS   ← probeMs 1.969 → 7.826
  row 5 (R1_finding):            DIFFERS   ← payload identical, row_hash differs
  row 6 (R2_finding):            DIFFERS   ← payload identical, row_hash differs
  row 7 (R3_finding):            DIFFERS   ← payload identical, row_hash differs
  row 8 (R4_mapping):            DIFFERS   ← payload identical, row_hash differs
  row 9 (R5_finding):            DIFFERS   ← payload identical, row_hash differs
```

Read the diff carefully: **rows 5–9 have byte-identical payloads and differ only in `row_hash`.**
Every scientific value is deterministic; the *chain* is not, because `probeMs` (seq 4) and
`wallMs` (seq 10) are **inside the hashed rows**. One wall-clock measurement is enough to change
the tip.

So the two defects compose: the anchor is unenforceable *because* the tip is not reproducible, and
the tip is not reproducible *because* a clock is inside the hash. Move `probeMs`/`wallMs` out of
the hashed payload (or hash a *bucketed* timing) and the tip becomes a fixed anchor — at which
point truncation is detectable too.

> **New class (az) — a clock inside the hash.** A receipt chain that hashes a wall-clock
> measurement cannot be reproduced even when the underlying science is perfectly deterministic.
> **The experiment is deterministic; the receipt chain is not.** Detector: re-run the producer and
> diff the tip. If the tip moves and no payload field changed, find the timing field.

### 2f · A third, smaller gap — the chain does not bind the code

No receipt row contains a digest of `bells/methods.mjs` or `bells/rota.mjs`. Row 1 names them in
prose (`"machine":"bells/methods.mjs … + bells/rota.mjs …"`), and row 9's `"digest"` is the
**trace** digest, not a source digest. So the chain certifies a narrative about the code, not the
code. A commit that edits `methods.mjs` leaves every receipt row valid.

> **New class (ba) — a receipt of a narrative, not of an artifact.** A hash chain over payloads
> that *describe* the code is not a hash chain over the code. **Add one row: sha256 of each
> source file in the experiment.**

### 2g · Why another agent should care

The fleet's stated doctrine — from `unspoken-resonance`'s prereg chain (round 122) — is
"pre-register the decision rules, then run." `ropesight` is the **first implementation of that
doctrine I have seen that also works, records its own refutations, and refuses to declare its
negative results a failure.** The R3 "MIXED" verdict and the 0/900 silent conspiracy are the
findings; the honest label is the value.

Its central result is also directly reusable: **a coordinated two-party deviation is invisible to
every local channel and to the rounds check** (`clash=0`, `uninvolvedSignal=0`, `fullySilent=155`,
`validRowButWrong=900`) — under one rule it heals byte-identically and is undetectable forever.
That is the cleanest statement in the fleet of the blind spot that the cell doctrine keeps
discussing, and it is **measured, not argued**.

---

## 3 · `musician-soul` — the best-kept secret in the fleet, with one false promise

*"Vector-database personas that learn musicians by digesting MIDI, develop their own 'what-works'
by jamming, and evolve from imitating influences into something with a genuine musical identity —
a **soul**."* — **Pure Rust, zero dependencies, `#![forbid(unsafe_code)]`.**

### 3a · It executes, and it is honest about its count

`Cargo.toml` has an **empty `[dependencies]` section** — so `cargo test --offline` works with no
network at all:

```
test result: ok. 74 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.02s
   Doc-tests musician_soul
test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

**74 tests + 3 doctests, all passing** — exactly the count the README claims (the README does not
claim a number; the count is in the crate's own doctests and the source). CI is **green 5 times**
(2026-09-19). The crate also **distinguishes two constructs that are constantly conflated**:
`soul_percentage()` (self-generated fraction) vs `soul_print()` (centroid of *proven* patterns),
and says so plainly: *"A persona can be 90 % 'its own' by evolution while its soul print is still
empty."* It also honestly labels the Python file in a "pure Rust" crate: *"`extractor.py` is a
**standalone scaffold**, not part of the Rust crate."*

### 3b · But the determinism promise is false

The README: *"**The arc is deterministic, so your numbers will match the comments.**"* and the
example's own closing line: *"Re-run it — the arc is deterministic, so the numbers repeat."*

**8 runs of `cargo run --example jam` produced 3 distinct outputs** (md5 `98087afe29a4` ×5,
`177644122c8c` ×3, `4fae4d8874a4` ×1, `4749196cf0e6` ×1 over 10 runs). Exactly two lines vary:

```
  6×  • Trane  on tenor_sax  ← John Coltrane (1.0), Johnny Hodges (0.4)
  2×  • Trane  on tenor_sax  ← Johnny Hodges (0.4), John Coltrane (1.0)
  5×  • Miles  on trumpet    ← Clark Terry (0.3), Miles Davis (1.0)
  3×  • Miles  on trumpet    ← Miles Davis (1.0), Clark Terry (0.3)
```

**Cause:** `pub influence_weights: HashMap<String, f32>` (`src/lib.rs:510`) — Rust's `HashMap` uses
`RandomState`, a per-process random SipHash seed, so iteration order differs every run.
`examples/jam.rs:105` iterates it directly to build the printed list.

### 3c · The dangerous hypothesis was checked and **refuted** — the science is safe

Before reporting this as a scientific defect I checked the one thing that would make it one: if
the example *digested* phrases by iterating the same `HashMap`, pattern insertion order into the
fixed-capacity, eviction-based `PatternVectorDB` would vary per process, and the surviving
pattern set could differ. It does not: `examples/jam.rs:119-123` digests with **explicit**
influence names in a fixed order:

```rust
for i in 0..8 {
    miles.digest_phrase(&miles_phrase(&format!("miles_{i}")), "Miles Davis");
    trane.digest_phrase(&coltrane_phrase(&format!("trane_{i}")), "John Coltrane");
    monk.digest_phrase(&monk_phrase(&format!("monk_{i}")), "Thelonious Monk");
}
```

And measured: across 30 runs, **every numeric value was identical** — `27.3 % own`, the
divergences `0.00 / 0.36 / 0.43`, the soul print strength `1.778`, the pattern counts.

**So: the science is deterministic; the printed narrative is not.** The fix is one line
(`BTreeMap`, or sort by weight before printing). Reported as a *promise* defect, not a science
defect — and the distinction is the whole value of the finding.

*(Minor: `src/dummy.wav` is committed at **0 bytes** — an empty artifact in the source tree.)*

### 3d · Why another agent should care

This is the fleet's most complete **emergence** experiment: a persona library digests influences,
a jam session scores harmony and surprise, reinforcement/penalty mutates patterns, and a *soul*
is defined as the fraction of the library the source material never contained. The mechanism is
the cell doctrine's feedback loop with an identity metric attached, and it is the only place in
the fleet where "it became itself" is defined as a **measurable ratio** rather than a metaphor.
`FLEET.md` already maps it onto `quilt`'s cell-feedback and aggregation model. With zero
dependencies it is also the easiest crate in the fleet to fork and instrument.

---

## 4 · `lau-*` — the positive control: six crates whose badges are exactly right

`lau-complex-agents` (113 tests), `lau-measure-agents` (134), `lau-geometric-deep-learning` (132),
`lau-geometric-measure` (112), `lau-information-geometry-agents` (118),
`lau-optimal-transport-agents` (75).

| crate | README claims | `#[test]` counted in source | match |
|---|---|---|---|
| lau-complex-agents | 113 tests | 113 | ✅ |
| lau-measure-agents | 134 tests | 134 | ✅ |
| lau-geometric-deep-learning | 132 tests | 132 | ✅ |
| lau-geometric-measure | 112 tests | 112 | ✅ |
| lau-information-geometry-agents | 118 tests | 118 | ✅ |
| lau-optimal-transport-agents | 75 tests | 75 (in `tests/integration_tests.rs`) | ✅ |

**Six for six, exact.** This is the fleet's standard for a test-count badge, and it is the
positive control against which the `holodeck-c` and `ropesight` findings should be read.

All six share a **byte-identical** `ci.yml` (`md5 93243ed4cd953a916973ccf5330b6fb3`):
`cargo check` → `cargo test` → `cargo clippy -- -D warnings`. The step-level conclusions from the
runs API (2026-07-12, the latest for all six):

```
lau-complex-agents:  cargo check ✓   cargo test ✓   cargo clippy -- -D warnings ✗
lau-measure-agents:  cargo check ✓   cargo test ✓   cargo clippy -- -D warnings ✗
```

**The maths passes; the lint is red.** These are the fleet's most rigorous crates — measure
theory, geometric measure theory, information geometry, complex analysis, Bronstein geometric
deep learning — implemented as the rigorous substrate for the cell doctrine, and **nobody has
run them**, because the badge is red and the red is only clippy pedantry.

*Honesty note:* I could **not** execute these locally — `crates.io` returns **403** from this
sandbox and all six depend on `nalgebra`/`serde`/`rand`. The pass evidence is CI's own step
conclusion, which is a server-side receipt, not my run.

*Scope note:* 63 distinct `lau-*` names appear across the 128 prior reports (a family-level sweep
is in the round-124 report). **These six are not among them** — each was checked by name and by
string search against the full corpus.

---

## 5 · `constraint-ranch` — a CI job named "Test" that runs no test

A gamified multi-agent puzzle farm (*"Breed. Train. Coordinate."*) with a real
`puzzles/__tests__/puzzles.test.ts` — 9 `it()` blocks covering puzzle counts, unique IDs,
per-type minimums, breeding-hint math, ID patterns, and cross-puzzle validation.

**The CI job is named `Test:` and contains no test step:**

```yaml
jobs:
  test:
    name: Test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - name: Type check
        run: npx tsc --noEmit
      - name: Lint
        run: npm run lint
```

No `npm test`. No `vitest`. **The suite has never executed in CI.** And `package.json` says:

```json
"scripts": { "test": "jest" },
"devDependencies": { …, "vitest": "^4.1.4" }
```

**`jest` is not a dependency.** The repo ships a `vitest.config.ts` and a vitest-style test file;
`npm test` invokes a framework that is not installed. The declared test command would fail even if
CI ran it.

**The same shape appears in two siblings in this round** — `opensmile-bridge/ci.yml` and
`rag-indexer/ci.yml` each contain a job named `test` with **0** test-command lines. 3 of 40
repos examined. (This is the fleet's "a job named Tests is not a test run" shape; the *repo-level*
instances of class (d)/(g) in previous rounds were about the *step*, not the *job*.)

CI: 4 failures, latest 2026-04-14. `Build` and `Deploy` are `skipped` behind it.

> **New class (bb) — a job named "Test" that runs no test.** The job *name* is not evidence of a
> test run; read the `run:` lines. Detector: for every workflow, for every job whose name matches
> `test|tests`, assert at least one `run:` line contains a test command.

---

## 6 · `CascadeRouter` — every CI step is `continue-on-error: true`

The current `.github/workflows/ci.yml` (after commit `f6ddb5c` *"ci: simplify, remove matrix/cache,
continue-on-error"*):

```yaml
      - run: npm install
      - run: npm run lint
        continue-on-error: true
      - run: npm test
        continue-on-error: true
      - run: npm run build
        continue-on-error: true
```

**The only step that can still fail the job is `npm install`.** The runs API agrees: the four
earlier failures all died at *Install dependencies*; the one green run (2026-05-26T18:56) shows
every step `success` — `lint`, `npm test` and `build` included, but only because their failures
are swallowed.

`npm test` is `vitest`; there are 5 spec files and **79 test calls** across them. `npm run build`
is `tsc`. The repo has a real suite that the CI cannot fail on.

The irony worth recording: **`release.yml` runs `npm test` and `npm run build` with *no*
`continue-on-error`**. The release path is stricter than the CI path — so a broken test would be
caught only at publish time, and `npm publish` is the step that actually matters.

> **New class (bc) — a green run that proves the step was reached, not that it passed.** Read
> `continue-on-error` on the step, not the run's conclusion.

---

## 7 · A fleet-wide template finding: the certification form is checked in **zero** repos

`DOCKSIDE-EXAM.md` is the fleet's standard certification checklist — 7 sections (Identity, Code
Quality, Testing, Fleet Integration, Documentation, Safety, Operational), scored 7/7 = Seaworthy.

Across the 44 repos examined this round, **17 carry the file. In 17 of 17, every checkbox is
empty** (0 `[x]`, with 21 or 59 `[ ]` depending on variant):

```
BLANK  CascadeRouter  agent-forge  ai-character-sdk  constraint-ranch  deployment-automator
BLANK  distributed-tracing  ec2mud  edge-relay-agent  fleet-agent-api  flux-decompiler
BLANK  flux-profiler  flux-skills  holodeck-c  inference-optimizer  rag-indexer
BLANK  voxel-logic  ws-status-indicator
```

**A certification checklist that is checked in zero repos is a template, not a gate — but it is
also the fleet's most useful untaken step.** `holodeck-c` is the sharpest case: its README says
`FLEET CERTIFIED` while its own exam form scores **0/7 = Needs Work** by its own rule.

> **New class (bd) — a template mistaken for a record.** The file's presence proves the fleet
> *wrote* a standard; it says nothing about whether any repo was ever examined against it.
> Detector: `grep -c '^\- \[x\]' DOCKSIDE-EXAM.md` — 0 across the board.

---

## 8 · Method notes (durable)

- **A repo can under-certify itself as loudly as it can over-certify.** `holodeck-c` passes 40/40
  and advertises 15/40. Always compile the *largest* candidate suite in a repo before reading its
  README's number; the biggest file is often the one nothing builds.
- **`grep` the Makefile, not the README, for what actually runs.** `src/conformance.c` was
  described in two documents and compiled by nothing.
- **Two suites in one repo are often complementary, not redundant.** The mutation table is the
  only way to see it: `make test` caught M3/M12 and missed M6/M9; the dead suite caught M6/M9 and
  missed M3/M12. **A repo can hold the answer and not use it.**
- **Re-run a receipt producer and diff the tip.** `ropesight`'s payloads were byte-identical and
  its tip moved, because a `wallMs` sat inside a hashed row.
- **Truncate a chain to N−1 rows and re-verify it.** A chain that verifies at any length has no
  anchor — and the anchor may already be sitting in a sibling file, uncompared.
- **A `HashMap` iteration in a "deterministic" demo is a promise defect; check whether it reaches
  the computation before calling it a science defect.** I checked `musician-soul` and it does not.
- **`continue-on-error: true` on a step means the run's conclusion is evidence of *reachability*,
  not of *passing*.** Look at the step list, not the badge.
- **A job's *name* is not a test run.** Read the `run:` lines.
- **Two independent implementations that agree beat one implementation that is trusted.** The
  `lau-*` crates' exact test counts are the yardstick this round's other findings are measured
  against — and the fact that a whole namespace of rigorous mathematics is red only on clippy is
  itself a finding: **the fleet's red badge hid a passing library.**

## 9 · Environment (durable, this wipe)

- **The MITM proxy leaf expired `Oct 21 23:48:43 GMT`.** Python `urllib` → `CERTIFICATE_VERIFY_FAILED`;
  `curl` without `-k` → `HTTP=000`; **`curl -sk` → 200.** The expired-leaf wall is *not* the
  cert-anchor wall: rebuilding the CA bundle does not help and does not hurt. **Use `curl -sk`.**
- **Rust installs to a clean `HOME` only.** With `HOME=/workspace/.home` (the NAS, 100 % full,
  `EDQUOT`) `rustup-init` installs the shims and then dies writing
  `/workspace/.home/.cargo/env`. Setting `HOME=/tmp/rawhome CARGO_HOME=/tmp/rawhome/.cargo
  RUSTUP_HOME=/tmp/rawhome/.rustup` installs cleanly (cargo 1.99.1, rustc 1.99.1).
  **A zero-dependency crate is then fully testable offline.**
- `crates.io` → **403** from this sandbox; crates with external dependencies cannot be built here.
  Use CI's own step conclusions for those, and say so.
- `node` 22, `gcc` 12.2, `python3` 3.11, `jq` present. `gh` absent — use `curl -sk` with
  `$GITHUB_TOKEN`. `actions/jobs/{id}/logs` still needs admin; `actions/runs` + `/jobs` do not.
- **`git clone --depth 1` is not enough for "never edited afterward" claims** — re-clone with full
  history to check a charter against its first commit.
- **`/workspace` is at 100 % (EDQUOT); every write goes to `/tmp` via shell heredoc.** The `write`
  tool cannot reach `/tmp`, and `/workspace` is full.
- **A partial clone (`--filter=blob:none --no-checkout`) leaves the index full of staged
  deletions.** `git reset` before committing, and `git add` **only** the new file — never `git add -A`.
