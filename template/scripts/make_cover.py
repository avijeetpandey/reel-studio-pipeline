#!/usr/bin/env python3
"""Real-frame cover A/B: a real photo of the creator, no cut-out, no glow.

  python3 -I make_cover.py <reel folder> --lines "Docker needs" --accent "Kubernetes" [--kicker "K8s explained in 30 sec"] \
        [--logos docker:2496ED,kubernetes:326CE5] [--src src.mp4 --crop 1296:2304:252:1536] [--t 38.1] \
        [--b-lines "..." --b-accent "..." --b-caption "..." --b-t 12.4]

Face frame (round 8: a cover face is a NEUTRAL, STILL face — closed mouth, eyes on camera, no teeth, no mid-word frame):
  * default: picks the sharpest frame from the silent gaps of the video (silencedetect) — the mouth is closed there, e.g. the beat
    after the last word. It also writes covers/candidates.png (the best 8) so you can look and override with --t.
  * --window S:E: only search that stretch (needed with --crop: the crop fits ONE framing, a close-up stretch would be mis-cropped).
  * --any-frame: the old behaviour (sharpest frame in the first 12 s, may catch a mid-word mouth).
  * --src <original 4K clip>: take the frame from the source (HLG is matrix-swapped to BT.709) instead of the 1440 p cut, so a crop stays sharp.
  * --crop W:H:X:Y: crop in source pixels (9:16, e.g. 1296:2304:252:1536 on a 2160x3840 wide shot) before scaling to 1080x1920, so a face
    that sits low in a wide shot ends up centred with head-room above it for logos.
  * --grade: ffmpeg eq for the face (default brightens: a dim, muddy face was a rejection reason).
Tool logos: --logos slug:HEX,slug:HEX (simple-icons slugs, brand colour) or path/to.svg:HEX — white rounded badges with a "+" between, above the head.
(--lines holds the lines BEFORE the accent word; the accent is added by the template. --head-top moves A's headline; --zoom lifts a wide-shot face.)
Renders covers/cover_a.jpg (photo) and cover_b.jpg (notebook) with headless Chrome plus covers/grid_check.png (3:4 profile-grid crop).
Never overwrite a cover the creator has already seen: write alternatives with --out-suffix _v2 and show them.
"""
import argparse, glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "thumbnail", "cover-real.html")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HLG = "scale=in_color_matrix=bt2020:out_color_matrix=bt709:in_range=tv:out_range=tv"
GRADE = "eq=brightness=0.05:contrast=1.05:saturation=1.07:gamma=1.12"
SI_VERSION = "13.21.0"
SI_DIR = os.path.expanduser("~/.cache/reel-studio/simple-icons")


def sh(*a, **k):
    return subprocess.run(a, capture_output=True, text=True, **k)


def probe(video, entry):
    return sh("ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", f"stream={entry}", "-of", "csv=p=0", video).stdout.strip()


def silences(video):
    """(start, end) of every pause >= 0.35 s; the end of the clip counts as a silence boundary."""
    out = sh("ffmpeg", "-hide_banner", "-i", video, "-vn", "-af", "silencedetect=noise=-35dB:d=0.35", "-f", "null", "-").stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    dur = float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video).stdout or 0)
    if len(starts) > len(ends):
        ends.append(dur)
    return list(zip(starts, ends))


def sharpness(video, span=None):
    """[(blur, t)] at 4 fps, lower blur = sharper."""
    cmd = ["ffmpeg", "-hide_banner"] + (["-t", str(span)] if span else []) + ["-i", video, "-vf", "fps=4,blurdetect,metadata=print:file=-", "-an", "-f", "null", "-"]
    out, t, res = sh(*cmd).stdout, None, []
    for line in out.splitlines():
        m = re.search(r"pts_time:([0-9.]+)", line)
        if m:
            t = float(m.group(1))
        m = re.search(r"lavfi\.blur=([0-9.]+)", line)
        if m and t is not None:
            res.append((float(m.group(1)), t))
    return res


