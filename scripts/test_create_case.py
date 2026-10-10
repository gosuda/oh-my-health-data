#!/usr/bin/env python3
"""Behavior checks for the portable, network-free draft generator."""

from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/mma-health-data/scripts/create_case.py"
ROUTES = ("disclosure", "access", "inquiry", "deletion", "stop")


def fixture() -> dict:
    return {
        "version": 1,
        "source_baseline": "2026-10-09",
        "templates": [{
            "id": route,
            "label": f"경로 {route}",
            "portal_url": "https://example.invalid/portal",
            "recipient": "테스트 기관",
            "title": f"{route} 요청",
            "opening": "다음 사항을 요청합니다.",
            "questions": [
                {"id": "first", "text": "첫 번째 질문 본문입니다."},
                {"id": "second", "text": "두 번째 질문 본문입니다."},
                {"id": "third", "text": "세 번째 질문 본문입니다."},
            ],
            "closing": "답변을 요청합니다.",
        } for route in ROUTES],
    }


class CreateCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="mma-case-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "installed-skill"
        (self.skill / "scripts").mkdir(parents=True)
        (self.skill / "assets").mkdir()
        self.script = self.skill / "scripts/create_case.py"
        shutil.copyfile(SCRIPT, self.script)
        (self.skill / "assets/templates.json").write_text(
            json.dumps(fixture(), ensure_ascii=False), encoding="utf-8"
        )
        self.cwd = self.root / "unrelated-cwd"
        self.cwd.mkdir()

    def run_cli(self, *args: str, script: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script or self.script), *map(str, args)],
            cwd=self.cwd, capture_output=True, text=True, check=False,
        )

    def assert_rejected(self, output: Path, *args: str) -> None:
        result = self.run_cli("--template", "disclosure", "--output-dir", str(output), *args)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, "")
        self.assertFalse(output.exists())

    def test_selected_questions_and_private_metadata(self) -> None:
        output = self.root / "new-private-parent" / "case"
        result = self.run_cli(
            "--template", "access", "--output-dir", output,
            "--recipient", "개인 수신 기관", "--scope", "개인 범위 123",
            "--question", "third", "--question", "first", "--question", "third",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        case = json.loads((output / "case.json").read_text(encoding="utf-8"))
        draft = (output / "draft.md").read_text(encoding="utf-8")
        self.assertEqual([item["id"] for item in case["questions"]], ["first", "third"])
        self.assertIn("1. [first]", draft)
        self.assertIn("2. [third]", draft)
        self.assertNotIn("두 번째 질문", draft)
        self.assertIn(case["recipient"], draft)
        self.assertIn(case["scope"], draft)
        self.assertNotIn(case["scope"], result.stdout)
        self.assertNotIn(case["recipient"], result.stdout)
        self.assertEqual(case["status"], "draft")
        self.assertFalse(case["evidence_checked"])
        self.assertIsNone(case["submitted_at"])
        self.assertIsNone(case["receipt"])
        self.assertEqual(case["source_baseline"], "2026-10-09")
        self.assertIsNotNone(datetime.fromisoformat(case["created_at"].replace("Z", "+00:00")).tzinfo)
        if os.name == "posix":
            for path in (output, output.parent):
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o700)
            for path in output.iterdir():
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_each_template_and_defaults(self) -> None:
        for route in ROUTES:
            with self.subTest(route=route):
                output = self.root / f"case-{route}"
                extra = ("--scope", "선택한 자료에 한정") if route in {"deletion", "stop"} else ()
                result = self.run_cli("--template", route, "--output-dir", output, *extra)
                self.assertEqual(result.returncode, 0, result.stderr)
                case = json.loads((output / "case.json").read_text(encoding="utf-8"))
                self.assertEqual(case["template_id"], route)
                self.assertEqual(case["route"], f"경로 {route}")
                self.assertEqual(len(case["questions"]), 3)
                self.assertEqual(case["scope"], "선택한 자료에 한정" if extra else "")

    def test_deletion_and_stop_require_scope_before_writing(self) -> None:
        for route in ("deletion", "stop"):
            for extra in ((), ("--scope", "   ")):
                with self.subTest(route=route, extra=extra):
                    output = self.root / "must-not-create-parent" / route
                    result = self.run_cli("--template", route, "--output-dir", output, *extra)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(result.stdout, "")
                    self.assertFalse(output.parent.exists())

    def test_list_exposes_only_ids_and_labels(self) -> None:
        result = self.run_cli("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(result.stdout.splitlines()), len(ROUTES))
        self.assertIn("first, second, third", result.stdout)
        for private_or_body in ("요청합니다", "본문", "https://", "테스트 기관"):
            self.assertNotIn(private_or_body, result.stdout)
        self.assertNotEqual(self.run_cli("--list", "--scope", "secret").returncode, 0)

    def test_invalid_ids_fail_before_creating_any_directories(self) -> None:
        for option in (("--question", "missing"), ("--template", "missing")):
            output = self.root / "missing-parent" / "case"
            self.assert_rejected(output, *option)
            self.assertFalse(output.parent.exists())

    def test_existing_directory_or_file_is_preserved(self) -> None:
        output = self.root / "existing-case"
        output.mkdir()
        marker = output / "draft.md"
        marker.write_text("do not alter", encoding="utf-8")
        result = self.run_cli("--template", "disclosure", "--output-dir", output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(encoding="utf-8"), "do not alter")
        self.assertEqual(list(output.iterdir()), [marker])
        result = self.run_cli("--template", "access", "--output-dir", marker)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(marker.read_text(encoding="utf-8"), "do not alter")

    def test_relative_output_is_rejected(self) -> None:
        self.assert_rejected(Path("relative-case"))
        self.assertFalse((self.cwd / "relative-case").exists())

    def test_git_directory_and_worktree_file_destinations_are_rejected(self) -> None:
        for marker_kind in ("directory", "file"):
            with self.subTest(marker_kind=marker_kind):
                repo = self.root / f"repo-{marker_kind}"
                repo.mkdir()
                marker = repo / ".git"
                if marker_kind == "directory":
                    marker.mkdir()
                    (marker / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
                else:
                    marker.write_text("gitdir: /unread/location", encoding="utf-8")
                self.assert_rejected(repo / "nested" / "case")
                self.assertFalse((repo / "nested").exists())

    def test_empty_sandbox_git_placeholder_is_not_a_checkout(self) -> None:
        parent = self.root / "sandbox-placeholder"
        parent.mkdir()
        (parent / ".git").mkdir()
        output = parent / "private-case"
        result = self.run_cli("--template", "disclosure", "--output-dir", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((output / "case.json").is_file())
        self.assertEqual(list((parent / ".git").iterdir()), [])

    def test_skill_package_destination_is_rejected(self) -> None:
        self.assert_rejected(self.skill / "private-case")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unavailable")
    def test_symlink_into_git_or_package_is_rejected(self) -> None:
        repo = self.root / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        (repo / ".git/HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        for target, name in ((repo, "linked-repo"), (self.skill, "linked-skill")):
            link = self.root / name
            link.symlink_to(target, target_is_directory=True)
            self.assert_rejected(link / "case")
            self.assertFalse((target / "case").exists())
        dangling = self.root / "dangling-case"
        target = self.root / "must-not-be-created"
        dangling.symlink_to(target, target_is_directory=True)
        result = self.run_cli("--template", "access", "--output-dir", dangling)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(dangling.is_symlink())
        self.assertFalse(target.exists())

    def test_package_is_relocatable(self) -> None:
        moved = self.root / "moved" / "package"
        moved.parent.mkdir()
        self.skill.rename(moved)
        output = self.root / "relocated-case"
        result = self.run_cli(
            "--template", "inquiry", "--output-dir", output,
            script=moved / "scripts/create_case.py",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((output / "draft.md").is_file())

    def test_invalid_template_schema_fails_without_output(self) -> None:
        bad = fixture()
        bad["templates"][0]["questions"][1]["id"] = "first"
        (self.skill / "assets/templates.json").write_text(json.dumps(bad), encoding="utf-8")
        self.assert_rejected(self.root / "invalid-schema-case")

    def test_no_submission_or_network_cli(self) -> None:
        output = self.root / "not-submitted"
        self.assert_rejected(output, "--submit")


if __name__ == "__main__":
    unittest.main()
