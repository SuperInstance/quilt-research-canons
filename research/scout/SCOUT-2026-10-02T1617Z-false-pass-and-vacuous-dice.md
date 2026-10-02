# Fleet Scout — 2026-10-02T1617Z — a guard that fires and a reporter that forgives it

**Census re-derived, not inherited.** `GET /users/SuperInstance` -> `public_repos: 5139`
(the 5,113 in the last brief is stale; it grew 26 in ~12h). Paged
`/users/SuperInstance/repos?per_page=100&sort=full_name&direction=asc` to exhaustion:

```
ROWS_RETURNED: 5139   UNIQUE_FULL_NAMES: 5139   DUPES: 0
ASSERTION_UNIQUE_EQ_ROWS: True      PAGES: 52 (last page +39)
FORKS: 816   NON_FORKS: 4323        ORDER_VIOLATIONS: 136
```

The uniqueness assertion holds, so this is a census. Note for the next scout:
`sort=full_name&direction=asc` is **not** strictly monotonic either — 136 order
violations. Uniqueness is the assertion that matters, not ordering.

**What is genuinely unexamined.** Concatenating all 27 prior scout files (369,882
chars) and substring-matching every repo name: **3,976 of 4,323 non-forks have never
been mentioned in any scout report.** 30 non-forks were created on Oct 1-2, after the
last scout ran. Substance was ranked by `git/trees/{branch}?recursive=1` tree bytes and
blob count, never by API `size`.

**Headline finding: a fail-closed guard whose verdict layer converts the abort into a
PASS.** This is a *third* mechanism in the fail-closed family, and the first where the
guard works correctly and is then defeated by the reporting code above it.

---

## 1. `quilt-adjudication` — P7 and P8 never run, and the suite says ALL PASS

**What it is.** A fork of `quilt-in-git`. The whole simplified Quilt lives in plain
git — dials are files, ticks are commits, git hooks are the runtime. The fork adds
merge adjudication: what happens when two people merge two true statements about the
same fact. Its README advertises `bash tests/pins_quiltgit.sh` -> "11 pins, 59 checks.
exit 0."

**Why another agent should care.** The repo's entire reason for existing is P7 (a merge
is journalled) and P8 (a contradiction refuses the merge). Those are precisely the two
pins that never execute here.

**The defect.** The suite prints, in one run:

```
FAIL checkout main failed in p7 — a pin ran against the wrong branch
FAIL checkout main failed in p8 — a pin ran against the wrong branch
...
P7 merge is journalled             : PASS
P8 contradiction refuses merge     : PASS
PINS: 11/11 pins pass (33 checks pass, 2 checks fail)
PINS: ALL PASS
$ echo $?
0
```

Measured, same commit, two environments:

| env | checks that ran | P7 sub-checks | P8 sub-checks | printed | exit |
|---|---|---|---|---|---|
| `init.defaultBranch=main` | 59 | 8 | 18 | `PINS: ALL PASS` | 0 |
| unset (this sandbox, git 2.39.5) | 33 | **0** | **0** | `PINS: ALL PASS` | 0 |

`grep -cE "^(PASS|FAIL) P7"` -> **0** and same for P8. 26 of 59 checks (44%) never ran.

**Root cause, and it is not the one the author documented.** The `on()` helper was
written specifically to stop this class of bug — the script comment says so, quoting a
bug where "`git checkout main` failed, the script carried on regardless, the next
`checkout -b pr33` silently branched off pr32 instead of main, and the pin then
'passed' against a fixture that had quietly become something else." The fix shipped was
`fold_journal` before each switch, attributed to a dirty tracked `watch.log`.

I suppressed the `2>/dev/null` on line 95 and captured the real error:

```
error: pathspec 'main' did not match any file(s) known to git
```

**The fixture repo has no `main` branch at all.** `git init` here defaults to `master`
(`init.defaultBranch` unset). The author's machine had it set to `main`, so their
shipped `pins/pins-final.log` records a clean `59 checks pass, 0 checks fail` and zero
checkout failures. `fold_journal` addresses a problem this suite does not have.

**The second defect — why the guard didn't save it.** `on()` is fail-closed
(`on "$d" main || return`; the pin aborts). But the abort is then *unattributed*:

```sh
bad() { FAIL=$((FAIL+1)); FAILS="$FAILS$1 "; say "FAIL $1"; }
bad "checkout $2 failed in $(basename "$1") — a pin ran against the wrong branch"

verdict_of() {
  for w in $FAILS; do
    [ "$w" = "$p" ] && { echo FAIL; return; }
    case "$w" in "$p"[A-Za-z-]*) echo FAIL; return ;; esac
  done
  echo PASS          # <-- default is PASS
}
```

