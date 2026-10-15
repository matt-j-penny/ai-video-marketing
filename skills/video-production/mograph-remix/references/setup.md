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

A library has two parts that can live in different places:
- the **templates folder** (`.../Assets/templates/`, with the template files and often `templates.json`)
- one or more **galleries** (`template-library.html` files that list templates in a `TEMPLATES = [` array). A gallery can be opened as a file, or it can be served by a local app (for example `http://localhost:4300/template-library.html`) from a folder somewhere else.

Several copies can exist, such as an exported copy in Downloads. Saving to a copy the user never opens is the failure this step prevents.

Look for a library first. Ask only when the search can't decide.

1. Run `$T lib-find`. It lists every templates folder, the galleries that show it, when each was last edited and any localhost URL that serves it, a ready `config:` line per folder, and a last line:
   - **`recommended: <folder>`**: use that folder's `config:` line as `library`. It includes every gallery that shows the folder, so saved templates appear in all of them. Tell the user in one line which folder and galleries were picked, and that any other copies found were skipped. Do not ask.
   - **`ambiguous: ...`** (several libraries, none served by a running app): ask with AskUserQuestion which one they open, listing each folder with its last-edited date. Note which ones look like stale copies, such as an export in Downloads.
   - **`no template library found`**: ask with AskUserQuestion: "No template library found. Where should templates go?" The options are:
     - **Create a new template library**: ask where (default `~/HyperFrames-Template-Library`), run `$T lib-init <path>`, and use its `config:` line.
     - **I have one somewhere else**: ask for the gallery path or URL, then build the config by hand: `{"mode": "library", "templates": "<Assets/templates folder>", "galleries": [{"file": "<template-library.html>", "url": "<url or null>"}]}`. To find which file a URL serves, use `lsof -nP -iTCP:<port> -sTCP:LISTEN` and read the server's code.
     - **Keep them in this session only**: templates stay in `./mograph-remix/<video-id>/templates/`.
2. If the user later says the templates went to the wrong place, re-run this step and take their answer.

## 4. Save config

```bash
mkdir -p ~/.config/mograph-remix
```

Write `~/.config/mograph-remix/config.json`:

```json
{
  "library": {
    "mode": "library",
    "templates": "/abs/path/Assets/templates",
    "galleries": [
      { "file": "/abs/path/template-library.html", "url": null },
      { "file": "/abs/other/app/template-library.html", "url": "http://localhost:4300/template-library.html" }
    ]
  },
  "transcriber": "deepgram",
  "configured": "YYYY-MM-DD"
}
```

For session only, write `"library": { "mode": "session" }` and skip step 5.

## 5. Verify the library

Setup is not finished until this passes.

1. Run `$T lib-check`. For each gallery it proves that:
   - the gallery file exists and has a `TEMPLATES = [` array (`const` or `let`)
   - it sits beside the templates folder, or has a `url`
   - most of its entries point at files that really are in the templates folder, so it reads this folder and not a copy
   - its `url`, when set, serves exactly this file
   - the templates folder is writable and `templates.json`, if present, is valid.

   Fix every error and re-run it. A "not reachable" warning means the app is not running; ask the user to start it and re-run, or accept the warning if they only open the file.
2. For each gallery with a `url`, open the URL in the browser and use `find` to confirm one existing template card name is on the page. This proves the app loads templates from this folder, which `lib-check` cannot see.

Confirm the choice to the user in one line, naming the templates folder and each gallery. Then continue with the job.
