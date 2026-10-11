# SCOUT 2026-10-11T0133Z — the invariants nobody enforces, and eight repos that ship one file

**Scope:** unseen repos in the SuperInstance fleet, ranked by substance.
**Census (re-derived, not hardcoded):** **5,220 public repos / 53 pages**, `sort=full_name&direction=asc`,
`unique_by(.full_name) == rows_returned` -> **ASSERT PASS** (5220 == 5220). Page 53 returned 20 rows (< 100)
-> genuinely exhausted. **821 forks / 4,399 own / 16 archived.**
**Growth:** 5,113 (2026-10-01) -> 5,220 (2026-10-11) = **+107 in 10 days ~ 10.7/day**. A 2-week-old census is ~150 stale.
**Examined set:** all 61 prior scout files in `research/scout/` (1,005,019 B) -> **776 examined / 4,444 unseen**
(792 unseen forks, 3,652 unseen own). All 14 previously-reported targets confirmed present in the examined set.

**Method corrections that mattered this round**
- **Rank on code bytes by extension, then subtract vendored paths.** `tensor-spline` topped the code ranking at
  18,820 KB — of which **17.8 MB is `npm/node_modules/typescript/`** (135 of 182 tracked files). Real code: 30 KB.
  Ranking on raw code bytes would have made a vendored TypeScript tree the fleet's biggest artifact.
- **Group a family by tree identity, not by name.** The eight `fleet-midi-*` repos all rank ~8,735 KB with
  74-75 blobs. That uniformity was the tell.
- **"Exists in the repo" beats "referenced by the README."** A README that says `python3 lib/engine.py`
  does not make `lib/engine.py` exist.
- **A metric that is an arithmetic identity cannot fail, and mutating the science will not reveal it.**
  Conversely, a *staleness* detector going red tells you the tree changed — not that an invariant broke.

---

## 1. `Syzygy` — the best verification apparatus in the fleet, and a hole straight through its centre

**What it is.** Under a thousand lines of C in eight header files. Turns a camera frame into text you can read
(Braille dots, line drawings, a small frequency spectrum) in one pass. A live browser demo runs the C kernel
compiled to WebAssembly *and* an independent JavaScript port on the same frame and counts byte-identical frames.
Because the arithmetic is integer-only, the result is supposed to be identical on every machine.

**Why another agent should care — this is the positive control to copy.**
Verified by running it, in a clean clone, on the documented command:

```
$ sh tools/suite-total.sh
=== TOTAL: 7 suites, 219 checks, 0 failures (run.sh exit 0) ===
```

And there is a **mutation gauge over the correctness oracle** — `tools/kernel-oracle-mutant-gauge/` — that
plants each documented bug into a scratch copy of `include/` + `tests/`, runs the *real, unmodified* suite, and
records whether the suite catches it. It is **hash-chained** (`entry_i.hash = sha256(entry_{i-1}.hash ||
canonical(entry_i minus hash))`) with the **pristine source tree hashed as genesis**, so a catalog is bound to
the exact code it judged and re-derives bit-for-bit on a rerun.

I re-derived it independently:

```
$ node tools/kernel-oracle-mutant-gauge/gauge.mjs
oracle-strength score: 41/41 = 100.0%  (1 equivalent excluded)
no surviving mutants: every planted bug is caught
genesis (source tree): 495579763a9963658ffb1c3d0f2ecf76c78101649bb91f2af153e7ab70ad6558

$ node tools/kernel-oracle-mutant-gauge/selftest.mjs
gauge selftest: 13 checks, 0 failures
```

Two details in that selftest are worth more than the 41/41 itself:
- **`T05 (provably equivalent) SURVIVES: the gauge does not over-kill`** — it asserts that a mutant which is
  *semantically equivalent* must NOT be killed. A mutation harness that only ever tries to look good will
  happily kill every mutant. This one is checked for false positives too.
- **`catalog genesis == current include/+tests/ tree hash (not stale)`** — the catalog cannot outlive the code.
- `flipping one verdict breaks the chain` — tamper-evidence is itself tested, not asserted.

