# yt-feed-research: setup

Scans the logged-in YouTube home feed in your real Chrome profile for on-niche outlier video ideas and tailors the feed while it goes: every off-niche tile gets "Not interested" (one-off) or "Don't recommend channel" (categorically wrong), then the feed is reloaded and re-scanned until the idea target is hit (default 20 long-form ideas). VidIQ badges (VPH, outlier multiplier, subs) are read straight off the tiles. Claude drives the whole thing, you just trigger it ("scan my home feed", "yt feed research", "tailor my youtube feed").

## Install

Drop this folder into a skills directory:
- `<project>/.claude/skills/yt-feed-research/` for one project, or
- `~/.claude/skills/yt-feed-research/` to use it everywhere.

## Prerequisites

- **Claude-in-Chrome MCP** connected to your real Chrome profile, logged into YouTube. Run from terminal Claude Code (the desktop app opens the MCP tab hidden and the scrape silently fails).
- **VidIQ extension** in that profile (optional; without it views/age still parse but outlier scoring is weaker).
- **YouTube UI in English.** `scripts/feed-tools.js` matches English menu labels and tile text.
- No yt-dlp, no Apify, no API keys. Everything comes off the feed tiles.
- **A filled-in creator profile.** What counts as on-niche is derived at run time from the repo root: the `CLAUDE.md` Creator Profile Niche line, `backbone/offer.md` + `backbone/icp.md`, and `competitor-list.md` `## YouTube` (listed channels are always kept). If the Niche line still shows a `<<` placeholder, the skill stops and asks you to apply your brand kit first.

## Output

Writes `research/YT-Feed-Research_YYYY-MM-DD_HHMMSS.html` (filled from `assets/report-template.html`) and opens it in your default browser (macOS `open <file>`, Linux `xdg-open <file>`, Windows/Git Bash `start "" <file>`). Viewing needs network: thumbnails hotlink from i.ytimg.com and the mono font from Google Fonts. Prior reports are never deleted.

## Gotchas

- Re-inject `scripts/feed-tools.js` after every navigation (page loads wipe `window.*`).
- Max 3 `__dismissAny` calls per `javascript_tool` call; a timed-out call usually still finished, so re-check tile state before re-running.
- Channel mode never falls back to a video-level dismissal: `ix:no-entry` means the menu had no "Don't recommend channel"; run `'video'` explicitly if you still want it gone.
