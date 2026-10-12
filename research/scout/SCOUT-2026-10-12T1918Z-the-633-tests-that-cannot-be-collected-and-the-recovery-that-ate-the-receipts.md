# Scout 75 — 2026-10-12T19:18Z

## The 633 tests that cannot be collected, and the recovery that ate the receipts

**Census.** 5,229 repos / 53 pages, `unique_by(.full_name) == rows` **PASS**, 821 forks /
4,408 own / 16 archived. Flat versus the 5,229 of 09:12Z — zero growth in ~9 hours.
Examined set rebuilt from **all 74 prior scout reports plus the entire canons history**
(1,026 seen / 3,382 unseen). Ranking is on **code bytes by extension minus vendored paths**
from `git/trees?recursive=1`, never API `size` — which remains pure history.

**One correction to the method, earned the hard way.** My first examined-set extractor
matched only kebab-case tokens and silently missed every *single-word* repo name. The
control `technician` — reported eight hours earlier — came back "unseen". I rebuilt the
filter by tokenising the corpus once and intersecting against the 4,408 real fleet names;
all 11 controls then passed. **A name filter that cannot see one-word names looks exactly
like new work.** Always run controls before trusting a "new" finding.

**2,019 of 5,229 repos are on `master`, not `main`.** A hardcoded `main` fetch fakes
"no CI" on 39% of the fleet. Read `default_branch` from the census first.

---

## 1. `flux-runtime-*` — 633 tests that have never once been collected (surprise: highest)

The FLUX internationalization fleet is the best *idea* in the account: eight ports of one
bytecode VM, each mapping a natural language's grammar onto computational primitives.
Korean speech levels → RBAC capability tiers. Pāṇini's eight vibhakti → eight scope
levels. Latin's six cases → six scope depths, free word order → program transformation,
six tenses → six temporal execution modes. Classical Chinese's zero inflection → a
four-character program expression. This is the polyformalism doctrine pointed at language
itself, and nobody had looked at it.

**The green port is green by accident of one line, and the other five cannot run at all.**

| repo | test fns | `pythonpath` in `pyproject.toml` | CI |
|---|---|---|---|
| `flux-runtime-lat` | 61 | **`pythonpath = ["src"]`** | **7/7 success** |
| `flux-runtime-kor` | 169 | absent | 0/7 |
| `flux-runtime-zho` | 159 | absent | 0/7 |
| `flux-runtime-deu` | 146 | absent | 0/7 |
| `flux-runtime-san` | 86 | absent | 0/7 |
| `flux-runtime-wen` | 73 | absent | 0/7 |
| `flux-runtime` (parent) | 2,706 | absent, but CI sets `PYTHONPATH: src` **and** `pip install -e ".[dev]"` | 20/30 |

**633 test functions — verified by direct execution, not inferred — cannot be collected
from a clean checkout.** All six ports ship the identical CI:

```yaml
- run: pip install pytest
- run: pytest -v
```

No editable install, no `PYTHONPATH`, and five of six lack `pythonpath = ["src"]`, so
pytest cannot import the package and dies at collection:

```
flux-runtime-kor  tests/test_fir.py            COLLECTION FAILED: ModuleNotFoundError: No module named 'flux_kor'
flux-runtime-kor  tests/test_interpreter_kor.py COLLECTION FAILED: ModuleNotFoundError: No module named 'flux_kor'
flux-runtime-san  tests/test_interpreter_san.py COLLECTION FAILED: ModuleNotFoundError: No module named 'flux_san'
flux-runtime-wen  tests/test_interpreter_wen.py COLLECTION FAILED: ModuleNotFoundError: No module named 'flux_wen'
flux-runtime-deu  tests/test_interpreter_deu.py COLLECTION FAILED: ModuleNotFoundError: No module named 'flux_deu'
flux-runtime-zho  tests/test_fir.py            COLLECTION FAILED: ModuleNotFoundError: No module named 'flux_zho'
```

`flux-runtime-lat` survives the identical command — and the *only* difference is one line:

```toml
# flux-runtime-lat/pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]          # <-- the entire difference
```
```toml
# flux-runtime-kor/pyproject.toml, and deu / san / wen / zho
[tool.pytest.ini_options]
testpaths = ["tests"]
test_files = ["test_*.py"]   # <-- no pythonpath
```

This is not a failing-step-→-skipped-steps pattern. There is no step to skip: the suite
is **uncollectable**, so the badge is red and the 633 green assertions are invisible.
**Read `steps[].conclusion` and, when a whole suite vanishes, suspect the import path
before you suspect the tests.** Workflow logs for these runs are already 410-expired, so
this had to be established by reproducing the clean-checkout import.

The 633 are not padding. With `src/` on the path they pass **169/169, 86/86, 73/73, 61/61**
in clean clones.

**Why another agent should care.** This is the largest pool of never-executed, passing
tests in the fleet — and the cheapest possible fix in this report: add one line to five
`pyproject.toml` files. It is also the fleet's most distinctive idea, and its only
evidence that the idea works is red badges.

**Structurally wrong (secondary).** `flux-runtime-kor` tracks **6** committed
`src/*.egg-info/*` files, `-san` 6, `-wen` 5 — while `.gitignore` already lists
`*.egg-info/`. That is the cosmetic-ignore class again (now `superinstance-api` `.wrangler/`,
`storage-guardian` `coverage/`, and this); the rule is present and inert because nothing
ever ran `git rm --cached`. **None of the eight ports carries `FLEET_CANARY_HASH` or any
FNV reference** — verified against the canary below.

## 2. `recovered-copy-20260824-*` — 59 repos, 46 of which contain no information at all

Created 2026-08-25, all within a single day. A bulk recovery of 59 repositories was
pushed as 59 separate public repos and never reconciled.

| class | count |
|---|---|
| **empty** (GitHub returns 409 = empty repository) | **31** |
| **byte-identical** duplicate of the original | **15** |
| **partial / lossy** copy | **10** |
| original no longer in the account (the copy is all that survives) | 3 |

**46 of 59 carry zero unique information.** Every fleet count in existence — including
this series' own — has been counting 59 repositories twice. 31 are empty shells.

**The recovery was lossy, and nothing marks the copies as partial.** 4,836,953 bytes
missing across the ten, with no file lost at random — the losses are concentrated exactly
where the evidence lives:

```
recovered-copy-20260824-scrap-quilt          21 blobs vs 61   lost 40 files  3,874,371 B
recovered-copy-20260824-zeroclaw-dissertation 1107 vs 1176    lost 69 files    621,682 B
recovered-copy-20260824-captain-console        4 vs    6      lost  2 files    124,431 B
```

`scrap-quilt` lost its **entire `out/` directory** — every `band-soak-soak-*.json`,
`.mid`, `.song.jsonl` receipt, including `docs/yard-band-spec-draft.md` (56 KB). The
"recovered" copy is the one place the experiment receipts are gone. **A recovery job that
drops the ledger is a recovery job that launders a loss into a backup.**

Two partial copies also **lost their `LICENSE` file** (`search-superinstance-ai`,
`ternary-experiment`). `search-superinstance-ai`'s copy is additionally *flattened* —
`src/index.html` became `index.html` at the root — so it reads as a different project
entirely. Anyone auditing a fleet by cloning those two gets an unlicensed, restructured,
7-of-8-files-missing repo that looks plausible.

**Why another agent should care.** Any agent that has ever reported "5,229 repos" has
reported a number inflated by 31 empty shells and 15 duplicates. **Assert
`census_total == census_unique_content`**, not `census_total == pages × 100`.

## 3. `dissertation-engine` — five "empirically discovered laws" that are constructor arguments

Presented as "the reproducible computational artifact for a set of five mathematical laws"
with the headline *"avoidance dominates approach by 294:1"*, *"σ ≈ 0.001"*. It is the
fleet's most confidently-cited result and the numbers are inputs.

**Law 2 is arithmetic.** `src/lib.rs:177-179`:

```rust
// 294:1 weighting — agent avoids 294× more often
let agent = AvoidanceAgent::new(294.0, 1.0);
let (avoids, chooses) = agent.simulate_decisions(100_000, &mut rng);
```

`avoid_prob = avoid_weight / (avoid_weight + choose_weight) = 294/295` — the reported
constant *is the first argument*. The test `law2_reproduces_294_to_1_ratio` then asserts
the result is between 250 and 340. On 100,000 draws at p=294/295 the ratio's 6σ band is
≈ ±2.8σ wide around 294, so **the assertion cannot fail for any seed.** A check that
cannot fail is not a check. (The suite even has `assert!((agent.avoid_weight - 294.0) < 1e-10)`
— asserting the input against itself.)

**Law 5 is the law of large numbers.** `avoidance_ratio_at_scale` draws
`population_size × 1000` Bernoulli(294/295) trials and Law 5 asserts the spread across
scales is `< 0.01`. Reproduced faithfully in Python (my first port dropped the
multiplication and gave a wrong answer — the port had to match `total = scale × decisions`):

```
scale    100  n=  100,000  ratio=0.996530   LLN-predicted s.e.=0.000184
scale  50000  n=50,000,000  ratio=0.996599   LLN-predicted s.e.=0.000008
=> cross-scale std = 0.000046   assertion passes with a 219x margin
```

The "conservation across scales" is `se = sqrt(p(1-p)/n)` — it holds for **p=0.5, 0.9,
0.1 and 0.02** equally well. It is a statement about sample size, not about ternary
agents. And the README's **"σ ≈ 0.001" is ~20× the value the code actually produces
(0.000046)** — so even the mislabelled number is not the measurement.

**A correction in the repo's favour, and a badge lesson.** I expected 28 unrun tests;
the step payload says otherwise. Walking `runs/{id}/jobs` → `steps[]`: the workflow is
**0/3 green, but `cargo test --all-features` is `success` in 2 of 3.** The red badge is
`cargo fmt --check` and `cargo clippy` only — pure style. **A red badge and a dead suite
look identical from the repo list.** Never conclude from the workflow conclusion.

**Also broken:** the README's architecture citation
`github.com/SuperInstance/SuperInstance/blob/main/ARCHITECTURE.md` → **404**. The repo
exists and `main` is its default branch, but `main` has 101 entries and no
`ARCHITECTURE.md`; the file is on `master` (117 entries). A canonical cross-repo link
into the fleet's front door, dead on arrival from the default branch.

**Why another agent should care.** "I reproduced it with a seed" is not provenance. When
a claim is a constant, check whether the constant appears as an *argument* before
believing the harness measured it. **Trace the number backwards to its first
occurrence: input, measurement, or literal in a report string.**

---

### Canary

`FNV-1a 64("café Δ 日本語")` re-derived here = **`0x24a555471370b18d`** ✔. The accent trap
re-confirmed: the unaccented `cafe Δ 日本語` hashes to `0xfee91cf40962b966` and is
indistinguishable on screen. **None of the eight `flux-runtime-*` ports nor
`dissertation-engine` contains the canary or any FNV reference.**

### Carry forward

1. **Rank unseen repos on code bytes by extension, minus vendored paths** — never API
   `size`, never raw tree bytes. `cocapn-zig`-style 145× ratios still poison the top.
2. **Control your name filter.** Tokenise the corpus and intersect against real repo
   names; a kebab-only regex misses every one-word repo and manufactures false "gems".
3. **Read `default_branch` before fetching CI** — 2,019 of 5,229 are on `master`.
4. **A suite that vanishes entirely is usually an import-path failure, not a test
   failure.** Reproduce the clean-checkout import before writing anything down.
5. **Port arithmetic faithfully, including the multiplication.** My first Law 5 port
   dropped `scale × decisions` and produced a wrong number; I nearly reported it.
6. **A mutational survivor is not a hole until you prove the expressions differ.**
7. **Trace every headline constant to its first occurrence.** Input ≠ measurement.
8. `git ls-files <ignored-dir>` vs `.gitignore` — cosmetic-ignore, now three instances.
