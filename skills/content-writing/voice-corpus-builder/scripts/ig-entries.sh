#!/usr/bin/env bash
# ig-entries.sh — turn the creator's OWN Instagram reels into voice-corpus entries.
# usage: ig-entries.sh <dataset.json> [N] [--era TAG]
#
# <dataset.json> = the bare items array from apify/instagram-post-scraper
# (dataDetailLevel: detailedData) for the creator's handle — the orchestrator
# pulls it via the Apify MCP exactly like ig-competitor-research does. This
# script keeps the videos, ranks them by plays (likes when the actor returns no
# play count), takes the top N (default 20), then for each: curls the reel from
# its signed videoUrl, transcribes it with faster-whisper, and writes
# voice-corpus/ig-<shortCode>.md (tags left TODO). Prints one line per entry.
# Signed CDN URLs expire in hours — run this right after the scrape.
set -euo pipefail
for t in curl ffmpeg uv; do
  command -v "$t" >/dev/null 2>&1 || { echo "[error] $t is not installed; run ./setup.sh from the project root" >&2; exit 1; }
done
# Windows installs Python as `python` (its `python3` is a Store stub): resolve once by running it
PY=python3; python3 -c '' >/dev/null 2>&1 || { PY=python; python -c '' >/dev/null 2>&1 || { echo "[error] python not found; run ./setup.sh from the project root" >&2; exit 1; }; }

HERE="$(cd "$(dirname "$0")" && pwd)"
DATASET="${1:?usage: ig-entries.sh <dataset.json> [N] [--era TAG]}"
N=20; ERA=current
shift
while [ $# -gt 0 ]; do
  case "$1" in
    --era) ERA="${2:?--era needs a value}"; shift 2 ;;
    ''|*[!0-9]*) echo "[error] unknown arg: $1" >&2; exit 1 ;;
    *) N="$1"; shift ;;
  esac
done
[ -s "$DATASET" ] || { echo "[error] dataset missing or empty: $DATASET" >&2; exit 1; }

WORK="$(mktemp -d "${TMPDIR:-/tmp}/vcb-ig-XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

# rank + emit a TSV plan: shortCode  videoUrl  plays  likes  date  duration  url  caption
"$PY" - "$DATASET" "$N" "$WORK/plan.tsv" <<'PY'
import json, sys
src, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
raw = json.load(open(src, encoding="utf-8"))
items = raw.get("items", raw) if isinstance(raw, dict) else raw
def i(v):
    try: return int(v)
    except (TypeError, ValueError): return 0
vids = []
for it in items:
    if (it.get("type") or "").lower() != "video": continue
    if not it.get("videoUrl"): continue
    plays = i(it.get("videoPlayCount") or it.get("videoViewCount"))
    likes = i(it.get("likesCount"))
    ts = (it.get("timestamp") or "")[:10] or "unknown"
    cap = " ".join((it.get("caption") or "").split()).replace("\t", " ")
    vids.append((plays, likes, it.get("shortCode") or "", it["videoUrl"], ts,
                 i(it.get("videoDuration")), it.get("url") or f"https://www.instagram.com/p/{it.get('shortCode','')}/", cap))
if not vids:
    print("[error] no videos with a videoUrl in the dataset (need dataDetailLevel: detailedData)", file=sys.stderr); sys.exit(1)
has_plays = any(v[0] > 0 for v in vids)
vids.sort(key=lambda v: (v[0], v[1]), reverse=True)
with open(out, "w", encoding="utf-8") as f:
    for v in vids[:n]:
        f.write("\t".join(str(x) for x in (v[2], v[3], v[0], v[1], v[4], v[5], v[6], v[7])) + "\n")
print(f"[ig-entries] {len(vids)} videos in dataset, ranking by {'plays' if has_plays else 'likes (no play counts returned)'}, keeping top {min(n, len(vids))}", file=sys.stderr)
PY

k=0; fails=0
while IFS=$'\t' read -r CODE VURL PLAYS LIKES DATE DUR URL CAP; do
  k=$((k+1))
  echo "[ig-entries] $k. $CODE ($PLAYS plays, $LIKES likes)" >&2
  MP4="$WORK/$CODE.mp4"
  if ! curl -sSL --fail --retry 3 --retry-delay 2 -A "Mozilla/5.0" -o "$MP4" "$VURL"; then
    echo "[ig-entries]    ✗ download failed (signed URL expired? re-scrape and re-run)" >&2
    fails=$((fails+1)); continue
  fi
  TXT="$WORK/$CODE.txt"
  if ! bash "$HERE/transcribe-file.sh" "$MP4" "$TXT"; then
    echo "[ig-entries]    ✗ transcription failed" >&2; fails=$((fails+1)); continue
  fi
  "$PY" "$HERE/write_entry.py" --id "ig-$CODE" --platform instagram --url "$URL" \
    --views "$PLAYS" --likes "$LIKES" --date "$DATE" --duration "$DUR" \
    --caption "$CAP" --transcript-file "$TXT" --era "$ERA"
  rm -f "$MP4"
done < "$WORK/plan.tsv"
echo "[ig-entries] done: $((k-fails)) written, $fails failed" >&2
[ "$fails" -eq 0 ]
