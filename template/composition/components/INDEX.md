# Reusable graphic components

One line per component: file — what it shows — treatment — reels used in.

Each file is self-contained (CSS + markup + a `buildX(tl, opts)` function that adds seek-safe GSAP tweens to the main timeline); the header comment lists usage, options and rules. Ported from the Remotion `animated-reels` template (Oct 2026).

- `roll-text.html` — headline words rise out of a mask with stagger, `*accent*` word, optional exit; for hook words / big claims — any (colours from `--ink` / `--accent`) — not yet used.
- `swing-window.html` — app/screen window that swings in and out in 3D with blur; holds a real screenshot; use once or twice per reel — any — not yet used.
- `pop-blur.html` — default enter/exit for chips, labels, cards (rise + scale + blur-clear, calm exit); time to the spoken word — any — not yet used.
- `code-window.html` — dark code/terminal card that types its lines at reading speed with a blinking cursor; for dev/AI explainers — any (accent cursor) — not yet used.
- `step-progress.html` — "TOOL 2 OF 3" kicker + numbered stepper (done steps ticked) + optional giant serif numeral per item; for list reels (from the reference reels) — Editorial Split / any — not yet used.
- `cta-card.html` — in-video CTA: follow card (cursor clicks Follow → Following), save button (→ Saved) or comment composer typing the yes/no answer; replaces the static Like/Comment/Follow tiles — any — not yet used.
- `list-header.html` — list title pinned from frame 0 + a "#N" chip that swaps per item, or the full list with the current item lit (round 3: theaustinschneider, tenfoldmarc); for lists of 4+ — any (use instead of step-progress, never both) — not yet used.
- `check-card.html` — titled card ("Claude added:") whose empty circles tick one by one as each item is said, the text wiping in (round 4: carolyn.rose); for 3–5 short "what it does" items — any (pair with the `check-blip` SFX) — not yet used.
- `pill-list.html` — dense numbered list of 8–12 skills in colour pills + a role chip + a sourced fact line, one card per role, made to be screenshotted (round 5: xouryn 25K) — any — not yet used.
- `split-frame.html` — 2–4 rounded panels of footage (the same take at different moments, or b-roll) sliding in on the beat; panels are the composition's own muted `<video class="clip">` elements (round 5: kalylsfilms) — any, once per reel — not yet used.
- `flash-open.html` — 6–8 stills flashed two frames each (+ optional white frames) as a section opener, ≤ 0.6 s, never at frame 0 (round 5: kalylsfilms) — any, once per reel — not yet used.
- `tier-board.html` — S/A/B/C/F board whose chips land on each spoken placement (round 5: tier-list reels) — Editorial Split / any — not yet used.
- `count-roll.html` — odometer number whose digits roll from one value to another + small label; for stars/installs/users/$ (round 3: hananazeez.ai) — Data / Clean Tech / any — not yet used.
- `hand-annotate.html` — hand-drawn circle + arrow + handwritten label that draws itself onto the real frame, pointing at a real object (round 3: iamsarahsnow) — Notebook / Studio Kinetic / any (needs the Caveat font) — not yet used.

## Round 6 — IG study 30 Oct 2026 (31 editing/sound/AI-edit reels; notes in `research/ig_study_2026-10-30/REPORT.md`)
All verified by scrubbing the GSAP timeline in a browser (`components/_preview/gen.py` writes one test page per component exposing `window.TL` — serve the folder, `TL.seek(t)`, screenshot).
- `kinetic-type-3d.html` — **faceless / cutaway reels only; never a full-screen beat in a talking-head reel (it replaced the creator's face in an example v2 draft and they rejected it)**. Words land on the spoken syllable on a staggered stair; a virtual camera follows each word (motion blur), one accent word per line, then pulls back to the full phrase (DfEJ6KaI9g2, DeyusrQMOmi) — faceless/cutaway beats, cream+red or graphite+gold — not yet used.
- `sound-strip.html` — labelled waveform pills scroll past a fixed playhead; the lit pill = the sound you hear (Dd3r5DyxYxX 48.8K, Dd_EPp5RzRN, DcwZp1xM7Gi, DeKCJSlz5BX) — sound/tools/AI topics or a 2-s HUD when a sound family plays — not yet used.
- `sfx-chip.html` — small card (equaliser + sound name + 00:03) that pops 60 ms before its sound (Viewcci "With This / Use This") — any teach-a-sound/tool beat — not yet used.
- `select-caption.html` — top caption, current word bright / past words dim, meaning-words boxed with editor "selection handles" (speedy_devv 35M-view reel) — dark graphite treatments — not yet used.
- `stamp-slap.html` — rubber stamp ("CHEAP?", "FAKE") slams in at an angle with shake; answers an objection (DeT79uPlMkH) — any, ≤ 2 per reel — not yet used.
- `loading-hook.html` — "TUTORIAL LOADING 0→100 %" bar over the demo; bridges demo → how-to (Harry Allsop) — how-to reels only — not yet used.
- `dm-toast.html` — phone notification + comment rows landing; CTA as proof-of-demand (speedy_devv). Use with the yes/no question, not a keyword — any — not yet used.
- `stopwatch.html` — dial + "4 → 20 days" counter for time-claims; pairs with `count-roll` (speedy_devv) — any — not yet used.
- `ab-header.html` — two pinned labels, the lit side swaps with the demo ("WITHOUT SFX | WITH SFX") (Viewcci) — A/B / before-after reels — not yet used.
- `sticker-kit.html` — flat illustrated stickers (clock, server rack, cloud, satellite, atomic-clock tile, label chip, bubble, dashed link, cross, DB cylinder) + the pop/hands/blink/flow motion recipe; for concept explainers where graphics must ILLUSTRATE the sentence and the face stays on screen (an example reel v2, the creator's notes 30 Oct) — Sticker Pop world — used in an example reel.

