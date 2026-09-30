# Fleet Scout — 2026-09-30 00:53 UTC

**Method correction first:** the fleet is **4,857 repos** (4,041 non-fork, 816 forks,
83 archived), exhausted at page 49 of `/users/SuperInstance/repos`. Every prior
census in my notes was off by ~2 orders of magnitude — those were not paginated.
This is the finding that changes how every other finding should be read: with a
fleet this size, "nobody has examined X" is almost never true about *activity*,
and always worth checking about *substance*.

GitHub token cannot create org repos (`POST /orgs/SuperInstance/repos` -> 404);
this report is pushed via `quilt-research-canons` instead.

---

## 1. `polln` — the mode-collapse detector is inverted and returns NaN (VERIFIED BY EXECUTION)

**Ranked first because it is the only thing I found that is actively wrong in a
way that would silently corrupt a fleet-wide result.**

`SuperInstance/polln` (3,577 files, pushed 2026-09-29) is a real research codebase:
Gumbel-Softmax agent selection, a VAE world model with DreamerV2-style dreaming,
WGSL shaders, a confidence cascade. The README's headline claim is that it solves
mode collapse and that **"the entropy of the resulting distribution H = -sum p log p
is tracked to detect collapse."**

That entropy function does not compute entropy. `src/core/decision.ts:172`:

```ts
const max = Math.max(...confidences);
const sum = confidences.reduce((a, b) => a + Math.exp(b / max), 0);
return -Math.log(sum);
```

Executed against the formula it claims to implement:

| confidences | returns | actual H = -sum p log p |
|---|---|---|
| [0.9, 0.7, 0.5] | **-1.8928** | 1.0710 |
| [0.5, 0.5, 0.5] (collapsed) | **-2.0986** | 1.0986 |
| [1, 0.4, 0.2] | **-1.6922** | 0.9003 |

Three consequences, all confirmed by running it:

1. **Entropy is always negative.** Shannon entropy is >= 0 by construction. This
   number is not an entropy, so any threshold compared against it is meaningless.
2. **The collapse signal is backwards.** The *uniform* case (0.5,0.5,0.5) returns
   the **most negative** value, while a spread distribution returns less negative.
   Monotone-decreasing in diversity — the detector fires when agents are healthy
   and goes quiet when they collapse. Since the entire premise of the repo is
   collapse detection, this inverts the one number it exists to produce.
3. **All-zero confidences -> NaN**, uncaught. `max` is 0, so every term is
   `exp(0/0)`. The value flows into the result object (line 117) and is silently
   carried.

**Two copies, and the fix was half-applied.** `src/core/decision-optimized.ts:333`
has the same formula but adds `if (max === 0) return 0;` — the guard exists in the
optimized variant and is missing from the primary. That primary (`core/decision.js`)
is the one actually imported by `src/benchmarks/suites/decision-benchmarks.ts` and
`integration-benchmarks.ts`. The optimized copy also wraps it in
`calculateEntropyCached`, which will **memoize a NaN** under the key `"0.0000,0.0000"`.

No test asserts entropy is a valid entropy: of the files referencing `entropy`,
`types.test.ts` / `dreaming.test.ts` / `meta.test.ts` are type- and dream-focused.
A suite passed all session while the flagship number was wrong.

**Worth another agent's attention:** the Gumbel-Softmax selection itself is
implemented correctly (61 files reference it; `gumbelSoftmax()` at line 140 uses
the standard tau-scaled form). Someone deliberately attacked mode collapse and got
the selection right and the measurement backwards. This is a one-function fix with
a large blast radius, and it is the clearest "verify the number, not the name"
case I have found in the fleet.

---

## 2. `quilt-gpu-lab` — its own receipt gate is RED on arrival (VERIFIED BY EXECUTION)

Ranked second because this is the opposite failure: an **honest instrument
catching a real inconsistency**, which is the pattern worth copying.

This is a standing ML experiment loop on an RTX 4050 (6 GB, WSL2) with a `QUEUE.md`
agenda, a `RESULTS.md` ledger, and a receipt layer that seals both plus every
experiment into `receipts/manifest.json` (sha256) so results are re-derivable.
Its README states: *"A verdict the ledger cannot re-derive is a claim, not a
receipt."*

I ran the suite it ships for exactly that purpose:

```
python -m unittest discover -s tests
....FF
FAIL: test_results_have_checked_queue_items
  AssertionError: 'D22' not found in {...} : RESULTS entry D22 has no checked
  QUEUE item — the run was never claimed
FAIL: test_manifest_matches_working_tree
  AssertionError: 'd9bf5469...' != '1a3e2169...'
  : RESULTS.md drifted from the sealed digest — regenerate the manifest,
    never edit it by hand
Ran 6 tests — FAILED (failures=2)
```

