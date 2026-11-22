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

> Rounds 9–13 (frame-0 headline, logo chips, two platform masters, phrase captions, grade checks, look tests) shipped as code in `template/auto/`; their detailed notes are summarised in the docstrings of `autodirect.py` / `compose.py`.

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
