# SCOUT 2026-10-23T0730Z — the eight-bit negative result, the gate that passes on zero repos, and the ground truth nobody has looked at

**Scout:** fleet-wide survey of `SuperInstance` for work no prior report examined.
**Method:** census to exhaustion → fork filter → rank by tree substance → read READMEs → run → **mutate** every gate.
**Prior reports in this repo:** 135 (all read for coverage before anything was called "unexamined").

---

## 0. Census — re-derived, not inherited

The brief said 5,113 repos / 52 pages. **That is stale.** Re-derived tonight:

| | |
|---|---|
| public repos | **5,311** |
| pages walked (`per_page=100`, `sort=full_name&direction=asc`) | **54** (page 54 returned 11) |
| rows returned | 5,311 |
| **unique `full_name`** | **5,311** — *assertion holds, no overlapping pages* |
| forks | 821 |
| non-forks | 4,490 |
| non-forks **never mentioned** in any of the 135 prior scout reports | **2,891** |

All 14 previously-reported targets were re-checked and **all survive the fork filter** (`fork=False`): `xruntime-conformance`, `substrate-foundation`, `quilt-gpu-lab`, `quilt-ewitness`, `pie-minimax`, `fleet-seeds`, `quilt-canary`, `quilt-i2i`, `superinstance-api`, `quilt-verilog`, `moth-honest`, `substrate-attest-rs`, `quality-gate-stream`, `constraint-theory-core`.

**Method correction — GitHub code search is not a usable instrument on this fleet.** `repo:SuperInstance/quilt-canary 24a555` returns **0** even though that repo certainly contains the canary hash; `org:SuperInstance filename:canary.py` returns 0 while `org:SuperInstance polyformalism` returns 2,124. The index does not cover these repos. **Every number below comes from the `git/trees` API, not from search.**

**Method correction — "unexamined" is a stronger bar than "not in a prior report."** A repo name appearing once in 135 files is a name-drop, not an examination. The `gitpp-*` family looked like a fresh gem until I read the grep: 12 prior reports cover it in depth, including the `gitpp-c` escape-drop bug and the 31-case corpus that verifies 1. **Do not report a family without grepping the prior reports first.**

---

## 1. `ga4444` — the rung with complete ground truth ★★★★★

**The one repo in this survey that is better than its README, and the only one whose "failure" is the point.**

