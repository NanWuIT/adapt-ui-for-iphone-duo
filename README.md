English | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

# Adapt UI for iPhone Duo

`$adapt-ui-for-iphone-duo` is an open-source [Agent Skill](https://agentskills.io/specification) (`SKILL.md`) for Codex and compatible coding agents. It audits, designs, implements, and verifies adaptive SwiftUI and UIKit interfaces for iPhone Duo and foldable iPhone displays.

The [skill instructions](skills/adapt-ui-for-iphone-duo/SKILL.md) provide a repeatable native iOS workflow for outer/cover and inner displays, partial folds, reserved regions, vertical system bars, resizable scenes, state continuity, accessibility, and older-device fallbacks. This is a skill—not a UI framework, runtime dependency, device-detection library, or separate brand.

## Current status

The hardware profile and platform guidance were reviewed on **2026-09-11** against primary Apple sources. Apple’s official product name is **iPhone Duo**.

Apple has published iOS 27.1 examples in its iPhone Duo Tech Talks, but Xcode 27.1 beta was still listed as coming later in September at the review date. The repository therefore labels those signatures as preview guidance rather than compile-verified API. The installed SDK always determines what an implementation may compile.

See [Apple guidance](skills/adapt-ui-for-iphone-duo/references/apple-guidance.md) for the dated toolchain status and primary-source links.

## What it covers

- SwiftUI and UIKit audits for fixed geometry, global-screen assumptions, orientation branches, broad safe-area overrides, manual positioning, and custom bars.
- Selection between navigation split views and two-content arrangement views.
- Active fold division regions and camera occlusion regions for custom bounded content.
- Compact, regular, continuously resized, book-like, and tabletop-like configurations.
- Navigation, selection, draft, playback, task, and per-scene state continuity.
- Dynamic Type, VoiceOver, Voice Control, right-to-left layout, Reduce Motion, and Reduce Transparency.
- Explicit fallbacks when iOS 27.1 APIs or Device Hub are unavailable.

The skill does not use model names, pixel dimensions, physical dimensions, or hinge angles as layout breakpoints. It does not target Android foldables, generic responsive websites, or ordinary iPad-only adaptation.

## Public hardware profile

| | Inner display | Outer display |
| --- | --- | --- |
| Size | 7.6-inch folding OLED | 5.4-inch OLED |
| Resolution | 1878 × 2670 px | 1398 × 2034 px |
| Density | 430 ppi | 460 ppi |
| Refresh rate | Up to 120 Hz | Up to 120 Hz |
| Peak outdoor brightness | 3000 nits | 3000 nits |

Apple lists open dimensions of 164.6 × 117.8 × 5.2 mm, closed dimensions of 84.1 × 117.8 × 11.3 mm, and a weight of 254 g. These values are for documentation, mockups, and test planning only. The structured, source-mapped data is in [device-profile.json](skills/adapt-ui-for-iphone-duo/references/device-profile.json).

## How discovery works

GitHub discovery and agent selection are separate steps. The preview [`gh skill search`](https://cli.github.com/manual/gh_skill_search) command searches public GitHub repositories for `SKILL.md` files whose `name` or `description` matches a query, and ranks name matches first. After installation, [Codex](https://developers.openai.com/codex/skills) sees the skill name and description and may invoke it when the task matches. The documented flow is therefore search or install first, then agent selection; an uninstalled GitHub repository is not part of Codex's local skill list.

## Install

[GitHub CLI's Agent Skills commands](https://cli.github.com/manual/gh_skill) are currently in preview. After publication, users can search the public GitHub skill index and install the skill for Codex with:

```bash
gh skill search "iphone duo"
gh skill install NanWuIT/adapt-ui-for-iphone-duo adapt-ui-for-iphone-duo --agent codex --scope user
```

The canonical GitHub repository is `NanWuIT/adapt-ui-for-iphone-duo`.

From an existing local checkout, GitHub CLI can install the standard skill directory directly:

```bash
gh skill install . adapt-ui-for-iphone-duo --from-local --agent codex --scope user
```

Or expose it to Codex with a manual user-level symlink:

```bash
mkdir -p ~/.agents/skills
ln -s "$PWD/skills/adapt-ui-for-iphone-duo" ~/.agents/skills/adapt-ui-for-iphone-duo
```

Keep the complete `skills/adapt-ui-for-iphone-duo` directory so the skill can load its references and run its scanner. The stable invocation identifier remains `$adapt-ui-for-iphone-duo` regardless of the checkout directory name.

## Use

Invoke it explicitly:

```text
Use $adapt-ui-for-iphone-duo to audit this SwiftUI reader for iPhone Duo. Do not edit files.
```

```text
Use $adapt-ui-for-iphone-duo to adapt this player and queue screen while preserving our iOS 26 fallback.
```

```text
Use $adapt-ui-for-iphone-duo to verify this UIKit layout. Report which Duo poses cannot be tested with the installed Xcode.
```

The trigger metadata also recognizes native iOS requests involving a foldable iPhone, book or tabletop pose, hinge or crease avoidance, reserved regions, and arrangement views. It includes negative boundaries to avoid unrelated responsive-layout tasks.

## Optional source scanner

The scanner requires Bash and [ripgrep](https://github.com/BurntSushi/ripgrep). From this repository:

```bash
bash skills/adapt-ui-for-iphone-duo/scripts/audit-duo-layout.sh -- /path/to/ios-project
```

It recursively inspects Swift and Objective-C sources, ignores common generated dependency trees, and prints `RISK` review candidates separately from `INFO` adaptive primitives. Findings are not automatic defects. Use `--fail-on-findings` only when that policy is intentional; run `--help` for the exit-code contract and other options.

## Validate a contribution

From the repository root:

```bash
bash scripts/validate.sh
```

Validation checks skill metadata, JSON data and eval fixtures, Markdown links, shell scripts, scanner behavior, and—when installed—ShellCheck. It also runs `gh skill publish --dry-run` when the installed GitHub CLI includes the preview Agent Skills commands. Python 3, Bash, and ripgrep are required for the complete local validation path.

## Repository layout

```text
README.md / README.*.md                     English and localized project docs
skills/adapt-ui-for-iphone-duo/              Installable Agent Skill payload
  SKILL.md                                    Trigger metadata and workflow
  agents/openai.yaml                          Human-facing skill metadata
  references/                                 Apple guidance and test patterns
  scripts/audit-duo-layout.sh                 Read-only native source scanner
evals/                                        Trigger and task contract cases
scripts/validate.sh                           Repository validation entry point
tests/                                        Scanner and validator regressions
.github/workflows/validate.yml                Continuous validation
```

## Primary sources

- [iPhone Duo technical specifications](https://www.apple.com/iphone-duo/specs/)
- [Get ready for iPhone Duo](https://developer.apple.com/iphone-duo/)
- [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- [Strike a pose with adaptive layouts on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111463/)

The complete source list is maintained in [Apple guidance](skills/adapt-ui-for-iphone-duo/references/apple-guidance.md).

## Contributing and license

See [CONTRIBUTING.md](CONTRIBUTING.md). The skill is available under the [MIT License](LICENSE). Apple trademarks are used only to describe compatibility; see [NOTICE](NOTICE). This project is independent and is not affiliated with or endorsed by Apple.
