#!/usr/bin/env python3
"""
Carousel cover generator — Higgsfield (Nano Banana Pro) -> 4:5 cover image(s).

Reads the carousel manifest's `cover` block, generates N *textless* cover
variants via the Higgsfield CLI, and downloads them next to the manifest in
`cover/`. You then set slides[0].image to the one you like and render — the
headline is overlaid in HTML by render.js, so text is NEVER baked into the
image (crisp, editable, on-brand typography; AI glitch-text impossible).

Manifest `cover` block:
  "cover": {
    "concept": "cinematic, textless, no-UI prompt for the cover background",
    "face_refs": false,        # true => anchor with assets/face-refs/ photos
    "aspect": "4:5",           # 1080x1350 is exactly 4:5; CSS object-fit covers anyway
    "variants": 3
  }
  # multiple cover directions: use "concepts": [{ "id": "...", "prompt": "..." }, ...]

Usage:
  python3 cover.py <manifest.json> [--variants N] [--yes] [--dry-run] [--only-concept ID]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
FACE_REF_DIR = PROJECT_ROOT / "assets" / "face-refs"
MODEL = "nano_banana_2"          # the CLI id for Nano Banana Pro
RESOLUTION = "2k"                # nano_banana_2 uses --resolution (2k is free vs 1k)
DEFAULT_ASPECT = "4:5"
DEFAULT_VARIANTS = 3
WAIT_TIMEOUT = "10m"
CREDITS_PER_IMG = 2.0
IMG_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
IMG_EXT_RE = re.compile(r"\.(png|jpe?g|webp)(\?|$)", re.I)


def ensure_cli():
    if shutil.which("higgsfield") is None:
        sys.exit("[cover] higgsfield CLI not found. Install: "
                 "curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh")
    # NOTE: it's `account status` (exit 0 when logged in), NOT `auth status`.
    r = subprocess.run(["higgsfield", "account", "status"], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("[cover] higgsfield CLI not authenticated. Run: higgsfield auth login")


def collect_face_refs(enabled):
    if not enabled:
        return []
    refs = []
    if FACE_REF_DIR.is_dir():
        refs = sorted(p for p in FACE_REF_DIR.iterdir() if p.suffix.lower() in IMG_SUFFIXES)
    if not refs:
        print(f"[cover] WARNING: face_refs=true but 0 reference photos found in {FACE_REF_DIR} "
              "(expects <project>/assets/face-refs/ with this skill installed at "
              "<project>/.claude/skills/carousel-generator/). Generating WITHOUT a face anchor.",
              file=sys.stderr)
    return refs


def extract_result_url(stdout):
    """Walk the JSON for a node with status==completed AND a string result_url.
    Strict (no regex fallback) so we don't grab echoed --image upload URLs."""
    try:
        data = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        return None
    found = []

    def walk(n):
        if isinstance(n, dict):
            if n.get("status") == "completed" and isinstance(n.get("result_url"), str):
                found.append(n["result_url"])
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    walk(data)
    return found[0] if found else None


def ext_from_url(url):
    m = IMG_EXT_RE.search(url)
    if not m:
        return ".png"
    e = m.group(1).lower()
    return ".jpg" if e in ("jpg", "jpeg") else f".{e}"


def download(url, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=180) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)


