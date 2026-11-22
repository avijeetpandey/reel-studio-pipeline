---
name: make-content
description: End-to-end {brand} pipeline. The creator PASTES THE SCRIPT (the pipeline never writes one) — it then makes the paired carousel + LinkedIn post from their words, and when the footage arrives it edits the reel completely automatically (auto-director picks the look, grade, captions, camera moves, transitions, SFX and music; compose builds the HyperFrames composition), plus A/B thumbnails + posting kit, all uploaded to one Drive folder. Tracks every stage in a resumable manifest, stops only for filming and the two approvals. Use when the creator says "make: <pasted script>", "edit: <video> + script", "footage ready", "study: <reel links>", "continue <reel>", "pipeline status", "posted <reel> …", "stats: …", "report: …" or "trends:".
---

# make-content (orchestrator)

> **Setup first.** These values come from `~/.config/reel-studio/config.json` (written by the `studio-setup` skill — run it if the file is missing):
> `$STUDIO` = `studio_dir` (your working folder: `template/`, `reels/`, `carousels/`, `research/`) · `$PLUGIN` = `plugin_root` (this plugin) ·
> `{brand}`, `{handle}`, `{creator_name}`, `{drive_remote}`, `{drive_folder}` = the matching config keys. Channel rules, approval gates,
> posting slots and timezone live in `$STUDIO/CHANNEL_RULES.md` — they override any default numbers written below.

This skill only orchestrates. **Since 14 Nov 2026 the pipeline does not write scripts: the creator's pasted script is the input and is never rewritten.** The work follows `reel-edit` (+ its `humanize.md`: the automatic edit) and `generate-carousel` — read them before running a stage and never re-implement their rules. `reel-script` is no longer a stage (its LinkedIn section 6 is still used for the post). Spec: `$STUDIO/template/PIPELINE.md`. Channel rules + approval gates: `$STUDIO/CHANNEL_RULES.md`. Learned patterns from the creator's reference reels (hooks, layouts, CTA cards, covers, captions): `$STUDIO/template/WINNING_PATTERNS.md` — every stage reads it.
`P = python3 -I $STUDIO/template/scripts/pipeline.py` (manifest, render locks, footage pickup, gated uploads).
**The creator's script is the input** (pasted into chat; never rewritten). The playbook (`$STUDIO/{handle}-content-plan.html`: R01–R30 reels, C01–C30 carousels) is optional context for choosing a carousel format only.

## Commands
| The creator says | Do |
|---|---|
| `make: <pasted script>` (a reel name on the first line, or derived from the hook) | Half 1 from the creator's script: carousel + LinkedIn (their words), checkpoint 1, upload 1 — **add `reel only` to skip carousel/LinkedIn** |
| `make: <script 1> --- <script 2>` | Half 1 for several scripts in parallel, one combined checkpoint |
| `footage ready` / `footage ready <reel>` | Half 2: **automatic edit** (if no name: the reel with `footage: waiting`, oldest first) |
| `edit: <video> + <pasted script>` (the usual case now: footage and script together) | **Edit-only mode** below — straight to Half 2 |
| `edit: <video>` (no script) | same; the transcript becomes `script.md` |
| `study: <links>` (reference reels the creator likes) | **Learning mode** below |
| `cartoon: <topic>` / `make cartoon: <topic>` + a voiceover file | **hand off to the `make-cartoon-content` skill** (script → storyboard → open-source render → covers → kit → Drive). Needs no filming. |
| `continue <reel>` | `P status <reel>` → resume at `P next <reel>` |
| `pipeline status` | `P status` → one line per topic |
| `posted <reel> <instagram url> <youtube url>` | `P posted <reel> --ig <url> --yt <url>` (both platforms; ask for whichever link is missing) |
| `stats: <reel>` / `stats: all` | **Stats mode** below: read Instagram Insights + YouTube Studio for that reel (or every reel `P due` lists) + a channel snapshot of both |
| `report:` / `report: 2026-11` | **Report mode** below: `channel_report.py` → monthly report + `performance.json` |
| `trends:` | **Trends mode** below: 3 topic suggestions from this week's AI / career trends |

**On demand only.** `stats:`, `report:` and `trends:` run ONLY when the creator types them. Never create a scheduled task, cron, loop or background job for them, and never start one on your own: they cost tokens and need the creator's signed-in browser. `P due` only *lists* what is due; it runs nothing.

