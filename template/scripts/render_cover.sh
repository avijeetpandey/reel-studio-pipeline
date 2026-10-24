#!/usr/bin/env bash
# Thumbnail: pick a frame, cut the subject out, render the cover HTML with headless Chrome.
# Usage: render_cover.sh <source.mp4> <timestamp> <workdir>
# Then copy thumbnail/cover-template.html into <workdir>/cover.html, edit the headline/visual,
# and re-run with SKIP_CUTOUT=1 to only re-render.
set -euo pipefail
SRC="$1"; T="$2"; W="$3"; mkdir -p "$W"
HF="node $HOME/.claude/plugins/cache/hyperframes/hyperframes/$(ls $HOME/.claude/plugins/cache/hyperframes/hyperframes | sort -V | tail -1)/skills/hyperframes/scripts/plugin-cli.mjs"
if [ -z "${SKIP_CUTOUT:-}" ]; then
  ffmpeg -v error -y -ss "$T" -i "$SRC" -frames:v 1 \
    -vf "scale=1440:-2:flags=lanczos,unsharp=5:5:0.8,eq=brightness=0.04:contrast=1.08:saturation=1.12:gamma=1.08" "$W/face.png"
  $HF remove-background "$W/face.png" -o "$W/cutout.png"
fi
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1080,1920 --virtual-time-budget=8000 --allow-file-access-from-files \
  --screenshot="$W/cover.png" "file://$W/cover.html" >/dev/null 2>&1
ffmpeg -v error -y -i "$W/cover.png" -q:v 2 "$W/cover.jpg"
# grid-crop check (3:4 centre crop Instagram shows on the profile)
ffmpeg -v error -y -i "$W/cover.png" -filter_complex "[0]scale=540:-1[a];[0]crop=1080:1440:0:240,scale=540:-1,pad=540:960:0:120:color=0x222222[b];[a][b]hstack" -frames:v 1 "$W/cover-check.png"
echo "cover: $W/cover.jpg   check: $W/cover-check.png"
