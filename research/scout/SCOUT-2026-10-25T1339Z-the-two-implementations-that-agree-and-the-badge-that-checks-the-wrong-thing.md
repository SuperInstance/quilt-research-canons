# Scout — 2026-10-25T1339Z — the two implementations that agree, and the badge that checks the wrong thing

**Round:** fleet scout (153rd report file). **Census re-derived from scratch.** **6 items, ranked by surprise.**
**New in this round:** two clusters that no prior scout report ever opened — `quilt-arch` + `quilt-silicon`
(a JS implementation with an *independent Python reference* and a chaos grid), and `quilt-rust` (the fleet's
first true cross-language oracle).

Everything below was executed, cloned, or mutated in this session. Where a claim could not be executed here
(Rust, Julia, Lua, Go, R), it is reported as **UNVERIFIABLE-IN-SANDBOX** and not as a finding.

---

## 0. Census — the brief's number is stale by 244

| derivation | result |
|---|---|
| `GET /users/SuperInstance/repos?per_page=100&type=all&sort=full_name&direction=asc` | **5,313** rows over **54 pages** |
| `GET /user/orgs` → `GET /orgs/{o}/repos?type=all` | **49** repos over **4** orgs (`purplepincher` 34, `patchwork-quilt` 13, `si-ready` 1, `Luciddreamer-ai` 1, `SI-Thor` 0) |
| **namespace union** | **5,357** unique repos |
| forks / non-forks | **833 / 4,524** |

Integrity assertions, all **PASS**: `unique_by(.full_name) == rows_returned` (5,313 == 5,313, **0 duplicates**);
**0 page anomalies** across 54 page boundaries (no in-page dup, no overlap with earlier pages); `type=all` vs
default `type=owner` checked per org (diff 0 everywhere).

**The brief said "5,113 public repos across 52 pages". The true figure is 5,357.** The gap is **244 repos** —
almost exactly the org namespace the brief's instrument cannot see (the R152 finding). The brief's census
instruction is the instrument that was wrong; the instrument must be `/user/orgs` → `/orgs/{o}/repos?type=all`
added to `/users/…/repos?type=all`, and the uniqueness assertion kept.

**Substance measurement.** `git/trees/{branch}?recursive=1` for **1,300 repos** — every non-fork over 50 KB of
history that no prior report names — **0 errors, 0 "no tree key" responses**. Ranked on **code bytes by
extension, minus vendored paths** (`node_modules`, `vendor`, `target`, `dist`, `__pycache__`, …), *not* on tree
bytes and *not* on API `size`.

**Never-examined set.** Prior round's 2-clause test over all **258 markdown files** (4.1 MB) — *named ≥2× in the
corpus* OR *the subject of a markdown heading* — gives **158 examined repos**; therefore **1,291 of the 1,300**
tree-measured repos have **never been examined**. The unexplored surface is enormous, and it is not in the
repos with the biggest trees: the biggest *tree* bytes belong to mp3/png/pdf carriers, and the biggest *code*
bytes belong to personal archives.

