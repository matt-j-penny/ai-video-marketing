#!/usr/bin/env python3
"""
TikTok/raw caption + hook-card builder  (LOCKED PRESET — see presets/tiktok-raw-style.md)

Two overlays, dead simple, no animation:
  1. HOOK CARD  — one static white box / black Inter text, pinned top, shown only
                  over the spoken hook line.
  2. CAPTIONS   — line-by-line white Inter + black stroke, no box, no animation,
                  parked low under the face. Each line holds until the next one replaces it.

Source of truth = the canonical cut transcript outputs/<job>.transcript.json (transcribe-once,
remapped through cuts.json). We NEVER re-transcribe. Renders PIL PNGs and overlays them with
ffmpeg (this ffmpeg has no drawtext/libass — PIL is the house pattern).

Usage:
  python3 presets/tiktok-raw/build.py <job_dir> [--until SECONDS] [--hook-end SECONDS]
                                       [--hook-text "...."] [--out PATH]
"""
import argparse, json, os, platform, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
# Windows consoles/pipes default to cp1252, which can't encode the → glyphs in this
# script's status lines: a cosmetic print must never kill a pipeline step (it did once,
# 2026-08-13, mid-splice on a real Windows job). Force UTF-8; no-op on macOS/Linux.
for _s in (sys.stdout, sys.stderr):
    try:
        if (getattr(_s, "encoding", "") or "").lower().replace("-", "") != "utf8":
            _s.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

# ---------------------------------------------------------------- layout (LOCKED)
W, H = 1080, 1920
SAFE_TOP, SAFE_BOT = 200, 1620          # no key visuals outside this band (platform UI / chrome)

FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "fonts", "Inter-Bold.otf")   # bundled Inter (no system-font dependency)
FALLBACK_FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "fonts", "Inter-Bold.otf")  # if SFNS.ttf is absent (non-standard macOS)
HOOK_WEIGHT = "Semibold"                # hook card = Inter Semibold
CAP_WEIGHT  = "Semibold"                # captions  = Inter Semibold

# hook card
HOOK_SIZE      = 64
HOOK_TOP_Y     = 250                    # box top (just below the 200px safe band)
HOOK_BOX_W     = 940                    # box max width (centered → 70px side margins)
HOOK_PAD_X     = 32                     # white margin hugging the text (box sized to ink, not metrics)
HOOK_PAD_Y     = 20
HOOK_RADIUS    = 22
HOOK_LINE_GAP  = 10
HOOK_FILL      = (255, 255, 255, 255)   # white box
HOOK_TEXT_COL  = (0, 0, 0, 255)         # black text

# captions
CAP_SIZE       = 42                     # 30% smaller than the original 60
CAP_CENTER_Y   = 1500                   # vertical center of the caption block (low, under the face)
CAP_MAX_W      = 960                    # wrap width
CAP_MAX_CHARS  = 20                     # soft cap → keeps each line short (≈3-4 words)
CAP_MAX_WORDS  = 4
CAP_STROKE     = 4
CAP_TEXT_COL   = (255, 255, 255, 255)   # white
CAP_STROKE_COL = (0, 0, 0, 255)         # black stroke
CAP_LINE_GAP   = 8
CAP_HOLD_PAD   = 0.40                   # last line lingers this long after the final word

# empty = no hook card unless --hook-text is passed (the documented contract:
# every locked per-job invocation passes it explicitly; clipper passes "")
DEFAULT_HOOK_TEXT = ""  # set per job via --hook-text (see brand-kit.md)

# ---------------------------------------------------------------- corrections
def load_corrections(repo_root):
    merged = {}
    cpath = os.path.join(repo_root, "presets", "caption-corrections.json")
    if os.path.exists(cpath):
        merged.update(json.load(open(cpath)).get("auto", {}))
    # Add your brand/product name fixes to presets/caption-corrections.json (loaded above).
    return merged

_token = re.compile(r"^(\W*)(.*?)(\W*)$", re.DOTALL)
def correct(word, table):
    pre, core, suf = _token.match(word).groups()
    if not core:
        return word
    hit = table.get(core.lower())
    return f"{pre}{hit}{suf}" if hit else word

# ---------------------------------------------------------------- fonts
def load_font(size, weight):
    try:
        f = ImageFont.truetype(FONT_PATH, size)
    except OSError:
        f = ImageFont.truetype(FALLBACK_FONT, size)   # SFNS.ttf absent → bundled Inter Bold
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f

