import SwiftUI
import UIKit

struct LayoutCandidates: View {
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass

    var body: some View {
        NavigationSplitView {
            Text("Primary")
        } detail: {
            Text("Secondary")
        }
        .frame(
            width: 390,
            height: 240
        )
        .ignoresSafeArea()
    }
}

final class CustomLayoutController: UIViewController {
    override func viewDidLayoutSubviews() {
        super.viewDidLayoutSubviews()

        let displayScale = UIScreen
            .main
            .scale
        let orientation = UIDevice.current.orientation
        view.center = CGPoint(
            x: view.bounds.midX,
            y: view.bounds.midY
        )
        _ = (displayScale, orientation)
    }
}

struct PlaybackToolbar: View {
    var body: some View {
        Text("Playback")
    }
}
