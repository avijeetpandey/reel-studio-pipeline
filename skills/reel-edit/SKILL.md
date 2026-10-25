---
name: reel-edit
description: Edit the creator's (@{handle}) raw talking-head footage into a finished Instagram Reel + YouTube Short with HyperFrames, in stages like a senior editor — review, tight cut, face map, a treatment chosen per reel (6 looks, rotated so no two reels look alike), beat map (scene type per line, one graphic per idea, real visuals), director-style motion briefs, sound map, automated self-check, review gate, render, A/B covers, posting kit + LinkedIn post, Drive upload after approval. Frame 0 = their face already speaking the hook, never a title card; 25–35 s; yes/no CTA; loop ending. Runs on autopilot with a single approval checkpoint. Use whenever the creator hands over a video / raw footage to edit, or asks to re-edit or revise a reel.
---

# Reel edit ({brand})

> **Setup first.** These values come from `~/.config/reel-studio/config.json` (written by the `studio-setup` skill — run it if the file is missing):
> `$STUDIO` = `studio_dir` (your working folder: `template/`, `reels/`, `carousels/`, `research/`) · `$PLUGIN` = `plugin_root` (this plugin) ·
> `{brand}`, `{handle}`, `{creator_name}`, `{drive_remote}`, `{drive_folder}` = the matching config keys. Channel rules, approval gates,
> posting slots and timezone live in `$STUDIO/CHANNEL_RULES.md` — they override any default numbers written below.

Follow every step, in order. The channel rules in `$STUDIO/CHANNEL_RULES.md` (growth rules, approval gates) apply on top.
`T = $STUDIO/template/` holds the reusable code: `scripts/` (**choose_style.py**, analyze.sh, envelope.py, make_cut.py, make_lut.py, finalize.sh, render_cover.sh, make_srt.js, sample_frames.sh, safe_zone.sh, **qa_reel.py**), `composition/reference-index.html` (code patterns: hook words, captions, cards, CTA, progress bar, screen card), `composition/assets/audio/sfx/` + `music/INDEX.md`, `review/review.html` (timestamped-notes player), `thumbnail/cover-template.html` (A) + `cover-template-b.html` (B), `posting-kit-template.md`.
**Read before building:** `$STUDIO/template/WINNING_PATTERNS.md` (what the reference reels the creator picked do — hooks, layouts, captions, CTA cards, covers), `treatments.md` (6 looks + brand constants), `planning.md` (beat map), `motion.md` (motion briefs, design, captions, camera, b-roll), `enhance.md` (content-driven motion upgrades + vetting), `sound.md` (sound map), `qa.md` (self-check) — all in this skill folder.
Work in `$STUDIO/reels/<reel_name>/` (snake_case; move the session there with change_directory), never a temp folder. Ask the creator whenever a sign-in is needed.

**Engine: HyperFrames** (HTML + GSAP, seek-driven, deterministic; local transcription, background removal, Studio preview, `check` audits). Compared with Remotion in Oct 2026: same headless-Chrome + FFmpeg core, but HyperFrames fits talking-head + overlays better (transparent cutouts, text-behind-subject, faster local renders, 20+ agent skills, Apache 2.0) and the whole pipeline already runs on it. Use these skills as needed: `hyperframes` (front door), `hyperframes-core`, `hyperframes-animation`, `hyperframes-keyframes` (camera moves), `hyperframes-registry` (search ~400 blocks before hand-building), `hyperframes-audio` (mix, carve, reverb), `hyperframes:embedded-captions` (text behind the subject), `media-use` (bundled SFX), `hyperframes-cli`. If a specific Remotion technique is ever needed, port it with `remotion-to-hyperframes`.

