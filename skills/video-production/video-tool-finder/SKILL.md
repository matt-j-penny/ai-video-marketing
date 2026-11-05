---
name: video-tool-finder
description: "Pick the right open-source tool, library or agent skill for a video job before building it. A researched catalog of ~58 GitHub repos (editing/cleanup, motion graphics, Claude video skills and style packs, audio/voice/captions, 3D) with what each does best, when to use it, when not to, license and install. Use when the user asks 'what should I use to make/edit X', 'is there a tool/skill for…', is planning a video, motion graphic, voiceover, caption, 3D or code-rendered film and the approach isn't decided yet, or invokes '/video-tool-finder'. Also use it yourself before starting any video build where the stack hasn't been chosen."
metadata:
  version: 1.0.0
  last_updated: 2026-11-05
---

# Video Tool Finder

You choose the stack for a video job. Read the job, match it against the catalog below, and recommend the fewest tools that get it done. Recommending nothing new is a valid answer when an already-installed skill or plain ffmpeg covers it.

## Freshness Check

Compare `last_updated` above to today's date. If more than 4 weeks have passed, tell the user the catalog may be stale (these repos move fast) and offer to re-check star counts and READMEs with `gh api repos/<owner>/<repo>`, then continue.

## How to pick

1. **Name the job in one line**: input (raw footage, script, topic, URL, audio) → output (MP4, overlay, captions, voiceover, CapCut/Resolve project, 3D scene) → look (talking head, motion graphics, cartoon, 3D, pixel, documentary).
2. **Check this repo first.** If a skill in `ai-video-marketing` already does the job (see "Already in this repo"), use it and say so.
3. **Check what's installed** before recommending installs: `which ffmpeg yt-dlp auto-editor scenedetect`, `pip show <pkg>`, `ls ~/.claude/skills`, and the skills listed in the session.
4. **Match by job** using the quick table, then read the catalog entries for the candidates.
5. **Recommend 1–3 tools**, in order, each with one line on why and what it costs (local/free, API credits, license limits). Flag non-commercial licenses (CC BY-NC) when the user's work is commercial (client or brand videos are).
6. **If nothing fits**, say so and fall back to ffmpeg + HyperFrames/Remotion written from scratch.

Code-rendered films (Opus 5.5 style) all share one pipeline: a web page draws frame `t` (Canvas/SVG/WebGL/Three.js/p5), headless Chrome screenshots each frame, ffmpeg joins frames + audio. The style packs below are prompts and conventions on top of that pipeline, not separate engines.

## Already in this repo

| Job | Use |
|---|---|
| Transcribe a local file with word timings | `video-editing/transcribe` (Deepgram first) |
| Transcribe a URL | `video-analysis/transcribe-url` (yt-dlp + faster-whisper) |
| Cut dead air and bad takes | `video-editing/rough-cut` (beats Auto-Editor when takes, not just silence, must go) |
| Even out narration loudness | `video-editing/level-audio` |
| Raw talking head → finished graphics edit | `video-production/full-edit` (Remotion) or `capcut/full-edit` |
| Topic → faceless video | `capcut/faceless-video` |
| Copy another video's motion-graphics style | `video-production/mograph-snatcher`, `mograph-remix` |
| Script/video → storyboard → Remotion render | `video-production/storyboard` |
| CapCut subtitles, zooms, beat detection | `capcut/subtitles`, `capcut/zoom-highlights`, `capcut/beat-detector` |

## Quick pick by job

