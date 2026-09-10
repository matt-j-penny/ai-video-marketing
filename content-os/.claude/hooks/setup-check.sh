#!/usr/bin/env bash
# SessionStart hook: on a fresh install, inject a reminder telling Claude to run the
# onboarding flow (CLAUDE.md "FIRST RUN" gate) before doing anything else. Emits NOTHING
# once setup AND personalization are done. Always exits 0 so it can never break a session.
#
# Pure bash + printf on purpose (NO jq / python dependency): on a brand-new machine those
# may not be installed yet, and this is the very hook that's supposed to get them installed.
# Runs on macOS, Linux, and Windows (Claude Code on Windows runs hooks through Git Bash).
#
# cwd is the project root. Two deterministic states:
#   tools done      = the .setup-complete marker exists (written by ./setup.sh after verify)
#   personalized    = CLAUDE.md contains no <<ALL_CAPS>> placeholder tokens (written by "apply my brand kit")

TOOLS=0; BRAND=0
[ -f .setup-complete ] && TOOLS=1
if [ -f CLAUDE.md ] && ! grep -qE '<<[A-Z][A-Z0-9_]*(:[^>]*)?>>' CLAUDE.md 2>/dev/null; then BRAND=1; fi

if [ "$TOOLS" -eq 0 ] && [ -f check-setup.sh ]; then
  msg='⚠️ FRESH INSTALL: setup has not finished yet (no .setup-complete marker).\n\nFollow the FIRST RUN gate in CLAUDE.md before running any skill:\n  1. Run ./setup.sh yourself (no need to ask). It detects the OS, installs every missing tool, pre-builds the transcription engine + carousel renderer, verifies with ./check-setup.sh, then prints the CONNECTIONS checklist. It is idempotent; re-run it any time.\n  2. Handle its exit codes: 2 = walk the user through restarting Claude Code, then re-run it. 1 = read the output and fix what it names (Homebrew one-liner on macOS, sudo apt lines on Linux). 0 = tools done: check which MCPs are already connected (ToolSearch for notion-search, call-actor, tabs_context_mcp) and list only the missing connections, once, in one message.\n  3. Then offer the brand kit (fill brand-kit.md, say apply my brand kit). Personalization is what makes scriptwriter/hooks/carousels sound like the user; the research skills work before it.\n\nIf the user asks for a skill right now, run setup first (nothing transcribes or renders without the tools).'
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$msg"
elif [ "$BRAND" -eq 0 ] && [ -f brand-kit.md ]; then
  msg='ℹ️ Tools are installed but the system is not personalized yet: CLAUDE.md still has ALL-CAPS <<placeholder>> tokens. If the user asks for anything voice- or offer-dependent (scripts, hooks, carousels, captions, DMs, descriptions), first run the brand-kit flow in CLAUDE.md (fill brand-kit.md Part A, then apply it: CLAUDE.md profile, backbone/, competitor-list.md, Notion DB via notion-create-database into notion-pipeline.md, auto-poster .env, then voice-corpus-builder to build voice-corpus/ + voice-dna.md). Research and transcription skills work without it; do not block those.'
  printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$msg"
fi
exit 0
