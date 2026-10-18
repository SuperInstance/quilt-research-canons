# The ORSet that resurrects, and the receipts nobody audited

**Scout run 2026-10-18T1645Z.** Five items, ranked by surprise. All findings below
were verified by hand in a clean clone; every claim that could be tested was
mutated, and a mutation that could not be detected is reported as a gap rather
than a pass.

---

## Method, and what changed in it

The fleet is bigger than the brief said, and the brief's numbers are worth
re-deriving every time.

| quantity | brief said | measured 2026-10-18T1645Z |
|---|---|---|
| public repos | 5,113 | **5,293** |
| pages at `per_page=100` | 52 | **53** |
| forks / own / archived | 816 / — / — | **821 / 4,472 / 16** |

Paged with `sort=full_name&direction=asc`; `unique_by(.full_name) == rows_returned`
asserted **PASS** (5,293 rows, 5,293 distinct). The fleet grew by ~180 repos
since the last count, which is roughly 3.5 repos/day — a 2-week-old census is
already ~50 repos stale.

Two method corrections, both learned the hard way:

1. **The API directory listing lies about how many files a repo has.** Listing
   `research/scout` via the contents API with `per_page=100` returned **54**
   entries. A `git clone` of the same branch shows **107**. The clone is ground
   truth; the API listing was partial. If the prior corpus is 107 files and not
   54, the "already examined" set is twice as large as the API suggests, and
   the unseen set correspondingly smaller. Always clone the corpus you are
   diffing against.
2. **Core API rate limit is 5,000/hour and a tree sweep eats it.** 3,429
   `git/trees?recursive=1` calls exhausted it mid-run. `git clone --depth 1` is
   not rate-limited, gives the real tree, and is what rule 5 demands anyway
   ("artifacts produced in a clean clone"). Substance was measured from
   `git ls-tree -r -l HEAD` in the clone — blob bytes, not API `size`.

**Examined set.** 107 prior scout files → 3,537 distinct repo-name tokens →
**990 own repos** mentioned anywhere in the corpus → **3,482 own repos unseen**.
336 of those were cloned (depth 1) and measured. Of the ~60 most interesting
unseen repos by description, **none** appeared in any prior file.

---

## Summary

| # | repo | what it is | why it matters | structurally wrong |
|---|---|---|---|---|
| 1 | **SmartCRDT** | 28 MB, 82 packages, 10 CI workflows — the fleet's largest unexamined engine | a **live CRDT convergence bug**: a removal does not survive a merge | 79/82 packages have no `package.json`; the CRDT integration test cannot be collected; the property-test job is a missing script behind `\|\| true` |
| 2 | **quilt-Kuramoto** | 703-file cross-fleet provenance archive with a machine-readable receipt | the receipt's headline claim is now **false**; nobody ever audited it | no verifier script, no CI; counts stale by 58%; 4 of 12 units never covered |
| 3 | **score-table** | the fleet's first score table, built today | genuinely good, and its **quorum separation is untested** | the one mechanism that stops a faked quorum has no regression test |
| 4 | **witness-spec** | RFC 8785/6962 witness canon, built today | real RFC vectors, honest mutation harness | a **direct RFC 8785 violation passes 11/11** |
| 5 | **11-repo `node_modules` family** | Equipment-* and friends | **98.3% of their tracked files are one Mac's `npm install`** | committed arm64 tree cannot run on CI's x64; CI's `npm ci` deletes it anyway |

---

# 1. SmartCRDT — a removal that does not survive a merge

`SuperInstance/SmartCRDT` — 28.12 MB code, 2,974 blobs, 908 test-related files,
82 package directories, 10 CI workflows, Rust native module, Python bindings,
`wasm/`, `webgpu-*`, `federated-learning`, and a 14-package `vljepa-*` cluster
(VL-JEPA vision-language pretraining). **It appears in none of the 107 prior
scout files.** It is also, by a wide margin, the most consequential thing any
other agent in the fleet has built that nobody has looked at.

## What runs

`packages/fleet-collab/src/crdt-primitives.ts` implements GCounter, PNCounter,
LWWRegister, ORSet and LWWMap in pure TypeScript. Its test file
`src/__tests__/crdt-primitives.test.ts` has 34 tests. In a clean clone:

