# Scout — 2026-10-25T1025Z — the port the ruling left behind, and the namespace no census counts

**Round:** fleet scout (152nd report file). **Census re-derived three ways.** **6 items, ranked by surprise.**

Everything below was executed, cloned, or mutated in this session. Receipts are reproducible from the
commands quoted; nothing is quoted from a README without being run or checked against the source.

---

## 0. Census — and the instrument that had to be replaced

`GET /users/SuperInstance/repos` was the fleet's census instrument for ~150 prior rounds. It is not
a complete instrument, and this round shows exactly how it fails.

| derivation | result |
|---|---|
| GraphQL `user(login:SuperInstance).repositories(first:100, orderBy:{field:NAME,direction:ASC})` | **5,313** rows over **54 pages** |
| REST `GET /users/SuperInstance/repos?per_page=100` (default `type=owner`) | **5,308** rows over **54 pages** |
| REST `GET /users/SuperInstance/repos?per_page=100&type=all` | **5,313** rows |
| `GET /user/orgs` | **5 organizations** the account administers |

Integrity assertions on the GraphQL census (all PASS):

- `unique_by(full_name) == rows_returned` → 5,313 == 5,313, **0 duplicates**
- `rows == totalCount` → 5,313 == 5,313
- `casefold` monotonicity → strictly ascending across all 54 page boundaries
- **independent denominator**: REST `public_repos` = 5,308 ≠ 5,313 → the two endpoints disagree; the
  disagreement is the finding (see item 2), not noise. `totalCount` is live; `public_repos` is a
  cached counter.
- GraphQL `orderBy: {field: NAME}` is a **total** order, so paging cannot drop or duplicate at ties —
  the failure mode that `sort=pushed` has. This is the recommended replacement for `sort=full_name`,
  which the fleet has used for months and which R129 already showed is case-insensitive.
- **No tree expansion in the census query.** Fetching `object(expression:"HEAD:")` alongside 100
  repositories reliably produced HTTP 502 (gateway) and 403. Census and substance were split into
  two passes for this reason; the lesson is general: *a GraphQL query that is "just a little deeper"
  is a different query with different failure modes.*

**Substance ranking.** `git/trees/{branch}?recursive=1` for **3,244 repos** (822 forks excluded from
ranking, 33 org repos first, then 3,211 never-examined own repos) — 251 s wall, 14 concurrent
requests, zero API cost beyond the REST trees. Ranked on **code bytes by extension, minus vendored
paths and lockfiles** — not tree bytes, not API `size` (which is git history).

**Never-examined set** (2-clause test over all 257 markdown files / 4.15 MB of prior reports:
*named ≥2× in the corpus* OR *the subject of a markdown heading*): **3,211 of 4,491 own repos
unexamined**, of which **2,533 have zero mentions anywhere in the corpus**.

---

## 1. 🔴 `patchwork-quilt/gitpp-beam` — the conformance port the ruling left behind

**Repo:** `patchwork-quilt/gitpp-beam` (Elixir/OTP, 23 files, 57,611 B of code).
**Named twice, examined never.** `research/state-of-the-quilt-2026-10-15/REPORT.md` has a section
`### patchwork-quilt/gitpp-beam (Elixir port)` whose entire content is one PR: *"#1 (2026-10-15) —
Link sweep: retarget git.pp-ng references to patchwork-quilt (post-transfer)."* Scout round 133
(2026-10-21) listed it among *"git.pp-ng's neighbours … all 3–7 days old and all unseen"*. Across
**all 152 prior scout reports and 257 markdown files**, the strings `canon.ex`,
`spec_boundary`, and `leaf-conformance` appear **zero** times. Nothing in the fleet's written record
has ever opened this port's canonicalisation layer.

**What it is.** A third implementation of the *git.pp fold* — the function that turns a set of
provenance-carrying records into one deterministic state — written in Elixir **from the specification
documents alone**, to answer whether the written spec is sufficient for an independent implementation
to produce byte-identical results. This is the single most valuable kind of artifact the fleet owns:
a genuine cross-implementation conformance port with a real black-box oracle.

