# Enhance pass — add motion that the content earns, then vet it

# Autonomous mode (default — the creator is never asked)
1. `python3 -I T/scripts/choose_style.py work/lines.txt --script script.md --out work/style_plan.json` → treatment, why, signature move, music mood, per-line components (budget and quiet beats already applied).
2. Review the plan once like an editor: for each upgraded line apply the earn-it test below; drop or swap what fails. Add what the script's edit brief demands. Record every change you made to the plan and why.
3. Build, then vet with the auto-fix loop (SKILL.md step 6): up to 3 rounds; failing components are removed, not shipped.
4. At checkpoint 2 report in one block: treatment + why, signature move, components used (and lines deliberately left plain), anything auto-fixed or dropped. the creator can reply with a one-line override ("use Terminal", "no swing window") → rebuild only what changed.
5. After the render, append the row to `reels/style_log.md` (treatment, signature move, music) so the next reel's rotation sees it.
Questions to the creator are limited to the standing gates: sign-ins, the preview approval, and the Drive upload. Missing real assets for a swing-window (a screenshot of the named app) → capture one with `hyperframes capture`; if that fails, downgrade the line to pop-blur and say so.

Runs after the beat map and motion briefs (step 3) and before building (step 4). It does NOT add effects for their own sake: it reads each line, decides whether it deserves a motion upgrade, and picks the lightest component that makes the idea clearer. The default answer for a line is "no upgrade".

Components live in `T/composition/components/` (see `INDEX.md`, header comment of each file has usage + options). Registry blocks (`hyperframes-registry`) are the next choice; hand-built is last.

## 1. Classify every beat by what the line says
| The line… | Upgrade | Component | Notes |
|---|---|---|---|
| is the hook claim, a big number, or the twist word | headline roll | `roll-text` | ≤ 4 words, accent on the one word that carries the claim. Hook words stay 0–0.55 s unless the treatment says otherwise |
| names a term/thing and a card pops with it (stat, label, "no credits") | calm entrance | `pop-blur` | the default for every card; time `start` to the spoken word from WORDS |
| shows an app, page, doc or tool | screen card | `swing-window` | a REAL screenshot/recording inside; signature-level, max 2 per reel |
| quotes a prompt, command, code or config | typed card | `code-window` | real text from the script, ≤ 6 lines, ≤ 28 chars/line; max 2 heavy per reel together with swing-window |
| is personal, an opinion, the twist delivery, the CTA question | nothing | — | stays `T` (face only) — these are the quiet moments |
| says "number one / two / the best one" (a list) | visible progress | `step-progress` | one per reel, for the whole list; `style_plan.json` gives the step times |
| is the CTA (last 3.9 s) | in-video CTA | `cta-card` | variant from `style_plan.json` (`cta_variant`: follow / save) or the edit brief; comment variant types the yes/no answer |
| has a chart, map, counter or diagram | registry block | `npx hyperframes catalog` | adapt to the treatment; tag `data-component="<block name>"` |

## 2. Budget (hard limits)
- ≤ 1 signature move per reel (treatment's own) + ≤ 2 heavy components (swing-window / code-window). `step-progress` and `cta-card` don't count toward the heavy budget. Everything else is pop-blur or plain.
- At least 2 quiet beats stay motion-free (twist, pre-CTA). Never a heavy component in the first 2 s or on the last 4 s.
- Component colours/fonts come from the treatment variables, never inline hexes. Min text 34 px, nothing over the face box, safe box x 60–930, y 250–1420.
- If the reel is mostly personal opinion with no named thing, ship it plain and say so at the checkpoint — fewer effects is the brand.

## 3. Wire it into the plan and the build
- Add a **Component** column to `EDIT_PLAN.md` (`roll-text` / `swing-window` / `pop-blur` / `code-window` / registry name / —) and one line of "why this line earns it".
- In the composition, copy the component's CSS + markup + JS, call `buildX(tl, {…})` with `start` taken from the spoken word, and tag the clip `data-component="<name>"` (qa_reel.py reads it).
- Helper agents: pass the component file and the beat's options in the brief.

## 4. Vet (before the self-check in step 6)
Run these and fix until clean; record the result in the checkpoint's "choices made":
1. `python3 -I T/scripts/qa_reel.py <composition_dir> --segments … --geometry …` → 0 errors, including the `enhance:` rules (≤ 2 heavy, no overlap, roll-text ≤ 4 words).
2. **Earn-it test**, per component: delete it mentally — does the viewer understand the line less? If not, remove it.
3. **Silent test:** muted, does the component help the story or just decorate?
4. **Timing:** each `start` lands on or ≤ 0.1 s before the spoken word; nothing appears after the word is said; exit is faster than entrance.
5. **Seek test:** `npx hyperframes snapshot` at 3 times per component (before / during / after) and once scrubbed backwards — no stuck states, text fully typed/fully rolled where expected.
6. **Look:** full-size frame of each component beside the treatment's reference — fonts, colours, radii match; nothing looks like a template.
7. `npx hyperframes lint` + `check --snapshots` → 0 errors.
A component that fails vetting is fixed or removed; never shipped "to see if anyone notices".
