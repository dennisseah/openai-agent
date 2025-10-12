from typing import Callable
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from openai_agent.services.azure_openai_service import AzureOpenAIService


@pytest.fixture
def fn_mock_service(mocker: MockerFixture) -> Callable[[bool], AzureOpenAIService]:
    def wrapper(with_api_key: bool) -> AzureOpenAIService:
        mocker.patch(
            "openai_agent.services.azure_openai_service.AsyncAzureOpenAI",
            autospec=True,
        )

        mock_cred = MagicMock()
        mock_cred.get_token.return_value = MagicMock(
            token="mock_token",
            scope="https://example.com/.default",
        )
        mocker.patch(
            "openai_agent.services.azure_openai_service.DefaultAzureCredential",
            return_value=mock_cred,
        )

        env = MagicMock()
        if not with_api_key:
            env.azure_openai_api_key = None
        return AzureOpenAIService(env=env)

    return wrapper


def test_get_client(
    fn_mock_service: Callable[[bool], AzureOpenAIService], mocker: MockerFixture
):
    mock_service = fn_mock_service(with_api_key=True)  # type: ignore
    assert mock_service.get_client() is not None


def test_get_client_without_api_key(
    fn_mock_service: Callable[[bool], AzureOpenAIService], mocker: MockerFixture
):
    mock_service = fn_mock_service(with_api_key=False)  # type: ignore
    assert mock_service.get_client() is not None


def test_get_deployed_model(
    fn_mock_service: Callable[[bool], AzureOpenAIService],
):
    mock_service = fn_mock_service(with_api_key=True)  # type: ignore
    mock_service.env.azure_openai_deployed_model_name = "test-model"

    model_name = mock_service.get_deployed_model_name()
    assert model_name == "test-model"
