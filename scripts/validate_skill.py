#!/usr/bin/env python3
"""Validate this portable skill without third-party Python packages."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple
from urllib.parse import unquote, urlparse


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
EXPECTED_SKILL_NAME = "adapt-ui-for-iphone-duo"
SKILL_RELATIVE_DIRECTORY = Path("skills") / EXPECTED_SKILL_NAME
TASK_MODES = {"audit", "design", "implementation", "verification"}
REQUIRED_DISCOVERY_TERMS = (
    "iPhone Duo",
    "foldable iPhone",
    "SwiftUI",
    "UIKit",
    "adaptive UI",
)
README_NAVIGATION = {
    "README.md": (
        "English | [简体中文](README.zh-CN.md) | "
        "[繁體中文](README.zh-TW.md) | [日本語](README.ja.md)"
    ),
    "README.zh-CN.md": (
        "[English](README.md) | 简体中文 | "
        "[繁體中文](README.zh-TW.md) | [日本語](README.ja.md)"
    ),
    "README.zh-TW.md": (
        "[English](README.md) | [简体中文](README.zh-CN.md) | "
        "繁體中文 | [日本語](README.ja.md)"
    ),
    "README.ja.md": (
        "[English](README.md) | [简体中文](README.zh-CN.md) | "
        "[繁體中文](README.zh-TW.md) | 日本語"
    ),
}


class ValidationError(Exception):
    pass


def parse_frontmatter(skill_path: Path) -> Tuple[Dict[str, str], str]:
    try:
        text = skill_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"cannot read {skill_path}: {exc}") from exc

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValidationError("SKILL.md must begin with YAML frontmatter")

    try:
        closing_index = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as exc:
        raise ValidationError("SKILL.md frontmatter is not closed with ---") from exc

    metadata: Dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing_index], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace() or ":" not in line:
            raise ValidationError(
                f"SKILL.md:{line_number}: expected a top-level scalar key"
            )
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key or not value:
            raise ValidationError(
                f"SKILL.md:{line_number}: frontmatter key and value cannot be empty"
            )
        if key in metadata:
            raise ValidationError(f"SKILL.md:{line_number}: duplicate key '{key}'")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        metadata[key] = value

    body = "\n".join(lines[closing_index + 1 :]).strip()
    return metadata, body


def validate_frontmatter(metadata: Dict[str, str], body: str) -> None:
    allowed_keys = {"name", "description"}
    missing = allowed_keys - metadata.keys()
    extra = metadata.keys() - allowed_keys
    if missing:
        raise ValidationError(
            "SKILL.md frontmatter is missing: " + ", ".join(sorted(missing))
        )
    if extra:
        raise ValidationError(
            "SKILL.md frontmatter contains unsupported keys: "
            + ", ".join(sorted(extra))
        )

    name = metadata["name"]
    if len(name) > 64 or not NAME_RE.fullmatch(name):
        raise ValidationError(
            "skill name must be at most 64 characters of lowercase letters, digits, and hyphens"
        )
    if name != EXPECTED_SKILL_NAME:
        raise ValidationError(
            f"skill name must remain '{EXPECTED_SKILL_NAME}' to preserve invocation compatibility"
        )

    description = metadata["description"]
    if len(description) > 1024:
        raise ValidationError("skill description must be at most 1024 characters")
    if len(description) > 800:
        raise ValidationError(
            "skill description must stay at or below 800 characters for concise discovery metadata"
        )
    for term in REQUIRED_DISCOVERY_TERMS:
        if term not in description:
            raise ValidationError(
                f"skill description must retain the discovery term '{term}'"
            )
    if not body:
        raise ValidationError("SKILL.md must contain an instruction body")


def validate_local_links(root: Path, markdown_path: Path) -> None:
    text = markdown_path.read_text(encoding="utf-8")
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        relative_target = unquote(target.split("#", 1)[0])
        candidate = (markdown_path.parent / relative_target).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError as exc:
            raise ValidationError(
                f"{markdown_path.relative_to(root)} link escapes the skill root: {raw_target}"
            ) from exc
        if not candidate.exists():
            raise ValidationError(
                f"{markdown_path.relative_to(root)} link does not exist: {raw_target}"
            )


def load_json(json_path: Path, root: Path) -> Any:
    try:
        with json_path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(
            f"invalid JSON in {json_path.relative_to(root)}: {exc}"
        ) from exc


def validate_json_files(root: Path, skill_root: Path) -> None:
    json_paths: Iterable[Path] = (
        path
        for directory in (skill_root / "references", root / "evals")
        if directory.is_dir()
        for path in directory.rglob("*.json")
    )
    for json_path in sorted(json_paths):
        load_json(json_path, root)


def require_mapping(value: Any, context: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{context} must be an object")
    return value


def require_positive_number(value: Any, context: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValidationError(f"{context} must be a positive number")


def require_iso_date(value: Any, context: str) -> None:
    raw_date = require_nonempty_string(value, context)
    try:
        date.fromisoformat(raw_date)
    except ValueError as exc:
        raise ValidationError(f"{context} must use YYYY-MM-DD format") from exc


def validate_device_profile(root: Path, skill_root: Path) -> None:
    profile_path = skill_root / "references" / "device-profile.json"
    if not profile_path.is_file():
        raise ValidationError(
            f"{profile_path.relative_to(root)} is required"
        )

    profile = require_mapping(
        load_json(profile_path, root), str(profile_path.relative_to(root))
    )
    if profile.get("schema_version") != 2:
        raise ValidationError("device profile schema_version must be 2")
    if profile.get("official_name") != "iPhone Duo":
        raise ValidationError("device profile official_name must be 'iPhone Duo'")
    if "runtime layout breakpoints" not in require_nonempty_string(
        profile.get("profile_purpose"), "profile_purpose"
    ):
        raise ValidationError(
            "device profile profile_purpose must prohibit runtime layout breakpoints"
        )
    require_iso_date(profile.get("profile_reviewed_on"), "profile_reviewed_on")
    require_iso_date(profile.get("announcement_date"), "announcement_date")
    require_iso_date(profile.get("availability_date"), "availability_date")

    displays = require_mapping(profile.get("displays"), "displays")
    for display_name in ("inner", "outer"):
        display = require_mapping(displays.get(display_name), f"displays.{display_name}")
        pixels = require_mapping(
            display.get("pixels"), f"displays.{display_name}.pixels"
        )
        if set(pixels) != {"short_edge", "long_edge"}:
            raise ValidationError(
                f"displays.{display_name}.pixels must use short_edge and long_edge"
            )
        require_positive_number(
            pixels.get("short_edge"), f"displays.{display_name}.pixels.short_edge"
        )
        require_positive_number(
            pixels.get("long_edge"), f"displays.{display_name}.pixels.long_edge"
        )
        if pixels["short_edge"] >= pixels["long_edge"]:
            raise ValidationError(
                f"displays.{display_name}.pixels short_edge must be less than long_edge"
            )
        for field in (
            "diagonal_inches",
            "ppi",
            "max_refresh_hz",
            "peak_outdoor_nits",
        ):
            require_positive_number(
                display.get(field), f"displays.{display_name}.{field}"
            )

    runtime_policy = require_mapping(profile.get("runtime_policy"), "runtime_policy")
    expected_runtime_policy = {
        "pixel_values_are_layout_breakpoints": False,
        "physical_dimensions_are_layout_breakpoints": False,
        "model_name_detection_allowed": False,
        "use_size_classes_safe_areas_and_reserved_regions": True,
    }
    for key, expected in expected_runtime_policy.items():
        if runtime_policy.get(key) is not expected:
            raise ValidationError(f"runtime_policy.{key} must be {expected}")

    source_map = require_mapping(profile.get("source_map"), "source_map")
    sources = profile.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ValidationError("device profile sources must be a non-empty list")
    source_set = set(sources)
    for source in sources:
        parsed = urlparse(require_nonempty_string(source, "device profile source"))
        if parsed.scheme != "https" or not (
            parsed.hostname == "apple.com"
            or (parsed.hostname or "").endswith(".apple.com")
        ):
            raise ValidationError(
                f"device profile source must be a primary Apple HTTPS URL: {source}"
            )
    for pointer, mapped_sources in source_map.items():
        require_nonempty_string(pointer, "device profile source_map key")
        if not isinstance(mapped_sources, list):
            raise ValidationError(f"source_map.{pointer} must be a list")
        for source in mapped_sources:
            if source not in source_set:
                raise ValidationError(
                    f"source_map.{pointer} contains a URL absent from sources: {source}"
                )


def validate_readme_translations(root: Path) -> None:
    shared_fragments = (
        "$adapt-ui-for-iphone-duo",
        "Agent Skill",
        "Codex",
        "SwiftUI",
        "UIKit",
        "2026-09-11",
        "1878 × 2670 px",
        "1398 × 2034 px",
        "7.6",
        "5.4",
        "430 ppi",
        "460 ppi",
        "164.6 × 117.8 × 5.2 mm",
        "84.1 × 117.8 × 11.3 mm",
        "254 g",
        "README.md / README.*.md",
        "skills/adapt-ui-for-iphone-duo/SKILL.md",
        'gh skill search "iphone duo"',
        "gh skill install NanWuIT/adapt-ui-for-iphone-duo adapt-ui-for-iphone-duo --agent codex --scope user",
        "gh skill install . adapt-ui-for-iphone-duo --from-local --agent codex --scope user",
        "gh skill publish --dry-run",
        'ln -s "$PWD/skills/adapt-ui-for-iphone-duo" ~/.agents/skills/adapt-ui-for-iphone-duo',
        "bash skills/adapt-ui-for-iphone-duo/scripts/audit-duo-layout.sh -- /path/to/ios-project",
        "bash scripts/validate.sh",
        "https://www.apple.com/iphone-duo/specs/",
    )

    for filename, expected_navigation in README_NAVIGATION.items():
        readme_path = root / filename
        if not readme_path.is_file():
            raise ValidationError(f"{filename} is required")
        try:
            readme_text = readme_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValidationError(f"cannot read {filename}: {exc}") from exc

        first_line = readme_text.splitlines()[0] if readme_text else ""
        if first_line != expected_navigation:
            raise ValidationError(
                f"{filename} must begin with the synchronized language navigation"
            )
        for fragment in shared_fragments:
            if fragment not in readme_text:
                raise ValidationError(
                    f"{filename} is missing synchronized content: {fragment}"
                )


def require_nonempty_string(value: Any, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{context} must be a non-empty string")
    return value


def validate_evals(root: Path, skill_name: str) -> None:
    evals_dir = root / "evals"
    if not evals_dir.is_dir():
        raise ValidationError("evals directory is required")

    for filename, eval_kind in (
        ("trigger-cases.json", "trigger"),
        ("task-cases.json", "task"),
    ):
        eval_path = evals_dir / filename
        if not eval_path.is_file():
            raise ValidationError(f"evals/{filename} is required")
        payload = load_json(eval_path, root)
        if not isinstance(payload, dict):
            raise ValidationError(f"evals/{filename} must contain an object")
        if payload.get("schema_version") != 1:
            raise ValidationError(f"evals/{filename} schema_version must be 1")
        if payload.get("skill") != skill_name:
            raise ValidationError(
                f"evals/{filename} skill must match SKILL.md name '{skill_name}'"
            )

        cases = payload.get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValidationError(f"evals/{filename} cases must be a non-empty list")

        seen_ids = set()
        seen_prompts = set()
        trigger_outcomes = set()
        for index, case in enumerate(cases):
            context = f"evals/{filename} case {index + 1}"
            if not isinstance(case, dict):
                raise ValidationError(f"{context} must be an object")
            case_id = require_nonempty_string(case.get("id"), f"{context} id")
            if case_id in seen_ids:
                raise ValidationError(f"evals/{filename} has duplicate id '{case_id}'")
            seen_ids.add(case_id)
            prompt = require_nonempty_string(case.get("prompt"), f"{context} prompt")
            if prompt in seen_prompts:
                raise ValidationError(f"evals/{filename} contains a duplicate prompt")
            seen_prompts.add(prompt)

            if eval_kind == "trigger":
                if not isinstance(case.get("should_trigger"), bool):
                    raise ValidationError(f"{context} should_trigger must be boolean")
                trigger_outcomes.add(case["should_trigger"])
                require_nonempty_string(case.get("rationale"), f"{context} rationale")
            else:
                mode = require_nonempty_string(case.get("mode"), f"{context} mode")
                if mode not in TASK_MODES:
                    raise ValidationError(
                        f"{context} mode must be one of: "
                        + ", ".join(sorted(TASK_MODES))
                    )
                artifact = case.get("artifact")
                if artifact is not None:
                    artifact_path = (
                        root / require_nonempty_string(artifact, f"{context} artifact")
                    ).resolve()
                    try:
                        artifact_path.relative_to(root.resolve())
                    except ValueError as exc:
                        raise ValidationError(
                            f"{context} artifact escapes the skill root"
                        ) from exc
                    if not artifact_path.exists():
                        raise ValidationError(
                            f"{context} artifact does not exist: {artifact}"
                        )
                requirements = case.get("must_include")
                if (
                    not isinstance(requirements, list)
                    or not requirements
                    or any(
                        not isinstance(item, str) or not item.strip()
                        for item in requirements
                    )
                ):
                    raise ValidationError(
                        f"{context} must_include must be a non-empty string list"
                    )
        if eval_kind == "trigger" and trigger_outcomes != {True, False}:
            raise ValidationError(
                "evals/trigger-cases.json must contain positive and negative cases"
            )


def parse_openai_interface(openai_path: Path) -> Dict[str, str]:
    try:
        lines = openai_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValidationError(f"cannot read agents/openai.yaml: {exc}") from exc

    if not lines or lines[0].strip() != "interface:":
        raise ValidationError("agents/openai.yaml must begin with interface:")

    values: Dict[str, str] = {}
    for line_number, line in enumerate(lines[1:], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r'  ([a-z_]+):\s*("(?:[^"\\]|\\.)*")', line)
        if not match:
            raise ValidationError(
                f"agents/openai.yaml:{line_number}: expected a quoted interface string"
            )
        key, quoted_value = match.groups()
        if key in values:
            raise ValidationError(
                f"agents/openai.yaml:{line_number}: duplicate key '{key}'"
            )
        try:
            value = json.loads(quoted_value)
        except json.JSONDecodeError as exc:
            raise ValidationError(
                f"agents/openai.yaml:{line_number}: invalid quoted string"
            ) from exc
        values[key] = value
    return values


def validate_openai_yaml(root: Path, skill_root: Path, skill_name: str) -> None:
    openai_path = skill_root / "agents" / "openai.yaml"
    if not openai_path.is_file():
        raise ValidationError("agents/openai.yaml is required")

    interface = parse_openai_interface(openai_path)
    required = {"display_name", "short_description", "default_prompt"}
    missing = required - interface.keys()
    if missing:
        raise ValidationError(
            "agents/openai.yaml is missing: " + ", ".join(sorted(missing))
        )
    for key in required:
        require_nonempty_string(interface[key], f"agents/openai.yaml {key}")
    if interface["display_name"] != "Adapt UI for iPhone Duo":
        raise ValidationError(
            "agents/openai.yaml display_name must remain 'Adapt UI for iPhone Duo'"
        )
    if not 25 <= len(interface["short_description"]) <= 64:
        raise ValidationError(
            "agents/openai.yaml short_description must contain 25 to 64 characters"
        )
    invocation = f"${skill_name}"
    if invocation not in interface["default_prompt"]:
        raise ValidationError(
            f"agents/openai.yaml default_prompt must contain '{invocation}'"
        )


def validate(root: Path) -> None:
    if not root.is_dir():
        raise ValidationError(f"skill directory does not exist: {root}")
    skill_root = root / SKILL_RELATIVE_DIRECTORY
    skill_path = skill_root / "SKILL.md"
    if not skill_path.is_file():
        raise ValidationError(
            f"{SKILL_RELATIVE_DIRECTORY}/SKILL.md is required for GitHub skill discovery"
        )
    for required_file in ("CONTRIBUTING.md", "LICENSE", "NOTICE"):
        if not (root / required_file).is_file():
            raise ValidationError(
                f"{required_file} is required for the public repository"
            )

    metadata, body = parse_frontmatter(skill_path)
    validate_frontmatter(metadata, body)
    if skill_root.name != metadata["name"]:
        raise ValidationError(
            "the skill directory name must match the SKILL.md name"
        )
    for bundled_file, repository_file in (
        (skill_root / "LICENSE.txt", root / "LICENSE"),
        (skill_root / "NOTICE", root / "NOTICE"),
    ):
        if not bundled_file.is_file():
            raise ValidationError(
                f"{bundled_file.relative_to(root)} is required in the installable payload"
            )
        if bundled_file.read_text(encoding="utf-8") != repository_file.read_text(
            encoding="utf-8"
        ):
            raise ValidationError(
                f"{bundled_file.relative_to(root)} must match "
                f"{repository_file.relative_to(root)}"
            )
    for markdown_path in sorted(root.rglob("*.md")):
        if ".git" not in markdown_path.parts:
            validate_local_links(root, markdown_path)
    validate_json_files(root, skill_root)
    validate_device_profile(root, skill_root)
    validate_readme_translations(root)
    validate_evals(root, metadata["name"])
    validate_openai_yaml(root, skill_root, metadata["name"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate skill metadata, local links, JSON, evals, and UI metadata."
    )
    parser.add_argument(
        "skill_directory",
        nargs="?",
        default=str(Path(__file__).resolve().parent.parent),
    )
    args = parser.parse_args()

    root = Path(args.skill_directory).expanduser().resolve()
    try:
        validate(root)
    except ValidationError as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1

    print(f"skill structure valid: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
