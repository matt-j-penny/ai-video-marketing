#!/usr/bin/env bash
# setup.sh — ONE-COMMAND auto-setup for content-os. Detects your OS (macOS, Windows
# via Git Bash, or Linux), installs every system tool the skills need, pre-builds the
# shared transcription engine and the carousel renderer so first use is instant,
# verifies with ./check-setup.sh, and writes the .setup-complete marker.
# Safe to re-run any time: it skips what's already done.
#
#   ./setup.sh
#
# macOS:   installs via Homebrew (if Homebrew itself is missing you run its one-liner
#          once, it needs your password, then re-run this).
# Windows: run from Git Bash (the shell Claude Code uses on Windows); installs via
#          winget. Newly installed tools sometimes need a new terminal before they're
#          on PATH; this script pulls in their well-known install dirs so most setups
#          finish in ONE run; if anything is still pending it says exactly what to do.
# Linux:   apt for the system tools (you run the printed sudo lines), uv for the rest.
#
# Exit codes (Claude reads these; each prints exactly what to do):
#   0  tools done (the CONNECTIONS checklist it prints is the next step)
#   1  something needs fixing first; the output says what
#   2  restart needed: freshly installed tools aren't on this session's PATH yet.
#      Restart Claude Code, then re-run ./setup.sh; it finishes the rest.
#
# What this does NOT do (it can't; these are your accounts): connect the Notion /
# Apify / Chrome MCPs inside Claude Code, add your Zernio key, log in to Higgsfield,
# or personalize the system (brand-kit.md). Claude walks you through those next.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$HERE/check-setup.sh" ]; then ROOT="$HERE"
elif [ -f "$HERE/../../check-setup.sh" ]; then ROOT="$(cd "$HERE/../.." && pwd)"
else printf 'ERROR: cannot locate the project root (check-setup.sh not found)\n' >&2; exit 1; fi
cd "$ROOT"

say()  { printf '%s\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

UNAME="$(uname -s 2>/dev/null || echo unknown)"
case "$UNAME" in
  Darwin)               OS=mac ;;
  MINGW*|MSYS*|CYGWIN*) OS=windows ;;
  Linux)                OS=linux ;;
  *)                    OS=other ;;
esac
pybin() {  # Windows installs `python`; its `python3` is a Store stub, so probe by running
  if python3 -c '' >/dev/null 2>&1; then echo python3
  elif python -c '' >/dev/null 2>&1; then echo python
  else echo ""; fi
}

if [ "$OS" = other ]; then
  say "Unrecognized shell/OS ($UNAME)."
  say "On Windows, run this from Git Bash (installed with Git for Windows: winget install Git.Git)."
  exit 1
fi
case "$OS" in mac) OSLBL="macOS" ;; windows) OSLBL="Windows · Git Bash" ;; *) OSLBL="Linux" ;; esac
say "== content-os auto-setup ($OSLBL) =="
say ""
PENDING=0

# ─── macOS: Homebrew ─────────────────────────────────────────────────────────
if [ "$OS" = mac ]; then
  if ! have brew; then
    say "Homebrew is missing: it's the one step that needs YOUR password, so run this"
    say "in your terminal, then re-run ./setup.sh:"
    say ''
    say '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
  fi
  for pkg in uv ffmpeg yt-dlp jq node python; do
    case "$pkg" in
      python) [ -n "$(pybin)" ] && { say "  ✓ python present"; continue; } ;;
      *)      have "$pkg" && { say "  ✓ $pkg present"; continue; } ;;
    esac
    say "  ▸ installing $pkg (brew)…"
    brew install "$pkg" || say "  ⚠ brew install $pkg failed; re-run ./setup.sh after fixing the error above"
  done
fi

