# Contributing to Prometra

Thank you for your interest in contributing to **Prometra**! We welcome contributions from developers of all experience levels.

This guide outlines our development workflow, coding standards, and submission guidelines.

---

## Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating in our community.

---

## How Can I Contribute?

- **Reporting Bugs**: Open a bug report using our [Bug Template](.github/ISSUE_TEMPLATE/bug_report.md).
- **Suggesting Features**: Propose new ideas using our [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).
- **Submitting Pull Requests**: Fix issues or implement approved features.

---

## Development Setup

### 1. Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment (`venv` or `uv`)

### 2. Fork & Clone Repository

```bash
git clone https://github.com/your-username/Prometra.git
cd Prometra
```

### 3. Create Virtual Environment & Install Dependencies

```bash
python -m venv .venv

# On macOS/Linux
source .venv/bin/activate

# On Windows
.venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e ".[dev]"
```

---

## Running Tests

We maintain a strict 100% test pass policy. Before submitting any changes, verify the test suite:

```bash
pytest
```

To run tests with coverage reporting:

```bash
pytest --cov=prometra
```

---

## Coding Standards & Conventions

We enforce standard Python best practices across the repository:

- **Style Guide**: Strictly follow **PEP 8**.
- **Type Hints**: Use strict static type annotations (`typing` module / standard generic types).
- **Data Models**: Use standard dataclasses or Pydantic models for structured data.
- **CLI Commands**: Implement user-facing commands in `prometra/cli/commands.py` using `typer` and `rich`.
- **Modularity**: Keep functions focused, modular, and decoupled.
- **Local-First Privacy**: Never introduce network calls or external cloud dependencies into core features.

---

## Development Workflow

### 1. Branch Naming Conventions

Use descriptive branch names with appropriate prefixes:

- `feature/feature-name` (e.g. `feature/session-export`)
- `fix/issue-description` (e.g. `fix/timeline-date-parsing`)
- `docs/page-title` (e.g. `docs/cli-reference`)
- `refactor/component-name` (e.g. `refactor/query-builder`)

### 2. Commit Messages

Follow clear, imperative commit messages:

```
feat: add local CSV export option to timeline viewer
fix: handle timezone conversion edge case in SQLite storage
docs: update search CLI flag documentation in README
test: add test coverage for session comparison edge cases
```

### 3. Submitting Pull Requests

1. Ensure all **96+ unit tests** pass locally (`pytest`).
2. Include comprehensive unit tests for any new features or bug fixes.
3. Update relevant documentation in `docs/` and `README.md`.
4. Submit your pull request using our [Pull Request Template](.github/pull_request_template.md).

---

## Pull Request Checklist

- [ ] My code follows the repository's PEP8 and type hinting guidelines.
- [ ] All existing automated unit tests pass cleanly (`pytest`).
- [ ] I have added new unit tests for my changes.
- [ ] I have updated relevant documentation.
- [ ] No local-first privacy guarantees or zero-external-API rules are violated.
