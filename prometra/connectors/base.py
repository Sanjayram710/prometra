from abc import ABC, abstractmethod
from typing import Dict, Any
from prometra.connectors.models import ConnectorMetadata, ConnectorStatus, ConnectorConfig

class BaseConnector(ABC):
    """Abstract Base Class for all Prometra Connectors."""
    
    @abstractmethod
    def initialize(self, config: ConnectorConfig) -> None:
        """Initialize the connector with configuration."""
        pass

    @abstractmethod
    def connect(self) -> None:
        """Establish connection or spin up resources."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Teardown connection and release resources."""
        pass

    @abstractmethod
    def capture(self, **kwargs) -> Dict[str, Any]:
        """Capture state or perform an action specific to the connector."""
        pass

    @abstractmethod
    def metadata(self) -> ConnectorMetadata:
        """Return the connector's metadata."""
        pass

    @abstractmethod
    def health(self) -> ConnectorStatus:
        """Return the connector's current health status."""
        pass

    @abstractmethod
    def supports(self, capability: str) -> bool:
        """Check if connector supports a specific capability."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Perform a clean shutdown."""
        pass
