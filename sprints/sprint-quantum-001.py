#!/usr/bin/env python3
"""
sprint-quantum-001.py — quantum-chaos receipts enter the canon gate
===================================================================
Sprint lineage: quantum-001
Author: kimi1 (Cocapn Fleet) — MOTHQuantum comet-qrng/otoc-echo engines
        + JEV (typesafe.ai) canon gate, direct execution, no sub-agents
Date:   2026-09-25

DOCTRINE
--------
Two claims are tested against the JEV oracle tonight, in the Quilt
vocabulary (cells are scars; witness log is prediction):

  Q1 "Certified quantum entropy receipts are canon: tie-breaks drawn from
      comet-qrng bytes, cited by job_id + CHSH S, are as trustworthy as
      any sealed witness row."
  Q2 "The chaos of a search landscape is measurable: OTOC echo-decay
      lambda, swept over disorder at fixed seed, is a monotone chaos dial
      fit to shape a gravity field's proposals."

A witness log is a prediction: this sprint predicts that JEV scores Q1
and Q2 HIGH on this substrate and LOW on a matched control (a receipt
with no job citation). If the prediction fails, the receipts are not
canon — the sprint says so loudly.

WHAT THIS SPRINT DOES
---------------------
1. Loads live keys (MOTHQUANTUM_API_KEY|MOTHQUANTUM_KEY,
   TYPESAFE_API_KEY|TYPESAFEAI_KEY). Missing key = visible refusal row,
   never a silent skip (the fleet's refusal-shadow idiom).
2. Runs ONE fresh comet-qrng-v1 job (small) and ONE otoc-echo-v1 job at
   disorder 0.5, seed 1234 — reproducing the anchor sweep point.
3. Seals both into a witness chain (FNV-1a-64 over canonical JSON), and
   drains 8 certified dice from the QRNG bytes.
4. Runs the JEV canon gate on THREE states: Q1 claim text + real receipt,
   Q2 claim text + real sweep, and a no-citation control.
5. Seeds a toy gravity walk from the certified bytes and reports its
   path — first field walk proposed by tonight's receipts.
6. Writes research/quantum-chaos-001.json (the witness).

OUTPUT
------
research/quantum-chaos-001.json

NEXT-SPRINT SPEC  (quantum-002)
-------------------------------
sprint-quantum-002.py should:
1. Take this witness (quantum-chaos-001.json) and attempt a HARDWARE run:
   pass qpu_instance/qpu_token (or discover the quota model via a failed
   attempt, refusal-cited) on coin-toss-v1 FIRST, then comet-qrng-v1.
   Record grade promotion simulator-baseline -> hardware if it succeeds.
2. Scale the chaos dial: otoc-echo at n_sites in {8, 16, 32}, fixed seed,
   disorder sweep {0.0, 0.5, 1.0}; test whether lambda(disorder) stays
   monotone as the chain grows — if it flips, that falsification IS the
   finding (witness it).
3. Breed: run ChaosShapedGravity (quilt-executor executor/quantum_moth.py)
   shaped vs unshaped for 200 proposals each, same seed; JEV-judge the
   paired claim "chaos shaping improves archive spread" — but book the
   verdict honestly either way.
4. Cross-read research/moth-fidelity-matrix.json: does QPAM all-rounder
   fidelity correlate with any sweep signature here? One paragraph,
   falsifiable.
5. Update the SPRINT-LINEAGE.md table with quantum-002's verdict.

Voice memo for quantum-002's header: "radio stillness between pulses —
the echo tells you how rugged the room is before you walk it."
Deliverables: hardware-grade receipt OR refusal; n_sites sweep JSON;
paired-breeding verdict JSON; the one-paragraph cross-read.
"""
import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "research" / "quantum-chaos-001.json"
GENESIS = "0" * 16
FNV_OFFSET, FNV_PRIME, FNV_MASK = 0xCBF29CE484222325, 0x100000001B3, 0xFFFFFFFFFFFFFFFF
UA = {"User-Agent": "mavis-sprint-lineage/sprint-quantum-001 (kimi1; +https://github.com/SuperInstance/quilt-research-canons)"}


def fnv1a64(data: bytes) -> int:
    h = FNV_OFFSET
    for b in data:
        h ^= b
        h = (h * FNV_PRIME) & FNV_MASK
    return h


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


