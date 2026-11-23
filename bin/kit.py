#!/usr/bin/env python3
"""Plug the kit into a repository, unplug it, or show its status.

Touches only the target repository's .claude/settings.json and, when needed,
its .gitignore. Never commits or pushes.

  bin/kit.py plug    <repo> [--packages core,superpowers,ui] [--source github:OWNER/devkit | path:/absolute/path]
  bin/kit.py unplug  <repo> [--packages ui]     # without --packages the whole kit is removed
  bin/kit.py status  <repo>
  bin/kit.py install <repo>                     # downloads the plugins on this machine (once per person)

Runs on Windows, macOS and Linux; needs only Python 3.9+. On Windows: py -3 bin\\kit.py ...
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
CONFIG = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
MARKETPLACE = CONFIG["marketplace"]
KNOWN = [p["name"] for p in json.loads(
    (KIT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))["plugins"]]

GITIGNORE_BLOCK = [
    "# Claude Code: the team settings file is tracked, personal and session files are not",
    "**/.claude/*",
    "!/.claude/settings.json",
    "!/.claude/rules/",
    "!/.claude/skills/",
]
IGNORES_EVERYTHING = {".claude", ".claude/", "/.claude", "/.claude/", "**/.claude", "**/.claude/"}

# Most Windows consoles are not UTF-8; never let output encoding raise.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def fail(message: str) -> "None":
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def tool(name: str) -> str:
    """Full path of an executable. Also finds wrappers such as claude.cmd on Windows."""
    path = shutil.which(name)
    if not path:
        fail(f"'{name}' was not found on PATH")
    return path


def settings_ignored(repo: Path) -> bool:
    return subprocess.run(
        [tool("git"), "-C", str(repo), "check-ignore", "-q", ".claude/settings.json"]).returncode == 0


def repo_path(arg: str) -> Path:
    path = Path(arg).expanduser().resolve()
    if not (path / ".git").exists():
        fail(f"{path} is not a git repository")
    if path == KIT:
        fail("the kit cannot be plugged into itself")
    return path


def read_settings(repo: Path) -> dict:
    file = repo / ".claude" / "settings.json"
    if not file.exists():
        return {}
    try:
        return json.loads(file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{file} is not valid JSON ({e}); fix it by hand first")


def write_settings(repo: Path, data: dict) -> None:
    file = repo / ".claude" / "settings.json"
    if not data:
        if file.exists():
            file.unlink()
        return
    file.parent.mkdir(exist_ok=True)
    # Claude Code writes these two keys last, in this order. Keeping the same
    # order means 'install' produces no diff on a developer's machine.
    for key in ("enabledPlugins", "extraKnownMarketplaces"):
        if key in data:
            data[key] = data.pop(key)
    # LF on every operating system, the same as Claude Code writes.
    with open(file, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def resolve_source(arg: str | None) -> dict:
    if arg is None:
        source = CONFIG["source"]
        if "OWNER" in json.dumps(source):
            fail("the source in kit.json is not filled in yet (OWNER/devkit). "
                 "Put the kit repository's GitHub address in kit.json or pass --source.")
        return source
    kind, _, value = arg.partition(":")
    if kind == "github" and value.count("/") == 1:
        return {"source": "github", "repo": value}
    if kind == "path" and Path(value).is_absolute():
        return {"source": "directory", "path": value}
    fail("--source must be github:OWNER/REPO or path:/absolute/path")


def packages(arg: str | None, default: list[str]) -> list[str]:
    chosen = [p.strip() for p in arg.split(",") if p.strip()] if arg else list(default)
    unknown = [p for p in chosen if p not in KNOWN]
    if unknown:
        fail(f"not in the kit: {', '.join(unknown)} (available: {', '.join(KNOWN)})")
    return chosen


def fix_gitignore(repo: Path) -> str | None:
    """Narrows .gitignore when it hides .claude/settings.json from git."""
    if not settings_ignored(repo):
        return None
    file = repo / ".gitignore"
    raw = ""
    if file.exists():
        with open(file, encoding="utf-8", newline="") as f:
            raw = f.read()
    newline = "\r\n" if "\r\n" in raw else "\n"  # keep the file's own line endings
    lines, changed = [], False
    for line in raw.splitlines():
        if line.strip() in IGNORES_EVERYTHING:
            if not changed:
                # Keep the repository's own comment when the rule already has one.
                has_comment = bool(lines) and lines[-1].lstrip().startswith("#")
                lines.extend(GITIGNORE_BLOCK[1:] if has_comment else GITIGNORE_BLOCK)
                changed = True
            continue
        lines.append(line)
    if not changed:
        return ("WARNING: git ignores .claude/settings.json, but not because of a single "
                "'.claude/' line in the root .gitignore. Check by hand: "
                "git check-ignore -v .claude/settings.json")
    with open(file, "w", encoding="utf-8", newline="") as f:
        f.write(newline.join(lines) + newline)
    if settings_ignored(repo):
        return "WARNING: .gitignore was narrowed but settings.json is still ignored. Check by hand."
    return ".gitignore narrowed: .claude/settings.json can now be committed."


def plug(args) -> None:
    repo = repo_path(args.repo)
    chosen = packages(args.packages, CONFIG["default_packages"])
    data = read_settings(repo)
    data.setdefault("extraKnownMarketplaces", {})[MARKETPLACE] = {"source": resolve_source(args.source)}
    enabled = data.setdefault("enabledPlugins", {})
    for p in chosen:
        enabled[f"{p}@{MARKETPLACE}"] = True
    write_settings(repo, data)
    note = fix_gitignore(repo)
    print(f"Plugged: {', '.join(chosen)} -> {repo}")
    if note:
        print(note)
    print("Next: review the change (git diff) and commit it. Each developer then runs once "
          f"on their own machine: {Path(__file__).name} install {repo}")


def unplug(args) -> None:
    repo = repo_path(args.repo)
    data = read_settings(repo)
    enabled = data.get("enabledPlugins", {})
    ours = [k for k in enabled if k.endswith(f"@{MARKETPLACE}")]
    targets = [f"{p}@{MARKETPLACE}" for p in packages(args.packages, [])] if args.packages else ours
    removed = [k for k in targets if enabled.pop(k, None) is not None]
    left = [k for k in enabled if k.endswith(f"@{MARKETPLACE}")]
    if not left:
        data.get("extraKnownMarketplaces", {}).pop(MARKETPLACE, None)
    for key in ("enabledPlugins", "extraKnownMarketplaces"):
        if key in data and not data[key]:
            del data[key]
    write_settings(repo, data)
    print(f"Unplugged: {', '.join(k.split('@')[0] for k in removed) or 'nothing (it was not plugged)'} -> {repo}")
    if left:
        print(f"Still plugged: {', '.join(k.split('@')[0] for k in left)}")


def status(args) -> None:
    repo = repo_path(args.repo)
    data = read_settings(repo)
    market = data.get("extraKnownMarketplaces", {}).get(MARKETPLACE)
    enabled = {k.split("@")[0]: v for k, v in data.get("enabledPlugins", {}).items()
               if k.endswith(f"@{MARKETPLACE}")}
    print(f"Repository: {repo}")
    print(f"Marketplace: {json.dumps(market['source']) if market else 'not declared'}")
    for p in KNOWN:
        print(f"  {p:<12} {'on' if enabled.get(p) else ('off' if p in enabled else 'not plugged')}")
    for p in sorted(set(enabled) - set(KNOWN)):
        print(f"  {p:<12} plugged, but the kit has no such package (renamed or removed); "
              "run unplug, then plug again")
    for file in ("AGENTS.md", "CLAUDE.md", "docs/PROGRESS.md"):
        print(f"  {file:<18} {'present' if (repo / file).exists() else 'missing'}")
    print(f"  settings.json {'can be committed' if not settings_ignored(repo) else 'CANNOT be committed (.gitignore hides it)'}")


def install(args) -> None:
    repo = repo_path(args.repo)
    data = read_settings(repo)
    enabled = [k for k, v in data.get("enabledPlugins", {}).items() if v and k.endswith(f"@{MARKETPLACE}")]
    if not enabled:
        fail("the kit is not plugged into this repository; run 'plug' first")
    # A committed setting does not register the marketplace on this machine; do that first.
    source = data.get("extraKnownMarketplaces", {}).get(MARKETPLACE, {}).get("source", {})
    address = source.get("repo") or source.get("path") or source.get("url")
    if not address:
        fail(f"settings.json has no source for {MARKETPLACE}; run 'plug' first")
    claude = tool("claude")
    result = subprocess.run([claude, "plugin", "marketplace", "add", address, "--scope", "project"],
                            cwd=repo, capture_output=True, text=True)
    if result.returncode != 0:
        out = (result.stdout + result.stderr).strip().splitlines()
        fail(f"could not register the marketplace ({out[-1] if out else 'no output'}). "
             "Check that you can read the kit repository: gh auth login, gh auth setup-git")
    for plugin_id in enabled:
        if plugin_id.split("@")[0] not in KNOWN:
            print(f"{plugin_id}: SKIPPED (the kit has no such package; it was renamed or removed. "
                  "Run unplug, then plug again.)")
            continue
        result = subprocess.run([claude, "plugin", "install", plugin_id, "--scope", "project"],
                                cwd=repo, capture_output=True, text=True)
        out = (result.stdout + result.stderr).strip().splitlines()
        print(f"{plugin_id}: {'installed' if result.returncode == 0 else 'FAILED'}"
              + (f" ({out[-1]})" if result.returncode != 0 and out else ""))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name, handler in (("plug", plug), ("unplug", unplug), ("status", status), ("install", install)):
        p = sub.add_parser(name)
        p.add_argument("repo")
        if name in ("plug", "unplug"):
            p.add_argument("--packages", help="comma-separated package names")
        if name == "plug":
            p.add_argument("--source", help="github:OWNER/REPO or path:/absolute/path")
        p.set_defaults(handler=handler)
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
