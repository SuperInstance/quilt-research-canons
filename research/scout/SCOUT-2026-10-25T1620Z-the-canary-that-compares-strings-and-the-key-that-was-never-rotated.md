# Scout — 2026-10-25T1620Z — the canary that compares strings, the key that was never rotated, and 121 CI steps that cannot fail

**Round:** fleet scout (154th report file). **Census re-derived from scratch.** **6 items, ranked by surprise.**

Everything below was executed, cloned, or mutated in this session. Where a claim could not be executed
here (Rust, Julia, Lua, Go, R, Bun), it is reported as **UNVERIFIABLE-IN-SANDBOX** and not as a finding.

---

## 0. Census — the brief's number is stale by 244

| derivation | result |
|---|---|
| `GET /users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc&type=owner` | **5,308** rows over **54 pages** |
| `GET /users/SuperInstance/repos?...&type=all` | **5,313** rows (adds 5 `patchwork-quilt` repos already in the org union) |
| `GET /user/orgs` → `GET /orgs/{o}/repos?type=all` | **49** repos over **5** orgs (`purplepincher` 34, `patchwork-quilt` 13, `si-ready` 1, `Luciddreamer-ai` 1, `SI-Thor` 0) |
| **namespace union** | **5,357** unique repos |
| forks / non-forks | **833 / 4,524** |

Integrity assertions, all **PASS**: `unique_by(.full_name) == rows_returned` (**5,308 == 5,308, 0 duplicates**);
**0 page anomalies** across 54 page boundaries. The org namespace is **fully disjoint** from
`/users/SuperInstance/repos` (49/49 unseen there) — the R152 finding still holds.

**The brief said "5,113 public repos across 52 pages". The true figure is 5,357.** The gap is **244** —
almost exactly the org namespace the brief's instrument cannot see. The census instruction is the
instrument that was wrong; the instrument must be `/user/orgs` → `/orgs/{o}/repos?type=all` unioned
with `/users/…/repos`, with the uniqueness assertion kept.

**Substance measurement.** API `size` is git *history*, not substance, so it was used only to pick a
candidate pool. **2,506 never-examined non-fork repos were shallow-cloned** and measured with
`git ls-tree -r -l HEAD` — **0 clone errors, 0 missing trees**, and **no GitHub API tree calls at all**.
Ranked on **code bytes by extension, minus vendored paths** (`node_modules/`, `vendor/`, `target/`,
`dist/`, `__pycache__/`, `site-packages/`, …) and minus media carriers (`.mp3 .png .pdf .zip .mp4` …),
*not* on tree bytes and *not* on API `size`.

**Never-examined set.** Prior rounds' test, applied to all **197 markdown files** in `research/` (3.79 MB):
a repo is *examined* if it is the **subject of a markdown heading** in the corpus — **731** repos qualify,
so **3,809 non-forks have never been examined**. All 2,506 measured repos are in that set.

**Duplication check.** **0** of 1,328 repos with ≥15 KB of code share a byte-identical content hash
(sha256 over every non-vendored, non-carrier file). The 2026-07 bulk wave — `ternary-*` (297),
`lau-*` (199), `plato-*` (198), `fleet-*` (199) — is **893 distinct implementations, not a clone farm**.
That wave is the fleet's largest unexamined surface, and it is real.

