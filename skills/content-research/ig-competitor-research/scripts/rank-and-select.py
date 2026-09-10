#!/usr/bin/env python3
"""rank-and-select.py — rank scraped IG posts, then prep job dirs + media.

usage:
    python3 rank-and-select.py <dataset.json> <run_dir> [--per-handle 3] [--expect h1,h2,h3] [--expect-count N]

<dataset.json>  the `get-dataset-items` result the MCP tool saved to disk (the
                one combined media-inclusive read). Shape: {"items":[...]} or a
                bare list of items. No Apify call happens here — this is pure
                local processing, stdlib only (no uv, no pillow).
<run_dir>       /tmp/ig-research/<RUN>/  where <RUN> = YYYY-MM-DD_HHMMSS
                (e.g. /tmp/ig-research/2026-06-03_153012/)

Ranks every post by LIKES (hidden -1 sorts last, ties broken by comments),
keeps the top N per handle, pools, sorts the whole set high-to-low, and writes:

  <run_dir>/selection.json                    the ordered picks (meta only)
  <run_dir>/<rank>_<handle>/videourl.txt      reels/videos  (the muxed videoUrl)
  <run_dir>/<rank>_<handle>/imageurls.txt     carousels/images (one URL per line)
  (e.g. <run_dir>/1_handle_a/imageurls.txt)

Prints a ranked table to stderr and flags any pick whose media URL is missing,
plus any --expect handle that returned nothing in the window. The orchestrator
reads selection.json to fan out the subagents — it never has to sort, format a
date, or touch a giant media blob itself.
"""
import sys, os, json, argparse, re, statistics
from datetime import datetime