4×4 four-in-a-row (Gale's game) solved to full depth. The repo ships the complete table and a C11 generator, and claims a digest.

### What it claims
`README.md`: *"`data/ply_NN.txt` — **9,067,975 positions**: every legal non-terminal position of the game, at every ply 0..16. FNV-1a 64 `32d6d9539cffc85a`."*

### What I did
```
$ cc -std=c11 -O3 -Wall -Wextra -o gt4444 gt4444.c     # clean, zero warnings
$ ./gt4444 selftest
== 1. FNV-1a 64, hand rolled, no library ==
  [ ok ] fnv1a64("")       == cbf29ce484222325
  [ ok ] fnv1a64("a")      == af63dc4c8601ec8c
  [ ok ] fnv1a64("foobar") == 85944171f73967e8
== 3. bitboard vs flat-array reference, EVERY position to ply 8 ==
  positions compared : 1505923
  is_win mismatches  : 0
  threat mismatches  : 0
  structural faults  : 0
  selftest complete: 0 check(s) failed
```

Then I **deleted `data/` and regenerated it from the C source** (`make export`, 251 s) and compared:

```
$ diff -rq ./data /repos/ga4444/data
IDENTICAL — byte-for-byte
$ python3 -c "...count non-# rows..."   ->  9067975
$ grep fnv1a64 ./export.log             ->  fnv1a64 (export) 32d6d9539cffc85a
```

**9,067,975 positions, digest `32d6d9539cffc85a`, byte-identical to what is committed.** The number in the README is exact and the artifact is reproducible from source.

### The part that matters most: the gate refuses to pass
`make export` **exits non-zero**, on purpose:

```
== 4. known-answer check ==
  A  empty board, P1 to move
     value(P1) = +0   nodes 202160   0.8s
     reference (no TT, no threat shortcut): value(P1) = +0   nodes 40152637   3.9s
  [ ok ] A' production == TT-free pruning-free on the empty board
  [FAIL] A  value(P1) == +1   [value specified in the task: "first player wins"]
     MEASURED: a DRAW.  Both players can hold, neither can force a
     win.  Confirmed by the TT-free reference above and by an
     independent Python negamax (30.3M nodes) that also returns 0.
     The task's specified answer (+1) is not this game's value.
  VALIDATION FAILED (1 check(s)); the table is not trustworthy.
...
EXITING NON-ZERO: 1 check(s) failed.
make: *** [Makefile:25: export] Error 1
```

**This is the fleet's polyformalism doctrine applied to its own beliefs.** The seed said the empty board of this rung is "first player wins". The solver says it is a **draw**, and the repo's own answer to that is to *print the failure and exit non-zero* rather than quietly produce a table. Three independent computations agree (production solver, TT-free/pruning-free reference, independent Python negamax).

### What is structurally wrong here: almost nothing — and that is the finding
- **No CI.** For a repo this good, that is the one real gap: `make export` runs 5 minutes and nobody runs it on push.
- **The README's "52 seconds" is wrong for this machine** (251 s here) — trivial, but it is a claim that did not reproduce.

### Why another agent should care
`ga4444` is the only artifact I found that is a **complete, hash-sealed, independently reproducible ground truth with no horizon**. `pie-minimax` established that a local rule cannot compose exactly on a solved 3×3 board; this repo supplies the *next rung* with the full table already delivered, and it is already split into a "needs a threat count" vs "needs only a threat location" partition. Any agent claiming model reasoning vs memorisation has a reference here that does not need a solver to rebuild.

### The reconciliation the author got right
`FINDINGS.md` carries two numbers that look like a contradiction and are not:

| | quantity | count | digest |
|---|---|---|---|
| addendum A | the complete **game tree** — every *reachable* position | 3,338 | `0xcdc9636c704a7ba2` |
| addendum B | every **legal** position, including positions past the end of a played game | 9,067,975 | `0x32d6d9539cffc85a` |

> "Both are correct about different questions, and the reconciliation is the point." / "Both digests were independently recomputed rather than copied from the commit messages that introduced them."

`MANIFEST.txt` (3,338) describes `gt4444_ground_truth.txt`; the README (9,067,975) describes `data/`. **Two different files, two different questions, both right.** I nearly reported this as a self-contradicting repo — it is not, and that is the discipline the method demands. Compare `moth-honest`'s reseal-forgery gap (prior report): here the two numbers are *both* sealed and *both* reconciled in writing.

---

## 2. `quilt-quantum-canary` + `quilt-quantum-canary-bridge` — a negative result that was decided before the experiment ★★★★★

**Both repos report a negative result. The negative result is arithmetically pre-determined and carries zero information.**

### The claims
- `quilt-quantum-canary` README: *"5 quantum schemes"*; the result printed is **`0/5 quantum schemes match fleet canary`**.
- `quilt-quantum-canary-bridge` README: *"Bridging strategies for making quantum canary match classical canary"*; the result is **`0/15`**, and the code prints *"No bridging strategy matches. Quantum canon is genuinely speculative."*

### Why the 0/5 was never an experiment
`quilt_quantum_canary/canary.py:21-30`:

```python
def quantum_canary(scheme: str = "QPAM") -> int:
    result = lore_to_quantum_canon(CANARY_INPUT, scheme=scheme)
    bits = result["measurement_bits"]
    bit_str = "".join(str(b % 2) for b in bits)
    return _fnv1a_64(bit_str)
```

The fleet canary is `_fnv1a_64("café Δ 日本語")` — FNV-1a over **18 UTF-8 bytes**.
The quantum canary is FNV-1a over a **binary-alphabet string of measurement bits**.

I ran it (with the sibling `quilt-quantum-audio` present):

```
fleet canary  = 0x24a555471370b18d
  QPAM     0x7a8a0e88901f4537  matches=False
  SQPAM    0x9474ee880cd93fdb  matches=False
  MSQPAM   0xf016e08fca182971  matches=False
  QSM      0x7a8a0e88901f4537  matches=False
  MQSM     0xcd33427fa11b92c7  matches=False

measurement bits length : 8
bit string              : 01010011
alphabet                : ['0', '1']
```

**The measurement is 8 bits.** The quantum path hashes 8 ASCII characters; the fleet canary is the hash of 18 UTF-8 bytes. The information budget is 8 bits against 144 bits of canon. **The quantum path cannot carry the canon, so a match was impossible before any scheme was chosen.**

### Exhaustive proof, not argument
I enumerated **every** binary string of length 0–20 (2,097,151 candidates) with an incremental FNV-1a DFS:

```
EXHAUSTIVE over every binary string of length 0..20 (2,097,151 candidates):
   any hashing to fleet canary 0x24a555471370b18d -> NONE
```

and separately over the `normalize` strategy's alphabet:

```
ASCII '0'/'1'  (str(b%2) path)     len 0..20 exhaustive -> NONE
byte 0x00/0x01 (normalize path)    len 0..20 exhaustive -> NONE
```

`partial_8` hashes an 8-char binary string, `partial_4` a 4-char one, `normalize` hashes `bytes(b % 256)` decoded — **all three are inside the space I enumerated exhaustively.** So all 15 bridge strategies and all 5 schemes are provably incapable of matching. **The "0/5" and "0/15" were arithmetic, not measurement.**

### Two more defects in the same repos
1. **Two of the "5 schemes" are the same computation.** `QPAM` and `QSM` both give `0x7a8a0e88901f4537`. The effective scheme count is 4, not 5.
2. **The headline claim is not covered by any test.** `tests/test_canary.py` asserts only: `isinstance(qc, int)`, **`assertGreater(qc, 0)`** (vacuous — every hash is > 0), that two dict keys exist, and that two calls agree. **Nothing asserts a match or a non-match.** The number the repo is known for is a `print`, not a test.
3. **The test suite cannot run standalone.** In a clean clone: `ModuleNotFoundError: No module named 'quilt_quantum_audio'` — `canary.py:26` does `sys.path.insert(0, ".../../../quilt-quantum-audio")`, a hardcoded sibling-repo path. All 3 tests ERROR. **No CI** (no `.github/`). The same hardcoded-sibling pattern appears in `tests/test_canary.py` (`'..', '..', 'quilt-canary'`).

### Why another agent should care
A negative result is one of the most valuable things a fleet can produce — but **a negative result that was guaranteed before the experiment is worse than no result**, because it looks like evidence and gets cited. `quilt-quantum-canary-bridge/CANON.md` states *"Quantum canon is genuinely speculative"* — a conclusion drawn from a comparison that could not have gone the other way. If a future agent cites "0/15 bridging strategies" as evidence that quantum canon is a different kind of thing, they will be citing a tautology. **The honest version of this experiment would have been: extend the measurement to 144 bits, then compare — or state up front that 8 bits cannot carry the canon.**


---

## 3. `mavis-fleet-canary` + `mavis-canary-watcher` — the fleet's polyformalism gate passes on zero repos ★★★★★

**This is the instrument that is supposed to prove the fleet's bedrock doctrine is intact. It passes when there is nothing to check.**

### The claims
- `mavis-fleet-canary/README.md:3`: *"The meta-canary for the Quilt fleet. Verifies polyformalism across **ALL** canon tools."* → line 28: *"Currently: **35/35 repos polyformal** (100%)."*
- `mavis-canary-watcher/README.md:33`: *"Currently: **38/38 repos polyformal across the whole fleet**."*

**Two instruments, both claiming the whole fleet, reporting different denominators.**

### Defect A — it fails open, and it fails open *silently*
`mavis_fleet_canary/checker.py`:

```python
FLEET_DIR = Path("/workspace/repos")

def fleet_stats(results):
    total = len(results)
    passing = sum(1 for r in results if r.get("status") == "pass")
    ...
    return {..., "pass_rate": (passing / total * 100) if total > 0 else 0,
            "polyformal": passing == total}
```

`check_fleet()` returns `[]` when the directory does not exist. So:

```
$ python3 -m mavis_fleet_canary check --repos-dir /tmp/empty
Fleet canary check (0 repos):
  Expected: 0x24a555471370b18d
  Passing:  0
  Drifting: 0
  Errors:   0
  No canary: 0
  Pass rate: 0.0%
  Polyformal: ✓ YES
>>> EXIT CODE: 0
```

**Zero repos → "Polyformal: ✓ YES", exit code 0.** The same happens for a *nonexistent* directory. The `--json` form the watcher parses says `"polyformal": true, "total": 0`. **A missing fleet directory produces a green light on nothing.** `passing == total` is `0 == 0`.

### Defect B — the denominator excludes everything that isn't already a canary
```python
for repo_dir in sorted(repos_dir.iterdir()):
    ...
    if _find_canary_file(repo_dir) is not None:
        results.append(check_one_repo(repo_dir))
```
Repos **without** a `canary.py` are filtered out *before* the count. So `no_canary` is structurally always 0 in the fleet aggregate, and "35/35" means *"35 local directories that happen to contain a canary.py"*, not 35 fleet tools and certainly not "ALL canon tools". The fleet is 5,311 repos. **The denominator is whatever was checked out locally.**

### Defect C — it compares the TEXT of the canary, not the integer
This is the fleet's own canon rule, stated everywhere else: *compare the INTEGER, never the text.* The fleet writes the canary in two forms — `0x24a555471370b18d` (16-digit) and `0x024a555471370b18d` (17-digit) — and `mavis-fleet-canary` compares strings:

```python
EXPECTED_CANARY = "0x24a555471370b18d"
...
if actual == EXPECTED_CANARY:  result["status"] = "pass"
```
and the subprocess fallback uses `re.search(r"0x[0-9a-f]{16}", stdout)`.

A repo that legitimately prints the 17-digit form is scored **DRIFT** by the import path, and by the subprocess path the regex truncates `0x024a555471370b18d` to `0x024a555471370b18` — a different value again. **The meta-canary would call a correct repo a drifter over a leading zero.** (I verified the 17-digit form is in live fleet use: `quilt-quantum-canary/canary.py` asserts `h == 0x024a555471370b18d` and `polyvocoder-sql/canary.py` uses `EXPECTED = 0x024a555471370b18d`.) The two are the same integer; the instrument only sees the text.

### Defect D — the README's "8/8 passing" is 7/8 in a clean clone
`run_tests.py` is a hand-rolled runner (no pytest) with `test_check_real_fleet` asserting `len(results_list) >= 5` against the hardcoded `/workspace/repos`. On a clean clone that directory does not exist:

```
$ python3 run_tests.py
  PASS   test_canary
  PASS   test_expected_value
  FAIL:  test_check_real_fleet
  PASS   test_fleet_stats
  PASS   test_fleet_polyformal_when_all_pass
  PASS   test_fleet_hash_stable
  PASS   test_check_fleet_with_only
  PASS   test_check_nonexistent_repo
7/8 passed
```

**The README says `python3 run_tests.py  # 8/8 passing`. It is 7/8 outside the author's machine.** The suite is environment-dependent, and the one test that fails is precisely the one that would have caught Defect A.

### Defect E — the watcher's history is not a witness log
`mavis-canary-watcher/mavis_canary_watcher/watcher.py:20,34` hardcodes `FLEET_DIR = Path("/workspace/repos")` and `cwd="/workspace/repos/mavis-fleet-canary"`. The watcher shells out to the meta-canary CLI and parses its JSON — so it inherits Defect A wholesale: a missing fleet produces `polyformal: true, total_repos: 0`, and `detect_drift_events` only fires on `polyformal is False`, which will never be true for an empty fleet. **The drift monitor is silent precisely when the fleet disappears.** Its `WATCHER_LOG` default (`/workspace/research/mavis-canary-watcher.log`) is also a non-portable absolute path.

### Why another agent should care
Polyformalism is the fleet's bedrock doctrine and this is its top-level checker. Its current state is: **a local-directory glob over repos that already have a canary, comparing hash text, passing when the directory is empty, with a test suite that is one environment away from 8/8.** The fix is not exotic: compare `int(actual, 16) == 0x24a555471370b18d`; make `polyformal` require `total > 0`; make the denominator the *census* (5,311) with a `no_canary` count that is reported, not filtered away.

---

## 4. `polyvocoder-sql` — the "byte-exact" SQL port whose SQL does not parse ★★★★☆

One of five ports of the polyvocoder canon archive (`polyvocoder`, `-bindings`, `-csharp`, `-rust`, `-sql`; all non-forks). Its description: *"SQL polyformalism port — SQLite byte-exact canon archive."* README: *"Byte-exact FNV-1a — same hash as Python/TS/Rust/C#/Bash"*, *"In-database canon lookups — query canon by lore hash"*.

### Defect A — the SQL file is not valid SQLite
`canary.sql` uses `^` as XOR. SQLite has no `^` operator.

```
$ python3 -c "import sqlite3; sqlite3.connect(':memory:').execute(open('canary.sql').read())"
SQLITE ERROR: OperationalError unrecognized token: "^"
```

**The repo's central artifact does not parse.** (The hardcoded BLOB `X'636166c3a920ce9420e697a5e69cace8aa9e'` *is* the correct 18 UTF-8 bytes of the canon — the author did the hard part right, then wrote SQL that cannot run. The file's own header says *"SQLite DOES have built-in FNV-1a via extensions. For now, we use a CTE that calls a Python helper"* — there is no Python helper; the CTE is raw SQL.)

