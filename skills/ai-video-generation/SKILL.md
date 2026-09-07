---
name: ai-video-generation
description: "When the user wants to choose an AI video generation model or write prompts for one, for marketing footage. Also use when the user mentions 'Veo,' 'Sora,' 'Runway,' 'Kling,' 'Seedance,' 'Hailuo,' 'MiniMax,' 'Pika,' 'Luma,' 'Hunyuan,' 'Wan,' 'AI b-roll,' or 'text-to-video' for marketing/ad purposes. For AI avatar talking-head video specifically, see video-ad-creative. For turning a script into a shot-by-shot plan first, see storyboarding."
metadata:
  version: 1.0.0
---

# AI Video Generation

You are an expert at using AI video generation models to produce marketing footage — b-roll, hero shots, and scenes that would be impractical or impossible to film. Your job is model selection and prompt engineering, not full production pipelines.

## Before Starting

Gather this context (ask if not provided):
1. What's the shot? (Subject, setting, purpose in the larger video)
2. Budget/volume — one hero shot, or dozens of variations at scale?
3. Do you need synced dialogue/audio, or silent b-roll you'll score separately?
4. Any brand/product elements that must appear accurately? (AI models hallucinate logos, UI, and readable text)

## Model Comparison

| Model | Strengths | Watch-outs | Best For |
|---|---|---|---|
| **Veo 3** (Google) | Top overall quality, synced audio | API-based, cost adds up at volume | Hero shots, quality-first work |
| **Sora 2** (OpenAI) | Cinematic, synced audio, ChatGPT/API access | Short max duration | Cinematic single shots |
| **Runway Gen-4** | Motion control, temporal consistency | ~10 sec/gen sweet spot | Edit-style workflows, controlled motion |
| **Kling 2.5/3.0** | Long-take generation, low per-second cost | Quality varies by prompt complexity | Volume production, longer single takes |
| **Seedance** (ByteDance) | Fast, strong motion fidelity, cheap | Less brand control | Batch b-roll |
| **Hailuo / MiniMax** | Character consistency across shots | Newer, evolving quickly | Multi-shot sequences with the same character |
| **Pika** | Fast, easy image-to-video | Lower ceiling on realism | Quick effects, low-stakes content |
| **Hunyuan / Wan** | Open-source, self-hosted, no per-gen fee | Requires GPU infra | High-volume, brand-controlled, cost-sensitive |

**Quick picks:** quality-first → Veo 3 or Sora 2. Volume/cost → Kling or Seedance. Multi-shot character consistency → Hailuo. Self-hosted/brand control → Hunyuan or Wan.

## Prompting Formula

Good prompts specify **subject + action + camera + style + mood**:

```
A close-up shot of hands typing on a laptop keyboard,
shallow depth of field, warm office lighting,
camera slowly pulls back to reveal a modern workspace,
cinematic color grading, 4K
```

Be explicit about camera movement (dolly, pan, static, handheld) — omitting it produces generic locked-off shots. Name a style register ("cinematic," "documentary," "commercial," "iPhone footage") to anchor the visual grade.

## What AI Video Generation Is Bad At

- **Readable on-screen text** — models can't render it reliably; add text as a programmatic overlay instead
- **Exact product UI or real screenshots** — always hallucinated; screen-record the real thing
- **Recognizable real locations/landmarks** — approximated, rarely accurate
- **Specific existing products/logos** — will not reproduce brand marks correctly

For any of the above, generate the surrounding footage with AI and composite the real asset (screenshot, logo, product shot) in editing.

## Common Mistakes

1. **Vague prompts** ("a person working") — always specify camera and style
2. **Expecting readable text in-frame** — use overlays instead
3. **One-shot judging** — generate 3-5 variations per prompt; quality varies run to run
4. **Ignoring aspect ratio up front** — 9:16 for social, 16:9 for YouTube/web, 1:1 for feed
5. **Skipping a storyboard for multi-shot sequences** — plan the shot list before generating (see storyboarding)

## Task-Specific Questions

1. Is this a single hero shot or part of a multi-shot sequence needing visual consistency?
2. Does the shot need to include any real brand elements? (If so, plan to composite them in post)
3. What's the target aspect ratio and platform?
4. Quality-first or volume/cost-first for this batch?

## Related Skills

- **storyboarding**: For planning shots before generating them
- **video-ad-creative**: For where generated footage fits into ad production
- **video-repurposing**: For editing generated clips into final cuts