# ─── Windows: winget + same-session PATH pickup ──────────────────────────────
if [ "$OS" = windows ]; then
  if ! have winget && ! have winget.exe; then
    say "winget is missing. Install 'App Installer' from the Microsoft Store, then re-run ./setup.sh."
    exit 1
  fi
  WG_FAILED=""
  wg() {  # wg <winget-id> <label>: install; on a real failure show winget's last lines and remember it
    local out rc
    out="$(winget install --exact --id "$1" --accept-source-agreements --accept-package-agreements --disable-interactivity 2>&1)"; rc=$?
    # winget returns distinct nonzero codes for "already installed" (0x8A15002B) / "no newer version";
    # treat only codes that also leave the tool invisible as failures (checked after refresh_path)
    if [ $rc -ne 0 ] && ! printf '%s' "$out" | grep -qiE 'already installed|no available upgrade|No newer package'; then
      say "  ⚠ winget install $1 exited $rc:"; printf '%s\n' "$out" | tail -n 3 | sed 's/^/      /'
      WG_FAILED="$WG_FAILED $2"
    fi
    return 0
  }
  refresh_path() {
    local d
    for d in "/c/Program Files/nodejs" \
             "$(cygpath -u "${LOCALAPPDATA:-}" 2>/dev/null)/Programs/Python/Python312" \
             "$(cygpath -u "${LOCALAPPDATA:-}" 2>/dev/null)/Programs/Python/Python312/Scripts" \
             "$(cygpath -u "${USERPROFILE:-}" 2>/dev/null)/.local/bin" \
             "$(cygpath -u "${LOCALAPPDATA:-}" 2>/dev/null)/Microsoft/WinGet/Links"; do
      [ -d "$d" ] && PATH="$d:$PATH"
    done
    for d in "$(cygpath -u "${LOCALAPPDATA:-}" 2>/dev/null)/Microsoft/WinGet/Packages"/Gyan.FFmpeg*/ffmpeg-*/bin; do
      [ -d "$d" ] && PATH="$d:$PATH"
    done
    export PATH
  }
  if have uv;     then say "  ✓ uv present";     else say "  ▸ installing uv (winget)…";     wg astral-sh.uv uv; fi
  if have ffmpeg; then say "  ✓ ffmpeg present"; else say "  ▸ installing ffmpeg (winget)…"; wg Gyan.FFmpeg ffmpeg; fi
  if have yt-dlp; then say "  ✓ yt-dlp present"; else say "  ▸ installing yt-dlp (winget)…"; wg yt-dlp.yt-dlp yt-dlp; fi
  if have jq;     then say "  ✓ jq present";     else say "  ▸ installing jq (winget)…";     wg jqlang.jq jq; fi
  if have node;   then say "  ✓ node present";   else say "  ▸ installing node (winget)…";   wg OpenJS.NodeJS.LTS node; fi
  if [ -n "$(pybin)" ]; then say "  ✓ python present"; else say "  ▸ installing python (winget)…"; wg Python.Python.3.12 python; fi
  refresh_path
  MISSING_WIN=""
  for t in uv ffmpeg yt-dlp jq node; do have "$t" || MISSING_WIN="$MISSING_WIN $t"; done
  [ -n "$(pybin)" ] || MISSING_WIN="$MISSING_WIN python"
  if [ -n "$MISSING_WIN" ]; then
    # a tool whose winget install actually failed is a fix-first (exit 1), not a restart (exit 2)
    for t in $MISSING_WIN; do
      case " $WG_FAILED " in *" $t "*) say "  ✗ $t: the winget install failed (see above). Run ./check-setup.sh for the exact command, install it by hand, then re-run ./setup.sh"; WIN_FIX=1 ;; esac
    done
    [ "${WIN_FIX:-0}" -eq 1 ] && exit 1
    # installed fine but not on this session's PATH yet: one restart; a second miss means PATH is really wrong
    RESTARTS=0; [ -f .setup-restarts ] && RESTARTS="$(cat .setup-restarts 2>/dev/null || echo 0)"
    if [ "${RESTARTS:-0}" -ge 2 ]; then
      say "  ✗ still not visible after two restarts:$MISSING_WIN"
      say "    Open a NEW terminal, run: where $(echo $MISSING_WIN | cut -d' ' -f1)   and if it prints nothing, install it by hand"
      say "    (./check-setup.sh prints the winget line), then re-run ./setup.sh."
      exit 1
    fi
    echo $((RESTARTS + 1)) > .setup-restarts
    say "  ⚠ installed but not visible yet in this session:$MISSING_WIN"
    PENDING=1
  fi
fi

# ─── Linux: apt lines are printed (sudo), uv installs itself + yt-dlp ───────
if [ "$OS" = linux ]; then
  MISSING_APT=""
  for t in ffmpeg jq curl python3; do have "$t" || MISSING_APT="$MISSING_APT $t"; done
  if [ -n "$MISSING_APT" ]; then
    say "  ▸ these need sudo, run them yourself, then re-run ./setup.sh:"
    say "      sudo apt update && sudo apt install -y$MISSING_APT"
    if ! have node; then say "      curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs"; fi
    exit 1
  fi
  if ! have node; then
    say "  ▸ node is missing (needs sudo), run this then re-run ./setup.sh:"
    say "      curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs"
    exit 1
  fi
  if have uv; then say "  ✓ uv present"; else
    say "  ▸ installing uv (astral installer, no sudo)…"
    curl -LsSf https://astral.sh/uv/install.sh | sh >/dev/null 2>&1 || say "  ⚠ uv install failed"
    export PATH="$HOME/.local/bin:$PATH"
  fi
  if have yt-dlp; then say "  ✓ yt-dlp present"; else
    say "  ▸ installing yt-dlp (uv tool)…"
    uv tool install yt-dlp >/dev/null 2>&1 || say "  ⚠ uv tool install yt-dlp failed"
    export PATH="$HOME/.local/bin:$PATH"
  fi
