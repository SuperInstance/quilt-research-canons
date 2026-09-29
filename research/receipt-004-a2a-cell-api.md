---
title: Receipt 004 — the A2A cell API, executable
date: 2026-09-29
artifact: quilt-c PR #5 (cell_api.py), branch mavis/cell-api-ref
status: open, not merged
---

Chain link **Days 51-70** now has something in it. A reference implementation, not a
deployment — and the distinction is asserted by the artifact, not just claimed in prose.

## The design question

The JEV room's answer to "bespoke wire format or converge on MCP/A2A" was:

> **Wire format is commodity. Cell semantics are the asset.**

So the ONE resource is the **Cell** — Quilt already treats every cell as a live addressable
capability, and the API just stops hiding it behind a UI. The five opcodes become the methods
on that resource.

```
GET  /v1/cells/{addr}            -> {addr, kind, dials, neighbors, version, state_digest}
GET  /v1/cells?query=&kind=&op=  -> discovery without grep
POST /v1/cells/{addr}/ops        -> {op: BIND|LINK|EFFECT|VIEW|TICK, args} -> a receipt
GET  /v1/receipts/{receipt_id}   -> {id, op, target, input_hash, output_hash, signatures, parent}
```

Every mutation returns a receipt, and receipts chain by `parent`. An agent can pass
`parent_receipt` into its next call and produce a verifiable lineage **without trusting this
service**. That is the two-reader requirement met by the protocol rather than by the discipline.

## Real vs not real, and the self-test asserts both

| REAL | NOT REAL |
|---|---|
| the 5 opcodes, against this repo's C99 semantics | **no authentication** — an unauthenticated mutation endpoint is not shippable |
| receipt chain, chained by parent, hashed | **flat addressing** — the real graph is 4D |
| hard guards: VIEW pure, TICK monotone, BIND idempotent by content | **no network transport** — dispatch is a function call |
| fail-closed with distinct error codes | |
| FNV-1a 64 state digests, matching the kernel | |

Leg 12 checks those limits **structurally** — inspecting the running object for a signature
verifier, an HTTP handler, a hierarchical address walk — not by grepping the source. The first
version grepped, and matched its own docstring describing those markers. **A test reading its
own description of itself passes for the wrong reason.**

## Five bugs the artifact found in itself

1. **Failures returned un-sealed.** A caller could not tell from a receipt whether an op had
   been attempted. Fixing that produced the second bug: op bodies returned a *sealed receipt*
   which `op()` sealed again — a receipt nested inside a receipt. The fix is the split: bodies
   return **results**, `op()` seals **once**.
2. **The idempotence law was unsatisfiable.** BIND bumped `version` unconditionally, so
   re-binding identical dials changed the version key. The law was not being tested, it was
   being contradicted. Idempotence is a property of *content*.
3. **`TICK` silently succeeded on a missing cell.** Graph-scoped is legitimate; succeeding on
   a typo'd address was accidental. Now it takes the graph or an existing cell, and says which.
4. **The state digest raised `OverflowError` on negative dials.** Repeated TICK drives
   odd-index dials negative; the canonical serializer writes 4-byte **unsigned** ints. The
   C99 kernel has the same hazard. Fixed by explicit saturation — which is also the right
   domain semantic: a quota reads zero, not -1.
5. **Receipts were pointers, not snapshots.** Found by running `--demo`, **not** by the tests.
   A BIND receipt printed `[100, 0]` at seal time and `[101, -1]` after a later TICK mutated
   the same list in place.

**Bugs 4 and 5 are the same class as the two earlier ones in `verify.py`** — a self-referential
digest, and wall-clock timings inside a hashed body. The artifact looked right and was not,
**because nothing read it twice.**

> That is the argument for reading receipts by diffing runs rather than by inspecting them once.

## Fail-closed, four fault classes

| injected fault | caught by |
|---|---|
| VIEW mutates state | `VIEW is pure — hard guard` |
| BIND bumps version unconditionally | `BIND creates and is idempotent` |
| receipt chain drops the parent link | `receipts chain by parent` |
| receipt holds a live pointer | `a receipt is an immutable snapshot` |

13/13 self-test legs, four independently confirmed failure modes.

## Why it is not a new repo

The fleet has 4,856 repos and 33 stars. A 4,857th repo **is** the failure mode the
greater-SuperInstance read identified, not a fix for it. This belongs next to the kernel whose
semantics it shares, so the reference port stays the one runnable thing.

## The demo is a boat

`--demo` runs a 48-hour quota boat through the opcodes, because the cell graph was always going
to be about a deck, a hold, and a limit — and an API is easier to argue about against something
that means that than against a synthetic grid.

```
BIND    boat-1/quota   mutating=True   {"dials": [100, 0], "version": 1}
LINK    graph          mutating=True   {"edge": ["boat-1/quota", "boat-1/hold"]}
EFFECT  boat-1/quota   mutating=True   {"propagated_to": []}
VIEW    boat-1/hold    mutating=False  {"dials": [100, 0], ...}
TICK    graph          mutating=True   {"tick": 1, "delta": 1, "cells": 2}
receipts: 6   graph_digest: 848e51f2941e193f2d8d9a3ee85a6d01
```

## What would make it shippable

In order, and none of them are mine to decide alone:

1. **Auth.** Ed25519 per agent, capability tokens scoped by cell and op. Until then there is no
   deployment, only a design.
2. **4D addressing.** The flat string keys are a stand-in. The real graph is 4D and the
   addressing is the interesting part.
3. **Transport.** Converge on MCP/A2A adapters rather than a bespoke socket — the semantics
   are the asset and the wire format is not.
4. **An outside reader.** Every check so far has been by the person who wrote it, in a second
   language. Still not external.
