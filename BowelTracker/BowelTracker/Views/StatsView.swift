import SwiftUI
import SwiftData
import Charts

struct StatsView: View {
    @Query(sort: \BowelMovement.timestamp, order: .reverse) private var movements: [BowelMovement]

    // MARK: - Computed stats

    private var last7DaysData: [DayCount] {
        let cal = Calendar.current
        return (0..<7).reversed().compactMap { offset -> DayCount? in
            guard let day = cal.date(byAdding: .day, value: -offset, to: cal.startOfDay(for: .now)),
                  let next = cal.date(byAdding: .day, value: 1, to: day)
            else { return nil }
            let count = movements.filter { $0.timestamp >= day && $0.timestamp < next }.count
            return DayCount(date: day, count: count)
        }
    }

    private var daysWithData: Int {
        last7DaysData.filter { $0.count > 0 }.count
    }

    private var dailyAverage: Double {
        guard daysWithData > 0 else { return 0 }
        return Double(last7DaysData.map(\.count).reduce(0, +)) / Double(daysWithData)
    }

    private var bloodPct: Double {
        guard !movements.isEmpty else { return 0 }
        return Double(movements.filter { $0.hasBlood }.count) / Double(movements.count) * 100
    }

    private var mucusPct: Double {
        guard !movements.isEmpty else { return 0 }
        return Double(movements.filter { $0.hasMucus }.count) / Double(movements.count) * 100
    }

    private var avgConsistency: Double {
        guard !movements.isEmpty else { return 0 }
        return Double(movements.map(\.consistency).reduce(0, +)) / Double(movements.count)
    }

    private var avgUrgency: Double {
        guard !movements.isEmpty else { return 0 }
        return Double(movements.map(\.urgency).reduce(0, +)) / Double(movements.count)
    }

    // MARK: - Body

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    FrequencyChart(data: last7DaysData)
                        .padding(.horizontal)

                    LazyVGrid(
                        columns: [GridItem(.flexible()), GridItem(.flexible())],
                        spacing: 12
                    ) {
                        StatCard(
                            title: "Daily Avg",
                            value: String(format: "%.1f", dailyAverage),
                            icon: "chart.line.uptrend.xyaxis",
                            color: .blue
                        )
                        StatCard(
                            title: "Avg Urgency",
                            value: urgencyText(avgUrgency),
                            icon: "exclamationmark.triangle.fill",
                            color: urgencyColor(avgUrgency)
                        )
                        StatCard(
                            title: "Blood",
                            value: String(format: "%.0f%%", bloodPct),
                            icon: "drop.fill",
                            color: bloodPct > 0 ? .red : .secondary
                        )
                        StatCard(
                            title: "Mucus",
                            value: String(format: "%.0f%%", mucusPct),
                            icon: "drop",
                            color: mucusPct > 0 ? .orange : .secondary
                        )
                        StatCard(
                            title: "Avg Bristol",
                            value: avgConsistency > 0
                                ? String(format: "%.1f", avgConsistency)
                                : "—",
                            icon: "square.stack.3d.up",
                            color: bristolColor(avgConsistency)
                        )
                        StatCard(
                            title: "Total Logged",
                            value: "\(movements.count)",
                            icon: "tray.full.fill",
                            color: .purple
                        )
                    }
                    .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .navigationTitle("Trends")
            .overlay {
                if movements.isEmpty {
                    ContentUnavailableView(
                        "No Data Yet",
                        systemImage: "chart.bar",
                        description: Text("Log some entries to see your trends")
                    )
                }
            }
        }
    }

    // MARK: - Helpers

    private func urgencyText(_ avg: Double) -> String {
        guard avg > 0 else { return "—" }
        return String(format: "%.1f", avg)
    }

    private func urgencyColor(_ avg: Double) -> Color {
        switch avg {
        case ..<1.5: return .green
        case ..<2.5: return .yellow
        case ..<3.5: return .orange
        case ..<4.5: return .red
        default:     return .purple
        }
    }

    private func bristolColor(_ avg: Double) -> Color {
        switch avg {
        case ..<2.5: return .brown
        case ..<4.5: return .green
        case ..<6:   return .orange
        default:     return .red
        }
    }
}

// MARK: - Chart

struct DayCount: Identifiable {
    let id = UUID()
    let date: Date
    let count: Int
}

struct FrequencyChart: View {
    let data: [DayCount]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Last 7 Days")
                .font(.headline)

            Chart(data) { item in
                BarMark(
                    x: .value("Day", item.date, unit: .day),
                    y: .value("Movements", item.count)
                )
                .foregroundStyle(barColor(item.count).gradient)
                .cornerRadius(5)
            }
            .frame(height: 160)
            .chartXAxis {
                AxisMarks(values: .stride(by: .day)) { _ in
                    AxisValueLabel(format: .dateTime.weekday(.narrow))
                }
            }
            .chartYAxis {
                AxisMarks(position: .leading) { value in
                    AxisGridLine()
                    AxisValueLabel()
                }
            }
        }
        .padding()
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.05), radius: 8, y: 2)
    }

    private func barColor(_ count: Int) -> Color {
        switch count {
        case 0...4: return .blue
        case 5...7: return .orange
        default:    return .red
        }
    }
}

// MARK: - Stat Card

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundStyle(color)

            Text(value)
                .font(.title2.weight(.bold))

            Text(title)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 14))
        .shadow(color: .black.opacity(0.04), radius: 4, y: 1)
    }
}
