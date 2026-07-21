import sys
from typing import Dict, List, Type
from prometra.connectors.base import BaseConnector
from prometra.connectors.exceptions import ConnectorRegistrationError

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    # Requires importlib_metadata for Python < 3.10
    from importlib_metadata import entry_points # type: ignore

class ConnectorRegistry:
    """Registry to discover and hold connector classes."""
    
    def __init__(self):
        self._connectors: Dict[str, Type[BaseConnector]] = {}

    def register(self, name: str, connector_class: Type[BaseConnector]) -> None:
        """Manually register a connector class."""
        if name in self._connectors:
            raise ConnectorRegistrationError(f"Connector '{name}' is already registered.")
        
        self.validate(connector_class)
        self._connectors[name] = connector_class

    def unregister(self, name: str) -> None:
        """Unregister a connector class."""
        if name in self._connectors:
            del self._connectors[name]

    def get(self, name: str) -> Type[BaseConnector]:
        """Get a registered connector class by name."""
        if name not in self._connectors:
            raise KeyError(f"Connector '{name}' not found.")
        return self._connectors[name]

    def list(self) -> List[str]:
        """List all registered connector names."""
        return list(self._connectors.keys())

    def validate(self, connector_class: Type[BaseConnector]) -> None:
        """Validate that the class properly implements BaseConnector."""
        if not issubclass(connector_class, BaseConnector):
            raise ConnectorRegistrationError(f"{connector_class.__name__} must inherit from BaseConnector.")
            
    def discover_plugins(self) -> None:
        """Discover external plugins via importlib.metadata entry_points."""
        try:
            # Using a specific entry point group: prometra.connectors
            eps = entry_points(group="prometra.connectors")
            for ep in eps:
                try:
                    plugin_class = ep.load()
                    name = ep.name
                    if name not in self._connectors:
                        self.register(name, plugin_class)
                except Exception:
                    pass
        except Exception:
            # Fallback if entry_points group param is not supported
            pass
