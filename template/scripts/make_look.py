#!/usr/bin/env python3
"""Colour looks as 33^3 .cube LUTs (numpy) — skin-safe, calibrated on the round-8 reference reels.

  tools/.venv/bin/python make_look.py <preset> out.cube        # write a LUT
  tools/.venv/bin/python make_look.py --list
  tools/.venv/bin/python make_look.py --preview <preset> frame.png out.png   # before | after strip (for the review step)
  python3 -I make_cut.py src.mp4 segments.txt assets/main.mp4 --look warm_cinema   # applied once, in the cut's single encode

Reference numbers (41 talking-head reels, median): mean luma 96 (top-12 reels 87: a bit moodier), saturation 0.28, red−blue +17 (warm skin),
luma contrast 26, highlights tinted warm (+2…+20 b*), shadows neutral to slightly teal. Presets stay inside those bands: footage must still
look like footage, never like a filter. Skin hues (0–50°, moderate saturation) are protected from tints and saturation boosts.

Presets  clean_bright  gentle S-curve, +exposure, sat ×1.05, a touch warm — default for explainers
         warm_cinema   lifted-to-crushed blacks, teal shadows, amber highlights, sat ×0.96, warm balance — story / career / opinion
         punchy        higher contrast, sat ×1.12, teal/orange split — hype / claims
         neutral       identity (for already-graded footage)
"""
import colorsys, sys
import numpy as np

N = 33
# contrast: S-curve strength · gamma: >1 brightens mids · black: lift(+)/crush(−) · sat · warm: +R −B · shadow/high: (dR,dG,dB) tint at full weight
PRESETS = {
    "neutral": dict(contrast=0.0, gamma=1.0, black=0.0, sat=1.0, warm=0.0, shadow=(0, 0, 0), high=(0, 0, 0), vignette=0.0),
    "clean_bright": dict(contrast=0.22, gamma=1.06, black=0.012, sat=1.05, warm=0.02, shadow=(-0.004, 0.0, 0.01), high=(0.012, 0.006, -0.004), vignette=0.0),
    "warm_cinema": dict(contrast=0.32, gamma=0.98, black=-0.012, sat=0.96, warm=0.035, shadow=(-0.022, 0.004, 0.034), high=(0.034, 0.016, -0.026), vignette=0.18),
    "punchy": dict(contrast=0.42, gamma=1.0, black=-0.018, sat=1.12, warm=0.015, shadow=(-0.02, 0.0, 0.03), high=(0.03, 0.012, -0.02), vignette=0.12),
}


def smooth(x):
    return x * x * (3 - 2 * x)


def apply(rgb, p):
    """rgb: (...,3) float 0..1 -> graded"""
    x = np.clip(rgb, 0, 1) ** (1.0 / p["gamma"])
    x = x + p["contrast"] * (smooth(x) - x)
    x = np.clip(p["black"] + x * (1 - p["black"]), 0, 1)
    L = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    # skin mask (hue 0–50°, moderate saturation, mid luma): protects faces from tints + saturation boosts
    mx, mn = x.max(-1), x.min(-1)
    d = mx - mn + 1e-6
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    s = d / (mx + 1e-6)
    skin = np.exp(-(((h - 22) / 24) ** 2)) * np.clip((s - 0.12) / 0.2, 0, 1) * np.clip((0.95 - s) / 0.25, 0, 1) * np.clip((L[..., 0] - 0.12) / 0.2, 0, 1)
    skin = skin[..., None]
    ws = (1 - L) ** 2.2
    wh = L ** 2.2
    tint = ws * np.array(p["shadow"]) + wh * np.array(p["high"])
    x = x + tint * (1 - 0.65 * skin)
    x[..., 0] *= 1 + p["warm"]; x[..., 2] *= 1 - p["warm"]
    sat = 1 + (p["sat"] - 1) * (1 - 0.5 * skin)
    L2 = (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    x = L2 + (x - L2) * sat
    return np.clip(x, 0, 1)


def write_cube(path, p):
    g = np.linspace(0, 1, N)
    B, G, R = np.meshgrid(g, g, g, indexing="ij")          # cube order: red varies fastest
    rgb = np.stack([R, G, B], -1).reshape(-1, 3)
    out = apply(rgb, p)
    with open(path, "w") as f:
        f.write(f"TITLE \"reel studio look\"\nLUT_3D_SIZE {N}\n")
        for o in out:
            f.write("%.6f %.6f %.6f\n" % tuple(o))


def vf(preset, cube):
    """the ffmpeg filter string make_cut.py splices in (LUT + optional vignette)"""
    p = PRESETS[preset]
    s = f"lut3d=file='{cube}':interp=tetrahedral"
    if p["vignette"]:
        s += f",vignette=angle=PI/{max(4.0, 9 - p['vignette'] * 18):.1f}:mode=backward"
    return s


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--list":
        print("\n".join(PRESETS)); sys.exit()
    if a[0] == "--preview":
        import subprocess, tempfile, os
        preset, src, out = a[1], a[2], a[3]
        cube = tempfile.mktemp(suffix=".cube"); write_cube(cube, PRESETS[preset])
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", f"[0:v]split[a][b];[b]{vf(preset, cube)}[b2];[a][b2]hstack", "-frames:v", "1", out], check=True)
        os.remove(cube); sys.exit()
    write_cube(a[1], PRESETS[a[0]])
