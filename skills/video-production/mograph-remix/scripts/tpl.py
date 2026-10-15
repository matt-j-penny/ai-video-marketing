"""Template tooling for mograph-remix.

A template is a folder holding template.hft (the canonical source, written with
the __COMP__ placeholder; see references/template-contract.md) plus fonts/ and assets/.

  moments                                            print the moment vocabulary used in template.json
  check      <template_dir>                          validate the template contract + template.json
  catalog    <templates_dir>                         list every template's moment card (for edit planning)
  standalone <template_dir>                          write <template_dir>/index.html (preview/check/snapshot)
  instance   <template_dir> <project> <inst_id> [--values JSON]
                                                     write <project>/compositions/<inst_id>.html for an edit
  lib-find                                           list template folders, the galleries that show them, served URLs
  lib-init   <library_dir>                           create a new, empty template library
  lib-check  [--config CFG]                          prove every configured gallery will show saved templates
  lib-add    <template_dir> --meta '{"id","name","desc","features"?}' [--config CFG]
                                                     add/replace the template in every gallery + templates.json
"""
import argparse
import html as htmllib
import json
import os
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
STARTER = HERE / "assets" / "library-starter.html"

MOMENTS = {
    "hook": "the opening line or title of the video or a chapter",
    "emphasis": "a key point, claim or punchline the speaker stresses",
    "list": "2–5 items, options or examples named in a row",
    "steps": "an ordered process, framework or numbered parts",
    "comparison": "A vs B, before/after, pros/cons",
    "stat": "a number, percentage, money amount or count",
    "flow": "cause and effect, or something moving from one thing to another",
    "timeline": "dates or years, progress across time",
    "story": "a personal anecdote, place, person or photo-worthy moment",
    "quote": "a quotation or memorable line attributed to someone",
    "definition": "a term being introduced and explained",
    "question": "a rhetorical question put to the viewer",
    "callout": "naming a person, product, tool, place or source",
    "cta": "subscribe, link, download or next step",
}
CARD_KEYS = ("kind", "mediaMode", "duration", "useWhen", "describe", "limits")

STANDALONE_CSS = (
    "<style>html, body { margin: 0; padding: 0; width: 1920px; height: 1080px; "
    "overflow: hidden; background: transparent; }</style>"
)
SHIM = """<script>
      window.__timelines = window.__timelines || {};
      if (!window.__hyperframes) {
        const decl = JSON.parse(document.documentElement.getAttribute("data-composition-variables") || "[]");
        const vals = Object.fromEntries(decl.map((d) => [d.id, d.default]));
        decl.forEach((d) => document.documentElement.style.setProperty("--" + d.id, d.default));
        window.__hyperframes = { getVariables: () => vals };
      }
    </script>"""
AUTOPLAY = (
    '<!-- hf-autoplay --><script>(function(){if(window.self===window.top)return;function play(){'
    "var tl=window.__timelines||{};var k=Object.keys(tl);if(!k.length){setTimeout(play,150);return;}"
    'k.forEach(function(id){var t=tl[id];t.eventCallback("onComplete",function(){setTimeout(play,1200)});'
    "t.restart();});}setTimeout(play,200);}());</script>"
)


def die(msg):
    sys.exit(f"error: {msg}")


def read_tpl(tdir):
    p = Path(tdir) / "template.hft"
    if not p.exists():
        die(f"{p} not found")
    return p.read_text()


def parts(src):
    """Split template.html into (variables_attr_value, head_styles, body_inner)."""
    m = re.search(r"<html[^>]*?data-composition-variables=(['\"])(.*?)\1", src, re.S)
    variables = htmllib.unescape(m.group(2)) if m else "[]"
    head = re.search(r"<head>(.*?)</head>", src, re.S).group(1)
    styles = "\n".join(re.findall(r"<style>.*?</style>", head, re.S))
    body = re.search(r"<body>(.*?)</body>", src, re.S).group(1)
    return variables, styles, body


