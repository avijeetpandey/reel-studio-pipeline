#!/usr/bin/env python3
"""Round 6 SFX (30 Oct 2026, IG study of 31 editing/sound reels): original synthesized sounds, no downloads, no licences.
Usage: python3 -I make_sfx2.py <out_dir>   (then ffmpeg → mp3). Reuses the helpers of make_sfx.py.
Families named after what the reference editors call them: typewriter, glitch, camera-flash, slice, whip, notif-pop,
negation, stamp, bass-drop, reverse-swell, counter-roll, ding, mouse-click, zap, ui-open, ticktock-rev."""
import math, os, random, sys
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_sfx.py")).read().split("out = sys.argv")[0]
exec(_src)  # SR, svf, noise, env, bell, write, whoosh, riser, hit, chime, tick, soft_pluck, low_pulse ...
random.seed(30)


def mix(*parts):
    n = max(len(p) for p in parts); out = [0.0] * n
    for p in parts:
        for i, v in enumerate(p): out[i] += v
    return out


def at(x, t):  # delay a sound by t seconds
    return [0.0] * int(t * SR) + list(x)


def typewriter(n_keys=9, gap=0.065):
    """Mechanical key clacks with a slight pitch/level jitter and a bell at the end."""
    out = []
    for k in range(n_keys):
        f = random.uniform(1400, 2600); n = int(0.045 * SR)
        clack = [(random.uniform(-1, 1) * 0.7 + math.sin(2 * math.pi * f * i / SR) * 0.5) * math.exp(-i / SR * 120) for i in range(n)]
        thump = [math.sin(2 * math.pi * 180 * i / SR) * math.exp(-i / SR * 70) * 0.6 for i in range(n)]
        out = mix(out, at([a + b for a, b in zip(clack, thump)], k * gap + random.uniform(-0.008, 0.008)))
    return mix(out, at([0.5 * v for v in chime([2093], dur=0.35, gap=0)], n_keys * gap + 0.02))


