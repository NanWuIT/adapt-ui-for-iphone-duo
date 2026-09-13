#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_dir="$(cd "$script_dir/.." && pwd)"
audit_script="$project_dir/skills/adapt-ui-for-iphone-duo/scripts/audit-duo-layout.sh"
fixtures_dir="$script_dir/fixtures"
positive_dir="$(cd "$fixtures_dir/positive" && pwd)"
negative_dir="$(cd "$fixtures_dir/negative" && pwd)"
exclusions_dir="$(cd "$fixtures_dir/exclusions" && pwd)"
helpers_dir="$(cd "$script_dir/helpers" && pwd)"
real_rg="$(command -v rg)"
test_tmp_root="${TMPDIR:-/tmp}"
test_tmp_dir="$(mktemp -d "$test_tmp_root/duo-ui-audit-tests.XXXXXX")"
stdout_file="$test_tmp_dir/stdout.txt"
stderr_file="$test_tmp_dir/stderr.txt"
last_status=0

cleanup() {
  if [[ -n "${test_tmp_dir:-}" && -d "$test_tmp_dir" ]]; then
    rm -rf -- "$test_tmp_dir"
  fi
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

fail() {
  printf 'test failure: %s\n' "$1" >&2
  if [[ -s "$stdout_file" ]]; then
    printf '%s\n' '--- stdout ---' >&2
    sed -n '1,160p' "$stdout_file" >&2
  fi
  if [[ -s "$stderr_file" ]]; then
    printf '%s\n' '--- stderr ---' >&2
    sed -n '1,160p' "$stderr_file" >&2
  fi
  exit 1
}

run_capture() {
  : >"$stdout_file"
  : >"$stderr_file"
  set +e
  "$@" >"$stdout_file" 2>"$stderr_file"
  last_status=$?
  set -e
}

assert_status() {
  local expected="$1"
  local context="$2"
  if [[ "$last_status" -ne "$expected" ]]; then
    fail "$context: expected exit $expected, got $last_status"
  fi
}

assert_stdout_contains() {
  local expected="$1"
  if ! "$real_rg" -Fq -- "$expected" "$stdout_file"; then
    fail "stdout did not contain: $expected"
  fi
}

assert_stderr_contains() {
  local expected="$1"
  if ! "$real_rg" -Fq -- "$expected" "$stderr_file"; then
    fail "stderr did not contain: $expected"
  fi
}

assert_stdout_excludes() {
  local unexpected="$1"
  if "$real_rg" -Fq -- "$unexpected" "$stdout_file"; then
    fail "stdout unexpectedly contained: $unexpected"
  fi
}

for required_fixture in \
  "$exclusions_dir/App/CleanView.swift" \
  "$exclusions_dir/Pods/Vendor.swift" \
  "$exclusions_dir/Nested/Carthage/Checkouts/Vendor.swift" \
  "$exclusions_dir/Nested/Build/DerivedData/Generated.m" \
  "$exclusions_dir/Nested/Package/.build/Generated.swift" \
  "$exclusions_dir/Nested/Package/SourcePackages/checkouts/Dependency.swift"; do
  if [[ ! -f "$required_fixture" ]]; then
    fail "required exclusion fixture is missing: $required_fixture"
  fi
done

run_capture "$audit_script" --help
assert_status 0 "help"
assert_stdout_contains "Usage: audit-duo-layout.sh [OPTIONS] [--] [PROJECT_DIRECTORY]"
assert_stdout_contains "--fail-on-findings"
assert_stdout_contains "--max-results N"
assert_stdout_contains "74  Temporary-file or source-scan failure."

run_capture "$audit_script" "$positive_dir"
assert_status 0 "positive report scan"
assert_stdout_contains "Adapt UI for iPhone Duo audit: $positive_dir"
assert_stdout_contains "[RISK] [DEVICE_GEOMETRY]"
assert_stdout_contains "[RISK] [ORIENTATION_BRANCH]"
assert_stdout_contains "[RISK] [FIXED_FRAME]"
assert_stdout_contains "[RISK] [SAFE_AREA]"
assert_stdout_contains "[RISK] [CUSTOM_BAR]"
assert_stdout_contains "[RISK] [MANUAL_POSITION]"
assert_stdout_contains "[INFO] [ADAPTIVE_CONTAINER]"
assert_stdout_contains "[INFO] [ADAPTIVE_ENVIRONMENT]"
assert_stdout_contains ".scale"
assert_stdout_contains "LegacyLayout.m"

run_capture "$audit_script" --fail-on-findings "$positive_dir"
assert_status 1 "fail-on-findings positive scan"
assert_stdout_contains "[RISK] [DEVICE_GEOMETRY]"

run_capture "$audit_script" --fail-on-findings "$negative_dir"
assert_status 0 "negative scan"
assert_stdout_contains "Summary: 0 RISK group(s), 0 RISK matched line(s); 0 INFO group(s), 0 INFO matched line(s)."
assert_stdout_contains "No audit candidates or adaptive signals found"
assert_stdout_excludes "[RISK]"
assert_stdout_excludes "[INFO]"

run_capture "$audit_script" --fail-on-findings "$exclusions_dir"
assert_status 0 "recursive dependency exclusion scan"
assert_stdout_contains "Summary: 0 RISK group(s), 0 RISK matched line(s); 0 INFO group(s), 0 INFO matched line(s)."
assert_stdout_excludes "Vendor.swift"
assert_stdout_excludes "Generated.swift"
assert_stdout_excludes "Dependency.swift"

run_capture "$audit_script" --max-results=1 "$positive_dir"
assert_status 0 "capped report scan"
assert_stdout_contains "... truncated: showing 1 of"

dash_parent="$test_tmp_dir/dash-parent"
mkdir -p "$dash_parent"
cp -R "$positive_dir" "$dash_parent/-project"
run_dash_path_scan() {
  (
    cd "$dash_parent"
    "$audit_script" -- -project
  )
}
run_capture run_dash_path_scan
assert_status 0 "dash-prefixed project path"
assert_stdout_contains "Adapt UI for iPhone Duo audit: -project"
assert_stdout_contains "[RISK] [DEVICE_GEOMETRY]"

space_project="$test_tmp_dir/project with spaces"
cp -R "$negative_dir" "$space_project"
run_capture "$audit_script" "$space_project"
assert_status 0 "absolute path containing spaces"
assert_stdout_contains "Adapt UI for iPhone Duo audit: $space_project"

run_capture "$audit_script" "$test_tmp_dir/does-not-exist"
assert_status 64 "missing project directory"
assert_stderr_contains "directory not found"

run_capture env TMPDIR="$test_tmp_dir/missing/tmp" "$audit_script" "$positive_dir"
assert_status 74 "temporary directory failure"
assert_stderr_contains "could not create a temporary scan directory"

run_capture "$audit_script" --not-an-option
assert_status 64 "unknown option"
assert_stderr_contains "use -- before a path beginning with '-'"

run_capture "$audit_script" --max-results 0 "$positive_dir"
assert_status 64 "invalid max-results"
assert_stderr_contains "must be a positive integer"

run_capture "$audit_script" --max-results
assert_status 64 "missing max-results value"
assert_stderr_contains "--max-results requires a value"

run_capture "$audit_script" --max-results 1001 "$positive_dir"
assert_status 64 "oversized max-results"
assert_stderr_contains "cannot exceed 1000"

run_capture "$audit_script" "$positive_dir" "$negative_dir"
assert_status 64 "extra positional argument"
assert_stderr_contains "expected at most one PROJECT_DIRECTORY"

run_capture env PATH="$helpers_dir:$PATH" "$audit_script" "$positive_dir"
assert_status 74 "ripgrep scan failure"
assert_stderr_contains "source scan failed"
assert_stderr_contains "synthetic ripgrep failure"
assert_stdout_excludes "No audit candidates"

empty_path="$test_tmp_dir/empty-path"
mkdir -p "$empty_path"
run_capture env PATH="$empty_path" /bin/bash "$audit_script" "$positive_dir"
assert_status 69 "missing ripgrep"
assert_stderr_contains "ripgrep (rg) is required"

printf '%s\n' 'audit scanner tests passed'
