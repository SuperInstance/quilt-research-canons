# §6 doctrine — decision tree

> One page. The captain picks the option that matches their answer to the four questions.

```
Q1. Does a captain's authority extend beyond their own work?
    │
    ├── NO  ────────────────────►  Option I (pure self-retraction)
    │                              Author-only. Captain's
    │                              ratification is a warning,
    │                              not a claw.
    │
    └── YES
        │
        Q2. Is the captain's retraction visible to future readers?
        │
        ├── NO  ──────────────────►  Option II (captain-retract, no stain)
        │                            The captain's signature on
        │                            the settlement is the only
        │                            accountability. Surface is
        │                            silent on captain-vs-self.
        │
        └── YES
            │
            Q3. Do you want a permanent record of every captain
            │   action against a standing author?
            │
            ├── NO  ──────────────►  Option II (captain-retract, no stain)
            │                        (same as Q2-NO)
            │
            └── YES
                │
                Q4. Are you willing to broaden the closure-root
                │   leaf domain to cover `dispute` and `settlement`
                │   records' `target` and `author` fields?
                │
                ├── NO  ──────────►  Option II (captain-retract, no stain)
                │                    (defer Option III until
                │                    the leaf is ready)
                │
                └── YES
                                    │
                                    ▼
                                  Option III (captain-retract, stain)
                                  New leaf domain, new corpus family,
                                  new consumer logic in desk/grid/worker/runner.
```

## The four questions in plain English

1. **Q1 — "Can a captain act on someone else's record?"** If your answer is "no, the captain can only author overrides and cannot void other people's records," Option I is correct. If your answer is "yes, the captain is a steward of the project's truth," continue.

2. **Q2 — "Should a future reader see the captain's mark?"** If your answer is "no, the captain's signature on the settlement is enough," Option II is correct. If your answer is "yes, the captain's actions should be visible in the substrate," continue.

3. **Q3 — "Do you want every captain action permanently in the record?"** This is a strong version of Q2. If yes, continue. If no, you are at Option II.

4. **Q4 — "Is the leaf-domain broadening affordable now?"** The leaf domain must cover `dispute.target` and `settlement.dispute` for the surface to distinguish captain action from self-retraction. This is a real change to the conformance corpus, the desk UI, the grid rendering, the worker collection, and the runner. If now is not the time, defer Option III.

## The current recommendation

**Option II** is the default because:
- Q1's answer is "yes" (the captain already has override authority; that's the inheritance doctrine).
- Q2's answer is "the captain's signature on the settlement suffices" (no new field needed; no new corpus family).
- Q3's answer is "not now" (we have one contested case in the design duel; the live system has zero).
- Q4's answer is "not now" (broadening the leaf costs a corpus family, a desk UI change, and a worker route — all justified, but only when there's a real contested case to test against).

The §6 doctrine doc (`DOCTRINE.md`) records this as Option II with the load-bearing invariant any option must pass. If a contested case appears in production, the captain re-evaluates; the mechanics in PR #16 are forward-compatible with all three options.

