"""Tests for bin/kit.py, the session-start hook and the kit's manifests.

Standard library only, so the same file runs on Windows, macOS and Linux:
    python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
KIT_PY = KIT / "bin" / "kit.py"
HOOKS = KIT / "plugins" / "core" / "hooks"
MARKET = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))["marketplace"]


def run_kit(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(KIT_PY), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def run_hook(project_dir: Path) -> subprocess.CompletedProcess:
    wrapper = str(HOOKS / "run-hook.cmd")
    command = ["cmd", "/c", wrapper, "progress-context"] if os.name == "nt" else ["sh", wrapper, "progress-context"]
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project_dir))
    return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)


class RepoCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name).resolve() / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.source = f"path:{KIT}"

    def settings(self) -> dict:
        return json.loads((self.repo / ".claude" / "settings.json").read_text(encoding="utf-8"))

    def ignored(self, path: str) -> bool:
        return subprocess.run(["git", "-C", str(self.repo), "check-ignore", "-q", path]).returncode == 0


class PlugTests(RepoCase):
    def test_plug_writes_marketplace_and_default_packages(self) -> None:
        result = run_kit("plug", str(self.repo), "--source", self.source)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = self.settings()
        self.assertEqual(data["extraKnownMarketplaces"][MARKET]["source"],
                         {"source": "directory", "path": str(KIT)})
        self.assertEqual(data["enabledPlugins"], {f"core@{MARKET}": True, f"superpowers@{MARKET}": True})

    def test_placeholder_source_is_refused(self) -> None:
        config = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
        if "OWNER" not in json.dumps(config["source"]):
            self.skipTest("kit.json already has a real source")
        result = run_kit("plug", str(self.repo))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.repo / ".claude").exists())

    def test_unknown_package_is_refused(self) -> None:
        result = run_kit("plug", str(self.repo), "--packages", "nope", "--source", self.source)
        self.assertNotEqual(result.returncode, 0)

    def test_settings_file_uses_lf_and_cli_key_order(self) -> None:
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude" / "settings.json").write_text('{"permissions": {"allow": ["Bash(ls:*)"]}}',
                                                              encoding="utf-8")
        run_kit("plug", str(self.repo), "--source", self.source)
        raw = (self.repo / ".claude" / "settings.json").read_bytes()
        self.assertNotIn(b"\r\n", raw)
        self.assertEqual(list(self.settings()), ["permissions", "enabledPlugins", "extraKnownMarketplaces"])

    def test_unplug_one_package_then_all_keeps_other_settings(self) -> None:
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude" / "settings.json").write_text('{"permissions": {"allow": ["Bash(ls:*)"]}}',
                                                              encoding="utf-8")
        run_kit("plug", str(self.repo), "--packages", "core,ui", "--source", self.source)
        run_kit("unplug", str(self.repo), "--packages", "ui")
        self.assertEqual(self.settings()["enabledPlugins"], {f"core@{MARKET}": True})
        run_kit("unplug", str(self.repo))
        self.assertEqual(self.settings(), {"permissions": {"allow": ["Bash(ls:*)"]}})

    def test_unplug_removes_file_that_only_held_the_kit(self) -> None:
        run_kit("plug", str(self.repo), "--source", self.source)
        run_kit("unplug", str(self.repo))
        self.assertFalse((self.repo / ".claude" / "settings.json").exists())

    def test_status_reports_package_the_kit_does_not_have(self) -> None:
        (self.repo / ".claude").mkdir()
        (self.repo / ".claude" / "settings.json").write_text(
            json.dumps({"enabledPlugins": {f"gone@{MARKET}": True}}), encoding="utf-8")
        result = run_kit("status", str(self.repo))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("gone", result.stdout)
        self.assertIn("no such package", result.stdout)


class GitignoreTests(RepoCase):
    def test_blanket_ignore_is_narrowed(self) -> None:
        (self.repo / ".gitignore").write_text("node_modules/\n.claude/\n", encoding="utf-8")
        run_kit("plug", str(self.repo), "--source", self.source)
        self.assertFalse(self.ignored(".claude/settings.json"))
        self.assertTrue(self.ignored(".claude/settings.local.json"))
        self.assertTrue(self.ignored("apps/mobile/.claude/settings.local.json"))
        self.assertIn("node_modules/", (self.repo / ".gitignore").read_text(encoding="utf-8"))

    def test_crlf_line_endings_are_kept(self) -> None:
        (self.repo / ".gitignore").write_bytes(b"dist/\r\n.claude/\r\n")
        run_kit("plug", str(self.repo), "--source", self.source)
        raw = (self.repo / ".gitignore").read_bytes()
        self.assertIn(b"\r\n", raw)
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))

    def test_gitignore_untouched_when_settings_not_ignored(self) -> None:
        (self.repo / ".gitignore").write_text("dist/\n", encoding="utf-8")
        run_kit("plug", str(self.repo), "--source", self.source)
        self.assertEqual((self.repo / ".gitignore").read_text(encoding="utf-8"), "dist/\n")


class HookTests(RepoCase):
    def test_prints_top_of_progress_file(self) -> None:
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "PROGRESS.md").write_text("# Progress\n\n## Now\n\n- marker ZEBRA-4417\n",
                                                         encoding="utf-8")
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("docs/PROGRESS.md", result.stdout)
        self.assertIn("ZEBRA-4417", result.stdout)

    def test_silent_when_file_is_missing(self) -> None:
        result = run_hook(self.repo)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

    def test_long_file_is_capped(self) -> None:
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "PROGRESS.md").write_text("".join(f"line {i}\n" for i in range(500)),
                                                         encoding="utf-8")
        result = run_hook(self.repo)
        self.assertIn("line 79", result.stdout)
        self.assertNotIn("line 80\n", result.stdout)
        self.assertLess(len(result.stdout), 5000)


class ManifestTests(unittest.TestCase):
    def test_marketplace_packages_exist_and_defaults_are_known(self) -> None:
        market = json.loads((KIT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        names = [p["name"] for p in market["plugins"]]
        self.assertEqual(market["name"], MARKET)
        for plugin in market["plugins"]:
            if isinstance(plugin["source"], str):
                folder = KIT / plugin["source"]
                manifest = json.loads((folder / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["name"], plugin["name"])
            else:
                self.assertRegex(plugin["source"].get("sha", ""), r"^[0-9a-f]{40}$",
                                 f"{plugin['name']} must be pinned to a full commit")
        defaults = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))["default_packages"]
        self.assertTrue(set(defaults) <= set(names))

    def test_every_skill_has_matching_name_and_short_description(self) -> None:
        skills = sorted(KIT.glob("plugins/*/skills/*/SKILL.md"))
        self.assertTrue(skills)
        for skill in skills:
            text = skill.read_text(encoding="utf-8")
            self.assertTrue(text.startswith("---"), skill)
            front = text.split("---", 2)[1]
            fields = {}
            for line in front.splitlines():
                if ":" in line and not line.startswith(" "):
                    key, _, value = line.partition(":")
                    fields[key.strip()] = value.strip().strip('"')
            self.assertEqual(fields.get("name"), skill.parent.name, skill)
            self.assertIn("description", fields, skill)
            self.assertLessEqual(len(fields["description"]), 1536, skill)

    def test_hook_script_has_no_extension_and_hooks_json_is_valid(self) -> None:
        hooks = json.loads((HOOKS / "hooks.json").read_text(encoding="utf-8"))
        command = hooks["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        self.assertIn("run-hook.cmd", command)
        self.assertNotIn(".sh", command)
        self.assertTrue((HOOKS / "progress-context").is_file())


if __name__ == "__main__":
    unittest.main()
