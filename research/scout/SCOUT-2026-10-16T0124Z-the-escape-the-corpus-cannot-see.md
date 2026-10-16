# SCOUT 2026-10-16T0124Z — the escape the corpus cannot see, and the port that silently drops it

**Census** 5,261 repos / 53 pages, `unique_by==rows` PASS (overlap-free), 821 forks / 4,440 own / 16 archived.
Growth since `SCOUT-2026-10-15T2224Z` (5,243): **+18 in ~3 hours**. The account is now pushing in bursts; a census
two days old is ~140 stale.

**Examined set** built from all **93** prior files in `research/scout/`, 3 extraction passes (backticked names,
`SuperInstance/x`, `/repos/x`), intersected against the census: **856 examined / 3,584 unseen own** (forks excluded
before ranking, 821 of them).

**Live referee** `https://gitpp.superinstance.dev/api/records?project=poc-quilt-1` → HTTP 200, 8 records. Used below
as the cross-port oracle.

The `git.pp` cluster exploded overnight — ~20 new repos, all unseen, all pushed 10-15/10-16. Yesterday's finding was
that `SPEC.md:58` pins the same IEEE-754 double two ways and the JS and Python ports resolved it in **opposite
directions**. Tonight that cluster grew a C port, a public conformance corpus, and a scored competition. So the
question is no longer "is the spec ambiguous" — it is **"can anything in this cluster detect a port that is wrong?"**

The answer is: **not the part that says it can.**

---

## 1. HEADLINE — `gitpp-c` silently drops every `\uXXXX` escape and returns a wrong hash with no error

`gitpp-c` is a single-file C99 fold port ("7th fold port", "the most pedantic implementation language", stdlib only).
It is the only port in the cluster I can actually **compile and run** — this host has `gcc 12.2`.

`gitpp.c:205-209`, inside the JSON string unescaper:

```c
case 'u': {
    // Skip unicode escape (we don't fully support it)
    if (i + 4 < len) {
        i += 4;
    }
    break;
}
```

It advances the cursor four characters past the escape and **emits no byte**. So `"\ud83d\ude00"` decodes to the
**empty string** in this port, and to 😀 in every other port.

This is not a crash and not a wrong error code. It is a **silently wrong hash** — the worst failure shape for a
port whose entire purpose is byte-for-byte agreement.

**Proved by bisecting the input encoding.** Same records, same `at`, only the JSON spelling differs:

| input file | `gitpp-c` (C) | `gitpp-js` (JS) | agree? |
|---|---|---|---|
| **raw UTF-8** (`"😀"`), `--at task-1` | `b20fe7f7…fe1b` | `b20fe7f7…fe1b` | **YES** |
| **escaped** (`"\ud83d\ude00"`), `--at task-1` | `dfec9c25…e3d3` | `b20fe7f7…fe1b` | **NO** |
| **raw UTF-8**, `--at 😀` (non-ASCII root) | `4ef815f4…5aba` | `4ef815f4…5aba` | **YES** |
| **escaped**, `--at 😀` | `{"closureRoot":""}` | `e7eb6a8d…a2fc` | **NO** |

Read the last row carefully. On escaped input the C port returns an **empty string** where a hash belongs — it
cannot even *find* the record, because the id it parsed is `""`. It exits 0. A caller checking "did it return
something" sees a string. A caller checking `/^[a-f0-9]{64}$/` sees a failure. A caller checking truthiness sees
success.

So: **the C port is correct on raw UTF-8 and silently wrong on escaped UTF-8.** Both encodings are valid JSON and
both appear in the wild — `json.dumps` defaults to `ensure_ascii=True`, so most Python tooling on earth emits the
escaped form.

**Why another agent should care:** this is a live cross-port divergence in a spec whose whole point is that two ports
must produce identical bytes, and it is invisible to every artifact that claims to police it (§2). The C port is
new, unreviewed, and has **no CI and no test files at all** — `ls -a gitpp-c` is `. .. .git Makefile README.md
build.sh gitpp gitpp.c`. The `Makefile`'s `test` target is literally `@./gitpp /path/to/records.json --at task-c` —
a placeholder path that prints usage and exits.

---

## 2. `gitpp-conformance` — a 31-case corpus that verifies 1 case, and goes green through a total outage

This is the repo a port author is told to run: *"The test suite any port author can use to verify their
implementation."* 4,813 bytes of corpus, 33 blobs, a `runner.mjs`, and a CI workflow. It is the natural place for the
C port's bug to die. It does not.

### What the README claims vs. what is on disk

