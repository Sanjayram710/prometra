from prometra.connectors.models import ConnectorMetadata


class AntigravityMetadata(ConnectorMetadata):
    api_key_set: bool = False
    default_model: str = "antigravity-flash"
