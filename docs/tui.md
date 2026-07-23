# Interactive Terminal UI (TUI) Documentation

Prometra features a full-screen, interactive **Terminal User Interface (TUI)** built with [Textual](https://textual.textualize.io/) and [Rich](https://rich.readthedocs.io/).

It provides a rich terminal experience comparable to tools like `lazygit` or `btop` while running **100% locally** against Prometra's SQLite event database.

---

## Launching the TUI

To open the interactive terminal interface:

```bash
prometra ui
```

---

## Interactive Views Overview

Prometra TUI is organized into **8 interactive view screens**:

### 1. Dashboard View (`1`)
- **Real-Time Overview**: Active session, total recorded events, tracking duration, and AI cost estimates.
- **Top Edited Files**: Rankings of most modified files across development sessions.
- **Activity Feed**: Live event updates across filesystem, Git, and AI tool operations.

### 2. Timeline View (`2`)
- **Chronological Event Table**: View all tracked activity with timestamps, categories (`filesystem`, `ai_prompt`, `ai_tool`, `git_commit`), and summary metadata.
- **Color-Coded Badges**: Instant visual identification of event categories.

### 3. Replay View (`3`)
- **Session Player**: Replay coding sessions step-by-step.
- **Playback Controls**: Play/Pause (`Space`), Step Forward (`→`), Step Backward (`←`), and Speed Controls (`1x` - `10x`).
- **Progress Bar**: Animated visual progress bar indicating sequence position.

### 4. Search View (`4`)
- **Instant Search**: Query event history by keyword (prompts, commits, file paths).
- **Match Highlight**: Displays relevant snippets and match confidence scores.

### 5. Diff View (`5`)
- **File Version Diffing**: Select tracked file versions and view colorized line-by-line diffs.
- **Change Breakdown**: Header stats showing added (`+`), removed (`-`), and modified (`~`) lines.

### 6. Compare View (`6`)
- **Side-by-Side Session Comparison**: Compare metrics across two development sessions.
- **Productivity Delta**: Rates for events per minute, files changed per minute, and commits per hour.

### 7. Analytics View (`7`)
- **Codebase Health Score**: Overall development efficiency score.
- **AI Model Token Breakdown**: Token consumption table and estimated cost per model (`claude-3-5-sonnet`, `gpt-4o`).
- **Peak Activity Hours**: Developer peak coding windows.

### 8. Help View (`8` / `?`)
- **Keybindings Cheat Sheet**: Full reference guide for TUI shortcuts and features.

---

## Navigation & Controls

| Shortcut Key | Action / Command |
| :--- | :--- |
| **`1`** | Switch to **Dashboard View** |
| **`2`** | Switch to **Timeline View** |
| **`3`** | Switch to **Replay View** |
| **`4`** | Switch to **Search View** |
| **`5`** | Switch to **Diff View** |
| **`6`** | Switch to **Compare View** |
| **`7`** | Switch to **Analytics View** |
| **`8`** / **`?`** | Switch to **Help View** |
| **`Ctrl+P`** / **`:`** | Open **Command Palette** modal dialog |
| **`Ctrl+F`** / **`/`** | Open **Search Popup** modal dialog |
| **`Ctrl+T`** | Cycle **Color Themes** (`Cyan` -> `Dark` -> `Dracula` -> `High Contrast`) |
| **`R`** | Refresh active view data from SQLite |
| **`Space`** | Toggle Play / Pause in Replay View |
| **`Q`** / **`Ctrl+C`** | Quit Prometra TUI |

---

## Terminal Features

- **Mouse Support**: Clickable tabs, buttons, list items, and modal dialogs.
- **Command Palette (`Ctrl+P`)**: Jump to any view or trigger actions instantly.
- **Search Modal (`Ctrl+F`)**: Pop up a search overlay from any view screen.
- **Responsive Layout**: Resizes automatically to fit any terminal window dimensions.
- **Status Bar**: Bottom bar displaying active view indicator and keybindings legend.
