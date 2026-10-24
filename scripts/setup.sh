#!/usr/bin/env bash
# Reel Studio — dependency check / install (macOS + Homebrew; Linux users install the same tools with their package manager).
# Usage: bash scripts/setup.sh [--install]   (without --install it only reports)
set -uo pipefail
INSTALL=0; [ "${1:-}" = "--install" ] && INSTALL=1
ok(){ printf "  \033[32m✓\033[0m %s\n" "$1"; }; miss(){ printf "  \033[31m✗\033[0m %s — %s\n" "$1" "$2"; MISSING=1; }
MISSING=0
echo "Reel Studio dependency check"
need(){ # name, command, brew formula
  if command -v "$2" >/dev/null 2>&1; then ok "$1 ($(command -v "$2"))"
  elif [ $INSTALL = 1 ] && command -v brew >/dev/null; then brew install "$3" && ok "$1 installed" || miss "$1" "brew install $3"
  else miss "$1" "brew install $3"; fi; }
command -v brew >/dev/null || echo "  ! Homebrew not found — install from https://brew.sh (needs your password) or install the tools below manually"
need ffmpeg ffmpeg ffmpeg
need ffprobe ffprobe ffmpeg
need node node node
need python3 python3 python
need whisper-cli whisper-cli whisper-cpp
need rclone rclone rclone
need yt-dlp yt-dlp yt-dlp
if [ -d "/Applications/Google Chrome.app" ]; then ok "Google Chrome"; else miss "Google Chrome" "install from https://www.google.com/chrome (covers, carousels, LinkedIn image render headless)"; fi
NODEV=$(node -v 2>/dev/null | tr -d v | cut -d. -f1); [ -n "$NODEV" ] && [ "$NODEV" -lt 18 ] && miss "node ≥ 18" "brew upgrade node"
M=~/.cache/hyperframes/whisper/models/ggml-small.en.bin
if [ -f "$M" ]; then ok "whisper model small.en"; else
  if [ $INSTALL = 1 ]; then mkdir -p "$(dirname "$M")" && curl -L -o "$M" https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin && ok "whisper model downloaded" || miss "whisper model" "see README"
  else miss "whisper model small.en (≈ 470 MB)" "bash scripts/setup.sh --install"; fi; fi
if npx --yes hyperframes@latest --version >/dev/null 2>&1; then ok "HyperFrames CLI (npx)"; else miss "HyperFrames CLI" "needs network: npx --yes hyperframes@latest --version"; fi
ffmpeg -hide_banner -h filter=lut3d 2>&1 | grep -q "Filter lut3d" && ok "ffmpeg lut3d filter (HDR phone footage)" || miss "ffmpeg lut3d" "reinstall ffmpeg"
rclone listremotes 2>/dev/null | grep -q . && ok "rclone remotes: $(rclone listremotes | tr '\n' ' ')" || echo "  ! no rclone remote yet — run 'rclone config' (Google Drive) if you want uploads"
[ $MISSING = 0 ] && echo "All required tools found." || echo "Some tools are missing (see ✗ above). Re-run with --install to install via Homebrew."
