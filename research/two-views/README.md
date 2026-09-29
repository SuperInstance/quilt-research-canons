# two-views — one substrate, a human view and an agent view

## The property

They are **not two implementations that agree today**. They are one walk over one dict,
rendered twice.

```
substrate  ──►  project_human()  ->  cols + rows, with a receipt on every cell
            └─►  project_agent()  ->  flat cells, stable addr, digest, error contract
```

A bug that changes a cell changes it in both. A schema drift in the agent view is a bug in
the human view too — which is why there is no sync step to forget. The self-test checks
this at every frame, and the negative control corrupts one view and asserts the check fires.

## What the human view buys

**Rewind.** A substrate you cannot step backwards through is a log. One you can is a
timeline, and a timeline is the only form you can reason about. The frames are append-only
— that is the no-deletion doctrine — and it is also what makes rewind free. Writing to
frame 20 does not change frame 5, and the test asserts exactly that.

## What the agent view buys

No rendering decisions. A stable `addr` as the identifier, so a consumer can hold a
reference across frames. A `digest` over the cell addresses so a caller can cheap-check it
has not drifted. And a declared error contract, so an agent can fail against the surface
rather than guess at it:

```json
"errors": {
  "shape": {"error": "str", "detail": "str", "frame": "int|null"},
  "codes": ["UNKNOWN_CELL", "NO_SUCH_FRAME", "RATE_LIMITED"],
  "retry": "idempotent on GET; 429 carries Retry-After"
}
```

An agent does not need a table. It needs a contract it can fail against.

## The receipts

Every cell carries a sha256 over `addr | value`. Two properties, both tested:

- **stable** — a cell's receipt does not change when *other* cells move
- **sensitive** — changing a cell's value changes *its* receipt

A human row shows the receipt truncated to 8 chars inline, because a number a human
cannot trace is a number they have to take on faith.

## Self-test: 15/15, and the two gaps it found

The suite checks the data and the wiring. Two things it did **not** check until a fault
injection went uncaught:

1. **The render.** Disabling `render()` entirely — a page that renders nothing — passed all
   14 original legs. Now there is a leg that fails if the render path stops writing the
   table body, the agent JSON, or the tab toggle. **Both** injections are caught.
2. **The rewind actually rewinding.** The first page incremented a counter and re-rendered
   the same data. The negative control now constructs that exact counter-example and
   asserts the detector rejects it, so the leg cannot pass by restating leg 11.

## What this is not

No server, no auth, no network, no dependencies. It is the two projections with the
substrate behind them, so the question "do the human and the agent see the same thing" has
an answer you can run rather than an agreement you have to trust.

The history in the shipped page is hand-authored — a boat's night, written, with real
receipts attached. The receipt proves a value was set; it does not prove the boat did that,
and the page says so. See `REVIEW.md` for the five users who made that explicit.

## Running it

```sh
python3 self_test.py
open index.html
```

## Fleet position

- **chiaroscuro** — renders the frame; a residual is a sparse edge set
- **exoj** — external non-collapsing vectorised scratch paper; a residual is what a plane
  intersection holds
- **agent-microtone** — the agent-facing surface this view is shaped for
- **MicroMoth-quilt** — where the receipts go, so the timeline is measured over time rather
  than authored once
