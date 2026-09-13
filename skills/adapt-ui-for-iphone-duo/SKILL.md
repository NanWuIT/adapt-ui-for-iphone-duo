---
name: adapt-ui-for-iphone-duo
description: Adapt iPhone Duo and foldable iPhone UI in native iOS apps built with SwiftUI or UIKit. Use for adaptive UI audits, designs, implementations, or verification involving outer/cover and inner displays, book/tabletop/half-open poses, fold/hinge/crease or camera occlusion avoidance, reserved regions, ArrangementView or UIArrangementViewController, vertical system bars, and state continuity across fold or display transitions. Also use for the discovery alias “iPhone 18 Duo” or explicit $adapt-ui-for-iphone-duo. Do not use for ordinary iPhone/iPad responsiveness, generic resizing or multiwindow work, Android/Surface Duo, web/Flutter/React Native, incidental fold wording, or hardware specs, dimensions, shopping, comparison, news, or rumors.
---

# Adapt UI for iPhone Duo

Adapt native iOS interfaces to the space and system state that iPhone Duo provides. Preserve product hierarchy, state, accessibility, and older-device behavior instead of creating a separate layout for every display or pose.

## Route the task

Resolve the directory containing this `SKILL.md` as `skill_root`. Resolve the user's iOS repository or source directory as `project_root`. Do not assume the current working directory is the skill directory.

Determine the requested mode before acting:

- **Audit:** inspect and report; do not edit files.
- **Design:** recommend a pattern and migration plan; do not edit files unless asked.
- **Implementation:** edit the scoped project, then build or type-check what the environment supports.
- **Verification:** test an existing adaptation and report observed results without silently changing it.

Inspect repository instructions, deployment targets, installed Xcode and SDK versions, supported platforms, current navigation architecture, and working-tree state. Keep unrelated user changes intact.

Load only the guidance needed for the task:

- Read [references/apple-guidance.md](references/apple-guidance.md) before making Duo-specific behavior or API claims.
- Read [references/swiftui-uikit-patterns.md](references/swiftui-uikit-patterns.md) when auditing, designing, or changing SwiftUI or UIKit code.
- Read [references/test-matrix.md](references/test-matrix.md) when planning or performing verification.
- Read [references/device-profile.json](references/device-profile.json) only for hardware facts, documentation, mockups, or simulator planning. Never turn its pixel or physical values into runtime breakpoints.

## Establish the implementation boundary

Treat the installed SDK as the source of truth for compilable symbols. The date-stamped reference material can describe official preview APIs that are not yet present locally.

- Check the exact Xcode and iPhoneOS SDK build before using iOS 27.1-only APIs.
- Remember that `if #available` gates runtime execution; it does not make symbols missing from the compile SDK available.
- If the installed SDK lacks a preview symbol, implement the strongest SDK-supported adaptive behavior and keep preview-only code out of compiled sources. Present any future snippet as an explicitly unverified sketch.
- If the repository must compile with older Xcode versions, use its established compiler/SDK fencing strategy or isolate new-SDK code in an appropriate target. Do not invent a guard that has not been build-tested.
- Never claim that a Tech Talk sample compiled, Device Hub ran, or a physical pose passed unless that happened in the current environment.

Identify the UI stack and preserve its architecture:

- Treat `SwiftUI`, `NavigationStack`, `NavigationSplitView`, `TabView`, and view modifiers as SwiftUI.
- Treat view controllers, Auto Layout, `UINavigationController`, `UISplitViewController`, and `UITabBarController` as UIKit.
- Handle a mixed project one screen boundary at a time and preserve existing hosting bridges.

## Scan and inspect

When source code is available, run the bundled read-only scanner from the resolved skill directory. It requires `bash` and `ripgrep` (`rg`):

Substitute the resolved absolute paths when invoking it; do not run a relative path from the target repository:

```bash
bash "/resolved/skill/root/scripts/audit-duo-layout.sh" -- "/resolved/project/root"
```

Use `--fail-on-findings` only in automation that intentionally treats review candidates as a failing result. A normal scan exits successfully even when it reports candidates. Treat every match as a lead that requires contextual inspection, never as a proven defect or a support verdict.

If `rg` is unavailable, do not install software without authorization. Continue with read-only repository search tools already available, inspect the same risk categories below, and report that the bundled scanner was not run.

Map the important screens, navigation paths, and state transitions. Prioritize:

- fixed frames, global-screen reads, orientation branches, or manual positioning;
- centered controls, media, canvases, maps, dialogs, and non-scrolling overlays;
- custom navigation, toolbars, tab bars, sheets, popovers, menus, or alerts;
- navigation hierarchies and two-content relationships such as player/queue or canvas/inspector;
- edge-to-edge content, asymmetric padding, and broad safe-area overrides;
- grids spanning the wide inner display;
- state that could reset when compact, regular, split, or overlay presentation changes.

