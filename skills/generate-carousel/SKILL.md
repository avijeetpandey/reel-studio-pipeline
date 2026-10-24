---
name: generate-carousel
description: Generate a ready-to-post {brand} (@{handle}) Instagram/LinkedIn carousel from a topic, a playbook ID (C01–C30) or the creator's own slide-by-slide descriptions — format choice, hooky plain-English copy, 1080×1350 slide images in the natural "engineer's notebook" look (paper, one ink, highlighter, red-pen notes, their real face — never AI-looking), QA, caption + alt text + pinned comment, a LinkedIn PDF, approval, then Drive upload. Built to earn likes, saves, shares, a comment and a follow. Use whenever the creator asks for a carousel, slides, a swipe post, a LinkedIn document post, or "make C07".
---

# Generate carousel ({brand})

> **Setup first.** These values come from `~/.config/reel-studio/config.json` (written by the `studio-setup` skill — run it if the file is missing):
> `$STUDIO` = `studio_dir` (your working folder: `template/`, `reels/`, `carousels/`, `research/`) · `$PLUGIN` = `plugin_root` (this plugin) ·
> `{brand}`, `{handle}`, `{creator_name}`, `{drive_remote}`, `{drive_folder}` = the matching config keys. Channel rules, approval gates,
> posting slots and timezone live in `$STUDIO/CHANNEL_RULES.md` — they override any default numbers written below.

Follow every step in order. The channel rules and approval gates in `$STUDIO/CHANNEL_RULES.md` apply on top.
`T = $STUDIO/template/carousel/` holds the code: `deck.html` (all layouts), `render.sh` (PNG/JPG + PDF + contact sheet + QA), `assets/` (`avatar-cartoon.png` = the header/follow avatar set during studio setup — bring your own), `examples/sampler/slides.js` (every layout once — copy patterns from it).
Read `$STUDIO/template/WINNING_PATTERNS.md` §9 (carousel patterns from the reference posts) first. References in this skill folder: `formats.md` (slide recipes per format + which calendar IDs use them) and `copy.md` (hooks, flow, CTAs, banned words, worked examples). Read both before writing.
Work in `$STUDIO/carousels/<carousel_name>/` (snake_case, e.g. `c02_15_ai_words`). Playbook (calendar, outlines): `$STUDIO/{handle}-content-plan.html`.

**Pipeline mode:** when `make-content` runs this skill (the carousel folder is `reels/<reel_name>/carousel/` next to a `pipeline.json`), do steps 1–7 only: no checkpoint, no upload — stop after `caption.md` and report the QA result + contact-sheet path. `make-content` merges the review into its checkpoint 1 and uploads with `pipeline.py upload … half1`.

## What every carousel must earn — and which slide earns it
| Goal | Earned by |
|---|---|
| **Like** | A cover that names something the viewer has felt or wondered (relatable claim, their face), and slides that pay it off fast. |
| **Save** | A slide worth coming back to: recap, checklist, template, framework, glossary. Label it with the red-pen note "screenshot this" / "save this one". |
| **Share** | The final slide names a *specific* person to send it to ("the friend who trusts ChatGPT with everything"). Safe Mode → family; Career → a job-hunting friend. |
| **Comment** | One debatable **yes/no question** on the final slide and in the caption — never "comment KEYWORD". |
| **Follow** | The author header on every slide (a person, not a brand), the series name, and the follow card's promise ("I decode one AI thing every day"). Series consistency is what makes a follow make sense. |

## Autopilot
Run steps 1–7 without questions, taking the defaults. Stop once at the checkpoint (step 8). If the creator gave slide-by-slide descriptions, they are the plan: keep their order and content, only tighten words and pick layouts. If something essential is missing (a screenshot only they can take), use the best available substitute and list it at the checkpoint.

## 1. Brief
- Input is a topic, a playbook ID (read its title, format and slide outline from the playbook file), or the creator's per-slide descriptions.
- Decide: **format** (from `formats.md`), **series** (your series names from CHANNEL_RULES.md), **the one promise** of the carousel in one sentence ("After this you'll know 15 AI words well enough to explain them"), **the fix or takeaway**, **who it's for**, and **who they'd send it to**.
- **Pairing with a reel:** if a reel on the same topic exists or is planned (calendar pair, or a folder in `$STUDIO/reels/`), read its `script.md` and reuse its claim, analogy, **fix** and yes/no question word for word where they fit, so the two posts reinforce each other. Reuse its real assets instead of re-capturing: screen recordings in `broll/`, captured pages in `work/cap*`/`assets/`, and the cover cutout `work/cover/cutout.png` (fresher than the default photo). Copy what you use into `<carousel>/assets/`.

