import fnmatch
import os

DEFAULT_IGNORE_PATTERNS = [
    # Directories
    ".git",
    ".git/*",
    ".prometra",
    ".prometra/*",
    ".venv",
    ".venv/*",
    "venv",
    "venv/*",
    "env",
    "env/*",
    "__pycache__",
    "__pycache__/*",
    ".pytest_cache",
    ".pytest_cache/*",
    ".mypy_cache",
    ".mypy_cache/*",
    ".ruff_cache",
    ".ruff_cache/*",
    ".idea",
    ".idea/*",
    ".vscode",
    ".vscode/*",
    "coverage",
    "coverage/*",
    "build",
    "build/*",
    "dist",
    "dist/*",
    "node_modules",
    "node_modules/*",
    ".eggs",
    ".eggs/*",
    # Files and Extensions
    "*.pyc",
    "*.pyo",
    "*.log",
    "*.tmp",
    "*.swp",
    "Thumbs.db",
    ".DS_Store",
]


class IgnoreManager:
    """Manages filesystem ignore rules (default + .prometraignore)."""

    def __init__(self, root_dir: str | None = None):
        self.root_dir = os.path.abspath(root_dir) if root_dir else None
        self.patterns: list[str] = []
        self._load_rules()

    def _load_rules(self):
        """Load default ignore rules and merge optional .prometraignore."""
        # 1. Add default patterns
        self.patterns = list(DEFAULT_IGNORE_PATTERNS)

        # 2. Check for .prometraignore
        if self.root_dir:
            ignore_file = os.path.join(self.root_dir, ".prometraignore")
            if os.path.isfile(ignore_file):
                try:
                    with open(ignore_file, "r", encoding="utf-8") as f:
                        for line in f:
                            # Strip inline comments
                            if "#" in line:
                                line = line.split("#", 1)[0]
                            cleaned = line.strip()
                            if cleaned and cleaned not in self.patterns:
                                self.patterns.append(cleaned)
                except OSError:
                    pass

    def should_ignore(self, path: str, root_dir: str | None = None) -> bool:
        """
        Check whether a path should be ignored according to loaded rules.
        Handles both Windows and Linux paths cleanly.
        """
        if not path:
            return False

        effective_root = os.path.abspath(root_dir) if root_dir else self.root_dir

        # Normalize slashes to forward slashes for cross-platform matching
        norm_path = path.replace("\\", "/")

        # Calculate relative path if absolute path provided
        rel_path = norm_path
        if effective_root:
            norm_root = effective_root.replace("\\", "/")
            if norm_path.startswith(norm_root):
                rel_path = norm_path[len(norm_root) :].lstrip("/")

        filename = os.path.basename(rel_path)
        parts = rel_path.split("/")

        # Check directory segment matches
        for part in parts[:-1]:  # Check parent directory names
            if part in [
                ".git",
                ".prometra",
                ".venv",
                "venv",
                "env",
                "__pycache__",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
                ".idea",
                ".vscode",
                "coverage",
                "build",
                "dist",
                "node_modules",
                ".eggs",
            ]:
                return True

        # Match against patterns list using fnmatch
        for pattern in self.patterns:
            pat_clean = pattern.rstrip("/").replace("\\", "/")

            if pattern.endswith("/") and (
                rel_path.startswith(pat_clean + "/")
                or any(part == pat_clean for part in parts[:-1])
            ):
                return True

            # Direct fnmatch on filename or relative path
            if fnmatch.fnmatch(filename, pat_clean) or fnmatch.fnmatch(
                rel_path, pat_clean
            ):
                return True

            # Match directory glob patterns like build/*, dist/*, .venv/*
            if fnmatch.fnmatch(rel_path, pat_clean + "/*") or fnmatch.fnmatch(
                rel_path, pat_clean + "/**"
            ):
                return True

        return False
