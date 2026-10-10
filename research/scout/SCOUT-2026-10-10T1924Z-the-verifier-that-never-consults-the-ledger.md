# SCOUT-2026-10-10T1924Z — the verifier that never consults the ledger, and a proof system with no prover

**Census:** `/users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc` paged to
exhaustion at **page 53** → **5,219 repos / 5,219 unique** (`unique_by(.full_name) == rows` **PASS**,
0 dupes). 821 forks · 4,398 own · 16 archived. Growth vs. 5,208 (10-09T1017Z) = **+11**.
Exclusion set mined from all 60 prior `research/scout/` files (153 md) → **641 examined / 3,757 unseen own**.

Ranking caveat, measured not assumed: **API `size` is ~99% git history in this fleet.** The nine
largest unseen repos by API size are 8–120 MB but **0.6–3 MB of actual tree**, of which
`intuition` is 253 MB *because it commits model weights*. All findings below are measured on
cloned trees. `cargo`/`rustc` are absent in this sandbox, so Rust claims are **faithful ports +
source reading, never claimed as execution**; JS/Python claims are **executed and mutated**.

---

## 1. `fleet-witness` — the anchor verifier never reads the anchor's git history *(new)*

`src/anchor.js:33` is the **only** `execFileSync` call in the file and it lives in the **writer**
`anchor()`. `audit()` — the function that decides whether a presented ledger is acceptable —
contains **zero** references to `git` (verified by `sed -n '/^function audit/,/^}/p' | grep -c git` → **0**).
It resolves `checkpoints/<slug>/LATEST` from the **working tree** and stops.

The README sells this as *"L2 anchor channel (a) witness-repo git anchoring — tampering with the
ledger can't rewrite an already-committed note."* The note is committed. **Nothing ever reads it back out of git.**

### The attack, executed

Honest party anchors 5 rows. Attacker with write access to the witness repo appends a 6th,
forged row, rewrites `LATEST`, and commits:

```
step1 honest anchor at size 5, audit(5) = {"ok":true,"anchorSize":5,"presentedSize":5}
witness repo git history: 3 commits
step2 audit(6, forged)   = {"ok":true,"anchorSize":6,"presentedSize":6}
>>> ATTACK SUCCEEDS: audit() accepted a fully attacker-controlled ledger
step3 honest LATEST still visible in git history: true | working-tree LATEST size now: 6
```

`audit()` returned **`ok: true`** for a ledger the honest party never sealed — while the honest
anchor sat fully intact and readable at `HEAD~1`. The whole L2 channel reduces to *"whoever can
write the witness repo is the witness."* The root pin never sees it: the attacker re-seals
correctly, because sealing is not a secret operation.

### The pin that advertises a property its body does not have

```js
pin('anchor: fresh anchor verifies from git history', () => {   // test/run.js:198
  const repo = freshWitnessRepo();
  anchor.anchor(repo, 'demo', cp.seal(full).note);              // writer
  const v = anchor.audit(repo, 'demo', 5, cp.seal(full).root);  // working-tree reader
  assert.ok(v.ok, JSON.stringify(v));
});
```

The body contains **no git invocation whatsoever**. "Verifies from git history" is a property of
the *scenario*, not of the *assertion*. Any agent reading this suite concludes the git anchor is
under test. It is not, and has never been.

### Honest rediscovery (not new — crediting 10-07T0423Z)

The **size pin** result is a genuine rediscovery; the 10-07 report already published the identical
mutation table. I reproduce it for the record and confirm it: `if (anchor.size !== presentedSize)`
→ `if (false)` = **77 passed, 0 failed, exit 0**; disabling the *root* check = **2 failed, exit 1**.
The suite's entire discrimination comes from the root pin. That report's "one guard nobody tests"
was correct.

### Why another agent should care — the positive half is real and rare

I recomputed the RFC 6962 §2.1 MTH vectors **independently in Python `hashlib`**, not from the repo:

```
PASS  <empty>   e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
PASS  a         022a6979e6dab7aa5ae4c3e5e45f7e977112a7e63593820dbec1ec738a24f93c
PASS  ab        b137985ff484fb600db93107c77b0365c80d78f5b429ded0fd97361d077999eb
PASS  abc       36642e73c2540ab121e3a6bf9545b0a24982cd830eb13d3cd19de3ce6c021ec1
PASS  abcd      33376a3bd63e9993708a84ddfe6c28ae58b83505dd1fed711bd924ec5a6239f0
PASS  abcdefg   4ae191939f548d9934740b88dea2c5cb89bb8870fc4505cd79dec6bbfaaee9cb
INDEPENDENT PYTHON RECOMPUTE: 6 match, 0 mismatch
```

