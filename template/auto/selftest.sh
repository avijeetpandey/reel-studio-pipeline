#!/usr/bin/env bash
# Smoke test of the auto-edit chain on a SYNTHETIC clip (test pattern + tone, fake word timings): plan -> compose -> carve -> lint for all three worlds. No render, no private footage.
#   template/auto/selftest.sh     -> "0 error(s)" three times when plan + compose + effects + CTA cards all assemble
set -euo pipefail
A="$(cd "$(dirname "$0")" && pwd)"; T="$(mktemp -d)/_selftest"          # a leading underscore keeps the world-variety log untouched
mkdir -p "$T/work" "$T/videos/_selftest/assets"
ffmpeg -v error -y -f lavfi -i testsrc2=size=1440x2560:rate=30:duration=20 -f lavfi -i "sine=frequency=220:duration=20" -c:v libx264 -preset ultrafast -pix_fmt yuv420p -c:a aac -shortest "$T/videos/_selftest/assets/main.mp4"
printf '0-5\n5-10\n10-15\n15-20\n' > "$T/segments.txt"
python3 - "$T/work/words_cut.json" <<'PY'
import json, sys
s = ["This is the claim that matters.", "Most people never check it, but you should.", "Now here is the simple reason behind it.", "It saves two hours every single week.", "So the real question is this.", "Do you check it before you post?", "Follow for one more idea tomorrow."]
t, out = 0.2, []
for sent in s:
    ws = sent.split(); isl = []
    for w in ws:
        isl.append([w, round(t, 2), round(t + 0.38, 2)]); t += 0.42
    out.append(isl); t += 0.25
json.dump(out, open(sys.argv[1], "w"))
PY
for W in clean_pop warm_cinema hype_hero; do echo "== $W"; "$A/run.sh" "$T" "$W" | tail -3; done
rm -rf "$(dirname "$T")"
