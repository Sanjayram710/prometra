# AI Session Intelligence Documentation

Prometra features a **100% Local-First AI Session Intelligence Engine**. It analyzes recorded development sessions to compute productivity metrics, detect behavioral coding patterns, automatically classify session intent, and generate actionable developer recommendations—without invoking external cloud APIs or sending telemetry data off your machine.

---

## Key Features

- **📊 Session Summary**: Calculates continuous coding duration, files modified/created/deleted, Git commits, AI prompts used, peak activity hours, top edited files, and primary programming languages.
- **🌟 Productivity Score (0–100)**: Evaluates focus time, commit frequency, AI tool synergy, context switching penalties, and task completion. Displays scores as `92 / 100` and star ratings (`★★★★☆`).
- **🏷️ Session Classification**: Automatically categorizes development intent:
  - `Feature Development`
  - `Bug Fix`
  - `Refactoring`
  - `Documentation`
  - `Research`
  - `Testing`
  - `Maintenance`
- **🔍 Coding Pattern Detection**: Identifies long coding sessions (>120 mins), frequent context switching, repeated file churn, large refactors, documentation updates, and bug fixes.
- **💡 Actionable Developer Recommendations**: Suggests practical improvements (e.g. committing more frequently, taking breaks after long sessions, refactoring high-churn files, adding documentation).
- **🖥️ Interactive TUI View #9 (`[9] Insights`)**: Integrated terminal dashboard view for session intelligence.

---

## CLI Usage (`prometra insights`)

### 1. Analyze Latest Development Session

```bash
prometra insights
```

### 2. Analyze Specific Session ID

```bash
prometra insights --session sess-1
```

### 3. Export Formats

Export intelligence reports to JSON, Markdown, or CSV:

```bash
# JSON Output
prometra insights --json

# Markdown Report
prometra insights --markdown > report.md

# CSV Metrics
prometra insights --csv
```

---

## Terminal Output Example

```
┌────────────────────────────────────────────────────────────────────────────────┐
│ 🚀 Prometra AI Session Intelligence                                            │
├────────────────────────────────────────────────────────────────────────────────┤
│ Session ID:                         sess-2026-07-24                            │
│ Classification:                     Feature Development (Confidence: 95%)      │
│ Productivity Score:                 92 / 100 (★★★★☆)                          │
│ Duration:                           45.0 mins (0.75 hrs)                       │
│ Files Modified / Created / Deleted: 8 / 2 / 0                                  │
│ Git Commits:                        3                                          │
│ AI Prompts Used:                    14                                         │
│ Estimated AI Cost:                  $0.052                                     │
│ Languages:                          Python, TypeScript                         │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│ 🔍 Detected Coding Patterns                                                    │
├────────────────────────────────────────────────────────────────────────────────┤
│ • [Feature Development] (positive): Added new features and created 2 files.   │
│ • [Repeated File Churn] (warning): File 'app.py' changed 10 times in session. │
└────────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────────┐
│ 💡 Actionable Developer Recommendations                                        │
├────────────────────────────────────────────────────────────────────────────────┤
│ • File Refactoring Opportunity (HIGH):                                         │
│   This file changed 10 times today. Consider breaking it into smaller modules.  │
│                                                                                │
│ • Rest & Break Reminder (MEDIUM):                                              │
│   Take a 10-15 minute break after continuous coding.                           │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## Interactive TUI View #9 (`Insights`)

Launch the terminal user interface:

```bash
prometra ui
```

Press key **`9`** or open the Command Palette (**`Ctrl+P`**) and select `Insights` to view the full-screen interactive session intelligence dashboard.
