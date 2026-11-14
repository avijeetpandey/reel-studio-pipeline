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
