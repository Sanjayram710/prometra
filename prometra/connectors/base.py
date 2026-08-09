from abc import ABC, abstractmethod
from typing import Any

from prometra.connectors.models import (
    ConnectorConfig,
    ConnectorMetadata,
    ConnectorStatus,
)


class BaseConnector(ABC):
    """Abstract Base Class for all Prometra Connectors."""

    @abstractmethod
    def initialize(self, config: ConnectorConfig) -> None:
        """Initialize the connector with configuration."""

    @abstractmethod
    def connect(self) -> None:
        """Establish connection or spin up resources."""

    @abstractmethod
    def disconnect(self) -> None:
        """Teardown connection and release resources."""

    @abstractmethod
    def capture(self, **kwargs) -> dict[str, Any]:
        """Capture state or perform an action specific to the connector."""

    @abstractmethod
    def metadata(self) -> ConnectorMetadata:
        """Return the connector's metadata."""

    @abstractmethod
    def health(self) -> ConnectorStatus:
        """Return the connector's current health status."""

    @abstractmethod
    def supports(self, capability: str) -> bool:
        """Check if connector supports a specific capability."""

    @abstractmethod
    def shutdown(self) -> None:
        """Perform a clean shutdown."""
