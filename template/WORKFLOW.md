# {brand} — template folder

All rules and steps live in the skills: `$PLUGIN/skills/reel-script/` (topic → script + shoot sheet),
`$PLUGIN/skills/reel-edit/` (footage → finished reel; plus treatments.md, planning.md, motion.md, sound.md, qa.md)
and `$PLUGIN/skills/generate-carousel/` (topic → carousel). Channel rules and approval gates: `$STUDIO/CHANNEL_RULES.md`.
This folder only holds reusable code and assets:

```
scripts/analyze.sh               ← silences + per-island word timings
scripts/envelope.py              ← RMS envelope to find safe cut points inside a phrase
scripts/make_cut.py              ← cut + (HLG→SDR) + upscale + grade + voice chain + end hold
scripts/make_lut.py              ← HLG→BT.709 .cube (called by make_cut.py)
scripts/finalize.sh              ← two-pass loudnorm to −14 LUFS
scripts/render_cover.sh          ← frame → cutout → cover.png/jpg + grid-crop check
scripts/make_srt.js              ← caption WORDS → .srt for YouTube
scripts/sample_frames.sh         ← contact sheets (+ 6×6 grid for the face map)
scripts/safe_zone.sh             ← shade Instagram/YouTube UI zones on review stills
scripts/qa_reel.py               ← self-check: flashes, read time, face flashes, text over face, variety, transcript repeats/fillers/pauses
scripts/make_sfx.py              ← synthesizes original SFX (whoosh-air/long, riser-metal, hit-heavy, paper, pen, ui-success, tick, line-draw)
review/review.html               ← draft player: press N for a timestamped note, copy all notes back to Claude
posting-kit-template.md          ← Instagram + YouTube copy skeleton
composition/reference-index.html ← composition code patterns (hook words, captions, CTA, progress bar, screen card)
composition/components/          ← reusable graphic components (+ INDEX.md)
composition/assets/audio/sfx/    ← 25 sounds by family (see reel-edit/sound.md)
composition/assets/audio/music/  ← approved YouTube Audio Library tracks + INDEX.md (mood tags)
composition/assets/broll/        ← example captured page
carousel/                        ← generate-carousel: deck.html, render.sh, assets, examples
thumbnail/cover-template.html    ← cover A "curiosity"
thumbnail/cover-template-b.html  ← cover B "bold claim"
```
Also: `../reels/style_log.md` (treatment rotation), `../broll/INDEX.md` (b-roll library), optional `style-dna.md` (3–5 reference reels the creator loves).

scripts/pipeline.py              ← make-content: manifest, render locks, footage pickup, approval-gated Drive upload
PIPELINE.md                      ← make-content design (parallel graph, manifest, checkpoints)
