#!/usr/bin/env bash

set -uo pipefail

readonly EX_USAGE=64
readonly EX_UNAVAILABLE=69
readonly EX_IOERR=74
readonly DEFAULT_MAX_RESULTS=25
readonly MAX_ALLOWED_RESULTS=1000

readonly program_name="${0##*/}"
fail_on_findings=0
max_results="$DEFAULT_MAX_RESULTS"
target_dir="."
end_options=0
positional_count=0

usage() {
  printf '%s\n' \
    "Usage: $program_name [OPTIONS] [--] [PROJECT_DIRECTORY]" \
    "" \
    "Find review candidates and adaptive-layout signals in Swift and Objective-C." \
    "PROJECT_DIRECTORY defaults to the current directory. Use -- before a path" \
    "that begins with a dash." \
    "" \
    "Options:" \
    "  --fail-on-findings  Exit 1 when one or more RISK groups are found." \
    "  --max-results N     Show at most N matched lines per group (default: 25," \
    "                      maximum: 1000)." \
    "  -h, --help          Show this help." \
    "" \
    "Exit status:" \
    "  0   Scan completed; report mode, or no RISK groups in fail mode." \
    "  1   RISK groups found with --fail-on-findings." \
    "  64  Invalid arguments or project directory." \
    "  69  Required tool unavailable (ripgrep)." \
    "  74  Temporary-file or source-scan failure." \
    "" \
    "RISK results require human review and are not automatically defects." \
    "INFO results identify existing adaptive primitives and never fail the scan."
}

usage_error() {
  printf 'error: %s\n' "$1" >&2
  printf "Try '%s --help' for usage.\n" "$program_name" >&2
  exit "$EX_USAGE"
}

validate_max_results() {
  if [[ ! "$max_results" =~ ^[1-9][0-9]*$ ]]; then
    usage_error "--max-results must be a positive integer"
  fi

  if ((max_results > MAX_ALLOWED_RESULTS)); then
    usage_error "--max-results cannot exceed $MAX_ALLOWED_RESULTS"
  fi
}

while (($# > 0)); do
  if ((end_options == 0)); then
    case "$1" in
      -h|--help)
        usage
        exit 0
        ;;
      --fail-on-findings)
        fail_on_findings=1
        shift
        continue
        ;;
      --max-results)
        if (($# < 2)); then
          usage_error "--max-results requires a value"
        fi
        max_results="$2"
        shift 2
        continue
        ;;
      --max-results=*)
        max_results="${1#*=}"
        shift
        continue
        ;;
      --)
        end_options=1
        shift
        continue
        ;;
      -*)
        usage_error "unknown option '$1' (use -- before a path beginning with '-')"
        ;;
    esac
  fi

  if ((positional_count > 0)); then
    usage_error "expected at most one PROJECT_DIRECTORY"
  fi
  target_dir="$1"
  positional_count=1
  shift
done

validate_max_results

if [[ ! -d "$target_dir" ]]; then
  printf 'error: directory not found: %s\n' "$target_dir" >&2
  exit "$EX_USAGE"
fi

if ! command -v rg >/dev/null 2>&1; then
  printf 'error: ripgrep (rg) is required\n' >&2
  exit "$EX_UNAVAILABLE"
fi

scan_tmp_root="${TMPDIR:-/tmp}"
scan_tmp_dir="$(mktemp -d "$scan_tmp_root/duo-ui-audit.XXXXXX")" || {
  printf 'error: could not create a temporary scan directory\n' >&2
  exit "$EX_IOERR"
}

# ShellCheck cannot infer that the EXIT trap invokes this cleanup function.
# shellcheck disable=SC2317,SC2329
cleanup() {
  if [[ -n "${scan_tmp_dir:-}" && -d "$scan_tmp_dir" ]]; then
    rm -rf -- "$scan_tmp_dir"
  fi
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

rg_options=(
  --line-number
  --no-heading
  --color never
  --hidden
  --multiline
  --glob '*.swift'
  --glob '*.m'
  --glob '*.mm'
  --glob '*.h'
  --glob '!Pods/**'
  --glob '!**/Pods/**'
  --glob '!Carthage/**'
  --glob '!**/Carthage/**'
  --glob '!DerivedData/**'
  --glob '!**/DerivedData/**'
  --glob '!.build/**'
  --glob '!**/.build/**'
  --glob '!SourcePackages/**'
  --glob '!**/SourcePackages/**'
  --glob '!.git/**'
  --glob '!**/.git/**'
)

risk_group_count=0
risk_line_count=0
info_group_count=0
info_line_count=0
scan_index=0

scan() {
  local severity="$1"
  local code="$2"
  local description="$3"
  local pattern="$4"
  local matches_file
  local errors_file
  local rg_status
  local matched_lines

  scan_index=$((scan_index + 1))
  matches_file="$scan_tmp_dir/matches-$scan_index.txt"
  errors_file="$scan_tmp_dir/errors-$scan_index.txt"

  rg "${rg_options[@]}" -- "$pattern" "$target_dir" \
    >"$matches_file" 2>"$errors_file"
  rg_status=$?

  case "$rg_status" in
    0)
      ;;
    1)
      return 0
      ;;
    *)
      printf 'error: source scan failed while evaluating [%s] (rg exit %d)\n' \
        "$code" "$rg_status" >&2
      sed -n '1,20p' "$errors_file" >&2
      return "$EX_IOERR"
      ;;
  esac

  matched_lines="$(wc -l <"$matches_file" | tr -d '[:space:]')"
  if [[ -z "$matched_lines" || "$matched_lines" == "0" ]]; then
    return 0
  fi

  if [[ "$severity" == "RISK" ]]; then
    risk_group_count=$((risk_group_count + 1))
    risk_line_count=$((risk_line_count + matched_lines))
  else
    info_group_count=$((info_group_count + 1))
    info_line_count=$((info_line_count + matched_lines))
  fi

  printf '\n[%s] [%s] %s\n' "$severity" "$code" "$description"
  sed -n "1,${max_results}p" "$matches_file"
  if ((matched_lines > max_results)); then
    printf '... truncated: showing %d of %d matched lines (raise --max-results to see more)\n' \
      "$max_results" "$matched_lines"
  fi
}

