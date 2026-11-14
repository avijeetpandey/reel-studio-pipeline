#!/usr/bin/env python3
"""Pick + trim the music bed from music/INDEX.json (YouTube Audio Library + Mixkit; every row carries its licence).

  python3 -I pick_music2.py --len 27 --moods upbeat,funky --reel NAME --out assets/audio/bgm.mp3 [--json]

Energetic from second 1: the start is one of the track's precomputed bar-line starts (loudest window, no soft intro). Skips the last 3 reels' tracks
(reels/auto_style_log.json + the old style_log.md), prefers energy >= 72, BPM 100–126, matching mood. Rotates between a track's top starts by reel name so
the same track never opens the same way twice. Last stdout line (--json) = {file, start, bpm, energy, beats (relative to the trim), licence}.
"""
import argparse, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # the studio folder ($STUDIO)
MUSIC = os.path.join(ROOT, "template/composition/assets/audio/music")


def used_recent(n=3):
    used = []
    try:
        used += [r.get("music") for r in json.load(open(os.path.join(ROOT, "reels/auto_style_log.json"))) if r.get("music")]
    except Exception:
        pass
    p = os.path.join(ROOT, "reels/style_log.md")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            if ln.startswith("| 20") and len(ln.strip().strip("|").split("|")) >= 7:
                used.append(ln.strip().strip("|").split("|")[-1].strip().lower())
    return [u for u in used if u][-n:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--len", type=float, required=True); ap.add_argument("--moods", default="upbeat"); ap.add_argument("--reel", default="")
    ap.add_argument("--out"); ap.add_argument("--json", action="store_true"); ap.add_argument("--bpm", type=int, default=112)
    a = ap.parse_args()
    ip = os.path.join(MUSIC, "INDEX.json")
    if not os.path.exists(ip):
        sys.exit("no music index yet: run template/scripts/fetch_free_audio.py music, then template/auto/music_index.py (the reel is built without music until then)")
    idx = json.load(open(ip))
    used = used_recent()
    moods = [m.strip() for m in a.moods.split(",")]
    best = None
    for f, t in idx.items():
        if any(u and (u in f.lower() or f.lower().replace(".mp3", "") in u) for u in used):
            continue
        if t["duration"] < a.len + 12 or not t.get("starts"):
            continue
        s = t["energy"] - abs(t["bpm"] - a.bpm) / 2.2
        s += 14 * max([1 - i * 0.35 for i, m in enumerate(moods) if m in t["moods"]] or [0])
        if t["energy"] < 72:
            s -= 30
        if t["intro_s"] > 8:
            s -= 4
        if best is None or s > best[0]:
            best = (s, f, t)
    if not best:
        sys.exit("no unused track fits — run fetch_free_audio.py music or add a YouTube Audio Library track")
    _, f, t = best
    k = sum(ord(c) for c in a.reel) % len(t["starts"])
    start = t["starts"][k]
    if start + a.len + 1 > t["duration"]:
        start = t["starts"][0]
    beats = [round(b - start, 3) for b in t["beats"] if start <= b <= start + a.len + 0.5]
    res = dict(file=f, start=start, bpm=t["bpm"], energy=t["energy"], licence=t.get("licence"), source=t.get("source"), beats=beats)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-i", os.path.join(MUSIC, f), "-t", f"{a.len + 0.5:.2f}",
                        "-af", f"afade=t=in:d=0.15,afade=t=out:st={max(0.5, a.len - 0.9):.2f}:d=0.9", a.out], check=True)
    print(f"music: {f}  bpm {t['bpm']}  energy {t['energy']}  start {start}s  ({t.get('source')}, skipped recent: {', '.join(used) or 'none'})", file=sys.stderr)
    print(json.dumps(res))


if __name__ == "__main__":
    main()
