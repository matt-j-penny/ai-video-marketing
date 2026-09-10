# AI Video Editing Skills

A collection of AI agent skills focused on video editing. Built for creators, marketers, and founders who want AI coding agents to help clean up raw footage before a final edit. Works with Claude Code and any agent that supports the [Agent Skills spec](https://agentskills.io).

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
```

You can also invoke a skill directly:

```
/transcribe
/rough-cut
/level-audio
/create-design-md
/create-frames-md
/storyboard
```

## Contributing

Found a way to improve a skill? Have a new skill to suggest? PRs and issues welcome. Follow the existing `SKILL.md` format (frontmatter with `name`/`description`, then persona, context-gathering, workflow, common mistakes, task-specific questions) and add a matching `evals/evals.json`. **Bump `metadata.last_updated` to today's date whenever you edit a `SKILL.md`** — each skill checks this against today's date and tells the user to re-pull the repo if it's more than 2 weeks stale, so an unbumped date after a real change makes that check lie.

## License

[MIT](LICENSE) - Use these however you want.