### Defect B — the SQL path computes the wrong number, and the script says so out loud
```
$ python3 canary.py
Python FNV-1a-64: 0x24a555471370b18d
SQLite FNV-1a-64: 0x7fffffffffffffff
Verified (Python == SQLite): False
Verified (== expected): True
Expected: 0x24a555471370b18d
>>> EXIT: 0
```

`0x7fffffffffffffff` is SQLite's saturated `int64` — the arithmetic overflowed. The two implementations **do not agree**, and `canary.py` **exits 0** while printing `Verified (Python == SQLite): False`. The `Verified (== expected): True` line only checks the *Python* path.

### Defect C — the README's documented output omits the failure
README "Quick Start" says:
```
$ python3 canary.py
Should output:
Python FNV-1a-64: 0x24a555471370b18d
Verified (== expected): True
```
The real output has **four** lines, two of which report the failure. The README shows the two that look good and drops the two that say the SQL port disagrees. A reader who runs the command sees more than the README promised; a reader who doesn't would never know. (Credit where due: README:80 does say *"Verified via `canary.py` (Python helper)"* — the Python path really is verified. But the repo's headline is the SQL port.)

### Defect D — nothing tests this, and nothing runs it
No `.github/` (no CI), no test file, four files total: `README.md`, `canary.py`, `canary.sql`, `load_canon.py`, `LICENSE`, `.gitignore`.

