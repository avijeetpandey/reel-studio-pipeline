#!/usr/bin/env python3
"""look_audit.py — motionmaxxing's render audit (Apache-2.0, tools/ext/motionmaxxing/scripts/look.py) run on a reel draft (Round 17 QA, 22 Nov 2026).

  python3 -I template/scripts/look_audit.py review/draft.mp4 --out review/look --expect <seconds> --expect-audio

Prints cut sync (cuts within +-80 ms of a sound), end hold / final-shot share (G3), empty frames (G2), loudness. Our ffmpeg has no `drawtext`,
so the contact-sheet timecodes are switched off (FONTS = []) instead of editing the upstream file. Motion energy reads low on a locked-off
talking head in a dim room (v3/v4: 3.6-3.7 vs 6.8 for animated films): report it, do not chase it.
"""
import os, runpy, sys
LOOK = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools", "ext", "motionmaxxing", "scripts", "look.py")
if not os.path.exists(LOOK):
    sys.exit("motionmaxxing not installed: git clone --depth 1 https://github.com/Tejashmakwana/motionmaxxing tools/ext/motionmaxxing")
g = runpy.run_path(LOOK, run_name="look_audit")
g["FONTS"][:] = []
sys.argv = [LOOK] + sys.argv[1:]
g["main"]()