It is **wired into CI** (`.github/workflows/ci.yml`, job *"verifier cells (mutant gauge, drift differ)"*):
`selftest.mjs` then `gauge.mjs --verify --strict`, alongside a `wasm-native-drift-differ` and a `seed-guard.sh`.
CI: **17 runs, 17 success, 0 failure.**

And the README has a section titled **"What is not true yet"**, which lists its own gaps — including:
> *"The seed's performance table is a claim, not a measurement. `bench/` is DRAWN; the only timing in this
> README is the one the landing page measures on your device."*
> *"No microcontroller has actually run it yet... the golden hash has been produced on x86-64, wasm32 and in
> JavaScript only."*
> *"'Register-resident' is the loop's shape, not a measured fact."*

An author writing "my benchmark table is a drawing" into their own README is doing the thing this whole fleet
series keeps finding missing. **Copy this shape.**

### The hole: the two invariants the entire design rests on are enforced by nothing

The design rationale is stated in the README's own words: *"never allocates memory, never touches floating
point and never calls the C library, so the same source runs on a desktop, in a browser tab... Because the
arithmetic is exact, a result can be checked by anyone, anywhere, by comparing one number."* The three promises
are **I1: no allocation**, **I2: integer-only, fused**, **I3: merge without consensus** — and the README claims
*"Each has a test that fails if it is broken."*

I1 and I2 have **no test**. Measured, not assumed:

- `grep -rniE '\b(float|double|malloc|calloc|realloc)\b' include/ src/` -> **5 hits, all inside comments**
  (e.g. `* Pure integer, libc-free, FPU-free, no malloc, header-only.`). Zero real uses. The purity claim is
  **true today** — and held only by convention.
- `grep -rniE 'malloc|calloc|realloc|float|double' tools/ --include=*.sh --include=*.py` -> **0 hits.**
  No static purity check anywhere in the tooling.

**Mutation (the part that matters).** I copied the repo to a scratch tree and injected one line into
`include/syz_arena.h` — a live `malloc(16)` and a `double`, in the kernel header:

```c
void *SYZ_MUTANT_LEAK = malloc(16); double SYZ_MUTANT_FLOAT = 1.5; (void)SYZ_MUTANT_FLOAT;
```

| layer | result on the `malloc` tree |
|---|---|
| documented suite | **`=== TOTAL: 7 suites, 219 checks, 0 failures (run.sh exit 0) ===`** |
| gauge self-test | **`gauge selftest: 13 checks, 0 failures`** |
| oracle strength | **`41/41 = 100.0%` — "no surviving mutants: every planted bug is caught"** |
| catalog chain | **re-verified green** against the mutated tree |

Every layer of an unusually strong verification apparatus is green while the kernel allocates heap memory and
declares floating point — the two properties the entire cross-platform byte-identity guarantee is derived from.
A single `float` on one architecture is enough to void the golden hash on another.

**And note *how* the one thing that did go red misled me.** Before I regenerated the catalog, the self-test
reported exactly one failure: `catalog genesis == current include/+tests/ tree hash (not stale)`. That is a
**staleness** detector, not a **purity** detector — it fires because the tree changed, not because an invariant
broke. A maintainer does the natural thing (`gauge.mjs --write`) and the chain verifies perfectly. Proven above:
after `--write`, 13/13 green with `malloc` still in the header.

**Fix is four lines** — the cheapest high-value fix in this report:
```sh
# tools/purity.sh — run first in ci.yml
! grep -rnE '\b(malloc|calloc|realloc|free)\s*\(' include/ src/
! grep -rnE '\b(float|double)\b' include/ src/ | grep -v '^\s*\*'
```
It would have caught both of my mutations. Note this is a *different kind* of check from the 41 logic mutants
already in the gauge — the gauge hunts behaviour, and a purity violation is a property of the source text.

