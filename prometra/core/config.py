
from pydantic import BaseModel, Field


class ProjectConfig(BaseModel):
    name: str = "Default Project"
    root: str = "."
    description: str | None = None
    client: str | None = None
    environment: str = "development"


class TrackingConfig(BaseModel):
    enabled: bool = True
    mode: str = "metadata_only"
    session_auto_start: bool = False
    filesystem: bool = True
    git: bool = True
    prompts: bool = False
    responses: bool = False
    tool_calls: bool = False
    capture_content: bool = False
    include: list[str] = Field(default_factory=lambda: ["src/**", "tests/**"])
    exclude: list[str] = Field(
        default_factory=lambda: [
            ".git/**",
            ".venv/**",
            "node_modules/**",
            "dist/**",
            "build/**",
            ".prometra/**",
        ]
    )
    debounce_ms: int = 250
    max_queue_size: int = 10000


class GitConfig(BaseModel):
    enabled: bool = True
    repository: str = "auto"
    branch: str = "current"
    capture_diffs: str = "metadata_only"
    capture_merge_history: bool = True
    capture_tags: bool = True


class FilesystemConfig(BaseModel):
    enabled: bool = True
    watch: bool = True
    poll_interval_ms: int = 500
    hash_files: bool = False
    record_content: bool = False
    max_file_size_mb: int = 10


class StorageConfig(BaseModel):
    backend: str = "sqlite"
    database_path: str = ".prometra/prometra.db"
    artifact_path: str = ".prometra/artifacts"
    cache_path: str = ".prometra/cache"
    encrypt_sensitive_content: bool = True
    encryption_key_env: str = "PROMETRA_ENCRYPTION_KEY"
    redact_secrets: bool = True
    retention_days: int = 365
    max_database_size_mb: int = 2048


class PrometraConfig(BaseModel):
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    tracking: TrackingConfig = Field(default_factory=TrackingConfig)
    git: GitConfig = Field(default_factory=GitConfig)
    filesystem: FilesystemConfig = Field(default_factory=FilesystemConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
