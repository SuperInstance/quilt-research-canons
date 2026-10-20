import struct, math
# EXACT port of constraint-bench-suite/gpu/drift_bench.cu (E64/E32/E16/EBF16/EI8 + kernel loop)
ITER = 10000
def f32(x):
    try: return struct.unpack('<f', struct.pack('<f', x))[0]
    except (OverflowError, ValueError): return math.inf if x>0 else -math.inf
def f16(x):
    try: return struct.unpack('<e', struct.pack('<e', x))[0]
    except (OverflowError, ValueError): return math.inf if x>0 else -math.inf
def bf16_trunc(x):
    x = f32(x)
    u = struct.unpack('<I', struct.pack('<f', x))[0]
    if math.isinf(x) or math.isnan(x): return x
    return struct.unpack('<f', struct.pack('<I', (u >> 16) << 16))[0]
def i8c(v): return max(-127, min(127, v))
def s8(v): return max(-127, min(127, v))

def run(kind):
    if kind=='fp64': a,b = 3.0,5.0
    elif kind=='fp32': a,b = f32(3.0), f32(5.0)
    elif kind=='fp16': a,b = f16(3.0), f16(5.0)
    elif kind=='bf16': a,b = bf16_trunc(3.0), bf16_trunc(5.0)
    else: a,b = 48, 80                     # int8 scaled by 16
    out=[]
    for i in range(ITER):
        if kind=='int8':
            a,b = i8c((a*32 - b*16)>>4), i8c((a*16 + b*32 - b*16)>>4)
        else:
            oa,ob = 2.0,1.0
            na = a*oa - b*ob
            nb = a*ob + b*oa - b*ob
            if kind=='fp32': na,nb = f32(na), f32(nb)
            elif kind=='fp16': na,nb = f16(na), f16(nb)
            elif kind=='bf16': na,nb = bf16_trunc(na), bf16_trunc(nb)
            a,b = na,nb
        if i%3==0:
            na,nb = -b, a-b
            if kind=='fp32': na,nb = f32(na), f32(nb)
            elif kind=='fp16': na,nb = f16(na), f16(nb)
            elif kind=='bf16': na,nb = bf16_trunc(na), bf16_trunc(nb)
            elif kind=='int8': na,nb = i8c(-b), i8c(a-b)
            a,b = na,nb
        if i%5==0:
            x,y = (16,-16) if kind=='int8' else (1,-1)
            na,nb = a+x, b+y
            if kind=='fp32': na,nb = f32(na), f32(nb)
            elif kind=='fp16': na,nb = f16(na), f16(nb)
            elif kind=='bf16': na,nb = bf16_trunc(na), bf16_trunc(nb)
            elif kind=='int8': na,nb = i8c(na), i8c(nb)
            a,b = na,nb
        out.append((a,b))
    return out

# reference = FP64 path (identical computation -> drift identically 0)
ref = run('fp64')
print("REFERENCE (= the FP64 path itself):  a[9999]=%.6e  b[9999]=%.6e" % ref[9999])
print("   is it finite? ", all(math.isfinite(x) and math.isfinite(y) for x,y in ref))
first_inf = next((i for i,(x,y) in enumerate(ref) if not (math.isfinite(x) and math.isfinite(y))), None)
print("   FP64 first non-finite iteration:", first_inf)
print()
print("| Format | Max Drift    | @ 1e-3 | @ 1e-6 | @ 1e-9 | first non-finite |")
print("|--------|-------------|--------|--------|--------|-------------------|")
for kind,label in [('fp64','FP64'),('fp32','FP32'),('fp16','FP16'),('bf16','BF16'),('int8','INT8')]:
    v = run(kind)
    maxd=0.0; viol=[-1,-1,-1]; nonfin=None
    for i,(x,y) in enumerate(v):
        rx,ry = ref[i]
        da,db = x-rx, y-ry
        d = math.sqrt(da*da+db*db)
        if not (math.isfinite(x) and math.isfinite(y)) and nonfin is None: nonfin=i
        if d>maxd: maxd=d
        for t,th in enumerate([1e-3,1e-6,1e-9]):
            if viol[t]<0 and d>th: viol[t]=i
    def f(s): return "Never" if s<0 else "~iter %d"%s
    print("| %-6s | %11.2e | %6s | %6s | %6s | %s |" % (label, maxd, f(viol[0]), f(viol[1]), f(viol[2]),
          ("iter %d"%nonfin) if nonfin is not None else "never"))

print()
print("=== LAST-FINITE drift before overflow (what a 'max drift' column would show) ===")
for kind,label in [('fp32','FP32'),('fp16','FP16'),('bf16','BF16')]:
    v = run(kind); lastfin=0.0; lf_i=-1
    for i,(x,y) in enumerate(v):
        rx,ry = ref[i]
        d = math.sqrt((x-rx)**2 + (y-ry)**2)
        if math.isfinite(d) and d>lastfin: lastfin, lf_i = d, i
    print("  %-5s last finite max drift = %.3e  at iter %d" % (label, lastfin, lf_i))
print()
print("=== magnitude growth model: |2+w| = sqrt(3) = %.6f ; start |(3,5)| = %.4f" % (math.sqrt(3), math.sqrt(19)))
for name,mx in [('FP16',65504.0),('FP32',3.4028235e38),('BF16',3.3895314e38),('FP64',1.7976931e308)]:
    pred = math.log(mx/math.sqrt(19))/math.log(math.sqrt(3))
    print("  %-5s max representable %.4e -> predicted overflow at iter %.1f" % (name,mx,pred))
