import asyncio
from typing import Any, Literal

from agents import (
    Agent,
    FunctionToolResult,
    ModelSettings,
    RunContextWrapper,
    Runner,
    ToolsToFinalOutputFunction,
    ToolsToFinalOutputResult,
    function_tool,
)
from faker import Faker
from pydantic import BaseModel

from openai_agent.agentic_patterns.common.llm_model import llm_model

fake = Faker()
"""
This example shows how to force the agent to use a tool. It uses
`ModelSettings(tool_choice="required")` to force the agent to use any tool.

You can run it with 3 options:
1. `default`: The default behavior, which is to send the tool output to the LLM. In
    this case, `tool_choice` is not set, because otherwise it would result in an
    infinite loop - the LLM would call the tool, the tool would run and send the
    results to the LLM, and that would repeat (because the model is forced to use a
    tool every time.)
2. `first_tool_result`: The first tool result is used as the final output.
3. `custom`: A custom tool use behavior function is used. The custom function
    receives all the tool results, and chooses to use the first tool result to
    generate the final output.

Usage:
python examples/agent_patterns/forcing_tool_use.py -t default
python examples/agent_patterns/forcing_tool_use.py -t first_tool
python examples/agent_patterns/forcing_tool_use.py -t custom
"""


class Specialist(BaseModel):
    first_name: str
    last_name: str
    salutation: str = "Dr."

    @classmethod
    def generate(cls) -> "Specialist":
        return cls(first_name=fake.first_name(), last_name=fake.last_name())

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.salutation} {self.first_name} {self.last_name}"


@function_tool
def get_specialist(city: str) -> Specialist:
    return Specialist.generate()


async def custom_tool_use_behavior(
    context: RunContextWrapper[Any], results: list[FunctionToolResult]
) -> ToolsToFinalOutputResult:
    specialist: Specialist = results[0].output
    return ToolsToFinalOutputResult(is_final_output=True, final_output=str(specialist))


async def main(
    tool_use_behavior: Literal["default", "first_tool", "custom"] = "default",
):
    if tool_use_behavior == "default":
        behavior: (
            Literal["run_llm_again", "stop_on_first_tool"] | ToolsToFinalOutputFunction
        ) = "run_llm_again"
    elif tool_use_behavior == "first_tool":
        behavior = "stop_on_first_tool"
    elif tool_use_behavior == "custom":
        behavior = custom_tool_use_behavior

    agent = Agent(
        name="Medical Expert agent",
        instructions="You are a helpful agent who assist in finding medical specialists.",  # noqa E501
        tools=[get_specialist],
        tool_use_behavior=behavior,
        model_settings=ModelSettings(
            tool_choice="required" if tool_use_behavior != "default" else None
        ),
        model=llm_model,
    )

    result = await Runner.run(agent, input="I need a cardiologist in Seattle")
    print(result.final_output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tool-use-behavior",
        type=str,
        required=True,
        choices=["default", "first_tool", "custom"],
        help=(
            "The behavior to use for tool use. Default will cause tool outputs"
            "to be sent to the model. first_tool_result will cause the first tool "
            "result to be used as the final output. custom will use a custom tool use "
            "behavior function."
        ),
    )
    args = parser.parse_args()
    asyncio.run(main(args.tool_use_behavior))
