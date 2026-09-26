# /// script
# requires-python = ">=3.9"
# dependencies = ["pyobjc-framework-ApplicationServices", "pyobjc-framework-Quartz"]
# ///
"""Faceless video pipeline — one subcommand per stage, all state in one job folder.

  uv run faceless.py tts        <job>                 script.md -> voiceover.mp3 (Inworld)
  uv run faceless.py transcribe <job>                 voiceover.mp3 -> transcript.json + words.json (Deepgram)
  uv run faceless.py images     <job> [--redo N]      shots.json -> images/NN.png (+ clips/NN.mp4 in video mode)
  uv run faceless.py assemble   <job> --name <draft>  new CapCut draft: image clips on the video track, voiceover on an audio track
  uv run faceless.py kenburns   <job> --name <draft>  zoom keyframes on every image shot
  uv run faceless.py captions   <job> --name <draft>  word-highlighted native CapCut captions
  uv run faceless.py --selftest

Settings come from ~/.claude/faceless-video-preferences.md ("- key: value" lines),
then FV_<key> env vars for one-off overrides; anything missing falls back to DEFAULTS.
"""
import argparse
import base64
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAPCUT = HERE.parent.parent
PREFS = Path.home() / ".claude/faceless-video-preferences.md"
FPS = 30
CANVAS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080), "4:5": (1080, 1350)}
DEFAULTS = {
    "length": "60s", "aspect": "9:16", "visuals": "images", "cut_speed": "fast",
    "voice": "Blake", "tts_model": "inworld-tts-2", "speaking_rate": "1.0",
    "image_provider": "topview", "image_model": "", "video_model": "kling-2.6/image-to-video",
    "style": "default", "ken_burns": "1.12",
    "caption_words": "3", "caption_color": "#FFFFFF", "caption_highlight": "#FFD400",
    "caption_case": "upper", "caption_y": "-0.45",
}


def prefs():
    p = dict(DEFAULTS)
    if PREFS.exists():
        for line in PREFS.read_text().splitlines():
            m = re.match(r"\s*-\s*([a-z_]+):\s*(.+?)\s*$", line)
            if m:
                p[m[1]] = m[2]
    p.update({k[3:]: v for k, v in os.environ.items() if k.startswith("FV_")})
    return p


def key(name):
    if os.environ.get(name):
        return os.environ[name]
    env = json.loads((Path.home() / ".claude/settings.json").read_text()).get("env", {})
    if not env.get(name):
        sys.exit(f"{name} missing — add it to the env block of ~/.claude/settings.json")
    return env[name]


def http(url, body=None, headers=None, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=300) as r:
        out = r.read()
    return out if raw else json.loads(out)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bridge():
    return load("capcut_bridge", CAPCUT / "bridge/capcut-bridge.py")


# ---------- tts ----------

def spoken_text(md):
    """script.md -> just the words to be read: drop headings, notes, and blank lines."""
    lines = [l.strip() for l in md.splitlines()]
    return " ".join(l for l in lines if l and not l.startswith(("#", ">", "<!--")))


def chunks(text, limit=1900):
    out, cur = [], ""
    for sent in re.split(r"(?<=[.!?])\s+", text):
        if cur and len(cur) + len(sent) + 1 > limit:
            out.append(cur)
            cur = sent
        else:
            cur = f"{cur} {sent}".strip()
    return out + ([cur] if cur else [])


def cmd_tts(job):
    p = prefs()
    text = spoken_text((job / "script.md").read_text())
    auth = {"Authorization": f"Basic {key('INWORLD_API_KEY')}"}
    parts = []
    for i, c in enumerate(chunks(text)):
        r = http("https://api.inworld.ai/tts/v1/voice", {
            "text": c, "voiceId": p["voice"], "modelId": p["tts_model"],
            "audioConfig": {"audioEncoding": "MP3", "speakingRate": float(p["speaking_rate"])}}, auth)
        part = job / f".tts-{i}.mp3"
        part.write_bytes(base64.b64decode(r["audioContent"]))
        parts.append(part)
    lst = job / ".tts.txt"
    lst.write_text("".join(f"file '{x.name}'\n" for x in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(job / "voiceover.mp3")], check=True)
    for x in parts + [lst]:
        x.unlink()
    print(f"voiceover.mp3: {duration(job / 'voiceover.mp3'):.1f}s, voice {p['voice']}, {len(text.split())} words")


def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(path)]))


# ---------- transcribe ----------

