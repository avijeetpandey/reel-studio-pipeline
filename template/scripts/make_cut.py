#!/usr/bin/env python3
"""Step 2: bake the tightened, upscaled, graded A-roll from a list of kept source ranges.
Usage: python3 -I make_cut.py <source.mp4> <segments.txt> <out.mp4> [--hold 0.3] [--exposure 0.92] [--saturation 1.1] [--no-grade]
segments.txt: one "start-end" (seconds, source time) per line, in order.
Pad each kept range ~0.06 s before the first word and ~0.08 s after the last word.
Prints the cut-time position of every join (use these for punch-in zooms).
HLG HDR sources (phone footage, color_transfer=arib-std-b67) are tone-mapped to SDR BT.709 first and
retagged, otherwise `hyperframes render` switches to HDR compositing and ignores clip-path (the round
face-cam PiP renders square). --exposure tunes that LUT (default 0.92). SDR sources are untouched."""
import os, subprocess, sys

src, segfile, out = sys.argv[1:4]
hold = float(sys.argv[sys.argv.index("--hold") + 1]) if "--hold" in sys.argv else 0.3  # round 3: end on the last word (13/19 proven reels end ≤ 0.4 s after it)
expo = sys.argv[sys.argv.index("--exposure") + 1] if "--exposure" in sys.argv else "0.92"
grade = "" if "--no-grade" in sys.argv else None  # --no-grade: skip the brighten/contrast pass (bright phone footage)
sat = sys.argv[sys.argv.index("--saturation") + 1] if "--saturation" in sys.argv else "1.1"  # lower (0.85–0.95) for already-vivid footage
trc = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=color_transfer",
                      "-of", "default=nw=1:nk=1", src], capture_output=True, text=True, check=True).stdout.strip()
HDR = ""
if trc == "arib-std-b67":  # HLG → 33³ LUT (OOTF, 2020→709, soft-knee) → BT.709; setparams is what retags
    cube = os.path.abspath(out) + ".hlg2sdr.cube"  # (-color_trc etc. alone do not), no zscale in this ffmpeg
    subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "make_lut.py"),
                    cube, expo], check=True)
    HDR = ("scale=in_color_matrix=bt2020:in_range=tv:out_range=pc,format=gbrp,lut3d=file='" + cube.replace("'", "") +
           "',scale=out_color_matrix=bt709:out_range=tv,eq=contrast=1.04:saturation=" + sat + ",format=yuv420p,"
           "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv,")
    print(f"HLG HDR source → tone-mapped to SDR BT.709 (LUT {cube}, exposure {expo})")
elif trc not in ("", "unknown", "bt709", "smpte170m", "bt470bg", "iec61966-2-1"):
    print(f"warning: source color_transfer={trc} is not SDR/HLG — check render.log for hasHdrContent", file=sys.stderr)
S = [tuple(map(float, l.strip().split("-"))) for l in open(segfile) if l.strip()]
f, t, joins = [], 0.0, []
for i, (a, b) in enumerate(S):
    d = b - a
    f.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}]")
    f.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={d - 0.03:.3f}:d=0.03[a{i}]")
    t += d; joins.append(round(t, 2))
n = len(S)
f.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
# upscale + light sharpen + gentle grade; tpad holds the last frame for the CTA end card
EQ = "" if grade == "" else f"eq=brightness=0.035:contrast=1.07:saturation={sat}:gamma=1.06,"
f.append(f"[cv]{HDR}scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,{EQ}"
         f"tpad=stop_mode=clone:stop_duration={hold},format=yuv420p[vo]")
# voice chain (tested on vector_embeddings: identical transcript, +3 dB presence, room tail −11…−15 dB):
# rumble cut → denoise → mud cut → presence + air → de-ess → compress → soft gate (shrinks room echo
# between words, i.e. light de-reverb) → pad silence for the end hold
VOICE = ("highpass=f=80,afftdn=nr=12:nf=-45,equalizer=f=220:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1:g=3,"
         "treble=g=1.5:f=8000,deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=10:release=150:makeup=2,"
         "agate=threshold=0.05:ratio=3:range=0.18:attack=3:release=90")
f.append(f"[ca]{VOICE},apad=pad_dur={hold}[ao]")
open(out + ".filter", "w").write(";\n".join(f))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-/filter_complex", out + ".filter",
                "-map", "[vo]", "-map", "[ao]", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", out], check=True)
print(f"speech length {t:.2f}s + hold {hold}s = {t + hold:.2f}s")
print("joins (cut time):", joins[:-1])
