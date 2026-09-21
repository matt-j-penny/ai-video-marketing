---
name: full-edit
description: "End-to-end Remotion edit: rough-cut the raw talking-head footage (silences/bad takes) with ffmpeg, then plan and build motion graphics across the whole video in a Remotion composition and render the finished MP4 — full-screen, overlay, and split layouts, verified. Runs with the user's saved preferences (canvas, brand, cut aggressiveness, graphic density, layouts) and runs a first-time setup if none exist. Use when the user wants a complete pass from raw clip to a graphics-finished video in one go (e.g. '/full-edit'). Orchestrates transcribe, rough-cut, level-audio, and storyboard."
metadata:
  version: 2.0.0
  last_updated: 2026-09-21
---

# Full Edit

Raw clip in, graphics-finished video out, all in Remotion and ffmpeg. Two phases: cut it, then cover it in motion graphics that are rendered and placed, not just planned. Brand-matched, sleek, fast-moving, never a dead stretch.

## Ground Rules

- **Always start from scratch.** Never look for, open, reuse, or learn from existing edits, transcripts, cuts, compositions, renders, or project folders derived from the source file (including earlier runs on the same clip). Work only from the raw source and the saved preferences. Every run builds a fresh project and re-transcribes the raw source.
- **Never ask for permission or confirmation.** Once everything required is in hand, run the whole edit start to finish: no approvals, no "should I proceed", no checking in between steps. The only reason to ask the user anything is a missing required input (source path, saved preferences, brand file, API keys), and then ask up front, before editing starts.

## Freshness Check

Compare `last_updated` to today. Warn if >2 weeks stale, then continue.

## Requirements

Check every run, before anything else:

- **`ffmpeg`** and **`node`** on PATH (`ffmpeg -version`, `node -v`). Remotion installs through `npx`. If either is missing, stop and tell the user what to install.
- **`DEEPGRAM_API_KEY`** — word-level transcription (`transcribe` falls back to ElevenLabs, then local Whisper, without it).
- **`BRAVE_API_KEY`** — web search for real logos and reference images the graphics need.

Look for each key in the `env` block of `~/.claude/settings.json` or the shell environment. If a key is missing, ask the user to add it to `~/.claude/settings.json` themselves (Deepgram: https://console.deepgram.com, Brave: https://brave.com/search/api), or to skip it. Never write or request a key in chat. Skipping Deepgram means the Whisper/ElevenLabs fallback; skipping Brave means no real logos or reference images.

## Preferences

Preferences live in `~/.claude/full-edit-preferences.md` (per user, shared across projects).

- **File exists:** read it, tell the user in one line which preferences are being applied, and use them for the rest of the run. Explicit instructions in the current request override the file for that run only.
- **File missing (or the user says "reset preferences"):** preferences must exist before any editing, so run setup first. Ask these in one batch, offer the default for each, then write the answers to the file:
  1. Output canvas — 9:16, 16:9, or 1:1 (default 9:16)
  2. Brand reference — path/URL to a DESIGN.md or other brand file. If they have none, run `create-design-md` (guided questions, or from their site if they have one), then save the resulting DESIGN.md path
  3. Cut aggressiveness — aggressive (0.3s gap threshold), moderate (0.4s, `rough-cut`'s default), or light (0.6s). Default: moderate
  4. Graphic density — dense (default), moderate, or sparse
  5. Allowed layouts — any of `full-screen`, `overlay`, `split` (default: all)
  6. Sections to keep plain talking-head (e.g. "first 5 seconds", "serious moments"), or none

File format:

```markdown
# Full Edit Preferences
- canvas: 9:16
- brand: <path to DESIGN.md or brand file>
- cut: moderate
- density: dense
- layouts: full-screen, overlay, split
- plain_sections: none
```

Then continue with the run.

## Before Starting

1. Path to the raw source video.
2. Everything else comes from preferences. If the brand entry is empty, run `create-design-md` rather than inventing a palette.

## Phase 1 — Rough cut

1. Run `transcribe` on the raw source.
2. Run `rough-cut` as a pure ffmpeg edit (no editor connected) with the preferred gap threshold. Silences and bad takes out.
3. Run `level-audio` on the result if its loudness check says the narration needs it.
4. Run `transcribe` again on the cut video so every downstream timestamp is on the edited timeline.

Don't skip or abbreviate this; graphics timed against un-cut footage drift the moment cuts change.

## Phase 2 — Motion graphics

Run the `storyboard` skill on the cut video from Phase 1, but **skip its AI image generation entirely**: no storyboard images, no overview image, no image-matching feedback loop. Plan beats as text (timestamps, transcript excerpt, layout, visual idea), then build each scene as HTML/React straight from the beat plan and the brand file, then Composition and Final Video, and run its Review Loop against the rendered frames and the beat plan instead of storyboard images. This invocation counts as the explicit request `storyboard` requires. Apply the preferences:

- **Canvas** sets the Remotion composition size; scenes are built for it.
- **Brand** file supplies colors, type, and components for every scene.
- **Density** sets beat frequency: dense is roughly 1-2 graphics per 15-20s, moderate about half that, sparse only the strongest moments. Every graphic still needs a genuine showable; never invent one to hit a quota.
- **Layouts** limits what each graphic beat may use:
  - `full-screen` — opaque scene covering the footage (stat reveal, title card, section break)
  - `overlay` — transparent scene over the visible footage (lower-third, callout), placed clear of the face
  - `split` — footage scaled and docked to part of the frame while a moving scene fills the rest; confirm the footage's rect and the scene's cutout line up in rendered frames, not just in numbers
- **Plain sections** get no graphics and no zooms.
- Use Brave search for real logos and reference images when a beat calls for one (found, not AI-generated). Stats and numbers come only from what is said in the video, never from search.

Nothing static for more than ~4-5s; quick in/out; keep some plain talking-head stretches so it reads sleek, not noisy.

## Common Mistakes

1. Skipping the rough cut, or not re-transcribing the cut video.
2. Every beat becoming a graphic: a video with no plain talking-head stretches reads as noisy.
3. `overlay` scenes with an opaque background: they cover the footage instead of sitting over it.
4. A `split` scene whose cutout doesn't match the footage's docked rect.
5. Reporting done before the Review Loop is clean.
6. Asking for or writing API keys in chat; only point the user to `~/.claude/settings.json`.
7. Asking for permission or confirmation when nothing required is missing, or reusing any earlier edit of the same source.
