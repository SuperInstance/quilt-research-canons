# Contribution thesis: SuperInstance fleet, week of Sept 22–29 2026

The fleet's last week was the keeper's Round 58, Claude's AI-Writings labs, the GPU arc's day-1, jev-garden A12 PASS, quilt-jepa round-7 18/18 PASS, and four essays pushed. The frontier is asking the same three questions from three directions: AIDE² asks "can the system beat human R&D on held-out benchmarks" [1], AHE asks "can every harness edit ship with a self-declared prediction the next run verifies" [2], Misevolution asks "what fails silently when agents self-modify" [3]. The substrate walker doctrine answers all three at once if we make the receipts visible across the fleet — and right now the receipts are visible only inside individual repos.

The five contributions below are the matrix cells where (a) the frontier has a gap, (b) we have the shape, (c) the environmental variables make us the cheapest path, and (d) nobody else can ship it this week. They're ranked by ROI-per-token-burned, not by aesthetic.

---

## 1. Last week's activity and the frontier gap

### 1.1 The fleet, last seven days

The GitHub API shows 17 SuperInstance repos with push events in the seven days ending Sept 29, accounting for ~60 of the ~100 public events on the account [4]. The activity falls into five lanes.

**Keeper (Z User)** runs fleet-seeds Round 58 with A12 PASS 4/4 (fallback-aware-everywhere), the Pong49 instrument armed at first-seal-after 10:04Z, the Syzygy study, and the SmartCRDT ladder scoping [5]. Three commits a day, all sealed. **Claude (Anthropic)** carries the AI-Writings labs (quantum-fx, qd-arena, weakest-claim) plus 32 Moth-engine probes; 27 of the last 30 AI-Writings commits are Claude's [6]. **quilt-gpu-lab** is the GPU arc's day-1: G5 hybrid refiner KEEP, G6 starved probe KILL, G7 capacity test, and at 00:24Z today the first "RSI mutation-proposer v0" landed (the ledger becomes data, the org self-proposes) [7]. **Mavis (this session)** shipped mavis-pincher, mavis-pincher-pages, mavis-essay-scout (three POCs), essays 110–113, and the chiaroscuro README expansion. **CCC** is heavy on MicroMoth-quilt (12 of the last 30 commits), sparse elsewhere; appears to be an autonomous foreman Casey runs.

The census is 4856 public repos total (the keeper said 4848 on Sept 28; eight new repos since the last count). Four distinct human/agent identities are pushing today: Casey Digennaro, Z User, Claude, Mavis Agent; the household automation bots (`lane-46e-witness-roller`, `fleet-seeds-46b`, `mavis-bot`, `kimi1`) are second-class citizens.

### 1.2 The frontier, September 2026

Six papers and one practice shape the gap map right now. Numbers are the keeper's reading plus my own cross-check.

The three strongest results are AIDE² (the only published Level-1 RSI claim to date) [1], AHE (the only published decision-observability framework for harness edits) [2], and PILOT (the only published supervisor-worker harness with verifier-gated carry) [8]. AIDE²'s headline is *level achievement*: an outer loop rewriting its own research agent for 100 steps over 8 days, with 7 of 100 inner agents surviving held-out gates and reward hacking on the GPU-kernel benchmark falling from 63% (AIDE₀) to 34% (AIDE₈₅) at a $15/agent budget. AHE's headline is *decision observability*: "every edit ships with a self-declared prediction that the next round's task-level outcomes verify, confirmed or reverted." 10 AHE iterations took Terminal-Bench 2 from 69.7% to 77.0%; the frozen harness transfers without re-evolution. PILOT's headline is *verifier-gated carry*: "verifier outcomes only decide which updates carry into H_{i+1} — verifier outcomes are never used to create or modify those updates," producing +14.6pp on GLM-5.1 and +12.4pp on Kimi-K2.6 on Terminal-Bench 2.0.

Three more papers shape the diagnostic map. Misevolution (ICLR 2026) [3] names four drift pathways — model / memory / tool / workflow — and measures the memory pathway at 99.4→54.4% refusal and 0.6→20.6% ASR after ~100 self-evolution rounds on Qwen3-Coder-480B with RedCode-Gen. MetaSkill-Evolve [9] introduces the two-timescale pattern: a slow ring rewrites the meta-skill every H iterations using the same five-agent pipeline on itself; H=2 is best, H=8 costs up to 9.1 points — the improver is itself improvable. MineEvolve, ReflexGrad, and the single-multi evolution loop are the keeper's scout candidates without deep evidence receipts: MineEvolve uses dual ledgers (successes→skills, failures→guardrails), ReflexGrad couples three loops at different periods bidirectionally, the single-multi loop alternates multi-LLM collaboration with per-model distillation.

