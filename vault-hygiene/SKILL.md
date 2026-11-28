---
name: vault-hygiene
description: The note standard for an Obsidian vault and the three ways to apply it — writing a new note, normalizing an existing one, or screening a note out of the archive into the knowledge folder. Use whenever a note is being created, retyped, summarized, linked, or normalized; whenever the user asks to "clean up", "fix up", "standardize", "backfill" or "screen" a note or a folder; and before any bulk edit inside a vault. Accepts a single note or one folder.
---

# Vault Hygiene

This skill holds **procedure and reasoning**. The vault holds the **values**, in
`.vault-standard.yml` at its root. Read that file first — it is authoritative for scope, the
type vocabulary, folder floor and ceiling, required properties and banned basenames. Where this
document names a rule, it explains *why* the rule exists; where it names a number, that number
is a description of the config, not a second copy of it.

**No `.vault-standard.yml` means this is not a vault. Stop.** Do not infer the rules from what
the files look like — guessing the standard is how a cleanup pass confidently mangles someone
else's directory.

Scope is `scope.enforced`. Everything else is furniture: `scope.report_only` is capture and has
no note standard at all, `scope.archive` is the screening queue, and anything under
`scope.opaque` is a session's implementation that nothing outside inspects.

**Accepts a single note or one folder. There is no whole-vault mode**, deliberately: a pass
whose diff is too large to read gets rubber-stamped, which defeats the point of proposing one.

---

## The reasoning behind the rules

### Type is a trust decision, not a filing decision

The vocabulary is closed and lives in `types` in the config. Every note carries exactly one.
Do not invent one more — if a note genuinely does not fit, **stop and say so** rather than
forcing it.

The distinction that actually costs something is `concept` vs `resource`. A `concept` is the
user's own claim; a `resource` is quotable but not endorsed. Get it wrong and captured material
starts being repeated as established fact. When the note is someone else's material, `resource`
is the honest answer **even if the material is good** — this vault's T7 pass found talk notes
that were credited to named speakers and carried transcription errors, and typing them `concept`
would have asserted that shaky material as the user's own position.

Some types carry extra required properties (`requires` in the config) — `author` on `concept`,
`kind` on `session`. Leave `author:` blank rather than guessing where material came from.

### Summary is the interface, so it exists exactly once

One sentence stating what the note *is*, in frontmatter, so it is queryable and indexes render
themselves. It is how anyone — human or machine — surveys the whole vault without opening it.

**Quote it.** A summary sentence very easily contains `": "`, which makes the frontmatter
invalid YAML. Obsidian then shows the note with **no properties at all** rather than an error,
so it looks correct in the editor while every Base and query silently ignores it. This cost
three notes before it was caught, and would have scaled to the entire vault. Always write
`summary: "..."`.

**Extract it; never invent it.** If the note does not say what it is, the summary is a quote or
a compression of its own opening — not a description written from knowledge of the subject. An
invented summary reads as authoritative and is wrong, which is worse than no summary at all.
If the note is too thin to summarize, say so and propose nothing.

**Never copy it into a MOC or an index.** A duplicated summary drifts from the note it describes,
and the stale copy is then read with confidence. Indexes and MOCs carry prose and wikilinks
only; summaries are rendered from frontmatter — by a Base for the human, by the health check
script for Claude, who never sees a rendered Base.

### Stubs are a queue, not a defect

A note with a title and no content is a **stub**: `status: stub`, a `type:`, and **no
`summary:`**. There is no prose to extract one from, and writing one anyway is exactly the
invention the standard forbids.

This is not an edge case here — "make a note called X" means scaffold only, so stubs are created
deliberately (`Meta/Memory/create-notes-empty-by-default.md`). Both enforcement layers treat
them as a to-write queue, and exempt them from connectivity too: a note with nothing written
has nothing to link from. When a stub gets written, drop `status: stub` and add the summary in
the same pass.

### Links: inline first, and folders are free

**Inline wikilinks are primary.** Link the term where it occurs in the sentence. An inline link
carries its sentence into the target's backlink panel, so the backlink shows *why* two notes
relate. A `## Related` list yields a context-free line and is a **backstop** — for real
connections with no natural mention in the prose.

- `[[Note Name]]` is the only link primitive. Obsidian rewrites wikilinks on rename; Markdown
  links rot silently.
- **Folders do not affect link resolution.** `[[Name]]` resolves by basename vault-wide and
  Obsidian rewrites links on move, so reorganizing folders cannot rot a link. Two things can:
  a **duplicate basename**, which silently resolves to the wrong file, and a `../` relative
  path, which Obsidian has no concept of at all. `naming.banned_basenames` lists the generic
  names that collide the moment a second one appears.
