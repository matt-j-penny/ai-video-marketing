---
name: youtube-editing-style
description: Analyze the editing style of a YouTube URL or local video with Gemini 3.8 Flash through OpenRouter, producing timestamped evidence and a practical recreation guide. Use for editing breakdowns, reference-video analysis, and requests to recreate a video's style.
---

# YouTube editing style

Download the URL using yt-dlp, then submit actual MP4 video with audio to `google/gemini-3.8-flash` via OpenRouter. Use the bundled script and prompt; do not substitute thumbnail or transcript-only analysis.

Resolve this skill's folder and run:

```bash
python3 <skill-folder>/scripts/analyze.py '<url-or-local-path>' --first-seconds 30 --out-dir '<workspace>/research/editing-style/<unique-run>'
```

Use a 30-second opening excerpt for an initial style test when the user has not specified scope. Honor explicit duration requests; set `--first-seconds 240` for the first four minutes, or omit `--first-seconds` for the whole video. Always state the analyzed interval and do not imply excerpt findings cover unseen footage. The downloaded source stays local; ffmpeg prepares only the requested interval for submission. Choose a fresh output directory. Requirements: Python 3, yt-dlp, ffmpeg and ffprobe. The script reads `OPENROUTER_API_KEY` from the environment, falling back to `env.OPENROUTER_API_KEY` in `~/.claude/settings.json`. Never print, copy into the skill, or commit the key. `--prepare-only` downloads/prepares without calling the API; `--resume` reuses an existing run only when its configuration matches. API calls incur normal OpenRouter charges. A URL supplied for analysis authorizes the download and model submission.

The script preserves audio and original frame rate, creating 720p H.264 analysis clips of at most 180 seconds with 2-second overlaps. This is a practical upload-size choice, not a provider limit. Longer videos get per-clip analysis followed by a text synthesis. All original timestamps use clip offsets. Review the guide alongside the clip reports; synthesis cannot recover details missed by the model. The model may sample internally, so do not promise frame-accurate cut or transition measurements.

Options: `--model` explicitly changes the model; `--focus` adds user priorities; `--clip-seconds` changes chunk length; `--processing agentic|static|default` selects Gemini video processing (agentic by default). API responses stream via SSE; raw events and generation headers are retained for diagnostics. No silent model fallback. Do not automatically retry ambiguous failed paid requests; report the error and retained artifacts.

The report must cover camera versus editorial movement, cut logic, edit density, graphics, full subtitles versus selective text, font roles/substitutes, colour palette, timing, animation paths/easing, B-roll rules, layouts, masking/occlusion, texture, audio bridges, structural rhythm and reusable component recipes. Distinguish Observed, Estimated, Recommended and Unknown.

Read `guide.md`, remove any leaked scratch notes from the user-facing guide while preserving the raw API response, and flag unsupported precision. Spot-check representative frames with ffmpeg when useful; these checks supplement the native video analysis. Summarize the defining style rules, and link the guide plus supporting report files. Mention incomplete/truncated analysis or material uncertainty. Source MP4, analysis clips, prompt, responses, usage metadata and run manifest stay in the output directory. If asked for an edit rather than analysis, use the resulting guide as a reference for the appropriate editing workflow.

The full analysis instructions are in [references/analysis-prompt.md](references/analysis-prompt.md). Official API reference: https://openrouter.ai/docs/guides/overview/multimodal/videos
