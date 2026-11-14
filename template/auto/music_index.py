#!/usr/bin/env python3
"""Analyse every track in the music library and write music/INDEX.json (bpm, beat grid, energy, drop points, moods, licence).

  tools/.venv/bin/python music_index.py [--len 30] [--only file.mp3]

Per track: bpm + every beat time (librosa), energy 0–100, intro_s (seconds until it is within 3 dB of its loud level), `starts` = the 3 best
start points for a --len second reel (a bar line, loudest window, ≥ 85 % of that loudness in the first 3 s so the bed is energetic from second 1),
moods (from genre + tempo + brightness), and where it came from + its licence. `pick_music2.py` reads this file.
"""
import json, os, re, sys
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "composition", "assets", "audio", "music")
LICENCE_YT = "YouTube Audio Library — Attribution not required"
MOOD_BY_GENRE = {
    "funk": ["funky", "upbeat", "warm"], "funk-rock": ["funky", "upbeat"], "hip-hop": ["funky", "upbeat"], "trap": ["bright", "upbeat"], "dance-pop": ["upbeat", "bright"],
    "electropop": ["bright", "upbeat"], "synthpop": ["bright", "upbeat"], "house": ["upbeat", "bright"], "deep-house": ["warm", "upbeat"], "tech-house": ["bright", "upbeat"],
    "tropical-house": ["bright", "warm", "upbeat"], "future-bass": ["bright", "upbeat"], "indie-pop": ["warm", "upbeat"], "lo-fi-beats": ["calm", "warm"], "chillout": ["calm", "warm"],
    "downtempo": ["calm", "warm"], "neo-soul": ["warm", "calm"], "jazz-funk": ["warm", "funky"], "technology": ["bright", "curious"], "lifestyle": ["warm", "bright"],
    "corporate-music": ["bright", "curious"], "rhythmic-underscore": ["curious", "tense"], "cinematic": ["cinematic", "tense"], "underscore": ["curious", "calm"], "pop": ["upbeat", "bright"],
    "electronic": ["bright", "curious"], "edm": ["upbeat", "bright"], "electro-house": ["upbeat", "bright"], "drum-and-bass": ["upbeat", "tense"], "breakbeat": ["funky", "upbeat"],
}


def analyse(path, L):
    import librosa
    y, sr = librosa.load(path, sr=22050, mono=True, duration=300)
    dur = len(y) / sr
    hop = 512
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop)
    tempo = float(np.atleast_1d(tempo)[0])
    bt = librosa.frames_to_time(beats, sr=sr, hop_length=hop)
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    db = 20 * np.log10(rms + 1e-6)
    p90 = np.percentile(db, 90)
    intro = float(t[np.argmax(db > p90 - 3)]) if (db > p90 - 3).any() else 0.0
    cent = float(librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)[0].mean())
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    # window scores on bar lines (every 4th beat)
    bars = bt[::4]
    cands = []
    for b in bars:
        if b + L + 1 > dur:
            break
        w = (t >= b) & (t < b + L)
        first = (t >= b) & (t < b + 3)
        if w.sum() < 10:
            continue
        mean = rms[w].mean()
        if rms[first].mean() < 0.85 * mean:
            continue
        cands.append((float(mean + 0.15 * onset[w].mean() / (onset.max() + 1e-6) * rms.max()), float(b)))
    cands.sort(reverse=True)
    starts, last = [], -999
    for s, b in cands:
        if all(abs(b - x) > 8 for x in starts):
            starts.append(round(b, 2))
        if len(starts) == 3:
            break
    loud = float(np.percentile(db, 95))
    od = float(onset.mean() / (onset.max() + 1e-6))
    energy = int(max(0, min(100, 35 + (1 - abs(tempo - 116) / 60) * 25 + od * 60 + (loud + 30) * 0.6 - intro * 0.5)))
    return dict(duration=round(dur, 1), bpm=round(tempo), beats=[round(float(x), 2) for x in bt], energy=energy, loud_db=round(loud, 1), intro_s=round(intro, 1),
                centroid=round(cent), starts=starts or [round(float(intro), 2)])


def main():
    L = float(sys.argv[sys.argv.index("--len") + 1]) if "--len" in sys.argv else 30.0
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    idxf = os.path.join(ROOT, "INDEX.json")
    idx = json.load(open(idxf)) if os.path.exists(idxf) else {}
    mk = {}
    p = os.path.join(ROOT, "mixkit", "mixkit_index.json")
    if os.path.exists(p):
        mk = {v["file"]: v for v in json.load(open(p)).values()}
    files = [f for f in sorted(os.listdir(ROOT)) if f.endswith(".mp3")] + ["mixkit/" + f for f in sorted(os.listdir(os.path.join(ROOT, "mixkit"))) if f.endswith(".mp3")] if os.path.isdir(os.path.join(ROOT, "mixkit")) else [f for f in sorted(os.listdir(ROOT)) if f.endswith(".mp3")]
    for f in files:
        if only and only not in f:
            continue
        if f in idx and idx[f].get("beats") and not only:
            continue
        try:
            a = analyse(os.path.join(ROOT, f), L)
        except Exception as e:
            print("skip", f, e); continue
        if f.startswith("mixkit/"):
            m = mk.get(os.path.basename(f), {})
            cat = m.get("cat", ""); moods = list(MOOD_BY_GENRE.get(cat, ["curious"]))
            a.update(source="Mixkit", title=m.get("title"), genre=cat, licence=m.get("licence"), url=m.get("source"))
        else:
            moods = ["upbeat", "funky"]
            a.update(source="YouTube Audio Library", licence=LICENCE_YT, genre="library")
        if a["centroid"] > 3200 and "bright" not in moods:
            moods.append("bright")
        a["moods"] = moods
        idx[f] = a
        print(f"{f[:48]:48} bpm {a['bpm']:3} energy {a['energy']:3} intro {a['intro_s']:5} starts {a['starts']} {moods}", flush=True)
        json.dump(idx, open(idxf, "w"), indent=0)
    json.dump(idx, open(idxf, "w"), indent=0)
    print(len(idx), "tracks indexed →", idxf)


if __name__ == "__main__":
    main()