**Pipeline mode:** if `pipeline.json` exists in the reel folder, `make-content` is orchestrating. Then: update stages with `P set` (`P = python3 -I $STUDIO/template/scripts/pipeline.py`); run every HyperFrames render/snapshot through `P locked render -- …` and the final render through `P locked final -- …`; record deliverables with `P file <reel> video|cover_a|cover_b|srt|posting_kit <path>`; on approval run `P approve <reel> checkpoint2`; upload only with `P upload <reel> half2` (replaces step 10's rclone commands — same Drive folder, verified sizes). The source clip is `src.<ext>` placed by `P footage`.

## Autopilot (default)
When the creator hands over a video (with or without notes), run the whole pipeline end to end and stop only at ONE checkpoint. Don't ask questions along the way; take the default for every decision and list the choices at the checkpoint.
- If `script.md` (from `reel-script`) exists, it is the plan: its beats, on-screen text, visuals, highlight term and any **edit brief** (treatment, scene types, music mood) win over defaults.
- Defaults: drop dead air, fillers, false starts and repeated lines; move a buried claim to the front; keep all other content. If the cut runs over 40 s, build the full version anyway and offer a ready shorter variant at the checkpoint.
- Music: **automatic** — `python3 -I T/scripts/pick_music.py --len <reel s> --mood <edit-brief mood> --out videos/<name>/assets/audio/bgm.mp3` picks the most energetic approved track not used in the last 3 reels and trims it to its best start point (energetic from second 1). Library = YouTube Audio Library "Attribution not required" only (`INDEX.md`); to grow it, list candidates in YouTube Studio's Audio Library (signed-in browser), score them with `T/scripts/music_energy.py`, keep energy ≥ 72. If nothing fits, download a fitting "Attribution not required" track from the YouTube Audio Library yourself (no asking — the creator's standing OK) and add it to INDEX.md. Never ship a reel without music, never use music from anywhere else.
- Screen recordings: use any in `broll/`; if `script.md` lists missing ones, use a real captured page and mention it.
- **The checkpoint** (one message): Studio preview link + `review/review.html` with the draft, safe-zone contact sheet, storyboard (one frame per beat), hook A/B, covers A + B, posting kit (+ LinkedIn post), QA report, review notes (footage issues for next shoot), and the choices made (treatment, signature move, music). the creator replies "approved" or timestamped notes → final render at full quality, finalize to −14 LUFS, upload to Drive. Approval of the checkpoint = approval of video and covers; any change = fix, re-check, show the changed parts, ask again.

**Hard rules:** HyperFrames + ffmpeg only. Never spend money or use paid APIs without the creator's OK. Never use ripped footage/music. Music only from the YouTube Audio Library ("Attribution not required"); every reel gets music, which Claude downloads without asking. Never render the final before the creator approves the preview; never upload before they approves BOTH video and covers.

