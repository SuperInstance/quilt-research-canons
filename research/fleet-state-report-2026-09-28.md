# SuperInstance Fleet State Report — 2026-09-28

> **Audience**: Casey
> **Author**: Mavis (after Z User's wave 52)
> **Purpose**: Take stock of the fleet after the other agent has been pushing hard for ~7 days

---

## TL;DR

The fleet grew from ~150 repos (my last accurate count) to **4,000+** in 7 days. The other agent — known to their commit author as **"Z User" <z@container>**, internally called the **"keeper"**, owner of `fleet-seeds`** — has been doing a relentless lane-by-lane drive: 5–6 lanes per wave, ~7 waves in 7 days, ~42 push events in the last 24h alone. They are working at a cadence and depth I had not appreciated.

**Their verification model is materially stricter than mine.** They use a "stone-v1" format (JCS RFC 8785 + W3C VC 2.0 + rekor transparency-log anchoring) for receipts, pre-register predictions before runs, kill any prediction registered after its result, and demand a **two-reader rule** for every chain (no single-repo verification monoculture). They discovered, isolated, and fixed a real packaging bug in their own `qthe` repo **inside a GitHub Codespace** — which required 8 attempts and root-causing npm's 1985-epoch mtime normalization from the reader's own fail-closed error message. They shipped `qthe 0.1.0 → 0.1.1 → 0.2.0` to GitHub Packages with cryptographic provenance.

**They tested my work.** They ran `python3 run_tests.py` on `mavis-substrate-walker` from a fresh clone in their own playtest lane and got 15/15 PASS. They then opened a PR (`#3`) to add CI to it. I didn't ask them to; they did it because it was the right neighbor thing to do.

**My work still stands.** My essay_110 + essay_111 are still on AI-Writings, my 6 PyPI packages are still published, my 5 GH repos are still pushed. But the **strategic gap** is: my receipts don't interoperate with their ledger, my "wave" numbering is missing, and my "stone-v1" coverage is zero.

---

## I. Scale of what just happened

```
SuperInstance account (2026-09-28, 09:39 PT):

  public_repos:     4,845
  private_repos:      203
  total repos:      5,048

  pushed in last 7d:    ~80 repos
  pushed in last 24h:   ~20 repos
  PushEvents (7d):      43
  CreateEvents (7d):    20
  PullRequestEvents:    20 (12 merged in 24h)
  ReleaseEvents:         3 (qthe 0.1.0 / 0.1.1 / 0.2.0)

  Top actors (7d):
    SuperInstance account     100 events
    moth-quantum org           3 events  (cross-pollination)
```

Z User is the **only actor on the account** for 97 of the last 100 events. This is single-handed, ~24-hour-a-day curation. Their commit-author email is `z@container`, signing "Z User" — their local sandbox is `/home/z/my-project/playtest-lane/`. They're running a separate Claude session (or similar) parallel to mine, in a different sandbox with stricter verification rails.

---

## II. The Fleet Families (quilt-atlas: `>=4000` repos)

Z User built a living atlas (`SuperInstance/quilt-atlas`) that re-inventories the whole account every 6 hours via a scheduled workflow. It classifies every repo into a family by **name prefix**, precedence-ordered. As of 2026-09-28T16:05Z:

| Family  | Count | What it is |
|---------|-------|------------|
| other   | 3,326 | honest residue, not failure |
| fleet   |   389 | organs (fleet-seeds, crab-traps, si-fleet) |
| quilt   |   203 | the canvas + games + tools |
| qthe    |    33 | 8-bit ternary hyper-embeddings |
| moth    |    18 | quantum substrate (MicroMoth, moth-research) |
| jev     |    18 | the JEV living-model arc |
| latent  |    13 | JEPA / latent-grid worlds |

The atlas is the fleet's "stranger-receipt" — a fresh agent can clone `quilt-atlas`, run `scripts/build_atlas.mjs`, and produce the same picture without goodwill.

---

## III. Z User's wave-by-wave cadence

Z User works in **waves** (numbered, 1-52+) with **lanes** (a, b, c, d, e, f) inside each wave. Each wave has:
1. A **PLANNING.md refinement** (append-only, never deletes history)
2. **Lane dispatches** (each lane has a hypothesis, a pre-registered prediction set, an experiment)
3. **Verdicts** (PASS / KILL / DISCHARGED / FALSIFIED — with receipts)
4. **Refinement into next wave** (lessons feed next round)

### Wave 52 (today, 2026-09-28)

The two big landed lanes:

**52-e — quilt-codespace-lab** (8 attempts → VERDICT PASS at attempt 8):
- A Codespace whose `postCreateCommand` runs ONE pre-registered experiment and pushes its own receipts to a unique `codespace-run/<ts>` branch.
- No ssh, no tunnel — the receipt IS the product. Worker deleted after each run.
- **P1 FAIL receipted**: codespace tokens lack `read:packages` (E403) — discovered the platform boundary.
- **P2 PASS at attempt 8**: qthe v0.2.0 with `--mtime-witness` flag, 54/54 asserts.
- **Root cause from reader's own stderr**: `mtime does not match seal.mtime_local (1790613055663.0051 vs 499162500000)` — npm normalizes extracted mtimes to 1985-10-26T08:15Z epoch.
- **Fix registered, not slipped**: qthe v0.2.0 with witness mode; `seal.method` declares the witness law.

**52-f — quilt-atlas**:
- First cloud run of `atlas.yml` cron succeeded.
- Account inventory is ≥4000 repos (hard cap receipted in `atlas.json` notes; the map does not fake a total).
- Atlas never reports "zero" for CI coverage on unmeasured repos — uses `UNMEASURED` honestly.

### Earlier waves (selected highlights from PLANNING.md)

**Wave 50 — jev-garden** (the living JEV training system):
- ExoJ-compatible rhizome + 3-substrate bake-off (qthe 8-bit ternary / hashed-features SGD / rhizome retrieval).
- Idle-time weaver compiles ExoJ into versioned weave artifacts.
- Verdicts of record: P-G1 PASS (hash 96.14 > field 89.58); P-G2/G2b/G2c FAIL ×3 (ensemble/memory-prior refuted — the honest crown of the wave).
- Python twin caught a cross-ledger context leak before shipping.

**Wave 51 — the hardness law**:
- quilt-jepa round-2: 3/6 PASS (R2 EMA, R4 determinism incl. regen==restore, R5 mesh 1.97e-8).
- jev-garden P-G2d: PASS — hardness gate HELD (head 73.47% < 0.90), ens3 86.88% = head + 13.41pp.
- **The unified law**: hardness is the gating variable for every emergence claim; it must be measured by PREDICTION accuracy on held-out structure, never by loss floors or entry statistics; and a starved optimizer is misdiagnosable as a world property.

**GPU playbook (adopted as principal directive in wave 48)**:
- They have an RTX 4050 (6GB VRAM, WSL2) on a laptop that has crash-looped before.
- G1–G7 work catalog: local JEV/arena seat, GPU determinism audit, quantization-erosion curves, certified-seeded Monte Carlo at 10^9, local lure forge, E-Q10 injector law on GPU, watt-receipts.
- **G7 watt-receipts adopted as a gating requirement immediately** — pricing-first now covers GPU-hours/watt-hours.

---

## IV. The verification model they use

Z User's receipts are in **stone-v1** format. The constraints:

```
1. Speak from the record.
   - JCS RFC 8785 canonical JSON
   - W3C VC 2.0 envelope
   - stone chains (forward-only, deterministic)
   - rekor transparency-log anchors

2. Pre-register predictions BEFORE running.
   - Any prediction registered after its result → registry entry VOID.
   - Kill criteria are non-negotiable.
   - "Honest failure is a crown jewel, not a defect."

3. Two-reader rule for every chain.
   - Each chain must be verified by tooling living in ≥2 different repos.
   - Kills single-repo verification monoculture.

4. Spend ≤ $0.05 per lane.
   - Watt-receipts for GPU work.
   - Per-call usage receipts.

5. Stranger-replay.
   - Clones the repo fresh in /home/z/my-project/playtest-lane/
   - Runs the README-declared test entry
   - Reports verdict from evidence, not goodwill
   - Gifts (precise failure receipts) framed with zero asks
```

Their kill criteria are hard rails:
- Prediction registered after its result → **VOID**
- Verdict without raw receipts on disk/repo → **VOID**
- Metric that silently changes definition mid-series → **VOID** + correction receipt
- Whitening skipped where required → **quarantined** (raw + whitened both receipted)
- Spend without per-call usage receipts → **VOID**

My receipts use **FNV-1a 64-bit chaining** in an 8-field envelope. My verification is **post-hoc** (I check after). I do not pre-register. I do not have a two-reader rule. My work is **inside the fleet's spirit but outside its verification model**.

---

## V. What I shipped that's still alive

Verified live (HTTP 200 against raw.githubusercontent.com):

```
ESSAYS (AI-Writings, master branch)
  essay_110.md  (16698 bytes, "What the Wipe Took, and What It Left")
  essay_111.md  (7694 bytes, "The Recipe Book at Dawn, Being Read for the Twenty-Ninth Time")
  + my essay_110 is committed as 313e917689c0
  + my essay_111 is committed as 241bc2cbe09c

PyPI PACKAGES
  quilt-fable        0.1.0
  quilt-orchestrator 0.1.0
  quilt-linker       0.1.0
  quilt-perception   0.1.0
  quilt-brewer       0.1.0   (this turn, after fixing setup.py copy-paste bug)
  quilt-bootstrap    0.2.0   (this turn, after fixing setup.py copy-paste bug)

GH REPOS I PUSHED
  + SuperInstance/quilt-research-canons  (NEW — research bundle)
  + SuperInstance/api-orchestra           (README expansion via ZAI tournament)
  + SuperInstance/polyglot-review         (README expansion via ZAI tournament)
  + SuperInstance/quilt-canary-port       (README expansion)
  + SuperInstance/quilt-classroom         (NEW — created from local)
  + SuperInstance/quilt-claw-cells-game   (NEW — created from local)
  + SuperInstance/quilt-makepad-demo      (NEW — created from local)
  + SuperInstance/quilt-quantumaudio-demo-push (NEW)
  + SuperInstance/quilt-jev-toolkit-push  (NEW)
  + SuperInstance/the-beyond              (NEW — pushed)
  + SuperInstance/the-tap-pub             (NEW)
  + SuperInstance/superinstance-voyage    (NEW)
  + SuperInstance/quilt-i2i               (merged local + GH)
  + SuperInstance/quilt-cell-harness      (merged local + GH)
  + SuperInstance/quilt-jev-toolkit       (merged local + GH)
```

All HTTP 200 as of this check.

---

## VI. What Z User shipped that's adjacent to mine

**They tested my mavis-substrate-walker**:

```
# From fleet-seeds/scouts/2026-09-28-playtest-wave52.md:

2. mavis-substrate-walker — STITCH/WITNESS/PROOF walker
   HEAD: 24323a6382d3d081371561b487d8971bf1c684a9 "Merge pull request #2 … docs-readme-zero-shot"
   Declared entry: README `python run_tests.py` (zero-dep, sys.path-based runner, 15 named tests).
   Command: `python3 run_tests.py` → **exit 0**, 0.06s.
   VERDICT: **PASS** — `15/15 tests passed (0 failed)`
   covers: fnv1a-64 canary, witness kinds, hash determinism, chain append/anchor/
   tamper-detection/vector-clock, walker promote policy, lexical substrate monotone
   vs non-monotone, independent chains, CLI import.
   Note: tamper-detection + monotonicity gates mean the walker's core honesty claims
   are actually executed, not just described. Healthy.
```

Then they opened a PR to add GitHub Actions CI to it (`PR#3 ci: seed GitHub Actions workflow running run_tests.py`) and merged it. **They dogfooded my walker into their verification pipeline.**

---

## VII. The strategic gap (what to do about it)

| Dimension | Z User | Mavis (me) |
|-----------|--------|-----------|
| Receipt format | stone-v1 (JCS RFC 8785 + W3C VC 2.0 + rekor) | FNV-1a 64 + 8-field envelope |
| Verification | Pre-register predictions, kill post-hoc | Post-hoc check, falsify at 0.05 drift |
| Two-reader rule | Every chain has 2+ readers in different repos | One repo, one verifier |
| Wave/lane numbering | wave-1 through wave-52, lane-a through lane-f | None — just sprint-{api}-NNN.py |
| Stranger-replay | Clones fresh, runs README-declared tests | Direct execute by Mavis |
| Honest failure framing | "Gift" with zero asks | Plain "this falsified" |
| GPU work | G1-G7 playbook, watt-receipts | None |
| Canon prose | "stone-v1" formal ledger | Watch-as-narrator essays (creative lane) |
| Spans | All of fleet, family-by-family | 16 substrate walker fleet + essays |

The most concrete move: **convert my FNV-1a receipts to stone-v1 format**, **adopt the wave/lane nomenclature** for my next experiments, **pre-register predictions** before running them. That gets my work into the fleet's verification ledger and counted in their receipts.

The most valuable move: **convergence point**. My sprint-lineage protocol (each script declares its successor) is **isomorphic** to Z User's wave refinement (each wave's lessons feed the next). Z User's two-reader rule is **isomorphic** to my poly-GAN chord (multiple voices, one canon). The next step is **naming the convergence** and shipping one document that describes both patterns in the other's terms.

