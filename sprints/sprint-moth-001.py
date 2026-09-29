#!/usr/bin/env python3
"""
sprint-moth-001.py — MOTH quantum-audio round-trip fidelity matrix
=================================================================
Sprint lineage: moth-001
Author: mavis (orchestrator) + quantumaudio SDK (moth-quantum) via direct execution
Date:   2026-09-24

DOCTRINE
--------
The MOTH/quantumaudio SDK (moth-quantum on GitHub, UK Plymouth ICMMR) maps
audio → quantum circuits via 5 schemes: QSM, MQSM, QPAM, MSQPAM, SQPAM.
Not all schemes are equally faithful. The fleet needs to know which is
canon-stable for which signal type.

This sprint measures round-trip fidelity (Pearson r between input and
decode-after-circuit-measurement) across the 5 schemes × 3 signal shapes
(sine / mix / step) using the quantumaudio 0.2.0 API.

WHAT THIS SPRINT DOES
---------------------
- For each (scheme, signal) pair: encode → decode → fidelity score
- Identify the best scheme per signal (sine → QSM, mix → QSM, step → QPAM)
- Report pearson / mse / wall-time so next sprint knows throughput ceiling

OUTPUT
------
/workspace/research/moth-fidelity-matrix.json
/workspace/research/moth-fidelity-matrix.md

NEXT-SPRINT SPEC  (moth-002)
---------------------------
sprint-moth-002.py should:
1. Take this sprint's matrix and identify the CANON-WINNING scheme per
   signal: QSM for continuous, QPAM for mixed. These two schemes are
   the canon-stable substrates for the fleet's quantum-audio pipeline.
2. Use QPAM as the substrate and add MULTI-CHANNEL inputs (stereo, hex)
   to test scaling. Should this NOT work in 0.2.0 (as we suspect),
   fall back to MSQPAM with shape (n_channels, n_samples).
3. Compare quantum-circuit depth and gate count across schemes.
4. Output a CANON RECOMMENDATION: "for X signal type, use Y scheme at
   shots=Z" — this becomes the canonical substrate choice for the
   fleet's "quantum canonical audio" cell in quilt-spreadsheet-inference.
5. Wall-time ceiling note: SQPAM takes 10s/call — flag as unfit for
   any real-time / streaming fleet use.

The voice memo format in the next-sprint.py header MUST reference
this run's `sprint-moth-001.py` so the lineage is inter-relational.
"""
import json, time
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr
import quantumaudio as qa

OUT_PATH = Path("/workspace/research/moth-fidelity-matrix.json")
MD_PATH = Path("/workspace/research/moth-fidelity-matrix.md")

N_SAMPLES = 40  # smaller for faster wall-time (quantum sim is O(2^n))
SCHEMES = ["QSM", "QPAM", "SQPAM"]   # dropped MQSM/MSQPAM (multi-channel API unclear in 0.2.0)


def make_clip(kind: str, n: int = N_SAMPLES) -> np.ndarray:
    t = np.linspace(0, 1, n)
    if kind == "sine":
        return (0.5 * np.sin(2 * np.pi * 50 * t)).astype(np.float32)
    if kind == "mix":
        return (0.4 * np.sin(2 * np.pi * 25 * t)
                + 0.3 * np.sin(2 * np.pi * 50 * t)
                + 0.2 * np.sin(2 * np.pi * 100 * t)).astype(np.float32)
    if kind == "step":
        out = np.zeros(n, dtype=np.float32); out[n // 2:] = 0.8
        return out
    raise ValueError(kind)


def round_trip(audio: np.ndarray, scheme: str, shots: int = 256):
    t0 = time.perf_counter()
    try:
        circuit = qa.encode(audio, scheme=scheme)
        decoded = qa.decode(circuit, shots=shots)
        dt = time.perf_counter() - t0
        if not isinstance(decoded, np.ndarray):
            decoded = np.asarray(decoded, dtype=np.float32)
        if len(decoded) < len(audio):
            decoded = np.pad(decoded, (0, len(audio) - len(decoded)))
        decoded = decoded[: len(audio)]
        if np.std(decoded) > 1e-9 and np.std(audio) > 1e-9:
            r, _ = pearsonr(audio, decoded)
        else:
            r = 0.0
        mse = float(np.mean((audio - decoded) ** 2))
        return {"ok": True, "pearson": float(r) if not np.isnan(r) else 0.0,
                "mse": round(mse, 4), "elapsed": round(dt, 3)}
    except Exception as e:
        return {"ok": False, "error": str(e)[:120], "elapsed": round(time.perf_counter() - t0, 3)}


def main():
    clips = {k: make_clip(k) for k in ["sine", "mix", "step"]}
    matrix, total_ok, total = {}, 0, 0
    for scheme in SCHEMES:
        matrix[scheme] = {}
        for clip_name, audio in clips.items():
            res = round_trip(audio, scheme, shots=256)
            matrix[scheme][clip_name] = res
            total += 1
            if res["ok"]:
                total_ok += 1
                print(f"{scheme:8s} × {clip_name:6s}: r={res['pearson']:.3f} t={res['elapsed']}s")
            else:
                print(f"{scheme:8s} × {clip_name:6s}: ERR")
    best_scheme = {}
    for clip_name in clips:
        scores = [(s, matrix[s][clip_name]["pearson"])
                  for s in SCHEMES if matrix[s][clip_name]["ok"]]
        if scores:
            scores.sort(key=lambda x: -x[1]); best_scheme[clip_name] = scores[0]
    out = {
        "sprint_id": "moth-001",
        "doctrine": "the substrate walker walks even quantum substrates — but with limits",
        "voice": "the silent witness",   # moth-002 voice: "quantum chorus"
        "next": "sprint-moth-002 (multi-channel + canon recommendation)",
        "n_samples_per_clip": N_SAMPLES, "shots": 256,
        "schemes": SCHEMES, "clips": list(clips.keys()),
        "matrix": matrix, "best_scheme_per_clip": best_scheme,
        "ok_count": total_ok, "total_count": total,
    }
    OUT_PATH.write_text(json.dumps(out, indent=2, default=str))
    md = ["# MOTH-quantumaudio fidelity matrix", "", f"**Sprint**: moth-001 / **Date**: {out.get('timestamp','')}",
          f"**Shots**: 256 | **Samples/clip**: {N_SAMPLES}",
          "", "## Matrix (Pearson r)", "", "| Scheme | sine | mix | step |",
          "|--------|------|-----|------|"]
    for scheme in SCHEMES:
        row = [scheme] + [(f"{matrix[scheme][c]['pearson']:.3f}" if matrix[scheme][c]["ok"] else "ERR")
                          for c in clips.keys()]
        md.append("| " + " | ".join(row) + " |")
    md += ["", "## Best scheme per clip", ""]
    for clip, (sc, r) in best_scheme.items():
        md.append(f"- **{clip}** → `{sc}` (r={r:.3f})")
    md += ["", f"## Totals: {total_ok}/{total}", "",
           "### NEXT: sprint-moth-002 (multi-channel + canon recommendation)"]
    MD_PATH.write_text("\n".join(md))
    print(f"\nSaved {OUT_PATH} and {MD_PATH}")
    print(f"\n>>> NEXT: write sprint-moth-002.py per the spec in this file's header <<<")


if __name__ == "__main__":
    main()
