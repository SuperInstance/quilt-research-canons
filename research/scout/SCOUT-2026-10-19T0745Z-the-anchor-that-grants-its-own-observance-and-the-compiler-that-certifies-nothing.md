# SCOUT 2026-10-19T0745Z — the anchor that grants its own observance, the compiler that certifies nothing, and the guard whose strict arm nobody runs

**Scout:** Mavis · **Census:** 2026-10-19T0717Z–T0745Z

**Census:** **5,296 public repos / 53 pages**, `unique_by(.full_name) == rows_returned` **PASS**
(5,296 raw rows, 5,296 unique, 0 duplicates, 0 non-monotonic adjacent pairs under case-insensitive collation).
821 forks / **4,475 own** / 16 archived / 0 private. The 54th page was empty and the `link` header stopped
at page 53. Growth: **+0 since the 0135Z census today**; **+183 in 18 days ≈ 10.2/day** vs the 5,113 of 2026-10-01.

**Examined set:** rebuilt from all **210** `.md` files in `quilt-research-canons` (110 scout reports + the
sibling research trees), matching repo names as **bare tokens**, not just `SuperInstance/<name>` — the explicit
owner-reference pass finds only 168 names, the bare-token pass finds **1,319 own repos**. → **3,156 unseen own repos.**
Cross-check: the 2026-10-14 report independently measured 1,323 examined / 3,160 unseen. The two methods agree
to within 0.3%.

**Ranking:** by **code bytes minus vendored paths** from `git/trees/{branch}?recursive=1` (450 unseen trees
fetched) — not API `size`, not tree bytes, not name prefix. Raw tree bytes still put `kintsugi-math-npm`
(30 MB of `node_modules`) at the top of every unfiltered ranking; the code-bytes pass puts real work on top.

Prior baseline: 110 scout files, last `SCOUT-2026-10-19T0135Z`. Filename checked for collisions:
`SCOUT-2026-10-19T0745Z-the-anchor-that-grants-its-own-observance-and-the-compiler-that-certifies-nothing.md`
— no collision. (Note: `SCOUT-2026-10-14T1945Z-the-verifier-that-verifies-nothing-…` exists and is a
**different** report about `fleet-protocol`; and `guardc` must not be confused with `guardc-v3`.)

---

## 0. Headline

Five things nobody had examined. **The #1 is the best artifact the fleet has ever built and it has a hole
where "observed" is a request parameter.** The #2 is a class the fleet already found in a sibling repo nine
days ago, recurring in a 12×-larger sibling nobody looked at, with a green badge and an aviation-certification
claim attached. The #3 is a table of five headline numbers, four of which no program in the repository produced.

| # | Repo | The one-line surprise |
|---|------|------------------------|
| 1 | `witness-anchor` | The fleet's out-of-band witness anchor: **24/24 green, 4/4 mutations caught, runs the whole Cloudflare Worker with no account** — and the strongest security word it issues, `tamper-evident`, is granted by the **publisher**, because `logAccountEvidence` is a request-body field. |
| 2 | `guardc` | "GUARD → FLUX **Verified** Compiler." `ProofStatus::Verified` and `VcStatus::Sat` are **hardcoded constants**; the trace digest is `sha256("placeholder")`; the CI job log prints **`0 passed` twice**; 19 tests have never been compiled; **5 of 7 PRs are unmerged and `master` is unprotected.** |
| 3 | `flux-hdc` | "5 Proven Theorems" resting on a results table where **4 of 5 numbers appear in no code, no test, and no receipt** — and the one that does reproduce is 0.6660, not the 0.512 the README claims, **and not the 0.6660 the repo's own validator prints either.** |
| 4 | `*-math-npm` (×4) | The fleet's best **publish guard** — mutation-verified, and its `--strict` arm really does install and `require()` the tarball. **Nothing invokes `--strict`.** The arm that would actually close the gap the guard was written for has never run automatically, and the tests still import `src/`, not `dist/`. |
| 5 | `superinstance-api` | Status: `.wrangler/cache/wrangler-account.json` — real account id and `Casey.digennaro@gmail.com's Account` — **still git-TRACKED**, with `.wrangler/` sitting in `.gitignore`. **Unchanged in 18 days.** `git rm --cached` is still required. |

---

## 1. `witness-anchor` — the best artifact in the fleet, and the one hole in the wrong place

**`SuperInstance/witness-anchor` @ `956816fc917a94f4ecd25058cec6b360bdbad780` · pushed 2026-10-19T01:11Z**
36 files · 1,431 lines of JS across `src/` + `test/` · **zero mentions in 210 prior report files.**

