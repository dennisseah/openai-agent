import asyncio

from agents import (
    Agent,
    Runner,
)

from openai_agent.agentic_patterns.common.language_agents import (
    TranslationOutput,
    french_agent,
    italian_agent,
    spanish_agent,
)
from openai_agent.agentic_patterns.common.llm_model import llm_model

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