def generate_one(concept, v, aspect, refs, out_dir):
    cid = concept["id"]
    cmd = ["higgsfield", "--json", "generate", "create", MODEL,
           "--prompt", concept["prompt"],
           "--aspect_ratio", aspect,
           "--resolution", RESOLUTION,
           "--wait", "--wait-timeout", WAIT_TIMEOUT]
    for p in refs:
        cmd += ["--image", str(p)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return {"id": f"{cid}_v{v}", "status": "error",
                "error": (r.stderr or r.stdout or "cli error").strip()[:300]}
    url = extract_result_url(r.stdout)
    if not url:
        return {"id": f"{cid}_v{v}", "status": "error", "error": "no result_url in output"}
    dest = out_dir / f"{cid}_v{v}{ext_from_url(url)}"
    try:
        download(url, dest)
    except Exception as e:  # noqa: BLE001
        return {"id": f"{cid}_v{v}", "status": "error", "error": f"download failed: {e}"}
    return {"id": f"{cid}_v{v}", "status": "ok", "path": str(dest), "source_url": url}


def main():
    ap = argparse.ArgumentParser(description="Generate carousel cover images via Higgsfield.")
    ap.add_argument("manifest", help="path to carousel.json")
    ap.add_argument("--variants", type=int, help="override cover.variants")
    ap.add_argument("--yes", action="store_true", help="skip the confirm prompt")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, submit nothing")
    ap.add_argument("--only-concept", help="generate just this concept id")
    args = ap.parse_args()

    mpath = Path(args.manifest).resolve()
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    cover = manifest.get("cover") or {}

    concepts = cover.get("concepts")
    if not concepts and cover.get("concept"):
        concepts = [{"id": "cover", "prompt": cover["concept"]}]
    if not concepts:
        sys.exit("[cover] manifest has no cover.concept (or cover.concepts[]). "
                 "Add a textless, no-UI cinematic prompt.")

    for i, c in enumerate(concepts):
        c.setdefault("id", f"cover{i + 1}" if len(concepts) > 1 else "cover")
        if not c.get("prompt"):
            sys.exit(f"[cover] concept {c['id']} missing prompt")
    if args.only_concept:
        concepts = [c for c in concepts if c["id"] == args.only_concept]
        if not concepts:
            sys.exit(f"[cover] no concept id matches {args.only_concept}")

    aspect = cover.get("aspect") or DEFAULT_ASPECT
    # distinguish None from 0 so an explicit 0 isn't silently coerced to the default
    variants = args.variants if args.variants is not None else cover.get("variants")
    if variants is None:
        variants = DEFAULT_VARIANTS
    if variants < 1:
        sys.exit("[cover] variants must be >= 1")
    refs = collect_face_refs(bool(cover.get("face_refs", False)))
    out_dir = mpath.parent / "cover"

    jobs = [(c, v) for c in concepts for v in range(1, variants + 1)]
    total = len(jobs)
    print(f"[cover] {len(concepts)} concept(s) x {variants} variant(s) = {total} image(s) "
          f"~ {total * CREDITS_PER_IMG:g} credits | aspect {aspect} | refs {len(refs)} | {MODEL}",
          file=sys.stderr)
    for c in concepts:
        print(f"        - {c['id']}: {c['prompt'][:90]}...", file=sys.stderr)

    if args.dry_run:
        print("[cover] dry-run, nothing submitted.", file=sys.stderr)
        return

    ensure_cli()
    # confirm only when a human is at a TTY; non-interactive runs (Claude's Bash,
    # CI) skip the prompt so they neither abort on EOF nor hang on a blocked stdin.
    if not args.yes and sys.stdin.isatty():
        try:
            ans = input("[cover] generate now? [y/N] ").strip().lower()
        except EOFError:  # Ctrl-D at the prompt = no
            ans = ""
        if ans not in ("y", "yes"):
            sys.exit("[cover] aborted.")

    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    with ThreadPoolExecutor(max_workers=min(6, total)) as ex:
        futs = {ex.submit(generate_one, c, v, aspect, refs, out_dir): (c["id"], v)
                for c, v in jobs}
        for fut in as_completed(futs):
            r = fut.result()
            results[r["id"]] = r
            tag = "OK " if r["status"] == "ok" else "ERR"
            print(f"[cover] {tag} {r['id']}: {r.get('path') or r.get('error')}", file=sys.stderr)

    ok = sorted((r for r in results.values() if r["status"] == "ok"), key=lambda r: r["id"])
    print(f"\n[cover] {len(ok)}/{total} generated -> {out_dir}")
    if ok:
        rel = os.path.relpath(ok[0]["path"], mpath.parent)
        print(f'[cover] pick one, then set slides[0] = '
              f'{{"type":"cover_image","image":"{rel}", "headline":"...", ...}}')
    if len(ok) < total:
        sys.exit(2)


if __name__ == "__main__":
    main()
