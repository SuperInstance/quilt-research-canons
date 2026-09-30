"""Shared harness. Every experiment reports WHICH PATH IT TOOK.

The CRDT package's headline turned out to be an arithmetic identity: CRDT latency was
2.00 for average, min AND max across 98 simulations. A number that cannot vary is not
evidence. That lesson is enforced here mechanically: if CUDA is unavailable, the report
says CPU, always, in the summary line.
"""
import importlib, math, time, random

def backend():
    """(name, available, note) — never lie about which device produced a number."""
    try:
        torch = importlib.import_module("torch")
        if torch.cuda.is_available():
            n = torch.cuda.get_device_name(0)
            return "cuda", True, n
        return "cpu", False, "torch present but no CUDA device"
    except ImportError:
        return "cpu", False, "torch not installed"
    except Exception as e:
        return "cpu", False, f"torch present but probe failed: {type(e).__name__}"

def banner(name, what):
    mode, cuda, note = backend()
    print()
    print("=" * 78)
    print(f"  {name}")
    print("=" * 78)
    print(f"  {what}")
    print(f"  BACKEND: {mode.upper()}" + (f"  ({note})" if cuda else f"  -- FALLBACK: {note}"))
    print("  " + "=" * 78)
    return mode

def refutes(condition, statement):
    print(f"  {'REFUTED  ' if condition else 'holds    '} {statement}")

def done():
    print("  " + "=" * 78)
    print()
