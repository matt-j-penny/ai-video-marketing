#!/usr/bin/env bash
# transcribe-url.sh — get a transcript for any video URL
# usage: transcribe-url.sh <url> [output_dir]
#
# fast path: if the URL is YouTube and auto-captions exist, pull the VTT
# directly (no audio download, no whisper — finishes in ~2s).
# fallback: download audio via yt-dlp + transcribe with faster-whisper.

set -euo pipefail

URL="${1:?usage: transcribe-url.sh <url> [output_dir]}"
OUTPUT_DIR="${2:-transcripts/url}"
MODEL="${WHISPER_MODEL:-small.en}"
# optional: YTDLP_COOKIES_BROWSER=chrome (or firefox, safari, ...) for login-walled URLs.
# Appended as --cookies-from-browser to both yt-dlp calls; unset = public content only.
COOKIES_BROWSER="${YTDLP_COOKIES_BROWSER:-}"

# system python for the caption parser (YouTube fast path). Windows installs
# ship `python`, not `python3`; probe once, use "$PY" below.
PY=python3; python3 -c '' >/dev/null 2>&1 || { PY=python; python -c '' >/dev/null 2>&1 || { echo "[error] python not found; run ./setup.sh from the project root" >&2; exit 1; }; }

WORK="$(mktemp -d /tmp/transcribe-url-XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

is_youtube=0
case "$URL" in
  *youtube.com*|*youtu.be*) is_youtube=1 ;;
esac

echo "[fetch] $URL" >&2

# pull metadata always; on YouTube also try to grab captions in the same call.
YTDLP_ARGS=(
  --skip-download
  --no-playlist
  --quiet --no-warnings
  --print-to-file "%(title)s" "$WORK/title.txt"
  --print-to-file "%(uploader)s" "$WORK/uploader.txt"
  --print-to-file "%(webpage_url)s" "$WORK/url.txt"
  --print-to-file "%(duration)s" "$WORK/duration.txt"
  --print-to-file "%(upload_date)s" "$WORK/upload_date.txt"
)
if [ "$is_youtube" = 1 ]; then
  YTDLP_ARGS+=(
    --write-subs --write-auto-sub
    --sub-lang en
    --sub-format vtt
    -o "$WORK/sub.%(ext)s"
  )
fi
if [ -n "$COOKIES_BROWSER" ]; then
  YTDLP_ARGS+=(--cookies-from-browser "$COOKIES_BROWSER")
fi
yt-dlp "${YTDLP_ARGS[@]}" "$URL" >&2

TITLE="$(cat "$WORK/title.txt" 2>/dev/null || echo untitled)"
UPLOADER="$(cat "$WORK/uploader.txt" 2>/dev/null || echo unknown)"
DURATION="$(cat "$WORK/duration.txt" 2>/dev/null || echo 0)"
UPLOAD_DATE="$(cat "$WORK/upload_date.txt" 2>/dev/null || echo "")"
CANONICAL_URL="$(cat "$WORK/url.txt" 2>/dev/null || echo "$URL")"

# build slug from title for the filename
SLUG="$(printf '%s' "$TITLE" \
  | tr '[:upper:]' '[:lower:]' \
  | tr -c 'a-z0-9' '-' \
  | sed -E 's/-+/-/g; s/^-//; s/-$//' \
  | cut -c1-60)"
[ -z "$SLUG" ] && SLUG="transcript"

TODAY="$(date +%Y-%m-%d)"
mkdir -p "$OUTPUT_DIR"
# resolve to an absolute path so the returned path is unambiguous regardless of cwd
OUTPUT_DIR="$(cd "$OUTPUT_DIR" && pwd)"
OUT_FILE="$OUTPUT_DIR/${SLUG}_${TODAY}.md"
# same title pulled again today: suffix _2, _3, ... instead of clobbering the earlier transcript
n=2
while [ -e "$OUT_FILE" ]; do
  OUT_FILE="$OUTPUT_DIR/${SLUG}_${TODAY}_${n}.md"
  n=$((n + 1))
done

# locate VTT (yt-dlp picks the actual extension/lang variant)
VTT_FILE=""
if [ "$is_youtube" = 1 ]; then
  VTT_FILE="$(find "$WORK" -maxdepth 1 -name 'sub*.vtt' | head -n1)"
fi

if [ -n "$VTT_FILE" ]; then
  echo "[captions] using $VTT_FILE" >&2
  "$PY" - "$VTT_FILE" "$OUT_FILE" "$TITLE" "$UPLOADER" "$CANONICAL_URL" "$DURATION" "$UPLOAD_DATE" <<'PY'
import re, sys

vtt_path, out_file, title, uploader, url, duration, upload_date = sys.argv[1:]

with open(vtt_path, encoding="utf-8") as f:
    raw = f.read()

# split into cues by blank line
blocks = re.split(r'\n\s*\n', raw)
cues = []  # (start_seconds, clean_text)
ts_re = re.compile(r'(?:(\d+):)?(\d+):(\d+(?:\.\d+)?)\s+-->')

