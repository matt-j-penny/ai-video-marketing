---
name: create-frames-md
description: "Create a frames.md file — a plain-text motion system document that defines how every element in a video or motion graphic moves: timing and duration tokens (in ms and frames), easing curves and spring configs, entrance/exit patterns per element type, stagger and choreography, scene transitions, emphasis and camera moves, hold times, and do's/don'ts — so an agent animating title cards, lower-thirds, overlays, and scenes in Remotion, GSAP/HyperFrames, CSS, or After Effects produces motion that feels consistent. Use when the user wants to define an animation or motion style, document how an existing video's or codebase's animations behave, extract motion rules from a reference video, or build a motion language from scratch through a guided set of questions. The motion counterpart to DESIGN.md."
metadata:
  version: 1.0.0
  last_updated: 2026-09-10
---

# Create a frames.md

A frames.md puts a video's motion language into words precise enough for an AI agent to animate matching scenes without ever watching a reference: exact durations, exact easing curves, exact distances and scales, exact stagger offsets, plus enough prose that the *feel* of the motion comes through, not just the numbers. It's the motion counterpart to a `DESIGN.md` — DESIGN.md says what things look like, frames.md says how they move.

## Freshness Check

Compare `last_updated` above to today's date. If more than 2 weeks have passed, tell the user this skill file may be out of date and suggest re-pulling/reinstalling the `ai-video-marketing` repo (`git pull`, or re-running whichever install command they used) before relying on it — then continue with the workflow below regardless.

## Step 1: Figure Out the Source

Work out which of these applies before drafting anything:

1. **A reference video or animation** — a file, a YouTube/social URL, or a live site whose motion the user likes. Measure it rather than eyeballing it (see Step 3).
2. **Existing animation code** — a Remotion project, GSAP timelines, CSS keyframes/transitions, Framer Motion, a HyperFrames composition. Grep for `spring(`, `interpolate(`, `Easing.`, `durationInFrames`, `gsap.`, `ease:`, `cubic-bezier`, `@keyframes`, `transition` and read the actual values.
3. **A reference brand/mood** — the user names a brand or style whose motion they want to sit near (e.g. "Apple keynote", "MrBeast-style short", "Stripe product video").
4. **Nothing at all** — no reference, no code. Don't invent a motion style silently — run the question set below.

Also check for a `DESIGN.md` in the project. If one exists, read it first — the motion personality should match the visual one (a sharp-cornered, technical system shouldn't bounce; a playful, rounded one shouldn't move like a spreadsheet).

## Step 2: No Reference Material? Ask.

Ask these together as one set, not one at a time, with example answers in each so the user can reply quickly:

1. **What is it and where does the motion live?** — vertical short-form (Reels/TikTok/Shorts), a YouTube explainer, a product demo, a talking-head overlay package, UI animation.
2. **How should it feel?** — 2-3 adjectives. If stuck, offer pairs: "snappy and energetic", "calm and premium", "playful and bouncy", "precise and technical", "cinematic and weighty".
3. **Tempo** — fast and punchy (things land in 150-250ms), measured (300-500ms), or slow and luxurious (600ms+).
4. **Physics** — springy with overshoot, smooth ease-out with no overshoot, or mechanical/linear.
5. **Frame rate and format** — 24, 30, or 60fps; 16:9, 9:16, 1:1, 4:5.
6. **Toolchain** — Remotion, GSAP/HyperFrames, CSS, After Effects, or "whatever you pick." This decides which value formats the Implementation section needs.
7. **Sync** — cut to a music beat, to voiceover word timings, or free-running?
8. **Reference points** — any videos, channels, or brands whose motion (not look) they'd want to sit near.
9. **Off-limits** — anything banned (bounce, spin, 3D, blur, glitch), and any zones that must stay clear (a face on camera, burned-in captions, a platform UI overlay area).

## Step 3: Measure, Don't Guess (when extracting from video)

Eyeballed durations are wrong by 2x more often than not. Pull frames at the source's native frame rate around each distinct motion:

```bash
ffmpeg -ss <start> -to <end> -i input.mp4 -vsync 0 frames/%04d.png
```

For each motion, count frames from the first moved frame to the settled frame — that's the duration (`frames / fps × 1000` = ms). Step through the in-between frames: most of the distance covered early then a long settle means a strong ease-out; passing the final position then coming back means a spring with overshoot; equal distance per frame means linear. Note the start offset (px, % of frame, or scale) and any opacity/blur change alongside it.

When extracting from code, read the values directly — a `spring({ damping: 12 })` or `power3.out` is already a spec.

## Step 4: Draft the Sections

Every frames.md needs to cover these, in order:

