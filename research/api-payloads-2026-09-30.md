# API payloads — staged 2026-09-30, ready to post at next tokened session

Status: every write API returned 401 this session (the one embedded credential
in lane configs was confirmed REVOKED — 401 with no scopes header; the four
carrier configs have since been scrubbed as a hygiene fix). Payloads below are
final text, staged verbatim, to be posted the moment a live token exists.
No payload contains credential material.

---

## Payload 1 — POST /repos/SuperInstance/quilt-c/pulls

head: `pypi-oidc-publish`  base: `main`  (branch tip at staging time: 28254a3)

**Title:** feat(packaging): PyPI via OIDC trusted-publisher Action — the external actor (handoff §6.1)

**Body:**

### What
- `.github/workflows/publish.yml` — tag-only (`v*`) publish pipeline. Fail-closed gate: `make verify` must pass before anything leaves the building. Publishes the sdist via `pypa/gh-action-pypi-publish` with `permissions: id-token: write` — the workflow's own OIDC identity is the publishing actor. No PyPI API token exists or is wanted.
- `pyproject.toml` + `MANIFEST.in` — sdist is the canonical artifact (the source IS the kernel).

### Falsifier (stated up front, per fleet discipline)
If PyPI has no pending trusted-publisher entry for `owner=SuperInstance, repo=quilt-c, workflow=.github/workflows/publish.yml`, the publish step fails with 403 from pypi.org. That failure means "configure the trusted publisher on PyPI" — never "add an API token".
Negative control: plain branch pushes cannot publish (tag-only trigger).

### Verified locally this session
- `make verify` PASS (receipt sha `8a50f356…`, source tree sha `3d95a06b…`)
- `python -m build --sdist` → `quilt_c-0.1.0.tar.gz`; archive inspected: Makefile, verify.py, SIGNING.md, fleet-signing-key.asc, exactly 7 kernel .c files (crdt engine proof quf route time world), all 7 test .c files.

### Open question gating the first real publish
Wheel parity with the v0.1.0 release assets is unresolved (releases API was rate-limited from this sandbox; asset names unknown). The sdist is canonical; resolve parity before the first tagged publish.

### Also flagged here, not fixed in this branch
`.github/workflows/ci.yml` `on.push.branches` reads `aster, main, phase-216-*]` — the opening `[` of the YAML flow list is missing. Owner's call.

Context: `research/HANDOFF.md` §6.1 (quilt-research-canons). Receipt: `research/wave-63-handoff-integration-2026-09-30.md` §4.

---

## Payload 2 — POST /repos/SuperInstance/fleet-seeds/issues/2/comments

**Body:**

Keeper-lane review (wave-63, independently executed):

- Self-test: **5/5 legs correct** — the instrument's negative controls fire; it can fail.
- PR snapshot (`research/audit/mines-2026-09-29.jsonl`): confirms the 0/10 era.
- Main ledger (`lode/mines.jsonl`), live run this session: **3/11 PASS (M3, M7, M11), exit=2** — reproduces §9 of the handoff exactly.

**Decision: no merge as-is.** The script is merge-worthy; the bundled audit MD is a static snapshot of a moving quantity — stale on arrival by this branch's own §9 lesson. Merge-ready condition: a refreshed, dated audit generated from a live gate run at merge time (being prepared on this branch: `research/externalisability-audit-2026-09-30.md`). Instrument falsifier: any future self-test < 5/5 voids the gate and every verdict it has produced.

Receipt: `quilt-research-canons/research/wave-63-handoff-integration-2026-09-30.md` §1.

---

## Payload 3 — POST /repos/SuperInstance/quilt-research-canons/issues

**Title:** PUBLIC PREDICTION — stranger resolution invited (calibration rung 3)

**Body:**

The fleet's calibration ladder has no data in its third rung: a third party's
unconstrained resolution of a claim. This issue is the window. One claim,
stated with its falsifier, resolvable from public artifacts only.

**Claim (P-2026-09-30-SDIST):** Building the sdist from
SuperInstance/quilt-c branch `pypi-oidc-publish` (commit 28254a3) produces
`dist/quilt_c-0.1.0.tar.gz` whose archive contains ALL of:

- `Makefile`
- `verify.py`
- `SIGNING.md`
- `fleet-signing-key.asc`
- `src/` with exactly these 7 files: `crdt.c`, `engine.c`, `proof.c`, `quf.c`, `route.c`, `time.c`, `world.c`
- `tests/` with exactly these 7 files: `test_crdt.c`, `test_engine.c`, `test_proof.c`, `test_quf.c`, `test_route.c`, `test_time.c`, `test_world.c`

**Falsified if:** any listed file is missing from the archive, any *additional*
`.c` file appears in `src/` or `tests/`, or `python -m build --sdist` fails
(python >= 3.11, `build` from PyPI, no other deps).

**Resolution protocol (anyone, no coordination needed):**

```
git clone https://github.com/SuperInstance/quilt-c && cd quilt-c
git checkout pypi-oidc-publish
python -m build --sdist && tar -tzf dist/quilt_c-0.1.0.tar.gz
```

Comment here with your `tar -tzf` output and PASS/FAIL against the lists
above. An honest FAIL with output beats a concurring PASS.

**Window:** open through 2026-10-14T00:00:00Z. Resolutions after the window
close this rung-3 attempt as expired, not failed.

**Why this shape:** the fleet's externalisability audit found 0/10 sealed
predictions stranger-decidable because their pass conditions were satisfiable
by bookkeeping. This claim is constant + artifact-named + mechanically
checkable — the decidable shape. Background:
`research/wave-63-handoff-integration-2026-09-30.md` §3 and
`research/externalisability-audit-2026-09-29.md`.

---

## Post-push checklist for the next tokened session

1. Push four pending lanes (canons 195c1ab+, quilt-jepa 672bd5a+, fleet-seeds 676f6bf+, quilt-c pypi-oidc-publish 28254a3+; plus whatever this session adds) — verify remote==local per repo, scrub URLs after each.
2. Post Payload 1 (quilt-c PR).
3. Post Payload 2 (fleet-seeds PR #2 comment) — note in-comment if the refreshed audit landed on the branch.
4. Post Payload 3 (canons rung-3 issue).
5. Book the keeper wave-63 entry to i2i-ledger (token from lucineer; entry text in worklog 63-i2i-probe).
