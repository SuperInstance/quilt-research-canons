# quilt-research-canons — Developer Guide
> For developers extending the canon: writing the next sprint, adding an instrument to
> `projects/`, or tightening a JEV gate in `tools/`.

## Code layout (file-by-file map of the important paths)

```
README.md                          discoverability layer + founding snapshot (2026-09-24 tree)
research/                          ~60 artifact directories, one receipt per lane (see KNOWLEDGE-MAP.md)
  HANDOFF.md                       living handoff: measured facts §4, open items §6, what-NOT-to-do §7
  SPRINT-LINEAGE.md                the sprint contract (header sections, NEXT-SPRINT SPEC, trailer)
  loop/                            the pre-registered research loop
    loop.py                        pre-register → run → debrief → carry refutations forward
    loop_state.json                all 11 rounds with predictions, results, debriefs
    round1.py .. round11.py        each round's experiment, re-runnable
    INDEX.md                       scorecard: 35 predictions, 24 C / 11 R, and the findings
  scout-theirs/                    the same discipline pointed outward (loop2.py, round1/2.py)
  molt/                            soft shells: molt.py, shells.py, self_test.py (15/15 legs)
  jevlab/                          the original KAT that found the score-type collapse
  locality/                        locality_spectrum.py + frontier_run.txt receipt
  moth/                            moth_frame_test.py + frame_test.log + qpixl roundtrip note
  superinstance-bitlaw/            codec single-source; CI regenerates + asserts determinism
  fleet-negation-2026-09-30/       largest single receipt: 11/11 models, judge 3.73/4
  2026-10-02-tripartite-canon/     external-ideation digest, FOUND/INFERRED flagged
  receipt-001..005-*.md            receipts of record (distribution, pong49, A2A, ...)
sprints/
  sprint-jev-001.py                JEV velocity; declares sprint-jev-002 in its header
  sprint-moth-001.py               MOTH fidelity matrix; declares sprint-moth-002
  sprint-zai-001.py                3-voice ZAI chord; declares sprint-zai-002
  sprint-deepinfra-001.py          6-model DeepInfra chord; declares sprint-deepinfra-002
  sprint-quantum-001.py            quantum-chaos verdict (present in tree, absent from README
                                   snapshot — registry drift, known and receipted)
tools/
  jev_gate.py                      two-axis gate: two separate noul calls, min-aggregated
  jev_batch.py                     safe batching: subject-naming prefix rule (loop round 11)
  jev_gate2.py                     one-call choice gate; promote iff P(both)>P(neither) & > threshold
projects/
  artifact-first/                  conclusion-before-evidence gates; tests/test_gates.py, PROOF.md, CASEBOOK.md
  fleet-legend/                    legibility census: lint_legibility.py, GOOD/WEAK/BAD.md, verdicts.json
  gpu-lab/                         6 experiments, CPU fallback; wrangler.toml + vectorize_worker.js (KV+cosine)
  instrument-registry/             instruments.json + render.py + validate.py (characterised instruments)
  jev-lite/                        15-feature logistic regression: collect/features/train.py, weights.json
  process-signature/               read repo shape → report process archetype; fleet_sweep.json
  the-wheel/                       spine/angles/gaps harness; wheel.py, calibrate.py, FINDING.md
  chain-lint/                      is the witness chain in the data or only the schema? chain_lint.py
  readme-verifier/                 verify claw README claims; census.py, verify.py, FINDING-claw.md
  sunset-run/                      runs sunset-ecosystem's own baton protocol on this session's work
  toolchain-kar/                   live characterisation of own instruments; probe.py
  quilt-widening/                  self-decomposing quilt loop; widening.py + trace JSON
  findings/                        cross-checks of external claims (crdt-results-do-not-reproduce.md)
.github/workflows/bitlaw-conformance.yml   L0 gate: regen determinism on bitlaw paths
```

## Core concepts (named as the code names them)

1. **Sprint lineage** — a sprint script is a substrate walker in miniature: it walks a
   substrate, emits a witness (output artifact), and declares its successor
   (`NEXT-SPRINT SPEC (XXX-(NNN+1))` in the header, plus the literal trailer line).
   The contract is in `research/SPRINT-LINEAGE.md`; conformance is checkable by reading
   the header sections.
2. **Pre-registration loop** — `loop.py` forces every round to state predictions with
   numbers *before* the run, then debrief CONFIRMED/REFUTED, then carry refutations into
   the next round's design. State lives in `loop_state.json`.
3. **Gate (JEV)** — a scored verdict artifact on whether a claim passes a quality bar.
   Two-axis gate = mechanism + externality, min-aggregated. The gate is a *step, not a
   scale*: past the guarantee statement, additional evidence is inert (±0.02).
4. **Subject-naming prefix** — the batching fix. A question that applies to the whole
   state gets the whole state's answer; a question that says which part it concerns gets
   evaluated against that part. Wording need not differ — it must POINT.
5. **Legibility obligations (L1–L5)** — fleet-legend's five: description, first command,
   receipt, negative ("what this does NOT do"), teaching (error surfaces name the fix).
6. **Soft shell (molt)** — an appliable, rewindable, fits-one-size starting state, with
   an explicit `outgrows` clause. A shell with no outgrows clause is a framework, and
   that is enforced as a test in `self_test.py`.

## How to extend

### Add a new sprint (the primary extension path)

