---
name: video-tool-finder
description: "Pick the right open-source tool, library or agent skill for a video job before building it. A researched catalog of ~190 GitHub repos and skills (editing/cleanup, motion graphics, Claude video skills and style packs, audio/voice/captions, 3D, export) with what each does best, when to use it, when not to, license and install. Use when the user asks 'what should I use to make/edit X', 'is there a tool/skill for…', is planning a video, motion graphic, voiceover, caption, 3D or code-rendered film and the approach hasn't been chosen yet, or invokes '/video-tool-finder'. Also use it yourself before starting any video build where the stack hasn't been chosen."
metadata:
  version: 1.2.0
  last_updated: 2026-11-22
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
| Video editor GUI (free, open-source) | Kdenlive | Shotcut, OpenShot |
| Reverse-engineer a video shot-by-shot | Rea-Video | `mograph-snatcher`, manual analysis |
| Code agent → video agent (hybrid workflow) | OpenFilm | HyperFrames, Remotion |
| Motion graphics in code, agent-driven | HyperFrames | Remotion, Motion Canvas |
| Product promo / launch film from screenshots | video-shotcraft | huashu-motion, Remotion |
| Pick a named visual style for a code film | lemo-opuscar | mg-styles-15, animate |
| Math / diagram explainer | Manim | animate (math style) |
| Data visualization / charts | D3 | Remotion + Recharts |
| Hand-drawn cartoon character animation | ClaudeAnimationBase | OpenToonz (manual) |
| Sketchy / hand-drawn look | Rough.js | canvas-sketch |
| Pixel-art effects | pixelfx | — |
| Interactive particles / confetti | tsParticles | mo.js |
| Fluid / liquid effects | WebGL Fluid Simulation | regl custom shaders |
| Shape morphing / interpolation | Flubber | GSAP MorphSVG |
| Typing animation | Typed.js | custom GSAP |
| Text split for per-character animation | Splitting | GSAP SplitText |
| Gradient animations | Granim.js | CSS, GSAP |
| Image hover distortion | hover-effect | custom shaders |
| 3D tilt effect on hover | vanilla-tilt.js | CSS transforms |
| Flip clock / counter | Flip | custom canvas |
| Hand-drawn annotations | Rough Notation | Rough.js custom |
| Find the right name for a motion move | motion-prompt | `animation-vocabulary` skill |
| Teach agents motion design principles | Motion Design Skill | Impeccable |
| Catch AI design slop | Unslop | Impeccable |
| Review design quality | Impeccable | manual review |
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
| Audio waveform visualization | wavesurfer.js | canvas-sketch |
| Voiceover, free and quick | edge-tts | Piper, Kokoro (local) |
| Voiceover, high quality local / cloning | Chatterbox | Qwen3-TTS, CosyVoice (multilingual) |
| Voiceover, SFX, music via API | ElevenLabs Skills | elevenlabs MCP |
| Clean up / mix audio by hand | Audacity | `level-audio` skill |
| Remove background noise from voice | DeepFilterNet | ElevenLabs voice-isolator (paid) |
| 2D mouth animation from audio | Rhubarb Lip Sync | manual animation |
| 3D scene or product render | Blender + Blender MCP | Three.js |
| AI assets in Blender | Scenario Blender Plugin | Blender MCP |
| Rigged human for 3D | MPFB2 | — |
| Motion capture from a webcam | FreeMoCap | — |
| 3D in a browser-coded film | Three.js | — |
| Particle effects in Three.js | three.quarks | PointsMaterial |
| Physics in React Three Fiber | react-three-rapier | cannon-es |
| Postprocessing in React Three Fiber | react-postprocessing | raw three postprocessing |
| 3D text rendering in Three.js | Troika | TextGeometry |
| Camera controls in Three.js | camera-controls | OrbitControls |
| Thick lines in Three.js | MeshLine | fat lines |
| GPU physics / simulations | Taichi | gpu-io |
| Custom shaders library | LYGIA | ShaderToy snippets |
| Timeline/tween animation in HTML | GSAP | Anime.js, Motion |
| Bursts, shape effects | mo.js | GSAP |
| Play After Effects animations | Lottie (lottie-web) | — |
| Visual keyframe editor for web animation | Theatre.js | Motion Canvas |
| 2D vector drawing/animation API | Two.js | SVG.js, Canvas directly |

## Catalog

Stars and dates are a snapshot from 2026-11-22. "Agent-ready" means it ships a Claude Code skill or MCP.

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

**Kdenlive** — github.com/KDE/kdenlive · GPL-3.0 · 6.1k★ · desktop app
Best at: free open-source non-linear video editor with multi-track timeline, effects, transitions, color correction, and broad format support.
Use when: a human wants a full-featured FOSS video editor (Linux-first, runs on Mac/Windows). For agent-driven editing use Remotion/HyperFrames or the `davinci-resolve` MCP.

**Rea-Video** — github.com/JuneYaooo/rea-video · Apache-2.0 · 11k★ · `npx skills add juneyaooo/rea-video` · agent-ready
Best at: reverse-engineering any video shot by shot — filmed, AI-generated, or coded — identifying the technique and outputting a structured VIDEO.md breakdown with remake instructions.
Use when: analyzing reference videos to learn their production method before recreating the style. Pairs well with `mograph-snatcher` and `youtube-editing-style`.

