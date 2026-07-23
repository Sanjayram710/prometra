# Changelog

All notable changes to **Prometra** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-07-23

### Added
- Complete open-source documentation overhaul across `README.md` and `docs/`.
- Repository governance files: `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (v2.1), `SECURITY.md`.
- Issue templates (`bug_report.md`, `feature_request.md`) and Pull Request template.
- Release documentation (`docs/releases/v1.9.0.md` & `v2.0.0.md`) and screenshot asset guide (`docs/images/README.md`).
- Community guidelines in `docs/community.md`.
- Shields.io status badges and ASCII architecture diagram.

### Changed
- Refactored `README.md` into a production-grade open-source landing page.
- Verified 96 automated unit tests passing.

---

## [1.9.0] - 2026-07-23

### Added
- **Session Comparison Engine** (`prometra compare` CLI command).
- Side-by-side session metrics (files created/modified/deleted, commits, AI events, duration).
- Productivity statistics (events per minute, files changed per minute, commits per hour).
- Support for `--latest`, `--json`, `--markdown`, and `--export PATH`.

---

## [1.8.0] - 2026-07-23

### Added
- **File Diff Viewer** (`prometra diff` CLI command).
- Sub-50ms local file diffing between tracked event sequence checkpoints.
- Uses Python stdlib `difflib.unified_diff` and `SequenceMatcher.get_opcodes`.
- Support for `--session`, `--from-event`, `--to-event`, `--latest`, `--context`, `--json`, `--markdown`.

---

## [1.7.0] - 2026-07-23

### Added
- **Intelligent Search Engine** (`prometra search` CLI command).
- Sub-150ms instant querying across all SQLite event history.
- Filtering by category (`--type`), time ranges (`--today`, `--week`, `--since`, `--until`), and multi-format exports.

---

## [1.6.2] - 2026-07-23

### Added
- **Smart Ignore Rules** (`.prometraignore`).
- Automatic exclusion of virtual environments, dependencies, caches, and build outputs.

---

## [1.6.0] - 2026-07-23

### Added
- **Analytics Dashboard** (`prometra dashboard`).
- Interactive development insights (Sessions, File Edit rankings, Top AI Models, Token Usage, Cost estimation, Peak hours).

---

## [1.5.0] - 2026-07-23

### Added
- **Session Replay Engine** (`prometra replay`).
- Step-by-step session playback with speed controls (`1x`, `2x`, `5x`, `10x`, `instant`).

---

## [1.4.0] - 2026-07-23

### Added
- **Interactive Timeline Explorer** (`prometra timeline`).
- Visual tables, event filtering, session grouping, and summary metrics.

---

## [1.3.0] - 2026-07-23

### Added
- **Provider-Agnostic AI Event Model**.
- Unified Pydantic AI event structures and event bus translation.

---

## [1.2.0] - 2026-07-23

### Added
- **Claude Connector Integration**.
- Automatic recording of Claude Code events and prompts.

---

## [1.1.0] - 2026-07-23

### Added
- **Connector SDK & Registry**.
- Dynamic plugin system for external AI tools.

---

## [1.0.0] - 2026-07-23

### Added
- Initial Release of Prometra.
- Local tracking engine for filesystem and Git activity.
- SQLite persistent storage layer.
- CLI interface (`prometra init`, `start`, `stop`, `status`, `history`, `doctor`).
