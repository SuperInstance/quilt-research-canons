# Tripartite Canon Digest — external ideation, fleet-anchored

> **Provenance:** source conversation between Kimi and another agent
> (`downloads/1a0fa426…idea4kimi1.md`, ~3,800 lines, received 2026-10-02).
> Digest + synergy map + R&D backlog by snowball (main-session fleet lane).
> **Status:** FOUND material — every claim below about the source is IN the
> source; every claim about the fleet is cited to a repo/pin; INFERRED
> readings are flagged as such per memo protocol.

---

## 1. What the source conversation is

One continuous ideation arc in six movements:

1. **Neural DAW** — Quilt-as-DAW for NN engineering: LLM execution paths as
   audio tracks, `--cont-batching -np N` slots as the mixer bus, SSE/httpx
   async router as the patch bay. Application: *SyncWeaver AI* — game-audio
   engine shipping a `.nab` (Neural Audio Bundle) instead of static stems;
   generative infill, semantic stem replacement, zero-latency ducking.
2. **Vibe-coding voice loop** — STT cell → cloud LLM (bifurcated
   `tts_payload` + `diff_payload`) → TTS cell + Listener cell (self-hearing
   conversation loop) → Quilt MCP Diff Cell (applies code diffs to the
   running engine, gated by keystroke).
3. **Tripartite architecture** — three independently-evolving agents:
   **User-Agent** (exocortex; feedback = human correction loops),
   **Hardware-Agent** (silicon liaison; feedback = telemetry; migratable
   into ASIC), **Application-Agent** (logic builder; feedback = CI/CD,
   FAIL-first). Consensus over `QUILT_SOCK` via NDJSON frames:
   `{tx_id, source, target, phase}` with phase cycling
   deliberation → consensus_achieved → execution.
4. **Universal vocabulary** — three zero-shot domain simulations (neural DAW,
   marine sonar, medical ultrasound) converge on four terms:
   **Blueprint** (active compiled reality), **Blueprint Branch** (isolated
   experiment), **Snapshot/Milestone** (immutable rewind point),
   **Grafting/Locking** (fusing a chosen snapshot back into the Blueprint).
   Human input is always **Dual-Signal**: Target Signal (raw physical
   material) + Transformation Mask (semantic instruction).
5. **Curriculum "Git Mechanics 201"** — a 15-week course where the fleet's
   own practices (FAIL-first pins, double-entry ledgers, path-spawning,
   substrate-budget conflict resolution, sovereign redaction before
   publish) are the syllabus. The fleet is the living lab.
6. **Panoramic foundation + CF framing** — Four Pillars (Intent Track,
   Logic Track, Substrate Track, Holo-Projection) on a first-class Temporal
   Ledger; "uncooking the loaf" = bidirectional trace; planetary
   P2P seed-ledger as CF-challenge-scale substrate.

## 2. The five open problems (the source's own tail)

The conversation ends by naming exactly five unengineered joints. These are
the **R&D backlog**:

| # | Name | Stated issue |
|---|------|--------------|
| P1 | Temporal Jitter Sieve | async linguistic tokens vs 44.1kHz substrate clock must realign to sub-sample boundaries |
| P2 | Deterministic Rollback Collision | 0.6ms cascade recalc vs incoming human input needs an in-flight capture buffer |
| P3 | Compaction Threshold Rules | uniform Weber-Fechner scalar is crude; need a Priority Weight Schema (structural anchors vs soft buffers) |
| P4 | Zero-Knowledge Substrate Proof | anonymized patches are spoofable; prove genuine-chip compilation without revealing identity |
| P5 | TUI Redraw Pipeline | socket flooding → need Delta-Opcode Matrix (bounding-box updates only) |

---

## 3. Fleet synergy map — the source's concepts land on our repos

This is the load-bearing section: the conversation independently re-derives
mechanisms the fleet has already built, and names open problems our stack
is positioned to close. **Adoption, not collision** — same relation our
edge-watch declared for Casey's quilt-adjudication fork.

