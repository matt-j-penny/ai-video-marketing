#!/usr/bin/env bash
# fetch-images.sh — download carousel slides / a single image for visual analysis.
# usage: fetch-images.sh <outdir> <imageurls.txt>
#
# <imageurls.txt> is the file rank-and-select.py wrote into the job dir: the
# Apify `images[]` array (carousel) or the single `displayUrl` (image post),
# one URL per line. The script reads it itself, so no shell word-splitting of
# scraped URLs. Slides are saved in order as slide_01.jpg, slide_02.jpg, …
# These are public cdninstagram/fbcdn URLs — a plain curl is enough.
set -euo pipefail

OUTDIR="${1:?usage: fetch-images.sh <outdir> <imageurls.txt>}"
URLFILE="${2:?usage: fetch-images.sh <outdir> <imageurls.txt> (one URL per line)}"
[ -s "$URLFILE" ] || { echo "[error] url file missing or empty: $URLFILE" >&2; exit 1; }
mkdir -p "$OUTDIR"

i=0
while IFS= read -r url || [ -n "$url" ]; do
  [ -n "$url" ] || continue
  i=$((i + 1))
  out="$OUTDIR/$(printf 'slide_%02d.jpg' "$i")"
  curl -fsSL --retry 3 --retry-delay 1 \
    -H 'User-Agent: Mozilla/5.0' \
    "$url" -o "$out" >&2 || { echo "[warn] slide $i failed" >&2; continue; }
done < "$URLFILE"
[ "$i" -ge 1 ] || { echo "[error] no image urls in $URLFILE" >&2; exit 1; }

[ "$(find "$OUTDIR" -name 'slide_*.jpg' | wc -l | tr -d ' ')" -gt 0 ] \
  || { echo "[error] no slides downloaded" >&2; exit 1; }
echo "$OUTDIR"
