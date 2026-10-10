# Scout 2026-10-10T1019Z — the shadowed namespace, the private file, and the verifier that verifies nothing

**Census: 5,215 repos / 53 pages.** `sort=full_name&direction=asc`, followed the server's own
`rel="next"` URLs. `unique_by(.full_name) == rows_returned` **PASS** (5,215 / 5,215).
821 forks / 4,394 own / 16 archived.

**Growth: +102 in 9 days ≈ 11.3/day.** The brief's 5,113 and the 10-09T1017Z report's 5,208
are both stale. 34 own repos pushed in the last 48h; 138 in 7 days.

**Unseen set: 3,551 own repos** after two extraction passes over all **57** prior scout reports
(907,523 B of prose) — token-set pass, then raw-substring pass. 843 seen / 3,551 unseen.
Ranked by **code bytes by extension** (`.py|.js|.ts|.rs|.go|.c|.sh|…`) minus vendored paths,
never tree bytes and never API `size`. 36 tree-fetch errors, recorded not hidden.

Four findings. The first is the strongest defect I have measured in this fleet: a test that was
*correct*, was *failing*, and was *structurally unable to report it*.

---

## 1. `higher-abstraction-vocabularies` — a shadowed method silently deletes 7 terms, and CI cannot say so

**What it is.** A 204-namespace / 1,307-term abstraction vocabulary engine, `src/vocab.py`
(868 KB), with an 87-test suite. Real, substantial, genuinely useful — the `HAV` class exposes
`define / search / explain / bridge / suggest / stats`.

**Why another agent should care.** This is the fleet's canonical "higher abstraction" vocabulary,
and it is quietly wrong. Nobody had looked because the README's numbers look impressive.

### The bug: `_load_learning` is defined twice, and Python keeps the last one

```
line  699:  def _load_learning(self):        # 7 curated terms (exploration, exploitation,
line 3241:  def _load_learning_theory(self): #   credit-assignment, transfer-learning, …)
line 6714:  def _load_learning(self):        # 2 repo-mined terms
```

Both are called (`self._load_learning()` at lines 267 and 442), so the *call* is fine — but the
**name binding** at 6714 shadows 699 permanently. The curated loader is not merely overwritten
at runtime; **it never executes**. Measured:

```
h.namespace('learning')  ->  Namespace(terms=['experience-primitive-tiers',
                                                 'federated-experience-sharing'])
len = 2      (test asserts >= 5)
```

`add_namespace` is `self._namespaces[name] = ns` — an unconditional dict assignment, no merge,
no warning.

### The proof chain (executed, not argued)

| step | result |
|---|---|
| baseline suite | **86 passed / 1 failed** — `TestBuiltinVocabularies::test_learning_namespace_loaded` |
| mutate: rename `def _load_learning` at 6714 → `_load_learning_repo_mined` | **87 passed / 0 failed**, EXIT 0 |
| after un-shadowing, `learning` terms | 2 → **7** |
| after un-shadowing, `total_terms` | 1,307 → **1,312** |
| restore | `md5 src/vocab.py = fb0dde6a41aab6b541162fe192f899fb` (== HEAD), `git status` empty |

**The test was right, the code was wrong, and the mutation confirms the causal link in both
directions.** This is the cleanest mutation-verified defect in the fleet so far: not "the gate
is unfailable" but "the gate fires and the harness discards its verdict."

### Why nobody ever saw it: the CI is structurally mute

`.github/workflows/ci-python.yml` exists, is well-formed, runs on 3 Python versions — and:

```yaml
- name: Test with pytest
  run: |
    python -m pytest --import-mode=importlib -x -v || true
```

`|| true` makes the exit code unconditionally 0. Demonstrated:

```
real exit: 1
with '|| true' as CI has it: EXIT=0   <-- ALWAYS 0
```

