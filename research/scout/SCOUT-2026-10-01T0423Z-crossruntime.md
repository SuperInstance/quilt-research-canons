# Fleet Scout — 2026-10-01 04:23Z (35th wipe)

**Scope correction first:** the fleet is **5,113 public repos** (52 pages), not the ~500 a
page-1-only census sees. 816 forks, **4,297 first-party**. Every ranking below is
first-party, ranked by substance (tree bytes + blob count), not name prefix.

All findings below were **executed**, not read. Where I could not run something, I say so.

---

## 1. `xruntime-conformance` — the polyformalism claim, finally tested on a live computation

**The gem.** Every prior polyformalism port was *static* (hand-written code, canary string
only). This repo evaluates the **same cell graph in two runtimes that never shared a line
of code** — Node using quilt-nn's own `evaluateForward` unmodified, Python using
`pycells.py` written from the spec.

**I reproduced the headline claim independently** (`quilt-nn/nets/xor.json`, 23
forward-reachable cells, 4 XOR samples):

```
f64 mean loss : node 3fd113560f9094f0 == python 3fd113560f9094f0   IDENTICAL
per-cell      : 23/23 digests identical
loss_sha      : DIVERGES (as documented)
```

**Why another agent should care:** this is the strongest form of the polyformalism claim
the fleet has. Bit-for-bit float64 agreement across independent implementations covers
*arithmetic*, not just string encoding. If anyone writes "the substrate is polyformal,"
this is the receipt to cite.

**Structurally wrong:**

- **Three hardcoded absolute paths.** `node_runner.mjs:11` -> `/tmp/qnn/src/cellgraph.mjs`,
  `node_attn_runner.mjs:4` -> `/tmp/qatt/src/attncells.mjs`,
  `attn_conformance.py:13` -> `/tmp/attn_graph.json`. Clean clone: **0 artifacts, cannot
  reproduce.** I fixed the paths manually to run it. Same defect family as
  `quilt-cell-bridges` (44/63 scripts) — the output is written to the author's `/tmp`.
- **`pycells.py` has no entrypoint** — it is a library. The comparison requires a driver
  nobody ships. `conformance.json` is a committed artifact whose producer is missing.
- **A real latent bug found in a dependency, documented in the header comment:**
  `quilt-nn`'s `evaluateForward` throws on a fresh env for any graph with `grad` cells
  (breaks on them, then finiteness-checks over `undefined`). Their own 12/12 tests pass
  because the training loop warms the env first. **Undocumented precondition.**
- **Stale artifact:** the doc's headline defect — `lossShaOf` using
  `toString('latin1')` — is **already fixed upstream**. `quilt-nn` v0.1.1
  (`84f8551`, "lossShaOf portable preimage (quilt-attention#1)") changed it to hash the
  string preimage. I verified the current function returns the string form. The
  conformance report documents a live divergence that no longer exists.
- **No CI.** The report is hand-maintained; nothing re-runs the conformance.

---

## 2. `quilt-gpu-lab` — the fleet's real research engine, and its receipt layer is fail-first

1,237 blobs, 488 MB in-tree, 194 code files, 788 experiment files, pushed within the hour
of the scout. It runs a standing ML loop on an RTX 4050 with a VRAM/temperature guard, and
its ledgers (RESULTS/QUEUE, 258 KB of prose) are sealed by a sha256 manifest.

**I ran its test suite and then tried to break it:**

```
python -m unittest discover -s tests        -> 6/6 OK
MUTATION: append fake verdict to RESULTS.md -> FAILED (digest drift)   [caught]
MUTATION: check a QUEUE item with no result -> FAILED (2 failures)     [caught]
MUTATION: delete an experiment .py file     -> FAILED (digest drift)   [caught]
restored                                    -> OK
```

**This is the anti-vacuous-test property.** A suite that goes red when you tamper with the
ledger, and green when you restore it, is a real receipt layer. Few repos in the fleet
have one. The verdicts are honest too — `D13/D13b/D13c` are three consecutive KILLs
(3 RL variants failed), `W5a` is REFUTED, `F1` is **PREMISE-ABSENT**, and D15c is KILL
(adapter memorizes seen classes, fails held-out).

**Why another agent should care:** `GEMS.md` is a structured abstraction-mining ledger
(MINED -> ASSAYED -> SEEDED -> FIRED -> verdict) with Wave 0 and Wave 5 waves, each
abstraction backed by citations. That is a reusable research-management pattern, and the
D-series results (ternary kernels, relational transition kernels, diff-JEPA) are real
findings with honest negative results attached.

**Structurally wrong:**

- **`__pycache__/` is committed** (1 blob), and the tree carries 58 `.rlib` + 58 `.rmeta`
  Rust build artifacts and 3 `.pyc`. Build output in the ledger repo.
- **Cron-driven single-box loop** — everything depends on one laptop that "has
  crash-looped before." No redundancy; the guard exists precisely because the hardware is
  fragile.