# ---------------------------------------------------------------- chunking
SENT_END = (".", "?", "!", "…")
def chunk_lines(words, hook_end):
    """all words → list of {text,start,end}. Captions are always on (the hook card just
    overlays on top during the hook). Each line holds until the next begins."""
    post = list(words)
    lines, cur = [], []
    def flush():
        if cur:
            lines.append({
                "text": " ".join(w["disp"] for w in cur),
                "start": cur[0]["start"],
                "end": cur[-1]["end"],
                "nwords": len(cur),
                "rawdur": cur[-1]["end"] - cur[0]["start"],
            })
            cur.clear()
    for w in post:
        cur.append(w)
        joined = " ".join(x["disp"] for x in cur)
        ends_sentence = w["disp"].rstrip().endswith(SENT_END)
        if ends_sentence or len(cur) >= CAP_MAX_WORDS or len(joined) >= CAP_MAX_CHARS:
            flush()
    flush()
    # drop sub-0.2s single-word slivers — clip-boundary false-start tails, not real captions
    lines = [ln for ln in lines if not (ln["nwords"] == 1 and ln["rawdur"] < 0.20)]
    # hold each line until the next one starts (no flicker / no gaps mid-speech)
    for i in range(len(lines) - 1):
        lines[i]["end"] = lines[i + 1]["start"]
    if lines:
        lines[-1]["end"] = lines[-1]["end"] + CAP_HOLD_PAD
    return lines

# ---------------------------------------------------------------- wrapping
def wrap_to_width(text, font, max_w, draw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = wd
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- rendering
def render_caption(text, font, draw_probe):
    lines = wrap_to_width(text, font, CAP_MAX_W, draw_probe)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    asc, desc = font.getmetrics()
    lh = asc + desc + CAP_LINE_GAP
    total_h = lh * len(lines)
    y = CAP_CENTER_Y - total_h / 2
    for ln in lines:
        d.text((W / 2, y), ln, font=font, fill=CAP_TEXT_COL, anchor="ma",
               stroke_width=CAP_STROKE, stroke_fill=CAP_STROKE_COL)
        y += lh
    return crop(img)

def render_hook(text, font):
    inner_w = HOOK_BOX_W - 2 * HOOK_PAD_X
    probe = ImageDraw.Draw(Image.new("RGBA", (W, H)))
    lines = []
    for para in text.split("\n"):
        lines += wrap_to_width(para, font, inner_w, probe) or [""]
    asc, desc = font.getmetrics()
    lh = asc + desc + HOOK_LINE_GAP
    # draw text on a scratch layer, then size the box to the ACTUAL ink extents
    # (not font ascent/descent) so the white box hugs the text instead of ballooning.
    scratch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scratch)
    y = 120
    for ln in lines:
        sd.text((W / 2, y), ln, font=font, fill=HOOK_TEXT_COL, anchor="ma")
        y += lh
    bb = scratch.getbbox()
    if bb is None:
        # No ink (empty / whitespace-only hook). Without this guard scratch.crop(None)
        # returns the WHOLE 1080x1920 frame, ballooning the box to cover the footage.
        return crop(Image.new("RGBA", (W, H), (0, 0, 0, 0)))
    text_crop = scratch.crop(bb)
    box_w = text_crop.width + 2 * HOOK_PAD_X
    box_h = text_crop.height + 2 * HOOK_PAD_Y
    box_x = (W - box_w) // 2
    box_y = HOOK_TOP_Y
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h], radius=HOOK_RADIUS, fill=HOOK_FILL)
    out.alpha_composite(text_crop, (box_x + HOOK_PAD_X, box_y + HOOK_PAD_Y))
    assert box_y >= SAFE_TOP, "hook card crosses the top safe band"
    return crop(out)

def crop(img):
    bb = img.getbbox()
    if not bb:
        return img, 0, 0
    l, t, r, b = bb
    l, t = max(0, l - 4), max(0, t - 4)
    r, b = min(W, r + 4), min(H, b + 4)
    return img.crop((l, t, r, b)), l, t

