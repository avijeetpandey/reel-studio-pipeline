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
- `count-roll.html` — odometer number whose digits roll from one value to another + small label; for stars/installs/users/$ (round 3: hananazeez.ai) — Data / Clean Tech / any — not yet used.
- `hand-annotate.html` — hand-drawn circle + arrow + handwritten label that draws itself onto the real frame, pointing at a real object (round 3: iamsarahsnow) — Notebook / Studio Kinetic / any (needs the Caveat font) — not yet used.
