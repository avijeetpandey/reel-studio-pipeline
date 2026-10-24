#!/usr/bin/env bash
# "Watch" a video: sample frames at a fixed rate and build contact sheets Claude can read.
# Usage: sample_frames.sh <video> <out_dir> [fps=1] [grid=0]
#   fps  : frames per second to sample (use 2 when studying a style reference)
#   grid : 1 = draw a labelled 6x6 grid on each frame (for take geometry)
set -euo pipefail
VIDEO="$1"; OUT="$2"; FPS="${3:-1}"; GRID="${4:-0}"
mkdir -p "$OUT/frames"
VF="fps=${FPS},scale=640:-2"
if [ "$GRID" = "1" ]; then
  # 6x6 grid; columns A-F left to right, rows 1-6 top to bottom
  VF="$VF,drawgrid=w=iw/6:h=ih/6:t=1:c=yellow@0.8"
  for c in 0 1 2 3 4 5; do
    L=$(printf "\\x$(printf %x $((65+c)))")
    VF="$VF,drawtext=text='$L':x=w*$c/6+4:y=4:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.5"
  done
  for r in 0 1 2 3 4 5; do
    VF="$VF,drawtext=text='$((r+1))':x=4:y=h*$r/6+20:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.5"
  done
fi
# timestamp burned in so every frame can be referenced by time
VF="$VF,drawtext=text='%{pts\\:hms}':x=w-tw-6:y=h-th-6:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6"
ffmpeg -v error -y -i "$VIDEO" -vf "$VF" -q:v 4 "$OUT/frames/f_%05d.jpg"
# contact sheets: 4x4 tiles = 16 frames per sheet
ffmpeg -v error -y -framerate 1 -i "$OUT/frames/f_%05d.jpg" -vf "scale=320:-2,tile=4x4:padding=4:color=black" -q:v 4 "$OUT/sheet_%03d.jpg"
N=$(ls "$OUT/frames" | wc -l); S=$(ls "$OUT"/sheet_*.jpg | wc -l)
echo "sampled $N frames at ${FPS}fps -> $OUT/frames ; $S contact sheets -> $OUT/sheet_*.jpg (frame k is at t=(k-1)/${FPS}s)"
