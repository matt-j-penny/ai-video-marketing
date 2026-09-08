---
name: rough-cut
description: "When the user wants to turn a raw talking-head or narrated video into a rough cut — strip dead air, and remove bad takes (false starts, repeated takes, fluffs/mistakes). Use when the user mentions 'rough cut,' 'remove the silences,' 'cut out the ums,' 'bad takes,' 'jump cuts,' or hands over raw talking-head/narration footage to clean up before a final edit. Finds every cut — dead air and bad takes alike — from the gaps and content of a word-level-timestamp transcript (Deepgram nova-2 first, then ElevenLabs, then local Whisper), then refines each one against a small local window of the audio before cutting, in ffmpeg or in a connected video editor."
metadata:
  version: 2.0.0
---

# Rough Cut

You are an editor doing the first-pass cut on talking-head/narration footage: strip silence, remove bad takes, leave a clean assembly ready for a final polish pass. This is mechanical, not creative — every cut must be justified by the transcript and confirmed against the audio.

## Before Starting

Gather or confirm:
1. Path to the source video.
2. Is a video editor being driven for this project (e.g. a connected DaVinci Resolve MCP), or is this a file-based ffmpeg edit? Cuts are made wherever the project already lives — don't switch tools mid-task.
3. Gap threshold if the user has a preference (default: any inter-word gap **≥0.4s** is a candidate cut, with `~120ms` padding kept on each side so words don't clip).
4. Transcription preference override — default order is **Deepgram (nova-2) → ElevenLabs → local Whisper**, falling through only if the preferred one is unavailable. Never use a transcription source that doesn't return word-level timestamps — a plain transcript string isn't enough to find cut points.

## Why transcript-first, not a blind ffmpeg silence scan

A first instinct is to run `ffmpeg silencedetect` over the raw audio and cut whatever it flags. Don't lead with that — it measures absolute loudness against a fixed dB threshold, and any background music bed, room tone, or camera noise sits close enough to speech level to break that badly in both directions: real dead air gets fragmented into several sub-threshold blips that never get cut (this is exactly what happened to a video's ~6s cold open — several short "silences" separated by faint music swells, none of which individually cleared `d=0.5s`), while pushing the threshold up to catch it starts clipping into the leading consonant of the next spoken word elsewhere in the file.

The word-level transcript doesn't have this problem, because Deepgram/ElevenLabs/Whisper already separated speech from non-speech acoustically — a gap between two consecutive words is silence (or at least non-speech) *regardless* of what's playing under it. So: **derive every candidate cut — leading dead air, trailing dead air, mid-video pauses, and bad takes — from the transcript**, and only reach for `ffmpeg silencedetect` afterward, aimed at a narrow window around one specific transcript timestamp, to nudge that one cut to the exact clean point. Never run it as a global scan.

## Workflow

Work in this order — each step's output feeds the next:

### 1. Extract the audio from the source

Transcribe the **original** video, not a pre-cut version — every downstream cut (silence and bad-takes alike) is computed from this one transcript, so there's only one timeline to reason about.

```bash
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 source.mp3
```

### 2. Transcribe with word-level timestamps

In preference order:

1. **Deepgram** — model `nova-2`, with `smart_format`, `punctuate`, `paragraphs`, `utterances`, and `words` on. `words` is what gives per-word timestamps.
2. **ElevenLabs** speech-to-text, if Deepgram is unavailable.
3. **Local Whisper**, with word-level timestamps enabled (`word_timestamps=True` / the equivalent flag), as the last resort.

Keep the word-level timestamp array — sentence-level timestamps aren't precise enough to find a clean cut point later.

### 3. Find every cut candidate from the transcript

All of these come from the same word array — no audio scanning yet:

| Type | How to find it |
|---|---|
| **Leading dead air** | Gap from `t=0` to the first word's start |
| **Trailing dead air** | Gap from the last word's end to the file's duration |
| **Mid-video pause** | Gap between consecutive words ≥ the threshold (default 0.4s) |
| **Unfinished sentence** | A sentence starts, breaks off with no terminal punctuation or trails into a filler ("...and, uh—"), and is then followed by a new sentence covering the same ground |
| **Repeated take** | Two or more consecutive sentences are near-duplicates of each other (same content, re-said) — the speaker re-did the line |
| **Fluff / mistake** | Stutters, false starts ("I— I think"), self-corrections ("no wait, let me say that again"), or an explicit flag ("sorry, let me redo that") |

For a repeated take, keep the **last** clean instance (usually the one the speaker was satisfied with) and mark every earlier attempt for removal. Note each candidate's rough start/end from word timestamps — these are approximate, not the final cut points.

### 4. Refine each cut point against a local audio window

A transcript timestamp lands on a word boundary, not necessarily a clean edit point. For each candidate, look at a small window of the source audio around it (~1-2s either side) and find the actual silence/breath to cut on — this is the only place `silencedetect` belongs, scoped to one gap at a time:

```bash
ffmpeg -i source.mp3 -ss <ts-2> -t 4 -af silencedetect=noise=-30dB:d=0.15 -f null - 2>&1 | grep silence_
```

Snap the cut to the start of that local silence, not the raw transcript timestamp. If the gap has no natural pause either side (a bad take that runs straight into the next line with no breath — common when a speaker re-does a line immediately), cut exactly at the word boundary instead; a local window is what tells you which case you're in.

### 5. Build one keep-list and cut once

Combine every refined range from step 4 into a single sorted list of cuts, invert it into keep-ranges, and cut once — don't cut silence in one pass and bad takes in another.

- **Video editor connected:** import the source and place cuts on the timeline at the keep-list boundaries.
- **ffmpeg only:** cut the keep segments in a single pass with `select`/`aselect` (avoids re-encoding N separate files and concatenating):

```bash
ffmpeg -i input.mp4 \
  -vf "select='..keep-ranges..',setpts=N/FRAME_RATE/TB" \
  -af "aselect='..keep-ranges..',asetpts=N/SR/TB" \
  -c:v hevc_videotoolbox -tag:v hvc1 -c:a aac -b:a 256k \
  output.mp4
```

`-tag:v hvc1` matters on macOS: ffmpeg's default HEVC mux tags the stream `hev1`, which QuickTime Player won't open even though the codec itself is fine — always tag HEVC output `hvc1`.

## Common Mistakes

1. **Running a global `ffmpeg silencedetect` scan as the primary silence-finder** — background music or noise defeats a fixed dB threshold in both directions (misses real dead air, clips real speech elsewhere). Derive candidates from the transcript; use `silencedetect` only on a narrow window around one already-known timestamp.
2. **Cutting on the raw transcript timestamp** without checking a local audio window first — words rarely start exactly where the transcript says.
3. **Cutting silence and bad takes in two separate passes** — build one combined keep-list and cut once (step 5).
4. **Using a transcript source without word-level timestamps** — a plain transcript can locate roughly which sentence is bad, not where to cut.
5. **Removing every repeated take instead of keeping one** — the goal is one clean instance per line, not zero.
6. **Re-encoding per-cut and concatenating** when a single-pass `select`/`aselect` filter would do it without the quality/sync loss of repeated encodes.
7. **Leaving ffmpeg's default `hev1` HEVC tag on macOS output** — tag it `hvc1` or QuickTime Player will refuse to open a perfectly valid file.

## Task-Specific Questions

1. Is there a video editor already open/connected for this project, or should this stay a pure ffmpeg pipeline?
2. Any lines the speaker flagged themselves as bad (mentioned in the recording or separately) worth checking first?
3. How aggressive should the pause threshold be — natural pauses for emphasis should usually survive; only dead air should go.
