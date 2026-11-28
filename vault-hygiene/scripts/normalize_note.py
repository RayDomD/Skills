"""T2 mechanical normalization. Content-preserving markup fixes only.

Transforms
  A. strip OneNote/pandoc backslash escape artifacts   -- all notes in scope.enforced
  B. lone **Bold line** -> real heading                -- scope list only
  C. collapse runs of blank/whitespace-only lines      -- scope list only
  D. order existing frontmatter keys (never add keys)  -- scope list only

Never touches fenced code blocks or inline code spans.

Run from the vault root (or set VAULT_ROOT).
    normalize_note.py <path>            dry run over one note or one folder
    normalize_note.py <path> --report   dry run, listing every heading it would create
    normalize_note.py <path> --apply    write the changes
    normalize_note.py                   no path: the whole T2 scope at once

Verification is structural, not word-count based: a bold line becoming a heading changes the
whitespace-separated word count without changing any content. Instead the body's alphanumeric
token sequence must be identical, and frontmatter must be a permutation of the original.

This is Phase 1 of the skill's Mode B. Phase 2 (type, summary, aliases, inline links) is
judgment work and is never scripted.
"""
import os, re, sys, difflib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _standard

VAULT = os.environ.get("VAULT_ROOT") or os.getcwd()
DIRS = _standard.scope_dirs(VAULT)

# --- scope -------------------------------------------------------------
FM_RE = re.compile(r"^---\r?\n.*?\r?\n---\r?\n", re.S)
HEADING_RE = re.compile(r"^#{1,6} \S", re.M)

# --- A: escapes --------------------------------------------------------
# Deliberately NOT stripped, these are real content, not import artifacts:
#   \$  guards Obsidian math mode ("\$160k" -> "$160k ... $250k" would render as math)
#   \"  \\  \t  \n   inside shell/JSON transcripts and a note *about* escape chars
#   \<  \>  when paired as \<placeholder\>  (unescaping yields a swallowed HTML tag)
#   \|  one note has a table crushed onto a single line; repairing it is content work
#   \   (backslash + NBSP) shell line continuations
# \> is only ever needed at the start of a line, where a bare > would open a blockquote.
# Anywhere else it is an import artifact:  -\>  /  - \>  /  ────\>  /  Agent \> workflows.
# requires non-space earlier on the line, so a line-start "- \>" list bullet never matches
ARROW_RE = re.compile(r"(?<=\S)([ \t]*)([-=])[ \t]*\\>")  # "a -\> b" / "a - \> b" -> "a -> b"
GT_RE    = re.compile(r"(?<=\S)\\>|(?<=[ \t])\\>")  # any other mid-line \>  ->  >
GT_START = re.compile(r"^\s*(?:>[ \t]*)*\\>")       # line-start: keep, a bare > would quote
PUNCT_RE   = re.compile(r"\\([*_\[\]])")         # \* \_ \[ \]
ORDINAL_RE = re.compile(r"^(\s*\d+)\\\.", re.M)  # 1\.  =>  1.
DASH_RE    = re.compile(r"^(\s*)\\-(\s)", re.M)  # \- x =>  - x
HASH_RE    = re.compile(r"(?<=[^\s])\\#|\\#(?=\d)")  # \#1 => #1, never at line start

CODE_FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

def strip_escapes_line(line):
    # \<placeholder\> pairs are left intact: unescaping only the > yields a swallowed HTML tag
    do_gt = "\\<" not in line and not GT_START.match(line)
    parts, last = [], 0
    for m in INLINE_CODE_RE.finditer(line):          # protect inline code spans
        parts.append((line[last:m.start()], True))
        parts.append((m.group(0), False))
        last = m.end()
    parts.append((line[last:], True))
    out = []
    for text, editable in parts:
        if editable:
            if do_gt:
                text = ARROW_RE.sub(r"\1\2>", text)
                text = GT_RE.sub(">", text)
            text = PUNCT_RE.sub(r"\1", text)
            text = ORDINAL_RE.sub(r"\1.", text)
            text = DASH_RE.sub(r"\1-\2", text)
            text = HASH_RE.sub("#", text)
        out.append(text)
    return "".join(out)

