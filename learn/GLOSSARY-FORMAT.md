# GLOSSARY.md Format

`GLOSSARY.md` is the canonical language for this teaching workspace. All explainers, exercises, and learning records should adhere to its terminology. Building it is itself part of learning: compressing a concept into a tight definition is evidence the user understands it.

## Structure

```md
# {Topic} Glossary

{One or two sentence description of the topic this glossary covers.}

## Terms

**Hypertrophy**:
Muscle growth driven by mechanical tension and metabolic stress over repeated training sessions.
_Avoid_: Bulking, getting big

**Progressive overload**:
Systematically increasing the demand on a muscle over time — via load, volume, or intensity.
_Avoid_: Pushing harder, levelling up

**RPE (Rate of Perceived Exertion)**:
A 1–10 self-rating of how hard a set felt, where 10 is failure and 8 means two reps left in the tank.
_Avoid_: Effort score, intensity rating
```

`## Terms` alone is enough for topics whose vocabulary is all concepts. Topics with tools and a callable surface — programming, music software, anything with equipment — split it into three sections instead:

```md
## Concepts

**Axes**:
The single plot area a chart is drawn on. One Figure can hold several.
_Avoid_: The plot, the graph, the chart

## Libraries

**pandas**:
The table library. Holds data in memory and reshapes it into the shape a chart
needs, before anything is drawn.

**matplotlib**:
The drawing library. Every visible piece of a chart — line, title, tick, legend —
is a matplotlib object that can be addressed and restyled.

## Functions

| What you write | What it is | Lesson |
| --- | --- | --- |
| `df.shape` | A pair, `(rows, columns)`. A property, not a call — no parentheses. | 0001 |
| `df.head()` | The first 5 rows. A method, so it needs the parentheses. | 0001 |
| `plt.subplots()` | Makes a Figure and one Axes, handed back as a pair. | 0001 |
```

## Rules

- **Add a term only when the user understands it.** The glossary is a record of compressed knowledge, not a dictionary the user reads to learn. If the user has just been introduced to a concept, wait until they can use it correctly before promoting it here.
- **Be opinionated.** When several words exist for the same concept, pick the best one and list the rest as aliases to avoid. This is how language compresses.
- **Keep definitions tight.** One or two sentences. Define what the term IS, not what it does or how to do it.
- **Use the glossary's own terms inside definitions.** Once a term is in the glossary, prefer it everywhere — including inside other definitions. This is what makes complex terms easier to grasp later.
- **Group under subheadings** when natural clusters emerge (e.g. `## Anatomy`, `## Programming`). A flat list is fine when terms cohere.
- **Flag ambiguities explicitly.** If a term is used loosely in the wider field, note the resolution: "In this workspace, 'set' always means a working set — warm-ups are tracked separately."
- **The understanding gate applies to Concepts only.** Libraries go in when first used. Functions go in immediately, on the lesson that taught them: that table is a lookup aid, not a record of comprehension, and gating it just means the user cannot look things up.
- **Say what a thing is, not how to use it.** One or two lines each, in every section. Usage examples and copy-paste patterns belong in a `reference/` cheat sheet arranged in workflow order. A glossary that grows code blocks has taken on a job that is not its own.
- **Record the lesson number in the Functions table.** It is how the user retraces where something came from, and how you spot a function taught but never used again.
- **Call out what trips people up, in the definition itself.** A property mistaken for a method, a false friend between two languages, a move whose name implies the wrong body part. One clause is enough, and it is the clause that earns the entry.
- **Revise as understanding deepens.** A definition the user wrote in week one may be wrong by week six. Update in place; do not leave stale entries.
