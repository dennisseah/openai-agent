from agents import (
    Agent,
    OpenAIChatCompletionsModel,
)
from pydantic import BaseModel

from openai_agent.hosting import container
from openai_agent.protocols.i_azure_openai_service import IAzureOpenAIService

azure_openai_service = container[IAzureOpenAIService]


class TranslationOutput(BaseModel):
    input_text: str
    translated_text: str


llm_model = OpenAIChatCompletionsModel(
    model=azure_openai_service.get_deployed_model_name(),
    openai_client=azure_openai_service.get_client(),
)

INSTRUCTIONS = (
    "You are a professional medical translator specializing in "
    "@@from_language@@ to @@to_language@@ translation. Translate medical "
    "communications with precision, maintaining clinical accuracy and appropriate "
    "medical terminology. Ensure translations are culturally sensitive "
    "and use formal, respectful language suitable for patient-doctor "
    "communication. Preserve the original meaning while adapting to "
    "@@to_language@@s medical conventions and terminology standards."
)

spanish_agent = Agent(
    name="spanish_agent",
    instructions=INSTRUCTIONS.replace("@@to_language@@", "Spanish").replace(
        "@@from_language@@", "English"
    ),
    handoff_description="An english to spanish translator",
    model=llm_model,
)

french_agent = Agent(
    name="french_agent",
    instructions=INSTRUCTIONS.replace("@@to_language@@", "French").replace(
        "@@from_language@@", "English"
    ),
    handoff_description="An english to french translator",
    model=llm_model,
)

italian_agent = Agent(
    name="italian_agent",
    instructions=INSTRUCTIONS.replace("@@to_language@@", "Italian").replace(
        "@@from_language@@", "Spanish"
    ),
    handoff_description="An spanish to italian translator",
    model=llm_model,
)
