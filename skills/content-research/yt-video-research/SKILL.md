---
name: yt-video-research
description: "Researches a video topic before you make it. Finds the YouTube videos on that topic that over-performed in a time window (vidIQ outliers plus top-viewed search), analyses their titles, pulls transcripts and breaks down each winner's hook, angle, format, demos and tips in parallel subagents, mines their comments through the YouTube API (or yt-dlp), and reverse-engineers what viewers actually want from this topic. Then gives you angles, demo ideas and a tips list for your own video, writes the intro with youtube-intro (or hook-generator), hands the structure to outliner if installed, and optionally saves it all to Content OS. Triggers: research videos about, yt video research, what's working for this topic, research this video idea, find outliers on, break down the top videos on, who's done well on, research before I film."
metadata:
  version: 1.0.0
  last_updated: 2026-11-14
---

# YT Video Research: from topic to angle, demos and intro

The user brings a topic for a video they want to make ("Fable 5.2 + Blender"). This skill finds what has already worked on that topic, works out **why** it worked and **what viewers wanted from it**, then helps the user build their own version: angles, demos, a tips list and an intro.

It is a conversation, not a one-shot report. There are two checkpoints where the user steers: after the synthesis (Phase 5) and after the angles (Phase 6). Keep chat replies tight; the user reads findings, not process.

`yt-competitor-research` tracks fixed channels' packaging week to week. This skill is topic-first, goes into transcripts and comments, and ends in a plan for a specific video.

---

## Freshness check

Compare `last_updated` above to today's date. If it's more than 2 weeks old, tell the user this skill may be out of date and suggest re-pulling the `ai-video-marketing` repo, then carry on.

## Prerequisites

- **vidIQ MCP** (`vidiq`): outlier search, YouTube search, video metadata, transcripts. Load the tools with ToolSearch (`select:mcp__vidiq__vidiq_outliers,mcp__vidiq__vidiq_youtube_search,mcp__vidiq__vidiq_get_videos_by_ids,mcp__vidiq__vidiq_video_transcript`). If vidIQ isn't connected, say so and stop: it's the backbone of Phases 1-3.
- **Comments:** `YOUTUBE_API_KEY` in the environment or in `.env` (YouTube Data API v3) is preferred. Without it, `yt-dlp` on PATH is the free fallback. Comments don't use vidIQ.
- **Optional:** Content OS MCP (Phase 9), `youtube-intro` and `outliner` skills (Phases 7-8). Check what's available; never fail because an optional piece is missing.

`<SKILL_DIR>` = this skill's folder (the "Base directory for this skill" path shown at launch).

## Credit budget

vidIQ calls cost about 5 credits each. A full run is roughly 60-100 credits (3-4 searches, 6-9 transcripts, a metadata or image call). Comments cost no vidIQ credits. Tell the user the total at the end of Phase 5.

---

## Phase 0: Intake

Ask once, in a single message, and default whatever isn't answered:

- **Topic**, plus adjacent topics worth searching (e.g. the previous model + the same tool).
- **Time window:** default last month (`thisMonth`); widen to `threeMonths` if results are thin.
- **Long-form or Shorts:** default long-form.
- **Their angle or constraints**, if any (e.g. "must tie to motion graphics", "for beginners").
- Any **factual question** they want answered along the way (e.g. "what's the difference between X and Y?").

If the user's message already covers this, don't ask; go.

## Phase 1: Find what worked

Run these **in parallel in one message**:

1. 2-3 `vidiq_outliers` searches with different phrasings of the topic (the literal topic, a "tool + outcome" phrasing, an adjacent-model phrasing), `publishedWithin` set to the window, `sort: breakoutScore`, `limit: 25`.
2. One `vidiq_youtube_search`: `type: ["video"]`, `order: viewCount`, `publishedAfter` = start of window, `limit: 25`. This catches big videos from big channels that don't score as outliers.

Then:
- Merge and dedupe. Drop off-topic results and re-uploads.
- Note any of **the user's own videos** in the results (their channel is in the project's CLAUDE.md or memory): those are proven angles for this audience.
- Show a shortlist table, ranked: title, channel, subs, views, outlier score, views/hour, age, length.
- Pick **6-9 videos to break down**. Mix the highest outlier scores with the highest absolute views and favour different formats. Briefly say why each was picked.

## Phase 2: Titles and packaging

Across the **whole shortlist** (not just the picks), in the main thread:
- Recurring title patterns ("I Tested X", "X vs Y", "X Is Scary Good at Y", "How to X (Full Workflow)", "I Gave X Full Control") and which ones sit on the highest outlier scores.
- Recurring words and framing: model names, emotional words, outcome promises, "without X" claims.
- Thumbnails only when worth it: `vidiq_get_images` on the top 3-5.

## Phase 3: Transcript breakdowns (subagents)

Split the picks into **3 batches of 2-3 videos** and spawn **3 general-purpose subagents in parallel, in one message**. Transcripts never touch the main context.