def glitch(dur=0.32, bad=False):
    """Stuttering bit-crushed burst. bad=True → lower, buzzier 'negative' glitch."""
    n = int(dur * SR); out = []; hold = 0; val = 0.0
    step = 18 if bad else 7
    base = noise(n, False)
    for i in range(n):
        if i % step == 0: val = round(base[i] * 6) / 6
        gate = 1.0 if (i // int(0.022 * SR)) % 3 != 1 else 0.0  # stutter gate
        buzz = math.sin(2 * math.pi * (110 if bad else 740) * i / SR) * 0.4
        out.append((val * 0.8 + buzz) * gate)
    e = env(n, 0.002, 0.08, 1.0)
    return svf([a * b for a, b in zip(out, e)], lambda i: 1800 if bad else 5000, 0.6)


def camera_flash(dur=0.75):
    """Rising capacitor-charge whine then a bright pop and a short tail."""
    n = int(dur * SR); chg = int(0.5 * SR); out = []; ph = 0.0
    for i in range(n):
        if i < chg:
            f = 2200 * (2.8 ** (i / chg)); ph += 2 * math.pi * f / SR
            out.append(0.18 * math.sin(ph) * (i / chg) ** 1.5)
        else:
            t = (i - chg) / SR
            out.append((random.uniform(-1, 1) * math.exp(-t * 55) + 0.5 * math.sin(2 * math.pi * 260 * t) * math.exp(-t * 30)) * 0.9)
    return out


def shutter():
    a = [random.uniform(-1, 1) * math.exp(-i / SR * 260) for i in range(int(0.035 * SR))]
    b = [random.uniform(-1, 1) * math.exp(-i / SR * 200) * 0.8 for i in range(int(0.04 * SR))]
    return svf(mix(a, at(b, 0.075)), lambda i: 3500, 0.8)


def slice_whoosh():
    return whoosh(0.22, 1500, 7000, 3000, q=1.4, peak=0.4)


def whip():
    return whoosh(0.3, 500, 5500, 900, q=1.0, peak=0.35)


def notif_pop():
    return mix(chime([1174.7], dur=0.28, gap=0), at(chime([1568], dur=0.3, gap=0), 0.09))


def negation():
    """Two descending low buzzes — 'wrong'/'negative' highlight."""
    def buzz(f, d=0.16):
        n = int(d * SR)
        return [(1 if math.sin(2 * math.pi * f * i / SR) > 0 else -1) * 0.45 * min(1, i / (0.004 * SR)) * math.exp(-i / SR * 9) for i in range(n)]
    return svf(mix(buzz(196), at(buzz(147, 0.22), 0.17)), lambda i: 1400, 0.7)


def stamp():
    """Rubber-stamp slap: thud + snap + tiny room tail."""
    thud = hit(0.5)[: int(0.5 * SR)]
    snap = svf(noise(int(0.05 * SR), False), lambda i: 2800, 0.8)
    snap = [v * math.exp(-i / SR * 90) * 1.6 for i, v in enumerate(snap)]
    base = mix(thud, snap)
    tail = svf(noise(int(0.4 * SR)), lambda i: 700, 0.9)
    return mix(base, [0.12 * v * math.exp(-i / SR * 10) for i, v in enumerate(tail)])


def bass_drop(dur=1.1):
    n = int(dur * SR); out = []; ph = 0.0
    for i in range(n):
        t = i / SR; f = 28 + 110 * math.exp(-t * 7); ph += 2 * math.pi * f / SR
        out.append(math.tanh(1.4 * math.sin(ph)) * math.exp(-t * 2.4))
    return out


def reverse_swell(dur=1.0):
    return whoosh(dur, 300, 3500, 3500, q=0.8, peak=0.99)  # filter + level peak at the very end = swell into the cut


def counter_roll(n_ticks=16, t0=0.07, t1=0.025):
    out = []; t = 0.0
    for k in range(n_ticks):
        out = mix(out, at(digital_tick(2600 + 40 * k), t)); t += t0 + (t1 - t0) * k / (n_ticks - 1)
    return out


def ding():
    return chime([1760], dur=0.9, gap=0)


def mouse_click():
    a = [math.sin(2 * math.pi * 1500 * i / SR) * math.exp(-i / SR * 380) for i in range(int(0.02 * SR))]
    b = [math.sin(2 * math.pi * 1100 * i / SR) * math.exp(-i / SR * 300) * 0.7 for i in range(int(0.02 * SR))]
    return mix(a, at(b, 0.055))


def zap(dur=0.28):
    n = int(dur * SR); out = []; ph = 0.0
    for i in range(n):
        f = 4200 * (0.12 ** (i / n)); ph += 2 * math.pi * f / SR
        out.append((1 if math.sin(ph) > 0 else -1) * 0.4 * math.exp(-i / SR * 12))
    return svf(out, lambda i: 4000, 0.9)


def ui_open(dur=0.4):
    return mix(digital_sweep(dur, 400, 1800), at(soft_pluck(990, 0.25), dur * 0.55))


def ticktock_rev(n=4, gap=0.22):
    out = []
    for k in range(n):
        f = 1500 if k % 2 == 0 else 1100
        t = [math.sin(2 * math.pi * f * i / SR) * math.exp(-i / SR * 70) for i in range(int(0.08 * SR))]
        out = mix(out, at(t[::-1], k * gap))
    return out


out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out_dir, exist_ok=True)
sounds = {
    "typewriter": typewriter(), "glitch": glitch(), "glitch-negative": glitch(0.4, bad=True), "camera-flash": camera_flash(),
    "camera-shutter": shutter(), "slice": slice_whoosh(), "whip": whip(), "notif-pop": notif_pop(), "negation": negation(),
    "stamp": stamp(), "bass-drop": bass_drop(), "reverse-swell": reverse_swell(), "counter-roll": counter_roll(), "ding": ding(),
    "mouse-click": mouse_click(), "zap": zap(), "ui-open": ui_open(), "ticktock-rev": ticktock_rev(),
}
for name, x in sounds.items():
    write(os.path.join(out_dir, name + ".wav"), x); print(name, round(len(x) / SR, 2), "s")
