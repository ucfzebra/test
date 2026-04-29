import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            TodayView()
                .tabItem { Label("Today", systemImage: "house.fill") }
            HistoryView()
                .tabItem { Label("History", systemImage: "calendar") }
            StatsView()
                .tabItem { Label("Trends", systemImage: "chart.bar.fill") }
        }
        .tint(.blue)
    }
}
