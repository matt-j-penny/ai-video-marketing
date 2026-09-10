#!/usr/bin/env python3
"""build-report.py — render a self-contained HTML YT competitor-research report.

usage:
    bash <SKILL_DIR>/scripts/build-report.sh <run_dir | manifest.json> <out.html> [--open]
    (the wrapper runs this file on the shared pillow venv at
    ~/.cache/content-os/pillow-venv, built once by uv; CONTENT_OS_PILLOW_VENV overrides)

Each pick's thumbnail is read from its `jobdir` (thumb.jpg), downscaled, and
base64-embedded so the output is ONE portable file that never breaks — no
asset folder, no expiring CDN links.

Manifest schema:
{
  "generated": "2026-06-09",
  "channels_scraped": 5,
  "videos_count": 15,
  "window": "last 7 days",
  "pattern": "…synthesis paragraph…",
  "videos": [
    {
      "rank": 1, "handle": "somechannel", "title": "…",
      "views": "1.2M", "likes": "38K", "like_rate": "3.1%",
      "date": "Jun 4, 2026", "duration": "14:22",
      "outlier_label": "4.5×", "outlier_score": 4.5, "baseline": "266K",
      "url": "https://www.youtube.com/watch?v=…",
      "jobdir": "/tmp/yt-research/…/1_somechannel",
      "title_archetype": "",   // 2-4 words: the title's hook structure
      "thumb_breakdown": "",   // what's visually on the thumbnail, incl. any text verbatim
      "packaging": "",         // one sentence: how title + thumb create the click gap
      "breakdown": "",         // one sentence: what the video actually is
      "why": "…"
    }
  ]
}
"""
import sys, os, json, base64, html, io, webbrowser

MAXW = 760          # downscale width for embedded thumbnails
JPEG_Q = 78


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


