# ig-feed-research: setup

Scans the logged-in Instagram home feed (reels, carousels, and image posts together) in your real Chrome profile for on-niche content ideas, and tailors the algorithm while it does it: every suggested post that fails the niche test gets three-dots → "Not interested" (plus "Don't suggest posts from X" for categorically wrong accounts). Harvest and tailoring are one loop on one surface. Trigger it with "ig feed research", "scan my instagram feed", "tailor my instagram feed", or "what's my ig pushing".

## Install

Drop this folder into a skills directory:
- `<project>/.claude/skills/ig-feed-research/` for one project, or
- `~/.claude/skills/ig-feed-research/` to use it everywhere.

## Prerequisites

**1. Claude-in-Chrome MCP** connected to your real Chrome profile, logged into Instagram. Terminal Claude Code only: the desktop app spawns the MCP tab hidden and the scrape silently fails.

**2. Instagram UI language set to English.** `scripts/feed-tools.js` matches English strings ('Suggested for you', 'Sponsored', 'Learn more', 'More options', 'Not interested', "Don't suggest posts from"); any other locale classifies every row as followed, misses ads, and returns `no-entry` on every dismissal.

**3. Nothing else to install.** No Apify, no yt-dlp, no Python. `scripts/feed-tools.js` is pasted into the page by the skill itself.

**4. Your brand kit applied.** Fill `brand-kit.md` and say "apply my brand kit" before the first run. The niche filter (what gets kept vs "Not interested") is derived at run time from your Creator Profile in `CLAUDE.md` (the Niche line), `backbone/offer.md`, `backbone/icp.md`, and `competitor-list.md`; the skill refuses to run while the Niche line still holds a placeholder.

## Output

Fills `assets/report-template.html` and writes `research/IG-Feed-Research_YYYY-MM-DD_HHMMSS.html` (dark card grid: outliers, strong picks, carousel steals, borderline, tailoring log), then opens it in your default browser (macOS `open`, Linux `xdg-open`, Windows Git Bash `start "" <file>`). Prior reports are never deleted. Cards are text-only with linked usernames; IG media URLs are signed and expire, so no thumbnails.

## Gotchas

- Instagram action-blocks bots: read + dismiss only, one dismissal at a time, cap around 40 per session, max 2 sessions a day. Stop dismissing on any "Try again later" toast.
- "Not interested" exists only on SUGGESTED home-feed posts. Followed posts and ads get no action (ads are flagged `AD` and refused by the helper).
- Every navigation wipes the injected helpers; re-paste `scripts/feed-tools.js` after any reload.
