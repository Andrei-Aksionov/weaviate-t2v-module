import json

import pytest
from fastapi.testclient import TestClient
from requests import Response

from app import app


class TestVectorsEndpoint:
    def __post_text(
        self,
        text: str,
        endpoint: str = "/vectors",
        as_json: bool = True,
        assert_status_code: bool = True,
    ) -> Response:
        # When you need your event handlers (startup and shutdown) to run in your tests,
        # you can use the TestClient with a with statement
        with TestClient(app) as client:
            data = {"text": text}
            response = client.post(endpoint, data=json.dumps(data))
            if assert_status_code:
                assert response.status_code == 200
            if as_json:
                response = response.json()
            return response

    @pytest.mark.parametrize("text", ["", "Test text"])
    def test_vectors_output_is_dictionary(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert isinstance(response, dict)

    @pytest.mark.parametrize("text", ["", "Test text"])
    def test_vectors_output_dict_not_empty(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert bool(response)

    @pytest.mark.parametrize("text", ["", "Test text"])
    def test_vectors_output_dict_contains_expected_keys(self, text: str) -> None:
        # Given
        expected_keys = ("text", "vector", "dim")

        # When/Then
        response = self.__post_text(text)
        for key in expected_keys:
            assert key in response

    @pytest.mark.parametrize("text", ["", "Test text"])
    def test_vectors_output_dict_not_empty_values(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        # if provided text value was empty string, then in the response
        # empty string also will be presented
        if text:
            assert all(response.values())
        else:
            assert all(value for key, value in response.items() if key != "text")

    @pytest.mark.parametrize("text", ["", "Test text"])
    def test_vectors_output_check_vector_length(self, text: str) -> None:
        # When/Then
        response = self.__post_text(text)
        assert len(response["vector"]) > 0
        assert len(response["vector"]) == response["dim"]