## Edit principles
- **Frame 0 = the creator's face, already speaking the hook.** Face on screen, undimmed, from the very first frame; first word audible within 0.1 s. Never open on a title card, cover, logo, dark frame, screen recording or b-roll — covers are uploaded separately (Oct 2026 audit: 4 of 7 reels opened on a dark card and stalled at 79–184 views).
- **Cut hard:** the first frame is the claim — no intro, no lead-in. Every pause > 0.3 s, filler, throat-clear and retake goes. Target **≥ 190 WPM** after the cut (the proven reference reels run 167–246; `qa_reel.py --audio` reports it).
- **Plan before building:** beat map first (`planning.md`). One graphic per idea, each held long enough to read; breathers between graphics; real visuals for anything named.
- **Different every time, recognisable always:** brand constants never change; the treatment changes per reel (`treatments.md`, rotation via `reels/style_log.md`). One signature move per reel.
- **Restraint:** fewer effects, smaller elements (~25% smaller than instinct), muted colours with one accent, nothing that doesn't help someone understand or keep watching. No glitch, shake or whoosh transitions on footage.
- **Voice first; silent test:** voice clear on top; muted, captions + on-screen text alone tell the story.
- **Finish strong — end ON the last word:** the CTA card appears while the yes/no question is being spoken, and the video ends ≤ 0.5 s after its last word. No frozen hold, no outro, no music tail; the loop restarts straight into the hook (round 3: 13/19 proven reels end ≤ 0.4 s after the last word; `qa_reel.py --audio` checks the tail).
- **The ending must be the cleanest, best-looking moment of the reel** (the creator, 24 Oct 2026: the test reel's ending was "the worst aesthetic" — a grey dim over busy footage with three stacked overlays). End on the best face shot or a clean full-bleed graphic; put the CTA on a calm background (blur + darken the footage behind the card, or a solid treatment-colour plate); max one card + the question; nothing half-faded; no messy screen footage behind text. Snapshot the last 4 s at full size and judge it like a cover.
- **Result first** (round 5, 55–70K): when the reel builds or shows something, the finished result is the first cutaway (≤ 1.5 s in, after the face opens on the hook), then the steps; show each list item AS itself (the overhead shot is an overhead shot).
- **Show the change, don't describe it** (round 3): every "do X" line gets a frame where X visibly happens: the light switches on, the bad version then the good one, Raw | Edited side by side. A list reel with no screen content jumps location/outfit per item when the footage has it.
- **Editorial type for key phrases** (round 3): a serif with ONE italic/script accent word, mixed sizes in one block, for 3–5 moments. It reads as made by a person; the bold sans caption stays the readable default for everything else.
- **Literal hook image** (round 3): when `style_plan.json` has `hook_image`, show the hook's strongest verb as a picture for ~1 s right after frame 0 (tape across a logo for "murdered", a struck-through "CHATBOT"). Face first, then the image, then back to the face.
- **No AI-slop tells** (round 4, full list in `qa.md`): never all-caps centred text on a gradient, glow on everything, neon overload, cartoon versions of real people. Keep one honest human moment if the creator has one (a laugh, a self-aware "um").
- **Never film/TV clips or other creators' footage** even as a 1 s reference: use a quote card (serif line + "— Dune") or the creator acting the line.
- **Must not look AI-edited, cartoony or monotonous** (the creator, 24 Oct 2026): no emoji-stuffed labels (≤ 1 emoji per reel on screen), no sticker on every beat, no generic "whimsical" doodles as a substitute for an idea. Edits come from real editing craft: rhythm cuts, speed ramps, punch-ins on the beat, match cuts, sound design, real b-roll, and 2–3 strong designed moments — not a constant layer of overlays. Vary the rhythm: fast stretches, then a held face moment.

## 1. Review (before touching anything)
- `T/scripts/analyze.sh src.mp4 work/` → `work/islands.txt`, `work/silences.txt`; transcribe; read the whole transcript. `T/scripts/sample_frames.sh src.mp4 work/watch 1` → look at every contact sheet.
- `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,color_transfer,color_primaries -of compact src.mp4`. HLG is handled by make_cut.py; PQ must be converted first; **compare one graded frame with the raw frame side by side before cutting** — bright phone HDR can come out neon/over-saturated: then use `--no-grade --exposure 0.6 --saturation 0.62` (calibrated 24 Oct on a face-mask selfie) and re-check; log footage (S-Log/D-Log) → Rec.709.
- Note what can be better: hook in the first 1.5 s? face in frame (eyes top third, head centred) when the hook starts? length vs 25–35 s; fillers/repeats; missing yes/no CTA or loop line; topic broad or dev-only; footage issues (resolution, backlight, dark face, camera height, framing too wide, echo, low energy, takes not looking at the lens).

## 2. Cut
- Keep whole speech islands; drop dead air, fillers, throat-clears, repeats, false starts (keep the last clean take; "again"/"cut"/"let me redo" = drop the attempt before it). When two takes are equally clean, keep the one looking into the lens with more energy. Never change the creator's content.
- Buried claim → move that segment to the front. Cut inside islands at an envelope dip below ~−45 dB (`T/scripts/envelope.py src.mp4 a-b`); whisper timings near pauses drift — never trust them alone.
- Pads ~0.04–0.06 s before the first word, ~0.06–0.08 s after the last (tight Shorts pacing); 20 ms fade-in / 30 ms fade-out per segment. The first segment starts ≤ 0.06 s before the hook's first word and its first frame shows the face (nudge if blinking / looking away).
- `python3 -I T/scripts/make_cut.py src.mp4 segments.txt assets/main.mp4 --hold 0.3 [--exposure E --saturation S --no-grade]` (bakes tone-map, 9:16, upscale + gentle grade, voice cleanup). Confirm `color_transfer=bt709`.
- **Speech you can't transcribe reliably** (Hindi/Hinglish with the English-only model, mumbles): caption only the lines you can verify; give the rest visual-only beats — never guess words into captions. If a reel is mostly non-English, ask the creator once whether to add a multilingual whisper model (≈ 470 MB download).
- **Verify the cut:** `python3 -I T/scripts/qa_reel.py --audio assets/main.mp4` → no repeated words/phrases, no fillers, no pauses > 0.25 s, first word ≤ 0.1 s, tail ≤ 0.5 s after the last word; fix and re-cut until clean. Fix brand-name spellings for captions.

## 3. Face map, treatment, beat map
- `T/scripts/sample_frames.sh assets/main.mp4 work/geo 0.5 1` → `work/geometry.json`: per shot `{from, to, face: "C2:D3 (x 400-800, y 430-850)", text_zone, caption_zone, reframe}` — always include exact face pixels. If the head isn't centred or the framing is too wide, plan a reframe (scale/translate on `#cam`).
- **Choose the style automatically** — never ask the creator: write the cut's sentences (with times) to `work/lines.txt` and run `python3 -I T/scripts/choose_style.py work/lines.txt --script script.md --out work/style_plan.json`. It picks the treatment from the content (signals + the script's format label), enforces the rotation rules in `style_log.md` (not the last 2, Cinematic once per 4, frequency penalty), the signature move, music mood and a per-line component plan within the enhance budget. Use its result as the starting `EDIT_PLAN.md`; override it only for a reason you can state in one line (e.g. the script's edit brief names a treatment, or the creator said "use Notebook"). Read `template/style-dna.md` if it exists.
- **Write `EDIT_PLAN.md`** exactly in the `planning.md` format: scene type per line (T / TC / TL / SP / FG / TB), the real visual for each, motion feel, hold time, quiet moments, assets needed. Check all 11 rules before building.
- **Write a motion brief** (`motion.md`) under each graphic beat.
- **Enhance pass** (`enhance.md`, autonomous — starts from `style_plan.json`): read each line, confirm or adjust the lightest component that earns its place (`roll-text`, `pop-blur`, `swing-window`, `code-window`, `count-roll`, `hand-annotate`, `list-header`/`step-progress`, or a registry block; default is none), fill the Component column of `EDIT_PLAN.md`, and respect the budget (≤ 2 heavy, 2+ quiet beats).
- Write the **sound map** (`sound.md`) under the table.

## 4. Composition (HyperFrames)
`npx hyperframes init videos/<name> --non-interactive --example=blank --skill=general-video`, then build `index.html` from `T/composition/reference-index.html` patterns.
- Canvas 1080×1920, 30 fps; root `data-duration` = cut length incl. hold. `const CONTENT = {…}` at the top holds every word, number and colour.
- **Tag every clip**: `data-role="graphic|broll|hook|cta|caption|group"` and `data-scene="T|TC|TL|SP|FG|TB"` (qa_reel.py and the variety rules read these).
- **Safe box: x 60–930, y 250–1420.** Only the progress bar sits outside it.
- **Camera (`#cam`):** motivated moves only (`motion.md`): 1.00/1.06 at jump cuts, one 1.12–1.15 punch on the key term/twist, slow push-in on serious lines, slow 6% zoom-out on long talk stretches, reframe per shot from `geometry.json`. Use `hyperframes-keyframes` for smooth camera paths.
- **Treatment look:** surfaces, fonts, colours, feel and SFX palette from `treatments.md`; brand constants unchanged.
- **Hook words (0–0.55 s):** 2–4 huge plain-English words (the spoken claim) in the graphics band above the face over a light top scrim (≤ 0.45 opacity, top 760 px) — `.flash`/`.flash-in` in the reference. Face never dimmed or covered. Bass hit at 0, whoosh as the words clear at ~0.42, camera snaps 1.18 → 1 at 0.45. First caption and card wait until 0.5 s.
- **Captions:** reference chunker (≤ 3 words, no punctuation shown, never ending on a weak word), word pop, one highlighted word per chunk max, y ≈ 1230, moved/hidden during TL cards.
- **Components:** build the enhance-pass picks from `T/composition/components/` (`buildRollText`, `buildSwing`, `buildPop`, `buildCodeWindow`), tag each clip `data-component="<name>"`.
- **On-screen facts:** fact-check every number/label that appears on screen against a primary source before building (24 Oct: "50 applications per 24 h" became "50 a day" per Naukri's own FAQ).
- **Graphics:** build from the motion briefs; registry first; real assets; content block; three-object rule; min 34 px text; never two cards at once; never over the face box.
- **Scene types:** TL darkens/blurs only behind the card; SP puts the face (head centred) in the bottom half; FG ≤ 3 s; TB via `hyperframes:embedded-captions` / `npx hyperframes remove-background` with background dimmed 30–40% (skip TB if cutout edges look rough).
- **B-roll:** hard cuts, 1.2–3 s, covers nearby jump cuts (no face flash < 0.6 s), real and specific to the line. Screen cards via the creator's recordings or `npx hyperframes capture <url> -o cap --skip-vision --skip-assets --max-screenshots 3` (crop, scroll). Never fake product UIs.
- **Loop ending:** the identical hook-words overlay fades in over the final 0.55 s on the face; the CTA clip ends exactly when it begins.
- **Progress bar:** 8 px accent bar at the very top over the speech.
- **CTA card (while the yes/no question is spoken, ≈ the last 2.5–3 s; the reel ends on the question's last word):** the in-video CTA from `T/composition/components/cta-card.html` (WINNING_PATTERNS §6): **follow** (default — profile card with the cartoon avatar, "@{handle} · one AI thing decoded every day", cursor clicks Follow → Following), **save** for framework/reference reels, or **comment** (composer types the yes/no answer, e.g. "YES", and posts it) when the question is the point. The yes/no question stays on screen above the card; "{brand}" stays. `script.md`'s edit brief picks the variant; default follow.
- **Two hook variants:** A = hook words over the face, B = no overlay (face + caption only), for Instagram Trial Reels. Both open on the face speaking.
- Seek-safe (state object + `tl.eventCallback("onUpdate", render)`); `npx hyperframes lint` after each structural change.
- **Build order:** hero beat first → snapshot → compare with the treatment → fix → the rest → snapshot one frame per beat (storyboard) → animate details.
- **Helper agents (approved by the creator):** with 3+ graphic beats, give each beat to a helper agent (`model: "sonnet"`) as its own sub-composition `compositions/beat-N.html`, briefed with: the treatment section, the beat's motion brief, the content block, canvas/safe box/face box, "seek-safe GSAP, no wall clock, run `npx hyperframes lint`". The main agent (planning, design calls, assembly, QA) stays on the stronger model. **At most 4 renders/snapshots at a time.**

## 5. Sound
- Follow the sound map with the reel's **2–3 signature SFX used the same way every time** (sound.md "SFX as structure"): SFX motivated by on-screen motion, ≥ 2 silent spots, never two at once, no SFX on b-roll hard cuts or caption pops, volume 0.15–0.35, 30–60 ms fade on tails, light shared reverb glue.
- **Beat grid:** `python3 -I T/scripts/beat_grid.py assets/audio/bgm.mp3 --offset <bed start> --out work/beats.json` → snap graphic entrances, b-roll cuts and camera punch-ins that are NOT tied to a word onto beats (big moments on bars); after the build run it with `--check` (qa.md step 5). Speech timing always wins.
- Music: `pick_music.py` (see Autopilot) → trimmed `bgm.mp3` that is energetic from second 1; never a soft intro. Bed ≈ −20 dB under the voice (gain 0.10–0.12), carved with `hyperframes-audio`'s `carve.mjs` (`--bed bgm --voice a-roll`), lift to ~0.2 under the CTA question, then a 0.15 s fade with the last word (no music tail). the creator's voice is never suppressed.

## 6. Self-check + review gate (before showing the creator) — full list in `qa.md`
0. **Vet the enhance pass** (`enhance.md` §4): earn-it test, timing to the spoken word, seek test, look vs the treatment.
1. `npx hyperframes check --snapshots` → 0 errors; plus the two `--caption-zone` UI-zone runs.
2. `python3 -I T/scripts/qa_reel.py videos/<name> --segments segments.txt --geometry work/geometry.json` → 0 errors (flashes, read time, face flashes around b-roll, text over the face, scene variety).
3. **Frame-0 gate:** `npx hyperframes snapshot --at 0,0.25 --no-end -o review/f0` → face visible and lit, hook words above, no card; voice starts ≤ 0.1 s.
4. `npx hyperframes snapshot --frames 24 -o review/v1` → `T/scripts/safe_zone.sh review/v1 review/v1_safe`; look at every still and at full-size frames for each beat: the by-eye list in `qa.md` (plays twice, late text, face covered, head centred, lip sync, cheap mockups, rough cutouts, rhythm, sound).
5. **Studio preview for the creator** (their approval gate): `npx --yes hyperframes@<pinned> preview videos/<name> --no-open --port 3002` (runs in the background), open http://localhost:3002 in the built-in browser and give them the link; stop it with `--stop` after approval.
5b. Draft render for review: `npx hyperframes render -o review/draft.mp4 -f 30 --quality draft -w 2`; open `T/review/review.html` (load the draft; the creator presses N to leave timestamped notes and copies them back).
6. **Auto-fix loop (no questions):** fix everything found, re-run 0–4; repeat up to 3 rounds. A component that still fails after round 2 is removed (plain beats broken). Only then show the checkpoint, listing what was auto-fixed or dropped.

## 7. Render (after approval)
- `npx hyperframes render -o renders/raw.mp4 -f 30 -q delivery -w 2`; the log must show `"hasHdrContent":false`. Long renders: `HYPERFRAMES_RENDER_DETACHED=1` in its own process group.
- `T/scripts/finalize.sh renders/raw.mp4 renders/<name>_final.mp4` → −14 LUFS, −1.5 dBTP. Verify with ffprobe (1080×1920, 30 fps, audio + video) and re-run the frame-0 gate + `qa_reel.py --audio` on the final file.
- `node T/scripts/make_srt.js index.html renders/<name>.srt`.
- Append to `reels/style_log.md`: date, reel, treatment, signature move, scene mix, caption highlight, music track.
- Record what the reel IS for the channel report: `P features <reel> format="<script format>" hook_shape="<claim|question|persona twist|if I started|list number|…>" treatment="<treatment>" signature="<move>" length_s=<final s> wpm=<qa_reel pace> music="<track>" cta=yesno series="<series or none>" episode=<n> components="<comma list>"` (P = `python3 -I T/scripts/pipeline.py`).

## 8. Two covers (A/B)
Covers are separate image files — **never put a cover into the video**. Instagram: upload as the reel's cover in the post flow ("Edit cover" → "Add from camera roll"). YouTube: custom thumbnail where allowed, otherwise pick the most expressive frame in the app. The posting kit says which file goes where.
A = curiosity question (`cover-template.html`), B = bold claim (`cover-template-b.html`). **From the reference reels (WINNING_PATTERNS §7):** the cover states the promise in ≤ 8 words — for a list reel the number + topic + scarcity ("3 Claude tools nobody uses"); a small lead-in line + a big key phrase; the face (expressive, tight) or the hero visual; a series tag when it's a series ("pt.2", "Day 4"). Never a cover without a headline — `qa_reel.py --cover <file>` fails a near-blank image. 1080×1920; most expressive face frame cut out; curiosity-gap headline at the top; topic visual; teaser pill; "{brand}" tag; cover styling may echo the reel's treatment. `T/scripts/render_cover.sh src.mp4 <t> work/cover` (then `SKIP_CUTOUT=1`). Everything important inside the 3:4 grid crop (y 240–1680) — check `cover-check.png`.

## 9. Posting kit (`posting_kit.md` from `T/posting-kit-template.md`; quick web search for current trends first)
- Instagram: search keyword in caption line 1, 2–3 plain lines, save / send / yes-no question; max 5 hashtags (3 on-topic + 2 trending tech, never #ai #fyp #reels #explorepage); alt text; pinned question comment; story poll sticker.
- YouTube: keyword-first title ≤ 60 chars phrased like a search query, no hashtags in the title; description with 3 hashtags; tags ≤ 500 chars that belong to THIS reel (re-read them); `.srt`; Science & Technology; not made for kids.
- Schedule: Instagram 7–9 PM (your timezone), YouTube 12–2 PM (your timezone); never two on one platform within 12 h; never 11 PM–9 AM (your timezone).
- **LinkedIn:** `linkedin_post.md` + `linkedin_image.png` from `reel-script` if present; otherwise write them per section 6 of `$PLUGIN/skills/reel-script/SKILL.md` (professional voice, no your employer internals). Post the morning after, Tue–Thu 8–10 AM (your timezone).
- After posting: pin the question, reply to every comment in the first hour, share to Story with a poll, 10 genuine comments on bigger tech creators' fresh posts, log the 48 h numbers.

## 10. Upload — only after the creator approves BOTH the video and the covers
rclone remote `{drive_remote}:` (already authorized). Folder `{drive_folder}` (spelled exactly like this). **Always create a NEW subfolder named `<reel_name>` first; never upload into `{drive_folder}` itself.**
```bash
rclone mkdir "{drive_remote}:{drive_folder}/<reel_name>"
rclone copyto "<final.mp4>" "{drive_remote}:{drive_folder}/<reel_name>/<reel_name>.mp4" -P
rclone copyto "<cover.jpg>" "{drive_remote}:{drive_folder}/<reel_name>/<reel_name>_thumbnail.jpg" -P
rclone copyto "<cover-b.jpg>" "{drive_remote}:{drive_folder}/<reel_name>/<reel_name>_thumbnail_b.jpg" -P
rclone copyto "<name>.srt" "{drive_remote}:{drive_folder}/<reel_name>/<reel_name>.srt" -P
rclone copyto "posting_kit.md" "{drive_remote}:{drive_folder}/<reel_name>/<reel_name>_posting_kit.md" -P
rclone copyto "linkedin_post.md" "{drive_remote}:{drive_folder}/<reel_name>/<reel_name>_linkedin_post.md" -P
rclone copyto "linkedin_image.png" "{drive_remote}:{drive_folder}/<reel_name>/<reel_name>_linkedin_image.png" -P
rclone lsl "{drive_remote}:{drive_folder}/<reel_name>"   # verify sizes match
```
If rclone auth fails, ask the creator to run `rclone config reconnect {drive_remote}:`.

## 11. Revisions and learning
Fix the named beat, `npx hyperframes snapshot --range a,b --frames 6`, re-check, re-render as `_v2`. For **every** note the creator gives: ask "which instruction would have prevented this?" and write that rule into this skill or its reference files (add an automated check to `qa_reel.py` when possible), then tell them what changed. Save any reusable graphic as a component in `T/composition/components/` (one HTML file + one line in `components/INDEX.md`) and new b-roll in `$STUDIO/broll/INDEX.md`.
