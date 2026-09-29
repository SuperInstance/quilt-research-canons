#!/usr/bin/env python3
"""
lint_legibility.py — can a zero-shot agent get in?

THE MEASURED PROBLEM

Census of 100 fleet repos, fetched by a script that had never seen the fleet:

    repos with a README                       98 / 100   98%
    repos with a RUNNABLE first command       68 / 100   68%
    repos with NO description                 20 / 100   20%   <- invisible to search

So almost every repo LOOKS documented and only two-thirds can be entered. The README is
not the binding constraint. The missing first command is.

THE FIVE OBLIGATIONS

  L1  DESCRIPTION   one line saying what this is, so the repo is findable at all
  L2  FIRST COMMAND a fenced block whose first non-comment line is something runnable
  L3  RECEIPT       what observable output proves it worked
  L4  NEGATIVE      what it does NOT do
  L5  TEACHING      for anything that wraps an API, does the error surface name the fix?

L5 is the one nobody has and the one that costs the most. See ERRORS.md.
"""
from __future__ import annotations
import re, sys, json, os

FENCE = re.compile(r"```(\w*)\s*\n(.*?)```", re.S)
RECEIPT_WORDS = re.compile(
    r"\b(receipt|output|prints|emits|assert\w*|verif\w+|should print|expected output|"
    r"exits? with|stdout|reports)\b", re.I)
NEGATIVE_WORDS = re.compile(
    r"\b(does not|doesn't|does NOT|not yet|limitation|caveat|scope|non-goal|"
    r"out of scope|not supported|unimplemented|won't|will not)\b", re.I)
TEACHING = re.compile(
    r"\b(error|4\d\d|5\d\d|exception|troubleshoot|gotcha|common mistakes|"
    r"if you see)\b", re.I)
CMDISH = re.compile(r"^(\$|#|>|\S)")
PURE_COMMENT = re.compile(r"^\s*(#|\*|//|<!--)")

OBLIGATIONS = ("L1-description", "L2-first-command", "L3-receipt",
               "L4-negative-space", "L5-teaching-errors")


def first_commands(md: str) -> list[str]:
    out = []
    for _lang, body in FENCE.findall(md):
        for line in body.splitlines():
            s = line.strip()
            if not s:
                continue
            if PURE_COMMENT.match(s) or s.startswith(("$", ">")):
                continue
            out.append(s)
            break
    return out


def lint(md: str, has_description: bool = True) -> list[dict]:
    findings = []

    if not has_description:
        findings.append(dict(check="L1", ok=False,
                             detail="no repo description, so the repo is unsearchable"))

    cmds = first_commands(md)
    if not cmds:
        findings.append(dict(check="L2", ok=False,
                             detail="no fenced block with a runnable first line"))
    elif len(md) > 200 and not RECEIPT_WORDS.search(md):
        findings.append(dict(check="L3", ok=False,
                             detail="a command exists but nothing says what output proves it worked"))

    if len(md) > 200 and not NEGATIVE_WORDS.search(md):
        findings.append(dict(check="L4", ok=False,
                             detail="nothing states what this does NOT do"))

    if len(md) > 200 and not TEACHING.search(md):
        findings.append(dict(check="L5", ok=False,
                             detail="no error/troubleshooting surface, so a wrong first call teaches nothing"))

    return findings


def verdict(findings) -> str:
    """Three grades, and L2 decides the first one.

    A repo that fails L2 is INVISIBLE to a zero-shot agent no matter how good its prose
    is, because there is nothing to run. That is the whole point of grading on L2
    first.

    (An earlier version of this function returned ENTERABLE before it could reach the
    WEAK branch, so ENTERABLE-WEAK was unreachable and the fleet report printed
    '0 are ENTERABLE-WEAK' as if it were a finding. It was a dead branch reported as a
    result. Same class as every other silent-wrong-number tonight.)"""
    failed = {f["check"] for f in findings if not f["ok"]}
    if "L2" in failed:
        return "INVISIBLE"
    if not failed:
        return "ENTERABLE"
    return "ENTERABLE-WEAK"


if __name__ == "__main__":
    path = sys.argv[1]
    desc = "--no-desc" not in sys.argv
    md = open(path).read()
    f = lint(md, desc)
    print()
    print("  LEGIBILITY LINT — %s" % os.path.basename(path))
    print("  " + "=" * 62)
    print("  verdict: %s" % verdict(f))
    for x in f:
        print("  [FAIL] %s  %s" % (x["check"], x["detail"]))
    if not f:
        print("  [ ok ] all five obligations met")
    print()