**Generalisable lesson, and it is the sharpest one here:** *a hash-chained, genesis-bound, mutation-verified
receipt proves the code has not changed since the receipt was made. It says nothing about whether the property
being receipted was ever true.* The catalog binds a tree; it does not bind a claim. Any receipt over a
*property* (purity, licence, absence of a string, dependency count) needs a checker for that property, or the
chain is a very expensive way to certify that nobody edited the file.

---

## 2. `tensor-spline` — careful lattice math, an inert `.gitignore`, a stale wheel, and a metric that cannot fail

**What it is.** Parameterises NN weight matrices by control points on an **Eisenstein (hexagonal) lattice**
instead of independent floats. A 512x512 `nn.Linear` is 262,144 weights; this claims 16 control points.
Has a real `pyproject.toml`, a `superinstance.plugins` entry point, CI, and both a Python package and an npm
build. Genuinely the most substantial *math* in the unseen set.

**The math is correct — verified independently.** I ported `EisensteinLattice._build_lattice` to numpy verbatim:

- The docstring's ring formula `1 + 3R(R+1)` is **right**: measured 37 points within R=3 and 91 within R=5, matching exactly.
- For n = 1, 7, 16, 64, 256: origin is always first, points are distinct, max norm normalises to exactly 1.000000.
- It genuinely selects the N closest Eisenstein integers (Euclidean distance in Cartesian `(a - b/2, b*sqrt(3)/2)`
  equals the Eisenstein norm `a^2 - ab + b^2`, so the two orderings agree — no subtle bug there).

### Defect 1 — the `.gitignore` is a single line containing literal backslash-n, so it matches nothing

```
$ od -c .gitignore
0000000   _  _  p  y  c  a  c  h  e  _  _  /  \  n  *  .  p  y  c  \  n  *  .  p  y  o  \n
0000033
```

27 bytes: **one** line, `__pycache__/\n*.pyc\n*.pyo`, where the `\n` are two literal characters, not newlines
(shell `echo` without `-e`). Python confirms: `patterns git sees: ['__pycache__/\\n*.pyc\\n*.pyo']` — a single
pattern that matches no real path. Consequence, measured:

```
$ git check-ignore -v tensor_spline/__pycache__/spline.cpython-310.pyc
NOT-IGNORED          (git status is clean => it is committed)
$ git ls-files '*.pyc' | wc -l
15
```

**15 `.pyc` files are committed**, including `__pycache__/...pytest-9.0.3.pyc`. The clone reports clean, so the
decorative ignore rule is invisible. The file *contains the right words*, which is why a description-level read
passes it — a reviewer sees `__pycache__/` and `*.pyc` and moves on.

### Defect 2 — the committed wheel has drifted from the source, and ships the *old* half of a duplicated test suite

`dist/tensor_spline-1.0.0-py3-none-any.whl` is tracked. Unpacked and diffed against the working tree:

| module | wheel vs source |
|---|---|
| `spline_nd.py`, `mesh.py` | identical |
| `__init__.py`, `spline.py`, `low_rank.py`, `hierarchical_spline.py` | **DIFFER** |

The wheel is an **older build**: it predates every input-validation guard the source added —
`if in_features < 1: raise ValueError`, `if rank < 1: raise ValueError`, `if n_control_points < 2: raise
ValueError`, plus the whole `__all__` export list. Anyone installing the committed artifact gets a version that
accepts `rank=0` and `in_features=0` and then crashes. **Nothing in the repo checks that `dist/` matches source.**

There are **two divergent test suites** — `tests/` (new; explicit imports, no `torch.nn` at module scope) and
`tensor_spline/tests/` (old; docstring "Six required cases"). They are not copies (md5 differs on all three
shared filenames). This is not harmless: `pyproject.toml` has `include = ["tensor_spline*"]` and
`exclude = ["tests*"]`, so **the package ships `tensor_spline/tests/` (the old suite) and drops the new top-level
one** — and the wheel's bundled tests omit `test_spline_nd.py` and `test_mesh.py` entirely. The packaging config
selects the wrong half.

