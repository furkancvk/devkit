# Contributing

Changes reach `main` only through a pull request with green CI and one approving review. Direct pushes are blocked for everyone, including maintainers.

1. Fork or branch, and keep the change to one concern.
2. Run the tests: `python -m unittest discover -s tests -v`. They use the standard library only and must pass on Windows, macOS and Linux; CI runs all three.
3. If you touched a plugin, run `claude plugin validate .` and `claude plugin validate plugins/<package>`.
4. If the change should reach users, raise `version` in that package's `.claude-plugin/plugin.json` and add a line to `CHANGELOG.md`.
5. Open the pull request and say what you changed and how you checked it.

## What fits

- A rule or skill earns its place by fixing something that actually went wrong. Say what went wrong.
- Every skill and every line of always-loaded text costs context in every session. Prefer changing an existing rule to adding one.
- Hooks and scripts use shell builtins or the Python standard library only, run on all three operating systems, and make no network calls.

## Third-party content

Do not edit bundled third-party skills in place without recording it. If you change one, add the change to `THIRD_PARTY.md`. To update a pinned source, read its diff first, then change the commit there and in `.claude-plugin/marketplace.json`. New third-party content needs a licence that allows redistribution, its licence text under `licenses/` or in its folder, and a row in `THIRD_PARTY.md`.
