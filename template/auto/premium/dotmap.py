"""rasterise Natural Earth land (topojson) into a dot grid: rows of '0'/'1', equirectangular, lat 75N..-58S"""
import json, sys
t = json.load(open(sys.argv[1])); sc, tr = t["transform"]["scale"], t["transform"]["translate"]
arcs = []
for a in t["arcs"]:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x * sc[0] + tr[0], y * sc[1] + tr[1]))
    arcs.append(pts)
def ring(idx):
    out = []
    for i in idx:
        p = arcs[i] if i >= 0 else arcs[~i][::-1]
        out += p if not out else p[1:]
    return out
polys = []
for g in t["objects"]["land"]["geometries"]:
    if g["type"] == "Polygon": polys.append([ring(r) for r in g["arcs"]])
    else: polys += [[ring(r) for r in p] for p in g["arcs"]]
def inside(x, y, r):
    c = False; n = len(r)
    for i in range(n):
        x1, y1 = r[i]; x2, y2 = r[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c
W, H = int(sys.argv[2]), int(sys.argv[3]); LAT0, LAT1 = 75, -58
rows = []
for j in range(H):
    lat = LAT0 + (LAT1 - LAT0) * (j + 0.5) / H; row = ""
    for i in range(W):
        lon = -180 + 360 * (i + 0.5) / W
        land = any(inside(lon, lat, p[0]) and not any(inside(lon, lat, h) for h in p[1:]) for p in polys)
        row += "1" if land else "0"
    rows.append(row)
json.dump(dict(w=W, h=H, lat0=LAT0, lat1=LAT1, rows=rows), open(sys.argv[4], "w"))
print("\n".join(r.replace("0", ".").replace("1", "#") for r in rows[::2]))
