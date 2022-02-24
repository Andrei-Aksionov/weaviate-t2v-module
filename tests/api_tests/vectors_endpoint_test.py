import json

from fastapi.testclient import TestClient
from hypothesis import example, given, settings
from requests import Response

from app import app
from src import config
from tests.utils.hypothesis_utils import generate_text


class TestVectorsEndpoint:

    test_texts = ["", "Test text"]

    @classmethod
    def setup_class(cls: "TestVectorsEndpoint") -> None:
        cls.client = TestClient(app)
        # When you need your event handlers (startup and shutdown) to run in your tests,
        # you can use the TestClient with a `with` statement
        # but it has to be done in each test which means that model will be loaded each time
        # that's why it's better to call startup/shutdown handlers explicitly once
        # for all tests
        cls.client.__enter__()
        cls.endpoint = "/vectors"

    @classmethod
    def teardown_class(cls: "TestVectorsEndpoint") -> None:
        cls.client.__exit__()

    def __post_text(
        self,
        text: str,
        as_json: bool = True,
        assert_status_code: bool = True,
    ) -> Response:
        data = {"text": text}
        response = TestVectorsEndpoint.client.post(
            TestVectorsEndpoint.endpoint,
            data=json.dumps(data),
        )
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
