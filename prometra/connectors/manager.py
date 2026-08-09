import contextlib

from prometra.connectors.base import BaseConnector
from prometra.connectors.events import (
    ConnectorConnected,
    ConnectorDisconnected,
    EventBus,
)
from prometra.connectors.exceptions import ConnectorLifecycleError
from prometra.connectors.models import ConnectorConfig
from prometra.connectors.registry import ConnectorRegistry


class ConnectorManager:
    def __init__(self, registry: ConnectorRegistry, event_bus: EventBus):
        self.registry = registry
        self.event_bus = event_bus
        self.active_connectors: dict[str, BaseConnector] = {}

    def start_connector(self, name: str, config: ConnectorConfig) -> None:
        if name in self.active_connectors:
            return

        connector_class = self.registry.get(name)
        connector_instance = connector_class()

        try:
            connector_instance.initialize(config)
            connector_instance.connect()
            self.active_connectors[name] = connector_instance
            self.event_bus.publish(ConnectorConnected(connector_name=name))
        except Exception as e:  # noqa: BLE001
            raise ConnectorLifecycleError(f"Failed to start connector {name}: {e!s}")

    def stop_connector(self, name: str) -> None:
        if name not in self.active_connectors:
            return

        connector = self.active_connectors[name]
        with contextlib.suppress(Exception):
            connector.disconnect()
            connector.shutdown()

        del self.active_connectors[name]
        self.event_bus.publish(ConnectorDisconnected(connector_name=name))

    def stop_all(self) -> None:
        for name in list(self.active_connectors.keys()):
            self.stop_connector(name)

    def check_health(self) -> dict[str, dict]:
        health_status = {}
        for name, connector in self.active_connectors.items():
            try:
                status = connector.health()
                health_status[name] = status.model_dump()
            except Exception as e:  # noqa: BLE001
                health_status[name] = {
                    "state": "error",
                    "error_message": str(e),
                    "last_active": None,
                }
        return health_status
