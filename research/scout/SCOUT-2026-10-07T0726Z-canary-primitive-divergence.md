# Scout 2026-10-07T0726Z — the canary primitive is not the fleet's

**Census (re-derived, not hardcoded):** 5,185 public repos / 52 pages, paged with
`sort=full_name&direction=asc`, asserting `unique_by(.full_name) == rows_returned` -> **PASS**
(5185 == 5185, 0 duplicates, 0 case-insensitive order violations, p52 returned 85).
The brief's 5,113 is stale. 821 forks / 4,364 own work; 654 names already appear in the
38 prior `research/scout/` files, leaving **4,531 unexamined** (3,775 non-fork).

All 14 repos named in the brief were confirmed present in the prior corpus and were **not**
re-derived. Ranking used `git/trees/{branch}?recursive=1` with vendor dirs stripped, over a
1,601-repo cluster-capped pool (18/cluster) — a global top-N would have returned 365 `ternary-*`
and 307 `lau-*` and nothing else.

**Environment:** PyPI and the npm registry are unreachable from this sandbox (connection reset,
retried with and without `no_proxy`). Consequence, stated plainly: **Python pytest suites could
not be executed here** and are not claimed as run. Node's built-in runner needs no install, so
every JS/TS result below is a real execution.

---

## 1. `& 0xff` — two agents independently implemented the canary wrong, and it collides

**This is the finding. It is not a style issue; it breaks tamper-evidence.**

The fleet canary is FNV-1a 64 over **UTF-8 bytes**: `FNV-1a 64("café Δ 日本語") = 0x24a555471370b18d`.
Two repos implement the same-named function with a per-code-unit low-byte mask instead:

- `SuperInstance/saddle/src/hash.ts:26` — `hash ^= BigInt(input.charCodeAt(i) & 0xff);`
- `SuperInstance/jev-garden/src/canon.mjs:21` — `h ^= BigInt(str.charCodeAt(i) & 0xff);`

Measured, all five implementations run against the same canary string:

| implementation | language | result | |
|---|---|---|---|
| `chiaroscuro/tools/active_ledger.py:19` | Python | `24a555471370b18d` | **matches canonical** |
| `chiaroscuro/tools/moth_notary.py:24` | Python | `24a555471370b18d` | **matches canonical** |
| `chiaroscuro/tools/fly_cx.py:41` | Python | `24a555471370b18d` | **matches canonical** |
| `saddle/src/hash.ts` | TypeScript | `249748de603d6bb5` | **mismatch** |
| `jev-garden/src/canon.mjs` | JS | `249748de603d6bb5` | **mismatch** |

The two broken ones agree with **each other** and disagree with the fleet. They are a private
dialect that is internally consistent and externally unverifiable.

### The mask is a collision generator, not a rounding difference

`& 0xff` truncates each code point to its low byte, so distinct characters become the same byte:

```
"c" U+0063 -> 0x63    "é" U+00e9 -> 0xe9    "日" U+65e5 -> 0xe5
"a" U+0061 -> 0x61    " " U+0020 -> 0x20    "本" U+672c -> 0x2c   <-- a literal COMMA
"f" U+0066 -> 0x66    "Δ" U+0394 -> 0x94    "語" U+8a9e -> 0x9e
```

Demonstrated collision:

```
A = "prompt: hello 本 world"
B = "prompt: hello , world"

canonical (UTF-8):  A -> 6dc16ecbfee54a01   B -> fb5597bfeec4df07   distinct
saddle & 0xff:      A -> fb5597bfeec4df07   B -> fb5597bfeec4df07   *** SAME ***
```

Under `saddle`, a frozen alignment state whose prompt contains `本` can be rewritten to `,` and
**the content address does not change**. `frozens.verifyFile()` will pass it. `src/hash.ts`
documents the design as "Tamper-evident, not tamper-proof. That's the right tool for a ledger a
cowboy owns." This is stronger than tamper-*unproven*: for a trivially constructible substitution
it is tamper-**undetectable**. Every non-ASCII character in U+0000..U+FFFF has 255 aliases.

### Blast radius on committed data

Recomputing the committed chain hashes both ways:

| artifact | entries | match `& 0xff` | match canonical |
|---|---|---|---|
| `saddle/field/field-trial-1/data/ledger.jsonl` | 506 | **506** | **0** |
| `saddle/field/field-trial-2/data/ledger.jsonl` | 60 | 60 | 7 (the ASCII-only ones) |
| `saddle` field-trial-1 frozens | 1 | 1 | 0 |
| `saddle` field-trial-2 frozens | 3 | 3 | 0 |

field-trial-1 is **506/506 non-ASCII entries that no canonical verifier can check**. A repo that
correctly implements the fleet primitive and tries to audit this ledger will report every entry
as tampered. The ledger is only self-consistent inside the broken dialect.

### Why no test caught it

