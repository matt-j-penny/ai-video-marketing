# First-run setup

Run this when `~/.config/mograph-remix/config.json` is missing, or when the user asks to change where templates are saved.

## 1. Tools

```bash
for t in yt-dlp ffmpeg ffprobe uv npx; do printf "%-8s " $t; command -v $t || echo MISSING; done
npx -y hyperframes@latest --version
```

If something is missing, give the user its install command and stop until it is installed:

| Missing | Install |
|---|---|
| yt-dlp, ffmpeg/ffprobe | `brew install yt-dlp ffmpeg` |
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| npx | install Node.js 22+ from nodejs.org |

Optionally, the HyperFrames skills (`/hyperframes-core` and others) help with harder builds. Check for `~/.claude/skills/hyperframes-core`; if it's absent, mention that `npx hyperframes skills` installs them. This skill works without them.

## 2. Transcription

The edit step needs word timestamps.
- **Deepgram** (preferred): `$DEEPGRAM_API_KEY` is set, or `env.DEEPGRAM_API_KEY` is in `~/.claude/settings.json`. Then `transcriber = "deepgram"`.
- **No Deepgram key**: tell the user that they can add one to `~/.claude/settings.json` under `env`, or use HyperFrames' local transcriber. Then `transcriber = "hyperframes"`, which uses `npx hyperframes transcribe`.

Never ask the user to paste a key into the chat.

## 3. Where templates go

Ask with AskUserQuestion: "Where should the motion graphics templates be saved?"

1. **Connect my template library**: the user already has a HyperFrames template library, which is a folder with `template-library.html` and `Assets/templates/`.
   - Ask for the folder path. Search likely spots first and offer what you find:
     ```bash
     find ~ -maxdepth 4 -name template-library.html -not -path "*/node_modules/*" 2>/dev/null
     ```
   - Validate it with `$T lib-check <path>`. If it fails, explain why and ask again, or offer option 2.
2. **Create a new template library**: ask where (default `~/HyperFrames-Template-Library`), then run `$T lib-init <path>`. Tell them to open `<path>/template-library.html` in a browser to browse it.
3. **Keep them in this session only**: templates stay in the run folder (`./mograph-remix/<video-id>/templates/`) and nothing is saved anywhere else.

## 4. Save config

```bash
mkdir -p ~/.config/mograph-remix
```

Write `~/.config/mograph-remix/config.json`:

```json
{
  "library": { "mode": "library", "path": "/absolute/path/to/library" },
  "transcriber": "deepgram",
  "configured": "YYYY-MM-DD"
}
```

For option 3, write `"library": { "mode": "session", "path": null }`. Confirm the choice to the user in one line, then continue with the job.