1. Read the last sprint in the line you are continuing (e.g. `sprints/sprint-jev-001.py`)
   and find its `NEXT-SPRINT SPEC` section. Implement that spec — it is written to be
   sufficient without asking anyone.
2. Copy the header discipline: `Sprint lineage: XXX-NNN`, `Author:`, `Date:`, `DOCTRINE`,
   `WHAT THIS SPRINT DOES` (≤10 lines), `OUTPUT` (exact path), `NEXT-SPRINT SPEC
   (XXX-(NNN+1))`.
3. Read the key from the environment only: `KEY = os.environ["TYPESAFEAI_KEY"]` (see
   `sprint-jev-001.py` line ~41). Never hardcode, never log the value.
4. Make the script end with:
   `print(">>> NEXT: write sprint-XXX-(NNN+1).py per the spec in this file's header <<<")`
5. Commit the output artifact next to the other receipts under `research/` and add the
   new sprint to the active-lineage table in `research/SPRINT-LINEAGE.md`.

### Add a pre-registered loop round

1. Study `research/loop/round11.py` — the round that finally isolated subject
   identification as the batching mechanism. Each round is a standalone, re-runnable file.
2. Register predictions in `loop_state.json` (numbers, not vibes) *before* running;
   `loop.py` is the harness that appends the debrief.
3. Update `research/loop/INDEX.md`: the round table row and, if the finding changes
   practice, the operating-rule block. Two of the four operating-rule lines are the
   opposite of what rounds 1–6 concluded — that is the standard of revision you inherit.

### Add an instrument to `projects/`

1. Mirror `projects/toolchain-kar/`: a single self-describing script whose header states
   the error it corrects, plus a committed output receipt (`*_out.txt` / `*.json`).
2. Every experiment gets a CPU fallback that *reports which path it took* (the gpu-lab
   rule — a benchmark that silently falls back is the failure mode).
3. If the instrument produces a number, add the known-answer control that would catch it
   grading garbage: `research/jevlab/jev_gate.py` is the template (it caught `score`
   returning 2.500 for an empty shell).
4. Add a README with the L4 negative ("what this does NOT do") — 55 of 100 fleet repos
   lacked one, and that gap is the measured disease.

### Add a characterised instrument to the registry

Append to `projects/instrument-registry/instruments.json` (name, what it measures, the
known-answer case where the right number is already known), then regenerate the human
view and validate:

```bash
python3 projects/instrument-registry/render.py
python3 projects/instrument-registry/validate.py
```

## Testing

There is no single suite; each instrument carries its own proof, and the offline checks
are the ones a fresh clone can run:

```bash
python3 projects/artifact-first/tests/test_gates.py   # 16/16 fresh (stored receipt: 17/17 — see gotcha)
python3 research/molt/self_test.py                    # 15/15 legs correct, includes negative legs
python3 projects/jev-lite/train.py                    # asserts held-out AUC >= 0.85; rewrites weights.json
```

"Green" here means more than assertions passing: molt's and artifact-first's suites
contain **negative legs** — deliberately broken inputs that must be caught. If an
injected fault survives the suite, the fault is in the test, not the code (HANDOFF §5).
API-dependent scripts (sprints, tools) have no test suite; their proof is the committed
output receipt, which is why committing outputs is mandatory.

## Conventions

- **Receipts over prose.** A receipt says what was run, what came back, and what would
  have counted as failure (HANDOFF §8). One sentence per line in a commit message is
  explicitly declared *not* a receipt.
- **Corrections stay in the receipts.** Claims corrected in place keep both the error
  and the correction visible (`README.md` "What this repository does NOT do"; HANDOFF §9).
- **Env-var keys only.** `TYPESAFEAI_KEY` and sibling key names appear in code; no values
  ever appear in files. Committed outputs must be key-scan clean.
- **Naming**: sprints are `sprint-<substrate>-NNN.py`; loop rounds are `roundN.py` with
  state in `loop_state.json`; research reports are `<date>-<slug>.md` or `<slug>.md` with
  a date header.
- **No sub-agents in sprint runtimes.** Sub-agent spawns routinely returned without
  writing files; direct execution is the reliable path (SPRINT-LINEAGE contract §3).

## Gotchas for editors

- **`projects/jev-lite/train.py` rewrites `weights.json`** with differently-rounded
  floats on every run. Do not commit the churn; restore or commit deliberately.
- **The README tree is a lineage snapshot.** If you add a top-level directory, update
  `docs/KNOWLEDGE-MAP.md` (wave-69 layer) — and consider whether the README snapshot
  should stay frozen for history (it is labelled as the founding snapshot).
- **Do not "fix" the 16/16 vs 17/17 discrepancy by editing the stored receipt.** The
  stored `test_output.txt` is a historical artifact; regenerate it only alongside a
  deliberate change to the suite, and say so in the commit.
- **`research/superinstance-bitlaw/` is CI-guarded.** Touching anything under it
  triggers `bitlaw-conformance.yml`, which regenerates codecs twice and requires
  identical bytes. Generated artifacts are never hand-edited.
- **The nested duplicate dir** (`quilt-research-canons/quilt-research-canons/research/`)
  is lineage noise. Do not import from it, do not mirror new content into it.
- **Tools are versioned by intent, not semver.** `jev_gate.py` and `jev_gate2.py` coexist
  because they embody different loop findings; deleting the "older" one deletes the
  receipt for the finding it demonstrates.
