---
name: capcut-transcribe
description: "Transcribe a video/audio file with Deepgram to get a word-level timestamped transcript, for use by other CapCut skills (rough-cut, subtitles, zoom-highlights, beat-detector). Use when the user asks to transcribe footage for a CapCut project, or when a CapCut workflow needs exact word timings. Deepgram nova-2 only — no ElevenLabs/Whisper fallback, per house rule."
metadata:
  version: 1.0.0
  last_updated: 2026-09-15
---

# CapCut Transcribe

Produces one artifact: a transcript where every word carries its own start/end timestamp, relative to the **source** file (before any cutting). This is the shared input every other CapCut skill in this folder builds on — it doesn't touch CapCut itself.

## Freshness Check

Compare `last_updated` above to today's date. If more than 2 weeks have passed, tell the user this skill file may be out of date before relying on it — then continue regardless.

## Before Starting

1. Path to the source video/audio.
2. Where to save `transcript.json` — default to alongside the source file (e.g. `<job>/transcript.json`), since `rough-cut`, `subtitles`, `zoom-highlights`, and `beat-detector` all expect to find it there.
3. Confirm `DEEPGRAM_API_KEY` is set — it lives in `~/.claude/settings.json`'s `env` block. If missing, stop and tell the user rather than falling back to another provider.

## Why Deepgram only, no fallback

House rule (global instructions): always use Deepgram for transcription, never Whisper or ElevenLabs. Other skills in this repo have a three-way fallback chain — this one doesn't, by design. If Deepgram fails (bad key, outage), stop and report the error rather than silently switching providers.

## Workflow

### 1. Extract audio, if given a video

```bash
ffmpeg -i input.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

Skip this if already given an audio file.

### 2. Transcribe

```bash
curl -s -X POST \
  "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true&paragraphs=true&utterances=true&words=true" \
  -H "Authorization: Token ${DEEPGRAM_API_KEY}" \
  -H "Content-Type: audio/mpeg" \
  --data-binary @audio.mp3 \
  -o transcript.json
```

`words=true` is what produces the per-word array — without it Deepgram only returns the flat transcript string. Per-word data lives at `results.channels[0].alternatives[0].words[]`, each entry `{word, start, end, confidence, punctuated_word}`.

### 3. Verify before handing off

- The word array has real per-word `start`/`end` values (seconds, floats).
- Timestamps are relative to the file actually sent to Deepgram — if audio was extracted from video first with no `-ss` offset, timestamps still line up with the original video's timeline.
- Spot-check a couple of words against the audio if precision matters downstream (it always does here — rough-cut and subtitles both use these timestamps directly for placement in CapCut).

### 4. Hand off

Save the full Deepgram response JSON (not just the flattened word array) as `transcript.json` next to the source — `rough-cut`, `subtitles`, `zoom-highlights`, and `beat-detector` all read `results.channels[0].alternatives[0].words[]` from it.

## Common Mistakes

1. **Omitting `words=true`** — silently succeeds with only prose, no per-word timing.
2. **Reaching for ElevenLabs/Whisper "just this once"** — don't; this skill exists specifically to enforce Deepgram-only.
3. **Losing the offset** if audio extraction used `-ss` — always extract from `t=0`.

## Task-Specific Questions

1. Where should `transcript.json` be saved — default next to the source file?
2. Is the source already audio, or does it need extracting from video first?
