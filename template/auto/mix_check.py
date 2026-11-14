"""Voice vs (music+SFX) per second: fit the voice stem to the mix, residual = everything else. Target median 10-14 dB, never < 8."""
import subprocess, sys, numpy as np
mix_f, voice_f = sys.argv[1], sys.argv[2]
def load(f):
    raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-vn","-ac","1","-ar","48000","-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(raw,dtype=np.float32).astype(np.float64)
m, v = load(mix_f), load(voice_f)
n = min(len(m), len(v)); m, v = m[:n], v[:n]
sr = 48000; out = []
for s in range(int(n/sr)):
    a, b = s*sr, (s+1)*sr
    vv, mm = v[a:b], m[a:b]
    if np.sqrt(np.mean(vv**2)) < 0.004:  # voice silent in this second
        r = np.sqrt(np.mean(mm**2)); out.append((s, None, 20*np.log10(r+1e-9))); continue
    g = np.dot(vv, mm)/np.dot(vv, vv); res = mm - g*vv
    vr = np.sqrt(np.mean((g*vv)**2)); rr = np.sqrt(np.mean(res**2))
    out.append((s, 20*np.log10(vr/(rr+1e-9)), 20*np.log10(rr+1e-9)))
vals = [x[1] for x in out if x[1] is not None]
print("per-second voice-over-residual (dB):", " ".join(f"{x[0]}:{x[1]:.0f}" if x[1] is not None else f"{x[0]}:--" for x in out))
print(f"median {np.median(vals):.1f} dB  min {min(vals):.1f}  max {max(vals):.1f}  (target median 10-14, min >= 8)")
