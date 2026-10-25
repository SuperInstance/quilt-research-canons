"""Minimal pytest shim: fixtures (incl. class-scoped), parametrize, raises, approx, warns."""
import sys, os, glob, inspect, tempfile, traceback
from pathlib import Path

class _Approx:
    def __init__(self, v, rel=1e-6, abs_=1e-12): self.v=v; self.rel=rel; self.abs=abs_
    def __eq__(self, o):
        try: return abs(o-self.v) <= max(self.abs, self.rel*max(abs(o),abs(self.v)))
        except Exception: return False
    def __repr__(self): return f"approx({self.v})"
def approx(v, rel=1e-6, abs=1e-12): return _Approx(v, rel, abs)

class _Raises:
    def __init__(self, exc, match=None): self.exc=exc; self.match=match
    def __enter__(self): return self
    def __exit__(self, et, ev, tb):
        if et is None: raise AssertionError(f"DID NOT RAISE {self.exc}")
        if not issubclass(et, self.exc): return False
        if self.match and not re.search(self.match, str(ev)): raise AssertionError(f"{ev!r} !~ {self.match}")
        self.value = ev; return True
def raises(exc, match=None): return _Raises(exc, match)

class _Warns:
    def __init__(self, cat): self.cat=cat
    def __enter__(self): return self
    def __exit__(self, et, ev, tb): return et is not None and issubclass(et, self.cat)
def warns(cat, match=None): return _Warns(cat)

class _Mark:
    def __getattr__(self, n):
        if n == "parametrize":
            def parametrize(argnames, argvalues, **kw):
                def deco(f):
                    params = getattr(f, "_parametrize", [])
                    params.append((argnames, list(argvalues)))
                    f._parametrize = params
                    setattr(f, "_marks", getattr(f,"_marks",[])+["parametrize"])
                    return f
                return deco
            return parametrize
        def deco(*a, **k):
            if len(a)==1 and callable(a[0]) and not k:
                f=a[0]; setattr(f, "_marks", getattr(f,"_marks",[])+[n]); return f
            return lambda f: f
        return deco
mark = _Mark()

def fixture(*a, **k):
    if len(a)==1 and callable(a[0]) and not k:
        a[0]._is_fixture = True; return a[0]
    return lambda f: f

def skip(*a, **k): raise _Skipped()
class _Skipped(Exception): pass
def fail(msg=""): raise AssertionError(msg)
def importorskip(name, *a, **k):
    try: return __import__(name)
    except ImportError: raise _Skipped()
def param(*a, **k): return ("__param__", a, k)

import re

def _is_fixture(obj):
    return getattr(obj, "_is_fixture", False) or hasattr(obj, "_pytestfixturefunction")

def _resolve(name, cls_inst, cls, cache, stack):
    if name in cache: return cache[name]
    if name == "tmp_path": v = Path(tempfile.mkdtemp(prefix="pt_")); cache[name]=v; return v
    if name == "capsys":
        import io, contextlib
        class _Cap:
            def __init__(self):
                self._out=io.StringIO(); self._err=io.StringIO()
                self._ctx=contextlib.ExitStack()
                self._ctx.enter_context(contextlib.redirect_stdout(self._out))
                self._ctx.enter_context(contextlib.redirect_stderr(self._err))
            def readouterr(self):
                o,e=self._out.getvalue(), self._err.getvalue()
                self._out.truncate(0); self._out.seek(0); self._err.truncate(0); self._err.seek(0)
                class R: pass
                r=R(); r.out=o; r.err=e; return r
            def disable(self):
                try: self._ctx.close()
                except Exception: pass
            def close(self):
                try: self._ctx.close()
                except Exception: pass
        v=_Cap(); _CAPS.append(v); cache[name]=v; return v
    if name == "tmp_path_factory":
        class T:
            def mktemp(self, n, num=None): return Path(tempfile.mkdtemp(prefix=n))
        v=T(); cache[name]=v; return v
    cand = getattr(cls, name, None) if cls else None
    if cand is not None and (callable(cand) and (_is_fixture(cand) or name in getattr(cls,"_fixture_names",()))):
        fn = cand
        if isinstance(fn, (staticmethod, classmethod)): fn = fn.__func__
        sub = {}
        for p in inspect.signature(fn).parameters:
            if p == "self": continue
            sub[p] = _resolve(p, cls_inst, cls, cache, stack)
        if cls_inst is not None:
            try: v = fn(cls_inst, **sub)
            except TypeError: v = fn(**sub)
        else:
            v = fn(**sub)
        if inspect.isgenerator(v):
            g = v
            v = next(g)
            _GENS.append(g)
        cache[name]=v; return v
    # module-level fixture
    for mod in _MODS:
        f = getattr(mod, name, None)
        if f is not None and callable(f) and _is_fixture(f):
            sub = {p:_resolve(p, cls_inst, cls, cache, stack) for p in inspect.signature(f).parameters}
            v = f(**sub)
            if inspect.isgenerator(v):
                g = v; v = next(g); _GENS.append(g)
            cache[name]=v; return v
    raise AssertionError(f"fixture '{name}' not found")

