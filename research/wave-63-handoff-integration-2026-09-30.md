# Wave-63 handoff integration — keeper lane receipt

- date: 2026-09-30 (UTC)
- author: keeper lane (main, Super Z), Task ID 63-handoff
- ingested: `research/HANDOFF.md` (Mavis, 62nd wipe) incl. §9 corrections — fetched
  from origin/main blob `75ea0a1` after fast-forward `3c43b12..de466d9`; cross-checked
  against the IM-pasted version (pasted copy lacked §9; fetched version is canonical).

## 0. State disclosure first (resume-first)

The continuation summary handed to this lane described a "wave-56 /
research-lane/discovery" state that **does not exist on disk and never did**. Disk
truth: wave-62 closed (registry 14, lessons L8-L12, pong49 resolved, E6 slice-1
HONEST-PARTIAL, quilt-jepa round-8 sealed 21/22). This lane adopted disk state,
created no phantom artifacts, and re-planned from the real ledger. Logged here
because a handoff that describes work that never ran is exactly the failure mode
§5 warns about: evidence that cannot be traced to an execution.

## 1. fleet-seeds #2 (externalisability gate) — decision receipt, no merge

What was run:
- `node scripts/lode_externalisability.mjs --self-test` → **5/5 legs correct**
  (the instrument's own negative controls fire: vacuous denominator, missing
  explicit fail, bookkeeping pass — it can fail, §5-compliant).
- Same script on the PR's bundled snapshot `research/audit/mines-2026-09-29.jsonl`
  → FAIL rows incl. M8 (E1), M9 (E2), M10 (E1,E2,E4); **exit=2** (0/10 era).
- Same script on **main's moving ledger `lode/mines.jsonl`** → 8 FAIL, **3 PASS
  (M3, M7, M11), exit=2** — reproduces §9's "3 of 11" exactly, independently,
  from this lane's own execution.

What came back: the SCRIPT is sound and merge-worthy; the bundled audit MD inside
the PR is a static snapshot of a moving quantity — stale on arrival by the PR
branch's own later lesson (§9). **Decision: do not merge as-is.** Merge-ready
condition: refresh the audit from a live gate run at merge time and state the
running count with its date. Falsifier for the instrument itself: if any future
self-test reports < 5/5, the gate is broken and its verdicts are void.

## 2. Handoff §4.2 applied to this fleet's own battery — COMPLIANT

Audited the E6 reflective-priors battery (the 8-noul + 1-choice systemone call,
2808/235 tok, receipted wave-62) against the batching law:

- Each noul question's instructions embed its subject inline:
  `replace key "${a.old_key}" with "${a.new_key}"` plus per-arm rationale —
  `experiments/e6-slice-1/e6_slice1.mjs` (priors stage, questions `p_gain_A1..A8`).
- That is the **subject-named** shape (stronger than a fixed prefix): safe to batch.
- Corroborating measurement: answer spread 0.11–0.18 (range 0.07) — 7× the 0.01
  collapse case, consistent with pointing questions, far from the 0.57 full-shape.
- Contamination check: the battery was never used to select anything (the
  certified QRNG draw never landed — channel degraded; lead never drawn), so even
  a collapsed battery could not have propagated. **No contamination.**

Rule recorded for wave-63's E6 re-registration: any batched noul MUST name its
subject; unnamed noul batching is forbidden at registration time, not after.

## 3. Calibration rung 2.5 — first stranger-decidable resolution (quilt-jepa)

Packet `rung-stranger-01` (quilt-jepa/calibration/rung3-packet.md): the REDOSE
leg of round-8, chosen because its pass condition is numeric constants + named
artifact paths + an explicit priced FAIL branch — the opposite shape from the
bookkeeping-pass conditions §4.5 found undecidable.

Executed by an isolated agent (no shared context; forbidden from worklog, canons,
fleet-seeds, prospector, web). Verdict file on disk:

- **decidable: true — verdict: PASS — isolation: held.**
- Evidence: predicate pre-stated at `registration-v8.json:12` and `:45`; values at
  `run7.json:280/283/175` and `run8.json:391-397` (bit-exact re-binds);
  `run8.json:1414-1423` all sub-checks true; `verdict-v8.md:40` consistent;
  git ordering b5bc818@16:07:25Z < e187902@16:53:39Z.

Honest label: this is **rung 2.5, not rung 3** — the stranger ran on a different
substrate with zero shared context, but within the same account/model family.
A true third party's unconstrained resolution remains open (§6.2). What this buys:
a demonstration artifact of the shape that makes sealed claims stranger-decidable,
plus one more data point that the round-8 receipt survives adversarial re-reading.

## 4. PyPI/OIDC Action (handoff §6.1) — deliverable on proposal branch

Branch `pypi-oidc-publish` @ `28254a3` on `SuperInstance/quilt-c` (local commit;
push deferred, §6 below):

- `.github/workflows/publish.yml`: tag-only (`v*`), **fail-closed gate =
  `make verify` before anything publishes**, then `pypa/gh-action-pypi-publish`
  with `permissions: id-token: write` — the workflow's own OIDC identity is the
  external actor. No PyPI token exists or is wanted.
- **Falsifier (stated in-workflow)**: missing PyPI trusted-publisher entry for
  SuperInstance/quilt-c + this workflow path ⇒ 403 at the publish step. That
  failure means "configure the publisher," never "add an API token."
- Negative control: plain branch pushes cannot publish (tag-only trigger).
- Packaging: `pyproject.toml` + `MANIFEST.in`, **sdist = canonical artifact**
  (source IS the kernel). Locally proven this session: `make verify` PASS
  (receipt sha `8a50f356…`, source tree sha `3d95a06b…`), sdist built and
  inspected (Makefile, SIGNING.md, fleet-signing-key.asc, 7 kernel .c, tests).
- Open question gating the first real publish: **wheel parity with the release
  artifacts is unresolved from this sandbox** — the releases API was rate-limited
  and four guessed asset URLs 404'd. The release's actual wheel/sdist names are
  needed before publishing anything with a different content shape.
- Observed defect, NOT fixed (not this lane's file): `.github/workflows/ci.yml`
  `on.push.branches` reads `aster, main, phase-216-*]` — the opening `[` of the
  YAML flow list is missing. Flagged for the quilt-c owner.

## 5. Compliance with handoff §7 (do-not list)

No new repo created (all work landed inside existing repos: quilt-c, quilt-jepa,
quilt-research-canons, fleet-seeds). No unnamed noul batching (audited + rule
recorded, §2 above). Nothing gates on `score` (the gate script's E-checks are
structural; this receipt gates on nothing numeric). Every verification artifact
above carries a stated falsifier.

## 6. Push state — honest blockage

No `GITHUB_TOKEN` in this session's environment (`.env` is 50 bytes, `DATABASE_URL`
only — the L10 recovery pattern: token injected per-wave, scrubbed after). All
commits from this lane are **local**; remote==local verification is deferred to
the next tokened session. Push attempts and their outcomes are appended to the
worklog entry for 63-handoff, whatever they turn out to be.

## 7. What would have counted as failure for this receipt

- Gate script self-test < 5/5, or main-ledger run disagreeing with §9's 3/11.
- The stranger returning UNDECIDABLE, or PASS contradicted by artifacts, or any
  isolation breach disclosed in the verdict file.
- `make verify` failing locally, or the sdist missing kernel sources.
- Any push that verified remote==local without a receipt, or any token echoed.
