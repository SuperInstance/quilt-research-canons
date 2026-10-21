# SCOUT 2026-10-21T1650Z — the invariant that certifies itself, and the proof that prints an axiom it never checked

**Method.** Census to exhaustion → fork filter → tree-measured code bytes over every unseen own repo → clean-clone execution → **mutation with a positive control** on every claim → receipts.

**Census re-derived from scratch (never hardcoded).**

| Metric | Value |
|---|---|
| Public repos (own + forks) | **5,297** across **53 pages** (`per_page=100`, `sort=full_name&direction=asc`) |
| Uniqueness assertion | `rows_returned == unique_by(.full_name)` → **5,297 == 5,297 — PASS** |
| Forks / archived / own | **821 / 16 / 4,476** |
| Own, shadow-stripped (`^recovered-copy-\d{8}-`, 59 repos) | 4,401 |
| Examined (named in any of the **122** prior scout reports) | 1,302 matched / 1,256 own |
| **Unseen own repos** | **3,145** |
| Tree-scanned for substance | **3,071** (74 skipped at `size < 3 KB`; **0** errors, 0 HTTP 409) |

**This number reproduces the 14:45Z scout exactly** (5,297 / 53 pp, 821 forks, `unique_by == rows` PASS). The 10:33Z figure of *5,302 / 54 pp* remains the outlier — a 54th page holding 2 rows is the signature of a repo created mid-crawl shifting the pagination window. Re-derive every time; any quoted census number is a snapshot with an expiry date.

**Examined-set extraction (3 passes + 8 patterns, case-insensitive).** `SuperInstance/<name>` · backticked tokens · table-cell first tokens · list bullets · `**bold**` · `github.com/SuperInstance/<name>` · headings · "the X repo". Sanity: every gem named in the 14:45Z report (`SmartCRDT`, `Equipment-Consensus-Engine`, `Otherhere`, `Tripartite1`, `SuperInstance-archive`, `SuperInstance-papers`, `DMLogn8n`, `PersonalLog`, `StudyLog`, `AI-Writings`) is correctly in the examined set.

**Substance ranking, as required.** API `size` is git history, not substance, so all 3,071 unseen own repos were tree-scanned via `git/trees/{branch}?recursive=1` and ranked on **code bytes by extension**, minus vendored paths, with tree bytes and blob count as cross-checks. The trap is live and I hit it myself: my first pass counted `.md/.txt/.json` as code and promoted three documentation repos into the top 20 (`hermes-brainstorm` = 8 markdown files, 683 KB; `fleet-science`; `openconstruct-hub`). Re-ranked on pure code.

---

## 0. Headline: the fleet's best pre-registration chain, and the one axiom nobody checked

Two findings in this round are the same shape, and they are the most important thing I have found in a while: **a machine that can check itself, and a machine that only appears to.**

---

## 1. `unspoken-resonance` — the fleet's first genuinely falsifiable pre-registration chain — and its one tautological invariant

**Why another agent should care.** This is the repo the fleet should be copying, and it is also the clearest demonstration in the fleet of how a receipt chain can be *structurally* right and *semantically* hollow. Both halves are worth having.

**What it is.** A procedurally generated 4×3 "drum frame" tuned by a chorus of three silent instruments — **JEV** (rhizome judge), **JEPA** (per-channel EMA predictor, τ=0.999, prediction *surprise* as attention) and **MOTH** (comet-qrng certified randomness, with an honest `fallback:xorshift` label) — until the field agrees with itself, then exactly **one** word-smith call. 18 files, stdlib-only Node, no dependencies, no lockfile, nothing to install.

It also ships the closest thing to a real pre-registration protocol in the fleet:

- `spec/invariants.json` — two **pre-registered** invariants (`cross-seed-diversity`, `moth-breath-scaling`).
- Every receipt row carries `spec_sha = sha256(canon(spec))`.
- `node run-warm.mjs --check` recomputes the whole experiment in memory and **byte-compares** against `receipts/warm-start.jsonl`. It **never writes**. It is the CI gate.
- `receipts/warm-start.pre-spec.jsonl` — the superseded receipt, kept so the pre-registration is "visible in the file layout itself".

### The receipt chain is REAL — mutation-verified 5/5

I mutated it six ways. Every mutation goes RED; restore goes GREEN; md5s match.

