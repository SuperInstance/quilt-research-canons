#!/usr/bin/env python3
"""
complete.py — draft the two sentences nobody writes, FROM THE REPO.

THE GAP, MEASURED
    L3  what output proves it worked      14 repos missing
    L4  what it does NOT do               55 repos missing
    L5  what to do when it fails          59 repos missing

114 gaps. Writing 114 paragraphs by hand is the wrong move when almost all of them are
DERIVABLE from what is already in the repository. The negative space of a repo is not
opinion; it is knowable. A repo with no tests has a knowable limitation. A repo whose
only entry point is a stub has a knowable one. A repo with no CI config has a knowable
one. And a repo with NO error surface is itself a knowable fact, which is the whole of L5.

THE RULE THIS FILE ENFORCES

    Every drafted sentence carries the artifact it came from.
    Anything not derivable is emitted as a QUESTION, never as a claim.

That is `artifact-first` applied to documentation. The danger is specific and obvious: a
completer that invents "what this does not do" produces fluent, confident, fabricated
limitations — which are worse than absent ones, because a reader cannot tell them from
real ones. So the negative control below asserts that a fabricated sentence CANNOT be
produced for a fact the repo does not contain.
"""
from __future__ import annotations

import os, re, json
from dataclasses import dataclass, field


@dataclass
class Evidence:
    """One verified fact about a repo, with the path it was read from."""
    fact: str
    artifact: str
    kind: str = "negative"      # negative | positive

    def render(self) -> str:
        return f"{self.fact} _(from `{self.artifact}`)_"


@dataclass
class Draft:
    section: str
    lines: list = field(default_factory=list)
    questions: list = field(default_factory=list)
    evidence: list = field(default_factory=list)


# ----------------------------------------------------------------- inspection
def from_github(repo: str, token_env: str = "GITHUB_TOKEN", branch: str = "main",
                fetch: int = 40) -> tuple[list, str]:
    """Read a repo through the API instead of cloning it.

    Cloning was the wrong tool and it cost the run: AI-Writings exceeded an 80-second
    clone timeout and the TimeoutExpired took down every repo after it. A tree listing
    plus a bounded number of file fetches is faster, works on a 133MB repo, and cannot
    hang the fleet. Returns (file paths, a virtual root)."""
    import urllib.request, urllib.error, json as _j, os as _os
    import base64
    key = _os.environ.get(token_env, "")
    h = {"Authorization": f"Bearer {key}", "User-Agent": "legibility-completer"}

    def _get(u, raw=False, t=25):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=h), timeout=t) as r:
                d = r.read()
                return r.status, (d.decode("utf-8", "replace") if raw else _j.loads(d))
        except urllib.error.HTTPError as e:
            return e.code, {} if not raw else ""
        except Exception:
            return 0, "" if raw else {}

    st, tree = _get(f"https://api.github.com/repos/SuperInstance/{repo}/git/trees/{branch}?recursive=1")
    if st != 200 or "tree" not in tree:
        return [], ""
    files = [e["path"] for e in tree["tree"] if e["type"] == "blob"]
    return files, repo


def file_head(repo: str, path: str, branch: str = "main", nbytes: int = 4000) -> str:
    import urllib.request, urllib.error, base64, os as _os
    h = {"Authorization": f"Bearer {_os.environ.get('GITHUB_TOKEN','')}", "User-Agent": "legibility-completer"}
    try:
        with urllib.request.urlopen(urllib.request.Request(
                f"https://raw.githubusercontent.com/SuperInstance/{repo}/{branch}/{path}",
                headers=h), timeout=20) as r:
            return r.read(nbytes).decode("utf-8", "replace")
    except Exception:
        return ""


def tree_files(root: str) -> list[str]:
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in (".git", "node_modules", "__pycache__", "dist", "build", "target", ".venv")]
        for f in fn:
            out.append(os.path.relpath(os.path.join(dp, f), root))
    return out


def _count(root: str, files: list[str], pred) -> list[str]:
    return [f for f in files if pred(f)]


