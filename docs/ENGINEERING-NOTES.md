# quilt-research-canons — Engineering Notes
> For engineers operating, reviewing, or building on the canon and its instruments.

## Architecture

The repo is an artifact store with three producer layers and one index layer. There is
no service to operate; the "architecture" is the flow of evidence:

```
            ┌───────────────────────────────────────────────────────────┐
            │                      external substrates                  │
            │   Typesafe.ai /v1/systemone (JEV) · ZAI · DeepInfra ·     │
            │   Groq · Gemini · ElevenLabs · Cloudflare · MOTH          │
            └───────────────▲───────────────────────▲───────────────────┘
                            │ (env keys only)       │
     sprints/sprint-*-.py ──┘        tools/jev_*.py ─┘
        (NEXT-SPRINT SPEC chain)       (gate instruments)
                            │ output artifacts
                            ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │ research/  — one receipt per lane                                  │
   │   loop/ (pre-register→run→debrief, loop_state.json)                │
   │   scout-theirs/ (instruments pointed outward)                      │
   │   dated reports: fleet-negation, externalisability audit,          │
   │   claw audit, tripartite canon, jev-loop rounds, receipts 001-005  │
   └───────────────▲────────────────────────────────────────────────────┘
                   │ instruments built FROM findings
   ┌───────────────┴────────────────────────────────────────────────────┐
   │ projects/  — standalone toolkits, each with its own receipt        │
   │   artifact-first · fleet-legend · gpu-lab · instrument-registry ·  │
   │   jev-lite · process-signature · the-wheel · chain-lint · ...      │
   └───────────────▲────────────────────────────────────────────────────┘
                   │ regen determinism (CI)
        .github/workflows/bitlaw-conformance.yml → research/superinstance-bitlaw/
```

Data flow: an agent picks the newest sprint or HANDOFF open item, runs a script with
env-var credentials, commits the output artifact plus a dated report, and the next agent
reads the chain. The only always-on component is the CI L0 gate, which regenerates the
bitlaw codecs and asserts two runs produce identical bytes.

## Invariants

1. **The chain is the roadmap.** Every sprint declares its successor; the directory, not
   session memory, holds the plan. Enforced by the SPRINT-LINEAGE contract and checked
   by reading headers (the wave-64 decomposition lane smoke-tested 5/5 sprint scripts
   against the contract).
2. **Keys in env vars only.** All API-reading scripts fetch from `os.environ`
   (`TYPESAFEAI_KEY` in `tools/jev_batch.py`, `sprints/sprint-jev-001.py`). Enforced by
   code inspection and the fleet key-scan discipline; no committed artifact should carry
   a credential value.
3. **Pre-registration before measurement.** `loop.py` appends a debrief only to a round
   that registered predictions with numbers; `loop_state.json` is the enforcement
   surface — 11 rounds, 35 predictions, all debriefed.
4. **A gate must have a negative control exercising its own failure mode** (HANDOFF §5).
   Enforced in-repo by the `[PASS] NEGATIVE:` legs in `artifact-first/tests/test_gates.py`
   and `research/molt/self_test.py`.
5. **Regen determinism for bitlaw codecs.** Enforced by `.github/workflows/bitlaw-conformance.yml`
   on every push touching `research/superinstance-bitlaw/**`.
6. **Refutations are never deleted.** `loop_state.json` keeps all 11 refuted predictions;
   the operating-rule block in `loop/INDEX.md` records where a refutation reversed a rule.

## Failure modes & blast radius

- **Unnamed-subject noul batching** — silent data corruption of a measurement: N answers
  come back as one number with plausible-looking per-item values (spread 0.01). Blast
  radius: any batched evaluation. Containment: `tools/jev_batch.py` implements the prefix
  rule; `research/loop/INDEX.md` documents the numbers to compare against (0.01 vs 0.57).
- **`score`-type gating** — a constant generator (~2.500, confidence ~0.62) that fails
  open. Blast radius: any automated promotion decision using `score`. Containment: the
  KAT in `research/jevlab/jev_gate.py`; HANDOFF §4.4 and §7 ("do not use `score` to gate
  anything").
- **Tautology questions** — a bare guarantee question returns 0.98 against a description
  that merely restates the guarantee. Containment: two-axis or choice-distribution gates.
- **A suite that cannot fail** — eleven positive tests passed for the wrong reason when a
  route builder's guard was false on an empty list (routes permanently empty; nothing was
  ever posted). Containment: the negative-control discipline, stated in HANDOFF §5.