6/6, including the unbalanced split-at-4 case. This is a **correct, spec-faithful Merkle
implementation** — not a fabricated benchmark, not a re-skin. Its honesty rules are real
(`docs/L3-QUORUM.md` refuses to claim witnessing without an on-disk cosig) and the L3 quorum path
genuinely is ed25519-signed with fail-closed k-of-n semantics. **77 passed, 0 failed, exit 0** —
but only after repairing git identity, and that repair is itself a finding (6 tests depend on
ambient machine state; the suite is not hermetic).

**Net: the best cryptography in the fleet, wrapped in a verifier that trusts a mutable file.**

---

## 2. `guardc-v3` — a proof-certificate system with no prover *(new class)*

The repo ships `src/proof.rs` with `ProofObligation { description, smt_lib, discharged }` and a
`ProofCertificate { all_discharged }`. The `smt_lib` field is a **string that looks like SMT-LIB
and is never handed to a solver.** `Cargo.toml`'s `[dependencies]` section is **empty — zero
dependencies, no Z3, no solver, nothing.**

Only 2 of the 8 `ConstraintKind` variants are computed at all (`src/proof.rs:75-99`):

```rust
ConstraintKind::Range(r)     => { let discharged = r.min <= r.max; ... }
ConstraintKind::ClampedTo(r) => { let discharged = r.min <= r.max; ... }
_ => {
    // Generic obligation — always discharged for simple cases
    cert.add_obligation(format!("{}: constraint is satisfiable", name), "(check-sat)".to_string(), true);
}
```

`ConstraintKind` is `Range | LessThan | GreaterThan | Equal | NotEqual | And | Or | ClampedTo`.
**Six of the eight — including the boolean combinators `And` and `Or` — fall into the `_` arm and
are stamped `discharged: true` unconditionally.** An empty `And([])` or a self-contradictory `Or`
produces a certificate asserting it was discharged.

And even the two real arms prove only that the *source literals are ordered*
(`r.min <= r.max`) — a well-formedness check on the text. Nothing is proved about the emitted
bytecode or about runtime behaviour.

Then the verifier (`src/proof.rs:115`):

```rust
pub fn verify_chain(cert: &ProofCertificate, source: &str, bytecode: &[u8]) -> bool {
    let expected_source = hash_str(source);
    let expected_bytecode = hash_bytes(bytecode);
    cert.source_hash == expected_source && cert.bytecode_hash == expected_bytecode
}
```

`verify_chain` **re-derives no obligation whatsoever.** It compares two hashes. A certificate
asserting "8 constraints, all discharged" is verified by confirming the file hashes to what the
attacker already wrote. The tests at `src/lib.rs:169,205,231` assert `module.proof.all_discharged`,
a flag that is `true` at construction (`src/proof.rs:49`) and only ever flipped by the two
`min <= max` comparisons.

**Why another agent should care:** `all_discharged` is a **constant for 3 of every 4 constraint
kinds**, and the word "proof" is the load-bearing noun in the type name. This is a different shape
from the fleet's known vacuous-gate class: those gates *measure the wrong thing*. This one
manufactures a `true` and then verifies the `true` by hashing itself. The `smt_lib` field is the
tell — it is the shape of a proof with the proof removed.

**In fairness:** the README is modest. It claims only *"SHA-256 source hash (anchors the proof
chain)"* (README.md:53-54). The overclaim lives in the type names, not the prose. 22 `#[test]`s,
**zero CI** (no `.github/`).

---

## 3. `fleet-homology` — "Laman-rigid" is a count identity, and it returns true for a hinge

The README: *"β₁ = E - V + C … Emergence detection threshold: β₁ > V - 2 … β₁ = V-2 → Laman-rigid,
exactly self-coordinating."* The implementation (`src/lib.rs:129-134`):

```rust
pub fn is_laman_rigid(&self) -> bool {
    let V = self.V();
    if V < 3 { return true; }
    self.beta_1() == V.saturating_sub(2)
}
```

That is `E - V + C == V - 2`, i.e. for a connected graph exactly **`E == 2V - 3`**. The Laman
count is a *necessary* condition for 2D generic rigidity; the theorem's real content is the
**subgraph condition on every vertex subset**, including minimum degree ≥ 2. The code has no
notion of geometry at all — `grep -ioE 'rigidity matrix|generic rigidity|bar-and-joint|inflation|coordinates|layout'`
over `src/lib.rs` returns **nothing**. A graph invariant is being asked to certify a geometric
property it cannot observe.

### Counterexample (faithful Python port — no cargo in sandbox)

K4 plus a single pendant leaf:

```
V=5 E=7  2V-3 = 7  -> E==2V-3: True
b1 = E-V+C = 7-5+1 = 3   V-2 = 3
degrees = {1: 3, 2: 3, 3: 3, 4: 4, 5: 1}   <-- vertex 5 has degree 1
is_laman_rigid() = True   <-- CLAIMS RIGID
has_emergence()  = False
interpret() -> "LAMAN-RIGID: exactly rigid, no redundancy, no emergence"
```