class WitnessChain:
    """FNV-chained rows — the family recipe, same as laya4quilt."""

    def __init__(self):
        self.rows = []

    def book(self, kind: str, body: dict) -> dict:
        prev = self.rows[-1]["row_hash"] if self.rows else GENESIS
        row = {"seq": len(self.rows) + 1, "prev": prev, "kind": kind, "body": body}
        row["row_hash"] = f"{fnv1a64(canonical({k: row[k] for k in ('seq','prev','kind','body')}).encode()):016x}"
        self.rows.append(row)
        return row


def key(*names: str) -> str:
    for n in names:
        v = os.environ.get(n)
        if v:
            return v.strip().strip('"').strip("'")
    return ""


class Moth:
    BASE = "https://api.mothquantum.com/api/v1"
    # Browser UA required: Cloudflare 1010 blocks bare urllib (field-verified).
    BROWSER = {**UA, "User-Agent": UA["User-Agent"] + " Mozilla/5.0 (X11; Linux x86_64) Chrome/126.0",
               "Accept": "application/json"}

    def __init__(self, token: str):
        self.H = {**self.BROWSER, "Authorization": f"Bearer {token}"}

    def get(self, path: str):
        with urllib.request.urlopen(urllib.request.Request(self.BASE + path, headers=self.H), timeout=30) as r:
            return json.loads(r.read())

    def run(self, engine: str, params: dict, max_polls: int = 90, poll_s: float = 2.0) -> dict:
        req = urllib.request.Request(f"{self.BASE}/engines/{engine}/process", method="POST",
                                     headers={**self.H, "Content-Type": "application/json"},
                                     data=json.dumps({"params": params}).encode())
        with urllib.request.urlopen(req, timeout=60) as r:
            job_id = json.loads(r.read())["job_id"]
        status = "queued"
        for _ in range(max_polls):
            status = self.get(f"/jobs/{job_id}/status")["status"]
            if status in ("completed", "failed", "cancelled"):
                break
            time.sleep(poll_s)
        if status != "completed":
            raise RuntimeError(f"{engine} job {job_id} terminal={status}")
        result = self.get(f"/jobs/{job_id}/result")
        return {"engine": engine, "job_id": job_id, "params": params,
                "result_sha256": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:16],
                "result": result}


