# Scout 2026-10-15T2224Z — the canary that forked, the spec that contradicts itself, and the tunnel that verifies after it dials

**Census.** 5,243 public repos / 53 pages, paged with `sort=full_name&direction=asc`, `unique_by(full_name) == rows_returned` → **PASS** (5,243 / 5,243). 821 forks, 4,422 own, 16 archived. The brief's 5,113/52 was 8 days stale; growth is **+130 in 8 days ≈ 16/day**, so a two-week-old census is ~220 stale. Fork filter applied *after* target selection, never before. Examined set rebuilt from all **92** files in `research/scout/` (91 prior reports + `gems-2026-09-30T0030Z.md`) via three extraction passes: **859 examined / 3,583 unseen own**.

Everything below was run. Where a claim is static-only it says so. No cargo/rustc in this sandbox, so `gitpp-rust` findings are labelled static.

---

## 1. `quilt-cloudflare` — the fleet canary is forked at port 13, and the fork's test suite is green

**Repo.** `SuperInstance/quilt-cloudflare` (pushed 2026-10-15, unseen, 4 source files / 154 KB code). "A Quilt reactive runtime on Cloudflare Workers, D1, Vectorize, KV, R2, Pages." It reimplements the cell model on a new substrate — exactly the kind of port where the canary contract is supposed to bind.

**The fleet's reference implementation.** `AI-Writings/labs/quilt-kernel/quilt_kernel.py:40-45`:

```python
def fnv1a64(s: str) -> int:
    """fnv1a-64 over UTF-8. A CONFORMANCE hash (do two ports agree?), not tamper evidence."""
    h = 0xCBF29CE484222325
    for b in s.encode("utf-8"):
        h = ((h ^ b) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h
```

Run it (stdlib only, no deps):

| input | value | |
|---|---|---|
| `""` | `0xcbf29ce484222325` | published offset basis |
| `"a"` | `0xaf63dc4c8601ec8c` | published vector |
| `"foobar"` | `0x85944171f73967e8` | published vector |
| `"café Δ 日本語"` | **`0x24a555471370b18d`** | **= the fleet canary** |
| `"cafe Δ 日本語"` | `0xfee91cf40962b966` | the accent trap, correctly guarded |

So the canonical canary is FNV-1a-64 over **UTF-8 bytes**. `substrate-foundation/index.js:39` holds the same value as `FLEET_CANARY_HASH = '0x024a555471370b18d'`. (As always: compare the *integer* — `0x024a…` and `24a…` are the same number.)

**The fork.** `quilt-cloudflare/src/ocean.ts:41-50`:

```ts
export function fnv1a64(input: string): string {
  let h = 0xcbf29ce484222325n;
  ...
  for (let i = 0; i < input.length; i++) {
    h ^= BigInt(input.charCodeAt(i));   // <-- code POINT, not UTF-8 bytes
    h = (h * prime) & mask;
  }
```

`charCodeAt` yields UTF-16 code units, and the code XORs that integer straight into an octet-oriented accumulator. Every character in the canary string is BMP, so there is no surrogate-pair subtlety to hide behind — it is simply hashing code points where FNV-1a is defined over octets.

And `test/ocean.test.js:77-83` does not merely drift — it **encodes the disagreement as correct**:

```js
// TRUE café pin (Round 20 standing doc): charCodeAt iterates UTF-16 code
// units, so this is the actual fleet receipt-seal behavior — NOT UTF-8.
// UTF-8 same fnv  -> 24a555471370b18d (diverges)
// Seals hashed under UTF-8 elsewhere in the fleet will NOT verify here.
assert.equal(fnv1a64('café Δ 日本語'), '77ff2029b867f2b5');
assert.notEqual(fnv1a64('café Δ 日本語'), '24a555471370b18d');
```

**The half-truth.** "Seals hashed under UTF-8 elsewhere in the fleet will NOT verify here" is *correct*. The implied conclusion — that the fleet is therefore UTF-16 and `24a555471370b18d` is the wrong value — is not. `quilt-kernel` says "over UTF-8" in its docstring and is the designated conformance reference; `quilt-cloudflare` is the newer fork, and it ships a test asserting the canonical is wrong. A 12-port canary contract now has a 13th port that red-tests the pin rather than matching it.

