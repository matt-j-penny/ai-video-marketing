#!/usr/bin/env python3
"""build-report.py — render a self-contained HTML competitor-research report.

usage:
    bash <SKILL_DIR>/scripts/build-report.sh <RUN_DIR | manifest.json> <out.html> [--open]

build-report.sh runs this file on the shared build-once pillow venv
(~/.cache/content-os/pillow-venv; CONTENT_OS_PILLOW_VENV overrides). The wrapper
is the one path; don't invoke this file with a per-run dependency resolver.

Per-post media is read straight from each post's `jobdir` (slide_*.jpg for
carousels/images, frame_*.jpg for reels), downscaled, and base64-embedded so the
output is ONE portable file that never breaks — no asset folder, no expiring CDN
links.

Manifest schema:
{
  "generated": "2026-06-03",
  "accounts_scraped": 5,
  "posts_count": 15,
  "window": "last 7 days",
  "pattern": "…synthesis paragraph…",
  "posts": [
    {
      "rank": 1, "handle": "handle_a", "format": "Carousel",
      "likes": "2,749", "comments": "4,272", "date": "May 29, 2026",
      "outlier_label": "3.6×", "outlier_score": 3.6, "baseline": 760,
      "url": "https://www.instagram.com/p/…/",
      "jobdir": "/tmp/ig-research/2026-06-03_153012/1_handle_a",
      "hook": "…",                 // the opening hook (spoken line or on-screen text)
      "hook_type": "",            // "spoken" | "on-screen text" | "spoken + text"
      "content_format": "",       // talking head, listicle, side-by-side, reaction, …
      "breakdown": "",            // one-sentence concept of the whole post
      "transcript": "",           // reels: full transcript · carousels: all slide text
      "why": "…"
    }
  ]
}
"""
import sys, os, json, glob, base64, html, io, webbrowser

MAXW = 760          # downscale width for embedded media
JPEG_Q = 72


