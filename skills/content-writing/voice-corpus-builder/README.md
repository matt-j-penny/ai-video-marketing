# voice-corpus-builder: setup

Builds (or refreshes) `voice-corpus/` at the project root from the creator's OWN top-performing
videos, then drafts `voice-dna.md` from it. This is the few-shot source `scriptwriter` needs before
it will draft anything, so it runs once at onboarding ("build my voice corpus") and again whenever
a new batch of winners lands. Adds/overwrites entries; never deletes.

## What it needs

- **yt-dlp** (YouTube ranking + captions), **ffmpeg** + **uv** (the shared faster-whisper venv at
  `~/.cache/content-os/whisper-venv`, built on first use or by `./setup.sh`), **jq** + **curl**
  (Instagram dataset + reel downloads), **python3** (stdlib only).
- **Apify MCP** connected in Claude Code for the Instagram half (`apify/instagram-post-scraper`,
  `detailedData`; roughly $0.18 for one handle). YouTube needs no account.
- Repo-root context it reads: the creator's handles (CLAUDE.md Creator Profile or `brand-kit.md`).
  It writes `voice-corpus/*.md`, `voice-corpus/index.md`, and (via Claude) `voice-dna.md`.

## Flow

`yt-top.sh` ranks the channel → `yt-entry.sh` per keeper (captions, whisper only if a video has none) ·
Apify scrape → `ig-entries.sh` ranks by plays/likes, curls + transcribes each reel · Claude tags each
entry with `tag.py` (vocabulary in `reference/tags.md`) · `build-index.py` · Claude drafts
`voice-dna.md` from `reference/voice-dna-template.md`. All scripts write to `<project>/voice-corpus/`
(`VOICE_CORPUS_DIR` overrides, for tests).

## Gotchas

- Signed Instagram CDN URLs expire in hours: run `ig-entries.sh` right after the scrape.
- YouTube json3 auto-captions: events carry no separator between them; `yt-entry.sh` joins them with a
  space (otherwise words fuse).
- A channel with 6 uploads contributes 6 entries; under ~10 total the corpus is thin and the rulebook
  says so at the top of `voice-dna.md`.
