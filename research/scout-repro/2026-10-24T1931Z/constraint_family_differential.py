"""Differential harness: two INT8 constraint contracts in the SAME family.

Contract A: constraint-theory-rust-python/src/constraint.rs   (Rust + PyO3 + pure-python fallback)
Contract B: cuda-constraint-checker/src/constraint_checker.cu (CUDA + its C++ CPU reference)

Both are transcribed VERBATIM from the sources named above.
"""
def wrap_i8(x):        # C int8_t conversion = two's-complement wrap (CUDA side)
    x &= 0xFF
    return x - 256 if x >= 128 else x

# ---------- Contract A: sat8 clamps to [-127, +127] (src/constraint.rs) ----------
def A_sat8(v):  return max(-127, min(127, v))
def A_check(value, lo, hi):
    lo, hi = A_sat8(lo), A_sat8(hi)
    sv = A_sat8(value)
    saturated = sv != value
    passed = lo <= sv <= hi
    mask = 0x00
    if saturated:           mask |= 0x08   # SATURATION
    if sv == lo:            mask |= 0x01   # SAT_MIN_DOT
    if sv == hi:            mask |= 0x02   # SAT_MAX_DOT
    if passed and not saturated:
        rng = hi - lo
        if rng > 0:
            margin = rng // 10            # 10% deadband
            if sv - lo <= margin or hi - sv <= margin: mask |= 0x04  # CONFIDENCE_GAP
    sev = 0 if passed else 3              # Pass / Caution / Warning / Critical
    return {"pass":passed, "mask":mask, "severity":sev, "sat":sv}

# ---------- Contract B: native int8_t, no saturation (src/constraint_checker.cu) ----------
def B_check(value, lo, hi):
    v, lb, hb = wrap_i8(value), wrap_i8(lo), wrap_i8(hi)
    violated = (v < lb) or (v > hb)
    sev = 0
    if violated:
        sev = 2                          # SEVERITY_CRITICAL
    else:
        rng = hb - lb
        margin = rng >> 2                # 25% deadband
        if margin > 0 and (v < lb + margin or v > hb - margin): sev = 1  # SEVERITY_WARN
    mask = 1 if violated else 0          # 1 bit per constraint, packed 8/byte
    return {"pass":(not violated), "mask":mask, "severity":sev, "sat":v}

CASES = [
    ("value at the int8 floor",        -128, -127, 127),
    ("value at the int8 floor, wide",  -128, -128, 127),
    ("value below int8 floor",         -200, -127, 127),
    ("value above int8 max",            200, -127, 127),
    ("lower bound below int8 floor",   -128, -200, 127),
    ("upper bound above int8 max",      127, -127,  200),
    ("mid-band, 10% vs 25% zone",        30,   0, 100),
    ("mid-band, 25% zone only",          20,   0, 100),
    ("ordinary in-range value",          50,   0, 100),
]
print(f"{'case':<34}{'value':>7}{'A pass':>8}{'A sev':>7}{'A mask':>8}   {'B pass':>8}{'B sev':>7}{'B mask':>8}   DIVERGES")
print("-"*118)
div = 0
for name, v, lo, hi in CASES:
    a, b = A_check(v, lo, hi), B_check(v, lo, hi)
    d = []
    if a["pass"] != b["pass"]:  d.append("VERDICT")
    if a["severity"] != b["severity"]: d.append("SEVERITY")
    if a["mask"] != b["mask"]:  d.append("MASK")
    if a["sat"] != b["sat"]:    d.append("SATURATED_VALUE")
    if d: div += 1
    print(f"{name:<34}{v:>7}{str(a['pass']):>8}{a['severity']:>7}{a['mask']:>8}   "
          f"{str(b['pass']):>8}{b['severity']:>7}{b['mask']:>8}   {','.join(d) or '-'}")
print("-"*118)
print(f"cases where the two implementations disagree: {div}/{len(CASES)}")

print()
print("=== severity vocabulary ===")
print("  A (rust/py): Pass=0 Caution=1 Warning=2 Critical=3   (4 levels)")
print("  B (cuda)   : PASS=0 WARN=1 CRITICAL=2                 (3 levels)  <- 'Critical' is 3 in A, 2 in B")
print("=== error_mask encoding ===")
print("  A: class flags  PASS=0x00 SAT_MIN_DOT=0x01 SAT_MAX_DOT=0x02 CONFIDENCE_GAP=0x04 SATURATION=0x08")
print("  B: 1 bit per constraint (violated), 8 constraints packed per byte")
print("=== deadband ===")
print("  A: 10% of range (margin = range/10), only when passed && !saturated")
print("  B: 25% of range (margin = range>>2)")