**OpenFilm** — github.com/openfilm/openfilm · MIT · 8.5k★ · desktop app
Best at: turning any coding agent into a video agent — each shot becomes an editable web page (images/animations in HTML/CSS), timeline editor like CapCut, MP4 export.
Use when: a hybrid workflow where code generates shots but a human wants timeline control. 5,800+ stars but young; watch for stability.

**Shotcut** — github.com/mltframework/shotcut · GPL-3.0 · 12.4k★ · desktop app
Best at: open-source timeline editor to finish the cut — multi-track editing, filters, transitions.
Use when: a human wants a free, cross-platform NLE. Similar to Kdenlive. Not agent-drivable.

**Editly** — github.com/mifi/editly · MIT · 5.2k★ · `npm install -g editly`
Best at: turns a JSON/JS edit plan into a finished video with titles and transitions.
Use when: programmatic video assembly from a declarative config. Agent-friendly editing pipeline.

**FireRed-OpenStoryline** — github.com/FireRedTeam/FireRed-OpenStoryline · Apache-2.0 · 2.9k★ · clone repo
Best at: AI editing agent with natural-language instructions, reusable editing styles and Claude Code skills.
Use when: editorial decisions by natural language. Experimental but promising for agent-driven editing.

**OpenChatCut** — github.com/0xsline/OpenChatCut · MIT · 1.7k★ · clone repo + MCP setup
Best at: connects Claude Code/Codex to a real editing timeline through MCP — preview and approve edits.
Use when: agent proposes edits but a human reviews before committing. MCP bridge to timeline editors.

**OpenCut** — github.com/OpenCut-app/OpenCut · GPL-3.0 · 2.1k★ · desktop app
Best at: open-source CapCut-style timeline editor.
Use when: a free timeline editor with CapCut familiarity. Young project; for production use CapCut or Kdenlive.

**davinci-resolve-mcp** — github.com/samuelgursky/davinci-resolve-mcp · MIT · 1.3k★ · MCP server
Best at: Claude grades and edits inside DaVinci Resolve through MCP.
Use when: agent-driven work in Resolve. Complements video-editor-skills. Requires Resolve Studio.

**SpaceCut AI** — x.com/SpaceCutAI · app (no GitHub repo)
Best at: AI video editor app that learns an editor's style and makes animations in the same vibe.
Use when: style-consistent editing. App-only, not open source. Watch for availability.

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

**Penpot** — github.com/penpot/penpot · MPL-2.0 · 38k★ · web app + self-host
Best at: open-source Figma alternative with an MCP server so agents read your design files.
Use when: open-source design tool integration with agent workflows. Alternative to Figma for agent access.

**Storyboarder** — github.com/wonderunit/storyboarder · GPL-3.0 · 15.8k★ · desktop app
Best at: plan shots and build animatics before you animate — sketching, timing, camera angles.
Use when: pre-visualization and shot planning. Human-operated; exports timing for animation pipelines.

**Chrome DevTools MCP** — github.com/ChromeDevTools/chrome-devtools-mcp · BSD-3-Clause · 1.8k★ · MCP server
Best at: lets the agent see and record its own animation and fix mistakes before export.
Use when: agent reviews its own rendered output and iterates. Self-checking workflow.

### More from motion design guides

These 16 tools only appeared inside the long-form guides that the bookmarked posts link to, not in the posts' own lists:

**Playwright** — github.com/microsoft/playwright · Apache-2.0 · 76k★ · npm
Best at: drives a headless browser to capture each animation frame for rendering.
Use when: rendering animations to video — Remotion, HyperFrames and others use it under the hood.

**p5.js** — github.com/processing/p5.js · LGPL-2.1 · 23k★ · npm
Best at: creative-coding library used with p5.brush in ClaudeAnimationBase and other generative work.
Use when: Processing-style sketches in JavaScript. Foundation for many creative-coding animations.

**gsap-skills** — github.com/greensock/gsap-skills · MIT · 1.2k★ · `npx skills add greensock/gsap-skills` · agent-ready
Best at: GreenSock's official agent skills for GSAP UI motion and kinetic type.
Use when: teaching agents GSAP best practices. Official skills from the GSAP team.

**claude-video (/watch)** — github.com/bradautomates/claude-video · MIT · 980★ · `npx skills add bradautomates/claude-video` · agent-ready
Best at: /watch pulls frames and transcript from any video so the agent can study references.
Use when: agent needs to analyze reference videos. Extracts visual and textual content.

**Mediabunny** — github.com/Vanilagy/mediabunny · MIT · 890★ · npm
Best at: read, write and convert video in the browser, no ffmpeg.
Use when: video processing entirely in JavaScript/WASM. Good for web-only environments.

**ai-portals** — github.com/emollick/ai-portals · MIT · 1.1k★ · source study
Best at: source of Ethan Mollick's Portals — a multi-agent pipeline that built 471 Three.js worlds.
Use when: studying multi-agent 3D generation workflows. Framework example, not a ready tool.

**awesome-ai-motion** — github.com/guanmo-ai/awesome-ai-motion · CC BY 4.0 · 780★
Best at: prompt library for AI motion design.
Use when: finding proven prompts for motion graphics. Curated prompt collection.

**awesome-claude-video-skills** — github.com/zhuyansen/awesome-claude-video-skills · MIT · 1.5k★
Best at: 180 graded video skills for Claude.
Use when: browsing video skills by quality/category. Skill directory with ratings.

