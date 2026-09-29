---
title: Receipt 002 — the first externally-verifiable release
date: 2026-09-29
repo: SuperInstance/quilt-c
tag: v0.1.0
commit: adae27e496bb
---

Receipt 001 made a tree good. Receipt 002 makes a *release claim* checkable.

## The gap Receipt 001 left open

`make verify` proves a tree is good. It does not prove that a named release corresponds to
that tree. Anyone could write "v0.1.0: 1,285 assertions pass" in a README and there would be
nothing to check it against — the claim and the artifact are separate, and only the author
held the link between them.

## The trust root

```
release claim = (tag -> commit) + (commit -> tree hash) + (receipt at tag time)
```

All three are independently checkable by anyone with a clone. Git object hashes are
content-addressed; a tag points at exactly one commit; that commit's tree is derivable by
anyone. So the check needs no trust in the author, the CI, or the repository.

`release_verify.mjs` checks the three are *consistent*. Fail-closed, exit 2.

## The release

**`quilt-c` v0.1.0** at `adae27e496bb`, tagged after verification, with the receipt as the
tag message — so the claim travels with the commit permanently.

```
assertions         1285 passed / 0 failed (7 suites)
source_tree_sha256 be3be613f3528be487e15d6b207ec81f...
receipt_sha256     37ee07375870eebda46623c9db4d3152f621f7401ae71759cf8d65c52dc77131
```

## Stranger test, cold clone, at the tag

```sh
git clone https://github.com/SuperInstance/quilt-c.git
cd quilt-c && git checkout v0.1.0
make verify                        # 1285 assertions + a fresh receipt
node release_verify.mjs --tag v0.1.0
```

```
[ok] tag_resolves            -> adae27e496bb
[ok] receipt_unaltered       recomputed=37ee073... recorded=37ee073...
[ok] receipt_verified        verdict=VERIFIED
[ok] no_failures             1285 passed / 0 failed
[ok] tree_matches_receipt    now=be3be613... receipt=be3be613...
[ok] file_count_matches      now=29 receipt=29
RELEASE VERIFIED
```

Exit 0, from a fresh clone, at the tag, with no context and no trust in the author.

## Three real bugs, caught by testing against the Python implementation

The point of a receipt is that a **second reader can reproduce it**. So the verifier was
written in JS against `verify.py`'s output and made to agree. It did not, three times.

1. **Different exclusion sets.** The JS excluded `.gitignore` as a dotfile; `verify.py`
   included it. Different file sets, so the digests could never match.
2. **Different sort tiebreak.** JS sorted by path only; `verify.py` sorted `(rel, digest)`
   tuples. Same order for distinct paths, but the tiebreak now matches the spec instead of
   relying on paths never colliding.
3. **`JSON.stringify`'s second argument is a REPLACER, not a key-ordering directive.**
   `JSON.stringify(body, Object.keys(body).sort(), 2)` silently turned every nested object
   into `{}` — `suites_detail` became seven empty braces, the canonical string was 333 bytes
   instead of 948, and the hash could never match.

**Bug 3 is the one worth naming.** It is the class of error that presents as *evidence*: the
check reports a hash mismatch, which looks exactly like a tampered receipt. It would have
failed forever, and the natural response — re-sign the receipt — would have papered over a
bug in the checker. An instrument that fails confidently and always is more dangerous than
one that is obviously broken, because it gets blamed on the thing it was checking.

Also fixed an argv trap: `--tag` absent means `indexOf` returns `-1`, so `-1 + 1 === 0` made
the flag value the literal string `"--tag"`.

## The pattern, stated once

`verify.py` had its own two bugs — a self-referential digest, and wall-clock timings inside a
hashed body. Both were found by **running the thing three times and diffing**, not by reading
it. The JS verifier then found three more by running against an independent implementation.

> **Two independent implementations that agree are worth more than one implementation that
> has been read carefully.**

That is the whole external-verification thesis, applied to the verification tooling itself.
The fleet's stated remedy for "the second reader shares our substrate" has been true in
practice: the reader here is a different language, a different author pass, and a different
process, and it disagreed three times before it agreed.

## Chain position

| link | status |
|---|---|
| Days 8-30 dependency-closed artifact | **done** (Receipt 001) |
| Days 31-50 export verification | **done for the first artifact** — green on a fresh runner, deterministic receipt, signed tag, third-party release check |
| Days 51-70 thin A2A cell API | not started |
| Days 71-90 sealed experiment vs public baseline | not started |

The next link is not "add more verification tooling." It is: **an outside party who did not
write any of this runs the check and disagrees with us.** Everything so far has been verified
by the same person who wrote the thing, in a second language. That is better than nothing and
is still not external.
