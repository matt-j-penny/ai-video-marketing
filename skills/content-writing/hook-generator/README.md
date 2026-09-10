# hook-generator — setup

Generates spoken video hooks from a bank of 404 proven frameworks scraped from top-performing short-form reels. You give Claude a topic, a rough concept, or a full script; it picks the best-fit hook structures, pulls the highest-performing frameworks from the data, and writes 6–8 spoken hook options in your voice — each one tied to a real framework and its view-count proof.

Trigger phrases: write a hook, write me a hook, hook for this video, hook for my video, generate hooks, give me hooks, hook ideas, viral hook, scroll stopper, opening line, hook generator, need a hook, what's a good hook for.

## Install

Drop this folder into a skills directory:
- `<project>/.claude/skills/hook-generator/` — for one project, or
- `~/.claude/skills/hook-generator/` — to use it everywhere.

When copying or zipping the folder for someone else, exclude `__pycache__/` and `.DS_Store` (local artifacts that regenerate on their own).

## Prerequisites

**1. Python 3 (required).** The skill queries the hook bank via `scripts/find_hooks.py`, which uses only Python stdlib — no pip install needed. Needs Python 3.8+ on PATH (`python3 --version`; `python --version` on Windows). macOS: accept the Command Line Tools prompt or run `xcode-select --install`; Windows/Linux: install from python.org or your package manager. Commands in SKILL.md are written to run from the repo root: `python3 .claude/skills/hook-generator/scripts/find_hooks.py --list` (`python` on Windows).

**2. Hook bank CSV (included).** `404-kallaway-hooks.csv` ships inside the skill folder. Nothing to download. Provenance: the bank = the public Kallaway 404-hooks dataset (creator handles and source links are kept intact per row).

**3. Three repo files the package builds for you.** The skill reads voice, proof, and your own winning hooks from the repo root; nothing is hardcoded in the skill.

- `voice-dna.md`: your speech patterns, openers, closers, slang, and tone markers. Written by the `voice-corpus-builder` skill from your own top videos ("build my voice corpus"). Until then, Claude falls back to the Voice/Tone one-liner in `CLAUDE.md`.

- `backbone/messaging.md`: your positioning plus a "proof bank" of real numbers and wins the hooks can quote. Written when you say "apply my brand kit" (from `brand-kit.md`).

- `knowledge/winning-hooks.md`: hook patterns that have already worked for you, proof-linked. Written by the `knowledge-compile` skill ("compile knowledge") after your first research runs. Optional: the skill only reads it if it exists.

If a file is missing, Claude still runs but leans on the bank alone, so the output is more generic until the file lands.

## Output

All output is delivered in chat. Claude presents 6–8 hook options grouped by structure, each showing the hook line, the framework it's built on, and the source view count. It ends with a single recommendation. No files are written.
