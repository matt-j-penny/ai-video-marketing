#!/usr/bin/env python3
"""Write ONE voice-corpus entry (voice-corpus/<id>.md) with the standard frontmatter.

Shared by yt-entry.sh and ig-entries.sh so both platforms produce byte-identical
shapes that find_voice.py (scriptwriter) can slice. Tags (era / format /
hook_type / spoken_hook) are left as placeholders here; Claude fills them with
tag.py after reading the transcript.

usage:
  write_entry.py --id yt-abc123 --platform youtube --url URL --views 12345
                 --likes 0 --date 2026-01-31 --duration 612 --caption "Title"
                 --transcript-file /path/to/transcript.txt [--corpus DIR]
Prints the written path.
"""
import argparse, os, re, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CORPUS = os.environ.get("VOICE_CORPUS_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "voice-corpus"))


def yaml_str(s: str, limit: int = 140) -> str:
    """One-line double-quoted YAML scalar, safe for find_voice.py's naive parser."""
    s = " ".join((s or "").split())
    s = s.replace('"', "'")
    if len(s) > limit:
        s = s[: limit - 1].rstrip() + "…"
    return f'"{s}"'


def wrap(text: str, width: int = 92) -> str:
    """Wrap a one-paragraph transcript to readable lines (matches the existing corpus)."""
    text = " ".join((text or "").split())
    if not text:
        return "(no speech detected)"
    # break at sentence ends first so lines read like the spoken beats
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for s in sentences:
        out.extend(textwrap.wrap(s, width=width) or [s])
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="entry id, e.g. yt-<videoId> or ig-<shortCode>")
    ap.add_argument("--platform", required=True, choices=["youtube", "instagram", "tiktok"])
    ap.add_argument("--url", required=True)
    ap.add_argument("--views", type=int, default=0)
    ap.add_argument("--likes", type=int, default=0)
    ap.add_argument("--date", default="unknown", help="YYYY-MM-DD")
    ap.add_argument("--duration", type=int, default=0, help="seconds")
    ap.add_argument("--caption", default="", help="video title (YT) or caption (IG)")
    ap.add_argument("--transcript-file", required=True)
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--era", default="current")
    args = ap.parse_args()

    with open(args.transcript_file, encoding="utf-8") as f:
        transcript = f.read()

    os.makedirs(args.corpus, exist_ok=True)
    path = os.path.join(args.corpus, f"{args.id}.md")

    if args.platform == "youtube":
        h1 = f"# {' '.join(args.caption.split()) or args.id} — {args.views:,} views"
        # long-form: the title IS the hook (scriptwriter rule)
        hook_type, spoken_hook = "title", yaml_str(args.caption)
    else:
        label = {"instagram": "IG reel", "tiktok": "TikTok"}[args.platform]
        # the post scraper returns no play counts on some accounts; show likes instead of "0 plays"
        stat = f"{args.views:,} plays" if args.views > 0 else f"{args.likes:,} likes"
        h1 = f"# {label} {args.id.split('-', 1)[-1]} — {stat}"
        hook_type, spoken_hook = "TODO", '"TODO — first spoken sentence, verbatim"'

    fm = "\n".join([
        "---",
        f"id: {args.id}",
        f"platform: {args.platform}",
        f"url: {args.url}",
        f"views: {args.views}",
        f"likes: {args.likes}",
        f"date: {args.date}",
        f"duration_s: {args.duration}",
        f"caption: {yaml_str(args.caption)}",
        f"era: {args.era}",
        "format: TODO",
        f"hook_type: {hook_type}",
        f"spoken_hook: {spoken_hook}",
        "---",
    ])
    body = f"{fm}\n\n{h1}\n\n{wrap(transcript)}\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    print(path)


if __name__ == "__main__":
    main()
