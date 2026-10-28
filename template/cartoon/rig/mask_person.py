#!/usr/bin/env python3
"""Cut the person out of a flat-colour cartoon sticker (scenery behind him) without ML:
flood-fill each outlined region from seed points, add the ink outline around them, fill holes.
  python3 -I mask_person.py src.png seeds.json out_rgba.png
seeds.json = {"w":864,"h":1184,"seeds":[[x,y],...],"ink":[43,35,33],"dark_seeds":[[x,y,x0,y0,x1,y1],...]}"""
import json, subprocess, sys
from collections import deque
src, seedf, out = sys.argv[1:4]
cfg = json.load(open(seedf)); W, H = cfg["w"], cfg["h"]; ink = cfg["ink"]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
def px(i): return raw[3*i], raw[3*i+1], raw[3*i+2]
barrier = bytearray(W*H); soft = bytearray(W*H)
for i in range(W*H):
    r, g, b = px(i)
    d2 = (r-ink[0])**2 + (g-ink[1])**2 + (b-ink[2])**2
    if d2 < 45**2: barrier[i] = 1
    if d2 < 120**2: soft[i] = 1
fill = bytearray(W*H)
def grow(seed, ok, box=None):
    x, y = seed; i0 = y*W+x; q = deque([i0]); fill[i0] = 1
    while q:
        i = q.popleft(); y, x = divmod(i, W)
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < W and 0 <= ny < H:
                if box and not (box[0] <= nx <= box[2] and box[1] <= ny <= box[3]): continue
                j = ny*W+nx
                if not fill[j] and ok(j): fill[j] = 1; q.append(j)
BOX = cfg.get("box")
def near(c, tol):
    return lambda j: (not barrier[j]) and (raw[3*j]-c[0])**2 + (raw[3*j+1]-c[1])**2 + (raw[3*j+2]-c[2])**2 < tol*tol
for s in cfg["seeds"]:
    c = px(s[1]*W+s[0]); grow(tuple(s), near(c, cfg.get("tol", 60)), BOX)
    print("seed", s, "filled so far", sum(fill))
for s in cfg.get("dark_seeds", []): grow((s[0], s[1]), lambda j: barrier[j], s[2:6])
for b in cfg.get("dark_boxes", []):
    for yy in range(b[1], b[3]+1):
        for xx in range(b[0], b[2]+1):
            if soft[yy*W+xx]: fill[yy*W+xx] = 1
# add the outline: dilate fill by R px, but only onto barrier-ish pixels
R = cfg.get("outline", 7); mask = bytearray(fill)
cur = set(i for i in range(W*H) if fill[i])
frontier = list(cur)
for _ in range(R):
    nxt = []
    for i in frontier:
        y, x = divmod(i, W)
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x+dx, y+dy
            if 0 <= nx < W and 0 <= ny < H:
                j = ny*W+nx
                if not mask[j] and soft[j]: mask[j] = 1; nxt.append(j)
    frontier = nxt
# fill holes: anything not reachable from the border without crossing the mask
outside = bytearray(W*H); q = deque()
for x in range(W):
    for y in (0, H-1):
        if not mask[y*W+x] and not outside[y*W+x]: outside[y*W+x] = 1; q.append(y*W+x)
for y in range(H):
    for x in (0, W-1):
        if not mask[y*W+x] and not outside[y*W+x]: outside[y*W+x] = 1; q.append(y*W+x)
while q:
    i = q.popleft(); y, x = divmod(i, W)
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < W and 0 <= ny < H:
            j = ny*W+nx
            if not mask[j] and not outside[j]: outside[j] = 1; q.append(j)
rgba = bytearray(W*H*4)
for i in range(W*H):
    if not outside[i]: rgba[4*i:4*i+3] = raw[3*i:3*i+3]; rgba[4*i+3] = 255
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-i", "-", out], input=bytes(rgba), check=True)
print("mask pixels:", sum(1 for i in range(W*H) if not outside[i]))