def cmd_transcribe(job):
    url = ("https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&punctuate=true"
           "&paragraphs=true&utterances=true&words=true")
    req = urllib.request.Request(url, data=(job / "voiceover.mp3").read_bytes(), headers={
        "Authorization": f"Token {key('DEEPGRAM_API_KEY')}", "Content-Type": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=300) as r:
        t = json.loads(r.read())
    (job / "transcript.json").write_text(json.dumps(t))
    words = [{"text": w["punctuated_word"], "start": round(w["start"], 3), "end": round(w["end"], 3)}
             for w in t["results"]["channels"][0]["alternatives"][0]["words"]]
    (job / "words.json").write_text(json.dumps(words, indent=0))
    print(f"words.json: {len(words)} words, last ends {words[-1]['end']:.2f}s")


# ---------- shots ----------

def load_shots(job):
    """shots.json, made contiguous and frame-aligned: each shot runs until the next
    one starts, the first starts at 0, the last runs to the end of the voiceover."""
    shots = json.loads((job / "shots.json").read_text())["shots"]
    end = duration(job / "voiceover.mp3")
    return normalize(shots, end)


def normalize(shots, end):
    shots = sorted(shots, key=lambda s: s["start"])
    frames = [0] + [round(s["start"] * FPS) for s in shots[1:]] + [round(end * FPS)]
    for i, s in enumerate(shots):
        s["start"], s["end"] = frames[i] / FPS, frames[i + 1] / FPS
    bad = [i for i, s in enumerate(shots) if s["end"] <= s["start"]]
    if bad:
        sys.exit(f"shots {bad} have zero/negative length — fix their start times in shots.json")
    return shots


def save_shots(job, shots):
    path = job / "shots.json"
    d = json.loads(path.read_text())
    d["shots"] = shots
    path.write_text(json.dumps(d, indent=2, ensure_ascii=False))


# ---------- images ----------

KIE = "https://api.kie.ai/api/v1/jobs"


def kie(model, inp, poll=5):
    auth = {"Authorization": f"Bearer {key('KIE_API_KEY')}"}
    r = http(f"{KIE}/createTask", {"model": model, "input": inp}, auth)
    if r.get("code") != 200:
        sys.exit(f"kie createTask failed: {r}")
    tid = r["data"]["taskId"]
    while True:
        d = http(f"{KIE}/recordInfo?taskId={tid}", headers=auth)["data"]
        if d["state"] == "success":
            return json.loads(d["resultJson"])["resultUrls"][0]
        if d["state"] == "fail":
            sys.exit(f"kie task {tid} failed: {d.get('failMsg')}")
        time.sleep(poll)


TOPVIEW = "https://api.topview.ai/v1/common_task/image_edit/task"
IMAGE_MODELS = {"topview": "Nano Banana 2", "kie": "nano-banana-2"}


def topview(model, prompt, refs, aspect):
    auth = {"Authorization": f"Bearer {key('TOPVIEW_API_KEY')}", "Topview-Uid": key("TOPVIEW_UID")}
    r = http(f"{TOPVIEW}/submit", {"model": model, "prompt": prompt, "inputImageFileIds": refs,
                                  "aspectRatio": aspect, "resolution": "1K", "generateCount": 1}, auth)
    if str(r.get("code")) != "200":
        sys.exit(f"topview submit failed: {r}")
    tid = r["result"]["taskId"]
    while True:
        d = http(f"{TOPVIEW}/query?taskId={tid}&needCloudFrontUrl=true", headers=auth)["result"]
        if d["status"] == "success":
            return d["images"][0]["fileId"], d["images"][0]["filePath"]
        if d["status"] == "fail":
            sys.exit(f"topview task {tid} failed: {d.get('errorMsg')}")
        time.sleep(4)


def gen_image(p, prompt, ref):
    """-> (reference id for the next shot, download url). Topview references by fileId, Kie by URL."""
    model = p["image_model"] or IMAGE_MODELS[p["image_provider"]]
    if p["image_provider"] == "topview":
        return topview(model, prompt, [ref] if ref else [], p["aspect"])
    url = kie(model, {"prompt": prompt, "image_input": [ref] if ref else [], "aspect_ratio": p["aspect"],
                      "resolution": "1K", "output_format": "png"})
    return url, url


def style_text(p):
    path = HERE.parent / "references/style-guide.md" if p["style"] == "default" else Path(p["style"]).expanduser()
    m = re.search(r"## Prompt block\s*\n(.+?)(\n## |\Z)", path.read_text(), re.S)
    return (m[1] if m else path.read_text()).strip()


def cmd_images(job, redo=None):
    p = prefs()
    shots = load_shots(job)
    style = style_text(p)
    (job / "images").mkdir(exist_ok=True)
    if redo is not None:
        shots[redo].pop("image_url", None)
        shots[redo].pop("image_ref", None)
        shots[redo].pop("video_url", None)
    for i, s in enumerate(shots):
        img = job / "images" / f"{i:02d}.png"
        if not s.get("image_url") or not img.exists():
            # ponytail: sequential on purpose — each image references the previous one to hold the style
            ref = shots[i - 1].get("image_ref") if i else None
            prompt = f"{s['prompt']}\n\nStyle: {style}"
            if ref:
                prompt += "\nMatch the visual style, palette and rendering of the reference image; new subject."
            s["image_ref"], s["image_url"] = gen_image(p, prompt, ref)
            img.write_bytes(http(s["image_url"], raw=True))
            save_shots(job, shots)
            print(f"image {i:02d} ({s['start']:.1f}s) {s.get('anchor', '')}")
        if p["visuals"] == "video" and not s.get("video_url"):
            (job / "clips").mkdir(exist_ok=True)
            s["video_url"] = kie(p["video_model"], {"prompt": s.get("motion", s["prompt"]),
                                                    "image_urls": [s["image_url"]], "sound": False,
                                                    "duration": "5" if s["end"] - s["start"] <= 5 else "10"}, 15)
            (job / "clips" / f"{i:02d}.mp4").write_bytes(http(s["video_url"], raw=True))
            save_shots(job, shots)
            print(f"clip  {i:02d} animated")
    print(f"{len(shots)} shots ready in {job / 'images'}")


# ---------- assemble ----------

def cmd_assemble(job, name):
    p = prefs()
    w, h = CANVAS[p["aspect"]]
    shots = load_shots(job)
    tmp = job / ".segments"
    tmp.mkdir(exist_ok=True)
    fit = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS},format=yuv420p"
    for i, s in enumerate(shots):
        n = round((s["end"] - s["start"]) * FPS)
        clip = job / "clips" / f"{i:02d}.mp4"
        src = ["-stream_loop", "-1", "-i", str(clip)] if clip.exists() else ["-loop", "1", "-i", str(job / "images" / f"{i:02d}.png")]
        subprocess.run(["ffmpeg", "-v", "error", "-y", *src, "-vf", fit, "-frames:v", str(n), "-an",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", str(tmp / f"{i:02d}.mp4")], check=True)
    (tmp / "list.txt").write_text("".join(f"file '{i:02d}.mp4'\n" for i in range(len(shots))))
    out = job / "visuals.mp4"  # silent: the voiceover goes on its own audio track below
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                    "-c", "copy", str(out)], check=True)
    cuts = {"clip": out.name, "fps": FPS,
            "segments": [{"clip": out.name, "start": s["start"], "end": s["end"], "note": s.get("anchor", "")}
                         for s in shots]}
    b = bridge()
    b.create_draft(name, out, cuts, w, h)
    b.add_audio(name, job / "voiceover.mp3", 0.0)