| Job | First choice | Alternatives |
|---|---|---|
| Cut silence only, fast | Auto-Editor | ffmpeg `silencedetect` |
| Find shot changes / split into shots | PySceneDetect | ffmpeg `select='gt(scene,0.4)'` |
| Trim/merge without quality loss (by hand) | LosslessCut | ffmpeg `-c copy` |
| Stabilize shaky footage | ffmpeg `vidstabdetect`/`vidstabtransform` (vid.stab) | — |
| Match color across shots | color-matcher | ffmpeg `lut3d` with a made LUT |
| Cut out a subject / remove background | rembg | Higgsfield/Topview remove-background (paid) |
| Smooth slow-mo / raise frame rate | RIFE | ffmpeg `minterpolate` (worse) |
| Upscale or restore old/low-res footage | Real-ESRGAN | Topview/Higgsfield upscale (paid) |
| Download source footage | yt-dlp | — |
| Screen recording | OBS Studio | macOS screenshot tool |
| Motion graphics in code, agent-driven | HyperFrames | Remotion (+ Remotion Skills) |
| Product promo / launch film from screenshots | video-shotcraft | huashu-motion, Remotion |
| Pick a named visual style for a code film | lemo-opuscar | mg-styles-15, animate |
| Math / diagram explainer | Manim | animate (math style) |
| Hand-drawn cartoon character animation | ClaudeAnimationBase | OpenToonz (manual) |
| Pixel-art effects | pixelfx | — |
| Find the right name for a motion move | motion-prompt | `animation-vocabulary` skill |
| Prompt inspiration for code-rendered video | awesome-opus5-5-videos | opus-video-prompts, awesome-claude-5-5-videos |
| Music video with lyric sync | pdoom-video (study it) | PDoomVideo |
| AI-generated footage/images (not code) | Higgsfield Skills | ComfyUI (local) |
| First-pass edit inside DaVinci Resolve | video-editor-skills (non-commercial) | davinci-resolve MCP |
| Douyin-style knowledge short | vibe-knowledge-film | animate |
| Script → voiceover → images → JianYing draft | story-studio (non-commercial, Chinese) | `capcut/faceless-video` |
| Word-timed transcript, local, with speakers | WhisperX | faster-whisper; Deepgram via `transcribe` |
| Fix/sync subtitle files by hand | Subtitle Edit | — |
| Split music from vocals / stems | Demucs | ElevenLabs voice-isolator (paid) |
| Beat grid for cutting to music | librosa | `capcut/beat-detector` |
| Voiceover, free and quick | edge-tts | Kokoro (local) |
| Voiceover, high quality local / cloning | Chatterbox | Qwen3-TTS, CosyVoice (multilingual) |
| Voiceover, SFX, music via API | ElevenLabs Skills | elevenlabs MCP |
| Clean up / mix audio by hand | Audacity | `level-audio` skill |
| 3D scene or product render | Blender + Blender MCP | Three.js |
| Rigged human for 3D | MPFB2 | — |
| Motion capture from a webcam | FreeMoCap | — |
| 3D in a browser-coded film | Three.js | — |
| Timeline/tween animation in HTML | GSAP | Anime.js, Motion |
| Bursts, shape effects | mo.js | GSAP |
| Play After Effects animations | Lottie (lottie-web) | — |
| Visual keyframe editor for web animation | Theatre.js | — |
| 2D vector drawing/animation API | Two.js | Canvas directly |

## Catalog

Stars and dates are a snapshot from 2026-11-05. "Agent-ready" means it ships a Claude Code skill or MCP.

### Editing and cleanup

