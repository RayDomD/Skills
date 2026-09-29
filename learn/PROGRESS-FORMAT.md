# PROGRESS.md Format

`PROGRESS.md` lives at the workspace root. It is the one page that shows where the user is: what has been taught, how it went, what needs another pass, and what comes next. It is rewritten at the close of every session (see [Closing a Session](./SKILL.md#closing-a-session)).

It is a view, not a second source of truth. Scores and misses live in `grades/`, modules live in `MISSION.md`. The only thing this file owns is each lesson's **status**, because the completion gate's explain-back check happens in conversation and no grade file captures it.

## Structure

```md
# Progress: {Topic}

Last session: {YYYY-MM-DD} · Next: {00NN-dash-case-name}

## Lessons

| #    | Lesson          | Module   | Score | Status           |
| ---- | --------------- | -------- | ----- | ---------------- |
| 0001 | first-dataframe | 1 Basics | 5/5   | Complete         |
| 0002 | groupby-monthly | 1 Basics | 4/5   | Complete         |
| 0003 | tick-labels     | 1 Basics | 3/5   | Needs review     |
| 0004 | stacked-bars    | 2 Charts | 5/5   | Practice pending |

## Review queue

| Item                                 | From | Reason               |
| ------------------------------------ | ---- | -------------------- |
| `ax.set_xticks` vs `set_xticklabels` | 0003 | Missed twice         |
| Why stacking needs a sorted index    | 0004 | Explain-back missing |

## Modules

| Module   | Lessons | Review score | Status      |
| -------- | ------- | ------------ | ----------- |
| 1 Basics | 3       | Not taken    | In progress |
| 2 Charts | 1       | Not taken    | In progress |
```

## Rules

- **Rebuild the derived parts from their sources every time.** Scores and the review queue come from `grades/`; the module list comes from `MISSION.md`. Never carry a score forward from the previous version of this file, or it drifts from the grades the first time a retry changes one.
- **Status is the only hand-written column.** Set it by the gate in [Completing a Lesson](./SKILL.md#completing-a-lesson): `Complete`, `Needs review`, or `Practice pending`. Modules are `In progress` or `Complete`, the latter only at 80% or more on the module review.
- **List lessons taught plus the one next.** No pre-planned route. Each lesson is picked from the zone of proximal development at the time, so a planned route is wrong within a few lessons.
- **Every review queue item names where it came from.** The lesson number is how the next retry block finds the item, and the reason says whether it was a quiz miss or an explanation gap.
- **Clear an item only when it is answered correctly later,** in a retry block or module review. Update the lesson's status in the same pass.
- **In an Obsidian workspace, compute the derived parts live.** A `dataviewjs` block can read `grades/*.json` and render the scores and review queue on open, so only the status column is ever written. Use the same `dv.view()` engine as the lessons.
- **Keep it to one screen.** Once a module is Complete, collapse its lessons to one line. The detail is still in `grades/`.
