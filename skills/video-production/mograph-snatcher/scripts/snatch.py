# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Frame tooling for mograph-snatcher.

  download <url> <root>                        -> root/<video-id>/source.mp4 + meta.json
  scan     <workdir> [--every 2] [--until S]   -> workdir/scan/sheet-NN.jpg (labeled contact sheets)
  dense    <workdir> <id> <start> <end> [--fps 6] -> workdir/segments/<id>/{clip.mp4, frames/, sheet-NN.jpg}
"""
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

COLS, ROWS, THUMB_W = 5, 4, 384


def run(cmd):
    subprocess.run(cmd, check=True)


def tc(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:05.2f}"


def font(size):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", size)
    except OSError:
        return ImageFont.load_default()


def contact_sheets(frames, out_dir, prefix="sheet"):
    """frames: list of (time, path). Writes labeled grids of COLS x ROWS."""
    out_dir.mkdir(parents=True, exist_ok=True)
    f = font(20)
    per = COLS * ROWS
    sheets = []
    for n, i in enumerate(range(0, len(frames), per), start=1):
        chunk = frames[i:i + per]
        thumbs = []
        for t, p in chunk:
            im = Image.open(p).convert("RGB")
            im = im.resize((THUMB_W, round(im.height * THUMB_W / im.width)))
            d = ImageDraw.Draw(im)
            label = tc(t)
            d.rectangle([0, 0, 12 * len(label) + 12, 28], fill="black")
            d.text((6, 3), label, fill="yellow", font=f)
            thumbs.append(im)
        th = thumbs[0].height
        sheet = Image.new("RGB", (COLS * THUMB_W, ROWS * th), "black")
        for k, im in enumerate(thumbs):
            sheet.paste(im, ((k % COLS) * THUMB_W, (k // COLS) * th))
        path = out_dir / f"{prefix}-{n:02d}.jpg"
        sheet.save(path, quality=85)
        sheets.append(str(path))
    return sheets


def extract(src, out_dir, fps, start=0.0, end=None):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("f-*.jpg"):
        old.unlink()
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(src)]
    if end is not None:
        cmd += ["-t", str(end - start)]
    cmd += ["-vf", f"fps={fps},scale='min(1280,iw)':-2", "-q:v", "3", str(out_dir / "f-%05d.jpg")]
    run(cmd)
    files = sorted(out_dir.glob("f-*.jpg"))
    return [(start + k / fps, p) for k, p in enumerate(files)]


def cmd_download(a):
    vid = subprocess.run(["yt-dlp", "--ignore-config", "--no-playlist", "--print", "id", a.url],
                         check=True, capture_output=True, text=True).stdout.strip()
    w = Path(a.root) / vid
    w.mkdir(parents=True, exist_ok=True)
    run(["yt-dlp", "--ignore-config", "--no-playlist",
         "-f", "bv*[height<=1080]+ba/b[height<=1080]", "--merge-output-format", "mp4",
         "--write-info-json", "-o", str(w / "source.%(ext)s"), a.url])
    info = json.loads((w / "source.info.json").read_text())
    meta = {k: info.get(k) for k in ("id", "title", "channel", "duration", "webpage_url", "width", "height", "fps")}
    (w / "meta.json").write_text(json.dumps(meta, indent=2))
    (w / "source.info.json").unlink()
    print(json.dumps({"workdir": str(w), **meta}, indent=2))


def cmd_scan(a):
    w = Path(a.workdir)
    frames = extract(w / "source.mp4", w / "scan" / "frames", 1 / a.every, 0.0, a.until)
    sheets = contact_sheets(frames, w / "scan")
    print(json.dumps({"frames": len(frames), "every": a.every, "sheets": sheets}, indent=2))


def cmd_dense(a):
    w = Path(a.workdir)
    seg = w / "segments" / a.id
    seg.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.start), "-i", str(w / "source.mp4"),
         "-t", str(a.end - a.start), "-c:v", "libx264", "-crf", "18", "-an", str(seg / "clip.mp4")])
    frames = extract(w / "source.mp4", seg / "frames", a.fps, a.start, a.end)
    sheets = contact_sheets(frames, seg)
    print(json.dumps({"segment": str(seg), "frames": len(frames), "sheets": sheets}, indent=2))


p = argparse.ArgumentParser()
sub = p.add_subparsers(required=True)
d = sub.add_parser("download"); d.add_argument("url"); d.add_argument("root"); d.set_defaults(fn=cmd_download)
s = sub.add_parser("scan"); s.add_argument("workdir"); s.add_argument("--every", type=float, default=2); s.add_argument("--until", type=float); s.set_defaults(fn=cmd_scan)
x = sub.add_parser("dense"); x.add_argument("workdir"); x.add_argument("id")
x.add_argument("start", type=float); x.add_argument("end", type=float)
x.add_argument("--fps", type=float, default=6); x.set_defaults(fn=cmd_dense)
a = p.parse_args()
a.fn(a)