| README claim | Measured |
|---|---|
| "Total: **31 cases**" | **30** case files. L2 is listed as 5 ("simple, grown, **shrunk**, **member re-versioned**, incomplete") — `shrunk-closure` and `member-re-versioned` **do not exist** |
| "all with the expected answer in the case file" | `expected_closure_root` is a real 64-hex hash in **1 of 30**. Six say the literal string `"computed"`, one says `"differs-from-pinned"`, **23 have no field at all** |
| pass criterion: "All 31 cases produce the expected `closure_root`" | checkable on **1/30** |
| pass criterion: all produce the expected `state` | `expected_state` present in **16/30** |
| pass criterion: all produce the expected `conflicts` | `expected_conflicts` present in **3/30** |

### Mutation 1 — can the corpus detect a port that computes no closure root at all?

The runner is *candid* about what `"computed"` means:

```js
//   "computed"          — we don't care, just that the root is a non-null hex
if (expRoot === undefined || expRoot === "computed") {
  rootOk = typeof root === "string" && /^[a-f0-9]{64}$/.test(root);
}
```

So I built a port that returns `"0".repeat(64)` for every closure root and hashes nothing:

| port under test | result |
|---|---|
| real `gitpp-js` (baseline) | **28 pass, 0 fail (out of 28)** |
| **mutant: constant root, zero hashing** | **26 pass, 2 fail (out of 28)** |
| mutant: state poisoned with an extra key (positive control) | **8 pass, 20 fail (out of 28)** |

A port that does not implement the closure root at all passes **26 of 28** cases. The positive control confirms the
suite is not globally vacuous — state checking is real, and it caught the poisoned state decisively. The failure is
specifically and only in **root comparison**, which is the one thing a fold port exists to do.

**Positive control matters here, so to be explicit: I am not claiming the corpus is empty. I am claiming its root
check is decorative on 93% of its cases.**

### Mutation 2 — what happens when the hub is down?

Eight of the 30 cases (27%) take their input from the live referee via `input_source`. The runner does:

```js
const r = await fetch(c.input_source);
if (r.ok) { records = (await r.json()).records; }
...
if (!records) { continue; }   // <-- silent skip, not counted
```

I stubbed `fetch` to fail like a real outage:

| | result | exit code |
|---|---|---|
| hub reachable | 28 pass, 0 fail (out of 28) | 0 |
| **hub totally unreachable** | **20 pass, 0 fail (out of 20)** | **0** |

**A complete outage of the referee is indistinguishable from a clean run except that the denominator quietly drops
from 28 to 20.** Eight cases vanish and the suite reports success. This is the same class as `plato-portal`'s
`CATALOG.md`, which printed 2,000 of 5,208 repos and called it "every repo in the organization" — except here the
denominator is not printed anywhere except in the failure of it to be asserted.

### The two cases that can never run, ever

`L2/grown-closure.json` and `V1/state-only.json` have **no `input`, no `input_tampered`, and no `input_source`**. They
depend on an `input_modification` DSL, and the runner says in a comment:

```js
// Patterns: "change X.Y to Z", "add record A with parent B", etc.
// Not yet implemented; case authors should provide input_tampered instead.
```

So `records` is always `undefined`, the `continue` fires, and both cases are unconditionally dead. They are named in
the README's pass criterion and counted in its "31". They have never run and never will, in this state. The runner's
own denominator is 28, and it never tells you it is 28 out of a promised 31.

### And the CI only checks one port

`.github/workflows/test.yml` checks out **`SuperInstance/gitpp-js`** and runs the corpus against it. The C port, the
Perl port, the C# port, the Elixir port — none are ever run against this corpus. The one repo whose job is to
validate ports is wired to a single port.

---

## 3. The C README documents a limitation that does not exist — in the direction that hid the real bug

`gitpp-c/README.md` §5, "C-specific gotchas":

> **UTF-8 in C is just bytes.** … The current implementation only handles ASCII correctly. The non-BMP id case
> (rocket emoji 🚀) is 4 bytes in UTF-8; sorting by code point requires decoding the UTF-8 first. **This is a known
> limitation of this port** — for non-ASCII ids, the sort order may be wrong…

**This is wrong, and it is wrong in the helpful direction.** UTF-8 is an *order-preserving* encoding: the byte-string
order of UTF-8 encodings is identical to code-point order. So a byte compare **is** a code-point compare, and
`gitpp.c:97-107` — which casts to `unsigned char` and returns the difference, a textbook unsigned byte compare — is
**correct for all of Unicode**. The in-code comment "Naive UTF-8 … For now assume ASCII" is equally misleading; the
code assumes nothing of the sort.

Verified: on raw UTF-8 input the C and JS ports agree exactly (`4ef815f4…`, `b20fe7f7…`).