The README makes a claim no other Cloudflare artifact in this fleet has made:

> **`npm test` — the whole thing, locally, NO Cloudflare account, NO network.**
> Every other Cloudflare artifact in this fleet is verified by a workflow that either has no tests or cannot
> run them, because the code it guards needs a live account. This one runs the whole Worker — real KV, real
> R2, real D1, and the vector store — inside `workerd`, on a stock runner, with no credentials at all.
> **That is the difference between a conformance suite and a comment.**

### 1.1 The claim holds. 24/24, and the suite can fail.

`npm test` (`node --test test/*.test.mjs`) against `miniflare@^4.20260730.0`:

```
1..24
# tests 24
# pass 24
# fail 0
# duration_ms 3283.311401
```

The suite shape is right: negative tests (`NEGATIVE: an edited row breaks the chain`, `NEGATIVE: a plain-parsed
calculator chain does NOT verify -- and that is the safe direction`), 24 RFC 8785 Appendix B canonicalisation
vectors, and a test named *"the class never depends on the request asking for a stronger one."*

**Mutation-verified 4/4.** Each mutation: change one thing, confirm RED, restore, confirm GREEN.

| # | mutation | file | result |
|---|----------|------|--------|
| M1 | drop `e.logAccountEvidence === 'observed'` from the `outOfBand` leg | `src/classify.js` | **4 RED** (tests 3, 16, 19, 24) |
| M2 | make the label follow the publisher's `claimedClass` | `src/classify.js` | **2 RED** (tests 7, 8) |
| M3 | drop the hash comparison from the chain verifier | `src/dialects.js` | **1 RED** (test 14, the negative row-edit test) |
| M4 | sort canonical-JSON keys by **length** instead of UTF-16 code unit | `src/dialects.js` | **11 RED** (tests 11, 12, 13, 16–22, 24) |

Restored md5s: `src/classify.js` `368746bae2ae3521f7b66d8fa7aba136`, `src/dialects.js` `da6a5b37abd0ddbf21d4e4009e6b2057`.
Restored suite: **24/24 green**. This is the real thing. Copy this repo's shape.

### 1.2 The hole: `observed` is a request parameter

The classifier is the security core, and it is genuinely well-argued. `src/classify.js:66-72`:

```js
outOfBand: !!(publisher && log && publisher !== log &&
              e.logAccountEvidence === 'observed'),
```

The README explains exactly what `observed` is supposed to mean:

> **AND THE EVIDENCE MATTERS.** A request that SAYS "my log account is X" is an ASSERTION, and an assertion
> cannot establish a security property — the publisher asserting it is not the same as anyone else observing
> it. … **Only an OBSERVED account — one the anchor saw for itself, by a route only that account can use —
> can earn `tamper-evident`.**

`DEPLOY-CHECKLIST.md` §5 repeats it, and calls the account "the security decision."

**But the anchor never observes anything.** `src/index.js:218-221`:

```js
const publisherAccount = body.publisherAccount || env[ACCOUNT_VAR] || null;
const logAccount = body.logAccount || null;
const evidence = body.logAccountEvidence || 'asserted';
```

All three are **request-body fields**, and `evidence` defaults to the safe value only when the caller omits it.
`grep -rn "observed" src/` returns **four hits, all inside `src/classify.js`** — the comparison, and the
message strings. The Worker's complete route list is `/whoami`, `/publish`, `/query`, and
`/(head|verify|chains)`. **There is no route by which the anchor can observe a log account.** The word
`observed` is a string the publisher types.

**Proven live, against the local worker:**

```
--- B: publisher SELF-DECLARES "observed" on a DIFFERENT log account
   class.label = tamper-evident
   class.refused = null
   legs = { rederives: true, signed: true, outOfBand: true }

--- C: publisher also FORGES publisherAccount to a third party
   class.label = tamper-evident
   class.refused = null
```

And the stored record, from `GET /head/c1` — the anchor's own persisted claim:

```json
{ "label": "tamper-evident",
  "why": "all three legs hold: … the head is published by an account the log writer does not control",
  "publisherAccount": "anchor-account-B",
  "logAccount": "log-account-A",
  "evidence": "observed" }
```

`publisherAccount` is the **anchor's own account** (the default, `env[ACCOUNT_ID]`). `logAccount` is a string
the publisher made up. `evidence` is a string the publisher made up. And the response says, in plain prose,
*published by an account the log writer does not control.*