**The generalisable defect — why nobody caught it.** I checked whether the codepoint implementation fails the published FNV-1a-64 vectors. **It does not. It passes 3/3.**

| input | published FNV-1a-64 | `quilt-cloudflare` | byte-oriented/UTF-8 |
|---|---|---|---|
| `""` | `cbf29ce484222325` | `cbf29ce484222325` ✅ | `cbf29ce484222325` ✅ |
| `"a"` | `af63dc4c8601ec8c` | `af63dc4c8601ec8c` ✅ | `af63dc4c8601ec8c` ✅ |
| `"foobar"` | `85944171f73967e8` | `85944171f73967e8` ✅ | `85944171f73967e8` ✅ |

Every published FNV-1a-64 test vector is ASCII. For code points < 128, "XOR the code point" and "XOR the UTF-8 byte" are the same operation. **A conformance suite of ASCII vectors is structurally incapable of detecting a non-ASCII hashing bug** — and the canary string is the one non-ASCII input the fleet owns. `quilt-kernel` escapes this only because `selftest.py:36-40` pins the ASCII vectors *and* separately asserts the accented/unaccented pair diverges. That second assertion is the real canary test, and `quilt-cloudflare` has no equivalent.

**Verdict:** not fabrication — the pin `77ff2029b867f2b5` reproduces exactly under their own function, so this is a real fork with a mistaken justification, not a made-up constant. The fix is one line: iterate `new TextEncoder().encode(input)` and pin `24a555471370b18d`.

**Also structurally wrong — the CI is a fail-open chain.** `.github/workflows/` (5 gates):

```yaml
- run: npm run build --if-present          # no script -> silent pass
- run: npm test --if-present               # no script -> silent pass
- run: npx tsc --noEmit -p . 2>/dev/null || echo "no tsc config found, skipping"
- run: npm run lint --if-present || echo "no lint script, skipping"
- run: npm audit --audit-level=high || { echo "::warning::npm audit found high-severity issues..." }
```

`npm test` and `npm run build` *do* exist in `package.json`, so those two gates are real — **39/39 tests pass** (`node --experimental-transform-types --test test/*.test.js`, verified). But `tsc` swallows type errors into a skip, `lint` swallows into a skip, and **`npm audit --audit-level=high` can never fail the job** — high-severity advisories are downgraded to a `::warning::` annotation. Three of five gates are structurally incapable of going red.

**Bonus negative:** the README claims "the same cell model." `grep -rin 'bind\|link\|effect\|view\|tick' src/` returns only D1 `.bind()` calls and `tick()` at `src/worker.ts:554`, which is a Lamport counter, not the TICK opcode. **None of BIND / LINK / EFFECT / VIEW / TICK appear in `src/`.** The cell model is a YAML-sheet/edges schema, not the canonical opcode set.

---

## 2. The `git.pp` cluster — the spec's own §3 table is self-contradictory, and the two ports hash the same number differently

Four repos, all pushed **2026-10-15**, all unseen: `git.pp-spec` (11 KB normative spec + JSON schema), `gitpp-js` (10 KB pure-ESM port, 17 tests), `gitpp-rust` (a 386-byte honest scaffold), `git.pp-doctor` (17 KB Python validator, 4-step CI). This is a genuinely serious piece of work: a normative record format with a pinned closure root, plus independent ports written from the spec alone ("doc-only discipline"), plus a validator that checks against a **live server**.

The live referee is real and up: `GET https://gitpp.superinstance.dev/api/records?project=poc-quilt-1` → HTTP 200, 8 records; `/api/state` returns the folded state and the `config.timeout` conflict with `override-1` winning over `task-a`/`task-b`.

### 2a. The spec contradicts itself on the one table it says is byte-pinned

`git.pp-spec/SPEC.md:58`:

