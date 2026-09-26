# /// script
# requires-python = ">=3.9"
# dependencies = ["pyobjc-framework-ApplicationServices", "pyobjc-framework-Quartz"]
# ///
"""Add one caption line to a CapCut draft, with an optional highlighted keyword
(its own font/colour) and optional per-word timing — the bridge's own `add-text`
command can't do either: it always stretches a single style over the whole
string. This reuses the bridge's file-lane machinery (quit/relaunch, draft
repair) via `edit_draft`, and only replaces the style-building step.

Usage:
  uv run add_caption.py <draft> "<text>" --at <s> --dur <s> \\
      [--highlight <word>] [--highlight-color "#FFD400"] [--highlight-font <path>] \\
      [--color "#FFFFFF"] [--font-size 15] [--words <json-file-or-inline>]

`--words` (optional): JSON array of {"text","start","end"} with start/end in
seconds relative to the CAPTION's own start (not the timeline) — drives
CapCut's native per-word timing field. Omit it and words are split evenly
across --dur.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

BRIDGE_DIR = Path(__file__).resolve().parent.parent.parent / "bridge"
TEMPLATES = BRIDGE_DIR / "capcut-templates"


def load_bridge():
    spec = importlib.util.spec_from_file_location("capcut_bridge", BRIDGE_DIR / "capcut-bridge.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hex_to_rgb01(hexcolor):
    h = hexcolor.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def even_words(text, dur):
    words = text.split()
    if not words:
        return {"start_time": [], "end_time": [], "text": []}
    step = dur / len(words)
    starts, ends = [], []
    for i in range(len(words)):
        starts.append(round(i * step * 1000))
        ends.append(round((i + 1) * step * 1000))
    return {"start_time": starts, "end_time": ends, "text": words}


def build_styles(base_tm_style, text, base_color, highlight, highlight_color, highlight_font, highlight_from=0):
    """One style run for the whole string, plus a second run over the
    highlighted word's character range if --highlight matched something."""
    style = dict(base_tm_style)
    style["range"] = [0, len(text)]
    style["fill"] = {"content": {"solid": {"color": hex_to_rgb01(base_color)}, "render_type": "solid"}}
    styles = [style]

    if highlight:
        idx = text.lower().find(highlight.lower(), highlight_from)
        if idx == -1:
            print(f"warning: highlight word {highlight!r} not found in {text!r} — no highlight applied", file=sys.stderr)
        else:
            hi = dict(base_tm_style)
            hi["range"] = [idx, idx + len(highlight)]
            hi["fill"] = {"content": {"solid": {"color": hex_to_rgb01(highlight_color)}, "render_type": "solid"}}
            if highlight_font:
                hi["font"] = {"path": highlight_font, "id": hi.get("font", {}).get("id", "")}
            styles.append(hi)
    return styles