def load_items(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("items", []) if isinstance(data, dict) else data


def fmt_count(n):
    """Comma-formatted integer; hidden likes (-1) -> 'hidden'."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "hidden"
    return "hidden" if n < 0 else f"{n:,}"


def fmt_date(ts):
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        try:
            dt = datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return str(ts)[:10]
    return f"{dt.strftime('%b')} {dt.day}, {dt.year}"


def post_format(item):
    t = (item.get("type") or "").lower()
    pt = (item.get("productType") or "").lower()
    if t == "sidecar":
        return "Carousel"
    if t == "image":
        return "Image"
    if t == "video":
        return "Reel" if pt == "clips" else "Video"
    return "Reel"  # default branch: treat unknowns as a reel


def rank_key(item):
    """Sort ascending puts the best first: non-hidden, then likes desc, comments desc."""
    likes = item.get("likesCount", -1)
    try:
        likes = int(likes)
    except (TypeError, ValueError):
        likes = -1
    comments = item.get("commentsCount", 0) or 0
    try:
        comments = int(comments)
    except (TypeError, ValueError):
        comments = 0
    return (likes < 0, -(max(likes, 0)), -comments)


def safe_handle(h):
    return re.sub(r"[^A-Za-z0-9._-]", "_", h or "unknown")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset")
    ap.add_argument("date_root")
    ap.add_argument("--per-handle", type=int, default=3)
    ap.add_argument("--expect", default="")
    ap.add_argument("--expect-count", default="",
                    help="hard-fail unless the dataset holds exactly this many items "
                         "(guards the get-dataset-items-to-disk write against a dropped record); "
                         "a non-numeric value (e.g. 'null' from an envelope with no itemCount) skips the guard")
    args = ap.parse_args()

    items = load_items(args.dataset)
    if not items:
        print("[error] dataset has no items", file=sys.stderr)
        sys.exit(1)
    expect_count = 0
    if args.expect_count.strip():
        try:
            expect_count = int(args.expect_count.strip())
        except ValueError:
            print(f"[note] --expect-count={args.expect_count!r} is not a number; skipping the item-count guard",
                  file=sys.stderr)
    if expect_count and len(items) != expect_count:
        print(f"[error] dataset.json holds {len(items)} items but --expect-count={expect_count}. "
              f"A record was dropped or garbled writing the get-dataset-items result to disk — "
              f"re-fetch via the MCP and rewrite dataset.json verbatim before re-running.",
              file=sys.stderr)
        sys.exit(1)

    # restrict to the requested roster: the actor occasionally returns a stray
    # handle (a tagged or collab post), and --expect is authoritative here — not
    # just a missing-flag. Empty --expect (no roster passed) keeps everything.
    expected = [h.strip().lstrip("@").lower() for h in args.expect.split(",") if h.strip()]
    if expected:
        items = [it for it in items if (it.get("ownerUsername") or "unknown").lower() in expected]
        if not items:
            print(f"[error] no posts match --expect handles ({', '.join(expected)}) — "
                  f"check the handles or the scrape", file=sys.stderr)
            sys.exit(1)

    # group by handle
    by_handle = {}
    for it in items:
        h = it.get("ownerUsername") or "unknown"
        by_handle.setdefault(h, []).append(it)

    # per-handle baseline = median likes across that handle's non-hidden posts in
    # the window. A pick's breakout score = its likes / this baseline, so a small
    # account's overperformer isn't buried under a big account's median-level post.
    def likes_int(it):
        try:
            return int(it.get("likesCount", -1))
        except (TypeError, ValueError):
            return -1

    baseline = {}
    for h, posts in by_handle.items():
        vals = [v for v in (likes_int(p) for p in posts) if v >= 0]
        baseline[h] = statistics.median(vals) if vals else 0

    # top N per handle, then pool + global sort
    picks = []
    for h, posts in by_handle.items():
        posts.sort(key=rank_key)
        picks.extend(posts[: args.per_handle])
    picks.sort(key=rank_key)

    os.makedirs(args.date_root, exist_ok=True)
    selection, warnings, rows = [], [], []

    for i, it in enumerate(picks, start=1):
        handle = it.get("ownerUsername") or "unknown"
        fmt = post_format(it)
        jobdir = os.path.join(args.date_root, f"{i}_{safe_handle(handle)}")
        os.makedirs(jobdir, exist_ok=True)

        if fmt in ("Carousel", "Image"):
            if fmt == "Carousel":
                urls = [u for u in (it.get("images") or []) if u]
            else:
                urls = [it["displayUrl"]] if it.get("displayUrl") else []
            with open(os.path.join(jobdir, "imageurls.txt"), "w", encoding="utf-8") as f:
                f.write("\n".join(urls) + ("\n" if urls else ""))
            if not urls:
                warnings.append(f"#{i} @{handle} {fmt}: no image URLs in dataset")
            elif any(not u.startswith("http") for u in urls):
                warnings.append(f"#{i} @{handle} {fmt}: an image URL looks malformed — re-check the dataset write")
        else:  # Reel / Video
            vurl = it.get("videoUrl") or ""
            with open(os.path.join(jobdir, "videourl.txt"), "w", encoding="utf-8") as f:
                f.write(vurl + ("\n" if vurl else ""))
            if not vurl:
                warnings.append(f"#{i} @{handle} {fmt}: no videoUrl in dataset — this reel can't be downloaded")
            elif not vurl.startswith("http"):
                warnings.append(f"#{i} @{handle} {fmt}: videoUrl looks malformed — re-check the dataset write")

        likes = fmt_count(it.get("likesCount", -1))
        comments = fmt_count(it.get("commentsCount", 0))
        date = fmt_date(it.get("timestamp", ""))
        url = it.get("url") or ""

        # breakout score: this post's likes vs its handle's weekly median
        lk, base = likes_int(it), baseline.get(handle, 0)
        if lk >= 0 and base and base > 0:
            score = round(lk / base, 1)
            olabel = f"{score:g}×"
        else:
            score, olabel = None, "—"

        selection.append({
            "rank": i,
            "handle": handle,
            "shortCode": it.get("shortCode", ""),
            "format": fmt,
            "likes": likes,
            "comments": comments,
            "date": date,
            "url": url,
            "outlier_score": score,
            "outlier_label": olabel,
            "baseline": int(base) if base else 0,
            "jobdir": jobdir,
            "caption": (it.get("caption") or "").strip(),
        })
        cap = " ".join((it.get("caption") or "").split())[:44]
        rows.append(f"  #{i:<2} @{handle:<18} {fmt:<9} {likes:>9} likes  {olabel:>6} brk  {comments:>7} cmts  {date:<13} {cap}")

    with open(os.path.join(args.date_root, "selection.json"), "w", encoding="utf-8") as f:
        json.dump(selection, f, indent=2, ensure_ascii=False)

    # report
    print(f"[rank] {len(items)} posts scraped across {len(by_handle)} handle(s) "
          f"-> {len(selection)} picks (top {args.per_handle}/handle)", file=sys.stderr)
    for r in rows:
        print(r, file=sys.stderr)

    have = {h.lower() for h in by_handle}
    missing = [h for h in expected if h not in have]
    for h in missing:
        warnings.append(f"@{h}: no posts in the window — contributes 0")
    for w in warnings:
        print(f"[warn] {w}", file=sys.stderr)

    print(os.path.join(args.date_root, "selection.json"))


if __name__ == "__main__":
    main()
