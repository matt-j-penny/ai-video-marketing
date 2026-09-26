---
name: capcut-faceless-video
description: "Turn a single topic into a finished faceless video as a CapCut draft: research, an engaging human-sounding script, an Inworld voiceover, a Deepgram word-level transcript, a timed shot list, style-consistent AI images (Topview or Kie.ai, each image referencing the previous one), then assembled in CapCut with Ken Burns zooms and word-by-word highlighted native captions. Use when the user says '/faceless-video', asks to make a faceless video / faceless short / AI slideshow video about a topic, or wants a video from just a topic. Supports running the whole thing in one go, or step by step when the user asks."
metadata:
  version: 1.0.0
  last_updated: 2026-09-26
---

# CapCut Faceless Video

Topic in, finished CapCut draft out. Eight stages, all of them writing into one job folder, driven by `scripts/faceless.py` (one subcommand per stage) plus Claude's own writing for research, script and shot list.

## Freshness Check

Compare `last_updated` to today. Warn if >2 weeks stale (Kie.ai and Inworld model IDs move fast), then continue.

## Run mode — ask nothing, just read the request

- **Default: all at once.** Run every stage back to back and only stop at the end (or on an error).
- **Step by step:** if the user says "step by step", "one step at a time", "walk me through it", "pause after each step" or similar, stop after **every** stage. Show what that stage produced (see "Show" under each stage), say in one line what the next stage does, and wait. Moving on: "next" / "go" / "continue", or any message that approves the current stage or asks for the next one ("looks good, make the voiceover"). Anything that asks for a change to the current stage is feedback: apply it, re-show, and wait again. Never run two stages in one turn in this mode.

## Requirements

Check once at the start: `ffmpeg` and `uv` on PATH, and these in the `env` block of `~/.claude/settings.json` (or the shell env): `INWORLD_API_KEY`, `DEEPGRAM_API_KEY`, plus the image provider's keys, `TOPVIEW_UID` + `TOPVIEW_API_KEY` (default provider) or `KIE_API_KEY` (if `image_provider: kie`, and always for `visuals: video`). If one is missing, tell the user where to get it (Inworld: https://platform.inworld.ai, Deepgram: https://console.deepgram.com, Topview: topview.ai → account menu → API Settings, Kie: https://kie.ai/api-key) and to add it to `~/.claude/settings.json` themselves. Never ask for a key in chat. CapCut desktop must be installed. The CapCut stages quit and relaunch it around each write.

## Preferences

Stored in `~/.claude/faceless-video-preferences.md`. The script reads the same file, so what's saved there is what runs.

- **File exists:** read it and say in one line which settings are being used (e.g. "60s · 9:16 · images · fast cuts · Blake"). Anything the user says in the current request overrides the file for this run only. Pass those to every script call as `FV_<key>=<value>` env vars (e.g. `FV_aspect=16:9 uv run "$F" ...`).
- **File missing, or user says "change my settings" / "reset preferences":** ask these in one batch with the defaults shown, then write the file:

| key | options | default |
|---|---|---|
| `length` | any duration, e.g. 30s, 60s, 3m | 60s |
| `aspect` | 9:16, 16:9, 1:1, 4:5 | 9:16 |
| `visuals` | `images` (stills + Ken Burns) or `video` (each image animated by an image-to-video model) | images |
| `cut_speed` | fast (~2s/shot), medium (~3.5s), slow (~5s) | fast |
| `voice` | any Inworld voice ID | Blake |
| `style` | `default` (references/style-guide.md) or a path to your own style file | default |
| `caption_words` | words per caption line | 3 |