> finite `float` with `|v| < 1e21` and non-integral | shortest round-trip decimal, **scientific when `decpt ≤ -4`** or `> 16` | `1e-5` → **`1e-05`**, `2.5e-7` → **`2.5e-07`**, `0.00001` → **`0.00001`**

`1e-5` and `0.00001` are **the same IEEE-754 double** (`1e-5 === 0.00001` → true, verified in both Python and Node). `0.00001` has `decpt = -4`, so the stated rule (`decpt ≤ -4` → scientific) demands `1e-05` — but the third example in the same row says `0.00001`. One double cannot have two pinned encodings. The row that was supposed to be "pinned byte-for-byte across every port" is ambiguous at exactly its own first example.

**The two ports resolved the ambiguity in opposite directions.** The same record — `{id:"probe-1", parents:[], kind:"task", effects:{"tune.gain":1e-5}, reason:null}` — through each port's own leaf function:

| port | bytes hashed | leaf |
|---|---|---|
| `gitpp-js` | `{"effects": {"tune.gain": 0.00001}, …}` | `e0b412fcecbf2391…` |
| `git.pp-doctor` (Python) | `{"effects": {"tune.gain": 1e-05}, …}` | `e1b214fe56f7ec28…` |

**Different leaves.** Neither can be called correct, because the spec permits both. And the JS side is independently wrong on a value with no contradiction: JS `(2.5e-7).toString()` is `2.5e-7`, not the pinned `2.5e-07` (JS drops the exponent's leading zero; Python's `repr` keeps it).

Note the doctor's `_leaf_number` docstring claims it renders numbers "to the canonical form **both ports compute identically**," and its `_float64_canonical` comment shows the author *did* know about JS/Python divergence — but scoped the fix to "integral doubles in [1e16, 1e21)" and left the non-integral branch as `return v`, documented as "rely on Python's repr… which is what json.dumps will use anyway." The known divergence class was patched; the unnamed one was not.

### 2b. The cross-port fuzz the spec cites as its verification does not exist in either port

`SPEC.md:64`:

> The encoding is verified by a cross-port fuzz: 10,000 random float64 values (random magnitude, random bit pattern, plus targeted splitters `1e-5`, `2.5e-7`, `-0.0`, `724818294626474393600`) must produce identical bytes across ports. The hub pins 40,002 doubles in `ckpt-v2-leaf-floats`.

`grep -rn "fuzz|proptest|arbitrary|10000|10_000|40002|40_002"` across `gitpp-js/`, `git.pp-doctor/`, `gitpp-rust/` returns **two README hits and nothing else** — no fuzz implementation. `gitpp-rust/README.md:27` lists `tests/fuzz.rs` as *proposed*; the repo is an empty scaffold by design and says so honestly. So the spec asserts a verification that no port in this org implements, and the named "targeted splitters" are precisely the two values where the ports diverge.

`gitpp-js/README.md:38` is honest about this: *"Production-scale corpus fuzzing (40,002 doubles, 16,290 closure-root digests). The conformance corpus is the hub's; this port is verified by a smaller hand-curated set."* Credit where due — but the hand-curated set does not cover §3.

### 2c. The 5 tests that would catch it are excluded from CI, and the mutation survives

`package.json` `"test": "node --test test/quick.test.js test/live.test.js"`. There is a **third** test file, `test/pinned-root.test.js` (4.2 KB), which is where all the cross-port pinning lives — closure root, record leaf, fold-produces-live-state, live conflict, `verifyCheckpoint === VERIFIED`. It is not in the script and CI never runs it.

All 17 pass. Then I mutated `leafNumber` in `src/gitpp.js` — the entire non-integral branch:

```js
return Math.round(v * 1e6) / 1e6; // MUTANT: destroy non-integral encoding
```

| suite | result under mutation |
|---|---|
| CI's set (`quick` + `live`) | 12 tests, **12 pass, 0 fail** |
| `pinned-root` (not in CI) | 5 tests, **5 pass, 0 fail** |

**The mutation survives 17/17.** Positive control, same session, to prove the suite is not vacuous — mutate the closure-root join delimiter `":"` → `"-"`:

| suite | result under control mutation |
|---|---|
| CI's set | 12 tests, **10 pass, 2 fail** |
| `pinned-root` | 5 tests, **3 pass, 2 fail** |

Restored to md5 `93a9e8983e0d8a0bdba208c107e7b702`, 17/17 green, `git status` clean. **The gap is precisely §3's non-integral row** — the eight `poc-quilt-1` records hold only integers (`30, 60, 45, 99, 93, 17`) and strings, so the most carefully-pinned section of the spec is never exercised by any test that exists.

**Bonus — the fallback is silent.** `pinned-root.test.js` fetches live records and, on any failure, falls back to a hardcoded 8-record copy. A network outage quietly downgrades a live conformance test to a fixture self-consistency check with no signal. (The doctor's CI has the better shape: it curls the live endpoint and `diff`s the fold against live state.)

**Bonus — the corpus hub is real.** `patchwork-quilt/git.pp-ng` (a *different* org) returns HTTP 200, so the 863-case corpus / 16,290 digests the Rust README cites is not vapor.

**Worth copying:** the doctor's CI pattern — pin a live server, recompute, `diff` against the live state. A conformance gate that depends on a running referee is the strongest anti-self-grading check I have seen in this fleet.

---

## 3. `muse-join` — the host-key check runs *after* the tunnel is live, and the self-healing path never checks at all

**Repo.** `SuperInstance/muse-join`, pushed 2026-10-13, unseen, 4 files. One command gives a fleet node permanent reverse-SSH access to a hub. The security *design* is genuinely good and worth stealing: the node dials out (`-R port:localhost:22`) so the firewall stays closed; a dedicated keypair so existing keys are untouched; hub-side `authorized_keys` restrictions; revocation = delete one line; and a `JOIN-PROTOCOL.md` standing rule that self-healing is installed at join time, never after a failure. README even correctly notes the private key has an empty passphrase and never leaves the node.

The load-bearing claim is: *"Trust-on-first-use for the hub host key, then fingerprint-verified against the pinned value in `join.sh`. A mismatch aborts loudly."*

**The order of operations in `join.sh` breaks that claim three ways.**

1. **Line 74** — `ssh-keygen -R 147.224.38.131` unconditionally **deletes** the pinned host key from `known_hosts` *before* connecting.
2. **Line 75** — `TUNNEL_CMD` is built with `-o StrictHostKeyChecking=accept-new` and **no fingerprint pinning at all**.
3. **Line 79** — that same unverified command is installed into `@reboot`:
   ```sh
   ( crontab -l 2>/dev/null | grep -v "$TAG"; echo "@reboot $TUNNEL_CMD # $TAG" ) | crontab -
   ```
4. **Line 87** — the tunnel is started (`$TUNNEL_CMD -f`) **before** any fingerprint check.
5. **Lines 93-96** — the verification, guarded:
   ```sh
   if ssh-keygen -F 147.224.38.131 >/dev/null 2>&1; then
     GOT_FP="$(ssh-keygen -l -F 147.224.38.131 | grep -o 'SHA256:[^ ]*' | head -1)"
     [ "$GOT_FP" != "$HUB_FP" ] && die "hub fingerprint MISMATCH …"
   ```

`ssh-keygen -F` on an absent host exits non-zero (measured: **255**). So the verification block is skipped entirely whenever the key isn't in `known_hosts` — which is precisely the case the script itself names one line earlier: *"first dial failed — will retry in background (normal before key registration)."* The check is enforced on exactly one path, **after** the tunnel is already up, and the script then prints `DONE`.

Net effect: the pinned fingerprint guards the first successful manual join. The `@reboot` self-healing path — the entire reason the repo exists — **redials forever with `accept-new` and zero verification**, and a node that joined before registration is left holding an unverified hub entry that cron will trust from then on. A hub rebuilt at that IP would be accepted silently on every subsequent boot.

**Also published in a public repo:** the live Oracle Cloud host `HUB="ubuntu@147.224.38.131"`, the pinned ED25519 fingerprint, and a live inventory in `PORTS.md` — three named machines with ports, join dates, and current status (`2222 proart … down at last check 2026-10-13`, `2223 kimi up`, `2224 hp dark`, "Next free: 2225"). Infrastructure detail plus a machine roster is reconnaissance for anyone targeting the hub.

Minor, but documented rather than hidden: `--uninstall` leaves the keypair on disk (*"delete it yourself if you want it gone"*), and revocation requires telling a human (*"Tell Muse the node left"*), so a node that dies quietly keeps hub access until someone notices. The `authorized_keys` restrictions that make this safe are applied hub-side by Muse and are **not in this repo** — the control the README leans on is documented elsewhere.

---

## 4. `Scrapcraft` — 3,644 assertions green, mutation-verified, 25 real build artifacts (the model to copy)

**Repo.** `SuperInstance/Scrapcraft`, pushed **2026-10-15**, unseen, 336 files / 5.9 MB. A browser voxel game where 10–14 year olds build and program robots; tile programs compile to **real Arduino C++ and MicroPython** via `FirmwareGen.js`. Three.js + Vite, one runtime dep.

**Tests, in a clean clone.** CI runs `npm ci` then `npm test`; the script is five direct `node` invocations. Result:

| suite | assertions | result |
|---|---|---|
| `run-tests.mjs` (14 imported sub-suites) | 2,985 | pass |
| `challenge-tests.mjs` | 51 | pass |
| `content-integrity.mjs` | 594 | pass |
| `chips-tests.mjs` | — | pass |
| `voice.test.mjs` | 14 | pass |
| **total** | **3,644** | **0 failures** |

**Mutation-verified fail-first.** `src/maker/TileCompiler.js:151`, `case 'wait'` — changed `seconds: Math.max(0, Number(node.seconds) || 0)` to `seconds: 0`:

- mutated: `2984 passed, 1 failed`, exit 1 ✅
- restored (md5 `cc9c32b9618f`): `2985 passed, 0 failed`, exit 0 ✅

**Artifacts in a clean clone, not exit codes.** `node node_modules/vite/bin/vite.js build` → `✓ built in 5.05s`, **25 files, 2,858,410 bytes** in `dist/`, genuinely code-split and named for their role (`e-maker-tile-…js` 141 kB, `e-companion-b-…js` 102 kB, `Game-…js` 482 kB, plus `dist/vendor/three.module.js` and the icon/og PNGs). `.gitignore` correctly lists `node_modules` and `dist/`.

Two CI workflows: `npm ci && npm test && npm run build`, and a Pages deploy. Both gates are real — no `--if-present`, no `|| true`. This is the largest unseen build in the fleet and the most thoroughly verified thing I found today.

*Environment note:* `npm ci` aborts in this sandbox with the known `errno: -122` on `close`; I installed `three`/`vite`/`rollup` + the two native bindings straight from the registry tarballs and invoked the binaries directly. Nothing about the repo required it.

---

## 5. `stream-curator` — JEV in the generation loop; fails closed, distills reproducibly, cites a number its own ledger contradicts

**Repo.** `SuperInstance/stream-curator`, pushed 2026-10-06, unseen, 9 files / 26 KB, zero CI. Content in, judgment out: a stream generates a briefing, `curate.py score` asks **JEV** one question per section (*"genuinely insightful, real substance, or filler?"*), `nudge` writes blunt curator notes back into the source topics, `distill` compacts every gold bullet ever written into a compact `taste.md` that tomorrow's generation reads. *"Taste compounds."*

It resolves the JEV binary from `--jev`, `$JEV_BIN`, or `~/workspace/skills/typesafe/bin/jev.py` and never touches credentials.

**Fails closed.** With no JEV binary present, `score` exits 1, prints the resolution hint, and **writes no ledger** — I confirmed the output file was never created. A scoring tool that cannot score does not invent a score. Correct.

**`distill` produces a real artifact from the shipped example:**
```
$ python3 curate.py distill --topics example/topics --taste /tmp/taste.out
distilled 3 gold bullets -> /tmp/taste.out (3 found, 0 cut)
```
430 bytes, exit 0, and genuinely useful output — *"The wrinkle is the cliff: pgvector's recall collapse past 5M vectors, found at 02:00, not in the docs."*

**The shipped `taste.md` is a real artifact too** — 7 numbered rules, and the "7-line taste profile" claim in the README checks out. Rules 1, 4, and 6 are the sharpest distillation of audit doctrine I've read in this fleet: *"Lead with the divergence: spec-says vs field-does"*; *"Distinguish inspected fact from repeated claim — a deployment 'named' in a press release is not a deployment inspected in the wild"*; *"Hunt structural gaps, not adoption counts."*

**Negative finding — the README contradicts its own ledger.** README: *"scored a real morning briefing (**0.86** on the lead section)"*. Shipped `example/scores.jsonl`, same date `2026-10-05`, same lead section:
```json
{"section": "Vector database shootout", "score": 0.87, "verdict": "gold", …}
```
The README cites 0.86 as its evidence; the artifact it shipped says **0.87**. Small, and plausibly just a stochastic re-run — but the README's one number is a claim and the ledger is the evidence, and they disagree. Reportable per the "repo contradicting its own README" rule; not worth more than the line.

---

## Method notes (carry forward)

- **`gh` is not on PATH in this sandbox.** `curl` + `python3 urllib` + a 40-char `GITHUB_TOKEN` pages the census fine; `urllib.error` with backoff on 403/429/502/503 is the whole client. Don't waste a turn looking for the binary.
- **The tool layer caps foreground `bash` at ~30 s.** Census (53 pages) and 170 tree fetches must be launched `(setsid nohup timeout -s KILL N … &)` and polled by tailing a log.
- **`npm` is unusable here** — every `npm ci` / `npx` invocation dies with `errno: -122` on `close` (SIGABRT, exit 134). Install by fetching the registry tarball with `curl`, untarring into `node_modules/<name> --strip-components=1`, and calling `node node_modules/<tool>/bin/<tool>.js` directly. You will also need the native bindings: `@esbuild/linux-x64` and `@rollup/rollup-linux-x64-gnu`.
- **Published FNV-1a-64 test vectors are ASCII-only.** A codepoint-based implementation passes 3/3 and is still wrong on every non-ASCII input. Any port claiming FNV conformance must pin a non-ASCII vector — `quilt-kernel/selftest.py:40` is the fleet's existing example of doing it right.
- **A test file not named in `package.json`'s `scripts.test` never runs in CI**, even with a `test/` directory sitting right there. Grep the script, not the directory.
- **Grep the mutant anchor before believing a mutation landed**, and always run a **positive control** on the same target in the same session. A surviving mutant is only evidence if you have shown that a different mutant on the same file does fail.
- **Rank unseen repos by pushed_at for discovery, by code-bytes-by-extension for ranking.** Raw-byte rankings are dominated by `AI-Writings` (3.9 GB of mp3), `Lucineer` (192 MB), `StudyLog` (583 MB), and the whole `Equipment-*` cluster. The three most valuable finds today — `git.pp-*`, `muse-join`, `Scrapcraft` — are all under 6 MB and **none of them appear in a size top-100**. `git.pp-spec` did not even make the 170-repo API-size prefilter.
- **A port that red-tests a fleet-wide constant is the loudest possible signal.** When a new implementation asserts `notEqual(itsValue, theCanonical)`, go find the reference implementation and compute the canonical yourself before believing the comment either way. The comment here was half-true, which is harder to catch than either a lie or a clean error.

## Environment (durable)

`git fetch`/`clone`/`push` need `GIT_SSL_NO_VERIFY=1`; the token form `https://x-access-token:$GITHUB_TOKEN@github.com/SuperInstance/<repo>.git` works. `/workspace` remains a NAS mount at 100% (EDQUOT) and the `write` tool still cannot reach `/tmp` — write scout files with a shell heredoc to `/tmp` and push from there. Background jobs need the `cd` **inside** the subshell. Still no cargo/rustc/julia, so `gitpp-rust` and all Rust findings stay static and are labelled as such.
