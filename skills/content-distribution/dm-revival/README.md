# dm-revival: setup

Grinds the Instagram DM inbox in your real, logged-in Chrome to find lost leads (people who showed interest and then went quiet), reads each lead's profile, drafts a personalized re-opener in your voice, and sends approved batches inside the existing threads. Warm follow-up only, never cold outreach. Trigger it with "grind my dms", "dm revival", "find lost leads", "work my inbox", or "dead leads".

## Install

Drop this folder into a skills directory:
- `<project>/.claude/skills/dm-revival/` for one project, or
- `~/.claude/skills/dm-revival/` to use it everywhere.

## Prerequisites

**1. Claude-in-Chrome MCP**, connected, and Claude Code run from the **terminal** (the desktop app spawns the MCP tab hidden, so inbox reads come back empty).

**2. Instagram logged in** on that Chrome profile. The DM inbox only exists logged in; a fresh automation profile or Playwright will not work.

**3. Context files at your project root**, loaded in preflight before anything is classified or drafted:
- `backbone/icp.md`: who counts as a lead (the segments there are the ICP test).
- `backbone/offer.md`: what is sold (interest = a real question about it), plus its "What is NOT sold" list, which the drafts never touch. Offer name and price come from here, never from the skill.
- `voice-dna.md`: the voice rulebook the drafts are written in. While it is still the stub, the Voice/Tone one-liner in your root `CLAUDE.md` is the fallback; drafts read generic until `voice-corpus-builder` has generated the real file.

Works on professional and personal Instagram accounts: with no Primary/General split it works the single thread list, then Requests.

## Output

State log at `outreach/dm-revival/log.json` (project root, created on first run). One entry per handled thread with status `sent | drafted | skipped`, reason, message text, thread URL, and `sent_at` for sends. It makes the grind resumable across sessions, guarantees nobody gets the same revival twice, and is what the send caps (about 15/hour, 40/day) are counted from. Drafts you did not approve resurface once at the start of the next run; drop one and it stays dropped.

## Rails

Any "Try Again Later" banner, action block, or failed send stops the run immediately. Drafts are single-line (Enter sends on IG web). Nothing gets typed into a message box until you approve the batch.
