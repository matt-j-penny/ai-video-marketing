#!/usr/bin/env python3
"""Fetch top comments for YouTube videos into one markdown file per video.

Usage: fetch-comments.py <out_dir> <video_id> [<video_id> ...] [--max 100]

Uses the YouTube Data API v3 (commentThreads, sorted by relevance) when
YOUTUBE_API_KEY is set in the environment or in ./.env. Falls back to yt-dlp
(free, no key) otherwise. Stdlib only.
"""
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request


def api_key():
    if os.environ.get("YOUTUBE_API_KEY"):
        return os.environ["YOUTUBE_API_KEY"]
    if os.path.exists(".env"):
        for line in open(".env"):
            if line.strip().startswith("YOUTUBE_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def via_api(vid, key, limit):
    out, token = [], None
    while len(out) < limit:
        q = {"part": "snippet", "videoId": vid, "order": "relevance", "maxResults": min(100, limit - len(out)),
             "textFormat": "plainText", "key": key}
        if token:
            q["pageToken"] = token
        url = "https://www.googleapis.com/youtube/v3/commentThreads?" + urllib.parse.urlencode(q)
        data = json.load(urllib.request.urlopen(url, timeout=30))
        for item in data.get("items", []):
            s = item["snippet"]["topLevelComment"]["snippet"]
            out.append((s.get("likeCount", 0), item["snippet"].get("totalReplyCount", 0), s["textDisplay"]))
        token = data.get("nextPageToken")
        if not token:
            break
    return out


def via_ytdlp(vid, limit):
    r = subprocess.run(["yt-dlp", "-J", "--skip-download", "--write-comments", "--extractor-args",
                        f"youtube:comment_sort=top;max_comments={limit},all,0",
                        f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True, timeout=300)
    comments = json.loads(r.stdout or "{}").get("comments") or []
    return [(c.get("like_count") or 0, 0, c.get("text", "")) for c in comments if c.get("parent") == "root"][:limit]


def main():
    args = sys.argv[1:]
    limit = 100
    if "--max" in args:
        i = args.index("--max")
        limit = int(args[i + 1])
        del args[i:i + 2]
    out_dir, ids = args[0], args[1:]
    os.makedirs(out_dir, exist_ok=True)
    key = api_key()
    for vid in ids:
        try:
            rows, src = (via_api(vid, key, limit), "api") if key else (via_ytdlp(vid, limit), "yt-dlp")
        except Exception as e:  # comments disabled, quota, network: note it and move on
            print(f"{vid}: failed ({e})", file=sys.stderr)
            continue
        rows.sort(key=lambda r: -r[0])
        with open(os.path.join(out_dir, f"{vid}.md"), "w") as f:
            f.write(f"# Comments for {vid} ({len(rows)}, via {src}, sorted by likes)\n\n")
            for likes, replies, text in rows:
                f.write(f"- [{likes} likes, {replies} replies] {' '.join(text.split())}\n")
        print(f"{vid}: {len(rows)} comments via {src}", file=sys.stderr)


if __name__ == "__main__":
    main()
