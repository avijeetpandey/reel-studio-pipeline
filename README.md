# Reel Studio — an end-to-end short-form content pipeline for Claude Code

Turn **any topic** into a ready-to-post **Instagram Reel / YouTube Short** — plus a matching **carousel** and **LinkedIn post** — with Claude Code doing the writing, editing, motion graphics, music, captions, covers, QA and upload. You only do two things: **film** and **approve**.

```
you:     make: why ChatGPT agrees with everything
Claude:  research → script (3 hooks, timed beats) → shoot sheet on your phone → carousel → LinkedIn post   ← checkpoint 1
you:     film it, AirDrop it, say "footage ready"
Claude:  cut → style → beat map → motion graphics → captions → music + SFX → QA (auto-fix ×3) → covers A/B → posting kit
                                                                                               ← checkpoint 2 (Studio preview)
you:     "approved"
Claude:  final render (−14 LUFS) → SRT → upload everything to a new Drive folder → log
```

It also **learns** in two ways:
- **From reels and carousels you like** — `study: <links>` watches them (frames, transcript, speaking pace, music level, captions, covers, every carousel slide), writes the patterns down and updates its own rules.
- **From your own results** — `posted` → `stats:` reads Instagram Insights and YouTube Studio for every reel (48 h and 7 days) plus a channel snapshot of both; `report:` turns that into a monthly report and nudges the style picker toward what works for *your* audience.

Everything runs only when you ask: there are no scheduled or background jobs.

> Built and battle-tested by a creator running a daily AI/tech channel. Everything personal has been stripped — the first run interviews **you** and fills in your name, brand, audience, posting times, rules and Drive folder.

---