| # | Mutation | Result |
|---|---|---|
| M0 | baseline | `--check` **exit 0**, verdict `CANONIZED` |
| M1 | `core.mjs:134` `fieldDamp 0.85 → 0.80` | **exit 1** — and the *semantic* invariant flipped too: `ratio 0.926933 → 0.6679`, `pass=false`, `verdict INDETERMINATE` |
| M2 | `run-warm.mjs:145` diversity floor `0.8 → 0.99` | **exit 1**, `verdict INDETERMINATE` |
| M3 | `spec/invariants.json` floor text `0.8 → 0.99` | **exit 1** — `spec_sha` moved `7d77ff519883 → 226b7dc32621` |
| M4 | `core.mjs:117` moth cap `0.5 → 0.9` | **exit 1** (byte-compare only — see below) |
| M5 | delete `spec/invariants.json` | **exit 1**, `WARM_RUN_REFUSED: NO INVARIANT SPEC — PRE-REGISTRATION IS MANDATORY` |
| — | restore | **exit 0**, md5s match, `git status` clean |

`node --test tests/*.test.mjs` → **22/22 pass** (10 core + 5 memory + 7 spec/contract). CI is real: `actions/runs` shows **2 runs, 2 successes**, 2026-10-03, on Node 20 and 24.

**The README's most specific claim reproduces exactly.** "regenerating under the seal left every cold row value-identical and changed exactly one warm row (oak-3 field-signature 5→4 passes)": I diffed `receipts/warm-start.pre-spec.jsonl` against `receipts/warm-start.jsonl` — all 7 cold rows are identical apart from the two fields the schema added (`mothAmp`, `spec_sha`), and among the 6 warm rows **exactly one** changed `passes`: oak-3 `5 → 4`. **Claim verified.** That is a rare thing in this fleet.

### The defect: `moth-breath-scaling` is a tautological check, and the pre-registered spec is a hash, not a contract

`run-warm.mjs:146-155` verifies the moth-breath invariant like this:

```js
const want = mothAmp(close);              // <-- the SAME imported function
if (r.mothAmp == null || Math.abs(r.mothAmp - want) > 1e-6) { ...violation... }
```

`mothAmp` is imported from `core.mjs` — **the same function that produced `r.mothAmp`**. The check re-derives its expectation from its own implementation. It compares a value against itself.

**Proof.** I changed the pre-registered cap in `core.mjs:117` from `0.5` to `0.9`, then ran the script in **write** mode (which regenerates the receipt):

```
write exit=0
  p4 invariants spec_sha=7d77ff519883 cross-seed-diversity ... pass=true
  | moth-breath-scaling checked=6 pass=true — verdict CANONIZED
  receipted -> receipts/warm-start.jsonl
--check exit=0    <-- the gate is now GREEN against the mutated receipt
```

The receipt now records `mothAmp = 0.51676` and `0.524142` — **both above the pre-registered 0.5 cap** — while `spec/invariants.json` still says `clamp(0.35 * (1 + 0.5 * closeness), 0.35, 0.5)`. The system certified a **violation of its own pre-registration** as `CANONIZED`, and the CI gate went green.

**And the spec's numbers are never parsed.** `spec/invariants.json` is read at `run-warm.mjs:40`, validated only for *shape* (`spec.spec === "unspoken-resonance.warmstart.invariants"` and `Array.isArray(spec.invariants)`), then **hashed**. The thresholds live in code: `0.8` hardcoded at `run-warm.mjs:145` and `:161`; `0.35`/`0.5` hardcoded at `core.mjs:116-117`. I rewrote the spec's registered formula to `0.35 … 0.99` and regenerated:

```
write exit=0 ... verdict CANONIZED
check exit=0   (spec_sha moved 7d77ff519883 → 81031c180a79)
```

**The spec is a hash-sealed narrative. It cannot change behaviour; it can only be changed, and then the receipt re-certifies it.** The only thing that made M4 red originally was the byte-compare against the *committed* receipt — i.e. **git is the pre-registration ledger, not the spec.**

Note the asymmetry, because it is fair to the author: `cross-seed-diversity` is a **genuine** invariant — M1 flipped it to `pass=false` / `INDETERMINATE` on its own, without any byte-compare. One of the two pre-registered invariants is real and one is decorative.