def append_caption(d, bridge, text, at, dur, highlight=None, highlight_color="#FFD400",
                   highlight_font=None, color="#FFFFFF", font_size=15.0, words=None,
                   render_index=None, highlight_from=0):
    """Append one caption segment to an in-memory draft. `words`: optional list of
    {"text","start","end"} relative to the caption's own start."""
    tm_tpl = json.loads((TEMPLATES / "text-material.json").read_text())
    seg_tpl = json.loads((TEMPLATES / "text-segment.json").read_text())
    anim_tpl = json.loads((TEMPLATES / "text-ref-material_animations.json").read_text())
    base_content = json.loads(tm_tpl["content"])
    base_style = base_content["styles"][0] if base_content.get("styles") else {"size": font_size, "strokes": []}

    content = dict(base_content)
    content["text"] = text
    content["styles"] = build_styles(base_style, text, color, highlight, highlight_color, highlight_font, highlight_from)

    tm = dict(tm_tpl)
    tm["id"] = bridge.uid()
    tm["content"] = json.dumps(content, ensure_ascii=False)
    if words:
        tm["words"] = {
            "start_time": [round(w["start"] * 1000) for w in words],
            "end_time": [round(w["end"] * 1000) for w in words],
            "text": [w["text"] for w in words],
        }
    else:
        tm["words"] = even_words(text, dur)
    d["materials"]["texts"].append(tm)

    anim = dict(anim_tpl)
    anim["id"] = bridge.uid()
    d["materials"]["material_animations"].append(anim)

    seg = dict(seg_tpl)
    seg["id"] = bridge.uid()
    seg["material_id"] = tm["id"]
    seg["extra_material_refs"] = [anim["id"]]
    seg["source_timerange"] = {"start": 0, "duration": round(dur * 1e6)}
    seg["target_timerange"] = {"start": round(at * 1e6), "duration": round(dur * 1e6)}
    if render_index is not None:
        seg["render_index"] = render_index

    track = next((t for t in d["tracks"] if t["type"] == "text"), None)
    if track is None:
        track = {"id": bridge.uid(), "type": "text", "segments": [], "flag": 1,
                 "attribute": 0, "name": "", "is_default_name": True}
        d["tracks"].append(track)
    track["segments"].append(seg)
    return seg


def selftest():
    assert hex_to_rgb01("#FFD400") == [1.0, 212 / 255, 0.0]
    words = even_words("cut it aggressively", 3.0)
    assert words["text"] == ["cut", "it", "aggressively"]
    assert words["start_time"] == [0, 1000, 2000] and words["end_time"] == [1000, 2000, 3000]
    base = {"size": 15, "strokes": [], "font": {"path": "", "id": ""}}
    styles = build_styles(base, "cut it aggressively", "#FFFFFF", "aggressively", "#FFD400", None)
    assert len(styles) == 2
    assert styles[0]["range"] == [0, len("cut it aggressively")]
    assert styles[1]["range"] == [7, 7 + len("aggressively")]
    assert styles[1]["fill"]["content"]["solid"]["color"] == [1.0, 212 / 255, 0.0]
    assert build_styles(base, "go go go", "#FFFFFF", "go", "#FFD400", None, 3)[1]["range"] == [3, 5]
    styles_none = build_styles(base, "cut it", "#FFFFFF", "nomatch", "#FFD400", None)
    assert len(styles_none) == 1
    print("selftest OK")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("text")
    ap.add_argument("--at", type=float, required=True, help="timeline seconds")
    ap.add_argument("--dur", type=float, default=2.0)
    ap.add_argument("--highlight", default=None, help="keyword to style differently")
    ap.add_argument("--highlight-color", default="#FFD400")
    ap.add_argument("--highlight-font", default=None, help="path to a .otf/.ttf")
    ap.add_argument("--color", default="#FFFFFF", help="base text color")
    ap.add_argument("--font-size", type=float, default=15.0)
    ap.add_argument("--words", default=None, help="JSON array or path to one, relative to caption start")
    ap.add_argument("--render-index", type=int, default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    bridge = load_bridge()
    words = None
    if args.words:
        raw = Path(args.words).read_text() if Path(args.words).exists() else args.words
        words = json.loads(raw)

    def mutate(d, folder):
        if not args.force and bridge.already_at(d, round(args.at * 1e6), text=args.text):
            sys.exit(f"{args.text!r} is already at {args.at}s — pass --force to add a second copy")
        append_caption(d, bridge, args.text, args.at, args.dur, highlight=args.highlight,
                       highlight_color=args.highlight_color, highlight_font=args.highlight_font,
                       color=args.color, font_size=args.font_size, words=words,
                       render_index=args.render_index)

    bridge.edit_draft(args.draft, mutate)
    hi = f" (highlight: {args.highlight!r})" if args.highlight else ""
    print(f"caption: {args.text!r} at {args.at:.2f}s for {args.dur:.2f}s{hi}")


if __name__ == "__main__":
    main()
