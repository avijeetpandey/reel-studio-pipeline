#!/usr/bin/env python3
"""Find the deliberate sound-design events in a reel's audio, even under dense speech.

  tools/.venv/bin/python audio_events.py <video.mp4> [--json out.json] [--png out.png]

Voice rarely owns the sub-bass (<100 Hz) or the air band (>6 kHz) for more than ~120 ms, so:
  impact  = sub-bass spike (>= 9 dB over its 1.5 s median, rise < 60 ms)            -> boom / hit / bass drop
  whoosh  = air-band swell lasting >= 0.2 s, peak in the middle                      -> whoosh / swoosh / whip
  riser   = air-band swell that is still growing when it ends (peak in last third)    -> riser / reverse swell
  fall    = swell that starts at its peak and decays (peak in first third)            -> sweep-out / reverse hit
  tick    = very short air-band click (<= 70 ms) isolated by >= 0.35 s of nothing     -> click / pop / camera shutter
Returns [{t, type, dur, db}] sorted by time. Approximate on purpose: it measures density and type mix, not exact files.
"""
import json, subprocess, sys
import numpy as np


def load(f, sr=32000):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(p.stdout, np.float32), sr


def med_baseline(x, n):
    pad = np.pad(x, (n // 2, n // 2), mode="edge")
    out = np.empty_like(x)
    step = max(1, n // 10)
    idx = np.arange(0, len(x), step)
    vals = np.array([np.median(pad[i:i + n]) for i in idx])
    return np.interp(np.arange(len(x)), idx, vals)


def events(f):
    import librosa
    y, sr = load(f)
    if len(y) < sr:
        return [], 0.0
    hop = 256
    S = np.abs(librosa.stft(y, n_fft=1024, hop_length=hop)) ** 2
    fr = librosa.fft_frequencies(sr=sr, n_fft=1024)
    def band(lo, hi): return 10 * np.log10(S[(fr >= lo) & (fr < hi)].sum(0) + 1e-10)
    sub, hi = band(30, 100), band(6000, 15000)
    hp = hop / sr
    n = int(1.5 / hp)
    bsub, bhi = med_baseline(sub, n), med_baseline(hi, n)
    out = []
    # impacts
    d = sub - bsub
    i = 3
    while i < len(d) - 6:
        if d[i] > 14 and d[i] - d[i - 3] > 8:
            j = i
            while j < len(d) - 1 and d[j] > 6:
                j += 1
            if (j - i) * hp >= 0.1:
                out.append(dict(t=round(i * hp, 2), type="impact", dur=round((j - i) * hp, 2), db=round(float(d[i]), 1)))
            i = j + int(0.2 / hp)
        else:
            i += 1
    # air-band swells
    d = hi - bhi
    sm = np.convolve(d, np.ones(5) / 5, "same")
    i = 0
    while i < len(sm):
        if sm[i] > 6:
            j = i
            while j < len(sm) - 1 and sm[j + 1] > 3.5:
                j += 1
            dur = (j - i + 1) * hp
            seg = sm[i:j + 1]
            pk = int(np.argmax(seg)) / max(1, len(seg) - 1)
            if dur >= 0.25 and seg.max() > 24:
                typ = "riser" if pk > 0.66 else "fall" if pk < 0.25 else "whoosh"
                out.append(dict(t=round(i * hp, 2), type=typ, dur=round(dur, 2), db=round(float(seg.max()), 1)))
            elif dur <= 0.07 and seg.max() > 20:
                out.append(dict(t=round(i * hp, 2), type="tick", dur=round(dur, 2), db=round(float(seg.max()), 1)))
            i = j + 1
        else:
            i += 1
    out.sort(key=lambda e: e["t"])
    # drop ticks that sit within 0.35 s of any other event (sibilants, whoosh edges)
    keep = []
    for k, e in enumerate(out):
        if e["type"] == "tick" and any(abs(o["t"] - e["t"]) < 0.35 for o in out if o is not e):
            continue
        keep.append(e)
    return keep, len(y) / sr


if __name__ == "__main__":
    f = sys.argv[1]
    ev, dur = events(f)
    if "--json" in sys.argv:
        json.dump(ev, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=0)
    cl = {}
    for e in ev:
        cl[e["type"]] = cl.get(e["type"], 0) + 1
    print(json.dumps(dict(duration=round(dur, 1), events=len(ev), per_10s=round(len(ev) / max(dur, 1) * 10, 1), classes=cl)))
    for e in ev:
        print(e)
