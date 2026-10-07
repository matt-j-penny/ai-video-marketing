# Extract: find and recreate the motion graphics

## 1. Download

```bash
$S download "<youtube-url>" ./mograph-remix
```

The download goes into `./mograph-remix/<id>/` (this is `RUN`) and is capped at 1080p. `meta.json` holds the title, channel, duration and fps.

## 2. Sparse scan

```bash
$S scan RUN --every 2 [--until <seconds>]
```

This writes `scan/sheet-NN.jpg` files. Each sheet is a 5×4 grid of timestamped frames, one every 2s, so it covers 40s. For a video over 20 minutes use `--every 3`. Use `--every 1` only if the graphics are very short.

**Read every sheet.** A frame has a motion graphic when it contains designed, added-in-post elements:
- titles or kinetic text
- lower-thirds, chips or tags
- callout boxes
- numbers or counters
- charts
- icons or icon tiles
- logos or stings
- maps
- social or UI cards
- designed full-screen scenes, such as a photo collage on a designed background or numbered cards.

These do **not** count:
- plain burned-in subtitles
- raw b-roll or footage
- the talking head alone
- a static watermark.

Group the hits into segments:
- Pad each one by about 1s on each side and clamp it to the scan range.
- Merge segments that are less than 1s apart, unless they are clearly different graphics.
- A full-screen scene that keeps the same design system while its photos and words change is **one** segment. Its template is one beat, and the analysis lists the other beats.

Write `RUN/segments.json`:

```json
[{"id": "seg-01", "start": 12.0, "end": 17.5, "kind": "lower-third", "summary": "Name bar slides in from left, white on red"}]
```

Show the user a table of id, timecode, kind and summary, then continue without waiting. If no graphics are found, say so and stop.

## 3. Dense capture

```bash
$S dense RUN seg-01 <start> <end> --fps 6
```

This writes `segments/seg-01/clip.mp4`, `frames/` and labelled sheets. Use `--fps 10` for graphics under 2s, and `--fps 4` for segments over 6s.

Read every sheet, then refine the start and end to where the first element appears and where the last element is gone. If an edge hits the padding, re-run with a wider range.

To check a colour or detail closely, grab one full frame:

```bash
ffmpeg -v error -y -ss <t> -i RUN/source.mp4 -frames:v 1 /tmp/f.png
```

## 4. Analyze

Write `segments/<id>/analysis.md` with these sections:

- **What it is**: the category and its purpose. Say whether it is an overlay or full-screen.
- **Layout**: each element's position and size in px on a 1920×1080 frame, plus safe areas.
- **Style**: palette as hex, fonts (closest Google Font plus weight and size), radius, strokes, shadows, blur and texture.
- **Motion timeline**: one row per element, giving its start offset, property, from and to values, duration, ease feel and stagger. Get these from the frame-to-frame differences.
- **Hold and exit**: how long it holds and how it leaves.
- **Not reproducible**: anything a template can't do alone, such as a subject occluding the graphic (that needs a matte).
- **Variables**: what should be editable, usually text, numbers, colours, and photo or icon slots.

## 5. Build one template per segment

Name each template `<kind>` in kebab-case, for example `stacked-tags`. If two segments share a kind, add `-2`.

Write it to `references/template-contract.md`:
- Recreate it faithfully from `analysis.md` and the dense sheets.
- Use the source content as the defaults.
- Use placeholder SVGs for photos, logos and icons, written to `assets/`.

Write its `template.json` moment card. Base `useWhen` on what the speaker was *saying* when the graphic appeared in the source (to know that, transcribe the source once with `$TR RUN/source.mp4 RUN` and read `RUN/transcript.md` around the segment's timecode), and generalise it to the kind of moment it suits.

Verify it as that file describes. Make at most 2 repair passes against the reference frames, and do not render.

Build sequentially unless the user asked for parallel subagents.
