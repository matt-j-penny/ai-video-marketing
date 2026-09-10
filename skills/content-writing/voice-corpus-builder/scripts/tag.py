#!/usr/bin/env python3
"""Set the classification tags on one voice-corpus entry's frontmatter.

Claude reads the transcript, decides the tags, then runs (one call per entry):
  tag.py <id> --format giveaway-demo --hook-type bold-claim --spoken-hook "..." [--era current]

Only the given fields change; the rest of the file is untouched. Prints the
remaining TODO count for the whole corpus so you know when tagging is done.
Vocabulary + definitions: ../reference/tags.md
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CORPUS = os.environ.get("VOICE_CORPUS_DIR") or os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "voice-corpus"))
FORMATS = {"giveaway-demo", "tutorial-walkthrough", "case-study", "transparency", "build-in-public",
           "rant", "story", "listicle", "reaction", "vlog", "interview", "other"}
HOOKS = {"bold-claim", "question", "callout", "secret-reveal", "shock-number", "title", "story-open",
         "contrarian", "how-to", "other"}


def set_field(text, key, value):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        sys.exit("no frontmatter block")
    fm = m.group(1)
    line = f"{key}: {value}"
    if re.search(rf"^{key}:.*$", fm, re.M):
        fm = re.sub(rf"^{key}:.*$", line.replace("\\", "\\\\"), fm, flags=re.M)
    else:
        fm += "\n" + line
    return text[: m.start(1)] + fm + text[m.end(1):]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--format", dest="fmt", choices=sorted(FORMATS))
    ap.add_argument("--hook-type", choices=sorted(HOOKS))
    ap.add_argument("--spoken-hook", help="first spoken sentence, verbatim (long-form: the title)")
    ap.add_argument("--era")
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    a = ap.parse_args()

    path = os.path.join(a.corpus, f"{a.id}.md")
    if not os.path.isfile(path):
        sys.exit(f"no such entry: {path}")
    text = open(path, encoding="utf-8").read()
    if a.fmt:
        text = set_field(text, "format", a.fmt)
    if a.hook_type:
        text = set_field(text, "hook_type", a.hook_type)
    if a.spoken_hook is not None:
        s = " ".join(a.spoken_hook.split()).replace('"', "'")
        text = set_field(text, "spoken_hook", f'"{s}"')
    if a.era:
        text = set_field(text, "era", a.era)
    open(path, "w", encoding="utf-8").write(text)

    todo = 0
    for fn in os.listdir(a.corpus):
        if fn.endswith(".md") and fn != "index.md":
            head = open(os.path.join(a.corpus, fn), encoding="utf-8").read(2000)
            if re.search(r"^(format|hook_type|spoken_hook):.*TODO", head, re.M):
                todo += 1
    print(f"tagged {a.id}; {todo} entr{'y' if todo == 1 else 'ies'} still TODO")


if __name__ == "__main__":
    main()
