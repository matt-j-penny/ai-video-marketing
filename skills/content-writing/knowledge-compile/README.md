# knowledge-compile: setup

Refreshes `knowledge/`, the repo's short compiled memory layer (compiled, plain markdown). Six source-linked markdown pages (index, content opportunities, winning hooks, competitor patterns, positioning, script formats) that ideation, `scriptwriter`, and `hook-generator` read first instead of re-reading 100k+ words of raw reports and transcripts. Trigger it with "update knowledge", "compile knowledge", "refresh repo memory", "update the wiki", or "knowledge layer".

## Install

Drop this folder into `<project>/.claude/skills/knowledge-compile/`. Pure prompt skill: no scripts, no venv, no MCP. Only Python 3 (`python3`, or `python` on Windows; the one-liners resolve whichever exists) and `grep` are used, for the inline text-extraction and lint one-liners in SKILL.md.

## Prerequisites

The sources it compiles from live at the repo root, and it only reads them: `backbone/` (offer, ICP, messaging, vision), `voice-dna.md`, `voice-corpus/`, `research/`, `transcripts/{url,local,analysis}/`, `CLAUDE.md` Lab Notes / Gotchas section, and each skill's `SKILL.md`. Missing sources are skipped, not invented.

## When to run

Manually, after a research report lands, after a high-signal transcript, or after an offer/positioning change. Research skills never write into `knowledge/` on their own; this skill is the only writer. Step 3 of the workflow prints a "N days behind" warning per page so the gap is visible.

## Output

Rewrites only the affected pages in `knowledge/*.md`, each with `last_updated` and a `sources:` frontmatter list of real repo paths. Nothing else is touched.

## Gotchas

- Never `Read` a raw `research/*.html` (5-8 MB with embedded media). Use the text-extraction one-liner in SKILL.md.
- Every `sources:` path must exist on disk before a page is saved; dangling paths mean re-source or drop the claim.
- Retired or excluded offer names must not appear in `knowledge/`: build the sweep grep in SKILL.md from the "What is NOT sold" names in `backbone/offer.md` (skip if it says "none"); it must return nothing. Offer name and price come from `backbone/offer.md`, never hardcoded.
- `creator-ai-positioning.md` keeps its filename across lane changes because `scriptwriter` reads it by name.
