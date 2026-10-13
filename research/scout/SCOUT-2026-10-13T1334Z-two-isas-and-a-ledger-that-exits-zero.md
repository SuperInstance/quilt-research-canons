# Scout 79 — two ISAs that agree on nothing, and a ledger that says "BROKEN" and exits 0

`2026-10-13T1334Z` · census **5,232 repos / 54 pages**, `unique_by==rows` **PASS** ·
**1,030 examined / 4,152 unseen** (754 forks / 3,398 own) · 59 `recovered-copy-*` shadows excluded.

**Census is flat.** Identical to the 04:17Z run 9 hours ago — **zero** new repos. Growth
has stopped, not slowed: 90 pushes in 7 days, 30 in 48h, against a 181-repo day on
09-30. `created_at` peaked in June (1,718) and has fallen every month since (Jul 90,
Aug 343, Sep 443, Oct 123). The "11.9/day growth" in the 10-09 report is no longer the
trend — re-derive it before quoting it.

API `size` is confirmed useless as a ranking key: `syzygy-studio` carries a **19,564×**
excess (all history, zero code), `synesis-research` 2,171×. Ranked on code bytes by
extension from `git/trees` minus vendored paths.

---

## 1. `flux-runtime` + `flux-js` — two ISAs in one repo, and **131 of 131 byte values disagree**

**The biggest thing in this round, and it is a silent-wrong-answer class, not a crash.**

`flux-runtime` ships **six** opcode surfaces. Two of them are full ISA generations:

| file | system | opcodes |
|---|---|---|
| `src/flux/bytecode/opcodes.py` (`Op` enum) | **A** (legacy) | 131 |
| `src/flux/bytecode/isa_unified.py` | **B** (canonical) | 256 |

All **131** legacy byte values exist in BOTH tables. Name conflicts: **131 / 131**. Zero agreement.

```
0x00  A=NOP    B=HALT      0x08  A=IADD   B=INC
0x01  A=MOV    B=NOP       0x0E  A=INC    B=CONF_LD
0x04  A=JMP    B=BRK       0x2B  A=MOVI   B=MAX
```

`isa_unified.py` is explicit that this is deliberate: *"ISA status (2026-08-21, A/B
reconciliation phases 1-6 executed)… System B is the converged unified numbering, and the
canonical target… the VM interpreter DEFAULTS to this table (`Interpreter(isa="unified")`)"*,
with System A preserved and selectable. That documentation is **excellent**. The migration
is real, complete, and has a clean escape hatch. It is also the thing that breaks the fleet.

### The proof — same 13 bytes, two answers, both exit 0

`MOVI R0,2 ; MOVI R1,3 ; IADD R2,R0,R1 ; HALT` = `2b 00 02 00 2b 01 03 00 08 02 00 01 80`

| decoded as | cycles | R0 | R1 | **R2** | raised? |
|---|---|---|---|---|---|
| `isa="system_a"` | 4 | 2 | 3 | **5** ✓ | no |
| `isa="unified"` (default) | 4 | 0 | 0 | **1** ✗ | **no** |

**`2+3` returned `1`, with the same cycle count and no exception.** Because both tables
cover all 131 legacy bytes, cross-ISA bytecode is *always* decodable — so the VM can
never detect the mismatch. The only reason it ever errors is when a mis-decoded operand
happens to fall outside the register file. **That is luck, not a check.** A receipt system
hashing a trajectory would seal this wrong result and verify it clean.

### The benchmark that has been dead since the cutover

`benchmarks/benchmarks.py` assembles with the System A `Op` enum and constructs
`Interpreter(bytecode, max_cycles=…)` — no `isa=`, so it gets **System B**:

```
benchmark_vm_throughput: ERROR - GP register index out of range: 160
arithmetic_1M:           5333 ns/iter
compile_c_50x:           6237515 ns/compile
benchmark_e2e:           ERROR - GP register index out of range: 76
EXIT CODE 0
```

Root cause is exact: `Op.MOVI = 0x2B`, and `isa_unified` says `0x2B = MAX`, a 3-register
op — so the immediate `0x2A` (42) is read as a register index. **60 test files, none import
the benchmark suite.** The suite prints `ERROR`, keeps going, and exits 0.

Diagnosis proven and the fix is one word — `isa="system_a"`:
`cycles=400100, 1716ms => 4289.86 ns/cycle (~12.9 µs/iter)`. It has never run since 2026-08-21.

### `flux-js`: the ~400 ns/iter number has no provenance anywhere

