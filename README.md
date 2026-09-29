# Skills

Agent skills I use and maintain. Each folder is one skill.

| Skill | What it does |
| --- | --- |
| [learn](./learn) | Turns any folder into a course that remembers you: short lessons pitched just past what you know, real quizzes, and a progress page that picks up where you left off. |

## Install

### With one command (needs Node.js)

```
npx skills add RayDomD/Skills --skill learn -g
```

It asks which agents to install for (Claude Code, Codex, and others). `-g` installs it for your whole machine rather than one project. To see every skill in this repo first, run `npx skills add RayDomD/Skills --list`.

To get later changes: `npx skills update`.

### By hand

1. Click the green **Code** button on this page, then **Download ZIP**, and unzip it. (Or `git clone https://github.com/RayDomD/Skills`.)
2. Copy the skill's folder, e.g. `learn`, into your agent's skills folder:

   | Agent | Put it at |
   | --- | --- |
   | Claude Code | `~/.claude/skills/learn/` |
   | Codex CLI | `~/.codex/skills/learn/` |
   | Other agents | Their skills folder, or point the agent at `SKILL.md` |

   On Windows, `~` is your user folder, e.g. `C:\Users\<you>`.
3. Restart the agent.

Each skill carries its own `LICENSE`.