- Never invent a link target. Check it resolves. An unresolved link is either **rot** (renamed,
  moved, mistyped — a defect, fix it) or a **seed** (a deliberate pointer to a note not yet
  written — a queue entry, not a defect). Say which one you are creating.
- `aliases:` does **not** make a link resolve. Obsidian follows a typed `[[Name]]` only to a file
  whose basename is `Name`; an alias feeds autocomplete and search, which write `[[Note|alias]]`.
  Fix rot by pointing the link at the real title and keeping the natural spelling as display
  text: `[[Note Title|spelling]]`. A bare `[[alias]]` is unresolved, and clicking it in Obsidian
  creates an empty note at the vault root.

### Connectivity is tiered so no note is forced into a fake link

Only types flagged `associate` in the config must link outward. Leaves are exempt by design —
a one-off clipping with no links is not a defect. Types carrying `debt` owe something on
completion instead: a `session` marked `done` must show at least one link into the knowledge
folder, and `abandoned` is an honest state that owes nothing.

Reachability is separate from association, and they fail differently. Reachable means findable
by walking index → MOC → note. Associated means linked laterally to related ideas. A note can
be perfectly reachable and still be a dead end.

### A folder must be deep enough to justify its MOC

`folder.floor` and `folder.ceiling` exist because a folder is a module and its MOC is the
interface. Below the floor the MOC hides nothing its parent index could not hold — run the
deletion test: remove it and no complexity reappears. Above the ceiling the MOC stops being
readable in one sitting and the folder should split.

A topic below the floor is not a folder. Its notes sit directly in the knowledge folder and are
reached through the root index until the topic graduates.

### MOC shape

A curated `## Start here` — the 3–5 notes that matter, ordered, with a line of commentary each —
above an embedded Base listing the folder's full contents. Editorial signal on top, coverage
guarantee underneath, so completeness is never maintained by hand. **Commentary, not summaries.**

### Editing a `.base`

**Always run the validator before saving. Valid YAML is not enough.**

```
python <skill>/scripts/validate_base.py
```

`filters` must be a single string, or a mapping with exactly one `and` / `or` / `not` key.
`filters: ['x']` is valid YAML and invalid Bases — and **one bad view fails the entire file**,
so every embed of every view breaks, not just the one you touched. Every `formula.X` referenced
in `order`, `filters`, `groupBy` or `properties` must exist in the `formulas` block.

Guard optional properties with `if()`, and use `.days` before number maths on a Duration.
The `obsidian-bases` skill holds the full syntax reference.

---

## Mode A — writing a new note

1. Confirm the folder from the type, not the other way round.
2. Create it from the matching `Templates/` file. Fill in the title.
3. **Stop there.** "Make a note called X" means the scaffold only. The note is the user's
   thinking space; pre-filling it with a summary of the topic replaces the learning the note
   exists to capture. If you have useful content, offer it in chat.
4. Link it from its MOC, or from the root index if its topic is below the floor, so it is
   reachable from birth.

`summary:` and body content get filled in by whoever writes the note.

**Course notes** (a lecture video or reading under `Sessions/*/_work/`) use
`Templates/Course Note.md`, not the generic `Resource.md`. When the user hands over a
transcript or screenshot and asks for notes, that is the explicit request to write content:
follow the rules in the template's comment, and match the sibling notes in the same module
folder.

## Mode B — normalizing an existing note

**A note imported from outside the vault is Mode B, not Mode C.** Mode C screens out of an
in-vault queue (`scope.archive`), and a vault may have none — in which case the outside folder
the relic came from *is* the archive, and copying one in is the import. Put it straight into
the knowledge folder or a session, **not into `scope.report_only`**: capture is a live stream
whose count answers "am I keeping up?", and back-filling it with relics kills that signal.
Placing the file is the human's triage decision and it comes first, exactly as in Mode C.

Two phases, kept apart on purpose: a bad mechanical guess is obvious in a diff, a bad judgment
call is not, and mixing them hides the second in the noise of the first.

**Phase 1 — mechanical.** Deterministic, no judgment.

```
python <skill>/scripts/normalize_note.py            # dry run
python <skill>/scripts/normalize_note.py --report   # + heading decisions
python <skill>/scripts/normalize_note.py --apply
```

Lone `**Bold line**` → real heading, OneNote backslash escapes stripped, import padding
collapsed, frontmatter keys ordered. It never touches code fences or inline code, and it
verifies itself: body alphanumeric token sequence identical, frontmatter a permutation.
It is idempotent.

Word count is **not** a valid check here — `**Bold**` → `## Bold` changes it while changing
nothing. The script's own check is the one to trust.

**Phase 2 — judgment.** Propose a diff; change nothing without approval.

