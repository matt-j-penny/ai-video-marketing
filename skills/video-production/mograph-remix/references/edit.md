# Remix: edit a new video in the source's graphic style

Inputs:
- `RUN/STYLE.md`
- `RUN/templates/*`
- the user's new video, which can be on a different topic with a different script.

Output: the HyperFrames project `RUN/edit/`, which is the new footage with matching motion graphics.

## 1. Footage

```bash
npx hyperframes init RUN/edit --non-interactive --example=blank
mkdir -p RUN/edit/assets
```

- **Local file**: copy it to `RUN/edit/assets/footage.mp4`. If it isn't H.264 MP4, transcode it with `ffmpeg -i <in> -c:v libx264 -crf 18 -c:a aac`.
- **URL**: `yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" --merge-output-format mp4 -o RUN/edit/assets/footage.mp4 "<url>"`.

Probe the footage's duration, size and fps with `ffprobe`. If it isn't 16:9 1920×1080, tell the user. All templates are 1920×1080, so scale or letterbox the footage and say which you did.

## 2. Transcript

- With `CFG.transcriber = "deepgram"`, run `$TR RUN/edit/assets/footage.mp4 RUN/edit`. This writes `transcript.json` (word times) and `transcript.md` (timed sentences).
- If that exits with code 2, or the transcriber is `hyperframes`, run `npx hyperframes transcribe RUN/edit/assets/footage.mp4 -d RUN/edit --json` and read its word timings (`RUN/edit/transcript.json`) instead.

Read the whole transcript before planning, then run `$T catalog RUN/templates` to see what each template is for.

## 3. Plan

Write `RUN/edit/EDIT_PLAN.md` with one row per graphic:

| # | start–end | spoken trigger (quote) | moment | template or NEW | values |
|---|---|---|---|---|---|

How to plan:
- **Moments**: go through the transcript and tag the moments worth illustrating with a moment type from `$T moments`, such as emphasis, list, steps, stat or flow. Keep only the strongest ones that fit the pacing.
- **Matching**: for each moment, pick the template whose `useWhen` contains that moment, preferring the one where it is listed first. The content must fit the template's `limits`, and none of its `avoidWhen` may apply. Read `describe` to break ties.
- **Pacing**: match STYLE.md's graphics per minute, overlay-to-full-screen ratio and average on-screen time. Don't stack graphics on top of each other, and leave breathing room between them.
- **Timing**: start each graphic 0.1–0.3s before its trigger word, using `transcript.json`. Word-by-word reveals should land on the spoken words: set the template's stagger or per-word timings so word *n* appears when it is said, if the template supports that.
- **Reuse first**: use a template whose *kind* fits the moment and rewrite its values for the new content. Keep text lengths close to the defaults; if a line is much longer, shorten it or let the template wrap.
- **New graphics**: when a moment matters but no template's `useWhen` or `limits` fits it, design a NEW one in the style. Take colours, fonts, shapes and motion language from STYLE.md and author it as a new template under `RUN/templates/<name>/` following the contract, including its `template.json`. Verify it standalone, then save it to the library like the others.
- **Media slots**: photo, logo or icon slots need real images. If the user hasn't supplied any, keep the placeholders, list them in the plan, and offer to use frames from the footage (`ffmpeg -ss <t> -frames:v 1`) or images they provide.

Show the user the plan table and ask "build this, or what changes?". Wait for the answer.

## 4. Build

For each planned graphic `gNN`:

```bash
$T instance RUN/templates/<name> RUN/edit gNN --values '<json>'
```

Then write `RUN/edit/index.html`:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      html, body { margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #000; }
      #root { position: relative; width: 100%; height: 100%; }
      #a-roll { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
      .gfx { position: absolute; inset: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="<footage seconds>" data-width="1920" data-height="1080">
      <video id="a-roll" class="clip" src="assets/footage.mp4" playsinline data-has-audio="true"
             data-start="0" data-duration="<footage seconds>" data-track-index="0"></video>
      <!-- one per graphic; id and data-composition-id both = gNN -->
      <div id="g01" class="gfx" data-composition-id="g01" data-composition-src="compositions/g01.html"
           data-start="<s>" data-duration="<template duration>" data-track-index="1" data-width="1920" data-height="1080"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({ paused: true });
    </script>
  </body>
</html>
```

- **Full-screen graphics** cover the picture while the footage audio keeps playing underneath. That's intended.
- **Speaker picture-in-picture**: when a full-screen template has a speaker slot, place a muted, trimmed copy of the footage over that slot at the host level, and match the slot's rect and radius:
  ```html
  <video id="g03-pip" class="clip" src="assets/footage.mp4" muted playsinline
         data-start="<s>" data-media-start="<s>" data-duration="<d>" data-track-index="2"
         style="position:absolute; left:1478px; top:250px; width:410px; height:578px; border-radius:32px; object-fit:cover;"></video>
  ```
  The rect comes from the template's CSS.
- **Track order**: footage on 0, graphics on 1, picture-in-picture on 2. Never let two graphics on the same track overlap in time.
- **Slot length**: a slot longer than the template holds its last frame. Lengthen a template's hold only by giving it a duration variable, never by guessing.

## 5. Verify

```bash
cd RUN/edit && npx hyperframes lint . && npx hyperframes check .
npx hyperframes snapshot --at <mid-point of every graphic>
```

- Read the contact sheet. Each graphic should show its new values, sit where the plan says, keep clear of the speaker's face for overlays, and look like it belongs to the STYLE.md language.
- Fix layout, overflow and collision failures.
- Contrast failures that come from source palettes are acceptable; note them.

## 6. Preview and render

```bash
cd RUN/edit && npx hyperframes preview --background
```

Give the user the preview URL and ask "render now, or what changes?". Render only after a yes:

```bash
cd RUN/edit && npx hyperframes render --output renders/edit.mp4
```

Check `npx hyperframes render --help` for flags before running if unsure. Stop the preview afterwards with `npx hyperframes preview --stop`.