- **Prefix searches missing the biggest repo** — the claw census: 7,445 files, 9% of the
  account's code, invisible all day because searches were `quilt`-prefixed and the repo
  does not start with `quilt`. Containment: `research/claw-audit.md` +
  `projects/readme-verifier/`; the general lesson (search shape vs corpus shape) is in
  the wheel's stopword finding.
- **Stopword filters tuned to generic English** — in a corpus whose repos are named
  `quilt-*`, "cell"/"architecture"/"model" are content, not noise; filtering them made
  the matcher unable to see the answer (`projects/the-wheel/FINDING.md`).
- **Stale snapshots of moving quantities** — the externalisability figure 0/10 became
  3/11 within hours (HANDOFF §9). Treat every census number as of-its-date.

## Performance & cost envelope

Measured numbers from the loop receipts (all on Typesafe.ai `/v1/systemone`):

- Batch of 4 subject-named `noul` questions: **545 input tokens vs 1,344** for four
  separate calls — **2.5x cheaper**; wall-clock ~200 ms either way
  (`research/loop/INDEX.md` finding 4; `tools/jev_batch.py` header).
- Gate stability: same question × 6 calls, sd 0.005–0.011, zero threshold flips —
  repeat-calling buys almost nothing (`tools/jev_gate.py` header).
- Gate step: +0.690 on the single rung adding the guarantee statement; all later rungs
  ≤0.02 (`jev-gate-experiments-2026-09-29.md`).
- jev-lite training: offline, seconds, on a small corpus (`projects/jev-lite/corpus.json`);
  held-out AUC 1.000 on the fixed seed (20260930) at wave-69 re-run; asserts ≥ 0.85.
- Fleet legibility census: 100 repos fetched and scored by one scriptless prior-knowledge
  agent (`projects/fleet-legend/` numbers above); the triage referral scanned 243 repos /
  15,880 files in 162 s (docs/REFERRAL-fleet-triage-resolver.md — measured on the
  fleet-triage side, cited here).
- Estimates, not receipts: per-question cost of the `choice` gate in `jev_gate2.py` is
  one call per claim and was not separately token-metered in a committed receipt.

## Operations

- **Local**: Python 3 stdlib runs everything offline; API work needs `TYPESAFEAI_KEY`
  (and, for other sprints, their own env key names — ZAI, DeepInfra, Groq, Gemini,
  ElevenLabs, Cloudflare, MOTH). No `.env` is committed; no key value belongs in any file.
- **CI**: one workflow, `bitlaw-conformance.yml` — checkout, Python 3.12, Node 22,
  regenerate codecs, assert determinism. Everything else is receipt-on-commit, not CI.
- **Workers**: `projects/gpu-lab/` ships `wrangler.toml` + `vectorize_worker.js` — a KV-
  backed knowledge index with in-Worker cosine (Cloudflare Vectorize returns
  `unknown_content_type` 1005 on this account, so the worker says which backend is live
  at `/health`). `upload_index.py` fills the KV namespace; the wrangler KV id is a
  placeholder by design ("REPLACE_AFTER_running_upload_index.py").
- **Credentials model**: env-var names only; wave-67/68 established the purge and
  key-rotation discipline for the account (see `research/KEY-ROTATION-2026-10-04.md`
  for the rotation receipt format). Audit before pushing: the fleet key-scan.

## Design decisions & why

1. **Artifact store, not a service.** The value is the chain of dated receipts; a server
   would add an ops surface and subtract verifiability. Tradeoff: no query API — the
   discovery layer is grep + README pointers, which is why KNOWLEDGE-MAP.md exists.
2. **Two gate generations kept side by side.** `jev_gate.py` (two `noul` calls,
   min-aggregated) vs `jev_gate2.py` (one `choice` call, distribution rule). Keeping both
   preserves the receipt for the findings that distinguish them; the cost is that a
   newcomer must read two headers to know which to use — ONBOARDING says: use gate2.
3. **Corrections stay in receipts, errors stay visible.** HANDOFF §9 corrected its own
   §4.6 census without rewriting it. Tradeoff: readers can quote stale numbers; the
   mitigation is that every stale number is annotated in place.
4. **The loop refutes itself on purpose.** 11/35 refuted, and two refutations reversed
   the operating rules. Tradeoff: slower "progress", but the loop that only confirms
   cannot correct a belief (`loop/INDEX.md`).
5. **KV + in-Worker cosine instead of Vectorize.** Vectorize is broken on this account;
   rather than ship a binding that fails, the worker reports its real backend at
   `/health` and a gap-aware search endpoint returns the negative space (`/gaps`).
6. **Soft shells, not a framework.** `research/molt/` ships seven shells each with an
   `outgrows` clause, enforced by test — the anti-framework commitment is machine-checked
   (`research/molt/self_test.py`, 15/15).
