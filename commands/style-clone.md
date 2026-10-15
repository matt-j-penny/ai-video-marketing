---
description: Find the motion graphics in a YouTube video and recreate each one as a reusable HyperFrames template. Add your own video and it edits it with graphics in the same style.
argument-hint: <youtube-url> [your video path or URL]
---

Run the `mograph-remix` skill (`skills/video-production/mograph-remix/SKILL.md`). It handles both jobs: a style URL alone (extract and save templates), or a style URL plus the user's own video (also edit that video in the style). Its setup gate finds and verifies the template library before anything is saved.

$ARGUMENTS
