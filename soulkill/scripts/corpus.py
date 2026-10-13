#!/usr/bin/env python
"""
Capture a person's material into a brain corpus and index it.

Usage:
  corpus.py yt-list <channel-or-playlist-url> [--limit N] [--min-minutes M]
  corpus.py yt-fetch <slug> [<url> ...] [--file urls.txt]
  corpus.py web-links <index-url> [--match REGEX]
  corpus.py web-fetch <slug> [<url> ...] [--file urls.txt]
  corpus.py add-local <slug> <path> [<path> ...]
  corpus.py index <slug>
  corpus.py status <slug>

Raw material lands in ~/.claude/brain-corpus/<slug>/{transcripts,writing,local}/ as
markdown with frontmatter. `index` gives every source a stable id (S001...) and
writes the table in ~/.claude/brains/<slug>/sources.md. `status` lists sources
that still have no extraction notes.
"""
import argparse
import html
import json
import re
import shutil
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

HOME = Path.home() / ".claude"
CORPUS = HOME / "brain-corpus"
BRAINS = HOME / "brains"

SOURCE_DIRS = {"transcripts": "video", "writing": "writing", "local": "local"}
FM_KEYS = ["id", "title", "url", "date", "type", "channel", "captions", "words", "dropped"]
TABLE_START = "<!-- sources:start -->"
TABLE_END = "<!-- sources:end -->"

SLUG_MAX = 60
PARAGRAPH_SECONDS = 60  # one timestamp marker per minute of captions
FETCH_PAUSE_SECONDS = 2  # YouTube throttles rapid caption requests
FETCH_RETRIES = 3
THIN_PAGE_WORDS = 100  # below this a web page probably failed to extract
MAIN_CONTENT_MIN_WORDS = 150  # trust <article>/<main> only when it holds real text
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) brain-corpus/1.0"
TEXT_SUFFIXES = {".md", ".txt"}
CAPTION_SUFFIXES = {".vtt", ".srt"}


# ---------- files ----------

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:SLUG_MAX].strip("-") or "untitled"


