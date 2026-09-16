---
name: capcut-full-edit
description: "End-to-end CapCut edit: rough-cut the raw footage (silences/bad takes), then plan and BUILD motion graphics across the whole video as real overlay assets placed on new CapCut overlay tracks — full-screen graphics, on-screen overlays (e.g. lower-third callouts), and split layouts (footage cropped/repositioned, e.g. to 9:16 docked to one side, with a graphic filling the rest). Use when the user wants a complete pass from raw clip to a graphics-finished CapCut draft in one go (e.g. '/full-edit'). Orchestrates capcut-rough-cut, capcut-beat-detector, the motion-graphics skill, and the bridge's overlay/transform commands, ending in the add-motion-graphics verification loop."
metadata:
  version: 1.0.0
  last_updated: 2026-09-16
---

# CapCut Full Edit

Raw clip in, graphics-finished CapCut draft out. Two phases: cut it, then cover it in motion graphics that are actually rendered and placed — not just planned. Brand-matched, sleek, fast-moving, never a dead stretch (same bar as `capcut-add-motion-graphics`, applied from the start of a project instead of onto an existing draft).

## Freshness Check

Compare `last_updated` to today. Warn if >2 weeks stale, then continue.

## Before Starting

1. Path to the raw source video, and a draft name for the new CapCut project.
2. Brand reference (colors/fonts/voice) — check the project for one; ask before inventing a palette if none exists.
3. Output canvas — confirm aspect (9:16, 16:9, 1:1) before doing any split-layout geometry (phase 2, step 3c), since the crop/dock math depends on it.
4. Cut aggressiveness — defaults to `capcut-rough-cut`'s aggressive default (0.3s gap threshold) unless told otherwise.

## Phase 1 — Rough cut

Run `capcut-transcribe` (if no transcript yet) then `capcut-rough-cut` in full, exactly as documented there — silences and bad takes out, draft built via `replay`. Don't skip or abbreviate this; everything downstream (beat timing, graphic placement) is built on the resulting edited timeline.

## Phase 2 — Plan and build motion graphics

### 1. Plan the beats

Run `capcut-beat-detector` against the rough-cut's transcript + `cuts.json`. For this workflow, push density toward the denser end of its guidance (roughly 1-2 per 15-20s, denser where the content supports it) — "never nothing happening" means real gaps get filled, but every beat still needs a genuine showable, never invented to hit a quota.

For each beat with `suggestedAction: "graphic"`, `capcut-beat-detector` also tags a `layout`:

- **`full-screen`** — own opaque background; original footage fully hidden for this span (a stat reveal, a title card, a section break).
- **`overlay`** — transparent graphic over the still-visible footage (a lower-third, a callout, a stat card sitting over the talking head).
- **`split`** — footage cropped/repositioned to occupy part of the frame (e.g. a 9:16 crop docked to one third) while a graphic fills the rest.

Beats with `suggestedAction: "zoom"` go to `capcut-zoom-highlights` instead — a camera move, not a new asset. Run that pass too if any exist; it composites fine alongside the graphics below since it only transforms the main-track clip.

### 2. Check the registry before hand-building anything

Before authoring a graphic from scratch, check the `hyperframes-registry` skill for an existing block that fits (stat counters, callouts, lower-thirds, transitions, chart types, etc.) — faster, and a maintained block is more likely to already look sleek/professional than a first-draft custom one. Fall back to hand-authoring with the `motion-graphics` skill only when nothing fits.

### 3. Build each graphic

Use the `motion-graphics` skill (or a placed registry block) for the actual authoring — kinetic typography, a stat count-up, a callout, a lower-third, a transition card — matched to the project's brand (colors/fonts/voice from Before Starting). Fast-moving: quick in/out, no graphic sitting static and unchanging for more than ~4-5s. Export target depends on layout:

**3a. `full-screen`** — render as an opaque MP4/MOV (no alpha needed, it covers the frame entirely). Duration matches the beat's `start`/`end`.

