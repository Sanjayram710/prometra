from prometra.connectors.base import BaseConnector
from prometra.connectors.events import EventBus, SessionStarted
from prometra.connectors.manager import ConnectorManager
from prometra.connectors.models import (
    ConnectorConfig,
    ConnectorMetadata,
    ConnectorStatus,
)
from prometra.connectors.registry import ConnectorRegistry


class DummyConnector(BaseConnector):
    def __init__(self):
        self.is_connected = False
        self.is_initialized = False

    def initialize(self, config: ConnectorConfig) -> None:
        self.is_initialized = True

    def connect(self) -> None:
        self.is_connected = True

    def disconnect(self) -> None:
        self.is_connected = False

    def capture(self, **kwargs):
        return {"captured": True}

    def metadata(self) -> ConnectorMetadata:
        return ConnectorMetadata(name="dummy", version="1.0")

    def health(self) -> ConnectorStatus:
        return ConnectorStatus(
            state="connected" if self.is_connected else "disconnected"
        )

    def supports(self, capability: str) -> bool:
        return capability == "test"

    def shutdown(self) -> None:
        pass


def test_registry_registration():
    registry = ConnectorRegistry()
    registry.register("dummy", DummyConnector)
    assert "dummy" in registry.list()
    assert registry.get("dummy") == DummyConnector


def test_manager_lifecycle():
    registry = ConnectorRegistry()
    registry.register("dummy", DummyConnector)
    bus = EventBus()

    manager = ConnectorManager(registry, bus)
    manager.start_connector("dummy", ConnectorConfig())

    assert "dummy" in manager.active_connectors
    assert manager.active_connectors["dummy"].is_connected == True

    manager.stop_connector("dummy")
    assert "dummy" not in manager.active_connectors


def test_event_bus():
    bus = EventBus()
    received = []

    def callback(event):
        received.append(event)

    bus.subscribe(SessionStarted, callback)
    bus.publish(SessionStarted(session_id="s1", project_id="p1"))

    assert len(received) == 1
    assert received[0].session_id == "s1"