## 2. Facts
Quick web check of every number, date and claim; prefer primary sources. Anything single-sourced gets softer wording ("one study found"). Put the source on the slide (`source:` field, small mono line) when a number appears. Never invent screenshots, quotes or stats.

## 3. Copy (the part that decides everything — follow `copy.md`)
- **Everyday-tech explainers make strong carousels** (round 4: "How do VPNs work?" 297K as a reel): one slide per step with its everyday analogy, then a "what it does NOT do" slide (the honest caveat) before the CTA.
- **The viewer's problem first, the tool second** (`WINNING_PATTERNS.md` §16, round 3): the cover names the reader's pain or goal ("Your ChatGPT forgets everything — 5 fixes"), not the tool's feature list. Retired cover shapes: "you're using X wrong", "master X in one weekend".
- **Patterns from the winners (`WINNING_PATTERNS.md` §9):** cover = number + benefit + time frame ("7 ChatGPT settings you can fix in 5 minutes"); slide 2 = proof or the promise paid off at once; for lists a **roadmap slide** ("there are 5 steps: 1)…5)") then one item per slide in the **recipe** shape (item number in the accent · name · one-line outcome · a real screenshot with one red-pen circle · the tools as small logos joined by "+"); the yes/no question appears once mid-carousel (~60 %) as a slim strip and again on the last slide; every slide's footer says "save for later".
- 6–10 slides. Slide 1 cover, slide 2 delivers the promise immediately, one idea per slide, a surprise in the middle, **a fix slide** (one concrete thing to do today — a setting, a sentence to type, a check; red-pen note "save this"), recap/save slide near the end, CTA last. Every carousel has a fix slide; in how-to/checklist formats the steps themselves are the fix.
- Cover headline 5–12 words, plain-English claim, no jargon unless the jargon IS the topic. Content headlines ≤ 8 words. Body ≤ 25 words per slide (glossary/checklist slides may run longer — QA enforces caps).
- Voice: the creator, first person, the creator (their role from CHANNEL_RULES.md) talking to a smart friend. Short sentences, contractions, daily-life Indian examples that also make sense abroad. Every slide should make the next one feel necessary (see "flow" in `copy.md`).
- Marks, used sparingly (≤ 1 highlight and ≤ 1 pen note per slide): `==highlight==` for the key word, `__underline__`, `((circle))`, `**bold**`; `note:` for one red-pen margin note.
- Read every slide aloud. If you wouldn't say it to a friend over chai, rewrite it. Run the banned-words list.

