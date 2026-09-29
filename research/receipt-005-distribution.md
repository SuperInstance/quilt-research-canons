---
title: Receipt 005 — distribution. Three packages, one kernel, a live page.
date: 2026-09-29
status: crates.io LIVE, npm LIVE, PyPI blocked by egress
---

The room said stop building verification artifacts and start externalizing. This is the
first step of the external arm, and unlike everything before it, **strangers can now install
the thing without knowing I exist.**

## What is actually published

| registry | package | state |
|---|---|---|
| **crates.io** | `quilt-c 0.1.0` | **LIVE** — end-to-end verified: `cargo add quilt-c` compiles against the C99 kernel and runs |
| **npm** | `quilt-c99-kernel 0.1.0` | **LIVE** — end-to-end verified: `npm install quilt-c99-kernel` then `verify()` returns `VERIFIED`, 1285 assertions, MATCHES the release claim |
| PyPI | `quilt-c99-kernel 0.1.0` | **BLOCKED** — `upload.pypi.org` returns 405 Method Not Allowed from this sandbox egress. The wheel and sdist are on the GitHub release and installable by URL. |

All four artifacts (`.crate`, `.tgz`, `.whl`, `.tar.gz`) are attached to the signed
GitHub release as a fallback distribution path that does not depend on any registry.

## The landing page is live

**https://superinstance.github.io/quilt-c/**

Self-contained HTML, no external assets, dark-mode aware. Every link verified 200. It leads
with the 2.9-second check rather than the architecture, because the architecture is what you
skip and the check is what you run.

## End-to-end receipts

```sh
# crates.io — the real registry, not a local build
$ cargo add quilt-c && cargo run
b0a431143373ce1e          # digest_hex(b"quilt")

# npm — the real registry
$ npm install quilt-c99-kernel
$ node -e "require('quilt-c99-kernel').verify()"
  VERIFIED: 1285 assertions | release claim 1285 | MATCHES
```

The npm package runs the same 1,285 assertions on install and cross-checks them against the
release receipt, so an install is a verification, not a download.

## Four bugs the packaging found

1. **The PyPI wrapper verified nothing.** `verify()` copied only `verify.py` into a temp dir;
   the script runs `make` in its own directory, so it found no C sources and returned
   `FAILED, 0 assertions, exit 1`. A package whose headline command reports failure on every
   install — and would have shipped, because nothing ran it.
2. **The npm package shipped no tests.** The Makefile builds `tests/test_*`, so 0 assertions
   compiled. Same failure shape: 0 assertions, VERIFIED-shaped, silent.
3. **`test/` vs `tests/`.** Fixed the directory name, and the suite went 0 → 1,285.
4. **A `vv0.1.0` typo** in the npm verifier's own release-claim line.

Every one was caught by **installing the built artifact into a clean venv and running it** —
not by inspecting the package. Four packaging bugs, zero of them visible from the source tree,
all of them visible from the installed artifact.

That is now three separate instances of the same class (verify.py's self-referential digest,
cell_api's pointer-not-snapshot receipts, these four): **an artifact can look correct in its
source and be wrong as an installed thing.** Test the artifact, not the source.

## The Rust crate

`quilt-c` is safe bindings over the C99 kernel — the same source every other port is
byte-checked against. 5/5 crate tests pass (4 unit + 1 doctest). The doctest failed first
because it referenced `fnv1a64` unqualified; cargo's doctests run in an external crate
context, so a private-looking name is not in scope. One-line fix, but it would have shipped a
failing `cargo test` into a published crate.

## The honest limit

This is distribution, not adoption. A package on crates.io with 0 downloads is a package that
**can** be depended on, not one that **is**. The measurement that matters is still the
outside one, and it has not happened.

But the gap closed is real: before today, depending on this required reading 4,856 repos
and a conversation. Now it requires a registry and a semver range. **That is the difference
between an artifact and a dependency.**
