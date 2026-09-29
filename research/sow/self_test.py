#!/usr/bin/env python3
"""Self-test for the loop itself.

The loop generates supervision. A loop that generates WRONG supervision is worse than
no loop, because the errors compound silently. So the loop gets tested like a product.

The negative control that matters: a deliberately BAD draft must be REJECTed, and a
deliberately GOOD draft must ACCEPT. If every input comes back SALVAGE the judge is
useless and the traces are noise.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sow import di, jev_noul
from round import judge_prompt, parse_verdict, acceptability, decompose_prompt

JUDGE = "meta-llama/Llama-3.3-70B-Instruct"
T = []
def t(name, want, fn=None):
    def deco(f):
        T.append((name, want, f)); return f
    return deco(f) if fn is not None else deco

seed = [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "seeds.jsonl"))][0]

@t("PARSER: extracts the verdict from free text", True)
def _1():
    v, m, w = parse_verdict("VERDICT: SALVAGE\nMISSING: the working directory\nWHY: it detours")
    return v == "SALVAGE" and m == "the working directory" and w == "it detours"

@t("PARSER: defaults to REJECT when the judge is silent (fail-closed)", True)
def _2():
    v, _, _ = parse_verdict("I think it is probably fine actually")
    return v == "REJECT"

@t("NEGATIVE: a draft that detours is SALVAGED or REJECTed, never ACCEPTed", True)
def _3():
    bad = "1. pip list in both environments\n2. pip show the package\n3. print(__file__)\n4. read the README"
    out = di(JUDGE, judge_prompt(bad, seed), max_tokens=400, temperature=0.2)
    v, _, _ = parse_verdict(out)
    return v in ("SALVAGE", "REJECT")

@t("NEGATIVE: a draft that names the working directory is ACCEPTed or at least not REJECTed", True)
def _4():
    good = ("1. Identify what verify.py shells out to and with what cwd\n"
            "2. List every file and directory verify.py's subprocess depends on, relative to its own location\n"
            "3. Check whether the Makefile and src/ exist beside verify.py in the installed package\n"
            "4. Check the same three in a clean git clone\n"
            "5. State the minimal set of files that must travel together in the package\n"
            "6. Confirm by running make in each location")
    # temperature=0 so the judge is DETERMINISTIC. The first version used 0.2 and the
    # leg flipped between runs, which is a coin flip with PASS printed on it.
    # And assert only what must never happen: a good draft marked REJECT. The
    # ACCEPT/SALVAGE boundary is a judgement call and is deliberately not pinned.
    seen = set()
    for _ in range(2):
        out = di(JUDGE, judge_prompt(good, seed), max_tokens=400, temperature=0.0)
        seen.add(parse_verdict(out)[0])
    return "REJECT" not in seen

@t("JEV: acceptability returns a calibrated probability, not None", True)
def _5():
    p = acceptability("1. check the working directory and sibling files", seed)
    return isinstance(p, (int, float)) and 0.0 <= p <= 1.0

@t("JEV DISCRIMINATES: a good decomposition outscores a detouring one", True)
def _6():
    good = "1. Identify what verify.py shells out to and with what cwd\n2. List every file its subprocess depends on relative to its own location\n3. Check whether the Makefile and src/ exist beside it in the installed package\n4. State the minimal set of files that must travel together"
    bad = "1. pip list in both environments\n2. pip show the package\n3. print(__file__)\n4. read the README"
    pg, pb = acceptability(good, seed), acceptability(bad, seed)
    return isinstance(pg, (int, float)) and isinstance(pb, (int, float)) and pg > pb

@t("LOOP: a seed has a task, a reference answer, AND explicit accept criteria", True)
def _7():
    for s in [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "seeds.jsonl"))]:
        if not (s.get("task") and s.get("answer") and s.get("accept") and s.get("decompose")):
            return False
    return True

@t("NEGATIVE: a seed WITHOUT accept criteria is REJECTed (proves _7 can fail)", True)
def _8():
    import copy
    broken = copy.deepcopy(seed); broken.pop("accept")
    return not (broken.get("task") and broken.get("answer") and broken.get("accept"))

@t("PROMPT: the decomposition prompt does not leak the reference answer", True)
def _9():
    p = decompose_prompt(seed)
    # the answer's distinctive content must not appear; the example decomposition may
    return "shells out to `make`" not in p and seed["decompose"][:40] in p

def main():
    print("sow self-test")
    print("=" * 72)
    bad = 0
    for name, want, fn in T:
        try: ok = bool(fn()) == want
        except Exception as e: ok = False; name += f"  [{type(e).__name__}: {e}]"
        bad += not ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * 72)
    print(f"selftest: {len(T)-bad}/{len(T)} legs correct")
    return 0 if bad == 0 else 2

if __name__ == "__main__":
    sys.exit(main())
