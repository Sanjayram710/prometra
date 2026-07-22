# Prometra Session Replay

**Session Replay** (`prometra replay`) in Prometra reconstructs and plays back an entire development session from recorded timeline events. It tells the chronological story of a coding session step-by-step or in real-time.

## Replayed Events Sequence

A session replay visually tracks:
- 🚀 **Session Started**
- 💡 **AI Prompts**
- 🤖 **AI Responses**
- 🛠️ **Tool Invocations**
- 📝 **Filesystem Changes**
- 🔀 **Git Commits**
- ❌ **Diagnostic Errors**
- 🏁 **Session Ended**

## Usage & Options

### 1. Replay Specific Session
Replay a specific session by ID:
```bash
prometra replay --session 8caa2490-ca09-4100-b6f1-a1b2c3d4e5f6
```

### 2. Replay Most Recent Session
Automatically select and replay the latest recorded session:
```bash
prometra replay --latest
```

### 3. Accelerated & Real-Time Playback Speeds
Adjust playback timing:
```bash
prometra replay --latest --speed 1x      # Real-time pacing
prometra replay --latest --speed 2x      # 2x speed
prometra replay --latest --speed 5x      # 5x speed
prometra replay --latest --speed 10x     # 10x speed
prometra replay --latest --speed instant # Instant rendering (default)
```

### 4. Interactive Step Mode
Pause after every event and wait for `Enter`:
```bash
prometra replay --latest --step
```

### 5. Multi-Format Output & Export
Output raw JSON, Markdown, or export directly to a file:
```bash
prometra replay --latest --json
prometra replay --latest --markdown
prometra replay --latest --export replay.md
prometra replay --latest --export replay.json
```

## Terminal UI Colorization & Status Icons

| Event Type | Status Icon | Rich Color |
| --- | --- | --- |
| **Session Started / Stopped** | 🚀 / 🏁 | `Cyan` |
| **AI Prompt** | 💡 | `Bright Cyan` |
| **AI Response** | 🤖 | `Green` |
| **Tool Invocation** | 🛠️ | `Yellow` |
| **Filesystem Changed** | 📝 | `Green` |
| **Git Commit** | 🔀 | `Blue` |
| **Error / Failed** | ❌ | `Red` |
