---
name: studio-setup
description: First-run setup (and re-setup) for the Reel Studio pipeline — interviews the creator about their channel, brand, audience, posting slots, approval gates and Drive folder, writes ~/.config/reel-studio/config.json and $STUDIO/CHANNEL_RULES.md, installs the template into the studio folder, checks/installs dependencies, generates the original SFX pack and guides the music library. Use when the user says "set up reel studio", "studio setup", "configure the pipeline", "change my channel settings", or when any other Reel Studio skill finds the config missing.
---

# Studio setup (run once, re-run any time to change answers)

Goal: after this, `make: <topic>` works for this person exactly like it does for the author — with *their* name, brand, audience and rules.

## 0. Check what exists
- `cat ~/.config/reel-studio/config.json` — if it exists, show the current answers and ask which to change (re-setup), otherwise do the full interview.
- `$PLUGIN` = this plugin's root = two folders up from this skill's base directory (the folder that contains `skills/` and `template/`).

## 1. Interview (ask in small batches with AskUserQuestion where there are clear options; free text otherwise). Never invent answers — use the default only when the user says "default".
**Creator & brand**
1. Your name (as shown on screen) — `creator_name`
2. Brand / channel name (e.g. "Decoded by Sam") — `brand`
3. Instagram handle without @ — `handle` (also YouTube handle if different — `yt_handle`)
4. Your role / credibility line (e.g. "Senior software engineer", "Fitness coach") — `role`
5. One-line promise for the follow card (e.g. "one AI thing decoded every day") — `promise`
6. Accent colour (hex, default `#3ee0ff`) and an optional avatar image path (cartoon or photo, used on carousels/CTA) — `accent`, `avatar`
7. Employer or clients you must never reveal internals about (optional) — `confidential`

**Audience & content**
8. Niche + topics (e.g. "AI tools and tech careers") — `niche`
9. Audience: who + where (country/city, language) — `audience`; spoken language(s) in your videos — `languages` (if not English-only, offer the multilingual whisper model in step 4)
10. Topics to prefer / avoid — `prefer`, `avoid`
11. Series names you want to run (e.g. "Fact or Hype?", "AI Decoded") — `series`

**Channel rules (defaults in brackets — these came from the author's analytics, keep or change)**
12. Reel length [25–35 s speech, hard cap 40 s] — `length`
13. CTA style [one debatable yes/no question; no "comment KEYWORD for DM"] — `cta`
14. Timezone [Asia/Kolkata] and posting slots [Instagram 7–9 PM, YouTube 12–2 PM, one per day, never two within 12 h, never 11 PM–9 AM] — `timezone`, `slots`
15. Music rule [YouTube Audio Library "Attribution not required" only; the pipeline downloads tracks without asking] — `music_rule`

**Approval gates & delivery**
16. Approve the script/shoot sheet before filming? [yes — checkpoint 1] — `gate_script`
17. Approve the Studio preview before the final render? [yes] — `gate_preview`
18. Upload deliverables to Google Drive? [yes] → rclone remote name [gdrive] + folder [reels] (always a new subfolder per reel) — `drive_remote`, `drive_folder`. If they say no, uploads are skipped and files stay local.
19. Where should the studio folder live? [~/Documents/reel-studio] — `studio_dir`
20. Platforms [Instagram + YouTube Shorts + LinkedIn post + carousel] — `platforms`

## 2. Write the config
Save the answers to a JSON file in the scratchpad, then:
`python3 -I "$PLUGIN/scripts/configure.py" --answers <answers.json> --plugin "$PLUGIN"`
It writes `~/.config/reel-studio/config.json`, generates `$STUDIO/CHANNEL_RULES.md` from the answers, copies `$PLUGIN/template/` into `$STUDIO/template/` (filling `__BRAND__`, `__HANDLE__`, `__NAME__`, `__ROLE__`, `__PROMISE__`, `__ACCENT__`), creates `reels/`, `carousels/`, `research/`, `inbox/`, an empty `reels/style_log.md` and the music `INDEX.md`. Re-running keeps existing reels and logs.

## 3. Dependencies
Run `bash "$PLUGIN/scripts/setup.sh"` (checks, and offers to install via Homebrew: ffmpeg, node ≥ 18, python3, whisper-cpp + the small.en model, rclone, yt-dlp; checks Google Chrome; warms `npx hyperframes`). Tell the user what's missing and the exact command for anything that needs their password. HyperFrames skills: recommend installing the HyperFrames plugin (`/plugin marketplace add heygen-com/hyperframes` if not present) because `reel-edit` uses them.

## 4. Media
- **SFX:** `python3 -I $STUDIO/template/scripts/make_sfx.py $STUDIO/template/composition/assets/audio/sfx` generates an original, licence-free SFX pack (then convert to mp3 as the script says). Optionally add more from the HyperFrames `media-use` skill.
- **Music:** the library starts empty. Follow "Music library" in `make-content` (YouTube Studio → Audio Library in the signed-in browser → score with `music_energy.py` → keep energy ≥ 72). Ask the user to sign in to YouTube Studio in the browser if needed. Aim for 10–15 tracks across funky / happy / bright / dramatic.
- **Multilingual speech** (if `languages` isn't English-only): offer to download `ggml-small.bin` (multilingual, ≈ 470 MB) into `~/.cache/hyperframes/whisper/models/` and note it in the config (`whisper_model`).
- **Drive:** if uploads are on, check `rclone listremotes`; if the remote is missing, tell the user to run `rclone config` (Google Drive, name = their `drive_remote`) — it opens a browser sign-in only they can do.

## 5. Smoke test
- `python3 -I $STUDIO/template/scripts/pipeline.py status` (no error) · `python3 -I $STUDIO/template/scripts/choose_style.py` on a 3-line sample · `npx --yes hyperframes@latest --version`.
- Print a summary: config path, studio folder, what's installed, what's still missing (music, Drive), and the next command: `make: <your first topic>`.