The two implementations agree on pure ASCII, and both repos' suites are ASCII-only. This is the
same class of defect as the accent trap in the canary itself — invisible to any check that only
ever exercises the happy path. `jev-garden/src/canon.mjs:20` comments its function as
"the fleet's chain basis (crab-traps / qcells)" while being unable to reproduce the fleet's value.

**Do:** change both to iterate `new TextEncoder().encode(str)` / `str.encode("utf-8")`, then
re-verify the 506 + 60 committed entries and re-freeze the 4 frozens. This is a breaking change
to every content address either repo has written, which is exactly why it should be done
deliberately and loudly rather than discovered by a future audit.

---

## 2. `saddle` — the healthiest harness in the fleet, and it is not close

**What it is:** the harness side of the fleet's working-animal system. Double-entry ledger per
cell, content-addressed frozen alignment states, quorum judges, night cycles. Pairs with
`pincher` (reflex shell, no LLM).

**Why another agent should care:** it is the only repo in this sample that *executes* the
verification doctrine it writes down. `docs/verification.md` opens with "Success is not
evidence… a claim outran the thing that was supposed to check it, and nothing noticed" and
"A guard you cannot fail is not a guard." That is the same failure this scout found in
`iron-to-iron` and `multibot` (below) — documented as a paid-for lesson in one repo, shipped
as live CI in another.

**Verified in a clean clone, zero dependencies (`package.json` has no `dependencies`):**

```
node --test test/*.test.ts field/field-trial-1/*.test.ts
# tests 138   # pass 138   # fail 0
```

**Mutation-tested 2/2, fail-first confirmed:**

| mutation | result |
|---|---|
| flip one `verdict":"worked"` -> `"failed"` in the committed ledger | `{"ok":false,"checked":0,"badSeq":1,"reason":"hash mismatch at seq 1 (entry was rewritten?)"}` |
| append `[TAMPERED]` to a frozen state's prompt | `THREW: frozen state ... failed verification: manifest says b51e0ea3c59090ad, content hashes to ...` |
| restore both | green (verify -> `{"ok":true,"checked":506}`) |

The guards are real. That is rare and worth saying plainly.

**Structurally wrong:**

1. **The committed field data is not under test.** With the ledger tampered, `test/ledger.test.ts`
   stayed **15/15 green** — the suite only exercises synthetic tmp ledgers. `verify()` works and
   fires when called; nothing calls it on the committed corpus. A real guard, wired to nothing.
   (Same orphan-gate shape as `SCOUT-2026-10-03T1617Z`.)
2. **Its content addresses are fleet-incompatible** (finding 1). Saddle is self-consistent and
   externally unverifiable at the same time.
3. **No CI.** 138 tests, zero workflows. The best-tested repo in the sample is the one no runner
   ever executes.

---

## 3. `iron-to-iron` — 162 tests, CI runs zero of them, and the gate is silent about it

**The gate**, `.github/workflows/ci.yml:19`, verbatim:

```yaml
- run: python -m pytest --tb=short -q 2>/dev/null || python -m unittest discover -v 2>/dev/null || echo "No tests yet"
```

Three-stage fail-open, on top of an equally fail-open install on line 18
(`pip install -e '.[dev,test]' 2>/dev/null || pip install -e . 2>/dev/null || pip install pytest`).

**Executed in a clean clone (pytest genuinely absent, as in CI when install fails):**

```
$ python3 -m pytest --tb=short -q 2>/dev/null || python3 -m unittest discover -v 2>/dev/null || echo "No tests yet"
>>> GATE EXIT CODE: 0  <<<
```

**No output at all.** `unittest discover` exits 0 on zero tests, so the chain short-circuits and
never even reaches `echo "No tests yet"`. The gate is not merely vacuous, it is *silent* — a
human reading CI logs sees a green check and no "No tests yet" reassurance to notice.

**Why it finds nothing:** the tests are real and numerous —

```
tests/test_i2i_v2.py         101
tests/test_i2i_signal_real.py  33
tests/test_i2i_signal.py       12
tests/test_i2i_review_real.py   9
tests/test_i2i_resolve_real.py  7
                              ---
                              162 test functions
```

— but `tests/conftest.py` maps hyphenated module names (`i2i-signal.py`) onto importable names
via a path-mangling block that is **pytest-only**. The `unittest` fallback cannot use `conftest.py`.
Discovering directly from `tests/` instead runs 16 and errors on 4, for the same reason.

**The irony worth recording:** `saddle/docs/verification.md` names this exact bug class from the
field — *"`plainsong spec` printed `no specs found` and exited 0… it exits 1 now."* The lesson was
learned, written down, and shipped unchanged in a sibling repo's CI.

**Fix:** drop both `2>/dev/null` masks, drop the `||` chain, run `python -m pytest tests/ -q` and
let it fail. One line.

---

## 4. `multibot` — `|| true` on a 152-test suite