**Battle-of-Austerlitz-Film** — github.com/WinterArc21/Battle-of-Austerlitz-Film · MIT · 670★ · source study
Best at: source of a long-form code-made history film to study.
Use when: learning how to structure long narrative films in code. Reference implementation.

**blender-claymation-skill** — github.com/angrypenguinpng/blender-claymation-skill · MIT · 890★ · `npx skills add angrypenguinpng/blender-claymation-skill` · agent-ready
Best at: claymation look in Blender — a good example SKILL.md.
Use when: stop-motion/claymation aesthetic in Blender. Also a skill-writing reference.

**claude-animation-skill** — github.com/buildwithhanif/claude-animation-skill · MIT · 760★ · `npx skills add buildwithhanif/claude-animation-skill` · agent-ready
Best at: node-canvas animation skill for Claude.
Use when: canvas-based animation workflows. Alternative to browser-based approaches.

**earshot** — github.com/Leonxlnx/earshot · MIT · 1.1k★ · MCP server
Best at: MCP that lets the agent listen to, review and make sound (CPU only).
Use when: audio generation and analysis via MCP. CPU-based, no GPU needed.

**motion2code** — github.com/lovisdotio/motion2code · MIT · 1.3k★ · `npx skills add lovisdotio/motion2code` · agent-ready
Best at: rebuilds a reference motion clip as SVG + one GSAP timeline, checked frame by frame.
Use when: converting reference animations to code with frame-by-frame verification.

**opus-video-skills** — github.com/tuzhechen2005/opus-video-skills · MIT · 980★ · `npx skills add tuzhechen2005/opus-video-skills` · agent-ready
Best at: painted-animation and kinetic-type video skills.
Use when: specific painted or kinetic-type animation styles. Specialized skill set.

**Picsart** — picsart.com · web app (not GitHub)
Best at: image, video and audio models used as the asset/voice layer in animation studio workflows.
Use when: AI generation layer in multi-stack workflows. App-based, not open source.

**Whisper (OpenAI)** — github.com/openai/whisper · MIT · 85k★ · `pip install openai-whisper`
Best at: word timestamps for the caption layer — the original Whisper model.
Use when: basic transcription. faster-whisper, WhisperX and Stable-ts build on this.

### UI polish skills that help motion graphics

These 8 skills are pitched for UI rather than motion, but they also help motion graphics look less AI-generated:

**Taste Skill** — github.com/Leonxlnx/taste-skill · MIT · 2.1k★ · `npx skills add leonxlnx/taste-skill` · agent-ready
Best at: gives the agent design taste to avoid generic AI UI.
Use when: any visual work. Teaches aesthetic judgment.

**Emil Kowalski Design Engineering skills** — github.com/emilkowalski/skills · MIT · 1.9k★ · `npx skills add emilkowalski/skills` · agent-ready
Best at: design-engineering skills from Emil Kowalski, strong on UI animation feel.
Use when: micro-interactions and UI motion. High attention to animation detail.

**Vercel Web Design Guidelines** — github.com/vercel-labs/agent-skills · MIT · 2.3k★ · `npx skills add vercel-labs/agent-skills` · agent-ready
Best at: Vercel's web interface guidelines as agent skills.
Use when: clean, modern web design. Vercel's design system principles.

**Hallmark** — github.com/Nutlope/hallmark · MIT · 1.5k★ · `npx skills add nutlope/hallmark` · agent-ready
Best at: UI polish skill.
Use when: final polish pass on interfaces. Catches common UI mistakes.

**Make Interfaces Feel Better** — github.com/jakubkrehel/make-interfaces-feel-better · MIT · 1.3k★ · `npx skills add jakubkrehel/make-interfaces-feel-better` · agent-ready
Best at: micro-interaction and animation polish for interfaces.
Use when: UI motion feels stiff or mechanical. Adds life to interactions.

**Stageshow (Benji Taylor skills)** — github.com/benjitaylor/skills · MIT · 1.1k★ · `npx skills add benjitaylor/skills` · agent-ready
Best at: Benji Taylor's UI/design skills.
Use when: UI design and presentation polish. Focus on visual storytelling.

**Anti UI Slop (Uizze)** — uizze.com · skill site (not GitHub)
Best at: UI anti-slop skill.
Use when: catching AI-typical UI patterns. Web-based skill, not GitHub repo.

**ThinkUI** — thinkui.xyz · skill site (not GitHub)
Best at: UI design-quality skill.
Use when: design quality review. Web-based skill, not GitHub repo.

**D3** — github.com/d3/d3 · ISC · 114k★ · npm
Best at: data-driven documents — charts, graphs, network diagrams, maps, any visualization where data binds to SVG/Canvas/HTML.
Use when: the motion graphic is fundamentally about data, not just illustration. The industry standard for web data viz.

**Motion Canvas** — github.com/motion-canvas/motion-canvas · MIT · 20k★ · npm
Best at: programmatic animation with TypeScript, visual editor, real-time preview, tweening, and scenes. Code-first but with GUI controls.
Use when: you want code control with a visual timeline for tweaking. A middle ground between pure code (HyperFrames) and pure GUI (After Effects).

**Rough.js** — github.com/rough-stuff/rough · MIT · 21.4k★ · npm
Best at: creating graphics with a hand-drawn, sketchy appearance — lines, curves, fills, all with controllable "roughness."
Use when: the look needs to feel informal, human, or sketchbook-style. Works with Canvas, SVG, and most libraries.

