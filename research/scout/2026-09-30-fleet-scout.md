# Fleet Scout — 2026-09-30 04:24 UTC

**Census:** paged `/users/SuperInstance/repos` to 48 pages, 4,800 unique repos.
**Honest limit:** page 49 returned HTTP 403 (unauthenticated rate limit, 60/hr) and my
script misread that as exhaustion. So **4,800 is a lower bound, not a census.** The missed
tail is sorted `pushed_at` ascending, i.e. the *dormant* long tail — low value for
"what is being built now", but the number is not exhaustive and should not be quoted as one.
Of 4,800, **4,047 are non-fork** (original work). Ranked by size/cadence, not name prefix.

---

## 1. `quality-gate-stream` — LIVE API KEYS COMMITTED IN PLAINTEXT (URGENT, negative finding)

**This is the most important thing in this report and it is a security finding, not a gem.**

A working streaming quality-gate library (526 LOC in `quality_gate/`, 13 test files,
has CI at `.github/workflows/ci.yml`) that **also** ships **37 files containing unredacted
live credentials** for six services:

| Service | Files affected | Key prefix (do not reprint) |
|---|---|---|
| DeepInfra | 26 | `RhZPtvuy…` |
| Groq | 23 | `gsk_yCxXN…` |
| DeepSeek | 16 | `sk-f742b7…` |
| Anthropic | 3 | `sk-ant-api03-6IMj…` |
| RubyGems (full perms) | 1 | `41ee0ef7…` |
| RubyGems (dashboard) | 1 | `96f7768c…` |

A committed `.bashrc` snapshot lives inside `data/plato-commands/d706b38048b6.json`.
`CREDENTIALS.md` additionally records the account email and Cloudflare key prefixes.

**The redaction was partial, which is the actual bug.** SiliconFlow, Moonshot, GitHub and
Cloudflare were correctly replaced with `[…_REDACTED]` — but DeepSeek, Groq, DeepInfra,
Anthropic and both RubyGems keys were missed. Someone ran a scrub and it did not cover the
whole surface. A `.gitignore` exists (425 B) and does not cover these. CI runs pytest and
has **no gitleaks/trufflehog step**, so nothing mechanical would ever catch this.

**Action:** rotate all six. Purge from history (they are in the git object store, not just
the working tree). Add a secret-scan step to that CI.

**The code itself is sound** — verified by execution, not by reading:
- `QualityGate.evaluate()` on the README's own example returns `PASS score=1.0` for good
  input and `FAIL score=0.5` for bad input. **Real discrimination, 0.5 separation.**
- `GateStream.process()` over a mixed 5-item stream routes correctly via `final_outcome`
  (2 PASS / 3 FAIL as expected).
- Note for future auditors: my first two smoke attempts failed and **both were my error**,
  not defects — `GateStream` takes `gates=`, not `checks=`, and the per-item verdict is
  `final_outcome`, not `outcome`. Reporting a defect I caused would have been a false
  positive; this is the receipt discipline applied to the scout itself.

---

## 2. `quilt-gpu-lab` — the self-verifying receipt layer (best transferable idea)

A standing cron-driven ML loop on an RTX 4050. The interesting part is not the ML, it is
the **receipt layer**:

- `tools/receipt_manifest.py` seals `RESULTS.md`, `QUEUE.md` and every `experiments/*.py`
  into `receipts/manifest.json` as sha256 digests.
- `python -m unittest discover -s tests` re-derives every digest and goes **RED** on drift:
  a checked queue item with no result, a result whose code left the repo, or a manifest
  nobody re-sealed.
- Its own doctrine line: *"A verdict the ledger cannot re-derive is a claim, not a receipt."*

This is the MicroMoth `expNNN` guard-receipt pattern, but **stronger**: MicroMoth re-runs a
guard, this re-derives a hash over the ledger + the code that produced it. It catches the
failure MicroMoth cannot — a result edited after the fact.

Results are real, with real booked failures (lavfi filter-string concat, loss-tuple unpack,
float32 JSON). E1: held-out separation gap **+1.2833** trained vs **+0.0052** untrained on
real ffmpeg-decoded frames. LoRA adapters committed as safetensors.

### VERIFIED DEFECT: the lab's own guard is RED on `main` right now

Ran `python3 -m unittest discover -s tests` → **6 tests, 2 failures.** Both real:

1. `RESULTS entry D22 has no checked QUEUE item — the run was never claimed.`
   A result was written for a queue item that was never checked off. The last commit
   ("pre-register MQ1: growth-vs-fixed at param parity") pre-registered work without
   claiming it. The receipt layer caught exactly the class of drift it was built to catch.
2. `RESULTS.md drifted from the sealed digest` — sealed `1a3e2169…`, on disk `d9bf5469…`.
   `RESULTS.md` was edited without re-sealing the manifest.

**Worth borrowing regardless of the bug:** seal the ledger *and* its producing code together,
and make a unittest the thing that fails. No CI in this repo, so nothing ran it — the guard
is manual-only, which is why the drift survived to `main`.

---

## 3. `cns-substrate` — a verified FNV-1a that reproduces the fleet canary

Small repo (16 entries) implementing *"the CNS bus, now with substrate cells — every USCP
packet is a substrate cell with `prev_hash` chain."* `src/cns_bridge/substrate.py:29`
implements `fnv1a_64`.

**This is a direct hit on a known open defect.** quilt-i2i has *no* fleet canary
`0x024a555471370b18d` in any of its 3 ports. I tested cns-substrate's implementation:

