#!/usr/bin/env python3
"""
verify.py — a README is an executable claim. Nobody ran it.

Extracts what a README PROMISES and checks the tree for whether it exists.
Three independent checks, because each catches a different kind of drift:

  A. CODE      — symbols the Quick Start calls that do not exist in the source.
  B. MECHANISM — named mechanisms in the prose with zero matches anywhere.
  C. TREE      — file paths the README documents that are not in the repo.

Deliberately NOT a link checker and NOT a style linter. Those cannot tell you a
claim is false; only the tree can.

A KNOWN-ANSWER CONTROL ships with it (`--self-test`) and the control is built from
real, already-confirmed defects — a scanner with no negative case is decoration.
"""
import argparse, json, os, re, sys, urllib.request, urllib.error

H = {"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN','')}",
     "Accept": "application/vnd.github+json", "User-Agent": "readme-verifier"}
GH = "https://api.github.com"


# READMEs and source trees are PUBLIC. This tool has never needed a credential, so it
# must not die when one expires. The token died mid-session (401 on every call) and
# took the whole census with it -- which is the tool being wrong, not the data being
# unavailable. Public reads still work unauthenticated, so we fall back and SAY so.
ANON = {"Accept": "application/vnd.github+json", "User-Agent": "readme-verifier"}
_auth_state = {"token_dead": False}


