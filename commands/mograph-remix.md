---
description: Recreate a YouTube video's motion graphics as HyperFrames templates, then edit your own video with graphics in the same style.
argument-hint: <youtube-url> [your video path or URL] [e.g. "first 2 minutes only"]
---

Run the `mograph-remix` skill (`skills/video-production/mograph-remix/SKILL.md`) on the request below.

0. Run first-time setup if `~/.config/mograph-remix/config.json` doesn't exist (tools, transcription, and where templates are saved: connect a library, create one, or this session only).
1. Extract: find the motion graphics, recreate each as a template with a moment card (when to use it), and write the style guide.
2. Save the templates to the configured library.
3. If a new video was given: transcribe it, plan graphics against the moment cards, wait for plan approval, build, verify, preview. Render only on a yes.

$ARGUMENTS
