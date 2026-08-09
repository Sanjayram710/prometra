from prometra.connectors.models import ConnectorMetadata


class ClaudeMetadata(ConnectorMetadata):
    executable_path: str = ""
    os_platform: str = ""
