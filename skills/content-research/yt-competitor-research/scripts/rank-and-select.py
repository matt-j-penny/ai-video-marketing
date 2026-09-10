#!/usr/bin/env python3
"""rank-and-select.py — rank yt-dlp video metadata, then prep job dirs.

usage:
    python3 rank-and-select.py <meta_dir> <run_dir> [--per-handle 3] [--days 7] [--expect h1,h2,h3]

<meta_dir>   <RUN_DIR>/meta/ — one subdir per handle, each holding the raw
             `yt-dlp -J` output as <videoId>.json. No network call happens
             here — pure local processing, stdlib only (no uv, no pillow).
<run_dir>    /tmp/yt-research/<RUN>/

Keeps only videos uploaded in the last --days days (the orchestrator pulls a
20-newest buffer per channel; this is where the week window is enforced),
ranks the survivors by VIEWS (ties broken by likes), keeps the top N per
handle, pools, sorts the whole set high-to-low, and writes:

  <run_dir>/selection.json                    the ordered picks (meta only)
  <run_dir>/<rank>_<handle>/thumburl.txt      best jpg thumbnail URL
  <run_dir>/<rank>_<handle>/description.txt   full description, verbatim

Breakout score = views ÷ that channel's median views across its uploads in
the window (its weekly median), so a small channel's overperformer isn't
buried under a big channel's median-level video.

Prints a ranked table to stderr and flags unparseable fetches, null-view
videos (live/premiere), and any --expect handle with nothing in the window.
The orchestrator reads selection.json to fan out the subagents — it never
has to sort, format a count, or read a raw yt-dlp blob itself.
"""
import sys, os, json, glob, argparse, re, statistics
from datetime import datetime, timedelta