## Setup per script
- **The script is the input.** Save the creator's pasted text verbatim as `reels/<reel_name>/script.md` (spoken lines only matter; keep any notes they wrote). Never edit, shorten or "improve" it. `script_lint.py` may be run for advice (never blocking) and its advice goes into the checkpoint as a one-line note at most.
- `reel_name` = snake_case of the hook / title they give. `P init <reel_name> --script script.md [--topic "<one line>"]` (this marks the script stage done: "provided by the creator"; there is no research or script-writing stage any more). Work in `$STUDIO/reels/<reel_name>/` (move the session there with change_directory); the carousel lives in `reels/<reel_name>/carousel/`.
- Check `reels/` + `style_log.md` for a repeat; if the script repeats a reel already made, say so at the checkpoint (no change to their words).
- Update the manifest at every stage: `P set <reel> <stage> running` → do it → `P set <reel> <stage> done` (or `failed --note "<error>"`). Record deliverables with `P file <reel> <key> <path>`. Skip any stage already `done` (idempotent resume).

## Half 1 — from the creator's script, no footage needed (no questions)
1. **carousel + linkedin in parallel** (skip both on `reel only`):
   - **carousel** → helper agent (`model: "sonnet"`): "Follow $PLUGIN/skills/generate-carousel/SKILL.md steps 1–7 for <reel> (format chosen from `generate-carousel/formats.md` to fit the script) in <reel>/carousel/, using <reel>/script.md (the creator's own words — do not rewrite their claims). Pipeline mode: do NOT show a checkpoint and do NOT upload; stop after caption.md and report the QA result and the contact-sheet path." Then `P file <reel> carousel_dir <reel>/carousel`.
   - **linkedin** → helper agent (`model: "sonnet"`): "Follow $PLUGIN/skills/reel-script/SKILL.md section 6 for <reel>/script.md; write linkedin_post.md and render linkedin_image.png; report paths." Then `P file` for `linkedin_post` and `linkedin_image`.
2. **checkpoint1** — one message: carousel contact sheet + cover, LinkedIn post text + image, any failed stage, and the ONE-line world/grade the auto-director would pick for this script (`autodirect.py world --script`). The creator replies "ok"/notes. On approval: `P approve <reel> checkpoint1`. (No shoot card is made: he films from his own script.)
3. **upload1**: `P upload <reel> half1`. `footage` stays `waiting`.
4. Tell the creator: "Film <reel> (4K, HDR off), AirDrop the original from Photos, then say `footage ready`."
Several scripts: up to 4 helpers in parallel (carousel/LinkedIn per script), one combined checkpoint 1.

## Half 2 — after "footage ready"
1. **footage**: `P footage <reel>` — finds the newest video in `~/Downloads` (AirDrop) or `inbox/` since the topic started, prefers a file named after the reel/ID, waits until it has stopped copying, checks ≥ 1080p / 15 s–8 min / audio / 20 GB free, copies it to `reels/<reel>/src.<ext>` (the original stays in Downloads). Exit 2 = several candidates → ask the creator once which one (`--file`). Exit 3 = pre-flight failed → report and stop this reel only.
2. **cut → plan (automatic)** — `reel-edit/humanize.md` steps 2–3: review (raw-vs-graded HDR check, `footage_check.py`) → `autodirect.py world` (grade from the script) → cut with `make_cut.py … --look <grade>` + `qa_reel.py --audio` (repeats, fillers, pauses > 0.25 s, pace, tail ≤ 0.5 s) → **`person_matte.py` (cut-out `fg.webm` for the depth layer, Round 14)** → `autodirect.py plan` (set `HEADLINE="kick|word"` from the hook: it becomes the word behind the head; transcript → read + fix words in `work/words_cut.json` → plan again) → plan lives in `edit_plan.json` + `EDIT_PLAN.md`. The creator is never asked for style.
3. Then in **parallel**:
   - **build**: `compose.py` (humanize.md step 4) + carve; Sticker Pop graphics only where the script needs a drawing (step 5), one helper per graphic beat, every HyperFrames render/snapshot through `P locked render -- <command>` (max 4 at once).
   - **covers**: helper (`model: "sonnet"`): `reel-edit` step 8 (A + B). Cover rules (`reel-edit` §8 round 8): neutral still face (closed mouth, no teeth), whole head, bright, logos on the cover for tool topics, show alternatives as `_v2`, never overwrite or upload a cover the creator has not approved. Then `P file <reel> cover_a|cover_b <path>`.
   - **posting_kit**: helper (`model: "sonnet"`): `reel-edit` step 9 from `posting-kit-template.md` (trend search; caption = hook line → list as text → trust line → yes/no question → SEO keyword line → 3–5 specific tags; YouTube title, tags, schedule) → `P file <reel> posting_kit <path>`.
