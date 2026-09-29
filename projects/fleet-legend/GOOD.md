# good-repo

One line saying exactly what this is, so search finds it.

## First command

```
make verify
```

## What it proves

Prints a `receipt@v1` line and exits non-zero on any failed assertion. If you see the
receipt line, it ran.

## What it does NOT do

It does not test the LLM calls, and it is not a substitute for the integration suite.
Out of scope for this repo.

## When it goes wrong

If you see `OSError -122 EDQUOT` the filesystem is full; write to /tmp instead. The
verifier itself has no recovery path for this.
