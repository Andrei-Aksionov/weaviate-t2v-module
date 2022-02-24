from fastapi.testclient import TestClient

from app import app


class TestMetaEndpoint:
    def test_meta_output_is_dictionary(self) -> None:
        # When/Then

        # When you need your event handlers (startup and shutdown) to run in your tests,
        # you can use the TestClient with a with statement
        with TestClient(app) as client:
            response = client.get("/meta")
            assert response.status_code == 200
            assert isinstance(response.json(), dict)

    def test_meta_output_dict_not_empty(self) -> None:
        # When/Then
        with TestClient(app) as client:
            response = client.get("/meta")
            assert response.status_code == 200
            assert bool(response.json())