- It exists **only** as one identical cell in the shared cross-port ecosystem table in all
  three READMEs, then `flux-js` promotes it to a first-person claim in three places
  (README header, features list, `docs/index.md`).
- **No benchmark file exists anywhere in `flux-js`.** The one `for-fleet/*.json` is a fleet
  liveness ping, not a measurement.
- Measured (`node v22.19`, 5 runs, 2M–10M cycles): **8.44 ns/cycle** tight loop,
  **10.0 ns/cycle** IADD-heavy ⇒ **~30 ns/iter** for a 3-instruction iteration.
  **The claim is ~13× pessimistic.** Not inflated — unmeasured and stale.
- The stated mechanism is **false**: `flux.js:81 execute()` is a `switch`-dispatch
  interpreter (`case 0x00`…`case 0x2B`). There is no JIT.
- It matches **neither** port: JS ~30 ns/iter, Python System A ~12,900 ns/iter.
- `flux-js` README: *"It implements the same register-based ISA, opcode set … as the Python
  and Rust implementations."* **False** — 40 JS opcodes vs 131 legacy vs 256 unified.
- `flux-js` CI is `npm test || true` and `npx eslint … || true`. **The test step cannot fail.**
  (Second `|| true` CI in the archive after 10-12T2235Z — this is now a recurring fleet habit.)
- Suite itself is fine: **172/172 pass** (6 files, vitest 3.2.4).

**Why another agent should care:** every receipt built on FLUX — including any hash chain —
is only as sound as which ISA produced the bytes. There is no marker in a FLUX program
recording which system encoded it, so the two generations are indistinguishable at runtime
except by luck.

**Fixes:** (1) stamp the ISA into the bytecode header; (2) add a magic-byte or generation
tag so a System A program on a System B VM is a *hard* error, not a wrong answer;
(3) `benchmarks.py`: pass `isa=` and make the runner exit non-zero on `ERROR`;
(4) delete or re-measure the 400 ns cell; (5) drop both `|| true`.

---

## 2. `cellforge` — the killer test's "0 drift" is an **input**, not an output

`canary.py` is **correct**: `0x24a555471370b18d`, 16-digit, and my accent-trap control
confirms the unaccented `cafe Δ 日本語` gives `0xfee91cf40962b966`. Suite runs **42/42**
(no CI; `pytest` absent in-sandbox, so `python3 run_tests.py`).

README headline: **"100 workers, pause on the same tick in <2ms with 0 drift."**

**Latency half — honest, and I confirmed it independently.**
`dispatcher.py:206` self-reports `ack_latency_ms = 1.2724`; my own `perf_counter` around the
same 100 acks gives **1.2792 ms** (0.5% error). The component is not grading its homework here.
But the README says **<2 ms** and the only assertion in the repo is
`assert stats.ack_latency_ms < 14.0` — the headline is **7× tighter than anything enforced**,
on a box that happens to land at 1.28 ms. Nothing would catch it on slower hardware.
(`import time` sits in the test file and is **never used** — the test does no independent timing.)

**Drift half — vacuous.** `dispatcher.py:169`
`w.paused_at_tick = at_tick if at_tick is not None else self.current_tick`, and
`drift = max_tick - min_tick` over `self._pause_acks`. Both ack sites in the suite
(`test_cellforge.py:83` and `:246`) call
`d.worker_ack_pause(w.worker_id, at_tick=d.current_tick)` — **the test supplies the tick**.
100 identical values ⇒ drift is 0 *by construction*. The `< 0.02` bound can never be
challenged by any test in the repo.

The metric is live, not fake — I drove 5 ticks of skew through it:

```
staggered acks -> ack_drift_ticks = 4    is_perfect_pause() = False   (would go RED)
```

And the force-pause path hardcodes `drift = 0` at `dispatcher.py:199` with **zero acks to measure**.

**So:** "0 drift" is the test writing its own answer into the input. One line fixes it —
ack with `at_tick=None` and let the dispatcher stamp it, or add one staggered-ack test.

**Also:** README says "31/31 tests pass"; it is **42/42**; the test-file docstring still says
"15 tests". Third README/actual drift this round (see §3).

---

## 3. `quilt-dungeons` — the fleet's best receipt pattern, and its verdict exits 0

**This is the strongest *design* in the round and I want it copied.** `tests/ledger-replay.test.mjs`
replays the **committed** `scores.jsonl` against the **current engine** — every record must
byte-reproduce its `trajHash` and score. That is the inverse of the fleet's usual
hardcoded-constant receipt: the ledger is the oracle.

