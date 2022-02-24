from fastapi.testclient import TestClient

from app import app


class TestMetaEndpoint:
    @classmethod
    def setup_class(cls: "TestMetaEndpoint") -> None:
        cls.client = TestClient(app)
        # When you need your event handlers (startup and shutdown) to run in your tests,
        # you can use the TestClient with a with statement
        # but it has to be done in each test which means that model will be loaded each time
        # that's why it's better to call startup/shutdown handlers explicitly once
        # for all tests
        cls.client.__enter__()
        cls.endpoint = "/meta"

    @classmethod
    def teardown_class(cls: "TestMetaEndpoint") -> None:
        cls.client.__exit__()

    def test_meta_output_is_dictionary(self) -> None:
        response = TestMetaEndpoint.client.get(TestMetaEndpoint.endpoint)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_meta_output_dict_not_empty(self) -> None:
        # When/Then
        response = TestMetaEndpoint.client.get(TestMetaEndpoint.endpoint)
        assert response.status_code == 200
        assert bool(response.json())
