---
name: make-content
description: End-to-end {brand} pipeline from ANY topic (or straight from existing footage, or a study of reference reels) — script + shoot sheet + LinkedIn post (reel-script), a paired carousel (generate-carousel), then after the creator AirDrops the footage, the fully edited reel + A/B thumbnails + posting kit (reel-edit), all uploaded to one Drive folder. Works for any topic they gives; the 30-day playbook is optional context, used only when a topic matches one of its ideas. Runs in parallel with helper agents, tracks every stage in a resumable manifest, and stops only for filming and the two approvals. Use when the creator says "make <topic>", "make: <topic>; <topic>", "make R03", "footage ready", "edit: <video>", "study: <reel links>", "continue <reel>", or "pipeline status".
---

# make-content (orchestrator)

> **Setup first.** These values come from `~/.config/reel-studio/config.json` (written by the `studio-setup` skill — run it if the file is missing):
> `$STUDIO` = `studio_dir` (your working folder: `template/`, `reels/`, `carousels/`, `research/`) · `$PLUGIN` = `plugin_root` (this plugin) ·
> `{brand}`, `{handle}`, `{creator_name}`, `{drive_remote}`, `{drive_folder}` = the matching config keys. Channel rules, approval gates,
> posting slots and timezone live in `$STUDIO/CHANNEL_RULES.md` — they override any default numbers written below.

This skill only orchestrates. The work itself follows `reel-script`, `generate-carousel` and `reel-edit` exactly — read each one before running its stage and never re-implement their rules. Spec: `$STUDIO/template/PIPELINE.md`. Channel rules + approval gates: `$STUDIO/CHANNEL_RULES.md`. Learned patterns from the creator's reference reels (hooks, layouts, CTA cards, covers, captions): `$STUDIO/template/WINNING_PATTERNS.md` — every stage reads it.
`P = python3 -I $STUDIO/template/scripts/pipeline.py` (manifest, render locks, footage pickup, gated uploads).
**Any topic is the default input.** The playbook (`$STUDIO/{handle}-content-plan.html`: R01–R30 reels, C01–C30 carousels) is optional context — use it when the topic matches one of its ideas, never require it.

## Commands
| the creator says | Do |
|---|---|
| `make <topic>` / `make: <topic>` | Half 1 for one topic (the normal case) |
| `make: <topic>; <topic>; <topic>` | Half 1 for several topics in parallel, one combined checkpoint |
| `make R03` / `make week N` | Same, taking the topic(s) from the playbook (optional shortcut) |
| `footage ready` / `footage ready R03` | Half 2 (if no name: the topic(s) with `footage: waiting`, oldest first) |
| `edit: <video> [notes]` (footage that has no script) | **Edit-only mode** below |
| `study: <links>` (reference reels the creator likes) | **Learning mode** below |
| `continue <reel>` | `P status <reel>` → resume at `P next <reel>` |
| `pipeline status` | `P status` → one line per topic |