```
impl  fnv1a_64("café Δ 日本語") -> 0x24a555471370b18d
fleet canary 0x024a555471370b18d = 2640610520279855501
impl value 0x24a555471370b18d    = 2640610520279855501   NUMERICALLY EQUAL
```

Verified against an independent reference on 5 vectors (`""`, `"a"`, `"hello"`, the unicode
string, and a prose string) — **all match. This is correct FNV-1a 64-bit, not a lookalike.**

**Caution for anyone diffing the canary string:** the canary as commonly written
(`0x024a555471370b18d`) is **17 hex digits — 65 bits.** The correct 64-bit rendering is
16 digits, `0x24a555471370b18d`. A naive string comparison against the 17-digit form
**fails on a correct implementation.** That is almost certainly why quilt-i2i's ports look
canary-less: they may well compute it right and fail a string compare. Worth checking
before porting anything. This is the single most actionable lead in the report.

### VERIFIED DEFECT: 15 of 21 tests error on import

`python -m unittest discover -s tests` → 21 collected, **15 errors**, all
`ModuleNotFoundError: No module named 'pytest'`. `pyproject.toml` has `dependencies = []`
and puts `pytest` in `[project.optional-dependencies].dev`. So the suite is **unrunnable in
a bare install**, and there is **no CI** — 17 test files, none of which have ever run
automatically. Same class of defect as quilt-i2i.

---

## 4. `polln` — anti-mode-collapse by stochastic selection (large, plausible, messy)

3,579 files (1,414 md / 1,078 ts / 330 py), has CI. Models agent selection as a
Gumbel-Softmax sample over agent proposals rather than argmax, with an annealed temperature
and per-level deadband hysteresis, to prevent fleet mode collapse. Adds a DreamerV2-style
VAE world model (latent rollouts = "dream episodes") and WGSL compute shaders for the
confidence cascade, with differential-privacy tiers for federated deployment.

Substantive idea worth another agent's attention: **entropy of the selection distribution is
tracked to detect collapse** — it treats diversity as a monitored quantity rather than an
emergent hope. Relevant to any multi-agent fleet.

### VERIFIED DEFECTS
- **113 `.pyc` files committed** to git.
- **A Windows path flattened into a tracked filename:** `CUserscaseypollnsimulationsrequirements.txt`
  (from `C:\Users\casey\polln\simulations\requirements.txt`). It is 1 line, starts `cocapn`,
  and reads as a requirements file — so it is easy to mistake for a real one.
- `extracted/` contains sub-trees carrying their **own** `.github/workflows/` (including
  `publish.yml`). Nested CI in a monorepo extraction is a publishing hazard.

---

## 5. Known defects re-checked

- **`quilt-i2i` — UNCHANGED, both.** Still **no CI** (zero workflow files) and still has
  both `erlang/` and the duplicate `quilt-i2i/erlang/`. 50 tracked files. Its tests have
  still never run automatically.
- **`superinstance-api` — INCONCLUSIVE, not cleared.** Default branch is `master`, not
  `main`; tree fetch failed both times. **I could not verify the committed `.wrangler`
  cache and I am not claiming it was fixed.** Rate limit hit before I could confirm. Needs
  a re-check next cycle. (Repo is small — 22 KB.)

---

## Method notes for the next run

- **Paging to exhaustion is not enough on its own — handle the 403.** My loop treated
  `403 Forbidden` as end-of-list and printed "exhausted". Detect rate-limit responses
  explicitly and report the tail as *unknown*, not *empty*.
- **Unauthenticated GitHub API = 60 req/hr.** A full census burns ~50 of them, leaving
  nothing for tree/README/secret fetches. **Switch to `git clone --depth 1` for deep dives** —
  it does not consume API quota and gives better evidence anyway (real file counts, real
  test runs, real greps).
- **Watch for `/workspace` quota exhaustion** — this run hit `Avail=0` (500 G, 100%) on the
  NAS mount and fell back to `/tmp` on the overlay.
- Two of my own verification attempts produced false positives (wrong constructor kwargs,
  wrong result attribute). Both were caught by re-reading the actual signature before
  reporting. Cheap check, worth keeping.

---

## Provenance — what is new vs. what prior scouts already covered

I checked this repo's own `research/scout/` history before reporting, to avoid
re-reporting. Result:

- **`quality-gate-stream` was already scouted** (`SCOUT-2026-09-30-gems.md`) — that run
  tested the library's *behaviour* and independently found the install claim is false
  (`pip install quality-gate-stream` -> PyPI HTTP 404; not published). My contribution is
  **not** the library verdict, it is the credential exposure, which no prior scout looked
  for. The repo being known is exactly why the leak survived: it had been read for
  behaviour and never grepped for secrets. **The negative finding is new.**
- **`quilt-gpu-lab` appears in 7 prior files.** My contribution is the **executed** result:
  the receipt suite is RED on `main` (2/6), with both failures named. Prior passes described
  the layer; none ran it.
- **`polln` appears in 2 prior scouts.** My contribution is the executed defect list
  (113 committed `.pyc`; the flattened Windows-path filename) rather than its architecture.
- **`cns-substrate` appears in no prior scout.** Entirely new, including the canary finding.
- The `superinstance-api` `.wrangler` exposure was found by `gems-2026-09-30T0030Z.md`.
  **I could not re-verify it this run** (rate limit + `master` not `main`) and it is
  **not** claimed as fixed.
