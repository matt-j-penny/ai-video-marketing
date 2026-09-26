# Default style guide

Every image prompt gets the **Prompt block** below appended, and each image after the first is generated with the previous image as a reference. Together these keep the whole video looking like one piece.

To use your own look: copy this file somewhere, edit the Prompt block, and set `style: /path/to/your-style.md` in `~/.claude/faceless-video-preferences.md`. Only the text under `## Prompt block` is used.

## Prompt block

Cinematic documentary still, photorealistic, shot on a 35mm lens with shallow depth of field. Moody, directional natural light with deep shadows and warm highlights. Muted, slightly desaturated colour grade with teal shadows and amber highlights, subtle film grain. Rich texture and detail. Single clear focal subject, uncluttered background. No text, no letters, no logos, no watermarks, no borders, no split panels.

## Notes

- Keep the block describing *look* only (lens, light, grade, texture). Subjects go in each shot's prompt.
- If one image drifts off-style, regenerate just that shot with `images <job> --redo N`; it re-references the previous shot.
