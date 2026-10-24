#!/usr/bin/env bash
# Shade the areas Instagram Reels and YouTube Shorts cover with their own UI (username, caption,
# buttons, progress bar) on 1080x1920 frames, so review stills show at a glance whether any text,
# caption or key visual sits underneath. Union of both apps' commonly cited overlays (approximate):
#   top 250 px, bottom 500 px, right 150 px, left 60 px  ->  safe box x 60-930, y 250-1420
# Usage: safe_zone.sh <image_or_dir> <out_dir>
set -euo pipefail
IN="$1"; OUT="$2"; mkdir -p "$OUT"
VF="scale=1080:1920,drawbox=x=0:y=0:w=iw:h=250:c=red@0.35:t=fill,drawbox=x=0:y=ih-500:w=iw:h=500:c=red@0.35:t=fill,drawbox=x=iw-150:y=250:w=150:h=ih-750:c=red@0.35:t=fill,drawbox=x=0:y=250:w=60:h=ih-750:c=red@0.25:t=fill,drawbox=x=60:y=250:w=870:h=1170:c=lime@0.9:t=3"
if [ -d "$IN" ]; then files=("$IN"/*.png "$IN"/*.jpg); else files=("$IN"); fi
for f in "${files[@]}"; do
  [ -e "$f" ] || continue
  ffmpeg -v error -y -i "$f" -vf "$VF" "$OUT/$(basename "${f%.*}")_safe.jpg"
done
ffmpeg -v error -y -pattern_type glob -i "$OUT/*_safe.jpg" -vf "scale=270:480,tile=6x2:padding=4" -frames:v 1 "$OUT/_sheet.jpg" 2>/dev/null || true
echo "shaded stills + _sheet.jpg in $OUT (red = covered by app UI, green box = safe for text)"
