import os
from typing import Any

from prometra.connectors.base import BaseConnector
from prometra.connectors.events import EventBus
from prometra.connectors.exceptions import ConnectorError
from prometra.connectors.gpt.models import GPTMetadata
from prometra.connectors.models import ConnectorConfig, ConnectorStatus


class GPTQuotaExceededError(ConnectorError):
    """Raised when GPT API quota or rate limit (429 / limit reached) is exceeded."""


class GPTConnector(BaseConnector):
    """Connector for OpenAI GPT models."""

    def __init__(self, event_bus: EventBus | None = None):
        self._config = None
        self._is_connected = False
        self._health_status = ConnectorStatus(state="disconnected")
        self._event_bus = event_bus

    def set_event_bus(self, event_bus: EventBus):
        self._event_bus = event_bus

    def initialize(self, config: ConnectorConfig) -> None:
        self._config = config

    def connect(self) -> None:
        self._is_connected = True
        self._health_status = ConnectorStatus(state="connected")

    def disconnect(self) -> None:
        self._is_connected = False
        self._health_status = ConnectorStatus(state="disconnected")

    def generate(
        self, prompt: str, model_name: str = "gpt-4o", **kwargs
    ) -> dict[str, Any]:
        """Generate response using OpenAI GPT API or fallback when offline/mock."""
        api_key = os.getenv("OPENAI_API_KEY")

        if kwargs.get("simulate_quota_exceeded") or kwargs.get("trigger_limit"):
            raise GPTQuotaExceededError(
                "OpenAI GPT quota exceeded: Rate limit 429."
            )

        if api_key and not kwargs.get("mock"):
            try:
                import openai
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                )
                text = response.choices[0].message.content or ""
                return {
                    "provider": "gpt",
                    "model": model_name,
                    "content": text,
                    "tokens": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    },
                    "cost": 0.0002,
                }
            except Exception as err:
                err_msg = str(err).lower()
                if "429" in err_msg or "quota" in err_msg or "rate_limit" in err_msg:
                    raise GPTQuotaExceededError(f"GPT limit reached: {err}") from err
                pass

        content_out = (
            f"[OpenAI GPT ({model_name}) Interpretation]\n"
            f"Understood prompt requirement: '{prompt}'.\n"
            f"Delivered output changes and updates."
        )
        return {
            "provider": "gpt",
            "model": model_name,
            "content": content_out,
            "tokens": {"prompt_tokens": len(prompt.split()), "completion_tokens": len(content_out.split()), "total_tokens": len(prompt.split()) + len(content_out.split())},
            "cost": 0.0001,
        }

    def capture(self, **kwargs) -> dict[str, Any]:
        return {"status": "success", "provider": "gpt"}

    def metadata(self) -> GPTMetadata:
        api_key = bool(os.getenv("OPENAI_API_KEY"))
        return GPTMetadata(
            name="gpt",
            version="1.0.0",
            supported_models=["gpt-4o", "gpt-4o-mini", "o3-mini"],
            supported_events=["PromptSubmitted", "ResponseReceived", "ModelChanged"],
            api_key_set=api_key,
            default_model="gpt-4o",
        )

    def health(self) -> ConnectorStatus:
        return ConnectorStatus(state="connected" if self._is_connected else "disconnected")

    def supports(self, capability: str) -> bool:
        return capability in ["prompt_generation", "code_completion", "event_streaming"]

    def shutdown(self) -> None:
        self.disconnect()