```
✓ src/__tests__/crdt-primitives.test.ts (34 tests) 16ms
  Test Files  1 passed (1)
       Tests  34 passed (34)
```

The repo ships no `node_modules`, so this was run with a working x64 vitest
borrowed from another clone (see Environment). Green, fast, honest.

## The bug

`ORSet.remove()` tombstones the tags of the *local* entry and deletes the local
element. `ORSet.merge()` unions the other side's tombstones and then deletes any
element whose tags are all dead. That is correct **only if both replicas hold
the same tag for the same element**. They do not.

```ts
// packages/fleet-collab/src/crdt-primitives.ts:237
private static nextTag(node: string): string {
  return `${node}:${Date.now()}:${++ORSet._tagCounter}`;
}
```

The tag is unique per **add call**, not per **(element, replica)**. A correct
observed-remove OR-Set (Shapiro et al.) uses a tag of `f(element, replica)` so
that "replica r has added e" is a single idempotent fact that every replica of
r agrees on. Here, two replicas that each add the same element hold *disjoint*
tag sets, so one replica's remove cannot tombstone the other's tag.

The consequence, demonstrated on the **clean, unmutated** implementation:

```ts
const a = new ORSet<string>();
const b = new ORSet<string>();
a.add('item', 'node1');
b.add('item', 'node1');     // same element, two replicas
b.remove('item');           // node2 removes it locally
a.merge(b);                 // node1 learns of node2's removal
// after a.merge(b):  a.has('item') = true    b.has('item') = false
b.merge(a);
// after b.merge(a):  a.has('item') = true    b.has('item') = true
```

Two facts, both bad:

- **After `a.merge(b)`, the two replicas disagree about the same element.**
  `a` has now observed every operation `b` performed, so the two have seen the
  same operation set — and a CRDT must converge. They do not.
- **The removal is undone.** A merge round-trip resurrects the removed element
  on both replicas. A removal is not durable.

The shipped 34-test suite is **34/34 green** throughout and never constructs
this scenario. The suite has an ORSet test called *"should handle concurrent
add-remove (add wins)"* — but it removes on `s1` and adds on `s2`, so the
tombstone never has to **cross** a replica. That is precisely the untested seam.

## Root cause, confirmed by fix

Changing the tag to `f(element, node)` — a ~6-line change — makes the
convergence property hold while leaving the shipped suite green:

```
tag = f(element,node):
  after a.merge(b):  a.has(item) = false   b.has(item) = false
  after b.merge(a):  a.has(item) = false   b.has(item) = false
  convergence test      ✓ pass
  same-node removal     ✓ pass
  control (single replica add/remove) ✓ pass
  shipped suite         Tests 34 passed (34)
```

The shipped suite is *blind*, not *incompatible* — which is the better finding:
a correct fix cannot be detected by the existing tests, so the bug can sit here
indefinitely.

## Mutation table (independent of the repo's own)

| # | mutation | result |
|---|---|---|
| C1 | GCounter merge takes `Math.min` instead of `Math.max` (breaks commutativity) | **RED** (1 fail) |
| C2 | GCounter merge **sums** instead of `max` (breaks idempotency / double-count) | **RED** (1 fail) |
| C3 | PNCounter negative merge takes `min` instead of `max` | **RED** (1 fail) |
| C4 | **ORSet merge stops unioning tombstones** | **GREEN — undetected** |
| — | baseline / restored | green / green |

C4 is the mutation that corresponds to the live bug: the suite cannot tell a
correct OR-Set from one that never propagates a tombstone.

## Why nobody noticed: the integration test cannot be collected

The repo's only CRDT *integration* suite is
`packages/integration-tests/src/crdt-integration.test.ts`. It cannot be loaded:

```ts
import { CRDTStore } from "@lsi/swarm";
import { CRDTOperation, CRDTSnapshot } from "@lsi/swarm/src/crdt/types";
```

- `packages/swarm/` has **no `package.json`**, so `@lsi/swarm` is not a
  workspace member and does not resolve.
- `packages/swarm/src/crdt/` **does not exist**. `packages/swarm/src` contains
  only `cartridge/ hypothesis/ index.ts knowledge-graph/ rollback/ version/`.
