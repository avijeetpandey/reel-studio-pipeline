#!/usr/bin/env python3
"""Synthesize original sound effects for reels (no downloads, no licences).
Usage: python3 -I make_sfx.py <out_dir>   → whoosh-long, whoosh-air, riser-metal, hit-heavy, paper-slide,
pen-scribble, ui-success, tick, line-draw, plus a soft 'digital' family (round 4, the 16K free-SFX reel: soft pluck,
low pulse, digital sweep, digital tick, soft electronic hit, check-blip) for UI beats, checklists and counters
(.wav, 44.1 kHz mono, peak −3 dBFS). Convert to mp3 with ffmpeg."""
import math, os, random, struct, sys, wave

SR = 44100
random.seed(11)


def svf(x, cutoff, q=0.7):
    """State-variable band-pass with a per-sample cutoff (Hz) — gives the swept 'air' of whooshes."""
    low = band = 0.0
    out = []
    for i, s in enumerate(x):
        f = 2 * math.sin(math.pi * min(cutoff(i), SR / 6) / SR)
        high = s - low - q * band
        band += f * high
        low += f * band
        out.append(band)
    return out


def noise(n, pinkish=True):
    b0 = b1 = b2 = 0.0
    out = []
    for _ in range(n):
        w = random.uniform(-1, 1)
        if pinkish:  # Paul Kellet's economy pink filter
            b0 = 0.99765 * b0 + w * 0.0990460
            b1 = 0.96300 * b1 + w * 0.2965164
            b2 = 0.57000 * b2 + w * 1.0526913
            w = (b0 + b1 + b2 + w * 0.1848) * 0.2
        out.append(w)
    return out


def env(n, attack, release, shape=2.0):
    a, r = max(1, int(attack * SR)), max(1, int(release * SR))
    return [(i / a) ** shape if i < a else ((n - i) / r) ** shape if i > n - r else 1.0 for i in range(n)]


def bell(n, peak=0.5, power=2.0):
    p = int(n * peak)
    return [(i / p) ** power if i < p else ((n - i) / (n - p)) ** power for i in range(n)]


def write(path, x, peak_db=-3.0):
    m = max(1e-9, max(abs(v) for v in x))
    g = 10 ** (peak_db / 20) / m
    fade = int(0.01 * SR)
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        frames = bytearray()
        for i, v in enumerate(x):
            if i > len(x) - fade:
                v *= (len(x) - i) / fade
            frames += struct.pack("<h", int(max(-1, min(1, v * g)) * 32767))
        w.writeframes(bytes(frames))


def whoosh(dur, f0, f1, f2, q=0.9, peak=0.55):
    n = int(dur * SR)
    def cut(i):
        t = i / n
        return f0 * (f1 / f0) ** (t / peak) if t < peak else f1 * (f2 / f1) ** ((t - peak) / (1 - peak))
    y = svf(noise(n), cut, q)
    e = bell(n, peak, 1.6)
    return [a * b for a, b in zip(y, e)]


def riser(dur=2.0):
    n = int(dur * SR)
    nz = svf(noise(n), lambda i: 200 * (30 ** (i / n)), 0.5)
    out, ph = [], 0.0
    for i in range(n):
        t = i / n
        f = 220 * (6 ** t) * (1 + 0.01 * math.sin(2 * math.pi * 6 * i / SR))
        ph += 2 * math.pi * f / SR
        tone = 0.35 * math.sin(ph) + 0.15 * math.sin(2.01 * ph) + 0.08 * math.sin(3.02 * ph)
        out.append((nz[i] * 0.8 + tone) * (t ** 2.2))
    return out


def hit(dur=1.3):
    n = int(dur * SR)
    out, ph = [], 0.0
    burst = svf(noise(int(0.06 * SR), False), lambda i: 900, 0.6)
    for i in range(n):
        t = i / SR
        f = 45 + 75 * math.exp(-t * 18)
        ph += 2 * math.pi * f / SR
        body = math.tanh(1.8 * math.sin(ph)) * math.exp(-t * 3.2)
        click = burst[i] * 2.5 if i < len(burst) else 0.0
        out.append(body + click)
    return out


def paper(dur=0.45):
    n = int(dur * SR)
    y = svf(noise(n, False), lambda i: 3200 + 1200 * math.sin(i / n * math.pi), 1.2)
    grain = [0.6 + 0.4 * abs(math.sin(2 * math.pi * (35 + 25 * random.random()) * i / SR)) for i in range(n)]
    e = env(n, 0.07, 0.25, 1.4)
    return [a * b * c for a, b, c in zip(y, grain, e)]


