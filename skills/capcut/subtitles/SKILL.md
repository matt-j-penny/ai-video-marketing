---
name: capcut-subtitles
description: "Add subtitles/captions to a CapCut project — either as native CapCut text segments inside the draft, or as a burned-in overlay via the house ffmpeg/PIL or HyperFrames caption builders (often the better-looking result). Supports highlighting one keyword per line in a different font or colour. Use when the user wants captions or subtitles added to a CapCut project. Needs a word-level transcript (capcut-transcribe) and, if the video was rough-cut first, that cut's cuts.json to map timestamps onto the edited timeline."
metadata:
  version: 2.0.0
  last_updated: 2026-09-16
---

# CapCut Subtitles

Two ways to get captions onto a CapCut project — pick based on what the job needs, not a fixed rule:

- **Burn-in** (`bridge/presets/tiktok-raw/` or `bridge/presets/captions/`) — renders the caption look with PIL+ffmpeg or as a HyperFrames composition, then composites it onto the exported cut. This is the more mature, proven house pipeline (locked style specs, word-pop reveal, hook-card treatment) and **usually looks better** — default to this unless the user specifically wants captions to stay hand-editable inside CapCut.
- **Native CapCut** (`scripts/add_caption.py`) — places real text segments on CapCut's own text track, editable afterward like any other layer in the app. Use this when the captions need to be tweakable inside CapCut itself, or the project is staying entirely in CapCut with no external render step.

Both need word-level timestamps mapped onto the **edited** (post-cut) timeline first.

## Freshness Check

Compare `last_updated` to today. Warn if >2 weeks stale, then continue.

## Before Starting

1. The draft/project — if a rough cut exists, its `cuts.json`.
2. `transcript.json` (from `capcut-transcribe`) for word timings.
3. Which path: burn-in or native CapCut (ask if not obvious — see Task-Specific Questions).
4. Caption style: line length (default 3-5 words), base color/font, and whether a keyword should be highlighted in a different font/colour.

## Step 1 — Map word timestamps onto the edited timeline (both paths need this)

If a rough cut exists, its `cuts.json` segments were placed back-to-back with no gaps (`capcut-rough-cut` step 5). For a source-timeline timestamp `t`, walk the kept segments in order and accumulate:

```python
def to_edited(t, segments):
    cursor = 0.0
    for s in segments:
        if s["start"] <= t <= s["end"]:
            return cursor + (t - s["start"])
        cursor += s["end"] - s["start"]
    return None  # t falls inside a cut — word was removed
```

Any transcript word whose timestamp maps to `None` was cut — drop it. If there was no rough cut, source time == edited time.