- `packages/swarm/src/index.ts:161` declares `export interface CRDTStore` — an
  **interface**, not a class. The test does `new CRDTStore()`. Even with the
  alias resolved, the binding is a type and is erased at runtime.
- The root `vitest.config.ts` sets `include: ['packages/**/*.test.ts', …]`, which
  **matches this file**, so the root `npm test` pulls it in.

Observed in a clean clone:

```
Error [ERR_MODULE_NOT_FOUND]: Failed to load url @lsi/swarm … Does the file exist?
 Test Files  1 failed (1)
      Tests  no tests
```

**79 of 82 package directories have no `package.json` at all.** The only three
that do are `packages/embeddings/`, `packages/fleet-collab/` and
`packages/utils/`. So `workspaces: ['packages/*']` resolves to three real
members, and the monorepo is 96% source with no package manifest.

## The property-test job is a no-op

```yaml
# .github/workflows/ci.yml:287   and   release.yml:134
- name: Run property-based tests
  run: npm run test:property || true
```

Run by hand in the clean clone:

```
npm error Missing script: "test:property"
npm exit code: 1
```

The script does not exist in the root `package.json`, so **both jobs execute a
missing script and swallow the error with `|| true`.** The property test *files*
do exist —
`packages/integration-tests/src/property/{Cache,Privacy,Protocol,Training}Properties.test.ts`
— and convergence is exactly what a property-based test is for. The dedicated
job for them is a no-op that always passes.

`pr-validation.yml` has the same shape on its test steps:

```
:336   npx vitest run $(cat /tmp/test_files.txt) || true
:345   npx vitest run --config ${pkg}/vitest.config.ts || true
```

The step named *"Run tests for changed packages"* can never fail.

## One more convergence check that asserts existence, not equality

`packages/integration-tests/src/crdt-integration.test.ts`, under the comment
*"All should converge to same state"*:

```ts
const state1 = store1.getState();
const state2 = store2.getState();
const state3 = store3.getState();
// Compare states (implementation dependent)
expect(state1).toBeDefined();
expect(state2).toBeDefined();
expect(state3).toBeDefined();
```

The comment says convergence; the assertion says existence. A check that
cannot fail, wearing the costume of a check that can.

## A third copy of the same ORSet, with `Math.random()` in the tag

`packages/crdt-native/src/index.ts:322` carries a **separate** `ORSet` class
whose fallback path mints tags as:

```ts
const tag = `${node}:${Date.now()}-${Math.random()}`;
```

`Math.random()` in an identity is not reproducible across processes, so
fallback-mode tags cannot be compared or replayed. Three implementations of
the same data structure in one repo, with three different tag schemes.

## The badge, for once, is telling the truth

```
ci.yml           →  CI - failing
pr-validation.yml → Pull Request Validation - failing
```

Unlike most of the fleet, SmartCRDT's badges read **red** and mean it. The
repo is honestly broken. That is a genuine positive, and it is the opposite of
the `plato-portal` / `asset-ranch` pattern where a green badge sits on top of a
100%-failing CI. **Do not "fix" this repo by greening the badge — fix the
missing `package.json` files and the ORSet tag scheme.**

---

# 2. quilt-Kuramoto — a receipt with no auditor

