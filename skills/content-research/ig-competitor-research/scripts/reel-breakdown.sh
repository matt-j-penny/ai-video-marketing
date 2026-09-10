#!/usr/bin/env bash
# reel-breakdown.sh — download a reel, grab keyframes, transcribe it.
# usage: reel-breakdown.sh <outdir> <video_url>
#
#   <video_url>  the detailedData `videoUrl` (a muxed mp4 CDN link with
#                audio+video) — downloaded with a plain curl. CDN URLs are
#                signed + expire, so the subagent downloads immediately.
#
# Produces in <outdir>:
#   video.mp4        the downloaded reel
#   frame_01s.jpg …  keyframes at 1s, 2s, 3s, and the video midpoint
#   transcript.md    hook (first spoken line) + full transcript
#
# Whisper model defaults to small.en (override: WHISPER_MODEL=medium.en).
# Uses a persistent faster-whisper venv (~/.cache/content-os/whisper-venv),
# built once on first run and reused every run after — no per-run dep resolve.
set -euo pipefail

# preflight: fail fast with an actionable message instead of a silent exit-127 mid-pipeline
for t in curl ffmpeg ffprobe uv; do
  command -v "$t" >/dev/null 2>&1 || { echo "[error] $t is not installed; run ./setup.sh from the project root (or see the skill README Prerequisites)" >&2; exit 1; }
done

OUTDIR="${1:?usage: reel-breakdown.sh <outdir> <video_url>}"
SRC="${2:?usage: reel-breakdown.sh <outdir> <video_url> (the detailedData videoUrl)}"
MODEL="${WHISPER_MODEL:-small.en}"
mkdir -p "$OUTDIR"
VIDEO="$OUTDIR/video.mp4"

# --- download: curl the muxed CDN videoUrl (retry transient blips) ---
echo "[reel] curl $SRC" >&2
curl -fsSL --retry 3 --retry-delay 1 -H 'User-Agent: Mozilla/5.0' "$SRC" -o "$VIDEO" 2>/dev/null || true
[ -s "$VIDEO" ] || { echo "[error] reel download failed (videoUrl dead/expired): $SRC" >&2; exit 1; }

# --- keyframes: 1s, 2s, 3s (hook window) + midpoint (body format) ---
DUR="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO" 2>/dev/null | cut -d. -f1 || true)"
case "$DUR" in ''|*[!0-9]*) DUR=0;; esac   # covers ffprobe failure, empty, and "N/A"
MID=$(( DUR / 2 )); [ "$MID" -lt 1 ] && MID=4
for t in 1 2 3 "$MID"; do
  label="$(printf '%02ds' "$t")"
  ffmpeg -nostdin -loglevel error -ss "$t" -i "$VIDEO" -frames:v 1 -q:v 3 \
    "$OUTDIR/frame_${label}.jpg" -y >&2 || true
done

# --- audio → whisper ---
AUDIO="$OUTDIR/audio.mp3"
# a silent reel (no audio stream) is still a valid pick: keep the frames, write a
# transcript stub, exit 0 so the subagent reports OK instead of FAIL
ffmpeg -nostdin -loglevel error -i "$VIDEO" -vn -ac 1 -ar 16000 -q:a 4 "$AUDIO" -y >&2 || {
  echo "[warn] no audio stream (or audio extraction failed): writing a transcript stub" >&2
  printf '**Hook (first spoken line):** (no speech detected)\n\n**Full transcript:**\n\n(no speech detected)\n' > "$OUTDIR/transcript.md"
  echo "$OUTDIR"
  exit 0
}

# Persistent venv: built once, reused every run (no per-run dep resolution).
VENV="${CONTENT_OS_WHISPER_VENV:-$HOME/.cache/content-os/whisper-venv}"
PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
# sentinel written only after a successful install — a half-built venv (install
# interrupted once) self-heals on the next run instead of wedging forever
if [ ! -e "$VENV/.deps-ok" ]; then
  echo "[reel] first-run: building faster-whisper venv at $VENV" >&2
  rm -rf "$VENV"
  uv venv "$VENV" --python 3.11 >&2
  PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
  uv pip install --python "$PYBIN" faster-whisper onnxruntime >&2
  touch "$VENV/.deps-ok"
fi
echo "[reel] transcribing (model=$MODEL)" >&2
"$PYBIN" - "$AUDIO" "$OUTDIR/transcript.md" "$MODEL" <<'PY'
import sys
from faster_whisper import WhisperModel

audio, out_file, model_name = sys.argv[1:]
model = WhisperModel(model_name, device="auto", compute_type="int8")
segments, _ = model.transcribe(
    audio, vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500)
)
segs = [s.text.strip() for s in segments if s.text.strip()]
hook = segs[0] if segs else "(no speech detected)"
full = " ".join(segs) if segs else "(no speech detected)"
with open(out_file, "w", encoding="utf-8") as f:
    f.write(f"**Hook (first spoken line):** {hook}\n\n**Full transcript:**\n\n{full}\n")
PY

echo "$OUTDIR"