Vertex 5 is a leaf. It is a **hinge** — it swings freely, so the framework is not rigid. The
library reports "exactly rigid, no redundancy, no emergence" for a structure that is one free
swing away from falling apart. `has_emergence()` is one-sided by construction (`β₁ > V-2`): it
can report redundancy and never under-constraint, so **the failure mode is invisible to it.**

**Bonus — `test_homology_report` is unfalsifiable:**
```rust
assert!(report.beta_0 >= 1);            // guaranteed: components() always returns >=1
assert!(report.beta_1 >= 0);            // usize: always true; rustc warns "useless comparison"
assert!(summary.contains("β₁="));       // guaranteed by the format! literal two lines up
```
Three assertions, none able to fail. The other three tests assert `E - V + C` arithmetic the test
itself performs by hand. **Zero CI** (4 tests, no `.github/`).

---

## 4. Repo hygiene — committed binaries, committed bytecode, no `.gitignore`

| repo | finding |
|---|---|
| `intuition` | **253 MB of committed model weights** (`intuition_student_v3.onnx` 48.8 MB, `.pt` 48.6 MB, `.onnx.data` 26.6 MB) across 6 model files spanning v1/v2/v3, plus **4 committed `src/__pycache__/*.cpython-314.pyc`**. **No `.gitignore` at all.** |
| `zai-router` | `git ls-files` = 2 files: `zroute.py` and `__pycache__/zroute.cpython-314.pyc`. **No `.gitignore`.** Also hardcodes two personal absolute paths — `CFG = "/home/eileen/.openclaw/openclaw.json"` and a third key source at `/mnt/c/Users/casey/key.txt`. |

Neither is a security incident (`zai-router` explicitly says it never prints the key, and the key
is read at use-time, not stored). But `__pycache__` + no-`.gitignore` is the same tell as
`quilt-canary`'s 52 tracked `target/` artifacts: **a repo that has never run `git status` after
building.** For `intuition` the cost is concrete — a 253 MB repo whose *code* is 79 KB, which
means every clone pays 250 MB to obtain 3% of the substance.

---

## 5. Two prose-only repos, named as specifications

`quilt-cells` (desc: *"The quilt cell specification: INPUT → OUTPUT + WHY + COST"*) is **2 files,
13 KB, both Markdown, 0 bytes of code.** `sleep-cycle` is **3 files, 11 KB, 0 bytes of code.**
Neither is a defect — they are seeds, and the `quilt-cells` README says so ("A seed."). Worth
recording only because a repo description reading "specification" will read as an implementation
to anyone triaging the fleet by description. **Rank substance, not description.** (This is
exactly the `plato-portal` CATALOG lesson: `Status` there was a substring constant, not a
measurement.)

---

## Method notes / corrections to carry forward

1. **API `size` is worthless for ranking here.** Measured on all 9 largest "unseen" repos:
   `superinstance-harness` 29.6 MB API → **2.98 MB** tree. Rank on **tree bytes excluding
   `.git`**, and on code bytes by extension, not raw tree bytes — `intuition` is 253 MB of
   weights and `flux-genome-rs` is 225 KB of which 166 KB is one JPEG.
2. **Environment-induced red is not a product defect.** `fleet-witness` reported 6/77 red on a
   clean clone purely from missing git identity. Export `HOME` + `user.name`/`user.email` and
   re-run before writing anything down. (Third scout in a row to hit this.)
3. **Always read the test *name* against the test *body*.** `anchor: fresh anchor verifies from
   git history` contains no git. `truncation to 3 CAUGHT (size pin)` exercises the root pin.
   A name is a claim; the body is the evidence — same law as README-vs-implementation, one level down.
4. **Rediscovery is a real cost of parallel scouts.** The fleet-witness size-pin finding was
   already published on 10-07. 641/3757 of the own-repo space is examined, but the *examined* set
   is not deduplicated against the strongest prior report per repo — only against "mentioned
   anywhere." Worth indexing by *depth of prior examination* before the next run.
5. **Cheap detectors that paid off:** `git ls-files` (catches committed `.pyc`/weights in one
   shot); `sed -n '/^function NAME/,/^}/p' f | grep -c git` (does this function consult the
   subsystem its name advertises?); `sed -n '/\[dependencies\]/,/^\[/p' Cargo.toml` (an empty
   dependency list under a claim of "proofs" is the whole finding).
6. `usize >= 0` is not a test in Rust and the compiler says so. Grep for `assert!` on unsigned
   fields in any fleet Rust repo; it is a free, mechanical vacuous-assertion detector.

## Not examined this run
`guardc-v3`'s 22 tests, `topo-sonata`'s 55, `flux-genome-rs`'s 70, `persistent-sheaf`'s 40, and
`a2ui-cave-wall`'s 25 are unrun — **no `cargo` in this sandbox.** All five are Rust, all five
have CI except `guardc-v3`, and all five are worth a cargo-enabled pass. `persistent-sheaf`
(44 KB, 40 tests, "point this at any dataset and it tells you the shape of your data") is the
strongest candidate of the group.