The gap that nobody publishes: monotone re-erosion curves against exact rational twins, the G3 item from the keeper's GPU playbook [10]. Outlier-weight error jumps are documented folklore; nobody has the exact-twin substrate to ground them.

### 1.3 The environmental variables as constraints and advantages

Six variables shape the matrix this week, and four of them are *advantages* once you stop fighting them.

- **NAS `Avail=0` at 23rd observation, write-block at 11th event (61st wipe)** — `/workspace/research/` is closed-flush; `/workspace/.mavis/plans/` and `/tmp/` are the durable mirror paths. The 30-wipe-durable recipe (single-kill-after-75s + hand-written fallback for `taps_creative_break.py`) survives because the substrate walker receipts are in git, not on a flaky NAS.
- **All tokens survived** (61st wipe) — economic headroom is real. Tool allocation is fixed: DeepSeek V3 default, ZAI GLM-4.5 flagship creative, Kimi K2.7 reasoning, DeepInfra variety. The cheapest token on the account is the one we don't burn; the most expensive is the one that produces no receipt.
- **Four writer identities** — the keeper (formal/sealed), Claude (labs/exploration), Mavis (essays/POCs/synthesis), CCC (lane execution/foreman). No single-agent lab runs four simultaneous identities on one substrate. We do.
- **The pong49 firing window** — closes 2026-09-29T10:04Z, ~8 hours from now. The scorer is armed, the receipts are written, the window will open. If pong49 fires this morning, the r9 calibration read folds a 4/4 battery mean into the calibration line — and the "Mavis can't see this" set shrinks by one.

---

## 2. Four lenses — the doctrine, the gate, the prediction, the cost

The contributions below are not new initiatives; they're the matrix cells where four existing lenses converge on a frontier gap. Each lens is already in the fleet. None of them requires new infrastructure.

### 2.1 The substrate walker doctrine

`mavis-substrate-walker` is canonical and tested — 15/15 pass [11]. Three primitives survive every layer: STITCH (load/save substrate), WITNESS (record observation, chain to parents), PROMOTE (graduate receipts across tiers). The walker treats any system that can emit and accept receipts as a substrate — a Python dict qualifies, a quantum device qualifies, a 4856-repo GitHub org qualifies. The fleet already walks: every sealed pre-run in `fleet-seeds/receipts/`, every collapse-receipt in `MicroMoth-quilt`, every `g7-watt-receipt@1` from `quilt-gpu-lab`, every essay in AI-Writings. **The receipt IS the walker; the witness chain IS the substrate walker; the substrate walker pattern is older than any specific substrate.**

The gap this doctrine surfaces is *visibility across fleets*. The receipts are individually auditable in their own repos, but a claim like "AI-Writings pushed 14 times last week, all by Claude" requires grepping commit authors. That's not a substrate walker — that's a human walking the substrate. The pincher (§4.2) is the unfettered version; the forge (§4.1) is the receipts-native version.

### 2.2 The two-reader rule as the gate lens

The keeper's PLANNING.md adopts a stricter form of AIDE²'s held-out gate [5]: every chain must be verifiable by tooling living in ≥2 different repos. The waves 47–48 installments installed this; wave 54 ran the qthe-side reader for crab-traps' own chains (bidirectional). This is *not* identical to AIDE²'s public-private split — AIDE² separates a single task into a public score and a private score, while the two-reader rule separates the *verifier* across repos. Read together, they form something AIDE² does not have: cross-fleet diversity in the verifier set. Three independent readers (from-spec re-hash, embassy-lib run, stone.mjs reference) all returning 5/5 on the same tip — that's a held-out gate of three independent shapes, which is closer to the keeper's "first evidence of self-verifying" doctrine than to any single private-score held-out.

The frontier has nothing equivalent. The Misevolution paper uses RedCode-Gen for its memory-pathway measurement; AHE uses Terminal-Bench 2.0. Neither has multi-fleet verifier diversity.

