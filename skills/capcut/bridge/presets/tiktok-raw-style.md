<!-- ⚠️  BRAND VALUES BELOW ARE PLACEHOLDERS — replace with your own.
     Fill in brand-kit.md and tell Claude "apply my brand kit", or edit the values here directly. -->

# TikTok/Raw Style — your LOCKED preset (hook card + line captions)

The standard graphics + caption treatment for **short-form TikTok/raw talking-head** videos
(the "front hook card only, then raw" format). Locked 2026-06-24 (`your-job`).
Apply verbatim every time.

Two overlays, dead simple, **no animation**:
1. **HOOK CARD** — one static white box / black text, pinned top, shown only over the spoken hook line.
2. **CAPTIONS** — line-by-line, parked low under the face, **always on** for the whole video.

Builder: [`presets/tiktok-raw/build.py`](tiktok-raw/build.py) · Corrections: [`presets/caption-corrections.json`](caption-corrections.json)

Engine = PIL PNG overlays + ffmpeg `overlay` (enable-timing). This ffmpeg has **no** `drawtext`/`libass`,
and PIL gives exact control over the Inter weight + stroke + box — it's the house pattern.

---

## 🔒 THE LOOK — locked

**Hook card** (top)
- **Font:** Inter **Bold** (`assets/fonts/Inter-Bold.otf`).
- **Size:** `64px`, black text `#000` on a solid **white** box `#fff`.
- **Box:** radius `22px`, sized to the **actual ink extents** (not font metrics) + padding `32px` x / `20px` y —
  it hugs the text, never balloons. Max width `940px`, centered. No animation — hard cut on/off.
- **Position:** box top at `y250` (just under the 200px top safe band).
- **When:** only over the spoken hook — auto-ends on the first `larp`/`lark` word (or first sentence break),
  override with `--hook-end SECONDS`.
- **Copy:** styled, not necessarily verbatim. Lowercase-casual brand voice. Set with `--hook-text "..."`.

**Captions** (bottom)
- **Font:** Inter **Bold**.
- **Size:** `42px`. **Text:** white `#fff` with a `4px` **black stroke** (`stroke_fill`), **no box**.
- **Position:** horizontally centered, vertical center `y1500` — low, under the face, above the 300px bottom band.
- **Phrasing:** ~3–4 words per line (`MAX_WORDS=4` / `MAX_CHARS=20`), broken on clause/sentence punctuation.
- **Animation:** none. Each line is a hard cut and **holds until the next line begins** (no flicker, no gaps).
- **Always on:** captions run from the first word to the last, the whole video. The hook card just overlays
  on top during its window — it does NOT replace the captions underneath.

**Safe zones:** every key visual stays inside `y200 → y1620`. Hook card sits below 200; captions sit above 1620.

## 🔒 THE TIMING RULE — this is the lock

**Always build from the canonical transcribe-once transcript:** `projects/<job>/outputs/<job>.transcript.json`
(WhisperX large-v3 word timings remapped through `cuts.json` — the SAME timeline as the audio that ships, so
captions are on-beat with zero manual nudging). **Caption over the render that SHIPS** (the final cut). Never
re-transcribe; never time off an ad-hoc subset transcript.

## 🔧 AUTO-FIX mis-transcribed words

Every word runs through [`caption-corrections.json`](caption-corrections.json) (`auto` map) — add your brand and product-name fixes there — before captioning (display text only; the source transcript is never touched). The builder also **drops
sub-0.2s single-word slivers** (clip-boundary false-start tails like a clipped "what?"). Grow the corrections
file whenever a new mistake shows up.

---

## ▶️ Per-job workflow (steps 3 + 5 — hook card + captions)

Preconditions: the rough cut + derived transcript exist (`outputs/<job>.mp4` + `outputs/<job>.transcript.json`).

1. **Preview** the first 30s while you dial the hook copy:
   `python3 presets/tiktok-raw/build.py projects/<job> --until 30 --hook-text "your hook"`
   → writes `/tmp/video-editor/<job>/tiktok-raw/preview.mp4` and prints the caption sheet + detected `hook_end`.
2. **Final** — drop `--until`, render to the deliverable:
   `python3 presets/tiktok-raw/build.py projects/<job> --hook-text "your hook" --out projects/<job>/outputs/<job>.final.mp4`

The rough cut at `outputs/<job>.mp4` stays the clean base the builder reads from; the captioned deliverable is
`outputs/<job>.final.mp4`. (Don't overwrite the base, or a re-run would caption an already-captioned video.)

## Knobs (only if asked to tweak)

Captions: `CAP_SIZE` · `CAP_WEIGHT` (`Semibold`/`Regular`/…) · `CAP_STROKE` · `CAP_CENTER_Y` (height) ·
`CAP_MAX_WORDS`/`CAP_MAX_CHARS` (phrase length) · uppercase = map `.upper()` in `render_caption`.
Hook card: `--hook-text`, `--hook-end`, `HOOK_SIZE`/`HOOK_PAD_*`/`HOOK_RADIUS`/`HOOK_TOP_Y`/`HOOK_WEIGHT`.
