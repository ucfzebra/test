import SwiftUI
import SwiftData

struct LogEntryView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.dismiss) private var dismiss

    @State private var timestamp = Date.now
    @State private var consistency = 4
    @State private var urgency = 1
    @State private var hasBlood = false
    @State private var hasMucus = false
    @State private var notes = ""

    var body: some View {
        NavigationStack {
            Form {
                Section("Time") {
                    DatePicker(
                        "Timestamp",
                        selection: $timestamp,
                        displayedComponents: [.date, .hourAndMinute]
                    )
                    .labelsHidden()
                }

                Section {
                    BristolPicker(selected: $consistency)
                } header: {
                    Text("Consistency — Bristol Stool Scale")
                } footer: {
                    Text("Types 1–2: constipation · Types 3–4: normal · Types 5–7: diarrhea")
                }

                Section {
                    UrgencyPicker(selected: $urgency)
                } header: {
                    Text("Urgency")
                }

                Section("Symptoms") {
                    Toggle(isOn: $hasBlood) {
                        Label("Blood present", systemImage: "drop.fill")
                            .foregroundStyle(hasBlood ? .red : .primary)
                    }
                    .tint(.red)

                    Toggle(isOn: $hasMucus) {
                        Label("Mucus present", systemImage: "drop")
                            .foregroundStyle(hasMucus ? .orange : .primary)
                    }
                    .tint(.orange)
                }

                Section("Notes (optional)") {
                    TextField("e.g. after meal, cramping…", text: $notes, axis: .vertical)
                        .lineLimit(3...)
                }
            }
            .navigationTitle("Log Entry")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Save") { save() }
                        .fontWeight(.semibold)
                }
            }
        }
    }

    private func save() {
        let movement = BowelMovement(
            timestamp: timestamp,
            consistency: consistency,
            urgency: urgency,
            hasBlood: hasBlood,
            hasMucus: hasMucus,
            notes: notes
        )
        modelContext.insert(movement)
        dismiss()
    }
}

// MARK: - Bristol Scale Picker

struct BristolPicker: View {
    @Binding var selected: Int

    var body: some View {
        VStack(spacing: 0) {
            ForEach(BowelMovement.bristolTypes) { type in
                Button {
                    withAnimation(.easeInOut(duration: 0.15)) {
                        selected = type.id
                    }
                } label: {
                    HStack(spacing: 12) {
                        ZStack {
                            Circle()
                                .fill(bristolColor(type.id).opacity(0.15))
                                .frame(width: 34, height: 34)
                            Text("\(type.id)")
                                .font(.headline)
                                .foregroundStyle(bristolColor(type.id))
                        }

                        VStack(alignment: .leading, spacing: 2) {
                            Text(type.name)
                                .font(.subheadline.weight(.medium))
                            Text(type.description)
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }

                        Spacer()

                        if selected == type.id {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundStyle(.blue)
                                .transition(.scale.combined(with: .opacity))
                        }
                    }
                    .foregroundStyle(.primary)
                    .padding(.vertical, 6)
                }
                .buttonStyle(.plain)

                if type.id < 7 {
                    Divider().padding(.leading, 58)
                }
            }
        }
    }

    func bristolColor(_ type: Int) -> Color {
        switch type {
        case 1, 2: return .brown
        case 3, 4: return .green
        case 5, 6: return .orange
        case 7:    return .red
        default:   return .gray
        }
    }
}

// MARK: - Urgency Picker

struct UrgencyPicker: View {
    @Binding var selected: Int

    private let labels = BowelMovement.urgencyLabels
    private let colors: [Color] = [.green, .yellow, .orange, .red, .purple]

    var body: some View {
        HStack(spacing: 6) {
            ForEach(1...5, id: \.self) { level in
                let idx = level - 1
                let isSelected = selected == level
                Button {
                    withAnimation(.easeInOut(duration: 0.15)) {
                        selected = level
                    }
                } label: {
                    VStack(spacing: 4) {
                        Text("\(level)")
                            .font(.title3.weight(.bold))
                        Text(labels[idx])
                            .font(.caption2)
                            .lineLimit(1)
                            .minimumScaleFactor(0.6)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                    .background(isSelected ? colors[idx] : colors[idx].opacity(0.1))
                    .foregroundStyle(isSelected ? .white : (idx == 1 ? .brown : colors[idx]))
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                }
                .buttonStyle(.plain)
            }
        }
        .padding(.vertical, 4)
    }
}
