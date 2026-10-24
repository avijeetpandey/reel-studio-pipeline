# Motion, design, captions and camera — how to make it look made by a great editor

## The motion brief (write one per graphic beat, before coding it)
Four parts, in this order:
1. **What & where:** "A 2.6 s lower card for a 30 s talking-head reel, 1080×1920, over the chest area, while the creator says '…'."
2. **Look:** treatment name + exact hex colours, fonts and sizes, surfaces (from `treatments.md`), and the real asset it uses.
3. **Beat by beat with seconds:** "0.00–0.30 card slides up 24 px and fades in; 0.30–1.10 the word 'token' is circled in red pen; 1.10–2.30 holds; 2.30–2.60 slides down and out."
4. **Rules:** "max 6 words on the card; the number is always in the accent; nothing touches the face box; no bounce; nothing smaller than 34 px."
Then add the treatment's **feel paragraph** verbatim. Describe feelings like a director, and translate them to code yourself:

| Say (feel) | Means in code |
|---|---|
| "settles like a page landing on a desk" | `power3.out`, 0.35–0.45 s, 16–24 px travel, tiny overshoot ≤ 2% |
| "pops like it's excited to be there" | `back.out(1.6)`, 0.25 s, scale 0.85 → 1 |
| "has weight" | longer ease-out, no elastic, shadow grows as it lands |
| "drawn, not flown in" | SVG stroke-dashoffset draw, 0.4–0.7 s, `power1.inOut` |
| "types at reading speed" | ~14–18 characters/s, cursor blink 0.5 s |
| "counts up" | number tween with `snap`, 0.6–1.0 s, `power2.out`, tick SFX every few steps |
| "calm exit" | exits are faster than entrances (0.2–0.25 s), fade + 8–12 px drift |

## Design rules (what separates pro from amateur)
- **Three-object rule:** one main object in the centre of the card, supporting elements at its edges, small depth elements (dots, faint lines, labels) around the outside. Not ten things competing.
- **Make every element ~25% smaller than first instinct.** Big icons and huge shapes scream beginner. Minimum text 34 px, headline 64–96 px.
- **Fewer effects = each one feels special.** One signature move per reel; everything else is plain fades, slides and draws.
- **Muted colours look high-end:** dull blues, slate, teal, sand, off-white. Avoid pure #000/#fff fills and bright pure red; the accent is the only saturated colour.
- **Real assets:** screenshots or recordings of the real app/page beat any drawn icon. Use `npx hyperframes capture <url>` or the creator's own recordings; crop tight; put them in a clean card (radius 20, 1 px border, soft shadow) — no fake device mockups unless the treatment needs them, and never a cheap-looking phone frame.
- **Check the registry first:** before hand-building a named effect (chart, terminal, counter, map, glitch), search `hyperframes-registry` (`npx hyperframes catalog`) and adapt a block to the treatment.
- **Content block:** put every word, number and colour a graphic uses in one JS object at the top of the composition (`const CONTENT = {…}`) so a change is a one-line edit.
- **Optional finishing for full-screen graphics (FG):** a subtle edge-only chromatic fringe or vignette blur on the corners — never on the centre, never on the face.

## Captions
- **Learned from the reference reels (`$STUDIO/template/WINNING_PATTERNS.md` §4):** in split/PiP scenes use the seam caption (2–3 words, uppercase mono/bold sans in a dark box on the seam between graphic and face); in talking-head reels the hook may run as **one huge word at a time** (≈ 140 px, key word in the accent) for the first 2 s, then switch to the normal captions. One meaning-word per headline may be *italic serif* (the treatment decides).
- Word-by-word pop (scale 0.96 → 1, 0.12 s), ≤ 3 words per chunk, break on punctuation, **punctuation never shown**, **never end a chunk on a weak word or single letter** (the template enforces both).
- Position: y ≈ 1230 (inside the safe box), never over the face; move above a **TL** card or hide during it.
- **One highlighted word per chunk at most** — the word that makes you keep watching (the noun or number that carries the idea). Highlight style comes from the treatment.
- Spell brand names correctly (ChatGPT, Claude, LLM, UPI) — fix the transcript before building captions.

## Camera & face dynamics
- **Framing check first:** eyes in the top third, head horizontally centred (± 40 px). If the source framing is off, reframe with a scale/translate on `#cam` per shot from `geometry.json`.
- **Punch-ins are motivated:** alternate 1.00 / 1.06 at jump cuts (hides the cut), one 1.12–1.15 punch on the key term or the twist, a slow 1.00 → 1.06 push-in during an emotional/serious line, and a slow 6% **zoom-out** during long talk stretches (> 4 s with no graphic). No zoom on a timer.
- **Split (SP):** face scaled to fill the lower half, head centred; the graphic owns the top half; a 2 px divider or a soft gradient seam — never a hard black bar.
- **Text behind head (TB):** cut the creator out with `hyperframes:embedded-captions` (local matting) or `npx hyperframes remove-background`; place the word between background and cutout; dim the background 30–40%; check the cutout edges at full size (hair, shoulders) — if edges look rough, don't use TB in this reel.
- **Take selection:** when two takes are equally clean, prefer the one where they look into the lens and has more energy.
- **Lower card (TL):** darken + blur only the region behind the card, never the face.

## B-roll
- Sources, in order: the creator's own recordings (`broll/` and the b-roll index `$STUDIO/broll/INDEX.md` when it exists), real page captures, real screenshots. AI-generated b-roll only if the creator asks.
- Each b-roll shot: 1.2–3 s, hard cut in and out, covers any nearby jump cut (planning rule 7), matches the exact meaning of the line.
- Footage shot in a log profile (S-Log, D-Log) → convert to Rec.709 + gentle contrast before use.
- After the reel, add any new b-roll/screen recording to `broll/INDEX.md` (file, what it shows, keywords, length) so future reels reuse it.

## Layouts and life in the frame (from the reference reels)
- **Proof on screen at frame 0** next to the face (the real page, the result, a diagram already moving) — never a blank band.
- **Split (SP)** is the default for lists and tool demos; **PiP** (diagram 70 %, face in a rounded box at the bottom) for diagram-heavy explanations; full-graphic cutaways 2–4 s.
- **Something visibly changes every 1–3 s** inside a graphic beat: a node appears, a tick lands, a counter rises, a cursor clicks. A graphic that sits still for > 2.5 s gets a small state change or ends.
- **List reels:** pinned list title or the `step-progress` stepper for the whole list; the strongest item last after an open-loop line; an optional 1.2 s fast recap of all items right before the CTA (people pause or re-watch to read it).
