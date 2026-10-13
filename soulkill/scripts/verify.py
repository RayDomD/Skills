#!/usr/bin/env python
"""
Verify a brain against its raw corpus.

Usage:
  verify.py check <slug>
  verify.py phrases <slug> [--type video|writing|local] "<phrase>" ["<phrase>" ...]

check    Every brain file exists, _hot.md fits its budget, every source id cited
         exists, and every quote attributed to a source id, like "..." (S095),
         appears verbatim in that source. Exit code 1 on any failure.
phrases  How many sources use each phrase, and how often. Feeds the counts in voice.md.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus import BRAINS, read_source, source_files  # noqa: E402

BRAIN_FILES = ["_hot.md", "frameworks.md", "principles.md", "positions.md", "stories.md",
               "voice.md", "books.md", "sources.md", "persona.md"]
HOT_MAX_BYTES = 5000  # the hot sheet is read on every question, so it stays one page
MIN_QUOTE_WORDS = 2
ATTRIBUTION_REACH = 40  # characters allowed between a closing quote and its (S001)
ID = r"S\d{3,}"


def norm(text):
    text = re.sub(r"\[\d+:\d\d(:\d\d)?\]", " ", text)  # caption timestamps
    text = text.lower().replace("’", "").replace("‘", "").replace("'", "")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", text)).strip()


def load_corpus(slug, kind=None):
    """Return {source id: normalized text} for sources that were not dropped."""
    corpus = {}
    for path in source_files(slug):
        fm, body = read_source(path)
        if fm.get("id") and not fm.get("dropped") and kind in (None, fm.get("type")):
            corpus[fm["id"]] = norm(body)
    return corpus


def attributed_quotes(text):
    """Yield (quote, source id) for each quoted span followed closely by a source id."""
    for line in text.replace("“", '"').replace("”", '"').splitlines():
        marks = [i for i, ch in enumerate(line) if ch == '"']
        for start, end in zip(marks[::2], marks[1::2]):
            tail = line[end + 1: end + 1 + ATTRIBUTION_REACH]
            m = re.match(rf'[^"]*?[(\[]({ID})', tail)
            if m:
                yield line[start + 1: end], m.group(1)


def cmd_check(args):
    brain, corpus, problems = BRAINS / args.slug, load_corpus(args.slug), []
    if not corpus:
        sys.exit(f"no indexed sources for {args.slug}; run corpus.py index first")

    for name in BRAIN_FILES:
        if not (brain / name).exists():
            problems.append(f"MISSING FILE  {name}")
    hot = brain / "_hot.md"
    if hot.exists() and hot.stat().st_size > HOT_MAX_BYTES:
        problems.append(f"HOT TOO LONG  _hot.md is {hot.stat().st_size} bytes, budget {HOT_MAX_BYTES}")

    verified = 0
    for path in sorted(brain.glob("*.md")):
        if path.name == "sources.md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for sid in sorted(set(re.findall(rf"\b{ID}\b", text)) - set(corpus)):
            problems.append(f"UNKNOWN ID    {path.name}: {sid}")
        for quote, sid in attributed_quotes(text):
            parts = [norm(p) for p in re.split(r"\.\.\.|…", quote)]
            parts = [p for p in parts if len(p.split()) >= MIN_QUOTE_WORDS]
            if not parts or sid not in corpus:
                continue
            if all(p in corpus[sid] for p in parts):
                verified += 1
                continue
            elsewhere = [other for other, body in corpus.items() if all(p in body for p in parts)]
            where = f"WRONG ID      found in {', '.join(elsewhere[:3])}, not" if elsewhere else "NOT IN SOURCE "
            problems.append(f'{where} {sid}  {path.name}: "{quote[:140]}"')

    print(f"quotes verified: {verified}; problems: {len(problems)}")
    print("\n".join(problems))
    sys.exit(1 if problems else 0)


def cmd_phrases(args):
    corpus = load_corpus(args.slug, args.type)
    print(f"{len(corpus)} sources" + (f" of type {args.type}" if args.type else ""))
    print("sources\tuses\tphrase")
    for phrase in args.phrases:
        needle = f" {norm(phrase)} "
        counts = [f" {body} ".count(needle) for body in corpus.values()]
        print(f"{sum(1 for c in counts if c)}\t{sum(counts)}\t{phrase}")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("phrases")
    p.add_argument("slug")
    p.add_argument("--type", choices=["video", "writing", "local"])
    p.add_argument("phrases", nargs="+")
    p.set_defaults(fn=cmd_phrases)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
