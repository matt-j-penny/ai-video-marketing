#!/usr/bin/env python3
"""Slice the voice corpus (voice-corpus/*.md) by format / platform / era / keyword.

Returns the best-matching entries ranked by views so the scriptwriter can pull
2-3 verbatim few-shot transcripts without reading the whole corpus.

Examples (run from the repo root; `python` on Windows):
  python3 .claude/skills/scriptwriter/scripts/find_voice.py --list                       # tag counts across corpus
  python3 .claude/skills/scriptwriter/scripts/find_voice.py --format giveaway --top 3    # top giveaway reels
  python3 .claude/skills/scriptwriter/scripts/find_voice.py --platform youtube --top 3 --excerpt 400
  python3 .claude/skills/scriptwriter/scripts/find_voice.py --keyword "workflow" --era <current-era-tag>
  python3 .claude/skills/scriptwriter/scripts/find_voice.py --id <entry-id> --full       # one entry, full text
"""
import argparse, os, re, sys

CORPUS = os.path.join(os.path.dirname(__file__), "../../../../voice-corpus")


def load_entries():
    if not os.path.isdir(CORPUS):
        sys.exit("voice-corpus/ not found at " + os.path.normpath(CORPUS)
                 + ". Build it with the voice-corpus-builder skill first.")
    entries = []
    for fn in sorted(os.listdir(CORPUS)):
        if not fn.endswith(".md") or fn == "index.md":
            continue
        with open(os.path.join(CORPUS, fn), encoding="utf-8") as f:
            text = f.read()
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
        if not m:
            continue
        meta = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        meta["views"] = int(meta.get("views", 0))
        try:
            meta["likes"] = int(meta.get("likes", 0))
        except ValueError:
            meta["likes"] = 0
        meta["body"] = m.group(2).strip()
        meta["path"] = os.path.join("voice-corpus", fn)
        entries.append(meta)
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", help="format tag, substring match (e.g. giveaway, rant, tutorial)")
    ap.add_argument("--platform", choices=["instagram", "youtube", "tiktok"])
    ap.add_argument("--era", help="era tag, substring match (e.g. current, previous)")
    ap.add_argument("--keyword", help="case-insensitive search in transcript body")
    ap.add_argument("--id", help="exact entry id")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--full", action="store_true", help="print full transcript")
    ap.add_argument("--excerpt", type=int, metavar="N", help="print first N words of transcript")
    ap.add_argument("--list", action="store_true", help="show tag counts")
    args = ap.parse_args()

    entries = load_entries()
    if not entries:
        sys.exit("No corpus entries found at " + CORPUS + " (build it with the voice-corpus-builder skill: say \"build my voice corpus\")")

    if args.list:
        from collections import Counter
        for field in ("format", "hook_type", "era", "platform"):
            counts = Counter(e.get(field, "?") for e in entries)
            print(f"{field}: " + ", ".join(f"{k} ({v})" for k, v in counts.most_common()))
        print(f"total: {len(entries)} entries")
        return

    if args.id:
        entries = [e for e in entries if e.get("id") == args.id]
    if args.format:
        entries = [e for e in entries if args.format.lower() in e.get("format", "").lower()]
    if args.platform:
        entries = [e for e in entries if e.get("platform") == args.platform]
    if args.era:
        entries = [e for e in entries if args.era.lower() in e.get("era", "").lower()]
    if args.keyword:
        entries = [e for e in entries if args.keyword.lower() in e["body"].lower()]

    entries.sort(key=lambda e: (-e["views"], -e["likes"]))  # likes break ties (IG entries without play counts)
    for e in entries[: args.top]:
        print(f"=== {e['id']} · {e['platform']} · {e['views']:,} views · {e.get('date')} · "
              f"format={e.get('format')} · hook={e.get('hook_type')} · era={e.get('era')}")
        print(f"    {e['path']} · spoken_hook: {e.get('spoken_hook')}")
        if args.full:
            print(e["body"] + "\n")
        elif args.excerpt:
            words = e["body"].split()
            print(" ".join(words[: args.excerpt]) + (" […]" if len(words) > args.excerpt else "") + "\n")


if __name__ == "__main__":
    main()
