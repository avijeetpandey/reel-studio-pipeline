#!/usr/bin/env python3
"""Grow the SFX / music libraries from Mixkit (Mixkit License: free for commercial use in videos, NO attribution needed).

  python3 -I fetch_free_audio.py sfx   [--per 14] [--only whoosh,boom]    -> composition/assets/audio/sfx/mixkit/
  python3 -I fetch_free_audio.py music [--per 5]  [--only hip-hop,funk]    -> composition/assets/audio/music/mixkit/
  python3 -I fetch_free_audio.py list                                       (show which category slugs exist)

Every file is analysed (ffmpeg: duration, integrated LUFS, peak) and logged to <dir>/mixkit_index.json with its Mixkit
title, id, category tags and licence line, so nothing unlicensed ever enters the library and every sound can be traced.
Rule (round 8): music must be free-licence + no attribution; YouTube Audio Library and
Mixkit both qualify. Instagram's in-app library is NOT allowed (not licensed outside the app).
"""
import json, os, re, subprocess, sys, time, urllib.request, html

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "composition", "assets", "audio")
UA = {"User-Agent": "Mozilla/5.0 (compatible; reel-studio-pipeline)"}
LICENCE = "Mixkit License (free for commercial use, no attribution) — https://mixkit.co/license/"

SFX_CATS = ["whoosh", "woosh", "swoosh", "swish", "sweep", "sweeping", "swell", "slide", "spin", "impact", "boom", "thud", "stomp", "hit",
            "punch", "crash", "drop", "bass", "cinematic", "click", "tap", "pop", "camera", "ding", "correct", "bell", "chimes", "alerts",
            "notification", "bleep", "beep", "countdown", "cartoon", "cute", "coin", "arcade", "magic", "sparkle", "keyboard", "key", "mouse",
            "laptop", "page", "paper", "dj-record-scratch", "buzzer", "error", "lose", "glitch", "interface", "high-tech", "technology",
            "static", "rewind", "movie", "intro", "sci-fi", "laser", "game-show", "glass", "clock", "heartbeat", "squeak", "funny"]
MUSIC_CATS = ["hip-hop", "funk", "funk-rock", "dance-pop", "electropop", "synthpop", "house", "deep-house", "tech-house", "tropical-house",
              "future-bass", "indie-pop", "trap", "lo-fi-beats", "chillout", "downtempo", "neo-soul", "jazz-funk", "technology", "lifestyle",
              "corporate-music", "rhythmic-underscore", "cinematic", "underscore", "pop", "electronic", "edm", "electro-house", "drum-and-bass",
              "breakbeat", "transition"]


def get(url, binary=False, tries=3):
    for i in range(tries):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30)
            b = r.read()
            return b if binary else b.decode("utf-8", "ignore")
        except Exception as e:
            if i == tries - 1:
                return None
            time.sleep(1.5)


def parse(page, kind):
    out = []
    for blk in page.split('class="item-grid__item"')[1:]:
        m = re.search(r'data-audio-player-preview-url-value="([^"]+)"', blk)
        iid = re.search(r'data-audio-player-item-id-value="(\d+)"', blk)
        title = re.search(r'item-grid-card__title">\s*([^<]+?)\s*</h2>', blk)
        if not (m and iid):
            continue
        cats = re.findall(r'meta-links__link"[^>]*href="/free-(?:sound-effects|stock-music)/([a-z0-9-]+)/"', blk)
        out.append(dict(id=int(iid.group(1)), url=m.group(1), title=html.unescape(title.group(1)) if title else str(iid.group(1)), tags=sorted(set(cats))))
    return out


def probe(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r)
    d = int(dur[1]) * 3600 + int(dur[2]) * 60 + float(dur[3]) if dur else 0
    li = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); pk = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
    return dict(duration=round(d, 2), lufs=float(li[-1]) if li else None, peak_db=float(pk[-1]) if pk else None)


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "list"
    per = int(sys.argv[sys.argv.index("--per") + 1]) if "--per" in sys.argv else (14 if kind == "sfx" else 5)
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    base = "https://mixkit.co/free-sound-effects/" if kind == "sfx" else "https://mixkit.co/free-stock-music/"
    cats = only or (SFX_CATS if kind == "sfx" else MUSIC_CATS)
    if kind == "list":
        for k, b in (("sfx", "https://mixkit.co/free-sound-effects/"), ("music", "https://mixkit.co/free-stock-music/")):
            p = get(b) or ""
            print(k, sorted(set(re.findall(r'href="/free-(?:sound-effects|stock-music)/([a-z0-9-]+)/"', p))))
        return
    outdir = os.path.join(ROOT, kind, "mixkit"); os.makedirs(outdir, exist_ok=True)
    idxf = os.path.join(outdir, "mixkit_index.json")
    idx = json.load(open(idxf)) if os.path.exists(idxf) else {}
    for cat in cats:
        page = get(base + cat + "/")
        if not page:
            print("skip (no page):", cat); continue
        items = parse(page, kind)[:per]
        got = 0
        for it in items:
            key = str(it["id"])
            if key in idx:
                continue
            slug = re.sub(r"[^a-z0-9]+", "-", it["title"].lower()).strip("-")[:40]
            fn = f"{slug}-{it['id']}.mp3"
            b = get(it["url"], binary=True)
            if not b or len(b) < 4000:
                continue
            path = os.path.join(outdir, fn); open(path, "wb").write(b)
            info = probe(path)
            if kind == "sfx" and info["duration"] > 12:      # long ambience / music beds don't belong in the SFX bin
                os.remove(path); continue
            idx[key] = dict(file=fn, title=it["title"], cat=cat, tags=it["tags"], licence=LICENCE, source=f"https://mixkit.co/free-{'sound-effects' if kind == 'sfx' else 'stock-music'}/{cat}/", **info)
            got += 1
            time.sleep(0.3)
        print(f"{cat}: +{got}", flush=True)
        json.dump(idx, open(idxf, "w"), indent=1, ensure_ascii=False)
    print("total", len(idx), "files in", outdir)


if __name__ == "__main__":
    main()
