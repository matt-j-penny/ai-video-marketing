# Caption Style — your LOCKED preset (talking-head explainer captions)

The standard burn-in caption format for **short-form talking-head explainers** (Preset A).
Locked 2026-06-24 (`your-job` hook v5). Apply verbatim every time — this replaces any
generic HyperFrames caption treatment for this format.

**Render CLI re-validated on 0.7.92 (2026-08-04), pin moved off 0.7.3.** The look is unchanged: a
real preset build (canonical `your-job` transcript, 14 chunks, 18.34s) rendered
`--format png-sequence` on both CLIs comes back identical over every in-duration frame except
**11 pixels total on 2 frames**, one scanline of glyph antialiasing (max delta 45/255, 0.0003% of
the frame). `lint` is clean on both, and 0.7.92's stricter `check` passes outright: 0 layout issues
across 9 samples, 0 motion errors, 14/14 contrast checks WCAG AA. The one real behaviour change is a
**fix**: 0.7.3 rendered the final tail frame BLACK (a 1-frame flash, visible as a blink where Reels
and TikTok autoloop), and 0.7.92 holds the last video frame instead (0.7.90, "resolve the true final
playable frame for held-tail media"). Re-validate the same way before moving this pin again.

Builder: [`presets/captions/build.py`](captions/build.py) · Corrections: [`presets/caption-corrections.json`](caption-corrections.json)

---

## 🔒 THE LOOK — locked

- **Font:** Coolvetica Regular (`assets/fonts/Coolvetica-Rg.otf`, @font-face'd into the hf project).
- **Box:** solid black `#000`, radius `14px`, padding `14px 24px`. The box **never animates** — hard cut on/off.
- **Text:** white `#fff`, `49px`, letter-spacing `0.5px`, natural case.
- **Position:** dead-centered both axes — vertical center `y960` (exact frame middle / graphics-face seam), horizontally centered.
- **Box sizing:** **pre-sized to the full phrase** and held that size — it does NOT grow word-by-word.
- **Animation = words only:** each word pops in (opacity + 6px rise, 0.13s) on its **own word-level timestamp**. On-beat karaoke; the box just sits there and the words appear onto it.
- **Phrasing:** 2–4 words per box, broken on clause/sentence punctuation.

## 🔒 THE TIMING RULE — this is the lock

**Always build captions from the canonical transcribe-once transcript:**
`projects/<job>/outputs/<job>.transcript.json`

That file is WhisperX large-v3 word timings remapped through `cuts.json` — it is the SAME timeline as the
audio that ships, so captions are on-beat **with zero manual nudging**.

- **NEVER** time captions off an ad-hoc/subset transcript (e.g. a `hook.transcript.json`). That is exactly
  what caused the back-half drift on v1–v4: a stale subset had dropped "it works." and compressed the tail,
  so later captions slid in early. The canonical transcript has every word at its true time.
- **Caption over the render that SHIPS** (the final cut or the graphics render of it). Same audio → same
  timeline → guaranteed sync. Verify once with `ffmpeg silencedetect` if you ever suspect drift: the audio's
  silences must line up with the transcript's word gaps.

## 🔧 AUTO-FIX mis-transcribed words

The builder runs every word through [`caption-corrections.json`](caption-corrections.json) before captioning
(caption display text only — the source transcript is never touched):
- **`auto`** — silent whole-word fixes: `clod/claud/clawed → Claude`, casing like `anthropic → Anthropic`,
  `chatgpt → ChatGPT`, `ai → AI`, `mcp → MCP`, etc.
- **`flag`** — ambiguous words (`cloud`, `school`) the builder PRINTS so you eyeball them in context that run.
  When a flagged word IS a fix for that video (e.g. "my **school** community" = your **YourBrand**), drop a
  `corrections.local.json` next to `build.py` (`{"auto": {"school": "YourBrand"}}`) — job-local, so the shared map stays conservative.
- **Grow the file** whenever a new mistake shows up. The build log lists every fix it made + every flag to check.

---

## ▶️ Per-job workflow (step 5 — captions)

1. `mkdir -p projects/<job>/hf-captions/assets/fonts` and copy in `package.json`, `hyperframes.json`,
   `Coolvetica-Rg.otf`, and `presets/captions/build.py`. (Durable under the job folder — regenerable scratch,
   but don't author it in `/tmp`; macOS clears it.)
2. Copy the **shipping render** (final cut / graphics render) into `assets/captions-bg.mp4`.
3. In `build.py` set the 3 per-job lines: `JOB`, (TRANSCRIPT auto-derives), `BG`, `HOOK_END_T`
   (`None` = whole video; a number previews just the hook).
4. `python3 build.py` → writes `index.html`. Read the log: confirm the chunk list, apply any `⚠ REVIEW` flags,
   note the printed `COMP_DUR` (the bg must be ≥ this).
5. `npx hyperframes@0.7.92 lint` → `npx hyperframes@0.7.92 render --quality standard --fps 30 -o projects/<job>/outputs/<job>.final.mp4`.
   Keep `outputs/<job>.mp4` as the clean base the builder reads from — don't overwrite it, or a re-run captions an already-captioned video.

Result is an overlay pass: video copied as the background, caption track composited on top. The caption box
lives on the seam (y960), inside the short-form safe box (y200→1620).

## Knobs (only if asked to tweak)

`FONT_SIZE` · `UPPERCASE` (→ ALL CAPS) · `BOX_COLOR`/`BOX_RADIUS`/`BOX_PAD` · `MAX_WORDS` (phrase length) ·
`WORD_FADE`/`WORD_RISE` (pop feel) · `REVEAL` (`word` = on-beat karaoke, `phrase` = whole phrase at once).
