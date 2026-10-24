#!/usr/bin/env python3
"""Score music tracks for reels: tempo, punch, how fast they get going, and the best start point.

  python3 -I music_energy.py <track.mp3> [<track.mp3> ...] [--len 35] [--json out.json]

Per track: bpm (onset autocorrelation, 70–180), onset_rate (hits/s), loud_db (loudest second),
intro_s (seconds until the track is within 4 dB of its loud level — the soft intro to skip),
best_start (start of the most energetic --len-second window: trim the file there),
energy (0–100 composite: tempo near 100–128, hit density, steady loudness, short intro).
Pure python + ffmpeg, no numpy. Used by reel-edit's sound step (sound.md: "energetic from second 1").
"""
import json, math, struct, subprocess, sys

SR, HOP = 11025, 0.02


def pcm(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    return struct.unpack("<%dh" % (len(raw) // 2), raw)


def analyse(path, win):
    x = pcm(path)
    h = int(SR * HOP)
    n = len(x) // h
    rms = []
    for i in range(n):
        s = 0
        for v in x[i * h:(i + 1) * h:2]:  # every 2nd sample is plenty for energy
            s += v * v
        rms.append(math.sqrt(s / (h / 2)) / 32768 + 1e-9)
    db = [20 * math.log10(r) for r in rms]
    per = [sum(db[i:i + 50]) / len(db[i:i + 50]) for i in range(0, n, 50)]  # per-second dB
    loud = sorted(per)[int(len(per) * 0.9)] if per else -60
    intro = next((i for i, v in enumerate(per) if v > loud - 4), 0)
    # onset envelope (positive flux) and tempo by autocorrelation on 30 s from the intro point
    st = intro * 50
    seg = rms[st:st + 1500]
    on = [max(0.0, seg[i] - seg[i - 1]) for i in range(1, len(seg))]
    m = sum(on) / max(1, len(on))
    o = [v - m for v in on]
    best, lag_best = -1e9, 25
    for lag in range(17, 43):  # 70–176 BPM at 20 ms hops
        s = sum(o[i] * o[i + lag] for i in range(len(o) - lag))
        if s > best:
            best, lag_best = s, lag
    bpm = 60 / (lag_best * HOP)
    if bpm < 85:
        bpm *= 2  # half-time detection → report the felt tempo
    hits = sum(1 for v in on if v > m * 3) / max(1, len(on) * HOP)
    # best window: highest mean loudness with the lowest variance (steady drive)
    best_start, best_score = 0, -1e9
    hi = max(intro + 1, int(len(per) * 0.8) - win)  # stay in the body of the song: after the intro, before the outro
    for s0 in range(intro, max(intro + 1, hi)):
        w = per[s0:s0 + win]
        mu = sum(w) / len(w)
        sd = (sum((v - mu) ** 2 for v in w) / len(w)) ** 0.5
        sc = mu - 0.8 * sd
        if sc > best_score:
            best_score, best_start = sc, s0
    tempo_fit = max(0.0, 1 - abs(bpm - 116) / 50)
    energy = 100 * (0.35 * tempo_fit + 0.3 * min(1, hits / 4) + 0.2 * max(0, 1 - intro / 16) + 0.15 * max(0, min(1, (loud + 30) / 20)))
    return {"file": path.split("/")[-1], "dur": round(n * HOP), "bpm": round(bpm), "onset_rate": round(hits, 1),
            "loud_db": round(loud, 1), "intro_s": intro, "best_start": best_start, "energy": round(energy)}


def main():
    args = [a for a in sys.argv[1:]]
    win = 35
    out = None
    if "--len" in args:
        win = int(args[args.index("--len") + 1]); args = [a for i, a in enumerate(args) if a != "--len" and (i == 0 or args[i - 1] != "--len")]
    if "--json" in args:
        out = args[args.index("--json") + 1]; args = [a for i, a in enumerate(args) if a != "--json" and (i == 0 or args[i - 1] != "--json")]
    rows = []
    for p in args:
        r = analyse(p, win)
        rows.append(r)
        print(f"{r['energy']:3d}  {r['bpm']:3d} bpm  hits {r['onset_rate']:4.1f}/s  intro {r['intro_s']:2d}s  start@{r['best_start']:3d}s  {r['file']}", flush=True)
    if out:
        json.dump(rows, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