def embed(path):
    """Return a base64 data-URI for an image, downscaled to MAXW wide."""
    try:
        from PIL import Image
        im = Image.open(path)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        if im.width > MAXW:
            h = round(im.height * MAXW / im.width)
            im = im.resize((MAXW, h), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=JPEG_Q, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/jpeg;base64,{b64}"
    except Exception as e:  # noqa
        print(f"[warn] could not embed {path}: {e}", file=sys.stderr)
        return None


def media_files(post):
    jd = post.get("jobdir", "")
    fmt = post.get("format", "").lower()
    if fmt in ("carousel", "image"):
        files = sorted(glob.glob(os.path.join(jd, "slide_*.jpg")))
    else:  # reel / video
        files = sorted(glob.glob(os.path.join(jd, "frame_*.jpg")))
    return [f for f in files if os.path.isfile(f)]


def image_size(path):
    """Return (width, height) for an image, or None."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.width, im.height
    except Exception:  # noqa
        return None


def gallery_html(post):
    files = media_files(post)
    pairs = [(f, u) for f, u in ((f, embed(f)) for f in files) if u]
    if not pairs:
        return '<div class="gallery empty"><span>media unavailable</span></div>'
    n = len(pairs)
    # Hug the real media aspect ratio so reels (9:16) and square carousels (1:1)
    # don't get letterboxed inside a fixed box. The container adopts the first
    # frame/slide's ratio; with object-fit:contain that means no black bars.
    ar_style = ""
    sz = image_size(pairs[0][0])
    if sz and sz[0] and sz[1]:
        ar_style = f' style="aspect-ratio:{sz[0]}/{sz[1]}"'
    imgs = "".join(f'<img loading="lazy" src="{u}" alt="">' for _, u in pairs)
    multi = n > 1
    nav = (
        '<button class="nav prev" aria-label="previous">‹</button>'
        '<button class="nav next" aria-label="next">›</button>'
        f'<span class="counter">1 / {n}</span>'
        '<div class="dots">' + "".join(
            f'<span class="dot{" active" if i == 0 else ""}"></span>' for i in range(n)
        ) + "</div>"
    ) if multi else ""
    return f'<div class="gallery" data-n="{n}"{ar_style}><div class="track">{imgs}</div>{nav}</div>'


def post_card(p):
    fmt = p.get("format", "")
    fmt_l = fmt.lower()
    rank = p.get("rank", "")
    badge_cls = "badge gold" if rank == 1 else "badge"
    bits = []
    bits.append('<article class="card">')
    bits.append(f'<div class="rank"><span class="{badge_cls}">#{rank}</span></div>')
    bits.append('<div class="media-col">')
    bits.append(gallery_html(p))
    bits.append(f'<a class="ig-btn" href="{html.escape(p.get("url") or "")}" target="_blank" rel="noopener">▶ View on Instagram</a>')
    bits.append("</div>")

    bits.append('<div class="info">')
    bits.append('<div class="meta-row">')
    bits.append(f'<span class="handle">@{html.escape(p.get("handle",""))}</span>')
    bits.append(f'<span class="tag tag-{fmt_l}">{html.escape(fmt)}</span>')
    bits.append("</div>")
    bits.append('<div class="pills">')
    bits.append(f'<span class="pill likes">♥ {html.escape(str(p.get("likes","")))}</span>')
    olabel = (p.get("outlier_label") or "").strip()
    if olabel and olabel != "—":
        try:
            score = float(p.get("outlier_score") or 0)
        except (TypeError, ValueError):
            score = 0
        heat = "hot" if score >= 3 else ("warm" if score >= 1.5 else "cool")
        emoji = "🔥 " if heat == "hot" else ""
        title = (f'{p.get("likes","")} likes vs @{p.get("handle","")}\'s '
                 f'{p.get("baseline","")} median this week')
        bits.append(f'<span class="pill breakout {heat}" title="{html.escape(title)}">{emoji}{html.escape(olabel)} breakout</span>')
    bits.append(f'<span class="pill comments">💬 {html.escape(str(p.get("comments","")))}</span>')
    bits.append(f'<span class="pill date">{html.escape(p.get("date",""))}</span>')
    bits.append("</div>")

    hook = p.get("hook", "").strip()
    if hook:
        htype = p.get("hook_type", "").strip()
        hk_label = f"Hook · {html.escape(htype)}" if htype else "Hook"
        bits.append(f'<div class="hook"><span class="lbl">{hk_label}</span><p>{html.escape(hook)}</p></div>')

    cfmt = p.get("content_format", "").strip()
    if cfmt:
        bits.append(f'<div class="fmt"><span class="lbl">Format</span><span class="chip">{html.escape(cfmt)}</span></div>')

    breakdown = p.get("breakdown", "").strip()
    if breakdown:
        bits.append(f'<div class="block"><span class="lbl">Breakdown</span><p>{html.escape(breakdown)}</p></div>')

    tr = p.get("transcript", "").strip()
    if tr:
        tr_label = "Slide Text" if fmt_l in ("carousel", "image") else "Transcript"
        bits.append(
            f'<details class="transcript"><summary><span class="lbl-inline">{tr_label}</span>'
            f'<button class="copy-btn" type="button">Copy</button></summary>'
            f'<p>{html.escape(tr)}</p></details>'
        )

    why = p.get("why", "").strip()
    if why:
        bits.append(f'<div class="why"><span class="lbl">Why it worked</span><p>{html.escape(why)}</p></div>')

    bits.append("</div>")   # .info
    bits.append("</article>")
    return "".join(bits)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0c0c0f;--surface:#15151b;--surface2:#1d1d25;--line:#2a2a34;
  --text:#ededf2;--muted:#9a9aa9;--accent:#fa5a8e;--accent2:#feaa54;
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);
  font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
  -webkit-font-smoothing:antialiased;padding:0 0 80px}
.wrap{max-width:1080px;margin:0 auto;padding:0 24px}
header{padding:56px 0 28px;border-bottom:1px solid var(--line);margin-bottom:36px}
.kicker{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);font-weight:700}
h1{font-size:40px;line-height:1.05;font-weight:800;letter-spacing:-.02em;margin:10px 0 18px}
.stats{display:flex;flex-wrap:wrap;gap:8px}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:999px;
  padding:6px 14px;font-size:13px;color:var(--muted)}
.stat b{color:var(--text);font-weight:700}
.pattern{background:linear-gradient(135deg,rgba(250,90,142,.12),rgba(254,170,84,.08));
  border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:14px;
  padding:20px 22px;margin-bottom:40px}
.pattern .lbl{display:block;font-size:12px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--accent);font-weight:700;margin-bottom:8px}
.pattern p{font-size:16px;color:#dcdce4}
.card{display:grid;grid-template-columns:44px 340px 1fr;gap:24px;align-items:start;
  background:var(--surface);border:1px solid var(--line);border-radius:18px;
  padding:22px;margin-bottom:22px}
.rank{position:sticky;top:18px}
.info{min-width:0}
.badge{display:grid;place-items:center;width:44px;height:44px;border-radius:12px;
  background:var(--surface2);border:1px solid var(--line);font-weight:800;font-size:16px}
.badge.gold{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#1a0b12;border:0}
.media-col{width:340px}
.gallery{position:relative;width:340px;aspect-ratio:4/5;background:var(--surface2);
  border-radius:14px;overflow:hidden;border:1px solid var(--line)}
.gallery.empty{display:grid;place-items:center;color:var(--muted);font-size:13px}
.track{display:flex;width:100%;height:100%;overflow-x:auto;scroll-snap-type:x mandatory;
  scrollbar-width:none}
.track::-webkit-scrollbar{display:none}
.track img{flex:0 0 100%;width:100%;height:100%;object-fit:contain;scroll-snap-align:center}
.nav{position:absolute;top:50%;transform:translateY(-50%);z-index:2;width:34px;height:34px;
  border-radius:50%;border:0;background:rgba(0,0,0,.55);color:#fff;font-size:20px;
  cursor:pointer;display:grid;place-items:center;backdrop-filter:blur(4px);opacity:0;transition:.15s}
.gallery:hover .nav{opacity:1}
.nav.prev{left:8px}.nav.next{right:8px}
.counter{position:absolute;top:10px;right:10px;z-index:2;background:rgba(0,0,0,.6);
  color:#fff;font-size:12px;font-weight:600;padding:3px 9px;border-radius:999px;backdrop-filter:blur(4px)}
.dots{position:absolute;bottom:10px;left:0;right:0;display:flex;justify-content:center;gap:6px;z-index:2}
.dot{width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,.4)}
.dot.active{background:#fff;width:18px;border-radius:3px}
.ig-btn{display:block;text-align:center;margin-top:12px;padding:10px;border-radius:10px;
  background:var(--surface2);border:1px solid var(--line);color:var(--text);
  text-decoration:none;font-size:14px;font-weight:600;transition:.15s}
.ig-btn:hover{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#1a0b12;border-color:transparent}
.meta-row{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.handle{font-size:18px;font-weight:700}
.tag{font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;
  padding:4px 9px;border-radius:6px;background:var(--surface2);border:1px solid var(--line);color:var(--muted)}
.tag-carousel{color:#7bb8ff;border-color:#27405e}
.tag-reel,.tag-video{color:#ff9ec2;border-color:#5e2740}
.tag-image{color:#9affc4;border-color:#27543c}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}
.pill{font-size:13px;color:var(--muted);background:var(--surface2);border:1px solid var(--line);
  border-radius:999px;padding:4px 12px}
.pill.likes{color:#ff8fb3}
.pill.breakout{font-weight:700}
.pill.breakout.hot{color:#ff6a4d;border-color:#5e2e27;background:rgba(255,90,60,.12)}
.pill.breakout.warm{color:#feaa54;border-color:#5e4a27;background:rgba(254,170,84,.12)}
.pill.breakout.cool{color:#9a9aa9}
.lbl{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);font-weight:700;margin-bottom:6px}
.hook{margin-bottom:16px}
.hook p{font-size:20px;line-height:1.35;font-weight:700;letter-spacing:-.01em}
.fmt{margin-bottom:16px}
.fmt .chip{display:inline-block;font-size:14px;font-weight:700;color:var(--accent2);
  background:rgba(254,170,84,.1);border:1px solid rgba(254,170,84,.32);
  border-radius:8px;padding:5px 12px;text-transform:capitalize}
.block{margin-bottom:16px}
.block p{color:#d2d2dc}
.transcript{margin-bottom:16px;background:var(--surface2);border:1px solid var(--line);
  border-radius:10px;padding:0 14px}
.transcript summary{display:flex;align-items:center;cursor:pointer;padding:11px 0;font-size:13px;
  font-weight:600;color:var(--muted);list-style:none;letter-spacing:.04em;text-transform:uppercase}
.transcript summary::-webkit-details-marker{display:none}
.transcript summary:before{content:"▸";color:var(--accent);margin-right:9px}
.transcript[open] summary:before{content:"▾"}
.copy-btn{margin-left:auto;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--accent);background:var(--surface);border:1px solid var(--line);border-radius:7px;
  padding:4px 11px;cursor:pointer;transition:.15s}
.copy-btn:hover{background:var(--accent);color:#1a0b12;border-color:transparent}
.copy-btn.copied{background:#2faa6a;color:#06210f;border-color:transparent}
.transcript p{padding:0 0 14px;color:#c3c3cf;font-size:14.5px;overflow-wrap:anywhere}
.why{background:linear-gradient(135deg,rgba(250,90,142,.1),rgba(254,170,84,.06));
  border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.why .lbl{color:var(--accent)}
.why p{color:#e6e6ee}
footer{text-align:center;color:var(--muted);font-size:13px;margin-top:48px}
@media(max-width:760px){
  .card{grid-template-columns:1fr;gap:16px}
  .rank{position:static}.media-col,.gallery{width:100%}
  h1{font-size:30px}
}
"""

JS = """
document.querySelectorAll('.gallery[data-n]').forEach(function(g){
  var track=g.querySelector('.track'), counter=g.querySelector('.counter');
  var dots=[].slice.call(g.querySelectorAll('.dot'));
  var n=parseInt(g.getAttribute('data-n'),10);
  function idx(){return Math.round(track.scrollLeft/track.clientWidth);}
  function update(){var i=idx();if(counter)counter.textContent=(i+1)+' / '+n;
    dots.forEach(function(d,j){d.classList.toggle('active',j===i);});}
  track.addEventListener('scroll',function(){window.requestAnimationFrame(update);});
  var prev=g.querySelector('.prev'),next=g.querySelector('.next');
  if(prev)prev.addEventListener('click',function(){track.scrollBy({left:-track.clientWidth,behavior:'smooth'});});
  if(next)next.addEventListener('click',function(){track.scrollBy({left:track.clientWidth,behavior:'smooth'});});
  dots.forEach(function(d,j){d.addEventListener('click',function(){track.scrollTo({left:j*track.clientWidth,behavior:'smooth'});});});
});
document.querySelectorAll('.transcript .copy-btn').forEach(function(btn){
  btn.addEventListener('click',function(e){
    e.preventDefault();e.stopPropagation();
    var det=btn.closest('.transcript'),p=det?det.querySelector('p'):null;
    var text=p?p.textContent:'';
    function done(ok){btn.textContent=ok?'Copied!':'Copy failed';btn.classList.toggle('copied',ok);
      setTimeout(function(){btn.textContent='Copy';btn.classList.remove('copied');},1500);}
    function fallback(){try{var ta=document.createElement('textarea');ta.value=text;
      ta.style.position='fixed';ta.style.top='-9999px';document.body.appendChild(ta);
      ta.focus();ta.select();var ok=document.execCommand('copy');document.body.removeChild(ta);done(ok);
      }catch(err){done(false);}}
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(text).then(function(){done(true);},fallback);
    }else{fallback();}
  });
});
"""


def assemble_from_dateroot(date_root):
    """Build the manifest from a date_root dir instead of a pre-written file.

    selection.json (written by rank-and-select.py) is the AUTHORITY for the
    scraped facts — rank, handle, format, likes, comments, date, url, jobdir.
    Each <jobdir>/post.json (written by a subagent) supplies only the analysis —
    hook, hook_type, content_format, breakdown, transcript, why. pattern.txt
    holds the synthesis line.
    A pick whose post.json is missing/unreadable still renders (media + facts),
    flagged so the orchestrator can re-run just that one.
    """
    sel_path = os.path.join(date_root, "selection.json")
    with open(sel_path, encoding="utf-8") as f:
        selection = json.load(f)
    selection.sort(key=lambda p: p.get("rank", 0))

    pattern = ""
    pat_path = os.path.join(date_root, "pattern.txt")
    if os.path.isfile(pat_path):
        with open(pat_path, encoding="utf-8") as f:
            pattern = f.read().strip()

    posts, missing = [], []
    for s in selection:
        post = {k: s.get(k, "") for k in
                ("rank", "handle", "format", "likes", "comments", "date", "url", "jobdir",
                 "outlier_score", "outlier_label", "baseline")}
        pj = os.path.join(s.get("jobdir", ""), "post.json")
        analysis = {}
        if os.path.isfile(pj):
            try:
                with open(pj, encoding="utf-8") as f:
                    analysis = json.load(f)
            except Exception as e:  # noqa
                print(f"[warn] bad post.json for #{s.get('rank')} @{s.get('handle')}: {e}", file=sys.stderr)
                missing.append(s.get("rank"))
        else:
            missing.append(s.get("rank"))
        if not isinstance(analysis, dict):
            # valid JSON but wrong shape (list/str/number) — degrade this card, don't kill the build
            print(f"[warn] post.json for #{s.get('rank')} @{s.get('handle')} is not a JSON object", file=sys.stderr)
            missing.append(s.get("rank"))
            analysis = {}
        # analysis fields only; never let a subagent overwrite a scraped fact
        # (note: content_format is the *content* style — distinct from the
        #  scraped "format" media type, which stays Reel/Carousel/Image)
        # str() coercion: a wrong-typed value renders ugly instead of crashing .strip()/escape.
        for k in ("hook", "hook_type", "content_format", "breakdown", "transcript", "why"):
            if analysis.get(k):
                post[k] = str(analysis[k])
        if not post.get("why"):
            post["why"] = "(breakdown unavailable — subagent did not complete; re-run this rank)"
            if s.get("rank") not in missing:
                missing.append(s.get("rank"))
        posts.append(post)

    if missing:
        print(f"[warn] {len(missing)} pick(s) missing a usable post.json: {missing}", file=sys.stderr)

    # run dirs are timestamped (<YYYY-MM-DD>_<HHMMSS>); show just the clean date
    date = (os.path.basename(date_root.rstrip("/")) or "").split("_")[0]
    manifest = {
        "generated": date,
        "accounts_scraped": len({p["handle"] for p in posts}),
        "posts_count": len(posts),
        "window": "last 7 days",
        "pattern": pattern,
        "posts": posts,
    }
    # leave an inspectable manifest behind
    with open(os.path.join(date_root, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest


def build(manifest, out_html):
    cards = "".join(post_card(p) for p in manifest.get("posts", []))
    stats = (
        f'<span class="stat"><b>{manifest.get("accounts_scraped","?")}</b> accounts</span>'
        f'<span class="stat"><b>{manifest.get("posts_count","?")}</b> posts</span>'
        f'<span class="stat">{html.escape(manifest.get("window","last 7 days"))}</span>'
        f'<span class="stat">ranked by <b>likes</b></span>'
        f'<span class="stat">🔥 <b>breakout</b> = likes ÷ creator median</span>'
        f'<span class="stat">{html.escape(str(manifest.get("generated","")))}</span>'
    )
    pattern = manifest.get("pattern", "").strip()
    pattern_html = (
        f'<div class="pattern"><span class="lbl">Pattern</span><p>{html.escape(pattern)}</p></div>'
        if pattern else ""
    )
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>IG Competitor Research — {html.escape(str(manifest.get("generated","")))}</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🔬</text></svg>">
<style>{CSS}</style></head><body><div class="wrap">
<header><div class="kicker">Instagram Competitor Research</div>
<h1>What's working in the niche</h1><div class="stats">{stats}</div></header>
{pattern_html}{cards}
<footer>Generated {html.escape(str(manifest.get("generated","")))} · ig-competitor-research · ranked by likes (no view data from source)</footer>
</div><script>{JS}</script></body></html>"""
    os.makedirs(os.path.dirname(os.path.abspath(out_html)) or ".", exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(doc)
    return out_html


def main():
    args = [a for a in sys.argv[1:] if a != "--open"]
    do_open = "--open" in sys.argv
    if len(args) < 2:
        print("usage: build-report.py <date_root | manifest.json> <out.html> [--open]", file=sys.stderr)
        sys.exit(1)
    src, out_html = args[0], args[1]
    # directory -> assemble from selection.json + post.json files + pattern.txt;
    # file -> use as a pre-written manifest (legacy path, still supported).
    if os.path.isdir(src):
        manifest = assemble_from_dateroot(src)
    else:
        with open(src, encoding="utf-8") as f:
            manifest = json.load(f)
    build(manifest, out_html)
    size_kb = os.path.getsize(out_html) // 1024
    print(f"[report] wrote {out_html} ({size_kb} KB)", file=sys.stderr)
    if do_open:
        webbrowser.open("file://" + os.path.abspath(out_html))
    print(out_html)


if __name__ == "__main__":
    main()