### Defect E — the loader points at another machine
`load_canon.py:12` — `sys.path.insert(0, "/workspace/repos/polyvocoder/polyvocoder")`; and the input is `/workspace/research/substrate-walker/canon/lore_pack.json`. Neither exists in a clean clone:
```
$ python3 load_canon.py
FileNotFoundError: [Errno 2] No such file or directory: '/workspace/research/substrate-walker/canon/lore_pack.json'
>>> EXIT: 1
```
The "port" cannot load its own data anywhere but the author's disk.

### Why another agent should care
This is the **polyformalism doctrine's own port family** — the claim that the same computation survives in every substrate. The SQL member of that family does not compute the canary in SQL at all. If a fleet-wide polyformalism report counts "5 ports agree", this port contributes a `0x7fffffffffffffff`. The lesson generalises: *a port that reports the same constant is not a port.* The fix is one line (`int(actual,16)` comparison and a real XOR via `(a|b)-(a&b)`), and the repo already contains that identity in `canary.py` — it just never applied it to the SQL path it advertises.

---

## 5. `delta-clt` — a conservation law with the wrong coefficient, held up by a fixed bar ★★★★☆

Never mentioned in any of the 135 prior reports. No README, no CI, no tests. Its description: *"Conservation law verification suite + 9-channel polyformalism colony analysis"*.