4. **qa**: `reel-edit` step 6 + `humanize.md` step 6 — auto-fix loop up to 3 rounds: `hyperframes lint` + `check --snapshots` + both UI-zone checks, a snapshot of every transition (read the frames), `qa_reel.py` (static stretches, read time, face box), `qa_reel.py --cover` on covers A + B, `mix_check.py` (voice 10–14 dB over music + SFX), **frame grading** (every 1 s frame ≥ 8/10), AI-slop tells, frame-0 gate, the "feels human" checklist, draft render via `P locked render -- npx hyperframes render … --quality draft`, Studio preview started for checkpoint 2.
5. **checkpoint2**: `reel-edit`'s checkpoint message (Studio preview + review.html draft, storyboard, hook A/B, covers A/B, posting kit, QA report). Approval → `P approve <reel> checkpoint2`. Notes → `reel-edit` step 11 (fix + rule update) → show again.
6. **final**: `P locked final -- npx hyperframes render -o renders/raw.mp4 -f 30 -q delivery -w 2` → finalize → SRT → re-check frame 0 + `qa_reel.py --audio` → `P file <reel> video <final.mp4>` and `srt`.
7. **upload2**: `P upload <reel> half2` (video, both thumbnails, SRT, posting kit — size-verified). Then log the reel in `reels/style_log.md`, record its features (`P features …`, reel-edit step 7), mark it posted-ready, and reply with the Drive folder + posting times + "after posting, tell me `posted <reel> <instagram link> <youtube link>`".
Several reels with footage: run Half 2 one reel at a time (helpers parallel inside each); queue their final renders under `P locked final`.

## Edit-only mode (`edit: <video>` — footage without a script)
1. `P init <reel> --topic "<the creator's one-line description>" [--script script.md]` → `P footage <reel> --file <video>` → mark carousel/linkedin/checkpoint1/upload1 `done --note "edit-only"`.
2. Run Half 2 from step 2 (automatic edit). The pasted script is saved as `script.md` (verbatim); without one the transcript becomes `script.md`. The creator's notes ("keep the length", "make it moody") override the auto-director's defaults and the channel length rules — say so at the checkpoint (a note like "moody" = pass `--world warm_cinema`).
3. Skip carousel/LinkedIn unless the creator asks. Test reels the creator won't post: never upload, mark `checkpoint2 failed --note "test"`, still turn their notes into rules.

## Learning mode (`study: <links>` — learn from reels the creator likes)
1. **Download with yt-dlp** (works without a login for public reels; the creator asked for it on 14 Nov 2026): `mkdir research/refs_<date>/src && yt-dlp -a urls.txt -o 'src/%(id)s.%(ext)s' --write-info-json --write-thumbnail --convert-thumbnails jpg -f 'bv*+ba/b' --merge-output-format mp4 --ignore-errors --sleep-interval 1`. The `.info.json` carries caption, hashtags, likes, comment count and ~12 top comments. A link that returns "empty media response" is private/removed: list it as failed. If yt-dlp ever needs cookies, ask the creator first (never export browser cookies on your own). Carousels: image slides are skipped (use the browser route in the older notes only if the slides matter).
2. **Analyse:** `$STUDIO/tools/.venv/bin/python template/scripts/analyze_ref2.py research/refs_<date> --workers 4` (cuts, flashes, whips, punches, shake, grade, skin share, whisper transcript, LUFS, bed, tempo, caption stats; `view.jpg` = 8 hook frames + 24 overview frames; `events.jpg` = 6 frames around each transition; `audio.png` = spectrogram) then `$STUDIO/tools/.venv/bin/python template/scripts/audio_events.py <mp4> --json analysis/<id>/sfx.json` for sound-design events under dense speech. ≈ 1–1.5 min per reel at 4 workers. Read `view.jpg` of every reel that matters (weight by proven performance; posts a few hours old prove nothing yet) and `events.jpg` for every new transition style.
3. Write `research/refs_<date>/REPORT.md` (headline numbers table, technique → seen in → where it now lives), append a round to `template/WINNING_PATTERNS.md`, then push each rule into the owner: `template/auto/autodirect.py` + `worlds.json` + `fx.js` (effects), `make_look.py` (grade), `reel-edit/humanize.md`, qa/posting kit.
4. Delete the downloaded videos when done; keep notes, transcripts, sheets and metrics. Report what changed in each stage.

