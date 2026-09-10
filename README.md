# AI Video Marketing Skills

A collection of AI agent skills for video marketing: researching what's working, writing hooks and scripts in your own voice, editing raw footage, and posting the finished cut. Built for creators, marketers, and founders who want AI coding agents to run their content pipeline. Works with Claude Code and any agent that supports the [Agent Skills spec](https://agentskills.io).

**Contributions welcome!** Found a way to improve a skill or have a new one to add? Open a PR.

## What are Skills?

Skills are markdown files that give AI agents specialized knowledge and workflows for specific tasks. When you add these to your project, your agent can recognize when you're working on a video editing task and apply the right workflow.

## Available Skills

| Skill | Description |
|-------|-------------|
| [video-editing/transcribe](skills/video-editing/transcribe/) | Transcribe a video or audio file with word-level timestamps (Deepgram nova-2 → ElevenLabs → local Whisper) — the input other workflows like rough-cut build on. |
| [video-editing/rough-cut](skills/video-editing/rough-cut/) | Turn a raw talking-head or narrated video into a rough cut — strip dead air and remove bad takes (false starts, repeated takes, fluffs) using a word-level-timestamp transcript. |
| [video-editing/level-audio](skills/video-editing/level-audio/) | Even out a video's narration so no part is noticeably louder or quieter than the rest, using loudness-range measurement and speech-specific dynamics processing. |
| [video-editing/create-design-md](skills/video-editing/create-design-md/) | Create a DESIGN.md design-system doc — from a live site, existing code, or a guided question set when there's no reference material — so motion graphics, title cards, and on-screen UI stay visually consistent. |
| [video-editing/create-frames-md](skills/video-editing/create-frames-md/) | Create a frames.md motion-system doc — timing tokens, easing/springs, entrances/exits, stagger, transitions, and sync rules — from a reference video, existing animation code, or a guided question set, so every animated element moves consistently. |
| [video-production/storyboard](skills/video-production/storyboard/) | Explicit-only (`/storyboard`): build a reviewable beat-by-beat storyboard from a script or video, then turn approved beats into HTML, React, and Remotion scenes. |
| [video-analysis/transcribe-url](skills/video-analysis/transcribe-url/) | Transcribe any public video URL (YouTube, Instagram, TikTok, X, and more) with yt-dlp and local faster-whisper into a markdown transcript. |
| [content-research/ig-competitor-research](skills/content-research/ig-competitor-research/) | Rank tracked Instagram competitors' last-week posts by likes and breakout score, transcribe and break down the winners, and build a visual HTML report (Apify MCP). |
| [content-research/yt-competitor-research](skills/content-research/yt-competitor-research/) | Rank tracked YouTube channels' last-week uploads by views and breakout score, break down each winner's title and thumbnail, and build a visual HTML report (yt-dlp, free). |
| [content-research/ig-feed-research](skills/content-research/ig-feed-research/) | Scan your logged-in Instagram home feed for on-niche ideas and hit "Not interested" on everything off-niche to tune the algorithm (Claude in Chrome). |
| [content-research/yt-feed-research](skills/content-research/yt-feed-research/) | Scan your logged-in YouTube home feed for outlier ideas using VidIQ badges, dismissing off-niche tiles to tailor the feed (Claude in Chrome). |
| [content-writing/hook-generator](skills/content-writing/hook-generator/) | Write 6-8 spoken hooks for a video idea, each built on a proven framework from a 404-hook bank ranked by views. |
| [content-writing/scriptwriter](skills/content-writing/scriptwriter/) | Turn a research pick or raw idea into a filmable beat sheet in Notion, drafted against verbatim transcripts of your own top videos and voice-linted. |
| [content-writing/voice-corpus-builder](skills/content-writing/voice-corpus-builder/) | Build `voice-corpus/` from your own top YouTube and Instagram videos and draft `voice-dna.md`, the voice rulebook the writing skills use. |
| [content-writing/knowledge-compile](skills/content-writing/knowledge-compile/) | Refresh `knowledge/`: short, source-linked pages summarizing your research, transcripts, and business docs for ideation and scripting. |
| [content-writing/yt-description](skills/content-writing/yt-description/) | Write a finished long-form video's YouTube description in your channel's live format, with chapter timestamps indexed from the final export. |
| [content-distribution/auto-poster](skills/content-distribution/auto-poster/) | Post or schedule a finished video to every connected platform through Zernio, writing a caption from the transcript if you don't give one. |
| [content-distribution/carousel-generator](skills/content-distribution/carousel-generator/) | Design 4:5 Instagram carousels: an AI-generated cover plus token-locked HTML body slides rendered to PNGs, with a caption package. |
| [content-distribution/dm-revival](skills/content-distribution/dm-revival/) | Work your Instagram DM inbox for lost leads and draft personalized re-openers in your voice, sending only batches you approve. |

