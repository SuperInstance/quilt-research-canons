# Deliverable — Adversarial audit of C3 "val AUC 1.0 (64/64, p 5.4e-20)"

## Summary

Cloned `SuperInstance/quilt-gpu-lab` read-only and audited the C3 latent-probe claim
end to end: pre-registration, data pipeline, probe script, AUC/binomial code, and the
shipped 15 MB of float16 embeddings, which I re-scored independently. **Verdict:
EVAL-BUG.** 41 of the 64 val clips are byte-identical (same sha256) to training clips,
and **all 32 "real" val clips are duplicates — the validation set contains zero unseen
real examples**, so the reported "64/64, p 5.4e-20" is a training-set score. The
pre-registration is genuine, early, and untampered; the AUC and binomial code are
correct and the p-value is conservative. Re-scored under group-disjoint splits the
separation is *still* perfect, so the effect is real and the number is wrong.

## Changed files

Created (read-only audit; nothing written to the audited repo):
- `/tmp/scout_out/gpu-lab-auc-verdict.md` — full verdict report (14.8 KB)
- `/tmp/scout_out/gpu-lab/` — repo clone (read-only, 292 MB)
- `/workspace/.mavis/plans/plan_e77091f8/outputs/gpu-lab-auc-claim/deliverable.md` — this file
- `/workspace/.mavis/plans/plan_e77091f8/board.md` — progress entry appended

## Notes for the verifier

**Verdict: EVAL-BUG.** Headline evidence:
- `data/c3/manifest.json` and `results/c3_probe.json` agree on all 256 sha256 (0
  disagreements), so contamination is a property of the data, not a reporting artifact.
- 41/64 val clips byte-identical to train; 32/32 val *real* clips duplicated;
  0 unseen real clips; the 27-clip `still` family (`color=c=gray`) is 1 unique file.
- Root cause in `experiments/c3_make_data.py:real_t0s()` — the deterministic t0 grid
  spans the same [0, 4.30 s] of the same two 6.1 s videos for train and val, so grid
  points collide exactly (94% / 82% consecutive frame overlap). Split is by index, not
  by group. `verify_clips()` passes because the manifest faithfully records the defect.

**Credit where due — do not misread this as a fabricated result:**
- Pre-registration is real: `1436cf5` @ 12:47:09 -0800, result `289a615` @ 13:23:36,
  plan blob `a3fee48b…` touched by exactly one commit and unchanged to HEAD, not
  edited in the result commit. The only post-prereg code change is a legitimate decode
  bugfix. But its `INVALID_HARNESS` list is entirely mechanical (dtype, sha, OOM, frame,
  processor key) and contains **no train/val contamination clause** — so it could not
  have caught this.
- **The effect survives honest splits.** Using the shipped embeddings with
  group-disjoint splits: leave-one-real-video-out AUC 1.0000 (87/87, both folds);
  leave-one-synth-family-out 17/17, 19/23→23/23, 17/17, 16/16, 17/17. Nothing
  scientific is overturned; only the booked evidence and the "ANY encoder" framing.
- AUC code is a correct exact Mann-Whitney; I reproduced val AUC 1.0000 / acc 1.0000
  on both layer B and layer A from the stored vectors.
- p-value: `2^-64 = 5.4210e-20`, exactly what `binom_tail_ge(64,64)` returns. It is the
  *accuracy* tail, hence **conservative** (exact Mann-Whitney p for 32v32 complete
  separation is 0.0993). **No tie inflation** — the 7 duplicate `still` items are all
  synth-side and `auc_exact` only compares cross-class pairs. The defect is the null
  model (64 independent unseen items assumed; 23 existed, 32 were in the centroid).
- The "label-flip" flag is a real **code** bug misdiagnosed as a data issue. `yt=1`
  marks real so the head learns high-score⇒real, but `score_layer` does
  `pred = 0 if s > 0 else 1` (s>0 read as synth) — opposite conventions. I re-ran
  their head in numpy: 0.0000 with their rule, **1.0000 / 64-of-64** with the sign
  fixed. Their own `train_auc=0.0` was the tell. Does not affect the primary gate.
- Scoping concern: synth = 5 lavfi test patterns (incl. a constant gray square) vs
  center-crops of two 6.1 s videos. A ≥0.90 gate was never at risk, so the
  "cells can key on this structure in ANY encoder" sentence overreaches.

**What I could NOT check:** no GPU here, so I did not re-run Cosmos3-Edge — I verified
the analysis pipeline against the shipped embeddings but cannot independently confirm
they were produced by the vision tower rather than fabricated. The `.rgb` pixels are
uncommitted (only `manifest.json` is in git), so the sha256s are attested twice by two
committed files but not re-hashed by me. I did not audit K3c, C1, or C2. Full scope
statement in §7 of the report.