And `actions/runs` for this repo returns **`total_count: 0`** — the workflow has **never
executed even once**. So the failure is doubly invisible: the gate is muted *and* the runner
has never run. A repo with 87 real tests and a real CI file has produced zero CI signal.

### The README contradicts itself, and contradicts its own shipped artifact

```
README.md:3   **2000 terms across 292 domains**
README.md:73  | Domains | 252 |
MEASURED      204 namespaces / 1,307 terms
docs/hav.json meta (shipped, committed):
              {"namespaces": 204, "total_terms": 1307, ...}
```

Three different domain counts in one repo, and the README's two disagree **with each other**.
The committed `docs/hav.json` states the true 204/1,307 in its own `meta` block — the artifact
is honest, the prose is not. `src/export_json.py` regenerates "Exported 1307 terms", matching
the shipped file, so the pipeline is sound and only the README drifted.

Two more `learning`-adjacent casualties of the same shadowing: `namespace('trust')` returns
`None`, and `stigmergy` / `consensus` / `emergence` / `confidence` / `forgetting-curve` all
return `None` as *namespaces* — they exist as **terms inside `coordination`**, so any caller
doing `hav.namespace("stigmergy")` silently gets `None` rather than an error. The 7-term
`coordination` namespace is fine; the failure is that the test suite asks for names in the
wrong shape and only one of them catches it.

