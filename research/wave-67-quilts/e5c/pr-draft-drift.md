# dissent(route 17): buzz histogram diverged from baseline — suspected route-field drift

> Auto-promoted by the wave-67 dissent loop (research/wave-67-quilts/e5c/loop.py).
> Dissent law: buzz is non-authoritative; promotion into a PR is how the fabric
> speaks. This PR is the fabric's voice, not a human's.

## Evidence
- fire tick index 58 (absolute tick 0x0000002A, past the u32 wrap — frame law held)
- KL(baseline || window) = 4.7235 on decoded route 17 (threshold 2.0)
- affected receiver position: the cell whose expected route is 17; producer words decode to a different route

## Sample cell words (last 4 acks on the affected route)
```
00772242
00632242
00642242
006D2242
```

## Reproduce / conformance
```
cd research/superinstance-bitlaw
python3 gen.py && python3 frame_gen.py   # regenerate codecs from the single source
node conformance.test.mjs && node frame.test.mjs
```

## Requested change
Producer's route encoding drifted (shift-class bug: `route << 1`). Re-align the
producer with the cell-word law (spec.json route:8 shift:8) — do NOT widen the
receivers to accept both encodings; the contract is the law, the fabric adapts.