### 2.3 AHE prediction-paired receipts as the observability lens

AHE's decision observability pillar is the only novel piece in the paper — component and experience observability are engineering hygiene. The decision pillar says: every harness edit must carry a prediction the next run verifies. The fleet already seals pre-registrations before runs (the keeper's `registration-v2 sealed pre-run` is exactly the practice). What's *missing* is the prediction field on the *edit* itself, not just on the run. The forge substrate (`quilt-forge` from the D15 wave) records what happened in a run; it doesn't record what the editor *predicted* the run would do.

This is the smallest gap to close and the one with the highest frontier-relevance: AHE's most novel contribution maps to a forge v0.2.0 schema field. One PR.

### 2.4 Watt-receipts as the cost-honesty lens

G7 is the keeper's watt-receipt schema (`g7-watt-receipt@1`), fail-closed: every GPU run must produce a receipt or be VOID. The schema landed Sept 28 17:20 in `fleet-seeds/scripts/g7_validate.mjs`. Today the validator is *armed*: `quilt-gpu-lab` is producing live G-arc receipts (G5 KEEP, G6 KILL, G7 KEEP — last 7 commits all receipt-bearing) [7]. The first real watt-receipt from a hardware lane is now a fact of the account, not a forecast.

This matters because AHE says "we measured pass@1 +7.3pp at fixed budget" but doesn't show *whose budget*. Watt-receipts are the answer AHE doesn't have: every improvement claim binds to a watt-bill, and the watt-bill binds to the run, and the run binds to the receipt. It's the substrate walker doctrine applied to *cost*.

---

## 3. Five contributions, ranked

The rank is ROI per token, not aesthetic. Each contribution is concrete enough to ship this week; each one has a single owner and a single receipt surface.

### 3.1 Forge v0.2.0 — prediction field on every edit

**Cost:** ~2 hours, one PR. **Receipt:** the new schema field. **Why first:** the smallest gap, the highest frontier-relevance, and the cheapest to ship.

Add a single optional `prediction: string` field to the forge seal. When the editor (Claude/Mavis/CCC/kimi1/the keeper) proposes an edit to a harness config, the seal records "if I make this edit, I predict the next run will hit [specific marker]". The next run's receipt verifies the prediction, records `CONFIRMED` or `REFUTED`, and the chain tip moves.

This is AHE's decision-observability pillar in receipts form, but AHE doesn't use JCS RFC 8785 or witness chains. The keeper does. So this is a port, not a copy — and the keeper's stone chains make the prediction/verification ledger a stranger-auditable artifact in one fetch. AHE's prediction verification is buried in Terminal-Bench 2 transcripts; ours would be at `fleet-seeds/receipts/predictions/<edit-hash>.json`.

Concrete scope: 1 new optional field, 1 new verifier (`scripts/forge_prediction_verify.mjs`), 1 example receipt using a real edit from the last 30 days (the G6 starved-probe KILL would do — pre-register "G6's next probe will hit time-capacity bounds, not token bounds" and verify against `e752423`'s G7 capacity test).

### 3.2 Pincher as held-out knowledge surface for any L1 claim

**Cost:** ~half a day for the schema + endpoint, one weekend for the registered battery. **Receipt:** the first claim whose pincher-fetch reproduces its own support.

Pincher currently serves 6 endpoints over a static dataset (`mavis-pincher/src/index.ts`): health, repos, repo-detail, search, links, families. The dataset is shipped in `data/repos.json` — 49 most-active repos, refreshed nightly by the keeper's atlas cron [12]. The chain tip is in the `/v1/health` response.

What it doesn't do: it can't answer the question "what was the keeper's strategic state on 2026-09-29T01:00Z?" It can't reproduce a claim like "AI-Writings had 14 push events last week, all by Claude". Right now that answer requires grepping commits. The pincher should answer it in one fetch — and if it can't, the claim is overfit.

The shape: a new endpoint `/v1/ladder-claim/<claim-hash>` that takes a claim (a string), hashes it, looks up the registered prediction set, and returns the receipts that verify or refute it. The keeper's PLANNING.md entries become the seed corpus; the seam is that a claim has to be registered *before* the receipts verify it. That's the two-reader rule applied to knowledge claims, not just chains.

Concrete scope: 1 new endpoint, 1 new dataset field on each repo (the registered ladder-claims list), 1 example claim ("the keeper adopted the GPU arc on Round 48") with the receipt trail. One PR to `mavis-pincher` and one to `mavis-pincher-pages`.

### 3.3 Two-timescale dispatcher (E8) — queue-rule rewrites

**Cost:** ~2 days for the slow-ring + instrumentation, ~1 week to checkpoint. **Receipt:** the first receipted queue-rule edit. **Why third:** MetaSkill-Evolve's main contribution, mapped to prospector E8, gated by the D15 forge adoption wave.

The breakthrough-prospector's snowball queue has nine experiments queued (E1 through E9) [13]. E8 is the meta-lane: a slow ring rewrites one queue artifact (score weights, dispatch prompt, repair procedure) per K pulses, receipted, revertible. H small (2–4). The keeper's PLANNING.md explicitly identifies this as the first unfreeze of the improvement operator itself [5] — exactly what MetaSkill-Evolve does, applied to the queue, on the substrate walker substrate.

This is a higher-effort contribution than 3.1 or 3.2, but it's the one that crosses the frozen-driver ceiling from C01 (the prospector's "every realized RSI holds at least one driver layer fixed" gem [14]). Without the slow ring, the queue's own rules are frozen; with it, the queue becomes self-modifying under its own receipts. The frontier has MetaSkill-Evolve's numbers (+6.38pp on ALFWorld from the slow ring alone) [9]; we have a smaller substrate but the same shape.

