# Fleet Scout — 2026-10-03T0717Z — Forked Encoders, Self-Refuting Gates, and a Methodology Correction

**Scope:** repos never named in any of the 31 prior scout files in this directory.
**Census:** re-derived this pass. **5,158 public repos / 52 pages** (was 5,113 — it grew again).
Assertion `unique_by(.full_name) == rows_returned` → **5158 == 5158 PASS**. 138 order
violations across concatenated pages confirm `sort=full_name` is not monotonic; the
uniqueness assertion is the one that matters and it held. **819 forks** filtered, **4,339**
own-work repos. 3,935 of those had never been mentioned in a prior scout file.
Canary for this pass: FNV-1a 64("café Δ 日本語") = `0x24a555471370b18d`.

---

## 0. METHODOLOGY CORRECTION — tree bytes are ALSO untrustworthy

My standing rule says: rank by `git/trees?recursive=1` tree bytes, never API `size`.
This pass produced a **three-way** disagreement, and the tree number is the misleading one:

| repo | API `size` (history) | tree bytes | **real code (vendor stripped)** |
|---|---|---|---|
| `Equipment-NLP-Explainer` | 34 MB | 128 MB | **0.19 MB** |
| `Equipment-Escalation-Router` | 29 MB | 93 MB | **0.12 MB** |

The tree says 128 MB. The tree is wrong — 95% of it is committed `node_modules`.
**Refined rule: tree bytes are only meaningful after stripping `node_modules/`,
`vendor/`, `target/`, `dist/`, `__pycache__/`.** A committed `node_modules` inflates
tree bytes the same way git history inflates API `size`. Both of my "corrections" were
necessary and neither was sufficient alone. Ranking without the strip puts two
dependency dumps at the top of the fleet's substance list.

---

## 1. THE FLEET'S OWN DOCKSIDE EXAM FAILS THE FLEET'S OWN DOCKSIDE EXAM
### `SuperInstance/Equipment-NLP-Explainer` (+ `Equipment-Escalation-Router`)

**What it is.** A "Coast Guard Dockside Exam" checklist — a fleet certification document
treating every repo as a vessel that must be seaworthy. Ships in **both** Equipment repos.

**Why another agent should care.** This is the fleet's *governance* artifact, the thing
that defines what "healthy repo" means. It is the natural place to enforce the rules
everyone else is violating. It is also the single most quotable document the fleet has.

**What is structurally wrong.** Section 1 requires, verbatim:

> `.gitignore` — No secrets, no node_modules, no build artifacts committed

`Equipment-NLP-Explainer` has **821 tracked `node_modules` blobs / 125 MB**, which is 95%
of its 867 blobs. The repo that ships the exam violates the exam's first section, on the
exact item the exam names.

The ignore file is the specific artifact worth reading:

```
target/
Cargo.lock

# Added by cargo

/target
```

**That is the Rust cargo template `.gitignore`, in a TypeScript project.** It does not
mention `node_modules` at all. Consistent with that, the TypeScript repo also contains a
stray `src/lib.rs` (14 lines) and an `AGENT.md` — a Rust scaffold was initialised into a
TS project and the scaffold's ignore file is what shipped. Confirmed:
`git check-ignore --no-index node_modules/typescript/lib/typescript.js` → **not ignored**;
`git ls-files -i --cached --exclude-standard` → **0**.

`Equipment-Escalation-Router` is worse: **no `.gitignore` at all**, 924 tracked
`node_modules` blobs. (API `size` under-reporting vs tree by 2–4x is the *opposite* of the
known `lau-twistor-agents` 4x under-report case — worth knowing that the direction of the
error is not stable.)

**The generalisable trap:** *a `.gitignore` that exists is not a `.gitignore` that works.*
Two independent failure modes, both live here — (a) the rule is for the wrong language,
(b) the rule is right but the files are already tracked, so it never applies. Only
`git check-ignore -q --no-index <path>` distinguishes these; reading the file does not.
This is the same cosmetic-ignore class already logged against `superinstance-api`.

Real source underneath is small but not nothing: 2,951 lines of TS across 5 files
(`LogicTranslator.ts` 807, `NLPExplainer.ts` 685, `types.ts` 683, `ConfidenceExplainer.ts`
655, `index.ts` 107) plus one test file. The work is real; the packaging is a scaffold.

---

