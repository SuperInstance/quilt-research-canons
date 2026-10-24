import sys, os, importlib.util, inspect, tempfile, traceback, itertools, re
sys.path.insert(0, "/tmp/harness")
import minipytest
sys.modules["pytest"] = minipytest.build_module()

REPO = sys.argv[1]
sys.path.insert(0, REPO)

class Skipped(minipytest.Skipped): pass

def load_module(path):
    name = "t_" + os.path.basename(path)[:-3]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

class Ctx:
    def __init__(self, mod): self.mod = mod; self.cache = {}; self.finalizers = []
    def fixture(self, name):
        if name in self.cache: return self.cache[name]
        if name == "tmp_path":
            import pathlib
            v = pathlib.Path(tempfile.mkdtemp(prefix="mp_")); self.cache[name] = v; return v
        f = getattr(self.mod, name, None)
        if f is None or not getattr(f, "_is_fixture", False):
            raise KeyError(name)
        kwargs = {p: self.fixture(p) for p in getattr(f, "_fixture_params", [])}
        res = f(**kwargs)
        if inspect.isgenerator(res):
            gen = res; val = next(gen)
            self.finalizers.append(lambda g=gen: next(g, None))
        else:
            val = res
        self.cache[name] = val
        return val
    def cleanup(self):
        for fn in reversed(self.finalizers):
            try: fn()
            except Exception: pass

def resolve(ctx, func, params):
    kwargs = dict(params)
    sig = inspect.signature(func)
    for p in sig.parameters:
        if p in ("self",): continue
        if p in kwargs: continue
        if p == "tmp_path":
            d = tempfile.mkdtemp(prefix="mp_"); kwargs[p] = __import__("pathlib").Path(d); continue
        kwargs[p] = ctx.fixture(p)
    return kwargs

def expand(func):
    """Yield (id, params) for each parametrize combination."""
    marks = getattr(func, "_parametrize", [])
    if not marks: return [("", {})]
    combos = [("", {})]
    # apply in reverse so first-applied is outermost
    for names, values in reversed(marks):
        new = []
        for _, base in combos:
            for v in values:
                vals = v if len(names) > 1 else (v,)
                d = dict(base); d.update(dict(zip(names, vals)))
                new.append((str(vals), d))
        combos = new
    return combos or [("", {})]

results = []
files = sorted(f for f in os.listdir(os.path.join(REPO, "tests")) if f.startswith("test_") and f.endswith(".py"))
for fn in files:
    path = os.path.join(REPO, "tests", fn)
    mod = load_module(path)
    items = []
    for nm, obj in vars(mod).items():
        if nm.startswith("test_") and inspect.isfunction(obj) and not getattr(obj, "_is_fixture", False): items.append((nm, obj, None))
        elif nm.startswith("Test") and inspect.isclass(obj):
            for mn, mo in vars(obj).items():
                if mn.startswith("test_") and inspect.isfunction(mo) and not getattr(mo, "_is_fixture", False):
                    items.append((f"{nm}::{mn}", mo, obj))
    for label, func, cls in items:
        if getattr(func, "_skip", None): continue
        for pid, params in expand(func):
            ctx = Ctx(mod)
            try:
                inst = cls() if cls else None
                kwargs = resolve(ctx, func, params)
                if inst is not None: func(inst, **kwargs)
                else: func(**kwargs)
                results.append(("PASS", f"{fn}::{label}[{pid}]", ""))
            except Skipped as e:
                results.append(("SKIP", f"{fn}::{label}[{pid}]", str(e)))
            except Exception as e:
                results.append(("FAIL", f"{fn}::{label}[{pid}]", f"{type(e).__name__}: {e}"))
            finally:
                ctx.cleanup()

npass = sum(1 for r in results if r[0]=="PASS")
nfail = sum(1 for r in results if r[0]=="FAIL")
nskip = sum(1 for r in results if r[0]=="SKIP")
print(f"# tests={len(results)}")
print(f"# pass={npass}")
print(f"# fail={nfail}")
print(f"# skip={nskip}")
for st, nm, msg in results:
    if st != "PASS": print(f"{st} {nm} :: {msg}")