| Source concept | Fleet anchor (cited) | Relation |
|---|---|---|
| Temporal Ledger / Milestones | `SuperInstance/quilt-in-git` — receipts as timeline cells, dials trees, orphan branch | same primitive, different name; their Ledger = our receipts + refs/quilt/* |
| Double-Entry Balance Sheet | `SuperInstance/doubt-ledger` — entries as trust debits/credits, fire→due→discharge | direct hit: "double-entry" ≈ ledger entry pairs (observation, relocated-trust) |
| Snapshot / Grafting | `SuperInstance/frozen-clock-lab` P5 genesis-anchor: replay-forward-to-terminal from an anchor position | their Graft = our replay-from-anchor made interactive |
| Blueprint (active reality) | quilt-in-git P4/P7/P8: clone-provable world, cross-clone verify | the "single source of truth everyone interacts with" is our HEAD + receipt chain |
| NDJSON tx frames | doubt-ledger Entry grammar + quilt receipt() rows | same envelope discipline (required fields, named refusals, no silent gaps) |
| Sovereign Audit (line-item veto) | **wave4-query** lane (in flight): `trusted-but-unaudited`, coverage, divergence, `attest` | the audit UI the source sketches is literally our query layer |
| FAIL-first labs (every week) | fleet-wide pins culture; frozen-clock P6 red-demo; pong-quilt R73 demonstrated-RED | the fleet is the curriculum's existing implementation evidence |
| "A canary that cannot fail is worse than no canary" (Mavis doctrine, thread #2) | frozen-clock pins/audit-p6-red.log · quilt-in-git P10 | doctrine already adopted fleet-side 2026-10-02 |
| Durable Objects as "Living Edge Rooms" | Casey's `quilt-organ-workers` (organ-boot-loader/judge-relay/watcher, manifest v1) + `quilt-adjudication` CF entry | same CF substrate reading; ours = receipts/doubt layer, theirs = organ/judge layer |

## 4. The five open problems → buildable fleet increments

Ranked by value×feasibility (smallest first build per problem):

- **P5 TUI Delta-Opcode → `quilt-canvas-tui` opcode increment.** The
  HEWN/SHAPED/DRAWN dialect already exists; the missing piece is a
  bounding-box delta contract so only changed cells transit the socket.
  *One-evening build: a `quilt-delta` filter that diffs two frame states
  and emits only dirty-rect opcodes, with a pin proving bandwidth drop.*
  FOUND: the source asks for exactly this.

- **P2 In-Flight Capture Buffer → frozen-clock SimClock mode.** Honest-mode
  capture during a replay-forward window IS the capture buffer, named in
  our vocabulary: while P5-replay-forward runs, honest-mode appends keep
  landing in the same receipts file; reconciliation order-not-time (P2 pin).
  *Build: a `capture_window` context in frozen-clock that demonstrates
  append-during-replay with no loss; pin: every captured op lands
  byte-identical after the graft.* INFERRED: source's 0.6ms CUDA number is
  unverified; the buffer mechanism is substrate-independent.

- **P3 Priority Weight Schema → doubt-ledger schema question.** We already
  carry the distinction the source wants: `stopped_checking` (soft buffer —
  compressible) vs active entries with live coverage (structural anchor).
  *Build: a `weight` field + a compaction exercise pin — run a uniform
  scalar vs a schema-guided compaction over a seeded ledger, show the
  schema preserves anchors.* Smallest of the five.

- **P1 Temporal Jitter Sieve → order-not-time doctrine (frozen-clock P2).**
  Our receipts order ops by chain position, never wall clock; linguistic
  tokens reconciled to substrate anchors by position is the same sieve
  generalized. *Build: a two-clock demo (44.1kHz anchor stream + token
  stream) where re-ordering token arrival changes nothing in the merged
  outcome.* INFERRED mapping — the source's sub-sample alignment claim is
  stronger than our current pins; treat as research, not port.

- **P4 Zero-Knowledge Substrate Proof → the hard one.** Our sig-canonical
  pins (canonical fnv1a-64 vectors, frozen-clock P6 / quilt-in-git P10) are
  the germ: a chain of attested receipts is an attestation of the machine
  that produced them. A real ZK proof-of-genuine-chip is cryptography the
  fleet has not done. *Honest posture: mark RESEARCH; the interim ship is
  the `attest` ref from wave4-query (auditor attestation, not ZK).*

## 5. Long-horizon research directions (from the digest)

1. **Tripartite as fleet org structure.** The User/Hardware/Application
   agent split maps onto real fleet lanes (user-model lanes / hardware-
   futurist lanes / application builders) with independent feedback loops.
   INFERRED, but the curriculum's claim "the fleet is the lab" is testable:
   the receipts ARE the CI/CD feedback the Application-Agent is specified
   to consume.
2. **`.nab` (Neural Audio Bundle) as a quilt dialect.** A small, named,
   receipted file format with a population/lane structure is exactly the
   pong-quilt artifact class (`pong-quilt/coev@v1`). INFERRED — no audio
   lane exists; record as cross-domain pattern only.
3. **Curriculum as onboarding.** "Git Mechanics 201" Weeks 5–10 describe
   practices the fleet enforces culturally; packaging them as a course is
   an AI-Writings-class artifact, not code. Low priority, high canon value.
4. **Planetary seed-ledger ↔ CF competition.** Module 4's P2P snapshot mesh
   is the CF-scale story; our contribution layer is verification (receipts,
   doubt entries, attest refs) rather than transport. Found: three fleet
   agents (Casey's entry, Mavis's entry, wave4-query) now converge on the
   same competition surface — coordination note already on quilt-adjudication.

## 6. Honest limits

- The source is ideation, not verification: CUDA cascade timings, RTX 4050
  budgets, and ZK mechanisms are **design claims with no receipts**. This
  digest pins none of them.
- The Universal Vocabulary (Blueprint/Snapshot/Graft) is derived from three
  simulations run by one conversation; it is a hypothesis about convergent
  terminology, not evidence of convergence across independent systems.
- Fleet anchors cite pins as of 2026-10-02; pins can be superseded (the
  wave-3 stacked PRs #2–#7 are open, Casey-gated).
- This memo deliberately does NOT adopt the branding ("SuperInstance",
  "Tripartite") into fleet repos; it records the canon for later lanes.

## 7. Cross-references

- Wardroom thread #2 (Mavis, 2026-10-02): canary doctrine, public
  claim-resolver — the verification layer the source's Module 4 assumes.
- cf-native-backend README: design question #3 (trusted-but-unaudited API)
  — wave4-query lane answers it; this memo feeds questions #1/#2.
- research/HANDOFF.md — the living open-work pointer; this digest's §4
  backlog should be considered for inclusion there by the keeper lane.
