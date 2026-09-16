---
name: capcut-ai-generate
description: "Generate an AI image or video via Kie.ai and place it into a CapCut draft as an overlay. Use when the user wants an AI-generated image/video clip (b-roll, a cutaway, a graphic element, a background) added to a CapCut project. Handles the async submit/poll pattern Kie.ai's API uses, and hands the downloaded result to the bridge's add-overlay command."
metadata:
  version: 1.0.0
  last_updated: 2026-09-15
---

# CapCut AI Generate (Kie.ai)

Submits a generation job to Kie.ai, polls it to completion, downloads the result, and places it into a CapCut draft via the bridge. Kie.ai is a marketplace of many underlying models (image and video) behind one common async job API — this skill covers that common API; the exact `input` fields differ per model and must be checked per model before calling (see step 1).

## Freshness Check

Compare `last_updated` to today. Kie.ai's model catalog changes often — if this file is more than 2 weeks old, treat the example model names/params below as illustrative only and re-check the model's own page at `docs.kie.ai/market/<vendor>/<model>` before calling. Then continue.

## Before Starting

1. `KIE_API_KEY` set — check `~/.claude/settings.json`'s `env` block; if missing, tell the user to add one from https://kie.ai/api-key rather than guessing at a key.
2. What's being generated — image or video — and the prompt/brief.
3. Which draft this is going into, and roughly where on the timeline (`--at`) and how long it should sit on screen.
4. Which model — if the user doesn't care, pick a reasonable default (a current general-purpose image or text-to-video model from https://kie.ai/market) and say which one was used.

## The API shape

Base: `https://api.kie.ai/api/v1`. Auth: `Authorization: Bearer ${KIE_API_KEY}` on every request.

**Submit** — `POST /jobs/createTask`
```json
{ "model": "<model-id>", "input": { "...model-specific fields..." } }
```
→ `{ "code": 200, "msg": "success", "data": { "taskId": "task_..." } }`

**Poll** — `GET /jobs/recordInfo?taskId=<taskId>`
→
```json
{ "code": 200, "msg": "success", "data": {
  "taskId": "...", "state": "success",
  "resultJson": "{\"resultUrls\":[\"https://.../file.mp4\"]}",
  "failCode": "", "failMsg": "", "progress": 100
}}
```
`state` is one of `waiting`, `queuing`, `generating`, `success`, `fail`. On `success`, `resultJson` is a **JSON string** (parse it) whose `resultUrls[]` holds the output file URL(s). On `fail`, read `failMsg`.

Rate limit: up to 20 new `createTask` calls per 10s (HTTP 429 past that) — irrelevant for a single generation, matters if batching several.

## Workflow

### 1. Confirm the model's exact input schema

Model IDs and their input fields are model-specific and change as Kie.ai adds/updates models — don't assume the examples below still match. Check `https://kie.ai/market` for the current catalog and the specific model's `docs.kie.ai/market/<vendor>/<model>` page for its exact `input` object before submitting. Two illustrative examples as of this writing:

Image (`nano-banana-2` or similar text-to-image):
```json
{ "model": "google/nano-banana-2", "input": { "prompt": "...", "aspect_ratio": "9:16", "resolution": "1K", "output_format": "png" } }
```

Video (`kling-2.6/text-to-video`):
```json
{ "model": "kling-2.6/text-to-video", "input": { "prompt": "...", "aspect_ratio": "9:16", "duration": "5", "sound": false } }
```

### 2. Submit

```bash
curl -s -X POST "https://api.kie.ai/api/v1/jobs/createTask" \
  -H "Authorization: Bearer ${KIE_API_KEY}" -H "Content-Type: application/json" \
  -d '{"model":"<model-id>","input":{...}}' | tee task.json
```
Pull `data.taskId` out of the response.

### 3. Poll to completion

```bash
while true; do
  resp=$(curl -s "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=${TASK_ID}" \
    -H "Authorization: Bearer ${KIE_API_KEY}")
  state=$(echo "$resp" | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['state'])")
  [ "$state" = "success" ] && break
  [ "$state" = "fail" ] && { echo "$resp"; exit 1; }
  sleep 5
done
echo "$resp" | python3 -c "
import json,sys
d = json.load(sys.stdin)['data']
print(json.loads(d['resultJson'])['resultUrls'][0])
"
```
Video generation typically takes longer than image (poll on a longer interval, e.g. 10-15s, for video jobs — no point hammering it every second).

### 4. Download the result

```bash
curl -s -o generated.mp4 "<resultUrl>"   # or generated.png for an image
```

### 5. Place it into CapCut

The bridge's `add-overlay` expects **video** media (it probes fps/duration/audio via ffprobe). For a video result, use it directly:

```bash
uv run "${CLAUDE_SKILL_DIR}/../bridge/capcut-bridge.py" add-overlay <draft> generated.mp4 --at <s> --mute
```

For a still image, loop it into a short silent clip first (ffmpeg doesn't need Kie.ai's help for this — a generated PNG isn't itself a video):

```bash
ffmpeg -loop 1 -i generated.png -t <duration> -c:v hevc_videotoolbox -tag:v hvc1 -pix_fmt yuv420p generated.mp4
uv run "${CLAUDE_SKILL_DIR}/../bridge/capcut-bridge.py" add-overlay <draft> generated.mp4 --at <s> --dur <duration> --mute
```

Remember: raw footage/overlay media must be reachable for hardlinking — the bridge handles copying it under the draft's `Resources/`, but the source file itself should exist on local disk (already true once downloaded above).

## Common Mistakes

1. **Guessing a model's `input` schema instead of checking its docs page** — schemas vary per model and change over time.
2. **Forgetting `resultJson` is a JSON string, not a nested object** — parse it before reading `resultUrls`.
3. **Placing a raw image file with `add-overlay`** — it expects video; convert stills to a short clip first.
4. **Not muting an overlay that has its own audio track** when it's layered over footage that already has sound — pass `--mute` unless the generated clip's audio is actually wanted.
5. **Tight polling** — a 1-2s poll loop on a video job just wastes calls; space it out.

## Task-Specific Questions

1. Image or video, and what's the brief/prompt?
2. Which draft and roughly where on the timeline should this land?
3. Any model preference, or pick a reasonable current default?
