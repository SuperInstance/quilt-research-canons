# the-wheel

**Sequential spine, parallel angles, and the negative space as the work queue.**

## The shape

```
spine (one item at a time, ordered by READINESS not by file position)
  └── N parallel ANGLES on the same goal
        └── each angle emits CELLS
              └── each cell carries what the angle could NOT determine
                    └── those gaps BECOME the next spine item
```

That last arrow is the wheel. **An angle that cannot determine something has produced the
next thing to look at.** The negative space is not a report section — it is the queue.

## The six angles

`claims` · `code` · `runnable` · `calibrate` · `adversary` · `negative`

Same goal, incompatible methods. An angle that cannot conclude says `GAP` and names what
it would need. Two angles that disagree produce a `contradicts` edge rather than a
compromise.

## The cells are the fleet's own

Every cell serialises as the canonical envelope — `witness_id`, `prev_witness_id`,
`cell_id`, `substrate`, `polarity`, `timestamp`, `payload` — with `witness_id` an FNV-shaped
content hash. A knowledge graph that is not in the substrate's own format is another
island, and the substrate already has one.

## Measured over the corpus

```
151 cells   223 terms   bag-of-words cosine, local
  SUPPORTED   56
  GAP         82
  UNKNOWN     13
```

**More than half the corpus is unmapped, and the wheel knows which half and why.** Each
GAP cell names its own obstruction — "cannot tell whether a code path exists under a
different name", "reproducing stored results was not performed by this pass".

## The finding the negative-space map produced

**14 of 31 papers have no attached artifact of any kind** — no repo, no code, no stored
results, no appendix. For those the wheel cannot help, because there is nothing to press.
They are **write** tasks, not **press** tasks, and no amount of tooling changes that. That
is the single most useful thing the map said, and it is the kind of statement a summary
of the papers would never have produced.

Two papers (`03-Confidence-Cascade`, `06-Tile-Algebra-Formalization`) appear **twice** on
the spine, because each exists in both `white-papers/` and `white-papers/final/` and the
copies differ. A spine that silently walks both versions of a paper is a spine doing the
work twice and learning it once.

## Vectorisation, honestly

**Cloudflare Vectorize is unavailable on this account** — it returns
`vectorize.unknown_content_type` (1005) for this token. The known working alternative is
Workers KV plus in-Worker cosine for corpora under ~25MB.

So the backend here is a local bag-of-words index with cosine by dot product, behind a
swappable interface. **It is not a vector database and does not pretend to be one.** A
knowledge index that claims a capability it lacks is the exact failure this wheel exists
to detect, and shipping one inside the wheel that detects it would be embarrassing.

## Run it

```bash
python3 wheel.py --scan                 # the spine, ranked by readiness
python3 wheel.py --cell 29-Spreadsheet  # all six angles on one paper, as cells
python3 wheel.py --index                # whole corpus to a searchable index
python3 wheel.py --index --query "chain"
```

## Limits

- Readiness is keyword-matched, not semantic. A repo named after nothing the paper says
  will read as absent. That is the honest failure direction — it under-claims.
- The `calibrate` angle is declared but not yet implemented against real outcome data.
- No angle writes back to the substrate yet. The cells are shaped for it; the wiring is
  the next thing.