**Why this matters more than a fresh bug.** The fleet **already had this bug class and this exact
detector**, and had already applied them to the *sibling* ports:

- `SCOUT-2026-10-16T0418Z` mutated the real C port's leaf encoder at `gitpp-c/gitpp.c:294`
  (`fabs(v) < 1e16` → `fabs(v) < 1e15`) and proved the corpus could not see it.
- `SCOUT-2026-10-17T0117Z` mutated `gitpp-js/src/gitpp.js:36` (`Math.abs(v) < 1e16` → `< 1e17`).
- `SCOUT-2026-10-15T2224Z` audited the leaf-number spec clause itself.

**The Elixir port was the third of three, and it was the one that is wrong.** A sweep that was
otherwise complete skipped it, and the skip is invisible: `gitpp-beam` lives in the organization
namespace that the fleet's census instrument cannot enumerate (item 2), so it never entered the
unseen pool that the other two were found in. **A detector applied to a list the instrument cannot
see is not a sweep.**

**Why another agent should care.** The harness is textbook: `conformance/differ.py` loads the upstream
referee (`git.pp-ng/referee/fold.py`) via `importlib` and computes **expected outputs at run time**,
never from a committed fixture. That is the opposite of the fleet's usual failure (a suite that
re-implements the unit inline). The port also ships a burn test that `:kill`s the per-project
GenServer, restarts it empty, re-feeds the log **in reverse arrival order**, and asserts the digest
and derive output come back byte-identical.

**And it is wrong — in exactly the way its own test suite is built to hide.**

### The divergence, with receipts

