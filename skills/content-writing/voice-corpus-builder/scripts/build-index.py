#!/usr/bin/env python3
"""Regenerate voice-corpus/index.md from the entries' frontmatter (ranked by views).

usage: build-index.py [--corpus DIR] [--owner "Name"]
Run after adding or re-tagging entries. Prints a one-line summary + any entries
still carrying TODO tags (those are invisible to scriptwriter's format filters).
"""
import argparse, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CORPUS = os.environ.get("VOICE_CORPUS_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "voice-corpus"))


def load(corpus):
    rows = []
    for fn in sorted(os.listdir(corpus)):
        if not fn.endswith(".md") or fn == "index.md":
            continue
        text = open(os.path.join(corpus, fn), encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            continue
        meta = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        meta["_file"] = fn
        for k in ("views", "likes"):
            try:
                meta["_" + k] = int(meta.get(k, 0))
            except ValueError:
                meta["_" + k] = 0
        rows.append(meta)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--owner", default="Your", help='possessive label for the blurb, e.g. "Jane\'s" (default "Your")')
    a = ap.parse_args()
    rows = load(a.corpus)
    if not rows:
        sys.exit(f"no entries in {a.corpus}")
    rows.sort(key=lambda r: (r["_views"], r["_likes"]), reverse=True)  # likes break ties (no play counts)

    n_ig = sum(1 for r in rows if r.get("platform") == "instagram")
    n_yt = sum(1 for r in rows if r.get("platform") == "youtube")
    n_tt = sum(1 for r in rows if r.get("platform") == "tiktok")
    todo = [r["id"] for r in rows if any("TODO" in r.get(k, "") for k in ("format", "hook_type", "spoken_hook"))]

    lines = [
        "# Voice Corpus Index", "",
        f"{a.owner} own top-performing content, verbatim transcripts. Built {date.today().isoformat()} "
        f"with the `voice-corpus-builder` skill ({n_ig} IG, {n_yt} YT{f', {n_tt} TikTok' if n_tt else ''}). "
        "One file per video, YAML frontmatter carries metadata + tags. Query with "
        "`.claude/skills/scriptwriter/scripts/find_voice.py` — don't read every file.", "",
        "| entry | platform | views/plays | date | dur | format | title/caption |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        dur = r.get("duration_s", "0")
        cap = (r.get("caption") or "").replace("|", "¦")[:60]
        lines.append(f"| [{r['id']}]({r['_file']}) | {r.get('platform','')} | {r['_views']:,} | "
                     f"{r.get('date','')} | {dur}s | {r.get('format','')} | {cap} |")
    if todo:
        lines += ["", f"> ⚠️ {len(todo)} entries still carry TODO tags (tag them with `tag.py`): " + ", ".join(todo)]
    lines.append("")
    open(os.path.join(a.corpus, "index.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"index.md: {len(rows)} entries ({n_ig} IG, {n_yt} YT); {len(todo)} untagged")


if __name__ == "__main__":
    main()