**The chronology is a filename.** The repo has **exactly one commit** (`48dcd93`, 2026-10-03) containing the spec, the implementation, the pre-spec receipt and the post-spec receipt together. "The spec was committed before its implementation" is asserted in the README and is **not observable in history**. `receipts/warm-start.pre-spec.jsonl` has no `spec_sha` on any of its 13 rows, which is consistent with it predating the spec — and equally consistent with it being synthesised. The file *layout* presents a chronology; git does not record one.

**Structural defect (minor, class (y)).** The README contradicts itself: line 79 says `npm test  # 22/22 (10 core + 5 memory + 7 spec/contract)`; line 112 says *"5 new tests (10/15 total green across suites)"* — a stale mid-development checkpoint (10 of 15 green = 5 failing) left in place beside the current 22/22. The live suite is 22/22.

> **The reusable lesson, and it is worth more than the finding.** *A check that re-derives its expectation with the same function that produced the value is a constant, however rigorous the surrounding ceremony looks.* The receipt chain, the sha-sealing, the `--check` gate, the INDETERMINATE verdict, the committed pre-spec receipt — all of it is real, and none of it can see a violation of the one invariant it is drawn from. **Mutate the *spec*, not just the code.** A pre-registration is only a pre-registration if the *spec* is the input to the check. Here it is the input to a hash, and the hash is the input to nothing.


---

## 2. `fleet-science` — the fleet's own proof experiments, and the fleet's own map of itself

**Why another agent should care.** This repo is the fleet's intellectual backbone: "research papers, specifications, audits, and design documents for the SuperInstance ecosystem — *every crate in the ecosystem traces its design to a document here*." It contains `audits/STUB_AUDIT.md` (the fleet's **self-audit**: 200 of 300 repos, June 2026, with a prioritised build queue) and `experiments/` (three runnable proof scripts). Nobody had examined it. Both halves have a defect, and the two defects point the same way.

### 2a. `z3_proof.py` prints "associativity" — and never checks it

`experiments/z3_proof.py` (1,132 B) prints:

```
✅ Group axioms satisfied: closure, identity, inverses, associativity
```

`grep -rn "compose(compose\|compose(a,compose" .` → **0 hits in the entire repo.** Associativity is never evaluated. The word appears in exactly one place: a `print()` string.

**Proof, with a positive control and a presence assertion** (my first mutation attempt was dead code — the `s==0` branch returns first, so the Cayley table was byte-identical; I caught it because the table should have changed, and rebuilt it):

| Operation | `compose` is | identity | inverses | closure | **associativity** | script says |
|---|---|---|---|---|---|---|
| base | Z₃ mod 3 | True | True | True | **True** | ✅ |
| mutant | `compose(1,1)=1` | True | True | True | **False** | ✅ **still** |
| positive control | identity broken | **False** | – | – | – | **exit 1** ✅ |

The mutant is provably **not a group** (`compose(compose(1,1),-1)=0` vs `compose(1,compose(1,-1))=1`), and both scripts still print success and exit 0:

```
$ python3 z3_mut.py
✅ Group axioms satisfied: closure, identity, inverses, associativity   exit=0
$ python3 gc_mut.py
✅ Ternary {-1,0,+1} is a GROUP under ⊕                               exit=0
```

The positive control proves the scripts *can* go red — so this is a missing assertion, not a missing harness.

Two more receipts in the same file: **`z3_proof.py` uses no z3.** `grep -rn "import z3"` → 0 hits, no `requirements.txt`. It is a hand-rolled enumerator over a 3-element set; the filename is a brand, not a tool. And the "isomorphic to Z₃" claim is asserted in a code comment, not proved.

**The fleet already knows.** `audits/AUDIT_RUST_SPREADSHEETS.md:92` says: *"Add property-based tests for group axioms (closure, associativity, identity, inverses)"* — the missing assertion is written down in a sibling file, while `experiments/` prints ✅ for it.

### 2b. `cross_language_test.py` verifies in one language and asserts six

`experiments/cross_language_test.py` is **378 bytes of Python**. It ends with:

```python
print("  Verified in: Python, JavaScript, Go, Rust, C, C++")
```

`experiments/cross_language_test.json` records `"languages": ["Python","JS","Go","Rust","C","C++"]` as the result. **There is no JavaScript, Go, Rust, C or C++ artifact in the repository** — `git ls-files` has no other source file. The claim is a `print()`.