# --- B: bold line -> heading ------------------------------------------
BOLD_LINE_RE = re.compile(r"^\*\*(.+?)\*\*$")
MAX_HEADING_LEN = 60

def is_heading_candidate(line):
    m = BOLD_LINE_RE.match(line.strip())
    if not m:
        return None
    content = m.group(1).strip()
    if "**" in content or not content:
        return None
    if len(content) > MAX_HEADING_LEN:
        return None                                   # a bolded sentence, not a heading
    if content[-1] in ".:!,;":
        return None                                   # "...for every table:" / "...the minimum."
    if ". " in content:
        return None                                   # multi-sentence emphasis
    return content

def is_blank(line):
    return line.strip().strip("\u00a0\u200b") == ""

# --- D: frontmatter key order -----------------------------------------
KEY_ORDER = ["type", "title", "summary", "status", "aliases", "author", "source",
             "created", "date", "date_clipped", "date_started", "due_date",
             "course", "area", "project", "repo", "progress", "trigger",
             "lesson", "positions", "auth", "tags"]
KEY_RE = re.compile(r"^([A-Za-z_][\w-]*):")

def reorder_frontmatter(lines):
    """lines = full file as list. Returns new list. Only reorders top-level keys
    whose blocks are contiguous; bails out on anything it does not fully understand."""
    if not lines or lines[0].strip() != "---":
        return lines
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return lines
    blocks, cur = [], None
    for ln in lines[1:end]:
        m = KEY_RE.match(ln)
        if m:
            cur = [m.group(1), [ln]]
            blocks.append(cur)
        elif cur is not None and (ln.startswith((" ", "\t", "-")) or ln.strip() == ""):
            cur[1].append(ln)
        else:
            return lines                              # unparsed line: leave alone
    names = [b[0] for b in blocks]
    if len(set(names)) != len(names):
        return lines
    if any(n not in KEY_ORDER for n in names):
        return lines
    ordered = sorted(blocks, key=lambda b: KEY_ORDER.index(b[0]))
    if [b[0] for b in ordered] == names:
        return lines
    body = [l for b in ordered for l in b[1]]
    return ["---"] + body + lines[end:]

# --- driver ------------------------------------------------------------
def transform(text, in_scope):
    lines = text.split("\n")
    if in_scope:
        lines = reorder_frontmatter(lines)

    # locate frontmatter end so heading logic ignores it
    fm_end = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                fm_end = i + 1
                break

    # pass 1: escapes (A), everywhere outside code fences
    out, in_fence = [], False
    for ln in lines:
        if CODE_FENCE_RE.match(ln):
            in_fence = not in_fence
            out.append(ln)
            continue
        out.append(ln if in_fence else strip_escapes_line(ln))
    lines = out
    if not in_scope:
        return "\n".join(lines)

    # pass 2: which bold lines qualify, and at what level (B)
    cands, in_fence = [], False
    for i, ln in enumerate(lines):
        if CODE_FENCE_RE.match(ln):
            in_fence = not in_fence
            continue
        if in_fence or i < fm_end:
            continue
        c = is_heading_candidate(ln)
        if c and ln == ln.strip():                    # unindented only (not list items)
            cands.append((i, c))
    title_idx = None
    if cands:
        first_content = next((i for i in range(fm_end, len(lines)) if not is_blank(lines[i])), None)
        if cands[0][0] == first_content:
            title_idx = cands[0][0]

    # pass 3: rewrite headings and collapse padding (B + C)
    out, in_fence, blank_run = [], False, 0
    for i, ln in enumerate(lines):
        if CODE_FENCE_RE.match(ln):
            in_fence = not in_fence
        if not in_fence and i >= fm_end and is_blank(ln):
            blank_run += 1
            if blank_run == 1:
                out.append("")
            continue
        blank_run = 0
        hit = next((c for j, c in cands if j == i), None)
        if hit is not None:
            level = "##" if i == title_idx else ("###" if title_idx is not None else "##")
            out.append(f"{level} {hit}")
        else:
            out.append(ln)
    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.rstrip("\n") + "\n"