def fmt_short(n):
    """Human-readable count: 1.2M, 296K, 47.3K, 812."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "n/a"
    if n < 0:
        return "n/a"
    if n >= 999_500:  # would otherwise round to "1000K"
        v = n / 1_000_000
        return f"{v:.1f}M".replace(".0M", "M")
    if n >= 100_000:
        return f"{round(n / 1_000)}K"
    if n >= 1_000:
        v = n / 1_000
        return f"{v:.1f}K".replace(".0K", "K")
    return str(n)


def fmt_date(yyyymmdd):
    if not yyyymmdd:
        return ""
    try:
        dt = datetime.strptime(str(yyyymmdd), "%Y%m%d")
    except ValueError:
        return str(yyyymmdd)
    return f"{dt.strftime('%b')} {dt.day}, {dt.year}"


def fmt_duration(item):
    ds = item.get("duration_string")
    if ds:
        return str(ds)
    try:
        secs = int(item.get("duration") or 0)
    except (TypeError, ValueError):
        return ""
    if not secs:
        return ""
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def best_thumb(item):
    """Highest-res jpg from the thumbnails array; hqdefault as the floor."""
    thumbs = item.get("thumbnails") or []
    jpgs = [t for t in thumbs
            if t.get("url") and ".jpg" in t["url"].split("?")[0]]
    if jpgs:
        jpgs.sort(key=lambda t: (t.get("width") or 0, t.get("preference") or -9999))
        return jpgs[-1]["url"]
    if item.get("id"):
        return f"https://i.ytimg.com/vi/{item['id']}/hqdefault.jpg"
    return item.get("thumbnail") or ""


def views_int(item):
    try:
        v = item.get("view_count")
        return -1 if v is None else int(v)
    except (TypeError, ValueError):
        return -1


def likes_int(item):
    try:
        v = item.get("like_count")
        return -1 if v is None else int(v)
    except (TypeError, ValueError):
        return -1


def safe_handle(h):
    return re.sub(r"[^A-Za-z0-9._-]", "_", h or "unknown")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("meta_dir")
    ap.add_argument("run_dir")
    ap.add_argument("--per-handle", type=int, default=3)
    ap.add_argument("--days", type=int, default=7,
                    help="only keep videos uploaded within the last N days (the week window)")
    ap.add_argument("--expect", default="")
    args = ap.parse_args()

    expected = [h.strip().lstrip("@") for h in args.expect.split(",") if h.strip()]
    cutoff = (datetime.now() - timedelta(days=args.days)).strftime("%Y%m%d")

    # load: meta/<handle>/<id>.json, handle = parent dir name
    by_handle, warnings = {}, []
    outside_window = 0
    for path in sorted(glob.glob(os.path.join(args.meta_dir, "*", "*.json"))):
        handle = os.path.basename(os.path.dirname(path))
        try:
            with open(path, encoding="utf-8") as f:
                item = json.load(f)
        except Exception:
            warnings.append(f"@{handle}: {os.path.basename(path)} unparseable — fetch failed, skipped")
            continue
        if not isinstance(item, dict) or not item.get("id"):
            warnings.append(f"@{handle}: {os.path.basename(path)} has no video data, skipped")
            continue
        if views_int(item) < 0:
            # live streams / premieres report null views until they end
            warnings.append(f"@{handle}: \"{(item.get('title') or '')[:40]}\" has no view count (live/premiere?), skipped")
            continue
        ud = str(item.get("upload_date") or "")
        if not ud:
            warnings.append(f"@{handle}: \"{(item.get('title') or '')[:40]}\" has no upload date, skipped")
            continue
        if ud < cutoff:
            # older than the window — expected, since the fetch pulls a 20-newest buffer
            outside_window += 1
            continue
        by_handle.setdefault(handle, []).append(item)

    if not by_handle:
        print(f"[error] no videos within the last {args.days} days across any channel — "
              f"either a quiet week everywhere or the yt-dlp fetch step failed", file=sys.stderr)
        sys.exit(1)

    # per-channel baseline = median views across its uploads in the window
    # (its weekly median), mirroring the IG skill's per-creator baseline
    baseline = {h: statistics.median(views_int(v) for v in vids)
                for h, vids in by_handle.items()}

    # top N per handle by views (likes break ties), then pool + global sort
    def rank_key(item):
        return (-views_int(item), -max(likes_int(item), 0))

    picks = []
    for h, vids in by_handle.items():
        vids.sort(key=rank_key)
        picks.extend((h, v) for v in vids[: args.per_handle])
    picks.sort(key=lambda hv: rank_key(hv[1]))

    os.makedirs(args.run_dir, exist_ok=True)
    selection, rows = [], []

    for i, (handle, it) in enumerate(picks, start=1):
        jobdir = os.path.join(args.run_dir, f"{i}_{safe_handle(handle)}")
        os.makedirs(jobdir, exist_ok=True)

        thumb = best_thumb(it)
        with open(os.path.join(jobdir, "thumburl.txt"), "w", encoding="utf-8") as f:
            f.write(thumb + ("\n" if thumb else ""))
        if not thumb:
            warnings.append(f"#{i} @{handle}: no thumbnail URL — subagent must analyze title only")

        with open(os.path.join(jobdir, "description.txt"), "w", encoding="utf-8") as f:
            f.write((it.get("description") or "").strip() + "\n")

        views, likes = views_int(it), likes_int(it)
        like_rate = f"{likes / views * 100:.1f}%" if likes >= 0 and views > 0 else "n/a"

        base = baseline.get(handle, 0)
        if base and base > 0:
            score = round(views / base, 1)
            olabel = f"{score:g}×"
        else:
            score, olabel = None, "—"

        title = (it.get("title") or "").strip()
        date = fmt_date(it.get("upload_date"))
        selection.append({
            "rank": i,
            "handle": handle,
            "id": it.get("id", ""),
            "title": title,
            "views": fmt_short(views),
            "views_raw": views,
            "likes": fmt_short(likes),
            "like_rate": like_rate,
            "date": date,
            "duration": fmt_duration(it),
            "url": it.get("webpage_url") or f"https://www.youtube.com/watch?v={it.get('id','')}",
            "outlier_score": score,
            "outlier_label": olabel,
            "baseline": fmt_short(base),
            "jobdir": jobdir,
        })
        rows.append(f"  #{i:<2} @{handle:<22} {fmt_short(views):>7} views  {olabel:>6} brk  "
                    f"{fmt_short(likes):>6} likes  {like_rate:>5}  {date:<13} {fmt_duration(it):>8}  {title[:44]}")

    with open(os.path.join(args.run_dir, "selection.json"), "w", encoding="utf-8") as f:
        json.dump(selection, f, indent=2, ensure_ascii=False)

    total = sum(len(v) for v in by_handle.values())
    print(f"[rank] {total} videos in the last {args.days} days across {len(by_handle)} channel(s) "
          f"({outside_window} older candidates dropped) "
          f"-> {len(selection)} picks (top {args.per_handle}/channel, ranked by views)", file=sys.stderr)
    for r in rows:
        print(r, file=sys.stderr)

    for h in expected:
        if h not in by_handle:
            warnings.append(f"@{h}: no videos in the window — contributes 0")
    for w in warnings:
        print(f"[warn] {w}", file=sys.stderr)

    print(os.path.join(args.run_dir, "selection.json"))


if __name__ == "__main__":
    main()
