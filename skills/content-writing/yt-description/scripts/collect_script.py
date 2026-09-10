#!/usr/bin/env python3
"""Collect the word-for-word script for a finished video-editor job.

The canonical script for any job is the spliced transcript that `rough-cut`
derives from the final cut: projects/<job>/outputs/<job>.transcript.json (and
one per section for section-assembled jobs). This reads them, reports how much
of the final export they actually cover, and prints the whole thing as markdown.

Usage:
  collect_script.py <job> [--root ~/Projects/video-editor] [--text-only]

Exit codes: 0 ok · 2 job not found · 3 job found but no transcript
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path.home() / "Projects" / "video-editor"


def probe_duration(path: Path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=60,
        )
        return float(out.stdout.strip())
    except Exception:
        return None


def load_transcript(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    words = data.get("words") or []
    starts = [w["start"] for w in words if isinstance(w.get("start"), (int, float))]
    ends = [w["end"] for w in words if isinstance(w.get("end"), (int, float))]
    return {
        "path": path,
        "text": (data.get("text") or "").strip(),
        "n_words": len(words),
        "start": min(starts) if starts else None,
        "end": max(ends) if ends else None,
        "engine": data.get("engine", ""),
    }


def fmt_secs(s):
    if s is None:
        return "?"
    return f"{int(s // 60)}:{int(s % 60):02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--text-only", action="store_true",
                    help="print only the concatenated script text")
    args = ap.parse_args()

    root = Path(os.path.expanduser(args.root))
    job_dir = root / "projects" / args.job

    if not job_dir.is_dir():
        print(f"job not found: {job_dir}", file=sys.stderr)
        others = sorted(p.name for p in (root / "projects").glob("*") if p.is_dir())
        near = [o for o in others if args.job.lower() in o.lower() or o.lower() in args.job.lower()]
        print("closest jobs: " + ", ".join(near or others), file=sys.stderr)
        return 2

    # The exported deliverable, newest-first by convention.
    final = None
    for cand in (f"{args.job}.final.mp4", f"{args.job}-4k.mp4", f"{args.job}.mp4"):
        p = job_dir / "outputs" / cand
        if p.exists():
            final = p
            break
    final_dur = probe_duration(final) if final else None

    parts = []
    parent = job_dir / "outputs" / f"{args.job}.transcript.json"
    if parent.exists():
        parts.append(("(parent)", load_transcript(parent)))
    for sec in sorted((job_dir / "sections").glob("*/outputs/*.transcript.json")):
        parts.append((sec.parents[1].name, load_transcript(sec)))

    if not parts:
        print(f"no transcript under {job_dir}/outputs or /sections", file=sys.stderr)
        print("this job was never rough-cut here — use the Notion beat sheet instead",
              file=sys.stderr)
        return 3

    if args.text_only:
        print("\n\n".join(p[1]["text"] for p in parts))
        return 0

    spoken = sum((p[1]["end"] or 0) - (p[1]["start"] or 0) for p in parts)

    print(f"# Script bundle — {args.job}\n")
    print(f"- job folder: `{job_dir}`")
    print(f"- final export: `{final}`" if final else "- final export: **none found in outputs/**")
    print(f"- final duration: {fmt_secs(final_dur)} ({final_dur:.1f}s)" if final_dur else "")
    print(f"- transcript parts: {len(parts)}")
    print(f"- spoken time across parts: {fmt_secs(spoken)} ({spoken:.1f}s)")

    if final_dur and spoken:
        cover = spoken / final_dur
        print(f"- coverage: {cover:.0%} of the final export")
        if cover < 0.9:
            print("\n> ⚠️  The transcripts do NOT cover the final export. This job was")
            print("> assembled outside the splice (Premiere/hand-finished, extra sections,")
            print("> or a re-order). Treat the text below as the script only. Chapter")
            print("> timestamps MUST come from `chapter_index.sh` on the final file.")
        elif cover > 1.05:
            print("\n> ⚠️  The transcripts run LONGER than the final export. Parts include")
            print("> superseded or overlapping takes (a section re-cut, a take dropped in the")
            print("> final assembly). Timings are not trustworthy and some text below may not")
            print("> be in the video. Chapter timestamps MUST come from `chapter_index.sh`.")

    print("\n## Parts\n")
    print("| # | part | words | span | source |")
    print("|---|------|-------|------|--------|")
    for i, (name, t) in enumerate(parts, 1):
        span = f"{fmt_secs(t['start'])}–{fmt_secs(t['end'])}"
        print(f"| {i} | {name} | {t['n_words']} | {span} | `{t['path'].name}` |")

    print("\n> Part order above is filesystem order (parent first, then sections A→Z).")
    print("> It is NOT guaranteed to be the order on the final timeline — confirm the")
    print("> running order against the video before you write chapters.\n")

    for i, (name, t) in enumerate(parts, 1):
        print(f"\n## Part {i} — {name}\n")
        print(t["text"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
