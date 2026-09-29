# /learn

A skill that turns any folder into a course that remembers you. Tell it what you want to learn and why, and each session it teaches one short lesson just past what you already know, quizzes you, and saves the results so the next session picks up where you left off.

## Install

With Node.js installed, one command does it:

```
npx skills add RayDomD/Skills --skill learn -g
```

Or copy this whole `learn` folder into your agent's skills folder by hand (see the [repo README](../README.md#by-hand) for downloading it):

| Agent | Put it at |
| --- | --- |
| Claude Code | `~/.claude/skills/learn/` |
| Codex CLI | `~/.codex/skills/learn/` |
| Other agents | Their skills folder, or point the agent at `SKILL.md` |

On Windows, `~` is your user folder, e.g. `C:\Users\<you>`. Restart the agent afterwards.

## Use

1. Make an empty folder for the topic, e.g. `learn-spanish`, and open your agent in it.
2. Run `/learn` followed by the topic, e.g. `/learn conversational Spanish for a trip in March`.
3. The first session asks why you want to learn it. Answer concretely; everything else is built from that.
4. Come back to the same folder for each session and run `/learn` again.

One topic per folder.

## Requirements

None required. The skill checks your machine and picks the best way to deliver lessons:

- **Obsidian with the Dataview plugin** (DataviewJS on): lessons open as notes with quizzes built in.
- **Python installed**: lessons open in your browser from a small local server, with quizzes that save as you go. If a lesson page is blank, run the `start-server` file in your topic folder.
- **Neither**: lessons are pages you double-click, and the graded quiz happens in the chat.

You can ask for a different mode any time, e.g. "use chat grading".

## What ends up in your topic folder

- `MISSION.md`: why you're learning this
- `PROGRESS.md`: what you've done, your scores, what needs review, what's next
- `lessons/`: the lessons
- `grades/`: your quiz results
- `GLOSSARY.md`, `QUESTIONS.md`, `reference/`: terms, your questions, and cheat sheets

## License

MIT. See `LICENSE`.
