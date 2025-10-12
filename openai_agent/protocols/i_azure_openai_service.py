from typing import Protocol

from openai import AsyncAzureOpenAI


class IAzureOpenAIService(Protocol):
    def get_client(self) -> AsyncAzureOpenAI:
        """
        Get the Azure OpenAI client.

        :return: An instance of AsyncAzureOpenAI.
        """
        ...

    def get_deployed_model_name(self) -> str:
        """
        Get the deployment name for the Azure OpenAI model.

        :return: The deployment name as a string.
        """
        ...