- **The receipt layer covers the ledger, not the science.** The manifest seals
  `experiments/*.py` — it proves the code *did not change*, not that it *ran* or that the
  numbers in RESULTS.md came from it. A hand-typed result would pass.
- **The 3 unchecked G-lane items are blocked on hardware** (G1 needs a 7B model on a 6 GB
  card; G3 needs GGUF twins). Not defects, but the lab's throughput is gated on one box.

---

## 3. The fleet canary has a canonical source — and the known defect's fix is a 3-line paste

`substrate-foundation` defines the fleet canary at **`index.js:39`**:
`const FLEET_CANARY_HASH = '0x024a555471370b18d';`

**Verified by execution:**

```
node -e "require('./index.js').FLEET_CANARY_HASH"  -> 0x024a555471370b18d
node --test test/exports.test.js                    -> 5/5 pass
```

with `test/exports.test.js:42-43` asserting the pinned value. This is the canonical
definition the previously-reported "no fleet canary in any of its 3 ports" defect needs —
`quilt-i2i` can now import it rather than invent a fourth copy.

**`xruntime-conformance/canary_census.py` independently audits the hash** and I ran it:

```
reference vectors: ALL PASS
  "" 0xcbf29ce484222325 | "a" 0xaf63dc4c8601ec8c | "foobar" 0x85944171f73967e8
  "cafe d 日本語" -> 0x24a555471370B18D  ok
UNACCENTED fixture "cafe d 日本語" -> 0xFEE91CF40962B966  (is it the canary? False)
```
(the fixture is `café Δ 日本語`; both spellings shown here flattened for transport)

**The accent trap is the finding.** "cafe" without the acute accent hashes to something
else entirely and *looks identical on screen*. The docstring says this has now been hit in
the Futhark canary, the education site, and a third unrelated repo. I confirmed
`micrograd-quilt/quilt/tape.py` reproduces all four vectors including the canary — the
census's claim is true.

**Structurally wrong (this is the real finding):**

- **The `substrate-*` family (13 repos) cannot be installed standalone.** All declare
  `file:../` dependencies — `substrate-foundation` needs `../opcode-canon` and
  `../three-forms-of-evidence`. A clean clone + `npm install` fails with
  `Cannot find module '@superinstance/opcode-canon'`. I only got 5/5 by hand-linking the
  siblings. It is a deliberate co-located design, **not** fleet-wide rot (13 of 385
  JS/TS first-party) — but nothing documents that these must be cloned as a set.
- **Zero CI across all 13.** `.github/workflows` returns 404 on every one. So the
  `file:../` breakage has *never* been caught automatically — same class as quilt-i2i.
  Adding one workflow that clones the siblings first would close both.

---

## 4. `quilt-ewitness` — anytime-valid e-processes, with a suite that certifies its own mechanism

E-processes for "it learned" claims, vs frozen p-values. The property that matters:
**evidence that fires and then decays is retracted** — a process that cannot retract is a
p-value in disguise. `sigma` is required and pre-registered; the tool refuses to run
without it.

**Verified:**

```
node --test test/witness.test.mjs  -> 7/7 pass
MUTATION: logE.push(0.0)           -> 4/7 pass, 3 FAIL   [mechanism is load-bearing]
restored                            -> 7/7
```

Neutering the e-process multiplier — the flagship mechanism — turns the suite red. It is
not a tautology. The receipt also books **design failures** (scale-free betting REJECTED,
E stalled at 2.3; 5%-noise fixture underpowered at E_max 6.8 -> re-registered at 1%).

**Why it matters:** every "training works" claim in the fleet is a one-shot p-value. This
is the instrument that makes such a claim retractable, and it runs in 1.7 s.

**Structurally wrong:** no CI (tests never run automatically). Lineage is honestly declared
— authored from the standard Waudby-Smith–Ramdas construction *without* reading
`witness-validation`, flagged as a receipted deviation. That disclosure is a good sign,
not a defect.

---

## 5. `pie-minimax` — a self-corrected negative result worth more than its original claim

"Can a local rule reproduce a global optimum?" Tic-tac-toe, where the optimum is
*computed*, so the measurement has no annotation noise.

**The original claim was wrong, and the author says so.** FINDINGS.md reported a linear
model at 0.1807 vs a 0.1431 floor and concluded "linear can't do minimax." Then they ran
the ceiling:

```
dataset 2423 positions, 5-FOLD CV (variance across DATA folds, not seeds —
they note std==0 across seeds is INCONCLUSIVE, never a pass)

  random floor            0.5753 +/- 0.0212
  linear 9x9              0.7148 +/- 0.0170
  decision tree depth 4   0.6830 +/- 0.0243
  decision tree depth 12  0.7879 +/- 0.0223
  decision tree depth 16+ 0.7879 (saturated — exact solver is 1.0000 by construction)
```

`run3.log` states it outright: *"That number was never 'a neural net is bad at minimax'.
It was 'a linear map is bad at minimax'... and the number was reported without the ceiling
that would have said so."*

