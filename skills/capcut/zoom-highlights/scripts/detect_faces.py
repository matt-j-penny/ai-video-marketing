# /// script
# requires-python = ">=3.10"
# dependencies = ["opencv-python-headless", "numpy"]
# ///
"""uv run detect_faces.py <video> --at 4.2 12.7 30.1
   uv run detect_faces.py <video> --start 0 --end 60 --interval 2

Face box at each requested timestamp. YuNet detector (bundled model), largest
face per frame. Prints normalized boxes (0-1 of the source frame) as JSON.

Standalone adaptation of the Edit Pipeline's stages/faces.py — same detector
and model, no dependency on that pipeline's job/state.json/cuts.json layout.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODEL = Path(__file__).resolve().parent.parent / "models" / "face_detection_yunet_2023mar.onnx"


def probe_dims(video):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", video],
        capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split("x")
    return int(w), int(h)


def main():
    import cv2

    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--at", type=float, nargs="+", help="explicit timestamps (seconds)")
    ap.add_argument("--start", type=float, default=None)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--interval", type=float, default=2.0)
    args = ap.parse_args()

    if not MODEL.exists():
        sys.exit(f"missing model: {MODEL}")

    if args.at:
        times = list(args.at)
    elif args.start is not None and args.end is not None:
        times = []
        t = args.start
        while t < args.end:
            times.append(round(t, 3))
            t += args.interval
    else:
        sys.exit("pass either --at t1 t2 ... or --start/--end[/--interval]")

    src_w, src_h = probe_dims(args.video)
    tmp = tempfile.mkdtemp()

    def grab(i_t):
        i, t = i_t
        out = str(Path(tmp) / f"{i:05d}.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", args.video,
                        "-frames:v", "1", "-vf", "scale=640:-2", "-q:v", "4", "-y", out],
                       capture_output=True)
        return out

    with ThreadPoolExecutor(8) as ex:
        files = list(ex.map(grab, enumerate(times)))

    det = None
    samples = []
    for t, f in zip(times, files):
        img = cv2.imread(f)
        if img is None:
            samples.append({"t": t, "face": None})
            continue
        h, w = img.shape[:2]
        if det is None:
            det = cv2.FaceDetectorYN_create(str(MODEL), "", (w, h), score_threshold=0.6)
        det.setInputSize((w, h))
        _, faces = det.detect(img)
        if faces is None or len(faces) == 0:
            samples.append({"t": t, "face": None})
            continue
        x, y, bw, bh, *rest = max(faces, key=lambda d: d[2] * d[3])
        samples.append({"t": t, "face": {
            "cx": round((float(x) + float(bw) / 2) / w, 4),
            "cy": round((float(y) + float(bh) / 2) / h, 4),
            "w": round(float(bw) / w, 4), "h": round(float(bh) / h, 4),
            "conf": round(float(rest[-1]), 3)}})

    found = [s["face"] for s in samples if s["face"]]
    result = {"source": {"w": src_w, "h": src_h}, "samples": samples,
              "detected": len(found), "missing": len(samples) - len(found)}
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