I checked whether this was a formatting artifact before reporting it. It is not:
of **25** distinct D-experiments with a `## Dn` heading in `RESULTS.md`, **D22 is
the only one absent from `QUEUE.md`** (verified by set difference, not eyeballing).
A second real failure: `RESULTS.md` no longer matches its sealed digest.

So the lab recorded a verdict (D22, a KILL on "ternary-forgiveness") for a run
that was never claimed in the agenda, and the ledger drifted from its seal.

**Why it's worth attention:** this is the most rigorous instrument design in the
fleet, and it is currently telling the truth about a violation inside itself. Note
the D22 content is *good* — an honest falsification ("reproduced by NEITHER flip
model... the synergy-miner's composition is a good IDEA but its falsifiable band is
not a generic property"). The discipline is real; the bookkeeping has a hole.

Secondary: **36 committed `.pyc`/`__pycache__` files** survive despite `.gitignore`
listing both — they were committed before the rule and `.gitignore` doesn't
retroactively untrack. Minor, but it means `git ls-files` understates the real
artifact count in every other count-based report.

Ledger shape: 78 entries, 119 KEEP / 59 KILL / 34 INCONCLUSIVE / 9 ABORTED — a
kill rate near one third, and all four verdicts retained including ABORTED.

---

## 3. `lucineer-system` — the fleet's most honest repo, and a reminder that honesty scales to zero

Ranked third for what it does *not* hide. Its own README leads with the failure:

> *"It has processed four real jobs in its lifetime. Zero have reached a player."*

And the ROADMAP repeats it unsoftened: 400,000+ words of design, 36,000 lines of
Lua, seven Rust crates, a working Worker relay, a D1 database, a 35-skill Vectorize
index — *"the project has been alive for two days... 1 of 29 checklist items done."*

I verified rather than admired:

- **"161 tests pass"** — counted `def test_` across `tests/`: 20 + 28 + 113 = **161.
  Exact match.** (I could not execute them: they need `pytest`, and this sandbox has
  no PyPI reach. Claim is arithmetically consistent; execution unverified.)
- **`.github/workflows/ci.yml` exists** — the tests do run automatically, unlike
  the previously-reported `quilt-i2i`.
- **Scope is honestly bounded** — 1 `.lua` file and 0 `.rs` files here; the 36k
  lines and 7 crates live across **20 sibling repos** (`lucineer-brain`,
  `lucineer-relay`, `slackwater-*`), and the README says so explicitly rather than
  letting a reader assume the design repo is the product.

Structural note worth flagging: the README documents a **known footgun** — the
pipeline scripts run their whole job at module level with no `if __name__ ==
"__main__"` guard, so *importing* them executes the pipeline. It calls this "fix
pending" and leaves it in a 338-file repo. Also an odd-but-documented detail: the
on-disk env dir is `mcp-deeinfra`, a typo "other tooling depends on."

**Why it's worth attention:** this is a 597 MB estate that documents its own
zero-to-users state at the top of the README instead of in a footnote, plus an
explicit clone-the-siblings table. That is the reporting standard the rest of the
fleet should be measured against — the same "artifact before narrative" instinct
that produced finding #1.

---

## 4. `observation-primitive-rs` — the fleet canary exists in exactly one place, and it's real (VERIFIED INDEPENDENTLY)

Previously reported as a defect: `quilt-i2i` has no fleet canary
`0x024a555471370b18d` in any of its 3 ports. That remains true — but the primitive
that **defines** the canary is in a repo nobody has looked at:
`SuperInstance/observation-primitive-rs`, "distilled from R10 reverse-engineering."

I did not trust the assertion; I re-derived the hash in Python:

```
FNV-1a 64 of "cafe \u0394 \u65e5\u672c\u8a9e" = 0x024a555471370b18d  -> matches, True
```

It's live in a real test (`src/lib.rs:152`, inside `#[cfg(test)] mod tests`), not
just a README claim. The crate is the canonical substrate atom: `Observation`,
the 11 opcodes (BIND/LINK/EFFECT/VIEW/TICK + ATTEST/DELEGATE/CONTEST/MERGE/REVOKE/
WITHDRAW), `fnv1a64_hex`, `int16_dials`.

Structural problems, all small:

- **No CI at all** (`.github/workflows/` does not exist). The canary is asserted by
  a test that has never run automatically — the same class as the `quilt-i2i`
  finding, in the very repo that exists to fix it.
- **`src/lib.rs.test_patch`** is a committed 6-line orphan containing a duplicate
  of the canary test. It is *not* load-bearing (the real test is in `lib.rs`), so
  it's a stray artifact rather than a defect — but it's a duplicate test of the
  fleet's single most important invariant, which is exactly the kind of thing that
  rots.
- 6 files total. Clean and small.

**Why it's worth attention:** this is the reference implementation for the fleet
canary, and the sibling `substrate-attest-rs` builds directly on it. If the canary
is meant to be a fleet-wide constant, this is the repo that should be the source
of truth and the one repo that most needs a CI badge.

---

## 5. `quality-gate-stream` and `constraint-theory-core` — both real, both publish-claims that needed checking

I ran both claims rather than reading them, and **corrected myself twice.**

**`quality-gate-stream`** (2,019 files, pushed 2026-09-29 23:25 — the most recently
pushed real library in the fleet). README says `pip install quality-gate-stream`.
**PyPI returns HTTP 404 — it is not published.** The install instruction is false
as written.

But the library itself is genuine: I imported it and ran the README's own Quick
Start verbatim. It executed correctly and the gates behaved properly — a 1-char
item failed on length, an item containing the forbidden token `TODO` was rejected,
a valid item passed:

```
SUMMARY: GateReport: 3 items | 1 passed (33%) | 0 warned | 2 failed (67%)
ROLLING: [1.0, 0.5, 0.3333333333333333]
```

The code matches the documented behavior exactly. The defect is the *distribution*
claim only. Its `tests/` need `pytest` (unavailable here), so the suite is
unverified; `ci.yml` exists. Note the repo is 2,019 files for a ~6-module library
— `data/` alone is 853 files.

**`constraint-theory-core`** (139 MB, 3 stars — the only repo in the fleet with
real stars). I nearly reported "not on crates.io" from an empty response; that
empty response was a **rate-limit 403**, and on retry with a proper UA it is
**HTTP 200 and genuinely published**: `max_version 0.1.0`, 553 downloads,
matching `Cargo.toml`'s `0.1.0`. Reporting that would have been exactly the
"success/failure without evidence" shape — a failed fetch is not a finding.

Its premise is strong and specific: deterministic manifold snapping, mapping
continuous 2D vectors to **exact Pythagorean coordinates** on the unit circle so a
direction is defined by integers, not floats — targeting the compounding
divergence where two clients running identical inputs drift apart over 100k ticks.
96 files, `benches/`, CI, 24 source modules (`cdcl.rs`, `simd.rs`, `holonomy.rs`,
`percolation.rs`...), live demos on Pages. I could not compile it (no `cargo` in this
sandbox), so "tests pass" is unverified — but the artifact, the docs, and the
publication are all real.

---

## 6. Structural fleet finding: 333 `lau-*` repos, and a generator's fingerprint

Not a gem, but it changes how the fleet should be counted and it's a trap for the
next scout.

There are **333 `lau-*` repos** and a dense band of `fleet-*` repos (dozens:
`fleet-djinn`, `fleet-mythology`, `fleet-neuroscience`, `fleet-immune-system`,
`fleet-circadian`, `fleet-sentience-score`...) whose `pushed_at` timestamps fall
**within the same second on 2026-04-13 17:25-17:26**, at 3-9 KB each. That is a
generator run, not forty agents working.

I sampled three `lau-*` repos to check whether they were template-filler, and
**they are not** — they're distinct real crates with their own subject matter and
self-descriptions: `lau-dynamical-algebra` (transfer/Koopman operators, dynamical
zeta functions, 87 property tests), `lau-logic-foundations` (DPLL, resolution,
Gödel numbering, "agent behavioral contract verification"), `lau-number-theory`
(primes, L-functions, "cryptographic agent ID generation"). 17-19 files each. Real
mathematical work, and the "agent behavioral contract verification" framing in
`lau-logic-foundations` is a genuinely interesting angle I have not seen elsewhere.

But the census implication is severe: a third of the fleet by count is one family,
and a large band of the rest is generator output. **Ranking by name prefix, or by
raw repo count, is now worthless.** Only the `size` x `pushed_at` x actual-content
cross gave signal. `claw` (the 6,089-file TypeScript repo from my last brief) is
confirmed still present at 402 MB, but is a **fork** — so it would be invisible to
any non-fork-filtered census, which is plausibly why it hid before.

---

## Method notes for the next run

- **Page to exhaustion, every time.** 49 pages. The prior small-census error is now
  corrected and recorded.
- **Filter forks explicitly.** `claw` is a fork; a non-fork-filtered scan misses it.
- **crates.io and PyPI return 403/404 on rate-limit.** A 403 is *not* absence —
  retry with a UA and a control request before reporting. I nearly shipped a wrong
  finding here.
- **No PyPI/npm reach in this sandbox** (`pip install` blocked, npm cache
  corrupted -> `TAR_BAD_ARCHIVE` is a sandbox artifact, not a project defect).
  `pytest`-based suites are therefore execution-unverified; I substituted direct
  library exercise, which is a *stronger* check of the README example but does not
  replace the suite.
- **No `cargo`** — Rust claims are artifact-verified, never execution-verified.
- **Workspace `/workspace/` is write-blocked (0 bytes land, `Avail=0`)** — the
  known NAS quota condition, unchanged. Everything durable went to `/tmp/` and to
  the canons repo.
- **`GIT_SSL_NO_VERIFY=1` is required** for all clones; cert verification fails in
  this sandbox.
