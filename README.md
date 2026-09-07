# AI Video Marketing Skills

A collection of AI agent skills focused on video marketing. Built for creators, marketers, and founders who want AI coding agents to help with hooks, UGC ad scripts, AI video generation, YouTube SEO, repurposing, and creative testing. Works with Claude Code and any agent that supports the [Agent Skills spec](https://agentskills.io).

Inspired by [marketingskills](https://github.com/coreyhaines31/marketingskills) — same format, focused specifically on video.

**Contributions welcome!** Found a way to improve a skill or have a new one to add? Open a PR.

## What are Skills?

Skills are markdown files that give AI agents specialized knowledge and workflows for specific tasks. When you add these to your project, your agent can recognize when you're working on a video marketing task and apply the right frameworks and best practices.

## How Skills Work Together

```
                        ┌───────────────────────┐
                        │      video-hooks       │
                        │ (feeds every format)   │
                        └───────────┬────────────┘
                                    │
        ┌───────────────┬──────────┼──────────┬───────────────┐
        ▼                ▼          ▼          ▼               ▼
┌───────────────┐ ┌────────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐
│  Production    │ │  Ads       │ │Discover│ │ Measure  │ │  Partnerships│
├────────────────┤ ├────────────┤ ├────────┤ ├──────────┤ ├──────────────┤
│storyboarding   │ │ugc-ad-     │ │youtube-│ │video-    │ │influencer-   │
│ai-video-       │ │ scripts    │ │video-  │ │analytics │ │ video-briefs │
│ generation     │ │video-ad-   │ │seo     │ │video-ab- │ │              │
│video-          │ │ creative   │ │        │ │ testing  │ │              │
│ repurposing    │ │            │ │        │ │          │ │              │
└────────────────┘ └────────────┘ └────────┘ └──────────┘ └──────────────┘
```

See each skill's **Related Skills** section for the full dependency map.

## Available Skills

| Skill | Description |
|-------|-------------|
| [video-hooks](skills/video-hooks/) | Write and evaluate the first 1-3 seconds of a short-form video — the hook that stops the scroll. |
| [ugc-ad-scripts](skills/ugc-ad-scripts/) | Write UGC-style talking-head ad scripts for TikTok/Reels/Shorts and paid social. |
| [video-ad-creative](skills/video-ad-creative/) | Plan, scale, and iterate video ad creative across Meta, TikTok, YouTube, and LinkedIn. |
| [ai-video-generation](skills/ai-video-generation/) | Choose an AI video model (Veo, Sora, Runway, Kling, and more) and prompt it for marketing footage. |
| [video-repurposing](skills/video-repurposing/) | Turn long-form video (podcasts, webinars, YouTube) into short-form clips. |
| [youtube-video-seo](skills/youtube-video-seo/) | Optimize titles, thumbnails, descriptions, tags, and chapters for YouTube discovery. |
| [video-analytics](skills/video-analytics/) | Read retention curves and engagement metrics to diagnose why a video is or isn't working. |
| [storyboarding](skills/storyboarding/) | Turn a script or concept into a shot list before filming or generating footage. |
| [video-ab-testing](skills/video-ab-testing/) | Structure valid tests between hooks, thumbnails, angles, and full ad concepts. |
| [influencer-video-briefs](skills/influencer-video-briefs/) | Write creator briefs for sponsored or gifted video partnerships. |

## Installation

### Option 1: CLI Install (Recommended)

Use [npx skills](https://github.com/vercel-labs/skills) to install skills directly:

```bash
# Install all skills
npx skills add matt-j-penny/ai-video-marketing

# Install specific skills
npx skills add matt-j-penny/ai-video-marketing --skill video-hooks ugc-ad-scripts

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

Once installed, just ask your agent to help with video marketing tasks:

```
"Write 5 hook options for this TikTok ad"
→ Uses video-hooks skill

"Turn this podcast episode into short clips"
→ Uses video-repurposing skill

"Why is our retention dropping at second 4?"
→ Uses video-analytics skill
```

You can also invoke skills directly:

```
/video-hooks
/ugc-ad-scripts
/youtube-video-seo
```

## Skill Categories

### Hooks & Retention
- `video-hooks` — Opening seconds that stop the scroll
- `video-analytics` — Retention curves and drop-off diagnosis

### Ad Creative
- `ugc-ad-scripts` — Talking-head/UGC ad scripts
- `video-ad-creative` — Creative testing strategy and refresh cadence
- `video-ab-testing` — Structuring and reading creative tests

### Production
- `storyboarding` — Shot lists before filming/generating
- `ai-video-generation` — Model selection and prompting for AI footage
- `video-repurposing` — Long-form to short-form clipping

### Discovery
- `youtube-video-seo` — Titles, thumbnails, descriptions, tags

### Partnerships
- `influencer-video-briefs` — Creator briefs for sponsored content

## Contributing

Found a way to improve a skill? Have a new skill to suggest? PRs and issues welcome. Follow the existing `SKILL.md` format (frontmatter with `name`/`description`, then persona, context-gathering, frameworks, common mistakes, task-specific questions, related skills) and add a matching `evals/evals.json`.

## License

[MIT](LICENSE) - Use these however you want.
