# Repro scripts — SCOUT 2026-10-24T1350Z

Companion to `research/scout/SCOUT-2026-10-24T1350Z-the-instrument-that-measured-response-length-and-the-repos-the-fleet-owns-twice.md`.

Every claim in that report is reproducible with the files here.

## `fleet_resonance_logprobs_probe.rs` — the decisive receipt (§1)

Copy into `SuperInstance/fleet-resonance/tests/` and run:

    cargo test --test fleet_resonance_logprobs_probe -- --nocapture

It starts a one-shot `TcpListener`, serves a chat-completion body in the
shape OpenAI's API reference documents (`choices[0].logprobs` = **object**
`{ content: [...] }`), calls the crate's own `OpenAICompatibleClient::blocking_generate`,
and asserts on the parsed logprobs.

Observed on pristine `main`:

    PARSE_RESULT content="hello world" logprobs=[] token_probs=[]
    assertion failed: expected 2 logprobs from a documented OpenAI-compatible response, got 0

That is the whole bug: `src/probe.rs` reads `choices[0]["logprobs"].as_array()`,
but the value is an object, so `as_array()` yields `None` and the `else` arm
always runs. The repo's own 62 tests are green in exactly this state.

One-line fix (keep the `if let`, add an `or_else` onto the `.content` array):

    let lp_arr = chat_resp["choices"][0]["logprobs"]["content"].as_array()
        .or_else(|| chat_resp["choices"][0]["logprobs"].as_array());
    let (logprobs, token_probs) = if let Some(lps) = lp_arr { ... }

With it, the probe prints `logprobs=[-0.1, -0.5]` and the repo's 62 tests
still pass — which is the proof that the suite never covered this path.

The repo declares `mockito` in `[dev-dependencies]` and never uses it, and no
test references `OpenAICompatibleClient` or `blocking_generate`.

## `minipytest.py` + `runner.py` — the ternary-rom suite (§3)

PyPI is firewalled in the scouting sandbox and `pytest` is not installed, so
these two files implement **only** the pytest API surface
`SuperInstance/ternary-rom`'s suite actually uses (`approx`, `raises`,
`fixture`, `mark.parametrize`, `skipif`), plus fixture resolution with
generator fixtures, the `tmp_path` builtin, and class-scoped test collection.

**This is not pytest and does not claim to be.** It is a minimal runner whose
only job is to make a 340-function suite executable offline so it can be
mutated. It reproduces the repo's own counts:

    # tests=424
    # pass=424
    # fail=0

Use it as:

    python3 runner.py /path/to/ternary-rom

Known deviations from pytest that matter, and how they were handled:
* pytest excludes functions carrying a fixture marker from collection — so a
  fixture named `test_weights_npy` is **never run as a test**. The runner
  replicates that exclusion (it was the cause of one misleading early run).
* `parametrize` combinations are expanded in application order.
* Three defects in the runner itself were found and fixed during the scout
  (unseeded combination list; missing `tmp_path` builtin; fixture functions
  collected as tests). The reported baseline is from the fixed runner.

## `mut.py` — a mutation helper that cannot edit a docstring (§0a.3)

    python3 mut.py <file> '<old text>' '<new text>'

It refuses to run unless the old text occurs **exactly once**, then walks the
AST and **aborts if the new text landed inside a docstring**. This exists
because the first mutation of `fleet-resonance` silently edited a docstring
instead of the code below it and the suite stayed green — which looked like a
repo defect and was not.

## `dupes_by_tree_sha.sh` — the corrected duplicate detector (§0a.1, §5)

    ./dupes_by_tree_sha.sh ternary-rom recovered-copy-20260824-ternary-rom fleet-math-py ...

Groups repos by **content** (`git rev-parse HEAD^{tree}`), not by the commit
sha that `GET /git/trees/{branch}` returns. Run it over the 55
`recovered-copy-20260824-*` repos to reproduce the 13 byte-identical twins
reported in §5, and the 17 byte-identical shell repos in §4.

## `quicunnel_pin_experiment.sh` — the receipt for §2

    ./quicunnel_pin_experiment.sh /path/to/quicunnel

As shipped, `SuperInstance/quicunnel` **does not compile**: `Cargo.toml:36`
asks for `rustls-pemfile = "2.2"` while `src/tls.rs` is written against the
**1.x** API (`certs()` returned a `Result<Vec<CertificateDer>>`; in 2.x it
returns an iterator). That yields `error[E0599]` at `src/tls.rs:41` and three
`error[E0308]` at `src/tls.rs:87/90/93`, and `cargo test` exits **101 with zero
tests run**. `Cargo.lock` is gitignored, so CI resolves the newest
`rustls-pemfile` every build — which is why every `main` run has failed.

The script runs the suite as shipped, then applies the one-line pin
(`rustls-pemfile = "1"`) and runs it again:

    as shipped  : 4 compile errors, exit 101, 0 tests run
    pinned to 1 : 28 unit tests passed, 0 failed  +  9 doc tests passed

and restores `Cargo.toml` afterwards. The 4 compile errors are in the crate's
**mutual-TLS certificate handling** — the feature its README marks
"✅ — works today, exercised by the test suite".