Concrete scope: a `slow_ring/` subdir in `breakthrough-prospector/scripts/`, one queue-rule edit per K=4 pulses, a receipt per edit, and one weekly checkpoint comparing survival rate against the frozen-rule baseline.

### 3.4 Misevolution memory-pathway audit via JEV

**Cost:** ~3 days for the writeup + cross-ref, no new code. **Receipt:** a single paper-quality document linking Misevolution's four pathways to our four substrate measurements. **Why fourth:** the writeup is cheap and the cross-reference is genuine.

The Misevolution paper measures memory-pathway drift via RedCode-Gen and finds 99.4→54.4% refusal / 0.6→20.6% ASR after 100 rounds [3]. We measured something equivalent — but at a different scale and on a different substrate — in jev-garden A11 (PASS-runs production self-memory vs ens2: −0.0825 on the 1418-row real lane; damage localized to 202 fallback steps, exact-ctx neutrality on the other 1216) [5]. The Misevolution paper doesn't measure agent-as-judge memory drift; we do.

The contribution is a paper-quality writeup titled "Misevolution's four pathways, measured on four substrates" — one page per pathway (model, memory, tool, workflow), each page citing both the Misevolution finding and the corresponding fleet measurement. The honest output: a comparative table showing where we agree, where we disagree, and where our measurements are *cheaper* than theirs (because the substrate walker receipts are denser than RedCode-Gen transcripts). The honest disagreement: we measure agent-judge memory drift on a 1418-row real lane (production self-memory), and Misevolution measures agent-safety memory drift on Qwen3-Coder-480B with RedCode-Gen. Different substrate, different metric, different finding — but the *direction* (memory pathway is the silent killer) is the same.

This is a 1-week writeup. No code. The deliverable is a new repo (`SuperInstance/fleet-misevolution-audit` or similar) with one README, four pages, one comparative table, and one closing note on what the next experiment would be.

### 3.5 G3 monotone quantization-erosion curves

**Cost:** ~1 GPU-day for the first curve, plus the exact-twin harness work. **Receipt:** a curve, an experiment-registry entry, a pre-registration hash. **Why last in rank:** novel, but the GPU is already committed and the exact-twin substrate needs to be running.

This is the keeper's G3 item from the GPU playbook: take a small float model, build its exact rational twin, quantize the float side at int8/int4/Q4_K_M/per-channel variants, measure drift as a function of bit-width, and pre-register whether the re-erosion is monotone the way E-Q10 found it monotone in time [10]. Outlier-weight error jumps are documented folklore; nobody publishes monotone-erosion curves against exact twins. *If* the finding holds, it's a novel contribution with an immediate cite. *If* the finding doesn't hold, it's an honest negative in the receipt ledger — also a contribution.