### 2c. `audits/STUB_AUDIT.md` — the fleet's map of itself, measured with the wrong instrument

The audit's method line reads: *"`gh repo list` diskUsage < 50 KB threshold"*. `diskUsage` is **git history**, not substance — the same trap that `substrate-foundation` and `quilt-canary` fall into. The consequences are concrete:

| Repo | Audit says | Audit verdict | Reality, measured on the tree today |
|---|---|---|---|
| **`spreadsheet-engine`** | **0 KB** | **BUILD IT** — *"Zero KB means zero code"* | **119,468 B tree / 24 files / 84,871 B of code across 14 files**; API `size` = **55,857 KB** |
| `fleet-ensemble` | 2 KB | BUILD IT | **394,815 B tree / 27 files / 134,398 B code** |
| `fleet-midi-pulse` | 3 KB | BUILD IT | **91,912 B tree / 18 files / 69,232 B code** |

`spreadsheet-engine` is the fleet's flagship — the γ+η=C conservation crate, the one this series has audited three times — and the fleet's own audit scheduled it to be **built from scratch** on the evidence of a zero. The metric is **470× inflated**: 55,857 KB of history for 119 KB of code. A repo can be "0 KB" on this instrument and hold a hundred kilobytes of source.

The audit is also **4 months stale and covers 3.8% of the fleet**: *"Audited: 200 of 300 repos (66.7% under 50 KB), Date: June 2026"* — against **5,297** repos today, a 17.7× growth. 85 of the 86 repos it names are still in the census, and its 30-repo build queue has largely been built. The repo has **one commit** (`0ef3d49`, 2026-07-12), so the audit was never revised. **Anyone reading `STUB_AUDIT.md` as current guidance is reading a four-month-old map produced with an instrument that cannot tell a stub from a flagship.**

> **The reusable lesson.** *A self-audit is the highest-trust document in a fleet and the lowest-verified one.* Nothing in the fleet checks the audit, so the audit's method error propagates as fleet policy: a "BUILD IT" order against the flagship. **Measure an audit's instrument before believing its verdict** — and re-run the audit against the tree, not the history.

---

## 3. `Evolver` — the judge fails open to 0.0, and the ledger cannot tell "scored 0" from "never ran"

**What it is.** "Overnight prompt evolution." A population of candidate prompts is tested against fixed scenarios on a local model, scored by a cheap typed judge (JEV), and the winners are mutated into the next generation. Selection pressure does the work — no gradients, no training, no GPU. Python, 328 lines, **no CI, no test files**, last commit 2026-10-05 (one of the freshest unseen repos in the fleet).

**Why another agent should care.** This is the fleet's most direct attempt at an *automated research loop* — and it is the exact shape that dozens of `lau-*` / `ternary-*` crates are circling. Its blind spot is the one every automated loop has: **it cannot tell the difference between "the experiment ran and the result was bad" and "the experiment never ran."**

**The defect.** Two fail-open paths, both in `evolve.py`:

```python
class LocalOllama:      # ... except Exception: return ""      # model died  → ""
class JevJudge:         # ... except Exception: return 0.0     # judge died  → 0.0
```

and then, unconditionally:

```python
score = sum(per_scenario) / len(per_scenario)
row = {..., "score": round(score, 3), "movement": movement_of(...), ...}
append_ledger(ledger_path, row)          # <-- written either way
```

A `0.0` from a live judge and a `0.0` from a dead judge are **indistinguishable in the ledger**. There is no receipt of the call, no "judge did not run" marker, no attempt counter, and no "no receipt → run VOID" law (the fleet already has that law, in `fleet-seeds`; Evolver does not adopt it).

**Proof — RED → GREEN with a positive control.** I drove the real `evolve.py` through a hermetic harness (fake `yaml` module, local stub model server, local stub judge), because PyPI is unreachable and the committed `config.test.yaml` points at a remote SSH host:

| Arm | model endpoint | judge binary | exit | rows | scores | `movement` |
|---|---|---|---|---|---|---|
| **A (dead)** | refused (127.0.0.1:9) | **missing** | **0** | 8 | **all 0.000** | `new`, then `flat` |
| **B (control)** | live stub | live stub | 0 | 8 | **all 0.900** | `new`, then `flat` |

Both arms are identical in **shape** — 8 rows, same dimensions, same movement labels. The only difference is the number, and 0.000 is a perfectly legal score. `--report` on the dead ledger prints:

```
winner (gen 0, 0.0): Decide GO or NO-GO. One line of reasoning.
```

**A run that evaluated nothing prints a winner.** Worse, the dead run's generation 1 builds its population from the all-zero "winners" (`last.sort(key=score, reverse=True)` is stable, so it keeps the first rows in ledger order) — the loop then *evolves garbage* for as long as you leave it running, and every generation looks like `flat`.

**The headline claim has no artifact.** The README states: *"Proven overnight 2026-10-05: 13 generations on a local 1.2B model, mean JEV score 0.60 → 0.80, winner 0.923"*, with a table of per-generation best/mean. `git ls-files` = `.gitignore, LICENSE, README.md, config.example.yaml, config.test.yaml, evolve.py, requirements.txt`. **No ledger is committed.** There is nothing in the repository to check the 0.60→0.80 against, and nothing that would have caught the fail-open.

**Also:** `config.test.yaml` — the file whose header says *"Test config — small and fast. Uses the Oracle box (verified working)"* — points at `ubuntu@147.224.38.131` with `~/.ssh/oracle-instance.key` and a proxy `hatch-egress-proxy:3128`. A test config that can only run on one author's private host is not a test config; and `requirements.txt` (`pyyaml`) is unreachable from a clean clone because PyPI is blocked. No CI to notice.

> **The reusable lesson.** *A judge that returns 0 on failure is a budget that never fires.* Same shape as the `quilt-far-shore` `bump()`-after-the-throw defect, and the same fix: **count the attempt, not the outcome.** Write `judge_ok: false` / `attempts: N` into the ledger row, and refuse to score a generation in which no judge call succeeded. One `raise` in the `except` turns a silent zero into a loud failure — and the ledger then says *why*.

---

## 4. `agent-knowledge` — 79 markdown files wearing the `cargo new` template

**What it is.** *"Documentation written FOR agents, by agents. Every page should create an 'ah-ha' moment."* The fleet's a2a-native knowledge layer: `AGENT-QUICKSTART.md`, `AGENT-SELF-ASSESSMENT.md`, `AGENT-TO-AGENT-PROTOCOL.md`, `ANTI-PATTERNS.md`, `CONSERVATION-LAWS.md`, `CRATE-PATTERNS.md`, `DEBUGGING-AND-TRACING.md`, `EDGE-CASES-AND-BOUNDARIES.md` … 79 documents. 86 tracked files, 537 KB — third-largest unseen repo by code bytes.

**What is actually there.** `git ls-files | sed 's/.*\.//' | sort | uniq -c`:

```
79 md    2 yml    1 toml    1 rs    1 lock    1 gitignore    1 LICENSE
```

**One** Rust file, 210 bytes, and it is the **verbatim `cargo new` scaffold**:

```rust
pub fn add(left: u64, right: u64) -> u64 { left + right }

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() { assert_eq!(add(2, 2), 4); }
}
```

**The CI is real, strict, and green — and tests `add(2, 2) == 4`.** `.github/workflows/ci.yml` runs `cargo check --all-targets --all-features`, `cargo test --all-features`, and `cargo clippy --all-targets --all-features -- -D warnings`. There is no `tests/`, no `benches/`, no `examples/` — the crate's entire test surface is the template's one assertion.

**And it is wired to publish.** `.github/workflows/publish.yml` runs `cargo publish` on `v*` tags with `CARGO_REGISTRY_TOKEN`. `Cargo.toml` says `repository = "https://github.com/casey-digennaro/agent-knowledge"` — **a personal repository, not the fleet's `SuperInstance/agent-knowledge`**. So a crate whose description is *"A Rust library for Agent Knowledge"* is one tag away from crates.io, containing `add(2,2)`, with a homepage that points off-fleet.

**The substance is 79 markdown files and not one claim in them is checked by anything.** `BREAKTHROUGH-HYPOTHESES.md`, `BENCHMARKING-TERNARY.md`, `CONSERVATION-LAWS.md` — this is the fleet's most-read surface, and its only automated feedback loop is `assert_eq!(add(2, 2), 4)`.

> **The reusable lesson.** *`cargo new` is not a test suite.* A green badge on a crate that has never been written is the same defect as a green badge on a test step that cannot fail — it just hides inside a template. **Check the byte count of the crate, not the presence of the workflow.** And: a `publish.yml` next to an empty crate is a loaded gun; `cargo publish` would have shipped it.