## Contents
- [What you get](#what-you-get)
- [Requirements](#requirements)
- [Install](#install)
- [First-run setup (the interview)](#first-run-setup)
- [Daily use](#daily-use) · full guide: [docs/USAGE.md](docs/USAGE.md)
- [How the pipeline works](#how-the-pipeline-works) · deep dive: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [Customising](docs/CUSTOMIZE.md) · [Music](docs/MUSIC.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Updating](#updating) · [What's not included](#whats-not-included) · [Licence](#licence)

---

## What you get
| Skill | Say | Does |
|---|---|---|
| `studio-setup` | "set up reel studio" | First-run interview → config + your channel rules, installs the template, checks dependencies, SFX, music library |
| `make-content` | `make: <topic>` · `make: a; b; c` · `footage ready` · `edit: <video>` · `study: <links>` · `posted <reel> <ig> <yt>` · `stats:` · `report:` · `trends:` · `continue <reel>` · `pipeline status` | The orchestrator: runs everything below in parallel with helper agents, tracks every stage in a resumable manifest, stops only for filming and the two approvals |
| `reel-script` | "script a reel about …" | Format pick (10 formats incl. **Fact or Hype?**, identity reframe, mantra, skit, experiment, myth-or-fact…), 3 hooks, timed 25–35 s script (≈ 200 WPM), edit brief, b-roll list, covers, LinkedIn post + image, a **shoot sheet** artifact for your phone (framing, lighting for the chosen look, checklist) |
| `reel-edit` | "edit this reel" | Senior-editor workflow on HyperFrames: review → tight cut → face map → **automatic style** (10 treatments, rotated) → beat map → motion components → captions → **automatic energetic music** + signature SFX → QA auto-fix loop → Studio preview → final render → A/B covers → posting kit → Drive |
| `generate-carousel` | "make a carousel about …" | 1080×1350 "engineer's notebook" slides (plus photo, roadmap, ✗/✓ and finding layouts), recipe-list and roadmap formats, QA, caption with SEO keyword line, alt text, LinkedIn PDF |

Plus: 24 seek-safe motion components (round 7 adds kinetic-type-3d, sound-strip, sfx-chip, select-caption, stamp-slap, loading-hook, dm-toast, stopwatch, ab-header and the sticker-kit illustration set; roll-text, pop-blur, swing-window, code-window, step-progress, list-header, check-card, pill-list, tier-board, split-frame, flash-open, count-roll, hand-annotate, cta-card), a beat grid that snaps graphic entrances to the music, a music energy analyser + automatic picker/trimmer, a reference-reel analyser, a QA script (read time, static stretches, face box, component budget, pace, blank covers), cover/carousel/LinkedIn templates, a timestamped review player, and `WINNING_PATTERNS.md` — the distilled lessons from ~94 reference reels and 10 carousels (seven study rounds).

## Requirements
- **Claude Code** (CLI or desktop app) with a plan that allows long sessions. The desktop app adds the built-in browser (used for Studio previews, YouTube Audio Library and `study:`).
- **macOS** recommended (tested). Linux works if you install the same tools; Windows via WSL is untested.
- **Tools** (`scripts/setup.sh` checks and installs them with Homebrew): `ffmpeg` (with lut3d), `node ≥ 18`, `python3`, `whisper-cpp` + the `small.en` model, Google Chrome (headless renders), `rclone` (Drive uploads, optional), `yt-dlp` (optional).
- **HyperFrames plugin for Claude Code** (the video engine and its skills): `/plugin marketplace add heygen-com/hyperframes` then `/plugin install hyperframes`.
- ~25 GB free disk while editing.

## Install
In Claude Code:
```
/plugin marketplace add avijeetpandey/reel-studio-pipeline
```
```
/plugin install reel-studio
```
(Or clone the repo and run `/plugin marketplace add /path/to/reel-studio-pipeline`.)

Then in a terminal, check the tools:
```bash
bash ~/.claude/plugins/marketplaces/reel-studio/scripts/setup.sh --install
```
(The exact plugin path is shown by `/plugin`; setup also runs this for you.)

## First-run setup
Start a Claude Code session and say:
```
set up reel studio
```
Claude interviews you (≈ 20 questions, grouped): **name, brand, handle, role/credibility line, follow-card promise, accent colour, avatar, anything confidential, niche, audience + language, topics to prefer/avoid, series names, reel length, CTA style, timezone + posting slots, music rule, approval gates, Drive remote + folder, studio folder**. Defaults come from the author's analytics; keep or change each one.

It then writes:
- `~/.config/reel-studio/config.json` — your answers (every script and skill reads it)
- `<studio>/CHANNEL_RULES.md` — your channel rules in plain English (edit any time)
- `<studio>/template/` — the pipeline's template, branded with your name/handle
- `<studio>/reels/`, `carousels/`, `research/`, `inbox/`, `reels/style_log.md`

…checks dependencies, generates an original licence-free SFX pack, and walks you through building your music library (sign in to YouTube Studio in the browser when asked). Re-run "studio setup" any time to change answers.

## Daily use
```
make: 3 ChatGPT settings nobody uses
```
1. Claude researches, writes `script.md`, publishes a **shoot sheet** (open it on your phone while filming), builds the carousel and LinkedIn post → **checkpoint 1** (reply "approved" or give notes).
2. You film (one take is fine — retakes and pauses are cut), AirDrop to `~/Downloads`, say `footage ready`.
3. Claude edits on autopilot → **checkpoint 2**: Studio preview link, draft video, storyboard, covers A/B, posting kit, QA report, the style it chose and why. Reply "approved" or timestamped notes ("0:12 move the card up").
4. Final render, SRT, upload to `Drive/<folder>/<reel_name>/`, posting times.

Other commands: `edit: ~/Downloads/clip.mov make it fun, keep the length` (no script) · `study: <reel links>` (learn from reels you like) · `make: a; b; c` (batch) · `continue <reel>` · `pipeline status`.

After posting: `posted <reel> <instagram link> <youtube link>` → `stats: all` (48 h / 7 d, both platforms + channel) → `report:` (monthly; the style picker learns from it) · `trends:` (3 fresh topic ideas when you want them). See [docs/USAGE.md §8–9](docs/USAGE.md). Every note you give becomes a permanent rule. Full walkthrough: **[docs/USAGE.md](docs/USAGE.md)**.

## How the pipeline works
```
LEARN    study: <links> → frames + transcript + pace + music level + captions → WINNING_PATTERNS.md → rules in every skill
HALF 1   research → script.md (format · look A–E · 95–120 words · proof by 5 s · reactions + verdict · yes/no CTA + loop)
         → shoot sheet ∥ carousel ∥ LinkedIn → CHECKPOINT 1 → upload
FILM     you → footage ready   (or edit: <video>)
HALF 2   review (HDR check) → cut (pace ≥ 190 WPM) → face map → choose_style.py (10 looks, rotation) → beat map → enhance pass
         (11 components, budget, beat grid) → facts checked → pick_music.py (energetic, trimmed) + SFX → build ∥ covers ∥ posting kit
         → QA auto-fix ×3 (incl. ends on the last word, frame grading ≥ 8/10) → draft + Studio preview → CHECKPOINT 2 → final → −14 LUFS → SRT → upload → style_log
LOOP     your notes → rules · posted → stats: (Instagram + YouTube) → report: → performance.json → style picker · trends: → ideas
         (all on demand — nothing is scheduled)
```
Details, file layout, every script and every QA check: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

## Updating
`/plugin update reel-studio`, then say "studio setup" → it refreshes `<studio>/template/` (your reels, logs, music and edits to `CHANNEL_RULES.md` are kept).

## What's not included
- **No music files** — YouTube Audio Library tracks are free to use in videos but not to redistribute. Setup builds *your* library from the Audio Library (attribution-free only) with the included scorer.
- **No personal media** (avatars, photos, footage) and no reference-reel downloads. Bring your own avatar; `study:` downloads reels only for analysis and deletes them.
- Posting itself is manual (the posting kit tells you exactly what to paste where and when).

## Licence
MIT — see [LICENSE](LICENSE). HyperFrames, Claude Code, YouTube Audio Library tracks and fonts keep their own licences.
