#!/usr/bin/env python3
"""Regression tests for the repository's dependency-free skill validator."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_PATH = PROJECT_ROOT / "scripts" / "validate_skill.py"
SKILL_RELATIVE_DIRECTORY = Path("skills") / "adapt-ui-for-iphone-duo"

sys.dont_write_bytecode = True
module_spec = importlib.util.spec_from_file_location("skill_validator", VALIDATOR_PATH)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError(f"could not load validator: {VALIDATOR_PATH}")
validator = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(validator)


class SkillValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(
            prefix="duo-skill-validator-tests."
        )
        self.skill_root = Path(self.temporary_directory.name) / "skill"
        shutil.copytree(
            PROJECT_ROOT,
            self.skill_root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_current_repository_is_valid(self) -> None:
        validator.validate(self.skill_root)

    def test_invocation_name_cannot_change(self) -> None:
        skill_path = self.skill_root / SKILL_RELATIVE_DIRECTORY / "SKILL.md"
        skill_text = skill_path.read_text(encoding="utf-8")
        skill_path.write_text(
            skill_text.replace(
                "name: adapt-ui-for-iphone-duo",
                "name: renamed-duo-skill",
                1,
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(validator.ValidationError, "preserve invocation"):
            validator.validate(self.skill_root)

    def test_broken_markdown_link_is_rejected(self) -> None:
        readme_path = self.skill_root / "README.md"
        readme_path.write_text(
            readme_path.read_text(encoding="utf-8") + "\n[Missing](missing.md)\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(validator.ValidationError, "does not exist"):
            validator.validate(self.skill_root)

    def test_invalid_eval_json_is_rejected(self) -> None:
        trigger_path = self.skill_root / "evals" / "trigger-cases.json"
        trigger_path.write_text("{\n", encoding="utf-8")

        with self.assertRaisesRegex(validator.ValidationError, "invalid JSON"):
            validator.validate(self.skill_root)

    def test_eval_artifact_cannot_escape_repository(self) -> None:
        cases_path = self.skill_root / "evals" / "task-cases.json"
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
        cases["cases"][0]["artifact"] = "../../outside"
        cases_path.write_text(
            json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(validator.ValidationError, "escapes the skill root"):
            validator.validate(self.skill_root)

    def test_default_prompt_must_keep_dollar_invocation(self) -> None:
        metadata_path = (
            self.skill_root / SKILL_RELATIVE_DIRECTORY / "agents" / "openai.yaml"
        )
        metadata_text = metadata_path.read_text(encoding="utf-8")
        metadata_path.write_text(
            metadata_text.replace(
                "$adapt-ui-for-iphone-duo",
                "adapt-ui-for-iphone-duo",
                1,
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(validator.ValidationError, "default_prompt"):
            validator.validate(self.skill_root)

    def test_localized_readme_drift_is_rejected(self) -> None:
        readme_path = self.skill_root / "README.zh-CN.md"
        readme_text = readme_path.read_text(encoding="utf-8")
        readme_path.write_text(
            readme_text.replace("1878 × 2670 px", "1878 × 2671 px", 1),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(validator.ValidationError, "synchronized content"):
            validator.validate(self.skill_root)

    def test_display_pixel_axes_are_orientation_independent(self) -> None:
        profile_path = (
            self.skill_root
            / SKILL_RELATIVE_DIRECTORY
            / "references"
            / "device-profile.json"
        )
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        profile["displays"]["inner"]["pixels"] = {
            "width": 1878,
            "height": 2670,
        }
        profile_path.write_text(
            json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(validator.ValidationError, "short_edge and long_edge"):
            validator.validate(self.skill_root)

    def test_standard_skill_directory_is_required(self) -> None:
        skill_directory = self.skill_root / SKILL_RELATIVE_DIRECTORY
        renamed_directory = skill_directory.with_name("duo-ui-fit")
        skill_directory.rename(renamed_directory)

        with self.assertRaisesRegex(validator.ValidationError, "GitHub skill discovery"):
            validator.validate(self.skill_root)

    def test_discovery_terms_cannot_drift(self) -> None:
        skill_path = self.skill_root / SKILL_RELATIVE_DIRECTORY / "SKILL.md"
        skill_text = skill_path.read_text(encoding="utf-8")
        skill_path.write_text(
            skill_text.replace("foldable iPhone", "dual-screen handset", 1),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(validator.ValidationError, "discovery term"):
            validator.validate(self.skill_root)

    def test_task_mode_must_match_skill_contract(self) -> None:
        cases_path = self.skill_root / "evals" / "task-cases.json"
        cases = json.loads(cases_path.read_text(encoding="utf-8"))
        cases["cases"][0]["mode"] = "review"
        cases_path.write_text(
            json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(validator.ValidationError, "mode must be one of"):
            validator.validate(self.skill_root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
