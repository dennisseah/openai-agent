import asyncio

from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)
from pydantic import BaseModel

from openai_agent.hosting import container
from openai_agent.protocols.i_azure_openai_service import IAzureOpenAIService

set_tracing_disabled(True)
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
    handoff_description="An english to italian translator",
    model=llm_model,
)


orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a medical translation orchestrator responsible for routing "
        "translation requests to specialized medical translators. Analyze the "
        "user's request to identify the target language (Spanish, French, or "
        "Italian) and select the appropriate translation tool. If no specific "
        "language is mentioned, default to Spanish translation. You must always "
        "delegate translations to the specialized tools - never attempt to "
        "translate directly. Ensure accurate routing for optimal medical "
        "translation quality. You may need to use multiple tools in sequence "
        "because some translations may require an intermediate language step."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the doctor's message to Spanish",
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the doctor's message to French",
        ),
        italian_agent.as_tool(
            tool_name="translate_to_italian",
            tool_description="Translate the doctor's message to Italian",
        ),
    ],
    model=llm_model,
    output_type=TranslationOutput,
)


async def main():
    msg = input(
        "Enter a medical message in English and specify target language "
        "(Spanish, French, Italian, or leave blank for Spanish): "
    )

    orchestrator_result = await Runner.run(orchestrator_agent, msg)

    print()
    print("Translation Result:")
    print(orchestrator_result.final_output.model_dump_json(indent=4))
    print()


if __name__ == "__main__":
    asyncio.run(main())