# ---------------------------------------------------------------- ffmpeg
def build(job_dir, until, hook_end_override, hook_text, out_path):
    job_dir = os.path.abspath(job_dir)
    job = os.path.basename(job_dir)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    src = os.path.join(job_dir, "outputs", f"{job}.mp4")
    tj = os.path.join(job_dir, "outputs", f"{job}.transcript.json")
    assert os.path.exists(src), f"missing render: {src}"
    assert os.path.exists(tj), f"missing transcript: {tj}"
    src_dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nk=1:nw=1", src]).decode().strip())

    table = load_corrections(repo_root)
    words = json.load(open(tj))["words"]
    for w in words:
        w["disp"] = correct(w["text"], table)

    # hook end = end of the last hook word (auto: first 'larp/lark', else first sentence break)
    if hook_end_override is not None:
        hook_end = hook_end_override
    else:
        hook_end = None
        for w in words:
            if w["text"].lower().strip(".,?!").startswith(("lark", "larp")):
                hook_end = w["end"] + 0.10; break
        if hook_end is None:
            for w in words:
                if w["text"].rstrip().endswith(SENT_END):
                    hook_end = w["end"] + 0.10; break
        hook_end = hook_end or 5.0

    work = f"/tmp/video-editor/{job}/tiktok-raw"
    os.makedirs(work, exist_ok=True)
    os.system(f"rm -f {work}/*.png")

    cap_font = load_font(CAP_SIZE, CAP_WEIGHT)
    hook_font = load_font(HOOK_SIZE, HOOK_WEIGHT)
    probe = ImageDraw.Draw(Image.new("RGBA", (W, H)))

    overlays = []   # (png_path, x, y, start, end)

    # hook card — skip entirely when there's no hook text (e.g. an unset DEFAULT_HOOK_TEXT),
    # so an empty hook is a clean no-op (captions still run) instead of a frame-covering box.
    if hook_text and hook_text.strip():
        himg, hx, hy = render_hook(hook_text, hook_font)
        hp = os.path.join(work, "hook.png"); himg.save(hp)
        overlays.append((hp, hx, hy, 0.0, hook_end))

    # captions
    lines = chunk_lines(words, hook_end)
    if until:
        lines = [ln for ln in lines if ln["start"] < until]
    for i, ln in enumerate(lines):
        img, x, y = render_caption(ln["text"], cap_font, probe)
        p = os.path.join(work, f"cap_{i:03d}.png"); img.save(p)
        end = min(ln["end"], until) if until else ln["end"]
        overlays.append((p, x, y, ln["start"], end))

    # ffmpeg overlay chain
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", src]
    for ov in overlays:
        cmd += ["-loop", "1", "-i", ov[0]]
    fc, last = [], "0:v"
    for idx, ov in enumerate(overlays, start=1):
        _, x, y, s, e = ov
        nxt = f"v{idx}"
        fc.append(f"[{last}][{idx}:v]overlay={x}:{y}:enable='between(t,{s:.3f},{e:.3f})'[{nxt}]")
        last = nxt
    filter_complex = ";".join(fc)
    # ALWAYS bound the output: the -loop 1 image inputs never EOF, so without -t the render
    # runs away past the base video. Cap at the preview length, else the source duration.
    tcap = min(until, src_dur) if until else src_dur
    cmd += ["-filter_complex", filter_complex, "-map", f"[{last}]", "-map", "0:a",
            "-t", f"{tcap:.3f}"]
    # Apple HW encoder on macOS; libx264 everywhere else (Windows/Linux) — see splice.sh.
    if platform.system() == "Darwin":
        venc = ["-c:v", "h264_videotoolbox", "-b:v", "10M"]
    else:
        venc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"]
    # audio is unfiltered (mapped straight from the base cut) — stream-copy it;
    # re-encoding here was a second lossy AAC generation below the splice's 256k
    cmd += [*venc, "-c:a", "copy",
            "-movflags", "+faststart", out_path]

    print(f"[tiktok-raw] hook_end={hook_end:.2f}s  caption_lines={len(lines)}  overlays={len(overlays)}")
    print(f"[tiktok-raw] rendering → {out_path}")
    subprocess.run(cmd, check=True)
    print(f"[tiktok-raw] done: {out_path}")
    # echo the caption sheet for review
    for i, ln in enumerate(lines):
        print(f"  {ln['start']:6.2f}-{ln['end']:6.2f}  {ln['text']}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("job_dir")
    ap.add_argument("--until", type=float, default=None, help="preview length cap (seconds)")
    ap.add_argument("--hook-end", type=float, default=None, help="override hook card end (seconds)")
    ap.add_argument("--hook-text", default=DEFAULT_HOOK_TEXT)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    job = os.path.basename(os.path.abspath(a.job_dir))
    out = a.out or f"/tmp/video-editor/{job}/tiktok-raw/preview.mp4"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(a.job_dir, a.until, a.hook_end, a.hook_text, out)
