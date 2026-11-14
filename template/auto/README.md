# template/auto — the automatic edit (14 Nov 2026)

Script in → finished reel out. Manual: `$PLUGIN/skills/reel-edit/humanize.md`. Study behind it: `research/refs_<date>/REPORT.md`.

| file | job |
|---|---|
| `autodirect.py` | `world --script` (world + grade before the cut) · `plan --reel` (camera, transitions, SFX, music, CTA, face-safe rows → `edit_plan.json` + `EDIT_PLAN.md`) |
| `worlds.json` | the three worlds (clean_pop, warm_cinema, hype_hero): grade, caption style, transition weights, punch strength, SFX palette, music moods |
| `compose.py` | `edit_plan.json` → complete HyperFrames `index.html` (captions, `fx.js` effects, SFX, music, grain, progress, CTA, optional `#stage` graphics) |
| `fx.js` | camera/lens effects: camTo, punch, whip, shrink, blurIn, leak, shake, aperture, rgb, grain, pulse |
| `run.sh` | plan → compose → carve (shared `tools/hf-core`) → lint in one command; creates the project if missing (`SKIP_PLAN=1` keeps hand edits; `GRAPHICS/GRAPHICS_JS/GRAPHICS_CSS/OVERLAY` mount drawn scenes) |
| `selftest.sh` | smoke test of all three worlds on a synthetic clip (no render, no private footage) |
| `pick_music2.py`, `music_index.py` | music choice + library analysis (`music/INDEX.json`) |
| `sfx_roles.py` | files every SFX under the job it does (`sfx/ROLES.json`) |
| `face_boxes.swift` (+ built `face_boxes`) | Apple Vision face rectangles (macOS only; rebuilt automatically with `swiftc` if missing) |
| `balance.py` | closes the music loop: measures a draft, nudges `music.vol` in the plan to 12 dB over the voice |
| `mix_check.py` | voice vs music + SFX per second (target median 10–14 dB, min ≥ 8) |

Related: `template/scripts/make_look.py` (LUT looks, used by `make_cut.py --look`), `analyze_ref2.py` + `audio_events.py` (reference-reel study), `fetch_free_audio.py` (library growth).
Python with numpy/opencv/librosa: `tools/.venv/bin/python`.
