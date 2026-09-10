#!/usr/bin/env bash
# yt-entry.sh — turn ONE YouTube video into a voice-corpus entry.
# usage: yt-entry.sh <video-url-or-id> [--era TAG]
#
# One yt-dlp metadata call (views/likes/date/duration/title) that also grabs the
# English captions (creator-uploaded first, YouTube auto-captions otherwise) as
# json3. If the video has no captions at all, the audio is downloaded and
# transcribed locally with faster-whisper — captions vs whisper is decided by the
# video, not by a failure. Writes voice-corpus/yt-<id>.md (tags left TODO) and
# prints its path. Re-running overwrites the entry (tags reset to TODO).
set -euo pipefail
command -v yt-dlp >/dev/null 2>&1 || { echo "[error] yt-dlp is not installed; run ./setup.sh from the project root" >&2; exit 1; }
# Windows installs Python as `python` (its `python3` is a Store stub): resolve once by running it
PY=python3; python3 -c '' >/dev/null 2>&1 || { PY=python; python -c '' >/dev/null 2>&1 || { echo "[error] python not found; run ./setup.sh from the project root" >&2; exit 1; }; }

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="${1:?usage: yt-entry.sh <video-url-or-id> [--era TAG]}"
ERA=current
shift || true
while [ $# -gt 0 ]; do
  case "$1" in
    --era) ERA="${2:?--era needs a value}"; shift 2 ;;
    *) echo "[error] unknown arg: $1" >&2; exit 1 ;;
  esac
done
case "$SRC" in http*) URL="$SRC" ;; *) URL="https://www.youtube.com/watch?v=$SRC" ;; esac

WORK="$(mktemp -d "${TMPDIR:-/tmp}/vcb-yt-XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

echo "[yt-entry] $URL" >&2
yt-dlp --skip-download --no-playlist --quiet --no-warnings \
  --write-subs --write-auto-subs --sub-lang en --sub-format json3 \
  --print-to-file '%(id)s' "$WORK/id.txt" \
  --print-to-file '%(title)s' "$WORK/title.txt" \
  --print-to-file '%(view_count)s' "$WORK/views.txt" \
  --print-to-file '%(like_count)s' "$WORK/likes.txt" \
  --print-to-file '%(upload_date)s' "$WORK/date.txt" \
  --print-to-file '%(duration)s' "$WORK/duration.txt" \
  --print-to-file '%(webpage_url)s' "$WORK/url.txt" \
  -o "$WORK/sub.%(ext)s" "$URL" >&2

VID="$(cat "$WORK/id.txt")"
TITLE="$(cat "$WORK/title.txt" 2>/dev/null || echo "")"
VIEWS="$(cat "$WORK/views.txt" 2>/dev/null || echo 0)"; case "$VIEWS" in ''|NA|None) VIEWS=0 ;; esac
LIKES="$(cat "$WORK/likes.txt" 2>/dev/null || echo 0)"; case "$LIKES" in ''|NA|None) LIKES=0 ;; esac
DUR="$(cat "$WORK/duration.txt" 2>/dev/null || echo 0)"; case "$DUR" in ''|NA|None) DUR=0 ;; esac; DUR="${DUR%%.*}"
RAWDATE="$(cat "$WORK/date.txt" 2>/dev/null || echo "")"
if printf '%s' "$RAWDATE" | grep -Eq '^[0-9]{8}$'; then DATE="${RAWDATE:0:4}-${RAWDATE:4:2}-${RAWDATE:6:2}"; else DATE=unknown; fi
CANON="$(cat "$WORK/url.txt" 2>/dev/null || echo "$URL")"

SUB="$(find "$WORK" -maxdepth 1 -name 'sub*.json3' | head -n1)"
TXT="$WORK/transcript.txt"
if [ -n "$SUB" ]; then
  echo "[yt-entry] captions found, parsing json3" >&2
  "$PY" - "$SUB" "$TXT" <<'PY'
import json, sys
src, out = sys.argv[1:]
d = json.load(open(src, encoding="utf-8"))
# segs inside one event are word pieces (their utf8 carries its own leading space);
# events themselves carry no separator, so join events with a space or words fuse
events = []
for ev in d.get("events", []):
    segs = [seg.get("utf8", "") for seg in (ev.get("segs") or [])]
    line = "".join(t for t in segs if t and t != "\n").strip()
    if line:
        events.append(line)
text = " ".join(" ".join(events).split())
open(out, "w", encoding="utf-8").write(text + "\n")
print(f"[yt-entry] {len(text.split())} words from captions", file=sys.stderr)
PY
else
  echo "[yt-entry] no captions on this video, downloading audio for whisper" >&2
  yt-dlp -x --audio-format m4a --no-playlist --quiet --no-warnings -o "$WORK/audio.%(ext)s" "$URL" >&2
  AUDIO="$(find "$WORK" -maxdepth 1 -name 'audio.*' | head -n1)"
  [ -n "$AUDIO" ] || { echo "[error] audio download failed for $URL" >&2; exit 1; }
  bash "$HERE/transcribe-file.sh" "$AUDIO" "$TXT"
fi

"$PY" "$HERE/write_entry.py" --id "yt-$VID" --platform youtube --url "$CANON" \
  --views "$VIEWS" --likes "$LIKES" --date "$DATE" --duration "$DUR" \
  --caption "$TITLE" --transcript-file "$TXT" --era "$ERA"
