#!/usr/bin/env bash
# Fetch the three SIL-OFL fonts the premium layer uses (Anton, Instrument Serif, Hanken Grotesk) + their licence texts from google/fonts
# into template/auto/premium/fonts/. Safe to re-run. compose.py copies them into every reel project; without them type falls back to system fonts.
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)/fonts"; B=https://raw.githubusercontent.com/google/fonts/main/ofl; mkdir -p "$D"
get() { [ -s "$D/$3" ] || curl -fsSL "$B/$1/$2" -o "$D/$3"; }
get anton Anton-Regular.ttf Anton-Regular.ttf;                              get anton OFL.txt OFL-Anton.txt
get instrumentserif InstrumentSerif-Italic.ttf InstrumentSerif-Italic.ttf;  get instrumentserif InstrumentSerif-Regular.ttf InstrumentSerif-Regular.ttf
get instrumentserif OFL.txt OFL-InstrumentSerif.txt
get hankengrotesk 'HankenGrotesk%5Bwght%5D.ttf' HankenGrotesk.ttf;          get hankengrotesk OFL.txt OFL-HankenGrotesk.txt
echo "premium fonts ready in $D"
