# SwiftUI and UIKit patterns

Use these as selection and review patterns alongside [Apple guidance](apple-guidance.md). The iOS 27.1 examples are transcribed from Apple's public Tech Talks. As of 2026-09-11, Xcode 27.1 beta is announced but not yet available, so compile-check every signature with the released SDK before shipping it.

## Contents

- [Compatibility and environmental inputs](#compatibility-and-environmental-inputs)
- [Screen corners and safe areas](#screen-corners-and-safe-areas)
- [Navigation hierarchy](#navigation-hierarchy)
- [Reserved regions](#reserved-regions)
- [Arrangement views](#arrangement-views)
- [Bars and controls](#bars-and-controls)
- [Displacement and hinge data](#displacement-and-hinge-data)
- [Multitasking, scenes, and accessories](#multitasking-scenes-and-accessories)

## Compatibility and environmental inputs

Keep the existing compact/regular implementation as the baseline. Add iOS 27.1 behavior behind availability checks, and keep older deployment targets compiling and behaving correctly.

Prefer:

- SwiftUI: horizontal and vertical size classes, container geometry, safe-area insets, reserved regions, and arrangement placement state.
- UIKit: trait collections, safe-area layout guides, layout margins, view bounds, reserved regions, and adaptive system view controllers.

The inner display doesn't honor supported-interface-orientation restrictions. Use size classes and scene geometry for layout; orientation declarations still matter for the outer display and older devices.

Don't use `UIScreen.main` on a two-display device. Prefer environment or trait values, including `traitCollection.displayScale`; when a screen object is necessary, obtain it from the active window scene:

```swift
let screen = view.window?.windowScene?.screen
```

Never branch on a model identifier, pixel resolution, physical dimension, assumed hinge width, or hinge angle.

## Screen corners and safe areas

Use the iOS 26 Concentricity APIs for custom edge-to-edge shapes that need to follow the screen's corners. They don't identify iPhone Duo and aren't layout breakpoints.

```swift
// SwiftUI
ConcentricRectangle()
    .fill(backgroundStyle)
    .ignoresSafeArea()

// UIKit: configure an appropriate UICornerConfiguration.
```

Read safe-area insets per edge. Don't average leading and trailing values or assume symmetry. Keep controls and readable foreground content inset; let decorative backgrounds extend to the view bounds when appropriate. Review every `ignoresSafeArea` call and avoid applying it to an entire interactive hierarchy.

## Navigation hierarchy

Use `NavigationSplitView` or `UISplitViewController` when the inner display can show more hierarchy. Keep selection and navigation models outside the compact/regular branch so state survives a transition.

Use one-pane navigation in compact width and side-by-side hierarchy when regular width is available. Let the system adapt column widths and margins around the fold instead of hard-coding equal pixel widths.

## Reserved regions

System containers and safe areas handle most content. Query reserved regions for custom edge-to-edge UI and important bounded elements that the system doesn't position; don't require the query for every custom view.

Apple's SwiftUI query pattern is:

```swift
GeometryReader { proxy in
    let divisionRegions = proxy.reservedRegions(kind: .division)
    let divisionFrames = divisionRegions.map(\.frame)
    // Place custom high-priority controls outside active frames.
}
```

Active regions are returned by default. Include inactive regions only for high-level planning, such as preferring an even grid-column count:

```swift
let possibleDivisions = proxy.reservedRegions(
    kind: .division,
    options: .includeInactive
)
```

Query camera or other obscuring regions with `.occlusion`. UIKit follows the same model:

```swift
let regions = view.reservedRegions(kind: .division)
let frames = regions.map(\.frame)
```

Convert frames when the consuming custom layout uses a different coordinate space. Don't add a permanent center gutter when the division region is inactive.

## Arrangement views

Use an arrangement for two content views, not for navigation infrastructure.

```swift
NavigationStack {
    ArrangementView {
        PrimaryView()
    } secondary: {
        SecondaryView()
    }
    .arrangementViewStyle(.split)
}
```

Restrict a split to the horizontal axis only when the product meaning requires side-by-side content:

```swift
.arrangementViewStyle(.split.axes(.horizontal))
```

Choose `.overlay` when the primary view is foreground content over a secondary background. Read `overlayArrangementZIndex` to adapt the foreground's internal presentation without discarding state.

UIKit uses `UIArrangementViewController`, assigns primary and secondary view controllers, and updates to a split or overlay arrangement. Make it the root of a navigation controller rather than placing navigation inside the arrangement controller.

Don't put an arrangement view inside `List`, `ScrollView`, or another scrolling container, and don't use it to replace `NavigationSplitView`.

## Bars and controls

With the iOS 27.1 SDK behavior, system container bars are vertical on the outer display and the inner display in landscape. They remain horizontal on the inner display in portrait and stay on the hardware-aligned side in right-to-left languages.

Attach SwiftUI toolbars to `NavigationStack` or `NavigationSplitView`; use bars owned by `UINavigationController` or `UITabBarController` in UIKit. Standalone custom bars and standalone `UIToolbar`, `UINavigationBar`, or `UITabBar` instances don't receive the complete Duo placement behavior.

- Group related actions with `ToolbarItemGroup` or `UIBarButtonItemGroup`.
- Avoid fixed spacers between toolbar items.
- Provide a title and symbol for non-text-only items so overflow remains understandable.
- Assign visibility priority when some actions can overflow.
- Keep controls affecting a leading pane with that pane instead of moving every action into the outer system bar.
- Choose and test whether toolbar items or the tab bar compress first when height is constrained.

## Displacement and hinge data

Before moving content, determine whether a bounded element intersects an active reserved-region frame. Move a standalone control independently and a tightly related cluster as a unit. Keep motion brief, trackable, and compatible with Reduce Motion.

Don't displace an article, feed, or other continuously scrolling surface solely because it crosses the fold. Ensure important floating controls, selection affordances, and non-scrolling overlays remain clear.

Use SwiftUI's `onHingeChange` or UIKit's `UIHingeInteraction` only when live hinge status or angle drives an interaction or effect. For layout, use size classes, reserved regions, and arrangements.

## Multitasking, scenes, and accessories

Treat side-by-side apps and stacked video-and-app presentation as resizable layouts driven by size classes and scene geometry.

If the app supports multiple scenes on iPad, audit per-scene state on iPhone Duo too. New windows can't be created on the outer display; handle scene-activation errors or use the system `UIWindowSceneActivation` action, which hides when unavailable.

Use scene accessories only for supplementary content on the second display. Observe accessory availability because the system can change it, and disable dependent controls when unavailable. `CameraCaptureAccessory` is appropriate only for the documented full-screen inner-display camera experience.