def check(src):
    errs = []
    if 'data-composition-id="__COMP__"' not in src:
        errs.append('root needs data-composition-id="__COMP__"')
    if 'id="__COMP__-root"' not in src:
        errs.append('root needs id="__COMP__-root"')
    if 'window.__timelines["__COMP__"]' not in src:
        errs.append('register the timeline as window.__timelines["__COMP__"]')
    for i in re.findall(r'(?<![\w-])id="([^"]+)"', src):
        if not i.startswith("__COMP__-"):
            errs.append(f'id "{i}" must start with __COMP__-')
    if re.search(r"[\w)\]-]\s+@font-face", src):
        errs.append("@font-face must be top level, never after a selector")
    if re.search(r"(?m)^\s*(html|body)\b[^{]*{", src):
        errs.append("no html/body rules — standalone mode adds them")
    _, styles, _ = parts(src)
    css = re.sub(r"@font-face\s*{[^}]*}", "", "".join(re.findall(r"<style>(.*?)</style>", styles, re.S)))
    css = re.sub(r"@keyframes[^{]*{(?:[^{}]*{[^}]*})*\s*}", "", css)
    for sel in re.findall(r"([^{}]+){", css):
        for s in sel.split(","):
            s = s.strip()
            if s and not s.startswith("#__COMP__-root") and not s.startswith("@"):
                errs.append(f'CSS selector "{s}" must start with #__COMP__-root')
    if re.search(r"getElementById\(\s*[`'\"](?!__COMP__-)", src):
        errs.append("getElementById must use a __COMP__- id")
    if "data-composition-variables" in src:
        try:
            json.loads(parts(src)[0])
        except json.JSONDecodeError as e:
            errs.append(f"data-composition-variables is not valid JSON: {e}")
    return errs


def standalone_html(src, comp="main"):
    s = src.replace("__COMP__", comp)
    return s.replace("</head>", f"    {STANDALONE_CSS}\n  </head>", 1)


def read_card(tdir):
    p = Path(tdir) / "template.json"
    return json.loads(p.read_text()) if p.exists() else None


def check_card(card):
    if card is None:
        return ["template.json missing — see references/template-contract.md"]
    errs = [f"template.json needs {k}" for k in CARD_KEYS if k not in card]
    if card.get("mediaMode") not in ("overlay", "standalone"):
        errs.append('template.json mediaMode must be "overlay" or "standalone"')
    use = card.get("useWhen", [])
    if not 1 <= len(use) <= 3:
        errs.append("template.json useWhen needs 1–3 moments, best first")
    errs += [f'useWhen "{m}" is not a moment (see `tpl.py moments`)' for m in use if m not in MOMENTS]
    return errs


def cmd_moments(a):
    for k, v in MOMENTS.items():
        print(f"{k:11} {v}")


def cmd_catalog(a):
    for tdir in sorted(p for p in Path(a.templates).iterdir() if (p / "template.hft").exists()):
        c = read_card(tdir) or {}
        decl = json.loads(parts(read_tpl(tdir))[0])
        print(f"## {tdir.name}  [{c.get('mediaMode', '?')}, {c.get('duration', '?')}s]  useWhen: {', '.join(c.get('useWhen', []))}")
        print(f"   {c.get('describe', '(no template.json)')}")
        print(f"   limits: {c.get('limits', '-')}" + (f" | avoid: {c['avoidWhen']}" if c.get("avoidWhen") else ""))
        print(f"   vars: {', '.join(d['id'] for d in decl)}")


def cmd_check(a):
    errs = check(read_tpl(a.template)) + check_card(read_card(a.template))
    print("\n".join(errs) if errs else "ok")
    sys.exit(1 if errs else 0)


def cmd_standalone(a):
    src = read_tpl(a.template)
    errs = check(src)
    if errs:
        die("template contract:\n  " + "\n  ".join(errs))
    (Path(a.template) / "index.html").write_text(standalone_html(src))
    print(Path(a.template) / "index.html")


def merge_dir(src, dst):
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)


