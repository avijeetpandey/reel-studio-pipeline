#!/usr/bin/env python3
"""Close the music/voice loop: measure a draft, nudge music.vol in edit_plan.json so the voice sits 12 dB over music + SFX (target band 10–14, min >= 8).

  python3 -I balance.py reels/<reel> reels/<reel>/videos/<reel>/review/draft.mp4
  → then:  SKIP_PLAN=1 template/auto/run.sh reels/<reel>   and render the draft again (max 2 rounds; usually 1)
Calibrated 14 Nov 2026 on the a test reel clip: carve 0.5 left the bed 21.9 dB under the voice (too quiet); carve 0.25 + vol 0.38 lands ≈ 12 dB.
"""
import json, os, subprocess, sys
import numpy as np

reel, draft = sys.argv[1], sys.argv[2]
name = os.path.basename(os.path.abspath(reel))
voice = os.path.join(reel, "videos", name, "assets", "audio", "voice.wav")
load = lambda f: np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-vn", "-ac", "1", "-ar", "48000", "-f", "f32le", "-"], capture_output=True).stdout, np.float32).astype(np.float64)
m, v = load(draft), load(voice)
n = min(len(m), len(v)); m, v = m[:n], v[:n]; sr = 48000; vals = []
for s in range(n // sr):
    a, b = s * sr, (s + 1) * sr
    vv, mm = v[a:b], m[a:b]
    if np.sqrt(np.mean(vv ** 2)) < 0.004:
        continue
    g = np.dot(vv, mm) / np.dot(vv, vv); res = mm - g * vv
    vals.append(20 * np.log10(np.sqrt(np.mean((g * vv) ** 2)) / (np.sqrt(np.mean(res ** 2)) + 1e-9)))
med, mn = float(np.median(vals)), float(min(vals))
pf = os.path.join(reel, "edit_plan.json"); p = json.load(open(pf))
old = p["music"]["vol"]
if 10 <= med <= 14 and mn >= 8:
    print(f"median {med:.1f} dB, min {mn:.1f}: balanced, music.vol stays {old}"); sys.exit(0)
new = round(max(0.12, min(0.9, old * 10 ** ((med - 12) / 20))), 2)
p["music"]["vol"] = new; json.dump(p, open(pf, "w"), indent=1, ensure_ascii=False)
print(f"median {med:.1f} dB, min {mn:.1f}: music.vol {old} -> {new}  (re-run: SKIP_PLAN=1 template/auto/run.sh {reel})")