## Stats mode (`stats: <reel>` / `stats: all` — Instagram + YouTube Shorts)
1. Which reels: `P due` (posted reels whose 48 h / 7 d numbers aren't recorded yet), or the one the creator named. A reel without `posts` → ask the creator for both links (`posted`). Same content goes to both platforms, so always do both.
2. **YouTube Studio** (built-in browser, signed in; if it shows a sign-in page, stop and ask the creator): open `https://studio.youtube.com/video/<id>/analytics/tab-overview/period-default` (the id is in the Shorts URL; Studio → Content → Shorts lists them) and the Engagement + Audience tabs; the numbers render late, so wait ~5 s, then read with `get_page_text` / a screenshot. **Studio often shows a "Verify that it's you" dialog on analytics pages: that is a sign-in step — never click through it; stop and ask the creator to complete it in the browser pane, then continue.** The channel dashboard (`studio.youtube.com`) shows latest-Short views, average % viewed and 28-day totals without that step. Record `views`, `stayed_pct` (Shorts: "stayed to watch"), `avg_viewed_pct`, `avg_view_s`, `likes`, `comments`, `shares`, `subs_gained`, plus `impressions`/`ctr` when shown and `shorts_feed_pct` (traffic source). Window: 48 h or 7 d after posting (use Studio's date range; say which).
3. **Instagram** (built-in browser, signed in): the reel page itself has no insights on the web (only likes/comments). Use the professional dashboard: account level at `https://www.instagram.com/accounts/insights/?timeframe=30` (views, viewers, follower vs non-follower %, interactions, accounts engaged, profile visits, follower change; `timeframe=7` for 7 days) and per reel at `https://www.instagram.com/accounts/insights/content/?media_type=all&metric=views&sort_by=highest&timeframe=30&view_type=card` (cards load slowly — wait, scroll, then open the reel's card for its detail). Record `views` (plays), `reach`, `likes`, `comments`, `shares`, `saves`, `avg_view_s`, `follows`, and `skip_rate` / `non_follower_pct` if shown. If the web doesn't show a field, record it as `na`, never estimate; if it shows nothing, ask the creator for screenshots of the app's Insights screen and read the numbers from them.
4. Save each: `P stats <reel> yt --window 48h views=… stayed_pct=… …` and `P stats <reel> ig --window 48h …` (prints the target verdict and appends `reels/stats_log.md`).
5. **Channel snapshot (both)**: YouTube Studio → Analytics (last 7 + 28 days): `subscribers`, `subs_7d`, `views_7d`, `views_28d`, `watch_h_28d`, top 5 Shorts, traffic sources (`shorts_feed_pct`, `search_pct`, `channel_pct`), `india_pct`, `returning_pct`. Instagram → professional dashboard / Insights (last 7 + 30 days): `followers`, `followers_7d`, `reach_7d`, `reach_30d`, `engaged_30d`, top 5 reels, `india_pct`, `non_follower_reach_pct`. Save with `P channel yt …` / `P channel ig …`.
6. Reply: a 2-platform table per reel (target verdicts), channel growth since the last snapshot, and anything that beat the median 3× (→ suggest 2–3 follow-ups, CHANNEL_RULES.md).

## Report mode (`report:` / `report: <YYYY-MM>` / `report: all`)
1. `python3 -I $STUDIO/template/scripts/channel_report.py --month <YYYY-MM>` → `reports/<month>.md` + `reels/performance.json` (per-feature scores, only groups with ≥ 3 reels).
2. Needs `features` on each reel (written in reel-edit step 7; for older reels fill them from `script.md` + `style_plan.json` with `P features <reel> format=… hook_shape=… treatment=… length_s=… wpm=… series=… cta=…`).
3. Reply with the headline findings: medians per platform, the winning and losing format / hook shape / treatment / length, where Instagram and YouTube disagree (→ platform-specific title / cover / caption next time), post-time notes (suggestions only — the CHANNEL_RULES.md slots stay until the creator changes them), follow-up topics for 3× winners.
4. From then on `choose_style.py` reads `performance.json` automatically (a capped nudge, rotation still wins) and the report informs the auto-director's weights (`template/auto/worlds.json`: which world / transition mix wins on each platform) — change a weight only after ≥ 3 reels per group.

## Trends mode (`trends:` — only when asked)
1. 6–10 web searches (mode "extended" for freshness) for the last 7 days: AI launches and viral AI claims, AI + jobs/careers news for your audience's country (layoffs, hiring, salaries, new roles), what tech-career creators are posting this week; optionally browse Instagram Explore / YouTube Shorts search for 2–3 terms in the signed-in browser (read only).
2. Filter: broad AI curiosity / career > dev-only (CHANNEL_RULES.md); skip anything already made (`reels/` folders, `style_log.md`) or older than 14 days; check each claim against a primary source.
3. Write `research/trends/<YYYY-MM-DD>.md` (suggestions for the creator's OWN scripts — the pipeline never writes the script): **3 topic suggestions**, each with the trend + source links + date, the viewer's-problem framing, 3 hooks in proven shapes (WINNING_PATTERNS §1, §11, §16, §22, §27), the best format (reel-script table), series fit (Fact or Hype? / How does X work? / Day N), and the paired carousel format; plus a short "skipped and why" list.
4. Reply with the 3 suggestions; the creator starts one with `make: <topic>`. Never start `make:` from trends by yourself, never schedule this.

## Music + SFX libraries (never an interruption)
- **Allowed sources (the creator, 14 Nov 2026):** YouTube Audio Library ("Attribution not required") and any other free-licence, no-attribution source (Mixkit is in; Pixabay-style sites qualify if their licence says no attribution and commercial use is fine — record the licence line). Never Instagram's in-app music (not licensed outside the app), never ripped tracks.
- `template/scripts/fetch_free_audio.py sfx|music [--per N] [--only cat,cat]` grows the libraries from Mixkit and logs each file with its licence; `template/auto/music_index.py` (venv) analyses every track (BPM, beat grid, energy, intro, best bar-aligned starts, moods) into `music/INDEX.json`; `template/auto/sfx_roles.py` re-files all sounds by role into `sfx/ROLES.json`. `pick_music2.py` does the per-reel choice + trim (energetic from second 1, never the last 3 reels' tracks). If nothing unused fits a mood, fetch more — no asking.
- YouTube Audio Library route (signed-in browser) still works for more tracks: list through the page's `creator_music/list_tracks`, score with `music_energy.py`, add rows to `music/INDEX.md`, then re-run `music_index.py`.

## Learning loop (every reel)
- Every note the creator gives → fix + "which rule would have prevented this?" → write it into the owning skill/QA script → tell the creator (reel-edit step 11). Durable preferences also go to memory.
- After posting: the creator says `posted <reel> <ig> <yt>`; when they ask `stats:` (48 h / 7 d), record both platforms; a reel ≥ 3× the channel median → suggest 2–3 follow-ups on that topic (CHANNEL_RULES.md). `report:` monthly (when they ask) turns the numbers into `performance.json` for the style picker.

## Robustness rules
- A failed stage: retry it twice (fresh helper), then `P set … failed --note`, **keep the other branches going**, and list the failure in the next checkpoint. Never stop silently, never hide a failure.
- Helpers report back paths + QA results; the main agent verifies their output (opens the contact sheet / files) before marking the stage done.
- `P upload` refuses without the matching approval in the manifest and verifies every file's size on Drive — never upload any other way in pipeline mode.
- If the session ends, `continue <reel>` picks up from the manifest; nothing is redone.
- Interruptions allowed: filming, checkpoint 1, checkpoint 2, a footage choice when ambiguous, and sign-ins. Music is never an interruption: if the index has nothing unused for the mood, fetch another free-licence, no-attribution track without asking.