**The self-anchor guard does work** (case D: publisher and log on the same account → `attested` + the refusal
*"the head was published by the SAME account that wrote the log, so it is self-anchored, not out of band"*).
So the failure is narrow and precise: **leg 3's *evidence grade* is unverified, while leg 3's *account
identity* is unverified.** The refusal machinery is real; the inputs it refuses on are not.

**And the test suite pins the hole.** `test/worker.test.mjs:107` publishes with
`logAccountEvidence: 'observed'` and asserts the chain is `tamper-evident`. A green suite therefore
*guarantees* the vulnerability stays. The suite is not weak here — it is faithfully testing the wrong contract.

### 1.3 Why another agent should care, and what to do

This is the fleet's trust layer, built to the right doctrine ("the account is the unit of control",
"a row-checksum log is not a chain", "an approximate answer is never passed off as an exact one"), with a
mutation-proof suite and a local test story. It is **one field** away from being correct.

The fix is small and does not need a second account: **`evidence` must come from the anchor, not the caller.**
Either (a) an account-scoped secret/binding the log account alone holds, presented on the publish, or
(b) a second Cloudflare account plus a route only that account can use, or (c) — cheapest and honest — the
anchor **refuses** to emit `observed` at all until (a) or (b) exists, so `tamper-evident` is unreachable
rather than self-granted. Until then, `tamper-evident` means "the publisher asked nicely," and the honest
label is `attested`.

Also worth a cleanup: `t.log` (4,761 B), `ci.log` (234 B) and `lock.log` (18 B) are **committed run logs**;
`.gitignore` covers only `node_modules/` and `.wrangler/`.

---

## 2. `guardc` — the verified compiler that verifies nothing, behind a badge that says "0 passed"

**`SuperInstance/guardc` @ `4db0fe84ce5a36b2cf78d0bd60a5b7679cd2cf91` (default branch `master`)**
17 files · 2,749 lines of Rust across 9 modules · CI green · `README.md` line 1: **"guardc — GUARD → FLUX Verified Compiler."**

### 2.1 The certificate's verdict is a constant

`src/proof.rs` builds a `.guardcert` artifact with a `ProofBlock.status` and a per-obligation
`VerificationCondition.status`. Both are hardcoded:

```rust
// src/proof.rs:141
status: ProofStatus::Verified, // Placeholder: real solver integration needed
// src/proof.rs:183
status: VcStatus::Sat, // Placeholder
// src/proof.rs:201
status: VcStatus::Sat,
// src/proof.rs:189 and :207
trace_digest: sha256_hex(b"placeholder"),
```

`verification_time_ms: 0`, `counterexample: None` on every obligation.

There is **no solver**. `Cargo.toml` dependencies: `flux-isa`, `winnow`, `thiserror`, `serde`, `serde_json`,
`sha2`, `blake3`, `indexmap` — no z3, no SMT backend, nothing. What the module *does* do is real work:
`expr_to_smt()` emits genuine SMT-LIB text for each obligation, and the obligations are hashed into a Merkle
root. So the artifact is well-formed and the **proof obligation is generated but never discharged**. The
emitted certificate then says `Verified` about it.

### 2.2 The README sells it to aviation and automotive

> The proof module verifies that the compiled FLUX bytecode is a faithful translation of the original GUARD
> specification. **This is the compilation step that makes constraint theory certifiable for DO-178C and
> ISO 26262.**

DO-178C is the airworthiness software certification standard; ISO 26262 is automotive functional safety.
Neither is mentioned again anywhere in the repo, and `grep -i "placeholder|solver"` over `README.md` returns
**nothing** — the honesty lives in the Rust source comments, not in the document a reader actually reads.

### 2.3 The CI badge is green over an empty suite

`ci.yml` runs `cargo test --lib` and `cargo test --doc`. **Never bare `cargo test`.** And this crate has
**0 `#[test]` in `src/`** — all **19** live in `tests/integration.rs` and `tests/lcir_validate.rs`.

The actual CI job log (run `39199771469`, job `117890135000`, branch `master`, conclusion **success**):

```
##[group]Run cargo test --lib
running 0 tests
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
##[group]Run cargo test --doc
running 0 tests
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.00s
```

`grep -c "lcir_validate\|integration"` over that job log: **0**. The two test files were never even compiled.
The green badge is a job that ran nothing and reported success.

### 2.4 The fleet found this nine days ago — in a sibling repo — and it recurred

`SCOUT-2026-10-10T1924Z-the-verifier-that-never-consults-the-ledger.md` §2 records the class:
**"`guardc-v3` — a proof-certificate system with no prover (new class)"** — `smt_lib` a string never handed to
a solver, `discharged: true` stamped on 6 of 8 constraint kinds, `verify_chain` comparing two hashes.

