"""Word-level transcript of a video with Deepgram (nova-2).

  transcribe.py <video> <out_dir>   -> out_dir/transcript.json (words) + transcript.md (timed utterances)

Key: $DEEPGRAM_API_KEY, else env.DEEPGRAM_API_KEY in ~/.claude/settings.json.
Exit code 2 = no key (caller falls back to `npx hyperframes transcribe`).
"""
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

PARAMS = "model=nova-2&smart_format=true&punctuate=true&paragraphs=true&utterances=true"


def key():
    k = os.environ.get("DEEPGRAM_API_KEY")
    if k:
        return k
    settings = Path.home() / ".claude" / "settings.json"
    if settings.exists():
        return json.loads(settings.read_text()).get("env", {}).get("DEEPGRAM_API_KEY")


def tc(t):
    m, s = divmod(t, 60)
    return f"{int(m)}:{s:05.2f}"


video, out = Path(sys.argv[1]), Path(sys.argv[2])
k = key()
if not k:
    print("no DEEPGRAM_API_KEY — use `npx hyperframes transcribe` instead", file=sys.stderr)
    sys.exit(2)
out.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    mp3 = Path(tmp) / "audio.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-b:a", "96k", str(mp3)], check=True)
    req = urllib.request.Request(
        f"https://api.deepgram.com/v1/listen?{PARAMS}",
        data=mp3.read_bytes(),
        headers={"Authorization": f"Token {k}", "Content-Type": "audio/mpeg"},
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        res = json.load(r)

alt = res["results"]["channels"][0]["alternatives"][0]
words = [{"word": w.get("punctuated_word", w["word"]), "start": w["start"], "end": w["end"]} for w in alt["words"]]
(out / "transcript.json").write_text(json.dumps({"words": words, "duration": res["metadata"]["duration"]}, indent=1))
lines, cur = [], []
for w in words:
    cur.append(w)
    if w["word"][-1:] in ".?!" or w is words[-1]:
        lines.append(f"[{tc(cur[0]['start'])}–{tc(cur[-1]['end'])}] " + " ".join(x["word"] for x in cur))
        cur = []
(out / "transcript.md").write_text("\n".join(lines) + "\n")
print(json.dumps({"words": len(words), "duration": res["metadata"]["duration"], "md": str(out / "transcript.md")}))
