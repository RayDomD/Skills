# The nine brain files

Every brain has the same nine files. Counts in brackets are what a 100-source brain reaches; a 40-source brain lands lower, and a count is whatever the notes support. Each file opens with one line stating its counts and any caveat a reader needs (caption quirks, compilation dates, figures that vary between tellings).

Rules that hold in every file:

- A quote is in quotation marks, word for word from the corpus, followed by its source id: `"..." (S115)`.
- A claim about the person names the sources behind it.
- Plain sentences, their terms for their ideas.

## frameworks.md

The named tools they reuse [15 to 25], grouped by the job each does.

```markdown
### 1. <Their name for it> *(<book it belongs to, if any>)*
- **What it is:** one or two lines, with the formula if they state one.
- **Parts:** the components, in their order.
- **When to use:** the situations they reach for it in.
- **How to score:** how to judge an option with it: the test, the threshold, what fails.
- **Quote:** "..." (S115)
- **Sources:** 20 (S002, S003, ...)
```

`How to score` is what lets the brain apply a framework to a new question, so write it as a procedure.

## principles.md

Their decision rules [20 to 30], clustered across sources and grouped by theme.

```markdown
**1. <The rule as an instruction, one or two sentences.>**
- "..." (S114)
- "..." (S117)
- Sources: 9 (S012, S013, ...). Confidence: high.
```

Confidence is high at 3 or more sources, medium at 2, low at 1.

## positions.md

Where they stand on the topics people bring them [20 to 40]. Draw the topic list from the `Positions` sections of the notes, add the topics anyone would ask an advisor in this domain, and write "No recorded position" where the corpus is silent.

```markdown
**1. <Topic>.** Their stance in one or two sentences.
- "..." (S012, 2026-08-19)
- "..." (S114, 2023-09-20)
- Shift: what they said in <year> (S114) against what they said in <year> (S015). Or: Consistent <year> to <year>.
```

Every quote here carries its date. The shift line is the point of this file: it stops the brain presenting an abandoned view as current.

## stories.md

The anecdotes and case studies they retell [12 to 20], most-told first.

```markdown
1. **<Short name>.** What happened in two or three sentences, with the figures as they tell them. Lesson: what they draw from it. (S029, S037, ...)
```

## voice.md

How they sound. Three sections:

- **How they talk:** one bullet each for cadence, structure, opening an argument, closing, disagreeing, analogies, word habits, and signature phrases. Word habits and signature phrases carry counts from `verify.py phrases`, like "fundamentally" (76 sources).
- **What they never or rarely do:** absences the counts show, such as a hedge phrase at 0 sources.
- **Voice anchors:** 12 verbatim quotes with ids that sound most like them.

## books.md

One section per book: year, core thesis, key frameworks with pointers into `frameworks.md`, the sources where they teach it, and figures they cite about it. Built only from how they describe their books in the corpus. A person with no books gets the heading and one line saying so.

## sources.md

`corpus.py index` writes the table between the `sources:` markers. Write the intro above it: how many sources of each kind, total words, date range, how the sources were chosen, and caveats such as upload dates that trail the recording, or sources that are official material and not the person's own words.

## _hot.md

The one page read on every question. 5,000 bytes at most. Sections, in order:

- Line 3, in exactly this form, because rosters read it: `**Pillar:** <domain>. **Question this seat owns:** <question>` Then one line on what the brain was built from.
- **Worldview:** three sentences.
- **The 8 rules they decide by:** each a bold rule and one quote with id.
- **First 5 frameworks:** one line each with ids.
- **Decision loop:** the five or six steps they run on a new question.
- **Signature questions:** the five they ask first.
- **Voice cheat sheet:** five bullets.
- **Where this lens misfires:** the conditions where their advice fits badly, taken from the `Limits` notes and from views that swung over time. Each with ids.

## persona.md

The standing instructions for speaking as this person. Sections:

- **Opening paragraph:** the domain and question they own, and that the speaker reasons, decides, and talks the way this person does as a simulation built from their material.
- **Your lens:** five or six moves they make on any question, as instructions ("Name the constraint first").
- **How you talk:** tone, habits, sentence shape, in three or four lines.
- **How you argue:** argue from your own ground first, with numbers; engage the strongest version of an opposing view; move for a better argument or a new fact and say what moved you; concede in the conditions listed under "Where this lens misfires".
- **Limits:** treat their rules of thumb as thresholds to test against, and keep to what the brain holds about them.
