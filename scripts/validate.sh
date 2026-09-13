#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "$script_dir/.." && pwd)"
skill_dir="$project_dir/skills/adapt-ui-for-iphone-duo"

for required_command in python3 rg; do
  if ! command -v "$required_command" >/dev/null 2>&1; then
    printf 'error: %s is required for validation\n' "$required_command" >&2
    exit 69
  fi
done

bash -n "$skill_dir/scripts/audit-duo-layout.sh"
bash -n "$script_dir/validate.sh"
bash -n "$project_dir/tests/test_audit.sh"
bash -n "$project_dir/tests/helpers/rg"
python3 "$script_dir/validate_skill.py" "$project_dir"
python3 -B "$project_dir/tests/test_validate_skill.py"
bash "$project_dir/tests/test_audit.sh"

if command -v gh >/dev/null 2>&1 && gh skill publish --help >/dev/null 2>&1; then
  gh skill publish "$project_dir" --dry-run
else
  printf '%s\n' 'note: GitHub CLI Agent Skills validation unavailable; gh skill publish --dry-run skipped'
fi

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck \
    "$skill_dir/scripts/audit-duo-layout.sh" \
    "$script_dir/validate.sh" \
    "$project_dir/tests/test_audit.sh" \
    "$project_dir/tests/helpers/rg"
else
  printf '%s\n' 'note: ShellCheck not installed; shell lint skipped'
fi

printf '%s\n' 'skill validation passed'
