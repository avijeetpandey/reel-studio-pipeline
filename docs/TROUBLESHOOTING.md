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
