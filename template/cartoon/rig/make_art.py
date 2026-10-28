#!/usr/bin/env python3
"""Rebuild rig/avi_art.svg (the traced HEAD of the creator's cartoon) from the reference image. Open source only: ffmpeg + vtracer (MIT).
  /tmp/vt/bin/python make_art.py <cartoon image> [workdir]   # needs: python3 -m venv /tmp/vt && /tmp/vt/bin/pip install vtracer
Steps: cut the person out of the sticker (mask_person.py + seeds.json), keep the largest blob, crop the head (src px 232..612 x 262..622),
pad with paper colour so the background is the dominant colour, trace (vtracer defaults: other arguments segfault on Python 3.15),
drop background / full-canvas paths, and DELETE the traced eyes and brows (they are redrawn live by the engine so they can blink and move)."""
import os, re, subprocess, sys
from collections import deque
HERE = os.path.dirname(os.path.abspath(__file__)); WORK = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(HERE, "work")
SRC = os.path.abspath(sys.argv[1])   # your cartoon/sticker image; edit seeds.json (one seed per outlined region) for a new image
os.makedirs(WORK, exist_ok=True); W, H = 864, 1184
def sh(*a, **k): return subprocess.run(a, check=True, **k)
sh("ffmpeg", "-v", "error", "-y", "-i", SRC, os.path.join(WORK, "src.png"))
sh(sys.executable, os.path.join(HERE, "mask_person.py"), os.path.join(WORK, "src.png"), os.path.join(HERE, "seeds.json"), os.path.join(WORK, "person.png"))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(WORK, "person.png"), "-f", "rawvideo", "-pix_fmt", "rgba", "-"], capture_output=True).stdout
a = bytearray(raw[3::4]); seen = bytearray(W * H); best = []
for i in range(W * H):
    if a[i] and not seen[i]:
        q = deque([i]); seen[i] = 1; comp = [i]
        while q:
            k = q.popleft(); y, x = divmod(k, W)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H:
                    j = ny * W + nx
                    if a[j] and not seen[j]: seen[j] = 1; q.append(j); comp.append(j)
        if len(comp) > len(best): best = comp
keep = bytearray(W * H)
for k in best: keep[k] = 1
out = bytearray(raw)
for i in range(W * H):
    if not keep[i]: out[4 * i + 3] = 0
sh("ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-i", "-", os.path.join(WORK, "person_clean.png"), input=bytes(out))
sh("ffmpeg", "-v", "error", "-y", "-i", os.path.join(WORK, "person_clean.png"), "-vf", "crop=380:360:232:262", os.path.join(WORK, "head_only.png"))
sh("ffmpeg", "-v", "error", "-y", "-i", os.path.join(WORK, "head_only.png"), "-f", "lavfi", "-i", "color=c=0xe8ecef:s=780x760", "-filter_complex", "[1][0]overlay=200:200,scale=1560:1520:flags=lanczos", "-frames:v", "1", os.path.join(WORK, "head_pad.png"))
import vtracer
vtracer.convert_image_to_svg_py(os.path.join(WORK, "head_pad.png"), os.path.join(WORK, "head_pad_raw.svg"))
s = open(os.path.join(WORK, "head_pad_raw.svg")).read(); paths = re.findall(r"<path[^>]*/>", s); BG = (232, 236, 239)
col = lambda p: (lambda m: tuple(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)) if m else None)(re.search(r'fill="#([0-9A-Fa-f]{6})"', p))
def bbox(p):
    d = re.search(r' d="([^"]+)"', p).group(1); t = re.search(r"translate\(([-\d.]+),([-\d.]+)\)", p)
    tx, ty = (float(t.group(1)), float(t.group(2))) if t else (0, 0); n = [float(x) for x in re.findall(r"-?\d+\.?\d*", d)]
    return min(n[0::2]) + tx - 400, min(n[1::2]) + ty - 400, max(n[0::2]) + tx - 400, max(n[1::2]) + ty - 400
BOXES = [(182, 368, 290, 492), (416, 368, 524, 492), (176, 318, 298, 372), (410, 318, 532, 372)]      # eyes + brows, art units
inside = lambda b, bx: b[0] >= bx[0] and b[1] >= bx[1] and b[2] <= bx[2] and b[3] <= bx[3]
luma = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
kept, eyes = [], 0
for p in paths:
    c, b = col(p), bbox(p)
    if c and sum((x - y) ** 2 for x, y in zip(c, BG)) < 10 ** 2: continue
    if (b[2] - b[0]) > 1400 and (b[3] - b[1]) > 1400: continue
    if any(inside(b, bx) for bx in BOXES) and c and luma(c) < 200: eyes += 1; continue
    kept.append(p)
open(os.path.join(HERE, "avi_art.svg"), "w").write('<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="1560" height="1520">\n<g transform="translate(-400 -400)">' + "\n".join(kept) + "</g>\n</svg>")
print(f"avi_art.svg: {len(kept)} paths ({eyes} eye/brow paths removed)")