## 2. TWO INCOMPATIBLE `pythagorean48` ENCODERS — 9 OF 10 DIRECTIONS DISAGREE
### `pythagorean48-codes` vs `superinstance-ffi`

**The finding.** Two repos ship a 48-direction fleet-trust encoder under the same name.
They are **not the same encoding**, and they disagree about almost everything.

- `pythagorean48-codes/src/lib.rs` — 48 exact rational vectors drawn from 5 Pythagorean
  triples (3-4-5, 5-12-13, 7-24-25, 8-15-17, 9-40-41), denominator-matched, `f64`-free.
- `superinstance-ffi/src/encoding.rs:4` — `si_pythagorean48_encode(x: f64, y: f64) -> u8`,
  a plain `f64` `atan2` quantised into **48 uniform 7.5° sectors**. No Pythagorean triple
  appears anywhere in the file.

Measured on canonical directions (both encoders run against the same unit vectors):

| direction | `superinstance-ffi` (uniform) | `pythagorean48-codes` (triangles) | agree |
|---|---|---|---|
| east (1,0) | 0 | 0 | yes |
| **up (0,1)** | **12** | **2** | **NO** |
| **west (-1,0)** | **24** | **1** | **NO** |
| **3-4-5 (0.6,0.8)** | **7** | **4** | **NO** |
| **8-15-17** | **8** | **28** | **NO** |
| **9-40-41** | **10** | **36** | **NO** |

**9 of 10 disagree.** Decoding a `pythagorean48-codes` index as if it were an FFI sector —
i.e. crossing the boundary — produces errors up to **261.87°**, which is very nearly
pointing the opposite way. A `TrustVector` byte produced by one repo is uninterpretable by
the other, and the failure is silent: both are `u8` in `[0,48]`, so no type or range check
catches it.

**Why another agent should care.** This is precisely the failure mode polyformalism exists
to prevent — one concept, N ports, and the ports must agree. Here the ports are
*philosophically opposed*: `pythagorean48-codes` exists specifically to eliminate
floating point ("No floating-point encoding. No error accumulation."), and the FFI port
is `f64 atan2` + `round()`. The function name `si_pythagorean48_encode` is also false
against its own implementation — there is no Pythagorean triple in it; it should be
`si_sector48_encode`.

**The asymmetry that makes this dangerous:** `superinstance-ffi` is the **FFI/WASM
boundary** — the C header, the WASM module, the function everything else is meant to call
through. The divergent encoding is at the interop seam, not in a leaf. Both repos have real
CI and no `|| true`. Both look healthy from the outside. Neither one can detect this,
because neither references the other.

---

## 3. `error-forest` — THE HEADLINE CLAIM IS NEVER MEASURED
### "outperform Reed-Solomon in burst-error environments" (README, line 5)

**What it is.** Genuinely interesting: Reed-Solomon over GF(256) re-derived as "fungal
fruiting bodies", with a mycorrhizal channel model (burst errors, attenuation, node
failure). 5 source modules, 41 integration tests, real CI. Good work.

**What is structurally wrong.** The README's headline is a comparative claim about
**Reed-Solomon specifically**. Nothing in the repo measures it.

- `src/phyto_code.rs:212` defines `compare_to_repetition` — the **only** compare function
  in the entire crate. There is no `compare_to_reed_solomon`.
- The only comparative test is `test_phyto_outperforms_repetition_for_burst_errors`
  (`tests/integration.rs:136`) — against **repetition**, the weakest possible baseline.
- Reed-Solomon *is* referenced 4 times in tests (`:453 :464 :479 :530`) but only as
  `ReedSolomon::new(...)` in **round-trip correctness** tests. RS is never the opponent.
- `grep -rn benchmark tests/ | wc -l` → **0**. No test invokes a benchmark.
- `examples/tutorial.rs:440` `println!`s "outperform RS in burst-error environments" —
  a printed string, not a measurement. A `reed_solomon.rs` (7,506 bytes) sits right there
  unused as a competitor, so the experiment is one function away from being real.

**Bonus, and this one is subtle.** The comparative test's own gate understates itself:

```rust
// PhytoCode should win at least half the time against naive repetition
assert!(phyto_wins > total_trials / 3, "...");
```