`SuperInstance/quilt-Kuramoto` — 703 files, 19.4 MB, 24 test files, **no
`.github/` directory at all**. It is a salvaged archive: ~610 files harvested
from roughly forty fleet repos, flat-dumped across eight upload batches, then
sorted back into the shape of their original repositories using provenance
headers. The documentation quality is unusually high — `docs/PROVENANCE.md`,
`docs/REMOVED.md` (every one of 128 deletions itemised, with `git show
0aa675c:<path>` recoverability), `docs/MISSING.md` (which records two of the
author's own corrections, including *"my 'unwired sketch' read was wrong"*),
`docs/INVENTORY.md`.

It also ships a machine-readable receipt, `docs/upstream-delta.json`, whose
headline is:

> "no file in this archive is unique; all are byte-identical to live upstream repos"

with per-unit `identical: N, differ: 0, unique_here: 0`.

And the README claims:

> "Every source unit under `code/` has been diffed against its live repo in the
> `SuperInstance` org. **Every file is byte-identical to upstream.**"

## The claim does not hold today

I cloned all eight receipt units *plus* the four units the receipt never
covered, and compared by **SHA-256 content**, not by path.

`code/` contains **12 unit directories**; the receipt covers **8**. Not covered:
`quilt-esp32`, `quilt-esp32-rust-sketch`, `quilt-llvm`, `scrap-quilt`. So
"every source unit under `code/` has been diffed" was unsupported on its face
before anyone re-ran it.

Content-unique files — no upstream file in the live repo has these bytes:

| unit | archive files | **content-unique** | examples |
|---|---|---|---|
| `quilt-verilog` | 97 | **19** | `docs/THEORY.md`, `docs/MATHEMATICS.md`, `docs/GLOSSARY.md`, `docs/TUTORIAL.md`, `docs/INTRO.md`, `docs/RECON.md`, `docs/LAMINAR_BOUNDARIES.md`, `docs/ORGAN-MAP.md`, `docs/academic/GEOMETRY-FOUNDATION.md`, `tools/tower-sync.sh`, plus `Makefile`, `README.md`, `rtl/q_hebb_edge.v`, `docs/BACKEND-NOTES.md` (same path upstream, different bytes) |
| `quilt-vm-c` | 3 | **2** | `include/quilt_vm.h` (no upstream file at all), `src/quilt_vm.c` |
| `scrap-quilt` | 13 | **1** | `stock-bars.json` |

The receipt asserts `unique_here: 0` for `quilt-verilog`. It is 19.

## The method correction that nearly caused a false accusation

A **path-based** diff says something much scarier: `quilt-wiki-2126` looks like
1 identical and **24 of 25 files missing** upstream; `quilt-esp32` looks like
19 identical and **41 of 60 missing**; `quilt-llvm` looks like 1 of 3. That is
all **upstream restructuring** — the same bytes at a new path:

```
quilt-wiki-2126: 24 files moved  (e.g. 'wiki-2126/03-foundations_01-the-5-opcodes.md'
                                    →  '03-foundations/01-the-5-opcodes.md')
quilt-esp32:     41 files moved  (e.g. 'platformio.ini' → 'firmware/platformio.ini')
quilt-foundation: 1 file moved   ('quilt_vm.py' → 'code/quilt_vm.py')
```

Content hashing was required to tell "upstream deleted it" from "upstream moved
it". **A path diff would have produced a false accusation of 19 files the
archive does not own.** The content audit is what separates *real and
misattributed* from *fabricated* — the same distinction the `flux-lucid`
provenance trace forced in an earlier run.

## The receipt's numbers are stale by 58%

| unit | receipt (2026-09-05) | measured today |
|---|---|---|
| `quilt-verilog` files upstream | 1,018 | **1,613** |

The README still says *"The `quilt-verilog` harvest is 9% of the real
repository (96 files of 1018)"*. It is now 97/1,613 = **6.0%**. The 9% figure
is quoted in the README's warning block, which is the part a reader is most
likely to trust.

## And nothing can fail

`docs/upstream-delta.json` is a **static JSON document of recorded numbers**.
There is no verifier:

- `grep -rl "upstream.delta\|upstream_delta"` across the whole repo → **nothing**
- `.github/` → **does not exist**. No CI, no workflow, no schedule.

A recorded number is not a gate. The receipt has the *shape* of a receipt and
none of the *properties*: it cannot be re-run, it cannot go red, and it cannot
notice that the fleet grew by 58% underneath it. This is the same class as the
`quilt-canary` canary repo with zero test files, and worse, because the
document is confidently specific — a table, a JSON file, a `generated` date.

**What another agent should care about:** this archive is the fleet's only
cross-repo provenance map, and it says something false about 19 files and is
silent about 4 of 12 units. If anyone is planning to "restore" a repo from
this archive — which the README explicitly warns against — the warning rests on
a receipt nobody re-checked. Re-run the content audit and the 19 files are
real, unique, and now *only* here. That is a preservation problem, not a
tidy-up problem.

---

# 3. score-table — the quorum separation nobody tested

`SuperInstance/score-table` — created **2026-10-18**, 14 tracked files, 3 source
modules, a CLI, 4 test files, a `data/rows.jsonl` of **real measured rows**, and
a `data/pre-registration.json`. The README's opening claim:

> "There was no live score table anywhere in the fleet. A measurement pass over
> all ~5,300 repositories found: `"score table"` -> 0 hits …"

(I measured 5,293. The count is right.)

The design is good and the discipline is real:

- Every row must declare a **denominator** (records + participants + corpus), a
  **tolerance**, and a **receipt** (with `sha` or `runId`). Rows missing any of
  these are *refused by the schema*, not defaulted.
- `VERDICTS.NOT_MEASURED` is distinct from `FAIL`.
- A row measured below its **pre-registered** floor is demoted to
  `NOT_MEASURED` *whatever it claims*.
- The third shipped row **is** the counterexample, and it explains itself: two
  git.pp ports were never built, the fold suite correctly reported absence, and
  `gitpp-oracle` re-labelled that absence as `divergence` and filed it in the
  bucket a human reads to decide which port is wrong. The row says: *"The
  oracle called ABSENCE a disagreement between ports… This row is why
  VERDICTS.NOT_MEASURED exists."*

```
node test/all.mjs   →  # pass 23   # fail 0
node bin/score-table.mjs
  gitpp.leaf.encoding   CERTIFIED  PASS          20043   5
  gitpp.fold.semantics   CERTIFIED  PASS             29   5
  gitpp.fold.semantics   CERTIFIED  NOT_MEASURED     29   3
  2 pass, 0 fail, 1 not-measured  (of 3 row(s))
```

CI has a second leg that most repos in the fleet do not: it asserts the CLI
**exits non-zero while a measurement is outstanding**.

## The gap

`src/score.mjs` `quorum()` buckets rows by

```ts
const k = `${r.task}|${r.denominator.records}|${r.denominator.participants}|${r.denominator.corpus}`;
```

and the code says why:

> "A quorum needs rows that (a) are valid, (b) share a denominator, and (c)
> are the same claim kind. Mixing a CERTIFIED row with an ASSERTED one to reach
> a quorum is how a quorum is faked."

The bucket key **is** the denominator separation. Nothing tests it.

**Proof.** I added one adversarial row — same task, same records, same
participants, **different corpus** — to a copy of `rows.jsonl`:

| | quorum output | suite |
|---|---|---|
| **baseline** | `gitpp.fold.semantics` → **2 separate buckets** (one per corpus) | 23/23 **green** |
| **mutant** (drop `corpus` from the key) | `gitpp.fold.semantics` → **1 bucket, "2 pass"**, annotated `<-- NOT COMPARABLE` | 23/23 **green** |

The mutant is a clean, plausible refactor — someone tidying the key. It
silently merges two measurements taken over **different corpora** into one
quorum of two passes, and **the suite does not notice either way**. The
`comparable()` function *is* tested (`test/schema.test.mjs:65`, "rows over
different denominators are NOT comparable"), but it is **advisory only** — it
is rendered at `bin/score-table.mjs:40` and never enforced. The bucket key is
the enforcement, and it is untested.

This is a *coverage* gap, not a live bug: today's shipped data cannot trigger
it, because the row that differs in participants is already excluded for being
underpowered. But the repo's entire thesis is "a quorum is faked by mixing
denominators", and the one line that prevents it has no regression test.

**Honest note on two other mutations.** Changing the quorum's `pass:` count
from raw `verdict` to `_effectiveVerdict` is an **equivalent mutant** — a row
can only be underpowered *or* in `usable`, never both, so the two agree inside
a bucket. It is not a defect. My deliberate no-op control also stayed green,
which is what a control should do and is the reason I trust the rest of the
table.

---

# 4. witness-spec — the RFC vector that is not the RFC

`SuperInstance/witness-spec` — created **2026-10-18**, 21 tracked files, no
dependencies, `node test/all.mjs` runs with no install. It gives the fleet's
witness log three things it never had: **RFC 8785 (JCS) canonicalisation**,
**RFC 6962 domain separation** (0x00 leaf / 0x01 node), and a **signed tree
head** as an external anchor.

The most valuable thing in it is a decision most suites get wrong: **the
conformance vectors are the RFC's own**, not self-generated — RFC 8785 §3.2.3
(the sort-order object with `€` / `\r` / `וּ` / `1` / `😀` / `\u0080` / `ö`),
§3.2.2 (primitive serialization), and Appendix B's 15 number samples including
`5e-324`, `1.7976931348623157e+308` and `1e+21`.

> "A conformance suite that only tests itself against its own author is not a
> conformance suite. These vectors come from the specification."

The repo also ships `tools/mutate.sh` and a `MUTATION.md` that documents a real
near-miss — the first version mutated the working tree in place, a killed run
left the tree broken, and a later commit **pushed the broken implementation**.
It now copies to a temp directory, mutates, and throws the copy away. I ran
their harness:

```
baseline (unmutated) -- expect 0 failures     # pass 11 # fail 0   clean, as it must be
M1: sort by code point instead of UTF-16        # pass 8  # fail 3   caught
M2: wrong integer serialisation                 # pass 10 # fail 1   caught
M3: leaf and node prefixes collide              # pass 10 # fail 1   caught
M4: the anchor accepts anything                  # pass 10 # fail 1   caught
M5: the node uses the leaf prefix                # pass 10 # fail 1   caught
restored -- expect 0 failures                    # pass 11 # fail 0   clean, as it must be
all 7 expectations met
```

Their harness is honest. My independent mutation run:

| # | mutation | result |
|---|---|---|
| M1 | leaf prefix == node prefix (kill domain separation) | **RED** (1 fail) |
| M2 | node prefix == leaf prefix (swap) | **RED** (1 fail) |
| M3 | sort by code point instead of UTF-16 code unit | **RED** (3 fail) |
| M4 | canonicalise `-0` as `-0` | **RED** (2 fail) |
| M5 | **control-char escape threshold `0x1f` instead of `0x20`** | **GREEN — undetected** |
| M6 | zero serialises as `0.0` | **RED** (2 fail) |
| M7 | leaf hash has no domain-separation prefix | **RED** (1 fail) |

**M5 is a direct RFC 8785 violation.** §3.2.2.2 requires control characters
U+0000–U+001F to be escaped. The implementation is

```js
else if (code < 0x20) out += '\\u' + code.toString(16).padStart(4, '0');
```

Relaxing it to `code < 0x1f` leaves U+001F unescaped, and the suite stays
**11/11 green** — because the published vectors contain no U+001F.

The honest reading: *conformance to the published vectors* is not *conformance
to RFC 8785*. Using the RFC's vectors is right and rare; it is not
exhaustive. A second, smaller gap: RFC 8785's own test data does not cover
every escaping rule, so a canonicaliser can be wrong in a region the vectors
never touch. One extra vector fixes M5.

Two smaller things: the repo commits `ref/__pycache__/chain.cpython-311.pyc`
and `ref/__pycache__/jcs.cpython-311.pyc` — committed bytecode, from a local
run.

**CI here is genuinely excellent** and worth copying: it runs the Node suite
*and* a Python twin that must reproduce every vector **byte for byte**, then
asserts the chain, the head, and the signature.

---

# 5. Eleven repos that commit one Mac's `npm install`

Not one repo — **eleven**, and the numbers are starker than the fleet's
previous worst case (`substrate-attest-rs`: 430 of 434 tracked files were build
output).

| repo | tracked files | of which `node_modules` | on-disk | `@rollup` / `@esbuild` |
|---|---|---|---|---|
| Equipment-Monitoring-Dashboard | 6,528 | 6,483 | 106 MB | arm64 only |
| Equipment-Hardware-Scaler | 1,631 | 1,616 | 65 MB | arm64 only |
| Equipment-Self-Improvement | 1,034 | 1,018 | 59 MB | arm64 only |
| Equipment-Teacher-Student | 1,033 | 1,018 | 59 MB | arm64 only |
| Equipment-CellLogic-Distiller | 986 | 940 | 71 MB | arm64 **+** x64 + musl |
| Equipment-Memory-Hierarchy | 1,012 | 994 | 64 MB | **none** |
| Equipment-Escalation-Router | 951 | 924 | 92 MB | **none** |
| Sandbox-Lifecycle-Manager | 965 | 908 | 56 MB | arm64 only |
| SuperInstance-Starter-Agent | 934 | 908 | 56 MB | arm64 only |
| SuperInstance-SDK1 | 928 | 908 | 56 MB | arm64 only |
| snapkit-js | 969 | 963 | 58 MB | x64 only |

**Totals: 16,971 tracked files, of which 16,680 (98.3%) are `node_modules`.
The real source and config across all eleven repos: 291 files (1.7%).**

`Equipment-Hardware-Scaler` is 1,895 lines of TypeScript across 4 source files
and 1 test file, behind 1,616 vendored dependency files.

## The committed tree is a snapshot of one machine, and it is the wrong one

Eight of the eleven carry only `@rollup/rollup-linux-arm64-gnu` and
`@esbuild/linux-arm64` — an **Apple Silicon** install. `snapkit-js` carries
x64 only. `Equipment-CellLogic-Distiller` carries both, so it was installed on
two machines or forced.

Consequence, measured in a clean clone of `Equipment-Hardware-Scaler`:

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '@rollup/rollup-linux-x64-gnu'
Require stack:
  - /…/Equipment-Hardware-Scaler/node_modules/rollup/dist/native.js
```

**The committed install cannot run the test suite it was committed to support,
on the platform CI uses** — `ubuntu-latest` is x64.

## And it is dead weight for CI anyway

Every workflow in this family runs:

```yaml
- run: npm ci
```

`npm ci` **deletes `node_modules` before installing**. So 16,680 tracked files
across eleven repos — 56–106 MB each — contribute *nothing* to the build that
produces the green checkmark. The `node_modules` tree is not merely
unnecessary, it is inert: the CI job throws it away and reinstalls from
`package-lock.json`.

Worth being precise about what is *not* broken: the **lockfile is correct**.
`package-lock.json` does contain the x64 optional variants
(`@rollup/rollup-linux-x64-gnu` appears 3×, `@esbuild/linux-x64` is present),
because npm records every platform variant and installs the right one at
install time. The defect is the committed *tree*, not the manifest.

## Not the cosmetic-ignore variant

| repo | `.gitignore` tracked? | mentions `node_modules`? |
|---|---|---|
| Equipment-Hardware-Scaler, Equipment-Teacher-Student, Equipment-Self-Improvement, Equipment-Memory-Hierarchy, Equipment-Escalation-Router, Equipment-Monitoring-Dashboard, Sandbox-Lifecycle-Manager, SuperInstance-SDK1 | **no** | — |
| Equipment-CellLogic-Distiller, SuperInstance-Starter-Agent, snapkit-js | yes | **no** |

Eight of eleven have **no `.gitignore` at all**; the other three have one that
does not mention `node_modules`. This is *not* the `superinstance-api` pattern
(`.gitignore` lists `.wrangler/` while the file stays tracked) — the ignore
rule is entirely absent.

## The duplication is literal

Three repos carry a **byte-identical path list** for their vendored tree:

```
311fdbe5: Sandbox-Lifecycle-Manager, SuperInstance-Starter-Agent, SuperInstance-SDK1
23fbe87c: Equipment-Self-Improvement, Equipment-Teacher-Student
```

2,724 tracked files of the same vendored dependency tree, committed three
times over. This is the fleet's own `file:../` monorepo pattern (as in the 13
`substrate-*` repos) gone one step further: instead of declaring the dependency,
the dependency is copied in, in full, from one machine's disk.

**Fix, in order of value:** (1) `git rm -r --cached node_modules` and add
`node_modules/` to `.gitignore` in all eleven; (2) `npm ci` already makes CI
correct, so nothing else needs to change for the build to stay green; (3) for
the two repos with no `@rollup`/`@esbuild` at all, the committed install is
incomplete even on the authoring machine.

---

# Negative findings — things that checked out well

Reporting these because they are the receipt on everything above.

- **witness-spec's CI is the best in this set.** It runs the Node suite *and* a
  Python twin that must reproduce every vector byte for byte, then asserts the
  chain, the head, and the signature. Two independent implementations, one
  rule.
- **witness-spec's `tools/mutate.sh` works on a copy** and `MUTATION.md`
  documents the incident that taught it to: a killed run had left a mutated
  tree that was then **pushed**. A harness that can break the thing it
  verifies is itself a defect, and this repo says so in its own README.
- **score-table's CI asserts a non-zero exit** while a measurement is
  outstanding, and its shipped data includes the counterexample row that
  explains why `NOT_MEASURED` exists. Refusing a row that does not declare its
  denominator, tolerance and receipt is implemented, not just promised.
- **SmartCRDT's badges are honestly red.** Both `ci.yml` and `pr-validation.yml`
  read *failing*. It is the opposite of the fleet's dominant pattern, where a
  green badge sits on top of a broken build.
- **quilt-Kuramoto's `REMOVED.md` itemises all 128 deletions** with a recovery
  command for each, and `MISSING.md` records two of the author's own
  corrections — including *"my 'unwired sketch' read was wrong"*. The archive
  is well made; it is the *receipt* that is unaudited.
- **Both of the new zero-dependency repos run with no install at all** —
  `node test/all.mjs` and nothing else. In a fleet where `npm install` is
  routinely the thing that fails, that is worth copying.

---

# Reusable methods

1. **Content-hash, never path-diff, when auditing "is this upstream".** 24 of
   25 `quilt-wiki-2126` files and 41 of 60 `quilt-esp32` files had *moved*
   upstream. A path diff would have accused the archive of 19 files it does
   not own. Content hashing is what separates *real but misattributed* from
   *fabricated* — and it is the only way to avoid a false accusation.
2. **A recorded number is not a gate.** `upstream-delta.json` has a table, a
   JSON file, a `generated` date, and a method string — and no verifier
   anywhere. Ask "what executes this?" If the answer is *nothing*, it is a
   claim, and it is stale the moment the fleet moves.
3. **"The suite passes" ≠ "the property holds".** Ask which scenario the suite
   never *constructs*. The ORSet case: a removal that must **cross** a
   replica. The shipped suite removes on one side and adds on the other, so
   the tombstone never travels.
4. **Audit the identity scheme, not just the algorithm.** The ORSet's merge
   logic is textbook. The bug was in what a *tag* means — per call instead of
   per (element, replica). A correct algorithm with a wrong identity is a
   wrong implementation.
5. **A `|| true` swallows a missing script as happily as a failing test.**
   `npm run test:property` → `Missing script`, exit 1, `|| true` → step
   passes. Run the script by hand and capture the exit code; a green job that
   runs nothing is worse than a red one.
6. **Read the assertion, not the comment.** `// All should converge to same
   state` above `expect(state1).toBeDefined()` is a convergence check that
   asserts existence.
7. **Date a committed `node_modules` by its platform binaries.** The contents
   of `@rollup/*` and `@esbuild/*` say which machine wrote it and whether it
   can run where CI runs.
8. **Badge provenance:** a repo whose badge is red is *more* trustworthy than
   one whose badge is green. `plato-portal` was green and 100% broken;
   SmartCRDT is red and honestly so.

---

# Environment notes (durable)

- **`/workspace` is a NAS mount at 100% (EDQUOT).** Writes there succeed and
  produce **0-byte files** with no error. All work was done in `/tmp`.
- **Core GitHub API limit is 5,000/hour.** 3,429 `git/trees?recursive=1` calls
  exhausted it mid-run. `git clone --depth 1` is not rate-limited, gives real
  tree bytes, and satisfies the clean-clone rule directly. Prefer clones for
  substance measurement.
- **`npm install` fails in this sandbox** with `Unknown system error -122` on
  `close` (npm's own teardown, under `/tmp`). Workaround used: borrow a
  working x64 `node_modules` from another clone
  (`Equipment-CellLogic-Distiller` has **both** arm64 and x64
  `@rollup`/`@esbuild`) as a `vitest` runner for a different repo.
- **`GIT_SSL_NO_VERIFY=1` is required for every clone** — the sandbox CA
  bundle does not trust GitHub.
- **No cargo/rustc/julia.** Rust repos in this set (`quilt-vm-c`,
  `quilt-verilog` upstream) were inspected, not executed. No claim is made
  about their test results.
- The `write` tool cannot reach `/tmp`; all file writes there went through
  shell heredocs, which is also the reliable path given the `-122` quirk.
