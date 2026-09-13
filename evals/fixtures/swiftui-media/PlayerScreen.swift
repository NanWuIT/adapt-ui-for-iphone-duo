import SwiftUI
import UIKit

struct PlayerScreen: View {
    @State private var selectedEpisode: Episode?
    @State private var isPlaying = false

    let episodes: [Episode]

    var body: some View {
        GeometryReader { proxy in
            if UIScreen.main.bounds.width > 700 {
                HStack(spacing: 0) {
                    player
                    queue
                }
            } else {
                NavigationStack {
                    player
                }
            }

            PlayerToolbar(isPlaying: $isPlaying)
                .frame(width: 360, height: 96)
                .position(x: proxy.size.width / 2, y: proxy.size.height - 48)
        }
        .ignoresSafeArea()
    }

    private var player: some View {
        Rectangle()
            .fill(.black)
            .overlay {
                Text(selectedEpisode?.title ?? "Choose an episode")
                    .foregroundStyle(.white)
            }
    }

    private var queue: some View {
        List(episodes, selection: $selectedEpisode) { episode in
            Text(episode.title)
                .tag(episode)
        }
        .frame(width: 420)
    }
}

struct PlayerToolbar: View {
    @Binding var isPlaying: Bool

    var body: some View {
        HStack {
            Button("Back 15") {}
            Button(isPlaying ? "Pause" : "Play") {
                isPlaying.toggle()
            }
            Button("Forward 30") {}
        }
        .padding()
        .background(.ultraThinMaterial, in: Capsule())
    }
}

struct Episode: Identifiable, Hashable {
    let id: UUID
    let title: String
}
