import time

import requests

from src import config


class TestMetaDocker:
    @classmethod
    def __wait_for_startup(cls: "TestMetaDocker", url: str, timeout: int) -> None:

        for _ in range(timeout):
            response = requests.get(url)
            if response.status_code == 204:
                return None
            time.sleep(1)
            continue

        raise Exception(f"Service hasn't started in {timeout} seconds")

    @classmethod
    def setup_class(cls: "TestMetaDocker") -> None:
        cls.endpoint = f"http://{config.app.host}:{config.app.port}/meta"
        ready_endpoint = f"http://{config.app.host}:{config.app.port}/.well-known/ready"
        cls.__wait_for_startup(ready_endpoint, 100)

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
