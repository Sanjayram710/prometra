from prometra.connectors.models import ConnectorMetadata


class GPTMetadata(ConnectorMetadata):
    api_key_set: bool = False
    default_model: str = "gpt-4o"
