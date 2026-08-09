from prometra.connectors.models import ConnectorMetadata


class MCPMetadata(ConnectorMetadata):
    server_url: str = "mcp://localhost:8000"
    connected_models: list[str] = ["gemini-via-mcp", "claude-via-mcp", "gpt-via-mcp"]
