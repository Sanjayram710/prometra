<div align="center">

# 🚀 Prometra

### The Local-First Developer Intelligence Platform for AI-Assisted Software Development

*Git tells you **WHAT** changed. Prometra tells you **WHY** it changed.*

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/Tests-140%2B%20Passing-brightgreen.svg?style=for-the-badge&logo=pytest)](tests/)
[![Release](https://img.shields.io/badge/Release-v2.2.0-blue.svg?style=for-the-badge)](docs/insights.md)
[![GitHub Stars](https://img.shields.io/github/stars/Sanjayram710/prometra?style=for-the-badge&logo=github)](https://github.com/Sanjayram710/prometra)
[![GitHub Issues](https://img.shields.io/github/issues/Sanjayram710/prometra?style=for-the-badge&logo=github)](https://github.com/Sanjayram710/prometra/issues)

```
       ____  ____  ____  __  ___ _____ _____ ____   A
      / __ \/ __ \/ __ \/  |/  // ____/_   // __ \ / \
     / /_/ / /_/ / /_/ / /|_/ // __/   / // /_/ / / \
    / ____/ _, _/ ____/ /  / // /___  / // _, _/ /---\
   /_/   /_/ |_/_/   /_/  /_//_____/ /_//_/ |_| /_____\
```

---

</div>

## 📌 Project Overview

### What is Prometra?

**Prometra** is a local-first development intelligence and observability platform designed for AI-assisted software development. It bridges the critical gap between traditional source control (Git) and modern AI coding assistants (Claude Code, ChatGPT, Cursor, GitHub Copilot).

By monitoring filesystem changes, Git state, and AI interactions in real-time, Prometra constructs a comprehensive, chronological timeline of your development sessions.

### The Problem It Solves

Modern software development relies heavily on AI tools. While Git flawlessly records commits, it completely fails to preserve the critical context behind those commits:
- Which AI prompts generated this code?
- Which tool calls were made?
- How long did the session take?
- How much did the AI interaction cost?
- What exact file diffs occurred between checkpoints?

Prometra records all of this intelligence **100% locally** inside your repository using SQLite. No data is sent to external servers or cloud services.

### Who It Is For

- **Software Developers**: Track your workflow context, debug AI code edits, and search history instantly.
- **Engineering Managers & Tech Leads**: Inspect session productivity, AI token costs, and code churn without invasive cloud monitoring.
- **Open-Source Contributors**: Preserve development reasoning and session replays for pull request reviewers.

### Key Benefits

- **🔒 100% Local-First Privacy**: Zero external API dependencies, zero remote servers, zero cloud telemetry.
- **⚡ Sub-150ms Instant Search**: Query every file edit, commit, prompt, and tool call instantly.
- **🔍 File Diff Viewer**: Inspect line-by-line diffs between event sequence checkpoints locally.
- **📊 Session Comparison**: Compare development sessions side-by-side to evaluate productivity and code churn.
- **🎞️ Session Replay**: Replay coding sessions step-by-step with animated speed controls.
- **🛡️ Smart Ignore Rules**: Automatically ignores virtual environments, build artifacts, and `.prometraignore` patterns.

---

## 🏗️ Architecture

```
+-----------------------------------------------------------------------------------+
|                                 DEVELOPER CLI                                     |
|    prometra (init | start | stop | status | timeline | replay | search | diff...) |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             TRACKING ENGINE & CONNECTORS                          |
|        Filesystem Tracker  |  Git Tracker  |  Claude Connector  |  SDK          |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                             LOCAL PERSISTENT STORAGE                              |
|                          SQLite Database (.prometra/prometra.db)                   |
+-----------------------------------------------------------------------------------+
                                          |
      +-------------------+---------------+---------------+-------------------+
      |                   |               |               |                   |
      v                   v               v               v                   v
+-----------+       +-----------+   +-----------+   +-----------+       +-----------+
| TIMELINE  |       |  REPLAY   |   |  SEARCH   |   |   DIFF    |       | COMPARE   |
| Engine    |       | Engine    |   | Engine    |   | Engine    |       | Engine    |
+-----------+       +-----------+   +-----------+   +-----------+       +-----------+
      |                   |               |               |                   |
      +-------------------+---------------+---------------+-------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                               ANALYTICS DASHBOARD                                 |
|                Metrics | Edit Rankings | AI Token Usage | Productivity            |
+-----------------------------------------------------------------------------------+
```

---

## ✨ Features Matrix

| Feature | Description | Status |
| :--- | :--- | :--- |
| **Session Tracking** | Lifecycle tracking for continuous development sessions. | ✅ Active |
| **Filesystem Monitoring** | Real-time tracking of file creations, edits, and deletions. | ✅ Active |
| **Git Tracking** | Capture commits, branches, author details, and changed files. | ✅ Active |
| **Provider-Agnostic AI Events** | Standardized model for AI prompts, responses, tool calls, and costs. | ✅ Active |
| **Interactive Timeline** | Rich visual tables, session grouping, filters, and summary metrics. | ✅ Active |
| **Session Replay** | Step-by-step coding session reconstruction with speed controls (`1x`-`10x`). | ✅ Active |
| **Analytics Dashboard** | Comprehensive productivity insights, edit rankings, token costs, and peak hours. | ✅ Active |
| **Intelligent Search Engine** | Sub-150ms instant querying across all history with text highlighting. | ✅ Active |
| **File Diff Viewer** | Local line-by-line file diffing between event checkpoints (`prometra diff`). | ✅ Active |
| **Session Comparison** | Compare two sessions side-by-side (`prometra compare`) with productivity stats. | ✅ Active |
| **Smart Ignore Rules** | Excludes dependencies, virtual environments, build outputs, and `.prometraignore`. | ✅ Active |
| **AI Session Intelligence Engine** | Local-first session analysis, productivity scoring, pattern detection, and recommendations (`prometra insights`). | ✅ Active |
| **Interactive Terminal UI (TUI)** | Full-screen terminal app (`prometra ui`) with 9 views, keyboard navigation, and theme switcher. | ✅ Active |
| **Plugin System & Extension Framework** | Local-first extension framework (`prometra plugins`) with fault-isolated event hooks. | ✅ Active |
| **Connector SDK** | Extensible architecture for integrating external AI assistants. | ✅ Active |
| **Project Diagnostics** | Built-in environment and database diagnostics (`prometra doctor`). | ✅ Active |
| **Multi-Format Exporter** | Export reports and metrics to JSON, Markdown, HTML, CSV, and ZIP archives. | ✅ Active |

---

## 💻 Installation

### Prerequisites

- **Python 3.11+**
- **Git**

### Option 1: Install via PyPI / pip

```bash
pip install prometra
```

### Option 2: Install from Source (Editable Mode)

```bash
git clone https://github.com/Sanjayram710/prometra.git
cd prometra
pip install -e ".[dev]"
```

Verify installation:

```bash
prometra version
# Prometra Version: 2.0.0
```

---

## 🚀 Quick Start Guide

### 1. Initialize Prometra in Your Repository

```bash
prometra init
```

### 2. Start Background Tracking

```bash
prometra start
```

### 3. Explore Interactive Timeline

```bash
# View timeline events
prometra timeline

# View summary metrics
prometra timeline --summary

# Filter timeline by today or session
prometra timeline --today
prometra timeline --session sess-1
```

### 4. Search Event History

```bash
# Search for keywords in files, commits, and prompts
prometra search "authentication"

# Filter search by category or output JSON
prometra search "git" --type git
prometra search "auth" --json
```

### 5. Inspect File Diffs

```bash
# Diff latest two versions of a file
prometra diff hello.py

# Diff between specific event checkpoints
prometra diff hello.py --from-event 12 --to-event 20

# Export diff as Markdown
prometra diff hello.py --markdown
```

### 6. Compare Development Sessions

```bash
# Compare the latest two recorded sessions
prometra compare --latest

# Compare specific session IDs
prometra compare sess-a sess-b

# Export comparison as JSON
prometra compare sess-a sess-b --json
```

### 7. Replay Development Session

```bash
# Replay session step-by-step
prometra replay --session sess-1

# Replay at 5x speed
prometra replay --session sess-1 --speed 5x
```

### 8. Open Analytics Dashboard

```bash
prometra dashboard
```

---

## 🖼️ Visual Screenshots

*(Placeholders - Visual screenshots captured from Rich terminal interfaces)*

| Feature | Screenshot |
| :--- | :--- |
| **Analytics Dashboard** | ![Dashboard Screenshot](docs/images/dashboard.png) |
| **Intelligent Search** | ![Search Screenshot](docs/images/search.png) |
| **Interactive Timeline** | ![Timeline Screenshot](docs/images/timeline.png) |
| **File Diff Viewer** | ![Diff Screenshot](docs/images/diff.png) |
| **Session Comparison** | ![Compare Screenshot](docs/images/compare.png) |

---

## 📁 Project Structure

```
Prometra/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
├── docs/
│   ├── images/
│   │   └── README.md
│   ├── releases/
│   │   ├── v1.9.0.md
│   │   └── v2.0.0.md
│   ├── architecture.md
│   ├── cli.md
│   ├── community.md
│   ├── compare.md
│   ├── dashboard.md
│   ├── diff.md
│   ├── ignore.md
│   ├── replay.md
│   ├── search.md
│   └── timeline.md
├── prometra/
│   ├── ai/               # Provider-agnostic AI Event Model & translators
│   ├── analyzer/         # Stats and health calculation modules
│   ├── cli/              # Typer CLI application and commands
│   ├── compare/          # Session Comparison engine, renderer, formatter
│   ├── connectors/       # SDK and Claude connector implementation
│   ├── context/          # Pydantic context tree builder
│   ├── core/             # Configuration, time, schemas
│   ├── dashboard/        # Analytics Dashboard engine, renderer, formatter
│   ├── diff/             # File Diff Viewer engine, renderer, formatter
│   ├── replay/           # Session Replay engine, player, renderer
│   ├── reports/          # Report generation engine
│   ├── search/           # Intelligent Search engine, query builder
│   ├── storage/          # SQLAlchemy SQLite models & storage
│   ├── timeline/         # Timeline engine, queries, formatter, renderer
│   └── tracker/          # Filesystem, Git, and Ignore rules trackers
├── tests/                # 96 Unit tests
├── CHANGELOG.md          # Keep a Changelog documentation
├── CONTRIBUTING.md       # Contribution guidelines & workflow
├── CODE_OF_CONDUCT.md    # Contributor Covenant v2.1
├── SECURITY.md           # Security policy & local privacy guarantees
├── LICENSE               # MIT License
├── pyproject.toml        # Project metadata and dependencies
└── README.md             # Project documentation
```

---

## 🧪 Testing

Prometra includes a comprehensive automated test suite built with `pytest`:

```bash
# Run full test suite (96 passing tests)
pytest

# Run tests with coverage output
pytest --cov=prometra
```

Current Test Status: **96 / 96 Tests Passing (100% Pass Rate)**

---

## 🗺️ Roadmap

### Completed Milestones

- [x] **v1.0 Local Tracking**: Filesystem monitoring, Git commits, SQLite storage, CLI.
- [x] **v1.1 Connector SDK**: Extensible plugin system & dynamic connector registry.
- [x] **v1.2 Claude Connector**: Real-time integration with Claude Code actions.
- [x] **v1.3 AI Event Model**: Provider-agnostic Pydantic AI event structure.
- [x] **v1.4 Interactive Timeline**: Visual tables, session grouping, and timeline summary metrics.
- [x] **v1.5 Session Replay Engine**: Animated session playback with speed controls (`1x`-`10x`).
- [x] **v1.6 Analytics Dashboard**: Development insights, token consumption, and cost calculations.
- [x] **v1.6.2 Smart Ignore Rules**: `.prometraignore` file support & automatic exclusion.
- [x] **v1.7 Intelligent Search Engine**: Instant keyword search across SQLite event history.
- [x] **v1.8 File Diff Viewer**: Local line-by-line diffing between event sequence checkpoints.
- [x] **v1.9 Session Comparison**: Side-by-side session productivity & code churn comparison.
- [x] **v2.0 Open Source Release**: Repository polish, community governance, release notes, and documentation overhaul.

### Future v2.x Roadmap

- [ ] **v2.1 Multi-Connector Support**: OpenAI Codex, GitHub Copilot, and Ollama connectors.
- [ ] **v2.2 Web Visualizer GUI**: Optional local browser dashboard built with React / Next.js.
- [ ] **v2.3 Team Session Merging**: Exportable session archives for team code reviews.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) and [Community Guidelines](docs/community.md) for details on setting up your environment, coding standards, and submitting pull requests.

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

---

## 🔒 Security & Privacy

Prometra is built with privacy as a foundational principle. Read our [Security Policy](SECURITY.md) for details on our local privacy guarantees and security reporting procedures.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
