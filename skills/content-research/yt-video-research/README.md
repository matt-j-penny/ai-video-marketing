# yt-video-research — setup

Topic in, video plan out. Finds the YouTube videos on a topic that over-performed in a time window, breaks down their titles, hooks, angles, formats, demos and tips from transcripts, mines their comments, works out what viewers actually want from the topic, then helps you pick an angle, choose demos, build a tips list and write the intro. Trigger it with "research videos about <topic>" or `/yt-video-research <topic>`.

## Prerequisites

- **vidIQ MCP** connected (outliers, search, metadata, transcripts). A full run uses roughly 60-100 vidIQ credits.
- **Comments:** a YouTube Data API v3 key as `YOUTUBE_API_KEY` in your environment or project `.env` (free quota covers many runs). Without a key, `yt-dlp` on PATH is used instead.
- Python 3 (stdlib only).

## Optional

- `youtube-intro` skill: writes the intro in the Payoff / Social Proof / Context / Setup framework. Falls back to `hook-generator`.
- `outliner` skill: takes the chosen angle and builds the full outline.
- Content OS MCP: saves the script, outline and research to your idea card.

## Files

- `SKILL.md`: the workflow.
- `references/breakdown-template.md`: what each transcript subagent reports per video.
- `scripts/fetch-comments.py`: top comments per video via the YouTube API or yt-dlp.
