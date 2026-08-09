from prometra.connectors.models import ConnectorMetadata


class GeminiMetadata(ConnectorMetadata):
    api_key_set: bool = False
    default_model: str = "gemini-2.5-flash"
