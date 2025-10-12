import asyncio

from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from pydantic import BaseModel

from openai_agent.hosting import container
from openai_agent.protocols.i_azure_openai_service import IAzureOpenAIService

set_tracing_disabled(True)
azure_openai_service = container[IAzureOpenAIService]


class DepartmentOutput(BaseModel):
    reasoning: str
    department_name: str


symptom_agent = Agent(
    name="symptom_agent",
    instructions=(
        "You are a medical symptom generator. Given a disease or medical condition, "
        "generate the most characteristic and clinically significant symptoms that "
        "patients typically experience. Focus on primary symptoms that are commonly "
        "observed and would be most relevant for medical triage. Present symptoms "
        "in a clear, concise manner using medical terminology that healthcare "
        "professionals would recognize. Prioritize symptoms by frequency and "
        "diagnostic significance."
    ),
    model=OpenAIChatCompletionsModel(
        model=azure_openai_service.get_deployed_model_name(),
        openai_client=azure_openai_service.get_client(),
    ),
)
medical_agent = Agent(
    name="medical_agent",
    instructions=(
        "You are a medical triage specialist. Analyze the given symptoms and provide "
        "a comprehensive assessment including: 1) Clear reasoning that explains the "
        "medical rationale for your recommendation, 2) The most appropriate hospital "
        "department name for initial evaluation and treatment. Consider symptom "
        "severity, urgency, and specialization requirements. Provide professional, "
        "evidence-based recommendations suitable for healthcare routing decisions."
    ),
    model=OpenAIChatCompletionsModel(
        model=azure_openai_service.get_deployed_model_name(),
        openai_client=azure_openai_service.get_client(),
    ),
    output_type=DepartmentOutput,
)


async def main():
    input_prompt = input(
        "Enter a medical condition or disease name (e.g., 'diabetes', 'pneumonia', 'migraine'): "  # noqa: E501
    )

    symptom = await Runner.run(symptom_agent, input_prompt)
    print("\nSymptom:")
    print(symptom.final_output)

    department_result = await Runner.run(medical_agent, symptom.final_output)
    print("\nDepartment Information:")
    print(department_result.final_output.model_dump_json(indent=4))
    print()


if __name__ == "__main__":
    asyncio.run(main())