def scribble(dur=0.7):
    n = int(dur * SR)
    y = svf(noise(n, False), lambda i: 4200 + 1500 * math.sin(2 * math.pi * 9 * i / SR), 1.4)
    strokes, out = 9.5, []
    for i in range(n):
        s = abs(math.sin(math.pi * strokes * i / SR)) ** 0.7
        out.append(y[i] * s * (0.8 + 0.2 * random.random()))
    e = env(n, 0.03, 0.12, 1.0)
    return [a * b for a, b in zip(out, e)]


def chime(freqs, dur=0.55, gap=0.09):
    n = int(dur * SR)
    out = [0.0] * n
    for k, f in enumerate(freqs):
        st = int(k * gap * SR)
        for i in range(st, n):
            t = (i - st) / SR
            a = min(1, t / 0.006) * math.exp(-t * 7)
            out[i] += a * (math.sin(2 * math.pi * f * t) + 0.25 * math.sin(2 * math.pi * 2 * f * t) + 0.1 * math.sin(2 * math.pi * 3 * f * t))
    return out


def tick():
    n = int(0.05 * SR)
    return [math.sin(2 * math.pi * 2100 * i / SR) * math.exp(-i / SR * 160) for i in range(n)]


def line_draw(dur=0.6):
    n = int(dur * SR)
    y = svf(noise(n, False), lambda i: 1800 + 1400 * i / n, 2.0)
    am = [0.75 + 0.25 * math.sin(2 * math.pi * 23 * i / SR) for i in range(n)]
    e = env(n, 0.05, 0.15, 1.2)
    return [a * b * c for a, b, c in zip(y, am, e)]


def soft_pluck(f=660, dur=0.35):
    """Karplus-Strong pluck, darkened — a gentle 'something appeared'."""
    n, period = int(dur * SR), int(SR / f)
    buf = [random.uniform(-1, 1) for _ in range(period)]
    out = []
    for i in range(n):
        v = buf[i % period]
        buf[i % period] = 0.5 * (v + buf[(i + 1) % period]) * 0.985
        out.append(v)
    return [v * math.exp(-i / SR * 9) for i, v in enumerate(out)]


def low_pulse(dur=0.5, f=58):
    """Sub thump with a soft attack — under a reveal or a big number."""
    n = int(dur * SR)
    return [math.sin(2 * math.pi * (f + 30 * math.exp(-i / SR * 25)) * i / SR) * min(1, i / (0.012 * SR)) * math.exp(-i / SR * 7) for i in range(n)]


def digital_sweep(dur=0.45, f0=300, f1=2400):
    """Rising filtered tone — screen/card transitions instead of an airy whoosh."""
    n, ph, out = int(dur * SR), 0.0, []
    for i in range(n):
        f = f0 * (f1 / f0) ** (i / n)
        ph += 2 * math.pi * f / SR
        out.append(math.sin(ph) + 0.3 * math.sin(2 * ph))
    y = svf(out, lambda i: 600 + 3000 * i / n, 1.4)
    e = bell(n, 0.7, 1.5)
    return [a * b for a, b in zip(y, e)]


def digital_tick(f=3200):
    """Short square blip — counters, list items, cursor clicks."""
    n = int(0.03 * SR)
    return [(1 if math.sin(2 * math.pi * f * i / SR) > 0 else -1) * 0.5 * math.exp(-i / SR * 220) for i in range(n)]


def soft_hit(dur=0.7):
    """Rounded electronic hit: low sine + a short low-passed noise burst (gentler than hit-heavy)."""
    n = int(dur * SR)
    tone = [math.sin(2 * math.pi * 98 * i / SR) * math.exp(-i / SR * 6) for i in range(n)]
    nz = svf(noise(n), lambda i: 900, 0.8)
    return [a + 0.6 * b * math.exp(-i / SR * 30) for i, (a, b) in enumerate(zip(tone, nz))]


out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)
sounds = {
    "whoosh-long": whoosh(1.2, 250, 2600, 500),
    "whoosh-air": whoosh(0.55, 700, 4800, 1500, q=1.1, peak=0.45),
    "riser-metal": riser(),
    "hit-heavy": hit(),
    "paper-slide": paper(),
    "pen-scribble": scribble(),
    "ui-success": chime([880, 1318.5]),
    "tick": tick(),
    "line-draw": line_draw(),
    "soft-pluck": soft_pluck(),
    "low-pulse": low_pulse(),
    "digital-sweep": digital_sweep(),
    "digital-tick": digital_tick(),
    "soft-hit": soft_hit(),
    "check-blip": chime([1046.5, 1568], dur=0.3, gap=0.06),
}
for name, x in sounds.items():
    write(os.path.join(out, name + ".wav"), x)
    print(name)
