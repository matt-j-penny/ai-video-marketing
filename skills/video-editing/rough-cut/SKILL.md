---
name: rough-cut
description: "When the user wants to turn a raw talking-head or narrated video into a rough cut — strip dead air, and remove bad takes (false starts, repeated takes, fluffs/mistakes). Use when the user mentions 'rough cut,' 'remove the silences,' 'cut out the ums,' 'bad takes,' 'jump cuts,' or hands over raw talking-head/narration footage to clean up before a final edit. Finds cut points from a word-level-timestamp transcript (Deepgram nova-2 first, then ElevenLabs, then local Whisper) and refines each one against the actual audio before cutting, in ffmpeg or in a connected video editor."
metadata:
  version: 1.0.0
---

# Rough Cut

You are an editor doing the first-pass cut on talking-head/narration footage: strip silence, remove bad takes, leave a clean assembly ready for a final polish pass. This is mechanical, not creative — every cut must be justified by the transcript and confirmed against the audio.

## Before Starting

Gather or confirm:
1. Path to the source video.
2. Is a video editor being driven for this project (e.g. a connected DaVinci Resolve MCP), or is this a file-based ffmpeg edit? Cuts are made wherever the project already lives — don't switch tools mid-task.
3. Silence thresholds if the user has a preference (default: `-30dB` noise floor, `0.5s` minimum duration, `120ms` padding kept on each side of a cut so words don't clip).
4. Transcription preference override — default order is **Deepgram (nova-2) → ElevenLabs → local Whisper**, falling through only if the preferred one is unavailable. Never use a transcription source that doesn't return word-level timestamps — a plain transcript string isn't enough to find cut points.

## Workflow

Work in this order — each step's output feeds the next:

### 1. Detect and cut silence

Find silence on the original audio track directly from the source video (no need to extract audio first for detection):

```bash
ffmpeg -i input.mp4 -af silencedetect=noise=-30dB:d=0.5 -f null - 2>&1 | grep silence_
```

This prints `silence_start` / `silence_end` pairs. Build a keep-list: the inverse of the silence ranges, with ~120ms padding kept on either side of each cut so words don't clip.

- **Video editor connected:** import the source and place cuts on the timeline at the keep-list boundaries.
- **ffmpeg only:** cut the keep segments in a single pass with `select`/`aselect` (avoids re-encoding N separate files and concatenating):

```bash
ffmpeg -i input.mp4 -vf "select='..keep-ranges..',setpts=N/FRAME_RATE/TB" \
       -af "aselect='..keep-ranges..',asetpts=N/SR/TB" rough_v1.mp4
```

Call the result `rough_v1` (silence removed). All later steps work on this version, not the original — its timeline is what gets cut next.

### 2. Extract the audio

Strip a clean audio-only file from `rough_v1` for transcription:

```bash
ffmpeg -i rough_v1.mp4 -vn -acodec libmp3lame -q:a 2 rough_v1.mp3
```

### 3. Transcribe with word-level timestamps

Transcribe `rough_v1.mp3`, in preference order:

1. **Deepgram** — model `nova-2`, with `smart_format`, `punctuate`, `paragraphs`, `utterances`, and `words` on. `words` is what gives per-word timestamps.
2. **ElevenLabs** speech-to-text, if Deepgram is unavailable.
3. **Local Whisper**, with word-level timestamps enabled (`word_timestamps=True` / the equivalent flag), as the last resort.

Keep the word-level timestamp array — sentence-level timestamps aren't precise enough to find a clean cut point in step 5.

### 4. Find bad takes in the transcript

Scan the transcript for:

| Type | Signal |
|---|---|
| **Unfinished sentence** | A sentence starts, breaks off with no terminal punctuation or trails into a filler ("...and, uh—"), and is then followed by a new sentence covering the same ground |
| **Repeated take** | Two or more consecutive sentences are near-duplicates of each other (same content, re-said) — the speaker re-did the line |
| **Fluff / mistake** | Stutters, false starts ("I— I think"), self-corrections ("no wait, let me say that again"), or an explicit flag ("sorry, let me redo that") |

For a repeated take, keep the **last** clean instance (usually the one the speaker was satisfied with) and mark every earlier attempt for removal. For each bad take, note its rough start/end word timestamps — these are approximate, not the final cut points.

### 5. Refine each cut point against the audio

A transcript timestamp lands on a word boundary, not necessarily a clean edit point. For each noted timestamp, look at `rough_v1`'s audio in a small window either side of it (~1-2s) and find the actual silence/breath to cut on:

```bash
ffmpeg -i rough_v1.mp3 -ss <ts-2> -t 4 -af silencedetect=noise=-30dB:d=0.15 -f null - 2>&1 | grep silence_
```

Snap the cut to the start of that local silence, not the raw transcript timestamp — this is what keeps the cut inaudible.

### 6. Make the cuts

- **Video editor connected:** apply the cuts on the existing timeline at the refined points.
- **ffmpeg only:** cut the bad-take ranges out of `rough_v1` the same way as step 1 (single-pass `select`/`aselect` over the keep-list) to produce the finished rough cut.

Optionally re-run step 1's silence detection once more on the result — removing a bad take can leave a slightly-too-long gap at the join.

## Common Mistakes

1. **Cutting on the raw transcript timestamp** — words rarely start exactly where the transcript says; always refine against the audio (step 5).
2. **Transcribing the original instead of `rough_v1`** — if silence removal happens after transcription, every downstream timestamp is off relative to the cut timeline.
3. **Using a transcript source without word-level timestamps** — a plain transcript can locate roughly which sentence is bad, not where to cut.
4. **Removing every repeated take instead of keeping one** — the goal is one clean instance per line, not zero.
5. **Re-encoding per-cut and concatenating** when a single-pass `select`/`aselect` filter would do it without the quality/sync loss of repeated encodes.

## Task-Specific Questions

1. Is there a video editor already open/connected for this project, or should this stay a pure ffmpeg pipeline?
2. Any lines the speaker flagged themselves as bad (mentioned in the recording or separately) worth checking first?
3. How aggressive should silence removal be — natural pauses for emphasis should usually survive; only dead air should go.
