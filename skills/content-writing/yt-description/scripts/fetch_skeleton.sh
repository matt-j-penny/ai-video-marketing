#!/usr/bin/env bash
# Pull the most recent long-form descriptions off the creator's YouTube channel.
# The newest one IS the skeleton for the new description; the older ones are
# only there so you can tell a FIXED block (appears every time) apart from a
# one-off block (appeared once, e.g. a one-off referral block).
#
# Usage: fetch_skeleton.sh [--count N] [--out DIR] [--channel URL]
# Channel: --channel wins, else $YT_DESC_CHANNEL, else the script's built-in
# default if any (SKILL.md always passes --channel with the /videos URL of the
# channel in CLAUDE.md, Creator Profile).
# Writes: DIR/skeleton-1.txt (newest) ... DIR/skeleton-N.txt + DIR/index.txt (the IDs)
# Prints the output dir on the last line.
#
# The /videos tab is long-form only — Shorts live on /shorts and never carry
# this description format, so they can't leak into the skeleton.

set -euo pipefail

CHANNEL="${YT_DESC_CHANNEL:-}"
COUNT=2
OUT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --count)   COUNT="$2"; shift 2 ;;
    --out)     OUT="$2"; shift 2 ;;
    --channel) CHANNEL="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 64 ;;
  esac
done

command -v yt-dlp >/dev/null || { echo "yt-dlp not found" >&2; exit 69; }
[ -n "$CHANNEL" ] || { echo "no channel: pass --channel https://www.youtube.com/@<handle>/videos or set YT_DESC_CHANNEL (the channel handle/ID is in CLAUDE.md, Creator Profile)" >&2; exit 64; }

if [ -z "$OUT" ]; then
  OUT="$(mktemp -d "${TMPDIR:-/tmp}/yt-desc.XXXXXXXX")"
fi
mkdir -p "$OUT"

# Step 1: the newest COUNT video IDs. One --print per field: a literal \t in a
# single template is NOT interpreted, so a combined "%(id)s\t%(title)s" comes
# back as one unsplittable string.
yt-dlp --flat-playlist --playlist-end "$COUNT" \
       --print "%(id)s" "$CHANNEL" > "$OUT/index.txt"

# Step 2: one full-metadata fetch per ID for the title + description body.
n=0
while read -r id; do
  [ -n "$id" ] || continue
  n=$((n + 1))
  {
    echo "### VIDEO $n — https://www.youtube.com/watch?v=$id"
    yt-dlp --skip-download --print "%(title)s" "https://www.youtube.com/watch?v=$id"
    echo
    yt-dlp --skip-download --print "%(description)s" "https://www.youtube.com/watch?v=$id"
  } > "$OUT/skeleton-$n.txt"
done < "$OUT/index.txt"

echo "$OUT"
