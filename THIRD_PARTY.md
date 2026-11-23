# Third-party content

| Content | Source | Commit | Licence | In this kit |
| --- | --- | --- | --- | --- |
| superpowers | github.com/obra/superpowers (v7.0.2) | 22f0b463e7a5e579904dd6211a520321035526f7 | MIT, `licenses/superpowers.MIT.txt` | The plugin is not copied; `.claude-plugin/marketplace.json` points at this commit. One file is copied unchanged: `hooks/run-hook.cmd` to `plugins/core/hooks/run-hook.cmd` |
| grill-me, grilling, handoff | github.com/mattpocock/skills (`skills/productivity/`) | abeeaf95660ba9e8b7c753eb38f441ca707a8823 | MIT, `licenses/mattpocock-skills.MIT.txt` | `plugins/core/skills/`. Change: grill-me calls `core:grilling`, the plugin-namespaced name |
| fable-orchestration | github.com/avenoxai/avenoxskills (`skills/fable-orchestration/`) | 18e74b8741f851d3362fe00c8f632bec391e947b | MIT, `licenses/avenoxskills.MIT.txt` | `plugins/core/skills/`. Changes: GPT and Codex routing removed (Claude tiers only); hard rules 7 to 9 added (one task per delegate with a ceiling, a stop condition in every brief, output kept out of the context) |
| frontend-design, webapp-testing | github.com/anthropics/skills (`skills/`) | e4bb5d960d87126ff3b3a8af1a104b7db67560ba | Apache-2.0, `LICENSE.txt` in each skill folder | `plugins/ui/skills/`, unchanged |

Two team rules in the `AGENTS.md` template ("build only what was asked", "change only what the task needs") restate, in this kit's own words, ideas from Andrej Karpathy's notes on LLM coding pitfalls as collected in github.com/multica-ai/andrej-karpathy-skills. No text is copied from that repository.

The `repo-setup` skill, the progress hook, `bin/kit.py`, `bin/usage.py` and the tests were written for this kit.