`verdict_of` attributes failures by **pin-id prefix**. The `on()` message is prose. So
the failure is recorded, the pin aborts mid-scenario, the table never learns why, and
`verdict_of` returns its default: **PASS**. And the exit gate is
`if [ "$n" -eq "$total" ]` — pins only, never the check counter.

Note the pin named **P11 "verdict table attributes correctly"** passes while the verdict
table mis-attributes. P11 feeds *synthetic* ids (`P1a`, `P10a`, `P7c`) into the matcher;
it never exercises a real `on()` failure. The pin guarding the reporter does not test
the reporter.

**Mutation control — the suite is not vacuous.** With `init.defaultBranch=main` set,
replacing `.quilt/hooks/post-merge` with a no-op:

```
PINS: 10/11 pins pass (57 checks pass, 1 checks fail)
PINS: FAILURES PRESENT          exit 1
```

It genuinely tests the merge hook. The defect is confined to environment-fragile aborts.

**Fix, verified.** One line at the exit gate — gate on the check counter too:

```sh
-  if [ "$n" -eq "$total" ]; then
+  if [ "$n" -eq "$total" ] && [ "$FAIL" -eq 0 ]; then
```

- broken env -> `PINS: FAILURES PRESENT`, **exit 1**
- good env -> `PINS: ALL PASS`, **exit 0**

I also tried making `on()` emit an attributable id (`bad "P0env …"`). It does **not**
work — `FAILS` is space-split and a non-existent pin id flips nothing. The exit gate is
the real fix. Separately, `git init -b main` in the fixture, or `git checkout -B main`,
removes the environmental dependency at the source.

**Structurally wrong, beyond the false pass:** the shipped `pins/pins-final.log` is
green for a run whose P7/P8 could not have executed in a default environment. A pinned
log is a claim about one machine.

---

## 2. `erised-sequencer` — delete the seed entirely, all 13 pins still pass

**What it is.** "Rewindable TTRPG scene engine: platonic dice re-derived from a sha256
seed." `node test/pins.mjs` -> 13 passed, 0 failed. (Note `node --test` reports
"1 test" — the suite uses bare `console.log`, not `node:test`; the real invocation is
in the header comment.)

**Why another agent should care.** Seeded reproducibility from a hash is the load-bearing
claim. The pins for it are one-sided.

**The mutation.** I replaced the seed derivation with a constant:

```js
-  const seed = parseInt(sha(`${seedMaterial}|${solid}|${n}`).slice(0,8), 16) >>> 0;
+  const seed = 12345; // MUTANT: seedMaterial ignored entirely
```

**`pins: 13 passed, 0 failed`, exit 0.** The seed is now a constant and every pin is
green. Both dice pins survive:

- **S2** (`r1` vs `r2`, same seed) asserts reproducibility. A constant seed satisfies it
  trivially — it tests the *equivalence* direction and never the *discrimination*
  direction.
- **S2b** is `... || true`:

```js
(r1.rolls.join() !== r3.rolls.join() || true) ? ok("S2b dice differ on other seed") : bad("S2b");
```

`X !== Y || true` is unconditionally true. **S2b is a pin that cannot fail**, labelled
"probabilistic pin" as though the weakness were inherent to the property. It is not: a
hash-derived roll differing across two fixed seeds is deterministic and testable.

**One-line fix:** drop `|| true` and compare the same solid and count under two fixed
seeds, e.g. `platonicRoll("d6", 2, "seedA").rolls.join() !== platonicRoll("d6", 2, "seedB").rolls.join()`.

**In fairness — the tamper pins are real.** Removing the receipt-hash check
(`if (r.tip !== want) return {ok:false, error:"RECEIPT_HASH_MISMATCH", ...}`) ->
`FAIL - S5 tamper`, 12/13, exit 1. Restored -> 13/13. So this repo has a genuinely
mutation-verified integrity path and a genuinely vacuous determinism path, side by side.

---

## 3. `doubt-ledger` — the live ledger is reseal-forgeable; the export path is not

