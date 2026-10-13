#!/usr/bin/env python
"""
Check every quoted line in a mikoshi session against the brains.

Usage:
  python check_quotes.py <session folder>

Scans round-*.md and verdict.md for quotes attributed to a source id, like
"..." (S095), and looks for each in ~/.claude/brains/. A quote that is in no
brain is either a quote of another seat or the brief (fine if it appears in an
earlier round file of the same session) or an invented quote (remove it from
the report). Exit code 1 if any quote is unaccounted for.
"""
import re
import sys
from pathlib import Path

BRAINS = Path.home() / ".claude" / "brains"
MIN_QUOTE_WORDS = 6  # shorter spans are phrases, not quotes worth verifying
MIN_PART_WORDS = 3  # pieces of an elided quote shorter than this match too easily


def norm(s):
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[^a-z0-9' ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    session = Path(sys.argv[1])
    brain_text = norm(" ".join(p.read_text(encoding="utf-8", errors="replace") for p in BRAINS.rglob("*.md")))
    session_files = sorted(session.glob("round-*.md")) + [p for p in [session / "verdict.md"] if p.exists()]
    brief = norm((session / "brief.md").read_text(encoding="utf-8")) if (session / "brief.md").exists() else ""
    bad, ok, internal = [], 0, 0
    seen_session = ""
    for f in session_files:
        text = f.read_text(encoding="utf-8", errors="replace")
        # only quotes attributed to a source id, e.g. "..." (S095) or "..." [S048, 2026]
        for q in re.findall(r"[\"“]([^\"“”\n]{20,400})[\"”][^\n\"]{0,40}?[\(\[]S\d{3}", text):
            nq = norm(q)
            if len(nq.split()) < MIN_QUOTE_WORDS:
                continue
            # a quote with an ellipsis is checked piece by piece
            parts = [x for x in (norm(part) for part in re.split(r"\.\.\.|…", q)) if len(x.split()) >= MIN_PART_WORDS]
            if parts and all(part in brain_text for part in parts):
                ok += 1
            elif nq in seen_session or nq in brief:
                internal += 1
            else:
                bad.append((f.name, q))
        seen_session += " " + norm(text)
    print(f"brain quotes verified: {ok}; quotes of earlier rounds or the brief: {internal}; unverified: {len(bad)}")
    for name, q in bad:
        print(f"  UNVERIFIED [{name}] \"{q[:160]}\"")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