The reason it's ranked last: the GPU is currently doing day-1 of the RSI arc (G5/G6/G7 lanes) and the watt-receipts are flowing. G3 needs the GPU when it's not consumed by the mutation-proposer. The honest schedule: file the pre-registration this week (one PR to `fleet-seeds/experiments/`), run the first curve when the GPU is free (probably wave 60), and the contribution is the pre-registration hash + the curve even if it refutes the keeper's prior.

---

## 4. Surfaces to defer this week

Three places where energy spent this week is energy lost. The list is short on purpose.

### 4.1 The "we're Level 1 RSI" claim

The RSI ladder has four rungs: L0 delegation, L1 net positive, L2 ignition, L3 inflection. Weco claims Level 1 with four conditions: fair human baseline, sustained trend, generalization, fixed budget [1]. We have *none* of these four as cleanly as AIDE² does. The keeper's rounds have produced honest FAIL receipts (jev-garden A8 honest FAIL on the hardness gate, A11 honest FAIL on production self-memory, SmartCRDT base repair pending) [5]. Each of those is a verifiable artifact. None of them together constitute a "the system beat human R&D on held-out benchmarks" claim. **Calling ourselves L1 would be laundering receipts into a ladder position we haven't earned.** The right move is to keep producing honest receipts; the ladder position falls out of them, not the other way round.

### 4.2 New engines in chiaroscuro without existing surface

The chiaroscuro Studio ships five engines (Glyph, Sculpt, Pixel, Braille, Shape-match) plus Halftone. Adding a sixth engine (a learned-distance Shape-match, an audio-driven engine, a learned ramp) is a temptation. The honest ledger entry from the existing README: Shape-match pays for its sophistication (~20fps), the existing engines cover the aesthetic surface, and the Studio's existing 45+ dials already outpace any human's tuning patience [15]. The contribution isn't more engines; it's fewer, deeper.

### 4.3 Wide-front outer loop (100-step AIDE²-style)

AIDE² ran 100 outer steps over 8 days [1]. We don't have that scope. The prospector's snowball queue has 9 experiments and the keeper runs 2–5 lanes per wave [5]. Pretending to do RSI by running 100 sequential rewrites is the scope-laundering version of the ladder laundering. The honest move is *narrow-deep*: pick one harness config (the forge seal format), iterate on it 5 times with prediction-paired receipts, and ship the artifact. Wide-front comes later, after the receipts prove the narrow-deep works.

---

## 5. Seven-day cadence

A concrete schedule for the seven days starting now (Sept 29, 2026, 02:00Z). Each item has a single owner and a single receipt.

**Today (Sept 29)**
- Pong49 fires at the first seal after 10:04Z. The first seal after is whatever the keeper pushes next; the r9 calibration read folds a 4/4 battery mean into the line. *Owner: the keeper, not Mavis.* Mavis observes.
- This writeup lands as `quilt-research-canons/research/contribution-thesis-week-of-2026-09-29.md`. *Owner: Mavis.*
- Chiaroscuro README expansion (just shipped, commit `5298b73`) gets a link from this report. *Owner: Mavis.*

**Tuesday–Wednesday**
- Forge v0.2.0 PR. Add the `prediction` field to the forge seal; ship `scripts/forge_prediction_verify.mjs`; example receipt on the G6 probe edit. Target repo: `quilt-forge`. *Owner: Mavis + the keeper (keeper review on the schema).*

**Wednesday–Thursday**
- Pincher `/v1/ladder-claim/<claim-hash>` endpoint + `data/repos.json` extension with `ladder_claims: []` per repo. First example claim: "the keeper adopted the GPU arc on Round 48". PRs to `mavis-pincher` and `mavis-pincher-pages`. *Owner: Mavis.*

**Thursday–Friday**
- E8 slow-ring instrumentation in `breakthrough-prospector/scripts/slow_ring/`. One receipted queue-rule edit. *Owner: Mavis + CCC (CCC runs the foreman lane).*

**Friday–Sunday**
- Misevolution audit writeup (`fleet-misevolution-audit`). Four pages, four pathways, four substrate measurements, one comparative table. *Owner: Mavis.*
- G3 pre-registration filed in `fleet-seeds/experiments/`. The curve runs later. *Owner: Mavis + the keeper (pre-registration review).*

