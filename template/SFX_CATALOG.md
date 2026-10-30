# SFX catalog — what each sound is FOR (rewritten 30 Oct 2026 after the IG study of 31 editing/sound reels)

Every file here is an ORIGINAL synthesized or the creator-cleared sound — no third-party licence (`make_sfx.py` round 1–5, `make_sfx2.py` round 6). Regenerate any that feels off.
Vocabulary = what pro editors call the sounds in the reference reels (anderson.tai: "click for pop-ups, flash for quick cuts, whoosh for scene changes, glitch for text, riser for tension"; Viewcci "use THIS sound with THIS animation").

| Job on screen | Use (primary → alternate) | Notes |
|---|---|---|
| Something pops up / a card appears | `pop`, `click-soft`, `soft-pluck`, `mouse-click` | 0.18–0.3 vol; fire 40–60 ms BEFORE the visual lands |
| Text / caption line appears | `typewriter` (long lines), `digital-tick`, `glitch` (hook word, punch word) | glitch only on the 1–2 words that matter |
| Quick jump-cut / punch-in | `camera-shutter`, `camera-flash`, `slice` | ≤ 0.2 s; only on cuts that change the idea, not every cut |
| Scene / layout change | `whip` (fast), `whoosh-short`, `whoosh-air`, `digital-sweep` (UI), `whoosh-long` (big move) | match length to the move |
| Build tension → payoff | `riser` / `riser-metal` / `reverse-swell` (0.6–1.2 s) → `hit-heavy` / `bass-drop` / `impact-bass-*` | max one build per reel; silence for 150 ms right before the hit |
| Stop-the-scroll opener | `notif-pop` (iPhone-style ping), `bass-drop`, `camera-flash` | frame 0–0.3 s, under the first word, not over it |
| Negative / "wrong" / myth | `negation`, `glitch-negative`, `error` | pair with RED text |
| Positive / fact / done | `ui-success`, `check-blip`, `ding`, `sparkle` | pair with GREEN/accent |
| Verdict / objection stamp | `stamp`, `hit-heavy`, `soft-hit` | pair with `stamp-slap` component |
| Counter / odometer / list step | `counter-roll` (rolling number), `tick`, `digital-tick`, `low-pulse` (under the final number) | tick every 3rd digit change |
| Typing / terminal | `typing`, `key-press`, `typewriter` | ≤ 0.25 vol |
| Hand-drawn / notebook | `pen-scribble`, `line-draw`, `paper-slide` | Notebook treatment |
| Time claim | `ticktock-rev` (reversed ticks), `counter-roll` | pair with `stopwatch` |
| UI opens / panel slides | `ui-open`, `zap`, `digital-sweep` | |

## Density (measured in the study reels — replaces "never SFX on b-roll cuts / caption pops")
- Talking reels of the study carry one deliberate non-voice sound every **1.5–3 s** (≈ 4–7 per 10 s); SFX-teaching reels one every ~1 s.
- **Every visual event gets a sound; no sound without a visual event** (a pop, a text hit, a cut that changes idea, a counter step, a state change). Hard cuts inside ONE continuous idea stay silent; a cut to NEW b-roll/graphic gets `slice`/`camera-shutter`/`whip`.
- **Sync:** the sound's transient starts 1–2 frames (30–60 ms) BEFORE the visual lands — it reads as "tight". Never after.
- Layer a tiny tail: ≥ 10 % room reverb on the SFX bus; every SFX 20–40 ms fade-out. Voice stays on top: SFX −10…−16 dB under the voice peak (vol 0.15–0.35).
- Two signature sounds per reel (e.g. `whip` = every scene change, `ding` = every fact) PLUS accents from the table so it doesn't sound like a loop.
- Hinglish lines: the voice is fast and dense — keep SFX short (< 0.3 s) in dense stretches so words stay clear.