Advanced keys (don't ask; mention they exist): `tts_model` (inworld-tts-2), `speaking_rate` (1.0), `image_provider` (topview | kie), `image_model` (provider's name for the model; default Nano Banana 2, e.g. `GPT Image 2.5 Flare` on Topview for higher quality at higher cost), `video_model` (Kie; kling-2.6/image-to-video), `ken_burns` (1.12 = max zoom), `caption_color` (#FFFFFF), `caption_highlight` (#FFD400), `caption_case` (upper|as-is), `caption_y` (-0.45, vertical position, negative = lower).

File format:

```markdown
# Faceless Video Preferences
- length: 60s
- aspect: 9:16
- visuals: images
- cut_speed: fast
- voice: Blake
- style: default
- caption_words: 3
```

## Job folder

`~/Movies/Faceless Videos/<topic-slug>/`, which is under `~/Movies` so CapCut's sandbox can read it. Draft name = the topic in Title Case. If a draft with that name exists, append ` 2`, ` 3`...

Set `F="${CLAUDE_SKILL_DIR}/scripts/faceless.py"` and `JOB=<job folder>` for the commands below.

## Stage 1 — Research

Research the topic from your own knowledge. No external tools unless the topic is time-sensitive (news, recent releases, live stats); then use web search. Write `research.md`: 8–15 bullet facts, each specific and concrete (names, numbers, places, dates), plus the single most surprising fact marked **HOOK**. Drop anything you aren't confident is true.

**Show:** the bullet list and the chosen hook.

## Stage 2 — Script

Read [`references/script-rules.md`](references/script-rules.md) and follow it exactly. Target words = length in seconds × 2.5. Write `script.md`: a `# Title` line, then the spoken script as plain paragraphs. Run the self-check in the rules file before showing it.

**Show:** the full script and its word count vs. target.

## Stage 3 — Voiceover

```bash
uv run "$F" tts "$JOB"
```
Inworld TTS with the preference voice → `voiceover.mp3`. Long scripts are chunked and joined automatically.

**Show:** the printed duration vs. target length, and the file path so the user can listen. If more than 15% off target, offer to trim or extend the script (back to stage 2) rather than changing speaking rate.

## Stage 4 — Transcribe

```bash
uv run "$F" transcribe "$JOB"
```
Deepgram nova-2 → `transcript.json` (full response) + `words.json` (`[{text,start,end}]`). This is what lets images and captions land on the exact word.

**Show:** word count and total duration, plus the first ~10 words with timestamps.

## Stage 5 — Shot list

Read [`references/visual-selection.md`](references/visual-selection.md) and follow it exactly. Read `words.json` and write `shots.json`. Run its self-check.

**Show:** a table of shot # · start time · anchor word · prompt (short).

## Stage 6 — Images

```bash
uv run "$F" images "$JOB"
```
`image_provider` / `image_model`, one shot at a time, each passing the previous image as a style reference, with the style guide's Prompt block appended. Writes `images/NN.png` and saves each result back into `shots.json`, so a rerun resumes where it stopped. In `video` mode it also animates each image into `clips/NN.mp4`. Takes a while, so run it in the background and report progress.

Afterwards, **look at every image** (Read the PNGs). Regenerate any that are off-style, off-topic, contain text, or repeat the previous shot: `uv run "$F" images "$JOB" --redo N`.

**Show:** the images in order (send them as files), noting any you regenerated and why.

## Stage 7 — Assemble in CapCut

```bash
uv run "$F" assemble "$JOB" --name "<Draft Name>"
```
Creates a new CapCut draft at the preference aspect ratio with two separate tracks:

- **Video track:** one clip per shot, each exactly as long as its shot and cropped to the canvas (built from a silent `visuals.mp4`).
- **Audio track:** `voiceover.mp3` on its own track from 0s, so it can be adjusted, replaced or mixed with music independently of the images.

**Show:** the printed draft summary (segments, duration) and the audio line. CapCut relaunches with the draft in its project list.

## Stage 8 — Ken Burns

```bash
uv run "$F" kenburns "$JOB" --name "<Draft Name>"
```
Scale keyframes on every image clip, alternating zoom-in and zoom-out (1.0 ↔ `ken_burns`) so consecutive shots don't all push the same way. Skipped on animated (video-mode) clips. Re-running replaces the zooms rather than stacking them.

**Show:** the printed count.

## Stage 9 — Captions

```bash
uv run "$F" captions "$JOB" --name "<Draft Name>"
```
Native CapCut text on the text track: short lines (`caption_words` per line, broken early at sentence ends and pauses), with one segment per spoken word so the current word lights up in `caption_highlight` as it's said. Uses `capcut-subtitles`' `append_caption`. Re-running replaces all captions.

**Show:** the printed count.

## Stage 10 — Verify (always, both modes)

Open the draft and grab frames using the bridge's live lane:

```bash
B="${CLAUDE_SKILL_DIR}/../bridge/capcut-bridge.py"
uv run "$B" open "<Draft Name>"
uv run "$B" seek <t> --draft "<Draft Name>" && uv run "$B" shot "$JOB/check-<t>.png"
```

Check at 3–4 points (start, ~⅓, ~⅔, near the end): image fills the frame (no black bars, including at the zoomed-out end of a Ken Burns move), caption is readable and not covering the subject, highlighted word matches what's being said, no gap in images. Fix and re-run the relevant stage if anything's wrong. Then tell the user the draft name and that it's ready to export in CapCut, or run `uv run "$B" export --to "$JOB"` if they asked for the MP4.

## Common Mistakes

1. **Skipping the de-AI pass** on the script. Default AI prose is the #1 reason these videos feel fake.
2. **Shot starts that don't match a real word's start time**, so cuts land mid-word. Copy `start` from `words.json`.
3. **Generic prompts** ("a person thinking"). Every image must show what's being said at that moment.
4. **Running stages in parallel.** Each depends on the previous one's output, and images are sequential on purpose.
5. **Re-running `assemble` onto an existing draft name.** It refuses; pick a new name. Ken Burns and captions are safe to re-run on the same draft.
6. **Hand-editing in CapCut, then re-running a stage.** Ken Burns and captions only touch their own properties, but anything else you changed on those clips/captions can be overwritten. Finish the pipeline first, polish by hand last.
