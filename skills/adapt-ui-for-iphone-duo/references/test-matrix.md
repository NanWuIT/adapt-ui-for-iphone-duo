# iPhone Duo verification matrix and release gates

Use the smallest matrix that covers the changed behavior, then expand for high-risk navigation, state, camera, media, or scene changes.

| Configuration | Expected behavior |
| --- | --- |
| Outer display, compact width | Full functionality remains available in one pane |
| Inner display, fully open | Regular layout uses space productively without arbitrary stretching |
| Inner display, book-like partial fold | Important bounded content and controls avoid the active division region |
| Inner display, tabletop partial fold | Distant content occupies the upper region and interactive controls remain reachable below |
| Inner display, portrait | Bars remain horizontal and hierarchy stays coherent |
| Inner display, landscape | System container bars become vertical and asymmetric safe areas are respected |
| Inner display with a restrictive orientation declaration | Layout still fills and adapts because the inner display doesn't honor supported-interface-orientation restrictions |
| Split View, app on physical left | Controls use the app's outer edge and content remains inset |
| Split View, app on physical right | Controls use the opposite outer edge without assuming symmetric insets |
| Stacked video and app | Layout follows the resulting size classes and scene geometry without endpoint assumptions |
| Two instances of a multiple-scene app on the inner display | Navigation, selection, drafts, and transient state remain isolated per scene |
| Request a new window on the outer display | The system action is unavailable or the activation failure is handled without losing work |
| Scene accessory becomes available, unavailable, then available | Supplementary UI and its controls track availability without duplicating or losing primary state |
| Inner camera inactive then active | Custom edge-to-edge UI responds to the occlusion region without losing state |
| Dynamic Island or Live Activity expanded | Outer-display controls remain visible or overflow safely |
| Keyboard or constrained vertical-bar height | The chosen toolbar-versus-tab-bar compression preserves primary destinations and actions |
| Reduce Transparency | Custom vertical-bar content remains legible when the system supplies an opaque background |
| Edge-to-edge custom shape on each display | Concentricity follows the active screen's corners without a device or pixel branch |
| Hinge-driven interaction or effect | `onHingeChange` or `UIHingeInteraction` updates the effect; layout still uses regions, arrangements, and size classes |
| Open-to-closed and closed-to-open | Navigation, selection, drafts, playback, and task state persist |
| Largest accessibility text sizes | Text reflows; primary actions remain reachable; labels don't clip |
| Right-to-left language | Semantic order is correct while hardware-aligned vertical bars stay on their physical side |
| VoiceOver and Voice Control | Reading and focus order match visual meaning after rearrangement |
| Reduce Motion | Transitions remain understandable without relying on large movement |
| Older supported iPhone and OS | Availability fallback compiles and preserves existing behavior |

Only run the multiple-scene, scene-accessory, Concentricity, or hinge rows when the changed feature uses those capabilities.

## Verification methods

1. Record the exact Xcode and SDK build. As of 2026-09-11, Apple lists Xcode 27.1 beta as coming later in September, so don't claim iOS 27.1 compilation or Duo simulation yet.
2. Build with the latest installed SDK and the project's minimum deployment target. Use compact/regular and continuous-resize tests as the pre-27.1 baseline.
3. When Xcode 27.1 is available, compile every new signature and use Device Hub to simulate both displays, rotations, folds, and transitions.
4. Resize continuously instead of checking only endpoints. Watch for state resets, discontinuous jumps, stale safe-area values, and stale reserved-region frames.
5. Overlay or log active reserved-region frames for custom-layout debugging, but remove debug visuals from production.
6. Exercise sheets, alerts, menus, popovers, keyboard presentation, rotation, and applicable multitasking or multi-scene flows on changed screens.
7. Test a standard iPhone and, when supported, iPad or window resizing to catch overfitting.

Record what actually ran and what remains preview-only. Don't claim partial-fold verification from a static wide simulator or API verification from a Tech Talk snippet alone.