# ---------- ken burns ----------

def kenburns_points(i, dur_us, strength):
    """Alternate zoom-in / zoom-out so consecutive shots don't all push the same way."""
    a, b = (1.0, strength) if i % 2 == 0 else (strength, 1.0)
    return [(0, a), (dur_us, b)]


def cmd_kenburns(job, name):
    p = prefs()
    b = bridge()
    strength = float(p["ken_burns"])
    videos = {i for i in range(len(load_shots(job))) if (job / "clips" / f"{i:02d}.mp4").exists()}

    def mutate(d, folder):
        main = next(t for t in d["tracks"] if t["flag"] == 0)
        for i, seg in enumerate(main["segments"]):
            if i in videos:
                continue
            src = seg["source_timerange"]["start"]
            kfs = [e for e in seg.get("common_keyframes", []) if e["property_type"] not in b.KF_TYPES["scale"]]
            for ptype in b.KF_TYPES["scale"]:
                kfs.append({"id": b.uid(), "material_id": "", "property_type": ptype, "keyframe_list": [
                    {"id": b.uid(), "curveType": "Line", "time_offset": src + t,
                     "left_control": {"x": 0.0, "y": 0.0}, "right_control": {"x": 0.0, "y": 0.0},
                     "values": [v], "string_value": "", "graphID": ""}
                    for t, v in kenburns_points(i, seg["target_timerange"]["duration"], strength)]})
            seg["common_keyframes"] = kfs
        print(f"ken burns on {len(main['segments']) - len(videos)} shots (1.0 <-> {strength})")
    b.edit_draft(name, mutate)