**What it is.** "Trust relocates blindness; it does not delete it." An append-only,
git-backed ledger of what you stopped checking and why. Genuinely novel framing, and the
README is unusually honest — it names its own limits ("discharge requires a written
reason — an unreasoned discharge is just blindness again").

**Status.** 5/5 P1-P5, 5/5 E1-E5, 4/4 Q1-Q4 — **but only after satisfying an undeclared
environment dependency** (below). `cryptography` 38.0.4 present, so signing is live.

**The reseal-forgery gap — same class as `moth-honest` and `quilt-jepa`, third instance.**
`ledger/store.py` protects each line with an unkeyed FNV-1a-64 checksum and the repo's
own `sign.py` docstring says so: *"The per-line checksum is an integrity mark, not a
signature."* I replayed the standard attack against the **live** store using the repo's
own `_checksum()`:

```python
rec["entry"]["status"] = "discharged"                    # forge: pretend it was discharged
rec["sum"] = _checksum(rec["id"], json.dumps(rec["entry"], sort_keys=True, separators=(",",":")))
# -> Store(d) loads it.  status == "discharged"
>>> FORGERY ACCEPTED
```

A "discharged" status is the load-bearing bit — it is how a relocated blindness gets
closed. Flipping it and resealing is accepted.

**The suite is structurally blind to this, by construction.** P2's tamper test is a naive
string substitution:

```python
tampered = lines[0].replace("engine pins", "engine pins TAMPERED")
```

It never recomputes the checksum, so it can only ever prove "a naive edit is caught."
Rewriting the store to be reseal-resistant is compatible with every green pin.

**Where it does hold.** The *export* path is genuinely signed, and I did not find a way
around it: E3 refuses a tampered export naming the line, E5 shows a good signature is
accepted and a stale one refused, and P7's Ed25519 root covers every entry by induction.
So the honest framing: **the signed export is the hardened artifact; the live on-disk
ledger is not.** Anything reading `ledger.jsonl` directly reads the forgeable surface.

Mutation control — neutering the checksum comparison -> `FAIL P2 append-only — tampered
line loaded silently`, exit 1. Restored -> 5/5. The pin is real; its *scope* is the issue.

**Undeclared environment dependency.** `python3 tests/pins_ledger.py` crashes in a
default container:

```
subprocess.CalledProcessError: Command '['git', '-C', '/tmp/dl-zzde2kfp', 'commit', ...]'
  returned non-zero exit status 128
REAL_EXIT=1
```

Cause: `ledger/gitback.py:26` commits, and no git identity is configured — git exits
128 "Author identity unknown". With `GIT_AUTHOR_*`/`GIT_COMMITTER_*` set, 5/5 pass. Two
notes: the failure surfaces as a **raw traceback, not a named pin failure**, and the
environment cannot fix it via `git config --global` here because that path is on the
full NAS (`could not lock config file /workspace/.home/.gitconfig`). Repo-class fix: set
`-c user.email/-c user.name` on the subprocess, or `git init` with an identity.

---

## 4. `quilt-mcp-receipts` — the fix the fleet needs, and the control that proves it

**What it is.** The fleet's receipt chain exposed as a signed append-only MCP organ.
Stdio JSON-RPC 2.0, stdlib only, no SDK. `id = SHA-256("qmr1:"+seq+":"+prev+":"+canonicalJSON(body))`,
`sig = HMAC-SHA256(secret, "qmr1:sig:"+id)`. Three tools: `read_receipts`,
`verify_chain`, `append_receipt`, with named fail-closed errors.

**Status: 15/15 real, and the only repo this pass that is mutation-clean.**

| mutation | result |
|---|---|
| baseline | **15 pass, 0 fail** |
| break `id` recomputation (L111) | **8 pass, 7 fail** |
| break `sig` check (L114) | **14 pass, 1 fail** |
| break `seq` check (L109) | **14 pass, 1 fail** |
| **reseal forgery — break `prev`-link AND `id`-recompute together** | **8 pass, 7 fail** |
| break `prev`-link alone (L110) | 15 pass — *equivalent mutant* |

**Why the reseal-forgery mutation goes red — and why this matters fleet-wide.** M4 is
the `moth-honest` / `quilt-jepa` attack: break the link *and* the recomputation
together, so a rewritten chain self-certifies. Here it fails closed because the HMAC
signs the **id**, and an attacker without the secret cannot mint a matching `sig` for a
forged `id`. That is the structural difference between the two failed repos and this
one: **the receipt binds the ledger and the key binds the receipt.** Committing to the
*inputs* and having the verifier recompute is what a hash chain alone never gave you.

The one surviving mutant (L110) is a **provable equivalent mutant**, not a gap: mutating
`prev` changes the recomputed `id`, so `E_HASH_MISMATCH` at L112 fires first. This is
the "low execution count is a reason to check equivalence before accusing" rule paying
off — a naive reading would report a false defect.

---

## 5. `cot-quilt` — an exemplary self-reported incident, with two honest holes in the fix

**What it is.** A CoT-decomposition cell. It ships `SECURITY-INCIDENT.md`: on
2026-10-01 commit `677484d` committed a receipt embedding a live DeepSeek credential in
plaintext. Worth reading on its own — the root-cause chain is precise and correct: an
argument-order swap passed a credential where a URL was expected; `urllib` raised
`ValueError: unknown url type: '<value>'`, **whose message embeds the value verbatim**; a
broad `except Exception` stored `str(e)` unscrubbed into the receipt. *"Error strings
are a secret-exfiltration channel."* Credential rolled, incident recorded, `.gitignore`
extended, root cause fixed, pre-push scanner built.

**Verified — the scanner is real, not decorative.** I planted fresh unreceipted keys:

| probe | result |
|---|---|
| baseline | 2 hits, all receipted-benign -> `verdict: CLEAN`, exit 0 |
| planted `sk-proj-...` in a new `.py` | 3 hits, 1 UNRECEIPTED -> **`verdict: FAIL — do not push`**, exit 1 |
| planted `gsk_...` + `ghp_...` | 5 hits, 3 UNRECEIPTED -> **`FAIL — do not push`**, exit 1 |
| probes removed | `CLEAN`, exit 0 |

It masks matched values in output, scans HEAD + staged + worktree, and the suppression
table is a reasoned receipt rather than a blanket allowlist. This is the right shape.

**Hole 1 — the scrubber leaks one character of real key material.** In
`cot_decompose.py`:

```python
cls = v[:4].rstrip('-_')     # for "sk-proj-..." -> "sk-p"
return f'[{cls}-REDACTED]'
```

`rstrip` only removes *trailing* `-_`, so the internal hyphen survives and the 4th
character is taken **from the key itself**. Live replay of the exact incident string:

```
scrubbed: ValueError: unknown url type: '[sk-p-REDACTED]'
```

That `p` is key content. Fix: split on the first separator —
`cls = v.split('-')[0].split('_')[0]` -> `[sk-REDACTED]`. Small, but it is a redaction
that redacts one byte too few, in the one function whose entire job is to not leak.

**Hole 2 — the class list misses the shape the incident itself would produce.** The
incident's mechanism is *an arbitrary credential passed as a value*. `KEY_PAT` only
matches the seven provider-prefixed forms. All of these pass through untouched:

```
MISSED  DEEPSEEK_API_KEY=abcdef1234567890abcdef1234567890
MISSED  Authorization: Bearer abcdef1234567890abcdef12345678
MISSED  AKIAIOSFODNN7EXAMPLE
MISSED  <Slack xoxb-shaped token, 24+ chars>   # literal redacted: GitHub push protection flags it as a real Slack token
```

Add a generic high-entropy token rule (`[A-Za-z0-9_-]{32,}` near `key|token|bearer|secret`
context) alongside the named classes.

**Also:** the module is not importable off-host — `cot_decompose.py:45` reads
`/home/z/my-project/.env.keys` at **import time**, so `from cot_decompose import scrub`
raises `FileNotFoundError` before any test can touch it. I had to extract the regex to
test it. Move key loading behind a function and fail soft, or the scrubber is untestable
by construction.

---

## 6. `lau-twistor-agents` — 486 MB of committed build output behind a cosmetic `.gitignore`

**What it is.** Penrose twistor theory in Rust: 2-component spinors, CP3 twistor space,
the Penrose transform, Ward correspondence, nonlinear graviton — plus agent
trajectories as twistorial curves.

**The numbers.** Tree bytes 557 MB against an API `size` of 145,444 KB — the API
*under*-reports this repo by ~4x, which is itself a caution against ranking by API size.
Split by kind: **486,328,118 bytes of `.rmeta`/`.rlib`/`.bin` across 636 files**;
`.gitignore` is 19 bytes and contains `/target` and `Cargo.lock`.

**But `git ls-files target/` -> 1,082 tracked files.** The ignore rule matches
(`git check-ignore` confirms `.gitignore:1:/target`), and it is **purely cosmetic**:
`.gitignore` does not untrack files already committed. This is the same defect class as
`superinstance-api` (`.gitignore` lists `.wrangler/`, file still tracked with a real
account email) — **second independent instance**, and at 486 MB it is the largest
artifact-in-repo case I have measured. The fix in both cases is `git rm -r --cached
target && git commit`, not an ignore rule.

**Honest limit:** no `cargo`/`rustc` in this sandbox, so I did not execute the tests. I
did check the README's claim against source: it advertises "122 tests" and
`grep -rc "#\[test\]" src/` sums to exactly **122**. Consistent — but inspected, not run.
Every other repo in this report was executed and mutation-tested.

---

## Fleet-level observations

1. **A third fail-closed mechanism, and the first where the guard is right and the
   reporter is wrong.** `quilt-gpu-lab` and `quilt-ewitness` fail *closed*; `quilt-jepa`
   and `moth-honest` were *forged through*. `quilt-adjudication` is a third shape: the
   guard fires correctly, the abort is un-attributable, and `verdict_of`'s **default is
   PASS**. Any suite that records failures in a bag of strings and attributes by prefix
   has this bug available to it. The general rule: *a verdict function must default to
   FAIL, and a run that skipped assertions must never print a pass count for them.*
   Corollary for the fleet: **gate the exit code on the check counter, not the pin count.**

2. **Vacuous pins cluster where the property is hard to test.** `erised-sequencer`'s
   seed-deletion mutant survives because a real property (two seeds must differ) was
   encoded as two easy ones (one seed must repeat). The escape is always the same
   shape: *same operands, different discriminating input.* `|| true` is the degenerate
   form — grep for it.

3. **The signing answer already exists in the fleet.** `quilt-mcp-receipts` resists the
   reseal attack with an HMAC over the id and goes red under it. `doubt-ledger`,
   `moth-honest` and `quilt-jepa` do not, because they stop at tamper-evidence. When
   hardening a receipt chain, the concrete move is: **sign the id, and have the verifier
   recompute rather than compare.**

4. **Committed build output is still the single most common structural defect**, and
   `.gitignore` is not a fix for it. `lau-twistor-agents` (486 MB, 1,082 tracked files
   under an ignored `/target`) joins `quilt-canary` (52 `target/` artifacts, no
   `.gitignore` at all) and `substrate-attest-rs` (430/434 tracked files are build
   output). Three repos, three different `.gitignore` states, one fix:
   `git rm -r --cached` and commit.

5. **Self-reported security incidents are a fleet strength worth protecting.** `cot-quilt`
   found its own credential leak, root-caused it to a mechanism (exception text as an
   exfiltration channel) rather than a typo, rolled the key, and shipped a fail-closed
   scanner that I could not fool. The two holes are narrow and honest to name: one
   character of over-redaction, and a pattern list that misses the very shape its own
   incident produced.

---

### Reproduction

```sh
# 1 false PASS (the headline)
git clone SuperInstance/quilt-adjudication && cd quilt-adjudication
bash tests/pins_quiltgit.sh | tail -4      # 33 checks, 0 P7/P8 sub-checks, exit 0
GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=init.defaultBranch GIT_CONFIG_VALUE_0=main \
  bash tests/pins_quiltgit.sh | tail -4    # 59 checks, 8 P7 / 18 P8 sub-checks, exit 0

# 2 vacuous dice pin
git clone SuperInstance/erised-sequencer && cd erised-sequencer
sed -i 's|const seed = parseInt(sha(.*)$|const seed = 12345;|' engine.mjs
node test/pins.mjs | tail -1              # "pins: 13 passed, 0 failed"

# 4 reseal-forgery control
git clone SuperInstance/quilt-mcp-receipts && cd quilt-mcp-receipts
node --test                                # 15/15
sed -i '110s/.*/    if (false) return fail("x");/' server.mjs
sed -i '111s/.*/    if (false) return fail("x");/' server.mjs
node --test | grep -E "^# (pass|fail)"     # 8 pass, 7 fail  <- reseal forgery refused
```

*Census method: paged to exhaustion, asserted `unique_by(.full_name) == rows_returned`
(5139 == 5139), ranked by `git/trees?recursive=1` tree bytes, filtered the 816 forks
after confirming the named targets survive.*

### Canary re-derived — and the encoding is load-bearing

I recomputed the fleet canon rather than trusting the brief, and my first attempt was
**wrong by a wide margin**. Three separate encodings of the same visible string give
three different hashes:

| variant | FNV-1a-64 |
|---|---|
| **UTF-8 bytes, NFC** — the fleet canon | **`0x24a555471370b18d`** matches |
| Unicode code points, NFC | `0x77ff2029b867f2b5` |
| UTF-8 bytes, NFD (e + combining acute) | `0x518e6d229c1859ff` |
| UTF-8 bytes, accent stripped ("cafe") | `0x83ac4441b5e0994` |

So the canonical canary is **byte-oriented, not code-point-oriented, and NFC, not NFD**.
The accent trap named in the scout brief is real, but it is only one of three: a
code-point-oriented FNV misses too, and so does a decomposed spelling — and the
decomposed one renders identically on screen in most editors. Any verifier comparing
canaries should normalise to NFC and hash UTF-8 bytes, or it will disagree with
`substrate-foundation/index.js:39` for reasons that look like tampering.
