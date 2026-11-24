#!/usr/bin/env bash
# One command after the cut + matte: relight (automatic look) -> plan -> compose -> carve the music under the voice -> lint.
#   template/auto/run.sh reels/<reel> [world]        (assets/main.mp4 + work/words_cut.json + segments.txt already exist)
# Re-run it any time after editing reels/<reel>/edit_plan.json: pass SKIP_PLAN=1 to keep your edits.
set -euo pipefail
R=$(cd "$1" && pwd); NAME=$(basename "$R"); A="$(cd "$(dirname "$0")" && pwd)"; P="$R/videos/$NAME"; STUDIO="$(cd "$A/../.." && pwd)"
[ -f "$P/hyperframes.json" ] || (mkdir -p "$R/videos" && cd "$R/videos" && npx --yes hyperframes@0.9.44 init "$NAME" --non-interactive --example=blank --skill=general-video >/dev/null 2>&1 || true)
# LOOK (24 Nov 2026, automatic): matte-split relight -> assets/main_look.mp4 + fg_look.webm. It reads the footage + the script's world and PICKS teal_amber / studio_key / golden_hour
# itself (reasons in work/look.json + EDIT_PLAN.md). Runs BEFORE the plan so the accent colour is picked against the relit room. LOOK=<name> forces one; LOOK=off or RELIGHT=0 skips it.
# It needs assets/fg.webm (person_matte.py) and ~7 min per 36 s reel (4 workers); cached while the cut + matte are unchanged. A failure keeps the plain footage.
if [ -f "$P/assets/fg.webm" ]; then
  "$A/../../tools/.venv/bin/python" "$A/relight.py" "$P" ${2:+--world "$2"} | tail -1 || echo "WARN: relight failed; the reel keeps its plain footage"
else echo "relight skipped: no assets/fg.webm (run person_matte.py first)"; fi
if [ -z "${SKIP_PLAN:-}" ]; then python3 -I "$A/autodirect.py" plan --reel "$R" ${2:+--world "$2"}; fi
python3 -I "$A/compose.py" "$R/edit_plan.json" "$P" ${GRAPHICS:+--graphics "$GRAPHICS"} ${GRAPHICS_JS:+--graphics-js "$GRAPHICS_JS"} ${GRAPHICS_CSS:+--graphics-css "$GRAPHICS_CSS"} ${OVERLAY:+--overlay "$OVERLAY"}
cd "$P"
# shared @hyperframes/core (tools/hf-core, installed once) so a fresh project needs no npm install
[ -d "$STUDIO/tools/hf-core/node_modules/@hyperframes/core" ] || (cd "$STUDIO/tools/hf-core" && npm i @hyperframes/core@0.9.44 --silent --no-audit --no-fund)
node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music --voice voice --strength "${CARVE:-0.25}" --core "$STUDIO/tools/hf-core" | tail -2
npx --yes hyperframes@0.9.44 lint | tail -3
# ONE master only (24 Nov 2026, the creator's call: render only one video; the subscribe / follow split can wait). The YouTube Subscribe master (18 Nov) is dormant:
# set YT_MASTER=1 to build videos/<reel>_yt (same cut, same audio, red Subscribe end card) when the split is wanted again.
if [ "${YT_MASTER:-0}" = "1" ]; then
  PY="$R/videos/${NAME}_yt"; mkdir -p "$PY"
  [ -e "$PY/assets" ] || ln -s "$P/assets" "$PY/assets"
  cp "$P/hyperframes.json" "$P/package.json" "$PY/" 2>/dev/null || true
  python3 -I "$A/compose.py" "$R/edit_plan.json" "$PY" --platform yt ${GRAPHICS:+--graphics "$GRAPHICS"} ${GRAPHICS_JS:+--graphics-js "$GRAPHICS_JS"} ${GRAPHICS_CSS:+--graphics-css "$GRAPHICS_CSS"} ${OVERLAY:+--overlay "$OVERLAY"} | tail -1
  (cd "$PY" && node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music --voice voice --strength "${CARVE:-0.25}" --core "$STUDIO/tools/hf-core" | tail -1)
  echo "yt master composed: $PY (render both: cd videos/$NAME && npx hyperframes render -o ../../renders/${NAME}_final.mp4 ; cd ../${NAME}_yt && npx hyperframes render -o ../../renders/${NAME}_youtube.mp4)"
fi
echo "next: npx hyperframes snapshot (transitions) -> render --quality draft -> python3 -I $A/mix_check.py review/draft.mp4 assets/audio/voice.wav   (ONE render: renders/${NAME}_final.mp4)"