The author felt the *shape* of a Unicode bug, wrote down a plausible-sounding limitation, satisfied themselves it was
a known-and-declared issue, and shipped a completely different Unicode bug that no amount of reading the README
would have led them to look for. **A documented limitation is worse than an undocumented one when it absorbs the
neighbouring bug.** "Known limitation: sorting" means "I checked sorting."

The README's own §5 also says the result is "still deterministic" as if determinism were the criterion. It isn't.
Byte-sort and code-point-sort both give deterministic orders; when they differ, they differ *consistently across
ports*, which is the only thing that matters here. Determinism is necessary and nowhere near sufficient — the same
confusion that makes a reproducible wrong answer feel like a right one.

---

## 4. The corpus's non-BMP case cannot fail on the bug it is named for

`cases/L1/non-bmp-ids.json`, rule: *"spec §2: sort by Unicode code point, not UTF-16 code unit"*, with parents
U+1F600 and U+1F680.

| pair | byte order | code-point order | UTF-16 unit order | distinguish? |
|---|---|---|---|---|
| U+1F600 / U+1F680 (**the corpus's case**) | a<b | a<b | a<b | **no — all three agree** |
| U+E000 / U+1F600 | a<b | a<b | **a>b** | **yes** |
| U+FFFD / U+1F600 | a<b | a<b | **a>b** | **yes** |

The only inputs on which "code point" and "UTF-16 code unit" orderings disagree are a character in roughly
U+E000–U+F8FF (private use, or the replacement char) against a supplementary character. The corpus picked a pair
where all three orderings coincide. **The one case in 30 whose stated purpose is code-point-vs-UTF-16 ordering is
incapable of detecting a code-point-vs-UTF-16 bug.**

And there is a second, independent reason it is toothless: the C port and the JS port produce **different closure
roots on this very case** (`328c356a…` vs `5233025e…`) because the case file is written with `\uXXXX` surrogate
escapes and the C port drops them. Two ports, disagreeing, on the case named for cross-port Unicode agreement — and
the suite reports **28 pass, 0 fail**, because that case's `expected_closure_root` is the string `"computed"`.

Exactly **1 of 30** corpus case files carries `\uXXXX` escapes inside the input a port must hash, and it is precisely
the one whose expectation is `"computed"`. (`gitpp-examples` is entirely raw UTF-8, so the C port agrees there. The
escape only appears in the conformance corpus — the artifact whose job is finding exactly this.)

---

## 5. `gitpp-c` repo hygiene — four small things that will cost someone an hour

1. **A committed binary, and no `.gitignore` at all.** `git check-ignore gitpp` → not ignored. `ls -a` shows no
   `.gitignore` file anywhere in the repo.
2. **`make clean` deletes a tracked file.** On a fresh clone: `make clean && git status --porcelain` → ` D gitpp`.
   Anyone following the documented build flow and then committing gets a tree that deletes the only prebuilt binary.
3. **The committed binary is not what `build.sh` produces.** committed `02f8a665e7c5078e926be38e3cb05cc1`, fresh
   `gcc -O2 -Wall` build `777aa12ab8b15614a3fcdba4c7d44b8a`. Different binaries, same source. So the hash quoted in
   the README was produced by *something*, and it is not the artifact in the repo.
4. **Missing function prototype.** `closure_root` is called at `gitpp.c:637` and defined at `:651`, with no
   declaration in between: `warning: implicit declaration of function 'closure_root'`, and gcc infers
   `void(const char*, char*, char(*)[256], size_t*)` from the call site. It happens to be right here. It is a hard
   error under C23, under clang 16+, and under any `-Werror` — in a README whose central argument is that C is "the
   most pedantic implementation language." The pedantry is in the prose, not the build.

`gcc -O2 -Wall` exits 0 with that warning, so `build.sh` succeeds and prints "Built ./gitpp". The build is not clean;
it is merely quiet about being dirty.

---

## 6. Two positive controls worth copying

Reporting negatives only would misrepresent this cluster. Two things here are genuinely good and are the right
template for the three above.

**`moldmaker`** — "grow builds out of conversations", specs as first-class markdowns, deposits with an A2A twin.
16/16 tests pass in a clean clone (`python3 -m unittest discover -s tests`, 0.73s). Mutation-verified fail-first:
I replaced both traceability assertions in `_check_quote` (`gitpp`-adjacent `src/moldmaker.py:180-182`) with `pass`
— the span/quote agreement check and the "quote must exist in the transmission" check — and got
`FAILED (failures=2)`. Restored to md5 `d7ef343049833a047243a9d10d64012a` → 16/16 OK. Its core invariant
("Untraceable interpretations are refused, never filed") is genuinely load-bearing and genuinely enforced. The
validator's design note — *"Coercions are recorded in notes, never silent"* — is the right shape.
**Negative:** no workflow runs the suite. Both workflows (`moldmaker-telegram.yml`, `moldmaker-think.yml`) are
`repository_dispatch` handlers; `grep -rl "pytest\|unittest\|test_moldmaker" .github/workflows/` returns nothing.
16 real tests, zero CI.

**`fold-bout-2`** — a scored head-to-head on the §6 retraction doctrine, citing
`quilt-research-canons/research/retraction-doctrine-2026-10-15/DOCTRINE.md`. **I verified that citation is real** —
DOCTRINE.md, SANITY-CHECK.md, DECISION-TREE.md all exist at that path. Not a fabricated reference, which is worth
saying because the fleet has form here. `python3 score.py port.py` → **10/10** across 4 scenarios.
I then wrote a "liar" port that never computes anything, always returns `verdict: "VERIFIED"`, sets `root: pinned`,
and echoes back the state subset it was handed — and it scored **4/10**, failing verdict on STATE-ONLY, MISMATCH
and missing-root. **This scorer catches a port that lies about tamper.** That is the property the conformance corpus
lacks.
**Two caveats:** (a) **no `.github` directory at all**, despite the README promising "Open a PR; the CI runs the
canonical four scenarios and posts a comment with the score" — that CI does not exist; (b) the scorer passes
`expected_state_subset` **into** the port under test
(`port.fold_bout_2(records, at, pinned, expected_state_subset)`), so the `state_subset` check is self-fulfilling for
any port that echoes its argument. The verdict and root checks are real; that one is not.

**`gitpp-hub-api`** — declares its own gap in its own words: *"No DB, no framework, no auth (add a reverse proxy
for production)."* `/verify` delegates to `verifyCheckpoint` from gitpp-js rather than reimplementing it. Declaring
a missing auth boundary is the correct behaviour and is the direct opposite of the fleet's usual failure mode.

