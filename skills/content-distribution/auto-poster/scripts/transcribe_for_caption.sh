#!/usr/bin/env bash
# Transcribe a video for post captions with faster-whisper.
#
# Uses the SAME persistent faster-whisper venv every other transcription skill in
# this repo uses (~/.cache/content-os/whisper-venv, built once by uv, sentinel-
# gated), so there is exactly one speech engine to install and one place it lives.
# Model defaults to tiny.en (~75 MB, fast, plenty for a caption). Override with
# AUTO_POSTER_WHISPER_MODEL=base.en / small.en for more accuracy at more time.
#
# First run on a machine: builds the venv (~200 MB) and downloads the model.
# Later runs: a 90-second reel transcribes in a few seconds on CPU.
#
# Usage: transcribe_for_caption.sh <local-video-path-or-direct-url> [output.txt]
#
# If output.txt is omitted, the transcript is written to a fresh mktemp file
# (mode 600, owned by this user) and its path is printed on stdout. Do NOT
# default to a shared fixed path like /tmp/something.txt: anyone with write
# access to /tmp could pre-seed it and inject content into your posts.

set -euo pipefail

VIDEO="${1:?usage: transcribe_for_caption.sh <local-video-path-or-direct-url> [output.txt]}"
OUT="${2:-}"

for t in ffmpeg uv; do
  command -v "$t" >/dev/null 2>&1 || { echo "[auto-poster] $t is not installed; run ./setup.sh (or ./check-setup.sh) from the project root" >&2; exit 1; }
done

# Session-scoped work dir (mode 700, this user only).
WORK="$(mktemp -d "${TMPDIR:-/tmp}/auto-poster.XXXXXXXX")"
chmod 700 "$WORK"
trap 'rm -rf "$WORK"' EXIT

# Output: caller's path, or a fresh private temp file that survives cleanup.
if [ -z "$OUT" ]; then
  OUT="$(mktemp "${TMPDIR:-/tmp}/auto-poster-transcript.XXXXXXXX")"   # mktemp = mode 600
fi

MODEL="${AUTO_POSTER_WHISPER_MODEL:-tiny.en}"
log() { printf '[auto-poster] %s\n' "$*" >&2; }

# Resolve input: download if URL, otherwise must be a local file.
INPUT="$VIDEO"
case "$VIDEO" in
  http://*|https://*)
    INPUT="$WORK/source.mp4"
    curl -L --fail --silent --show-error "$VIDEO" -o "$INPUT"
    ;;
esac
if [ ! -f "$INPUT" ]; then
  log "video not found: $INPUT"
  exit 1
fi

# 16 kHz mono wav: ~50x smaller than the source video, and what whisper wants.
AUDIO="$WORK/audio.wav"
ffmpeg -nostdin -y -loglevel error -i "$INPUT" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$AUDIO"

# Shared persistent venv (transcribe-url, ig-competitor-research, voice-corpus-builder,
# yt-description all use this exact block). Sentinel written only after a successful
# install, so a half-built venv self-heals on the next run instead of wedging.
VENV="${CONTENT_OS_WHISPER_VENV:-$HOME/.cache/content-os/whisper-venv}"
PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
if [ ! -e "$VENV/.deps-ok" ]; then
  log "first-run: building faster-whisper venv at $VENV"
  rm -rf "$VENV"
  uv venv "$VENV" --python 3.11 >&2
  PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
  uv pip install --python "$PYBIN" faster-whisper onnxruntime >&2
  touch "$VENV/.deps-ok"
fi

log "transcribing (model=$MODEL)"
"$PYBIN" - "$AUDIO" "$OUT" "$MODEL" <<'PY'
import sys
from faster_whisper import WhisperModel

audio, out_file, model_name = sys.argv[1:]
model = WhisperModel(model_name, device="auto", compute_type="int8")
segments, _ = model.transcribe(audio, vad_filter=True,
                               vad_parameters=dict(min_silence_duration_ms=500))
text = " ".join(seg.text.strip() for seg in segments if seg.text.strip()).strip()
with open(out_file, "w", encoding="utf-8") as f:
    f.write(text + "\n")
PY

echo "$OUT"
