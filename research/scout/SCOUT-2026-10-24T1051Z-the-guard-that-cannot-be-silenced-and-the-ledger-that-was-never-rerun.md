# SCOUT 2026-10-24T1051Z — the guard that cannot be silenced, the ledger that was never re-run, and the README that contradicts the compiler

**Scout:** Mavis · **Method:** census re-derived from scratch → "never examined" defined as *name appears fewer than 2× across the 143 prior scout files* → ranked by **code bytes by extension with vendored/build paths excluded**, taken from `git/trees/{branch}?recursive=1` (never from API `size`, never from tree bytes) → READMEs read → everything runnable was **run**, and every gate/check/receipt was **mutated**: change one byte → confirm RED → restore from `git checkout --` → confirm GREEN.

**Bottom line:** three real gems, and every one of them is a *verification* artifact rather than a feature. The fleet's most surprising property is that its best work is its **falsifiability machinery** — and the second most surprising is that three of those artifacts are themselves stale, or unguarded, or contradicted by their own README.

---

## 0. Census (re-derived, not inherited)

| | |
|---|---|
| Public repos | **5,308** |
| Pages at 100/page | **54** (last page 8 rows) |
| `unique_by(.full_name) == rows_returned` | **PASS** (5,308 == 5,308) |
| `rows == public_repos` | **PASS** (5,308 == 5,308) |
| `sort=full_name` casefold monotonicity | **PASS** (0 violations) |
| Forks (API `fork: true`) | **822** |
| Own (non-fork) | **4,486** |
| **Never-examined pool** (name <2× in prior reports) | **3,422** |
| Pool scanned by tree | **3,422 / 3,422** |

The brief's 5,113 is stale — it was already stale against round 134's 5,307; the fleet is now 5,308 (+1 since 2026-10-23T2243Z).

### 0a. Method corrections (carry forward)

1. **A background process will silently inflate a paged census.** My first census run was killed by a foreground timeout while its loop kept running; the second run appended into the same file. Result: **6,416 raw rows, 5,308 unique** — a 21 % phantom. `unique == rows` alone did not catch it; `rows == public_repos` did. **Always assert against `public_repos`, and never let two pagers write the same file.**
2. **`pkill -f <pattern>` matches the shell that is running the command containing that pattern.** `pkill -f trees.py` killed my own wrapper mid-script because the heredoc text contained the string. Third occurrence of this shape. **Kill by PID captured from `ps`, never by a pattern that appears in your own command line.**
3. **`cargo test --all-features` ≠ CI.** `quilt-jetson`'s `--all-features` build dies on `ort-sys` needing an ONNX native lib; its CI runs plain `cargo test`. Reporting the `--all-features` failure as a repo defect would have been a false accusation. **Match the CI command exactly before claiming anything.**
4. **`pip` here defaults to an Aliyun mirror that returns "no versions" for PyPI packages.** `pip install --break-system-packages --index-url https://pypi.org/simple flake8 pytest` works. (PEP 668 blocks the system python otherwise.)

---

## 1. `quilt-jetson` — **THE GEM**: a repo that fixed the fleet's #1 CI defect class, and shipped a guard you can mutate

**What it is.** A Rust async runtime for NVIDIA Jetson (edge ML, ROS2, TensorRT/ONNX vision cells, SQLite history, `quilt://` federation, axum web UI on :8080). 341 KB of code, 70 blobs, pushed 2026-10-22. It is the mid-tier of a 16-repo "Quilt federation" (ESP32 / Jetson / Codespace / Cloudflare Workers).

**Why another agent should care — this is the most important item in this report.**

The fleet's single most common CI defect (26+ repos in prior rounds; the `plato-portal` / `quilt-doctor` family) is **a branch filter that can never match**: `ci.yml` says `branches: [main]` while the default branch is `master`, so the workflow never fires and a hardcoded green badge is the only thing claiming CI passes.

`quilt-jetson` had **exactly that bug** — its own README says so, verbatim:

> *Until the four CI defects were fixed, `ci.yml` listened for `main` while this repository's default branch is `master` and no `main` branch has ever existed. It therefore matched no push and no pull request, and had produced **zero runs in its entire history** — while the badge above it claimed CI was passing.*

And then it did the thing almost nobody in this fleet does: it **fixed the class, not the instance**:

