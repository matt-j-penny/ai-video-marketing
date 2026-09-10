# CLAUDE.md — Content OS

<<YOUR_NAME>>'s content workspace for Instagram and YouTube. Not a code repo: a content system where
**Claude IS the application.** This system is the **front half** of a content pipeline: research,
ideation, hooks, scripting, the Notion pipeline, standalone IG carousels, and final posting. Each step
runs through a skill in `.claude/skills/`. Video editing is a separate system (the Claude Video Editor,
`~/Projects/video-editor` if you run it); this repo hands off filmed clips to it and posts the finished
cut when it comes back.

---

## 🪟 On Windows? One check first

This system runs natively on **macOS, Windows, and Linux** (no WSL, no VM). On Windows the `.sh`
scripts run through **Git Bash** (installed with Git for Windows), the same shell Claude Code itself
uses there. Run `uname -s` in the shell: `Darwin` / `Linux` / `MINGW…` / `MSYS…` → set. A
command-not-found or PowerShell-looking output → Git for Windows is missing: have the user run
`winget install Git.Git` in PowerShell, restart Claude Code, re-check. Python on Windows is `python`,
never `python3` (that name is a Store stub; every script here probes for both).

---

## 🚦 FIRST RUN — onboarding gate (read before doing anything else)

A SessionStart hook (`.claude/hooks/setup-check.sh`) injects a reminder for as long as onboarding is
incomplete. Trigger this flow whenever the user says **"run the setup"** / **"set me up"** /
**"continue setup"**, or asks for any skill while the tools aren't installed.

**Two deterministic states.** (a) Tools done ⇔ the marker file **`.setup-complete`** exists (written by
`./setup.sh` after `./check-setup.sh` passes). (b) Personalized ⇔ **`CLAUDE.md` contains no ALL-CAPS
placeholder tokens** (the `YOUR_NAME`-style tokens wrapped in double angle brackets; written by "apply my
brand kit"; the hook checks `grep -E '<<[A-Z][A-Z0-9_]*'`). Both present ⇒ skip this gate, work normally.
Marker present but the user says "continue setup" ⇒ don't redo step 1; re-run `./setup.sh` once
(instant) and pick up at step 2.

0. **Skills: check `.claude/skills/` first.** Missing or empty ⇒ the skills aren't installed yet: point
   the user at step 0 of `SETUP.md` (copy them in from the ai-video-marketing repo) and wait until
   they're there; `./setup.sh` can't build the carousel renderer without them.
1. **Tools: run `./setup.sh` yourself.** Don't ask first and don't hand the user a command list;
   announce what it's doing as it goes. It detects the OS (macOS → Homebrew, Windows → winget, Linux →
   prints the sudo apt lines + installs uv/yt-dlp itself), installs every missing tool (uv, ffmpeg,
   yt-dlp, jq, node, python), **pre-builds the shared transcription engine** (faster-whisper venv at
   `~/.cache/content-os/whisper-venv`) and the **carousel renderer** (Playwright + Chromium), verifies
   with `./check-setup.sh`, writes `.setup-complete`, and prints the connections checklist. Idempotent:
   re-run after any interruption. Exits: **0** done → step 2. **2** (Windows) → fresh PATH needed: walk
   the user through a Claude Code restart, then re-run. **1** → read the output; Homebrew missing (macOS)
   → the user runs the printed one-liner (needs their password); Linux → the user runs the printed sudo
   apt lines; then re-run.
2. **Connections: check, then list only what's missing, once.** These are the user's accounts; a script
   can't do them, and you never ask for tokens or keys in chat. "Probe" = look for the tool in your tool
   list (use `ToolSearch` when tools are deferred). Desktop-app users add the same servers under
   Settings → Connectors instead of `claude mcp add`; the skills work the same either way.
   - **Notion MCP** (the pipeline DB + scriptwriter): probe for `notion-search`. Missing → the user runs
     `claude mcp add --transport http notion https://mcp.notion.com/mcp`, then `/mcp` to sign in, then
     restarts Claude Code.
   - **Apify MCP** (ig-competitor-research + the IG half of the voice corpus): probe for `call-actor`.
     Missing → `claude mcp add --transport http Apify https://mcp.apify.com` (capital A: the research skills
     address the tools as `mcp__Apify__…`), then `/mcp` (Apify account, pay-as-you-go: about $0.20 per
     research run).
   - **Claude in Chrome** extension (feed research + dm-revival): probe for `tabs_context_mcp`. Missing →
     install the extension in Chrome; these skills also need Claude Code run from the **terminal**, not
     the desktop app (the desktop app spawns the MCP tab hidden and reads come back empty).
   - **Zernio** (auto-poster): `.claude/skills/auto-poster/.env` with `ZERNIO_API_KEY` (the user copies
     `.env.example` and pastes the key themselves; you fill the account IDs later from the API).
   - **Higgsfield** (optional, AI carousel covers): CLI + `higgsfield auth login`. Body-only carousels
     (typographic cover) work without it.
   Present the missing ones as one short checklist and move on. `transcribe-url`, the feed-research skills
   (with Chrome), and `hook-generator` work right away; competitor research needs the competitor list from
   brand-kit section 6 (the shipped `competitor-list.md` only has EXAMPLE blocks, which the skills ignore),
   so it comes alive with the brand kit or the moment the user names handles inline. Say so.