**mo.js** — github.com/mojs/mojs · MIT · 18.9k★ · npm
Best at: burst animations, shape effects, timeline control, and declarative motion — the "pop" library for UI.
Use when: celebrating moments (success, level-up, confetti), transitions, or UI flourishes. Complements GSAP (GSAP for timelines, mo.js for bursts).

**PixiJS** — github.com/pixijs/pixijs · MIT · 48.9k★ · npm
Best at: ultra-fast 2D WebGL rendering with sprites, filters, blend modes, containers. The engine under many web games.
Use when: rendering hundreds of moving objects or when Canvas 2D is too slow. Not declarative like React — lower-level than Remotion.

**WebGL Fluid Simulation** — github.com/PavelDoGreat/WebGL-Fluid-Simulation · MIT · 16.9k★ · standalone JS file
Best at: beautiful, interactive fluid dynamics that run on GPU — works on mobile browsers.
Use when: abstract, organic backgrounds or interactive visualizations. Drop the script in any page. Touch/mouse reactive.

**Typed.js** — github.com/mattboldt/typed.js · no explicit license · 16.3k★ · npm
Best at: realistic typing animations with backspace, pauses, multiple strings, smart backspacing.
Use when: terminal-style reveals, typewriter effects, or chatbot-style text. Simple to integrate.

**Zdog** — github.com/metafizzy/zdog · no explicit license · 10.7k★ · npm
Best at: flat, round, designer-friendly pseudo-3D engine for Canvas/SVG — rotatable 3D shapes without WebGL complexity.
Use when: isometric or low-poly looks without Three.js overhead. Great for icons, diagrams, and playful 3D.

**SVG.js** — github.com/svgdotjs/svg.js · no explicit license · 11.9k★ · npm
Best at: lightweight SVG manipulation and animation — create, morph, animate SVG elements with a simple API.
Use when: vector animations, morphing shapes, or drawing without Canvas. Smaller and simpler than D3 for non-data work.

**Isotope** — github.com/metafizzy/isotope · no explicit license · 11.1k★ · npm
Best at: filtering, sorting, and animating grid layouts with masonry, fitRows, and other layouts.
Use when: animated product grids, portfolio galleries, or category filters with smooth transitions.

**Rough Notation** — github.com/rough-stuff/rough-notation · MIT · 9.8k★ · npm
Best at: animated hand-drawn annotations — underline, box, circle, highlight, strike-through, bracket.
Use when: emphasizing text or UI elements with a human, informal touch. Pairs well with Rough.js.

**tsParticles** — github.com/tsparticles/tsparticles · MIT · 9.1k★ · npm, framework wrappers
Best at: highly customizable particle effects, confetti, fireworks, snow, and animated backgrounds with React/Vue/Angular components.
Use when: celebration effects, ambient backgrounds, or interactive particle systems. Feature-rich but heavier than mo.js.

**EffectCraft** — github.com/storytold/effectcraft · Apache-2.0 · 9k★ · standalone app (Rust-based)
Best at: open-source motion graphics and compositing tool written in Rust — node-based, GPU-accelerated, aims to be an After Effects alternative.
Use when: a human wants a free compositing app. Very young (launched 2024); not agent-drivable yet. Watch this space.

**Flubber** — github.com/veltman/flubber · MIT · 7k★ · npm
Best at: smooth shape-to-shape interpolation (SVG path morphing) with multiple algorithms.
Use when: animating between two SVG shapes. Handles tricky cases like different point counts. Use with GSAP or D3 transitions.

**3D Force Graph** — github.com/vasturiano/3d-force-graph · MIT · 6.6k★ · npm
Best at: 3D network/graph visualizations with force-directed layouts, using Three.js under the hood.
Use when: visualizing connections, hierarchies, or networks in 3D. Interactive camera, customizable nodes/links.

**canvas-sketch** — github.com/mattdesl/canvas-sketch · MIT · 5.3k★ · npm
Best at: a framework for generative artwork — hot-reload, export frames/video, print sizes, CLI tools.
Use when: generative art, creative coding, or algorithm-driven visuals. Designed for artists; pairs with p5, Three.js, or raw Canvas.

**regl** — github.com/regl-project/regl · MIT · 5.6k★ · npm
Best at: functional WebGL — simpler, cleaner API than raw WebGL without the overhead of Three.js.
Use when: custom shaders, generative visuals, or data viz that needs GPU speed but not a full 3D engine.

**Granim.js** — github.com/sarcadass/Granim.js · MIT · 5.3k★ · npm
Best at: fluid, interactive gradient animations with color transitions and image blending.
Use when: animated gradient backgrounds, hero sections, or ambient color-shifting effects.

**Tweakpane** — github.com/cocopon/tweakpane · MIT · 4.7k★ · npm
Best at: compact GUI for fine-tuning parameters and monitoring value changes in real-time.
Use when: debugging generative animations, exposing controls for creative tweaking, or building live parameter UIs.

**vanilla-tilt.js** — github.com/micku7zu/vanilla-tilt.js · MIT · 4k★ · npm
Best at: smooth 3D tilt effect on hover — cards, images, or any element.
Use when: adding depth and interactivity to flat elements. Lightweight, no dependencies.

**Synfig** — github.com/synfig/synfig · GPL-3.0 · 2.5k★ · desktop app
Best at: open-source 2D vector animation with bones, tweening, and traditional animation tools.
Use when: a human animator wants a free 2D animation app. Not agent-driven; for agent cartoons use ClaudeAnimationBase.

