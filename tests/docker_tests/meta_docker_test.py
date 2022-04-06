import pytest
import requests

from src import config
from tests.utils.endpoint_utils import wait_for_startup


@pytest.mark.Docker
class TestMetaDocker:
    @classmethod
    def setup_class(cls: "TestMetaDocker") -> None:
        # before starting any test need to wait till docker container is ready
        ready_endpoint = f"http://{config.app.host}:{config.app.port}/.well-known/ready"
        timeout = config.test.docker.wait_for_startup
        wait_for_startup(url=ready_endpoint, expected_status_code=204, timeout=timeout)
        cls.endpoint = f"http://{config.app.host}:{config.app.port}/meta"

    def test_meta_output_is_dictionary(self) -> None:

        # When
        response = requests.get(TestMetaDocker.endpoint)

        # Then
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_meta_output_dict_not_empty(self) -> None:
        # When
        response = requests.get(TestMetaDocker.endpoint)

        # Then
        assert response.status_code == 200
        assert bool(response.json())
