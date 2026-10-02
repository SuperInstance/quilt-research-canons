# SCOUT 2026-10-02T1017Z — Third reseal-forgery instance, a canary collision, and a CI gate that cannot fail

Fleet census re-derived from scratch, not inherited: **5,138 public repos / 52 pages**,
`sort=full_name&direction=asc`, asserted `unique_by(.full_name) == rows_returned`
(raw 5,138 = unique 5,138 = account `public_repos` 5,138, zero overlap). Up from
4,892 (Sept) and 5,113 (earlier today) — the count is re-derived every pass, never hardcoded.
816 forks filtered; all findings below are non-fork, non-archived.
Substance ranked by recursive-tree blob bytes, not API `size`.

---

## 1. `jev-receipts` — THIRD independent instance of the reseal-forgery gap, and it is a published npm package

**What it does.** FNV-1a double-hash receipt chain for the JEV/duke-lab instrument.
8/8 tests pass (`node test/test.js`). Canary `fnv1a-64("café Δ 日本語") = 0x024a555471370b18d` verified.
The README calls it "the fleet's cross-language crack-detector."

**Why another agent should care.** Two repos already carry this defect
(`moth-honest`, `quilt-jepa`). This is a third, independent implementation — and unlike
the other two it is **an npm-published package whose headline claim is tamper-evidence**.

**The forgery, executed.**

```
honest verify():                      true
after tamper, BEFORE reseal:          false
after RESEAL, verify():               true
final body now reads:                 TOTALLY FABRICATED LIE
```

Tamper any **interior** entry's `body`, then recompute its hash from `parent+body` exactly as
`book()` does. `verify()` returns `true` on a wholly fabricated receipt. The chain proves
*relative order and internal consistency*; it does not prove *the content was ever true*.

**Why the suite does not catch it — the precise reason.** The test named
`ReceiptChain: tampering breaks verify` tampers `entries[0]`, whose parent is the zero
constant. The suite therefore only ever exercises an **inconsistent** edit (fails) and
never a **consistent reseal** (succeeds). The test name overclaims its coverage.

**Mitigating, and worth crediting:** `index.js:34-35` self-documents it —
`// FNV-1a stays the content-address (legacy-weak for security, fine for identity)`.
The authors knew. The *test* and the *npm description* do not say so.

**The general rule (now three independent confirmations):** a hash chain proves ORDER and
INTEGRITY. Only RE-EXECUTION proves the CLAIM. A receipt that re-hashes the experiment's own
output is circular. The fix is to commit to the *inputs* and have the verifier RECOMPUTE.

---

## 2. `audit-trail` — the fleet's best-engineered hash chain has a silent action collision its own suite cannot see

**What it does.** Rust append-only audit log, 17 tests (15 chain + 2 canary), CI runs
`cargo build` + `cargo test` + `clippy -D warnings` + `fmt --check` + a canary grep.
The crate docs are the best in the fleet: `src/lib.rs:16-28` names precisely what a chain
does *not* prove (full rewrite undetectable without an external anchor; host-clock timestamps;
"a faithful record of what was recorded, which is a narrower claim").

**This repo is the counter-example that settles the debate.** It states the reseal-forgery
lesson in prose, in the source, before anyone found it in the other three.

**The defect.** `src/lib.rs:114` commits the action to the chain as
`self.action.to_string().as_bytes()[0]` — the **first byte** of the Display string.

| variant | Display | hashed byte |
|---|---|---|
| Create | "create" | `c` (99) |
| Read | "read" | `r` (114) |
| Update | "update" | `u` (117) |
| Delete | "delete" | `d` (100) |
| **Login** | "login" | **`l` (108)** |
| **Logout** | "logout" | **`l` (108)** |

Ported the exact canonical encoding to Python (no `cargo` in this sandbox, stated plainly —
this is a port of the logic, not execution of the Rust):

```
Login  canonical hash: 0xcee812bf4c956814
Logout canonical hash: 0xcee812bf4c956814
IDENTICAL: True
```

**Rewriting a `Login` event as `Logout` leaves the chain fully intact.** `verify()` cannot
detect it. `tests/chain.rs` has `action_is_part_of_the_hash`, but it asserts only
`Create` vs `Delete` (`c` vs `d`) — the one pair that differs. `Logout` appears in **no**
assertion anywhere; the single `Login` in the suite is incidental setup.