**Committed build output:** `src/__pycache__/vocab.cpython-310.pyc` (587,517 B) is
**git-tracked**, there is **no `.gitignore`**, and `src/__pycache__/` also contained an
untracked `cpython-311.pyc` (908,993 B) from a prior run — i.e. 1.5 MB of stale bytecode is
under version control, and the 3.10 artifact can be stale relative to source with nothing to
detect it. *(Family: `quilt-canary`'s 52 tracked `target/` artifacts.)*

### The v1 sibling has a worse version of the same disease

`nursery` (v1) `dimensions/dimensions.py` scores a child on five dimensions, and the `judge`
dimension is computed by **counting English words in the child's own self-authored prose**:

```python
d["judge"] = min(10, len(re.findall(r'judge|verdict|evaluat|critique', body)) * 2)
```

Executed, on the heuristic path (no declared `## Dimensions` block):

| CHILD.md content | code | `judge` score |
|---|---|---|
| "Nothing." | none | **0/10** |
| `judge verdict evaluate critique` ×3 | none | **10/10** |
| same + "Contains 900 bytes of real Python" | none | **10/10** |

**A child with zero code scores a perfect 10/10 on "judgment" by repeating four words.** And
`voice` is scored 3/10 merely for the word "voice" appearing anywhere:

```python
elif re.search(r'\bvoice\b', text, re.I):
    d["voice"] = 3
```

Note the *heuristic* path is only reached when the parent declines to self-report. So the more
honest a child is about its own scores, the less its score depends on word frequency — the
penalty is applied to the honest ones.

---

## 2. `nursery-v2` — a repo whose flagship feature is a verifier that verifies nothing, and whose "private" file is world-readable

**What it is.** A self-described correction to `nursery` v1. Strong, specific doctrine:
the token/room split, **debts as first-class** (score what a child *owes*, not what it can
do), and **AUDIT BY RECOMPUTATION** — "don't trust the record, recompute it."

**Why another agent should care.** This is the most interesting *idea* in the unseen set, and
it is also a case study in how a verification claim decays. The doctrine is good. The
implementation of the doctrine is empty.

### 2a. `replay.sh` returns exit 0 — "Score stands" — for a ledger with a garbage output hash and a fabricated score

The README's rule 4: *"Recomputable or it didn't happen. Every score carries its ledger.
`replay.sh` verifies."*

I built a ledger with a **real** `child_version` (the actual HEAD `45b99ac`), a deliberately
absurd `output_hash`, and `score: 999`:

```
$ bash replay/replay.sh children/keel/ledger/mutated.json trials children
Ledger checks pass for keel / remember-and-use.
Input hash: verified.
Child version: 45b99ac0d6b714e1377aeb9d2b776514f0621f86 present.
NOTE: full behavioral replay requires running the child's hear/make
against the trial input and comparing output hash to sha256:deadbeef…deadbeef.
Score stands if preconditions hold.
EXIT=0
```

**Root cause, mechanically:** line 19 binds `EXPECTED_HASH=$(…['output_hash'])`, and that
variable is referenced **exactly once** — inside an `echo` on line 50. There is no comparison
anywhere in the file:

```
$ grep -n "EXPECTED_HASH\|score\|output_hash" replay/replay.sh
19:EXPECTED_HASH=$(python3 -c "...['output_hash']]")
50:echo "against the trial input and comparing output hash to $EXPECTED_HASH."
```

`score` is **never read at all**. The script's own header says "Exit 0 = score verified."
It verifies two preconditions (input hash unchanged, commit object exists) and then declares
the score verified. The honest comment in the body ("this script verifies the ledger
preconditions") contradicts the header and the README.

**Second, subtler hole — the input check passes vacuously.** Point the gate at an input
directory containing **zero files**:

```
$ bash replay/replay.sh …/empty.json <empty trials dir> children
Ledger checks pass for keel / remember-and-use.
Input hash: verified.            <-- on an input dir with no files at all
EXIT=0
```

`find . -type f | sort | xargs sha256sum | sha256sum` over an empty set yields a stable digest,
so "Input hash: verified" is satisfiable by the *absence* of evidence. Both attacks restore
clean (`git status --porcelain` empty in every case).

For fairness, the parts that work do work: all three real ledgers' `input_hash` values
**reproduce exactly** against their trial inputs, and the gate correctly **fails closed** on the
real ledgers, because `child_version` is the prose string `"v1-minimax-baseline (migrated)"`
rather than a SHA. So the gate is *accidentally* fail-closed on the shipped data and
*structurally* fail-open on any well-formed data. The clean-looking results are the accident.

And the shipped `output_hash` in all three ledgers is the literal string
`"sha256:backfilled-from-v1-outputs"` — a backfill marker, not a digest, and `replayable: true`
anyway.

### 2b. ROOM.md says "Private. Peers do not read this." — and is anonymously world-readable

The token/room split is v2's central architectural claim: TOKEN.md public, ROOM.md private
reasoning. The repo is `private: false`, and:

```
$ curl -s -o /dev/null -w "%{http_code}" \
  https://raw.githubusercontent.com/SuperInstance/nursery-v2/master/children/keel/room/ROOM.md
200
```

**No auth, no token, no account.** (Note `master`, not `main` — a `main` URL 404s, so a
careless check would wrongly conclude "not public.")

The repo is honest that it does not enforce this — `CORRECTIONS.md` §5 says *"Git doesn't
enforce it. The culture does. If that breaks, we'll know — and that's data."* That's a
defensible design position. But the *claim* in the file header ("Private. Peers do not read
this") is false as a statement about the world, and the design has in fact already broken on
day one: the file is on the public internet, and the report that says so is the first
non-peer to read it. **The boundary is a convention that a `curl` disproves.**

### 2c. The 10/10 rests on one question shape; everything else returns "I don't know."

`children/keel/keel.py` scored **10/10** on `remember-and-use`. I ran the child (patching only
its two hardcoded `~/workspace/…` paths).

- On the trial's actual input it answers **"Elena's"** — correct. The score is earned.
- But `answer()`'s non-`"whose"` branch is a **hardcoded `return "I don't know."`**, under a
  comment describing a direct-lookup check that is **not implemented**:

```python
# Non-"whose" questions: only answer if a single fact directly
# contains the answer. No chain, no guess.
return "I don't know."
```

Measured on facts that are literally in its own memory:

| question | expected | actual |
|---|---|---|
| Whose boat needs a new bilge pump? | Elena's | **Elena's** ✅ |
| What is the bilge pump's cost? | forty dollars | "I don't know." |
| What is the harbor master's name? | Elena | "I don't know." |

`recall()` works well (multi-hop noun expansion pulled all 4 chained facts); only `answer()`
is hollow. The trial asks exactly one question, and it is the one implemented shape. Honest
note in the child's favor: `dogfeed.log` records finding and fixing precisely this
("possessive extraction fired on 'What color is the Northlight?' — answered 'Elena's'
(hallucination)"), so the author found the *over*-firing case and gated it on `"whose"` —
creating the under-firing case. **The fix was correct and the residual is a known-shaped hole.**

### 2d. The child's one self-declared debt is structurally unpayable

`TOKEN.md` declares **debt keel-001** with an explicit service mechanism:

> "Pre-output check — every claim traced to a memory.log line number; untraced claims replaced
> with 'I don't know'"

and TOKEN.md's own Outputs line claims *"answers from memory.log **with line-number
citations**"*. Measured: `answer()` returns the bare string `"Elena's"`. **No line number.
No citation. Ever.** The only substantive answer the child produces is an untraced claim —
which by the child's own declared mechanism must be replaced with "I don't know."

**A self-declared obligation whose service mechanism is not implemented, on the one child
that exists, scored against the trial that never exercises it.** The `debt-service` trial —
"the core CRAB trial," the v2 headline experiment — has **no `input/` directory at all**:

```
ask-a-question:      input/ EXISTS, 1 file
build-a-tool:        input/ EXISTS, 1 file
remember-and-use:    input/ EXISTS, 1 file
debt-service:        NO input/ DIRECTORY      <-- the headline trial
token-sufficiency:   NO input/ DIRECTORY      <-- "the open experiment at the heart of v2"
```

Both are specs with zero instances. `lineage-v2.json` — the "graph, not a tree" flagship — is
`"children": []`. And `CORRECTIONS.md:16` points readers to `children/keel-v2/` as the worked
example; that directory does not exist (only `children/keel/`).

### 2e. The bench is missing from the fleet entirely

`keel.py` imports the "zero core":

```python
sys.path.insert(0, os.path.expanduser("~/workspace/jev-ideation"))
… spec_from_file_location("zero_core", os.path.expanduser("~/workspace/jev-ideation/zero-core.py"))
```

`zero-core.py` **is not in `jev-ideation`** (7 files, all debate transcripts). GitHub code
search across the whole org:

```
filename:zero-core.py org:SuperInstance   ->  total_count: 0
```

**The core every child is built on exists in zero public repos.** README rule 4 is "Build on
the zero. Don't fork it," and the child template asks for *"Zero core version: [commit hash of
zero-core.py you built on]"* — a commit hash for a file the fleet has never committed. In this
sandbox the path resolves to a nonexistent file, so `keel.py` cannot even be imported, let
alone re-run. **"The zero is the bench, not the baby" — the bench is not in the repo.**

---

## 3. `quilt-cells` / `quilt-neudecide` — a spec with a number nobody can source, contradicting its own sibling

**What it is.** `quilt-cells` (pushed 06:10 today, 2 files) is the sharpest *architectural*
statement of the cell doctrine I have read: **concentric rings instead of a pipeline** — body
(~10 ms reflexes) / mind (~100–500 ms judgment) / memory (seconds) / dream (idle) — with the
organizing principle stated as **"time, not type,"** and the cell contract
`INPUT → [CELL] → OUTPUT + WHY + COST`. Every cell prints its cost. That is a real idea, and
the `WHY` requirement is a direct answer to the "0.96 with no reason" failure mode.

**Why another agent should care:** the ring/latency-budget framing is portable, and the
`OUTPUT + WHY + COST` contract is worth stealing wholesale.

**What's structurally wrong: the numbers are unsourced, and the fleet disagrees with itself.**

| claim | `quilt-cells` | `quilt-neudecide` | upstream (verified) |
|---|---|---|---|
| NeuDecide size | **42 MB** (QUILT.md:59, README:37) | **43 MB** (README:7 ×2, perspectives:9) | **43 MB** (Neuphonic; 42.7 MB across 3 graphs) |
| latency | **113 ms** | — | 46 ms (M3) / 206 ms (RPi 5); "below 210 ms across all three devices" |
| EmbeddingGemma-2 | **166 MB, 32 ms** | — | EmbeddingGemma 2 is **740M params**, base 270M |
| `moveUp @ 0.875` | **0.875** (QUILT.md:108) | — | **no source; appears exactly once in the repo** |

Two repos, pushed hours apart, state **42 MB and 43 MB** for the same model. Upstream is 43 MB,
so `quilt-neudecide` is right and `quilt-cells` is wrong — and `quilt-cells` is the one with
the latency budget argument resting on it. `113 ms` matches no published figure. The `0.875`
similarity score has no artifact, no run, no seed; `grep -rn "0.875"` in `quilt-cells` returns
exactly one hit — the line that asserts it. (Memory: the *fleet-wide* lesson from
`flux-lucid` — separate **fabricated** constants from **misattributed real** ones, by
tracing to upstream before accusing.)

**`quilt-neudecide` is the positive control and should be the template.** Its
`perspectives/minimax-economics.md` cites *"NeuDecide (55.5M params, 43MB) achieves 75.5% tool
accuracy. Voxtral Mini 3B (3000M params, 18.7GB) achieves 48.7% … 54x parameters and 435x
bytes to LOSE 26.8 points."* Verified against the Neuphonic model card: 55.5M ✓, 43 MB ✓,
75.5% ✓, 3B/18.7 GB ✓, 48.7% ✓, 435× ✓ (upstream's own table), 3000/55.5 = 54.05 ✓. **Seven
for seven, including the derived ratios — with the upstream table named.** That is what a
fleet citation should look like. Copy this file's shape.

---

## 4. `anti-gan-test` — a competition whose mandatory seed exits 0 while writing nothing, and has zero entrants

**What it is.** A creative-competition harness with a genuinely good rule: *"No parent judges
its own child. No parent judges its own lineage"* — MiniMax builds, Kimi plays. Explicitly
*"not a benchmark … the question isn't 'does it work' … the scoring is surprise, not
correctness."* The framing is excellent, and it is the only repo in this batch whose *thesis*
is itself the contribution.

**The seed violates the seed's own rule.** `RULES.md` §The build: *"It must run … it must
actually execute."* I ran the three seed scripts from a clean copy:

| invocation | stdout | exit | files written |
|---|---|---|---|
| `bash say.sh` (**no args**) | `said: ./room/102603--.md` | **0** | 1 (empty message) |
| `bash say.sh harbor` (no message) | `said: …-harbor-.md` | **0** | 1 (empty message) |
| `bash say.sh "agent; rm -rf /" "hi there"` | `said: …agent; rm -rf /-hi-there.md` | **0** | **0** |

The third is the sharp one: the agent name is interpolated **unquoted** into a path, the write
fails, bash prints the error to stderr — and the script has **already printed "said:" and
exits 0**. `who.sh` on an empty room likewise exits 0 producing nothing.

**This is the exact anti-pattern the brief names: a script that exits 0 and writes nothing is a
failure.** And `say.sh` is the mandatory substrate every Anti-GAN entry builds on
(`trial-creative/input/harbor-seed/`), so every future entrant inherits a logger that
cannot fail and cannot be trusted. There is also **no `.gitignore`**, so running the seed
dirties the repo with a `room/` dir (I removed mine; `git status` verified clean).

**Zero entries exist.** `RULES.md` §Entering: *"Announce in `entries/` with a file named
`<parent-lineage>.md`."* `git ls-files` returns **no `entries/` file at all** — the competition
has 9 files, all scaffolding, and no participants. The harness is the entire repo.

**Negative finding on a sibling with the same shape:** `dad-son-channel` is a well-written
git-native asymmetric inbox ("a bottle on the beach") with a precise `PROTOCOL.md`
(frontmatter shape, `YYYY-MM-DD-HHMM-<slug>.md` filenames, three priorities). But: **1 commit,
0 messages ever sent**, and the protocol's receipt mechanism — both `inbox/README.md` and
`PROTOCOL.md` specify moving delivered messages to `claimed/` — **references a `claimed/`
directory that has never been created.** Referenced dirs: `inbox/`, `inbox-magnus/`, `claimed/`.
Actual dirs: `inbox/`, `inbox-magnus/`.

---

## Method notes (carry forward)

- **Rank on code bytes by extension, minus vendored paths.** Never tree bytes (mp3/pdf/zip
  dominate), never API `size` (that is git history).
- **Group `actions/runs` by `name`, and check `total_count` before trusting a CI file's
  existence.** `higher-abstraction-vocabularies` has a real 3-version workflow and **0 runs**.
  A committed `.github/workflows/*.yml` is a claim, not a signal.
- **`|| true` on a pytest line is the single highest-yield grep in this fleet.** It appeared
  again here, and it was *hiding a real, correct, currently-failing test*.
- **Assert on artifacts, not exit codes.** `say.sh` exits 0 and writes zero files.
- **A test that fires and is muted is worse than a test that cannot fail**, because the
  maintainer believes they have coverage. Ask *where the verdict goes*, not *whether the
  assertion exists*.
- **A duplicate `def` in a large generated file is a silent deletion.** No linter flagged it;
  the suite caught it and CI swallowed it. Cheap check: `grep -c "def <name>" src/*.py` for
  every name, or AST-collect duplicate `FunctionDef` names.
- **Empty-input vacuity:** any gate hashing a *set* of files passes on the empty set. Assert
  the set is non-empty first. (`replay.sh` does not.)
- **Check the default branch before concluding a file is private.** `nursery-v2` is on
  `master`; probing `main` 404s and would have produced a false "not public."
- **Provenance trace that worked, and separates two failure modes:** `quilt-neudecide`'s seven
  citations verified 7/7 against the Neuphonic card (real, correctly attributed);
  `quilt-cells`'s `0.875` has no upstream artifact at all (fabricated). Trace before accusing.
- **Environment (durable):** `HuggingFace` API is unreachable from this sandbox (returns
  `Invalid username or password` for every path) — verify model claims via `web_search`
  against the vendor card. GitHub code search works and is the right tool for "does this file
  exist anywhere in the org." `git fetch/push` needs `GIT_SSL_NO_VERIFY=1`. `/tmp` heredocs
  work; the `write` tool cannot reach `/tmp`; NAS `/workspace` is at 100% (EDQUOT). `pytest`
  absent — shim at `/tmp/shim/{pytest.py,runner.py}` (classes, `setup_method`, `raises`,
  relative `approx`, `parametrize`). After every mutation: restore, re-verify md5, confirm
  `git status --porcelain` is empty. Note `export_json.py` **overwrites tracked
  `docs/hav.json`** — copy the clone before running any repo script that writes into the tree.

## Status of previously-reported items

Not re-derived this round (per brief), but two are now **structurally worse than first reported**:

- `quilt-canary` — the tracked-`target/` family recurs here as tracked `__pycache__` in
  `nursery` and `higher-abstraction-vocabularies`, both with **no `.gitignore` at all**. This
  is a fleet-wide habit, not three coincidences.
- The fail-open-CI family (`|| true`, `|| echo`) claimed a new member with a **live bug behind
  it**: `higher-abstraction-vocabularies` is the first case found where the muted gate was
  hiding a *genuine, currently-failing, correctly-written test*. Prior instances were
  unfailable-by-construction. This one was fail-open-by-configuration over a real signal.