**3b. `overlay`** — render with an alpha channel (ProRes 4444), transparent everywhere except the graphic element itself, so the footage underneath stays visible. Position it clear of the face per `capcut-beat-detector`'s beat context (check the beat's role/line — don't cover a talking face with a lower-third that overlaps it).

**3c. `split`** — two things to build:
  - The footage's target rect on the canvas (e.g. right third, 9:16 sub-frame). Compute a starting `transform` guess for the main-track segment (scale to fit the rect's height or width, whichever is the binding constraint against the canvas, then center within the rect), apply it with the bridge's `transform` command, then **verify with `shot` and nudge `scale`/`x`/`y` iteratively until the footage visually fills exactly the intended rect** — like `capcut-zoom-highlights`, this geometry isn't derivable to pixel precision from the bridge alone, so converge visually rather than trusting a first-pass number. Once correct for a given canvas/source combo, the same values can be reused for the rest of that video's split beats.
  - The "rest of the frame" graphic: render with alpha, canvas-sized to the full draft canvas, fully transparent in exactly the footage's target rect (so the transformed clip shows through with nothing double-covering it) and opaque/animated everywhere else. This is the "other things happening on the left side" — it should itself be moving (bullets appearing, a chart building, icons animating in), not a static panel.

### 4. Place every graphic

```bash
BRIDGE="${CLAUDE_SKILL_DIR}/../bridge/capcut-bridge.py"
uv run "$BRIDGE" add-overlay <draft> <rendered.mov> --at <beat-start> --dur <beat-duration> --level <N> --mute
```

Each `--level` is its own overlay track (a new video channel in the CapCut UI) — the bridge creates one automatically per level. Use a fresh level whenever two graphics' time ranges overlap; reuse a level for non-overlapping ones to avoid an unbounded pile of tracks. `--mute` unless a graphic genuinely carries its own audio that should play.

For `split` beats, place the "rest of frame" graphic as an overlay (step 4 above) and apply the footage `transform` (step 3c) as a separate `transform` call on the main-track segment — two operations for one beat.

### 5. Verification loop

Same loop as `capcut-add-motion-graphics` — run it in full, don't abbreviate:

1. `open` the draft, walk it in 2-3s intervals with `seek` → `shot`.
2. At each interval, confirm something is visibly different from the last — flag any stretch of no change beyond ~3-4s.
3. Fill every flagged gap with a beat (graphic, zoom, or caption emphasis) and re-check it.
4. Full end-to-end pass: brand colors/fonts consistent across every graphic, nothing overlapping/cluttered, no `split` rect misaligned (footage bleeding outside its intended third, or a gap between footage and its graphic), pacing genuinely fast (nothing static past ~4-5s).
5. Only report done once this pass is clean — fix and re-loop otherwise.

## Common Mistakes

1. **Skipping or abbreviating the rough cut** — graphics timed against un-cut footage drift the moment silences/bad takes are removed later.
2. **Hand-authoring a graphic without checking the registry first** — slower, and more likely to look rough.
3. **`overlay` graphics rendered without alpha** — covers the footage entirely instead of sitting over it; always ProRes 4444 with real transparency for `overlay`/`split`-graphic layouts.
4. **Trusting a first-pass `transform` number for `split` layouts** — always verify with `shot` and nudge; the geometry isn't exact on the first try.
5. **A `split` graphic whose transparent cutout doesn't match the footage's actual transformed rect** — the two are built somewhat independently (step 3c); double check they align once both are placed, don't assume the numbers matched.
6. **Every beat becoming a graphic** — reserve `graphic` for real showables (per `capcut-beat-detector`'s own rule); a video that's graphics wall-to-wall with no plain talking-head stretches reads as noisy, not sleek.
7. **Reporting done without running the verification loop** — the brief explicitly requires it; a first pass is not the deliverable.

## Task-Specific Questions

1. Output canvas/aspect ratio for this project?
2. Brand reference — existing file/spec, or gather colors/fonts/voice now?
3. Any sections that should stay plain talking-head with no graphics (e.g. an intro hook, a serious moment)?
