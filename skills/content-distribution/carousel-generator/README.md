# carousel-generator — setup

Turns a topic, trend, news item, or post into a polished Instagram carousel with a **hybrid engine**: an AI-generated cover image (Higgsfield / Nano Banana Pro) for the thumb-stopping slide 1, then a token-locked HTML/CSS design system for the body slides — crisp 1080×1350 PNG slides at 2x (2160×2700) plus a `caption.md` package. Claude writes the cover concept + slide copy and picks one theme/font combination; `cover.py` generates the cover, then a Playwright-driven headless Chromium browser screenshots the real HTML output (cover image + overlaid text + body slides) so it looks designed, not generated. Trigger phrases: "make a carousel", "instagram carousel", "ig carousel", "carousel generator", "turn this into a carousel", "slide deck for instagram", "4:5 slides", "design a carousel", "trend carousel", "news carousel", "post carousel".

## Scripts

All commands are run from the **project root** (the folder that contains `.claude/`), e.g. `node .claude/skills/carousel-generator/scripts/render.js ...`.

- `scripts/cover.py` — generates the AI cover image(s) via the Higgsfield CLI (Nano Banana Pro), downloads textless variants next to the manifest in `cover/`. Needs network access (in Claude Code, run its Bash call with the sandbox disabled).
- `scripts/render.js` — renders the deck: embeds images as base64, screenshots each slide, writes the caption + contact sheet beside the manifest.
- `scripts/library.js` — saveable template library (`list` / `new` / `save`) for repeatable decks. `new <template> <slug>` scaffolds `carousel/outputs/<slug>/carousel.json` (`--out PATH` puts it elsewhere).

## Install

Drop this folder at `<project>/.claude/skills/carousel-generator/`. The skill locates the project root (for `assets/face-refs/`) from that position, so keep it project-local.

When copying or zipping the folder for someone else, exclude `scripts/node_modules/`, `scripts/package-lock.json`, `__pycache__/`, and `.DS_Store`. Those regenerate on first run.

## Prerequisites

**1. Node.js (required).** The renderer is plain Node.js — no uv, no Python. Install via [nodejs.org](https://nodejs.org) or `brew install node` on macOS. Any current LTS (v18+) works.

**2. One-time bootstrap: `bash install.sh`.** This is THE install path. From the project root:

```bash
bash .claude/skills/carousel-generator/install.sh
```

It checks Node/Python, runs `npm install` in `scripts/` (Playwright 1.60.0 into `scripts/node_modules/`), downloads Playwright's Chromium (one-time, ~130 MB, into Playwright's cache: `~/Library/Caches/ms-playwright/` on macOS, `~/.cache/ms-playwright/` on Linux, `%LOCALAPPDATA%\ms-playwright\` on Windows), and reports whether the Higgsfield CLI is present. If `render.js` later errors with "Executable doesn't exist" (cache wiped), just re-run `install.sh`. Under the hood it is `npm install` + `node node_modules/playwright/cli.js install chromium` in `scripts/`; you don't need to run those by hand.

**3. Fonts (already bundled).** All five typefaces (Space Grotesk, Hanken Grotesk, Bricolage Grotesque, Fraunces, Anton) ship as TTF files in `assets/fonts/` and are embedded as base64 in the rendered HTML — no system fonts required, output is identical on any machine.

**4. Higgsfield CLI (required for AI covers).** The cover generator (`cover.py`) drives the Higgsfield CLI — Python 3 only, no extra packages. Run it as `python3 .claude/skills/carousel-generator/scripts/cover.py <manifest>` (`python` on Windows; `install.sh` prints the binary it found).

```bash
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
higgsfield auth login
```

There's no API key or env var — the CLI stores its own login session. Verify with `higgsfield account status` (exit 0 when authed). Each cover image costs ~2 credits. `cover.py` only asks `[y/N]` when a human runs it at a TTY; from Claude's non-interactive Bash it submits straight away (`--yes` forces that from a terminal, `--dry-run` prices without submitting). To use a person in the cover, drop reference photos in `assets/face-refs/` (in your project root) and set `"face_refs": true` in the manifest's `cover` block; if none are found it warns loudly and generates without a face anchor. If you'd rather skip AI covers entirely, omit `cover.py` and use a typographic cover (`"type": "cover"` for slide 1) — no Higgsfield needed.

**5. Voice and CTA context (optional but strongly recommended).** Claude uses these files to write copy in your voice and tie CTAs to your offer. These live in your project root, not inside the skill folder. Create them yourself:

- `voice-dna.md` — your speech patterns, openers, closers, slang. Claude pulls from this when writing slide copy.
- `backbone/offer.md` — your offer/funnel details (name, price, deliverables, positioning, comment keyword, and the "What is NOT sold" list) so the CTA slide links to the right thing and never pitches a retired offer. Prices are never hardcoded in the skill; they come from here.
- `backbone/messaging.md` holds the proof bank + positioning principle; `stat` slides use only exact figures from here.

If these files don't exist, Claude will still generate carousels but the copy will be generic.

## Output

Everything for one deck lives in one folder: the manifest at `carousel/outputs/<slug>/carousel.json` (project-root relative), cover variants from `cover.py` in `carousel/outputs/<slug>/cover/`, and `render.js` writes its results beside the manifest (or to `--out DIR` if you override it):

- `slide_01.png … slide_NN.png` — final slides at 2160×2700 (2x; Instagram downscales cleanly). Images (the AI cover, any `media` screenshots) are embedded as base64, so each PNG is fully self-contained.
- `caption.md` — hook, body, CTA, hashtags, and optional first-comment text
- `contact_sheet.png` — all slides in one grid for quick review, auto-opened on render in your default browser (macOS `open`, Linux `xdg-open`, Windows `cmd /c start`)
- `preview.html` — written during `--preview` runs; opens in your default browser to inspect the deck before committing to PNGs

Keeping the manifest next to the outputs means a deck can be re-previewed, re-copied, or saved as a template (`library.js save`) any time later.

## Posting

Carousels are posted by hand: upload the `slide_XX.png` set in the Instagram app and paste the caption block from `caption.md`. `auto-poster` is single-media only (one video or one image per post) and cannot publish a multi-slide carousel.
