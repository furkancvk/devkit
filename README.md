# devkit

A small, opinionated kit for building software with Claude Code. You plug it into a repository with one command and unplug it with another. The skills live here, not in your repositories: a repository only carries two settings that point at the kit.

Türkçe kullanım kılavuzu: [KULLANIM.md](KULLANIM.md).

## What you get

| Package | Contents | Where to turn it on |
| --- | --- | --- |
| `superpowers` | [obra/superpowers](https://github.com/obra/superpowers) v7.0.2, pinned to a commit: design, plan, test-first, debugging, verify-before-done, and a session-start check that makes the agent look for a skill before it acts | every repository |
| `core` | `grill-me`, `grilling`, `handoff`, `fable-orchestration`, `repo-setup`, and a session-start hook that shows the top of `docs/PROGRESS.md` | every repository |
| `ui` | `frontend-design`, `webapp-testing` | repositories with a user interface |

What the kit adds on top of the skills it bundles:

- **Rules that are always loaded.** `repo-setup` writes an `AGENTS.md` with a short set of team rules: build only what was asked, change only what the task needs, keep changes small, verify before saying done, ask before anything hard to undo.
- **State that survives a cleared session.** The agent keeps `docs/PROGRESS.md` current, and the hook shows its top at the start of every session, including after `/clear`.
- **A delegation policy that keeps token use down.** One task per subagent, a stop condition in every brief, the cheapest model that can carry the work, and command output kept out of the context.
- **A way to measure.** `bin/usage.py` reads your local transcripts and shows where usage went.

## Install

Requirements: Claude Code, git, Python 3.9+. On Windows also Git for Windows, and call the scripts as `py -3 bin\kit.py ...`.

```bash
git clone https://github.com/furkancvk/devkit && cd devkit

bin/kit.py plug ~/code/my-app                          # core + superpowers
bin/kit.py plug ~/code/my-app --packages core,superpowers,ui
bin/kit.py install ~/code/my-app                       # downloads the plugins on this machine
```

`plug` writes two keys into the repository's `.claude/settings.json` (`extraKnownMarketplaces`, `enabledPlugins`) and, if `.gitignore` hides that file, narrows the ignore rule. It never commits. Review the diff and commit it yourself.

Each developer runs `install` once per repository on their own machine, then opens Claude Code in the repository and accepts the folder trust prompt. A committed setting alone does not download a plugin.

Then, once per repository, inside Claude Code:

```
/core:repo-setup
```

This writes `AGENTS.md`, `CLAUDE.md` (the single line `@AGENTS.md`), `docs/PROGRESS.md`, defines the repository's verify command, protects secret files, and offers path-scoped rules for high-risk code. It shows the diff and stops.

Without the script, the same thing by hand:

```bash
cd ~/code/my-app
claude plugin marketplace add furkancvk/devkit --scope project
claude plugin install core@devkit --scope project
claude plugin install superpowers@devkit --scope project
```

## Everyday commands

```bash
bin/kit.py status ~/code/my-app
bin/kit.py unplug ~/code/my-app --packages ui     # one package
bin/kit.py unplug ~/code/my-app                   # the whole kit
bin/usage.py --days 7                             # where did usage go
```

To turn a package off on your own machine only, leave the repository alone and put this in `.claude/settings.local.json`:

```json
{ "enabledPlugins": { "superpowers@devkit": false } }
```

Open Claude Code inside the repository, not in a parent folder: a session started above the repository does not load the kit.

## What runs on your machine

- One hook: at session start, `plugins/core/hooks/progress-context` prints up to 80 lines or 4,000 characters of `docs/PROGRESS.md`. It uses shell builtins only, makes no network call, and prints nothing when the file is absent.
- `bin/kit.py` and `bin/usage.py` run only when you call them. `usage.py` reads `~/.claude/projects` and sends nothing anywhere.
- The `superpowers` package is fetched from its own repository at the commit pinned in `.claude-plugin/marketplace.json`, and brings its own session-start hook. Read it before you trust it; skills are instructions that run with your agent's permissions.

## Platforms

Written for Windows, macOS and Linux. The test suite runs on all three in CI (`.github/workflows/test.yml`), on Python 3.9 and 3.13, and covers `kit.py`, the hook and the manifests. End-to-end sessions with Claude Code have been run on Linux only, and `repo-setup` has been run on one real repository so far (a .NET, React and Expo monolith); reports from Windows, macOS and other stacks are welcome.

On Windows the hook runs through `run-hook.cmd`, which finds the bash that ships with Git for Windows. If no bash is found the hook is skipped silently and the rest of the kit works.

## Maintaining the kit

- Change skills only here. A change reaches developers when you raise `version` in `plugins/<package>/.claude-plugin/plugin.json`; they pull it with `claude plugin marketplace update devkit` and `claude plugin update core@devkit`. Nothing updates on its own.
- Third-party content is pinned; sources, commits and local changes are listed in [THIRD_PARTY.md](THIRD_PARTY.md). When you bump a pin, read the diff first.
- New hooks and scripts follow the same rule as the existing one: no external commands beyond shell builtins, and no `.sh` in the file name.
- Before a release: `python -m unittest discover -s tests`, `claude plugin validate .`, and `claude plugin validate plugins/<package>` for each package. Write the change into [CHANGELOG.md](CHANGELOG.md).
- To rename the kit, change `name` in `.claude-plugin/marketplace.json` and `marketplace` in `kit.json`, then replace the name in the docs. Do this before repositories are plugged in; afterwards every repository's settings file carries the old name.

## Limits

- Claude Code only. Codex and other agents read `AGENTS.md` but not these packages.
- Whether a skill fires is the model's choice. `superpowers` pushes hard on that choice but cannot guarantee it. Anything that must hold belongs in CI.
- The kit does not enforce verification with a hook; the rule lives in `AGENTS.md`.

## Sources and licences

Most of the skills here were written by other people. This kit selects them, pins them, and adds the glue around them.

| What | Author and source | Licence | Changed here |
| --- | --- | --- | --- |
| superpowers (15 skills, session-start hook) | Jesse Vincent, [obra/superpowers](https://github.com/obra/superpowers) | MIT | Not copied; fetched at a pinned commit. `run-hook.cmd` is copied unchanged |
| grill-me, grilling, handoff | Matt Pocock, [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | grill-me calls the plugin-namespaced skill name |
| fable-orchestration | Avenox, [avenoxai/avenoxskills](https://github.com/avenoxai/avenoxskills) | MIT | GPT and Codex routing removed; rules 7 to 9 added |
| frontend-design, webapp-testing | Anthropic, [anthropics/skills](https://github.com/anthropics/skills) | Apache-2.0 | Unchanged |
| Two team rules ("build only what was asked", "change only what the task needs") | Ideas from Andrej Karpathy's notes on LLM coding pitfalls, as collected in [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | n/a | Restated in this kit's own words; no text copied |

Exact commits and the licence texts are in [THIRD_PARTY.md](THIRD_PARTY.md) and [`licenses/`](licenses). Everything else in this repository (`repo-setup`, the progress hook, `bin/`, the tests, the templates) is the kit's own and is MIT ([LICENSE](LICENSE)).

This is an independent project. It is not affiliated with or endorsed by Anthropic or by any of the authors above.