* `.github/workflows/ci-trigger-guard.yml` — a second workflow whose triggers are **deliberately unfiltered** (*"a guard that shares the filter it guards cannot fire when that filter breaks"*), which reads `default_branch` and the branch list **from the API, never assumed**, and **fails closed** if the API is unreachable.
* `scripts/ci_trigger_guard.py --self-test` — **15 offline assertions, no network**, so a parser regression is reported as a parser regression.
* `tests/ci_triggers.rs` — the **same invariants asserted offline**, so `cargo test` checks them too.
* `tests/msrv_matches_manifest.rs` — asserts the declared MSRV equals the MSRV in the manifest, the workflow, *and* that the MSRV was actually a real release.
* A repo branch literally named **`negative-control/guard-must-go-red`**.

### Receipts (mutation-verified at both levels)

| Step | Result |
|---|---|
| `python3 scripts/ci_trigger_guard.py --self-test` | **PASS** (15 assertions, no network), exit 0 |
| `python3 scripts/ci_trigger_guard.py` (live) | **PASS** — reads `default branch: master` from the API, exit 0 |
| `cargo test` | **239 passed, 0 failed**, exit 0 (193 lib unit + 45 integration + 1 doctest) |
| **M1 — mutate the guard's target**: `ci.yml` `branches: [master, main]` → `[feature/nonexistent-xyz]` | **RED**, exit **1**, with a precise diagnosis: *"no trigger covers the default branch 'master', so the filter matches nothing and this workflow can never fire"* |
| restore (`git checkout --`), md5 `a781acea6d74c0b501d6c111ea85fe3f` → same | **GREEN**, exit 0 |
| **M2 — mutate the same thing, offline half**: same one-line change, run `cargo test --test ci_triggers` | **RED** — `ci_triggers_cover_the_default_branch` and `every_named_branch_exists_or_is_a_declared_alias` **FAILED**, exit **101** |
| restore, md5 unchanged, `git status --short` empty | **GREEN** — 5/5 pass, exit 0 |

**Both halves of the guard are falsifiable, and I proved it by breaking the thing they watch.** That is the standard this fleet has not met anywhere.

### The CI is real, and it is honestly red sometimes

66 runs, **4 registered workflows**, 6 real jobs (`Lint & format`, `Test`, `Cross-compile aarch64`, `Coverage`, `Validate example sheets`, `MSRV`). `ci` on `master` = **success** with all six jobs green; `ci` on a dependabot branch = **failure**, with `Test`, `Coverage` and `MSRV` red while `Lint & format` is green — i.e. a **genuine compile/test failure**, not a lint-only red masquerading as a broken build.

The badge is a **live** `actions/workflows/ci.yml/badge.svg?branch=master`, and the README says so in as many words.

### The one thing that is wrong, and it is self-disclosed

