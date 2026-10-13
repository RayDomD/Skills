# Capture a person into a brain

Six steps. Each ends on a check; finish the check before starting the next step. `<slug>` paths below are under `~/.claude/brain-corpus/<slug>/` unless they name the brain folder.

## 1. Scope

Settle these with the user in one exchange:

- **Person and slug.** If `~/.claude/brains/<slug>/` already exists, this run extends it: capture only new sources, extract only those, then redo steps 5 and 6.
- **The question they own.** One domain and one question this advisor answers better than anyone, like "Will people pay, how much, and how do we close?" It steers source picks and the persona.
- **Size.** 40 sources by default. `--full` means 100 or more.
- **Material.** Public scraping, local files the user supplies, or both.

Done when the user has confirmed all four.

## 2. Discover

Skip to step 3 when the material is local files only.

Research where this person's own words live, then write `candidates.md` with one row per source: url, kind (video or writing), date if known, and why it earns a place.

- **Their channel:** `corpus.py yt-list <channel-url> --min-minutes 15` lists long-form videos, most viewed first.
- **Their writing:** `corpus.py web-links <index-url> --match <regex>` lists the essays, posts, or letters under an index page.
- **Interviews:** search for long conversations where they are the main guest.

Pick a mix: about half top and recent long-form from their own channel, about a third chosen because they bear on the question they own, the rest long guest interviews, plus their writing where it exists. Spread the dates across their career so shifts in view show up.

Every candidate is a **primary** source: this person speaking or writing. Articles about them, clips cut by others, and shorts stay out, because every quote in the brain must be their own words.

Done when `candidates.md` reaches the target size and the user has approved the list. Show them the counts by kind and the date range, and wait.

## 3. Capture

Put the approved video urls in one file and the writing urls in another, one per line, then:

```
corpus.py yt-fetch <slug> --file <video-urls>
corpus.py web-fetch <slug> --file <writing-urls>
corpus.py add-local <slug> <file-or-folder> ...
corpus.py index <slug>
```

- Fetching resumes: rerun the same command after a failure and it skips what it already has.
- A video with no English captions cannot be captured. Drop it and name it to the user.
- A page flagged `THIN` did not extract. Fetch it another way and save it by hand in `writing/` with the same frontmatter as its neighbours.
- `add-local` takes `.md`, `.txt`, `.vtt`, and `.srt`. Convert PDFs and Word files to `.md` first. Audio or video files without a transcript are outside this skill; tell the user they need transcribing first.
- Fill in any blank `date:` you can establish. Dates drive the change-over-time record in `positions.md`.

Done when `index` reports a source count equal to the approved list minus the failures you reported, and every public source has a date.

## 4. Extract

Write one notes file per source at `notes/<id>.md`, following [`extract.md`](extract.md).

Each source gets a fresh context, because one long transcript fills most of a window and the corpus is many times larger than any window. Dispatch one worker per source, several in parallel, on the tier the "Agent assignment" table in `SKILL.md` gives for extraction. Give each the person's name, the question they own, the source path, the notes path, and the path to `extract.md`. Where no workers are available, work through the sources yourself one at a time, writing each notes file before opening the next source.

Done when `corpus.py status <slug>` exits 0, then run `corpus.py index <slug>` again so dropped sources leave the table.

## 5. Synthesize

Write the nine brain files into `~/.claude/brains/<slug>/` following [`brain-files.md`](brain-files.md), on the tier the "Agent assignment" table gives for synthesis. Work from the notes, one brain file at a time, reading the matching section across every notes file (the `## Frameworks` sections for `frameworks.md`, and so on). Go back to a corpus file only to copy a quote exactly or settle a conflict between notes.

Order: `frameworks.md`, `principles.md`, `positions.md`, `stories.md`, `books.md`, `voice.md`, the intro of `sources.md`, then `_hot.md` and `persona.md` last, because those two compress the rest.

For `voice.md`, take the candidate phrases from the notes and count them with `verify.py phrases <slug> "<phrase>" ...`. Report only counts the script printed.

Done when all nine files exist and every framework, principle, and position lists its source ids.

## 6. Verify

Run `verify.py check <slug>` and fix every problem it prints until it exits 0.

- `NOT IN SOURCE`: open the cited corpus file, find what they actually said, and correct the quote to match it word for word. Delete the quote when the words are not there.
- `WRONG ID`: change the id to the source the script names.
- `HOT TOO LONG`: cut `_hot.md`; the detail lives in the other files.

Then ask the brain one question inside its domain, following [`speak.md`](speak.md), and show the user the answer with the build numbers: sources, words, quotes verified, sources dropped.
