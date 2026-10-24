"""Minimal pytest API shim: enough to import and execute assert-style suites.
Supports: raises, approx, mark.parametrize (real expansion), mark.skipif,
fixture (incl. params/yield), skip, importorskip, warns, fail, approx.
"""
import re, math, functools, sys, types

class Skipped(Exception): pass
class Failed(Exception): pass

def skip(reason=""): raise Skipped(reason)
def fail(msg=""): raise Failed(msg)
def xfail(reason=""): raise Skipped(reason)

def importorskip(modname, minversion=None, reason=None):
    try:
        return __import__(modname)
    except ImportError:
        raise Skipped(reason or f"could not import {modname!r}")

class _Approx:
    def __init__(self, expected, rel=None, abs=None, nan_ok=False):
        self.expected = expected; self.rel = rel; self.abs = abs; self.nan_ok = nan_ok
    def _cmp(self, e, a):
        if isinstance(e, dict):
            return isinstance(a, dict) and set(e)==set(a) and all(self._cmp(e[k],a[k]) for k in e)
        if isinstance(e, (list,tuple)):
            return isinstance(a,(list,tuple)) and len(e)==len(a) and all(self._cmp(x,y) for x,y in zip(e,a))
        if isinstance(e, float) and math.isnan(e): return isinstance(a,float) and math.isnan(a)
        if self.abs is not None: return abs(e-a) <= self.abs
        if self.rel is not None: return abs(e-a) <= max(self.rel*max(abs(e),abs(a)), 1e-12)
        return abs(e-a) <= 1e-6*max(1.0,abs(e),abs(a))
    def __eq__(self, other):
        ok = self._cmp(self.expected, other)
        if not ok: raise AssertionError(f"approx({self.expected!r}) != {other!r}")
        return True
    def __repr__(self): return f"approx({self.expected!r})"

def approx(expected, rel=None, abs=None, nan_ok=False):
    return _Approx(expected, rel, abs, nan_ok)

class RaisesContext:
    def __init__(self, expected, match=None):
        self.expected = expected; self.match = match; self.value = None
    def __enter__(self): return self
    def __exit__(self, et, ev, tb):
        if et is None:
            raise Failed(f"DID NOT RAISE {self.expected}")
        if not issubclass(et, self.expected):
            return False
        self.value = ev
        if self.match is not None and not re.search(self.match, str(ev)):
            raise Failed(f"pattern {self.match!r} not found in {str(ev)!r}")
        return True

def raises(expected, *args, match=None, **kw):
    if args: return RaisesContext(args[0], match=match)
    return RaisesContext(expected, match=match)

class WarnsContext:
    def __init__(self, expected): self.expected = expected
    def __enter__(self): return self
    def __exit__(self, et, ev, tb):
        if et is None or not issubclass(et, self.expected): return False
        return True
def warns(expected): return WarnsContext(expected)

class _Mark:
    def parametrize(self, argnames, argvalues, ids=None, indirect=False):
        names = [n.strip() for n in (argnames.split(",") if isinstance(argnames,str) else list(argnames))]
        def deco(fn):
            sets = getattr(fn, "_pytest_params", [])
            new = []
            for vals in argvalues:
                if len(names)==1:
                    vals = (vals,) if not isinstance(vals,(tuple,list)) or (isinstance(vals,tuple) and len(names)!=1) else (vals,)
                vals = tuple(vals) if isinstance(vals,(list,tuple)) else (vals,)
                new.append(dict(zip(names, vals)))
            fn._pytest_params = sets + [new]
            return fn
        return deco
    def skipif(self, condition, reason=""):
        def deco(fn):
            if condition: fn._pytest_skip = reason or "skipif"
            return fn
        return deco
    def skip(self, reason=""):
        def deco(fn): fn._pytest_skip = reason or "skip"; return fn
        return deco
    def xfail(self, reason=""):
        def deco(fn): fn._pytest_xfail = True; return fn
        return deco
    def __getattr__(self, name):
        def deco(*a, **k):
            if len(a)==1 and callable(a[0]) and not k: return a[0]
            def inner(fn): return fn
            return inner
        return deco
mark = _Mark()

def fixture(func=None, *, scope="function", params=None, autouse=False, name=None):
    def deco(f):
        f._pytest_fixture = True
        f._pytest_params_list = params
        f._pytest_name = name or f.__name__
        return f
    if func is not None: return deco(func)
    return deco

class FixtureRequest:
    def __init__(self): self._f = {}
    def getfixturevalue(self, n): return self._f.get(n)
    def param(self, n): return self._f.get(n)

def main(*a, **k): raise NotImplementedError("pytest shim: use /tmp/scout/pt.py")