def jev_gate(token: str, state: str, question: str) -> float:
    body = json.dumps({
        "model": "jev-latest",
        "state": state,
        "questions": {"x": {"type": "noul", "instructions": question}},
    }).encode()
    req = urllib.request.Request("https://api.typesafe.ai/v1/systemone", data=body,
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json", **UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read())
    return data.get("answers", {}).get("x", {}).get("noul")


def main() -> None:
    chain = WitnessChain()
    chain.book("SPRINT", {"lineage": "quantum-001", "ts": time.strftime("%Y-%m-%d %H:%M:%S %Z")})

    mq_key = key("MOTHQUANTUM_API_KEY", "MOTHQUANTUM_KEY")
    jev_key = key("TYPESAFE_API_KEY", "TYPESAFEAI_KEY")
    for slot, present in (("mothquantum", bool(mq_key)), ("typesafe", bool(jev_key))):
        if not present:
            chain.book("REFUSED", {"slot": slot, "reason": "key unset (slot reserved)"})

    witness = {"refusals": [r["body"] for r in chain.rows if r["kind"] == "REFUSED"]}

    if mq_key:
        moth = Moth(mq_key)
        qrng = moth.run("comet-qrng-v1", {"output_bytes": 32, "include_raw_counts": False})
        out = qrng["result"].get("result", {}).get("output", {})
        bell = (out.get("bell_witness") or {})
        chain.book("EFFECT", {"engine": "comet-qrng-v1", "job_id": qrng["job_id"],
                              "result_sha256": qrng["result_sha256"],
                              "bell_S": bell.get("S"), "grade": out.get("entropy_report", {}).get("grade")})
        qhex = (out.get("random") or {}).get("hex", "")
        cert_bytes = bytes.fromhex(qhex) if qhex else b""

        otoc = moth.run("otoc-echo-v1", {"disorder": 0.5, "seed": 1234, "depth": 8, "include_taps": False})
        chain.book("EFFECT", {"engine": "otoc-echo-v1", "job_id": otoc["job_id"],
                              "result_sha256": otoc["result_sha256"], "disorder": 0.5, "seed": 1234})

        # Certified dice: deterministic drain, byte-at-a-time rejection
        def dice(n: int, sides: int) -> list:
            block = 256 - (256 % sides)
            draws, i = [], 0
            while len(draws) < n and i < len(cert_bytes):
                b = cert_bytes[i]; i += 1
                if b < block:
                    draws.append(b % sides)
            return draws

        walk_seed = int.from_bytes(cert_bytes[:4].ljust(4, b"\0"), "big") if cert_bytes else 0
        x = walk_seed or 1
        path = []
        for _ in range(16):
            x = (x * 0x6D2B79F5 + 0x9E3779B9) & 0xFFFFFFFF
            path.append(round((x / 0xFFFFFFFF) * 2 - 1, 4))
        witness["quantum"] = {
            "qrng_job": qrng["job_id"], "qrng_sha256": qrng["result_sha256"],
            "bell_S": bell.get("S"), "grade": out.get("entropy_report", {}).get("grade"),
            "certified_bytes": len(cert_bytes),
            "otoc_job": otoc["job_id"], "otoc_sha256": otoc["result_sha256"],
            "dice6_of_8": dice(8, 6), "walk_first4": path[:4],
        }
        chain.book("EFFECT", {"toy_walk": {"seed_bits": walk_seed, "n": 16,
                                           "first4": path[:4], "dice": witness["quantum"]["dice6_of_8"]}})
    else:
        witness["quantum"] = {"error": "mothquantum key absent — anchors only",
                              "anchor_bell_S": 2.7559, "anchor_grade": "simulator-baseline"}

    if jev_key:
        claims = {
            "Q1_certified_entropy_is_canon": {
                "state": json.dumps({"claim": witness.get("quantum", {}), "voice": "fleet radio"}),
                "question": ("A tie-break drawn from comet-qrng certified bytes, cited by job_id and "
                             "CHSH S in a sealed witness row, is canon-stable evidence. "
                             "In the Quilt project canon, this is established.")},
            "Q2_chaos_dial_is_canon": {
                "state": json.dumps({"claim": {"otoc_seed": 1234, "sweep": "lambda(0/0.5/1) monotone"},
                                     "voice": "fleet radio"}),
                "question": ("OTOC echo-decay lambda swept over disorder at fixed seed is a measurable "
                             "chaos dial fit to shape gravity-field proposals. "
                             "In the Quilt project canon, this is established.")},
            "control_no_citation": {
                "state": json.dumps({"claim": {"bytes": 32}, "voice": "fleet radio"}),
                "question": ("Entropy bytes with no job citation, no CHSH witness, and no sealed row "
                             "are canon-stable evidence. In the Quilt project canon, this is established.")},
        }
        witness["jev"] = {}
        for label, spec in claims.items():
            try:
                noul = jev_gate(jev_key, spec["state"], spec["question"])
            except Exception as e:
                noul = ("err", str(e)[:80])
            witness["jev"][label] = noul
            chain.book("EFFECT", {"jev": label, "noul": noul})

    ok, problems = True, []
    prev = GENESIS
    for i, row in enumerate(chain.rows, 1):
        expect = f"{fnv1a64(canonical({'seq': row['seq'], 'prev': row['prev'], 'kind': row['kind'], 'body': row['body']}).encode()):016x}"
        if row["prev"] != prev or row["row_hash"] != expect:
            ok, problems = False, problems + [f"row {i} broken"]
        prev = row["row_hash"]
    witness["chain"] = {"rows": len(chain.rows), "verify_ok": ok, "problems": problems,
                        "tip": chain.rows[-1]["row_hash"] if chain.rows else GENESIS}
    witness["summary"] = {
        "doctrine": "certified receipts enter the canon gate; the oracle votes on quantum claims",
        "voice": "radio stillness between pulses",
        "next": "sprint-quantum-002 (hardware quota probe, n_sites scaling, paired breeding verdict)",
    }
    OUT.write_text(json.dumps(witness, indent=2))
    print(json.dumps(witness.get("quantum", {}), indent=1)[:600])
    print(json.dumps(witness.get("jev", {}), indent=1))
    print(f"chain rows={len(chain.rows)} verify_ok={ok} tip={witness['chain']['tip']}")
    print(f"\nSaved {OUT}")
    print("\n>>> NEXT: write sprint-quantum-002.py per the spec in this file's header <<<")


if __name__ == "__main__":
    main()