def read_source(path):
    """Return (frontmatter dict, body)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n"):
        return {}, text
    head, _, body = text[4:].partition("\n---\n")
    fm = {}
    for line in head.splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fm[key.strip()] = value.strip()
    return fm, body.lstrip("\n")


def write_source(path, fm, body):
    keys = [k for k in FM_KEYS if fm.get(k)] + [k for k in fm if k not in FM_KEYS and fm[k]]
    head = "\n".join(f"{k}: {str(fm[k]).replace(chr(10), ' ')}" for k in keys)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{head}\n---\n\n{body.strip()}\n", encoding="utf-8")


def source_files(slug):
    root = CORPUS / slug
    return [p for d in SOURCE_DIRS for p in sorted((root / d).glob("*.md"))]


def known_urls(slug):
    return {read_source(p)[0].get("url") for p in source_files(slug)}


def free_path(folder, name, tiebreak):
    path = folder / f"{name}.md"
    return path if not path.exists() else folder / f"{name}-{slugify(tiebreak)}.md"


def collect_urls(args):
    urls = list(args.urls)
    if args.file:
        lines = Path(args.file).read_text(encoding="utf-8").splitlines()
        urls += [ln.split()[0] for ln in lines if ln.strip() and not ln.startswith("#")]
    if not urls:
        sys.exit("no urls given")
    return urls


# ---------- network (all outbound calls live here) ----------

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        charset = resp.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


def ydl(**opts):
    try:
        import yt_dlp
    except ImportError:
        sys.exit("yt-dlp is missing. Install it with: python -m pip install yt-dlp")
    return yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True, **opts})


def youtube_listing(url):
    if re.search(r"youtube\.com/(@|channel/|c/|user/)[^/]+/?$", url):
        url = url.rstrip("/") + "/videos"
    with ydl(extract_flat=True) as y:
        return y.extract_info(url, download=False).get("entries") or []


def youtube_captions(url):
    """Return (info, caption format, 'manual'|'auto', raw caption text) or raise."""
    with ydl() as y:
        info = y.extract_info(url, download=False)
        for kind, tracks in (("manual", info.get("subtitles") or {}), ("auto", info.get("automatic_captions") or {})):
            langs = [k for k in tracks if k == "en-orig"] + [k for k in tracks if k == "en"] + \
                    sorted(k for k in tracks if k.startswith("en-") and k != "en-orig")
            for lang in langs:
                for ext in ("json3", "vtt"):
                    for fmt in tracks[lang]:
                        if fmt.get("ext") == ext and fmt.get("url"):
                            raw = y.urlopen(fmt["url"]).read().decode("utf-8", errors="replace")
                            return info, ext, kind, raw
    raise RuntimeError("no English captions")


# ---------- caption and html parsing ----------

def stamp(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"[{h}:{m:02d}:{s:02d}]" if h else f"[{m}:{s:02d}]"


def paragraphs(cues):
    """cues: [(start seconds, text)] -> text with one [m:ss] marker per PARAGRAPH_SECONDS."""
    out, current, mark = [], [], None
    for start, text in cues:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue
        if mark is None or start - mark >= PARAGRAPH_SECONDS:
            if current:
                out.append(" ".join(current))
            current, mark = [stamp(start)], start
        current.append(text)
    if current:
        out.append(" ".join(current))
    return "\n\n".join(out)


def cues_from_json3(raw):
    cues = []
    for event in json.loads(raw).get("events", []):
        text = "".join(seg.get("utf8", "") for seg in event.get("segs") or [])
        cues.append((event.get("tStartMs", 0) / 1000, text))
    return cues


def cues_from_vtt(raw):
    """Handles .vtt and .srt. Drops the rolling duplicate lines auto captions produce."""
    cues, start, last = [], 0.0, None
    for line in raw.splitlines():
        m = re.match(r"\s*(?:(\d+):)?(\d{1,2}):(\d{2})[.,]\d+\s+-->", line)
        if m:
            start = int(m.group(1) or 0) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            continue
        line = html.unescape(re.sub(r"<[^>]+>", "", line)).strip()
        if not line or line.isdigit() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        if line != last:
            cues.append((start, line))
            last = line
    return cues


class PageText(HTMLParser):
    SKIP = {"script", "style", "noscript", "nav", "header", "footer", "aside", "form", "svg", "button"}
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.scope = {"article": 0, "main": 0}
        self.text = {"article": [], "main": [], "all": []}
        self.title, self.meta_title, self.date, self.in_title = "", "", "", False
        self.links, self.href, self.link_text = [], None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self.skip += 1
        if tag in self.scope:
            self.scope[tag] += 1
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            name, content = a.get("property") or a.get("name") or "", a.get("content") or ""
            if name == "og:title":
                self.meta_title = content
            if name in ("article:published_time", "date", "pubdate") and not self.date:
                self.date = content[:10]
        if tag == "time" and a.get("datetime") and not self.date:
            self.date = a["datetime"][:10]
        if tag == "a" and a.get("href"):
            self.href, self.link_text = a["href"], []
        if tag in self.BLOCK:
            self.handle_data("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.scope and self.scope[tag]:
            self.scope[tag] -= 1
        if tag == "title":
            self.in_title = False
        if tag == "a" and self.href:
            self.links.append((self.href, " ".join("".join(self.link_text).split())))
            self.href = None
        if tag in self.BLOCK:
            self.handle_data("\n")

    def handle_data(self, data):
        if self.in_title:
            self.title += data
            return
        if self.href is not None:
            self.link_text.append(data)
        if self.skip:
            return
        self.text["all"].append(data)
        for scope, depth in self.scope.items():
            if depth:
                self.text[scope].append(data)

    def body(self):
        for scope in ("article", "main", "all"):
            lines = [" ".join(ln.split()) for ln in "".join(self.text[scope]).splitlines()]
            text = "\n\n".join(ln for ln in lines if ln)
            if scope == "all" or len(text.split()) >= MAIN_CONTENT_MIN_WORDS:
                return text


def parse_page(url):
    page = PageText()
    page.feed(http_get(url))
    return page


# ---------- commands ----------

def cmd_yt_list(args):
    rows = []
    for e in youtube_listing(args.url):
        minutes = (e.get("duration") or 0) / 60
        if minutes >= args.min_minutes:
            rows.append((e.get("view_count") or 0, minutes, e.get("id"), e.get("title") or ""))
    rows.sort(reverse=True)
    print("views\tminutes\turl\ttitle")
    for views, minutes, vid, title in rows[: args.limit]:
        print(f"{views}\t{minutes:.0f}\thttps://www.youtube.com/watch?v={vid}\t{title}")
    print(f"# {min(len(rows), args.limit)} of {len(rows)} videos shown", file=sys.stderr)


def cmd_yt_fetch(args):
    folder, done, failed = CORPUS / args.slug / "transcripts", known_urls(args.slug), []
    for url in collect_urls(args):
        result = None
        for attempt in range(1, FETCH_RETRIES + 1):
            try:
                result = youtube_captions(url)
                break
            except Exception as err:  # yt-dlp raises many types; report and move on
                error = str(err).splitlines()[0]
                if "no English captions" in error:
                    break
                time.sleep(FETCH_PAUSE_SECONDS * attempt * 3)
        if not result:
            failed.append((url, error))
            print(f"FAILED  {url}  {error}")
            continue
        info, ext, kind, raw = result
        canonical = f"https://www.youtube.com/watch?v={info['id']}"
        if canonical in done:
            print(f"have    {canonical}")
            continue
        body = paragraphs(cues_from_json3(raw) if ext == "json3" else cues_from_vtt(raw))
        day = info.get("upload_date") or ""
        fm = {
            "title": info.get("title") or info["id"],
            "url": canonical,
            "date": f"{day[:4]}-{day[4:6]}-{day[6:]}" if len(day) == 8 else "",
            "type": "video",
            "channel": info.get("channel") or info.get("uploader") or "",
            "captions": kind,
            "words": len(re.sub(r"\[\d+:\d\d(:\d\d)?\]", "", body).split()),
        }
        path = free_path(folder, slugify(fm["title"]), info["id"])
        write_source(path, fm, body)
        done.add(canonical)
        print(f"saved   {fm['words']:>6} words  {path.name}")
        time.sleep(FETCH_PAUSE_SECONDS)
    sys.exit(1 if failed else 0)


def cmd_web_links(args):
    page, seen = parse_page(args.url), set()
    host = urlparse(args.url).netloc
    for href, text in page.links:
        link = urldefrag(urljoin(args.url, href))[0]
        if urlparse(link).netloc != host or link in seen or link == args.url:
            continue
        if args.match and not re.search(args.match, link):
            continue
        seen.add(link)
        print(f"{link}\t{text}")
    print(f"# {len(seen)} links", file=sys.stderr)


def cmd_web_fetch(args):
    folder, done, failed = CORPUS / args.slug / "writing", known_urls(args.slug), []
    for url in collect_urls(args):
        if url in done:
            print(f"have    {url}")
            continue
        try:
            page = parse_page(url)
        except Exception as err:
            failed.append(url)
            print(f"FAILED  {url}  {err}")
            continue
        body = page.body()
        title = " ".join((page.meta_title or page.title).split()) or url
        fm = {"title": title, "url": url, "date": page.date, "type": "writing", "words": len(body.split())}
        path = free_path(folder, slugify(title), urlparse(url).path)
        write_source(path, fm, body)
        done.add(url)
        thin = "  THIN: check this page by eye" if fm["words"] < THIN_PAGE_WORDS else ""
        print(f"saved   {fm['words']:>6} words  {path.name}{thin}")
        time.sleep(FETCH_PAUSE_SECONDS)
    sys.exit(1 if failed else 0)


def cmd_add_local(args):
    folder, skipped = CORPUS / args.slug / "local", []
    files = [f for p in map(Path, args.paths) for f in ([p] if p.is_file() else sorted(p.rglob("*"))) if f.is_file()]
    for f in files:
        suffix = f.suffix.lower()
        if suffix in TEXT_SUFFIXES:
            fm, body = read_source(f)
        elif suffix in CAPTION_SUFFIXES:
            fm, body = {}, paragraphs(cues_from_vtt(f.read_text(encoding="utf-8", errors="replace")))
        else:
            skipped.append(f)
            continue
        fm = {
            "title": fm.get("title") or f.stem,
            "url": fm.get("url", ""),
            "date": fm.get("date", ""),
            "type": "local",
            "words": len(body.split()),
            "origin": str(f),
        }
        path = folder / f"{slugify(f.stem)}.md"
        write_source(path, fm, body)
        print(f"saved   {fm['words']:>6} words  {path.name}")
    for f in skipped:
        print(f"SKIPPED {f}  (convert to .md or .txt first)")


def cmd_index(args):
    entries = [(p, *read_source(p)) for p in source_files(args.slug)]
    if not entries:
        sys.exit(f"no sources in {CORPUS / args.slug}")
    used = [int(fm["id"][1:]) for _, fm, _ in entries if re.fullmatch(r"S\d{3,}", fm.get("id", ""))]
    next_id = max(used, default=0) + 1
    for path, fm, body in entries:
        if not fm.get("id"):
            fm["id"] = f"S{next_id:03d}"
            next_id += 1
            write_source(path, fm, body)
    entries.sort(key=lambda e: e[1]["id"])
    kept = [e for e in entries if not e[1].get("dropped")]
    root = CORPUS / args.slug
    cell = lambda v: str(v or "").replace("|", "/")
    rows = ["| ID | Title | URL | Date | Type | Words | File |", "|---|---|---|---|---|---|---|"]
    for path, fm, _ in kept:
        words = f"{int(fm.get('words') or 0):,}"
        rows.append("| " + " | ".join([fm["id"], cell(fm.get("title")), cell(fm.get("url")), cell(fm.get("date")),
                                       cell(fm.get("type")), words, path.relative_to(root).as_posix()]) + " |")
    dropped = [f"- {fm['id']} {cell(fm.get('title'))}: {fm['dropped']}" for _, fm, _ in entries if fm.get("dropped")]
    if dropped:
        rows += ["", "Dropped at extraction (not cited anywhere in this brain):", *dropped]
    table = "\n".join([TABLE_START, *rows, TABLE_END])

    out = BRAINS / args.slug / "sources.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    old = out.read_text(encoding="utf-8") if out.exists() else f"# Sources: {args.slug}\n\n{TABLE_START}\n{TABLE_END}\n"
    if TABLE_START in old and TABLE_END in old:
        new = old[: old.index(TABLE_START)] + table + old[old.index(TABLE_END) + len(TABLE_END):]
    else:
        new = old.rstrip() + "\n\n" + table + "\n"
    out.write_text(new, encoding="utf-8")

    total = sum(int(fm.get("words") or 0) for _, fm, _ in kept)
    by_type = {}
    for _, fm, _ in kept:
        by_type[fm.get("type", "?")] = by_type.get(fm.get("type", "?"), 0) + 1
    undated = sum(1 for _, fm, _ in kept if not fm.get("date"))
    mix = ", ".join(f"{n} {t}" for t, n in sorted(by_type.items()))
    print(f"{len(kept)} sources ({mix}), {total:,} words, {len(dropped)} dropped, {undated} undated -> {out}")


def cmd_status(args):
    notes = CORPUS / args.slug / "notes"
    missing, unindexed, kept = [], 0, 0
    for path in source_files(args.slug):
        fm, _ = read_source(path)
        if fm.get("dropped"):
            continue
        kept += 1
        if not fm.get("id"):
            unindexed += 1
        elif not (notes / f"{fm['id']}.md").exists():
            missing.append(f"{fm['id']}  {fm.get('words', '?'):>7} words  {path.relative_to(CORPUS / args.slug).as_posix()}")
    print(f"{kept} sources, {kept - unindexed - len(missing)} with notes, {len(missing)} without, {unindexed} not indexed")
    print("\n".join(missing))
    sys.exit(1 if missing or unindexed else 0)


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("yt-list")
    p.add_argument("url")
    p.add_argument("--limit", type=int, default=200)
    p.add_argument("--min-minutes", type=float, default=0)
    p.set_defaults(fn=cmd_yt_list)

    for name, fn in (("yt-fetch", cmd_yt_fetch), ("web-fetch", cmd_web_fetch)):
        p = sub.add_parser(name)
        p.add_argument("slug")
        p.add_argument("urls", nargs="*")
        p.add_argument("--file")
        p.set_defaults(fn=fn)

    p = sub.add_parser("web-links")
    p.add_argument("url")
    p.add_argument("--match")
    p.set_defaults(fn=cmd_web_links)

    p = sub.add_parser("add-local")
    p.add_argument("slug")
    p.add_argument("paths", nargs="+")
    p.set_defaults(fn=cmd_add_local)

    for name, fn in (("index", cmd_index), ("status", cmd_status)):
        p = sub.add_parser(name)
        p.add_argument("slug")
        p.set_defaults(fn=fn)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
