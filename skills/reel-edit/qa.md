# Self-check — catch everything before the creator sees it

Run all of this after the build and again on the final render. Fix, re-run, and only then show the checkpoint. Look like a viewer, not a computer.

## Automated
1. `npx hyperframes check --snapshots` → 0 errors (layout overlaps, text off-canvas, contrast, runtime).
2. `npx hyperframes check --caption-zone "x0=0;y0=0.74;x1=1;y1=1;severity=error"` and `… "x0=0.86;y0=0;x1=1;y1=1;severity=error"` → nothing in Instagram/YouTube UI zones (bottom 500 px, right 150 px).
3. `python3 -I T/scripts/qa_reel.py <composition_dir> --segments <reel>/segments.txt --geometry <reel>/work/geometry.json` → checks:
   - **flash:** any graphic/b-roll clip on screen < 0.8 s
   - **read time:** text on screen shorter than 0.3 s × words + 0.6 s
   - **face flash:** a jump cut within 0.6 s of a b-roll edge (extend the b-roll over the cut)
   - **face box:** runs `check --caption-zone` with each shot's face box from `geometry.json` → no text over the face
   - **enhance budget:** more than 2 heavy components (swing-window/code-window), two overlapping, roll-text over 4 words (reads `data-component`)
   - **scene variety:** same scene type > 2 in a row, < 3 scene types, missing breathers (reads `data-scene` attributes)
4. **Transcript re-check** on the cut (before building) and on the final: `python3 -I T/scripts/qa_reel.py --audio <file.mp4>` re-transcribes word-level and flags a **word/phrase said twice** within 3 s, filler words (um, uh, like-as-filler, basically, so-as-opener), pauses > 0.25 s between words, a tail > 0.8 s after the last word (end ≤ 0.5 s after it), a clipped first/last word, and lists brand names to verify spelling.
5. **Beat check:** `python3 -I T/scripts/beat_grid.py <composition>/assets/audio/bgm.mp3 --offset <bed start> --check <composition_dir>` → apply every `SNAP` suggestion that keeps the entrance ≤ 0.1 s before its word (round 4: "lock every cut to the beat"); big moments on bar lines.
6. Frame 0 gate and A/V: first frame shows the face (snapshot at 0 and 0.25 s), voice starts ≤ 0.1 s, audio and video streams both start at 0 (`ffprobe -show_entries stream=start_time`).

## Enhance pass (see `enhance.md` §4)
Every component passes the earn-it test, lands on its spoken word, survives a backwards seek, and matches the treatment. Failures are fixed or removed.

## Reference-reel checks (WINNING_PATTERNS.md)
- `qa_reel.py` warns when a graphic beat holds still for long stretches (no clip starts/ends for > 4 s while no camera move is planned) and fails a near-blank cover (`--cover`).
- By eye: proof is on screen at frame 0 beside the face; lists show progress (stepper/pinned title); the CTA card is in the safe box and ends before the loop overlay.

## Frame grading (round 4 — "make it watch its own frames")
Sample one frame per second (`T/scripts/sample_frames.sh final.mp4 work/grade 1`) and look at **every** frame full size. Score each 1–10: is the face clear and well lit, is the text readable and placed on purpose, would a human editor have made this frame? Any frame **< 8** gets fixed (re-place, simplify, re-time) and re-graded. A **dead frame** (nothing changed for > 4 s and no camera move) counts as a 6. Write the scores into the checkpoint's QA report (min, median, every frame < 8 and what changed).

## AI-slop tells (round 4 — fail the reel if any is present)
All-caps centred text on a gradient · glow/neon on everything · 3D or cartoon versions of real people · "FREE FOREVER"-style stickers · more than one decoration on a beat · emoji labels · a template look nobody would choose by hand. The four most decorated reference reels got the fewest likes.

## the creator's taste checks (24 Oct 2026)
- Play the first 3 s of the music alone: is it energetic? If not, re-trim or re-pick.
- Last 4 s at full size: is it the best-looking frame of the reel? If not, redo the ending.
- Count on-screen emojis (≤ 1) and overlay beats (no more than ~1 designed moment per 6–8 s); would a human editor have made this, or does it look templated?

## By eye (contact sheet of 24 frames + full-size frames at every beat)
- An animation that **plays twice** or restarts.
- A graphic that **appears late** for its line (lands after the word is said) or leaves before the line ends.
- **Face covered** by anything, or cut off by a split.
- **Head not centred** in split or reframed shots (check 3 frames per shot).
- **Lips drifting** from the voice (watch 3 spots at full speed with sound).
- Cards touching the safe-box edges, text widows, cheap-looking mockups, rough cutout edges.
- Rhythm: read the beat map while scrubbing — breathers present, twist is calm, nothing static > 4 s.
- Sound: every SFX lands on its motion, silences are silent, music never fights the voice.

## When the creator gives a note
Fix it, then ask "which instruction would have prevented this?" and write that rule into SKILL.md / treatments / planning / motion / sound / qa (and add a check here if it can be automated). Tell the creator which rule changed.


## Added 30 Oct 2026 (v2 re-edit notes)
- **Face-visible gate:** at every 0.5 s snapshot the face is fully visible (nothing opaque over the face band except captions); a full-screen beat that hides the face = fail.
- **Illustration gate:** each graphic is a drawing of something the line names; if it is a generic card / window / big type, redo it with `sticker-kit`.
- **Load gate:** ≤ 4 objects and ≤ 3 words per object at any time; the same scene carries consecutive beats.
- **Edge gate after scaling:** all art ≥ 60 px from the screen edge; read the full-size snapshot of every beat before showing the creator.
- Known false positive: `qa_reel.py` "nothing new on screen" when all stickers live in one clip.
