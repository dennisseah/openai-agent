from agents import (
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
)

from openai_agent.hosting import container
from openai_agent.protocols.i_azure_openai_service import IAzureOpenAIService

set_tracing_disabled(True)
azure_openai_service = container[IAzureOpenAIService]

llm_model = OpenAIChatCompletionsModel(
    model=azure_openai_service.get_deployed_model_name(),
    openai_client=azure_openai_service.get_client(),
)
