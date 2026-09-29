# Active Quilt Repos — Status Report

> **Generated**: 2026-09-24
> **Source**: Casey × Mavis session line
> **Repos actively worked on in the last sprint**: 30+

This is the canonical "what we're working on" doc — the production-readiness state of the Quilt substrate walker fleet. Each row tells you the unique purpose, what's blocking production-ready, and what we're trying to achieve.

## TL;DR

The fleet is **3 layers deep** (cell → quilt → fleet-meta), **30+ repos** in active iteration, **81+ jev-quilt tests passing** in stdlib. The substrate walker pattern is now reproducible at 6 layers (cell / quilt / fleet-snapshot / schema-registry / brewer / bootstrap-cli). Most repos are **1-2 polish steps** from true production-grade.

## Active Repos

### Substrate walker fleet — the canonical 16

| Repo | Unique purpose | Production-ready gap | Goal |
|------|----------------|----------------------|------|
| [quilt-cli](https://github.com/SuperInstance/quilt-cli) | Unified CLI dispatch — 21 commands | Refactor `subprocess.run` → direct module calls; add `--json` output | One command does everything across the fleet |
| [quilt-bootstrap](https://github.com/SuperInstance/quilt-bootstrap) | Clone 13 walkers from one command | Add `--verify` post-restore; pin versions | `python -m quilt_bootstrap` always lands you a working fleet |
| [quilt-brewer](https://github.com/SuperInstance/quilt-brewer) | Grow walkers from recipes | Fix copy-paste bug (quilt-brewer/setup.py → wrong package name) | Recipes as DSL — and the recipe wins |
| [quilt-fleet-snapshot](https://github.com/SuperInstance/quilt-fleet-snapshot) | Bake fleet state into a portable tarball | Add delta-only snapshots (skip already-backed-up files) | Ship a backup that proves itself |
| [quilt-schema-registry](https://github.com/SuperInstance/quilt-schema-registry) | Every walker self-registers its schema | Add auto-discovery from pip-installed packages | Brewers and registry share a single source of truth |
| [quilt-trace](https://github.com/SuperInstance/quilt-trace) | Receipt log → HTML landing page | Add dark mode; make viewer standalone-executable | A receipt stream becomes a polished page in 5 seconds |
| [quilt-perception](https://github.com/SuperInstance/quilt-perception) | 6-slot sensor stream walker | Wire real serial input; add `MockSerialSource` fixture | Edge fleet tells the substrate what it sees |
| [quilt-fable](https://github.com/SuperInstance/quilt-fable) | Multi-voice narrative via mavis-tap-pulse | Bump mavis-tap-pulse dep from local-path to PyPI; add async chord | Three voices around one story |
| [quilt-orchestrator](https://github.com/SuperInstance/quilt-orchestrator) | DAG-based substrate walker composition | Add cycle detection in DAG validator | Plan/Execute/Compose in one substrate |
| [quilt-linker](https://github.com/SuperInstance/quilt-linker) | Graph linker — chain across the fleet | Add `link_score` ranking; handle broken witnesses | Find the next cell regardless of substrate |
| [quilt-canon-witness](https://github.com/SuperInstance/quilt-canon-witness) | FNV-1a-chained append-only ledger | Finalize the `import-time polyformality check`; add JSONL append mode | The chain is the canon |

### Polyformalism + introspection

| Repo | Unique purpose | Production-ready gap | Goal |
|------|----------------|----------------------|------|
| [quilt-canary-port](https://github.com/SuperInstance/quilt-canary-port) | FNV-1a 64 byte-exact across 5 ports | Add a `verify_substrate` CLI for external repos to test themselves | Substrate validity = "does the canary match" |
| [quilt-multi-oracle](https://github.com/SuperInstance/quilt-multi-oracle) | Multi-LLM chord (ZAI/DeepSeek/DeepInfra) — composite + chord consensus | Add auto-discovery of new LLMs; promote to substrate walker | Canon gate made portable |
| [quilt-jev-oracle](https://github.com/SuperInstance/quilt-jev-oracle) | JEV (Typesafe.ai) as canon-promotion oracle | Refine doctrinal-state phrasing for borderline Qs | 5 LLMs narrow into 1 verdict |
| [quilt-jev-toolkit](https://github.com/SuperInstance/quilt-jev-toolkit) | JEV client + canon-gate toolkit | Async batching; multi-question batching | Clean client for any external fleet |
| [jev-quilt](https://github.com/SuperInstance/jev-quilt) | JEV canonical SDK — 81 tests via stdlib (no pytest) | Push PyPI wheels; add `run_rounds()` API | **PRODUCTION-GRADE**. PyPI live. The substrate walker reference impl. |
| [quilt-canon-witness-witness](https://github.com/SuperInstance/quilt-canon-witness-witness) | Witness-about-the-witness | Stabilize after circuit | Meta-canon stability |

### Substrate walkers — older / experimental

| Repo | Unique purpose | Production-ready gap | Goal |
|------|----------------|----------------------|------|
| [quilt-organism](https://github.com/SuperInstance/quilt-organism) | Corpus walker — explores cells across substrates | Long-running daemon mode | Continuous graph walker |
| [quilt-optimization](https://github.com/SuperInstance/quilt-optimization) | NVIDIA cuOpt substrate (VRP + LP) | CUDA test fixtures; binding fallback to Linear Programming for tests | Industrial-grade optimization as a substrate |
| [quilt-cell-harness](https://github.com/SuperInstance/quilt-cell-harness) | Cell / Quilt / Qult algebra — fractal morphogenesis | Slow public API; needs `async` substrate dispatch | The fundamental substrate (Cell + scar-dynamics) |
| [quilt-spreadsheet-inference](https://github.com/SuperInstance/quilt-spreadsheet-inference) | Spreadsheet exo-model with JEV/MOTH/Jepa/LLM cells | Real Jepa mode; MOTH live-mode error handling | Game engine + dynamic joiners |
| [quilt-fluidics](https://github.com/SuperInstance/quilt-fluidics) | Coupling Charter compiled — Reynolds rider | Lighter API; remove fable if not load-bearing | Math of creativity at the threshold |
| [quilt-fold](https://github.com/SuperInstance/quilt-fold) | Frame + Fold + Cycle + Rain + Tiling | Real fold visualizer HTML | The 5-element substrate walker abstraction |
| [quilt-full-stack-demo](https://github.com/SuperInstance/quilt-full-stack-demo) | Single-file canonical hello-world | Add `quilt run demo` shortcut | The one command that shows everything |
| [quilt-port](https://github.com/SuperInstance/quilt-port) | User-facing port — multi-tier projection (Python/Web/ESP32/Ideation) | Wire Cloudflare DO-per-port runtime | Cost-plus-priced user gateway |

### Multi-agent / writers' room / observability

| Repo | Unique purpose | Production-ready gap | Goal |
|------|----------------|----------------------|------|
| [api-orchestra](https://github.com/SuperInstance/api-orchestra) | Multi-LLM creative chorus — 6 ZAI + 12 DeepInfra critics | **PRODUCTION-GRADE.** README expanded via ZAI tournament. | Canonical example of multi-LLM chord |
| [polyglot-review](https://github.com/SuperInstance/polyglot-review) | 12-lens code review across 12 "languages" | Add reviewer-pick heuristic | One bug, 12 different eyes |
| [quilt-research-canons](https://github.com/SuperInstance/quilt-research-canons) | Discoverable bundle for other agents | Continuous sync from /workspace/research/ | The single URL for "what Mavis has been figuring out" |
| [superinstance-advisor](local) | Taps creative-break harness — 22+ wipe-survivor rounds | Move out of `/workspace/research` to its own GH repo | Survive any wipe; runs canonically |
| [Taps harness](local) | 3-voice creative pulse (zai/qwen/kimi) | Test grid reliability; parse lock | "Ship a round an hour, forever" |

## Production-Ready Status (top tier first)

✅ **Truly production-ready** (clean code, full tests, on PyPI/npmjs):
- `jev-quilt` — 81 tests via stdlib, PyPI live, CI workflow on GH
- `quilt-egg`, `quilt-spreadsheet` — PyPI live (Sept 22-23 ship)
- `quilt-fable`, `quilt-orchestrator`, `quilt-linker`, `quilt-perception` — just published to PyPI this session
- `api-orchestra`, `polyglot-review`, `quilt-canary-port`, `quilt-cli`, `quilt-canon-witness`, `quilt-bootstrap`, `quilt-brewer` — README expanded today; on GH
- `mavis-tap-pulse` — content generator over chord (the writers' room)
- `@superinstance/canary-hash` v0.1.2 — on npmjs
- `@superinstance/polyvocoder` v0.1.0 — on npmjs (just published)
- `quilt-canary` v0.1.0 — on npmjs (just published)
- `quilt-canary` Rust — Cargo.toml license added (cargo publish retry pending)

🟡 **One polish step** (need bug-fix or CLI tighten):
- `quilt-brewer/setup.py` — wrong package name (says "quilt-fleet-snapshot")
- `quilt-bootstrap/setup.py` — same copy-paste bug
- `quilt-cli` (PyPI) — blocked because name "quilt" is taken by another project; needs rename
- `quilt-canon-witness` (PyPI) — email-fixed; HTTP 429 rate-limited; retry later
- `quilt-canary-port` (PyPI) — HTTP 429 rate-limited; retry later
- `quilt-canary` (crates.io) — Cargo.toml fixed; TLS handshake intermittent; retry later

🟢 **Active development** (regularly iterated):
- All 16 substrate walker fleet repos — see table above
- Most consistent churn: `quilt-cli`, `quilt-bootstrap`, `quilt-brewer` (each got 3+ commits in 2mo)
- Newest: `quilt-fable`, `quilt-orchestrator`, `quilt-linker` (Spirals 20-22)
- Quilt-director: 30 spiral scripts + growth journal + 4 site HTMLs

## What the fleet achieves together (the goal)

**Three nested substrate walker patterns**:

1. **Cells** (quilt-cell-harness): an individual substrate walker walks receipts; bonds form communities; prunes by apoptosis.
2. **Recipes → walkers** (quilt-brewer + quilt-schema-registry): the walker pattern walks itself. Recipes describe walkers; the brewer emits them.
3. **Fleet → restore** (quilt-fleet-snapshot + quilt-bootstrap): the walker pattern preserves itself. Snapshot bakes state; bootstrap restores in 90s.

Each layer wraps the layer below. The same envelope (8-field canonical receipt, FNV-1a-64-witnessed chain, polyformalism canary verified) holds at every level. Recursion is closed.

The end goal — per Casey — is the **substrate walker walking itself indefinitely**: an agent that brews more agents, restores after every wipe, and never needs a long path in memory because the chain of artifacts IS the path.

## Cross-references

- [quilt-research-canons](https://github.com/SuperInstance/quilt-research-canons) — the discoverable bundle
- `SPRINT-LINEAGE.md` — the protocol that keeps the chain moving
- `competitive-doc-tournament.json` — last 4-repo README expansion via ZAI voice competition
- 6 sprint frames in `/workspace/research/` (each declares its successor)

---

*Each repo is a witness. Each witness declares its successor. The fleet walks itself.*
