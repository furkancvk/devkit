---
name: repo-setup
description: Prepares a repository for the kit - sets up AGENTS.md, CLAUDE.md, a verify command, docs/PROGRESS.md, secret-file protection and rules for high-risk areas. Manual only (/core:repo-setup).
disable-model-invocation: true
argument-hint: "(optional) one-sentence description of the repository"
---

# Repository setup

Make this repository ready to work with the kit. Turning the plugin on or off is not this skill's job; `bin/kit.py` in the kit repository does that. This skill sets up the repository side the plugin relies on: the files an agent needs in order to know the repository.

The templates are in the `templates/` folder next to this file. Never overwrite an existing file: read it, add what is missing, and show the difference.

Everything you write into these files is in English, whatever language the existing notes are in. Translate; do not drop content. Keep product names and non-English domain words as they are and list them under "Domain terms".

## Steps

1. **Read the repository.** README, package and solution files (`package.json`, `*.sln`, `pyproject.toml`, `go.mod`, `Cargo.toml` and the like), CI workflows, and any existing instruction or handover notes (`AGENTS.md`, `CLAUDE.md`, and whatever status or hand-off documents the team keeps). Take the setup, run, build, type-check, lint, and test commands from these files. Do not invent a command you could not find; ask the user.
   - READMEs and status notes go stale. Before you carry a statement about branches, working copies, folders or the current state into `AGENTS.md` or `docs/PROGRESS.md`, check it against the repository: does the path exist, does git agree, is the date recent. Leave out what you cannot confirm and list it in your final report.

2. **Define the verify command.** It is the one command every agent and developer runs before calling work done, so it must run unchanged on Windows, macOS and Linux. Assume a mixed team.
   - Use only commands that really exist in this repository and finish within a few minutes: build, type check, lint, fast tests. Leave out heavy suites that need a database or a browser; those are CI's job.
   - If the repository has a single `package.json` at its root, add a `verify` script there and make the command `npm run verify`.
   - Otherwise, including repositories with several packages or more than one stack, write the commands themselves under "Verify" in `AGENTS.md`, one per line, to be run in order (for example `dotnet build --nologo -v q`, then `dotnet test --nologo -v q`; or `ruff check .`, then `pytest -q`).
   - Do not add a bash-only or PowerShell-only wrapper script. Reuse a wrapper only if the repository already has one that runs on all three systems.
   - Make it quiet on success and detailed on failure, where the tools allow it: quiet verbosity flags, `npm run --silent <script>`, a failures-only test reporter. Its output goes into the agent's context on every run, so a passing run should print a few lines, not a full log.
   - Run the command once. If it is red, report it as it is; do not remove a step to make it pass.

3. **Write `AGENTS.md`.** Start from `templates/AGENTS.md`.
   - Fill the repository sections at the top (description, commands, layout, do not touch, domain terms) with what you found in step 1. Keep it short: the whole file stays under 100 lines. Link to a document under `docs/` for detail.
   - If `AGENTS.md` already exists, keep its lasting rules. Move state (phases, dated handover notes, "we are currently at") into `docs/PROGRESS.md`. Remove absolute paths that belong to one person's machine.
   - Leave the "Team rules" section exactly as it is in the template; it is the same in every repository.

4. **Write `CLAUDE.md`.** Copy `templates/CLAUDE.md`. Its content is the line `@AGENTS.md`; do not copy rules into it.

5. **Write `docs/PROGRESS.md`.** Start from `templates/PROGRESS.md`. Summarise what is still current from existing handover and status notes, and link to the old note. Put the most important state first: the top of this file is injected into every session.

6. **Protect secret files.** Look for files that hold secrets: `.env`, `.env.*`, key and certificate files, and secret folders used by the deployment setup. Add `Read(...)` rules to `permissions.deny` in `.claude/settings.json`, keeping every other key in that file as it is:
   - for each secret file or folder that exists (for example `"Read(./secrets/**)"`);
   - and, even when absent, for the usual untracked names at any depth: `"Read(./**/.env)"` and `"Read(./**/.env.local)"`.
   - Do not deny example files (`.env.example`) or files that are tracked on purpose and hold no secret, such as public build-time configuration. Look at key names, not values, to tell.
   - If a file that does hold a secret is tracked by git, say so; do not fix it yourself.
   - Editing `.claude/settings.json` may be refused or need approval. If it is refused, print the exact rules for the user to add.

7. **Offer rules for high-risk areas.** Ask the user which parts of the code are expensive to get wrong: typically money, authentication and permissions, database migrations, and public API contracts. For each area they name, write `.claude/rules/<area>.md` from `templates/rule.md`: a `paths:` list of globs for that code, and three to six rules that are specific to it and that you can point to in the code or docs (which test suite must pass, which document is the source of truth, what needs a second person). These files load only when a matching file is touched, so they cost nothing elsewhere. Skip this step if the user names no area; do not invent rules.

8. **Show the difference and stop.** Show `git status` and `git diff --stat`. Do not commit or push; that is the user's decision.

## Do not

- Delete an existing test, CI step, or document.
- Touch the plugin lines (`enabledPlugins`, `extraKnownMarketplaces`) in `.claude/settings.json`; `bin/kit.py` manages them.
- Write a password, key, or personal data into a settings or instruction file.