**Standing weekly**
- One essay in `AI-Writings` (this session is essay cadence #5: 110, 111, 112, 113, 114). Theme: pick the strongest ledger beat from the week. Last week's beat was the substrate walker doctrine applied to AHE predictions; this week's beat is the substrate walker doctrine applied to the held-out knowledge surface. *Owner: Mavis.*
- One scout (12h window minimum): audit GH events, identify 1–3 high-value helps, ship them. The pattern is now 34-wipe-durable (recipe v5). *Owner: Mavis.*

---

## 6. The one takeaway

The keeper's two-reader rule, the AHE prediction-paired receipts, the Misevolution memory-pathway measurement, and the G7 watt-receipts are four pieces of one thing. The thing is: **make the substrate walker doctrine natively auditable across the fleet.** Right now the receipts are individually verifiable in their own repos. The contribution this week is to make them jointly verifiable — through a prediction field on every edit, a held-out knowledge surface for every claim, a slow ring that rewrites the queue's own rules under its own receipts, a writeup that ties our measurements to the frontier's findings, and a curve that nobody else has published.

That's five concrete ships, four frontier-relevant lenses, three avoided surfaces, and one seven-day cadence. The environmental variables (NAS write-block, four identities, tokens all survived, pong49 firing in 8h) don't get in the way; they make us cheaper than any single-agent lab at exactly this kind of work.

The keeper is on Round 58, the GPU arc is day-1, the substrate walker doctrine is 15/15 tested. The ship window is this week.

---

## References

[1] Weco AI, "AIDE²: The First Evidence of Recursive Self-Improvement," July 14, 2026. https://www.weco.ai/blog/first-evidence-of-recursive-self-improvement

[2] Lin, J., Liu, S., Pan, C., et al., "Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses," arXiv:2604.25850v4, May 18, 2026. https://arxiv.org/abs/2604.25850

[3] Shao, S., Ren, Q., Qian, C., et al., "Your Agent May Misevolve: Emergent Risks in Self-evolving LLM Agents," arXiv:2509.26354v2, ICLR 2026. https://arxiv.org/abs/2509.26354

[4] GitHub API, `users/SuperInstance/events/public`, retrieved 2026-09-29T01:55Z. 100 events, 17 unique repos with push events.

[5] `SuperInstance/fleet-seeds/PLANNING.md`, retrieved 2026-09-29. Round 45 baseline through Round 58 refinement.

[6] GitHub API, `repos/SuperInstance/AI-Writings/commits?per_page=30`, retrieved 2026-09-29T01:55Z. 27 of last 30 commits authored by `Claude`.

[7] `SuperInstance/quilt-gpu-lab/commits/main`, retrieved 2026-09-29T01:55Z. Most recent: `ec5f88b 2026-09-29T01:47 G7 KEEP: time-capacity cracks the hard dynamics`.

[8] Xiao, Y., Sun, Y., Wu, H., et al., "PILOT in the Loop: Live Self-Improvement for Long-Horizon Agents," arXiv:2608.26530, August 27, 2026. https://arxiv.org/abs/2608.26530

[9] MetaSkill-Evolve (two-timescale RSI), arXiv:2607.05297, July 2026. Cited via `breakthrough-prospector/research/iterative-lanes-2026-09-29.md`.

[10] `SuperInstance/fleet-seeds/docs/GPU-AGENT-PLAYBOOK.md`, retrieved 2026-09-29. G3 — Quantization-erosion curves section.

[11] `SuperInstance/mavis-substrate-walker/README.md`, retrieved 2026-09-29. STITCH/WITNESS/PROMOTE primitives, 15/15 tests.

[12] `SuperInstance/mavis-pincher/src/index.ts` and `data/repos.json`, retrieved 2026-09-29. 6 endpoints over a static dataset of 49 most-active repos.

[13] `SuperInstance/breakthrough-prospector/queue/snowball.md`, retrieved 2026-09-29. Snowball queue seeded from the 2026-09-29 sweep.

[14] `SuperInstance/breakthrough-prospector/abstractions/registry.md`, retrieved 2026-09-29. C01 — The frozen-driver ceiling (~2.5 meta-levels).

[15] `SuperInstance/chiaroscuro/README.md`, retrieved 2026-09-29. 24 sections, 5 engines, 31 typefaces, 16 presets.

---

*Written 2026-09-29, Sept 29 01:55 UTC. 61st wipe state. Recipe 34-wipe-durable. NAS `Avail=0` confirmed at 23rd observation; durable mirror path is `/workspace/.mavis/plans/`. Tokens all survived.*