def pick_frame(video, any_frame, window=None):
    scored = sharpness(video, 12.0 if any_frame else None)
    if window:
        scored = [x for x in scored if window[0] <= x[1] <= window[1]]
    if any_frame:
        return min((s for s in scored if s[1] > 0.4), default=(0, 0.5))[1], []
    gaps = silences(video)
    cands = sorted(s for s in scored if any(a + 0.1 <= s[1] <= b - 0.05 for a, b in gaps))
    if not cands:
        print("no silent gap found: falling back to the sharpest frame of the first 12 s (check the mouth by eye)", file=sys.stderr)
        return min((s for s in scored if s[1] > 0.4), default=(0, 0.5))[1], []
    return cands[0][1], [t for _, t in cands[:8]]


def logo(spec):
    """slug:HEX or file.svg:HEX -> {"d": svg path, "hex": HEX}."""
    name, _, hexv = spec.rpartition(":")
    path = name if name.endswith(".svg") else os.path.join(SI_DIR, "package", "icons", f"{name}.svg")
    if not os.path.exists(path):
        os.makedirs(SI_DIR, exist_ok=True)
        sh("npm", "pack", f"simple-icons@{SI_VERSION}", "--pack-destination", SI_DIR, "--silent")
        sh("tar", "-xzf", glob.glob(os.path.join(SI_DIR, "simple-icons-*.tgz"))[0], "-C", SI_DIR, "package/icons")
    if not os.path.exists(path):
        sys.exit(f"no simple-icons logo '{name}' (browse the slugs at simpleicons.org) — or pass path/to.svg:HEX")
    return {"d": re.search(r' d="([^"]+)"', open(path, encoding="utf-8").read()).group(1), "hex": hexv.lstrip("#")}


def render(html, png):
    sh(CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--window-size=1080,1920",
       "--virtual-time-budget=9000", "--allow-file-access-from-files", f"--screenshot={png}", f"file://{html}")
    sh("ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", png.replace(".png", ".jpg"))


