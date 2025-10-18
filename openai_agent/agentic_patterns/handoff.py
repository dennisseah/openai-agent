import asyncio

from agents import Agent, RawResponsesStreamEvent, Runner, TResponseInputItem
from openai.types.responses import ResponseTextDeltaEvent

from openai_agent.agentic_patterns.common.doctor_agents import get_all_agents
from openai_agent.agentic_patterns.common.llm_model import llm_model

triage_agent = Agent(
    name="triage_agent",
    instructions=(
        "Handoff to the appropriate agent based on the medical condition of "
        "the patient."
    ),
    handoffs=get_all_agents(),  # type: ignore
    model=llm_model,
)


async def main():
    msg = input(
        (
            "Hi! Tell me about your medical condition and we will route your request "
            "to the appropriate agent: "
        )
    )
    agent = triage_agent
    inputs: list[TResponseInputItem] = [{"content": msg, "role": "user"}]

    while True:
        result = Runner.run_streamed(
            agent,
            input=inputs,
        )

        async for event in result.stream_events():
            if isinstance(event, RawResponsesStreamEvent):
                data = event.data
                if isinstance(data, ResponseTextDeltaEvent):
                    if result.current_agent.name != agent.name:
                        print(
                            f"\n\033[33m--- Handing off to {result.current_agent.name} ---\033[0m\n"  # noqa: E501
                        )
                        agent = result.current_agent
                    print(data.delta, end="", flush=True)

        inputs = result.to_input_list()
        print("\n")

        user_msg = input("Enter a message: ")
        inputs.append({"content": user_msg, "role": "user"})


if __name__ == "__main__":
    asyncio.run(main())
