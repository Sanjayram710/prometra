# Time Machine & Checkpoint System Documentation

Prometra includes a **100% Local Time Machine & Checkpoint System**. It allows developers to capture instant state snapshots of their project codebase, inspect differences between points in history, preview affected files, and safely restore project state—without cloud services or Git remote dependencies.

---

## Key Features

- **📍 Local Checkpoints**: Captures atomic file snapshots, SHA-256 hashes, Git branch/commit metadata, active session ID, AI prompts, productivity score, and summaries inside `.prometra/checkpoints/`.
- **🔍 Safe Pre-Restore Preview**: Inspects created, modified, and deleted files before executing a restore operation, prompting confirmation to prevent accidental data loss.
- **⚡ Checkpoint Comparison**: Side-by-side and unified diff comparisons between any two saved checkpoints (`prometra compare-checkpoints A B`).
- **📅 Timeline Integration**: View checkpoints directly inside chronological timeline event listings (`prometra timeline --checkpoints`).
- **🖥️ Interactive TUI View #10 (`[10] Time Machine`)**: Full-screen terminal checkpoint browser, diff inspector, and restore previewer.

---

## CLI Command Reference

### 1. Create a Checkpoint (`prometra checkpoint`)

```bash
prometra checkpoint "Finished authentication feature"
```

Options:
- `--session <id>`: Associate checkpoint with a specific session.

---

### 2. List Checkpoints (`prometra checkpoints`)

```bash
prometra checkpoints
```

Export options:
- `--json`: Export checkpoint list as JSON.
- `--markdown`: Export checkpoint list as Markdown document.
- `--csv`: Export checkpoint list as CSV.

---

### 3. Restore Project State (`prometra restore`)

```bash
prometra restore chk-20260724-1400-a1b2
```

Workflow:
1. Prometra computes and renders a **Restore Preview** listing:
   - **Created Files** (To add)
   - **Modified Files** (To overwrite)
   - **Deleted Files** (To remove)
2. Prometra prompts for explicit interactive confirmation: `⚠️ Are you sure you want to restore workspace files to this checkpoint? [y/N]`.
3. To bypass interactive confirmation in automated scripts, pass `--confirm` or `-y`:

```bash
prometra restore chk-20260724-1400-a1b2 --confirm
```

---

### 4. Compare Checkpoints (`prometra compare-checkpoints`)

Compare any two saved checkpoints:

```bash
prometra compare-checkpoints chk-20260724-1230-e5f6 chk-20260724-1400-a1b2
```

Outputs colorized file metrics (added, removed, modified count) and syntax-highlighted unified line diffs.

---

### 5. Display Checkpoints in Timeline (`prometra timeline --checkpoints`)

```bash
prometra timeline --checkpoints
```

Merges checkpoint markers (📍) chronologically alongside timeline filesystem, Git, and AI events.

---

## Interactive TUI View #10 (`Time Machine`)

Launch the terminal user interface:

```bash
prometra ui
```

Press key **`0`** or open the Command Palette (**`Ctrl+P`**) and select `Time Machine` to browse checkpoints, preview restores, and view diffs interactively inside the terminal.