run_scan() {
  scan "$@" || exit $?
}

printf 'Adapt UI for iPhone Duo audit: %s\n' "$target_dir"
printf '%s\n' 'RISK matches require review; INFO matches show reusable adaptive primitives.'

run_scan "RISK" "DEVICE_GEOMETRY" \
  "Global screen access can bind layout to the wrong display or scene" \
  'UIScreen\s*[.]\s*(main|mainScreen)\b|\[\s*UIScreen\s+mainScreen\s*\]'

run_scan "RISK" "ORIENTATION_BRANCH" \
  "Orientation branching can miss folding, resizing, and Split View geometry" \
  'UIDevice\s*[.]\s*current\s*[.]\s*orientation\b|\[\s*\[\s*UIDevice\s+currentDevice\s*\]\s+orientation\s*\]|\b(interfaceOrientation|statusBarOrientation)\b|\bUIInterfaceOrientationIs(Landscape|Portrait)\s*[(]|\b(isLandscape|isPortrait)\b'

run_scan "RISK" "FIXED_FRAME" \
  "Large numeric frames deserve compact, regular, and partial-fold review" \
  '[.]\s*frame\s*[(][^)]*\b(width|height)\s*:\s*([89][0-9]([.][0-9]+)?|[1-9][0-9]{2,}([.][0-9]+)?)\b|CGRect\s*[(][^)]*\b(width|height)\s*:\s*([89][0-9]([.][0-9]+)?|[1-9][0-9]{2,}([.][0-9]+)?)\b|CGRectMake\s*[(]\s*[^,]+,\s*[^,]+,\s*([89][0-9]([.][0-9]+)?|[1-9][0-9]{2,}([.][0-9]+)?)\s*,|CGRectMake\s*[(]\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*([89][0-9]([.][0-9]+)?|[1-9][0-9]{2,}([.][0-9]+)?)\s*[)]'

run_scan "RISK" "SAFE_AREA" \
  "Safe-area overrides can expose controls to occlusion or reserved regions" \
  '[.]\s*(ignoresSafeArea|edgesIgnoringSafeArea)\s*[(]|insetsLayoutMarginsFromSafeArea\s*=\s*(false|NO)\b|edgesForExtendedLayout\s*=\s*UIRectEdgeAll\b|extendedLayoutIncludesOpaqueBars\s*=\s*(true|YES)\b'

run_scan "RISK" "CUSTOM_BAR" \
  "Custom or directly instantiated bars may miss system vertical placement" \
  '\b(UIToolbar|UINavigationBar|UITabBar)\s*[(]|\[\s*\[\s*(UIToolbar|UINavigationBar|UITabBar)\s+alloc\s*\]|\b(struct|class|final\s+class)\s+[A-Za-z_][A-Za-z0-9_]*(Toolbar|TabBar|NavigationBar)\b'

run_scan "RISK" "MANUAL_POSITION" \
  "Manual bounded-content positioning can place controls across a fold" \
  '[.]center\s*=|\bsetCenter\s*:|[.]position\s*[(][^)]*\b(x|y)\s*:|CGPoint\s*[(][^)]*\b(x|y)\s*:[^)]*[.]mid[XY]\b|CGPointMake\s*[(][^)]*CGRectGetMid[XY]\s*[(]'

run_scan "INFO" "ADAPTIVE_CONTAINER" \
  "Existing adaptive containers are useful implementation anchors" \
  '\b(NavigationSplitView|UISplitViewController|ArrangementView|UIArrangementViewController|ViewThatFits|AnyLayout)\b'

run_scan "INFO" "ADAPTIVE_ENVIRONMENT" \
  "Existing trait, safe-area, or reserved-region handling can be reused" \
  '\b(horizontalSizeClass|verticalSizeClass|traitCollectionDidChange|registerForTraitChanges|safeAreaInsetsDidChange|viewSafeAreaInsetsDidChange|reservedRegions|toolbarVerticalEdge)\b'

printf '\nSummary: %d RISK group(s), %d RISK matched line(s); %d INFO group(s), %d INFO matched line(s).\n' \
  "$risk_group_count" "$risk_line_count" "$info_group_count" "$info_line_count"

if ((risk_group_count == 0 && info_group_count == 0)); then
  printf '%s\n' 'No audit candidates or adaptive signals found in supported source files.'
elif ((risk_group_count == 0)); then
  printf '%s\n' 'No RISK candidates found; INFO signals are shown for context.'
fi

if ((fail_on_findings == 1 && risk_group_count > 0)); then
  exit 1
fi

exit 0
