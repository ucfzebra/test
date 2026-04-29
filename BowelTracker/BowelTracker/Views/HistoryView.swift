import SwiftUI
import SwiftData

struct HistoryView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \BowelMovement.timestamp, order: .reverse) private var movements: [BowelMovement]

    private var grouped: [(key: Date, value: [BowelMovement])] {
        let cal = Calendar.current
        let dict = Dictionary(grouping: movements) { cal.startOfDay(for: $0.timestamp) }
        return dict.sorted { $0.key > $1.key }
    }

    var body: some View {
        NavigationStack {
            List {
                ForEach(grouped, id: \.key) { date, dayMovements in
                    Section {
                        ForEach(dayMovements) { movement in
                            EntryRow(movement: movement)
                                .listRowInsets(EdgeInsets(top: 4, leading: 12, bottom: 4, trailing: 12))
                                .listRowBackground(Color.clear)
                                .listRowSeparator(.hidden)
                        }
                        .onDelete { offsets in
                            for index in offsets {
                                modelContext.delete(dayMovements[index])
                            }
                        }
                    } header: {
                        DayHeader(date: date, count: dayMovements.count, movements: dayMovements)
                    }
                }
            }
            .listStyle(.insetGrouped)
            .navigationTitle("History")
            .overlay {
                if movements.isEmpty {
                    ContentUnavailableView(
                        "No History",
                        systemImage: "calendar.badge.clock",
                        description: Text("Logged entries will appear here")
                    )
                }
            }
        }
    }
}

struct DayHeader: View {
    let date: Date
    let count: Int
    let movements: [BowelMovement]

    private var hasBlood: Bool { movements.contains { $0.hasBlood } }
    private var hasMucus: Bool { movements.contains { $0.hasMucus } }

    var body: some View {
        HStack(spacing: 6) {
            Text(date, format: .dateTime.weekday(.abbreviated).month(.abbreviated).day())
                .font(.subheadline.weight(.semibold))
                .foregroundStyle(.primary)

            Spacer()

            if hasBlood {
                Image(systemName: "drop.fill")
                    .foregroundStyle(.red)
                    .font(.caption)
            }
            if hasMucus {
                Image(systemName: "drop")
                    .foregroundStyle(.orange)
                    .font(.caption)
            }

            Text("\(count)")
                .font(.caption.weight(.bold))
                .monospacedDigit()
                .foregroundStyle(.white)
                .padding(.horizontal, 7)
                .padding(.vertical, 2)
                .background(countColor.opacity(0.85))
                .clipShape(Capsule())
        }
        .textCase(nil)
    }

    private var countColor: Color {
        switch count {
        case 0...4: return .blue
        case 5...7: return .orange
        default:    return .red
        }
    }
}
