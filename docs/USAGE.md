# Usage guide

Everything is driven by plain sentences in Claude Code. Start a session (CLI: `claude`; desktop app: Code tab) — any folder works; the pipeline moves itself to `<studio>/reels/<reel_name>/`.

## 1. One reel, start to finish — `make: <topic>`
```
make: why AI agents fail at simple tasks
```
**Half 1 — no footage needed (≈ 10–20 min, no questions):**
1. **Research** — fact-checks every claim the script will make (primary sources first) → `research.md`.
2. **Script** (`script.md`) — topic check (broad > niche), format + alternative, 3 hooks (different shapes, each with what's on screen at frame 0), timed beats (line · on-screen text · scene type · visual · motion feel · delivery note), 95–120 spoken words, a proof line by second 5, reactions + an honest verdict, the fix, yes/no CTA + loop line, b-roll list, edit brief (look A–E, music mood, assets to capture), cover ideas, YouTube title, teleprompter block.
3. **Shoot sheet** — an artifact page for your phone: framing guide, lighting plan for the chosen look, do/avoid, checklist, the script by beat.
4. **Carousel + LinkedIn** in parallel (helper agents).
5. **Checkpoint 1** — one message with the shoot sheet link, carousel contact sheet, LinkedIn post. Reply `approved` or notes.
6. Uploads the carousel + LinkedIn assets to Drive (if enabled).

**Film:** follow the shoot sheet. Retakes are fine — say "again" and redo the line; the cut keeps the last clean take. AirDrop (or copy) the file to `~/Downloads` or `<studio>/inbox/`, then:
```
footage ready
```
**Half 2 — editing on autopilot (≈ 30–60 min):** footage check → review → cut (pauses > 0.3 s, fillers, false starts out; pace check) → face map → style chosen automatically → beat map + motion briefs → enhance pass (components only where a line earns one) → on-screen facts checked → music picked + trimmed + SFX → build (helpers per graphic beat) ∥ covers A/B ∥ posting kit → QA auto-fix (up to 3 rounds) → draft render + **Studio preview**.

**Checkpoint 2** — Studio link, draft video, storyboard, hook A/B, covers A/B, posting kit, QA report, and the choices made (style + why, signature move, music, what was auto-fixed). Reply:
- `approved` → final render at full quality, −14 LUFS, SRT, upload to `Drive/<folder>/<reel_name>/`, log, posting times; or
- notes, e.g. `0:07 the card covers my face · music too loud · use Terminal style` → fixes only those, shows the changed parts, asks again. **Every note becomes a rule** in the skill that caused it.

## 2. Several topics — `make: a; b; c`
Half 1 for up to 4 topics in parallel, one combined checkpoint. Then `footage ready <reel>` per reel (edits run one reel at a time; final renders queue).

## 3. Footage without a script — `edit: <video> [notes]`
```
edit: ~/Downloads/vlog.mov casual and fun, keep the length
```
Skips Half 1. Your notes override defaults (even length caps). Test reels: say "test, don't post" and nothing is uploaded.

## 4. Learn from reels you like — `study: <links>`
```
study: https://www.instagram.com/reel/…  https://www.instagram.com/reel/…
```
Opens each link in the built-in browser (sign in to Instagram there first), saves the video, caption, likes/comments and music info, then measures: transcript with word timings, words per minute, first-word time, loudness, music bed level, cuts, hook strip (0–2 s) and a 16-frame sheet. Claude watches every sheet, reads every transcript and cover, weights proven reels over fresh ones, writes `research/refs_<date>/NOTES.md`, adds a new round to `template/WINNING_PATTERNS.md` and pushes each rule into the skill/script that owns it. Videos are deleted afterwards.

## 5. Other commands
| Say | Does |
|---|---|
| `continue <reel>` | resumes from the manifest — nothing done is redone |
| `pipeline status` | one line per topic: stage, waiting on what |
| `footage ready <reel>` | starts Half 2 for a specific reel |
| `script a reel about …` | just the script + shoot sheet (`reel-script`) |
| `make a carousel about …` / `make C07` | just a carousel (`generate-carousel`) |
| `edit this reel` + a file | just the edit (`reel-edit`) |
| `studio setup` | change your answers / refresh the template |

## 6. Overriding the robot
At any checkpoint you can say: `use Studio Kinetic` (or any of the 9 styles), `no swing window`, `make line 3 a code window`, `keep it plain`, `pick a funkier track`, `cover B as main`. Up front: `footage ready, use Data style`.

## 7. Approval gates (never skipped)
Sign-ins (Instagram, YouTube Studio, Drive) are always yours. Checkpoint 1 (script) and checkpoint 2 (Studio preview) can be turned off in `CHANNEL_RULES.md`; uploads only happen after you approve **both** video and covers. Music is the one thing it does without asking (attribution-free Audio Library tracks only).

## 8. After posting
The posting kit lists exactly what to do: pin the yes/no comment, reply in the first hour, Story poll, log 48 h numbers. Tell Claude the numbers (`R03: 12k views, 71% stayed`) — a reel ≥ 3× your median gets 2–3 follow-up ideas.
