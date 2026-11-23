# <Project name>

<One sentence: what this repository does and who uses it.>

## Commands

- Setup: `<command>`
- Run: `<command>`
- Verify: `<command>` (build, type check, lint, fast tests; must run on Windows, macOS and Linux)
- Heavy tests: `<command>` (CI only, or when asked)

## Layout

- `<dir>/`: <what lives here>
- Details: `docs/<document>.md`

## Do not touch

- <Generated files, locked decisions, areas owned by another team>

## Domain terms

Product names and domain words that are not English stay as they are in the UI and in conversation. Map each to its name in code so nobody translates it differently.

- `<term>` = `<CodeName>`: <one-line meaning>

## Team rules

This section is the same in every repository that uses the kit and comes from the kit template. Do not edit it here; change it in the kit.

- Build only what was asked. No extra features, options, abstractions, or error handling for cases that cannot happen. If a simpler solution exists, say so before building.
- Change only what the task needs. Do not reformat, rename, or refactor nearby code, and match the existing style. Remove only what your own change made unused; report other dead code instead of deleting it. Every changed line should trace back to the request.
- Keep changes small: one concern per branch and pull request. If a diff grows past what one person can review in one sitting, split it.
- Before saying work is done, run the Verify command listed under Commands. Do not report success without seeing its output; if it is red, say it is red.
- Never make a test pass by deleting it, loosening its threshold, or hiding the failure. If behaviour changes on purpose, write down why and what the new expectation is.
- Stop and ask before anything that is hard to undo: a destructive migration, deleting data or branches, rewriting history, changing an authentication or permission model, breaking a public contract.
- Do not add a dependency without saying what it is for, and check that it is maintained and its licence fits the project.
- When a meaningful piece of work is finished, update `docs/PROGRESS.md`: what was done, what is open, the next step.
- For small work (a one-file fix, a typo, a comment, a rename) skip brainstorming and planning; do it and verify. Work that spans several files or changes behaviour gets a plan first.
- Do not create git worktrees unless the developer asks for one. Work on a branch in the current checkout.
- Design and plan documents under `docs/superpowers/` are working files. When the work is merged, delete its plan. If a design holds a decision that will outlive the work, move that decision to `docs/adr/` and delete the rest.
- When spawning subagents, follow `core:fable-orchestration`: pass the model explicitly on every call, give each subagent one task with a clear end, and have it stop and report rather than take a second task or run past about 200K tokens of context.
- Keep command output out of the context. Use quiet flags and show failures only; filter a log instead of printing it; read the part of a file you need, not the whole file. Everything printed is re-read on every later step.
- For UI work, read this repository's design document first (`docs/design/` if it exists); do not decide by general taste.
- Passwords, keys, and personal data never go into the repository, settings files, or instruction files.
- Files written for agents (this file, `docs/PROGRESS.md`, plans, specs) are in English. Reply to the developer in the language they write in. Text shown to product users stays in the product's language.