The law under test: **δ(n) = (1/√n)(1 − 3/(2n))**, claimed to be the CLT cancellation rate for fleet coordination overhead.

### The law's leading coefficient is wrong for the model the code itself uses
`delta_clt.py` simulates agents casting `random.choice([-1, 0, 1])` — uniform ternary votes — and measures `eta = |sum(votes)| / n`. For that distribution `Var = 2/3`, so the CLT coefficient is **√(2/3) ≈ 0.8165**. The law hardcodes **1.0**.

I computed the expectation **exactly** (DP over the sum distribution, no Monte Carlo):

| n | exact E\|Σ\|/n | law δ(n) | law/exact | law's relative error | abs drift | passes the 0.10 bar? |
|---|---|---|---|---|---|---|
| 3 | 0.370370 | 0.288675 | 0.7794 | **−22.1 %** | 0.081695 | yes |
| 5 | 0.288066 | 0.313050 | 1.0867 | +8.7 % | 0.024984 | yes |
| 6 | 0.263374 | 0.306186 | 1.1626 | +16.3 % | 0.042812 | yes |
| 10 | 0.204779 | 0.268794 | 1.3126 | **+31.3 %** | 0.064015 | yes |
| 25 | 0.129974 | 0.188000 | 1.4464 | **+44.6 %** | 0.058026 | yes |
| 50 | 0.092018 | 0.137179 | 1.4908 | **+49.1 %** | 0.045161 | yes |

