#!/usr/bin/env bash
# fetch-thumb.sh — download a pick's YouTube thumbnail for visual analysis.
# usage: fetch-thumb.sh <jobdir>
#
# Reads <jobdir>/thumburl.txt (written by rank-and-select.py) and saves the
# image as <jobdir>/thumb.jpg. Public i.ytimg.com URL — a plain curl is enough.
set -euo pipefail

JOBDIR="${1:?usage: fetch-thumb.sh <jobdir>}"
URL="$(head -n 1 "$JOBDIR/thumburl.txt" 2>/dev/null || true)"
[ -n "$URL" ] || { echo "[error] $JOBDIR/thumburl.txt is missing or empty" >&2; exit 1; }

curl -fsSL --retry 3 --retry-delay 1 \
  -H 'User-Agent: Mozilla/5.0' \
  "$URL" -o "$JOBDIR/thumb.jpg" >&2 \
  || { echo "[error] thumbnail download failed: $URL" >&2; exit 1; }

[ -s "$JOBDIR/thumb.jpg" ] || { echo "[error] thumb.jpg is empty" >&2; exit 1; }
echo "$JOBDIR/thumb.jpg"