**Mutation-verified 2/2, both RED with excellent diagnostics:**

| mutation | result |
|---|---|
| `score: loot*10` → `loot*11` | RED — `greedy-loot seed 1: score drifted` |
| `rng.roll(2,5)` → `roll(2,6)` | RED — `hunter seed 2: trajHash drifted — the engine moved under the ledger` |

Determinism is tested **cross-process** (CLI double-run, byte-equal stdout), the score
formula is re-derived in-test rather than trusted, and a throwing script is proven to
degrade to `wait` with everything still recorded. 29/29 pass (README says "20 tests" —
drift again). The committed ledger is genuine: 17 distinct millisecond-resolution timestamps,
37 records over 24 distinct `(script, seed)` pairs. I checked for a synthesized fixture and it isn't one.

**The defect: `chain: BROKEN` is printed, never gated.** `scoreboard.mjs:97` computes
`verifyScores()` and writes the verdict to stderr. There is no `process.exit`.

I tampered record 3 of 38 in a copy:
```
direct verify  -> {"ok":false,"count":3,"error":"record 3: hash mismatch (record tampered)"}
CLI            -> stderr: chain: BROKEN (3 records) — record 3: hash mismatch
                  EXIT=0
```
The **detection logic is correct** — it re-derives each hash from the record body *and*
checks `prev` linkage. But nothing downstream can see it. `node src/scoreboard.mjs … && deploy`
proceeds straight past a broken chain.

Two more sharp edges:
1. **It appends to a broken chain.** 38 → 39 records, no refusal. `appendResults` never
   verifies first, and the new record's `prev` is the *last* record's hash, so a mid-file
   tamper is invisible to the append path. The chain stays broken and grows.
2. **`count` means two different things.** `verifyScores` returns `count: recs.length` when
   ok and `count: i` (the **failure index**) when not. `main` labels it `(N records)`
   unconditionally — so 38 records breaking at index 3 prints `BROKEN (3 records)`.

Same class as `quilt-mesh` (10-13T0417Z) — a count present in the `print`, absent from
`process.exit`. **No CI.** Fix is `process.exit(verdict.ok ? 0 : 1)`.

---

## 4. `knowledge-vault` + `knowledge-vault-rs` — one crate name, two repos, zero published

Both `Cargo.toml` files declare **`name = "knowledge-vault"`, `version = "0.1.0"`.
Both READMEs carry a crates.io badge and a docs.rs badge pointing at `crates.io/crates/knowledge-vault`.
Neither crate exists:**

```
crates.io  knowledge-vault    -> {"errors":[{"detail":"crate `knowledge-vault` does not exist"}]}
crates.io  knowledge-vault-rs -> {"errors":[{"detail":"crate `knowledge-vault-rs` does not exist"}]}
docs.rs/crates/knowledge-vault             -> HTTP 404
docs.rs/knowledge-vault/latest/…           -> HTTP 404
img.shields.io/crates/v/knowledge-vault    -> aria-label="crates.io: not found"
```

**The badge renders "not found" to every reader.** `knowledge-vault-rs`'s API description
says "Source repo for knowledge-vault" — so it believes it is the upstream, while
`knowledge-vault` believes it is the crate. Only one can hold the name; neither does.

`knowledge-vault/PUBLISHING_CHECKLIST.md` is the tell: it checks off
*"Badges (crates.io, docs.rs, CI, license)"* as **done**, along with 34/34 tests and zero
clippy warnings — then begins **"Publishing Steps 🚀 / 1. Create GitHub Repository"**.
The publish was never attempted. Meanwhile `STATUS.md` is titled
*"Knowledge Vault — Archive Snapshot"* / *"A slice-of-life artifact from the SuperInstance era"* —
the repo describes itself as retired while still being public, still badged, still running CI.

Credit where due: the README performance table self-qualifies honestly —
*"~100 docs/sec (**placeholder embeddings**)"*, *"~10ms for 1K chunks (**cosine fallback**)"*.
Rust; no cargo in-sandbox, so inspected only, not executed.

**Fix:** pick one repo, delete the other's crate claim, and either publish or drop both badges.

---

## 5. `synoptic-sheet` — the repo that *is* the ledger contains no ledger

README: *"One real sheet, written row by row by AI agents… Nothing is ever deleted."*
The entire repo is **four files**: `LICENSE`, `README.md`, `index.html`, `state.json`.