Each subagent's prompt must include: the video IDs with title, channel, views and outlier score; the instruction to load `mcp__vidiq__vidiq_video_transcript` via ToolSearch and pull each transcript; the full text of `<SKILL_DIR>/references/breakdown-template.md` pasted in (subagents can't see this file unless you give them the path); and any factual question from Phase 0 that these videos can answer.

## Phase 4: Comments

Pick the **top 4-6 videos** (the biggest outliers plus anything with high comment counts) and run:

```
python3 <SKILL_DIR>/scripts/fetch-comments.py "<scratchpad>/yt-video-research/comments" <id1> <id2> ... --max 100
```

It uses the YouTube Data API when `YOUTUBE_API_KEY` is set (in env or `./.env`) and yt-dlp otherwise, and writes one markdown file per video sorted by likes. Read its stderr for failures (comments disabled, quota) and carry on.

Hand the comment files to **one general-purpose subagent** to read and return, per video and then overall:
- **Questions** viewers ask (gaps to answer).
- **Requests** ("do this with X next", "full tutorial please").
- **Complaints** (too long, sponsor-heavy, didn't work on Mac, clickbait).
- **Praise**: what specifically they loved.
- **Who's watching**: beginners, pros, a specific job?
Keep quotes short and attributed by video.

## Phase 5: What viewers want, and the synthesis (checkpoint 1)

This is the core of the skill. Before writing anything, reverse-engineer the demand:

**What are viewers actually after on this topic?** Look across the winners' "what the viewer came for" lines, the formats that beat their channel average, the titles' promises and the comments. Name the job(s) the audience is hiring these videos for, in your own words. It can be anything: a full tutorial, a quick setup, proof the tool is good, a head-to-head verdict, examples to steal, a money outcome, a story, news, a challenge. Rank the jobs by evidence and say what the evidence is (e.g. "the 3 biggest outliers are all fair tests; the tutorials sit at 1-2x; comments ask 'which should I use?' 20+ times"). Also name jobs that are **under-served**: asked for in comments but not delivered by any winner.

Then present, in this order:
1. **The answer first:** one or two lines on what's working and where the opening is.
2. **Any factual question** from Phase 0, answered from the transcripts.
3. **What viewers want:** the demand analysis above.
4. **Table:** each broken-down video with hook, angle, format.
5. **Patterns:** hooks, formats, titles, comments.
6. **Demos worth borrowing:** specific enough to recreate.
7. **The gap:** the angle nobody has done, tied to the user's own past winners where possible.
8. Credits used.

Stop and let the user react.

## Phase 6: Angles (checkpoint 2)

Give **5 angles**. For each: a working title, why it should work (which outlier, demand or gap it rides), and a short hook in four beats (Payoff / Proof / Context / Setup). End with a recommendation.

- Don't clone a competitor's video. "Similar, not the same": borrow the format or the job, change the subject.
- Every claim in a hook must be one the user can stand behind; mark real numbers as `[placeholders]` for the user to fill.

## Phase 7: Build out the video (iterate with the user)

Once an angle is chosen:
- **Demo/example ideas:** pull from the breakdowns and comments, plus the user's own ideas. When the user adds an idea, go back to the research for evidence that supports or shapes it. Order the final list so **each example teaches one new thing**, with the strongest payoff last.
- **Middle sections** (e.g. "what is the tool", a screenshare plan, install steps): bullet the beats.
- **Tips list:** a numbered list from the research the user can strike from. Keep their removals removed.
- **Production prompts** for each demo if asked: format, length, assets to get, the copy-paste prompt, what to show on camera.
- If the `outliner` skill is available, offer to hand off the chosen angle, examples and tips to it for the full outline; otherwise lay out the structure here.

## Phase 8: Intro

Use the **`youtube-intro`** skill if available (Payoff / Social Proof / Context / Setup). If not, use **`hook-generator`**. If neither is installed, write it in those four beats yourself.

- If the user gives their own draft, keep their wording and tighten it; don't rewrite it into yours.
- Flag a claim that may not hold up once, briefly. If they keep it, keep it.
- Don't add back a section they removed.

## Phase 9: Save to Content OS (optional)

Only if a Content OS MCP is connected (ToolSearch "content-os"); otherwise skip silently, or offer to write a markdown file into `research/` instead.

- Find the matching idea (`list_content_ideas`; the output can be huge, so grep the saved file for the topic) or create one (`content_type` YT Long Form or Short Form, status Researching).
- `script_idea` = the script only (the intro, then sections as they get written).
- `premise` = the outline: examples in order, sections, tips.
- `ai_research` = the shortlist table, what viewers want, patterns and comment insights.
- Update only the fields being changed, and ask before the first write.

---

## Rules

- Parallelise: searches in one message, breakdown subagents in one message.
- Transcripts and comment dumps go to subagents, never into the main thread.
- Note sponsorships: a sponsored tool showing up in every video is a signal about money, not about viewer demand.
- No invented numbers. Costs, prices, market caps and results are `[placeholders]` until the user supplies them.
- Real brands and logos in demo prompts: suggest generic versions.
- Catch tool mix-ups (e.g. an image model named where a video model is needed) and say so in one line.