3. **Brand kit: required for anything in the user's voice.** Point them at `brand-kit.md` (Part A, ten
   minutes) and, when they say **"apply my brand kit"**, follow **Part B** exactly: CLAUDE.md profile →
   `backbone/` → `competitor-list.md` → Notion DB (`notion-create-database`, schema in
   `notion-pipeline.md`) → auto-poster `.env` account IDs → yt-description `links.md` → then run the
   `voice-corpus-builder` skill (the long step; it builds `voice-corpus/` + `voice-dna.md` from their own
   top videos) → verify (`find_voice.py --list`, one hook-generator spread, and
   `grep -cE '<<[A-Z]' CLAUDE.md` prints 0). Blanks stay as visible ALL-CAPS placeholders; never invent
   numbers or an offer.

**Restart walkthrough (be exact and friendly):** *"Quit Claude Code completely (Cmd+Q on Mac / close
the app on Windows; in a terminal: exit `claude`, then open a NEW terminal window so PATH refreshes),
reopen it in this same folder, and say **continue setup**."* On resume, re-run `./setup.sh` (it skips
what's done) and continue. Never assume a restart loaded an MCP; probe for its tools first.

---

## Creator Profile

### Handles & Links

- **Instagram:** [@<<YOUR_IG_HANDLE>>](https://www.instagram.com/<<YOUR_IG_HANDLE>>/)
- **YouTube:** [@<<YOUR_YT_HANDLE>>](https://www.youtube.com/@<<YOUR_YT_HANDLE>>) (channel ID `<<YOUR_YT_CHANNEL_ID>>`)
- **TikTok:** @<<YOUR_TIKTOK_HANDLE>>
- **The offer:** <<OFFER_NAME>> · <<OFFER_URL>>

- **Niche:** <<YOUR_NICHE_ONE_LINER>>
- **Voice/Tone:** <<YOUR_VOICE_ONE_LINER>> (the real rulebook is `voice-dna.md`, generated from
  `voice-corpus/` by `voice-corpus-builder`; this line is the fallback until it exists)
- **Proof:** the live numbers (followers, revenue, members, wins) live in `backbone/vision.md` +
  `backbone/messaging.md` (proof bank). They go stale fast: pull from there, never restate them here or
  in a skill.

### Offer — one offer, one motion (canonical: `backbone/offer.md`)

**<<OFFER_NAME>> is the business.** Price, deliverables, positioning, and the comment keyword live in
`backbone/offer.md`; never hardcode the price in content, captions, or skills (say "the community" /
the offer name and read the price from the backbone when it has to appear).

**Never pitched:** <<RETIRED_OFFERS>>. Side doors (a paid call, a service page) are never a content CTA.

Full backbone: `backbone/{vision,icp,offer,messaging}.md`, the single source of truth for the business.
Load on demand.

---

## Content Pipeline

The front half is one linear flow. Each step has a dedicated skill (or is the creator's job):

| Step | Skill | What It Does |
|------|-------|--------------|
| 1. Research | `ig-competitor-research`, `yt-competitor-research`, `yt-feed-research`, `ig-feed-research` | Scrape competitors / scan the algorithm, output a ranked visual HTML report to `research/`. The two competitor skills read `competitor-list.md` (top 5 handles by default, top 3 posts each, last week): IG enriches winners with transcripts + media breakdowns (Apify MCP), YT with title + thumbnail packaging breakdowns (yt-dlp, free). `yt-feed-research` / `ig-feed-research` scan the logged-in home feed in the real Chrome profile for algorithm-pushed outliers while tailoring the feed (Not-interested clicks on off-niche content). |
| 2. Ideation | _(no skill: the creator's job, in chat)_ | Pull the research, pick winners, hand to scripting. |
| 3. Hooks | `hook-generator` | Writes scroll-stopping spoken hooks from a ranked 404-hook bank, matched to 8 proven hook structures, in the creator's voice. Feeds ideation/scripting. |
| 4. Scripting | `scriptwriter` | Turns a pick or raw idea into a beat sheet in Notion. Writes against verbatim few-shot examples from `voice-corpus/` with a voice-lint subagent pass: imitation, not description. |
| 5. Filming → editing handoff | _(the creator)_ | Records on camera from the beat sheet, then edits (in the Claude Video Editor if they run it, or their own editor). Rough cut, finishing, thumbnails happen there, not here. |
| 6. Posting | `auto-poster` | Posts/schedules the finished cut through Zernio to every account in `.claude/skills/auto-poster/.env`. Writes a caption; transcribes the video if none is given. |
| 6b. YT description | `yt-description` | Long-form only. Pulls the creator's last published description off the channel as the live skeleton, reads the word-for-word script (a video-editor job if present, else the Notion beat sheet), builds real chapter timestamps by indexing the final export, picks the link blocks, writes copy to `descriptions/`. |

### Videos live in Notion: resolve + sync

Every video we work on is a page in the Notion content DB (`notion-pipeline.md` = live schema; flow
`Idea → Scripting → To Edit → Editing → Review → Ready → Posted → Archived`). Two standing rules:

1. **Resolve every video reference.** When the user mentions a video by name or description, find its
   page before doing anything with it: `notion-search` with ONE distinctive keyword from the title,
   scoped to the DB's data source (`data_source_url: collection://<Data source ID>` from `notion-pipeline.md`; it must be the data source, not the database), then `notion-fetch` the
   hit for status + body. Multiple hits: list them and ask. Zero hits when we're starting real work on
   it: create the page (`notion-create-pages`, Status `Idea` or the stage that matches).
2. **Status moves are automatic side effects.** When a pipeline step completes in a session, flip the
   page in the same turn (`notion-update-page`). Don't ask first:
   - `scriptwriter` lands a beat sheet → `Scripting` (the skill sets this on create)
   - the user says it's filmed / hands clips to the editor → `To Edit` (+ `Raw Footage` if a link is given)
   - `auto-poster` succeeds → `Posted` + `Post Date` = today
   - any other state the user reports → the matching status
   (If they run the Claude Video Editor, the `Editing` / `Review` / `Ready` flips happen there.)

Helper: `transcribe-url` pulls a transcript from any video URL (not part of the main pipeline).
Helper: `knowledge-compile` refreshes the compiled `knowledge/` layer after high-signal research or a positioning change.
Helper: `carousel-generator` is a standalone IG content lane: turns trends/news/posts into polished carousel PNGs + a caption package (AI cover + token-locked HTML body).
Helper: `voice-corpus-builder` builds/refreshes `voice-corpus/` from the creator's own top videos and drafts `voice-dna.md`. Run at onboarding and whenever a new batch of winners lands.
Helper: `dm-revival` is the outreach lane outside the linear pipeline: grinds the IG DM inbox in real Chrome for lost leads and drafts personalized re-openers; resumable ledger in `outreach/dm-revival/log.json`.

**One transcription engine.** Every skill that transcribes (transcribe-url, ig-competitor-research
reels, auto-poster captions, voice-corpus-builder, yt-description chapter index) runs faster-whisper from
the same persistent venv, `~/.cache/content-os/whisper-venv` (built once by `uv`, sentinel-gated,
`CONTENT_OS_WHISPER_VENV` overrides). Models download from Hugging Face on first use (tiny.en for
captions, small.en for research). Nothing else to install.

---

## Folder Structure

| Folder | What's In It |
|--------|--------------|
| `.claude/skills/` | The 13 skills: research ×4, hook-generator, scriptwriter, yt-description, auto-poster, transcribe-url, knowledge-compile, carousel-generator, voice-corpus-builder, dm-revival. |
| `brand-kit.md` | The one file you fill in. "apply my brand kit" pushes it everywhere below (Part B = the exact map). |
| `backbone/` | Your business, the single source of truth: `vision.md`, `icp.md`, `offer.md`, `messaging.md` (dated "Current as of" headers). Every price/proof number comes from here. |
| `voice-corpus/` | Your own top-performing videos as verbatim tagged transcripts with view counts. The few-shot voice source for `scriptwriter`. Built by `voice-corpus-builder`; query via `find_voice.py`, don't read wholesale. |
| `voice-dna.md` | Your speech patterns, openers, closers, slang, anti-patterns, generated from the corpus. Feeds every writing skill. |
| `notion-pipeline.md` | Live schema for your Notion content database (IDs, properties, status flow). Skills load this for IDs/shapes. |
| `competitor-list.md` | Tracked competitor handles/channels (YouTube + Instagram sections). Order = priority. |
| `knowledge/` | Compiled repo memory (starts empty). After research runs, `knowledge-compile` writes short source-linked pages here; start here for strategy/ideation before opening raw reports. |
| `research/` | Research reports, `*-Research_YYYY-MM-DD[_HHMMSS].html`. Never deleted. |
| `transcripts/` | Raw transcripts by source: `url/`, `local/`, `analysis/` (see its README). Nothing loose at the top level. |
| `carousel/outputs/` | Rendered carousels: `<slug>/carousel.json`, `cover/`, `slide_XX.png`, `contact_sheet.png`, `caption.md`. |
| `descriptions/` | Written YouTube descriptions, `<job>_<YYYY-MM-DD>.md`. |
| `outreach/` | `dm-revival/log.json`, the DM lane's resumable ledger (created on first run). |
| `assets/face-refs/` | Optional: 3-4 photos of your face for AI carousel covers (`face_refs: true`). |
| `setup.sh` / `check-setup.sh` | One-command installer / report-only checker (OS-aware). |

Secrets: the ONLY `.env` is `.claude/skills/auto-poster/.env` (Zernio key + account IDs; copy from
`.env.example`). Notion, Apify, and Chrome are OAuth-connected MCPs, never tokens; never ask the user
to paste or export an API token in chat.

---

## Rules

- **Research is research-skills only.** Don't make ad-hoc scraper or API calls from chat; if a request
  needs research data, invoke the matching `*-research` skill (`ig-competitor-research`,
  `yt-competitor-research`, `ig-feed-research`, `yt-feed-research`). Scrapers live *inside* the skills.
- **Use `knowledge/` first for synthesis** once it exists; verify important claims against source files.
- **Refresh compiled memory when signal changes.** After high-signal research or a positioning change,
  run `knowledge-compile` to update only the affected `knowledge/` pages.
- **Don't improvise scripts inline.** Scripts go through `scriptwriter` (drafted against verbatim
  `voice-corpus/` examples, linted). Don't write scripts in chat or invent hook/structure rules.
- **Every piece of content ties back to one CTA:** the offer in `backbone/offer.md` (comment keyword
  or a direct mention). Nothing in `backbone/offer.md`'s "not sold" list, ever. The skills handle this;
  just don't drop CTAs by accident.
- **Document, don't manufacture.** Authenticity outperforms. Real numbers only, from the backbone.
- **One hardened path per step.** No fallback chains, no env-token fallbacks. If a step fails twice, stop
  and tell the user what failed.
- **Surgical changes only** when editing skills or context files. Touch what's asked.

---

## Lab Notes / Gotchas (tool-level, learned the hard way)

- `carousel-generator`: `cover.py` needs network (run its Bash with the sandbox disabled); `render.js`
  runs fine sandboxed. Output lands next to the manifest (`carousel/outputs/<slug>/`); `--out` overrides.
  Higgsfield `nano_banana_2` accepts `4:5`. Carousels are posted by hand in the IG app (auto-poster is
  single-media).
- `auto-poster`: Zernio compresses before the TikTok upload but hands the raw file to Instagram's Graph
  API; anything over ~100 MB can sit at `awaiting-finalize` forever. Downscale to 1080p first (`-crf 20
  -maxrate 12M`, keep framing). A stuck IG post leaves a live container open, so never re-post until the
  old record is deleted or it double-posts. Threads captions silently fail over 500 chars (post a trimmed
  Threads version separately). Zernio account IDs change on every OAuth reconnect ("accounts do not
  belong to this user" = stale ID; refresh via `GET /accounts` and update the skill `.env`). An interrupted
  post may already have fired server-side: reconcile via `GET /posts` before re-running.
- Apify: `apify/instagram-post-scraper` returns no play counts (rank by likes); `detailedData` is what
  returns the reel `videoUrl` + carousel `images[]` (signed, expire in hours: download immediately).
  Fire `call-actor` with `waitSecs: 0` and poll `get-actor-run`; pull with `get-dataset-items` and no
  `fields` filter so the result spills to disk; `jq '.items'` it, never read the blob.
- Chrome-MCP skills (feed research, dm-revival) only work when Claude Code runs from the terminal;
  the desktop app's MCP tab is hidden and reads come back empty. YouTube's `/videos` sort is sticky:
  always click Latest. English UI only for the feed helpers (they match English menu labels).
- YouTube titles drift (competitors A/B retitle within hours): carry the video ID through every step,
  never re-match by title. `yt-dlp` breaks when YouTube changes something; `brew upgrade yt-dlp` /
  `winget upgrade yt-dlp.yt-dlp` / `uv tool upgrade yt-dlp` fixes most download errors.
- Bash cwd resets to the project root on every new user turn: use absolute paths (or the documented
  from-root paths) in every command; never rely on a `cd` from a previous turn.
- Windows (Git Bash): where a skill doc says `python3 x.py`, run `python x.py`; "open the report" =
  `start "" <file>` (macOS `open`, Linux `xdg-open`); `/tmp` is Git Bash's own temp dir, fine for the
  scripts. All Python here runs in UTF-8 mode (`PYTHONUTF8=1` in `.claude/settings.json`) so emoji in
  captions and titles never break a write.
