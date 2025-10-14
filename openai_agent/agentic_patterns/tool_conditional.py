import asyncio
from typing import Literal

from agents import (
    Agent,
    AgentBase,
    RunContextWrapper,
    Runner,
)
from pydantic import BaseModel

from openai_agent.agentic_patterns.common.language_agents import (
    TranslationOutput,
    french_agent,
    italian_agent,
    spanish_agent,
)
from openai_agent.agentic_patterns.common.llm_model import llm_model

# in the other example, we default the language to Spanish if not specified.
# here, we will use a context object to control which languages are available


language_options = [
    ("spanish_only", "Spanish only"),
    ("french_spanish", "French and Spanish"),
    ("italian_spanish", "Italian and Spanish"),
]


class AppContext(BaseModel):
    language_preference: Literal[
        "spanish_only", "french_spanish", "italian_spanish"
    ] = "spanish_only"


def french_spanish_enabled(
    ctx: RunContextWrapper[AppContext], agent: AgentBase
) -> bool:
    """Enable for French preferences."""
    return ctx.context.language_preference == "french_spanish"


def italian_spanish_enabled(
    ctx: RunContextWrapper[AppContext], agent: AgentBase
) -> bool:
    """Only enable for Italian preference."""
    return ctx.context.language_preference == "italian_spanish"


orchestrator_agent = Agent(
    name="orchestrator_agent",
    instructions=(
        "You are a translator. You use the tools given to you to respond to users. "
        "You must call ALL available tools to provide responses in different"
        "languages. You never respond in languages yourself, you always use the "
        "provided tools."
    ),
    tools=[
        spanish_agent.as_tool(
            tool_name="translate_to_spanish",
            tool_description="Translate the doctor's message to Spanish",
            is_enabled=True,
        ),
        french_agent.as_tool(
            tool_name="translate_to_french",
            tool_description="Translate the doctor's message to French",
            is_enabled=french_spanish_enabled,
        ),
        italian_agent.as_tool(
            tool_name="translate_to_italian",
            tool_description="Translate the doctor's message to Italian",
            is_enabled=italian_spanish_enabled,
        ),
    ],
    model=llm_model,
    output_type=TranslationOutput,
)


def select_languages() -> RunContextWrapper:
    print("Choose language preference:")
    for idx, lang in enumerate(language_options, start=1):
        print(f"{idx}. {lang[1]}")

    # error handling omitted for brevity
    choice = input("\nSelect option (1-3): ").strip()

    if not choice:
        print("No choice made, defaulting to Spanish only.")
        choice = "1"

    idx = int(choice) - 1
    if idx < 0 or idx >= len(language_options):
        print("Invalid choice, defaulting to Spanish only.")
        idx = 0
    return RunContextWrapper(
        AppContext(language_preference=language_options[idx][0]),  # type: ignore
    )


async def main():
    context = select_languages()

    user_request = input(
        "Enter a medical message in English and see responses in available languages: "
    )

    # Run with LLM interaction
    result = await Runner.run(
        starting_agent=orchestrator_agent,
        input=user_request,
        context=context.context,
    )

    print("\nResponse:")
    print()
    print(result.final_output.model_dump_json(indent=4))
    print()


if __name__ == "__main__":
    asyncio.run(main())