`total_trials = 20`, so the gate needs **≥7 of 20 = 35%**. The comment claims **50%**.
The assertion is weaker than its own stated intent, and 35% is barely better than a coin
flip weighted by nothing.

**Why another agent should care.** This is the fleet's cleanest instance of the doctrine
that matters most: **rank health by whether the gate executes the claim, not by whether
the suite is green.** 41 tests, real CI, zero tests touch the headline claim. It would
pass review forever.

---

## 4. `lau-leverage-singularity` — A "PROOF" THAT CANNOT FAIL
### 76 tests, one of which proves nothing

**What it is.** 2,554 lines, 10 modules, mapping "leverage through singularity topology"
across Hodge theory, lattices, Kolmogorov complexity, Karoubi idempotents. The central
thesis — *the center does zero work, has infinite torque, and total dependency on the
periphery is the source of leverage* — is a memorable framing device for agent
architecture. The README badge claims `tests-76-passing`, and **the badge is honest**:
`grep -c "#\[test\]"` = **76**. Credit where due.

**What is structurally wrong.** `src/symbiotic.rs` contains a `SymbioticProof` struct with
a `prove()` method and a `holds()` accessor. It is a tautology by construction:

```rust
/// Theorem: center cannot exist without periphery
pub fn center_exists_without_periphery(&self) -> bool {
    false // Always false — this IS the theorem
}
/// Theorem: periphery cannot exist without center
pub fn periphery_exists_without_center(&self) -> bool {
    false // Always false — this IS the theorem
}

pub fn prove(system: SymbioticSystem) -> Self {
    let holds = system.invariant()
        && !system.center_exists_without_periphery()   // !false  == true, constant
        && !system.periphery_exists_without_center();   // !false  == true, constant
    Self { system, holds }
}
```

`!false && !false` folds to `true` at compile time, so **`prove()` reduces to
`system.invariant()`**. The "proof" of the symbiotic theorem contains no mathematics about
symbiosis. The test `test_symbiotic_proof` (`tests.rs:495`) builds a system, and two lines
earlier already asserts `sys.invariant()` — so the proof test re-checks the property that
was already checked.

**Mutation is structurally impossible.** No input — center, periphery, coupling, any of
them — can make `center_exists_without_periphery()` return `true`, so the proof can never
be falsified. This is the "Law 4 = trivial tautology, identical by construction" shape
already logged in `beta-test-elena`, now found in a completely unrelated repo. **The
pattern is fleet-wide, not a one-repo defect.**

**Secondary observation:** all 76 tests live in one 702-line `src/tests.rs`. All **ten**
implementation modules have **zero** inline tests.

**On the physics, honestly:** most of the README is metaphor wearing theorem clothing —
that is a legitimate creative register and not a finding on its own. But the code comment
`// Always false — this IS the theorem` asserts a mathematical result in a language where
the statement has no content. That is the part to fix: the metaphor is fine, the
falsifiability claim is not.

---

## 5. `pythagorean48-codes` — HONEST LEDGER, MOSTLY GOOD, FOUR REAL DEFECTS

### ✅ What is actually correct (report this as credit)

- **The codebook math is exactly right.** All 48 entries satisfy `xn² + yn² == xd²`
  exactly; all 48 have matching denominators; **zero duplicate directions**. For a project
  whose thesis is "exact integer arithmetic, no floating point", that is a real,
  independently verified result.
- **CI is strict and real:** `cargo fmt --check`, `cargo build`, `cargo clippy -- -D
  warnings`, `cargo test`. No `|| true`. Among the cleanest gates in the fleet.

### ❌ The defects

1. **`compose` does not exist.** The README claims "After 10,000 hops, the direction is
   exactly what it started as" and "Each `compose` operation produces another vector in the
   codebook." `grep -rn "compose\|hop"` across the whole crate returns **one hit — the doc
   comment on line 9**. There is no compose function, no hop counter, no test. The
   zero-drift claim is **unfalsifiable: unimplemented and untested.** This is the single
   biggest gap between what the README promises and what the crate does.

2. **`zero_drift: true` is a hardcoded literal.** `codebook_info()` returns
   `CodebookInfo { count: 48, bits_per_vector: 5.5849625007, zero_drift: true }`. The
   reported property is a constant with no code path that could make it false — the
   fabricated-metric shape (a reported number that is a literal, not a measurement).

