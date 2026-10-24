"""A minimal, honest pytest shim: implements ONLY the API surface ternary-rom's suite uses.
   approx / raises / fixture / mark.parametrize / skipif / importorskip.
   It is NOT pytest and does not claim to be."""
import math, types, functools

class Skipped(Exception): pass

class _Approx:
    def __init__(self, expected, rel=None, abs=None, nan_ok=False):
        self.expected = expected; self.rel = rel; self.abs = abs; self.nan_ok = nan_ok
    def _cmp(self, a, b):
        if isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
            return len(a)==len(b) and all(self._cmp(x,y) for x,y in zip(a,b))
        if isinstance(a,dict) and isinstance(b,dict):
            return set(a)==set(b) and all(self._cmp(a[k],b[k]) for k in a)
        if isinstance(a,(int,float)) and isinstance(b,(int,float)):
            if math.isnan(a) or math.isnan(b): return self.nan_ok and math.isnan(a) and math.isnan(b)
            rel = 1e-6 if self.rel is None else self.rel
            ab  = 1e-12 if self.abs is None else self.abs
            return math.isclose(a,b,rel_tol=rel,abs_tol=ab)
        return a == b
    def __eq__(self, other): return self._cmp(other, self.expected)
    def __repr__(self): return f"approx({self.expected!r})"

def approx(expected, rel=None, abs=None, nan_ok=False):
    return _Approx(expected, rel, abs, nan_ok)

class _Raises:
    def __init__(self, expected, match=None):
        self.expected = expected; self.match = match; self.value = None
    def __enter__(self): return self
    def __exit__(self, et, ev, tb):
        if et is None:
            raise AssertionError(f"DID NOT RAISE {self.expected}")
        if not issubclass(et, self.expected):
            return False
        self.value = ev
        if self.match:
            import re
            if not re.search(self.match, str(ev)):
                raise AssertionError(f"pattern {self.match!r} not found in {str(ev)!r}")
        return True

def raises(expected, match=None):
    return _Raises(expected, match)

def fixture(func=None, **kw):
    def wrap(f):
        f._is_fixture = True
        f._fixture_params = list(inspect_free_params(f))
        return f
    if func is not None: return wrap(func)
    return wrap

def importorskip(name, *a, **k):
    try: return __import__(name)
    except ImportError: raise Skipped(f"could not import {name!r}")

def skip(reason=""): raise Skipped(reason)

def inspect_free_params(f):
    import inspect
    try: sig = inspect.signature(f)
    except Exception: return []
    return [p for p in sig.parameters if p != "self"]

class _Mark:
    def parametrize(self, argnames, argvalues, **kw):
        names = [n.strip() for n in (argnames.split(",") if isinstance(argnames,str) else list(argnames))]
        def deco(f):
            existing = getattr(f, "_parametrize", [])
            f._parametrize = existing + [(names, list(argvalues))]
            return f
        return deco
    def skipif(self, cond, reason=""):
        def deco(f):
            if cond: f._skip = reason or "skipif"
            return f
        return deco
    def skip(self, reason=""):
        def deco(f): f._skip = reason or "skip"; return f
        return deco
    def xfail(self, *a, **k):
        def deco(f): return f
        return deco
    def __getattr__(self, k):
        def deco(*a, **kw):
            if len(a)==1 and callable(a[0]) and not kw: return a[0]
            return lambda f: f
        return deco

mark = _Mark()

def build_module():
    m = types.ModuleType("pytest")
    m.approx=approx; m.raises=raises; m.fixture=fixture; m.mark=mark
    m.skip=skip; m.importorskip=importorskip; m.Skipped=Skipped
    m.main = lambda *a, **k: None
    return m