def cmd_instance(a):
    tdir, proj = Path(a.template), Path(a.project)
    src = read_tpl(tdir)
    variables, styles, body = parts(src)
    decl = json.loads(variables)
    values = json.loads(a.values) if a.values else {}
    unknown = set(values) - {d["id"] for d in decl}
    if unknown:
        die(f"unknown variables for {tdir.name}: {sorted(unknown)}")
    for d in decl:
        if d["id"] in values:
            d["default"] = values[d["id"]]
    inst = a.inst_id
    body = re.sub(r"<script src=[^>]*></script>", "", body)
    out = (
        "<!doctype html>\n"
        f"<html data-composition-variables='{json.dumps(decl).replace(chr(39), '&#39;')}'>\n"
        "  <head><meta charset=\"UTF-8\" /></head>\n  <body>\n    <template>\n"
        f"      {styles}\n{body}\n    </template>\n  </body>\n</html>\n"
    ).replace("__COMP__", inst)
    (proj / "compositions").mkdir(parents=True, exist_ok=True)
    (proj / "compositions" / f"{inst}.html").write_text(out)
    merge_dir(tdir / "fonts", proj / "fonts")
    merge_dir(tdir / "assets", proj / "assets")
    print(proj / "compositions" / f"{inst}.html")


CFG = Path.home() / ".config" / "mograph-remix" / "config.json"
ANCHOR_RE = re.compile(r"(?:const|let|var) TEMPLATES = \[\n")


def gallery_block(s):
    m = ANCHOR_RE.search(s)
    if not m:
        return None, ""
    return m, s[m.end():s.index("\n];", m.end())]


def entry_files(block):
    return [Path(p).name for p in re.findall(r"path:\s*['\"]Assets/templates/([^'\"]+)['\"]", block)]


def fetch(url):
    from urllib.request import urlopen
    try:
        with urlopen(url, timeout=3) as r:
            return r.read()
    except Exception:
        return None


def load_lib(cfg_path):
    p = Path(cfg_path).expanduser()
    if not p.exists():
        die(f"{p} not found — run setup")
    lib = json.loads(p.read_text()).get("library", {})
    if lib.get("mode") != "library":
        die("library mode is not 'library' — templates stay in the run folder")
    if "templates" not in lib or not lib.get("galleries"):
        die("config library needs `templates` and `galleries` — re-run setup")
    return Path(lib["templates"]).expanduser().resolve(), lib["galleries"]


def verify(tpl_dir, galleries):
    """Errors and warnings proving each gallery will show templates written to tpl_dir."""
    errs, warns = [], []
    if not tpl_dir.is_dir():
        return [f"templates folder {tpl_dir} does not exist"], warns
    if not os.access(tpl_dir, os.W_OK):
        errs.append(f"templates folder {tpl_dir} is not writable")
    tj = tpl_dir / "templates.json"
    if tj.exists():
        try:
            d = json.loads(tj.read_text())
            if not any(isinstance(d.get(k), list) for k in ("mg-templates", "templates")):
                errs.append(f"{tj} has no `mg-templates` or `templates` list")
        except json.JSONDecodeError as e:
            errs.append(f"{tj} is not valid JSON: {e}")
    for g in galleries:
        f = Path(g["file"]).expanduser()
        if not f.exists():
            errs.append(f"{f}: not found")
            continue
        src = f.read_text()
        m, block = gallery_block(src)
        if not m:
            errs.append(f"{f}: no `TEMPLATES = [` list — unsupported gallery format")
            continue
        names = entry_files(block)
        local = (f.parent / "Assets" / "templates").resolve() == tpl_dir
        url = g.get("url")
        if not local and not url:
            errs.append(f"{f}: does not sit beside {tpl_dir} and has no url — it cannot load these templates")
        missing = [n for n in names if not (tpl_dir / n).exists()]
        if names and len(missing) * 2 > len(names):
            errs.append(f"{f}: {len(missing)}/{len(names)} of its entries are not in {tpl_dir} — it reads a different folder")
        if url:
            served = fetch(url)
            if served is None:
                warns.append(f"{url}: not reachable now (server down?) — saves still go to {f}")
            elif served != f.read_bytes():
                errs.append(f"{url} serves a different file than {f}")
        print(f"gallery {f}{' @ ' + url if url else ''}: {len(names)} entries")
    return errs, warns


