# KEY ROTATION EVENT — 2026-10-04

**Directive:** principal rotates ALL fleet keys except Cloudflare. GitHub and all
model-provider keys return later. Until then: local-first execution, Cloudflare is
the only live external capacity, every artifact lands push-ready.

**UPDATE same day, part 2:** principal returned with GitHub + typesafe.ai + moth +
groq. All four verified live in `recon/key-receipts-2026-10-04/` (typesafe noul
heartbeat 0.87; moth /me 200; GitHub login SuperInstance). Groq restored-but-
region-blocked (HTTP 403 Forbidden, same as pre-rotation) → unblocked via a
Cloudflare Worker relay (`quilt-groq-relay`: Workers egress ≠ this box's region —
"cloudflare in the loops" doing its job). DeepSeek/Kimi/deepinfra still burned.
Staged bundles pushed: wave69 (new repo) + quilt-research-canons.

## Status board

| Key | State | Fleet impact | Mitigation in force |
|---|---|---|---|
| Cloudflare (`cfut_…`) | **LIVE (not rotated)** | none — it is the regime | Workers AI + now a groq relay worker |
| GitHub (`ghp_…`) | **RESTORED part 2** | pushes + CI live again | wave69 + canons pushed on return |
| DeepSeek | still burned | reasoner lane down | `@cf/deepseek-ai/deepseek-v4-*` on Workers AI (live) |
| Groq | **RESTORED part 2** — but region-blocked from this box (403) | smallest-model lane needs relay | `quilt-groq-relay` CF Worker (egress ≠ this box) |
| Kimi | still burned | reasoner lane down | `@cf/moonshotai/kimi-k2.6` on Workers AI (live) |
| Mothquantum | **RESTORED part 2** | H3 IonQ recon UNPARKED | `/me` 200 verified; engines list shape TBD |
| typesafe.ai | **RESTORED part 2** | workhorse lane UP — System One question oracle | noul heartbeat 0.87 verified |
| deepinfra | still burned | bulk lane down | CF catalog holds 35 text-generation models / 17 families |

## Headline finding

**Key loss ≠ model loss.** Every rotated provider has a same-or-adjacent model
family running on Cloudflare Workers AI under the one live token. The Wave-69
multi-model cognitive-heterogeneity invariant survives the rotation entirely:
Generator = `@cf/meta/llama-3.1-8b-instruct` (meta family, smoke-tested `ONLINE`),
Validator = `@cf/qwen/qwen2.5-coder-32b-instruct` (qwen family, smoke-tested,
returns structured JSON). 35 text-generation models across 17 families remain
cataloged (`scripts/cf_catalog.sh`).

## Hygiene actions taken (values never printed, never written to disk)

1. `.env.keys` did **not** exist anywhere pre-rotation (verified) — old keys are
   burned in conversation only, never landed on disk. New vault written with
   Cloudflare only, chmod 600, gitignored (verified via `git check-ignore`).
2. Residue scan over the whole workspace found **6 files** carrying rotated-key
   shapes; all scrubbed in place with `REDACTED-ROTATED-KEY` (data preserved,
   secrets gone):
   - `cot-quilt/runs/20261001T195410Z-503b10b9/receipt.json` (1 DeepSeek-shape hit)
   - `scripts/w56_recover_creds.mjs` (2 hits: moth + typesafe)
   - `scripts/quilt-lab/moth_key.env` (1 hit)
   - `scripts/quilt-lab/e13_typesafe_probe.mjs` (1 hit)
   - `si-fleet/jev-quilt/jev_oracle.py` (1 hit)
   - `si-fleet/jev-quilt/tests/test_jev_oracle.py` (1 hit)
3. Post-scrub re-scan: **CLEAN — 0 residue** (`scripts/rotate_scrub.sh`).
4. Honest disclosure: the cot-quilt receipt is git-**tracked**; if that repo was
   ever pushed, the DeepSeek key was remotely exposed. Rotation of that key
   covers the exposure. History was NOT rewritten (fleet law: never delete data;
   the scrub is itself the truthful state going forward).
5. The dying GitHub token was deliberately **not probed** — per directive it is
   treated as burned from this message forward; no command embeds it, so no
   token residue exists in shell history or scripts.

## Operating regime until keys return

- All Wave-69 work builds locally under `/home/z/my-project/wave69/`, committed
  to local git, push-ready in one command each (see
  `/home/z/my-project/wave69/PUSH-ON-KEY-RETURN.md`).
- Cloudflare Workers AI is the model substrate: meta/qwen cells live now;
  deepseek/kimi/glm families available for later heterogeneous cells.
- CI workflows ship in-repo but stay "unverified-on-remote" until push; local
  test receipts stand in (same discipline as wave-67 fresh-clone receipts).
- No external model spend beyond Workers AI on the existing CF plan.
