#!/usr/bin/env python3
"""gift_lint — the reusable static auditor for AI-gifted code (wave-67 tooling).

The gift pattern: fluent prose + confident structure + arithmetic that runs +
code that never compiled + outputs that were never produced. This linter runs
the cheapest REAL check per language and prints a verdict table:

  .py   -> py_compile (syntax)          [semantics: run only with explicit --run]
  .js   -> node --check (syntax)        [DOM/GL semantics unverifiable headless]
  .rs   -> rustc parse+resolve (no deps)  [needs crate deps => reported as such]
  .glsl -> identifier audit: declared vs used uniforms/ins/locals, unused vars,
           and the specific 'writes-into-but-never-reads' dead-code shape
  *.md  -> embedded claimed outputs are NOT verifiable (prose is not a receipt)

Usage: python3 gift_lint.py <file_or_dir> [...]
Exit 0 if every file passes its cheapest real check; 1 otherwise.
"""
import re, subprocess, sys, tempfile, pathlib

GLSL_BUILTIN = {"texture", "sin", "cos", "mix", "fract", "floor", "ceil", "dot", "cross", "normalize",
                "length", "abs", "min", "max", "clamp", "smoothstep", "step", "pow", "exp", "sqrt"}
GLSL_TYPES = {"void", "float", "int", "uint", "bool", "vec2", "vec3", "vec4", "ivec2", "ivec3", "ivec4",
              "uvec2", "uvec3", "uvec4", "bvec2", "bvec3", "bvec4", "mat2", "mat3", "mat4",
              "sampler2D", "usampler2D", "isampler2D"}

def lint_glsl(path):
    src = path.read_text()
    src_nc = re.sub(r"//[^\n]*", "", src)
    src_nc = re.sub(r"/\*.*?\*/", "", src_nc, flags=re.S)
    src_nc = re.sub(r"^#.*$", "", src_nc, flags=re.M)          # strip #version etc.
    src_nc = re.sub(r"\.\s*(\w+)", " ", src_nc)                # strip member access/swizzles (.x, .r)
    declared = set(re.findall(r"\b(?:uniform|in|out)\s+\w+\s+(\w+)", src_nc))
    for m in re.finditer(r"\b(\w+)\s+(\w+)\s*(?:=|;|\[)", src_nc):
        if m.group(1) in GLSL_TYPES:
            declared.add(m.group(2))
    # function declarations AND their parameters
    for m in re.finditer(r"\b(\w+)\s+(\w+)\s*\(([^)]*)\)", src_nc):
        if m.group(1) in GLSL_TYPES | {"void"}:
            declared.add(m.group(2))
        for pm in re.finditer(r"\b(?:\b(?:in|out|inout)\b)?\s*(?:\b(?:lowp|mediump|highp)\b)?\s*(\w+)\s+(\w+)", m.group(3)):
            if pm.group(1) in GLSL_TYPES:
                declared.add(pm.group(2))
    words = set(re.findall(r"\b([a-zA-Z_]\w*)\b", src_nc))
    known = declared | GLSL_BUILTIN | GLSL_TYPES | {"main", "precision", "highp", "mediump", "lowp",
                                                    "if", "else", "for", "while", "return", "in", "out",
                                                    "uniform", "layout", "location", "true", "false", "version"}
    undefined = sorted(w for w in words - known if not re.search(rf"\b\w+\s+{w}\s*\(", src_nc))
    unused = []
    for d in sorted(declared):
        if d == "main" or d.startswith("u_") or d.startswith("v_"):   # uniforms/varyings live in other stages
            continue
        if len(re.findall(rf"\b{d}\b", src_nc)) <= 1:
            unused.append(d)
    problems = []
    if undefined:
        problems.append(f"UNDEFINED identifiers (will not compile): {undefined}")
    if unused:
        problems.append(f"declared-but-never-used (suspect dead code): {unused}")
    return problems

def lint_rs(path):
    with tempfile.NamedTemporaryFile("w", suffix=".rs", delete=False) as tf:
        tf.write(path.read_text())
        tmp = tf.name
    r = subprocess.run(["rustc", "--edition", "2021", "--crate-type", "lib", tmp, "-o", "/tmp/gift_lint_tmp.rlib"],
                       capture_output=True, text=True, timeout=120)
    errs = [l for l in r.stderr.splitlines() if l.startswith("error")]
    if r.returncode != 0:
        # distinguish missing-crate (packaging) from real code errors
        missing_crate = "unresolved" in r.stderr and "crate" in r.stderr
        tag = "FAIL (missing crate declaration — packaging gap)" if missing_crate and "cannot find value" not in r.stderr and "E0425" not in r.stderr else "FAIL (code does not compile)"
        return [f"{tag}: {'; '.join(errs[:2])}"]
    return []

def lint_py(path):
    r = subprocess.run(["python3", "-m", "py_compile", str(path)], capture_output=True, text=True, timeout=60)
    return [] if r.returncode == 0 else [f"FAIL py_compile: {r.stderr.splitlines()[-1] if r.stderr else '?'}"]

def lint_js(path):
    r = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return [f"FAIL node --check: {r.stderr.splitlines()[0] if r.stderr else '?'}"]
    return ["note: syntax OK; DOM/WebGL semantics unverifiable headless (no boundary crossed)"]

def main():
    targets = []
    for a in sys.argv[1:]:
        p = pathlib.Path(a)
        if p.is_dir():
            targets.extend(sorted(p.rglob("*.*")))
        else:
            targets.append(p)
    table, all_ok = [], True
    for p in targets:
        ext = p.suffix.lower()
        if ext == ".py":
            problems = lint_py(p)
        elif ext == ".js":
            problems = lint_js(p)
        elif ext == ".rs":
            problems = lint_rs(p)
        elif ext in {".glsl", ".frag", ".vert"}:
            problems = lint_glsl(p)
        else:
            continue
        verdict = "PASS" if not problems else "FAIL"
        if problems:
            all_ok = False
        print(f"{verdict:4s}  {p.name:28s} {' | '.join(problems) if problems else 'cheapest real check green'}")
        table.append({"file": str(p), "verdict": verdict, "problems": problems})
    (pathlib.Path("/tmp/gift_lint_table.json")).write_text(repr(table))
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
