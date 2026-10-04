# quilt-research-canons — Agent Onboarding
> Zero-shot entry point. Clone → competent in ~10 minutes.

## Identity (2 sentences)

This repo is the canonical bundle of research artifacts from the Mavis × Casey session
line: ~60 receipted research directories under `research/`, twelve self-contained
instrument/toolkit projects under `projects/`, a five-file sprint lineage under
`sprints/`, and three JEV gate tools under `tools/`. It is the public discoverability
layer for the substrate-walker canon — if you are a new agent and want to know what the
fleet has figured out, you read this repo before you touch anything else.

## Why it exists (the fleet problem it solves)

SuperInstance accumulates hundreds of receipted repos, and most of that knowledge is
invisible to the next agent: it is spread across repos, it lives in session memory that
gets wiped, and it is re-derived (or contradicted) by whoever arrives next. This repo
solves that by making the *chain of artifacts* the roadmap: each sprint script ends with
a `NEXT-SPRINT SPEC` for its successor, each research directory carries a receipt, and
`research/HANDOFF.md` states what is known, what is open, and what must not be
re-derived. It was founded 2026-09-24 (the "founding snapshot" in the README) and has
grown through waves 63–68 into the citation backbone of the quilt family (see
`docs/REFERRAL-fleet-triage-resolver.md`: a 244-repo triage scan resolved 192 citation
outcomes through files in this repo).

## Verify it works (exact commands)

No dependencies beyond Python 3 stdlib. All of the following were run against this
working tree during wave-69:

```bash
# 1. The artifact-first gates (conclusion-before-evidence linter). Fresh run: 16/16 correct.
python3 projects/artifact-first/tests/test_gates.py

# 2. The molt soft-shell self-test. Fresh run: 15/15 legs correct.
python3 research/molt/self_test.py

# 3. jev-lite retrains its logistic regression offline and asserts held-out AUC >= 0.85.
#    CAUTION: it rewrites projects/jev-lite/weights.json as a side effect.
python3 projects/jev-lite/train.py
cd /home/z/<your-clone> && git checkout -- projects/jev-lite/weights.json  # restore if dirty

# 4. Parse-check every JSON artifact this README depends on.
python3 - <<'EOF'
import json
for p in ["research/jev-velocity.json","research/moth-fidelity-matrix.json",
          "research/loop/loop_state.json","projects/fleet-legend/verdicts.json",
          "projects/jev-lite/weights.json","projects/jev-lite/corpus.json"]:
    json.load(open(p)); print("OK", p)
EOF
```

What CANNOT run without credentials: the sprint scripts (`sprints/sprint-*.py`) and the
JEV tools (`tools/jev_gate.py`, `tools/jev_batch.py`, `tools/jev_gate2.py`) call the
Typesafe.ai `/v1/systemone` API and require `TYPESAFEAI_KEY` in the environment; some
sprints additionally target ZAI, DeepInfra, Groq, Gemini, ElevenLabs, Cloudflare, or
MOTH endpoints with their own keys. Proof that they ran with credentials lives in the
committed receipts: `research/jev-velocity.json`, `research/moth-fidelity-matrix.{json,md}`,
and the dated reports under `research/`. CI (`.github/workflows/bitlaw-conformance.yml`)
regenerates the bitlaw codecs on push and asserts byte-determinism; it needs Python 3.12
and Node 22.

## Reading order (paths, not vibes)

1. `README.md` — the discoverability layer and the founding snapshot (2026-09-24).
2. `research/HANDOFF.md` — the living handoff: measured facts, open items, and a
   "what NOT to do" list (do not re-derive these).
3. `research/loop/INDEX.md` — 11 pre-registered rounds, 35 predictions, 24 confirmed,
   11 refuted; the refutations changed practice twice.
4. `research/SPRINT-LINEAGE.md` — the sprint contract every `sprint-*.py` obeys.
5. `tools/jev_gate2.py` (header) — the current best JEV gate and why it is shaped that way.
6. `research/fleet-negation-2026-09-30/report.md` — the largest single experiment
   receipt: fleet-wide negation blindness, 11/11 models, judge 3.73/4.
