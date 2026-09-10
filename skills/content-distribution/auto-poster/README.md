# auto-poster — setup

Posts or schedules a video through Zernio. Give Claude a local video path or a public video URL and it handles the rest: uploads the file, generates a caption if you don't provide one (transcribes the video with faster-whisper), and publishes or schedules across your connected platforms (default = every account in `.env`). Trigger phrases: "post this video", "post /path/to/video.mp4", "schedule this video", "queue this video", "publish reel", "post to instagram", "post to zernio".

## Install

Lives at `.claude/skills/auto-poster/` in this project. Every command in this README and in `SKILL.md` runs from the project root (`python3 .claude/skills/auto-poster/scripts/...`; on Windows use `python` in place of `python3`).

## Prerequisites

**1. Zernio account and credentials (required).** You need an active Zernio account with at least one connected social platform. Copy `.env.example` to `.env` in the skill folder (`.claude/skills/auto-poster/.env`) and fill in your own values:

```
ZERNIO_API_KEY=
# only the ones you have connected; every key present is a default posting target
ZERNIO_ACCOUNT_INSTAGRAM=
ZERNIO_ACCOUNT_TIKTOK=
ZERNIO_ACCOUNT_YOUTUBE=
ZERNIO_ACCOUNT_LINKEDIN=
ZERNIO_ACCOUNT_FACEBOOK=
ZERNIO_ACCOUNT_THREADS=
```

Only include the platforms you have connected; leave the rest blank or delete them. Values in this `.env` win over any `ZERNIO_*` already exported in your shell. To get the account IDs, fill in `ZERNIO_API_KEY` first, then run from the project root:

```
python3 .claude/skills/auto-poster/scripts/post_to_zernio.py --list-accounts
```

It prints one paste-ready `ZERNIO_ACCOUNT_<PLATFORM>=<id>    # platform: display name` line per connected account (the key itself is never printed). Paste the ones you want as default posting targets into `.env`. Account IDs change on every OAuth reconnect in Zernio; when a post fails with "accounts do not belong to this user", re-run that command and update the IDs in `.env`.

Optional keys (add only if needed):

```
ZERNIO_API_URL=https://zernio.com/api/v1
ZERNIO_PROFILE_ID=
ZERNIO_QUEUE_ID=
ZERNIO_TIMEZONE=America/New_York
```

`ZERNIO_PROFILE_ID` is required only if you use `addToQueue` mode. `ZERNIO_TIMEZONE` is your IANA timezone (`America/New_York` is just an example) and is required only for `customScheduled` mode (`--timezone` overrides it per call; `shareNow` ignores it).

**2. System tools.** `python3`, `ffmpeg`, `curl`, and `uv` (macOS, Linux, Windows via Git Bash). On macOS:

```
brew install ffmpeg curl python3 uv
```

On Linux, install the equivalents via your package manager (`apt install ffmpeg curl python3` plus `uv` from astral.sh). `./check-setup.sh` at the repo root reports anything missing.

`ffmpeg` is used on every run to extract audio before transcription. `curl` is used by the posting script. `uv` builds the transcription venv once.

**First-run note:** if you post without providing a caption, the transcriber uses the shared faster-whisper engine every skill in this repo uses: a persistent venv at `~/.cache/content-os/whisper-venv`, built by `uv` the first time any transcription runs (or by `./setup.sh` from the repo root; about 200 MB plus the model download, a couple of minutes). `CONTENT_OS_WHISPER_VENV` overrides the venv location. Every subsequent run reuses it and transcription takes a few seconds. The model defaults to `tiny.en`; set `AUTO_POSTER_WHISPER_MODEL` (e.g. `base.en`) for higher quality.

## Output

The posting script prints a JSON result to stdout with the Zernio post ID, publish status, and per-platform URLs and errors. For `customScheduled` mode, include a `--due-at` time in ISO format (e.g. `2026-05-18T12:00:00`) plus a timezone (`--timezone America/New_York` style, or `ZERNIO_TIMEZONE` in `.env`).

## Known gotchas

- Threads captions silently fail over 500 characters: post a trimmed Threads version in its own call.
- Sources over about 100 MB hang Instagram at `awaiting-finalize`: re-encode to 1080p first (`ffmpeg ... -crf 20 -maxrate 12M`), keep the framing.
- A stuck Instagram post leaves a live container open: never re-post until the old record is deleted, or it double-posts.
- Full details and the exact ffmpeg recipe are in `SKILL.md` under "Known platform gotchas".