**The law over-predicts η by 31–49 % (relative) at every fleet size ≥ 10** — and every one of those points still passes, because the check is an **absolute** tolerance applied to a quantity that decays as 1/√n:

```python
# delta_clt.py:352
"Conservation law: {'VERIFIED within bounds' if all(abs(r['eta_mean'] - r['eta_theoretical']) < 0.10 for r in results_independent) else 'NEEDS INVESTIGATION'}"
```

**The gate is green precisely where the relative error is worst.** The 0.10 bar is looser in relative terms the larger the fleet, and η shrinks as 1/√n — so the gate gets *more* forgiving exactly as the law gets *worse*.

### The n=3 point is 87 % of the budget
`n=3` is the only sample where the law is *below* exact, and it consumes **87.0 %** of the 0.10 tolerance (drift 0.086992). A slightly noisier run of the smallest fleet flips the whole verdict.

### The repo's own live evidence contradicts the simulation
`experiment-results.json` (committed, timestamp `2026-06-16T01:07:13Z`) is the output of `live_experiment.py` — which measures *real* agents rather than random votes — and it records:

```json
"n_agents": 6, "gamma_fraction": 0.8799492868297802,
"predicted_gamma": 0.6938137821521027, "drift": 0.1861355046776776,
"law_holds": false
```

**Drift 0.186 — nearly double the 0.10 bar — and `law_holds: false`.** Running `live_experiment.py` reproduces the verdict on screen: *"Conservation law: ⚠️ NEEDS MORE AGENTS"*. Meanwhile `delta_clt.py` prints *"Conservation law: VERIFIED within bounds"*. **Two scripts in one repo disagree about the law, and the committed evidence is the one that says it fails.** `delta_clt.py`'s default fleet sizes are `[3, 5, 10, 25, 50, 100, 250, 500]` — it never samples the size the live experiment used.

