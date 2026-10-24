#!/usr/bin/env python3
"""Receipt: the wheel shipped in constraint-theory-rust-python/dist installs a
top-level `_flux` package — NOT `flux_constraint` (the source package, absent
from the wheel) and NOT `constraint_engine_rs` (the README's import) — and
cannot be imported at all on a Python whose ABI differs from cp310.

    python3 wheel_import_probe.py /path/to/constraint-theory-rust-python
"""
import sys, zipfile, tempfile, importlib.util, os, glob
REPO = sys.argv[1] if len(sys.argv) > 1 else "."
whl = glob.glob(os.path.join(REPO, "dist", "*.whl"))
if not whl: sys.exit("no wheel in dist/")
whl = whl[0]
print(f"wheel: {os.path.basename(whl)}")
with zipfile.ZipFile(whl) as z:
    for i in z.infolist(): print(f"   {i.file_size:>8}  {i.filename}")
d = tempfile.mkdtemp()
zipfile.ZipFile(whl).extractall(d)
sys.path.insert(0, d)
print(f"\npython {sys.version.split()[0]}")
for m in ["constraint_engine_rs", "flux_constraint", "_flux"]:
    try:
        s = importlib.util.find_spec(m)
        print(f"  import {m:<22} -> {'FOUND ' + str(s.origin) if s else 'ModuleNotFoundError (not installed)'}")
    except Exception as e:
        print(f"  import {m:<22} -> {type(e).__name__}: {e}")
print("\n  --- actually importing the one that resolved ---")
try:
    import _flux
    print("   _flux imported OK:", [x for x in dir(_flux) if not x.startswith("_")])
except Exception as e:
    print(f"   FAILED: {type(e).__name__}: {e}")
