#!/usr/bin/env python3
"""HLG (BT.2100, BT.2020 primaries) -> SDR BT.709 3D LUT (33^3). Usage: make_lut.py out.cube [exposure=0.92]
Used automatically by make_cut.py when the source is HLG HDR (iPhone/Android phone footage)."""
import math, sys
out = sys.argv[1]
expo = float(sys.argv[2]) if len(sys.argv) > 2 else 0.92
a, b, c = 0.17883277, 0.28466892, 0.55991073
def inv_oetf(x):
    x = min(max(x, 0.0), 1.0)
    return x * x / 3 if x <= 0.5 else (math.exp((x - c) / a) + b) / 12
M = [[1.6605, -0.5876, -0.0728], [-0.1246, 1.1329, -0.0083], [-0.0182, -0.1006, 1.1187]]
LW = 1000 / 203
def tm(L):  # linear below knee, smooth roll-off to 1.0 at LW
    k = 0.75
    if L <= k: return L
    t = (L - k) / (LW - k)
    return k + (1 - k) * (1 - (1 - min(t, 1)) ** 2) if t < 1 else 1.0
N = 33
with open(out, "w") as f:
    f.write(f"LUT_3D_SIZE {N}\n")
    for bi in range(N):
        for gi in range(N):
            for ri in range(N):
                rgb = [inv_oetf(v / (N - 1)) for v in (ri, gi, bi)]
                # HLG OOTF (system gamma 1.2) on luminance, scene -> display, normalised so 75% HLG = ref white
                Y = 0.2627 * rgb[0] + 0.6780 * rgb[1] + 0.0593 * rgb[2]
                g = Y ** 0.2 if Y > 0 else 0
                lin = [v * g for v in rgb]
                ref = inv_oetf(0.75) * inv_oetf(0.75) ** 0.2
                lin = [v / ref * expo for v in lin]
                lin = [max(0.0, sum(M[i][j] * lin[j] for j in range(3))) for i in range(3)]
                m = max(lin)
                if m > 0:
                    s = tm(m) / m
                    lin = [v * s for v in lin]
                o = [min(1.0, v) ** (1 / 2.4) for v in lin]
                f.write("%.6f %.6f %.6f\n" % tuple(o))