for block in blocks:
    lines = [l for l in block.splitlines() if l.strip()]
    if not lines:
        continue
    ts_line = next((l for l in lines if ts_re.search(l)), None)
    if not ts_line:
        continue
    m = ts_re.search(ts_line)
    h = int(m.group(1) or 0)
    mm = int(m.group(2))
    ss = float(m.group(3))
    start = h * 3600 + mm * 60 + ss
    body = [l for l in lines if l != ts_line and not l.startswith(('WEBVTT', 'Kind:', 'Language:'))]
    # find the line with word-level timestamps (the "currently typing" line)
    active = next((l for l in body if re.search(r'<\d+:\d+:[\d.]+>', l) or '<c>' in l), None)
    if active is None and body:
        # plain srt-style sub (no rolling tags) — take the joined body
        active = ' '.join(body)
    if active is None:
        continue
    clean = re.sub(r'<[^>]+>', '', active).strip()
    if not clean:
        continue
    cues.append((start, clean))

# dedupe consecutive identical lines (rare but safe)
deduped = []
for start, text in cues:
    if deduped and deduped[-1][1] == text:
        continue
    deduped.append((start, text))

plain_lines = [text for _, text in deduped]
timed_lines = [f"`[{int(s//60):02d}:{int(s%60):02d}]` {text}" for s, text in deduped]
plain = " ".join(plain_lines).strip() or "(no captions)"

if upload_date and len(upload_date) == 8 and upload_date.isdigit():
    upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
elif not upload_date or upload_date == "NA":
    upload_date = "unknown"

try:
    d = float(duration)
    dur_str = f"{int(d // 60)}:{int(d % 60):02d}"
except (ValueError, TypeError):
    dur_str = "unknown"

md = f"""# {title}

- **Source:** {url}
- **Uploader:** {uploader}
- **Uploaded:** {upload_date}
- **Duration:** {dur_str}
- **Method:** YouTube captions (no transcription needed)

## Transcript

{plain}

## Timestamped

{chr(10).join(timed_lines) if timed_lines else "(no captions)"}
"""

with open(out_file, "w", encoding="utf-8") as f:
    f.write(md)

print(f"[captions] wrote {out_file}", file=sys.stderr)
PY
  echo "$OUT_FILE"
  exit 0
fi

# ---- fallback: download audio + run faster-whisper ----
echo "[fallback] no captions available, downloading audio for whisper" >&2
AUDIO_ARGS=(
  -x --audio-format mp3
  --no-playlist
  --quiet --no-warnings --progress
  -o "$WORK/audio.%(ext)s"
)
if [ -n "$COOKIES_BROWSER" ]; then
  AUDIO_ARGS+=(--cookies-from-browser "$COOKIES_BROWSER")
fi
yt-dlp "${AUDIO_ARGS[@]}" "$URL" >&2

AUDIO="$WORK/audio.mp3"
[ -f "$AUDIO" ] || { echo "[error] audio download failed" >&2; exit 1; }

# Persistent venv shared with ig-competitor-research: built once, reused every
# run (no per-run dep resolution). Same faster-whisper box both skills use.
VENV="${CONTENT_OS_WHISPER_VENV:-$HOME/.cache/content-os/whisper-venv}"
PYBIN="$VENV/bin/python"
[ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"   # Windows venv layout
# sentinel written only after a successful install — a half-built venv (install
# interrupted once) self-heals on the next run instead of wedging forever
if [ ! -e "$VENV/.deps-ok" ]; then
  echo "[transcribe] first-run: building faster-whisper venv at $VENV" >&2
  rm -rf "$VENV"
  uv venv "$VENV" --python 3.11 >&2
  PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
  uv pip install --python "$PYBIN" faster-whisper onnxruntime >&2
  touch "$VENV/.deps-ok"
fi
echo "[transcribe] model=$MODEL audio=$AUDIO" >&2

"$PYBIN" - "$AUDIO" "$OUT_FILE" "$TITLE" "$UPLOADER" "$CANONICAL_URL" "$DURATION" "$UPLOAD_DATE" "$MODEL" <<'PY'
import sys
from faster_whisper import WhisperModel

audio, out_file, title, uploader, url, duration, upload_date, model_name = sys.argv[1:]

model = WhisperModel(model_name, device="auto", compute_type="int8")
segments, info = model.transcribe(
    audio,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
)
plain_lines = []
timed_lines = []
for seg in segments:
    text = seg.text.strip()
    if not text:
        continue
    plain_lines.append(text)
    mm = int(seg.start // 60)
    ss = int(seg.start % 60)
    timed_lines.append(f"`[{mm:02d}:{ss:02d}]` {text}")

plain = " ".join(plain_lines).strip() or "(no speech detected)"

if upload_date and len(upload_date) == 8 and upload_date.isdigit():
    upload_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"
elif not upload_date or upload_date == "NA":
    upload_date = "unknown"

try:
    d = float(duration)
    dur_str = f"{int(d // 60)}:{int(d % 60):02d}"
except (ValueError, TypeError):
    dur_str = "unknown"

md = f"""# {title}

- **Source:** {url}
- **Uploader:** {uploader}
- **Uploaded:** {upload_date}
- **Duration:** {dur_str}
- **Detected language:** {info.language} (p={info.language_probability:.2f})
- **Model:** {model_name}

## Transcript

{plain}

## Timestamped

{chr(10).join(timed_lines) if timed_lines else "(no speech detected)"}
"""

with open(out_file, "w", encoding="utf-8") as f:
    f.write(md)

print(f"[transcribe] wrote {out_file}", file=sys.stderr)
PY

echo "$OUT_FILE"
