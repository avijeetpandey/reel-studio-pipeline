#!/usr/bin/env python3
"""music_space.py — how much room each track leaves for the voice (22 Nov 2026, the creator: "the background music is not at all okay").

  tools/.venv/bin/python -I template/auto/music_space.py      (run after music_index.py whenever tracks are added; idempotent)

Adds to every row of music/INDEX.json, measured over 36 s from the track's best start:
  voice_share  fraction of energy in 300 Hz – 3 kHz (where the voice lives; a busy melody/guitar/vocal here fights the speech)
  sub_share    fraction in 30 – 150 Hz (the pulse that gives energy without masking words)
pick_music2.py penalises voice_share > 0.05 and rewards sub_share. The 22 Nov pick (minimal-techno-01-162: voice 0.033, sub 0.87) sat under the voice
cleanly; the funky bed it replaced (gimme-that-groove: voice 0.089) fought it.
"""
import json, os, warnings
import numpy as np, librosa

warnings.filterwarnings("ignore")
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "composition", "assets", "audio", "music")
P = os.path.join(D, "INDEX.json")
idx = json.load(open(P))
rows = idx if isinstance(idx, dict) else {}
n = 0
for f, r in rows.items():
    if not isinstance(r, dict) or "voice_share" in r:
        continue
    st = (r.get("starts") or [0])[0]
    st = st if isinstance(st, (int, float)) else (st.get("t", 0) if isinstance(st, dict) else 0)
    try:
        y, sr = librosa.load(os.path.join(D, f), sr=22050, offset=float(st), duration=36)
    except Exception as e:
        print("skip", f, e); continue
    S = np.abs(librosa.stft(y, n_fft=2048)) ** 2
    fr = librosa.fft_frequencies(sr=sr)
    tot = S.sum() + 1e-12
    r["voice_share"] = round(float(S[(fr >= 300) & (fr < 3000)].sum() / tot), 4)
    r["sub_share"] = round(float(S[(fr >= 30) & (fr < 150)].sum() / tot), 4)
    n += 1
json.dump(idx, open(P, "w"), indent=1)
print(f"measured {n} tracks")