**hover-effect** — github.com/robin-dela/hover-effect · MIT · 1.9k★ · npm
Best at: WebGL-powered image hover distortion effects (liquid, displacement maps).
Use when: interactive portfolio images, product showcases, or artistic image transitions.

**Splitting** — github.com/shshaw/splitting · MIT · 1.8k★ · npm
Best at: splitting elements by words, characters, lines, or children — each with CSS variables for staggered animations.
Use when: text reveals, per-character effects, or any staggered animation. Pairs perfectly with GSAP.

**jquery.ripples** — github.com/sirxemic/jquery.ripples · MIT · 1.1k★ · jQuery plugin
Best at: water ripple effect on any background using WebGL.
Use when: interactive water effects for hero sections or creative backgrounds. Requires jQuery.

**Flip** — github.com/pqina/flip · MIT · 1k★ · npm
Best at: classic flip clock/counter animation with customizable styles.
Use when: countdowns, timers, or retro number displays.

**Hydra** — github.com/hydra-synth/hydra · AGPL-3.0 · 2.8k★ · live coding environment
Best at: livecoding networked visuals in the browser with analog video synth-style functions.
Use when: VJ sets, experimental visuals, or live performances. Not for typical motion graphics — this is for live improvisation.

**Pixelorama** — github.com/Orama-Interactive/Pixelorama · MIT · 7.2k★ · desktop app
Best at: pixel art and sprite animation — drawing, layers, onion skinning, animation timeline.
Use when: retro/pixel-art animation or game sprites. Human-operated; not agent-driven. Pairs with pixelfx for code-generated pixel effects.

**twigl** — github.com/doxas/twigl · MIT · 1.1k★ · web app
Best at: live shader coding and GIF loops — write GLSL, see it instantly, export GIF.
Use when: creating shader-based animations or generative loops. Good for experimentation and sharing short shader sketches.

**ai-kit (Motion)** — github.com/motiondivision/ai-kit · no explicit license · 134★ · Cursor plugin
Best at: Cursor plugin for Motion (Framer Motion) with autocomplete, docs, and templates.
Use when: using Framer Motion in Cursor. Tiny plugin; mainly convenience. Already covered above under Claude skills.

### Claude video skills, style packs and prompt collections

**Remotion Skills** — github.com/remotion-dev/skills · 6.4k★ · `npx skills add remotion-dev/skills` · agent-ready
Best at: official Remotion know-how — create, markup, studio, render, maps, captions, docs lookup, upgrade.
Use when: building anything in Remotion. A `remotion-best-practices` skill is already loaded here.

**Impeccable** — github.com/pbakaus/impeccable · Apache-2.0 · 113k★ · `npx skills add pbakaus/impeccable` · agent-ready
Best at: the design vocabulary for coding agents — steer with "polish" and "bolder," review with "critique" and "audit," catch AI slop before it ships.
Use when: any visual output (UI, graphics, video) needs design feedback. Teaches agents what good design looks like. Extremely high adoption (113k stars).

**Unslop** — github.com/heydamir/unslop · CC BY 4.0 · 18.7k★ · `npx skills add heydamir/unslop` · agent-ready
Best at: turning vibecoded, AI-looking UI into a designed interface — fixing generic gradients, awkward spacing, and typical AI tells.
Use when: an agent-built UI or graphic looks "off." Complements Impeccable (Impeccable sets vocabulary, Unslop fixes slop).

**Motion Design Skill** — github.com/LottieFiles/motion-design-skill · MIT · 3.4k★ · `npx skills add lottiefiles/motion-design-skill` · agent-ready
Best at: universal motion design principles for AI agents — timing, easing, choreography, Disney animation principles adapted for UI.
Use when: any code-animated work. Teaches 12 principles of animation, anticipation, follow-through, squash/stretch, etc. Foundational.

**UI UX Pro Max** — github.com/nextlevelbuilder/ui-ux-pro-max-skill · MIT · 2.8k★ · `npx skills add nextlevelbuilder/ui-ux-pro-max-skill` · agent-ready
Best at: generating a full design system (pattern, palette, typography) from a brief before you animate.
Use when: you need a consistent visual language established before motion work begins. Sets up the design foundation.

**/anatomy** — skills.wheresryan.sh/anatomy · skill site (not GitHub)
Best at: drawing machines and systems as isometric figures.
Use when: technical explainers need isometric cutaways. Not a GitHub repo — skill accessed via URL.

**/anatomy-reveal** — typingmind.com/skills/annnguyentt-anatomy-reveal · skill site (not GitHub)
Best at: exploded product views plus a reveal MP4.
Use when: product showcases need dramatic reveals. Not a GitHub repo — skill accessed via URL.

**/hairline** — hairline.lucasmarkes.com/skills · skill site (not GitHub)
Best at: interactive line-figure animations from an idea or an SVG.
Use when: minimalist line animations or wireframe explainers. Not a GitHub repo — skill accessed via URL.

**anidoodle** — github.com/alexgreensh/anidoodle · MIT · 1.2k★ · clone repo
Best at: doodle-style animations and loops, all in code.
Use when: casual, hand-drawn animation style without actual drawing.

**awesome-claude-5-5-videos** — github.com/athemeroy/awesome-claude-5-5-videos · CC BY 4.0 · 1k★
Best at: archive of Claude-made animations with original sources, tools and workflows.
Use when: researching what's possible, finding workflow evidence, or studying proven approaches. Similar to awesome-opus5-5-videos.

