from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ConnectorMetadata(BaseModel):
    name: str
    version: str
    supported_models: List[str] = Field(default_factory=list)
    supported_events: List[str] = Field(default_factory=list)

class ConnectorStatus(BaseModel):
    state: str = "disconnected"  # connected, disconnected, error
    error_message: Optional[str] = None
    last_active: Optional[str] = None

class ConnectorConfig(BaseModel):
    enabled: bool = True
    settings: Dict[str, Any] = Field(default_factory=dict)