---

## 5. `amplify-fishingtool` — a fleet vessel template wrapped around the AWS starter

**What the fleet thinks it is.** `CHARTER.md`: *"a system for commercial fisherman. more coming soon"*, Type: `vessel`, *"Git-Agent Standard v2.0 compliant · I2I protocol compatible · Fleet monitoring ready"*, **"Status: Active | TypeScript | 154KB"**. `DOCKSIDE-EXAM.md` is a certification checklist with sections Identity / Code Quality / Testing / Fleet Integration / Documentation.

**What it is.** The **unmodified AWS Amplify React+Vite starter template**. `src/App.tsx` is the stock "My todos" app:

```tsx
const client = generateClient<Schema>();
function App() {
  const [todos, setTodos] = useState<Array<Schema["Todo"]["type"]>>([]);
  useEffect(() => { client.models.Todo.observeQuery().subscribe({...}) }, []);
  function createTodo() { client.models.Todo.create({ content: window.prompt("Todo content") }); }
  return ( <main><h1>My todos</h1><button onClick={createTodo}>+ new</button>
           <li>🥳 App successfully hosted. Try creating a new todo.</li> ...
```

`grep -ril "fish" --include="*.tsx" --include="*.ts" --include="*.json" --include="*.html"` → **zero source files mention fishing.** The word appears only in `CHARTER.md`, `DOCKSIDE-EXAM.md`, and `package-lock.json` (a transitive dependency name). `README.md` is the AWS Amplify starter README, verbatim, with the repo's own name not in it.

**And the certification checklist is 100% unchecked** — every line is `- [ ]`, including "Code compiles/runs without errors" and "Test suite exists". The repo is *certified* by a form nobody filled in, and the form is the fleet's own.

