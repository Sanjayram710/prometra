from typing import Any

from pydantic import BaseModel, Field


class ConnectorMetadata(BaseModel):
    name: str
    version: str
    supported_models: list[str] = Field(default_factory=list)
    supported_events: list[str] = Field(default_factory=list)


class ConnectorStatus(BaseModel):
    state: str = "disconnected"  # connected, disconnected, error
    error_message: str | None = None
    last_active: str | None = None


class ConnectorConfig(BaseModel):
    enabled: bool = True
    settings: dict[str, Any] = Field(default_factory=dict)
