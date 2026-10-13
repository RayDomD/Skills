# Extracting notes from one source

You are reading one source from a person's corpus and writing its notes file. The notes are all that synthesis will see of this source, so they carry everything worth keeping and nothing else.

## Speaker check first

Read the whole source and decide who is speaking.

- **The person throughout** (their own video, essay, letter): extract everything.
- **An interview:** captions carry no speaker labels. The host asks and the guest answers at length; take only the person's turns. When you cannot tell whose line it is, leave it unquoted.
- **Someone else throughout** (a video about them, a reupload of another speaker): add `dropped: <reason>` to the source's frontmatter and write no notes file. You are done.

## Notes file

Keep every heading, in this order. Write `none` under a heading the source gives nothing for. Aim for 600 words or fewer.

```markdown
# <id>: <title> (<date>)

Speaker: <the person throughout | the person as guest of <host> | mixed, which parts>

## Frameworks
- **<their name for it>:** what it is, its parts, when they use it. "<quote>" [12:30]

## Rules
- <a decision rule in one line>. "<quote>" [4:10]

## Positions
- **<topic>:** their stance here. "<quote>" [31:05]

## Stories
- **<short name>:** what happened, the figures as told, the lesson they draw.

## Books
- **<title>:** what they say it argues and which frameworks it holds.

## Voice
- How they open, close, and disagree here. Analogies used.
- Candidate phrases, exact words: "<phrase>", "<phrase>"

## Limits
- Where they say their advice stops applying, admit a mistake, or reverse an earlier view.
```

## Rules for the notes

- **Quotes are copied, word for word**, from the source text. Auto captions have quirks and missing punctuation: keep the words exactly, add punctuation only. A script later checks each quote against this source and rejects any changed word.
- Give each quote its nearest `[m:ss]` marker when the source has them.
- A framework is something they name and reuse. A rule is how they decide. A position is where they stand on a topic people ask them about. Put each item under one heading.
- Record figures as they tell them, with the unit and the year when stated.
- Prefer what bears on the question this person owns, and keep anything they clearly treat as central even when it falls outside it.
- `Books` covers only how they describe their books in this source.
