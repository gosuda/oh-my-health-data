#!/usr/bin/env python3
"""Check the public archive contract and the extracted skill's portability."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills/mma-health-data"
PACKAGER = ROOT / "scripts/package_skill.mjs"
FILES = (
    "SKILL.md", "agents/openai.yaml", "assets/templates.json",
    "references/evidence.md", "references/portals.md", "references/replies.md",
    "scripts/create_case.py",
)


class PackageSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="mma-public-bundle-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        shutil.copytree(SOURCE, self.source)

    def package(self, output: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", str(PACKAGER), "--source-root", str(self.source), "--output", str(output)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )

    def test_exact_members_crc_content_and_no_private_extras(self) -> None:
        sentinel = "PRIVATE_SENTINEL_NEVER_BUNDLE_0927"
        for relative in ("case.json", "draft.md", "private/receipt.txt", "__pycache__/secret.pyc"):
            extra = self.source / relative
            extra.parent.mkdir(parents=True, exist_ok=True)
            extra.write_text(sentinel, encoding="utf-8")
        output = self.root / "download.zip"
        result = self.package(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(sentinel.encode(), output.read_bytes())
        with zipfile.ZipFile(output) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.namelist(), [f"mma-health-data/{name}" for name in FILES])
            for relative in FILES:
                name = f"mma-health-data/{relative}"
                info = archive.getinfo(name)
                expected = (self.source / relative).read_bytes()
                self.assertEqual(archive.read(name), expected)
                self.assertEqual(info.CRC, zlib.crc32(expected))
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(info.external_attr >> 16, 0o100644)
        for extra in self.source.glob("private/*"):
            self.assertEqual(extra.read_text(encoding="utf-8"), sentinel)

    def test_deterministic_bytes(self) -> None:
        first, second = self.root / "first.zip", self.root / "second.zip"
        self.assertEqual(self.package(first).returncode, 0)
        for relative in FILES:
            (self.source / relative).touch()
        self.assertEqual(self.package(second).returncode, 0)
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_extracted_cli_lists_templates_from_unrelated_cwd(self) -> None:
        output = self.root / "download.zip"
        self.assertEqual(self.package(output).returncode, 0)
        destination = self.root / "extracted"
        with zipfile.ZipFile(output) as archive:
            archive.extractall(destination)
        script = destination / "mma-health-data/scripts/create_case.py"
        result = subprocess.run(
            [sys.executable, str(script), "--list"], cwd=self.root,
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((self.source / "assets/templates.json").read_text(encoding="utf-8"))
        self.assertEqual(len(result.stdout.splitlines()), len(data["templates"]))
        for template in data["templates"]:
            self.assertIn(f"{template['id']}\t{template['label']}\t", result.stdout)

    def test_missing_public_file_preserves_existing_archive(self) -> None:
        output = self.root / "download.zip"
        self.assertEqual(self.package(output).returncode, 0)
        previous = output.read_bytes()
        (self.source / "references/evidence.md").unlink()
        result = self.package(output)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(output.read_bytes(), previous)

    def test_public_symlink_is_rejected(self) -> None:
        public_file = self.source / "references/evidence.md"
        public_file.unlink()
        outside = self.root / "private-outside.txt"
        outside.write_text("PRIVATE_SENTINEL", encoding="utf-8")
        public_file.symlink_to(outside)
        output = self.root / "download.zip"
        self.assertNotEqual(self.package(output).returncode, 0)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