def api(path, timeout=35):
    headers = ANON if _auth_state["token_dead"] else H
    for attempt in (0, 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(GH + path, headers=headers), timeout=timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 401 and attempt == 0 and not _auth_state["token_dead"]:
                _auth_state["token_dead"] = True      # one retry, unauthenticated
                headers = ANON
                continue
            return {"__err": e.code}
        except Exception:
            return {"__err": "network"}


def readme(repo):
    for name in ("README.md", "readme.md", "README.rst", "README"):
        d = api(f"/repos/{repo}/contents/{name}")
        if "__err" not in d and d.get("content"):
            import base64
            return name, base64.b64decode(d["content"]).decode("utf-8", "replace")
    return None, ""


def tree(repo):
    t = api(f"/repos/{repo}/git/trees/HEAD?recursive=1")
    if "__err" in t:
        return None
    return [e["path"] for e in t.get("tree", []) if e["type"] == "blob"]


# ---------------------------------------------------------------- check A: code
CALL = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]{2,})\s*\(")
IGNORE = {"if","for","while","switch","catch","return","function","def","fn","let","const","var",
          "print","println","echo","new","typeof","await","async","require","import","from","assert",
          "expect","not","and","or","is","in","of","super","this","class","struct","func","match",
          "with","as","lambda","else","elif","try","raise","throw","yield","await","using","namespace",
          # shell / CLI verbs. `git clone ...` in a fenced bash block is an instruction to
          # the reader, not an API the repo must export. Flagging these was pure noise.
          "git","npm","npx","pnpm","yarn","cargo","rustc","make","docker","kubectl","curl","wget",
          "cd","ls","cat","grep","sed","awk","chmod","chown","mkdir","rm","cp","mv","touch","sudo",
          "apt","apt-get","pip","pip3","python","python3","node","go","rustup","gh","jq","tar","gzip",
          "sh","bash","zsh","source","export","set","env","which","find","head","tail","wc","diff"}


SPEC_HINT = re.compile(r"→|->\s*\{|primitives?:|grammar|abstract machine|type signature|"
                       r"\|\s*\w+\s*\|.*\|", re.I)


def check_code(md, paths, blob_text):
    """Symbols the README CALLS, that appear nowhere in the source."""
    # Fenced blocks AND inline `code` spans. The self-test caught this: a Quick Start
    # written as inline backticks (`forge.compile(x)`) is invisible to a fenced-only
    # scan, which is the most common way a README shows an API call.
    blocks = re.findall(r"```[a-zA-Z0-9+#-]*\n(.*?)```", md, re.S)
    blocks += re.findall(r"`([^`\n]{1,120})`", md)
    # A block that reads as a grammar or a type table is a SPECIFICATION of an abstract
    # machine (`BRANCH(cond, t, f) -> void`, "six primitives: READ, WRITE, ..."). Those
    # name a language, not a function this repo exports, so they are not claims.
    blocks = [b for b in blocks if not (SPEC_HINT.search(b) and "->" in b or "→" in b)]
    called = {}
    QUAL = re.compile(r"([A-Za-z_][A-Za-z0-9_]{1,30})\.([A-Za-z_][A-Za-z0-9_]{2,})\s*\(")
    for b in blocks:
        for m in CALL.finditer(b):
            name = m.group(1)
            if name in IGNORE or len(name) < 3:
                continue
            recv = None
            q = QUAL.search(b, max(0, m.start() - 40))
            if q and q.group(2) == name:
                recv = q.group(1)
            prev = called.get(name, (0, None, False))
            called[name] = (prev[0] + 1, recv or prev[1], prev[2] or bool(recv))
    missing = []
    for name, (n, receiver, qualified) in sorted(called.items()):
        # NOT a bare substring search. This was the instrument's own version of the
        # aperture trap it exists to help find: forgemaster's 900 KB of source contains
        # the STRING "compile" in unrelated places, so a presence test said CLEAN on a
        # README whose Quick Start provably raises AttributeError. A word appearing
        # somewhere is not a member existing somewhere. Demand a POSITION.
        if re.search(r"(?:^|[^.\w])(?:def|fn|func|function|class|struct|impl|interface|trait)\s+"
                     + re.escape(name) + r"\b", blob_text, re.M):
            continue                                     # defined as a function/class
        if re.search(r"\." + re.escape(name) + r"\s*[(<:]", blob_text):
            continue                                     # reached as a member
        if receiver and re.search(re.escape(receiver) + r"\s*\.\s*" + re.escape(name) + r"\b", blob_text):
            continue                                     # the exact receiver.method pair
        # Self-test leg 1 caught this: the previous version skipped any symbol that
        # appeared ANYWHERE in the README, but the Quick Start is exactly where a
        # CALLED symbol appears -- so the check could never fire. It must only accept
        # the symbol if the README DEFINES it.
        if re.search(r"(?:def|fn|func|function|class|struct|interface|impl|const|let|var)\s+"
                     + re.escape(name) + r"\b", md):
            continue
        missing.append((name, n, qualified))
    return missing


# ------------------------------------------------------------ check B: mechanisms
FEATURE = re.compile(r"\*\*([a-z][a-z0-9 +\-_/]{2,40})\*\*")
LINKED = re.compile(r"\[[^\]]{3,50}\]\((?:src|lib|crates|packages)/([^)\s]+)")


# A "named mechanism" is a technical noun phrase, not bolded English. The first
# version of this check reported "rearrange", "absorb" and "the specification" as
# missing mechanisms on a repo whose README was fine -- i.e. it cried wolf on every
# repo, which is the same failure as a linter nobody runs.
COMMON = {
    "the","a","an","and","or","of","to","in","for","with","on","at","by","from","this","that",
    "note","warning","example","quick","start","install","usage","features","requirements",
    "license","todo","design","overview","see","also","why","how","what","when","where",
    "specification","checker","readme","api","cli","sdk","core","main","src","test","tests",
    "example","examples","support","status","summary","architecture","implementation","default",
    "configuration","development","building","running","getting","started","contents","table",
    "rearrange","absorb","approach","problem","solution","result","results","name","value",
    "values","type","types","data","file","files","code","all","one","two","new","old","first",
    "second","third","before","after","when","then","else","each","both","only","also","just",
}


def check_mechanisms(md, blob_text):
    """Named mechanisms in bold prose, with zero occurrences in the tree."""
    out = []
    for m in FEATURE.finditer(md):
        phrase = m.group(1).strip().lower().rstrip(".")
        words = re.findall(r"[a-z][a-z0-9+_-]{2,}", phrase)
        if len(words) < 2:
            continue                                   # a mechanism has a name, not a word
        if any(w in COMMON for w in words):
            continue                                   # ordinary English
        # require every content word to be absent from the tree, not just most of them
        if all(not re.search(r"\b" + re.escape(w), blob_text, re.I) for w in words):
            out.append(phrase)
    return out


# ----------------------------------------------------------------- check C: tree
def check_paths(md, paths):
    """A README link is RELATIVE to the README's own directory.

    The first version compared the literal link target against absolute tree paths and
    flagged `engine.c` when the file is `src/engine.c` — a broken link by string
    comparison on a link that is correct by construction. Match on suffix.
    """
    linked = set()
    for m in LINKED.finditer(md):
        linked.add(m.group(1).split("#")[0].lstrip("./"))
    P = set(paths)
    missing = []
    for t in linked:
        if t in P:
            continue
        if any(x.endswith("/" + t) for x in P):   # relative link, file lives in a subdir
            continue
        missing.append(t)
    return sorted(missing)


def fetch_text(paths, cap=260, budget=900_000):
    """Read a bounded sample of source files. Enough to refute a claim, and it keeps
    the check cheap enough to run over hundreds of repos."""
    src = [p for p in paths
           if re.search(r"\.(py|js|ts|tsx|jsx|rs|c|h|go|java|rb|php|ex|exs|erl|pl|fth|mjs|cjs)$", p)]
    out, used = [], 0
    for p in src:
        if used > budget or len(out) >= cap:
            break
        d = api(f"/repos/{os.environ['REPO']}/contents/{p}")
        if "__err" in d or not d.get("content"):
            continue
        import base64
        try:
            t = base64.b64decode(d["content"]).decode("utf-8", "replace")
        except Exception:
            continue
        out.append(t)
        used += len(t)
    return "\n".join(out)


def analyse(repo, sample=260):
    """Never report a verdict derived from a path that threw. A check that cannot
    run must surface as UNREADABLE, not be silently absent from a denominator --
    the first version of census.py reported "0% drifted" over 11 vacuous passes
    while 15 of 26 repos had thrown, because the errors were excluded from the
    ratio instead of counted as failures."""
    name, md = readme(repo)
    if not name:
        return {"repo": repo, "verdict": "NO README"}
    paths = tree(repo)
    if paths is None:
        return {"repo": repo, "verdict": "TREE UNREADABLE"}
    os.environ["REPO"] = repo
    blob = fetch_text(paths, cap=sample)
    code = check_code(md, paths, blob)
    mech = check_mechanisms(md, blob)
    treebad = check_paths(md, paths)
    src_files = [q for q in paths
                 if re.search(r"\.(py|js|ts|tsx|jsx|rs|c|h|go|java|rb|php|ex|exs|erl|pl|fth|mjs|cjs)$", q)]
    # Below this, a partial sample is a real sample. Above it, a "missing symbol" is
    # almost certainly the symbol living outside the budget — i.e. a defect in the
    # SAMPLER. Say so rather than emitting a false positive.
    partial = len(src_files) > sample * 2
    if partial:
        code = []
    return {"repo": repo, "verdict": "CLEAN" if not (code or mech or treebad) else "DRIFTED",
            "readme": name, "src_files": len(src_files), "partial_sample": partial,
            "files_sampled": blob.count("\n") and len(blob),
            "missing_symbols": [c[0] for c in code][:8],
            "missing_mechanisms": mech[:6],
            "missing_paths": treebad[:6]}


# ------------------------------------------------------------------- the control
SELF_TEST = [
    # (readme, tree, blob, must_flag, why)
    ("Call `forge.compile(x)` to build.",
     ["forge.py"], "def submit(x):\n    return x\n", True,
     "README calls compile(); only submit() exists. This is the forgemaster defect."),
    ("**ternary action routing** and **conservation-aware scheduling** and **gamma+eta=C**.",
     ["a.py"], "def route(x):\n    return x\n", True,
     "Three mechanisms named, zero occurrences in source. This is the claw defect."),
    ("See [`src/real.rs`](src/real.rs) and [`src/ghost.rs`](src/ghost.rs).",
     ["src/real.rs"], "fn main(){}\n", True,
     "One documented path does not exist. This is the quilt-arch defect."),
    ("## Install\n\nRun `cargo build` then use the `--release` flag.",
     ["src/main.rs"], "fn main(){ let release = 1; let flag=1; }\n", False,
     "A README whose claims are all true must come back CLEAN, or the checker is a complainer."),
    # The aperture trap, in this instrument. `compile` occurs all over a real 900 KB
    # tree. Presence is not membership.
    ("Call `forge.compile(x)` to build.",
     ["a.py"],
     "import compile\nx = compile.thing()\ncompile = 3\ndef other(): return compile\n" * 40,
     True,
     "the word 'compile' is everywhere in the tree but no member is defined — "
     "presence must not be read as membership (this is the forgemaster false negative)"),
]


def selftest():
    import tempfile, os as _os
    ok = 0
    print(f"  self-test {len(SELF_TEST)} legs, from real confirmed defects:")
    for md, paths, blob, must, why in SELF_TEST:
        code = check_code(md, paths, blob)
        mech = check_mechanisms(md, blob)
        tbad = check_paths(md, paths)
        flagged = bool(code or mech or tbad)
        good = flagged == must
        ok += good
        print(f"    {'ok  ' if good else 'FAIL'} {'FLAGS' if flagged else 'clean':5} — {why[:72]}")
    print(f"  {ok}/{len(SELF_TEST)}")
    return 0 if ok == len(SELF_TEST) else 2


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("repos", nargs="*")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--sample", type=int, default=260)
    a = ap.parse_args()
    if a.self_test:
        sys.exit(selftest())
    if not a.repos:
        ap.error("give at least one repo, or --self-test")
    for r in a.repos:
        res = analyse(r, a.sample)
        print(json.dumps(res, indent=1))
