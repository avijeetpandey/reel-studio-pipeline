# Auto edit — script in, finished reel out (round 8, 14 Nov 2026)

The creator pastes a **script** (and, when they have it, the footage). They give **no style instructions**: the edit is decided by `template/auto/` and the study behind it
(`research/refs_<date>/REPORT.md` from the `study:` command; round 8 analysed 59 reels). This file wins over `treatments.md` / `planning.md` / `enhance.md` wherever they overlap; the creator's hard notes in `variety.md` §0, §7, §8 still apply.
`A = $STUDIO/template/auto`, `S = $STUDIO/template/scripts`, `PY = $STUDIO/tools/.venv/bin/python` (numpy, opencv, librosa; `scripts/setup.sh --install` creates it).

## The run (everything automatic; checkpoint 2 is the only stop)
1. **Intake.** `P init <reel> --script script.md` (script = the creator's words, copied verbatim; never rewritten, `script_lint.py` is advice only). Footage via `P footage <reel>`.
2. **World + look, before the cut.** `python3 -I A/autodirect.py world --script script.md` → `{world, grade}`. Cut once with the look baked into the single encode:
   `python3 -I S/make_cut.py src.mp4 segments.txt assets/main.mp4 --look <grade> [--size 1440x2560 for punch headroom]` (then the usual `qa_reel.py --audio`).
   Pre-flight, review, footage_check, cut rules in SKILL.md §1–2 are unchanged.
3. **Plan.** `python3 -I A/autodirect.py plan --reel reels/<reel>` → `edit_plan.json` + `EDIT_PLAN.md` (transcribes `assets/main.mp4` with the Hinglish whisper prompt if `work/words_cut.json` is missing —
   **read the words and fix names / Hinglish spellings in `work/words_cut.json`, then re-run `plan`**). The plan holds: world, caption style + rows that avoid the face, camera track, transitions, SFX list, music,
   CTA. It also logs the world in `reels/auto_style_log.json` so the next reel differs.
4. **Compose.** One command: `A/run.sh reels/<reel> [world]` = plan → `compose.py` → carve the music under the voice (strength 0.25, via the shared `tools/hf-core`, so a brand-new project needs no npm install) → lint. It creates the HyperFrames project (`videos/<reel>/`) if missing. The cut lives at `videos/<reel>/assets/main.mp4` (a cut written to `<reel>/assets/main.mp4` is linked in automatically). Keep your own edits to `edit_plan.json` with `SKIP_PLAN=1 A/run.sh reels/<reel>`.
   `compose.py` writes the complete `index.html` (footage + voice stem + captions + camera effects + SFX + music + grain + progress + CTA cards). **Per-shot reframe is automatic:** Apple Vision measures the face in every shot and `autodirect` zooms wide shots (≤ 1.32×, `main.mp4` has 1440×2560 headroom) and shifts them so the face is the same size and height everywhere; the caption row hugs the hair (top-style worlds) or sits on the chest, and the CTA row never touches a face — all computed AFTER the reframe. **CTAs:** a question in the last 3 sentences gets a *comment* card typing a sample answer ("YES" for yes/no, "Mera answer" for an open question); a "follow" line gets a *follow* card right after it (each card ends when the next starts); `answer` spaces are kept.
5. **Graphics (optional, agent-made or carried over).** Slots (env vars for `run.sh`, flags for `compose.py`): `GRAPHICS=g.html` (inside `#stage`, follows the camera at 45 %), `GRAPHICS_JS=g.js`, `GRAPHICS_CSS=g.css`, `OVERLAY=o.html` (static, outside the camera — for cards that bring their own animation; then set `cta: null` in the plan). Re-editing a reel that already has an approved scene: lift it with a small one-off script (extract the scene DOM/CSS/JS + its sounds from the old composition) and merge the sounds into the plan — the new camera, grade, captions and music replace the old ones. **A re-edit is a new folder `reels/<reel>_v3` (never overwrite the approved cut).** `autodirect` marks `graphics: optional-sticker` for explainer/hype worlds. Add Sticker Pop scenes (`components/sticker-kit.html`, variety.md §0/§8: containerless, face 100 %, ≤ 4 objects,
   motion shows the mechanism) ONLY for ideas that need a drawing; a plain, well-cut reel beats a decorated one (round 4: the most decorated reels got the fewest likes). They go in the `#stage` slot and follow the camera at 45 %.
6. **QA (auto-fix ×3).** `hyperframes lint` + `check --snapshots` + both UI-zone checks; **snapshot every transition** (`snapshot --at J-0.1,J,J+0.1`) and read the frames; `qa_reel.py` (flashes, static stretches, face box); mix loop
   `python3 -I A/balance.py reels/<reel> review/draft.mp4` → voice 10–14 dB over music + SFX (min ≥ 8); it nudges `music.vol` in the plan, then `SKIP_PLAN=1 A/run.sh reels/<reel>` + a new draft (max 2 rounds; carve 0.25 is the default — 0.5 ducked the bed 22 dB under the voice, inaudible); frame grading (≥ 8/10); AI-slop tells (qa.md).
7. **Checkpoint 2, final render, covers, posting kit, upload** exactly as SKILL.md §5–10 (covers/posting kit helpers unchanged). The checkpoint lists: world + why, grade, caption style, transitions (time + type), music + licence line, anything the QA fixed.

## Worlds (`A/worlds.json`) — picked from the script, never the same as the last two reels when another fits
| World | When | Grade | Captions | Transitions | Punch |
|---|---|---|---|---|---|
| **clean_pop** (default) | tech explainers, how-it-works | `clean_bright` | pop: heavy sans, accent `#ffd23f`, 2 words | whip 5 · shrink 2 · blurIn 2 | 1.07, ~2.2 per 10 s, shake every 3rd |
| **warm_cinema** | career, story, opinion | `warm_cinema` | serif (Playfair) above the hair, italic accent words | leak 4 · blurIn 3 · whip 1 (≤ 2 leaks) | 1.05, ~1.4 per 10 s |
| **hype_hero** | bold claims, news, "stop doing X" | `punchy` | hero: giant opening words, then pop | shrink 4 · whip 4 · blurIn 1 + one rgb split + aperture opener | 1.09, ~2.8 per 10 s |

## Effect grammar (`A/fx.js`; every effect moves the footage or is one lens-style layer — never a panel, glow, glass or sticker on the face)
- **Camera track:** shots alternate 1.00 / world B-scale so every jump cut reads as a camera cut; slow drift inside a shot; opening snap 1.12–1.2 → 1.0 in 0.45 s; punches 0.09 s up / 0.5 s settle on emphasis words (numbers, negations, contrast, stretched words), ≥ 1.4 s apart, never within 0.5 s of a join; punches snap to a music beat only if it sits ≤ 120 ms before the word (speech timing wins).
- **Transitions only at jump cuts that start a new idea** (sentence start + connector word, ≥ 2 s since the last join): ≤ 1 per ~9 s, ≥ 4.5 s apart, none in the first 3 s or last 4 s, never the same type twice in a row. whip = directional SVG motion blur + 12 % overscale (no edge shows); shrink = tilt/shrink/fly with vertical blur, captions blink out; blurIn = focus pull; leak = amber lens leak (film world only).
- **Texture:** one jittered grain layer over footage + graphics; the colour look is baked into `main.mp4` (no composition-level vignette, shade, flash or streak — variety.md §8).
- **Captions:** colour = meaning (red negative, green good, accent = number/contrast); chunker never ends on a weak word; rows come from Apple Vision face boxes (`face_boxes`): the caption row and CTA row never touch a face (hair-top → chin, with camera-zoom margin).
- **Sound (ROLES.json):** whip/shrink/focus/leak transitions get their role sound 40 ms early; numbers → `tick`, negations → `negation`, contrast/stretch → `hit_soft`, hook ping only in clean_pop/hype, CTA → `notif` + `click` + `success`. One file per role per reel (seeded by the reel name), all levelled to the same peak (−10 dBFS) before the role volume (0.18–0.30), spacing ≥ 0.35 s, the sentence before the CTA stays silent, voice ≥ 10 dB over everything else.
- **Music:** `pick_music2.py` — energetic from second 1 (precomputed bar-aligned starts, no soft intros), BPM 100–126 preferred, mood by world, skips the last 3 reels' tracks, rotates between a track's top starts, 0.28 s fade with the last word, carved under the voice. Sources: YouTube Audio Library ("Attribution not required") and Mixkit (free licence, no attribution) — every row of `music/INDEX.json` carries its licence line. Instagram's in-app music is never used (not licensed outside the app).

## "Feels human" checklist (from the study; run it at QA)
- Cuts land every ~3 s on average and each one is hidden by a framing change or a transition; nothing static for > 4 s.
- First word ≤ 0.1 s, face in frame 0, last frame ≤ 0.5 s after the last word, loop restarts into the hook.
- ≤ 3 transitions, each at an idea change; ≤ 1 loud SFX per ~6 s outside transitions; at least 2 silent beats.
- Captions sit where a person would put them (above the hair or on the chest, never on the face), key word coloured by meaning.
- The grade looks like footage, not a filter: skin untouched, luma mean 85–110, saturation 0.2–0.35.
- At most ONE designed moment per 6–8 s; no gradient panels, neon, all-caps centred text on a gradient, emoji labels.
- If a human editor would have left a line plain, it is plain.

## Pickup shots (what to film next time to feel less "one camera, one room")
`EDIT_PLAN.md` ends with 3 suggestions taken from the script's sentences: an overhead shot of hands doing the thing, a wardrobe/location change at the idea change (the strongest "human" tell in the study: celfstudies, iamsarahsnow, liveairprod), a prop held up as the proof object. Suggestions only — the edit never waits for them.

## When something looks wrong
Fix the plan, not the composition: edit `edit_plan.json` (change a transition type/time, drop a punch, swap an SFX role, switch `world`) and re-run `compose.py`; it is deterministic and takes seconds. Every note from the creator → which rule in `autodirect.py` / `worlds.json` / this file would have prevented it → write it there (SKILL.md §11).

> Rounds 9–13 (frame-0 headline, logo chips, phrase captions (one master since Round 22), grade checks, look tests) shipped as code in `template/auto/`; their detailed notes are summarised in the docstrings of `autodirect.py` / `compose.py`.

## Round 14 — the PREMIUM layer (22 Nov 2026; study `research/refs_<date>/REPORT.md`; "make it premium, polished, not monotonous")
Why: every effect up to Round 13 moved the camera; nothing happened IN the scene, and with no person matte every graphic floated flat on top (the "AI-edited" note).
The reference edits (eightsenses "Kinetic Text Reels") get their premium feel from DEPTH: the room becomes a set, words and a glass ribbon sit BEHIND the person.
**It is ON by default** (`PREMIUM=0` = the Round 13 look). Files: `A/person_matte.py|.swift`, `A/premium/{premium.py, premium.js, premium.css, themes.json, fonts/}`.
1. **Matte (after the cut, before `run.sh`):** `python3 -I A/person_matte.py reels/<reel>/videos/<reel>` → `assets/fg.webm` (Apple Vision person segmentation, VP9 + alpha,
   ~3.5 min for 36 s at `--quality accurate`; cached; `--force` after a re-cut). Check one frame over magenta (hair, fingers, held objects) before composing.
   Without `fg.webm` compose drops the word-behind + room tint and warns (they would cover the face).
2. **Plan:** `autodirect.py plan` calls `premium.plan()`: theme (rotates; never the last two), room tint 0.58, back ribbon + 4 edge orbs, the frame-0 claim as the
   WORD BEHIND THE HEAD (`HEADLINE="kick line|word"` — line 2 is the big word, line 1 the small kick above it; set it from the creator's hook as in Round 12),
   numbers → outline word, "samjho X … phonebook hai" → X behind the head, two-tier captions, and ONE card per sentence that DOES something:
   comparison (nahi…sirf) → ✕/✓ checklist · sequence of tech terms → node timeline · "kis server / kahan kam" → 3-stop slider · "hazaaron" → counter ·
   "load ho jaati" → loading bar · a question (not the CTA) → search bar typing it · CTA "A ya B?" → **DM bubble with reply chips** (replaces the comment card;
   the follow card stays). Each card kind once per reel (nodes twice), ≥ 1.2 s apart, one on screen. Transitions: `shrink` → `zoomBlur`; the join nearest the
   first "samjho / matlab" becomes one theme-coloured `streak`; each gets riser → impact. Read the "Premium layer" block in `EDIT_PLAN.md`.
   **Override anything** in `reels/<reel>/work/beats.json` (keys of `plan.premium`: `behind`, `cards`, `trans`, `theme`, `room`, `depth`…; given keys replace the auto ones).
   `THEME=chrome_night` forces a theme.
3. **Layout (automatic, from the Vision face box):** card band y 285 → caption row − 16 (cards shrink to fit: never over the face); caption block just above the hair;
   the word's baseline sinks ~1/3 into the hair; captions skip a phrase the word/kick already shows and lift above a word on screen. Front ribbon is OFF
   (a band across the chest covers his hands — test 22 Nov 2026); orbs stay at the frame edges.
4. **QA additions:** snapshot the frame-0 word, each card, and every zoomBlur/streak (J−0.06, J+0.06); read: word legible ≥ 60 % above the hair, no card or
   caption over the face, room tint looks like a lit set (not a filter) and skin is unchanged, streak ≤ 1 per reel.
5. Rules that still stand: face 100 % on screen (no full-screen cards), only LIGHT frosted cards sized to their content (the dark glass HUD stays banned),
   numbers are never invented (slider labels are names, not fake percentages), music stays (mixed under the voice as before).
6. **Also built (same day):** face-in-circle iris (the first open-loop question after the hook: the frame irises to a circle round the face, ring + the
   sentence on a circular path, themed set around it; one per reel) · split panel (the first node timeline of a ≥ 3 s sentence becomes a full-width panel
   above the head, face 100 % below) · particle word (the outline number, else the 2nd word, assembles from particles) · logo row (≥ 2 brands in one
   sentence; DM chips carry the brand logos too — `brands.json` now has chrome/brave/firefox/safari/edge) · photo fan (only when the creator drops stills in
   `reels/<reel>/broll/`; never stock images).
Test reel: `the first test reel` (not uploaded).

## Round 14b — the creator's notes on the first premium draft (22 Nov 2026): "slow, not energetic, purple everywhere, flashy, ugly AI crap; the earlier cut was better"
What he rejected: violet room tint, glass ribbon + orbs ("purple strips killing the vibe"), generic frosted cards / DM bubble / two-tier pills replacing the reel's own
infographics, soft blur-in motion, a thin serif word that the head half-covered. What he liked in the ORIGINAL cut: natural room colour, the Sticker Pop scene telling
the story beat by beat, ~50 sounds tied to what's on screen, punchy pop captions, the comment card typing "Chrome".
**The premium layer is now ADDITIVE and small (defaults changed in code):**
1. **Never tint the room, no ribbon, no orbs, no streak, no particles** (all off; `room/depth` stay null). The footage keeps its own colour (16 Nov rule stands).
2. **Colour per reel, from the footage + script** — `premium.footage_palette()` reads the room's hue/saturation/lights from 3 frames; `pick_accent()` scores
   yellow/lime/cyan/coral/orange/pink/mint/violet by contrast with the room, harmony with its lit details, the script's mood, and avoids the last two reels'
   accents; violet is penalised. The accent colours the word, the caption highlights and the glow. (Olive/khaki dim room + tech script → cyan.)
3. **The reel's own scene owns the story.** Generic cards are OFF (`PREMIUM_CARDS=1` turns them back on for a reel with no drawn scene). Keep the Sticker Pop scene;
   a re-edit carries it over (`GRAPHICS*` env + its scene_events sounds, see `the first test reel/work/apply_v3.py`).
4. **Word behind the head, done right:** heavy Anton block caps in the accent (white→accent gradient, hard shadow), ≤ 3 per reel, ≤ ~840 px wide, top at
   hair − 0.74·size so the head covers only the lower ~25 % of the middle letters; it SLAMS in (1.55→1, 0.2 s, power4) with a camera bump + whoosh → impact,
   drifts 6 %, snaps out in 0.16 s; ≥ 1.4 s on screen; captions step aside while it is up (`caption.skip`). Candidates: the hook claim (`HEADLINE="kick|word"`),
   numbers (only when there is no drawn scene: the scene owns numbers), the defined term of a "samjho X … hai" sentence — but never a word the scene already
   draws (visible text of `GRAPHICS*`) and never a generic word (internet, website, request, computer…): then the sentence's strongest other noun (PHONEBOOK).
5. Captions: the approved pop style (never `hero`, never two-tier pills by default) in the reel's accent. CTA: the approved comment + follow cards; an "A ya B?"
   question types A (Chrome). Transitions: the camera ones (whip / blurIn); `shrink` still becomes `zoomBlur` (no black void).
6. Fixed on the way: `compose.py` dropped any SFX shorter than 30 ms, so `digital-tick.mp3` (the typing sound) was silent in every reel — now kept.

## Round 15 — KINETIC DEPTH (22 Nov 2026, third pass after the creator: "you edited it the same as before; learn what the references actually do; use my background")
What the references really do (re-studied at 5–10 fps): a CONTINUOUS kinetic-type track. Every phrase becomes designed type in the room: a small lead-in
line + (when the phrase has one) a BIG keyword that blooms out of a light smear, sits behind the head, lights the wall and whips out; props live in the room
behind the speaker; the room is graded darker so the type is the light source. One word twice per reel (Round 14b) is not that.
**Now the default** (`KINETIC=0` turns it off): `premium/premium.py` `kinetic()` + `premium/kinetic.js`; captions are replaced by the lead lines.
- Big keyword per phrase: number (+unit, "ek second" → 1 SECOND) > tech/brand pair (LOAD BALANCER, IP ADDRESS) > tech/brand > tagged word; never Hindi
  function words (HSTOP), never generic words (GENERIC), never the same root twice within 4 s; ≥ 0.9 s apart, ≤ 2 s each, one on screen; width MEASURED in the
  browser and fitted to 860 px; top = hair − 0.74·size. "X nahi, sirf Y" → X is struck in red, then Y lands.
- Lead lines: the phrase minus the big word; a lead of ≤ 1 word is dropped, tiny phrases merge; above the big word, or at hair − 210 alone.
- Props from what the sentence is about: map (duniya / a country; the arc launches ON that word, India → named place) · digits (an IP under "IP") ·
  tilted search card (a "naam → IP / convert" sentence: types website.com → resolves the IP) · server racks either side of the head ("kis server / kahan kam";
  the emptiest goes green on "kam"; no big word while racks are up) · light sweep ("load ho jaati") · VS + brand logos flanking the head (CTA "A ya B?").
- Stage: room shade 0.42 behind the person (skin untouched), accent light spill that flares with every word, camera bump on each landing, whoosh → soft hit.
- QA: 2 fps sheet of the whole draft + a snapshot at every big word and prop; read every frame: nothing clipped, nothing over the face, one big at a time,
  lead never under a card, arc on its word. 
## Round 16 — craft pass (22 Nov 2026, the creator: "right direction, but the effects / motion / illustrations look below average and the music is not okay")
1. **Music must leave the voice band free.** `A/music_space.py` measures every track's energy share in 300 Hz–3 kHz (`voice_share`) and 30–150 Hz
   (`sub_share`); `pick_music2.py` penalises voice_share > 0.05. Funky/guitar beds (gimme-that-groove 0.089) fight Hinglish speech; a dark minimal pulse
   (minimal-techno-01-162: 0.033 / sub 0.87) sits under it. Re-run `music_space.py` after adding tracks. Always `balance.py` after the first draft
   (the denser bed needed vol 0.19, median 12.0 dB).
2. **Type craft (`premium/kinetic.js` v2):** big words rise letter by letter from the centre out of a light smear, then a sheen sweeps them; landings snap to
   a music beat within −100/+40 ms; lead lines reveal word by word at the spoken word times; leads attach to the NEWEST big word in their window and sit
   above its real (browser-measured) cap height — a lead placed against the glyph box vanished into the white top of "99%".
3. **Illustrations rebuilt:** real Natural Earth dot map (`premium/worlddots.json`, `dotmap.py`) with a radial reveal from the origin, comet-trail arc,
   arrival ripples and city pills; timer ring around the head for "N second(s)" (no counter label — it fought the word); glass search card in 3D tilt with a
   sheen and a drawn check; load-balancer hub feeding 4 glass racks by animated dashed links + packets, the emptiest turns green; progress sweep with %
   (no big word over it); VS logos with glow tiles.
4. **Bugs that shipped in the previous draft and are now guarded:** the lead container kept `opacity:0` from v1 (leads were invisible except while fading out);
   outer racks clipped at the frame edge once the camera zoomed (racks now x 84–996).
5. Review loop that found all of the above: 2 fps sheet of the full draft + snapshots at every big word and prop, read at full size, fix, repeat.

## Round 17 — DEFAULT since 22 Nov 2026 (approved on a test reel; study `research/refs_<date>/REPORT.md`)
Tools in `tools/ext/` (each in its own venv): **earshot** (MIT, sound from code, CPU, offline), **claude-video-effects** (MIT, look reference only —
rebuild good looks in HyperFrames; never put a file named `fx_private.py` in its scripts folder: fx.py executes it), **motionmaxxing** (Apache-2.0, rules + render audit).
1. **Emphasis budget** (`premium.py`, `KINETIC_V=3` = Round 16): 4–7 big words chosen by role — hook claim (shown from 0.6 s, frame-0 rule), the struck
   wrong word, the defined term, two-word terms; repeats of an earlier word score −6; ≥ 1.8 s apart; dropped words return to the lead line spoken over them
   (never duplicated).
2. **Role looks + room lighting** (`kinetic.js`): hook = neon serif + spotlight (room to near-black, he stays lit); struck = editorial serif + red strike;
   defined term = chrome; hero (last two-word term) = light rays + twinkles; numbers = block + spotlight. No bounce easing, no % counters.
3. **Transitions at every idea change** (`premium/v4_finish.py`): joins that start a sentence, ≥ 2.2 s apart, none in the first 3 s / last 4 s,
   alternating whip h / zoomBlur / whip v.
4. **Sound = shared earshot kit** (`composition/assets/audio/sfx/earshot/`, rendered once, `peaks.json`): every cue placed by the sound's PEAK
   (whoosh per cut, blip per word, boom on spotlights, riser→boom→shine on the hero, keystrokes + knock on the search card). Falls back to ROLES.json
   if earshot is missing. Then `balance.py` as always (v4 needed music 0.19).
5. **QA adds** `python3 -I S/look_audit.py review/draft.mp4 --out review/look --expect <s> --expect-audio`: report cut sync and G2/G3 at the checkpoint;
   motion energy reads low on a talking head (3.6) — note it, don't chase it.

## Round 18 — per-reel curation of the kinetic layer (24 Nov 2026; the creator: "edit it the same way as the first test reel, energetic and high paced")
The v4 recipe is the default (cut → `person_matte.py --quality accurate` → `autodirect.py plan` → `run.sh`), but its automatic big-word picker only knows DNS/browser vocabulary: on the crawler script it chose SERVERS, IP, GOOGLE, DOMAIN. Fixes now in the shared code:
1. **`KEYWORDS=<abs path>/work/keywords.json`** (read by `premium.kinetic()`): `bigs` = the reel's own list `[{big, t0, t1, role?: hero|chrome, strike?, style?}]` (cut-timeline seconds; replaces the automatic picks, no budget / spacing rule — keep it to ≤ 7, ≥ 0.8 s each, `hero` = the solution reveal with light rays, first big = the hook claim with the spotlight); `props` = the reel's own props (replaces the automatic ones, so no IP digits on a non-DNS reel); `cta_leads: true` keeps the lead lines up while a LONG CTA question is spoken (cards land only at its end; without it the question has no text on screen for ~3 s). Pick the words by reading the plan's lead lines + the script: one per idea, the term a viewer would search for.
2. **New props in `kinetic.js`** (canvas, one clock, seek-safe; band y 285–535): `flood` (GET chips converge on a server, load bar green→red, shake, "IP BLOCKED" stamp, later chips bounce), `urls` (infinite URL trap: /page/1 … /page/∞ with a looping arrow), `queues` (URL chips routed into one lane per domain, one worker bot per lane pulling one chip at a time, "1 req / sec", ✓ counters). Sounds for them are placed in `v4_finish.py` by peak (riser→boom on the stamp, key-clicks per URL row, pop per routed chip, blip per worker, ding per tick).
3. **Safe margins:** the camera zoom (up to ~1.26) crops the outer ~100 px of anything in `#behind`; keep prop content inside x 120–960 (the first queue labels were cut at "mazon.in"). Prop text ≥ 28 px, chips ≥ 100×38 px — the first sizes read as tiny at phone size.
4. **Phrase breaks:** `phrases_of` splits every 4 words, which leaves one-word orphans ("mein", "hai."): mark `|` after ≤ 4 words in `build_words.py` so every phrase has 2–4 words.
5. `TECH` now knows crawler / BFS / DDoS / frontier / queues / workers / throughput / overload / traps. Hinglish ASR tricks that worked here: a second whisper pass on 0.7× slowed audio (times ×0.7) fixed the squeezed fast-speech timings; `-l hi` (Devanagari) confirms WHAT he said when the Roman pass hallucinates ("scrollers" = crawlers, "Excuse me" = a clipped "queues").
6. Accent: the planner picked coral because the script contains "attack"; the reference look is cyan, so `THEME=cyan` was forced (the brief said "same as the first test reel"). `CHIPS=0` when a brand mention would collide with the kinetic type.
Run: `THEME=cyan CHIPS=0 KEYWORDS=$PWD/reels/<reel>/work/keywords.json bash template/auto/run.sh reels/<reel> clean_pop`.

## Round 19 — notification-system props + mix lessons (24 Nov 2026; the creator: "edit it the same way as the first test reel, energetic and high paced")
Recipe unchanged from Round 18 (cut → `person_matte.py --quality accurate` → `KEYWORDS=… THEME=cyan CHIPS=0 [MUSIC_FILE=…] run.sh`). New / learned:
1. **New props in `kinetic.js` (canvas, one clock, band y 285-535):** `jam` (one SINGLE QUEUE: promo chips flood + 10,000,000 counter, the login OTP joins at the back and waits → STUCK → USER DROP-OFF stamp; params `flood_t otp_t stuck_t drop_t`), `priority` (HIGH lane OTP/PAY fast + LOW lane PROMO slow into a worker pool; `hi_t lo_t pool_show pool_ts[3]` — pool box + 3 bots appear at `pool_show`, the SMS/EMAIL/PUSH names land at `pool_ts`), `retry` (PAY chip hops ✕ ✕ ✕ → ✓ with 1× 2× 4× wait brackets; `hops[4]`), `dupe` (payment card, TIMEOUT → RETRY, same card again, SENT TWICE stamp; `card1_t timeout_t card2_t dup_t`). Sounds are placed per prop in `v4_finish.py`. Reuse them for any queue / retry / idempotency / duplicate-delivery script.
2. **Layout bugs caught at snapshot:** an empty dark pool box shown 7 s before its bots (show it only with its content); a label placed on the path of the chip / arrow (keep labels off every moving element's path); a prop running into the CTA comment card (end the prop when the card lands: `t1` = card `t0` − 0.05) and CTA cards touching the lead line (`cta[].y` 470 → 432 in `edit_plan.json`, then `SKIP_PLAN=1 run.sh`).
3. **`MUSIC_START` is an INDEX into the track's `starts` list**, not seconds (`MUSIC_START=86.1` crashed pick_music2 and the reel silently got no music — `run.sh` printed "no <audio>/<video> with id=music"; always read that line). Index 0 and 1 both gave 11.1 s on minimal-techno-01-162 (the reference reel's slice); index 2 gave 1.74 s.
4. **Mix:** this voice sits quieter than the reference reel's: at the default 0.38 the bed + SFX were as loud as the voice (median −0.2 dB). `balance.py` clamps at 0.12, which was still 9.4 dB: set `music.vol` 0.07 by hand AND scale every sfx vol × 0.8 (cap booms/stamps at 0.26) → median 11.9, min 7.8 (voice pause at the CTA). Do this loop on the first draft instead of trusting the default; `mix_check.py` takes ~10 s.
5. **ASR where he differs from the script (captions follow what he SAYS):** "Seedhe dedicated queues mein jaate hain" (script: high-priority queues par), "exponential retries" (no "backoff"), "toh same notification user ko do baar" (script adds "payment"), a shorter CTA than the script ("Comments mein batao, aur aise videos ke liye follow kar lo"). Confirm each with a Devanagari pass on the 0.7× slowed island (`whisper-cli -l hi -ml 0`); flag the doubtful ones at the checkpoint.
6. **Length:** 43.1 s of speech from a 35 s script (he reads slower than the script's timing marks). Not cut (his words are never edited); every island boundary became a jump cut (15 segments), which keeps the pace high.
7. **Dark phone room (frame luma 47, face 46):** `eq=gamma` lifts washed the blacks milky (1.6 → luma 92 but flat); a shadow-lift curve `curves=all='0/0 0.08/0.21 0.18/0.41 0.5/0.71 0.8/0.91 1/1'` via `--look neutral --no-grade --extra-vf` kept the blacks (face ~86 on the test frame, 102 on the plan's check). Test 4 variants side by side on one frame first.

## Round 20 — two-person DIALOGUE from many clips (23 Nov 2026, a test reel; one person plays both speakers (the outfit tells them apart))
Brief: "dialogue-based edit, subtle, clean, premium, trim dead air". Recipe = Round 18/19 (v4 kinetic) with these changes:
1. **Many clips, one source:** `ffmpeg -f concat -safe 0 -i list.txt -c copy work/all.mp4` (same phone, same rotation) → `P footage <reel> --file work/all.mp4`. Per-clip offsets = cumulative container durations. Islands from `analyze.sh`; one segment per island (islands < 0.25 s apart merge); pads −0.05 / +0.08. Word timings: whisper medium `-ml 1 -sow` on each `work/isl/N.wav` **sequentially** (3 in parallel silently wrote nothing for 10 of 15 clips) + a 0.7× pass and a Devanagari pass to confirm what he says. If a stretch > 3 s has no cut (QA "static"), split a segment into two CONTIGUOUS ranges in `segments.txt` — the plan gets a camera join, `main.mp4` needs no re-cut.
2. **Speaker tags** (the dialogue cue): one quiet pill per turn at the left chest (y 1452, 30 px, amber dot = E1, accent dot = E2, 2 s), made with `OVERLAY=o.html GRAPHICS_JS=g.js GRAPHICS_CSS=g.css` (see a test reelwork/`). Whips sit ONLY on speaker changes and ping-pong direction (E1→E2 sign −1, E2→E1 sign +1); one zoomBlur per idea change (here Postgres → MySQL). ≤ 6 transitions per 50 s.
3. **New env knobs** (shared code, defaults unchanged): `TRANS_AT="6.33:whip:h:-1,14.57:zoomBlur,…"` (v4_finish), `ALT_B=1.05`, `PUNCH_AMT=1.04`, `HOOK_SNAP=1.08` (autodirect) — a close-up face (hair y 560, face 790 px tall) turns the default 1.10 alternation + 1.09 punch into a 1.25–1.4× zoom.
4. **Close-up layout:** only ~300 px of ceiling above the hair → NO props; `keywords.json` `max_w: 700` (the camera zoom crops ~100 px per side, 860 clipped "WORKLOAD"/"PHYSICAL LOCATION"), `lift: 40–50` so the quiff doesn't cover the middle letters, and when cards sit at y 290 the lead lines collide with them: set `cta_t0` to where the cards land and do NOT set `cta_leads`.
5. **Mix:** the default bed (0.38) gave median 8.7 dB; music 0.22 + every SFX × 0.75 (cap 0.26) → median 13.3 (`work/apply_mix.py`, re-run after every plan run).
6. **Dim room (frame luma 57-67):** `curves=all='0/0 0.09/0.205 0.2/0.405 0.5/0.69 0.8/0.895 1/1',eq=saturation=1.04` with `--look neutral --no-grade` → face ~110, blacks kept; a grey hoodie washes out under the stronger curve (0.08/0.21).
7. **Length:** 50.3 s of speech from a 30 s script (he speaks slower than the marks). Not cut — flag it at the checkpoint and offer a shorter variant.

## Round 21 — dialogue from 13 separate clips, one line per clip (24 Nov 2026; the creator: "dialogue-based edit, subtle, clean, premium, don't overdo, trim dead air")
Recipe = Round 20 (v4 kinetic kept subtle, speaker pills, whips only on speaker changes). New / learned:
1. **Never merge clips with `-c copy` concat when their audio is shorter than their video** (iPhone clips: audio 20–60 ms short): the audio drifted 0.33 s late by clip 13. Build `work/all.mp4` with the concat FILTER and frame-exact segments: per clip `fps=30000/1001,trim=end_frame=N,setpts=PTS-STARTPTS` + `aresample=48000,apad=whole_dur=VD,atrim=0:VD` (VD = N·1001/30000), libx264 crf 12 (see a test reelwork/` intake snippet in the transcript: offsets = cumulative VD). Mixed 30/60 fps clips are fixed by the `fps` filter. Verify by cross-correlating each clip's own wav with `all16.wav` (error ≤ 1 ms except a clip whose audio is longer than its video).
2. **Clips the creator already trimmed edge to edge:** segments = per-clip speech window (first/last 3 consecutive 10 ms frames above −43 dB), pads −0.05 / +0.08, clamped to the clip. No inner pauses > 0.25 s existed; the cut only trimmed heads/tails (39.0 s → 36.35 s). Voice level was already even across both speakers (−21.9…−24.9 dB mean) — check with a per-segment RMS before adding gain.
3. **Per-segment ASR on the CUT audio** (`work/seg_asr.py`, sequential): medium normal + 0.7× Roman + 0.7× Devanagari. The slowed pass clumps / hallucinates the prompt at the tail of some segments (use the normal pass for those); Devanagari confirms the words ("Kyunki", "karte hain", "zyada sasta", "Batao kya tum"). `work/build_words.py` takes a hand-typed phrase list (`|` = phrase break, `:y/r/g` = tag) and aligns it to the whisper tokens with difflib, interpolating unmatched words — far less typing than a full timing table.
4. **keywords.json pitfalls the planner swallows silently:** a big shorter than 0.8 s is dropped (KILL at 0.65 s vanished); a lead of ≤ 1 word is dropped (the big took "Optimistic", so "Concurrency" never appeared — end the phrase after "aur" so the lead has 2 words); a big that takes a word out of the MIDDLE of a phrase leaves "baad mein mein" (split the phrase there); a lead that flashes for 0.06 s before the CTA means `cta_t0` should be the segment start. Always list the planner's lead lines (`edit_plan.json` → `premium.kinetic.lines`) before rendering.
5. **Long two-word terms shrink to ~70 px** (22 characters in 760 px): use the single strongest word as the big and pair them (PESSIMISTIC … OPTIMISTIC hero) — the lead carries the rest.
6. `premium.clean()` now keeps the comma inside numbers ("10,000" showed as "10000" in the lead line).
7. **Transitions for a quick question/answer pair:** the 2 s question between two answers got a hard cut in and a zoomBlur into the answer (= the idea change), not two whips 2 s apart. Whips (ping-pong direction) stayed on the other speaker changes.
8. **Accent:** the planner chose coral because the script says "crash"; `THEME=cyan` forced (warm brown room + blue monitor, same as the series). Music: `deep-techno-ambience-134` (voice_share 0.043) needed music 0.13 (balance.py), sfx × 0.75.
9. **Fact check for the kit:** no primary source confirms Amazon's internal Prime Day inventory design (web search 23 Nov); the video says it (the creator's script), so the caption/description frame it as a simplified pattern and say Amazon has not published its internals.
10. Look: dim room (luma 39 raw, face 57) → the Round 20 curve `curves=all='0/0 0.09/0.205 0.2/0.405 0.5/0.69 0.8/0.895 1/1',eq=saturation=1.04` with `--look neutral --no-grade` (face 105, room 73).
Cut cost: a 4K → 1440×2560 cut of 36 s took 4.6 min with the person matte running at the same time (matte 292 s).

## Round 22 — AUTOMATIC LOOK + ONE MASTER (24 Nov 2026; study `research/refs_<date>/REPORT.md` + `effects_study.html`; the creator: "choose the best fit from the content, the frames and how it was shot, on your own; render only one video")
1. **Why:** the face-to-room brightness gap (L*) was **4** on the creator's footage (dim beige-olive room as bright as his face) vs **21-33** in the reference edits. A global LUT moves both together and only tints ("just adds warmth").
   The references keep skin natural and rebuild the ROOM as a lit set. the creator never has to pick a look or an effect: the pipeline does, and explains itself in `EDIT_PLAN.md`.
2. **`A/relight.py` (venv python, runs inside `run.sh` BEFORE the plan, needs `assets/fg.webm` from `person_matte.py`):** measures the footage (face / room L*, room cast a*/b*, saturation), picks **teal_amber** (default explainers / hype),
   **studio_key** (room already cool, bright or colourful) or **golden_hour** (story / career scripts in a neutral or warm room) from the script's world + those numbers, never the same look as the last two reels (`reels/auto_look_log.json`),
   calibrates exposure (face L* ~52, room at the look's target) and renders `assets/main_look.mp4` + `assets/fg_look.webm` (relit pixels + his matte, so the word-behind-the-head layer still matches). `assets/fg_raw.webm` keeps the plain matte.
   `compose.py` and `autodirect.py` (palette) use the `*_look` files when they exist and are newer than the cut. Result + reasons: `reels/<reel>/work/look.json`, printed as the **Look** block in `EDIT_PLAN.md`.
   spotlight / moonlight / high_key are never auto-picked; neon_night / lime_pop only with `LOOK=<name>` (the creator rejected purple room tints on 22 Nov). `LOOK=off` or `RELIGHT=0` removes the look: the reel renders as before. A failure logs and keeps the plain footage.
3. **Cut grade:** `autodirect.py world` now prints `grade: natural` (skin-safe) when the relight pass is on (`world_grade` keeps the old one; `RELIGHT=0` restores it). Never warm the cut.
4. **Order:** cut (`--look natural`) -> `person_matte.py` -> `run.sh` (relight -> plan -> compose). Cost ~7 min per 36 s reel at 4 workers on top of the ~5 min matte; cached while the cut + matte are unchanged. A re-cut makes the old relit twin stale (compose ignores it).
5. **Transitions follow the world** (`v4_finish.py`): hype_hero = shake3d, whip h, shake3d, whip v; clean_pop = whip h, zoomBlur, shake3d, whip v; warm_cinema = whip h, zoomBlur, whip v, zoomBlur (no shake in calm story reels). `shake3d` (premium.js) = push + roll + jolt + RGB fringe, landing on a soft boom, from the realtor reel.
6. **ONE master.** `run.sh` composes only `videos/<reel>/` (Follow card) and you render one `renders/<reel>_final.mp4` for Instagram AND YouTube. `YT_MASTER=1` rebuilds the dormant Subscribe master (see step 3 of Round 12). Never build / render / upload `video_yt` otherwise.
7. **At checkpoint 2** show one before | after frame (raw cut vs `main_look`), name the look in one line with its reason; never ask which look he wants.
8. **Studied but NOT wired (proofs only, `research/refs_2026-11-24/lab/fxlab.py`):** tilted wall word, outline text that follows the matte contour, face-tracking HUD, pixel-mosaic dissolve, die-cut sticker outline. Port one to HyperFrames only when a reel's script calls for it; keep them to one in-room beat per reel.
