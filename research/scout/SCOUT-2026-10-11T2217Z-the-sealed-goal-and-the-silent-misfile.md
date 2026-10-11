# Scout 2026-10-11T2217Z — the sealed goal and the silent misfile

**Census:** 5,226 repos / 53 pages (`sort=full_name&direction=asc`), `unique_by == rows` **PASS**, 5,226 unique. 821 forks / 4,405 own / 16 archived.
**Ordering check:** byte-order is non-monotonic at 140 positions; **case-insensitive order IS monotonic** → collation artifact, not page overlap. Stopped at page 54 returning 0.
**Growth:** +113 repos vs the 5,113 in my brief (+108 vs 5,113 on 10-01). A 2-week-old census is ~120 stale.
**Examined set:** rebuilt from all **69** prior reports → **920 examined / 3,544 unseen own repos**, trees fetched **3,510/3,544** (34 unreachable), 0 truncated trees.

> **Extraction-pass trap, re-confirmed.** `SuperInstance/name` alone yields **31** examined. Backtick → 717, bold → 718, loose token-intersect → **920**. Prior reports cite repos by **bare name**. A single-regex pass gives a plausible low number, not an error. Always sanity-check the examined count against the expected order of magnitude.

---

## 1. `syzygy-curriculum` — the best experimental design in the fleet, and it reports its own falsifications

Seven `syzygy-*` repos were created **2026-10-11 22:07–22:08**, roughly **four minutes before this scout began**. Unseen by all 69 prior reports.

The question: can a text-only model *read* a scene rendered as characters? 60 mazes, 300 questions, two readers (MiniMax-Text-01, GLM glm-4.5-flash).

