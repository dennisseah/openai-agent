import re

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

emergency_department_agent = Agent(
    name="emergency_department_agent",
    instructions=(
        "Handle emergency medical situations promptly and efficiently. "
        "Triage patients based on the severity of their conditions and "
        "provide immediate care."
    ),
    model=llm_model,
)

surgery_agent = Agent(
    name="surgery_agent",
    instructions=(
        "Manage surgical procedures, both inpatient and outpatient. "
        "Coordinate pre-operative and post-operative care, ensuring patient safety."
    ),
    model=llm_model,
)

icu_agent = Agent(
    name="icu_agent",
    instructions=(
        "Provide critical care for severely ill or injured patients. "
        "Manage life-support systems and monitor vital signs closely."
    ),
    model=llm_model,
)

cardiolofy_agent = Agent(
    name="cardiology_agent",
    instructions=(
        "Focus on diagnosing and treating heart-related conditions. "
        "Perform cardiac assessments and recommend appropriate interventions."
    ),
    model=llm_model,
)

obstetrics_agent = Agent(
    name="obstetrics_agent",
    instructions=(
        "Oversee pregnancy, childbirth, and postpartum care. "
        "Monitor fetal development and manage any complications that arise."
    ),
    model=llm_model,
)

pediatrics_agent = Agent(
    name="pediatrics_agent",
    instructions=(
        "Specialize in the medical care of infants, children, and "
        "adolescents. Monitor growth and development, and address "
        "common childhood illnesses."
    ),
    model=llm_model,
)

oncology_agent = Agent(
    name="oncology_agent",
    instructions=(
        "Deal with the diagnosis and treatment of cancer. "
        "Develop treatment plans and provide supportive care to patients."
    ),
    model=llm_model,
)

neurology_agent = Agent(
    name="neurology_agent",
    instructions=(
        "Specialize in diagnosing and treating disorders of the nervous system. "
        "Conduct neurological assessments and recommend treatment options."
    ),
    model=llm_model,
)

radiology_agent = Agent(
    name="radiology_agent",
    instructions=(
        "Use medical imaging techniques to diagnose and treat diseases. "
        "Interpret X-rays, CT scans, MRIs, and other imaging results."
    ),
    model=llm_model,
)

orthopedics_agent = Agent(
    name="orthopedics_agent",
    instructions=(
        "Treat injuries and diseases of the musculoskeletal system. "
        "Perform orthopedic assessments and recommend treatment plans."
    ),
    model=llm_model,
)

gastroenterology_agent = Agent(
    name="gastroenterology_agent",
    instructions=(
        "Deal with the digestive system. "
        "Diagnose and treat conditions related to the gastrointestinal tract."
    ),
    model=llm_model,
)


def get_all_agents() -> list[Agent]:
    return [
        emergency_department_agent,
        surgery_agent,
        icu_agent,
        cardiolofy_agent,
        obstetrics_agent,
        pediatrics_agent,
        oncology_agent,
        neurology_agent,
        radiology_agent,
        orthopedics_agent,
        gastroenterology_agent,
    ]


def get_departments() -> list[str]:
    def fn_upper(match):
        return match.group(1).upper()

    def fn_space_upper(match):
        return " " + match.group(1).upper()

    return [
        re.sub(
            r"^(\S)",
            fn_upper,
            re.sub(r"_(\S)", fn_space_upper, re.sub(r"_agent$", "", agent.name)),
        )
        for agent in get_all_agents()
    ]