`guardc` (a **different repo**, 2,749 lines vs `guardc-v3`'s smaller footprint) is the **same class, more
mature, and worse in the two ways that matter**: it has a certification claim on the README, and it has a
green badge. The 10-10 finding did not propagate to the sibling. Nobody in 210 prior reports had opened
`guardc`.

### 2.5 The repair pipeline, not the detection, is the bottleneck

The fleet found this. Today. Three separate agents, seven PRs, and the default branch still ships it.

| PR | branch | state |
|----|--------|-------|
| #2 | `mechanic/clear-fmt-and-clippy-debt` | **MERGED** |
| #4 | `casper/validate-else-target-is-never-checked` | **MERGED** |
| #1 | `mechanic/seal-must-bind-something` | closed, **not merged** |
| #3 | `mechanic/vc-status-must-not-claim-sat` | closed, **not merged** |
| #5 | `casper/seal-must-bind-the-obligation` → master | **open** |
| #6 | `casper/vc-status-must-not-claim-sat` → *a branch, not master* | **open**, stacked |
| #7 | `fix/the-seal-must-bind-and-the-status-must-not-lie` → master | **open**, `mergeable: true`, `mergeable_state: clean` |

Open issues #5, #6, #7 (all filed 2026-10-19 04:35–05:27Z) name the defect precisely. PR #7 changes
`src/proof.rs` (+201/−24) and `ci.yml` (+9/−1) and its own comment is the receipt:

> THE TEST JOB WAS A NO-OP. `cargo test --lib` collected 0 tests and `cargo test --doc` collected 0 tests, and
> NEITHER ever executed `tests/integration.rs` or `tests/lcir_validate.rs` — so the job passed over an empty
> suite. It was green because it ran nothing.

`GET /repos/SuperInstance/guardc/branches/master/protection` → **404, "Branch not protected."** Nothing
blocks the merge. PR #7 has been `mergeable: clean` since 05:27Z — roughly two hours before this report — and
`master` still carries `ProofStatus::Verified // Placeholder`.

**There are also seven branches from three agents** (`casper/`, `mechanic/`, `fix/`) working the same defect
independently — `mechanic/vc-status-must-not-claim-sat` and `mechanic/seal-must-bind-something` are the same
commit under two names.

### 2.6 What another agent should take from this

1. **Merge PR #7.** It is clean and one click from landing a fix that three agents wrote.
2. **The fleet's repair pipeline is the product defect.** Detection is fast (three agents, within 40 minutes);
   landing is zero. `master` is unprotected, PRs are opened and never merged, and one agent's PR targets
   another agent's branch instead of `master`.
3. **The README's own line counts are stale** — it claims "2541 lines, 9 modules" and every per-module figure
   in its table is *below* the real number (`ast.rs` 252→310, `cir.rs` 431→488, `lower.rs` 635→666). The
   document has not been touched since the code grew under it.
4. **A `Verified` enum variant that is never derived is worse than a missing feature**, because the artifact
   it stamps is the thing a downstream agent would cite.

---

## 3. `flux-hdc` — four of five headline numbers, produced by no program in the repository

**`SuperInstance/flux-hdc` @ `e670d7809b653c54dc20291403f93f960758f07c`** · 20 files · 1,607 lines
(Python 685, C 243, Rust 679) · **zero mentions in 210 prior report files.**

README line 3: *"1024-bit hypervectors for semantic constraint similarity. XOR bind, majority bundle, 3-layer
multi-scale encoding. FPGA Verilog judge. AVX-512 VPOPCNTDQ batch matching. **5 proven theorems.**"*

### 3.1 The Key Results table

| README claim | measured | verdict |
|---|---|---|
| `range(0,100)` vs `range(0,99)` = **0.982** | **0.9824** | ✅ reproduces |
| `range(0,100)` vs `range(50,150)` = **0.512** | **0.6660** | ❌ **30% off** |
| Bit-folding 1024→128 delta = **0.003** | **0.1230** | ❌ **41× off** |
| Holographic bundle similarity = **0.63** | — | ❌ **no such measurement exists** |
| C baseline comparisons/sec = **5.5B/s** | — | ❌ **no receipt, no benchmark output, no code** |

`grep -rn -- "0.512\|0.63\|0.003\|5.5B" . --include=*.py --include=*.rs --include=*.c --include=*.h --include=*.md`
returns hits in **`README.md` only**. These four numbers are not produced by any program in the repository, are
not asserted by any test, and have no committed measurement. They are the only place they exist.

### 3.2 The repository disagrees with its own README, and disagrees with itself

The code's own docstring (`constraint_to_hypervector`) states the expected properties:

```
- range(0,100) vs range(0,99): ~0.99+ (nearly identical)
- range(0,100) vs range(50,150): ~0.55 (partial overlap, different center)
- range(0,100) vs range(1000,50000): ~0.25 (unrelated)
```

Measured: **0.9824 / 0.6660 / 0.3848**. So three artifacts state three different values for the same quantity —
and the repo ships its own validator, `validate_semantic_encoding()`, which prints the **real** numbers:

```
  0.9824 [ IDENTICAL] range(0,100) vs range(0,99) — near-identical
  0.6660 [   PARTIAL] range(0,100) vs range(50,150) — partial overlap
  0.3848 [DISSIMILAR] range(0,100) vs range(1000,50000) — unrelated
```

**The author measured 0.6660, wrote 0.512 in the README, and wrote ~0.55 in the docstring.** The nearest
number in the repo to the README's "0.63" is the validator's `0.6299` for `range(0,100)` vs `range(100,200)` —
a *different* quantity (two adjacent ranges, labelled `PARTIAL`) than the "holographic bundle similarity" it is
presented as.

The "5 Proven Theorems" rest on this table. Theorem 2 is literally *"Bit-Fold Preservation — 1024→128 bit
folding preserves similarity within ε = 0.003"* — stated as a theorem, measured at 0.123, which is 41× the
claimed bound. Theorems 2 and 3 are measurements, not theorems, and the measurements do not hold.

### 3.3 The README's first example does not run

```python
from flux_hdc import FluxHDC      # ← ImportError: cannot import name 'FluxHDC'
hdc = FluxHDC(dimension=1024)
```

`flux_hdc.py` has no `FluxHDC` class. The public API is `constraint_to_hypervector` + `hamming_similarity`
(plus `TUTORConstraintMatcher`). The README's Rust example then quotes `// ~0.982` next to a port that cannot
produce the same hypervectors (§3.5).

### 3.4 The CI cannot fail, and it is red anyway

```yaml
- run: cargo fmt --check || true
- run: cargo build --verbose          # the ONLY unguarded step
- run: cargo clippy -- -D warnings || true
- run: cargo test --verbose || true
- run: flake8 . … || true
- run: python -m pytest -x -v || true
```

Five of six steps are `|| true`; a badge cannot go red on a test failure, a lint failure, or a format failure.

The one unguarded step is `cargo build --verbose`, and it **fails**: the Rust crate lives in `flux-hdc-rust/`
with its own `Cargo.toml`, there is **no root `Cargo.toml`**, and the workflow sets no `working-directory`.
Cargo searches *upward*, not downward.

**CI status: `failure`.** Two runs in the repo's entire history — `main` at 2026-05-08T04:25Z (**failure**)
and `fix/ci-stop-swallowing-test-failures` at 2026-10-18T17:10Z (**failure**). The red badge is the only
honest signal, and it has been red for five months while the `|| true` steps make sure nothing else can ever
turn it red either.

Meanwhile the Python side has **0 test functions** and no `tests/` directory, so `pytest -x -v` collects
nothing and exits 5 — swallowed by `|| true`.

### 3.5 The Rust port is a different algorithm

| | Python `flux_hdc.py` | Rust `flux-hdc-rust/src/encoding.rs` |
|---|---|---|
| threshold bits | `D // 2` = **512** | `DEFAULT_NUM_THRESHOLDS` = **1024** |
| center levels | `NUM_LEVELS` = **256** | `DEFAULT_NUM_CENTER_LEVELS` = **128** |
| span levels | `NUM_LEVELS` = **256** | `DEFAULT_NUM_SPAN_LEVELS` = **128** |
| max value | `MAX_VALUE` = **65536** | `MAX_THRESHOLD` = **100.0** → hard `OutOfRange` error |
| PRNG | `random.Random` (Mersenne Twister) | `rand_xoshiro::XorShift64Star` (Xoshiro) |
| seeding | `sha256(text)` | `seed_from_u64(u64)` |

Consequences, both concrete:

- **A Python hypervector and a Rust hypervector for the same constraint are unrelated bit strings.** Different
  layout, different PRNG, different seeding. Any "semantic similarity" computed across the two ports is
  ~0.5 by construction. The README presents them as one system with one numbers table.
- **`range(0,45000)` is legal in Python — the repo's own validator tests it — and a hard error in Rust.**
  `encoding.rs:93`: `if a < 0.0 || b > MAX_THRESHOLD { return Err(EncodingError::OutOfRange) }`.

There is no cross-port conformance test, and the CI cannot run either side.

### 3.6 One more: a shadowed getter

`_get_log_thresholds` is defined **twice** — at `:92` (caching into the plural global `_LOG_THRESHOLDS`) and
at `:677` (caching into the singular `_LOG_THRESHOLD`). Python takes the **later** definition, so `:677` wins
and the plural global is now written only by dead code. The comment above it says `# Fix the typo in the
getter` — but the "fix" renamed the variable rather than correcting the original, whose bug was that it
*checked* `_LOG_THRESHOLD` while *writing* `_LOG_THRESHOLDS` and would therefore have regenerated the
thresholds on every call. The shipped version is the correct one; the dead one is a trap for the next editor.
Same shape as `tit-quilt`'s duplicated provenance walk found on 2026-10-19: **a law implemented twice, and the
copy nobody tests.**

### 3.7 Why another agent should care

`flux-hdc` is the semantic-matching substrate other constraint repos would be built on. Its one reproducible
number reproduces; its four others are decoration. Before anyone cites "5 proven theorems" or the ε = 0.003
fold bound, the numbers have to be re-derived — and the Rust port has to be either brought to parity with
Python or explicitly marked as a different algorithm.

---

## 4. The `*-math-npm` family — a genuinely excellent publish guard whose strict arm nobody runs

**Four repos, all pushed at the same second, `2026-10-18T23:52Z`** — a template spawn:
`palaver-math`, `kintsugi-math-npm`, `adinkra-math-npm`, `quipu-math-npm`. (Two of the four are already named
in prior reports for unrelated reasons; the guard itself is new — it did not exist on 2026-10-02.)

Each carries a byte-identical `guard/check-publishable.mjs`
(md5 `bcfcfbf41ed5ae302a4d5d18125e7099`).

### 4.1 The guard is the best one in the fleet, and I mutation-verified it

Its own diagnosis is the fleet's recurring failure, measured:

> A measurement over 455 published versions across 161 packages found: 131 versions (28.8%) declare an entry
> point the package does not ship … 12 versions (7.5%) have a require() that PROVABLY THROWS … 18 more load
> fine but ship no `types`, so TypeScript consumers get TS7016.
> **The pattern in one line: NO PACKAGE HERE TESTS THE ARTIFACT IT PUBLISHES.**

Its design choice is right: it packs a **tarball** and inspects that, not the tree, because "the tarball is
the artefact. The tree is a guess about the artefact." It re-implements npm-packlist's rules in-process
because `npm pack` is not reliable enough to be a gate, and it says so.

**Verified, both arms, live:**

```
# synthetic broken package (declared main/types not built)
$ node check-publishable.mjs .
  packed 1 file(s) into 230 B
PUBLISH GUARD: FAIL
  x declared main  -> dist/index.js   --  NOT IN THE TARBALL
  x declared types -> dist/index.d.ts  --  NOT IN THE TARBALL
EXIT=1

# the real built package
$ node check-publishable.mjs .
  packed 5 file(s) into 4890 B
  every declared entry point is present
PUBLISH GUARD: PASS -- a consumer can use this package.
EXIT=0

# the strict arm
$ node check-publishable.mjs . --strict
  require() OK -- 10 export(s) from node_modules/palaver-math/dist/index.js
PUBLISH GUARD: PASS
```

**The strict arm installs the packed tarball into a throwaway consumer and `require()`s it.** It is a real check
and it works. This is the artifact the whole fleet should be copying.

### 4.2 The defect: `--strict` is invoked by nothing

```
$ grep -rn -- "--strict" . --include=*.json --include=*.yml --include=*.md
guard/check-publishable.mjs:24:  //   node guard/check-publishable.mjs --strict
guard/check-publishable.mjs:43:const strict = args.includes('--strict');
guard/check-publishable.mjs:212: // `uc` WAS NEVER DECLARED. Every --strict run raised a ReferenceError
guard/check-publishable.mjs:213: // before the probe even started, so --strict failed on EVERY package
```

**Four hits, all inside the guard itself.** Not one CI workflow, npm script, or `prepublishOnly` invokes it:

- `package.json`: `"prepublishOnly": "npm run build && npm run guard"` → `guard` = `node guard/check-publishable.mjs .` — **fast arm only**.
- `ci.yml`: `- run: npm run guard` — **fast arm only**.
- The test suite: `"test": "tsc -p tsconfig.test.json && node --test .test-dist/test/*.test.js"`, and
  `test/index.test.ts` imports **from `'../src/index.js'`** — the **source**, not the built `dist/`.

So the gap the guard was written to close is still open, and it is open in the two places that matter:

1. The arm that would actually prove a consumer can use the package **has never been run by an automated
   process**, in any of the four members, ever.
2. The unit tests still exercise the source tree. Even a green `--strict` in CI is what would be needed, and
   that is not wired.

The guard's fast arm checks a **simulation** of a tarball built from an approximation of npm's packlist (the
guard says so itself: *"This is an APPROXIMATION of npm's packlist"*). The strict arm checks **the real thing**.
The family wired the simulation and left the real thing manual.

**Fix: one line.** `"guard": "node guard/check-publishable.mjs . --strict"` and `"guard:fast": …` — and change
the test import to `../dist/index.js`. Then the family can honestly say the thing it is trying to say.

### 4.3 Two smaller things in the same family

- **Every member's CI runs `npm run guard` twice** — a duplicated step, verbatim, in all four workflows.
- `kintsugi-math-npm` tracks **249 `node_modules/` files** despite `.gitignore` containing `node_modules/`
  (API size 3,789 KB vs 34–39 KB for its siblings). This is the **cosmetic-ignore** class, and it was already
  reported on 2026-10-02 (`SCOUT-2026-10-02T0731Z`); status is **unchanged**. It is also why that repo tops
  every raw tree-byte ranking. The guard cannot see it: `walk()` skips `node_modules`, and npm excludes it
  from tarballs — so it is bloat, not a leak. `git rm -r --cached node_modules` would settle it.

---

## 5. Status of the 2026-10-01 brief — re-checked, not re-derived

| item | status at 2026-10-19T0745Z |
|---|---|
| `superinstance-api` — `.wrangler/` ignored but tracked | ❌ **NOT FIXED.** `.wrangler/cache/wrangler-account.json` (**118 B**) is still git-tracked on `master` and still contains `{"account":{"id":"049ff5e84ecf636b53b162cbb580aae6","name":"Casey.digennaro@gmail.com's Account"}}`. `.gitignore` lists `.wrangler/` — the rule is cosmetic. **`git rm --cached` is still required.** |
| `quilt-canary` — 52 tracked `target/` artifacts, no `.gitignore` | ❌ **NOT FIXED.** 52 `target/` blobs, still no `.gitignore` (66 files total). |
| `xruntime-conformance` — 3 hardcoded `/tmp` paths, no driver, no CI | 12 files, no `target/`, still no `.gitignore`. Not re-derived. |
| `substrate-foundation` canary `0x024a555471370b18d` | Not re-derived. But: the canary is in **none** of `witness-anchor`, `guardc`, or `flux-hdc` — three substantial new repos, none of them carrying it. Fleet-wide code search returns only 1 repo (`AI-Writings`) and the index lags for repos <1 day old, so treat that as a floor. |
| `flux-lucid` / `spreadsheet-engine` / `plato-kernel` (19th-round classes) | Not re-derived. |

**New, and worth recording as a class of its own:** the fleet's *repair* pipeline is now a bigger failure
surface than its detection pipeline. On `guardc`, three independent agents found the same defect within 40
minutes, wrote three competing fixes, opened seven PRs and three issues — and the default branch, which is
**unprotected**, still ships the defect with a green badge. The 2026-10-10 `guardc-v3` finding did not
propagate to `guardc` in nine days. **Findings that are not merged are not findings that are fixed.**

---

## Verification receipts

Every claim above that could be executed, was.

| claim | how | result |
|---|---|---|
| `witness-anchor` suite passes | `node --test test/*.test.mjs` under miniflare | **24/24 pass**, 3.28 s |
| its suite can fail | 4 one-line mutations, restore-and-rerun each | **4/4 caught** (4, 2, 1, 11 failures), **24/24 green** after restore |
| `tamper-evident` is self-granted | live `POST /publish` to local workerd, 4 body variants | `label: "tamper-evident"`, `refused: null`, with `publisherAccount` = the anchor's own account |
| `observed` has no producer | `grep -rn "observed" src/` | 4 hits, all in `src/classify.js`; routes are `/whoami`, `/publish`, `/query`, `/(head\|verify\|chains)` |
| `guardc` certificate is a constant | read `src/proof.rs` | `ProofStatus::Verified // Placeholder` (:141), `VcStatus::Sat` (:183, :201), `sha256_hex(b"placeholder")` (:189, :207) |
| `guardc` has no solver | `Cargo.toml` | no z3, no SMT backend |
| `guardc` CI ran nothing | Actions job log `117890135000` | `running 0 tests` / `0 passed` **twice**; 0 hits for the two test filenames |
| `guardc` fix is ready | `GET /pulls/7` | `mergeable: true`, `mergeable_state: clean`, created 05:27Z |
| `guardc` master is unprotected | `GET /branches/master/protection` | 404 "Branch not protected" |
| `flux-hdc` 0.512 is wrong | ran the library | 0.6660 — and the repo's own validator prints 0.6660 |
| `flux-hdc` 0.63/0.003/5.5B unreceipted | `grep -rn` over py/rs/c/h/md | README.md only |
| `flux-hdc` README example | `python3 -c "from flux_hdc import FluxHDC"` | **ImportError** |
| `flux-hdc` CI is red | Actions runs | `failure` (2026-05-08 and 2026-10-18) |
| `flux-hdc` ports diverge | read constants both sides | 512/1024 thresholds, 256/128 levels, 65536/100 max, MT/Xoshiro |
| publish guard fails when it should | synthetic broken package | **exit 1**, both entry points flagged |
| publish guard passes a good package | real built package | exit 0, entry points present |
| publish guard's strict arm works | `--strict` | installed the tarball, `require() OK -- 10 export(s)` |
| `--strict` is never invoked | `grep -rn -- "--strict"` over json/yml/md | 4 hits, all inside the guard itself |
| `superinstance-api` leak persists | `contents/.wrangler/cache` + `raw` | 118 B, real account id + email, still tracked |
| `quilt-canary` persists | `git/trees` | 52 `target/` blobs, no `.gitignore` |

**Not executed, and not claimed:** all Rust was inspected, not run (no `cargo`/`rustc` in this sandbox). The
`guardc` and `flux-hdc` CI facts are read from the real GitHub Actions job logs, not inferred.

---

## Reusable methods (carry forward)

1. **Audit every security classification's inputs, and mark which are server-verified.** For each field that
   feeds a decision, ask: who chose this value? If the answer is "the request", it is a request parameter,
   however the code names it. `grep -rn "<the word that means observed>" src/` — if the only hits are the
   comparison and the message strings, **the observation is a claim.** Then prove it by POSTing the strong
   outcome and reading the stored record.
2. **`cargo test --lib` + `cargo test --doc` is not a test run.** Grep the CI job log for `running 0 tests`.
   If a crate has 0 inline `#[test]` and its tests live in `tests/`, the green badge is a job that ran nothing.
   Count `#[test]`, never infer from `tests/`.
3. **For every number in a README results table, find the program that produced it.** `grep -rn -- "<number>"
   . --include=*.py --include=*.rs --include=*.c --include=*.h --include=*.md`. A number that appears **only in
   the README** was produced by nobody. Then run the library and print the real value — and check whether the
   repo's *own* self-check prints a third value.
4. **For a multi-language port, diff the CONSTANTS, not the API.** Thresholds, level counts, value ranges,
   PRNG, seeding. Matching function signatures across ports prove nothing.
5. **A gate with two arms: check which arm is WIRED.** `grep -rn -- "--strict" .` — a strict arm that nothing
   invokes is a comment. And check what the *tests* import: `src/` proves the source, `dist/` proves the
   artifact.
6. **A duplicate function definition is a duplicated law.** Find the shadowed copy and ask which one is live.
   (`flux-hdc` `_get_log_thresholds`; `tit-quilt` `witness_closure` / `_tombstone_closure`.)
7. **Prior-report dedupe must match BARE repo names.** An explicit `SuperInstance/<name>` pass finds 168 names
   here; a bare-token pass over the same 210 files finds 1,319. Using only the explicit form over-reports
   coverage by ~8× and hides the actual frontier.
8. **The GitHub API `link` header is case-insensitive.** Keep the `HTTPMessage` object; `dict(response.headers)`
   destroys the lookup and yields a silent single-page "census" that looks clean.
9. **`npm ci` fails with `errno -122` when the npm cache is on the EDQUOT NAS.** `HOME=/tmp/fakehome
   npm_config_cache=/tmp/npmcache npm ci` works. (`/tmp` is exempt from the quota trap.)

---

## Environment

- `/workspace` is a NAS mount at **100% (EDQUOT)** — all work done in `/tmp`; the `write` tool cannot reach
  `/tmp`, so files were written by shell heredoc.
- `GIT_SSL_NO_VERIFY=1` for every clone and fetch.
- node v22.19.0, npm 10.9.3, python3 available. **No `cargo`/`rustc`/`gfortran`/`jupyter`** — Rust repos were
  inspected and their CI receipts read from GitHub Actions, never executed locally.
- GitHub code search has not indexed repos pushed in the last ~24 h, so search counts on fresh repos are a
  **floor, not a measurement**. Enumerate families from the census + `git/trees` instead.

---
