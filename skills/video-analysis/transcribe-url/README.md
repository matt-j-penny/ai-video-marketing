# transcribe-url — setup

Pulls a transcript from any public video URL and saves it as a markdown file with metadata, plain transcript, and timestamped segments. Works with YouTube, Instagram Reels, TikTok, X/Twitter, Vimeo, Facebook, LinkedIn, and anything else yt-dlp handles. Trigger it with phrases like "transcribe this link \<url\>", "transcribe this reel", "what does this video say", "pull transcript from \<url\>", or "get the transcript of this video".

## Install

Drop this folder into a skills directory:
- `<project>/.claude/skills/transcribe-url/` — for one project, or
- `~/.claude/skills/transcribe-url/` — to use it everywhere.

## Prerequisites

**1. System tools:** `yt-dlp`, `uv`, `python`, `ffmpeg` (macOS / Linux / Windows via Git Bash). `./setup.sh` at the repo root installs them and `./check-setup.sh` reports what is missing. On macOS, for example:

```
brew install yt-dlp uv python3 ffmpeg
```

- `yt-dlp` — downloads video metadata and audio.
- `uv` — builds the Python venv on first run (whisper fallback path only).
- `python` — used inline for caption parsing (YouTube fast path); the script probes `python3` then `python`, so the Windows install name works too. Whisper runs on a uv-managed Python 3.11 venv, not system python.
- `ffmpeg` — required by yt-dlp when extracting audio with `-x --audio-format mp3` (the whisper fallback path).

**First-run note (whisper fallback only).** YouTube URLs with auto-generated captions skip whisper entirely and finish in about 2 seconds. For everything else, the script downloads audio and transcribes it with faster-whisper. The first time that path runs, it builds a Python venv at `~/.cache/content-os/whisper-venv` — expect roughly 700 MB of one-time downloads (packages + the `small.en` model weights) and a few minutes to complete. Subsequent runs reuse the venv and finish without any install step. If the first build gets interrupted, the script detects the half-built venv via a `.deps-ok` sentinel file and rebuilds cleanly on the next run.

## Output

Writes `transcripts/url/<title-slug>_<YYYY-MM-DD>.md`. The output directory is the second argument to the script and defaults to `transcripts/url/` relative to your working directory (run from the repo root, or pass an absolute path); the script prints the absolute path of the file it wrote, and Claude will display it after the run completes. Pulling the same title twice on one day writes `..._2.md`, `..._3.md` instead of overwriting.

Each file contains video metadata (source URL, uploader, upload date, duration), a full plain-text transcript block, and a timestamped version with `[MM:SS]` markers. YouTube caption files also note the method used; whisper-transcribed files include the detected language and model name.

The default whisper model is `small.en`. To use a larger model for better accuracy on heavy accents or music-heavy audio, set the environment variable before triggering: `WHISPER_MODEL=medium.en`.