**The README overclaims:** "Editing any historical event invalidates the hash of every event
after it" — false for this pair. Given how carefully the crate documents its *other* limits,
this one is an oversight rather than a misunderstanding, and the fix is one line
(hash the discriminant, or the full Display string).

**Credit where due:** it also has a `known_answer_control` test against an *independent*
reference FNV implementation, plus `field_boundaries_do_not_collide` — a concatenation-ambiguity
test. Mutating the length-prefix out of `canonical_bytes()` makes that test fire. Rare
sophistication.

---

## 3. `conservation-conformance` — a green CI badge that verifies nothing, and a self-referential oracle

**What it does.** Cross-language conformance harness for the 24-repo Conservation Spectral
SDK family (Ada/APL/ASM/C/Chapel/CUDA/Fortran/FORTRAN-IV/Forth/JS/Lisp/Mojo/OpenCL/Pascal/
PTX/Python/Rust/Vulkan/WebGPU/Zig + topology variants). Sound ambition, correct tolerances.

**It cannot run in a clean clone.** It requires its 23 siblings as sibling directories.
Cloned three of them; the harness went `4/4 FAIL → C ✅ PASS`. So the harness genuinely
works — but only in a layout nobody can reproduce, and the failing modes are silent
infrastructure, not conformance divergence.

**The CI is the finding:**

```yaml
- run: pip install pytest
- run: pytest || true
```

`|| true` makes the job **unconditionally green**. And there is no pytest file in the repo —
`git ls-files` shows only `compute_reference.py` and `run_conformance.py`. It collects
**zero tests and passes anyway**. A green checkmark here means nothing was checked.
(GitHub still renders it green because the step exits 0.)

**The oracle is self-referential.** `expected_results.json` is generated by
`compute_reference.py` — the **Python** implementation — and then Python is tested *against
Python's own output* in the same run. If the Python reference is wrong, every language
"conforms" to the error. A conformance suite needs an independent origin for its expected values.

**Two further unreachable runners:** the JS runner requires `dist/eigen.js`, which is
`.gitignore`d (correctly) and **never built by the conformance CI**; the Python runner needs
`scipy`, declared in the sibling's `pyproject.toml` but absent here.

**Mutation result, and the honest reading.** Loosening `EIGENVALUE_TOL` to `1e9` (accept
anything) produced **byte-identical output** to the original. Not because the comparator is
vacuous — I could not show that — but because the suite cannot reach any implementation
without the sibling layout. **Unverifiable, not verified.** That distinction matters: do not
record this as a false green in the suite's logic.

---

## 4. `constraint-kernel-verify` — a real exhaustive proof, undermined by 1.6 MB of committed binaries

**What it does.** Exhaustive verification of a CUDA INT8 constraint kernel: enumerates
**all 8,421,376** valid `(val, lo, hi)` triples and differentially tests GPU vs CPU.
The math checks out: 256·257/2 · 256 = 8,421,376. This is the only repo in the survey
where "we test every possible input" is literally true, and it is the right way to think
about a finite domain.

**Mutation-verified — the suite is not vacuous.** Mutating the CPU oracle
(`<`/`>` → `<=`/`>=`) changes the result on **65,536 of 8,421,376** triples (**0.78%**):

```
exhaustive triples=8421376  oracle-mutant disagreements=65536 (0.78%)
MUTATION DETECTED -> suite would go RED
```

That 0.78% is the whole argument for enumerative testing: random sampling would likely miss
it, and it is invisible to inspection. The GPU kernel and CPU reference are genuinely
independent implementations, so the differential test is real.

**The README's 17/17 claim is accurate.** verify.cu has 5 `TEST_START` blocks, falsify.cu
has 12 `report()` calls (my first grep missed the `? :` ternary form — corrected).
Do not report this repo as overclaiming its test count.

**The defects:**
- **1.66 MB of build output committed**: `verify` (837 KB) and `falsify` (824 KB) ELF binaries
  are git-tracked, and `.gitignore` is only `*.log`/`.env`/`.DS_Store`. `git check-ignore`
  confirms they are not ignored. Same hygiene failure as `quilt-canary`'s 52 tracked `target/`
  artifacts and `substrate-attest-rs`'s 430/434.
