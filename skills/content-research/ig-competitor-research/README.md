# ig-competitor-research — setup

Scans Instagram competitors, ranks their last-week posts by likes + breakout score, transcribes/analyzes each winner, and builds a self-contained HTML report. Claude drives the whole thing — you just trigger it ("research @handle_a @handle_b", or "content research" to use your competitor list).

## Install

Drop this folder into a skills directory:
- `<project>/.claude/skills/ig-competitor-research/` — for one project, or
- `~/.claude/skills/ig-competitor-research/` — to use it everywhere.

When copying/zipping the folder for someone else, exclude `__pycache__/` and `.DS_Store` (local machine artifacts that regenerate on their own).

## Prerequisites

**1. Apify account + MCP (required, paid).** The scrape is one call to the `apify/instagram-post-scraper` actor. Connect the **Apify MCP server** in Claude Code and have credit on your account. Cost is ~$0.003/post (~$0.11 for 3 handles, ~$0.18 for 5). No API token or env vars — the OAuth MCP connection handles auth, and the dataset is pulled back through that same MCP (`get-dataset-items`).

**2. System tools.** Install these (the scripts call them directly):
- `uv` — https://docs.astral.sh/uv/ (builds the two shared venvs on first use, no manual pip: faster-whisper at `~/.cache/content-os/whisper-venv` for reel transcription, pillow at `~/.cache/content-os/pillow-venv` for the report; `scripts/build-report.sh` is the one entry point for the report build)
- `ffmpeg` + `ffprobe` — keyframes + audio extraction
- `jq` — extracts the scraped dataset to disk (recent macOS ships it; older macOS/Linux: install it)

`python3` (`python` on Windows) and `curl` are assumed present. `./setup.sh` at the repo root installs the tools (by hand on macOS: `brew install uv ffmpeg jq`).

The first reel breakdown does a one-time ~700 MB of downloads (Python 3.11 via uv if needed, faster-whisper wheels, and the `small.en` model weights into `~/.cache`) — give it network and a few minutes; every later run reuses the caches.

**3. Handles.** Either name them inline when you trigger the skill, or create a `competitor-list.md` in your project root with an `## Instagram` section of `instagram.com/<handle>/` URLs — the skill defaults to the first 5.

## Output

Writes `research/IG-Competitor-Research_<timestamp>.html` (built by `bash .claude/skills/ig-competitor-research/scripts/build-report.sh <RUN_DIR> <out.html> --open`) and auto-opens it in your default browser (macOS `open`, Linux `xdg-open`, Windows `start "" <file>`, via Python's stdlib `webbrowser`). The pipeline is bash + `/tmp`: macOS, Linux, Windows via Git Bash; `./setup.sh` at the repo root installs the tools.
