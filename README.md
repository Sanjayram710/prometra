# Prometra

The Intelligence Layer for AI-Assisted Software Development.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-72_Passing-success.svg)](tests/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

## Table of Contents
- [What is Prometra?](#what-is-prometra)
- [Why Prometra?](#why-prometra)
- [Project Status](#project-status)
- [Architecture](#architecture)
- [Core Features](#core-features)
- [Intelligent Search Engine](#intelligent-search-engine)
- [Smart Ignore Rules](#smart-ignore-rules)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Screenshots](#screenshots)
- [Connector System](#connector-system)
- [AI Event Model](#ai-event-model)
- [Project Structure](#project-structure)
- [Architecture Principles](#architecture-principles)
- [Development](#development)
- [Testing](#testing)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## What is Prometra?

**Git tells you *WHAT* changed. Prometra tells you *WHY* it changed.**

Prometra is a local-first development intelligence platform that bridges the gap between your source control and your AI coding tools. By tracking filesystem changes, Git state, and AI interactions in real-time, Prometra builds a comprehensive, chronological timeline of your development sessions. 

All your development context—AI interactions, development sessions, filesystem changes, Git activity, timelines, and reports—is recorded entirely **locally**.

---

## Why Prometra?

Modern software development relies heavily on AI. While Git flawlessly records commits, it completely fails to preserve the critical context behind those commits: the prompts, the AI tool choices, and the development workflow. Prometra fills this exact gap. It ensures that the intelligence and reasoning behind your AI-assisted code are never lost.

---

## Project Status

<<<<<<< HEAD
**Current Release (v1.9.0):**
=======
**Current Release (v1.8.0):**
>>>>>>> 2761a9f97943060944da3d25eb29b5bece7b3423
- ✅ Local-first Tracking
- ✅ Git Tracking
- ✅ SQLite Storage
- ✅ Connector SDK
- ✅ Claude Connector
- ✅ Provider-Agnostic AI Event Model
- ✅ Interactive Timeline Explorer
- ✅ End-to-End AI Event Persistence
- ✅ Session Replay Engine
- ✅ Analytics Dashboard
- ✅ Smart Ignore Rules (`.prometraignore`)
- ✅ Intelligent Search Engine (`prometra search`)
- ✅ File Diff Viewer (`prometra diff`)
<<<<<<< HEAD
- ✅ Session Comparison (`prometra compare`)

**Testing:** 96 Automated Tests Passing  
=======

**Testing:** 84 Automated Tests Passing  
>>>>>>> 2761a9f97943060944da3d25eb29b5bece7b3423
**Status:** Actively Developed

---

## Architecture

```mermaid
flowchart TD
    Dev[Developer] --> CLI[Tracking]
    CLI --> SM[Context]
    SM --> TE[Connectors]
    TE --> EventM[Generic Events]
    EventM --> DB[(SQLite)]
    DB --> Analytics[Analytics]
    DB --> Search[Intelligent Search]
    DB --> Diff[File Diff Viewer]
<<<<<<< HEAD
    DB --> Compare[Session Comparison]
```

**Data Flow:**
Developers interact with their codebase while Prometra seamlessly monitors activity in the background. The core system gathers context, delegates tool execution to external AI Connectors, translates all specialized actions into a Generic AI Event Model, and persists everything to a local SQLite database for downstream analytics, reporting, instant search queries, local file diff viewing, and session comparison.
=======
```

**Data Flow:**
Developers interact with their codebase while Prometra seamlessly monitors activity in the background. The core system gathers context, delegates tool execution to external AI Connectors, translates all specialized actions into a Generic AI Event Model, and persists everything to a local SQLite database for downstream analytics, reporting, instant search queries, and local file diff viewing.
>>>>>>> 2761a9f97943060944da3d25eb29b5bece7b3423

---

## Core Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Session Tracking** | Graceful lifecycle tracking of continuous development sessions. | ✅ Active |
| **Filesystem Tracking** | Real-time monitoring of file modifications, creations, and deletions. | ✅ Active |
| **Git Tracking** | Capture commits, branch states, and repository metadata. | ✅ Active |
| **SQLite Storage** | Local-first, schema-driven persistent storage. | ✅ Active |
| **Interactive Timeline** | Rich visual tables, filtering (`--session`, `--type`, `--connector`, `--search`, `--today`), grouping (`--group session`), summary statistics (`--summary`), and multi-format exports (`--export`). | ✅ Active |
| **Session Replay** | Reconstruct and play back coding sessions step-by-step or with animated playback speeds (`1x`, `2x`, `5x`, `10x`, `instant`). | ✅ Active |
| **Analytics Dashboard** | Interactive development insights (Sessions, File Edit rankings, Top AI Models, Token Usage, Cost estimation, Peak hours) with time window filters (`--today`, `--week`, `--month`). | ✅ Active |
| **Intelligent Search** | Sub-150ms instant querying across all recorded events (Filesystem, Git commits, AI prompts, AI responses, Tool calls, Session lifecycle) with filtering (`--type`, `--session`, `--today`, `--week`, `--since`, `--until`, `--limit`), text highlighting, and JSON/Markdown export options. | ✅ Active |
| **File Diff Viewer** | Local line-by-line file diffing between tracked event checkpoints (`prometra diff`) with session filtering (`--session`), event range selection (`--from-event`, `--to-event`), context options (`--context`), and JSON/Markdown exports. | ✅ Active |
<<<<<<< HEAD
| **Session Comparison** | Compare two sessions side-by-side (`prometra compare`), comparing files created/modified/deleted, commits, AI interactions, duration, productivity rates, and timeline differences, with `--latest` and JSON/Markdown/Export options. | ✅ Active |
=======
>>>>>>> 2761a9f97943060944da3d25eb29b5bece7b3423
| **Smart Ignore Rules** | Excludes virtual environments (`.venv`), dependencies (`node_modules`), caches (`__pycache__`), build outputs, and `.prometraignore` patterns. | ✅ Active |
| **Project Analytics** | Codebase health, risk level, and statistical insights. | ✅ Active |
| **Report Generation** | Multi-format (Markdown, HTML, JSON, CSV) intelligence reports. | ✅ Active |
| **Export System** | Compress and package project intelligence into portable archives. | ✅ Active |
| **Connector SDK** | Extensible interface for integrating external AI tools. | ✅ Active |
| **Connector Registry** | Dynamic Python discovery for external plugins. | ✅ Active |
| **Context Engine** | Generates strict Pydantic context trees from raw SQLite history. | ✅ Active |
| **Event Bus** | Pub/Sub architecture for decoupling tracking from AI events. | ✅ Active |

---

## File Diff Viewer

Inspect line-by-line changes between tracked file versions locally:

```bash
# Diff latest two recorded versions of a file
prometra diff hello.py

# Diff between specific event checkpoints
prometra diff hello.py --from-event 12 --to-event 20

# Filter file history by session ID
prometra diff hello.py --session sess-1

# Export diff results as JSON or Markdown
prometra diff hello.py --json
prometra diff hello.py --markdown
```

---

## Intelligent Search Engine

Instantly search every recorded event stored inside your local SQLite database:

```bash
# Keyword search across filesystem, commits, and prompts
prometra search "hello.py"
prometra search "authentication"
prometra search "jwt"

# Filter by category, time range, and export format
prometra search "git" --type git
prometra search "api" --today
prometra search "auth" --json
prometra search "README" --markdown
```

---

## Smart Ignore Rules

Prometra automatically excludes irrelevant files and directories from tracking (e.g. `.venv/`, `node_modules/`, `__pycache__/`, `.git/`, `build/`, `dist/`, `*.log`, `*.tmp`).

You can customize project-specific ignore rules by creating a `.prometraignore` file in your repository root:

```gitignore
# Exclude build outputs and logs
build/
dist/
logs/
data/

# Exclude specific file types
*.csv
*.zip
```

---

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/<username>/Prometra
cd Prometra
pip install -e .
```

Verify your installation:

```bash
prometra --help
```

---

## Quick Start

Prometra operates seamlessly alongside your existing workflow.

1. **Initialize a Project**  
   Set up Prometra in your current repository.
   ```bash
   prometra init
   ```
2. **Start a Session**  
   Begin tracking filesystem and AI activity.
   ```bash
   prometra start
   ```
3. **Work as Usual**  
   Perform your coding tasks, commit via Git, and use your AI tools.
4. **Stop the Session**  
   Gracefully end tracking.
   ```bash
   prometra stop
   ```
5. **Analyze the Project**  
   Generate codebase health and risk analytics.
   ```bash
   prometra analyze
   ```
6. **Generate a Report**  
   Export comprehensive development intelligence.
   ```bash
   prometra report --format markdown
   ```
7. **View Timeline**  
   Review the chronological sequence of your session.
   ```bash
   prometra timeline
   ```
8. **View History**  
   Review past development sessions.
   ```bash
   prometra history
   ```

---

## Screenshots

### Timeline
<!-- Add screenshot -->

### Connector CLI
<!-- Add screenshot -->

### Reports
<!-- Add screenshot -->

---

## Connector System

Prometra Version 2 introduces a decoupled **Connector SDK** allowing external AI providers to interface with the core tracking engine without modifying base code. Features include dynamic discovery, health checks, enabling/disabling via CLI, and rigorous schema validation.

| Connector | Purpose | Status |
|-----------|---------|--------|
| **Claude Code** | Native integration for Anthropic's Claude Code CLI. | ✅ Implemented |
| **Codex** | OpenAI Codex integration. | 🚧 Planned |
| **Gemini** | Google Gemini integration. | 🚧 Planned |
| **Cursor** | Cursor IDE telemetry integration. | 🚧 Planned |

---

## AI Event Model

To maintain a purely decoupled analytical core, Prometra enforces a **Provider-Agnostic Event Model**. Timeline generation, Reports, Analytics, and the SQLite storage engine *only* consume generic events. This future-proofs Prometra, allowing new AI plugins to be added without rewriting the core engine.

| Claude Event | Translates To |
|--------------|---------------|
| `ClaudeSessionStarted` | `SessionStarted` |
| `ClaudeSessionStopped` | `SessionEnded` |
| `ClaudeHealthChanged` | `ErrorOccurred` |

---

## Project Structure

```text
prometra/
├── prometra/
│   ├── ai/                 # Generic Event Model & Translators
│   ├── analyzer/           # Project Health & Statistics
│   ├── cli/                # Typer CLI Commands
│   ├── connectors/         # SDK, Registry, and Claude Implementation
│   ├── context/            # Context Builder Engine
│   ├── core/               # Configuration and Utilities
│   ├── reports/            # Markdown, HTML, CSV, JSON Exporters
│   ├── storage/            # SQLite Models and Engine
│   ├── timeline/           # Chronological Event Sequencing
│   └── tracker/            # Session, Filesystem, and Git Trackers
├── tests/                  # Pytest Suite
├── docs/                   # Documentation Artifacts
├── pyproject.toml          # Packaging and Entry Points
└── README.md
```

---

## Architecture Principles

| Principle | Description |
|-----------|-------------|
| **Local-first** | All tracking, storage, and analysis run locally on your machine. |
| **SOLID** | Strict adherence to single responsibility and interface segregation. |
| **Dependency Injection** | Core components accept interfaces dynamically rather than hardcoding. |
| **Plugin Architecture** | Extending Prometra requires zero core modifications. |
| **Provider-Agnostic Design** | Core systems only understand generic AI events. |
| **Event-Driven Design** | The Event Bus decouples publishers from subscribers. |

---

## Development

Formatting and linting are maintained via `black` and `isort`.

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black prometra/ tests/
isort prometra/ tests/
```

---

## Testing

Prometra uses `pytest` for rigorous testing. Every Pull Request must pass the full test suite.

```bash
pytest tests/
```

> [!NOTE]
> **Current Status**: 21 tests passing (100% coverage across core mechanics, CLI, context building, and event translation).

---

## Roadmap

### Completed Milestones
- **v1.0** - Local-first Tracking, Git, SQLite 
- **v1.1** - Connector SDK
- **v1.2** - Claude Connector & Generic AI Event Model

### Upcoming
- **v2.0** - Interactive Timeline
- **v2.1** - Session Replay
- **v2.2** - Analytics Dashboard
- **v2.3** - Prompt Search
- **v2.4** - Diff Viewer
- **v3.0** - VS Code Extension

### Future Connectors
- Codex Connector
- Gemini Connector
- Cursor Connector

---

## Contributing

We welcome contributions from the community! To get started:
1. **Fork** the repository.
2. Create a new **Feature Branch** (`git checkout -b feature/amazing-feature`).
3. Commit your changes and run the **Tests** (`pytest tests/`).
4. Open a **Pull Request** with a detailed description of your architectural decisions.

---

## License

MIT
