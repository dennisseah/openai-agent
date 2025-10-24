from __future__ import annotations

import asyncio

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    input_guardrail,
)
from pydantic import BaseModel

from openai_agent.agentic_patterns.common.llm_model import llm_model


class DrugPurchaseOutput(BaseModel):
    reasoning: str
    requested: bool


@input_guardrail
async def drug_purchase_guardrail(
    context: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    guardrail_agent = Agent(
        name="Guardrail check",
        instructions="Check if the user is requesting for any drug purchases.",
        output_type=DrugPurchaseOutput,
        model=llm_model,
    )

    result = await Runner.run(guardrail_agent, input, context=context.context)
    final_output = result.final_output_as(DrugPurchaseOutput)

    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=final_output.requested,
    )


async def main():
    agent = Agent(
        name="Customer support agent",
        instructions=(
            "You are a medical customer support agent. Answer user questions "
            "about medical products and services, but do not assist with drug "
            "purchases."
        ),
        input_guardrails=[drug_purchase_guardrail],
        model=llm_model,
    )

    input_data: list[TResponseInputItem] = []

    while True:
        user_input = input("Enter a message: ")
        input_data.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        try:
            result = await Runner.run(agent, input_data)
            print(result.final_output)
            input_data = result.to_input_list()
        except InputGuardrailTripwireTriggered:
            message = "Sorry, I can't help you with your request."
            print(message)
            input_data.append(
                {
                    "role": "assistant",
                    "content": message,
                }
            )


if __name__ == "__main__":
    asyncio.run(main())
