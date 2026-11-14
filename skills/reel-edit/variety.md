# Variety, sound and cadence rulebook — round 7 (IG study, 30 Oct 2026)
Source: a 31-reel study (editing/sound craft + Claude-made edits), 30 Oct 2026 — measured numbers are summarised in `template/WINNING_PATTERNS.md` §34. The creator's complaint that triggered it: "my edits look like a generic AI made them and all my videos feel the same."
Read this BEFORE choosing the treatment. It adds to `treatments.md` / `sound.md` / `motion.md`; where it conflicts with an older rule, **this file wins** (the older rules came from before the study).

## 0. The creator's hard notes (30 Oct 2026, an example reel v2 — they rejected two drafts before approving the third)
1. **The creator's face stays on screen 100 % of the time.** No full-screen text or graphic beats in a talking-head reel (FG is for b-roll/real screen footage only, never typography). A giant-text beat that replaced the creator's face was rejected: "I want my face in the video, not replaced by text."
2. **Graphics must ILLUSTRATE the sentence** — the real objects of the idea (servers, clocks, satellite, atomic clock, packets, transactions), drawn as one consistent flat illustration style (`composition/components/sticker-kit.html`). Never generic cards, terminal windows, sticky notes or big type as the explanation: "looks like a simple machine / AI did this, this is what we wanted to avoid."
3. **Low cognitive load, clean, energetic:** one idea per beat, ≤ 4 objects on screen, ≤ 3 words of text per object, ONE persistent scene that evolves (the same INDIA/US racks + clocks carried 5 beats) instead of a new card per sentence; energy comes from motion (pop with overshoot, ticking clock hands, blinking LEDs, flowing dashes, a packet that crawls and dies), not from more things.
4. **Motion explains:** every animation shows the mechanism (a packet crossing, a hand drifting ahead, chips re-sorting 2·3·1 → 1·2·3), timed to the spoken word; sound lands 40 ms early.
5. **No mistakes shipped:** snapshot every beat at full size and read it before showing the creator (overlaps, clipped art, edge margins, class clashes); iterate silently until clean.
6. **Versioning:** a re-edit never overwrites the first cut. Local files `renders/<reel>_v2_final.mp4`, `_v2.srt`, covers `<reel>_v2_thumbnail(.b).jpg`, `posting_kit_v2.md`, composition in `video_v2/`; Drive: `<drive remote>:<drive folder>/<reel>/v2/` (a NEW subfolder inside the reel's folder, after the creator approves video AND thumbnails).
7. Build gotchas learned: caption word class `.w` and hidden-object class `.o` clash with component classes (use `.wh`, `.or`, `.kw`); animate `x/y/scale`, never `left/top` (lint error); art placed in a scaled wrapper must be checked against the 60 px edge margin AFTER scaling; one `#stage` clip makes `qa_reel.py` report a false "static for 35 s".

## 1. The sameness cure: every reel gets its own "world"
A reel's look = **World** (palette + type + surface) + **Signature gadget** (one component nobody sees twice in a row) + **Sound palette** (2–3 signature sounds) + **one human/physical element**.
- Read `reels/style_log.md` first. **Never repeat the previous two reels' World or Signature gadget.** Log all four in the style log row.
- Worlds (the three in `treatments.md` still count; these five are new and live in the same brand constants — face frame 0, safe box, one accent):
| World | Look (hex) | Type | Signature gadgets | SFX palette | Seen in |
|---|---|---|---|---|---|
| **Graphite HUD** | bg `#0b1120`, gold `#e8b84a`, white; thin 1 px gold frames | Montserrat 700 captions top + JetBrains Mono labels | `select-caption`, `count-roll` + `stopwatch`, timeline HUD, `dm-toast` CTA | digital-tick, soft-pluck, ui-open, low-pulse | DeyusrQMOmi (35M-view claim) |
| **Sticker Pop** | real footage + flat illustrated stickers (ink `#16213e` outline, hard shadow), blue `#2f6bff` / orange `#ff7a1a` / yellow `#ffd23f`, green ok, red wrong | Montserrat 900 + one Playfair italic accent | `sticker-kit` scene (racks, clocks, cloud, satellite, chips), one persistent scene | pop, ui-open, negation, whip, ding | an example reel v2 (approved) — default for concept explainers with the creator on camera |
| **Paper Kinetic** | cream `#e9e4d8` with soft vignette, ink `#141414`, ONE red `#d7261e` word per line | Montserrat 800, tight tracking | `kinetic-type-3d`, `stamp-slap` (**faceless reels only — see §0**) | whip, slice, typewriter, stamp | DfEJ6KaI9g2 |
| **Neon Waveform** | black `#050505`, lime `#c6ff3d` glow | Montserrat 800 + script accent | `sound-strip`, `sfx-chip`, `ab-header` | glitch, zap, typewriter, riser→hit | Dd_EPp5RzRN, Dd3r5DyxYxX |
| **Warm Cinematic Serif** | real footage graded warm/teal, shallow focus, vignette | EB Garamond / Cormorant, italic accent, soft glow | physical props (paper timeline, hands), wardrobe/location change | whoosh-air, paper-slide, soft-hit | Dad6htNxoo1, DfAZMAjseOQ |
| **Blue-Room Pills** | saturated blue key light behind the face, captions on solid pills (blue pill + yellow keyword) | Inter/Montserrat 700 | proof card top (real page), counters, `loading-hook` | notif-pop, counter-roll, ding | DfFFGpzxcEe, DdQ7l1DRgg5, DdEiw1Ggo0c |
- Variation budget per reel: change **World** and **gadget**; keep the brand constants. Coverage: after 5 reels all five worlds + the original three should have appeared at least once.
- **One human/physical element per reel** (not another overlay): a hand gesture staged to a sound, a real prop, a wardrobe or location change between sections, a words-in-the-scene moment (word sits behind/next to the creator in the actual room), a paper/notebook b-roll, a screen recording with tap rings.

## 2. Hook formula — the proof object is in frame 0 (all 30 reels)
Voice starts at ≤ 0.1 s. Frame 0 shows the creator's face (rule stays) **plus a proof object in the graphics band**: a number contrast ("3.2M | 322", "125K vs 16.6M"), the real page/card, the odometer already rolling, the finished effect. Six shapes: number-contrast · claim+proof · finished-effect-first · forbidden/emotion ("feels illegal to tell this") · word-play contrast ("Your type isn't boring. Your *timing* is.") · physical gag.
- **Demo first, then "here's how"** for any how-to (all of Harry Allsop / Frenciel / Arthur): the finished effect plays 3–5 s, `loading-hook` bridges, then steps. For explainers: the *result/claim visual* first.
- **Open loop in 3 words** mid-reel ("Wait for last!", "but there's a catch") — see DfBT7LNuykR.
- **Demonstrate each rule in the thing it names** (DeRe3zfiI1j: the yellow-text rule is yellow; the glow rule glows; DcgVac4o__C names fonts in their own font).
- **Example cards carry real numbers** (view counts, before/after); never invented. **Series badge** ("DAY 9/365", "pt.2") on tutorials the creator plans as a run.

## 3. Captions that carry meaning
- Chunks 1–3 words (1–2 in Hinglish, see §6); **colour = meaning**: red = stop/negative/mistake, yellow = attention/transition, green = success/good, white default, accent = the number. Keep to one accent family per World.
- Top-of-frame captions when the creator sits low (Graphite HUD, Blue-Room Pills); `select-caption` selection box on ≤ 2 words per minute.
- **Words in the scene:** a keyword sits at the object it names (the word "pop up" pops in red next to the hand) — one per reel, max.

## 4. Sound (full catalog: `composition/assets/audio/sfx/CATALOG.md`)
- **Density:** a deliberate sound every 1.5–3 s in talking reels. Every visual event has a sound; no sound without one. This replaces "never SFX on b-roll cuts / caption pops": a cut to a NEW idea gets `slice` / `camera-shutter` / `whip`; the one or two punch words get `glitch`; list/step captions get `digital-tick` / `typewriter`. Cuts within one idea stay silent.
- **Sync:** the transient lands 30–60 ms BEFORE the visual. Build the sound map from the beat map's frame times minus 2 frames.
- **See the sound** when the topic is AI tools / editing / sound: `sound-strip` or `sfx-chip` — the named sound on screen while it plays.
- **Voice-only A/B:** three of the study's Claude-made reels use NO music (voice + UI sounds, digital silence between words). the creator's rule (every reel has music) stays; ship ONE reel in 5 voice + SFX only and compare 48-h retention.
- **Master:** −14 LUFS integrated, true peak ≤ −1 dBTP (25 of 30 study reels sit at −14.0…−14.6).

## 5. Cadence — the pro-editor tell
- Voice 170–230 wpm after the cut (study median ≈ 190); silences/breaths ≤ 0.12 s; first word ≤ 0.1 s.
- **Visible event every ≤ 1.5 s** (caption word, chip, counter tick, camera drift, cut). Don't count cuts — static screen reels and kinetic type have none and still hold.
- Camera: slow drift always on (scale 1.00→1.04 over a shot), punch on key words, **match-cut on eye position** across b-roll cuts (DfAZMAjseOQ: a bracket box stays in the same place while the shot changes).
- Transitions are allowed again, but **earned**: `whip` / `slice` / flash-frame or a golden-bokeh flash when the *idea* changes (≤ 3 per reel, each with its sound). Still no transition inside one idea.

## 6. Code-mixed / non-English scripts (example: Hinglish)
- **Transcribe with the multilingual model and a Roman-script prompt** (tested 30 Oct 2026 on a Hindi TTS sample: plain/auto → Devanagari with "Claude" mangled; with the prompt → Roman Hinglish, English terms intact):
  `whisper-cli -m ~/.cache/hyperframes/whisper/models/ggml-small.bin -f work/a16.wav -l hi -ml 1 -sow -np --prompt "Hinglish in Roman script. English tech words stay English: Claude, AI agent, token, API, prompt, LLM."`
  Don't put the reel's own sentences in the prompt (it parrots them). Verify every line by eye; fix names. If accuracy is poor on real footage, download `ggml-medium.bin` (≈ 1.5 GB) and tell the creator.
- **Captions in Roman Hinglish** (readable in one glance for the India audience; Devanagari only if the creator asks). English nouns stay English, Hindi glue stays Hindi ("Claude ek agent hai jo…"). 1–2 words per chunk at Hinglish speed; the key noun (English) gets the accent colour.
- Script (`reel-script`): the hook is one plain Hinglish claim ≤ 9 words; the analogy is an everyday India-specific one (chai, auto, UPI, Swiggy, cricket); the CTA stays one yes/no question, in Hinglish ("Kya aap AI par apna resume bharosa karoge? YES / NO").
- SFX stay short (< 0.3 s) in dense Hinglish stretches; keep voice 6 dB above the bed.
- Study gap: none of the 31 reels is Hinglish — these are extrapolated; compare retention after the first 3 Hinglish reels and update.

## 7. Checklist before the checkpoint (add to `qa.md` run)
World ≠ last two · gadget ≠ last two · ≥ 1 physical element · proof object in frame 0 · colour-meaning map applied · sound every ≤ 3 s, early by ≥ 30 ms · ≥ 2 silent spots · −14 LUFS/−1 dBTP · style_log row written.

## 8. Creator note, 14 Nov 2026 (a payments explainer) — "motion graphics look ugly, generic, edited by AI, not human"
First draft used a dark navy-glass "Fintech Glass" panel over a darkened wall (translucent cards, mono labels, pills, a flash + streak on the whips). Rejected on sight; the same family as the rejected "Lime Console" (an earlier indexing explainer). Rebuilt as **Sticker Pop** (ink-outlined flat objects, hard shadow, overshoot pops) and approved direction again.
1. **Never put a dark glass/console panel, dark gradient shade, pills-with-mono-labels or neon accent over the footage.** Footage stays untouched (no `shade-top`, no vignette overlay in the composition — the grade is baked into main.mp4).
2. **Draw the real object of every sentence** (phone with PAY, ₹ coins, server rack, balance chip, key, paper sheet + rubber stamp, red ✕ gate). A "REJECTED" moment is a physical stamp on a paper, not a UI card. Text ≤ 3 words per object, ink text on green (white on green fails contrast).
3. **No composition-level effects that read as AI**: no white flash overlay, no light-streak on whips, no glass blur. A whip is only the camera smear + its sound.
4. Palette for a payment topic: ink #16213e, phone blue #2f6bff, coin orange #ff7a1a, key/attention yellow #ffd23f, ok green #19b36b, wrong red #ef3b3b. Idle life (blinking LEDs, flowing dashes, spinner) + tap pulses on the beat make it feel handmade.
5. Build gotchas hit here: the scene container class `.g` collided with a green-tag class `.g` (`inset:0` stretched tags over the face) — use `.gr`; every absolutely positioned sticker needs `position:absolute` written out.

## 9. Creator note, 14 Nov 2026 (a prefetching explainer, first draft rejected): "the motion graphics look ugly, like an AI edited it; they pop out instead of blending with the content"
The draft used a dark glass HUD panel (Graphite HUD) holding a tiny phone, spinner and cards: a mostly empty box slapped on top of the shot, blur-pop entrances, generic dashboard look. Rebuilt in Sticker Pop and approved-style craft. New rules (they win over §1's Graphite HUD row for concept explainers):
1. **No containers.** No panel, card background or glass box behind a scene. Objects (phone, queue, dial, tags) sit directly on the footage as flat ink-outlined stickers with a hard shadow, sized to their content, never a big box with one small object inside.
2. **Real content inside the graphic.** A phone shows the reel's own footage (a small `assets/phone.mp4` proxy cropped to the face, played by a `<video class="clip">`); queue cards are stills from the footage. Never gradient rectangles as stand-ins for video. A `<video>` must not sit inside a timed wrapper (`video_nested_in_timed_element`): leave the scene wrapper untimed and tween an inner `#sceneW`.
3. **Graphics ride the shot.** The scene wrapper follows the camera zoom at 45 % (`PAR`) and slides with the whips, so stickers sit in the room instead of floating above it. Camera `transform-origin` ≈ the hair top (50 % 44 %) so punch-ins do not push the head into the caption row.
4. **Settle, don't pop.** Entrances travel ~26 px with `power3.out` over 0.45–0.5 s (no `back.out`, no blur-pop); exits are faster and small; use the same objects across beats (one phone, one stopwatch that turns green) instead of new cards.
5. **One texture over everything:** film grain (jittered at 12 fps, overlay 10 %) + the baked vignette, so footage and graphics read as one piece.
6. Build gotchas: a utility class `.g` (full-screen layer) collided with the green tag variant `.tg.g` and stretched the tag to a tall bar (name colour variants `gn`); absolutely-position every standalone SVG; prefer `fromTo` + `immediateRender:false` over `tl.set` for state that must survive a backwards seek; hide the overlay screens (home, spinner, stopwatch) explicitly when a scene leaves.
