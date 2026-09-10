# scriptwriter: setup

Turns a pick (a winning video from research, with its URL) or a raw idea into a filmable beat sheet in Notion, written in the creator's own voice. The trick is imitation, not description: every draft is written next to 2-3 verbatim transcripts of the creator's own top-performing videos in the same format, with `voice-dna.md` as the rulebook and a fresh-context voice-lint pass before anything lands in Notion. Trigger it with "write a script", "script this", "beat sheet", "script the pick", or "write the reel".

## Install

Drop this folder into `<project>/.claude/skills/scriptwriter/`. It expects the `transcribe-url` skill next to it (`.claude/skills/transcribe-url/`); Step 2 shells out to that skill's script for source-video transcripts and does not carry a transcription engine of its own. When copying or zipping the folder for someone else, exclude `__pycache__/` and `.DS_Store`.

## Prerequisites

1. **Python 3.** `scripts/find_voice.py` is stdlib-only, no pip install.
2. **Notion MCP** (OAuth-connected). The finished beat sheet is created with `notion-create-pages`; the database IDs and property shapes come from `notion-pipeline.md` at your project root.
3. **`transcribe-url` skill installed** plus its prerequisites (`yt-dlp`, `uv`, `ffmpeg`). Only needed when the pick has a source URL. Its script builds the shared faster-whisper venv on first use, so the first run with a non-YouTube source is slow.
4. **Repo-root context files:** `voice-corpus/` (see below), `voice-dna.md`, `notion-pipeline.md`, `backbone/offer.md` + `backbone/messaging.md` (CTA, comment keyword, not-sold list, and proof come from here, never hardcoded).
5. **Optional, improves results:** `knowledge/` (`winning-hooks.md`, `reusable-script-formats.md`, `creator-ai-positioning.md`). It starts empty and fills in once `knowledge-compile` has run; on a fresh install the skill leans on `backbone/` + the corpus instead.

## The voice corpus contract

`voice-corpus/` is built by the `voice-corpus-builder` skill: one markdown file per top video, `<id>.md`, plus an `index.md` that `find_voice.py` skips. Each entry opens with YAML-style frontmatter that `find_voice.py` slices on: `id`, `platform` (`instagram` / `youtube` / `tiktok`), `url`, `views` (integer, ranks results), `likes` (tie-breaker), `date`, `era` (current vs older positioning), `format`, `hook_type`, `spoken_hook`. Body after the frontmatter = the verbatim transcript. Run `python3 .claude/skills/scriptwriter/scripts/find_voice.py --list` from the project root (`python` on Windows) to see the tags in your corpus; if the folder is missing the script exits with a pointer to `voice-corpus-builder`.

## Output

The beat sheet is shown in chat, iterated, then written as a Notion page (Status `Scripting`, Format set, Type left blank for the creator to tag). Source transcripts from Step 2 land in `transcripts/url/` at your project root.

## Gotchas

- Long-form source transcripts stay inside the Step 2 subagent; only the format skeleton and the spoken intro reach the main context.
- Short-form hook = the first spoken line; long-form hook = the video title. The skill never substitutes a caption.
- One CTA only: a comment-keyword giveaway or a direct mention of the offer (name/price per `backbone/offer.md`). Never anything on `backbone/offer.md`'s "What is NOT sold" list.
