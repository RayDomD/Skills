"""Vault-wide title + alias index, for proposing aliases and checking link targets.

Every wikilink target Obsidian can currently resolve, and every wikilink that resolves to
nothing. A link resolves only to a file's basename: Obsidian does NOT follow a bare [[alias]]
(aliases feed autocomplete, which writes [[Note|alias]]). Use it to answer three questions
without guessing:

  - does [[X]] resolve?                      -> "unresolved" section
  - what do other notes already call this?   -> "inbound names" per note
  - how do I fix this rot?                   -> "alias_of" (write [[Note|X]]) or a near-miss

Run from the vault root (or set VAULT_ROOT).
    build_link_index.py                 full index
    build_link_index.py --unresolved    only links that resolve to nothing
    build_link_index.py <path>          only notes under <path>
"""
import os, re, sys, json, difflib, collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _standard

VAULT = os.environ.get("VAULT_ROOT") or os.getcwd()
DIRS = _standard.scope_dirs(VAULT)

FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
ALIAS_RE = re.compile(r"^aliases:\s*(.*)$", re.M)


def load_aliases(front):
    m = ALIAS_RE.search(front)
    if not m:
        return []
    raw = m.group(1).strip()
    if raw.startswith("["):
        return [a.strip().strip("\"'") for a in raw[1:-1].split(",") if a.strip()]
    out = []
    for line in front[m.end():].split("\n"):
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip().strip("\"'"))
        elif s and not s.startswith(" "):
            break
    if raw:
        out.insert(0, raw.strip("\"'"))
    return [a for a in out if a]


SKIP_DIRS = {".git", ".obsidian", ".claude", ".agents", ".claudian", "node_modules"}


def scan():
    """notes  = wiki notes in DIRS, the things this skill reports on.
    targets  = every file anywhere in the vault, because a link may legitimately point at an
               attachment, a root note or a template. Indexing only DIRS would report every
               image embed as link rot."""
    notes, targets, alias_of = {}, {}, {}
    links = collections.defaultdict(list)
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, VAULT)
            stem = os.path.splitext(f)[0]
            targets.setdefault(stem, rel)
            targets.setdefault(f, rel)          # links may carry the extension
            if not f.endswith(".md"):
                continue
            in_scope = rel.replace("\\", "/").split("/")[0] in DIRS
            text = open(p, encoding="utf-8", errors="replace").read()
            fm = FM_RE.match(text)
            aliases = load_aliases(fm.group(1)) if fm else []
            if in_scope:
                notes[stem] = {"path": rel, "aliases": aliases}
            for a in aliases:
                alias_of.setdefault(a.lower(), stem)   # autocomplete only; never a link target
            for t in LINK_RE.findall(text):
                links[t.strip()].append(rel)
    return notes, targets, links, alias_of


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = args[0].replace("\\", "/").rstrip("/") if args else None
    notes, targets, links, alias_of = scan()

    # every name a wikilink can resolve to, anywhere in the vault
    resolvable = {name.lower(): name for name in targets}

    unresolved = {}
    for target, sources in links.items():
        key = target.lower()
        tail = target.replace("\\", "/").split("/")[-1].lower()
        if key in resolvable or tail in resolvable:
            continue
        near = difflib.get_close_matches(tail, list(resolvable), n=3, cutoff=0.7)
        unresolved[target] = {"linked_from": sorted(set(sources)),
                              "alias_of": alias_of.get(tail),
                              "did_you_mean": [resolvable[n] for n in near]}

    if "--unresolved" in sys.argv:
        for t, info in sorted(unresolved.items()):
            if info["alias_of"]:
                hint = f"   -> alias of {info['alias_of']}: write [[{info['alias_of']}|{t}]]"
            elif info["did_you_mean"]:
                hint = f"   -> maybe {info['did_you_mean']}"
            else:
                hint = ""
            print(f"[[{t}]]{hint}")
            for s in info["linked_from"]:
                print(f"     from {s}")
        print(f"\n{len(unresolved)} unresolved of {len(links)} distinct targets")
        return

    # inbound names: what other notes actually call each note
    inbound = collections.defaultdict(set)
    for target, sources in links.items():
        stem = resolvable.get(target.lower()) or \
               resolvable.get(target.replace("\\", "/").split("/")[-1].lower())
        if stem:
            inbound[stem].add(target)

    out = []
    for stem, meta in sorted(notes.items()):
        if only and not meta["path"].replace("\\", "/").startswith(only):
            continue
        names = sorted(n for n in inbound.get(stem, set()) if n != stem)
        out.append({"note": meta["path"], "title": stem,
                    "aliases": meta["aliases"], "inbound_names": names})
    print(json.dumps({"notes": out, "unresolved": unresolved}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
