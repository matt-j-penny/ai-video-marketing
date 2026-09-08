---
name: level-audio
description: "When the user says a video's voice/narration sounds too loud in some parts and too quiet in others, wants the volume 'evened out' or 'leveled,' or asks to 'normalize the audio' — check first whether they mean overall loudness (a single quiet/loud file) or inconsistent loudness within the file (loud bits and quiet bits mixed together), since those need different fixes. Measures loudness range (LRA) and true peak with ffmpeg's ebur128/loudnorm, then evens out internal loud/quiet swings with speechnorm (not just loudnorm's linear mode, which only shifts the whole track by a constant and leaves internal swings untouched) before a final safe-level pass."
metadata:
  version: 1.0.0
---

# Level Audio

You are an audio engineer doing a leveling pass on talking-head/narration audio: even out parts that are noticeably louder or quieter than the rest, and land the whole track at a safe, consistent listening level. This is corrective, not creative — every adjustment should be measurable before and after.

## Before Starting

Gather or confirm:
1. Path to the video/audio file.
2. What "normalize" actually means here — ask if ambiguous. **Overall loudness** (the whole file is uniformly too quiet/loud) is fixed by a single gain shift. **Inconsistent loudness** (some lines louder than others within the same file) needs dynamics processing, not just a level shift — these are different problems with different fixes; don't assume which one is meant.
3. Target integrated loudness if the user has a preference (default: **-16 LUFS**, a reasonable level for online video; broadcast delivery specs are typically -23 LUFS — ask if this is for broadcast).

## Why a plain `loudnorm` pass often doesn't fix "some bits are louder than others"

`ffmpeg`'s `loudnorm` filter has two modes. `linear=true` (used with two-pass measured values) applies one constant gain to the entire file — it corrects the overall level and prevents clipping, but a loud sentence and a quiet sentence keep the same *relative* gap between them, just both scaled down or up together. Its default dynamic mode does compress somewhat as it goes, but it's tuned for broadcast compliance, not for aggressively flattening speech dynamics.

If the actual complaint is "some parts are louder, some are quieter" (a wide loudness range within the file), reach for **`speechnorm`** — a filter built specifically to expand quiet speech up and compress loud speech down as it plays. Diagnose which situation you're in with `ebur128`'s **LRA (loudness range)** stat before picking a filter: clean, consistently-delivered narration is typically **3-5 LU**; anything meaningfully higher means real internal swings that `speechnorm` should address, not just a `loudnorm` level shift.

## Workflow

### 1. Measure the current loudness

```bash
ffmpeg -i input.mp4 -af ebur128=peak=true -f null - 2> loudness.log
```

Read the `Summary` block at the end of `loudness.log` for **Integrated loudness (I)**, **Loudness range (LRA)**, and **True peak**. LRA above ~5-6 LU, or a true peak at/above 0 dBTP (clipping), is what triggers this workflow.

To find *where* the loud/quiet swings are (useful for confirming with the user, or spot-checking), parse the per-line `M:`/`S:` (momentary/short-term LUFS) values the same command prints while running, and flag stretches that deviate several LU from the file's mean short-term loudness.

### 2. Even out the internal dynamics with `speechnorm`

Measure what `speechnorm` produces before committing to a target, by chaining it into a throwaway `loudnorm` analysis pass:

```bash
ffmpeg -i input.mp4 -af "speechnorm=e=4:c=6:p=0.95,loudnorm=I=-16:TP=-1.5:LRA=5:print_format=json" -f null -
```

- `e` (expansion) lifts quiet speech, `c` (compression) pulls loud speech down, `p` is the peak ceiling it works within. `e=4:c=6:p=0.95` is a solid starting point; push `c` higher for footage with bigger swings, but check the diminishing returns — doubling `c` again rarely moves the resulting LRA much further once the filter's converged.
- Read the analysis pass's `input_lra` (this is `speechnorm`'s *output*, since it's the input to the chained `loudnorm`) — confirm it's now down in the 3-5 LU range before moving on.

### 3. Apply a final linear gain to a safe target

Don't let `loudnorm`'s own dynamic mode run again on top of `speechnorm` — that's a second, uncontrolled dynamics pass stacked on the first. Use `linear=true` with the exact `measured_*` values from step 2's analysis pass instead, so this step is just a constant gain shift onto the already-evened-out signal:

```bash
ffmpeg -i input.mp4 \
  -af "speechnorm=e=4:c=6:p=0.95,loudnorm=I=-16:TP=-1.5:LRA=5:linear=true:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:print_format=summary" \
  -c:v copy -c:a aac -b:a 256k \
  output.mp4
```

`-c:v copy` — this workflow never touches the video stream, so don't re-encode it; only the audio filter and its codec need to run.

### 4. Verify

Re-run step 1's `ebur128` measurement on the output. Confirm LRA has dropped to roughly 3-5 LU and true peak is safely below 0 dBTP (a couple dB of headroom, e.g. -1 to -6 dBTP, is fine).

## Common Mistakes

1. **Reaching for `loudnorm` linear mode alone when the complaint is uneven internal loudness** — it fixes overall level and peak safety, not the gap between a loud line and a quiet one.
2. **Chaining `speechnorm` into `loudnorm`'s dynamic mode for the final pass** — that stacks two uncontrolled dynamics processors; use `linear=true` with measured values for the final step so it's just a gain shift.
3. **Judging the fix by integrated loudness alone** — integrated loudness can look identical before/after while LRA (the actual "loud bits vs quiet bits" measure) hasn't moved. Always check LRA.
4. **Re-encoding video that wasn't touched** — use `-c:v copy`; only the audio needs a new codec pass.
5. **Assuming "normalize" means one specific fix** — confirm with the user whether the complaint is overall level or internal inconsistency before picking a filter.

## Task-Specific Questions

1. Is the whole file too quiet/loud, or are specific parts louder/quieter than the rest? (Determines linear `loudnorm` vs `speechnorm`.)
2. Is there a target loudness standard for the destination platform (e.g. broadcast -23 LUFS vs -16 LUFS for general online video)?
3. Any specific timestamp the user has already flagged as too loud/quiet, worth checking first against the `ebur128` output?