def report(errs, warns):
    for w in warns:
        print(f"warning: {w}")
    if errs:
        die("library check failed:\n  " + "\n  ".join(errs))


def cmd_lib_find(a):
    import subprocess
    found = subprocess.run(
        ["find", str(Path.home()), "-maxdepth", "7", "-name", "template-library.html",
         "-not", "-path", "*/node_modules/*", "-not", "-path", "*/Library/*", "-not", "-path", "*/.Trash/*"],
        capture_output=True, text=True).stdout.split("\n")
    galleries = [Path(x) for x in found if x]
    dirs = {(g.parent / "Assets" / "templates").resolve() for g in galleries if (g.parent / "Assets" / "templates").is_dir()}
    ports = subprocess.run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], capture_output=True, text=True).stdout
    ports = sorted({int(x) for x in re.findall(r"(?:127\.0\.0\.1|localhost|\*|\[::1\]):(\d+) \(LISTEN\)", ports)})
    served = {}
    for port in ports:
        url = f"http://localhost:{port}/template-library.html"
        body = fetch(url)
        if body:
            served[body] = url
    groups = {}
    for g in galleries:
        names = entry_files(gallery_block(g.read_text())[1])
        sib = (g.parent / "Assets" / "templates").resolve()
        best = sib if sib in dirs else max(dirs, key=lambda d: sum((d / n).exists() for n in names), default=None)
        entry = {"file": str(g), "url": served.get(g.read_bytes())}
        groups.setdefault(str(best), []).append((entry, len(names), g.stat().st_mtime))
    import time
    groups = {d: gs for d, gs in groups.items() if d != "None"}
    if not groups:
        print("no template library found")
        return
    # ponytail: a library served by a running app wins; several unserved ones are ambiguous, so ask
    rank = lambda gs: (any(e["url"] for e, _, _ in gs), max(mt for _, _, mt in gs))
    best = max(groups, key=lambda d: rank(groups[d]))
    tie = sum(rank(gs)[0] == rank(groups[best])[0] for gs in groups.values()) > 1 and not rank(groups[best])[0]
    for d, gs in groups.items():
        print(f"\ntemplates folder: {d}")
        for e, n, mt in gs:
            print(f"  gallery {e['file']}  ({n} entries, edited {time.strftime('%Y-%m-%d', time.localtime(mt))})"
                  + (f"  served at {e['url']}" if e["url"] else ""))
        print("  config: " + json.dumps({"mode": "library", "templates": d, "galleries": [e for e, _, _ in gs]}))
    print(f"\n{'ambiguous' if tie else 'recommended'}: {best}")


def cmd_lib_init(a):
    lib = Path(a.library).expanduser().resolve()
    if (lib / "template-library.html").exists():
        die(f"{lib} already has a template library — connect to it instead")
    for d in ("Assets/templates/assets/fonts", "Assets/templates/assets/sfx"):
        (lib / d).mkdir(parents=True, exist_ok=True)
    shutil.copy(STARTER, lib / "template-library.html")
    (lib / "AGENTS.md").write_text(
        "# HyperFrames Template Library\n\n"
        "Open `template-library.html` in a browser to browse templates. "
        "Keep it beside `Assets/` — it loads templates through relative paths.\n\n"
        "- `Assets/templates/<id>.html` — one self-contained HyperFrames template per file\n"
        "- `Assets/templates/assets/` — fonts, images and sound effects the templates use\n"
    )
    print("config: " + json.dumps({"mode": "library", "templates": str(lib / "Assets" / "templates"),
                                   "galleries": [{"file": str(lib / "template-library.html"), "url": None}]}))


def cmd_lib_check(a):
    tpl_dir, galleries = load_lib(a.config)
    report(*verify(tpl_dir, galleries))
    print(f"ok — templates go to {tpl_dir}, listed in {len(galleries)} gallery file(s)")


