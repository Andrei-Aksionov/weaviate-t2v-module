import json
import time

import pytest
import requests
from requests import Response

from src import config


class TestVectorsDocker:

    test_texts = ["", "Test text"]

    @classmethod
    def __wait_for_startup(cls: "TestVectorsDocker", url: str, timeout: int) -> None:

        for _ in range(timeout):
            response = requests.get(url)
            if response.status_code == 204:
                return None
            time.sleep(1)
            continue

        raise Exception(f"Service hasn't started in {timeout} seconds")

    @classmethod
    def setup_class(cls: "TestVectorsDocker") -> None:
        cls.endpoint = f"http://{config.app.host}:{config.app.port}/vectors"
        ready_endpoint = f"http://{config.app.host}:{config.app.port}/.well-known/ready"
        cls.__wait_for_startup(ready_endpoint, 100)

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

    @pytest.mark.parametrize("text", test_texts)
    def test_vectors_output_is_dictionary(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert isinstance(response, dict)

    @pytest.mark.parametrize("text", test_texts)
    def test_vectors_output_dict_not_empty(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert bool(response)

    @pytest.mark.parametrize("text", test_texts)
    def test_vectors_output_dict_contains_expected_keys(self, text: str) -> None:
        # Given
        expected_keys = ("text", "vector", "dim")

        # When/Then
        response = self.__post_text(text)
        for key in expected_keys:
            assert key in response

    @pytest.mark.parametrize("text", test_texts)
    def test_vectors_output_dict_not_empty_values(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        # if provided text value was empty string, then in the response
        # empty string also will be presented
        if text:
            assert all(response.values())
        else:
            assert all(value for key, value in response.items() if key != "text")

    @pytest.mark.parametrize("text", test_texts)
    def test_vectors_output_check_vector_length(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert len(response["vector"]) > 0
        assert len(response["vector"]) == response["dim"]
