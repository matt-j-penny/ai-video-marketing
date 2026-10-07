---
name: mograph-remix
description: >
  Give it a YouTube URL and it finds every motion graphic in the video, recreates each one as a
  reusable HyperFrames template, and learns the video's graphic style. Give it a new video too and
  it edits that video with motion graphics in the same style, even when the topic and script are
  completely different. Templates can be saved to a HyperFrames template library. Use when the
  user says "/mograph-remix", "steal the motion graphics style from <youtube url>", "edit my video
  with graphics like <youtube url>", "extract the motion graphics from this video", or gives a
  YouTube URL plus their own footage and wants matching graphics.
---

# mograph-remix

The pipeline runs: style source URL, then find the graphics, then templates and a style guide, then save them to the library. If the user gave a new video, it continues: edit the new video with graphics in that style.

```
SKILL = the folder containing this SKILL.md     (scripts live in $SKILL/scripts)
S     = uv run -q $SKILL/scripts/snatch.py      (download, scan, dense frames)
T     = uv run -q $SKILL/scripts/tpl.py         (template contract, instancing, library)
TR    = uv run -q $SKILL/scripts/transcribe.py  (Deepgram word timestamps)
CFG   = ~/.config/mograph-remix/config.json
RUN   = ./mograph-remix/<source-video-id>/      (in the current working directory)
```

## 0. Setup gate

Read `CFG`. If it does not exist, or the user asks to change setup, follow `references/setup.md` before doing anything else. That step checks the tools and asks where templates should be saved. If `CFG` exists, check that a configured library still passes `$T lib-check <path>`. If it fails, tell the user and re-run setup.

## 1. Work out the job

- **Style source** (required): a YouTube URL. If it is missing, ask for it.
- **Range**: the user may limit the scan, for example "only the first 2 minutes". Pass it on as `--until`.
- **New video** (optional): a local file path or a URL, the footage to edit. With it, the job is **remix** (sections 2–5). Without it, the job is **extract** (sections 2–3, then finish).

## 2. Extract the graphics

Follow `references/extract.md`. It produces:
- `RUN/segments.json`
- per-graphic `RUN/segments/<id>/analysis.md`
- one template per graphic in `RUN/templates/<name>/`, each written to `references/template-contract.md` and verified.

## 3. Style guide and saving

1. Write `RUN/STYLE.md` with the source's graphic language:
   - **Palette**: hex values with roles, such as background, ink, accent, chip and card.
   - **Type**: each font with its role, weight and size range, and how the fonts pair (for example "bold serif headline + handwritten accent").
   - **Shape language**: radii, shadows, strokes, textures and recurring backgrounds (for example "cream background + soft grey swoosh").
   - **Motion language**:
     - entrance types and their durations and eases
     - word-by-word or letter reveals
     - stagger values
     - exit style
     - whether graphics sit behind the subject
   - **Layout habits**: where overlays sit, how much of the frame they use, and full-screen versus overlay.
   - **Pacing**: graphics per minute over the scanned range, average on-screen time, and the ratio of overlay to full-screen graphics.
   - **Template index**: paste the output of `$T catalog RUN/templates`, which lists each template's `useWhen` moments, description and limits from its `template.json`.

   The edit step uses this file to build *new* graphics that feel like the source, so be concrete.
2. Save the templates according to `CFG.library.mode`:
   - **`library`**: for each template, run:
     ```bash
     $T lib-add <CFG.library.path> RUN/templates/<name> --meta '<json>'
     ```
     Fill the meta as follows:
     - `id`: `<name>-<source-video-id>`
     - `name`: `"MG: <Readable Name>"`
     - `desc`: one sentence ending "Recreated from <title> — <channel>."
     - `features`: a list of 3–5 short tags

     The duration, overlay or standalone mode, and when-to-use come from the template's `template.json`.

     Running it again with the same id replaces the old entry.
   - **`session`**: leave the templates in `RUN/templates/` and save nothing else.

For an **extract** job, finish here and go to section 5.

## 4. Remix: edit the new video

Follow `references/edit.md`: get the footage, transcribe it, plan the graphics, wait for the user to approve the plan, build, verify, then preview. Render only after an explicit yes.

## 5. Finish

Write `RUN/INDEX.md`. It lists:
- the source title and URL
- the templates in a table with id, source timecode as a `&t=` link, kind, variables, path, check status and library id
- for a remix, the edit project path and render path.

Tell the user, in at most four lines:
- how many graphics were found
- where the templates went: library path, or "this session only"
- for a remix, how to preview the edit (`cd RUN/edit && npx hyperframes preview`)
- what is left to do, such as placeholder photos to swap in.

`RUN/source.mp4` and `RUN/scan/frames/` are large. Offer to delete them, but never delete them without asking.

## Rules

- Recreate the **design**, never the source's content. Do not copy logos, faces, footage or photos. Placeholders go in `assets/`, exposed as variables.
- Recreate faithfully and do not reinterpret: layout, type, colour and motion timing should match the reference frames.
- Never render a template or the edit without the user saying so. Previews and snapshots are fine.
