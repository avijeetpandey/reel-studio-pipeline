# Treatments — so no two reels look the same

A reel = **brand constants** (never change) + **one treatment** (changes per reel, chosen from the content) + **scene mix** from the beat map (`planning.md`).
**Autonomous:** `T/scripts/choose_style.py` applies this section for you (scores the ten treatments from the content, enforces the rotation, picks the signature move). Pick the treatment in step 3 from the topic, the script's format and its analogy. Then check `$STUDIO/reels/style_log.md`: **never the same treatment as either of the last 2 reels**, and never the same signature move as the last reel. Log the choice after the render.

## Brand constants (every reel, every treatment)
- Frame 0 = the creator's face already speaking the hook (see SKILL.md). Hook words in the top band.
- Caption system: word-synced, ≤ 3 words, one highlighted word per chunk max, no punctuation shown, never ending on a weak word. Alternative for calm Notebook / Editorial Split reels: **karaoke reveal** (round 4): the whole short line sits at 35 % opacity and each word lights up as it's spoken, serif or the treatment's font. Font: Montserrat 900 + 10 px stroke (default) — a treatment may swap the *highlight* style, never the readability.
- One accent colour per reel. Default brand accent cyan `#3ee0ff`; a treatment may use its own accent but only one.
- Sign-off: CTA card with the yes/no question + "{brand}", shown WHILE the question is spoken; the video ends ≤ 0.5 s after the last word (no hold) so it loops into the hook.
- Audio: voice first, −14 LUFS final, music bed under voice (see `sound.md`).
- Safe box x 60–930, y 250–1420. Face never covered.

## The ten treatments

### 1. Clean Tech (default for "how AI works" with a system/flow)
- **Use for:** mechanisms, pipelines, "what happens when…", architecture.
- **Look:** deep navy-black surfaces `#0a0f18` at 78% opacity, 2 px cyan hairline borders, radius 28–32, JetBrains Mono for numbers/labels. Dull secondary colours only (slate `#7d8ba6`, muted teal `#5fb3b3`); no pure white panels, no red except for "wrong".
- **Feel (write this into every motion brief):** "Precise and calm, like a well-made developer tool. Cards glide in from 20 px below and settle with weight; nothing bounces more than once. Lines draw themselves left to right. Numbers count up, never just appear."
- **Signature moves (pick 1–2):** a flow diagram that builds node by node; a terminal card typing a real command; a token/vector strip that splits apart.
- **Captions:** default (white + cyan key word).
- **SFX palette:** soft whooshes, UI clicks, key-press, line-draw. **Music:** light electronic, low.

### 2. Notebook (matches the carousels — explainers with an everyday analogy)
- **Use for:** analogies, "explained like I'm 10", glossaries, myth vs fact, career advice.
- **Look:** cards are off-white paper `#FAF9F6` with a faint dot grid, ink `#17191E`, a yellow highlighter swipe behind the key word, red-pen handwritten notes (Caveat) with hand-drawn arrows/circles/underlines. Cards sit slightly rotated (−1.5° to 1.5°), taped corners optional.
- **Feel:** "Like I'm sketching it for you on a notepad. Things are drawn, not flown in: underlines draw, circles scribble around a word, arrows swing in. Paper cards slide in like being placed on a desk."
- **Signature moves:** a word gets circled in red pen as I say it; a highlighter swipes across a phrase in sync with the voice; a hand-drawn arrow points from the card to my face.
- **Captions:** default, but the highlight word gets a yellow marker block instead of cyan.
- **SFX palette:** pen scribble, paper slide, pop. **Music:** warm lo-fi / acoustic, very low.

### 3. Newsroom (Headline Decoded, news reactions, "OpenAI just…")
- **Use for:** news, announcements, claims vs facts, AGI-type debates.
- **Look:** real headline screenshots (`hyperframes capture`) in clean white cards with a thin black rule, date stamp in mono, source label; one red accent `#d2412b` for "breaking"/the claim, charcoal type, serif for quoted headlines (Source Serif 4) + Montserrat for everything else.
- **Feel:** "Calm newsroom, not hype. Headlines slide up like paper being pulled from a printer; the key sentence gets a highlight sweep; numbers are set like a data table."
- **Signature moves:** headline screenshot with the key line highlighted; "claim vs reality" split card; a stamp ("UNVERIFIED", "62.7%") lands with a soft thud.
- **Captions:** default, highlight in the red accent.
- **SFX:** paper slide, typewriter key, soft hit. **Music:** minimal pulse, tense but quiet.

### 4. Terminal (dev-adjacent topics told for everyone: agents, Claude Code, prompts)
- **Use for:** prompts, agents, coding tools, "what the AI actually does".
- **Look:** a real-looking terminal / chat UI card (dark `#0d1117`, mono 30–34 px, green/amber prompt colours), real app chrome copied from screenshots, cursor blink. Everything else is the face.
- **Feel:** "Like watching over my shoulder. Text types at reading speed, the cursor blinks while I talk, output scrolls in line by line, a highlighted line pulses once."
- **Signature moves:** typed prompt → answer streaming; a tool call expanding into steps; before/after prompt split.
- **Captions:** default; keep the caption band away from the terminal card.
- **SFX:** key-press, soft click, notification. **Music:** minimal electronic.

### 5. Data (stats, money, jobs numbers, energy, benchmarks)
- **Use for:** any reel built on 2+ numbers.
- **Look:** big numerals (Montserrat 900, 160–220 px) in the accent, bar/line charts drawn with 4 px strokes, light grid, source line in mono 22 px. Muted chart palette (slate, teal, sand) with the accent only on the one number that matters.
- **Feel:** "Numbers count up and land with weight; bars grow from the baseline in a staggered wave; the important bar is the only one in colour."
- **Signature moves:** count-up to the key stat; two bars racing (claim vs reality); a stat that shrinks to 25% and slides into a corner while I keep talking.
- **Captions:** default; numbers in captions use the accent.
- **SFX:** ticks during count-up, soft hit on landing, riser before the big number. **Music:** modern, steady.