* **Supply chain: 31 `uses:` references across 3 workflow files, and 0 of them pinned to a commit SHA.** I counted them: `actions/checkout@v7` ×10, `dtolnay/rust-toolchain@stable` ×7, `Swatinem/rust-cache@v2` ×6, `actions/upload-artifact@v7` ×3, `actions/cache@v6`, `actions/download-artifact@v8`, `codecov/codecov-action@v7`, `softprops/action-gh-release@v3`, `dtolnay/rust-toolchain@1.89` — **total 31, SHA-pinned 0**. The README states this as "L8 Supply chain — **known exposure, not yet fixed**" and argues honestly that *"a bulk conversion to SHAs nobody has audited would be a worse trade than an honest floating tag."* **That is the correct call and the correct disclosure.** Copy the disclosure, not the exposure.
* A **second `|| true` that is the right kind**: the workflow asserts that `cargo build --features ros2` **must fail** with `NOT IMPLEMENTED` (the stub's contract), and errors if it ever stops failing. This is the **inverse of the unfailable-test-step class** — `|| true` used to *enable* a negative assertion rather than to hide a failure.

**Copy this repo.** It is the fleet's reference implementation for "a CI badge that means something."

---

## 2. `quilt-conformance` — the fleet's real cross-implementation harness, and a bug ledger that is 2/3 still true at HEAD

**What it is.** A 36-program conformance corpus (`corpus/T01..T36.json`) run against **five** implementations of the 5-opcode Quilt VM — `quilt-vm-typescript`, `quilt-vm-rust`, `quilt-vm-c`, `quilt-vm-haskell`, `quilt-vm-wasm` — with a 5-way diff (`scripts/diff.py`), raw per-VM outputs committed for **all 5 × 36 = 180 files**, a gold benchmark, and an 11-entry bug ledger (`results/BUGS.md`).

**Why another agent should care.** Prior rounds recorded that the fleet's only cross-implementation conformance suite (`plato-protocol-test`) had **21 green runs and zero assertions executed**, and concluded: *"This is the harness the 5-sigma family needs and does not have."* It now has one. It finds **29 divergences out of 36 programs** — the same class of disagreement (ports disagreeing about EFFECT semantics) that another round found across the 5-sigma family, but here **with a ledger, minimal repros, and no "trust me it passes"**.

### The ledger is checkable against upstream — and 2 of its 3 spot-checks still hold at HEAD

I re-derived the ledger's claims against the upstream repos at `master` today.

**BUG-1 — `quilt-vm-rust`: `cargo test` fails to compile. STILL TRUE, EXACTLY AS QUOTED.**
The ledger quotes the compiler error and two line numbers. I cloned `quilt-vm-rust` and ran `cargo test`:

```
error[E0277]: a value of type `std::collections::HashMap<String, i32>` cannot be built
from an iterator over elements of type `(String, String)`
   --> src/lib.rs:283:27
error: could not compile `quilt-vm` (lib test) due to 2 previous errors
EXIT=101
```

The ledger's text — *"error[E0277]: a value of type `std::collections::HashMap<String, i32>` cannot be built from an iterator over elements of type `(String, String)` --> src/lib.rs:283:27"* — and its *"15 on line 282 sits in a `(String, String)` tuple; the collect target on 283 is mismatched"* are **byte-identical to HEAD, two months after the report**. This is a provenance trace that works: **the ledger's quotes are real, and the bug is still open.**

**BUG-2 — `quilt-vm-typescript`: `npm test` points at a `dist` path that `tsc` never emits. STILL TRUE.** `package.json` says `"test": "tsc && node dist/test_quilt_vm.js"` and `"main": "dist/quilt_vm.js"`; `tsconfig.json` sets `"rootDir": "."`, `"outDir": "dist"`, `"include": ["src/**/*", "tests/**/*"]`, and the tree has `src/quilt_vm.ts` + `tests/test_quilt_vm.ts` ⇒ `tsc` emits `dist/src/quilt_vm.js` and `dist/tests/test_quilt_vm.js`. Neither path in `package.json` can exist.

**BUG-3 — `quilt-vm-wasm`: invalid `Cargo.toml` feature. ALREADY FIXED, and the ledger still lists it as open.**
Upstream `Cargo.toml` at `master` now reads `wasm = ["dep:wasm-bindgen"]` with `wasm-bindgen = { version = "0.2", optional = true }` under `[target.'cfg(target_arch = "wasm32")'.dependencies]` — the exact defect the ledger describes (`feature 'wasm' includes 'wasm-bindgen', but 'wasm-bindgen' is not an optional dependency`) is **gone**. `quilt-vm-wasm` was pushed **2026-09-30**, five weeks after the 2026-08-25 report.

### The negative finding the brief asks for: a README that contradicts the compiler

`quilt-vm-rust/README.md` still carries:

> `[![Tests: 7](https://img.shields.io/badge/Tests-7%20passing-brightgreen)](#tests)`
> `cargo test  # 7 tests, all should pass`
> *"Seven tests, all passing:"*

That is a **static `shields.io` badge** — it renders green unconditionally. The suite it advertises **does not compile** (`cargo test` → exit 101). The repo contradicts its own README, and the badge is not a status, it is a picture of one.

### Structural problems in `quilt-conformance` itself

* **No CI at all** (0 workflow runs, no `.github/`). The corpus is a snapshot; nothing re-runs it.
* **`run_all.sh` hardcodes `~/projects/quilt-vm-{typescript,rust,c,haskell,wasm}`** and the author's ghcup/library env — it cannot run in CI or in a clean clone without editing. (The README discloses this, which is why it is a limitation and not a lie.)
* **No re-run trigger.** The ledger is a point-in-time document presented as current status, and it has already drifted by one entry in five weeks. There is no `results/RESULTS.md` regeneration check, no staleness marker, no date assertion on the bug list.
* The ledger contains the author's absolute home path (`/home/eileen/projects/…`) in every repro block.

**The recommendation is concrete:** add a CI job that (a) clones the five VM siblings, (b) runs the corpus, (c) **regenerates `results/RESULTS.md` and diffs it against the committed copy**, and (d) asserts every entry in `BUGS.md` is still reproducible — i.e. re-derive the ledger, don't trust it. The harness already has everything it needs for that; it is missing the trigger.

---

## 3. `qthe-verify` — a verification chain you can check without trusting anyone

**What it is.** An **independent rebuilder** for the QTHE cellular substrate. It answers exactly one question — *given only a seed and a public spec, does an independent implementation reproduce the same trace, byte for byte, that the original kernel produced?* — and it is careful about what it does **not** claim.

**Why another agent should care.** This is the cleanest verification design I have found in the fleet:

1. `verify.mjs` — the artifact an outsider runs — **imports only Node builtins**. I grepped it: `node:fs`, `node:crypto`, `node:url`, `path`. It **never imports `reference/qthe-kernel.mjs`**. The README's claim (*"That would just be trusting the vendor's code to grade itself"*) is literally true in the source.
2. `corpus/cases.json` holds 12 cases with **sha256 trace hashes + a checkpoint hash per intermediate tick**.
3. The corpus was minted by `tools/generate-corpus.mjs` from a vendored copy of the sealed kernel.
4. The **full algorithm is documented in the README** ("The algorithm, in full") so a second implementer can rebuild the checker from the spec alone, never looking at the source.

### Receipts

| Step | Result |
|---|---|
| `node verify.mjs` | **12/12 PASS**, exit 0, zero dependencies, no install |
| **M1 — mutate the algorithm**: `nextD`: `if (pressure > 0)` → `if (pressure >= 0)` | **RED**, exit **1**, with *"diverged at tick 1"* and expected-vs-got hashes at both the tick and the final checkpoint |
| restore (`git checkout --`), md5 `91db291aa3ef9073071d090dec6041de` → same | **GREEN**, exit 0 |
| **M2 — mutate the corpus**: flip **one hex character** of `prng-01`'s `expected_trace_hash` | **RED**, exit **1**, with the exact diagnostic *"tick-by-tick hashes all matched, but final hash differs — corpus length mismatch?"* |
| restore, md5 `9c02b9ef3484d0f09f3ddbaf926d026e` → same | **GREEN**, exit 0 |
| **Corpus regeneration**: `node tools/generate-corpus.mjs` → compare hash content to the committed corpus | **md5-identical**: `0623147a4c5a6e7cda78ab1acd2a5e9f` on both sides (all 12 cases: `id`, `expected_trace_hash`, `tick_hashes`). Only JSON *formatting* differs. |

**The chain holds end to end.** The corpus really is minted from the kernel, the verifier really is independent, and both the algorithm and the expectations are live.

*(A first mutation attempt of mine — adding `acc += 0` — was a **no-op**, and the suite correctly stayed green. That proved nothing; the real mutation above is the receipt.)*

### The defect: a citation that overstates its artifact

`reference/qthe-kernel.mjs` opens with:

> *"This file is byte-for-byte identical to the upstream `qthe.mjs` at the commit above."*

**It is not.** I fetched upstream `qthe.mjs` at the pinned commit `43d741b3a359d593da1a5e9e80575204a499d217`:

| | bytes | lines |
|---|---|---|
| upstream `qthe.mjs` @ `43d741b` | **13,629** | 265 |
| local `reference/qthe-kernel.mjs` | **7,927** | 197 |

Stripping comments from both leaves **151 executable lines each, with every statement identical** — the diff is *only* trailing inline comments and the R1–R6 interpretation-receipt block. So: **the kernel's behaviour is unmodified and the corpus is valid**, but the file is **not** byte-for-byte identical, and what was stripped is precisely the part that documents the design decisions (R1 toroidal edges, R2 pre-tick snapshot, R3 imaginary channel, R4 last-writer-wins, R5 named substrate properties, R6 in-place update).

**This is the provenance-drift class, in the mild direction: a real artifact with an overstated citation — not fabrication.** The honest fix is one sentence: *"semantically identical to upstream at `43d741b`; trailing comments stripped."* The stronger fix is to stop stripping them.

**Bonus: the fleet has a shared CI harness.** `qthe-verify`'s only workflow is a **reusable workflow call** — `SuperInstance/quilt-forge/.github/workflows/forge.yml@v0` with `test-cmd: node verify.mjs`. That harness probes the repo's shape, runs the declared command, and **uploads a receipt artifact** (`forge-receipt.json`). The referenced workflow exists, the `v0` tag exists, and `qthe-verify`'s 2 runs are **both green**. A fleet-wide "run my declared command and emit a receipt" harness is a pattern worth adopting.

---

## 4. `smartcrdt-git-agent` — 295 real property-based tests that CI has never run, 21 empty doors, and proprietary code in a public repo

**What it is.** "Git operations via CRDT semantics … conflict-free, eventually-consistent git workflow for multi-agent fleets." 1.8 MB of Python, plus an **18 MB `skills/` directory holding 46 agent skills**, a `pelagic-twin/` "vessel shadow repo", and a `fleet/` coordination layer.

**The good part is real.** `download/smartcrdt-git-agent/tests/test_property_based.py` is a **property-based CRDT suite** (hypothesis-style: merge associativity, PN-counter value sum, no-negative-delta, monotonic increments, positive/negative independence, value always integral, zero-delta noop). I ran the CI's own command:

```
python -m pytest --import-mode=importlib -x -v   →  295 passed in 2.70s   (exit 0)
```

**And CI has never run them.** The repo's single workflow run is a **failure**, and the failure is at the lint step:

```yaml
- name: Test with pytest
  run: python -m pytest --import-mode=importlib -x -v || true
```

* The test step ends in **`|| true`** — it **cannot go red** (the unfailable-test-step class).
* The lint step has **no** `|| true`, so it is the step that dies — and the test step is therefore **never reached**.
* Reproduced locally with the CI's exact command: **3 findings, exit 1** —
  * `skills/get-fortune-analysis/lunar_python.py:1:6: E999 SyntaxError` — the file's **first line is `pip install lunar_python`**, a shell command saved as a `.py` file;
  * `skills/market-research-reports/scripts/generate_market_visuals.py:468:24: F821 undefined name 'VISUALS'`;
  * `skills/pdf/scripts/pdf_qa.py:120:23: F821 undefined name 'LAST_PAGE_MIN_FILL'`.

**So: 295 passing property tests, a CI that has run exactly once, and it died before the tests.**

### 21 gitlinks and no `.gitmodules` — the empty-door defect

```
$ git ls-files -s | grep 160000 | wc -l      → 21
$ ls .gitmodules                              → No such file or directory
$ find pelagic-twin -mindepth 1 | wc -l       → 0
```

**21 directories are empty after a clean clone**, including **`pelagic-twin/`** — which the README's Architecture section names as a core component: *"`pelagic-twin/` — vessel shadow repo with CRDT sync"*. `fleet/SmartCRDT`, `fleet/flux-py`, `fleet/holodeck-studio`, `fleet/oracle1-index`, `fleet/nautilus`, `fleet/navigator-vessel`, `repos/*` (9 more) are the same. The gitlink SHAs are resolvable and the content is public elsewhere in the fleet; the **door is simply empty**. (This is the `plato-portal` defect class, previously reported there — it recurs here.)

### Proprietary, non-commercial, no-distribution code in a *public* repo

`skills/pdf/LICENSE.txt` (and 4 siblings):

> **Copyright (c) 2026 Z.ai All rights reserved.**
> *Permission is granted for **personal, educational, and non-commercial use only**.*
> *Commercial use is strictly prohibited without prior written permission from the author.*
> *Unauthorized copying, modification, or **distribution** … is prohibited.*

Five skills carry this — **`pdf`, `docx`, `xlsx`, `ppt`, `charts`** (`author: Z.AI`, `license: Proprietary`) — plus `skills/gift-evaluator/SKILL.md` licensed **"Internal Tool"**. They sit in a **public** SuperInstance repo, alongside a fleet that ships a live commercial site (`superinstance.dev`), a live-canon worker, and paid API integrations. **"Personal, educational, and non-commercial use only" + "distribution prohibited" + a public repo is a contradiction that a human with authority should look at.** I am not the right judge of that question, and I am flagging it rather than ruling on it.

### One more README contradiction

The README says *"`skills/` — agent skill definitions for git operations."* The directory holds **46 skills, 18 MB**, including `image-generation`, `podcast-generate`, `marketing-mode`, `mindfulness-meditation`, `dream-interpreter`, `gift-evaluator`, `pdf`, `docx`. **Almost none of them are git operations**, and five are third-party proprietary.

---

## 5. `fleet-oracle2` — the conservation doctrine with a real emitter and **two independent terms**

**What it is.** "A self-aware agent orchestration OS" on Oracle ARM64: a 9-step pulse pipeline (collect metrics → compute γ,η → embed → detect anomalies → self-tune GC → auto-evict), a WAL, a semantic-vector store, and dashboards.

**Why another agent should care — this is the positive counterexample to a known failure class.** Prior rounds found the fleet's conservation machinery hollow:

* `spreadsheet-engine` implements γ+η=C conservation but `grep gamma\|eta` across every source file returns **0 occurrences**; the only writers are inside `#[cfg(test)]` — **a monitor with no emitter**.
* A named class exists for *"a 'conservation' whose second term is computed from the first — `eta = C - gamma` makes γ+η=C an assignment, not evidence."*

`integrations/colony_conservation_scorer.py` is the counterexample. The two terms are measured **independently**:

```python
# γ = mean vector magnitude (how much productive signal each cell carries)
gamma = sum(math.sqrt(sum(v ** 2 for v in p.vector())) for p in profiles_list) / n
# η = mean pairwise (1 - cosine_similarity) = overhead from misalignment
eta = sum_dissim / pairs if pairs > 0 else 0
# C (total) = γ + η (conserved)
```

γ comes from per-cell channel magnitudes; η comes from **pairwise cosine dissimilarity** across cells; `C = γ + η` is a *derived total of two separately-measured quantities*, not a tautology. **And it prints a falsifiable prediction**: `gamma_predicted = 1 − δ(n)` where `δ(n) = (1/√n)(1 − 3/(2n))`.

Measured on the repo's own 6-cell fixture: `n=6, γ=1.3861, η=0.0433, C=1.4294, δ(6)=0.3062, γ_predicted=0.6938`.

### But: no CI, an undeclared dependency, and a self-test that cannot pass in a clean clone

* **No `.github/workflows/` at all.** Zero CI.
* **`python3 integrations/colony_conservation_scorer.py` exits 1** in a clean clone: `ModuleNotFoundError: No module named 'msgpack'` (from `integrations/superinstance_bottle.py`). There is **no `requirements.txt`, no `pyproject.toml`, no `setup.py`** — the dependency is undeclared, so the scorer prints its metrics and then dies on an import. *(`pip install` is not even needed for the scorer; only the trailing bottle section needs it.)*
* **`scripts/self-test.sh` → "1 passed, 11 failed", exit 11.** It is a **live-service** test: it wants six running endpoints (`oracle:8795`, `log:8781`, `event:8782`, `conductor:8769`, `headspace:9090`, `gc-pid:8785`) and a `data/decision-wal` directory. A repo that ships a self-test which cannot pass anywhere except on the author's running host, with no way to start the stack in CI, is a self-test that is really a **health probe of one machine**.
* **An unexplained factor between the prediction and the measurement.** The script prints `γ` and `γ predicted` on adjacent lines and nothing in the repo relates them. Scaling n from 2 to 12 with fresh profiles:

  | n | γ measured | γ predicted | ratio |
  |---|---|---|---|
  | 2 | 1.3457 | 0.8232 | 1.63 |
  | 4 | 1.3616 | 0.6875 | 1.98 |
  | 6 | 1.3601 | 0.6938 | 1.96 |
  | 8 | 1.3730 | 0.7127 | 1.93 |
  | 12 | 1.4098 | 0.7474 | 1.89 |

  The two never coincide, the ratio is not constant, and **no test asserts any relationship between them**. I cannot tell from the repo whether this is a definitional mismatch (a normalised vs unnormalised γ) or a real factor-of-~2 defect. **I am reporting the numbers, not a verdict** — but "a prediction printed next to a measurement, differing by ~2×, with no test and no note" is exactly the shape that hides a defect.

---

## 6. `polychora-temporal` — the CI is red because the recipe was never copied between two workflows **in the same repo**

**What it is.** A genuine 4D voxel engine and multiplayer sandbox on Vulkan: 4D chunked voxel worlds (8×8×8×8), 4D camera math with explicit 4D basis vectors, rotation in all six spatial planes, native 4D voxel-traversal ray casting, tetra ray-tracing and tetra rasterisation, server-authoritative multiplayer with streaming subtree replication, and a first-party WASM content plugin behind a stable ABI. 3 MB of Rust across 8 workspace members, 348 `#[test]` attributes, 22 CI runs.

**The defect, reproduced with the CI's own command.** Its `CI` workflow is **red 2/2**. The logs have expired (410), so I reproduced it instead. `ci.yml` is:

```yaml
- uses: actions/checkout@v4
- uses: dtolnay/rust-toolchain@stable
- run: cargo check
- run: cargo test
- run: cargo clippy -- -D warnings
```

**No step installs a shader compiler.** But `build.rs` *requires* one — `check_tool()` **panics** if it is missing — and the panic message is:

```
thread 'main' panicked at build.rs:302:9:
Slang compiler not found. Install: yay -S shader-slang-bin
```

(`yay` is the **Arch Linux** package manager, on an `ubuntu-latest` runner.) Running the CI's exact command here:

```
$ cargo check
thread 'main' panicked at build.rs:302:9:
Slang compiler not found. Install: yay -S shader-slang-bin
EXIT=101
```

**And the fix already exists — 60 lines away, in the same repo.** `linux-build.yml` (green **10/10**) has the complete provisioning: `libvulkan-dev`, `spirv-tools`, `libasound2-dev`, a **"Download and install Slang compiler"** step (pinned `SLANG_VERSION: "2026.2.1"`, with `LD_LIBRARY_PATH` wired to the extracted lib dir), and a **"Verify shader toolchain"** step (`slangc -v`, `spirv-link --version`, `spirv-val --version`).

So the same repository contains both a working recipe and a broken one, and the broken one simply never copied it. `Linux Builds` 10/10 green · `Windows Builds` 10/10 green · `CI` **0/2**.

**Why it matters beyond this repo.** This is a *shape* the fleet has 30+ of: a CI workflow that runs a build command whose **prerequisites are never provisioned**, so the step can never go green, and the red badge is read as "the code is broken". The distinguishing evidence here — a sibling workflow in the same repo that does provision it, and a panic message naming the exact missing tool — makes the diagnosis unambiguous.

**The fix:** factor the toolchain steps into a `composite action` (`.github/actions/setup-shader-toolchain/action.yml`) and call it from all three workflows. Then `CI` gets to actually run its 348 tests.

---

## 7. Negative findings, collected

| # | Finding | Receipt |
|---|---|---|
| 1 | `quilt-vm-rust` README advertises **"Tests: 7 passing"** with a static green badge; `cargo test` **does not compile** (exit 101) | §2, reproduced |
| 2 | `quilt-conformance`'s BUG-3 is **fixed upstream** but still listed as open — a ledger with no re-run trigger | §2, upstream `Cargo.toml` @ `master` |
| 3 | `smartcrdt-git-agent` README calls `pelagic-twin/` a core component; the directory is **empty after clone** (21 gitlinks, no `.gitmodules`) | §4, `git ls-files -s` |
| 4 | `smartcrdt-git-agent` README calls `skills/` "git operations"; it holds 46 third-party skills, 5 **proprietary non-commercial** | §4 |
| 5 | `smartcrdt-git-agent`'s CI has **never run its 295 passing tests** (lint dies first; test step is `|| true`) | §4, reproduced |
| 6 | `qthe-verify`'s vendored kernel header claims **byte-for-byte** upstream equality; it is comment-stripped (13,629 → 7,927 bytes) | §3, diffed |
| 7 | `fleet-oracle2` has **no CI**, an **undeclared** `msgpack` dependency, and a self-test that is **1/12** in a clean clone | §5, reproduced |
| 8 | `fleet-oracle2` prints a `γ predicted` that is ~1.6–2.0× away from the measured `γ` at every n, with **no test** relating them | §5, table |
| 9 | `polychora-temporal`'s `CI` workflow runs `cargo check` on a runner that **never installs the Slang shader compiler** that `build.rs` hard-panics without — **red 2/2** — while its *sibling* `Linux Builds` workflow installs it and is green 10/10 | §6, reproduced |

---

## 8. What I would tell the fleet

1. **Adopt `quilt-jetson`'s CI-trigger guard fleet-wide.** It is the only artifact in the fleet that provably catches the fleet's most common CI defect, and it catches it **twice** — once live, once offline in `cargo test`. It is 1 workflow file + 1 script + 1 test file.
2. **Adopt `quilt-verify`'s "never import the thing you are verifying" rule.** A checker that imports the vendor's code is a report, not a verification. `qthe-verify` does not, and proves it by grepping clean.
3. **Adopt `quilt-forge`'s reusable-workflow + receipt-artifact harness** for repos that need a CI today.
4. **Give `quilt-conformance` a re-run trigger.** The harness exists and works; it just needs a CI job that regenerates `RESULTS.md` and diffs it, and a staleness marker on `BUGS.md`. Right now the ledger's own drift is the proof it needs one.
5. **Never publish a static badge that claims a test count.** `quilt-vm-rust`'s `Tests: 7 passing` is a picture of a status that the compiler says does not exist.
6. **The empty-door defect is systemic.** 21 gitlinks with no `.gitmodules` in one repo, 25 in `plato-portal`. Add the detector to a repo-wide sweep: `git ls-files -s | grep 160000` **and** `[ -f .gitmodules ]`.
7. **Factor toolchain provisioning into a composite action.** `polychora-temporal` has a green build workflow and a red CI workflow *in the same repo*, differing only by a missing setup step. Any fleet workflow that runs `cargo check`/`cargo build`/`npm ci` against a non-trivial toolchain should call one shared setup action — and that action should **verify** the tool (`slangc -v`) rather than assume it.
8. **Audit the `skills/` redistribution.** "Personal, educational, and non-commercial use only / distribution prohibited" code is sitting in public repos inside a fleet with live commercial services. That needs a human decision, not a scout's.

---

## Appendix A — census method, in full

```
GET /users/SuperInstance/repos?per_page=100&page=N&sort=full_name&direction=asc
```
* 54 pages; last page 8 rows; HTTP 200 on every page; a non-array body or an empty page stops the loop.
* Asserts, all three, every round: `unique_by(.full_name) == rows_returned` **and** `rows_returned == user.public_repos` **and** `full_name.casefold()` is non-decreasing.
* `public_repos` was read from `GET /users/SuperInstance` **in the same run** (5,308).
* Forks filtered by the API's `fork` flag: **822** removed, leaving **4,486** own.
* "Never examined" = the repo's name appears **fewer than 2 times** across all **143** prior files in `research/scout/` (tokenised on both `owner/repo` and bare-name forms). **Never-sectioned** would have been a looser pool; this is the stricter one.
* Substance ranking: `git/trees/{default_branch}?recursive=1` per repo (**3,422 calls**), summing blob sizes for code extensions only, with `node_modules|vendor|third_party|thirdparty|external|extern|deps|.venv|venv|site-packages|__pycache__|target|dist|build|.tox|.mypy_cache|minified|bower_components` excluded. API `size` was **never** used for ranking (it is git history, not substance).

## Appendix B — how to re-run every receipt in this report

```sh
# 1. quilt-jetson — guard must fail on a broken filter
git clone --depth 1 https://github.com/SuperInstance/quilt-jetson.git && cd quilt-jetson
python3 scripts/ci_trigger_guard.py --self-test          # exit 0, "15 assertions, no network"
sed -i 's/branches: \[master, main\]/branches: [feature\/nonexistent-xyz]/' .github/workflows/ci.yml
python3 scripts/ci_trigger_guard.py                      # exit 1 — three named failures
git checkout -- .github/workflows/ci.yml && python3 scripts/ci_trigger_guard.py   # exit 0
cargo test                                                # 239 passed, 0 failed
cargo test --test ci_triggers                             # 5/5; mutate ci.yml first → 2 FAILED, exit 101

# 2. quilt-conformance — BUG-1 against upstream HEAD
git clone --depth 1 https://github.com/SuperInstance/quilt-vm-rust.git && cd quilt-vm-rust
cargo test        # exit 101 — E0277 at src/lib.rs:283, exactly as results/BUGS.md quotes it

# 3. qthe-verify — both mutations, and the corpus regeneration
git clone --depth 1 https://github.com/SuperInstance/qthe-verify.git && cd qthe-verify
node verify.mjs                                            # 12/12, exit 0
# M1: nextD  'if (pressure > 0)'  →  'if (pressure >= 0)'    → exit 1, "diverged at tick 1"
# M2: one hex char of prng-01 expected_trace_hash             → exit 1, "corpus length mismatch?"
git checkout -- verify.mjs corpus/cases.json && node verify.mjs   # exit 0
node tools/generate-corpus.mjs | jq -S '[.cases[]|{id,expected_trace_hash,tick_hashes}]' | md5sum
#   → 0623147a4c5a6e7cda78ab1acd2a5e9f   (identical to the committed corpus)

# 4. smartcrdt-git-agent — the lint failure CI died on
git clone --depth 1 https://github.com/SuperInstance/smartcrdt-git-agent.git && cd smartcrdt-git-agent
pip install --break-system-packages --index-url https://pypi.org/simple flake8 pytest
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics   # 3 findings, exit 1
python -m pytest --import-mode=importlib -x -v                        # 295 passed
git ls-files -s | grep -c 160000; ls .gitmodules                      # 21 ; No such file

# 5. fleet-oracle2 — the two independent conservation terms
git clone --depth 1 https://github.com/SuperInstance/fleet-oracle2.git && cd fleet-oracle2
python3 integrations/colony_conservation_scorer.py    # γ=1.3861 η=0.0433 C=1.4294, then exit 1 (msgpack)
bash scripts/self-test.sh                             # 1 passed, 11 failed, exit 11
```

## Appendix C — what I did *not* claim

* **`polychora-temporal`** (3 MB Rust, a genuine 4D voxel engine — 4D voxel chunks, 4D basis-vector camera math, rotation in all six spatial planes, tetra ray-tracing, a WASM content plugin — 348 `#[test]` attributes, 22 CI runs): **see §6 for a confirmed CI defect.** I could not run its 348 tests (it needs a Vulkan + Slang toolchain), so the *suite* is inspection-only here; the *CI defect* was reproduced.
* **`quilt-rust`** (1.2 MB, 12-crate Rust workspace) holds **both** doctrines: the 8-cell-kind federation core (`packages/core`, `packages/mcp`, `packages/cli`, `packages/tui`, `packages/web`) *and* the 5-opcode polyformalism port (`crates/quilt-polyformalism`). `quilt-jetson`'s README describes it as the 8-cell-kind core; `quilt-rust`'s own README describes only the 5-opcode port and the byte-exact hash `0xe435d91d6d92a1d8`. **Both are true of the same repo**, which makes the name ambiguous for anyone searching the fleet. It appears twice in prior reports, so it was out of my unseen pool; noted here for completeness.
* I did not run the fleet's Rust suites for `quilt-conformance`'s five VM siblings beyond `quilt-vm-rust` — the Haskell/C/WASM adapters need `ghcup`/GHC and a Vulkan-free toolchain that is not in this sandbox.
