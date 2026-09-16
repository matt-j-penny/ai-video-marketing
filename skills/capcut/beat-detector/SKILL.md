---
name: capcut-beat-detector
description: "Find the interesting narrative beats in a talking-head/narration video from its word-level transcript — hook, punchlines, key stats, reactions, transitions — and write beats.json on the edited (post-cut) timeline. Use when the user wants to know 'what are the interesting moments', or as a prerequisite for capcut-zoom-highlights (where to zoom), capcut-subtitles (which word to emphasize per line), or capcut-full-edit (where/what type of motion graphic to build). Adapted from the Edit Pipeline's ev-beats stage, minus its HyperFrames-template selection (not applicable to CapCut)."
metadata:
  version: 1.1.0
  last_updated: 2026-09-16
---

# CapCut Beat Detector

Storyboards a talking-head/narration video into **beats** — spans of the timeline worth calling out, each tagged with a broad category (zoom / graphic / caption-emphasis) — without designing or building the actual graphic (that's `capcut-zoom-highlights`, `capcut-subtitles`, or `capcut-full-edit`'s job). This skill decides **where**, **why**, and **roughly what kind**.

Method carried over from the Edit Pipeline's `ev-beats` stage (`Edit Pipeline/.claude/skills/ev-beats/SKILL.md`) — the role vocabulary and "what earns a beat" judgment are the same; the HyperFrames template-matching half of that stage doesn't apply here and is dropped.

## Freshness Check

Compare `last_updated` to today. Warn if >2 weeks stale, then continue.

## Before Starting

1. `transcript.json` (from `capcut-transcribe`).
2. If the video was rough-cut, its `cuts.json` — beats are placed on the **edited** timeline, same reasoning as `capcut-subtitles` step 1.
3. Roughly how many beats is reasonable — a good rule of thumb is 1-2 per 15-20s of runtime; don't force beats where nothing actually stands out.

## What earns a beat

A beat needs a **showable** — a number, name, product, claim, before/after, list, or a genuine emotional/energy shift (a punchline, a reaction, a reveal). A sentence with no showable rarely earns one. Every beat must be justified by something actually said or that actually happens on screen — never invented to hit a quota.

## Roles

Tag each beat with one role (same vocabulary as `ev-beats`):

`hook` `promise` `setup` `point` `evidence` `demo` `payoff` `punchline` `transition` `aside`

The hook (opening moment that earns attention) and the punchline (the payoff line) are usually the two strongest beats in the video — flag them explicitly.

## Workflow

### 1. Map to the edited timeline

If this footage was rough-cut, convert every candidate word's source timestamp to edited-timeline time first (same walk as `capcut-subtitles` step 1 — accumulate kept-segment durations, skip anything that falls inside a cut). If uncut, source time == edited time.

### 2. Read the transcript as an arc

Summarize the throughline in one sentence, then walk sentence by sentence, tagging each with a role and noting its showable (if any). This is the same pass a human editor would do skimming the transcript for "what's worth calling out."

### 3. Write `beats.json`

```json
{
  "arc": "one-sentence throughline",
  "beats": [
    { "id": "b01", "start": 0.0, "end": 3.7, "role": "hook",
      "reason": "cold open claim that earns the next 20s",
      "line": "most people don't know this costs literally $0",
      "suggestedAction": "zoom", "keyword": "$0" },
    { "id": "b02", "start": 41.2, "end": 44.9, "role": "punchline",
      "reason": "payoff of the setup at b0X",
      "line": "...and that's the whole trick.",
      "suggestedAction": "zoom" },
    { "id": "b03", "start": 12.0, "end": 18.4, "role": "evidence",
      "reason": "a concrete stat worth putting on screen, not just said",
      "line": "we cut render time from 40 minutes to 90 seconds",
      "suggestedAction": "graphic", "layout": "overlay", "keyword": "90 seconds" }
  ]
}
```

- `start`/`end` — edited-timeline seconds.
- `reason` — why this earns a beat; never leave this blank, it's what lets a human (or the next skill) sanity-check the pick.
- `line` — the exact spoken words in this span, for reference.
- `suggestedAction` — `zoom` (emotional/emphasis moment, good candidate for `capcut-zoom-highlights`), `graphic` (a showable worth an actual on-screen graphic, for `capcut-full-edit`/`capcut-add-motion-graphics`), `caption-emphasis` (a word worth highlighting in `capcut-subtitles` but not necessarily a camera move or graphic), or `none` (flagged as interesting but no specific action yet).
- `layout` (only when `suggestedAction: "graphic"`) — `full-screen` (own opaque background, original footage fully hidden for this span), `overlay` (transparent graphic over the still-visible footage — a lower-third, a callout, a stat card), or `split` (footage cropped/repositioned to occupy part of the frame — e.g. a 9:16 crop docked to one third — while a graphic fills the rest). See `capcut-full-edit` for how each is actually built.
- `keyword` (optional) — if there's one word or short phrase that carries the beat (a stat, a name, the punch word), name it here so `capcut-subtitles`/`capcut-full-edit` can pick it up without re-deriving it.

Save as `beats.json` next to `transcript.json`.

### 4. Sanity-check density

Don't cluster beats — if two are within ~2s of each other, decide if they're really one beat split awkwardly, or genuinely two. Don't force a beat every N seconds on a mechanical cadence; a quiet stretch of setup with no showable gets none.

## Common Mistakes

1. **Inventing showables that weren't actually said** to hit a beat quota.
2. **Beats on source timestamps instead of edited-timeline** on a rough-cut video.
3. **Every beat marked `zoom`/`graphic`** — most beats are just "interesting to know about"; only mark `zoom` where a camera move actually helps (emphasis, reaction, reveal), and `graphic` only where there's a real showable worth rendering, not every fact.
4. **Skipping the `reason` field** — it's the only thing that lets this be checked later.

## Task-Specific Questions

1. Was this footage rough-cut already (need `cuts.json` for the timeline mapping), or is this raw/uncut?
2. Any beats the user already knows they want called out (a specific stat, a specific reaction), to seed the pass?