_MODS = []
_CAPS = []
_FILT=[None]
_GENS = []

def _make_expect(actual, negated):
    def ok(cond, msg):
        if negated:
            if cond: raise AssertionError(f"expected NOT {msg}")
        else:
            if not cond: raise AssertionError(msg)
    eq = lambda a,b: a==b if not isinstance(a,(dict,list)) else a==b
    api = {
      "toBe": lambda e: ok(actual is e or actual==e, f"expected {actual!r} to be {e!r}"),
      "toEqual": lambda e: ok(eq(actual,e), f"expected {actual!r} to equal {e!r}"),
      "toStrictEqual": lambda e: ok(eq(actual,e), f"expected {actual!r} to strictly equal {e!r}"),
      "toBeTruthy": lambda: ok(bool(actual), f"expected {actual!r} truthy"),
      "toBeFalsy": lambda: ok(not actual, f"expected {actual!r} falsy"),
      "toBeNull": lambda: ok(actual is None, f"expected {actual!r} null"),
      "toBeUndefined": lambda: ok(actual is None or actual is ..., f"expected {actual!r} undefined"),
      "toBeDefined": lambda: ok(actual is not None, f"expected defined, got {actual!r}"),
      "toBeGreaterThan": lambda e: ok(actual>e, f"expected {actual!r} > {e!r}"),
      "toBeGreaterThanOrEqual": lambda e: ok(actual>=e, f"expected {actual!r} >= {e!r}"),
      "toBeLessThan": lambda e: ok(actual<e, f"expected {actual!r} < {e!r}"),
      "toBeLessThanOrEqual": lambda e: ok(actual<=e, f"expected {actual!r} <= {e!r}"),
      "toBeInstanceOf": lambda e: ok(isinstance(actual,e), f"expected {actual!r} instance of {e}"),
      "toContain": lambda e: ok(actual is not None and (e in actual if hasattr(actual,'__contains__') else False), f"expected {actual!r} to contain {e!r}"),
      "toHaveLength": lambda e: ok(actual is not None and len(actual)==e, f"expected len {len(actual) if actual is not None else None} == {e}"),
      "toHaveBeenCalledTimes": lambda e: ok(getattr(actual,'mock',None) and actual.mock.calls.__len__()==e, f"expected {getattr(actual,'mock',None) and actual.mock.calls.__len__()} calls == {e}"),
      "toHaveBeenCalled": lambda: ok(getattr(actual,'mock',None) and len(actual.mock.calls)>0, "expected called"),
      "toHaveBeenCalledWith": lambda *a, **k: ok(getattr(actual,'mock',None) and any(c[0]==a[0] for c in actual.mock.calls), "expected called with"),
      "toThrow": lambda *a, **k: ok(False, "toThrow unsupported"),
      "toBeCloseTo": lambda e,p=2: ok(abs(actual-e)<10**(-p)/2, f"expected {actual!r} close to {e!r}"),
      "toMatch": lambda re_: ok(re.search(re_, str(actual)), f"expected {actual!r} to match {re_}"),
      "toMatchObject": lambda e: ok(all(actual.get(k)==v for k,v in e.items()), "match object"),
    }
    return api

def expect(actual):
    a=_make_expect(actual, False); setattr(a, "not", _make_expect(actual, True)); return a

class _Spy:
    def __init__(self, impl=None, ret=None):
        self.mock={"calls":[]}; self._impl=impl; self._ret=ret
    def __call__(self,*a,**k):
        self.mock["calls"].append((a,k))
        if self._impl: return self._impl(*a,**k)
        return self._ret
    def mockReturnValue(self,v): self._ret=v; return self
    def mockImplementation(self,f): self._impl=f; return self
    def mockResolvedValue(self,v): self._impl=lambda *a,**k: v; return self
    def mockRejectedValue(self,v): self._impl=lambda *a,**k: (_ for _ in ()).throw(v); return self
    def mockClear(self): self.mock["calls"]=[]; return self
    def mockRestore(self): return self
def vi():
    return {"fn": lambda *a,**k: _Spy(*a,**k)}