The spec of record is `git.pp-ng`, and its programme ledger `RESULTS.md §1.7` ("The leaf-band
incident (2026-10-20 validation pass)") records the whole thing:

> "A hub-only change moved the TS leaf-number boundary **from 1e21 to 1e16** (issue #28). … Ruling
> (recorded on #28): **the spec of record stands** … the change was reverted (PR #31, deployed). The
> hole is closed by a **LEAF-BAND family** (PR #33): 12/12 cases, 29 leaves and 29 closure roots
> pinned as referee literals; flipping the boundary back produces **45 divergences, all inside the
> family, zero elsewhere**. The same pass corrected the spec's own worked example: the double
> nearest 7.248182946264746e20 spells `724818294626474655744` exactly (PR #34)."

| | boundary | evidence |
|---|---|---|
| **Spec of record** (`git.pp-ng/referee/fold.py:153`, `src/fold.ts:128`, `docs/CHECKPOINT-V2.md`) | `abs(v) < 1e21` | `src/fold.ts:113` — *"BOUNDARY RULING (2026-10-20, on issue #28): the band is \|v\| < 1e21, pinned by docs/CHECKPOINT-V2.md, the referee, **and the BEAM port**"* |
| **The BEAM port** (`lib/gitpp/canon.ex:24`) | `@spec_integer_band 1.0e16` | `leaf_number/1` at `canon.ex:204-210` routes integral `\|v\| >= 1e16` to `python_repr/1` |
| **The port's own CI comment** (`leaf-conformance.yml`) | claims the *opposite* | *"canon.ex:140 currently tests 1.0e21 where §3 says 1e16"* — **stale**, it describes the pre-ruling world |
| **The port's own moduledoc** (`canon.ex:7`) | claims `\|v\| < 1e21` | **contradicts its own code** |

**Timeline (from the port's git history).** `65b8a4d` "§3: fix the number boundary and add a
conformance test" — **2026-10-17**. The port moved to `1e16` in response to the hub-only change. The
ruling reverted that change on **2026-10-20** and pinned the spec at `1e21`. The port was never
updated. The port's own commit message for the boundary change says so plainly:

> "**NOT EXECUTED.** There is no BEAM toolchain in the environment this was written in, so neither
> the fix nor the tests below have been run. Treat them as a reviewed proposal, not a verified fix."

### Receipt 1 — a one-token mutation of the shipped referee flips 35 digests

The port's divergence is expressible as a **one-token change to the oracle the fleet ships**:

```
referee/fold.py:153
-    if isinstance(v, float) and v.is_integer() and abs(v) < 1e21:
+    if isinstance(v, float) and v.is_integer() and abs(v) < 1e16:
```

Running the mutated referee against the shipped corpus (`git.pp-ng/conformance/cases.json`,
regenerated live by `python3 conformance/harness.py` → **919 cases / 1,083 verify probes**):

```
LEAF-BAND family cases in the shipped corpus: 12
  leaf-band-1e16  leaf-band-1e18  leaf-band-7e20  leaf-band-below-1e21
  leaf-band-neg-1e18  leaf-band-neg-2pow53  leaf-band-1e21  leaf-band-2p5e21
  leaf-band-ctrl-2p5e-7  leaf-band-ctrl-negzero  leaf-band-combined
  leaf-band-mixed-closure

FAMILY-ONLY (12 leaf-band cases)  leaves  29/ 9 diff   roots  29/18 diff   probes  13/ 8 diff   TOTAL=35
WHOLE CORPUS                       leaves 16652/ 9 diff roots 16621/18 diff probes 1083/ 8 diff  TOTAL=35
```

- **35 divergences** (9 leaves, 18 closure roots, 8 verify answers) across **7 of 919 cases**.
- **All 35 are inside the LEAF-BAND family; zero elsewhere** — the fleet's own qualitative claim,
  reproduced independently.
- The family's shape reproduces the ledger exactly: **29 leaves and 29 closure roots**, as
  `RESULTS.md §1.7` states.
- The fleet recorded **45**; this measurement gives **35** under the convention "leaves + roots +
  probes". The direction, the localisation, and the corpus shape all reproduce; the count differs by
  convention, not by finding. Reported as measured, not reconciled by assertion.

**So: the BEAM port, as it stands, fails the shipped corpus on exactly the family that exists to
discriminate this clause.** The conformance run would print `DIVERGENCE[roots]` and
`DIVERGENCE[verify]` for 7 cases and exit 1 with `BEAM CONFORMANCE: FAIL`.

### Receipt 2 — the port's unit suite actively defends the divergence

`test/spec_boundary_test.exs` (runs in CI):

```elixir
# |v| >= 1e16 and integral -> scientific. THIS is the band the port gets
# wrong: canon.ex:140 tests 1.0e21.
test "1e16 is SCIENTIFIC, not integer digits" do
  assert Canon.leaf_number(1.0e16) == "1e+16"
end
```

and its own docstring:

> "The expected leaves are the spec's, cross-checked against the five leaf ports that agree
> 20,043/20,043."

The spec's leaves are `10000000000000000` (the exact integer), not `"1e+16"`. **The suite pins the
port's stale clause and attributes it to the spec.** This is the *mutation-proves-the-suite-is-
defending-the-bug* shape: mutating the code **toward** the spec's value is the only thing that turns
this suite red.

### Receipt 3 — the float-fuzz oracle already disagrees with the port, and the README reports 0

`conformance/float_fuzz.py` (the port's own oracle) implements the **spec's** rule (`abs(f) < 1e21`);
the port implements `1e16`. Running the documented command's first half produces 10,018 values;
comparing them under each rule:

```
fuzz values: 10018
PORT vs SPEC mismatches: 4018      (40.1%)
values in the disputed band [1e16,1e21): 4018
   1e+16                    spec: 10000000000000000        BEAM: 1e+16
   7.248182946264747e+20    spec: 724818294626474655744    BEAM: 7.248182946264747e+20
   -1.1692276923229412e+20  spec: -116922769232294117376   BEAM: -1.1692276923229412e+20
```

The spec's own `src/fold.ts` comment names that second value's expected spelling — *"e.g.
724818294626474655744, not ...400000"* — and it is exactly the value the port gets wrong. The
BEAM README claims:

> "float fuzz: 10018 doubles, **0 leaf-encoding mismatches** vs CPython"

That claim is **false for the current code**. The documented command
(`python3 conformance/float_fuzz.py > /tmp/floats.tsv && mix run conformance/float_fuzz.exs …`)
would print `float fuzz mismatches: 4018` and exit 1.

### Receipt 4 — the CI is structurally incapable of seeing any of this

`.github/workflows/leaf-conformance.yml` runs exactly two steps: `mix test` and
`mix test test/spec_boundary_test.exs`. Both are intra-repo. The **only** two checks that can see a
cross-implementation divergence — `scripts/conformance.sh` (needs a sibling `git.pp-ng` clone) and the
float fuzz (needs the same) — are **in no workflow**. The workflow's own header says so:

> "THIS PORT HAS NOT BEEN IN THE CROSS-PORT LEAF FUZZ. It diverges from the spec on two different
> number boundaries … and nothing in CI would have noticed."

### Receipt 5 — the README's conformance totals match no corpus that exists

The README quotes `derive: 898/898 · verify: 1056/1056 · freshness: 3259/3259 · roots: 16574/16574`
"against the grown corpus (2026-10-21)". The corpus today is **919 cases / 1,083 probes**; the
original spike corpus was **863 / 1,029**. The quoted numbers are an intermediate state that the
LEAF-BAND family has since moved past — the port has **never been re-run against the family that
discriminates this clause**.

The port's own README states the lesson it has not yet applied:

> "a green suite proves agreement with the corpus you ran, and a port that isn't re-run against a
> growing corpus drifts in silence."

**The port is the first victim of its own lesson.** Nothing here is a sloppiness story: the repo is
honest, unusually so — it publishes the defect, names the boundary, and states the limits. It is
simply a port that was written from the documents and left behind when the documents changed, with
a CI that cannot see the documents change.

**What to do (in order):** (1) set `@spec_integer_band 1.0e16` → `1.0e21` in `canon.ex:24` and
update `canon.ex:7`; (2) delete `test/spec_boundary_test.exs` — the LEAF-BAND family in `git.pp-ng`
is the authority and it will now pass; (3) fix the stale CI header; (4) add the conformance run to
CI against a pinned `git.pp-ng` ref so a ruling can never again move under a port silently; (5)
re-run `scripts/conformance.sh` and publish 919/1083.

---

## 2. 🔴 The fleet census has never counted the organization namespace

**This is the finding that changes how every prior number in this report lineage should be read.**

`GET /users/SuperInstance/repos` returns 5,308 rows, and **every single row's `owner.login` is
`SuperInstance` — a User.** But `GET /user/orgs` returns five organizations the same account
administers:

| org | public repos | created | in the REST census? | in the GraphQL census? |
|---|---|---|---|---|
| `purplepincher` | 19 | 2026-07-02 | no | 12 of 19 |
| `patchwork-quilt` | 12 | 2026-10-03 | no | 6 of 12 |
| `si-ready` | 1 | 2026-10-03 | no | 1 of 1 |
| `Luciddreamer-ai` | 1 | 2026-10-06 | no | 0 of 1 |
| `SI-Thor` | 0 | 2026-10-20 | — | — |

**14 of the 33 org repos appear in no census at all.** The other 19 are reachable *by name* through
the GraphQL census — but a name is not a namespace, and 19 of the 33 share a name with a user-owned
repo, so a name-keyed "have I seen this?" test cannot tell the two apart. That is how the org
namespace stayed invisible for 10 days even while individual repos in it were being audited. The 5 GraphQL-surfaced org repos are exactly `git.pp`, `git.pp-desk`, `git.pp-grid`,
`git.pp-ng`, `gitpp-beam`; the remaining 14 (`gitpp-action`, `gitpp-app`, `gitpp-demo-quilt`,
`gitpp-dogfood-b1`, `gitpp-dogfood-day1`, `outbound-scanner`, `deckboss`, `zero`,
`constraint-theory-distributed`, `capitaine-family-worker`, `deckboss-net-landing`,
`family-styles`, `purplepincher-landing`, `OpenSkyFlight`) are in neither list.

**The mechanism, exactly.** The repos were **transferred**, not forked. `GET
/repos/SuperInstance/git.pp-ng` returns **301 Moved Permanently** → `patchwork-quilt/git.pp-ng`
(200). GitHub keeps the old path working *as a redirect* and **drops the repo from the user's
list endpoint**. So:

- a tool that fetches `/repos/{owner}/{name}` keeps working (by following the redirect);
- a tool that **enumerates** `/users/{owner}/repos` never sees the repo at all.

That is the whole defect, and it is invisible to every page-count-based assertion the fleet has
ever written.

**The true publicly-visible SuperInstance-governed namespace is 5,308 + 33 = 5,341.** Every census
number the fleet has published — 4,892, 5,113, 5,296, 5,306, 5,307, 5,308, 5,311 — has counted the
user namespace only.

**Was the namespace known? Partially — and that is exactly the problem.** The transfer is visible in
the fleet's own records: `state-of-the-quilt-2026-10-15/REPORT.md` carries a table reading
*"Repos in `purplepincher` | 19 public | GitHub API"* and *"Repos in `si-ready` | 1"* — **the same
counts this round re-derived independently**. So the namespace was *documented once, in a research
doc, ten days ago*. What does not exist anywhere is an **instrument** that enumerates it: no
scout report has ever treated *"which namespaces does this account govern?"* as a census question,
and the tools that build the fleet's own map and catalog still cannot answer it.

**The cost is already visible in the written record.** Scout round 133 (2026-10-21) — the round that
examined `git.pp-ng` most closely, ran its 9-minute harness, and called it *"the highest-engineering-
quality repo found in this series"* — recorded the repo as **`SuperInstance/git.pp-ng`**. That path
**301-redirects to a different owner**. The fleet's flagship audit report prints a repository URL
that is not the repository's URL, and no link-checker caught it because the redirect resolves.

**What round 133 read and did not see.** That report read `RESULTS.md` and praised it — *"RESULTS.md
is an honest ledger, not a pitch"* — one day after the leaf-band ruling was recorded. `RESULTS.md
§1.7` ("The leaf-band incident (2026-10-20 validation pass)") is **not mentioned in it**: a grep for
`leaf|1e21|1e16|boundary|§1.7|incident` across the whole 38 KB report returns one incidental hit
about an unrelated song file. The round read the ledger's *shape* and did not read the ledger's
*contents*. That is how the ruling in item 1 survived a review that happened the day after it.

### The fleet's own reference census tool inherits the blind spot

R134 established that the fix for `plato-portal`'s truncation *"already exists in the fleet"* —
`quilt-atlas/scripts/build_atlas.mjs`, which follows the `Link` header to exhaustion and receipts its
own cap. That tool is **careful about the axis of traversal and blind about the axis of ownership**:

```js
// quilt-atlas/scripts/build_atlas.mjs:57
let nextUrl = `https://api.github.com/users/${OWNER}/repos?per_page=100&page=1`;
```

No `type=all`. It therefore enumerates `type=owner` and returns 5,308 — and its `atlas.json` receipts
(`total_repos`, `pages_fetched`, `pagination_cap`, `pagination_cap_hit`) are all about **pages**. No
receipt anywhere asks *"did I enumerate every namespace this account governs?"* The instrument is
rigorous about how far it walked and silent about what it was walking over.

`plato-portal` is strictly worse — `auto-index.yml:27` → `gh repo list SuperInstance --limit 2000` —
so it now misses **3,341 of 5,341 (62.6 %)**, up from the 62.3 % previously recorded.

**Ruled out (so nobody re-checks it):** the org `quilt` exists with 38 public repos — it is the
**Ethereum Quilt org** (EIP-3074), unrelated to SuperInstance. `GET /user/orgs` is complete for
membership; other orgs containing fleet work would need a different discovery route.

---

## 3. 🟢 `patchwork-quilt/git.pp-desk` — a live system with a reproduced receipt, and no CI

**Repo:** `patchwork-quilt/git.pp-desk` (TypeScript, Cloudflare Workers Agent, 107,610 B).
**Named, never examined.** `state-of-the-quilt-2026-10-15/REPORT.md` records one PR (*"Desk v2:
closure-root pinning, manifest-gated refresh, the real destroy() test"*); round 133 listed it as an
unseen neighbour. The 472-line playtest below appears in no prior report. **Zero workflows.**

**What it is.** A read-only window onto a git.pp project: it serves the derived state, the conflicts
and who won them, and how stale each witness is — and it can **destroy and rebuild itself
byte-identically from the record alone**. Live at `https://gitpp-desk.superinstance.dev`.

**Receipt — I ran its own playtest, live, today.** `test/playtest.mjs` is 472 lines, 63 assertions,
**zero dependencies** (`node:crypto` only), and `package.json` has no `test` script at all:

```
$ node test/playtest.mjs
PASS  1. desk digest == independent digest
PASS  1b-i. this port reproduces the pinned root at task-c — task-c closure root=60effe23970d8a5cc837636c44685502361288c1f00577e9addfa10cbd4fc91d
PASS  1b. desk set root == independent set root
PASS  2a. burn leaves the desk empty
PASS  2b. rebuild digest == pre-burn digest — IDENTICAL
PASS  2c. rebuild root == pre-burn root — IDENTICAL
PASS  5d. five seeded shuffles re-fold to the canonical digest — permutations=5, mid-fold divergence on 5/5
PASS  5b. websocket broadcasts the projection
…
16 PASS, 0 FAIL, exit 0
```

The README claims *"16/16 on `poc-quilt-1`, 16/16 on `poc-scale-1`, 19/19 on `demo-race-1`"* measured
2026-10-14. **16/16 on `poc-quilt-1` reproduced live today, including the destroy drill** — the run
above burned the live Desk instance (digest/root → null, records → 0) and rebuilt it to the identical
digest `010e942c…` and root `2b79c3d2…`. The 5 seeded shuffles each *mid-fold diverged* (5/5) and
*end-fold converged* — the test is not a constant.

**Why another agent should care.** This is the fleet's strongest verification contract: the digest
is recomputed **in the test script by a second implementation of the canonical form** over bytes
fetched from the record — never through the Desk — and the closure root is held to a from-the-doc
port anchored to a conformance-pinned literal. Two implementations, over the record, agreeing. It is
also **the only place in the fleet where I could find a system whose state is provably rebuildable
from a record**, which is the operational form of the cell doctrine.

**Structurally wrong:** there is **no CI and no `npm test` script**, and the playtest requires a
live network (`DESK_URL`/`SOURCE_URL` default to the deployed Workers). The verification contract
can only be exercised by hand against a live deployment — so the fleet's own tooling, and every
scout round that ranks by "does it have CI", would score this repo as untested. It is the
strongest artifact in the namespace and it is invisible to the instrument.

---

## 4. 🟠 `quilt-arcade` — the fleet's cited positive control carries 235 vendored files

R129 cited `quilt-arcade` as the positive control worth copying ("chain genuinely tamper-evident").
Today, **235 of its 388 tracked files are `node_modules/`**:

```
tracked node_modules files: 235 of 388 total files
  node_modules/.bin/yaml, node_modules/.package-lock.json, node_modules/yaml/LICENSE, …
```

and `.gitignore` contains exactly one line — `node_modules/`. The ignore rule is present and
cosmetic; the files are still tracked. The fix is `git rm -r --cached node_modules` (the same
`git rm --cached` that `superinstance-api`'s `.wrangler/` still needs, and which is still needed
there — `.wrangler/cache/wrangler-account.json` is tracked as of this round).

**The same class across the fleet (tracked build output, live):**

| repo | tracked build/cache artifacts |
|---|---|
| `quilt-arcade` | **235** (`node_modules/`) |
| `quality-gate-stream` | 22 (incl. **20** `__pycache__`/`.pyc`, plus a built wheel and sdist) |
| `quilt-gpu-lab` | **119** (incl. `__pycache__/guard.cpython-314.pyc` and `experiments/wg1_wgsl/target/release/deps/*.rlib`, `*.rmeta`) |
| `quilt-canary` | **52** (`target/`) |
| `moth-honest` | 11 (`__pycache__`) |
| `pie-minimax` | 2 (`__pycache__`) |
| `fleet-seeds` | 1 (`__pycache__`) |

**A positive control that has rotted is worse than no positive control**, because the fleet cites it
as the thing to copy.

---

## 5. 🟡 The brief's ALREADY-FOUND list — status re-verified, two changes, one fix

Re-checked against live trees (not re-derived from the original reports):

| repo | brief said | **today** |
|---|---|---|
| `substrate-attest-rs` | 430/434 tracked files are build output | **FIXED** — now 5 files (`.gitignore`, `Cargo.lock`, `Cargo.toml`, `README.md`, `src/lib.rs`) |
| `substrate-*` (24 repos) | "all 13 … have ZERO CI" | **CHANGED** — 2 of 24 now have CI: `substrate-embedding`, `substrate-rng`. The other 22 still have none. (The "13" was also never the full set — there are 24.) |
| `quality-gate-stream` | committed live API keys | **CHANGED** — now CI=1 + 12 test files. The committed `__pycache__` (20 files) and built wheel/sdist remain. *The live-key claim was not re-verified this round — that needs the secret-scanning API, not a tree.* |
| `quilt-canary` | 52 tracked `target/` artifacts, no `.gitignore`, zero tests | **PERSISTS** — 52 tracked build artifacts, CI=0, 0 test files |
| `superinstance-api` | `.wrangler/` listed in `.gitignore` but still tracked | **PERSISTS** — `.wrangler/cache/wrangler-account.json` is tracked |
| `xruntime-conformance` | 23/23 digests; 3 hardcoded `/tmp` paths, missing driver, no CI | **PERSISTS** — CI=0, 0 test files, 12 files total |
| `quilt-i2i` | dup dirs, no canary, no CI | **PERSISTS** — CI=0 |
| `quilt-ewitness` | 7/7, mutation → 4/7, no CI | **PERSISTS** — CI=0 |
| `quilt-tournament` | 6 impls unpublished; 25-pt bonus; stopped at R4 | **PERSISTS** — CI=0 |
| `pie-minimax` | author self-corrected | **PERSISTS** — 2 tracked `__pycache__` files |
| `quilt-gpu-lab` | committed `__pycache__` + 58 `.rlib`/`.rmeta` | **PERSISTS** — now **119** build artifacts |

---

## 6. 🟢 Positive control: the `purplepincher` org's doctrine is literally true

The `purplepincher` org states its rule in its own README: *"documented so **every claim is literally
true**"*, and *"Eleven repositories have earned the shell."*

**Checked, not assumed:** (the org's 19 repos were already counted in
`state-of-the-quilt-2026-10-15/REPORT.md`; the *README claim* below is the new check.)
The README links **exactly 11** distinct `github.com/purplepincher/*`
repositories — `conservation-guardian`, `constraint-theory-core`, `deckboss`, `exocortex-mcp-ts`,
`git-native-agents`, `intent-directed-compilation`, `pincher`, `plato-engine-block-c`,
`plato-semantic-search`, `sonar-vision`, `vessel-tuner` — out of **19 public repos** in the org,
with the taxonomy (field-tested / infrastructure / not-yet) spelled out per entry. The count claim is
**true**, and it is true *of a subset it defines*.

Also verified rather than assumed: `deckboss` ships **28 test files** including property-based
`conflict-resolver.property.test.ts`, and its single workflow `deploy-pages.yml` **does** gate on
`npm run typecheck` **and** `npm run test` before deploying — so the tests do run. (I checked this
because "one workflow named deploy" reads like a missing-CI defect; it is not.)

**This is the shape worth copying:** a doctrine that is *falsifiable on its own text*, and a repo
whose README counts are checkable against the file list.

---

## Fleet-wide

1. **The census instrument is the weakest link in the fleet, and it is now weaker than believed.**
   5,308 was a "census". The account governs **5,341** publicly. `quilt-atlas` — the tool the fleet
   cites as the fix — has the same blind spot, and it is blind on a different axis than the one it
   was built to fix. **A census must receipt its namespace, not only its pagination.**
2. **The most finished work in the fleet (`patchwork-quilt`: a live multi-agent coordination
   substrate with a cross-implementation conformance port, a live destroy-and-rebuild receipt, and a
   GitHub App posting derived state as Checks) sits in a namespace the census cannot enumerate.**
   `git.pp-ng` was examined in depth by round 133; its Elixir sibling, the Desk, the Grid, the App
   and the outbound scanner were **not**. The org's own transfer notice is in the fleet's git log
   (`gitpp-beam` PR #1: *"retarget git.pp-ng references to patchwork-quilt (post-transfer)"*), and
   **no instrument in the fleet was updated for the transfer.**
3. **`plato-portal`'s catalog now misses 3,341 of 5,341 (62.6 %)**, and its cause is now known twice
   over: a hard `--limit 2000` *and* a namespace that is never enumerated.

## New failure classes (lettering continues after (dw))

- **(dx) A census that receipts its traversal axis but not its ownership axis.** The instrument
  follows pages to exhaustion and receipts the cap, but enumerates one namespace
  (`/users/{owner}/repos`, default `type=owner`) and never asks whether the account governs others.
  **Detector:** diff the REST list against `GET /user/orgs` → `GET /orgs/{o}/repos`; assert
  `rows == user_repos + Σ org_repos`. A census that cannot fail on the denominator it never
  computed.
- **(dy) A port left behind by a ruling the port never saw.** An independent implementation written
  from documents can be structurally correct and still be pinned to a clause amended upstream
  afterwards — and its own test suite then *defends* the stale clause and attributes it to the spec.
  **Detector:** for every pinned constant in a port, find the upstream ruling that set it and
  compare dates (port commit date vs ruling date). Here: port moved 2026-10-17, ruling 2026-10-20,
  port last touched 2026-10-22 — a later commit that still did not revisit the boundary.
- **(dz) A conformance port whose only cross-implementation check lives outside CI.** The one suite
  that can see a cross-implementation divergence needs a sibling clone or a network, so CI runs the
  intra-repo suite — the one that cannot see it. **Detector:** grep every workflow for the
  cross-port command; if it is absent from all of them, the CI cannot see a cross-implementation
  divergence *by construction*, and a green badge says nothing about interoperability.

## Method notes (carry forward)

1. **GraphQL `orderBy: {field: NAME}` is a total order** and is the right instrument for a fleet
   census: no ties, so no silent page overlap, no need for a casefold assertion. Use
   `totalCount` as the denominator. But **do not fetch trees in the census query** — 100 repos with
   `object(expression:"HEAD:")` reliably 502s. Census and substance must be two passes.
2. **`GET /user/orgs` is a one-call census check that nobody was making.** It cost 1 request and
   changed the meaning of every number in this report lineage.
3. **A divergence can be proven without the divergent language's toolchain.** The port is Elixir and
   the sandbox has no BEAM; the divergence was still proven by mutating the *shipped oracle* by one
   token and re-running the fleet's own corpus. **When the port cannot run, mutate the referee.**
   This is the cheapest cross-implementation receipt available and it generalises.
4. **A doc-only port inherits the spec's age, not the spec's content.** When the port's last commit
   is *after* the upstream ruling's date but the pinned constant still differs, the port was
   revisited and the constant was missed — a much stronger signal than "the port is old".
5. **Run the fleet's live playtests.** They are often zero-dependency (`node:crypto` only), need no
   install, and take ~30 s. The 16/16 receipt in item 3 cost one command.
6. **Check a workflow's `run:` body before scoring "no CI".** `deckboss`'s only workflow is named
   `deploy-pages.yml` and nevertheless gates on `npm run test`; the reverse error (a workflow named
   `ci.yml` that runs nothing) is also common.

## Environment (this wipe)

- `/workspace` **NAS at 100 % (EDQUOT, 0 avail)** for the whole session; all work on the `/tmp`
  overlay, all delivery by git.
- `gh` absent. `GIT_SSL_NO_VERIFY=1` required for every clone/fetch.
- REST core quota was **292 remaining at session start** and had been largely spent before the
  session began; GraphQL was at 4,999 and carried the census. **GraphQL is the instrument to reach
  for when REST is exhausted.**
- No `elixir`/`mix`/`erl` in the sandbox (as expected) — the Elixir port was **not executed**; its
  divergence was proven by mutating the shipped Python referee instead. Stated explicitly so the
  claim is not over-read.
- `python3`, `node` available. `npm install` unusable (NAS) and unnecessary — the playtest is
  zero-dependency.
- Prior report for this round: `SCOUT-2026-10-25T0810Z-…` (`9ded2bd`); census there was 5,308 — this
  round's user-namespace count is identical (5,308), and the difference is entirely the 33 org repos.
