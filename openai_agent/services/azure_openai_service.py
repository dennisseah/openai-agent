from dataclasses import dataclass
from typing import Callable

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from lagom.environment import Env
from openai import AsyncAzureOpenAI

from openai_agent.protocols.i_azure_openai_service import IAzureOpenAIService


class AzureOpenAIServiceEnv(Env):
    azure_openai_endpoint: str
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str
    azure_openai_deployed_model_name: str


@dataclass
class AzureOpenAIService(IAzureOpenAIService):
    env: AzureOpenAIServiceEnv

    def get_openai_auth_key(self) -> dict[str, str | Callable[[], str]]:
        if self.env.azure_openai_api_key:
            return {"api_key": self.env.azure_openai_api_key}

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
        )

        return {"azure_ad_token_provider": token_provider}

    def get_client(self) -> AsyncAzureOpenAI:
        return AsyncAzureOpenAI(
            azure_endpoint=self.env.azure_openai_endpoint,
            api_version=self.env.azure_openai_api_version,
            **self.get_openai_auth_key(),  # type: ignore
        )

    def get_deployed_model_name(self) -> str:
        return self.env.azure_openai_deployed_model_name
