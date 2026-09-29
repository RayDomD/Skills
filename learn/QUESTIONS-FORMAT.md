# QUESTIONS.md Format

`QUESTIONS.md` lives at the workspace root. It is the running log of questions the user asked during lessons, written down as they were asked. At the end of a module it becomes `reference/Module N Questions.md`, where each entry is expanded properly.

It is a capture file, not a polished document. Appending to it should cost seconds.

## Structure

```md
# {Topic} Questions

Questions asked during lessons, captured as they came up. Expanded at the end of
each module into `reference/Module N Questions.md`.

## Module 1 - Evolution

### Why does `fig, ax = plt.subplots()` return two things?
_Lesson 0001, 2026-09-18 - open_

Short answer given: the Figure is the whole canvas and the Axes is the one plot
area on it; you usually style the Axes and save the Figure.

### Is `df.shape` a function?
_Lesson 0001, 2026-09-18 - answered in Module 1 Questions_

Short answer given: no, it is a property, so no parentheses.
```

## Rules

- **Capture before answering.** Write the entry the moment the question is asked, then answer. An answer given first and logged afterwards is logged in your words, not theirs, and half the time is not logged at all.
- **Verbatim, as a heading.** Keep the user's own phrasing, including the informal bits. How they asked it is evidence about where the confusion sits; a tidied-up version loses that.
- **Record the short answer you gave.** One or two sentences. This is what the expansion later builds on, and it stops the module document contradicting what the user was told in the moment.
- **Tag with lesson and date.** The lesson number is how entries are grouped into modules later.
- **Track status.** `open` until the module questions document expands it. Anything still `open` when a module closes must be expanded or explicitly dropped.
- **Group under the module heading**, so the end-of-module sweep is a filter rather than a judgement call.
- **Log questions asked outside a lesson too**, tagged with the nearest lesson. Curiosity between sessions is the strongest signal of engagement the workspace ever gets.
- **Do not answer at length here.** This file stays terse. The long-form treatment belongs in the module document, where the user has the context for it.
- **Never reconstruct from the transcript.** A question recovered days later has drifted in wording and lost the ones that felt too small to mention, which are often the revealing ones.

## What belongs elsewhere

- A question that exposed a misconception also warrants a [learning record](./LEARNING-RECORD-FORMAT.md). Log it here and write the record; they serve different purposes.
- A question about what a term means is usually a [glossary](./GLOSSARY-FORMAT.md) entry, often with an ambiguity flag.
- A question requiring real-world judgement should still be logged, but the answer points at a community from `RESOURCES.md`.
