#!/usr/bin/env bash
# Build a word-level timeline index of the FINAL exported video.
#
# Chapters have to line up with the file that actually ships, not with the
# editing transcript — a Premiere/section-assembled cut re-orders and pads the
# timeline, so the splice transcript's times are wrong by minutes. So: always
# index the final file itself, then look phrases up in it (find_times.py).
#
# Quality doesn't matter here (this is an index, not copy) — the script text
# comes from the job transcript. faster-whisper base.en with word timestamps is
# plenty, and it runs on the SAME persistent venv every other transcription
# skill here uses (~/.cache/content-os/whisper-venv): one speech engine, no
# extra install. Word timestamps are native (real words, not sub-word tokens).
#
# Usage: chapter_index.sh <final-video> [out.tsv]
# Writes TSV: start_seconds <TAB> word     (prints the path on the last line)

set -euo pipefail

VIDEO="${1:?usage: chapter_index.sh <final-video> [out.tsv]}"
OUT="${2:-}"
MODEL="${YT_DESC_WHISPER_MODEL:-base.en}"

for t in ffmpeg uv; do
  command -v "$t" >/dev/null 2>&1 || { echo "$t not found; run ./setup.sh from the project root" >&2; exit 69; }
done
[ -f "$VIDEO" ] || { echo "no such video: $VIDEO" >&2; exit 66; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/yt-desc-idx.XXXXXXXX")"
chmod 700 "$WORK"
trap 'rm -rf "$WORK"' EXIT

[ -n "$OUT" ] || OUT="$(mktemp "${TMPDIR:-/tmp}/yt-desc-index.XXXXXXXX")"

ffmpeg -nostdin -v error -y -i "$VIDEO" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$WORK/a.wav"

# Shared persistent venv (same block as transcribe-url / auto-poster / voice-corpus-builder).
VENV="${CONTENT_OS_WHISPER_VENV:-$HOME/.cache/content-os/whisper-venv}"
PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
if [ ! -e "$VENV/.deps-ok" ]; then
  echo "first-run: building faster-whisper venv at $VENV" >&2
  rm -rf "$VENV"
  uv venv "$VENV" --python 3.11 >&2
  PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
  uv pip install --python "$PYBIN" faster-whisper onnxruntime >&2
  touch "$VENV/.deps-ok"
fi

"$PYBIN" - "$WORK/a.wav" "$OUT" "$MODEL" <<'PY'
import sys
from faster_whisper import WhisperModel

audio, dst, model_name = sys.argv[1:]
model = WhisperModel(model_name, device="auto", compute_type="int8")
segments, _ = model.transcribe(audio, word_timestamps=True, vad_filter=True,
                               vad_parameters=dict(min_silence_duration_ms=500))
n = 0
with open(dst, "w", encoding="utf-8") as f:
    for seg in segments:
        for w in seg.words or []:
            word = w.word.strip()
            if word:
                f.write(f"{w.start:.2f}\t{word}\n"); n += 1
print(f"{n} words indexed", file=sys.stderr)
PY

echo "$OUT"
