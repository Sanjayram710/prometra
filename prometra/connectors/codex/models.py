from prometra.connectors.models import ConnectorMetadata


class CodexMetadata(ConnectorMetadata):
    api_key_set: bool = False
    default_model: str = "codex-davinci"