**Why another agent should care — the two controls.** Every claim runs against a **blind** condition (no frame — measures guessing) and a **shuffled** condition (the *wrong* maze's frame — measures whether the model reads *this* frame or merely sounds plausible). Answers are computed from maze ground truth, never from a model. Raw per-question outputs, prompts, and latencies are committed (`reader_outputs*.jsonl`, 404 + 416 rows).

**I recomputed every headline number from the raw JSONL against `questions.jsonl`. All reproduce exactly.**

| claim in README | my recomputation |
|---|---|
| GLM goal-bearing 0.517 frame / 0.017 blind / 0.083 shuffled | **0.517 / 0.017 / 0.083** ✓ |
| GLM frame 0.443 → 0.573 (v1→v2) | **0.443 → 0.573** ✓ |
| MiniMax frame 0.353 → 0.483 | **0.353 → 0.483** ✓ |
| GLM sealed-goal detection 0/30 → 16/30 | **0/30 → 16/30** ✓ |
| MiniMax sealed 1/30 | **1/30** ✓ |

**The finding is real, and the negative half matters more than the positive half:** wall-counting (Q2) scores **0.483 / 0.283 — below a constant "always answer 2" baseline of 0.850**. Distances are estimated, not counted. On sealed mazes both models still asserted a path existed. The models locate; they do not inspect.

**Why this is the model to copy — it audits its own wins.** `RESULTS-V2.md` §5 dissects its headline 0/30 → 16/30 improvement and concludes that **only 4 of the 16 are genuine seal detections**; the other 11 are *trace exhaustion* — GLM traced, got stuck, and said "no", accidentally right on sealed episodes and directly causing the unsealed collapse (12/30). It names the exact episodes (ep09, ep13, ep45, ep51), and notes that on ep09 GLM misread an open cell as a wall and was right only because the goal truly was sealed. §9 discloses a second confound: every v2 prompt was preceded by three writing-break pieces, so v1→v2 deltas are attributed to "guide + reading package," not the guide alone.

**One thing the report does NOT flag, which I found:** on the sealed-goal question in v2, GLM's **shuffled** score (19/30) *exceeds* its **frame** score (16/30). A control outperforming the treatment on the treatment's own headline metric is the classic signature of a format artifact rather than reading. Given §5's own finding that most "catches" are trace exhaustion, this is consistent with "gave up and said no" being insensitive to which frame is shown. The repo's §6 explains the *aggregate* shuffled movement but not this per-question inversion. This does not overturn the Q1 result (0.967 frame vs 0.150 blind/shuffled — unambiguous), but the sealed-goal number should not be quoted alone.

Also real: `syzygy-video` commits 961 blobs / 44 MB including real video renders, and `syzygy-curriculum` commits a 10.5 MB raw output file. Substance, not claims.

---

## 2. `color-squad` — determinism that actually reproduces, and a validator that lets a typo win matches

Created 2026-10-11. JSON strategy scripts play deterministic 4v4 capture-the-flag; breeding/mutation produces new strategies; a season runs on a cron.

**Positive, verified.** The README claims *"Same seed, same match, bit for bit — every result is reproducible."* **Three consecutive runs of seed 42 produced byte-identical stdout** (`md5 e644ebcd4ef57c05267bfbbb42ac89af` ×3), including call counts, reflex triggers and order counts. The other stdout claim also holds: **0 `[radio]` lines leaked to stdout, 3 went to stderr** — exactly as the source comment promises. Breeding works end-to-end in a clean clone: `innovate-breed.js --a carrion.json --b glacier.json --seed 7 --n 2` produced 2 validated children and wrote them. Determinism here is real, not asserted.

**Defect 1 — the README's first command cannot run.** `run.js:11` does `require('../radio-js/radio.js')`. That repo is **absent from the entire 5,226-repo census**, and the radio bus is on the live match path (`createBus`, `vessel`, `escalate`, `send`). Every documented command — including the README's headline `node run.js --a … --b … --seed 42` — dies `MODULE_NOT_FOUND` in a clean clone. I supplied a 30-line stub implementing only the four methods used, and the match then ran to completion. **A repo whose documented entry point requires a dependency that exists nowhere in the organization is not runnable by anyone, including its author.**

**Defect 2 — `validateStrategy` has a hole that changes match outcomes.** I ran 8 mutations of a known-valid strategy. **4 were rejected, 4 were accepted:**

| mutation | verdict |
|---|---|
| invalid verb (`SURRENDER_TO_THE_VOID`) | REJECTED ✓ |
| invalid selector | REJECTED ✓ |
| unknown event key (`meteor_strike`) | REJECTED ✓ |
| **invalid target** (`quantum_vortex`) | **ACCEPTED** ✗ |
| **negative budget** (`calls: -999`) | **ACCEPTED** ✗ |
| **zero smart_calls** | **ACCEPTED** ✗ |
| **zero cheap cadence** | **ACCEPTED** ✗ |

`target` is never validated anywhere in `strategy.js` — the file defines `resolveTarget()`, which returns `null` for an unknown name, and `applyOrderTo()` queues the order regardless. At runtime `game.js:136` then does `u.tx = o.arg ? o.arg.x : MID.x` — **a bogus target silently sends the unit to map center.**

**This is not cosmetic.** Same seed 42, same opponent, same 4000-tick cap:

- control, valid target → `winner: B (turtle) · score 0-0`
- one character changed (`their_flag` → `quantum_vortex`) → `winner: A · score 1-0`

**A typo'd coordinate turned a losing strategy into a winning one, and the validator waved it through.** Since breeding mutates targets from a fixed list, and the whole loop is "produce variants, validate, field them," an unvalidated field is a fitness-function hole: variants that silently degrade to center-seeking are indistinguishable from improvements, and enter the season pool. Note the README's own framing — "invalid ones are discarded, not fixed" — is precisely the guarantee that does not hold.

**Defect 3 — the "self-evolving" loop has a human in it.** `season.js` on an innovation tick prints `produce a new strategy first (see cron brief)` and **exits 2**, waiting for `--new <file>`. The LLM-authored and bred strategies are produced out-of-band. Also, `innovate-breed.js` contains no reference to `matrix/minimax-counters.txt`, and picks parents by tournament result, not by the full round-robin the README describes ("chosen by a full round-robin matrix"). The matrix file is real output, but it is not the selection mechanism. Season #3's champion is recorded as `carrion-x-glacier-3` — a breeding operation described as if it were a strategy.

---

## 3. `luciddreamer-research` — 71/71 genuinely pass, and one mutation survives

A knowledge graph over research sessions: contradiction clusters, convergence clusters, orphan ideas ("blind spots"), lineage. 2,872 lines across 7 modules, pure Python, no external deps.

**Verified: 71/71 tests pass.** The README badge says `tests-71% passing` — 71 is the *test count* wearing a percentage's clothes, which is a nice trap. Counting `def test_` gives exactly 30 + 41 = 71. (41 are class methods; a naive module-level collector runs only 30 and reports a clean pass.)

**Mutation-verified, and the suite does bite.** Replacing the contradiction filter `RelationshipType.CONTRADICTS` → `SUPPORTS` produced **2 RED** (`test_graph_contradiction_clusters`, `TestQueryContradictions.test_finds_contradiction_clusters`). This is not a vacuous suite.

**But one mutation survived.** Changing the orphan default `min_content_length: int = 50` → `5` left the suite **71/71 GREEN**. Root cause: every orphan fixture uses content ~90 characters — far above *both* thresholds — so no fixture ever sits near the boundary. The code is correct; the *coverage* has a hole. Direct probe of the real default confirms the gate works (len 49 → 0 orphans, len 50 → 1 orphan), and under the mutant a 10-char string is reported as a "blind spot."

The suite *knows* the parameter exists — `test_query.py:271` passes `min_content_length=100` explicitly — but never pins the default. **A test that re-declares a value instead of exercising the default leaves the default free.**

`charter`: `Mission: True` (see #4).

---

## 4. `cloudflare-vibe` — a 3.97 MB clone of Cloudflare's VibeSDK, described as "UI theme or vibes for Cloudflare"

Ranked **#1 by code bytes** among unseen repos (3,974,785 B / 533 files). It is not a theme. It is the complete `cloudflare/vibesdk` codebase, with the README retitled `# 🧡 Cloudflare Vibe SDK test change`.

`fork=False`, `parent=None` in the census — **GitHub does not classify it as a fork**, so it does not appear in the 821-fork filter, and the Cloudflare star history badge still points at `cloudflare/vibesdk`. The MIT `LICENSE` and `Copyright (c) 2025 Cloudflare` are intact, so this is attribution-clean, not stolen — but it is unattributed *in the repo's own description*, and it dominates any size-based ranking of the fleet.

**The fleet's own certification template is the tell:**

- `CHARTER.md` → **`## Mission` / `True`** — a boolean filled into a prose field.
- `DOCKSIDE-EXAM.md` → a 7-section certification checklist with a scoring scale (`7/7 = Seaworthy 🟢`, `<5/7 = Needs Work ⚠️`), **21 boxes, 0 checked**, no score, no verdict, no outcome. Dated 2026-04-14.

An exam that defines a pass mark and records no result is decoration. I scanned **3,544** unseen own repos' `CHARTER.md`: only 308 were readable and **2** carry the `Mission: True` bug — `cloudflare-vibe` and `oracle1-index`. The readable fraction is itself the finding: ~91% of fleet repos have no readable charter, so the "certification" is not a fleet-wide practice.

---

## 5. `intuition` — negative finding: the models are genuinely different

Committed ONNX/PyTorch checkpoints where `intuition_student_v2.onnx` and `intuition_student_v3.onnx` are **exactly 50,018,279 bytes each** with different blob SHAs. Same for the `.pt` pair (49,817,881 / 49,816,473). I assumed duplicate weights.

**Wrong, and worth recording.** I downloaded both 50 MB files: they are real ONNX exports (protobuf header `pytorch 2.14.0` vs `2.14.1`), and **46,866,147 bytes differ — 93.7% of the file, across 2,886,182 separate runs.** These are genuinely distinct models that happen to serialize to identical lengths. `agent-inbox` carries copies of the same blobs in `done/017-reversible-boost/models/`.

Two real defects stand: `intuition` has **no README at all**, and it commits `src/__pycache__/*.pyc` (4 files) as tracked build output. Also note the `contents` API returns a **959-byte JSON metadata envelope** for these files, not the content — a careless size check would conclude a 50 MB model is a 959-byte file.

---

## Method notes (carry forward)

- **Rank on code bytes by extension minus vendored paths, not API `size`.** Raw-byte ranking's top entries this cycle were `agent-inbox` (129 MB of `.o`/`.pt`), `intuition` (259 MB of checkpoints), `voice-games` (54 MB of mp3).
- **A repo's description can be about a different repo than its contents.** `cloudflare-vibe` ("UI theme or vibes for Cloudflare") is a full SDK; `DMLog` ("Debug and monitor logs for dark mode features") is an AI-society D&D simulator; `project1` ("Placeholder project repository") is a Z.ai webapp scaffold; `fleet-dashboard-api` is 3 blobs / 555 KB. Read the README.
- **Class methods hide from naive test collectors.** A module-level `test_*` sweep reported 30/30 passing on a suite that declares 71. Collect classes too, or your "all green" is a subset.
- **Mutation-test validators, not just test suites.** `validateStrategy` rejected 3 of 8 corruptions and passed the 4 that matter. Grep for the fields the validator *should* check, then feed each one garbage.
- **Check that documented commands run in a clean clone** — `require('../radio-js/radio.js')` where the sibling repo is absent from a 5,226-repo census.
- Cheap checks worth repeating: `git ls-files -s | grep 160000` + `[ -f .gitmodules ]`; assert `catalog_rows == census_total`; `md5` the *same* command's stdout three times before believing a determinism claim.