fi

# ─── Restart gate (Windows PATH) ─────────────────────────────────────────────
if [ "$PENDING" -eq 1 ]; then
  say ""
  say "== Almost done: some just-installed tools need a fresh environment =="
  say "One step for you: quit Claude Code, open a NEW terminal window (so PATH refreshes),"
  say "start Claude Code in this folder again and say \"continue setup\"; it re-runs"
  say "./setup.sh, which skips everything already done and finishes the rest."
  exit 2
fi

# ─── Shared transcription engine (faster-whisper venv, built once) ───────────
say ""
VENV="${CONTENT_OS_WHISPER_VENV:-$HOME/.cache/content-os/whisper-venv}"
if [ -e "$VENV/.deps-ok" ]; then
  say "  ✓ transcription engine ready ($VENV)"
elif have uv; then
  say "  ▸ building the shared transcription engine (faster-whisper, ~200 MB, one time)…"
  rm -rf "$VENV"
  if uv venv "$VENV" --python 3.11 >/dev/null 2>&1; then
    PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
    if uv pip install --quiet --python "$PYBIN" faster-whisper onnxruntime; then
      touch "$VENV/.deps-ok"; say "  ✓ transcription engine built"
    else
      say "  ⚠ faster-whisper install failed (network?); the first transcription retries it automatically"
    fi
  else
    say "  ⚠ uv venv failed; the first transcription retries it automatically"
  fi
else
  say "  ⚠ uv not available; the transcription engine builds on first use instead"
fi
# (whisper models download from Hugging Face on first use: tiny.en ~75 MB for captions,
#  small.en ~460 MB for research/corpus transcripts. Needs internet once.)

# ─── Report builder venv (pillow, for the two competitor-research HTML reports) ──
PVENV="${CONTENT_OS_PILLOW_VENV:-$HOME/.cache/content-os/pillow-venv}"
if [ -e "$PVENV/.deps-ok" ]; then
  say "  ✓ report builder ready ($PVENV)"
elif have uv; then
  say "  ▸ building the report-builder venv (pillow, small, one time)…"
  rm -rf "$PVENV"
  if uv venv "$PVENV" --python 3.11 >/dev/null 2>&1; then
    PPY="$PVENV/bin/python"; [ -e "$PPY" ] || PPY="$PVENV/Scripts/python.exe"
    if uv pip install --quiet --python "$PPY" pillow; then touch "$PVENV/.deps-ok"; say "  ✓ report builder built"
    else say "  ⚠ pillow install failed (network?); the first research report retries it automatically"; fi
  else
    say "  ⚠ uv venv failed; the first research report retries it automatically"
  fi
fi

# ─── Carousel renderer (npm deps + headless Chromium, built once) ────────────
CAR="$ROOT/.claude/skills/carousel-generator"
if [ -d "$CAR/scripts/node_modules/playwright" ]; then
  say "  ✓ carousel renderer ready"
elif have node && have npm; then
  say "  ▸ installing the carousel renderer (Playwright + Chromium, ~130 MB, one time)…"
  if bash "$CAR/install.sh" >/dev/null 2>&1; then say "  ✓ carousel renderer installed"
  else say "  ⚠ carousel install failed; run: bash .claude/skills/carousel-generator/install.sh  (read its output)"; fi
else
  say "  ⚠ node/npm not available; run bash .claude/skills/carousel-generator/install.sh later"
fi

# ─── Verify ──────────────────────────────────────────────────────────────────
say ""
say "== Verifying with check-setup.sh =="
./check-setup.sh || { say ""; say "Fix the items above, then re-run ./setup.sh"; exit 1; }
touch ".setup-complete"; rm -f .setup-restarts

# ─── Connections checklist (your accounts; Claude walks you through these) ───
say "== Tools done. Next: CONNECTIONS (Claude checks which are already live) =="
say "  1. Notion MCP (the content pipeline DB + scriptwriter):"
say "       claude mcp add --transport http notion https://mcp.notion.com/mcp   then /mcp to sign in"
say "  2. Apify MCP (Instagram competitor research + your own IG voice corpus):"
say "       claude mcp add --transport http apify https://mcp.apify.com          then /mcp to sign in"
say "  3. Claude in Chrome extension (feed research + DM revival): install it in Chrome,"
say "       run Claude Code from the terminal (not the desktop app) when using those skills."
say "  4. Zernio (auto-poster): API key + connected accounts -> .claude/skills/auto-poster/.env"
say "       (copy .env.example there; Claude can fill the account IDs from the API for you)"
say "  5. Higgsfield (optional, AI carousel covers): install the CLI, then higgsfield auth login"
say ""
say "Then personalize: fill brand-kit.md and tell Claude \"apply my brand kit\" (it builds your"
say "voice corpus, backbone, competitor list, and Notion DB from that one file)."
exit 0