**blender-skills** — github.com/EL4CTEO/blender-skills · MIT · 890★ · `npx skills add el4cteo/blender-skills` · agent-ready
Best at: 28 pro Blender techniques packaged as agent skills — a Claude Code plugin for Blender workflows.
Use when: Blender work beyond basic MCP commands. Complements Blender MCP with higher-level techniques.

**cinetic** — github.com/Leonxlnx/cinetic · MIT · 1.5k★ · clone repo
Best at: launch films straight from code.
Use when: product launch videos, promo films. Similar to huashu-motion and video-shotcraft.

**diagram-design** — github.com/cathrynlavery/diagram-design · MIT · 1.9k★ · `npx skills add cathrynlavery/diagram-design` · agent-ready
Best at: on-brand diagrams as one HTML+SVG file (animatable).
Use when: technical diagrams, flowcharts, system architecture visuals that need to match brand guidelines.

**FFmpeg Skill** — github.com/kajisho5/ffmpeg-skill · MIT · 1.3k★ · `npx skills add kajisho5/ffmpeg-skill` · agent-ready
Best at: 42 local editing tools for agents — cuts, captions, audio cleanup, reframing, overlays, exports.
Use when: agent-driven ffmpeg workflows. Packages common ffmpeg operations as agent-friendly skills.

**Graphed UGC Studio** — github.com/graphed-inc/marketing-skills/tree/main/skills/ugc-studio · MIT · 980★ · skill in repo
Best at: open-source HeyGen alternative — talking-head videos in bulk with motion graphics added.
Use when: UGC-style videos at scale without paid services.

**Herk Edit Kit** — github.com/nateherkai/herk-edit-kit · MIT · 1.1k★ · `npx skills add nateherkai/herk-edit-kit` · agent-ready
Best at: Nate Herk's Claude Code/Codex editing kit — dead-air cuts, transcript edits, captions and HyperFrames motion graphics.
Use when: editorial workflows combining cuts, transcripts and motion graphics.

**huashu-art-motion** — github.com/alchaincyf/huashu-art-motion · MIT · 1.8k★ · `npx skills add alchaincyf/huashu-art-motion` · agent-ready
Best at: turns paintings into moving art in 35 art styles.
Use when: animating static art, museum piece presentations, or art-history content.

**Motion AI Kit** — github.com/motiondivision/ai-kit · no explicit license · 134★ · clone repo
Best at: Motion's official agent kit — CSS springs, motion best practices and motion audits.
Use when: using Framer Motion in agent work. Small Cursor plugin for Motion library.

**Motion Video Kit** — github.com/echris6/motion-video-kit · MIT · 2.3k★ · `npx skills add echris6/motion-video-kit` · agent-ready
Best at: Claude Code workflows for launch videos, animated product demos and motion graphics, with sound design and visual review.
Use when: end-to-end video production workflows from brief to finished film.

**motionmaxxing** — github.com/Tejashmakwana/motionmaxxing · MIT · 980★ · `npx skills add tejashmakwana/motionmaxxing` · agent-ready
Best at: turns AI-slop motion into designer-level motion.
Use when: polishing agent-generated animations. Complements Unslop and Impeccable for motion work.

**REA (Reverse Engineer Anything)** — github.com/morluto/rea · Apache-2.0 · 2.1k★ · clone repo
Best at: the 'reverse anything' repo that Rea-Video and HyperFrames' reverse-any-video build on.
Use when: understanding the foundation of reverse-engineering tools. Framework/library rather than a ready skill.

**reanimate** — github.com/NiazMorshed2007/reanimate · MIT · 1.4k★ · `npx skills add niazmorshed2007/reanimate` · agent-ready
Best at: rebuilds any animation you see, frame by frame.
Use when: copying reference animations precisely. Similar to Rea-Video but focused on animation recreation.

**Scenario Skills + MCP** — github.com/scenario-labs/skills · MIT · 1.8k★ · `npx skills add scenario-labs/skills` · agent-ready
Best at: Scenario's agent skills including scenario-motion-loops, kinetic film and caption studio — powers the 80 Motion Loops collection.
Use when: working with Scenario's AI image/video generation in agent workflows. Includes MCP server.

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

**wavesurfer.js** — github.com/katspaugh/wavesurfer.js · BSD-3-Clause · 10.5k★ · npm
Best at: audio waveform player with interactive waveforms, regions, markers, and peaks.
Use when: visualizing audio for editing UIs, podcast timelines, or music players. Renders to Canvas or Web Audio API.

**Piper** — github.com/OHF-Voice/piper1-gpl · GPL-3.0 · 6.3k★ · `pip install piper-tts`
Best at: fast, local neural text-to-speech engine with many voices and languages.
Use when: quick, offline voiceovers without API costs. Quality is good but not quite Chatterbox/Qwen3-TTS level.

**DeepFilterNet** — github.com/Rikorose/DeepFilterNet · no explicit license · 5.1k★ · Python, GPU helps
Best at: noise suppression using deep filtering — cleans up background noise from voice recordings.
Use when: cleaning noisy recordings before transcription or voiceover use. Alternative to ElevenLabs voice-isolator (paid).

**Rhubarb Lip Sync** — github.com/DanielSWolf/rhubarb-lip-sync · no explicit license · 2.8k★ · command-line tool
Best at: automatically creating 2D mouth animation from voice recordings — outputs phoneme timings for cartoon characters.
Use when: syncing a cartoon character's mouth to dialogue. Works with Spine, Moho, Adobe Animate, etc.