Classify each finding:

- `P0`: primary action, required content, or navigation becomes unavailable.
- `P1`: important bounded content can be obscured, a common configuration is unusable, or state is lost.
- `P2`: layout wastes space, moves excessively, clips at accessibility sizes, or relies on fragile assumptions.
- `P3`: polish, grouping, motion, or documentation improvement.

For every finding, include evidence, affected configuration, user impact, recommended pattern, and a verification case.

## Choose the adaptive pattern

Apply these rules in order:

1. Prefer system containers, bars, and presentations so safe areas, reserved regions, placement, and transitions adapt with the system.
2. Drive hierarchy with horizontal and vertical size classes plus container or scene geometry. Continue supporting arbitrary resized widths rather than detecting only outer and inner endpoints.
3. Read every safe-area edge independently; do not assume symmetry.
4. Use `NavigationSplitView` or `UISplitViewController` for navigation hierarchy. Preserve selection and paths when it collapses to one pane.
5. Use `ArrangementView` or `UIArrangementViewController` only for a relationship between two content views. Keep navigation outside the arrangement.
6. Choose split arrangement for peer, main/detail, or side-by-side/stacked content; choose overlay for a genuine foreground/background relationship.
7. Query active division or occlusion regions only for custom edge-to-edge layout and important bounded elements the system does not place safely.
8. Let continuously scrolling content cross a fold when system layout keeps it readable and operable. Move a bounded control or tightly related cluster only when an active region would obscure or split it.
9. Move the smallest coherent unit, preserve spatial relationships, and avoid dramatic pose-specific rearrangements.
10. Prefer an even grid-column count when a grid spans both sides of a possible division region.

Do not identify iPhone Duo by model string, display pixels, physical dimensions, a hard-coded crease, or a guessed hinge angle. Use hinge angle only for a documented interaction or visual effect; use size classes, geometry, safe areas, reserved regions, and arrangements for layout.

## Implement without regressions

Keep existing behavior as the fallback and preserve:

- full functionality on outer and inner displays and older supported devices;
- navigation path, selection, drafts, playback, task progress, and per-scene state across resizing and display transitions;
- semantic order, accessibility labels, Dynamic Type, VoiceOver, Voice Control, Reduce Motion, Reduce Transparency, and right-to-left layout;
- standard gestures and presentation behavior.

Use toolbars owned by system navigation containers so iOS can choose horizontal or vertical placement. Group related actions, provide understandable labels and symbols, assign sensible visibility priority, and let lower-priority actions overflow. Test bar compression rather than assuming every item remains visible.

Allow decorative backgrounds to extend edge to edge. Keep interactive foreground content inside system-managed safe areas unless a reserved-region-aware custom layout is required and verified.

Audit multiple scenes, stacked video-and-app layouts, scene accessories, and camera accessories only when the app uses those capabilities. Do not make them universal requirements.

## Verify proportionately

Build or type-check every changed target available in the environment. Select relevant cases from [references/test-matrix.md](references/test-matrix.md) and include at minimum:

- compact and regular layouts plus continuous resizing;
- state continuity across presentation changes;
- applicable reserved-region, safe-area, toolbar, sheet, keyboard, and rotation behavior;
- largest Dynamic Type, accessibility navigation, right-to-left layout, and motion/transparency settings affected by the change;
- the project's minimum supported OS and a conventional iPhone fallback.

Use Xcode Device Hub for actual iPhone Duo displays and poses only when the installed toolchain provides it. Otherwise run the strongest available proxies and name the unverified Duo configurations.

Reject an implementation when a primary action disappears, an important bounded interactive element is obscured by an active region, transition state resets, accessibility becomes unusable, or an older supported build regresses. Do not reject ordinary continuously scrolling content merely for crossing a division region.

## Return a mode-specific result

Lead with the outcome and keep verified facts separate from assumptions:

- **Audit:** scope and environment; findings ordered by priority with file and line evidence; recommended fixes; verification cases; scan/tooling limitations.
- **Design:** chosen adaptive pattern; state and accessibility behavior; compatibility boundary; implementation sequence; unresolved product decisions and validation needs.
- **Implementation:** files changed; resulting compact/regular and fold behavior; fallback strategy; exact builds or checks run and their results; remaining Device Hub or hardware validation.
- **Verification:** environment; cases run with pass/fail results; defects with reproduction evidence; configurations not run and why.

Never report “Duo-ready” from static review, scanner output, or endpoint-only simulator checks.
