---
name: capcut-zoom-highlights
description: "Punch in on interesting moments INSIDE a CapCut draft — animate a keyframed zoom (default ~115% scale) centered on the speaker's face when it's a talking-head shot, using the bridge's keyframe command. Use when the user wants zoom-ins/punch-ins on the interesting parts of a CapCut video. Consumes beats.json (capcut-beat-detector) for where, and face detection for how to frame each zoom."
metadata:
  version: 1.0.0
  last_updated: 2026-09-15
---

# CapCut Zoom Highlights

Adds a camera-move — not a new clip, not a new overlay — to the existing main-track footage: scale keyframes that punch in around an interesting beat, then ease back out. Uses the bridge's file-lane `keyframe`/`transform` commands, so this is a `common_keyframes` animation on the segment already on the timeline.

## Freshness Check

Compare `last_updated` to today. Warn if >2 weeks stale, then continue.

## Before Starting

1. The draft name — must already have the footage on its main track (built by `capcut-rough-cut`/`replay`, or already open).
2. `beats.json` (from `capcut-beat-detector`) for candidate moments, or a specific list of timestamps the user already wants zoomed. Only beats with `suggestedAction: "zoom"` are candidates by default.
3. Target zoom scale — default **1.15** (115%), matching the user's ask; adjust only if told to.
4. Whether the shot is a talking-head (face should stay framed) or something else (b-roll, screen recording) — face-centering only applies to the former.

## Why keyframes, not a static transform

A static `transform` scale change (the bridge's `transform` command) applies for the whole segment. A zoom-*in* effect needs motion: scale ramps up into the beat, holds, then eases back down — that's `common_keyframes`, driven by the bridge's `keyframe` command called multiple times at different `--at` points on the same segment.

## Workflow

### 1. Pick candidate beats

From `beats.json`, take every beat with `suggestedAction: "zoom"` (or the user's explicit list). Each needs a `start`/`end` on the **edited** timeline already (that's how `capcut-beat-detector` writes them).

### 2. Find the main-track segment index for each beat

`uv run "${CLAUDE_SKILL_DIR}/../bridge/capcut-bridge.py" state <draft>` dumps the timeline as JSON — use it to confirm which main-track segment (flattened index, per the bridge's addressing) each beat's timestamp falls inside, and that segment's `source_timerange` in-point (needed for face detection, which reads the **source** file).

### 3. If it's a talking-head shot, find the face

Convert the beat's edited-timeline start back to source time (`source_in_point + (edited_t - segment_edited_start)`), then:

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/detect_faces.py" <source-video> --at <source-t1> <source-t2> ...
```

Take the returned `face.cx`/`face.cy` (normalized 0-1 of the source frame) for the moment being zoomed. If no face is detected (b-roll, wide shot, no one on camera), skip face-centering and just zoom on the frame center.

### 4. Compute the pan to keep the face centered

CapCut's segment `clip.transform.x`/`.y` are normalized to the canvas, where `x=0.5` shifts content a full half-frame right (confirmed in the bridge's `set_transform` docstring). To bring a face at normalized position `(fx, fy)` (0=left/top, 1=right/bottom, 0.5=center) to the canvas center:

```
pan_x = 0.5 - fx
pan_y = 0.5 - fy
```

This is a first-pass estimate, not a verified pixel-exact formula — CapCut's pan/scale interaction isn't documented. Apply it, then check with `shot` (step 6) and nudge `x`/`y` if the face isn't actually centered; it should be close since it's a direct offset-from-center calculation.

### 5. Set the keyframes

For a beat spanning `start`→`end` (edited seconds), animate scale up into it and back down, e.g.:

```bash
BRIDGE="${CLAUDE_SKILL_DIR}/../bridge/capcut-bridge.py"
uv run "$BRIDGE" keyframe <draft> --track main --index <N> --at <start-0.15> --scale 1.0 --x 0 --y 0
uv run "$BRIDGE" keyframe <draft> --track main --index <N> --at <start+0.1>  --scale 1.15 --x <pan_x> --y <pan_y>
uv run "$BRIDGE" keyframe <draft> --track main --index <N> --at <end-0.1>    --scale 1.15 --x <pan_x> --y <pan_y>
uv run "$BRIDGE" keyframe <draft> --track main --index <N> --at <end+0.15>   --scale 1.0  --x 0 --y 0
```

Four points: rest → punched-in (fast ramp, ~0.25s) → hold for the beat → back to rest (~0.25s ease-out). Skip the first/last point if the beat sits at the very start/end of the segment (nothing to ease from/to). Remember `--at` is **timeline** seconds — the bridge converts to the segment's source-relative offset internally; don't pre-convert it yourself (that conversion is what the bridge's docstring warns is easy to get backwards).

### 6. Verify visually

```bash
uv run "$BRIDGE" open <draft>
uv run "$BRIDGE" seek <midpoint-of-beat>
uv run "$BRIDGE" shot check.png
```

Look at `check.png` — face still in frame, no dead space at the edges from over-panning. Nudge `x`/`y` and re-run `keyframe` on the same points if not.

## Common Mistakes

1. **Zooming every beat** — reserve it for beats actually marked `zoom`; overusing it reads as jittery, not punchy.
2. **Face-centering a non-talking-head shot** — skip step 3-4 for b-roll/screen recordings, just zoom on center.
3. **Forgetting the rest keyframes before/after** — without them the zoom snaps instead of animating.
4. **Not verifying with `shot`** — the pan formula is a first-pass estimate; always check at least the first one visually before doing the rest.
5. **Re-running `replay`** after zooms are in place — wipes them, same rule as every other skill here.

## Task-Specific Questions

1. Default 115% scale okay, or does a specific beat want a stronger/subtler punch-in?
2. Confirm which beats are actually talking-head shots vs b-roll, if `beats.json` doesn't already distinguish.