**Bark** — github.com/suno-ai/bark · MIT · 42.7k★ · `pip install bark`
Best at: generates voices and sound effects from text — multilingual, non-verbal sounds (laughs, sighs, music).
Use when: expressive narration with emotion or when you need sound effects generated from descriptions. CPU-friendly but slow.

**Pedalboard** — github.com/spotify/pedalboard · GPL-3.0 · 6.1k★ · `pip install pedalboard`
Best at: reverb, compression and audio effects — Spotify's audio processing library for Python.
Use when: programmatic audio processing, music production effects, or cleaning/mastering audio in code.

**Stable-ts** — github.com/jianfch/stable-ts · MIT · 2.4k★ · `pip install stable-ts`
Best at: Whisper subtitles with word-level timestamps (SRT/VTT/ASS) — improved timestamp stability.
Use when: Whisper timestamps aren't stable enough. Alternative to WhisperX for word-level timing.

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

**Motion (Framer Motion)** — github.com/motiondivision/motion · MIT · 35k★ · npm
Best at: declarative React/JS animation with springs, layout animations, gestures.
Use when: animating React UI for screen recordings or web. In Remotion, prefer Remotion's own `spring`/`interpolate` (frame-driven, deterministic).

**Two.js** — github.com/jonobr1/two.js · MIT · 8.7k★ · npm
Best at: one 2D drawing API that renders to SVG, Canvas or WebGL.
Use when: procedural 2D shapes/vector animation without picking a renderer up front.

**Taichi** — github.com/taichi-dev/taichi · Apache-2.0 · 28.5k★ · `pip install taichi`
Best at: productive, portable, high-performance GPU programming in Python — parallel computing, physics simulations, graphics.
Use when: custom physics, simulations, or compute-heavy visuals that need GPU acceleration. Powers many research projects.

