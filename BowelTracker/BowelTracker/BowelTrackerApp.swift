import SwiftUI
import SwiftData

@main
struct BowelTrackerApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: BowelMovement.self)
    }
}
