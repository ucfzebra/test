import SwiftUI
import SwiftData

struct TodayView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \BowelMovement.timestamp, order: .reverse) private var allMovements: [BowelMovement]
    @State private var showingLogSheet = false

    private var todayMovements: [BowelMovement] {
        let cal = Calendar.current
        let start = cal.startOfDay(for: .now)
        let end = cal.date(byAdding: .day, value: 1, to: start)!
        return allMovements.filter { $0.timestamp >= start && $0.timestamp < end }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    DailyCountCard(movements: todayMovements)
                        .padding(.horizontal)

                    if todayMovements.isEmpty {
                        emptyState
                    } else {
                        VStack(alignment: .leading, spacing: 8) {
                            Text("Today's Log")
                                .font(.headline)
                                .padding(.horizontal)

                            ForEach(todayMovements) { movement in
                                EntryRow(movement: movement)
                                    .padding(.horizontal)
                                    .contextMenu {
                                        Button(role: .destructive) {
                                            modelContext.delete(movement)
                                        } label: {
                                            Label("Delete", systemImage: "trash")
                                        }
                                    }
                            }
                        }
                    }
                }
                .padding(.vertical)
            }
            .navigationTitle(Date.now.formatted(.dateTime.weekday(.wide).month(.wide).day()))
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button {
                        showingLogSheet = true
                    } label: {
                        Image(systemName: "plus.circle.fill")
                            .font(.title2)
                    }
                }
            }
            .sheet(isPresented: $showingLogSheet) {
                LogEntryView()
            }
        }
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "checkmark.circle")
                .font(.system(size: 52))
                .foregroundStyle(.secondary)
            Text("No entries yet today")
                .font(.headline)
                .foregroundStyle(.secondary)
            Button("Log a Movement") { showingLogSheet = true }
                .buttonStyle(.borderedProminent)
        }
        .padding(.top, 40)
    }
}

// MARK: - Daily Summary Card

struct DailyCountCard: View {
    let movements: [BowelMovement]

    private var count: Int { movements.count }
    private var hasBlood: Bool { movements.contains { $0.hasBlood } }
    private var hasMucus: Bool { movements.contains { $0.hasMucus } }
    private var avgUrgency: Double {
        guard !movements.isEmpty else { return 0 }
        return Double(movements.map(\.urgency).reduce(0, +)) / Double(movements.count)
    }

    var body: some View {
        VStack(spacing: 14) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 2) {
                    Text("Movements Today")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                    Text("\(count)")
                        .font(.system(size: 60, weight: .bold, design: .rounded))
                        .foregroundStyle(countColor)
                }
                Spacer()
                VStack(alignment: .trailing, spacing: 6) {
                    if hasBlood {
                        SymptomBadge(text: "Blood", icon: "drop.fill", color: .red)
                    }
                    if hasMucus {
                        SymptomBadge(text: "Mucus", icon: "drop", color: .orange)
                    }
                }
            }

            if !movements.isEmpty {
                Divider()
                HStack {
                    Label(
                        String(format: "Avg urgency: %.1f", avgUrgency),
                        systemImage: "exclamationmark.triangle"
                    )
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    Spacer()
                }
            }
        }
        .padding()
        .background(.ultraThinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 16))
        .shadow(color: .black.opacity(0.06), radius: 8, y: 2)
    }

    private var countColor: Color {
        switch count {
        case 0...4: return .primary
        case 5...7: return .orange
        default: return .red
        }
    }
}

// MARK: - Entry Row

struct EntryRow: View {
    let movement: BowelMovement

    var body: some View {
        HStack(spacing: 12) {
            Text(movement.formattedTime)
                .font(.subheadline.monospacedDigit())
                .fontWeight(.medium)
                .frame(width: 68, alignment: .trailing)

            Rectangle()
                .fill(Color.secondary.opacity(0.25))
                .frame(width: 1, height: 46)

            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 4) {
                    if let b = movement.bristolType {
                        Text("Bristol \(b.id)")
                            .fontWeight(.semibold)
                        Text("·")
                            .foregroundStyle(.secondary)
                        Text(b.description)
                            .foregroundStyle(.secondary)
                    }
                }
                .font(.subheadline)

                HStack(spacing: 6) {
                    UrgencyBadge(urgency: movement.urgency)
                    if movement.hasBlood {
                        SymptomBadge(text: "Blood", icon: "drop.fill", color: .red)
                    }
                    if movement.hasMucus {
                        SymptomBadge(text: "Mucus", icon: "drop", color: .orange)
                    }
                }
            }

            Spacer()
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background(.background)
        .clipShape(RoundedRectangle(cornerRadius: 10))
        .shadow(color: .black.opacity(0.04), radius: 4, y: 1)
    }
}

// MARK: - Shared Badges

struct UrgencyBadge: View {
    let urgency: Int

    var color: Color {
        switch urgency {
        case 1: return .green
        case 2: return .yellow
        case 3: return .orange
        case 4: return .red
        case 5: return .purple
        default: return .gray
        }
    }

    var label: String {
        guard urgency >= 1, urgency <= 5 else { return "" }
        return BowelMovement.urgencyLabels[urgency - 1]
    }

    var body: some View {
        Text(label)
            .font(.caption2.weight(.semibold))
            .foregroundStyle(urgency == 2 ? .brown : color)
            .padding(.horizontal, 6)
            .padding(.vertical, 2)
            .background(color.opacity(urgency == 2 ? 0.25 : 0.12))
            .clipShape(Capsule())
    }
}

struct SymptomBadge: View {
    let text: String
    let icon: String
    let color: Color

    var body: some View {
        Label(text, systemImage: icon)
            .font(.caption2.weight(.semibold))
            .foregroundStyle(color)
            .padding(.horizontal, 7)
            .padding(.vertical, 2)
            .background(color.opacity(0.12))
            .clipShape(Capsule())
    }
}