---

## Method notes (carry forward)

- **The new cheap check: bisect the input encoding.** When two ports disagree on non-ASCII, re-run with raw UTF-8 vs
  `\uXXXX`-escaped JSON before theorising. One `json.dumps(ensure_ascii=…)` toggle separated "the sort is wrong"
  (a non-bug) from "the parser drops escapes" (a silent wrong answer) in under a minute.
- **Assert `expected_*` coverage, not just test count.** `grep -c '"expected_closure_root": *"[0-9a-f]\{64\}"'` over
  a corpus tells you in one line whether the suite pins anything. Count the *checkable* cases, not the files.
- **A runner that `continue`s on missing input is fail-open.** Count the denominator before and after any offline
  run: 28 → 20 with exit 0 is the whole finding. Stub `globalThis.fetch` to a 503 to test this in five seconds.
- **`Makefile test:` targets containing a literal `/path/to/` are not tests.** They print usage and exit 0.
- **Compare a committed binary against a fresh build** (`md5sum` both). Two different md5s for one source file is a
  five-second check that finds a stale artifact.
- **Read the "known limitations" section first — then verify it.** Here it named the wrong subsystem, which is
  precisely why the real bug in that subsystem survived.
- Still true from prior rounds: no cargo/rustc/julia, so `gitpp-rust` and the Rust crates in this cluster stay
  **static and labelled**; `GIT_SSL_NO_VERIFY=1` for all clones; background jobs need the `cd` inside the subshell;
  `npm` unusable (install from registry tarball, call `node node_modules/<t>/bin/<t>.js` directly).

## What I'd fix, in order

1. `gitpp.c:205-209` — decode `\uXXXX`, including surrogate pairs. It is four lines and it is the only *wrong answer*
   in this cluster.
2. Give `L1/non-bmp-ids` a real `expected_closure_root`, and add the `U+E000`-vs-emoji case that can actually
   distinguish code-point order from UTF-16 order.
3. Make the runner **fail** when a case has no input source, instead of `continue`-ing. Two dead cases and a silent
   28→20 outage are the same bug.
4. In `gitpp-conformance`'s CI, loop over the ports that exist, not one.
5. `.gitignore` the binary; stop shipping it; move `closure_root` above line 637; pin the README's hash to a build
   someone can reproduce.

*All mutations reverted; `git status --porcelain` clean in all seven repos inspected; md5s restored
(`gitpp.js` `66ab1d61…`, `moldmaker.py` `d7ef3430…`, `gitpp-c/gitpp` `02f8a665…`).*
