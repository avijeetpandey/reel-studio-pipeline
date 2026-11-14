# Music

**Rule:** only free-licence, no-attribution music — the YouTube Audio Library ("Attribution not required") or similar (round 8 adds Mixkit via `template/scripts/fetch_free_audio.py music`) — free to use in your videos (including monetised), not to redistribute, which is why none ship with this repo. Never Instagram's in-app music (not licensed outside the app).

## Build your library (once, ≈ 10 min, Claude does it)
1. Sign in to YouTube Studio in Claude's built-in browser (desktop app) when asked.
2. Claude opens Studio → Audio library, lists tracks through the page's own API (licence = attribution-free; genres hip-hop / pop / dance & electronic / R&B; moods funky / happy / bright; with drums), and downloads ~25 candidates to `research/music_candidates/`.
3. `music_energy.py *.mp3` scores each: BPM, hits per second, intro length, best start point, energy 0–100.
4. Tracks with energy ≥ 72 go to `<studio>/template/composition/assets/audio/music/` with a row in `INDEX.md` (file · mood · bpm · notes with `energy N/100` and `start at S s`); the rest are deleted.

## Per reel (automatic)
`pick_music.py --len <seconds> --mood <mood> --out …/bgm.mp3` → the most energetic track not used in your last 3 reels, BPM near 115, trimmed to its best section with a 0.3 s fade-in and 1.5 s fade-out, so the bed is energetic from the first second. Mixed ≈ −20 dB under the voice, rising on the end card.

## Manual
Drop any attribution-free Audio Library MP3 in the music folder, run `music_energy.py` on it and add its row to `INDEX.md`.

## Round 8: machine-readable libraries (music + SFX)
- `python3 template/scripts/fetch_free_audio.py music [--per 3] [--only hip-hop,funk]` and `… sfx [--per 12]` download from Mixkit (free licence, no attribution) into `composition/assets/audio/{music,sfx}/mixkit/` and log every file with its licence line. Nothing is downloaded until you run it, and the files are git-ignored.
- `template/auto/music_index.py` (needs the studio venv) analyses every track into `music/INDEX.json`: BPM, full beat grid, energy 0–100, intro length, three bar-aligned best starts, moods, licence. `template/auto/pick_music2.py` picks the track: energetic from second 1, BPM 100–126 preferred, mood by world, never one of the last 3 reels' tracks, start rotated by reel name.
- `template/auto/sfx_roles.py` files every sound under the job it does (whip, whoosh, hit_soft, impact, riser, pop, tick, click, notif, success, error, negation, shutter, glitch, paper, scratch, sparkle) in `sfx/ROLES.json`; the plan picks one file per role per reel and levels all of them to the same peak before the role volume.
- Close the loop on a draft with `template/auto/balance.py`: it measures the voice against music + SFX and nudges the music volume until the voice sits ≈ 12 dB over everything else (target 10–14 dB).