## 4. Build `slides.js`
`window.DECK = { id, series, theme: "paper" (default) | "ink", paper: "dots" (default) | "ruled" | "plain", slides: [...] }`. Layouts (`type`) and their fields — copy shapes from `T/examples/sampler/slides.js`:
`cover {kicker, title, sub, note, photo, swipe}` · `statement {kicker, title, body, note, size:"xl"}` · `point {n, kicker, title, body, eg, image, note}` · `steps {kicker, title, steps:[{label, text, hot}]}` · `compare {title, left:{head, points}, right:{head, points}}` · `myth {n, myth, fact, body}` · `checklist {title, items:[{text, small}]}` · `glossary {kicker, terms:[{term, def, eg}]}` (2–3 terms) · `story {stamp, text:[...]}` · `stat {kicker, number, title, body}` · `timeline {title, events:[{when, text, hot}]}` · `screenshot {title, image, body, note}` · `template {title, copy}` · `recap {title, items}` · `cta {question, yn, share, follow}`. Any slide may add `source`.
- **Cover visual:** never a wide, low-quality cutout of the creator sitting at a desk (it reads as cheap) or a frame grabbed from a seated video.
  - Default: a **no-photo topic cover** — `cover` with `tags: [...]` (the topic's terms as paper tags; `lit: [i]` highlights one, `circle: i` circles one in red pen, `ghost: [i]` for a muted "+7 more"), or a real screenshot / object that *is* the topic. The headline should challenge or promise ("You've heard all 15. Can you explain them?").
  - Photo covers only from the **cover photo pack** in `T/assets/photos/` (when it exists): tight head-and-shoulders, plain background, good light, an expressive pose (pointing at the headline, eyebrows up, holding the phone with the app on screen). Pick the pose that matches the headline.
  - The small round avatar in the header stays on every slide: `assets/avatar-cartoon.png` (the image chosen in studio setup). Any new avatar or image swap: show the creator first, re-render only after they approve.
- Screenshots: real pages only (`npx hyperframes capture <url> -o cap --skip-vision --skip-assets --max-screenshots 3`) or the creator's own screen; crop tight; put files in `<carousel>/assets/`.

## 5. Render + QA loop
`bash T/render.sh $STUDIO/carousels/<name>` → `out/slide-XX.png|jpg`, `out/<name>-linkedin.pdf`, `out/sheet.jpg`, `out/grid-check.jpg`, `out/qa.json` (printed). Fix every QA issue by **cutting words, never by shrinking type**, and re-render until it says "all slides pass".

## 6. Look at it like a viewer (mandatory — open `out/sheet.jpg` and at least the cover + 2 slides at full size)
- Cover: readable at thumbnail size? Claim clear in 1 second? Face visible? `grid-check.jpg` (3:4 profile crop) keeps the headline intact?
- Does it look made by a person? Paper, one ink, at most one highlight + one pen note per slide, consistent margins and header on every slide. **No** gradients, glow, neon, glassmorphism, 3D icons, emoji bullets, stock/AI illustrations, rainbow colours, more than the built-in fonts. Don't add CSS effects to "make it pop".
- Rhythm: layouts vary (don't run 5 identical slides in a row unless it's a glossary/list format), but the system stays the same.
- Flow: read slides 1→N quickly — each one pulls to the next? Slide 2 pays off the cover?
- Fix, re-render, re-check once.

## 7. Posting kit — write `caption.md`
- **Instagram caption:** line 1 = hook + the search keyword (≤ 125 chars so it shows before "more"); for list carousels the **whole list as numbered text** (1️⃣ … one line of benefit each — searchable and it answers "where do I find these?"), otherwise 2–4 short lines of value; one trust line ("real tips, no hype" style, in their words); an **SEO keyword line** at the end of the caption (3–5 plain search phrases separated by " · ", WINNING_PATTERNS §15); a save line ("Save this for …"); a send line naming the person; the yes/no question; 3–5 hashtags (3 on-topic + up to 2 broader tech; never #ai #fyp #explorepage).
- **Alt text** for each slide (one plain sentence of what it says).
- **Pinned first comment:** the sources + the question again.
- **Music:** add a calm, instrumental track from Instagram's library when posting (reportedly lets carousels surface in the Reels tab — unverified; free to test).
- **Schedule:** Instagram 9:00 AM (your timezone) on its calendar day (Mon/Wed/Fri); never within 12 h of another Instagram post; never 11 PM–9 AM.
- **LinkedIn:** upload `out/<name>-linkedin.pdf` as a document post; caption = 2-line hook, 3–5 short lines in the creator's professional voice (no your employer internals), one question, 3 hashtags; links in the first comment.
- After posting: reply to every comment in the first hour; reshare to Story with a yes/no poll sticker.

## 8. Checkpoint (one message)
Show `out/sheet.jpg` (and the cover full size), the caption, and the list of choices made (format, cuts, substitutes). the creator replies "approved" or asks for changes → fix only the named slides, re-render, show the changed slides, ask again.

## 9. Upload — only after the creator approves
rclone `{drive_remote}:` → **always a NEW subfolder** `{drive_folder}/<carousel_name>/`, never into `{drive_folder}` itself:
```bash
rclone mkdir "{drive_remote}:{drive_folder}/<carousel_name>"
rclone copy "<dir>/out" "{drive_remote}:{drive_folder}/<carousel_name>" --include "slide-*.jpg" --include "*.pdf" -P
rclone copyto "<dir>/caption.md" "{drive_remote}:{drive_folder}/<carousel_name>/<carousel_name>_caption.md" -P
rclone lsl "{drive_remote}:{drive_folder}/<carousel_name>"
```

## 10. Log, revisions and learning
- After approval, append one line to the **Carousels** table in `$STUDIO/reels/style_log.md`: date, carousel, format, layouts used (in order), paired reel. Before building the next carousel, read the last 3 lines: don't open with the same cover style twice in a row, and vary the layout mix (no identical layout sequence to the previous carousel).
- For **every** note the creator gives (specific or general): fix it, then ask "which instruction would have prevented this?" and write that rule into this skill, `copy.md`, `formats.md` or `T/deck.html` (add a QA check in `deck.html` when it can be automated), so every future carousel gets it — and tell them what changed.
- After a carousel's 48 h numbers come in (saves, shares, profile visits), note what worked in `formats.md` under that format.
