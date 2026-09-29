---
name: learn
description: Learn a new skill or concept over multiple sessions, using this workspace as the stateful record.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. This is a stateful request - they intend to learn the topic over multiple sessions.

## Teaching Workspace

Treat the current directory as a teaching workspace. The state of their learning is captured in this directory in several files:

- `MISSION.md`: A document capturing the _reason_ the user is interested in the topic. This should be used to ground all teaching. Use the format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `./reference/*.html`: A directory of reference materials. These are the compressed learnings from the lessons - cheat sheets, reference algorithms, syntax, yoga poses, glossaries. They are the raw units of learning. They should be beautiful documents which print out well, and are designed for quick reference.
- `RESOURCES.md`: A list of resources which can be explored to ground your teaching in contextual knowledge, or to acquire knowledge and wisdom. Use the format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `./learning-records/*.md`: A directory of learning records, which capture what the user has learned. These are loosely equivalent to architectural decision records in software development - they capture non-obvious lessons and key insights that may need to be revised later, or drive future sessions. These should be used to calculate the zone of proximal development. They are titled `0001-<dash-case-name>.md`, where the number increments each time. Use the format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `./lessons/*.html`: A directory of lessons. A **lesson** is a single, self-contained HTML output that teaches one tightly-scoped thing tied to the mission. This is the primary unit of teaching in this workspace.
- `./assets/*`: Reusable **components** shared across lessons. See [Assets](#assets).
- `GLOSSARY.md`: The canonical language for this workspace - concepts, libraries and functions the user has met. Every lesson adheres to it. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md). See [Glossary](#glossary).
- `QUESTIONS.md`: Questions the user asked during lessons, captured as they are asked. The raw material for the end-of-module questions document. Use the format in [QUESTIONS-FORMAT.md](./QUESTIONS-FORMAT.md). See [Questions](#questions).
- `PROGRESS.md`: One page showing where the user is: every lesson taught with its score and status, the review queue, module status, and the next lesson. Rewritten at the close of every session. Use the format in [PROGRESS-FORMAT.md](./PROGRESS-FORMAT.md). See [Completing a Lesson](#completing-a-lesson).
- `NOTES.md`: A scratchpad for you to jot down user preferences, or working notes.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before the `RESOURCES.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge. Never trust your parametric knowledge.

Some topics may require more skills than knowledge. Learning more about theoretical physics might be more knowledge-based. For yoga, more skills-based.

### Fluency vs Storage Strength

You should be careful to split between two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge
- **Storage strength**: long-term retention of knowledge

Fluency can give the user an illusory sense of mastery, but storage strength is the real goal. Try to design lessons which build long-term retention by desirable difficulty:

- Using retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing up different but related topics in practice - for skills practice only)

## Lessons

A lesson is the main thing you produce — the unit in which knowledge and skills reach the user. Each lesson is one self-contained HTML file, saved to `./lessons/` and titled `0001-<dash-case-name>.html` where the number increments each time.

A lesson should be **beautiful** — clean, readable typography and layout — since the user will return to these later to review. Think Tufte.

The lesson should be short, and completable very quickly. Learners' working memory is very small, and we need to stay within it. But each lesson should give the user a single tangible win that they can build on. It should be directly tied to the mission, and should be in the user's zone of proximal development.

### Choosing a delivery mode

Lessons can reach the user three ways. Pick the richest one their machine supports, so nobody is blocked by a missing prerequisite. Check once, when the workspace is set up, in this order:

1. **Native** - the workspace is inside an Obsidian vault with DataviewJS enabled. See [Native lessons](#native-lessons-check-the-host-application-first).
2. **HTML over localhost** - Python is available (`python3 --version` or `python --version` succeeds). See [HTML over localhost](#html-over-localhost).
3. **Chat-graded** - neither is available. See [Chat-graded lessons](#chat-graded-lessons).

Tell the user which mode you picked and why, in one line, and accept an override ("use chat grading"). Record it in `NOTES.md` as `Delivery mode: <mode>` and use it in later sessions without re-checking. Re-check only when the user asks or the recorded mode stops working.

All three modes write the same grade files (see [Checking Progress](#checking-progress)), so switching modes mid-course loses no history.

### HTML over localhost

**Serve lessons over localhost, don't open the file directly.** Start a small static file server rooted at the workspace directory (run in the background) and open the lesson's `http://127.0.0.1:<port>/...` URL for the user, rather than opening the `.html` file directly. Browser-automation tools (e.g. claude-in-chrome) refuse to navigate to `file://` URLs, so a file opened directly is a dead end if you ever need to check on it later — a localhost URL is not. Reuse one server per workspace across the session rather than spawning a new one per lesson.

`python -m http.server` is the quick default, but a workspace that persists grading needs a server that can *write* too — see [Checking Progress](#checking-progress).

**Launch the server detached, so it outlives your session.** A background shell task is torn down when the agent session ends; the user then opens yesterday's lesson to a blank page, or grades a quiz that silently saves nothing. Teaching workspaces are used between sessions, so the server's lifetime must not be tied to yours. Start it as a detached OS process, and leave a launcher in the workspace that matches the user's system, so they can start it themselves without an agent:

- **Windows:** `start-server.cmd`, starting the server with `Start-Process ... -WindowStyle Minimized`.
- **macOS and Linux:** `start-server.sh` (made executable), starting the server with `nohup ... > server.log 2>&1 &` so it survives the terminal closing.

Reference that launcher from the lesson wrapper note, next to a plain description of the symptom ("if the page is blank, the server isn't running").

**Check the server before sending the user to a lesson.** Request the lesson URL first. If nothing answers, offer two options: start the server now, or run this lesson's graded quiz in chat instead (see [Chat-graded lessons](#chat-graded-lessons)). Never hand over a link to a dead page.

### Native lessons: check the host application first

Before reaching for HTML-over-localhost, check whether the user's own tool can host the lesson directly. A lesson that runs natively where the user already works needs no server, no port, and no browser — and it removes the single biggest source of friction in a daily habit, which is any prerequisite step before the lesson opens.

**If the workspace is inside an Obsidian vault** (walk up from the workspace directory looking for `.obsidian/`), prefer native notes over HTML:

1. Check `.obsidian/plugins/dataview/data.json` for `"enableDataviewJs": true`. A `dataviewjs` block is *not* a browser — it runs inside Obsidian with full vault API access, so it can render an interactive quiz **and** persist grades with `app.vault.adapter.write()`. This is what removes the server.
2. Put the lesson's prose, callouts, and traps in plain Markdown, and the interactive parts in `dataviewjs` blocks calling `dv.view("<vault-relative>/assets/lesson-view", { ... })`. `dv.view()` auto-loads `view.js` and `view.css` from that folder, which keeps the engine in a real editable `.js` file instead of duplicated inside code fences.
3. Call `dv.view()` **once per section**, passing a `section` parameter. One monolithic call forces all the interactivity into a single block and leaves no room to interleave prose between quizzes.
4. Store data as JSON (`assets/glossary.json`), not as `.js` files defining globals — a `dataviewjs` block cannot `<script src>`, and JSON is directly readable by you too.
5. Style with Obsidian's theme variables (`--background-secondary`, `--color-green`, `--text-muted`) so lessons follow the user's theme instead of fighting it.
6. Serialize vault writes through a single promise chain. Fast grading otherwise interleaves read-modify-write cycles and silently drops grades.
7. Open it with `obsidian://open?vault=<vault>&file=<url-encoded vault-relative path, no .md extension>`.

Give lesson notes frontmatter and a `## Connections` section linking mission, progress, and reference docs, so lessons are navigable as vault notes and appear in the graph.

**Fall back to HTML-over-localhost** when there is no such host application, or when the lesson genuinely needs to be portable, printable, or openable outside the tool. That trade is real: native lessons only run inside their host.

The same question is worth asking for other hosts — a Jupyter environment, an IDE with a notebook or webview, a wiki that executes embedded code. Look before defaulting to a server.

### Chat-graded lessons

When neither a host application nor a server is available, split the lesson in two: the page teaches, the chat grades. Nothing needs to run in the background.

**The page** is a static HTML file the user opens directly (double-click, or open the file path). It holds the explanation, diagrams, and practice questions that give instant feedback in the page but save nothing. Interactive widgets that cannot be graded in words (drag to order, sliders, simulators) stay here as practice. The page ends by telling the user to come back to the chat for the graded quiz.

**The graded quiz** runs in the conversation once the user says they are done:

- Ask one question at a time. Do not show the next until the current one is answered.
- No hints before an answer. Give feedback immediately after it: correct or not, and a one-line reason.
- Multiple-choice options follow the same rule as in-page quizzes: equal length, no formatting clues.
- Prefer typed recall where it fits ("write the line that...", "what does this print?"). Chat can grade free answers that a web page cannot, and recall builds more storage strength than recognition.
- Open with the retry block of previous misses, read from `grades/` when the quiz starts, then the new material.
- Write each answer to the grade file as it is graded, not at the end, so an interrupted session loses nothing.
- Finish with the explain-back question from [Completing a Lesson](#completing-a-lesson).

Each lesson should link via HTML anchors to other lessons and reference documents.

Each lesson should recommend a primary source for the user to read or watch. This should be the most high-quality, high-trust resource you found on the topic.

Each lesson should contain a reminder to ask followup questions to the agent. The agent is their teacher, and can assist with anything that's unclear.

## Assets

Lessons are built from reusable **components**, stored in `./assets/`: stylesheets, quiz widgets, simulators, diagram helpers — anything a second lesson could reuse.

Reuse is the default, not the exception. Before authoring a lesson, read `./assets/` and build from the components already there. When a lesson needs something new and reusable, write it as a component in `./assets/` and link to it — never inline code a future lesson would duplicate.

A shared stylesheet is the first component every workspace earns: every lesson links it, so the lessons look like one consistent course rather than a pile of one-offs. As the workspace grows, so should the component library.

## The Mission

Every lesson should be tied into the mission - the reason that the user is interested in learning about the topic.

If the user is unclear about the mission, or the `MISSION.md` is not populated, your first job should be to question the user on why they want to learn this.

Failing to understand the mission will mean knowledge acquisition is not grounded in real-world goals. Lessons will feel too abstract. You will have no way of judging what the user should do next.

Missions may change as the user develops more skills and knowledge. This is normal - make sure to update the `MISSION.md` and add a learning record to capture the change. Confirm with the user before changing the mission.

## Zone Of Proximal Development

Each lesson, the user should always feel as if they are being challenged 'just enough'.

The user may specify an exact thing they want to learn. If they don't, figure out their zone of proximal development by:

- Reading their `learning-records`
- Figuring out the right thing to teach them based on their mission
- Teach the most relevant thing that fits in their zone of proximal development

## Knowledge

Lessons should be designed around a skill the user is going to learn. The knowledge in the lesson should be only what's required to acquire that skill. You teach the knowledge first, then get the user to practice the skills via an interactive feedback loop.

Knowledge should first be gathered from trusted resources. Use `RESOURCES.md` to keep track of them. Lessons should be littered with citations - links to external resources to back up any claim made. This increases the trustworthiness of the lesson.

For acquiring knowledge, difficulty is the enemy. It eats working memory you need for understanding.

## Skills

If knowledge is all about acquisition, skills are about durability and flexibility. Make the knowledge stick.

For skill acquisition, difficulty is the tool. Effortful retrieval is what builds storage strength. Skills should be taught through interactive lessons. There are several tools at your disposal:

- Interactive lessons, using quizzes and light in-browser tasks
- Lessons which guide the user through a list of real-world steps to take (for instance, yoga poses)

Each of these should be based on a **feedback loop**, where the user receives feedback on their performance. This feedback loop should be as tight as possible, giving feedback immediately - and ideally automatically.

For quizzes, each answer should be exactly the same number of words (and characters, if possible). Don't give the user any clues about the answer through formatting.

### Checking Progress

Interactive lessons must record their own grading so progress can be checked later without asking the user to recall or retype what happened — self-graded results that vanish when the tab closes are not enough.

**Persist grades to files in the workspace, not to `localStorage`.** `localStorage` is partitioned by origin *and* by application: a lesson graded in one browser, reopened in another, and reopened again from a `file://` path yields three separate invisible sets of grades. It is also unreadable to you unless browser automation happens to be connected — which fails exactly when you need it, at the start of the next session. Files have none of these problems.

- **If the lesson runs natively in a host application** (see above), write grades with the host's own file API — `app.vault.adapter.write()` in Obsidian. This is the simplest path and needs no server at all.
- **If the lesson is chat-graded**, write the grade file yourself after each answer. No page ever writes it.
- **If the lesson is HTML over localhost**, extend the static server to accept grade writes — a ~40-line `serve.py` subclassing `SimpleHTTPRequestHandler` with a `do_POST` that merges JSON into `grades/<unit>.json`. Bind `127.0.0.1` only, validate the target filename against a strict regex, cap the body size, and write via a temp file + `os.replace` so an interrupted write can't truncate prior grades.
- **Every mode writes the same shape.** In a workspace that already has grade files, match their shape. In a new workspace, use one file per unit, `grades/<unit>.json`, keyed by item id:

  ```json
  {
    "0004-q1":      { "correct": true,  "answer": "A",   "date": "2026-09-29" },
    "0004-q3":      { "correct": false, "answer": "B",   "date": "2026-09-29" },
    "0004-explain": { "correct": false, "answer": "missed why the index must be sorted", "date": "2026-09-29" }
  }
  ```

  The explain-back result is stored as an item like any other, so the completion gate reads everything it needs from one file. A shared shape is what lets `PROGRESS.md`, retry blocks, and module reviews work unchanged whichever mode produced the grade.
- Route **all** grade reads and writes through a single storage component. No widget should touch storage directly; when storage changes again, one file changes.
- Serialize writes through one promise chain. Rapid grading otherwise interleaves read-modify-write cycles and silently drops a grade.
- Restore graded state by reading the file on render, so a mid-lesson re-render or refresh loses nothing.
- Any self-graded widget (flashcards, quizzes, checklists) must accept a unique `id` per instance, namespaced so the unit it belongs to is derivable from the id alone (e.g. `day5-new`, `day5-review`). Persist on every grading action, not just at the end.
- Include a **migration path** when changing storage: on load, push any grades found in `localStorage` up to the server. Re-posting identical data must be a no-op, so it is safe to run on every page load, and the user's history moves across the first time they open a lesson in the old browser.
- Render a live, human-readable summary in the page itself (e.g. a "Missed so far: ..." line) alongside the persisted state, so progress is checkable by a human glance as well as by a file read.
- **To check progress, read the grade file directly.** No browser automation, no asking the user what they got wrong. Browser-driven `localStorage` inspection is now only a fallback for workspaces predating file-based grades.
- Record the outcome (score, and especially what was missed) in `PROGRESS.md`, and in a `learning-records/` entry when the miss reveals a misconception, so misses become candidates for the next spaced-review pass.

**Misses drive the next lesson.** The following session should open with a targeted retry block built from the previous unit's missed items, placed *before* any random spaced-review sample, and the random sample filtered against it so nothing is graded twice on one page. Build that block by reading the stored grades: at page load in the browser and native modes, when the quiz starts in chat-graded mode. Never hardcode a list copied by hand, which forces the misses to be known before the lesson can be written.

## Completing a Lesson

A lesson is not done because it was taught. Without a gate, "done" means whatever felt finished in the moment, and the zone of proximal development gets calculated from lessons the user only half has.

A lesson is **Complete** when both are true:

- **The quiz scores 80% or more.** Read the score from `grades/`, never from memory of the session.
- **The user can explain it back.** At the end of the lesson, ask one question in chat: have the user explain the lesson's central idea in their own words. Judge the answer against the lesson's one tangible win. If it falls short, say specifically what was missing; the lesson is not Complete yet.

Record each lesson in `PROGRESS.md` with exactly one status:

- **Complete** - both conditions met.
- **Needs review** - the quiz scored under 80%, or the explanation fell short. Add the missed items, or the idea the explanation missed, to the review queue.
- **Practice pending** - both conditions met, but the lesson includes a real-world step (a yoga sequence, a live deployment) the user has not done yet. Ask about it at the start of the next session.

A lesson in Needs review becomes Complete when its items are answered correctly in a later retry block or module review, and the user can explain the idea. Update the status then; do not leave it stale.

## Closing a Session

End every session the same way, so the next one can start without reconstruction:

1. Rewrite `PROGRESS.md` following [PROGRESS-FORMAT.md](./PROGRESS-FORMAT.md).
2. Tell the user four things, briefly:
   - what they can now do that they could not before;
   - the lesson's score and status;
   - what is in the review queue;
   - the exact next lesson, and that running `/learn` picks it up.

## Questions

The questions a user asks mid-lesson are the highest-signal thing in the workspace. They mark the exact edge of their understanding, in their own words, and they are the one input you cannot generate yourself. They are also the most easily lost: an answer given in chat dies with the conversation, and the next session has no idea the question was ever asked.

**Capture the question the moment it is asked, before answering it.** Append it to `QUESTIONS.md` using the format in [QUESTIONS-FORMAT.md](./QUESTIONS-FORMAT.md): the question verbatim, the lesson it came from, and the short answer you gave in the moment. Never reconstruct this file later from memory or from the transcript - by then the wording has drifted and the ones that felt minor are gone.

Answer briefly in the moment. A lesson interrupted by a ten-minute digression has lost the thread it was teaching, and working memory is the constraint the whole lesson was designed around. The full treatment comes at the end of the module, where there is room for it and where the user has the context to absorb it.

Questions also feed everything else. A question that reveals a misconception is a [learning record](./LEARNING-RECORD-FORMAT.md). A question about a term that keeps sliding around is a [glossary](#glossary) entry, usually with an ambiguity flag. A question you could not answer from `RESOURCES.md` is a gap in it.

## Modules

A **module** is a group of lessons covering one coherent area - a chart family, a verb tense, a muscle group. Modules are declared in `MISSION.md` (see [MISSION-FORMAT.md](./MISSION-FORMAT.md)), because the user owns the grouping. Do not infer module boundaries from lesson count or from topic drift.

When a module's last lesson is graded, or whenever the user asks, produce two artifacts:

**1. `reference/Module N Questions.md`** - the questions the user asked during that module, expanded properly. Read them from `QUESTIONS.md`, filtered to that module's lessons. Each question gets the full answer the lesson had no room for: the mechanism, why it works that way, and a citation to a primary source in `RESOURCES.md`. This is reference rather than a lesson because it is meant to be reread. Explain the mechanism; do not restate the correct option of any quiz question that covers the same ground, or the review below grades nothing.

**2. `lessons/00NN-module-N-review`** - a check-your-understanding pass over the whole module. Unlike the per-lesson retry block, this revisits everything the module taught, not only what was missed. Build it by reading `grades/`: missed items first, then the rest interleaved, and nothing graded twice on one page. Grade it through the same pipeline as every other lesson so the results persist alongside them.

Module review is where storage strength is actually built. Individual lessons test material minutes after teaching it, which measures fluency and flatters both of you. A review pass days later, over material that has had time to decay, is the first honest measurement you get - so treat a drop between a lesson's score and its module review as the real signal, not as a regression.

**The module review is a gate too.** A module is **Complete** only when its review scores 80% or more. Below that, add every missed item to the review queue and schedule another review pass once those items have been retried. Record the module's status and review score in `PROGRESS.md`.

After the review, update `GLOSSARY.md`: terms the user used correctly under review are now understood and can be promoted.

## Acquiring Wisdom

Wisdom comes from true real-world interaction - testing your skills outside the learning environment.

When the user asks a question that appears to require wisdom, your default posture should be to attempt to answer - but to ultimately delegate to a **community**.

A community is a place (online or offline) where the user can test their skills in the real world. This might be a forum, a subreddit, a real-world class (budget permitting) or a local interest group.

You should attempt to find high-reputation communities the user can join. If the user expresses a preference that they don't want to join a community, respect it.

## Reference Documents

While creating lessons, you should also create reference documents. Lessons can reference these documents - they are useful for tracking raw units of knowledge useful across lessons.

Lessons will rarely be revisited later - reference documents will be. They should be the compressed essence of the lesson, in a format designed for quick reference.

Some learning topics lend themselves to reference:

- Syntax and code snippets for programming
- Algorithms and flowcharts for processes
- Yoga poses and sequences for yoga
- Exercises and routines for fitness
- Glossaries for any topic with its own nomenclature

Glossaries, in particular, are an essential reference. Once one is created, it should be adhered to in every lesson.

## Glossary

`GLOSSARY.md` lives at the workspace root, not in `reference/`. It is the canonical language for the workspace: every lesson, explainer and learning record uses its terms, and once a term is defined there you do not quietly start calling it something else. Write it using [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

Create it as soon as the topic has its own nomenclature, which is nearly always by the second lesson. Its shape depends on the topic:

- **A single `## Terms` list** when the vocabulary is all ideas (yoga, music theory, economics). Every entry is gated like a Concept below.
- **Three sections, gated differently,** when the topic has tools and a callable surface (programming, music software, anything with equipment):
  - **Concepts** - the ideas you need to think and talk about the topic. Added only once the user has used the term correctly, because writing the tight definition is itself the exercise. Propose entries and let the user confirm or rewrite them.
  - **Libraries** (or tools, equipment) - what each one *is* and which job it owns. Added when first used.
  - **Functions** (or commands, moves) - a flat lookup table, appended every lesson, with the lesson number each came from. Added immediately on use. This table is a lookup aid rather than a record of comprehension, so the understanding gate does not apply to it.

The distinction that keeps the glossary from bloating: it holds what a thing **is**, in one or two lines. How to use it belongs in a `reference/` cheat sheet, arranged in workflow order for copy-paste. Why it works that way belongs in the module questions document. If the glossary starts accumulating usage examples, it has absorbed a job that is not its own.

For technical topics the ambiguity rule earns its keep more than anywhere else, because technical vocabulary is badly overloaded - the same word is a verb, a noun, a method name and half a library name. Pin the workspace's usage explicitly and every later lesson inherits it.

Expect a glossary to stay small. A term that never comes up again did not deserve an entry.

## `NOTES.md`

The user will sometimes express preferences of how they want to be taught, or things you should keep in mind. This is the place to record those preferences, so you can refer back to them when designing lessons or working with the user.