1. Infer `type:` from folder and content shape. If it does not fit, halt.
2. Write `summary:` **extracted from the note's own text**.
3. Propose `aliases:` from title variants and from how other notes already refer to it, so
   autocomplete finds the note under those spellings — `scripts/build_link_index.py` gives the
   vault-wide title and alias index. Links written by hand still target the title:
   `[[Note Title|variant]]`.
4. Scan the body for terms that are notes and link them inline where they occur.
5. Add the note to its MOC, or to the root index if its topic is below the floor.

Then re-run `vault-health-check`. **Violation counts must not increase.**

## Mode C — screening a note out of the archive

The operation this vault runs most. `scope.archive` holds pre-rebuild material: readable,
searchable, and **not** held to the standard. A note leaves it only when someone decides it is
worth keeping, and it arrives at standard in the same motion.

**The decision is the user's, and it comes first.** Do not screen a note because it is next in
the folder. Ask: would you re-read this? If the answer needs thought, the answer is no — the
archive is not a backlog to be drained, and a note left there is not lost.

1. **Move, never copy** (`migration.move_not_copy`). Two reasons: Obsidian rewrites the links on
   a move and cannot on a copy, and a copy leaves the archived original colliding by basename
   with its rewritten twin. Use `git mv` so the history shows a rename.
2. Run Mode B phase 1 on it — archived material predates the standard and usually carries
   import artifacts.
3. Run Mode B phase 2. The type decision is the real work; apply the trust test above.
4. Place it: into a topic folder if that topic is at or above `folder.floor`, otherwise directly
   in the knowledge folder, listed in the root index.
5. Re-link it. Its old links may point at notes still in the archive — those are now **seeds**,
   not rot, and should be left as the queue they are. Say which ones you left.
6. Re-run `vault-health-check`. The archive count should fall by one and defects should not rise.

**Screening does not mean everything eventually moves.** The archive is done when what remains
is material nobody wants, and deleting it then is the correct ending.

## Mode D — distilling a session into the knowledge folder

How learning becomes knowledge. A session generates a great deal of material, almost all of
which is scaffolding for the learning rather than the learning itself. This mode decides what
survives and pays the session's debt.

**Nothing inside `scope.opaque` is knowledge yet.** It is a session's implementation, and the
health check never inspects it — that opacity is what lets a generator write freely without
producing defects. Distilling is the only path out of it, and it is a **rewrite, not a move**:
generated material is often HTML, and always written for teaching rather than for reference.

**What crosses, and what never does.** For a `/teach` workspace the mapping is direct, because
its own artifact definitions line up with the type vocabulary:

| Generated artifact | Becomes | Why |
|---|---|---|
| `learning-records/*.md` | `concept` | "non-obvious lessons and key insights" — these are the user's own claims |
| `reference/*.html` | `reference` | "cheat sheets, algorithms, syntax, glossaries" — operative, consulted |
| `lessons/`, `assets/`, `NOTES.md`, `MISSION.md` | nothing | teaching scaffolding; it stays in `_work/` |

1. **Read the learning records first.** They are the queue — the session already wrote them as
   it went, so no separate list is maintained. Present them and let the user choose. A record
   the user no longer endorses does not cross; being written down is not the same as being true.
2. For each survivor, write a note the normal way — Mode A for the scaffold, then Mode B phase 2
   for `type`, `summary`, aliases and inline links. **The summary is extracted from the record,
   not from your knowledge of the subject.**
3. `concept` notes need `author`. A learning record is the user's own insight, so the user is
   the author — but a reference sheet built from cited external sources is not, and the
   citation belongs in the note.
4. Link the session's entry note to what crossed. That is the debt, and it is what lets the
   session be marked `done`.
5. If nothing survived, mark the session `abandoned`. That is an honest outcome and is exempt.
   **Do not manufacture a link to clear the check** — a fake ATLAS note is worse than an
   abandoned session, because the check will then read as passing forever.
6. Re-run `vault-health-check`. Session debt should clear and defects must not rise.

**Distillation is driven by need, not by quota.** A course that produced one durable idea
produced one note. Extracting the other forty for completeness is how a curated wiki turns
back into a dump.

### Hard rules

- **Do not split a note.** Broken markup is not broken content.
- **Do not rewrite prose.** Normalizing is markup and metadata, not editing.
- **Reflow pasted source text.** One paragraph per line. Join lines hard-wrapped mid-sentence by
  PDFs, course readings, or web copies — Obsidian renders every newline as a break. Keep a break
  only for a real paragraph, list item, or deliberate line. Reflowing changes no words, so it is
  not rewriting prose.
- **Propose, then wait.** One folder per pass, one commit per pass, diff reviewed each time.
- **Never invent a summary, an alias, a link target, or a type outside the vocabulary.** Halting
  is a valid outcome and a cheaper one than a confident wrong answer.