def image_size(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.width, im.height
    except Exception:  # noqa
        return None


def thumb_html(p):
    path = os.path.join(p.get("jobdir", ""), "thumb.jpg")
    uri = embed(path) if os.path.isfile(path) else None
    if not uri:
        return '<div class="thumb empty"><span>thumbnail unavailable</span></div>'
    # hug the real aspect ratio (maxres 16:9 vs hqdefault 4:3) — no letterbox
    ar_style = ""
    sz = image_size(path)
    if sz and sz[0] and sz[1]:
        ar_style = f' style="aspect-ratio:{sz[0]}/{sz[1]}"'
    url = html.escape(p.get("url") or "")
    return (f'<a class="thumb-link" href="{url}" target="_blank" rel="noopener">'
            f'<div class="thumb"{ar_style}><img loading="lazy" src="{uri}" alt=""></div></a>')


def video_card(p):
    rank = p.get("rank", "")
    badge_cls = "badge gold" if rank == 1 else "badge"
    url = html.escape(p.get("url") or "")
    bits = []
    bits.append('<article class="card">')
    bits.append(f'<div class="rank"><span class="{badge_cls}">#{rank}</span></div>')
    bits.append('<div class="media-col">')
    bits.append(thumb_html(p))
    bits.append(f'<a class="yt-btn" href="{url}" target="_blank" rel="noopener">▶ Watch on YouTube</a>')
    bits.append("</div>")

    bits.append('<div class="info">')
    bits.append('<div class="meta-row">')
    bits.append(f'<span class="handle">@{html.escape(p.get("handle",""))}</span>')
    dur = str(p.get("duration", "")).strip()
    if dur:
        bits.append(f'<span class="tag">{html.escape(dur)}</span>')
    bits.append("</div>")

    # for long-form the title IS the hook — give it hook-level prominence
    title = p.get("title", "").strip()
    if title:
        bits.append(f'<h2 class="title"><a href="{url}" target="_blank" rel="noopener">{html.escape(title)}</a></h2>')

    bits.append('<div class="pills">')
    bits.append(f'<span class="pill views">▶ {html.escape(str(p.get("views","")))} views</span>')
    olabel = (p.get("outlier_label") or "").strip()
    if olabel and olabel != "—":
        try:
            score = float(p.get("outlier_score") or 0)
        except (TypeError, ValueError):
            score = 0
        heat = "hot" if score >= 3 else ("warm" if score >= 1.5 else "cool")
        emoji = "🔥 " if heat == "hot" else ""
        title_attr = (f'{p.get("views","")} views vs @{p.get("handle","")}\'s '
                      f'{p.get("baseline","")} median this week')
        bits.append(f'<span class="pill breakout {heat}" title="{html.escape(title_attr)}">{emoji}{html.escape(olabel)} breakout</span>')
    likes = str(p.get("likes", "")).strip()
    if likes and likes != "n/a":
        bits.append(f'<span class="pill likes">👍 {html.escape(likes)}</span>')
    lr = str(p.get("like_rate", "")).strip()
    if lr and lr != "n/a":
        bits.append(f'<span class="pill">{html.escape(lr)} like rate</span>')
    date = str(p.get("date", "")).strip()
    if date:
        bits.append(f'<span class="pill date">{html.escape(date)}</span>')
    bits.append("</div>")

    arch = p.get("title_archetype", "").strip()
    if arch:
        bits.append(f'<div class="fmt"><span class="lbl">Title archetype</span><span class="chip">{html.escape(arch)}</span></div>')

    tb = p.get("thumb_breakdown", "").strip()
    if tb:
        bits.append(f'<div class="block"><span class="lbl">Thumbnail</span><p>{html.escape(tb)}</p></div>')

    pkg = p.get("packaging", "").strip()
    if pkg:
        bits.append(f'<div class="block"><span class="lbl">Packaging</span><p>{html.escape(pkg)}</p></div>')

    breakdown = p.get("breakdown", "").strip()
    if breakdown:
        bits.append(f'<div class="block"><span class="lbl">Breakdown</span><p>{html.escape(breakdown)}</p></div>')

    desc = p.get("description", "").strip()
    if desc:
        bits.append(
            f'<details class="desc"><summary><span class="lbl-inline">Description</span>'
            f'<button class="copy-btn" type="button">Copy</button></summary>'
            f'<p>{html.escape(desc)}</p></details>'
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
  --text:#ededf2;--muted:#9a9aa9;--accent:#ff4d4d;--accent2:#feaa54;
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
.pattern{background:linear-gradient(135deg,rgba(255,77,77,.12),rgba(254,170,84,.08));
  border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:14px;
  padding:20px 22px;margin-bottom:40px}
.pattern .lbl{display:block;font-size:12px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--accent);font-weight:700;margin-bottom:8px}
.pattern p{font-size:16px;color:#dcdce4}
.card{display:grid;grid-template-columns:44px 380px 1fr;gap:24px;align-items:start;
  background:var(--surface);border:1px solid var(--line);border-radius:18px;
  padding:22px;margin-bottom:22px}
.rank{position:sticky;top:18px}
.info{min-width:0}
.badge{display:grid;place-items:center;width:44px;height:44px;border-radius:12px;
  background:var(--surface2);border:1px solid var(--line);font-weight:800;font-size:16px}
.badge.gold{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#1a0b0b;border:0}
.media-col{width:380px}
.thumb-link{display:block;text-decoration:none}
.thumb{position:relative;width:380px;aspect-ratio:16/9;background:var(--surface2);
  border-radius:14px;overflow:hidden;border:1px solid var(--line)}
.thumb.empty{display:grid;place-items:center;color:var(--muted);font-size:13px}
.thumb img{width:100%;height:100%;object-fit:contain;display:block;transition:transform .2s}
.thumb-link:hover img{transform:scale(1.03)}
.yt-btn{display:block;text-align:center;margin-top:12px;padding:10px;border-radius:10px;
  background:var(--surface2);border:1px solid var(--line);color:var(--text);
  text-decoration:none;font-size:14px;font-weight:600;transition:.15s}
.yt-btn:hover{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#1a0b0b;border-color:transparent}
.meta-row{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.handle{font-size:16px;font-weight:700;color:var(--muted)}
.tag{font-size:11px;font-weight:700;letter-spacing:.05em;
  padding:4px 9px;border-radius:6px;background:var(--surface2);border:1px solid var(--line);color:var(--muted)}
.title{font-size:22px;line-height:1.3;font-weight:700;letter-spacing:-.01em;margin-bottom:12px}
.title a{color:var(--text);text-decoration:none}
.title a:hover{color:var(--accent2)}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px}
.pill{font-size:13px;color:var(--muted);background:var(--surface2);border:1px solid var(--line);
  border-radius:999px;padding:4px 12px}
.pill.views{color:#ff8f8f;font-weight:600}
.pill.likes{color:#9affc4}
.pill.breakout{font-weight:700}
.pill.breakout.hot{color:#ff6a4d;border-color:#5e2e27;background:rgba(255,90,60,.12)}
.pill.breakout.warm{color:#feaa54;border-color:#5e4a27;background:rgba(254,170,84,.12)}
.pill.breakout.cool{color:#9a9aa9}
.lbl{display:block;font-size:11px;letter-spacing:.14em;text-transform:uppercase;
  color:var(--muted);font-weight:700;margin-bottom:6px}
.fmt{margin-bottom:16px}
.fmt .chip{display:inline-block;font-size:14px;font-weight:700;color:var(--accent2);
  background:rgba(254,170,84,.1);border:1px solid rgba(254,170,84,.32);
  border-radius:8px;padding:5px 12px;text-transform:capitalize}
.block{margin-bottom:16px}
.block p{color:#d2d2dc}
.desc{margin-bottom:16px;background:var(--surface2);border:1px solid var(--line);
  border-radius:10px;padding:0 14px}
.desc summary{display:flex;align-items:center;cursor:pointer;padding:11px 0;font-size:13px;
  font-weight:600;color:var(--muted);list-style:none;letter-spacing:.04em;text-transform:uppercase}
.desc summary::-webkit-details-marker{display:none}
.desc summary:before{content:"▸";color:var(--accent);margin-right:9px}
.desc[open] summary:before{content:"▾"}
.copy-btn{margin-left:auto;font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--accent);background:var(--surface);border:1px solid var(--line);border-radius:7px;
  padding:4px 11px;cursor:pointer;transition:.15s}
.copy-btn:hover{background:var(--accent);color:#1a0b0b;border-color:transparent}
.copy-btn.copied{background:#2faa6a;color:#06210f;border-color:transparent}
.desc p{padding:0 0 14px;color:#c3c3cf;font-size:14.5px;white-space:pre-wrap;overflow-wrap:anywhere}
.why{background:linear-gradient(135deg,rgba(255,77,77,.1),rgba(254,170,84,.06));
  border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.why .lbl{color:var(--accent)}
.why p{color:#e6e6ee}
footer{text-align:center;color:var(--muted);font-size:13px;margin-top:48px}
@media(max-width:760px){
  .card{grid-template-columns:1fr;gap:16px}
  .rank{position:static}.media-col,.thumb{width:100%}
  h1{font-size:30px}
}
"""

JS = """
document.querySelectorAll('.desc .copy-btn').forEach(function(btn){
  btn.addEventListener('click',function(e){
    e.preventDefault();e.stopPropagation();
    var det=btn.closest('.desc'),p=det?det.querySelector('p'):null;
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


def assemble_from_rundir(run_dir):
    """Build the manifest from a run_dir instead of a pre-written file.

    selection.json (written by rank-and-select.py) is the AUTHORITY for the
    scraped facts — rank, handle, title, views, likes, like_rate, date,
    duration, url, breakout, jobdir. Each <jobdir>/post.json (written by a
    subagent) supplies only the analysis — title_archetype, thumb_breakdown,
    packaging, breakdown, why. <jobdir>/description.txt supplies the
    collapsible description. pattern.txt holds the synthesis line.
    A pick whose post.json is missing/unreadable still renders (thumb +
    facts), flagged so the orchestrator can re-run just that one.
    """
    sel_path = os.path.join(run_dir, "selection.json")
    with open(sel_path, encoding="utf-8") as f:
        selection = json.load(f)
    selection.sort(key=lambda p: p.get("rank", 0))

    pattern = ""
    pat_path = os.path.join(run_dir, "pattern.txt")
    if os.path.isfile(pat_path):
        with open(pat_path, encoding="utf-8") as f:
            pattern = f.read().strip()

    videos, missing = [], []
    for s in selection:
        video = {k: s.get(k, "") for k in
                 ("rank", "handle", "title", "views", "likes", "like_rate", "date",
                  "duration", "url", "jobdir", "outlier_score", "outlier_label", "baseline")}
        desc_path = os.path.join(s.get("jobdir", ""), "description.txt")
        if os.path.isfile(desc_path):
            with open(desc_path, encoding="utf-8") as f:
                video["description"] = f.read().strip()
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
        # analysis fields only; never let a subagent overwrite a scraped fact.
        # str() coercion: a wrong-typed value renders ugly instead of crashing .strip()/escape.
        for k in ("title_archetype", "thumb_breakdown", "packaging", "breakdown", "why"):
            if analysis.get(k):
                video[k] = str(analysis[k])
        if not video.get("why"):
            video["why"] = "(breakdown unavailable — subagent did not complete; re-run this rank)"
            if s.get("rank") not in missing:
                missing.append(s.get("rank"))
        videos.append(video)

    if missing:
        print(f"[warn] {len(missing)} pick(s) missing a usable post.json: {missing}", file=sys.stderr)

    # run dirs are timestamped (<YYYY-MM-DD>_<HHMMSS>); show just the clean date
    date = (os.path.basename(run_dir.rstrip("/")) or "").split("_")[0]
    manifest = {
        "generated": date,
        "channels_scraped": len({v["handle"] for v in videos}),
        "videos_count": len(videos),
        "window": "last 7 days",
        "pattern": pattern,
        "videos": videos,
    }
    # leave an inspectable manifest behind
    with open(os.path.join(run_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    return manifest


def build(manifest, out_html):
    cards = "".join(video_card(v) for v in manifest.get("videos", []))
    stats = (
        f'<span class="stat"><b>{manifest.get("channels_scraped","?")}</b> channels with uploads this week</span>'
        f'<span class="stat"><b>{manifest.get("videos_count","?")}</b> videos</span>'
        f'<span class="stat">{html.escape(manifest.get("window","last 7 days"))}</span>'
        f'<span class="stat">ranked by <b>views</b></span>'
        f'<span class="stat">🔥 <b>breakout</b> = views ÷ channel weekly median</span>'
        f'<span class="stat">{html.escape(str(manifest.get("generated","")))}</span>'
    )
    pattern = manifest.get("pattern", "").strip()
    pattern_html = (
        f'<div class="pattern"><span class="lbl">Pattern</span><p>{html.escape(pattern)}</p></div>'
        if pattern else ""
    )
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>YT Competitor Research — {html.escape(str(manifest.get("generated","")))}</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📺</text></svg>">
<style>{CSS}</style></head><body><div class="wrap">
<header><div class="kicker">YouTube Competitor Research</div>
<h1>What's working in the niche</h1><div class="stats">{stats}</div></header>
{pattern_html}{cards}
<footer>Generated {html.escape(str(manifest.get("generated","")))} · yt-competitor-research · ranked by views · packaging analysis only (title + thumbnail)</footer>
</div><script>{JS}</script></body></html>"""
    os.makedirs(os.path.dirname(os.path.abspath(out_html)) or ".", exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(doc)
    return out_html


def main():
    args = [a for a in sys.argv[1:] if a != "--open"]
    do_open = "--open" in sys.argv
    if len(args) < 2:
        print("usage: build-report.py <run_dir | manifest.json> <out.html> [--open]", file=sys.stderr)
        sys.exit(1)
    src, out_html = args[0], args[1]
    # directory -> assemble from selection.json + post.json files + pattern.txt;
    # file -> use as a pre-written manifest.
    if os.path.isdir(src):
        manifest = assemble_from_rundir(src)
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