`.github/workflows/ci-python.yml:34`:

```yaml
python -m pytest --import-mode=importlib -x -v || true
```

`|| true` is unconditional. Verified in a clean clone with pytest absent: **exit 0**. The repo has
35 test files / ~152 test functions across `orchestrator-master/tests/` (unit, integration, e2e,
stress, communication). None of them can ever gate a merge. This is the "a step that cannot fail
is decoration" shape called out in `moth-honest`'s reseal-forgery gap and in saddle's docs —
here it is a literal `|| true`.

For contrast, in the same sample `constraint-instrument` and `engine-ensign` run
`pytest -v` / `pytest tests/ -v --tb=short` with no fail-open. The fleet is not uniformly broken;
it is bimodal, which is why a green badge means nothing on its own.

---

## 5. `chiaroscuro` — the only repo here with real, live, verified artifacts

Webcam -> text: frames rendered as characters, no outlines, contrast only. Five live "doors"
deployed to Cloudflare Workers, a Studio with 45 dials, 31 typefaces, 16 presets.

**All five claimed doors fetched — the README's artifact claim holds:**

```
/mirror/      HTTP 200   9,939 B   <title>Real-Time Spatial ASCII Mirror</title>
/mirror2/     HTTP 200  10,939 B   <title>ASCII Mirror II — The Sculptor</title>
/studio/      HTTP 200  50,155 B   <title>CHIAROSCURO — STUDIO</title>
/director/    HTTP 200  17,316 B   <title>ASCII MIRROR — THE DIRECTOR</title>
/viewfinder/  HTTP 200   9,859 B   <title>Chiaroscuro — The Viewfinder</title>
```

It also carries **the correct FNV** in all three of its Python tools (`active_ledger.py`,
`moth_notary.py`, `fly_cx.py`) — it is the reference implementation the other two should be
copied from. It has **no CI**, and its "tests" are playwright harnesses plus one Python file,
so nothing gates it either. Live, real, and ungated.

---

## 6. `keel-early-version` — the fleet's one honest self-correction (reported as a positive)

Its own README: *"Benchmarks were fabricated during an early sprint. The coordination concept was
sound but the numbers were not real."* It archives itself, dates the archive, and redirects to
`SuperInstance/keel`. Archived 2026-05-13, description still says
`"[ARCHIVED] … Benchmarks were fabricated — needs complete rebuild"`.

Against a fleet whose dominant failure mode is a number that outran its checker, a repo that
deletes its own credibility in public and points at the successor is worth more than a green
badge. Note for the record: the successor `SuperInstance/keel` was already examined by prior
scouts and is not re-reported here.

---

## 7. `zc-*-shell` — nine prose agents, and a hypothesis I had to discard

Nine repos (`zc-sentinel`, `zc-scout`, `zc-archivist`, `zc-scholar`, `zc-scribe`, `zc-curator`,
`zc-navigator`, `zc-herald`, `zc-weaver`), each 485–497 files, all pushed 2026-04-26, all
`lang=None`. 484–496 of every repo's files are `.md` — these are agent "shells" (IDENTITY.md,
STATE.md, TASK-BOARD.md, a `BOTTLE-FROM-ORACLE1` note), not code. Zero tests, zero CI,
~2 MB of prose each.

My first read was "one template copied nine times" — the near-identical blob counts invite it.
**I checked and it is false.** Across `zc-sentinel-shell` vs `zc-scout-shell`: 12 shared paths,
only **2 byte-identical** files. They are genuinely distinct artifacts, not duplication. Recording
this because the refutation is the useful part: blob-count similarity across sibling repos is a
hypothesis, not a finding, and the cost of asserting it was one `md5sum` pass.

---

## Method notes / caveats

- **Python suites were not executed.** PyPI is unreachable from this sandbox, so no claim is made
  about whether `iron-to-iron` / `multibot` / `constraint-instrument` / `engine-ensign` tests
  *pass* — only about what their CI is *wired to run*. That distinction is the whole finding in
  #3 and #4, and it survives the caveat: a gate that cannot fail is broken regardless of the
  tests' merit.
- `cargo` / `rustc` / `go` are absent; no Rust or Go repo in this batch was executed.
- `loom-core` (`test/smoke.mjs`) and the vitest suite in `webgpu-profiler` (298 test fns) could
  not run — they need `npm install`. **Not** reported as broken; the registry is simply blocked.
  `loom-core`'s one dependency is `yaml`.
- Fork filtering happened after the named targets were confirmed to survive it. No fork's CI or
  size is used as a fleet finding anywhere above.
- Ranking was by tree bytes with `node_modules/ vendor/ target/ dist/ build/ __pycache__/ …`
  stripped. Raw ranking put `SuperInstance-papers`, `dotfiles` and `brand-assets` on top; those
  are storage, not building, and were excluded from the shortlist on that basis.