Build a normalized word list from this — both builders below expect the same shape:
```json
{"words": [{"text": "word", "start": 1.23, "end": 1.41}, ...]}
```
(Deepgram's `punctuated_word` → `text`; everything else already lines up.)

## Path A — Burn-in (recommended default)

### A1. Export the cut from CapCut

```bash
uv run "${CLAUDE_SKILL_DIR}/../bridge/capcut-bridge.py" export <draft> --to <job_dir>/outputs
```
Rename the export to `<job_dir>/outputs/<job>.mp4` (`<job>` = the basename of `<job_dir>`) — both builders expect exactly that path.

### A2. Write the normalized transcript

Save the Step 1 word list to `<job_dir>/outputs/<job>.transcript.json`.

### A3a. TikTok/raw style — hook card + line captions, no animation

```bash
python3 "${CLAUDE_SKILL_DIR}/../bridge/presets/tiktok-raw/build.py" <job_dir> \
  --hook-text "your hook line" [--until 30]   # --until for a quick preview
```
Full look/knobs documented in [`bridge/presets/tiktok-raw-style.md`](../bridge/presets/tiktok-raw-style.md). No built-in keyword-color highlight — every caption word renders in one fixed color (`CAP_TEXT_COL`). To add a highlight here, the smallest patch is per-word color in the `d.text(...)` calls around line 152 of `build.py`, switching fill based on whether the word matches the keyword — not done by default, only add it if the user specifically wants this path AND a highlight.

### A3b. Centered explainer style — HyperFrames, word-by-word pop-in

Scaffold the HyperFrames project (use the `hyperframes-cli` skill for `init`, don't hand-write `package.json`/`hyperframes.json`), copy in `bridge/presets/captions/build.py`, `bridge/assets/fonts/Coolvetica-Rg.otf`, and the exported cut as `assets/captions-bg.mp4`. Edit the three per-job lines in `build.py` (`JOB`, `BG`, `HOOK_END_T`), then:
```bash
python3 build.py            # writes index.html
npx hyperframes lint
npx hyperframes render --quality standard --fps 30 -o <job_dir>/outputs/<job>.final.mp4
```
Full spec in [`bridge/presets/captions-style.md`](../bridge/presets/captions-style.md). This one already reveals each word on its own timestamp (karaoke-style pop), but all words share one `TEXT_COLOR` — no keyword-color highlight built in. Smallest patch point: wrap the matched word's `<span class="w">` (around line 130) in a second CSS class with its own `color`.

### A4. Auto-fix mis-transcribed words

Both builders run every word through `bridge/presets/caption-corrections.json` (`auto` = silent fixes, `flag` = printed for review) before rendering — check the printed flags, add brand/product names to a job-local `corrections.local.json` if needed.

## Path B — Native CapCut text track

```bash
uv run "${CLAUDE_SKILL_DIR}/scripts/add_caption.py" <draft> "the exact line text" \
  --at <edited-start-seconds> --dur <edited-duration-seconds> \
  --color "#FFFFFF" --font-size 15 \
  --highlight "keyword" --highlight-color "#FFD400" \
  --highlight-font "${CLAUDE_SKILL_DIR}/../bridge/assets/fonts/Inter-Black.otf"
```

This script (not the bridge's own `add-text`, which only supports one style spanning the whole string) builds a CapCut text material with **two style runs** — base color/font across the line, and a second run scoped to just the highlighted word's character range with its own color/font. That's the real CapCut mechanism: `content.styles[]` entries each carry their own `range` (character start/end) plus `fill`/`font`/`size`. Highlighting works out of the box here, unlike either burn-in builder.

Group words into 3-5 word lines first (same phrasing rule as the burn-in presets), each line's `--at`/`--dur` from its first/last word's edited timestamps. Pass `--words` with per-word `{"text","start","end"}` (seconds relative to the line's own start) for exact timing, or let it split evenly across `--dur`.

Spot-check with `open` → `seek` → `shot` afterward.

## Common Mistakes

1. **Captioning off source timestamps on a rough-cut draft** — always convert to edited-timeline time first (Step 1), on either path.
2. **Assuming either burn-in builder highlights a keyword by default** — neither does; only Path B does out of the box.
3. **Using the bridge's plain `add-text` for a highlighted line** (Path B) — it force-stretches one style over the whole string; use `scripts/add_caption.py` instead.
4. **Wrong job-folder layout for the burn-in builders** — they hardcode `<job_dir>/outputs/<job_dir_basename>.mp4` and `....transcript.json`; get the naming exactly right or they won't find their inputs.
5. **Captioning words that were cut** — check the source timestamp actually falls inside a kept span before placing it.
6. **Re-running `replay`** on a draft with native captions already placed — wipes them.

## Task-Specific Questions

1. Burn-in (better default look, exits CapCut as a flattened render) or native CapCut text (stays hand-editable in the app)? If not specified, default to burn-in.
2. If burn-in: TikTok/raw style (hook card + static line captions) or centered explainer style (HyperFrames word-pop)?
3. Any specific words per line that should be highlighted, or should highlighting be judgment-based (numbers, names, the punchline word)? Note if burn-in is chosen and highlighting matters, it needs the small patch noted above.
4. Was this draft built by `capcut-rough-cut`, or is it uncut raw footage?
