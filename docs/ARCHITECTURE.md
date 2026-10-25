# Architecture

## Layout
```
reel-studio-pipeline/            (this repo = the Claude Code plugin)
  .claude-plugin/                plugin.json, marketplace.json
  skills/
    studio-setup/                first-run interview → config, rules, template install, deps
    make-content/                orchestrator (commands, both halves, edit-only, learning mode, music library, robustness)
    reel-script/                 script + shoot sheet + LinkedIn (templates: shoot-sheet-template.html, linkedin-image-template.html)
    reel-edit/                   SKILL.md + treatments.md (10 looks) · planning.md (beat map) · motion.md · enhance.md · sound.md · qa.md
    generate-carousel/           SKILL.md + formats.md + copy.md
  template/                      copied to <studio>/template by setup (tokens filled)
    WINNING_PATTERNS.md          lessons from reference reels (grows with study:)
    PIPELINE.md · WORKFLOW.md    spec + map
    scripts/                     see below
    composition/                 reference-index.html (code patterns) · components/ (14 motion components + INDEX.md)
    carousel/                    deck.html (all layouts, incl. finding · dodont · roadmap · photo) · render.sh · examples/sampler/slides.js
    thumbnail/                   cover-template.html (A, curiosity) · cover-template-b.html (B, bold claim)
    review/review.html           timestamped-notes player
    posting-kit-template.md
  scripts/                       setup.sh (deps) · configure.py (config + rules + template install)
  docs/
```
Your data (never in the repo): `~/.config/reel-studio/config.json` and `<studio>/` = `CHANNEL_RULES.md`, `template/`, `reels/<reel>/` (src, cut, composition, renders, covers, posting kit, `pipeline.json` manifest), `reels/style_log.md`, `carousels/`, `research/`, `inbox/`.

## Scripts (`<studio>/template/scripts/`)
| Script | Role |
|---|---|
| `pipeline.py` | manifest per reel (`init/set/file/approve/status/next`, plus `features`, `posted`, `stats`, `channel`, `due` for your numbers), footage pickup + pre-flight, machine-wide render locks (max 4 + 1 final), approval-gated Drive upload with size verification |
| `analyze.sh` | silences + per-island whisper transcription with word timings |
| `envelope.py` | audio envelope to cut at real dips |
| `make_cut.py` | bakes the cut: HLG→SDR tone-map (`--exposure`, `--saturation`, `--no-grade`), 9:16, upscale, voice chain, 0.3 s end pad (the reel ends on the last word) |
| `choose_style.py` | picks the treatment from the script (signals + format label + rotation in `style_log.md`), signature move, music mood, per-line component plan, CTA variant, list device (step-progress / list-header), count-roll + hand-annotate lines, literal hook image |
| `pick_music.py` | picks the most energetic approved track not used in the last 3 reels, trims it to its best start with fades |
| `beat_grid.py` | tempo + beat phase of the trimmed bed (whole-track comb, no drift), beats/bars in reel time; `--check` lists graphic entrances / b-roll cuts off the beat with the snapped time |
| `channel_report.py` | monthly report from your Instagram + YouTube stats: medians, each format / hook / style / length vs median per platform, platform disagreements, post times, 3× winners; writes `performance.json` for the style picker |
| `music_energy.py` | scores tracks: BPM, hit density, intro length, best start, energy 0–100 |
| `qa_reel.py` | timeline QA (flash, read time, face flash, face box, scene variety, static stretches, component budget), `--audio` (repeats, fillers, pauses > 0.25 s, first word, pace WPM, tail after the last word), `--cover` (near-blank) |
| `analyze_reference.py` | reference reels → metrics.json, transcripts, hook strip + sheets |
| `make_sfx.py` | synthesises an original SFX pack (whooshes, riser, hits, paper, pen, chime, tick, line-draw + a digital family: soft pluck, low pulse, digital sweep, digital tick, soft hit, check blip) |
| `render_cover.sh` · `finalize.sh` · `make_srt.js` · `sample_frames.sh` · `safe_zone.sh` · `make_lut.py` | covers, −14 LUFS master, SRT, contact sheets, UI-zone overlay, HDR LUT |

## The edit (reel-edit) in stages
1. **Review** — transcript, contact sheets, probe (HDR check: graded vs raw frame).
2. **Cut** — whole speech islands, dead air/fillers/retakes out, buried claim moved first, 40–60 ms pads, `qa_reel.py --audio` clean (pace ≥ 190 WPM target).
3. **Face map** (`geometry.json`), **style** (`choose_style.py`), **beat map** (`EDIT_PLAN.md`, 11 rules), **motion briefs**, **enhance pass** (components + budget), **sound map**.
4. **Composition** (HyperFrames, 1080×1920, seek-safe GSAP) — hook words at 0 s over the face, captions, components, camera moves, b-roll, CTA card, loop frame; helpers build graphic beats in parallel.
5. **Sound** — energetic bed from second 1, carved under the voice, 2–3 signature SFX.
6. **QA auto-fix ×3** — lint, check (+ UI zones), qa_reel (incl. the video ends ≤ 0.5 s after the last word), beat check, frame grading (every 1 s frame ≥ 8/10), AI-slop tells, frame-0 gate, taste checks (music energy, best-looking ending, ≤ 1 emoji, nothing templated), draft + Studio preview.
7. **Final** — delivery render, −14 LUFS, SRT, style log. 8. **Covers A/B**. 9. **Posting kit**. 10. **Upload**. 11. **Revisions → rules**.

## Treatments (10) and looks (A–E)
Clean Tech · Notebook · Newsroom · Terminal · Data · Cinematic Cutout · Editorial Split · Studio Kinetic · Fact-or-Hype Reaction · Halftone Collage — chosen automatically, never the same as the last 2 reels. Looks (what you film): A lo-fi selfie · B cinematic studio · C graphic top / face box · D reaction/stitch · E prop as screen.

## Learning
Your own numbers: `pipeline.py posted/stats/channel` store Instagram + YouTube results per reel (`reels/stats_log.md`, `reels/channel_log.json`); `channel_report.py` → `reports/<month>.md` + `reels/performance.json`; `choose_style.py` reads it (capped nudge, ≥ 3 reels per style). Nothing is scheduled.

`WINNING_PATTERNS.md` holds the rules learned from reference reels (hooks, structure, pace, layouts, captions, CTA cards, covers, sound, captions/tags). Every skill reads it; `study:` appends a round. Your own notes go straight into the skill files ("which rule would have prevented this?").
