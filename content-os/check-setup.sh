#!/usr/bin/env bash
# check-setup.sh — verify the system tools the content-os skills need.
#
# Report-only: checks what's installed and prints the install command for
# anything missing. Installs NOTHING and touches nothing. (./setup.sh is the
# installer; it calls this at the end to verify.)
#
#   ./check-setup.sh
#
# Cross-platform: macOS (Homebrew), Linux (apt + uv), Windows (Git Bash + winget —
# the shell Claude Code uses on Windows). The Python side (faster-whisper) is NOT
# installed here: every transcription skill shares ONE persistent venv at
# ~/.cache/content-os/whisper-venv that builds itself on first use (or setup.sh
# pre-builds it). Exit 0 = every core tool present.
set -uo pipefail

UNAME="$(uname -s 2>/dev/null || echo unknown)"
case "$UNAME" in
  Darwin)               OS=mac;     OSLABEL="macOS" ;;
  Linux)                OS=linux;   OSLABEL="Linux" ;;
  MINGW*|MSYS*|CYGWIN*) OS=windows; OSLABEL="Windows (Git Bash)" ;;
  *)                    OS=other;   OSLABEL="$UNAME" ;;
esac

# install hint per tool + platform (bash 3.2-safe: case, no assoc arrays)
hint() {
  case "$OS:$1" in
    mac:uv)          echo "brew install uv" ;;
    mac:ffmpeg)      echo "brew install ffmpeg" ;;
    mac:yt-dlp)      echo "brew install yt-dlp" ;;
    mac:jq)          echo "brew install jq" ;;
    mac:node)        echo "brew install node" ;;
    mac:python3)     echo "brew install python" ;;
    mac:curl)        echo "brew install curl" ;;
    linux:uv)        echo "curl -LsSf https://astral.sh/uv/install.sh | sh" ;;
    linux:ffmpeg)    echo "sudo apt install -y ffmpeg" ;;
    linux:yt-dlp)    echo "uv tool install yt-dlp        (apt's yt-dlp is too old)" ;;
    linux:jq)        echo "sudo apt install -y jq" ;;
    linux:node)      echo "curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs" ;;
    linux:python3)   echo "sudo apt install -y python3" ;;
    linux:curl)      echo "sudo apt install -y curl" ;;
    windows:uv)      echo "winget install astral-sh.uv         (then open a NEW terminal)" ;;
    windows:ffmpeg)  echo "winget install Gyan.FFmpeg          (then open a NEW terminal)" ;;
    windows:yt-dlp)  echo "winget install yt-dlp.yt-dlp        (then open a NEW terminal)" ;;
    windows:jq)      echo "winget install jqlang.jq            (then open a NEW terminal)" ;;
    windows:node)    echo "winget install OpenJS.NodeJS.LTS    (then open a NEW terminal)" ;;
    windows:python3) echo "winget install Python.Python.3.12   (then open a NEW terminal)" ;;
    windows:curl)    echo "(curl ships with Windows 10+/Git Bash)" ;;
    *:higgsfield)    echo "curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh   then: higgsfield auth login" ;;
    *)               echo "install $1" ;;
  esac
}

if [ -t 1 ]; then
  G=$(tput setaf 2); R=$(tput setaf 1); Y=$(tput setaf 3); D=$(tput setaf 8); B=$(tput bold); N=$(tput sgr0)
else
  G=; R=; Y=; D=; B=; N=
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
missing=0
check() {  # check <cmd> <label> <hint-key> <used-by>
  if command -v "$1" >/dev/null 2>&1; then
    printf "  ${G}✓${N} %-11s ${D}%s${N}\n" "$2" "$4"
  else
    printf "  ${R}✗${N} %-11s ${Y}%s${N}  ${D}(needed by %s)${N}\n" "$2" "$(hint "$3")" "$4"
    missing=$((missing + 1))
  fi
}
ok()   { printf "  ${G}✓${N} %-11s ${D}%s${N}\n" "$1" "$2"; }
note() { printf "  ${Y}!${N} %-11s ${D}%s${N}\n" "$1" "$2"; }

printf "\n${B}content-os — system prerequisites${N}  ${D}(%s)${N}\n\n" "$OSLABEL"

if [ "$OS" = other ]; then
  printf "  ${R}Unsupported shell/OS ($UNAME).${N} On Windows run this from Git Bash (winget install Git.Git), not PowerShell.\n\n"
elif [ "$OS" = mac ] && ! command -v brew >/dev/null 2>&1; then
  printf "  ${Y}Homebrew not found${N} — the installs below use it. Install it first (needs your password):\n"
  printf "    ${B}/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${N}\n\n"