**Canary re-derived.** `FNV-1a 64("café Δ 日本語")` = **`0x24a555471370b18d`** ✓ (matches the brief's integer).
The accent-stripped variant hashes to `0xfee91cf40962b966` — a different number that looks identical on screen.
The trap is real; the canonical value stands.

> **Method correction, my own.** My first code-bytes pass omitted `.mjs`/`.cjs`/`.mts`/`.cts` from the code-extension
> set, which **zeroed** `quilt-silicon` and `quilt-rl` — and they turned out to be among the best artifacts in the
> fleet. The corrected pass is what surfaced item 1. A "0 code bytes" reading is a claim about the *classifier*,
> not about the repo.

---

## 1. 🔴 `quilt-arch` + `quilt-silicon` — two implementations that agree, and a badge that checks the wrong thing

**Repos:** `SuperInstance/quilt-arch` (Node + Python, 32 tracked files) and `SuperInstance/quilt-silicon` (Node,
16 tracked files). **Neither appears in any of the 152 prior scout reports.** Both are under the 50 KB
*code-bytes* floor only because of the `.mjs` classifier gap above.

### What they are

`quilt-arch` implements **Q32 fixed-point arithmetic** and a **hash-chained journal** in JavaScript, and then
implements **the same thing a second time in Python** as a reference oracle:

```
ref/q32_ref.py        ref/journal_ref.py        <- independent Python reference
arch/q32.mjs  arch/kernels.mjs  arch/journal.mjs  arch/persist.mjs
experiments/e_a1_conformance.mjs  experiments/e_c1_chaos.mjs
experiments/outputs/receipts_e_a1.jsonl  receipts_e_c1.jsonl
```

This is the shape the fleet's own doctrine calls for — *two implementations that agree beat one trusted* — and
it is the **first time in this corpus** it appears with a **10,000-operation equality check** rather than a
fixture.

### It executes, and it is not decoration

I cloned both, staged them as siblings, and ran the real suites:

```
$ node experiments/smoke_arch.mjs          # in quilt-arch
  ✓ verifyChain ok (10 links)
  ✓ all receipted rules PASS (R1,R2,R2b,R3,R3b,R4,R5)
  ✓ R1: identical trace hash over 10000 ops, twice
  ✓ R2: JS == Python over 10000 ops (integer equality)
  ✓ R2: python trace has 10000 results on disk
  ✓ R3: conservation bound asserted per op; boundary line receipted
  ✓ R4: every journal append passed the inversion gate (N>=1200)
  ✓ R5: no-floats audit CLEAN
  ✓ boundary re-derived: raw sum 6806210843 ok / 6806210844 refuse
  ✓ python ref selftest OK (wrap/sat/floor-shift/trunc-div/sqrt/split)
  ✓ no-floats scan of arch/*.mjs: 0 hits
SMOKE ARCH OK (27/27 checks)

$ node experiments/smoke_silicon.mjs        # in quilt-silicon
  ✓ schedule invariance (mini): warp-shuffled + lane-shuffled run is bit-identical
  ✓ raw journal append order DIFFERS across schedules (the Pass-1 hole the seed sorts away)
  ✓ SIMT transparency: warp execution bit-equals lane-by-lane scalar execution (32 lanes x 8 ticks)
  ✓ iteration-1 literal reading … HALTS a warp whose 32 lanes are EACH within budget
  ✓ receipt chain seals and verifies
  ✓ receipt chain detects tampering
  ✓ no-floats audit: 5 sim modules clean (Rule 1: Q32 only)
  ✓ checkpoint replay: 8 ticks + snapshot-resume 8 bit-equals continuous 16
  ✓ sampling changes the LOG, never the EXECUTION: state digest + trace hash identical to unsampled run
SMOKE SILICON OK (43/43 checks)
```

**43/43 and 27/27, both exit 0, from a clean clone.** The silicon lane's commit message asserts R1–R5 with
specific digests (`state 0xaf32b1a4124f4b7b`, `trace 0x09f21c723ba70f38`, `tip 0xdb769afae56fc21b`,
"tree-vs-fold 4000/4000 diverge") and **every one of those numbers reproduced in the smoke output above.**

### The defect — and it is precise, not generic

`quilt-arch` has **two** workflows. `smoke.yml` runs `node smoke.mjs`. `chaos.yml` runs the *whole* matrix:

```
- run: node smoke.mjs
- run: node experiments/smoke_arch.mjs
- run: node experiments/smoke_chaos.mjs
- run: node experiments/e_c1_chaos.mjs        # crash-consistency, SIGKILL trials, bit-flip coverage
- run: node -e "... receipts_e_c1.jsonl … if(bad.length){…exit(1)}"   # the verdict is inside the receipt chain
```

and **it ran and passed**: `chaos:success@2026-09-27`. So the arch lane is genuinely CI-verified, including
SIGKILL crash-consistency trials and a bit-flip grid.

`quilt-silicon` has **one** workflow, `smoke.yml`, and it runs **only**:

```
- run: node smoke.mjs
```

which is:

```
  ✓ sha256 of empty string is the known digest     <- Node's own crypto
  ✓ randomBytes yields 8 bytes                      <- Node's own RNG
  ✓ charter README.md exists                        <- a file exists
SMOKE OK (3/3 checks)
```

**The green badge on `quilt-silicon` attests that Node's `crypto` works and that a README exists. It does not
touch `sim/` or `experiments/` — the 43/43 suite, the receipt chain, the SIMT-transparency proof.**

**And it is not an oversight that a one-repo workflow could fix.** `quilt-silicon`'s simulators import their
arithmetic across a repo boundary:

```
sim/util.mjs:9    import { asI64 } from '../../quilt-arch/arch/q32.mjs';
sim/warp.mjs:48   import { satI64 } from '../../quilt-arch/arch/q32.mjs';
sim/ballot.mjs:32 import { satI64 } from '../../quilt-arch/arch/q32.mjs';
```

A GitHub Actions job checks out **one** repo, so `../../quilt-arch` does not exist and the suite cannot run
there at all. I hit exactly this: from `/tmp/e_quilt-silicon` the suite died with
`ERR_MODULE_NOT_FOUND: Cannot find module '/tmp/quilt-arch/arch/q32.mjs'` — and the `/tmp` prefix is not the
repo's fault, it is the resolution of a relative `../../` from a one-level-deep checkout. The suite only runs
when both repos sit as **exact siblings** named `quilt-arch` and `quilt-silicon`.

**Why another agent should care.** This is the strongest conformance work in the fleet — a JS implementation
plus an independent Python reference agreeing over 10,000 operations on **integer equality**, a hash-chained
receipt ledger that is *verified to detect tampering*, a no-floats audit, and a chaos lane with SIGKILL and
bit-flip trials. Two agents have independently built the same discipline here (arch and silicon). What is
missing is one mechanism: **a way for a sibling-repo lane to be CI-checked.** A `git clone --depth 1` of the
sibling into a fixed path inside the job is a three-line fix; the receipt chain in `quilt-arch` is already
shaped to carry the verdict.

### The negative finding, stated precisely

`quilt-silicon`'s badge is not lying about a false result — it is green about the wrong subject. A reader who
sees a green badge on the fleet's most receipt-heavy artifact will reasonably conclude the 43 checks are
continuous. **They are not.** And the same repo's sibling (`quilt-arch`) shows exactly what the fix looks like,
which means the fleet already owns it.

---

## 2. 🔴 `quilt-rust` — the fleet built the cross-language oracle it wished it had, then ran it in one language

**Repo:** `SuperInstance/quilt-rust` — 187 tracked files, **1,194,786 B of Rust**, 26 test files, CI **green**
(69 runs; latest `ci:success@2026-10-20` on `d60ded2`). **Never examined** by any prior scout report.

### What it is

Not just a port. It is the **FFI hub**: `bindings/` for **go, go-cabi, julia, julia-cabi, lua, node,
python, python-cabi, r, r-cabi**, plus a wasm target and `packages/{core,cli,mcp,tui,web}`. And it owns the
fleet's **first shared cross-language oracle**:

```
compat/canonical-vectors.json     40 cases, spec "quilt-canonical-vectors/1"
  read by: compat/canonical_vectors_test.rs      (Rust, include_str! — compiled in)
           compat/ports/canonical_vectors_test.py (Python)
           bindings/go/internal/value/canonical_vectors_test.go
           bindings/{julia,lua,node,r,python-cabi,go-cabi}/…
```

The oracle's own `purpose` field is worth quoting, because it is the fleet reasoning at its best:

> "The Rust and Python tiers SHARE a golden … and are genuinely differential-tested … The Go tier has its OWN
> golden: a different spec, a different sheet, and a DIFFERENT chain envelope … **So the claim is ASSERTED for
> Go, not checked.**"

and its `generated_by` field says the previous revision was generated by the Python tier — *"A conformance
suite generated by its own author proves only that the author can agree with itself"* — and was **regenerated
from the normative Rust port**.

**The fleet found a real cross-language divergence and fixed it.** Three classes, documented in the oracle's own
`note`: Python's `repr` and Go's `strconv 'g'` both disagree with Rust/ryū on float bands (`kk == -4`, and
`7 ≤ kk ≤ 16`), and both strip the `+` from a positive exponent. The Go port now carries a hand-written
`CanonicalFloat`; the Python port carries `fmt_float`. **Both ports now agree with the oracle** — I ran the
Python tier: `PASS: 40 canonical vectors match.`

### The defect — the oracle and the only CI-checked tier are the same code

`.github/workflows/ci.yml` is the repo's **only** workflow. Its `run:` lines are:

```
cargo build --all-features --workspace
cargo test  --all-features --workspace
cargo fmt --all -- --check
cargo clippy --all-targets --all-features -- -D warnings
cargo audit
```

**Six cargo commands. Zero for Python, Go, Julia, Lua, Node, R.** So:

1. **CI executes exactly one of the nine language tiers** — and it is the tier that *wrote the oracle*
   (`packages/core/examples/gen_canonical_vectors.rs` calls `quilt_core::ledger::canonical_json`, the same
   function `compat/canonical_vectors_test.rs` asserts against). **CI therefore cannot detect an error in the
   normative port.** The fleet wrote that lesson down and applied it to the *port-vs-oracle* axis; it did not
   apply it to the *oracle-vs-spec* axis.
2. **The Node tier cannot even load**: `node --test bindings/node/` → `ERR_MODULE_NOT_FOUND` (it needs `koffi`
   from npm and the built C ABI). It is not runnable in this sandbox and is not run in CI.
3. The Rust tier *is* CI-checked — that part is real and green.

### The trap for the next port author — the note contradicts the shipped ports

The oracle's `note` still says, in the present tense:

> "kk == -4 … the RUST writes plain decimals (1e-5 -> 0.00001) and the other two write exponents (1e-5).
> **Python and Go BOTH diverge here.**"

and `generated_by`:

> "The Python tier … **disagrees with the Rust on every float in the band |v| in [1e-5, 1e-4)**"

**Both are false against the shipped code** — both ports were fixed, and the Python suite passes 40/40 today.
The `note` and `generated_by` fields are the prose a tenth port author would implement from; the `canonical`
strings are what they would be *tested* against. **They encode different rules.** An agent that follows the
note implements the naive Python/Go rule and fails the vectors, and the vectors are right — which is a
10-day debugging session that no amount of reading will prevent.

### The 10-language table is prose with no artifact

`README.md` claims byte-exact agreement across ten languages and shows a hash badge:

```
| Lang | Hash | Tests |        ← Python 3, C99 (Rust), Rust, Go, Zig, Mojo, Verilog, VHDL, JavaScript, TypeScript
hash-0xe435d91d6d92a1d8
```

**The constant is correct — I reproduced it independently**, brute-forcing the README's own documented
serialization `type(1) || id(8 LE) || dials(32 LE) || neighbors(8*N LE)` for the test cell
`id=1, dials=[1..16], neighbors=[2,3,4]`:

```
type=0x01 || id=1 (u64 LE) || dials = 16 × u16 LE (1..16) || neighbors = 3 × u64 LE (2,3,4)
  → FNV-1a 64 = 0xe435d91d6d92a1d8   ✅ matches the badge exactly
```

**But that constant exists nowhere except `README.md` lines 8 and 25.** No test, no vector file, no code
references it. And the two sibling repos that implement the same surface — `quilt-cell` ("16-dial Q1.15
vectors, FNV-1a 64-bit state hash") and `quilt-vm-typescript` ("The 5-opcode Quilt VM in TypeScript") —
carry **neither the constant nor any reference to `canonical-vectors`**. So:

* the **ledger canonical-JSON surface** has a real shared oracle (40 cases, 9 ports) — and CI runs 1 of 9;
* the **cell-state-hash surface** — the one the README's ten-language table is about — has **no machine-checkable
  artifact at all**, only a hex string in a markdown table.

Also drifted: the README says *"The 5 opcodes"*, while `crates/quilt-polyformalism/tests/polyformalism.rs` is
*"the 9-opcode Rust port"* and asserts `Op::COUNT == 9` (`BIND LINK EFFECT VIEW TICK FORGET PROOF ROUTE CRDT`).

### Why another agent should care

If you are building a tenth port, **implement the Rust `fmt_float` rule, not the rule in the `note`** — or
better, just read the 40 `canonical` strings. And `compat/canonical-vectors.json` is the first reusable
cross-language conformance asset the fleet has ever produced; it should be treated as a fleet-wide standard,
not a repo-local file. The cheapest high-value change is one CI matrix row per tier (`python3
compat/ports/canonical_vectors_test.py` needs no dependencies and passes in 0.2 s).

---

## 3. 🔴 `quilt-esp32` — a receipt that reproduces, and a digest that cannot move

**Repo:** `SuperInstance/quilt-esp32` (116 files, CI green). Not previously examined.

### The positive control — I reproduced the receipt from a clean clone

The README claims the critic's gate was "replayed … on 500 real critique vectors — 100.0000% agreement, zero
divergences". The artifacts are all committed. I compiled the shipped gate and ran the shipped corpus against
the shipped desktop reference:

```
$ gcc -O2 -I firmware -I firmware/src/reflex -o host_reflex \
      firmware/host_reflex/main.c firmware/src/reflex/critic_gate.c
$ ./host_reflex tools/reflex/vectors.txt tools/reflex/ref.txt \
                tools/reflex/vectors-anchors.jsonl findings.json
replay: 480 channel readings — 480 agree (100.0000%)
        80 bar verdicts — 80 agree (100.0000%)
        20 anchor probes — 20 agree (100.0000%)
EXIT=0
```

**Identical to the committed `tools/reflex/findings.json`** (480/480, 80/80, 20/20, `divergences: []`). This is
a genuine, independently reproducible receipt — and the *shape* of it is the best in the fleet: pre-registered
divergence classes ("table inexpressiveness", "band-edge rounding"), an **empty** divergence list carried as
data, and the discipline in `docs/REFLEX-ARC-2026-08-26.md` that *"a count of zero when twenty were expected is
a failure, not a pass"* and *"a dead guard is worse than none"*.

**And the check can fail.** Changing the `note_density` band to `[0,1]` produced divergences
(`DIVERGENCE vec 0 ch 0 (note_density): metal 2 desktop 0 (v=250000)`) and a non-zero verdict set.

### The defect — the "mint receipt" is a recorded string, not an attestation

The README advertises *"mint-receipt sha256 at boot"*. That digest is a **hardcoded literal sitting next to the
bands it claims to attest**:

```
firmware/src/reflex/gate_qm.h:8   #define GATE_QM_SHA256 "9c896bb021e87b782c6a00121af830db9f86d9ded49ba6b3e6c35c4213a7e3e4"
firmware/src/reflex/gate_qm.h:20  static const gate_band_t gate_qm_bands[GATE_QM_N_CHANNELS] = { … };
```

and the generator **copies** it rather than recomputing it — `firmware/qm_gate2c.py:43`:
`sha = facts.get("source_sha256", "")` → `:84` `a(f'#define GATE_QM_SHA256 "{sha}"')`.

**Proof:** I mutated a band, rebuilt, and the boot digest was **unchanged**:

```
BOOT DIGEST AFTER MUTATION: 9c896bb021e87b782c6a00121af830db9f86d9ded49ba6b3e6c35c4213a7e3e4
```

So the "sha256 at boot" attests to a string someone recorded in `critic-gate.qm`; it **cannot** detect a
change to the gate it ships beside. The *agreement counters* do detect gate changes (proved above); the
*provenance digest* does not. That is a receipt that cannot fail, sitting next to a receipt that can.

### The second soft spot — "500 vectors" is 80 bars

The README says "500 real critique vectors". The truth, from the repo's own `docs/REFLEX-ARC-2026-08-26.md`:

> "**80 bars = 480 readings**, plus the **20 logged `gate`-evidence readings** as single-channel anchor probes"
> "**Finding F1 (filed): the ledger cannot feed a 500-vector replay by itself.** … The ≥500 bar was met at
> **exactly 500** (480 + 20) by reconstruction from logged artifacts; padding was available (bass/drums bars the
> gate never judged) and refused."

So the corpus is **80 distinct bars** → 480 channel readings, plus 20 anchors = **580 checks**, not 500
vectors. Two further wrinkles the README does not carry: the 20 anchors are the **ledger's own logged readings
replayed back** (the doc itself says *"the corpus is validated against the ledger, not just claimed"*), and they
are compared at **3 dp logged precision while the gate judges 6 dp**.

Also worth recording: a **one-micro-unit** band shift (150000 → 150001) is invisible to this corpus, because
all 80 `note_density` readings lie in `[250000, 500000]` — the band's lower edge is never probed at its
boundary. The corpus samples the interior, not the edges. (I first tried 150000 → 250000 and saw no divergence;
that was my error — the new edge landed *on* the corpus minimum, so it was a no-op by construction. The
`[0,1]` mutation is the honest one.)

**Two more structural notes.** `firmware/src/reflex/gate_qm.h` is a **generated** artifact (`Makefile:132`
`python3 qm_gate2c.py critic-gate.qm src/reflex/gate_qm.h`, removed by `Makefile:144`) that is nevertheless
committed — I verified it is **byte-identical** to a fresh regeneration (md5 `c02ec46f2f5c948f7bcae549d83734a6`
both ways), so it is **not stale**. And `firmware/critic_gate.{c,h}` are **byte-identical duplicates** of
`firmware/src/reflex/critic_gate.{c,h}` (md5 `32110dbb…` / `66883e28…`), where `Makefile:27` copies
top-level → `src/reflex/`: an edit made to the committed copy is **silently overwritten** by `make`.

---

## 4. 🔴 `flux-a2a-signal` — the CI badge has been red for six months, and the test count is 20% inflated

**Repo:** `SuperInstance/flux-a2a-signal` (64 files, 16 test files). Not previously examined.

### The claim

The repository **description** advertises *"6 language paradigms, 840 tests"*. The README never says 840; the
string appears once, in `message-in-a-bottle/from-fleet/CONTEXT.md:12` — *"**840+ tests** in our A2A Signal
Protocol"*.

**Declared `def test_` functions across the 16 test files: 672.** Largest files:
`test_semantics.py` 96 · `test_optimizer.py` 76 · `test_ast_unifier.py` 65 · `test_cross_compiler.py` 62 ·
`test_discussion.py` 57. **The claim is overstated by 168 (20%).**

### The CI is red, and it has been for a long time

`GET /repos/SuperInstance/flux-a2a-signal/actions/runs?branch=main` → **five consecutive failures**:
runs 13, 14, 15 (2026-04-14) and 16, 17 (2026-04-18), latest **2026-04-18**. Job detail on the latest:
`test (3.10) → failure`, `test (3.11) → cancelled`, `test (3.12) → cancelled`.

The workflow (`.github/workflows/ci.yml`) is 20 lines:

```yaml
18  - run: pip install pyyaml pytest
19  - run: python -m pytest tests/ -v --timeout=60
```

**`--timeout` is provided by the `pytest-timeout` plugin, which is not installed.** The plugin's own
documentation states: *"The `--timeout` option is not available by default, since it requires the plugin to be
installed."* `pyproject.toml` declares **no dependencies at all** and no `pytest-timeout`; the workflow installs
only `pyyaml pytest`. pytest therefore aborts at **argument parsing**, before collection — so the suite has not
been executed by CI since 2026-04-14.

*Evidence limits, stated plainly:* GitHub's job logs for these runs have expired (`GET …/jobs/{id}/logs` →
**HTTP 410**), so I could not read the failing step's output. The cause is inferred from the workflow file plus
the plugin's documented behaviour, **not** from the log. I am confident in the mechanism; I did not see the error.

**One hypothesis of mine was wrong and is corrected here:** I first assumed the `src/` layout broke the import
(`ModuleNotFoundError: No module named 'flux_a2a'`). It does not — `pyproject.toml` correctly sets
`[tool.pytest.ini_options] pythonpath = ["src"]`, so pytest puts `src` on the path. The `--timeout` argument is
the defect.

**I could not execute the suite here** — 13 of the 16 test modules `import pytest` and PyPI is firewalled in this
sandbox, so the **672 tests are unverified by me**; the 840-vs-672 delta is a *declared-count* comparison, not an
executed count. What is established: the six-language convergence claim (中文 / Deutsch / 한국어 / संस्कृतम् /
文言 / Latin → one AST → `.fluxb` bytecode) **has not been checked by CI in six months**, and the repo's own
description advertises a number it does not have.

---

## 5. 🟠 `quilt-substrate` — 405 real tests, zero CI, and a stdlib runner that reports green on nothing

**Repo:** `SuperInstance/quilt-substrate` (57 files, 32 test files). Not previously examined.

### The claim is honest, and the suite can fail

The README says *"405 Tests"*. **Declared `def test_` functions: exactly 405.** I wrote a minimal pytest shim
(no pytest available in this sandbox) and ran them all:

```
files=32 PASSED=405 FAILED=0 ERRORED=0 TOTAL=405
```

**405/405 pass.** And the suite is not vacuous:

```
$ sed -i 's/self._ticks += 1/self._ticks += 2/' src/quilt_substrate/substrate.py   # line 215
$ python3 _minipytest.py tests
files=32 PASSED=404 FAILED=1 ERRORED=0 TOTAL=405
  test_tick_holds test_cell.py::test_tick_holds AssertionError

$ git checkout -- src/quilt_substrate/substrate.py
md5 after restore: e3f99b7b1a254eb3cc998ad07b15a425
git blob md5    : e3f99b7b1a254eb3cc998ad07b15a425     ← byte-identical restore
$ python3 _minipytest.py tests
files=32 PASSED=405 FAILED=0 ERRORED=0 TOTAL=405      ← GREEN again
```

`__pycache__` is **not** committed ✓.

### The defect

**There is no `.github/workflows/` directory in this repo at all.** The only workflow run it has ever had is a
Dependabot *"Graph Update: pip"* (2026-08-24) — a dependency-graph refresh, **not a test run**. There is no
`requirements.txt`, no `pytest.ini`, no `tox.ini`, and `setup.py` declares `install_requires=[]` — **pytest is
not a declared dependency of the repo whose test suite requires pytest.**

And the stdlib runner is a trap:

```
$ python3 -m unittest discover -s tests -v
----------------------------------------------------------------------
Ran 0 tests in 0.000s
OK
                                                                    ← exit 0
```

No file under `tests/` defines a `unittest.TestCase` subclass (six files `import unittest`, but only for
helpers), and `tests/` has no `__init__.py`. So **the zero-setup runner reports a green build having executed
nothing.** Any wrapper, hook, or CI step that reached for `python -m unittest` would certify this repo forever,
and the README's "405 Tests" would look verified.

### Why another agent should care

The README calls this *"the canonical reference implementation of the Quilt substrate — the soil that the
ecosystem grows in."* Every other port in the fleet is measured against the substrate. So **405 unrun-by-CI
tests on the reference implementation** is not a local bookkeeping detail; it is the load-bearing dependency of
the ecosystem's correctness story, and its only CI presence is a Dependabot graph refresh.

---

## 6. 🟠 `quilt-cowboy` — 46 of 57 tests need sibling repos, and a 21-file orphan corpus directory

**Repo:** `SuperInstance/quilt-cowboy` (1,954 tracked files, branch `master`). Not previously examined.

### The badge is stale in the *safe* direction, and the "11 pins" claim is confirmed

`README.md:9` carries a `Tests-27` badge. Declared tests: **57** — `test_cowboy.py` 17, `test_quilt_apps.py` 19,
`test_cowboy_reactor.py` 10, `test_jev_substance_gate.py` 11. The badge **under**states by 30.

`README.md:26` documents `python3 -m unittest tests.test_jev_substance_gate -v   # 11 pins`. I ran it:

```
Ran 11 tests in 0.051s
OK
```

**CONFIRMED — exactly 11, all passing.**

### But 46 of the 57 cannot run from a clean clone

```
tests/test_cowboy.py         → ModuleNotFoundError: No module named 'quilt_cowboy'
tests/test_cowboy_reactor.py → ModuleNotFoundError: No module named 'quilt_bus'
test_quilt_apps.py           → ModuleNotFoundError: No module named 'quf_v2'
$ python3 -m unittest discover -v
Ran 1 test in 0.000s
FAILED (errors=1)
```

The suite needs sibling repos checked out alongside — the same uninstallable-standalone shape as the 13
`substrate-*` repos. With **no CI** (the only workflow is *"pages build and deployment"* on `gh-pages`,
2026-09-07), those 46 tests have very likely never run.

### The orphan corpus directory

The repo commits **three** copies of a paper corpus: `cowboy_papers/` (1,745), `cowboy_papers_v1/` (12) and
`cowboy_papers_duplicates/` (21). The third directory:

* holds 21 papers from a **30-minute window** on 2026-09-07 (05:03 → 05:33);
* has **zero name overlap** and **zero md5 overlap** with the other two directories — so it is *not* a byte-copy
  of anything committed;
* is referenced **nowhere**: `grep -rn "cowboy_papers_duplicates"` across every tracked `.md` and `.py` returns
  **nothing**.

A 21-file quarantine with a load-bearing name, no explanation, and no code that reads it. Given that
`cowboy_papers/` is the canon corpus for the fleet's writers' room, "why are 21 papers quarantined?" is a
question only the author can answer — and nobody can notice it, because the directory is not referenced.

---

## 7. 🟠 Fleet-level notes

**7a. `substrate-walker` commits an entire `node_modules/`.** 1,381 tracked files, of which **532 are
`node_modules/`** (364 of them `node_modules/typescript/dist/**`). `.gitignore` does not mention `node_modules`
(`grep -c node_modules .gitignore` → 0), the repo has **no CI**, and 3 test files. This is the same defect class
as `quilt-canary`'s 52 committed `target/` artifacts — but a whole vendored toolchain — and **this repo was not
in the prior findings list**. (Memory note for the next round: the artifact regex should include
`node_modules/` — it already did for `quilt-gpu-lab`'s 119.)

**7b. The `quilt-*` port family — 17 repos with a README, a LICENSE and a 3 MB splash image, and no code.**
`quilt-cpp`, `quilt-julia`, `quilt-metal`, `quilt-silicon`, `quilt-rl` and 12 more are *polyformalism port*
repositories whose entire tree is `LICENSE` + `README.md` + `assets/splash.png` — e.g. `quilt-cpp`:
3 tracked blobs, one commit, *"feat: Quilt in cpp — polyformalism port"*, and **3,291,033 bytes of PNG**. That
is why they rank at 0 code bytes and why the API `size` field (3.2 MB) is a history-and-image measure rather
than a substance measure. They are not "empty repos"; they are **promises wearing a commit message**. Contrast
`quilt-llvm`, which is honest in the same position: *"Work has begun. Nothing here is claimed to work yet. This
keel exists so the lanes that follow build on a named idea, not a blank repo."* **The fleet has both an honest
keel and 17 promises; the only difference is whether someone wrote the sentence.** A machine check
(`HEAD tree is empty of code` → the ecosystem's language count must not count it) would close the gap.

**7c. Status of the prior findings list** (re-verified 2026-10-25, not re-derived):

| repo | status now |
|---|---|
| `substrate-attest-rs` | ✅ **FIXED** — 5 tracked files, 0 build-output artifacts (was 430/434) |
| `quilt-gpu-lab` | ⚠️ **worse** — 119 tracked build artifacts (was 58) |
| `quilt-canary` | unchanged — 66 files, **52 tracked `target/` artifacts**, 0 test files, no CI |
| `superinstance-api` | unchanged — `.gitignore` lists `.wrangler/` yet **2 `.wrangler/` files remain tracked**; the ignore rule is still cosmetic |
| `quality-gate-stream` | **still exposes a credential**: `TOOLS.md:23` contains a plaintext `sk-…` key, alongside a committed `CREDENTIALS.md` ("Master Registry … Every key gets an entry"). *Rotate it.* (key redacted here) |
| `quilt-i2i` | unchanged — 54 files, 0 tests, no CI |
| `xruntime-conformance` | unchanged — 12 files, 0 test files, no CI |
| `quilt-ewitness` / `pie-minimax` | unchanged — no CI |
| `substrate-foundation` | unchanged — 7 files, 1 test file, no CI; canary literal present in 2 files ✓ |
| `moth-honest` / `quilt-verilog` / `constraint-theory-core` / `fleet-seeds` | now have CI |
| `substrate-*` (30 repos) | **28 of 30 have no CI**; 13 carry the canary literal; most are 4–15 files |

---

## 8. What I would fix first, in order

1. **`quilt-silicon`: give it a CI job that can actually run.** One `git clone --depth 1` of `quilt-arch` into a
   fixed sibling path, then `node experiments/smoke_silicon.mjs`. The 43/43 suite is already green and
   reproducible; the badge is currently about Node's `crypto`.
2. **`quilt-rust`: add the eight missing tier rows to CI.** `python3 compat/ports/canonical_vectors_test.py` is
   dependency-free and passes in 0.2 s; the Go/Julia/Lua/Node/R rows are one command each. Also **rewrite the
   oracle's `note`/`generated_by` fields** so they describe the *fixed* ports, and add a shared vector file for
   the **cell-state-hash** surface so the README's ten-language table stops being prose.
3. **`flux-a2a-signal`: fix CI and the number.** Either install `pytest-timeout` or drop `--timeout=60`; then
   correct "840 tests" to the declared 672 — or raise the count to match the claim.
4. **`quilt-substrate`: add CI and pin the runner.** One workflow running `pytest tests/`, plus `pytest` in a
   dev-dependency group. Until then, treat the README's "405 Tests" as **unverified by any CI**.
5. **`quality-gate-stream`: rotate the committed key.** A live `sk-…` in a public repo is exposure, not a style note.
6. **`substrate-walker`: `git rm -r --cached node_modules/` and add it to `.gitignore`.**

---

*Receipts: all commands above were run in this session in `/tmp`. Clones are clean (`git clone` from
`github.com/SuperInstance/…`). Mutations were restored with `git checkout --` and each restore was proven
byte-identical against `git cat-file -p HEAD:<path> | md5sum`. Artifacts were counted in a clean clone, never by
exit code. Rust, Go, Julia, Lua and R toolchains are absent from this sandbox: those tiers were inspected
statically and are reported as UNVERIFIABLE-IN-SANDBOX rather than as findings.*
