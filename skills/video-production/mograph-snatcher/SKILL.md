---
name: mograph-snatcher
description: >
  Give it a YouTube URL. It scans the video for motion graphics (titles, lower-thirds, stat hits,
  charts, callouts, kinetic type, animated overlays), extracts each one with dense frames, analyzes
  what the animation does, and recreates every graphic as a reusable HyperFrames template with
  variables. Use when the user says "/mograph-snatcher", "snatch the motion graphics from <youtube url>",
  "turn the graphics in this video into templates", or gives a YouTube URL and wants its motion
  graphics recreated.
---

# mograph-snatcher

The pipeline is: URL, download, sparse scan, find graphics, dense frames per graphic, analysis, then a HyperFrames template per graphic.

`S = <folder containing this SKILL.md>/scripts/snatch.py` (run it with `uv run -q $S ...`; Pillow installs automatically).

Requires `uv`, `yt-dlp`, `ffmpeg`, Node (for `npx hyperframes`), and the HyperFrames skills (`/hyperframes`, `/hyperframes-core`, `/motion-graphics`). If those skills are missing, install them with `npx skills add heygen-com/hyperframes`.
`OUT = ./snatched/<video-id>/` in the current working directory.

## 1. Download

```bash
uv run -q $S download "<url>" ./snatched
```

The download goes into `./snatched/<id>/` (printed as `workdir`) and is capped at 1080p. `meta.json` holds the title, channel, duration, and fps.

## 2. Sparse scan to find the graphics

```bash
uv run -q $S scan $OUT --every 2
```

This writes `scan/sheet-NN.jpg`. Each sheet is a 5×4 grid of frames, one every 2s, and every frame is stamped with its timestamp. For a video over 20 minutes use `--every 3`. Use `--every 1` only if the graphics are very short. If the user only wants part of the video, add `--until <seconds>`, and use the same limit for the rest of the run.

**Read every sheet.** A frame counts as a motion graphic when it contains designed, added-in-post elements:
- titles, kinetic text, or big words on screen
- lower-thirds, name bars, or callout boxes
- numbers, stats, counters, charts, or graphs
- icons, logos, stings, maps, or UI/social cards (tweets, headlines)
- animated shapes, transitions, or full-screen designed scenes

These do **not** count: plain burned-in subtitles, raw b-roll or footage, the talking head on its own, or a static channel watermark.

Group consecutive hits into segments. For each one, pad the range by about 1s on each side (one scan step) so that you catch the in-animation and out-animation. Clamp it to [0, duration]. Merge segments that are less than 1s apart, unless they are clearly different graphics. A full-screen designed scene that changes its content but keeps the same design system (same background and type, new photos and words) is **one** segment. Its template covers one beat, and the analysis notes the other beats. Write `OUT/segments.json`:

```json
[{"id": "seg-01", "start": 12.0, "end": 17.5, "kind": "lower-third", "summary": "Name bar slides in from left, white on red"}]
```

Show the user the list as a table with id, timecode, kind, and summary, then continue without waiting. If no graphics are found, say so and stop.

## 3. Dense capture per segment

```bash
uv run -q $S dense $OUT seg-01 <start> <end> --fps 6
```

This writes `segments/seg-01/clip.mp4`, `frames/`, and labeled `sheet-NN.jpg` files. Use `--fps 10` for fast graphics under 2s. Read every sheet for the segment. After reading the sheets, refine the start and end to where the graphic really begins (first element appears) and ends (last element is gone). If the refined edges hit the padded bounds, the graphic may continue past them, so re-run `dense` with a wider range.

## 4. Analyze each graphic

Write `segments/<id>/analysis.md` with these sections:

- **What it is**: the category and its purpose in one line.
- **Layout**: canvas position of each element (as % of frame), sizes, and safe-area use. Say whether it is an overlay on footage or a full-screen design.
- **Style**: palette as hex (estimate it from the frames), fonts (closest Google Font plus its weight), corner radius, strokes, shadows, blur, and texture.
- **Motion timeline**: one row per element. Each row gives the time offset from graphic start, the property (position, scale, opacity, mask/wipe, clip, blur, rotation, letter stagger, or count), from and to values, duration, easing feel (snappy ease-out, overshoot or back, elastic, linear), and stagger. Get these from the frame-to-frame differences in the dense sheets.
- **Hold and exit**: how long the graphic holds and how it leaves.
- **Not reproducible**: anything a template cannot do on its own, for example graphics occluded by the speaker, which needs a subject matte.
- **Variables**: the parts that should be editable in a template. Usually that means text strings, numbers, colors, the image or logo, and sometimes duration.

## 5. Build one HyperFrames template per segment

For each segment, run `/motion-graphics`. Read `/hyperframes` and `/hyperframes-core` first if they are not already loaded. Follow these overrides:

- `PROJECT_DIR = OUT/templates/<id>-<kind>/`
- The brief comes from `analysis.md` plus the segment's dense sheets, which are the visual reference. **Skip the director's clarifying question**, because the reference answers it. The goal is a faithful recreation of the layout, style, and motion timing, not a reinterpretation.
- Make it a **template**. Declare every item from the analysis's Variables list in `data-composition-variables` on `<html>`, with defaults taken from the original's content. Bind them with `data-var-text`, `data-var-src`, or `var(--id)`. Colors go in `color` variables.
- If the original overlays footage, build it on a transparent background so it can be rendered as a webm/mov overlay. Do not embed the source footage.
- Do not copy logos, faces, or footage from the source. Use placeholders that are exposed as `data-var-src` variables. Write simple SVG placeholders into `assets/`.
- Fonts: `lint` requires a local `@font-face` for every named family. Download the closest Google Fonts as TTF files (for example from `github.com/google/fonts/raw/main/ofl/<family>/...`) into a shared `templates/_fonts/`, then copy that folder into each project as `fonts/`.
- Hidden starting states: put `opacity: 0` in CSS or inline, or use `fromTo`. Do not use `tl.set(..., 0)`, because frame 0 ignores it. To reveal text word by word, read the text with `window.__hyperframes.getVariables()`, split it into spans in JS, and then build the timeline.
- If `check` flags contrast on a palette taken from the source, keep the source colour (it is a variable anyway) and record the failure in INDEX.md.
- Verify with `npx hyperframes lint`, `npx hyperframes check`, and the proof snapshots. Compare the snapshot contact sheet side by side with the segment's `sheet-01.jpg` and fix the biggest mismatches, with at most 2 repair passes.
- **Do not render** and do not ask the render question for each template. Stop after verification and move on to the next segment.

You can build segments in parallel with subagents only if the user asks for that. Otherwise build them sequentially.

## 6. Finish

Write `OUT/INDEX.md`. It should hold the video title and URL, plus a table with one row per template giving the id, source timecode (as a `&t=` link), kind, variables, template path, and verification status. Tell the user the path and how to preview a template:

```bash
cd OUT/templates/<id>-<kind> && npx hyperframes preview
```

`source.mp4` and the `scan/frames` folder can be large. Offer to delete them, but never delete them without asking.