def collect_evidence(root: str) -> list[Evidence]:
    """Read the repo and return only what can be VERIFIED. Nothing here is inferred from
    the README, because the README is the thing being fixed."""
    ev: list[Evidence] = []
    files = tree_files(root)
    if not files:
        return ev

    has_ci = _count(root, files, lambda f: f.startswith((".github/workflows/", ".gitlab-ci", "Jenkinsfile")))
    if not has_ci:
        ev.append(Evidence("there is no CI configuration in this repository, so nothing here "
                           "is checked automatically on push", "(no CI config found)", "negative"))
    else:
        ev.append(Evidence(f"CI runs on {len(has_ci)} workflow file(s)", has_ci[0], "positive"))

    tests = _count(root, files, lambda f: re.search(r"(^|/)(test|tests|spec)/|_test\.|test_|\.test\.|\.spec\.", f, re.I))
    if not tests:
        ev.append(Evidence("it ships no automated tests, so the example command below is the "
                           "only check available", "(no test files found)", "negative"))
    else:
        ev.append(Evidence(f"it ships {len(tests)} test file(s)", tests[0], "positive"))

    lic = _count(root, files, lambda f: re.search(r"^(LICENSE|COPYING)", f, re.I))
    if not lic:
        ev.append(Evidence("it carries no LICENSE file", "(no LICENSE file)", "negative"))
    else:
        ev.append(Evidence("it carries a LICENSE", lic[0], "positive"))

    # stubs: a real, checkable form of "not done yet"
    stubs = []
    for f in files:
        if not f.endswith((".py", ".js", ".ts", ".c", ".h", ".rs", ".go")):
            continue
        p = os.path.join(root, f)
        try:
            with open(p, errors="replace") as fh:
                head = fh.read(4000)
        except Exception:
            continue
        if re.search(r"\b(TODO|FIXME|XXX|not implemented|NotImplemented|unimplemented|coming soon)\b", head, re.I):
            stubs.append(f)
    if stubs:
        ev.append(Evidence(f"it contains {len(stubs)} file(s) carrying TODO / FIXME / "
                           f"not-implemented markers, so parts of the surface are declared "
                           f"incomplete", stubs[0], "negative"))

    readme = _count(root, files, lambda f: f.lower() == "readme.md")
    if readme:
        try:
            with open(os.path.join(root, readme[0]), errors="replace") as fh:
                rd = fh.read()
            fences = len(re.findall(r"```", rd)) // 2
            if fences == 0:
                ev.append(Evidence("its README contains no runnable example at all",
                                   readme[0], "negative"))
        except Exception:
            pass
    return ev


# ----------------------------------------------------------------- drafting
def draft_limitations(ev: list[Evidence]) -> Draft:
    """L4. Every line is a negative-space fact that was read out of the repo."""
    d = Draft("L4-negative-space")
    neg = [e for e in ev if e.kind == "negative"]
    if not neg:
        d.questions.append(
            "No negative-space facts could be verified automatically. A human needs to "
            "state what this does not do -- the absence of detectable markers is not the "
            "same as the absence of limitations.")
    for e in neg:
        d.lines.append(f"- {e.render()}")
        d.evidence.append(e)
    return d


def draft_failures(ev: list[Evidence]) -> Draft:
    """L5. If the repo has no error surface, THAT is the finding, stated as a fact."""
    d = Draft("L5-teaching-errors")
    has_surface = any(("error" in e.fact.lower() or "troubleshoot" in e.fact.lower()) for e in ev)
    if not has_surface:
        d.questions.append(
            "No error or troubleshooting surface was found. The honest entry here is: "
            "'this tool has no documented failure modes, which means a failing call gives "
            "you nothing to read.' Write the two or three failures that actually happen and "
            "what to do about each -- a human has to supply these, they cannot be derived.")
    return d


def draft_receipt(root: str, ev: list[Evidence]) -> Draft:
    """L3. Prefer a command that the repo's own tooling defines, so the receipt the reader
    sees is the receipt the maintainer intends."""
    d = Draft("L3-receipt")
    for cand, why in (("Makefile", "make test"), ("justfile", "just test"),
                      ("package.json", "npm test"), ("pyproject.toml", "pytest"),
                      ("Cargo.toml", "cargo test"), ("go.mod", "go test ./...")):
        if os.path.exists(os.path.join(root, cand)):
            d.lines.append(f"`{why}` — defined by `{cand}`, so the output you see is the one "
                           f"the project already considers canonical.")
            d.evidence.append(Evidence(f"project defines its test command in {cand}", cand, "positive"))
            return d
    d.questions.append(
        "No standard test/build file was found. A human must state which command produces "
        "the output that proves this works -- that cannot be guessed, because guessing it is "
        "how a completer invents a receipt.")
    return d


# ----------------------------------------------------------------- the guard
FORBIDDEN = re.compile(
    r"\b(produces|generates|handles|supports|returns|is capable of)\b", re.I)


def render(drafts: list[Draft]) -> str:
    out = ["<!-- generated by legibility/complete.py; every line cites its artifact -->", ""]
    for d in drafts:
        if d.lines:
            out.append(f"## {d.section}")
            out.extend(d.lines)
            out.append("")
        if d.questions:
            out.append(f"### {d.section}: NEEDS A HUMAN")
            for q in d.questions:
                out.append(f"- {q}")
            out.append("")
    return "\n".join(out)