def cmd_lib_add(a):
    tpl_dir, galleries = load_lib(a.config)
    errs, _ = verify(tpl_dir, galleries)
    report(errs, [])
    tdir = Path(a.template)
    meta = json.loads(a.meta)
    for k in ("id", "name", "desc"):
        if k not in meta:
            die(f"--meta needs {k}")
    card = read_card(tdir)
    errs = check_card(card)
    if errs:
        die("\n  ".join(errs))
    meta["desc"] = meta["desc"].rstrip() + f" Use when: {card['describe']}"
    meta = {"duration": card["duration"], "mediaMode": card["mediaMode"], **meta,
            "useWhen": card["useWhen"], "limits": card["limits"]}
    tid = meta["id"]
    html = standalone_html(read_tpl(tdir))
    html = html.replace('"assets/', f'"assets/{tid}/').replace("&quot;assets/", f"&quot;assets/{tid}/")
    html = html.replace('url("fonts/', 'url("assets/fonts/')
    html = re.sub(r"(<script src=\"https://cdn\.jsdelivr\.net/npm/gsap)", SHIM + r"\n    \1", html, count=1)
    html = html.replace("</body>", AUTOPLAY + "\n</body>", 1)
    (tpl_dir / f"{tid}.html").write_text(html)
    merge_dir(tdir / "assets", tpl_dir / "assets" / tid)
    merge_dir(tdir / "fonts", tpl_dir / "assets" / "fonts")

    entry = {"id": tid, "category": "mg", "features": [], **meta, "path": f"Assets/templates/{tid}.html"}
    body = ",\n".join(f"    {k}: {json.dumps(v)}" for k, v in entry.items())
    block = f"  {{ // mograph-remix\n{body},\n  }},\n"
    for g in galleries:
        f = Path(g["file"]).expanduser()
        s = re.sub(r"  \{ // mograph-remix\n    id: " + re.escape(json.dumps(tid)) + r",.*?\n  \},\n", "", f.read_text(), flags=re.S)
        m, _ = gallery_block(s)
        f.write_text(s[:m.end()] + block + s[m.end():])

    tj = tpl_dir / "templates.json"
    if tj.exists():
        d = json.loads(tj.read_text())
        key = "mg-templates" if isinstance(d.get("mg-templates"), list) else "templates"
        d[key] = [t for t in d[key] if t.get("id") != tid] + [{
            "id": tid, "name": meta["name"], "path": f"templates/{tid}.html", "description": meta["desc"],
            "bestFor": card["useWhen"], "avoidWhen": [x for x in (card.get("avoidWhen"), card["limits"]) if x],
            "features": meta.get("features", []),
            "technical": {"framework": "HyperFrames", "width": 1920, "height": 1080,
                          "mediaMode": card["mediaMode"], "defaultDuration": card["duration"]},
        }]
        tj.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f"added {tid} -> {tpl_dir / (tid + '.html')} (+ {len(galleries)} gallery, templates.json: {tj.exists()})")


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(required=True)
c = sub.add_parser("moments"); c.set_defaults(fn=cmd_moments)
c = sub.add_parser("check"); c.add_argument("template"); c.set_defaults(fn=cmd_check)
c = sub.add_parser("catalog"); c.add_argument("templates"); c.set_defaults(fn=cmd_catalog)
c = sub.add_parser("standalone"); c.add_argument("template"); c.set_defaults(fn=cmd_standalone)
c = sub.add_parser("instance"); c.add_argument("template"); c.add_argument("project"); c.add_argument("inst_id")
c.add_argument("--values"); c.set_defaults(fn=cmd_instance)
c = sub.add_parser("lib-init"); c.add_argument("library"); c.set_defaults(fn=cmd_lib_init)
c = sub.add_parser("lib-find"); c.set_defaults(fn=cmd_lib_find)
c = sub.add_parser("lib-check"); c.add_argument("--config", default=CFG); c.set_defaults(fn=cmd_lib_check)
c = sub.add_parser("lib-add"); c.add_argument("template"); c.add_argument("--config", default=CFG)
c.add_argument("--meta", required=True); c.set_defaults(fn=cmd_lib_add)
a = ap.parse_args()
a.fn(a)
