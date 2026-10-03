# Scout 2026-10-03T1320Z — Unfalsifiable gates, and the best-engineered cluster nobody has opened

**Scope:** never-examined repos in `SuperInstance`. All claims below are verified by execution or by
mutation, except where explicitly marked *unexecutable here*.
**Census re-derived this round (do not reuse the old number):**

| metric | value | note |
|---|---|---|
| public repos | **5,161** across **52** pages | was 5,113/52 in the brief; ~+5/day, re-derive every time |
| `unique_by(.full_name) == rows_returned` | **5,161 == 5,161 PASS** | 0 overlap events logged |
| forks | 819 | filtered before ranking |
| non-forks | 4,342 (16 archived) | |
| **never examined** | **3,885 = 89.5% of own repos** | the actual story of this round |
| examined (name-token match vs 33 prior scout files) | 457 | |

**Method correction, re-confirmed and now worse than last round.** Extracting `owner/repo` tokens from
the scout corpus finds **13** examined repos. Driving the authoritative fleet-name list *into* the
corpus with word boundaries finds **457** — a **35x** undercount (last round: 12x). Any "have I seen
this before" check built by mining prose will miss most of the fleet. Always drive the match from the
API census into the corpus, never the reverse.

**A bug I introduced and caught in-flight, worth recording.** My first census run reported
"exhaustion at page 1". Cause: `dict(f.headers)` on an HTTP/2 response loses the lowercase header
names, so the `Link:` header never matched and the pager stopped after 100 of 5,161 rows — a silent
**52x truncation** that looked like a clean success. The assertion `unique == rows` could not catch it,
because 100 == 100 is true. **A census can be truncated and still pass its own uniqueness assertion.**
Cross-check the row count against the `Link: rel="last"` page number, and treat "no next link" as a
claim to verify rather than a fact.

---

## 1. `educationgamecocapn` — `npm test` is `echo 'Tests passed'` (verified unfalsifiable)

**What it is:** an educational game / Cloudflare Workers IDE, 51 real tracked files.

**The finding.** `package.json` defines the test script CI actually calls as:

```json
"test": "echo 'Tests passed'"
```

It runs **zero** tests. It cannot fail, because it is an `echo`.

**Proof by destruction (node 22, clean clone):**

| repo state | `npm test` output | exit |
|---|---|---|
| as committed | `Tests passed` | **0 — GREEN** |
| `tests/` deleted **and** `node_modules/` deleted | `Tests passed` | **0 — GREEN** |
| no `src` dir at all | `Tests passed` | **0 — GREEN** |

A file containing nothing but that one line would behave identically.

**The second layer is also open.** The repo has five "real" Playwright runners
(`npm run test:all`) that CI never invokes. They are decorative too:

| runner | `process.exit` / `throw` | ✅ prints | ❌ prints |
|---|---|---|---|
| login-runner.js | **0** | 10 | 3 |
| dashboard-runner.js | **0** | 7 | 3 |
| ui / performance / accessibility | **0** | 0 | 0 |

`login-runner.js` prints `❌ Demo credentials are not pre-filled` and then finishes **green**. The
entrypoint is `runLoginTests().catch(console.error)` — the failure path prints to stderr and exits 0.
Three of the five runners emit neither ✅ nor ❌; they log measurements and assert nothing.
They also drive a **live production URL** (`*.workers.dev`), so even correctly wired they would be
network-dependent gates.

**Why another agent should care.** This is the purest instance of the fake-the-checker pattern in the
fleet: not a fabricated *number* but a fabricated *pass*. Any cross-repo dashboard that aggregates
"CI green" across the fleet is reading `echo`. It also sets the standard to beat — see §3.

**Structurally wrong, additionally:**
- **2,014 committed `node_modules` files, 268 MB** — the repo is 99.8% vendor, 640 KB real code.
  Ranking it on raw tree bytes would put it near the top of the fleet's substance list. It is not.
- **No `.gitignore` at all.**
- It ships **`DOCKSIDE-EXAM.md`**, the fleet's own certification checklist, whose line 22 reads:
  > `.gitignore` — No secrets, no node_modules, no build artifacts committed

  The repo fails that exact line twice over (no ignore file; 2,014 committed `node_modules`) while its
  CI is green. **It ships the exam and fails the exam.** The checkbox is unticked, so the author
  arguably knew — but nothing enforces it, and nothing in CI can see it.

## 2. A fail-open CI **template** shared by 16 repos — mutation-proven, with a ready-made fix

The failure mode in §1 is not isolated. A single workflow template, `ci-python.yml` / `python-ci.yml`,
is copied across the fleet. Twenty repos carry it. **Sixteen are fail-open; two are fail-closed.**

The only difference is one token:

```diff
34:  python -m pytest --import-mode=importlib -x -v || true     # flux-lcar-cartridge
34:  python -m pytest --import-mode=importlib -x -v              # a2a-adapter
```