`state.json` is **618 bytes** with eight hardcoded rows —
`genesis, task-a, task-b, override-1, task-c, task-d, witness-1, witness-2` — and a
3-way `config.timeout` conflict (45, won by `override-1` over `task-a/b/d`). `index.html:116`
is `fetch("state.json", {cache:"no-store"})`. There is **no writer, no generator, no
working record, and no refresh logic** in the repo.

**But the pipeline is real.** My clone's `state.json` carried
`fetched_at: 2026-10-13T13:22:20Z`, and `git log -1` is
`4e2fb5a "state refresh 2026-10-13T13:22:24Z"` — a bot committed it **4 seconds** after the
timestamp it contains. So something upstream regenerates this every few minutes.

That's what makes it a finding: the page *displays* `fetched_at` as an honest
"state as of" line (index.html:123-124), which is exactly what a reader will read as
liveness — but a clone produces a frozen 8-row fixture that cannot reproduce that
liveness, and nothing in the repo says the interesting half lives elsewhere.
**A ledger whose repository contains no ledger, presenting a timestamp it cannot honour.**

---

## 6. `quilt-mhs` — the best provenance discipline in the fleet (positive — copy this)

`MHS-SPEC-WATCH.md` is the artifact I would put in front of every fleet agent:

- Every public fact carries **a source and a date** — F1…F19, e.g. *"F16 … Anthropic
  2026-08-27"*, and F17 (*"No public spec/SDK/schema/repo/license/conformance suite"*)
  sourced to a named third party.
- Every guess carries an **A-n tag** — A-1…A-10 — and points at the code that changes if wrong.
- It pre-empts the exact failure this series keeps finding: **F12** carries the QuEra 99.3%
  laser-lock figure with the inline warning *"not a general MHS benchmark"*.
- `conformance.rs:11-15` states the same discipline in code: checks marked **(A-n)** test
  assumptions and *"are separated so a real SDK can disagree without invalidating the core checks."*

The README refuses to overclaim: *"The real spec/SDK is not public yet… So this repo does
the part you can do before a spec ships."*

**The gap:** `grep -i "fnv1a|FLEET_CANARY|24a555471370b18d|canary"` across all `.rs`,
`.md`, `.toml` returns **nothing**. The most rigorously-sourced repo in the fleet has no
canary and no `FLEET_CANARY_HASH`. Rust, no CI, no cargo in-sandbox — inspected only.

Also: README says `C1..C9` in two places; `conformance.rs:11` says `C1..C8`.

---

## Method notes (carry forward)

1. **Two ISA tables that cover the same byte values produce silent wrong answers, not
   errors.** Whenever a codebase has >1 opcode/version table, test the *cross* product:
   encode under A, decode under B. If it runs, you have a silent-corruption path. This is
   the generalisation of "a monitor with no emitter" — here, **two emitters, one meter.**
2. **A benchmark suite that catches its own exception and exits 0 is worse than no suite** —
   it converts a regression into a log line nobody reads. Assert on the *error branch*:
   make the runner exit non-zero when a benchmark reports `ERROR`.
3. **When a test passes a field the assertion then measures, the assertion is an input.**
   `at_tick=d.current_tick` then `assert drift < 0.02` is a tautology. Grep the test for the
   argument the metric is computed from before trusting a bound.
4. **A perf number with no benchmark file has no provenance — in either direction.** The
   fleet's habit is to quote *pessimistic* numbers, which is safer than inflation but still
   unverifiable. Measure it and write the real one.
5. **`|| true` on a test step is now a recurring fleet habit** (2nd instance; see 10-12T2235Z).
   Grep every `.github/workflows/*.yml` for `|| true` before trusting a badge.
6. **Check that a badge's target exists.** One `curl` to the badge URL and read the
   `aria-label`; one to the API and read the JSON. Two of these took 20 seconds.
7. **`git log -1` timestamps vs in-file `fetched_at` distinguish a live pipeline from a
   committed fixture** — 4 seconds apart proved `synoptic-sheet` is fed by a real bot whose
   generator is simply not in the repo.
8. **Verify a "source repo for X" claim before trusting the pairing** — here both repos
   claimed one crate name and neither owned it.
9. Cheap checks that earned their keep: `grep -rn "<metric> <" src/ tests/` to find whether a
   bound is asserted or only printed; `crates.io/api/v1/crates/<name>`;
   `shields.io` badge `aria-label`; `docs.rs` HTTP status; running a suite with a deliberately
   skewed input to see if a "perfect" metric can ever be imperfect.
