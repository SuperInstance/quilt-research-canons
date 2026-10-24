#!/usr/bin/env python3
"""pytest-compatible runner (assert-style suites). NOW supports mark.parametrize
expansion and module/class fixtures, including fixtures with params."""
import sys, os, inspect, traceback, importlib.util, tempfile, shutil, itertools

# Self-contained: put THIS directory on sys.path so test modules that
# `import pytest` resolve to the shim next to us, not to a real pytest.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# Also make the repo under test importable without PYTHONPATH juggling:
# cwd, cwd/src, and cwd/. (a src-layout package) are the usual roots.
for _root in (os.getcwd(), os.path.join(os.getcwd(), "src")):
    if os.path.isdir(_root) and _root not in sys.path:
        sys.path.insert(0, _root)

class _Fail(Exception): pass
class _Skipped(Exception): pass
_MISSING = object()

class MonkeyPatch:
    def __init__(self): self._undo = []
    def setattr(self, target, name, value=None, raising=True):
        old = getattr(target, name, _MISSING); self._undo.append(("attr",target,name,old))
        setattr(target, name, value)
    def setitem(self, d, k, v):
        old = d.get(k, _MISSING); self._undo.append(("item",d,k,old)); d[k]=v
    def setenv(self, name, val):
        old = os.environ.get(name, _MISSING); self._undo.append(("env",None,name,old)); os.environ[name]=str(val)
    def delenv(self, name, raising=False):
        old = os.environ.get(name, _MISSING); self._undo.append(("env",None,name,old)); os.environ.pop(name,None)
    def chdir(self, p):
        old=os.getcwd(); self._undo.append(("chdir",None,None,old)); os.chdir(p)
    def undo(self):
        for kind,t,n,old in reversed(self._undo):
            if kind=="attr":
                if old is _MISSING: delattr(t,n)
                else: setattr(t,n,old)
            elif kind=="item":
                if old is _MISSING: t.pop(n,None)
                else: t[n]=old
            elif kind=="env":
                if old is _MISSING: os.environ.pop(n,None)
                else: os.environ[n]=old
            elif kind=="chdir": os.chdir(old)
        self._undo=[]

_MP = None  # set after MonkeyPatch is defined
def _collect_fixtures(mod):
    fx = {}
    for nm, obj in vars(mod).items():
        if callable(obj) and getattr(obj, "_pytest_fixture", False):
            fx[obj._pytest_name] = obj
    return fx

def _fixture_values(fx, name, tmpdir, cache, mod=None, stack=None):
    if name in cache: return cache[name]
    fn = fx.get(name)
    if fn is None: return None
    stack = stack or []
    if name in stack: return None
    stack = stack + [name]
    sig = inspect.signature(fn)
    kwargs = {}
    for pname in sig.parameters:
        dep = _fixture_values(fx, pname, tmpdir, cache, mod, stack)
        if dep is not None: kwargs[pname] = dep
    val = fn(**kwargs)
    if hasattr(val, "__next__") and not isinstance(val, (list, tuple, dict, str)):
        val = next(val)
    cache[name]=val; return val

def _resolve(name, mod, fx, tmpdir, cache, inst):
    if name == "tmp_path":
        from pathlib import Path
        p = os.path.join(tmpdir, "tp"); os.makedirs(p, exist_ok=True); return Path(p)
    if name == "tmpdir":
        p = os.path.join(tmpdir, "td"); os.makedirs(p, exist_ok=True); return p
    if name == "monkeypatch": return _MP
    if name in fx:
        return _fixture_values(fx, name, tmpdir, cache, mod)
    obj = getattr(mod, name, None)
    if obj is None and inst is not None: obj = getattr(inst, name, None)
    if callable(obj):
        try:
            if len(inspect.signature(obj).parameters)==0:
                v=obj()
                if hasattr(v,"__next__") and not isinstance(v,(list,tuple,dict,str)): v=next(v)
                return v
        except Exception: pass
    return obj

def _expand_params(fn):
    """Return list of kwargs dicts for a (possibly parametrized) test fn."""
    sets = getattr(fn, "_pytest_params", None)
    if not sets: return [{}]
    combos = []
    for group in sets:
        combos.append(group)
    out=[]
    for combo in itertools.product(*combos):
        d={}
        for p in combo: d.update(p)
        out.append(d)
    return out

def run_module(path, filt=None):
    path=os.path.abspath(path); d=os.path.dirname(path)
    name=os.path.splitext(os.path.basename(path))[0]
    sys.path.insert(0,d)
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod
    try: spec.loader.exec_module(mod)
    except Exception:
        return [(name,"IMPORT",traceback.format_exc())]
    global _MP
    _MP = MonkeyPatch()
    fx=_collect_fixtures(mod)
    results=[]; tmpdir=tempfile.mkdtemp(prefix="pt_")
    items=[]
    for nm,fn in list(vars(mod).items()):
        if nm.startswith("test_") and callable(fn) and inspect.isfunction(fn): items.append((nm,fn,None))
    for nm,obj in list(vars(mod).items()):
        if nm.startswith("Test") and inspect.isclass(obj):
            for mn,mf in list(vars(obj).items()):
                if mn.startswith("test_") and callable(mf): items.append((f"{nm}::{mn}",mf,obj))
    for label,fn,cls in items:
        if filt and filt not in label: continue
        if getattr(fn,"_pytest_skip",None): results.append((label,"SKIP","")); continue
        inst = cls() if cls is not None else None
        combos=_expand_params(fn)
        for ci,extra in enumerate(combos):
            lbl = label if len(combos)==1 else f"{label}[{ci}]"
            try:
                sig=inspect.signature(fn); kwargs=dict(extra)
                for pname in sig.parameters:
                    if pname in kwargs: continue
                    v=_resolve(pname,mod,fx,tmpdir,{},inst)
                    if v is not None or pname in ("tmp_path","tmpdir","monkeypatch"): kwargs[pname]=v
                setup = getattr(inst, "setUp", None) if inst is not None else None
                teardown = getattr(inst, "tearDown", None) if inst is not None else None
                if setup: setup()
                try:
                    if cls is not None: fn(inst,**kwargs)
                    else: fn(**kwargs)
                finally:
                    if teardown: teardown()
                results.append((lbl,"PASS",""))
            except _Skipped:
                results.append((lbl,"SKIP",""))
            except Exception as e:
                import unittest as _ut
                if isinstance(e, _ut.SkipTest):
                    results.append((lbl,"SKIP",str(e)))
                else:
                    results.append((lbl,"FAIL",traceback.format_exc()))
    shutil.rmtree(tmpdir,ignore_errors=True); _MP.undo()
    return results

if __name__=="__main__":
    print(f"pytest-shim runner (NOT pytest) -- {_HERE}")
    filt=None; args=sys.argv[1:]
    if args and args[0]=="-k": filt=args[1]; args=args[2:]
    tp=tf=ts=0
    for f in args:
        for label,st,tb in run_module(f,filt):
            print(f"{st:6s} {label}")
            if st in ("FAIL","IMPORT"):
                tail=tb.strip().splitlines()
                print("        "+" | ".join(tail[-3:])[:280])
            if st=="PASS": tp+=1
            elif st in ("FAIL","IMPORT"): tf+=1
            else: ts+=1
    print(f"\n{tp} passed, {tf} failed, {ts} skipped")
    sys.exit(1 if tf else 0)