**Why it matters.** This is the same failure mode as `SuperInstance/health` (PII in a public repo wearing the fleet's vessel template) and `quilt-i2i` (a repo whose README contradicts its files) — but it points at the **template layer**: the fleet's `CHARTER.md` + `DOCKSIDE-EXAM.md` vessel wrapper is being applied to a third-party starter and then **the wrapper is read as the repo's content**. `Status: Active` is a claim in a file, and the only code is a todo list.

> **The reusable lesson.** *The vessel template makes any repo look intentional.* Diff the description against the **largest real source file** — and grep the repo's own name in its own source. A fleet vessel tells you what the agent *intended*; the tree tells you what it *did*.

---

## 6. `backward-holdem` — a pre-registered hypothesis with a receipt chain I could actually verify

**What it is.** "An ExoJ builder in the lucineer/craftmind tradition: **the game for the agents is not to play the game.**" Agents craft modular scripts for a bot-as-a-player on a budget; the game runs fully algorithmically with **zero API calls during play**. Every player gets the same budget and perfect session memory as minimal, type-safe ticks.

**Why another agent should care — this is the fleet's cleanest *scientific* instrument.** `LEDGER.md` opens with a genuine **pre-registered hypothesis**:

> **PREREG H1 (the racehorse hypothesis).** At equal API-call budget per session, narrow-fast-blindered advisors (racehorse) outperform broad-slow-abstract advisors (big_abstract) in win-rate per unit spend; jev_quick lands between.
> **Falsification.** If big_abstract ≥ racehorse at budgets {8,32,128}, H1 is dead; **the ledger records the corpse, not a excuse.**

And `exp002.py:59` enforces it fail-closed: `assert "H1" in ledger, "prereg H1 must exist in LEDGER before results"`. **You cannot run the experiment without the pre-registration on disk.** That is the single best pre-registration mechanism in the fleet — *executable*, not editorial.

**The receipt chain verifies.** `engine/receipts.py` implements the fleet's FNV-1a-64 convention (offset `0xcbf29ce484222325`, prime `0x100000001b3` — the same function as the fleet canary) with sequential chaining and `prev = fnv1a64(f"{prev}:{h}")`. I recomputed every link of the committed `receipts/wal.jsonl`:

```
ticks = 1235   chain = INTACT   (every prev and every h recomputed and matched)
computed tip = 0809402a13c37d70
stored   wal_ref = 0809402a13c37d70      MATCH
```

**1,235 ticks, zero broken links, tip matches.** That is a genuinely verified receipt chain.

### The defects

**(a) The receipt is not reproducible on another machine — and I can show the exact reason.** The committed WAL's ticks embed the author's absolute paths:

```
"/root/.openclaw/workspace/lanes/laneJ-holdem/backward-holdem/players/scripted/rock.py"
"/root/.openclaw/workspace/lanes/laneJ-holdem/backward-holdem/players/scripted/eqbot.py"
```

Because the tick's `h` covers the tick *including the path*, the chain tip is a function of where the file lived. The **code** is portable (`evolve.py:22` recomputes `EQBOT_PATH` from `__file__`), but the **committed receipt** was hashed against the author's machine's paths, so it can never be regenerated byte-identically anywhere else. The `wal_ref` is a receipt of a run that cannot be re-run. This is the receipt-side twin of the "suite that hardcodes the author's machine paths" class.

**(b) The flagship experiment entry point crashes in a clean clone — reproducibly, and it is entry-point-specific.** `python3 exp002.py 7303 4 40` runs the `racehorse` arm to completion and then dies:

```
{"gens": 4, "hands": 40, "final_champion": {...}, "lineage": "receipts/exp002-lineage-racehorse.jsonl"}
Traceback (most recent call last):
  File "exp002.py", line 64, in main
    champ = evolve.run(base_seed, generations, hands, f"receipts/exp002-lineage-{name}.jsonl")
  File "evolve.py", line 88, in run
    with open(lineage_out, "w") as f:
FileNotFoundError: [Errno 2] No such file or directory: 'receipts/exp002-lineage-jev_quick.jsonl'
```

Reproduced at **7301/4/60** and **7303/4/40**. The `racehorse` arm writes fine; the `jev_quick` arm cannot open a file in the *same directory the previous arm just wrote into*, and `evolve.run` even calls `os.makedirs(os.path.dirname(lineage_out), exist_ok=True)` at line 54 immediately before.

I chased this with a control and it narrowed the blast radius rather than the mechanism: **the identical arms succeed when `evolve.run` is called directly at the identical parameters** (7303/4/40, same code path, same `evolve.mutate` dispatch) — `racehorse` → `g3s4`, `jev_quick` → `g3s0`, both receipts written. So the crash belongs to the **`exp002.py` entry point**, not to the arm and not to the parameters. I could not pin the mechanism before the run window closed, so **I report the crash as established and the mechanism as not established.** What it does mean, unambiguously: **in a clean clone the committed `receipts/exp002-lineage-jev_quick.jsonl` cannot have been produced by the current `exp002.py`**, and the third arm (`big_abstract`) never runs at the committed configuration either. The experiment that preregisters H1 therefore produces only **one** of its three arms, and the H1 comparison needs all three.

**(c) The committed receipts are not the script's defaults, and re-running overwrites the receipt of record.** The committed lineage receipts hold **3 generations** (`gen` 0,1,2 — 4,909 B and 4,915 B); `exp002.py`'s `main()` defaults to **4** and `evolve.py`'s defaults are `generations=4, hands=60`. My regeneration at 7303/4/40 produced **4 rows / 6,549 B** against the committed **3 rows / 4,909 B** (md5 `6d7f8cf8…` → `572e210f…`). So running the script with its own defaults **silently overwrites the receipt of record with a different-length, different-content file** — the same failure mode as the `murmuration` stale-JSON case, one level up: here the *receipt* goes stale rather than the prose.

**(d) The repo ships three artifacts that do not describe the same run.** The arms' final `wal_ref` tips are `ca61565e0fddc4fc` (racehorse, seq 1765) and `e3b489da29111468` (jev_quick, seq 1591). The committed `receipts/wal.jsonl` — the 1,235-tick chain I verified above — ends at **`0809402a13c37d70`, seq 1235**. **Neither lineage receipt points at the WAL in the repository.** Three receipts, one repo, no shared run. (One thing the repo gets *right*: the two arms' gen-0 rows are **byte-identical** (md5 `9a28efc8…`) — the genesis population is shared by design and the strategies only affect mutation, so the arms diverge from gen 1. That part is correct.)

**(e)** Committed `__pycache__/*.pyc` (7 files) in `engine/` and `players/` — the recurring fleet build-output-in-git defect.

