# Beat map — plan every line before building anything

Changing the plan costs nothing; changing a finished graphic costs a lot. Write `EDIT_PLAN.md` (beat map) after the cut and face map, and check it against the rules below before any composition code.

## Scene types (one per line of the script)
| Code | Scene | Layout | Use for |
|---|---|---|---|
| **T** | Talk | Face + captions only | Breathing room, personal lines, the twist, the CTA question |
| **TC** | Talk + top card | Card in the graphics band (y 250 → ≤ 700) above the face | A term, a number, a short visual |
| **TL** | Talk + lower card | Card over the chest area (y ~1000–1400); only the area right behind the card darkens 35% and blurs 12 px; captions move above or hide for that beat | UI moments (a notification, a chat bubble, a setting) — "small things that pop up while I talk" |
| **SP** | Split | Graphic fills the top half (0–960), face scaled into the bottom half, framed head-and-shoulders, head horizontally centred | A visual that needs room while my face stays on (comparisons, diagrams) |
| **FG** | Full graphic / b-roll | Real b-roll / real screen recording full screen, voice continues; max 3 s. **Never typography or a full-screen graphic that replaces the creator's face (variety.md §0.1)** | The money visual, real screenshots/recordings, covering a jump cut |
| **TB** | Text behind head | Big word/number behind the creator's cutout, background dimmed | One signature moment (hook or twist), Cinematic Cutout treatment or once per 3 reels otherwise |

## Rules
1. **One graphic per idea, not per sentence.** A 30 s reel usually has 4–6 ideas → 4–6 graphic beats.
2. **Hold long enough to read:** on-screen time ≥ max(1.2 s, 0.3 s × words + 0.6 s). Nothing flashes for < 0.8 s (except the 0.55 s hook words).
3. **Never two cards at once.** A new card replaces the old one.
4. **Breathing room:** after every 2 graphic beats, at least one **T** beat. The twist line is always **T** (face, close, calm).
5. **Variety:** no scene type more than 2 times in a row; at least 3 different scene types per reel; at most one **TB** per reel.
6. **Something changes every 2–4 s** — but motivated by the words: a scene change, a punch-in on emphasis, a card, or b-roll. Never a zoom on a timer.
7. **B-roll covers cuts:** if a jump cut lands within 0.6 s of a b-roll edge, extend the b-roll over the cut. The face must never flash for under 0.6 s between b-roll and a cut.
8. **Hard cuts into b-roll**, no whoosh transitions on b-roll. Motion transitions are for graphics, not footage.
9. **Real over generic:** whenever a product, app, document, site, number or person is named, the visual is the real thing (screen recording, `hyperframes capture`, real screenshot, real logo) — Google-Docs-looking doc, real YouTube Studio, real LinkedIn feed — never a generic icon or stock "analytics chart". Pick visuals from the meaning of the whole line, not a keyword (a "cut" in editing is not a knife).
10. **Tease:** if the reel has a payoff visual later, consider flashing 0.8 s of it right after the hook (a "here's where we're going" glimpse) — only if it doesn't spoil the twist.
11. Plan **2+ deliberate quiet moments** (no new graphic, no SFX) — usually the twist and right before the CTA.

## EDIT_PLAN.md format
```
Treatment: Notebook (last 2: Clean Tech, Data)   Signature move: red-pen circle on "token"
Accent: #3ee0ff   Caption highlight: yellow marker   Music mood: warm lo-fi (INDEX: …)

| # | Time | Line (exact words) | Scene | Visual (real asset / graphic idea) | Component (`enhance.md`) | Motion feel | SFX | Hold |
| 1 | 0.0–2.1 | "ChatGPT doesn't know your answer." | T + hook words | hook words "DOESN'T KNOW" top band | roll-text | words snap in, settle | sub hit at 0 | — |
| 2 | 2.1–5.4 | "Think of your phone's autocomplete…" | TL | real iOS keyboard suggestion bar screenshot, lower card | pop-blur | slides up like a keyboard | soft pop | 2.6 s |
…
Quiet moments: #6 (twist), #8 (before CTA)
Assets needed from the creator: (none) / screen recording of X
```
Check every row against rules 1–11 before building. List the assets the creator must supply at the checkpoint (or use real captures).

## Build order
1. Build the **hero beat** first (the most complex graphic), snapshot it, compare with the treatment's look and feel, fix.
2. Build the remaining graphic beats (in parallel with helper agents when there are 3+ — see SKILL.md), then assemble.
3. Snapshot one frame per beat (`npx hyperframes snapshot --at <mid-times> --no-end`) = the storyboard; check it before animating details.