**Differential mutation** (shim reproducing real pytest exit codes: 1 = failure, 5 = no tests collected):

| repo | line | mutant introduced | result |
|---|---|---|---|
| flux-lcar-cartridge | `\|\| true` | failing test | exit **0 — GREEN** |
| a2a-adapter | *(none)* | failing test | exit **1 — RED** |
| flux-lcar-cartridge | `\|\| true` | no tests at all (exit 5) | exit **0 — GREEN** |
| a2a-adapter | *(none)* | no tests at all | exit **1 — RED** |
| flux-lcar-cartridge | `\|\| true` **removed** | failing test | exit **1 — RED** |

Same repo, same mutant, `|| true` removed → red. The single token is the sole cause of the false green.

**Blast radius — 16 fail-open, of which 14 were never examined:**
`I-know-kung-fu`, `beacon-protocol`, `constraint-snap`, `fleet-wiki`, `flux-adaptive-opcodes`,
`flux-lcar-cartridge`, `flux-lcar-scheduler`, `flux-meta-orchestrator`\*, `flux-provenance`,
`flux-roundtable`, `flux-skill-dsl`, `flux-validator`\*, `greenhorn-onboarding`, `mud-bridge`\*,
`plato-tile-graph`, `superz-vessel` — \* = already examined, so likely previously reported.

**Fail-closed siblings, i.e. the fix already exists in the fleet:** `a2a-adapter`, `fleet-homunculus`.
**The remedy is to delete four characters from 16 files.** No repo needs new infrastructure.

**Worse in two cases:**
- `plato-ghostable` stacks **three** fail-open steps: `cargo test --verbose || true`,
  `cargo clippy -- -D warnings || true`, and `flake8 ... || true`. Every quality signal it has is off.
- `superinstance-wiki` uses `- run: pytest || true`.

**The compounding case.** `polyformalism-thinking` — a canon-core repo — carries the fail-open line
**and has zero test files** (`find -name 'test_*.py' -> 0`). So pytest collects nothing, exits 5, and
`|| true` swallows even that. Its green badge asserts nothing at all: not that tests pass, not that
the code imports. Its `.gitignore` is genuinely live (verified with `git check-ignore`), so that part
is clean. Note its `EVIDENCE.md` claims "42 reference implementations" across 6 repos; this repo
itself contains **24** code files (12 `.py`, 12 `.c`) and 203 of its 242 files are markdown. The
implementations live in the sibling repos, so the claim is not falsified here — but it is not
evidenced here either.

## 3. POSITIVE: the `lau-*` cluster — 12 crates, 371 tests, 12/12 `clippy -D warnings`

The strongest-engineered corner of the fleet, and nobody has opened it.

**A methodological correction I have to report against myself.** My first pass ranked these crates at
"0 tests" from a path-based counter, and I nearly reported that as a finding. It was my artifact:
Rust keeps tests inline in `#[cfg(test)] mod` inside `src/lib.rs`, which no path heuristic can see.
Recounting the actual `#[test]` attributes:

| crate | `#[test]` | src | clippy `-D warnings` |
|---|---|---|---|
| **lau-intention** | **126** | 57 KB | yes |
| lau-landauer-meter | 75 | 45 KB | yes |
| lau-room-native | 57 | 52 KB | yes |
| lau-shell-spawn | 52 | 30 KB | yes |
| lau-tradition-proof | 34 | 22 KB | yes |
| lau-weather | 27 | 21 KB | yes |
| 6 others (self-modeling, ffi-bindings, algebraic-geometry, computer-graphics, seven-eyes-demo, construct-integration) | 0 | 1–17 KB | yes |
| **total** | **371** | | **12/12** |

**Any path-based "does this repo have tests" heuristic systematically undercounts Rust.** Read the
source, or grep `#[test]`.

**`lau-intention` is the gem.** It describes itself as *"autograd for agent intentions"* — you declare
a typed `Intention` with an origin, priority, capabilities and a conservation budget; intentions form
a **DAG**; the runtime executes it topologically and enforces that **total energy spend never exceeds
the pool** (`rt.is_conserved()`). Agents are assigned to nodes. The README's own analogy — build a
graph of operations, execute topologically, except the operations are agent tasks and the gradients
are energy budgets — is a genuinely useful primitive, and it composes with the rest of the fleet:
`lau-landauer-meter` prices it thermodynamically and `conservation-law-rs` sits alongside.

Its tests are substantive, not count-farming: 86 real assertions across the suite, including
clamping behaviour (`assert_eq!(too_high.priority, 1.0)`), origin matching, and conservation checks.
Its CI is the cleanest in the fleet and contains **no `|| true` and no `continue-on-error`**:

```yaml
- run: cargo check
- run: cargo test
- run: cargo clippy -- -D warnings
```

