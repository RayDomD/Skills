---
name: mikoshi
description: Convene captured soulkill brains to argue a decision or question, with the user choosing who sits, who faces whom, and on what. Use when the user says "mikoshi", wants advisors matched or debated against each other, wants a council or board on a decision, or names two or more captured people and a question.
argument-hint: "<who> [vs <who> [on <topic>]] : <decision or question> [--quick]"
---

Mikoshi seats brains from `~/.claude/brains/` around one question. Each **seat** argues from its own lens at full strength. You are the **Chair**: you run the rounds, keep the score, and write the report, and you hold no side.

Reference, read before the first run: [`rounds.md`](rounds.md) (what each seat is sent), [`scoring.md`](scoring.md) (the math), [`report.md`](report.md) (the output).

## The table

Four settings define a session. Take what the user gave, and ask for the rest in one batch.

| Setting | Choices |
|---|---|
| **What** | A **decision** with options A, B, C gets scores and a verdict. An **open question** gets stances and cruxes, unscored. |
| **Who** | Any two or more brains. When the user names none, show the roster (each brain's pillar and question, from the first bold line of its `_hot.md`) and let them pick. |
| **Matchups** | Pairs the user wants head to head, each with an optional topic: "Hormozi vs Buffett on cash risk". A seat can sit in several. Without any, you set them after Round 1. |
| **Depth** | **Full**: open, debate, and for a decision a vote on your draft resolution. **Quick** (`--quick`): open and debate only. |

## Steps

### 1. Brief

Write `brief.md`, under 300 words, with every assumption marked `(assumed)`:

- The question in one line. For a decision, the options as A, B, C, always including "keep doing what you do now".
- The facts the seats need: the situation, the numbers, the limits, what success looks like, and which way the user leans.
- For a decision, a relevance **weight** per seat from 1 to 3 with a one-line reason (`scoring.md`). The user's own weights replace yours.
- The matchups the user set.

Ask for a missing fact only when the answer would turn on it. Save the session in `~/.claude/mikoshi-sessions/YYYY-MM-DD-<topic>/`.

### 2. Round 1: opening

Dispatch every seat in one message with the Round 1 prompt, so each opening is written without sight of the others. Save the cards word for word to `round-1.md` under one `## <Seat>` heading each, and send back once any card missing a field.

Then add `## Chair notes`:

- The **cruxes**: the one to three underlying disagreements that explain the split, each labelled fact, numbers, or values, with the seats on each side. A topic the user attached to a matchup is a crux.
- The **matchups** for Round 2. Keep the user's. Give every other seat the seat furthest from it on the main crux.
- When every seat agrees, name the strongest unargued alternative as a crux and assign the seat whose pillar it fits best to argue it at full strength.

### 3. Round 2: debate

Dispatch every seat with the Round 2 prompt, its matchup, and the cruxes. Save to `round-2.md` with `## Chair notes`: who moved and why, which cruxes resolved, and what is still open.

An open question, or a quick decision, goes to step 5 from here.

### 4. Round 3: vote

Write `draft-resolution.md`: the recommended option, the conditions the seats asked for (merged, each checkable), next steps with dates, the cheapest test, and kill criteria. Weigh arguments over headcount: one seat with a decisive fact outweighs three with a preference. Apply the overrides in `scoring.md`.

Dispatch every seat with the Round 3 prompt. Save to `round-3.md` with a `## Chair` section listing each amendment, whether you adopted it, and why. Adopt an amendment no seat opposes or whose argument went unanswered; put the losing side of a conflict in the minority report.

### 5. Verify and report

1. Run `python ~/.claude/skills/mikoshi/scripts/check_quotes.py <session folder>`. Remove from the report every quote it prints as unverified.
2. For a decision, compute the numbers from the last round's cards per `scoring.md`.
3. Write `verdict.md` from `report.md`.
4. Give the user the short version in chat, under 200 words: the call or the stances, the scores on one line, the arguments that carried the room, the strongest objection, and the path to `verdict.md`.

## Chair rules

- Every point in the report comes from a seat. A gap you notice goes to the closest seat as a crux in the next round.
- Seat cards are quoted exactly as written.
- Seats speak in their person's voice; your own writing is plain English.
- The seats are simulations. A line is that person's words only when it is a verbatim quote with a source id from their brain.

## Agent assignment

Each seat answers by following `~/.claude/skills/soulkill/speak.md` for its brain. Any runner can fill a seat: a subagent in this session, Codex, or another agent CLI with read access to `~/.claude/brains/` and the session folder.

| Job | Tier | Effort | Runs |
|---|---|---|---|
| Chair | the current session | medium | 0 |
| Seats | **mid or heavy**, the same tier for every seat | medium | seats x rounds |

Every seat runs on the same tier, so no advisor loses an argument to a weaker model. A run costs roughly 50K tokens. Before the first dispatch, show the user the seats, the rounds, the run count, and the tier mapped to the models their runner offers, and wait for a yes.

Where no workers are available, write each seat's card yourself in turn, finishing one before reading the next brain, and in Round 1 keep each card unseen while you write the others.
