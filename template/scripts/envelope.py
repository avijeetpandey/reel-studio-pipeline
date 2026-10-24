#!/usr/bin/env python3
"""Print a 20 ms RMS (dB) envelope around candidate cut points to find the dip between words.
Usage: python3 -I envelope.py <source.mp4> 36.9-38.9 48.7-50.5 ...
A deep dip (< -45 dB) between two words is a safe place to cut."""
import array, math, subprocess, sys

src, windows = sys.argv[1], sys.argv[2:]
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ar", "16000", "-ac", "1", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
a = array.array("h", pcm)
for w in windows:
    t0, t1 = map(float, w.split("-"))
    row = []
    for k in range(int(t0 * 50), int(t1 * 50)):
        seg = a[k * 320:(k + 1) * 320]
        r = math.sqrt(sum(x * x for x in seg) / len(seg)) if seg else 0
        row.append("%.2f:%d" % (k / 50, 20 * math.log10(r / 32768 + 1e-9)))
    print(w); print(" ".join(row))