1. **Motion Personality** — prose, not specs. How the motion feels and why: tempo, weight, physicality, how much moves at once. Close with 6-10 bullet points naming the concrete choices that produce the feel — not "smooth and modern," but "every entrance is a 24px rise with a hard ease-out, nothing overshoots."
2. **Timing Tokens** — the frame rate, then a named duration scale (e.g. `instant`, `fast`, `base`, `slow`, `scene`) with every value given in both ms and frames at the project fps. Include the minimum hold time for text on screen (e.g. 1 second + 0.3s per word).
3. **Easing & Springs** — every named curve with its exact value: `cubic-bezier()` for eases, stiffness/damping/mass for springs, plus what each is *for* (entrances, exits, UI moves, camera). Give each curve's equivalents in the chosen toolchain(s).
4. **Entrances & Exits** — per element type: headline/kinetic text, body text, lower-third, card/panel, icon/logo, image/footage, numbers/data, captions. For each: properties animated, start values (distance in px, scale, opacity, blur), duration token, easing token, and how the exit differs from the entrance (exits are usually faster and quieter).
5. **Choreography & Stagger** — the order things enter (background → container → headline → supporting → CTA, or whatever this system uses), stagger offsets between siblings, how much sequential animations overlap, per-word/per-letter/per-line text splitting rules, and the maximum number of elements moving at once.
6. **Scene Transitions** — the allowed transition types (hard cut, crossfade, push, wipe, match cut, zoom-through), each with duration, easing, and when to use it. Name what's banned.
7. **Emphasis & Camera** — highlight/underline draws, pulses, number count-ups, idle/ambient motion (drift, slow parallax), and camera moves (Ken Burns, punch-in, whip) — each with exact scale/distance/duration values and how often they're allowed.
8. **Sync & Pacing** — how motion lines up with audio: snap entrances to beats or word onsets (and how many frames before/after), how scene length relates to narration, minimum shot length, and pacing differences between hook, body, and CTA.
9. **Do's and Don'ts** — five or more of each, specific to this motion system rather than generic animation advice.
10. **Implementation Mapping** — the tokens translated into the chosen toolchain as copy-pasteable values: Remotion `spring()` configs and `interpolate(..., { easing: Easing.bezier(...) })` calls, GSAP `ease` strings and `stagger` objects, CSS `transition`/`animation` shorthands. Only include the toolchains this project uses.
11. **Agent Prompt Guide** — a short cheat-sheet: the 4-5 most-used motion tokens, 3-4 example prompts showing how to ask an agent to animate a component in this system (a title card, a lower-third, a stat reveal, a scene transition), and common follow-up adjustments ("snappier", "less bounce", "hold longer").

Every section needs actual values — a duration with no ms/frame number, or an easing with no curve, isn't finished. Timing tokens should look like this, not like "fast/medium/slow":

| Token | ms | Frames @30fps | Use |
|-------|----|---------------|-----|
| `fast` | 200 | 6 | Exits, small UI moves |
| `base` | 400 | 12 | Most entrances |

## Step 5: Validate Before Writing

- [ ] Section 1 ends with concrete motion traits, not adjectives alone
- [ ] The frame rate is stated and every duration has both ms and frames
- [ ] Every easing has an exact curve or spring config and a stated use
- [ ] Every element type's entrance and exit has properties, start values, duration, and easing
- [ ] Stagger offsets and the max-simultaneous-motion rule have real numbers
- [ ] Every allowed transition has a duration and easing; banned ones are named
- [ ] Text hold times are defined so nothing leaves before it can be read
- [ ] Do's/Don'ts are specific to this system, not generic animation advice
- [ ] Implementation values are copy-pasteable in the project's actual toolchain
- [ ] The agent prompt guide has runnable example prompts, not placeholders

If something is still vague, don't ship it — measure the real value from the source, or, if none exists, go back and ask.

## Step 6: Write the File

Save as `frames.md`, in the location the user specifies — default to the project root, next to `DESIGN.md` if one exists. Open with a first line naming what the file documents, e.g. `# Motion System — {Name}`.

## Common Mistakes

1. Writing "smooth, snappy, modern" in place of the actual durations and curves that make a motion system usable by an agent.
2. Giving durations in ms only — video tools think in frames, and 250ms at 30fps is 7.5 frames, which forces a silent rounding decision. Pick token values that land on whole frames.
3. Eyeballing a reference video's timing instead of stepping through its frames.
4. Defining entrances and forgetting exits, holds, and transitions — an agent will then invent them, inconsistently.
5. Motion that fights the visual system in `DESIGN.md` (bouncy springs on a sharp, technical brand).
6. Skipping the question set when there's no reference and inventing a motion style without checking it's what the user wants.

## Task-Specific Questions

1. Is this documenting motion that already exists (a video, a codebase) or designing a motion language from scratch?
2. Which animation toolchain will build from this file, and at what frame rate?
3. Where should the finished `frames.md` be saved?
