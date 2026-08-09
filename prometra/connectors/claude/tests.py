from prometra.connectors.claude.connector import ClaudeConnector
from prometra.connectors.claude.discovery import ClaudeDiscovery
from prometra.connectors.models import ConnectorConfig


def test_claude_discovery():
    meta = ClaudeDiscovery.get_metadata()
    assert "is_installed" in meta
    assert "version" in meta
    assert "executable_path" in meta
    assert "os_platform" in meta


def test_claude_connector_metadata():
    conn = ClaudeConnector()
    meta = conn.metadata()
    assert meta.name == "claude"
    assert "claude-3-5-sonnet" in meta.supported_models


def test_claude_connector_lifecycle():
    conn = ClaudeConnector()
    conn.initialize(ConnectorConfig())
    conn.connect()

    health = conn.health()
    assert health.state in ["connected", "error"]

    res = conn.capture()
    if health.state == "connected":
        assert res["status"] == "success"
        assert "context" in res
    else:
        assert res["status"] == "error"

    conn.disconnect()
    conn.shutdown()
