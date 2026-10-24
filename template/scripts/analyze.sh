#!/usr/bin/env bash
# Step 1: map silences and transcribe every speech "island" on its own for exact word timings.
# Usage: analyze.sh <source.mp4> <workdir>
# Output: <workdir>/islands.txt  — "[i start-end] t word | t word ..." (source time)
#         <workdir>/silences.txt — silence ranges
set -euo pipefail
SRC="$1"; W="$2"
MODEL="${WHISPER_MODEL:-$HOME/.cache/hyperframes/whisper/models/ggml-small.en.bin}"
mkdir -p "$W/isl"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SRC")

# silences at -32 dB, >= 0.15 s
ffmpeg -hide_banner -i "$SRC" -af silencedetect=noise=-32dB:d=0.15 -f null - 2>&1 \
  | grep -oE "silence_(start|end): [0-9.]+" | awk '{print $2}' | paste - - > "$W/silences.txt"

# islands = gaps between silences
python3 -I - "$W/silences.txt" "$DUR" > "$W/isl/list.txt" <<'EOF'
import sys
sil=[tuple(map(float,l.split())) for l in open(sys.argv[1]) if l.strip()]
dur=float(sys.argv[2]); prev=0.0; i=0
for a,b in sil:
    if a-prev>0.05: print(i,f"{prev:.3f}",f"{a:.3f}"); i+=1
    prev=b
if dur-prev>0.05: print(i,f"{prev:.3f}",f"{dur:.3f}")
EOF

: > "$W/islands.txt"
while read -r i a b; do
  s=$(python3 -c "print(max(0,$a-0.05))"); d=$(python3 -c "print($b-$a+0.1)")
  ffmpeg -v error -y -ss "$s" -t "$d" -i "$SRC" -ar 16000 -ac 1 "$W/isl/$i.wav"
  whisper-cli -m "$MODEL" -f "$W/isl/$i.wav" -ml 1 -sow -np 2>/dev/null | python3 -I -c "
import sys,re
o=float('$s');out=[]
for l in sys.stdin:
  m=re.match(r'\[00:00:([\d.]+) --> 00:00:([\d.]+)\]\s+(.*)',l)
  if m and m.group(3).strip(): out.append('%.2f %s'%(float(m.group(1))+o,m.group(3).strip()))
print('[$i $a-$b]',' | '.join(out))" >> "$W/islands.txt"
done < "$W/isl/list.txt"
echo "wrote $W/islands.txt and $W/silences.txt"
