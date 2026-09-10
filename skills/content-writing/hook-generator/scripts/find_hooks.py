#!/usr/bin/env python3
"""find_hooks.py — query the proven-hook bank for the hook-generator skill.

Surfaces the highest-performing hook FRAMEWORKS (the templated [X]/[Y] forms)
plus their real proof (example line, view count, source link), ranked by
performance. The CSV is the single source of truth — this just slices it so the
skill never has to load 400 rows into context.

The bank: 404 hooks pulled from top-performing short-form reels, each tagged with
its structure, production notes, source link, and views. performance_rank 1 = the
best-performing tier (avg ~9.5M views); higher numbers = lower tiers.

Usage:
  find_hooks.py --list                              # the 8 structures + counts
  find_hooks.py --structure "secret" --top 15       # top frameworks in one structure
  find_hooks.py --structure all --top 3             # top N per structure (a spread)
  find_hooks.py --keyword ai --top 20               # search hooks/frameworks by word
  find_hooks.py --structure question --keyword money # combine filters

Notes:
  - --structure matches loosely: "secret" -> "Secret Reveal", "contrarian" ->
    "Contrarian/Negative". Case-insensitive substring.
  - Results are de-duped by framework so you get variety, not the same template
    five times.
  - Sorted best-first: performance_rank ascending, then views descending.
"""

import argparse
import csv
import os
import re
import sys

# The shipped bank, one level above scripts/. Override with --bank <path>.
HOOK_BANK = "404-kallaway-hooks.csv"

# Canonical display order for the labels we know (by frequency in the bank).
# The live structure list is derived from the CSV; unknown labels are appended
# (sorted) and flagged on stderr so a swapped-in bank never silently drops rows.
CANONICAL_ORDER = [
    "Educational/Tutorial",
    "Secret Reveal",
    "Contrarian/Negative",
    "Raw Shock",
    "Question",
    "Experimentation",
    "Fortuneteller",
    "Comparison",
]


def structures_in(rows):
    seen = {r["_structure"] for r in rows if r["_structure"]}
    known = [s for s in CANONICAL_ORDER if s in seen]
    unknown = sorted(seen - set(CANONICAL_ORDER))
    if unknown:
        print(f"warning: {len(unknown)} structure label(s) not in the canonical 8: "
              + ", ".join(unknown), file=sys.stderr)
    return known + unknown


def load_rows(bank=None):
    here = os.path.dirname(os.path.abspath(__file__))
    path = bank or os.path.join(here, "..", HOOK_BANK)
    if not os.path.isfile(path):
        sys.exit(f"Hook bank not found: {path} (expected {HOOK_BANK} in the skill folder, or pass --bank <path>).")
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        try:
            r["_rank"] = int(r["performance_rank"])
        except (ValueError, KeyError):
            r["_rank"] = 999
        try:
            r["_views"] = int(r["views"])
        except (ValueError, KeyError):
            r["_views"] = 0
        r["_structure"] = (r.get("spoken_hook_structure") or "").strip()
    return rows


def sort_key(r):
    return (r["_rank"], -r["_views"])


def dedupe(rows):
    seen, out = set(), []
    for r in rows:
        key = (r.get("spoken_hook_framework") or "").strip().lower()
        if key and key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def trunc(s, n=150):
    s = (s or "").strip().replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def fmt(r, idx=None):
    tag = f"{idx}. " if idx is not None else ""
    lines = [
        f"{tag}[{r['_structure']}]  {r['_views']:,} views · rank {r['performance_rank']}",
        f"   framework: {trunc(r.get('spoken_hook_framework'))}",
        f"   example:   {trunc(r.get('spoken_hook'))}",
        f"   source:    {r.get('video_link', '').strip()}",
    ]
    return "\n".join(lines)


def cmd_list(rows, structures):
    print(f"Proven-hook bank: {len(rows)} hooks across {len(structures)} structures\n")
    counts = {s: 0 for s in structures}
    for r in rows:
        if r["_structure"] in counts:
            counts[r["_structure"]] += 1
    for s in structures:
        print(f"  {counts[s]:>4}  {s}")
    print("\nFilter with --structure <name> (loose match) and/or --keyword <word>.")


def main():
    p = argparse.ArgumentParser(description="Query the proven-hook bank.")
    p.add_argument("--structure", help='structure name (loose match) or "all" for a spread')
    p.add_argument("--keyword", help="case-insensitive substring across hooks + frameworks")
    p.add_argument("--top", type=int, default=12, help="how many to return (per structure when --structure all)")
    p.add_argument("--list", action="store_true", help="show the 8 structures and counts")
    p.add_argument("--bank", help=f"path to a hook-bank CSV (default: {HOOK_BANK} in the skill folder)")
    args = p.parse_args()

    rows = load_rows(args.bank)
    structures = structures_in(rows)

    if args.list:
        cmd_list(rows, structures)
        return

    if args.keyword:
        # Word-prefix match so short anchors ("ai") hit the word AI, not "trains".
        pat = re.compile(r"\b" + re.escape(args.keyword), re.IGNORECASE)
        rows = [
            r for r in rows
            if pat.search(r.get("spoken_hook") or "")
            or pat.search(r.get("spoken_hook_framework") or "")
        ]

    rows.sort(key=sort_key)

    # Spread mode: top N per structure.
    if args.structure and args.structure.lower() == "all":
        printed = False
        for s in structures:
            block = dedupe([r for r in rows if r["_structure"] == s])[: args.top]
            if not block:
                continue
            printed = True
            print(f"\n===== {s} =====")
            for i, r in enumerate(block, 1):
                print(fmt(r, i))
                print()
        if not printed:
            print("No matches.")
        return

    # Single-structure or keyword-only mode.
    if args.structure:
        sub = args.structure.lower()
        rows = [r for r in rows if sub in r["_structure"].lower()]

    rows = dedupe(rows)[: args.top]
    if not rows:
        print("No matches. Try --list to see structures, or loosen the keyword.")
        return
    for i, r in enumerate(rows, 1):
        print(fmt(r, i))
        print()


if __name__ == "__main__":
    main()