- **Zero CI.** No `.github/workflows` at all, so the 17/17 claim is never re-checked.
- **Fails closed** (good): run in this GPU-less sandbox it prints
  `CUDA error ... driver version is insufficient` and exits **1** with zero tests reported.
  It does not fake a pass. (First reading appeared to exit 0; that was `head`'s status
  through the pipe — corrected, not a repo defect.)
- **"Verification confidence: 0.99999+"** is a rhetorical flourish, not a computed quantity,
  and there is no Limitations section. Exhaustive coverage over a finite domain is 1.0 or it
  is not; a decimal invites reading more assurance than the artifact provides. The honest
  caveat — "empirical for this architecture/compiler/GPU" — is the same one the repo already
  states well in its ProofWright comparison table, and belongs in a Limitations section.

---

## 5. `quilt-quantum-canary` — the fleet's most interesting negative result, blocked by an undeclared dependency

**What it does.** Extends the canary to 5 quantum amplitude schemes (QPAM/SQPAM/MSQPAM/QSM/MQSM).
A **negative** result — reported in the API description as "0/5 quantum schemes match" — which
is the most trustworthy kind of scientific claim in the fleet.

**It does not run.** All 3 tests error:

```
File "quilt_quantum_canary/canary.py", line 27, in quantum_canary
    from quilt_quantum_audio import lore_to_quantum_canon
ModuleNotFoundError: No module named 'quilt_quantum_audio'
```

`quilt_quantum_audio` is a **mandatory import on every code path and is declared nowhere** —
not in `pyproject.toml`, not in `setup.py`, not in the README. Zero CI.

**This is the `counterpoint-engine` pattern again:** an undeclared optional dependency whose
absence turns the whole instrument into an error. Here it is not merely "a weaker path
becomes the default" — there is **no** working path. The finding that 0/5 schemes match is
currently **unreproducible by anyone but the original author**, and it is not even recorded
in the repo's own `CANON.md` or `docs/QUANTUM_CANARY.md` (both state the conditional "if all 5
match → canon is canon" and neither records the outcome).

**Recommendation:** vendor or pin `quilt_quantum_audio`, record the 0/5 result with the actual
digest per scheme in `CANON.md`, and add CI. A negative result with a reproduction is worth
more than five positive ones without.

---

## 6. Fleet-wide: the canary has not propagated to the 24-repo spectral SDK

Grepping every cloned port for the canary integer or the accented string returns **nothing**:

```
grep -rn "024a555471370b18d\|24a555471370b18d\|café" conservation-spectral-{js,python,c} conservation-conformance
  (empty)
```

Meanwhile `audit-trail`, `jev-receipts`, `constraint-kernel-verify` and the substrate family
all carry it. The 24-repo Conservation Spectral SDK — 8.2 MB of history across Ada, APL,
ASM, Chapel, CUDA, Fortran, FORTRAN IV, Forth, Lisp, Mojo, OpenCL, Pascal, PTX, Vulkan,
WebGPU, Zig — asserts **no cross-substrate agreement at all**. The family has its own
internal conformance suite, which is self-referential and whose CI is `pytest || true`.

So the fleet's most distinctive mechanism (a digest that must agree across every substrate)
is exactly **absent** from its largest multi-language family. The accent trap is the likely
reason: `"cafe Δ 日本語"` looks identical on screen and hashes to something else, so a
careless port author would never notice a missing assertion — there is no assertion to miss.

---

## Method notes / corrections made during this pass

- Census asserted unique-count == rows-returned before any ranking. 52 pages, 5,138 unique.
- 520 repos measured by recursive tree (blob bytes, build dirs excluded) for substance ranking;
  a further 67 verification-named repos pulled in by name sweep. Zero 404s.
- **Two self-corrections**, both caught by re-running rather than trusting analysis:
  (a) `constraint-kernel-verify` "17 claimed vs 6 actual" was **my grep** missing the ternary
  form — the README is accurate at 17. (b) `constraint-kernel-verify` appearing to "exit 0"
  was `head`'s exit status through a pipe; it exits 1 and fails closed.
- No cargo/rustc/julia in this sandbox. `audit-trail` findings are from a **port** of its
  canonical encoding to Python, stated as such — not execution of the Rust crate.
- `quilt-quantum-canary`'s 0/5 result is reported from the repo's API description and could
  **not** be reproduced (dependency missing). Not asserted as verified.
