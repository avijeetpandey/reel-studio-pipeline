#!/usr/bin/env bash
# One command after the cut: plan -> compose -> carve the music under the voice -> lint.
#   template/auto/run.sh reels/<reel> [world]        (assets/main.mp4 + work/words_cut.json + segments.txt already exist)
# Re-run it any time after editing reels/<reel>/edit_plan.json: pass SKIP_PLAN=1 to keep your edits.
set -euo pipefail
R=$(cd "$1" && pwd); NAME=$(basename "$R"); A="$(cd "$(dirname "$0")" && pwd)"; P="$R/videos/$NAME"; STUDIO="$(cd "$A/../.." && pwd)"
[ -f "$P/hyperframes.json" ] || (mkdir -p "$R/videos" && cd "$R/videos" && npx --yes hyperframes@0.9.44 init "$NAME" --non-interactive --example=blank --skill=general-video >/dev/null 2>&1 || true)
if [ -z "${SKIP_PLAN:-}" ]; then python3 -I "$A/autodirect.py" plan --reel "$R" ${2:+--world "$2"}; fi
python3 -I "$A/compose.py" "$R/edit_plan.json" "$P" ${GRAPHICS:+--graphics "$GRAPHICS"} ${GRAPHICS_JS:+--graphics-js "$GRAPHICS_JS"} ${GRAPHICS_CSS:+--graphics-css "$GRAPHICS_CSS"} ${OVERLAY:+--overlay "$OVERLAY"}
cd "$P"
# shared @hyperframes/core (tools/hf-core, installed once) so a fresh project needs no npm install
[ -d "$STUDIO/tools/hf-core"/node_modules/@hyperframes/core ] || (cd "$STUDIO/tools/hf-core" && npm i @hyperframes/core@0.9.44 --silent --no-audit --no-fund)
if grep -q 'id="music"' index.html; then   # no music in the plan (empty library): nothing to carve
  node ~/.claude/skills/hyperframes-audio/scripts/carve.mjs --comp index.html --bed music --voice voice --strength "${CARVE:-0.25}" --core "$STUDIO/tools/hf-core" | tail -2
fi
npx --yes hyperframes@0.9.44 lint | tail -3
echo "next: npx hyperframes snapshot (transitions) -> render --quality draft -> python3 -I $A/mix_check.py review/draft.mp4 assets/audio/voice.wav"