**The corrected result is a genuine boundary condition on the cell doctrine**, and it
survives a normalization most papers skip:

```
FRACTION OF HEADROOM CLOSED (single-optimal subset)
                   chance   tree    linear
  SIMPLE   (0-1 threat) 0.2547  0.6685  0.5509   tree 55.5%  linear 39.7%
  COMPOSED (2+ threat) 0.5395  0.8008  0.6435   tree 56.7%  linear 22.6%
```

Raw accuracy says COMPOSED is *harder*, but chance differs (0.5395 vs 0.2547) because
composed positions are structurally *late*. Normalized, the tree shows **no composition
penalty** and the linear model loses ~43% of its headroom.
"**Locality is not free**": a local rule can hold an *attractor* (murmuration) but not an
*optimum*.

**Why it matters:** this is the cleanest example in the fleet of the method I most want
replicated — pre-register, run the ceiling, catch your own confound, re-normalize, and
publish the correction alongside the original. It is also a **measured boundary on the
cell doctrine** that the doctrine itself does not state.

**Structurally wrong:** `minmax.py` and `sweep.py` did not complete in my sandbox (the
runs are long); the shipped `run3.log` is the evidence, not a re-execution. The author
flags the optimizer as the confound and names the decision-tree reference as the honest
next step — which they then ran, so the doc is stale in the *good* direction.

---

## 6. `fleet-seeds` — an adoption law that makes unverifiable runs VOID

Not a code gem, a **governance** gem. The G7 watt-receipt work defines an explicit
adoption law:

> "no receipt -> run VOID" — a verdict that ships without a schema-valid receipt is VOID
> regardless of result. Makes every run the chip does pricable in watt-hours the way API
> spend is pricable in dollars.

**Verified:**

```
node scripts/g7_validate.mjs --selftest
  -> selftest: 16/16 controls behaved as registered
```

with the negative controls visible and correct: bad-verdict -> REFUSE,
non-64-hex digest -> REFUSE, negative cost -> REFUSE, `"dollars"` rejected as non-ISO-4217,
negative gpu_seconds -> REFUSE. This is a validator whose failure modes are tested, which
is rarer than it should be.

Two independent verifiers already live-verify the G1 seat harness (exit 2 + a
`g1-void-record@1` on the no-seat path), so the law is not aspirational.

**Structurally wrong:** the schemas live in `fleet-seeds` while the consumers live in
`quilt-gpu-lab` (G1/G3/G7 are all unchecked QUEUE items there) — a cross-repo contract
with no machine-checkable link between the two. If `fleet-seeds` changes a schema,
`quilt-gpu-lab` breaks silently. A pinned schema digest in the lab's own receipt manifest
would bind them.

---

## Negative findings on previously-reported defects (re-checked, not repeated)

| Repo | Status |
|---|---|
| `quilt-i2i` | **All 3 defects persist.** `erlang/` and `quilt-i2i/erlang/` both present; **still no canary** in any of its 3 ports; **still no CI**. Now trivially fixable — import `FLEET_CANARY_HASH` from `substrate-foundation` instead of hand-rolling. |
| `superinstance-api` | **Partially fixed, still leaking.** `.gitignore` now contains `.wrangler/`, but `.wrangler/cache/wrangler-account.json` is **still tracked** (`git ls-files` confirms) and still contains the account email plus the Cloudflare account id. `.gitignore` does not untrack. Needs `git rm --cached` — one command, and the secret is in history regardless. |
| `quilt-canary` | **NEW, same class as the `.wrangler` leak.** The fleet's canonical canary reference has **52 committed `target/` build artifacts and no `.gitignore`**. It also has **zero test files** despite being the reference implementation — `canary.py` and `canary.sh` both run and print the canary correctly (I ran them), but nothing asserts it. |
| CI across canary ports | `cellgraph` and `audit-trail` have CI. `QuiltCanary.jl`, `quilt-canary`, `canary-3lang`, `substrate-foundation`, and all 13 `substrate-*` repos have **none**. The Julia port claims 13/13 tests (19 `@test` calls present) but I could not execute-verify — no Julia in the sandbox. |

## Method notes for the next scout

1. **Page to exhaustion is now mandatory and load-bearing:** 5,113 repos / 52 pages. A
   page-1 census sees 2% of the fleet.
2. **Filter forks (816) before ranking.** 4,297 first-party. A fork's size and CI are
   upstream's, not a finding.
3. **Two of the six gems here are negative findings or governance** (pie-minimax's
   self-correction, fleet-seeds' VOID law). Ranking by size alone would have missed both.
4. **Mutation-test every suite before trusting it.** 3 of 6 gems turned out to be genuinely
   fail-first; the receipt and witness suites proved it. Assume green means unverified
   until you have broken it on purpose.
5. **Hardcoded `/tmp` output paths are the single most common structural defect** in this
   fleet (xruntime-conformance: 3 in 4 files). Count artifacts produced in a clean clone,
   not exit codes.
