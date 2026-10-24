#!/usr/bin/env bash
# Render a carousel folder into Instagram slides, a LinkedIn PDF, a contact sheet and a QA report.
# Usage: render.sh <carousel_dir>        (the folder holds slides.js and, optionally, assets/)
# Output: <dir>/out/slide-01.png … (1080×1350), slide-XX.jpg (upload these), <name>-linkedin.pdf,
#         sheet.jpg (all slides), grid-check.jpg (cover as the 3:4 profile-grid crop), qa.json
set -euo pipefail
W="$(cd "$1" && pwd)"; T="$(cd "$(dirname "$0")" && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAME="$(basename "$W")"; B="$W/build"; O="$W/out"
rm -rf "$B" "$O"; mkdir -p "$B/assets" "$O"
cp "$T/deck.html" "$B/deck.html"; cp "$W/slides.js" "$B/slides.js"
cp -R "$T/assets/." "$B/assets/"; [ -d "$W/assets" ] && cp -R "$W/assets/." "$B/assets/"
N=$(node -e 'global.window={};require(process.argv[1]);console.log(window.DECK.slides.length)' "$B/slides.js")
run() { "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --virtual-time-budget=9000 --allow-file-access-from-files "$@" 2>/dev/null; }

# 1. QA (overflow + word limits), read back from the page
run --window-size=1080,1350 --dump-dom "file://$B/deck.html?qa=1" | sed -n 's:.*<pre id="qa">\(.*\)</pre>.*:\1:p' > "$O/qa.json"

# 2. one PNG per slide, then high-quality JPGs for upload
for i in $(seq 1 "$N"); do
  f=$(printf "%s/slide-%02d" "$O" "$i")
  run --window-size=1080,1350 --screenshot="$f.png" "file://$B/deck.html?slide=$i" >/dev/null
  ffmpeg -v error -y -i "$f.png" -q:v 1 "$f.jpg"
done

# 3. LinkedIn document post (PDF, one slide per page)
run --no-pdf-header-footer --print-to-pdf="$O/$NAME-linkedin.pdf" "file://$B/deck.html?print=1" >/dev/null

# 4. contact sheet (5 per row) + profile-grid crop check for the cover
COLS=$(( N < 5 ? N : 5 )); ROWS=$(( (N + 4) / 5 ))
ffmpeg -v error -y -framerate 1 -i "$O/slide-%02d.png" -vf "scale=360:-1,tile=${COLS}x${ROWS}:padding=14:margin=14:color=0x777777" -frames:v 1 "$O/sheet.jpg"
ffmpeg -v error -y -i "$O/slide-01.png" -vf "crop=1012:1350:34:0,scale=300:-1" "$O/grid-check.jpg"

node -e '
const qa = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8") || "[]");
const bad = qa.filter(x => x.issues && x.issues.length);
if (!bad.length) console.log("QA: all slides pass");
else { console.log("QA issues:"); bad.forEach(x => x.issues.forEach(m => console.log(`  slide ${x.slide ?? "deck"}: ${m}`))); }
' "$O/qa.json"
echo "slides: $O/slide-01.jpg … $(printf 'slide-%02d.jpg' "$N")   sheet: $O/sheet.jpg   pdf: $O/$NAME-linkedin.pdf"