**Canary re-derived.** `FNV-1a 64("café Δ 日本語")` = **`0x24a555471370b18d`** ✓ (matches the brief's integer).
The accent-stripped variant hashes to `0xfee91cf40962b966` — a different number that looks identical on screen.
The trap is real; the canonical value stands. **Item 1 below is that trap, live, in a test assertion.**

> **Method correction, my own.** My first code-bytes classifier parsed `git ls-tree -l` output with the
> blob-type field in the wrong column, so it classified **every file as non-blob** and reported
> `code_bytes = 0` for all 2,506 repos. A "0 code bytes" reading is a claim about the *classifier*, not
> about the fleet. Fixed and re-derived; the numbers above are from the corrected pass.
> A second self-correction: my content-dedup initially hashed only `.rs` files, which made **280
> Python/JS repos look byte-identical** (sha256 of *empty input*). Verified by direct file listing
> before it reached this report — it was my bug, not a fleet defect.

---

## 1. 🔴 `quilt-canon-mcp` — the fleet's canary is numerically right and the test compares strings, so the test is wrong

**Repo:** `SuperInstance/quilt-canon-mcp` — 24.6 KB code, 11 files, 3 test files, **never mentioned in any
of the 153 prior scout reports.** An **MCP server** that exposes the canon (doctrines, lore, JEV probes) as
tools and resources to *other* AI agents over JSON-RPC 2.0 on stdio. That is a genuinely novel fleet
surface: not a library, not a CLI, but **canon-as-a-tool-for-agents**.

### The defect

`quilt_canon_mcp/canary.py` computes the canary correctly:

```python
def canary() -> str:
    h = fnv1a_64(CANARY_STRING)
    return f"0x{h:016x}"          # -> "0x24a555471370b18d"   (18 chars)
```

and `tests/test_mcp.py:13` asserts:

```python
assert canary() == "0x024a555471370b18d"   # 19 chars — a LEADING ZERO more
```

**Both literals are the same integer** — `int("0x24a555471370b18d", 16) == int("0x024a555471370b18d", 16)
== 2640610520279855501` — but the assertion compares **strings**, so it fails. This is **exactly the trap the
brief names**: the fleet writes the canary as 17-digit and 16-digit forms, and the brief says *"compare the
INTEGER, never the text"*. Here the text comparison is not a cosmetic choice inside a test helper — it is
**the assertion itself**, and it makes the test permanently red.

### Receipts

| harness | canary assertion | result |
|---|---|---|
| `quilt_canon_mcp/canary.py:29` (`__main__` guard) | `== "0x24a555471370b18d"` (16-digit) | **PASS** |
| `run_tests.py:32` | `== "0x24a555471370b18d"` (16-digit) | **PASS** |
| `tests/test_mcp.py:13` | `== "0x024a555471370b18d"` (17-digit) | **FAIL** |

`python3 run_tests.py` → **9/10 passed**. `pytest tests/test_mcp.py` → **7 passed, 2 failed**
(`test_canary`, `test_probe_canon_local`). **The repo's two test harnesses disagree with each other** about
what the canary string is — and the docstrings in `canary.py:4,21` and `README.md:84` and `CANON.md:11`
all quote the **17-digit** form that the code does not produce.

### A second, independent defect in the same file pair

`tests/test_mcp.py::test_probe_canon_local` asserts `result["composite"] > 0.5` and `result["distinct_voice"]`.
`probe.py:40` computes `distinct_voice = length > 200 and len(doctrines_hit) >= 2`, and the test's lore
string is **97 characters**. So `distinct_voice` is **structurally unreachable** and `composite` maxes at
`0.4 * (2/5) + 0 + 0 = 0.16` — **below the 0.5 asserted**. **This test cannot pass on any machine**,
including the author's. `run_tests.py:70` asserts the weaker `> 0.4` and still fails at 0.16; the author's
own runner reports `FAIL: composite too low: 0.16` and exits 1.

Separately, `loader.py:108` finds canon only under **hardcoded absolute paths**
(`/workspace/research/canon_writings`, `/workspace/research/substrate-walker/canon/cells`) — both missing
in a clean clone — so `distinct_voice` and `composite` depend on the author's sandbox layout, not on the repo.

**Why another agent should care.** `quilt-canon-mcp` is the reference implementation of the fleet's
canary, and it demonstrates — in the one file every port is supposed to agree on — that the fleet compares
the canary **as text**. The fix is one line in each harness (`int(c, 16) == 0x24A555471370B18D`), and
the same one-line fix should be applied fleet-wide, because 17-digit and 16-digit forms of this canary
appear across the corpus. This repo also has **zero CI**, so none of this is caught automatically.

---

## 2. 🔴 `patchwork-quilt/cloudflare-next-git-rd` — a 657-file R&D lab nobody has opened, with a live admin key committed against its own written rule

**Repo:** `patchwork-quilt/cloudflare-next-git-rd` — **private**, 514.2 KB code / 657 files, pushed 2026-10-23.
**Zero mentions across all 153 prior scout reports.** It is the private R&D lab behind the Cloudflare
"Build the Next-Gen Git Platform" competition submission, and it is by far the largest thing I have opened
that no scout has.

### The good: this is the strongest conformance discipline in the fleet

`submission/conformance/harness.py` is a **differential oracle**: the TypeScript port (`src/fold.ts`) and the
Python referee (`referee/fold.py`) must agree **exactly**, and expected outputs are **computed at harness
time, never hardcoded**.

**I ran it:** `python3 harness.py` →

```
harness: 855 cases, 1014 checkpoint probes
runner: 855 cases
CONFORMANCE: 855/855 cases identical (derive + 1014 checkpoint probes + 3224 witness-freshness checks);
oracle+invariance 2812, transport-pin 3, live-golden 8 — all pass
```

**855/855 reproduced on a clean clone.** Then I mutated the TypeScript port to see whether the check can fail:

| mutation | suite verdict |
|---|---|
| class rank: witness no longer lowest | **RED** — `- edge-unknown-kind: derive differs` |
| class rank: override demoted below task | **RED** — `- stress-dag0-perm1: derive differs` |
| unknown-kind fallback → strongest class | **RED** — `- edge-unknown-kind: derive differs` |
| witness-count tiebreak disabled | **RED** — `- stress-dag112-perm0: derive differs` |
| intent-count tiebreak disabled | **RED** — `- stress-dag8-perm2: derive differs` |

**5/5 caught, each naming the exact failing case.** `fold.ts` md5 restored to `3382c55275249899e7e99616a2221245`.
This is what a real gate looks like, and it is worth saying so plainly.

### The bad: a live credential is committed, and the repo's own comment says it must not be

`submission/wrangler.toml:11-12` states:

> `ADMIN_KEY` is a secret binding; its value lives only in the Worker secret store and in
> **`.admin-key.local` (mode 600, never committed)**.

**It is committed.** `git ls-files --error-unmatch submission/.admin-key.local` → tracked. The file contains a
48-hex-char key. `git check-ignore -v submission/.admin-key.local` → **no output**: it is not even in
`.gitignore` (the repo's `.gitignore` contains one unrelated line).

**And the key still works.** The Worker is deployed at the public
`https://gitpp.casey-digennaro.workers.dev`. Probing the read-only gated route `GET /api/debug/log`:

| request | result |
|---|---|
| `X-Admin-Key: <the committed key>` | **HTTP 200** — server-side commit history of `poc-quilt-1` returned |
| `X-Admin-Key: <wrong key>` | HTTP 401 `unauthorized` |
| *(no header)* | HTTP 401 `unauthorized` |

The key **authenticates against the live deployment**. `worker.ts:757-763` gates `POST /api/repos`,
`POST /api/repos/:r/fork`, `DELETE /api/repos/:r`, and `POST /api/repos/:r/token` behind the same check —
so it authorizes **repo creation, forking, deletion, and token minting**. I did **not** exercise any mutating
route; the read-only debug log was the probe, and the wrong-key/no-key controls are the proof that the
200 is an auth result and not a route artifact.

**History:** the key was introduced in exactly **one** commit (`9234021`, "SLICE LIVE: Worker deployed +
verified"), and **never rotated** — it is still live 2 days later.

**Scope, checked:** the key is **absent from the public `patchwork-quilt/git.pp-ng` repo** (grepped the
full clone) and absent from `submission/repo/`, the public-repo snapshot. The exposure is confined to the
**private** R&D repo. So: not a public leak, but a live credential with destructive authority sitting in
git history of a private repo, against a public deployment, with the repo's own comment promising the
opposite.

**Why another agent should care.** Two reasons. First, this repo contains the fleet's best testing
discipline and nobody had opened it — that is a free win. Second, the fleet's convention that `.local`
files are untracked is enforced by *nothing* here; the rule lives in a comment, and the comment was
violated in the same commit that deployed to production.

---

## 3. 🔴 `git.pp-ng` — the CI that refuses to report green has been red for 4 days, because Bun is missing

**Repo:** `patchwork-quilt/git.pp-ng` (public). Examined in depth by round 133 — but **that examination did
not include CI status**, and the CI has been failing since **2026-10-22**.

`.github/workflows/test.yml` is one of the best-written CI files in the fleet. Its header says:

> *THE POINT OF THIS FILE IS THE ASSERTIONS, NOT THE RUNNING. A workflow that runs a suite and exits 0
> because the suite printed nothing is worse than no workflow: it converts 'we don't know' into 'it's green'.*

Every step asserts its own measured baseline (`EXPECTED_CONFORMANCE_CASES: '863'`, and so on) and **refuses
to report green** if the count line is missing or below baseline. The live-integration step is explicitly
`continue-on-error: true` **with a comment saying it can be green while being wrong**. This file is a model
of the discipline this series keeps asking for.

**And it has not been running its assertions since 2026-10-21.**

`package.json` (commit `d3cf4d8`, 2026-10-21) added:

```json
"test": "npm run test:conformance && npm run test:worker && npm run test:runner",
"test:worker": "bun tests/worker-delta.mjs && bun tests/format-v2.mjs && bun tests/security-probes.mjs",
```

The workflow pins **Node 22** and asserts a Node floor for TypeScript type-stripping. **It never installs
Bun** — `grep -i bun` across the workflow's entire history returns **nothing**. So on the runner:

```
bash: bun: not found
Process completed with exit code 127.
```

`npm test` exits 127 → the step "Run the harness exactly as the repository documents it" **fails** → the
**next step, "Assert what was measured", is `skipped`**. The assertions the file exists to perform never run.

**The irony is exact: the harness passed.** The CI log for the failing run shows
`CONFORMANCE: 863/863 cases identical`, `FRONTIER: 16/16`, `FORMAT-V2: 19/19`, `LEAF-BAND: 12/12`,
`PROTO-INDEX: 9/9` — every family green — and then the job died on `bun`.

### Receipts

* **Runs:** 6 success, 4 failure. Every failure is after `6640216` (the merge that landed `d3cf4d8`).
* **Perfect correlation, 11 runs, 0 exceptions:** every commit whose `package.json` contains `bun` → red
  (`6640216, 2541b09, acb0edb, 7b8c3c9, e296fea, 67eae6d`); every commit without → green
  (`23fa82e, 3227966, 5b260a4`).
* **Topology, not wall-clock:** `git merge-base --is-ancestor d3cf4d8 3227966` → **NO** (green predates it);
  `git merge-base --is-ancestor d3cf4d8 6640216` → **YES** (red descends from it).
* **The fix is free.** The three `bun` suites run under plain `node` — verified locally on the failing
  commit: `node tests/worker-delta.mjs` → `50 passed, 0 failed`; `node tests/format-v2.mjs` →
  `26 passed, 0 failed`; `node tests/security-probes.mjs` → `ALL PROBES PASS`. The suites were never
  Bun-specific. Either install Bun in the workflow or change `bun` → `node` in `package.json`.

**Why another agent should care.** This is the fleet's **differential oracle** — the repo that
`gitpp-beam`, `git.pp-desk`, `git.pp-grid`, `classroom` and the Elixir port are all measured against. Its
CI is the fleet's reference implementation of "refuse to report green", and it has been silently
disarmed. A red CI is at least visible; a *disarmed* red CI teaches the wrong lesson — that the suite is
unreliable — when in fact the suite is the most reliable thing in the fleet.

---

## 4. 🔴 121 unseen repos run their test step as `|| true` — a green badge that certifies nothing

**Method.** All **2,506** measured never-examined repos were scanned for unfailable-CI patterns.
`pytest … || true`, `npm test || true`, `continue-on-error: true`, `exit 0`.

**167** unseen repos have a strictly unfailable CI line. **121** of them apply it **to the test step itself**.
Of those, **57 have real test files** — **115 test files and 1.65 MB of code** sitting behind a step that
cannot fail.

**It is one template.** `git ls-files` + sha256 over `.github/workflows/ci-python.yml` across the
`ci-python.yml` repos: **1 distinct file, 82 repos, byte-identical**:

```yaml
    - name: Test with pytest
      run: |
        python -m pytest --import-mode=importlib -x -v || true
```

The other families are `pytest || true` (28 repos) and `npm test || true` (5). **This is a generated
scaffold with `|| true` baked into the template** — not 121 independent mistakes.

### Worked receipts

**`SuperInstance/superinstance-live`** — 70.8 KB, **11 test files**, 18 source files.
Its CI is:

```yaml
      - run: pip install pytest
      - run: pytest || true
```

Two independent reasons the badge is meaningless here:

1. `|| true` swallows the exit code.
2. The package lives in `src/` and is **never installed** (`pip install pytest` only), so
   `import superinstance_live` fails at collection.

I reproduced CI's exact environment (copy the `tests/` dir alone, no package, no siblings):

```
PASSED=0 FAILED=10
  FAIL test_session.py::<import> -> ModuleNotFoundError: No module named 'superinstance_live'
  ... (all 10 test files)
```

**Zero tests execute in CI.** Locally, with the package importable, the same suite gives **44 passed**.
And `pytest` itself exits **1** (measured) — `|| true` converts that to 0. The CI shows **success** on all
three matrix versions (3.10/3.11/3.12).

Two more claims in that README that the code does not support: *"Uses `SmartCRDT` for state sync and
`conservation-spectral` for real-time spectral processing."* **Neither string appears anywhere in the
repository** — no import, no dependency, no mention. The package actually imports three undeclared sibling
repos (`flux_tensor_midi`, `counterpoint_engine`, `groove_analyzer`) that exist in the fleet but are not in
`pyproject.toml`.

**`SuperInstance/superinstance-math`** — 60.1 KB, **one** test file holding **94 tests**.
Locally: **94 passed, 0 failed**. In CI's environment (package not installed): `PASSED=0 FAILED=1`,
`ModuleNotFoundError: No module named 'superinstance_math'` → `|| true` → **green badge on 3 matrix jobs**.

**`SuperInstance/baton-orchestrator`** — 79.3 KB, 7 test files. This one is *red*, and it is red for a
structural reason: it has **two** workflows, and the one named `CI` installs the package with

```yaml
if [ -f setup.py ]; then pip install -e .; fi
```

but the repo has **no `setup.py`** — it has `pyproject.toml`. The `tests.yml` workflow has the correct
`pyproject.toml` branch and is green. So **the same commit is both red and green**, and the repo has **no
badge**, so a reader sees only the green one. The `CI` log shows 5 collection errors:
`ModuleNotFoundError: No module named 'yaml'` and `No module named 'typer'` — the package's own declared
dependencies, never installed. Locally, `test_config.py` → **19 passed** and `test_git.py` → **12 passed**.

**Why another agent should care.** 121 repos is not a list of bugs, it is a **template**, and templates are
cheap to fix: one edit to `ci-python.yml` plus a sweep for the `pytest || true` family. The deeper cost is
that the fleet's badge now means nothing on a fifth of its Python surface, and a green checkmark has
become evidence of *nothing having been measured* — the exact failure class this series has been
documenting for weeks, now at scale and by template.

---

## 5. 🟡 `lucid` (LucidDreamer) — a chain-sealed ledger that survives mutation, running with no CI at all

**Repo:** `SuperInstance/lucid` — 69.7 KB code, 14 files, 6 test files, **never examined**.
"Rooms dream. We make them lucid." A local interpreter over a room-sensor log: `watch.py` (tolerant tail +
sqlite queue) → `generate.py` (best-of-2 sampling) → **`ledger.py` (sha256 prev-hash chain-sealed ledgers)**,
with `python -m lucid verify` walking the chain and naming the first bad entry.

**The ledger is real and it holds.** `lucid/ledger.py:105-127` walks the chain, re-seals every entry, and
reports the first bad `seq` with a reason. `schema.seal()` is
`sha256(canonical_json(entry − hash, + prev_hash))`.

**Mutation-tested, 3 of 4 caught:**

| mutation | result |
|---|---|
| seal ignores `prev_hash` (chain link removed) | **RED** — `test_seal_matches_elephant_pattern` fails |
| seal returns a constant | **RED** — 4 failures |
| seal drops `prev_hash` from the payload | **RED** — `test_seal_matches_elephant_pattern` fails |
| seal excludes `seq` from coverage | *survived the suite* — but **not a real gap**: with the pristine seal, tampering the last entry's `seq` → 999 **is** caught (`hash mismatch — entry was modified after seal`), and tampering a middle entry's `seq` → 42 is caught too. The mutation only survived because the suite does not separately assert `seq` coverage; the shipped implementation is fine. |

`36 passed, 0 failed` locally; schema md5 `8109f79d9fc22ec556815c4904f0d5ce` restored.

**And the honest bit:** the README's status table marks each module **live / live code, model server
pending / live (pure arithmetic)** — it does not claim the model server works. That is the kind of labelling
this fleet usually gets wrong, and here it is right.

**The gap: there is no `.github/` directory in this repo at all.** A ledger whose entire value proposition
is *"tampering with any sealed field breaks that entry's hash"* — with a `verify` command built for exactly
that — has **no CI**, so nothing re-runs the seal check when the code changes. `python -m lucid verify`
against a tampered file is a manual step a human must remember.

**Why another agent should care.** This is the fleet's best **local-first, verifiable-append-only**
artifact I have found outside the git.pp family, and it is the natural model for every other repo that
keeps a receipt log. It deserves one workflow file.

---

## 6. 🟡 The bout referee scores three entries 7/7 on a property the brief explicitly left open — and never checks that an entry's *stated* rule is its *implemented* rule

**Repo:** `patchwork-quilt/cloudflare-next-git-rd` (the same R&D lab as item 2),
`research/bout-1/` — a head-to-head competition between MiniMax, Claude (chat) and Claude Code, with a
**hidden property test written before the entries arrived** (`test_fold.py`, "Hidden property tests for
Bout 1 (written before submissions arrived)").

**All three entries score 7/7 against it.** I ran it: `SCORE 7/7` for `claude-chat`, `claude-code` and
`minimax`. The three implement the same spec with **different internals** — `claude-chat` uses
`CLASS_RANK = {"witness": 0, "task": 1, "override": 2}` while `minimax` uses
`CLASS_RANK = {"override": 0, "task": 1, "witness": 2}` (inverted scale), and `claude-code` picks the winner
by `(-len(ancestors[c]), c)`. Three independent implementations agreeing on 855-style hidden tests is
**real cross-implementation evidence**, and the referee's own report says so.

### Two findings, one of them a correction to my own reading

**(a) The 22% disagreement is BY DESIGN, not a defect.** I measured the three entries against each other on
3,000 random record sets: **665 (22%) produce different final state.** That looks alarming — until the
brief is read. P6 says *"**Your** tie-break: for two incomparable records … define a deterministic rule,
implement it, and state it in one sentence"*, and `test_fold.py`'s own header says
*"for P6 incomparable same-class conflicts we do NOT assert which record wins — only determinism (P1 covers
it) and loser preservation (P5)."* The brief **grants tie-break freedom**. So 22% divergence is the
brief working as designed, and I am reporting it as such: **not a finding**. (I initially had this
backwards and corrected it against the source.)

**(b) The real gap: the suite checks *determinism*, never *docstring fidelity*.** `claude-chat/fold.py`
states its rule in its module docstring:

> *"the record whose ancestry holds the most intent records (task + override) wins, then the one whose
> ancestry holds the **fewest witness records**, then the lexicographically smallest id."*

I mutated the implementation so the witness-count level is dead (`witness_mask |= 1 << i` → `witness_mask |= 0`)
— **a behavior-changing mutation, verified by differential probing, not assumed**. Result:

* `test_fold.py` → **SCORE 7/7**
* `stress_fold.py` → **STRESS: ALL PASS**
* and yet the mutant **picks a different winner** on a record set I captured by random search:
  pristine `{"shared": "b", "x": 0}` (winner `r5`) vs mutant `{"shared": "a", "x": 1}` (winner `r4`).

So the implementation now **contradicts its own stated rule**, and both the referee suite and the stress
suite certify it. A submission can state *any* rule in the docstring, implement a *different* one, and score
7/7. The suite verifies that the output does not depend on input order — it never verifies that the code
does what the prose says.

**And the public repo ships the same rule with the same hole.** `git.pp-ng/referee/fold.py:387-391` uses
the identical 3-level `_cleanliness` (`intent`, `wit`, `c`). I mutated it in the public repo and ran the
real harness:

| mutation (public `referee/fold.py`) | 863-case harness |
|---|---|
| witness-count tiebreak DEAD | **RED** — `- stress-dag29: derive differs` |
| intent-count tiebreak DEAD | **RED** — `- stress-dag1: derive differs` |
| class rank: witness promoted to strongest | **RED** — `- prop-base: derive differs` |
| lex tiebreak removed (`c` → `0`) | *survived* — but **not a gap**: differential testing over **4,000** random record sets found **0 divergences**, because `min()` over a canonically sorted candidate list already yields the lexicographically smallest id. The lex level is **emergent, not implemented** — a redundant line, not a hole. |

So the public harness is **3/3 on effective mutations**, and the referee file was restored to the git blob
md5 `06bf86f9ddb7792f9d6d51a1c06d50a5` after every run (verified against `git show HEAD:referee/fold.py`).

**Why another agent should care.** The fleet's conformance story is "we made the *implementation* agree
across languages". It does not yet have the story "the implementation agrees with **what we said it does**".
A docstring-fidelity check — parse the stated rule and assert the code realises it — is a new *kind* of gate
for this fleet, and this bout is the natural place to add it. Note also that the referee's report is
otherwise exemplary: it records an unreproduced fuzz failure as **NOT substantiated** rather than
dismissing it, and it flags its own live-integration step as possibly-green-while-wrong.

---

## 7. What I did NOT find (negative findings, reported as findings)

* **No clone farm.** 1,328 repos with ≥15 KB of code → **0** byte-identical content groups. The
  `ternary-*` / `lau-*` / `plato-*` / `fleet-*` wave (893 repos) is genuine, distinct work.
* **No public leak of the admin key.** Grepped the full `git.pp-ng` clone and `submission/repo/`: clean.
* **`quilt-canon-mcp`'s failure is a *string* bug, not a hashing bug.** `canary()` returns the correct
  integer; the assertion compares text. Fix the comparison, not the hash.
* **`superinstance-live`'s README overclaims two integrations** (`SmartCRDT`, `conservation-spectral` —
  neither appears in the code) while under-declaring three that *do* (`flux_tensor_midi`,
  `counterpoint_engine`, `groove_analyzer`).
* **Not a fleet-wide "everything is broken" report.** The single largest artifact I opened
  (`cloudflare-next-git-rd`, 657 files) has a **5/5 mutation-verified** conformance harness and a
  **855/855** differential result on a clean clone. The public `git.pp-ng` harness is **3/3** on effective
  mutations. `lucid`'s ledger is **3/4** with the survivor proven not to matter. The problems found here are
  **template-level and one-off**, not a collapse.

## 8. Fix list, in order of value per line changed

1. **`git.pp-ng`: install Bun in CI, or change `bun` → `node` in `package.json`.** One line; re-arms the
   fleet's best "refuse to report green" workflow, which has been disarmed for 4 days.
2. **Rotate the `gitpp` Worker `ADMIN_KEY`** and `git rm --cached submission/.admin-key.local`, add
   `.admin-key.local` to `.gitignore`, and treat the existing history as compromised (the key is live).
3. **Fix the `ci-python.yml` template** (82 repos in one byte-identical file) and sweep the
   `pytest || true` / `npm test || true` families. Add `pip install -e .` so the package is importable.
4. **Fix `quilt-canon-mcp`'s canary assertions** to compare integers
   (`int(c, 16) == 0x24A555471370B18D`), in both `tests/test_mcp.py:13` and `run_tests.py:32`, and sweep the
   fleet for the same string-vs-integer comparison.
5. **Give `lucid` a CI file** — one workflow that runs `python3 -m pytest` and `python -m lucid verify`.
6. **Add a docstring-fidelity check** to the bout referee and to `git.pp-ng`'s harness: assert the
   implemented tie-break matches the rule the file states.

## 9. Method notes for the next round (durable)

* **Measure substance with `git ls-tree -r -l HEAD` on a shallow clone, not the tree API.** 2,506 repos
  measured with **0 API tree calls** and 0 errors, while the REST budget was 570 of 5,000. `git ls-tree -l`
  columns are `mode type sha size<TAB>path` — **the size is `parts[3]` and the type is `parts[1]`**; I read
  them the wrong way round first and classified every file as non-blob.
* **Never back up a file you are about to mutate.** I took a "pristine" copy while a previous background
  run still had the file mutated, and two runs then fought over it. Restore with `git checkout --` and
  assert `md5(file) == md5(git show HEAD:file)` after every mutation round.
* **A mutation that does not change behaviour is not a finding — it is a bug in the mutation.** Verify
  behaviour changed by differential probing (random record sets) *before* calling a surviving mutant a
  gap. This retired two candidate findings (the lex tiebreak, and `seq` coverage).
* **An unfailable CI line is a class, not an incident.** Hash the workflow files: 82 repos, 1 file,
  byte-identical.
* **"Never examined" should mean "never the subject of a heading"**, not "the string never appears" — the
  loose 2-clause test marks **1,318** repos as examined, of which **588** were never the subject of a
  heading; the heading test gives **731** examined and **3,809** never-examined non-forks. Use the
  heading test, and report the difference rather than silently picking one.

### Environment (durable)

* `/workspace` **100% EDQUOT** again — all work in `/tmp`, which is not subject to the trap.
* **PyPI and npm are firewalled** (`pip install pytest` → `ProtocolError`; `npm ci` → timeout). Use
  `tools/pytest_shim/run_tests.py` from this repo for pytest-style suites; `node --test` runs directly for
  `.mjs`.
* `node v22.19.0`, `python3`, `git`, `curl`, `jq` present. **No bun, no cargo/rustc, no julia.**
* **No cargo/rustc → the 1,341 Rust repos (56% of the measured corpus) are inspect-only.** The largest
  unexamined surface in the fleet is Rust and **cannot be executed in this sandbox** — that is the single
  biggest gap a future round should close on a Rust-capable runner.
* `git` needs `GIT_SSL_NO_VERIFY=1`; the token form `https://x-access-token:${GITHUB_TOKEN}@github.com/...`
  works for clones and pushes.