**Auto-Editor** — github.com/WyattBlue/auto-editor · Unlicense · 5.8k★ · `pip install auto-editor`
Best at: removing silence/dead air automatically by audio loudness or motion; exports straight to MP4 or to Premiere/Resolve/Final Cut timelines (XML) so cuts stay editable.
Use when: you just want pauses gone fast. Not when: you need bad takes or repeated lines removed (it can't read words) — use `rough-cut`.

**PySceneDetect** — github.com/Breakthrough/PySceneDetect · BSD-3 · 5.4k★ · `pip install scenedetect[opencv]`
Best at: finding every hard cut and fade in a video, outputting timecodes/CSV, splitting into shot files, saving a thumbnail per shot.
Use when: breaking down a reference video's pacing, extracting shots for B-roll, or prepping per-shot analysis (pairs well with `mograph-snatcher` and `youtube-editing-style`).

**LosslessCut** — github.com/mifi/lossless-cut · GPL-2.0 · 45.7k★ · desktop app (brew `--cask losslesscut`)
Best at: hand-trimming and merging huge files instantly with no re-encode, stream/track picking, chapter markers.
Use when: the user wants a GUI for quick trims. An agent should use `ffmpeg -c copy` instead (same idea, scriptable). Cuts snap to keyframes.

**vid.stab** — github.com/georgmartius/vid.stab · GPL-ish · 1k★ · built into most ffmpeg builds
Best at: two-pass stabilization of handheld footage (`vidstabdetect` then `vidstabtransform`).
Use when: shaky phone/handheld clips. Check `ffmpeg -filters | grep vidstab` first. Crops/zooms the edges.

**color-matcher** — github.com/hahnec/color-matcher · GPL-3.0 · 0.7k★ · `pip install color-matcher`
Best at: transferring the color of a reference image onto frames (histogram matching, MKL, Reinhard methods).
Use when: two cameras/shots don't match, or to match a reference look. Works on images, so for video run it on a frame and bake a LUT, or process frames. Not a creative grader.

**rembg** — github.com/danielgatis/rembg · MIT · 25k★ · `pip install "rembg[cli]"`
Best at: one-command AI background removal for images (u2net, BiRefNet, isnet models); batch folders.
Use when: cutouts of people/products for graphics, thumbnails, or per-frame mattes. Per-frame video mattes can flicker; for talking-head video use the `embedded-captions` matting flow or a video matting model.

**RIFE** — github.com/hzwer/ECCV2022-RIFE · MIT · 5.7k★ · Python + PyTorch, GPU helps
Best at: real-time frame interpolation — 2×/4×+ frame rates, smooth slow motion from normal footage.
Use when: smoothing slow-mo or upconverting 24/30 → 60fps. Artifacts on fast motion and occlusions. Repo is research code (last push 2025); practical wrappers like rife-ncnn-vulkan run easier on a Mac.

**Real-ESRGAN** — github.com/xinntao/Real-ESRGAN · BSD-3 · 37k★ · Python or the portable `realesrgan-ncnn-vulkan` binary
Best at: 4× upscaling and cleaning low-res/compressed images and video frames; anime model available.
Use when: upscaling old clips, screenshots or AI images for 4K. Not maintained since 2024 but stable. Can over-smooth faces and text.

**FFmpeg** — github.com/FFmpeg/FFmpeg · LGPL/GPL · 66k★ · `brew install ffmpeg`
Best at: everything underneath — convert, cut, concat, scale, overlay, burn subtitles, loudnorm, silence/scene detection, encode. Every other pipeline here ends in it.
Use when: always the default before adding any tool.

**yt-dlp** — github.com/yt-dlp/yt-dlp · Unlicense · 205k★ · `brew install yt-dlp`
Best at: downloading video/audio/subtitles/metadata from YouTube and ~1,800 sites, format selection, section downloads (`--download-sections`).
Use when: grabbing reference or source footage. Respect copyright: reference/analysis is fine, republishing others' footage isn't.

**OBS Studio** — github.com/obsproject/obs-studio · GPL-2.0 · 79k★ · desktop app
Best at: screen + camera recording and live streaming with scenes and sources.
Use when: the user needs to record a screen demo or tutorial. Human-operated; not something an agent drives.

### Motion graphics and animation

**Remotion** — github.com/remotion-dev/remotion · Remotion license (free for individuals/small teams, paid company license) · 71k★ · `npx create-video@latest`
Best at: React-coded videos with props/data, Studio preview, captions, maps, server/Lambda rendering at scale. The repo's `full-edit` and `storyboard` skills use it.
Use when: data-driven or templated videos, reusable branded compositions, or anything already in the Remotion stack. Check the license for companies over 3 people.

**HyperFrames** — github.com/heygen-com/hyperframes · Apache-2.0 · 79k★ · `npx skills add heygen-com/hyperframes`
Best at: plain HTML + GSAP compositions rendered to video, built for agents; ~450 ready-made blocks (transitions, titles, captions, charts, maps); lint/preview/render CLI. The repo's `mograph-*` skills use it.
Use when: agent-written motion graphics, overlays and explainers without a React build. Usually the first choice for new motion graphics here. Agent-ready.

**Manim** — github.com/ManimCommunity/manim · MIT · 42k★ · `pip install manim` (needs LaTeX for equations)
Best at: precise math animation — equations, graphs, geometric transforms (3Blue1Brown look).
Use when: math, physics, algorithms, data structures. Not for brand/marketing motion graphics.

**Theatre.js** — github.com/theatre-js/theatre · Apache-2.0 · 13k★ · npm
Best at: a visual keyframe timeline/editor on top of web animation and Three.js.
Use when: a human wants to tweak timing by hand in a GUI. Inactive since 2024; prefer GSAP for agent work.

**Lottie (lottie-web)** — github.com/airbnb/lottie-web · MIT · 32k★ · npm
Best at: playing After Effects animations (exported as JSON via Bodymovin) on web/mobile.
Use when: the user has AE/LottieFiles animations to drop into a HyperFrames/Remotion composition (Remotion has `@remotion/lottie`). Not a creation tool.

**OpenToonz** — github.com/opentoonz/opentoonz · BSD-ish · 8k★ · desktop app
Best at: full traditional 2D animation (Studio Ghibli used its predecessor) — drawing, xsheets, compositing.
Use when: a human animator draws by hand. Not agent-drivable; for agent cartoons use ClaudeAnimationBase.

**GSAP** — github.com/greensock/GSAP · free standard license (now 100% free incl. plugins) · 30k★ · npm
Best at: timelines, eases, stagger, SplitText, MorphSVG, ScrollTrigger — the animation engine inside HyperFrames and most Opus code films.
Use when: any HTML/SVG motion. There's a `gsap` skill loaded in this setup.

**ComfyUI** — github.com/Comfy-Org/ComfyUI · GPL-3.0 · 145k★ · local app, GPU needed
Best at: node-graph workflows for local AI image/video generation (Flux, Wan, Hunyuan, etc.), ControlNet, upscaling.
Use when: the user has a capable GPU and wants local generation with fine control. On a Mac without a strong GPU, hosted Higgsfield/Topview is more practical.

### Claude video skills, style packs and prompt collections

**Remotion Skills** — github.com/remotion-dev/skills · 6.4k★ · `npx skills add remotion-dev/skills` · agent-ready
Best at: official Remotion know-how — create, markup, studio, render, maps, captions, docs lookup, upgrade.
Use when: building anything in Remotion. A `remotion-best-practices` skill is already loaded here.

**video-shotcraft** — github.com/Vincentwei1021/video-shotcraft · Apache-2.0 · 17k★ · `npx skills add Vincentwei1021/video-shotcraft` · agent-ready
Best at: product promo films from your real pages/screenshots in Remotion: 124 shot recipe cards / 150 shots, storyboard, beat-synced cut, sound design, per-frame checks; editable in its Motion Workbench; JianYing export. Sibling `video-talkcraft` locks motion to a narration.
Use when: SaaS/app/product promos and launch videos. Best-in-list for this.

**lemo-opuscar** — github.com/lemomo-ai/lemo-opuscar · MIT · 12.6k★ · `claude plugin marketplace add lemomo-ai/lemo-opuscar` · agent-ready
Best at: 66+ named film styles (watercolor, metro map, chalkboard, LiDAR survey, documentary/evidence styles from real data), each a style prompt + demo film; director/technique guides; storyboard option; save your own styles. Picture, music (sample libraries) and TTS narration all in code.
Use when: a narrative or explainer film where the look matters and you want a proven style. Tuned for Opus 5.5.

**mg-styles-15** — github.com/Vincentwei1021/mg-styles-15 · MIT · 3.1k★ · copy a prompt from `prompts/`
Best at: 15 motion-design styles (line boil, isometric, flat vector, 3D render, shape morph, sticker explainer, HUD, collage, glassmorphism, Bauhaus, synthwave, pixel, liquid, variety captions 9:16) with full prompts, source and a review rubric.
Use when: you need a reference prompt + source for a specific MG look, or a review rubric for a second pass.

**huashu-motion** — github.com/alchaincyf/huashu-motion · MIT · 2.4k★ · `npx skills add alchaincyf/huashu-motion` · agent-ready (Chinese README)
Best at: commercial launch films: reads the product, offers 3 directions, composes its own score (ABC notation + instrument samples, locally), SFX on every landing, and a browser editor where you click a frame to request a change to just that element.
Use when: launch/promo films where iterative click-to-fix revisions matter. Works with cheaper models too.

**animate** — github.com/cth9191/animate · MIT · 1.6k★ · Claude Code skill · agent-ready
Best at: short single-file procedural canvas videos with check-ins (story → look frames → storyboard → build) and measured delivery checks; 7 styles (cut paper, crosshatch, riso, sketchbook, math, pixel, isometric) or one matched from your references; beat-mapped music; shape-morph transitions.
Use when: short explainers/histories/stories where you want approval gates before rendering, or a custom style learned from references.

**pixelfx** — github.com/patch-gg/pixelfx · MIT · 5.2k★ · npm/clone · agent-ready
Best at: 244 code pixel-art effects (fire, explosions, magic, weather, UI, transitions, critters), recolorable, sprite-sheet export, plus a skill to make new ones.
Use when: retro/game-style videos, gamified overlays, pixel transitions.

**motion-prompt** — github.com/showheyohtaki/motion-prompt · MIT · 1.3k★ · gallery: showheyohtaki.github.io/motion-prompt
Best at: 192 named moves (motion-graphics moves, camera moves/transitions, UI components, landing-page effects, photo looks) each with a moving sample and an example prompt; multilingual.
Use when: you need the right term to ask for a move. Complements the `animation-vocabulary` skill.

**video-editor-skills** — github.com/appariciojunior/video-editor-skills · CC BY-NC 4.0 (no commercial use) · 0.4k★ · skills only, no code
Best at: first-pass YouTube/vlog edits in DaVinci Resolve Studio: transcript cuts, vlog pacing, B-roll by action, music/SFX + ducking, captions, Remotion brand overlays, Resolve API pitfalls, export settings.
Use when: the user edits in Resolve Studio. Read it for method; don't ship it in commercial work. The `davinci-resolve` MCP is connected here.

**vibe-knowledge-film** — github.com/HeyChengC/vibe-knowledge-film · MIT code, analysed examples copyrighted · 1.1k★ · Chinese
Best at: Douyin viral "knowledge" shorts in two styles ("Nocturne" for deep science, "Fable" for behaviour/psychology): subtitles, shot list, Canvas engine, auto SFX, 30s sample before the full film.
Use when: short educational explainers in that look. Needs Python + Playwright + Chrome + ffmpeg.

**story-studio** — github.com/konlu/story-studio · CC BY-NC-SA 4.0 (no commercial use) · 0.8k★ · Chinese
Best at: history/biography narration shorts: topic + hook library (370+ references), script, Doubao TTS or your own MP3, local timestamp alignment, 3 consistent image styles, editable JianYing Pro draft.
Use when: studying the pipeline. For English/commercial work use `capcut/faceless-video`.

**Higgsfield Skills** — github.com/higgsfield-ai/skills · MIT · 1.9k★ · `npx skills add higgsfield-ai/skills` · agent-ready, uses Higgsfield credits
Best at: AI generation across 30+ models (Veo, Kling, Seedance, Nano Banana, GPT Image), Soul ID face-consistent characters, product photoshoots, brand kits, Marketing Studio ads, faceless explainers, YouTube thumbnails, virality scoring.
Use when: the shot needs real-looking footage or images code can't draw. Several `higgsfield-*` skills are already loaded here.

**awesome-opus5-5-videos** — github.com/yihui-dev/awesome-opus5-5-videos · MIT · 13.7k★
Best at: 703 prompts behind viral Opus 5.5 code videos (motion graphics, explainers, 3D, games), each tagged by tech (Canvas, SVG+GSAP, GLSL, Three.js) with live remakes on Skillry.
Use when: looking for a proven prompt to adapt. Search `data/videos.json` by tech or category.

**awesome-claude-5-5-videos** — github.com/athemeroy/awesome-claude-5-5-videos · CC-BY-4.0 · 1k★
Best at: 424 source-linked Claude 5.5 video cases across Opus/Sonnet/Haiku/Fable, with research findings (e.g. ads lean motion-graphics/UI, games lean 3D) and production paths.
Use when: deciding which model/approach suits a video type, or finding workflow evidence.

**opus-video-prompts** — github.com/joeseesun/opus-video-prompts · 1k★ · Chinese
Best at: 18 full copy-ready prompts and 54 cases across 9 tech routes (Canvas, p5, Three.js, Remotion, Manim, Blender), plus writing tips. Notes code is weak at photoreal people — pair with a video model for that.
Use when: quick-start prompts, especially one-liners that produce launch films.

**pdoom-video** — github.com/mexicat/pdoom-video · MIT · 3.8k★
Best at: a reference build of a lyric music video: Demucs stems + CTC/Whisper forced alignment for word timings, beat/downbeat analysis, Three.js renderer with bloom/grain, scenes snapped to the beat grid, deterministic export.
Use when: building any lyric video or music-synced piece — copy its analysis pipeline.

**PDoomVideo** — github.com/JohnHeibel/PDoomVideo · no license (view only) · 2.8k★
Best at: a p5.js + p5.brush painted music video, with Opus's own STORYBOARD.md and ANIMATION_GUIDE.md used to brief parallel subagents.
Use when: studying multi-agent scene production. No license, so don't reuse the code; use ClaudeAnimationBase instead.

**ClaudeAnimationBase** — github.com/JohnHeibel/ClaudeAnimationBase · MIT · 2.6k★
Best at: hand-painted cartoon character animation in p5.js + p5.brush: Clawd character, 31 acted emotions, an animation guide (storyboard first, contact-sheet self-checks, transitions always).
Use when: character-driven cartoon shorts. Watercolor fills are slow without a GPU — ask for flat fills on a laptop.

### Audio, voice and captions

**WhisperX** — github.com/m-bain/whisperX · BSD-2 · 25k★ · `pip install whisperx`
Best at: Whisper + forced alignment for accurate word timestamps, plus speaker diarization (pyannote, needs a Hugging Face token).
Use when: local, offline word-timed transcripts with speaker labels. Default here is still Deepgram (`transcribe` skill).

**Subtitle Edit** — github.com/SubtitleEdit/subtitleedit · MIT · 15k★ · desktop app (Windows-first; runs on Mac via Mono/newer builds)
Best at: hand-editing, syncing, converting and spell-checking SRT/ASS/VTT files.
Use when: a human needs to fix subtitle timing by eye. Agents edit SRT directly.

**Demucs** — github.com/facebookresearch/demucs · MIT · 10k★ · `pip install demucs`
Best at: splitting music into vocals/drums/bass/other stems with high quality (htdemucs).
Use when: removing music under a voice, isolating vocals for lyric alignment, or remixing. No updates since 2024 but still the standard.

**librosa** — github.com/librosa/librosa · ISC · 8.8k★ · `pip install librosa`
Best at: beat/tempo tracking, onsets, loudness envelopes, spectral features.
Use when: cutting or animating to music beats; generating a beat grid JSON for a composition.

**Qwen3-TTS** — github.com/QwenLM/Qwen3-TTS · Apache-2.0 · 14k★ · Python, GPU preferred
Best at: expressive, streaming TTS with free-form voice design from a text description and voice cloning; strong Chinese/English.
Use when: local high-quality voiceovers or a designed voice without an API.

**CosyVoice** — github.com/QwenAudio/CosyVoice · Apache-2.0 · 24k★ · Python, GPU preferred
Best at: multilingual zero-shot voice cloning and cross-lingual voiceovers with training/deployment tooling.
Use when: voiceovers in many languages or dubbing your own voice into another language locally.

**edge-tts** — github.com/rany2/edge-tts · LGPL-3.0 · 12k★ · `pip install edge-tts`
Best at: free, instant Microsoft neural voices (hundreds, many languages) with word-boundary subtitle output.
Use when: quick drafts, scratch VO, or timed captions for free. Online service; not for premium final narration.

**Kokoro** — github.com/hexgrad/kokoro · Apache-2.0 · 9.9k★ · `pip install kokoro`
Best at: an 82M-parameter TTS that sounds natural and runs fast on CPU/Mac.
Use when: free, offline voiceovers of good quality. No cloning.

**Chatterbox** — github.com/resemble-ai/chatterbox · MIT · 28k★ · `pip install chatterbox-tts`
Best at: state-of-the-art open TTS with zero-shot voice cloning from a short clip and an emotion/exaggeration control; watermarked output.
Use when: best free local narration or cloning the user's own voice (with consent).

**faster-whisper** — github.com/SYSTRAN/faster-whisper · MIT · 26k★ · `pip install faster-whisper`
Best at: ~4× faster Whisper with less memory (CTranslate2), word timestamps, VAD.
Use when: local transcription; already used by `transcribe-url`.

**ElevenLabs Skills** — github.com/elevenlabs/skills · MIT · 0.5k★ · `npx skills add elevenlabs/skills` · agent-ready, paid API
Best at: official guidance for TTS, speech-to-text, sound effects, music, voice changer, voice isolator, dubbing, voice agents.
Use when: premium voiceover, SFX or music via API. The `elevenlabs` MCP is also connected here.

**Audacity** — github.com/audacity/audacity · GPL · 19k★ · desktop app
Best at: manual audio cleanup — noise reduction, EQ, compression, multitrack mixing.
Use when: a human is cleaning audio by ear. Agents should use ffmpeg filters / `level-audio`.

### 3D and scene tools

**Blender** — github.com/blender/blender · GPL · 22k★ · desktop app with Python API
Best at: modeling, rigging, animation, physics, Cycles/EEVEE rendering, compositing; scriptable headless (`blender -b -P script.py`).
Use when: photoreal or stylized 3D product shots, logos, scenes. mg-styles-15's 3D film used it.

**Blender MCP** — github.com/ahujasid/mcp-for-blender · MIT · 33k★ · `uvx mcp-for-blender setup` · agent-ready
Best at: letting Claude build, light and animate scenes inside a running Blender, plus asset pulls (Poly Haven, Sketchfab, Hyper3D).
Use when: agent-driven 3D. Installer edits MCP configs (keeps backups).

**MPFB2** — github.com/makehumancommunity/mpfb2 · GPL · 0.7k★ · Blender extension
Best at: generating rigged, customizable human characters inside Blender.
Use when: you need a person in a 3D scene to animate.

**FreeMoCap** — github.com/freemocap/freemocap · AGPL-3.0 · 11k★ · `pip install freemocap`
Best at: markerless motion capture from regular webcams (multi-camera for 3D), exports to Blender.
Use when: animating a character with real human movement. Needs the user to record themselves.

**Three.js** — github.com/mrdoob/three.js · MIT · 118k★ · npm
Best at: WebGL 3D in the browser — the 3D engine behind most code-rendered films (pdoom-video, many Opus demos).
Use when: 3D inside a HyperFrames/Remotion/Canvas composition (`@remotion/three` exists).

**Anime.js** — github.com/juliangarnier/anime · MIT · 74k★ · npm
Best at: lightweight CSS/SVG/DOM animation with timelines, stagger, SVG morph/draw.
Use when: a smaller alternative to GSAP. In HyperFrames, stay with GSAP.

**mo.js** — github.com/mojs/mojs · MIT · 19k★ · npm
Best at: bursts, shape swirls and eased "pop" effects for UI flourishes.
Use when: celebration bursts, click/impact accents in a motion graphic.

**Motion (Framer Motion)** — github.com/motiondivision/motion · MIT · 35k★ · npm
Best at: declarative React/JS animation with springs, layout animations, gestures.
Use when: animating React UI for screen recordings or web. In Remotion, prefer Remotion's own `spring`/`interpolate` (frame-driven, deterministic).

**Two.js** — github.com/jonobr1/two.js · MIT · 8.7k★ · npm
Best at: one 2D drawing API that renders to SVG, Canvas or WebGL.
Use when: procedural 2D shapes/vector animation without picking a renderer up front.

## Licensing quick flags

- **Non-commercial only**: video-editor-skills (CC BY-NC), story-studio (CC BY-NC-SA).
- **No license (view only)**: PDoomVideo, opus-video-prompts.
- **Company license may be needed**: Remotion.
- **Copyleft (fine to use as a tool, careful if bundling code)**: FFmpeg (GPL builds), LosslessCut, color-matcher, ComfyUI, Blender, FreeMoCap (AGPL).
- **Paid API/credits**: Higgsfield Skills, ElevenLabs Skills.

## Output

Reply with a short recommendation, for example:

> **Use:** HyperFrames (already installed) for the overlays, librosa for the beat grid, Chatterbox for the voiceover.
> **Why:** agent-written HTML motion graphics; cuts land on beats; free local narration.
> **Skip:** Remotion (not needed for a one-off), ElevenLabs (paid, Chatterbox is enough).

Then offer to start the build with the chosen stack.
