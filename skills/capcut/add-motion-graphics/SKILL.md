---
name: capcut-add-motion-graphics
description: "Use when the user says '/add-motion-graphics', or asks to add motion graphics throughout a CapCut video, make it more engaging/sleek/professional, or make sure something is always happening on screen. This is a prompt-augmentation skill — it expands the request into the full brief below and points at the other capcut-* skills that actually do the work, ending in a mandatory verification pass."
metadata:
  version: 1.0.0
  last_updated: 2026-09-16
---

# Add Motion Graphics

This skill has one job: when triggered, treat the task as the brief below — don't just add a graphic or two and stop.

## The brief

> Add motion graphics throughout the **entire** video, not just the hook or a couple of spots. Match the project's brand — colors, fonts, voice. Keep it **sleek and professional**, never cluttered or amateur. Keep it **fast-moving and engaging** — snappy transitions, no dead air. **There should always be something happening on screen**: no stretch of more than a few seconds with nothing moving, changing, or being introduced. Run the verification loop below before calling this done — don't report finished on a first pass.

## How — the existing skills in this folder do the actual work

1. `capcut-transcribe` → `capcut-rough-cut`, if the project isn't cut yet.
2. `capcut-beat-detector` is the backbone here — it's what decides where things happen across the *whole* runtime. Its default guidance is roughly 1-2 beats per 15-20s and "don't force one where nothing stands out." For this brief, lean toward the **denser** end of that range — "always something happening" means gaps get filled — but every beat still has to be justified by something real in the footage; don't invent beats just to hit density.
3. For each beat, pick the action:
   - `suggestedAction: "zoom"` → `capcut-zoom-highlights`.
   - A beat that wants an actual graphic (stat callout, label, transition card) rather than a camera move → place it with the bridge's `graphics`/`add-overlay` commands ([`bridge/README.md`](../bridge/README.md)), or `capcut-ai-generate` when the graphic needs a generated asset (animated background, icon, b-roll insert).
   - Caption motion counts too — `capcut-subtitles`' burn-in `captions` preset already pops each word in on its own timestamp, which is itself "something happening" throughout dialogue-heavy stretches.
4. **Brand:** check the project for an existing brand reference (colors, fonts, voice). If none exists, ask before inventing a palette — don't default to a generic look and call it "the brand."

## Verification loop — don't skip this

1. `open` the draft, then walk it in fixed intervals (every 2-3s) with `seek` → `shot`.
2. At each interval, confirm something is visibly different from the previous one — a graphic, a zoom in progress, a caption word popping, a transition. Flag any stretch with no change for more than ~3-4s.
3. For every flagged gap, add a beat there (graphic, zoom, or caption emphasis) and re-check it.
4. Once no gap remains, do one full end-to-end pass checking: brand colors/fonts consistent across every graphic (sleek/professional check), nothing overlapping or cluttered, pacing actually feels fast (a static graphic holding >4-5s with nothing changing is dragging, even if it's not a total dead spot).
5. Only report the task done once this pass comes back clean. If it doesn't, fix and re-run the loop — don't report partial progress as finished.

## Task-Specific Questions

1. Where's the brand reference (colors/fonts/voice) — an existing file/spec, or should specifics be gathered now?
2. Any part of the video that should stay graphics-free on purpose (e.g. a serious/sensitive moment, or the raw hook)?
