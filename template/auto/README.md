# template/auto — the automatic edit (14 Nov 2026)

Script in → finished reel out. Manual: `$PLUGIN/skills/reel-edit/humanize.md`. Study behind it: `research/refs_<date>/REPORT.md`.

| file | job |
|---|---|
| `autodirect.py` | `world --script` (world + grade before the cut) · `plan --reel` (camera, transitions, SFX, music, CTA, face-safe rows → `edit_plan.json` + `EDIT_PLAN.md`) |
| `worlds.json` | the three worlds (clean_pop, warm_cinema, hype_hero): grade, caption style, transition weights, punch strength, SFX palette, music moods |
| `compose.py` | `edit_plan.json` → complete HyperFrames `index.html` (captions, `fx.js` effects, SFX, music, grain, progress, CTA, optional `#stage` graphics) |
| `fx.js` | camera/lens effects: camTo, punch, whip, shrink, blurIn, leak, shake, aperture, rgb, grain, pulse |
| `relight.py` + `lookstack.py` | **automatic look:** measures the footage + the script's world, PICKS teal_amber / studio_key / golden_hour, calibrates exposure, relights the room behind the person matte (skin natural) → `assets/main_look.mp4` + `fg_look.webm`, `work/look.json`. Run by `run.sh` before the plan; `LOOK=<name>` forces one, `LOOK=off` / `RELIGHT=0` skips it. Needs the venv python (OpenCV) and `person_matte.py` first. |
| `run.sh` | relight → plan → compose → carve (shared `tools/hf-core`) → lint in one command (ONE master, `videos/<reel>` only; `YT_MASTER=1` rebuilds the dormant YouTube Subscribe master); creates the project if missing (`SKIP_PLAN=1` keeps hand edits; `GRAPHICS/GRAPHICS_JS/GRAPHICS_CSS/OVERLAY` mount drawn scenes) |
| `selftest.sh` | smoke test of all three worlds on a synthetic clip (no render, no private footage) |
| `pick_music2.py`, `music_index.py` | music choice + library analysis (`music/INDEX.json`) |
| `sfx_roles.py` | files every SFX under the job it does (`sfx/ROLES.json`) |
| `face_boxes.swift` (+ built `face_boxes`) | Apple Vision face rectangles (macOS only; rebuilt automatically with `swiftc` if missing) |
| `balance.py` | closes the music loop: measures a draft, nudges `music.vol` in the plan to 12 dB over the voice |
| `mix_check.py` | voice vs music + SFX per second (target median 10–14 dB, min ≥ 8) |

Related: `template/scripts/make_look.py` (LUT looks, used by `make_cut.py --look`), `analyze_ref2.py` + `audio_events.py` (reference-reel study), `fetch_free_audio.py` (library growth).
Python with numpy/opencv/librosa: `tools/.venv/bin/python`.

## Premium layer (Rounds 14–17, default)
| file | job |
|---|---|
| `person_matte.py` / `.swift` | cuts the speaker out of the cut once per reel (Apple Vision on macOS, `npx hyperframes remove-background` fallback) → `assets/fg.webm` (VP9 + alpha) so words/props can sit BEHIND the head |
| `premium/premium.py` | the director for the layer: footage-derived accent colour, role-styled big words (emphasis budget), lead-line timing, props from sentence cues, lighting cues |
| `premium/kinetic.js` + `premium.css` | the renderer: per-letter type with a sheen, word-timed leads, dot map + comet arc, timer ring, glass search card, server racks, VS logos, spotlight / light rays |
| `premium/v4_finish.py` | a transition at every idea change + the earshot sound kit placed by each sound's peak (falls back to the ROLES.json sounds when earshot is absent) |
| `premium/worlddots.json` | accurate world dot map rasterised from Natural Earth (public domain) by `premium/dotmap.py` |
| `premium/fetch_fonts.sh` | fetches the three SIL-OFL fonts (Anton, Instrument Serif, Hanken Grotesk) with their licences from google/fonts; run once |
| `music_space.py` | adds `voice_share` / `sub_share` to the music index so `pick_music2.py` prefers beds that leave room for the voice |
| `../scripts/look_audit.py` | QA: runs the motionmaxxing `look.py` render audit (cut sync, end hold, empty frames, loudness); needs `git clone --depth 1 https://github.com/Tejashmakwana/motionmaxxing tools/ext/motionmaxxing` (Apache-2.0) |

Optional sound generator: `python3 -m venv tools/ext/earshot/.venv`, then install earshot from GitHub (MIT; `pip install "git+https://github.com/Leonxlnx/earshot"` — the PyPI name belongs to another project) and symlink/copy its `earshot` entry point to `tools/ext/earshot/.venv/bin/earshot`. Switches: `PREMIUM=0` (old look), `KINETIC_V=3` (Round 16 look), `THEME=<accent>`, `PREMIUM_CARDS=1`, `HEADLINE="kick|word"`.
