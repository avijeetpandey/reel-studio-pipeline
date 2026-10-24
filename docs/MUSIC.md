# Music

**Rule:** only YouTube Audio Library tracks marked "Attribution not required" — free to use in your videos (including monetised), not to redistribute, which is why none ship with this repo.

## Build your library (once, ≈ 10 min, Claude does it)
1. Sign in to YouTube Studio in Claude's built-in browser (desktop app) when asked.
2. Claude opens Studio → Audio library, lists tracks through the page's own API (licence = attribution-free; genres hip-hop / pop / dance & electronic / R&B; moods funky / happy / bright; with drums), and downloads ~25 candidates to `research/music_candidates/`.
3. `music_energy.py *.mp3` scores each: BPM, hits per second, intro length, best start point, energy 0–100.
4. Tracks with energy ≥ 72 go to `<studio>/template/composition/assets/audio/music/` with a row in `INDEX.md` (file · mood · bpm · notes with `energy N/100` and `start at S s`); the rest are deleted.

## Per reel (automatic)
`pick_music.py --len <seconds> --mood <mood> --out …/bgm.mp3` → the most energetic track not used in your last 3 reels, BPM near 115, trimmed to its best section with a 0.3 s fade-in and 1.5 s fade-out, so the bed is energetic from the first second. Mixed ≈ −20 dB under the voice, rising on the end card.

## Manual
Drop any attribution-free Audio Library MP3 in the music folder, run `music_energy.py` on it and add its row to `INDEX.md`.
