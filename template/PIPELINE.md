# make-content — end-to-end pipeline (built 22 Oct 2026)

Goal: one command per topic (or per week) → script, carousel, LinkedIn post, edited reel, covers, all in one Drive folder, with filming + 2 approvals as the only interruptions. Built on the existing skills: `reel-script`, `generate-carousel`, `reel-edit`. This file is the spec to build from. Since 24 Oct 2026 every stage also follows `WINNING_PATTERNS.md` (learned from the creator's reference reels), `reel-edit` picks the style itself with `scripts/choose_style.py` + the enhance pass, and QA includes `qa_reel.py --cover` and the static-frame check.

## Pipeline as of 25 Oct 2026 (after four reference-reel studies + the first test edit)
```
LEARN (any time)   study: <links> → browser → MP4 + caption + stats → analyze_reference.py (transcript, WPM, cuts, loudness,
                   sheets) → NOTES.md → WINNING_PATTERNS.md round → rules pushed into each skill / QA script
HALF 1  make:      research (facts + trending claim for Fact-or-Hype) → script.md [format · look A–E · 95–120 words ≈ 200 WPM ·
                   credibility by 5 s · reactions + verdict · yes/no CTA + loop · edit brief] → shoot sheet (lighting from the look)
                   ∥ carousel (recipe-list / formats.md, SEO caption) ∥ LinkedIn → CHECKPOINT 1 → upload half 1
FILM               the creator films + AirDrops → `footage ready`      (or `edit: <video>` = edit-only mode, no Half 1)
HALF 2             footage → review (raw-vs-graded HDR check) → cut (pauses out, qa --audio: repeats, fillers, pace ≥ 190 WPM)
                   → face map → choose_style.py (10 treatments, rotation) → beat map + motion briefs → enhance pass (10 components + beat grid,
                   budget) → on-screen facts checked → pick_music.py (energetic track, trimmed to its drop) + 2–3 signature SFX
                   → build (helpers per beat) ∥ covers A/B ∥ posting kit (hook, list, trust line, yes/no, SEO keyword line, tags)
                   → QA auto-fix ×3 (lint, check, UI zones, qa_reel: enhance/static/read-time/face, --cover, beat_grid --check, frame grading ≥ 8/10, frame-0, taste:
                   music first 3 s · ending · ≤1 emoji) → draft + Studio preview → CHECKPOINT 2 → final render → −14 LUFS → SRT
                   → upload half 2 → style_log row
LOOP               the creator's notes → rule in the owning skill; 48 h numbers → follow-ups when ≥ 3× median
```
Scripts in `scripts/`: pipeline.py (manifest/locks/uploads) · analyze.sh · make_cut.py (`--exposure --saturation --no-grade`) · envelope.py ·
choose_style.py · pick_music.py · music_energy.py · beat_grid.py · qa_reel.py (`--audio`, `--cover`) · analyze_reference.py · render_cover.sh · finalize.sh · make_srt.js.
Components in `composition/components/` (INDEX.md). Music in `composition/assets/audio/music/` (INDEX.md: bpm, energy, best start).

## Commands
- `make R03` / `make: <topic>` → Half 1 now, Half 2 when footage arrives.
- `make week 1` → Half 1 for 7 topics in parallel; one combined review.
- `footage ready <reel_name>` → start Half 2 by hand (or the inbox watcher does it).
- `continue <reel_name>` / `status` → resume from the manifest / show every topic's stage.

## Shape: two halves around filming
```
HALF 1 (no footage)                                   HALF 2 (footage)
research ─► script ─┬─► carousel copy ─► render ─┐     transcribe ─► cut ─► verify cut
                    ├─► LinkedIn post + image ───┼─► CHECKPOINT 1 ─► upload carousel+LinkedIn
                    └─► shoot sheet (publish) ───┘           │
                                                  you film ──┘ drop file in inbox
face map + beat map ─┬─► graphic beats (helpers, ≤4 renders) ─┐
                     ├─► covers A/B ──────────────────────────┤
                     ├─► sound map + mix plan ────────────────┼─► assemble ─► QA ─► draft render ─► CHECKPOINT 2
                     └─► posting kit (+ trend search) ────────┘                                       │
final render ─► finalize (−14 LUFS) ∥ SRT ∥ final QA ─► upload all ─► log (style_log, calendar status)
```
Arrows = hard dependencies; branches after a `┬` run in parallel.

## Parallelism rules
| What | How | Limit |
|---|---|---|
| Topics in a batch (Half 1) | one helper agent per topic, model `sonnet`; main agent reviews | 4 topics at a time |
| Carousel / LinkedIn / shoot sheet | parallel branches after the script | — |
| Graphic beats (Half 2) | one helper per beat → `compositions/beat-N.html` | 4 concurrent |
| Covers, posting kit, sound map | parallel with graphic beats | — |
| Headless Chrome / HyperFrames renders (machine-wide) | lock files in `$STUDIO/.locks/render-{1..4}` | **4 max** |
| Final full-quality render | one at a time (`.locks/final`), batch renders queue overnight | 1 |
| Reels in a batch (Half 2) | sequential per reel (RAM/disk), their helpers parallel inside | 1 reel at a time |
Model split: planning, design calls, QA judgement and checkpoints on the main (strong) model; building graphics, captions, slides, copy variants on `sonnet` helpers. Drafts render at `--quality draft`; full quality only after approval.

## Manifest (robustness + resume) — `reels/<reel_name>/pipeline.json`
```json
{ "reel_name": "why_chatgpt_agrees", "playbook_id": "R03", "carousel_id": "C02",
  "stages": {
    "research":   {"status": "done", "outputs": ["script.md#facts"], "attempts": 1},
    "script":     {"status": "done", "outputs": ["script.md", "shoot_sheet.html"]},
    "carousel":   {"status": "done", "outputs": ["carousel/out/sheet.jpg"]},
    "linkedin":   {"status": "done", "outputs": ["linkedin_post.md", "linkedin_image.png"]},
    "checkpoint1":{"status": "approved", "by": "the creator", "at": "2026-10-23T10:12+05:30"},
    "upload1":    {"status": "done", "verified": true},
    "footage":    {"status": "waiting", "inbox_file": null},
    "edit":       {"status": "pending"}, "covers": {"status": "pending"},
    "checkpoint2":{"status": "pending"}, "final": {"status": "pending"}, "upload2": {"status": "pending"} },
  "drive": "{drive_remote}:{drive_folder}/why_chatgpt_agrees", "errors": [] }
```
- Status: `pending → running → done | failed | waiting | approved`. Every stage is **idempotent**: if its outputs exist and status is `done`, skip it.
- Failure: retry a stage twice (fresh helper), then mark `failed`, record the error, **keep the other branches running**, and report all failures in the next checkpoint message — never stop silently.
- Approvals are written into the manifest; **uploads refuse to run without the matching approval** (CHANNEL_RULES.md gates: Drive upload only after video + thumbnails approved).
- `continue <reel_name>` re-reads the manifest and resumes at the first stage that isn't done.

## Footage hand-off (inbox)
- Drop zone: `$STUDIO/inbox/` (AirDrop from iPhone). File name starts with the reel name or playbook ID (`R03.mov`, `why_chatgpt_agrees.mov`); otherwise match by most recent `footage: waiting` topic and ask once.
- Watcher (not enabled — the creator says "footage ready" after AirDrop; AirDrop lands in ~/Downloads, which `pipeline.py footage` searches): scheduled task every 30 min → for each new file, wait until its size is unchanged for 60 s (still copying), move it to `reels/<reel_name>/src.mp4`, set `footage: done`, start Half 2.
- Pre-flight before Half 2: free disk ≥ 20 GB, file ≥ 1080p, duration 20 s–8 min, audio present; else report and stop that reel only.

## Checkpoints (the only interruptions)
1. **Checkpoint 1** (after Half 1; one message per topic or one for the batch): shoot-sheet link, carousel contact sheet + cover, LinkedIn post text + image. Reply "ok" or numbered notes. → upload carousel + LinkedIn files immediately (so carousels can post on their own day).
2. **Checkpoint 2** (after Half 2): Studio preview + `review/review.html` draft, storyboard, hook A/B, covers A/B, posting kit, QA report. Reply "approved" or timestamped notes. → final render, finalize, upload.
In batch mode both checkpoints are one combined message (one section per topic), and notes can be addressed per topic ("R05: …").

## Drive layout (one new subfolder per topic, never into `{drive_folder}` itself)
```
{drive_folder}/<reel_name>/
  <reel_name>.mp4  <reel_name>_thumbnail.jpg  <reel_name>_thumbnail_b.jpg  <reel_name>.srt
  <reel_name>_posting_kit.md  <reel_name>_linkedin_post.md  <reel_name>_linkedin_image.png
  carousel/  slide-01…NN.jpg  <carousel>-linkedin.pdf  <carousel>_caption.md
```
Every upload ends with `rclone lsl` and a byte-size comparison against the local files; mismatch → re-upload that file once, then report.

## Cost & interruption guards
- Pre-stock the music library (10–15 YouTube Audio Library tracks across calm/curious/tense/warm/upbeat/cinematic) so Half 2 never stops to ask for a download.
- Helpers on `sonnet`; low-res drafts; reuse components (`composition/components/`) and b-roll (`broll/INDEX.md`) before building new ones.
- One fact-check pass per topic in Half 1 (shared by script, carousel and LinkedIn) — no duplicate research.
- Batch overnight: queue final renders after approval and let them run unattended.

## Build list (when credits allow)
1. `$PLUGIN/skills/make-content/SKILL.md` — commands, the two halves, manifest handling, checkpoints, uploads (calls the three skills; adds nothing they already do).
2. `template/scripts/pipeline.py` — manifest read/write, stage status, lock-file semaphore (`acquire/release`), inbox scan with size-stable check, Drive verify.
3. `inbox/` folder + optional scheduled task (watcher).
4. Small edits: `reel-script` / `generate-carousel` / `reel-edit` read and write `pipeline.json` when it exists.
5. Test: `make R03` (Half 1) → film → drop file → Half 2 → both checkpoints → Drive.