**Troika** — github.com/protectwise/troika · MIT · 2k★ · npm
Best at: JavaScript framework for interactive 3D and 2D visualizations — text rendering in Three.js, WebGL UI, and layout tools.
Use when: rendering high-quality 3D text in Three.js (Troika's text renderer is excellent) or building 3D UIs.

**three.quarks** — github.com/Alchemist0823/three.quarks · MIT · 1.2k★ · npm
Best at: general-purpose particle system / VFX engine for Three.js — GPU-accelerated, behavior graphs.
Use when: fire, smoke, explosions, magic effects, weather in a Three.js scene. More advanced than basic PointsMaterial.

**react-three-rapier** — github.com/pmndrs/react-three-rapier · MIT · 1.7k★ · npm
Best at: Rapier physics in React Three Fiber — rigid bodies, collisions, joints, raycasting.
Use when: physics-driven 3D in React (falling objects, ragdolls, simulations). Fast and deterministic.

**react-postprocessing** — github.com/pmndrs/react-postprocessing · MIT · 1.7k★ · npm
Best at: postprocessing effects for react-three-fiber — bloom, depth of field, glitch, vignette, etc.
Use when: adding cinematic or stylized effects to React Three scenes. Declarative wrapper around three's postprocessing.

**gpu-io** — github.com/amandaghassaei/gpu-io · MIT · 1.5k★ · npm
Best at: GPU-accelerated computing library for physics simulations and GPGPU in the browser.
Use when: custom simulations (fluids, particles, physics) that need GPU speed. Lower-level than Taichi.

**Scenario Blender Plugin** — github.com/scenario-labs/blender-plugin · GPL-3.0 · 1.1k★ · Blender extension
Best at: AI images, video, 3D and PBR materials in Blender viewport, plus a local MCP server for agents. Blender 5.0+ extension.
Use when: bringing AI generation into Blender workflows. Still young but integrates AI models directly into Blender.

**camera-controls** — github.com/yomotsu/camera-controls · MIT · 2.5k★ · npm
Best at: camera control for Three.js — similar to OrbitControls but supports smooth transitions, more features, and better API.
Use when: interactive 3D camera work in Three.js that needs smooth animations between views.

**MeshLine** — github.com/pmndrs/meshline · MIT · 385★ · npm
Best at: mesh replacement for THREE.Line — renders lines with actual geometry so they can have thickness and advanced materials.
Use when: thick lines, glowing lines, or textured lines in Three.js. Standard Line is always 1px; MeshLine gives control.

**LYGIA** — github.com/patriciogonzalezvivo/lygia · no explicit license · 3.5k★ · shader library
Best at: granular, multi-language shader library (GLSL, HLSL, Metal, WGSL, WEGL, CUDA) for performance and flexibility.
Use when: writing custom shaders and want reusable functions (noise, colors, lighting, etc.). Like a standard library for shaders.

**Babylon.js** — github.com/BabylonJS/Babylon.js · Apache-2.0 · 25.8k★ · npm
Best at: real-time 3D rendering engine — powerful alternative to Three.js with built-in physics, PBR, and XR support.
Use when: complex 3D scenes, games, or when Three.js doesn't fit. Steeper learning curve but more complete out of the box.

**cables.gl** — github.com/cables-gl/cables_electron · MIT · 1.2k★ · desktop app
Best at: node-based visual scene building — patch together nodes for generative visuals and 3D without code.
Use when: visual artists want to build 3D/generative work without writing code. Not agent-driven.

**Drei** — github.com/pmndrs/drei · MIT · 10.3k★ · npm
Best at: ready-made React Three Fiber helpers — cameras, controls, loaders, effects, abstractions.
Use when: using React Three Fiber and want pre-built components. Saves boilerplate.

**Spark** — github.com/sparkjsdev/spark · MIT · 890★ · npm
Best at: Gaussian splat rendering for Three.js — real-time 3D Gaussian Splatting viewer.
Use when: displaying 3DGS captures in the browser. Cutting-edge technique for photorealistic 3D.

**SPlisHSPlasH** — github.com/InteractiveComputerGraphics/SPlisHSPlasH · MIT · 2.3k★ · C++ library
Best at: fluid, foam and splash simulation — research-grade SPH fluid simulator.
Use when: physically accurate fluid simulations for research or high-end VFX. Requires C++ build.

**THREE-CustomShaderMaterial** — github.com/FarazzShaikh/THREE-CustomShaderMaterial · MIT · 1.6k★ · npm
Best at: custom shaders that keep Three.js lighting — extend Three.js materials without losing built-in features.
Use when: custom shaders need to work with Three.js lighting system. Bridges custom and standard materials.

**cannon-es** — github.com/pmndrs/cannon-es · MIT · 2.1k★ · npm
Best at: 3D physics and collisions — JavaScript physics engine for Three.js.
Use when: simpler physics than Rapier. Good for basic rigid-body physics.

**Effekseer** — github.com/effekseer/Effekseer · MIT · 1.9k★ · standalone + Three.js plugin
Best at: stylized particle effects — game-style VFX editor with Three.js runtime.
Use when: game-like explosions, magic effects, or stylized particles. Visual editor exports to code.

**img2threejs** — github.com/img2threejs/img2threejs · MIT · 1.2k★ · `npx skills add img2threejs/img2threejs` · agent-ready
Best at: rebuilds the object in a reference image as animation-ready Three.js code.
Use when: turning product photos or illustrations into 3D code. Experimental but useful for quick 3D from 2D.

**Jolt Physics** — github.com/jrouwe/JoltPhysics · MIT · 7.8k★ · C++ library with JS bindings
Best at: rigid and soft body physics and collisions — high-performance physics engine.
Use when: demanding physics simulations. More performant than Cannon but heavier integration.

**PlayCanvas** — github.com/playcanvas/engine · MIT · 10.1k★ · npm
Best at: real-time 3D worlds engine — game engine for the web with visual editor.
Use when: building 3D web games or interactive worlds. Alternative to Babylon.js.

**postprocessing (pmndrs)** — github.com/pmndrs/postprocessing · Zlib · 3.9k★ · npm
Best at: bloom, depth of field and grading for Three.js — vanilla Three.js postprocessing (non-React).
Use when: Three.js without React. For React Three Fiber use react-postprocessing instead.

**Sverchok** — github.com/nortikin/sverchok · GPL-3.0 · 3.1k★ · Blender addon
Best at: procedural geometry nodes for Blender — parametric modeling with node graphs.
Use when: algorithmic/generative 3D modeling in Blender. Requires Blender.

**Tesseract (Mirage)** — github.com/mirage-hq/Tesseract · MIT · 1.1k★ · agent skills + local engine
Best at: agent skills + local engine for editing, motion graphics and path-traced 3D scenes.
Use when: local 3D rendering with agent workflows. Young project; watch for development.

**three-gpu-pathtracer** — github.com/gkjohnson/three-gpu-pathtracer · MIT · 1.9k★ · npm
Best at: realistic path-traced lighting and reflections for Three.js — GPU-accelerated path tracing.
Use when: photorealistic rendering in Three.js. Slow but beautiful. Requires WebGL 2.

## Licensing quick flags

- **Non-commercial only**: video-editor-skills (CC BY-NC), story-studio (CC BY-NC-SA).
- **No license or unclear license (verify before commercial use)**: PDoomVideo, opus-video-prompts, Typed.js, Isotope, Zdog, SVG.js, ai-kit, Rhubarb Lip Sync, DeepFilterNet, LYGIA, Motion AI Kit.
- **Attribution required**: Unslop (CC BY 4.0), awesome-claude-5-5-videos (CC BY 4.0), awesome-ai-motion (CC BY 4.0).
- **Company license may be needed**: Remotion.
- **Copyleft (fine to use as a tool, careful if bundling code)**: FFmpeg (GPL builds), LosslessCut, color-matcher, ComfyUI, Blender, FreeMoCap (AGPL), Hydra (AGPL), Kdenlive (GPL), OpenToonz, Synfig (GPL), EffectCraft (copyleft if bundling), Scenario Blender Plugin (GPL), Piper (GPL), Audacity (GPL), Shotcut (GPL), OpenCut (GPL), Storyboarder (GPL), Pedalboard (GPL), Sverchok (GPL).
- **MPL-2.0 (weak copyleft)**: Penpot.
- **Paid API/credits**: Higgsfield Skills, ElevenLabs Skills, SpaceCut AI (app), Picsart (app).

## Output

Reply with a short recommendation, for example:

> **Use:** HyperFrames (already installed) for the overlays, librosa for the beat grid, Chatterbox for the voiceover.
> **Why:** agent-written HTML motion graphics; cuts land on beats; free local narration.
> **Skip:** Remotion (not needed for a one-off), ElevenLabs (paid, Chatterbox is enough).

Then offer to start the build with the chosen stack.
