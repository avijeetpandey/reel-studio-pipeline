#!/usr/bin/env python3
"""Beat grid for the reel's music bed, and a check that graphic entrances / b-roll cuts land on it.

  python3 -I beat_grid.py <bgm.mp3> [--offset 0] [--out work/beats.json] [--check <composition_dir|index.html>] [--tol 0.09]

Finds the tempo (onset autocorrelation, like music_energy.py) and the beat phase (the offset whose beats line up
with the most onsets), then writes every beat time in REEL time (`--offset` = where the bed starts in the reel).
--check reads every `data-start` of elements tagged `data-component` / `data-broll` / class "cut" in the composition
and reports how far each one is from the nearest beat, with the snapped time to use when it is off by more than
--tol (default 90 ms) but within 150 ms. Speech wins: an entrance tied to a spoken word only moves if the new time
is still ≤ 0.1 s before that word (the edit plan decides; this script only suggests).
Round 4 (WINNING_PATTERNS §23): the motion-studio reel locks "every cut to the beat — 120 BPM, cut every 2 beats, 0 ms off-beat".
"""
import json, math, os, re, struct, subprocess, sys

SR, HOP = 11025, 0.01


def onsets(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True).stdout
    x = struct.unpack("<%dh" % (len(raw) // 2), raw)
    h = int(SR * HOP)
    rms = [math.sqrt(sum(v * v for v in x[i * h:(i + 1) * h:2]) / (h / 2)) / 32768 + 1e-9 for i in range(len(x) // h)]
    lg = [math.log10(r) for r in rms]
    return [max(0.0, lg[i] - lg[i - 1]) for i in range(1, len(lg))]


def grid(on):
    m = sum(on) / max(1, len(on))
    o = [v - m for v in on]
    seg = o[:3000]
    best, lag_best = -1e18, 50
    for lag in range(33, 86):  # 70–180 BPM at 10 ms hops
        s = sum(seg[i] * seg[i + lag] for i in range(len(seg) - lag))
        if s > best:
            best, lag_best = s, lag
    # refine the period to sub-hop precision with a parabola through the neighbours
    def ac(l): return sum(seg[i] * seg[i + l] for i in range(len(seg) - l))
    a, b, c = ac(lag_best - 1), ac(lag_best), ac(lag_best + 1)
    den = a - 2 * b + c
    period = (lag_best + (0.5 * (a - c) / den if den else 0)) * HOP
    if 60 / period < 85:
        period /= 2
    # period + phase together: a comb over the WHOLE bed (±3 % around the estimate, 0.5 ms steps) so the grid
    # does not drift by the end of the reel; the winner collects the most onset energy on its beats
    def comb(per, ph):
        s, t = 0.0, ph
        while t / HOP < len(on) - 1:
            i = int(t / HOP)
            s += max(on[max(0, i - 1):i + 2])
            t += per
        return s
    best_per, best_p, best_s = period, 0.0, -1e18
    per = period * 0.97
    while per <= period * 1.03:
        for k in range(0, max(1, int(per / HOP)), 2):
            sc = comb(per, k * HOP)
            if sc > best_s:
                best_s, best_per, best_p = sc, per, k * HOP
        per += 0.0005
    for k in (-1, 1):  # the coarse phase skipped odd hops
        ph = best_p + k * HOP
        if ph >= 0 and comb(best_per, ph) > best_s:
            best_s, best_p = comb(best_per, ph), ph
    return best_per, best_p


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    def opt(name, d=None):
        return a[a.index(name) + 1] if name in a else d
    bgm, off, tol = a[0], float(opt("--offset", 0)), float(opt("--tol", 0.09))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", bgm], capture_output=True, text=True).stdout or 0)
    period, phase = grid(onsets(bgm))
    beats, t = [], phase
    while t < dur:
        beats.append(round(t + off, 3)); t += period
    res = {"bpm": round(60 / period, 1), "period": round(period, 4), "offset": off, "beats": beats,
           "bars": beats[::4], "note": "snap graphic entrances / b-roll cuts to beats (bars for big moments); speech timing wins"}
    out = opt("--out")
    if out:
        json.dump(res, open(out, "w"), indent=1)
    print(f"{res['bpm']} BPM, beat every {period:.3f}s, first beat at {beats[0] if beats else 0:.3f}s, {len(beats)} beats")
    chk = opt("--check")
    if chk:
        html = os.path.join(chk, "index.html") if os.path.isdir(chk) else chk
        src = open(html, encoding="utf-8").read()
        rows = []
        for m in re.finditer(r"<[^>]+>", src):
            tag = m.group(0)
            if not re.search(r'data-component=|data-broll|class="[^"]*\bcut\b', tag):
                continue
            s = re.search(r'data-start="([\d.]+)"', tag)
            if not s:
                continue
            st = float(s[1])
            name = (re.search(r'data-component="([^"]+)"', tag) or re.search(r'id="([^"]+)"', tag) or [None, "clip"])[1]
            nb = min(beats, key=lambda b: abs(b - st)) if beats else st
            rows.append((st, name, nb, st - nb))
        on_beat = sum(1 for r in rows if abs(r[3]) <= tol)
        for st, name, nb, d in rows:
            if abs(d) <= tol:
                print(f"ok    {st:7.2f}s {name}: {d * 1000:+.0f} ms")
            elif abs(d) <= 0.15:
                print(f"SNAP  {st:7.2f}s {name}: {d * 1000:+.0f} ms off -> data-start=\"{nb:.2f}\" (if it stays ≤ 0.1 s before its word)")
            else:
                print(f"free  {st:7.2f}s {name}: {d * 1000:+.0f} ms (tied to speech, leave it)")
        if rows:
            print(f"\n{on_beat}/{len(rows)} entrances on the beat (±{tol * 1000:.0f} ms)")


if __name__ == "__main__":
    main()
