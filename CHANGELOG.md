# Changelog

## core 0.1.1 (2026-11-23)

Findings from the first run of `repo-setup` on a real repository (a .NET, React and Expo monolith):

- `repo-setup` now checks statements from READMEs and status notes against the repository before copying them; the first run carried over a folder and a branch description that no longer existed.
- The verify step says what to do in a repository with several packages or stacks.
- The secret-file step also denies the usual untracked names (`.env`, `.env.local`) when absent, never denies tracked non-secret configuration, and prints the rules when editing the settings file is refused.
- `kit.py plug` no longer adds a second comment line when the `.claude/` ignore rule it replaces already has one above it.

## 0.1.0 (2026-11-23)

- Packages: `core` (grill-me, grilling, handoff, fable-orchestration, repo-setup, session-start progress hook), `ui` (frontend-design, webapp-testing), and `superpowers` v7.0.2 pinned to a commit.
- `bin/kit.py`: plug, unplug, status, install. Touches only `.claude/settings.json` and, when needed, `.gitignore`; never commits.
- `repo-setup`: writes `AGENTS.md`, `CLAUDE.md` and `docs/PROGRESS.md` from templates, defines a verify command that runs on Windows, macOS and Linux and is quiet on success, adds deny rules for secret files, and offers path-scoped rules for high-risk code.
- Team rules in the `AGENTS.md` template: build only what was asked, change only what the task needs, keep changes small, verify before done, never weaken a test to pass it, ask before anything hard to undo, justify new dependencies, no worktrees unless asked, delete plans after merge, one task per subagent, keep output out of the context.
- `fable-orchestration`: one task per delegate with a ceiling of about 200K tokens or 100 tool calls, a stop condition in every brief, output kept out of the context.
- Session-start hook shows the top of `docs/PROGRESS.md`; runs through the cross-platform wrapper from superpowers and uses shell builtins only.
- `bin/usage.py`: local usage report by model, main session versus subagent, context size and project.
- Tests for `kit.py`, the hook and the manifests; CI on Windows, macOS and Linux.
- Files read by agents are in English. `KULLANIM.md` is a Turkish user guide.
