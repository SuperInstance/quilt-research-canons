import sys, re
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(path).read()
n = src.count(old)
if n != 1:
    print(f"ABORT: old string occurs {n} times in {path} (need exactly 1)"); sys.exit(2)
open(path,"w").write(src.replace(old, new))
after = open(path).read()
ok = (after.count(old) == 0) and (after.count(new) == 1)
# extra guard: new string must not be inside a docstring
import ast
tree = ast.parse(after)
docstrings = set()
for node in ast.walk(tree):
    if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        d = ast.get_docstring(node, clean=False)
        if d: docstrings.add(d)
indoc = any(new in d for d in docstrings)
print(f"MUTATION APPLIED: {path}  replaced 1 occurrence; new_present={after.count(new)==1} old_absent={after.count(old)==0} new_inside_docstring={indoc}")
if indoc: print("ABORT: mutation landed in a docstring"); sys.exit(3)