# ---------- captions ----------

def caption_lines(words, per_line):
    """Group words into short lines: break at per_line words, sentence ends, or pauses."""
    lines, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        if (len(cur) >= per_line or w["text"][-1] in ".!?" or not nxt or nxt["start"] - w["end"] > 0.4):
            lines.append(cur)
            cur = []
    return lines


def caption_events(words, per_line, upper):
    """One event per spoken word: the whole line on screen, that word highlighted,
    held until the next word starts (or its own end, at a line break)."""
    events = []
    for line in caption_lines(words, per_line):
        texts = [(w["text"].upper() if upper else w["text"]) for w in line]
        text = " ".join(texts)
        pos = 0
        for j, w in enumerate(line):
            end = line[j + 1]["start"] if j + 1 < len(line) else w["end"]
            events.append({"text": text, "at": w["start"], "dur": max(end - w["start"], 1 / FPS),
                           "word": texts[j].strip(".,!?;:\"'"), "from": pos})
            pos += len(texts[j]) + 1
    return events


def cmd_captions(job, name):
    p = prefs()
    b = bridge()
    cap = load("add_caption", CAPCUT / "subtitles/scripts/add_caption.py")
    words = json.loads((job / "words.json").read_text())
    events = caption_events(words, int(p["caption_words"]), p["caption_case"] == "upper")

    def mutate(d, folder):
        for t in d["tracks"]:  # re-running replaces captions instead of stacking them
            if t["type"] == "text":
                t["segments"] = []
        for e in events:
            seg = cap.append_caption(d, b, e["text"], e["at"], e["dur"], highlight=e["word"] or None,
                                     highlight_color=p["caption_highlight"], color=p["caption_color"],
                                     highlight_from=e["from"])
            seg["clip"]["transform"] = {"x": 0.0, "y": float(p["caption_y"])}
            seg["clip"]["scale"] = {"x": 1.0, "y": 1.0}
        print(f"{len(events)} caption events on {len(caption_lines(words, int(p['caption_words'])))} lines")
    b.edit_draft(name, mutate)


# ---------- selftest ----------

def selftest():
    assert chunks("A b. C d. E f.", 8) == ["A b.", "C d.", "E f."]
    assert spoken_text("# Title\n\nHello there.\n> note\nBye.") == "Hello there. Bye."
    s = normalize([{"start": 3.0}, {"start": 0.4}], 7.0)
    assert (s[0]["start"], s[0]["end"], s[1]["start"], s[1]["end"]) == (0, 3.0, 3.0, 7.0)
    assert kenburns_points(0, 10, 1.1) == [(0, 1.0), (10, 1.1)]
    assert kenburns_points(1, 10, 1.1) == [(0, 1.1), (10, 1.0)]
    words = [{"text": t, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, t in enumerate(["go", "go", "now.", "Then", "stop."])]
    assert [len(l) for l in caption_lines(words, 3)] == [3, 2]
    ev = caption_events(words, 3, True)
    assert ev[1]["text"] == "GO GO NOW." and ev[1]["word"] == "GO" and ev[1]["from"] == 3
    assert ev[2]["word"] == "NOW" and abs(ev[2]["dur"] - 0.4) < 1e-9
    assert abs(ev[0]["dur"] - 0.5) < 1e-9
    print("selftest OK")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["tts", "transcribe", "images", "assemble", "kenburns", "captions"])
    ap.add_argument("job", type=Path)
    ap.add_argument("--name")
    ap.add_argument("--redo", type=int)
    a = ap.parse_args()
    job = a.job.expanduser().resolve()
    if a.cmd in ("assemble", "kenburns", "captions") and not a.name:
        sys.exit("--name <draft> required")
    {"tts": lambda: cmd_tts(job), "transcribe": lambda: cmd_transcribe(job),
     "images": lambda: cmd_images(job, a.redo), "assemble": lambda: cmd_assemble(job, a.name),
     "kenburns": lambda: cmd_kenburns(job, a.name), "captions": lambda: cmd_captions(job, a.name)}[a.cmd]()


if __name__ == "__main__":
    main()
