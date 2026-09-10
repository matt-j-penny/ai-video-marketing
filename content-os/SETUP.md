# 🛠️ Setup — read this first

This is a **content system you run with [Claude Code](https://claude.com/claude-code).** Research
your niche, generate hooks, write scripts in your own voice, keep a Notion pipeline, design Instagram
carousels, write YouTube descriptions, post to every platform. Claude runs each step through a skill;
you talk to it in plain English.

**Runs natively on macOS, Windows, and Linux.**

The fastest path: get the files (step 0 below), open this folder in Claude Code, and say **"run the setup"**. Claude runs the
one-command installer (**`./setup.sh`**: installs every tool via Homebrew on macOS / winget on Windows /
apt+uv on Linux, pre-builds the transcription engine and the carousel renderer, verifies itself, safe to
re-run), tells you which accounts still need connecting, and then walks you through
**`brand-kit.md`**, the one file that makes the system yours. Everything below is the same setup by
hand, if you prefer to see each step.

### 🪟 On Windows — one install first

No WSL, no VM. The scripts run through **Git Bash**, the shell that ships with **Git for Windows**
(also the shell Claude Code uses on Windows):

1. `winget install Git.Git` (in PowerShell), then restart Claude Code so it finds Git Bash.
2. Put the project anywhere normal (e.g. `C:\Users\<you>\content-os`, see step 0) and open that
   folder in Claude Code.
3. Everything below runs unchanged; wherever a command says `brew`, use the **Windows (winget)**
   line. After any `winget install`, open a **new** terminal (and restart Claude Code once) so PATH
   picks the tool up. Python on Windows is `python`, not `python3` (the scripts handle it).

---

## 0. Get the files

This folder is the `content-os/` template from the
[ai-video-marketing](https://github.com/matt-j-penny/ai-video-marketing) repo. The skills live in
that repo's `skills/` folder and get copied into `.claude/skills/` here:

```bash
git clone https://github.com/matt-j-penny/ai-video-marketing.git
cp -R ai-video-marketing/content-os ~/content-os
mkdir -p ~/content-os/.claude/skills
cp -R ai-video-marketing/skills/*/* ~/content-os/.claude/skills/
```

To update the skills later, `git pull` and repeat the last line. It overwrites
`.claude/skills/yt-description/references/links.md` and any carousel templates you saved, so back those
up first (your auto-poster `.env` isn't in the repo, so it's left alone).

## 1. Install the tools

**Automatic** (recommended):

```bash
./setup.sh
```

Installs everything missing, builds the shared faster-whisper engine
(`~/.cache/content-os/whisper-venv`) and the carousel renderer (Playwright + Chromium), runs
`./check-setup.sh`, and writes the `.setup-complete` marker. Re-run after any restart; it skips what's
done. The one manual step it can ask of you: installing Homebrew on a fresh Mac (needs your password),
or the `sudo apt` lines on Linux.

**Manual**, if you'd rather:

```bash
./check-setup.sh      # report-only: prints the exact install command for anything missing
```

macOS: `brew install uv ffmpeg yt-dlp jq node python`
Windows: `winget install astral-sh.uv Gyan.FFmpeg yt-dlp.yt-dlp jqlang.jq OpenJS.NodeJS.LTS Python.Python.3.12`
Linux: `sudo apt install -y ffmpeg jq curl python3` + Node ≥ 22 via NodeSource + `curl -LsSf https://astral.sh/uv/install.sh | sh` + `uv tool install yt-dlp`

Then, once: `bash .claude/skills/carousel-generator/install.sh` (npm deps + Chromium, ~130 MB).

Whisper models (~75 MB to ~460 MB) download from Hugging Face the first time each skill transcribes.
Needs internet once.

## 2. Connect your accounts (Claude tells you which of these are still missing)

| Connection | Used by | How |
|---|---|---|
| **Notion MCP** | the content pipeline DB, `scriptwriter`, `yt-description` | `claude mcp add --transport http notion https://mcp.notion.com/mcp`, then `/mcp` inside Claude Code to sign in, then restart Claude Code |
| **Apify MCP** | `ig-competitor-research`, the Instagram half of your voice corpus | `claude mcp add --transport http Apify https://mcp.apify.com` (capital A), then `/mcp` to sign in. Pay-as-you-go, roughly $0.20 per research run |
| **Claude in Chrome** (extension) | `yt-feed-research`, `ig-feed-research`, `dm-revival` | Install the extension in the Chrome profile that's logged in to YouTube/Instagram. Run Claude Code from the **terminal** for these skills (the desktop app can't drive the tab) |
| **Zernio** (posting) | `auto-poster` | Create an account, connect your platforms, copy the API key: `cp .claude/skills/auto-poster/.env.example .claude/skills/auto-poster/.env` and paste it there. Claude fills the account IDs for you |
| **Higgsfield** (optional) | AI covers in `carousel-generator` | `curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh \| sh` then `higgsfield auth login`. Skip it and carousels use a typographic cover |

Using the Claude desktop app instead of the CLI? Add Notion and Apify under Settings → Connectors;
the skill instructions are the same.

## 3. Make it yours (required for anything in your voice)

1. Open **`brand-kit.md`** and fill in Part A: name, handles, niche, offer (name, URL, price,
   deliverables, comment keyword), who it's for, proof, competitors, your Notion parent page.
   Ten minutes. Leave blanks if you must; Claude asks for them.
2. Say **"apply my brand kit"**. Claude writes your `CLAUDE.md` profile, the four `backbone/` files,
   `competitor-list.md`, creates the Notion content database (schema in `notion-pipeline.md`), fills
   the auto-poster account IDs, then runs **`voice-corpus-builder`**: it pulls your top YouTube uploads
   and Instagram reels, transcribes them into `voice-corpus/`, and drafts `voice-dna.md`, the rulebook
   every writing skill uses. That last step is what makes scripts sound like you instead of like AI.
3. Optional: drop 3-4 square photos of your face into `assets/face-refs/` for AI carousel covers.

## 4. First things to try

- **"research my competitors on YouTube"** (yt-competitor-research, no accounts needed; needs your
  competitor list from the brand kit, or just name the channels inline) or **"instagram competitor
  research"** (same, plus Apify).
- **"write me hooks for a video about X"** (hook-generator).
- **"script this: <a research pick or an idea>"** (scriptwriter → beat sheet in Notion).
- **"make a carousel about X"** (carousel-generator → PNGs + caption in `carousel/outputs/`).
- **"post this video: ~/Downloads/final.mp4"** (auto-poster → Zernio → every connected platform).
- **"write the youtube description for <video>"** (yt-description).
- **"transcribe this link: <url>"** (transcribe-url).

The whole pipeline and every rule is documented in `CLAUDE.md`; each skill's own README lives in
its folder under `.claude/skills/`.

---

## What's in the box

| Path | What it is |
|------|-----------|
| `CLAUDE.md` | The system's brain: the pipeline, the Notion rules, the folder map, the gotchas. |
| `SETUP.md` | This file. |
| `brand-kit.md` | The one file you fill in; "apply my brand kit" pushes it everywhere. |
| `setup.sh` / `check-setup.sh` | One-command installer / report-only checker (macOS, Windows, Linux). |
| `.claude/skills/` | The 13 skills (each with a SKILL.md, most with a README and scripts). |
| `backbone/` | Your business docs (templates until you apply the brand kit). |
| `voice-corpus/`, `voice-dna.md` | Your voice, built from your own videos by voice-corpus-builder. |
| `competitor-list.md`, `notion-pipeline.md` | Who to research; the Notion schema + your DB ids. |
| `knowledge/`, `research/`, `transcripts/`, `carousel/outputs/`, `descriptions/` | Where the outputs land (start empty, each has a README). |
