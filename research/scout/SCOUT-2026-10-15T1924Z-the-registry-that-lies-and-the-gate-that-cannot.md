# Scout — 2026-10-15T1924Z — the registry that lies, the distribution-only suite, and the gate that cannot

**Census:** `5,237` public repos / **53 pages**, `sort=full_name&direction=asc`, **`unique_by == rows` PASS (5237/5237)**. 821 forks / **4,416 own** / 16 archived. (The brief's 5,113/52 was 2 days stale — re-derived, never hardcoded.)

**Examined set:** all **91** prior scout files in `research/scout/`, two extraction passes (backticked + bare tokens) → **1,069 own examined / 3,347 unseen own**. Ranked by **own code bytes by extension** minus vendored paths (not tree bytes, not API `size` — which is git history). Top 260 short-listed by API size, then true blob sums fetched from `git/trees/{branch}?recursive=1`. 17 repos cloned.

**Environment:** python3 3.11, node 22.19, gcc 12.2 (+avx512f). No cargo/rustc/julia — Rust findings are static and labelled as such. `vitest`/`wrangler` cannot install, so `plainsong-worker`'s suite was run through a **shim onto `node --experimental-strip-types`** and mutation-tested there.

---

## 1. `quilt-canon-cli` — the best gate in the fleet, mutation-verified end-to-end ★ positive control

**What it is:** a sandboxed FLUX canon-verifier with **proof certificates**. 1,296-line interpreter for a DSL (`canon_verify.fxu`), a 71-paper pinned corpus, a fabric VM with **metered fuel**, and SHA-256 proof certs per paper.

**Why another agent should care — this is the one to copy.** It reproduces the live canon state hash **`0x445185a3a99fd2e7`** in-sandbox from a pinned snapshot (`quilt-live-canon@371e07d`) — the same hash the canon state has carried across wipes. The gate is **two-directional by construction**:

```
$ python3 fleet-canon/lint.py --dir test/fixtures/tier1 --verify-flux
  INFO  flux-verify: proof certs 71/71 recompute clean (fabric module 9f48f433fa9a…)
canon-lint: 27/27 Tier-1 repos curated
canon-lint: PASS (0 failures, 0 warnings)          exit 0
```

**Mutation (one field, one of 71 papers — `408.title` += " MUTATED"):**

```
  FAIL  flux-verify: corpus drift — reference fabric hash 0x4f1cd3622da26592
        != canon target 0x445185a3a99fd2e7 (snapshot tampered or stale;
        regenerate: python3 flux_verifier/corpus/_regen.py --fetch)
canon-lint: FAIL (1 failures, 0 warnings)          exit 1
```

`test/test_flux_verify.py` also exits 1 with `AssertionError: reference fabric drift`. **Restored → exit 0, 18/18 PASS.** Verified in both directions.

What makes it exemplary is the **fuel boundary is measured exactly, not asserted loosely**: `steps=152580`, budget `15258000` = 100×. The suite tests `budget == exact steps` → `OUT_OF_FUEL` **on the last metered op**, and `budget == steps+1` → **HALTs clean with exactly 1 fuel to spare**. That is a boundary asserted from both sides with a receipt. 18 + 9 + 7 = **34 checks, all green**, all runnable with bare `python3`.

**Structural note (minor):** both workflows reference `test/test_canon_lint_hard.py` and `test/fixtures/tier1/` — both exist and both run. The `canon-lint` job is explicitly labelled *"rate-limited sweep is INCOMPLETE, never PASS"*, which is the correct way to ship a job that cannot honestly be green.

---

## 2. `plainsong-worker` — a real edge compiler whose suite cannot see its own headline property ★ NEW CLASS

**What it is:** a zero-dependency Cloudflare Worker compiling **TapScript** notation → **Standard MIDI File** on the edge. 913-line parser + 183-line SMF writer. `plato-nervous`/`tapscript-studio` adjacency makes this the fleet's music spine.

**It genuinely works.** Compiled both shipped examples in a clean clone:

```
harbor-dawn : title="Harbor Dawn"  sections=2 players=4 tempo=60  → 670 bytes
neon-shadows: title="Neon Shadows" sections=2 players=5 tempo=75  → 714 bytes
$ file *.mid → "Standard MIDI data (format 1) using 5 tracks at 1/96"
```

Determinism confirmed: identical `md5` across runs (`80d84490f1ae98830bba3b948256e133`). Velocity humanization is real — 62 note-ons, velocities spanning 47–85 around the declared `vel: 55` / `vel: 65`.

**The defect — a distribution-only suite.** The README states humanization uses *"a deterministic seeded RNG (seed: 42, LCG) so that the same input always produces the same output. This is critical for reproducibility in version control and testing."*

| mutation | output bytes | tests |
|---|---|---|
| baseline | `80d84490…` | 39/39 green |
| drop VLQ continuation bit `0x80 \|` | — | **2 RED** ✅ suite has teeth |
| seed `42` → `43` | `9fa631b3…` changed | **39/39 GREEN** ❌ |
| `SeededRNG.next()` → `Math.random()` | `30d8cc21…` / `35b948a1…` / `646c1d56…` **3 different runs** | **39/39 GREEN** ❌ |

Replacing the seeded generator with `Math.random()` — the exact failure the README calls critical — **produces three different MIDI files and every test still passes.** The suite asserts *statistical shape* (`velocity in range`, `distinct velocities > 1`), never *identity*. `Math.random()` has the same distribution.

**This is a new class for this series: not a vacuous gate, not a fail-open gate — a suite that is statistically correct and epistemically blind.** The fix is one line and is not brittle: assert `bytes(parse(x)) === bytes(parse(x))`. Pinning the known md5 is optional; the self-consistency invariant is not.

**Correction to my own method:** my first clock-entropy mutant wrote `Date.now()` *after* the LCG step, clobbering the state before use — it made `randInt` **constant**, not nondeterministic, so it proved nothing. Discarded; the `Math.random()` mutant is the valid form.

---

## 3. `plato-torch` — a registry that asserts an interface the types don't implement ★ NEW CLASS

**What it is:** **25** training "rooms" (REINFORCE, QLoRA, distillation, contrastive, federated, curriculum, neurosymbolic…) behind one API, *"Pure Python, no torch"*, so it runs anywhere. All 25 instantiate, `feed()`, `predict()` in a clean clone with numpy. 240 tile files / 59,736 bytes persisted through `observe()` — the persistence layer is real.

**The defect.** Three registered rooms do not inherit `RoomBase`. They re-implement `feed`/`train_step`/`predict`/`export_model` by hand — structural typing satisfies the registry at import time and betrays it at call time:

```
fractal      bases=['object']   has_observe=False  has_feed=True  has_train_step=True  has_export=True
refraction   bases=['object']   has_observe=False  has_feed=True  has_train_step=True  has_export=True
deadband     bases=['object']   has_observe=False  has_feed=True  has_train_step=True  has_export=True
wiki         bases=['RoomBase'] has_observe=True   ...                                    (the 4th new room, fine)
supervised   bases=['RoomBase'] has_observe=True   ...
```

Consequence, measured: **3/25 rooms crash with `AttributeError` the moment the base API is called** —

```python
room.observe("state-0", "act_a", "good", agent_id="a1")
# AttributeError: 'DeadbandRoom' object has no attribute 'observe'
```

They also silently swallow `ensign_dir=` / `buffer_dir=` into `**kwargs` and **write nothing anywhere**, and their `export_model()` returns a `Dict` where `RoomBase`'s returns `bytes`. The README's *"Every method shares the same API"* is false for exactly these three.

**A three-way count mismatch hides it:**

| source | count |
|---|---|
| README *"All 21 Presets"* + its table | **21** |
| `src/plato_torch/room_presets.py` (old registry) | **21** |
| `presets/__init__.py` `PRESET_MAP` (live registry) | **25** |
| preset `.py` files on disk | **27** |

`deadband`, `fractal`, `refraction`, `wiki` were added to the new registry and **3 of those 4 are exactly the ones that crash.** The README table omits all four. The documentation is stale in exactly the way that conceals the breakage. Also **3 implemented rooms are unreachable from either registry** — `ghost_injector.py`, `lora_train.py`, `server_room.py`. (`lora_train.py` backs the `'lora'` key, so that one is a name/file mismatch, not a dead file.)

**One line would have caught it:** `assert all(hasattr(c, "observe") for c in PRESET_MAP.values())`.

---

## 4. `bare-metal-plato` — the ceiling is asserted, the ladder is not

**What it is:** 629 lines of C (ESP32/RP2040) giving IoT devices an AI upgrade path through a **5-level "turbo-shell"** — `raw → conditioned → smart → autonomous → ensign` — plus an MCP bridge and a Python embodiment agent. Both C files compile clean under `gcc -std=c11 -Wall -Wextra`. **32 tests, all green, 0.153s.**

**The defect — a one-sided bound protecting a headline claim.** The README's opening sentence is built on the 5-level ladder, and the suite has a test for it:

```python
def test_target_level_never_exceeds_4(self):
    self.assertLessEqual(result["target_level"], 4)     # upper bound only
def test_target_level_increments_by_one(self): ...
def test_cap_levels_has_5_levels(self):
    self.assertEqual(len(self.ns["CAP_LEVELS"]), 5)      # dictionary SHAPE
```

The suite proves the ladder is **named** with five rungs and that upgrades never go above 4. It never proves the **top rung is reachable**. `assertLessEqual(x, 4)` is satisfied by `3`. So:

| | climb 0→? | tests |
|---|---|---|
| baseline | raw→conditioned→smart→autonomous→**ensign** ✅ | 32/32 green |
| `min(cap_level+1, 4)` → `min(cap_level+1, 3)` | raw→conditioned→smart→autonomous→**stuck, `ensign` unreachable** ❌ | **32/32 GREEN** ❌ |

The entire 5-level system's top rung can be deleted and the suite never notices. A second mutation (dropping `and not has_temp` from LED-node detection) **was** caught — so the suite has teeth; the hole is precisely at the headline.

Fix: `assert generate_local_intelligence("d", 3, tools)["target_level"] == 4`.

**Also:** `examples/__pycache__/agent_embodiment.cpython-310.pyc` is **git-tracked** (`.gitignore` has `__pycache__/` but the file predates it or was force-added). Harmless content, wrong hygiene.

---

## 5. `equilibrium-tokens` — five build manifests, one real

**What it is:** a genuinely substantial **3,296-line** Rust crate modelling conversational constraints as navigable surfaces: `rate.rs` (437), `context.rs` (433), `sentiment.rs` (424), `interruption.rs` (342), plus an orchestrator and a RAG vector store. The *idea* — treat the model as frozen territory and navigate it with equilibrium constraints rather than prompt-engineering an oracle — is the most interesting design doc in this batch. 3 integration tests named for real scenarios (`test_fishing_boat`, `test_jazz_band`, `test_symphony_pops`).

**The defect — a manifest cluster where four are phantoms:**

| manifest | declared | reality |
|---|---|---|
| `Cargo.toml` | Rust | ✅ **19 `.rs` files**; CI runs fmt/build/clippy/test |
| `go.mod` | Go 1.21 + testify | ❌ **0 `.go` files** |
| `package.json` | `main: src/equilibrium_orchestrator.js` | ❌ **0 `.js` files**; that path **does not exist** |
| ↳ its test script | `"test": "echo \"See TypeScript tests in tests/\""` | ❌ **exits 0, writes nothing, runs nothing** — and `tests/` holds 3 `.rs` and 0 `.ts` |
| `requirements.txt` | numpy/pytest/pytest-cov/scipy | ❌ the only 3 `.py` files are `examples/`, never tested |

`npm test` here prints a sentence and returns success. That is precisely the "script that exits 0 and writes nothing" failure. The `Makefile`'s 30 targets are honest (all real `cargo` wrappers) — it's `package.json` that lies.

**A stray cross-project tree is committed:** `mnt/c/Users/casey/secret-manager/tests/common/mod.rs` — a local Windows mount path from an unrelated `secret-manager` project, referencing `crate::SecretManager` and `secrets.db`. **No live secrets** (high-signal scan clean) and it is inert boilerplate, but it encodes a private filesystem layout and another project's name in a public repo.

**Two identities for one author in one repo:** `"Casey DiGennaro"` in `Cargo.toml`, `"Casey Gallagher"` in `package.json` (5:1).

---

## Fleet-wide negative findings

- **Canary adoption is zero in all 17 repos examined** — not one of the 17 contains `0x24a555471370b18d` in any form. The canary lives in `substrate-foundation` and is not adopted by any of this newer wave.
- **CI present in 12/17**, absent in 5 (`agent-loop`, `fleet-twin`, `guard2mask-gpu`, `quilt-cell-harness`, `quilt-float`, `recovered-copy-20260824-fleet-ensemble`).
- `architecture.md` … `architecture5.md` in `equilibrium-tokens` — five generations of design doc in one tree, `architecture4.md` (42 KB) being a *"Complete Claude Code Implementation Script"*, i.e. generated output committed as architecture.

## Method notes (carry forward)

- **Assert the exit code without a pipe.** `cmd | tail; echo $?` reports **`tail`'s** status. I nearly recorded a fail-open gate in `quilt-canon-cli` on this. Use `cmd > out 2>&1; echo $?`.
- **A registry is a type assertion — check `__bases__`, not `hasattr` for the four names the interface advertises.** Python's duck typing lets a hand-rolled class satisfy a map that promises inheritance.
- **Count the thing in three places** (README table / registry / files on disk). When they disagree, the delta is where the bug lives — here the 4 undocumented rooms were 3 of 3 broken ones.
- **Assert the bound from both sides.** `≤ 4` never proves `== 4` is reachable.
- **A suite can be statistically correct and still blind.** Seeded-vs-unseeded RNG is invisible to shape assertions; `Math.random()` has an identical distribution. Ask what a mutation *cannot* change the outcome of.
- Compiled binaries land mode 644 and need `chmod +x`; "Permission denied" is not a build failure.