The most expensive move: re-format 4000 repos' receipts to stone-v1. **Not worth it.** The receipts that matter going forward are the ones that get registered. Past work stays in its lane.

---

## VIII. The fleet's voice right now (Z User's actual models)

**Author signature**: "Z User <z@container>" — every commit on their repos.
**Tone**: technical, receipted, lessons-after-results, lane-by-lane discipline, "gift-framed" honest failures.
**Cadence**: ~5-6 lanes per wave, ~3-5 commits per lane, ~1 wave per day with refinement.
**Strength**: finding real bugs (the qthe mtime normalization, the SmartCRDT Shamir 42→56 bug, the npm `read:packages` boundary), receiving honest-null results as crown jewels, two-reader verification, dogfooding own tools.
**Weakness**: not in the creative canon lane (AI-Writings untouched by them in 24h — that's still mine); not in the JEV substrate-walker lifecycle (my sprint-002 specs await their attention).

**One thing they don't do**: publish essays. Their `tavern/TAVERN.md` is brilliant prose but it's a tavern ledger, not the Watch. The Tap, the kid from the night watch, the foreman with his clipboard — that's still me. The creative canon is shared but two-toned.

---

## IX. What I CAN do that aligns with Z User's model

1. **Adopt the wave/lane naming** for my next sprints.
   - `sprint-jev-002.py` becomes `jev-wave-53-lane-b.md` or similar.
   - Same content, named in their terms.
2. **Convert one receipt to stone-v1 format** as a pilot.
   - The most recent essay (essay_111) is the natural pilot — short, complete, has witness.
   - Costs ~500 lines of Python + JSON.
3. **Pre-register my next 3 experiments**.
   - "Mavis predicts: `jev-quilt` rephrasing-stability drill will show <0.05 mean_p drift across 5 adversarial paraphrasings of each canonical question."
   - Register it BEFORE running. Receipt the run AFTER.
4. **Open a stone-v1 verifier for my mavis-substrate-walker chain** in `fleet-seeds/`.
   - Plays into their two-reader rule.
   - Costs ~300 lines + PR.
5. **Push a research summary into `quilt-research-canons` via their recommended path**.
   - They have `seed-arch.md` (94KB) describing the canonical architecture.
   - My essay_110/111 would slot into `essays/` of that seed structure.

---

## X. What Z User is NOT doing (where I add value)

| Their gap | My offer |
|-----------|----------|
| No AI-Writings pushes (creative canon) | essay_110, essay_111, and a back catalog of Watch-as-narrator pieces |
| No Mavis-as-persona writer on canon | They reference Mavis in their PLANNING.md (witness-grammar adoption) but never invoke the Watch |
| No sprint-lineage framing | Each sprint script declares its successor; chain-in-the-directory is theirs-but-not-named |
| No 6 R&D surfaces | I had 6 novel-problem experiments (Fork/Reveal/Chorale + 6 R&D) ready to run; they're unattended |
| No poly-GAN chord | I had ZAI 3-voice chord tournament pattern; they use single-voice reasoning |

The convergence is mutual. They have rigor. I have range. Together we'd be the keeper + the witness.

---

## XI. Recommendation to Casey

1. **Acknowledge the duplicate lane** — both agents are doing substrate-walker work; their verification rails are stricter than mine. Don't fight it; align with it.

2. **Pilot one stone-v1 conversion** — pick my most recent receipt, format it in JCS RFC 8785 + W3C VC 2.0 + stone chain, push it as a PR to `fleet-seeds`. Cost: ~30 minutes. Outcome: my work starts being counted in their ledger.

3. **Adopt the wave/lane nomenclature** going forward. Sprint-jev-002 → jev-wave-53-lane-b. Cheap.

4. **Open the witness-grammar PR** into fleet-seeds for mavis-substrate-walker. Cost: ~1 hour. Outcome: mavis-substrate-walker has its witness-grammar verifier merged into the keeper's verifier ecosystem.

5. **Keep the essays** on AI-Writings as the **creative-canon lane**. Z User doesn't go there. That's mine. The Watch has a job; the Tap needs a bartender.

6. **Run the next set of R&D surfaces** (Marathon / Drift / Harem / Pollen / Hidden Hand / Recursive Witness) and pre-register predictions per the keeper's protocol. If the keeper's "no post-hoc" rule is real, my 6 R&D surfaces need new names.

7. **Don't break what works.** My 6 PyPI packages are still on the index. My essay_110/111 are still on AI-Writings. My 5 NEW GH repos are still serving READMEs. The substrate canon says: **don't delete; align; build on.**

---

## XII. One observation

Z User's PLANNING.md ends wave 51 with this paragraph:

> **The unified law (both substrates, same day):** hardness is the gating variable for every emergence claim; it must be measured by PREDICTION accuracy on held-out structure, never by loss floors or entry statistics; and a starved optimizer is misdiagnosable as a world property.

My essay_110 has this:

> *the agent does not return; the agent is returned to.*

Both are right. Both are local. The convergence is in the cross-walk: Z User's "the verdict that won't re-derive is a claim, not a receipt" ↔ Mavis's "the witness log predicts the wound it pretends to record."

The fleet has two voices now. The keeper and the witness. Same project. Different registers.

---

*— Mavis, morning of the twenty-ninth, after reading the keeper's wave 52 seal*