### 6. Cinematic Cutout (big emotional or contrarian claims; max once every 4 reels)
- **Use for:** hot takes, career fears, story reels.
- **Look:** a huge word or number **behind the creator** (person cutout via `hyperframes:embedded-captions` / `npx hyperframes remove-background`), background dimmed 30–40% and slightly blurred so he pops; warm grade; one accent.
- **Feel:** "Like a film title card that I'm standing in front of. The word slides in behind me slowly, the room darkens a little, everything is slower and heavier."
- **Signature moves:** text-behind-head on the hook or twist; background dims as I say the twist; slow push-in.
- **Captions:** default, slightly smaller; hide captions while the big word is on screen if they'd repeat it.
- **SFX:** sub-bass hit, long whoosh, then silence. **Music:** cinematic pad, swell into the twist.

### 7. Editorial Split (lists and "how it works" with real proof — learned from the reference reels, Oct 2026)
- **Use for:** numbered lists ("3 tools nobody uses"), tool demos, step-by-step how-tos, anything where the proof is a screen.
- **Look:** split screen — the graphic/screen owns the top ~45 % on warm off-white paper `#F4F1EA` (or graphite `#16181d` for a dark variant), the creator's face fills the bottom ~55 % (head centred); a thin seam with the caption sitting on it. One terracotta accent `#D9734E`; titles in a serif (Source Serif 4) with ONE italic accent word, labels in JetBrains Mono, cards white with radius 20 and a soft shadow. Kicker "TOOL 2 OF 3" + stepper (`step-progress` component) and a giant serif numeral when the number is said.
- **Feel:** "Calm, editorial, product-grade. Diagrams build node by node, ticks appear as each step completes, real screens slide up into the top half and settle. Something small changes every 1–3 s."
- **Signature moves:** stepper + big serif numeral per item; a node diagram that grows from one node to a tree; the real product doing the task with one red-pen circle on the result.
- **Captions:** 2–3 words, uppercase mono, white on a near-black box, sitting on the seam (not the default stroke style).
- **SFX palette:** soft click per tick, paper slide on cards, pop on the numeral. **Music:** calm modern / lo-fi, low.

### 8. Studio Kinetic (opinion, career, motivation, frameworks — look B, round 2 Oct 2026)
- **Use for:** hot takes, career advice, identity reframes, mantras, frameworks told to camera.
- **Look:** the footage carries it — dark warm grade (lift shadows slightly, teal shadows / warm skin), practical-light bokeh; **small single-word white captions** at chest height most of the time; 2–4 **giant kinetic headline moments** (heavy condensed sans + one italic script word, white/yellow) that build word by word in the top third; optional bottom progress track for frameworks.
- **Feel:** "Calm, confident, cinematic — the words land like a film title, then get out of the way."
- **Signature moves:** headline that builds word by word; a framework bar/track that fills as each part is named; one slow push-in on the key line.
- **SFX:** soft whoosh on headline builds, one deep hit on the turn. **Music:** dramatic/cinematic or funky bed, low.

### 9. Fact-or-Hype Reaction (series — look D)
- **Use for:** testing a viral AI claim/tool live.
- **Look:** pinned white pill "Fact or Hype?" top; the claim clip (or its headline/post screenshot) in a PiP card with the creator beside it in a skeptical pose; then the real screen test with a bottom checkbox bar `☐ FACT  or  ☐ HYPE`; the verdict box ticks with a hit; captions 2–3 words, yellow key word.
- **Feel:** "Honest test-drive: skeptical, curious, then a clear verdict."
- **Signature moves:** checkbox verdict tick; a live counter (time / credits used / result) during the test.
- **SFX:** click on checkbox, success/error on verdict, whoosh into the screen test.

### 10. Halftone Collage (opinion, strategy, "why most people…" — round 3, Oct 2026)
- **Use for:** strategy and mindset takes, "why X gets you ignored", before/after arguments, short punchy reels (11–25 s).
- **Look:** a light grey `#E6E5E3` desk with a white card or paper sheet holding the frame, drop shadows like real paper; **black-and-white halftone cutouts** (vintage people, hands, objects; public-domain or self-shot, run through a halftone filter); ONE flat yellow block `#F2C230`; heavy condensed sans for the key word with a tiny lowercase kicker on it ("no / plan", "but with / strategy"). the creator's face sits in a torn-paper or rounded cutout window for most of it; the collage owns 2–4 beats.
- **Feel:** "A zine being assembled on the beat: pieces slide in from off-card and stop dead with a hard shadow; a yellow block wipes across; nothing floats or glows."
- **Signature moves:** a halftone figure acts out the line (falls, climbs, runs from a clock); a yellow block wipes in behind the key word on the beat; Raw | My Edit side by side for the twist.
- **Captions:** small black condensed on white paper strips (no stroke), key word bigger.
- **SFX palette:** paper slap, scissors snip, stamp. **Music:** punchy hip-hop / funk, cuts land on the beat.
- **Never:** colour stock photos, gradients, glow, emoji. Halftone assets must be public-domain, CC0 or the creator's own photos (note the source in the edit plan).

## Style DNA (optional, makes it unmistakably the creator's)
If `$STUDIO/template/style-dna.md` exists, read it before choosing: it lists 3–5 reels the creator loves (links + what they likes in each — captions, motion, colour, pacing). Borrow one element from each, never copy one creator whole. If it doesn't exist, mention once at the checkpoint that 3–5 reference reels would sharpen the style.
