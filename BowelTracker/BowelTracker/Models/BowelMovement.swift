import SwiftData
import Foundation

@Model
final class BowelMovement {
    var timestamp: Date
    var consistency: Int  // Bristol Stool Scale 1–7
    var urgency: Int      // 1–5: None → Extreme
    var hasBlood: Bool
    var hasMucus: Bool
    var notes: String

    init(
        timestamp: Date = .now,
        consistency: Int = 4,
        urgency: Int = 1,
        hasBlood: Bool = false,
        hasMucus: Bool = false,
        notes: String = ""
    ) {
        self.timestamp = timestamp
        self.consistency = consistency
        self.urgency = urgency
        self.hasBlood = hasBlood
        self.hasMucus = hasMucus
        self.notes = notes
    }
}

extension BowelMovement {
    struct BristolType: Identifiable {
        let id: Int
        let name: String
        let description: String
    }

    static let bristolTypes: [BristolType] = [
        .init(id: 1, name: "Type 1", description: "Separate hard lumps"),
        .init(id: 2, name: "Type 2", description: "Lumpy, sausage-like"),
        .init(id: 3, name: "Type 3", description: "Sausage with cracks"),
        .init(id: 4, name: "Type 4", description: "Smooth, soft sausage"),
        .init(id: 5, name: "Type 5", description: "Soft blobs, clear-cut"),
        .init(id: 6, name: "Type 6", description: "Fluffy, mushy pieces"),
        .init(id: 7, name: "Type 7", description: "Watery, no solid pieces"),
    ]

    static let urgencyLabels = ["None", "Mild", "Moderate", "High", "Extreme"]

    var bristolType: BristolType? {
        BowelMovement.bristolTypes.first { $0.id == consistency }
    }

    var urgencyLabel: String {
        guard urgency >= 1, urgency <= 5 else { return "Unknown" }
        return BowelMovement.urgencyLabels[urgency - 1]
    }

    var formattedTime: String {
        timestamp.formatted(date: .omitted, time: .shortened)
    }
}
