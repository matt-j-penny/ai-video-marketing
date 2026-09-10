#!/usr/bin/env bash
# carousel-generator — one-shot installer (THE bootstrap for this skill).
# Run once after dropping this folder into <project>/.claude/skills/, from the project root:
#   bash .claude/skills/carousel-generator/install.sh
set -euo pipefail
cd "$(dirname "$0")"
SKILL_REL=".claude/skills/carousel-generator"

echo "▶ carousel-generator setup"

# 1. Node check
if ! command -v node >/dev/null 2>&1; then
  echo "✗ Node.js not found. Install it (https://nodejs.org or 'brew install node'), then re-run." >&2
  exit 1
fi
echo "✓ node $(node -v)"

# 2. Python check (for AI covers via cover.py). Probe by RUNNING it: on Windows
#    `python3` may be the Store stub that resolves but never runs, and the real
#    binary is `python`.
PY=""
if python3 -c '' >/dev/null 2>&1; then PY=python3
elif python -c '' >/dev/null 2>&1; then PY=python
fi
if [ -n "$PY" ]; then
  echo "✓ $("$PY" --version 2>&1) (run cover.py with: $PY)"
else
  echo "⚠ python3/python not found — AI cover generation (cover.py) won't work, but HTML rendering will."
fi

# 3. npm deps (Playwright)
echo "▶ Installing npm dependencies (Playwright)…"
( cd scripts && npm install --no-audit --no-fund )

# 4. Chromium for Playwright (one-time, ~130 MB)
echo "▶ Installing Chromium for Playwright (one-time)…"
( cd scripts && node node_modules/playwright/cli.js install chromium )

# 5. Higgsfield CLI (optional — only needed for AI cover images)
if command -v higgsfield >/dev/null 2>&1; then
  echo "✓ higgsfield CLI found"
else
  echo "⚠ higgsfield CLI not installed (optional — only needed for AI cover images)."
  echo "  Install:  curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh"
  echo "  Then:     higgsfield auth login"
fi

echo
echo "✓ Done. Smoke-test it (from the project root; slides land in carousel/outputs/_smoketest/):"
echo "    node $SKILL_REL/scripts/render.js $SKILL_REL/scripts/smoketest.json --out carousel/outputs/_smoketest --no-open"
[ -n "$PY" ] && echo "  AI covers: $PY $SKILL_REL/scripts/cover.py carousel/outputs/<slug>/carousel.json"
echo "  Or just ask Claude: \"make a carousel about <topic>\""
