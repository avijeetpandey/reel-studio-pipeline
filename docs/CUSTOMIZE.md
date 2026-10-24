# Customising

- **Your answers** — say `studio setup` to change any of them, or edit `~/.config/reel-studio/config.json` and `<studio>/CHANNEL_RULES.md` directly. `CHANNEL_RULES.md` always wins over default numbers written inside the skills.
- **Brand look** — accent colour comes from the config; covers live in `<studio>/template/thumbnail/` and the carousel deck in `<studio>/template/carousel/deck.html` (fonts, colours, layouts). Treatments (looks per reel) are in the plugin's `skills/reel-edit/treatments.md`.
- **Avatar** — put a square PNG at `<studio>/template/carousel/assets/avatar-cartoon.png` (setup copies the one you named).
- **Formats and hooks** — `skills/reel-script/SKILL.md` (format table, hook rules), `template/WINNING_PATTERNS.md` (hook bank).
- **Approval gates** — `CHANNEL_RULES.md` → "Approval gates". Turning a gate off means that checkpoint is skipped and its choices are reported at the next one.
- **No Drive** — leave `drive_folder` empty in setup; everything stays in the reel folder.
- **Other languages** — add the multilingual whisper model in setup; captions are only written where the transcript is reliable.
- **Your own components** — add an HTML file to `<studio>/template/composition/components/` (CSS + markup + a `buildX(tl, opts)` function, seek-safe) and one line to its `INDEX.md`.
- **Keep your changes when updating** — edits to the plugin's skills are overwritten by `/plugin update`; put personal rules in `CHANNEL_RULES.md`, or fork the repo.