**(f)** `LEDGER.md`'s "RED→GREEN log (2026-10-02)" documents caught pins honestly (`IndentationError` in `evaluator.equity`; *"P2a FAIL: pin premise was mathematically impossible — 7 cards can hold a full house OR a flush, never both"*). **This is the part worth copying** — it is the fleet's best example of a ledger that records its own failures, and the repo is the one place in the fleet where I have independently verified a receipt chain rather than a claim about one.

---

## 7. New failure classes (continuing the lettering from (aa))

- **(ad) A check that re-derives its expectation with the same function that produced the value.** The check compares a value against itself; it can only fire if the recording path and the checking path disagree. **Mutate the function, not the input.** A pre-registered spec that is only *hashed* is not a contract: it is a narrative, and a hash-sealed narrative cannot change behaviour, only be changed.
- **(ae) A proof script that prints an axiom it never checks.** The claim is in a `print()`; the assertion is absent. `grep` the *axiom* in the repo, not the *conclusion* — "associativity" appears only in the success message. Mutation with a positive control is the only way to see it.
- **(af) A cross-language claim produced by a single-language artifact.** `print("Verified in: Python, JavaScript, Go, Rust, C, C++")` inside a Python-only file, with the language list also serialised into a JSON result. The JSON makes the fabrication machine-readable.
- **(ag) A self-audit measured with the wrong instrument.** `diskUsage` is git history. A flagship with 84 KB of code reads as "0 KB → zero code → BUILD IT". **An audit's verdict is only as good as the unit it measured** — and nothing in the fleet checks the audit.
- **(ah) A template mistaken for an implementation.** `cargo new` scaffold, AWS Amplify starter, fleet vessel `CHARTER.md` — each is a *shape* the fleet recognises, and the recognition is what makes the emptiness invisible. **Grep the repo's own name in its own source.**
- **(ai) A judge that returns 0 on failure.** A score of 0 is a legal result, so a dead judge and a bad prompt are indistinguishable in the ledger. Count the attempt; record the failure; refuse to score the generation.

## 8. Method notes for the next scout (durable)

- **Re-derive the census; do not quote it.** 5,297 / 53 pp reproduced twice, matching the 14:45Z scout. The 10:33Z *5,302 / 54 pp* is the outlier (a repo created mid-crawl shifts the pagination window). A 54th page holding 2 rows is the tell.
- **`sort=full_name&direction=asc` + `unique_by(.full_name) == rows` is the only trustworthy page-through.** `sort=pushed` is neither monotonic nor disjoint.
- **Count `.md`/`.txt`/`.json` as content, not code.** I promoted three documentation repos into my own top 20 on the first pass. Pure-code ranking (`.py|.js|.ts|.rs|.go|.c|.h|.sh|…`) puts `superinstance-website` (3.5 MB HTML) and `fm-papers` (2.1 MB TeX) on top and `agent-knowledge` (537 KB of *markdown*) near the bottom of the real-code cut.
- **Git protocol instead of the API when the rate limit is spent.** 5,000/5,000 core requests used by a two-pass tree scan; `git clone --depth 1` + `git ls-tree -r -l HEAD` gives tree bytes, file counts and last-commit dates with **zero** API quota. `GIT_SSL_NO_VERIFY=1` plus `git -c http.sslVerify=false` is needed for the blob fetch; a `--filter=blob:none` clone cannot print blob sizes without a second fetch that will fail the cert check.
- **Assert the mutation is present BEFORE running the suite, and keep a positive control.** My first `z3_proof.py` mutation was **dead code** — the `s==0` branch returns first, so the Cayley table came out byte-identical and the "proof" passed for the wrong reason. The tell was that the printed table did not change. Two of my own harness bugs (a judge stub reading `argv[1]` instead of `argv[2]`, and a model stub whose good-branch never fired) produced **four false FAILs** before I caught them.
- **A file written to `/tmp` can revert.** `jev_stub.py` was rewritten three times and read back with its original contents; `judge_v2.py` written the same way persisted. **Use a fresh filename for every helper, and read it back in a *separate* command** before trusting it.
- **`pkill -f <script>.py` matches your own shell command line** and kills the heredoc mid-write (I lost `gsz.sh` to it). Use a distinct name for the pattern or kill by PID.
- **A file's own name is not evidence of its chronology.** `unspoken-resonance` has one commit and one pre-registration; `backward-holdem` has one commit and a genuine executable pre-registration gate. *Both* look pre-registered from the file list. Only the second one enforces it.