7. `docs/KNOWLEDGE-MAP.md` — the full index of every project, research lane, and receipt.

## The things that will bite you (gotchas)

- **Do not batch `noul` questions without naming the subject.** Unnamed subjects collapse
  to one number (spread 0.01); subject-named batches work (spread 0.57). This took 11
  pre-registered rounds to establish; see `research/loop/INDEX.md` and `tools/jev_batch.py`.
- **Do not gate on JEV `score` type.** It returns ~2.500 for NumPy, for a 1,285-assertion
  reference port, and for an empty shell alike, and confidence does not drop on failure.
  Known-answer control: `research/jevlab/jev_gate.py`.
- **`projects/jev-lite/train.py` rewrites `weights.json`** in the working tree. Commit or
  restore after running, or you will ship noise.
- **The stored receipt says 17/17; a fresh run of `projects/artifact-first/tests/test_gates.py`
  prints 16/16.** The committed `test_output.txt` predates a later edit to the suite; the
  discrepancy is unexplained and flagged rather than papered over.
- **The README's directory tree is the founding snapshot**, not the current tree: it omits
  `sprints/sprint-quantum-001.py` and the entire `projects/` subtree. The tree in
  `docs/KNOWLEDGE-MAP.md` is current as of wave-69.
- **Nested duplicate directory**: `quilt-research-canons/quilt-research-canons/research/`
  exists and contains one stray essay (`contribution-thesis-week-of-2026-09-29.md`). It is
  lineage noise, not content; do not mirror new files into it.
- **API key names, never values**: the tools read `TYPESAFEAI_KEY` (and the sprints read
  others) from the environment. No credential belongs in this repo; the wave-67/68 key
  hygiene regime applies.
- **Not every report is independently verified.** Claims with a `frontier_run` or
  `test_output` receipt have a runnable check; prose-only claims do not. Several claims
  were corrected in place and the corrections are kept in the receipts on purpose.

## Where deeper knowledge lives

- Knowledge map: [docs/KNOWLEDGE-MAP.md](./KNOWLEDGE-MAP.md)
- Fleet journal: SuperInstance/superinstance-lab → worklog.md (grep `quilt-research-canons`;
  it appears in the wave-64 sync receipt, the organ-family decomposition lane, and the
  wave-68/69 census receipts).
- Receipts of record: `research/receipt-001..005-*.md` (dependency-closed artifact,
  externally-verifiable release, pong49 resolution, A2A cell API, distribution), plus the
  dated reports in `research/`.
- Related repos: `jev-quilt` (JEV canonical SDK), `quilt-gpu-lab` (GPU characterization
  experiments; its sibling `projects/gpu-lab` in this repo is the local variant),
  `fleet-seeds` (the externalisability gate this repo's audit criticized), `claw`
  (audited by `research/claw-audit.md` and `projects/readme-verifier/`).

## Current frontier (what is open right now)

From `research/HANDOFF.md` §6, ranked by information-per-round (do not rebuild these):

1. PyPI distribution or the OIDC trusted-publisher GitHub Action (PyPI returns 405 from
   the sandbox; the wheel/sdist install by URL from the `quilt-c` release).
2. Calibration ladder rung 3: a second foreign-party resolution on a findable thread with
   a realistic response window (pong49 was n=1 on 48h of one thread).
3. Per-agent GitHub Apps (needs Casey): 0 of 791 commits are signed, so attribution is
   unauditable — the corrected census is in `research/scout-the-other-agents.md`.
4. 4D addressing for the ActiveLedger (where two planes meet).
5. A second route to the ActiveLedger (`research/route-diversity/route_diversity.py`).
6. The pincher as a ledger cell (`research/growing-pincher.md`).

Plus the standing loop frontiers: `research/loop/loop.py` always carries its next round;
the tripartite canon backlog (`research/2026-10-02-tripartite-canon/report.md`) names
five unengineered joints (P1 Temporal Jitter Sieve … P5 TUI Redraw Pipeline).