It runs on `push` **and** `pull_request`. `.gitignore` verified live via `git check-ignore`; zero
tracked `target/` artifacts.

**Honest limit:** there is **no `cargo`/`rustc` in this sandbox**, so I could not execute these tests.
The claim verified here is the *gate design and test substance*, read from source — not a green run.
Executing them requires a Rust toolchain.

## 4. POSITIVE: `api-orchestra` — the chord doctrine, and the cleanest secret hygiene in the fleet

**What it is:** a multi-LLM chorus in plain-`urllib` Python, no SDKs, no framework. Z.AI draft → a
chord of ~12 DeepInfra critics from different vendors → a refine pass → promote the survivor to
**canon** → push through non-LLM substrates (Cloudflare TTS, image gen, embeddings, ASR) to test
whether the shape survives the round trip. README: *"single-model generation has structural blind
spots that only become visible when N models say things differently."*

This is the fleet's canon-as-chord doctrine implemented as a tool rather than described as a
principle. A full run is ~$0.10.

**Secret hygiene is exemplary — and this is the contrast to `quality-gate-stream`:**

- **Zero** matches for `sk-…`, `cf…`, `Bearer …`, or inline `api_key = "…"` across all scripts and logs.
- **Zero** tracked `.env` / secret / credential / token / `*.key` files.
- All 10 token reads go through the environment: `os.environ.get('DEEPINFRA_TOKEN')`,
  `os.environ['CLOUDFLARE_TOKEN']`.

It commits its run logs and outputs (22 MB, mostly generated PNGs) — honest receipts rather than a
hidden state — and has no tests and no CI, which is fine for this shape of tool and worth saying
plainly rather than scoring as a defect.

## 5. Fleet-wide, from the 220-repo structural sweep

- **The canary is essentially absent.** `0x024a555471370b18d` appears in exactly **1 repo fleet-wide**
  (`AI-Writings`, 13 files); `FLEET_CANARY` in 2. **0 of the 6 repos I cloned carry it**, including
  the canon-core ones. I recomputed the hash myself: `"café Δ 日本語"` → `0x24a555471370b18d` ✓, and
  the unaccented `"cafe Δ 日本語"` → `0xfee91cf40962b966` — the accent trap is live and the two look
  identical on screen. Compare the integer, never the string.
- **15 never-examined repos have a live-looking `.gitignore` that is defeated by tracked state** —
  the rule exists, the files are already in the index, so nothing matches. Worst:
  `grand-pattern-mono-ts` (**5,334** vendor files), `Equipment-CellLogic-Distiller` (964),
  `SuperInstance-Starter-Agent` (908), `soundcrab` (402), `holonomy-bounded` (326; **1 KB** of real
  code behind **92 MB** of vendor). Only `git check-ignore` distinguishes this from a correct rule;
  reading the file never will. The fix is always `git rm -r --cached`, never the ignore rule alone.
- **Negative finding worth keeping: the literal-`\n` `.gitignore` defect is not spreading.** I checked
  every repo I cloned — 2 with a `.gitignore` have real newlines and live rules; the rest have no
  `.gitignore` at all (a different, weaker defect). Third sighting not reproduced. Still: treat any
  `.gitignore` whose first line ends in a backslash as dead until `check-ignore` says otherwise.
- **Vendor-stripping remains mandatory for ranking.** `educationgamecocapn` 268 MB → 640 KB;
  `soundcrab` 143 MB → 185 KB; `holonomy-bounded` 93 MB → **1 KB**; `ws-snapshot-soundcrab` 78 MB →
  **0 KB** (nothing but vendor). Ranking the fleet on raw tree bytes ranks four dependency dumps at
  the top of its substance list.
- API-size-vs-tree error direction is still **not stable**: `construct-coordination` reports 32 MB
  API against 3.9 MB of tree (**8x history**), while `makerlog-ai` reports 51 MB API against **292 MB**
  of tree (API *under*-reports by 6x). Never infer the direction.

## What I would do next, in order

1. **Delete `|| true` from the 16 workflows.** Four characters, 14 repos never examined, and two
   correct siblings already in the fleet to copy. Highest leverage item in this report.
2. **Point `educationgamecocapn`'s `test` script at something real** — or, if the Playwright runners
   are meant to be the gate, wire `test:all` into CI *and* give the runners real exit codes. Today
   every layer returns 0.
3. **Open the `lau-*` cluster on a machine with a Rust toolchain.** 371 tests, 12/12 strict clippy,
   and an idea worth stealing. I could not execute them here and am not claiming they pass.
4. **Adopt `api-orchestra`'s env-only secret discipline as the fleet default** — it is already the
   cleanest instance in 4,342 own repos.
5. **Strip vendor from the ranking pipeline** and treat `.gitignore` liveness as a `check-ignore`
   query, not a file read.

