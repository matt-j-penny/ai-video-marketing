# voice-corpus/ — your own top videos, verbatim

The few-shot source of truth for `scriptwriter`: every script is drafted next to 2-3 verbatim
transcripts of YOUR best-performing videos in the same format, so the model imitates instead of
describing. Empty until you build it.

**Build it:** say **"build my voice corpus"** (the `voice-corpus-builder` skill). It ranks your
YouTube uploads by views and your Instagram reels by plays, transcribes the winners, writes one
tagged markdown file per video here (`yt-<id>.md`, `ig-<shortcode>.md`), regenerates `index.md`,
and drafts `voice-dna.md` at the project root. Re-run it whenever a new batch of winners lands (it
adds, never deletes).

Query it with `.claude/skills/scriptwriter/scripts/find_voice.py --list`; don't read every file.