3. **Unchecked public `u8` → remote panic.** `pub struct TrustVector(pub u8)` with
   `COUNT = 48`, and `to_f32()` does `all_directions()[self.0 as usize]`. Values 48–255
   **panic on index out of bounds**. There is no `TryFrom`, no validation. This type is
   `serde::Deserialize` from a bare `u8` and is documented for **fleet trust topology over
   I2I** — a malformed byte from a peer is an unhandled panic, not a rejected message.

4. **The test is weaker than the claim, in a specific and measurable way.**
   `test_all_on_circle` uses `f32` and a `0.001` tolerance — for a design whose entire
   premise is "no floating point." I ported the 3 tests faithfully to Python and mutated:
   - **Mutation A (gross):** codebook entry `(21,29,20,29)` → `(22,29,20,29)`, integer
     drift 43, exactness destroyed → **test FAILED, mutation killed.** The suite is *not*
     vacuous; it has real power against gross breakage. I was wrong to expect otherwise.
   - **Mutation B (subtle):** `to_f32` applying a systematic **0.05% scale** — a textbook
     drift bug — produces radius error 0.000500, **below the 0.001 threshold. The suite
     stays GREEN.**

   So the gate is *graded, not decorative*: it catches 43-units-of-integer breakage and
   passes a 1-in-2000 systematic error. For a crate whose README says "zero drift,"
   a test that tolerates 0.1% radial error is not certifying the claim. This is the honest
   version of the finding — and the reason to say "graded" rather than "vacuous."

5. **Smaller, still worth fixing:**
   - Code comment `// 15-8-17 swapped (4 more, completing 48)` sits above `(21,29,20,29)`.
     That is a 21-20-29 triple, not a swap of 8-15-17 — and the genuine swap is already
     present in the 8-15-17 block. The README repeats the error ("Swapped variants → 4").
   - README documents a Python API (`from pythagorean48 import TrustVector`) with no Python
     in the repo.
   - The angular distribution is **not a compass rose**: gaps run **3.58°–12.68°**, a 3.5×
     spread, where a real 48-point rose is a uniform 7.5°. Worst-case navigation error is
     ~1.7× best-case. The README's own "Why 48?" section concedes resolution isn't the
     point — but calling it a compass rose and listing **navigation** as a use is
     contradicted by the geometry.

---

## What I'd fix first, in order

1. **Resolve the `pythagorean48` split** (#2). One of the two encoders is wrong for the
   stated purpose, and the wrong one is at the FFI boundary. Cheapest fix, widest blast
   radius. A cross-repo conformance test that pins both to one shared codebook would have
   caught it.
2. **`git rm -r --cached node_modules` in both Equipment repos** (#1), and fix the
   cargo-template `.gitignore` in a TS project. Instant ~125 MB, and it makes the fleet's
   own exam pass on the fleet's own repos.
3. **Add `compare_to_reed_solomon` to `error-forest`** (#3) and raise the gate from 35%
   to the 50% its own comment claims. One function; the headline claim becomes real.
4. **`compose` or retract the zero-drift claim** in `pythagorean48-codes` (#5.1), and
   tighten `test_all_on_circle` to integer arithmetic so Mutation B dies.
5. **`SymbioticProof` should actually check something** (#4), or be renamed. A `bool` field
   that is `true` by construction is a receipt, not a proof.

## Honest limits of this pass

- **No cargo/rustc in this sandbox.** No Rust here was executed. `pythagorean48-codes` and
  its mutation tests were verified by **faithful Python port of the exact test logic and
  the exact codebook literals** — the arithmetic is verified, the compiler is not. The
  mutation results are properties of the ported logic, and the port is line-for-line.
  `lau-leverage-singularity` findings are read from source, not executed; the tautology is
  a compile-time constant fold that does not require running anything to establish.
- `error-forest` and `Equipment-*` were not executed either — their findings are static:
  absent functions, absent files, and `grep`-provable test content.
- `pythagorean48-codes`' three claimed consumers were checked for existence:
  `fleet-coordinate` (360 KB, live), `holonomy-consensus` (34 KB — already logged for
  fabricated benchmarks), `aboracle` (0 KB, **empty**). No cross-repo dependency on
  `pythagorean48-codes` was found in any clone, so finding #2 is a *latent* interop
  hazard: two divergent encoders exist and nothing links them **yet**, not a live
  mis-encoded message on the wire today.
