# transcripts/ — conventions

Raw video transcripts, organized by **where they came from**. Keep this folder self-maintaining:
every transcript lands in one of the three subfolders below with the standard filename.
**Nothing loose at the top level.**

## Where it goes

| Subfolder | Holds | Produced by |
|-----------|-------|-------------|
| `url/` | Transcript of any video pulled from a URL (YouTube, IG, TikTok, X, etc.), yours or a competitor's. | `transcribe-url` skill (default output dir) |
| `local/` | Transcript of a file already on disk (e.g. something in `~/Downloads`). | `bash .claude/skills/voice-corpus-builder/scripts/transcribe-file.sh <file> transcripts/local/<slug>_<date>.txt` (same shared whisper venv) |
| `analysis/` | Video-*derived* docs that are **not** raw transcripts: script-structure beat-maps, packaging breakdowns. | scripting/research passes |

Your own curated top performers do NOT live here; they live in `voice-corpus/` (built by
`voice-corpus-builder`).

## Filename

```
<title-slug>_<YYYY-MM-DD>.md          # transcripts (url/ and local/)
<title-slug>_<YYYY-MM-DD>_STRUCTURE.md # analysis/ (script-structure docs)
```

- **slug** = the video title, lowercased, non-alphanumerics → `-`, collapsed, max 60 chars
  (`transcribe-url.sh` builds this automatically).
- **date** = the date you pulled it, *not* the upload date. The real source URL is always in the file's header.
- No video IDs in the filename; the canonical URL lives inside the file.

## Rules

- **Don't re-transcribe.** Search `transcripts/` for the URL/title first; if it's already here, read the existing file.
- **Never delete** existing transcripts. A repeat pull just writes a new dated file.
- Every transcript file starts with an H1 title and a metadata block (Source URL, Uploader, Uploaded, Duration), then `## Transcript` / `## Timestamped`.
