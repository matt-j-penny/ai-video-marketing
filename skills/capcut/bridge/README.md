# CapCut Bridge Kit

CapCut has no API. This kit drives it two other ways: editing its draft files
directly on disk, and clicking its real UI through the macOS accessibility
tree. macOS only, needs the CapCut desktop app and `uv` (`brew install uv`).

Run any command with:

```bash
uv run capcut-bridge.py <command> ...
```

The script's `# /// script` header declares its two dependencies
(`pyobjc-framework-ApplicationServices`, `pyobjc-framework-Quartz`) — `uv run`
installs them itself on first use, no setup step needed.

## The two lanes

**File lane** (structural builds) — CapCut drafts are plain JSON under
`~/Movies/CapCut/User Data/Projects/com.lveditor.draft/<name>/`. The bridge
writes/edits that JSON directly, which means CapCut must be **fully closed**
while it does — the app owns that folder and rewrites its own registry on
quit, clobbering anything written while it was open. The bridge handles this
itself: it quits CapCut if running, writes, then relaunches it.

**Live lane** (interactive) — with the editor open, the bridge finds elements
in the accessibility tree by their internal automation ID (CapCut's QML UI
exposes ByteDance's own test hooks — `PlayerPlayBtn`, `MTLSVideoP:<clip>`,
etc.) and clicks them with synthesized CGEvents. No quit/relaunch involved.
These IDs are undocumented test hooks, not a public contract — re-verify with
`dump` after a CapCut update.

## Commands

File lane (quits + relaunches the app around the write):
```
replay <job> [--name <draft>]            # EDL -> new draft, one clip per cut
add-overlay <draft> <mov> --at <s> [--layer N] [--dur <s>] [--src <s>] [--ri N] [--mute] [--force]
add-text <draft> "<text>" --at <s> [--dur <s>] [--ri N] [--force]
graphics <draft> <job>                   # place a job's whole graphics plan
transform <draft> [--track main|text|overlay] [--index N] [--scale S] [--x X] [--y Y] [--rotate R] [--opacity O]
remove <draft> [--track main|text|overlay] [--index N]
keyframe <draft> [--track ...] [--index N] --at <s> [--scale S] [--x X] [--y Y] [--rotate R] [--opacity O]
clear-keyframes <draft> [--track ...] [--index N]
ls                                       # drafts in the registry
```

Live lane (open editor, no restart):
```
open <draft> · launch · quit
seek <seconds> [--draft <name>]          # frame-exact, closed-loop
select <i> · split [seconds] · delete <i>
trim-left · trim-right · undo · redo · marker · zoomfit · save
play · playhead · clips · state          # state = JSON timeline snapshot
export [--to <dir>] [--timeout <s>]      # drive CapCut's export dialog, verify the file
shot [out.png]                           # window grab for QA
dump [needle] · click <name> · clickxy <x> <y> · key <combo>
```

Run with no arguments for this same list from the script itself.

## Hard rules (learned the hard way — don't relearn these)

- **CapCut must be fully quit while the bridge writes a draft.** It rewrites
  its own draft registry on quit; if it's still running, that rewrite clobbers
  any draft the bridge just wrote or edited. The bridge quits/relaunches
  around every file-lane write — don't call file-lane commands while
  bypassing that.
- **Raw footage must live under `~/Movies`.** CapCut's sandbox can only read
  that tree, so paths outside it show up as broken red "File not accessible"
  clips. The bridge handles this by hardlinking source media into the
  draft's own `Resources/` folder — never point it at footage elsewhere and
  expect it to just work.
- **Editing a draft CapCut has already opened requires wiping its `Timelines/`
  cache first**, or your edit is silently ignored. CapCut only re-imports
  `draft_info.json` when that native cache is absent — otherwise it trusts
  its own cached state over the file on disk. The bridge's `edit_draft`
  helper does this automatically.
- **Once a draft has been hand-edited in the app, only ADD to it** — use
  `add-overlay` / `add-text` / `graphics` / `transform`, never `replay`
  again. `replay` rebuilds the draft from scratch and wipes hand edits.
- **A text segment with `source_timerange: null` wedges CapCut's encoder
  mid-export.** CapCut's own save normalizes text segments to a null source
  range; if you re-import after wiping `Timelines/`, that null survives and
  breaks export. The bridge repairs every segment before writing.
- **The post-export "share to TikTok/YouTube" screen is modal and blocks the
  next operation.** `export` clears it automatically — never click through
  it by hand, it publishes.

## What's in this kit

- `capcut-bridge.py` — the bridge script.
- `capcut-templates/` — raw CapCut material stubs the bridge needs for
  `add-text`/`graphics`: text styling (`text-material.json`), the timeline
  segment shape (`text-segment.json`), and a sticker-style animation ref
  (`text-ref-material_animations.json`).
- `presets/tiktok-raw-style.md` — the caption/hook-card look these text
  templates implement (Inter Bold, no box, low under the face).
- `presets/captions-style.md` — the alternate centered explainer caption
  look (Coolvetica, white-on-black box).
- `assets/fonts/` — Coolvetica + Inter, the fonts both presets above assume
  are available locally.
- `INPUT-CONTRACT.md` — the shape of the two JSON files (`cuts.json`,
  `graphics-plan.json`) that `replay` and `graphics` read.

This kit is pulled from a larger video-editing pipeline. Everything above is
what the CapCut lane needs standalone; it doesn't include the rest of that
pipeline (transcription, rough-cut splicing, other app lanes).
