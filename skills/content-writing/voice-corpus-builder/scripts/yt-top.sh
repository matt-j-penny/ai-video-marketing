#!/usr/bin/env bash
# yt-top.sh — rank a YouTube channel's uploads by views and print the top N.
# usage: yt-top.sh <channel> [N] [--shorts]
#   <channel>  a handle (@name or name), a channel URL, or a full /videos | /shorts URL
#   N          how many to keep (default 15)
#   --shorts   rank the Shorts tab instead of long-form uploads
#
# Output: one JSON object per line, ranked by views desc:
#   {"rank":1,"id":"...","url":"https://www.youtube.com/watch?v=...","title":"...","views":123,"duration":612}
# (metadata comes from a single flat-playlist listing — no per-video fetch here;
#  yt-entry.sh does the per-video work for the ones you keep)
set -euo pipefail
command -v yt-dlp >/dev/null 2>&1 || { echo "[error] yt-dlp is not installed; run ./setup.sh from the project root" >&2; exit 1; }
# Windows installs Python as `python` (its `python3` is a Store stub): resolve once by running it
PY=python3; python3 -c '' >/dev/null 2>&1 || { PY=python; python -c '' >/dev/null 2>&1 || { echo "[error] python not found; run ./setup.sh from the project root" >&2; exit 1; }; }

CHANNEL="${1:?usage: yt-top.sh <channel> [N] [--shorts]}"
N=15; TAB=videos
shift
for a in "$@"; do
  case "$a" in
    --shorts) TAB=shorts ;;
    ''|*[!0-9]*) echo "[error] unknown arg: $a" >&2; exit 1 ;;
    *) N="$a" ;;
  esac
done

case "$CHANNEL" in
  http*://*/videos|http*://*/shorts) URL="$CHANNEL" ;;
  http*://*)                          URL="${CHANNEL%/}/$TAB" ;;
  @*)                                 URL="https://www.youtube.com/$CHANNEL/$TAB" ;;
  *)                                  URL="https://www.youtube.com/@$CHANNEL/$TAB" ;;
esac
echo "[yt-top] listing $URL" >&2

yt-dlp --flat-playlist -j --quiet --no-warnings "$URL" \
| "$PY" -c '
import json, sys
n = int(sys.argv[1]); rows = []
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try: d = json.loads(line)
    except json.JSONDecodeError: continue
    vid = d.get("id") or ""
    if not vid: continue
    rows.append({
        "id": vid,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "title": d.get("title") or "",
        "views": int(d.get("view_count") or 0),
        "duration": int(d.get("duration") or 0),
    })
rows.sort(key=lambda r: r["views"], reverse=True)
if not rows:
    print("[yt-top] no videos found (private channel, wrong handle, or yt-dlp needs an update: yt-dlp -U)", file=sys.stderr); sys.exit(1)
for i, r in enumerate(rows[:n], 1):
    r = {"rank": i, **r}
    print(json.dumps(r, ensure_ascii=False))
print(f"[yt-top] {len(rows)} uploads scanned, top {min(n, len(rows))} kept", file=sys.stderr)
' "$N"
