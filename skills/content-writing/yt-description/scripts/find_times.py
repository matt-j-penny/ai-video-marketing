#!/usr/bin/env python3
"""Find where chapter-opening lines land on the final video's timeline.

You pick the chapter boundaries from the script (you know the structure), then
this tells you the timestamp of each one by fuzzy-matching your phrase against
the word index built by chapter_index.sh. Token-lean by design: you never read
the index, you read N lines of output.

Usage:
  find_times.py --index idx.tsv --phrases phrases.txt
  find_times.py --index idx.tsv "so without further ado" "the first thing I did"

phrases.txt = one phrase per line, in running order. Blank lines and lines
starting with # are ignored. A phrase should be 5-10 words of what the creator
actually SAYS at the start of that chapter (not the chapter title).

Output columns: TIME | SCORE | your phrase | what matched in the video
SCORE below 0.6 means the phrase probably isn't in the final cut (line was cut,
or you're matching a section that got dropped). Never ship a low-score time.
"""

import argparse
import re
import sys
from difflib import SequenceMatcher

# The index holds real words (faster-whisper word timestamps, one row per word).
# Apostrophes are still dropped on both sides so a contraction tokenizes the
# same way in the phrase and in the index ("you're" -> "you" + "re"): symmetric
# tokenization is what keeps the window length honest.
WORD_RE = re.compile(r"[a-z0-9]+")


def norm(text):
    return WORD_RE.findall(text.lower())


def load_index(path):
    times, words = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 2:
                continue
            for w in norm(parts[1]):
                times.append(float(parts[0]))
                words.append(w)
    return times, words


def fmt(seconds):
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def best_match(phrase_tokens, times, words, start_at=0):
    """Slide a phrase-sized window over the index, keep the best-scoring one."""
    n = len(phrase_tokens)
    if n == 0 or not words:
        return None
    best = (0.0, None, "")
    for i in range(start_at, max(start_at + 1, len(words) - n + 1)):
        window = words[i:i + n]
        score = SequenceMatcher(None, phrase_tokens, window).ratio()
        if score > best[0]:
            best = (score, i, " ".join(window))
        if score == 1.0:
            break
    score, idx, matched = best
    return (score, times[idx], matched, idx) if idx is not None else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", required=True)
    ap.add_argument("--phrases", help="file with one phrase per line")
    ap.add_argument("rest", nargs="*", help="phrases as arguments instead")
    args = ap.parse_args()

    if args.phrases:
        with open(args.phrases, encoding="utf-8") as f:
            phrases = [l.strip() for l in f
                       if l.strip() and not l.lstrip().startswith("#")]
    else:
        phrases = args.rest
    if not phrases:
        print("no phrases given", file=sys.stderr)
        return 64

    times, words = load_index(args.index)
    if not words:
        print(f"empty index: {args.index}", file=sys.stderr)
        return 65

    cursor = 0          # chapters run forward — never match backwards
    low = False
    for phrase in phrases:
        hit = best_match(norm(phrase), times, words, start_at=cursor)
        if not hit:
            print(f"  ?   | 0.00 | {phrase} | <no match>")
            continue
        score, when, matched, idx = hit
        flag = "" if score >= 0.6 else "   <-- LOW, verify by hand"
        low = low or score < 0.6
        print(f"{fmt(when):>7} | {score:.2f} | {phrase} | {matched}{flag}")
        if score >= 0.6:
            cursor = min(idx + max(1, len(norm(phrase))), len(words) - 1)

    if low:
        sys.stdout.flush()
        print("\nLow-score rows above are not usable timestamps: that line isn't in "
              "the final cut. Pick a different opening phrase from the same beat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
