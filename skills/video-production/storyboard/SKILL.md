---
name: storyboard
description: "Build a reviewable storyboard from a script or video, then turn approved beats into HTML, React, and Remotion scenes. Explicit-only: use when the user invokes '/storyboard' or '$storyboard', not for ordinary video, Remotion, image, or script requests."
metadata:
  version: 1.1.0
  last_updated: 2026-09-10
---

# Storyboard

You turn a script or video into a beat-by-beat visual storyboard for review, then — only once beats are approved — build the matching Remotion scenes. This skill is explicit-only: do not apply it to ordinary video, Remotion, image, or script requests unless the user typed `/storyboard` or `$storyboard`.

## Freshness Check

Compare `last_updated` above to today's date. If more than 2 weeks have passed, tell the user this skill file may be out of date and suggest re-pulling/reinstalling the `ai-video-marketing` repo before relying on it — then continue with the workflow below regardless.

## Before Starting

Gather or confirm:
1. Is the source a script (text) or a video/clip?
2. Storyboard mode (propose beats + images for review) or scene/build mode (implement already-approved beats)? Default to storyboard mode for a new source.
3. The project's brand colors and any existing `AGENTS.md`/`DESIGN.md` style guidance to follow.
4. Is there a person on camera, and any zone of the frame to keep clear (their face, a brand bug, burned-in captions)?

If given a video, extract its audio with `ffmpeg` and transcribe it with word-level timestamps (Deepgram nova-2 preferred; see the `transcribe` skill) before breaking it into beats. If given a script, use its structure directly and only ask for timing when it's needed for implementation.

## Storyboard Mode

Divide the spoken/script content into meaningful visual beats — don't force a fixed count, use as many as the narrative needs. Mark beats where no graphic is needed and the source video can stay on screen.

For every graphic beat, generate a 16:9 storyboard image with an **opaque** background (the source video must not show through). Visual direction:

- sleek, minimal, professional, and legible
- flat/2D graphics, no 3D treatment
- follow the project's existing style guidance (`AGENTS.md`/`DESIGN.md`) when present
- icons are optional, not required

When starting from a video, also produce a single overview image showing the proposed sequence of graphic moments where practical, then one image per beat.

Write a manifest beside the preview using the schema in [references/preview-schema.md](references/preview-schema.md). Keep beat IDs stable so later implementation files map back to the approved images.

Build a standalone local HTML preview showing, per beat: beat number/title/ID, image + aspect ratio + generation status, start/end time or script range, transcript/script excerpt, visual objective and motion description, whether the source video stays visible, and review status/notes. Use relative paths so the preview works without a dev server. Do not create React or Remotion scene files in this mode unless explicitly asked.

## Scene/Build Mode

Only enter this mode once the user has approved beats or explicitly asks for the HTML/React/Remotion implementation. For each approved graphic beat:

1. Create an HTML or React/TypeScript scene that reproduces the approved storyboard image precisely.
2. Reuse the project's existing Remotion conventions, tokens, fonts, and components where compatible.
3. Animate with `useCurrentFrame()` plus `spring()`/`interpolate()` — not CSS transitions or Tailwind animation classes.
4. Keep on-screen copy at least 24px unless the user explicitly asks for smaller text.
5. Align scene timing to the transcript/script timestamps.
6. Keep full-background graphics opaque where they're meant to cover source footage.
7. Update the implementation HTML preview with links to each scene, its source storyboard image, a rendered frame, and review notes.

Then run the Review Loop below before calling any scene done. Once every scene passes, assemble them into a seamless Remotion composition, and render the final video only when asked.

## Review Loop

Never declare a scene done from the code alone — render it and look at it. Render representative frames (at minimum the start, middle, and end of each beat, plus both sides of every transition), composited over the source video wherever the beat overlays footage rather than covering it. Check each frame against all three checks below, fix, and re-render until they pass.

**1. Matches the approved storyboard image.** Compare layout, scale, spacing, color, and timing against the approved board and correct any drift.

**2. Nothing sits over a person's face.** For any beat where a graphic overlays the source video, locate the face in the sampled frames and confirm no graphic element — text, card, lower-third, icon, callout — overlaps it, with a margin rather than butting against its edge. Sample across the whole beat, not just its first frame: a speaker who starts left of frame can drift under a graphic that was clear at `t=0`. On a conflict, move the graphic to the free third of the frame, shrink it, or shift the beat to a moment where the face is elsewhere — lowering opacity is not a fix.

**3. No sub-second flashes of source video between two full-screen graphics.** If a full-screen graphic ends, the original video shows for less than ~1s, and another full-screen graphic starts, that gap reads as a glitch, not as a cut back to the speaker. Join the two into one continuous run: extend the first to meet the second, pull the second earlier, or transition graphic → graphic with no return to footage. Keep the gap only when it's long enough to land as a deliberate return (~1s+, carrying its own beat of narration). This check reads the beat manifest, not pixels — run it in storyboard mode too, since a beat plan is far cheaper to fix than a built scene.

## Common Mistakes

1. **Skipping straight to scene/build mode** on a first-time request — always propose beats and stop for review unless approval is already explicit.
2. **Transparent backgrounds on full-coverage beats** — a graphic beat that's meant to hide the source footage must be opaque; a transparent one lets old footage bleed through.
3. **Claiming visual fidelity without rendering a frame** — always capture and compare a rendered frame against the approved storyboard image before calling a scene complete.
4. **Unstable beat IDs** — regenerating an image or scene under a new ID breaks the mapping back to the approved storyboard; keep IDs fixed once assigned.
5. **CSS transitions/Tailwind animation classes in Remotion scenes** — these aren't frame-accurate; drive all motion from `useCurrentFrame()`.
6. **Graphics parked over the speaker's face** — check overlay beats against frames sampled across the whole beat, since the face moves even when the graphic doesn't.
7. **A sub-second flash of source video between two full-screen graphics** — merge them into one run; a gap that short reads as a glitch rather than a return to the speaker.

## Task-Specific Questions

1. Script or video source — and if video, is a transcript with word-level timestamps already available?
2. Any existing brand/style reference (`AGENTS.md`, `DESIGN.md`, an existing Remotion project) to match?
3. Storyboard-only for now, or build straight through to Remotion scenes once beats look right?
