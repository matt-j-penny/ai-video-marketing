# yt-description: setup

Writes the full YouTube description for a finished long-form video in the channel's live format. It pulls the newest published description off the channel as the skeleton, reads the word-for-word script from the `video-editor` job (or the Notion beat sheet), builds real chapter timestamps by word-indexing the final export, picks the link blocks from `references/links.md`, and hands back copy-paste-ready copy. Trigger it with "write the youtube description", "yt description", "description for this video", or "write my description".

## Prerequisites

- `yt-dlp`, `ffmpeg`/`ffprobe`, `jq`, `python3` (`python` on Windows), `uv` (checked by `check-setup.sh` at the repo root; `brew install yt-dlp ffmpeg jq uv` on macOS).
- Transcription runs on the shared faster-whisper venv at `~/.cache/content-os/whisper-venv`. `./setup.sh` at the repo root pre-builds it; otherwise the first `chapter_index.sh` run builds it with `uv` (a few hundred MB, one time). `CONTENT_OS_WHISPER_VENV` overrides the path, `YT_DESC_WHISPER_MODEL` overrides the `base.en` model.
- Notion MCP connected (`notion-fetch` for the beat-sheet lane, `notion-create-pages` for a missing page). The page lookup itself follows the "Resolve every video reference" rule in the repo-root `CLAUDE.md`, with the Data source ID from `notion-pipeline.md`.
- The sibling `video-editor` project at `~/Projects/video-editor` for the transcript lane (optional: without it the copy comes from the Notion beat sheet).
- Repo-root context files: `backbone/offer.md` (offer name and price for the CTA line) and `notion-pipeline.md`.

## Output

`descriptions/<job>_<YYYY-MM-DD>.md` in the repo, plus the raw description printed in chat as one fenced block. Scratch files (skeleton pull, word index, phrase list) live in the session scratchpad and are disposable.

## Gotchas

- The skeleton is pulled every run, never remembered. Claude passes `fetch_skeleton.sh --channel <the /videos URL of the channel in CLAUDE.md, Creator Profile>` (env `YT_DESC_CHANNEL` also works); a different channel is a different flag, not a script edit.
- Timestamps only ever come from the final exported file (`chapter_index.sh` + `find_times.py`); editing transcripts are for the text. A `find_times.py` score under 0.6 is not a usable timestamp.
- YouTube silently drops the whole chapter list if any rule breaks: first chapter `0:00`, at least 3 chapters, each 10s or longer, ascending.
- One CTA only: the community per `backbone/offer.md`. Nothing from its "What is NOT sold" list, no apply links, no call bookings, no invented URLs.