elif [ "$OS" = linux ]; then
  printf "  ${D}Installs below use apt (run ${B}sudo apt update${N}${D} once first) + uv.${N}\n\n"
elif [ "$OS" = windows ]; then
  printf "  ${D}Installs below use winget. After each install open a NEW terminal (and restart Claude Code once) so PATH updates.${N}\n\n"
fi

printf "${B}Core${N} (the skills need these):\n"
check uv     uv     uv     "builds the shared faster-whisper venv (transcribe-url, research, auto-poster captions, voice corpus, yt-description chapters)"
check ffmpeg ffmpeg ffmpeg "audio extraction for every transcription + reel keyframes"
check ffprobe ffprobe ffmpeg "media probing (ig-competitor-research)"
check yt-dlp yt-dlp yt-dlp "transcribe-url, yt-competitor-research, yt-description, voice-corpus-builder"
check jq     jq     jq     "ig-competitor-research + voice-corpus-builder (write the Apify dataset to disk)"
check curl   curl   curl   "media downloads (research, auto-poster, voice corpus)"
check node   node   node   "carousel-generator (Playwright renderer)"
check npm    npm    node   "carousel-generator one-time deps"

# Python: probe by RUNNING it (Windows installs `python`, and its `python3` is a Store stub)
PYBIN=""
if python3 -c '' >/dev/null 2>&1; then PYBIN=python3
elif python -c '' >/dev/null 2>&1; then PYBIN=python; fi
if [ -n "$PYBIN" ]; then
  ok "python" "stdlib-only helper scripts in every skill (runs as \`$PYBIN\`)"
else
  printf "  ${R}✗${N} %-11s ${Y}%s${N}  ${D}(needed by every skill's helper scripts)${N}\n" "python" "$(hint python3)"
  missing=$((missing + 1))
fi

printf "\n${B}Optional${N} (only if you use the feature):\n"
if command -v higgsfield >/dev/null 2>&1; then
  if higgsfield account status >/dev/null 2>&1; then
    ok "higgsfield" "installed + logged in — carousel-generator AI covers"
  else
    note "higgsfield" "installed but not logged in: run \`higgsfield auth login\` (carousel-generator AI covers)"
  fi
else
  note "higgsfield" "not installed; only needed for AI carousel covers: $(hint higgsfield)"
fi

printf "\n${B}One-time bootstraps${N}  ${D}(./setup.sh does these; each skill also self-heals on first use)${N}:\n"
VENV="${CONTENT_OS_WHISPER_VENV:-$HOME/.cache/content-os/whisper-venv}"
if [ -e "$VENV/.deps-ok" ]; then
  ok "whisper venv" "$VENV (shared faster-whisper engine, ready)"
else
  note "whisper venv" "not built yet — builds automatically on the first transcription (~200 MB + model), or run ./setup.sh"
fi
PVENV="${CONTENT_OS_PILLOW_VENV:-$HOME/.cache/content-os/pillow-venv}"
if [ -e "$PVENV/.deps-ok" ]; then
  ok "report venv" "$PVENV (pillow, for the competitor-research HTML reports, ready)"
else
  note "report venv" "not built yet — builds automatically on the first competitor-research report, or run ./setup.sh"
fi
CAR="$REPO/.claude/skills/carousel-generator/scripts"
if [ -d "$CAR/node_modules/playwright" ]; then
  ok "carousel deps" "Playwright installed in the skill (run \`bash .claude/skills/carousel-generator/install.sh\` again if Chromium is missing)"
else
  note "carousel deps" "not installed — run: bash .claude/skills/carousel-generator/install.sh   (npm deps + headless Chromium, one time)"
fi
if [ -f "$REPO/.claude/skills/auto-poster/.env" ]; then
  ok "auto-poster" ".claude/skills/auto-poster/.env present (Zernio key + account IDs)"
else
  note "auto-poster" "no .claude/skills/auto-poster/.env yet — copy .env.example there and add your Zernio API key + account IDs before posting"
fi

printf "\n${B}Connections${N}  ${D}(set up inside Claude Code, not checkable from a shell)${N}:\n"
printf "  ${D}•${N} Notion MCP (scriptwriter + the pipeline DB) · Apify MCP (ig-competitor-research, voice-corpus-builder IG) · Claude in Chrome extension (feed research, dm-revival)\n"

printf "\n"
if [ "$missing" -eq 0 ]; then
  printf "${G}${B}All core tools present.${N}\n\n"
else
  printf "${R}${B}%d core item(s) missing.${N} Run the commands shown above, then re-run this script.\n\n" "$missing"
fi
[ "$missing" -eq 0 ]