def collect(target=None):
    """target: a note or a folder, relative to the vault root. None = the whole T2 scope.

    A note named explicitly is always treated as in scope for the heading and padding
    transforms; without a target, only notes matching the >300-words-and-<=1-heading audit
    get them, and everything else gets escape-stripping alone."""
    roots = [os.path.join(VAULT, d) for d in DIRS]
    explicit = None
    if target:
        t = os.path.normpath(os.path.join(VAULT, target))
        if not os.path.exists(t):
            sys.exit(f"no such note or folder: {target}")
        if os.path.isfile(t):
            explicit, roots = {t}, [t]
        else:
            roots = [t]

    scope, allnotes = set(), []
    for r in roots:
        walk = [(os.path.dirname(r), None, [os.path.basename(r)])] if os.path.isfile(r) \
               else os.walk(r)
        for root, _, files in walk:
            for f in sorted(files):
                if not f.endswith(".md"):
                    continue
                p = os.path.join(root, f)
                allnotes.append(p)
                if explicit and p in explicit:
                    scope.add(p)
                    continue
                body = FM_RE.sub("", open(p, encoding="utf-8").read(), count=1)
                if len(body.split()) > 300 and len(HEADING_RE.findall(body)) <= 1:
                    scope.add(p)
    return scope, allnotes

ALNUM_RE = re.compile(r"[^0-9A-Za-z]+")

def split_fm(text):
    """-> (frontmatter_lines, body). Frontmatter compared as a multiset (reordering is
    legal); body compared as an alphanumeric token sequence (nothing may move)."""
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return sorted(lines[1:i]), "\n".join(lines[i + 1:])
    return [], text

def content_signature(text):
    fm, body = split_fm(text)
    return fm, ALNUM_RE.sub(" ", body).split()

def main():
    apply = "--apply" in sys.argv
    report = "--report" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    scope, allnotes = collect(args[0] if args else None)
    changed, fails, headings = [], [], []
    for p in allnotes:
        raw = open(p, encoding="utf-8", newline="").read()
        # CRLF is normalized to LF, not refused. Notes authored on Windows or imported
        # from outside the vault routinely carry it, and refusing them made the tool look
        # broken on exactly the files it exists for. This is safe: the file is written
        # back with newline="" so LF is what lands on disk, git stores LF anyway, and the
        # preservation check below compares an alphanumeric token sequence, which is blind
        # to line endings -- so it still verifies honestly. A CR-only change is a change.
        orig = raw.replace("\r\n", "\n").replace("\r", "\n")
        new = transform(orig, p in scope)
        if new == raw:
            continue
        rel = os.path.relpath(p, VAULT)
        ofm, obody = content_signature(orig)
        nfm, nbody = content_signature(new)
        if obody != nbody:
            i = next((k for k in range(min(len(obody), len(nbody))) if obody[k] != nbody[k]), 0)
            fails.append((rel, f"body text changed near token {i}: "
                               f"{obody[i:i+6]} -> {nbody[i:i+6]}"))
        if ofm != nfm:
            fails.append((rel, "frontmatter is not a permutation of the original"))
        changed.append(rel)
        for ln in new.split("\n"):
            if ln.startswith(("## ", "### ")) and ln not in orig.split("\n"):
                headings.append((rel, ln))
        if apply:
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
    print(f"scope notes: {len(scope)}   files changed: {len(changed)}")
    if report:
        cur = None
        for rel, ln in headings:
            if rel != cur:
                print(f"\n{rel}")
                cur = rel
            print(f"    {ln}")
        print(f"\n{len(headings)} headings created")
    else:
        for c in changed:
            print("  ", c)
    if fails:
        print("\n!! CONTENT-PRESERVATION FAILURES:")
        for r, why in fails:
            print(f"   {r}: {why}")
    else:
        print("\nOK: body text and frontmatter content preserved in every file.")

if __name__ == "__main__":
    main()
