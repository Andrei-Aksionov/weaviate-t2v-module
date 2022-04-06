import json

import pytest
import requests
from hypothesis import example, given, settings
from requests import Response

from src import config
from tests.utils.endpoint_utils import wait_for_startup
from tests.utils.hypothesis_utils import generate_text


@pytest.mark.Docker
class TestVectorsDocker:

    test_texts = ["", "Test text"]

    @classmethod
    def setup_class(cls: "TestVectorsDocker") -> None:
        # before starting any test need to wait till docker container is ready
        ready_endpoint = f"http://{config.app.host}:{config.app.port}/.well-known/ready"
        timeout = config.test.docker.wait_for_startup
        wait_for_startup(url=ready_endpoint, expected_status_code=204, timeout=timeout)
        cls.endpoint = f"http://{config.app.host}:{config.app.port}/vectors"

    def __post_text(
        self,
        text: str,
        as_json: bool = True,
        assert_status_code: bool = True,
    ) -> Response:
        data = {"text": text}
        response = requests.post(TestVectorsDocker.endpoint, data=json.dumps(data))
        if assert_status_code:
            assert response.status_code == 200
        if as_json:
            response = response.json()
        return response

    @settings(max_examples=config.test.hypothesis.max_examples)
    @given(generate_text())
    @example(*test_texts)
    def test_vectors_output_is_dictionary(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert isinstance(response, dict)

    @settings(max_examples=config.test.hypothesis.max_examples)
    @given(generate_text())
    @example(*test_texts)
    def test_vectors_output_dict_not_empty(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert bool(response)

    @settings(max_examples=config.test.hypothesis.max_examples)
    @given(generate_text())
    @example(*test_texts)
    def test_vectors_output_dict_contains_expected_keys(self, text: str) -> None:
        # Given
        expected_keys = ("text", "vector", "dim")

        # When/Then
        response = self.__post_text(text)
        for key in expected_keys:
            assert key in response

    @settings(max_examples=config.test.hypothesis.max_examples)
    @given(generate_text())
    @example(*test_texts)
    def test_vectors_output_dict_not_empty_values(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        # if provided text value was empty string, then in the response
        # empty string also will be presented
        if text:
            assert all(response.values())
        else:
            assert all(value for key, value in response.items() if key != "text")

    @settings(max_examples=config.test.hypothesis.max_examples)
    @given(generate_text())
    @example(*test_texts)
    def test_vectors_output_check_vector_length(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert len(response["vector"]) > 0
        assert len(response["vector"]) == response["dim"]