def grab(video, t, out, crop, grade):
    vf = [HLG] if probe(video, "color_transfer") == "arib-std-b67" else []
    if crop:
        vf.append("crop=" + crop)
    vf += ["scale=1080:1920:flags=lanczos", grade]
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", "-vf", ",".join(vf), "-q:v", "1", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("reel"); ap.add_argument("--video"); ap.add_argument("--src", help="original footage (use for --crop on 4K)")
    ap.add_argument("--t", type=float); ap.add_argument("--b-t", type=float, help="different frame for cover B")
    ap.add_argument("--any-frame", action="store_true"); ap.add_argument("--window", help="START:END seconds to search, e.g. the wide-shot stretch when --crop is for the wide framing"); ap.add_argument("--crop"); ap.add_argument("--grade", default=GRADE)
    ap.add_argument("--lines", required=True); ap.add_argument("--accent", required=True); ap.add_argument("--kicker", default="")
    ap.add_argument("--logos", help="slug:HEX,slug:HEX"); ap.add_argument("--by", default=None, help="brand tag (default: brand in ~/.config/reel-studio/config.json)")
    ap.add_argument("--head-top", type=int, help="y of the headline block on cover A (default 880); ~1190 when the face is centred in a 9:16 crop")
    ap.add_argument("--zoom", type=float, help="zoom cover A's photo about its bottom edge (1.25 lifts a wide-shot face ~20%%); --crop is sharper")
    ap.add_argument("--head-size", type=int); ap.add_argument("--accent-size", type=int)
    ap.add_argument("--b-lines"); ap.add_argument("--b-accent"); ap.add_argument("--b-caption", default=""); ap.add_argument("--b-tag", default="")
    ap.add_argument("--out-suffix", default="", help='e.g. "_v2": write cover_a_v2.* so earlier covers are kept')
    a = ap.parse_args()
    reel = os.path.abspath(a.reel); cov = os.path.join(reel, "covers"); os.makedirs(cov, exist_ok=True)
    cut = a.video or os.path.join(reel, "assets", "main.mp4")
    video = a.src or cut
    h = int(probe(video, "height") or 0)
    if h < 1920 and not a.crop:
        print(f"WARNING: source is {probe(video, 'width')}x{h}, below 1080x1920: the photo will look soft. Re-shoot in 4K, or use cover B only.")
    if a.t is not None:
        t, cands = a.t, []
    else:
        t, cands = pick_frame(video, a.any_frame, tuple(float(x) for x in a.window.split(":")) if a.window else None)
    sfx = a.out_suffix
    face = os.path.join(cov, f"face{sfx}.jpg")
    grab(video, t, face, a.crop, a.grade)
    face_b = face
    if a.b_t is not None:
        face_b = os.path.join(cov, f"face_b{sfx}.jpg"); grab(video, a.b_t, face_b, a.crop, a.grade)
    if cands:  # contact sheet of the best neutral candidates: look before approving
        for i, ct in enumerate(sorted(cands)):
            grab(video, ct, os.path.join(cov, f"_c{i}.jpg"), a.crop, a.grade)
        sh("ffmpeg", "-v", "error", "-y", "-pattern_type", "glob", "-i", os.path.join(cov, "_c*.jpg"), "-vf", "scale=270:480,tile=8x1", "-frames:v", "1", os.path.join(cov, "candidates.png"))
        for f in glob.glob(os.path.join(cov, "_c*.jpg")):
            os.remove(f)
        print("candidates (s):", ", ".join(f"{x:.2f}" for x in sorted(cands)))
    by = a.by
    if by is None:
        try:
            by = json.load(open(os.path.expanduser("~/.config/reel-studio/config.json"))).get("brand", "")
        except (OSError, ValueError):
            by = ""
    lines_a = [x for x in a.lines.split("|") if x.strip().lower() != a.accent.strip().lower()]   # the accent word is added by the template: never repeat it in --lines
    logos = [logo(x) for x in a.logos.split(",")] if a.logos else None
    base = {"photo": os.path.basename(face), "pos": "50% 30%", "kicker": a.kicker, "by": by, "headTop": a.head_top, "zoom": a.zoom}
    photo_a = dict(base, layout="photo", lines=lines_a, accent=a.accent, headSize=a.head_size, accentSize=a.accent_size)
    if logos:
        photo_a.update(logos=logos, tapeTop=70, logosTop=215)
    if a.head_top and a.head_top >= 1100:
        photo_a["byBottom"] = 70
    variants = {"a": photo_a,
                "b": dict(base, photo=os.path.basename(face_b), layout="notebook", lines=(a.b_lines or a.lines).split("|"), accent=a.b_accent or a.accent,
                          caption=a.b_caption, tag=a.b_tag or a.kicker)}
    tpl = open(TPL, encoding="utf-8").read()
    for k, cfg in variants.items():
        html = os.path.join(cov, f"cover_{k}{sfx}.html")
        cfg = {x: y for x, y in cfg.items() if y is not None}
        open(html, "w", encoding="utf-8").write(re.sub(r"/\*COVER_JSON\*/.*?/\*END\*/", lambda _: "const COVER=" + json.dumps(cfg, ensure_ascii=False), tpl, flags=re.S))
        render(html, os.path.join(cov, f"cover_{k}{sfx}.png"))
    sh("ffmpeg", "-v", "error", "-y", "-i", os.path.join(cov, f"cover_a{sfx}.png"), "-i", os.path.join(cov, f"cover_b{sfx}.png"), "-filter_complex",
       "[0]crop=1080:1440:0:240,scale=540:-1[a];[1]crop=1080:1440:0:240,scale=540:-1[b];[a][b]hstack", "-frames:v", "1", os.path.join(cov, f"grid_check{sfx}.png"))
    print(f"frame t={t:.2f}s  covers: {cov}/cover_a{sfx}.jpg  cover_b{sfx}.jpg  grid_check{sfx}.png")


if __name__ == "__main__":
    main()
