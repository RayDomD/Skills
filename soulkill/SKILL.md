---
name: soulkill
description: Capture a person into a sourced advisor brain from their videos, writing, or supplied files, then consult it. Use when the user says "soulkill", wants to capture or clone how someone thinks, or wants one captured advisor's take on a question.
argument-hint: "capture <person> [--full] | ask <slug> <question>"
---

A **brain** is nine markdown files in `~/.claude/brains/<slug>/`, distilled from one person's own words, with every quote tied to a source id. The raw **corpus** it was built from sits in `~/.claude/brain-corpus/<slug>/`. A brain is a simulation of the person, built from what they said and wrote.

## Branches

| The user wants | Do |
|---|---|
| `capture <person>`: build or extend a brain | Follow [`capture.md`](capture.md) |
| `ask <slug> <question>`: one advisor's answer | Follow [`speak.md`](speak.md) yourself and answer in chat |
| Two or more advisors against each other | That is the `mikoshi` skill |
| No branch named | List the folders in `~/.claude/brains/` and ask which branch and which brain |

A `<slug>` is the person's full name in kebab-case (`alex-hormozi`). Match a loose name ("Hormozi") to the one brain folder it fits.

## Agent assignment

Each job goes to a **tier**, and any runner can fill it: a subagent in this session, Codex, or another agent CLI. A worker needs only read and write access to the corpus and brain folders and the path to the file that instructs it.

| Job | Tier | Effort | Runs | Why |
|---|---|---|---|---|
| Discover sources | the current session | medium | 0 | Needs search and the user's approval. |
| Extract notes | **light**: the runner's fast, cheap model | low | 1 per source | Careful reading and copying. About 80% of a build's tokens, and `verify.py` catches copying errors. |
| Synthesize the brain | **heavy**: the runner's strongest model | high | 1 | Judgment across the whole corpus: clustering, shifts over time, the hot sheet. |
| Fix verify problems | whoever synthesized | low | 0 | Small edits against the corpus. |
| Ask | the current session | medium | 0 | One answer, read from the brain. |

A run costs roughly 50K tokens, more for a long source. Before the first dispatch, show the user this assignment mapped to the models their chosen runner offers, with the run count, and wait for a yes.

## Scripts

Both live in `scripts/` beside this file. Run each with `--help` for its commands.

- `corpus.py` captures sources into the corpus and indexes them.
- `verify.py` checks a brain's quotes against the corpus and counts phrases.