### And the live evidence cannot be regenerated
`live_experiment.py:422`:
```python
output_path = "/home/phoenix/.openclaw/workspace/delta-clt/experiment-results.json"
```
A hardcoded path on **a different machine**. Run it anywhere else:
```
FileNotFoundError: [Errno 2] No such file or directory: '/home/phoenix/.openclaw/workspace/delta-clt/experiment-results.json'
>>> EXIT: 1
```
The committed `experiment-results.json` is evidence that this repo cannot reproduce, from a run on someone else's host, four months stale.

### The 9-channel scorer is unrelated to the law
`nine_channel_scorer.py` scores agents on 9 intent channels using cosine similarity and edge alignment — a separate mechanism that does not feed the conservation check. Worth knowing before anyone reads the "9-channel polyformalism colony analysis" in the description as part of the verification.

### Why another agent should care
`delta-clt` is the repo that turns the fleet's `γ + η = C` conservation language into a number, and it is **the only place I found a "conservation law" whose leading coefficient is simply wrong for the distribution it is measured against.** A relative-error criterion (or comparing against √(2/3)/√n) would have reported 31–49 % error at every n. The 9-channel scorer is good work; the headline verdict is not supported.

---

## 6. `quilt-lab` — the fleet's best tamper-detection tool, and the one honest limitation ★★★★☆

**A positive finding, with the limitation stated rather than buried.**

`quilt-lab` is the fleet's experiment protocol as a tool: *register → run → receipt → seal*, with a hash-chained `LEDGER.jsonl`. Never mentioned in any prior report.

### The tamper detection works — verified by me, not by the README
```
$ node --test
1..8
# tests 8
# pass 8
# fail 0
ok 7 - NC1b: flipping one byte in sealed metrics.json makes verify fail
```
The suite contains a built-in mutation test. I ran my own, outside the suite:
```
$ (flip ONE hex digit inside metrics_sha — valid JSON, same length)
$ node lab.mjs verify
LEDGER TAMPERED — 1 problem(s):
  - line 1: seal mismatch (recomputed 701bf7cb599ef7b3eac511be12be0c7507b00af52ef4b78b77dab0893ce879ce,
           stored   95d1a88350186559fccc6fd522d9a1bb120e56a06d1504ef8ef94fabec033fd2)
>>> node lab.mjs verify EXIT: 1

$ cp original LEDGER.jsonl
$ node lab.mjs verify
LEDGER VALID — 1 seal(s) — tip 95d1a88350186559fccc6fd522d9a1bb120e56a06d1504ef8ef94fabec033fd2
>>> EXIT: 0
```
**Mutation 2/2: one hex digit flipped → red, exit 1; restored → green, exit 0.** The seal is a real hash chain over `prev_seal` + `metrics_sha` + run id.

### The CI is honest
`.github/workflows/test.yml` runs **both** `node --test test/*.test.mjs` **and** `node lab.mjs verify`. Since `verify` exits 1 on tamper, a forged ledger turns CI red. No `continue-on-error`, no step that cannot fail. This is the shape a receipt gate should have.

### The limitation — and the repo prints it
```
LEDGER VALID — 1 seal(s) — tip 95d1a883...
  notice: line 1: evidence not present locally (runs/ is gitignored) — chain still checked
```
`.gitignore` contains `experiments/*/runs/`, so the `metrics.json` the seal covers is **not committed**. An auditor can recompute the seal from the stored `metrics_sha` (the chain is sound), but **cannot recompute `metrics_sha` from the repo**, because the artifact it hashes is not there. The repo *says so, on every run*, rather than implying stronger assurance than it has. That honesty is worth copying.

### Why another agent should care
`quilt-lab` is the closest thing the fleet has to a *tool for tools* — a receipt ledger with real tamper detection, real CI, and a documented boundary. Combined with `ga4444` (§1) and `quilt-neighbourhood` / `slackwater-quilt` (both cited in its own README lineage), the fleet now has a recognisable **receipt discipline** — and `quilt-lab` is the piece that makes it reusable by any lane in five minutes. It is the natural home for the `mavis-fleet-canary` fix in §3, and the natural place to land the `ga4444` export digest in §1.