The `content-*` skills and `transcribe-url` run inside the [Content OS workspace](#content-os-workspace).

## Installation

### Option 1: CLI Install (Recommended)

Use [npx skills](https://github.com/vercel-labs/skills) to install skills directly:

```bash
# Install all skills
npx skills add matt-j-penny/ai-video-marketing

# Install a specific skill
npx skills add matt-j-penny/ai-video-marketing --skill rough-cut

# List available skills
npx skills add matt-j-penny/ai-video-marketing --list
```

> [!TIP]
> If you run the command from **inside** an agent session, pass the agent explicitly so it installs where Claude Code reads from:
>
> ```bash
> npx skills add matt-j-penny/ai-video-marketing -a claude-code
> ```

### Option 2: Claude Code Plugin

```bash
/plugin marketplace add matt-j-penny/ai-video-marketing
/plugin install ai-video-marketing
```

### Option 3: Clone and Copy

```bash
git clone https://github.com/matt-j-penny/ai-video-marketing.git
cp -r ai-video-marketing/skills/* .agents/skills/
```

### Option 4: Git Submodule

```bash
git submodule add https://github.com/matt-j-penny/ai-video-marketing.git .agents/ai-video-marketing
```

## Usage

Once installed, just ask your agent to help with video editing tasks:

```
"Transcribe this interview with word-level timestamps"
→ Uses video-editing/transcribe skill

"Make a rough cut of this talking-head video, cut the silences and bad takes"
→ Uses video-editing/rough-cut skill

"The voice in this video is loud in some parts and quiet in others, even it out"
→ Uses video-editing/level-audio skill

"Build me a DESIGN.md for the title cards and lower-thirds in this explainer video"
→ Uses video-editing/create-design-md skill

"Write a frames.md so all the animations in my explainer series move the same way"
→ Uses video-editing/create-frames-md skill

"/storyboard turn this script into a storyboard I can review"
→ Uses video-production/storyboard skill

"Research my Instagram competitors"
→ Uses content-research/ig-competitor-research skill

"Write me hooks for a video about batching a month of content"
→ Uses content-writing/hook-generator skill

"Post this video: ~/Downloads/final.mp4"
→ Uses content-distribution/auto-poster skill
```

You can also invoke a skill directly:

```
/transcribe
/rough-cut
/level-audio
/create-design-md
/create-frames-md
/storyboard
/transcribe-url
/ig-competitor-research
/yt-competitor-research
/ig-feed-research
/yt-feed-research
/hook-generator
/scriptwriter
/voice-corpus-builder
/knowledge-compile
/yt-description
/auto-poster
/carousel-generator
/dm-revival
```

## Content OS workspace

The content skills read and write files in one project folder: your creator profile (`CLAUDE.md`), `backbone/` (offer, ICP, messaging, vision), `voice-dna.md`, `voice-corpus/`, `competitor-list.md`, `notion-pipeline.md`, and output folders like `research/` and `transcripts/`. [`content-os/`](content-os/) is that folder as a template, with a one-command installer. To set it up, copy the template and install the skills into it:

```bash
git clone https://github.com/matt-j-penny/ai-video-marketing.git
cp -R ai-video-marketing/content-os ~/content-os
mkdir -p ~/content-os/.claude/skills
cp -R ai-video-marketing/skills/*/* ~/content-os/.claude/skills/
```

Then open `~/content-os` in Claude Code and say **"run the setup"**. [content-os/SETUP.md](content-os/SETUP.md) has the full walkthrough.

## Contributing

Found a way to improve a skill? Have a new skill to suggest? PRs and issues welcome. Follow the existing `SKILL.md` format (frontmatter with `name`/`description`, then persona, context-gathering, workflow, common mistakes, task-specific questions) and add a matching `evals/evals.json`. **Bump `metadata.last_updated` to today's date whenever you edit a `SKILL.md`** — each skill checks this against today's date and tells the user to re-pull the repo if it's more than 2 weeks stale, so an unbumped date after a real change makes that check lie.

## License

[MIT](LICENSE) - Use these however you want.
