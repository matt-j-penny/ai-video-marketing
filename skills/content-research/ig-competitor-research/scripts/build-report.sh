#!/usr/bin/env bash
# build-report.sh : run build-report.py on the shared build-once pillow venv
# (~/.cache/content-os/pillow-venv; sentinel-gated; no per-run dependency resolution).
set -euo pipefail
command -v uv >/dev/null 2>&1 || { echo "[error] uv is not installed; run ./setup.sh from the project root" >&2; exit 1; }
VENV="${CONTENT_OS_PILLOW_VENV:-$HOME/.cache/content-os/pillow-venv}"
PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
if [ ! -e "$VENV/.deps-ok" ]; then
  echo "[report] first-run: building pillow venv at $VENV" >&2
  rm -rf "$VENV"; uv venv "$VENV" --python 3.11 >&2
  PYBIN="$VENV/bin/python"; [ -e "$PYBIN" ] || PYBIN="$VENV/Scripts/python.exe"
  uv pip install --python "$PYBIN" pillow >&2; touch "$VENV/.deps-ok"
fi
exec "$PYBIN" "$(cd "$(dirname "$0")" && pwd)/build-report.py" "$@"
