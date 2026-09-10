# Voice DNA (not built yet)

This file is the explicit voice rulebook `scriptwriter`, `hook-generator`, `carousel-generator`,
`dm-revival`, and `yt-description` read before writing anything in your voice: openers, fillers,
closers/CTAs, energy markers, structure patterns, themes, anti-patterns, each grounded in your own
top-performing videos.

It is generated, not typed: run the **`voice-corpus-builder`** skill (say "build my voice corpus").
It pulls your top YouTube uploads (yt-dlp) and Instagram reels (Apify MCP), transcribes them into
`voice-corpus/`, and drafts this file from the transcripts using
`.claude/skills/voice-corpus-builder/reference/voice-dna-template.md`. Until then the writing skills
fall back to the voice one-liner in `CLAUDE.md` and sound generic.
