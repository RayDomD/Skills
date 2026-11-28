# Skills

Agent skills I use and maintain. Each folder is one skill.

| Skill | What it does |
| --- | --- |
| [handoff](./handoff) | Compacts the current conversation into a living Markdown handoff document in OS temp (with suggested skills, open decisions + defaults, and file pointers) so a fresh session can pick up at `0k` in the Smart Zone. |
| [tdd](./tdd) | Test-driven development loop at pre-agreed public seams: vertical slices (one failing test → one minimal implementation), avoiding implementation-coupled and tautological tests. |
| [code-review](./code-review) | Reviews changes since a fixed git ref along two parallel sub-agent axes — Standards (repo conventions + Fowler code smells) and Spec (requirements match) — and reports them side by side. |
| [vault-hygiene](./vault-hygiene) | Enforces an Obsidian vault's `.vault-standard.yml` note standard across four modes: scaffolding new notes, normalizing existing notes, screening archive notes in, and distilling session records into knowledge notes. |
| [learn](./learn) | Turns any folder into a course that remembers you: short lessons pitched just past what you know, real quizzes, and a progress page that picks up where you left off. |
| [soulkill](./soulkill) | Captures a person into a sourced advisor brain from their videos, writing, or files you supply, then lets you ask it questions. Every quote is tied to a source. Claude Code, global install. |
| [mikoshi](./mikoshi) | Seats two or more soulkill brains around a decision or question, runs them through debate rounds, and writes a scored verdict. Needs soulkill installed. Claude Code, global install. |

## Install

### With one command (needs Node.js)

```
npx skills add RayDomD/Skills --skill handoff -g
```

It asks which agents to install for (Claude Code, Codex, and others). `-g` installs it for your whole machine rather than one project. To see every skill in this repo first, run `npx skills add RayDomD/Skills --list`.

To get later changes: `npx skills update`.

### By hand

1. Click the green **Code** button on this page, then **Download ZIP**, and unzip it. (Or `git clone https://github.com/RayDomD/Skills`.)
2. Copy the skill's folder, e.g. `handoff`, into your agent's skills folder:

   | Agent | Put it at |
   | --- | --- |
   | Claude Code | `~/.claude/skills/handoff/` |
   | Codex CLI | `~/.codex/skills/handoff/` |
   | Other agents | Their skills folder, or point the agent at `SKILL.md` |

   On Windows, `~` is your user folder, e.g. `C:\Users\<you>`.
3. Restart the agent.

Each skill carries its own `LICENSE`.
