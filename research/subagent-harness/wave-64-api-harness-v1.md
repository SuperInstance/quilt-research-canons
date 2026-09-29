# Wave-64 API harness v1 — paste-ready briefing for fleet subagents

Purpose: refresh any subagent with working knowledge of the four provisioned organ APIs.
Verify date: 2026-09-30 (all shapes confirmed live; see `research/wave-64-keyroll-integration-2026-09-30.md`).
Secrets rule (absolute): keys live in `/home/z/my-project/.env.keys` (mode 600, gitignored). Source them;
never print, log, commit, or paste a value anywhere. Refer to keys by env-var NAME only. Mask any
key-shaped string that appears in captured output. `bash scripts/keyscan.sh` before any push.

```bash
set -a; source /home/z/my-project/.env.keys; set +a   # then use $VAR; never echo
```

## 1. muscle — deepinfra (OpenAI-compatible chat + embeddings)

- Base: `https://api.deepinfra.com/v1/openai` · Auth: `Authorization: Bearer $DEEPINFRA_KEY`
- Chat: `POST /chat/completions {"model":"ByteDance/Seed-2.0-mini","messages":[{"role":"user","content":"..."}],"max_tokens":24,"temperature":0}`
- Embeddings: `POST /embeddings {"model":"Qwen/Qwen3-Embedding-0.6B","input":"text"}` → 1024-dim vector (~0.9 s warm)
- Live fast lanes: Seed-2.0-mini 3.2 s; Qwen3.8-Flash 2.6 s; Nemotron-3.5-Lightning & Ling-3.0-flash cheapest ($0.06 in).
- Gotchas: `max_tokens` does NOT cap hidden reasoning (Seed billed 200 out-tokens on a 24-token ask) —
  set reasoning-effort knobs when cost matters; no rate-limit headers — self-throttle; bill by `estimated_cost`.
- Falsifier of this section: any 401/403 on a well-formed call = harness stale, re-verify before use.

## 2. judge — typesafe.ai (System One: noul / choice / score as a service)

- Base: `https://api.typesafe.ai` (NOT the apex — that is a marketing site) · Auth: `Bearer $TYPESAFE_API_KEY`
- Judge call: `POST /v1/systemone {"model":"jev-latest","state":"<text under judgment>","questions":{"q":{"type":"noul","instructions":"..."}}}`
  - `noul` → `{noul: 0..1}` (P(yes)) · `choice` → `{choice, confidence, probabilities}` (criteria = named options)
  - `score` → `{score, confidence, legend, probabilities}` (criteria = ordered level descriptions from 0)
- Model: `jev-latest` = jev-1.13.0 (same backing as wave-62 priors battery; `jev-preview` unexercised).
  Output tokens free; input tokens billed. Every response carries `x-typesafe-request-id` — include it in receipts.
- Error shapes: missing key → 403 `{"detail":{"error_type":"authentication_error",...}}` (403, not 401);
  bad path → 404 `{"detail":"Not Found"}`; apex 404 = 7.4 KB Framer HTML.
- Fleet meaning: the E9 sysone discipline (types hold, values leak, receipts surface it) — now external.
- Falsifier: a systemone answer without a request-id, or a 200 that lacks `answers`/`usage` keys.

## 3. quantum channel — mothquantum (emu now, IBM QPU on demand)

- Base: `https://api.mothquantum.com/api/v1` · Auth: `Bearer $MOTH_KEY`
- **CLIENT RULE (hard-won this wave): the edge HTML-403s the python-urllib User-Agent in <0.1 s.
  Use curl, or set a normal UA header. Never read that 403 as an authorization verdict.**
- Hello-world: `POST /engines/coin-toss-v1/process -d '{"params":{"shots":10}}'` → 202 `{job_id}` →
  poll `GET /jobs/{id}/status` (2–5 s) → `GET /jobs/{id}/result` (inline JSON; ages out → copy on first fetch)
- Read first, then spend: `GET /me` · `GET /engines` · `GET /engines/{id}` (params_schema, credits_per_run).
  Credits: comet-qrng-v1 = 5 (SP 800-90B certified QRNG — the E6 draw-channel candidate), coin-toss = 2,
  otoc-echo/tomography = 1, test engines = 0. QPU mode (`mode:"qpu"`, backend e.g. ibm_brisbane) queues
  minutes–hours — never submit without a registration; emu returns in seconds.
- Pipeline steps emit OpenQASM (`application/x-qasm`) as circuit IR; 300 req/min/key; RFC 7807 errors.
- Falsifier: a submit that returns neither 202+job_id nor an RFC 7807 body.

## 4. tissue — cloudflare (read-only until a registration says otherwise)

- Base: `https://api.cloudflare.com/client/v4` · Auth: `Bearer $CLOUDFLARE_TOKEN` (READ-scoped)
- Verify: `GET /user/tokens/verify` · Account: `049ff5e84ecf636b53b162cbb580aae6` (subdomain `casey-digennaro`)
- Inventory of record (2026-09-30): 372 workers (26 cron, incl. `cell-heartbeat`, `fleet-cron`) ·
  29 Vectorize indexes (cosine; `i2i-index` 1024d, `fleet-embeddings-v2` 768d, `quilt-canon-v2` 768d) ·
  Workers AI 319 models (`@cf/baai/bge-m3` = 1024d, matches i2i-index) · 145 KV · 42 D1 · 33 R2.
- i2i-ledger: worker `i2i-ledger` at `https://i2i-ledger.casey-digennaro.workers.dev` — routes `/near`,
  `/since`, `POST /book` (401 without keeper token; booking text staged in worklog 63-i2i-probe).
- Discipline: this lane NEVER writes (no deploy, no index mutation, no secret read) without a registered
  experiment; a 403 on a sub-endpoint is a scoped-out fact, not a failure.
- Falsifier: any write side-effect observed from a read-only lane run.

## Cross-organ receipt of record

wave64-cell-probe (3 organs, one cell): deepinfra embedded the rung-3 sdist claim (1024-dim,
sha256-16 6bd24957a996ce9a); typesafe judged it noul=0.79 stranger-decidable, score 3.57/4 resolvable —
independently corroborating the fleet's hand calibration; moth coin-toss completed 5/5 heads/tails (emu,
2 cr). Receipt: `lanes/wave-64/cross-probe-receipt.json` (local) + §3 of the wave-64 integration doc.
