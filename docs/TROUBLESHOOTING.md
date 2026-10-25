# Troubleshooting

| Problem | Fix |
|---|---|
| "config missing" / skills ask to run setup | say `studio setup` |
| `whisper-cli: command not found` or model missing | `bash scripts/setup.sh --install` |
| Neon / washed-out colours from iPhone HDR footage | the edit compares graded vs raw; force it with `make_cut.py … --no-grade --exposure 0.6 --saturation 0.62` |
| Captions wrong in non-English parts | install the multilingual model in setup; otherwise the edit captions only reliable lines |
| `hyperframes` errors / lint fails | `npx --yes hyperframes@latest --version`; make sure the HyperFrames Claude Code plugin is installed |
| Render shows `hasHdrContent: true` / round PiP renders square | the cut wasn't tone-mapped — re-run `make_cut.py` (it detects HLG) |
| Studio preview doesn't open | it runs on `http://localhost:3002`; stop old ones with `npx hyperframes preview <dir> --stop` |
| Drive upload refused | by design until checkpoint 2 is approved (`pipeline.py status <reel>`); or `rclone config reconnect <remote>:` |
| `study:` can't download a reel | sign in to Instagram in the built-in browser; private posts can't be studied |
| Music sounds calm | grow the library (docs/MUSIC.md); `pick_music.py` prefers energy ≥ 75 |
| A session ended mid-reel | `continue <reel_name>` |
| `stats:` stops at "Verify that it's you" in YouTube Studio | a security step only you can do — finish it in the browser pane, then say `continue` |
| Instagram per-reel numbers missing | the reel page has none on the web; stats come from `instagram.com/accounts/insights/content/…` — if a field is app-only, send a screenshot of the app's Insights |
| `report:` says "no posted reels with stats" | record links with `posted <reel> <ig> <yt>` and numbers with `stats:` first |
| Style picker ignores your results | it only uses a style after ≥ 3 posted reels with stats, and the nudge is capped; run `report:` to refresh `performance.json` |
| Worried about background token use | nothing is scheduled: `stats:`, `report:` and `trends:` only run when you type them |
