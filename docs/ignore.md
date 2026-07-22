# Smart Ignore Rules (Prometra v1.6.2)

Prometra includes a lightweight, local-first **Smart Ignore Engine** (`IgnoreManager`) that prevents irrelevant file and directory activity (virtual environments, caches, build artifacts, editor metadata, etc.) from polluting your Timeline, Session Replay, and Analytics Dashboard.

## Default Ignore Rules

By default, Prometra automatically excludes the following paths:

### Directories
- `.git/`, `.prometra/`
- `.venv/`, `venv/`, `env/`
- `__pycache__/`
- `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`
- `.idea/`, `.vscode/`
- `coverage/`
- `build/`, `dist/`, `node_modules/`, `.eggs/`

### Files & Extensions
- `*.pyc`, `*.pyo`, `*.log`, `*.tmp`, `*.swp`
- `Thumbs.db`, `.DS_Store`

## Customizing Rules via `.prometraignore`

You can extend default ignore rules by creating a `.prometraignore` file in the root directory of your project.

### Example `.prometraignore`
```gitignore
# Exclude build outputs and logs
build/
dist/
logs/
data/

# Exclude specific file extensions
*.csv
*.zip
*.bak

# Exclude specific files
secret.key
local_settings.py
```

## How It Works

1. **Rule Merging**: Default ignore patterns and project-level `.prometraignore` patterns are automatically loaded and merged once upon tracker initialization.
2. **Comment & Blank Line Filtering**: Empty lines and lines starting with `#` (or inline `#` comments) are stripped.
3. **Cross-Platform Path Normalization**: Both Windows paths (`C:\Project\.venv\...`) and Linux paths (`/home/user/project/.venv/...`) are normalized to standard forward slashes (`/`) before pattern matching.
4. **Glob Matching**: Supports standard glob patterns (`*.csv`, `build/*`, `cache/**`) using Python's `fnmatch`.
5. **Zero Database Pollution**: Ignored file events are filtered out at the tracker level before being recorded, ensuring database queries remain fast and clean.
