#!/usr/bin/env python3
"""round.py — one full round of the loop, end to end.

  seed (expensive, saved whole)
    -> small model drafts a decomposition (cheap, off the big budget)
    -> JEV scores acceptability with a CALIBRATED probability
    -> the judge issues ACCEPT / SALVAGE / REJECT with the specific missing step
    -> the trace is appended

The trace is the product. Round N's REJECTs are round N+1's training data.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sow import di, jev_noul, SMALL, HERE, JUDGE_RUNS, JUDGE_UNANIMITY

JUDGE = "meta-llama/Llama-3.3-70B-Instruct"

def decompose_prompt(seed, task=None):
    return f"""You are decomposing a task so a smaller model can attempt it.

TASK: {task or seed['task']}

Here is a worked example of a GOOD decomposition for a similar kind of task:
{seed['decompose']}

Produce a numbered decomposition of THIS task, 4 to 8 steps. Each step must be a
concrete action someone could take, not a category. Do not solve the task."""

def judge_prompt(output, seed, task=None):
    return f"""You are judging a small model's first-pass decomposition against what would
actually pass. Be strict and specific.

TASK: {task or seed['task']}

WHAT PASSING LOOKS LIKE:
{seed['accept']}

THE SMALL MODEL'S OUTPUT:
{output[:1800]}

Verdict, exactly one of:
ACCEPT  - this would pass, or leads to the answer
SALVAGE - the direction is right but it is not enough; name the specific missing step
REJECT  - wrong approach, or would not lead to the answer

Format:
VERDICT: <ACCEPT|SALVAGE|REJECT>
MISSING: <the one specific step it lacks, or NONE>
WHY: <one sentence>"""

def acceptability(output, seed, task=None):
    return jev_noul(
        state=f"TASK: {task or seed['task']}\n\nDECOMPOSITION: {output[:1500]}",
        instructions=("Carrying out this decomposition would lead a careful engineer to the "
                      "correct root cause of the problem described."),
        true="Yes — following this decomposition reaches the root cause.",
        false="No — this decomposition leads somewhere other than the root cause, or "
              "stalls on an unnecessary detour.")

def parse_verdict(txt):
    v = "REJECT"
    m = __import__('re').search(r'VERDICT:\s*(ACCEPT|SALVAGE|REJECT)', txt, __import__('re').I)
    if m: v = m.group(1).upper()
    missing = ""
    m2 = __import__('re').search(r'MISSING:\s*(.+)', txt)
    if m2: missing = m2.group(1).strip()
    why = ""
    m3 = __import__('re').search(r'WHY:\s*(.+)', txt, __import__('re').S)
    if m3: why = m3.group(1).strip().split("\n")[0]
    return v, missing, why

def run_round(seed, model, task=None, trace_path=None):
    t0 = time.time()
    draft = di(model, decompose_prompt(seed, task), max_tokens=800)
    p = acceptability(draft, seed, task)
    # The judge is a SAMPLE, not a verdict. Run it N times and keep the distribution.
    # Unanimity is required for ACCEPT; anything else collapses to the most conservative
    # verdict observed, because an undecided judge should not promote a draft.
    verdicts, missing, why = [], "", ""
    for _ in range(JUDGE_RUNS):
        jt = di(JUDGE, judge_prompt(draft, seed, task), max_tokens=500, temperature=0.0)
        v, m, w = parse_verdict(jt)
        verdicts.append(v)
        if m and not missing: missing = m
        if w and not why: why = w
    counts = {v: verdicts.count(v) for v in set(verdicts)}
    if JUDGE_UNANIMITY and len(counts) == 1:
        verdict = verdicts[0]
    else:
        order = ["REJECT", "SALVAGE", "ACCEPT"]
        verdict = min(verdicts, key=lambda v: order.index(v)) if verdicts else "REJECT"
    rec = {
        "schema": "sow/trace@v1",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed_id": seed["id"],
        "model": model,
        "task": task or seed["task"],
        "draft": draft.strip(),
        "jev_acceptability": p,
        "verdict": verdict,
        "verdicts": verdicts,
        "judge_unanimous": len(counts) == 1,
        "missing": missing,
        "why": why,
        "agree": None,   # filled in below
        "seconds": round(time.time()-t0, 1),
    }
    # CROSS-CHECK: does the calibrated probability agree with the judge?
    # When it does, the judge is confirmed by a second instrument. When it does not,
    # that disagreement IS the finding and gets recorded.
    if isinstance(p, (int, float)):
        rec["agree"] = (p > 0.7) == (verdict == "ACCEPT")
        rec["judge_runs"] = JUDGE_RUNS
    with open(trace_path or os.path.join(HERE, "traces.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec

if __name__ == "__main__":
    seeds = [json.loads(l) for l in open(os.path.join(HERE, "seeds.jsonl"))]
    models = sys.argv[1:] or SMALL[:2]
    for s in seeds:
        for m in models:
            r = run_round(s, m)
            print(f"  {r['seed_id']:28} {r['model'].split('/')[-1][:22]:24} "
                  f"jev={str(r['jev_acceptability']):6} {r['verdict']:8} "
                  f"runs={r['verdicts']} agree={r['agree']}", flush=True)
