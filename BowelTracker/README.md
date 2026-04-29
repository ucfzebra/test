# BowelTracker — UC Symptom Logger

An iOS app for tracking bowel movements and Ulcerative Colitis symptoms.

## Features

- **One-tap logging** — timestamp auto-fills to now (editable)
- **Bristol Stool Scale** (1–7) for consistency
- **Urgency rating** (1–5: None → Extreme)
- **Blood & mucus toggles**
- **Optional notes** per entry
- **Today view** — daily count with at-a-glance symptom flags
- **History view** — full log grouped by date with swipe-to-delete
- **Trends view** — 7-day frequency chart + stats (daily avg, blood %, mucus %, avg consistency/urgency)
- Data stored locally with **SwiftData** — no account needed

## Requirements

- iOS 17+
- Xcode 15+

## Setup

### Option A — XcodeGen (recommended, ~1 min)

```bash
brew install xcodegen
cd BowelTracker
xcodegen generate
open BowelTracker.xcodeproj
```

### Option B — Manual Xcode setup (~3 min)

1. Open Xcode → **File › New › Project**
2. Choose **iOS › App**, name it `BowelTracker`
3. Set **Interface: SwiftUI**, **Storage: SwiftData**, minimum deployment **iOS 17**
4. Delete the generated `ContentView.swift` and `Item.swift`
5. Drag in all `.swift` files from the `BowelTracker/` folder, preserving the folder structure
6. Replace the generated `Assets.xcassets` with the one in this repo
7. Build & run (⌘R)

## Project Structure

```
BowelTracker/
├── BowelTrackerApp.swift       # App entry point + SwiftData container
├── ContentView.swift           # Root tab view
├── Models/
│   └── BowelMovement.swift     # SwiftData model
├── Views/
│   ├── TodayView.swift         # Today tab: count card + log list
│   ├── LogEntryView.swift      # Log sheet: Bristol picker, urgency, symptoms
│   ├── HistoryView.swift       # History tab: date-grouped list
│   └── StatsView.swift         # Trends tab: chart + stat cards
└── Assets.xcassets/
```

## Bristol Stool Scale Reference

| Type | Appearance | UC Relevance |
|------|-----------|--------------|
| 1–2 | Hard lumps / lumpy sausage | Constipation |
| 3–4 | Cracked / smooth sausage | Normal |
| 5–7 | Soft blobs / mushy / watery | **Flare indicator** |

Types 6–7 with blood or mucus are common during UC flares — track them to share with your GI doctor.
