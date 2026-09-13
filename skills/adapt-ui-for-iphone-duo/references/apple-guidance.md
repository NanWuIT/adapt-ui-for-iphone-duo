# Apple guidance and source status

Last reviewed: 2026-09-11.

## Provenance and toolchain status

Apple announced **iPhone Duo** on 2026-09-09.

iPhone Duo ships with iOS 27.1. Apple has published iOS 27.1 API examples in its iPhone Duo Tech Talks, but, as of this review, says Xcode 27.1 beta is coming later in September; Xcode 27 RC is the current public build. Treat the examples as official preview guidance, not compile-verified signatures, until the 27.1 SDK is available.

## Platform facts

- The outer display uses compact width. The fully available inner display uses regular width and height; folding, Split View, and stacked video-and-app multitasking create additional sizes.
- The inner display doesn't honor supported-interface-orientation restrictions. Use horizontal and vertical size classes plus scene or container geometry for layout decisions.
- `UIScreen.main` is ambiguous on a two-display device. Prefer environment and trait values; obtain a screen from the active window scene only when a `UIScreen` is required.
- Safe areas and layout margins can be asymmetric. Read each edge independently, including in Split View.
- iOS 26 Concentricity APIs (`ConcentricRectangle` and `UICornerConfiguration`) help edge-to-edge custom content follow screen corners. They are geometry tools, not a way to detect iPhone Duo.
- Each display has a camera-related reserved region. A conditional division region represents the fold when it divides the inner display.

Apps run on iPhone Duo without recompilation, but screen use improves with newer SDKs. Apple says the iOS 27.1 SDK enables content to reach the screen edge and gives standard navigation and toolbar controls the Duo vertical presentation.

## Layout rules

- Keep functionality, hierarchy, and state consistent across display transitions; expose more hierarchy on the inner display when useful.
- Use size classes, scene or container geometry, safe areas, and layout margins instead of device or pixel detection.
- Standard navigation and content containers, bars, and presentations adapt around the fold. Keep ordinary foreground content in the safe area.
- Query active reserved regions for custom edge-to-edge UI or important bounded elements that the system doesn't position. Ordinary custom content inside the safe area doesn't need a reserved-region query merely because it is custom.
- Keep important controls away from an active fold. Continuously scrolling articles and feeds generally shouldn't displace solely because they cross it.
- Prefer modest displacement, move the smallest coherent unit, and prefer an even grid-column count across the fold.
- Use `NavigationSplitView` or `UISplitViewController` for navigation hierarchy. Use arrangement views for two content views, with navigation outside the arrangement.
- Use a split arrangement for side-by-side, stacked, peer, or main-detail content and an overlay arrangement for a foreground-background relationship.

## Vertical bars

- System container bars move vertically on the outer display and on the inner display in landscape; the inner display in portrait keeps horizontal bars.
- Use toolbars attached to `NavigationStack` or `NavigationSplitView`, or bars owned by `UINavigationController` and `UITabBarController`. Standalone custom or system bar instances don't receive the complete placement behavior.
- The vertical bar stays on the hardware-aligned side in right-to-left languages. In Split View, each app places controls on its own outer edge.
- Group related items, avoid fixed spacers, provide a title and symbol for non-text-only items, and set visibility priority when actions may overflow.
- Test toolbar-versus-tab-bar compression with constrained height, Live Activities, and the keyboard. Test custom bar content with Reduce Transparency.

## Hinge, scenes, and both displays

- `onHingeChange` in SwiftUI and `UIHingeInteraction` in UIKit expose hinge status and angle for interactions or effects. Don't use hinge angle to drive layout; use size classes, reserved regions, and arrangements.
- All apps participate in side-by-side multitasking, and the stacked video-and-app layout is another resizable scene geometry to support.
- iPhone Duo can run multiple instances of apps that already support multiple scenes on iPad. New windows can't be created on the outer display, so handle activation errors or use the system window-activation action that hides when unavailable.
- Scene accessories can present supplementary UI on both displays. Their availability is system-controlled and can change, so observe it and disable dependent controls when unavailable. `CameraCaptureAccessory` is the camera-specific system accessory.

## Sources

- [Get ready for iPhone Duo](https://developer.apple.com/iphone-duo/)
- [Xcode 27 RC release](https://developer.apple.com/news/releases/?id=09092026h)
- [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- [Prepare your app for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111461/)
- [Raise the bar with iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111462/)
- [Strike a pose with adaptive layouts on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111463/)
- [Leverage multiple displays and scenes on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111464/)
- [Build a great camera experience for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111465/)
- [Design for iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111466/)
- [Apple Human Interface Guidelines: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Apple Design Resources](https://developer.apple.com/design/resources/)
- [iPhone Duo technical specifications](https://www.apple.com/iphone-duo/specs/)
- [Apple unveils iPhone Duo](https://www.apple.com/newsroom/2026/09/apple-unveils-iphone-duo/)

Re-check the current SDK, API documentation, and HIG before implementation. Replace preview status with the exact Xcode build used once Xcode 27.1 is available.
