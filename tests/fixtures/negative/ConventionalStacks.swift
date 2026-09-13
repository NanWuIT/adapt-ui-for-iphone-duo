import SwiftUI

struct ConventionalStacks: View {
    var body: some View {
        VStack {
            HStack {
                Image(systemName: "star")
                    .frame(width: 24, height: 24)
                Text("A normal stack is not a foldable-layout finding")
            }

            ZStack {
                RoundedRectangle(cornerRadius: 12)
                Text("Local layout")
            }
            .frame(height: 44)
        }
    }
}