### Defect 3 — `compression_ratio` is a parameter-count identity, and no test anywhere checks that the layer works

The docstring headline: `compression_ratio(layer)  # 262144 / 16 = 16384.0`. That is `out*in / n_control_points`
— arithmetic on constructor arguments. It is **identical for every possible value of `control_values`, for every
lattice, kernel and basis**. It cannot fail. The suite agrees:

```python
def test_compression(self):  assert ratio > 1.0      # cannot fail for any valid construction
def test_num_params(self):   assert n > 0            # parameter count checked non-zero
def test_internal_materialization(self): assert W.shape == (16, 32)   # shape only
def test_basic(self):        assert y.shape == (4, 16)                 # shape only
```

Grepping both suites for `approx|fidel|reconstruct|rmse|mse` returns **exactly one line**:
`tests/test_spline_nd.py:153: assert layer.compression_ratio() == pytest.approx(16384.0)` — the identity again.

**So the README's central empirical claim — "You're replacing 262K parameters with 528 and *the layer still
works*" — is asserted and never tested.** No test compares a spline layer's output to the dense layer it
replaces. I measured what the expressible set actually is: `W[i,j] = sum_k K(d(i,j), lattice_k) * c_k`, so the
weights live in the **column space of a fixed `out*in`-by-`n` kernel matrix** — a fixed **n-dimensional linear
subspace** of the weight space. Best achievable fit (128x128, 16 control points, subspace = 0.098% of the space):

| target weight matrix | best possible rel. error | energy unexplained |
|---|---|---|
| random Gaussian | 0.9993 | **99.85%** |
| rank-1 outer product `a . b^T` | 0.9997 | **99.94%** |
| rank-64 (proxy for a trained layer) | 0.9996 | **99.91%** |
| smooth 2x2 Fourier | 0.5172 | 26.75% |
| smooth 3x3 Fourier | 0.3228 | 10.42% |
| smooth 9x9 Fourier | 0.2917 | 8.51% |

The rank-1 result is the surprising one: the basis is **radially symmetric about the origin on a linear grid**,
so it cannot represent a *separable* `a_i * b_j` function at all. Compression is real; it is a **spatial-smoothness
prior**, and the README is right to argue from smoothness — it just never measures whether the smoothness
assumption holds for the layer you actually compressed. (One correction to my own first pass, recorded because it
matters: I initially claimed the reshaped weight matrix has rank <= n. It does not — flattening a kernel-weighted
vector back to a square matrix produces a generally full-rank matrix. The correct statement is the fixed
n-dimensional *subspace* above.)

**Why another agent should care:** this is the highest-quality *science* in the unseen set, and it is still
protected by tests that check shapes. A lattice can be perfect and the compression claim can be unfalsifiable in
the same repository.

- CI: last run 2026-05-26 **green**; two failures on 2026-05-25 (earlier commits). Nothing since — **4.5 months stale**.
- `npm` job is `continue-on-error: true` — a fail-open job that cannot redden the build.
- `pyproject.toml` URLs point at `github.com/example/tensor-spline` — placeholder org, never updated.
- 17.8 MB of 18.8 MB "code" is vendored `npm/node_modules/typescript` (135/182 tracked files); the real code is ~30 KB.
- `review/AUDIT.md` is a peer README audit that scored **4/5**, crediting *"Honest Findings section +
  compression table make the tradeoffs clear"*. **`grep -c findings README.md` -> 0.** It graded a section that
  does not exist, and the compression table it endorsed is the identity above.

---

## 3. The `fleet-midi-*` family — eight musical doctrines, one byte-identical file

Eight repos, eight confident and *mutually incompatible* descriptions:

| repo | description |
|---|---|
| `fleet-midi-resonance` | Resonant frequency MIDI from agent harmonics |
| `fleet-midi-phase` | Phase-shifted MIDI from agent state offsets |
| `fleet-midi-cycle` | Cyclic patterns from agent state periodicity |
| `fleet-midi-live` | Low-latency live performance MIDI engine |
| `fleet-midi-feed` | Feedback/FMIDI from agent state feedback loops |
| `fleet-midi-collab` | Multi-user collaborative MIDI composition |
| `fleet-midi-pedagogy` | Music theory education through fleet MIDI |
| `fleet-midi-quantum` | Quantum state-inspired MIDI generation |

I fetched `lib/rust/src/lib.rs` from all eight through the API. **All eight are byte-identical: md5
`7939488d58`, 16 lines.** The entire mechanism is:

```rust
pub fn process(v: &[i8], base: u8) -> Vec<u8> {
    let mut n = vec![base];
    for &x in v {
        let last = *n.last().unwrap_or(&base);
        n.push(if x == 1 { last + 4 } else if x == -1 { last.wrapping_sub(4) } else { last });
    }
    n
}
```

A random walk in +/-4 semitones from a seed. No harmonics, no phase, no periodicity, no feedback, no
collaboration, no quantum anything. **The descriptions are the only thing that differs between the eight repos.**

### The polyformalism claim, and the command that does not exist

`fleet-midi-resonance`'s README leads with:

> *"That command runs the same ternary->music mapping **verified across 6 languages: Python, JavaScript, Go,
> Rust, C, and C++**. The output never changes because the mathematics doesn't change"*
> ```bash
> python3 lib/engine.py
> ```
> `[1, 0, -1, 1, 0, -1, 1, 1] -> [60, 64, 64, 60, 64, 64, 60, 64, 68]`

- `python3 lib/engine.py` -> **`can't open file ... No such file or directory`**. The file was never committed.
- Count of `.py|.js|.go|.c|.cpp|.ts` files in the repo: **0**. The "6 languages" have **n=1** implementation.
- The lone `#[test] fn same_output()` asserts the literal `vec![60,64,64,60,64,64,60,64,68]` — which is the same
  literal printed in the README. **It compares a value against itself, in the file that defines it.** There is
  nothing to cross-check against, so "the output never changes" is unfalsifiable.
- CI: **0 workflow runs. No CI at all.**

To be fair: the arithmetic is *correct* — I traced the walk by hand and it does produce exactly the README's
9-element output from 8 inputs (the 9th is the seed, so 8->9 is the seed plus one step per input, not a bug).
The defect is not the maths. It is that a cross-language identity claim is made in prose with zero
cross-language evidence, and the one test that exists is self-referential.

### 98.8% of each repo is committed cargo build output

```
total tracked:  96 files, 9,508,041 bytes
under target/:  87 files, 9,396,200 bytes      (.gitignore = *.log, .env, .DS_Store — no target/)
```

Full `target/debug/` trees: `.o` files, `.rlib`, `.rmeta`, `dep-graph.bin`, `query-cache.bin`, and
`invoked.timestamp` — committed in eight repos, in two different build snapshots. (Same family as
`substrate-attest-rs` at 430/434 build output, but here it is the *majority of the repository*.)

**Why another agent should care:** the fleet's signature doctrine is polyformalism — one claim, many languages.
Here that doctrine is *asserted eight times over* and *implemented zero times over*. A reader scanning repo
descriptions would reasonably conclude the fleet has eight distinct musical mechanisms.

---

## 4. `tzpro-agent` — a real boat, a genuinely good doctor, and an e2e suite pytest cannot see

**What it is.** The largest unseen repo by file count: a "boat agent" platform with an **NMEA GPS serial->TCP
bridge**, a bathymetric sounder analyser, tide/bathy contour preprocessing, a screenshot capture daemon, a
FastAPI LAN dashboard, a **DPAPI key vault**, and `pystray`. 155 source files, Windows-targeted
(PowerShell, `.bat`, scheduled tasks) but cross-platform enough to import on Linux.

**Positive, and verified by running it.** `doctor.py` is a real 9-check health tool that works:

```
$ python3 doctor.py check
  [FAIL] bridge:tcp:6006      nothing listening on 127.0.0.1:6006
  [FAIL] vault:roundtrip       vault round-trip failed: OSError: [Errno 122] Disk quota exceeded
  [OK  ] capture:daemon       STOPPED (no stampfile; ...)
  tzpro-agent doctor: 1/9 healthy
```

It is **properly fail-closed** — real exit code **1** with 8 failures (`return 0 if all(r.ok ...) else 1`). My
first read took the exit status off a `tail` pipe and saw 0; the tool was right and I was wrong. It also makes
an explicitly *informational* check honest rather than fake: `check_capture_daemon` returns `ok=True` for a
stopped daemon **and says why in the source** — *"'STOPPED' is not necessarily an error because the captain may
be at the dock with TZ Pro off. So this check reports info, ok=True"* — while still reporting true state in the
detail string. That is the right way to have a non-failing check. (Minor: the summary tallies it as "healthy",
so the headline `1/9 healthy` counts a check the author explicitly says is not a health check.)

### The gap: 13 test-looking files are hidden from pytest, and the only CI run in the repo's history is a bot

- **15** pytest-collectible test files exist, containing **61** test functions in `tests/` alone.
- **13** files are named like tests but are prefixed `_`, so pytest's default `test_*.py` / `*_test.py` patterns
  skip them **silently** — including **`scripts/_test_phase1_e2e.py`** (the end-to-end test),
  `scripts/_test_capture_daemon.py`, `scripts/_test_providers.py`, `scripts/_test_schema.py`, `scripts/_test_tray_app.py`,
  and `tests/_test_memory_integration.py`.
- Of the 10 files in `tests/`, only **2** are collectible (`test_offline_llm.py` 25 fns, `test_signal_fusion.py`
  36 fns). The other 7 are `_`-prefixed scripts; `run_canary.py` matches nothing.
- There is **no `pytest.ini`, `setup.cfg`, `tox.ini` or `pyproject.toml`** in the repo, so nothing overrides the
  collection patterns.
- **CI history: 1 run, "success", named `Graph Update: pip in /. #1462301577`.** That is a dependency-graph bot.
  **No test has ever run in CI.**
- `_test_cuda.py`, `_test_florence.py`, `_test_import.py`, `_test_voice_catch.py` at the repo root are the same
  pattern — named as tests, invisible to the runner.

**Why another agent should care:** this is the one repo in the shortlist where a working test suite plausibly
already exists and simply is not wired up. The e2e layer is written and shadowed. Un-shadowing 13 files
(renaming, or one `python_files` setting) is a very cheap recovery of real coverage.

---

## Cross-cutting: three failure shapes, all new this round

1. **A property that is only ever asserted in a comment.** `Syzygy` holds two load-bearing purity invariants
   by convention; nothing in 219 checks, 41 mutants, 13 self-tests or CI notices when they break. *Grep for the
   forbidden token as a test, not as a review step.*
2. **A receipt that binds a tree, not a claim.** Hash-chained, genesis-bound, mutation-verified integrity is
   real and worth having — and it certified a kernel that called `malloc`. Chain the **property checker**, not
   only the file.
3. **Descriptive divergence without substantive divergence.** Eight repos, eight doctrines, one md5. A README
   audit scored 4/5 by crediting a section that does not exist. Both are invisible to any scan of descriptions
   or file counts — only a *content* comparison across the family exposes them.

**Cheap detectors worth adding to the standing toolkit**
- `od -c .gitignore` — a one-line `.gitignore` with literal `\n` is invisible to `cat` and defeats `git check-ignore`.
- `git ls-files | grep -cE 'target/|node_modules|__pycache__'` — catches vendored and build-output mass.
- Unpack any committed `dist/*.whl` and diff it against the working tree; a tracked build artifact that has
  drifted is a supply-chain finding.
- For a family of same-shaped repos, hash one file across all of them: `md5sum` over a fixed path, repo by repo.
  Identical hashes across N descriptions is the whole finding in one command.