## Setup per topic
- **Resolve the topic (any topic works):**
  - **Free topic (default):** take the creator's words as the topic. Quick-check the playbook and `reels/` (folders + `style_log.md`): if it matches a playbook reel idea, reuse that idea's hook, fix, demand note and paired carousel outline as a head start (record the ID); if it repeats a reel already made, say so in the checkpoint and pick a fresh angle. Otherwise build everything from the topic itself.
  - **Playbook ID** (`R03`): its title, hook, fix, and the paired carousel from the calendar.
  - **Carousel without a playbook pair:** choose the format from `generate-carousel/formats.md` that fits the script (how-it-works → step-by-step, myth → myth vs fact, career → framework/checklist, news → explainer, story → story) and build it from `script.md`.
  - Apply the channel rules to every topic: broad angle over dev-only (reel-script's topic check), the fix, plain-English hook, yes/no CTA.
- `reel_name` = snake_case of the topic. `P init <reel_name> --topic "<topic>"` (+ `--playbook R03 --carousel C02` only when a playbook idea was used). Work in `$STUDIO/reels/<reel_name>/` (move the session there with change_directory); the carousel lives in `reels/<reel_name>/carousel/`.
- Update the manifest at every stage: `P set <reel> <stage> running` → do it → `P set <reel> <stage> done` (or `failed --note "<error>"`). Record deliverables with `P file <reel> <key> <path>`. Skip any stage already `done` (idempotent resume).

## Half 1 — no footage needed (no questions)
1. **research** (main agent): one fact-check pass for the topic (shared by script, carousel and LinkedIn); note facts + sources in `research.md`.
2. **script** (main agent, `reel-script` sections 1–5, 7): `script.md` with the edit brief (format incl. Fact or Hype? / identity reframe / mantra / skit / money-saved list, **look A–E**, music mood), 95–120 spoken words (≈ 200 WPM), credibility line by second 5, live reactions + verdict, yes/no CTA + loop line; shoot sheet (lighting/framing from the look) published as an artifact. Done before anything else starts — everything below depends on it.
3. Then in **parallel**:
   - **carousel** → helper agent (`model: "sonnet"`): "Follow $PLUGIN/skills/generate-carousel/SKILL.md steps 1–7 for <topic> (format: <chosen format>; playbook outline <C-ID> if one was matched) in <reel>/carousel/, paired with <reel>/script.md and research.md. Pipeline mode: do NOT show a checkpoint and do NOT upload; stop after caption.md and report the QA result and the contact-sheet path." Then `P file <reel> carousel_dir <reel>/carousel`.
   - **linkedin** → helper agent (`model: "sonnet"`): "Follow $PLUGIN/skills/reel-script/SKILL.md section 6 for <reel>/script.md; write linkedin_post.md and render linkedin_image.png; report paths." Then `P file` for `linkedin_post` and `linkedin_image`.
   - Main agent meanwhile reviews the shoot sheet and prepares the checkpoint.
4. **checkpoint1** — one message (one section per topic in batch mode): shoot-sheet link, carousel contact sheet + cover, LinkedIn post text + image, any failed stage. the creator replies "ok" / "approved" (or per-topic notes → fix those only, show again). On approval: `P approve <reel> checkpoint1`.
5. **upload1**: `P upload <reel> half1` (carousel slides + PDF + caption, LinkedIn post + image → `{drive_folder}/<reel>/`, size-verified). Set `footage` stays `waiting`.
6. Tell the creator: "Film <reel> with the shoot sheet, AirDrop it, then say `footage ready`."

**Batch (`make: topic; topic; …`, or `make week N` from the playbook):** run Setup + steps 1–2 for each topic with up to **4 helper agents in parallel** (one per topic, `model: "sonnet"`, each following reel-script for its topic and returning when script.md + shoot sheet exist), then step 3 for all topics (carousel/LinkedIn helpers, max 4 running at once), then **one combined checkpoint 1**. Main agent checks each script against reel-script's rules before the checkpoint.

## Half 2 — after "footage ready"
1. **footage**: `P footage <reel>` — finds the newest video in `~/Downloads` (AirDrop) or `inbox/` since the topic started, prefers a file named after the reel/ID, waits until it has stopped copying, checks ≥ 1080p / 15 s–8 min / audio / 20 GB free, copies it to `reels/<reel>/src.<ext>` (the original stays in Downloads). Exit 2 = several candidates → ask the creator once which one (`--file`). Exit 3 = pre-flight failed → report and stop this reel only.
2. **cut → plan** (main agent, `reel-edit` steps 1–3, following `script.md`'s edit brief): review (raw-vs-graded frame check for HDR), cut + `qa_reel.py --audio` (repeats, fillers, pauses > 0.25 s, **pace ≥ 190 WPM**, **ends ≤ 0.5 s after the last word**), face map, **style chosen automatically** (`choose_style.py`: 10 treatments, rotation from `style_log.md`, list device, hook image), beat map, motion briefs, enhance pass (`enhance.md`: components + budget), on-screen facts checked, sound map, **music picked + trimmed automatically** (`pick_music.py`).
3. Then in **parallel**:
   - **build**: one helper per graphic beat (`reel-edit` step 4 "Helper agents"); every HyperFrames render/snapshot they run goes through `P locked render -- <command>` (max 4 at once on this Mac).
   - **covers**: helper (`model: "sonnet"`): `reel-edit` step 8 (A + B). the creator's cover rule: no wide gaming-chair cutouts — use a tight, expressive frame or a no-photo topic cover. Then `P file <reel> cover_a|cover_b <path>`.
   - **posting_kit**: helper (`model: "sonnet"`): `reel-edit` step 9 from `posting-kit-template.md` (trend search; caption = hook line → list as text → trust line → yes/no question → SEO keyword line → 3–5 specific tags; YouTube title, tags, schedule) → `P file <reel> posting_kit <path>`.
   - Main agent: assemble (components from `template/composition/components/`: roll-text, pop-blur, swing-window, code-window, step-progress, list-header, check-card, count-roll, hand-annotate, cta-card; entrances snapped to the music's beat with `beat_grid.py`), sound mix (`reel-edit` step 5: energetic bed from second 1, 2–3 signature SFX).
4. **qa**: `reel-edit` step 6 — auto-fix loop up to 3 rounds: `hyperframes lint` + `check --snapshots` + both UI-zone checks, `qa_reel.py` (enhance budget, static stretches, read time, face box), `qa_reel.py --cover` on covers A + B, `beat_grid.py --check`, **frame grading** (every 1 s frame scored, all ≥ 8/10), AI-slop tells, frame-0 gate, the creator's taste checks (music energetic in the first 3 s, last 4 s is the best-looking frame, ≤ 1 emoji, nothing templated), draft render via `P locked render -- npx hyperframes render … --quality draft`, Studio preview started for checkpoint 2.
5. **checkpoint2**: `reel-edit`'s checkpoint message (Studio preview + review.html draft, storyboard, hook A/B, covers A/B, posting kit, QA report). Approval → `P approve <reel> checkpoint2`. Notes → `reel-edit` step 11 (fix + rule update) → show again.
6. **final**: `P locked final -- npx hyperframes render -o renders/raw.mp4 -f 30 -q delivery -w 2` → finalize → SRT → re-check frame 0 + `qa_reel.py --audio` → `P file <reel> video <final.mp4>` and `srt`.
7. **upload2**: `P upload <reel> half2` (video, both thumbnails, SRT, posting kit — size-verified). Then log the reel in `reels/style_log.md`, mark it posted-ready, and reply with the Drive folder + posting times.
Several reels with footage: run Half 2 one reel at a time (helpers parallel inside each); queue their final renders under `P locked final`.

## Edit-only mode (`edit: <video>` — footage without a script)
1. `P init <reel> --topic "<the creator's one-line description>"` → `P footage <reel> --file <video>` → mark research/script/carousel/linkedin/checkpoint1/upload1 `done --note "edit-only"`.
2. Run Half 2 from step 2. Without a script, `reel-edit` writes `work/lines.txt` from the transcript, `choose_style.py` + the creator's words decide the style, and the creator's notes ("keep the length", "make it whimsical") override defaults and channel length rules — say so at the checkpoint.
3. Skip carousel/LinkedIn unless the creator asks. Test reels the creator won't post: never upload, mark `checkpoint2 failed --note "test"`, still turn their notes into rules.

## Learning mode (`study: <links>` — learn from reels the creator likes)
1. Open each link in the built-in browser (signed in) — one `browser_batch` of navigate + javascript per reel works well (the page's `script[type="application/json"]` blocks hold the media object whose `code` is the shortcode). For each reel read the page data for the direct MP4 link, caption, likes/comments, music; collect them in the page's localStorage across navigations, then download the MP4s with curl into `research/refs_<date>/` using the **full signed URL** (stripping the query string breaks the signature and yields empty files — check every file with ffprobe) (yt-dlp needs a login — never export browser cookies). Carousels: capture the slides in the page.
2. `python3 -I $STUDIO/template/scripts/analyze_reference.py research/refs_<date> --meta meta.json` → transcripts with word timings, WPM, first word, loudness, cuts, hook strip + 16-frame sheet per reel; check the music floor (10th-percentile RMS ≈ −25 dB = bed; when speech is wall-to-wall there are no gaps, so also measure the **tail** — seconds and level after the last word — which shows how the reel ends).
3. Watch every `view.jpg`, read every transcript and caption, look at every cover. Weight reels by proven performance (posts a few hours old prove nothing yet).
4. Write `research/refs_<date>/NOTES.md`, append a new round to `template/WINNING_PATTERNS.md`, then push each rule into the skill that owns it (reel-script, reel-edit + treatments/motion/sound/qa, generate-carousel, posting kit, choose_style/pick_music/qa_reel when it can be automated).
5. Delete the downloaded videos; keep notes, transcripts and sheets. Report what changed in each stage.

## Music library (never an interruption)
- Only YouTube Audio Library "Attribution not required". To grow the library: in YouTube Studio → Audio Library (signed-in browser) list tracks through the page's `creator_music/list_tracks` call (licence YOUTUBE; genres hip-hop / pop / dance & electronic / R&B; moods funky / happy / bright; drums), get download links with `get_tracks` (`includeDownloadUrl`), score candidates with `template/scripts/music_energy.py`, keep energy ≥ 72 and add rows (bpm, energy, best start) to `music/INDEX.md`. `pick_music.py` does the per-reel choice + trim.

## Learning loop (every reel)
- Every note the creator gives → fix + "which rule would have prevented this?" → write it into the owning skill/QA script → tell the creator (reel-edit step 11). Durable preferences also go to memory.
- 48 h after posting: log the numbers; a reel ≥ 3× the channel median → suggest 2–3 follow-ups on that topic (CHANNEL_RULES.md).

## Robustness rules
- A failed stage: retry it twice (fresh helper), then `P set … failed --note`, **keep the other branches going**, and list the failure in the next checkpoint. Never stop silently, never hide a failure.
- Helpers report back paths + QA results; the main agent verifies their output (opens the contact sheet / files) before marking the stage done.
- `P upload` refuses without the matching approval in the manifest and verifies every file's size on Drive — never upload any other way in pipeline mode.
- If the session ends, `continue <reel>` picks up from the manifest; nothing is redone.
- Interruptions allowed: filming, checkpoint 1, checkpoint 2, a footage choice when ambiguous, and sign-ins. Music is never an interruption: if `music/INDEX.md` has nothing unused for the mood, download a YouTube Audio Library "Attribution not required" track without asking. Everything else uses defaults and is listed at the checkpoint.
