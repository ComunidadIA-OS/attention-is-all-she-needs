'''Clients for large language models with structured output (answers parsed into Pydantic schemas)'''

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from aiasn.settings import LlmSettings

Schema = TypeVar("Schema", bound=BaseModel)


class LLMClient(ABC):
    @abstractmethod
    def complete(self, system: str, user: str, schema: type[Schema]) -> Schema:
        """Answer of the model to `user` under the `system` prompt, parsed into `schema`."""


class LiteLLMClient(LLMClient):
    """Any provider supported by litellm; by default an OpenAI-compatible endpoint (OVHcloud AI Endpoints)."""

    def __init__(self, cfg: LlmSettings):
        self.cfg = cfg
        self.token = "".join(cfg.token.get_secret_value().split())   # pasted tokens often carry line breaks

    def complete(self, system: str, user: str, schema: type[Schema]) -> Schema:
        if not self.token:
            raise RuntimeError("Missing LLM token: set OVH_AI_ENDPOINTS_ACCESS_TOKEN in the environment or .env")
        import litellm   # optional dependency (ADR-002): only needed when the model is called

        response = litellm.completion(
            model=self.cfg.model, api_base=self.cfg.base_url, api_key=self.token, temperature=self.cfg.temperature,
            timeout=self.cfg.timeout, num_retries=self.cfg.retries, response_format=schema,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        return schema.model_validate_json(response.choices[0].message.content)


class OllamaClient(LLMClient):
    """Local models with Ollama. Not implemented yet."""

    def __init__(self, cfg: LlmSettings):
        self.cfg = cfg

    def complete(self, system: str, user: str, schema: type[Schema]) -> Schema:
        raise NotImplementedError("Ollama client not implemented yet")


def make_llm_client(cfg: LlmSettings) -> LLMClient:
    """The client of the configured provider."""
    return {"litellm": LiteLLMClient, "ollama": OllamaClient}[cfg.provider](cfg)
