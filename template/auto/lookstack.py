#!/usr/bin/env python3
"""lookstack — matte-split relight + grade (free: numpy + OpenCV + ffmpeg). Promoted from the lab 24 Nov 2026 (research/refs_<date>/REPORT.md).
Used by relight.py (the automatic pass: it picks the look, calibrates exposure, renders assets/main_look.mp4 + fg_look.webm).

Why: the references (LIGHT 21-way relights, the "3D captions" amber room) get their premium feel from *light*, not from a global warm tint:
the ROOM is rebuilt (own colour ramp, practical bloom, shafts / blinds, vignette) while the PERSON keeps natural skin and only gets a key light + rim light.
We already have a person matte per reel (`person_matte.py` -> fg.webm, Apple Vision), so the split is free.

  tools/.venv/bin/python lookstack.py list | still frame.png matte.png out.png <look> | sheet frame.png matte.png out.jpg | video main.mp4 fg.webm out.mp4 <look>
"""
import os, sys, subprocess, math
import numpy as np, cv2
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import make_look  # skin-safe tone presets (existing)

W, H = 1080, 1920


def lin(x):  return np.power(np.clip(x, 0, 1), 2.2)
def srgb(x): return np.power(np.clip(x, 0, 1), 1 / 2.2)
def luma(x): return 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]
def hexrgb(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
def blur(a, s): return cv2.GaussianBlur(a, (0, 0), s) if s > 0 else a

# ------------------------------------------------------------------ helpers (fast: big blurs run at 1/4 resolution)
LIN = (np.arange(256, dtype=np.float32) / 255) ** 2.2
SRGB = (np.arange(4096, dtype=np.float32) / 4095) ** (1 / 2.2)
def lin8(rgb8): return LIN[rgb8]
def srgb8(x): return (SRGB[np.clip(x * 4095 + 0.5, 0, 4095).astype(np.int32)] * 255 + 0.5).astype(np.uint8)
def luma(x): return 0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2]
def hexrgb(h): h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)
def blur(a, s):
    if s <= 6: return cv2.GaussianBlur(a, (0, 0), s)
    f = 4 if s >= 24 else 2
    small = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (0, 0), s / f)
    return cv2.resize(small, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_LINEAR)

_cache = {}
def _grid(w=W, h=H):
    k = ("g", w, h)
    if k not in _cache:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        _cache[k] = (xx / w - 0.5, yy / h - 0.5)
    return _cache[k]

def _shift(a, dx, dy):
    return cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (a.shape[1], a.shape[0]), borderMode=cv2.BORDER_REPLICATE)

