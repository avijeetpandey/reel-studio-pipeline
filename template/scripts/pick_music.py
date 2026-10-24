#!/usr/bin/env python3
"""Pick and trim the music bed for a reel — automatically, from the approved library only.

  python3 -I pick_music.py --len 34 [--mood funky|happy|bright] [--bpm 110] [--out assets/audio/bgm.mp3]

Reads template/composition/assets/audio/music/INDEX.md (rows carry "bpm", "energy N/100", "start at S s"),
skips any track used in the last 3 reels of reels/style_log.md, prefers energy >= 75 and BPM 100–130
(or near --bpm), matches --mood when given, then trims the file from its best start point with a 0.3 s
fade-in and a 1.5 s fade-out (sound.md: energetic from the first second). Prints the choice + why.
"""
import argparse, os, re, subprocess, sys
import json
CFG_PATH = os.path.expanduser(os.environ.get("REEL_STUDIO_CONFIG", "~/.config/reel-studio/config.json"))
CFG = json.load(open(CFG_PATH)) if os.path.exists(CFG_PATH) else {}
STUDIO = os.path.expanduser(CFG.get("studio_dir", "~/Documents/reel-studio"))
PLUGIN = os.path.expanduser(CFG.get("plugin_root", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))

H = os.path.expanduser("~")
MUSIC = os.path.join(STUDIO, "template/composition/assets/audio/music")
LOG = os.path.join(STUDIO, "reels/style_log.md")


def tracks():
    rows = []
    for ln in open(os.path.join(MUSIC, "INDEX.md"), encoding="utf-8"):
        if not ln.startswith("| ") or ln.startswith("| file") or ln.startswith("|---"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 4 or not c[0].endswith(".mp3"):
            continue
        e = re.search(r"energy (\d+)/100", c[3]); s = re.search(r"start at (\d+) s", c[3])
        bpm = int(c[2]) if c[2].isdigit() else None
        rows.append({"file": c[0], "mood": c[1].lower(), "bpm": bpm,
                     "energy": int(e[1]) if e else 40, "start": int(s[1]) if s else 0, "notes": c[3]})
    return rows


def recent(n=3):
    used = []
    if os.path.exists(LOG):
        for ln in open(LOG, encoding="utf-8"):
            if ln.startswith("## ") and "carousel" in ln.lower():
                break
            if ln.startswith("| 20"):
                used.append(ln.strip().strip("|").split("|")[-1].strip().lower())
    return used[-n:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--len", type=float, required=True)
    ap.add_argument("--mood")
    ap.add_argument("--bpm", type=int)
    ap.add_argument("--out")
    a = ap.parse_args()
    used = recent()
    best, why = None, ""
    for t in tracks():
        if any(t["file"].split(".")[0] in u or u and u in t["file"] for u in used if u not in ("", "—", "-")):
            continue
        target = a.bpm or 115
        score = t["energy"] - (abs(t["bpm"] - target) / 2 if t["bpm"] else 15)
        if a.mood and a.mood.lower() in t["mood"]:
            score += 12
        if t["energy"] < 72:
            score -= 30  # calm tracks only when nothing energetic fits
        if best is None or score > best[0]:
            best = (score, t)
    if not best:
        sys.exit("no track available — download more from the YouTube Audio Library (Attribution not required)")
    t = best[1]
    print(f"music: {t['file']}  bpm {t['bpm']}  energy {t['energy']}  start {t['start']} s  (skipped recent: {', '.join(used) or 'none'})")
    if a.out:
        src = os.path.join(MUSIC, t["file"])
        fo = max(0.5, a.len - 1.5)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t["start"]), "-i", src, "-t", f"{a.len + 0.5:.2f}",
                        "-af", f"afade=t=in:d=0.3,afade=t=out:st={fo:.2f}:d=1.5", a.out], check=True)
        print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
