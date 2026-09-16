---
name: capcut-rough-cut
description: "Turn a raw talking-head/narrated clip into a rough cut INSIDE CapCut — strip dead air and bad takes (false starts, repeated takes, fluffs), cut aggressively, using the bridge's file-lane `replay` command. Use when the user wants a rough cut, wants silences/bad takes removed, and wants the result as a CapCut draft (not an ffmpeg output file). Needs a word-level transcript first (capcut-transcribe)."
metadata:
  version: 1.0.0
  last_updated: 2026-09-15
---

# CapCut Rough Cut

First-pass cut on talking-head/narration footage, built as a real CapCut draft: strip silence, remove bad takes, leave a clean assembly. Mechanical, not creative — every cut is justified by the transcript. Default posture is **aggressive**: when in doubt, cut it.

## Freshness Check

Compare `last_updated` above to today's date. If more than 2 weeks stale, warn the user before relying on this, then continue.

## Before Starting

1. Path to the source video. Per the bridge's hard rules, it (or a hardlink target) must resolve under `~/Movies` — the bridge's `replay` hardlinks it into the draft automatically, but the source file itself needs to exist somewhere CapCut's sandbox can read from at hardlink time.
2. Run `capcut-transcribe` first if `transcript.json` doesn't already exist next to the source.
3. Draft name for the new CapCut project (`--name`).
4. Gap threshold — default **aggressive: any inter-word gap ≥ 0.3s is a cut candidate**, ~80ms padding kept each side. This is tighter than a "safe" rough cut; loosen it only if the user asks for a gentler pass.
5. CapCut must be fully quit before this runs — the bridge handles quit/relaunch itself, but don't run this while mid-edit in the live lane.

## Why transcript-first, not a blind ffmpeg silence scan

A `ffmpeg silencedetect` pass measures absolute loudness against a fixed dB threshold — room tone, camera noise, or any background sound breaks it in both directions. The word-level transcript already separated speech from non-speech acoustically: a gap between two consecutive words is silence regardless of what's underneath it. Derive every cut candidate — dead air and bad takes alike — from the transcript; only reach for `silencedetect` afterward, scoped to a ~1-2s window around one already-known timestamp, to snap that one cut to the exact clean point.

## Workflow

### 1. Load the transcript

Read `transcript.json` (from `capcut-transcribe`). Pull `results.channels[0].alternatives[0].words[]`.

### 2. Find every cut candidate

All derived from the word array — no audio scanning yet:

| Type | How to find it |
|---|---|
| Leading dead air | Gap from `t=0` to the first word's start |
| Trailing dead air | Gap from the last word's end to file duration |
| Mid-video pause | Gap between consecutive words ≥ threshold (default 0.3s) |
| Unfinished sentence | Breaks off with no terminal punctuation / trails into filler, followed by a sentence covering the same ground |
| Repeated take | Two+ consecutive sentences are near-duplicates — the speaker re-did the line |
| Fluff / mistake | Stutters, false starts, self-corrections, explicit "let me redo that" |

For a repeated take, keep the **last** clean instance, mark every earlier attempt for removal. Being aggressive here means: when a pause or take is borderline, cut it — a slightly-too-tight edit is preferable to leftover dead air or a double take.

### 3. Refine each cut point against a local audio window

A transcript timestamp lands on a word boundary, not necessarily a clean edit point:

```bash
ffmpeg -i source.mp3 -ss <ts-2> -t 4 -af silencedetect=noise=-30dB:d=0.15 -f null - 2>&1 | grep silence_
```

Snap to the start of the local silence. If there's no natural pause either side (a retake that runs straight into the next line), cut exactly at the word boundary.

### 4. Build `cuts.json` — the KEEP list, not the cut list

Per the bridge's [`INPUT-CONTRACT.md`](../bridge/INPUT-CONTRACT.md), invert the cuts into an ordered list of spans to **keep**:

```json
{
  "clip": "raw.mp4",
  "fps": 30.0,
  "segments": [
    { "clip": "raw.mp4", "start": 4.12, "end": 11.30, "note": "HOOK - ..." },
    { "clip": "raw.mp4", "start": 14.87, "end": 22.40, "note": "..." }
  ]
}
```

`start`/`end` are seconds into the **source** clip. `replay` places these back-to-back on the CapCut timeline in this order with no gaps — segment N's edited-timeline start is the sum of durations of segments before it. Keep that mapping in mind: `subtitles`, `zoom-highlights`, and `beat-detector` all need it to place things on the cut timeline later.

### 5. Cut once, inside CapCut

```bash
uv run "${CLAUDE_SKILL_DIR}/../bridge/capcut-bridge.py" replay <job> --name <draft-name>
```

This quits CapCut if running, writes the draft, and relaunches it. Don't call `replay` again on a draft that's since been hand-edited or touched by another skill here — it rebuilds from scratch and wipes everything. Once a draft exists, later changes go through `add-overlay` / `add-text` / `transform` / `keyframe` only.

## Common Mistakes

1. **Running a global `silencedetect` scan** instead of deriving candidates from the transcript first.
2. **Cutting on the raw transcript timestamp** without a local audio window check.
3. **Writing the cut list instead of the keep list** — `cuts.json` is spans to keep, not spans to remove.
4. **Calling `replay` on a draft that already has hand edits or other skills' work** — wipes it. `replay` is only for the first build.
5. **Leaving CapCut open** when running — let the bridge handle quit/relaunch; don't fight it.
6. **Removing every repeated take instead of keeping one clean instance.**

## Task-Specific Questions

1. How aggressive — keep the default 0.3s gap threshold, or does this footage need a gentler pass (natural pauses for emphasis)?
2. New draft name?
3. Any lines the speaker flagged as bad takes themselves, worth checking first?