def shafts_img(angle, n, seed=3, t=0.0, w=W // 2, h=H // 2):
    """soft diagonal light beams; 0..1 (h,w)."""
    xn, yn = _grid(w, h)
    a = math.radians(angle); u = xn * math.cos(a) + yn * math.sin(a); v = -xn * math.sin(a) + yn * math.cos(a)
    rng = np.random.default_rng(seed); img = np.zeros((h, w), np.float32)
    for i in range(n):
        c = rng.uniform(-0.55, 0.55) + 0.012 * math.sin(t * 0.8 + i); wd = rng.uniform(0.02, 0.07)
        img += np.exp(-((u - c) / wd) ** 2) * rng.uniform(0.6, 1.0)
    fall = np.clip(1.0 - (v + 0.6) / 1.5, 0, 1) ** 1.3
    return cv2.GaussianBlur(np.clip(img * fall, 0, 1), (0, 0), 2)

def hot_img(cx, cy, r, w=W // 2, h=H // 2):
    """soft light pool on the wall; centre/radius as fractions of the frame."""
    xn, yn = _grid(w, h)
    return np.exp(-(((xn + 0.5 - cx) / r) ** 2 + ((yn + 0.5 - cy) / (r * 1.35)) ** 2)).astype(np.float32)

def tube_img(x, y0, y1, w=W // 2, h=H // 2, wd=3):
    img = np.zeros((h, w), np.float32); cv2.line(img, (int(x * w), int(y0 * h)), (int(x * w), int(y1 * h)), 1.0, wd)
    return img

# ------------------------------------------------------------------ looks
# room: exp (stops) · duo=(shadow, highlight, amount) colour ramp on the room's own luma · sat · vig · hot=(cx, cy, radius, strength, colour) light pool · floor (min level of the set lighting)
# subj: tone preset (applied BEFORE this module by ffmpeg lut3d = make_look) · expo · key=(dir_deg, strength, colour) · rim=(side -1|+1, colour, width px, strength)
# fx:   bloom (colour, strength, thr) · shafts (angle, colour, strength, n) · halo (colour, strength) · tube (x, y0, y1, colour, strength) · wash=(left colour, right colour, strength) · grain
TARGETS = {"studio_key": (52, 17), "golden_hour": (53, 24), "teal_amber": (52, 15), "spotlight": (53, 6), "moonlight": (50, 12), "high_key": (58, 58), "neon_night": (50, 14), "lime_pop": (52, 22)}  # (face L*, room L*) the calibration aims at
LOOKS = {
    "studio_key": dict(  # default for explainers: deep neutral-cool room with a soft pool of light behind him, warm key, thin rim
        room=dict(exp=-1.0, duo=("#070b10", "#b9c4cf", 0.60), sat=0.75, vig=0.45, hot=(0.62, 0.42, 0.34, 0.85, "#cfdcec"), floor=0.28),
        subj=dict(tone="premium", expo=0.08, key=(-35, 0.16, "#ffd9b0"), rim=(1, "#a9ccff", 5, 0.40)),
        fx=dict(bloom=("#ffe2b8", 0.18, 0.62), halo=("#7f9cc4", 0.16), grain=0.016)),
    "golden_hour": dict(  # window light from the left: amber room, long shafts, warm rim; skin stays natural
        room=dict(exp=-0.9, duo=("#140a05", "#ffcf8a", 0.66), sat=1.0, vig=0.42, hot=(0.12, 0.30, 0.38, 1.1, "#ffc272"), floor=0.22),
        subj=dict(tone="natural", expo=0.02, key=(-60, 0.24, "#ffbf80"), rim=(-1, "#ffb066", 6, 0.65)),
        fx=dict(shafts=(-58, "#ffcf9a", 0.30, 5), bloom=("#ffbf80", 0.24, 0.55), halo=("#ff9a45", 0.18), grain=0.018)),
    "teal_amber": dict(  # classic cinema: dark teal room, amber practical glow behind him, orange rim
        room=dict(exp=-1.25, duo=("#031116", "#6fb8b2", 0.78), sat=0.9, vig=0.5, hot=(0.80, 0.52, 0.22, 1.3, "#ff9a3d"), floor=0.2),
        subj=dict(tone="premium", expo=0.05, key=(35, 0.14, "#ffd2a0"), rim=(-1, "#ff9d4d", 5, 0.55)),
        fx=dict(bloom=("#ffa04d", 0.30, 0.55), halo=("#ff8a3d", 0.09), grain=0.018)),
    "neon_night": dict(  # magenta | cyan wash, a neon tube in the room, cool key, magenta rim
        room=dict(exp=-1.5, duo=("#0b0418", "#4a7bd8", 0.80), sat=1.0, vig=0.55, hot=(0.5, 0.40, 0.45, 0.5, "#6f6fff"), floor=0.18),
        subj=dict(tone="punchy", expo=0.0, key=(40, 0.20, "#9fd0ff"), rim=(-1, "#ff3fa8", 6, 0.85)),
        fx=dict(wash=("#ff2f9e", "#18c8ff", 0.34), tube=(0.84, 0.10, 0.52, "#ff4fc0", 1.3), bloom=("#ff4fb0", 0.22, 0.50), grain=0.02)),
    "moonlight": dict(  # low-key blue noir, one soft shaft from above
        room=dict(exp=-1.7, duo=("#04080f", "#7da0d8", 0.82), sat=0.7, vig=0.60, hot=(0.38, 0.12, 0.30, 0.9, "#a9c4ff"), floor=0.16),
        subj=dict(tone="storm", expo=-0.04, key=(0, 0.18, "#cfe0ff"), rim=(1, "#8fb4ff", 5, 0.80)),
        fx=dict(shafts=(-10, "#bcd2ff", 0.26, 3), halo=("#4f6fb0", 0.14), grain=0.022)),
    "high_key": dict(  # bright airy day look for light topics
        room=dict(exp=0.35, duo=("#a9b4bf", "#fffaf2", 0.35), sat=0.8, vig=0.10, hot=(0.5, 0.35, 0.6, 0.35, "#ffffff"), floor=0.9),
        subj=dict(tone="clean_bright", expo=0.10, key=(-30, 0.10, "#fff2e0"), rim=(1, "#ffffff", 5, 0.30)),
        fx=dict(bloom=("#fff4e0", 0.20, 0.70), grain=0.010)),
    "spotlight": dict(  # hook look: room near-black, he stays lit
        room=dict(exp=-2.1, duo=("#05070b", "#6c7a8c", 0.50), sat=0.55, vig=0.7, hot=(0.5, 0.45, 0.28, 0.7, "#8ea3c2"), floor=0.12),
        subj=dict(tone="premium", expo=0.10, key=(0, 0.24, "#fff0dc"), rim=(1, "#ffffff", 5, 0.45)),
        fx=dict(halo=("#7a8cab", 0.16), grain=0.016)),
    "lime_pop": dict(  # accent-coloured set (reel accent), skin natural
        room=dict(exp=-1.3, duo=("#05110a", "#a6ff4a", 0.74), sat=1.0, vig=0.5, hot=(0.5, 0.40, 0.4, 0.9, "#9dff3d"), floor=0.2),
        subj=dict(tone="premium", expo=0.04, key=(30, 0.14, "#f4ffd8"), rim=(-1, "#b6ff4a", 5, 0.65)),
        fx=dict(halo=("#7cff2a", 0.18), bloom=("#c8ff6a", 0.2, 0.60), grain=0.016)),
}


def apply_look(rgb8, alpha, look, t=0.0):
    """rgb8 (H,W,3) uint8 (ALREADY toned by make_look/lut3d), alpha (H,W) 0..1 (person) -> graded uint8.
    The room is rebuilt at half resolution (it is soft anyway); the person stays full resolution."""
    L = LOOKS[look] if isinstance(look, str) else look
    w2, h2 = W // 2, H // 2
    m1 = alpha.astype(np.float32)
    core = cv2.erode(m1, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))     # pull the matte in: no light fringe round hair
    a = cv2.GaussianBlur(core, (0, 0), 1.2)[..., None]
    base = lin8(rgb8)
    xn, yn = _grid()

    # ---- subject (full res): exposure, key light, rim light in linear light
    sp = L["subj"]
    subj = base * (2 ** sp["expo"])
    k_dir, k_str, k_col = sp["key"]; kd = math.radians(k_dir)
    g = np.clip(0.5 + (xn * math.sin(kd) * 1.6 - yn * 0.6 * math.cos(kd)), 0, 1)[..., None]
    subj = subj * (1 + k_str * g * hexrgb(k_col))
    side, r_col, r_w, r_str = sp["rim"]
    inner = np.clip(core - _shift(blur(core, r_w * 0.6), -side * r_w * 1.2, 0), 0, 1)
    subj = subj + cv2.GaussianBlur(inner, (0, 0), 1.0)[..., None] * hexrgb(r_col) * r_str * 0.45

    # ---- room (half res)
    bh = lin8(cv2.resize(rgb8, (w2, h2), interpolation=cv2.INTER_AREA))
    mh = cv2.resize(m1, (w2, h2), interpolation=cv2.INTER_AREA); ah = cv2.resize(core, (w2, h2), interpolation=cv2.INTER_AREA)[..., None]
    xh, yh = _grid(w2, h2)
    rp = L["room"]
    rl = np.clip(luma(bh) / 0.55, 0, 1)
    sh, hi, amt = rp["duo"]
    duo = (hexrgb(sh) + (hexrgb(hi) - hexrgb(sh)) * np.power(rl, 0.8)[..., None]) * (0.30 + 0.70 * rl[..., None]) * 1.1
    room = bh * (1 - amt) + duo * amt
    gray = luma(room)[..., None]; room = gray + (room - gray) * rp["sat"]
    hc, hy, hr, hs, hcol = rp["hot"]
    pool = hot_img(hc, hy, hr)[..., None]
    room = room * (2 ** rp["exp"]) * (rp["floor"] + (1 - rp["floor"]) * pool * 1.6)
    room = room + pool * hexrgb(hcol) * hs * 0.10
    room = room ** 1.12
    vv = (xh ** 2 + yh ** 2)[..., None]; room = room * (1 - rp["vig"] * np.clip(vv * 3.0, 0, 1))

    fx = L.get("fx", {})
    if "wash" in fx:
        c1, c2, st = fx["wash"]
        gl = np.clip(0.5 - xh * 1.8, 0, 1)[..., None]; gr = np.clip(0.5 + xh * 1.8, 0, 1)[..., None]
        room = room + (gl ** 2 * hexrgb(c1) + gr ** 2 * hexrgb(c2)) * st * 0.30 * (1 - ah * 0.7)
    if "tube" in fx:
        x_, y0, y1, col, st = fx["tube"]
        tb = tube_img(x_, y0, y1)
        glow = (cv2.GaussianBlur(tb, (0, 0), 2) * 1.6 + blur(tb, 13) * 2.0 + blur(tb, 40) * 1.4)[..., None]
        room = room + glow * hexrgb(col) * st * 0.55 * (1 - ah * 0.6) + (tb[..., None] * (1 - ah)) * 0.6
    if "halo" in fx:                                           # faint ambient spill AWAY from the edge (a tight glow reads as a sticker)
        col, st = fx["halo"]
        far = np.clip(blur(mh, 80) - 0.08, 0, 1) * (1 - np.clip(blur(mh, 14) * 2.0, 0, 1))
        room = room + far[..., None] * (1 - ah) * hexrgb(col) * st * 1.0
    if "bloom" in fx:
        col, st, thr = fx["bloom"]
        hl = np.clip((luma(bh) - thr ** 2.2) / (1 - thr ** 2.2 + 1e-4), 0, 1) * (1 - ah[..., 0])
        bl = blur(hl, 8) + blur(hl, 22) * 0.8
        room = room + bl[..., None] * hexrgb(col) * st * 1.3
    s_img_full = None
    if "shafts" in fx:
        ang, col, st, n = fx["shafts"]
        s_img = shafts_img(ang, n, t=t)[..., None]
        room = room + s_img * hexrgb(col) * st * (1 - 0.5 * ah)
        s_img_full = (cv2.resize(s_img[..., 0], (W, H), interpolation=cv2.INTER_LINEAR)[..., None], hexrgb(col) * st * 0.16)

    room = cv2.resize(room, (W, H), interpolation=cv2.INTER_LINEAR)
    if s_img_full is not None: subj = subj + s_img_full[0] * s_img_full[1] * a
    out = subj * a + room * (1 - a)
    if fx.get("grain"):
        rng = np.random.default_rng(int(t * 24) + 1)
        n = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.7)[..., None]
        out = out + n * fx["grain"] * (0.15 + np.clip(luma(out), 0, 1)[..., None])
    return srgb8(out)


def read_alpha_still(path):
    from PIL import Image
    im = Image.open(path)
    return (np.array(im.convert("RGBA"))[..., 3] if im.mode == "RGBA" else np.array(im.convert("L"))).astype(np.float32) / 255


def _work(args):
    rgb, al, look, t = args
    return apply_look(rgb, al, look, t=t).tobytes()


def probe_fps(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
    n, d = r.split("/"); return float(n) / float(d)


def video(src, fg, out, look, t0=0.0, dur=0.0, fps=None, wipe=False, workers=4, tone=None):
    """full production pass: ffmpeg decodes (+ make_look tone via lut3d) -> N workers grade frames in order -> x264 crf 14, audio copied.
    dur=0 means the whole clip. tone = a make_look preset name (defaults to the look's own `subj.tone`)."""
    import multiprocessing as mp, os, tempfile
    L = LOOKS[look] if isinstance(look, str) else look
    fps = fps or probe_fps(src)
    tone = tone or L["subj"]["tone"]
    lut = tempfile.mkdtemp() + "/tone.cube"
    subprocess.run([sys.executable, os.path.join(os.path.dirname(make_look.__file__), "make_look.py"), tone, lut], check=True, capture_output=True)
    tt = ["-t", str(dur)] if dur else []
    ffa = ["ffmpeg", "-v", "error", "-ss", str(t0)] + tt + ["-i", src, "-vf", f"fps={fps},scale={W}:{H},lut3d=file={lut}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    ffm = ["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-ss", str(t0)] + tt + ["-i", fg, "-vf", f"fps={fps},alphaextract,format=gray", "-f", "rawvideo", "-"]
    enc = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-ss", str(t0)] + tt + ["-i", src,
           "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", out]
    pa = subprocess.Popen(ffa, stdout=subprocess.PIPE); pm = subprocess.Popen(ffm, stdout=subprocess.PIPE); pe = subprocess.Popen(enc, stdin=subprocess.PIPE)

    def gen():
        n = 0
        while True:
            fa = pa.stdout.read(W * H * 3); fm = pm.stdout.read(W * H)
            if len(fa) < W * H * 3 or len(fm) < W * H: return
            yield (np.frombuffer(fa, np.uint8).reshape(H, W, 3), np.frombuffer(fm, np.uint8).reshape(H, W).astype(np.float32) / 255, look, n / fps)
            n += 1
    n = 0
    with mp.Pool(workers) as pool:
        for b in pool.imap(_work, gen(), chunksize=2):
            pe.stdin.write(b); n += 1
    pe.stdin.close(); pe.wait(); print("frames", n, "->", out)


def measure(rgb8, alpha, face_box):
    """(face L*, room L*) of a graded frame: face = centre half of the Vision box, room = pixels with no person in the upper 60 % outside the face columns."""
    lab = cv2.cvtColor(rgb8, cv2.COLOR_RGB2LAB).astype(np.float32); Lc = lab[..., 0] * 100 / 255
    x, y, w, h = [int(v) for v in face_box]
    face = float(Lc[y + h // 4:y + 3 * h // 4, x + w // 4:x + 3 * w // 4].mean())
    m = alpha < 0.02; m[int(H * 0.6):, :] = False; m[:, max(0, x - w):min(W, x + 2 * w)] = False
    return face, float(Lc[m].mean()) if m.any() else float(Lc.mean())


def sheet(frame_png, matte_png, out_jpg, looks=None):
    """contact sheet of every look on one frame (ORIGINAL first) - the review image for the creator's pick."""
    from PIL import Image, ImageDraw, ImageFont
    rgb = np.array(Image.open(frame_png).convert("RGB")); al = read_alpha_still(matte_png)
    toned = {}; tiles = []
    for n in ["ORIGINAL"] + list(LOOKS):
        if n == "ORIGINAL": im = rgb
        else:
            tn = LOOKS[n]["subj"]["tone"]
            if tn not in toned: toned[tn] = (np.clip(make_look.apply(rgb.astype(np.float32) / 255, make_look.PRESETS[tn]), 0, 1) * 255 + 0.5).astype(np.uint8)
            im = apply_look(toned[tn], al, n)
        p = Image.fromarray(cv2.resize(im, (360, 640), interpolation=cv2.INTER_AREA)); d = ImageDraw.Draw(p)
        d.rectangle([0, 0, 170, 26], fill=(0, 0, 0)); d.text((4, 3), n, fill=(255, 255, 0), font=ImageFont.load_default(size=18)); tiles.append(np.array(p))
    rows = [np.hstack(tiles[i:i + 5]) for i in range(0, len(tiles), 5)]
    while rows[-1].shape[1] < rows[0].shape[1]: rows[-1] = np.hstack([rows[-1], np.zeros((640, 360, 3), np.uint8)])
    Image.fromarray(np.vstack(rows)).save(out_jpg, quality=88)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("a", nargs="*")
    ap.add_argument("--t0", type=float, default=0); ap.add_argument("--dur", type=float, default=0); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--tone", default=None)
    x = ap.parse_args()
    if x.cmd == "list": print(" ".join(LOOKS))
    elif x.cmd == "still":      # frame.png matte.png out.png look
        from PIL import Image
        Image.fromarray(apply_look(np.array(Image.open(x.a[0]).convert("RGB")), read_alpha_still(x.a[1]), x.a[3])).save(x.a[2], quality=92)
    elif x.cmd == "sheet": sheet(*x.a[:3])             # frame.png matte.png out.jpg
    elif x.cmd == "video": video(x.a[0], x.a[1], x.a[2], x.a[3], x.t0, x.dur, workers=x.workers, tone=x.tone)   # main.mp4 fg.webm out.mp4 look
