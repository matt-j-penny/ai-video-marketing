# yt-competitor-research — setup

Scans YouTube competitors via yt-dlp, ranks each channel's last-week uploads by views (surfacing a breakout score vs that channel's weekly median), keeps the top 3 per channel, analyzes each winner's packaging (title + thumbnail — no transcription, no frame extraction), and builds a self-contained HTML report. Claude drives the whole thing — you just trigger it ("research my yt competitors", or name handles inline).

## Prerequisites

**1. System tools.** Free, no accounts, no API keys. `./setup.sh` from the project root installs everything (macOS via Homebrew, Windows via winget from Git Bash, Linux via apt + uv) and `./check-setup.sh` reports what's still missing:
- `yt-dlp` — pulls channel uploads + per-video metadata (no download). Keep it fresh when it warns about being >90 days old: `brew upgrade yt-dlp` (macOS), `winget upgrade yt-dlp.yt-dlp` (Windows), `uv tool upgrade yt-dlp` (Linux / uv installs).
- `uv` — https://docs.astral.sh/uv/ (builds the report builder's pillow venv once, no manual pip)
- Python and `curl` (`python3` on macOS/Linux, `python` on Windows).

The first run of `scripts/build-report.sh` builds a tiny pillow venv once under `~/.cache/content-os/pillow-venv` (sentinel-gated on `.deps-ok`; `CONTENT_OS_PILLOW_VENV` overrides the location). Takes a few seconds; every later run calls that venv's python directly.

**2. Channels.** Either name them inline when you trigger the skill, or fill the `## YouTube` section of `competitor-list.md` in your project root with `youtube.com/@handle` URLs (with or without a trailing `/videos`) — the skill defaults to the first 5 and ignores any `### EXAMPLE` placeholder block.

## Output

Writes `research/YT-Competitor-Research_<timestamp>.html` and opens it in your default browser (macOS / Windows / Linux). The scrape steps are bash/awk/xargs one-liners: macOS, Linux, Windows via Git Bash.