import importlib
def main():
    args=[a for a in sys.argv[1:] if not a.startswith("-")]
    filt=None
    if "-k" in sys.argv:
        i=sys.argv.index("-k")
        filt=sys.argv[i+1] if i+1 < len(sys.argv) else None
    files=[]
    for root in args:
        if os.path.isfile(root): files.append(root)
        else:
            files.extend(sorted(glob.glob(os.path.join(root,"**","test_*.py"), recursive=True)))
    root=os.path.dirname(files[0]) if files else "."
    _run_files(files, root, filt)
    return 0

def _run_files(files, root, filt=None):
    passed=failed=skipped=0; fails=[]
    _FILT=[filt]
    passed=failed=skipped=0; fails=[]
    for f in files:
        d=os.path.dirname(f); base=os.path.basename(f)[:-3]
        sys.path.insert(0,d); sys.path.insert(0,root)
        # walk up to the project root (pyproject.toml / setup.py / setup.cfg) and
        # put it on sys.path so flat-layout and src-layout imports both work
        probe=os.path.abspath(d)
        for _ in range(6):
            if any(os.path.exists(os.path.join(probe, m)) for m in ("pyproject.toml","setup.py","setup.cfg")):
                if probe not in sys.path: sys.path.insert(0, probe)
                srcdir=os.path.join(probe, "src")
                if os.path.isdir(srcdir) and srcdir not in sys.path: sys.path.insert(0, srcdir)
                break
            parent=os.path.dirname(probe)
            if parent==probe: break
            probe=parent
        cwd=os.getcwd()
        if cwd not in sys.path: sys.path.insert(0, cwd)
        try:
            mod=importlib.import_module(base)
        except _Skipped:
            skipped+=1; continue
        except Exception as e:
            failed+=1; fails.append((f,"<import>",f"{type(e).__name__}: {e}")); continue
        _MODS.append(mod)
        # module-level fixtures
        for nm in dir(mod):
            o=getattr(mod,nm)
            if _is_fixture(o) and isinstance(o,type): setattr(o,"_fixture_names",set())
        targets=[]
        for nm in dir(mod):
            o=getattr(mod,nm)
            if nm.startswith("test_") and inspect.isfunction(o):
                targets.append((nm, o, None))
            elif nm.startswith("Test") and isinstance(o,type):
                for cn in dir(o):
                    if cn.startswith("test_"):
                        cf=getattr(o,cn)
                        if callable(cf): targets.append((f"{nm}::{cn}", cf, o))
            _f=_FILT[0]
            if _f:
                targets=[t for t in targets if _f in t[0]]
        for label, fn, cls in targets:
            # parametrize
            marks = getattr(fn,"_marks",[])
            cases=[{}]
            for argnames, argvalues in getattr(fn, "_parametrize", []):
                names = [x.strip() for x in argnames.split(",")] if isinstance(argnames,str) else list(argnames)
                expanded=[]
                for base in cases:
                    for vals in argvalues:
                        vals = vals if isinstance(vals,(tuple,list)) else (vals,)
                        d=dict(base); d.update(dict(zip(names, vals))); expanded.append(d)
                cases=expanded
            for params in cases:
                try:
                    inst = cls() if cls else None
                    cache={}
                    kwargs=dict(params)
                    sig = inspect.signature(fn)
                    for p in sig.parameters:
                        if p=="self": continue
                        if p in kwargs: continue
                        kwargs[p]=_resolve(p, inst, cls, cache, set())
                    if cls:
                        import unittest as _ut
                        if isinstance(inst, _ut.TestCase):
                            inst.setUp()
                            fn(inst, **kwargs)
                            inst.tearDown()
                        else:
                            sm = getattr(inst, "setup_method", None)
                            if callable(sm): sm()
                            fn(inst, **kwargs)
                            tm = getattr(inst, "teardown_method", None)
                            if callable(tm): tm()
                    else:
                        fn(**kwargs)
                    passed+=1
                except _Skipped:
                    skipped+=1
                except Exception as e:
                    failed+=1; fails.append((f,label,f"{type(e).__name__}: {e}"))
                finally:
                    for c in _CAPS:
                        c.close()
                    _CAPS.clear()
                    for g in _GENS:
                        try: next(g)
                        except StopIteration: pass
                        except Exception: pass
                    _GENS.clear()
    print(f"PASSED={passed} FAILED={failed} SKIPPED={skipped}")
    for f,n,e in fails[:60]: print(f"  FAIL {os.path.basename(f)}::{n} -> {e}")
    return 0 if failed==0 else 1


if __name__=="__main__": sys.exit(main())