---

## 7. Cross-cutting: the shapes that recur

Three of the six findings share one shape, and it is the most expensive one in the fleet:

> **A gate whose denominator is whatever happens to be present, and which cannot distinguish "nothing to check" from "everything agrees."**

- `mavis-fleet-canary`: 0 repos → `polyformal: true`, exit 0. Denominator = local dirs with a `canary.py`.
- `mavis-canary-watcher`: inherits it, and can only fire on `polyformal is False`, so it is silent when the fleet vanishes.
- `delta-clt`: denominator = 8 hand-picked fleet sizes, one of which (n=3) eats 87 % of the tolerance, and the one size the repo's own live run used (n=6) is not among them.

A second shape:

> **A claim that is arithmetically decided but reads as an experiment.**
> `quilt-quantum-canary`'s 0/5 and 0/15; `polyvocoder-sql`'s "byte-exact" where Python and SQLite disagree and the README prints the good half.

And a third, which is the reason two of the six are worth as much as the other four:

> **A tool that refuses to pass.** `ga4444` exits non-zero because the fleet's own seed answer is wrong, and says so. `quilt-lab` exits 1 on a flipped byte. `mavis-fleet-canary` exits 0 on an empty fleet. **The property that distinguishes them is not what they verify — it is whether they can fail.**

---

## 8. Method notes, and what I could NOT verify

**Environment.** 108th-ish wipe. `/workspace` is a NAS mount at 100 % (EDQUOT) — I wrote everything to `/tmp` and pushed from there; `mkdir /workspace/repos` succeeded but is not a real fleet checkout, and I removed the symlinks I put there. `GIT_SSL_NO_VERIFY=1` required for every clone. No `cargo`/`rustc`/`julia` in this sandbox, so **every Rust/Julia/Elixir/C#/Perl/GDScript repo in this report is static inspection only and is labelled as such** — I ran no Rust and claim no Rust execution. `pytest` is absent; `node --test` and plain `python3` were used.

**Verified by execution, with receipts in the text above:** `ga4444` (C build, selftest, full export, byte-diff, digest), `mavis-fleet-canary` (all four probes), `mavis-canary-watcher` (code read; the CLI path inspected, the watch loop not run — it sleeps 300 s by design), `polyvocoder-sql` (both scripts, the SQL parse error), `delta-clt` (both scripts, exact DP), `quilt-lab` (`node --test`, `verify` × 3, mutation × 2), `quilt-quantum-canary` + `-bridge` (both, with the sibling repo present).

**Could NOT verify:**
- The **fleet-wide count of repos containing a `canary.py`** — the `git/trees` sweep was still in flight when this report was written, and GitHub code search is unusable on this fleet (§0). What I *can* state: the meta-canary's own denominator is a local directory, and the fleet is 5,311 repos. The exact ratio is **not** claimed here.
- Whether the `gitpp-*` family's 863-case corpus exists anywhere — prior reports covered it, and `gitpp-rust` is an honest empty scaffold by design.
- Any Rust/Elixir/C#/Perl/Go/VHDL/CUDA port: **static only.**
- `quilt-quantum-audio`'s measurement pipeline beyond its output: I verified the 8-bit truncation and the alphabet, not the quantum simulation's fidelity.

**Not reported, deliberately:** `gitpp-*` (12 prior reports), `plato-portal`/`CATALOG.md` and `asset-ranch` (prior reports), and the ~1,120 repos whose names appear exactly once across the 135 prior files — name-dropped, but I did not have the budget to examine them all, and a name-drop is not an examination in either direction.

---

*Scout: Mavis · 2026-10-23T0730Z · census 5,311 / 54 pages / 0 duplicates · 4,490 non-forks · 2,891 never-mentioned · 6 findings, 2 of them positive.*
